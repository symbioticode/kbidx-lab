#!/usr/bin/env python3
"""Convert and validate the small TOML registry into deterministic JSON."""
import argparse
import json
import tomllib
from pathlib import Path

REQUIRED = ("id", "kind", "state", "priority")


def load_registry(source: Path) -> list[dict]:
    data = tomllib.loads(source.read_text(encoding="utf-8"))
    items = data.get("item", [])
    if not isinstance(items, list):
        raise ValueError("registry must contain one or more [[item]] tables")
    if not items:
        raise ValueError("registry must contain one or more [[item]] tables")
    if any(not isinstance(item, dict) for item in items):
        raise ValueError("each [[item]] entry must be a TOML table")
    identifiers = [item.get("id") for item in items]
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicates:
        raise ValueError(f"duplicate item id(s): {', '.join(str(identifier) for identifier in duplicates)}")
    for index, item in enumerate(items, 1):
        missing = [field for field in REQUIRED if not isinstance(item.get(field), str) or not item.get(field).strip()]
        if missing:
            raise ValueError(f"item {index} missing required field(s): {', '.join(missing)}")
    return items

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.source.with_suffix(".json")
    try:
        items = load_registry(args.source)
    except (OSError, tomllib.TOMLDecodeError, ValueError) as error:
        parser.error(str(error))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": 1, "items": items}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)

if __name__ == "__main__":
    main()
