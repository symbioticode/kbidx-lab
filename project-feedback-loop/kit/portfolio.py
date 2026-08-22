#!/usr/bin/env python3
"""Refresh and aggregate several feedback-loop registries into one portfolio."""
import argparse
import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parent
PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path, help="directories containing registry.toml")
    parser.add_argument("--output", type=Path, default=Path("portfolio-generated"))
    parser.add_argument("--marker", action="append", dest="markers", help="marker to pass to every workspace refresh")
    parser.add_argument("--exclude-dir", action="append", default=[], help="directory name to skip in every workspace")
    args = parser.parse_args()
    workspace_names = [directory.name for directory in args.directories]
    if len(set(workspace_names)) != len(workspace_names):
        parser.error("workspace directory names must be unique")
    items = []
    observed_at = {}
    markers_by_workspace = {}
    excluded_dirs_by_workspace = {}
    for directory in args.directories:
        refresh_args = [sys.executable, str(ROOT / "refresh.py"), str(directory)]
        for marker in args.markers or []:
            refresh_args.extend(["--marker", marker])
        for excluded_dir in args.exclude_dir:
            refresh_args.extend(["--exclude-dir", excluded_dir])
        subprocess.run(refresh_args, check=True)
        context = directory / "generated/context.json"
        data = json.loads(context.read_text(encoding="utf-8"))
        observed_at[directory.name] = data.get("observed_at", "unknown")
        markers_by_workspace[directory.name] = data.get("markers", [])
        excluded_dirs_by_workspace[directory.name] = data.get("excluded_dirs", [])
        for item in data.get("items", []):
            copy = dict(item)
            copy["workspace"] = directory.name
            copy["workspace_observed_at"] = observed_at[directory.name]
            items.append(copy)
    items.sort(key=lambda item: (PRIORITY_ORDER.get(str(item.get("priority", "")).upper(), 3), str(item.get("workspace", "")), str(item.get("id", ""))))
    args.output.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "workspaces": workspace_names, "markers": markers_by_workspace, "excluded_dirs": excluded_dirs_by_workspace, "observed_at": observed_at, "items": items}
    (args.output / "portfolio.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in ("workspace", "id", "kind", "state", "priority", "source", "source_match", "signal_count", "workspace_observed_at")) + "</tr>"
        for item in items
    )
    table = "<!doctype html>\n<meta charset=\"utf-8\"><style>body{font:1rem system-ui,sans-serif;line-height:1.4;margin:2rem;color:#17202a}table{border-collapse:collapse;width:100%;max-width:110rem}caption{text-align:left;font-size:1.4rem;font-weight:700;margin-bottom:.5rem}th,td{border:1px solid #ccd;padding:.5rem;text-align:left}th{background:#eef2f5}tr:nth-child(even){background:#f8fafb}@media(max-width:40rem){body{margin:.75rem}table{font-size:.85rem;display:block;overflow-x:auto;white-space:nowrap}}</style><h1>Portfolio context</h1><table><caption>Tracked units by workspace</caption><thead><tr><th>Workspace</th><th>ID</th><th>Kind</th><th>State</th><th>Priority</th><th>Source</th><th>Match</th><th>Signals</th><th>Observed at</th></tr></thead><tbody>" + rows + "</tbody></table>\n"
    (args.output / "portfolio.html").write_text(table, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
