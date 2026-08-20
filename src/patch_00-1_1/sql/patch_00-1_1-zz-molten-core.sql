-- Unified Progression bundle: Molten Core launch state (patches 1.1-1.2).
--
-- Molten Core itself and the physical BRD entrance (area trigger 2886) existed
-- at launch. Lothos, the attunement quests, Core Fragment, and the two
-- Blackrock Mountain shortcut triggers were introduced in patch 1.3.

-- Normalize stale state left by an older progression module: map 409 is open.
DELETE FROM `disables` WHERE `sourceType` = 2 AND `entry` = 409;

-- The two faction variants of Attunement to the Core must not be obtainable.
DELETE FROM `disables` WHERE `sourceType` = 1 AND `entry` IN (7487, 7848);
INSERT INTO `disables` (`sourceType`, `entry`, `flags`, `params_0`, `params_1`, `comment`) VALUES
(1, 7487, 0, '', '', 'Attunement to the Core (Alliance) - patch 1.3'),
(1, 7848, 0, '', '', 'Attunement to the Core (Horde) - patch 1.3');

UPDATE `creature` SET `phaseMask` = 16384 WHERE `id` = 14387; -- Lothos Riftwaker
UPDATE `gameobject` SET `phaseMask` = 16384 WHERE `id` = 179553; -- Core Fragment

-- Keep the physical BRD portal untouched. These are only the post-attunement
-- window and lava shortcuts; their runtime script also verifies quest reward.
DELETE FROM `areatrigger_scripts` WHERE `entry` IN (3528, 3529);
INSERT INTO `areatrigger_scripts` (`entry`, `ScriptName`) VALUES
(3528, 'at_progression_molten_core_shortcut'),
(3529, 'at_progression_molten_core_shortcut');
