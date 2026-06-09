#!/usr/bin/env python3
"""Validate that route-to-service maps reference implemented functions."""

from __future__ import annotations

from pathlib import Path
import importlib
import sys


def _load_module(module_name: str):
    return importlib.import_module(module_name)


def _validate_pair(service_map_module: str, services_module: str, label: str) -> list[str]:
    errors: list[str] = []
    service_map_mod = _load_module(service_map_module)
    services_mod = _load_module(services_module)

    route_map = getattr(service_map_mod, "ROUTE_TO_SERVICE", {})
    if not isinstance(route_map, dict):
        return [f"{label}: ROUTE_TO_SERVICE is not a dict"]

    for route_key, service_name in route_map.items():
        if not isinstance(route_key, tuple) or len(route_key) != 2:
            errors.append(f"{label}: invalid route key {route_key!r}")
            continue
        if not hasattr(services_mod, service_name):
            errors.append(f"{label}: missing function '{service_name}' for route {route_key}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parent
    src_path = root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    checks = [
        ("api.importing.service_map", "api.importing.services", "importing"),
        ("api.matching.service_map", "api.matching.services", "matching"),
    ]

    all_errors: list[str] = []
    for service_map_module, services_module, label in checks:
        all_errors.extend(_validate_pair(service_map_module, services_module, label))

    if all_errors:
        print("Service-map validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("Service-map validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
