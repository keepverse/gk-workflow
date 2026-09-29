# SSH8.5 — publish the derived bore / imbue / forge-gem souls coefficients (materials v6)

The combo-budget report was RED, so R12/R20's publish ran. The report now prices every cell it can:
**0 failing, 126 unpriced**. The only remaining RED cause is the 126 **unpriced** cells — a container whose
grant family has no atom — which is **SSH4.4's** owner-run corpus gap (9 distinct families), not a price.

| Criterion | Command | Result |
|---|---|---|
| publish the derived coefficients | `python gk-core/tools/tuning/publish.py materials operations.bore.souls.coefficient=991 operations.imbue.souls.coefficient=991 operations.forge-gem.souls.coefficient=657 --label "combination pricing (R12, R20)"` | `published materials (v5 -> v6, 3 change(s)); v5 stays on disk for revert` |
| imbue = bore + essence still holds | `python -c "import json;j=json.load(open('gk-core/data/tuning/materials.v6.json'));b=j['operations']['bore'];i=j['operations']['imbue'];print(i['souls']==b['souls'], i['substrate']==b['substrate'], i.get('essence'))"` | `True True {'coefficient': 2, 'variable': 'rung'}` |
| readers switched in the same commit (H7) | `grep -rn "materials.v5.json" src/ tools/ tests/` | none; `SocketTuningFiles.Materials = materials.v6.json`, `brief.py`'s mirror, and the 7 test literals all read v6 |
| the report prices every cell it can | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items combo-budget --report` | **exit 1**, `materials.v6.json`, **0 cell(s) cheaper than the rarity route**, **126 unpriced**; derived `bore 991 / imbue 991 / forge-gem 657` == published |
| named acceptance tests | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~a_gem_only_cell_is_fixed_by_the_derived_forge_gem_coefficient|FullyQualifiedName~a_cell_no_leg_can_move_is_named_not_published"` | **2 passed / 0** (renamed from SSH6.3's `The_derived_forge_gem_coefficient_makes_a_gem_only_cell_pass` / `A_cell_no_lever_can_move_is_listed_by_id`) |
| the Verify filter | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "Category=BalanceGuard&FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus"` | **20 passed / 0** (the row writes `tests\FusionRpg.Core.Tests`; `MaterialCorpusTests` lives in `gk-core/tests/FusionRpg.Core.Items.Tests`, so the intent was run there) |
| no new balance literal | `python gk-core/scripts/audit-magic-numbers.py --summary` | **TOTAL 0** — the pre-existing M2 in `ComboPricingBoot.cs:46` (`TierLadderRungCount = 1`) is FIXED by deriving the count from the loaded ladder (`strainSpliceTuning.TierLadder.Count`), not allowlisted |
| integer overflow | `python gk-core/scripts/audit-overflow.py` | 0 findings |
| boundary | `verify-change.ps1 -Paths @(15 paths) -Session strain-splice-host-20260921` | **exit 1 for the pre-existing reason only**: `test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` (the actions corpus gap, red before this change per SSH2.1/SSH7.1/SSH7.3/SSH8.1 evidence and `tasks/reports/seedsmith-baseline-e0f1375d.json`). `MAGIC-NUMBER GUARD OK`, `DAL GUARD OK`; the checks it never reached were run directly: **Core.Items.Tests 1396/0, Data.Tests 1835/0, Server.Tests 791/0** |
| derivation minimality (found and fixed here) | (above, Core.Items.Tests) | `RequiredCoefficient` rounded through a per-mille factor first, over-deriving by ~1+c/1000 at a large coefficient — the exact repricing exposed it, and the "one below still fails" assertions failed. Now a SINGLE `CeilDiv((need - cannotMove) * current, legTotal)` |

## Not proved / open

- **The acceptance line `combo-budget --report exits 0` does NOT pass while SSH4.4 is open.** Exit 0
  requires the refused-cell count to be 0 as well (`report/cli.py` returns `EXIT_GAP` on `failing or
  refused`), and the 126 unpriced cells need SSH4.4's owner-run corpus regeneration. Erratum requested:
  the line should read "0 failing cells, with refusals attributed to SSH4.4", or SSH8.5 should not close
  until SSH4.4 lands. Everything else in the row is done and green.
- `maxRatioToRarityRouteMilli` is still the plan's default 1000 (no `comboPricing` published) — SSH6.8's
  publish.
- The `The_derived_coefficient_makes_every_cell_pass` double-ceiling property is now exact, so a future
  large-coefficient derivation will not over-price.

## Whole-suite gate (Checkpoint 6) — NOT RUN, and what replaced it

`pwsh -NoProfile -Command "& ./scripts/test-fast.ps1 -AllDefault"` was attempted twice and both runs were
killed by the harness at the long E2E stage (infrastructure interruption, not a test failure — the output
stops at `Test run for ...FusionRpg.E2E.Tests` with no result). The affected boundaries were run directly
instead:

| Boundary | Result |
|---|---|
| `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` | **11055 passed / 0** |
| `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests` | **1396 passed / 0** |
| `dotnet test gk-core/tests/FusionRpg.Data.Tests` | **1835 passed / 0** |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **791 passed / 0** |
| all 33 `tests/FusionRpg.Core.*.Tests` satellite projects (Release build) | **Build succeeded**, 0 errors |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests` | 583 passed / **2 pre-existing, other-owned failures** (`PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`, `ZombossCommanderLevelSingleReaderGuardTests…`) |
| seedsmith pytest (whole project) | 1107 passed / **1 pre-existing failure** (`test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch`, the actions-corpus gap) |

The E2E / FileMove / ItemSeedValidator projects were not re-run; nothing this lane changed reaches them
(no other test project references `SocketTuningFiles.Materials`, `MaterialTuning` or `ComboPricing`).
