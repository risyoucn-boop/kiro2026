//! ASR provider abstraction. See ARCHITECTURE.md §3.2.
//!
//! Implementations (in submodules in M1+):
//!   - DoubaoStreaming  (primary)
//!   - Paraformer       (alternative)
//!   - SenseVoice       (alternative)
//!   - LocalSherpaOnnx  (offline fallback only — see PRD anti-goal §2.3)
//!
//! M0 status: trait stubbed, no implementations yet.

use async_trait::async_trait;
use std::time::Duration;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AsrError {
    #[error("network error: {0}")]
    Network(String),
    #[error("authentication failed")]
    Auth,
    #[error("provider returned malformed payload: {0}")]
    Protocol(String),
    #[error("session timed out after {0:?}")]
    Timeout(Duration),
    #[error("provider quota exhausted")]
    QuotaExhausted,
}

#[derive(Debug, Clone)]
pub struct AsrConfig {
    pub sample_rate_hz: u32,         // typically 16_000
    pub language_hints: Vec<String>, // e.g. ["zh", "en"]
}

#[derive(Debug, Clone)]
pub enum AsrEvent {
    Partial { text: String, confidence: f32 },
    Final { text: String, segment_id: u64 },
}

#[async_trait]
pub trait AsrSession: Send {
    async fn push_audio(&mut self, frame: &[i16]) -> Result<(), AsrError>;
    async fn next_event(&mut self) -> Option<Result<AsrEvent, AsrError>>;
    /// Consume the session and return the final concatenated transcript.
    async fn finalize(self: Box<Self>) -> Result<String, AsrError>;
}

#[async_trait]
pub trait AsrProvider: Send + Sync {
    fn name(&self) -> &'static str;
    async fn start_session(&self, cfg: AsrConfig) -> Result<Box<dyn AsrSession>, AsrError>;
}
