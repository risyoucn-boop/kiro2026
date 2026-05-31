//! gRPC service implementation.
//!
//! M0 returned a hard-coded "hello world". M1 wires a configurable
//! `AsrProvider` through `session::drive`, so what the client sees is
//! whatever the provider produces. The default binary uses the Mock
//! provider; future commits add Doubao streaming.

use std::sync::Arc;

use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;
use tonic::{Request, Response, Status, Streaming};

use synapse_asr::AsrProvider;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontend;
use synapse_ipc::v0::{
    AudioFrame, PushAudioAck, SessionEvent, StartSessionRequest, StopSessionRequest,
    StopSessionResponse,
};
use synapse_polish::PolishProvider;

use crate::session::{build_pipes, drive, SessionRegistry};

#[derive(Debug)]
pub struct FrontendService {
    provider: Arc<dyn AsrProvider>,
    polish: Option<Arc<dyn PolishProvider>>,
    registry: Arc<SessionRegistry>,
}

impl FrontendService {
    pub fn new(provider: Arc<dyn AsrProvider>) -> Self {
        Self::with_polish(provider, None)
    }

    pub fn with_polish(
        provider: Arc<dyn AsrProvider>,
        polish: Option<Arc<dyn PolishProvider>>,
    ) -> Self {
        Self {
            provider,
            polish,
            registry: Arc::new(SessionRegistry::default()),
        }
    }
}

#[tonic::async_trait]
impl SynapseFrontend for FrontendService {
    type StartSessionStream = ReceiverStream<Result<SessionEvent, Status>>;

    async fn start_session(
        &self,
        request: Request<StartSessionRequest>,
    ) -> Result<Response<Self::StartSessionStream>, Status> {
        let req = request.into_inner();
        let id = synapse_core::SessionId::new();

        tracing::info!(
            client_id = %req.client_id,
            app = %req.app_context,
            ctx_chars = req.context_before.chars().count(),
            session_id = %id.0,
            asr = self.provider.name(),
            "StartSession"
        );

        let pipes = build_pipes();
        self.registry
            .register(id.0.clone(), pipes.grpc_audio_tx)
            .await;

        let provider = self.provider.clone();
        let polish = self.polish.clone();
        let registry = self.registry.clone();
        let session_id_for_task = id.clone();
        tokio::spawn(async move {
            drive(
                session_id_for_task.clone(),
                provider,
                polish,
                pipes.grpc_audio_rx,
                pipes.grpc_events_tx,
            )
            .await;
            registry.unregister(&session_id_for_task.0).await;
        });

        Ok(Response::new(ReceiverStream::new(pipes.grpc_events_rx)))
    }

    async fn stop_session(
        &self,
        request: Request<StopSessionRequest>,
    ) -> Result<Response<StopSessionResponse>, Status> {
        let req = request.into_inner();
        // Removing from the registry means new PushAudio calls won't find
        // this session. The drive task will end naturally once any in-flight
        // PushAudio finishes (its sender clone goes out of scope) OR once
        // the ASR provider returns Final.
        self.registry.unregister(&req.session_id).await;
        tracing::info!(session_id = %req.session_id, "StopSession");
        Ok(Response::new(StopSessionResponse {}))
    }

    async fn push_audio(
        &self,
        request: Request<Streaming<AudioFrame>>,
    ) -> Result<Response<PushAudioAck>, Status> {
        let mut stream = request.into_inner();
        let mut received: u64 = 0;
        let mut tx_cache: Option<mpsc::Sender<Vec<i16>>> = None;

        while let Some(frame) = stream.message().await? {
            // Resolve the session on first frame; cache the sender for the rest.
            if tx_cache.is_none() {
                tx_cache = self.registry.audio_tx(&frame.session_id).await;
                if tx_cache.is_none() {
                    return Err(Status::not_found(format!(
                        "no active session: {}",
                        frame.session_id
                    )));
                }
            }
            let pcm = pcm_from_bytes(&frame.pcm)
                .map_err(|e| Status::invalid_argument(format!("bad pcm: {e}")))?;
            if let Some(tx) = &tx_cache {
                if tx.send(pcm).await.is_err() {
                    // Drive task ended; stop accepting frames.
                    break;
                }
                received += 1;
            }
        }

        Ok(Response::new(PushAudioAck { received }))
    }
}

fn pcm_from_bytes(bytes: &[u8]) -> Result<Vec<i16>, &'static str> {
    if !bytes.len().is_multiple_of(2) {
        return Err("byte length not aligned to i16");
    }
    Ok(bytes
        .chunks_exact(2)
        .map(|c| i16::from_le_bytes([c[0], c[1]]))
        .collect())
}

#[cfg(test)]
mod tests {
    use super::pcm_from_bytes;

    #[test]
    fn pcm_decodes_le_pairs() {
        // 0x0001 LE = 256, 0xFFFF LE = -1
        let bytes = [0x00, 0x01, 0xFF, 0xFF];
        assert_eq!(pcm_from_bytes(&bytes).unwrap(), vec![256, -1]);
    }

    #[test]
    fn pcm_rejects_odd_length() {
        assert!(pcm_from_bytes(&[0u8; 3]).is_err());
    }
}
