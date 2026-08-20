#include "Config.h"

#include "mod_progression.h"

ProgressionMgr* ProgressionMgr::instance()
{
    static ProgressionMgr instance;
    return &instance;
}

char const* GetProgressionPatchDisplayName(uint8 patchId)
{
    switch (patchId)
    {
    case PATCH_VANILLA_1_1:                 return "1.1 World of Warcraft";
    case PATCH_MYSTERIES_OF_MARAUDON:       return "1.2 Mysteries of Maraudon";
    case PATCH_RUINS_OF_THE_DIRE_MAUL:      return "1.3 Ruins of the Dire Maul (MC attunement)";
    case PATCH_THE_CALL_TO_WAR:             return "1.4 The Call to War";
    case PATCH_BATTLEGROUNDS:               return "1.5 Battlegrounds";
    case PATCH_ASSAULT_ON_BLACKWING_LAIR:   return "1.6 Assault on Blackwing Lair";
    case PATCH_RISE_OF_THE_BLOOD_GOD:       return "1.7 Rise of the Blood God";
    case PATCH_DRAGONS_OF_NIGHTMARE:        return "1.8 Dragons of Nightmare";
    case PATCH_THE_GATES_OF_AHN_QIRAJ:      return "1.9 The Gates of Ahn'Qiraj";
    case PATCH_STORMS_OF_AZEROTH:           return "1.10 Storms of Azeroth";
    case PATCH_SHADOW_OF_THE_NECROPOLIS:    return "1.11 Shadow of the Necropolis";
    case PATCH_DRUMS_OF_WAR:                return "1.12 Drums of War";
    case PATCH_BEFORE_THE_STORM:            return "2.0 Before the Storm";
    case PATCH_BLACK_TEMPLE:                return "2.1 Black Temple";
    case PATCH_VOICE_CHAT:                  return "2.2 Voice Chat";
    case PATCH_THE_GODS_OF_ZUL_AMAN:        return "2.3 The Gods of Zul'Aman";
    case PATCH_FURY_OF_THE_SUNWELL:         return "2.4 Fury of the Sunwell";
    case PATCH_ECHOES_OF_DOOM:              return "3.0 Echoes of Doom";
    case PATCH_SECRETS_OF_ULDUAR:            return "3.1 Secrets of Ulduar";
    case PATCH_CALL_OF_THE_CRUSADE:          return "3.2 Call of the Crusade";
    case PATCH_FALL_OF_THE_LICH_KING:        return "3.3 Fall of the Lich King";
    case PATCH_ASSAULT_ON_THE_RUBY_SANCTUM: return "3.3.5 Assault on the Ruby Sanctum";
    default:                                 return "unknown";
    }
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
void Addmod_azeroth_erasScripts()
{
    RegisterProgressionScripts();
}

void Addmod_progressionScripts()
{
    RegisterProgressionScripts();
}

void Addmod_02_progressionScripts()
{
    RegisterProgressionScripts();
}
