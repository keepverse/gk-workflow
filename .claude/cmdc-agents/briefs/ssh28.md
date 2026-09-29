# Lane brief — `ssh28` · strain-splice-host, taking over from a drained lane

**Program**: `strain-splice-host` (anchor `tasks/strain-splice-host-anchor.md`; todo
`tasks/strain-splice-host-todo.md`; ledger `tasks/strain-splice-host-ledger.jsonl`; specs
`docs/architecture/strain-splice-host/**`).
**Session id**: `strain-splice-host-20260921`. **Branch**: `cmdc/ssh28`, cut from `features/mega-merge`.

## Why this lane exists (and why it is not `ssh27`)

`ssh27` did real work — SSH5.10 (the `sockets.v2` publish + reader flip), SSH5.11 (`resocket` dry-run),
SSH6.1 (circuit-aware geometry) are all merged at the reviewed SHA `4e94fd92` — but it is now **drained**:
each `continue` makes it start, spend `input 983 / output 3` tokens, and exit with `exitCodes [0,0,0]` and a
green verify. It cannot carry the owner-authorized rows any more. Those rows are handed to you, and you take
the lane id `ssh28` so nothing is confused with the drained one.

⚠ **Do not touch `.claude/worktrees/cmdc-ssh27`.** That worktree holds uncommitted `SSH5.10-P2` prose edits
that the drained lane never committed. You work in your own worktree; **redo that row from the row text**
rather than adopting files across worktrees (one writer per worktree).

## The owner's decisions that shape this slice (2026-09-21, given in conversation)

1. **SSH5.12 `resocket --write` was AUTHORIZED and is DONE** — executed by the manager on the owner's behalf
   (`ecf265a9`, 60 corpus files under `gk-data/packs/fusion/data/seed/items/base-types/**`; dry-run re-printed and identical to
   the authorized reading `total 1158 / unchanged 321 / resocketed 837`; validator PASS 3957 entries / 1013
   files / 2591 warnings; Core `StrainSpliceGrid|BaseTypeCorpus` 30/0; seedsmith base-types 69 passed).
   Evidence: `tasks/evidence-fragments/SSH5.12.md`.
2. **SSH5.13 (the R11 re-run) is authorized** and is yours to run.
3. CC8's live half stays deferred until the suite reds clear — not your problem.

## Your slice, in this order

1. **Finish SSH5.12's second acceptance line.** The re-stamp changed the corpus's shape, so the pre-restamp
   clause is now stale: `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py::ChassisTests::test_the_corpus_host_set_is_a_subset_of_the_tuning_host_set_and_no_row_exceeds_its_ceiling`
   fails on its **last** assertion — `self.assertEqual(wanted, max(by_role.values()))` → `AssertionError: 4 != 8`
   (`wanted` is `socketCeiling.strainSplice.ingredientCount` = 4; the corpus now reaches 8 because v2 widened
   the ceilings, which is the point of the re-stamp). Tighten the contract from **subset** to
   `the_corpus_host_set_equals_the_tuning_host_set` in **both** ports — the Python test above and
   `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs` — keeping the "no row exceeds its role
   ceiling" clause. Both must be green, and **SSH5.12's row closes only then**. One commit = one task.
2. **SSH5.13 — the R11 helm-host re-run under v2** (owner-authorized). Run it, report the re-printed report's
   readings, and say explicitly which grid cells remain blocked: that re-print is what makes **R13**
   answerable for the owner, and R13 is currently the owner's oldest open question.
3. **SSH6.2 `ComboPricing`** (M). The term map and design points are already recorded in the lane ledger
   (`ActorPowerCache.Compose`, `PriceReferenceSlate`/`WindowOf`, `MaterialRecipeCatalog.Resolve` +
   `RecipeContext`, `rarityGrant`, `GeometricCombinationCeiling`; `forgeGemRungNote` tier-as-rung; the
   upcycle chain; `ComboRecipe` carries no grants). Implement it: power, price floor, rarity reference, and
   the bound as a **checked `long`** with cross-multiplication (overflow is a RANGE question — widen before
   multiplying; integer overflow throws, never wraps).
4. **SSH5.10-P2** (XS) — the four prose notes from the independent H7 review (stale comments naming v1 or
   the old ceiling 4 in `SocketTuning.cs`, `StrainSpliceTuning.cs`, `RarityBudgetKeys.cs`,
   `SocketProgram`/`Program.cs`; the non-monotonic internal `version` field note; the live
   `strain-splice.v1.json` naming the superseded revision). Redo from the row text.
5. Then your own open rows in `tasks/strain-splice-host-todo.md`, worst-first (SSH6.3+).

## Hard edges

- **Generated data is never hand-edited** — `gk-data/packs/fusion/data/seed/items/**` is seedsmith output; regenerate through the
  generator. `gk-core/data/tuning/**` is authored but published via `gk-core/tools/tuning/publish.py`; **H7**: a publish
  switches its readers in the same commit. A new file under `gk-core/data/tuning/**` or `gk-data/packs/fusion/data/generated/**` needs its
  `boundaries[]` owner row in `gk-core/scripts/verification-boundaries.v1.json` (an `EnforcedRoots` member — the
  manager places rows for files whose fence excludes `scripts/`; ask if you need one).
- **Numeric types**: a magnitude that grows with `Θ` is `long`; integer overflow throws; per-mille math
  divides by 1000 last. No magic numbers on the balance surface — thresholds live in tuning data.
- **Guard files** (`gk-core/tests/FusionRpg.Guard.Tests/**`) are a protected path; if a guard needs editing, say so in
  the fragment and the manager or the pipeline lane carries it.
- **Findings route out**: a finding outside your fence becomes a row in the OWNING program's todo in the same
  commit as the fragment that reports it.
- **`ssh27` is drained, not deleted** — never edit its worktree or its branch.

## Verification

Put the printed numbers in each fragment:

- `.\scripts\verify-change.ps1 -Paths <your real changed paths> -Session strain-splice-host-20260921` —
  run it yourself with real paths; the brief's bullet list is the runner's own verify, so read the **numbers
  printed**, never the exit code alone (TVB-F3: it has printed failing runs and still exited 0).
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~BaseTypeCorpus|FullyQualifiedName~Combination"`
- `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` and
  `.../test_combogen.py -q`
- `dotnet run --project gk-forge/tools/ItemSeedValidator` — must stay PASS (3957 entries / 1013 files / 2591 warnings
  is the current reading)
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` (21 guards) and
  `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`
- `python gk-core/scripts/anchor-ledger.py tasks/strain-splice-host-ledger.jsonl check` after every ledger line

## Evidence contract (binding)

One fragment per task at `tasks/evidence-fragments/<task-id>.md` with `| Criterion | Command | Result |`,
the exact commands, **the numbers printed**, the committed artefact, an explicit **Not proved** list, and
every finding routed to its owning row in the same commit.
