# CAI1.15 — Propagate the program into the index documents (PARTIAL)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Bullet 3: this todo's cross-program notes list the `battle-engine-ssot.md` §4 D15 "clock sources" row as owed to that document's owner | read of `tasks/combat-ai-todo.md` | **already holds** — `tasks/combat-ai-todo.md:771` (was `:281`'s acceptance line pointing at it); no edit needed | `tasks/combat-ai-todo.md` |
| Bullet 1: `docs/DESIGN-GATE.md` §1 gains the "anything that decides what an actor does" row | — | **not run** — `docs/DESIGN-GATE.md` is outside this lane's fence. Filed with the insertion point read (`docs/DESIGN-GATE.md:56`, the BATTLE row) and the required content, in `tasks/combat-ai-todo.md` → "Deferred / named follow-ups" | — |
| Bullet 2: `combat-ai-ideal.md` no longer calls `AdvancedEffectClock` the lawn clock host for triggers | — | **not run** — `docs/architecture/combat-ai-ideal.md` is outside this lane's fence. Filed with the exact line read (`:129`, not `:119`) and the cause (its sibling `combat-ai-map.md:81` already carries the correction) in the same section | — |

`Files:` for this task are `docs/DESIGN-GATE.md`, `docs/architecture/combat-ai-ideal.md` and this todo.
Two of the three are outside this lane's allowed paths, so the achievable part of CAI1.15 is the two
rows above plus confirming bullet 3 already holds. **Both blocked edits are recorded with `file:line` and
the cause read in the owning program's todo, not in this fragment alone** (rules.md rule 2).

## Lane `combat-ai-2` closure (2026-09-20, tip `6811442b`)

Both remaining bullets landed. The two `docs/architecture/combat-ai-ideal.md` edits the previous lane
could not make are in this lane's fence; `docs/DESIGN-GATE.md` is too.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Bullet 1: `docs/DESIGN-GATE.md` §1 gains the decision row | read of `docs/DESIGN-GATE.md:57` | present, inserted immediately after the battle row (`:56`): names `battle-engine-ssot.md` §3c, `combat-ai-map.md` and `combat-ai-ideal.md`, and states the closed vocabularies with counts **read from code**, not from the plan | `docs/DESIGN-GATE.md:57` |
| The counts are code's counts, not prose | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~_has_"` | **168 passed, 0 failed** — every count pinned: `TargetSelector_has_eight_members`, `AiTier_has_two(_members)`, `AiPlace_has_four`, `AiRole_has_four`, `AiRowCondition_has_six`, `AiCensusCondition_has_five`, `PersonalityAxis_has_four(_members)`, `AiActorClass_has_two_members`, `ScoreTerm_has_seven_members`, plus the two pins added here | `CandidateScorerTests.cs`, `ResolvableHereTests.cs` |
| Two missing count pins | same run | added — `SelectionMode_has_two_members`, `Resolvability_has_three_members`, each with its reason in the test | — |
| Bullet 2: the ideal names the right clock | read of `docs/architecture/combat-ai-ideal.md:129` | `AdvancedEffectClock` (`EffectRuntime.cs:42,133`) is now called the **wall-clock-seeded status-expiry** clock and NOT the decision clock; scheduling names `KernelDriveHost.NowTicks` / `SimulationClock`; matches its sibling `combat-ai-map.md:81` | `docs/architecture/combat-ai-ideal.md:129` |
| Bullet 3 | read of `tasks/combat-ai-todo.md` cross-program notes | already held (the `battle-engine-ssot.md` §4 D15 "clock sources" row is listed as owed to that document's owner) | `tasks/combat-ai-todo.md` |
| Row's own Verify | `python scripts/audit-doc-citations.py --scope docs/DESIGN-GATE.md --summary` | exit 0 — **0 HIGH** on D1/D2/D3/D4 (28 resolvable citations, 1 document) | — |
| Doc citations re-anchored (DESIGN-GATE grew one row) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, **0 HIGH**. `spec-commander-direct-orders.md` cited `DESIGN-GATE.md:63` x3 → now `:64` | — |

**NOT proved.** Nothing here is a runtime claim; the two documents and the two pins are the deliverable.

**Deliberately left.** `tasks/evidence-fragments/SE0.3.md:6` cites `docs/DESIGN-GATE.md:242-243`; the insert
shifts that to `:243-244`. It is a frozen record of what a past lane read, so it is not re-pointed — the
range still lands inside §5's checklist. Named here rather than silently shifted.
