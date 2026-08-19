import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class ReadyTarget106Tests(unittest.TestCase):
    def test_launch_id_is_1_1_and_ready_target_is_1_6(self):
        header = (SRC / "mod_progression.h").read_text(encoding="utf-8")
        self.assertIn("PATCH_VANILLA_1_1 = 0", header)
        self.assertIn("PROGRESSION_READY_TARGET_PATCH = PATCH_ASSAULT_ON_BLACKWING_LAIR", header)

    def test_headline_unlocks_exist_for_1_1_through_1_6(self):
        expected = {
            "patch_00-1_1": ["(2, 349,", "(2, 429,", "(2, 469,"],
            "patch_01-1_2": ["entry` = 349"],
            "patch_02-1_3": ["entry` = 429", "7487", "7848"],
            "patch_03-1_4": ["18646"],
            "patch_04-1_5": ["entry` IN (1, 2)"],
            "patch_05-1_6": ["entry` = 469"],
        }
        for directory, needles in expected.items():
            disables = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (SRC / directory / "sql").glob("*-disables.sql")
            )
            extra = ""
            zz = list((SRC / directory / "sql").glob("*zz*.sql"))
            extra = "\n".join(path.read_text(encoding="utf-8") for path in zz)
            blob = disables + "\n" + extra
            for needle in needles:
                with self.subTest(directory=directory, needle=needle):
                    self.assertIn(needle, blob)

    def test_1_3_unhides_world_bosses_and_lothos(self):
        creatures = (SRC / "patch_02-1_3" / "sql" / "patch_02-1_3-creature.sql").read_text(encoding="utf-8")
        for npc in (6109, 12397, 14387):
            self.assertIn(str(npc), creatures)


if __name__ == "__main__":
    unittest.main()
