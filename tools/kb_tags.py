#!/usr/bin/env python3
"""
kb_tags.py -- genere des lignes compatibles avec le format 'tags' (ctags)
a partir des tables TOML de type [[nom]] qui contiennent un champ "id".

Pourquoi ce script existe : ctags 6.2.1 n'a pas de parseur TOML natif
(une tentative a ete ajoutee puis retiree en 6.2.0 pour bug de boucle
infinie -- cf. docs.ctags.io/en/latest/news/6-2-0.html). Pour un motif
simple sur une seule ligne, un parseur custom ctags (optlib) suffit et
ne necessite aucun script. Pour une structure TOML imbriquee et typee
comme celle-ci, un tout petit script stdlib est plus simple qu'un
optlib ctags multi-table.

Usage:
    python3 kb_tags.py kb.toml >> tags
    sort -o tags tags     # a refaire si le fichier tags doit rester trie

Aucune dependance externe (tomllib = stdlib depuis Python 3.11).
Deterministe, hors-ligne, zero LLM, zero reseau.
"""
import re
import sys
import tomllib

ID_LINE_RE = re.compile(r'^id[ \t]*=[ \t]*"([^"]+)"')


def build_entries(toml_path: str) -> list[str]:
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    entries = []
    for table_name, rows in data.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or "id" not in row:
                continue
            tag = row["id"]
            # Numéro de ligne au lieu d'un pattern : Vim cherche les patterns
            # de tags en mode nomagic (\s y est littéral) -> E434. Le numéro
            # de ligne est la forme la plus robuste (le format 'tags' le
            # supporte nativement).
            line_no = id_line(toml_path, tag)
            fields = "\t".join(
                f"{k}:{str(v).replace(chr(9), ' ').replace(chr(10), ' ')}"
                for k, v in row.items() if k != "id"
            )
            entries.append(f'{tag}\t{toml_path}\t{line_no};"\t{table_name}\t{fields}')
    return entries


def id_line(toml_path: str, tag: str) -> int:
    with open(toml_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if ID_LINE_RE.match(line) and f'"{tag}"' in line:
                return i
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: kb_tags.py <fichier.toml>")
    print("!_TAG_FILE_FORMAT\t2\t/extended format; --format=2/")
    print("!_TAG_FILE_SORTED\t1\t/0=unsorted, 1=sorted, 2=foldcase/")
    for line in build_entries(sys.argv[1]):
        print(line)
