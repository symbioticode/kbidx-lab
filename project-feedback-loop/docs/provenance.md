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
