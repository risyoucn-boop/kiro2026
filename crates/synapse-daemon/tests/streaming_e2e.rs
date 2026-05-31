//! Full end-to-end test: gRPC client → daemon → StreamingAsrProvider → WS mock server.
//!
//! Exercises the entire pipeline of the v0 IPC contract running against a
//! real (in-process) WebSocket ASR backend implementing our v0 control
//! protocol. This is the closest sandbox-only proof we can produce that
//! the production setup with a real ASR vendor will work.

use std::sync::Arc;
use std::time::Duration;

use futures_util::{SinkExt, StreamExt};
use tokio::net::{TcpListener, UnixListener, UnixStream};
use tokio_stream::wrappers::UnixListenerStream;
use tokio_tungstenite::accept_async;
use tokio_tungstenite::tungstenite::Message;
use tonic::transport::{Endpoint, Server, Uri};
use tonic::Request;
use tower::service_fn;

use synapse_asr::streaming::{AuthMode, StreamingAsrProvider, StreamingProviderConfig};
use synapse_asr::AsrProvider;
use synapse_daemon::service::FrontendService;
use synapse_ipc::v0::session_event::Kind;
use synapse_ipc::v0::synapse_frontend_client::SynapseFrontendClient;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontendServer;
use synapse_ipc::v0::StartSessionRequest;

#[tokio::test]
async fn end_to_end_streaming_through_grpc() {
    // ---- 1. spin up a WebSocket ASR backend ----
    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let port = listener.local_addr().unwrap().port();
    let ws_url = format!("ws://127.0.0.1:{port}");
    tokio::spawn(async move {
        let (stream, _) = listener.accept().await.unwrap();
        let ws = accept_async(stream).await.unwrap();
        let (mut tx, mut rx) = ws.split();

        // Read start frame
        let _ = futures_util::StreamExt::next(&mut rx).await;
        // First partial after a moment
        tokio::time::sleep(Duration::from_millis(30)).await;
        SinkExt::send(
            &mut tx,
            Message::Text(r#"{"type":"partial","text":"打开","confidence":0.7}"#.into()),
        )
        .await
        .unwrap();

        // Wait for a couple of audio frames
        let mut got = 0;
        while got < 2 {
            match futures_util::StreamExt::next(&mut rx).await {
                Some(Ok(Message::Binary(_))) => got += 1,
                Some(Ok(_)) => {}
                _ => return,
            }
        }

        // Second partial
        SinkExt::send(
            &mut tx,
            Message::Text(r#"{"type":"partial","text":"打开 V S Code","confidence":0.85}"#.into()),
        )
        .await
        .unwrap();
        tokio::time::sleep(Duration::from_millis(40)).await;

        // Final
        SinkExt::send(
            &mut tx,
            Message::Text(r#"{"type":"final","text":"打开 V S Code","segment_id":7}"#.into()),
        )
        .await
        .unwrap();
        let _ = SinkExt::close(&mut tx).await;
    });

    // ---- 2. spin up the daemon configured to use the streaming provider ----
    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");
    let unix_listener = UnixListener::bind(&socket).unwrap();

    let provider: Arc<dyn AsrProvider> =
        Arc::new(StreamingAsrProvider::new(StreamingProviderConfig {
            endpoint: ws_url,
            auth: AuthMode::None,
            display_name: Some("test_streaming"),
        }));
    let svc = SynapseFrontendServer::new(FrontendService::new(provider));
    let server = tokio::spawn(async move {
        Server::builder()
            .add_service(svc)
            .serve_with_incoming(UnixListenerStream::new(unix_listener))
            .await
            .unwrap();
    });
    tokio::time::sleep(Duration::from_millis(50)).await;

    // ---- 3. gRPC client ----
    let socket_for_client = Arc::new(socket.clone());
    let channel = Endpoint::try_from("http://[::]:50051")
        .unwrap()
        .connect_with_connector(service_fn(move |_: Uri| {
            let p = socket_for_client.clone();
            async move {
                let stream = UnixStream::connect(&*p).await?;
                Ok::<_, std::io::Error>(hyper_util::rt::TokioIo::new(stream))
            }
        }))
        .await
        .unwrap();
    let mut client = SynapseFrontendClient::new(channel);

    let mut stream = client
        .start_session(Request::new(StartSessionRequest {
            client_id: "e2e".into(),
            app_context: "vscode".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    // ---- 4. push some audio in parallel via PushAudio ----
    // (We could also send via a stream, but for a smoke test, two frames is enough.)
    let push_client = client.clone();
    let session_id_holder: Arc<tokio::sync::Mutex<Option<String>>> =
        Arc::new(tokio::sync::Mutex::new(None));
    let sid_for_push = session_id_holder.clone();
    let push_handle = tokio::spawn(async move {
        // Wait until we know the session id (set when the first event arrives).
        let id = loop {
            if let Some(sid) = sid_for_push.lock().await.clone() {
                break sid;
            }
            tokio::time::sleep(Duration::from_millis(10)).await;
        };
        let frames = futures_util::stream::iter(vec![
            synapse_ipc::v0::AudioFrame {
                session_id: id.clone(),
                pcm: vec![0u8; 640], // 320 i16 samples = 20ms @ 16kHz
                seq: 0,
            },
            synapse_ipc::v0::AudioFrame {
                session_id: id.clone(),
                pcm: vec![0u8; 640],
                seq: 1,
            },
        ]);
        let mut c = push_client;
        let _ = c.push_audio(Request::new(frames)).await;
    });

    // ---- 5. collect events ----
    let mut partials = Vec::new();
    let mut final_text = None;

    let result = tokio::time::timeout(Duration::from_secs(5), async {
        while let Some(evt) = tokio_stream::StreamExt::next(&mut stream).await {
            let evt = evt.unwrap();
            // Capture session id from the first event.
            if session_id_holder.lock().await.is_none() {
                *session_id_holder.lock().await = Some(evt.session_id.clone());
            }
            match evt.kind {
                Some(Kind::Partial(p)) => partials.push(p.text),
                Some(Kind::Final(f)) => {
                    final_text = Some(f.text);
                    break;
                }
                Some(Kind::Error(e)) => panic!("unexpected error: {e:?}"),
                Some(Kind::Quota(_)) | None => {}
            }
        }
    })
    .await;
    result.expect("timed out");

    let _ = push_handle.await;

    assert_eq!(
        partials,
        vec!["打开".to_string(), "打开 V S Code".to_string()]
    );
    assert_eq!(final_text.as_deref(), Some("打开 V S Code"));

    server.abort();
}
