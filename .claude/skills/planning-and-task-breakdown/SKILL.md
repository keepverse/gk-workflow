---
name: planning-and-task-breakdown
description: Breaks work into ordered tasks. Use when you have a spec or clear requirements and need to break work into implementable tasks. Use when a task feels too large to start, when you need to estimate scope, or when parallel work is possible.
---

# Planning and Task Breakdown

## Overview

Decompose work into small, verifiable tasks with explicit acceptance criteria. Good task breakdown is the difference between an agent that completes work reliably and one that produces a tangled mess. Every task should be small enough to implement, test, and verify in a single focused session.

## When to Use

- You have a spec and need to break it into implementable units
- A task feels too large or vague to start
- Work needs to be parallelized across multiple agents or sessions
- You need to communicate scope to a human
- The implementation order isn't obvious

**When NOT to use:** Single-file changes with obvious scope, or when the spec already contains well-defined tasks.

## The Planning Process

### Step 1: Enter Plan Mode

Before writing any code, operate in read-only mode:

- Read the spec and relevant codebase sections
- Identify existing patterns and conventions
- Map dependencies between components
- Note risks and unknowns

**Do NOT write code during planning.** The output is a plan document and a task list saved to the task list target (see Output Files), not implementation.

### Step 2: Identify the Dependency Graph

Map what depends on what:

```
Database schema
    │
    ├── API models/types
    │       │
    │       ├── API endpoints
    │       │       │
    │       │       └── Frontend API client
    │       │               │
    │       │               └── UI components
    │       │
    │       └── Validation logic
    │
    └── Seed data / migrations
```

Implementation order follows the dependency graph bottom-up: build foundations first.

### Step 3: Slice Vertically

Instead of building all the database, then all the API, then all the UI — build one complete feature path at a time:

**Bad (horizontal slicing):**
```
Task 1: Build entire database schema
Task 2: Build all API endpoints
Task 3: Build all UI components
Task 4: Connect everything
```

**Good (vertical slicing):**
```
Task 1: User can create an account (schema + API + UI for registration)
Task 2: User can log in (auth schema + API + UI for login)
Task 3: User can create a task (task schema + API + UI for creation)
Task 4: User can view task list (query + API + UI for list view)
```

Each vertical slice delivers working, testable functionality.

### Step 4: Write Tasks

Each task follows this structure, whether it lands in the markdown task list or as an item in an external tracker (see Output Files):

```markdown
## Task [N]: [Short descriptive title]

**Description:** One paragraph explaining what this task accomplishes.

**Acceptance criteria:**
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]

**Verification:**
- [ ] Tests pass: [the repository's focused-test command]
- [ ] Build succeeds: [the repository's build command]
- [ ] Manual check: [description of what to verify]

**Dependencies:** [Task numbers this depends on, or "None"]

**Files likely touched:**
- `src/path/to/file.ts`
- `tests/path/to/test.ts`

**Estimated scope:** [Small: 1-2 files | Medium: 3-5 files | Large: 5+ files]
```

### Step 5: Order and Checkpoint

Arrange tasks so that:

1. Dependencies are satisfied (build foundation first)
2. Each task leaves the system in a working state
3. Verification checkpoints occur after every 2-3 tasks
4. High-risk tasks are early (fail fast)

Add explicit checkpoints to the task list target:

```markdown
## Checkpoint: After Tasks 1-3
- [ ] All tests pass
- [ ] Application builds without errors
- [ ] Core user flow works end-to-end
- [ ] Review with human before proceeding
```

## Gates vs. checkpoints — don't manufacture a stall

A **checkpoint** (Step 5) verifies work already done and asks a human to review it before the next
phase starts — that's healthy, and cheap to satisfy: the work exists, so there's something concrete to
review. A **gate** is different: it blocks *starting* a phase on an external decision that hasn't
happened yet. Gates are where a plan can quietly stop being a plan and become a stall, and it's easy to
write one without noticing, because at the moment of writing it *feels* like appropriate caution.

Before adding any gate that blocks starting a task or phase, check it against two questions:

1. **Is it actually irreversible?** The only case that justifies a hard pre-work halt is one where
   proceeding wrongly cannot be undone or detected after the fact — e.g. two concurrent processes about
   to collide on the same versioned/shared state with no way to repair the collision later. An
   approval, a style/architecture sign-off, a "does another team have a conflicting change queued"
   coordination check — none of these are that. They're answerable, and being wrong is correctable.
2. **Could the uncertain part ship behind a reversible default instead?** If the answer might not be
   known for a while, and the project has any config/tunable convention, prefer building against a
   sensible default now and letting a later pass correct it, over freezing every downstream task until
   someone answers. A gate that halts a whole plan because of one unresolved, correctable detail is a
   worse outcome than shipping with that detail wrong and fixing it later — the plan exists to keep
   work moving, and a gate with no forcing function or fallback defeats that purpose.

A gate that survives both checks needs a **named resolver and a stated default**: who answers it, and
what happens if the plan reaches that point before they do (ship with X defaulted and flag Y for a
later pass — never "wait indefinitely"). A gate with neither is not a safety mechanism, it's an
unanswerable question wearing a checkbox — write it as a fast, separately-tracked ask instead, and let
everything that doesn't actually depend on the answer keep moving.

**Concrete incident this section exists because of (2026-09-05, `base-defense`):** a plan wrote three
pre-work gates — one genuinely irreversible (two programs both about to bump the same hashed-state
version with no collision detection), and two that were not (a cross-program bug to raise "before
level 8," and a design-doc approval that, on inspection, had already happened a day before the plan was
even written and was only still showing as blocked because the map document hadn't been re-read against
its own source of truth). All three were treated identically as hard stops, and the owner had to
intervene to unblock a plan that had frozen itself on two answerable, non-urgent, already-resolvable
questions. The fix afterward was this section, not just unblocking that one plan.

## Task Sizing Guidelines

| Size | Files | Scope | Example |
|------|-------|-------|---------|
| **XS** | 1 | Single function or config change | Add a validation rule |
| **S** | 1-2 | One component or endpoint | Add a new API endpoint |
| **M** | 3-5 | One feature slice | User registration flow |
| **L** | 5-8 | Multi-component feature | Search with filtering and pagination |
| **XL** | 8+ | **Too large — break it down further** | — |

If a task is L or larger, it should be broken into smaller tasks. An agent performs best on S and M tasks.

**When to break a task down further:**
- It would take more than one focused session (roughly 2+ hours of agent work)
- You cannot describe the acceptance criteria in 3 or fewer bullet points
- It touches two or more independent subsystems (e.g., auth and billing)
- You find yourself writing "and" in the task title (a sign it is two tasks)

## Output Files

- **Plan document:** Save the implementation plan to `tasks/<initiative>-plan.md`. This is always a markdown file — design decisions, risks, and open questions don't map cleanly onto individual tracker issues.
- **Task list:** Record each task in the **task list target** (defined below).

Create the `tasks/` directory if it does not exist.

### Task List Target

The task list target is where tasks and checkpoints are recorded. It is defined once, here; every other reference in this skill defers to it.

- **Always the prefixed pair: `tasks/<initiative>-plan.md` and `tasks/<initiative>-todo.md`.** This is unconditional. Pick `<initiative>` from the capability map or the branch name, match the naming the project's existing plans already use, and state both paths when handing the plan back — `/build` cannot guess.
- **`tasks/plan.md` and `tasks/todo.md` are not a default and not a fallback.** In a repo running several initiatives they belong to whichever stream claimed them first and are kept for history. **Do not read them to check whether they are free, and never write to them.** The old "read both, then decide" rule made every session re-derive the same answer; there is no condition to evaluate.
- **External tracker:** if the project's agent rules (`CLAUDE.md`, `AGENTS.md`, etc.) or the user designate an issue tracker (e.g. GitHub Issues, Jira, Linear, `bd`/beads), create one tracker item per task instead of writing `tasks/todo.md`. Map the Step 4 structure onto the tracker's fields: acceptance criteria and verification steps in the item body, dependencies via the tracker's linking mechanism (`bd dep add`, "blocked by", etc.). Record Step 5 checkpoints as tracker items too, or as a checklist in the plan document if the tracker has no natural equivalent.

When using an external tracker, note it in `tasks/<initiative>-plan.md` (e.g. "Tasks tracked in Linear project FOO") so downstream steps and future sessions know where to look, and keep the plan document's Task List section as an ordered index of tracker item IDs or links rather than a duplicate checklist.

## Plan Document Template

```markdown
# Implementation Plan: [Feature/Project Name]

## Overview
[One paragraph summary of what we're building]

## Architecture Decisions
- [Key decision 1 and rationale]
- [Key decision 2 and rationale]

## Task List

### Phase 1: Foundation
- [ ] Task 1: ...
- [ ] Task 2: ...

### Checkpoint: Foundation
- [ ] Tests pass, builds clean

### Phase 2: Core Features
- [ ] Task 3: ...
- [ ] Task 4: ...

### Checkpoint: Core Features
- [ ] End-to-end flow works

### Phase 3: Polish
- [ ] Task 5: ...
- [ ] Task 6: ...

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Ready for review

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [High/Med/Low] | [Strategy] |

## Open Questions
- [Question needing human input]
```

When tasks live in an external tracker, keep the Task List section above as an ordered index of tracker item IDs or links instead of a duplicate checklist.

## Parallelization Opportunities

When multiple agents or sessions are available:

- **Safe to parallelize:** Independent feature slices, tests for already-implemented features, documentation
- **Must be sequential:** Database migrations, shared state changes, dependency chains
- **Needs coordination:** Features that share an API contract (define the contract first, then parallelize)

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll figure it out as I go" | That's how you end up with a tangled mess and rework. 10 minutes of planning saves hours. |
| "The tasks are obvious" | Write them down anyway. Explicit tasks surface hidden dependencies and forgotten edge cases. |
| "Planning is overhead" | Planning is the task. Implementation without a plan is just typing. |
| "I can hold it all in my head" | Context windows are finite. Written plans survive session boundaries and compaction. |

## Red Flags

- Starting implementation without a written task list
- Writing the bare `tasks/todo.md` instead of the prefixed pair, or writing it when the project has designated an external tracker (or scattering tasks across both)
- Tasks that say "implement the feature" without acceptance criteria
- No verification steps in the plan
- All tasks are XL-sized
- No checkpoints between tasks
- Dependency order isn't considered
- A pre-work gate blocks a phase on a question that isn't actually irreversible (an approval, a
  coordination check, "raise this with another team") instead of shipping behind a reversible default
- A gate has no named resolver and no stated default if the plan reaches it unanswered
- A gate's premise was never checked against the doc that would confirm or deny it (an "approval
  pending" gate is worth one read of `decisions.md` — or whatever the project's own source of truth is
  — before it goes in the plan at all)

## Verification

Before starting implementation, confirm:

- [ ] Every task has acceptance criteria
- [ ] Every task has a verification step
- [ ] Task dependencies are identified and ordered correctly
- [ ] Tasks are recorded in the prefixed task list target (`tasks/<initiative>-todo.md`), **never** the bare `tasks/todo.md`, and both paths were stated in the hand-off
- [ ] No task touches more than ~5 files
- [ ] Checkpoints exist between major phases
- [ ] Every pre-work gate (not checkpoint) has been checked against "Gates vs. checkpoints" above: it protects an irreversible action, it names who resolves it, and it states what happens by default if unanswered when the plan reaches it
- [ ] The human has reviewed and approved the plan

## See Also

Acceptance criteria are per-task and answer "did we build the right thing?". They sit on top of the project-wide Definition of Done, the standing bar every task clears before it counts as done. See `../../references/definition-of-done.md`.
