//! Integration tests for `StreamingAsrProvider` against a real WebSocket
//! server (running on localhost). The test server is implemented inline
//! using tokio-tungstenite and reads our v0 JSON control protocol.
//!
//! These tests prove the wire format end-to-end without any external
//! dependency or API key.

use std::time::Duration;

use futures_util::{SinkExt, StreamExt};
use tokio::net::TcpListener;
use tokio_tungstenite::accept_async;
use tokio_tungstenite::tungstenite::Message;

use synapse_asr::streaming::{AuthMode, StreamingAsrProvider, StreamingProviderConfig};
use synapse_asr::{AsrConfig, AsrError, AsrEvent, AsrProvider};

// ----- Mock WS server -----

/// A scripted step for the mock server. Runs in order.
#[derive(Debug, Clone)]
enum Step {
    /// Drain inbound binary frames until we've received at least N. (Skips other frame types.)
    ExpectAudioFrames(usize),
    /// Send a `partial` text frame.
    SendPartial { text: &'static str, confidence: f32 },
    /// Send a `final` text frame and close.
    SendFinal { text: &'static str, segment_id: u64 },
    /// Send an `error` text frame and close.
    SendError {
        code: &'static str,
        message: &'static str,
        retryable: bool,
    },
    /// Sleep this long.
    Pause(Duration),
}

struct MockServer {
    url: String,
    /// What auth header (if any) the server saw on the upgrade. Set after handshake.
    pub seen_auth: tokio::sync::oneshot::Receiver<Option<String>>,
    _handle: tokio::task::JoinHandle<()>,
}

impl MockServer {
    async fn start(script: Vec<Step>) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let port = listener.local_addr().unwrap().port();
        let url = format!("ws://127.0.0.1:{port}");
        let (auth_tx, auth_rx) = tokio::sync::oneshot::channel();

        let handle = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();

            // Capture the Authorization header off the upgrade request.
            let auth = std::sync::Arc::new(std::sync::Mutex::new(None::<String>));
            let auth_clone = auth.clone();
            let callback = move |req: &tokio_tungstenite::tungstenite::handshake::server::Request,
                                 resp: tokio_tungstenite::tungstenite::handshake::server::Response| {
                if let Some(v) = req.headers().get("Authorization") {
                    if let Ok(s) = v.to_str() {
                        *auth_clone.lock().unwrap() = Some(s.to_string());
                    }
                }
                Ok(resp)
            };
            let ws = tokio_tungstenite::accept_hdr_async(stream, callback)
                .await
                .unwrap();
            let _ = auth_tx.send(auth.lock().unwrap().clone());

            let (mut tx, mut rx) = ws.split();

            // Always read and discard the `start` text frame first.
            let _start_frame = rx.next().await;

            for step in script {
                match step {
                    Step::ExpectAudioFrames(n) => {
                        let mut got = 0;
                        while got < n {
                            match rx.next().await {
                                Some(Ok(Message::Binary(_))) => got += 1,
                                Some(Ok(_)) => {} // ignore text/ping/pong/close
                                Some(Err(_)) | None => return,
                            }
                        }
                    }
                    Step::SendPartial { text, confidence } => {
                        let json = serde_json::json!({
                            "type": "partial",
                            "text": text,
                            "confidence": confidence,
                        })
                        .to_string();
                        if tx.send(Message::Text(json)).await.is_err() {
                            return;
                        }
                    }
                    Step::SendFinal { text, segment_id } => {
                        let json = serde_json::json!({
                            "type": "final",
                            "text": text,
                            "segment_id": segment_id,
                        })
                        .to_string();
                        let _ = tx.send(Message::Text(json)).await;
                        let _ = tx.close().await;
                        return;
                    }
                    Step::SendError {
                        code,
                        message,
                        retryable,
                    } => {
                        let json = serde_json::json!({
                            "type": "error",
                            "code": code,
                            "message": message,
                            "retryable": retryable,
                        })
                        .to_string();
                        let _ = tx.send(Message::Text(json)).await;
                        let _ = tx.close().await;
                        return;
                    }
                    Step::Pause(d) => tokio::time::sleep(d).await,
                }
            }
        });

        // Tiny pause for listener to be ready.
        tokio::time::sleep(Duration::from_millis(20)).await;

        // Touch unused symbol to avoid warnings.
        let _ = accept_async::<tokio::net::TcpStream>;

        Self {
            url,
            seen_auth: auth_rx,
            _handle: handle,
        }
    }
}

// ----- Tests -----

#[tokio::test]
async fn streaming_provider_round_trips_partials_and_final() {
    let server = MockServer::start(vec![
        Step::Pause(Duration::from_millis(20)),
        Step::SendPartial {
            text: "hello",
            confidence: 0.7,
        },
        Step::SendPartial {
            text: "hello world",
            confidence: 0.9,
        },
        Step::ExpectAudioFrames(2),
        Step::SendFinal {
            text: "hello world",
            segment_id: 42,
        },
    ])
    .await;

    let provider = StreamingAsrProvider::new(StreamingProviderConfig {
        endpoint: server.url.clone(),
        auth: AuthMode::None,
        display_name: Some("test"),
    });

    let mut ch = provider.start(AsrConfig::default()).await.unwrap();
    // Push some audio so the server's ExpectAudioFrames step is satisfied.
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
    collect.expect("timed out waiting for Final");

    assert_eq!(
        partials,
        vec!["hello".to_string(), "hello world".to_string()]
    );
    assert_eq!(final_text.as_deref(), Some("hello world"));
    assert_eq!(final_seg, Some(42));
}

#[tokio::test]
async fn server_error_maps_to_asr_error() {
    let server = MockServer::start(vec![
        Step::Pause(Duration::from_millis(20)),
        Step::SendError {
            code: "auth",
            message: "bad token",
            retryable: false,
        },
    ])
    .await;

    let provider = StreamingAsrProvider::new(StreamingProviderConfig {
        endpoint: server.url.clone(),
        auth: AuthMode::None,
        display_name: Some("test"),
    });

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

#[tokio::test]
async fn bearer_token_is_sent_on_upgrade() {
    let server = MockServer::start(vec![
        Step::Pause(Duration::from_millis(20)),
        Step::SendFinal {
            text: "ok",
            segment_id: 1,
        },
    ])
    .await;
    let auth_rx = server.seen_auth;

    let provider = StreamingAsrProvider::new(StreamingProviderConfig {
        endpoint: server.url.clone(),
        auth: AuthMode::Bearer("secret-123".into()),
        display_name: Some("test"),
    });

    let mut ch = provider.start(AsrConfig::default()).await.unwrap();
    drop(ch.audio_tx);
    // Drain
    while ch.events_rx.recv().await.is_some() {}

    let seen = tokio::time::timeout(Duration::from_secs(2), auth_rx)
        .await
        .unwrap()
        .unwrap();
    assert_eq!(seen.as_deref(), Some("Bearer secret-123"));
}
