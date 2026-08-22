#!/usr/bin/env python3
"""Run the minimal declaration-to-context pipeline in an isolated output dir."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory containing registry.toml")
    parser.add_argument("--output", type=Path, help="generated output directory")
    args = parser.parse_args()
    source = args.directory / "registry.toml"
    output = args.output or args.directory / "generated"
    output.mkdir(parents=True, exist_ok=True)
    registry = output / "registry.json"
    observations = output / "observations.json"
    subprocess.run([sys.executable, str(ROOT / "registry.py"), str(source), "--output", str(registry)], check=True)
    subprocess.run([sys.executable, str(ROOT / "observer.py"), str(args.directory), "--output", str(observations)], check=True)
    context = output / "context.txt"
    rendered = subprocess.run([sys.executable, str(ROOT / "render_context.py"), str(registry)], check=True, capture_output=True, text=True)
    context.write_text(rendered.stdout, encoding="utf-8")
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1, "artifacts": [p.name for p in (registry, observations, context)]}, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
