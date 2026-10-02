# Creative mode — autonomous idea-to-ship runs

**Status: binding for every creative program.** Added 2026-09-19 at the owner's request: a fully
agent-orchestrated way to invent new game mechanisms and carry them from idea to shipped code, so the
owner can see what agents build on their own.

**The model: the owner is the customer; a creative project manager is hired to build features for
them.** The project manager (the **director**) talks to the owner exactly once, in an **intake**
(§0), to collect the brief and the terms of the job. After that it runs the whole job with no human:

> intake → idea → audit and enrich idea → spec → audit and enrich spec → plan → audit and enrich plan
> → build → review → test → ship

A creative **program** can hold several **sub-programs**, one per feature; the director decides how
they are ordered and which run in parallel (§13). The owner's usual idea gate is replaced by the brief
(§0), **written criteria (§4, §5) and independent reviewer agents (§6)**. Finished sub-programs land
on the landing branch the owner named at intake; the owner reviews that branch whenever they choose.

Procedure: the `creative-mode` skill (`/creative`). This file is the policy the skill loads. When the
two disagree, this file wins; fix the skill in the same change.

Who reads this: the director, the reviewer agents (the **gates**), and the owner reading the results.

### Owner rulings (2026-09-19)

| Topic | Ruling |
|---|---|
| Human contact | One intake at program start (§0). Nothing is asked after it, including when a later session resumes the program |
| Charter | Asked at intake and stored; it covers the whole program and every session that resumes it (§0.2) |
| Program shape | A creative program holds several sub-programs; the director decides ordering and parallelism per program (§13) |
| Landing | Collected at intake; the director merges finished sub-programs into that branch itself (§8.4) |
| Game | A **second game install**, never the owner's own. At intake the owner either gives the path of a clone or names a source to clone from and explicitly permits the clone (§0.4) |
| Visual proof | Screenshots are required evidence for anything visible; a fresh gate judges them (§8.6) |
| Content generation | Seedsmith runs on the local LM Studio model, which is free. A cloud provider only when the owner explicitly commands it at intake and gives its details (§0.5) |
| Session records | The run closes its own records (§11) |

## 0. Intake — the context collector

The only phase that talks to the owner. It runs once, at the start of a program, as a structured
interview (`AskUserQuestion`, several rounds if needed). The director asks for what it cannot decide by
principle and nothing else: design questions are never asked here, because deciding them is the job.

### 0.1 The brief

- **What the customer wants.** A theme, a loop, a player experience, a *"surprise me"*, or examples of
  what they liked or disliked. Also anti-goals: what they do not want.
- **How big the job is.** The most sub-programs (features) this program may ship.
- **Priorities.** What matters most if the budget runs short.

### 0.2 The charter

Runtimes, exact models per runtime, token budget (per program, and per lane where a runner is used),
the concurrency cap if any, and the stop rule, exactly as the `project-manager` skill's Step 0 asks
them. The director records them in the runner's charter file, which lives in the user-level
`cmdc-subagent` skill outside this repo (as that skill says), and in the program's local file (§0.6). **This is the owner-approved charter for the whole
program**: a session that resumes the program reads it from the file and does not ask again (CLAUDE.md
"Multi-agent runs start with the owner's charter", creative-program clause). A provider credit or quota
error still stops the lane (§10), and the program ends with a report instead of asking.

### 0.3 Landing

The branch that finished sub-programs merge into. The recommended answer is a dedicated branch,
`creative/<program-id>`, created from the integration branch at setup, so nothing reaches a shared
integration branch without the owner. The owner may name another branch. Push, pull requests and
`--force` stay forbidden whatever the answer (§3.8).

### 0.4 The creative game install

A creative program never uses the owner's own game install. The owner either:

- gives the path of a clone that already exists; or
- names a **source** install and a **target** path, and explicitly permits the director to copy the
  source there. The copy is the only write the program makes outside the repo and its scratch
  directories, and only to the target the owner named.

With neither, the program is gameless: lawn probes are reported as **not run**.

### 0.5 Content generation

The default is the local LM Studio endpoint seedsmith already uses
(`gk-forge/tools/seedsmith/.env.example:12`, `http://localhost:1234/v1/chat/completions`), which costs nothing.
Before any generation run the director checks that the configured endpoint is on `localhost`. A cloud
provider is used only when the owner explicitly commands it at intake and gives the provider, the
model, where the key lives, and a spend limit; otherwise a non-local endpoint is a §3.12 stop for that
task.

### 0.6 Where the answers go

| File | Holds | Tracked |
|---|---|---|
| `docs/ideas/<program-id>/brief.md` | The brief, the landing branch, the content-generation terms, the charter's models and budget | Yes |
| `.kilo/sessions/<program-id>.local.json` | Machine-local facts: the creative game install's path, the clone source, the LLM endpoint | No (`.kilo/sessions/` is gitignored) |

A machine-local path never goes into a tracked file (AGENTS.md "Git"). The intake ends with one
confirmation: the director shows the owner the brief and the terms, and the owner confirms or corrects
them. From then on the run never asks.

---

## 1. What creative mode changes, and what it does not

- **Every rule that binds a normal session binds a creative run.** AGENTS.md and CLAUDE.md hard rules,
  [DESIGN-GATE.md](../DESIGN-GATE.md) (the §1 reading gate, the §2 invariants, the §3 evidence rules, the
  §5 checklist), [PRINCIPLES.md](../PRINCIPLES.md), [session-boundary.md](session-boundary.md),
  [live-probe-standard.md](live-probe-standard.md),
  [validation-ssot.md](../architecture/validation-ssot.md),
  [tunables-ssot.md](../architecture/tunables-ssot.md) and
  [ssot-power-scale.md](../architecture/power/ssot-power-scale.md) all apply unchanged.
- **Creative mode removes one thing: the owner's approval between phases.** It adds rules. It never
  relaxes one.
- **The run invents a mechanism, never the frame.** The product vision —
  [the-game.md](../guide/the-game.md) and [the-loops.md](../guide/the-loops.md) — is the fixed frame the
  run invents inside (§3).
- **Nearest precedent, and where it stops.** Owner ruling R28
  ([spec-rulings-2026-09-18.md](../architecture/spec-rulings-2026-09-18.md)) let an implementation run
  execute the *owner-run* and *ask first* steps of an owner-approved plan under independent agent
  review. Creative mode uses agent gates one phase earlier, at the idea. It does **not** inherit R28's
  scope: R28 covered steps inside a plan the owner had approved, and nothing here has been approved.
  That is why open owner reservations stay reserved (§3.7).
- **The intake is the only human contact** (§0). The charter the owner states there satisfies CLAUDE.md
  "Multi-agent runs start with the owner's charter" for the whole program.

## 2. Where the gates go

| Gate in the normal flow | In creative mode |
|---|---|
| The owner picks and approves the idea | The owner states a brief at intake (§0). The director builds a slate of candidates, filters it against the brief and the rules (§4) and scores it (§5); an independent gate re-checks the slate (§6, G1) |
| The owner answers the ideal doc's open questions | The director decides each one by principle and logs it (§7); nothing irreversible is decided |
| The owner reviews the map, the specs and the plan | An independent gate per audit phase (§6, G2–G4), at most three cycles each |
| The owner looks at the game screen | Screenshots judged by a fresh gate (§8.6) |
| The owner approves the merge | The director merges each shipped sub-program into the landing branch named at intake (§0.3, §8.4). The owner reviews that branch and decides whether it goes further |

**Why this is safe.** Everything a program does lives on its own branches, in its own worktrees,
against its own server, data and game install (§8.3). Its work reaches only the landing branch the
owner named. The actions that cannot be undone are the ones §3 reserves to the owner, and the program
never takes them. A wrong idea costs a branch, not the game.

## 3. Owner-reserved — a creative run never decides these

If a candidate needs one of these, it fails the filter (§4) or is killed (§9). The run records the
fact in its report and moves on. **It never stops to ask**: after the intake the owner is absent by
design. The intake cannot grant any item on this list except where an item says so.

**Product**

1. A new named loop, or any change to [the-game.md](../guide/the-game.md) or
   [the-loops.md](../guide/the-loops.md). *"To add a new named loop, grow this page (owner)."*
2. Anything the-loops.md "What a feature owes this page" forbids: a currency or material that fails
   the bottleneck test or skips its [registry](../architecture/empire-resource-ssot.md) row, a player
   class, a stamina gate, a prestige wipe, a fourth clock, replacing expeditions with delves, making
   the lawn the whole game. Also a new element or a second element ring (the-loops.md, "Combat depth").
3. Fiction outside Fusion's world: its plants and zombies, Crazy Dave, Penny, Zomboss, the rift and its
   shards (`decisions.md` **Product vision** row).
4. A second front-end library that overlaps one already locked
   ([tech-stack.md](../design/tech-stack.md); AGENTS.md "Buy before build").

**Architecture**

5. Overturning or amending a locked `decisions.md` row, a DESIGN-GATE §2 invariant, or an AGENTS.md /
   CLAUDE.md hard rule. This includes widening a vocabulary whose members a `decisions.md` row
   enumerates — for example a new layer in the **Actor layer stack (2026-09-16)** row (§12). The run
   **may draft a new** `decisions.md` row for its own feature, marked
   `Proposed (creative run <run-id>)`. It becomes a lock only when the owner takes the landing branch further.
6. A new Unity write path ([PRINCIPLES.md](../PRINCIPLES.md) §3: *"Any new write path needs a
   `decisions.md` row and a guard extension first"*).
7. An **open** item a source document reserves to the owner: a question still addressed to the owner,
   or text that requires the owner's sign-off before an action (for example, diverging the ring and
   shield element matrices — DESIGN-GATE §1 *Elements* row: *"divergence is an Ask-first balance
   decision"*). Text that records a decision the owner already made (*"owner decision 2026-09-18: …"*)
   is a rule the run obeys, not a reservation of that subsystem.

**Irreversible or shared outside the branch**

8. Merging anywhere except the landing branch named at intake (§0.3); `git push`; a pull request;
   anything with `--force`. The program's own session-record commits (§11) are the only commits it
   makes on the integration branch.
9. Another session's claimed paths, dirty files, record, branch or worktree
   ([session-boundary.md](session-boundary.md) §6). The boundary checker's hint *"remove the
   worktree"* or *"mark the owning record abandoned"* is never taken for a record or worktree the run
   did not create — not even to make the checker print `clean` (§11).
10. The owner's live runtime: the published server under `dist/` and its `data/` save, port 5088,
    Vite's port 5173, Playwright's preview port 4173, and the owner's own game install. The program
    uses only the creative game install from the intake (§0.4)
    ([session-boundary.md](session-boundary.md) §7; §8.3 below).
11. Migrating, re-keying or deleting existing save rows. Additive schema (a new table, a new nullable
    column) is allowed and is scored under R9.
12. An LLM-pipeline call (seedsmith or any other) to an endpoint that is not on `localhost`, unless the
    intake granted that cloud provider explicitly (§0.5).
13. Starting any worker — a Claude Code native subagent, cmdc or pi — outside the charter from the
    intake: a runtime or model it does not list, or spend past its token budget (§0.2, §10).

## 4. The hard filter — pass or fail, before any scoring

A candidate passes only when every line holds, each with written evidence.

| # | Check | Evidence that counts |
|---|---|---|
| F1 | **Loop.** Names at least one loop from the-loops.md, and says what the mechanism takes from the game and what it gives back | The loop names, and the two edges |
| F2 | **Nothing in §3** | A line per §3 group saying why none applies |
| F3 | **RPG layer.** Designed against the RPG's own stat, effect and combat stack; it never depends on PvZ representing the concept (CLAUDE.md "Every RPG feature lives in the RPG layer") | The RPG-layer seams it uses |
| F4 | **Standalone-first.** Playable with the Fusion game closed once it unlocks; the lawn may enrich it and never gates it (DESIGN-GATE §2.9) | The gameless play path |
| F5 | **Not a duplicate.** No existing or in-flight program covers it | What was searched: `docs/architecture/*-ideal.md`, `*-map.md`, `tasks/*-plan.md`, active `tasks/sessions/*.json`, `docs/ideas/`, and earlier slates `docs/ideas/creative-*.md`. Overlap with an in-flight program is a **fail**, never a merge opportunity |
| F6 | **Mechanism, not magnitude.** A new decision or interaction, never a bigger number on an existing one | *"A faster Banshee is still a Banshee"* ([05-failure-modes.md](../research/game-design/05-failure-modes.md) §7) |
| F7 | **No collision with an in-flight seam change.** The candidate does not build on a seam an active session is reshaping — a save re-key, a golden re-bless, a hard edge (H1–H7) of a running program, a file an active lane is rewriting | Each active record's `problem` line and its plan's hard edges, and the seams the candidate touches. A candidate keyed to an identity or table that an active lane is re-keying fails |
| F8 | **Serves the brief.** It answers what the owner asked for at intake and hits none of the brief's anti-goals | The brief line it answers, and a line per anti-goal |

## 5. The rubric — the written stand-in for the owner's taste

Score each criterion 0–3. Every score carries one sentence of evidence; **a score with no evidence is
0.**

| # | Criterion | 0 | 3 | Floor |
|---|---|---|---|---|
| R1 | **Loop leverage** | An island: nothing in, nothing out | Fed by a place loop and feeds a spine loop | 2 |
| R2 | **Player decision** | Passive: no choice changes | A recurring choice with two or more viable answers that depend on the situation | 2 |
| R3 | **Legibility** | Learning it needs a table | One sentence in [glossary](../guide/glossary.md) words; the facts to learn grow with named rules, not with pairs (named reactions versus an N×N matrix — [game-design README](../research/game-design/README.md) finding 4) | 1 |
| R4 | **Build diversity** | One answer dominates, or *"nothing interesting happens until X"* | Widens the set of viable builds, has counterplay, and no gate converges every build (05-failure-modes.md §1, §3) | 2 |
| R5 | **Reuse leverage** | Mostly real gaps | Mostly built or wiring gaps; composes existing SSOTs — ActorHub, atoms, the battle engine, statuses, elements, resources, tuning | 1 |
| R6 | **Fiction fit** | Generic fantasy | Reads as Fusion: plants, zombies, Dave, Penny, Zomboss, the rift, shards | 1 |
| R7 | **Slice-ability** | Only works whole | A thin, playable, end-to-end slice fits the run budget (§10); the rest is named follow-ups | 2 |
| R8 | **Visibility** | Engine-only; a player never sees it | The owner can try it through a real surface — the web first; the lawn may enrich | 1 |
| R9 | **Risk surface** (scored inversely) | Touches many shared seams, none mitigated | Touches few; each touched seam — save schema, goldens and `RulesetVersion`, an economy faucet, the hot path, a closed vocabulary — has a named mitigation | 1 |
| R10 | **Novelty** | Finishes an existing plan, or a decision the game already offers somewhere | A decision the game offers nowhere today; the point of a creative run | 2 |

**Selection.** Every floor met and a total of at least 20 of 30. The highest total wins; a tie goes to
the higher R10, then the higher R5. R5 rewards reuse and the *Inert machinery* lens favours finishing
wiring, so R10's floor is what stops a creative run from becoming a wiring pass. The slate gate
re-scores independently (§6, G1); any criterion where the two scores differ by 2 or more is reconciled
in writing before selection.

**What the rubric does not measure: fun and priority.** Nothing written can measure fun. The rubric
measures the documented structural causes of un-fun — converged builds, illegible rules, passive
numbers, islands — which is what the research corpus records. Priority against the owner's roadmap is
the owner's call at merge: the report names the in-flight programs the feature competes with for
attention. The report must say that fun is unverified (§11).

## 6. Independent gates

**The director never grades its own phase.** Each audit phase ends with a `creative-gate` agent
([.claude/agents/creative-gate.md](../../.claude/agents/creative-gate.md)): a fresh context, read-only,
adversarial, returning `GATE: PASS` or `GATE: FAIL` with blockers.

Rules. They come from `doubt-driven-development` and from the 2026-09-18/19 autonomous runs, where
independent falsifiers caught defects that workers had self-certified:

- The gate receives **artifact paths, this file, and its phase checklist.** Never the director's
  conclusions, summaries or claims of what passed. Handing a reviewer your conclusion buys agreement.
- The gate **re-derives**: it opens every cited `file:line`, runs the commands it needs, and searches
  for what the artifact says does not exist.
- A `FAIL` turns each blocker into the next work item. Fix it, then spawn a **fresh** gate for the same
  phase. **At most three cycles per phase.** A third `FAIL` kills the candidate (§9); a third `FAIL` at
  G1, where no candidate is selected yet, ends the run with a report. A fourth cycle is not allowed.
- **A gate is read-only by construction.** If `creative-gate` or `build-gate` cannot be spawned, run
  the agent file's body as the brief through the `Plan` agent type, which has no Edit or Write tool,
  and say so in the report. Never fall back to an agent that can edit, and never to self-grading.
- **Never edit the checklist, the rubric or an acceptance criterion to turn a `FAIL` into a `PASS`.** A
  criterion that is itself wrong is recorded as a finding in the report; the candidate proceeds only if
  it passes the corrected criterion too.
- **Enrich, not only fix.** After a `PASS`, apply the gate's non-blocking findings that are cheap and
  in scope; list the rest as follow-ups. That is the "enrich" in each audit phase.
- `build-gate` ([.claude/agents/build-gate.md](../../.claude/agents/build-gate.md)) gates every build
  task, exactly as in `/build full`.

### Phase checklists

**G1 — slate** (end of *idea*)
- Re-check every candidate's F1–F8 evidence. Run F5's search again yourself.
- Re-score R1–R10 independently; list every delta of 2 or more.
- Look for a §3 item hidden in a candidate's details.

**G2 — ideal** (end of *audit and enrich idea*)
- The idea-phase shape: a *Which loop this extends* section; findings sorted **built / wiring gap /
  real gap** with `file:line`; prior art with numbers and sources; every tunable with its owning file.
- For every **real gap**, try to find an existing mechanism. A wiring gap reported as a real gap is a
  blocker.
- Open every **built** citation and confirm it says what the doc claims.
- Conformance, where it applies: actor numbers → the five answers of the DESIGN-GATE §1 *"Anything that
  changes what an actor's numbers ARE"* row; a battle mechanism →
  [battle-engine-ssot.md](../architecture/battle-engine-ssot.md) §5; an economy change → the faucet names
  its sink and the registry row passes P4 and P6; any level-derived number → `Θ` / `P(Θ)` only; any cap →
  soft and configurable; any balance number → a tunable.
- The failure modes of 05-failure-modes.md are checked **by name**.
- The decision log (§7): every decision names its principle and is reversible; none is in §3.
- No manufactured open questions: each open question is either a logged decision or a task.

**G3 — spec** (end of *audit and enrich spec*)
- The DESIGN-GATE §5 checklist is completed in the capability map, and every box it cannot tick is
  named.
- `python scripts/audit-doc-citations.py --scope <doc>` reports no HIGH finding for any doc the run
  wrote.
- Every acceptance criterion is testable, and says **order-independent** where play can vary
  (DESIGN-GATE §2.16).
- Every event-refreshed cache lists its full trigger set, including the key-set edge, with one test per
  trigger.
- Numeric widths and overflow behavior are stated; every tunable has a file, a key and a unit.
- The standalone proof path is stated: how the feature is exercised with the game closed.
- Every new source, test, data, tuning or script path has a verification-boundary owner planned
  (`gk-core/scripts/verification-boundaries.v1.json`; an unmapped production path is a defect). New rows there
  are a shared-surface change: the report's merge guide names them, because other programs edit that
  registry too. The run's own documents need no new row: `docs-and-assistant-config` owns them (§8.5).
- Module count is within budget, and the first checkpoint is a thin playable slice.

**G4 — plan** (end of *audit and enrich plan*)
- Coverage: every spec acceptance criterion maps to at least one task, and every checkpoint criterion
  is in the todo.
- Each task touches at most five files and has Acceptance, a runnable Verify (§8.5) and its guards.
- Dependency order is right; the riskiest work comes first.
- No pre-work gates. A creative run takes no irreversible action, so nothing needs one.
- A golden-moving task is single-cause and names its re-bless. A change to an existing tuning domain
  publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`. A **new** domain's first file (`v1`) is written
  directly, because the tool only bumps a domain that already exists
  (`gk-core/tools/tuning/publish.py:60-70` returns nothing when no `v*` file exists); the report lists it under
  shared-surface changes. Generated data changes through its generator, never by hand.
- No test pins a population count or generated text ([validation-ssot.md](../architecture/validation-ssot.md)).

**G5 — review** (during *review*): the five-axis review of `BASE..HEAD`, plus confirmation that the
director ran every §8.1 falsifier and that each result is recorded.

**GV — visual** (during *test*, once per acceptance criterion a player can see): the gate receives the
screenshot files, the acceptance criterion's exact wording, and the capture steps. Nothing else. It
answers, per screenshot: does the image show what the criterion says, and is anything on screen wrong
that the criterion does not mention (§8.6).

## 7. Decisions made in the owner's place

The idea phase normally ends with questions for the owner. In creative mode each one becomes a logged
decision:

| Question | Options | Choice | Principle it follows | How to reverse it |
|---|---|---|---|---|

- **Decide by a principle the repo already states.** A tunable value is picked by principle, published
  and marked untuned (owner ruling 2026-09-19: never ask the owner to pick a calibration value); a
  level-derived number reads the one ladder; a scope question takes the thinner slice.
- **Only reversible decisions.** A decision whose wrong answer cannot be undone on the branch is
  either in §3 or a sign that the candidate is too big.
- The log lives in the ideal doc and is copied into the report (§11). It is the owner's first read.

## 8. Build, review, test, ship — the evidence rules

The normal rules apply: `verify-change.py` per change, the guards, the full suite at the end of a
feature, and [live-probe-standard.md](live-probe-standard.md) for anything live. Creative mode adds the
checks that caught every defect autonomous workers self-certified in the 2026-09-18/19 runs.

### 8.1 Falsifiers the director runs itself

Never delegated to the agent that built the change.

1. **Acceptance against the test body.** For each acceptance line, read the test: does Arrange build
   the precondition, and does Assert match the wording? A test can pass while asserting the opposite
   of its own name.
2. **Recompute every numeric claim**, units and arithmetic included. A thorough-looking derivation is
   not proof: a calibration error once passed review because its derivation looked careful.
3. **Grep new code and every evidence note** for `remains|owed|no host|not wired|no-op|stub|TODO`. An
   unwired mechanism reads as green tests plus one honest sentence.
4. **Every host is configured.** A new static hub or Configure-or-throw accessor must be configured in
   every host and test bootstrap that reaches its reader — Server, E2E, Injector. Run the Server and
   E2E test projects whole. `FusionRpg.Injector.Tests` needs interop references from a game install
   and is not in CI (AGENTS.md): run it whole when `FUSIONRPG_GAME_DIR` points at a game that has
   them, and otherwise report it as **not run**, with the reason.
5. **The published output carries the new data.** Prove it by starting the run's own server from its
   own publish output and reading the data back through an endpoint. A missing copy rule once shipped
   an empty action catalog that every test missed.
6. **"Pre-existing" is traced, never adopted.** A failure called pre-existing is run on the base commit
   in a separate checkout and tied to a cause older than the run. Worktree artifacts — CRLF from
   `core.autocrlf`, missing gitignored inputs — are named as such.
7. **Falsifiers run against committed `HEAD`**, never against a tree with uncommitted edits.

### 8.2 Honesty rules

From the 2026-09-15 goal-loop incident, where boxes were ticked without matching evidence.

- Tick a box only when the evidence matches its exact wording. Never reword a criterion in the commit
  that ticks it.
- Never weaken a test, a guard or a criterion to pass.
- An aggregate counter never proves a per-entity claim. Debug-fabricated state never proves a
  server-side claim ([live-probe-standard.md](live-probe-standard.md)).
- An honest open box beats a false tick. *"Not verified"* is a valid line in a report.
- After context compaction, re-read files and `git log` for evidence. A summary's *"N/N passed"* is a
  claim until re-run.

### 8.3 Running things

- **The run's own server.** Built from the run's worktree into a scratch directory, never into
  `dist/`:
  1. `npm run build` in `gk-web/web/fusion-rpg-web` — it writes the UI into `src/FusionRpg.Server/wwwroot`
     (`vite.config.ts` `outDir`).
  2. `dotnet publish gk-core/src/FusionRpg.Server -c Release -o <scratch>\server`.
  3. `Start-Process <scratch>\server\FusionRpg.Server.exe -WorkingDirectory <scratch>\server` with
     `FUSIONRPG_DATA` = `<scratch>\data`, `FUSIONRPG_URLS` = `http://127.0.0.1:<free port>` (never
     5088, 5173 or 4173) and `FUSIONRPG_NO_BROWSER=1`. The working directory matters: when
     `FUSIONRPG_DATA` is set, the server does not pin its content root to the exe folder
     (`gk-core/src/FusionRpg.Server/Program.cs:13-17`), so `wwwroot` resolves against the working directory.
  `Start-Process` is required because a server started inside a tool call dies with that call. Stop it
  at the end of the run.
- **"Try it" uses that server's own page** (`http://127.0.0.1:<port>/`), never `npm run dev`: in dev
  mode the web client hardcodes the owner's server (`gk-web/web/fusion-rpg-web/src/lib/bus/rest.ts:1`,
  `http://127.0.0.1:5088`).
- **The standalone proof is mandatory.** Exercise the feature through the run's own server with the
  game closed, through real endpoints on rows that real play could create, and read the state back
  through the normal query path — RPG Server scope in live-probe-standard.md terms.
- **Balance smoke.** When the feature changes combat numbers or choices, run
  [gk-core/tools/CombatSim](../../gk-core/tools/CombatSim/README.md) (and `gk-forge/tools/DominanceBaseline` where it applies) with
  and without the feature and report the readings. A mechanic that makes one answer win in every
  scenario fails R4 and goes back to *audit and enrich idea*, not to tuning.
- **The game — only the creative install from the intake** (§0.4), never the owner's own.
  - **One user at a time — the game lock.** Before a deploy, take the install's lock:
    `.\scripts\game-lock.ps1 -Acquire -GameDir <install> -Session <sub-program id>`; release it with
    `-Release` when the probe ends. `deploy-play.py` refuses to deploy into an install another
    live session holds. The lock stores the absolute path of the holder's session record, because each
    worktree has its own `tasks/sessions/`; a lock whose stored record is missing or no longer
    `active` is stale, `-Acquire` takes it over and `deploy-play.py` does not block on it. `-Acquire`
    creates the lock file atomically, so two sub-programs cannot both win it. The lock is also how
    parallel sub-programs serialize their lawn work.
  - **Deploy from the sub-program's worktree**, pointing the game at the sub-program's own server:
    `$env:FUSIONRPG_ML_GAMEDIR = <install>` then
    `python scripts\deploy-play.py --no-server --server-url http://127.0.0.1:<its port> --session <id>`.
    `-ServerUrl` writes that URL into the install's `fusionrpg.cfg` and the launch environment, and is
    refused unless it is loopback and `-NoServer` is set without `-RestartServer` (`-RestartServer`
    stops whatever listens on 5088, which is the owner's server). `deploy-play.py` resolves its root
    from its own location (`gk-fusion/scripts/deploy-play.py:56`), so it builds into that worktree's `dist/`,
    and it only counts a game process started from this install as "already running", so the owner's
    own game running elsewhere does not stop the launch.
  - **Drive the probe through debug-mcp at the same server.** The debug-mcp tools read
    `FUSIONRPG_SERVER_URL` per call (loopback only; default 5088 —
    `gk-fusion/tools/debug-mcp/tools/debug_call.py` `base_url`). The MCP server the session already runs keeps
    the environment it started with, so a sub-program calls the tool functions from Python with the
    variable set, for example
    `$env:FUSIONRPG_SERVER_URL='http://127.0.0.1:<port>'; python -c "from tools.debug_screenshot import screenshot; ..."`
    run in `gk-fusion/tools/debug-mcp`.
  - Probes follow `live-lawn-quick-start` and live-probe-standard.md.
- **Content generation** runs on the local endpoint (§0.5). Check `SEEDSMITH_LLM_ENDPOINT` is on
  `localhost` before every generation run; LM Studio not answering there is a blocker for that task,
  never a reason to switch to a cloud provider.

### 8.4 Ship

`/ship` runs its three reviewers — `code-reviewer`, `security-auditor`, `test-engineer` — in parallel
and returns GO or NO-GO. Each reviewer is briefed with the range `BASE..HEAD`; the diff is committed,
so "the staged changes" would be empty. A NO-GO is fixed and re-run at most twice; a NO-GO that
remains is reported as NO-GO. `/ship`'s *"NO-GO unless the user explicitly accepts the risk"* has no
taker in a creative run: nobody accepts risk on the owner's behalf, so a Critical stays NO-GO.

**Landing.** A GO sub-program is merged by the director into the landing branch from the intake
(§0.3) with `git merge --no-ff`, and the §8.5 verification is re-run on the merged result. A failure
there is fixed on the sub-program's branch and merged again; the merge is never amended. A NO-GO
sub-program is not merged: its branch stays, and the report says why. Never push.

### 8.5 Which verification covers which path

Pass `.\scripts\verify-change.py -Paths <every path the task touched> -Session <sub-program id>`
**every** path, documents included:

- **Documents and assistant config** (`docs/**`, `.claude/**`, `.agents/**`, `.commandcode/**`,
  `CLAUDE.md`, `AGENTS.md`) resolve to the `docs-and-assistant-config` boundary unless a more
  specific owner claims them, and every Markdown path also gets
  `audit-doc-citations.py --strict --scope <that file>`. A doc the run touches must have no HIGH
  citation finding, including older ones in that file.
- **`tasks/**`** runs the `session-boundary` guard, and `verify-change.py` hands it `-Session`: the
  guard fails only on drift that names this sub-program (its record, its branch, an overlap with its
  paths). Other sessions' drift is printed and does not fail, and is never the run's to clear (§3.9).
- The setup baseline (§11) stays useful as a record of what was already broken when the program
  started.

### 8.6 Visual proof — screenshots judged by a fresh gate

The owner's eyes caught a defect that every telemetry check had passed (CLAUDE.md "A debug API may
trigger a real operation, never fabricate its result", 2026-09-13). In a creative program a gate
stands in for them.

- **Every acceptance criterion a player can see needs a screenshot**, on the lawn or on the web: the
  game through debug-mcp's `debug_screenshot` or a desktop capture, the web page through Playwright or
  Chrome DevTools. Save the images under the sub-program's evidence folder with the capture steps.
- **A fresh `creative-gate` judges them (GV, §6)**, briefed with only the images, the criterion's exact
  wording and the capture steps. The director's own reading of its screenshots is not evidence.
- **The state behind the screen is still read back through the normal path** (live-probe-standard.md).
  A screenshot proves what is shown; it never proves persistence or server-side state.
- A `FAIL` follows §6: the defect becomes the next work item, at most three cycles.

## 9. Kill criteria — a killed idea is a result

Kill the current candidate when:

- a gate fails three cycles in one phase;
- a §3 item turns out to be required;
- the real-gap scope exceeds the budget even after the MVP cut;
- a build blocker invalidates the design, not only the code.

On a kill: mark the ideal doc `Killed (creative run <run-id>): <reason>`, commit it, and take the next
candidate on the slate. At most two restarts, so at most three candidates per run. When every
candidate is killed, the run ends with a report that says so and why.

**A forced ship is the failure mode. An honest kill report is useful.**

## 10. Budget

Defaults, per sub-program unless a row says otherwise; the intake may change any of them.

| Knob | Default |
|---|---|
| Sub-programs per program | from the brief (§0.1) |
| Candidates on the slate (per program) | 8, or twice the sub-program count if that is more |
| Restarts after a kill | 2 |
| Modules in the capability map | at most 5 |
| Tasks in the plan | at most 30 |
| Gate cycles per audit phase | at most 3 |
| `build-gate` rounds per task | at most 3 |
| `/ship` NO-GO fix rounds | at most 2 |
| Agent runtimes, models, token budget, concurrency, stop rule | **No default.** The charter from the intake (§0.2), for the whole program. The director sums `total_tokens` from each subagent's completion notice; when the budget is spent it spawns nothing more and ends the program with a report |
| Content generation | The local LM Studio endpoint, no call limit. A cloud provider only as the intake granted it (§0.5) |
| Game | The creative install from the intake (§0.4); gameless without one |
| Landing | The branch from the intake (§0.3); recommended `creative/<program-id>` |

## 11. Artifacts, provenance and the report

| What | Path |
|---|---|
| Session records | One per program (`tasks/sessions/<program-id>.json`, which owns the landing branch and `docs/ideas/<program-id>/**`) and one per sub-program (`tasks/sessions/<program-id>-<n>.json`), each with every field of `tasks/sessions/_template.json` (`session`, `program`, `problem`, `mode: worktree`, `branch` — the landing branch for the program, `worktree-<program-id>-<n>` for a sub-program — `worktree`, `paths`, `started`, `status: active`). A record must exist with identical content on the integration branch, because `session-boundary-check.py` reads it there, and on the branch that works under it, because `verify-change.py` reads it from its own worktree and refuses a path outside `paths`. The program record is committed on the integration branch before the landing branch is created from it; a sub-program record is committed on the integration branch and then identically as the first commit of the sub-program's branch. Every later change is made identically on both (the skill's *Boundary change* procedure); identical changes merge cleanly |
| Boundary baseline | The checker's full output at setup (skill Phase 1), kept in `state.md`. Drift already present then belongs to other sessions; the run's check is that no **new** line names its own record, branch or paths (§8.5) |
| Record lifecycle | **The program closes its own records.** A sub-program's record becomes `merged` when it lands on the landing branch, `abandoned` when it is killed or ends NO-GO. The program record closes when its last sub-program closes: `merged` if any sub-program landed, otherwise `abandoned`. Each close is a boundary change (the skill's procedure) |
| Brief and intake | `docs/ideas/<program-id>/brief.md` (tracked) · `.kilo/sessions/<program-id>.local.json` (machine-local) — §0.6 |
| Slate and run state | `docs/ideas/<program-id>/slate.md` and `docs/ideas/<program-id>/state.md` (the `<program-id>` is `creative-<yyyymmdd>-<4hex>`; in older text `<run-id>` means the same id) |
| Sub-program ids | `<program-id>-<n>` for records, branches and worktrees; each sub-program also gets a kebab-case `<program>` name for its docs |
| Program report | `docs/ideas/<program-id>/report.md` — one line per sub-program (landed, NO-GO, killed) linking its report, total spend per runtime, and what the brief asked for that nothing delivered |
| Ideal | `docs/architecture/<program>-ideal.md` |
| Capability map and specs | `docs/architecture/<program>-map.md` · `docs/architecture/<program>/spec-<module-id>.md` |
| Plan and todo | `tasks/<program>-plan.md` · `tasks/<program>-todo.md` |
| Report | `tasks/<program>-report.md` |

**Provenance.** Every document the run writes opens with
`**Status:** creative run <run-id> — agent-originated, not owner-reviewed.` Every `decisions.md` row it
drafts is marked `Proposed (creative run <run-id>)`. Until the owner takes the landing branch further and updates those lines, no
other session cites a creative document as an owner-approved design.

**The report** (`tasks/<program>-report.md`), in this order:

1. **The pitch** — the mechanism in player language, in five sentences or fewer, and the loops it
   touches.
2. **Try it** — exact steps to experience it, gameless first.
3. **What was built** — modules, commits, files.
4. **Decisions made in the owner's place** — the §7 log.
5. **Shared-surface changes** — closed-vocabulary widenings, new tunable files and keys, golden moves
   with cause and commit, `RulesetVersion` bumps, schema additions, economy registry rows, drafted
   `decisions.md` rows.
6. **Evidence** — each gate's verdict and cycle count; tests, guards and audits with their decisive
   lines; the standalone proof; balance-smoke readings. Short tables only.
7. **Honest gaps** — fun is unverified; what was not run and why; follow-ups not built.
8. **Merge guide** — how to merge, the conflicts to expect, and how to roll back (drop the branch, or
   revert the range).
9. **The slate** — the runners-up, and why each was not chosen.

## 12. Closed vocabularies

Widening a closed vocabulary — atom kinds, attach points or triggers; `ActionCategory`, `ActionTag`,
`ActionKind`, `ActionTargetMode`; status kinds — is allowed only when no `decisions.md` row enumerates
its members, and when:

- the ideal doc shows, with `file:line`, that no existing member can express the need. Composition is
  tried first;
- the gate for that phase checks the claim itself;
- the DESIGN-GATE §1 row and every count that names the vocabulary move **in the same change** (the
  atom row has gone stale four times because they did not);
- the report lists the widening under shared-surface changes.

A vocabulary that a `decisions.md` row enumerates — the actor layer stack (**Actor layer stack
(2026-09-16)**), the actor resource set — is widened only by amending that row, which §3.5 reserves to
the owner. Before widening anything else, search `decisions.md` for a row that lists its members.
Elements and the element ring are product vision (§3), not a widenable vocabulary.

## 13. Program and sub-programs

A creative program is one intake, one brief and one landing branch. It ships up to the brief's number
of **sub-programs**, one feature each.

- **Selection.** Phase 1 builds one slate for the program. The director selects as many winners as the
  brief allows, all passing §4 and §5, and G1 gates the selection as a whole: it also checks that no two
  winners are the same idea twice and that together they answer the brief.
- **Each sub-program runs Phases 2–10 on its own** — its own session record, branch, worktree,
  server and data (§8.3), gates and report. A kill (§9) ends that sub-program only; the director may
  promote the next runner-up from the program slate into its place, within §10's restart limit.
- **The director decides ordering and parallelism per program.** Before Phase 2 it writes a dependency
  graph into `state.md`: two sub-programs run in parallel only when they share no files, no seam an
  edit would change (save schema, goldens, a tuning domain, a closed vocabulary, a registry file) and
  no ordering; otherwise the later one waits for the earlier to land and branches from the landing
  branch. Concurrency never exceeds the charter's cap. Lawn work is always serialized (§8.3).
- **Who does the work.** The director may run a sub-program itself or give its build phase to a
  worker lane the charter allows (a native `implementer` / `implementer-hard` agent in its own worktree,
  or a cmdc/pi lane through the `project-manager` skill). Gates, falsifiers (§8.1), visual judgment
  (§8.6) and landing (§8.4) stay with the director: a worker never grades or lands its own work.
- **Resuming.** The program's state lives in `docs/ideas/<program-id>/state.md` and its local file. A
  session that resumes the program reads both, the charter included, and continues without asking.
