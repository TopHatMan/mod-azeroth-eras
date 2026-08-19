-- Maraudon outdoor quest NPCs (hidden in 1.1). Interior bosses stay in the
-- instance; map 349 is the gate for those.
UPDATE `creature` SET `phaseMask` = 1 WHERE `id1` IN (12239, 12240, 12241, 12242, 12243, 13656, 13697, 13718);
