# Lane `cc8-live` — CC8's live half: one real save, the changed state read back through the normal path

**Session:** `convergence-live-20260922` · **Program:** convergence (row 9 / CC8) · **Mode:** worktree
**Fence:** `tasks/evidence-fragments/**`, `tasks/reports/**`, `tasks/summoner-convergence-todo.md`

⛔ **This lane is NOT a unit-boundary re-runner.** The objective is explicit: the QA lane *produces live
evidence* — game via `gk-fusion/tools/debug-mcp/cli.py`, web via the `playwright-cli` skill. Re-running the test suite is
the manager's post-merge gate (`scripts/post_merge_check.py`) and `test-fast.ps1 -AllDefault`; doing it here
would be the wrong instrument and would duplicate the gate.

## Why it exists, and when it starts

CC8 is the last row: *"`test-fast.ps1 -AllDefault` green, plus a live probe per
`docs/contributing/live-probe-standard.md` on a real save with the changed state read back through the normal
path."* The suite half is the manager's. This lane is the live half, and it starts **only when the manager says
the suite half is green and the anchors' rows are closed** — not before, because a live probe of a moving tree
proves nothing about the tree that ships.

## The probe, in the standard's own terms

Read `docs/contributing/live-probe-standard.md` before anything else. The rule it exists for: a response body
is never proof, and a debug tool that can fabricate the precondition can equally fabricate a false pass. So:

1. **Claim a game slot** — `gk-core/scripts/live_slot.py --status`, then `--acquire --session convergence-live-20260922`.
   Three slots machine-wide; no install path is hardcoded (`FUSIONRPG_GAME_POOL` / `FUSIONRPG_GAME_SOURCE`).
   All slots held is a **wait**, never a kill. Release before you write the fragment up.
2. **Start the server as its own process** (`Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`) — a
   server started from an agent tool call dies with that call's process tree and looks like a mid-run crash.
   Point the client at your own loopback port, never the owner's `:5088`.
3. **Deploy the injector against the slot** — `python scripts\deploy-play.py --no-server --paths <changed files>`.
4. **Name the scope of every debug call you make** (`// Game Injector Debug` vs `// RPG Server Debug`) and
   obey the boundary: a debug API may trigger a real operation, never fabricate its result.
5. **Exercise the changed state through the normal path** — the real endpoint or the real UI, on a real save.
6. **Read it back through the normal path** — the RPG server's own domain/persistence read, or the game's own
   displayed state, not the debug surface that produced it.
7. **Record the fragment** at `tasks/evidence-fragments/CC8-live.md`: the exact commands, what the game showed,
   what the normal-path read returned, and a **NOT-proved** list.

## What CC8's probe should cover

The convergence changed four surfaces end to end; probe the seam each one crosses, not the feature in
isolation: **species-gear-chain** (an item/gear tier change reaching the sheet), **strain-splice-host** (a
combination binding firing on a real plant), **empire-progression** (Zomboss's Θ and the commander pool), and
**combat-ai** (a lawn action actually firing through the Funnel). If any of the four cannot be reached on a
real save, that is a finding, not a reason to substitute a debug call for the real path.

## Hard rules

- Never kill another session's game; never probe the owner's install when a slot is available.
- A fabricated precondition (a debug-bound loadout, a hand-written row) proves nothing — the incident that
  produced this standard was exactly that shape.
- Report a red as a red. The manager would rather merge nothing than merge a false green, and the fragment is
  read by a human.
