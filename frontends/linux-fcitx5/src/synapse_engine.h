// Synapse Nexus — Fcitx5 input method engine.
//
// M0 status: keypress hook only. Commits the literal string "hello world"
// when Super+Space is pressed, so we can prove end-to-end commitString
// works in both X11 and Wayland (TV-1 in ROADMAP M0).
//
// IPC integration (gRPC client to synapsed) lands as a follow-up commit
// once tonic-cpp / grpc++ pulls and Wayland TV-1 are both green.

#pragma once

#include <fcitx/inputmethodengine.h>
#include <fcitx/instance.h>

namespace synapse {

class SynapseEngine final : public fcitx::InputMethodEngineV2 {
  public:
    explicit SynapseEngine(fcitx::Instance *instance);
    ~SynapseEngine() override = default;

    // fcitx::InputMethodEngine
    void keyEvent(const fcitx::InputMethodEntry &entry, fcitx::KeyEvent &event) override;

  private:
    fcitx::Instance *instance_;
};

}  // namespace synapse
