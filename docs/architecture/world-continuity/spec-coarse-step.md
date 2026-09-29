# Spec: `coarse-step`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 6 of the
[world-continuity map](../world-continuity-map.md) (wave 2; depends on `hibernation-clock`,
`seat-outcome`, external trade-network `trade-foundation` · `world-stamp` and · `stock-deltas`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §3.1–§3.4, §6.3. Map assumption 4 (every
cross-world effect is a system-issued `WorldCommand`; a coarse catch-up is a logged record replay
reproduces). House style: [../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).
**Round 4 (2026-09-19):** system-issued commands arrive through `trade-foundation`'s shared system-command
path (owner Q10); the warden input is the logged power roll-up (owner P, `world-warden` §5); and the inputs
carry cross-world route flows (`rift-trade` ask A1, answered in §1).

## Objective

`CoarseStep(summary, seed, n, stamp, inputs)` advances a hibernating (or idle) world `n` turns in closed
form — per sector and per faction, never per unit — composed from the **same** rule functions
`TurnEngine.Step` calls. It runs when the player selects or looks at the world, or on a small background
budget after End Turn; it writes the graph once; and it appends one **coarse record** to the world's turn
log, so replay reproduces it byte for byte.

Success looks like: a world left for 20 End Turns catches up in one call whose cost does not depend on
20; the result hashes identically on every replay; production is strictly below what 20 full steps would
have produced; frontier losses happen as seeded, logged events that the digest lists in order.

## Scope and non-goals

**In scope:** the Core `CoarseStep`; its logged input record; the coarse record kind in the turn log;
the replay interleave; the three triggers (select, explicit catch-up, background budget); resolving the
system-issued commands filed into a non-active world; the outcome check at the end of a record.

**Not in scope:** the background multiplier's curve (`background-yield`; this module reads one per-mille
input); the event pulls (`world-event-budget`; this module reserves the slot and passes the budget);
the warden's defence term (`world-warden`; logged input slot); idle's wall clock (`idle-world`, which
calls this with its own `n`); the digest's rendering (`away-digest`, which reads the record).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `Step` is pure over `(world, commands, seed, resolver, powerTuning, …)` and hashes its result | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-209` |
| The phases it calls: Production (loam + siege construction), Growth, Pressure (sustain, supply, loam pressure, legion supply), Events (calendar) | `TurnEngine.cs:196-199`, `:302-313`, `:316-322`, `:337-349`, `:353-377` |
| Fade is a per-turn linear step, clamped: recovery `+RecoveryMilli`, decay `DecayFor(deficit)` | `gk-core/src/FusionRpg.Core/World/Loam/FadePolicy.cs:18-21` |
| Calendar boundaries are arithmetic over the turn number | `gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:22`, `:44-71` |
| Pure lazy idle resolver precedent: `Resolve(tierId, squad, seed, elapsedTicks)` | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61-67` |
| Θ-difference contest primitive | `gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8-9`; the same contest read `npc-story-events` `choice-resolution` uses (`docs/architecture/npc-story-events-map.md:218`) |
| Actor Θ and content Θ from one provider | `gk-core/src/FusionRpg.Core/Power/IPowerIndexProvider.cs:11-16` |
| Hub inputs reach a pure Core resolver as a delegate injected by Data, never a store read in Core | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:551-598` |
| The commit writes a diff, then one log row `(world_id, turn)` with hash, versions and report | `RpgStore.WorldTurns.cs:607`, `:663-681`; DDL `:41-51` |

### Wiring gap

| Gap | Evidence |
|---|---|
| Replay rebuilds from the template and calls `Step` once per turn | `RpgStore.WorldTurns.cs:769-775` |
| Replay refuses on any engine or ruleset mismatch | `RpgStore.WorldTurns.cs:759-760` |

A world advanced by a coarse catch-up is unreplayable as written: the loop at `:771` would call `Step`
for turns that no full step produced.

### Real gap

No coarse step; no coarse record kind; no replay branch for it; no trigger.

## Design

### 1. Signature and purity

```csharp
// src/FusionRpg.Core/World/Continuity/CoarseStep.cs
public const int CoarseVersion = 1;      // replay refuses a record whose version differs

public static CoarseResult Run(WorldState world, ulong seed, int n, WorldStamp stamp,
                               CoarseInputs inputs, ICoarseTrace? trace = null);

public sealed record CoarseInputs(
    IReadOnlyList<WorldCommand> SystemCommands,          // filed into this world while not active (§3)
    IReadOnlyList<FrontierTheta> Frontiers,              // Θ_content − Θ_actor per frontier sector (§5)
    long WardenPower,                                     // world-warden: logged legion-power roll-up of the warden legions; 0 = none
    int DefenceTheta,                                     // world-warden: ContestTheta(WardenPower) x weight; 0 until the power §10 row lands
    IReadOnlyList<RouteFlow> RouteFlows,                  // rift-trade sleeping-endpoint: exports and due imports (A1)
    int YieldMilli,                                       // background-yield; < 1000, validated
    int EventBudgetMilli,                                 // world-event-budget
    CoarseMode Mode);                                     // Hibernating | Idle (event budget row)

public sealed record CoarseResult(WorldState World, TurnReport Digest, string StateHash, CoarseRecord Record);
```

`n` is `min(pending, catchUpCapTurns)` for a hibernating world (`hibernation-clock`) or the credited idle
periods (`idle-world`). **No store, no clock, no ambient RNG**: every random draw is
`SeededRng.DeriveStream(seed, label)` with a label that names the absolute turn range (§6). The file lives
under the world determinism guard's scan root (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:253-266`).
**Route flows (answers `rift-trade-map.md` ask A1).** `RouteFlows` carries, per cross-world route with an end in
this world, the exports due out of and the imports due into the anchor sector over the span, as
`rift-trade` `sleeping-endpoint` computes them. `CoarseStep` applies them in closed form inside step 3 (§2),
as one more per-sector, per-good rate on the anchor's warehouse: an export drain is bounded by
`throughput × n` **and** by the anchor warehouse's stock at the start of each segment of the closed form, so a
drain never takes more than is there; imports land as located stock and never bank (the `background-yield`
rule). The formula for how much a route moves is `rift-trade`'s; this module only applies the logged amounts.
An empty list changes nothing.

`inputs` are computed Data-side and **logged verbatim** in the coarse record, so replay never recomputes
a Hub or Θ read (the map principle: warden strength enters as a logged input, never a live read).

### 2. What a coarse step computes — composed, not re-implemented

Order inside one record (fixed):

1. **System commands** (§3) through the Snapshot resolvers that own their kinds.
2. **Rates, measured once.** Run the economic phases `Step` runs — Production, Growth, Pressure's upkeep
   and legion supply — **once** on the current state, and read their per-sector, per-stock deltas from
   `TurnResult`'s stock-delta record (trade-foundation `stock-deltas`). That record is the rate.
   `CoarseStep` never re-derives a yield, an upkeep or a burn formula; if a phase changes, the coarse
   rate changes with it. Production-side deltas are scaled by `YieldMilli / 1000` (divide last, `long`,
   `checked`); upkeep-side deltas are **not** scaled — leaving never makes holding cheaper (ideal §3.3,
   §6.6.3).
3. **Stocks and fade in closed form.** Per anchor component: with net rate `r` and stock `s`, turns until
   empty `k0 = r < 0 ? s / −r : ∞`. For `n ≤ k0` the stock moves `n·r` and stability recovers
   `FadePolicy.ApplyN(stability, +, n)`; past `k0` the stock sits at 0 and stability decays
   `FadePolicy.ApplyN(stability, deficit, n − k0)`. `FadePolicy.ApplyN` is new, beside `Apply`
   (`FadePolicy.cs:18`), and a property test proves `ApplyN(x, b, n) == Apply^n(x, b)` for every `n` up
   to the cap — the same function, iterated in closed form. A sector whose stability reaches 0 fades to
   unowned exactly as `LoamPhases` does it (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:219`).
   **Every other per-turn state the measured phases mutate advances in closed form too (audit
   2026-09-20).** A rate measured once is only right if nothing it depends on changes over the span. The
   Production phase's siege construction advances `WorldSlot.SlotDepletionMilli` on every yielding turn
   and stops a slot's yield once it is exhausted (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:142-151`,
   `StructurePolicy.IsExhausted`, `gk-core/src/FusionRpg.Core/World/StructurePolicy.cs:66`). So per slot: turns
   to exhaustion `kx` follow from the slot's depletion and the per-harvest step; the slot yields for
   `min(n, kx)` turns of the span, and its `SlotDepletionMilli` ends where `min(n, kx)` harvests leave it
   — the same arithmetic `BoardEconomy.AdvanceDepletionMilli` applies once per turn, iterated in closed
   form, with a property test beside `FadePolicy.ApplyN`'s. Without this the coarse rate would keep an
   exhausted slot yielding and the world's depletion state would never move while hibernating — a coarse
   step that pays **more** than the full step (breaks acceptance 5) and diverges from `Step`'s state.
   **Rule:** `stock-deltas`' rate record must name, per measured phase, every hashed field that phase
   writes; `CoarseStep` refuses (throws at construction, a test fixture proves it) a phase that writes a
   field with no registered closed-form advance. A new field written by a measured phase is therefore a
   reviewed addition here, never a silent staleness.
4. **Frontier contests** (§5), processed in first-loss-turn order.
5. **Calendar pulses.** Boundaries crossed in `(t, t+n]` are counted arithmetically
   (`⌊(t+n)/DaysPerWeek⌋ − ⌊t/DaysPerWeek⌋`, `TurnCalendar.cs:22`); growth pulses that fire on a week
   boundary (recruit accrual, `world-graph-ideal.md` §3.11) apply that many times via the measured rate.
6. **Events.** `world-event-budget` draws `≤ EventBudgetMilli × n / 1000` pulls from the same deck;
   until it lands the slot is empty.
7. **Outcome.** `OutcomeTransition.Apply` (`world-victory` §2), which also carries `world-fall`.
8. **Intel.** One `Observe`-equivalent pass at the end so each faction's belief reflects the new
   ownership (no per-turn intel).
9. `CurrentTurn += n`; hash.

Movement, sieges, assaults and claims are **not** simulated: no unit moves in a hibernating world.
Legions stay where they are; their supply burn is part of step 2.

### 3. System commands into a non-active world

A non-active world refuses player submissions (`world-state-vocabulary` §5). Other modules file
**system-issued** commands into it through **the one shared system-command path `trade-foundation` owns (`trade-foundation` `system-commands`)**
(owner Q10, 2026-09-19; this spec's first draft named a `FileSystemCommandUnlocked` of this program's own —
withdrawn): `release-warden` (`world-warden`) and `rift-trade`'s `rift-window` / `rift-arrive`. (Legion
departure is not one: `advance-carry` resolves the player's own `depart`/`advance` orders in the **active**
world, `spec-advance-carry.md` §1.) They sit in `rpg_world_commands` for the world's
open turn exactly like a player's order (`RpgStore.WorldTurns.cs:159-208`) and are listed in the coarse
record's inputs. `CoarseStep` resolves them first, through the resolver that owns each kind (the same
`WardenResolver.Run`, `gk-core/src/FusionRpg.Core/World/Movement/WardenResolver.cs:23`) — never a second
resolver. The accepted kinds are a closed allow-list; any other kind in a non-active world's list is a
load-time error, not a silent drop.

### 4. The coarse record, and replay

`rpg_world_turn_log` gains three columns (additive, `EnsureColumn`):

| Column | Default | Meaning |
|---|---|---|
| `record_kind TEXT NOT NULL` | `'step'` | `'step'` or `'coarse'` |
| `span INTEGER NOT NULL` | `1` | turns this row advanced |
| `inputs_json TEXT` | `NULL` | the `CoarseInputs` verbatim (coarse rows only) |

A coarse row is keyed `(world_id, turn)` with `turn` = the world's `CurrentTurn` **before** the record —
the same convention a step row uses (the loop variable `t` at `:771` is the turn being ended). Its
`state_hash` is the hash after the record, its `engine_version`/`ruleset_version` the live ones, and the
coarse version rides in `inputs_json`.

Replay becomes:

```
world = WorldCreation.Rebuild(stamp, seed)            // world-creation §6
t = 0
while t <= target:
    row = log(t)
    if row.record_kind == 'coarse':
        world = CoarseStep.Run(world, seed, row.span, stamp, parse(row.inputs_json)).World;  t += row.span
    else:
        world = TurnEngine.Step(world, commands(t), seed, resolver).World;                    t += 1
```

Replay refuses, with a reason, a coarse row whose `CoarseVersion` differs from the live one — the same
honest refusal as `:759-760`. **After the record's one graph write, in the same transaction, the
catch-up runs `legion-build`'s legion reconcile** (`legion-owner-scope` §2 trigger T4, audit 2026-09-20),
so a legion a coarse contest destroyed leaves no layer-5c binding behind. **Report bodies:** a turn inside a coarse span has no report of its own;
`GetWorldTurnReport` for it returns the coarse record's digest. Report trimming
(`RpgStore.WorldTurns.cs:791-805`) never trims `inputs_json` — it is the replay input, like the command
log.

### 5. Frontier contests — Θ difference, seeded, logged

- A **frontier sector** is a player-owned sector joined by a lane to a sector owned by an enemy empire
  (faction kind `Zomboss` or `Rival`; `Clan` never expands and `Wild` is not an empire,
  `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18`).
- Per-turn loss chance: `p = CombatProbability.Sigmoid(ΔΘ − defenceΘ, scale) × pressureMilli / 1000`,
  where `ΔΘ = Θ_content(the enemy's adjacent sector) − Θ_actor(save)` is computed Data-side through the
  one `IPowerIndexProvider` (`IPowerIndexProvider.cs:11-16`) and logged; `defenceΘ` is `world-warden`'s
  logged `DefenceTheta` — `ContestTheta(WardenPower)`, the power program's conversion of the logged
  `legion-power` roll-up, **0 until that §10 row lands** (round 4 P); `scale` and `pressureMilli` are difficulty-profile knobs
  (`world-difficulty-profile`). **No private curve**: the contest reads Θ differences only (DESIGN-GATE
  §2.14).
- First-loss turn: `k = ⌈ln(1−u) / ln(1−p)⌉` with `u` drawn from
  `DeriveStream(seed, $"coarse:{worldId}:{fromTurn}:{sectorId}")`. **Edges, stated (audit 2026-09-20):**
  `p ≤ 0` ⇒ no loss in the span (`k = ∞`, the formula is never evaluated — `ln(1) = 0` would divide by
  zero); `p ≥ 1` ⇒ `k = 1`; `u` is drawn from `[0, 1)` and `k` is then clamped below at 1 (a `u` of 0
  gives `ln(1) = 0`, i.e. `k = 0`, which is not a turn of the span). The result is converted to `long` with
  a checked conversion; a `k` beyond `n` means "no loss in this span". Each edge has its own test.
  `k ≤ n` ⇒ the sector is captured at
  turn `t+k` by the adjacent enemy with the higher Θ_content (ties: ordinal faction id). Losses resolve in
  `k` order; after each, the frontier is recomputed. The number of re-computations is bounded by the
  sector count, never by `n`.
- `ln` is `double`. Floating point is allowed (PRINCIPLES.md §5); because the result feeds a hashed
  state, the coarse record carries the platform stamp the SSOT requires (ssot-power-scale §10.7). **Where
  (audit 2026-09-20):** `CoarseRecord.PlatformStamp` (the same stamp `BattleReport` carries), written into
  `inputs_json`; replay of a coarse row stamped on a different platform **refuses** with a named reason
  (`coarse.platform-mismatch`), the `decisions.md:40` sweep-guard behaviour, rather than re-resolving
  across architectures.

### 6. Determinism — looking never rerolls

Each draw is labelled by the absolute turn it starts from (`fromTurn = world.CurrentTurn`). A range is
consumed exactly once: the catch-up advances `CurrentTurn` and the clock mark, so the same turns are never
drawn again. Looking every turn (n = 1, twenty records) and looking once (n = 20, one record) give
**different but equally distributed** outcomes, and **neither can be re-rolled**. So:

- **Deterministic:** the same `(world, seed, n, stamp, inputs)` gives a byte-identical result and hash.
- **Additive where it can be:** for a window with no discrete event (no loss, no fade-to-unowned),
  `Run(n=a)` then `Run(n=b)` equals `Run(n=a+b)` on every stock and stability term (the rates are
  constant over such a window). Contest outcomes are equal in distribution, not per seed — stated, not
  hidden.

### 7. Triggers

| Trigger | Where | Transaction |
|---|---|---|
| Select a hibernating world | `SelectWorld` (`world-state-vocabulary` §4) | the select's own transaction, **before** activation — a world is never active with pending turns |
| Look at a hibernating world | `POST /api/world/{worldId}/catch-up` (the FE calls it when a hibernating world's view opens; a `GET` never writes) | its own |
| Background budget | after an advancing `CommitWorldTurn` returns, outside its transaction: up to `backgroundCatchUpsPerEndTurn` hibernating worlds of the save, largest pending first (ties: world id) | one per world |

The background path keeps End Turn's own latency unchanged (the commit transaction is not widened) and
lets an unwatched world fall on schedule rather than only when looked at (W4). Its size is a perf
tunable, not a balance number (runbook/perf-probe-plan: main-thread work stays bounded).

**Mandatory catch-up at the window (audit 2026-09-20).** Before the budgeted picks, the background pass
catches up **every** hibernating world of the save whose pending equals `catchUpCapTurns`, regardless of
`backgroundCatchUpsPerEndTurn`. Otherwise a world nobody looks at would forfeit its upkeep and pressure
past the window (`hibernation-clock` §3) and leaving would pay better than staying. The cost stays bounded:
a closed-form record's cost is independent of `n` (acceptance 2), and a world reaches the window at most
once per `catchUpCapTurns` End Turns, so the mandatory set averages at most `h / catchUpCapTurns` worlds
per End Turn for `h` hibernating worlds.

**One catch-up per span, never two (audit 2026-09-20).** The look trigger and the background trigger can
race on the same world. Every catch-up runs in its own transaction and first re-reads the world's
`clock_mark` and `current_turn`; it proceeds only if they equal the values its inputs were built from
(`expectedClockMark`, `expectedTurn` — the `CommitWorldTurn` stale-turn refusal shape,
`RpgStore.WorldTurns.cs:515`). The loser of a race writes nothing and returns `ok.already-current`, so a
span is never simulated twice and its draws are never consumed twice.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | pure `Step` and its phases; fade rule; calendar arithmetic; Θ provider; delegate injection | composed (§2) |
| Wiring gap | replay is template + per-turn `Step` only | §4 |
| Real gap | coarse step, coarse record, triggers, system-command resolution | §1–§3, §5, §7 |

## Acceptance (contract)

1. **Determinism:** the same `(world, seed, n, stamp, inputs)` gives a byte-identical `CoarseResult` and
   hash (run twice, compare canonical text).
2. **Cost independent of `n`:** with `ICoarseTrace` attached, the count of rule-function evaluations for
   `n = 1` equals the count for `n = catchUpCapTurns` on a world with no discrete event — a structural
   assertion, never a timing.
3. `n` never exceeds `catchUpCapTurns` (the caller passes pending; `Run` throws on a larger `n`).
4. **Additivity** (no-event window): `Run(a)` then `Run(b)` equals `Run(a+b)` on every stock and
   stability field.
5. **Leaving never pays more:** for the same state, the production-side stock deltas of `Run(n)` are
   strictly below `n` full steps' production (`YieldMilli < 1000` is validated at load); upkeep is not
   reduced.
6. **Replay:** a world whose log interleaves step and coarse rows replays to every stored hash. *Scope
   (audit 2026-09-20):* the store's re-derivation calls `Step` with the store-free resolver
   (`RpgStore.WorldTurns.cs:769-775`), so a **step** row whose battles were composed with store inputs is
   refused, not replayed (`legion-build` `general-member-hub` Hard edges adds that flag). This criterion
   is asserted over logs with no such flagged row; a flagged row makes the replay refuse by name, never
   diverge silently.
11. **Closed-form completeness:** a fixture phase that writes a hashed field with no registered closed-form
    advance makes `CoarseStep` refuse at construction; `SlotDepletionMilli` advances and exhausts in closed
    form exactly as `n` full steps would (property test).
12. **Edges of the loss draw** (`p ≤ 0`, `p ≥ 1`, `u = 0`) each have a test and never divide by zero.
13. **No forfeit in normal play:** after any sequence of End Turns, no hibernating world's pending exceeds
    `catchUpCapTurns` (the mandatory pass, §7); two racing catch-ups on one world write one record.
7. **No wall clock** inside `CoarseStep` (the determinism guard stays green with no new exemption).
8. Every captured sector appears once in the digest, in capture order, with its turn.
9. `FadePolicy.ApplyN(x, b, n) == Apply^n(x, b)` for all `n ≤ catchUpCapTurns` (property test).
10. A non-active world's command list containing a kind outside the allow-list fails loudly.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/CoarseStepTests.cs` (new): 1–5, 8, 10, 11, 12 on
  `two-hearths`; 13's race half in `WorldCoarseReplayTests.cs` (in-memory store, testing-standard R1).
- `gk-core/tests/FusionRpg.Core.Tests/World/Loam/FadePolicyTests.cs` (extend): 9.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs` and a new `WorldCoarseReplayTests.cs`: 6, the
  three triggers, report-body lookup inside a span, trim never touches `inputs_json`.
- `gk-core/tests/FusionRpg.Guard.Tests` (`WorldDeterminismGuardTests`): 7.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorldDeterminismGuard"
python gk-core/scripts/guard-dal.py
```

Crosses Core and Data: the full suite once at module end.

## Hard edges

- **`rpg_worlds` schema:** none (the clock mark is `hibernation-clock`'s). **Turn log schema:** three
  additive columns.
- **Replay:** the loop gains the coarse branch; `CoarseVersion` is a second refusal key beside
  engine/ruleset. `Step` is not changed by this module, so **no golden moves** for worlds that never
  hibernate.
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave**. This
  module is world-continuity **wave 2** and it grants a player-facing feature (hibernating worlds advancing
  through a coarse catch-up), so it rides **wave 2's single bump** — shared with `world-victory` and
  `world-fall`, taken at landing, never pre-assigned (map *Audit 2026-09-20* R1), recorded in
  [../trade-network/landing-order.md](../trade-network/landing-order.md) — rather than claiming *"no
  `RulesetVersion` bump"*. `CoarseVersion` stays its own, separate refusal key for the coarse form itself.
- **Corpse-cache tick key:** a coarse catch-up is not an End Turn: it never advances the save counter and
  never ticks corpse-cache decay (the save counter is the only tick, `hibernation-clock` §5).

## Dependencies

`hibernation-clock` (n), `seat-outcome` + `world-victory` (the outcome helper); external `world-stamp`
(the stamp input; blocking) and `stock-deltas` (the measured rates; blocking — without it this module
would have to re-derive yields, which is the defect ideal §3.1 forbids). Consumed by `world-fall`,
`world-warden`, `idle-world`, `background-yield`, `world-event-budget`, `away-digest`.

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `backgroundCatchUpsPerEndTurn` | worlds per End Turn (perf bound, structural, commented) | 1 | `data/tuning/world-continuity.v1.json` |
| contest `scale`, `pressureMilli` | Θ units; per-mille | from the difficulty profile | `world-difficulty-profile` |

## Boundaries

- **Always:** compose `Step`'s phases; log every input; one graph write per record.
- **Ask first:** simulating unit movement in a hibernating world.
- **Never:** a loop over `n`; a live Hub or Θ read during replay; a second resolver for a command kind;
  a wall clock; scaling upkeep down.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `CoarseStep.Run`, `CoarseInputs`, `CoarseRecord` | `idle-world`, `world-warden`, `background-yield`, `world-event-budget` |
| Coarse turn-log rows (`record_kind`, `span`, `inputs_json`) | `away-digest`, replay |
| Catch-up triggers | `world-state-vocabulary` (select), `multiverse-surface` (look) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn engine phases, loam fade, calendar, power index, world store log and replay.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md; trade-foundation-map.md §2.4, §2.6.
    Not read: runbook/perf-probe-plan.md and research/perf/00-baseline.md (Performance row) — the
    background budget's perf reasoning rests on PRINCIPLES.md §3, not on those docs. Gap stated.
[x] decisions.md checked: phase-order row (no phase added to Step).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: replay loop and refusal, log DDL, FadePolicy.Apply, TurnCalendar,
    IPowerIndexProvider, the Hub delegate seam.
[x] Surrounding sections read (replay's delve refusal; trim's budget-debit comment).
[ ] Constraint tested: "no golden moves" rests on Step being unchanged; not measured.
[x] No §2 invariant contradicted: contests read Θ difference; floating point with a platform stamp.
[x] Corrections propagated: map module 6 row matches (stock-deltas named as the rate source).
[x] No population pinned.
[x] No cache.
[x] Orderings: additivity is stated only where it holds; contest splits are stated equal in
    distribution, not per seed.
[x] Actor magnitudes: consumed as logged Θ values from the one provider; no private fold.
[x] No SOLID fork: phases composed, one resolver per command kind.
[ ] Registry rows: "no wall clock in CoarseStep" rides the existing determinism guard; "no loop over
    n" is acceptance 2's test — rows added when built.
```
