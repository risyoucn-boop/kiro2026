//! Audio capture. See ARCHITECTURE §3.1 (synapse-audio) and TV-2.
//!
//! M0 status: type-only stub. cpal integration arrives in M1 once TV-2
//! (PipeWire 16kHz mono capture) is verified on Ubuntu 23.10.

#[derive(Debug, Clone, Copy)]
pub struct AudioFormat {
    pub sample_rate_hz: u32,
    pub channels: u16,
    pub bits_per_sample: u16,
}

pub const FORMAT_16K_MONO_S16: AudioFormat = AudioFormat {
    sample_rate_hz: 16_000,
    channels: 1,
    bits_per_sample: 16,
};
