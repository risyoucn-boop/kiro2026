//! Finite state machine for a dictation session.
//!
//! Mirrors the diagram in `docs/ARCHITECTURE.md` §3.3:
//!
//! ```text
//! Idle -> Recording -> Recognizing -> Polishing -> Committing -> Terminated
//!                          ^               |
//!                          +-- (partials) -+
//! ```
//!
//! Only the transitions explicitly enumerated below are valid. Anything else
//! returns `TransitionError`, which the daemon treats as an internal bug.
//!
//! Failure paths: any state can transition to `Terminated` via
//! `FsmEvent::Failed`. This is how we model "ASR network died",
//! "Polish budget exceeded with no fallback transcript", etc.

use thiserror::Error;

use crate::SessionId;

#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash)]
pub enum SessionState {
    Idle,
    Recording,
    Recognizing,
    Polishing,
    Committing,
    Terminated,
}

#[derive(Debug, Clone)]
pub enum FsmEvent {
    /// The session was started — first audio frame is incoming.
    Started,
    /// ASR provider produced a partial hypothesis.
    Partial(String),
    /// ASR provider produced a final transcript for the utterance.
    Final(String),
    /// Polish completed within budget and is accepted.
    PolishDone(String),
    /// Polish failed (budget / audit / provider error). Use raw transcript.
    PolishSkipped,
    /// Final text was sent to the frontend / committed to the input.
    Committed,
    /// Any failure that ends the session.
    Failed(String),
}

#[derive(Debug, Error)]
#[error("invalid transition from {from:?} on event {event}")]
pub struct TransitionError {
    pub from: SessionState,
    pub event: String,
}

#[derive(Debug)]
pub struct Session {
    id: SessionId,
    state: SessionState,
    transcript: String,
    failure: Option<String>,
}

impl Session {
    pub fn new(id: SessionId) -> Self {
        Self {
            id,
            state: SessionState::Idle,
            transcript: String::new(),
            failure: None,
        }
    }

    pub fn id(&self) -> &SessionId {
        &self.id
    }

    pub fn state(&self) -> SessionState {
        self.state
    }

    pub fn transcript(&self) -> &str {
        &self.transcript
    }

    pub fn failure(&self) -> Option<&str> {
        self.failure.as_deref()
    }

    pub fn handle(&mut self, event: FsmEvent) -> Result<SessionState, TransitionError> {
        use FsmEvent as E;
        use SessionState as S;
        let event_repr = format!("{event:?}");
        let new_state = match (self.state, &event) {
            (S::Idle, E::Started) => S::Recording,

            (S::Recording, E::Partial(t)) | (S::Recognizing, E::Partial(t)) => {
                self.transcript = t.clone();
                S::Recognizing
            }

            (S::Recording, E::Final(t)) | (S::Recognizing, E::Final(t)) => {
                self.transcript = t.clone();
                S::Polishing
            }

            (S::Polishing, E::PolishDone(t)) => {
                self.transcript = t.clone();
                S::Committing
            }
            // Polish failure keeps the raw transcript that was set on Final.
            (S::Polishing, E::PolishSkipped) => S::Committing,

            (S::Committing, E::Committed) => S::Terminated,

            (s, E::Failed(reason)) if s != S::Terminated => {
                self.failure = Some(reason.clone());
                S::Terminated
            }

            _ => {
                return Err(TransitionError {
                    from: self.state,
                    event: event_repr,
                })
            }
        };
        self.state = new_state;
        Ok(new_state)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn s() -> Session {
        Session::new(SessionId::new())
    }

    #[test]
    fn happy_path_with_partials_and_polish() {
        let mut sess = s();
        sess.handle(FsmEvent::Started).unwrap();
        assert_eq!(sess.state(), SessionState::Recording);

        sess.handle(FsmEvent::Partial("打开".into())).unwrap();
        assert_eq!(sess.state(), SessionState::Recognizing);
        assert_eq!(sess.transcript(), "打开");

        sess.handle(FsmEvent::Partial("打开 V S Code".into()))
            .unwrap();
        assert_eq!(sess.transcript(), "打开 V S Code");

        sess.handle(FsmEvent::Final("打开 V S Code".into()))
            .unwrap();
        assert_eq!(sess.state(), SessionState::Polishing);

        sess.handle(FsmEvent::PolishDone("打开 VSCode".into()))
            .unwrap();
        assert_eq!(sess.state(), SessionState::Committing);
        assert_eq!(sess.transcript(), "打开 VSCode");

        sess.handle(FsmEvent::Committed).unwrap();
        assert_eq!(sess.state(), SessionState::Terminated);
    }

    #[test]
    fn polish_skipped_keeps_raw_transcript() {
        let mut sess = s();
        sess.handle(FsmEvent::Started).unwrap();
        sess.handle(FsmEvent::Final("hello world".into())).unwrap();
        assert_eq!(sess.transcript(), "hello world");

        sess.handle(FsmEvent::PolishSkipped).unwrap();
        assert_eq!(sess.state(), SessionState::Committing);
        assert_eq!(
            sess.transcript(),
            "hello world",
            "raw transcript must survive Polish skip"
        );
    }

    #[test]
    fn final_directly_after_started_is_allowed() {
        // Some ASR providers emit only Final (no partials) for very short utterances.
        let mut sess = s();
        sess.handle(FsmEvent::Started).unwrap();
        sess.handle(FsmEvent::Final("hi".into())).unwrap();
        assert_eq!(sess.state(), SessionState::Polishing);
    }

    #[test]
    fn failure_terminates_from_any_active_state() {
        for start in [
            SessionState::Idle,
            SessionState::Recording,
            SessionState::Recognizing,
            SessionState::Polishing,
            SessionState::Committing,
        ] {
            let mut sess = s();
            // crude: drive into the desired start state
            match start {
                SessionState::Idle => {}
                SessionState::Recording => {
                    sess.handle(FsmEvent::Started).unwrap();
                }
                SessionState::Recognizing => {
                    sess.handle(FsmEvent::Started).unwrap();
                    sess.handle(FsmEvent::Partial("x".into())).unwrap();
                }
                SessionState::Polishing => {
                    sess.handle(FsmEvent::Started).unwrap();
                    sess.handle(FsmEvent::Final("x".into())).unwrap();
                }
                SessionState::Committing => {
                    sess.handle(FsmEvent::Started).unwrap();
                    sess.handle(FsmEvent::Final("x".into())).unwrap();
                    sess.handle(FsmEvent::PolishSkipped).unwrap();
                }
                _ => unreachable!(),
            }
            sess.handle(FsmEvent::Failed("net".into())).unwrap();
            assert_eq!(sess.state(), SessionState::Terminated);
            assert_eq!(sess.failure(), Some("net"));
        }
    }

    #[test]
    fn invalid_transition_is_rejected() {
        let mut sess = s();
        // Can't commit from Idle.
        let err = sess.handle(FsmEvent::Committed).unwrap_err();
        assert_eq!(err.from, SessionState::Idle);
        assert_eq!(
            sess.state(),
            SessionState::Idle,
            "state must not change on rejected event"
        );
    }

    #[test]
    fn terminated_is_absorbing() {
        let mut sess = s();
        sess.handle(FsmEvent::Failed("boom".into())).unwrap();
        assert_eq!(sess.state(), SessionState::Terminated);
        // Further events are rejected (terminated is absorbing).
        assert!(sess.handle(FsmEvent::Started).is_err());
    }
}
