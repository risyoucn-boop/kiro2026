//! Integration tests for `QwenPolishProvider` against a real local HTTP server.
//!
//! Uses [`wiremock`] to stand up an OpenAI-compatible chat completions
//! endpoint on `127.0.0.1:<random>` and exercise the provider end-to-end.

use std::time::Duration;

use serde_json::json;
use wiremock::matchers::{header, method, path};
use wiremock::{Mock, MockServer, ResponseTemplate};

use synapse_polish::qwen::{QwenConfig, QwenPolishProvider};
use synapse_polish::{PolishError, PolishProvider, PolishRequest, UserCorrection};

fn req(raw: &str) -> PolishRequest {
    PolishRequest {
        raw: raw.into(),
        ..Default::default()
    }
}

fn cfg(server_uri: &str, key: &str) -> QwenConfig {
    QwenConfig::new(
        format!("{server_uri}/v1/chat/completions"),
        key,
        "qwen-flash",
    )
}

#[tokio::test]
async fn happy_path_returns_polished_text() {
    let server = MockServer::start().await;
    Mock::given(method("POST"))
        .and(path("/v1/chat/completions"))
        .and(header("authorization", "Bearer secret-123"))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "choices": [{
                "message": {"content": "打开 VSCode 写代码"}
            }]
        })))
        .mount(&server)
        .await;

    let provider = QwenPolishProvider::new(cfg(&server.uri(), "secret-123"));
    let polished = provider
        .polish(req("打开 V S Code 写代码"), Duration::from_secs(2))
        .await
        .unwrap();
    assert_eq!(polished, "打开 VSCode 写代码");
}

#[tokio::test]
async fn strips_code_fences_from_model_output() {
    let server = MockServer::start().await;
    Mock::given(method("POST"))
        .and(path("/v1/chat/completions"))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "choices": [{
                "message": {"content": "```\nhello world\n```"}
            }]
        })))
        .mount(&server)
        .await;

    let provider = QwenPolishProvider::new(cfg(&server.uri(), "k"));
    let polished = provider
        .polish(req("hello world"), Duration::from_secs(2))
        .await
        .unwrap();
    assert_eq!(polished, "hello world");
}

#[tokio::test]
async fn audit_rejects_excessive_rewrite() {
    let server = MockServer::start().await;
    // Model rewrites the input completely — should be rejected by audit.
    Mock::given(method("POST"))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "choices": [{
                "message": {"content": "完全不一样的非常长的内容这是模型在编故事"}
            }]
        })))
        .mount(&server)
        .await;

    let provider = QwenPolishProvider::new(cfg(&server.uri(), "k"));
    let err = provider
        .polish(req("打开"), Duration::from_secs(2))
        .await
        .unwrap_err();
    match err {
        PolishError::Rejected(reason) => {
            assert!(reason.contains("edit_ratio"), "got: {reason}");
        }
        other => panic!("expected Rejected, got {other:?}"),
    }
}

#[tokio::test]
async fn budget_exceeded_is_returned_as_typed_error() {
    let server = MockServer::start().await;
    Mock::given(method("POST"))
        .respond_with(
            ResponseTemplate::new(200)
                .set_delay(Duration::from_secs(2))
                .set_body_json(json!({
                    "choices": [{ "message": {"content": "too late"} }]
                })),
        )
        .mount(&server)
        .await;

    let provider = QwenPolishProvider::new(cfg(&server.uri(), "k"));
    let err = provider
        .polish(req("hi"), Duration::from_millis(150))
        .await
        .unwrap_err();
    assert!(
        matches!(err, PolishError::BudgetExceeded(d) if d == Duration::from_millis(150)),
        "got: {err:?}"
    );
}

#[tokio::test]
async fn http_error_is_provider_error() {
    let server = MockServer::start().await;
    Mock::given(method("POST"))
        .respond_with(ResponseTemplate::new(401).set_body_string("unauthorized"))
        .mount(&server)
        .await;

    let provider = QwenPolishProvider::new(cfg(&server.uri(), "wrong"));
    let err = provider
        .polish(req("hi"), Duration::from_secs(2))
        .await
        .unwrap_err();
    match err {
        PolishError::Provider(msg) => {
            assert!(msg.contains("401"), "got: {msg}");
        }
        other => panic!("expected Provider, got {other:?}"),
    }
}

#[tokio::test]
async fn empty_raw_short_circuits_without_calling_provider() {
    let server = MockServer::start().await;
    // No mock — if the provider hits the server, it'll get 404 and we'll see Provider error.
    let provider = QwenPolishProvider::new(cfg(&server.uri(), "k"));
    let polished = provider
        .polish(req(""), Duration::from_secs(2))
        .await
        .unwrap();
    assert_eq!(polished, "");
}

#[tokio::test]
async fn user_message_carries_context_lexicons_and_corrections() {
    use std::sync::Arc;
    use std::sync::Mutex;
    use wiremock::Match;

    // Custom matcher that captures the request body so we can assert on it.
    struct CaptureBody(Arc<Mutex<Option<String>>>);
    impl Match for CaptureBody {
        fn matches(&self, request: &wiremock::Request) -> bool {
            *self.0.lock().unwrap() = Some(String::from_utf8_lossy(&request.body).to_string());
            true
        }
    }

    let captured = Arc::new(Mutex::new(None));
    let server = MockServer::start().await;
    Mock::given(CaptureBody(captured.clone()))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "choices": [{ "message": {"content": "ok"} }]
        })))
        .mount(&server)
        .await;

    let provider = QwenPolishProvider::new(cfg(&server.uri(), "k"));
    let _ = provider
        .polish(
            PolishRequest {
                raw: "打开 V S Code".into(),
                context_before: "前文是".into(),
                active_lexicon_ids: vec!["code".into(), "ai".into()],
                user_corrections: vec![UserCorrection {
                    raw: "Rest API".into(),
                    user_final: "Rust API".into(),
                }],
            },
            Duration::from_secs(2),
        )
        .await;

    let body = captured.lock().unwrap().clone().expect("body captured");
    assert!(body.contains("前文是"), "context: {body}");
    assert!(body.contains("code"), "lexicons: {body}");
    assert!(body.contains("Rest API"), "corrections: {body}");
    assert!(body.contains("打开 V S Code"), "raw: {body}");
}
