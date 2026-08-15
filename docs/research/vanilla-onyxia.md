# Vanilla Onyxia progression notes

This file records the evidence and implementation boundary for the first launch-era Onyxia attunement correction.

## Horde chain identity

Onyxia's Lair and its faction-specific Drakefire Amulet chains were launch content. The Horde chain used Rexxar as the Champion of the Horde. The 3.3.5 database instead names creature entry `10182` Rokaro and rewrites quests `6567`, `6568`, `6601`, and `6602` around him because Rexxar later left Azeroth for Outland.

For Vanilla patches, Unified Progression restores:

- Rexxar on entry `10182`, model `11660`;
- Misha on entry `10204`;
- Rexxar's full 348-point Desolace patrol and companion formation;
- Rexxar-era English quest and item text;
- localized Rexxar and Rexxar's Testament names preserved by the historical dataset;
- Emberstrife (`10321`) as the downstream quest NPC.

Rokaro must not be treated as a launch NPC merely because the 3.3.5 database uses the same creature entry for him.

## Evidence

- [WoW Classic Onyxia attunement guide](https://www.wowhead.com/classic/guide/onyxia-onyxias-lair-attunement-drakefire-amulet-wow-classic) documents the original Horde chain through Rexxar and Emberstrife.
- [Warcraft Wiki's evolution guide](https://warcraft.wiki.gg/wiki/World_of_Warcraft_evolution_guide) records that Rokaro replaced Rexxar when Rexxar left for Outland.
- `Grimfeather/mod-individual-progression` preserves the Vanilla Rexxar template, quest text, model, Misha formation, and 348-point patrol used by this bundle.
- The classic database snapshot identifies entry `10182` as Rexxar and corroborates his model and combat spell set.

The historical databases are implementation evidence rather than infallible patch notes. The regression suite therefore checks the bundle's internal consistency separately from this research record.
