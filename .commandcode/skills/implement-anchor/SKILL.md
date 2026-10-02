---
name: implement-anchor
description: >-
  Set up a long-run program anchor and <=4000-char manager goal from map/spec/plan/todo inputs.
  Use when a program has multiple specs/todos and must run many tasks without context bloat or drift.
  Validates inputs, collects context slice-only, writes tasks/<program>-anchor.md, wires
  session-boundary + verify-change gates, then generates the goal prompt for the manager goal field.
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
7. Session `mode` (`direct` default) / `branch` / `paths` fence (one problem per session).

Validate: every path exists on disk. If any is missing, stop and say which — do not guess.

## Step 1 — Collect (read-only, slice-only)

Read-only. Load the minimum that proves scope. Standards reading is enforced, not assumed:

1. Mandatory committed standards (every run, in this session): `docs/PRINCIPLES.md` (one-page
   digest) + `docs/DESIGN-GATE.md` §1 row docs for every touched subsystem +
   `docs/architecture/decisions.md` locks. `AGENTS.md`/`CLAUDE.md` are gitignored local-only —
   never cite them as source of truth; their committed copy is `PRINCIPLES.md`. A prior session
   having read them does not count. Record the DESIGN-GATE §5 checklist; an unticked box is
   stated, never hidden. Every factual claim cites `file:line` (code beats docs; docs beat comments).
2. Map build order + dependency graph + open items for the ACTIVE wave only.
3. Todo ACTIVE slice only (wave/tasks from Step 0). Never load the whole file —
   `world-map-todo.md` (>128KB) and `combat-unification-todo.md` (691 lines) are why long runs bloat.
   Active slice lives in the session task list (`todo_write` in Command Code, the host's
   equivalent elsewhere); the full file stays on disk unread.
4. All `tasks/sessions/*.json` — check no active record overlaps `paths`. Run
   `python scripts/session-boundary-check.py`; clean (exit 0) is the precondition for editing.

## Step 2 — Anchor artifact (`tasks/<program>-anchor.md`, <60 lines)

Write the small pointer file. Template (fill `[BRACKETS]`, keep under 60 lines):

```md
# Anchor: [program]
Map: [map path] · Plan: [plan path] · Todo: [todo path] ([active tasks])
Specs: [spec paths in scope]
Session: [session id] ([mode], [branch]) · Paths: [paths fence]
Standards: PRINCIPLES + DESIGN-GATE §1 rows [subsystems] + decisions locks, read in this session
Peers: | Peer | Anchor | Provides | Consumes |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.py -Paths <changed> -Session [id]` (+ `-PlanOnly` to preview)
Evidence: `tasks/evidence-fragments/[task-id].md` per task (`| Criterion | Command | Result | Artifact |`)
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
3. `.\scripts\verify-change.py --paths <changed> --session <id>` — every changed path must resolve to
   exactly one owner (`verification-boundaries.v1.json`); `-PlanOnly` previews without running.
4. Per-task `Verify:` line — focused `dotnet test --filter` + applicable `scripts/guard-*.ps1`.
   Full suite only at: large-feature finish, cross-program change, or right before a live probe.
5. Commits with plain `git` (explicit paths) (the session fence), never `all=true`.
   Push/PR only when the owner asks.

## Step 4 — Goal prompt (<=4000 chars, then ask owner to set it)
1. `/session-start` — write `tasks/sessions/<session>.json` (template `tasks/sessions/_template.json`:
   `session/program/problem/mode/branch/worktree/paths/started/status`), commit with first change.
2. `python scripts/session-boundary-check.py` — exit 0 before first edit and before each commit.
3. `.\scripts\verify-change.py -Paths <changed> -Session <id>` — every changed path must resolve to
   exactly one owner (`verification-boundaries.v1.json`); `-PlanOnly` previews without running.
4. Per-task `Verify:` line — focused `dotnet test --filter` + applicable `scripts/guard-*.ps1`.
   Full suite only at: large-feature finish, cross-program change, or right before a live probe.
5. Commits with plain `git` (explicit paths) (the session fence), never `all=true`.
   Push/PR only when the owner asks.
COMPLETE [program]: SOURCE OF TRUTH: [plan] [todo active tasks] [specs]. Read ENTIRE scope first;
it owns requirements, deps, acceptance, evidence. Do not skip, reinterpret, or reduce.
MISSION: Drive to PROVEN COMPLETE. Every item resolved + evidenced.
STANDARDS: PRINCIPLES + DESIGN-GATE rows + decisions locks read in this session; cite file:line.
SESSION FENCE: work only inside session [id] paths [paths]; one problem per session; commit via
plain `git`, explicit paths only (never `-A`/`-a`).
CYCLE EVERY ITEM: 1.READ req+contract. 2.BUILD fix. 3.OBSERVE metrics/logs. 4.PROBE falsifier vs
real behavior. 5.TEST focused filter + guard. 6.REVIEW callers/contracts/edges. 7.FIX gaps.
GATES: session-boundary-check clean; verify-change -Paths <changed> -Session [id]; guards per
Verify line. Evidence row per criterion in tasks/evidence-fragments/[id].md
(Criterion|Command|Result|Artifact). Done-claims without executed proof = FAIL.
EXHAUSTION: pressure is not stop. Preserve item, stage, evidence, failures, pending cmds, next
item. After recovery reread scope + anchor [anchor path] and continue.
FINAL: reread ENTIRE scope, map every req to impl + evidence. NO PROVEN COMPLETION = NO STOP.
```

## Worked example

Owner: `/implement-anchor solid-remediation`. Intake confirms `program=solid-remediation`,
map `docs/architecture/solid-remediation-map.md`, specs the two module files in scope, plan
`tasks/solid-remediation-plan.md`, todo `tasks/solid-remediation-todo.md` active tasks `T6-T9`,
peers none, session `solid-remediation-20260917` (direct, current branch, its `paths` fence).
Collect loads the gate rows + active T6-T9 slice only (not the whole todo). Anchor written to
`tasks/solid-remediation-anchor.md` (<60 lines). Gates: `/session-start` record exists,
`session-boundary-check` exit 0, `verify-change -Paths <T6 paths> -Session ... -PlanOnly` resolves
one owner. Goal filled from the template (~1500 chars, well under 4000) and handed to the owner
to paste into the manager goal field.

## Anti-cheat (binding on every run from this skill)

- No silent skip, reinterpret, replace, or reduce of any requirement.
- Context pressure is never permission to stop or to shrink scope.
- `N/A` needs a written reason; documented-but-unfixed is `FAIL`.
- No `git stash`/`checkout`/`reset` around another session's files; no `all=true` commits.
- Generated seed data (`gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`) is never hand-edited — fix the
  generator and regenerate. Balance numbers live in `gk-core/data/tuning/<domain>.v{n}.json`.