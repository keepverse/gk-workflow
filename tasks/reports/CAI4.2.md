# CAI4.2 — `lawn-held-actions` A: the per-match frozen sets (Core/Match half)

> **Superseded** by `tasks/evidence-fragments/CAI4.2.md`, written after the manager widened this
> lane's fence to include `tasks/evidence-fragments/**`. Kept because this lane's earlier commit and
> its ledger lines reference it.

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Row: `tasks/combat-ai-todo.md` CAI4.2.
Spec: `docs/architecture/combat-ai/spec-lawn-held-actions.md`.

**Test home, stated:** the row names `tests/FusionRpg.Core.Tests/Match/Ai/LawnHeldActionSetsTests.cs`,
which is outside this lane's fence. New Core tests land in `tests/FusionRpg.Core.Balance.Tests/CombatAi/`
(in fence; the project already hosts this program's decision/schedule policy tests). A new test project
cannot be registered from inside the lane (`FusionRpg.slnx`, `gk-core/scripts/verification-boundaries.v1.json`).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Assembling the same `(basics, liveGrants)` twice yields the same ids in the same order | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnHeldActionSets"` | 11 passed / 0 failed (of which 2 determinism/order) | `LawnHeldActionSetsTests.Assembling_the_same_inputs_twice_yields_the_same_ids_in_the_same_order`, `..._ordered_by_the_shared_tag_preference_not_by_insertion_order` |
| A grant added after the freeze is absent from `Snapshotted()`; present after the next match | same | 11 passed / 0 failed | `A_grant_added_after_the_freeze_is_absent_until_the_next_match`, `BeginMatch_drops_every_freeze_so_the_next_push_assembles_again` |
| N pushes of one key share one `FrozenActionSet`; a Bound key resolves to its own set | same | 11 passed / 0 failed | `Many_push_of_one_key_share_one_frozen_set_and_assemble_once` (`Assert.Same`, `AssemblyCount == 1`, eligibility delegate called once), `A_bound_instance_key_resolves_to_its_own_set_not_its_species_set` |
| No pushed set ⇒ empty held list, never the basic-attack row | same | 11 passed / 0 failed | `A_species_with_no_pushed_set_yields_empty_and_never_a_basic_attack` |
| A compile failure reports once and returns empty on every later call; unknown id refused loudly | same | 11 passed / 0 failed | `Compile_failure_reports_once_and_is_refused_on_every_later_call`, `An_unknown_id_refuses_the_whole_set_rather_than_silently_dropping_it` |
| **Mutation to kill** — make a second push re-assemble | planted `if (false && sets.TryGetValue(...))`, then reverted | **3 tests red** (incl. the named freeze row); green again after revert | run log in the commit body |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | 5 passed / 0 failed | no battle/siege/delve file touched |
| Row Verify line: `verify-change` | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Match/Ai/LawnHeldActionSets.cs','tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs') -Session combat-ai-4` | exit 0, **15560 passed / 0 failed** across 35 project runs | `core-fallback` (module) + `core-balance` (module) |
| Row Verify line: `guard-dal.ps1` | `pwsh -NoProfile -File ./scripts/guard-dal.ps1` | exit 0 — "DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data" | — |
| Full in-fence suite | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests` | 221 passed / 0 failed (was 210, +11) | — |

**Row stays open, by the program's own precedent** (CAI2.5, CAI4.1): the store has no production caller
until CAI4.3 lands `LawnHeldActionRegistry` + the Cold push + `InjectorEntityRegistry.Remove/Clear`
(`gk-fusion/src/FusionRpg.Injector/**`, `gk-core/src/FusionRpg.Server/**` — outside this lane's fence). All five of this
row's acceptance lines are met and run; the wire is CAI4.3's.
