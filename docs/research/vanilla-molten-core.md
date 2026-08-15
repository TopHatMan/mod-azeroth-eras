# Vanilla Molten Core progression notes

This file records the evidence used by the first authoritative Molten Core bundle. It separates historical claims from AzerothCore implementation choices.

## Historical timeline

- Patch 1.1-1.2: Molten Core was already open and was reached through Blackrock Depths. Patch 1.2 notes specifically discuss corpse retrieval at the BRD instance line.
- Patch 1.3: Blizzard's notes state that players who completed the Molten Core discovery quest could port directly to the raid, bypassing Blackrock Depths.
- Patch 1.4: the discovery quest objective moved from inside Molten Core to Blackrock Depths. This is the boundary used for the Core Fragment relocation.

Sources:

- [Warcraft Wiki: Patch 1.3.0](https://warcraft.wiki.gg/wiki/Patch_1.3.0)
- [Warcraft Wiki: Core Fragment](https://warcraft.wiki.gg/wiki/Core_Fragment)
- [Blizzard forum archive quoting the original Molten Core patch-note sequence](https://us.forums.blizzard.com/en/wow/t/molten-core-changes/285565)

## AzerothCore mapping

The current AzerothCore 3.3.5 database provides:

- physical BRD-to-MC area trigger `2886`;
- Blackrock Mountain window/lava shortcuts `3528` and `3529`;
- Lothos Riftwaker creature `14387`;
- Alliance/Horde quest variants `7487` and `7848`;
- Core Fragment gameobject `179553`, canonical GUID `43133`;
- the final BRD-side Fragment spawn at map `230`, `(1128.01, -471.763, -104.032)`.

The 3.3.5 core does not attunement-gate shortcut triggers 3528/3529. Unified Progression supplies that runtime rule. For patch 1.3, the canonical Fragment spawn is temporarily moved to map 409 at the raid entry coordinates because the 3.3.5 database preserves only the later BRD-side spawn. Patch 1.4 restores the canonical row exactly.

The exact 1.3 object transform is therefore a documented server-side approximation. The historical map boundary is sourced; the surviving 3.3.5 data does not preserve the original pre-1.4 transform.
