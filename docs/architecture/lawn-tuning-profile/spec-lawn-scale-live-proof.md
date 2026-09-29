# Spec: `lawn-scale-live-proof` (lawn-tuning-profile module 9)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) ·
**Depends on:** every module in the program ·
**Closes:** `lawn-combat-wire` **proof 5 / L-N2**
**Status:** spec, 2026-09-16. Not built.

## Objective

Run the lawn on a real board with the profile's own numbers, and close the one proof
`lawn-combat-wire` could never run.

**Proof 5, in its own words:** *an exhausted actor's own Hub-composed `attackDamage`/`maxHp` stay
intact* — exhaustion gates the RPG trigger; it never degrades the actor's stats.

It has never been observed, and the reason is not instrumentation. It is arithmetic: with **any**
aptitude allocation the stamina pool never empties (`ExhaustionEvents` 0 at three points, 591 at zero),
so there is no exhausted-and-allocated actor in existence to observe. `lawn-resource-scale` and
`basic-attack-cost-scale` create one; this module reads it.

## What is measured

| # | Reading | Instrument |
|---|---|---|
| 1 | A zero-allocation actor exhausts and recovers on the **same ptr**, never a respawn | `LawnCombatObserver` per-actor transition rows (`lawn-playable`'s `exhaustion-event`), or per-ptr hit rows if that module has not landed |
| 2 | A **fully-invested** actor also exhausts, in a longer rhythm | same, second arm |
| 3 | **Proof 5:** while exhausted, that actor's `attackDamage`/`maxHp` equal the Hub snapshot for the same actor, unchanged from before exhaustion | `GET /api/actors/{id}/sheet` vs `debug.board-stats`, per window |
| 4 | Every refused swing still fires its **vanilla** shot | observer: vanilla hits continue while RPG records stop |
| 5 | A Peashooter's live `attack` is a stated multiple of its vanilla 20, not four digits | `debug.board-stats` |
| 6 | The zombie side reads Zomboss's build at `Θ_player + offset`, never the player's commander build | `debug.aptitude-trace` `bonusAtkContribs` |

⚠️ **Reading 1's instrument is unreliable until `lawn-playable`'s `exhaustion-event` lands.** Today's
counter is incremented per refused swing rather than per transition — the clean-player run reported
`ExhaustionEvents` 591 against `totalHits` 551, and more events than hits can only mean refusals are
being counted. Until that module ships, reading 1 must be taken from the per-ptr hit rows by hand, as
proof 4 did, and the run file must say so.

Readings 1 and 4 already exist from the clean-player run
(`_lawn-combat-proof4-exhaustion-clean-player.json`). They are **re-run** against the new scale, never
assumed to have survived it.

## Commands

```powershell
Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe
python scripts\deploy-play.py --no-server
# then, per arm, on a fresh board:
dotnet run --project gk-fusion/tools/LawnCombatObserver -- --seconds 300 --out docs/research/perf/_lawn-scale-proof5-<arm>.json
```

Two arms, fresh board each, committed as two files: `zero-allocation` and `full-investment`.

## Project structure

| What | Where |
|---|---|
| Prediction (written first) | `docs/research/perf/_lawn-scale-proof5-prediction.json` |
| Run files | `docs/research/perf/_lawn-scale-proof5-{zero,full}.json` |
| Verdict | `tasks/lawn-tuning-profile-todo.md`, and the proof-5 box in `tasks/lawn-combat-wire-todo.md` |

## Boundaries — this is a live probe, so the probe standard governs

- **Always:** a real board, a real player, real gameplay-produced records; every number quoted from a
  committed run file.
- **Always:** write the arithmetic prediction **before** the run and commit it, the way proof 2 did
  (predicted 1.51656, observed 1.51711). A prediction written after the reading is not a prediction.
- **Never:** fund, fabricate, or debug-mint any part of it.
  `docs/contributing/live-probe-standard.md` is binding: a `debug.*` command may set the board up, but
  it may never be the source of a reading that proves an RPG-layer claim. The 2026-09-13 incident — a
  fabricated loadout read back from the same injector's own telemetry — is why this program exists in
  the shape it does.
- **Never:** reword a bullet to tick it. Proof 5's wording is the acceptance; if the observation does
  not match it, the box stays open with the number that refuted it.

## Testing strategy

Offline tests cannot close this — that is the point of the module. What they must still do:

- ✅ The observer's per-ptr exhaustion record shape stays unit-tested (it already is).
- ✅ The prediction is computed from the shipped tunables by code, not by hand, so the two cannot drift.

## Success criteria

1. Both arms committed, both exhausting, per-ptr rows showing recovery on the same pointer.
2. Reading 3 observed: `attackDamage`/`maxHp` unchanged across the exhausted window and equal to Hub.
3. Reading 5 observed: the pea is a pea.
4. `lawn-combat-wire`'s proof-5 box ticked against its own wording, citing both files — or left open
   with the number that refuted it.
5. The program's "the lawn is tuned as its own mode" row closes on these files, never on a summary.

## Open questions

None.
