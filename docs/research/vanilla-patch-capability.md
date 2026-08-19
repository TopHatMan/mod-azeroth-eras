# Vanilla 1.1-1.12: what we can do without a core rewrite

- Status: research for a live 1.1 -> 1.2 test, 2026-08-17
- Sources: archived Blizzard patch notes via [Warcraft Wiki patch index](https://warcraft.wiki.gg/wiki/Patch), the existing module SQL/C++, and the Molten Core evidence file
- There is **no public content patch called 1.0**. Closed-beta builds used 1.0.x. Retail launch is **1.1.0** (7 Nov 2004). This project treats patch ID `0` as launch.

## How to read the tables

| Layer | Meaning | Risk |
|---|---|---|
| **SQL** | `disables`, `phaseMask`, quests, vendors, loot, events. Already how this module works. | Low. Reversible with a world-DB snapshot. |
| **Module C++** | Hooks we already own (`OnPlayerCanEnterMap`, area triggers, config, scripts under `src/`). | Low. Isolated to this module. |
| **Safe core** | Tiny, reviewable AzerothCore hook or config that does not change combat formulas or table primary keys. | Medium. Must rebase against Playerbots. One hook, one owner. |
| **Unsafe core** | Per-patch `item_template` keys, spell script rewrites, talent trees, combat tables. | High. Do not start this for the 1.1-1.2 test. |
| **Client** | Talents, helm/cloak hide UI, some spell tooltips, removed display IDs. | Out of scope until a versioned DBC pack exists. |

MC attunement is **patch 1.3**, not 1.2. Patch 1.2 is Maraudon + Winter Veil. If the goal is “Lothos and Attunement to the Core,” set `Progression.Patch = 2`.

## Risk rules for any core change

Do it only if all of these are true:

1. A module hook cannot see the event (no `PlayerScript` / `AllMapScript` / `UnitScript` for it).
2. The change is one function or one config default, not a new schema.
3. Official AC would plausibly accept it as an optional hook.
4. It is documented next to the patch that needs it.

Safe examples: “disable DBC item-attribute enforcement,” “fire a hook before meeting-stone grouping,” “expose instance player-cap from config.”

Unsafe examples: adding a `patch` column to live `item_template`, rewriting honor, forking spell.dbc loaders.

## Patch capability map

### 1.0 — World of Warcraft (ID 0) — 7 Nov 2004 (Blizzard client 1.1.0)

Launch world. This project labels it 1.0. MC and Onyxia exist. Enter MC through BRD (trigger 2886). No Lothos shortcut.

| Feature | Layer | In module? | Notes |
|---|---|---|---|
| Launch dungeons, MC, Onyxia maps | SQL + module C++ | Yes | Maps not disabled; level gate 60 |
| Hide TBC/WotLK maps, BGs, holidays | SQL `disables` | Yes | Runtime also blocks 530/571 |
| Hide later-patch NPCs/GOs | SQL `phaseMask` | Partial | EK/Kalimdor marked done; Outland/Northrend outdoor not walked |
| Lothos / attunement / fragment / shortcuts off | SQL + area-trigger script | Yes | Bundle tests exist |
| Horde Onyxia via Rexxar | SQL + scripts | Yes | Alliance chain still unaudited |
| Honor / arenas / LFG / dual spec / weather off | Module C++ config | Yes | |
| Full launch item/vendor/recipe snapshot | SQL | No | Inherited updates only; vMaNGOS extract later |
| Class/talent 1.1 behavior | Client + unsafe core | No | Approximate with damage/heal multipliers only |

**Test on 1.0:** enter MC via BRD; Lothos hidden; Maraudon blocked; `.progression info` says `0 (1.0 World of Warcraft)`.

### 1.2 — Mysteries of Maraudon (ID 1) — 18 Dec 2004

| Feature | Layer | In module? | Notes |
|---|---|---|---|
| Maraudon map 349 | SQL + runtime patch gate | Yes | Also level milestone 50 |
| Maraudon outdoor quests 7028-7070 | SQL `disables` | Yes | |
| Outdoor Maraudon NPCs (khans, Cavindra, Prophet, Willow) | SQL `phaseMask` | Yes as of this pass | Interior bosses stay in the instance |
| Winter Veil (events 2, 52) | SQL `disables` | Yes as of this pass | Decorations are `game_event` membership |
| Prayer of Fortitude / Gift of the Wild / Arcane Brilliance tomes | SQL item disables | Yes | 17413/17414/17682/17683/18600 |
| Reagent vendors (wild berries, candles) | SQL `npc_vendor` | Yes | 17021/17026/17028/17029 |
| Gurubashi arena floor-only FFA | Safe core or BG script | No | Stands PvP is a zone rule; skip for 1.2 test |
| Cross-race mounts at Exalted | SQL trainer/vendor | Not audited | |
| MC corpse at BRD entrance | Core instance graveyard | Stock AC already | No work |
| Helm/cloak hide checkbox | Client | Impossible here | |
| Class/talent tweaks (Bear armor, Pummel, etc.) | Client + unsafe core | No | Document only |

**Test on 1.2:** `Progression.Patch = 1`, level cap 50+. Enter Maraudon. Cavindra / Nameless Prophet visible. MC still BRD-only. Winter Veil can start if the event calendar allows it.

### 1.3 — Ruins of the Dire Maul (ID 2) — 7 Mar 2005

This is the MC attunement patch.

| Feature | Layer | In module? | Notes |
|---|---|---|---|
| Dire Maul map 429 | SQL + runtime | Yes | 5-man cap is stock AC |
| MC attunement quests 7487/7848 | SQL | Yes | |
| Lothos visible | SQL | Yes | |
| Core Fragment inside MC | SQL move | Yes | Approximation of the lost 1.3 transform |
| Shortcuts 3528/3529 after attunement | Module C++ | Yes | |
| Azuregos, Kazzak | SQL spawn + hide | Partial | Hidden in 1.1; need 1.3 unhide + scripts |
| Meeting stones | SQL GO + safe core | Hidden GOs exist | Group-finder AI is core; showing the stone is enough |
| 40-man MC/Onyxia, 15 BRS, 10 other 5-mans | Safe core / `dungeon_access` | Not forced | AC defaults already 5/10/25/40 |
| Dungeon player-cap enforcement | Already in AC | Yes | |

**Test on 1.3:** `Progression.Patch = 2`. Lothos up. Both attunement quests. Fragment inside MC. Shortcuts work only after turn-in. Dire Maul enterable.

### 1.4 — The Call to War (ID 3) — 19 Apr 2005

| Feature | Layer | In module? |
|---|---|---|
| Honor system on (rate 0.5 until Wrath) | Module C++ | Yes |
| Fragment moves to BRD | SQL | Yes |
| Children's Week, elemental invasions | SQL events 10, 13 | Yes |
| Rank rewards / PvP titles | SQL + client | Incomplete |
| Broad dungeon loot retune | SQL loot | Not done |

Honor *ranks* and decaying honor need core PvP code. Turning honor *on* is enough for a first 1.4 pass.

### 1.5 — Battlegrounds (ID 4) — 7 Jun 2005

| Feature | Layer | In module? |
|---|---|---|
| WSG + AV (maps 489, 30) | SQL disables + runtime | Yes |
| Cloth quartermasters | SQL NPCs | Need unhide |
| Historical AV (galv, towers, quests) | Module C++ / borrowed scripts | Not merged |

Stock AC AV is the Wrath rewrite. “Old AV” is a later bundle, not required to *open* the BG.

### 1.6 — Assault on Blackwing Lair (ID 5) — 12 Jul 2005

| Feature | Layer | In module? |
|---|---|---|
| BWL map 469 | SQL + runtime | Yes |
| Darkmoon Faire events | SQL events 3-5, 23, 71, 77 | Yes |
| Battlemasters | SQL NPCs | Need unhide audit |
| BWL attunement (Blackhand's Command) | SQL item 18987 disabled until 1.6 | Item disable exists at 1.1; 1.6 already clears 18987 |

### 1.7 — Rise of the Blood God (ID 6) — 13 Sep 2005

| Feature | Layer | In module? |
|---|---|---|
| ZG 309, AB 529 | SQL + runtime | Yes |
| Fishing Extravaganza, Harvest Festival | SQL events | Yes |
| Hakkar / ZG tokens | SQL loot | Not audited |
| Debuff slot limit 8->16 | Unsafe core / client | No |

### 1.8 — Dragons of Nightmare (ID 7) — 10 Oct 2005

| Feature | Layer | In module? |
|---|---|---|
| Ysondre/Lethon/Emeriss/Taerar | SQL unhide 14887-14890 | 1.1 hides them; 1.8 must unhide (check creature SQL) |
| Hallow's End | SQL event 12 | Yes |
| Silithus prep | SQL | Partial |

### 1.9 — The Gates of Ahn'Qiraj (ID 8) — 3 Jan 2006

| Feature | Layer | In module? |
|---|---|---|
| AQ20/AQ40 maps | SQL + runtime | Yes |
| War effort / gate / gong | Module scripts in `phase_00` | Scripts exist; event state is a later bundle |
| Lunar Festival, Love is in the Air | SQL events 7, 8 | Yes |

### 1.10 — Storms of Azeroth (ID 9) — 28 Mar 2006

| Feature | Layer | In module? |
|---|---|---|
| Weather | Module C++ `CONFIG_WEATHER` | Yes (off before 1.10) |
| Dungeon Set 2 quests 8922/8923 | SQL | Yes |
| Broad dungeon loot revision | SQL | Inherited item updates only |
| XP-to-gold at 60 | Module C++ | Yes from 1.10 |

### 1.11 — Shadow of the Necropolis (ID 10) — 20 Jun 2006

| Feature | Layer | In module? |
|---|---|---|
| Naxx 40 map 533 | SQL + runtime | Yes (needs `mod-vanilla-naxxramas`) |
| Scourge Invasion event 17 | SQL + planned controller | Event toggle yes; full lifecycle pending |
| Midsummer event 1 | SQL | Yes |
| Tier 3 | SQL loot | Not audited |

### 1.12 — Drums of War (ID 11) — 22 Aug 2006

| Feature | Layer | In module? |
|---|---|---|
| Silithus / EPL world PvP | SQL sourceType 5 | Yes |
| Final 1.12 riding/item states | SQL items | Almost empty (0 item file) |
| Cross-realm BGs | Core battleground queue | Not applicable on one realm |

## Recommended core changes (later, not for the 1.2 test)

| Change | Why | Risk |
|---|---|---|
| Stop enforcing `Item.dbc` stats over `item_template` | Server-side Vanilla stats actually show in the tooltip | Low-medium. One config or one check. Grim already does this. |
| Hook meeting-stone / LFG so we can no-op it before 1.3 | Stones can exist as objects without the 3.3.5 finder | Low if it is a hook, not a rewrite |
| Optional instance player-cap table | 1.3 10-man dungeon cap | Medium. AC already caps 5-mans at 5 |
| Honor decay / ranks | 1.4 authenticity | High. Leave stock honor-on for now |

Do **not** put a `patch` column on live AC tables for this test.

## How to test 1.1 -> 1.2 (and 1.3 if you want attunement)

1. Snapshot the world DB.
2. Rebuild worldserver so the new runtime gates and `.progression info` names are in the binary.
3. `Progression.Patch = 0`, `Progression.LevelCap = 60`, start once, confirm `.progression info` and that Maraudon / Lothos are closed.
4. Stop. Set `Progression.Patch = 1`. Start. The updater applies `patch_01-1_2`. Confirm Maraudon, Cavindra, Winter Veil event rows.
5. For **MC attunement**: stop, `Progression.Patch = 2`, start, talk to Lothos.

Do not use `Progression.Reset` on a realm you care about. Forward-only is fine: 0 -> 1 -> 2.
