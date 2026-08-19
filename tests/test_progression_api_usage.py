import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCARAB_GATE = SRC / "phase_00" / "scripts" / "Kalimdor" / "Silithus" / "go_scarab_gate.cpp"
MODULE_ENTRYPOINT = SRC / "mod_progression.cpp"


class ProgressionApiUsageTests(unittest.TestCase):
    def test_cpp_sources_do_not_call_removed_phase_manager_api(self):
        stale_references = []
        for path in sorted((*SRC.rglob("*.cpp"), *SRC.rglob("*.h"))):
            source = path.read_text(encoding="utf-8")
            for api in ("GetPhaseId", "SetPhaseId"):
                if api in source:
                    stale_references.append(f"{path.relative_to(ROOT)}: {api}")

        self.assertEqual(stale_references, [])

    def test_module_exports_loader_symbol_for_repository_directory_name(self):
        source = MODULE_ENTRYPOINT.read_text(encoding="utf-8")
        self.assertIn("void Addmod_azeroth_erasScripts()", source)

    def test_sql_path_resolver_includes_repository_directory_name(self):
        source = (SRC / "mod_progression_database.cpp").read_text(encoding="utf-8")
        self.assertIn('candidates.emplace_back("mod-azeroth-eras")', source)

    def test_scarab_gate_uses_the_historical_aq_patch_boundary(self):
        source = SCARAB_GATE.read_text(encoding="utf-8")
        self.assertIn(
            "GetPatchId() >= PATCH_THE_GATES_OF_AHN_QIRAJ",
            source,
        )
        self.assertNotIn("GetPatchId() >= 5", source)


if __name__ == "__main__":
    unittest.main()
