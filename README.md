# Unified Progression

**Unified Progression** is a rework of `mod-progression` for AzerothCore that is intended to become a single, deterministic progression system for servers that want to experience World of Warcraft content in historical order on the 3.3.5 client/core.

The repository is still named `mod-progression` while the rewrite is in progress. "Unified Progression" is the working project name for the new architecture.

## Why this fork exists

The original progression setup grew into several overlapping systems:

- server-wide historical content progression,
- level/bracket progression,
- individual-character progression,
- SQL that directly phases creatures and gameobjects,
- runtime hooks that separately gate maps, mechanics and player power.

Each system solves a useful problem, but running them together can create contradictory world state. One module can make an NPC visible while another still hides the quest object it depends on. A level unlock can remove a database restriction that a historical patch still expects to exist. Two difficulty layers can also modify the same player behavior at the same time.

This fork exists to remove those overlaps and make progression have **one source of truth**.

## Core design

Unified Progression separates progression into three concepts.

### 1. Historical patch

```ini
Progression.Patch = 0
```

The active patch determines what content existed at that point in World of Warcraft's timeline. Patch SQL is cumulative and is applied in historical order.

For example, selecting patch `2` applies the 1.1, 1.2 and 1.3 data layers.

### 2. Level milestone

```ini
Progression.LevelGating.Enabled = 1
Progression.LevelCap = 60
```

Level progression controls the current leveling milestone without competing with patch SQL for ownership of historical content state.

The supported milestone ladder is:

`10 -> 20 -> 30 -> 40 -> 50 -> 60 -> 70 -> 80`

Content is available only when both the level milestone and the historical patch allow it.

For Vanilla, these are launch stages: the realm begins with the `1-10` stage,
then advances through the ten-level stages until `50-59`. At level 60 the
Chromie-style dungeon ladder is complete. Level gating no longer withholds a
Vanilla dungeon, but historical patch gates, raid attunements, keys, and quest
requirements continue to apply. Patch progression and level progression never
unlock one another.

For the first Dire Maul test, use `Progression.LevelCap = 60` and
`Progression.Patch = 2`. Patch ID `1` is Vanilla 1.2 (Maraudon); Dire Maul was
released in Vanilla 1.3 and is patch ID `2` in this module.

### 3. Progression scope

The individual-progression merge will define **whose progression state is evaluated**, rather than maintaining a second independent content timeline.

Planned scopes are:

- `Server` — one shared progression state for the realm.
- `Character` — each character progresses independently using the same patch/content definitions.
- `Account` — a possible future option for progression shared across characters.

The goal is to reuse the persistence, phasing and player-aware behavior from Individual Player Progression while keeping one authoritative definition of what every patch unlocks.

See `docs/unified-progression.md` for the full design, item-progression model, implementation sequence, and source-module migration status.

## The most important rule: unlocks are atomic

A content unlock is not just a creature phase or one SQL row.

If a feature depends on several pieces, those pieces must move through progression together. A historical unlock may include:

- creatures and NPCs,
- gameobjects,
- quest starters and quest enders,
- quest items and loot,
- vendors and trainers,
- instance access,
- conditions and disables,
- scripts and runtime behavior.

The rewrite treats these as one logical content bundle.

This rule was reinforced during the Vanilla audit by the Molten Core discovery/attunement chain. The authoritative Molten Core bundle now keeps the raid and physical BRD entrance open in 1.1-1.2 while hiding Lothos, disabling both faction quest variants, hiding the Core Fragment, and blocking only the window/lava shortcuts. Patch 1.3 unlocks those dependencies together and places the Fragment inside Molten Core; patch 1.4 moves it to the canonical BRD-side location. The lesson is now executable: **dependent progression data must never be advanced independently.**

## Vanilla patch map

| ID | Patch | Title |
|---:|:---:|---|
| 0 | 1.1 | World of Warcraft (retail launch) |
| 1 | 1.2 | Mysteries of Maraudon |
| 2 | 1.3 | Ruins of the Dire Maul |
| 3 | 1.4 | The Call to War |
| 4 | 1.5 | Battlegrounds |
| 5 | 1.6 | Assault on Blackwing Lair |
| 6 | 1.7 | Rise of the Blood God |
| 7 | 1.8 | Dragons of Nightmare |
| 8 | 1.9 | The Gates of Ahn'Qiraj |
| 9 | 1.10 | Storms of Azeroth |
| 10 | 1.11 | Shadow of the Necropolis |
| 11 | 1.12 | Drums of War |

The **current ready target is 1.1 through 1.6** (IDs `0`–`5`): launch, Maraudon, Dire Maul / MC attunement, Honor, battlegrounds, and Blackwing Lair. See [`docs/vanilla-1.1-1.6-target.md`](docs/vanilla-1.1-1.6-target.md). Later Vanilla IDs still exist so the realm can keep walking the ladder, but they are not the accuracy target yet.

Blizzard shipped retail launch as client patch 1.1.0. Patch ID `0` therefore
means Vanilla 1.1, and the playable steps are
`1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6`.

TBC and Wrath patch SQL is also present as a foundation, but those eras are not the current target.

## Accuracy model

A 3.3.5 client/core cannot literally become a 1.1, 1.12, 2.x or early-Wrath client. Unified Progression therefore separates historical accuracy into four layers:

1. **Data gating** — creatures, gameobjects, quests, vendors, recipes, loot, instances, raids, world bosses and events.
2. **Runtime rules** — level/expansion caps, battleground availability, quest UI behavior and other rules exposed by AzerothCore.
3. **Server-side approximations** — mechanics or tuning needed because the 3.3.5 ruleset differs materially from the target era.
4. **Client limitations** — behavior that cannot be faithfully reproduced without client changes and must therefore be documented rather than silently approximated.

See `docs/vanilla-patch-roadmap.md` for the ongoing patch audit and `docs/vanilla-completion-matrix.md` for the full world-state workstream and completion criteria.

## SQL loading

The module uses AzerothCore's database updater and loads every patch directory from 1.1 through the selected patch.

It automatically detects any of these module source directories:

- `mod-azeroth-eras`
- `mod-02-progression`
- `mod-progression`

A custom source directory can be supplied with `Progression.ModuleDirectory`.

### Database safety and development SQL reset

Before installing the module or changing a live realm's patch data, take verified snapshots of the AzerothCore auth, characters and world databases. The guarded backup/restore workflow is documented in [`docs/database-safety.md`](docs/database-safety.md).

`Progression.Reset` is only a development aid for replaying SQL on a disposable database:

```ini
Progression.Reset = 1
Progression.Development.AllowUnsafeReset = 1
```

This clears the module's `patch_*` updater records so the selected cumulative patch layers are reapplied on startup. It does not undo overwritten or deleted data and must not be used as a production rollback mechanism.

After a successful reset, return it to:

```ini
Progression.Reset = 0
Progression.Development.AllowUnsafeReset = 0
```

A reset is not intended to be a permanent runtime mode.

## Current recommended Vanilla configuration

```ini
Progression.LevelGating.Enabled = 1
Progression.LevelCap = 60
Progression.Patch = 0
# Advance 0 -> 1 -> 2 -> 3 -> 4 -> 5 for the 1.1-1.6 ready target.
Progression.Reset = 0
Progression.Development.AllowUnsafeReset = 0
```

Adjust the selected patch as the realm progresses.

## Admin command

```text
.progression info
```

This reports the active patch, level gating state, effective level cap, patch-era cap and SQL reset state.

## Rewrite and merge roadmap

The current work is intentionally more than a patch-data cleanup.

1. Audit Vanilla patch SQL and remove contradictory/stale unlocks.
2. Convert content unlocks into deterministic, testable patch bundles.
3. Finish migrating the useful level-bracket behavior into the unified runtime engine.
4. Merge Individual Player Progression persistence and player-aware phasing as a progression **scope**, not as another competing timeline.
5. Consolidate damage/healing and other era-simulation settings so only one subsystem owns each modifier.
6. Add validation that detects incomplete unlock bundles and suspicious hidden-content rows before they reach a live realm.
7. Audit TBC and Wrath with the same rules after Vanilla is stable.
8. Rename/rebrand the repository and configuration namespace once the unified implementation is ready to replace the legacy modules cleanly.

## Relationship to Individual Player Progression

Individual Player Progression contains valuable work that this project intends to preserve, including character-specific progression persistence, player-aware NPC/gameobject visibility, restored historical content and Playerbots-friendly progression.

The merge is not intended to discard that work. Instead, the goal is to remove duplicate definitions of progression. Unified Progression should answer **what is unlocked**, while the selected progression scope answers **for whom it is unlocked**.

The pinned source inventory, collision map, migration order, and coexistence rules are documented in [`docs/research/individual-progression-integration.md`](docs/research/individual-progression-integration.md).

## Project status

This branch is an active rewrite and audit. It should be treated as development software until the Vanilla timeline has been validated end-to-end.

If you are testing it, keep database backups and use `.progression info` when reporting progression-state problems. Reports that identify the active patch, level cap, affected NPC/gameobject/quest ID and current `phaseMask` are especially useful.

## Credits

This work builds on the original `mod-progression`, Individual Player Progression, AzerothCore, TrinityCore and the historical data and restoration work contributed by the wider emulator community. The rewrite exists to make those ideas cooperate predictably rather than forcing server owners to stack several progression systems that can disagree with one another.
