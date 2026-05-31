//! ASR provider abstraction. See ARCHITECTURE.md §3.2.
//!
//! Implementations live in submodules:
//!   - `mock` — for tests / offline integration (always available)
//!   - DoubaoStreaming (coming in M1.2, real WebSocket)
//!   - Paraformer / SenseVoice (alternatives)
//!   - LocalSherpaOnnx (offline fallback only — PRD §2.3 forbids fully
//!     offline; this exists to cover network outages)
//!
//! ## Design note: channels, not `&mut self`
//!
//! An earlier sketch (M0) had `push_audio(&mut self)` and
//! `next_event(&mut self)` on a single trait object. That makes it
//! impossible to push audio and poll events concurrently inside a
//! `tokio::select!`, which is exactly what the daemon needs to do.
//!
//! Real implementations (WebSocket-based, gRPC-based) all internally
//! spawn their own driver task with one half pumping audio out and the
//! other half streaming events in. The trait now reflects that reality:
//! a session is a pair of channels.

use async_trait::async_trait;
use std::time::Duration;
use thiserror::Error;
use tokio::sync::mpsc;

pub mod mock;

#[derive(Debug, Error, Clone)]
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
    #[error("session was closed")]
    Closed,
}

#[derive(Debug, Clone)]
pub struct AsrConfig {
    pub sample_rate_hz: u32,
    /// BCP-47 language hints, e.g. ["zh", "en"].
    pub language_hints: Vec<String>,
}

impl Default for AsrConfig {
    fn default() -> Self {
        Self {
            sample_rate_hz: 16_000,
            language_hints: vec!["zh".into(), "en".into()],
        }
    }
}

#[derive(Debug, Clone)]
pub enum AsrEvent {
    Partial { text: String, confidence: f32 },
    Final { text: String, segment_id: u64 },
}

/// A live ASR session.
///
/// - Caller pushes 16 kHz mono i16 PCM frames into `audio_tx`. ~20ms / frame
///   is ideal. Closing `audio_tx` (drop the last clone) signals
///   end-of-utterance; the provider should then emit a final
///   `AsrEvent::Final` and close `events_rx`.
/// - Caller drains recognition events from `events_rx`. The receiver
///   closing means the provider has nothing more to say.
pub struct AsrChannels {
    pub audio_tx: mpsc::Sender<Vec<i16>>,
    pub events_rx: mpsc::Receiver<Result<AsrEvent, AsrError>>,
}

#[async_trait]
pub trait AsrProvider: Send + Sync + std::fmt::Debug {
    fn name(&self) -> &'static str;
    async fn start(&self, cfg: AsrConfig) -> Result<AsrChannels, AsrError>;
}
