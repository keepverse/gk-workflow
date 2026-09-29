# Spec: `treaty-lifecycle`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 9 of the [exchange map](../exchange-map.md) (wave 3; approved
2026-09-19, including Q1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.7.
Decision: `docs/architecture/decisions.md` *Treaties, Diplomacy rail layer, flow lens*.
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

The diplomacy verbs, as ordinary world commands resolved deterministically at End Turn: propose a
treaty, answer it, end it, set or lift an embargo, found, join or leave a bloc. Their only output is
**facts** in `counterparties` `diplomacy-facts`; `trade-access` derives everything else from those facts.
This module never keeps a second list of active treaties.

**Round 4 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)) is binding here:** diplomacy
with an **empire** needs an **Embassy** (Diplomacy tier 1 — treaties); a **Consulate** (tier 2) is
needed for blocs and embargo leverage; clans need no embassy (§3a). The dominant enemy empire never
makes peace or a treaty **with the player only** (Q4, §8).

## Scope and non-goals

In scope: the command kinds; resolution rules; minimum term, `treaty.broken` and truce; the bloc
lifecycle; refusal reasons. Offers and every fact are rows in `counterparties` `diplomacy-facts`'
one list (`../counterparties/spec-diplomacy-facts.md` §2: `offer.made` / `offer.declined`); this module
keeps no offer store of its own.

Not in scope: war and peace commands (`counterparties` `diplomatic-stance`, which owns
`war-declare` / `peace-offer` / `peace-accept`); the fact list's storage (`diplomacy-facts`); band
movement from `treaty.broken` (`relation-facts`); deciding whether an AI signs (`trade-ai`
`ai-treaty-policy`); the walk order over the article kinds (`trade-ai` `counter-offer-articles`). The
article **kinds**, the deal shape and the refusal codes are `treaty-vocabulary` §6 (trade-ai TC4 / ask
T-A5 — corrected here: this text used to say `counter-offer-articles` owned the list, which would make
admission depend on `trade-ai`).

## Design

### 1. Command kinds — a reviewed widening

`treaty-propose`, `treaty-respond`, `treaty-end`, `embargo-set`, `embargo-lift`, `bloc-propose`,
`bloc-join`, `bloc-leave` join `WorldCommandKinds` (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:121-126`).
The ideal's command list (§8.7) named none of them (the map's EC4); cancel-an-order is `order-set` at
quantity 0, so no cancel kind exists. Payload fields on `WorldCommand`: `TargetFactionId` (the one
counterpart field, added by `counterparties` `diplomatic-stance` — its ask A9; this module adds no
second one), `TreatyKindId`, `OfferId`, `Response` (`accept` | `decline` | `counter`, closed), `Deal`
(a typed record in `treaty-vocabulary` §6's shape: `TariffMilli?`, `TermTurns?`, `Legs[]` of
`(GoodId, Qty, FromFactionId, ToFactionId)`, `SoulsTopUp?`, `LiftsEmbargo`, `Shape`, and the hub sector
the legs settle at, `LegHubSectorId?`), `RefusalTerms?` on `treaty-respond` (code, band, shortfall,
building, articles tried — ask T-A5), `BlocId`, `InviteeFactionIds`.

### 2. Where and when they resolve

In **Snapshot**, at the one append position `diplomacy-facts` defines — after the phase's resolvers
(`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:408-425`), through its only writer `DiplomacyLedger.Append`
— in reveal order (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:214-217`). So a fact written on
turn *t* takes effect in turn *t+1*'s `Logistics` phase and in every `Access` read after it — filing
order inside a turn can never change what trades this turn.

### 3. Offers

- `treaty-propose` appends an `offer.made` fact (kind, articles, `OfferId` derived from the command's
  `(CommanderId, CommandId)`, so replay rebuilds it). The offer is open while no fact answers its
  `OfferId` and it is younger than `diplomacy.offerTtlTurns` — expiry is derived, never written
  (`diplomacy-facts`' rule and key).
- **Articles need a field (ask E-A13).** The fact record carries `MinTermTurns` but no tariff
  (`counterparties/spec-diplomacy-facts.md` §1). `trade-access` needs a treaty's tariff article, and a
  bloc's external tariff; filed: a `TariffMilli?` field on `offer.made`, `treaty.signed`,
  `treaty.imposed` and the founding `bloc.joined`. Until it lands, every treaty charges its kind's
  default tariff (`treaty.{kind}.defaultTariffMilli`), which is a smaller article list, not a wrong one.
- `treaty-respond accept` on a live offer writes `treaty.signed` (kind, articles, minimum term, the
  offer id as the treaty id) **if, at resolution:** the pair is at peace (`diplomatic-stance`), the
  logged band reaches the kind's lowest band (`treaty-vocabulary`), and no other rule below refuses.
  `decline` appends `offer.declined`. `counter` closes it and opens a new offer from the responder, with
  articles from the same fixed list.
- Two offers crossing in one turn (A→B and B→A, same kind) are two offers; each resolves on its own
  answer. There is no automatic merge — it would make the result depend on which was filed first.

### 3a. Buildings and deal legs — round 4

**The Diplomacy ladder is `counterparties`'** (answering its ask A16): `DiplomacyGate` (`TierOf`,
`TreatiesTier = 1`, `BlocsEmbargoTier = 2`) lives in `counterparties` `diplomatic-stance` §9 and is a thin
wrapper over `trade-foundation` `sector-features` `FactionTier(world, faction, SectorFeature.diplomacy)`
(round 5 X1: *"every feature gate reads `sector-features`"*). The Embassy row is `empire-seed`'s, in the
existing **`Enable`** role (round 5 X16: *"no new role; the only role widening is `exchange`"*;
`empire-seed` `trade-structure-rows` §5.3). **Round 5 X10 drops `StructureKind.Embassy`** from this module:
no kind is read or required here (superseded: *"`StructureKind.Embassy` and `DiplomacyGate` … live in
`diplomatic-stance` §9"*). This module reads the gate at its own admission sites and adds **no second
building check**:

| Command | Needs | Refusal |
|---|---|---|
| `treaty-propose` to an empire counterpart (any kind) | the **offerer's** `DiplomacyGate.TierOf ≥ TreatiesTier` (an Embassy; accepting needs nothing — **round 5 C2 (owner): *"only the side making the offer"***; was counterparties CQ1, default (a)) | `treaty.no-embassy` |
| the same to a `Clan` | nothing (clans need no embassy) | — |
| `bloc-propose`, `bloc-join` | the actor's `TierOf ≥ BlocsEmbargoTier` (a Consulate) and `Hubs.TradeTier ≥ 3` (an Exchange) | `bloc.no-consulate`, `bloc.no-exchange` |
| `embargo-set` (a deliberate embargo) | the actor's `TierOf ≥ BlocsEmbargoTier` (the Consulate's "embargo leverage" — **round 5 C3 (owner): *"a deliberate embargo needs a Consulate; war embargoes stay automatic"***; was exchange-map OQ-3) | `embargo.no-consulate` |
| `preferential` kind, any counterpart | the offerer's `Hubs.TradeTier ≥ 3` (an Exchange); **this is a trade tier, `exchange`'s own**, not a diplomacy gate | `treaty.no-exchange` |

Checked **at admission**, on the committed state the command is filed against — the same site
`diplomatic-stance` uses for `peace-offer`. The automatic war embargo needs no building. **Losing an
Embassy or Consulate voids nothing:** facts are append-only and the gate governs acts, not treaties in
force (`counterparties` `diplomatic-stance` §9 (`DiplomacyGate`)); a `preferential` treaty whose parties lose their Exchange keeps existing but charges
its preferential tariff only at a tier-3 hub (`trade-access` §2a — a trade tier, applied per hub).

**Deal legs** (`treaty-vocabulary` §6; ask T-A5). A deal may carry goods legs and, from the player only,
a one-off soul top-up:

- **Where legs settle.** At one hub sector named in the deal (`LegHubSectorId`), owned by one of the
  two parties, at which the other party's `LevelAt ≥ market` (`trade-access` §2a). The receiving side's
  goods land in its located stock (hub owner) or consignment (the other party); the giving side's leave
  from the same. Settlement is `settlement-payment` §7 — one settlement module, never a second one.
- **One-off** legs settle in the `Logistics` phase of the turn after signing; **per-turn** legs settle
  every turn of the term, in the same pass.
- **Funding.** A deal settles as a unit at one **fulfilment ratio** — every leg delivers the same share
  of what it owes, set by the least-deliverable leg (`settlement-payment` §7, audit 2026-09-20) — so a
  party that cannot deliver its side never receives the other side in full (the accept-then-default
  exploit). The short party is recorded on `TurnResult` and, in the same turn's Snapshot, this module
  appends `treaty.broken` against it if the minimum term has not passed, else `treaty.ended`.
  Deterministic, explainable, and no debt is carried (no stored arrears).

### 3b. The trade-ai asks answered here

- **T-A5** — article kinds, deal shape and refusal terms: `treaty-vocabulary` §6 and the payload above.
- **T-A6** (offers half) — open offers addressed to or from a faction are derived from
  `diplomacy-facts`' `offer.*` rows and exposed read-only through `IWorldView` as
  `OwnOpenOffers()`; the projection reads public facts only, so it leaks no fog.

### 4. Legality — admission versus resolution

- **Admission** (`WorldCommandAdmission`, `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-40`):
  kind known; counterpart exists and is not the commander; treaty kind known; articles inside
  `treaty.{kind}.tariffBandMilli`; the stamp grants `trade.diplomacy` (which implies
  `counterparties.diplomacy` — global audit m11, Hard edges).
- **Building gates read `sector-features`, never a kind or an owner comparison (round 6 S1).** `DiplomacyGate`
  delegates to `FactionTier(world, faction, SectorFeature.diplomacy)` (round 5 X1/X10), and `sector-features`
  is where *"a building whose sector and slot have different owners counts for nobody until one faction owns
  both"* lives. An Embassy on a slot the offerer does not own, in a sector it does, gates nothing — and this
  module asserts only that it **reads** that answer.
- **Resolution** (Snapshot): the band check, peace, truce, bloc rules. **A change from the map:** the
  map put the band check at admission, but admission has no band — the band arrives as the logged
  snapshot at commit (cross-map decision CM1). The check runs at resolution and reports
  `treaty.band-too-low:{kind}:{lowestBand}`, the same explainable refusal a turn later in the pipe.

### 5. Ending, breaking, truce

- `treaty-end` at or after `signedTurn + minimumTermTurns` writes `treaty.ended`; before it writes
  `treaty.broken`. `relation-facts` then moves the breaker's band with the partner and, less, with
  every observer that holds a treaty with the breaker (ideal §7.7).
- After a `treaty.broken`, the breaker cannot propose any treaty to that partner for `truceTurns`
  (`treaty.truce:{turnsLeft}`).
- `war.declared` (written by `diplomatic-stance`) voids every treaty and embargo state for the pair as
  a **derived** effect in `trade-access` — no fact is rewritten.
- **War inside the minimum term also writes `treaty.broken` — owner decision Q-A (round 6, 2026-09-20).**
  *"It also writes `treaty.broken`, with the same observer effect as any early exit."* The audit's F-X2 found
  that declaring war voided treaties with no `treaty.broken`, so war was a **free exit** from a minimum term
  while `treaty-end` cost the breaker its bands. Applied here, because the treaty facts are this module's:

  | | Rule |
  |---|---|
  | When | In the **same Snapshot** that resolves `war-declare`, for **every** live treaty between the pair whose `signedTurn + minimumTermTurns` has not passed |
  | What | One `treaty.broken` per such treaty, breaker = the **declarer**, with the treaty kind and the turns remaining in the reason payload; at or after the minimum term, `treaty.ended` (the same split as `treaty-end`, §5 first bullet) |
  | Effect | Exactly the effect of any early exit: `relation-facts` moves the declarer's band with the partner and, less, with every observer holding a treaty with the declarer (ideal §7.7) — *"the same observer effect"*, one path, not a war-specific one |
  | Truce | The `truceTurns` bar applies as always (§5), which is coherent: a pair at war cannot propose anyway, and the bar outlives the war |
  | Order | Order-independent with `treaty-propose` in the same turn (acceptance 5, extended): war voids what is live at resolution; a treaty signed in the same Snapshot as the war declaration is broken by it, whichever command was filed first |
  | Not changed | The **voiding** stays derived in `trade-access` (no fact is rewritten); Q-A adds a *fact*, not a second void path. And `war.declared` is still `diplomatic-stance`'s to write — this module only appends the treaty facts it owns |

### 6. Embargo

`embargo-set` writes `embargo.set` (actor → target); `embargo-lift` writes `embargo.lifted`. One-sided,
any band (`treaty-vocabulary`); a deliberate `embargo-set` needs the actor's Consulate (§3a), lifting
needs nothing. War implies a mutual embargo (derived). A bloc member's embargo is the
bloc's, and the bloc's is every member's (below).

### 7. Blocs (multilateral, in v1)

- `bloc-propose` names a new `BlocId`, the invitees and the shared external tariff (an article). It
  opens one offer per invitee.
- `bloc-join` accepts: the bloc exists once the founder and one invitee have joined. At each join, the
  joiner's logged band with **every** current member must be `eager` (the kind's lowest band);
  otherwise `bloc.band-too-low:{member}`. The joiner and the founder need the §3a buildings (an
  Exchange, and a Consulate for an empire).
- **Members give up their own trade policy toward outsiders.** While a member, a faction cannot hold a
  bilateral `market` or `preferential` tariff toward a non-member that differs from the bloc's external
  tariff: such proposals are refused `bloc.external-tariff-bound`, and on joining, `trade-access`
  already charges outsiders the bloc tariff. Embargoes are shared: an `embargo-set` by any member binds
  the bloc.
- `bloc-leave` before the member's minimum term writes `treaty.broken` toward each remaining member;
  after it, `bloc.left`. A bloc with one member left dissolves (`bloc.left` for the last member).
- External tariff changes are not in v1: a bloc keeps its founding article (a new bloc is the change).

### 8. Imposed treaties and the win condition

- `treaty.imposed` is written by `diplomatic-stance` as a peace term (`diplomacy-facts` §2 table). This
  module reads it exactly like `treaty.signed` for kind `market`, with the same end and break rules.
- **The dominant enemy empire never treats with the player — the player only** (counterparties Q1,
  confirmed by round 4 Q4): any proposal, answer or imposition on the **locked pair** is refused
  `treaty.win-condition-party`. The pair is read from `counterparties` `diplomatic-stance`'s
  `DiplomaticStance.IsLockedWar` (one rule), not re-derived from the `Zomboss` faction kind
  (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:11`). It may treat with rivals and clans, subject to
  the same buildings as anyone (§3a).
- **Clans need no treaty for `passage` and `market`** (Q1); a `market` treaty with a clan is still
  allowed, because its tariff article can differ from the clan default. `preferential` and `bloc`
  with a clan require a treaty, as with anyone.

### 9. Numeric types

Turn counts are `int` (an index, like `CurrentTurn`); tariffs are bounded per-mille `long`. No
magnitude is computed here.

## Required amendment (not made in this session)

`docs/architecture/world/spec-ai-commander.md:284` (*"no diplomacy or inter-faction negotiation"*) is
amended for this program in the change that lands the first diplomacy command — filed by
`counterparties` as its ask A5; this module depends on it, it does not make it.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | One command shape, one admission gate, stable reveal order | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:129-150`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-40`; `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:214-217` |
| Built | Snapshot as the settle-at-end-of-turn phase | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:404-426` |
| Wiring gap | No peace state (`diplomatic-stance` adds it) | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:12-16` |
| Real gap | Every command, the offer record, every rule above | — |

## Tunables

`data/tuning/diplomacy.v{n}.json`: `treaty.minimumTermTurns` (per kind), `truceTurns`,
`treaty.{kind}.defaultTariffMilli` (the fallback until E-A13). `offerTtlTurns` is `diplomacy-facts`'. (`acceptMilli.{band}` is `trade-ai`'s; `treaty.{kind}.tariffBandMilli` is
`trade-access`'s.) Turn counts are pacing numbers a balance pass would change, so they are tunables.

## Acceptance (contract)

1. A treaty exists only if both parties' commands are in the log (or a peace pair imposed it); replaying
   the log rebuilds the fact list byte for byte.
2. Ending at or after the minimum term writes `treaty.ended`; before it, `treaty.broken`; a broken
   pair cannot propose again for `truceTurns`. **(Round 6 Q-A)** The same holds for `war-declare`: declaring
   war on a partner writes one `treaty.broken` per live treaty still inside its minimum term (breaker = the
   declarer) and `treaty.ended` for the rest, with the identical observer effect — a test asserts that an
   early `treaty-end` and a war declaration at the same turn produce the same band movements for partner and
   observers, so war is never the cheaper exit.
3. A proposal whose kind's lowest band the pair does not reach is refused at resolution with the band
   named; with a band that reaches it, the same proposal signs.
4. A bloc member cannot hold a bilateral tariff toward a non-member that differs from the bloc's
   external tariff; a join with any member below `eager` is refused naming that member.
5. **Order-independent:** a `treaty-propose` and a `war-declare` for the same pair filed in one turn
   produce the same facts whichever is filed first (both filing orders tested); two crossing offers
   resolve independently.
6. The player and the dominant enemy empire can never sign, be imposed, or hold any treaty; the
   dominant enemy empire and a rival or clan can (round 4 Q4), given the buildings.
7. Every refusal carries a reason naming the rule, band or article (explainable, ideal §7.7).
8. A world whose stamp lacks `trade.diplomacy` refuses every kind here; a legacy log replays
   byte-identically.
9. **Buildings (round 4):** each gate in §3a refuses at admission with its named reason when the
   offerer's (or actor's) building is absent and admits when present; accepting needs no building; a clan
   treaty needs no Embassy; the war embargo needs no building; losing an Embassy after signing changes no
   fact and no `Level`.
10. **Deal legs:** a one-off deal delivers once, a per-turn deal every turn of its term; a short deal
    settles every leg at the one fulfilment ratio and writes `treaty.broken` against the short party
    inside the minimum term (`treaty.ended` after it); a mixed-shape deal is refused at admission.
11. **No default gain (audit 2026-09-20):** over generated one-off deals where one party holds less than
    it promised, that party never receives more than its delivered share of the other side.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Diplomacy/Lifecycle/` (new), trait `core.world-diplomacy.lifecycle`,
  boundary row `core-world-diplomacy`; command-shape tests beside the turn-engine tests.
- Crosses Core, Contracts and Server (new payload fields on the submit DTO,
  `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:518`): the focused boundaries for those paths; the full suite
  once at the end of wave 3.

## Hard edges

- **Facts only.** No active-treaty list, no stored `Access`, no relation number.
- **No solver.** Counters come from the fixed article list (the "make it equitable" solver exploit,
  ideal §7.7).
- **One pipe.** Every diplomacy verb enters through `WorldCommandAdmission`.
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave**, so a
  stamped world's rules never change mid-life. This module is exchange **wave 3** and grants a player-facing
  feature (treaties, blocs, embargoes and now the war-break fact), so it rides **wave 3's single bump**, taken
  at landing, never pre-assigned, and its own flag row belongs to **wave 3**, not to `exchange-hub`'s wave-2
  `trade.exchange` registration ([../landing-order.md](../landing-order.md)). It never claims "no bump".
- **Two diplomacy flags, one implication (global audit m11).** `trade.diplomacy` (this module's gate, via
  `world-stamp`) and `counterparties.diplomacy` (`counterparties` `diplomacy-facts`') are separate rows, and
  nothing said how they relate. Stated once, here, because this module is the consumer of both:
  **`trade.diplomacy` ⇒ `counterparties.diplomacy`** — a stamp that grants the trade-diplomacy verbs must grant
  the fact substrate they write into, and `world-stamp` validates the implication at registration (a stamp with
  `trade.diplomacy` and without `counterparties.diplomacy` is a load rejection naming both). The reverse does
  not hold: relation facts exist on a world with no treaty verbs.
- **Q-A's fact is appended, never a second void path (round 6).** War still voids access derivedly in
  `trade-access`; §5 adds the `treaty.broken` fact only.

## Dependencies

- Upstream: `treaty-vocabulary`, `trade-access`; `counterparties` `diplomacy-facts` (append API, offer
  facts, E-A13), `diplomatic-stance` (peace, `treaty.imposed`, `IsLockedWar`, `TargetFactionId`),
  `relation-facts` (band snapshot), `diplomatic-stance` §9 (`DiplomacyGate`, over `sector-features`
  `FactionTier(diplomacy)` — round 5 X1/X10; no `StructureKind.Embassy`);
  `trade-foundation` `world-stamp` (`trade.diplomacy`); `exchange-hub` (`TradeTier`);
  `settlement-payment` §7 (deal legs).
- Downstream: `trade-ai` `ai-treaty-policy`, `trade-surface` treaty screen, `trade-stories`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| The eight command kinds and their payload | human client, `trade-ai` |
| Open treaty offers, derived from `offer.*` facts | `trade-surface`, `trade-ai` (offers to or from itself) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (commands, Snapshot), diplomacy, relation ladder.
[~] Session boundary: trade-network-idea-20260919; new file only; the check's exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: trade-network-ideal §7.7, §8.7; counterparties-map (whole: Q1, diplomacy-facts,
    diplomatic-stance, relation-facts, A5); trade-ai-map (modules 4, 6); decisions.md :149.
[x] decisions.md :149 implemented; :7 (phase order) — resolution sits in Snapshot, no new phase.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: Snapshot resolver sequence, reveal order, admission shape, faction kinds.
[x] Surrounding sections read (Snapshot's comment on why claims settle there).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: band check moved to resolution (stated here and in the map).
[x] No population count pinned.
[x] No event-refreshed cache (Access is derived; the path cache reads trade-access's per-pair
    PassageBit in its key — the digest was withdrawn by the 2026-09-20 audit).
[x] Orderings: same-turn war/treaty filing tested in both orders.
[x] No actor magnitude.
[x] No SOLID-violating path: one fact list, one pipe, no second treaty store.
[x] Registry row: the rules are enforced by their own tests; no scan-shaped rule is added.
[x] Round 4 reconciliation (2026-09-19): decisions-round-4.md read whole; Embassy/Consulate gates read
    from counterparties' DiplomacyGate at admission (its A16; offerer only per its CQ1 default), Exchange
    tier gate for preferential/bloc; Q4 read through IsLockedWar; TargetFactionId reused (counterparties A9);
    T-A5 answered (deal legs settle through settlement-payment §7); scope line on article ownership
    corrected (TC4).
[x] Round 5 (2026-09-20): C2 (offerer only) and C3 (deliberate embargo needs a Consulate) are the
    owner's decisions; X10 dropped StructureKind.Embassy; X1 DiplomacyGate delegates to sector-features
    FactionTier(diplomacy); X16 the Embassy row is Enable-role (trade-structure-rows §5.3).
[x] Audit 2026-09-20 (independent): deal legs settle at one fulfilment ratio (the accept-then-default
    exploit); acceptance renumbered 1-11; solver-exploit wording made generic.
[x] Round 6 (2026-09-20): Q-A answered by the owner — war inside a minimum term also writes treaty.broken,
    same observer effect (§5, acceptance 2); F-X2 closed. C1 — the wave and the one shared RulesetVersion
    bump named (Hard edges); m11 — trade.diplomacy implies counterparties.diplomacy, stated once (§4).
```
