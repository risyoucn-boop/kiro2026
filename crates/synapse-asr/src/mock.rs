//! Mock ASR provider for tests and offline integration.
//!
//! Configurable: emits a scripted sequence of partials then a final, with
//! configurable inter-event delays. The mock does NOT inspect audio bytes
//! it merely drains them so callers can verify the audio path round-trips.

use std::time::Duration;

use async_trait::async_trait;
use tokio::sync::mpsc;
use tokio::time::sleep;

use crate::{AsrChannels, AsrConfig, AsrError, AsrEvent, AsrProvider};

#[derive(Debug, Clone)]
pub enum ScriptStep {
    Partial {
        text: String,
        after: Duration,
        confidence: f32,
    },
    Final {
        text: String,
        after: Duration,
    },
    Error {
        err: AsrError,
        after: Duration,
    },
}

#[derive(Debug, Clone)]
pub struct MockProvider {
    pub script: Vec<ScriptStep>,
}

impl MockProvider {
    /// A canned "hello world" script: two partials followed by a final.
    /// Total wall clock ~280 ms — well under the PRD §6 first-token P95 budget.
    pub fn hello_world() -> Self {
        Self {
            script: vec![
                ScriptStep::Partial {
                    text: "hello".into(),
                    after: Duration::from_millis(80),
                    confidence: 0.7,
                },
                ScriptStep::Partial {
                    text: "hello world".into(),
                    after: Duration::from_millis(80),
                    confidence: 0.9,
                },
                ScriptStep::Final {
                    text: "hello world".into(),
                    after: Duration::from_millis(120),
                },
            ],
        }
    }
}

#[async_trait]
impl AsrProvider for MockProvider {
    fn name(&self) -> &'static str {
        "mock"
    }

    async fn start(&self, _cfg: AsrConfig) -> Result<AsrChannels, AsrError> {
        let (audio_tx, mut audio_rx) = mpsc::channel::<Vec<i16>>(64);
        let (events_tx, events_rx) = mpsc::channel::<Result<AsrEvent, AsrError>>(8);

        // Drain audio in the background. Real providers would forward to
        // a WebSocket; the mock just counts frames it received via tracing.
        tokio::spawn(async move {
            let mut frames = 0u64;
            while audio_rx.recv().await.is_some() {
                frames += 1;
            }
            tracing::trace!(frames, "mock ASR drained audio stream");
        });

        let script = self.script.clone();
        tokio::spawn(async move {
            for step in script {
                match step {
                    ScriptStep::Partial {
                        text,
                        after,
                        confidence,
                    } => {
                        sleep(after).await;
                        if events_tx
                            .send(Ok(AsrEvent::Partial { text, confidence }))
                            .await
                            .is_err()
                        {
                            return;
                        }
                    }
                    ScriptStep::Final { text, after } => {
                        sleep(after).await;
                        let _ = events_tx
                            .send(Ok(AsrEvent::Final {
                                text,
                                segment_id: 1,
                            }))
                            .await;
                        return;
                    }
                    ScriptStep::Error { err, after } => {
                        sleep(after).await;
                        let _ = events_tx.send(Err(err)).await;
                        return;
                    }
                }
            }
        });

        Ok(AsrChannels {
            audio_tx,
            events_rx,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn hello_world_emits_two_partials_and_a_final() {
        let p = MockProvider::hello_world();
        let mut ch = p.start(AsrConfig::default()).await.unwrap();

        let mut partials = Vec::new();
        let mut final_text = None;
        while let Some(ev) = ch.events_rx.recv().await {
            match ev.unwrap() {
                AsrEvent::Partial { text, .. } => partials.push(text),
                AsrEvent::Final { text, .. } => {
                    final_text = Some(text);
                    break;
                }
            }
        }
        assert_eq!(
            partials,
            vec!["hello".to_string(), "hello world".to_string()]
        );
        assert_eq!(final_text.as_deref(), Some("hello world"));
    }
}
