# Registry contract

The registry is a small TOML declaration. Each tracked unit is one `[[item]]`
table:

```toml
[[item]]
id = "CT-2026-014"
kind = "change_ticket"
state = "PROPOSED"
priority = "MEDIUM"
owner = "team"
source = "change-ticket.md"
next_action = "human approval"
```

## Required fields

`id`, `kind`, `state`, and `priority` must be non-empty strings. IDs must be
unique within a registry. The kit does not prescribe one universal lifecycle:
the owner of a workflow chooses the state vocabulary that makes its decisions
explicit.

## Optional fields

`source`, `owner`, `next_action`, `confidence`, `last_review`, `evidence`, and
other fields may be added. They are preserved in the JSON projection. `source`
is special: when present, it identifies the source filename whose observed
signals may be counted for that item.

If two items declare the same source filename, the match is marked
`ambiguous`; if an item has no source, it is marked `none`. Neither case gets an
item-level signal count by accident.

The renderer matches declarations by basename so that a portable declaration
such as `STATUS.md` works across checkouts. If observed signals come from more
than one distinct path with that basename, the result is marked
`source_match=ambiguous` and no signal is assigned. Deployments needing
stronger provenance should use unique source names or replace the renderer with
a path-aware adapter.

## Common kinds

The reference scenarios use:

- `project` for an active body of work;
- `change_ticket` for a proposed or controlled change;
- `knowledge_article` for a KB article whose freshness and provenance matter.

These are conventions, not a closed enumeration. An adapter can add kinds while
keeping the common fields and documenting its lifecycle states.
