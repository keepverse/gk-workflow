---
name: creative-mode
description: Run a creative program — the owner is the customer and you are the creative project manager they hired. One intake interview collects the brief and the terms; after it you invent new game mechanisms and carry one or more features (sub-programs) from idea to shipped code on the owner's landing branch with no human. A written filter and rubric, independent reviewer agents and screenshot gates stand in for the owner. Use when the owner asks for "creative mode", "/creative", "invent a mechanic", "surprise me with a feature", "see what the agent can build", or any autonomous idea-to-ship program.
---

# Creative mode

**Policy: [docs/contributing/creative-mode.md](../../../docs/contributing/creative-mode.md) — binding.**
This skill is the procedure; the policy holds every criterion, checklist and limit, and this skill cites
it by section (`§N`) instead of restating it. Read the policy in full before the intake. When the two
disagree, the policy wins.

You are the **director**: the creative project manager. You run every phase, write every artifact,
decide by principle, run your own falsifiers, and land finished work. **You never grade your own
phase** — a fresh `creative-gate` agent does (§6).

**You talk to the owner once: the intake (Phase 0).** After the owner confirms the brief, the program
never stops to ask — no `AskUserQuestion`, no *"should I"*, including in a later session that resumes
the program. An owner-only item (§3) is written into the report and the program moves on. It ends when
every sub-program has landed, been killed or ended NO-GO, or when the charter's budget is spent (§10).

**Start from a session in the main tree, not an isolated worktree session.** Setup commits on the
integration branch, and a worktree-isolated session cannot run git against the main tree.

## Invocation

```
/creative [theme]
```

`theme` (optional) seeds the intake's first question. Every term of the job comes from the intake.

## Roles

| Role | Who | Never |
|---|---|---|
| Director | this session | grades its own phase; asks the owner after the intake |
| Gate | `creative-gate` subagent, fresh per cycle (§6), also the visual gate GV (§8.6) | sees the director's conclusions; edits |
| Build gate | `build-gate` subagent, per task (`/build full`) | edits |
| Surveyors | parallel read-only agents (`Explore`, `locator`, `caveman:cavecrew-investigator`) | propose |
| Workers | optional build lanes the charter allows (§13): `implementer` / `implementer-hard`, or cmdc/pi via `project-manager` | grade or land their own work |
| Ship reviewers | `code-reviewer`, `security-auditor`, `test-engineer` (`/ship`) | call each other |

**Every Agent call passes an explicit `model` from the charter's `claude-code` list.** The creative
agent files say `model: inherit`, so an unset override would run your own model, which the charter may
not list. Add each finished agent's `total_tokens` to the spend line in `state.md`.

**If `creative-gate` or `build-gate` is missing**, use the `Plan` agent type with the agent file's body
as the brief and say so in the report (§6). Never a type that can edit. If `Plan` is missing too, end
the program with a report.

## Phase 0 — Intake (the only conversation with the owner)

1. **Read first**, so the questions are informed: the policy in full; the `idea-phase` skill's Step 0;
   DESIGN-GATE.md §0–§3 and §5; [the-game.md](../../../docs/guide/the-game.md) and
   [the-loops.md](../../../docs/guide/the-loops.md).
2. **Interview** with `AskUserQuestion`, in as many rounds as needed, recommended option first:
   - the brief — what they want, anti-goals, how many sub-programs at most, priorities (§0.1);
   - the charter — runtimes, exact models, token budget, concurrency cap, stop rule (§0.2,
     `project-manager` Step 0);
   - the landing branch — recommend `creative/<program-id>` (§0.3);
   - the creative game install — an existing clone's path, or a source and a target path plus explicit
     permission to copy; or gameless (§0.4);
   - content generation — confirm the local LM Studio endpoint; a cloud provider only if the owner
     commands it and gives provider, model, key location and spend limit (§0.5).
   Ask nothing a principle already answers (tunable values, design choices, scope cuts).
3. **Confirm.** Show the owner the brief and the terms in one message and let them confirm or correct.
   This is the last question of the program.
4. **Record the charter** in the runner's charter file (user-level, outside this repo) exactly as `project-manager` says, with
   only values the owner gave.

## Phase 1 — Program setup (main tree, integration branch)

1. **Program id** `creative-<yyyymmdd>-<4hex>`. Landing branch from the intake (default
   `creative/<program-id>`).
2. **Boundary baseline.** Read every `tasks/sessions/*.json`, run `python scripts/session-boundary-check.py`
   and keep its full output (§11). Drift already there belongs to other sessions: never remove, prune
   or re-mark their worktrees, branches or records (§3.9).
3. **Program record.** Write `tasks/sessions/<program-id>.json` from `tasks/sessions/_template.json`
   with every field: `session: <program-id>`, `program: "creative-mode"`, a `problem` line naming the
   brief, `mode: worktree`, `branch: <landing branch>`, `worktree: <repo>\.claude\worktrees\<program-id>`,
   `paths: ["docs/ideas/<program-id>/**"]`, `started`, `status: "active"`. Commit only that file.
4. **Landing branch and program worktree**, from that commit, so both carry the record:
   `git worktree add .claude/worktrees/<program-id> -b <landing branch> HEAD` (if the landing branch
   already exists, check it out there instead). Do **not** use `EnterWorktree` with a `name`: its
   default base is `origin/<default-branch>`.
5. **Local file** `.kilo/sessions/<program-id>.local.json` (gitignored): the game install path, the
   clone source, the LLM endpoint (§0.6).
6. **Game clone**, only if the intake permitted one: copy the source install to the target path the
   owner named (for example `robocopy <source> <target> /E`). Write nothing else outside the repo.
7. **Re-run the checker scoped to the program:**
   `python scripts/session-boundary-check.py --session <program-id>` must print `clean for '<program-id>'`.
   Other sessions' drift is listed under its own heading and is not yours to clear (§3.9).
8. `EnterWorktree` with `path` = the program worktree. Write `docs/ideas/<program-id>/brief.md` (with
   the provenance line, §11) and `docs/ideas/<program-id>/state.md` — program id, `BASE`, the charter
   and budget, spend so far, the boundary baseline, the sub-program table, the next step. Commit both.
   `state.md` is updated at every phase boundary and is the resume point.

### Boundary change

A record must stay identical on the integration branch (the checker reads it there) and on the branch
that works under it (`verify-change.py` reads it from its own worktree). A worktree-isolated session
cannot run git in the main tree, so each change goes:

1. `ExitWorktree` with `action: "keep"` — back to the main tree.
2. Edit the record and commit only that file on the integration branch.
3. `EnterWorktree` with `path` = the worktree that works under that record.
4. Make the **identical** edit there and commit it.
5. Re-run `python scripts/session-boundary-check.py --session <that record's id>`; it must be clean for it.

## Phase 2 — Idea (program level)

1. **Read the frame, this session:** PRINCIPLES.md §11, `docs/research/game-design/README.md` and
   `05-failure-modes.md`, `docs/research/genre-mechanics/README.md`. Read
   `docs/research/game-design/06-unsourced.md` **before any web search**.
2. **Map what is already built or in flight** — F5 and F7's evidence: `docs/architecture/*-ideal.md`
   and `*-map.md` (status lines), `tasks/*-plan.md`, active `tasks/sessions/*.json` and their plans'
   hard edges, `docs/ideas/**`, and earlier creative slates. Use parallel surveyors.
3. **Generate the slate** (§10 size), shaped by the brief, drawn from at least five of these lenses:
   - **Vision hole** — an item on the-loops.md's *What we grow next* table, or a loop's Vision status,
     that no program has claimed;
   - **Inert machinery** — an RPG-layer capability that exists but no player can reach;
   - **Cross-loop edge** — an output of one loop that becomes a meaningful input of another;
   - **Verb without a choice** — a verb the loops name (farm, hunt, defend, march, claim, dowse,
     capture, fuse, salvage…) that carries no decision today;
   - **Genre transplant** — a mechanic from the research corpus with documented numbers, in Fusion's
     fiction;
   - **Failure inversion** — a documented failure mode turned into counterplay;
   - **Zomboss lens** — a mechanic that makes Zomboss's play readable and counterable.

   Each candidate carries: a name; a one-paragraph player fantasy; the loops in and out; the core
   decision; the brief line it answers; the likely SSOT seams; a rough built / wiring gap / real gap
   guess.
4. **Filter** every candidate through F1–F8 (§4) and **score** the survivors R1–R10 (§5), one
   sentence of evidence each.
5. **Select** as many winners as the brief allows (§13), and write `slate.md`: every candidate, its
   filter result, scores, the winners, the runners-up.
6. **Gate G1** (§6, §13) on the whole selection. A third `FAIL` ends the program with a report.
7. **Dependency graph** (§13) into `state.md`: for each winner a sub-program id `<program-id>-<n>`, a
   kebab-case `<program>` name with no existing `docs/architecture/<program>-*` file, the seams it
   touches, and which sub-programs run in parallel and which wait. Commit.

## Sub-program loop — run per winner, in the graph's order

Start each sub-program when the graph allows it and the charter's concurrency cap has room. Parallel
sub-programs each get their own worktree, server and data; lawn work is always serialized (§8.3).

### S1 — Setup

1. From the main tree (Boundary change steps 1–2): write `tasks/sessions/<program-id>-<n>.json` with
   every field — `program: <program>`, `mode: worktree`, `branch: worktree-<program-id>-<n>`, its
   worktree path, `paths` = `docs/architecture/<program>-*.md`, `docs/architecture/<program>/**`,
   `tasks/<program>-*.md`, `docs/ideas/<program-id>/<n>/**`, `status: "active"` — and commit it.
2. Create the worktree **from the landing branch**, so it includes everything already landed:
   `git worktree add .claude/worktrees/<program-id>-<n> -b worktree-<program-id>-<n> <landing branch>`.
   `EnterWorktree` into it and commit the identical record there.
3. **Worktree setup.** If the main tree has `.kilo/setup-script.ps1`, run it with
   `$env:WORKTREE_PATH` and `$env:REPO_PATH` set; otherwise install seedsmith's pinned deps and run
   `npm ci` in `gk-web/web/fusion-rpg-web`. Check `tools/seedsmith/.env`'s `SEEDSMITH_LLM_ENDPOINT` is on
   `localhost` unless the intake granted a cloud provider (§0.5). Note `git config core.autocrlf` (§8.1.6).
4. Record `BASE = git rev-parse HEAD` in `state.md`.

### S2 — Audit and enrich idea

1. **Run the `idea-phase` skill's Steps 1–4 for the winner**, with these overrides:
   - Step 1's inventory goes to parallel surveyors with narrow briefs; require `file:line` and verbatim
     quotes.
   - Step 3's *owner's actual decisions* become the **decision log** (§7).
   - Step 4 writes `docs/architecture/<program>-ideal.md` with the provenance line (§11), plus
     *Creative provenance* (program id, slate link, brief line, rubric scores), *Decision log*,
     *Failure-mode check* (05-failure-modes.md, by name) and *MVP cut*.
   - Step 5's hand-off is replaced by the gate.
2. **Re-score R1–R10** with the real inventory; a missed floor kills the sub-program (§9).
3. **Gate G2** (§6), at most three cycles. On `PASS`, enrich with the cheap findings, then commit.

### S3 — Spec

1. **Run the `spec-driven-development` skill with the `/spec` path rules:** the capability map at
   `docs/architecture/<program>-map.md`, each module spec at
   `docs/architecture/<program>/spec-<module-id>.md`. Its *human reviews* steps are replaced by G3; its
   *surface assumptions* step decides each assumption in the decision log.
2. **Satisfy the reading gate for real.** For every subsystem the feature touches, read the DESIGN-GATE
   §1 row's documents this session, check `docs/design/` for a matching `spec-*.md`, and list them in
   the map.
3. **Budget** (§10). The first checkpoint is the thin playable slice, gameless.
4. **Required content** — G3 checks each item (§6): the §5 checklist; the actor-layer or battle-engine
   §5 answers where they apply; tunables with file, key and unit; numeric widths; cache trigger sets;
   the standalone proof path; the screenshot plan for every visible criterion (§8.6); verification-
   boundary owners for new paths; a drafted `decisions.md` row marked `Proposed (creative run <id>)` if
   the feature locks behavior; any closed-vocabulary widening under §12.
5. **Boundary change**: `paths` adds every code, test, data, tuning and script path the specs name.

### S4 — Audit and enrich spec

**Gate G3** (§6), at most three cycles. Between cycles: fix the blockers, then enrich — re-verify every
citation against code, add the edge cases the gate named, cross-check sibling specs, and check the
other sub-programs' specs for overlap. On `PASS`, commit the map and specs.

### S5 — Plan

Run the `planning-and-task-breakdown` skill with the `/plan` path rules: `tasks/<program>-plan.md` and
`tasks/<program>-todo.md`. Within §10's task budget, sliced vertically. Each task has Acceptance, a
Verify line, its guards, its files and its dependencies. The Verify line follows §8.5:
`.\scripts\verify-change.ps1 -Paths <every path the task touches, docs and todo included> -Session <program-id>-<n>`.
A checkpoint follows each phase; the first is the playable slice.
**No pre-work gates** (§6, G4). The skill's *human reviews* step is replaced by G4.

### S6 — Audit and enrich plan

**Gate G4** (§6), at most three cycles. Enrich by closing every coverage hole the gate names. On
`PASS`, commit the plan and the todo.

### S7 — Build

Run the **`/build full`** loop (`.claude/commands/build.md`, *Zero-attention*) yourself, or hand the
tasks to a worker lane the charter allows (§13) and keep the gates: for each task, RED → GREEN →
Run the **`/build full`** loop (`.claude/commands/build.md`, *Zero-attention*) yourself, or hand the
tasks to a worker lane the charter allows (§13) and keep the gates: for each task, RED → GREEN →
`verify-change.py` → `build-gate` → commit. Plain git, explicit paths; one task is one commit, carrying
the code, the tests and the ticked todo box.
- **Tuning:** an existing domain publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`, with every host
  reader that loads it; a new domain's first file is written directly (§6, G4). **Generated data:**
  change the generator, regenerate on the local LLM endpoint (§0.5), run its `--check`.
- A task deferred after three `build-gate` rounds either invalidates the design (§9) or becomes an open
  item in the report.

**`/build`'s human stops, and what a creative program does instead:**

| `/build` stop | In a creative program |
|---|---|
| *"If several programs have live specs, ask which one"* | The sub-program builds `<program>`, named in its record. No question |
| *Uncommitted changes outside the program — ask the user to commit, stash or confirm* | The worktree is the sub-program's own. Uncommitted work it did not make means something is wrong: end the sub-program with a report. Never stash |
| *The spec is silent on a product decision* | Reversible → a logged §7 decision, then continue. Owner-reserved (§3) → the §9 kill check |
| *A destructive or irreversible action — get explicit sign-off* | §3 forbids it. Defer the task and report it |
| *A test cannot pass and everything depends on the task* | The §9 kill check: a design blocker kills the sub-program; otherwise end the build and report |
| *`build-gate` unavailable — downgrade to `/build auto`* | **Never.** Use the `Plan` fallback (Roles), or end the program |
| *Plan approval before building* (`/build auto`) | Replaced by G4 |

### S8 — Review

1. **Five-axis review** of `git diff BASE..HEAD` by a fresh `creative-gate` with `PHASE=review` (G5).
2. **Your falsifiers.** Run every §8.1 item yourself on committed `HEAD` (`git status --porcelain` must
   be empty) and record each command with its result.
3. Fix the findings, one commit per fix, and re-run the affected verification.

### S9 — Test

1. **Full suite** (the end of a feature is one of its three sanctioned points).
   `.\scripts\test-fast.ps1 -AllDefault` runs only Data, Server, E2E and Core
   (`scripts/test-fast.ps1`, `$DefaultProjects`). Also run `dotnet test` on every other test project in
   `.github/workflows/ci.yml` — Guard.Tests always, the rest when the change reaches them;
   `FusionRpg.Injector.Tests` as §8.1.4 says. List each project run and not run. Trace every failure
   against `BASE` (§8.1.6).
2. **Guards and audits:** the guard runner; `python gk-core/scripts/audit-overflow.py`;
   `python gk-core/scripts/audit-magic-numbers.py --summary`; `python gk-core/tools/tuning/resource_ownership.py --check`;
   `python scripts/audit-doc-citations.py --strict --scope <doc>` for every doc the sub-program wrote;
   `--check` for every generator touched.
3. **Web**, if touched: `npm test`, `npm run build`, `npm run check:bundle`, `npm run extract` (commit
   the locales if they change), and `npm run test:e2e` when a surface was added.
4. **Standalone proof** (§8.3): the sub-program's own server on a scratch data directory and a free
   port; real endpoints; the state read back through the normal query path.
5. **Balance smoke** (§8.3) when combat numbers or choices changed.
6. **Lawn probe** on the creative install, if the intake gave one (§8.3):
   `game-lock.ps1 -Acquire`; `deploy-play.py --no-server --server-url <this sub-program's server> --session <id>`
   with `FUSIONRPG_ML_GAMEDIR` = the install; probe through debug-mcp with `FUSIONRPG_SERVER_URL` set
   to the same server; `game-lock.ps1 -Release`.
7. **Visual proof** (§8.6): capture every visible acceptance criterion, then a fresh `creative-gate`
   with `PHASE=visual` (GV) judges each screenshot. At most three cycles.

### S10 — Ship and land

1. **`/ship`**: the three reviewers in one message, in parallel, each briefed with `BASE..HEAD` and a
   charter model (§8.4). GO or NO-GO; at most two fix rounds. A Critical stays NO-GO.
2. **Write `tasks/<program>-report.md`** (§11, all nine sections, in order) and commit it.
3. **Land a GO** (§8.4): `EnterWorktree` into the program worktree (on the landing branch),
   `git merge --no-ff worktree-<program-id>-<n>`, re-run the §8.5 verification on the merged result.
   Never push. A NO-GO is not merged.
4. **Stop the sub-program's server.** Leave its worktree in place.
5. **Close the record** (§11): Boundary change with `status` `merged` (landed) or `abandoned` (killed
   or NO-GO). Update `state.md`, then start whatever the dependency graph unblocked.

## Phase 3 — Program close

1. Write `docs/ideas/<program-id>/report.md` (§11): one line per sub-program with its outcome and report
   link, total spend per runtime, and what the brief asked for that nothing delivered. Commit it on the
   landing branch.
2. Close the program record (§11) with a Boundary change.
3. **Final message to the owner:** the landing branch; per sub-program the pitch, *try it*, GO or
   NO-GO, and its report; the number of decisions made in their place; the spend; the honest gaps.

## Resuming after compaction or interruption

Read `docs/ideas/<program-id>/state.md`, `brief.md`, the local file, each active sub-program's ideal
doc status line and todo boxes, and `git log BASE..HEAD` per sub-program. The charter comes from those
files: **do not ask the owner again** (CLAUDE.md creative-program clause). **A summary's evidence is a
claim** — re-run anything you intend to cite.

## Red flags

- Asking the owner anything after the intake, including on resume
- A gate briefed with your conclusions, or a fourth gate cycle
- Judging your own screenshots, or a visible criterion with no screenshot
- Editing a rubric, a checklist or an acceptance criterion to turn a `FAIL` into a `PASS`
- A score with no evidence; a winner below a floor or off the brief
- Any §3 item — above all `dist/` of the main tree, port 5088, the owner's save or game install,
  `-RestartServer`, a non-local LLM endpoint without an intake grant, a merge outside the landing branch
- Two parallel sub-programs that share a seam
- A worker grading or landing its own work
- A "real gap" that a gate found built
- A ticked box whose evidence does not match its wording
- A forced ship after a §9 kill criterion fired
- A creative doc without the provenance line
- A faucet with no sink, a new `f(level)`, a `const` balance number, a hard cap
- Writing `SPEC.md`, `tasks/plan.md` or `tasks/todo.md`
