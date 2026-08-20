from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class MoltenCoreProgressionBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.patch_11 = read("src/patch_00-1_1/sql/patch_00-1_1-zz-molten-core.sql")
        self.patch_13 = read("src/patch_02-1_3/sql/patch_02-1_3-zz-molten-core.sql")
        self.patch_14 = read("src/patch_03-1_4/sql/patch_03-1_4-zz-molten-core.sql")
        self.area_trigger = read("src/mod_progression_areatrigger.cpp")
        self.registration = read("src/mod_progression.cpp")

    def test_patch_11_keeps_raid_open_but_attunement_bundle_hidden(self) -> None:
        self.assertRegex(
            self.patch_11,
            r"DELETE FROM `disables` WHERE `sourceType` = 2 AND `entry` = 409",
        )
        self.assertRegex(self.patch_11, r"\(1, 7487, .*patch 1\.3'\)")
        self.assertRegex(self.patch_11, r"\(1, 7848, .*patch 1\.3'\)")
        self.assertRegex(self.patch_11, r"phaseMask` = 16384 WHERE `id` = 14387")
        self.assertRegex(self.patch_11, r"phaseMask` = 16384 WHERE `id` = 179553")

    def test_physical_entrance_is_not_bound_to_shortcut_gate(self) -> None:
        self.assertNotRegex(self.patch_11, r"\(2886,")
        self.assertRegex(self.patch_11, r"\(3528, 'at_progression_molten_core_shortcut'\)")
        self.assertRegex(self.patch_11, r"\(3529, 'at_progression_molten_core_shortcut'\)")

    def test_shortcut_requires_patch_13_and_attunement(self) -> None:
        self.assertIn("PATCH_RUINS_OF_THE_DIRE_MAUL", self.area_trigger)
        self.assertIn("GetQuestRewardStatus(QUEST_ATTUNEMENT_TO_THE_CORE_ALLIANCE)", self.area_trigger)
        self.assertIn("GetQuestRewardStatus(QUEST_ATTUNEMENT_TO_THE_CORE_HORDE)", self.area_trigger)
        self.assertIn("AddSC_progression_area_triggers();", self.registration)

    def test_patch_13_unlocks_complete_bundle_and_places_fragment_inside_mc(self) -> None:
        self.assertRegex(self.patch_13, r"entry` IN \(7487, 7848\)")
        self.assertRegex(self.patch_13, r"phaseMask` = 1 WHERE `id` = 14387")
        self.assertRegex(self.patch_13, r"`map` = 409,")
        self.assertRegex(self.patch_13, r"WHERE `id` = 179553")

    def test_patch_14_relocates_fragment_to_canonical_brd_spawn(self) -> None:
        self.assertRegex(self.patch_14, r"`map` = 230,")
        self.assertRegex(self.patch_14, r"`position_x` = 1128\.01,")
        self.assertRegex(self.patch_14, r"`position_y` = -471\.763,")
        self.assertRegex(self.patch_14, r"`position_z` = -104\.032,")
        self.assertRegex(self.patch_14, r"WHERE `id` = 179553")

    def test_no_patch_disables_molten_core_map(self) -> None:
        inserts_map_409 = []
        pattern = re.compile(r"\(2,\s*409,", re.IGNORECASE)
        for sql_file in (ROOT / "src").glob("patch_*/sql/*.sql"):
            if pattern.search(sql_file.read_text(encoding="utf-8")):
                inserts_map_409.append(str(sql_file.relative_to(ROOT)))
        self.assertEqual([], inserts_map_409)


if __name__ == "__main__":
    unittest.main()
