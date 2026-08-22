# Adapting the model

Keep the common fields, then adapt the source readers and state vocabulary.
Possible knowledge layers include Obsidian vaults, MkDocs sites, plain Markdown,
TOML registries, or a database export.

The reference observer reads regular Markdown, TOML, and text files below the
source directory. It skips generated output and symbolic links, so an adapter
that intentionally traverses external sources should make that boundary
explicit and test it.

The default markers are `TODO`, `FIXME`, `PENDING`, `blocked`, and `en attente`.
Replace them for another workflow, for example:

```text
python kit/refresh.py examples/minimal --marker NEEDS-REVIEW --marker BLOCKED
```

The scheduler is replaceable. The repository provides systemd-user and Windows
Task Scheduler examples; cron and GitHub Actions can use the same command
contract. Every adapter should call the complete `kit/refresh.py` pipeline
rather than only rendering a previously generated registry.

`portfolio.py` forwards repeated `--marker` options to every workspace and
requires unique directory names so that the aggregated `workspace` field stays
unambiguous.
