import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCH_DISABLES = ROOT / "src" / "patch_00-1_1" / "sql" / "patch_00-1_1-disables.sql"
PATCH_111_DISABLES = ROOT / "src" / "patch_10-1_11" / "sql" / "patch_10-1_11-disables.sql"
MANIFEST = ROOT / "src" / "patch_10-1_11" / "scourge_invasion_manifest.json"


class ScourgeInvasionProgressionTests(unittest.TestCase):
    def test_launch_disables_the_actual_scourge_invasion_event(self):
        sql = LAUNCH_DISABLES.read_text(encoding="utf-8")
        self.assertIn("(9, 17, 0, '', '', 'Scourge Invasion')", sql)
        cleanup = next(
            line
            for line in sql.splitlines()
            if line.startswith("DELETE FROM `disables`")
            and "`sourceType` = 9" in line
        )
        self.assertIn("17", re.search(r"IN \(([^)]+)\)", cleanup).group(1).split(", "))

    def test_patch_111_enables_scourge_and_midsummer_without_conflating_ids(self):
        sql = PATCH_111_DISABLES.read_text(encoding="utf-8")
        self.assertRegex(
            sql,
            re.compile(
                r"DELETE\s+FROM\s+`disables`\s+WHERE\s+`sourceType`\s*=\s*9"
                r"\s+AND\s+`entry`\s+IN\s*\(1,\s*17\)",
                re.IGNORECASE,
            ),
        )

    def test_manifest_owns_all_six_original_invasion_zones(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["availability"]["global_event_id"], 17)
        self.assertEqual(manifest["availability"]["minimum_patch"], 10)
        self.assertEqual(manifest["availability"]["minimum_level_cap"], 60)
        self.assertEqual(
            {zone["name"] for zone in manifest["invasion_zones"]},
            {
                "Azshara",
                "Blasted Lands",
                "Burning Steppes",
                "Eastern Plaguelands",
                "Tanaris",
                "Winterspring",
            },
        )

    def test_manifest_separates_city_attacks_milestones_and_epilogue(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            {event["event_id"] for event in manifest["city_attacks"]}, {129, 130}
        )
        self.assertEqual(
            [stage["battles_won"] for stage in manifest["realm_milestones"]],
            [50, 100, 150],
        )
        self.assertEqual(manifest["completion_event_id"], 99)
        self.assertIn(
            "stop-event-and-clean-runtime-summons", manifest["lifecycle"]
        )


if __name__ == "__main__":
    unittest.main()
