//! Synapse Nexus core orchestration.
//!
//! Owns the session state machine described in `docs/ARCHITECTURE.md` §3.3.

use uuid::Uuid;

pub mod state;

pub use state::{FsmEvent, Session, SessionState, TransitionError};

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
