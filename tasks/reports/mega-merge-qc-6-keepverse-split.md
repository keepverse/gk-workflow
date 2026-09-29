# Mega-merge QC 6 — keepverse-split on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Root/guard surface. No live game.

## Verdict: GREEN, no new findings

| Check | Command | Result |
|---|---|---|
| Content-root guard | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter FullyQualifiedName~TestContentRootGuard` | 6/6 |
| Population pin | `python gk-core/scripts/guard-population-pin.py` | exit 0, 0 findings |
| Vocabulary mirror | `python gk-core/scripts/guard-vocabulary-mirror.py` | OK, 9 pairs, no drift |
| Suite-wide root proof | full `gk-core/tests/FusionRpg.Core.Tests` (QC 5) | 9746/9746 — every converted helper resolves on this tree |

Note: a `--filter FullyQualifiedName~Keepverse` run matches zero tests (vacuous pass) — the real
guard class is `TestContentRootGuardTests`. Corrected in this QC; future runs must name it.

## Open rows noted, not QC failures

keepverse-split-todo: 24 done / 16 open blocks (KS-F3 forge roots, L5, guard splits). Program work;
no merge-interaction red.
