#include "Config.h"

#include "mod_progression.h"

ProgressionMgr* ProgressionMgr::instance()
{
    static ProgressionMgr instance;
    return &instance;
}

Progression::Progression() : AllBattlegroundScript("ProgressionAllBattlegroundScript"), DatabaseScript("ProgressionDatabaseScript"), MailScript("ProgressionMailScript"), PlayerScript("ProgressionPlayerScript"), UnitScript("ProgressionUnitScript"), WorldScript("ProgressionWorldScript") {}

void AddSC_spell_mark_of_kazzak();
void AddSC_instance_blackrock_spire_progression();
void AddSC_instance_onyxias_lair_progression();
void AddSC_boss_onyxia_progression();
void AddSC_go_scarab_gong();
void AddSC_go_scarab_gate();
void AddSC_spell_summon_nightbane();
void AddSC_npc_archmage_landalock();
void AddSC_npc_archmage_timear();
void AddSC_progression_commandscript();
void AddSC_progression_area_triggers();

namespace
{
void RegisterProgressionScripts()
{
    new Progression();
    AddSC_progression_commandscript();
    AddSC_progression_area_triggers();

    uint8 patchId = sConfigMgr->GetOption<uint8>("Progression.Patch", DEFAULT_PROGRESSION_PATCH);

    if (patchId < PATCH_BEFORE_THE_STORM)
        AddSC_spell_mark_of_kazzak();

    if (patchId < PATCH_ECHOES_OF_DOOM)
    {
        AddSC_instance_blackrock_spire_progression();
        AddSC_go_scarab_gong();
        AddSC_go_scarab_gate();
        AddSC_spell_summon_nightbane();
    }

    if (patchId < PATCH_CALL_OF_THE_CRUSADE)
    {
        AddSC_instance_onyxias_lair_progression();
        AddSC_boss_onyxia_progression();
    }

    AddSC_npc_archmage_landalock();

    if (patchId < PATCH_FALL_OF_THE_LICH_KING)
        AddSC_npc_archmage_timear();
}
}

// AzerothCore derives the loader symbol from the module directory name.
// Supporting both names makes the fork work whether installed as mod-progression
// or mod-02-progression (the Ashbringer module ordering convention).
void Addmod_progressionScripts()
{
    RegisterProgressionScripts();
}

void Addmod_02_progressionScripts()
{
    RegisterProgressionScripts();
}
