# Lawn combat AI — the ideal

**Status: FOLDED into [combat-ai-ideal.md](combat-ai-ideal.md) (2026-09-20)** as its **lawn profile**. That file owns the shared core, the principles and the build route. This file is kept for its lawn-specific detail, and where the two disagree, `combat-ai-ideal.md` wins. Originally: idea phase, 2026-09-20. It comes from owner ruling D2
([backlog-clean-up/rulings-2026-09-20.md](backlog-clean-up/rulings-2026-09-20.md)). This is not a spec,
and no build is authorized. The full `/idea` enrichment, with its reads listed in §7, runs before a map.
**Owning plan:** the lawn plan written by `backlog-clean-up` `orphan-plan-authoring` (`tasks/lawn-plan.md`),
as a sibling program of `lawn-playable` and `lawn-tuning-profile`.

---

## 1. The owner's direction (verbatim intent)

> Keep the lawn combat loop on; tune stamina later. There is no action casting in the lawn run except
> the basic attack. Trigger actions from the **basic attack count and a timer**, so a simple AI spends
> resources while they are available. That is a `lawn-combat-ai`. Extend the idea if there is better AI
> combat logic, but keep the performance impact small. This AI combat control lives in the **RPG AI
> layer**: it monitors the lawn combat FSM and decides what to cast, and the basic attack keeps working
> alongside it.

## 2. Why it matters (the problem it closes)

- **Every lawn actor's kit is dead weight today.** Actions, rungs, costs, cooldowns and statuses all
  exist, and battle casts them through `StubIntentSource`. On the lawn, only the basic attack rider
  spends a resource (`LawnBasicAttackCostCharger`).
- **Stamina never empties** (`lawn-tuning-profile` M2; `lawn-combat-wire` proof 5 / L-N2), because the
  only spender is the basic attack while aptitude regen outruns it. An actor that casts its kit spends
  its pools as designed. Exhaustion then becomes reachable through **play**, not only by shrinking pools.
  That changes what `lawn-resource-scale` must tune.
- It is the automatic counterpart of `lawn-interactive` Checkpoint E ("combat book full arm→Intent",
  deferred until the action corpus). The player arms by hand; the AI arms for everyone else. Both should
  resolve through the same intent-to-cast path.

## 3. What already exists (verified in code this session)

| Piece | Where | What it gives this feature |
|---|---|---|
| Intent seam | `Core/Battle/Timeline/IntentSource.cs` (`IIntentSource`, `ActionIntent` struct, `None` encoded in value) | A decision interface with no per-call allocation |
| Simple AI | `Core/Actions/StubIntentSource.cs` | Nearest enemy, then the first usable held action (preference-ordered), gated by stance, bound, cooldown and affordability. Reads only `IBattleView`. Its reads are bounded by the actor's own held-action count. |
| Board view | `Core/Battle/Board/BoardSnapshotAdapter.cs` | A "frozen lawn census" (`Ptr, Side, TypeId, Col, Row, …`), already shaped like the lawn |
| Lawn clock | `KernelDriveHost` (injector adapter over Core `TimelineDrive`), one kernel per board | A scaled, pause-respecting simulated clock. `LawnBasicAttackCostCharger.NowTick` = `NowTicks / 100` (100 ms lawn ticks) |
| Lawn cost authority | `LawnBasicAttackCostCharger` over Core `CostLedger` / `LawnBasicAttackCostGate` | The **same** cost types battle uses, not a second authority (`guard-actor-hub.py`) |
| Swing identity | `EventDrain` stamps `IsFirstOfSwing` | A per-actor **basic-attack counter** can hook here at no new detection cost |
| Control-loop lock | `overlay-control-loops.md` §3 | Lawn decisions are **Hot**: injector in-process, never a Server await |

## 4. The shape

### 4.1 Where it lives
- **Decision logic in Core**, under the RPG AI layer, beside `StubIntentSource`. CI never builds the
  injector (`KernelDriveHost`'s own note), so logic placed in the injector is untested.
- **The injector only adapts:** it feeds the triggers (swing count, kernel clock) and executes the
  chosen intent through the existing Hot path. That path is effect bag → Funnel → EntityStatWriter, with
  costs charged by the existing `CostLedger` gate. There is no new write path.

### 4.2 When it decides: the owner's triggers, kept cheap
A decision runs **only on a trigger edge**, never per frame and never per hit. The two triggers are OR'd:

| Trigger | Mechanic | Cost |
|---|---|---|
| **Swing count** | Every `N` first-of-swing records for that actor | An integer increment on a record already being drained |
| **Timer** | Every `T` lawn ticks since the actor's last decision | One comparison, evaluated only when a kernel pass already runs |

`N` and `T` are tunables in `data/tuning/lawn-combat-ai.v1.json` (new; does not exist yet). They can be
set per family or rung, and are never code literals. A decision that finds nothing usable costs one
`TryDeclare`, which is already bounded by held-action count.

### 4.3 What it decides: the owner's simple AI, then the extension
**v1 (the owner's baseline).** Reuse `StubIntentSource` unchanged: first usable, affordable,
off-cooldown action on the nearest enemy. This is the "spend while resources last" behaviour. It
drains stamina, makes exhaustion reachable, and exercises every held action.

**Extension (proposed; each piece has a cost in perf-budget terms):**
1. **Reserve floor.** The AI casts only while the pool stays above a tunable reserve. The basic attack
   then never starves, and "spam" becomes "spend the surplus". Cost: one comparison. This answers the
   owner's "basic attack keeps working together".
2. **Rung and tag preference, no search.** Order held actions once per board (the frozen set is
   already preference-ordered: `ActionTagPreference`), for example finishers when the target is low and
   area actions when a lane is dense. The order is static per actor. The decision stays a single pass.
3. **Lane-local targeting.** On the lawn, "nearest enemy" means same lane first, then adjacent lanes,
   from `BoardSnapshot` `Row/Col`. This is still one target per decision, which keeps `StubIntentSource`'s
   bounded-reads property.
4. **Budget cap per frame.** A global cap on decisions per frame, with the overflow carried to the next
   frame. It protects the 300-zombie case the lawn perf work measured.
5. **Deliberately not in v1:** utility scoring, lookahead, threat maps, and cross-actor coordination.
   These are the `ai-behavior-trees-utility-ai` family. Revisit only after v1's live numbers exist.

### 4.4 Which actors it drives
- RPG-backed lawn actors: Bound specimens, and general plants holding actions.
- Zombies read their side's allocation and Θ, via `lawn-tuning-profile`'s `zombie-power-source`, so both
  sides run the same AI with different inputs. That matches the symmetric-empires ruling R23.
- The player's manual arm (`lawn-interactive` Checkpoint E), when built, **pre-empts** the AI for that
  actor's next decision. There is one intent path, and the manual choice wins.

## 5. Performance guardrails (the owner's constraint, made measurable)

- Decisions run on trigger edges only. There are zero allocations per decision, the same acceptance
  line `StubIntentSource` already carries.
- There is a new `PerfProbe` section (`lawn.ai.decide`) with a budget share. It goes in
  `lawn-perf-budget.v1.json` (new; does not exist yet), which the lawn plan already makes the first task, beside
  `effect.onCapture`.
- An A/B at 300 zombies, AI on vs off, is part of `lawn-scale-live-proof`. The AI ships default-on only
  inside the budget. The kill switch follows the `LawnBasicAttackFeature` pattern: a constant default,
  an env override, and a debug override.

## 6. Relations and dependencies

- **Content:** lawn actors need held actions to cast. The action corpus run (D4, B0→B1 authorized) is
  what populates real kits. Before it runs, v1 is proven on fixture kits.
- **`lawn-playable` `exhaustion-event`:** the AI is the first real producer of exhaustion edges on the
  lawn, and the two land together in the lawn plan.
- **`lawn-tuning-profile`:** `lawn-resource-scale` and `basic-attack-cost-scale` are tuned against AI
  spend, not against basic-attack-only spend. This is the owner's "tune stamina later".
- **ActorHub / SOLID:** the AI reads Hub-composed numbers and charges through the existing cost gate.
  No second composer and no private resource fold.

## 7. Reads owed before the map (DESIGN-GATE §1 rows; not yet read in full this session)

`docs/architecture/action-ideal.md` (sealed) · `action-map.md` (the action-selection and lawn rows) ·
`action/spec-action-selection.md` (T33/T34) · `battle-engine-ssot.md` ·
`overlay-control-loops.md` (§3 read; §6 Hot fail-closed rules still to read) ·
`event-pipeline-v2-ssot.md` · `lawn-interactive/spec-commander-action-bar.md` ·
`runbook/perf-probe-plan.md` · `research/genre-mechanics/README.md` (prior art: auto-battler and
tower-defense skill triggers).

## 8. Open questions

None for the owner. N, T and the reserve floor are tunables, decided by principle and published as
`v1` (the "decide tunables by principle" rule). Everything else follows from D2 and the existing seams.
