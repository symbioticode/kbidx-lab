#!/usr/bin/env python3
"""Render a compact context for a human or an AI agent."""
import argparse
import html
import json
from pathlib import Path

def enrich(items: list[dict], signals: list[dict]) -> list[dict]:
    by_name: dict[str, int] = {}
    for signal in signals:
        name = Path(signal.get("source", "")).name
        by_name[name] = by_name.get(name, 0) + 1
    declared: dict[str, int] = {}
    for item in items:
        source = Path(str(item.get("source", ""))).name
        declared[source] = declared.get(source, 0) + 1
    enriched = []
    for item in items:
        copy = dict(item)
        source = Path(str(item.get("source", ""))).name
        copy["signal_count"] = by_name.get(source, 0) if declared.get(source) == 1 else 0
        copy["source_match"] = "unique" if declared.get(source) == 1 else "ambiguous"
        enriched.append(copy)
    return enriched


def render_text(items: list[dict], signal_count: int) -> str:
    return f"observations: {signal_count}\n" + "".join(
        f"{item.get('id')} | {item.get('kind')} | {item.get('state')} | priority={item.get('priority')} | signals={item.get('signal_count', 0)}\n"
        for item in items
    )


def render_html(items: list[dict], signal_count: int) -> str:
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in ("id", "kind", "state", "priority", "signal_count")) + "</tr>"
        for item in items
    )
    return "<!doctype html>\n<h1>Feedback context</h1><p>Observations: " + str(signal_count) + "</p><table><thead><tr><th>ID</th><th>Kind</th><th>State</th><th>Priority</th><th>Signals</th></tr></thead><tbody>" + rows + "</tbody></table>\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--format", choices=("text", "html", "json"), default="text")
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    observations = json.loads(args.observations.read_text(encoding="utf-8")) if args.observations else {"signals": []}
    signals = observations.get("signals", [])
    items = enrich(data.get("items", []), signals)
    if args.format == "html":
        print(render_html(items, len(signals)), end="")
    elif args.format == "json":
        print(json.dumps({"schema_version": data.get("schema_version", 1), "observation_count": len(signals), "items": items}, indent=2, sort_keys=True))
    else:
        print(render_text(items, len(signals)), end="")

if __name__ == "__main__":
    main()
