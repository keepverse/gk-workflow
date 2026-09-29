# Spec: expedition-lead-host

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `expedition-lead-host`, row 20 of the [npc-story-events map](../npc-story-events-map.md) (`:225`), wave 4.
Depends on `outcome-routing` and `host-content-theta`. Gate **G4** expedition half (`npc-story-events-map.md:299`:
*"An expedition lead arrives in a collect summary with expedition tier hashes unchanged at encounter chance 0"*).
Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Let an idle expedition come home with a **lead**: a character met, a rumor, or a quest offer. An encounter chance per
expedition tick is rolled and the lead **selected and auto-answered at dispatch** and **sealed** (ticks themselves
resolve at collect from the seed sealed at dispatch — Audit 2026-09-19: the draft said "like every tick", which the
ideal has since corrected); at collect it is delivered as a **log line in the collect summary** plus the lead — never a
modal. The idle clock never blocks.

Success looks like: with the game closed, a fixture expedition with a non-zero encounter chance seals a lead at
dispatch and reveals it in `CollectResult`; the lead's character is the creature the tick met; the expedition's tick
outcomes, battle plans and rewards manifest — and therefore every expedition tier hash — are byte-identical at **any**
encounter chance, not only at 0; nothing about the collect waits on the player.

## Locked anchors

- **Expeditions** (ideal §6.6 Expeditions row, `npc-story-events-ideal.md`): *"The idle clock never blocks. An
  encounter resolves at dispatch like every tick and comes home as a lead … `WildCreatureMet` is the natural host.
  Delivery is a log line in the collect summary, never a modal"*; idle players skip text (ideal §4.4, `:258-261`).
  Reconciled 2026-09-19: the ideal row now reads "sealed at dispatch, revealed at collect", because ticks resolve at
  collect (`ExpeditionEndpoints.cs:109`); this spec's §2 design is unchanged.
- **Ticks**: six closed kinds (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:7-15`); each tick draws its own
  stream `SeededRng.DeriveStream(seed, "tick:" + t)` (`:106`); `WildCreatureMet` rolls a species, then join-or-essence
  (`:120-141`). Resolution is pure in `(tier, squad, seed, elapsedTicks)` and runs at collect from the seed sealed at
  dispatch (`:40-46`, `:61-67`; `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:12-17`, `:109`).
- **The dispatch record seals squad and seed** (`rpg_expeditions`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:743-755`);
  collect is exactly-once (`ExpeditionEndpoints.cs:12-17`) and its payload is deliverable once (`:205-208`).
- **The encounter chance lives in `expeditions.v{n}`** (map row 20, `:225`; ideal §7, `:602`), beside the tier
  `dangerBand` `host-content-theta` adds (`spec-host-content-theta.md` §4).
- **Rewards from the host's budget**: an expedition lead pays nothing beyond the tick's own manifest entry
  (`spec-outcome-routing.md` §3). Owner ruling 2026-09-20: every narrative reward comes **out of** what the place
  already pays, never an extra roll; the expedition's budget line is the collect's own `expedition-tier` roll(s), and
  a quest a lead offers is paid by taking one of a later collect's rolls, not by adding one
  (`spec-outcome-routing.md` §3).
- **One stream per purpose, never shared with a combat stream** (map principle 12, `:111-114`; ideal §4.1 Slay the
  Spire row, `:219`).

## Design

### 1. The encounter roll never touches a tick's stream

For every tick `t` of the tier's full timeline whose kind is `WildCreatureMet` or `Quiet`:

```text
encounterRoll_t = SeededRng.DeriveStream(seed, "narrative:expedition:encounter:" + t).NextPerMille()
encounter_t     = encounterRoll_t < encounterMilli[kind_t]
```

The stream name is new and disjoint from `"tick:" + t` and `"battle:" + i` (`ExpeditionResolver.cs:92`, `:106`), so
the resolver's tick outcomes, battle plans and manifest do not move at any chance. The expedition resolver is **not
edited**: this module reads its `ExpeditionResolution` and derives leads beside it. This is stronger than G4's
wording and is what the tier-hash test proves (§7).

Hosting on two tick kinds, each with its own chance:

| Tick kind | Lead it can carry | Why |
|---|---|---|
| `WildCreatureMet` | a **character met** (the tick's own creature becomes a cast character) or a quest offer from it | the natural host (ideal §6.6): the tick already rolled a species (`ExpeditionResolver.cs:120`) |
| `Quiet` | a **rumor** (`story.flag` / history fragment) or a quest offer | quiet ticks are 40% of ticks (`ExpeditionResolver.cs:49-52`); a rumor is texture that costs no reward |

### 2. Resolved at dispatch, sealed

At `DispatchAsync` (`ExpeditionEndpoints.cs:34`), after the store accepts the dispatch, the Server:

1. resolves the tier's **full** timeline with `ExpeditionResolver.Resolve(tier, squad, seed, tier.TickCount)` — pure,
   the same call collect makes (`:109`);
2. for each encounter tick, asks `storylet-selection` for host `expedition.return` with the tick's context (tick kind,
   the met species for `WildCreatureMet`, the squad as party), casts it (`cast-resolver`), and resolves its **one**
   automatic choice (§3) through `choice-resolution` on the stream `narrative:expedition:{expeditionId}:{t}`;
3. writes the sealed leads to `rpg_expeditions.leads_json` (new column, nullable) in the dispatch transaction's
   successor write — a sealed, write-once field like `seed`.

Everything a lead depends on is fixed at dispatch: the ledger as it stood, the corpus revision, the seed. A collect
days later reveals exactly what was sealed, whatever the player did meanwhile. A **recall** reveals only leads whose
tick `≤ elapsed` (the resolver's own pro-rating rule, `ExpeditionResolver.cs:40-44`, `:67`); the rest are discarded unseen.

### 3. No choice at collect — an automatic resolution

A modal is forbidden and the collect cannot wait, so an expedition storylet is answered **by the squad at the time**:
the storylet's choices are evaluated with `ChoiceResolver.Present`, and the **first eligible choice in declaration
order that is not `leave`** is taken; if none is eligible, `leave`. narrative-seed's planner orders an
`expedition.return` storylet's choices from most to least desirable for this reason (filed on `narrative-planner`).
Because the choice is automatic, every `expedition.return` storylet must satisfy two preflight rules (§5): no `fight`
(the encounter never starts a battle; the tier's battles are the resolver's), no `offer:{stock}` (nothing is spent
without the player).

### 4. Delivery at collect

`CollectAsync` (`ExpeditionEndpoints.cs:79`) gains, after rewards commit:

1. read `leads_json`; keep leads with `tick ≤ elapsed` **whose sealed tick still matches the collect-time
   resolution** — same tick kind and, for `WildCreatureMet`, same species and same join flag. Audit 2026-09-19: the
   tick distribution is read from `ExpeditionTuningHub` at call time (`ExpeditionResolver.cs:48-58`) and the dispatch
   record pins no tuning version, so a tuning publish between dispatch and collect can turn a sealed wild tick into a
   quiet one; a lead whose tick no longer matches is discarded unseen (never re-selected against the later ledger),
   which keeps "the character met is the creature met" true;
2. for each, execute its sealed outcome plan through `OutcomeExecutor` (`spec-outcome-routing.md`), deduped on
   `expedition:{expeditionId}:lead:{t}`: a `met` fact and — for a character met — `CastCreatureCharacter` for the
   **tick's own creature** (`spec-character-registry.md` §4); a `flag.set` for a rumor; a `quest.offered` for a quest;
3. `QuestLifecycle.Capture` and `Settle` for expedition-clock quests (`spec-quest-sources.md` §3.3, §5);
4. return the leads in `CollectResult` as `Leads: IReadOnlyList<ExpeditionLeadDto>` — the log lines the collect
   summary renders.

```csharp
public sealed record ExpeditionLeadDto(int TickIndex, string LeadKind,       // "character" | "rumor" | "quest"
    NarrativeTextDto Line, string? CharacterToken, string? QuestKey);   // Alignment 2026-09-20: narrative-text's one wire text shape
```

`CollectResult` (`ExpeditionEndpoints.cs:70-77`) gains `Leads` as an appended member, so every existing consumer
keeps its shape. `NarrativeNotify.AfterCommit` fires after the collect (`spec-quest-log-contract.md` §4).

**The character met is the creature met.** If the tick's creature **joined** (`WildJoins`,
`ExpeditionResolver.cs:121-131`), it is already the player's specimen: the lead's character is bound to **that**
specimen (`CastCreatureCharacter` with an existing instance id instead of a mint — filed on `character-registry`, a
cast variant that adopts rather than mints) and its fate is `Joined` from the start. If it slipped away, the character
is minted under the narrative cast owner with the tick's species and becomes a save-scoped wanderer the player may
meet again. Either way no extra creature is granted: the join was the tick's, and a slipped-away creature stays
un-owned.

### 5. Preflight rules added with this module

| Rule id | Refuses |
|---|---|
| `expedition.no-fight` | a `fight` choice or `battle.start` outcome on an `expedition.return` storylet |
| `expedition.no-spend` | an `offer:{stock}` choice on an `expedition.return` storylet |
| `storylet.host-has-no-loot-budget` (from `outcome-routing`) | a `loot` outcome on `expedition.return` |

### 6. Tuning and Θ

Published as `expeditions.v{n+1}` through `gk-core/tools/tuning/publish.py expeditions` (T4), beside `tiers.*.dangerBand`:

| Key | Unit | Starting value and reason |
|---|---|---|
| `encounter.wildCreatureMetMilli` | per-mille | 250: about one lead per four wild meetings; wild ticks are 150‰ of ticks (`ExpeditionResolver.cs:49-52`), so a long tier brings home roughly one lead |
| `encounter.quietMilli` | per-mille | 50: quiet ticks are frequent; rumors stay occasional |

Θ for choice odds: `HostContentTheta.ForExpedition(power, tier, parentTerms)` (`spec-host-content-theta.md` §3).

## Data shapes

- `rpg_expeditions.leads_json TEXT NULL` (sealed at dispatch; `NULL` for every expedition dispatched before this
  module and when no encounter fired).
- Sealed lead: `{ tick, tickKind, offer: StoryletOffer, resolution: ChoiceResolution, plan: OutcomePlan }` canonical
  JSON.
- `CollectResult.Leads` (appended).

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| encounter chance, roll | `int` per-mille, the expedition tuning's own type (`ExpeditionResolver.cs:52-58`) | a bounded ratio |
| tick index | `int` | `ExpeditionTickOutcome.TickIndex` (`ExpeditionResolver.cs:17`) |
| seed | `ulong` | the expedition seed's own type |

## SOLID notes

- **S:** the resolver owns ticks; this module owns leads beside them; collect owns delivery.
- **O:** a new lead kind is a storylet shape, not code here.
- **L:** `CollectResult` gains an appended member; nothing existing changes shape.
- **D:** depends on `ExpeditionResolution` as data, never on the resolver's internals.
- No second RNG stream shared with ticks; no second reward path.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/Narrative/ExpeditionLeads.cs','gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs','tests/FusionRpg.Server.Tests/Narrative/ExpeditionLeadTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Expedition"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Expedition"
```

## Structure

```
src/FusionRpg.Core/Narrative/Hosts/ExpeditionLeadPlan.cs      (new: encounter rolls, auto-choice, pure)
src/FusionRpg.Server/Narrative/ExpeditionLeads.cs             (new: seal at dispatch, deliver at collect)
gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs                   (edited: DispatchAsync seals, CollectAsync delivers, CollectResult.Leads)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs             (edited: leads_json write-once, read)
gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs            (edited: encounter.* keys)
data/tuning/expeditions.v{n+1}.json                           (new version via publish.py)
src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs  (edited: §5 rules)
tests/FusionRpg.Core.Tests/Narrative/Hosts/ExpeditionLeadPlanTests.cs  (new)
tests/FusionRpg.Server.Tests/Narrative/ExpeditionLeadTests.cs          (new; in-memory store)
```

## Testing strategy

Game closed; fixture tiers, squads and corpus; stores in memory.

- **Tier hashes unchanged at any chance:** the existing expedition hash tests pass with `encounter.* = 0` and with
  `encounter.* = 1000`; `ExpeditionResolution` is byte-identical in both.
- **Sealed at dispatch:** a lead sealed at dispatch is revealed unchanged at collect even after the fixture ledger
  gains facts that would change selection (dispatch-then-facts and facts-then-dispatch are different, specified
  executions: the lead follows the ledger **at dispatch** in both).
- **Recall:** recall at elapsed `k` reveals exactly the leads with `tick ≤ k`.
- **Tuning moved between dispatch and collect (Audit 2026-09-19):** a fixture that seals a wild-tick lead, then swaps
  the event-roll tuning so that tick resolves `quiet` at collect, reveals no lead for it and writes no fact.
- **Once:** a retried collect after commit returns no second lead set and writes no second fact (the collect's own
  exactly-once gate).
- **Character met is the creature met:** a joined tick's lead character is bound to the minted join's `instanceId`;
  a slipped-away tick mints one narrative-owned specimen of the tick's species and grants the player nothing.
- **Auto-choice:** the first eligible non-`leave` choice is taken; with none eligible, `leave`.
- **Preflight:** `fight`, `offer` and `loot` on `expedition.return` each fail with their rule id.
- **Never modal:** `CollectResult.Leads` is data; no endpoint waits on an answer (a reflection test finds no
  expedition-host answer route).
- **No population:** fixtures only.

## Success criteria

1. Leads roll on their own stream and never move a tier hash. 2. Leads are sealed at dispatch and revealed at collect
as log lines. 3. The character met is the creature the tick met. 4. No payout beyond the tick's manifest; no spend and
no fight from an idle encounter. (G4 expedition half.)

## Boundaries

- **Always:** a disjoint stream; seal at dispatch; deliver in `CollectResult`.
- **Ask first:** hosting on `Battle`, `FoundSouls` or `Injury` ticks; a player choice at collect.
- **Never:** edit the expedition resolver's ticks; block or pause the idle clock; a modal; pay a lead on top of the
  manifest. (A quest a lead offers is paid on completion by `quest-sources` §6 — Owner ruling 2026-09-20: out of the
  collect's own `expedition-tier` rolls, one roll taken with the quest's window, never an added roll.)

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `CollectResult.Leads` → `ExpeditionLeadDto[]` | the expedition collect summary (FE), `quest-log-contract` (via facts) |
| `leads_json` | this module only |

## Contradictions found (report; not fixed here)

1. **"Resolves at dispatch" versus a resolver that runs at collect.** Ideal §6.6 says an encounter *"resolves at
   dispatch like every tick"*; ticks are actually resolved at collect from a seed sealed at dispatch
   (`ExpeditionEndpoints.cs:12-17`, `:109`). For ticks the two are equivalent (pure in the seed); for a lead they are
   not, because selection reads the ledger. This spec resolves leads at dispatch and seals them, which is the
   ideal's intent; the ideal's sentence describes ticks slightly inaccurately.
2. **Adopting a joined creature as a character.** `spec-character-registry.md` §4 casts only by minting. A lead
   whose tick creature joined needs a cast variant that binds a character to an existing player-owned specimen.
   Filed on `character-registry`.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: expeditions (reader, collect payload), tuning (expeditions domain), characters, quests, story ledger.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 20 and G4; ideal §4.4, §6.6, §7; DESIGN-GATE §1 Standalone and Economy rows; sibling
    specs host-content-theta, character-registry, outcome-routing, quest-sources; code: ExpeditionResolver (streams,
    tick kinds, wild tick), ExpeditionEndpoints (dispatch, collect, CollectResult), rpg_expeditions DDL.
[x] Every claim cites file:line.
[x] Tier hash stability is a test at chance 0 and 1000, not a claim.
[x] No population pinned.
[x] No cache.
[x] Order: dispatch vs later ledger facts specified both ways.
[x] Actor numbers: none; no creature granted beyond the tick's own join.
[x] No parallel path: the resolver is read, not forked.
[ ] Registry row: none new.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (Standalone, Economy, Tunables rows; three clocks), §2 (1, 2, 9,
12, 15), §3, §5; `economy-principles.md` P1, P13, P14; `ExpeditionResolver.cs`, `ExpeditionEndpoints.cs`; ideal §6.6
Expeditions row (reconciled wording).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | MEDIUM | **Tuning drift breaks the seal.** Leads are selected against a dispatch-time resolution, but ticks are re-resolved at collect with the tuning of that moment (`ExpeditionTuningHub`), and no tuning version is pinned at dispatch (`ExpeditionEndpoints.cs:109` calls `Resolve` with the live tuning). A publish in between could deliver a "creature met" lead on a tick that is now quiet, or bind the wrong species | **Fixed** (§4 step 1): collect-time match check, discard on mismatch; test |
| 2 | MEDIUM | "No payout beyond the tick's manifest" vs a lead's `quest.offer`, whose completion rolls `expedition-tier` (`spec-quest-sources.md` §6) | **Fixed in text** (Boundaries). **Resolved — Owner ruling 2026-09-20:** the quest's reward is taken out of a collect's own tier rolls (`spec-outcome-routing.md` §3), so there is no faucet on top |
| 3 | LOW | Objective still said the encounter is "resolved at dispatch, like every tick" | **Fixed** |

Checked and holding: disjoint `narrative:expedition:*` stream (tier hashes unchanged at any chance — a test, not a
claim); no modal, no choice at collect; the idle wall clock is the expedition's own, not a fourth clock; sealed write-once
field; the character met is the creature met (with #1); dedupe on `expedition:{id}:lead:{t}` (P14).

**Registry row proposed** (shared file, not written): `ns-expedition-lead-disjoint-stream` → the tier-hash tests at
`encounter.* = 0` and `1000`. **Boundary ask:** `src/FusionRpg.Server/Narrative/ExpeditionLeads.cs` (new),
`src/FusionRpg.Core/Narrative/Hosts/ExpeditionLeadPlan.cs` (new) → `FusionRpg.Server.Tests`/`FusionRpg.Core.Tests` filter
`Expedition`.

## Cross-lane alignment (2026-09-20)

- Alignment 2026-09-20: `ExpeditionLeadDto.Line` is `NarrativeTextDto` (`spec-narrative-text.md` §2); `TextRefDto`
  is withdrawn program-wide (`spec-quest-log-contract.md` §2).
- Owner ruling 2026-09-20 (rewards come out of the host budget): the expedition host's budget line is the collect's
  own `expedition-tier` roll(s) (`gk-data/packs/fusion/data/seed/loot/tables.v1.json` `drop.exp.*` rows; correlation `loot:exp:{sourceId}`,
  `gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs:138`). A lead adds nothing to the sealed manifest; an
  expedition-offered or save quest's reward takes one of a collect's own rolls with the quest's window; the deduction
  rule and its queue are `spec-outcome-routing.md` §3's. The P14 dedupe key `expedition:{id}:lead:{t}` is unchanged.

- Alignment 2026-09-20: `expedition.return` is a seed-side host row (`narrative-seed/spec-storylet-vocab.md` §3.1,
  admits `story`, `curio`; climate-neutral — Owner ruling 2026-09-20 (round 5): R19 keeps it neutral because an
  expedition carries no destination sector: `ExpeditionRow` holds a tier, a squad and a seed only,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:10-12`; if one ever carries a destination sector, its climate is
  ~~derived through the same sector-type registry, `narrative-seed/spec-storylet-vocab.md` §3.9~~ that sector's own
  `WorldSector.Climate` — Owner ruling 2026-09-20 (round 6), R20); §5's preflight still refuses `fight`, `offer` and `loot` on it.
