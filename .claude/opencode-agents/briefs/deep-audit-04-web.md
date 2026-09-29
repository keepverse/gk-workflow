# Deep audit retry 04 — web state and contract synchronization

## Goal

Audit one real web state path from Server/API event or query through the client bus/store to a rendered surface. Find stale-cache, ordering, reconnect, loading/error, accessibility, or contract defects that type-checking misses.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/fe-game-foundation.md`
- `docs/architecture/game-gui-principles.md`
- `docs/architecture/actor-hud-ideal.md`
- the selected web source, its API contract, and focused tests

## Bounds and method

- Read-only and worktree-local; no edits, commits, deployment, or background tasks.
- Select one stage or control-room path; do not inventory the entire web tree or run a full suite.
- Within 18 steps, trace the path, run one focused test or static check if useful, and write the report. Do not claim browser behavior without browser evidence.

## Required report

Give the exact SHA; up to five P0-P3 findings with `file:line`, user impact, exact evidence, confidence, and a reproduction step; a state/contract matrix; accessibility and performance risks; open questions; and an ordered next plan with stop conditions. `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -12 --oneline -- gk-web/web/fusion-rpg-web`
