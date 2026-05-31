//! End-to-end smoke test: in-process tonic server over a Unix socket,
//! a client calls StartSession, receives "hello world".
//!
//! This is the minimum proof that the IPC contract round-trips.

use std::sync::Arc;
use tokio::net::{UnixListener, UnixStream};
use tokio_stream::wrappers::UnixListenerStream;
use tokio_stream::StreamExt;
use tonic::transport::{Endpoint, Server, Uri};
use tonic::Request;
use tower::service_fn;

use synapse_daemon::service::FrontendService;
use synapse_ipc::v0::session_event::Kind;
use synapse_ipc::v0::synapse_frontend_client::SynapseFrontendClient;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontendServer;
use synapse_ipc::v0::StartSessionRequest;

#[tokio::test]
async fn start_session_returns_hello_world() {
    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");

    // ---- server ----
    let listener = UnixListener::bind(&socket).unwrap();
    let svc = SynapseFrontendServer::new(FrontendService);
    let server = tokio::spawn(async move {
        Server::builder()
            .add_service(svc)
            .serve_with_incoming(UnixListenerStream::new(listener))
            .await
            .unwrap();
    });

    // give the server a tick to be ready
    tokio::time::sleep(std::time::Duration::from_millis(50)).await;

    // ---- client (Unix socket via tower service_fn) ----
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
            client_id: "test-client".into(),
            app_context: "test".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    let evt = stream
        .next()
        .await
        .expect("expected an event")
        .expect("event was an error");

    match evt.kind {
        Some(Kind::Final(f)) => assert_eq!(f.text, "hello world"),
        other => panic!("unexpected event: {other:?}"),
    }

    server.abort();
}
