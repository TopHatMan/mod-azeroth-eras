# Vanilla 1.11 Scourge Invasion

Status: runtime reconstruction in progress

Patch: 1.11, module patch id `10`

Scope: original 2006 event; keep separate from the Wrath 3.0.2 invasion

## Finding that started this work

The inherited patch layer did not gate the invasion correctly. AzerothCore/vMaNGOS identify the Scourge Invasion as game event `17`, but the launch layer did not disable event `17` and the 1.11 layer only enabled event `1` (Midsummer Fire Festival). This produced two bad states: invasion data could leak before 1.11, and selecting 1.11 did not deliberately activate the actual invasion controller.

The patch layers now disable event `17` in 1.1 and enable it in 1.11. Event `1` remains a separate 1.11 unlock.

This fixes availability only. AzerothCore does not currently contain the complete original event controller, so merely enabling event `17` cannot reproduce the invasion.

## Player-facing target

Patch 1.11 must provide one coherent realm event:

1. Mark up to two active invasion zones on the world map.
2. Rotate attacks among Azshara, Blasted Lands, Burning Steppes, Eastern Plaguelands, Tanaris, and Winterspring.
3. Spawn flying necropolises, their camps, Necrotic Shards, minions, rare enemies, and Cultist Engineers.
4. Let minion deaths weaken a shard, then expose its damaged state.
5. Let a player spend eight Necrotic Runes to summon a Shadow of Doom.
6. Destroy the zone's necropolises, persist a realm victory, rotate the invasion, and update map/world-state counters.
7. Unlock the 50, 100, and 150 battle stages and their Argent Dawn rewards.
8. Run the Stormwind and Undercity assaults as part of the same event.
9. Include event quests, NPCs, vendors, dungeon invaders, drops, and Necrotic Rune spending.
10. End in an epilogue that stops new invasions but preserves the intended turn-in window.

Patch selection and the level axis intersect: the event requires patch 1.11 and the level-cap milestone 60. Reaching level 60 cannot open it on an earlier patch, and selecting 1.11 cannot bypass the server's level progression.

## Runtime ownership

`mod-azeroth-eras` will own the event controller. A generic `game_event` row may own static membership, but it cannot independently own rotation, combat state, counters, milestones, city assaults, persistence, or cleanup.

The controller needs durable realm state for:

- enabled/epilogue/completed state;
- per-zone next-attack timers;
- remaining necropolises for each active zone;
- total battles won and last attacked zone;
- active Stormwind and Undercity assault timers;
- enough spawn identity to resume safely after a restart.

Every transition must be idempotent. A restart must resume the selected patch state, and moving backward below 1.11 must stop child events and remove runtime summons without deleting unrelated creatures.

## Source map

The checked vMaNGOS database supplies the progressive 1.11 data and identifies the event family: global event `17`, zone events `90..95`, milestone events `96..98`, completion event `99`, city events `129/130`, and instance-boss event `81`.

CMaNGOS provides a working reference controller and encounter scripts at pinned revision `1408d4163bb2c107fdb8a543e04d6ae0df221917`:

- [Scourge invasion declarations](https://github.com/cmangos/mangos-classic/blob/1408d4163bb2c107fdb8a543e04d6ae0df221917/src/game/AI/ScriptDevAI/scripts/world/scourge_invasion.h)
- [Scourge invasion encounter scripts](https://github.com/cmangos/mangos-classic/blob/1408d4163bb2c107fdb8a543e04d6ae0df221917/src/game/AI/ScriptDevAI/scripts/world/scourge_invasion.cpp)
- [Persistent world-state controller](https://github.com/cmangos/mangos-classic/blob/1408d4163bb2c107fdb8a543e04d6ae0df221917/src/game/World/WorldState.cpp)

Blizzard corroborates that the event covers the six zones above, major cities, select dungeons, Necrotic Runes, invasion-point enemies, and an epilogue/turn-in period. Later re-releases changed timing and catch-up rules, so those details are evidence for event shape rather than automatic proof of 2006 numerical tuning:

- [WoW Anniversary Edition: Shadow of the Necropolis](https://worldofwarcraft.blizzard.com/en-us/news/24229247/wow-anniversary-edition-brave-the-shadow-of-the-necropolis)
- [WoW Classic 1.13.6 patch notes](https://worldofwarcraft.blizzard.com/en-us/news/23584136)

## Separation from the Wrath event

AzerothCore's 3.3.5 database contains assets from both invasion iterations. Vanilla must not leak Wrath-only rewards such as Haunted Memento or level-70/80 tuning. Every event creature, item, quest, loot row, and spell will be classified as:

- original 1.11;
- Wrath 3.0.2;
- shared asset with era-specific values;
- emulator helper not visible to players.

This classification must be complete before the event loot bundle is promoted to executable SQL.

## Implementation slices

1. **Gate and contract:** correct event `17` availability; commit a tested event manifest. **Implemented.**
2. **Inventory:** extract all vMaNGOS/CMaNGOS event rows and compare them with an installed AzerothCore world snapshot.
3. **Realm controller:** persist state, rotate zones, publish world states, and resume after restart.
4. **Necropolis loop:** camps, shards, minions, cultists, Shadow of Doom, and zone completion.
5. **Cities and dungeons:** Stormwind/Undercity assaults and event enemies in the original instances.
6. **Economy and story:** quests, vendors, Necrotic Runes, rewards, drops, and milestone stages.
7. **Epilogue and rollback:** stop new assaults, preserve intended turn-ins, and cleanly reconcile below 1.11.
8. **Naxxramas bundle:** connect the event to Naxxramas availability without making either system a fragile side effect of the other.

The machine-readable contract is `src/patch_10-1_11/scourge_invasion_manifest.json`. Tests will grow with each slice until no subsystem remains `pending`.
