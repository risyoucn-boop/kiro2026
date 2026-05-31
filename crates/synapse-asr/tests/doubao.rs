//! Integration tests for `DoubaoAsrProvider` against an inline mock that
//! speaks the documented Volc bigmodel binary protocol.
//!
//! These tests prove the binary frame round-trips end-to-end without any
//! external dependency or API key.

use std::time::Duration;

use bytes::{BufMut, BytesMut};
use futures_util::{SinkExt, StreamExt};
use tokio::net::TcpListener;
use tokio_tungstenite::accept_hdr_async;
use tokio_tungstenite::tungstenite::handshake::server::{Request, Response};
use tokio_tungstenite::tungstenite::Message;

use synapse_asr::doubao::proto;
use synapse_asr::doubao::{DoubaoAsrProvider, DoubaoConfig};
use synapse_asr::{AsrConfig, AsrError, AsrEvent, AsrProvider};

// ---- mock Volc/Doubao server ----

#[derive(Debug, Clone)]
enum Step {
    /// Drain inbound binary frames classified as `MSG_AUDIO_ONLY_REQUEST`
    /// until N have been seen.
    ExpectAudioFrames(usize),
    /// Send a server response with the given JSON payload and sequence.
    /// `final_marker = true` sets `FLAG_LAST` and a negative sequence.
    SendResponse {
        json: &'static str,
        sequence: i32,
        final_marker: bool,
    },
    /// Send an error frame and close.
    SendError {
        code: i64,
        message: &'static str,
    },
    Pause(Duration),
}

struct MockDoubao {
    url: String,
    /// Receives the Authorization header the server saw on upgrade.
    seen_auth: tokio::sync::oneshot::Receiver<Option<String>>,
    /// Receives the JSON config the client sent in the first frame.
    seen_config: tokio::sync::oneshot::Receiver<serde_json::Value>,
    _handle: tokio::task::JoinHandle<()>,
}

impl MockDoubao {
    async fn start(script: Vec<Step>) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let port = listener.local_addr().unwrap().port();
        let url = format!("ws://127.0.0.1:{port}");
        let (auth_tx, auth_rx) = tokio::sync::oneshot::channel();
        let (cfg_tx, cfg_rx) = tokio::sync::oneshot::channel();

        let handle = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();

            let auth = std::sync::Arc::new(std::sync::Mutex::new(None::<String>));
            let auth_clone = auth.clone();
            let callback = move |req: &Request, resp: Response| {
                if let Some(v) = req.headers().get("Authorization") {
                    if let Ok(s) = v.to_str() {
                        *auth_clone.lock().unwrap() = Some(s.to_string());
                    }
                }
                Ok(resp)
            };
            let ws = accept_hdr_async(stream, callback).await.unwrap();
            let _ = auth_tx.send(auth.lock().unwrap().clone());

            let (mut tx, mut rx) = ws.split();

            // First frame must be the JSON config (full client request).
            let first = rx
                .next()
                .await
                .expect("expected client frame")
                .expect("client frame was an error");
            let bytes = match first {
                Message::Binary(b) => b,
                other => panic!("expected binary frame, got {other:?}"),
            };
            let parsed = proto::parse_server_message(&bytes).expect("parse client frame");
            assert_eq!(parsed.message_type, proto::MSG_FULL_CLIENT_REQUEST);
            let cfg_value: serde_json::Value =
                serde_json::from_slice(&parsed.payload).expect("decode config");
            let _ = cfg_tx.send(cfg_value);

            for step in script {
                match step {
                    Step::ExpectAudioFrames(n) => {
                        let mut got = 0;
                        while got < n {
                            match rx.next().await {
                                Some(Ok(Message::Binary(b))) => {
                                    if let Ok(p) = proto::parse_server_message(&b) {
                                        if p.message_type == proto::MSG_AUDIO_ONLY_REQUEST {
                                            got += 1;
                                        }
                                    }
                                }
                                Some(Ok(_)) => {}
                                Some(Err(_)) | None => return,
                            }
                        }
                    }
                    Step::SendResponse {
                        json,
                        sequence,
                        final_marker,
                    } => {
                        let frame = encode_response(json.as_bytes(), sequence, final_marker);
                        if tx.send(Message::Binary(frame.to_vec())).await.is_err() {
                            return;
                        }
                        if final_marker {
                            let _ = tx.close().await;
                            return;
                        }
                    }
                    Step::SendError { code, message } => {
                        let body = serde_json::json!({"code": code, "message": message});
                        let bytes = serde_json::to_vec(&body).unwrap();
                        let frame = encode_error_frame(&bytes);
                        let _ = tx.send(Message::Binary(frame.to_vec())).await;
                        let _ = tx.close().await;
                        return;
                    }
                    Step::Pause(d) => tokio::time::sleep(d).await,
                }
            }
        });

        tokio::time::sleep(Duration::from_millis(20)).await;

        Self {
            url,
            seen_auth: auth_rx,
            seen_config: cfg_rx,
            _handle: handle,
        }
    }
}

/// Build a server-side `MSG_FULL_SERVER_RESPONSE` frame with the given
/// JSON payload + sequence + final marker.
fn encode_response(json: &[u8], sequence: i32, is_final: bool) -> BytesMut {
    let mut flags = proto::FLAG_HAS_SEQUENCE;
    if is_final {
        flags |= proto::FLAG_LAST;
    }
    let mut buf = BytesMut::new();
    buf.put_u8((proto::PROTO_VERSION << 4) | proto::HEADER_SIZE_4B);
    buf.put_u8((proto::MSG_FULL_SERVER_RESPONSE << 4) | flags);
    buf.put_u8((proto::SER_JSON << 4) | proto::CMP_NONE);
    buf.put_u8(0);
    buf.put_i32(sequence);
    buf.put_u32(json.len() as u32);
    buf.put_slice(json);
    buf
}

fn encode_error_frame(json: &[u8]) -> BytesMut {
    let mut buf = BytesMut::new();
    buf.put_u8((proto::PROTO_VERSION << 4) | proto::HEADER_SIZE_4B);
    buf.put_u8(proto::MSG_SERVER_ERROR << 4);
    buf.put_u8((proto::SER_JSON << 4) | proto::CMP_NONE);
    buf.put_u8(0);
    buf.put_u32(json.len() as u32);
    buf.put_slice(json);
    buf
}

// ---- tests ----

#[tokio::test]
async fn doubao_provider_round_trips_partials_and_final() {
    let server = MockDoubao::start(vec![
        Step::Pause(Duration::from_millis(20)),
        Step::SendResponse {
            json: r#"{"code":1000,"result":{"text":"hello","confidence":0.7}}"#,
            sequence: 1,
            final_marker: false,
        },
        Step::ExpectAudioFrames(1),
        Step::SendResponse {
            json: r#"{"code":1000,"result":{"text":"hello world","confidence":0.9}}"#,
            sequence: 2,
            final_marker: false,
        },
        Step::SendResponse {
            json: r#"{"code":1000,"result":{"text":"hello world","confidence":0.95}}"#,
            sequence: -3,
            final_marker: true,
        },
    ])
    .await;

    let cfg = DoubaoConfig {
        endpoint: server.url.clone(),
        api_key: "ark-test-key".into(),
        app_id: None,
        resource_id: None,
        language: "zh-CN".into(),
        display_name: Some("doubao_test"),
    };
    let provider = DoubaoAsrProvider::new(cfg);

    let mut ch = provider.start(AsrConfig::default()).await.unwrap();
    ch.audio_tx.send(vec![0i16; 320]).await.unwrap();
    ch.audio_tx.send(vec![0i16; 320]).await.unwrap();
    drop(ch.audio_tx);

    let mut partials = Vec::new();
    let mut final_text = None;
    let mut final_seg = None;

    let collect = tokio::time::timeout(Duration::from_secs(5), async {
        while let Some(ev) = ch.events_rx.recv().await {
            match ev.unwrap() {
                AsrEvent::Partial { text, .. } => partials.push(text),
                AsrEvent::Final { text, segment_id } => {
                    final_text = Some(text);
                    final_seg = Some(segment_id);
                    break;
                }
            }
        }
    })
    .await;
    collect.expect("timed out");

    assert_eq!(
        partials,
        vec!["hello".to_string(), "hello world".to_string()]
    );
    assert_eq!(final_text.as_deref(), Some("hello world"));
    assert_eq!(final_seg, Some(3)); // unsigned absolute value of -3
}

#[tokio::test]
async fn doubao_bearer_lands_on_upgrade_and_config_carries_settings() {
    let server = MockDoubao::start(vec![Step::SendResponse {
        json: r#"{"code":1000,"result":{"text":"ok"}}"#,
        sequence: -1,
        final_marker: true,
    }])
    .await;
    let auth_rx = server.seen_auth;
    let cfg_rx = server.seen_config;

    let cfg = DoubaoConfig {
        endpoint: server.url.clone(),
        api_key: "ark-secret-shh".into(),
        app_id: None,
        resource_id: None,
        language: "zh-CN".into(),
        display_name: None,
    };
    let provider = DoubaoAsrProvider::new(cfg);
    let mut ch = provider.start(AsrConfig::default()).await.unwrap();
    drop(ch.audio_tx);
    while ch.events_rx.recv().await.is_some() {}

    let seen_auth = tokio::time::timeout(Duration::from_secs(2), auth_rx)
        .await
        .unwrap()
        .unwrap();
    assert_eq!(seen_auth.as_deref(), Some("Bearer ark-secret-shh"));

    let seen_cfg = tokio::time::timeout(Duration::from_secs(2), cfg_rx)
        .await
        .unwrap()
        .unwrap();
    assert_eq!(
        seen_cfg.pointer("/audio/rate"),
        Some(&serde_json::json!(16000))
    );
    assert_eq!(
        seen_cfg.pointer("/audio/language"),
        Some(&serde_json::json!("zh-CN"))
    );
    assert_eq!(
        seen_cfg.pointer("/audio/format"),
        Some(&serde_json::json!("pcm"))
    );
}

#[tokio::test]
async fn doubao_server_error_frame_propagates_as_asr_error() {
    let server = MockDoubao::start(vec![Step::SendError {
        code: 45_000_001,
        message: "unauthorized",
    }])
    .await;

    let cfg = DoubaoConfig {
        endpoint: server.url.clone(),
        api_key: "ark-test".into(),
        app_id: None,
        resource_id: None,
        language: "zh-CN".into(),
        display_name: None,
    };
    let provider = DoubaoAsrProvider::new(cfg);
    let mut ch = provider.start(AsrConfig::default()).await.unwrap();

    let evt = tokio::time::timeout(Duration::from_secs(2), ch.events_rx.recv())
        .await
        .unwrap()
        .expect("event");
    match evt {
        Err(AsrError::Auth) => {}
        other => panic!("expected AsrError::Auth, got {other:?}"),
    }
}
