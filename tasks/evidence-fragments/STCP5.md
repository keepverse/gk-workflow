# STCP5 — A-G1 is live (program final checkpoint)

**Status: DONE.** Every row holds, including the full suite, which the manager ran in a clean checkout of
this branch at `5867b4e2`.

| Row | Requirement | State |
|---|---|---|
| 1 | The server, the injector and every seedsmith reader load v4, and the guard is green for `action-rungs` (and `action-base` once ST5.4 lands) | **GREEN.** v4 exists (published at the report's `referencePower` 1512) and all **ten** non-comment `action-rungs.v<n>.json` readers in the guard's scan roots name it — `Program.cs`, `RpgHost.cs`, `pool.py` ×3, `generate_validate_heal.py` ×2, `generate_distribution_planner.py` ×2, `derive.py` ×1. A scan of both roots returns exactly one version, `{4: 10}`. The guard filter is **9/9**, with `action-rungs` **and** `action-base` in `AgreedDomains`, each proven able to fail by its own planted-mismatch twin. |
| 2 | "0 rejected" stated in ST5.2's change description, and ST5.3 proves the check actually evaluates | **GREEN.** ST5.2's commit states 0 rejected and gives the witness: rung 4's v4 budget is `floor(1 × 1512 × 2315 / 1000) = 3500`, exactly the setter's realized power, so it sits on the line rather than above it. ST5.3's `ActionBudgetLiveTests` proves evaluation — every row carries a ceiling and a planted over-budget container is refused with `PowerBudgetExceeded` naming its container id. |
| 3 | **Full suite** (`.\scripts\test-fast.ps1 -AllDefault`), run once here, all six boundary guards green | **GREEN.** Run by the manager in a clean checkout of this branch at `5867b4e2`: **Data 1547/1547, Server 551/551, E2E 226/226, Core 14207/14208**. The single Core failure is `DungeonLootTableSeedFileTests` — the worktree-only CRLF artifact this lane has named since ST1.1, which passes **4/4** in the main checkout. All **six** boundary guards are green: single-writer, secondary-no-unity, funnel-delta, actor-hub, dal, test-substrate. |
| 4 | Map success criteria 1–7 hold: no `tier` column or field, no new curve, no model call, no hand-edited seed, and no test that pins a population or a tunable | **GREEN.** No `tier` column or field was added anywhere (ST1 put the rung's window on the existing `ContainerRow.MinTier`/`MaxTier`). No new curve: the report inverts the published derivation and reads only `poolRolls`/`qPowerMilli`. No model call: ST5.2's regeneration chain ran model-free (its `--dry-run`/write split is recorded in that commit). No hand-edited seed: the briefs tree was **regenerated** and compares equal to HEAD with every `corpusHash` removed — one line per brief. No test pins a population or a tunable: `ActionBudgetLiveTests` discovers the newest table rather than naming a version, and `BudgetCalibrationTests`/`PowerTableSeedTests` assert orderings, closure and reconciliation rather than counts. |

**Clearable-by is empty: nothing waits on anything.** The four rows above were each closed by a committed
artefact — `ef67cdea`/`27dd9ebe`/`06bc87f0` (the switch, the guard row, the seed tree), `5c59e295`
(live-check proof), the manager's suite run quoted in row 3, and `1be41c96` (the status lines that state
A-G1 is live, with the action-corpus follow-up named rather than edited).

**One caveat recorded, not hidden:** the suite's single red is the same CRLF worktree artifact this lane
has named since ST1.1, and the manager's run confirms it passes 4/4 in the main checkout — so it is a
property of a `core.autocrlf=true` worktree, not of this program.
