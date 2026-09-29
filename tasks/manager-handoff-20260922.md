# Manager handoff — `summoner-convergence` (2026-09-22, 21:20)

**Who wrote this:** the manager session `convergence-resume-20260920` (record: `tasks/sessions/convergence-resume-20260920.json`).
**For:** whoever takes over this work. Read this file first, then the four listed below it.

**Repo:** `D:/Works/source/plant-vs-zombie-rise-of-summoner` · **branch:** `features/mega-merge` · **head at handoff:** `e7509b77f`
**Working tree:** clean except `tasks/sessions/species-gear-chain-4.json`, which belongs to another session — **leave it alone.**

---

## 1. The one-paragraph situation

The `summoner-convergence` end state is: **every sub-program todo at zero open rows with evidence, then CC8**
(`test-fast.ps1 -AllDefault` green **plus** a live probe per `docs/contributing/live-probe-standard.md`).
CC8's **suite half is GREEN** (`Failed: 0, Passed: 18273` at `eb2a9a206`). CC8's **live half** is one row short:
`SSH4.9`'s four acceptance steps cannot run because no slot's save holds a socketable item and **no sanctioned
route grants one** — that is `SSH4.9-P2`, carrying an **open owner question**. Everything else is either merged,
running, or filed as a row.

## 2. Read these five, in this order

1. this file
2. `tasks/rpg-simulator-decisions.md` — the owner **cleared all 20 questions** on 2026-09-22; its `ANSWER:` lines are binding, five of them override the lanes' own recommendations
3. `tasks/summoner-convergence-report.md` §14–§16 — the last three checkpoints, each with its measurements
4. the tail of `tasks/run-board-20260920.md` (60 sections; the last ones are this era)
5. `AGENTS.md` + `docs/contributing/session-boundary.md` — the hard rules you will be held to

## 3. The owner's charter (the runner enforces it)

`C:/Users/NeneScarlet/.claude/skills/cmdc-subagent/allowed-models.json` — **pi only**, model
`opencode-go/deepseek-v4.1-flash`, effort `high` for implementation lanes and `max` for architect
investigations (owner-authorised 2026-09-22 for the simulator idea), **no fallback ever**,
`maxConcurrentLanes: 8`, `tokensPerLane: null`. A credit or quota error **stops the lane and is reported**.
The **spend gate is released for all corpus runs** (local LM Studio `google/gemma-4-26b-a4b-qat`); a *defect* or
*dependency* gate is not a spend gate. Record any new owner authorisation in that file's `approvedNote` with a
backup copy — the runner refuses to spawn without an `approvedAt`.

The goal objective itself is **immutable**: if it needs changing, the owner runs `/goal-tweak`; do not edit it.

## 4. ⚠ The one thing that will bite you first: launching a lane

The runner's child **cannot resolve `pi` or `node` by inheritance** (measured twice: `pi not found on PATH`, then
`FileNotFoundError [WinError 2]` from `CreateProcess`). Every `spawn`/`continue` must go through a `.cmd` that sets
them explicitly, run via `cmd.exe //c`:

```cmd
set "PATH=C:\nvm4w\nodejs;C:\ProgramData\nvm;%PATH%"
set "PI_ENTRY=C:\ProgramData\nvm\v25.9.0\node_modules\@earendil-works\pi-coding-agent\dist\cli.js"
cd /d D:\Works\source\plant-vs-zombie-rise-of-summoner
"C:\Users\NeneScarlet\miniconda3\python.exe" "C:\Users\NeneScarlet\.claude\skills\cmdc-subagent\scripts\cmdc_agent.py" --repo . continue --id <lane> --budget 2500 "<message>"
```

Working examples are in `D:/tmp/*.cmd` (12 of them). **Write them with the file tool, never through a shell
heredoc** — a truncated heredoc silently corrupted a launcher once.

A lane that fails **before turn 1** has **no session**: `continue` answers *"agent has no session to resume"*.
Recover with `tune --agent pi --id <lane>`, or remove the lane dir + its worktree + its branch and re-spawn.

## 5. Running right now (accept these when they land)

| lane | pid | doing | how to accept |
|---|---|---|---|
| `sim-map` | 57760 | RS5 — `docs/architecture/rpg-simulator-map.md` + `tasks/rpg-simulator-plan.md` over stable module ids | cheap checks (§6), then merge `--no-ff` naming the reviewed SHA |
| `sim-slice0` | 51248 | RS1 — the E2E scenario that proves the shape (no product code) | same; its verify is `dotnet test gk-core/tests/FusionRpg.E2E.Tests` + its own boundary check |

**Detached job, not a lane:** the **BCU2.12 corpus run** (plane d) — `[72/904]` at handoff, log
`.claude/worktrees/corpus-bcu212/tasks/reports/BCU2.12-run.log`, report artefact `BCU2.12-full-run.json` beside
it. Check it **periodically, never monitor it**; when the artefact lands, sequence `BCU2.13`. It had stalled once
at 1/904 (a 967-minute-old artefact, no process) — relaunch it the way its own header says, `Start-Process` with
log redirects, because a run started inside an agent turn dies with that turn's process tree.

**Detecting events without polling:** this session used a `wait_for` tool (`.pi/extensions/wait-for.ts`,
invoked as `pi -e .pi/extensions/wait-for.ts --tools wait_for -p "Call the wait_for tool exactly once with
{\"seconds\": 1800, \"until\": \"any\", \"pollSeconds\": 45, \"minIdleSeconds\": 900}. Then print the tool's
returned text verbatim and nothing else."`), which blocks until a lane actually changes state and costs nothing
while blocked. From a runtime without that extension, `python .claude/cmdc-agents/scripts/lane-signals.py` at a
slow cadence is the substitute. Either way: a lane that is merely quiet is **not** an event.

## 6. Acceptance is cheap — do exactly this

1. read the lane's own report: last `result` event in `.claude/cmdc-agents/agents/<lane>/events.jsonl`
2. `git log --oneline <base>..cmdc/<lane>` — the commits it claims
3. `git -C .claude/worktrees/cmdc-<lane> status --porcelain` — must be clean (a lane that hands off with an
   uncommitted ledger is incomplete; commit it or send it back)
4. does the diff match the numbers in the report? does every acceptance line get addressed or **named unmet**?
5. runner verify: `.claude/cmdc-agents/agents/<lane>/verify.json` — a `pass: false` must be **explained**, never
   waved through (one real case: the E2E project passed 231/231 while the full-suite command was interrupted —
   the lane named that gap itself)
6. merge with `--no-ff`, message naming the **reviewed SHA**
7. **then diff the branch's own changes against the merged result** — `git diff cmdc/<lane>..HEAD --stat -- <its files>`
   must be empty. A merge silently reverted a reader once; the build proved syntax, not intent.

Full harness: `.claude/cmdc-agents/scripts/accept_lane.py -Lane <lane> -ExpectSha <8-char-sha> -Check ...`
(⚠ the artefact name truncates the SHA to **8 chars**; a 9-char check reports a false PENDING).

## 7. Open work, in priority order

1. **`SSH4.9-P2` — the owner question.** A slot's save holds no socketable item (the catalog is fine: **984 of
   1178** base types declare `socketMax >= 1`) and no sanctioned route grants a real base-type instance
   (`/api/debug` is game-side only; the loot pipeline has no endpoint). **Ask the owner**: build a sanctioned
   grant route (product change, debug-scope labelled, minting nothing gameplay could not), or leave SSH4.9
   blocked pending real play? Filed in `tasks/strain-splice-host-todo.md`.
2. **CC8's live half** — the four steps (`socket → equip → read combo:…#c0 on the sheet → withdraw`) once item 1
   is answered. The path is already proven to **connect** (injector SignalR handshake) and to **serve reads**
   (`GET /api/items/armoury/1` → 200 with four real rows).
3. **CC8's suite half** — re-run `pwsh -NoProfile -File scripts/test-fast.ps1 -AllDefault` after new merges land
   (~25 min; the last run was `Failed: 0, Passed: 18273`).
4. **The simulator program** — `RS1`–`RS5` in `tasks/rpg-simulator-todo.md`; `RS3` (the clock) is **gated by the
   `decisions.md` row** and by a spec naming the seam's product shape.
5. **The TVB split** — `tvb58` is at **52 of 68** increments (its own chain; each increment is its own commit
   with the ci.yml/release.yml pair + registry rewrite in the same commit); `tvb59` landed TVB6.5's reading.
6. **Filed rows awaiting work**: `ADG-F5` (the roll offers un-grantable actions and throws), `DM-F2` (the ungated
   `/api/sim/effect/*` — owner ruled **drift, gate it**), `F14` (F13 has no committed regression test), `KS-F1`/`KS-F2`
   (boot has no Keepverse content-root awareness; nothing forbids a private repo-root walk in a test),
   `TVB-F22` (done: `AGENTS.md` no longer publishes a count that rots).
7. **Owner-gated lines** across programs — the register is `tasks/reports/backlog-reconciliation-20260921.md`
   plus each program's todo; do not close one without the owner's word.

## 8. Traps that already cost hours (each one measured)

1. **`2>&1` does not capture `Write-Host`** (information stream 6) — captures come back empty and parses fail on
   output that plainly printed. Use `*>&1`. Four call sites died on this in one script.
2. **Never pipe a detached launcher through `tail`** — the long-lived child holds the pipe, so `tail` never sees
   EOF: two commands hung 600 s and 900 s and *looked* like failures while the job was healthy. Verify a detached
   job by log growth and its process.
3. **`src/**/bin` holds 4 KB skip-stubs.** A *successful* `.39` injector build redirects its output into the
   game's `Mods/`; a ref-starved build prints `0 Error(s)` and produces no code. Check the deployed artifact.
4. **`Ambiguous project name 'FusionRpg.Injector'` is a repo property, not worktree drift** — a compatibility
   shim referencing a project whose `AssemblyName` is the same string. Build the host projects; pruning worktrees
   cannot fix it.
5. **PowerShell has no `if` expression**: `(if (...) {...} else {...})` dies at runtime with *"The term 'if' is not
   recognized"*. Precompute. Three occurrences found, each only on a code path that ran rarely.
6. **`deploy-play.ps1` launches the game itself.** Deploy with **`-NoGame`** when you intend to start the server
   first — otherwise the game starts with no server, renders at 60 fps, and issues **zero** API requests.
7. **A stale `dist/FusionRpg.Server` binary is the most convincing wrong answer a probe can give** — it produced
   eight bogus `no such column: player_id` errors. `scripts/prove-slot-connection.ps1` now fingerprints the
   binary it measures, deploys before starting the server, and reports `CONNECTION PROVEN` and
   `DATA PATH HEALTHY` as **separate** verdicts.
8. **Contention fakes reds**: 178 "failures" in 6 s were pure contention against 3 failed / 580 passed in 14 min
   on a quiet machine. Never run `dotnet test` where another test process is running; re-run before recording.
9. **Session records:** `worktree` must be an **absolute** path (a relative one makes `verify-change.ps1` exit 1
   on DRIFT in the lane's own record); `status` ∈ `active` / `merged` / `abandoned` only.
10. **A routed finding must actually land**: a reused id silently appends nothing while the commit message claims
    it did. Grep for the id after writing it.

## 9. Where the evidence lives

- board: `tasks/run-board-20260920.md` (60 sections — the operational log)
- checkpoints: `tasks/summoner-convergence-report.md` §14–§16
- the owner's cleared decisions: `tasks/rpg-simulator-decisions.md`
- the simulator idea: `docs/architecture/rpg-simulator-idea.md`, `…-shape-idea.md`
- live-path proof: `tasks/reports/live-test-proof-20260922.md`
- lane verdicts: `.claude/cmdc-agents/acceptance/<lane>-<8char>.json`
- lane reports: `.claude/cmdc-agents/agents/<lane>/{events,notes,status}.json[l]`
- the manager's own sweep tool: `python .claude/cmdc-agents/scripts/lane-signals.py`

## 10. What this handoff does NOT prove

- **`SSH4.9`'s acceptance is unrun** — no chassis was socketed, nothing equipped, no `combo:…#c0` read back.
- **The corpus run is incomplete** (`[72/904]`), and its earlier attempt stalled at 1/904.
- **`sim-map` and `sim-slice0` had just started** — their outputs are unverified at handoff.
- **The CC8 suite-green reading is a point-in-time measurement** at `eb2a9a206`; later merges invalidate it.
- **The `2>&1`/pipe/if-expression classes are fixed where found, not proven absent** elsewhere in `scripts/`.

## 11. The owner's working style (you will be corrected if you miss these)

Default to action on reversible in-scope steps; ask only for destructive, irreversible, product, or hard-boundary
work. **No life advice.** No watermarks or vendor names in docs, comments, or commits. Commit often — one logical
change per commit, **explicit paths, never `git add -A`** (parallel programs share this tree). Never publish a
number you have not reproduced. Generated data is regenerated, never hand-edited; tuning is published as `v{n+1}`.
Never widen a guard to make something pass; never add a `knownRed` entry. A structural edit validates in a step
that **gates** the commit.
