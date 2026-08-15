# Individual Progression integration inventory

- Audited source: [`Grimfeather/mod-individual-progression`](https://github.com/Grimfeather/mod-individual-progression/tree/67bbaea6d8d6d969bd65899549f775d4abff0b88)
- Pinned revision: `67bbaea6d8d6d969bd65899549f775d4abff0b88`
- Audit date: 2026-08-15
- Purpose: preserve Grim's useful character-aware progression work without creating a second patch timeline or a second owner for world data

## Architectural finding

Individual Progression's state is a raid-clear ladder, not a historical patch ladder. Its Vanilla stages progress from Molten Core through Onyxia, Blackwing Lair, the AQ states, and Naxxramas 40. Azeroth Eras separately needs patch `1.1..1.12`, level milestone `10..60`, and event/encounter state.

The stage number therefore must not be copied into the patch field or used as a patch alias. It becomes scope-owned encounter progress:

```text
effective access = patch availability
                && level milestone
                && character/account encounter progress
                && attunement/key policy
```

This preserves the thing that makes Individual Progression special—each character can have a fresh journey—while Azeroth Eras remains the only authority for what existed in each patch.

## Source inventory and target ownership

| Grim source area | Capability | Azeroth Eras decision |
|---|---|---|
| `IndividualProgression.h/.cpp` | Raid-clear state, custom kill progression, account checks, group synchronization | Extract behind a `ProgressionScopeState` interface; replace hidden-quest storage with versioned persistence after a migration path exists |
| `IndividualProgressionAwareness.cpp` and `zz_ipp_aware_npcs.sql` | Player-aware creature/gameobject visibility | Preserve as a character-scope adapter driven by shared bundle IDs; it must not own a parallel content catalog |
| `IndividualProgressionPlayer.cpp` | Player lifecycle, access, caps, adjustments, attunement, bots | Split by responsibility; scope state and bot synchronization are candidates, while caps/access/tuning call the unified policies |
| `IndividualProgressionBG.cpp`, `IndividualProgressionPvP.cpp`, `av*.sql`, `av_quests.cpp` | Original Alterac Valley and Vanilla PvP behavior | Port as patch-owned 1.5+ PvP bundles, with later patch changes audited separately |
| `vanillaScripts/instance_molten_core.cpp` | Manual rune and Aqual Quintessence behavior | Candidate for the Molten Core bundle after collision review against AzerothCore and the existing module script |
| Onyxia, Kazzak, Blackrock, AQ, and quest scripts | Restored Vanilla encounter/quest behavior | Import one atomic bundle at a time only after entity ownership, patch timing, and core-script conflicts are tested |
| `naxx40Scripts/` and `naxx40*.sql` | Vanilla Naxxramas | Preserve as a dedicated 1.11 bundle with separate identity/routing from Wrath Naxxramas |
| `data/sql/world/base/item_template.sql` and related loot/vendor SQL | Vanilla/TBC item candidates | Evidence input only; compare against vMaNGOS, cMaNGOS, AzerothCore, and primary patch evidence before generation |
| Zone and dungeon base SQL | Broad historical world restoration | Never bulk-import. Decompose into reviewed patch bundles so unrelated rows cannot silently overwrite the target baseline |
| Optional DBC/client archives | Profession, reagent, item, and client-facing changes | Treat as a separately versioned compatibility package; do not commit opaque archives into the module migration path |

## Known collisions

These features already have two possible owners and cannot be enabled independently in a finished installation:

| Feature | Existing Azeroth Eras owner | Individual Progression equivalent | Resolution |
|---|---|---|---|
| Damage/healing approximation | `Progression.Multiplier.*` | Vanilla/TBC power and healing adjustments | One tuning service; never multiply both |
| Level and map access | Milestone and patch policies | Player progression access restrictions | Unified policy consumes character scope state |
| Dungeon Finder | `Progression.DungeonFinder.Enforced` | `IndividualProgression.DisableRDF` | One era feature policy |
| Patch world rows | Patch SQL/reconciler | Large world base SQL | Reconciler owns final state; Grim data is candidate evidence |
| Items and acquisition | Historical item pipeline | Item, loot, vendor, quest SQL | One materialized per-patch item catalog |
| Molten Core/Onyxia scripts | Current bundle scripts | Grim encounter overrides | Select or adapt one implementation per script name/map |
| Battleground availability | Patch-aware battleground layer | Individual Progression BG/AV logic | Patch layer owns availability; AV bundle owns historical behavior |
| Character state | Not yet implemented | Hidden quests/Player Settings and account queries | Migrate into the new scope repository; do not discard existing characters' progress |

## Compatibility blockers to resolve before compile testing

Grim's current README states that the module requires Grim's AzerothCore/Playerbots fork. It also depends on Player Settings for saved character progress and on disabling DBC item-attribute enforcement for server-side item overrides. Those assumptions must be represented as explicit compatibility checks rather than silently inherited.

Before source is copied, record its original copyright/license header and complete a repository-license compatibility review. Preserve attribution for every adapted SQL or C++ bundle.

## Migration sequence

1. Define stable scope, encounter-progress, and bundle identifiers independent of both modules' current numeric enums.
2. Add read-only adapters that can interpret existing Individual Progression hidden-quest/player-setting state.
3. Add versioned Azeroth Eras character/account persistence and a repeatable migration with a dry-run report.
4. Port group and Playerbots synchronization against the shared scope API.
5. Port awareness hooks using bundle IDs supplied by the authoritative patch catalog.
6. Port Vanilla content in patch order: launch/MC/Onyxia, 1.5 PvP, later raids/events, then Naxxramas 40.
7. Disable and remove overlapping Individual Progression runtime owners only after parity tests pass.
8. Retire `mod-progression-system`; keep a migration note mapping its supported ten-level brackets to the eight Azeroth Eras milestones.

## Interim server rule

Do not install all three progression modules on a production database. Until the character-scope merge is complete, treat this branch as a development replacement candidate and keep the current live module set unchanged. Validate against database clones created with the guarded snapshot workflow in [`../database-safety.md`](../database-safety.md).

## Acceptance tests for the merge

- An existing Individual Progression character retains its encounter progress after migration.
- Two characters at different scope states see different eligible NPCs/objects without global database mutation.
- Both characters still use the same selected historical patch and item catalog.
- Patch 1.4 cannot expose a 1.5 battleground even if character encounter progress is advanced.
- A real player cannot bypass an attunement because a grouped bot is eligible.
- Damage/healing adjustment is applied once.
- MC, Onyxia, original Alterac Valley, AQ lifecycle, and Naxxramas 40 each have one registered runtime owner.
- Removing the legacy modules after migration does not remove saved progression state.
