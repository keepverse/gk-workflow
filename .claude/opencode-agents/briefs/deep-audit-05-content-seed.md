# Deep audit retry 05 — one generator/validator closure

## Goal

Audit one representative generated-content pipeline from generator/registry input through emitted artifacts and a consumer. Focus on provenance, deterministic regeneration, vocabulary/schema closure, and validator/test contracts.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/validation-ssot.md`
- `docs/architecture/tunables-ssot.md`
- the selected generator, its registry/seed input, emitted tree, loader, and focused validator/test

## Bounds and method

- Read-only and worktree-local; never hand-edit or regenerate generated data.
- Select one pipeline (items, actions, passive tree, or creatures); do not survey every corpus.
- Do not run generation or a full test suite. Within 18 steps, trace the closure, run one `--check`/focused validator if useful, and write the report.

## Required report

Give the exact SHA; up to five P0-P3 findings with `file:line`, impact, exact evidence, confidence, and falsification; a generator→artifact→consumer closure table; reproducibility/provenance gaps; open questions; and an ordered next plan with stop conditions. `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -12 --oneline -- data gk-forge/tools/seedsmith tools tests`
