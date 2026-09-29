# NPCs, story and events — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current, and so is its own map's.**
> [npc-story-events-map.md](npc-story-events-map.md) reads **"Map approved by the owner 2026-09-19
> ('approve, go'). Module specs authorized"** — but its own prose still marks the spec path
> `docs/architecture/npc-story-events/spec-<module-id>.md` as **"(new)"**. Measured directly against
> the tree today: **27** module specs already exist there. No `tasks/npc-story-events-todo.md`
> exists in this worktree yet.
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the module specs and the code directly — the map's own prose is stale here
> too.

**Status:** idea phase, 2026-09-19. Not a spec. No build authorized.
**Program id:** `npc-story-events`.
**Owner request (2026-09-19):** *"deploy agents for npc feature in this game, we have multiple game
mode include delve and world exploration, so it will very boring if don't have npc and story or
event."*
**How this was produced:** `/idea` (skill `idea-phase`). Five read-only survey agents (Delve, world
map and world stage, expeditions and quests, characters and story-scene, rules and economy seams) and
one prior-art research agent, under the owner charter recorded for this run. Every agent claim that
carries weight below was re-checked against code in this session. Three agent claims were wrong, and
§3.5 records the corrections.

**Sibling programs this must not fork:**

| Program | Owns | This program's relation to it |
|---|---|---|
| [story-scene](story-scene-map.md) | Scene presentation: `StorySceneHost`, cast, beats, cues, skip | **Consumes it** for every authored scene. Never a second scene player |
| [party-dungeon](party-dungeon-ideal.md) | The Delve loop, and the event deck, quests and wild talk it already wrote | **Generalizes its event engine** (§6.2). Owner ruling 2026-09-19 (round 3): the Delve's live-path wiring (start, room entry and draw, answer route, text on the wire, quest offer) moves to this program as `delve-live-start` and `delve-live-rooms`; party-dungeon keeps the Delve's content and the rest of its loop |
| [world-map-program](world-map-program.md) / [world-stage](world-stage-ideal.md) | Turn engine, turn report, notify rail | **Adds content** to the `Events` phase and the report. Never a second turn loop |
| [trade-network](trade-network-ideal.md) | Clans' trade centers, prices, relation-scaled spread, caravans | **Shares one relation ladder** with it (§6.4, owner question 4) |
| [achievement-title](achievement-title-map.md) | Achievement evaluator, reward bundles, titles | **Feeds it evidence.** Never a second counter engine |
| [notification-ssot](notification-ssot-map.md) | Player-routed push | **Posts through it** once it lands. Never a second push path |
| seedsmith (`gk-forge/tools/seedsmith`) | Offline content generation | **New adapters** for characters and storylets; seeds only, runtime casts per save |

---

## 0. Principles that constrain every choice below (restated, not linked)

A downstream session reads this document, not its links. Each rule below is stated in full because a
choice in §6 depends on it.

1. **Every RPG feature lives in the RPG layer, never in the PvZ game.** NPCs, dialogue, quests and
   events are RPG-layer systems: Core, Data, Server and web. Nothing here asks the PvZ game to know
   what a quest or a character is. The lawn contributes **observed facts** (`PvzActivityKinds`, 8
   kinds) and can host a fight. It never runs a story.
2. **Two async systems; record-then-drain.** The RPG never reads PvZ's current state. A story beat
   reacts to **past facts**: a turn report entry, a delve decision log row, a lawn activity fact.
   Delay is the designed degradation mode. A beat that fires one turn late is correct behaviour.
3. **Standalone-first is a capability rule.** Every NPC, quest and event must be playable with Fusion
   closed. A quest objective must therefore count a **mode-agnostic fact** (a kill from any battle
   source, source-tagged), never a lawn-only fact. The lawn may enrich; it never gates.
4. **Three clocks, not a fourth.** The lawn match clock, the idle expedition wall clock, and the world
   map's virtual turns. Story time rides these. **No daily quests on a real-life calendar and no
   "come back tomorrow" timers** — that is the diary meta-clock `the-loops.md` forbids.
5. **One power ladder.** A skill check (persuade, sneak, intimidate) is a **contest**: it reads
   `Θ_actor − Θ_content` through the shipped sigmoid-over-difference shape
   (`CombatProbability.Sigmoid`, `gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8`). A reward
   magnitude reads `P(Θ_content)` through the existing loot and price functions. A new `f(level)` is
   the defect. `ssot-power-scale.md` §10 is a closed inventory.
6. **The balance surface is data.** Deck weights, cooldowns, pity steps, disposition shifts and
   encounter chances live in `gk-core/data/tuning/<domain>.v{n}.json`, published as `v{n+1}` through the
   tuning tool. Display text lives in a catalog or seed file, never in the number file.
7. **No hard ceilings.** Nothing here caps a magnitude. Disposition bands are a bounded ladder
   (structural, and must say so in a comment). Rewards scale on `P(Θ)` without a ceiling.
8. **Every faucet names its sink; no stock without the registry.** An event pays in **existing**
   stocks (souls, essence, materials, items, recruits) through their existing grant paths with a
   dedupe key from a durable fact id. A new currency must land an `empire-resource-ssot.md` §3 row
   and pass P4 (a `min(x,y)` bottleneck) and P6 (two competing sinks) in the same change. **This
   program proposes no new stock.** Disposition is a derived band, not a spendable quantity.
9. **One ActorHub compose; the actor layer stack is closed to invention.** A character-granted buff
   is an atom container at an `OwnerScope`, or a registered `IActorStatSubsystem`. A relationship
   that changes an actor's numbers must answer the five layer questions (layer, scope, lifetime,
   carrier, SourceId) first. **This program's default is that relationships grant access, not
   stats.**
10. **The battle engine is the SSOT for every battle.** An event that starts a fight hands a
    `BattleRequest` or an `IIntentSource` to an existing battle mode. It never resolves damage itself.
    A mode may own its loop, never a mechanism.
11. **SOLID is binding.** One engine decides "which event happens here" for every place. The Delve
    already wrote that engine. A second deck for the world map would be the dual-compose defect again
    (`ActorHub` vs `BattleStatComposer`, fused 2026-09-13).
12. **Seed to concrete.** seedsmith emits seeds (character seeds, one per species that gets one; storylets). The runtime casts
    them into per-save concrete characters and events. LLMs author identity only: names, voice,
    flavor, and picks from closed lists. Every magnitude is table-owned.
13. **Generated data is never hand-edited.** A defect in a generated storylet is fixed in its
    generator and regenerated (§3.4 has two).
14. **A guardrail validates the contract, never a population.** The storylet corpus and the cast are
    populations that grow with content. Tests assert closed enums, joins, uniqueness and preflight
    rules, never "54 events".
15. **A game is a stage with layers.** A dialogue card is a band-2 panel over the current stage. A
    quest log is a layer, openable from anywhere, never a route. An authored scene uses
    `StorySceneHost` and its scoped GG-61 exemption (`size="scene"`) and nothing wider.

---

## 1. Which loop this extends

From [the-loops.md](../guide/the-loops.md). This is not a new loop.

| Loop | How this extends it |
|---|---|
| **7. Quests and events** (primary) | The loop's own status line names the gap: *"delve quests, world events and raids, player-facing **quest log** **Vision**"*. This program fills it |
| **6. The Delve** | Rooms get people and consequences: talkers, captives, traders, story chains |
| **4. World map — adventure** | Sectors get residents and turns get events. Clans get faces. The Rotwright gets a voice |
| **5. World stage — empire** | Held sectors get petitions and visitors. The Market slot gets a trader with a name |
| **2. Idle expeditions** | The loop's own Vision line: *"ticks that start quests and world events."* An expedition comes home with a lead |
| **3. Farm, hunt, defend** | *"Failure branches (Vision)"*: a lost sector or a failed extract opens a questline |
| **B. Creature summon and fusion** | A befriended character can join the roster through the existing wild-join intake |

The homeworld (Sanctum) is where story plays between outings. It is the spine's home ("Everything you
own lives at home"), not a new place.

---

## 2. What this is, in the player's language

The rift is inhabited. The Fracture did not only make monsters out of your lawn's plants and zombies.
Some of them woke up with names, grudges and plans. A peashooter hermit sells maps in a barren
sector. A clan of ice-marsh zombies wants a warcamp razed on their border. A captured Sunflower in a
delve cage remembers that you once let her sister go. Hourbloom tunes in between worlds to tell you
what she found. The Rotwright answers your strategy: lean on fire long enough and his armies come
back fire-proofed (§6.12).

Every place you play draws from one pool of **encounters**: short scenes with a situation and two to
four choices. Choices cost or pay what the game already runs on: souls, supplies, a creature's
loyalty, a fight. Some choices remember you. Some start a quest. Some change how a whole faction
treats you.

Over the top runs one **story**: the chase for the Rotwright and the pieces of his broken time machine.
Each world you win moves it forward; each world you lose can open a different path. It keeps going
across worlds, because you keep who you are.

Nothing here is a chore list. There are no dailies and no timers. Events happen **when you play** —
on a turn, in a room, when an expedition returns.

---

## 3. What already exists

The survey's headline: **most of the machinery is already written, and almost none of it reaches a
player.** The Delve holds a complete event deck, a quest engine, a talk tree with memory, and a store
of events seen — and none of it has a production caller. The world map has an `Events` phase and a
report pipe with no content in them. There is no character anywhere.

### 3.1 Built (works end to end today)

| What | Evidence |
|---|---|
| **Authored scene player.** `StorySceneHost`, linear beats, cast, cues, unconditional skip. The Rift prologue plays from a server-authoritative ledger | `gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx`; trigger at `gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx:90-94` calling `isSceneEligible` (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts:58-74`); ledger `OnboardingStoryRow` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs:25`). Beats are linear: `SceneBeat` (`sceneScript.ts:32`) has no branch field |
| **World turn pipeline with an `Events` phase.** Ten phases, deterministic, replayable | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` — `Events` phase body at `:341`: *"Calendar boundaries are rolled and reported; their effects belong to later modules."* |
| **Turn report as a fog-correct feed.** Audience-scoped and sector-scoped entries; web rail that flushes only on End Turn | `TurnReportKinds` (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10`: `command.accepted`, `command.dropped`, `calendar`, `event`, `battle`); `web/fusion-rpg-web/src/stages/world/notify/notifyRailStore.ts:3,13` (`blocking` state) |
| **Map-to-battle seam** | `BattleKinds` (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:6`: `Sector`, `Lane`, `Guard`, `District`) and `BattleRequest` (`:39`) |
| **Zomboss as a real commander** with a rules policy that files orders like any other commander | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs` |
| **Expedition ticks** — six closed kinds, sealed at dispatch, revealed at collect | `ExpeditionTickKinds` (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:7-15`), including `WildCreatureMet` (`:13`, emitted at `:140`) |
| **Creature personality and loyalty** — closed vocabularies with real rate effects | `LoyaltyRank` (`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:7`: Insubordinate, Bound, Sworn, Trusted, Devoted — derived, never stored); `CreaturePersonality` (`:18`: Loyal, Stoic, Proud, Calculating, Feral), rolled per specimen from `instanceId`; rates in `gk-core/data/tuning/contracts.v1.json` |
| **Onboarding checkpoints** — the one shipped ordered, level-gated milestone gate | `gk-core/src/FusionRpg.Core/Onboarding/OnboardingCheckpointEvaluator.cs:6-13` |
| **Lawn activity facts** — the only lawn events a quest may count | `gk-core/src/FusionRpg.Core/Activity/PvzActivityKinds.cs:6-13` (8 kinds). `decisions.md` PvzActivity row: *"Not RPG quests"* |
| **Grant paths with dedupe** | `AwardSouls` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:215`), `TrySpendSouls` (`:234`) |
| **Deterministic roll seeds** | `WorldSeed.DeriveRollSeed` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`); `SeededRng.DeriveStream` (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs`) |
| **One predicate engine** shared by atoms, actions and quests | `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateCompiler.cs` |
| **Atom containers at eight owner scopes** — the legal carrier for a timed boon or curse | `OwnerKind` (`gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20`); `ContainerKind` (`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:31`) includes `WorldBuff`, `Consumable`, `ActorTitle`, `EmpireTitle`. Vocabulary counts: 9 attach points, 18 kinds, 13 triggers (`AtomKindRegistry.cs:27,43,48`) |

### 3.2 Wiring gap (the machinery exists and is inert — not a wall)

| What | The inert line | What it would take |
|---|---|---|
| **The Delve cannot start live.** `dungeon_domain` is never populated, so `/start` refuses before `CreateDelve` | `ImportDungeonDomains` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:225`) has **zero production callers** (repo-wide grep, this session). Self-reported at `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:176` | Owner ruling 2026-09-19 (round 3): this program's `delve-live-start` (was party-dungeon's work). **Every Delve item below is unreachable until this lands** |
| **The Delve event engine has no production caller.** Catalog, deck, draw, outcome resolver and preflight are written and tested | `EventDeck`, `EventDraw.PickEvent`, `OutcomeResolver` and `EventCatalog.Load` are referenced only inside `gk-core/src/FusionRpg.Core/Delve/Events/` and tests. `RecordEventSeen` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:440`) and `MarkRoom` (`:379`, the only writer of a room's `event_id`) have no production caller (`DelveEndpoints.cs:168-169`: *"`RpgStore.MarkRoom`, still has zero production callers"*) | A room-entry route that draws, persists the draw, and a choice route that resolves it |
| **The web event panel shows placeholders only** | `gk-web/web/fusion-rpg-web/src/stages/delve/layers/EventPanel.tsx:10-17` renders each field's pending reason. Its comment says *"`EventResolution`/`EventDeck` do not exist anywhere in `.cs` source"* — **stale**: `EventDeck` exists | A wire DTO and an adapter; fix the stale comment in the same change |
| **Delve quests are never offered** | `WriteQuestOffer` (`RpgStore.Delve.cs:517`) is called only by tests. `quests_json` defaults to `'[]'`, so reward banking at close never fires. The HUD says so: `QuestTracker.tsx:6-8` | Call `QuestOffer.Draw` at `CreateDelve` and persist it |
| **Story chains are validated but never advanced** | `EventCatalog.cs:181-183` requires `chainRef` on `story` events; `EventDeckPreflight.CheckChainRefs` checks kind and cycles. No draw path reads `ChainRef` (`EventDraw.cs`, `EventDeck.cs`: no reference) | Draw eligibility that prefers the next link after the previous one was seen |
| **Wild talk is built but sits behind the unstartable Delve** | `TalkTree` verbs (`gk-core/src/FusionRpg.Core/Delve/Wild/TalkTree.cs:6`: Flatter, Threaten, OfferSouls, OfferSpirit, OfferSupply, OfferContract, Fight, Leave); `Disposition` over `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` (`eager, open, wary, hostile`); `WildMemory`; `RecruitMint`; routes `/rooms/{id}/talk`, `/cage`, `/pray` (`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:62-66`) | Nothing new — it goes live with the Delve |
| **Delve merchant sells nothing** | `DelvePrices.PriceUndesigned` (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:17`); `:46`: *"a merchant room opens as a sell-nothing rest"* | The item program's derived base price |
| **Achievements never evaluate in production** | `AchievementEvaluator` (`gk-core/src/FusionRpg.Server/Achievements/AchievementEvaluator.cs`) is not a hosted service: `gk-core/src/FusionRpg.Server/Program.cs:403` registers `EventIngest`, `CompactionWorker`, `UniqueActorDeployWatchdog`, `SimHeartbeatHost` only. Its trigger vocabulary already has `event-seen` (`AchievementRegistry.cs:25`) | Register it and give it evidence producers (achievement-title's work) |
| **Neutral factions exist in the vocabulary only** | `WorldFactionKind` (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7`: Player, Zomboss, Clan, Rival, Wild); `FactionPolicies.ById` (`gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13`) registers two policies, so a seeded `Clan` has no policy to resolve to | A clan policy (world-map / trade-network) |
| **Needs are flat** | `UniformNeeds` (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31`); `:29`: *"What is missing is the numbers, not the idea."* | Real needs per clan — the input a clan's request is computed from |
| **Map mobiles and slots with no mechanism** | `WorldEntityKind.Caravan` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:61`) is never constructed; `SlotKind.Shrine`, `Market`, `Anomaly`, `Tear`, `Vault` (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7`) are on shipped sector templates with nothing acting on them | Event hosts (§6.6) and trade-network's caravans |
| **Turn playback translates few event prefixes** | `world-stage-ideal.md` §2.2: *"Playback understands 5 of 21 event prefixes; the remaining 15 print raw"* (doc claim, not re-counted this session) | A typed event vocabulary (§6.6) plus its translation rows |
| **Lawn-side scene cues** | story-scene T27b is blocked by design (`tasks/story-scene-todo.md`) | Only matters for a beat that needs an in-game VFX cue |

### 3.3 Real gap (no mechanism anywhere)

| What | Why it matters | What must be built |
|---|---|---|
| **Characters.** No persistent NPC identity exists. A `merchant` is a room kind with a price function. Dave and Penny are two front-end rows (`actorCast.ts:67`, `ActorId = "penny" \| "dave"` at `sceneScript.ts:19`). Zomboss's player row (`RpgStore.ZombossDeploy.cs`) carries no identity | Without a "who", nothing can remember you, return, or join | A character record and a per-save cast (§6.3) |
| **Story state beyond onboarding and one delve.** No general story-flag store (`WorldFlag`/`StoryFlag`: zero hits). The only "seen" memory is the delve's three scopes (`RpgStore.Delve.cs:409-463`) | Arcs need to know what happened in earlier worlds and earlier turns | A story ledger with a save scope and a world scope (§6.7) |
| **World events.** The `Events` phase rolls only calendar boundaries. No anomaly, no era event, no failure branch type exists in `gk-core/src/FusionRpg.Core/World/` | The map has a heartbeat but no incidents | World hosts for the storylet engine (§6.6) |
| **Relations.** `WorldFaction` (`WorldState.cs:70`) has no relation field. `RelationKind` in Contracts is a targeting scope, not diplomacy. `spec-ai-commander.md` rules out diplomacy | Clans and characters cannot like or hate you | One relation ladder (§6.4) |
| **A quest log.** `the-loops.md` §7: *"A quest log you can open as a layer is a catalog gap today"* | Players cannot see what they were asked to do | A layer (§6.5), built through `/idea-ui` |
| **Quests outside the Delve.** The quest engine's only fact source is a `DelveReport` (`QuestProgress.cs:35-40`) | World and expedition quests need other fact sources | Fact sources per place, one engine (§6.5) |
| **A narrative localization path.** Story-scene decision S4 routes all player text through lingui. Seed-authored text (delve event `name`/`flavor`) is raw JSON with no path into the catalogs | Generated narrative is large; hand-copying it into lingui does not scale | Decide at spec (§9) |

### 3.4 Built, but defective (content)

| Defect | Evidence | Fix (never by hand) |
|---|---|---|
| **Chinese tokens leaked into English flavor text.** 53 of 54 delve event seeds contain CJK characters; e.g. *"a violent 分配 of essence … a sudden 攻击"* (`gk-data/packs/fusion/data/seed/dungeon/events/event.curio-creature.allpeater-001.json`) | Counted this session with a script over `data/seed/dungeon/events/event.*.json`. **The check already exists** — `language_consistency` (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py`), added 2026-09-08 after this very defect — but the generation retry loop never calls it: `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334` runs only `motif_coverage` and `anti_motif_violation`. The bulk batch predates the check and was never re-audited (corrected 2026-09-19; the first version of this row proposed building a check that exists) | Root cause is the prompt: themes carry Chinese motifs and the brief asks the model to use one (`adapters/dungeon/briefs.py:324`). Pass glossed motifs, widen and wire `language_consistency` into the retry loop at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334`, then regenerate ([narrative-seed-ideal.md](narrative-seed-ideal.md) §4.4, §8) |
| **Two of four story chains point at events that do not exist** (`…ashthreepeater-002`, `…dolldiamond-002`) | Root cause: the planner flattens every story cell in one run into a single cross-theme sequence and invents a `-{n+1}` id for the last entry (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:300-310`); two runs of two events each produced two invented ids. `EventDeckPreflight.cs:51-53` then skips an unresolved `chainRef` *"silently … rather than invented"* | Preflight treats a dangling `chainRef` as a failure. Chains are generated as whole arcs, so a link never points past the arc (see [narrative-seed-ideal.md](narrative-seed-ideal.md)) |

### 3.5 Corrections to the survey (recorded so no session repeats them)

- The Delve agent reported the event deck as **Built**. It is a **wiring gap**: no production caller,
  and the Delve itself cannot start.
- The characters agent reported **no narrative seedsmith adapter**. The dungeon adapter already
  generates event and quest `name`/`flavor` (`briefs.py:104-124,302-323`). What is missing is a
  **character** adapter.
- The rules-seams agent quoted **16** atom kinds from `effect-atom/definitions.md:37`. Code says 18
  (`AtomKindRegistry.cs:43`). Because `definitions.md` wins over any spec, its stale count was
  corrected in the same change as this document.
- `party-dungeon-ideal.md`, `achievement-title-ideal.md` and `docs/guide/delves-and-sieges.md` all
  carry status lines behind the code. Read them for reasoning, never for status.

---

## 4. Prior art

Researched 2026-09-19 from primary sources where reachable. **(2nd-tier)** marks a wiki, forum or
search-summary source; **UNVERIFIED** marks a figure that could not be confirmed. The repo already
holds some of this, and it is extended here, not repeated: `party-dungeon-ideal.md` §3.3 (Slay the
Spire, Darkest Dungeon curios), `party-dungeon/spec-event-deck.md` (band weights 1000/300/90/25/7,
pity, repeat scope), `species-progression-ideal.md:412` (RimWorld wealth scaling), and
`research/genre-mechanics/README.md` finding 7 (every decaying loyalty meter in that survey was
removed by its own studio). No `research/` file covers narrative, NPCs or storylets.

### 4.1 Selection and pacing

| Game | Mechanism and numbers | Documented failure | Lesson for us |
|---|---|---|---|
| **Slay the Spire** "?" rooms | Start at monster 10%, shop 3%, treasure 2%, else event. Each type not rolled gains its own step (+10/+3/+2) and resets when hit. Confirmed from code quotes ([forgottenarbiter](https://forgottenarbiter.github.io/Correlated-Randomness/)) — this closes the value `party-dungeon-ideal` §3.3 marked unverified. Shrine 25% chance: **UNVERIFIED** | Every random stream was seeded with the same value, so fight rolls and event rolls were correlated: after a non-Cultist first fight the first "?" room *had* to be an event | One derived stream per purpose. `DeriveStream` already does this; keep narrative streams separate |
| **Stellaris** anomalies | Chance = (5% + N × 0.5%) × (1 + bonuses), N = surveys since the last find ([wiki talk](https://stellaris.paradoxwikis.com/index.php?title=Talk%3AAnomaly&mobileaction=toggle_view_desktop)). "Situations" are a monthly progress bar with an event at each end | Scientist-vs-anomaly fail rolls were removed in 2.1; difficulty became research *time* **(2nd-tier)** | Price risk in cost or time, not in a hidden fail roll. A Situation bar is a ready shape for a story clock |
| **Crusader Kings 3** | Mean-time-to-happen removed; events fire on yearly/quarterly/5-year pulses from weighted pools, with `chance_of_no_event`, per-event `cooldown` and `weight_multiplier` ([CK3 wiki](https://ck3.paradoxwikis.com/Event_modding)) | "The same events over and over" — a pool too small for its pulse rate; players click through unread ([Steam](https://steamcommunity.com/app/1158310/discussions/0/3387291961152398998/)) | **Pool size ÷ pulse rate is the repetition budget.** Cooldowns from day one |
| **Total War: Warhammer** dilemmas | Trigger requirements + random chance + cooldowns (confederation: 5 turns) | Negative dilemmas back to back; lose-lose choices ([Steam](https://steamcommunity.com/app/1142710/discussions/0/4327475551415145342/)) | No lose-lose choices; no negative streaks (a rule derived from the complaints, not a source) |
| **Heroes of Might and Magic 3** calendar | Weekly: 25% a "Week of <creature>" (+5 growth), else flavor only. Monthly: 40% special month (doubled first week), 10% plague (halved population) ([thelazy.net](https://heroes.thelazy.net/index.php/Astrologers_proclaim)) | — | Most pulses can be quiet: ~75% of weeks carry flavor only and it reads fine. `world-graph-ideal.md` §3.11 already adopted this calendar |
| **RimWorld** storytellers | Cassandra: nothing before day 11; 4.6 days on / 6.0 off; 1–2 threats per on-phase; ≥1.9 days between threats; ~8.5 major threats per 60-day year; minor events every 4.8 days on average ([wiki](https://rimworldwiki.com/wiki/Cassandra_Classic)). Randy: an event every 1.35 days on average | Threat size from colony wealth punishes building (already in the repo) | On/off cycles with a minimum gap make threats readable. **Size from `Θ`, never wealth** |
| **Left 4 Dead** | Director: build, peak, fade, relax (30–45 s). Dialogue: a query is hundreds of key:value facts; a rule matches when all its criteria hold; **the rule with the most criteria wins**; responses write facts back, optionally expiring; ~10,000 lines in L4D2, searched in microseconds ([Ruskin, GDC 2012](https://archive.org/stream/valve-publications/2012/GDC2012_Ruskin_Elan_DynamicDialog_djvu.txt)) | — | "Most specific wins" plus expiring facts is the cheapest salience engine there is. A relax window after a big threat |
| **Hades** (from the shipped Lua, [mirror](https://github.com/GarageOfRick/hades_mod), may carry mod edits) | `PlayRandomRemainingTextLines`: pick among eligible unplayed SuperPriority sets, else Priority sets, else unplayed sets, else reset and pick from all. `NPCData.lua`: 99 SuperPriority, 498 Priority, 1,252 `PlayOnce`; requirement fields dominated by `RequiredTextLines` (1,403) and `RequiredFalseTextLines` (704). 21,020 voiced lines ([GDC](https://www.gdcvault.com/play/1026975/Breathing-Life-into-Greek-Myth)) | — | The story is a graph of "heard A, not heard B". **Tiers let story beats pre-empt flavor.** Death and return *is* the delivery: our expedition return, delve wipe and world end are the House |
| **Fallen London** | Card frequency: Rarest 1, Rare 10, Unusual 20, Very Infrequent 50, Infrequent 80, Standard 100, Frequent 200, Abundant 500, Ubiquitous 1000; "High Urgency" drawn first ([wiki](https://fallenlondon.wiki/wiki/Card_Frequency)). **Menaces**: at 8 Suspicion, Nightmares, Wounds or Scandal the player moves to a menace area with its own storylets and a way back ([Menaces](https://fallenlondon.wiki/wiki/Menaces_(Guide))) | — | **The owner's "failure opens content" has shipped for 15 years as menace areas.** Our band weights (1000/300/90/25/7) already sit close to Fallen London's |

### 4.2 Choices and characters

| Game | Mechanism and numbers | Lesson for us |
|---|---|---|
| **FTL** "blue options" | Choices unlocked by a crew race, a system level or an augment, usually the better outcome (Rock 5, Engi 7, Slug 10) ([forum](https://www.subsetgames.com/forum/viewtopic.php?t=24487), 2nd-tier) | **The roster is the blue-option key.** A creature's species, element or trait adds a choice, so collecting pays outside combat |
| **Darkest Dungeon** | Curios: bare-handed crate 75% heirloom / 25% nothing; the right provision makes most curios ~100% good ([wiki](https://darkestdungeon.wiki.gg/wiki/Curios)). Town events: a weekly deck with a player frequency setting; "Wolves at the Door" 12% +3% per town event **(2nd-tier)**; some beats fixed to a week | A supply you chose to carry turns a gamble into a decision. A weekly deck with a frequency dial fits held sectors |
| **Wildermyth** | Every event is a "play" with a cast; a role takes the highest-scoring hero, e.g. `(30*hunter)+(30*hook_weird)+LEADER`; a required role that cannot be cast removes the event ([wiki](https://wildermyth.com/wiki/Targets_and_Scoring_Guide)). Caps: 1 opportunity quest in chapter 1, then 2 per chapter; 3 hooks per hero, 1 resolved per campaign ([Hook](https://wildermyth.com/wiki/Hook)). Designer rules: trade-offs not good/bad choices; show percentages; *"never troll the player"*; *"relationships don't go down (not fun)"*; *"one bad name ruins ten good ones"*; *"if it affects combat, it's important"* ([GDC 2022](https://media.gdcvault.com/GDC+2022/Speaker+Slides/GettingPlayersEmotionally_Austin_Nate.pdf)) | **Cast the save's creatures into authored templates.** This is the direct answer to "no NPCs" |
| **Endless Legend** | Minor-faction villages: bribe, quest (the richest option, pacifies the whole region) or conquest ([dev diary](https://community.amplitude-studios.com/amplitude-studios/endless-legend-2/blogs/980-minor-factions-dev-diary-5)). Faction quests: 8 chapters, finishing one is a victory ([wiki](https://endlesslegend.wiki.gg/wiki/Faction_Quests)) | Matches `world-graph-ideal.md` §8.2's conquest / contract / ignore. The quest should be the richest path |
| **Battle Brothers** ambitions | Several goals offered from company and world state; each gives ≥100 renown and a mood boost; cancelling costs morale; ignoring one too long: *"the men may lose confidence"* ([dev blog #89](https://battlebrothersgame.com/dev-blog-89-ambitions/)) | Player-chosen medium goals give an open world a spine without a linear plot |
| **Caves of Qud** | 5 generated sultans; ~12 random events each, chosen with no causal logic, then rationalized from state ("the effect causes the cause"); fragments found out of order and sorted by the journal ([FDG'17](https://www.freeholdgames.com/papers/Generation_of_mythic_biographies_in_Cavesofqud.pdf)) | Generate **artifacts** of history, not a simulation. Zomboss's broken time machine can leave logs in vaults and shrines |
| **Monster Hunter** | Story assignments once; optional quests forever; one-time special assignments later become repeatable ([Fextralife](https://monsterhunterworld.wiki.fextralife.com/Investigations), 2nd-tier) | A story version runs once and leaves a repeatable version behind |

### 4.3 Relationships

| System | Numbers | Lesson |
|---|---|---|
| **Stardew Valley** | 250 points per heart, 10 hearts; talk +20/day; gifts +80/+45/+20/−20/−40; −2/day if not spoken to ([wiki](https://stardewvalleywiki.com/Friendship)) | Time decay makes a daily chore — the same failure as the repo's finding 7 |
| **Fire Emblem** (GBA) | 80 points per level; per-pair base and per-turn gain; ≤5 supports per unit; one conversation per chapter ([FE8](https://fe8.triangleattack.com/guides/supports)) | Per-pair authored rates plus a cap make pairs matter |
| **Hades** | Hearts lock at 5–7 of 7–10 until a favor story opens them (`GiftData.lua`) | A **story-gated band**, not a meter |
| **Persona 5** | Up to +3 per choice, ×1.5 with a matching persona; the scarce resource is time slots, not points ([guide](https://psnprofiles.com/guide/9938-persona-5-royal-confidants-guide)); rank thresholds **UNVERIFIED** | Scarce *opportunities* create choice |

### 4.4 Delivery and authoring

- **Arknights:** event rewards sat in the last stages, so players rushed past the story to farm;
  Dossoles Holiday fixed it by making every stage drop equal value
  ([Fun Makes Right](https://funmakesright.wordpress.com/2023/03/16/how-dossoles-holiday-solved-the-biggest-issue-with-events-in-arknights/)).
  **Never tie story position to reward efficiency.**
- **Genshin:** story never costs stamina (resin gates loot only); banked keys stop missed days being
  lost ([game8](https://game8.co/games/Genshin-Impact/archives/380307)).
- **Idle players skip text.** A scrolling log that never pauses play works; a modal does not
  (Idle Champions, Melvor Idle, 2nd-tier). Cookie Clicker's ticker is 200+ state-conditioned lines
  ([wiki](https://cookieclicker.wiki.gg/wiki/News_Ticker)): the cheapest storylet system is flavor
  conditioned on state.
- **Storylets / quality-based narrative** ([Short 2016](https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/)):
  content + prerequisites + effects on state. Named weaknesses: bookkeeping load; too many visible
  choices; boring until the database is big (Kreminski's "time-to-bootstrap"); salience has no
  dramatic structure of its own. Kreminski's fix, **resource binding** ("sell [cargo] on [planet]"),
  multiplies templates ([Short 2019](https://emshort.blog/2019/01/06/kreminski-on-storylets/)).
- **Branching cost:** *80 Days* is 750,000 words of ink; one playthrough shows about 2%
  ([Wikipedia](https://en.wikipedia.org/wiki/80_Days_(2014_video_game))). Yarn Spinner 3 (MIT, C#)
  has built-in storylets with a complexity score and least-recently-viewed selection
  ([docs](https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/saliency)).
- **LLM narrative at runtime:** AI Dungeon-style systems lose constraints across the context window,
  repeat, and lose continuity ([arXiv 2411.00308](https://arxiv.org/pdf/2411.00308)). A model may write
  text offline, validated; selection and casting stay deterministic.

**Could not confirm:** the Slay the Spire shrine chance; Darkest Dungeon town-event rates per
setting; Persona rank thresholds; the Pokémon affection ladder; Stellaris Situation numbers; Mount &
Blade relation decay; FTL's design reasoning. Fandom, Steam and Paradox forum pages were unreachable
or served empty.

### 4.5 What the prior art changes in this design

1. **Casting beats authoring volume** (Wildermyth, Kreminski). Templates with roles cast from the save
   multiply content without multiplying writing.
2. **Tiers beat weights alone** (Hades, Fallen London). Story beats pre-empt flavor.
3. **Most specific wins** (Valve). A storylet that matches more facts about this moment is preferred.
4. **The repetition budget is pool ÷ pulse** (CK3). The storylet corpus must grow with the pulse rate.
5. **Failure opens a place, not a game-over** (Fallen London menaces). This is the loop page's
   failure branch, already proven.
6. **Relationships do not decay with time** (Wildermyth, Hades, Stardew's chore, the repo's finding 7).
7. **The roster unlocks choices** (FTL blue options). Collecting pays outside combat.
8. **No lose-lose, show the odds, never tie story to reward efficiency** (Total War, Wildermyth,
   Arknights).
9. **Idle delivery is a log, not a modal** (idle games, Hades' return to the House).

---

## 5. The real question

Feasibility is not the question. Most of the machinery exists. The honest questions are two:

1. **Which shape.** One narrative engine that every place draws from, or an event system per place.
   The Delve already wrote the engine. Principle 11 decides it: **one engine, many hosts** (§6.2).
2. **What should it do** — content and identity. Who the characters are, what the story is about,
   and who writes the spine. That is the owner's (§10).

The largest lever is not new design. **Plug in what exists first**: the Delve's event deck, quest offer and talk tree go live the
day the Delve can start. A story program built before that ships content nobody can reach. Owner ruling 2026-09-19 (round 3): that
plugging-in is this program's own first Delve work (`delve-live-start`, `delve-live-rooms`), placed before `delve-host`.

---

## 6. The shape

### 6.1 Three layers of narrative

| Layer | What it is | Who writes it | Volume |
|---|---|---|---|
| **Spine** | The Rotwright chase: a finite run of chapters keyed to time-machine pieces (ruling R3), played as scenes | Generated by seedsmith (ruling R1) | Small, fixed per chapter |
| **Arcs** | Character and clan questlines: chains of storylets with roles cast from your save | Templates from seedsmith, cast at runtime | Medium, grows with content |
| **Texture** | One-off encounters in every place | seedsmith storylets | Large, grows with content |

The spine gives direction. Arcs give attachment. Texture keeps a turn, a room or a return from being
empty. Prior art (§4) is consistent that texture alone repeats and a spine alone runs out.

### 6.2 One storylet engine, many hosts

The Delve's event engine becomes the program's engine. It moves out of `Delve/` (a re-seam, not a
rewrite) and the Delve becomes its first **host**.

- **A storylet** is the existing `EventRow` shape: id, kind, theme, eligibility predicate, two to four
  outcomes with an ordinal (`good`/`bad`/`mixed`), effects by atom family and power band, a drop band,
  a repeat scope, and a `chainRef`. The shape already works; it widens, it is not replaced.
- **A host** is a place that can show a storylet: a delve room kind, a world slot kind, a world turn,
  an expedition return, a homeworld visit. Each storylet declares the hosts it fits.
- **Eligibility** compiles through the one `PredicateCompiler`. New predicate leaves (sector kind,
  relation band, story flag, character state, the Garden Keeper's level band — Dave's level in today's code) are closed-vocabulary additions, each a
  reviewed change.
- **Roles and casting.** A storylet names roles (required, optional, forbidden), each with a score
  over the save's facts. The runtime casts the best-scoring character or creature into each role; a
  required role that cannot be cast removes the storylet from the pool (Wildermyth, §4.2). One
  template therefore plays differently in every save.
- **Roster options.** A choice may require something the player brought: a creature of a species,
  element or trait in the party, a supply carried. That choice is usually the better one (FTL's blue
  options, §4.2). The shipped curio model already works this way: the right provision turns a
  gamble into a decision.
- **Selection, in order** (Hades, Fallen London, Valve — §4.1):
  1. **Tier.** An eligible story beat (spine) pre-empts everything, at most one per pulse. Then
     priority storylets (consequences, chain links whose previous link was seen). Then the pool.
  2. **Pool pick.** A seeded weighted draw. Weight = frequency band × specificity, where specificity
     grows with the number of conditions the storylet matched ("most specific wins", tempered by the
     draw). Unplayed before played; when the pool is exhausted it resets, cooldowns do not.
  3. **Fire chance with pity** for pulses that may be quiet: `p = min(1000, p0 + n × step)` per-mille,
     `n` = pulses since the last storylet fired, reset on fire (Slay the Spire, Stellaris). The `min`
     is a probability bound (a bounded ratio), not a magnitude cap.
  4. **Cooldowns** per storylet and per kind, counted on the host's own clock (turns, rooms,
     collects). The existing repeat scopes and recent-cells set are the first two.
- **Fairness rules** (Total War, Wildermyth, Arknights — §4.1, §4.4). No lose-lose choice. No two
  negative storylets in a row on one host. Show the odds of a contest. Risk is priced in cost, time or
  a fight rather than a hidden fail roll. Rewards do not depend on where a story beat sits.
- **Seeds.** `WorldSeed.DeriveRollSeed(worldSeed, "event:<host>", targetId)` or the Delve's named
  streams — one stream per purpose, never shared with a combat stream (Slay the Spire's correlated
  streams, §4.1).
- **Outcomes** stay a closed vocabulary. The existing effects (resource delta, status, loot draw)
  extend with six members, each routed through a path that already exists. (Owner ruling 2026-09-19 (round 3): every outcome names its consequence as one object, `{kind, ref, param}` — the kind above (or an existing one), the target it acts on (a role, a character, a flag, a quest, a scene or the host's wild slot; none for loot or a fight) and a closed modifier (for `relation.shift`, which relation fact it records: met, helped, refused, betrayed or spared). The seed contract owns the shape (`narrative-seed/spec-narrative-contract.md` §5); the runtime loads it as-is):

  | New outcome | Routes through |
  |---|---|
  | `quest.offer` | `QuestCatalog` / `QuestOffer` |
  | `relation.shift` | the relation ledger (§6.4) |
  | `story.flag` | the story ledger (§6.7) |
  | `battle.start` | `BattleRequest` or an `IIntentSource` into an existing battle mode |
  | `scene.play` | `StorySceneHost` via the scene-trigger ledger |
  | `recruit` | `RecruitMint` for an unnamed wild creature (the existing wild-join intake); an ownership transfer for a cast character (§6.3) |

- **A place owns its loop, never the mechanism.** A place decides *when* it asks for a storylet (a
  room entered, a turn resolved, an expedition collected). It never decides *which* storylet or *what
  it pays*.

### 6.3 Characters

A **character** is a persistent identity bound to a species. Every non-lead character is a
**creature with a name** — its **own** name, never a PvZ one. The Fracture made them, as it made your
roster. The three leads keep their **roles** (the summoner, the time-travelling companion, the
antagonist) but take **original names** in all story content (owner rulings R8–R10, §10); in text they
are always tokens resolved from a names registry, so a rename is one JSON edit
(`narrative-seed-ideal.md` §6.5b). *This amends the product-vision wording "Crazy Dave, Penny, and
Zomboss"; R9 says where that change lands.*

| Field | Vocabulary | Reuses |
|---|---|---|
| species | the species catalog | the art and the fight a character brings |
| role | closed: wanderer, trader, hermit, chronicler, clan elder, warlord, captive, envoy, companion | new, closed |
| personality | Loyal, Stoic, Proud, Calculating, Feral | `CreaturePersonality` — **no second personality vocabulary** |
| disposition | eager, open, wary, hostile | `disposition.v1.json` — **no second relation ladder** |
| home | sector or slot, delve domain, homeworld | world ids |
| memory | facts: met, helped, refused, betrayed, spared | the event-seen shape, generalized (§6.7) |
| fate | present, joined, departed, fallen | new, closed |

**Casting (seed to concrete).** seedsmith emits **one character seed per species that gets one**
(`narrative-seed-ideal.md` §6.3): the species, a role, a voice, lines per disposition band, and
closed-list picks. At world creation the runtime chooses **which** characters a save meets and places
them in homes, seeded, per save — the Wildermyth pattern (§4) applied to casting, not to species.
Two saves meet different people. Reconciled 2026-09-19: this paragraph used to cast species-agnostic
templates onto species; narrative-seed rejects those, and `npc-story-events/spec-cast-resolver.md` and
`spec-character-registry.md` follow narrative-seed.

**Mint-first identity.** A character is minted as a real specimen at casting time and held by a
non-player owner row, following the shipped precedent of Zomboss's dedicated player row
(`RpgStore.ZombossDeploy.cs`). Two consequences, both wanted:

- `ContractPolicy.PersonalityFor(instanceId)` already derives personality from the specimen id, so
  the character's personality **is** the specimen's. No stored override, no change to a derived rule.
- Joining your roster is an **ownership transfer**, not a new mint. The creature who talked to you is
  the creature who fights for you.

**Scope follows the game's own rule: you keep who you are; a world keeps its own.** Leads and companions are **save-scoped** and cross worlds with you. A clan elder or a sector hermit is **world-scoped**: they live as long as their world exists. Owner ruling 2026-09-19 (round 3):
under the approved `world-continuity` program a world no longer ends — it hibernates, goes idle, or falls (`world-continuity-map.md` modules `world-state-vocabulary`, `hibernation-clock`, `world-fall`). A world-scoped character stays present while its world is active, hibernating
or idle, whether contested or won. **Owner ruling 2026-09-19 (round 4):** when its world falls (`world-fall`'s `outcome → fallen`) it is **frozen**, never deleted — read-only history that the reserved `world-reclaim` may revive. There is no "abandoned" state: world-continuity deletes nothing (§6.7). Coming back to a hibernating world means meeting the same people.

### 6.4 Relationship: one ladder, two states

- Before a creature joins you, its relationship is **disposition** (the 4-band ladder).
- After it joins, its relationship is **loyalty** (`LoyaltyRank`, already built with personality
  rates). Joining converts disposition into a starting loyalty. There is never a second axis on one
  creature.
- A **faction's** relation (clan, rival) uses the same 4-band ladder, so trade-network's
  hostile/neutral/allied maps onto it instead of adding a third (owner question 4).
- Disposition is **derived from an append-only fact ledger**, never stored as a number — the same
  pattern as `LoyaltyRank` ("derived, never stored"). Replay recomputes it.
- **Disposition moves on facts, never on time.** Helping, refusing, betraying and sparing move it.
  Not visiting does not. Time decay turned relationships into a daily chore in Stardew Valley, and
  every decaying loyalty meter in the repo's own genre survey was removed by its studio (§4.3). The
  top band can be **story-gated** (Hades' locked heart): the last step opens only through the
  character's own storylet.
- **Relationships grant access, not stats.** A friendly character offers better choices, quests,
  prices, intel, a legion in a war, or a join. If a later design wants a relationship to change an
  actor's numbers, it answers the five actor-layer questions first (principle 9).

### 6.5 Quests: one engine, fact sources per place

- `QuestCatalog` / `QuestOffer` / `QuestProgress` (built for the Delve) is the engine. Other places add
  **fact sources**: a turn report for world quests, an expedition resolution for expedition leads.
- Objectives are **mode-agnostic** (principle 3): "defeat 30 zombie-type creatures" counts every
  battle source, source-tagged. "Kill 30 on the lawn" is not a legal objective.
- Rewards go through the existing grant paths with a dedupe key from the quest's durable id.
- Quest completion is also **achievement evidence** (`event-seen`, `counter-reach`). Achievements stay
  achievement-title's engine.
- The **quest log** is a layer, openable from any stage. Its content: open quests, the cast you have
  met, and the story so far. Its design goes through `/idea-ui`, not this document.

### 6.6 Per place

| Place | When it asks the engine | What it adds |
|---|---|---|
| **Delve** | On entering an event-capable room kind (`curio`, `shrine`, `trap`, `wild`, `merchant`, `unknown`) | Characters in rooms: a named trader in `merchant`, a captive in `wild` (the shipped cage variant), a chronicler at a `shrine`. Story chains go live |
| **World map** | In the `Events` phase, per sector holding a host slot (`Shrine`, `Anomaly`, `Tear`, `Vault`, `Market`, `Wildland`), fog-correct | A typed event vocabulary in `TurnReportKinds` instead of free-text prefixes. **A choice is a world command**, admitted through `WorldCommandAdmission` and resolved at End Turn — deterministic and replayable, like every other order. Owner ruling 2026-09-20 (round 5): the storylet's climate is ~~derived from the sector's type (R19)~~ the sector's own climate (R20, Owner ruling 2026-09-20 (round 6)), and its rewards take the claim loot `world-claim-loot` mints (R17) |
| **World map mobiles** | Warlords and caravans already exist as kinds | A warlord is a character with a name (world-graph's "roaming powers"). Caravans stay trade-network's |
| **World stage** | On a held sector's turn | Petitions: a resident asks for something the sector needs. A clan's request is **computed from world state**, never authored per clan (`world-graph-ideal.md` §8.2: *"a clan's price is its personality"*) |
| **Expeditions** | At collect | The idle clock never blocks. An encounter comes home as a **lead**: a character met, a rumor, a quest offer. The lead is **sealed at dispatch** (seeded: storylet, cast and its automatic choice fixed from the dispatch seed and the ledger as it stood) and **revealed at collect**; the ticks themselves resolve at collect from the seed sealed at dispatch (`ExpeditionResolver.Resolve`, `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:109`). `WildCreatureMet` is the natural host. Delivery is a **log line in the collect summary**, never a modal (§4.4: idle players skip text). Reconciled 2026-09-19: said the encounter "resolves at dispatch like every tick", but code resolves ticks at collect; matches `npc-story-events/spec-expedition-lead-host.md` §2 |
| **Homeworld (Sanctum)** | After an outing, on entry | Hub conversations with Hourbloom, companions and visitors, played through the scene-trigger ledger. This is where the spine lives. As in Hades' return to the House, **one conversation per character per return**, and characters react to how the outing went (a wipe, a win, a lost sector) |
| **Lawn** | Never mid-match | The lawn contributes facts and may host a fight. Scenes play before or after a match (the Rift prologue precedent) |

### 6.7 Story state: two scopes

A **story ledger**: append-only facts (`met`, `helped`, `chapter.reached`, `flag.set`) with a scope.

| Scope | Lives | Holds |
|---|---|---|
| **Save** | Across worlds, like souls and roster | Spine chapters reached, companions, leads' memory of you |
| **World** | As long as its world exists — active, hibernating or idle, contested or won (Owner ruling 2026-09-19 (round 3)) | Local characters' memory, clan relations, world arcs |

The onboarding story rows and the Delve's event-seen scopes are the two existing precedents. The
ledger generalizes them; it does not add a third parallel store beside them. Owner ruling 2026-09-19 (round 3): **world-scoped story state persists while a world hibernates.** The approved `world-continuity` program makes worlds hibernate instead of ending, with an attention axis (`active | hibernating | idle`) and an outcome axis (`contested | won | fallen`) (`world-continuity-map.md` locked assumption 1; module `world-state-vocabulary`). World-scoped story, character and relation state lives as long as its world exists in any attention state, and follows the world's state (**owner ruling 2026-09-19 (round 4)** — world-continuity deletes nothing, so neither does this program, and no "abandoned" state is needed or requested):

| World state (world-continuity) | World-scoped story state |
|---|---|
| `active` | **live** — drawn, written |
| `hibernating` / `idle` | **dormant** — kept intact, not drawn; the only writes are facts world-continuity's coarse step emits; quest expiry pauses because the host clock does not advance |
| `outcome = fallen` | **frozen** — read-only history; open quests close as failed-by-fall (a ledger fact, no penalty beyond the lost reward); failure branches read it; the reserved `world-reclaim` may revive it |

"Retire" in this program's specs means frozen, never deleted (the world's own rows are never deleted either — `world-fall` §4). The earlier line "dies with the world, like loam" is superseded — it described bounded worlds, which world-continuity retired.

### 6.8 Failure branches

`the-loops.md` names *failure branches (Vision)* on three loops: a lost sector, a failed extract or a
failed defense opens different ground, "not only a wipe". Fallen London has shipped exactly this for
fifteen years as menace areas (§4.1). The shape here:

- A failure writes a **fact** to the story ledger (`sector.lost`, `delve.wiped`, `siege.failed`), in
  the world or save scope that matches what was lost.
- That fact makes **priority storylets** eligible: a questline, a new character, a branch location
  (a bandit-held sector, a domain to reclaim) with its own storylets and a way back.
- No failure branch takes back what the game's own rules let you keep (roster, souls, essence).
  It offers content; it never adds a second penalty on top of the loss.

### 6.9 The only legal paths an outcome may take

1. **Resources**: the stock's existing grant or spend API, with a dedupe key from the event's durable
   fact id.
2. **Contests**: `Θ_actor − Θ_content` through `CombatProbability.Sigmoid`. A flat coin (the shipped
   `Flatter` roll against `wild.talk.flatterMilli`, `TalkTree.cs:88`) is fine for a disposition shift
   that does not scale with power.
3. **Magnitudes**: `P(Θ_content)` through the existing loot pipeline and `SoulSinkPolicy.Price`.
4. **Timed boon or curse**: an atom container at an `OwnerScope`, or a registered
   `IActorStatSubsystem`.
5. **Fights**: a `BattleRequest` or `IIntentSource` into an existing battle mode.
6. **Rolls**: `WorldSeed.DeriveRollSeed` or `SeededRng.DeriveStream` with a named stream. Never
   `System.Random`, never the wall clock.
7. **Numbers**: `gk-core/data/tuning/<domain>.v{n}.json`.
8. **Joins**: `RecruitMint` / ownership transfer, inside the soul economy's pull-rate target.

### 6.10 Authoring

The generation side — seed contracts for storylets with real choices, characters and arcs, the
pipelines and their validators — is designed in [narrative-seed-ideal.md](narrative-seed-ideal.md).
The bullets below are the runtime's view of it.

- **Spine**: generated scene scripts (ruling R1), emitted as data rather than TypeScript literals and
  carried into lingui by the same codegen bridge as every other generated string
  (`narrative-seed-ideal.md` §6.8). The chapter list itself is planned, not generated: one chapter per
  time-machine piece (ruling R3).
- **Characters**: a new seedsmith adapter. The LLM writes names, voice and lines per disposition band.
  Role, personality, species pool and home are closed picks. Magnitudes are table-owned.
- **Storylets**: the dungeon adapter's event pipeline widens to more hosts. Before it widens, its two
  defects (§3.4) are fixed in the generator. Templates use **resource binding** — slots like
  "[creature] asks for [supply] in [sector]" filled at runtime from world state (Kreminski, §4.4) —
  so one template covers many situations. This is also how `world-graph-ideal.md` §8.2 wants clan
  requests: a query over world state, not an authored quest per clan.
- **History as artifacts**: the time machine's scattered pieces can leave fragments — logs, broken
  parts, the Rotwright's notes — in vaults, shrines and delve caches, found out of order and sorted in the
  quest log (Caves of Qud, §4.2). It is cheap texture for the spine.
- **Names are a quality gate** (*"one bad name ruins ten good ones"*, Wildermyth). Character names
  and storylet titles go through the same review bar seedsmith applies to species names.
- **Validation**: preflight refuses a dangling `chainRef`, an unresolved pool id, an event that gates
  the boss (already a rule), a character with no species, and free text in the wrong script. Tests
  assert those rules and the closed vocabularies, never corpus sizes.

### 6.11 Alternatives rejected

| Alternative | Why not |
|---|---|
| An event system per place | Two engines deciding the same thing is the defect principle 11 forbids |
| Branching dialogue trees (ink, Yarn Spinner) | Storylet choices (2–4 outcomes) plus the talk tree's verbs cover the need. story-scene already deferred branching (*"No branch exists; revisit then"*). Trees multiply authoring cost, and generated trees are hard to validate |
| An original human cast | Product vision keeps the cast inside Fusion's own world |
| Daily or weekly quests on a real calendar | A fourth clock; `the-loops.md` forbids it |
| Reputation as a spendable currency | Fails the registry's P4/P6 bar and adds a wallet; disposition stays a derived band |
| Relationship stat bonuses by default | Invents an actor layer; access is the reward |
| LLM-written text at runtime | Non-deterministic, unvalidated, and not localizable; seedsmith writes offline, the runtime only casts |


### 6.12 Counter-doctrine — the Rotwright studies your war

**Owner ruling R13 (2026-09-19): no recurring-antagonist system.** Warner Bros. holds US patent
10,926,179 B2, *"Nemesis characters, nemesis forts, social vendettas and followers in computer games"*
(granted 2021-02-23, shown active to 2036-08-11 —
[Google Patents](https://patents.google.com/patent/US10926179B2/en)). The owner's words: *"avoid
nemesis system, we can be sue, make other better mechanism."* This section is that mechanism. It is a
design choice to stay far from the patent's distinctive elements; **it is not legal advice**, and a
counsel review belongs before a commercial release.

**Design rules that keep the antagonist side clear** (binding on this program and on
`world-graph-ideal.md`'s warlords):

1. **No individual enemy grows from meeting you.** No enemy character gains a level, trait, ability,
   rank or title because it survived, escaped, won or lost an encounter with the player.
2. **No enemy hierarchy.** No ranked roster of enemy captains with promotions, succession, rivalries
   or power struggles between them.
3. **No enemy remembers you personally.** No enemy character's lines are picked from its own past
   encounters with the player. Antagonist memory lives at the **faction and world** level.
   (Friendly characters' relationship lines — §6.4 — are the long-standing RPG relationship pattern and
   stay; they never apply to an enemy.)
4. **No enemy base built from an enemy character's traits.**
5. **No sharing of enemy data between players.** The game is local and offline; keep it that way here.
6. **Warlords "grow" by world rules only** (`world-graph-ideal.md` §3.10: *"warlords patrol, grow,
   claim lairs"*): by time, territory and lairs held — never by the outcome of fighting the player.

**What replaces it — and why it is better for this game.** The loop page already names the idea:
*"Enemy counter-development (Vision): if you lean fire, the war grows fire-hard; if you lean summons,
anti-summon shows up. Not 'enemy level = Dave's level.' Raise creatures → a strategy works → the world
counters → rebuild"* (`guide/the-loops.md:95`). A Nemesis-style system answers *"who beat me last
time?"* — an action-game question. This game is a strategy game: the interesting question is *"what is
my whole war doing, and how will the enemy answer it?"* Counter-doctrine answers that one.

| Part | How it works | Built on |
|---|---|---|
| **The reading** | Per world, the Rotwright reads the **aggregate** of your war: element share of your fielded creatures and damage, deploy modes, action tags used, the sector kinds you take. Owner ruling 2026-09-20 (round 5), R18: **only what his faction observed** — battles it took part in or saw, and sectors and forces inside its observation; a lean you keep out of his sight is not studied | His faction's per-turn observation, written by the turn engine's `Intel` phase (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:384-403`, into `WorldState.Intel`), and the turn's battle reports; a per-world aggregate, never an individual encounter, never a battle's outcome |
| **The study** | While one lean persists, a visible **study bar** advances each End Turn — *"The Rotwright is studying your fire."* (Stellaris Situations and XCOM 2's Avatar Project meter are the known shape: a threat the player can see coming and push back) | The `Events` phase of the turn engine; the bar and the adopted doctrine are **hashed faction state** on the antagonist's `WorldFaction` record (`gk-core/src/FusionRpg.Core/World/WorldState.cs:70`, hashed through `WorldCanonical` like `UpkeepHandicapMilli`), because the policy that reads them must replay from world state. The story ledger records only the voice (scene flags) and readings. Reconciled 2026-09-19: said "the story ledger"; `npc-story-events/spec-counter-doctrine.md` §2 hashes it on the faction record |
| **The doctrine** | When the bar fills, the Rotwright adopts a **doctrine** from a closed vocabulary — each one a counter to one lean (fire-proofing against a fire lean, anti-summon against summons, siegecraft against turtling). For a stated window of turns it changes **what** his faction fields (species drawn, resistance and element mix, AI order weights) — **never how strong**: magnitudes still read `P(Θ)` and contests `Θ` (principle 5) | Faction policy (`FrontierRulesPolicy`), species pools, the element ring |
| **The voice** | Adopting a doctrine plays a short scene in the Rotwright's voice, and spine chapters can comment on it. The line reacts to your **strategy**, not to an encounter with him | Storylets, `scene.play`, ruling R2 |
| **The counter-play** | Every doctrine is public, time-limited and has a stated weakness. The player can **slow the study** by changing strategy, **hide it** by fighting out of his sight (R18), or **set it back** by raiding a study site on the map (a host slot such as `Anomaly` or `Vault`) — a storylet or a fight | World commands, `BattleRequest`, storylets |
| **The loop** | Doctrine forces a rebuild, which is exactly the loop the vision asks for: *"a strategy works → the world counters → rebuild"* | — |

**Tunables** (decided by principle at spec, `gk-core/data/tuning/narrative.v1.json` (new) or the world
domain): study-bar rate per turn of a sustained lean, the lean threshold, doctrine window length, the
cooldown before the next doctrine, and how much a raid sets the bar back. The doctrine vocabulary
itself is a closed, reviewed list.

---

## 7. Tunables

Every number below lives in a tuning file, published through the tuning tool. Values are set at spec
by principle and prior art; none is an owner question.

| Tunable | Unit | Starting anchor (prior art, §4) | Owner file (proposed) |
|---|---|---|---|
| Frequency band weights | weight | Reuse the Delve's 1000/300/90/25/7 (`spec-event-deck.md`); close to Fallen London's scale | `gk-core/data/tuning/narrative.v1.json` (new) |
| Fire chance and pity step per pulse | per-mille | Dense host (delve room): 100 + 100 per miss (Slay the Spire). Sparse host (world slot): 50 + 5 per miss (Stellaris) | same |
| Quiet share of world turns | per-mille | ~750 quiet (HoMM3's flavor-only weeks) | same |
| Specificity weight per matched condition | weight | Set so a two-condition match beats a one-condition match most of the time (Valve) | same |
| Cooldown per storylet and per kind | turns / rooms / collects, on the host's own clock | Per-event cooldown (CK3); confederation-style 5 turns (Total War) | same |
| Threat on/off cycle, minimum gap, relax window | End Turns | Cassandra 4.6 on / 6.0 off / 1.9 gap, read as turns: ~1 major threat per 7 turns | same |
| Most storylets per pulse; opportunity storylets per chapter; conversations per character per return | count — **pacing limits, structural, each stated in a comment** | 1 spine beat per pulse; ≤2 opportunities per chapter (Wildermyth); 1 conversation per character per return (Hades) | same |
| Chance an expedition tick becomes an encounter | per-mille | — | `data/tuning/expeditions.v{n}.json` (existing domain) |
| Disposition shift per fact kind | band steps | Moves on facts only, never on time (§6.4) | `gk-core/data/tuning/narrative.v1.json` (new) |
| Contest scale for skill checks | Θ units | The existing contest policy — **no new scale** | existing |
| Reward bands | the existing `dropBand` / `powerBand` vocabularies | — | existing loot tuning |
| Display text | — | — | seed and catalog files, never the number file |

The pool-to-pulse ratio is the repetition budget (CK3, §4.1). The spec sets pulse rates against the
corpus size at the time, and seedsmith grows the corpus when a pool starts repeating. The corpus size
is a reading, never a test assertion (principle 14).

---

## 8. Dependencies on other programs

This program's content is unreachable until these land. Each belongs to its own program:

| Needed | Owner |
|---|---|
| The Delve can start (`ImportDungeonDomains` caller), rooms are marked, events are drawn and resolved, quests are offered | ~~party-dungeon~~ **this program** — Owner ruling 2026-09-19 (round 3): `delve-live-start`, `delve-live-rooms`; party-dungeon keeps the domain content they import |
| `AchievementEvaluator` is hosted and fed | achievement-title |
| Player-routed push | notification-ssot |
| A clan policy and real needs | world-map / trade-network |
| ~~A claim-loot mint for the world's budget line~~ | Owner ruling 2026-09-20 (round 5), R17: **this program** (`world-claim-loot`), transferred from world-map-runtime's `sector-loot-wiring` Part A |
| The item program's derived base price (for traders) | item program |

---

## 9. What this deliberately does not decide

- The quest log's and dialogue card's visual design (`/idea-ui`).
- The narrative localization mechanism: seed text into lingui catalogs at build, or per-locale seeds.
  Decide at spec against story-scene S4.
- Deck weights, cooldowns and chances (§7; decided by principle at spec).
- Which trader or merchant mechanics belong to trade-network rather than here: this program gives a
  market a face, trade-network owns the exchange.
- How a world-scoped character's specimen is retired when its world ends (mint-first, §6.3). The spec must state it, so a finished world leaves no orphaned specimen rows. Owner ruling
  2026-09-19 (round 3): "ends" now means **falls** (world-continuity `world-fall`) — never hibernates; stated in `npc-story-events/spec-character-registry.md` §4. Round 4: a fallen world's state is frozen, never deleted, and there is no "abandoned" state.
- Loyalty decay. The contracts program's `PersonalityRates` include a decay rate; §6.4's no-time-decay
  rule covers disposition only. Whether loyalty decay survives is that program's decision, and
  §4.3's evidence is relevant to it.
- Voice audio, portraits and art direction.
- Any spec, plan, task list or code.

---

## 10. Owner decisions

**All answered by the owner on 2026-09-19** (R6–R7 are in `narrative-seed-ideal.md` §10; R14–R16 on 2026-09-20; R17–R19 on 2026-09-20, round 5; R20–R22 on 2026-09-20, round 6). These are rulings, not open questions; `decisions.md`
rows are drafted at spec time.

| # | Question | Ruling | Consequence in this document |
|---|---|---|---|
| R1 | Who writes the spine? | **Fully generated** (not the recommended draft-and-accept) | The spine is a generated seed kind like arcs and texture — regenerated, never hand-edited, reviewed by sample like other open-loop content (§6.1, §6.10; `narrative-seed-ideal.md` §6.1) |
| R2 | Does Zomboss speak? | **Yes — story-scene's v1 deferral is lifted for this program** | Zomboss joins the cast as a lead character with lines reacting to world facts; `actorCast.ts`'s closed `ActorId` union widens as a reviewed change |
| R3 | Spine shape across worlds | **Finite chapters, then endless** | A fixed run of chapters keyed to time-machine pieces recovered (one per world won); after the last, arcs and texture continue. Not a progression ceiling |
| R4 | One relation ladder? | **Yes — the 4-band disposition ladder for characters and factions** | trade-network's hostile/neutral/allied maps onto it; that program's spec must cite this ruling (§6.4) |
| R5 | Recurring antagonists who remember you? | ~~Yes, after the patent check~~ **Superseded by R13** | — |
| R8 | Whose names does the story use? | **Our own, everywhere in narrative** (the widest option): the leads get original names, and story prose never names a species by its PvZ or Fusion name. Names are **parameters** | Structured story text with entity tokens and a names registry (`narrative-seed-ideal.md` §6.5b). Wherever this document says Dave, Penny or Zomboss, read the lead **role** |
| R9 | Existing surfaces that say Crazy Dave / Penny / Zomboss | **Rename everywhere** | A follow-up rename program moves the Rift prologue (`actorCast.ts`, `sceneScript.ts` and its lingui messages), the player guide and the product-vision wording (`guide/the-game.md`, the `decisions.md` Product vision row) to the lead tokens and the new names. Code identifiers such as `pvz.*` are untouched (`ip-censor-ideal.md` §6.1a). `decisions.md` is not edited here; the row changes in the rename program's own change |
| R10 | Who names the leads? | **Generated and `ip-censor`-checked**; the owner may veto | Lead names are character seeds like any other, written to the names registry. **Superseded for the three leads by R11**, which the owner chose directly |
| R11 | The leads' names | **The Garden Keeper** (was Crazy Dave, the summoner) · **Hourbloom** (was Penny, the time-travelling companion — a time machine grown from a seed) · **the Rotwright** (was Dr. Zomboss, the antagonist — a maker of rot whose time engine shattered) | The first three rows of the names registry (`narrative-seed-ideal.md` §6.5b). A web search on 2026-09-19 found no conflicting character for "Hourbloom" or "Rotwright"; rejected candidates collided (Dr. Rottwell — Marvel; Trellis — an existing game; Mildew — *How to Train Your Dragon*; Mordrake — *Brutal Orchestra*; Blight — *Dead by Daylight*). **A search is not trademark clearance and not legal advice**; a clearance check belongs before a commercial release |
| R13 | After the patent check (US 10,926,179 B2, active to 2036) | **Avoid a Nemesis-style system entirely; design a different, better mechanism** | §6.12 counter-doctrine: faction-level adaptation to the player's aggregate strategy, plus six design rules that keep enemies from growing, ranking or remembering individually |
| R14 | Where do narrative rewards come from? (2026-09-20) | **Out of the host's existing budget, never on top** | Story reshapes what a place already pays (Delve loot and souls, expedition rewards, world yields); total income is unchanged. Each host names the budget line and the deduction rule |
| R15 | What is the story for? (2026-09-20) | **The story is also the game's tutorial** — *"story not only make it interesting, story also game tutorial"* | A closed `teaches` vocabulary of mechanics, each tied to a loop in `the-loops.md`; spine chapters and storylets carry `teaches[]`; the first time a player meets a mechanic, an eligible teaching storylet gets the priority tier (once per save, a `mechanic.first-seen` ledger fact); scenes use the story-scene beat's existing `teaching` line (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:38-39`). Tutorial beats stay skippable and never gate play. The first-session checkpoints stay owned by `standalone/spec-first-session-progression.md`; the story supplies the scenes that teach |
| R16 | The four legacy `story` Delve events (2026-09-20) | **Regenerate them clean**, with the other 50 | Kept ids and text keys; their chain links still dangle as the legacy contract forces, accepted until `delve-event-regen` replaces the tree |
| R17 | Owner ruling 2026-09-20 (round 5): who mints world claim loot, which world story rewards take? | **This program** — world claim loot is pulled into npc-story-events | A prerequisite module, `world-claim-loot`, before `world-events-host` and `petition-host`: it turns `ClaimResolver`'s inert `claim.loot:` seam on and mints each player claim once, through the existing loot pipeline (never a second roller), seeded by `WorldSeed.DeriveRollSeed`, content level from the sector's danger band, deduped on the durable claim fact, sinks named; the narrative settle pass takes a line with a payout's window before the claim mints it (R14). world-map-runtime's `sector-loot-wiring` Part A transfers here (`npc-story-events/spec-world-claim-loot.md`) |
| R18 | Owner ruling 2026-09-20 (round 5): what may the Rotwright's reading see? | **Only what his faction observed** — counter-doctrine is fog-correct | The reading counts battles his faction fought or saw and sectors and forces inside his faction's `Intel` record; a lean kept out of his sight is not studied, which adds a counter-play. R13's six rules are unchanged: a battle is a sighting, never a memory, and its outcome is never read (§6.12; `npc-story-events/spec-counter-doctrine.md` §1) |
| R19 | Owner ruling 2026-09-20 (round 5): what climate does a world storylet have? | ~~**Derived from the sector type**~~ superseded by R20 | A closed registry owned by narrative-seed maps each sector type to an element or `none` (`narrative-seed/spec-storylet-vocab.md` §3.9); world hosts pass it into selection; the world seed grid gains climate cells; the Delve keeps its room climate; expedition hosts stay neutral until an expedition carries a destination sector |
| R20 | Owner ruling 2026-09-20 (round 6): which climate source, the type or the sector? | **The sector's own climate** | World hosts pass `WorldSector.Climate` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`) — the per-sector climate the world already uses for wild spawns, raised species and lane cost — into selection; R19's type registry is retired; one source of truth; the seed-side world grid takes all seven climates |
| R21 | Owner ruling 2026-09-20 (round 6): where can an Anomaly be? | **Add it to some sector types, in this program** | Module `world-anomaly-sites`: `storm`, `nexus`, `barren` allow `anomaly`; new template versions place unguarded anomaly slots; existing worlds untouched; doctrine study sites use Anomaly and Vault (`npc-story-events/spec-world-anomaly-sites.md`) |
| R22 | Owner ruling 2026-09-20 (round 6): the mythic claim bonus seed | **`WorldSeed.DeriveRollSeed(worldSeed, stream, sectorId)`, not the turn number** | Fixed inside `world-claim-loot` (§7) with replay and independence tests; the golden/stored-value effect is measured in the build |
| R23 | Owner ruling 2026-09-20: Vault placements | **Add guarded Vault slots in the same new template versions as the Anomaly slots** | Doctrine study sites use Anomaly and Vault ground; new worlds only; `npc-story-events/spec-world-anomaly-sites.md` |
| R12 | The IP and the game's title | **"Garden Keeper and his Multiverse" is the new IP, and it replaces "Rise of Summoner" as the player-facing title.** Internal `FusionRpg.*` names, namespaces, binaries and env vars are untouched (`AGENTS.md`: *"Do not rename `FusionRpg.*` namespaces or binaries unless explicitly asked"*) | Joins R9's rename program. Measured 2026-09-19 with `git grep`: "Rise of Summoner" appears 293 times in `docs/guide`, 4 in `README.md`, 3 in `AGENTS.md`, 3 in the launcher; "Dave" 246 times in `docs/guide` and 86 in the web source; "Zomboss" 179 in `docs/guide` and 45 in the server (mostly code identifiers, which stay). The exact title alone had no search hit; bare "Garden Keeper" is used by several small games, so the full title is the distinctive form |

---

## 11. Enrichment pass (2026-09-19)

A brainstorm over this document looking for holes, each checked against the repo. Every item is either
resolved by an existing principle (and the resolution is stated) or raised as an owner question above.

| # | Gap | Resolution |
|---|---|---|
| 1 | **Event rewards are a new faucet with no named sink.** §6.9 says outcomes pay through existing grant paths, but not *how much more* the game pays once every place has events | **Rewards come out of the host's existing budget, never on top of it.** A delve event draws from the delve's own loot and soul budget; an expedition lead from the expedition's rewards. `offer:{stock}` choices are sinks and count against the same ledger. The economy rule is *"every faucet names its sink in the same change"* (`economy-principles.md` P1), and the soul-pull target already paid for this lesson once. Owner ruling 2026-09-20 (round 5), R17: a world storylet's budget is the claim loot this program's `world-claim-loot` mints; nothing minted it before |
| 2 | **`Θ_content` has no source outside the Delve.** Contests and magnitudes need it; World and Expeditions code reads no `Θ` today | The SSOT already defines it: `Θ_content = Wz·zombossLevel + Wm·mapLevel(M) + Ww·worldTier + Wf·realmsAdvanced` (`power/ssot-power-scale.md:230`), with `mapLevel` from the sector's `DangerBand`. Each host names its inputs in the spec: sector danger for world storylets, the dispatch tier for expeditions, danger 0 for the homeworld. A wiring task, not a new curve |
| 3 | **Saves break when the corpus regenerates.** "Regenerate, never hand-edit" means a storylet's text or outcomes can change under a player's in-progress arc | Seeds carry a `revision`. The story ledger records `(id, revision)`. An in-progress arc keeps resolving against the revision it started on; a removed id is tombstoned, never reused (`item/seed-contract.md` §4: *"Ids are never reused"*). New draws always use the current revision |
| 4 | **Players meet everything at once, or nothing.** No rule says when the first character or storylet appears | Narrative unlocks ride the existing ladder, never a new tutorial: the first-session checkpoints (`OnboardingCheckpointEvaluator.cs:6-13`) and Dave-level chapters. The first-session sequence belongs to `standalone/spec-first-session-progression.md`; this program asks it for one slot (the first character met), it does not edit it |
| 5 | **Quest lifetime is unstated.** Can a quest expire or be abandoned? | Expiry is counted on the host's own clock (turns, delves, collects) — never real time (principle 4). Abandoning is free apart from losing the reward; a punishment for abandoning is a decaying meter by another name (§4.3) |
| 6 | **No way to tell whether choices are interesting.** Sid Meier's test is pick rates, and the game has no account or server telemetry | The story ledger already records every pick. A local report summarises pick rate per option per storylet; an option nobody takes, or everyone takes, flags the storylet for review. Local only, no upload |
| 7 | **Generated names could collide with third-party IP.** | Character names and storylet titles pass the `ip-censor` **release** gate (ruling IC-3), the sibling program that already names `gk-data/packs/fusion/data/seed/dungeon/**` in its scope (`ip-censor-ideal.md`). No second name filter |
| 8 | ~~**Enemies have no memory.**~~ **Superseded by ruling R13 and §6.12 (counter-doctrine).** Original row kept for the reasoning trail: The world has warlords and Zomboss, but a beaten warlord is just gone | A recurring antagonist is an **arc shape** over existing warlord characters: it survives a defeat as a fact in the story ledger, returns with a changed trait and a line that remembers how you beat it, and ends when you finish it. **Patent note (to verify, not verified this session):** Warner Bros. holds a US patent on the *Shadow of Mordor* "Nemesis" system, reported granted in 2021. The spec must read the claims and keep this design clear of them before building. Owner question 5 |
| 9 | **What does "not boring" measure?** The owner's request is about feel; nothing here says how to tell it worked | Program success readings (local, reported, never test assertions): beats per hour of play per place; first-repeat distance per pool (§7); share of storylets that offered a roster or supply option; share of sessions that met a named character. They guide content volume; they are not balance numbers |
| 10 | **Hand-written storylets have no home.** The owner may want to write a special event by hand | The storylet contract accepts authored entries under an authored path, with `provenance: authored`. Same validators, same engine — one contract, two sources (`item/seed-contract.md` §2's four ownership levels already allow it) |

---

## 12. DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: product vision, Delve, world map, world stage,
    expeditions, quests, achievements, story-scene, economy, power, tunables, effects, battle,
    actor layer, seedsmith, UI.
[x] Session boundary recorded (tasks/sessions/npc-story-events-idea-20260919.json); the checker's
    crossings with worktree lanes B/C/D are recorded in it (new files only).
[~] I read the §1 row docs this session: product vision (the-game.md, the-loops.md, decisions.md
    Product vision + Standalone-first rows), DESIGN-GATE itself, story-scene ideal and map,
    trade-network §7.4, world-graph §3.10–3.11 and §8.2. The Delve, world, economy, power, effects,
    battle and actor-layer rows were read by survey agents in this session, not by the writer; their
    load-bearing claims were re-checked against code.
[x] I checked decisions.md for a lock (Product vision, Standalone-first, PvzActivity rows).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this doc: 0 HIGH (56 citations; the two proposed-file
    citations carry the (new) marker). definitions.md's two HIGH findings (lines 774, 830,
    FoundationHarness.cs) predate this change and are not in this session's fence.
[x] Claims verified against code, not comments. Where a comment is quoted, the code was checked
    (ImportDungeonDomains, MarkRoom, WriteQuestOffer, EventDeck callers: grep, this session).
[x] I read the surrounding section of every rule quoted.
[x] No constraint reported as "moves goldens" or "needs sign-off"; nothing was assumed.
[x] Nothing contradicts a §2 invariant.
[x] No assertion pins a population count (the 53/54 figure is a reading, reported, not a test).
[x] No event-refreshed cache is introduced.
[x] No acceptance criterion; idea phase.
[x] Actor numbers: relationships grant access by default; any stat effect goes through ActorHub.
[x] No SOLID-violating parallel path: one storylet engine, one quest engine, one relation ladder,
    one personality vocabulary, one scene player.
[ ] New rule registry row: none proposed yet; the spec adds guards for §6.10's preflight rules.
```

---

## Handoff

Next step: `/spec npc-story-events` for a capability map and module specs, once §10 is answered. The
dependency table in §8 is a sequencing fact for `/plan`, not a task list.
