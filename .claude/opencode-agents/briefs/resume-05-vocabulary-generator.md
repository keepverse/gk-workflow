# Resume P1 05 — generated vocabulary and closure

## Goal

Close the confirmed passive-tree vocabulary drift and the FamilyExpandGen closure gaps without hand-editing generated data. Fix the generator/mirror/check path first, regenerate through the owning tool, and leave CI wiring for the verification-topology follow-up if its path is actively owned elsewhere.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/architecture/validation-ssot.md`
- `docs/architecture/tunables-ssot.md`
- `docs/architecture/creature-seed-map.md`
- `docs/architecture/effect-atom/atom-catalog-ssot.md`
- current FamilyExpandGen/PassiveTreeRosterGen code, registries, emitted data, and focused tests

## Allowed paths

- `gk-forge/tools/FamilyExpandGen/**`
- `gk-forge/tools/PassiveTreeRosterGen/**`
- `gk-data/packs/fusion/data/seed/passive-tree/vocabulary.json`
- `gk-data/packs/fusion/data/seed/atoms/generated/**`
- `gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/**`
- `gk-core/tests/FusionRpg.Core.Tests/**` only for directly affected vocabulary/atom tests

## Requirements

1. Make `PassiveTreeRosterGen --atom-vocab-check` agree with the live registries; regenerate the mirror from the generator, never hand-edit emitted JSON.
2. Make FamilyExpandGen refusal, pool, version-selection, and provenance closure explicit; add fixtures for v10/version ordering and durable refusal/reconciliation behavior.
3. Identify stale real-corpus fixtures and update them through their owning fixture/generator path; do not weaken a vocabulary test.
4. If `.github/workflows/ci.yml` is actively owned by another lane, do not touch it; write a precise handoff row naming the missing CI command and owner.
5. Run both `--check` modes and focused tests. Report any remaining registry/CI owner blocker explicitly.

## Evidence/report contract

Regenerate only through tools. Report full SHA, changed files, exact generation/check/test commands and counts, provenance evidence, open questions, and next plan. Leave dirty for manager review; no commit/push/merge.

## Verification

- `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check`
- `dotnet run --project gk-forge/tools/PassiveTreeRosterGen -- --atom-vocab-check`
- `dotnet test gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests --no-restore`
- `git status --porcelain`
- `git rev-parse --short HEAD`
