# Capability map: npc-story-events

**Status: spec phase, written 2026-09-19. Map approved by the owner 2026-09-19 ("approve, go"). Module specs authorized; no build authorized.**
Module specs are written only after the module boundaries, dependency direction and build order below
are approved. Specs land at `docs/architecture/npc-story-events/spec-<module-id>.md` (new); the plan and
task list at `tasks/npc-story-events-plan.md` (new) · `tasks/npc-story-events-todo.md` (new), the
prefixed pair this repo's parallel-program convention requires. The bare `tasks/plan.md` /
`tasks/todo.md` pair belongs to another stream and is never a fallback.

**Program id:** `npc-story-events` — the **runtime** side of NPCs, storylets, quests, the story ledger,
relations and counter-doctrine.
**Ideal it implements:** [npc-story-events-ideal.md](npc-story-events-ideal.md) — the shape (§6), owner
rulings R1–R13 (§10) and the enrichment pass (§11). This map does not reopen any of them. Owner ruling 2026-09-20
(round 5): rulings R17–R19 (ideal §10) are applied here — see the section of that name at the end.
**Content supply:** [narrative-seed-ideal.md](narrative-seed-ideal.md) §6.2 (storylet contract), §6.5b
(structured story text), §6.8 (localization bridge). Its capability map, `narrative-seed-map.md` (new),
is written in the same spec round.
**Session record:** `tasks/sessions/narrative-programs-spec-20260919.json` (this file is in its `paths`).
**DESIGN-GATE rows read this session:** Anything at all, Product vision, Stats, Actor layer, Economy,
Battle engine SSOT, World map, UI, Standalone, Live probe; §2 invariants; §3 evidence rules.

---

## What this program is

The runtime that makes every place the player goes **inhabited**: one storylet engine that the Delve,
the world map's turn, a held sector, an expedition's return and the homeworld all ask for an encounter;
persistent characters minted from seeds per save; one relation ladder for characters and factions; one
quest engine with a fact source per place and a quest log; a story ledger with save and world scopes;
failure branches that open content instead of stacking a penalty; and **counter-doctrine**, the
faction-level answer to the player's aggregate strategy that replaces a recurring-antagonist system
(R13).

## What it is not

- **Not a change to what PvZ is.** Every module is `Core/`, `Data/`, `Server/` or `web/`. The lawn
  contributes observed facts and may host a fight; it never runs a story, and no scene plays mid-match.
- **Not a second engine for any place.** The Delve's event engine is re-seamed out of `Delve/` and
  becomes the only engine (ideal §6.2). No place gets its own deck.
- ~~**Not the Delve's live path.**~~ **The Delve's live path is now this program's.** Owner ruling 2026-09-19 (round 3): npc-story-events absorbs the Delve live-path wiring — making the Delve startable, marking rooms,
  the room-entry draw route, the answer route, text on the wire and the quest offer at entry — as modules `delve-live-start` and `delve-live-rooms` (rows 28–29), placed before `delve-host`. Party-dungeon keeps the Delve's
  content (domains, rooms, events, encounters), its engine rules and the rest of its loop (extraction, room clear). The transferred party-dungeon task ids are listed at the top of `tasks/party-dungeon-todo.md`.
- **Not the generator.** Seeds (storylets, characters, arcs, spine chapters) are narrative-seed's. This
  program loads, casts and resolves them. It never calls a model.
- **Not a scene player.** Every authored scene plays through story-scene's `StorySceneHost`.
- **Not a second turn loop, counter engine or push path.** It adds content to the world `Events`
  phase, feeds achievement-title evidence, and posts through notification-ssot.
- **Not a currency.** Disposition is a derived band, never a spendable stock. No row is proposed for
  `empire-resource-ssot.md` §3.
- **Not the rename.** R9/R12 surface renames (prologue, guide, product-vision wording, title) are the
  identity-rename program's, planned at `tasks/identity-rename-plan.md` (new).

---

## Loops extended

From [the-loops.md](../guide/the-loops.md). No new loop.

| Loop | How this program extends it | Loop page evidence |
|---|---|---|
| **7. Quests and events** (primary) | Storylets in every place, quests beyond the Delve, the quest log layer, failure branches | `the-loops.md:139` (*"delve quests, world events and raids, player-facing **quest log** **Vision**"*), `:141` |
| **6. The Delve** | Named characters in rooms; story chains advance | Delve host (ideal §6.6) |
| **4. World map — adventure** | Sector events in the `Events` phase; named warlords; the Rotwright's voice and doctrine | `the-loops.md:95` (enemy counter-development, Vision) |
| **5. World stage — empire** | Petitions on held sectors; a trader with a name in the Market slot | ideal §6.6 |
| **2. Idle expeditions** | A tick can come home as a lead | `the-loops.md:75` (*"ticks that start quests and world events **Vision**"*) |
| **3. Farm, hunt, defend** | Failure branches open content | `the-loops.md:97` |
| **B. Creature summon and fusion** | A befriended character joins by ownership transfer | ideal §6.3 |

---

## Principles restated (binding on every module below)

A module spec reads this map, not its links, so each rule is stated in full.

1. **RPG layer only.** NPCs, storylets, quests, relations and doctrine are RPG-layer systems. The lawn
   contributes observed facts (`PvzActivityKinds`, `gk-core/src/FusionRpg.Core/Activity/PvzActivityKinds.cs:6-13`)
   and can host a fight. Nothing here asks PvZ to know what a quest or a character is.
2. **Record then drain; react to past facts.** A beat reacts to a turn report entry, a delve decision
   row, an expedition resolution or a lawn activity fact that already happened. A beat that fires one
   turn late is correct.
3. **Standalone-first is a capability rule.** Every storylet, quest and character is playable with
   Fusion closed. A quest objective counts a mode-agnostic, source-tagged fact; "kill 30 on the lawn" is
   not a legal objective (`decisions.md` Standalone-first row, `docs/architecture/decisions.md:107`).
4. **Three clocks, not a fourth.** The lawn match clock, the expedition wall clock and the world's
   virtual turns (`the-loops.md:11-13`). Cooldowns, quest expiry and pity count on the **host's own
   clock** (rooms, turns, collects). No daily quests, no real-calendar timers.
5. **One power ladder.** A skill check is a contest on `Θ_actor − Θ_content` through
   `CombatProbability.Sigmoid` (`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8`). A reward magnitude
   reads `P(Θ_content)` through the existing loot pipeline and `SoulSinkPolicy.Price`
   (`gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:40`). `Θ_content` per host is the SSOT formula
   (`power/ssot-power-scale.md:230`) with that host's inputs. A new `f(level)` is the defect.
6. **The balance surface is data.** Deck weights, pity, cooldowns, band shifts, study-bar rates and
   encounter chances live in `gk-core/data/tuning/narrative.v1.json` (new) or an existing domain file, published
   as `v{n+1}` through `gk-core/tools/tuning/publish.py`. Display text lives in seed and catalog files.
7. **No hard ceilings.** Nothing caps a magnitude. Disposition bands, fire-chance `min(1000, …)` and
   pacing limits (one spine beat per pulse, one conversation per character per return) are structural
   bounds or bounded ratios and each says so in a comment.
8. **Every faucet names its sink; no new stock.** An outcome pays in an existing stock through its
   existing grant path (`AwardSouls`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:215`) with a dedupe
   key from a durable fact id, and **out of the host's existing budget, never on top of it** (ideal §11
   item 1). `offer:{stock}` choices are sinks on the same ledger.
9. **One ActorHub compose.** Relationships grant **access** (choices, quests, prices, intel, a join),
   not stats. Any outcome that changes an actor's numbers is an atom container at an `OwnerScope` or a
   registered `IActorStatSubsystem`, and its spec answers the five actor-layer questions first
   (`decisions.md` Actor layer stack row, `:52`). No module here decides an actor number.
10. **The battle engine is the SSOT for every battle.** A `fight` choice or `battle.start` outcome hands
    a `BattleRequest` (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39`) or an `IIntentSource` to an
    existing battle mode. A place owns its loop, never a mechanism (`decisions.md:53`).
11. **SOLID is binding.** One storylet engine, one quest engine, one relation ladder, one personality
    vocabulary (`CreaturePersonality`), one scene player, one story store. A module that adds a second
    of any of these fails review.
12. **Seed to concrete; no model at runtime.** Seeds are cast per save, seeded and reproducible. Rolls
    use `WorldSeed.DeriveRollSeed` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`) or
    `SeededRng.DeriveStream` with a **named stream per purpose**, never shared with a combat stream,
    never `System.Random`, never the wall clock.
13. **Generated data is never hand-edited.** A defect in a storylet or character seed is fixed in
    narrative-seed's generator and regenerated. Authored storylets live under an authored path with
    `provenance: authored` and pass the same validators (ideal §11 item 10).
14. **A guardrail validates the contract, never a population.** Tests assert closed enums, joins,
    uniqueness, preflight rules, determinism and structural bounds. The storylet corpus, the cast and
    pick counts are readings.
15. **A game is a stage with layers.** A storylet card is a band-2 layer over the current stage; the
    quest log is a layer openable from anywhere, never a route. Authored scenes use `StorySceneHost` and
    its scoped `size="scene"` exemption and nothing wider (`decisions.md` Game GUI row, `:110`).
16. **Names are tokens (R8–R11).** Story text never contains a literal lead or species name. Leads are
    `{lead_summoner}` / `{lead_companion}` / `{lead_antagonist}`, resolved from a names registry — today
    the Garden Keeper, Hourbloom and the Rotwright (R11). A rename is one registry edit.
17. **No recurring antagonist (R13).** The six design rules of ideal §6.12 are binding on this program
    and on world-graph's warlords: no enemy grows from meeting you; no enemy hierarchy; no enemy
    remembers you personally; no enemy base built from an enemy's traits; no sharing of enemy data
    between players; warlords grow by world rules only.

---

## Locked assumptions

Each cites the ruling or rule that locks it. None is re-litigated at spec time.

1. **One engine, many hosts** (ideal §6.2, principle 11). The Delve is the first host.
2. **The storylet shape widens, it is not replaced** (ideal §6.2; narrative-seed §6.2). `EventRow`
   (`gk-core/src/FusionRpg.Core/Delve/Events/EventRow.cs:28`) gains `choices[]`, roles, hosts, `revision`,
   `provenance`, arc links and keyed text.
3. **Spine is fully generated (R1)**, finite chapters keyed to time-machine pieces, one per world won,
   then arcs and texture continue (R3) — not a progression ceiling.
4. **The antagonist speaks (R2).** story-scene's v1 deferral is lifted for this program.
5. **One 4-band relation ladder for characters and factions (R4)** — the `disposition.v1.json` ladder
   (`eager, open, wary, hostile`, `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`). trade-network's
   `counterparties` consumes it (`trade-network-ideal.md:315`).
6. **Leads' names and the title (R8–R12)** are tokens and a names registry here; surface renames are
   identity-rename's.
7. **Counter-doctrine replaces recurring antagonists (R13)**; the design stays clear of US 10,926,179 B2
   by the six rules. This is a design choice, not legal advice; a counsel review precedes a commercial
   release.
8. **Characters are mint-first** under a non-player owner row, following `EnsureZombossPlayer`
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:25`) and `MintForZomboss` (`:42`). Personality
   is the specimen's own (`ContractPolicy.PersonalityFor`,
   `gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:195`). Joining is an ownership transfer.
9. **Scope follows "you keep who you are"** (ideal §6.3, §6.7): leads and companions are save-scoped; local characters, clan relations and world arcs are world-scoped. Owner ruling 2026-09-19 (round 3): world-scoped state lives as long as
   its world exists — active, hibernating or idle, contested or won (world-continuity modules `world-state-vocabulary`, `world-fall`; `world-continuity-map.md` locked assumption 1). **Owner ruling 2026-09-19 (round 4):** world-scoped story state is **never deleted** — `active` is live (drawn, written); `hibernating`/`idle` is dormant (kept intact, not drawn, no writes except facts world-continuity's `CoarseStep` emits); outcome `fallen` is frozen (read-only history the reserved `world-reclaim` may revive). There is no "abandoned" state (`world-continuity-map.md:117`, `:127`, `:274-275`); "retire" in this program means frozen. The derived `WorldNarrativePhase` (`narrative-vocabulary`) carries it.
10. **Relations move on facts, never on time** (ideal §6.4). The top band may be story-gated.
11. **Rewards come from host budgets** (ideal §11 item 1); **`Θ_content` per host** from the SSOT
    formula (§11 item 2); **`(id, revision)` pinning** with tombstones (§11 item 3); **onboarding
    cadence** rides existing checkpoints and asks the first-session spec for one slot (§11 item 4);
    **quest expiry on host clocks**, abandoning is free (§11 item 5); **local pick-rate report**, no
    upload (§11 item 6); **ip-censor is a release gate** (ruling IC-3), no second name filter here
    (§11 item 7); **success readings** are reported, never asserted (§11 item 9).
12. **Branching dialogue trees are rejected** (ideal §6.11). Storylet choices plus talk verbs cover
    the need.

---

## Cross-program dependencies — wiring gaps other programs own

This program's content is **unreachable** until these land. Each is a wiring gap (the machinery exists
and is inert), owned by the program named. This map records them as dependencies with owners; it does
not absorb them. Verified against code this session.

| Gap | Evidence (verified 2026-09-19) | Owner | Blocks |
|---|---|---|---|
| **The Delve cannot start live.** `dungeon_domain` is never populated | `ImportDungeonDomains` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:225`) has no caller in `src/` outside its own file; `/start` returns before `CreateDelve` (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:175-176`) | **this program** (`delve-live-start`) — Owner ruling 2026-09-19 (round 3): was party-dungeon (`domain-catalog`; D4.16's production caller, D4.22's five start delegates). Domain **content** passing preflight stays party-dungeon's (D4.17, D4.30) | `delve-host` live proof |
| **The event engine has no production caller** | `EventDeck.Build`/`Resolve`/`Answer` (`gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:146,218,339`), `EventDraw.PickEvent` (`EventDraw.cs:42`) and `OutcomeResolver` (`OutcomeResolver.cs:35`) are referenced only inside `gk-core/src/FusionRpg.Core/Delve/` and tests; `MarkRoom` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:379`) and `RecordEventSeen` (`:440`) have no production caller | **this program** (`delve-live-rooms`) — Owner ruling 2026-09-19 (round 3): was party-dungeon (`event-deck`; the live call-site clauses of D3.3/D3.5 and D3.9's store callers). Deck goldens and the remaining preflight conjunct stay party-dungeon's | `delve-host` live proof |
| **No event answer route exists** | The Delve's registered routes are `/recovery-ritual`, `/domains/{playerId}`, `/start`, `/{delveId}` (`DelveEndpoints.cs:35-57`; Audit 2026-09-19: listed only two) and `/rooms/{id}/talk`, `/cage`, `/pray` (`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:62-66`) | **this program** (`delve-live-rooms`) — Owner ruling 2026-09-19 (round 3): was party-dungeon (D3.9's answer endpoint) | `delve-host` live proof; `storylet-card` on the Delve |
| **The loader refuses eligibility trees** | `EventSeedFile.cs:40-44` throws `NotSupportedException` on any non-null `eligibility` | **this program** (`storylet-contract`) — named here because party-dungeon's D3.9 preflight reads the same loader | — |
| **Delve quests are never offered** | `WriteQuestOffer` (`RpgStore.Delve.cs:517`) has no production caller; `QuestOffer.Draw` (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestOffer.cs:107`) is not called at `CreateDelve` | **this program** (`delve-live-start`: the offer at `CreateDelve` and the tracker route) — Owner ruling 2026-09-19 (round 3): was party-dungeon (`delve-quests`; D4.14). Verdicts at `CloseDelve` stay party-dungeon's | Delve quests in the quest log |
| **Achievements never evaluate** | `AchievementEvaluator` is not registered: the hosted services are `EventIngest`, `CompactionWorker`, `UniqueActorDeployWatchdog` and (flag-gated) `SimHeartbeatHost` (`gk-core/src/FusionRpg.Server/Program.cs:403-410`). Its trigger vocabulary already has `event-seen` (`gk-core/src/FusionRpg.Core/Achievements/AchievementRegistry.cs:25`) | achievement-title (`achievement-evaluator`) | quest completion as achievement evidence |
| **The world `Events` phase rolls the calendar only** | `TurnEngine.Events` (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:340-341`: *"Calendar boundaries are rolled and reported; their effects belong to later modules."*) | **this program adds content** (`world-events-host`); the turn engine, its phase order and `RulesetVersion` (`TurnEngine.cs:114`) stay world-map-program's | — |
| **Nothing ends or wins a world** (Reconciled 2026-09-19: found in the spec round by `spec-spine-progress.md`, `spec-story-ledger.md` and `spec-character-registry.md`) | `rpg_worlds.state` defaults to `'active'` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:32`) and is only ever written as `'active'` at creation (`:245`); the only `UPDATE rpg_worlds` advances `current_turn`/`revision` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:687-689`). No win record and no world-end transition exist | world-map-program (world-end transition with a win record) | `spine-progress` past chapter 1 (a piece per world won); world-scope cleanup: story-ledger world facts ending with the world and `character-registry` retiring world-scoped specimens **Update 2026-09-19:** owned by the approved `world-continuity` program — its `world-victory` module writes a durable world-won fact that `spine-progress` reads (`world-continuity-map.md` module 5 and its npc-story-events consumer row). World-scope lifetime must also follow that program's hibernation states (worlds hibernate rather than end). ~~**Owner ruling 2026-09-19 (round 3):** … retires only when the world is fallen or abandoned (filed on `world-state-vocabulary`)~~ **Owner ruling 2026-09-19 (round 4):** world-scoped story, character and relation state is never deleted: live while `active`, dormant while `hibernating`/`idle`, frozen (read-only) once `fallen`; no abandoned state and no ask on `world-state-vocabulary` — `spec-story-ledger.md` §5, `spec-character-registry.md` §4, `spec-relation-ledger.md` §2. |
| **Nothing mints world claim loot** (Owner ruling 2026-09-20 (round 5), R17) | `ClaimResolver` writes a `claim.loot:` report line only when `powerTuning` is passed and never mints (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:124-135`); `CommitWorldTurn` passes none (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`); no code reads the line | **this program** (`world-claim-loot`, row 30) — was world-map-runtime's `sector-loot-wiring` Part A; the world-map side records the transfer in its own change | `world-events-host` and `petition-host` rewards (R14: they take a claim roll, never add one) |
| **Clans have no policy and needs are flat** | `FactionPolicies.ById` registers `StandFastPolicy` and `FrontierRulesPolicy` only (`gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18`); `UniformNeeds` (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31`) | world-map-program (`ai-commander`) and trade-network (`counterparties`) | `petition-host` (clan requests are computed from needs) |
| **Player-routed push** | notification-ssot map is Phase 0 (`notification-ssot-map.md`, modules `notify-vocabulary` … `notify-service`) | notification-ssot | band-4 notices for leads and quest updates (the turn report rail works meanwhile) |
| **Delve merchant sells nothing** | `DelvePrices.PriceUndesigned` (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:17`) | item program (derived base price) | a named trader's goods; the trader's face and lines do not wait |
| **Seeds with choices, characters, arcs, spine chapters; motif glosses; the two corpus defects** | narrative-seed-ideal §8 steps 1–6; §3.4 of the ideal (CJK leakage, two dangling `chainRef`s) | narrative-seed | real content in every host; see gate G2 |
| **The first-session slot for "first character met"** | ideal §11 item 4 | `standalone/spec-first-session-progression.md` (asked, not edited) | onboarding cadence |

**The largest lever is the Delve's live path**, not new design (ideal §5). A story program built
before the Delve can start ships content nobody can reach in the one place that already has an engine.
Owner ruling 2026-09-19 (round 3): that lever is now this program's own first work — `delve-live-start` and `delve-live-rooms` in
wave 1, before `delve-host` — and the world and expedition hosts still do not wait for it.

---

## Modules

Stable kebab-case ids, chosen once. Every module is provable with the game closed. "FE" marks a web
module; FE modules go through `/idea-ui` before their spec (ideal §6.5, §9).

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `narrative-vocabulary` | C# readers for the **shared** closed registries that narrative-seed authors under `gk-data/packs/fusion/data/seed/narrative/_registry/` (new) — roles (9), choice kinds, consequence kinds, condition vocabulary, line contexts, voice registers, host kinds — so seed validator and runtime read **one** file each (the `dungeon-registries` precedent). Host kinds: `storylet-vocab` authors `host-kinds.v1.json` and the runtime reads it; this module defines the members (`spec-narrative-vocabulary.md` §2). Reconciled 2026-09-19: host kinds were listed as runtime-only, which contradicted `narrative-seed/spec-storylet-vocab.md` §3.1. Runtime-only closed vocabularies: character `fate` (present, joined, departed, fallen), story fact kinds, doctrine ids. The `gk-core/data/tuning/narrative.v1.json` (new) schema and loader, T5 rejection on a missing key, structural bounds with exemption comments | narrative-seed registries (external) | 0 |
| 2 | `storylet-reseam` | **Pure move, no behaviour change.** `EventCatalog`, `EventDeck`, `EventDraw`, `OutcomeResolver`, `EventDeckPreflight`, `EventFilters`, `UnknownPity` and their siblings move from `gk-core/src/FusionRpg.Core/Delve/Events/` to a place-neutral namespace (`src/FusionRpg.Core/Narrative/Storylets/` (new)) behind an `IStoryletHost` seam (host kind, host clock, seen scopes, stream name). The Delve keeps its behaviour through a Delve host adapter. Proven by the existing event-deck tests passing unchanged and every battle, expedition and world golden byte-identical | — | 1 |
| 3 | `storylet-contract` | Widens the loader and `EventRow`: `choices[]` (2–4, exactly one `leave`, each with a choice kind, a condition and 1–3 outcomes, each outcome's consequence the seed's one `{kind, ref, param}` object loaded as-is — Owner ruling 2026-09-19 (round 3):), `roles[]`, `hosts[]`, `revision`, `provenance: generated \| authored`, `arcRef`/`arcLink`, keyed text fields. Lifts the eligibility refusal (`EventSeedFile.cs:40-44`) — trees compile through `PredicateCompiler` within the atom predicate grammar (depth ≤ 4, ≤ 16 nodes, `effect-atom/definitions.md` §3). Legacy seeds load as today's fixed verb set (`EventChoices.Presented`, `gk-core/src/FusionRpg.Core/Delve/Events/EventChoices.cs:23`) until regenerated. Preflight **fails** on a dangling `chainRef` (today skipped silently, `EventDeckPreflight.cs:50-53`), an unresolved pool id, a role used but undeclared, and an event that gates a boss | `storylet-reseam`, `narrative-vocabulary` | 1 |
| 4 | `story-ledger` | One append-only fact store with **save** and **world** scopes: `met`, `helped`, `refused`, `betrayed`, `spared`, `flag.set`, `chapter.reached`, `storylet.seen`, `choice.picked`, `quest.*`, failure facts. Records `(storyletId, revision)` so an in-progress arc resolves against the revision it started on; ids are tombstoned, never reused. **Generalizes** the onboarding story rows (`OnboardingStoryRow`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs:25`) and the Delve's event-seen scopes (`RpgStore.Delve.cs:405-463`) behind one store — no third parallel store — while keeping story-scene's frozen `rift-prologue`/version `1` contract. World scope ~~ends with the world~~ lives as long as its world exists and is never deleted: dormant while the world hibernates or idles, frozen once it falls (Owner ruling 2026-09-19 (round 4); replaces round 3's "retires when fallen or abandoned"); the append path is the one write gate | `narrative-vocabulary` | 1 |
| 5 | `relation-ledger` | The **derived** 4-band disposition read model over story-ledger relation facts, for characters and factions (R4). Band shift per fact kind from tuning; **no time term**; story-gated top band; the band decides **whether** a character may join (access), and every join starts at the normal bind rank — owner answer (a) in `spec-relation-ledger.md` (Audit 2026-09-19: was "the conversion of disposition into a starting `LoyaltyRank`", which would give a relationship an actor-number effect). Exposes the band to trade-network's `counterparties` and to predicates. No stored number, no spendable quantity | `story-ledger` | 1 |
| 6 | `host-content-theta` | `Θ_content` per host through `PowerIndexComposer` (`gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:44`) and the SSOT inputs (`ssot-power-scale.md:230`): sector `DangerBand` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:156`) for world hosts, the dispatch tier for expeditions, the room Θ the Delve already composes, danger 0 for the homeworld. A wiring module; no new curve | party-dungeon `difficulty-ladder` (external) | 1 |
| 7 | `character-registry` | The character store: a persistent identity bound to a **minted specimen** held by a non-player owner row; species, role, home, fate, scope (save or world); memory as story-ledger facts; **ownership transfer** on join (the creature who talked to you is the one who fights for you); world-scoped characters **frozen, never deleted or retired**, when their world falls and dormant while it hibernates (Owner ruling 2026-09-19 (round 4), replacing round 3's retirement); every specimen stays explained by its row and its world's phase, so none is orphaned (ideal §9 asks the spec to state it); the anti-Nemesis rule that an enemy-role character's row never gains level, trait, rank or title from an encounter (principle 17) | `story-ledger`, `narrative-vocabulary` | 2 |
| 8 | `cast-resolver` | **Casting**: at world creation, which character seeds (one per species that gets one, species fixed in the seed) a save meets and their homes, seeded, per save (Reconciled 2026-09-19: was "templates onto concrete species"; see `spec-cast-resolver.md` Contradictions 1) (two saves meet different people); per storylet, roles (required / optional / forbidden, each with a score over the save's facts) cast from characters and the party — a required role that cannot be cast removes the storylet; arcs cast once and reused by later links. **Resource binding** of placeholders (`{place}`, `{supply}`, `{reward}`, `{cost}`) from world state | `character-registry`, `storylet-contract`, `relation-ledger` | 2 |
| 9 | `narrative-predicates` | The new predicate leaves, each a reviewed addition to the closed `LeafId` enum (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46`) with a `FactReader` reader: relation band, story flag, character state, the lead's level against a named gate, the antagonist's doctrine study (Alignment 2026-09-20: replaces the sector-kind leaf, which only duplicated host placement; `spec-narrative-predicates.md` §5 maps every seed condition id to its leaf) (Audit 2026-09-19: was "level band" — a band is a private `f(level)`), and the **party-composition leaf** that `bring:{tag}` needs (a real gap, narrative-seed §6.2) | `story-ledger`, `relation-ledger`, `character-registry` | 2 |
| 10 | `storylet-selection` | Selection, identical for every host: **tier** (one spine beat per pulse pre-empts; then priority storylets — consequences, next chain link after the previous was seen; then the pool); **pool pick** as a seeded weighted draw, weight = frequency band × specificity, unplayed before played, pool reset without resetting cooldowns; **fire chance with pity** `p = min(1000, p0 + n × step)` per-mille for sparse hosts; **cooldowns** per storylet and per kind on the host's clock; **fairness**: no two negative storylets in a row on one host | `storylet-contract`, `narrative-predicates`, `story-ledger` | 2 |
| 11 | `narrative-text` | Rendering of structured story text: entity tokens (`{lead_*}`, `{c_<slug>}`, `{c_<slug>_epithet}`, `{role_<id>}`, bound placeholders) resolved from the **names registry** `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (new) and the cast; ICU `select` on the registry's closed feature tags (`article`, `gender`, `number`); the closed semantic markup set rendered by the presentation layer; the **lingui codegen bridge** — a build step emitting literal `msg({ id, message })` descriptors from seed keys, committed and drift-checked, loaded in its own chunk (narrative-seed §6.8). Owner ruling 2026-09-19 (round 4): the bridge also carries the repaired, keyed legacy Delve event text | `narrative-vocabulary` | 1 (Owner ruling 2026-09-19 (round 4): moved from 2 so `delve-live-rooms` can show text in wave 1; its only dependency is wave 0) |
| 12 | `scene-script-loader` | Scene scripts as **data** (spine chapters and hub conversations) instead of TypeScript literals (`RIFT_PROLOGUE_SCRIPT`, `sceneScript.ts:105`; Reconciled 2026-09-19: `:32` is the `SceneBeat` type; the literal is at `:105`), played by `StorySceneHost`; speaker ids from the cast registry rather than the closed `ActorId` union (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:19`), which widens as a reviewed change under story-scene (R2 adds the antagonist); eligibility from the story ledger through the existing `isSceneEligible` seam (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts:58-74`), which only narrows | `narrative-text`, `story-ledger` | 2 |
| 13 | `choice-resolution` | Answering one choice: eligibility per choice kind (`interact`, `leave`, `use:{tag}`, `offer:{stock}`, `fight`, `bring:{tag}`, `persuade`, `threaten`); **contests** on `Θ_actor − Θ_content` through `CombatProbability.Sigmoid`, or the shipped flat coin for a disposition shift that does not scale with power (`TalkTree.cs:88`); **odds shown** for every contest; `offer` priced through the existing pricing (`OfferPricing`, `SoulSinkPolicy.Price`); `fight` hands a `BattleRequest` to an existing mode. Records `choice.picked` in the story ledger | `storylet-selection`, `cast-resolver`, `host-content-theta` | 3 |
| 14 | `quest-sources` | Generalizes `QuestProgress.Evaluate` (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestProgress.cs:30`), whose only fact source is a `DelveReport`, to **fact sources per place**: the delve report, the committed world turn report, an expedition resolution. Mode-agnostic objectives only. Save- and world-scoped quests persist as story-ledger facts; delve-scoped quests keep the Delve's per-run record. Expiry on the host's clock; abandoning is free; rewards through existing grant paths deduped on the quest's durable id; completion emitted as achievement evidence | `story-ledger` | 3 |
| 15 | `outcome-routing` | The six new consequence kinds, each routed through an existing path, reading the outcome's `{kind, ref, param}` consequence (Owner ruling 2026-09-19 (round 3): `param` carries the relation fact kind; no ordinal → fact mapping): `quest.offer` → `quest-sources`; `relation.shift` → `relation-ledger`; `story.flag` → `story-ledger`; `battle.start` → `BattleRequest`/`IIntentSource`; `scene.play` → `scene-script-loader`; `recruit` → `RecruitMint` for an unnamed wild creature (`gk-core/src/FusionRpg.Core/Delve/Wild/RecruitMint.cs:39`) or an ownership transfer for a cast character. Existing effects (resource delta, status, loot draw) keep their paths. **Every payout is drawn from the host's own budget** with a dedupe key from a durable fact id | `choice-resolution`, `quest-sources`, `relation-ledger`, `character-registry`, `scene-script-loader` | 3 |
| 16 | `quest-log-contract` | The server read model and wire DTO for the quest log: open quests across scopes (including the Delve's), the cast you have met, the story so far (spine chapters reached, history fragments found out of order and sorted). No UI | `quest-sources`, `character-registry`, `story-ledger` | 3 |
| 17 | `delve-host` | The Delve as a host: room kind → host kind (`curio`, `shrine`, `trap`, `wild`, `merchant`, `unknown`); characters in rooms (a named trader in `merchant`, a captive in `wild`'s cage variant, a chronicler at a `shrine`); **story chains advance** through the priority tier. It plugs into party-dungeon's room-entry draw and answer route; it does not build them | `outcome-routing`, `cast-resolver`, `delve-live-rooms` (Owner ruling 2026-09-19 (round 3): was "party-dungeon live path (external)") | 4 |
| 18 | `world-events-host` | Per sector holding a host slot (`Shrine`, `Anomaly`, `Tear`, `Vault`, `Market`, `Wildland` — `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7`), fog-correct, in the `Events` phase through a seam the turn engine calls; a **typed event vocabulary** added to `TurnReportKinds` (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10`) with playback translation rows filed on world-stage's `world-playback`; the quiet share of turns; a choice is the world command kind **`event.choose`**, added to `WorldCommandKinds` (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:7`), admitted through `WorldCommandAdmission.Admit` (`WorldCommandAdmission.cs:17`) and resolved at End Turn — deterministic and replayable like every order. Named warlords as characters (world-graph's roaming powers) | `outcome-routing`, `host-content-theta`, `cast-resolver`, `world-claim-loot` (Owner ruling 2026-09-20 (round 5)), `world-anomaly-sites` (Owner ruling 2026-09-20 (round 6)) | 4 |
| 19 | `petition-host` | Held-sector petitions on the sector's turn: a resident asks for what the sector needs, a clan's request **computed from world state** (never authored per clan, `world-graph-ideal.md` §8.2). Surfaces through world-stage's `world-inspector` and the notify rail as a filed ask | `world-events-host`, `world-claim-loot` (Owner ruling 2026-09-20 (round 5)); clan policy and real needs (external) | 4 |
| 20 | `expedition-lead-host` | An encounter chance per expedition tick (`expeditions.v{n}` tunable; `WildCreatureMet` is the natural host, `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:13`), **resolved at dispatch** like every tick and sealed; delivered at collect as a **log line in the collect summary** plus a lead (a character met, a rumor, a quest offer), never a modal. The idle clock never blocks | `outcome-routing`, `host-content-theta` | 4 |
| 21 | `sanctum-hub-host` | Homeworld conversations after an outing, on entry: Hourbloom, companions and visitors, **one conversation per character per return**, reacting to the outing (a wipe, a win, a lost sector); played through `scene-script-loader`. Holds the onboarding slot "first character met" asked of the first-session spec | `scene-script-loader`, `character-registry`, `storylet-selection` | 4 |
| 22 | `spine-progress` | The spine as data: chapter eligibility from save-scoped facts (a time-machine piece recovered per world won, R3), spine beats at the top tier, `chapter.reached` facts; after the last chapter, arcs and texture continue (no ceiling). History fragments placed in vaults, shrines and delve caches as storylets | `story-ledger`, `storylet-selection`, `scene-script-loader` | 4 |
| 23 | `failure-branches` | Failure facts written by **reading durable records other programs already commit** — a sector lost (turn report), a delve wiped (the Delve's close record), a siege failed (the siege result) — never by hooking their code; each fact makes priority storylets eligible (a questline, a character, a branch place with a way back). Never takes back what the rules let the player keep | `story-ledger`, `storylet-selection` | 4 |
| 24 | `counter-doctrine` | Per world: **the reading** (aggregate element share, deploy modes, action tags, sector kinds taken — never an individual encounter; Owner ruling 2026-09-20 (round 5), R18: **fog-correct** — only what the antagonist's faction observed: its `Intel`-phase record of sectors and forces, and battles it fought or saw, never a battle's outcome); **the study bar**, advanced each End Turn in the `Events` phase while a lean persists; **the doctrine**, adopted from a closed reviewed vocabulary when the bar fills, for a stated window, changing **what** the antagonist's faction fields (species drawn, element mix, order weights), never how strong; **the voice** through `scene.play`; **the counter-play** (change strategy to slow the study, raid a study site at an `Anomaly` or `Vault` to set it back). The doctrine is consumed by world-map-program's faction policy as an input (filed ask). Registry rows and guard tests for the six anti-Nemesis rules | `world-events-host`, `story-ledger`, `scene-script-loader`, `character-registry`, `world-anomaly-sites` (Owner ruling 2026-09-20 (round 6), R21: study sites exist on the map) | 5 |
| 25 | `narrative-readings` | Local reports only, no upload: **pick rate** per option per storylet (an option nobody or everybody takes flags the storylet for review); **success readings** — beats per hour of play per place, first-repeat distance per pool, share of storylets that offered a roster or supply option, share of sessions that met a named character; the pool-to-pulse **repetition budget** per host. Readings guide content volume; none is a test assertion | `story-ledger` | 5 |
| 26 | `storylet-card` (FE) | The band-2 storylet card over the current stage (generalizing the Delve's `EventPanel`, whose placeholder comment is stale — `gk-web/web/fusion-rpg-web/src/stages/delve/layers/EventPanel.tsx:10-17`): situation, choices with their odds and costs, rendered through `narrative-text`. Designed through `/idea-ui` first | `outcome-routing`, `narrative-text` | 6 |
| 27 | `quest-log-layer` (FE) | The quest log as a layer openable from any stage: quests, cast met, story so far. Designed through `/idea-ui` first | `quest-log-contract`, `narrative-text` | 6 |
| 28 | `delve-live-start` | Owner ruling 2026-09-19 (round 3): absorbed from party-dungeon. The Delve becomes **startable**: a boot caller for `ImportDungeonDomains` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:225`, never throws, the `PassiveTreeImportRunner` precedent); the five throwing live delegates of `POST /api/delve/start` filled from built pieces so it reaches `CreateDelve` (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:229-249`); the quest offer drawn and persisted at `CreateDelve` (`WriteQuestOffer`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:517`, test-only today) and a tracker route. Wiring only; every rule stays party-dungeon's. Spec: `spec-delve-live-start.md` | `host-content-theta` (the one `ParentWorldTerms` producer — Audit 2026-09-19: was "—"; the spec's own parent-terms read would have been a second producer) and party-dungeon's built code | 1 |
| 29 | `delve-live-rooms` | Owner ruling 2026-09-19 (round 3): absorbed from party-dungeon. A started delve's rooms **play**: a room-entry route (the first production caller of `MoveParty` and `MarkRoom`), the event draw at entry with its seen writes (`RecordEventSeen`) and the real pack-sourced `holdsOverrideStock` fact, the answer route `POST /api/delve/rooms/{id}/answer`, and event text on the wire as keyed `NarrativeTextDto`s (`EventView` carries none today, `gk-web/web/fusion-rpg-web/src/contract/types.ts:1276-1282`). ~~a legacy row stays text-`Pending` until `delve-event-regen`~~ Owner ruling 2026-09-19 (round 4): players never see a blank event — narrative-seed's wave-0 `dungeon-generator-repair` regenerates the legacy events clean and keyed, and they render through `narrative-text`'s codegen bridge from day one; wave-6 `delve-event-regen` later replaces them with storylets. Spec: `spec-delve-live-rooms.md` | `delve-live-start` (a real delve to play), `narrative-text`, narrative-seed `dungeon-generator-repair` (external: the repaired, keyed legacy corpus) — Owner ruling 2026-09-19 (round 4) | 1 |
| 30 | `world-claim-loot` | Owner ruling 2026-09-20 (round 5), R17: absorbed from world-map-runtime's `sector-loot-wiring` Part A. **Prerequisite of the world hosts' rewards.** Turns `ClaimResolver`'s inert `claim.loot:` seam on (passes `powerTuning` into `TurnEngine.Step` at commit and replay) and mints each player claim's loot in a post-Step pass of `CommitWorldTurn`'s transaction through the **existing** loot pipeline (`LootPipeline.Resolve`, `LootMintAt` → `Instantiator.TryInstantiate`, `PersistLootUnlocked`) — never a second roller; seed `WorldSeed.DeriveRollSeed(worldSeed, "loot:world-claim", "{worldId}:{sectorId}")`; content level `mapLevel(DangerBand)`, the shipped `world-sector` row; dedupe on the durable claim fact, once per sector per world (a reclaim of cleared ground pays nothing; template sector ids repeat across worlds, so the key is world-qualified); only the player's claims mint; sinks named (salvage → crafting and fusion materials; relics → wonder cost). Exposes the one mint the narrative settle pass uses to **take** a line with a payout's window (R14), and runs after that pass. Reviewed with world-map-program (commit, replay, `RulesetVersion`) and the item program. Owner ruling 2026-09-20 (round 6): R22 — it also re-seeds the mythic claim bonus from `WorldSeed.DeriveRollSeed(worldSeed, "claim.mythic", sectorId)` instead of the turn number, with replay and independence tests (spec §7). Spec: `spec-world-claim-loot.md` | built external code only (`ClaimResolver`, `WorldSectorLootSource`, the loot pipeline) | 1 |
| 31 | `world-anomaly-sites` | Owner ruling 2026-09-20 (round 6), R21: pulled into this program. `storm`, `nexus` and `barren` gain `anomaly` in `SectorTypeCatalog`'s allow-lists (validation only, `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:246-248`), and **new template versions** place unguarded anomaly slots on `first-light`'s `black-gate` and `ash-waste` and `two-hearths`' `corridor-4`; existing worlds keep their stamped version and are untouched (world-continuity `world-creation` §5 rule 1). Reuses `SlotValueCatalog`'s anomaly value; no new number. Makes `world.anomaly` and the doctrine study sites reachable. Kept apart from `world-claim-loot` (map content vs a commit-path mint; different reviewers). Spec: `spec-world-anomaly-sites.md` | built external code; the template half waits on world-continuity's versioned rebuild (`WorldCreation.Rebuild`, not built) | 1 |

### Dependency direction

One way, no cycles:

```text
narrative-vocabulary ─┬─ storylet-reseam ─ storylet-contract ─┐
                      ├─ story-ledger ─ relation-ledger ──────┼─ character-registry ─ cast-resolver
                      │                                       │         │
                      │                         narrative-predicates ───┘
                      │                                       │
                      ├─ narrative-text ─ scene-script-loader │
                      │                                       ▼
host-content-theta ───┴──────────────────────────── storylet-selection
                                                              │
                                   choice-resolution ─────────┘
                                          │
               quest-sources ─── outcome-routing ─── quest-log-contract
                                          │
      delve-host · world-events-host · expedition-lead-host · sanctum-hub-host
      spine-progress · failure-branches · petition-host (after world-events-host)
      (world-events-host and petition-host also after world-claim-loot, which depends on nothing here)
                                          │
                       counter-doctrine · narrative-readings
                                          │
                          storylet-card · quest-log-layer (FE)
```

`storylet-reseam` depends on nothing, so it can land before or after party-dungeon's open event-deck tasks: it is a pure move, and whichever lands second carries the other's code along. Owner ruling 2026-09-19 (round 3): the same holds for `delve-live-rooms`: its call sites move with the re-seam, whichever lands second. Order: `delve-live-start` → `delve-live-rooms` → `delve-host`. Owner ruling 2026-09-19 (round 4): `delve-live-rooms` also waits for `narrative-text` (moved to wave 1) and for narrative-seed's wave-0 `dungeon-generator-repair`, so its event text is keyed and clean from its first release; `delve-live-start` follows `host-content-theta` (Audit 2026-09-19). Owner ruling 2026-09-20 (round 5): `world-claim-loot` depends on no module of this program (only on built claim and loot code), and `world-events-host` and `petition-host` depend on it, because their rewards take its claim rolls (R14, R17).

---

## Build order

```text
Wave 0  narrative-vocabulary                      (after narrative-seed's registries exist)
Wave 1  storylet-reseam → storylet-contract ∥ story-ledger → relation-ledger ∥ narrative-text ∥ host-content-theta → delve-live-start → delve-live-rooms (after narrative-text and narrative-seed's dungeon-generator-repair; Owner ruling 2026-09-19 (round 3) and (round 4))
        ∥ world-claim-loot                        (Owner ruling 2026-09-20 (round 5), R17: before world-events-host and petition-host)
        ∥ world-anomaly-sites                     (Owner ruling 2026-09-20 (round 6), R21: before world-events-host and counter-doctrine;
                                                   template half after world-continuity's versioned rebuild)
Wave 2  character-registry → cast-resolver ∥ narrative-predicates → storylet-selection
        scene-script-loader (after narrative-text, now wave 1)
Wave 3  choice-resolution ∥ quest-sources → outcome-routing → quest-log-contract
Wave 4  world-events-host ∥ expedition-lead-host ∥ sanctum-hub-host ∥ spine-progress ∥ failure-branches
        delve-host (after delve-live-rooms) · petition-host (waits on clan needs)
        world-events-host and petition-host after world-claim-loot (Owner ruling 2026-09-20 (round 5)); world-events-host also after world-anomaly-sites (Owner ruling 2026-09-20 (round 6))
Wave 5  counter-doctrine ∥ narrative-readings
Wave 6  storylet-card ∥ quest-log-layer            (each after its /idea-ui gate)
```

**Why this order.** Model-free, contract-first: registries, a pure move, a loader and two ledgers produce value with no content and
make every later host testable against a fixture corpus. The two ledgers come before characters because a character's memory and relation
are ledger facts, not columns. Selection comes after predicates because tiering and specificity count matched conditions. Hosts come
last among Core modules because each is a thin adapter — a place decides **when** to ask, never which storylet or what it pays. The
world, expedition and homeworld hosts do not depend on the Delve's live path, so the program reaches players there even while it is
open. Owner ruling 2026-09-19 (round 3): the Delve's live path is wave 1 here: it wires built party-dungeon code, needs no module
of this program, and makes `delve-host`'s G5 reachable by the time wave 4 starts. Counter-doctrine follows the world host because
its study bar advances in the same phase. FE is last because each layer is a read model of modules above it.

---

## Gates

| Gate | Proves | After |
|---|---|---|
| **G0 — approval** | This map approved; the drafted `decisions.md` rows below appended in their owners' changes; the propagations below made | before any module spec |
| **G1 — one engine** | `storylet-reseam` moves the engine with every existing event-deck test green unchanged; **all battle, expedition and world goldens byte-identical**; `storylet-contract` loads today's corpus in its legacy shape and a fixture corpus in the widened shape; preflight rejects a dangling `chainRef` | wave 1 |
| **G2 — corpus honesty** | The preflight's dangling-`chainRef` failure lands no later than narrative-seed's regenerated corpus, so the committed corpus is never silently accepted (today two chains dangle — ideal §3.4). If the regeneration is later, the failing rule ships with the corpus marked as a named, owned content defect rather than a skip | wave 1, coordinated with narrative-seed |
| **G3 — a storylet resolves** | With the game closed, a fixture storylet is selected on a fixture host by tier and specificity, a choice is answered (contest odds shown; a `fight` reaches a battle mode through `BattleRequest`), every outcome kind routes through its existing path, rewards draw from the host budget with a dedupe key, and the pick is in the story ledger. Deterministic on replay from the same seed and ledger | wave 3 |
| **G4 — places play** | Owner ruling 2026-09-20 (round 5): a player claim mints its loot once through the loot pipeline and a world payout takes a claim line, never adds a roll (`world-claim-loot`). The world host fires in the `Events` phase, fog-correct, and an `event.choose` order resolves at End Turn; world goldens byte-identical when no world storylet is eligible, and any golden that moves with content on is re-blessed in the same change under world-map-program review. An expedition lead arrives in a collect summary with expedition tier hashes unchanged at encounter chance 0. A hub conversation plays once per character per return | wave 4 |
| **G5 — the Delve plays** | Once `delve-live-start` and `delve-live-rooms` land (Owner ruling 2026-09-19 (round 3): was "party-dungeon's live path"): a live delve draws a storylet on room entry, a named character appears in a room, and a chain link follows its predecessor. Proven through real `/api/delve/*` routes against a real delve row (RPG Server scope, `docs/contributing/live-probe-standard.md`), never a fabricated room | after `delve-live-rooms` and `delve-host` |
| **G6 — doctrine** | A sustained lean **the antagonist observes** advances the study bar, and one kept out of his sight does not (Owner ruling 2026-09-20 (round 5), R18); a doctrine changes the antagonist's species and element draw and order weights and never a magnitude; the six anti-Nemesis guards pass | wave 5 |
| **G7 — played surfaces** | The storylet card and quest log pass their `/idea-ui` gates and the band guard; no engine vocabulary on either surface; every string resolves through lingui with tokens rendered from the names registry | wave 6 |

---

## Ownership splits (binding)

| Concern | Owner | Must not |
|---|---|---|
| The storylet engine (catalog, deck, draw, outcome resolver, preflight), after the re-seam | **npc-story-events** | Leave a copy under `Delve/Events/`; let any place keep a private deck |
| The Delve's live path: domain import caller, `/start` reaching `CreateDelve`, `MarkRoom` caller, room-entry draw route, answer route, text on the wire, quest offer at `CreateDelve` | **npc-story-events** (`delve-live-start`, `delve-live-rooms`) — Owner ruling 2026-09-19 (round 3): was party-dungeon | Build a second route beside party-dungeon's; change a party-dungeon rule (deck, start refusals, preflight); take over what party-dungeon keeps — Delve content, engine rules, extraction and room-clear routes, quest verdicts at `CloseDelve` |
| Characters in Delve rooms, chain advancement in the Delve | **npc-story-events** (`delve-host`) | Change room kinds, the delve graph roll or delve battle profile |
| Seed contracts, registries, pipelines, validators, the corpus and its regeneration | **narrative-seed** | Edit a generated seed here; add a second registry file for a vocabulary narrative-seed owns |
| Runtime loading, casting, resolution, rendering, codegen bridge | **npc-story-events** | Call a model; decide a magnitude in text |
| Scene player, pieces, recipe, band-3 shell, `isSceneEligible` | **story-scene** | Build a second scene player; widen `ActorId` without story-scene review |
| Data-driven scene scripts, spine and hub scene eligibility from the story ledger | **npc-story-events** (`scene-script-loader`) | Change the frozen `rift-prologue`/version `1` contract |
| Turn engine, phase order, `RulesetVersion`, faction policies, clan policy and needs | **world-map-program** (`ai-commander`, `sector-development`) | Add a second turn loop; write a doctrine into `FrontierRulesPolicy` from here |
| World claim loot: the mint of `claim.loot:` lines after a committed claim (Owner ruling 2026-09-20 (round 5), R17) | **npc-story-events** (`world-claim-loot`), reviewed with world-map-program and the item program | Add a second roller or mint path; change a drop table, `ClaimResolver`'s rules or the pipeline from here |
| Event content in the `Events` phase, `event.choose`, typed event report kinds | **npc-story-events** (`world-events-host`), reviewed with world-map-program | Move a golden without that review |
| Map surfaces: playback translation, inspector actions, notify rail | **world-stage** (`world-playback`, `world-inspector`, `world-notify`) | Ship a raw event prefix to the player |
| The relation ladder (derivation, band rules) | **npc-story-events** (`relation-ledger`, R4) | Let trade-network or any program add a second relation scale |
| Relation-scaled spread, caravans, clan production, conquest consequences | **trade-network** (`counterparties`) | Be built here — this program gives a market a face, trade-network owns the exchange |
| Achievement evaluation, reward bundles, titles | **achievement-title** | Add a counter engine here; quest completion is evidence only |
| Player-routed push | **notification-ssot** | Add a push path here |
| Name clearance of character names and storylet titles | **ip-censor** (release gate, IC-3) | Add a second name filter here |
| Surface renames (prologue, guide, product-vision row, title) | **identity-rename** | Be done here |
| The first-session reveal sequence | `standalone/spec-first-session-progression.md` | Be edited here — this program asks for one slot |
| Loyalty and its decay rates | the contracts program | Be decided here (ideal §9) |

---

## Explicitly out

| Out | Why / owner |
|---|---|
| Recurring antagonists who remember, grow or rank | R13; replaced by `counter-doctrine` |
| Branching dialogue trees (ink, Yarn Spinner) | Ideal §6.11 |
| Any model call at runtime; free-text player input | Principle 12; narrative-seed §3 |
| Daily or weekly quests on a real calendar; time decay of relations | Principle 4; ideal §6.4 |
| Reputation or disposition as a spendable currency | Principle 8; ideal §6.11 |
| Relationship stat bonuses by default | Principle 9; a later design answers the five actor-layer questions first |
| Scenes during a lawn match; lawn-only quest objectives | Principles 1–3 |
| ~~The Delve's live-path wiring~~ | ~~party-dungeon~~ — Owner ruling 2026-09-19 (round 3): now in scope (`delve-live-start`, `delve-live-rooms`) |
| Seed generation, prompt design, corpus content | narrative-seed |
| Visual design of the storylet card and quest log | `/idea-ui` before those two module specs |
| Voice audio, portraits, art direction | Ideal §9 |
| Surface renames and the title change | identity-rename |
| `decisions.md` edits | Drafted below; appended in each owner's change |

---

## Success criteria

### Contract checks (tests assert these; none pins a population)

- **One engine:** no storylet, event, deck or draw type remains under `gk-core/src/FusionRpg.Core/Delve/Events/`
  after the re-seam except the Delve host adapter; a guard fails a second `*Deck`/`*Draw` selection
  type outside the engine namespace.
- **Closed vocabularies:** host kinds, roles, fates, choice kinds, consequence kinds, story fact kinds,
  doctrine ids and new predicate leaves are closed; each has a reviewed count stated with its reason
  (a declaration, not a reading).
- **Storylet preflight:** 2–4 choices, exactly one `leave`; no lose-lose; no dominated choice; a
  conditional choice at least as good as the best unconditional one; every role used is declared; no
  dangling `chainRef`; no storylet gates a boss; no digit in text; every token from the closed grammar.
- **Determinism:** the same seed, ledger and corpus revision select and resolve identically; narrative
  streams are named and never shared with a combat stream.
- **Revision pinning:** an arc started on revision `r` resolves against `r` after the corpus moves to
  `r+1`; a withdrawn id is a tombstone and is never reused.
- **Facts-only relations:** advancing turns, rooms or collects with no relation fact leaves every band
  unchanged; replay recomputes every band from facts.
- **Faucet discipline:** every payout carries a dedupe key from a durable fact id and draws from its
  host's budget; no grant path is added. Owner ruling 2026-09-20 (round 5): a world turn's item rolls equal its
  minted claim lines, whether a claim or a narrative payout took each (`world-claim-loot`).
- **Actor numbers:** no module writes an actor number; a doctrine changes selection and weights only.
- **Anti-Nemesis:** an enemy-role character's level, traits, rank and title are unchanged by any
  encounter outcome; no enemy line is keyed on that enemy's own encounter history; no enemy hierarchy
  type exists.
- **Standalone:** every host's end-to-end test runs with the game closed; no objective template reads a
  lawn-only fact.
- **Tokens:** every seed renders against two different name sets and the outputs differ exactly at the
  tokens; no names-registry display string appears literally in any text field.
- **Mint-first:** a joined character's `instanceId` is the specimen that talked to the player; a fallen
  world freezes its cast byte-identically (nothing deleted or retired), and a hibernating world keeps its cast dormant (Owner ruling 2026-09-19 (round 4), replacing round 3's "no unretired specimen").

### Readings (reported by `narrative-readings`, never asserted)

Beats per hour of play per place · first-repeat distance per pool against the pool-to-pulse budget ·
pick rate per option per storylet · share of storylets that offered a roster or supply option · share of
sessions that met a named character · corpus size per host kind.

---

## `decisions.md` rows to draft at spec time

Drafted here for approval; appended by the change that lands each. This map does **not** edit
`decisions.md`.

| # | Row | Draft text |
|---|---|---|
| **NS1** | One storylet engine | *"**Every place draws encounters from one storylet engine** (npc-story-events, 2026-09-19). The Delve's event engine is re-seamed to a place-neutral namespace; the Delve, the world `Events` phase, held-sector petitions, expedition returns and the homeworld are **hosts** that decide when to ask, never which storylet or what it pays. A per-place deck is the dual-engine defect SOLID forbids."* |
| **NS2** | One relation ladder | *"**Characters and factions share one 4-band disposition ladder** (`eager, open, wary, hostile`), derived from append-only facts, never stored as a number, never moved by time (owner ruling R4, 2026-09-19). After a creature joins, its relation is `LoyaltyRank`. trade-network's relation scaling reads this ladder. Relationships grant access, not stats."* |
| **NS3** | Story ledger | *"**One story store with save and world scopes** records narrative facts, `(storyletId, revision)` pins and picks. It generalizes the onboarding story rows and the Delve's event-seen scopes; no third parallel store. Seed ids are tombstoned, never reused."* |
| **NS4** | Characters | *"**A character is a minted specimen with a name, held by a non-player owner row** (the Zomboss player-row precedent). Joining the roster is an ownership transfer. Save-scoped characters cross worlds; world-scoped characters live as long as their world exists and are never deleted: dormant while it hibernates, frozen (read-only) once it falls."* (Owner ruling 2026-09-19 (round 4); replaces round 3's "retire when it falls or is abandoned") |
| **NS5** | Narrative names are tokens | *"**Story text names entities by token, never by display string** (owner rulings R8–R11, 2026-09-19). A names registry per locale maps tokens to display strings with closed grammatical feature tags; the leads are the Garden Keeper, Hourbloom and the Rotwright. Surface renames and the title (R9, R12) are the identity-rename program's rows."* |
| **NS6** | Counter-doctrine, no recurring antagonist | *"**The antagonist adapts at faction level to the player's aggregate strategy, never individually** (owner ruling R13, 2026-09-19). Six rules bind this program and world-graph's warlords: no enemy grows from meeting the player; no enemy hierarchy; no enemy remembers the player personally; no enemy base built from an enemy's traits; no sharing of enemy data between players; warlords grow by world rules only. A doctrine changes what a faction fields, never how strong."* |
| **NS7** | Leave in every storylet | *"**Every storylet carries exactly one `leave`** (narrative-seed §6.2 validator), superseding party-dungeon's event rule *'`leave` only on `kind: story`'* (`party-dungeon/spec-event-deck.md:50,205-206`; `EventChoices.cs:15-16`). Dominant or free choices are rejected by the widened contract's no-lose-lose, no-dominated-choice and conditional-choice rules instead."* Needs party-dungeon's concurrence in the same change (see *Conflicts found*) |
| **NS8** | World event orders | *"**A world storylet choice is the world command `event.choose`**, admitted through `WorldCommandAdmission` and resolved at End Turn like every order; world event report entries use typed kinds in `TurnReportKinds`, each with a playback translation row."* Joint with world-map-program |

---

## Conflicts found and propagations owed

Evidence rule 6: a correction that lands in one document and not its siblings has not landed.

1. **Leave rule (NS7) — approved by the owner 2026-09-19 with the map.** The party-dungeon program's own spec update still lands NS7 in `spec-event-deck.md`.** The widened storylet contract requires one `leave` in every storylet
   (`narrative-seed-ideal.md:337`); party-dungeon's shipped rule presents `leave` only on `kind: story`
   (`EventChoices.cs:15-16`, `EventChoices.cs:23-31`; `party-dungeon/spec-event-deck.md:50,205-206`).
   Both are approved documents; the later one widens the contract deliberately and replaces the free-leave
   guard with stronger validators. The amendment lands in `storylet-contract` together with party-dungeon's
   spec text, not silently in either.
2. **story-scene's out-of-scope row** still lists *"Dr. Zomboss as a v1 actor | Deliberate story
   deferral"* (`story-scene-map.md:177`). R2 lifts it for this program; the row gains a pointer to R2 in
   `scene-script-loader`'s change. (The "Dr. Zomboss" wording itself is identity-rename's.)
3. **Stale web comments.** `EventPanel.tsx:10-17` says *"`EventResolution`/`EventDeck` do not exist
   anywhere in `.cs` source"*; both exist (`EventDeck.cs:218` returns an `EventResolution`). Fixed in
   `storylet-card`'s change (ideal §3.2 already records it).
4. **The world turn report vocabulary** is five kinds (`TurnReport.cs:3-10`); world-stage's playback
   table must gain a row for every typed event kind `world-events-host` adds, filed as an ask on
   `world-stage-map.md` `world-playback`.

---

## Open questions

**None owner-facing.** Every question the ideal raised is answered by R1–R13 and the §11 enrichment
resolutions. Items the module specs must answer in their own text, by principle and not by owner
decision: tunable starting values (ideal §7); the exact migration shape that folds the onboarding story
rows and Delve event-seen scopes into `story-ledger` without changing `rift-prologue`/`1`; each host's
`Θ_content` inputs; the expedition encounter chance's home in `expeditions.v{n}`.

---

## DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: product vision and loops, the Delve, world map,
    world stage, expeditions, quests, achievements, story-scene, economy, power, tunables,
    effects (predicate leaves), battle, actor layer, UI, standalone, live probe.
[x] Session boundary recorded: tasks/sessions/narrative-programs-spec-20260919.json lists this file
    in its paths (docs only, direct mode, features/mega-merge).
[~] I read the §1 row docs this session: DESIGN-GATE itself (§1 rows, §2, §3, §5), the ideal in
    full, narrative-seed-ideal §6.1–§6.9 and §7–§11, the story-scene, party-dungeon and world-stage
    maps, the achievement-title, notification-ssot and ip-censor maps (module tables),
    trade-network-ideal §7.4, effect-atom/definitions.md §3 (predicates), decisions.md rows 52, 53,
    107, 109, 110. Not read in full this session: battle-engine-ssot.md, actor-layer-compose-ideal.md,
    the world-map runtime specs, game-gui-principles.md, the economy SSOTs, live-probe-standard.md.
    This map relies on their locked rows as quoted in DESIGN-GATE §1 and decisions.md; each module
    spec that touches one reads it first.
[x] I checked decisions.md for locks: Standalone-first (:107), Product vision (:109), Game GUI
    (:110), Actor layer stack (:52), Battle engine SSOT (:53), PvzActivity (:28). Nothing here
    contradicts them; NS1–NS8 are drafted, not appended.
[x] Every factual claim cites file:line, re-checked against code this session.
[x] audit-doc-citations.py --scope on this doc: see the report run with this change.
[x] I verified claims against code, not comments: ImportDungeonDomains, MarkRoom, RecordEventSeen,
    WriteQuestOffer, EventDeck/EventDraw/OutcomeResolver/QuestOffer callers (grep over src/),
    EventSeedFile's refusal, the Delve route list, Program.cs hosted services, TurnEngine's Events
    phase, FactionPolicies, LeafId, EventChoices' leave gate.
[x] I read the surrounding section of every rule quoted (the leave rule's spec section and its
    code; the Events phase body; the scene-trigger narrowing rule).
[x] No constraint reported as "moves goldens" or "needs sign-off" was assumed. Golden stability is
    stated as a gate to prove (G1, G4), not as a claim; nothing was run because this is a map.
[x] Nothing contradicts a §2 invariant.
[x] Propagations owed are listed (Conflicts found); none is made here because each file is outside
    this session's paths.
[x] No assertion pins a population. Closed vocabularies are named as declarations; corpus size, cast
    size and pick counts are readings.
[x] No event-refreshed cache is introduced. The relation band is derived on read from facts; if a
    spec adds a cache, it lists every trigger including the fact-append edge (§2.16).
[x] No acceptance criterion fixes an ordering that can vary: revision pinning and facts-only
    relations are stated order-independent; the leave amendment and corpus regeneration are an
    explicit coordinated gate (G2).
[x] Actor numbers: no module produces or consumes an actor magnitude beyond reading Θ for contests;
    relationships grant access; any future stat effect goes through ActorHub.
[x] No SOLID-violating parallel path: one engine, one quest engine, one ladder, one personality
    vocabulary, one scene player, one story store.
[ ] New rule registry rows: NS1's single-engine guard and NS6's anti-Nemesis guards need rows in
    gk-core/scripts/enforcement-registry.v1.json; they are written with the storylet-reseam and
    counter-doctrine specs.
```

## Standards audit (2026-09-19)

Independent audit of this map and fourteen of its specs (`narrative-vocabulary`, `storylet-reseam`,
`storylet-contract`, `story-ledger`, `relation-ledger`, `host-content-theta`, `character-registry`, `cast-resolver`,
`narrative-predicates`, `storylet-selection`, `narrative-text`, `scene-script-loader`, `delve-live-start`,
`delve-live-rooms`); each spec carries its own findings table. Findings on the map:

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Owner ruling 2026-09-19 (round 4): locked assumption 9, rows 4 and 7, the cross-program world row, NS4 and the mint-first criterion said world state "retires when fallen or abandoned" with an ask on `world-state-vocabulary` | **Fixed:** never deleted; live / dormant / frozen; no abandoned state |
| 2 | high | Owner ruling 2026-09-19 (round 4): row 29 planned legacy Delve events as text-`Pending` | **Fixed:** keyed, clean legacy text from day one; `delve-live-rooms` depends on `narrative-text` (moved to wave 1) and narrative-seed's `dungeon-generator-repair`; order stated in *Dependency direction* and *Build order* |
| 3 | high | Row 5 kept "the conversion of disposition into a starting `LoyaltyRank`" after the owner answered (a) (every join at the normal rank) — a relationship-to-actor-number path | **Fixed** |
| 4 | high | Row 28 said `delve-live-start` depends on nothing, while its spec built a second `ParentWorldTerms` producer beside `host-content-theta`'s | **Fixed:** depends on `host-content-theta`; the spec delegates |
| 5 | medium | Row 9 said "the lead's level band" (a private `f(level)`) | **Fixed** |
| 6 | low | The cross-program route list for the Delve named two of the four `DelveEndpoints.cs` routes | **Fixed** |

**Deferred, with owner of the fix (outside this audit's fence):**
- ~~`spec-quest-sources.md`, `spec-quest-log-contract.md`: world-fall closes quests `quest.failed` / shows retired
  characters — under round 4 they are frozen.~~ **Resolved** (`8ef48956`, round 4): `spec-quest-sources.md` §4 world
  table (dormant pauses, fallen closes as `quest.failed {cause: world-fallen}`, nothing deleted);
  `spec-quest-log-contract.md` §2 `paused`/`failed` states.
- ~~`spec-quest-log-contract.md`, `spec-expedition-lead-host.md`: `TextRefDto` is a second wire text shape beside
  `NarrativeTextDto` (SOLID S).~~ **Resolved** (`b42d77f4`, Alignment 2026-09-20): both use `NarrativeTextDto`.
- ~~`narrative-seed/spec-storylet-vocab.md` §3.4: proposed leaf names must follow `narrative-predicates`
  (`RelationBandAtMost`, `StoryFlagSet`) and gain a `lead-level-at-least` condition; a hub-conversation seed kind is
  missing for `sanctum-hub-host` (`spec-scene-script-loader.md` §1).~~ **Resolved** (`b42d77f4`, Alignment
  2026-09-20): one seed-id → leaf table in `spec-narrative-predicates.md` §5; hub conversations are `sanctum.hub`
  storylets plus `return-*` character lines (`narrative-seed/spec-storylet-vocab.md` §3.1,
  `spec-character-vocab.md` §5–§6). The eight `world.*`/`expedition.return` seed host rows and the fragment seed
  fields (`spec-spine-progress.md` §6) followed in the next alignment pass (Alignment 2026-09-20).
- ~~`narrative-seed/spec-dungeon-generator-repair.md`: its "not in scope: regenerating the 54 committed events" is
  superseded by round 4.~~ **Resolved** (`6be537b2`, round 4: non-story events regenerated; widened by owner ruling
  R16 `ccc49d86`, applied in `b42d77f4`: all 54, the `story` events included with their committed `chainRef`s).
- `power/ssot-power-scale.md` §8 row 6: expedition content "authored as `Θ_content`" vs `host-content-theta`'s tier
  danger band through the one composer. **Still open** (outside both narrative programs' fences; Alignment
  2026-09-20).

**Proposed enforcement-registry rows** (collected; the shared registry is not edited here):
`ns1-one-storylet-engine` (guard `StoryletEngineSingleSourceTests`), `ns2-one-relation-ladder` (new Guard.Tests scan),
`ns2-relations-access-not-stats` (Narrative contract test), `ns3-story-ledger-append-only` (Data text scan),
`ns3-story-sql-in-data` (`gk-core/scripts/guard-dal.py`), `ns-world-scope-never-deleted` (append-only scan + lifecycle test),
`ns5-names-are-tokens` (two-name-set render test), `ns6-no-enemy-growth` / `-memory` / `-hierarchy`
(`NarrativeNoEnemyGrowthTests`), R13 rule 5 no-sharing (`unguardableReason`: no upload path exists to scan),
`ns-narrative-streams-named`, `ns-narrative-leaf-context`, `ns-one-narrative-text-dto`, `ns-no-blank-event-text`,
`ns-one-scene-player`, `narrative-tuning-no-default`.

**Verification-boundary asks:** `core-narrative` (Core Narrative src/tests, `data/tuning/narrative*.v*.json`,
`gk-data/packs/fusion/data/seed/narrative/_registry/**`); `data-narrative` (`RpgStore.StoryLedger.cs`, `RpgStore.NarrativeCharacters.cs`,
`tests/FusionRpg.Data.Tests/Narrative/**`); a delve boundary for `DelveEventEndpoints.cs`, `DungeonDomainImportRunner.cs`,
`src/FusionRpg.Server/Delve/**`, `src/FusionRpg.Contracts/Delve/**`; a web boundary for
`web/fusion-rpg-web/src/features/narrative/**` (none exists for `web/**`).

`python scripts/audit-doc-citations.py` on this map and `docs/architecture/npc-story-events`: 0 HIGH findings; the
D1 rows are `(new)` files a spec proposes.

## Owner ruling 2026-09-20 (round 5)

Three rulings, R17–R19 (`npc-story-events-ideal.md` §10), applied to this map and its specs:

| Ruling | What changed | Where |
|---|---|---|
| **R17** — world claim loot is pulled into this program | New module row 30 `world-claim-loot` (wave 1), a prerequisite of `world-events-host` and `petition-host`; new cross-program gap row; ownership row; G4 and faucet criterion. The "owed until world-map adds the mint" wording is replaced by the dependency. The transfer of world-map-runtime's `sector-loot-wiring` Part A is recorded here as text only | `npc-story-events/spec-world-claim-loot.md` (new); `spec-outcome-routing.md` §3; `spec-world-events-host.md` §6; `spec-petition-host.md`; `spec-quest-sources.md` §6 |
| **R18** — counter-doctrine is fog-correct | Row 24's reading reads only what the antagonist's faction observed (its `Intel` record; battles it fought or saw; never an outcome); G6 | `npc-story-events/spec-counter-doctrine.md` §1, §2, §7, Testing |
| **R19** — world storylet climate is derived from the sector type (superseded by R20, Owner ruling 2026-09-20 (round 6)) | World hosts pass the sector type's climate from narrative-seed's closed `sector-climates.v1.json` (new) into selection; the Delve keeps its room climate; expedition hosts stay neutral (no destination sector) | `spec-world-events-host.md` §3; `spec-narrative-vocabulary.md` §1; `spec-petition-host.md`; `spec-expedition-lead-host.md`; `narrative-seed/spec-storylet-vocab.md` §3.1, §3.9 |

**Found while applying them (reported, not fixed here; Owner ruling 2026-09-20 (round 6): all three answered by R20–R22 below):** (1) no sector type allows an `anomaly` slot
(`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:55-102`), so `world.anomaly` fires nowhere today and counter-doctrine's
study-site raids are reachable only at a `Vault` — world-map's catalog decides that; (2) world sectors carry their own
era climate (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`) that can differ within a type — R19 follows the type,
and that choice is left open for the owner (`narrative-seed/spec-storylet-vocab.md` §3.9); (3) the mythic claim bonus
seeds from the turn number, not the world seed (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:142`) — filed on
world-map-program and left off by `world-claim-loot`.

## Owner ruling 2026-09-20 (round 6)

Three rulings, R20–R22 (`npc-story-events-ideal.md` §10), answering round 5's three findings:

| Ruling | What changed | Where |
|---|---|---|
| **R20** — world storylets read the sector's own climate | R19's `sector-climates.v1.json` (new) is retired (trail kept); world hosts pass `WorldSector.Climate` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`), the climate the world already uses for wild spawns, raised species and lane cost; one source of truth. The seed-side world grid takes all seven climate cells | `spec-world-events-host.md` §3; `spec-narrative-vocabulary.md` §1; `spec-petition-host.md`; `spec-expedition-lead-host.md`; `narrative-seed/spec-storylet-vocab.md` §3.1, §3.9 (superseded); `narrative-seed-map.md` §9 |
| **R21** — the Anomaly slot on some sector types | New module row 31 `world-anomaly-sites` (wave 1): `storm`, `nexus`, `barren` allow `anomaly`; new template versions place three unguarded anomaly slots; existing worlds untouched. Noted here only; no world-map file edited | `npc-story-events/spec-world-anomaly-sites.md` (new) |
| **R22** — mythic claim bonus seed | Folded into `world-claim-loot` §7: `WorldSeed.DeriveRollSeed(worldSeed, "claim.mythic", sectorId)`; replay, turn- and world-independence tests; the golden/stored-value effect is measured in the build (expected none: no production caller sets the rate) | `npc-story-events/spec-world-claim-loot.md` §7 |

**Still open:** no template places a `vault`, so doctrine study sites are anomalies only until template authoring adds
one; `world-anomaly-sites`' template half waits on world-continuity's versioned rebuild.
