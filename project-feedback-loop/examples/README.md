# Examples

These fixtures are deliberately small and anonymized.

## `minimal/`

One registry contains three kinds of tracked unit: a project, a change ticket,
and a knowledge article. The project and ticket source files contain heuristic
markers; the article does not. Run:

```bash
python3 kit/refresh.py examples/minimal
```

Inspect `examples/minimal/generated/context.html` for the human view or
`context.json` for the machine view.

## `portfolio/`

`team-alpha/` and `team-beta/` demonstrate aggregation across workspaces:

```bash
python3 kit/portfolio.py \
  examples/portfolio/team-alpha \
  examples/portfolio/team-beta \
  --output portfolio-generated
```

The generated portfolio keeps the workspace, priority, signals, freshness, and
source-match status for every item. `portfolio-generated/manifest.json` is the
completion marker and lists the two complete portfolio views. Generated
directories are ignored by Git.
