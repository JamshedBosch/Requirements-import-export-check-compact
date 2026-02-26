#!/usr/bin/env python3
"""
Scan a folder with module Excel files, extract module names from filenames,
then look up these module names in another Excel file (column: 'Modulename').

Matching is fuzzy: spaces, underscores, and dots are treated as equivalent,
and the source name only needs to be a prefix of the target key (target entries
may contain additional description text after the module name).

If found, print:
  Source module name (from filename)  ->  Target module name (value in 'Modulename')

Usage:
  python find_moduleName.py --source-folder "C:/path/to/folder" --target-excel "C:/path/target.xlsx" [--sheet "Sheet1"]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Tuple, Optional

import pandas as pd


FILENAME_PATTERN = re.compile(
    r"^(?P<base>.+?)_[0-9a-fA-F]{8}_local_conversion\.xlsx$"
)
# Example:
# LAH 893.010.B_Digitaler Entwicklungsprozess ..._003d14d6_local_conversion.xlsx
# base -> LAH 893.010.B_Digitaler Entwicklungsprozess ...


def normalize_for_match(s: str, case_insensitive: bool = True) -> str:
    """
    Normalize a module name for fuzzy matching:
    - Strip leading/trailing whitespace
    - Treat spaces, underscores, and dots as equivalent (all become '.')
    - Collapse consecutive dots
    - Optionally lowercase
    """
    s = s.strip()
    s = re.sub(r"[ _.]", ".", s)
    s = re.sub(r"\.{2,}", ".", s)
    if case_insensitive:
        s = s.lower()
    return s


def extract_module_name(filename: str) -> Optional[str]:
    """
    Return module name from a filename by removing:
      _<8-hex>_local_conversion.xlsx
    If it doesn't match the expected pattern, return None.
    """
    m = FILENAME_PATTERN.match(filename)
    if not m:
        return None
    return m.group("base")


def list_source_modules(source_folder: str) -> List[Tuple[str, str]]:
    """
    Returns list of tuples: (source_filename, extracted_module_name)
    """
    if not os.path.isdir(source_folder):
        raise FileNotFoundError(f"Source folder not found: {source_folder}")

    items: List[Tuple[str, str]] = []
    for fn in sorted(os.listdir(source_folder)):
        if not fn.lower().endswith(".xlsx"):
            continue
        module = extract_module_name(fn)
        if module:
            items.append((fn, module))
        else:
            print(f"[WARN] Skipping (unexpected filename pattern): {fn}", file=sys.stderr)
    return items


def load_target_modules(target_excel: str, sheet: str | None = None) -> pd.DataFrame:
    if not os.path.isfile(target_excel):
        raise FileNotFoundError(f"Target excel not found: {target_excel}")

    df = pd.read_excel(target_excel, sheet_name=sheet)

    # If sheet_name=None returns dict (all sheets), take the first sheet
    if isinstance(df, dict):
        if not df:
            raise ValueError("Target excel contains no sheets.")
        first_sheet_name = next(iter(df.keys()))
        df = df[first_sheet_name]
        print(f"[INFO] No sheet specified. Using first sheet: {first_sheet_name}")

    if "Modulename" not in df.columns:
        raise ValueError(
            "Column 'Modulename' not found in target excel. "
            f"Available columns: {list(df.columns)}"
        )

    df["Modulename_norm"] = df["Modulename"].astype(str).str.strip()
    # Extract just the module name from full paths like:
    #   /260177_Audi_SSP/.../AS_044_LAH.000.900.AF_Some Title
    # -> take last path segment, strip leading AS_NNN_ prefix
    df["Modulename_key"] = (
        df["Modulename_norm"]
        .str.split("/").str[-1]                          # last path segment
        .str.replace(r"^[A-Z]+_\d+_", "", regex=True)   # strip AS_044_ prefix
        .str.strip()
    )
    return df


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-folder", required=True, help="Folder containing source module Excel files (.xlsx)")
    parser.add_argument("--target-excel", required=True, help="Excel file where column 'Modulename' exists")
    parser.add_argument("--sheet", default=None, help="Optional sheet name in target excel")
    parser.add_argument("--case-sensitive", action="store_true", help="Match Modulename case-sensitively (default: case-insensitive)")
    args = parser.parse_args()

    ci = not args.case_sensitive  # default: case-insensitive

    source_items = list_source_modules(args.source_folder)
    if not source_items:
        print("No matching source module files found.", file=sys.stderr)
        return 2

    df_target = load_target_modules(args.target_excel, args.sheet)

    # Build list of (normalized_key, original_Modulename) for fuzzy prefix matching.
    # Spaces, underscores, and dots are treated as equivalent.
    # Source name only needs to be a PREFIX of the target key (target may have extra text).
    target_entries: List[Tuple[str, str]] = [
        (normalize_for_match(key, ci), str(orig))
        for key, orig in zip(df_target["Modulename_key"], df_target["Modulename"])
    ]

    # Pattern to extract just the LAH module ID (e.g. "LAH.000.900.CM") from a name.
    # Use [A-Za-z0-9.]+ (no underscore) so it stops at the first "_" separator.
    _lah_id_re = re.compile(r"^(LAH[A-Za-z0-9.]+)", re.IGNORECASE)

    def find_match(source_module: str) -> Optional[str]:
        src_norm = normalize_for_match(source_module, ci)
        # 1) Full prefix match: target key starts with normalized source name
        for tgt_norm, tgt_val in target_entries:
            if tgt_norm.startswith(src_norm):
                return tgt_val
        # 2) ID-only fallback: match on just the LAH code (e.g. "LAH.000.900.CM")
        #    when descriptions differ between source and target
        id_m = _lah_id_re.match(source_module)
        if id_m:
            id_norm = normalize_for_match(id_m.group(1), ci) + "."  # require dot/separator after ID
            for tgt_norm, tgt_val in target_entries:
                if tgt_norm.startswith(id_norm):
                    return tgt_val
        return None

    print("Matches (Source -> Target):")
    print("-" * 80)

    found_any = False
    not_found: List[str] = []

    for source_filename, source_module in source_items:
        match = find_match(source_module)
        if match:
            found_any = True
            print(f"{source_module}  ->  {match}")
        else:
            not_found.append(source_module)

    if not_found:
        print(f"\n[INFO] {len(not_found)} source module(s) not found in target:")
        # For each unmatched module, extract the LAH module ID and search for it
        # as a substring in all target keys (catches different descriptions/formats).
        lah_id_pattern = re.compile(r"^(LAH[\w. ]+?)(?:[_ ]|$)", re.IGNORECASE)
        for mod in not_found:
            print(f"  {mod}")
            id_match = lah_id_pattern.match(mod)
            if id_match:
                lah_id_norm = normalize_for_match(id_match.group(1), ci)
                candidates = [
                    tgt_val for tgt_norm, tgt_val in target_entries
                    if lah_id_norm in tgt_norm
                ]
                if candidates:
                    # Deduplicate while preserving order
                    seen: set = set()
                    for c in candidates:
                        if c not in seen:
                            seen.add(c)
                            print(f"    [SIMILAR] {c}")
                else:
                    print(f"    [NOT IN TARGET] No entry containing '{id_match.group(1)}' found")

    if not found_any:
        print("\nNo matching modules found.")
        print("\n[DEBUG] Normalized source module names:")
        for _, mod in source_items:
            print(f"  {repr(normalize_for_match(mod, ci))}")
        print("\n[DEBUG] First 20 normalized target Modulename_key values:")
        for val in df_target["Modulename_key"].drop_duplicates().head(20):
            print(f"  {repr(normalize_for_match(val, ci))}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
