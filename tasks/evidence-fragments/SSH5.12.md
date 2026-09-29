# SSH5.12 — `resocket --write` over `gk-data/packs/fusion/data/seed/items/base-types/**` (owner-run, manager-executed)

**Owner authorization:** asked in conversation 2026-09-21 and answered **"Run SSH5.12 now"** (the other
option was to decline and keep the subset contract). The delta written by lane `ssh27` and sent to the
owner's answer read: *"I dispatch the ask-first corpus rewrite as a detached job with a report artefact,
then SSH5.13 after it."*

**Why the manager executed it and not a lane:** the row is `OWNER-RUN`, and the lane that owns the surface
had gone unresponsive — `ssh27` was taking a `continue`, spending `input 983 / output 3` tokens per segment
with `exitCodes [0,0,0]` and a green verify, i.e. it started, emitted nothing and exited. Waiting on it had
already failed once (the authorization was issued at ~09:35 and by 11:52 nothing under
`gk-data/packs/fusion/data/seed/items/base-types/**` had changed). So the owner's job ran on the manager's own plane (d).

## Preflight — the condition the authorization was given against

| Step | Command | Result |
|---|---|---|
| dry run (re-printed before writing) | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith.adapters.items.basetypegen.resocket --dry-run` | exit 0, **total 1158 / unchanged 321 / resocketed 837** — identical to the reading the owner authorized against |

## The write

| Step | Command | Result |
|---|---|---|
| write | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith.adapters.items.basetypegen.resocket --write` | exit 0; the verb printed two JSON documents (plan, then write summary) carrying the same 1158/321/837 |
| corpus touched | `git status --porcelain gk-data/packs/fusion/data/seed/items/base-types \| wc -l` | **60 files** |
| only `socketMax` moved | `git diff -U0 gk-data/packs/fusion/data/seed/items/base-types` field census | `1674 "socketMax":` lines, plus 60 each of `batch`/`authoredUtc`/`note`/`model`/`promptVersion`/`sourceRef`/`entries` — the per-file `_meta.amendments` record. **No identity field** (`id`, `nameKey`, `name`, `class`, `band`, `implicit`, `enhanceTrack`, `tags`, `flavor`) appears in the diff |

## Verify lines from the row

| Check | Command | Result |
|---|---|---|
| validator, incl. the row's `no_base_type_exceeds_its_role_ceiling_after_resocket` | `dotnet run --project gk-forge/tools/ItemSeedValidator` | **PASS — 3957 entries across 1013 files, 2591 warnings**, exit 0, and **0** `SocketMax`/`SocketCeiling` findings |
| seedsmith corpus gate | `cd gk-forge/tools/seedsmith; python -m seedsmith check ../../data/seed/items --adapter items --gate` | exit 0 — `57 gap, 598 note, 153 not_measured` (the `not_measured` rows are `PipelineHealth/*` needing `creature_anchors`, unrelated to sockets) |
| Core contract tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid\|FullyQualifiedName~BaseTypeCorpus"` | **30 passed / 0 failed** |
| seedsmith base-types generator tests | `python -m pytest gk-forge/tools/seedsmith/tests/test_base_types_gen.py -q` | **69 passed** |
| SP contract test | `python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | **1 failed / 68 passed** — see below; this is the row's *next* acceptance line, not a corpus defect |

## The one failure, and why it is the row's next step rather than a broken write

`ChassisTests.test_the_corpus_host_set_is_a_subset_of_the_tuning_host_set_and_no_row_exceeds_its_ceiling`
fails at its **last** assertion, after the two contract assertions have passed:

```
base-type role X socketMax n exceeds its ceiling c        -> NOT raised (no row exceeds its ceiling)
self.assertEqual(wanted, max(by_role.values()))           -> AssertionError: 4 != 8
```

`wanted` is `socketCeiling`'s `strainSplice.ingredientCount` (**4**); the corpus's maximum `socketMax` is now
**8**, because v2 widened the role ceilings and the re-stamp is what lets rows reach them. The test's own
docstring says *"Subset is the default until SSH5.12's re-stamp tightens it to equality"* — so the clause
asserting the corpus tops out at the ingredient count is the pre-restamp invariant, and SSH5.12's second
acceptance line ("the follow-up agent edit tightens SSH5.1's corpus contract from subset to
`the_corpus_host_set_equals_the_tuning_host_set` in C# and Python, and it is green") is the change that
replaces it. It must move in **the same commit** as the corpus, or the corpus lands with a red test.

## Second acceptance line (lane `ssh28`, 2026-09-21)

SSH5.1's corpus contract tightened from **subset** to `the_corpus_host_set_equals_the_tuning_host_set` in
both ports, keeping the "no row exceeds its role ceiling" clause. The stale
`self.assertEqual(wanted, max(by_role.values()))` clause (corpus tops out at `ingredientCount` — the
pre-restamp invariant) is the assertion the re-stamp invalidates; it is replaced by two-sided set equality.
The corpus now reaches 4+ in exactly 11 roles, and the v2 ceiling table admits exactly those 11
(`socketCeiling ≥ strainSplice.ingredientCount`): the two sets are equal, which is the point of the re-stamp.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Python contract equals the tuning host set, no row above its role ceiling | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | **69 passed** in 7.16s | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` (`test_the_corpus_host_set_equals_the_tuning_host_set_and_no_row_exceeds_its_ceiling`) |
| same contract, C# port | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~BaseTypeCorpus"` | **30 passed / 0 failed**, 322 ms | `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs` |
| the row's whole filter set (adds `Combination`) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~BaseTypeCorpus|FullyQualifiedName~Combination"` | **154 passed / 0 failed** | — |
| combogen parity | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **27 passed** | — |
| validator against the re-stamped corpus + v2 | `dotnet run --project gk-forge/tools/ItemSeedValidator` | **PASS — 3957 entries across 1013 files, 2591 warnings**, 0 `SocketMax` findings | — |
| scoped verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py','tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs') -Session strain-splice-host-20260921"` | exit 0 — plan: `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs -> core-tests-fallback (module)`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -> seedsmith-tests (focused)`; **pytest 69 passed**; `FusionRpg.Core.Tests` **15075 passed / 0 failed** | — |
| 21-guard CI tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | **18 gating green, 3 red** — all three pre-existing at the base `5f51d6fcd492` and outside this change (see below) | — |
| doc citations, strict | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1: 1681 documents / 24920 citations checked, **21 HIGH in 8 docs — 0 anywhere under `strain-splice-host/`** | — |
| ledger integrity | `python gk-core/scripts/anchor-ledger.py tasks/strain-splice-host-ledger.jsonl check` | exit 0 | — |

### The three red guards are not this change's

`git diff --stat` at commit time is the two test files plus `tasks/**`; `git status` is clean for every file
the three guards name, so each finding is byte-identical at the base.

- `guard-doc-citations.ps1` — 21 HIGH, all in `notification-ssot-ideal.md` (12), `spec-petition-host.md` (2),
  `trade-surface-map.md` (2), `spec-legion-count-cost.md` (1), `spec-notify-vocabulary.md` (1),
  `spec-trade-click-budget.md` (1), `spec-trade-notify.md` (1), `spec-world-notify.md` (1). This class is
  already recorded at `tasks/multi-lane-handoff-20260920.md:92`, and the `notifyRailStore.ts`/`categories.ts`
  renames at `tasks/notification-ssot-todo.md:491` and `tasks/npc-story-events-todo.md:1253`.
- `guard-magic-numbers.ps1` — **M1=2**, both `new(64)` scratch-buffer capacities at
  `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:76,77`. Routed: row **CAI-guard-2** in
  `tasks/combat-ai-todo.md` (that program's own acceptance at `:98`/`:323` requires no
  `audit-magic-numbers.py` row for `Actions/Ai/`).
- `guard-population-pin.ps1` — **P1=1**, `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs:400`
  `Assert.Equal(32, result.Count)` restates the `cap` argument two lines above; the file is scanned as
  content-reading because of its own `FindRepoRoot()` helper at `:456`. Routed: row **CAI-guard-3**.

## NOT proved / open

- ~~**The contract tightening (SSH5.12's second acceptance line) is NOT done here**~~ — **done in this
  fragment's second section** (lane `ssh28`); the row closes with this commit.
- The three red CI guards above are unchanged by this lane; they are reported with file:line and routed, not
  fixed here (two own rows, **CAI-guard-2**/**CAI-guard-3**, in `tasks/combat-ai-todo.md`; the doc-citation
  class already filed).
- **`SSH5.13` (the R11 re-run) has not been run** — it is the next owner-authorized step and needs this
  corpus in the tree first; routed to the same fresh lane as a manager-authorized job.
- The write is committed as the generator's output, never hand-edited; reverting it is `git revert` of the
  corpus commit plus a regeneration.
- No live-game evidence: the re-stamped corpus has not been exercised in a real match (that belongs to CC8's
  live half, which the owner deferred until the suite reds clear).
