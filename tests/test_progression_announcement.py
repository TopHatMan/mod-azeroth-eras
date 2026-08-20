import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProgressionAnnouncementTests(unittest.TestCase):
    def test_login_and_startup_identify_azeroth_eras(self):
        player = (ROOT / "src/mod_progression_player.cpp").read_text(encoding="utf-8")
        server = (ROOT / "src/mod_progression_server.cpp").read_text(encoding="utf-8")
        header = (ROOT / "src/mod_progression.h").read_text(encoding="utf-8")
        config = (ROOT / "conf/mod_progression.conf.dist").read_text(encoding="utf-8")

        self.assertIn("void OnPlayerLogin", header)
        self.assertIn("Azeroth Eras is active", player)
        self.assertIn(".progression info", player)
        self.assertIn("Azeroth Eras active", server)
        self.assertIn("Progression.Announce.Enabled = 1", config)

    def test_patch_name_has_one_shared_runtime_source(self):
        core = (ROOT / "src/mod_progression.cpp").read_text(encoding="utf-8")
        player = (ROOT / "src/mod_progression_player.cpp").read_text(encoding="utf-8")
        command = (ROOT / "src/cs_progression.cpp").read_text(encoding="utf-8")

        self.assertIn("GetProgressionPatchDisplayName", core)
        self.assertIn("GetProgressionPatchDisplayName", player)
        self.assertIn("GetProgressionPatchDisplayName", command)


if __name__ == "__main__":
    unittest.main()
