#include "mod_progression.h"

namespace
{
bool IsValidProgressionLevelCap(uint8 levelCap)
{
    return levelCap >= 10 && levelCap <= 80 && levelCap % 10 == 0;
}
}

void Progression::OnAfterConfigLoad(bool reload)
{
    LOG_INFO("server.loading", "Progression...");

    // Azeroth Eras replaces both legacy progression modules.  Their database,
    // script, and combat hooks must not be active at the same time as this
    // module or the realm can receive conflicting gates and compounded tuning.
    if (sConfigMgr->GetOption<bool>("ProgressionSystem.LoadScripts", false) ||
        sConfigMgr->GetOption<bool>("ProgressionSystem.LoadDatabase", false))
    {
        LOG_ERROR("server.loading",
            "Azeroth Eras: legacy mod-progression-system is enabled. Remove/disable it before testing; its bracket SQL and scripts are not safe to stack with Azeroth Eras.");
    }

    if (sConfigMgr->GetOption<bool>("IndividualProgression.Enable", false))
    {
        LOG_ERROR("server.loading",
            "Azeroth Eras: legacy mod-individual-progression is enabled. Remove/disable it before testing; running both modules can duplicate gates and damage/healing adjustments.");
    }

    if (!reload)
    {
        uint8 patchId = sConfigMgr->GetOption<uint8>("Progression.Patch", DEFAULT_PROGRESSION_PATCH);
        uint8 auraId = sConfigMgr->GetOption<uint8>("Progression.IcecrownCitadel.Aura", 6);
        bool levelGatingEnabled = sConfigMgr->GetOption<bool>("Progression.LevelGating.Enabled", true);
        uint8 configuredLevelCap = sConfigMgr->GetOption<uint8>("Progression.LevelCap", DEFAULT_PROGRESSION_LEVEL_CAP);

        if (patchId >= PATCH_MAX)
        {
            LOG_ERROR("server.loading", "Patch ({}) must be in range 0..{}. Using patch 1.1 ({}).", patchId, PATCH_MAX - 1, DEFAULT_PROGRESSION_PATCH);
            patchId = DEFAULT_PROGRESSION_PATCH;
        }

        if (!IsValidProgressionLevelCap(configuredLevelCap))
        {
            LOG_ERROR("server.loading", "Progression.LevelCap ({}) must be one of 10, 20, 30, 40, 50, 60, 70, or 80. Using {}.", configuredLevelCap, DEFAULT_PROGRESSION_LEVEL_CAP);
            configuredLevelCap = DEFAULT_PROGRESSION_LEVEL_CAP;
        }

        LOG_INFO("server.loading", ">> Patch ID set to {} (ready target is 1.1-1.6 / IDs 0-{})", patchId, PROGRESSION_READY_TARGET_PATCH);
        sProgressionMgr->SetPatchId(patchId);
        sProgressionMgr->SetLevelGatingEnabled(levelGatingEnabled);

        if (auraId > 6)
        {
            LOG_ERROR("server.loading", "Aura ({}) must be in range 0..6. Using default value ({}).", auraId, 6);
            auraId = 6;
        }

        LOG_INFO("server.loading", ">> Aura set to {}", auraId);
        sProgressionMgr->SetAuraId(auraId);

        uint32 expansion = EXPANSION_WRATH_OF_THE_LICH_KING;
        uint8 eraLevelCap = 80;

        if (patchId < PATCH_BEFORE_THE_STORM)
        {
            expansion = EXPANSION_CLASSIC;
            eraLevelCap = 60;
        }
        else if (patchId < PATCH_ECHOES_OF_DOOM)
        {
            expansion = EXPANSION_THE_BURNING_CRUSADE;
            eraLevelCap = 70;
        }

        uint8 effectiveLevelCap = eraLevelCap;
        if (levelGatingEnabled && configuredLevelCap < eraLevelCap)
            effectiveLevelCap = configuredLevelCap;

        if (configuredLevelCap > eraLevelCap)
            LOG_INFO("server.loading", ">> Requested level cap {} is above the active patch era cap {}; clamped to {}", configuredLevelCap, eraLevelCap, eraLevelCap);

        sProgressionMgr->SetEraLevelCap(eraLevelCap);
        sProgressionMgr->SetLevelCap(effectiveLevelCap);

        LOG_INFO("server.loading", ">> Expansion set to {}", expansion);
        LOG_INFO("server.loading", ">> Level progression {}", levelGatingEnabled ? "enabled" : "disabled");
        LOG_INFO("server.loading", ">> Effective max level set to {}", effectiveLevelCap);
        sWorld->setIntConfig(CONFIG_EXPANSION, expansion);
        sWorld->setIntConfig(CONFIG_MAX_PLAYER_LEVEL, effectiveLevelCap);

        if (sConfigMgr->GetOption<bool>("Progression.QuestInfo.Enforced", true))
        {
            if (patchId < PATCH_THE_GODS_OF_ZUL_AMAN)
            {
                LOG_INFO("server.loading", ">> Disabled object quest markers");
                sWorld->setBoolConfig(CONFIG_OBJECT_QUEST_MARKERS, false);

                LOG_INFO("server.loading", ">> Disabled object sparkles");
                sWorld->setBoolConfig(CONFIG_OBJECT_SPARKLES, false);
            }

            if (patchId < PATCH_FALL_OF_THE_LICH_KING)
            {
                LOG_INFO("server.loading", ">> Points of interest for quests disabled");
                sWorld->setBoolConfig(CONFIG_QUEST_POI_ENABLED, false);
            }
        }
    }

    uint8 patchId = sProgressionMgr->GetPatchId();
    uint8 auraId = sProgressionMgr->GetAuraId();

    if (patchId < PATCH_STORMS_OF_AZEROTH)
    {
        LOG_INFO("server.loading", ">> Disabled weather");
        sWorld->setBoolConfig(CONFIG_WEATHER, false);
    }

    if (patchId < PATCH_THE_GODS_OF_ZUL_AMAN)
    {
        LOG_INFO("server.loading", ">> Disabled Alterac Valley reinforcements");
        sWorld->setIntConfig(CONFIG_BATTLEGROUND_ALTERAC_REINFORCEMENTS, 0);
    }

    if (patchId < PATCH_ECHOES_OF_DOOM)
    {
        LOG_INFO("server.loading", ">> Water breath timer set to 60 seconds");
        sWorld->setIntConfig(CONFIG_WATER_BREATH_TIMER, 60000);

        LOG_INFO("server.loading", ">> Disabled Wintergrasp");
        sWorld->setIntConfig(CONFIG_WINTERGRASP_ENABLE, 2);

        LOG_INFO("server.loading", ">> Enabled legacy arena points calculation");
        sWorld->setIntConfig(CONFIG_LEGACY_ARENA_POINTS_CALC, true);

        float damageMultiplier = sConfigMgr->GetOption<float>("Progression.Multiplier.Damage", 0.6f);
        LOG_INFO("server.loading", ">> Damage multiplier set to {}", damageMultiplier);
        sProgressionMgr->SetDamageMultiplier(damageMultiplier);

        float healingMultiplier = sConfigMgr->GetOption<float>("Progression.Multiplier.Healing", 0.5f);
        LOG_INFO("server.loading", ">> Healing multiplier set to {}", healingMultiplier);
        sProgressionMgr->SetHealingMultiplier(healingMultiplier);
    }

    if (patchId < PATCH_CALL_OF_THE_CRUSADE)
    {
        LOG_INFO("server.loading", ">> Disabled quest auto accept");
        sWorld->setBoolConfig(CONFIG_QUEST_IGNORE_AUTO_ACCEPT, true);

        if (sConfigMgr->GetOption<bool>("Progression.TradableBindsOnPickup.Enforced", true))
        {
            LOG_INFO("server.loading", ">> Disabled BoP item trades");
            sWorld->setBoolConfig(CONFIG_SET_BOP_ITEM_TRADEABLE, false);
        }

        LOG_INFO("server.loading", ">> Disabled experience rate in battlegrounds");
        sWorld->setRate(RATE_XP_BG_KILL_AV, 0.0f);
        sWorld->setRate(RATE_XP_BG_KILL_WSG, 0.0f);
        sWorld->setRate(RATE_XP_BG_KILL_AB, 0.0f);
        sWorld->setRate(RATE_XP_BG_KILL_EOTS, 0.0f);
        sWorld->setRate(RATE_XP_BG_KILL_SOTA, 0.0f);
        sWorld->setRate(RATE_XP_BG_KILL_IC, 0.0f);

        LOG_INFO("server.loading", ">> Set capture points in Arathi Basin to 2000");
        sWorld->setIntConfig(CONFIG_BATTLEGROUND_ARATHI_CAPTUREPOINTS, 2000);

        LOG_INFO("server.loading", ">> Set capture points in Eye of the Storm to 2000");
        sWorld->setIntConfig(CONFIG_BATTLEGROUND_EYEOFTHESTORM_CAPTUREPOINTS, 2000);
    }

    if (patchId < PATCH_SECRETS_OF_ULDUAR && sConfigMgr->GetOption<bool>("Progression.DualTalent.Enforced", true))
    {
        LOG_INFO("server.loading", ">> Disabled dual talent specialization");
        sWorld->setIntConfig(CONFIG_MIN_DUALSPEC_LEVEL, 255);
    }

    if (patchId < PATCH_FALL_OF_THE_LICH_KING)
    {
        if (sConfigMgr->GetOption<bool>("Progression.DungeonFinder.Enforced", true))
        {
            LOG_INFO("server.loading", ">> Dungeon Finder disabled");
            sWorld->setIntConfig(CONFIG_LFG_OPTIONSMASK, 0);
        }

        LOG_INFO("server.loading", ">> Low level regen boost disabled");
        sWorld->setBoolConfig(CONFIG_LOW_LEVEL_REGEN_BOOST, false);
    }

    float honorRate = sWorld->getRate(RATE_HONOR);
    if (patchId < PATCH_THE_CALL_TO_WAR)
        honorRate = 0.0f;
    else if (patchId < PATCH_FALL_OF_THE_LICH_KING)
        honorRate = 0.5f;

    LOG_INFO("server.loading", ">> Honor rate set to {}", honorRate);
    sWorld->setRate(RATE_HONOR, honorRate);

    if (patchId < PATCH_BEFORE_THE_STORM)
    {
        LOG_INFO("server.loading", ">> Arena points disabled");
        sWorld->setRate(RATE_ARENA_POINTS, 0.0f);
    }

    uint32 allianceBuffId = 73828;
    uint32 hordeBuffId = 73822;

    switch (auraId)
    {
    case 0:
        allianceBuffId = 0;
        hordeBuffId = 0;
        break;
    case 1:
        allianceBuffId = 73762;
        hordeBuffId = 73816;
        break;
    case 2:
        allianceBuffId = 73824;
        hordeBuffId = 73818;
        break;
    case 3:
        allianceBuffId = 73825;
        hordeBuffId = 73819;
        break;
    case 4:
        allianceBuffId = 73826;
        hordeBuffId = 73820;
        break;
    case 5:
        allianceBuffId = 73827;
        hordeBuffId = 73821;
        break;
    default:
        break;
    }

    sWorld->setIntConfig(CONFIG_ICC_BUFF_ALLIANCE, allianceBuffId);
    sWorld->setIntConfig(CONFIG_ICC_BUFF_HORDE, hordeBuffId);
}
