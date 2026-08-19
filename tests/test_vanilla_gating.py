import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PLAYER = SRC / "mod_progression_player.cpp"
DATABASE = SRC / "mod_progression_database.cpp"

VANILLA_INSTANCE_UNLOCKS = {
    349: "patch_01-1_2",   # Maraudon
    429: "patch_02-1_3",   # Dire Maul
    469: "patch_05-1_6",   # Blackwing Lair
    309: "patch_06-1_7",   # Zul'Gurub
    509: "patch_08-1_9",   # Ruins of Ahn'Qiraj
    531: "patch_08-1_9",   # Temple of Ahn'Qiraj
    533: "patch_10-1_11",  # Naxxramas
}

LAUNCH_OPEN_MAPS = {409, 249, 229, 230, 289, 329}  # MC, Onyxia, BRS, BRD, Scholo, Strat


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def disables_inserts_map(sql: str, map_id: int) -> bool:
    return re.search(rf"\(2,\s*{map_id},", sql) is not None


def disables_unlocks_map(sql: str, map_id: int) -> bool:
    return re.search(
        rf"DELETE FROM `disables` WHERE `sourceType` = 2 AND `entry`(?: = {map_id}| IN \([^)]*\b{map_id}\b)",
        sql,
    ) is not None


class VanillaGatingTests(unittest.TestCase):
    def test_sql_loader_checks_this_repository_directory_name(self):
        source = read(DATABASE)
        self.assertIn('candidates.emplace_back("mod-azeroth-eras")', source)
        self.assertIn("mod-azeroth-eras", source.split("could not find the module source directory")[1])

    def test_runtime_checks_patch_before_level_and_without_level_gating(self):
        source = read(PLAYER)
        self.assertIn("GetRequiredProgressionPatchForMap", source)
        self.assertIn("This content is not available in the current patch.", source)
        self.assertLess(
            source.find("GetRequiredProgressionPatchForMap"),
            source.find("IsLevelGatingEnabled"),
        )

    def test_level_60_finishes_vanilla_chromie_gate_without_bypassing_patch_gate(self):
        source = read(PLAYER)
        patch_check = source.index("GetRequiredProgressionPatchForMap", source.index("OnPlayerCanEnterMap"))
        vanilla_completion = source.index("GetLevelCap() >= 60", patch_check)
        level_table = source.index("GetRequiredProgressionLevelCapForMap", vanilla_completion)
        self.assertLess(patch_check, vanilla_completion)
        self.assertLess(vanilla_completion, level_table)
        self.assertIn("PATCH_BEFORE_THE_STORM", source[vanilla_completion - 160:vanilla_completion + 80])

    def test_legacy_progression_modules_are_reported_as_conflicts(self):
        config = read(SRC / "mod_progression_config.cpp")
        self.assertIn('ProgressionSystem.LoadScripts', config)
        self.assertIn('ProgressionSystem.LoadDatabase', config)
        self.assertIn('IndividualProgression.Enable', config)
        self.assertIn('compounded tuning', config)

    def test_runtime_vanilla_patch_boundaries(self):
        source = read(PLAYER)
        start = source.index("GetRequiredProgressionPatchForMap")
        end = source.index("void Progression::OnPlayerUpdateArea")
        patch_fn = source[start:end]
        expected = {
            "349": "PATCH_MYSTERIES_OF_MARAUDON",
            "429": "PATCH_RUINS_OF_THE_DIRE_MAUL",
            "469": "PATCH_ASSAULT_ON_BLACKWING_LAIR",
            "309": "PATCH_RISE_OF_THE_BLOOD_GOD",
            "509": "PATCH_THE_GATES_OF_AHN_QIRAJ",
            "531": "PATCH_THE_GATES_OF_AHN_QIRAJ",
            "533": "PATCH_SHADOW_OF_THE_NECROPOLIS",
            "530": "PATCH_BEFORE_THE_STORM",
            "571": "PATCH_ECHOES_OF_DOOM",
        }
        for map_id, patch in expected.items():
            with self.subTest(map_id=map_id):
                self.assertIn(f"case {map_id}:", patch_fn)
                case_at = patch_fn.index(f"case {map_id}:")
                return_at = patch_fn.index("return PATCH_", case_at)
                self.assertIn(patch, patch_fn[case_at:return_at + 64])

    def test_launch_sql_disables_later_vanilla_and_expansion_instances(self):
        sql = read(SRC / "patch_00-1_1" / "sql" / "patch_00-1_1-disables.sql")
        for map_id in VANILLA_INSTANCE_UNLOCKS:
            with self.subTest(map_id=map_id):
                self.assertTrue(disables_inserts_map(sql, map_id))
        for map_id in LAUNCH_OPEN_MAPS:
            with self.subTest(launch_map=map_id):
                self.assertFalse(disables_inserts_map(sql, map_id))
        for expansion_map in (530, 532, 564, 574, 603, 631, 724):
            if expansion_map == 530:
                continue
            with self.subTest(expansion_map=expansion_map):
                self.assertTrue(disables_inserts_map(sql, expansion_map))

    def test_each_vanilla_instance_unlocks_on_its_historical_patch(self):
        for map_id, patch_dir in VANILLA_INSTANCE_UNLOCKS.items():
            sql_files = list((SRC / patch_dir / "sql").glob("*-disables.sql"))
            self.assertTrue(sql_files, f"missing disables SQL in {patch_dir}")
            combined = "\n".join(read(path) for path in sql_files)
            with self.subTest(map_id=map_id, patch=patch_dir):
                self.assertTrue(disables_unlocks_map(combined, map_id))

    def test_launch_keeps_gurubashi_arena_booty_run_enabled(self):
        sql = read(SRC / "patch_00-1_1" / "sql" / "patch_00-1_1-disables.sql")
        self.assertNotRegex(sql, r"\(9,\s*16,")

    def test_quel_danas_is_blocked_before_sunwell_patch(self):
        source = read(PLAYER)
        self.assertIn("AREA_ISLE_OF_QUEL_DANAS", source)
        self.assertIn("PATCH_FURY_OF_THE_SUNWELL", source)


if __name__ == "__main__":
    unittest.main()
