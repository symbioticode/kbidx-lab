# Architecture

The system separates authority, knowledge, observation, projection, context,
and scheduling. The minimum implementation is script-based and does not need
an AI agent:

```text
sources → declarations and observations → normalized registry
        → human and machine projections → shared AI context
```

MyCollabIA owns explicit lifecycle decisions. MyKnowledgeBase (KBM/KB) preserves
meaning and provenance. Observers produce signals, not truth. Dashboards and
context files are derived views. A scheduler only starts the refresh command.
An AI agent is an optional consumer of the generated context, not an execution
dependency.
