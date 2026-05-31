//! synapsed — the Synapse Nexus core daemon.
//!
//! M0 scope: bind a Unix domain socket, expose the v0 gRPC `SynapseFrontend`
//! service, and respond to every `StartSession` by streaming back a single
//! `FinalText { text: "hello world" }` event. No audio, no ASR provider, no
//! Polish — those land in M1 / M2.

use anyhow::{Context, Result};
use std::path::Path;
use tokio::net::UnixListener;
use tokio_stream::wrappers::UnixListenerStream;
use tonic::transport::Server;

use synapse_ipc::v0::synapse_frontend_server::SynapseFrontendServer;

use synapse_daemon::service;

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
    // Permission 0600 so other local users cannot send audio through us.
    set_socket_perms_0600(&socket_path)?;

    tracing::info!(socket = %socket_path.display(), "synapsed ready");

    let frontend = service::FrontendService;

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
