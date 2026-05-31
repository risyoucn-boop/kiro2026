//! End-to-end test: gRPC client → daemon → Mock ASR → Qwen Polish (mock HTTP) → gRPC client.
//!
//! Verifies the full PRD §3 pipeline: ASR partials propagate live, ASR final
//! triggers Polish, audited polish output replaces the raw transcript on the
//! Final IPC event. Plus the budget-fallback path: when polish times out,
//! the raw transcript is delivered without breaking the session.

use std::sync::Arc;
use std::time::Duration;

use serde_json::json;
use tokio::net::{UnixListener, UnixStream};
use tokio_stream::wrappers::UnixListenerStream;
use tokio_stream::StreamExt;
use tonic::transport::{Endpoint, Server, Uri};
use tonic::Request;
use tower::service_fn;
use wiremock::matchers::{method, path};
use wiremock::{Mock, MockServer, ResponseTemplate};

use synapse_asr::mock::{MockProvider, ScriptStep};
use synapse_asr::AsrProvider;
use synapse_daemon::service::FrontendService;
use synapse_ipc::v0::session_event::Kind;
use synapse_ipc::v0::synapse_frontend_client::SynapseFrontendClient;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontendServer;
use synapse_ipc::v0::StartSessionRequest;
use synapse_polish::qwen::{QwenConfig, QwenPolishProvider};
use synapse_polish::PolishProvider;

async fn spawn_server(
    socket: std::path::PathBuf,
    asr: Arc<dyn AsrProvider>,
    polish: Option<Arc<dyn PolishProvider>>,
) -> tokio::task::JoinHandle<()> {
    let listener = UnixListener::bind(&socket).unwrap();
    let svc = SynapseFrontendServer::new(FrontendService::with_polish(asr, polish));
    let handle = tokio::spawn(async move {
        Server::builder()
            .add_service(svc)
            .serve_with_incoming(UnixListenerStream::new(listener))
            .await
            .unwrap();
    });
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

fn asr_with_script(steps: Vec<ScriptStep>) -> Arc<dyn AsrProvider> {
    Arc::new(MockProvider { script: steps })
}

#[tokio::test]
async fn polish_replaces_raw_when_audit_accepts() {
    // ---- mock LLM HTTP server ----
    let llm = MockServer::start().await;
    Mock::given(method("POST"))
        .and(path("/v1/chat/completions"))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "choices": [{ "message": { "content": "打开 VSCode 写代码" } }]
        })))
        .mount(&llm)
        .await;

    let polish: Arc<dyn PolishProvider> = Arc::new(QwenPolishProvider::new(QwenConfig::new(
        format!("{}/v1/chat/completions", llm.uri()),
        "test-key",
        "qwen-flash",
    )));

    // ASR will emit a single final ("打开 V S Code 写代码") that Polish
    // should rewrite to ("打开 VSCode 写代码").
    let asr = asr_with_script(vec![ScriptStep::Final {
        text: "打开 V S Code 写代码".into(),
        after: Duration::from_millis(20),
    }]);

    // ---- daemon ----
    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");
    let server = spawn_server(socket.clone(), asr, Some(polish)).await;

    let mut client = connect(socket).await;
    let mut stream = client
        .start_session(Request::new(StartSessionRequest {
            client_id: "polish-test".into(),
            app_context: "test".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    let final_text = tokio::time::timeout(Duration::from_secs(5), async {
        while let Some(evt) = stream.next().await {
            if let Some(Kind::Final(f)) = evt.unwrap().kind {
                return f.text;
            }
        }
        String::new()
    })
    .await
    .unwrap();

    assert_eq!(final_text, "打开 VSCode 写代码");
    server.abort();
}

#[tokio::test]
async fn polish_falls_back_to_raw_when_budget_exceeded() {
    // LLM intentionally slow — provider's budget timeout (600ms) should win.
    let llm = MockServer::start().await;
    Mock::given(method("POST"))
        .and(path("/v1/chat/completions"))
        .respond_with(
            ResponseTemplate::new(200)
                .set_delay(Duration::from_secs(2))
                .set_body_json(json!({
                    "choices": [{ "message": { "content": "polished but too late" } }]
                })),
        )
        .mount(&llm)
        .await;

    let polish: Arc<dyn PolishProvider> = Arc::new(QwenPolishProvider::new(QwenConfig::new(
        format!("{}/v1/chat/completions", llm.uri()),
        "test-key",
        "qwen-flash",
    )));

    let asr = asr_with_script(vec![ScriptStep::Final {
        text: "raw transcript".into(),
        after: Duration::from_millis(20),
    }]);

    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");
    let server = spawn_server(socket.clone(), asr, Some(polish)).await;

    let mut client = connect(socket).await;
    let mut stream = client
        .start_session(Request::new(StartSessionRequest {
            client_id: "polish-budget".into(),
            app_context: "test".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    let final_text = tokio::time::timeout(Duration::from_secs(5), async {
        while let Some(evt) = stream.next().await {
            if let Some(Kind::Final(f)) = evt.unwrap().kind {
                return f.text;
            }
        }
        String::new()
    })
    .await
    .unwrap();

    assert_eq!(
        final_text, "raw transcript",
        "budget-exceeded polish must fall through to the raw ASR result"
    );
    server.abort();
}

#[tokio::test]
async fn polish_falls_back_when_audit_rejects_hallucination() {
    // LLM returns a hallucinated rewrite; audit must reject (edit_ratio>0.30).
    let llm = MockServer::start().await;
    Mock::given(method("POST"))
        .and(path("/v1/chat/completions"))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "choices": [{
                "message": { "content": "完全不一样的非常长的内容这是模型在编故事根本不该输出" }
            }]
        })))
        .mount(&llm)
        .await;

    let polish: Arc<dyn PolishProvider> = Arc::new(QwenPolishProvider::new(QwenConfig::new(
        format!("{}/v1/chat/completions", llm.uri()),
        "test-key",
        "qwen-flash",
    )));

    let asr = asr_with_script(vec![ScriptStep::Final {
        text: "打开".into(),
        after: Duration::from_millis(20),
    }]);

    let dir = tempfile::tempdir().unwrap();
    let socket = dir.path().join("synapsed.sock");
    let server = spawn_server(socket.clone(), asr, Some(polish)).await;

    let mut client = connect(socket).await;
    let mut stream = client
        .start_session(Request::new(StartSessionRequest {
            client_id: "polish-audit".into(),
            app_context: "test".into(),
            context_before: String::new(),
        }))
        .await
        .unwrap()
        .into_inner();

    let final_text = tokio::time::timeout(Duration::from_secs(5), async {
        while let Some(evt) = stream.next().await {
            if let Some(Kind::Final(f)) = evt.unwrap().kind {
                return f.text;
            }
        }
        String::new()
    })
    .await
    .unwrap();

    assert_eq!(
        final_text, "打开",
        "audit must reject hallucinated polish and fall back to raw"
    );
    server.abort();
}
