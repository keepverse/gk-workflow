# Spec: choice-resolution

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `choice-resolution`, row 13 of the [npc-story-events map](../npc-story-events-map.md) (`:218`), wave 3.
Depends on `storylet-selection` (the offer being answered), `cast-resolver` (who fills each role, `{reward}`/`{cost}`
bindings) and `host-content-theta` (`Θ_content`). Consumed by `outcome-routing` (which applies what this module
decides) and every wave 4 host. Gate **G3** (`npc-story-events-map.md:298`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Answer one choice of one offered storylet, identically for every host:

1. decide whether the choice is **eligible** for its kind (`interact`, `leave`, `use:{tag}`, `offer:{stock}`,
   `fight`, `bring:{tag}`, `persuade`, `threaten`);
2. compute its **odds** — the same function shows them to the player and rolls them;
3. **resolve** it to exactly one outcome of that choice: by a contest on `Θ_actor − Θ_content` through
   `CombatProbability.Sigmoid`, by the shipped flat coin for a disposition-only shift, or by the engine's existing
   ordinal draw;
4. price an `offer` through the existing pricing, and hand a `fight` to an existing battle mode as a
   `BattleRequest` or an `IIntentSource`;
5. record `choice.picked` in the story ledger, once.

It **decides**; it never applies. Paying, spending, shifting a band, starting a fight or playing a scene is
`outcome-routing`'s, through paths that already exist.

Success looks like: with the game closed, a fixture storylet on a fixture host is answered for every choice kind;
the odds returned before the answer equal the probability the roll used; answering the same offer twice returns the
first resolution and writes one fact; replaying from the same seed, ledger and corpus revision gives the same
outcome.

## Locked anchors

- **Contests read `Θ` differences** (map principle 5, `:86-90`; ideal §6.9 item 2, `npc-story-events-ideal.md`):
  `CombatProbability.Sigmoid(double delta, double scale)` (`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8-9`).
  `Θ_actor` is the SSOT actor axis (`docs/architecture/power/ssot-power-scale.md:227-231`) composed by
  `PowerIndexComposer.ActorExplain(PowerTuning, ActorLadderSnapshot)` (`gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:53`);
  `Θ_content` is `host-content-theta`'s (`spec-host-content-theta.md` §3).
- **The flat coin** for a shift that does not scale with power is the shipped `Flatter` shape: the caller rolls
  `NextPerMille() < wild.talk.flatterMilli` and passes the result in (`gk-core/src/FusionRpg.Core/Delve/Wild/TalkTree.cs:86-94`).
- **No new contest scale** (ideal §7 row "Contest scale for skill checks", `npc-story-events-ideal.md`): the scale
  is an existing `stats.v1.json` key read through `CombatProbabilityPolicy` (`gk-core/src/FusionRpg.Core/Stats/Derived/CombatPolicies.cs:8-14`).
- **Prices read `P(Θ_content)`** through `SoulSinkPolicy.Price` (`gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:40`)
  via the Delve's `OfferPricing.Souls` (`gk-core/src/FusionRpg.Core/Delve/Wild/OfferPricing.cs:32`), whose floor is
  `DelvePrices.OfferFloor` (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:78`).
- **The battle engine is the SSOT for every battle** (map principle 10, `:105-107`; DESIGN-GATE §1 "Battle" row,
  `battle-engine-ssot.md` §5): a fight is a `BattleRequest` (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39-83`) or
  an `IIntentSource` (`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:27`) handed to an existing mode.
- **Show the odds; no lose-lose; risk priced in cost, time or a fight** (ideal §6.2 fairness bullet, `:357-359`).
- **NS7**: every widened storylet has exactly one `leave`, validated at load (`spec-storylet-contract.md` §5).
- **Rolls on named streams** (map principle 12, `:111-114`), rooted in the host's stream root
  (`IStoryletHost.StreamRoot`, `spec-storylet-reseam.md` §2).

## Design

### 1. Input: an offer, never a storylet id alone

A player never answers "storylet X". They answer **the offer** a host made: which storylet, at which revision, with
which cast, at which host site and host clock. `storylet-selection` produces it and the host persists it as a
`storylet.seen` fact (`spec-story-ledger.md` §2). This module consumes:

```csharp
namespace FusionRpg.Core.Narrative.Choices;

/// The offer being answered. Built from the storylet.seen fact the host wrote when it showed the storylet
/// (field names provisional until spec-storylet-selection.md fixes them; this module reads, never writes, it).
public sealed record StoryletOffer(
    string OfferRef,               // the seen fact's source_ref: "offer:{hostKind}:{slotKey}:{hostClock}"
    string HostKind, string SlotKey, long HostClock,
    string StoryletId, long Revision,
    string? PinKey,                // set when the storylet is an arc link (spec-story-ledger.md §4)
    StoryletCast Cast);            // spec-cast-resolver.md §6
```

The storylet row is loaded **by revision**: an arc link from its pin (`GetStoryPin` → `StoryletCanonical.Parse`,
`spec-story-ledger.md` §4, `spec-storylet-contract.md` §4); anything else from the live catalog, refusing
`choice.revision-moved` if the live revision differs from the offer's and there is no pin. A texture storylet
whose corpus moved between offer and answer is therefore refused rather than resolved against text the player
never saw; the host re-offers on its next pulse. Legacy rows (`IsLegacy`, `spec-storylet-contract.md` §2) are
never answered here: the Delve adapter keeps answering them through `DelveStoryletHost.Answer`
(`spec-storylet-reseam.md` §2).

### 2. What the host supplies

Everything a choice reads that is not the storylet is supplied by the host through one read-only context, so the
module never reaches into a place's state:

```csharp
public sealed record ChoiceContext(
    IStoryletHost Host,
    int ThetaActor,                          // PowerIndexComposer.ActorExplain(power, ladder).Total
    int ThetaContent,                        // HostContentTheta.For*(...).Theta
    FactReader Facts,                        // the same reader eligibility compiled against
    IReadOnlyList<PartyMember> Party,        // the creatures present at the host (delve party, legion members, expedition squad; empty at the homeworld)
    IReadOnlyDictionary<string, long> SupplyHeld,   // supply tag -> count at the host (the Delve pack; empty elsewhere)
    long SoulBalance,                        // read, never spent here
    ulong Seed,                              // the host's root seed for this offer
    PowerTuning Power, NarrativeTuning Narrative);

public sealed record PartyMember(string InstanceId, string SpeciesId, string Side,
    string ElementPrimary, IReadOnlyList<string> TraitIds);
```

`ThetaActor` is the summoner's axis (Garden Keeper level, realms advanced, runs — the SSOT's three terms): a
storylet choice is the summoner's decision, not one creature's. A contest where a specific creature acts (a `bring`
choice's creature does not contest; see §4) would need that creature's own Θ, which is party-dungeon's
`ActorThetaSeam` gap (`gk-core/src/FusionRpg.Core/Delve/Difficulty/ActorThetaSeam.cs:8-22`) and is not invented here.

### 3. Eligibility per choice kind

A choice is **eligible** when its `Condition` (compiled through `PredicateCompiler`, `spec-storylet-contract.md` §2)
holds on `Facts`, its `RoleGate` names a role the cast bound (`spec-cast-resolver.md` §3), and its kind rule holds:

| Choice kind | Kind rule (all must hold) | Refusal id |
|---|---|---|
| `leave` | always | — |
| `interact` | always | — |
| `use:{tag}` | `SupplyHeld[tag] ≥ 1` — the same "holds the tag" test `EventChoices.IsEligible` applies today (`gk-core/src/FusionRpg.Core/Delve/Events/EventChoices.cs:41`) | `choice.supply-missing` |
| `offer:{stock}` | the stock is **priced** (§5) and affordable: `SoulBalance ≥ price` for `souls` | `choice.offer-unpriced`, `choice.offer-unaffordable` |
| `fight` | the host declares a fight path (§6) and the storylet binds an opponent | `choice.fight-no-path` |
| `bring:{tag}` | some `PartyMember` matches the tag (the party-composition leaf, `narrative-predicates`) | `choice.bring-missing` |
| `persuade`, `threaten` | always (the contest may fail; failing is an outcome, never a refusal) | — |

An ineligible choice is **shown with its reason** (a `ChoiceView` with `Eligible = false` and the refusal id) —
never hidden, because a greyed "bring a fire creature" option is what teaches the player that the roster unlocks
choices (FTL, ideal §4.5 item 7). Answering an ineligible choice is refused with its id.

`leave` is always eligible and always resolves to "nothing happens"; it writes `choice.picked` and no consequence.

### 4. Resolution per kind

Every choice owns 1–3 outcomes, each with an ordinal (`good`, `mixed`, `bad`; `spec-storylet-contract.md` §2).

| Kind | How one outcome is chosen |
|---|---|
| `leave` | none |
| `interact`, `use`, `offer`, `bring`, `fight` | one outcome: that outcome. Several: the engine's existing ordinal draw — the drop-band weights `OutcomeResolver` already applies (`gk-core/src/FusionRpg.Core/Delve/Events/OutcomeResolver.cs:35-46`), moved by `storylet-reseam` — on stream `{root}:choice:{slot}` |
| `persuade`, `threaten` | a **contest**: `p = CombatProbability.Sigmoid(BattleRuleset.BaseDodge(ThetaActor) − BattleRuleset.BaseDodge(ThetaContent), scale)` — the `Θ` difference expressed in the contest scale's own units (Audit 2026-09-19, below); success picks the choice's best-ordinal outcome, failure its worst (ties between equal ordinals break by slot order in the seed file, which the contract makes unique). Roll: `NextPerMille()` on stream `{root}:choice:{slot}:contest`, success when `roll < round(p × 1000)` |
| a choice whose **only** consequence is `relation.shift` and whose effects are empty | the **flat coin** instead of a contest: `roll < wild.talk.flatterMilli` (the Delve's own `dungeon` tuning key, read directly — Audit 2026-09-19, §8), the `Flatter` shape (`TalkTree.cs:86-94`), because a band step does not scale with power |

`fight` resolves to its outcome **conditionally on the battle's result**: the outcome carries `battle.start`, and
`outcome-routing` applies the rest of the outcome's effects only after the battle mode reports a win (§6).

**Scale.** The contest reads `CombatProbabilityPolicy.AccuracyScale` (`CombatPolicies.cs:10`), the contest scale the
Delve's actor contest already uses (`ActorThetaSeam.cs:29-32`).

Audit 2026-09-19 — **unit mismatch, fixed.** `AccuracyScale` (100 in `stats.v1.json`) divides a difference of
**accuracy points**, not of `Θ`: the shipped contest feeds it `BaseAccuracy(Θa) − BaseDodge(Θd)`, and one `Θ` is
worth 26 of those points (`BaseAccuracy(θ) = 220 + 26θ`, `BaseDodge(θ) = 26θ`,
`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:367-368`; `ssot-power-scale.md` §2). The draft fed it a raw `Θ` difference,
which made a narrative contest ~26× flatter per `Θ` than a battle contest — a one-realm gap (25 `Θ`) would read
56% instead of ~100%. The fix expresses the difference through the ruleset's own linear read,
`BaseDodge(ThetaActor) − BaseDodge(ThetaContent)` (= 26·ΔΘ): no new constant, no new scale, parity stays at 500‰
(the +220 hit offset is deliberately **not** used — a persuade at parity is an even contest, not a 90% hit), and a
`Θ` gap is worth exactly what it is worth in battle. `BaseDodge` returns `int`; the difference is taken `checked` in
`long` (Numeric types). A narrative-only scale key would be the "new scale"
ideal §7 rules out; if a later balance pass needs narrative contests to be steeper or flatter than accuracy, that is
a new `stats.v{n+1}` key published through the tuning tool, decided then.

### 5. Odds and prices — one function for display and roll

```csharp
public sealed record ChoiceOdds(
    string Kind,                        // "certain" | "contest" | "coin" | "draw" | "battle"
    long SuccessMilli,                  // per-mille, 0..1000; 1000 for certain
    IReadOnlyList<(int OutcomeIndex, long WeightMilli)> Draw);   // for "draw": each outcome's share

public sealed record ChoicePrice(string Stock, long Amount);      // offer:{stock} only

public sealed record ChoiceView(int Slot, string ChoiceKind, string? Param, bool Eligible, string? RefusalId,
    ChoiceOdds Odds, ChoicePrice? Price);

public static class ChoiceResolver
{
    public static IReadOnlyList<ChoiceView> Present(StoryletOffer offer, EventRow row, ChoiceContext ctx);
    public static ChoiceResolution Resolve(StoryletOffer offer, EventRow row, int slot, ChoiceContext ctx);
}
```

`Present` and `Resolve` call the same private `OddsFor(choice, ctx)`; a test asserts that over many seeds the
observed success rate of `Resolve` converges to `Present`'s `SuccessMilli` and, more strictly, that the threshold
`Resolve` compares against **is** `Present`'s value (read back from the resolution).

**Prices.** `offer:souls` is `OfferPricing.Souls(costPerPull, ThetaContent, offerSoulsMilliOfPullPrice, power)`
(`OfferPricing.cs:32`), the same `P(Θ)` price the Delve's wild-talk offer pays, with the same two inputs from
`creature` and `dungeon` tuning — no narrative price key. Every other stock is **unpriced** in v1 and the choice is
ineligible with `choice.offer-unpriced`: `offer:supply` inherits the Delve's `PriceUndesigned` gap
(`OfferPricing.cs:56`; `DelvePrices.cs:17`, the item program's derived base price), and no other stock has a
narrative spend path yet. A narrative seed that uses such a stock is valid content that plays the day its price
lands, without a change here. The price is placed into the cast's `{cost}` binding for `narrative-text`.

### 6. Fights — a handoff, never a resolution

A `fight` choice yields a `FightHandoff`; the host turns it into its own mode's battle, which is the only place the
battle resolves:

```csharp
public abstract record FightHandoff
{
    /// World hosts: a guard fight at the host slot, by a player legion standing in the sector.
    /// Reuses BattleKinds.Guard (BattleSeam.cs:15) — "a deliberate attack on a slot's guard" — no new kind.
    public sealed record WorldGuard(string SectorId, int SlotIndex, string AttackerEntityId, string GuardWaveId) : FightHandoff;

    /// Delve hosts: the Delve's own encounter build for the room (party-dungeon's path; the Delve decides).
    public sealed record DelveEncounter(string RoomId, string EncounterRef) : FightHandoff;

    /// Hosts with no board of their own: a planned web-match battle, like an expedition's (§6 below).
    public sealed record PlannedMatch(string WaveId, ulong BattleSeed) : FightHandoff;
}
```

- **World**: the fight is a `BattleRequest` of kind `Guard` built by `world-events-host` and resolved by the
  `IBattleResolver` the turn already holds (`TurnEngine.Step`'s `resolver` parameter,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157-163`). Eligible only when a player legion stands in the sector —
  a guard fight needs an attacker entity (`BattleSeam.cs:52`).
- **Delve**: the Delve's own encounter path (Owner ruling 2026-09-19 (round 3): its live wiring is now `delve-live-rooms`', formerly party-dungeon's).
- **Expedition and homeworld**: no `fight` in v1 — an expedition's lead is selected and auto-answered at dispatch and
  sealed, then revealed at collect (`expedition-lead-host` §2; ticks themselves resolve at collect), and the homeworld is safe ground (`spec-host-content-theta.md` §3). A storylet that
  declares `fight` for those hosts fails preflight (`choice.fight-host-has-no-battle`, added to
  `EventDeckPreflight.Run` with this module).

The battle engine's §5 questions for this module: it adds **no** battle responsibility (1); it **decides** only
*that* a fight happens, the engine resolves it (2); it is a loop, not a mechanism (3); it extends `BattleRequest`
and the existing guard fight (4); every mode that has a board gets it (5); the handoff is plain seeded data (6).

### 7. Output and the ledger fact

```csharp
public sealed record ChoiceResolution(
    string OfferRef, int Slot, string ChoiceKind, int? OutcomeIndex, string? Ordinal,
    ChoiceOdds Odds, long RolledMilli, ChoicePrice? Price, FightHandoff? Fight,
    StoryletOutcome? Outcome);          // null for leave
```

**World hosts answer by command, not by this service** (Audit 2026-09-19; DESIGN-GATE §1 World map row: a world
choice is a command admitted through `WorldCommandAdmission` and resolved at End Turn). For `world.*` and
`world.petition`, the player files `event.choose`; `world-events-host`'s `Events` phase resolves it with this module's
arithmetic — `ChoiceResolver.ResolveFromViews(views, slot, stream)`, the same private `OddsFor` threshold and roll
compare as `Resolve`, fed the `ChoiceView`s precomputed into the persisted story input and a stream derived from the
world seed (`WorldSeed.DeriveRollSeed`) — and `choice.picked` is appended by the Settle pass. One resolver, two
entry points; never a second roll implementation in the phase.

The Server adapter (`ChoiceAnswerService`, new) appends `choice.picked` with source ref `answer:{hostKind}:{slotKey}:{hostClock}`
(`spec-story-ledger.md` §3) and attrs `{slot, choiceKind, outcomeOrdinal}` (`spec-story-ledger.md` §2), **in the same
transaction** as `outcome-routing`'s writes. A second answer to the same offer finds the fact through its dedupe key
and returns the stored resolution (idempotent retry; the answer is never re-rolled). The resolution itself is
reconstructible: same seed, same stream, same Θ inputs — which is why `Θ_actor` and `Θ_content` are written into the
fact's attrs (`thetaActor`, `thetaContent`), an attribute addition filed on `story-ledger` (Contradictions 1).

### 8. Tuning

~~One key joins `narrative.v1.json`: `contest.flatShiftMilli`, "the Delve's `wild.talk.flatterMilli` value, read from
`dungeon.v1.json` at publish time … two files, one value, noted in both `_meta`".~~ Audit 2026-09-19: withdrawn. Two
tuning keys carrying one value by convention is a second source of truth for one number (DESIGN-GATE §2.15 S; they
drift the first time one file is republished). The stated intent — one coin that feels the same in every place — is
met by reading the **one** existing key, `wild.talk.flatterMilli`, through the `dungeon` tuning this module already
reads for `offer:souls` prices (§5). **No narrative tuning key is added by this module.** If a balance pass later wants
narrative shifts to differ from the Delve's flatter, that is a new key published then, with its own value.

## Data shapes

No table. The resolution lives in the `choice.picked` fact's attrs. Wire DTOs (`ChoiceView`, `ChoiceResolution`
projections) are `quest-log-contract`'s and `storylet-card`'s to shape; none carries a raw Θ to the player (odds and
prices only), matching the Delve quest DTO's *"no `Θ`, rung id or `PartyIndex`"* rule
(`gk-core/src/FusionRpg.Core/Delve/Quests/QuestDto.cs:3-8`).

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `ThetaActor`, `ThetaContent` | `int` | the composer's type (`spec-host-content-theta.md` Numeric types) |
| contest difference | `long`, `checked` (each `BaseDodge` widened before subtracting), then `double` for `Sigmoid` | `26·Θ` fits `int` below `Θ` ≈ 82.6M; the widened difference cannot overflow; the sigmoid takes `double` |
| probability | `double` in, `long` per-mille out (`Math.Round`, away from zero) | floating point is allowed; the roll and the display share the rounded per-mille |
| prices | `long` | `OfferPricing.Souls` returns `long`; soul magnitudes grow with `P(Θ)` |
| roll | `int` from `NextPerMille()`, widened to `long` for the compare | as `ExpeditionResolver` does (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:105-106`) |

## SOLID notes

- **S:** this module decides one choice; `outcome-routing` applies it; hosts own when to ask.
- **O:** a new choice kind is a `ChoiceKindCatalog` row (narrative-seed's registry) plus one eligibility arm and one
  resolution arm; nothing else changes.
- **L:** every host's answer goes through `Resolve`; the Delve's legacy verbs keep `DelveStoryletHost.Answer`'s exact
  contract.
- **I:** hosts implement a small `ChoiceContext` producer, not the resolver.
- **D:** depends on `IStoryletHost`, `FactReader`, `PowerIndexComposer`, `OfferPricing` — never on a place's store.
- No private curve, no second contest scale, no second price function, no battle resolution.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Choices/ChoiceResolver.cs','src/FusionRpg.Server/Narrative/ChoiceAnswerService.cs','tests/FusionRpg.Core.Tests/Narrative/Choices/ChoiceResolverTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Choices"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ChoiceAnswer"
python scripts\audit-overflow.py ; python scripts\audit-magic-numbers.py --domain narrative
```

## Structure

```
src/FusionRpg.Core/Narrative/Choices/ChoiceResolver.cs        (new: Present, Resolve, OddsFor)
src/FusionRpg.Core/Narrative/Choices/ChoiceContext.cs         (new: ChoiceContext, PartyMember, StoryletOffer)
src/FusionRpg.Core/Narrative/Choices/ChoiceResolution.cs      (new: ChoiceView, ChoiceOdds, ChoicePrice, FightHandoff)
src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs  (edited: choice.fight-host-has-no-battle)
src/FusionRpg.Server/Narrative/ChoiceAnswerService.cs         (new: offer lookup, idempotent answer, fact append)
tests/FusionRpg.Core.Tests/Narrative/Choices/ChoiceResolverTests.cs     (new)
tests/FusionRpg.Server.Tests/Narrative/ChoiceAnswerServiceTests.cs      (new; in-memory store)
```

## Testing strategy

All with the game closed, over a **fixture** corpus (`tests/fixtures/narrative/storylets/`, `spec-storylet-contract.md`
Structure), never the committed one.

- **Eligibility table:** one fixture choice per kind; each refusal id fires exactly for its missing precondition
  (no supply, no match, unpriced stock, unaffordable, no fight path); ineligible choices are present with a reason.
- **Odds equal roll:** for a contest choice, `Resolve(...).Odds.SuccessMilli == Present(...)[slot].Odds.SuccessMilli`
  and the roll compared against exactly that value; over 10,000 fixed seeds the success share is within a stated
  tolerance of it (a statistical property on a fixed seed list, deterministic).
- **Contest shape:** success probability is non-decreasing in `ThetaActor − ThetaContent` and equals 500 per-mille at
  a zero difference (`Sigmoid`'s midpoint) — a relation, not a pinned curve.
- **Same units as battle (Audit 2026-09-19):** for a fixture gap `d`, the narrative contest's argument equals the
  battle hit contest's argument at the same `d` minus the parity offset — i.e. `BaseDodge(a) − BaseDodge(c)` equals
  `(BaseAccuracy(a) − BaseDodge(c)) − (BaseAccuracy(c) − BaseDodge(c))` — a relation between two shipped functions,
  no pinned number.
- **World entry point:** `ResolveFromViews` over the same views, slot and stream yields the same `ChoiceResolution`
  as `Resolve` (one arithmetic).
- **Coin path:** a relation-only choice ignores Θ (same odds at any Θ pair).
- **Leave:** resolves to no outcome, writes one `choice.picked`, never a consequence.
- **Idempotent answer:** answering twice returns the identical resolution and leaves one fact (in-memory store).
- **Revision guard:** a live revision that moved after the offer refuses `choice.revision-moved`; an arc link resolves
  from its pin after the corpus moves (order-independent: pin written before or after the corpus bump gives the same
  resolution for that arc).
- **Determinism:** same seed, facts, corpus revision and Θ inputs → byte-equal `ChoiceResolution`; different slot →
  different stream name.
- **Fight is a handoff:** a `fight` choice returns a `FightHandoff` and no applied effect; for a world host with no
  legion in the sector the choice is ineligible.
- **Streams:** every stream name this module derives starts with the host's `StreamRoot` and a `:choice:` segment; a
  scan fails on any `battle:` or `dungeon:quest:` literal in `Narrative/Choices/`.
- **No Θ on the wire:** the projection types carry no Θ field (reflection test).

## Success criteria

1. Every choice kind resolves or refuses with a named reason on a fixture host. 2. Displayed odds are the rolled odds.
3. Contests read `Θ_actor − Θ_content` through `Sigmoid` with an existing scale; no new curve or scale.
4. `offer:souls` prices through `OfferPricing.Souls`; other stocks are ineligible until priced. 5. A fight is always a
handoff to an existing battle path. 6. One `choice.picked` per offer, replay-identical. (G3's choice half.)

## Boundaries

- **Always:** decide, never apply; show every choice with odds or a reason; one stream per purpose; resolve against
  the offered revision.
- **Ask first:** a new contest scale key; pricing a new stock; a `fight` on a host without a battle mode.
- **Never:** resolve damage or a battle; invent a price function; roll on a combat stream; hide the odds of a contest;
  a lose-lose outcome set (preflight refuses it).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `ChoiceResolver.Present` → `ChoiceView[]` | every host, `storylet-card` (FE, wave 6) |
| `ChoiceResolver.Resolve` → `ChoiceResolution` | `outcome-routing` |
| `FightHandoff` | `world-events-host` (guard fight), `delve-host` (encounter) |
| `ChoiceAnswerService.Answer(playerId, offerRef, slot)` | the non-world hosts' answer routes (Delve: `delve-live-rooms`' answer route calls it for widened rows — Owner ruling 2026-09-19 (round 3): formerly party-dungeon's D3.9; homeworld: `sanctum-hub-host`) |
| `ChoiceResolver.ResolveFromViews` | `world-events-host`'s `Events` phase (Audit 2026-09-19) |

## Contradictions found (report; not fixed here)

1. **`choice.picked` attributes.** `spec-story-ledger.md` §2 closes `choice.picked` attrs at `{slot, choiceKind,
   outcomeOrdinal}`. Replaying a contest needs the two Θ inputs and the rolled per-mille. Filed as an attribute
   addition (`thetaActor`, `thetaContent`, `rolledMilli`) on `story-ledger`; it is a reviewed change to a closed
   attribute set, not a new table.
2. **`storylet.seen` must carry the offer.** `spec-story-ledger.md` §2 closes `storylet.seen` attrs at `{repeatScope,
   scopeKey, delveId}`. An offer needs `slotKey`, `revision`, `pinKey` and the cast. Filed on `story-ledger` together
   with item 1 (the cast is `EntityRef`s, serialized canonically).
3. **Seed-side consequence list.** `spec-narrative-vocabulary.md` Contradictions 1 already reports that
   `battle.start` is missing from narrative-seed's list; `fight` choices depend on it. No new report.

## Open questions

None for the owner. The contest scale and the flat-coin value are decided by principle above.

## Design-gate checklist

```
[x] Subsystems: power (contests, prices), battle (handoff only), economy (prices; spend is outcome-routing's),
    narrative engine, story ledger.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map (full), ideal §0, §6.2, §6.9, §7, §11; DESIGN-GATE §1 Battle, Economy, Standalone rows,
    §2, §5; battle-engine-ssot.md §5; sibling specs storylet-contract, storylet-reseam, story-ledger, cast-resolver,
    host-content-theta, narrative-vocabulary; code: CombatProbability, CombatPolicies, ActorThetaSeam, TalkTree,
    OfferPricing, DelvePrices, SoulSinkPolicy, PowerIndexComposer, EventChoices, EventDeck.Answer, BattleSeam,
    TurnEngine.Step, ExpeditionResolver.
[x] decisions.md: Battle engine SSOT row (map :105-107) respected; no lock contradicted.
[x] Every claim cites file:line.
[x] Nothing tested-as-assumed: no golden claim is made (this module touches no golden path).
[x] No population pinned; tests use fixtures.
[x] No cache.
[x] Order: revision pin vs corpus bump tested both ways.
[x] Actor numbers: reads Θ_actor for a contest only; writes none.
[x] No parallel path: one resolver, one contest function, one price function, the existing battle seam.
[ ] Registry row: the stream-literal scan is local to Core.Tests; no enforcement-registry row proposed.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (Power, Battle, World map, Tunables, Economy rows), §2 (1, 2, 9,
12, 13, 14, 15), §3, §5; `ssot-power-scale.md` §2 (contests are differences of same-scale quantities), §4.6, §5;
`battle-engine-ssot.md` §5; `CombatProbability.cs`, `CombatPolicies.cs`, `BattleModels.cs:367-368`,
`ActorThetaSeam.cs`, `WorldSeed.cs`.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | HIGH | **Contest unit mismatch.** `AccuracyScale` is calibrated for accuracy points (26 per `Θ`); the draft divided a raw `Θ` difference by it, so every narrative contest was ~26× flatter per `Θ` than the battle contest it claimed to share — "no new scale" in name, a different curve in effect (PS-3's same-scale requirement, `ssot-power-scale.md` §2) | **Fixed** (§4): difference taken through `BattleRuleset.BaseDodge`, the ruleset's own linear read; relation test added |
| 2 | MEDIUM | World choices had no stated path: `ChoiceAnswerService` answers immediately in a transaction, but DESIGN-GATE's World map row requires a command resolved at End Turn; `world-events-host` then rolled with its own arithmetic — two roll implementations | **Fixed** (§7): world hosts use `event.choose`; the phase calls `ResolveFromViews` (same `OddsFor`) |
| 3 | MEDIUM | `contest.flatShiftMilli` duplicated `wild.talk.flatterMilli`'s value "by convention" in a second file — two SSOTs for one number | **Fixed** (§8): read the one existing key; no narrative key |
| 4 | LOW | §6 still said an expedition encounter "is resolved at dispatch" (reconciled in the ideal) | **Fixed** |
| 5 | LOW | Ideal line citations drifted | **Fixed**: cited by section |

Checked and holding: fights are handoffs (`BattleRequest`/`IIntentSource`, battle-engine §5 answered); rolls on named
streams; no `Θ` on the wire; prices through `OfferPricing.Souls` (`P(Θ)`); no cap; standalone.

**Registry row proposed** (shared file, not written): `ns-choice-stream-literal` → the `Narrative/Choices/` stream-literal
scan in `ChoiceResolverTests` (no `battle:`/`dungeon:quest:` stream in narrative choices). **Boundary ask:**
`src/FusionRpg.Core/Narrative/Choices/**` → `FusionRpg.Core.Tests` filter `Narrative.Choices`.
