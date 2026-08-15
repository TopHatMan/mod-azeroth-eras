-- Unified Progression bundle: patch 1.4 Core Fragment relocation.
-- Patch 1.4 moved the objective from inside Molten Core to the BRD side of the
-- Molten Core portal. Restore AzerothCore's canonical 3.3.5 spawn exactly.

UPDATE `gameobject`
SET `map` = 230,
    `phaseMask` = 1,
    `position_x` = 1128.01,
    `position_y` = -471.763,
    `position_z` = -104.032,
    `orientation` = 3.01942,
    `rotation0` = 0,
    `rotation1` = 0,
    `rotation2` = 0.998135,
    `rotation3` = 0.0610484
WHERE `id` = 179553;
