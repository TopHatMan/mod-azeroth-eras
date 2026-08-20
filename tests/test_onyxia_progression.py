from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class OnyxiaProgressionBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch = read("src/patch_00-1_1/sql/patch_00-1_1-zz-launch-content-fixes.sql")
        self.horde = read("src/patch_00-1_1/sql/patch_00-1_1-zz-onyxia-horde.sql")

    def test_launch_restores_emberstrife(self) -> None:
        self.assertIn("WHERE `id` = 10321", self.launch)

    def test_launch_restores_rexxar_instead_of_rokaros_spawn(self) -> None:
        self.assertIn("`name` = 'Rexxar'", self.horde)
        self.assertNotIn("`name` = 'Rokaro'", self.horde)
        self.assertIn("(10182, 0, 11660, 1, 1, 11200)", self.horde)
        self.assertRegex(self.horde, r"\(29113, 10182, 1, .*?, 1, 1, 1,")

    def test_rexxar_and_misha_are_one_formation(self) -> None:
        self.assertRegex(self.horde, r"\(610204, 10204, 1, .*?, 1, 1, 0,")
        self.assertIn("(29113, 610204, 4, 90, 519, 0, 0)", self.horde)

    def test_original_chain_text_points_to_rexxar(self) -> None:
        for quest_id in (6567, 6568, 6601, 6602):
            self.assertRegex(self.horde, rf"WHERE `ID` = {quest_id};")
        self.assertIn("Rexxar''s Testament", self.horde)
        self.assertIn("return it to Rexxar", self.horde)

    def test_rexxars_patrol_is_complete_and_contiguous(self) -> None:
        points = [
            int(value)
            for value in re.findall(r"\(291130, (\d+),", self.horde)
        ]
        self.assertEqual(list(range(1, 349)), points)

    def test_no_patch_disables_onyxias_lair(self) -> None:
        offenders = []
        pattern = re.compile(r"\(2,\s*249,", re.IGNORECASE)
        for sql_file in (ROOT / "src").glob("patch_*/sql/*.sql"):
            if pattern.search(sql_file.read_text(encoding="utf-8")):
                offenders.append(str(sql_file.relative_to(ROOT)))
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
