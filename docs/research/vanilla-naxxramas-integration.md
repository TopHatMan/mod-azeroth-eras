# Vanilla Naxxramas integration contract

- Runtime owner: [`sogladev/mod-vanilla-naxxramas`](https://github.com/sogladev/mod-vanilla-naxxramas)
- Audited revision: `5e6f54fd776e07a76ef3a4f81fc5a57c76badd30`
- Audit date: 2026-08-15
- Azeroth Eras patch: 1.11 (`PATCH_SHADOW_OF_THE_NECROPOLIS`)

## Ownership boundary

`mod-vanilla-naxxramas` is the server's Naxxramas 40 encounter implementation. Azeroth Eras must not import or register a second copy of Individual Progression's Naxxramas scripts or SQL.

Azeroth Eras owns only the historical policy around that implementation:

```text
Naxxramas 40 access = patch >= 1.11
                    && effective level cap >= 60
                    && mod-vanilla-naxxramas entrance/attunement policy
```

The Scourge Invasion and Naxxramas are both patch-1.11 bundles, but neither may be activated as an accidental side effect of the other. The invasion controller owns event lifecycle; the Naxxramas module owns the raid encounter.

Individual Progression remains a candidate source for character/account encounter state and Playerbots synchronization only. It is not the Naxxramas 40 runtime owner.

## Upstream operating assumptions

The audited upstream revision documents these requirements:

| Concern | Upstream behavior | Azeroth Eras responsibility |
|---|---|---|
| Map and difficulty | Reuses map 533 and places Naxxramas 40 on 10-player heroic | Keep the 1.11 route distinct from Wrath Naxxramas 10/25 and test both transitions |
| Expansion | Requires `Expansion = 2` and Wrath-enabled accounts | Report this as an installation prerequisite; do not lower the realm expansion setting for Vanilla |
| Client data | Requires a `MapDifficulty.dbc` client patch to avoid login crashes in the instance | Treat the matching client package as required compatibility data and validate its version |
| Attunement | Own configuration and SQL control Argent Dawn reputation, attunement, and the Stratholme-first entrance | Defer to the module; do not add a competing Azeroth Eras attunement switch |
| Progression disables | Upstream provides optional SQL to remove map disables used by progression modules | Replace manual SQL with an explicit, reversible integration step once dependency detection is implemented |
| Encounter scripts | Shares the core map and some scripts with Wrath Naxxramas | Add compile/runtime collision checks against the pinned AzerothCore revision |
| Custom IDs | Uses custom creature, gameobject, and spell ranges documented in upstream issue 32 | Reserve and collision-check those ranges before other 1.11 content is materialized |

## Current integration status

The level-60 runtime gate already recognizes map 533, but the patch-1.11 SQL does not currently remove the map disable. This is intentional until Azeroth Eras can verify that the Naxxramas 40 dependency and compatible client data are installed; blindly opening map 533 would expose Wrath content on installations without the module.

For current test servers, follow the upstream installation instructions and its reversible `optional/RemoveDisables` compatibility step on a database clone. Do not import the Individual Progression Naxxramas bundle alongside it.

## Required implementation slices

1. Add a configured dependency handshake that identifies the installed Naxxramas module revision and client-data package.
2. Make patch 1.11 reconcile the map-533 disable only when that handshake succeeds.
3. Route level-60 players to the module's 10-player heroic Naxxramas 40 difficulty.
4. At Wrath patch 3.0, expose the normal Wrath difficulties without destroying the Vanilla route or its saved lockouts.
5. Preserve the module's attunement and optional Stratholme-first entrance policy.
6. Add upgrade checks for custom-ID collisions, shared-script collisions, and AzerothCore schema changes.
7. Add rollback that restores the pre-integration `disables`, map-difficulty, and module-owned database state.

## Acceptance tests

- Patch 1.10 cannot enter Naxxramas 40, even at level 60.
- Patch 1.11 plus a level-60 cap can enter the module's Naxxramas 40 route after satisfying its configured attunement policy.
- A level cap below 60 cannot enter the Vanilla route.
- Missing/incompatible module or client data fails closed with an actionable diagnostic.
- Installing Individual Progression scope support does not register duplicate Naxxramas scripts or apply duplicate Naxxramas SQL.
- Advancing to Wrath exposes Naxxramas 80 while the two versions retain unambiguous difficulty routing and lockouts.
- Rolling back below 1.11 restores the prior database disable state without deleting unrelated map-533 or Wrath data.

