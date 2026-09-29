# Lane `cs-f1` — a save that never fused carries layer-1b rows whose seed tree resolves to `SeedTreeNotFound`

**Session:** `creature-seed-csf1` · **Program:** `creature-seed` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Core/**`, `gk-core/tests/FusionRpg.Data.Tests/**`,
`tasks/creature-seed-todo.md`, `tasks/reports/**`

## The defect — measured at the integration head, do not re-derive it

Row **CS-F1** in `tasks/creature-seed-todo.md`:

```
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~After_a_real_boot_a_save_that_never_fused_has_no_layer_1b_rows"
-> Failed! 1/1 in 236 ms
   Assert.NotEqual() Failure: Values are equal — Expected: Not SeedTreeNotFound, Actual: SeedTreeNotFound
```

In the full suite the same project reads `1 failed, 1780 passed`. It was reproduced **in isolation**, so this is
not an ordering or parallelism artefact.

**What it means:** after a real boot, a save that never fused still carries layer-1b rows whose seed tree
resolves to the *absence sentinel* — the ledger records a fusion layer for a save that has no fusion, and what it
records is the sentinel for "there is no tree here".

**Why it is this program's:** the subject is the species-mod ledger's layer-1b rows; neither the test file nor its
project was touched by the round's merges, so this is not merge fallout — it is a condition on the shipped
boot/ledger path.

## Acceptance — and the one route that is closed

The test passes at the integration head, **or** the layer-1b rule it asserts is amended in the owning spec with
the reading recorded. ⛔ **Not by relaxing the assertion**: `SeedTreeNotFound` reaching a ledger row is the defect
the test exists for. Do not delete it, do not weaken it, do not add it to any known-red list, do not skip it.

## Deliverable

1. **The root cause, named by `file:line`** — where a layer-1b row is written for a never-fused save, and where
   the absence sentinel is stored in place of a resolved tree. Say which side is wrong: the row should not exist,
   or the value stored should not be the sentinel.
2. **The fix at the responsible layer** — not a test-side accommodation. If the correct fix is in the boot path
   or the ledger writer, fix it there; if the rule itself is wrong, amend the owning spec in the same commit and
   say exactly why the old rule was wrong.
3. **Proof**: the exact filter above printing `Passed!`, plus the Data suite numbers (total/failed).
4. **Findings** — anything you find that belongs to another program (a `FusionRpg.Core` rule, a boot-path
   concern) is routed to that program's todo, with the id asserted present.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter "FullyQualifiedName~After_a_real_boot_a_save_that_never_fused_has_no_layer_1b_rows"`
- `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

## Evidence contract (what your report must contain)

- exact command text and the numbers printed
- the committed artifact (SHA) and the files in it
- an explicit **NOT-proved** list
- every routed finding's row id, verified present in its file

## Boundaries

- Do not touch `tasks/sessions/**` of other sessions; your own record's `worktree` path must be **ABSOLUTE**
  (a relative one makes `verify-change.ps1` exit 1 on DRIFT in your own record — measured on lane `isg-gen-fix`).
- Generated trees (`gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**`) are never hand-edited: fix the generator and regenerate.
- `gk-core/data/tuning/**` is published as `v{n+1}`, never edited in place.
