# Spec: outcome-routing

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `outcome-routing`, row 15 of the [npc-story-events map](../npc-story-events-map.md) (`:220`), wave 3.
Depends on `choice-resolution` (what was decided), `quest-sources` (`quest.offer`), `relation-ledger`
(`relation.shift`), `character-registry` (`recruit` of a cast character) and `scene-script-loader` (`scene.play`).
Consumed by every wave 4 host. Gate **G3** (`npc-story-events-map.md:298`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Apply one resolved outcome, and only through paths that already exist. The existing consequence kinds (`none`,
`loot`, `encounter`, `scout`) and effects keep their paths; the six new consequence kinds each route to one owner:

| Consequence | Routes to |
|---|---|
| `quest.offer` | `quest-sources` (`QuestLifecycle.Offer`) |
| `relation.shift` | a relation fact in the story ledger (`relation-ledger` derives the band) |
| `story.flag` | a `flag.set` fact in the story ledger |
| `battle.start` | the host's battle path: `BattleRequest` / `IIntentSource` into an existing mode |
| `scene.play` | a due-scene flag `scene-script-loader` reads |
| `recruit` | `RecruitMint` for an unnamed wild creature, or `TransferCharacterToRoster` for a cast character |

**Every payout is drawn from the host's own budget** with a dedupe key from a durable fact id — never on top of it.
Success looks like: G3's "every outcome kind routes through its existing path, rewards draw from the host budget with
a dedupe key, and the pick is in the story ledger" holds with the game closed, and a replayed answer changes nothing.

## Locked anchors

- **The only legal outcome paths** (ideal §6.9, `npc-story-events-ideal.md`): resources through the stock's
  existing grant/spend API with a dedupe key; magnitudes through `P(Θ_content)` and the loot pipeline; timed boons
  through an atom container at an `OwnerScope` or a registered `IActorStatSubsystem`; fights through `BattleRequest`
  or `IIntentSource`; rolls on named streams; numbers in tuning; joins through `RecruitMint` / ownership transfer.
- **Host budgets** (ideal §11 item 1, `:674`; map principle 8, `:97-100`). `offer:{stock}` choices are sinks on the
  same ledger.
- **Grant APIs with dedupe**: `AwardSouls(playerId, delta, reason, dedupeKey)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:215`),
  `TrySpendSouls(playerId, amount, reason, correlationId)` (`:234`, *"a replayed … correlationId that previously
  succeeded returns the original success without spending again"*, `:229-231`).
- **Loot through one pipeline**: `LootCorrelation.Derive` (`gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs:135-161`)
  over known source kinds (`gk-core/src/FusionRpg.Core/Items/Drops/DropTableValidator.cs:58-59`).
- **The Delve applies an outcome to its party** through `EventOutcomeDispatch.Dispatch`
  (`gk-core/src/FusionRpg.Core/Delve/Events/EventOutcomeDispatch.cs:113`), moved to the Delve adapter by `storylet-reseam`
  (`spec-storylet-reseam.md` §1).
- **Recruit**: `RecruitMint.Build(ConcreteSpecies, traitIds, origin, thetaEnemy)`
  (`gk-core/src/FusionRpg.Core/Delve/Wild/RecruitMint.cs:39`); cast characters join by ownership transfer
  (`spec-character-registry.md` §4).
- **One ActorHub compose** (map principle 9, `:101-104`; DESIGN-GATE §1 Actor-layer row): no module here decides an
  actor number.
- **No new stock** (map principle 8; `docs/architecture/empire-resource-ssot.md` §4 rule 1).

## Design

### 1. The router

```csharp
namespace FusionRpg.Core.Narrative.Outcomes;

/// One consequence, planned as data. Core builds the plan; the Server executes it in one transaction.
public abstract record OutcomeStep
{
    public sealed record AppendFact(StoryFactAppend Fact) : OutcomeStep;                    // relation.shift, story.flag, scene.play
    public sealed record OfferQuest(QuestRow Quest, int Need, string HostRef) : OutcomeStep; // quest.offer
    public sealed record RollLoot(LootSourceRow Source, string CorrelationId, QuestRewardWindow? Window) : OutcomeStep;
    public sealed record SpendSouls(long Amount, string Reason, string CorrelationId) : OutcomeStep;   // offer:souls
    public sealed record AwardSouls(long Amount, string Reason, string DedupeKey) : OutcomeStep;       // host budget only (§3)
    public sealed record StartFight(FightHandoff Fight) : OutcomeStep;                                  // battle.start / fight
    public sealed record RecruitWild(CreatureMintSpec Spec, string DedupeKey) : OutcomeStep;
    public sealed record JoinCharacter(string CharacterId, string SourceRef) : OutcomeStep;
    public sealed record HostEffect(string HostKind, object Payload) : OutcomeStep;                    // existing per-host effect path (§4)
}

public static class OutcomeRouter
{
    /// Pure: resolution + offer + host budget -> ordered steps. Refuses rather than guessing.
    public static OutcomePlan Plan(ChoiceResolution resolution, StoryletOffer offer, EventRow row,
        IHostBudget budget, NarrativeTuning tuning);
}

public sealed record OutcomePlan(string AnswerSourceRef, IReadOnlyList<OutcomeStep> Steps);
```

`OutcomeRouter.Plan` is pure Core. `OutcomeExecutor` (Server, new) runs a plan's steps inside **one** store
transaction together with `choice-resolution`'s `choice.picked` fact, using the `…Unlocked` store variants
(`spec-story-ledger.md` §6, the `MintCreatureUnlocked` precedent). A step that refuses (unaffordable spend, a
character no longer present) rolls the whole answer back and returns the refusal: an answer lands whole or not at
all.

### 2. Consequence kinds → steps

Owner ruling 2026-09-19 (round 3): the router reads the outcome's one consequence object `{kind, ref, param}`
(`spec-storylet-contract.md` §1–§2, owned by `narrative-seed/spec-narrative-contract.md` §5) — `kind` picks the
arm, `ref` names the target, `param` the modifier. `consequenceRef` is retired.

| `consequence.kind` | Reads | Step | Dedupe / source ref |
|---|---|---|---|
| `none` | — | — | — |
| `loot` | — | `RollLoot` from the **host budget's** source (§3), the outcome's `dropBand` — Owner ruling 2026-09-20: on the Delve, the room's event roll; elsewhere a `reward.owed` fact that takes one existing roll of the host's budget line (§3) | P14 key `storylet:{answerRef}` (the owed fact's subject); the roll is minted under the budget line's own correlation (§3) — on the Delve, `LootCorrelation.Derive(kind, "{hostSourceId}:storylet:{answerRef}")` as today |
| `encounter`, `scout` | — | `HostEffect` — the Delve's existing paths (encounter build, scout reveal); other hosts do not declare them (preflight, §6) | the Delve's own |
| `relation.shift` | `ref` → subject (`role:<roleId>` resolved through the cast to `character:{id}`, or `character:<id>` directly); `param` → the fact kind | `AppendFact` of kind **`param`** (`met`, `helped`, `refused`, `betrayed` or `spared`) about that subject | `answer:{…}` (`spec-story-ledger.md` §3) + subject |
| `story.flag` | `ref` (`flag:<flagId>`) | `AppendFact` `flag.set`, subject = `ref`, in the storylet's scope | same |
| `quest.offer` | `ref` (`quest:<questId>`) | `OfferQuest` → `QuestLifecycle.Offer` with the anchor `ref` names (`spec-quest-sources.md` §4) | same |
| `battle.start` | — | `StartFight` with the `FightHandoff` from `choice-resolution` §6 | the battle id (world) / encounter ref (Delve) |
| `scene.play` | `ref` (`scene:<sceneId>`) | `AppendFact` `flag.set`, subject `flag:scene.due.{sceneId}` (§5) | same |
| `recruit` | `ref` | `JoinCharacter` when `ref` is a `role:` cast as a character; `RecruitWild` when `ref` is `host:wild` | `recruit:{answerRef}` |
| `doctrine.setback` (Audit 2026-09-19; added by `counter-doctrine` §5) | — | **no executor step**: it changes hashed world state, so it is applied inside the world `Events` phase at resolution (`spec-world-events-host.md` §4); the plan records it as already applied so a replay of the Settle pass never re-applies it; legal on `world.*` hosts only (preflight) | the battle id / offer ref of the resolving turn |

**No ordinal → fact mapping.** Owner ruling 2026-09-19 (round 3): the relation fact kind is the seed's `param`,
never inferred from the outcome's ordinal (the former `good → helped`, `bad → refused` rule is withdrawn). A
validator keeps the contract honest at load: `storylet.consequence-param` (`spec-storylet-contract.md` §5) refuses
a `relation.shift` whose `param` is absent or `none`, and `OutcomeRouter.Plan` repeats the check and refuses
(`outcome.relation-param-missing`) rather than guessing, so a row that slipped past preflight still cannot write a
fact of an invented kind.

`relation.shift` writes a **fact**, never a band: the band is derived (`spec-relation-ledger.md` §2). A shift about an
**enemy-role** subject is refused here (`outcome.enemy-relation`), mirroring `character-registry`'s ledger guard (R13
rule 3, `spec-character-registry.md` §5) at the planning step so the refusal names the storylet.

**Effects** (`effects[]` by atom family and power band): the Delve keeps `EventOutcomeDispatch` for its party
(status, resource delta, stat-derived grants). On other hosts an outcome with effects must name a legal carrier —
an atom container at an `OwnerScope` (`gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20`) of kind `WorldBuff` or
`Consumable` (`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:31-38`) — and it is a `HostEffect` the host applies
through that container path. The effect's magnitude is the atom's own `P(Θ_content)` scaling; nothing here computes
one. A world storylet whose effect targets actors therefore contributes through the container the actor layer already
reads, and this spec answers the five actor-layer questions for it (DESIGN-GATE §1): **layer** — the existing
container layer, no new one; **scope** — the container's `OwnerScope`, one of the kinds `OwnerKind` already has
(`Player`, `Sector` or `Slot`, `OwnerScope.cs:20-30`; Audit 2026-09-19: the draft said "world or faction", neither of
which is an `OwnerKind` — a faction-wide scope would be a new actor-layer scope and is an Ask first); **lifetime** — the
container's timed window; **carrier** — an atom container; **SourceId** — `narrative:{storyletId}:{answerRef}`
(GG-49 provenance). No `IActorStatSubsystem` is added.

### 3. Host budgets — "out of, never on top of"

```csharp
public interface IHostBudget
{
    string HostKind { get; }
    /// The loot source this host already pays from, if it has one. Null: this host pays no loot.
    /// Owner ruling 2026-09-20: a narrative payout takes one of this budget line's existing rolls (below), never adds one.
    LootSourceRow? LootSource(string answerRef);
    /// Soul award headroom this host already grants for this answer (0 when the host has no soul budget).
    long SoulAwardBudget(string answerRef);
    /// Stocks an offer:{stock} choice may spend at this host.
    IReadOnlyList<string> SpendableStocks { get; }
}
```

**Owner ruling 2026-09-20 — rewards come out of the host budget.** A narrative reward (a storylet `loot` outcome,
a narrative quest's reward, a petition's or an expedition lead's reward) is **taken out of what the place already
pays — never an extra roll on top**. Total income is unchanged; the story reshapes it. Each host names its budget
line and the deduction rule:

| Host | Budget line (what the place already pays) | Deduction rule | Souls |
|---|---|---|---|
| Delve rooms; Delve quests | the room's own `dungeon-room` source and `souls_unbanked` — today's event path; a Delve quest's `dungeon-quest` window on the table the delve already rolls (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestReward.cs:7-19`) | unchanged: a storylet **is** the room's event, paid as today | the Delve's own event soul path, unchanged |
| World slots, petitions, world quests | the claim loot rolls a committed End Turn already makes in that world — one per `claim.loot:<tableId>` report line (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:128-133`), each a roll of that sector's `world-sector` table (`gk-core/src/FusionRpg.Core/Items/Drops/WorldSectorLootSource.cs:32`) | each owed world payout **takes one unused claim line** of the settling turn in the same world: it is minted under **that line's** loot correlation, with the payout's own window (`dropBand` or `rewardBand`), so the claim's mint of the same line replays and pays nothing (Owner ruling 2026-09-20 (round 5): the lines and their mint are `world-claim-loot`'s, `spec-world-claim-loot.md` §2, §6). A line is unused while the loot pipeline holds no manifest for its correlation. Payouts beyond the turn's lines wait, oldest `seq` first, for the next full-step turn with an unused line | **0** — the world pays no souls today, so a world storylet may not start |
| Expedition leads; expedition-offered and save (sanctum) quests | the collect's own `expedition-tier` roll(s) (`gk-data/packs/fusion/data/seed/loot/tables.v1.json` `drop.exp.*`; correlation `loot:exp:{sourceId}`, `gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs:138`) | a lead adds nothing: the tick's sealed manifest **is** its payout. A quest reward takes one of a collect's own tier rolls, by the same take-a-line rule; waiting rewards ride the save's next collect, oldest first | **0** |
| Homeworld | none | conversations pay nothing; a save quest one offers is paid through the collect line above | **0** |

- **The owed queue.** Deciding a payout appends one `reward.owed` fact (a new `StoryFactKind`, reviewed,
  `spec-narrative-vocabulary.md` §3): subject = the payout's own P14 key (`storylet:{answerRef}` for a `loot` outcome,
  `quest:{questSubject}` for a quest reward), attrs `{budgetLine, sourceKind, window}`, deduped on that key. Taking a
  line mints the roll and appends `reward.paid` (subject = the same key, attrs `{lineCorrelation}`) in **one**
  transaction; the queue is `reward.owed` without `reward.paid`. A replayed settlement finds the `reward.paid` fact and
  the line's manifest and pays nothing twice. The P14 dedupe keys are unchanged; what changed is which correlation the
  roll is minted under.
- **Pairing order** is deterministic: owed payouts by `seq`, lines by report entry index (world) or roll order
  (collect). The narrative settle pass runs **before** the claim-loot mint in the same post-commit order, inside the
  world's write lock, so a line is never both paid by a claim and taken by a payout.
- ~~**Today's budget is honest, not guessed.** No production code mints the world's `claim.loot:` lines yet … the
  world budget line is empty until world-map-program's claim-loot mint lands (filed there …).~~ Owner ruling
  2026-09-20 (round 5): **R17 — the claim-loot mint is this program's module `world-claim-loot`**
  (`spec-world-claim-loot.md`), built before `world-events-host` and `petition-host`. It turns the inert seam on
  (`ClaimResolver` writes `claim.loot:` lines only when `powerTuning` is passed, `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:124-135`,
  and `CommitWorldTurn` passes none today, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`) and mints every
  unused line through the one loot pipeline, once per sector per world. A world payout **takes** a line through that
  module's `MintClaimLootLineUnlocked` with its own window (`spec-world-claim-loot.md` §6) — the same roll path the
  claim uses, so there is one roller and the roll count equals the line count. The owed queue stays: a payout waits
  only when the settling turn has no unused line.
- **Ideal §11 item 1 holds for every host.** The earlier text of this section called world and quest loot a
  "bounded faucet" on top of the claim roll and deferred the economy call; the owner's ruling closes it — no host
  adds a roll, so no new faucet exists and no new sink is needed.

The homeworld and expedition leads pay nothing **directly**. A `quest.offer` they make is paid on completion by
taking a collect line (above), not by adding one.

**Consequence:** a `loot` outcome on the homeworld or an expedition lead is a **preflight refusal**
(`storylet.host-has-no-loot-budget`, added to `EventDeckPreflight.Run` with this module), so content cannot promise
what the host cannot pay. `AwardSouls` appears in the step vocabulary only for hosts whose `SoulAwardBudget` is
positive — today none outside the Delve's own path — so a narrative soul faucet cannot be written by accident.

**Sinks on the same ledger.** `offer:souls` becomes `SpendSouls` with correlation `offer:{answerRef}`, through
`TrySpendSouls`; a retry returns the original spend. This is a soul **sink** (P1 is satisfied trivially: a sink adds
no inflation).

### 4. Fights

`StartFight` is executed by the host, not here: the plan carries the handoff, the host's commit path turns it into
its mode's battle (world: a `Guard` `BattleRequest` resolved in the turn, `world-events-host`; Delve: the Delve's
encounter). The outcome's **other** steps are split at planning time into `beforeFight` (none today) and
`onWin`/`onLoss` lists; `onWin` runs only when the battle mode reports a win for the player's side — the rest of the
outcome is conditional on the fight, never assumed. The battle result is read from the battle mode's own durable
report (world turn log, Delve battle record), so the conditional steps run in that host's next commit, deduped by the
battle id.

### 5. Scenes

`scene.play` appends `flag.set` with subject `flag:scene.due.{sceneId}`. `scene-script-loader` owns eligibility: a
data-driven scene is due when that flag exists and no `scene.acknowledged` fact for the scene's revision does
(`spec-story-ledger.md` §1, the acknowledgement mirror). Routing never plays a scene and never plays one mid-match:
the homeworld plays it on entry (`sanctum-hub-host`), which is the only place `StorySceneHost` is triggered today
(`gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx:86-98`). The frozen `rift-prologue`/`1` row is never written
here.

### 6. Preflight rules added with this module

Joined to `EventDeckPreflight.Run` (`spec-storylet-contract.md` §5), evaluated per host the storylet declares:

| Rule id | Refuses |
|---|---|
| `storylet.host-has-no-loot-budget` | a `loot` outcome on a host whose `IHostBudget.LootSource` is null |
| `storylet.host-effect-unsupported` | `encounter`/`scout` outside Delve hosts |
| `storylet.enemy-relation-shift` | a `relation.shift` whose `consequence.ref` role requires an enemy-side role, or names an enemy-role character (R13 rule 3) |
| `storylet.recruit-target` | a `recruit` whose `consequence.ref` is neither a declared role nor `host:wild` |

### 7. Idempotency and replay

Every step's key derives from the answer's source ref (`answer:{hostKind}:{slotKey}:{hostClock}`), which is unique per
offer. Re-executing a plan is a no-op per step: facts dedupe (`spec-story-ledger.md` §3), soul spends return the
original result, loot correlations are unique (`LootCorrelation.Derive`), the character transfer refuses a second
time and is checked first. The plan itself is a pure function of `(resolution, offer, row, budget, tuning)`, so a
replay rebuilds the same steps.

## Data shapes

No table: every durable effect lands in an existing store (story ledger, soul ledger, loot manifests, creature rows,
battle logs). The plan is transient.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| soul amounts | `long` | the soul ledger's type; `AwardSouls` guards headroom and throws (`RpgStore.Souls.cs:205-212`) |
| loot content level | `int` Θ | `LootSourceRow`'s `ContentLevel`, as `QuestReward` builds it (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestReward.cs:61`) |
| band steps | none here | a relation outcome writes a fact; the step count is `relation-ledger`'s tuning |

## SOLID notes

- **S:** one router maps consequence kinds to owners; each owner keeps its own write path.
- **O:** a new consequence kind is a registry row (narrative-seed) plus one mapping arm and its preflight rule.
- **L:** every host executes the same plan shape; the Delve's party application keeps its exact contract.
- **I:** a host implements `IHostBudget` (three members), not the router.
- **D:** the router depends on `IHostBudget` and step records; the executor on store APIs.
- No new grant path, no new stock, no new loot source kind, no actor-number decision.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Outcomes/OutcomeRouter.cs','src/FusionRpg.Server/Narrative/OutcomeExecutor.cs','tests/FusionRpg.Core.Tests/Narrative/Outcomes/OutcomeRouterTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Outcomes"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~OutcomeExecutor"
python gk-core/scripts/guard-actor-hub.py ; python gk-core/scripts/guard-dal.py
python tools\tuning\resource_ownership.py --check
```

## Structure

```
src/FusionRpg.Core/Narrative/Outcomes/OutcomeStep.cs          (new)
src/FusionRpg.Core/Narrative/Outcomes/OutcomeRouter.cs        (new: Plan)
src/FusionRpg.Core/Narrative/Outcomes/IHostBudget.cs          (new)
src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs  (edited: §6 rules)
src/FusionRpg.Server/Narrative/OutcomeExecutor.cs             (new: one transaction per answer)
tests/FusionRpg.Core.Tests/Narrative/Outcomes/OutcomeRouterTests.cs     (new)
tests/FusionRpg.Server.Tests/Narrative/OutcomeExecutorTests.cs          (new; in-memory store)
```

## Testing strategy

With the game closed; stores in memory.

- **One path per kind:** for each consequence kind a fixture outcome plans exactly the step named in §2, and the
  executor calls exactly that owner (a spy store records the call list).
- **Budget refusals:** a `loot` outcome on the homeworld and on an expedition lead fails preflight with
  `storylet.host-has-no-loot-budget`; no world or homeworld plan contains `AwardSouls`.
- **Out of, never on top of (Owner ruling 2026-09-20):** a fixture world turn with two `claim.loot:` lines and three
  owed payouts mints exactly two rolls (both under the lines' correlations, with the payouts' windows) and leaves the
  third owed; the claim mint of that turn mints nothing; the next turn with a line pays the third; the item-roll
  count across the fixture equals the claim-line count exactly. The same holds for collects. Replaying either
  settlement mints nothing.
- **Dedupe:** executing the same plan twice leaves one fact, one soul spend, one loot manifest, one transfer.
- **All or nothing:** an unaffordable spend inside a plan with a flag and a quest rolls back all three.
- **Relation writes a fact, not a band:** after `relation.shift`, no row other than a story fact is written.
- **Enemy guard:** a `relation.shift` about an enemy-role subject refuses at planning and at preflight.
- **Fact kind from `param`:** a `relation.shift` with `param: betrayed` on a `good` outcome writes one `betrayed`
  fact (the ordinal is never read); `param: none` refuses at preflight and at `Plan` (Owner ruling 2026-09-19
  (round 3)).
- **Fight conditional:** an outcome with `battle.start` and loot runs the loot only after a fixture win report; a
  loss runs `onLoss` only; the order "report arrives, then commit" and "commit, then report" both settle once.
- **Scene due:** `scene.play` writes one `scene.due` flag and never touches `rpg_onboarding_story`.
- **Actor layer:** a world effect plans a container with a `narrative:`-prefixed SourceId; `guard-actor-hub.py`
  stays green (no new composer).

## Success criteria

1. Every consequence kind routes through one existing path. 2. Every payout comes from the host's own budget, with a
dedupe key from a durable id; hosts without a budget cannot be promised one (preflight). 3. An answer lands whole or
not at all, and a replay changes nothing. 4. No new stock, grant path, loot source kind or actor composer. (G3.)

## Boundaries

- **Always:** plan in Core, execute in one transaction; dedupe every step; read battle results from the mode's record.
- **Ask first:** a soul budget for a non-Delve host (a new faucet needs its sink named, P1); an actor effect that is
  not an existing container kind.
- **Never:** write a band or a number for a relation; resolve a battle; add a grant path or a stock; play a scene
  mid-match; edit the Rift prologue row.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `OutcomeRouter.Plan` → `OutcomePlan` | every host |
| `IHostBudget` | implemented by `delve-host`, `world-events-host`, `petition-host`, `expedition-lead-host`, `sanctum-hub-host` (Owner ruling 2026-09-20 (round 5): the world implementations read their lines from `world-claim-loot`) |
| `OutcomeExecutor.Execute(playerId, plan)` | the hosts' answer paths (with `ChoiceAnswerService`) |
| `scene.due.{sceneId}` flags | `scene-script-loader`, `sanctum-hub-host`, `spine-progress` |

## Contradictions found (report; not fixed here)

1. **"Rewards from the host budget" versus `loot` on every host.** Ideal §11 item 1 (`npc-story-events-ideal.md`)
   says *"an expedition lead from the expedition's rewards"*; the expedition manifest is sealed at resolution and has
   no loot table of its own (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:28-38`). This spec reads "the
   expedition's rewards" as the tick's existing manifest entry and refuses a `loot` outcome on the expedition host
   rather than adding a roll. narrative-seed's planner must not emit `loot` outcomes for `expedition.return` (filed).
2. **Relation fact per ordinal — RESOLVED.** `spec-relation-ledger.md` §2 derives bands from five fact kinds, and the
   seed contract used to carry only an ordinal. Owner ruling 2026-09-19 (round 3): the consequence object's `param`
   carries the fact kind (`narrative-seed/spec-narrative-contract.md` §5, `spec-storylet-vocab.md` §3.5); the
   ordinal → fact mapping is withdrawn (§2) and the proposed `consequenceParam` is not needed.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: economy (souls, loot faucets and sinks), actor layer (containers only), battle (handoff), creatures
    (recruit, transfer), quests, story ledger, scenes.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map (full); ideal §6.2, §6.9, §11; DESIGN-GATE §1 Economy, Battle, Actor-layer rows, §2, §5;
    empire-resource-ssot.md §3-§4; economy-principles.md P1; sibling specs storylet-contract, story-ledger,
    relation-ledger, character-registry, cast-resolver, host-content-theta; code: RpgStore.Souls, LootPipeline,
    DropTableValidator, WorldSectorLootSource, ClaimResolver, EventOutcomeDispatch, RecruitMint, OwnerScope,
    ContainerRow, ExpeditionResolver, SanctumStage.
[x] Every claim cites file:line.
[x] No constraint assumed.
[x] No population pinned.
[x] No cache.
[x] Order independence: fight report vs commit tested both ways.
[x] Actor numbers: effects go through the existing container layer with a SourceId; the five questions answered (§2).
[x] No parallel path: every step is an existing owner's API.
[ ] Registry row: the preflight rules are covered by EventDeckPreflight tests; no enforcement-registry row proposed.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (Economy, Actor-layer, Battle, Stats rows), §2 (3, 9, 12, 15),
§3, §5; `economy-principles.md` P1, P2, P13, P14; `empire-resource-ssot.md` §3-§4; ideal §6.9 and §11 item 1; R13;
round-3 consequence `{kind, ref, param}`.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | HIGH | **World loot was mis-described as "the host's own budget".** The claim rolls a sector's table once; each world storylet answer rolls it again — an on-top faucet, contrary to ideal §11 item 1's "out of, never on top of" | **Resolved — Owner ruling 2026-09-20:** rewards come out of the host budget; §3 names each host's budget line and the take-a-line deduction rule with its `reward.owed`/`reward.paid` queue; no roll is added |
| 2 | MEDIUM | Actor-layer answer named scope "world or faction"; `OwnerKind` has neither (`OwnerScope.cs:20-30`: Match, Plant, Zombie, Entity, Player, Sector, Slot, UniqueActor). A faction scope would be a new actor-layer scope — the DESIGN-GATE Actor-layer row's closed vocabulary | **Fixed** (§2): `Player`/`Sector`/`Slot`; a faction scope is Ask first |
| 3 | MEDIUM | `doctrine.setback` (counter-doctrine) was a consequence kind with no routing row; the executor would have had no arm and the phase-vs-settle split was unstated | **Fixed** (§2 row): applied in the world phase, recorded, never re-applied |
| 4 | MEDIUM | Homeworld/expedition "pay nothing" read as absolute, while quests they offer pay on completion through `quest-sources` §6 | **Fixed** (§3). Owner ruling 2026-09-20: those quests take a collect's existing roll; no faucet |
| 5 | LOW | `ContainerRow.cs:31` cited for `WorldBuff`, which is at `:38` | **Fixed** (`:31-38`) |

Checked and holding: one consequence object `{kind, ref, param}`, no ordinal → fact mapping; relation shifts write facts,
never bands; `outcome.enemy-relation` and `storylet.enemy-relation-shift` enforce R13 rule 3; soul faucets impossible
outside the Delve; every step dedupes on a durable answer ref (P14); fights are handoffs.

**Registry row proposed** (shared file, not written): `ns-outcome-host-budget` → `EventDeckPreflightTests`
(`storylet.host-has-no-loot-budget`) and `OutcomeRouterTests` (no `AwardSouls` step outside the Delve).

## Cross-lane alignment (2026-09-20)

- Owner ruling 2026-09-20 — **rewards come out of the host budget.** §3 now names each host's budget line (Delve
  loot/soul budget, the world turn's claim loot lines, the expedition collect's tier rolls, none for the homeworld)
  and one deduction rule: a narrative payout takes an existing roll and is minted under that roll's correlation with
  its own window; payouts beyond the budget wait in a `reward.owed` queue. The "bounded faucet" wording and the
  deferred economy decision (audit #1, #4) are closed. P14 keys are unchanged. ~~Filed on world-map-program: the
  claim-loot mint (no production reader of `claim.loot:` lines exists today) runs after the narrative settle pass.~~
  Owner ruling 2026-09-20 (round 5): the claim-loot mint is this program's prerequisite module `world-claim-loot`
  (R17, `spec-world-claim-loot.md`); it still runs after the narrative settle pass, and the world-map side records
  the transfer of `sector-loot-wiring` Part A in its own change.
- Alignment 2026-09-20: `doctrine.setback` is now a row of the seed's consequence vocabulary
  (`narrative-seed/spec-storylet-vocab.md` §3.5), so the §2 routing row has a seed-side source.
