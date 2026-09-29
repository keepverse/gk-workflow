---
description: "Autonomously execute the actor-hub-and-combat-power-solid-fixing program end to end with guards, executed evidence, and no per-task stops."
agent: solid-runner
---

Implement the `actor-hub-and-combat-power-solid-fixing` program from the tasks and plan. This
command is the execution guardrail **and** the autonomy contract for that program.

**Read first, every session:**
- `tasks/actor-hub-and-combat-power-solid-fixing-todo.md` (tasks + acceptance criteria)
- `tasks/actor-hub-and-combat-power-solid-fixing-plan.md` (audit + risks + ordering)
- `docs/architecture/actor-hub-and-combat-power-solid-fixing-map.md` (module ownership)
- `docs/architecture/actor-hub-and-combat-power-solid-fixing-ideal.md` (stub-hygiene law)
- `tasks/actor-hub-and-combat-power-solid-fixing-runbook.md` (fan-out + integration order)
- the module spec the task names, under `docs/architecture/actor-hub-and-combat-power-solid-fixing/`

`AGENTS.md` wins over anything here. **First establish this session's boundary** with
`/session-start` (see [docs/contributing/session-boundary.md](docs/contributing/session-boundary.md)):
one problem, an owned `paths` list, and a mode/branch the owner chose. Then: **commit each verified
increment to the current branch via plain `git commit`** (validate the message first if
unsure) — one logical change per commit, without waiting to be asked, passing explicit `paths` and
never `all`. Never run raw `git commit`/`add`/`merge` (mechanically blocked); `push` is owner-only.
Never touch a path outside your boundary; a parallel session's dirty file is not yours to stage,
revert, or stash around.

## Modes

- **`/solid-run`** — **AUTO (default).** Execute every pending task in dependency order and keep
  going through all five waves in this one invocation. No per-task prompt, no wave pause.
- `/solid-run next` — do only the next pending task, then stop. The one manual stepping mode.
- `/solid-run Tn` — do only the named task, then stop.

## Autonomy contract (what AUTO means)

1. **No human gates.** The plan's `Ask-first` table already fixes every open choice; apply the
   listed default and record it as a non-blocking follow-up row in the evidence map. The single
   `RulesetVersion` bump (`= 4` → `= 5`) is **already locked by the approved plan** — T6 executes it
   and re-blesses goldens; it does not wait for a fresh approval. Do not invent a gate, a stopping
   point, a scope cut, or a "let me check with you" pause.
2. **Wave checkpoints are verification gates, not pauses.** At each `## Checkpoint`, fold evidence
   fragments, run the wave's guards and integrated filtered suites on the current tree, confirm
   every row is `PASS`/`N/A`, then continue to the next wave automatically.
3. **A running command is not a stopping condition.** Start it, then do independent eligible work
   while it runs; poll only when its result is required.
4. **Stop only for a genuine blocker:**
   - a test cannot be made to pass or the build breaks with no obvious fix (after
     `debugging-and-error-recovery`);
   - the spec is genuinely silent on a product decision the Ask-first table does not cover;
   - an action is destructive/irreversible **beyond** the locked T6 bump and the plan's deletions.
   Everything else continues. When blocked on one task, do any other eligible ready task first.
5. **Context pressure is not permission to stop.** Before compaction, write the current task, cycle
   stage, failures, evidence, pending commands, and next item into the evidence map; recover from
   it and resume. The evidence ledger is the recovery point.

## Per-task runcard (mandatory, every task, no skipping)

1. **READ** the task's acceptance criteria and module spec. Verify doc/comment claims against code.
   `docs/DESIGN-GATE.md` applies to anything beginning "we should".
2. **RED** — add the failing test/fixture the criteria imply before touching production code.
3. **BUILD** — minimum implementation to pass it. Hard boundaries: `long` magnitudes, no bare
   balance literals, no second ladder, no parallel compose/read path, no new stub.
4. **GREEN** — run the focused filter named in the task's Verification block.
5. **GUARDS** — run every guard the task lists, plus `python gk-core/scripts/guard-actor-hub.py` on any
   compose/read change. Never weaken a guard to pass.
6. **REGRESSION** — run the relevant full suite (`FusionRpg.Core.Tests`, `FusionRpg.Data.Tests`,
   `FusionRpg.Server.Tests`, `FusionRpg.Guard.Tests`, `FusionRpg.Injector.Tests` as applicable).
7. **EVIDENCE** — record one row per acceptance criterion in
   `tasks/actor-hub-and-combat-power-solid-fixing-evidence-map.md`: command, **executed** result
   (exit code + tail), artifact path. `PASS` only if run this cycle. Add the follow-up row for any
   Ask-first default applied.
8. **MARK DONE** — tick the todo boxes only when every evidence row for the task is recorded, then
   immediately pick the next pending task. Do not summarize-and-stop between tasks.

### Proof by surface (do not use one template for both)

- **C#/data tasks** (T1–T9, T12–T16, T18–T23): focused `dotnet test` filters, guards, prove
  scripts. Observability = the flow's structured logs/events; capture the decisive log line as
  evidence when a new flow is added.
- **FE tasks** (T10, T11, T17): `npm test -- --run <fold>` first, then Playwright E2E against the
  real app, then screenshots at desktop/tablet/mobile via Playwright MCP inspected for overflow,
  clipping, wrapping, stacking. Add stable `data-testid` to the elements touched.

Do not force Playwright, `data-testid`, or viewport screenshots onto tasks with no DOM. Do not treat
a build pass, an existing green suite, or an unexecuted test as completion.

## Execution order

Sequential on the current branch is the fully automatic path and is what AUTO uses:

`T1 → T2 → T3 → T4` (W1a) `→ T5 → T6 → T7` (W1b) `→ T8 → T9 → T10 → T11` (W2)
`→ T12 → T13 → T14` (W3) `→ T15 → T16 → T17 → T18 → T19` (W4) `→ T20 → T21 → T22 → T23` (W5).

Honor declared dependencies; if a task's dependency is unmet but another task is ready, do the
ready one first and return.

### Optional parallel fan-out

Only when invoked as `/solid-run fanout`: dispatch the independent task groups to Agent Manager
worktrees per the runbook §3–4, one session per group, each prompted `/solid-run Tn`. Worktrees
branch from `main` and each worktree commits its own slice with `git commit`; the owner merges
between waves. Use AUTO on the current branch when the goal is
zero manual steps.

## Termination gate

The run is done only when:

- every task's acceptance criteria are implemented;
- every declared Verification command was executed and recorded `PASS` (or justified `N/A`);
- guards are green and none was weakened;
- FE scope has Playwright E2E green **and** inspected screenshots at the required widths;
- all discovered defects are fixed and have regression coverage;
- the Program Done list in the todo and the map's Done-when list are each backed by an executed row.

"Done", "verified", "green", "covered", and "looks good" are claims, not proof. The evidence map is
the proof. Commit each verified wave on the current branch with `git commit` with explicit
`paths`; the final report lists the commit subjects and changed paths per wave.
