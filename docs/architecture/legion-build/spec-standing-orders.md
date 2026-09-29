# Spec: `standing-orders`

**Status: written against shipped code 2026-09-19.** Module id `standing-orders`, row 8 of the
[legion-build map](../legion-build-map.md) (wave 2; no dependencies inside this program; `trade-network`
`fleet` depends on it and needs it early). Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.3
and owner decision **L3**. **Owner decision SO (2026-09-19), accepting `fleet`'s request** (trade-network
map CM5, `docs/architecture/trade-network/fleet-map.md:19,89-91`): *standing orders carry a kind, and
each kind has its own resolver; the trade-route order is one kind.*

## Objective

A legion may hold one **standing order**. Each turn, the order's kind resolver turns it into an ordinary
`WorldCommand` that enters the one command pipe every human and AI order already uses, so a legion keeps
marching, escorting or running a trade route without the player re-filing it — with or without a
commander, because automation reads the order, never the roster.

Success looks like: an emitted command is resolved exactly as the same command filed by hand; an explicit
order for that legion this turn always wins; replay needs no new case; a world where no legion holds an
order hashes byte-identically to today.

## Scope and non-goals

- **In:** the order record on a legion; the closed kind vocabulary and resolver registry; two commands
  (`set-order`, `clear-order`); the emitter at the turn barrier; precedence; the lifecycle rules; the
  `repeat` kind's resolver.
- **Out:** the `escort` kind's resolver (`escort-stance`); the `trade-route` kind's resolver (`fleet`
  `trade-route-order`, `fleet-map.md:259-300`); the `crew` kind's resolver (`fleet` `crew`,
  `fleet-map.md:19,230-258`); FE surfaces.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | The AI builds one `WorldCommand` per legion, in the player's shape | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-582` |
| Built | AI orders are **written into the command log** at the barrier, after the same admission a person's order passes; replay never re-runs a policy because the log is the save | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-291` (insert at `:285`; *"replay never re-runs a policy"* at `:237-240`) |
| Built | The barrier: AI fill, then the all-committed check, then the command list is read and `Step` runs | `RpgStore.WorldTurns.cs:527-539,601` |
| Built | Reveal re-admits every command and drops with a reason; a routed legion's orders drop for its recovery turn | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:233-244` |
| Built | A march resumes mid-lane when the same path is re-issued | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:29-31` |
| Built | Canonical rows can be emitted only when present, keeping older worlds' bytes (the intel precedent) | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:71-72` |
| Built | A command-only addition moves no stored log and no golden (round 6 C1: the wave still takes one bump) | `TurnEngine.cs:134-140` |
| Real gap | Nothing stores an order; the client must resubmit | `docs/architecture/world-stage/spec-world-commands.md:266-267`; `docs/architecture/world-stage-ideal.md:246` |

## Design

### 1. The record

```csharp
public sealed record StandingOrder
{
    public string OrderId { get; init; } = "";      // "so-{turnSet}-{entityId}", derived from cause
    public string Kind { get; init; } = "";         // StandingOrderKinds, closed
    public WorldCommand? Template { get; init; }    // repeat: the command to re-issue; others: kind payload
    public string? KindState { get; init; }         // the kind's own small state, owned by its resolver
    public int SetOnTurn { get; init; }
}
// WorldEntity gains: public StandingOrder? StandingOrder { get; init; }
```

`KindState` is where `trade-route`'s phase (outbound, loading, inbound, unloading) lives
(`fleet-map.md:266`: *"lives in the standing order's own hashed record, which `legion-build` owns"*).
It is an opaque, resolver-validated string so this module never learns a kind's states.

### 2. The closed kind vocabulary and the resolver seam

```csharp
public static class StandingOrderKinds
{
    public const string Repeat = "repeat";           // this module
    public const string Escort = "escort";           // escort-stance
    public const string TradeRoute = "trade-route";  // fleet trade-route-order (owner decision SO)
    public const string Crew = "crew";               // fleet crew (fleet-map decision SO: "crew is a second kind")
    public static readonly IReadOnlyList<string> All = new[] { Repeat, Escort, TradeRoute, Crew };
}

public sealed record StandingOrderAdmission(bool Ok, string Reason, string? InitialKindState,
                                            IReadOnlyList<string> Warnings);

public interface IStandingOrderResolver
{
    string Kind { get; }
    // At submit (through WorldCommandAdmission) AND again when set-order resolves in Snapshot — the
    // "re-validated, never trusted from admission" discipline RaiseResolver states. Returns the order's
    // initial KindState and any warning tokens (admitted, reported, never refused).
    StandingOrderAdmission Validate(WorldState world, WorldEntity legion, StandingOrder order);
    // At the barrier: the one command to file this turn, or null to file nothing. Reads the owner's
    // BELIEVED world — an order sees what its faction knows, exactly like an AI policy.
    WorldCommand? Emit(IWorldView ownerView, WorldEntity legion, StandingOrder order, int turn);
    // Inside Step (Snapshot), after everything resolved: the order's next state, or null to end it.
    StandingOrder? Advance(StandingOrder order, WorldEntity legionAfter, WorldState world);
}
```

**One writer for order state.** Hashed order state changes only inside `Step`, and only through
`StandingOrders.WithKindState(world, entityId, kindState)` / `StandingOrders.End(world, entityId, reason)`.
The default call site is `Advance`, run for every order at the end of Snapshot. A kind whose transitions
belong to a phase its own program adds may call the same writer from that phase instead and return the
order unchanged from `Advance` — `fleet`'s `trade-route` transitions in trade-network's Logistics phase
(`docs/architecture/trade-network/fleet/spec-trade-route-order.md:43-44`). Either way there is one writer,
and the pre-`Step` `Emit` only reads.

`StandingOrderResolvers` is a closed registry keyed by kind. A kind whose resolver has not landed is
declared but unregistered, and `set-order` refuses it with `standing.kind-unavailable` — so `trade-route`
and `crew` can be named today and armed by `fleet` without either program waiting on the other (the
`CrossProgramLandedFlags` shape, `gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs:10`). Adding a
fifth kind is a reviewed change to the list, its membership test and this spec.

### 3. The `repeat` resolver (this module's kind)

`Template` is a command naming the legion as `EntityId`, of an allowed inner kind: `move`, `stance`,
`sustain`, `claim` (the kinds whose meaning is "keep doing this"). `Emit` returns the template with this
turn's `CommandId`. `Advance` ends the order when a `move` template's destination has been reached
(nothing left to march) and otherwise keeps it. Any other inner kind is refused at set time
(`standing.repeat-kind`).

### 4. Commands

`WorldCommandKinds` gains `set-order` (payload: the `StandingOrder` minus id/turn) and `clear-order`
(`WorldCommand.cs:124-126`'s list grows by two). Both name a legion the commander owns (admission) and
resolve in **Snapshot**; an order set in turn *t* is first emitted at turn *t + 1*'s barrier. A legion
holds at most one order: `set-order` replaces, with a report line naming the old kind.

### 5. The emitter — at the barrier, into the log

A pure Core function `StandingOrderEmitter.Emit(WorldState, IReadOnlySet<string> entitiesWithFiledOrders,
int turn)` returns the commands; the Data layer calls it **after** the all-committed check and **before**
the command list is read (between `RpgStore.WorldTurns.cs:535` and `:539`), and inserts each command
through `InsertCommandUnlocked` with reason `standing:{OrderId}`. **Walk order (corrected by the 2026-09-20
audit):** the first draft said "entities in ordinal order", but `escort-stance` §3 needs every charge's
command before it emits the escort's (*"the emitter processes non-escort orders first and escort orders
last, in one barrier pass"*). So each registered kind declares a `Pass` rank (a closed, per-kind
constant: `repeat`, `trade-route`, `crew` = 0; `escort` = 1), and the emitter walks
`(Pass, EntityId)` in ordinal order, handing pass-1 resolvers the commands already filed or emitted this
turn. A kind whose `Emit` reads another legion's command states its pass in the same reviewed change that
registers it. The order is total and deterministic, so the log the emitter writes is identical on every
rerun.

Because the emitted commands are **in the log**, replay reads them like any other command and never
re-runs the emitter or a resolver's `Emit` — the AI precedent exactly (`:237-240`).

### 6. Precedence — order-independent by construction

A legion whose owner has filed **any** command naming it (`EntityId`) this turn is skipped. Emission
happens once, at the barrier, after every person has committed and after AI fill (`:527`), so "explicit
wins" holds whatever order the player filed their orders in, and whether the standing order was set
before or after the explicit order was filed.

### 7. Lifecycle — each a stated rule

| Event | Rule |
|---|---|
| The emitted command is inadmissible or illegal at Reveal | dropped with its reason, like a hand order (`TurnEngine.cs:233-236`); **the order stays stored** — a blocked march resumes when the lane opens |
| The legion is routed | its emitted command drops `entity.routed` for the recovery turn (`TurnEngine.cs:244`); the order stays |
| The resolver's `Advance` returns null | the order ends, with a `standing.ended:{kind}` report line |
| `clear-order` / `set-order` | clears / replaces |
| The legion is destroyed or disbanded | the order goes with the entity |

### 8. Hash, persistence, wire

- **Hash:** an `order` canonical row for each entity **holding** an order, written after its entity's
  member rows. Worlds with no order hash byte-identically (the `WorldCanonical.cs:71-72` precedent).
- **Persistence:** `EnsureColumn(rpg_world_entities, standing_order_json TEXT)`, `NULL` when absent.
- **Wire:** the order on the owner's own entity DTO; two command kinds on the submit DTO.

## Tunables

None. No number decides anything here.

## Numeric types

`SetOnTurn` is `int` like every turn number in the world model (`WorldState.CurrentTurn`).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StandingOrder|FullyQualifiedName~TurnEngine|FullyQualifiedName~Movement"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldCommand|FullyQualifiedName~WorldAi|FullyQualifiedName~WorldTurn"
python gk-core/scripts/guard-dal.py
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                    MODIFIED  WorldEntity.StandingOrder
src/FusionRpg.Core/World/Orders/StandingOrder.cs          NEW       record, kinds, resolver seam, registry
src/FusionRpg.Core/World/Orders/RepeatOrderResolver.cs    NEW       §3
src/FusionRpg.Core/World/Orders/StandingOrderEmitter.cs   NEW       §5 (pure)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs             MODIFIED  set-order, clear-order
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs    MODIFIED  two arms
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs               MODIFIED  Snapshot: set/clear, then Advance
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                MODIFIED  order row when present
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs + WorldGraphDiff.cs   MODIFIED  column
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs          MODIFIED  emit at the barrier
gk-core/src/FusionRpg.Contracts/WorldDtos.cs + Server/WorldEndpoints.cs   MODIFIED  wire
```

## Testing strategy

- **Indistinguishable.** For every allowed `repeat` inner kind, a world with the order and one where the
  same command was filed by hand resolve to the same state and the same report lines except the
  command id.
- **Precedence, both orders.** (a) order stored, then explicit filed → explicit resolves, nothing emitted;
  (b) explicit filed, then `set-order` filed the same turn → explicit resolves, order stored, first
  emission next turn. And the AI case: an AI faction's own filed order beats its legion's standing order.
- **Lifecycle.** One test per row of §7.
- **Resume.** A `repeat move` whose legion ran out of budget mid-lane resumes next turn from its lane
  progress (`MarchResolver.cs:29-31`).
- **Replay.** A logged turn containing emitted commands replays byte-identically with the emitter
  disabled (proves replay never needs it).
- **Hash.** A world with no order: canonical bytes unchanged. A world with an order: exactly one `order`
  row per holder.
- **Pass order** (audit 2026-09-20). A charge's emitted command exists before its escort's `Emit` runs, for
  every entity-id ordering of the two (both orders tested).
- **Vocabulary.** `StandingOrderKinds.All` pinned to its four members with the reason; an unregistered
  kind is refused `standing.kind-unavailable`; a registered one resolves through its resolver only.
- **Fog.** `Emit` receives the owner's `BelievedWorldView`, never the true world (a resolver asserting on a
  hidden sector sees it as unknown).

## Boundaries

- **Always:** emit into the log at the barrier; skip a legion with an explicit order; resolve state
  changes inside `Step`.
- **Ask first:** more than one order per legion; an order on a non-legion entity; running `Emit` inside
  `Step`.
- **Never:** a second command pipe; re-running an emitter on replay; a kind resolver outside the registry.

## Success criteria

1. Emitted commands are hand-equivalent; explicit orders always win, order-independently.
2. Replay needs no emitter; worlds without orders hash unchanged.
3. The kind seam is live: `repeat` registered here, `escort` by `escort-stance`, `trade-route` and `crew` by `fleet`.

## Interface exposed to dependents

`StandingOrder`, `StandingOrderKinds`, `IStandingOrderResolver`, `StandingOrderResolvers.Register` —
consumed by `escort-stance` (the `escort` kind) and `trade-network` `fleet` (`trade-route`, `crew`).

**Answers `trade-ai-map.md` ask T-A2 (round-4 reconciliation):** a legion on a trade standing order is
identifiable from world state — its entity carries the stored order, and `StandingOrder.Kind ==
StandingOrderKinds.TradeRoute` (or `Crew`) says so. The order is hashed state on the faction's own entity, so
an AI policy reads it for its **own** legions through the world view it already receives; nothing new is
exposed about a foreign legion's orders.

## Hard edges

- **New hashed state, no re-bless, but it does ride its wave's bump** (rewritten 2026-09-20,
  reconciliation R-19.4; `legion-build-map.md` §14 already listed this spec as rewritten under round 6 C1
  and the rewrite had not landed). The `order` row exists only for holders and `set-order` is a new kind no
  stored log carries, so every stored world and log resolves and hashes as before
  (`TurnEngine.cs:134-140`) and **no golden is re-blessed**. But this module *grants a feature*, so under
  round 6 C1 it registers `legion.standingOrders` and rides its wave's single `RulesetVersion` bump — the
  earlier *"no bump"* claim is withdrawn, and so is the reading of map X11 that followed from it. The wave
  and the bump are the family's: see [trade-network/landing-order.md](../trade-network/landing-order.md) §2.
- **Schema:** one nullable column.
- **Closed vocabulary widened:** `WorldCommandKinds` +2 (`set-order`, `clear-order`). The pinned membership
  test names members, and its expected count is whatever the list holds when this lands — several modules
  across both programs widen the same list (audit 2026-09-20: "18 → 20" would be wrong by landing time).

## Dependencies

None in this program. `fleet` waits on it (`docs/architecture/trade-network-ideal.md:565`).

## Design-gate checklist

```
[x] Subsystems: world commands, turn barrier, turn engine (Snapshot), world hash and persistence.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, fleet-map.md (asks), trade-network-map.md CM5, DESIGN-GATE,
    PRINCIPLES §3-§13. NOT read: world-map row documents, spec-ai-commander.md.
[x] decisions.md checked: World turn phase order (:7) — no phase added; resolution sits in Snapshot.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: the barrier sequence, AI insertion and replay note, Reveal drops, march resume,
    the canonical intel precedent, the no-bump precedent, the command storage shape.
[x] Read the surrounding section of every rule quoted.
[~] No suite run; indistinguishability and replay are acceptance tests.
[x] No §2 invariant contradicted.
[~] Corrections propagated: X11 corrected in map §10.
[x] Pinned literal: StandingOrderKinds (4) is a closed vocabulary with its reason; WorldCommandKinds (20).
[x] No event-refreshed cache (emission reads the world at the barrier every turn).
[x] Precedence is order-independent and both orders are tested.
[x] No actor magnitude.
[x] No parallel path: one pipe, one emitter, one registry.
[x] New rule "emitted commands enter only through the barrier emitter" — guard: a source scan that
    StandingOrderEmitter has exactly one production caller; registry row written with the change.
```
