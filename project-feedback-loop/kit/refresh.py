#!/usr/bin/env python3
"""Run the minimal declaration-to-context pipeline in an isolated output dir."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parent


def non_empty_argument(value: str) -> str:
    if not value.strip():
        raise argparse.ArgumentTypeError("value must not be empty")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory containing registry.toml")
    parser.add_argument("--output", type=Path, help="generated output directory")
    parser.add_argument("--marker", action="append", dest="markers", type=non_empty_argument, help="marker to observe; repeat for multiple markers")
    parser.add_argument("--exclude-dir", action="append", default=[], type=non_empty_argument, help="directory name to skip; repeat for multiple names")
    args = parser.parse_args()
    source = args.directory / "registry.toml"
    output = args.output or args.directory / "generated"
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "manifest.json"
    manifest_tmp = output / ".manifest.json.tmp"
    manifest.unlink(missing_ok=True)
    manifest_tmp.unlink(missing_ok=True)
    registry = output / "registry.json"
    observations = output / "observations.json"
    subprocess.run([sys.executable, str(ROOT / "registry.py"), str(source), "--output", str(registry)], check=True)
    observer_args = [sys.executable, str(ROOT / "observer.py"), str(args.directory), "--output", str(observations)]
    for marker in args.markers or []:
        observer_args.extend(["--marker", marker])
    for excluded_dir in args.exclude_dir:
        observer_args.extend(["--exclude-dir", excluded_dir])
    subprocess.run(observer_args, check=True)
    context = output / "context.txt"
    render_args = [sys.executable, str(ROOT / "render_context.py"), str(registry), "--observations", str(observations)]
    rendered = subprocess.run(render_args, check=True, capture_output=True, text=True)
    context.write_text(rendered.stdout, encoding="utf-8")
    html_context = output / "context.html"
    html_context.write_text(subprocess.run(render_args + ["--format", "html"], check=True, capture_output=True, text=True).stdout, encoding="utf-8")
    machine_context = output / "context.json"
    machine_context.write_text(subprocess.run(render_args + ["--format", "json"], check=True, capture_output=True, text=True).stdout, encoding="utf-8")
    artifacts = (registry, observations, context, html_context, machine_context)
    manifest_tmp.write_text(json.dumps({"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "artifacts": [p.name for p in artifacts]}, indent=2) + "\n", encoding="utf-8")
    manifest_tmp.replace(manifest)
    print(output)


if __name__ == "__main__":
    main()
