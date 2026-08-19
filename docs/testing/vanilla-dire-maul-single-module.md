# Single-module Vanilla Dire Maul test

This profile replaces `mod-progression-system` and
`mod-individual-progression` with `mod-azeroth-eras` for a server-wide Vanilla
test. It does not replace the separate `mod-vanilla-naxxramas` runtime used for
Naxxramas 40.

## Patch identity

Do not confuse the configured patch ID with Blizzard's patch number:

| `Progression.Patch` | Historical patch | Headline unlock |
|---:|:---:|---|
| `0` | 1.0 / launch client 1.1.0 | Launch world, MC, Onyxia |
| `1` | 1.2 | Maraudon |
| `2` | 1.3 | Dire Maul and MC attunement |

Dire Maul testing therefore uses patch ID `2`, not `1`.

## 1. Stop and back up

Stop `worldserver` before changing modules or applying patch SQL. Take a full
MySQL snapshot of the actual world database. For the Ashbringer naming scheme,
replace the suffix below with the real world database name:

```bash
./tools/database/azerothcore_db.sh backup \
  --database azcore_ashbringer_world \
  --output-dir /path/to/verified/snapshots \
  --defaults-extra-file /path/to/mysql-client.cnf
```

Use the exact `azcore_ashbringer_nameofdb` world-database name from your
`worldserver.conf`; `azcore_ashbringer_world` above is only an example. The
permission-restricted MySQL option file supplies the host, port, user, and
password without exposing the password on the command line. The tool creates a
compressed dump and writes checksum and metadata sidecars. Do not use
`Progression.Reset` as a backup or rollback mechanism.

## 2. Replace the overlapping modules

Remove these two module directories from the AzerothCore source tree and make a
clean build so none of their scripts remain linked:

- `mod-progression-system`
- `mod-individual-progression`

Keep only `mod-azeroth-eras` as the progression owner. Remove their generated
configuration files from the runtime config directory as well. Azeroth Eras
logs an error during startup if it sees either legacy module enabled.

If another module modifies player damage or healing, set the Azeroth Eras
multipliers to `1.0` so only one module owns combat tuning.

## 3. Test configuration

For a level-60 Vanilla realm at the Dire Maul step:

```ini
Progression.LevelGating.Enabled = 1
Progression.LevelCap = 60
Progression.Patch = 2
Progression.Reset = 0
Progression.Development.AllowUnsafeReset = 0
```

At level 60 the Vanilla Chromie dungeon ladder is complete. Patch gates still
apply, so this setting does not open BWL, ZG, AQ, or Naxxramas early.

## 4. Prove the boundary before advancing

On a disposable copy of the backed-up world database, start first with patch
ID `1`:

- Maraudon is available.
- Dire Maul is rejected by the runtime map gate.
- Lothos Riftwaker and the MC attunement bundle remain unavailable.

Stop the server, change only `Progression.Patch` to `2`, and restart:

- Dire Maul is available.
- Lothos Riftwaker is visible.
- both faction variants of Attunement to the Core are available;
- the Core Fragment is inside Molten Core for the 1.3 state;
- Azuregos and Lord Kazzak are visible;
- BWL remains unavailable until patch ID `5`.

Use `.progression info` after each start to verify the effective patch, level
cap, era cap, and reset safety state.

## 5. Rollback rule

Patch SQL is currently forward-only. Do not point a progressed production world
database back at a lower patch ID and expect SQL state to reverse. Restore the
verified MySQL snapshot when the test must be undone.
