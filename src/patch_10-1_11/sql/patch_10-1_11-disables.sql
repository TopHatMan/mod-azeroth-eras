-- Patch 1.11 introduced both the Midsummer Fire Festival (event 1) and the
-- original Scourge Invasion (event 17). Keep the IDs explicit: event 1 is not
-- the invasion controller.
DELETE FROM `disables` WHERE `sourceType` = 9 AND `entry` IN (1, 17);
-- Naxxramas 40. This deployment uses mod-vanilla-naxxramas on map 533.
-- Wrath 10/25 difficulties stay a 3.0 concern for that module.
DELETE FROM `disables` WHERE `sourceType` = 2 AND `entry` = 533;
