# Project Feedback Loop

![Project feedback loop tests](https://github.com/symbioticode/kbidx-lab/actions/workflows/project-feedback-loop.yml/badge.svg)

How to keep a shared, useful context between humans, local files, scripts, and
optional AI consumers without rebuilding the situation at every session.

## The problem

The starting problem is not “how do we build an automation loop?”. It is the
drift between local files, knowledge articles, status declarations, AI session
context, and the dashboard used by a small team:

- context is updated manually and repeatedly;
- knowledge articles and local files disagree about their state;
- projects and files are not consistently tagged;
- the local agent and brainstorming AI must be given the same background again;
- there is no single visual view of active work, priorities, blockers, and state;
- Git activity is easily mistaken for meaningful work.

This repository shows how small procedures create value first. A feedback loop
appears only after their outputs become useful inputs to one another.

The reference loop does **not** require an AI agent. It runs with deterministic
Python scripts that read declared sources, produce derived views, and record
their outputs. An AI agent may consume the generated context later, but it is
not part of the minimum mechanism.

## Public vocabulary

Private systems are represented here by portable names:

- **MyCollabIA**: the authority that declares collaboration and work states.
- **MyKnowledgeBase**: a knowledge layer implemented with Obsidian, MkDocs,
  Markdown/TOML, or another local tool.

No private project, path, service, or account is required.

## The value flow

```text
declare → observe → normalize → aggregate → project → transmit → review
```

```text
work item → explicit state → observed signals → shared view → AI context
```

The loop is an emergent result, not the product’s only purpose.

## Scenarios

The same tracked-unit model applies to:

1. **Projects** — active, paused, archived work with priorities and pending items.
2. **Change Tickets** — proposed, approved, executing, successful, failed, or
   rolled-back changes with evidence and human gates.
3. **Knowledge Articles / KBM** — draft, active, superseded, archived, or void
   articles with provenance, freshness, and open questions. KBM is used here as
   a generic **KB (knowledge base)** layer, not as a required product.

See [`docs/scenarios.md`](docs/scenarios.md), [`docs/architecture.md`](docs/architecture.md), and [`examples/`](examples/).

## Foundations

The approach is informed by distributed cognition, organizational knowledge
creation, and provenance. See [`docs/foundations.md`](docs/foundations.md) and
[`docs/provenance.md`](docs/provenance.md).

## Getting started

```bash
python3 kit/refresh.py examples/minimal
python3 -m unittest discover -s tests -v
```

The command validates the declarations, observes source files, and writes all
derived artifacts under `examples/minimal/generated/` (which is ignored): a
machine-readable registry and context, heuristic observations, a compact text
context, and a browser-readable HTML table. The reference kit is intentionally
small and replaceable. Adapt the source paths, states, scheduler, and dashboard
to your environment. The individual scripts remain available when a deployment
needs separate stages.

## Windows contributions welcome

The first reference commands use Python and Unix-style examples, but Windows
support is explicitly open to contribution. PowerShell adapters, Windows Task
Scheduler definitions, path handling, Obsidian workflows, dashboard adapters,
tests, and installation notes are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Scope and limits

An observation is a signal, not automatically a truth. A dashboard is a derived
view, not an authority. Provenance makes a result inspectable; it does not make
the source correct. Human review remains necessary for ambiguous states.
