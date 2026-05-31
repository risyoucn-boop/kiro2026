//! Library surface of the Synapse Nexus daemon.
//!
//! Exposed so integration tests can construct the gRPC service in-process.
//! The `synapsed` binary in `main.rs` is a thin wrapper that wires this
//! library to a Unix socket listener.

pub mod service;
