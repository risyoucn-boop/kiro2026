//! Per-session orchestration.
//!
//! Each `StartSession` RPC spawns a [`drive`] task that:
//!
//! 1. Asks the configured `AsrProvider` for an [`AsrChannels`] pair.
//! 2. Pumps audio frames received over gRPC into the provider's `audio_tx`.
//! 3. Translates `AsrEvent`s coming back on `events_rx` into the v0
//!    `SessionEvent` IPC envelope and forwards them to the gRPC client.
//! 4. Runs the [`synapse_core::Session`] FSM in lock-step so we always
//!    have an authoritative state for telemetry and debugging.
//!
//! Polish / billing / lexicon are NOT wired in yet — those land in M2 / M3.
//! The current `drive` synthesises a `PolishSkipped` transition right after
//! every `AsrEvent::Final` so the FSM walks the full happy path.

use std::collections::HashMap;
use std::sync::Arc;

use tokio::sync::{mpsc, Mutex};
use tonic::Status;

use synapse_asr::{AsrChannels, AsrConfig, AsrError, AsrEvent, AsrProvider};
use synapse_core::{FsmEvent, Session, SessionId};
use synapse_ipc::v0::session_event::Kind;
use synapse_ipc::v0::{
    FinalText, PartialText, SessionError as IpcSessionError, SessionEvent as IpcEvent,
};

/// Channel buffer for downstream audio (gRPC client -> daemon).
const AUDIO_BUFFER_FRAMES: usize = 64;
/// Channel buffer for upstream events (daemon -> gRPC client).
const EVENTS_BUFFER: usize = 16;

/// Maps `session_id` to the channel that PushAudio writes into. Keeps the
/// PushAudio handler stateless and lets multiple gRPC streams (StartSession
/// and PushAudio) cooperate on the same session.
#[derive(Debug, Default)]
pub struct SessionRegistry {
    inner: Mutex<HashMap<String, mpsc::Sender<Vec<i16>>>>,
}

impl SessionRegistry {
    pub async fn register(&self, id: String, tx: mpsc::Sender<Vec<i16>>) {
        self.inner.lock().await.insert(id, tx);
    }

    pub async fn audio_tx(&self, id: &str) -> Option<mpsc::Sender<Vec<i16>>> {
        self.inner.lock().await.get(id).cloned()
    }

    pub async fn unregister(&self, id: &str) {
        self.inner.lock().await.remove(id);
    }
}

/// The four channel ends needed to connect a gRPC session to a `drive` task.
pub struct SessionPipes {
    /// gRPC's PushAudio handler sends frames here.
    pub grpc_audio_tx: mpsc::Sender<Vec<i16>>,
    /// `drive` reads frames from here.
    pub grpc_audio_rx: mpsc::Receiver<Vec<i16>>,
    /// `drive` writes IPC events here.
    pub grpc_events_tx: mpsc::Sender<Result<IpcEvent, Status>>,
    /// gRPC's StartSession streams this back to the client.
    pub grpc_events_rx: mpsc::Receiver<Result<IpcEvent, Status>>,
}

/// Construct the audio + events pipes for a fresh session.
pub fn build_pipes() -> SessionPipes {
    let (grpc_audio_tx, grpc_audio_rx) = mpsc::channel::<Vec<i16>>(AUDIO_BUFFER_FRAMES);
    let (grpc_events_tx, grpc_events_rx) = mpsc::channel::<Result<IpcEvent, Status>>(EVENTS_BUFFER);
    SessionPipes {
        grpc_audio_tx,
        grpc_audio_rx,
        grpc_events_tx,
        grpc_events_rx,
    }
}

/// Drive a single session until completion or failure.
pub async fn drive(
    id: SessionId,
    provider: Arc<dyn AsrProvider>,
    grpc_audio_rx: mpsc::Receiver<Vec<i16>>,
    grpc_events_tx: mpsc::Sender<Result<IpcEvent, Status>>,
) {
    let cfg = AsrConfig::default();
    let channels = match provider.start(cfg).await {
        Ok(c) => c,
        Err(e) => {
            tracing::warn!(session_id = %id.0, provider = provider.name(), error = %e, "asr.start failed");
            let _ = grpc_events_tx.send(Ok(error_event(&id, &e))).await;
            return;
        }
    };
    let AsrChannels {
        audio_tx: asr_audio_tx,
        events_rx: mut asr_events_rx,
    } = channels;

    let mut session = Session::new(id.clone());
    if let Err(err) = session.handle(FsmEvent::Started) {
        tracing::error!(?err, "fsm: failed to start");
        return;
    }

    // Audio pump: gRPC client -> ASR provider.
    let pump = {
        let id = id.clone();
        let mut grpc_audio_rx = grpc_audio_rx;
        let asr_audio_tx = asr_audio_tx.clone();
        tokio::spawn(async move {
            let mut frames = 0u64;
            while let Some(frame) = grpc_audio_rx.recv().await {
                if asr_audio_tx.send(frame).await.is_err() {
                    break;
                }
                frames += 1;
            }
            // Closing all senders signals end-of-utterance to the provider.
            drop(asr_audio_tx);
            tracing::debug!(session_id = %id.0, frames, "audio pump ended");
        })
    };
    drop(asr_audio_tx); // pump owns its clone now

    // Event pump: ASR provider -> gRPC client. Also drives the FSM.
    while let Some(ev_or_err) = asr_events_rx.recv().await {
        match ev_or_err {
            Ok(AsrEvent::Partial { text, confidence }) => {
                if let Err(err) = session.handle(FsmEvent::Partial(text.clone())) {
                    tracing::warn!(?err, "fsm rejected Partial; ignoring");
                }
                let evt = IpcEvent {
                    session_id: id.0.clone(),
                    kind: Some(Kind::Partial(PartialText { text, confidence })),
                };
                if grpc_events_tx.send(Ok(evt)).await.is_err() {
                    // Client dropped the stream; abort.
                    break;
                }
            }
            Ok(AsrEvent::Final { text, segment_id }) => {
                if let Err(err) = session.handle(FsmEvent::Final(text.clone())) {
                    tracing::warn!(?err, "fsm rejected Final; aborting");
                    break;
                }
                // M1: Polish provider not wired. Mark skipped so the FSM walks
                // the full happy path. M2 will run the polish step here.
                let _ = session.handle(FsmEvent::PolishSkipped);

                let evt = IpcEvent {
                    session_id: id.0.clone(),
                    kind: Some(Kind::Final(FinalText { text, segment_id })),
                };
                let _ = grpc_events_tx.send(Ok(evt)).await;
                let _ = session.handle(FsmEvent::Committed);
                break;
            }
            Err(e) => {
                tracing::warn!(session_id = %id.0, error = %e, "asr error");
                let _ = grpc_events_tx.send(Ok(error_event(&id, &e))).await;
                let _ = session.handle(FsmEvent::Failed(e.to_string()));
                break;
            }
        }
    }

    pump.abort();
    tracing::info!(
        session_id = %id.0,
        state = ?session.state(),
        chars = session.transcript().chars().count(),
        "session ended"
    );
}

fn error_event(id: &SessionId, err: &AsrError) -> IpcEvent {
    let (code, retryable) = match err {
        AsrError::Network(_) => ("asr.network", true),
        AsrError::Auth => ("asr.auth", false),
        AsrError::Protocol(_) => ("asr.protocol", false),
        AsrError::Timeout(_) => ("asr.timeout", true),
        AsrError::QuotaExhausted => ("asr.quota_exhausted", false),
        AsrError::Closed => ("asr.closed", false),
    };
    IpcEvent {
        session_id: id.0.clone(),
        kind: Some(Kind::Error(IpcSessionError {
            code: code.into(),
            message: err.to_string(),
            retryable,
        })),
    }
}
