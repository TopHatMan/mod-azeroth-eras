-- Patch 1.11 introduced both the Midsummer Fire Festival (event 1) and the
-- original Scourge Invasion (event 17). Keep the IDs explicit: event 1 is not
-- the invasion controller.
DELETE FROM `disables` WHERE `sourceType` = 9 AND `entry` IN (1, 17);
