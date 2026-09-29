# Mega-merge QC 2 — species-gear-chain (sgc-6) on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Focused suites + CI gate form. No live game.

## Verdict: GREEN, no new findings

| Check | Command | Result |
|---|---|---|
| Items domain | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests` | 1470/1470 (6 s) |
| Seed validator unit | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` | 98/98 |
| CI seedsmith gate (exact CI form) | `python -m seedsmith check --adapter items --gate ../../data/seed/items` (from `gk-forge/tools/seedsmith`) | exit 0 — 931 gap, 612 note, 153 not_measured (readings, gate passes) |

Note: the bare `check gk-data/packs/fusion/data/seed/items` form exits 1 on gap readings; the CI `--gate` form is the binding one and it passes. Gap/note counts are population readings, not failures.

## Open rows noted, not QC failures

species-gear-chain-todo: 37 done / 13 open — 5 owner-review gates (Phases 2–5, sign-off) plus SGC5-F2–F8 findings (generated-actions atom-family gap, dump self-consistency note, missing description, PATH-executable tests, sealed-doc contradictions/counts). Program work for lanes + owner; no merge-interaction red. The merges under QC (7 × `merge(cmdc/sgc-6)`) introduce no red above.
