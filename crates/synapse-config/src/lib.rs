//! Config + platform paths.

use anyhow::{Context, Result};
use std::path::PathBuf;

/// Default IPC socket path used by the daemon and frontends.
///
/// Linux: `$XDG_RUNTIME_DIR/synapse-nexus/synapsed.sock` if `XDG_RUNTIME_DIR`
/// is set (the systemd-managed runtime dir), otherwise `/tmp/synapse-nexus-<uid>/synapsed.sock`.
///
/// On Windows / iOS this function is unused; those platforms get their own
/// IPC paths added in v1.1 / v1.2.
pub fn default_socket_path() -> Result<PathBuf> {
    if let Some(runtime) = std::env::var_os("XDG_RUNTIME_DIR") {
        let mut p = PathBuf::from(runtime);
        p.push("synapse-nexus");
        return Ok(p.join("synapsed.sock"));
    }
    let uid = nix_uid();
    let mut p = PathBuf::from("/tmp");
    p.push(format!("synapse-nexus-{uid}"));
    Ok(p.join("synapsed.sock"))
}

/// User config dir, e.g. `~/.config/synapse-nexus/`.
pub fn config_dir() -> Result<PathBuf> {
    let dirs = directories::ProjectDirs::from("dev", "synapse-nexus", "synapse-nexus")
        .context("could not resolve user config dir (no $HOME?)")?;
    Ok(dirs.config_dir().to_path_buf())
}

/// Best-effort uid. Returns 0 when unavailable (Windows / no libc).
fn nix_uid() -> u32 {
    #[cfg(unix)]
    {
        // SAFETY: getuid is always safe to call.
        unsafe { libc_geteuid() }
    }
    #[cfg(not(unix))]
    {
        0
    }
}

#[cfg(unix)]
extern "C" {
    #[link_name = "geteuid"]
    fn libc_geteuid() -> u32;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn socket_path_under_runtime_dir() {
        std::env::set_var("XDG_RUNTIME_DIR", "/run/user/1000");
        let p = default_socket_path().unwrap();
        assert!(p.to_string_lossy().contains("synapse-nexus"));
        assert!(p.to_string_lossy().ends_with("synapsed.sock"));
    }
}
