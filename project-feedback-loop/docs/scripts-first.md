# Scripts first, AI optional

The reference workflow is intentionally executable without an AI agent:

```text
declared files and records
        ↓
Python observers and normalizers
        ↓
JSON/TOML/HTML projections
        ↓
human review or optional AI consumption
```

This separation matters. The scripts provide repeatability, scheduling,
provenance, and testability. An AI can help interpret or act on the context,
but it must not be silently treated as the source of truth.
