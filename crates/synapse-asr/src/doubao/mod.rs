//! Volc Engine streaming ASR ("bigmodel") provider.
//!
//! Wraps the binary protocol in [`proto`] in our standard [`AsrProvider`]
//! shape. ARK Bearer auth is the only supported credential — pass the API
//! key as a string; everything else (endpoint, app id, language) is in
//! [`DoubaoConfig`].
//!
//! ## Stability
//!
//! The wire protocol is documented at
//! <https://www.volcengine.com/docs/6561/1354869>. The implementation
//! sticks to documented bytes only; no clever bit-twiddling that could
//! drift if Volc revises the format. The `proto` submodule is unit-tested
//! standalone; the integration test in `tests/doubao.rs` exercises the
//! full provider against a mock server that speaks this exact shape.
//!
//! ## What is **not** validated against a real Volc endpoint
//!
//! - **Exact JSON config schema.** Volc has revised it across versions.
//!   The shape in [`build_config_payload`] is the documented one but
//!   may need tweaks per ARK product variant. The struct is built from
//!   `serde_json::json!` so adjustments are localized.
//! - **`Authorization: Bearer ark-...` vs alternative auth headers.**
//!   Some ARK endpoints additionally want `X-Api-App-Key` or
//!   `X-Api-Resource-Id`. [`DoubaoConfig`] takes them as `Option`.

use std::time::Duration;

use async_trait::async_trait;
use futures_util::{SinkExt, StreamExt};
use tokio::sync::mpsc;
use tokio_tungstenite::tungstenite::client::IntoClientRequest;
use tokio_tungstenite::tungstenite::handshake::client::Request;
use tokio_tungstenite::tungstenite::Message;
use uuid::Uuid;

use crate::{AsrChannels, AsrConfig, AsrError, AsrEvent, AsrProvider};

pub mod proto;

const DEFAULT_ENDPOINT: &str = "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel";

#[derive(Debug, Clone)]
pub struct DoubaoConfig {
    /// WebSocket endpoint. Defaults to the Volc bigmodel ASR URL.
    pub endpoint: String,
    /// ARK API key (`ark-...`). Sent as `Authorization: Bearer <key>`.
    pub api_key: String,
    /// Optional Volc app id (some endpoint variants want it as `X-Api-App-Key`).
    pub app_id: Option<String>,
    /// Optional Volc resource id (some endpoint variants want it as `X-Api-Resource-Id`).
    pub resource_id: Option<String>,
    /// Language hint, e.g. "zh-CN". Default `"zh-CN"`.
    pub language: String,
    /// Optional name override for telemetry. Defaults to `"doubao"`.
    pub display_name: Option<&'static str>,
}

impl DoubaoConfig {
    pub fn new(api_key: impl Into<String>) -> Self {
        Self {
            endpoint: DEFAULT_ENDPOINT.into(),
            api_key: api_key.into(),
            app_id: None,
            resource_id: None,
            language: "zh-CN".into(),
            display_name: None,
        }
    }
}

#[derive(Debug)]
pub struct DoubaoAsrProvider {
    cfg: DoubaoConfig,
}

impl DoubaoAsrProvider {
    pub fn new(cfg: DoubaoConfig) -> Self {
        Self { cfg }
    }
}

#[async_trait]
impl AsrProvider for DoubaoAsrProvider {
    fn name(&self) -> &'static str {
        self.cfg.display_name.unwrap_or("doubao")
    }

    async fn start(&self, asr_cfg: AsrConfig) -> Result<AsrChannels, AsrError> {
        let req = build_request(&self.cfg)?;
        tracing::debug!(endpoint = %self.cfg.endpoint, "doubao ws connecting");

        let (ws_stream, _resp) = tokio_tungstenite::connect_async(req)
            .await
            .map_err(classify_handshake_error)?;
        let (mut ws_sink, mut ws_stream) = ws_stream.split();

        // 1. Send the JSON config in a "full client request" frame.
        let config_json = build_config_payload(&self.cfg, &asr_cfg);
        let config_bytes = serde_json::to_vec(&config_json)
            .map_err(|e| AsrError::Protocol(format!("encode config: {e}")))?;
        let frame = proto::encode_full_client_request(&config_bytes);
        ws_sink
            .send(Message::Binary(frame.to_vec()))
            .await
            .map_err(|e| AsrError::Network(format!("ws send config: {e}")))?;

        let (audio_tx, mut audio_rx) = mpsc::channel::<Vec<i16>>(64);
        let (events_tx, events_rx) = mpsc::channel::<Result<AsrEvent, AsrError>>(8);

        // Audio pump: i16 frames -> Volc binary audio frames.
        let events_tx_for_audio = events_tx.clone();
        tokio::spawn(async move {
            // Drain frames; mark the eventual EOS frame with FLAG_LAST.
            let mut prev: Option<Vec<u8>> = None;
            while let Some(frame) = audio_rx.recv().await {
                if let Some(prev_bytes) = prev.take() {
                    let pkt = proto::encode_audio_chunk(&prev_bytes, false);
                    if let Err(e) = ws_sink.send(Message::Binary(pkt.to_vec())).await {
                        let _ = events_tx_for_audio
                            .send(Err(AsrError::Network(format!("ws send audio: {e}"))))
                            .await;
                        return;
                    }
                }
                prev = Some(i16_to_le_bytes(&frame));
            }
            // Send the buffered frame as EOS, or a zero-byte EOS if there were no frames.
            let last_payload = prev.unwrap_or_default();
            let pkt = proto::encode_audio_chunk(&last_payload, true);
            let _ = ws_sink.send(Message::Binary(pkt.to_vec())).await;
            // Server still needs to send the final result; don't close the socket.
        });

        // Event pump: Volc server frames -> AsrEvent.
        tokio::spawn(async move {
            while let Some(msg) = ws_stream.next().await {
                let bytes = match msg {
                    Ok(Message::Binary(b)) => b,
                    Ok(Message::Close(_)) => return,
                    Ok(Message::Ping(_) | Message::Pong(_) | Message::Frame(_)) => continue,
                    Ok(Message::Text(t)) => {
                        // Some endpoints send a final close text; treat as a structured error.
                        let _ = events_tx
                            .send(Err(AsrError::Protocol(format!(
                                "unexpected text frame: {}",
                                truncate(&t, 200)
                            ))))
                            .await;
                        return;
                    }
                    Err(e) => {
                        let _ = events_tx
                            .send(Err(AsrError::Network(format!("ws recv: {e}"))))
                            .await;
                        return;
                    }
                };
                let parsed = match proto::parse_server_message(&bytes) {
                    Ok(m) => m,
                    Err(e) => {
                        let _ = events_tx
                            .send(Err(AsrError::Protocol(format!("decode frame: {e}"))))
                            .await;
                        return;
                    }
                };
                match parsed.message_type {
                    proto::MSG_FULL_SERVER_RESPONSE => {
                        let parsed_payload = match parse_response_payload(&parsed.payload) {
                            Ok(p) => p,
                            Err(e) => {
                                let _ = events_tx.send(Err(e)).await;
                                return;
                            }
                        };
                        let is_final = parsed.sequence.map(|s| s < 0).unwrap_or(false)
                            || parsed.flags & proto::FLAG_LAST != 0;
                        if is_final {
                            let _ = events_tx
                                .send(Ok(AsrEvent::Final {
                                    text: parsed_payload.text,
                                    segment_id: parsed.sequence.unwrap_or(0).unsigned_abs() as u64,
                                }))
                                .await;
                            return;
                        } else if events_tx
                            .send(Ok(AsrEvent::Partial {
                                text: parsed_payload.text,
                                confidence: parsed_payload.confidence,
                            }))
                            .await
                            .is_err()
                        {
                            return;
                        }
                    }
                    proto::MSG_SERVER_ERROR => {
                        let err = parse_error_payload(&parsed.payload);
                        let _ = events_tx.send(Err(err)).await;
                        return;
                    }
                    other => {
                        tracing::debug!(message_type = other, "ignoring server message type");
                    }
                }
            }
        });

        Ok(AsrChannels {
            audio_tx,
            events_rx,
        })
    }
}

// ---- helpers ----

fn build_request(cfg: &DoubaoConfig) -> Result<Request, AsrError> {
    let mut req = cfg
        .endpoint
        .as_str()
        .into_client_request()
        .map_err(|e| AsrError::Network(format!("invalid url: {e}")))?;
    let bearer = format!("Bearer {}", cfg.api_key);
    req.headers_mut().insert(
        "Authorization",
        bearer
            .parse()
            .map_err(|e| AsrError::Network(format!("invalid Authorization header: {e}")))?,
    );
    if let Some(app) = &cfg.app_id {
        req.headers_mut().insert(
            "X-Api-App-Key",
            app.parse()
                .map_err(|e| AsrError::Network(format!("invalid X-Api-App-Key: {e}")))?,
        );
    }
    if let Some(rid) = &cfg.resource_id {
        req.headers_mut().insert(
            "X-Api-Resource-Id",
            rid.parse()
                .map_err(|e| AsrError::Network(format!("invalid X-Api-Resource-Id: {e}")))?,
        );
    }
    Ok(req)
}

fn build_config_payload(cfg: &DoubaoConfig, asr_cfg: &AsrConfig) -> serde_json::Value {
    serde_json::json!({
        "user": {
            "uid": "synapse-nexus"
        },
        "audio": {
            "format": "pcm",
            "rate": asr_cfg.sample_rate_hz,
            "bits": 16,
            "channel": 1,
            "language": cfg.language,
            "codec": "raw"
        },
        "request": {
            "model_name": "bigmodel",
            "reqid": Uuid::new_v4().to_string(),
            "show_utterances": false,
            "result_type": "single",
            "vad_segment": true
        }
    })
}

#[derive(Debug)]
struct ParsedResponse {
    text: String,
    confidence: f32,
}

fn parse_response_payload(bytes: &[u8]) -> Result<ParsedResponse, AsrError> {
    // Volc's payload shape (documented):
    // { "code": 1000, "message": "Success", "result": { "text": "...", "confidence": 0.9 } }
    // We tolerate small variations in nesting via serde_json::Value.
    let json: serde_json::Value = serde_json::from_slice(bytes)
        .map_err(|e| AsrError::Protocol(format!("decode response json: {e}")))?;

    if let Some(code) = json.get("code").and_then(|c| c.as_i64()) {
        if !(code == 0 || code == 1000) {
            let msg = json
                .get("message")
                .and_then(|m| m.as_str())
                .unwrap_or("(no message)");
            return Err(AsrError::Protocol(format!("server code {code}: {msg}")));
        }
    }

    // Try result.text or text at the root.
    let text = json
        .pointer("/result/text")
        .or_else(|| json.pointer("/text"))
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let confidence = json
        .pointer("/result/confidence")
        .or_else(|| json.pointer("/confidence"))
        .and_then(|v| v.as_f64())
        .map(|v| v as f32)
        .unwrap_or(1.0);

    Ok(ParsedResponse { text, confidence })
}

fn parse_error_payload(bytes: &[u8]) -> AsrError {
    let json: serde_json::Value = match serde_json::from_slice(bytes) {
        Ok(v) => v,
        Err(_) => return AsrError::Protocol("undecodable error frame".into()),
    };
    let code = json.get("code").and_then(|c| c.as_i64()).unwrap_or(-1);
    let msg = json
        .get("message")
        .and_then(|m| m.as_str())
        .unwrap_or("")
        .to_string();
    match code {
        // Auth-ish codes (Volc uses 4xx/55xx variants; conservative match)
        45_000_001..=45_000_999 => AsrError::Auth,
        // Quota/billing codes
        45_001_001..=45_001_999 => AsrError::QuotaExhausted,
        // Timeout codes
        45_100_001..=45_100_999 => AsrError::Timeout(Duration::from_secs(5)),
        _ => AsrError::Protocol(format!("server code {code}: {msg}")),
    }
}

fn classify_handshake_error(e: tokio_tungstenite::tungstenite::Error) -> AsrError {
    use tokio_tungstenite::tungstenite::http::StatusCode;
    use tokio_tungstenite::tungstenite::Error as TE;
    match e {
        TE::Http(resp) if resp.status() == StatusCode::UNAUTHORIZED => AsrError::Auth,
        TE::Http(resp) if resp.status() == StatusCode::FORBIDDEN => AsrError::Auth,
        TE::Http(resp) if resp.status() == StatusCode::TOO_MANY_REQUESTS => {
            AsrError::QuotaExhausted
        }
        other => AsrError::Network(format!("ws connect: {other}")),
    }
}

fn i16_to_le_bytes(samples: &[i16]) -> Vec<u8> {
    let mut out = Vec::with_capacity(samples.len() * 2);
    for s in samples {
        out.extend_from_slice(&s.to_le_bytes());
    }
    out
}

fn truncate(s: &str, max_chars: usize) -> String {
    if s.chars().count() <= max_chars {
        s.to_string()
    } else {
        let mut out: String = s.chars().take(max_chars).collect();
        out.push('…');
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_response_extracts_text_and_confidence() {
        let r =
            parse_response_payload(br#"{"code":1000,"result":{"text":"hello","confidence":0.92}}"#)
                .unwrap();
        assert_eq!(r.text, "hello");
        assert!((r.confidence - 0.92).abs() < 1e-6);
    }

    #[test]
    fn parse_response_tolerates_root_text() {
        let r = parse_response_payload(br#"{"text":"hi"}"#).unwrap();
        assert_eq!(r.text, "hi");
        assert_eq!(r.confidence, 1.0);
    }

    #[test]
    fn parse_response_rejects_error_code() {
        let err = parse_response_payload(br#"{"code":40001,"message":"bad request"}"#).unwrap_err();
        assert!(matches!(err, AsrError::Protocol(_)));
    }

    #[test]
    fn parse_error_maps_auth_code() {
        let err = parse_error_payload(br#"{"code":45000001,"message":"unauthorized"}"#);
        assert!(matches!(err, AsrError::Auth));
    }

    #[test]
    fn parse_error_maps_quota_code() {
        let err = parse_error_payload(br#"{"code":45001100,"message":"quota exhausted"}"#);
        assert!(matches!(err, AsrError::QuotaExhausted));
    }
}
