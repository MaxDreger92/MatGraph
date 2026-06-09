#!/usr/bin/env python3
"""Validate the lean migration manifest against files in the repository.

Usage:
    python recovery/lean_repo/check_manifest_paths.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import yaml


def _split_entry(entry: str) -> str:
    """Strip optional symbol suffixes like 'path.py:ClassName'."""
    return entry.split(":", 1)[0]


def _collect_entries(manifest: dict) -> dict[str, list[str]]:
    apps = manifest.get("apps", {})
    collected: dict[str, list[str]] = {"keep": [], "optional": [], "quarantine_first": []}

    for app_data in apps.values():
        for section in collected:
            values = app_data.get(section, [])
            collected[section].extend(values)

    collected["keep"].extend(manifest.get("shared_dependencies", {}).get("keep", []))
    collected["keep"].extend(manifest.get("project_routing", {}).get("required", []))

    return collected


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = repo_root / "recovery" / "lean_repo" / "module_manifest.yaml"

    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {manifest_path}")
        return 2

    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f) or {}

    entries_by_section = _collect_entries(manifest)

    missing_by_section: dict[str, list[str]] = {}
    for section, entries in entries_by_section.items():
        missing: list[str] = []
        for raw_entry in entries:
            path_str = _split_entry(raw_entry)
            if not path_str:
                continue
            candidate = repo_root / path_str
            if not candidate.exists():
                missing.append(raw_entry)
        if missing:
            missing_by_section[section] = missing

    print("Manifest validation summary")
    for section, entries in entries_by_section.items():
        print(f"- {section}: {len(entries)} entries")

    if not missing_by_section:
        print("\nAll referenced paths exist.")
        return 0

    print("\nMissing manifest entries:")
    for section, missing in missing_by_section.items():
        print(f"\n[{section}] ({len(missing)})")
        for entry in missing:
            print(f"  - {entry}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
