//! Polish (LLM post-processing) provider abstraction.
//!
//! See PRD FR-POLISH-01..05 and ARCHITECTURE.md §3.2 / §3.4.
//!
//! IMPORTANT contracts every implementation must respect:
//!   - Polish is best-effort. Exceeding `budget` => return Err and let the
//!     caller fall back to raw ASR (ARCHITECTURE.md §1 principle 5).
//!   - Output MUST go through `audit::audit_polish` before being committed
//!     (ARCHITECTURE.md §3.4) to prevent LLM hallucinations.

use async_trait::async_trait;
use std::time::Duration;
use thiserror::Error;

pub mod audit;

#[derive(Debug, Error)]
pub enum PolishError {
    #[error("polish budget exceeded ({0:?})")]
    BudgetExceeded(Duration),
    #[error("provider error: {0}")]
    Provider(String),
    #[error("output rejected by audit: {0}")]
    Rejected(String),
}

#[derive(Debug, Clone, Default)]
pub struct PolishRequest {
    pub raw: String,
    pub context_before: String,
    pub active_lexicon_ids: Vec<String>,
    /// Recent user corrections, oldest first. PRD FR-POLISH-05.
    pub user_corrections: Vec<UserCorrection>,
}

#[derive(Debug, Clone)]
pub struct UserCorrection {
    pub raw: String,
    pub user_final: String,
}

#[async_trait]
pub trait PolishProvider: Send + Sync {
    fn name(&self) -> &'static str;
    async fn polish(&self, req: PolishRequest, budget: Duration) -> Result<String, PolishError>;
}
