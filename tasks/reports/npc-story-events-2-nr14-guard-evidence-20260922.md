# Evidence — npc-story-events NR1.4, the `narrative` guard (its blocked half)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch
`cmdc/npc-story-events-2` (base `57e29b4b3`). Program `npc-story-events`; task
`tasks/npc-story-events-todo.md` NR1.4. Plan decisions: `tasks/npc-story-events-plan.md` §4 D3.

**The base does not carry lane `npc-story-events-1`'s commits** (NR0.2–NR2.1: the boundary rows,
`gk-core/src/FusionRpg.Core/Narrative/**`, `data/tuning/narrative.v*.json`, `tests/**/Narrative/**`). Measured:
`git merge-base HEAD cmdc/npc-story-events-1` = `9b56a8ec1`, `git merge-base --is-ancestor 78bebd0f7 HEAD`
false. So NR1.4's *code* half is absent here and its `narrative-tuning-no-default` row (backed by
`NarrativeTuningTests`, `cmdc/npc-story-events-1:gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeTuningTests.cs`)
cannot land. What this commit lands is the half that was blocked three times: the guard script, its
catalog entry and tier, its invariant row, and the falsifiers that prove it bites.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The guard exists, is catalogued (`ci`, `gating`), and names a row | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~EnforcementRegistryGuardTests"` | `Failed: 0, Passed: 18, Total: 18` (153 ms) — R1/R5/R6/R8 green with the new entry | `gk-core/scripts/enforcement-registry.v1.json` (`narrative`, `guard-narrative-row-map`) |
| It is green on the committed tree (static half) | `python gk-core/scripts/guard-narrative.py` | exit 0, `NARRATIVE GUARD OK - 1 row(s) guarded by 'narrative', 1 mapped` | `gk-core/scripts/guard-narrative.py` |
| The trait filter really selects tests (runtime half, CI's `args.ci`) | `python gk-core/scripts/guard-narrative.py -RunTraitFilter` | exit 0, `gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -> Guard=narrative selected 5 test(s), 0 failed` | same |
| It BITES on a planted violation — a registry row with no map line | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~NarrativeGuardContractTests"` | `Failed: 0, Passed: 5, Total: 5` — 1 control + 3 falsifiers + the committed-tree check; each falsifier asserts the guard's stdout names the violation | `gk-core/tests/FusionRpg.Guard.Tests/NarrativeGuardContractTests.cs` |
| It BITES when a real test loses its trait (plan §4 D3 falsifier 2) | stripped `[Trait("Guard", "narrative")]` from `NarrativeGuardContractTests.cs`, then `pwsh ... -File gk-core/scripts/guard-narrative.py` | exit 1, `mapped test class for row 'guard-narrative-row-map' does not carry [Trait("Guard", "narrative")]: gk-core/tests/FusionRpg.Guard.Tests/NarrativeGuardContractTests.cs`; direct `dotnet test ... --filter "Guard=narrative"` printed `No test matches the given testcase filter` (count 0). Trait restored, guard green again | same file |
| The guard runner runs it in CI mode | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | 22 guards run, 21 exit 0; `narrative ci gating 0 72.0`; the one red is `population-pin 1 110.7` | printed table |
| The one red is pre-existing | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-population-pin.ps1` | `P1 (1 finding(s)) gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:220 Assert.Equal(500, grantedIds.Count) has no pin: marker` — a file this lane never touched (`git status` lists 3 paths) | same |
| Path-owned verification of the two mapped paths | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/scripts/enforcement-registry.v1.json','gk-core/tests/FusionRpg.Guard.Tests/NarrativeGuardContractTests.cs') -AllowUnscoped"` | `enforcement-registry (focused)` + `guard-tests-fallback (module)`; `Failed: 0, Passed: 598, Total: 598` (6 m 5 s) then `Failed: 0, Passed: 18, Total: 18` | — |

**NOT proved / not closable on this base.**

- **NR1.4 stays OPEN.** Its acceptance's `narrative-tuning-no-default` → `["narrative"]` row is backed by
  `NarrativeTuningTests` in lane `-1`; the row id, its map line and its `Guard=narrative` trait must land
  in the commit that brings that test (plan §4 D3). What lands here instead is the row that keeps R8
  honest today: `guard-narrative-row-map` (the guard's own row → test-class map contract), backed by
  `NarrativeGuardContractTests`. Deviation from the plan's "lands in the same commit as the first row
  (`narrative-tuning-no-default`)" — forced by the base, not a re-scope of the plan.
- **The `guard.narrative` verification boundary is not in this tree.** It is NR0.2's `guard-narrative`
  row (`cmdc/npc-story-events-1:gk-core/scripts/verification-boundaries.v1.json`, `level: module`, no
  `verificationId`). Measured here: `verify-change.ps1 -Paths @('gk-core/scripts/guard-narrative.py') -AllowUnscoped -PlanOnly`
  → `VERIFICATION BOUNDARY MISSING: gk-core/scripts/guard-narrative.py` (`scripts/verify-change.ps1:114`). The
  test that makes the flip legal already carries `[Trait("VerificationId", "guard.narrative")]` and
  matches NR0.2's `tests/FusionRpg.Guard.Tests/NarrativeGuard*.cs` glob, so the flip is a two-field edit
  on top of `-1` — adding the row here would duplicate NR0.2's row at merge (the boundary guard refuses
  a duplicated owner pattern).
- **`-Session npc-story-events-2` cannot be used**: `tasks/sessions/npc-story-events-2.json` does not
  exist and `tasks/sessions/**` is not in this lane's allowed paths. The runs above pass
  `-AllowUnscoped`, the script's documented flag for work outside a session record.
- No server was started, no live probe was run, and no narrative engine path was exercised — none exists
  in this tree.
