# Spec: relation-ledger

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `relation-ledger`, row 5 of the [npc-story-events map](../npc-story-events-map.md) (`:211`), wave 1. Depends
on `story-ledger` (facts) and `narrative-vocabulary` (tuning, `StoryFactKind`). Consumed by `narrative-predicates`
(the relation-band leaf), `cast-resolver` (scoring), `choice-resolution`, `outcome-routing` (`relation.shift`,
`recruit`) and trade-network's `counterparties`. Draft decision row **NS2** (`npc-story-events-map.md:400`). Owner
ruling **R4** (`npc-story-events-ideal.md:656`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

One **derived** relation read model for characters and factions on the one 4-band disposition ladder
(`eager, open, wary, hostile`, `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`): a band computed from
append-only relation facts in the story ledger, with **no time term**, a story-gated top band, and the rule that a
band decides **whether** a character may join, never its starting loyalty (owner answer (a), Open questions). No
stored number, no spendable quantity.

Success looks like: replaying the same facts in any order yields the same band; advancing turns, rooms or collects
with no relation fact leaves every band unchanged; `eager` is unreachable until the character's own unlock flag
exists; trade-network reads the same band for a faction that a storylet reads for it.

## Locked anchors

- **One ladder** (R4; NS2; map locked assumption 5, `:145-147`). The ladder is the dungeon registry's
  `DispositionCatalog` (`gk-core/src/FusionRpg.Core/Dungeon/Registry/DispositionCatalog.cs:4-43`), `eager` = ordinal 0 by
  registry order (`gk-core/src/FusionRpg.Core/Delve/Wild/Disposition.cs:26-36`).
- **Derived, never stored** — the `LoyaltyRank` pattern: *"Derived from the number, never stored"*
  (`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:5-7`).
- **Facts, never time** (ideal §6.4, `npc-story-events-ideal.md:424-430`; map locked assumption 10, `:159`).
- **Access, not stats** (ideal §6.4, `:431-433`; map principle 9, `:101-104`).
- **After a join, the relation is `LoyaltyRank`**; there is never a second axis on one creature (ideal §6.4,
  `:418-420`).
- The ladder arithmetic already exists: `Disposition.Shift` sums signed steps, positive toward `hostile`, and
  clamps only the final sum to the registry's ends — a structural clamp on a closed ordinal
  (`Disposition.cs:38-56`).

## Design

### 1. One ladder arithmetic, shared with the Delve

`Disposition.Shift(baseId, rungShift, deltaBandShift, offerPreferenceShift, remembersShift, stanceShift)`
(`Disposition.cs:45-56`) is the Delve's five-input form. This module needs the same arithmetic with one net step.
To keep **one** ladder arithmetic, the pure core moves to a place-neutral helper and the Delve delegates:

```csharp
namespace FusionRpg.Core.Narrative.Relations;

public static class DispositionLadder
{
    /// Base ordinal plus a signed step count (positive toward hostile), clamped to the registry's ends.
    /// Structural clamp on a closed four-member ordinal, never a magnitude (Disposition.cs:51-54).
    public static string Step(string baseId, int netSteps);
    public static int OrdinalOf(string id);                 // moved from Disposition.OrdinalOf (Disposition.cs:29-36)
}
```

`Disposition.Shift` becomes `DispositionLadder.Step(baseId, rungShift + deltaBandShift + offerPreferenceShift +
remembersShift + stanceShift)`, byte-identical in behaviour; the existing wild-room tests prove it. The map gives
the ladder's derivation to this program (`npc-story-events-map.md:321`).

### 2. The derivation

For a subject `(kind ∈ {character, faction}, id)` in a scope:

```text
base     = tuning.relation.baseBandByRole[character.role]         (character)
         | tuning.relation.baseBandByFactionKind[faction.kind]    (faction; WorldFactionKind)
net      = Σ tuning.relation.shiftByFactKind[f.kind]  over relation facts f about the subject
band     = DispositionLadder.Step(base, net)
if tuning.relation.topBandStoryGated and band == eager and no unlock fact:
    band = open                                                     (Hades' locked heart, ideal §6.4)
```

- **Relation facts** are the five `StoryFactKind`s `met, helped, refused, betrayed, spared`
  (`spec-narrative-vocabulary.md` §3). Only those move a band. A `choice.picked`, a `storylet.seen` or an elapsed
  turn never does — the "facts, never time" rule is structural: the derivation has no clock input at all.
- **The unlock fact** is a `flag.set` fact with subject `flag:relation.unlock.{subjectKind}.{subjectId}`, written
  only by the subject's own storylet outcome (`story.flag`, routed by `outcome-routing`).
- **Order independence.** `net` is a sum and only the final value is clamped, the property `Disposition.Shift`
  already documents (`Disposition.cs:38-44`). Two facts in either order give the same band.
- **Faction kinds** come from `WorldFactionKind` (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7`: Player,
  Zomboss, Clan, Rival, Wild). A `Player` faction has no relation to itself; asking is an argument error.
- **Scope.** A character's facts live in the character's scope (save or world, `spec-character-registry.md`); a
  faction's in its world's scope. The read takes the scope from the subject, never from the caller.
- **World lifetime — Owner ruling 2026-09-19 (round 3).** A world-scoped subject's relation (a local character, a
  clan or rival faction) lives as long as its world exists under the approved world-continuity program — `active`,
  `hibernating` or `idle`, outcome `contested` or `won` (`world-continuity-map.md` locked assumption 1, module
  `world-state-vocabulary`). Hibernation changes nothing: the band is derived from facts with no clock input, so a
  world left for fifty End Turns returns with every band as it was, and world-continuity's pending turns
  (`hibernation-clock`) are not a relation input. **Owner ruling 2026-09-19 (round 4)** replaces "retires at fallen or
  abandoned": the view carries the subject's world `WorldNarrativePhase` (`spec-narrative-vocabulary.md` §3) —
  `Live` (active), `Dormant` (hibernating or idle: band intact, no host draws against it) or `Frozen` (fallen:
  read-only history, which the reserved `world-reclaim` may revive). Nothing is deleted and there is no "abandoned"
  state. A consumer decides what a non-`Live` phase means for it (trade-network's counterparties treat only `Live`
  as tradeable). Relation facts emitted by world-continuity's `CoarseStep` while the world is dormant (module
  `world-event-budget`) count like any other; no other writer may append them (`spec-story-ledger.md` §5).
- **Enemies.** The derivation applies to any subject, but R13 rule 3 (*"no enemy remembers you personally"*,
  `npc-story-events-ideal.md:556-559`) forbids an enemy's **lines** being picked from its own history; that rule is
  enforced where lines are chosen (`narrative-text`) and by `character-registry`'s enemy guards. A faction band for
  the antagonist's faction is faction-level memory, which rule 3 allows.

### 3. After a join

When `character-registry` records `character.joined`, the character's relation becomes its contract's
`LoyaltyRank`. `RelationLedger.For(subject)` returns `RelationView.Joined(instanceId)` from then on, and
`narrative-predicates`' relation-band leaf reads `joined` as "not on the ladder" (it evaluates false for every
band), so no storylet can address a roster creature through disposition.

**No conversion — Audit 2026-09-19, applying the owner's answer (a).** A join is an ordinary bind: the contracts
program's bind path (`BindContract`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:232`) starts the creature at
`ContractPolicy.BindLoyalty` (`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:84`), the rank any bind starts
at, which pays `+0‰` (`ContractPolicy.cs:57-62`). The band decides only **whether** a character may join:
`RelationLedger.CanJoin(view)` is true for `eager`, `open` and `wary` and false for `hostile` and for a view that is
already `Joined` — a structural access rule (relationships grant access, not stats; map principle 9), commented as
such, not a tunable. The earlier draft's `JoinStartingLoyalty`, `tuning.relation.joinRankByBand` and the filed ask
`ContractPolicy.FloorOf` are withdrawn: a key whose every value must equal the default is not a balance number, and
keeping it would let a tuning publish give a relationship an actor-number effect through `StarLoyaltySubsystem`
without the five actor-layer questions (DESIGN-GATE actor-layer row). This module touches no actor number.

### 4. Read API

```csharp
namespace FusionRpg.Core.Narrative.Relations;

public abstract record RelationView
{
    public sealed record Band(string DispositionId, bool TopGateOpen) : RelationView;
    public sealed record Joined(string InstanceId) : RelationView;
}

public sealed record RelationSubject(string Kind, string Id);      // "character" | "faction"

public static class RelationLedger
{
    /// Pure: folds the subject's relation facts (already read by the caller) into a view.
    public static RelationView Derive(RelationSubject subject, string baseBandId,
        IReadOnlyList<StoryFact> subjectFacts, NarrativeTuning tuning);

    /// Access, never stats: false for hostile and for an already-joined subject (owner answer (a)).
    public static bool CanJoin(RelationView view);
}

public sealed record RelationRead(RelationView View, WorldNarrativePhase Phase);   // Owner ruling 2026-09-19 (round 4)
```

The Server-side adapter `RelationReader` (new, `gk-core/src/FusionRpg.Server/Narrative/`) reads the subject's facts once
through `ListStoryFacts` and calls `Derive`. trade-network's `counterparties` reads a faction band through the same
adapter (`trade-network-ideal.md:315`, map `:147`); it never keeps its own scale (`npc-story-events-map.md:321-322`).
Owner ruling 2026-09-19 (round 4) (replacing round 3's `Retired` flag): `RelationReader` reads the subject's world
attention and outcome once per call and returns a `RelationRead` with the derived `WorldNarrativePhase` (§2 *World
lifetime*); a save-scoped subject is always `Live`.

### 5. No cache

The band is derived on every read from indexed facts (`ix_rpg_story_fact_subject`, `spec-story-ledger.md` §2). A
caller that needs many bands in one pulse builds a `RelationSnapshot` value from one query and discards it at the
end of the call — a value with a one-call lifetime, not a cache. If a later module adds a cache, DESIGN-GATE §2.16
requires its spec to list and test every trigger; the full set for a relation cache is: a relation fact appended
for the subject; the subject's unlock flag appended; a `character.joined`, `character.departed` or
`character.fell` fact (the **key-set edge**: the subject leaves or re-enters the ladder); a tuning publish (a host
restart); the active world changing (faction subjects are per world); and (Owner ruling 2026-09-19 (round 4)) the
subject's world changing `WorldNarrativePhase` — hibernate, wake, idle, fall, and a future `world-reclaim` revive —
which moves the set of subjects a host may read as live.

## Data shapes

No table: the band is derived. Tuning keys (`relation.*`) are declared in `spec-narrative-vocabulary.md` §4.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `net` steps | `int`, summed `checked` | each fact contributes a small signed step; the count of relation facts about one subject is bounded by play, and an overflow would throw rather than wrap |
| band ordinal | `int` | index into a four-member registry |
| starting loyalty | — | Audit 2026-09-19: none computed here; the bind path's `BindLoyalty` is the contracts program's number |

## SOLID notes

- **S:** one ladder, one arithmetic (`DispositionLadder`), one relation read model for characters and factions.
- **O:** a new relation fact kind is a vocabulary member and a tuning key; the fold is unchanged.
- **D:** trade-network, predicates and casting depend on `RelationLedger`/`RelationReader`, never on facts
  directly for a band.
- No second relation axis on a joined creature; no stored disposition number; no currency (map principle 8).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Relations/RelationLedger.cs','gk-core/src/FusionRpg.Core/Delve/Wild/Disposition.cs','tests/FusionRpg.Core.Tests/Narrative/Relations/RelationLedgerTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Relations|FullyQualifiedName~Delve.Wild"
```

## Structure

```
src/FusionRpg.Core/Narrative/Relations/DispositionLadder.cs      (new)
src/FusionRpg.Core/Narrative/Relations/RelationLedger.cs         (new)
gk-core/src/FusionRpg.Core/Delve/Wild/Disposition.cs                     (edited: Shift delegates to DispositionLadder)
src/FusionRpg.Server/Narrative/RelationReader.cs                 (new)
tests/FusionRpg.Core.Tests/Narrative/Relations/RelationLedgerTests.cs     (new)
```

## Testing strategy

- **Order independence:** for every permutation of a five-fact list (`met, helped, refused, betrayed, spared`),
  the band is identical — a property test over all 120 orders.
- **Facts only:** a subject with facts, read after zero and after 1,000 simulated host-clock ticks with no new
  fact, returns the same band (the derivation has no clock input; the test proves no hidden one).
- **Replay:** deleting nothing and re-deriving from the full fact list reproduces the band.
- **Gate:** enough `helped` facts to reach `eager` yield `open` until the unlock fact exists, then `eager`.
- **Clamp is structural:** ten `betrayed` facts end at `hostile`, not beyond; the final-sum clamp matches the
  Delve's (`Disposition.cs:51-54`).
- **Delve parity:** every existing `gk-core/tests/FusionRpg.Core.Tests/Delve/Wild/` test passes unchanged after
  `Disposition.Shift` delegates.
- **Joined:** after a `character.joined` fact, `Derive` returns `Joined`; `CanJoin` is false for it and for
  `hostile`, true for `eager`/`open`/`wary`. A contract test asserts no type in `FusionRpg.Core.Narrative` reads a
  `LoyaltyRank` threshold or writes a loyalty value (owner answer (a); Audit 2026-09-19).
- **Faction:** a `Player` subject throws; a `Clan` subject reads its base from tuning.
- **World lifecycle (Owner ruling 2026-09-19 (round 4)), one test per edge:** a clan's band read while its world is
  `active` (`Live`), after a fixture moves it to `hibernating` with pending turns and to `idle` (`Dormant`), on return
  (`Live`), and after a fixture `fallen` outcome (`Frozen`) is identical every time; only the phase changes; no fact is
  appended or deleted by any transition.

## Success criteria

1. One ladder arithmetic, used by the Delve and this module. 2. Bands are order-independent and time-free,
proven by the two property tests. 3. The top band is story-gated. 4. No stored band, no currency. 5.
trade-network reads bands through `RelationReader` only.

## Boundaries

- **Always:** derive from facts; one ladder; relation facts only.
- **Ask first:** any relation effect on an actor number (see Open questions); a fifth band.
- **Never:** a time term; a stored disposition; a spendable reputation; a second scale for trade-network.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `RelationLedger.Derive`, `RelationView`, `RelationSubject` | `narrative-predicates`, `cast-resolver`, `choice-resolution` |
| `RelationLedger.CanJoin` | `outcome-routing` (`recruit` of a cast character: eligibility only; the bind is the contracts program's) |
| `RelationReader.FactionBand(playerId, worldId, factionId)` | trade-network `counterparties` |
| `DispositionLadder` | party-dungeon's `Disposition.Shift` |

## Contradictions found (report; not fixed here)

1. **"Relationships grant access, not stats" versus a starting rank.** Map row 5 (`:211`) asks for *"the
   conversion of disposition into a starting `LoyaltyRank` on join"*. `LoyaltyRank` is not neutral: it feeds
   `ContractPolicy.RankBonusMilli` (`ContractPolicy.cs:107`), a per-mille bonus on the creature's own combat
   channels, contributed through the registered `StarLoyaltySubsystem`
   (`gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/StarLoyaltySubsystem.cs:55`). A friendlier join therefore
   starts with larger combat numbers than a colder one. The carrier is legitimate (a registered subsystem, the
   one-compose rule holds), but the effect is a relationship changing stats, which principle 9
   (`npc-story-events-map.md:101-104`) says is not the default. Raised as the open question below. *Resolved by the
   owner's answer (a); Audit 2026-09-19 removed the conversion (§3).*

## Open questions

> **Answered by the owner 2026-09-19: option (a).** Every join starts at the normal bind rank; friendship
> decides whether and on what terms a character joins, never its starting rank. `joinRankByBand` maps every
> band to the default rank. The question below is kept for the trail.

1. **Does a befriended character join at a higher loyalty rank than any other join?** A new contract row starts
   at loyalty 0 today (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:667`). Options:
   - **(a) Recommended:** every join starts where any bind starts; disposition decides *whether* the character
     joins and on what terms (price, which choices exist), never its starting rank. Principle 9 holds without
     exception; the map row's "starting `LoyaltyRank`" becomes "the rank any join starts at".
   - **(b)** The approved map wording: the band picks a higher starting rank (`joinRankByBand`), accepting that a
     friendship buys an earlier `StarLoyaltySubsystem` combat bonus.
   ~~Until the owner answers, the spec builds (a) with `joinRankByBand` mapping every band to the default bind
   rank, so choosing (b) later is a tuning publish, not a code change.~~ Audit 2026-09-19: withdrawn — (b) would be a
   relationship changing an actor number, which needs a new owner ruling and the five actor-layer questions, never a
   tuning publish; the key is gone (§3).

## Design-gate checklist

```
[x] Subsystems: relation ladder, contracts/loyalty (reader), actor layer (touched only through the open question),
    trade-network (consumer).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 5, NS2, R4; ideal §6.4; Disposition.cs, DispositionCatalog.cs, WildMemory.cs;
    ContractPolicy.cs (RankFor, RankBonusMilli); StarLoyaltySubsystem.cs:55; contract DDL.
[x] Every claim cites file:line.
[x] Actor numbers: the join conversion reaches an actor number only through the existing registered
    StarLoyaltySubsystem; named as an open question, not decided here.
[x] Cache: none; the full trigger set for any future cache is listed, including the key-set edge (join/depart/fall).
[x] Order independence stated and tested both ways (all permutations).
[x] No population pinned. No parallel ladder.
[ ] Registry row: none proposed. (Audit 2026-09-19: rows proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | The owner answered (a) — every join starts at the normal bind rank — yet the spec kept `JoinStartingLoyalty`, `joinRankByBand` (with non-default values in `spec-narrative-vocabulary.md` §4) and a `FloorOf` ask, and said choosing (b) "is a tuning publish". That leaves a relationship-to-actor-number path (`RankBonusMilli` via `StarLoyaltySubsystem`) switchable by tuning, against principle 9 and the actor-layer five questions | **Fixed:** conversion withdrawn; `CanJoin` (access only); joins use `BindLoyalty`; a contract test forbids loyalty reads/writes in Narrative |
| 2 | high | Round-4 owner ruling: "retires at fallen or abandoned" and a `Retired` flag; there is no abandoned state and nothing retires by deletion | **Fixed:** `RelationRead.Phase` (`Live/Dormant/Frozen`), per-edge tests |
| 3 | medium | The future-cache trigger list (§2.16) lacked the world-phase edge, which moves the set of subjects hosts may treat as live | **Fixed** |
| 4 | low | Map citations one line early (`:210`, `:399`, `:320`, `:320-321`) | **Fixed** |

Checked and clean: one ladder and one arithmetic (`DispositionLadder`, Delve delegates), derived never stored, no
time term (property test), order-independence over all 120 permutations, `int` band steps summed `checked`, no cache.
Verified: `ContractPolicy.cs` (`LoyaltyRank`, `BindLoyalty`, `RankFor`, `RankBonusMilli`), `WorldFactionKind`
(`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18`).

**Map propagation made:** map row 5 no longer says "the conversion of disposition into a starting `LoyaltyRank`".

**Proposed enforcement-registry rows:** `ns2-one-relation-ladder` — no second relation scale; guard: a Guard.Tests
scan for a disposition/reputation enum or ladder type outside `FusionRpg.Core.Narrative.Relations` and
`Dungeon/Registry` (new). `ns2-relations-access-not-stats` — no Narrative type reads a loyalty threshold or writes an
actor number; guard: the contract test above.
