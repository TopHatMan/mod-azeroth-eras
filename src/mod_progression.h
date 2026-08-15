#ifndef MOD_PROGRESSION_H
#define MOD_PROGRESSION_H

#include "ScriptMgr.h"

#include <string>
#include <vector>

enum ProgressionPatch : uint8
{
    PATCH_WORLD_OF_WARCRAFT = 0,
    PATCH_MYSTERIES_OF_MARAUDON,
    PATCH_RUINS_OF_THE_DIRE_MAUL,
    PATCH_THE_CALL_TO_WAR,
    PATCH_BATTLEGROUNDS,
    PATCH_ASSAULT_ON_BLACKWING_LAIR,
    PATCH_RISE_OF_THE_BLOOD_GOD,
    PATCH_DRAGONS_OF_NIGHTMARE,
    PATCH_THE_GATES_OF_AHN_QIRAJ,
    PATCH_STORMS_OF_AZEROTH,
    PATCH_SHADOW_OF_THE_NECROPOLIS,
    PATCH_DRUMS_OF_WAR,
    PATCH_BEFORE_THE_STORM,
    PATCH_BLACK_TEMPLE,
    PATCH_VOICE_CHAT,
    PATCH_THE_GODS_OF_ZUL_AMAN,
    PATCH_FURY_OF_THE_SUNWELL,
    PATCH_ECHOES_OF_DOOM,
    PATCH_SECRETS_OF_ULDUAR,
    PATCH_CALL_OF_THE_CRUSADE,
    PATCH_FALL_OF_THE_LICH_KING,
    PATCH_ASSAULT_ON_THE_RUBY_SANCTUM,
    PATCH_MAX
};

constexpr uint8 DEFAULT_PROGRESSION_PATCH = PATCH_WORLD_OF_WARCRAFT;
constexpr uint8 DEFAULT_PROGRESSION_LEVEL_CAP = 60;

class Progression : public AllBattlegroundScript, DatabaseScript, MailScript, PlayerScript, UnitScript, WorldScript
{
public:
    Progression();

    // AllBattlegroundScript
    void OnBattlegroundEndReward(Battleground* /*bg*/, Player* /*player*/, TeamId /*winnerTeamId*/) override;

    // DatabaseScript
    void OnAfterDatabasesLoaded(uint32 /*updateFlags*/) override;

    // MailScript
    void OnBeforeMailDraftSendMailTo(MailDraft* /*mailDraft*/, MailReceiver const& /*receiver*/, MailSender const& /*sender*/, MailCheckMask& /*checked*/, uint32& /*deliver_delay*/, uint32& /*custom_expiration*/, bool& /*deleteMailItemsFromDB*/, bool& /*sendMail*/) override;

    // PlayerScript
    void OnPlayerUpdateArea(Player* /*player*/, uint32 /*oldArea*/, uint32 /*newArea*/) override;
    bool OnPlayerShouldBeRewardedWithMoneyInsteadOfExp(Player* /*player*/) override;
    bool OnPlayerUpdateFishingSkill(Player* /*player*/, int32 /*skill*/, int32 /*zone_skill*/, int32 /*chance*/, int32 /*roll*/) override;
    bool OnPlayerReputationChange(Player* /*player*/, uint32 /*factionID*/, int32& /*standing*/, bool /*incremental*/) override;
    void OnPlayerQuestComputeXP(Player* player, Quest const* /*quest*/, uint32& /*xpValue*/) override;
    void OnPlayerGiveXP(Player* /*player*/, uint32& /*amount*/, Unit* /*victim*/, uint8 /*xpSource*/) override;
    bool OnPlayerCanEnterMap(Player* /*player*/, MapEntry const* /*entry*/, InstanceTemplate const* /*instance*/, MapDifficulty const* /*mapDiff*/, bool /*loginCheck*/) override;

    // UnitScript
    void ModifyPeriodicDamageAurasTick(Unit* /*target*/, Unit* /*attacker*/, uint32& /*damage*/, SpellInfo const* /*spellInfo*/) override;
    void ModifyMeleeDamage(Unit* /*target*/, Unit* /*attacker*/, uint32& /*damage*/) override;
    void ModifySpellDamageTaken(Unit* /*target*/, Unit* /*attacker*/, int32& /*damage*/, SpellInfo const* /*spellInfo*/) override;
    void ModifyHealReceived(Unit* /*target*/, Unit* /*healer*/, uint32& /*heal*/, SpellInfo const* /*spellInfo*/) override;

    // WorldScript
    void OnAfterConfigLoad(bool /*reload*/) override;
    void OnStartup() override;

private:
    std::vector<std::string> GetActivePatches();
};

class ProgressionMgr
{
public:
    static ProgressionMgr* instance();

    void SetPatchId(uint8 id) { patchId = id; }
    uint8 GetPatchId() const { return patchId; }

    void SetLevelGatingEnabled(bool enabled) { levelGatingEnabled = enabled; }
    bool IsLevelGatingEnabled() const { return levelGatingEnabled; }

    void SetLevelCap(uint8 cap) { levelCap = cap; }
    uint8 GetLevelCap() const { return levelCap; }

    void SetEraLevelCap(uint8 cap) { eraLevelCap = cap; }
    uint8 GetEraLevelCap() const { return eraLevelCap; }

    void SetAuraId(uint8 id) { auraId = id; }
    uint8 GetAuraId() const { return auraId; }

    float GetDamageMultiplier() const { return damageMultiplier; }
    void SetDamageMultiplier(float value) { damageMultiplier = value; }

    float GetHealingMultiplier() const { return healingMultiplier; }
    void SetHealingMultiplier(float value) { healingMultiplier = value; }

    void SetResetDatabase(bool value) { resetDatabase = value; }
    bool GetResetDatabase() const { return resetDatabase; }

private:
    uint8 patchId{DEFAULT_PROGRESSION_PATCH};
    bool levelGatingEnabled{true};
    uint8 levelCap{DEFAULT_PROGRESSION_LEVEL_CAP};
    uint8 eraLevelCap{60};
    uint8 auraId{6};
    float damageMultiplier{0.6f};
    float healingMultiplier{0.5f};
    bool resetDatabase{false};
};

#define sProgressionMgr ProgressionMgr::instance()

#endif
