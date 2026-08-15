# Vanilla completion matrix

Status: active implementation scope

Vanilla accuracy is a complete world-state problem. Item templates are one workstream inside an atomic patch bundle; a patch is not complete until its content, acquisition paths, mechanics, access rules, and rollback behavior agree.

## Workstreams

| Workstream | Vanilla target | Current state | Completion test |
|---|---|---|---|
| Patch state and rollback | Deterministic selection of 1.1-1.12 in either direction | Patch ladder exists; reconciliation is not complete | Clean install and arbitrary transitions produce identical target state |
| Level progression | Milestones 10, 20, 30, 40, 50, 60 with Vanilla cap 60 | Foundation implemented | Cap, XP, map gates, and admin reporting agree at every milestone |
| Expansion leakage | Hide TBC/Wrath quests, NPCs, objects, systems, items, and conveniences | Launch hidden-content layer exists; full audit pending | Automated scan finds no later-era source reachable in Vanilla |
| Dungeons and raids | Correct availability, entrances, size, lockouts, attunements, encounters, and loot | Molten Core access partially audited; Horde Onyxia chain partially restored | Each instance passes an atomic content/access/loot test bundle |
| Quests and story | Patch-correct starters, enders, chains, objectives, text, rewards, and prerequisites | Horde Onyxia work started; broad audit pending | Every active quest has all dependencies and no future rewards |
| Creatures and world objects | Correct templates, spawns, patrols, equipment, factions, interactions, and patch windows | Selected launch fixes exist; broad audit pending | Per-patch spawn/template diff is reviewed and loadable |
| Items and equipment | Patch-correct stats, requirements, effects, sets, durability, prices, and displays | vMaNGOS extraction and ID-coverage audit implemented | Materialized snapshots and reviewed adjacent deltas exist for 1.1-1.12 |
| Loot and acquisition | Creature, object, item, fishing, skinning, pickpocket, disenchant, mail, and reference loot | Mostly inherited and unaudited | Every obtainable item source is inside its availability window |
| Vendors and economy | Inventories, reputation gates, currencies, prices, auction access, and consumables | Sparse patch SQL; launch audit pending | No later item/recipe is purchasable and historical vendors are complete |
| Professions | Trainers, recipes, skill requirements, reagents, crafted results, specializations | Pending | Recipe graph and trainers are correct for each patch |
| Classes, spells, and combat | Trainer ranks, spell behavior, debuff limits, threat, regeneration, and era tuning | Selected scripts exist; systematic audit pending | Server behavior is exact or explicitly classified as an approximation/client limitation |
| PvP | Honor lifecycle, ranks, rewards, battlegrounds, marks, reputations, and world PvP | Pending | PvP systems and rewards activate only in their historical patches |
| World events | Holidays, elemental invasions, AQ war effort/gates, Scourge Invasion, and patch events | AQ scripts exist; lifecycle audit pending | Event state, quests, spawns, loot, and reset behavior transition together |
| Travel and services | Flight nodes, transports, graveyards, meeting stones, mail, banks, and related NPCs | Selected launch SQL exists; audit pending | Services match the selected patch and do not expose later systems |
| Client-facing data | Displays, DBC-backed spells, maps, item sets, text, UI-visible rules | Optional patch strategy designed; package not built | Server reports matching client-data version and documents every limitation |
| Bots and difficulty | Bot attunement policy and one non-stacking difficulty owner | Design defined; full merge pending | Real-player rules remain strict and difficulty modifiers cannot compound |

## Existing Vanilla patch-layer inventory

The number below is the count of distinct SQL table/bundle files currently present for each patch. It measures inherited implementation breadth, not correctness.

| Patch | SQL layers | Notable represented domains | Immediate gaps |
|:---:|---:|---|---|
| 1.1 | 48 | Broad launch baseline, items, loot, quests, vendors, trainers, travel, access | Full provenance, Alliance Onyxia, economy/professions, later-era leakage |
| 1.2 | 3 | Creatures, disables, vendors | Maraudon atomic bundle, items, quests, loot, recipes, mechanics |
| 1.3 | 8 | MC access, creatures, loot, reputation, items, conditions | Dire Maul/world bosses and complete acquisition audit |
| 1.4 | 5 | Creatures, vendors, items, MC relocation | Honor system, rewards, quests, events, class changes |
| 1.5 | 4 | Creatures, objects, items, disables | WSG/AV rules, vendors, marks, honor revision, reputations |
| 1.6 | 4 | Creatures, objects, items, disables | BWL, Darkmoon Faire, Tier 2 sources, professions, class changes |
| 1.7 | 5 | Creatures, objects, fishing, items, disables | ZG, AB, loot/tokens/enchants, debuff behavior |
| 1.8 | 4 | Creatures, objects, items, disables | Nightmare dragons, Silithus, quests, loot, vendors |
| 1.9 | 6 | Creatures, objects, items, trainers, vendors | AQ event/gates, raids, war effort, tokens, quests, recipes |
| 1.10 | 3 | Creatures, items, disables | Dungeon Set 2, dungeon loot overhaul, weather, quests, vendors |
| 1.11 | 7 | Creatures, patrols/formations, objects, items | Naxxramas 40, Scourge Invasion, Tier 3, crafting, attunement |
| 1.12 | 2 | Creatures and disables | World PvP, final class/PvP/item changes, riding requirements |

The sparse later-patch rows explain why restoring the old SQL is only a foundation. Missing files do not always mean Blizzard changed that table in the patch, but no patch can be marked complete until every workstream has an explicit “changed,” “unchanged,” or “not reproducible” determination.

## vMaNGOS coverage beyond items

The pinned vMaNGOS database exposes patch/build metadata across more than fifty tables, including:

- creature and gameobject templates, spawns, addons, equipment, and pools;
- quests and starter/ender relations;
- creature, object, item, fishing, skinning, pickpocket, disenchant, mail, and reference loot;
- battlegrounds, graveyards, events, maps, transports, taxis, trainers, and player creation spells;
- progressive spell templates, chains, proc rules, groups, threats, and targets.

These are candidate patch boundaries. They must be translated into AzerothCore's schema and checked against primary evidence, existing module behavior, client data, and core-version differences before import.

## Implementation order

1. Finish the 1.1 launch snapshot across all workstreams.
2. Complete Molten Core and both Onyxia attunement/encounter bundles.
3. Audit launch dungeons, vendors, professions, trainers, quests, travel, events, and expansion leakage.
4. Build generic snapshot/delta extraction for vMaNGOS world tables, not only `item_template`.
5. Process 1.2 through 1.12 in order; each patch receives evidence, data, runtime behavior, tests, and rollback validation.
6. Mark a patch complete only when every workstream has an explicit disposition.

## Required patch artifact

Every Vanilla patch will ultimately contain:

- a manifest of introduced, changed, removed, and intentionally unchanged bundles;
- evidence and confidence for each historical claim;
- canonical expected world-data snapshots and adjacent deltas;
- runtime scripts for behavior that SQL cannot express;
- client-data requirements and known limitations;
- integration tests for access, dependencies, acquisition, forward transition, and rollback.
