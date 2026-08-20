#!/usr/bin/env python3
"""
kb_index.py -- genere by_id.json, by_term.json, by_relation.json
depuis un corpus TOML TI-360. Stdlib seule, deterministe, zero LLM.

Usage:
    python3 kb_index.py corpus/*.toml --out-dir index/
"""
import argparse
import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ID_LINE_RE = re.compile(r'^id[ \t]*=[ \t]*"([^"]+)"')
WORD_RE = re.compile(r"[a-zà-ÿ0-9']+")
STOPWORDS = {"le", "la", "les", "de", "des", "du", "un", "une", "et",
             "que", "qui", "dans", "pour", "sur", "avec", "au", "aux"}
REL_FIELDS = {"source_id", "decision_id", "reunion_id", "instance_id"}
REL_LIST_FIELDS = {"source_ids", "extraction_ids"}


def id_line(path: str, tag: str) -> int:
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if ID_LINE_RE.match(line) and f'"{tag}"' in line:
                return i
    return 0


def build_indexes(paths: list[str]):
    by_id, by_term, by_relation = {}, defaultdict(lambda: defaultdict(int)), {}

    for path in paths:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        for table_name, rows in data.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                rid = row.get("id")
                if not rid:
                    continue

                # by_id
                by_id[rid] = {
                    "fichier": path,
                    "ligne": id_line(path, rid),
                    "table": table_name,
                    "champs": {k: v for k, v in row.items()
                               if k not in {"id"} | REL_FIELDS | REL_LIST_FIELDS},
                }

                # by_term (sur le champ contenu, s'il existe)
                for word in WORD_RE.findall(str(row.get("contenu", "")).lower()):
                    if word not in STOPWORDS and len(word) > 2:
                        by_term[word][rid] += 1

                # by_relation (liens sortants déclarés dans le TOML)
                rel = by_relation.setdefault(rid, {})
                for field in REL_FIELDS:
                    if row.get(field):
                        rel.setdefault(field, []).append(row[field])
                for field in REL_LIST_FIELDS:
                    for target in row.get(field, []):
                        rel.setdefault(field, []).append(target)

    # inversion : ajoute les liens entrants ("reçoit_de") pour navigation bidirectionnelle
    for rid, rel in list(by_relation.items()):
        for field, targets in rel.items():
            for target in targets:
                by_relation.setdefault(target, {}).setdefault("reçoit_de", [])
                if rid not in by_relation[target]["reçoit_de"]:
                    by_relation[target]["reçoit_de"].append(rid)

    return by_id, by_term, by_relation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    by_id, by_term, by_relation = build_indexes(args.files)

    (out / "by_id.json").write_text(
        json.dumps(by_id, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (out / "by_term.json").write_text(
        json.dumps({k: dict(v) for k, v in sorted(by_term.items())},
                    ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "by_relation.json").write_text(
        json.dumps(by_relation, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    print(f"by_id: {len(by_id)} entités | by_term: {len(by_term)} mots | "
          f"by_relation: {len(by_relation)} entités liées")


if __name__ == "__main__":
    sys.exit(main())