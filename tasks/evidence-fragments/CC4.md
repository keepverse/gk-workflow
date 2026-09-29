# CC4 — Layers resolve alone

Plan §6 evidence: "`SP` 6.1 re-bless landed with its explained table; zombie XP credits Zomboss's
empire." Todo's own CC4 maps to `species-progression`'s Checkpoint 2 (`tasks/species-progression-todo.md:308`,
**CLOSED 2026-09-19**) for the SP6.1 half, and Wave 7 `zomboss-commander-clock` (**CLOSED 2026-09-20**,
this same session, `f903dcb3`/`73e3163c`/`46a430de`) for the Zomboss XP-credit half.

| Item | Re-run | Result |
|---|---|---|
| SP6.1 re-bless (`BattleGoldenTests`, `ModeComposeParity`, `AptitudeResolver`, `PointBudget`, `ContributionSourceIds`, `SpeciesAllocationSource`) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests\|...\|FullyQualifiedName~SpeciesAllocationSource"` | **89/89 passed** |
| SP6.1 store-side (`AllocationStore`, `WorldTurn`) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore\|FullyQualifiedName~WorldTurn"` | **39/39 passed** |
| SP6.1's own explained-table commit | `git log` | `eceb08f1` (SP6.1), per Checkpoint 2's own already-verified ancestor chain `a2980c90` (AE1.3) → `283ab83b` (SP1.2) → `eceb08f1` (SP6.1); table in `tasks/evidence-fragments/SP6.1.md` |
| Zombie XP credits Zomboss's empire (`zomboss-commander-clock` SP7.1-SP7.3, this session) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderClock"` | **10/10 passed** — a human `defeat` awards Zomboss's OWN `(SaveId, EmpireId.Zomboss)` commander, never a human row |
| `guard-actor-hub.ps1` | `.\scripts\guard-actor-hub.ps1` | `ACTOR-HUB GUARD OK` |

## Verdict

**CC4 CLOSED.** SP6.1's per-layer resolve is re-blessed and green, and the Zomboss commander clock
(this session's own Wave 7, `zomboss-commander-clock`) delivers "zombie XP credits Zomboss's empire"
exactly as CC4's evidence clause names it — a resolved lawn run's outcome now advances Zomboss's own
empire commander level, never a human row or a by-name legacy row.

Note: this is narrower than `species-progression`'s own full Checkpoint 4 (which additionally requires
module 5's container-delivery work, SP6.10/SP6.11 — recorded **blocked** in that program's own todo on
`empire-progression EP4.13`/`EP4.14`, unrelated to CC4's specific evidence text here). CC4's own plan §6
wording is scoped to SP6.1 + the Zomboss XP credit only, both of which are met.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added by this checkpoint task.
