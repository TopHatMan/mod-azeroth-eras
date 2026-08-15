# Database snapshot and restore safety

Patch emulation changes thousands of world-database values. A cumulative SQL replay is not a rollback: it cannot reliably reconstruct values that an earlier patch overwrote or deleted. Take verified snapshots before installing the module, changing patch, regenerating historical item data, or testing reconciliation.

`tools/database/azerothcore_db.sh` creates compressed MySQL/MariaDB snapshots with SHA-256 checksums and metadata. Restore requires an exact target-database confirmation, validates the checksum, and takes a new rescue snapshot of the current database before importing anything.

## Credentials

Do not put a password in a command or repository file. Use a permission-restricted MySQL option file outside the repository:

```ini
[client]
host=127.0.0.1
port=3306
user=acore
password=replace-with-the-real-password
```

On Linux, restrict it with `chmod 600 /secure/path/azerothcore-client.cnf`.

## Back up a realm

Use an output directory outside the repository and web root. Back up all three AzerothCore databases even though most patch data is in the world database:

```bash
tools/database/azerothcore_db.sh backup \
  --database acore_auth \
  --output-dir /srv/azerothcore-backups/before-vanilla \
  --defaults-extra-file /secure/path/azerothcore-client.cnf

tools/database/azerothcore_db.sh backup \
  --database acore_characters \
  --output-dir /srv/azerothcore-backups/before-vanilla \
  --defaults-extra-file /secure/path/azerothcore-client.cnf

tools/database/azerothcore_db.sh backup \
  --database acore_world \
  --output-dir /srv/azerothcore-backups/before-vanilla \
  --defaults-extra-file /secure/path/azerothcore-client.cnf
```

Each command produces `.sql.gz`, `.sql.gz.sha256`, and `.sql.gz.metadata` files. Copy the complete set to storage separate from the game server and test a restore against a disposable database before treating the backup as proven.

## Restore one database

Stop `worldserver` and any process that writes to the target database. The value passed to `--confirm-database` must exactly match `--database`:

```bash
tools/database/azerothcore_db.sh restore \
  --database acore_world \
  --snapshot /srv/azerothcore-backups/before-vanilla/acore_world-YYYYMMDDTHHMMSSZ.sql.gz \
  --confirm-database acore_world \
  --pre-restore-dir /srv/azerothcore-backups/pre-restore-rescue \
  --defaults-extra-file /secure/path/azerothcore-client.cnf
```

The rescue snapshot is mandatory. A checksum failure, snapshot/target metadata mismatch, or mismatched confirmation stops before any import. Snapshots include `DROP DATABASE`/`CREATE DATABASE` statements so the restore account needs those privileges and the restored schema does not retain tables that were absent from the snapshot. Restore auth, characters, and world snapshots from the same backup window when a consistent whole-realm rollback is required.

## What this does not solve

Snapshots provide disaster recovery; they do not make patch transitions deterministic. The planned progression reconciler still needs reviewed per-patch manifests, an owned-field baseline, drift detection, and forward/backward transition tests. Until that exists, never use `Progression.Reset` as a production rollback mechanism.
