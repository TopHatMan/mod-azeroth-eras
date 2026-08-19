-- Patch 1.2: Maraudon dungeon + its outdoor quests, Winter Veil, and the
-- first group-buff tomes (Prayer of Fortitude / Gift of the Wild / Arcane Brilliance).
DELETE FROM `disables` WHERE `sourceType` = 1 AND `entry` IN (7028, 7029, 7041, 7044, 7064, 7065, 7066, 7067, 7068, 7070);
DELETE FROM `disables` WHERE `sourceType` = 2 AND `entry` = 349;
DELETE FROM `disables` WHERE `sourceType` = 9 AND `entry` IN (2, 52);
DELETE FROM `disables` WHERE `sourceType` = 10 AND `entry` IN (17413, 17414, 17682, 17683, 18600);
