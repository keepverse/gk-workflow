# Spec: `world-victory`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 5 of the
[world-continuity map](../world-continuity-map.md) (wave 2; depends on `world-state-vocabulary`,
`seat-outcome`). Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md) §6.1, W1 (victory
auto-enters *developing*). Owner decision **Q1** (2026-09-19). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

When the player takes the dominant enemy empire's seat, the world's outcome becomes `won` **inside the
turn that took it**, the full step keeps running, the other enemy empires keep acting, escalation slows
through a tunable, and one durable, idempotent **world-won fact** is recorded for the story spine. The power
ladder's realms axis counts **worlds held**, not worlds won (owner Q8, round 4 — §5).

## Scope and non-goals

**In scope:** the outcome as hashed world state; the transition inside `TurnEngine.Step` (and inside
`CoarseStep`, which calls the same helper); its persistence in `rpg_worlds.outcome`; the won-fact
table; the escalation knob and where it is read; the `RulesetVersion` bump.

**Not in scope:** fall (`world-fall`, which uses the same field and the same helper); the carry limit
itself (`advance-carry` reads `won`); story content (`npc-story-events` `spine-progress` consumes the
fact); the realms axis wiring (the power program's, see §5).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The commit runs `Step`, diff, cargo pass, log and advance in one transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:519-704` |
| Remaining factions keep acting through the AI fill before the barrier | `RpgStore.WorldTurns.cs:527` |
| `Step` is pure over `(world, commands, seed, resolver, …)` and hashes its result | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-209` |
| Claims settle in `Snapshot`, after every other phase | `TurnEngine.cs:411-439` |
| The canonical header row is `TemplateId, Seed, CurrentTurn` | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:27` |
| Field-only additions emitted only when non-default keep old hashes (precedent) | trade-foundation `world-stamp` acceptance (`docs/architecture/trade-network/trade-foundation-map.md` §2.4); `TurnEngine.cs:131-140` (the `Assaults` no-bump reasoning) |

### Real gap

No transition, no durable fact, no escalation knob. The power ladder's realms axis, defined as *"one per
retired world"* (`docs/architecture/power/ssot-power-scale.md:239`), is fed the literal `0`
(`gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs:49`) — and under continuity no world retires.

## Design

### 1. Outcome is hashed world state, persisted in the Q1 column

`WorldState` gains:

```csharp
public WorldOutcome Outcome { get; init; } = WorldOutcome.Contested;   // world-state-vocabulary §1
public int? OutcomeTurn { get; init; }                                  // turn the outcome was set
public int? WonAtTurn { get; init; }                                    // sticky: survives a later fall
```

- `WorldCanonical.Write` emits one `outcome` row **only when `Outcome != Contested`** — every existing
  world is contested, so no existing hash and no existing golden moves by the field alone.
- Persistence: `rpg_worlds.outcome` (Q1's column, added by `world-state-vocabulary`) plus two nullable
  columns `outcome_turn`, `won_at_turn`, loaded into `WorldState` by `LoadWorldState` and written by the
  commit's advance `UPDATE` (`RpgStore.WorldTurns.cs:687-689`) from `result.World`. The column is the
  **persisted form of a hashed field**, like every sector field the graph writer persists — not a second
  home. Nothing else writes it.
- `world-state-vocabulary` §7's "header columns are outside the hash" stays true for `state`; for
  `outcome` it is superseded by this section (the spec there says so).

Why inside `Step` and not after it: replay rebuilds a world from its command log by calling `Step`
(`RpgStore.WorldTurns.cs:769-775`). An outcome written after `Step`, from the Data layer, would be a
side-channel write replay never reproduces — the exact defect `warden-mortality-ideal.md` §The shape
rules out. Inside `Step` it is a pure function of the state, so replay reproduces it.

### 2. The transition — last in `Snapshot`, one shared helper

```csharp
// src/FusionRpg.Core/World/Continuity/OutcomeTransition.cs — pure
public static WorldState Apply(WorldState world, string dominantSeatId, int turn, TurnReport report, string phase)
{
    if (world.Outcome == WorldOutcome.Fallen) return world;                 // terminal (world-fall)
    switch (SeatOutcome.Read(world, dominantSeatId))
    {
        case SeatReading.SeatLost:   /* world-fall §2 */ ...
        case SeatReading.SeatTaken when world.Outcome == WorldOutcome.Contested:
            report.Add(phase, TurnReportKinds.Event, "world", "world.won", dominantSeatId);
            return world with { Outcome = WorldOutcome.Won, OutcomeTurn = turn, WonAtTurn = turn };
        default: return world;                                               // won is sticky
    }
}
```

Called once at the end of `Snapshot` (after `WardenResolver`, `TurnEngine.cs:439`), so every claim of
the turn has settled. The dominant seat id comes from `WorldTemplateCatalog.DominantSeatOf` (via the
stamp's template id), never from the store. `CoarseStep` calls the same helper at the end of each
coarse record (`coarse-step` §4).

- `won` never returns to `contested`: losing the enemy seat back does not un-win (W1: the world
  *develops*). `won → fallen` is legal (`world-fall`); `WonAtTurn` keeps the fact that it was won.

### 3. The durable world-won fact

`rpg_world_won_facts(save_id INTEGER NOT NULL, world_id TEXT NOT NULL, won_at_turn INTEGER NOT NULL,
committed_utc TEXT NOT NULL, PRIMARY KEY (save_id, world_id))` — save-scoped new table, one `save_id`
column (`docs/architecture/solid-enforcement/spec-save-identity.md:594-603`). Inserted with
`INSERT OR IGNORE` in the commit transaction when `result.World.WonAtTurn` is set and was not set in the
pre-step world. **Exactly one row per world, ever**; a replay or re-commit inserts nothing (the P14
dedupe shape, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-168`). It is written, never updated,
and survives the world falling.

Consumers: `npc-story-events` `spine-progress` (one time-machine piece per world won,
`docs/architecture/npc-story-events-map.md` module row `spine-progress`), `advance-carry` (the won
carry limit reads `outcome = won` of the world being left), and §5.

### 4. Escalation slows after victory — a tunable read inside the step

`escalationAfterVictoryMilli` (per-mille, a bounded ratio): the AI command policy and the `Events`
phase read `world.Outcome == Won` from `WorldState` — which they already receive — and scale their
escalation terms by the knob. Because the input is hashed state, no hidden input enters `Step`. Which
terms it scales is the AI policy's (`FrontierRulesPolicy`); this module adds the one tunable and the
read site, and asserts monotonicity, not a balance number.

### 5. The realms axis — worlds held (owner Q8, round 4, 2026-09-19)

`ssot-power-scale.md:239` defines `realmsAdvanced` as one per retired world. Under continuity no world
retires. This spec first recommended counting worlds **won**; the owner decided (Q8,
[decisions-round-4.md](../trade-network/decisions-round-4.md)): **the realms axis counts worlds held (not
fallen).** So:

- **Held** = a map world of the save whose `outcome` is not `fallen` (`contested` or `won`), in any attention
  state. It is a read over `rpg_worlds` (`world-state-vocabulary`'s two columns), exposed as
  `CountWorldsHeld(save)`; the won-fact table stays for `spine-progress` and `advance-carry`.
- **It can go down.** A fall lowers it, which is the point of Q8: a world you lost stops counting. Because
  `Wf = Wa` puts the same axis on both sides of every contest (`ssot-power-scale.md:299`), a change moves
  magnitudes (`P(Θ)`), not contest odds.
- **The consequence to state, not hide.** Advancing is free at any time (W2), and a newly created world is
  held from creation (`contested`), so each advance raises the count by one while the world stands. What
  stops it being a free faucet is that every held world keeps full-rate upkeep and enemy pressure and can
  fall (`coarse-step` §2, §5; `world-fall`). ~~Whether a world counts from creation or only once it has been
  held against pressure is a genuine owner question (map round-4 reconciliation, WC-R4-1); this spec builds
  the literal reading.~~ **Decided, round 5 D1 (owner, 2026-09-20): a new world counts as held from
  creation.** `CountWorldsHeld` counts every map world whose `outcome` is not `fallen` from the turn it is
  created; no first-coarse-record or N-turn threshold exists.
- Wiring it (replacing `RealmsAdvanced: 0` at `gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs:49`)
  is the power program's change to its own SSOT line (`ssot-power-scale.md:239`'s definition changes with
  it); this module exposes the count and files the ask.

### 6. `RulesetVersion` — the wave's one bump (round 6 C1)

`Step` gains a behaviour (the transition, and the escalation read). A command log that takes the
dominant seat now produces a different hash, so a bump is needed — and **round 6 C1 fixes which one:**
*"one capability flag and one ruleset bump per wave"*, so this module does **not** take a bump of its own.
This module is world-continuity **wave 2**; it rides **wave 2's single `TurnEngine.RulesetVersion` bump**
(13 today since `d6931e43a`, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`), taken at landing and never
pre-assigned (map *Audit 2026-09-20* R1), recorded in
[../trade-network/landing-order.md](../trade-network/landing-order.md). `world-fall` and `coarse-step` are the
other wave-2 modules and share the same bump — which is exactly the precedent this section already cited
(`TurnEngine.cs:118-124`, the `cede`/`bind-warden`/`dowse` wave), now the family's rule rather than an "if".
This module still **re-blesses the world goldens** in its own change, because it is the one that moves them:
a bump is not a re-bless.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | commit transaction; Snapshot ordering; AI fill | reused |
| Wiring gap | `RealmsAdvanced: 0` | §5 — worlds held (Q8), filed to the power program |
| Real gap | outcome state, transition, fact, escalation knob | §1–§4 |

## Acceptance (contract)

1. Taking the declared seat sets `Outcome = Won`, `OutcomeTurn = WonAtTurn = turn` in the same `Step`,
   with one `world.won` report entry.
2. `won` never becomes `contested` (losing the seat back leaves `won`).
3. Exactly one won-fact row per world; replaying or re-committing the turn inserts nothing.
4. A world that never takes the seat hashes byte-identically before and after this module (the outcome
   row is emitted only when not contested); a log that takes the seat changes hash, which is what wave 2's
   `RulesetVersion` bump covers (round 6 C1, §6).
5. Replay of a won world reproduces `Outcome`, `WonAtTurn` and every stored hash.
6. The escalation knob is monotone: with the knob at 1000‰ the AI's orders equal today's for the same
   believed view; lowering it never raises an escalation term.
7. The `rpg_worlds.outcome` column always equals `WorldState.Outcome` after a commit (a store test reads
   both).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/OutcomeTransitionTests.cs` (new): acceptance 1, 2, 4
  (hash of a never-won world before/after).
- `tests/FusionRpg.Core.Tests/World/Turn/TurnEngineTests.cs` (extend): a scripted `two-hearths` log that
  claims `z-home`.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs` (extend): acceptance 3, 5, 7.
- AI policy test for acceptance 6 beside the existing `FrontierRulesPolicy` tests.
- World golden re-bless in the same change.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-dal.py
```

Crosses Core and Data and moves goldens: the full suite once at module end.

## Hard edges

- **`rpg_worlds` schema:** two nullable columns (`outcome_turn`, `won_at_turn`) beside Q1's `outcome`.
- **Replay:** the outcome is produced by `Step`, so replay reproduces it; `RulesetVersion` bump refuses
  replay of pre-bump logs across the change, as `RpgStore.WorldTurns.cs:759-760` already does.
- **Goldens:** re-blessed with the bump; a never-won world's hash is unchanged.
- **Corpse-cache tick key:** none.

## Dependencies

`world-state-vocabulary`, `seat-outcome`. Consumed by `world-fall` (shares the helper and bump),
`coarse-step`, `advance-carry`, `world-event-budget`, `away-digest`, external `spine-progress`.

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `escalationAfterVictoryMilli` | per-mille multiplier on AI escalation terms (bounded ratio) | 500 | `data/tuning/world-continuity.v1.json` |

## Boundaries

- **Always:** the transition inside `Step`; one fact per world; one bump per wave.
- **Ask first:** letting a won world return to `contested`.
- **Never:** an outcome written from the Data layer outside the step; a second win predicate; wiring
  `realmsAdvanced` from this module.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldState.Outcome` / `OutcomeTurn` / `WonAtTurn`; `OutcomeTransition.Apply` | `world-fall`, `coarse-step` |
| `rpg_world_won_facts` + `CountWorldsWon(save)` | `spine-progress`, `advance-carry` |
| `CountWorldsHeld(save)` (outcome ≠ `fallen`) | the power program's `realmsAdvanced` (Q8) |
| `escalationAfterVictoryMilli` read site | AI policy, `world-event-budget` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn engine (Snapshot), world canonical hash, world store commit, AI policy, power ladder.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md; plus ssot-power-scale.md §5 axis table.
[x] decisions.md checked: phase order row (no phase added; the helper runs inside Snapshot).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: canonical header row, Snapshot order, RealmsAdvanced literal 0.
[x] Surrounding sections read (RulesetVersion history comments).
[ ] Constraint tested: "never-won worlds hash identically" is acceptance 4, to be run, not measured.
[x] No §2 invariant contradicted.
[x] Corrections propagated: world-state-vocabulary §7 updated for the hashed outcome.
[x] No population pinned.
[x] No cache.
[x] No ordering-fixed criterion (the helper runs after every claim; lost-and-taken is specified).
[x] Actor magnitude: none produced; the realms axis is filed to its owner.
[x] No SOLID fork: one helper for full and coarse step.
[ ] Registry row: "outcome written only by the step" — added when built.
[x] Round 5 (2026-09-20): D1 decided — held from creation; WC-R4-1 closed; no formula change.
```
