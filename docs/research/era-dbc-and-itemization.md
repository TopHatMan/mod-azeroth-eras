# Era DBC and itemization (no talent work)

- Status: product decision, 2026-08-17
- Ready target still: Vanilla 1.1–1.6
- Explicit non-goal: historical talent trees

## Decisions

1. **Talents stay 3.3.5.** Do not rebuild talent DBC or talent UI per era.
2. **Itemization is in scope.** Stats, armor, DPS, reqs, sockets, loot, vendors live in `item_template` and related world tables.
3. **ARAC (all races / all classes) is permanent.** It is not swapped when the realm moves Vanilla → TBC → Wrath.
4. **Era DBC is an overlay**, not a second client. The playable client stays 3.3.5a + ARAC. Vanilla / TBC / Wrath data is selected on the **server**, then optionally shipped as a small client pack for tooltip-only leftovers.

## What the 3.3.5 client actually uses

| Data | Authority | Era-swap? |
|---|---|---|
| Item stats, armor, damage, sockets | `item_template` (server sends query) | Yes, SQL |
| Item class / subclass / display / sheath | `Item.dbc`, unless `DBC.EnforceItemAttributes = 0` | Overlay `item_dbc` or turn enforcement off |
| Set-bonus **text** | client `ItemSet.dbc` | Client pack later |
| Profession reagent **window** | client `Spell.dbc` | Client pack later |
| Combat spell effects | server `Spell.dbc` + `spell_dbc` table | Server overlay |
| Talents | client + server talent DBC | **Never** |
| ARAC race/class combos | your modified DBC + create-info SQL | Always on |

AzerothCore already loads every major DBC file, then **overlays** same-ID rows from world tables (`item_dbc`, `spell_dbc`, `itemdisplayinfo_dbc`, `itemset_dbc`, `charstartoutfit_dbc`, `chrraces_dbc`, …). That is the safe hook. No new primary keys on live `item_template`.

## Layers (keep them separate)

```
3.3.5a client
  + ARAC DBC          always (race/class, start outfits)
  + optional era pack later (ItemSet / Spell tooltip leftovers)

worldserver dbc/      3.3.5 extract (may include ARAC files you already use)

world DB
  item_template       era snapshots from the module (1.1-1.6 first)
  item_dbc            only when class/display must change
  spell_dbc           only when a server spell must change
  ARAC create-info    never tied to Progression.Patch
```

## Safer than a “heavy” core fork

| Approach | Core change | Use |
|---|---|---|
| `item_template` snapshots per patch | None | 90% of itemization |
| `DBC.EnforceItemAttributes = 0` from this module | None | Stop DBC from overwriting display/class |
| Fill `item_dbc` / `spell_dbc` for the active patch | None | Server DBC overlay AC already supports |
| `DataDir/dbc/<era>/` selected at boot | ~10 lines in `LoadDBCStores` | Only if file-based packs are easier than SQL |
| Per-player live DBC swap / talent rebuild | Huge | Do not do this |

File-based `dbc/vanilla` vs `dbc/tbc` vs `dbc/wotlk` is optional later. Do **not** put ARAC files in those era folders or a 1.1 boot will lose all-races-all-classes.

## Recommended order

1. Keep 1.1–1.6 **gates** as the playable target (already the ready target).
2. Turn off DBC item-attribute enforcement in this module while a Vanilla patch is selected.
3. Build `item_template` snapshots for 1.1–1.6 (vMaNGOS → AC fields). That is itemization.
4. Only then generate `item_dbc` rows for items whose **display or class** actually changed.
5. Keep your current ARAC DBC on both client and server as a third, always-on layer.
6. A “dynamic” player pack (launcher copies `Patch-Z.MPQ` for Vanilla vs TBC vs Wrath) is optional and only for tooltip/set/profession UI.

## ARAC vs era

ARAC answers “who can be what.” Era DBC answers “what that Thunderfury looks like this patch.” Mixing them in one MPQ is how you lose one or the other on a patch bump. Keep two stacks.
