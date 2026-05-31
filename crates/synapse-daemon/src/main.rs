//! synapsed — the Synapse Nexus core daemon.

use std::path::Path;
use std::sync::Arc;

use anyhow::{Context, Result};
use tokio::net::UnixListener;
use tokio_stream::wrappers::UnixListenerStream;
use tonic::transport::Server;

use synapse_asr::doubao::{DoubaoAsrProvider, DoubaoConfig};
use synapse_asr::mock::MockProvider;
use synapse_asr::streaming::{AuthMode, StreamingAsrProvider, StreamingProviderConfig};
use synapse_asr::AsrProvider;
use synapse_daemon::service::FrontendService;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontendServer;
use synapse_polish::qwen::{QwenConfig, QwenPolishProvider};
use synapse_polish::PolishProvider;

/// Pick the Polish (LLM post-processing) provider, or `None` for raw-only.
///
/// Selection precedence:
///
/// 1. `SYNAPSE_POLISH_PROVIDER=none` — explicitly disabled.
/// 2. `SYNAPSE_POLISH_PROVIDER=qwen` — Qwen-Flash / OpenAI-compatible.
/// 3. If `SYNAPSE_POLISH_API_KEY` and `SYNAPSE_POLISH_ENDPOINT` are both set,
///    use `qwen`.
/// 4. Otherwise: `None` (no polish; daemon emits raw ASR results).
///
/// `qwen` env vars:
///   - `SYNAPSE_POLISH_ENDPOINT=...` (required, full chat completions URL)
///   - `SYNAPSE_POLISH_API_KEY=...` (required, Bearer token)
///   - `SYNAPSE_POLISH_MODEL=...` (optional, default `qwen-flash`)
fn pick_polish_provider() -> Option<Arc<dyn PolishProvider>> {
    let kind = std::env::var("SYNAPSE_POLISH_PROVIDER")
        .ok()
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| {
            if env_nonempty("SYNAPSE_POLISH_API_KEY") && env_nonempty("SYNAPSE_POLISH_ENDPOINT") {
                "qwen".into()
            } else {
                "none".into()
            }
        });

    match kind.as_str() {
        "none" => None,
        "qwen" => {
            let endpoint = std::env::var("SYNAPSE_POLISH_ENDPOINT")
                .ok()
                .unwrap_or_default();
            let api_key = std::env::var("SYNAPSE_POLISH_API_KEY")
                .ok()
                .unwrap_or_default();
            let model = std::env::var("SYNAPSE_POLISH_MODEL")
                .ok()
                .filter(|s| !s.is_empty())
                .unwrap_or_else(|| "qwen-flash".into());
            if endpoint.is_empty() || api_key.is_empty() {
                tracing::error!(
                    "SYNAPSE_POLISH_PROVIDER=qwen requires SYNAPSE_POLISH_ENDPOINT and SYNAPSE_POLISH_API_KEY"
                );
                return None;
            }
            Some(Arc::new(QwenPolishProvider::new(QwenConfig::new(
                endpoint, api_key, model,
            ))))
        }
        other => {
            tracing::warn!(
                provider = other,
                "unknown SYNAPSE_POLISH_PROVIDER, falling back to none"
            );
            None
        }
    }
}

fn env_nonempty(name: &str) -> bool {
    std::env::var(name).map(|s| !s.is_empty()).unwrap_or(false)
}

/// Pick the ASR provider based on env vars. Defaults to the deterministic
/// Mock provider so first-run users without any config still get a working
/// "hello world" demo without needing API keys.
///
/// Selection precedence:
///
/// 1. `SYNAPSE_ASR_PROVIDER` (explicit): `mock | streaming_ws | doubao`
/// 2. If `SYNAPSE_DOUBAO_API_KEY` is set, use `doubao`.
/// 3. If `SYNAPSE_ASR_ENDPOINT` is set, use `streaming_ws`.
/// 4. Otherwise: `mock`.
///
/// Provider-specific env vars:
///
/// `streaming_ws`:
///   - `SYNAPSE_ASR_ENDPOINT=wss://...`
///   - `SYNAPSE_ASR_TOKEN=...` (optional bearer)
///
/// `doubao` (Volc bigmodel):
///   - `SYNAPSE_DOUBAO_ENDPOINT=...` (optional, defaults to public URL)
///   - `SYNAPSE_DOUBAO_API_KEY=ark-...` (required)
///   - `SYNAPSE_DOUBAO_APP_ID=...` (optional)
///   - `SYNAPSE_DOUBAO_RESOURCE_ID=...` (optional)
///   - `SYNAPSE_DOUBAO_LANGUAGE=zh-CN` (optional)
fn pick_provider() -> Arc<dyn AsrProvider> {
    let kind = std::env::var("SYNAPSE_ASR_PROVIDER")
        .ok()
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| {
            if env_nonempty("SYNAPSE_DOUBAO_API_KEY") {
                "doubao".into()
            } else if env_nonempty("SYNAPSE_ASR_ENDPOINT") {
                "streaming_ws".into()
            } else {
                "mock".into()
            }
        });

    match kind.as_str() {
        "doubao" => {
            let api_key = std::env::var("SYNAPSE_DOUBAO_API_KEY").unwrap_or_else(|_| {
                tracing::error!("SYNAPSE_ASR_PROVIDER=doubao but SYNAPSE_DOUBAO_API_KEY is empty");
                String::new()
            });
            let mut cfg = DoubaoConfig::new(api_key);
            if let Ok(ep) = std::env::var("SYNAPSE_DOUBAO_ENDPOINT") {
                if !ep.is_empty() {
                    cfg.endpoint = ep;
                }
            }
            cfg.app_id = std::env::var("SYNAPSE_DOUBAO_APP_ID")
                .ok()
                .filter(|s| !s.is_empty());
            cfg.resource_id = std::env::var("SYNAPSE_DOUBAO_RESOURCE_ID")
                .ok()
                .filter(|s| !s.is_empty());
            if let Ok(lang) = std::env::var("SYNAPSE_DOUBAO_LANGUAGE") {
                if !lang.is_empty() {
                    cfg.language = lang;
                }
            }
            Arc::new(DoubaoAsrProvider::new(cfg))
        }
        "streaming_ws" => {
            let endpoint = std::env::var("SYNAPSE_ASR_ENDPOINT").unwrap_or_default();
            let auth = std::env::var("SYNAPSE_ASR_TOKEN")
                .ok()
                .filter(|s| !s.is_empty())
                .map(AuthMode::Bearer)
                .unwrap_or(AuthMode::None);
            Arc::new(StreamingAsrProvider::new(StreamingProviderConfig {
                endpoint,
                auth,
                display_name: Some("streaming_ws"),
            }))
        }
        _ => Arc::new(MockProvider::hello_world()),
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    init_tracing();

    let socket_path = synapse_config::default_socket_path()?;
    prepare_socket_dir(&socket_path)?;
    if socket_path.exists() {
        std::fs::remove_file(&socket_path).with_context(|| {
            format!("failed to remove stale socket at {}", socket_path.display())
        })?;
    }

    let listener = UnixListener::bind(&socket_path)
        .with_context(|| format!("failed to bind {}", socket_path.display()))?;
    set_socket_perms_0600(&socket_path)?;

    let provider = pick_provider();
    let polish = pick_polish_provider();
    tracing::info!(
        socket = %socket_path.display(),
        asr_provider = provider.name(),
        polish_provider = polish.as_ref().map(|p| p.name()).unwrap_or("none"),
        "synapsed ready"
    );

    let frontend = FrontendService::with_polish(provider, polish);

    Server::builder()
        .add_service(SynapseFrontendServer::new(frontend))
        .serve_with_incoming(UnixListenerStream::new(listener))
        .await
        .context("gRPC server terminated unexpectedly")?;

    Ok(())
}

fn init_tracing() {
    use tracing_subscriber::{fmt, EnvFilter};
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("synapse=info,synapsed=info,info"));
    fmt().with_env_filter(filter).with_target(false).init();
}

fn prepare_socket_dir(socket_path: &Path) -> Result<()> {
    if let Some(parent) = socket_path.parent() {
        std::fs::create_dir_all(parent)
            .with_context(|| format!("failed to create {}", parent.display()))?;
    }
    Ok(())
}

#[cfg(unix)]
fn set_socket_perms_0600(socket_path: &Path) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;
    let mut perms = std::fs::metadata(socket_path)?.permissions();
    perms.set_mode(0o600);
    std::fs::set_permissions(socket_path, perms)?;
    Ok(())
}

#[cfg(not(unix))]
fn set_socket_perms_0600(_socket_path: &Path) -> Result<()> {
    Ok(())
}
