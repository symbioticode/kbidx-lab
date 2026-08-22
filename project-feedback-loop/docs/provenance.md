# Provenance and AI context

Every generated state should be traceable to a source, an observation time, and
the procedure that produced it. A compact AI context should therefore include
the state, source reference, freshness, confidence, and next action.

```text
source → observation → normalized record → projection → agent context
```

The context is a navigation aid. It does not replace the source document or
human review.

The reference observer records `observed_at` in UTC, and `refresh.py` records
`generated_at` in its manifest. These timestamps describe when the procedure
ran; they do not certify that the source declaration was correct.
The observation artifact also records the exact marker list used for the run.
The same timestamp and marker configuration are copied into the rendered
context so that an exported context remains interpretable on its own.

When an observed signal's filename matches an item's declared `source`, the
rendered projections expose that relationship as `signal_count`. Unmatched
signals remain visible in the observation artifact and are not silently
assigned to an item. If more than one item declares the same source filename,
the projection marks the match `ambiguous` and assigns zero item-level signals;
this avoids false certainty.
Items without a declared source are marked `none` and likewise receive no
item-level signal count.

The portfolio projection preserves each workspace's observation timestamp in
`observed_at` and `workspace_observed_at`; it does not pretend that all
workspaces were observed simultaneously.
