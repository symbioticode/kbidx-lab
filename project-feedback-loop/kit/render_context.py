#!/usr/bin/env python3
"""Render a compact context for a human or an AI agent."""
import argparse
import html
import json
from pathlib import Path

def render_text(items: list[dict]) -> str:
    return "".join(
        f"{item.get('id')} | {item.get('kind')} | {item.get('state')} | priority={item.get('priority')}\n"
        for item in items
    )


def render_html(items: list[dict]) -> str:
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in ("id", "kind", "state", "priority")) + "</tr>"
        for item in items
    )
    return "<!doctype html>\n<table><thead><tr><th>ID</th><th>Kind</th><th>State</th><th>Priority</th></tr></thead><tbody>" + rows + "</tbody></table>\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("--format", choices=("text", "html", "json"), default="text")
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if args.format == "html":
        print(render_html(items), end="")
    elif args.format == "json":
        print(json.dumps({"schema_version": data.get("schema_version", 1), "items": items}, indent=2, sort_keys=True))
    else:
        print(render_text(items), end="")

if __name__ == "__main__":
    main()
