# Deep audit retry 02 — ActorHub, writer, Funnel, and battle seam

## Goal

Audit one narrow, high-risk combat seam end to end: event/delta intake -> EntityStatWriter/Funnel -> ActorHub composition -> battle effect application. Find reachable invariant violations, missing state-entry edges, and tests that cannot falsify them.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/combat-damage-ssot.md`
- `docs/architecture/effect-funnel.md`
- `docs/architecture/actor-hub-ssot.md`
- `docs/architecture/battle-engine-ssot.md`
- the directly called source files and their focused tests

## Bounds and method

- Read-only and worktree-local; no edits, commits, deployment, or background tasks.
- Do not inventory all of Core or run a full suite. Select one concrete path and at most two adjacent failure cases.
- Within 18 steps, inspect the path, run one focused test or static reproduction if useful, and write the report. Stop exploring before the budget boundary.

## Required report

Give the exact SHA; up to five P0-P3 findings with `file:line`, impact, exact evidence, confidence, and a falsification command; an invariant checklist; reachable/unreachable conclusions; open questions; and an ordered next plan with stop conditions. `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -12 --oneline -- gk-core/src/FusionRpg.Core tests`
