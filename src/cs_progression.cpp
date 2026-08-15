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

    static bool HandleInfoCommand(ChatHandler* handler)
    {
        handler->SendSysMessage("Unified Progression Module");
        handler->PSendSysMessage("Patch ID: {}", sProgressionMgr->GetPatchId());
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
