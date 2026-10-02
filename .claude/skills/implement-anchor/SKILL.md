---
name: implement-anchor
description: >-
  Set up a long-run program anchor and <=4000-char manager goal from map/spec/plan/todo inputs.
  Splits oversized scope into one anchor + goal per lane or sub-program, each with its own session.
  Validates inputs, collects context slice-only, writes tasks/<program>-anchor.md, wires
  session-boundary + verify-change + ledger gates, then generates the goal prompt for the manager goal field.
argument-hint: "[program]"
---

# Implement Anchor — Long-Run Setup Skill

Source of truth: `.agents/skills/implement-anchor/SKILL.md`. Mirrors (`.claude/skills/`,
`.cursor/`, `.kilo/` where a skills dir exists) must stay byte-identical copies. Never add this skill to `skills-lock.json` (local-authored,
same as `seedsmith`, `seedsmith-passivetree-repair`, `live-probe-mcp`).

## When to use / refuse

Use when the owner names a program with multiple specs/todos/plans and wants a long run of tasks
without context bloat or drift. Refuse single-file fixes and small 1-2 file changes — just do them
directly. Refuse to start if any named map/spec/plan/todo path does not exist.

Repo standard this skill enforces: `docs/architecture/<program>-map.md` (capability index),
`docs/architecture/<program>/spec-<module>.md` (module specs), `tasks/<program>-plan.md` +
`tasks/<program>-todo.md` (plan + tasks, never `tasks/plan.md`/`todo.md` — perf history).

## Step 0 — Intake (ask, then validate)

Ask the owner for exactly this, no more. If invoked as `/implement-anchor <program>`, item 1
arrives pre-filled — confirm it, don't re-ask:

1. `program` id (kebab-case, matches map/todo prefix).
2. `map` path — `docs/architecture/<program>-map.md` (or `-program.md`).
3. `specs[]` — module spec paths actually in scope (not the whole folder).
4. `plan` path — `tasks/<program>-plan.md`.
5. `todo` path — `tasks/<program>-todo.md` plus the ACTIVE wave/task ids (e.g. `W42-W60`, `F1-F3`).
6. `peers[]` — sub-programs. Each gets its OWN peer anchor (`tasks/<peer>-anchor.md`), linked by a
   provider/consumer table. Never nest them into one file.
7. Session `mode` (`direct` default) / `branch` / `paths` fence (the fence covers exactly this
   goal's queue — no more, no less).

Validate: every path exists on disk. If any is missing, stop and say which — do not guess.

## Step 0b — Size gate (split before anything else)

Count open checkboxes (`- [ ]`) across the in-scope todos and total bytes of those files.
Split into one anchor + one goal per lane or sub-program — each with its OWN session id,
paths fence, anchor, ledger, and goal — when ANY is true:

- more than **50 open items** in scope;
- in-scope todo text over **64KB**;
- scope spans **more than one plan/todo pair**;
- the plan itself names **separate lanes or sessions** (when the goal and its source of truth
  disagree, the agent follows the source and drops the rest).

Why 50 / 64KB: the failed `summoner-convergence` run carried ~1036 open items in ~1MB and
stalled after 5; the proven owner prompt closes audit-scale scope. An agent closes only a
handful of items per context window through the full 9-step cycle, and past ~64KB the scope
text crowds out the evidence the cycle needs — so one goal can only drive scope that fits in
one window plus a bounded queue. The smallest split unit is one plan/todo pair (or one lane
of it when the plan names lanes); splitting stops there. When the smallest unit still exceeds
the threshold — `species-gear-chain` alone carries 426 open items — that is expected: one
session record works the queue across as many context windows as it takes, continuing through
`resume` after every recovery (see EXHAUSTION in the goal). Program detail lives in per-lane
anchors; the goal stays under 4000 chars.

When split: run Steps 1–4 once per lane. Name sessions `<lane>-<date>` (e.g.
`lane-a-actions-20260918`). Each lane anchor records its own queue; cross-lane order comes only
from the parent plan's hard edges, cited by id.

## Step 1 — Collect (read-only, bounded)

Read-only. Load the minimum that proves scope. Standards reading is enforced, not assumed:

1. Mandatory committed standards (every run, in this session): `docs/PRINCIPLES.md` (one-page
   digest) + `docs/DESIGN-GATE.md` §1 row docs for every touched subsystem +
   `docs/architecture/decisions.md` locks. `AGENTS.md`/`CLAUDE.md` are gitignored local-only —
   never cite them as source of truth; their committed copy is `PRINCIPLES.md`. A prior session
   having read them does not count. Record the DESIGN-GATE §5 checklist; an unticked box is
   stated, never hidden. Every factual claim cites `file:line` (code beats docs; docs beat comments).
2. The parent plan (order, hard edges, lanes) — read fully; it is small by construction.
3. The active lane's todo(s) — read IN FULL. They are the queue's source.
4. Other todos ONLY for tasks the queue depends on (hard-edge prerequisites). Never "read entire
   scope" across a parent that aggregates many programs — that is what cost the failed run its
   context. The full files stay on disk unread.
5. Order the lane's tasks (hard edges first, then todo order). The queue + its concrete next item
   go into the anchor (Step 2) and the ledger `anchor --queue` line.
6. All `tasks/sessions/*.json` — check no active record overlaps `paths`. Run
   `python scripts/session-boundary-check.py`; clean (exit 0) is the precondition for editing.

## Step 2 — Anchor artifact (`tasks/<program>-anchor.md`, <60 lines)

Write the small pointer file. Template (fill `[BRACKETS]`, keep under 60 lines):

```md
# Anchor: [program]
Map: [map path] · Plan: [plan path] · Todo: [todo path] ([active tasks])
Specs: [spec paths in scope]
Session: [session id] ([mode], [branch]) · Paths: [paths fence]
Standards: PRINCIPLES + DESIGN-GATE §1 rows [subsystems] + decisions locks, read in this session
Queue: [ordered task ids, dependency order, comma-separated, ids only]
Next: [concrete next task id — first unblocked undone queue item]
Peers: | Peer | Anchor | Provides | Consumes |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.py -Paths <changed> -Session [id]` (+ `-PlanOnly` to preview)
Evidence: `tasks/evidence-fragments/[task-id].md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/<program>-ledger.jsonl` — append-only run-state (`anchor|task|note|gate|queue|complete`);
  EVERY event written through `python gk-core/scripts/anchor-ledger.py <ledger> ...` — never hand-write
  lines (hand-written lines fail `check`). Seed with
  `anchor --plan ... --todo ... --session ... --queue "[ids]"`; adopting an already-anchored
  ledger with no queue: `queue --ids "[ids]"` (latest line wins). A fresh agent runs
  `... resume` first, never re-reads history. `... check` must exit 0; `resume` prints the
  brief (scope, queue, done, blocked+reason, active, gates, last 5 notes, concrete next).
Verify: focused filter + guard per task Verify line, never full suite by default.
```

Rules: checkboxes in todo stay `Description/Acceptance/Verify/Files/Deps/Scope` — proof rows go to
`tasks/evidence-fragments/<task-id>.md` (format in its `README.md`: real executed results only,
`N/A` needs a reason, documented-but-unfixed = `FAIL`). Todo file itself is never bloated with
inline evidence dumps.

## Step 3 — Wire gates (deterministic, reused scripts)

No new check script — reuse only:

1. `/session-start` — write `tasks/sessions/<session>.json` (template `tasks/sessions/_template.json`:
   `session/program/problem/mode/branch/worktree/paths/started/status`), commit with first change.
2. `python scripts/session-boundary-check.py` — exit 0 before first edit and before each commit.
   Ledger writes: one `anchor` line at setup (with `--queue`); one `queue --ids` line when
   adopting an already-anchored ledger or re-ordering (latest wins); one `task --state started|done|blocked`
   per task transition; one `note` per decision future sessions must not rediscover; one `gate` per
   deterministic gate result; `complete` at the end. EVERY write goes through
   `gk-core/scripts/anchor-ledger.py` — the script stamps time + integrity mark; hand-written lines fail
   `check`. Resume: `python gk-core/scripts/anchor-ledger.py tasks/<program>-ledger.jsonl resume` is the
   first command of every fresh context window on the same session record; `... check` must exit 0 (schema + sequence drift).
3. `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` — every changed path must resolve to
   exactly one owner (`verification-boundaries.v1.json`); `-PlanOnly` previews without running.
4. Per-task `Verify:` line — focused `dotnet test --filter` + applicable `scripts/guard-*.ps1`.
   Full suite only at: large-feature finish, cross-program change, or right before a live probe.
5. Commits with plain `git` (explicit paths) (the session fence), never `all=true`.
   Push/PR only when the owner asks.

## Step 4 — Goal prompt (<=4000 chars, then ask owner to set it)

Fill the template, then check with `Measure-Object -Character` (or `wc -m`) — raw AND filled for
1. `/session-start` — write `tasks/sessions/<session>.json` (template `tasks/sessions/_template.json`:
   `session/program/problem/mode/branch/worktree/paths/started/status`), commit with first change.
2. `python scripts/session-boundary-check.py` — exit 0 before first edit and before each commit.
   Ledger writes: one `anchor` line at setup (with `--queue`); one `queue --ids` line when
   adopting an already-anchored ledger or re-ordering (latest wins); one `task --state started|done|blocked`
   per task transition; one `note` per decision future sessions must not rediscover; one `gate` per
   deterministic gate result; `complete` at the end. EVERY write goes through
   `gk-core/scripts/anchor-ledger.py` — the script stamps time + integrity mark; hand-written lines fail
   `check`. Resume: `python gk-core/scripts/anchor-ledger.py tasks/<program>-ledger.jsonl resume` is the
   first command of every fresh context window on the same session record; `... check` must exit 0 (schema + sequence drift).
3. `.\scripts\verify-change.py -Paths <changed> -Session <id>` — every changed path must resolve to
   exactly one owner (`verification-boundaries.v1.json`); `-PlanOnly` previews without running.
4. Per-task `Verify:` line — focused `dotnet test --filter` + applicable `scripts/guard-*.ps1`.
   Full suite only at: large-feature finish, cross-program change, or right before a live probe.
5. Commits with plain `git` (explicit paths) (the session fence), never `all=true`.
   Push/PR only when the owner asks.

DEPENDENCIES: Follow queue + hard-edge order. Prerequisites before dependents. Never skip hard items for easy ones.

ANTI-CHEAT: NOT completion: reading scope; making a plan; some items; a milestone/phase/wave; passing tests; building; launching background work; a summary; "done" without evidence; dropping a requirement without an explicit scope rule. Never invent an approval gate, stopping point, scope reduction, or permission to stop. Only the scope files define boundaries.

BACKGROUND: A running command is NEVER a stop. Do independent queue work while it runs; poll when its result is required; never claim verification before its result.

FAILURES: Every defect from probe, test, review, or build is fixed or resolved by an explicit scope rule. Never hide, defer, or paper over.

BLOCKED: If only the owner can clear an item (owner question, live probe, full suite): record it blocked + reason via the ledger script, continue with the next unblocked queue item. Stop only when EVERY remaining item is owner-blocked — then list them.

LEDGER: Every event through `python gk-core/scripts/anchor-ledger.py [ledger] ...` (task started|done|blocked, note, gate, queue --ids to adopt/replace the queue). Never hand-write lines. `resume` is the first command after every fresh start on the same record.

FENCE: Session [session] (the repo session record — one goal owns exactly one record; the record persists across context windows via resume), paths [paths]. This queue IS the record's scope — never one goal across records. Commits with plain `git`, explicit paths only (never `-A`/`-a`).

LOOP: After every verified item reread queue + ledger, take the next unblocked item, run its full cycle. Never end with only a progress report while queue work remains.

GATE: STOP only when ALL true: every queue item done or owner-blocked; impl + contracts complete; observability exercised; probes executed + evaluated; tests pass; found bugs fixed; regression cover exists; gates satisfied; evidence recorded; NOTHING unresolved except listed owner-blocked items. "Complete/fixed/green/done" are claims, not proof. Proof = executed commands, tests, probes, logs, diffs, artifacts.

EXHAUSTION: Context pressure is NOT a stop. Preserve item, cycle stage, evidence, failures, pending cmds, next item. After recovery reread scope + anchor [anchor] and continue.

FINAL: Before stopping reread the ENTIRE scope and map every queue item to impl + evidence. Anything unblocked remains = DO NOT STOP.

NO PROVEN QUEUE COMPLETION = NO STOP.
```

## Worked example

Owner: `/implement-anchor summoner-convergence`. The size gate fires first: ~1036 open items
across 11 plan/todo pairs (~1MB), and the parent plan names four lanes in separate sessions —
so one setup per lane, not one giant goal. For lane A the intake confirms
`program=lane-a-actions`, the parent plan (hard edges only), the two lane todos read in full
(other todos only for H1 prerequisites), session `lane-a-actions-20260918` (direct, current
branch, its own `paths` fence). Collect orders the queue per H1 then todo order. Anchor written
to `tasks/lane-a-actions-anchor.md` with `Queue:` ids and `Next: ST1.1` (ST2.1–ST2.5 are
done in the failed run's ledger, so lane A's wave-1 order gives ST1.1 next per todo line 76);
ledger seeded with `anchor --queue "ST1.1,..."`. Gates: `/session-start` record exists,
`session-boundary-check` exit 0, `verify-change -Paths <lane-A paths> -Session ... -PlanOnly`
resolves one owner. Goal filled from the template, measured raw and filled (both under 4000),
and handed to the owner to paste into the manager goal field — one goal per lane, each driving
its own queue to proven complete.

## Anti-cheat (binding on every run from this skill)

- No silent skip, reinterpret, replace, or reduce of any requirement.
- Never invent an approval gate, stopping point, scope reduction, or permission to stop.
- A milestone, phase, wave, plan, green test run, or build is not completion.
- Context pressure is never permission to stop or to shrink scope.
- `N/A` needs a written reason; documented-but-unfixed is `FAIL`.
- Blocked-on-owner items are recorded blocked + reason and skipped; stopping needs every
  remaining item owner-blocked and listed.
- Every ledger event goes through `gk-core/scripts/anchor-ledger.py`; hand-written lines fail `check`.
- No `git stash`/`checkout`/`reset` around another session's files; no `all=true` commits.
- Generated seed data (`gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`) is never hand-edited — fix the
  generator and regenerate. Balance numbers live in `gk-core/data/tuning/<domain>.v{n}.json`.
