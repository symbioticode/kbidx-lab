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
    for index, item in enumerate(items, 1):
        missing = [field for field in REQUIRED if not item.get(field)]
        if missing:
            raise ValueError(f"item {index} missing required field(s): {', '.join(missing)}")
    return items

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.source.with_suffix(".json")
    items = load_registry(args.source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": 1, "items": items}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)

if __name__ == "__main__":
    main()
