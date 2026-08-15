# Unified Progression design

- Status: working design, 2026-08-15
- Implementation target: AzerothCore and the 3.3.5a client
- Current accuracy target: Vanilla 1.1 at level 60

## Purpose

Unified Progression is the single progression module produced by merging the useful parts of:

- `mod-progression`, which provides the historical patch timeline;
- `mod-progression-system`, which provides level-bracket gates and selected encounter restorations;
- `mod-individual-progression`, which provides character-aware state, restored historical data, Playerbots integration, and selected encounter implementations.

The module must answer one question deterministically:

> Given a progression scope, level milestone, and historical patch, what exact world state should this player experience?

The answer includes more than raid availability. It includes item templates, loot sources, vendors, recipes, quests, NPCs, gameobjects, encounter behavior, PvP systems, world events, and server-side rules.

## Product requirements

1. Use one authoritative definition of historical world state.
2. Support level milestones `10 -> 20 -> 30 -> 40 -> 50 -> 60 -> 70 -> 80`.
3. Require both the level milestone and historical patch to permit content.
4. Reproduce Vanilla item data during Vanilla, TBC item data during TBC, and Wrath item data during Wrath.
5. Reproduce changes inside an era at the patch in which they occurred, rather than treating an expansion as one static database.
6. Make forward and backward progression transitions deterministic and testable.
7. Support server-wide progression first, then character and possibly account scope without duplicating the content timeline.
8. Preserve raid attunements for real players. A configured bot simulation may waive an attunement requirement for bots, but must not waive it for real players.
9. Gate raids, not ordinary five-player dungeons, with raid lockout rules.
10. Keep combat/difficulty adjustment under one owner so multipliers cannot compound with another difficulty module.

## Non-goals

- Byte-for-byte emulation of an old client on the 3.3.5a client.
- Importing every SQL file from either source module without provenance and conflict review.
- Retaining the 39 independent Boolean brackets from `mod-progression-system`.
- Allowing character progression to define a second, contradictory historical timeline.
- Faking client-only changes when a faithful server-side representation is not possible.

## Effective progression state

The effective state is the intersection of three axes:

| Axis | Values | Responsibility |
|---|---|---|
| Scope | `Server`, later `Character`, possibly `Account` | Whose saved state is evaluated |
| Level milestone | 10, 20, 30, 40, 50, 60, 70, 80 | Level cap and coarse instance access |
| Historical patch | 1.1 through 3.3.5 | What existed and how it behaved |

An unlock is available only if all applicable predicates are true:

```text
available = scope_state_allows
         && level_milestone_allows
         && historical_patch_allows
         && attunement_or_key_allows
```

The era imposes an absolute cap: Vanilla 60, TBC 70, and Wrath 80. A configured milestone above the era cap is clamped to the era cap.

### Initial scope behavior

`Server` is the first supported scope and remains the reference implementation. Character scope will reuse the same patch and bundle definitions, replacing only how the effective state is retrieved and how visibility/access is evaluated.

The scope layer must not mutate global rows differently for different characters. Character-specific visibility belongs in player-aware runtime hooks and phasing.

## Ownership model

Every progression-controlled row, field, or hook must have one owner.

| State | Owner |
|---|---|
| Historical NPC, object, quest, item, loot, vendor, recipe, and event state | Patch bundle/reconciler |
| Level cap and milestone map access | Runtime level-gating layer |
| Per-character persistence and visibility | Scope layer |
| Raid attunement and keys | Access policy, evaluated after patch and milestone |
| Era combat approximation | One unified tuning subsystem or the external difficulty module, never both |
| Client assets and DBC overrides | Versioned client-data package |

Historical patch SQL may own a `disables` row. Level gating therefore uses `OnPlayerCanEnterMap` and must not delete that row when a level milestone advances.

## Atomic content bundles

A feature is an atomic bundle, not a single creature spawn or SQL statement. A bundle can own:

- creature templates and spawns;
- gameobject templates and spawns;
- quest starters, enders, chains, text, objectives, and rewards;
- required quest items and their loot sources;
- vendors, trainers, recipes, and reputation requirements;
- conditions, disables, instance access, and area triggers;
- runtime scripts and encounter mechanics;
- item-template state and all acquisition paths;
- validation rules.

All required parts must move together. A quest must never be visible while its required object is hidden, and an item must never be advertised by a vendor while its template is in a later-era state.

### Molten Core reference bundle

The first enforced bundle defines:

| Patch | Expected state |
|---|---|
| 1.1-1.2 | Molten Core and the physical BRD entrance are open; Lothos, both attunement quests, Core Fragment, and both shortcuts are unavailable |
| 1.3 | Lothos and both quests unlock; Core Fragment exists inside Molten Core; shortcuts require either rewarded attunement quest |
| 1.4+ | Core Fragment moves to the canonical BRD-side portal location |

Area trigger 2886 remains the physical entrance. Shortcut triggers 3528 and 3529 are patch- and attunement-aware. The remaining MC bundle work includes the historical seven-rune/Aqual Quintessence behavior and encounter/loot/itemization audits.

## Historical item system

### Required behavior

An item's state is selected by historical patch, not by the 3.3.5 database that happens to be installed beneath the module.

- Vanilla patches use the Vanilla version of an item.
- TBC patches use the TBC version, including TBC changes to old Vanilla items.
- Wrath patches use the Wrath version, including later changes to old items.
- A change made within an era becomes active at the correct patch.
- An item introduced later must not leak through loot, vendors, quests, mail, crafting, or containers before its introduction.

Item progression includes more than `item_template`:

| Domain | Examples |
|---|---|
| Identity | name, quality, class/subclass, inventory type |
| Power | armor, damage, delay, stats, resistances, random properties, sockets |
| Requirements | level, class, race, skill, reputation, unique/equipped flags |
| Effects | spell IDs, triggers, charges, cooldowns, proc rates |
| Economy | buy/sell price, stack size, bonding, duration |
| Appearance | `displayid`, when the 3.3.5 client still contains the historical asset |
| Sets | set membership and server/client-supported set bonuses |
| Acquisition | creature/object/item loot, quest rewards, vendors, trainers, recipes, mail |
| Availability | introduced patch, removed patch, replacement relationship |

### Canonical snapshots and deltas

The installed AzerothCore 3.3.5 world database is an input baseline, not the historical authority. The target data model has:

1. a captured canonical 3.3.5 value for every progression-owned field;
2. a fully materialized expected snapshot for each supported patch;
3. reviewed deltas explaining the transition between adjacent patches;
4. provenance and confidence for every historical assertion.

Snapshots make the selected state unambiguous. Deltas make review practical. Generated SQL should be derived from the snapshot/delta model; hand-written cumulative updates are not the source of truth.

Suggested manifest shape:

```yaml
entity: item
id: 16854
owner: vanilla.tier1
states:
  "1.1":
    template: data/items/1.1/16854.yaml
    available: true
    sources: [loot:boss-id]
  "1.4":
    inherit: "1.1"
    template: data/items/1.4/16854.yaml
  "2.0":
    template: data/items/2.0/16854.yaml
evidence:
  - source: archived-patch-notes
    confidence: primary
limitations:
  appearance: exact
```

The exact serialization may change, but the information and ownership rules may not.

### Reconciliation

For a selected patch, the reconciler will:

1. load the canonical baseline and all owned manifests;
2. resolve inheritance into a complete expected state;
3. compare expected and actual database values;
4. apply only owned differences in a transaction;
5. validate acquisition paths and dependent bundles;
6. record manifest version, checksums, and the resulting state.

This must support transitions such as `1.1 -> 1.4`, `1.4 -> 1.1`, and `1.1 -> 1.12 -> 1.3`. The current `Progression.Reset` behavior, which clears updater records and replays cumulative SQL over a mutated database, is a development aid and does not satisfy this requirement.

### Existing item data and import policy

The repository already contains historical `item_template` SQL in many patch directories. Individual Progression also contains large `vanilla_item_changes.sql` and `tbc_item_changes.sql` datasets plus optional DBC/client patches. These are candidate inputs, not automatically trusted snapshots.

Each candidate change must be normalized, assigned to a bundle and patch, compared with the AzerothCore baseline and other historical projects, and given evidence/confidence. Conflicts are resolved explicitly; load order must never decide historical truth.

The item pipeline uses vMaNGOS as the primary candidate source for Vanilla 1.2-1.12 transitions, cMangos Classic as a final-1.12 cross-check, cMangos TBC as the TBC snapshot, and AzerothCore as the target Wrath baseline. vMaNGOS does not provide launch 1.1, so that state still requires separate reconstruction and corroboration. Pinned revisions, schema findings, counts, and the comparison command are documented in [`research/item-data-pipeline.md`](research/item-data-pipeline.md).

### Client limitations

Every historical difference is classified as:

- **Exact** — reproducible in world data or server code.
- **Approximation** — the player-facing effect can be reproduced server-side.
- **Client patch required** — needs DBC or MPQ data on both server and client.
- **Not practical** — documented instead of imitated misleadingly.

Historical Tier 1/Tier 2 placeholder appearances are exact when the display assets remain in the 3.3.5 client. Recipe reagents, spell descriptions, set bonuses, or UI behavior may require a versioned client-data package. Server and client package versions must be reported together by the admin command.

## Vanilla patch audit plan

Patch notes describe visible changes, but implementation requires an entity-level audit. Every patch receives a manifest, evidence register, bundle inventory, SQL/runtime changes, limitations, and regression tests.

The complete cross-system workstream inventory, present SQL-layer breadth, gaps, and patch completion rules are maintained in [`vanilla-completion-matrix.md`](vanilla-completion-matrix.md). No patch is considered accurate based on item data or raid availability alone.

| ID | Patch | Major historical targets | Item/economy targets | Audit state |
|---:|:---:|---|---|---|
| 0 | 1.1 | Launch world; MC; Onyxia; launch dungeons, quests, classes, professions, PvP state | Establish launch item snapshot; remove later acquisition leakage; launch loot/vendors/recipes and placeholder raid appearances | In progress |
| 1 | 1.2 | Maraudon and related quests/mechanics | Maraudon loot, quest rewards, recipes, and December 2004 item changes | Pending |
| 2 | 1.3 | Dire Maul, Azuregos, Kazzak, meeting stones, dungeon caps, MC shortcut | Dire Maul/world-boss loot, new profession recipes, item quality/stat/appearance changes | MC access fixed; rest pending |
| 3 | 1.4 | Honor system, PvP ranks/rewards, class and dungeon revisions | Honor rewards, dungeon loot overhaul, profession and stat changes | MC fragment move fixed; rest pending |
| 4 | 1.5 | WSG, Alterac Valley, honor revision, world hubs | Battleground rewards, rank gear, vendor and reputation changes | Pending |
| 5 | 1.6 | Blackwing Lair, Darkmoon Faire-era content, class revisions | BWL loot, Tier 2 source/state, Darkmoon rewards, recipe and item changes | Pending |
| 6 | 1.7 | Zul'Gurub, Arathi Basin, debuff limit and class revisions | ZG loot/tokens/enchants, AB rewards, set and profession changes | Pending |
| 7 | 1.8 | Nightmare dragons, Silithus/world revisions | World-boss loot, vendor/recipe and item stat changes | Pending |
| 8 | 1.9 | AQ war effort, gate event, AQ20/AQ40, linked quest lines | AQ loot/tokens/sets, war-effort items, profession recipes, relic/ranged-slot changes | Pending |
| 9 | 1.10 | Weather, dungeon-set upgrade quests, dungeon loot revision | Dungeon Set 2, broad dungeon loot/itemization, profession and reputation rewards | Pending |
| 10 | 1.11 | Naxxramas 40, Scourge Invasion, major class revisions | Tier 3, Naxx/Scourge loot and crafting, key/attunement economy | Pending |
| 11 | 1.12 | World PvP objectives, cross-realm battleground-era rules, final Vanilla class changes | Final Vanilla item states, PvP rewards, riding/item requirement changes | Pending |

This table is an audit contract, not a claim that the inherited SQL already implements every listed change.

### Vanilla raid order

The intended raid progression is:

1. Molten Core
2. Onyxia's Lair
3. Blackwing Lair
4. Zul'Gurub
5. Ruins of Ahn'Qiraj
6. Temple of Ahn'Qiraj
7. Naxxramas 40

Historical patch availability still applies. Reaching level 60 does not open a raid from a later patch. Naxxramas 40 and Wrath Naxxramas must remain distinct content targets with unambiguous routing.

## Later-era plan

Vanilla is completed and validated first. TBC and Wrath use the same architecture rather than another migration.

| Era | Patches | Level cap | Item-state objective |
|---|---|---:|---|
| Vanilla | 1.1-1.12 | 60 | Patch-correct Vanilla templates and sources |
| TBC | 2.0-2.4 | 70 | TBC templates, including TBC revisions to Vanilla items, with patch-specific sources |
| Wrath | 3.0-3.3.5 | 80 | Wrath templates and patch-specific emblem, raid, vendor, and catch-up changes |

The current patch ID map remains `0..21`. Patch aliases may be added for readability, but persisted state must use stable identifiers and support migrations if IDs ever change.

## Merge status

### Summary

| Capability | Source | Current status | Target |
|---|---|---|---|
| Patch ladder 1.1-3.3.5 | `mod-progression` | **Implemented foundation**; cumulative SQL restored, accuracy incomplete | Replace SQL-as-authority with reviewed manifests/reconciliation |
| Level milestones 10-80 | `mod-progression-system` | **Implemented foundation**; validation, era clamping, max level, and runtime map gates exist | Complete access matrix and tests without Boolean brackets |
| Atomic content bundles | New architecture | **Partially implemented**; MC and launch Horde Onyxia are first bundles | Manifest and validator for all progression content |
| Server scope | Current module | **Implemented** | Remain reference scope |
| Character persistence | Individual Progression | **Not merged** | Scope-state repository and migrations |
| Player-aware NPC/GO visibility | Individual Progression | **Not merged** | Runtime scope layer using shared bundles |
| Playerbots integration | Individual Progression | **Not merged** | Bot-aware state; optional attunement waiver only for bots |
| Vanilla/TBC historical item datasets | Individual Progression and existing patch SQL | **Discovered, not normalized** | Evidence-backed per-patch snapshots and deltas |
| MC seven-rune/Aqual Quintessence behavior | Both source modules | **Not merged** | Safe `instance_molten_core` override plus tests |
| Kazzak and selected restored encounters | Both source modules | **Not merged/audited** | Port only when patch ownership and core conflicts are resolved |
| Onyxia launch Horde attunement | Historical audit/Individual Progression evidence | **Implemented in branch** | In-game validation; Alliance chain audit |
| Naxxramas 40 | Individual Progression | **Not merged** | Separate map/content identity and routing from Naxxramas 80 |
| Combat scaling | Current module and Individual Progression | **Conflict remains**; current defaults are damage `0.6`, healing `0.5` pre-Wrath | One owner; use `1.0` in this module when external difficulty owns tuning |
| Deterministic backward transitions | New architecture | **Designed, not implemented** | Transactional reconciler with baseline restoration |
| Client-data package | Individual Progression optional assets | **Not merged/audited** | Versioned, optional package with compatibility reporting |

### What has already landed

- Public identity and architecture documented as Unified Progression.
- Level-gating configuration accepts only the eight ten-level milestones.
- Active era clamps the effective cap to 60/70/80.
- Runtime map gates preserve the historical patch layer's database ownership.
- Patch SQL directory discovery, validation, cumulative loading, and development reset are implemented.
- `.progression info` reports patch, level-gating state, effective cap, era cap, and reset state.
- Molten Core 1.1-1.4 access/attunement bundle is implemented with regression tests.
- Launch-era Horde Onyxia attunement restores Rexxar, Misha, the Desolace patrol, Emberstrife, and launch-era quest/item text, with regression tests.

### What has not been merged

No character progression persistence, player-aware visibility, or Playerbots scope logic from Individual Progression is active in this repository yet. Its large historical SQL sets, Naxxramas 40 implementation, and most encounter scripts are also not present as unified owned bundles. The old bracket module's Boolean loader and down-file chain are intentionally not being copied.

## Runtime and persistence design

The target runtime API separates definition from state:

```text
ProgressionCatalog   -> immutable patch/bundle/item definitions
ProgressionState     -> scope + patch + milestone + flags
ProgressionPolicy    -> access/visibility/attunement decisions
ProgressionReconciler-> global owned database state
ProgressionValidator -> invariants, provenance, drift, client compatibility
```

Suggested persisted state:

| Field | Purpose |
|---|---|
| scope type and key | server/character/account owner |
| patch ID | stable historical patch |
| level milestone | one of the eight supported caps |
| progression flags | event/bundle states such as AQ opening where historically necessary |
| revision | optimistic migration/version control |
| updated time and actor | auditability |

Patch selection and raid-clear progression are related but not identical. Historical patch availability answers whether content exists; encounter progression and attunement answer whether the player may enter or advance.

## Validation and tests

### Build-time/data generation

- Reject duplicate owners for the same table/key/field.
- Materialize every patch and verify inheritance has no gaps.
- Validate item field types, IDs, spell references, and display IDs.
- Confirm every introduced item has at least one intended acquisition path or an explicit unobtainable declaration.
- Detect loot/vendor/quest sources active outside the item's availability window.
- Produce adjacent-patch diffs suitable for human review.
- Record provenance and confidence for every non-baseline value.

### Runtime/startup

- Validate configuration, scope state, milestone, and patch ID.
- Detect drift between expected and actual owned database state.
- Report incomplete bundles with exact entity IDs.
- Refuse unsafe reconciliation when the baseline/version is incompatible.
- Report the required client-data package and whether it matches.

### Regression suites

- Forward and backward transition tests for every adjacent patch.
- Fresh-database and previously-mutated-database reconciliation tests.
- Item snapshot tests across at least one unchanged, changed, introduced, removed, and replacement item per patch bundle.
- Loot/vendor/quest acquisition consistency tests.
- Real-player versus bot attunement tests.
- Server versus character-scope visibility tests.
- Vanilla Naxxramas 40 versus Wrath Naxxramas 80 routing tests.
- Smoke tests in AzerothCore for compilation, SQL syntax, and startup validation.

## Implementation sequence

### Phase 1 — Vanilla state foundation

1. Capture the canonical AzerothCore 3.3.5 baseline for progression-owned tables.
2. Define manifest schema, ownership registry, evidence format, and generated SQL format.
3. Import existing 1.1 item SQL as unverified candidates and build the first materialized 1.1 item snapshot.
4. Build drift reporting and read-only validation before enabling writes.
5. Convert MC and Onyxia work into manifest-backed reference bundles.

### Phase 2 — Vanilla patch accuracy

1. Complete the full 1.1 launch audit, including Alliance Onyxia, vendors, trainers, professions, events, and later-expansion leakage.
2. Extract vMaNGOS 1.2-1.12 item and acquisition snapshots, then audit them in order against primary evidence and cMangos, producing reviewed adjacent-patch diffs.
3. Port selected MC, Kazzak, raid, event, vendor, and loot behavior from the source modules only when its owning bundle is ready.
4. Implement and validate deterministic down-transitions.
5. Complete Naxxramas 40 as a separate Vanilla bundle.

### Phase 3 — Scope merge

1. Add state storage behind a scope-neutral interface.
2. Port character persistence and player-aware NPC/GO visibility.
3. Add Playerbots-aware progression and the explicit bot attunement policy.
4. Extend `.progression info` to show effective scope state and validation failures.
5. Retire the old Individual Progression timeline/configuration after migration tooling exists.

### Phase 4 — TBC and Wrath

1. Materialize and audit 2.0-2.4 item/content snapshots.
2. Materialize and audit 3.0-3.3.5 item/content snapshots.
3. Audit attunement removals, catch-up systems, emblem changes, raid revisions, and old-item changes at their actual patches.
4. Publish compatible server/client data package versions where exact emulation requires them.

## Acceptance criteria for Vanilla

Vanilla is considered complete when:

- all patches 1.1-1.12 have reviewed manifests and evidence registers;
- every progression-owned item has a materialized expected state and acquisition state for each patch;
- selecting a Vanilla patch cannot expose a TBC/Wrath item version or later acquisition path;
- the full raid order, attunements, quests, world bosses, PvP systems, professions, vendors, events, and major patch mechanics pass bundle validation;
- forward and backward transitions produce the same expected state as a clean installation at the target patch;
- the 3.3.5 client limitations for each unsupported difference are explicit;
- real-player and bot policies are tested separately;
- one and only one subsystem owns combat adjustment.

## Evidence policy

Historical assertions should prefer:

1. original or archived Blizzard patch notes and client data;
2. Blizzard's historical/Classic engineering documentation as corroboration;
3. versioned emulator databases such as vMaNGOS/cMaNGOS as implementation evidence;
4. the source modules and community archives as candidate evidence, not automatic authority.

Every audit records the source URL or repository revision, the exact claim it supports, confidence, and any conflict resolution. Blizzard's Classic engineering write-up is also an important warning: using a later client/core foundation does not itself restore earlier data. The historical data must be selected and validated deliberately.

### Initial research register

- [Blizzard: Dev Watercooler — World of Warcraft Classic](https://worldofwarcraft.blizzard.com/news/21881587/dev-watercooler-world-of-warcraft-classic) — official explanation of restoring 1.12 data on a newer foundation.
- [Blizzard: World of Warcraft Classic FAQ](https://worldofwarcraft.blizzard.com/news/23090136/world-of-warcraft-classic-faq-what-you-need-to-know) — official phased-content reference and 1.12 Alterac Valley decision.
- [Blizzard: Shadow of the Necropolis](https://worldofwarcraft.blizzard.com/en-gb/story/timeline/chapter-10) — official patch 1.11 timeline reference.
- [Warcraft Wiki: patch index](https://warcraft.wiki.gg/wiki/Patch) — secondary index to archived patch notes; individual claims still require evidence review.
- [`TopHatMan/mod-progression-system`](https://github.com/TopHatMan/mod-progression-system) — source-module implementation evidence.
- [`Grimfeather/mod-individual-progression`](https://github.com/Grimfeather/mod-individual-progression) — scope, Playerbots, restored-content, item, and optional client-data candidates.
- [`research/individual-progression-integration.md`](research/individual-progression-integration.md) — pinned source inventory, ownership collisions, and migration sequence for Grim's module.
- [`vmangos/core`](https://github.com/vmangos/core) and [`cmangos/mangos-classic`](https://github.com/cmangos/mangos-classic) — versioned emulator implementation evidence, not substitutes for primary historical sources.

## Current testing configuration

For the current level-60 Vanilla 1.1 audit:

```ini
Progression.LevelGating.Enabled = 1
Progression.LevelCap = 60
Progression.Patch = 0
Progression.Reset = 0
Progression.Development.AllowUnsafeReset = 0
```

`Progression.Reset = 1` is only a temporary development reapply mechanism and is blocked unless `Progression.Development.AllowUnsafeReset = 1` is also set. Both should be returned to `0` after use, and this mechanism must eventually be superseded by deterministic reconciliation. Operational backup and guarded restore instructions are in [`database-safety.md`](database-safety.md).
