# Elementary mechanisms

## Drift

```text
local files ────────┐
knowledge base ─────┤
status records ─────┤──> divergent representations
AI sessions ────────┤
dashboard ──────────┘
```

## Declaration

```text
work item → identifier + state + date + source
```

## Observation

```text
sources → rules and signals → heuristic observation → human confirmation
```

## Projection

```text
normalized record
   ├── human HTML view
   ├── machine JSON view (TOML may remain a source format)
   └── compact AI context
```

The reference command is:

```text
python3 kit/refresh.py examples/minimal
        ├── generated/context.html   human view
        ├── generated/context.json    machine view
        └── generated/context.txt     compact context
```

Generated files are excluded from observation. They are projections, never
additional sources of truth.
