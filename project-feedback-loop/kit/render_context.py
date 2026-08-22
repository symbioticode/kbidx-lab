#!/usr/bin/env python3
"""Render a compact context for a human or an AI agent."""
import json, sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_context.py REGISTRY.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for item in data.get("items", []):
        print(f"{item.get('id')} | {item.get('kind')} | {item.get('state')} | priority={item.get('priority')}")

if __name__ == "__main__":
    main()
