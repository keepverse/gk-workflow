# SSH7.1 — the tier ladder: parser half LANDED, the literal-guard half is the pipeline lane's

**Landed:** `TierLadderRung` and the optional `recipe.tierLadder` (`StrainSpliceTuning`), the ladder's five
throw rules, a `SocketTuningFiles.StrainSplice` constant with its readers moved onto it, and 5 tests.
**Not landed:** the literal-guard extension the acceptance's second line names, because its only home is
`gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` — a pipeline-protected path outside this
lane's fence (the same class as SSH6.5 and CAI-guard-1). The row stays OPEN on that one line.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `Parse` reads `tierLadder`; a file with none maps to the ONE-rung ladder v1 implies | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~StrainSpliceGrid\|FullyQualifiedName~ComboPricing"` | **43 passed / 0**. `A_file_with_no_ladder_loads_as_the_one_rung_the_shipped_floor_describes`: the shipped file yields rung 1 whose floors ARE `MinTierPlan` and whose `grantDelta` is 0; a published 2-rung ladder replaces it whole |
| `a_non_ascending_or_non_increasing_ladder_throws` | (above) | floors falling inside one rung, a `grantDelta` that does not rise, a higher rung asking for less, and a floor above `insertTiers.count` — each throws with its own message (all asserted) |
| `a_ladder_whose_top_exceeds_the_atom_ladder_throws` | (above) | the F7 bound read at the top: `top grantDelta + top baseTier + attunedTierBonus` above `FamilyExpansion.TierCount` throws naming `bind no atom` and `never clamp` |
| `a_multi_rung_ladder_needs_measured_combination_pricing` | (above) | the ladder's OWN rung count feeds `ComboPricingProvenance.Check`: two rungs with no measurement → `socket.combo-pricing-unmeasured` naming `2 rungs`; one rung stays unaffected |
| `a_ladder_publish_invalidates_the_previous_measurement` | (above) | measured at `strainSpliceVersion 1`, loaded at 2 → `socket.combo-pricing-stale` naming `strainSpliceVersion measured 1, loaded 2` |
| `SocketTuningFiles` gains the constant, read by the server and mirrored by the combogen reader | `grep -rn '"strain-splice.v' src/ --include=*.cs` | only the constant itself remains as a literal in code: `SocketTuningFiles.StrainSplice` (v1, untouched — the ladder publish is SSH7.7's). `Program.cs` reads the constant; `combogen/tuning.py`'s `STRAIN_SPLICE_PATH` documents itself as its mirror. The two MESSAGES that named the revision at runtime were re-worded to interpolate the constant, so the guard extension has no other offender to report |
| **`every_reader_loads_the_current_strain_splice_revision`** (guard extension) | — | **NOT DONE — blocked**: the file is `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`, a protected path. Recommended shape for the pipeline lane: extend the same literal regex to `strain-splice\.v[0-9]+\.json`, allowlist `SocketTuningFiles.cs` (the constant), and keep the comment-line exemption the guard already has; `combogen/tuning.py` is Python, which that guard does not scan — its own literal is covered by the SSH5.6-style Python scan if it is widened too |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(<7 paths>) -Session strain-splice-host-20260921"` | exit **1** for the pre-existing reason (the `seedsmith-items` focused run stops on `tests/test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch`, 1 failed / 1089 passed, unrelated). Its `DAL` guard printed OK; the two checks it never reached were run directly: **Core 15096 passed / 0** (Release, whole project) and **Server 764 passed / 0** |
| the guard that exists still passes | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | **2 passed / 0** — the sockets half is untouched by this change |
| the generators that read the tuning still pass | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **104 passed** |

## Not proved / open

- The guard extension above — the row's one unmet line, routed to the pipeline lane.
- SSH7.2+ (the matcher returning a rung, the generator emitting no tier numbers, the ladder flip) are
  untouched by this row; the ladder PARSES now, and nothing yet reads a rung above 1.
