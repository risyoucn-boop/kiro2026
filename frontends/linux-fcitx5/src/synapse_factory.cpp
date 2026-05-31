#include <fcitx/addonfactory.h>
#include <fcitx/addonmanager.h>

#include "synapse_engine.h"

namespace synapse {

class SynapseEngineFactory : public fcitx::AddonFactory {
  public:
    fcitx::AddonInstance *create(fcitx::AddonManager *manager) override {
        return new SynapseEngine(manager->instance());
    }
};

}  // namespace synapse

FCITX_ADDON_FACTORY(synapse::SynapseEngineFactory);
