import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "item_progression"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "build_patch_transition.py"
SPEC = importlib.util.spec_from_file_location("build_patch_transition", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ItemPatchTransitionTests(unittest.TestCase):
    def test_classifies_direct_review_and_unmapped_fields(self):
        vmangos_sql = textwrap.dedent("""\
            CREATE TABLE `item_template` (
              `entry` int,
              `patch` int,
              `name` text,
              `armor` int,
              `extra_flags` int,
              `legacy_only` int
            );
            INSERT INTO `item_template` VALUES
            (1,0,'Original',10,0,7),
            (1,1,'Revised',12,4,8),
            (2,1,'Introduced',20,0,9);
        """)
        wrath_sql = textwrap.dedent("""\
            CREATE TABLE `item_template` (
              `entry` int,
              `name` text,
              `armor` int,
              `FlagsExtra` int
            );
            INSERT INTO `item_template` VALUES
            (1,'Wrath name',30,0),(2,'Wrath introduced',40,0);
        """)
        with tempfile.TemporaryDirectory() as directory:
            vmangos = Path(directory) / "vmangos.sql"
            wrath = Path(directory) / "wrath.sql"
            vmangos.write_text(vmangos_sql, encoding="utf-8")
            wrath.write_text(wrath_sql, encoding="utf-8")
            report = MODULE.build_transition(vmangos, wrath, 1)

        self.assertEqual(report["candidate_count"], 2)
        self.assertEqual(report["introduced_count"], 1)
        self.assertEqual(report["revised_count"], 1)
        first = report["candidates"][0]
        changes = {change["source_column"]: change for change in first["changes"]}
        self.assertEqual(changes["armor"]["policy"], "direct-candidate")
        self.assertEqual(changes["armor"]["azerothcore_current"], 30)
        self.assertEqual(changes["extra_flags"]["policy"], "review")
        self.assertEqual(changes["legacy_only"]["policy"], "unmapped")

    def test_rejects_patch_outside_vmangos_range(self):
        with self.assertRaisesRegex(ValueError, "between 0 .* and 10"):
            MODULE.build_transition(Path("missing"), Path("missing"), 11)


if __name__ == "__main__":
    unittest.main()
