#!/usr/bin/env python3
"""Audit existing Vanilla item SQL against vMaNGOS patch revision candidates.

This report measures candidate coverage only. A matching item ID does not prove
that the existing AzerothCore SQL has the correct historical values, and an
unmatched vMaNGOS row is not automatically authoritative.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Sequence

from compare_item_templates import iter_rows, read_columns


ENTRY_EQUALS = re.compile(r"`?entry`?\s*=\s*(\d+)", re.IGNORECASE)
ENTRY_IN = re.compile(r"`?entry`?\s+IN\s*\(([^)]*)\)", re.IGNORECASE)
INTEGER = re.compile(r"\b\d+\b")


def touched_item_entries(path: Path) -> set[int]:
    """Return item entries selected by UPDATE statements in a patch SQL file."""

    if not path.exists():
        return set()

    entries: set[int] = set()
    sql = path.read_text(encoding="utf-8", errors="replace")
    for statement in sql.split(";"):
        if "item_template" not in statement.lower() or "where" not in statement.lower():
            continue
        where = statement.lower().rsplit("where", 1)[1]
        entries.update(int(match.group(1)) for match in ENTRY_EQUALS.finditer(where))
        for match in ENTRY_IN.finditer(where):
            entries.update(int(value) for value in INTEGER.findall(match.group(1)))
    return entries


def vmangos_transitions(path: Path, columns: Sequence[str]) -> dict[int, dict[str, set[int]]]:
    entry_index = next(i for i, name in enumerate(columns) if name.lower() == "entry")
    patch_index = next(i for i, name in enumerate(columns) if name.lower() == "patch")
    entries_by_patch: dict[int, set[int]] = {}
    for row in iter_rows(path, columns):
        entries_by_patch.setdefault(int(row[patch_index]), set()).add(int(row[entry_index]))

    seen: set[int] = set()
    transitions = {}
    for patch in range(11):
        entries = entries_by_patch.get(patch, set())
        transitions[patch] = {
            "introduced": entries - seen,
            "revised": entries & seen,
        }
        seen.update(entries)
    return transitions


def build_report(vmangos: Path, repository: Path, sample_limit: int) -> dict:
    columns = read_columns(vmangos)
    transitions = vmangos_transitions(vmangos, columns)
    patches = {}

    for vmangos_patch in range(11):
        module_patch = vmangos_patch + 1
        wow_patch = f"1.{vmangos_patch + 2}"
        sql_path = (
            repository
            / "src"
            / f"patch_{module_patch:02d}-{wow_patch.replace('.', '_')}"
            / "sql"
            / f"patch_{module_patch:02d}-{wow_patch.replace('.', '_')}-item_template.sql"
        )
        touched = touched_item_entries(sql_path)
        revised = transitions[vmangos_patch]["revised"]
        introduced = transitions[vmangos_patch]["introduced"]
        covered = revised & touched
        missing = revised - touched
        extra = touched - revised
        patches[str(module_patch)] = {
            "wow_patch": wow_patch,
            "sql_path": str(sql_path.relative_to(repository)) if sql_path.exists() else None,
            "vmangos_introduced_candidates": len(introduced),
            "vmangos_revision_candidates": len(revised),
            "existing_sql_touched_items": len(touched),
            "revision_id_overlap": len(covered),
            "uncovered_revision_candidates": len(missing),
            "existing_only_candidates": len(extra),
            "uncovered_sample": sorted(missing)[:sample_limit],
            "existing_only_sample": sorted(extra)[:sample_limit],
        }

    return {
        "format_version": 1,
        "warning": (
            "Candidate ID coverage only; values and historical provenance still require review. "
            "vMaNGOS has no patch 1.1 state."
        ),
        "vmangos_source": str(vmangos),
        "patches": patches,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vmangos", required=True, type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sample-limit", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.vmangos, args.repository.resolve(), args.sample_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
