import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "item_progression"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "audit_vanilla_item_coverage.py"
SPEC = importlib.util.spec_from_file_location("audit_vanilla_item_coverage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VanillaItemCoverageTests(unittest.TestCase):
    def test_extracts_equal_and_in_item_ids(self):
        sql = """
        UPDATE `item_template` SET `armor`=1 WHERE `entry` = 10;
        UPDATE item_template SET Quality=2 WHERE entry IN (20, 21, 22);
        UPDATE creature_template SET entry=99 WHERE entry=88;
        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "items.sql"
            path.write_text(sql, encoding="utf-8")
            entries = MODULE.touched_item_entries(path)
        self.assertEqual(entries, {10, 20, 21, 22})

    def test_classifies_progressive_introductions_and_revisions(self):
        sql = textwrap.dedent("""\
        CREATE TABLE `item_template` (
          `entry` int,
          `patch` int,
          `name` text
        );
        INSERT INTO `item_template` VALUES
        (1,0,'First'),(2,0,'Second'),(1,1,'First revised'),(3,1,'Third');
        """)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vmangos.sql"
            path.write_text(sql, encoding="utf-8")
            columns = MODULE.read_columns(path)
            transitions = MODULE.vmangos_transitions(path, columns)
        self.assertEqual(transitions[0]["introduced"], {1, 2})
        self.assertEqual(transitions[0]["revised"], set())
        self.assertEqual(transitions[1]["introduced"], {3})
        self.assertEqual(transitions[1]["revised"], {1})


if __name__ == "__main__":
    unittest.main()
