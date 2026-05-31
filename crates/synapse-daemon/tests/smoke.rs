//! End-to-end smoke tests over the v0 IPC contract.
//!
//! Spins up an in-process tonic server bound to a Unix domain socket, then
//! drives it from a real `SynapseFrontendClient`. The server is configured
//! with `MockProvider::hello_world()` so we get deterministic Partials and
//! a Final, and we assert the gRPC stream surfaces them in order.

use std::sync::Arc;
use std::time::Duration;

use tokio::net::{UnixListener, UnixStream};
use tokio_stream::wrappers::UnixListenerStream;
use tokio_stream::StreamExt;
use tonic::transport::{Endpoint, Server, Uri};
use tonic::Request;
use tower::service_fn;

use synapse_asr::mock::MockProvider;
use synapse_asr::AsrProvider;
use synapse_daemon::service::FrontendService;
use synapse_ipc::v0::session_event::Kind;
use synapse_ipc::v0::synapse_frontend_client::SynapseFrontendClient;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontendServer;
use synapse_ipc::v0::StartSessionRequest;

async fn spawn_server(socket: std::path::PathBuf) -> tokio::task::JoinHandle<()> {
    let listener = UnixListener::bind(&socket).unwrap();
    let provider: Arc<dyn AsrProvider> = Arc::new(MockProvider::hello_world());
    let svc = SynapseFrontendServer::new(FrontendService::new(provider));
    let handle = tokio::spawn(async move {
        Server::builder()
            .add_service(svc)
            .serve_with_incoming(UnixListenerStream::new(listener))
            .await
            .unwrap();
    });
    // Tiny pause for the listener to be ready before clients connect.
    tokio::time::sleep(Duration::from_millis(50)).await;
    handle
}

async fn connect(socket: std::path::PathBuf) -> SynapseFrontendClient<tonic::transport::Channel> {
    let socket = Arc::new(socket);
    let channel = Endpoint::try_from("http://[::]:50051")
        .unwrap()
        .connect_with_connector(service_fn(move |_: Uri| {
            let p = socket.clone();
            async move {
                let stream = UnixStream::connect(&*p).await?;
                Ok::<_, std::io::Error>(hyper_util::rt::TokioIo::new(stream))
            }
        }))
        .await
        .unwrap();
    SynapseFrontendClient::new(channel)
}

#[tokio::test]
async fn streaming_emits_partials_then_final() {
    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");
    let server = spawn_server(socket.clone()).await;

    let mut client = connect(socket).await;
    let mut stream = client
        .start_session(Request::new(StartSessionRequest {
            client_id: "smoke".into(),
            app_context: "test".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    let mut partials = Vec::new();
    let mut final_text = None;

    // The whole hello-world script completes in ~280ms; give it 5s to be safe.
    let result = tokio::time::timeout(Duration::from_secs(5), async {
        while let Some(evt) = stream.next().await {
            match evt.unwrap().kind {
                Some(Kind::Partial(p)) => partials.push(p.text),
                Some(Kind::Final(f)) => {
                    final_text = Some(f.text);
                    break;
                }
                Some(Kind::Error(e)) => panic!("unexpected error event: {e:?}"),
                Some(Kind::Quota(_)) | None => {}
            }
        }
    })
    .await;
    result.expect("timed out waiting for Final");

    assert_eq!(
        partials,
        vec!["hello".to_string(), "hello world".to_string()],
        "partials must arrive in the scripted order"
    );
    assert_eq!(final_text.as_deref(), Some("hello world"));

    server.abort();
}

#[tokio::test]
async fn first_token_latency_under_budget() {
    // PRD §6 NFR: first-token P95 ≤ 1.5s. The mock script's first partial
    // is ~80ms after the StartSession resolves, so this is mostly a guard
    // against accidental head-of-line blocking in our IPC plumbing.
    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");
    let server = spawn_server(socket.clone()).await;

    let mut client = connect(socket).await;
    let started = std::time::Instant::now();

    let mut stream = client
        .start_session(Request::new(StartSessionRequest {
            client_id: "latency".into(),
            app_context: "test".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    // Wait for the first event (any kind). With the mock, this is the first Partial.
    let first = stream.next().await.expect("expected an event").unwrap();
    let elapsed = started.elapsed();

    assert!(
        matches!(first.kind, Some(Kind::Partial(_))),
        "first event from the mock must be a Partial, got {:?}",
        first.kind
    );
    // Generous bound — mock target is ~80ms; we assert <1500ms so flaky
    // CI hosts don't false-trip the PRD NFR check.
    assert!(
        elapsed < Duration::from_millis(1500),
        "first-token latency {elapsed:?} exceeds 1500ms budget"
    );

    server.abort();
}
