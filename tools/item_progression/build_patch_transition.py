#!/usr/bin/env python3
"""Build a reviewable vMaNGOS item transition for an AzerothCore target.

This tool does not emit executable SQL. It identifies the exact rows authored at
one vMaNGOS content patch, materializes the before/after item states, and maps
changed fields onto the AzerothCore item_template schema. Fields are classified
as direct candidates, explicit review requirements, or unavailable mappings.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from compare_item_templates import (
    REVIEW_REQUIRED,
    canonical_column,
    index_rows,
    iter_rows,
    read_columns,
)


VMANGOS_PATCH_NAMES = {patch: f"1.{patch + 2}" for patch in range(11)}


def row_as_dict(columns, row):
    return {column: row[index] for index, column in enumerate(columns)}


def target_column_map(columns):
    return {canonical_column(column): column for column in columns}


def build_transition(vmangos: Path, wrath: Path, patch: int) -> dict:
    if patch not in VMANGOS_PATCH_NAMES:
        raise ValueError("vMaNGOS content patch must be between 0 (1.2) and 10 (1.12)")

    vmangos_columns = read_columns(vmangos)
    wrath_columns = read_columns(wrath)
    entry_index = next(
        index for index, name in enumerate(vmangos_columns) if name.lower() == "entry"
    )
    patch_index = next(
        index for index, name in enumerate(vmangos_columns) if name.lower() == "patch"
    )

    authored_entries = {
        int(row[entry_index])
        for row in iter_rows(vmangos, vmangos_columns)
        if int(row[patch_index]) == patch
    }
    before_rows = index_rows(vmangos, vmangos_columns, patch - 1) if patch else {}
    after_rows = index_rows(vmangos, vmangos_columns, patch)
    target_rows = index_rows(wrath, wrath_columns)
    target_columns = target_column_map(wrath_columns)
    target_indices = {name: index for index, name in enumerate(wrath_columns)}
    review_required = {
        canonical_column(name): reason
        for name, reason in REVIEW_REQUIRED["vmangos"].items()
    }

    field_counts: Counter[str] = Counter()
    policy_counts: Counter[str] = Counter()
    candidates = []
    introduced = 0
    revised = 0

    for entry in sorted(authored_entries):
        before = before_rows.get(entry)
        after = after_rows[entry]
        target = target_rows.get(entry)
        transition_type = "introduced" if before is None else "revised"
        if before is None:
            introduced += 1
        else:
            revised += 1

        changes = []
        for index, source_column in enumerate(vmangos_columns):
            canonical = canonical_column(source_column)
            if canonical in {"entry", "patch"}:
                continue
            before_value = None if before is None else before[index]
            after_value = after[index]
            if before is not None and before_value == after_value:
                continue

            target_column = target_columns.get(canonical)
            if canonical in review_required:
                policy = "review"
                reason = review_required[canonical]
            elif target_column is None:
                policy = "unmapped"
                reason = "No same-name AzerothCore item_template column"
            else:
                policy = "direct-candidate"
                reason = "Same-name field; historical value still requires review"

            target_value = None
            if target is not None and target_column is not None:
                target_value = target[target_indices[target_column]]

            field_counts[canonical] += 1
            policy_counts[policy] += 1
            changes.append(
                {
                    "source_column": source_column,
                    "azerothcore_column": target_column,
                    "before": before_value,
                    "after": after_value,
                    "azerothcore_current": target_value,
                    "policy": policy,
                    "reason": reason,
                }
            )

        after_values = row_as_dict(vmangos_columns, after)
        candidates.append(
            {
                "entry": entry,
                "name": after_values.get("name"),
                "transition": transition_type,
                "present_in_azerothcore": target is not None,
                "changes": changes,
            }
        )

    return {
        "format": "azeroth-eras-item-transition-v1",
        "source_table": "item_template",
        "vmangos_content_patch": patch,
        "wow_patch": VMANGOS_PATCH_NAMES[patch],
        "candidate_count": len(candidates),
        "introduced_count": introduced,
        "revised_count": revised,
        "field_change_counts": dict(field_counts.most_common()),
        "policy_counts": dict(policy_counts.most_common()),
        "candidates": candidates,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vmangos", required=True, type=Path)
    parser.add_argument("--wrath", required=True, type=Path)
    parser.add_argument(
        "--patch",
        required=True,
        type=int,
        choices=range(11),
        metavar="0..10",
        help="vMaNGOS content patch: 0=1.2 through 10=1.12",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_transition(args.vmangos, args.wrath, args.patch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {args.output}: {report['introduced_count']} introduced, "
        f"{report['revised_count']} revised"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
