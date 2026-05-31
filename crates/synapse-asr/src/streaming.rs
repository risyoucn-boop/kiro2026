//! Generic WebSocket streaming ASR provider.
//!
//! ## Wire protocol — Synapse Streaming ASR v0
//!
//! This is **our** control protocol, designed to be vendor-neutral and
//! easy to mock for tests. Real vendor protocols (Doubao binary, Paraformer
//! binary, ...) get wrapped in adapters that translate to/from this shape.
//!
//! ### Frame types
//!
//! Client → Server:
//!   - **binary** frames: 16 kHz mono i16 LE PCM, ~20ms / frame is ideal.
//!   - **text** frames (JSON):
//!     ```json
//!     {"type":"start","sample_rate_hz":16000,"language_hints":["zh","en"]}
//!     {"type":"finalize"}
//!     {"type":"keepalive"}
//!     ```
//!
//! Server → Client:
//!   - **text** frames (JSON):
//!     ```json
//!     {"type":"partial","text":"...","confidence":0.9}
//!     {"type":"final","text":"...","segment_id":1}
//!     {"type":"error","code":"...","message":"...","retryable":true}
//!     ```
//!
//! ### Lifecycle
//!
//! 1. Client connects with optional `Authorization: Bearer <token>` header.
//! 2. Client sends `start`. Server begins recognition.
//! 3. Client streams binary audio; server streams `partial` events.
//! 4. Client either drops audio_tx (graceful) or sends `finalize` (explicit).
//! 5. Server responds with one `final` event and closes the stream.
//!
//! ## Errors map cleanly to `AsrError`
//!
//! | Server `code` | Mapped variant      |
//! |---------------|---------------------|
//! | `auth`        | `AsrError::Auth`    |
//! | `quota`       | `AsrError::QuotaExhausted` |
//! | `timeout`     | `AsrError::Timeout` |
//! | _other_       | `AsrError::Protocol` |

use std::time::Duration;

use async_trait::async_trait;
use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use tokio::sync::mpsc;
use tokio_tungstenite::tungstenite::client::IntoClientRequest;
use tokio_tungstenite::tungstenite::handshake::client::Request;
use tokio_tungstenite::tungstenite::Message;

use crate::{AsrChannels, AsrConfig, AsrError, AsrEvent, AsrProvider};

/// Authentication strategy attached to the WebSocket upgrade request.
#[derive(Debug, Clone)]
pub enum AuthMode {
    None,
    Bearer(String),
}

#[derive(Debug, Clone)]
pub struct StreamingProviderConfig {
    /// Full WebSocket endpoint, e.g. `wss://example.com/v0/asr`.
    pub endpoint: String,
    pub auth: AuthMode,
    /// Optional name override for tracing / logging. Defaults to `"streaming_ws"`.
    pub display_name: Option<&'static str>,
}

#[derive(Debug)]
pub struct StreamingAsrProvider {
    cfg: StreamingProviderConfig,
}

impl StreamingAsrProvider {
    pub fn new(cfg: StreamingProviderConfig) -> Self {
        Self { cfg }
    }
}

// ---- on-the-wire envelopes ----

#[derive(Debug, Serialize)]
#[serde(tag = "type", rename_all = "snake_case")]
enum ClientMsg {
    Start {
        sample_rate_hz: u32,
        language_hints: Vec<String>,
    },
    Finalize,
    #[allow(dead_code)] // used by long-running connections; emitted by future keep-alive task
    Keepalive,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
enum ServerMsg {
    Partial {
        text: String,
        #[serde(default = "default_confidence")]
        confidence: f32,
    },
    Final {
        text: String,
        #[serde(default = "default_segment_id")]
        segment_id: u64,
    },
    Error {
        code: String,
        message: String,
        #[serde(default)]
        retryable: bool,
    },
}

fn default_confidence() -> f32 {
    1.0
}
fn default_segment_id() -> u64 {
    0
}

#[async_trait]
impl AsrProvider for StreamingAsrProvider {
    fn name(&self) -> &'static str {
        self.cfg.display_name.unwrap_or("streaming_ws")
    }

    async fn start(&self, cfg: AsrConfig) -> Result<AsrChannels, AsrError> {
        let req = build_request(&self.cfg.endpoint, &self.cfg.auth)?;
        tracing::debug!(endpoint = %self.cfg.endpoint, "ws connecting");
        let (ws_stream, _resp) = tokio_tungstenite::connect_async(req)
            .await
            .map_err(classify_handshake_error)?;
        let (mut ws_sink, mut ws_stream) = ws_stream.split();

        // Send the start envelope before handing channels back.
        let start = ClientMsg::Start {
            sample_rate_hz: cfg.sample_rate_hz,
            language_hints: cfg.language_hints.clone(),
        };
        let start_json = serde_json::to_string(&start)
            .map_err(|e| AsrError::Protocol(format!("encode start: {e}")))?;
        ws_sink
            .send(Message::Text(start_json))
            .await
            .map_err(|e| AsrError::Network(format!("ws send start: {e}")))?;

        let (audio_tx, mut audio_rx) = mpsc::channel::<Vec<i16>>(64);
        let (events_tx, events_rx) = mpsc::channel::<Result<AsrEvent, AsrError>>(8);

        // Audio pump: i16 frames → WS binary. On drop of all senders, sends Finalize.
        let events_tx_for_audio = events_tx.clone();
        tokio::spawn(async move {
            while let Some(frame) = audio_rx.recv().await {
                let bytes = i16_to_bytes_le(&frame);
                if let Err(e) = ws_sink.send(Message::Binary(bytes)).await {
                    let _ = events_tx_for_audio
                        .send(Err(AsrError::Network(format!("ws send audio: {e}"))))
                        .await;
                    return;
                }
            }
            // Audio stream closed: politely tell the server to wrap up.
            if let Ok(json) = serde_json::to_string(&ClientMsg::Finalize) {
                let _ = ws_sink.send(Message::Text(json)).await;
            }
            // Don't close the socket — server still needs to send Final.
        });

        // Event pump: WS text → AsrEvent.
        tokio::spawn(async move {
            while let Some(msg) = ws_stream.next().await {
                match msg {
                    Ok(Message::Text(text)) => match serde_json::from_str::<ServerMsg>(&text) {
                        Ok(ServerMsg::Partial { text, confidence }) => {
                            if events_tx
                                .send(Ok(AsrEvent::Partial { text, confidence }))
                                .await
                                .is_err()
                            {
                                return;
                            }
                        }
                        Ok(ServerMsg::Final { text, segment_id }) => {
                            let _ = events_tx
                                .send(Ok(AsrEvent::Final { text, segment_id }))
                                .await;
                            return;
                        }
                        Ok(ServerMsg::Error {
                            code,
                            message,
                            retryable,
                        }) => {
                            let err = map_server_error(&code, &message, retryable);
                            let _ = events_tx.send(Err(err)).await;
                            return;
                        }
                        Err(e) => {
                            let _ = events_tx
                                .send(Err(AsrError::Protocol(format!(
                                    "decode server msg: {e}; raw={}",
                                    truncate(&text, 200)
                                ))))
                                .await;
                            return;
                        }
                    },
                    Ok(Message::Close(_)) => return,
                    Ok(Message::Ping(_) | Message::Pong(_)) => continue,
                    Ok(Message::Binary(_)) | Ok(Message::Frame(_)) => continue,
                    Err(e) => {
                        let _ = events_tx
                            .send(Err(AsrError::Network(format!("ws recv: {e}"))))
                            .await;
                        return;
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

fn build_request(url: &str, auth: &AuthMode) -> Result<Request, AsrError> {
    let mut req = url
        .into_client_request()
        .map_err(|e| AsrError::Network(format!("invalid url: {e}")))?;
    if let AuthMode::Bearer(token) = auth {
        let val = format!("Bearer {token}");
        let header_val = val
            .parse()
            .map_err(|e| AsrError::Network(format!("invalid bearer header value: {e}")))?;
        req.headers_mut().insert("Authorization", header_val);
    }
    Ok(req)
}

fn classify_handshake_error(e: tokio_tungstenite::tungstenite::Error) -> AsrError {
    use tokio_tungstenite::tungstenite::http::StatusCode;
    use tokio_tungstenite::tungstenite::Error as TE;
    match e {
        TE::Http(resp) if resp.status() == StatusCode::UNAUTHORIZED => AsrError::Auth,
        TE::Http(resp) if resp.status() == StatusCode::TOO_MANY_REQUESTS => {
            AsrError::QuotaExhausted
        }
        other => AsrError::Network(format!("ws connect: {other}")),
    }
}

fn map_server_error(code: &str, message: &str, retryable: bool) -> AsrError {
    match code {
        "auth" => AsrError::Auth,
        "quota" | "quota_exhausted" => AsrError::QuotaExhausted,
        "timeout" => AsrError::Timeout(Duration::from_secs(5)),
        _ => AsrError::Protocol(format!("{code}: {message} (retryable={retryable})")),
    }
}

fn i16_to_bytes_le(samples: &[i16]) -> Vec<u8> {
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
    fn audio_bytes_are_little_endian() {
        // i16 = 256 little-endian = [0x00, 0x01]
        // i16 = -1  little-endian = [0xFF, 0xFF]
        let bytes = i16_to_bytes_le(&[256i16, -1i16]);
        assert_eq!(bytes, vec![0x00, 0x01, 0xFF, 0xFF]);
    }

    #[test]
    fn truncate_is_char_aware() {
        // CJK char each = 1 char (multi-byte). Truncation must not split bytes.
        let s = "你好世界你好世界";
        let t = truncate(s, 4);
        assert_eq!(t.chars().count(), 5); // 4 + ellipsis
        assert!(t.starts_with("你好世界"));
    }

    #[test]
    fn server_msg_decodes_partial_with_default_confidence() {
        let msg: ServerMsg = serde_json::from_str(r#"{"type":"partial","text":"hi"}"#).unwrap();
        match msg {
            ServerMsg::Partial { text, confidence } => {
                assert_eq!(text, "hi");
                assert_eq!(confidence, 1.0);
            }
            _ => panic!("expected Partial"),
        }
    }

    #[test]
    fn server_msg_decodes_error() {
        let msg: ServerMsg = serde_json::from_str(
            r#"{"type":"error","code":"auth","message":"bad token","retryable":false}"#,
        )
        .unwrap();
        match msg {
            ServerMsg::Error {
                code,
                message,
                retryable,
            } => {
                assert_eq!(code, "auth");
                assert_eq!(message, "bad token");
                assert!(!retryable);
            }
            _ => panic!("expected Error"),
        }
    }

    #[test]
    fn map_server_error_routes_known_codes() {
        assert!(matches!(
            map_server_error("auth", "", false),
            AsrError::Auth
        ));
        assert!(matches!(
            map_server_error("quota", "", false),
            AsrError::QuotaExhausted
        ));
        assert!(matches!(
            map_server_error("quota_exhausted", "", false),
            AsrError::QuotaExhausted
        ));
        assert!(matches!(
            map_server_error("timeout", "", false),
            AsrError::Timeout(_)
        ));
        assert!(matches!(
            map_server_error("something_else", "details", true),
            AsrError::Protocol(_)
        ));
    }
}
