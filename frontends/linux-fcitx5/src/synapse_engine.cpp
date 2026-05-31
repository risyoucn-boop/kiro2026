#include "synapse_engine.h"

#include <fcitx-utils/key.h>
#include <fcitx/inputcontext.h>

namespace synapse {

SynapseEngine::SynapseEngine(fcitx::Instance *instance) : instance_(instance) {
    (void)instance_;  // M0: instance kept for future use (notifications, watchers).
}

void SynapseEngine::keyEvent(const fcitx::InputMethodEntry & /*entry*/, fcitx::KeyEvent &event) {
    // Fire only on key press, not release.
    if (event.isRelease()) {
        return;
    }

    // M0 trigger: Super+Space. Real config-driven hotkey arrives in M1.
    static const fcitx::Key kHotkey{FcitxKey_space, fcitx::KeyState::Super};
    if (!event.key().checkKeyList({kHotkey})) {
        return;
    }

    // M0 stub: commit literal text. Replace with daemon RPC in next commit.
    if (auto *ic = event.inputContext()) {
        ic->commitString("hello world");
    }
    event.filterAndAccept();
}

}  // namespace synapse
