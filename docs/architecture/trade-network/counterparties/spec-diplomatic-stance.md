# Spec: `diplomatic-stance`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `diplomatic-stance`, row 6 of the
[counterparties map](../counterparties-map.md) (wave 2; depends on `diplomacy-facts`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §7.6 (transit rights), §7.7 (*"`war.declared`
voids treaties and embargoes both ways"*; embargo *"automatic at war"*). **Owner decision Q1
(2026-09-19):** the dominant enemy empire starts at war with the player and never makes peace or a treaty
with the player, so its capital stays the win condition; rival empires and clans start at peace, with no
treaty, at band `wary`. Session record: `tasks/sessions/trade-network-idea-20260919.json`.
**Reconciled with the round-4 owner decisions 2026-09-19** ([../decisions-round-4.md](../decisions-round-4.md)):
**Q4** — the dominant enemy empire never makes peace **with the player only**; it may treat with rivals and
clans (closes this spec's former open question 1); **B** — *"Diplomacy: Embassy → Consulate. T1 treaties
with an empire; T2 blocs and embargo leverage (clans need no embassy)"* (§9 below).
**Round 5 (2026-09-20)**, R5-A/R5-X: **C2** — only the side making the offer needs an Embassy (map CQ1
answered (a), this spec's default); **C3** — a **deliberate** embargo needs a Consulate, war embargoes stay
automatic (§6, §9); **X1** — `DiplomacyGate.TierOf` delegates to `sector-features` `FactionTier`; **X14** —
the passage seam receives the logged band snapshot (§3, unchanged); **X16** — the Embassy row's role is
`Enable` (`empire-seed`'s row, no new role).

## Objective

Give the world a **peace state**. Today every faction is permanently hostile to every other
(`ZoneOfControl.cs:15-16`), so no treaty, no transit right and no war declaration can mean anything. This
module derives **war or peace per faction pair** from `diplomacy-facts`, makes `ZoneOfControl.IsHostile`
a read of that stance so every hostility consumer changes together, closes a peaceful faction's borders
to legions that hold no passage right, and adds the three commands that change a stance.

Success looks like: the player's legion and a clan's garrison share a road without a battle; a rival's
border stops the player's march until the player declares war or holds a passage treaty; the player can
never make peace with the dominant enemy empire; a world stamped before this module plays byte for byte
as today.

## Scope and non-goals

**In scope:** the stance derivation and its defaults; the hostility rule and every consumer of it; the
three places that compare faction ids directly where they mean hostility; closed borders at peace with a
passage seam; the commands `war-declare`, `peace-offer`, `peace-accept`; the path-cache trigger; the
capability flag; **the diplomacy building gate** (`DiplomacyGate` over the `diplomacy` sector feature, round 4).

**Non-goals:** treaty kinds, access levels, tariffs, embargo commands (`exchange`); which treaties a war
voids is **derived** by `exchange` `trade-access` from the facts this module writes; relation bands
(`relation-facts`); AI decisions to declare war or accept peace (`trade-ai` `ai-treaty-policy`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| **The one hostility rule, and it is total:** hostile iff the two faction ids differ | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16` |
| Its six direct call sites: lane and sector contact, the held-against test, believed supply, threat, the Finish rule | `gk-core/src/FusionRpg.Core/World/Movement/ContactResolver.cs:94`, `:120`; `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:37`; `gk-core/src/FusionRpg.Core/World/Ai/BelievedSupply.cs:64`; `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:71`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:235` |
| The held-against test's four callers: claims, the march's stop-on-entry, supply routing, the besieged test | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:82`; `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:126`; `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:31`, `:86` |
| A march halts on entering a hostile-held sector; a legion that starts surrounded may still leave | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:123-130` |
| The believed march graph takes an `include` set, so a policy can exclude ground it may not enter | `gk-core/src/FusionRpg.Core/World/Ai/MarchGraph.cs:33-35` |
| Commands are a closed list; admission rejects unknown kinds; one per-kind admission arm each | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:121-126`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-19`, `:48-193` |
| Commands are stored as a JSON payload, so a new optional field needs no column | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:21-30` |
| New-kind no-bump precedent: a phase no existing log can populate needs no ruleset bump | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:134-141` (the `Assaults` phase note; re-cited by the 2026-09-20 audit — `:117-123` is the version-6 **bump** note, the opposite precedent) |

### Wiring gap

None — the rule already sits behind one call, written so that *"alliances change one line instead of
every caller"* (`ZoneOfControl.cs:12-14`).

### Real gap — including three sites the one rule does not reach

A peace state; closed borders; the commands. And three places that compare owner ids **directly** where
the meaning is hostility, so they would ignore a peace:

| Site | What it does today | Under peace |
|---|---|---|
| `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs:66-70` | an assault on any sector the attacker does not own proceeds | refused, `assault.at-peace`, when the owner is at peace with the attacker |
| `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs:76-78` | the defender is any foreign force in the sector | the first force **hostile** to the attacker |
| `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:75-80` | any foreign force in the sector blocks `raise` (`raise.contested`) | only a hostile force blocks it (the held-against test) |

`ClaimResolver` refuses a claim only when hostile force stands in the sector or a guard is intact
(`ClaimResolver.cs:82-93`); an empty sector owned by anyone can be claimed. Under peace that would let a
legion annex a neighbour's empty ground, so a fourth refusal is added (§4).

## Design

### 1. The stance

```csharp
namespace FusionRpg.Core.World.Diplomacy;

public enum Stance { War, Peace }

public static class DiplomaticStance
{
    // Pure over (flags, facts, faction kinds). Two adapters: WorldState and IWorldView (diplomacy is public).
    public static Stance Of(WorldState world, string a, string b);
    public static Stance Of(IWorldView view, string a, string b);
    public static bool IsLockedWar(IReadOnlyList<WorldFaction> factions, string a, string b);
}
```

For `a != b`, in order:

1. **Legacy.** The stamp lacks `counterparties.stance` (wave 2's flag — §8) → `War` (today's rule, exactly).
2. **The wild** → `War`, always. The wild are terrain with teeth, not a party
   (`spec-ai-commander.md` §Who gets which policy); no command targets them.
3. **The locked pair** — the player and the dominant enemy empire → `War`, always (Q1; scope confirmed by
   round-4 Q4: *"never makes peace with the player only; it may treat with rivals and clans"*). Every other
   pair involving the dominant enemy empire follows rules 4–5 like any pair.
4. Otherwise the **latest** `war.declared` or `peace.made` fact for the pair decides.
5. No such fact → `Peace` (Q1: rivals and clans start at peace, with no treaty).

Rules 2, 3 and 5 are a structural table (`StanceDefaults`, a `const`-shaped rule with a comment): they
decide the win condition and who is a diplomatic party — changing them changes the game's design, not its
feel (tunables-ssot T2). The approved map's `diplomacy.defaultStance` key is therefore dropped; the map is
corrected.

The starting **band** of Q1 (`wary`) is not a stance and is not stored here: it is `npc-story-events`'
base band for the faction kind, read through `relation-facts`. Its current draft tuning gives `Rival` the
base `hostile` (`npc-story-events/spec-narrative-vocabulary.md` §4), which contradicts Q1 (contradiction
1 below).

### 2. One hostility rule, re-pointed

`ZoneOfControl.IsHostile(string, string)` is **replaced** (not overloaded — a two-argument form left
behind is a bypass) by:

```csharp
public static bool IsHostile(WorldState world, string a, string b) => DiplomaticStance.Of(world, a, b) == Stance.War;
public static bool IsHostile(IWorldView view,  string a, string b) => DiplomaticStance.Of(view,  a, b) == Stance.War;
```

Every direct caller already holds a world or a view, so each changes by one argument; `IsHeldAgainst`
passes its `world`. The three direct-comparison sites in the table above switch to `IsHostile` /
`IsHeldAgainst`. After this module, a source scan finds no owner-id inequality used as a hostility test
under `World/Movement`, `World/Turn` or `World/Growth` (the scan allows ownership checks — "is this
mine?" — which are not hostility).

### 3. Closed borders at peace

A legion may not **enter** a sector owned by a faction it is at peace with unless a passage rule grants
it (ideal §7.6: *"a route may cross another empire's ground only under a `passage` treaty"*).

```csharp
public interface IPassageRule { bool Grants(WorldState world, BandSnapshot bands, string grantor, string requester); }
```

*(Widened 2026-09-19 for `exchange` ask E-A17.)* Clan passage depends on the relation band (`exchange`
`trade-access` §4), and the band is not in `WorldState` — it is the logged step input `relation-facts` owns
(`spec-relation-facts.md` §3). So the seam receives the same `BandSnapshot` the step already carries; the
rule never reads the story ledger, and a legacy world passes an empty snapshot (every pair at its base
band). The belief-side twin receives the view's `BandWith` values the same way.

- Default registration: **no passage** (closed). `exchange` `trade-access` registers the real rule
  (`passage` or better). Absent `exchange`, peace means closed borders, which is exactly what logistics
  assumes (`logistics-flow-map.md` `path-cache`: *"absent, … foreign ground is closed"*).
- **Enforcement:** `MarchResolver` checks before committing a step into `towards`: a closed border halts
  the march in the current sector with `march.border-closed:<sectorId>`, the same halt shape as the
  zone-of-control stop (`MarchResolver.cs:123-130`). A legion already inside when a stance turns to peace
  is not expelled; it may leave, and may not claim (§4).
- **Belief side:** `MarchGraph.Of` receives an `include` set that omits sectors the viewer believes are
  owned by a faction it is at peace with and holds no passage from, so AI routes never plan through a
  closed border (`MarchGraph.cs:33-35`). Ownership comes from belief; the stance from public diplomacy.
- Unowned ground and one's own ground are always open.

### 4. Claims and assaults at peace

- `ClaimResolver`: after the contested check (`ClaimResolver.cs:82-86`), a claim on a sector owned by a
  faction at peace with the claimant drops `claim.at-peace`.
- `DistrictAssaultPhase`: an assault on a sector whose owner is at peace with the attacker drops
  `assault.at-peace`; the defender is the first **hostile** force.

### 5. The commands

`WorldCommand` gains one optional field, `TargetFactionId` (payload JSON, no column —
`RpgStore.WorldTurns.cs:21-30`), and `ImposedTreatyKindId` for a peace term. `exchange`'s treaty commands
reuse `TargetFactionId`; it is added once, here, because this module lands first.

| Kind | Fields | Admission refuses | Resolution (Snapshot, after claims, reveal order) |
|---|---|---|---|
| `war-declare` | `TargetFactionId` | flag absent; unknown/self/wild target; already at war (`diplomacy.already-at-war`); locked pair needs no declaration (`diplomacy.locked-war`) | appends `war.declared` |
| `peace-offer` | `TargetFactionId`, optional `ImposedTreatyKindId` | flag absent; not at war (`diplomacy.not-at-war`); locked pair (`diplomacy.locked-war`); target is an **empire** (dominant or `Rival`) and the commander holds no working Embassy (`diplomacy.no-embassy`, §9 — a clan target needs none); an imposed term while no treaty-kind registry is loaded (`peace.term-unavailable`) | appends `offer.made` (`OfferId = peace:<commander>:<turn>:<commandId>`) |
| `peace-accept` | `TargetFactionId`, `OfferId` | flag absent; locked pair | if the offer is open and addressed to the commander: appends `peace.made`, and `treaty.imposed` when the offer carried a term; else drops `peace.offer-closed` |

- **War dominates within a turn, whatever the filing order.** If a pair receives a `war-declare` and a
  `peace-accept` (or, later, an `exchange` treaty signing) in the same turn, the war fact is written and
  the other is dropped `diplomacy.superseded-by-war`. The outcome is therefore order-independent; the
  test files the pair both ways.
- A declined peace is not a command: an offer that is not accepted expires after
  `diplomacy.offerTtlTurns` (`diplomacy-facts`).
- **Effect from the next turn** (`diplomacy-facts` §3): the declaring turn's movement, contact and claims
  still see the old stance — a one-turn warning.

### 6. What war derives (never writes)

At war, for the pair: every treaty signed before the latest `war.declared` is void, and a mutual embargo
holds. Both are **derived** by `exchange` `trade-access` from the facts; this module writes only
`war.declared`. **This war embargo is automatic and needs no building** (round 5 C3): only a *deliberate*
embargo — an `exchange` `embargo-set` order (fact `embargo.set`) — needs a Consulate (§9).
The approved map said *"war.declared voids every treaty and embargo fact state … (derived,
not deleted)"* — this spec keeps it derived and names the reader.

### 7. The path-cache trigger

A turn whose Snapshot appends any `war.declared` or `peace.made` bumps `logistics-flow`'s graph version in
the same step (`logistics-flow-map.md` `path-cache` trigger T9, their ask A4). Until `logistics-flow`
lands, the bump is a no-op seam. It is a key-set edge for that cache (DESIGN-GATE §2.16): the set of
traversable sectors changes without any lane changing.

### 8. The stamp and the ruleset

**`counterparties.stance`** gates everything here (rule 1 of §1) — the flag of `counterparties` **wave 2**,
which this module shares with `relation-facts`, registered with that wave's single `RulesetVersion` bump
(round 6 C1; row 16 of [../landing-order.md](../landing-order.md) §2).

**Corrected by round 6 C1.** This section used to gate on wave 1's `counterparties.diplomacy` and to say
*"this module does not bump `RulesetVersion`"*. Both are withdrawn: a flag may not span waves (a world
stamped at wave 1 would have gained derived war/peace mid-life when wave 2 merged — the audit's C1), and
**a wave that grants a capability always takes its bump** (`../trade-foundation/spec-world-stamp.md` §2,
*"The bump is mandatory"*). The new-kind precedent (`TurnEngine.cs:134-141`) is about a *phase no old log can
populate*, not about skipping a capability's bump. A legacy world's outcomes still do not move, which is what
that precedent was cited for; the capability flag is still the gate.

### 9. The diplomacy building gate (round 4 B)

*"Buildings unlock features … Diplomacy: Embassy → Consulate — T1 treaties with an empire; T2 blocs and
embargo leverage (clans need no embassy)."* One structure row with two tier variants (Embassy T1, Consulate
T2), never two rows. The building is recognised by `StructureDef.Feature == SectorFeature.diplomacy` and its
tier by `SectorFeatures.TierFor(sector, factionId, SectorFeature.diplomacy)` — `trade-foundation`
`sector-features` (`../trade-foundation/spec-sector-features.md`; the feature's maximum tier is 2). The row
is `empire-seed`'s (map ask A15).

**No per-building kind, but the row loads as the neutral one (round 6 C2).** An earlier draft widened the
enum with `Embassy`, a second source for the fact `sector-features` owns, and that is still withdrawn (map
C19) — **nothing here gates on a kind.** What is corrected: *"no `StructureKind` member is added"* was read
as *"the row ships `structureKind: none"*, and a row with no kind **cannot load**
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`; `:330`), so no Embassy could ever be built and
`DiplomacyGate.TierOf` would return 0 forever — no treaty, ever (global audit C2). Every feature row now
loads as the neutral **`StructureKind.Feature`**, the `Obstacle` precedent
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`), with `StructureKind.Exchange` withdrawn and X1's
wording amended to allow that one kind (Round 6 C2).

**Round 6 S1 — whose Embassy it is.** The reads are `TierFor` and `FactionTier`, which apply *"it counts for
nobody until one faction owns both"* its sector and its slot, once, in `sector-features` §5a. An Embassy on a
contested slot buys no treaty for either side.

```csharp
public static class DiplomacyGate
{
    // = SectorFeatures.FactionTier(world, factionId, diplomacy) (round 5 X1 — a named wrapper, no second
    // building check): 0 none, 1 Embassy, 2 Consulate. Pure over WorldState / IWorldView.
    public static int TierOf(WorldState world, string factionId);
    public static int TierOf(IWorldView view, string factionId);
    public const int TreatiesTier = 1;   // structural: names the round-4 tier, not a balance number
    public const int BlocsEmbargoTier = 2;
}
```

| Act | Needs | Owner of the admission check |
|---|---|---|
| `peace-offer` to an empire | offerer `TierOf ≥ TreatiesTier` | this module (§5) |
| `peace-offer` to a clan; `war-declare`; `peace-accept` | nothing | — |
| Treaty offer or signing with an empire (`passage`, `market`, `preferential`) | offerer `TierOf ≥ TreatiesTier` | `exchange` `treaty-lifecycle` (map ask A16) |
| `bloc.joined` (founding or joining); a **deliberate** `embargo.set` (round 5 C3) | actor `TierOf ≥ BlocsEmbargoTier` (a Consulate) | `exchange` `treaty-lifecycle` (map ask A16) |
| The embargo that holds at war (§6) | nothing — automatic, derived from `war.declared` (round 5 C3) | `exchange` `trade-access` (derives it) |
| Anything with a clan | nothing (*"clans need no embassy"*) | — |

- **Why the offerer only** (map owner question CQ1 — **answered by the owner, round 5 C2: only the side
  making the offer**): requiring the building on both
  sides would let a faction that never builds one refuse every peace — a war nobody can end — and would make
  the AI's building order decide diplomacy. The offerer's Embassy is the unlock; acceptance is a response.
- `war-declare` needs no building: it is not a feature the register lists, and gating it would make a
  faction without an Embassy unable to answer an attack.
- Losing the Embassy (capture, destruction) does **not** void a signed treaty or a made peace — facts are
  append-only (`diplomacy-facts`); it only stops new acts at that tier. Stated so `trade-access` never
  re-derives access from a building.
- **Every empire runs the same gate** (principle 10): an AI empire needs its own Embassy to offer peace or a
  treaty to an empire; `trade-ai` builds it through the ordinary build path (map ask A17).

## Tunables

None new. `diplomacy.offerTtlTurns` is `diplomacy-facts`'. The map's `diplomacy.defaultStance` is
removed (structural, §1). The Embassy's build cost, turns, upgrade cost and upkeep are `empire-seed` bands;
`TreatiesTier`/`BlocsEmbargoTier` are structural (they name the owner's building table, not a feel).

## Numeric types

No magnitudes. Stance is an enum; turn arithmetic for offer expiry is `int`.

## Acceptance (contract)

1. **Legacy identity:** with the flag absent, `IsHostile(world, a, b) == (a != b)` for every pair, and the
   shipped scenarios replay byte-identically.
2. **Defaults (Q1):** with the flag and no facts, the player–dominant pair is `War`; every pair involving
   the wild is `War`; every other pair is `Peace`.
3. **Locked pair:** no command sequence produces `Peace` between the player and the dominant enemy
   empire; `peace-offer`/`peace-accept` for that pair are refused at admission.
4. **At peace, per consumer** (one test each): two legions on a lane or in a sector raise no contact
   battle; a sector holding a peaceful force is not held against its owner (supply routes through it,
   `raise` is not blocked); threat and believed supply ignore peaceful forces; the Finish rule is not
   blocked by a peaceful force; a claim on the peaceful owner's ground drops `claim.at-peace`; an assault
   on it drops `assault.at-peace`.
5. **At war:** every consumer behaves exactly as today.
6. **Borders:** a march into a peaceful faction's sector halts with `march.border-closed` when no passage
   is registered, and proceeds when a test passage rule grants it; a legion inside when peace is made may
   leave.
7. **Order-independent:** a war declaration and a peace acceptance for one pair in one turn produce
   `war.declared` and no `peace.made`, for both filing orders.
8. **Next-turn effect:** a declaration filed in turn N produces no contact battle in turn N and the
   ordinary battle in turn N + 1.
9. **Belief equals truth** for the stance (diplomacy is public).
10. **Trigger:** a turn that changes any pair's stance bumps the graph version (once `path-cache` exists).
11. **No bypass:** the two-argument `IsHostile` no longer exists; the source scan of §2 is green.
12. **Q4 scope:** the dominant enemy empire can reach `Peace` with a rival or a clan through the ordinary
    commands; only the player pair stays locked.
13. **Embassy gate:** a `peace-offer` to an empire is refused `diplomacy.no-embassy` without a working
    Embassy and admitted with one; a `peace-offer` to a clan and a `peace-accept` are never refused for a
    building; an AI empire is gated exactly like the player; capturing the offerer's Embassy after an offer
    was made does not void the resulting peace. **Order-independent:** building the Embassy and filing the
    offer in the same turn gives the same result in both filing orders (the gate reads the Embassy's
    state once, where the offer resolves in Snapshot, never the filing order).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Diplomacy/DiplomaticStanceTests.cs` (new): derivation, defaults,
  locked pair, commands, war-dominates, next-turn effect.
- Extend `ContactAndClearTests.cs`, `ClaimTests.cs`, `SupplyTests.cs`, `DistrictAssaultPhaseTests.cs`,
  `RaiseThreadingTests.cs`, `MovementTurnTests.cs` and `World/Ai/` threat/supply/rule tests with a
  peace-stamped case each (all under `gk-core/tests/FusionRpg.Core.Tests/World/`).
- A source-scan test for §2's "no owner inequality as hostility".
- Campaign scenarios (`TwoHearthsCampaignTests`, `TwoHearthsTenTurnProbeTests`, `WorldAiAcceptanceTests`)
  are run on legacy stamps and reported; a movement there is a defect, not a re-bless.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs','gk-core/src/FusionRpg.Core/World/Movement/ContactResolver.cs','gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs','gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs','gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs','gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs','gk-core/src/FusionRpg.Core/World/Ai/BelievedSupply.cs','gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs','gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs','gk-core/src/FusionRpg.Core/World/Ai/MarchGraph.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs','tests/FusionRpg.Core.Tests/World/Diplomacy/DiplomaticStanceTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldCommand|FullyQualifiedName~WorldTurn"
```

This touches every hostility consumer in the world engine: it is a boundary-crossing change within Core,
and the full suite runs once at module end.

## Hard edges

- **The hostility rule changes signature.** Every caller moves in the same commit; the build breaks
  otherwise, which is the point (no silent bypass).
- **Closed borders change AI behaviour** on trade-stamped worlds: a rival's expansion rule now stops at
  peaceful borders. Covered by the belief-side `include` set so the AI does not plan into a wall.
- **The win path.** On any trade-stamped template, a path from the player's homeworld to the dominant
  enemy empire's seat must cross no peaceful faction's ground (`empire-roster` acceptance 5), or peace
  would wall off the win condition.

## Dependencies

| Consumes | From |
|---|---|
| Fact list, append position, offer kinds | `diplomacy-facts` |
| The dominant-empire rule | `empire-roster` |
| Capability flag | `trade-foundation` `world-stamp` |
| Passage rule — a **seam `trade-access` registers into** (audit M1, edge 4: this was listed as a dependency, which reads as an upward edge; the direction is a registration, default closed until `exchange` lands at row 18) | `exchange` `trade-access` |
| Graph-version bump seam (optional) | `logistics-flow` `path-cache` |
| `SectorFeatures.TierFor(sector, faction, diplomacy)` / `FactionTier` and the placed tier (round 6 S1) | `trade-foundation` `sector-features` §5a |
| Embassy row with two tier variants | `empire-seed` `trade-structure-rows` (map ask A15) |

| Exposes | To |
|---|---|
| `DiplomaticStance.Of`, `IsLockedWar`, `IsHostile(world|view, …)` | every hostility consumer; `exchange` `trade-access` and `treaty-lifecycle` (locked pair refuses treaties with the player); `trade-ai`; `conquest-consequences` |
| `IPassageRule` seam | `exchange` `trade-access` |
| `DiplomacyGate.TierOf`, `TreatiesTier`, `BlocsEmbargoTier` | `exchange` `treaty-lifecycle` (A16); `trade-ai` `ai-treaty-policy` (A17); `trade-surface` `treaty-screen` |
| `TargetFactionId`, `ImposedTreatyKindId` on `WorldCommand` | `exchange` `treaty-lifecycle`, `trade-surface` `treaty-screen` |

## Contradictions found

1. **Q1 band versus the narrative tuning draft.** Q1 says rival empires start at band `wary`;
   `npc-story-events/spec-narrative-vocabulary.md` §4 drafts `baseBandByFactionKind` with `Rival:
   hostile`. That file is outside this fence; filed as ask A6 (set `Rival` to `wary`, keep `Zomboss`
   `hostile`). Until it lands, a rival's band reads `hostile` while its stance is `Peace`.
2. **The map counted "seven call sites"** for `IsHostile`. The code has six direct call sites (one inside
   `IsHeldAgainst`, which has four callers of its own) plus three owner-id comparisons that mean
   hostility. Corrected in the map.
3. **Q1's wording and treaties among AIs.** Q1 as recorded says the dominant enemy empire *"never makes
   peace or a treaty"*; the approved recommendation scoped that to the player (*"it may treat with
   rivals"*). **Resolved by round-4 Q4 (2026-09-19):** the player pair only; it may treat with rivals and
   clans. This spec already enforced exactly that.

## Open questions

None. Former question 1 was answered by round-4 Q4; the map's **CQ1** (does accepting also need an Embassy?)
was answered by round 5 **C2**: only the offerer (§9).

## Design-gate checklist

```
[x] Subsystems: world movement (contact, zone of control, march, claims), assaults, growth (raise),
    supply, world AI (threat, supply, rules, march graph), commands and admission.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus logistics-flow-map path-cache triggers,
    exchange-map modules 6 and 9, npc-story-events spec-relation-ledger and spec-narrative-vocabulary §3-§4;
    decisions-round-4.md in full (Q4, B).
[x] decisions.md: phase order (:7) — no phase added; Treaties row (:149) — access derived, respected.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: IsHostile body and every caller by grep; IsHeldAgainst callers; the three
    direct-comparison sites; MarchResolver halt; ClaimResolver refusals; MarchGraph include; command
    storage; the Assaults no-bump comment.
[x] Surrounding sections read (§7.6, §7.7 events; ZoneOfControl's own doc comment).
[x] Constraint not assumed: the no-bump reasoning rests on legacy identity, which is acceptance 1.
[x] §2 invariant 16: the path-cache key-set edge is named and has a test (acceptance 10).
[x] Corrections propagated to the map: call-site count, defaultStance removed, A6.
[x] No population pinned.
[x] Ordering: war-dominates makes same-turn filing order-independent; both orders tested.
[x] No actor magnitude.
[x] No SOLID-violating path: the one hostility rule re-pointed; the two-argument form removed.
[ ] Registry row: the "no owner inequality as hostility" scan is a local test; an enforcement-registry
    row is owed with the build.
```

## Audit 2026-09-20

Fixed here: the no-bump precedent was cited at `TurnEngine.cs:117-123`, which is the ruleset-6 **bump** note
(*"this bump exists only for the case a real order changes the outcome"*) — the opposite precedent; the
no-bump note for a brand-new command kind is `:134-141`. Checked in code: the six direct `IsHostile` callers
(`ContactResolver.cs:94`, `:120`; `ZoneOfControl.cs:37`; `BelievedSupply.cs:64`; `ThreatMap.cs:71`;
`FrontierRulesPolicy.cs:235`) match §Built; the three direct owner-id comparisons are real. Checked and clean:
one hostility rule re-pointed (the two-argument form is removed, so no bypass); war dominates within a turn in
both filing orders; the path-cache graph-version bump is named as the key-set edge (§2.16) with a test; the
Embassy gate reads `sector-features` only (X1); legacy identity is an acceptance test, not a claim.
**Verification boundary:** the `core-world-trade-counterparties` owner boundary (`spec-empire-goods-sinks.md`
*Audit 2026-09-20*) covers `World/Diplomacy/**`; the edits across `World/Movement`, `World/Turn`, `World/Growth`
and `World/Ai` stay on `core-fallback`, so this module runs the full suite once at its end (as §Test plan says).
