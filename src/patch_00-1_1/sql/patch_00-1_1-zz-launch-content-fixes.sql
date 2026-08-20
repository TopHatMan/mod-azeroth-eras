-- Patch 1.1 launch-content corrections.
-- Onyxia's Lair was available at launch, so Emberstrife must not remain in the
-- module's hidden-content phase. Rexxar is restored as a complete bundle in
-- patch_00-1_1-zz-onyxia-horde.sql; restoring the 3.3.5 Rokaro spawn here was
-- historically incorrect.
--
-- Lothos Riftwaker is intentionally NOT restored here: Lothos and the Molten Core
-- discovery/shortcut attunement were added in patch 1.3, where the existing 1.3
-- creature/gameobject layers restore Lothos (14387) and Core Fragment (179553).
UPDATE `creature` SET `phaseMask` = 1 WHERE `id` = 10321; -- Emberstrife
