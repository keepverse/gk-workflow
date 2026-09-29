# Task: live QA lane — prove merged work against the REAL running game

You are the ONLY live lane. One game process, one server, one `dist/`. Six other lanes are running
offline work at the same time; none of them touch the game. Never assume that is still true —
if `/health` or the game behaves as if someone else is deploying, stop and report it.

**Read `.claude/skills/live-qa/SKILL.md` in full before your first action.** It is the standard for
this work. Also read `docs/contributing/live-probe-standard.md`. Everything below assumes you have.

## You have no MCP. Use the CLI instead.

Every debug tool is reachable as:

```
python gk-fusion/tools/debug-mcp/cli.py <tool> --json '{...}'
```

`python gk-fusion/tools/debug-mcp/cli.py --list` names all 21. stdout is always a JSON envelope. The tools you
will use most: `debug_preflight`, `debug_lawn_setup`, `debug_game_state`, `debug_act`,
`debug_events`, `debug_actor`, `debug_verify`, `debug_screenshot`, `debug_menu_home`,
`debug_restart_game`.

## The two rules that decide whether your evidence is worth anything

**1. The response body of the call you just made is NEVER the proof.** Act, then read the state back
through the path a player's client would use — the REST API or the store. A probe once bound a
fabricated loadout into the injector and read it back from that same injector's telemetry: `ok: true`
end to end, for a feature that was actually broken. The owner caught it by looking at the screen.

**2. Two debug scopes, and you must name which one you are in.**
- *Game Injector Debug* (`debug.*` in `CheatCommandRunner.cs`, most of `DebugEndpoints.cs`) can
  fabricate engine-side state. It proves only that Unity reflects what you pushed. No domain logic,
  no persistence.
- *RPG Server Debug* (`/api/debug/derived-audit-actor`, the real `/api/aptitudes/*`) runs the real
  application and persistence path against a real row. Every id you pass must resolve to a row real
  gameplay could have created — never one the debug call invented.

A pass in one scope is never proof of the other. State the scope in every evidence fragment.

## Setup, in this order

1. `python gk-fusion/tools/debug-mcp/cli.py debug_preflight --json '{}'` — read-only readiness audit.
2. Deploy: `pwsh -NoProfile -File gk-fusion/scripts/deploy-play.py -NoServer`. The default MelonLoader game
   dir is already the script's own default — pass no game-dir flag.
3. **Start the server as its own detached process**:
   `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`.
   A server started inside a tool call dies when that call's process tree is cleaned up, and it looks
   exactly like a mid-run crash. This has bitten this repo twice.
4. Own the game yourself — `debug_restart_game` kills and relaunches only THIS install's game. Never
   kill by bare process or image name: that takes down every other session's clone too. Never ask the
   owner to close the game.
5. Confirm `injectorConnected=true` at `/health` before probing.
6. Reach a known board: `debug_lawn_setup` (scenario `lab-overlay`), per the
   `live-lawn-quick-start` skill.

## Your queue, in this order

**1. CC5 — empire progression live.** `tasks/summoner-convergence-plan.md:150`. Prove: empire level,
earned free respecs, the priced unique respec, and creature commanders. The EP lane's CP1–CP6 work is
merged. Respec pricing is a real persistence path — use RPG Server Debug scope and a real save.

**2. CC6 — items converge.** Plan line 151. Prove: species materials 2/8/0, combinations bind and
are priced, helm hosts words. SSH2.1–2.6 are merged, including the socket-words retirement that
replaced 25 legacy entries with 95 combination entries. Check the combo-budget report is green.

**3. CC7 — infrastructure.** Plan line 152. Notifications waves 1–4 and sharding are the live-visible
parts; the Core split and python lane are offline concerns you can verify by reading the reports.

**4. BCU8.1 live regression** — the `nerve.*` VFX apply cue drift (D17) just merged. Confirm the cue
fires at the right moment on the real lawn. This is a visual claim, so capture a screenshot.

**5. PT7 re-probe — BLOCKED until told otherwise. Do not start it.** A separate lane is adding a
side-wide owner key to `StatApplyScope` so the patron aura stops buffing zombies. When I tell you it
has merged, re-run PT7 criterion 2: read `combat.power.fire` back on BOTH sides and confirm the
zombie side no longer shows the aura. The plant-side magnitude was already correct at 47 — reading
only that side is what let this defect survive.

Work the queue in order. If an item is genuinely unreachable, say so with the reason and move to the
next — do not stall the whole queue on one blocker.

## Evidence

One fragment per item under `tasks/evidence-fragments/`, at most 25 lines each: the claim, the ids
you used, the decisive output lines, the scope, the verdict, and what would have falsified it.

Never describe an unrun check as passing. An honest "not proven, blocked by X" costs a sentence; a
fabricated pass costs the feature. If a criterion needs something you cannot reach (a real currency
balance, a save state you must not invent), say that plainly rather than routing around it through a
SIM-only shortcut.

## When a probe finds a defect

Report it with `file:line` and hand it to the owning program. Do NOT patch a defect outside your own
lane's scope — a QA lane that fixes what it finds stops being an independent check.

## Verification

- `python gk-fusion/tools/debug-mcp/cli.py debug_preflight --json '{}'`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

Run everything in the FOREGROUND. Never end a turn waiting on your own background job.
On `user-mapped section open`, run `dotnet build-server shutdown` and retry — another lane's MSBuild
holds the handle.
