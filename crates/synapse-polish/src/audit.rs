//! Hallucination audit for Polish output.
//!
//! ARCHITECTURE.md §3.4: A Polish result is rejected (and the raw ASR is
//! used instead) when:
//!   - Levenshtein edit ratio > 30%, OR
//!   - The polished text introduces named entities that don't appear in raw.
//!
//! M0 status: stub implementation. Real entity detection comes in M2.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AuditResult {
    Accept,
    Reject(RejectReason),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RejectReason {
    TooMuchChange,
    HallucinatedEntities(Vec<String>),
}

pub const MAX_EDIT_RATIO: f32 = 0.30;

pub fn audit(raw: &str, polished: &str) -> AuditResult {
    if raw.is_empty() {
        return AuditResult::Accept;
    }
    let raw_chars = raw.chars().count() as f32;
    let edit = levenshtein(raw, polished) as f32 / raw_chars;
    if edit > MAX_EDIT_RATIO {
        return AuditResult::Reject(RejectReason::TooMuchChange);
    }
    // TODO(M2): named-entity hallucination detection.
    AuditResult::Accept
}

/// Character-level Levenshtein distance.
fn levenshtein(a: &str, b: &str) -> usize {
    let a: Vec<char> = a.chars().collect();
    let b: Vec<char> = b.chars().collect();
    let (n, m) = (a.len(), b.len());
    if n == 0 {
        return m;
    }
    if m == 0 {
        return n;
    }
    let mut prev: Vec<usize> = (0..=m).collect();
    let mut curr = vec![0usize; m + 1];
    for i in 1..=n {
        curr[0] = i;
        for j in 1..=m {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            curr[j] = (curr[j - 1] + 1).min(prev[j] + 1).min(prev[j - 1] + cost);
        }
        std::mem::swap(&mut prev, &mut curr);
    }
    prev[m]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_minor_polish() {
        let raw = "打开 V S Code 写代码";
        let polished = "打开 VSCode 写代码";
        assert_eq!(audit(raw, polished), AuditResult::Accept);
    }

    #[test]
    fn rejects_excessive_rewrite() {
        let raw = "今天天气不错";
        let polished = "今天天气非常好我们一起去公园散步吧";
        assert!(matches!(
            audit(raw, polished),
            AuditResult::Reject(RejectReason::TooMuchChange)
        ));
    }

    #[test]
    fn empty_raw_accepts() {
        assert_eq!(audit("", "anything"), AuditResult::Accept);
    }
}
