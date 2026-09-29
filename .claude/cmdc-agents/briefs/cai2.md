# Lane `cai2` — combat-ai: the CAI2.x halves that are filed but unfinished

**Session:** `combat-ai-2b` · **Program:** `combat-ai` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector/**`, `tests/**`,
`gk-core/data/tuning/**`, `tasks/combat-ai-todo.md`, `docs/architecture/combat-ai/**`, `tasks/reports/**`

## Work

`tasks/combat-ai-todo.md` is the authority. Each row below records **which half landed** and which did not — read
the row before acting, because the title alone will mislead you:

- **`CAI2.2` — `replay-identity` B: pin the profile at match start, refuse rather than drift.** Filed, not attempted.
- **`CAI2.3` — `action-schedule-twin`: the analytic model follows the core policy.** The **identity half landed**;
  find and finish the remainder.
- **`CAI2.5` — `decision-inspector` B: the lawn ring, default off.** The **core half landed** (lane `combat-ai-2`);
  the injector half is yours.
- **`CAI2.6` — the reserve floor's rule: the shipped seam and the ideal disagree.** ⚠ **This one needs an owner
  ruling** ("needs a ruling by…" in the row). **Do not close it and do not pick a side**: sharpen the question to
  one line with the evidence on both sides and leave it open. That is the deliverable for this row.

Then continue down the list while each remaining row has a clear acceptance.

## Rules that bind this program

- **One ActorHub compose / one read.** Actor combat derived and `AppliedCombat` compose once in `ActorHub` — a
  second composer is the defect this program exists to prevent (`scripts/guard-actor-hub.ps1`).
- **Combat writes go through `EntityStatWriter` / the effect Funnel** — no ad-hoc Unity stat patches
  (`scripts/guard-single-writer.ps1`, `scripts/guard-funnel-delta.ps1`).
- **No magic numbers on the balance surface**: a number a balance pass would change lives in
  `gk-core/data/tuning/<domain>.v{n}.json`, published as `v{n+1}` — never edited in place, readers moved in the same
  commit.
- ⛔ Never widen a guard to pass; never add a `knownRed` entry.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` (when the compose path is touched)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session combat-ai-2b`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- one commit per row/increment, naming the row it closes
- findings routed to the owning todo in the same commit, **with the id asserted present**

## Boundaries

- The injector build needs `FUSIONRPG_ML_GAMEDIR` + `FUSIONRPG_GAME_PROFILE='pvzrh-3.9'`; a build that cannot
  resolve them emits a 4 KB skip-stub and reports `0 Error(s)` — never read a stub as a build.
- Your session record's `worktree` path must be **ABSOLUTE**.
