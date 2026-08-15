# Vanilla Patch Accuracy Roadmap

The detailed product design, historical item-state model, implementation phases, and source-module migration status are maintained in [`unified-progression.md`](unified-progression.md). The cross-system definition of Vanilla completion is tracked in [`vanilla-completion-matrix.md`](vanilla-completion-matrix.md).

The current goal is to make `mod-progression` emulate the **historical Vanilla patch cycle** while running on AzerothCore/3.3.5.

The restored historical SQL is useful source material, but it is not assumed to be correct. Each patch must be audited against historical patch notes, known content-release timing and the behavior available in AzerothCore.

An item-only patch is not a completed patch. Quests, loot, vendors, professions, creatures, objects, instances, events, PvP, travel, class behavior, client limitations, and rollback must receive an explicit disposition for every patch.

## Status

| Patch | Historical layer restored | Accuracy audit | Priority |
|:---:|:---:|:---:|---|
| 1.1 | Yes | In progress | **Current live server** |
| 1.2 | Yes | Pending | Next |
| 1.3 | Yes | Pending | Next |
| 1.4 | Yes | Pending | High |
| 1.5 | Yes | Pending | High |
| 1.6 | Yes | Pending | High |
| 1.7 | Yes | Pending | High |
| 1.8 | Yes | Pending | High |
| 1.9 | Yes | Pending | High |
| 1.10 | Yes | Pending | High |
| 1.11 | Yes | Pending | High |
| 1.12 | Yes | Pending | High |

## Historical progression target

The working patch ladder is:

- **1.1 — World of Warcraft:** launch-era leveling, Molten Core, Onyxia and launch dungeons.
- **1.2 — Mysteries of Maraudon:** Maraudon and its related content.
- **1.3 — Ruins of the Dire Maul:** Dire Maul; audit Azuregos, Kazzak, meeting stones and related additions.
- **1.4 — The Call to War:** PvP Honor System; audit Children's Week, Gurubashi Arena changes, elemental invasions and class quest additions.
- **1.5 — Battlegrounds:** Warsong Gulch and Alterac Valley; audit the 1.5 honor-system changes and world hubs.
- **1.6 — Assault on Blackwing Lair:** Blackwing Lair and Darkmoon Faire-era content.
- **1.7 — Rise of the Blood God:** Zul'Gurub and Arathi Basin-era content.
- **1.8 — Dragons of Nightmare:** Nightmare dragons and related world changes.
- **1.9 — The Gates of Ahn'Qiraj:** AQ war effort/opening state, AQ20/AQ40 and associated world/content changes.
- **1.10 — Storms of Azeroth:** weather and dungeon-set upgrade era.
- **1.11 — Shadow of the Necropolis:** Naxxramas and Scourge Invasion.
- **1.12 — Drums of War:** Silithus/EPL world PvP and late-Vanilla systems.

This list is an audit framework, not a claim that every existing SQL row is already historically correct.

## What to audit for every patch

### World and content availability
- Creature spawns and phase masks
- Gameobject spawns
- Dungeon and raid access
- World bosses
- Quest starters/enders and quest chains
- Flight masters, transports and zone hubs
- Seasonal/world events

### Items and economy
- Vendor inventories
- Reputation vendors
- Loot tables and drop locations
- Recipes and profession trainers
- Item stats/availability where server-side data can reproduce the historical version
- Auction-house NPC availability and behavior

### Classes and combat
- Trainer spell availability
- Rank availability
- Server-side spell data that can safely be backported
- Damage/healing approximation required because the core is 3.3.5
- Talent differences: document separately where client DBC changes are required

### PvP
- Honor system on/off
- Rank rewards
- Battleground availability
- Battleground marks/rewards
- Arathi/Alterac rule changes
- World PvP objectives

### Quality-of-life and core features
- Weather
- Quest markers/sparkles/POI
- Meeting stones / group-finding behavior
- Mail expiration
- XP-to-gold at level cap
- Dual spec, Dungeon Finder and later-expansion systems
- Expansion and level-cap enforcement

## 1.1 audit: immediate issues

### Fixed
- **Molten Core (map 409):** the 1.1 bundle now removes stale map-disable rows so the launch raid and physical BRD entrance remain open.
- **Lothos Riftwaker (14387):** remains hidden in 1.1-1.2 and unlocks with both attunement quest variants in 1.3.
- **Core Fragment (179553):** hidden in 1.1-1.2, placed inside Molten Core in 1.3, and restored to AzerothCore's canonical BRD-side spawn in 1.4.
- **MC shortcuts (area triggers 3528/3529):** unavailable before 1.3 and require a rewarded Alliance or Horde attunement quest thereafter. The physical BRD trigger (2886) remains untouched.
- **Molten Core bundle regression coverage:** CI validates the NPC, quests, gameobject location, shortcut gates, and map-open invariant together.
- **Horde Onyxia attunement:** Emberstrife is restored, while the 3.3.5 Rokaro shortcut is replaced with launch-era Rexxar, Misha, Rexxar-era quest/item text, and the full Desolace patrol.
- **Vanilla item discovery:** the pipeline now materializes vMaNGOS 1.2-1.12 item states and audits inherited patch SQL coverage. The inherited files cover 465 of 2,327 vMaNGOS revision candidates; the remaining 1,862 are queued for field-level historical review rather than blind import.

### Next checks
1. Audit the Alliance Onyxia chain and validate both faction chains in game from first quest through Drakefire Amulet access.
2. Verify Maraudon is actually unavailable until 1.2.
3. Verify Dire Maul, Azuregos and Kazzak stay unavailable until their intended patch.
4. Reconstruct the complete 1.1 item snapshot, then review the 1,862 uncovered vMaNGOS revision candidates and their acquisition paths in patch order.
5. Audit 1.1 vendor inventories so later recipes/items do not leak into the launch economy.
6. Audit trainer spells and profession recipes for later-patch additions.
7. Audit holiday/event tables so later events do not accidentally run at 1.1.
8. Check later-expansion NPC leakage not covered by the existing hidden-content list.

## 1.11 Scourge Invasion

The original invasion is now tracked as an owned event bundle rather than a single `game_event` toggle. The first correction gates AzerothCore/vMaNGOS event `17` at patch 1.11; the inherited SQL had only toggled event `1`, which is Midsummer Fire Festival. The complete lifecycle, source map, Vanilla/Wrath separation rules, and implementation slices are documented in [`research/vanilla-scourge-invasion.md`](research/vanilla-scourge-invasion.md).

## Loader reliability

A patch emulator is useless if the database layers silently fail to run. The loader therefore must:

- auto-detect the actual module source folder;
- support both `mod-progression` and `mod-02-progression`;
- validate every selected patch SQL directory before invoking `DBUpdater`;
- log the active patch and cumulative directory count;
- log missing directories as errors instead of silently skipping them;
- allow the guarded `Progression.Reset = 1` plus `Progression.Development.AllowUnsafeReset = 1` pair to reapply `patch_*` SQL on disposable development databases.

## Evidence policy

For future patch audits:

- Prefer archived/original Blizzard patch notes when available.
- Use Blizzard's Classic historical/re-release documentation as corroboration.
- Use Warcraft Wiki/Wowpedia-style archives when original Blizzard pages are unavailable, and label those findings as secondary.
- Treat the old module's patch SQL and embedded patch notes as implementation history, not authoritative historical evidence.

## Known client/core limitation

This project runs on the 3.3.5 client and AzerothCore. Some authentic patch differences cannot be reproduced only with world SQL. Those should be classified as:

- **Exact** — reproduce directly in DB/core configuration.
- **Approximation** — reproduce the player-facing effect with server code.
- **Client patch required** — requires DBC/client data changes.
- **Not practical** — document rather than fake it.

The objective is a coherent historical progression experience, not pretending the 3.3.5 client is byte-for-byte a 1.1 client.
