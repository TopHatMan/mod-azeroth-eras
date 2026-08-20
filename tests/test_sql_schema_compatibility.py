import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class SqlSchemaCompatibilityTests(unittest.TestCase):
    def test_creature_sql_uses_current_single_id_column(self):
        offenders = []
        for path in SRC.rglob("*.sql"):
            sql = path.read_text(encoding="utf-8")
            for obsolete in ("`id1`", "`id2`", "`id3`"):
                if obsolete in sql:
                    offenders.append(f"{path.relative_to(ROOT)} contains {obsolete}")

        self.assertEqual([], offenders, "\n".join(offenders))

    def test_launch_creature_inserts_use_current_column_list(self):
        for relative in (
            "src/patch_00-1_1/sql/patch_00-1_1-creature.sql",
            "src/patch_00-1_1/sql/patch_00-1_1-zz-onyxia-horde.sql",
            "src/phase_00/sql/phase_00-creature.sql",
        ):
            sql = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(path=relative):
                self.assertNotIn("`id1`", sql)
                self.assertNotIn("`id2`", sql)
                self.assertNotIn("`id3`", sql)
                self.assertIn("INSERT INTO `creature` (`guid`, `id`, `map`", sql)

    def test_patch_sql_never_mutates_character_quest_storage(self):
        forbidden = (
            "character_queststatus",
            "character_queststatus_rewarded",
            "character_queststatus_daily",
            "character_queststatus_weekly",
            "character_queststatus_monthly",
        )
        offenders = []
        for path in SRC.glob("patch_*/sql/*.sql"):
            sql = path.read_text(encoding="utf-8").lower()
            for table in forbidden:
                if table in sql:
                    offenders.append(f"{path.relative_to(ROOT)} references {table}")

        self.assertEqual([], offenders, "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
