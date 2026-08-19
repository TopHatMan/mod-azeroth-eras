# Ready target: Vanilla 1.1–1.6

Status: current playable target

Launch is **1.1** (`Progression.Patch = 0`). Blizzard’s retail client shipped as
1.1.0, so there is no separate step before 1.1 in this ladder.

Walk the realm **forward only**: `0 → 1 → 2 → 3 → 4 → 5`. Snapshot the world DB first.

## What “ready” means here

Headline **gates and bundles** work with SQL + this module’s C++. Not full itemization, not class/talent 1.x, not a core rewrite.

| ID | Patch | Ready to test | How |
|---:|:---:|---|---|
| 0 | 1.1 Launch | MC and Onyxia via BRD / launch attunement. Maraudon and later raids closed. Lothos hidden. Outland/Northrend closed. | `patch_00` SQL + runtime map gates |
| 1 | 1.2 Maraudon | Dungeon, outdoor khans/Cavindra/Prophet, Winter Veil, Fortitude tomes | `patch_01` SQL + runtime |
| 2 | 1.3 Dire Maul | Dire Maul. **MC attunement** (Lothos, both quests, fragment in MC, shortcuts). Azuregos + Kazzak visible. Meeting stones appear. | `patch_02` SQL + MC area-trigger script |
| 3 | 1.4 Honor | Honor rate turns on. Fragment moves to BRD. Children’s Week / elemental invasions. | config + `patch_03` SQL |
| 4 | 1.5 BGs | Warsong Gulch and Alterac Valley. AV/WSG world hubs unhide. | `patch_04` SQL + runtime BG maps |
| 5 | 1.6 BWL | Blackwing Lair. Darkmoon Faire events. Bindings of the Windseeker / Blackhand’s Command. | `patch_05` SQL + runtime |

IDs 6–11 (1.7–1.12) still load if you set the patch higher. They are **not** this target.

## Test commands

```ini
Progression.LevelGating.Enabled = 1
Progression.LevelCap = 60
Progression.Patch = 0
```

`.progression info` should print `0 (1.1 World of Warcraft)` and `Ready target: 1.1-1.6 (IDs 0-5)`.

Then bump `Progression.Patch` and restart:

1. `1` — enter Maraudon; Lothos still gone  
2. `2` — Lothos, attunement quests, Dire Maul, Azuregos/Kazzak  
3. `3` — honor ticks; fragment in BRD  
4. `4` — queue WSG/AV  
5. `5` — enter BWL  

Rebuild worldserver after pulling these changes. Do not use `Progression.Reset` on a realm you care about.
