//! gRPC contract generated from `proto/synapse/v0/synapse.proto`.
//!
//! Re-exported under `v0::*` so callers spell out the version explicitly.
//! When the wire protocol changes incompatibly we add `v1` alongside,
//! never silently break v0.

pub mod v0 {
    tonic::include_proto!("synapse.v0");
}
