# Historical item data pipeline

Status: progressive Vanilla extraction and cross-era comparison tooling implemented
Scope: vMaNGOS 1.2-1.12, cMangos Classic 1.12.1, cMangos TBC, and AzerothCore 3.3.5a

## Why these sources

vMaNGOS is the primary candidate source for Vanilla patch boundaries because its item table stores multiple rows per item and selects the newest row at or before the configured content patch. cMangos Classic and TBC provide coherent full-era cross-checks. AzerothCore provides the target 3.3.5a schema and Wrath baseline. Comparing all four gives Unified Progression a practical starting point without treating any cross-project SQL file as directly portable or historically authoritative on its own.

The first pinned source revisions are:

| Source | Revision |
|---|---|
| `vmangos/core` and `db_latest` | `18e37d1fe736a46ff916404d13e58302b5f05ef0`; database snapshot 2026-08-14, SHA-256 `f4101da8058a1f49d90b1820331b3d057f89b4f41bec624ebb8de8bdc27678a5` |
| `cmangos/classic-db` | `250a705a462c1acb457d3002359c7e0052c4dafe` |
| `cmangos/tbc-db` | `c972214b37980388ad602700e76b4136fa9ae940` |
| `azerothcore/azerothcore-wotlk` | `1e4d35bfce216c98c0d2804de2f085b44919dbf9` |

These revisions identify candidate datasets. Patch-note and client-data research is still required before a difference becomes authoritative patch data.

## Current schema findings

| Dataset | `item_template` columns | Important distinction |
|---|---:|---|
| vMaNGOS | 130 | Progressive `(entry, patch)` rows for content patches 1.2-1.12; five damage slots; server-specific fields |
| cMangos Classic | 128 | Five damage slots; Classic-specific `ExtraFlags`; no TBC socket fields |
| cMangos TBC | 141 | Five damage slots; `unk0`; socket/gem/totem fields; TBC `ExtraFlags` |
| AzerothCore Wrath | 138 | Two damage slots; Wrath scaling, item-limit, holiday, custom, and verified-build fields |

Most identity, requirement, stat, resistance, spell, socket, durability, set, and economy columns can be compared by name. The tool deliberately flags fields that need a policy rather than guessing:

- cMangos `ExtraFlags` is not assumed to equal AzerothCore `FlagsExtra`;
- TBC `unk0` is not mapped until its source-code meaning is confirmed;
- Classic/TBC damage slots three through five have no direct AzerothCore columns;
- Wrath scaling, item-limit, holiday, custom, and build fields need explicit preservation/reset rules.

## Comparison tool

`tools/item_progression/compare_item_templates.py` reads plain or gzip-compressed MySQL dumps directly and produces JSON containing:

- exact schema inventories;
- common, missing, identical, and changed item counts;
- difference counts per compatible field;
- bounded item-level difference samples;
- fields requiring manual mapping decisions.

When `--vmangos` is supplied, it also materializes the newest item row at or before each vMaNGOS content patch, reports introduction/revision counts, and compares the resulting 1.12 snapshot with cMangos Classic and AzerothCore Wrath.

Example:

```bash
python3 tools/item_progression/compare_item_templates.py \
  --classic /path/to/ClassicDB.sql.gz \
  --tbc /path/to/TBCDB.sql.gz \
  --wrath /path/to/azerothcore/item_template.sql \
  --vmangos /path/to/vmangos/mangos.sql \
  --output build/item-comparison.json
```

The JSON report is analysis output and should not be loaded into the world database.

### Patch transition candidates

`tools/item_progression/build_patch_transition.py` turns one vMaNGOS patch boundary into a review manifest. For every item row authored at that patch it records the previous Vanilla value, the new Vanilla value, the current AzerothCore Wrath value, and one of three mapping policies:

- `direct-candidate` — the field has a same-name AzerothCore destination, but still requires historical review;
- `review` — the schemas have a known semantic mismatch;
- `unmapped` — AzerothCore has no same-name destination.

Example for patch 1.12:

```bash
python3 tools/item_progression/build_patch_transition.py \
  --vmangos /path/to/vmangos/mangos.sql \
  --wrath /path/to/azerothcore/item_template.sql \
  --patch 10 \
  --output build/item-transition-1.12.json
```

This remains candidate evidence rather than executable SQL. Reviewed entries will be promoted into owned patch manifests before SQL generation.

The first 1.12 run contains 200 item transitions: 39 introductions and 161 revisions. Its field decisions comprise 5,187 direct candidates, 390 review-required values, and 78 unavailable mappings. The unavailable fields are `wrapped_gift` and `other_team_entry`; neither is mapped onto an unrelated AzerothCore field. Counts include the complete state of newly introduced items, including default-valued columns.

### Initial full comparison

The first complete run produced:

| Comparison | Left rows | Right rows | Common items | Identical common items | Changed common items | Only left | Only right |
|---|---:|---:|---:|---:|---:|---:|---:|
| Classic 1.12.1 vs AzerothCore Wrath | 17,718 | 46,096 | 17,713 | 811 | 16,902 | 5 | 28,383 |
| TBC vs AzerothCore Wrath | 30,396 | 46,096 | 30,396 | 18,231 | 12,165 | 0 | 15,700 |
| Classic 1.12.1 vs TBC | 17,718 | 30,396 | 17,713 | 581 | 17,132 | 5 | 12,683 |
| vMaNGOS 1.12 vs cMangos Classic 1.12.1 | 17,707 | 17,718 | 17,707 | 15,776 | 1,931 | 0 | 11 |
| vMaNGOS 1.12 vs AzerothCore Wrath | 17,707 | 46,096 | 17,707 | 1,264 | 16,443 | 0 | 28,389 |

These are raw project-to-project differences, not counts of confirmed Blizzard patch changes. High-volume differences include prices, flags, spell cooldown sentinel values, material, item level, required level, weapon damage/delay, armor, and binding. Project conventions and database fixes must be separated from historical changes before SQL is generated.

### vMaNGOS progressive inventory

vMaNGOS maps patch values `0..10` to Vanilla `1.2..1.12`. Its current database contains 20,034 `item_template` rows representing 17,707 distinct items; 2,327 rows are later historical versions of an existing entry.

| Vanilla patch | Rows authored at patch | New items | Revised existing items | Materialized items |
|:---:|---:|---:|---:|---:|
| 1.2 | 13,215 | 13,215 | 0 | 13,215 |
| 1.3 | 588 | 360 | 228 | 13,575 |
| 1.4 | 728 | 623 | 105 | 14,198 |
| 1.5 | 417 | 240 | 177 | 14,438 |
| 1.6 | 566 | 373 | 193 | 14,811 |
| 1.7 | 739 | 651 | 88 | 15,462 |
| 1.8 | 479 | 383 | 96 | 15,845 |
| 1.9 | 1,187 | 897 | 290 | 16,742 |
| 1.10 | 810 | 300 | 510 | 17,042 |
| 1.11 | 1,105 | 626 | 479 | 17,668 |
| 1.12 | 200 | 39 | 161 | 17,707 |

These counts describe vMaNGOS data modeling, not yet-verified Blizzard changes. Every transition still requires corroboration and AzerothCore field conversion.

### Existing Vanilla SQL coverage audit

`tools/item_progression/audit_vanilla_item_coverage.py` compares the item IDs touched by the inherited Vanilla patch SQL with vMaNGOS introduction and revision rows:

```bash
python3 tools/item_progression/audit_vanilla_item_coverage.py \
  --vmangos /path/to/vmangos/mangos.sql \
  --repository . \
  --output build/vanilla-item-coverage.json
```

| Patch | vMaNGOS new-item candidates | vMaNGOS revision candidates | Existing SQL item IDs | ID overlap | Uncovered revision candidates |
|:---:|---:|---:|---:|---:|---:|
| 1.2 | 13,215 | 0 | 0 | 0 | 0 |
| 1.3 | 360 | 228 | 14 | 14 | 214 |
| 1.4 | 623 | 105 | 30 | 30 | 75 |
| 1.5 | 240 | 177 | 139 | 139 | 38 |
| 1.6 | 373 | 193 | 6 | 6 | 187 |
| 1.7 | 651 | 88 | 12 | 12 | 76 |
| 1.8 | 383 | 96 | 5 | 5 | 91 |
| 1.9 | 897 | 290 | 79 | 79 | 211 |
| 1.10 | 300 | 510 | 134 | 134 | 376 |
| 1.11 | 626 | 479 | 46 | 46 | 433 |
| 1.12 | 39 | 161 | 0 | 0 | 161 |

Across 1.3-1.12, the inherited SQL touches 465 of 2,327 vMaNGOS revision candidates, leaving 1,862 candidate revisions to classify. Every inherited item ID overlaps a vMaNGOS revision at the same patch. That is a useful provenance signal, but it does not prove that either project's field values are correct.

Patch 1.2 is a special case: it is vMaNGOS's base item state rather than a delta from 1.1, so the zero revision count cannot be interpreted as “no items changed in 1.2.” Launch-to-1.2 differences require an independently reconstructed 1.1 snapshot.

## Conversion stages

1. **Extract:** parse source schemas and rows without importing foreign database structures.
2. **Normalize:** convert safe shared columns into a canonical item record.
3. **Classify:** mark each difference as era state, patch change, project-specific fix, server-only metadata, or client-dependent data.
4. **Corroborate:** check patch notes, DBC/client data, and versioned emulator history.
5. **Bundle:** connect the item state to loot, vendors, quests, recipes, and other acquisition paths.
6. **Materialize:** generate the expected AzerothCore state for one historical patch.
7. **Validate:** diff the generated state against a clean target database and test forward/backward transitions.

## Important limitations

- vMaNGOS has no 1.1 content-patch state. Its index begins at 1.2, so launch must still be reconstructed independently.
- The project goal is 1.2-1.12, but the current README lists supported executable client builds from 1.5.1 onward. Database patch rows for 1.2-1.4 are valuable candidate evidence, not proof of complete early-client emulation.
- cMangos Classic is a final 1.12.1 snapshot and cannot independently date changes inside Vanilla.
- The same per-patch reconstruction problem remains for the TBC cycle until a comparably versioned source is added.
- Item templates are only one part of availability. vMaNGOS also has patch-aware loot, vendors, quests, spawns, gameobjects, conditions, and core behavior; those dependencies must be extracted as atomic bundles.
