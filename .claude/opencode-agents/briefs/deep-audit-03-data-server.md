# Deep audit retry 03 — one real Data-to-Server path

## Goal

Audit one concrete write/read path from an HTTP or SignalR entry point through Contracts, Server service, FusionRpg.Data, SQLite schema, and normal read-back. Focus on identity, migration/closure, transactions, reconnect, and test realism.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/data-architecture.md`
- `docs/architecture/standalone-rpg-map.md`
- `docs/contributing/testing-standard.md`
- the source and focused tests for the selected path

## Bounds and method

- Read-only and worktree-local; no edits, database files outside the worktree, commits, deployment, or background tasks.
- Select one high-risk path (actor/empire/save/unique state is acceptable) rather than surveying every store.
- Do not run the full Data/Server suite. Within 18 steps, trace the path, inspect one adversarial test or schema check, and write the report.

## Required report

Give the exact SHA; up to five P0-P3 findings with `file:line`, impact, exact evidence, confidence, and falsification; a write/read/migration/test closure table; open questions; and an ordered next plan with stop conditions. `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -12 --oneline -- gk-core/src/FusionRpg.Data gk-core/src/FusionRpg.Server tests`
