# Lane `cai4` — combat-ai, the Core/Match + tuning half (and only that half)

**Session:** `combat-ai-4` · **Program:** combat-ai · **Mode:** worktree
**Ledger:** `tasks/combat-ai-ledger.jsonl` (append through `gk-core/scripts/anchor-ledger.py` only)
**Fence:** `gk-core/src/FusionRpg.Core/Match/**`, `data/tuning/combat-ai*.json`, `gk-core/data/tuning/lawn-perf-budget.v1.json`,
`docs/architecture/combat-ai/**`, `docs/research/combat-ai/**`, `gk-core/tests/FusionRpg.Core.Balance.Tests/**`,
`tests/FusionRpg.Core.Combat*Tests.Tests/**`, `tasks/combat-ai-todo.md`, `tasks/reports/**`

⚠ **Deliberately excluded, and not an oversight:** `gk-core/src/FusionRpg.Data/**` and `gk-core/src/FusionRpg.Server/**` are held
by lane `ep-3` (session `empire-progression-3`) right now; `tests/**` at large, `FusionRpg.slnx`,
`.github/workflows/**` and `scripts/**` are the single-writer chain held by `tvb58`/`tvb59`; and
`gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` is the subject of `CAI-guard-1` (a re-pin assigned to `tvb58` — do not
touch that file). If a row you are working genuinely needs a file outside your fence, **say so in your fragment
and stop that row**; the manager widens fences deliberately, never by accident.

## What this program is, and where it actually stands

Read `tasks/combat-ai-todo.md` and `docs/architecture/combat-ai-map.md` first, and `docs/DESIGN-GATE.md` §1 for
whichever subsystem you touch. The reconciliation (`tasks/reports/backlog-reconciliation-20260921.md`) measured
this program at **24 open task blocks / 26 done** — a real backlog, not the inflated line count: several rows
record a **partially landed** slice in their own text (*"IDENTITY HALF LANDED"*, *"SEAM HALF LANDED"*,
*"CORE HALF LANDED"*, *"VIEW HALF LANDED"*, *"COMPOSITE SLICE LANDED"*). Your first job is therefore to
establish, per row you take, **what remains** — against the code, not against the row's own summary.

## Deliverable

1. **Name the rows you take**, in dependency order, in your fragment. Candidates that live inside your fence:
   `CAI2.2` (replay-identity B), `CAI2.3` (action-schedule twin), `CAI2.5` (decision-inspector B, lawn ring,
   default off), `CAI2.6` (the reserve floor's rule), `CAI3.1` (stance-wiring, H7), `CAI4.1` (lawn actor view),
   `CAI4.2`/`CAI4.3` (lawn held-actions A/B), `CAI4.5` (lawn cost authority B), `CAI4.6`/`CAI4.7`/`CAI4.8`
   (lawn cast activation/trigger), `CAI4.9` (commander direct orders). Rows whose files sit outside the fence
   (`CAI3.2`, `CAI3.3`, `CAI3.5` — Data/Server) are **not yours**; report them as blocked-on-fence instead.
2. **Each taken row closed against its own acceptance lines**, with the exact command and the numbers printed.
3. **The ledger appended** for every row you close (`python gk-core/scripts/anchor-ledger.py tasks/combat-ai-ledger.jsonl append …`),
   and `… check` green.
4. **A NOT-proved list**, and any finding that belongs to another program named with that program — not fixed here.
5. **Do not tick a row whose acceptance you did not run.** A row recording a partial slice stays open until its
   remaining half is proven.

## Hard rules that bind here

- **H7 on tuning:** a tuning revision is published (`gk-core/tools/tuning/publish.py`, `v{n+1}`) and its readers switch in
  the **same commit** — never an in-place edit, never a publish without readers. `data/tuning/combat-ai*.json` is
  this program's domain; `lawn-perf-budget.v1.json` is shared with the lawn plan — if you need a new revision of
  that one, say so first.
- **One ActorHub compose / one read.** Combat derived state composes once in `ActorHub`; contribute via
  `IActorStatSubsystem` / registered atom readers or consume Hub output. `BattleStatComposer` was fused and
  deleted (2026-09-13) and is never a pattern to copy. `.\scripts\guard-actor-hub.ps1` must stay green.
- **Combat writes only via `EntityStatWriter` / Funnel**; SQL only inside `FusionRpg.Data` (which is not yours).
- **No magic numbers on the balance surface** and no hard progression ceilings; a number a balance pass would
  change lives in the tuning file.
- **Never widen a guard's allowlist and never add a `knownRed` entry** to make a check pass.
- **A debug API may trigger a real operation, never fabricate its result** — name which scope you are in.

## Verification

```powershell
dotnet test tests\FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicy|FullyQualifiedName~DecisionAllocation"
dotnet test tests\FusionRpg.Core.CombatFanoutTests.Tests
.\scripts\guard-actor-hub.ps1
python scripts\anchor-ledger.py tasks\combat-ai-ledger.jsonl check
.\scripts\verify-change.ps1 -Paths <every changed path> -Session combat-ai-4
```

Commit per row, `paths` explicit, one logical change per commit. The manager accepts at a frozen idle SHA with
the artefact, and merges on green.
