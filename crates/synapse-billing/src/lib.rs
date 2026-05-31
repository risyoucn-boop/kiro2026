//! Local billing. See PRD FR-BILL-01..06.
//!
//! Architectural choice (ARCHITECTURE §1 / PRD §10): billing is implemented
//! on the client, not on a SaaS proxy. The daemon counts characters in the
//! final committed text and reconciles with a thin backend. Anti-tamper via
//! HMAC-signed log (ARCHITECTURE §9).
//!
//! M0 status: types and arithmetic only. Persistence + HMAC in M3.

use thiserror::Error;

#[derive(Debug, Error)]
pub enum BillingError {
    #[error("insufficient quota: have {have} chars, need {need}")]
    InsufficientQuota { have: i64, need: i64 },
}

/// Billing units are 1e-6 yuan ("micros") to avoid floats.
pub type CostMicros = i64;

#[derive(Debug, Clone, Copy)]
pub struct PricingTier {
    pub name: &'static str,
    pub micros_per_char: CostMicros,
}

pub const FREE_TRIAL_CHARS: i64 = 1_000;

/// PRD §10.1 (placeholder values — to be replaced before launch).
pub const TIER_ENTRY: PricingTier = PricingTier {
    name: "entry",
    micros_per_char: 200,
};
pub const TIER_STANDARD: PricingTier = PricingTier {
    name: "standard",
    micros_per_char: 167,
};
pub const TIER_PRO: PricingTier = PricingTier {
    name: "pro",
    micros_per_char: 133,
};

#[derive(Debug, Clone, Copy)]
pub struct Quota {
    pub remaining_chars: i64,
}

impl Quota {
    pub fn try_charge(&mut self, chars: i64) -> Result<(), BillingError> {
        if chars > self.remaining_chars {
            return Err(BillingError::InsufficientQuota {
                have: self.remaining_chars,
                need: chars,
            });
        }
        self.remaining_chars -= chars;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn charge_deducts_balance() {
        let mut q = Quota {
            remaining_chars: 100,
        };
        q.try_charge(30).unwrap();
        assert_eq!(q.remaining_chars, 70);
    }

    #[test]
    fn charge_fails_when_insufficient() {
        let mut q = Quota {
            remaining_chars: 10,
        };
        assert!(q.try_charge(50).is_err());
    }
}
