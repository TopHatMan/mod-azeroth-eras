#include "Chat.h"
#include "Config.h"

#include "mod_progression.h"

using namespace Acore::ChatCommands;

class progression_commandscript : public CommandScript
{
public:
    progression_commandscript() : CommandScript("progression_commandscript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable progressionTable =
        {
            { "info", HandleInfoCommand, SEC_MODERATOR, Console::Yes }
        };

        static ChatCommandTable commandTable =
        {
            { "progression", progressionTable }
        };

        return commandTable;
    }

    static char const* PatchDisplayName(uint8 patchId)
    {
        switch (patchId)
        {
        case PATCH_VANILLA_1_1:                return "1.1 World of Warcraft";
        case PATCH_MYSTERIES_OF_MARAUDON:      return "1.2 Mysteries of Maraudon";
        case PATCH_RUINS_OF_THE_DIRE_MAUL:     return "1.3 Ruins of the Dire Maul (MC attunement)";
        case PATCH_THE_CALL_TO_WAR:            return "1.4 The Call to War";
        case PATCH_BATTLEGROUNDS:              return "1.5 Battlegrounds";
        case PATCH_ASSAULT_ON_BLACKWING_LAIR:  return "1.6 Assault on Blackwing Lair";
        case PATCH_RISE_OF_THE_BLOOD_GOD:      return "1.7 Rise of the Blood God";
        case PATCH_DRAGONS_OF_NIGHTMARE:       return "1.8 Dragons of Nightmare";
        case PATCH_THE_GATES_OF_AHN_QIRAJ:     return "1.9 The Gates of Ahn'Qiraj";
        case PATCH_STORMS_OF_AZEROTH:          return "1.10 Storms of Azeroth";
        case PATCH_SHADOW_OF_THE_NECROPOLIS:   return "1.11 Shadow of the Necropolis";
        case PATCH_DRUMS_OF_WAR:               return "1.12 Drums of War";
        case PATCH_BEFORE_THE_STORM:           return "2.0 Before the Storm";
        case PATCH_BLACK_TEMPLE:               return "2.1 Black Temple";
        case PATCH_VOICE_CHAT:                 return "2.2 Voice Chat";
        case PATCH_THE_GODS_OF_ZUL_AMAN:       return "2.3 The Gods of Zul'Aman";
        case PATCH_FURY_OF_THE_SUNWELL:        return "2.4 Fury of the Sunwell";
        case PATCH_ECHOES_OF_DOOM:             return "3.0 Echoes of Doom";
        case PATCH_SECRETS_OF_ULDUAR:          return "3.1 Secrets of Ulduar";
        case PATCH_CALL_OF_THE_CRUSADE:        return "3.2 Call of the Crusade";
        case PATCH_FALL_OF_THE_LICH_KING:      return "3.3 Fall of the Lich King";
        case PATCH_ASSAULT_ON_THE_RUBY_SANCTUM:return "3.3.5 Assault on the Ruby Sanctum";
        default:                               return "unknown";
        }
    }

    static bool HandleInfoCommand(ChatHandler* handler)
    {
        uint8 patchId = sProgressionMgr->GetPatchId();
        handler->SendSysMessage("Unified Progression Module");
        handler->PSendSysMessage("Patch ID: {} ({})", patchId, PatchDisplayName(patchId));
        handler->PSendSysMessage("Ready target: 1.1-1.6 (IDs 0-{})", PROGRESSION_READY_TARGET_PATCH);
        if (patchId + 1 < PATCH_MAX)
            handler->PSendSysMessage("Next patch: {} ({})", patchId + 1, PatchDisplayName(patchId + 1));
        handler->PSendSysMessage("Level gating: {}", sProgressionMgr->IsLevelGatingEnabled() ? "enabled" : "disabled");
        handler->PSendSysMessage("Effective level cap: {}", sProgressionMgr->GetLevelCap());
        handler->PSendSysMessage("Patch-era maximum level: {}", sProgressionMgr->GetEraLevelCap());
        bool resetRequested = sConfigMgr->GetOption<bool>("Progression.Reset", false);
        bool unsafeResetAllowed = sConfigMgr->GetOption<bool>("Progression.Development.AllowUnsafeReset", false);
        char const* resetState = "disabled";
        if (resetRequested)
            resetState = unsafeResetAllowed ? "enabled (development only)" : "requested but blocked";
        handler->PSendSysMessage("SQL reset/reapply: {}", resetState);
        return true;
    }
};

void AddSC_progression_commandscript()
{
    new progression_commandscript();
}
