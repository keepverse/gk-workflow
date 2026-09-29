---
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering
---

Invoke the agent-skills:planning-and-task-breakdown skill.

Read the existing spec and the relevant codebase sections. The spec may be `SPEC.md` at the root **or** a program's module specs under `docs/architecture/<program>/` — check the program's capability map (`docs/architecture/<program>-map.md`) for which specs are in scope, and ask if it is ambiguous which program you are planning. Then:

1. Enter plan mode — read only, no code changes
2. Identify the dependency graph between components
3. Slice work vertically (one complete path per task, not horizontal layers)
4. Write tasks with acceptance criteria and verification steps
5. Add checkpoints between phases
6. Present the plan for human review

**Where it goes — no condition to evaluate.** Write **`tasks/<program>-plan.md`** and **`tasks/<program>-todo.md`**. Always. `tasks/plan.md` and `tasks/todo.md` are **not a default and not a fallback** — they are the perf stream's files, kept only for history. Do not read them, do not test whether they are occupied, do not write to them. Pick the `<program>` id from the capability map or the branch name, and state the two paths you wrote.

**Before adding any pre-work gate** (a checkpoint that blocks *starting* a phase on an external decision, not one that reviews work already done): read `planning-and-task-breakdown`'s "Gates vs. checkpoints" section first. Reserve a hard gate for a genuinely irreversible action; everything else — approvals, coordination checks, cross-team asks — ships behind a reversible/tunable default and gets tracked as a non-blocking follow-up instead. Check a gate's premise against the project's actual source of truth (e.g. `decisions.md`) before writing it — "not yet approved" is a claim, not a fact, until it's been read that day. (Added 2026-09-05 after a plan froze itself on two gates that were either already resolved or never needed to block in the first place.)
