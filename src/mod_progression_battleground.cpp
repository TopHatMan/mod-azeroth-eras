#include "Player.h"

#include "mod_progression.h"

void Progression::OnBattlegroundEndReward(Battleground* bg, Player* player, TeamId winnerTeamId)
{
    if (sProgressionMgr->GetPatchId() >= PATCH_ECHOES_OF_DOOM)
        return;

    if (player->IsGameMaster())
        return;

    uint32 token = 0;

    switch (bg->GetMapId())
    {
    case MAP_ALTERAC_VALLEY:
        token = 20560;
        break;
    case MAP_WARSONG_GULCH:
        token = 20558;
        break;
    case MAP_ARATHI_BASIN:
        token = 20559;
        break;
    case MAP_EYE_OF_THE_STORM:
        token = 29024;
        break;
    case MAP_STRAND_OF_THE_ANCIENTS:
        token = 42425;
        break;
    case MAP_ISLE_OF_CONQUEST:
        token = 47395;
        break;
    default:
        break;
    }

    if (token > 0)
        player->AddItem(token, (player->GetTeamId() == winnerTeamId ? 3 : 1));
}
