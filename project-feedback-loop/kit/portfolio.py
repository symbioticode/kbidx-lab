#!/usr/bin/env python3
"""Refresh and aggregate several feedback-loop registries into one portfolio."""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent
PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path, help="directories containing registry.toml")
    parser.add_argument("--output", type=Path, default=Path("portfolio-generated"))
    parser.add_argument("--marker", action="append", dest="markers", help="marker to pass to every workspace refresh")
    args = parser.parse_args()
    workspace_names = [directory.name for directory in args.directories]
    if len(set(workspace_names)) != len(workspace_names):
        parser.error("workspace directory names must be unique")
    items = []
    for directory in args.directories:
        refresh_args = [sys.executable, str(ROOT / "refresh.py"), str(directory)]
        for marker in args.markers or []:
            refresh_args.extend(["--marker", marker])
        subprocess.run(refresh_args, check=True)
        context = directory / "generated/context.json"
        data = json.loads(context.read_text(encoding="utf-8"))
        for item in data.get("items", []):
            copy = dict(item)
            copy["workspace"] = directory.name
            items.append(copy)
    items.sort(key=lambda item: (PRIORITY_ORDER.get(str(item.get("priority", "")).upper(), 3), str(item.get("workspace", "")), str(item.get("id", ""))))
    args.output.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "workspaces": workspace_names, "markers": args.markers, "items": items}
    (args.output / "portfolio.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in ("workspace", "id", "kind", "state", "priority", "signal_count")) + "</tr>"
        for item in items
    )
    table = "<!doctype html>\n<h1>Portfolio context</h1><table><thead><tr><th>Workspace</th><th>ID</th><th>Kind</th><th>State</th><th>Priority</th><th>Signals</th></tr></thead><tbody>" + rows + "</tbody></table>\n"
    (args.output / "portfolio.html").write_text(table, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
