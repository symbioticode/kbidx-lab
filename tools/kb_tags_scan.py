#!/usr/bin/env python3
"""Inventory or generate per-project KB tags without touching source files."""
from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path

from kb_tags import build_entries

DEFAULT_EXCLUDES = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist", "build", "generated"}


def project_dirs(root: Path):
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def toml_files(project: Path):
    for path in sorted(list(project.rglob("*.toml")) + list(project.rglob("*.md"))):
        if any(part in DEFAULT_EXCLUDES or "backup" in part.lower() or "archive" in part.lower() for part in path.relative_to(project).parts):
            continue
        yield path


def is_taggable(path: Path) -> tuple[bool, int, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".md" and not (re.search(r"^\s*\[\[?[A-Za-z_][^\n]*\]\]?\s*$", text, re.M) and re.search(r"^\s*id\s*=\s*[\"']", text, re.M)):
            return False, 0, None
        data = tomllib.loads(text)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return False, 0, str(exc)
    count = 0
    for rows in data.values():
        if isinstance(rows, list):
            count += sum(isinstance(row, dict) and "id" in row for row in rows)
    return count > 0, count, None


def scan(root: Path):
    projects = []
    duplicate_ids: dict[str, list[str]] = {}
    for project in project_dirs(root):
        examined = taggable = entries = errors = 0
        files = []
        for path in toml_files(project):
            examined += 1
            ok, count, error = is_taggable(path)
            if error:
                errors += 1
                files.append({"path": str(path), "status": "invalid-toml", "error": error})
                continue
            if not ok:
                continue
            taggable += 1
            entries += count
            files.append({"path": str(path), "status": "taggable", "entries": count})
            try:
                data = tomllib.loads(path.read_text(encoding="utf-8"))
                for rows in data.values():
                    if isinstance(rows, list):
                        for row in rows:
                            if isinstance(row, dict) and "id" in row:
                                duplicate_ids.setdefault(str(row["id"]), []).append(str(path))
            except Exception:
                pass
        if examined or taggable or errors:
            projects.append({"project": project.name, "toml_examined": examined, "files_taggable": taggable, "entries": entries, "errors": errors, "files": files})
    duplicates = {key: value for key, value in duplicate_ids.items() if len(value) > 1}
    return {"root": str(root), "projects": projects, "duplicates": duplicates}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.home() / "Projects")
    parser.add_argument("--output-name", default="tags-kb")
    parser.add_argument("--generate", action="store_true", help="write tags-kb per project")
    args = parser.parse_args()
    report = scan(args.root)
    if args.generate:
        for item in report["projects"]:
            project = args.root / item["project"]
            lines = ["!_TAG_FILE_FORMAT\t2\t/extended format; --format=2/", "!_TAG_FILE_SORTED\t1\t/0=unsorted, 1=sorted, 2=foldcase/"]
            for file_item in item["files"]:
                if file_item["status"] == "taggable":
                    lines.extend(build_entries(file_item["path"]))
            if len(lines) > 2:
                (project / args.output_name).write_text("\n".join(sorted(lines[:2]) + sorted(lines[2:]) ) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
