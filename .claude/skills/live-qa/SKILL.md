---
name: live-qa
description: Run and prove a change against the real running game — deploy the injector and server, launch or restart PvZ Fusion, drive the lawn through the debug endpoints, check the web UI in a browser, and write evidence a reviewer can trust. Use for any live probe, "prove it on the lawn", an owner-run proof an agent can now run itself, a checkpoint that needs the real game, or a QA pass over a feature that unit tests cannot reach. Also use when a live run misbehaves (game exits at boot, injector never connects, server dies mid-run) — the failure table here names the real causes.
---

# Live QA — proving a change against the running game

Unit tests prove the RPG layer. This skill proves the part only the real game shows: that the wiring
reaches Unity, that the server persists what it claims, and that the player sees it.

**Only one live lane runs at a time.** One game process, one server on `:5088`, one `dist/` output.
Two agents deploying at once corrupt each other's run and produce evidence nobody can trust. If a live
lane is already running, wait or take the work as offline verification instead.

## What the machine already gives you

| Tool | Use |
|---|---|
| `gk-fusion/scripts/deploy-play.py` | guards → injector → server → game. `--no-server` / `--no-game` skip steps; `--paths <files>` runs the scoped tests once |
| `debug-mcp` tools (`debug_lawn_setup`, `debug_game_state`, `debug_screenshot`, `debug_restart_game`, `debug_act`, `debug_events`, `debug_verify`, …) | drive and observe the running game |
| `gk-fusion/tools/live_test` (`python -m live_test run <scenario>`) | scripted scenarios with their own client and reporting |
| `scripts/prove-*.ps1` | ready-made proofs: overlay combat, status, aptitude, hub combat, actor HUD, live probe |
| `live-lawn-quick-start` skill | cold-start sequence and the one-call lawn setup endpoint |
| `local-web-review` skill (`/review-web`) + Playwright | the web control room in a real browser |
| `docs/runbook/local-dev.md`, `docs/runbook/debug-pipeline.md`, `docs/runbook/live-test-ssot.md` | the full playbooks |

## The loop

1. **Know what you are proving.** Write the claim as a sentence with a number or a state in it
   ("a melee hit on Θ 70 moves the zombie's overlay HP by the funnel delta, and the sheet shows it
   after the drain"). A probe without a falsifiable claim produces a screenshot nobody can read.
2. **Build and deploy.** `python scripts\deploy-play.py --no-server` for an injector change; add `--paths`
   once to run the scoped tests. The full suite belongs immediately before the probe, not on every
   redeploy.
3. **In a worktree, the FE does not exist until you build it — and the deploy will not tell you.**
   `**/wwwroot/` is gitignored, so a fresh worktree has no `src/FusionRpg.Server/wwwroot`, and it has
   no `node_modules` either. `deploy-play.py` then prints `No src wwwroot yet — FE sync deferred`
   and **carries on**: you get a healthy API-only server, `/health` green, `injectorConnected=true`,
   and `/` returning 404. Every game-side probe passes and every web check is impossible, silently.

   So before any web claim: `npm ci` in `gk-web/web/fusion-rpg-web` inside your worktree, then redeploy (or
   `npm run build` and let the sync step mirror it). **Then read it back the same way you read back
   any other claim** — `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5088/` must print
   `200`, not 404. A deploy's own success message is not evidence that the thing it deployed exists;
   that is the same rule as everywhere else in this skill, applied to your own setup.
4. **Start the server as its own process** — `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`.
   A server started inside a tool call dies when that call's process tree is cleaned up, and it looks
   exactly like a mid-run crash.
5. **Own the game process.** Kill and relaunch it yourself (`debug_restart_game`, or stop the process
   and start `PlantsVsZombiesRH.exe` from the MelonLoader pack). Never ask the owner to close the game.
6. **Reach a known board.** `live-lawn-quick-start`: `POST /api/debug/lawn/quick-start` (scenario
   `lab-overlay`) or `Ensure-LiveLabBoard`. Confirm `injectorConnected=true` at `/health` first.
7. **Act, then read the result back through the normal path.** The response body of the call you just
   made is never the proof. Read the state through the API a player's client would use, or through the
   store.
8. **Capture evidence:** the decisive lines of output, the ids you used, and a screenshot where the
   claim is visual. Keep it short — the evidence fragment is at most 25 lines.
9. **Write the verdict,** including what would have falsified it.

## Two debug scopes — never confuse them

- **Game Injector Debug** (`debug.*` in `CheatCommandRunner.cs`, most of `DebugEndpoints.cs`): may
  fabricate engine-side state. It proves only that Unity reflects what you pushed. No domain logic, no
  persistence.
- **RPG Server Debug** (`/api/debug/reforge-world`, `/api/debug/derived-audit-actor`, the real
  `/api/aptitudes/*`): runs the real application path against a real row. Every id you pass must
  resolve to a row real gameplay could have created.

A pass in one scope is never proof of the other. The standard is
`docs/contributing/live-probe-standard.md`, and the incident behind it is in `CLAUDE.md`: a probe once
bound a fabricated loadout into the injector and read it back from the same injector's telemetry —
`ok: true` end to end for a feature that was broken.

## Failure table

| Symptom | Cause and fix |
|---|---|
| Server "crashes" mid-run | It was started inside a tool call. Use `Start-Process`. |
| `injectorConnected=false` | Game not running, or the MelonLoader mod did not load. Relaunch and wait for the host line. |
| Game exits shortly after "host ready", no log | Windows Application event 1000 (`0xc00000fd` = stack overflow). Bisect in a worktree build. |
| `lawn/quick-start` returns 404/405 | Stale `dist/`. Republish the server. |
| `/health` is green but `/` returns 404 | No FE in this tree's `wwwroot`. `**/wwwroot/` is gitignored and a worktree has no `node_modules`, so the deploy deferred the FE sync and said so in one line you scrolled past. `npm ci` in `gk-web/web/fusion-rpg-web`, redeploy, and confirm `/` is 200. |
| No living zombie ptr | Read `cheat.error` / `debug.effect.error` in the thrown message; return to the menu and re-run. |
| Repeated `force=true` enter-level crashes the game | Use one at a time and check `/health` between calls. |
| Overlay telemetry empty | It needs a debug session and real melee hits; events paging by `afterId` is broken — read the sqlite store instead. |

## Building test tooling instead of one-off scripts

When a probe would be worth repeating, add it where the repo already keeps such things: a scenario in
`gk-fusion/tools/live_test`, or a `scripts/prove-<thing>.ps1` that follows the existing ones. A new proof script
states its claim at the top, exits non-zero on failure, and prints the numbers it compared. Do not
build a second debug surface that re-implements the endpoints — adapter-wrap the existing ones, and
label every tool with its scope (`docs/architecture/debug-mcp-ideal.md`).

## When a probe finds a defect: fix it or hand it over, decided by effort

A live probe earns its cost by finding real defects. What happens next is a judgement call, and it
has a wrong answer in both directions: shipping a guessed fix, and filing a report for something you
already understood and could have fixed in ten minutes.

**"Out of scope" is not a verdict.** It is only true when one of the hand-over conditions below
actually holds. Reaching for it because fixing would be work is the lazy refusal this section exists
to stop — you are already in the file, with the cause on screen and a live loop that can re-prove
it. Nobody who picks the report up later will be that well placed.

**Fix it yourself when all of these hold:**

- You **read** the cause in the code. Not inferred from a symptom, not guessed from a stack trace.
- The fix is local: a missing route, an unwired call, a wrong constant, a predicate that names the
  wrong field, a default that was never applied.
- It sits in a file one program owns, and no other lane is mid-edit in it.
- You can re-prove it through the same live path that caught it.

Then fix it, and in the same commit keep the failing evidence next to the passing evidence. The
before/after pair is the proof; a commit that shows only green asks the reader to take your word for
what was broken.

**Hand it over — with `file:line` and the cause, never just the symptom — when any of these hold:**

- The fix needs a **new primitive**: a vocabulary entry, a grammar key, a channel, a spec decision.
  That is a design call with consequences past this defect.
- It would **move a golden**, cross a **migration or identity** edge, or need a publish to switch its
  readers in the same commit.
- It would **extend a seam that already violates SOLID**, rather than fix it.
- **Two programs both claim the file**, or the owning program has an open task for exactly this.

A hand-over is a real deliverable, not an absence of one: root cause read from the code, the exact
line, what you proved and what you could not, and what the fix would have to decide. That is worth
more to the owning program than a patch you were not equipped to choose.

**Either way, you never use your own fix as its own proof.** Re-run the probe the normal way — act,
then read the state back through the path a player's client would use. A green readback from the
call you just made proves nothing, and that is true of a fix as much as of a feature.

*Worked example (2026-09-20).* One session's QA lane hit both answers in the same run. T11's gate was
unreachable because `DebugEndpoints.cs` had no `MapPost` route for the scope commands — cause read,
two lines, one program, re-provable; it fixed it and all five criteria passed. PT7 found the patron
aura buffing the zombie side, caused by `StatApplyScope` returning `true` unconditionally for
`"match"` with no side-wide key in the grammar — a missing primitive, so it reported with the line
and let the owning program decide the spelling. Both calls were right, for the reasons above.

## Reporting

State what you ran, what it printed, and what it proves. If a claim could not be proven, say that and
name the blocker. Never describe an unrun check as passing, and never present injector telemetry as
proof of the injector. An honest "not proven" costs a sentence; a fabricated pass costs the feature.
