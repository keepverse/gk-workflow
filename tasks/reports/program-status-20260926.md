# Program status reader — `gk-core/scripts/program_status.py`

**Session:** `program-status-tool-20260926` (worktree `manage/program-status-tool-20260926`,
worktree path `.claude/worktrees/program-status-tool-20260926`, forked from
`features/mega-merge@2a7597ab1`).
**Problem:** the owner asked for one reliable answer to "what have we done, what is left", and for
every agent to be required to read it. Until now that answer was reconstructed by hand each time, and
the two reconstruction habits that had already been paid for once (counting `- [ ]` lines; reading a
lane's own `status.json`) were still available by default.

---

## 1. What shipped

| Path | Change |
|---|---|
| `gk-core/scripts/program_status.py` | **new.** The reader. Task-block status per program, session fences, acceptance evidence, ledger health, head state, todo-header reconciliation, `--json`, named refusals, hard timeouts. |
| `gk-core/scripts/audit-program-pipeline.py` | `iter_task_blocks` extracted from `task_blocks` (which is now the counting view over it) so there is **one** block rule; `block_identity` / `block_title` / `TaskBlock` / `BLOCKED_SIGNAL_RE` added. |
| `gk-core/tests/tools/test_program_status.py` | **new.** 25 tests, incl. two that read the PowerShell harnesses to prove the copied vocabularies have not drifted. |
| `gk-core/scripts/verification-boundaries.v1.json` | the new tool + its tests + `todo-shapes.v1.json` folded into the **existing** `pipeline-audit-scripts` owner (see §4 for the rejected first attempt). |
| `AGENTS.md` | new **"Status gate"** subsection under *Manager and lane tooling*, with the tool in the tool table; plus three citation repairs (§5). |
| `scripts/audit-doc-citations.py`, `gk-core/tests/FusionRpg.Guard.Tests/DocCitationAuditTests.cs` | one `status.json` entry in the EXEMPT 1 closed list, with the test row that keeps "a name not on the list still reports HIGH". |
| `tasks/sessions/program-status-tool-20260926.json` | the session record (fence widened twice; see §6). |

## 2. The answer, on the current head

`python gk-core/scripts/program_status.py` at `2a7597ab1`:

- **118 programs** — 116 measured, 2 unmeasured (`player-guide`, `world-map-gaps-followup`: no shape
  declared, so **not** "0 open").
- **670 open task blocks, 2 889 done**; 147 open blocks carry a blocking signal in their own text.
- Largest remainders: `trade-network` 162 (0 done — an idea-phase todo, never built),
  `npc-story-events` 93, `narrative-seed` 50, `combat-ai` 27, `onboarding-rift` 26, `solid-enforcement` 22.
- 8 active session records; the only program currently fenced by an active session is
  `rpg-simulator` (4 records).
- 78 acceptance artefacts, **all** naming a SHA already in this head; 54 GREEN, 14 RED-KNOWN,
  8 UNATTRIBUTED, 2 RED — i.e. the not-green set is entirely historical, not open debt on this head.

Two readings worth the manager's attention, both surfaced by the tool rather than by hand:

1. **`trade-network` has 162 open blocks and 0 done.** Either it is an approved idea with no
   implementation, or its todo was copied in and never started. The tool cannot tell which — that is
   an owner/program decision, and it is now a 30-second question instead of a reading exercise.
2. **The not-GREEN acceptance set is fully contained in this head** (`notInThisHeadAndNotGreen` is
   empty), so those 24 artefacts are superseded lanes, not a red suite. Recorded as a reading.

## 3. What it refuses, and why that matters

Nine named refusals, exit 2, nothing on stdout: `NO-REPO`, `SHAPE-MAP-UNREADABLE`, `NO-TODO-FILES`,
`BLOCK-RULE-MISMATCH`, `GIT-UNAVAILABLE`, `TIMEOUT`, `SESSION-RECORD-INVALID`,
`ACCEPTANCE-ARTEFACT-INVALID`, `LEDGER-UNREADABLE`, plus `NO-REPORT` for anything unexpected.

Each one exists because the empty report is the dangerous output:

- `SHAPE-MAP-UNREADABLE` — the shape map is read **before** the block rule is imported, so a missing
  marker map is a named refusal rather than an opaque import error. (It was an opaque import error
  first: the fixture run proved it.)
- `BLOCK-RULE-MISMATCH` — the per-block enumeration is cross-checked against the counting view for
  every file. Two counters over one corpus is the defect the refactor existed to prevent; the
  cross-check is what keeps them from re-forking.
- `ACCEPTANCE-ARTEFACT-INVALID` — an artefact whose file name names a different SHA than its own
  `sha` field is refused. That is the "a stale artefact for an already-merged SHA reads as a fresh
  verdict" trap from AGENTS.md, made a refusal instead of a footnote.
- `SESSION-RECORD-INVALID` — a record outside the closed `active/merged/abandoned` enum, or whose
  `session` does not match its file name, is refused. The vocabularies are read out of
  `session-boundary-check.py` and `accept_lane.py` and **re-read by the tests**, so the copies
  cannot drift alone. (`_template.json` is skipped, matching the checker's own `_`-prefix rule.)

## 4. Todo headers that no longer match the tree — and a check that had to be made precise first

A status line is what a reader believes without reading the body, so a stale number there is worse
than no number. The reader now prints every numeric self-claim in a todo's **header** beside what the
block rule measures today, and classifies it: `confirmed`, `falsified`, `scoped`, `unclear`.

**The first version of this check accused four programs falsely.** Each class is now a test:

| False positive | Real line it misread | Fix |
|---|---|---|
| tail of a range | `backlog-clear:17` "Phases 6–**10** open" | lookbehind rejects a number preceded by a dash or word char |
| number inside a task id | `story-scene:14` "**F7** done" | same lookbehind |
| a claim in a *task row*, not a header | `gui-lego:28` "queue **P0** done" | the header now ends at the first task block, not at a fixed line count |
| `open` as an adjective | `passive-tree:290` "9 **open** prefix families", `:1973` "§14 **open** question" | a state reading has punctuation after the word; an adjective reading has a noun |

**What survives: 2 falsified claims, both genuine, both in one file** —
`tasks/combat-ai-todo.md:9` says "**46 done, 25 open**" and the file measures **47 done, 27 open**.
Its line also says "Counted as TASK BLOCKS, never checkbox lines" and then gives the measurement as
``grep -c '^- \[x\] \*\*'`` — it states the right rule and cites the forbidden method. Routed to
`combat-ai`; **not** fixed here, because that todo belongs to another program (§6).

The other 25 header claims are `scoped` (a wave, a phase) or `unclear` (a bare "N tasks" describing
the file) and are printed without a verdict, because calling those false is the same mistake in the
other direction.

**A separate contradiction, found by hand while classifying the big remainders and not yet in the
tool:** `tasks/onboarding-rift-todo.md`'s header claims (2026-09-14) that "the durable story ledger,
media provenance registry, server contract … are implemented", while its own Tasks 6 and 7 — *story
ledger schema and bootstrap*, *story read/acknowledgement primitives* — are both `OPEN`, and the tree
contains no story-ledger or media-provenance implementation (only the **npc-story-events** specs at
`docs/architecture/npc-story-events/spec-story-ledger.md`). 26 open / 0 done. This looks like a header
describing a *different* program's work; which side is wrong is not something I can settle by reading,
so it is routed, not declared.

## 4b. The ledger↔todo reconciliation debt — and the number I refuse to publish

`combat-ai`'s stale header turned out to be sharper than a stale number. Its ledger's last event is
`2026-09-23T06:26:55Z` and it holds **zero** `state: done` events after that date, yet **six commits
on 09-24/25 edited `tasks/combat-ai-todo.md` and none touched `tasks/combat-ai-ledger.jsonl`**. So the
todo's counts moved without a record. That is a ledger-reconciliation gap, not a stale figure, and it
sent me measuring whether it is one file or a pattern.

Measured across every program that has both a todo and a ledger (27 programs):

- **4 cannot be reconciled by id at all** — `battle-derived-wire`, `combat-math-dedup`,
  `species-gear-chain`, `story-scene` are all `H-task`, and their block headings (`### Task 1: …`)
  carry no id for any of their 19/18/66/28 blocks. Their ledgers nevertheless record 9/13/18/6 done
  entries, so an id comparison reads every one of those as "recorded but not ticked".
- Of the **23 comparable programs, 18 disagree** — but **7 of those 23 have id coverage below 0.6**
  (`party-dungeon` 0.04, `data-test-substrate` 0.17, `summoner-convergence` 0.25,
  `combat-ai` 0.57, `creature-seed` 0.61), so their counts are weak evidence.
- The **strong** signals are the high-coverage ones: `test-verification-boundary` (0.85, 61 ticked
  but unlogged), `notification-ssot` (0.94, 46), `content-stack` (0.79, 41),
  `strain-splice-host` (0.95, 32), `item` (0.81, 10 unlogged + 35 unclosed), `npc-story-events` (0.93, 8).

**The number this report does not publish:** "266 tasks are ticked but not in their ledger, across 22
programs." A first pass produced exactly that, and it is not defensible — 4 programs cannot be
measured at all and 7 more measure poorly, so the total is an artifact of the measurement as much as
a fact about the repo. It is recorded here as a measurement to redo, not as debt.

**Consequence for the tool, deliberately:** there is **no** `--reconcile-ledgers` mode, even though
the code would be ten lines. It would print exactly the number I just proved undefensible. The
block rule's own precedent applies — a file with no declared shape is `unmeasured`, never zero — so
ledger reconciliation needs a declared per-program rule (which ids are comparable, or an id for every
`H-task` block) before it may be scored. That is the next increment's first task.

## 5. Two defects the tool's first run exposed in the rule it consumes

- **The label grammar took the first bold run as a task id.** `- [ ] **Owner shown the map**` and
  `**PAUSED**` and `**needs a ruling**` are not task ids, and they were being printed as the id
  column for **27 %** of this tree's open blocks. The grammar is now "a leading token that carries a
  digit" (`TVB5.9`, `ADG-F4`, `T19b`, `BCL-ledger-43`, `0a.1`), the same grammar the `H-id` shape
  marker already used.
- **The numeric id branch rejected `0a.1`** — a real shape in `trade-network`'s todo.

Both are in `audit-program-pipeline.py`, whose pre-existing 26 tests still pass **unchanged**: the
refactor is behaviour-preserving by that suite's own account.

**Rejected first attempt, recorded because the guard caught it:** a new `program-status-reader`
boundary claimed `gk-core/scripts/audit-program-pipeline.py`, which `pipeline-audit-scripts` already owned.
`verify-change.ps1` refused it — `ambiguous owner pattern: gk-core/scripts/audit-program-pipeline.py
(program-status-reader, pipeline-audit-scripts)`. One owner, not two: the new paths were folded into
the existing owner, which already maps to the same `tools-audit-tests` project.

## 6. The AGENTS.md gate, and three citations fixed in passing

`AGENTS.md` now carries a **"Status gate — read the status reader before reporting status (hard
rule)"** subsection: run the tool, **paste the reading used**, count blocks not checkbox lines, say
`unmeasured` rather than "0 open", route a refusal to its owner instead of reading files by hand,
never quote a figure not just reproduced, and remember a tick is a claim. It also states what the
reader cannot prove, and points at `audit-program-pipeline.py` for the *different* question (is the
idea→spec→plan→todo chain intact).

Editing `AGENTS.md` pulled that document into the scoped doc-citation gate, which was **red before
my change** — proven by running the same scoped audit on `features/mega-merge` with none of my
edits: identical 2 D1 + 1 D3. Two of the three were wrong pointers, not merely ambiguous:

- `prove-slot-connection.ps1` → the file is **`gk-fusion/scripts/prove-slot-connection.py`**. The citation was
  stale by exactly the Python port this repo mandates.
- `Program.cs:15-16` → 42 files share that basename; now `gk-core/src/FusionRpg.Server/Program.cs:15-16`.
- `status.json` → not a dead citation at all: `.claude/cmdc-agents/agents/` is **gitignored**
  (`.gitignore:169`), so a per-lane `status.json` is real and untracked by design — EXEMPT 1's stated
  case. Added to the closed list with the `.gitignore` line named, plus the test row that preserves
  "a name not on the list still reports HIGH".

The two first fixes are inside prose owned by other streams (`d5db5c2bf`, `2a7597ab1`); only the
pointers were changed, no claim was reworded. `AGENTS.md` is now 0 HIGH.

## 7. Session boundary

`paths` was widened twice, both times recorded in the session record itself: once to add
`gk-core/scripts/audit-program-pipeline.py` (the refactor, decided after measuring that a second counter was
the alternative), once to add `scripts/audit-doc-citations.py` and its guard test (the §5
exemption). `scripts/session-boundary-check.py --session program-status-tool-20260926` → **clean**
at the fork, re-checked before each commit.

## 8. Verification

| Check | Command | Result |
|---|---|---|
| New + pre-existing tool tests | `python -m pytest gk-core/tests/tools -q` | **60 passed** (34 new, 26 pre-existing unchanged) |
| The check the citation change affects | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --no-build --filter DocCitationAudit` | **6 passed** |
| Scoped verification boundary | `verify-change.ps1 -Paths <8 paths> -Session program-status-tool-20260926` | recorded on completion (§9) |
| AGENTS.md citations | `python scripts/audit-doc-citations.py --scope AGENTS.md` | **0 HIGH** (was 3 HIGH pre-change) |
| Session boundary | `scripts/session-boundary-check.py --session program-status-tool-20260926` | clean |
| The tool on the real tree | `python gk-core/scripts/program_status.py` | report produced; numbers in §2 |
| Clean-checkout acceptance | detached worktree at the reviewed SHA: `pytest gk-core/tests/tools` + `program_status.py` | **51 passed** and an identical reading (670 / 2 889) — the output does not depend on a branch or on a dirty tree |

**Two environmental failures, diagnosed rather than retried.** The first scoped-gate run failed with
`MSB3027 … locked by testhost`, and the second with `exit -1`. Both were my own fault and neither was
a code defect: I started a second gate run while the first was still in flight, then killed processes
by work-tree match, which took out the first run's test host. The fix was to stop, clear only this
worktree's orphans, and run the gate once. A gate that is re-run until it passes is not evidence.

Also worth recording: `pwsh -ExecutionPolicy Bypass` is **rejected** by PowerShell 7 — that flag
belongs to Windows PowerShell 5.1, which is what `verify-change.ps1` targets — and piping a
`Write-Host`-based script through `Select-Object` loses the INFORMATION stream, so a *passing* gate
reported nothing at all. Both are the exact traps AGENTS.md's Python ruling was written about; the
gate is now driven by a Python `subprocess.run(capture_output=True)` wrapper with a hard timeout.

No full unfiltered suite: the change is a Python tool, its tests, and two docs — one subsystem, well
inside a scoped boundary. CI/nightly/release owns the unfiltered evidence.

## 9. Scoped gate result

_(filled from the backgrounded `verify-change.ps1` run)_

## 10. Open questions for the owner

1. **`trade-network`: 162 open, 0 done.** Approved idea not yet scheduled, or a todo that was never
   started? The tool cannot answer this and I will not guess.
2. **The two unmeasured programs** (`player-guide`, `world-map-gaps-followup`) have no shape in
   `todo-shapes.v1.json`. Declare a shape and they become measurable, or record them as prose-only.
   Today they are honestly "unmeasured", which is not the same as "nothing left".
3. **`status.json` exemption** widened EXEMPT 1 by one name. Sanctioned by the tool's own comment,
   tested by the row added to `DocCitationAuditTests.cs` — flag it if the lane-state file should
   instead be tracked.

## 11. Next steps

- Merge this slice into `features/mega-merge` on the individual-check evidence in §8/§9, then fold the
  §2 reading into `tasks/reports/mega-merge-manager-resume-20260925.md` so the manager report stops
  restating hand-counted numbers.
- **Route the `verify-change.ps1` guard-step defect (§9) as its own bounded row.** It is
  verification-plane work, it is the objective's first priority, and it blocks *every* change whose
  paths map to the guard project — which is most of the repo. Prior art exists:
  `cold-process-test-build-20260912-e5b1` fixed the same race for tool tests by making the test not
  spawn a build.
- **Next increment: ledger reconciliation** (§4b) — declare comparability per program (or give every
  `H-task` block an id), then reconcile the high-coverage programs one at a time with evidence. Only
  then add a scored `--reconcile-ledgers` mode.
- Route the two todo findings to their owners: `tasks/combat-ai-todo.md:9` (stale numbers + a line
  that cites `grep -c` as its method, in a repo whose rule forbids counting checkbox lines) and
  `tasks/onboarding-rift-todo.md` (a header claiming an implementation its own open Tasks 6–7 and an
  empty tree contradict). Neither file is in this session's fence; both belong to their programs.
- The same reading answers the standing question from the last resumption: **the mega-merge
  program's own ledger rows are not where the 670 open blocks are.** They are in the
  `trade-network` / `npc-story-events` / `narrative-seed` / `combat-ai` / `onboarding-rift` tail —
  programs with no active session fencing them, and (measured in §2) `trade-network` is a
  docs-only umbrella that was never scheduled. That is a priority call for the owner, not a
  technical one.
