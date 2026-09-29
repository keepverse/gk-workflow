# Lane `adg-f4` — an E2E test that fails in the suite and passes alone: make it deterministic

**Session:** `action-dist-gaps-f4` · **Program:** `action-distribution-gaps` · **Mode:** worktree
**Fence:** `gk-core/tests/FusionRpg.E2E.Tests/**`, `tasks/action-distribution-gaps-todo.md`,
`tasks/action-distribution-gaps-ledger.jsonl`, `tasks/sessions/action-dist-gaps-f4.json`, `tasks/reports/**`

## The defect — already measured, do not re-derive it

Row **ADG-F4** in `tasks/action-distribution-gaps-todo.md`:

- in `test-fast.ps1 -AllDefault` the E2E project reads `1 failed, 230 passed`;
- the same test alone (`--filter "FullyQualifiedName~A_real_level_up_grants_a_real_action_row"`) reads
  `Passed! 1/1`;
- the test is `gk-core/tests/FusionRpg.E2E.Tests/UnlockTuningActivationTests.cs:60`.

That is an order/parallelism dependency, not a regression: the test either needs state another test in the same
run leaves behind, or shares state it must not.

## Why it matters

`test-fast.ps1 -AllDefault` green is one of CC8's two halves (the other is a live probe). A test that is green
alone and red in the suite makes the suite unusable as a gate, and "just re-run it" is not a fix.

## Deliverable

1. **The shared state, named by `file:line`** — what this test depends on that another test in the same run
   provides or perturbs (a shared store, a static, a fixture, a parallel-collection neighbour, a temp dir, a
   port, a clock). Reproduce first: show the suite run that fails **and** the isolated run that passes.
2. **The fix at the responsible layer** — give the test its own fixture/store, or establish the precondition in
   its own arrange step. ⛔ Do not fix it by disabling parallelism, by marking it known-red, by deleting it, or
   by weakening its assertion.
3. **Proof it is deterministic** — the E2E project's own suite (whole project, not a filter) green **twice in a
   row**, plus `test-fast.ps1 -AllDefault` with the E2E project green.

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`
- `pwsh -NoProfile -File scripts/test-fast.ps1 -AllDefault`

## Evidence contract (what your report must contain)

- exact command text and the numbers printed for every run above, **including the failing suite run that proves
  the diagnosis**
- the committed artifact (SHA)
- an explicit **NOT-proved** list
- findings routed to the owning todo in the same commit, **with the id asserted present**

## Boundaries

- If the root cause turns out to be **production** state rather than test isolation, say so and route it to the
  owning program instead of papering over it in the test — a test that hides a real ordering bug in production
  code is worse than a red test.
- Your session record's `worktree` path must be **ABSOLUTE**; a relative one makes `verify-change.ps1` exit 1 on
  DRIFT in your own record (measured on lane `isg-gen-fix`).
- The machine may be busy with other lanes. If a suite run reports mass failures within seconds, suspect
  **contention** and re-run when quiet rather than recording it as a defect — measured 2026-09-22: 178
  "failures" in 6 s that were pure contention versus 3 failed / 580 passed in 14 min on a quiet machine.
