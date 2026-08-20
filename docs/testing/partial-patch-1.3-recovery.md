# Recovering a partially applied patch 1.3 test

The old SQL used AzerothCore's removed `creature.id1`, `id2`, and `id3`
columns. A MySQL import could therefore apply the quest/gameobject statements
while failing the creature statement that reveals Lothos Riftwaker. The result
looks contradictory: the Core Fragment is visible, but Lothos is not.

## Diagnose first

Run these read-only queries against the exact Ashbringer world database:

```sql
SELECT `guid`, `id`, `phaseMask`
FROM `creature`
WHERE `id` = 14387;

SELECT `sourceType`, `entry`, `comment`
FROM `disables`
WHERE (`sourceType` = 1 AND `entry` IN (7487, 7848))
   OR (`sourceType` = 2 AND `entry` = 409);

SELECT `guid`, `id`, `map`, `phaseMask`, `position_x`, `position_y`, `position_z`
FROM `gameobject`
WHERE `id` = 179553;
```

For patch ID `2` / Vanilla 1.3, the expected state is:

- Lothos `14387` has `phaseMask = 1`;
- quest disables `7487` and `7848` do not exist;
- map disable `409` does not exist;
- Core Fragment `179553` is on map `409` with `phaseMask = 1`.

## Character quest safety

Azeroth Eras patch SQL contains no writes to `character_queststatus` or its
rewarded/daily/weekly/monthly companion tables. It changes world availability
through the world `disables` table. Before repairing anything, inspect the
character database to distinguish a hidden/unavailable quest from deleted
quest progress:

```sql
SELECT *
FROM `character_queststatus`
WHERE `guid` = YOUR_CHARACTER_GUID
  AND `quest` IN (7487, 7848);
```

Use the actual Ashbringer character database for that query, not the world
database. Do not invent or reinsert character quest rows without a verified
pre-test snapshot.

## Recovery rule

Take a verified MySQL snapshot first. If the failed test began from a disposable
database, the safest recovery is to restore that baseline and let the corrected
SQL run once in chronological order. Do not use `Progression.Reset` on the live
realm and do not delete updater history blindly: other patch statements may
already have committed successfully.
