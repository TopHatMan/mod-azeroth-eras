from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


MARAUDON_OUTDOOR_NPCS = (12239, 12240, 12241, 12242, 12243, 13656, 13697, 13718)
MARAUDON_QUESTS = (7028, 7029, 7041, 7044, 7064, 7065, 7066, 7067, 7068, 7070)


class MaraudonProgressionBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch_creatures = read("src/patch_00-1_1/sql/patch_00-1_1-creature.sql")
        self.launch_disables = read("src/patch_00-1_1/sql/patch_00-1_1-disables.sql")
        self.patch_12_creatures = read("src/patch_01-1_2/sql/patch_01-1_2-creature.sql")
        self.patch_12_disables = read("src/patch_01-1_2/sql/patch_01-1_2-disables.sql")
        self.player = read("src/mod_progression_player.cpp")
        self.info = read("src/cs_progression.cpp")

    def test_launch_hides_outdoor_maraudon_npcs_and_disables_the_dungeon(self):
        for npc in MARAUDON_OUTDOOR_NPCS:
            with self.subTest(npc=npc):
                self.assertIn(str(npc), self.launch_creatures)
        self.assertIn("(2, 349, 1, '', '', 'Maraudon')", self.launch_disables)
        for quest in MARAUDON_QUESTS:
            with self.subTest(quest=quest):
                self.assertIn(f"(1, {quest},", self.launch_disables)

    def test_patch_12_unlocks_maraudon_bundle_together(self):
        self.assertIn("sourceType` = 2 AND `entry` = 349", self.patch_12_disables)
        for quest in MARAUDON_QUESTS:
            self.assertIn(str(quest), self.patch_12_disables)
        for npc in MARAUDON_OUTDOOR_NPCS:
            with self.subTest(npc=npc):
                self.assertIn(str(npc), self.patch_12_creatures)

    def test_patch_12_enables_winter_veil(self):
        self.assertIn("sourceType` = 9 AND `entry` IN (2, 52)", self.patch_12_disables)

    def test_runtime_and_info_command_name_the_1_2_boundary(self):
        self.assertIn("PATCH_MYSTERIES_OF_MARAUDON", self.player)
        patch_names = (ROOT / "src" / "mod_progression.cpp").read_text()
        self.assertIn("1.1 World of Warcraft", patch_names)
        self.assertIn("1.2 Mysteries of Maraudon", patch_names)
        self.assertIn("1.3 Ruins of the Dire Maul (MC attunement)", patch_names)
        self.assertIn("Ready target: 1.1-1.6", self.info)


if __name__ == "__main__":
    unittest.main()
