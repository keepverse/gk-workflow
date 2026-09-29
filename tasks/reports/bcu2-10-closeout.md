# BCU2.10 close-out — the lane-side half, and what the 2026-09-21 attempt actually landed

Lane `cmdc/bcu8-4` (fence: `gk-core/src/FusionRpg.Data/**`, `gk-core/tests/FusionRpg.Data.Tests/**`,
`tasks/backlog-clean-up-todo.md`, its ledger, `tasks/data-test-substrate-todo.md`, `tasks/reports/**`,
`scripts/**`). Base `a4385c7dd6d3`.

## The row is a manager-run job, in flight — not a lane job

`tasks/run-board-20260920.md:1560` — *"`BCU2.10` — launched as a manager-run detached job (preflight
GREEN, all seven checks; resumed round-1 in its own worktree)"* — and the 2026-09-23 board entry
`2004b5a42` (on `features/mega-merge`, not at this base) — *"three-running-one-gated: `BCU2.10` running
(action round-1, resumed) · `BCU2.12` running (`[134/904]`) · `BCU2.13` running (108 species) ·
`BCU2.11` defect-gated"*. Its outputs are `gk-data/packs/fusion/data/seed/actions/**`, outside this lane's fence, so the lane
must not run it. The lane-reachable half is the reading below.

## Finding — the 2026-09-21 round-1 commit claims readings its artefact does not carry

`710390b56`'s body: *"generate_action_pipeline --round 1 …, then usage stats and the round-1 coverage
report, committed as one unit (T4.6). Readings recorded, never asserted: accepted size, thinCell
shortfall delta and quotaDrift are in `tasks/reports/BCU2.10-round-1.json`."* The commit changed exactly
two files:

| path | change |
|---|---|
| `gk-data/packs/fusion/data/seed/actions/_generated/characteristic-pool.json` | one string: `action-rungs.v1.json` → `v4.json` |
| `tasks/reports/BCU2.10-round-1.json` | 10 lines — `job` / `report` / `topLevelKeys`; **no readings** |

No pipeline output moved: `_rounds/round-1/accepted.json` was last written 2026-09-16 (`094ca0286`),
`_reports/coverage-round-1.json` 2026-09-19 (`e6324de18`), `committed-round-1.json` 2026-09-15
(`15497ee32`) — all **before** the 2026-09-21 replan (`c52697a4a`) and the run; and
`generate_usage_stats --write` (`generate_usage_stats.py:75-77`) writes `_reports/_usage-{date}.json`,
which exists in no branch's history. So the row's acceptance (*"round-1 report written; accepted size /
thinCell shortfall delta / `quotaDrift` clean recorded"*) was not met by that commit — the same class as
the claimed-write-that-did-not-land notes in `tasks/item-seedgen-todo.md` (ISG-gap-1's erratum) and
`tasks/action-distribution-gaps-todo.md` (ADG-F4). The artefact is deliberately left untouched: it is
the evidence.

## Readiness, re-checked at this head (`9541f1f2c`)

The run's own model-free preflight was re-run here rather than trusted from `BCU2.10-preflight.json`
(2026-09-21) — it is the gate that decides whether the in-flight job can spend model time, and it is the
kind of check that went stale once already (ADG-F1):

```
PYTHONPATH=gk-forge/tools/seedsmith python gk-forge/tools/seedsmith/action_run_preflight.py
[OK ] endpoint+model: http://localhost:1234/v1/models lists google/gemma-4-26b-a4b-qat
[OK ] vocab.TAGS: 9 tags, missing [] / extra []
[OK ] tuning mode: mode='full' version=3
[OK ] quality gate: coverage-round-1.json passing=True
[OK ] plan freshness: committed=188e8625f6e4… fresh=188e8625f6e4…
[OK ] pipeline accepts the plan: no stale-hash refusal
[OK ] pipeline dry-run: stops only on absent candidate scratch
preflight GREEN        (exit 0)
```

## The reading the acceptance needs — baseline, reproducible

```
PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-10-readings.py --out tasks/reports/bcu2-10-readings.json
```

| reading | value |
|---|---|
| accepted size | **181** (`corpusHash 9c8ff5b7…`) |
| thinCell shortfall | **20,384** over 48 thin cells of 48 |
| `quotaDrift` | **clean** — evaluated, not among the 4 gap metrics (`atomFamilyNamespace`, `enablerPayoffCoverage`, `speciesCoverage`, `thinCell`) |
| verdict / review queue | `pass` / 0 |
| next-round targets | 5,387 |
| committed report | same corpus hash and the same 20,384; the tool's live doc differs only by `+1` quota on 12 non-thin cells (from the replan) |

The command runs the coverage tool's own `--dry-run` path: **writes nothing tracked** (`git status
--short` unchanged apart from this lane's own files). Re-run it after the in-flight run for the delta.

## The item after it — BCU2.11's board line is stale on the criterion it names

`tasks/run-board-20260920.md:1563` gates BCU2.11 on its `SetCompletability` GAPs. Measured at this head:

```
cd gk-forge/tools/seedsmith && PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --metric Linkage/SetCompletability
→ no findings        (exit 0)
```

`tasks/item-seedgen-todo.md` ISG-gap-1 already records the 30 → 0 fix and asks for an erratum (the row's
own verify was measured on the unmerged `corpus/bcu211`). The gate that *is* real is ISG-gap-2's
correction (2026-09-22, same file): the BCU2.11 corpus **does not fill** the 911 `Coverage/EmptyPartition`
gaps and adds **747 near-duplicates**, which is why `ea2aeb756` reverted it (956 files, −130,881). That
closes by fixing the generator under `gk-forge/tools/seedsmith/**` — outside this lane's fence. `BCU2.12` is
running (`:1562`); `BCU2.13` is `ep2-1`-gated at this base (`:1565`) and launched per `2004b5a42`. All
four are manager-run model jobs; no lane can close them.

## The top-up half (T4.7–T4.10): the committed round-2 report cannot be its baseline

BCU2.10's title includes "then top-up rounds per its todo", and T4.7's own instruction is *"per round N:
T4.1 CLI plans `_briefs/round-N.json` from round N−1's report"*. Read model-free at `53ce6ef60`
(`python tasks/reports/bcu2-10-readings.py --round 2 --out tasks/reports/bcu2-10-readings-round-2.json`):

| reading | fresh `--round 2 --dry-run` at this head | committed `_reports/coverage-round-2.json` |
|---|---:|---:|
| accepted corpus | **181** (`corpusHash 9c8ff5b7…`) | **24** (`corpusHash 0f8c6c83…`) |
| tuning version | **3** | **2** |
| thinCell shortfall | **20,384** over 48 thin cells | **639** over 45 thin cells |
| entries | 5,435 | 237 |
| verdict | `pass` | `not-clean` |

So the round-2 report on disk describes a **different corpus generation** — 24 accepted rows at tuning v2,
not 181 at v3 — and its 639 shortfall is not comparable to the current 20,384. The first top-up round must
be planned from the *current* round-1 report; the committed round-2 report has to be regenerated by the run
(a `gk-data/packs/fusion/data/seed/actions/**` write, so the manager's), and reading it as a baseline would silently compare two
different corpora. That is the same staleness class ADG-F1 already cost this program once, and it is why
this lane records the fresh dry-run beside the committed file rather than only the dry-run.

Note what a fresh round-2 reading that equals round 1's does *not* mean: 181 accepted, 20,384 shortfall and
the same four gap metrics on both rounds is not "round 2 changed nothing" — the targets are derived from
the same corpus, so until a top-up round writes rows the two readings must agree.

