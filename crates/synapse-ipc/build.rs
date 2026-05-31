use std::path::PathBuf;

fn main() {
    // Use a vendored protoc binary so contributors don't need to install
    // protobuf-compiler manually. Hermetic builds in CI as well.
    let protoc = protoc_bin_vendored::protoc_bin_path()
        .expect("protoc-bin-vendored should provide a protoc binary for this host");
    std::env::set_var("PROTOC", protoc);

    let manifest_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    let proto_root = manifest_dir
        .parent()
        .and_then(|p| p.parent())
        .map(|p| p.join("proto"))
        .expect("workspace layout: <root>/crates/<crate>/build.rs -> <root>/proto");

    let proto_file = proto_root.join("synapse/v0/synapse.proto");

    println!("cargo:rerun-if-changed={}", proto_file.display());

    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(&[proto_file], &[proto_root])
        .expect("failed to compile synapse.proto");
}
