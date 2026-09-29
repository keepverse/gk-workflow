# Handoff — implementation orchestrator for `summoner-convergence`

**Written 2026-09-18, at the end of the planning phase.** Paste the prompt below into a fresh session. The
planning orchestrator stops here; the owner comes back afterwards to review the implementation results.

---

## The prompt

You are the **implementation orchestrator** for `summoner-convergence` in
`D:\Works\source\plant-vs-zombie-rise-of-summoner` (branch `features/mega-merge`). Idea, spec and plan phases
are finished and committed. Your job is to **build**, end to end, and leave a report the owner can review.

### 1. Read first, in this order

1. `AGENTS.md` and `CLAUDE.md` (hard rules — binding), `docs/DESIGN-GATE.md` §2 and §5.
2. `tasks/summoner-convergence-plan.md` — the parent: programs and plan pairs (§1), four suggested lanes (§2),
   couplings (§3), **hard edges H1–H7 (§4)**, the shared tuning ledger (§5), checkpoints CC1–CC8 (§6),
   working rules (§7). Then `tasks/summoner-convergence-todo.md`.
3. `docs/architecture/spec-rulings-2026-09-18.md` — **R1–R28, binding, never reopened.**
4. For each program you run: its `tasks/<program>-plan.md` and `-todo.md`, then its map and module specs
   under `docs/architecture/`. The specs are the source of truth for behaviour; the todo is the task list.

### 2. Your authority (owner ruling R28)

- **Full autonomy, no human gate. Agents are the gates.** Every step a plan marks *owner-run*, *owner review*,
  *owner-approved* or *ask first* is run by you and passes an **independent agent review** (a reviewer
  that did not write the change) instead of waiting for the owner.
- **You design your own orchestration workflow**: how many sub-agents, which lanes run in parallel, when to
  review. The plans' lanes and orders are **suggestions**. Only these bind: the rulings, the hard edges
  H1–H7, and the repo's hard rules.
- **Not in your authority:** a full model-calling corpus run beyond what a plan task names (for example an
  action-corpus full batch) — that stays the owner's separate decision. `git push`, PRs, and force anything.

### 3. Hard rules you must keep (restated so a sub-agent brief can copy them)

- **Commits:** only through the MCP tool `repo-git.commit`, with explicit `paths`, never `all`; one logical
  change per commit; no push; no attribution trailers or assistant names.
- **Sessions:** one session per problem — `tasks/sessions/<id>.json` with `paths`, status `active` →
  `merged` (valid: `active` / `merged` / `abandoned`). Run `python scripts/session-boundary-check.py`. **Never
  edit a path another active session claims** — at handoff time `creature-seed-rederive-20260918` and
  `solid-remediation-20260917` are active; re-read `tasks/sessions/*.json` before each lane starts. Never
  `git stash`/`checkout`/`reset` around another session's work.
- **Verify each task once** with `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`.
  The full suite (`.\scripts\test-fast.ps1 -AllDefault`) only at a program's final checkpoint, a change that
  crosses programs, CC8, or immediately before a live probe.
- **Tunables** live in `gk-core/data/tuning/` and are published through `gk-core/tools/tuning/publish.py` as `v{n+1}`, never
  edited in place; shared files follow the parent §5 ledger order; a publish and every host reader that loads
  it land in the same commit (H7). From `SSH6.8` on, any publish of `sockets`, `strain-splice` or
  `materials` re-runs `combo-budget --report` in the same commit.
- **Generated data is never hand-edited** (`gk-data/packs/fusion/data/seed/items/**`, `gk-data/packs/fusion/data/seed/actions/**`, `gk-data/packs/fusion/data/generated/**`,
  …): change the generator and regenerate.
- **Golden moves (H1):** one cause per commit; a re-bless may share the commit with the one code change that
  causes it (preferred — never leave the shared branch red), never with a second cause. Order:
  `ST2.3` → `ST1.3` → `AE1.5` → `SP1.2` (defect correction) → `SP6.1` → `EP4.18`; `EP1.14`, `EP2.7`,
  `EP2.13`+`EP2.14` are independent single-cause moves. Register each in `CV.2`.
- **Save identity (H2, R27):** built directly on the branch; `SE4.15`–`SE4.19` and `SE4.21`–`SE4.29` first,
  **`SE4.20` (turns the migration on) lands last**, then `SE4.30` rehearses on a real save copy (timestamped
  backup, idempotent second boot, rollback drill). No task writes a re-keyed row before `SE4.20`.
- **Invariants:** one ActorHub compose (no second composer or private fold), battle engine is the SSOT for
  every mode, one power ladder (Θ contests, P(Θ) magnitudes, no new `f(level)`), `long` magnitudes with
  `checked` arithmetic, SQL only in `FusionRpg.Data`, SOLID. Tests assert contracts and closed vocabularies,
  never population counts or generated text.
- **Live probes** follow `docs/contributing/live-probe-standard.md`: real endpoints on real rows, read back
  through the normal path; a debug-fabricated result is never evidence. Start the server with
  `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe` (a server started inside a tool call dies with
  it) and deploy the injector with `.\scripts\deploy-play.ps1 -NoServer`; you may kill and relaunch the game
  yourself.
- **Machine load:** many sessions run here at once. A full-suite crash or hang may be contention — check
  `Get-Process dotnet` before blaming a change; re-run a failure in isolation before trusting it.

### 4. Where to start (suggested)

Four lanes can run in parallel, each opening with a live defect:

| Lane | First tasks | Then |
|---|---|---|
| A — actions | `ST2.1` → `ST2.2` (costs scaled twice) | ST1, ST3→ST4→ST5; `AE1.x`, `AE2.x`; action `T62`/`T63`, `T67`, `T74` for visibility |
| B — identity & progression | `SE4.1`–`SE4.4` (commander-identity) → `SE4.11`–`SE4.14` (save-identity first slice) → `SP0.1`–`SP0.4` (fusion picks refused) | the migration unit (R27 order), `SP`, `EP`, then `BP` |
| C — items | `T39` (free enhancement protection) | species-gear-chain remaining tasks → `SSH` 1→2→5→6→7/8 |
| D — infrastructure | `TVB0.1` (release gate masks failures) | `SE0.1`–`SE0.8` and SE waves 1–3; TVB lanes; `NS` waves 1–4 |

Checkpoints CC1–CC8 (parent §6) are review points: at each, run an independent agent review of the evidence
and record the result in `tasks/summoner-convergence-todo.md`.

### 5. What to leave for the owner (the report)

Maintain **`tasks/summoner-convergence-report.md`** as you go, and finish it when you stop:

1. **Status per program:** tasks done / open / blocked, with commit hashes.
2. **Checkpoints reached** (CC1–CC8) with the evidence and the reviewing agent's verdict.
3. **Golden re-bless register** (mirrors `CV.2`): cause, commit, what moved and why.
4. **Every step you ran in place of the owner** (R28): what it was, what the reviewer agent checked, outcome.
5. **Deviations from a plan or spec**, each with the reason — including any spec you found wrong against code
   (fix the spec in the same change; never leave a known-stale claim).
6. **Live-probe evidence**, per the standard.
7. **Open items**: anything genuinely needing an owner decision (new business questions only — no
   manufactured ones), each with the default you shipped behind.

Stop when every lane is complete or genuinely blocked on something only the owner can decide; the report is
the hand-back.
