#include "ArenaSeasonMgr.h"

#include "mod_progression.h"

void Progression::OnStartup()
{
    uint8 patchId = sProgressionMgr->GetPatchId();

    if (patchId < PATCH_BEFORE_THE_STORM)
    {
        sArenaSeasonMgr->ChangeCurrentSeason(1);
        sArenaSeasonMgr->SetSeasonState(ARENA_SEASON_STATE_DISABLED);
        return;
    }

    if (patchId < PATCH_BLACK_TEMPLE)
        sArenaSeasonMgr->ChangeCurrentSeason(1);
    else if (patchId < PATCH_THE_GODS_OF_ZUL_AMAN)
        sArenaSeasonMgr->ChangeCurrentSeason(2);
    else if (patchId < PATCH_FURY_OF_THE_SUNWELL)
        sArenaSeasonMgr->ChangeCurrentSeason(3);
    else if (patchId < PATCH_ECHOES_OF_DOOM)
        sArenaSeasonMgr->ChangeCurrentSeason(4);
    else if (patchId < PATCH_SECRETS_OF_ULDUAR)
        sArenaSeasonMgr->ChangeCurrentSeason(5);
    else if (patchId < PATCH_CALL_OF_THE_CRUSADE)
        sArenaSeasonMgr->ChangeCurrentSeason(6);
    else if (patchId < PATCH_FALL_OF_THE_LICH_KING)
        sArenaSeasonMgr->ChangeCurrentSeason(7);
    else
        sArenaSeasonMgr->ChangeCurrentSeason(8);
}
