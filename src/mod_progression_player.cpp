#include "Player.h"

#include "mod_progression.h"

namespace
{
uint8 GetRequiredProgressionLevelCapForMap(uint32 mapId)
{
    switch (mapId)
    {
    // Level 20 milestone: first Vanilla dungeons
    case 33:  // Shadowfang Keep
    case 36:  // The Deadmines
    case 43:  // Wailing Caverns
    case 48:  // Blackfathom Deeps
    case 389: // Ragefire Chasm
        return 20;

    // Level 30 milestone
    case 34: // The Stockade
    case 47: // Razorfen Kraul
    case 90: // Gnomeregan
        return 30;

    // Level 40 milestone
    case 70:  // Uldaman
    case 129: // Razorfen Downs
    case 189: // Scarlet Monastery
        return 40;

    // Level 50 milestone
    case 109: // Sunken Temple
    case 209: // Zul'Farrak
    case 349: // Maraudon (patch gate still requires 1.2)
        return 50;

    // Level 60 milestone: late Vanilla dungeons and raids.
    // Historical patch SQL remains authoritative for patch-specific availability.
    case 229: // Blackrock Spire
    case 230: // Blackrock Depths
    case 249: // Onyxia's Lair
    case 289: // Scholomance
    case 309: // Zul'Gurub
    case 329: // Stratholme
    case 409: // Molten Core
    case 429: // Dire Maul
    case 469: // Blackwing Lair
    case 509: // Ruins of Ahn'Qiraj
    case 531: // Temple of Ahn'Qiraj
    case 533: // Naxxramas
        return 60;

    // Level 70 milestone: TBC leveling/endgame instances. Patch SQL decides which
    // endgame content is actually open inside the TBC patch cycle.
    case 269: // The Black Morass
    case 532: // Karazhan
    case 534: // Hyjal Summit
    case 540: // The Shattered Halls
    case 542: // The Blood Furnace
    case 543: // Hellfire Ramparts
    case 544: // Magtheridon's Lair
    case 545: // The Steamvault
    case 546: // The Underbog
    case 547: // The Slave Pens
    case 548: // Serpentshrine Cavern
    case 550: // Tempest Keep
    case 552: // The Arcatraz
    case 553: // The Botanica
    case 554: // The Mechanar
    case 555: // Shadow Labyrinth
    case 556: // Sethekk Halls
    case 557: // Mana-Tombs
    case 558: // Auchenai Crypts
    case 560: // Old Hillsbrad Foothills
    case 564: // Black Temple
    case 565: // Gruul's Lair
    case 568: // Zul'Aman
    case 580: // Sunwell Plateau
    case 585: // Magisters' Terrace
        return 70;

    // Level 80 milestone: Wrath leveling/endgame instances.
    case 574: // Utgarde Keep
    case 575: // Utgarde Pinnacle
    case 576: // The Nexus
    case 578: // The Oculus
    case 595: // The Culling of Stratholme
    case 599: // Halls of Stone
    case 600: // Drak'Tharon Keep
    case 601: // Azjol-Nerub
    case 602: // Halls of Lightning
    case 603: // Ulduar
    case 604: // Gundrak
    case 608: // Violet Hold
    case 615: // The Obsidian Sanctum
    case 616: // The Eye of Eternity
    case 619: // Ahn'kahet: The Old Kingdom
    case 624: // Vault of Archavon
    case 631: // Icecrown Citadel
    case 632: // The Forge of Souls
    case 649: // Trial of the Crusader
    case 650: // Trial of the Champion
    case 658: // Pit of Saron
    case 668: // Halls of Reflection
    case 724: // The Ruby Sanctum
        return 80;

    default:
        return 0;
    }
}

// Historical patch that first made this map available. 0 means launch-era / no patch gate.
// Level milestones are a separate check; both must pass.
uint8 GetRequiredProgressionPatchForMap(uint32 mapId)
{
    switch (mapId)
    {
    case 349: // Maraudon
        return PATCH_MYSTERIES_OF_MARAUDON;

    case 429: // Dire Maul
        return PATCH_RUINS_OF_THE_DIRE_MAUL;

    case 30:  // Alterac Valley
    case 489: // Warsong Gulch
        return PATCH_BATTLEGROUNDS;

    case 469: // Blackwing Lair
        return PATCH_ASSAULT_ON_BLACKWING_LAIR;

    case 309: // Zul'Gurub
    case 529: // Arathi Basin
        return PATCH_RISE_OF_THE_BLOOD_GOD;

    case 509: // Ruins of Ahn'Qiraj
    case 531: // Temple of Ahn'Qiraj
        return PATCH_THE_GATES_OF_AHN_QIRAJ;

    case 533: // Naxxramas (Vanilla 40 via mod-vanilla-naxxramas; Wrath 10/25 from 3.0)
        return PATCH_SHADOW_OF_THE_NECROPOLIS;

    // TBC continent and 2.0 instances
    case 269: // The Black Morass
    case 530: // Outland (includes Blood Elf / Draenei starting zones)
    case 532: // Karazhan
    case 534: // Hyjal Summit
    case 540: // The Shattered Halls
    case 542: // The Blood Furnace
    case 543: // Hellfire Ramparts
    case 544: // Magtheridon's Lair
    case 545: // The Steamvault
    case 546: // The Underbog
    case 547: // The Slave Pens
    case 548: // Serpentshrine Cavern
    case 550: // Tempest Keep
    case 552: // The Arcatraz
    case 553: // The Botanica
    case 554: // The Mechanar
    case 555: // Shadow Labyrinth
    case 556: // Sethekk Halls
    case 557: // Mana-Tombs
    case 558: // Auchenai Crypts
    case 560: // Old Hillsbrad Foothills
    case 565: // Gruul's Lair
    case 566: // Eye of the Storm
        return PATCH_BEFORE_THE_STORM;

    case 564: // Black Temple
        return PATCH_BLACK_TEMPLE;

    case 568: // Zul'Aman
        return PATCH_THE_GODS_OF_ZUL_AMAN;

    case 580: // Sunwell Plateau
    case 585: // Magisters' Terrace
        return PATCH_FURY_OF_THE_SUNWELL;

    // Wrath continent and 3.0 instances
    case 571: // Northrend
    case 574: // Utgarde Keep
    case 575: // Utgarde Pinnacle
    case 576: // The Nexus
    case 578: // The Oculus
    case 595: // The Culling of Stratholme
    case 599: // Halls of Stone
    case 600: // Drak'Tharon Keep
    case 601: // Azjol-Nerub
    case 602: // Halls of Lightning
    case 604: // Gundrak
    case 608: // Violet Hold
    case 615: // The Obsidian Sanctum
    case 616: // The Eye of Eternity
    case 619: // Ahn'kahet: The Old Kingdom
    case 624: // Vault of Archavon
        return PATCH_ECHOES_OF_DOOM;

    case 603: // Ulduar
        return PATCH_SECRETS_OF_ULDUAR;

    case 607: // Strand of the Ancients
    case 649: // Trial of the Crusader
    case 650: // Trial of the Champion
        return PATCH_CALL_OF_THE_CRUSADE;

    case 628: // Isle of Conquest
    case 631: // Icecrown Citadel
    case 632: // The Forge of Souls
    case 658: // Pit of Saron
    case 668: // Halls of Reflection
        return PATCH_FALL_OF_THE_LICH_KING;

    case 724: // The Ruby Sanctum
        return PATCH_ASSAULT_ON_THE_RUBY_SANCTUM;

    default:
        return 0;
    }
}
}

void Progression::OnPlayerUpdateArea(Player* player, uint32 /*oldArea*/, uint32 newArea)
{
    if (player->IsGameMaster())
        return;

    if (player->IsInFlight())
        return;

    if (sProgressionMgr->GetPatchId() < PATCH_FURY_OF_THE_SUNWELL && newArea == AREA_ISLE_OF_QUEL_DANAS)
    {
        player->GetSession()->SendAreaTriggerMessage("The Isle of Quel'Danas is currently unavailable.");
        player->TeleportTo(530, 9333.0f, -7884.0f, 27.6f, 0.0f); // Silvermoon outskirts; map 530 is already open in TBC
        return;
    }

    if (sProgressionMgr->GetPatchId() < PATCH_CALL_OF_THE_CRUSADE)
    {
        if (newArea == AREA_ARGENT_TOURNAMENT_GROUNDS)
        {
            player->GetSession()->SendAreaTriggerMessage("The argent tournament grounds are currently unavailable.");
            player->TeleportTo(571, 8163.57f, 799.76f, 484.03f, 3.18f);
        }
    }
}

bool Progression::OnPlayerCanEnterMap(Player* player, MapEntry const* entry, InstanceTemplate const* /*instance*/, MapDifficulty const* /*mapDiff*/, bool loginCheck)
{
    if (!entry)
        return true;

    uint8 requiredPatch = GetRequiredProgressionPatchForMap(entry->MapID);
    if (requiredPatch && sProgressionMgr->GetPatchId() < requiredPatch)
    {
        if (!loginCheck && player)
            player->GetSession()->SendAreaTriggerMessage("This content is not available in the current patch.");
        return false;
    }

    if (!sProgressionMgr->IsLevelGatingEnabled())
        return true;

    uint8 requiredLevelCap = GetRequiredProgressionLevelCapForMap(entry->MapID);
    if (!requiredLevelCap || sProgressionMgr->GetLevelCap() >= requiredLevelCap)
        return true;

    if (!loginCheck && player)
        player->GetSession()->SendAreaTriggerMessage("This instance is locked until the server reaches the level {} progression stage.", requiredLevelCap);

    return false;
}

bool Progression::OnPlayerShouldBeRewardedWithMoneyInsteadOfExp(Player* player)
{
    if (sProgressionMgr->GetPatchId() < PATCH_STORMS_OF_AZEROTH)
        return false;

    if ((player->GetLevel() == 60 && sWorld->getIntConfig(CONFIG_EXPANSION) == EXPANSION_CLASSIC) ||
        (player->GetLevel() == 70 && sWorld->getIntConfig(CONFIG_EXPANSION) == EXPANSION_THE_BURNING_CRUSADE) ||
        (player->GetLevel() == 80 && sWorld->getIntConfig(CONFIG_EXPANSION) == EXPANSION_WRATH_OF_THE_LICH_KING))
        return true;

    return false;
}

bool Progression::OnPlayerUpdateFishingSkill(Player* /*player*/, int32 /*skill*/, int32 /*zone_skill*/, int32 chance, int32 roll)
{
    if (sProgressionMgr->GetPatchId() < PATCH_ECHOES_OF_DOOM)
        if (chance < roll)
            return false;

    return true;
}

bool Progression::OnPlayerReputationChange(Player* /*player*/, uint32 factionID, int32& /*standing*/, bool /*incremental*/)
{
    if ((factionID == 911 || factionID == 930) && sProgressionMgr->GetPatchId() < PATCH_BEFORE_THE_STORM)
        return false;

    return true;
}

void Progression::OnPlayerQuestComputeXP(Player* /*player*/, Quest const* quest, uint32& xpValue)
{
    if (sProgressionMgr->GetPatchId() < PATCH_THE_GODS_OF_ZUL_AMAN && quest->GetQuestLevel() >= 30 && quest->GetQuestLevel() <= 60)
        xpValue = uint32(ceilf(xpValue / 1.428571429f));
}

void Progression::OnPlayerGiveXP(Player* /*player*/, uint32& amount, Unit* /*victim*/, uint8 xpSource)
{
    if (xpSource == PlayerXPSource::XPSOURCE_BATTLEGROUND && sProgressionMgr->GetPatchId() < PATCH_CALL_OF_THE_CRUSADE)
        amount = 0;
}
