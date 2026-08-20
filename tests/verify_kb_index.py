#!/usr/bin/env python3
"""
verify_kb_index.py — Script de vérification indépendant de kb_index.py.
Importe le code réel de triplet.kb_index (pas de duplication).

Usage :
    cd /home/andrei/Projects/69_CTAGS-KB
    python3 tests/verify_kb_index.py
"""
import json
import sys
from pathlib import Path

# Import du code réel — aucune logique dupliquée
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from triplet.kb_index import (
    ID_LINE_RE, WORD_RE, STOPWORDS, REL_FIELDS, REL_LIST_FIELDS,
    id_line, build_indexes,
)

EXCLUDE_FIELDS = {"id"} | REL_FIELDS | REL_LIST_FIELDS


def main():
    paths = sorted(str(p) for p in Path("corpus/all").glob("*.toml"))
    out = Path("index-run1")
    out.mkdir(parents=True, exist_ok=True)

    by_id, by_term, by_relation = build_indexes(paths)

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
