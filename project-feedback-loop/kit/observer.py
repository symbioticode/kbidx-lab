#!/usr/bin/env python3
"""Record heuristic signals without modifying the observed source corpus."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

MARKERS = ("TODO", "FIXME", "PENDING", "blocked", "en attente")

def observe(root: Path, excluded: Path | None = None) -> list[dict]:
    hits = []
    for path in sorted(root.rglob("*")):
        if excluded and (path == excluded or excluded in path.parents):
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".toml", ".txt"}:
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if any(marker.lower() in line.lower() for marker in MARKERS):
                    hits.append({"source": str(path), "line": number, "signal": line.strip()[:180]})
    return hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.directory
    output = args.output or root / "observations.json"
    hits = observe(root, output.parent if output.parent != root else output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(), "confidence": "heuristic", "signals": hits}, indent=2) + "\n", encoding="utf-8")
    print(output)

if __name__ == "__main__":
    main()
