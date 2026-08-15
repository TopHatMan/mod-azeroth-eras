#!/usr/bin/env python3
"""Compare cMangos/vMaNGOS item_template data with AzerothCore.

The tool reads plain or gzip-compressed MySQL dumps without importing them into a
database. It produces a machine-readable inventory of schema and row differences.
It intentionally does not generate migration SQL: every field first needs an
explicit compatibility decision and historical-patch owner.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import IO, Iterator, Sequence


CREATE_START = re.compile(r"^CREATE TABLE `item_template` \(")
COLUMN = re.compile(r"^\s*`([^`]+)`\s+")
INSERT_START = re.compile(r"^INSERT INTO `item_template`(?:\s*\([^)]*\))? VALUES")

# Safe semantic aliases. Case and separators are normalized automatically;
# server-specific fields are deliberately not mapped here.
COLUMN_ALIASES = {
    "area_bound": "area",
    "bag_family": "bagfamily",
    "buy_count": "buycount",
    "buy_price": "buyprice",
    "container_slots": "containerslots",
    "disenchant_id": "disenchantid",
    "display_id": "displayid",
    "food_type": "foodtype",
    "inventory_type": "inventorytype",
    "item_level": "itemlevel",
    "lock_id": "lockid",
    "map_bound": "map",
    "max_count": "maxcount",
    "max_durability": "maxdurability",
    "max_money_loot": "maxmoneyloot",
    "min_money_loot": "minmoneyloot",
    "page_language": "languageid",
    "page_material": "pagematerial",
    "page_text": "pagetext",
    "random_property": "randomproperty",
    "range_mod": "rangedmodrange",
    "required_city_rank": "requiredcityrank",
    "required_honor_rank": "requiredhonorrank",
    "required_level": "requiredlevel",
    "required_reputation_faction": "requiredreputationfaction",
    "required_reputation_rank": "requiredreputationrank",
    "required_skill": "requiredskill",
    "required_skill_rank": "requiredskillrank",
    "required_spell": "requiredspell",
    "sell_price": "sellprice",
    "set_id": "itemset",
    "start_quest": "startquest",
}

# These columns need a deliberate conversion or policy instead of name matching.
REVIEW_REQUIRED = {
    "classic": {
        "ExtraFlags": "cMangos server flags; not equivalent to AzerothCore FlagsExtra",
        "dmg_min3": "AzerothCore item_template has only two damage slots",
        "dmg_max3": "AzerothCore item_template has only two damage slots",
        "dmg_type3": "AzerothCore item_template has only two damage slots",
        "dmg_min4": "AzerothCore item_template has only two damage slots",
        "dmg_max4": "AzerothCore item_template has only two damage slots",
        "dmg_type4": "AzerothCore item_template has only two damage slots",
        "dmg_min5": "AzerothCore item_template has only two damage slots",
        "dmg_max5": "AzerothCore item_template has only two damage slots",
        "dmg_type5": "AzerothCore item_template has only two damage slots",
    },
    "tbc": {
        "unk0": "likely SoundOverrideSubclass, but requires source-code verification",
        "ExtraFlags": "cMangos server flags; not equivalent to AzerothCore FlagsExtra",
        "dmg_min3": "AzerothCore item_template has only two damage slots",
        "dmg_max3": "AzerothCore item_template has only two damage slots",
        "dmg_type3": "AzerothCore item_template has only two damage slots",
        "dmg_min4": "AzerothCore item_template has only two damage slots",
        "dmg_max4": "AzerothCore item_template has only two damage slots",
        "dmg_type4": "AzerothCore item_template has only two damage slots",
        "dmg_min5": "AzerothCore item_template has only two damage slots",
        "dmg_max5": "AzerothCore item_template has only two damage slots",
        "dmg_type5": "AzerothCore item_template has only two damage slots",
    },
    "vmangos": {
        "patch": "vMaNGOS content-patch revision key; use newest row at or before the target patch",
        "extra_flags": "vMaNGOS server flags; requires an explicit AzerothCore conversion policy",
        "dmg_min3": "AzerothCore item_template has only two damage slots",
        "dmg_max3": "AzerothCore item_template has only two damage slots",
        "dmg_type3": "AzerothCore item_template has only two damage slots",
        "dmg_min4": "AzerothCore item_template has only two damage slots",
        "dmg_max4": "AzerothCore item_template has only two damage slots",
        "dmg_type4": "AzerothCore item_template has only two damage slots",
        "dmg_min5": "AzerothCore item_template has only two damage slots",
        "dmg_max5": "AzerothCore item_template has only two damage slots",
        "dmg_type5": "AzerothCore item_template has only two damage slots",
    },
    "wrath": {
        "FlagsExtra": "Wrath/AzerothCore-only field; era reset policy required",
        "ScalingStatDistribution": "Wrath scaling field; must be disabled before introduction",
        "ScalingStatValue": "Wrath scaling field; must be disabled before introduction",
        "ItemLimitCategory": "Wrath field; patch availability policy required",
        "HolidayId": "Wrath field; patch availability policy required",
        "flagsCustom": "AzerothCore server field; preserve unless bundle owns it",
        "VerifiedBuild": "AzerothCore provenance field; do not copy from cMangos",
    },
}


@contextmanager
def open_text(path: Path) -> Iterator[IO[str]]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
            yield handle
    else:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            yield handle


def read_columns(path: Path) -> list[str]:
    columns: list[str] = []
    in_table = False
    with open_text(path) as handle:
        for line in handle:
            if not in_table:
                if CREATE_START.match(line):
                    in_table = True
                continue
            if line.startswith(")"):
                break
            match = COLUMN.match(line)
            if match:
                columns.append(match.group(1))
    if not columns:
        raise ValueError(f"item_template CREATE TABLE not found in {path}")
    return columns


def iter_tuple_text(path: Path) -> Iterator[str]:
    """Yield each raw tuple body from item_template INSERT statements."""

    in_values = False
    in_quote = False
    escaped = False
    depth = 0
    buffer: list[str] = []

    with open_text(path) as handle:
        for line in handle:
            if not in_values:
                match = INSERT_START.match(line)
                if not match:
                    continue
                in_values = True
                line = line[match.end() :]

            for char in line:
                if depth == 0:
                    if char == "(":
                        depth = 1
                        buffer = []
                    elif char == ";":
                        in_values = False
                    continue

                if in_quote:
                    buffer.append(char)
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == "'":
                        in_quote = False
                    continue

                if char == "'":
                    in_quote = True
                    buffer.append(char)
                elif char == "(":
                    depth += 1
                    buffer.append(char)
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        yield "".join(buffer)
                    else:
                        buffer.append(char)
                else:
                    buffer.append(char)

    if depth or in_quote:
        raise ValueError(f"unterminated item_template tuple in {path}")


def split_fields(tuple_text: str) -> list[str]:
    fields: list[str] = []
    buffer: list[str] = []
    in_quote = False
    escaped = False

    for char in tuple_text:
        if in_quote:
            buffer.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "'":
                in_quote = False
        elif char == "'":
            in_quote = True
            buffer.append(char)
        elif char == ",":
            fields.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(char)

    fields.append("".join(buffer).strip())
    return fields


MYSQL_ESCAPES = {
    "0": "\0",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
}


def decode_sql_string(value: str) -> str:
    body = value[1:-1]
    result: list[str] = []
    index = 0
    while index < len(body):
        char = body[index]
        if char == "\\" and index + 1 < len(body):
            index += 1
            escaped = body[index]
            result.append(MYSQL_ESCAPES.get(escaped, escaped))
        else:
            result.append(char)
        index += 1
    return "".join(result)


def normalize_value(value: str):
    if value.upper() == "NULL":
        return None
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return decode_sql_string(value)
    try:
        number = Decimal(value)
    except InvalidOperation:
        return value
    if number == number.to_integral_value():
        return int(number)
    return float(number)


def iter_rows(path: Path, columns: Sequence[str]) -> Iterator[tuple]:
    expected = len(columns)
    for raw_tuple in iter_tuple_text(path):
        fields = split_fields(raw_tuple)
        if len(fields) != expected:
            entry = fields[0] if fields else "unknown"
            raise ValueError(
                f"{path}: item {entry} has {len(fields)} values; schema has {expected} columns"
            )
        yield tuple(normalize_value(value) for value in fields)


def canonical_column(name: str) -> str:
    lowered = name.lower()
    aliased = COLUMN_ALIASES.get(lowered, lowered)
    return re.sub(r"[^a-z0-9]", "", aliased)


def compatible_columns(left: Sequence[str], right: Sequence[str]) -> list[tuple[str, int, int]]:
    right_index = {canonical_column(name): index for index, name in enumerate(right)}
    pairs = []
    for left_index, name in enumerate(left):
        canonical = canonical_column(name)
        if canonical == "entry" or canonical not in right_index:
            continue
        pairs.append((canonical, left_index, right_index[canonical]))
    return pairs


def index_rows(
    path: Path, columns: Sequence[str], content_patch: int | None = None
) -> dict[int, tuple]:
    """Index rows by entry, optionally materializing a vMaNGOS patch snapshot."""

    entry_index = next(i for i, name in enumerate(columns) if name.lower() == "entry")
    patch_index = None
    if content_patch is not None:
        try:
            patch_index = next(i for i, name in enumerate(columns) if name.lower() == "patch")
        except StopIteration as exc:
            raise ValueError(f"{path}: content-patch selection requires a patch column") from exc

    indexed: dict[int, tuple] = {}
    selected_patch: dict[int, int] = {}
    for row in iter_rows(path, columns):
        entry = int(row[entry_index])
        if patch_index is None:
            indexed[entry] = row
            continue

        row_patch = int(row[patch_index])
        if row_patch > content_patch or row_patch < selected_patch.get(entry, -1):
            continue
        indexed[entry] = row
        selected_patch[entry] = row_patch
    return indexed


def progressive_summary(path: Path, columns: Sequence[str]) -> dict:
    """Describe vMaNGOS item introduction/revision rows and materialized states."""

    entry_index = next(i for i, name in enumerate(columns) if name.lower() == "entry")
    patch_index = next(i for i, name in enumerate(columns) if name.lower() == "patch")
    entries_by_patch: dict[int, set[int]] = {}
    raw_rows = 0
    for row in iter_rows(path, columns):
        raw_rows += 1
        entries_by_patch.setdefault(int(row[patch_index]), set()).add(int(row[entry_index]))

    seen: set[int] = set()
    patches = {}
    for patch in range(11):
        entries = entries_by_patch.get(patch, set())
        introduced = entries - seen
        revised = entries & seen
        seen.update(entries)
        patches[str(patch)] = {
            "wow_patch": f"1.{patch + 2}",
            "rows_at_patch": len(entries),
            "introduced_items": len(introduced),
            "revised_items": len(revised),
            "materialized_items": len(seen),
        }

    return {
        "raw_rows": raw_rows,
        "distinct_items": len(seen),
        "historical_revision_rows": raw_rows - len(seen),
        "patches": patches,
    }


def compare_pair(
    left_path: Path,
    left_columns: Sequence[str],
    right_path: Path,
    right_columns: Sequence[str],
    sample_limit: int,
    left_patch: int | None = None,
    right_patch: int | None = None,
) -> dict:
    column_pairs = compatible_columns(left_columns, right_columns)

    left_rows = index_rows(left_path, left_columns, left_patch)
    right_rows = index_rows(right_path, right_columns, right_patch)

    left_total = len(left_rows)
    right_total = len(right_rows)
    common = 0
    identical = 0
    differing_items = 0
    difference_counts: Counter[str] = Counter()
    samples = []
    only_right = []

    for entry, right_row in right_rows.items():
        left_row = left_rows.pop(entry, None)
        if left_row is None:
            if len(only_right) < sample_limit:
                only_right.append(entry)
            continue

        common += 1
        item_diffs = []
        for column, left_index, right_index in column_pairs:
            left_value = left_row[left_index]
            right_value = right_row[right_index]
            if left_value != right_value:
                difference_counts[column] += 1
                if len(item_diffs) < 12:
                    item_diffs.append(
                        {"column": column, "left": left_value, "right": right_value}
                    )

        if item_diffs:
            differing_items += 1
            if len(samples) < sample_limit:
                samples.append({"entry": entry, "differences": item_diffs})
        else:
            identical += 1

    only_left = sorted(left_rows)[:sample_limit]
    return {
        "left_rows": left_total,
        "right_rows": right_total,
        "common_items": common,
        "identical_common_items": identical,
        "differing_common_items": differing_items,
        "only_left_count": left_total - common,
        "only_right_count": right_total - common,
        "only_left_sample": only_left,
        "only_right_sample": only_right,
        "compared_columns": [column for column, _, _ in column_pairs],
        "field_difference_counts": dict(difference_counts.most_common()),
        "item_difference_samples": samples,
    }


def schema_report(label: str, columns: Sequence[str]) -> dict:
    return {
        "column_count": len(columns),
        "columns": list(columns),
        "review_required": REVIEW_REQUIRED.get(label, {}),
    }


def build_report(
    classic: Path,
    tbc: Path,
    wrath: Path,
    sample_limit: int,
    vmangos: Path | None = None,
) -> dict:
    paths = {"classic": classic, "tbc": tbc, "wrath": wrath}
    if vmangos is not None:
        paths["vmangos"] = vmangos
    columns = {label: read_columns(path) for label, path in paths.items()}
    report = {
        "format_version": 2 if vmangos is not None else 1,
        "sources": {label: str(path) for label, path in paths.items()},
        "schemas": {
            label: schema_report(label, source_columns)
            for label, source_columns in columns.items()
        },
        "comparisons": {
            "classic_vs_wrath": compare_pair(
                classic, columns["classic"], wrath, columns["wrath"], sample_limit
            ),
            "tbc_vs_wrath": compare_pair(
                tbc, columns["tbc"], wrath, columns["wrath"], sample_limit
            ),
            "classic_vs_tbc": compare_pair(
                classic, columns["classic"], tbc, columns["tbc"], sample_limit
            ),
        },
    }
    if vmangos is not None:
        report["progression"] = {
            "vmangos_items": progressive_summary(vmangos, columns["vmangos"])
        }
        report["comparisons"]["vmangos_112_vs_classic"] = compare_pair(
            vmangos,
            columns["vmangos"],
            classic,
            columns["classic"],
            sample_limit,
            left_patch=10,
        )
        report["comparisons"]["vmangos_112_vs_wrath"] = compare_pair(
            vmangos,
            columns["vmangos"],
            wrath,
            columns["wrath"],
            sample_limit,
            left_patch=10,
        )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classic", required=True, type=Path, help="ClassicDB SQL or SQL.gz")
    parser.add_argument("--tbc", required=True, type=Path, help="TBCDB SQL or SQL.gz")
    parser.add_argument("--wrath", required=True, type=Path, help="AzerothCore item_template SQL")
    parser.add_argument(
        "--vmangos", type=Path, help="Optional vMaNGOS progressive world database SQL"
    )
    parser.add_argument("--output", required=True, type=Path, help="JSON report destination")
    parser.add_argument("--sample-limit", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        args.classic, args.tbc, args.wrath, args.sample_limit, vmangos=args.vmangos
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
