# Operating the reference kit

## One workspace

Run from the repository checkout:

```bash
python3 kit/refresh.py examples/minimal
```

The command reads `registry.toml` and source documents, then writes derived
files under `examples/minimal/generated/`:

- `registry.json`: validated declarations;
- `observations.json`: heuristic signals, marker configuration, and UTC time;
- `context.txt`: compact context for a terminal or prompt;
- `context.json`: machine-readable context;
- `context.html`: human-readable table;
- `manifest.json`: generated artifact list and generation time.

Generated files are disposable. Do not edit them or treat them as authorities;
edit the declarations and source documents, then refresh again.

## Several workspaces

```bash
python3 kit/portfolio.py \
  examples/portfolio/team-alpha \
  examples/portfolio/team-beta \
  --output portfolio-generated
```

The portfolio is a snapshot, not a live database. Compare the per-workspace
`observed_at` values before treating its rows as simultaneous. A row with
`source_match=ambiguous` or `source_match=none` needs a declaration review.

By default, each workspace receives a `generated/` directory. Use
`--workspace-output-root` when the source workspaces must remain untouched or
are mounted read-only.

## Scheduling

Schedule the complete `refresh.py` command, not a renderer alone. The supplied
systemd-user and Windows examples use that contract. A failed scheduled run
should be investigated from its exit code and logs; an old generated file is
not evidence that the source was successfully observed.

## Freshness and confidence

`observed_at` records when the observer ran. It does not validate the truth of a
source. Signals are heuristic, and absence of a signal is not proof that no
work remains. Human review remains the authority for lifecycle decisions.
