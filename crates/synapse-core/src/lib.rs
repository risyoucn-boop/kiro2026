//! Synapse Nexus core orchestration.
//!
//! Owns the session state machine described in `docs/ARCHITECTURE.md` §3.3:
//! `Idle -> Recording -> Recognizing -> Polishing -> Committing -> Idle`.
//!
//! M0 status: skeleton only. Full state machine wiring in M1.

use uuid::Uuid;

/// A dictation session — one push-to-talk press, one identifier.
#[derive(Debug, Clone, Eq, PartialEq, Hash)]
pub struct SessionId(pub String);

impl SessionId {
    pub fn new() -> Self {
        Self(Uuid::new_v4().to_string())
    }
}

impl Default for SessionId {
    fn default() -> Self {
        Self::new()
    }
}

/// Session lifecycle states. See ARCHITECTURE.md §3.3.
#[derive(Debug, Clone, Copy, Eq, PartialEq)]
pub enum SessionState {
    Idle,
    Recording,
    Recognizing,
    Polishing,
    Committing,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn session_id_is_unique() {
        let a = SessionId::new();
        let b = SessionId::new();
        assert_ne!(a, b);
    }
}
