#!/usr/bin/env python3
"""Render a compact context for a human or an AI agent."""
import argparse
import html
import json
from pathlib import Path

def normalized_source(value: object) -> str:
    return str(value).replace("\\", "/").lstrip("./")


def source_matches(declared: str, observed: str) -> bool:
    declared_normalized = normalized_source(declared)
    observed_normalized = normalized_source(observed)
    if "/" not in declared_normalized:
        return Path(declared_normalized).name == Path(observed_normalized).name
    return observed_normalized == declared_normalized or observed_normalized.endswith("/" + declared_normalized)


def enrich(items: list[dict], signals: list[dict]) -> list[dict]:
    declared: dict[str, int] = {}
    for item in items:
        raw_source = item.get("source")
        if raw_source:
            source = normalized_source(raw_source)
            declared[source] = declared.get(source, 0) + 1
    enriched = []
    for item in items:
        copy = dict(item)
        raw_source = item.get("source")
        source = normalized_source(raw_source) if raw_source else ""
        matching_signals = [signal for signal in signals if source and source_matches(source, str(signal.get("source", "")))]
        matching_paths = {normalized_source(signal.get("source", "")) for signal in matching_signals}
        source_is_ambiguous = "/" not in source and len(matching_paths) > 1
        copy["signal_count"] = len(matching_signals) if source and declared.get(source) == 1 and not source_is_ambiguous else 0
        copy["source_match"] = "unique" if source and declared.get(source) == 1 and not source_is_ambiguous else ("ambiguous" if source else "none")
        enriched.append(copy)
    return enriched


def render_text(items: list[dict], signal_count: int, observed_at: str = "unknown", excluded_dirs: list[str] | None = None) -> str:
    excluded = ", ".join(excluded_dirs or []) or "none"
    return f"observations: {signal_count} | observed_at: {observed_at} | excluded_dirs: {excluded}\n" + "".join(
        f"{item.get('id')} | {item.get('kind')} | {item.get('state')} | priority={item.get('priority')} | signals={item.get('signal_count', 0)}\n"
        for item in items
    )


def render_html(items: list[dict], signal_count: int, observed_at: str = "unknown", markers: list[str] | None = None, excluded_dirs: list[str] | None = None) -> str:
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in ("id", "kind", "state", "priority", "source", "source_match", "signal_count")) + "</tr>"
        for item in items
    )
    marker_text = ", ".join(markers or [])
    excluded_text = ", ".join(excluded_dirs or []) or "none"
    return "<!doctype html>\n<meta charset=\"utf-8\"><style>body{font:1rem system-ui,sans-serif;line-height:1.4;margin:2rem;color:#17202a}table{border-collapse:collapse;width:100%;max-width:90rem}caption{text-align:left;font-size:1.4rem;font-weight:700;margin-bottom:.5rem}th,td{border:1px solid #ccd;padding:.5rem;text-align:left}th{background:#eef2f5}tr:nth-child(even){background:#f8fafb}@media(max-width:40rem){body{margin:.75rem}table{font-size:.85rem;display:block;overflow-x:auto;white-space:nowrap}}</style><h1>Feedback context</h1><p>Observations: " + str(signal_count) + " | Observed at: " + html.escape(observed_at) + " | Markers: " + html.escape(marker_text) + " | Excluded directories: " + html.escape(excluded_text) + "</p><table><caption>Tracked units</caption><thead><tr><th>ID</th><th>Kind</th><th>State</th><th>Priority</th><th>Source</th><th>Match</th><th>Signals</th></tr></thead><tbody>" + rows + "</tbody></table>\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--format", choices=("text", "html", "json"), default="text")
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    observations = json.loads(args.observations.read_text(encoding="utf-8")) if args.observations else {"signals": []}
    signals = observations.get("signals", [])
    observed_at = str(observations.get("observed_at", "unknown"))
    markers = observations.get("markers", [])
    excluded_dirs = observations.get("excluded_dirs", [])
    items = enrich(data.get("items", []), signals)
    if args.format == "html":
        print(render_html(items, len(signals), observed_at, markers, excluded_dirs), end="")
    elif args.format == "json":
        print(json.dumps({"schema_version": data.get("schema_version", 1), "observation_count": len(signals), "observed_at": observed_at, "markers": markers, "excluded_dirs": excluded_dirs, "items": items}, indent=2, sort_keys=True))
    else:
        print(render_text(items, len(signals), observed_at, excluded_dirs), end="")

if __name__ == "__main__":
    main()
