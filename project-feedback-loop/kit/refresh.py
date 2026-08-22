#!/usr/bin/env python3
"""Run the minimal declaration-to-context pipeline in an isolated output dir."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
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
    html_context = output / "context.html"
    html_context.write_text(subprocess.run([sys.executable, str(ROOT / "render_context.py"), str(registry), "--format", "html"], check=True, capture_output=True, text=True).stdout, encoding="utf-8")
    machine_context = output / "context.json"
    machine_context.write_text(subprocess.run([sys.executable, str(ROOT / "render_context.py"), str(registry), "--format", "json"], check=True, capture_output=True, text=True).stdout, encoding="utf-8")
    manifest = output / "manifest.json"
    artifacts = (registry, observations, context, html_context, machine_context)
    manifest.write_text(json.dumps({"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "artifacts": [p.name for p in artifacts]}, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
