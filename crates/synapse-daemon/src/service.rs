//! gRPC service implementation. M0: returns a literal "hello world".

use synapse_ipc::v0::session_event::Kind;
use synapse_ipc::v0::synapse_frontend_server::SynapseFrontend;
use synapse_ipc::v0::{
    AudioFrame, FinalText, PushAudioAck, SessionEvent, StartSessionRequest, StopSessionRequest,
    StopSessionResponse,
};
use tokio_stream::wrappers::ReceiverStream;
use tonic::{Request, Response, Status, Streaming};

#[derive(Debug)]
pub struct FrontendService;

#[tonic::async_trait]
impl SynapseFrontend for FrontendService {
    type StartSessionStream = ReceiverStream<Result<SessionEvent, Status>>;

    async fn start_session(
        &self,
        request: Request<StartSessionRequest>,
    ) -> Result<Response<Self::StartSessionStream>, Status> {
        let req = request.into_inner();
        let session_id = synapse_core::SessionId::new().0;

        tracing::info!(
            client_id = %req.client_id,
            app_context = %req.app_context,
            ctx_len = req.context_before.chars().count(),
            session_id = %session_id,
            "StartSession (M0 stub: emitting hello world)"
        );

        let (tx, rx) = tokio::sync::mpsc::channel::<Result<SessionEvent, Status>>(8);
        let sid = session_id.clone();
        tokio::spawn(async move {
            let evt = SessionEvent {
                session_id: sid,
                kind: Some(Kind::Final(FinalText {
                    text: "hello world".to_string(),
                    segment_id: 1,
                })),
            };
            // Best-effort send; if the client dropped the stream we just exit.
            let _ = tx.send(Ok(evt)).await;
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }

    async fn stop_session(
        &self,
        request: Request<StopSessionRequest>,
    ) -> Result<Response<StopSessionResponse>, Status> {
        let req = request.into_inner();
        tracing::info!(session_id = %req.session_id, "StopSession");
        Ok(Response::new(StopSessionResponse {}))
    }

    async fn push_audio(
        &self,
        request: Request<Streaming<AudioFrame>>,
    ) -> Result<Response<PushAudioAck>, Status> {
        // M0: count frames and discard. M1 hands them to the ASR session.
        let mut stream = request.into_inner();
        let mut received: u64 = 0;
        while let Some(frame) = stream.message().await? {
            received += 1;
            tracing::trace!(seq = frame.seq, bytes = frame.pcm.len(), "audio frame");
        }
        Ok(Response::new(PushAudioAck { received }))
    }
}
