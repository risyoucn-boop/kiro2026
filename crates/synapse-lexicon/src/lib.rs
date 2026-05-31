//! Domain lexicons. See PRD FR-POLISH-03..05.
//!
//! M0 status: data types only. SQLite persistence in M2 (ARCHITECTURE §5.1).

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Eq, PartialEq, Serialize, Deserialize)]
pub enum LexiconCategory {
    Code,
    Ai,
    General,
    User,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LexiconEntry {
    pub category: LexiconCategory,
    /// Optional incorrect form to match against.
    pub pattern: Option<String>,
    /// Canonical form to insert.
    pub replacement: String,
    /// Higher = stronger preference. Default 1.0.
    pub weight: f32,
}
