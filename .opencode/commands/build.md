---
description: Implement tasks incrementally — build, test, verify, commit. Add "auto" to run the whole plan in one approved pass, or "full" for zero human attention with a subagent gate per task.
---

Load the `incremental-implementation` skill alongside `test-driven-development` via the `skill` tool.

> **This repo overrides the commit steps below.** AGENTS.md is git hands-off: never run `git commit`, `git add`, or any git write. Wherever a step says "commit", instead leave the work in the tree, mark the task complete, and hand the owner a one-line commit message plus the paths touched. Everything else in the loop (test, build, verify, stop-and-ask) applies unchanged.

## Modes

- **`/build`** — implement the *next* pending task, then stop (careful, one slice at a time).
- **`/build auto`** — generate the plan if needed, get a single approval, then implement *every* task without stopping between them.
- **`/build full`** — **zero human attention.** No approval gate and no human stop: verify every task with the **`build-gate` subagent** (a fresh context re-runs the task's verification before the task is marked complete), resume autonomously from blockers, and end only when the program is done or a genuine irreversible blocker is hit.

`$ARGUMENTS` selects the mode. Treat `full` as the maximally autonomous mode, `auto` (canonical) or
`all` as autonomous-with-one-approval, and anything else (or empty) as the default single-task mode.
No mode is faster *per task* — they run the same test-driven loop; they differ only in whose judgment
gates completion and how many times the human is consulted.

## Default: one task

Pick the next pending task from the plan. Then:

1. Read the task's acceptance criteria
2. Load relevant context (existing code, patterns, types)
3. Write a failing test for the expected behavior (RED)
4. Implement the minimum code to pass the test (GREEN)
5. Run the full test suite to check for regressions
6. Run the build to verify compilation
7. Commit with a descriptive message
8. Mark the task complete and stop

## Autonomous: the whole plan (`/build auto`)

Use this once a spec exists and you want to collapse plan + build into one run. It removes the manual stepping between tasks — **not** the verification. Every task still earns a passing test and its own commit.

1. **Require a spec, and know which one.** Look only for a spec at a known path: `SPEC.md` at the repo root, `docs/SPEC.md`, a file under `spec/`, or a program's module specs under `docs/architecture/<program>/` listed by its capability map. A README or arbitrary doc does **not** count. If none exists, stop and tell the user to run `/spec` first — do not invent requirements. If several programs have live specs, **ask which one you are building** rather than picking.
2. **Establish a clean baseline.** Run `git status --porcelain`. If there are uncommitted changes outside this program's expected planning artifacts (its spec, plan, and task list — the default `SPEC.md` / `tasks/plan.md` / `tasks/todo.md` set, or the program's prefixed equivalents), stop and ask the user to commit, stash, or confirm how to handle them. Autonomous per-task commits must not absorb unrelated local work, or the clean-rollback guarantee breaks. In a repo with several programs in flight, expect other streams' uncommitted work to be present and never sweep it into a commit.
3. **Plan if needed.** If this program has no plan (`tasks/plan.md`, or its prefixed equivalent), load `planning-and-task-breakdown` via the `skill` tool to generate one.
4. **Single checkpoint.** Present the full plan and wait for an unambiguous affirmative (e.g. "approve", "go", "yes"). Treat hedged responses ("looks reasonable", "I guess") as **not** approved. This is the only human gate — after approval, run autonomously. If you generated `tasks/plan.md`, commit it as a single preparatory commit now so it doesn't bleed into the first task's commit.
5. **Execute every task in dependency order.** Use each task's declared dependencies; if they aren't explicit, execute in the order the plan lists them. For each task, run the full default loop above (RED → GREEN → regression → build → commit → mark complete). Stage only the files that task touched plus its task-status update — never `git add -A` blindly — and make one commit per task so any point is a clean rollback.
6. **Stop and ask the user** (do not push through) when:
   - a test can't be made to pass or the build breaks without an obvious fix → load `debugging-and-error-recovery` via the `skill` tool
   - the spec is ambiguous, or a task needs a decision the spec doesn't cover
   - a task is high-risk or irreversible — auth/permission changes, destructive data migrations, payments, deletions, deploys, anything touching secrets, **or anything you can't undo with `git revert`** → load `doubt-driven-development` via the `skill` tool and get explicit sign-off before continuing

   After the user resolves a blocker, they re-invoke `/build auto` — it resumes from the next pending task.
7. **Summarize at the end:** tasks completed, tests added, commits made, and anything skipped, flagged, or left for the user.

If any step fails, load the `debugging-and-error-recovery` skill via the `skill` tool.

## Zero-attention: the gate subagent (`/build full`)

`/build full` is the same loop as `/build auto` with **one change**: the verification step is moved
out of the builder's own judgment and into an independent **`build-gate` subagent** — so no human
ever has to decide whether a task really passed.

**Why a subagent, not a human.** The builder runs long; its context accumulates the story it wants to
believe ("that test passed a while ago"). The subagent starts fresh: it re-reads the task's criteria,
inspects the actual diff, and **re-runs** the verification and guards itself. A builder summary is a
claim; the gate's executed output is proof.

**Why independence, not self-policing.** A single agent that writes the code and then grades its own
work grades generously. Independence is the whole mechanism, so the gate must be a separate context
and it must be read-only — it cannot "fix" what it is grading.

### 1. Setup (once)

Same as `/build auto` steps 1–3: a known spec, a clean baseline (record the dirty set **once** —
that is the baseline you subtract in every gate call), and a plan that exists. There is **no plan
approval gate**: `/build full` is authorized by its invocation.

### 2. Per task: build, then gate, then mark complete

For each task in dependency order:

1. **Build it** exactly as the default loop (RED → GREEN → focused test → guards → regression).
2. **Do not mark it complete yet.** Spawn the `build-gate` subagent with the Task tool
   (`subagent_type: "build-gate"`), passing: the program id +
   task id, the todo and spec paths, the **baseline dirty set** recorded at setup, and the task's
   declared Verify + guards.
3. **Read the gate's report.**
   - `GATE: PASS` → mark the todo box, record the gate report's decisive lines as the evidence, and
     go to the next task.
   - `GATE: FAIL` → treat each `BLOCKER` as the next work item. Fix it, then **re-spawn the gate**
     for the same task. Never mark a task complete whose latest gate report is `FAIL`. Never argue
     with a `FAIL` by editing the gate's criteria — fix the code or the test, or (if the criterion
     itself is wrong) stop per §4.
4. Because this repo is git hands-off, the "commit" of `/build auto` becomes the **owner hand-off**:
   for each gated task, report the one-line commit message, the explicit paths, and the gate's
   decisive proof line.

### 3. Bounded gate rounds (no infinite loop)

Give a task at most **3 gate rounds**. If it is still `FAIL`, do not keep burning context: **defer**
the task — leave it `in_progress` with the latest gate report attached, and pick the next task whose
dependencies are met. Return to deferred tasks after the ready set empties. If a deferred task is the
sole blocker for everything else, that is a genuine blocker (§4).

A gate `FAIL` is **not** a human stop. It is the loop working. Only §4 stops the run.

### 4. The only stops (same bar as `/build auto` step 6, restated)

- a test cannot be made to pass or the build breaks with no obvious fix (after
  `debugging-and-error-recovery`), **and** the task cannot be deferred because everything else
  depends on it;
- the spec is genuinely silent on a product decision — a question only a human can answer;
- an action is destructive/irreversible beyond the plan's locked scope — load
  `doubt-driven-development` and get explicit sign-off.

Everything else continues. When blocked on one task, do any other eligible ready task first; when a
command is running, do independent eligible work while it runs; context pressure is not a stop — write
state into the plan/todo and resume.

### 5. End

Stop when every task is gated or explicitly deferred, or a §4 blocker is hit. Report: per-task commit
message + paths, the gate result per task, gate rounds used, anything deferred with its last gate
report, and the tests added. Do not report a task as done whose latest gate report is not `PASS`.

**Fallback when the gate subagent is unavailable.** If spawning `build-gate` fails (missing agent,
subagents disabled), do **not** silently self-verify: downgrade to `/build auto` semantics for the
remaining tasks and say so in the final report. The gate's independence is the point — a builder
grading itself is exactly what `/build full` exists to remove, so this downgrade must be visible.

If any step fails, load the `debugging-and-error-recovery` skill via the `skill` tool.
