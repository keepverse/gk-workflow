# CC1 — Live defects closed

Plan §6 evidence: "each lane's first task green; the four regression tests named in their sub-plans."
Re-run against this session's merged `features/mega-merge` tree (`cmdc/lane-b` @ `a10cd2f9` and later),
not trusted from a checkbox.

| Item | Todo status | Re-run command | Result |
|---|---|---|---|
| `ST2.2` — cost scaled once (`costMulti²` defect) | `[x]` (`tasks/action-skill-tiers-todo.md:23`) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CostLedger\|FullyQualifiedName~ActionCostsCooldownsAdoption\|FullyQualifiedName~ActionCatalog"` | **58/58 passed** |
| `SP0.4` — fusion picks accepted (production-path regression) | `[x]`, Wave 0 **CLOSED** (`tasks/species-progression-todo.md:52,97`) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesModLedger"` | **6/6 passed** |
| | | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies"` | **5/5 passed** |
| `T39` — `craft-assurance` free-ward fix | `[x]` Shipped (`tasks/species-gear-chain-todo.md:36-37`, evidence `tasks/evidence-fragments/T39.md`) | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Workbench"` | **78/78 passed** |
| `TVB0.1` — `release.yml` exit checks | `[x]`, Checkpoint 0 **(parent CC1)** ticked (`tasks/test-verification-boundary-todo.md:14,38-40`) | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorkflowExitCheck"` | **4/4 passed** |

## Verdict

**CC1 CLOSED.** All four named regressions are green on the merged tree, not merely on their own
lane's isolated history — this rules out the specific risk a checkpoint exists to catch: one lane's
fix surviving its own branch but breaking (or never actually landing) once combined with the other
three.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added by this checkpoint task; it only re-runs
existing named test filters and reads existing todo/evidence state.
