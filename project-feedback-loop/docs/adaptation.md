# Adapting the model

Keep the common fields, then adapt the source readers and state vocabulary.
Possible knowledge layers include Obsidian vaults, MkDocs sites, plain Markdown,
TOML registries, or a database export.

The reference observer reads regular Markdown, TOML, and text files below the
source directory. It skips generated output and symbolic links, so an adapter
that intentionally traverses external sources should make that boundary
explicit and test it.

The scheduler is replaceable. See `schedulers/` for systemd-user, cron,
Windows Task Scheduler, and GitHub Actions examples. Every adapter should call
the complete `kit/refresh.py` pipeline rather than only rendering a previously
generated registry.
