# Mega-merge QC 9 — strain-splice-host on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Focused suites + engine report. No live game.

## Verdict: GREEN (SSH6.8 publish itself stays deferred — recorded separately)

| Check | Command | Result |
|---|---|---|
| Socket domain (split) | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter FullyQualifiedName~Socket` | 101/101 |
| Socket residual | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~Socket` | 2/2 |
| Engine proof | `python -m seedsmith items combo-budget --report` | exit 0 — PASS, 164 priced, 0 refused |

## Open rows noted, not QC failures

strain-splice-host-todo: 66 done / 9 open — SSH6.8 publish deferred per owner (resume-later note
in row), spec phase approved. No merge-interaction red.

## Fix cycle 8 (2026-09-24) — SSH6.8 publish landed

The deferred SSH6.8 row was implemented and checked here: `sockets.v3.json` published with the passing
report's **copied** `measuredAgainst` (digest `ea0e042f98b0…`), both readers switched to v3 in the same
commit (H7), `ComboBudgetDump` + the report now emit `measuredAgainst`, and the CI
`Category=BalanceGuard` guard (`ComboPricingBoundGuardTests`) recomputes the inequality over the shipped
tuning + corpus. Proof: report exit 0 (164 priced, 0 refused); BalanceGuard 1/1; `ComboPricingTests`
16/16; `ComboPricingBootTests` 3/3; seedsmith `test_combogen`+`test_base_types_gen`+`test_strain_splice_gen`
184 passed. QC 9 has **zero open rows** now.
