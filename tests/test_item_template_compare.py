import gzip
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "item_progression" / "compare_item_templates.py"
SPEC = importlib.util.spec_from_file_location("compare_item_templates", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture(columns, rows):
    definitions = ",\n".join(f"  `{column}` text" for column in columns)
    values = ",\n".join("(" + ",".join(row) + ")" for row in rows)
    return (
        "CREATE TABLE `item_template` (\n"
        + definitions
        + "\n);\nINSERT INTO `item_template` VALUES\n"
        + values
        + ";\n"
    )


class ItemTemplateCompareTests(unittest.TestCase):
    def test_plain_and_gzip_parsing_with_mysql_escapes(self):
        sql = fixture(
            ["entry", "name", "duration"],
            [["1", "'Rexxar\\'s Test'", "0"], ["2", "'line\\nvalue'", "1.50"]],
        )
        with tempfile.TemporaryDirectory() as directory:
            plain = Path(directory) / "items.sql"
            compressed = Path(directory) / "items.sql.gz"
            plain.write_text(sql, encoding="utf-8")
            with gzip.open(compressed, "wt", encoding="utf-8") as handle:
                handle.write(sql)

            for path in (plain, compressed):
                columns = MODULE.read_columns(path)
                rows = list(MODULE.iter_rows(path, columns))
                self.assertEqual(columns, ["entry", "name", "duration"])
                self.assertEqual(rows[0], (1, "Rexxar's Test", 0))
                self.assertEqual(rows[1], (2, "line\nvalue", 1.5))

    def test_comparison_counts_schema_and_item_differences(self):
        left_sql = fixture(
            ["entry", "name", "Duration"],
            [["1", "'Same'", "0"], ["2", "'Old'", "0"], ["3", "'Left only'", "0"]],
        )
        right_sql = fixture(
            ["entry", "name", "duration", "VerifiedBuild"],
            [["1", "'Same'", "0", "123"], ["2", "'New'", "0", "123"], ["4", "'Right only'", "0", "123"]],
        )
        with tempfile.TemporaryDirectory() as directory:
            left = Path(directory) / "left.sql"
            right = Path(directory) / "right.sql"
            left.write_text(left_sql, encoding="utf-8")
            right.write_text(right_sql, encoding="utf-8")
            result = MODULE.compare_pair(
                left,
                MODULE.read_columns(left),
                right,
                MODULE.read_columns(right),
                sample_limit=5,
            )

        self.assertEqual(result["common_items"], 2)
        self.assertEqual(result["identical_common_items"], 1)
        self.assertEqual(result["differing_common_items"], 1)
        self.assertEqual(result["only_left_count"], 1)
        self.assertEqual(result["only_right_count"], 1)
        self.assertEqual(result["field_difference_counts"], {"name": 1})

    def test_vmangos_snapshot_uses_latest_row_at_or_before_patch(self):
        sql = fixture(
            ["entry", "patch", "name"],
            [
                ["1", "0", "'Original'"],
                ["1", "2", "'Revised'"],
                ["2", "1", "'Introduced'"],
                ["3", "3", "'Too late'"],
            ],
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vmangos.sql"
            path.write_text(sql, encoding="utf-8")
            columns = MODULE.read_columns(path)
            snapshot = MODULE.index_rows(path, columns, content_patch=2)
            summary = MODULE.progressive_summary(path, columns)

        self.assertEqual(snapshot[1], (1, 2, "Revised"))
        self.assertEqual(snapshot[2], (2, 1, "Introduced"))
        self.assertNotIn(3, snapshot)
        self.assertEqual(summary["raw_rows"], 4)
        self.assertEqual(summary["distinct_items"], 3)
        self.assertEqual(summary["historical_revision_rows"], 1)
        self.assertEqual(summary["patches"]["2"]["revised_items"], 1)

    def test_canonical_columns_bridge_vmangos_and_azerothcore_names(self):
        self.assertEqual(MODULE.canonical_column("item_level"), "itemlevel")
        self.assertEqual(MODULE.canonical_column("ItemLevel"), "itemlevel")
        self.assertEqual(MODULE.canonical_column("page_language"), "languageid")
        self.assertEqual(MODULE.canonical_column("LanguageID"), "languageid")
        self.assertEqual(MODULE.canonical_column("other_team_entry"), "otherteamentry")
        self.assertNotEqual(
            MODULE.canonical_column("other_team_entry"),
            MODULE.canonical_column("TotemCategory"),
        )


if __name__ == "__main__":
    unittest.main()
