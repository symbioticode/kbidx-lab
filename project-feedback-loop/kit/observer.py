#!/usr/bin/env python3
"""Record heuristic signals without modifying the observed source corpus."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MARKERS = ("TODO", "FIXME", "PENDING", "blocked", "en attente")

def observe(root: Path, excluded: Path | None = None, markers: tuple[str, ...] = DEFAULT_MARKERS, excluded_dirs: tuple[str, ...] = ()) -> list[dict]:
    hits = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if any(part in excluded_dirs for part in path.parts):
            continue
        if excluded and (path == excluded or excluded in path.parents):
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".toml", ".txt"}:
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if any(marker.lower() in line.lower() for marker in markers):
                    hits.append({"source": str(path), "line": number, "signal": line.strip()[:180]})
    return hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--marker", action="append", dest="markers", help="marker to observe; repeat for multiple markers")
    parser.add_argument("--exclude-dir", action="append", default=[], help="directory name to skip; repeat for multiple names")
    args = parser.parse_args()
    root = args.directory
    output = args.output or root / "observations.json"
    markers = tuple(args.markers) if args.markers else DEFAULT_MARKERS
    excluded = None
    resolved_root = root.resolve()
    resolved_output = output.resolve()
    if resolved_output.parent == resolved_root:
        excluded = root / output.name
    elif resolved_output.parent.is_relative_to(resolved_root):
        excluded = root / resolved_output.parent.relative_to(resolved_root)
    hits = observe(root, excluded, markers, tuple(args.exclude_dir))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(), "confidence": "heuristic", "markers": list(markers), "excluded_dirs": list(args.exclude_dir), "signals": hits}, indent=2) + "\n", encoding="utf-8")
    print(output)

if __name__ == "__main__":
    main()
