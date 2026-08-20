-- Unified Progression bundle: patch 1.3 Molten Core discovery/attunement.
-- Lothos, both faction quest variants, and the attuned shortcuts unlock
-- together. In 1.3 the Core Fragment was still inside Molten Core.

DELETE FROM `disables` WHERE `sourceType` = 1 AND `entry` IN (7487, 7848);
DELETE FROM `disables` WHERE `sourceType` = 2 AND `entry` = 409;

UPDATE `creature` SET `phaseMask` = 1 WHERE `id` = 14387; -- Lothos Riftwaker

-- Reuse AzerothCore's canonical Core Fragment spawn (GUID 43133) and move it
-- just inside the raid entrance for the short-lived 1.3 layout.
UPDATE `gameobject`
SET `map` = 409,
    `phaseMask` = 1,
    `position_x` = 1091.89,
    `position_y` = -466.985,
    `position_z` = -105.084,
    `orientation` = 3.14159,
    `rotation0` = 0,
    `rotation1` = 0,
    `rotation2` = 1,
    `rotation3` = 0
WHERE `id` = 179553;
