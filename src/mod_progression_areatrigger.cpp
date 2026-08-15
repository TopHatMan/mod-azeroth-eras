#include "AreaTriggerScript.h"
#include "Player.h"

#include "mod_progression.h"

namespace
{
constexpr uint32 QUEST_ATTUNEMENT_TO_THE_CORE_ALLIANCE = 7487;
constexpr uint32 QUEST_ATTUNEMENT_TO_THE_CORE_HORDE = 7848;

class at_progression_molten_core_shortcut : public AreaTriggerScript
{
public:
    at_progression_molten_core_shortcut() : AreaTriggerScript("at_progression_molten_core_shortcut") { }

    bool OnTrigger(Player* player, AreaTrigger const* /*trigger*/) override
    {
        if (sProgressionMgr->GetPatchId() < PATCH_RUINS_OF_THE_DIRE_MAUL)
        {
            player->GetSession()->SendAreaTriggerMessage(
                "The Molten Core shortcut is unavailable until patch 1.3. Enter through Blackrock Depths.");
            return true;
        }

        if (!player->GetQuestRewardStatus(QUEST_ATTUNEMENT_TO_THE_CORE_ALLIANCE) &&
            !player->GetQuestRewardStatus(QUEST_ATTUNEMENT_TO_THE_CORE_HORDE))
        {
            player->GetSession()->SendAreaTriggerMessage(
                "You must complete Attunement to the Core before using this shortcut.");
            return true;
        }

        return false;
    }
};
}

void AddSC_progression_area_triggers()
{
    new at_progression_molten_core_shortcut();
}
