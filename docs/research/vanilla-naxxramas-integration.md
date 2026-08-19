# Vanilla Naxxramas integration contract

- Runtime owner: [`sogladev/mod-vanilla-naxxramas`](https://github.com/sogladev/mod-vanilla-naxxramas)
- Reference upstream audited: 2026-08-15
- Deployment profile: locally patched Ashbringer implementation
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

## Ashbringer operating contract

The public upstream repository is provenance and issue-history reference material, not a statement of this server's prerequisites. Nick's Ashbringer copy has already been patched to remove the stock `Expansion = 2` and external client-patch requirements. Azeroth Eras must target the installed Ashbringer implementation and must not reintroduce those upstream restrictions.

| Concern | Ashbringer behavior | Azeroth Eras responsibility |
|---|---|---|
| Map and difficulty | Naxxramas 40 is supplied by the patched Vanilla Naxxramas module on map 533 | Keep the 1.11 route distinct from Wrath Naxxramas 10/25 and test both transitions |
| Expansion | No `Expansion = 2` prerequisite | Do not add an expansion-setting or account-expansion gate |
| Client data | No separately installed client patch is required by this deployment | Do not block Naxxramas 40 on an external client-package check |
| Attunement | The installed module owns Argent Dawn reputation, attunement, and entrance behavior | Defer to the module; do not add a competing Azeroth Eras attunement switch |
| Progression disables | Azeroth Eras and the installed module must agree on map-533 availability | Replace ad-hoc SQL with one explicit, reversible integration step |
| Encounter scripts | The patched Ashbringer implementation owns the Naxxramas 40 encounter | Detect duplicate script registration and keep Individual Progression's copy disabled |
| Custom IDs | Preserve the IDs used by the installed Ashbringer implementation | Inventory and collision-check the actual installed fork before materializing other 1.11 content |

## Current integration status

The level-60 runtime gate and the patch-1.11 disable file both treat map 533 as a 1.11 unlock. This deployment uses `mod-vanilla-naxxramas` for the 40-player encounter. Do not import the Individual Progression Naxxramas bundle alongside it.

## Required implementation slices

1. Add a configured dependency handshake that identifies the installed patched Ashbringer Naxxramas module.
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
- A missing or incompatible Ashbringer Naxxramas module fails closed with an actionable diagnostic.
- Installing Individual Progression scope support does not register duplicate Naxxramas scripts or apply duplicate Naxxramas SQL.
- Advancing to Wrath exposes Naxxramas 80 while the two versions retain unambiguous difficulty routing and lockouts.
- Rolling back below 1.11 restores the prior database disable state without deleting unrelated map-533 or Wrath data.

