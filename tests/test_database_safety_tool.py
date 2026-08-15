import gzip
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "database" / "azerothcore_db.sh"


class DatabaseSafetyToolTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.log"
        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.bin}:{self.env['PATH']}"
        self.env["FAKE_DB_LOG"] = str(self.log)
        self._executable(
            "mysqldump",
            '#!/bin/sh\nprintf "mysqldump %s\\n" "$*" >> "$FAKE_DB_LOG"\nprintf "CREATE DATABASE test;\\n"\n',
        )
        self._executable(
            "mysql",
            '#!/bin/sh\nprintf "mysql %s\\n" "$*" >> "$FAKE_DB_LOG"\ncat >> "$FAKE_DB_LOG"\n',
        )

    def tearDown(self):
        self.temporary.cleanup()

    def _executable(self, name, body):
        path = self.bin / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def run_tool(self, *arguments):
        return subprocess.run(
            ["bash", str(SCRIPT), *arguments],
            env=self.env,
            text=True,
            capture_output=True,
        )

    def create_snapshot(self):
        backup_dir = self.root / "snapshots"
        result = self.run_tool(
            "backup", "--database", "acore_world", "--output-dir", str(backup_dir)
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(result.stdout.strip())

    def test_help_does_not_require_a_database(self):
        result = self.run_tool("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("backup --database", result.stdout)

    def test_backup_creates_compressed_snapshot_checksum_and_metadata(self):
        snapshot = self.create_snapshot()

        self.assertTrue(snapshot.is_file())
        self.assertTrue(Path(f"{snapshot}.sha256").is_file())
        metadata = Path(f"{snapshot}.metadata").read_text(encoding="utf-8")
        self.assertIn("format=azerothcore-db-snapshot-v1", metadata)
        self.assertIn("database=acore_world", metadata)
        with gzip.open(snapshot, "rt", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "CREATE DATABASE test;\n")
        self.assertIn("--single-transaction", self.log.read_text(encoding="utf-8"))
        self.assertIn("--add-drop-database", self.log.read_text(encoding="utf-8"))
        self.assertIn("--databases acore_world", self.log.read_text(encoding="utf-8"))

    def test_restore_refuses_mismatched_confirmation(self):
        snapshot = self.create_snapshot()
        result = self.run_tool(
            "restore",
            "--database", "acore_world",
            "--snapshot", str(snapshot),
            "--confirm-database", "acore_characters",
            "--pre-restore-dir", str(self.root / "rescue"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must exactly match", result.stderr)
        self.assertNotIn("mysql acore_world", self.log.read_text(encoding="utf-8"))

    def test_restore_refuses_modified_snapshot(self):
        snapshot = self.create_snapshot()
        with snapshot.open("ab") as handle:
            handle.write(b"tampered")
        result = self.run_tool(
            "restore",
            "--database", "acore_world",
            "--snapshot", str(snapshot),
            "--confirm-database", "acore_world",
            "--pre-restore-dir", str(self.root / "rescue"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum validation failed", result.stderr)
        self.assertFalse((self.root / "rescue").exists())

    def test_restore_refuses_snapshot_for_another_database(self):
        snapshot = self.create_snapshot()
        result = self.run_tool(
            "restore",
            "--database", "acore_auth",
            "--snapshot", str(snapshot),
            "--confirm-database", "acore_auth",
            "--pre-restore-dir", str(self.root / "rescue"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metadata is for database 'acore_world'", result.stderr)
        self.assertFalse((self.root / "rescue").exists())

    def test_restore_takes_rescue_snapshot_before_import(self):
        snapshot = self.create_snapshot()
        result = self.run_tool(
            "restore",
            "--database", "acore_world",
            "--snapshot", str(snapshot),
            "--confirm-database", "acore_world",
            "--pre-restore-dir", str(self.root / "rescue"),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.root / "rescue").glob("*.sql.gz"))), 1)
        log = self.log.read_text(encoding="utf-8")
        self.assertLess(log.rfind("mysqldump"), log.find("mysql acore_world"))


if __name__ == "__main__":
    unittest.main()
