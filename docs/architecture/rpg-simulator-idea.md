# An RPG simulator — what exists, what it must cover, and a first-cut idea

**Status:** idea, not a spec. Nothing here is decided; **§7** lists the decisions only the owner can make.
**Program:** `rpg-simulator` (new) · **Session:** `rpg-sim-idea-a` · **Fence:** this doc + `tasks/**`.
**Method:** `.agents/skills/idea-refine/SKILL.md`. Every section below is labelled with its phase —
**Phase 1** understand & expand (divergent), **Phase 2** evaluate & converge, **Phase 3** sharpen.
**Gate:** [`DESIGN-GATE.md`](../DESIGN-GATE.md) read this session, plus the rows for *Product vision*,
*Standalone / web RPG*, *Stats*, *Anything that changes what an actor's numbers ARE*, *Economy*, *Data /
SQL* and *Proving a feature works live*. §8.4 is the §5 checklist, completed.

**Genre and loop (required by the idea skill's repo note).** `guide/the-game.md` is the vision SSOT: an
**RPG plus empire-building extension for Plants vs. Zombies Fusion** (`the-game.md:10`). A simulator is
an **instrument, not a feature**: it extends no loop of its own and must not invent one
(`the-loops.md:170`, "What a feature owes this page"). It exists so the **spine** loops (A level up and
power, B summon and fusion, C item collection — `the-loops.md:28-62`) and the **places** loops (2 idle
expeditions, 4 world map, 5 world stage, 6 the Delve — `the-loops.md:74-147`) can be *played forward* and
measured without the lawn game. Standalone-first already makes this a capability requirement, not a new
one: *"every RPG feature must be fully playable and CI-provable with the PvZ game closed"*
(`standalone-rpg-map.md:43`).

---

## 1. The problem, restated (Phase 1 — Understand & Expand)

### 1.1 The owner's framing

> *"our work on this program dont use pvz much but a lot of rpg feature and we lack of simulator"*

### 1.2 How Might We

> **How might we let an agent (or CI) play the whole RPG *forward* — days of a save in seconds, for a
> real player record, with the PvZ game closed — and read the result back through the same query paths
> the player's own UI uses?**

### 1.3 One paragraph

Most of this repository's work is RPG-domain — progression, creatures, items and sockets, aptitudes,
passives, delves, the empire, notifications — and that domain is exercised today in exactly three ways:
**unit tests** with hand-built inputs, an **in-process E2E factory** that boots the real server and pokes
one endpoint, and the **live path** (game → injector → server), which needs a legal install, MelonLoader,
the injector and a server. None of the three plays the game *forward*. A unit test cannot see that a
route nothing reaches is unreachable; an E2E test that posts one request and asserts one response cannot
see that the aptitude allocation it wrote was read by a cache that only refreshes on a different edge; and
the live path costs a slot, an install and the owner's eyes. The result is that the defects this repo
actually suffers from — **reachability** (a socket route exists and no sanctioned path can put a socketable
item in a save: `tasks/strain-splice-host-todo.md:979`, SSH4.9-P2) and **cross-family sequencing** (a
specimen bound after its allocation is composed differently from one bound before: `DESIGN-GATE.md` §2.16,
three shipped instances) — are invisible until somebody plays, and playing is the most expensive thing we
have. A simulator is the instrument that makes "play it forward" cheap: **one scenario, many steps, real
domain path, read-back at the end.**

### 1.4 The specific RPG families it must serve

| # | Family | Why a forward-play instrument is the missing one |
|---|---|---|
| 1 | Progression / level-ups | XP arrives from *events*; level-up is a consequence of a sequence, never of one request |
| 2 | Items + instances | An instance only exists after a drop/materialise/equip sequence |
| 3 | Sockets + words (combinations) | The family whose end-to-end reachability is *currently unproven* (SSH4.9-P2) |
| 4 | Aptitudes (+ species/unique scopes, respec) | Allocation → compose is an **ordering** problem (`DESIGN-GATE.md` §2.16) |
| 5 | Passive tree | Allocate → bind atoms → reach a fight; the corpus is generated and the binding is a separate seam |
| 6 | Empire level + world turns | Turn-based, so "play" means *pressing End Turn N times*, not waiting |
| 7 | Expeditions | Wall-clock dispatch → due → collect; the only "wait" that is genuinely time |
| 8 | Delves | A room graph + interactive battles + haul/extract, i.e. a long stateful session |
| 9 | Notifications | Produced as a *side effect* of turns and cache changes; never the subject of a test today |
| 10 | Souls / economy | Faucets and sinks only reconcile when a session runs long enough to spend |

### 1.5 Sharpening questions — answered from the repo, or deferred

The skill says not to proceed until the audience and success criteria are known. This is an unattended
run, so the questions are answered from what the repository already asserts, and anything that is a
genuine owner decision is **deferred to §7 rather than guessed** (recorded as a `decision` note):

- **Who is it for?** Agents (a lane that must prove a feature before handing it over), CI (a gate that
  can fail without a game install), and the owner (a way to look at a long-run consequence without
  playing it). Evidence: the live-probe standard exists precisely because agents kept grading their own
  work (`docs/contributing/live-probe-standard.md:9-21`).
- **What does success look like?** A scenario that a human reads in one screen, that drives only real
  endpoints/services, and whose result is a **read-back through the normal query path**
  (`live-probe-standard.md:59-72`), not a response body.
- **What is the real constraint?** Not the game — `FusionRpg.Core` is Unity-free and `SimEngine` +
  `FUSIONRPG_SIM=1` already drive the pipeline without the game (`standalone-rpg-map.md:9`). The
  constraints are **time** (expeditions and turns are wall-clock), **substrate** (the sanctioned
  in-memory store helper lives in a *test* project: `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:37`),
  and the **never-fabricate** rule (`live-probe-standard.md:41`).
- **Why now?** Two open rows are blocked on exactly this gap: SSH4.9's live probe has no sanctioned
  route to a socketable item (`tasks/strain-splice-host-todo.md:979-991`), and the same shape recurs
  wherever a family's only entry point is real play.

---

## 2. What already exists — survey, not re-derivation (Phase 1)

Nothing below is proposed; each row is what the repository already has, with what it does and does not
cover. **Read this before §4** — three of the five divergent options are variations on a row here.

### 2.1 The in-process real-server factory — the closest thing that exists

`gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9` — `RpgApiFactory : WebApplicationFactory<Program>`.
`Program` is public (`gk-core/src/FusionRpg.Server/Program.cs:2129`), so this boots the **real** server: real DI,
real boot seeding, real HTTP, real SignalR, real SQLite.

- Sets `FUSIONRPG_SIM=1`, `FUSIONRPG_NO_BROWSER=1`, `FUSIONRPG_DATA=<temp dir>` (`RpgApiFactory.cs:16-18`),
  and repeats them in `ConfigureWebHost` (`:66-71`).
- Seeds the **real committed species corpus** before the host starts (`:34-52`), because
  `gk-core/src/FusionRpg.Server/Program.cs:572` calls `CreatureSpeciesCatalog.Configure(store.BuildCreatureSpeciesSnapshot())` and
  that **throws on an empty roster** (`gk-core/src/FusionRpg.Core/Creatures/SpeciesSnapshot.cs:43-48`). The
  comment at `RpgApiFactory.cs:19-33` records that this was a suite-wide pre-existing failure, not one
  test's problem.
- Dispose is leak-proof and file-bound (`:75-90`) — the real server reads `FUSIONRPG_DATA` from disk.
- One shared instance per collection, serialized: `[CollectionDefinition("e2e", DisableParallelization =
  true)] public class E2ECollection : ICollectionFixture<RpgApiFactory>` (`FoundationE2ETests.cs:307-308`).
- 47 of the 49 `.cs` files in the project reference it (including the factory and its tuning bootstrap).

**Covers:** the whole server boot pipeline, every endpoint, every catalog load, persistence, push.
**Does not cover:** playing forward. Each test resets and pokes; nothing owns a *session*.

### 2.2 `SimFlags` and `/api/test/*`

- `gk-core/src/FusionRpg.Server/SimFlags.cs:8` — `Enabled` iff `FUSIONRPG_SIM == "1"` (`RpgConstants.SimEnvVar`,
  `gk-core/src/FusionRpg.Contracts/Dtos.cs:257`).
- `gk-core/src/FusionRpg.Server/Program.cs:2051` — `if (SimFlags.Enabled) app.MapSimAndProbes();` — the whole
  `/api/sim` + `/api/test` surface exists **only** in sim mode.
- `gk-core/src/FusionRpg.Server/SimEndpoints.cs:13` — the `/api/sim` board group: a Unity-free board
  (`/board/start`, `/plant/spawn`, `/zombie/damage`, `/shield/grant`, `/state`, …).
- `SimEndpoints.cs:130-135` — the family seed helpers, each defined next to its owner:
  `/api/test/seed-souls-demo` (`SoulEndpoints.cs:27`, clamped at 1..1_000_000 against SQLite REAL
  corruption), `/web-match` (`WebMatchService.cs:762`), `/expedition-due`
  (`ExpeditionEndpoints.cs:347`), `/api/test/world/create` (`WorldEndpoints.cs:586`), plus fusion and
  contract.
- `SimEndpoints.cs:136` `/api/test/reset` (store reset + patron cache clear) and `:144`
  `/api/test/snapshot` — one composite read of health, stats, events, runs, players, entities, mowers,
  types, recipes and the sim board.
- **The only time control that exists:** `RpgStore.ForceExpeditionDue`
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202`) — a SIM-only `UPDATE rpg_expeditions SET
  due_utc=…`. There is no clock seam anywhere else; world turns advance because a client posts a command,
  which is why they need no time control at all.
- **What it refuses:** `SimService.Guard()` (`gk-core/src/FusionRpg.Server/SimService.cs:26-30`) returns **409
  `live injector connected`** when `store.LiveInjector`, which is `Source == injector && heartbeat < 5s`
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1206-1210`). The sim surface *turns itself off* when a real game
  is attached — the honest-scope property the whole idea must preserve.
- **One thing is not behind the flag:** `/api/sim/effect` is mapped unconditionally (`gk-core/src/FusionRpg.Server/Program.cs:2053`,
  `SimEffectEndpoints.cs:14`), because the offline effect host needs no board and no store.
- **The existing "fake injector" seam:** `gk-core/src/FusionRpg.Server/Program.cs:1492` — when `!store.LiveInjector && SimFlags.Enabled`,
  the server drives `SimEngine.SpawnZombie` in place of sending `pvz.spawn.extra` to an injector. This is
  precedent *and* the exact hazard §6 is about.

### 2.3 The sanctioned store substrate

- `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:37` — `Create()`: in-memory, already `Init()`ed, unique
  shared-memory database names, no temp dir. `:72` `CreateWithPreInitHot` for migration shapes; `:95`
  `CreateFileBacked` for file semantics only, with a leak-proof dispose that **throws** on a failed delete
  (`testing-standard.md` R3).
- It lives in a **test project**. `FusionRpg.E2E.Tests.csproj` consumes it by `<Compile Include=…>` link
  rather than a project reference — so a `src/` or `tools/` consumer has no clean way to reuse it today.
- `gk-core/src/FusionRpg.Data/Seed/SeedImportRunner.cs:130` — `RunSelfHealing(store, searchStartDir)`, called at
  boot from `gk-core/src/FusionRpg.Server/Program.cs:949`; **never throws** (a broken seed tree must not stop a player's server
  booting). `PassiveTreeImportRunner.RunSelfHealing` follows at `gk-core/src/FusionRpg.Server/Program.cs:976` with the identical
  contract. In a dev checkout the tree resolves by walking *up* from the exe, which is why the copy rules
  in `FusionRpg.Server.csproj` only ever mattered for published installs.

### 2.4 `gk-core/tools/CombatSim`

`gk-core/tools/CombatSim/README.md:8` states its one rule: **"This tool contains no combat math."** Every number
comes out of `gk-core/src/FusionRpg.Core` through `CombatDamageDispatcher.DispatchInstant` via
`FoundationHarness`. 14 commands (`gk-core/tools/CombatSim/Program.cs:15-30`), scenarios as JSON, `--set domain.key=value`
patches tuning *in memory* and refuses a key the file does not contain, and a closed-form twin
(`Analytic.cs`) that reads the same tuning and adds only the expectation.

**Covers:** combat math, shields, statuses, resources, aptitude/tuning balance. **Cannot:** persistence,
roster, progression, or anything that needs a `RpgStore`.

### 2.5 `gk-core/tools/SquadHarness` (+ `gk-core/tests/FusionRpg.SquadHarness.Tests`)

`gk-core/tools/SquadHarness/Program.cs:35-39` — `--seed` is **required and has no default** ("a seed nobody chose
behaves like one somebody did"). Modes: `duel`, `squad`, `transfer`, `erosion`, `concentration`,
`crossunlock`, `soultrack`, `budget`, `verify`; the real measurement types live in their own files and are
reached from the test project by `ProjectReference` (`gk-core/tools/SquadHarness/Program.cs:1-14`). It drives Core's `TreeModel`,
`SquadMatch`, `SoulTrackModel`, `Erosion`.

**Covers:** squad-vs-wave, the passive tree, soul track, budget sweeps, determinism.
**Cannot:** a real store, a real roster, a real endpoint.

### 2.6 Offline simulation primitives already inside `src/`

- `gk-core/src/FusionRpg.Core/SimEngine.cs:11` — the server-side board. It mounts the **real** `ActorHub`
  (`:24`, the sole Hot compose gate — `actor-hub-ssot.md:877`), the real `ShieldRuntime`/`ShieldGate`
  (`:37-39`) and a direct `IHpDeltaSink` (`:39`) because *"sim has no funnel by design"* (`:34`).
- `gk-core/src/FusionRpg.Core/Effects/FoundationHarness.cs:12` — the offline Foundation harness (39 files in
  `tests/` + `tools/` use it): `EffectBag`, `EffectFunnel`, seeded RNG, fake clock, recording sinks.
- `gk-core/src/FusionRpg.Core/Effects/SimEffectHost.cs:13` — the same shape as a host with plugins and a board.
- `gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:81` — **a declarative scenario layer already
  exists**: `EffectScenarioDto` steps executed against `SimEffectHost`, with golden plan comparison, and
  **49 JSON fixtures** under `gk-core/tests/fixtures/effects/scenarios/`.

**Covers:** the effect/status/combat pipeline without Unity, deterministically.
**Cannot:** anything above the effect layer — no roster, no store, no progression, no turns.

### 2.7 The headless battle producer — the strongest existing precedent

`gk-core/src/FusionRpg.Server/WebMatchService.cs:102` — `RunWebMatchAsync`: server-authoritative setup from the
real roster → durable log-before-ingest idempotency anchor → real `BattleEngine.Resolve` → dedicated
single-transaction ingest → contract loyalty → broadcast; a repeat correlation **replays** the stored
setup rather than re-fighting. `RunPlannedMatchAsync` (`:187`) is the expedition-collect shape.

- `BuildSquad` (`:527`) is the roster gate: contracts settled first, `squad.toolarge` /
  `squad.duplicate` / `squad.unknown-specimen` / `squad.unbound` / `squad.insubordinate` refusals.
- `:570-574` — **an empty roster falls back to a deterministic `Synthetic` squad** (`:713`), documented
  as "SIM convenience". This is a fabrication *by design*: it proves the engine resolves, never that the
  roster path works.
- `SweepUnresolved` (`:246`) refuses to re-resolve an interactive match with AI decisions, and refuses a
  report logged on another platform or another engine/ruleset version.

**Covers:** a whole RPG battle end to end, including ingest, runs, XP, souls and the boot-recovery sweep.
**Cannot:** anything *before* a squad exists (acquire, level, equip) or *after* it (dispatch, turn).

### 2.8 Delve battle sessions

`gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs:191` starts a real interactive battle in-process on a
background thread with a decision trace; `DelveBattleSession.cs:255` `Declare` is the live turn;
`DelveBattleEndpoints.cs:23` is status-only. The session is cancelled-and-discarded on freeze.

**Covers:** an interactive fight with real decisions, no Unity. **Cannot:** the delve *loop* — rooms,
pack, haul, extract — without a client driving it.

### 2.9 Scripted-client precedents (a driver against a *real* process)

- `gk-core/scripts/probe_sim_shield.py:71-75` — posts a whole shield scenario to `/api/sim/*` and reads
  `/api/sim/state`. A scenario *is* just a script of posts.
- `gk-core/scripts/smoke_player_pack.py:190` — boots a **published** `FusionRpg.Server.exe` as its own
  process with **SIM off** and probes it. This is the honest end of the spectrum: nothing is faked.
- `gk-core/tests/FusionRpg.E2E.Tests/WorldTurnFixtureTests.cs:32` — **six scripted world turns** on the
  `first-light` template, chosen to produce one entry of each visibility class, and asserted before the
  fixture is trusted. A hand-written play session, in a test, once.

### 2.10 The live path — what still genuinely requires the game

| Behaviour | Why it needs the game | Where it lives |
|---|---|---|
| The injector's Hot loop (record-then-drain, budgeted) | it runs inside the game process | `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs`, `EventDrainHost.cs` |
| Applying a composed number to a Unity entity | Unity object graph, single writer | `gk-fusion/src/FusionRpg.Injector/Stats/EntityStatWriter.cs:15`; guard `gk-fusion/scripts/guard-single-writer.py` |
| Entity lifecycle edges (spawn/die/ptr reuse, bind) | IL2CPP pointer reuse is the thing under test | `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs` |
| Injector-side caches refreshed on SignalR edges | the cache lives in the game process | `gk-fusion/src/FusionRpg.Injector/Stats/TreeBoundAtomsCache.cs`; `DESIGN-GATE.md` §2.16 |
| Real gameplay as an event *producer* (kills, waves, mowers) | the hook fires from the game | `gk-fusion/src/FusionRpg.Injector/GameHooks.cs` → `EventIngest` |
| Game-authored text capture (almanac prose) | it is read off the game's own UI | `gk-fusion/src/FusionRpg.Injector/AlmanacTextCapture.cs` |

`gk-fusion/tests/FusionRpg.Injector.Tests` exists (10 test files) and is **not in CI** — it needs interop refs.
So today the injector half is neither CI-covered nor cheaply probeable, which is a *second* reason the
simulator's line must be drawn at the process boundary rather than blurred across it.

### 2.11 CI coverage, measured

- `ci.yml:291` runs `FusionRpg.E2E.Tests`. The E2E factory **is** a CI gate.
- The file runs **60 distinct test projects** (counted by `grep -o "tests/[^ ]*\.csproj" | sort -u | wc -l`).
  ⚠ `AGENTS.md:155` says **13**; that prose predates the `core-split-wiring` E5 (TVB5.7) Core split. The
  CI file is the machine-guarded one — `gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs:18`
  (W5) fails the Guard suite if a Core project on disk is missing from `ci.yml`. Filed for routing in
  `tasks/rpg-simulator-todo.md`.
- **Whole families have no E2E HTTP coverage through the real `Program`.** Grepping the E2E project for
  `aptitudes`, `passive-tree`, `notifications`, `items/workbench`, `items/equip`, `empires/` returns
  **zero files**. Those families are covered in `FusionRpg.Server.Tests` (101 files) against a **minimal**
  in-process `WebApplication` built by the test itself — e.g. `AptitudeEndpointsTests.cs:23` — which
  proves the endpoint and the store but **not** the real boot pipeline, catalog load, DI graph or
  background workers.

---

## 3. Feature inventory — where the logic lives, what a simulator must drive (Phase 1)

"End to end" here means: a real player record, the real endpoint or service, the real domain and
persistence, and a read-back through the same query path the web FE uses.

| # | Family | Logic lives | A simulator must drive | Closest coverage today |
|---|---|---|---|---|
| 1 | **Progression / level-up** | curve + reasons `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:40,77,161`; writes `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:2846` `InsertEvents` → `:3380-3468` event-kind dispatch; reads `RpgStore.Progression.cs:546,606,629`; routes `gk-core/src/FusionRpg.Server/Program.cs:1422-1451` | produce the **event sequence** that awards XP (board → kill → run end), then read `/api/rpg/progression/{id}/summary` and `/ledger` | `RpgProgressionE2ETests.cs`; `/api/test/seed-rpg-progression-demo` (`SimEndpoints.cs:240`) |
| 2 | **Souls / economy** | `RpgStore` soul ledger + `SoulEarnPolicy`; routes `SoulEndpoints.cs:11` | award through the real policy, spend through the real sink, read the ledger | `SoulsE2ETests.cs`; `/api/test/seed-souls-demo` (`SoulEndpoints.cs:27`) |
| 3 | **Items / instances** | `gk-core/src/FusionRpg.Core/Items/**` (drops, materials, power, uniques); `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs`, `RpgStore.Import.cs`; routes `ItemSurfaceEndpoints.cs:104,127`, `ItemCardEndpoints.cs`, `ItemPreviewEndpoints.cs` | acquire a real instance through the instance/loot pipeline, equip it, read the armoury | ⚠ **no E2E HTTP test**; `FusionRpg.Core.Items.Tests` + `FusionRpg.Server.Tests` |
| 4 | **Sockets + words (combinations)** | `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:25`; `CombinationCorpus.cs`; `RpgStore.Sockets.cs:98,126`; boot `CombinationBoot.cs:26`; routes `WorkbenchEndpoints.cs:309,321,337` | socket a real chassis, insert a gem, have the word **fire** and reach the sheet | ⚠ **unreachable end to end** — `tasks/strain-splice-host-todo.md:979-991` |
| 5 | **Aptitudes** | `AptitudeEndpoints.cs:33` (commander), `:77` (unique), `:116` (respec); `RpgStore.Aptitudes.cs:68,112`; tuning `gk-core/data/tuning/aptitudes.v10.json` | allocate → **bind** (both orders) → read the sheet; the §2.16 edge is the whole point | ⚠ no E2E; `FusionRpg.Server.Tests/AptitudeEndpointsTests.cs` (minimal host) |
| 6 | **Passive tree** | `PassiveTreeEndpoints.cs:84` (allocate), `:109` (preview), `:149` (bound atoms); `RpgStore.PassiveTree.cs:54,97,224`; corpus `gk-data/packs/fusion/data/generated/passive-tree/**` | allocate nodes → atoms bind → reach a fight → read the bound-atom surface | ⚠ no E2E; `FusionRpg.Core.PassiveTree.Tests`; `gk-core/tools/SquadHarness` (Core-only) |
| 7 | **Empire level** | `EmpireEndpoints.cs:27`; `RpgStore.EmpireLevel.cs`; free respec `RpgStore.EmpireFreeRespec.cs` | level an empire through real XP, spend the free respec, read the level row | ⚠ no E2E |
| 8 | **World / empire turns** | `WorldEndpoints.cs:26` (group), `:586` (`/api/test/world/create`); `RpgStore.World.cs`, `RpgStore.WorldTurns.cs` | create a world from a template+seed, post N real commands, press End Turn N times, read the report | `WorldTurnE2ETests.cs`, `WorldTurnFixtureTests.cs:32` (6 scripted turns) |
| 9 | **Expeditions** | `ExpeditionEndpoints.cs:263` (group), `:347` (`/expedition-due`); `RpgStore.Expeditions.cs:202`; resolver `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs` | dispatch a real squad → make it due → collect → read rewards + progression | `ExpeditionE2ETests.cs` |
| 10 | **Delves** | `DelveEndpoints.cs:51` (start), `:57` (projection); `RpgStore.Delve.cs`; sessions `DelveBattleSessionManager.cs:191` | start a delve, walk rooms, fight (interactive), haul, extract, read the run | ⚠ no E2E HTTP; `FusionRpg.Server.Tests/Delve*Tests.cs` |
| 11 | **Notifications** | `NotificationEndpoints.cs:20,27,39`; `RpgStore.Notifications.cs:65,238,290`; producer `gk-core/src/FusionRpg.Server/Notifications/NotificationPublisher.cs:11`, `WorldTurnNotificationPump.cs`, `NotificationBootCatchUp.cs` | advance a world turn → publisher appends durably → read the page and the cursor | ⚠ no E2E |
| 12 | **Creatures / fusion / contracts / patron** | `CreatureEndpoints.cs:16`, `FusionEndpoints.cs:21`, `ContractEndpoints.cs:19`, `PatronEndpoints.cs:21`; `gk-core/src/FusionRpg.Core/Creatures/**` | summon → fuse → contract → field; the roster the battle producer reads | `SummonE2ETests.cs`, `FusionE2ETests.cs`, `PatronE2ETests.cs`, `CreatureE2ETests.cs` |

**What the table is saying.** The families with E2E coverage are the ones a *single request* can express
(creatures, souls, world commands, expeditions). The families with **no** E2E coverage are the ones that
need a **sequence** (items, sockets, aptitudes, passives, delves, notifications, empire level) — which is
the same list as "the families that keep producing ordering and reachability defects". That correlation is
the argument for this idea.

---

## 4. Divergent options (Phase 2 — Evaluate & Converge)

Five options, deliberately different in *where the driving happens* and *what is real*. Each row states
what it covers, what it cannot, and its cost. They are not exclusive — §5 picks a combination.

### Option A — Grow the in-process E2E factory into a "play session"

Keep `WebApplicationFactory<Program>` as the host; add a **session helper** that owns a scenario (a list
of steps), a real player record, and a read-back at the end. Concretely: one new fixture/helper in
`gk-core/tests/FusionRpg.E2E.Tests`, plus per-family step helpers, sharing the existing `[Collection("e2e")]`
host (`FoundationE2ETests.cs:307`).

- **Covers:** everything the real boot pipeline covers, with zero new production surface, in CI, today.
- **Cannot:** control time honestly (it would inherit `ForceExpeditionDue`'s SQL rewrite,
  `RpgStore.Expeditions.cs:202`, which is a store bypass); cannot be reused outside a test project,
  because `DataTestStore` lives in one (`DataTestStore.cs:37`) and is consumed by a `<Compile Include>`
  link; cannot be driven by an agent as a tool.
- **Cost:** smallest possible — no product code, no new project, no new invariant. It is where the
  smallest first slice should live (§5.3).

### Option B — A headless "sim host" server mode

A `gk-core/tools/RpgSim` (or `src/FusionRpg.SimHost`) console app that boots the **real** `Program` via
`WebApplicationFactory<Program>` (public at `gk-core/src/FusionRpg.Server/Program.cs:2129`) with an in-memory store, and runs a
**scenario file**: steps in, read-backs out, one process per scenario batch.

- **Covers:** everything A covers, plus it is a **CLI an agent can run** — the `gk-core/tools/CombatSim` /
  `gk-core/tools/SquadHarness` precedent, including `--seed` discipline (`SquadHarness/Program.cs:35-39`).
- **Cannot:** reach the injector half; cannot be a player surface.
- **Cost:** a new `tools/` project; `Microsoft.AspNetCore.Mvc.Testing` + a content-root setting (the E2E
  project gets the content root for free, a tools project does not — **not attempted in this lane, see
  §8.2**); the sanctioned in-memory store helper has to be shared properly rather than by a compile link.

### Option C — A scripted client against a **real server process**, SIM off

The `gk-core/scripts/smoke_player_pack.py:190` shape: boot a published or `dist/` server as its own process with
`FUSIONRPG_SIM=0`, and drive it over HTTP exactly as the web FE would.

- **Covers:** the **published** path — copy rules, catalog presence, boot order, the things
  `FusionRpg.Server.csproj`'s many "missing-copy-rule" comments say have silently broken before.
- **Cannot:** use `/api/test/*` at all (not mapped without SIM), so it can only seed through
  **player-facing** routes — which is a feature, not a bug, and also means it cannot do what SSH4.9-P2
  needs until a sanctioned acquisition route exists.
- **Cost:** needs a server binary and a port; slow; state is a real data dir; harder to assert on and to
  clean up. This is the right shape for a **release** check, not for the everyday loop.

### Option D — A fake injector / game shim

A client that joins the SignalR `injector` group, heartbeats as `RpgConstants.SourceInjector` so
`store.LiveInjector` goes true (`RpgStore.cs:1206-1210`), drains the command inbox
(`InjectorCommandInbox.cs:12`) and synthesizes the event envelopes a real run produces.

- **Covers:** the **server's half of the injector contract** — that a `unique.binding.clear` is sent, that
  a `pvz.stats.reload` carries the right revision, that the heartbeat/health surface is right.
- **Cannot:** prove anything about the injector — by construction it is the wrong side of the boundary
  (`live-probe-standard.md:25-37`). It also **turns the sim surface off**: `SimService.Guard()`
  (`SimService.cs:26`) starts returning 409 the moment it heartbeats, so it collides with A and B.
- **Cost:** moderate; and it is the option most likely to be *misused as evidence*. If it is ever built it
  must be labelled **Game Injector Debug scope substitute**, and its results must never be reported as
  "the injector works".

### Option E — A scenario/DSL layer (content, not code)

Promote the existing effect-scenario precedent — `EffectScenarioRunner.cs:81` + 49 JSON fixtures under
`gk-core/tests/fixtures/effects/scenarios/` — into the general shape: a JSON scenario is a list of steps
(`{op, args}`), the runner is thin, and the assertion is a **read-back path + expected predicate**.

- **Covers:** authoring. A scenario becomes a reviewable artifact a human reads in one screen, and the
  same file can be replayed by A, B or C — the runner is the only difference.
- **Cannot:** do anything on its own; it is a format, not an engine.
- **Cost:** low to define, but it must not become a **second language** for the domain: every `op` must
  name a real endpoint or service, and the runner must contain no domain math (the `CombatSim` rule,
  `gk-core/tools/CombatSim/README.md:8`).

### Option F (the combination worth naming) — A + E + a clock seam

A as the substrate, E as the interface, plus the one production change the idea actually asks for: make
the **wall-clock seam injectable** so an expedition can be "3 hours later" without an `UPDATE` against
`rpg_expeditions`. `TimeProvider` is the .NET 8 primitive; the consumers are few and nameable
(`RpgStore.Expeditions.cs:202` is the current workaround, plus the notification cursor
`RpgStore.Notifications.cs:363` and the world-turn clock).

- **Covers:** time honestly, and turns the "SIM-only timer rewind" hack into an honest abstraction.
- **Cannot:** be done without touching `FusionRpg.Data` (so it is a real change with a real review cost).
- **Cost:** one seam + a SIM gate so a real server's clock can never be faked.

---

## 5. Convergence (Phase 2 → Phase 3 — Sharpen & Ship)

### 5.1 Recommended shape

**Option A as the substrate now, Option E as the interface, Option F as the only production change — and
Option D explicitly refused.**

1. **The host is the real server, in-process.** `WebApplicationFactory<Program>` is the only thing in this
   repo that boots the real pipeline (real DI, real catalogs, real seeding, real background workers,
   real SQLite) without a game and without a published binary. Reusing it means the simulator cannot
   drift from production *by construction*: there is no second boot path to keep in sync.
2. **The unit is a scenario, and a scenario names real routes.** Steps are `{op, args}` where `op` resolves
   to an existing HTTP route or an existing DI-resolved service. The runner may **sequence** and **read**;
   it may not compute. This is `gk-core/tools/CombatSim`'s one rule (`README.md:8`) applied one layer up, and it
   is the whole defence against becoming a second implementation.
3. **The assertion is a read-back.** Every scenario ends by reading state back through the same GET route
   the web FE calls — `live-probe-standard.md:59-72` item 3 — never a response body and never a
   debug-only accessor.
4. **Time is the one seam worth adding.** `ForceExpeditionDue` (`RpgStore.Expeditions.cs:202`) is a
   SIM-only `UPDATE`; that is a store bypass and it is the reason "the sim can jump the clock" is not
   honest today. A `TimeProvider` seam behind `SimFlags` retires it. Everything else that looks like time
   is not time: world turns advance because a client posts a command, so they need no clock at all.
5. **The injector stays out of scope, permanently, in wave 1.** Option D is refused because the two debug
   scopes are the exact confusion the live-probe standard was written to end
   (`live-probe-standard.md:13-21`), and because a fake injector *disables the sim surface it needs*
   (`SimService.cs:26`).

### 5.2 Why not the others

- **B alone** is A with a CLI bolted on and a new content-root problem to solve; A first proves the
  scenarios are worth having, and B is a packaging decision that can follow with no rework.
- **C alone** cannot seed and cannot use `/api/test/*`, so it cannot reach the families in §3 at all. It
  is the right *release* check and the wrong everyday instrument.
- **D** is the option that most easily produces a false pass, and §6.1 explains why it must not exist in
  wave 1 at all.

### 5.3 The smallest first slice that would prove it

**Slice 0 — no product code, one new E2E scenario file. This is the slice to build first, because it
proves the shape with zero risk and zero new surface.**

*Scenario `first-session-forward`:* create a player → **award souls through the sanctioned seeding
surface `POST /api/test/seed-souls-demo`** → summon a creature through the real summon route → read the
roster back → dispatch a real expedition → make it due → collect → read
`/api/rpg/progression/{id}/summary`, the soul ledger and the run list back.

> **Erratum (2026-09-23, lane `sim-t3-2`, RS-F1) — this step read *"award souls through the real
> `/api/souls` path"*, and there is no such route.** `SoulEndpoints.MapSouls`
> (`gk-core/src/FusionRpg.Server/SoulEndpoints.cs:9`) maps exactly two routes, both GETs — the balance and the
> ledger — and there is deliberately no generic award endpoint ("Spends are feature-owned (summoning
> etc.), never generic", `SoulEndpoints.cs:6`). Souls are *earned* by gameplay
> (`SoulEarnPolicy.Reasons`, `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:49`) and spent by
> feature-owned routes, so the sanctioned award step for a scenario is
> `POST /api/test/seed-souls-demo` (`gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29`) — a fixture surface that
> performs the **real** `RpgStore.AwardSouls` write with reason `seed`, which is exactly why the RS4
> honesty guard allowlists it by name and why the corpus says so in its own `notes`. Earning the souls
> instead is not available either: a real match before a roster exists fields the `Synthetic` squad
> (`gk-core/src/FusionRpg.Server/WebMatchService.cs:570-574`), which is the fabrication slice 0 exists to refuse.
> **Owner ruling D3 (b) stands:** an unreachable condition is a finding, not a licence for a new route —
> so whether the soul economy should grow a player-facing award route is the *soul-economy* program's
> question, carried as **RS-F25** in `tasks/rpg-simulator-todo.md`, not something this program adds.

Every step of that exists today: souls (`SoulEndpoints.cs:11`, `/api/test/seed-souls-demo` for the award),
summon (`FusionEndpoints.cs:21` / `CreatureEndpoints.cs:16`), expedition dispatch and collect
(`ExpeditionEndpoints.cs:263`), due (`:347`), progression read (`gk-core/src/FusionRpg.Server/Program.cs:1422`). The battle it resolves
goes through the real `WebMatchService` (`WebMatchService.cs:102`) and the real `BattleEngine`.

**Why this slice and not a bigger one:** it crosses four families (economy, roster, expeditions,
progression) using only routes that already have E2E coverage, so if it fails, the failure is the
*shape* — the thing under test — not an unrelated missing route. It also immediately makes the
`Synthetic`-squad question answerable: the scenario must assert that the squad it fought with came from
the roster it just built, which is precisely the fabrication line §6.1 draws.

**Slice 1 — one family with no E2E coverage today, chosen for its known defect:** the **socket/word**
family (SSH4.9-P2). A scenario that acquires a socketable instance, sockets it, equips it and reads the
word back will *fail today* — and that failure is the deliverable: it converts a blocked live probe into a
reproducible, CI-visible defect. This slice is the reason to build the simulator.

**Slice 2 — the clock seam (Option F):** retire `ForceExpeditionDue` and let an expedition tick be
modelled honestly, which is what makes long-session economy claims (faucet/sink reconciliation,
`empire-resource-ssot.md`) checkable at all.

**Explicitly not in the first program:** the injector, the browser, balance, and any new `/api/sim/*`
route. See §6.

---

## 6. Risks and anti-goals (Phase 3)

### 6.1 The fabrication risk — the one that matters

`live-probe-standard.md:41` is binding: **"A debug API may trigger a real operation. It must never
fabricate the state that operation is supposed to produce."** A simulator is a machine for *producing
state*, which makes it exactly the kind of tool that rule was written about. Three concrete ways this idea
goes wrong, and the rule that prevents each:

1. **Minting the subject.** A scenario that inserts a socketable item, a specimen, or an allocation
   directly is the 2026-09-13 T14 defect with more steps (`live-probe-standard.md:9-21`). **Rule:** every
   scenario's *subject* must be created by a route a real player could have used; a scenario may skip
   tedium (a timer, a click) but never a service, a validation or a write.
2. **Reading the wrong half.** A scenario that drives the server and then reads a `SimEngine` snapshot has
   proven the server's half only. **Rule:** every read-back names the same query path the web FE uses, and
   a scenario that touches the injector is labelled **Game Injector Debug scope** in its own name.
3. **The `Synthetic` squad.** `WebMatchService.cs:570-574` fabricates a squad when the roster is empty —
   correctly, for engine coverage. A simulator that inherits it silently would report "the battle worked"
   for a roster it never used. **Rule:** a scenario that means to exercise the roster must assert the
   roster was used (the `InstanceIds` returned by `BuildSquad`, `WebMatchService.cs:527`), or refuse.

### 6.2 Drift — the second-implementation risk

The failure mode is a simulator that re-implements a rule because it was easier than calling the real
one, and then disagrees with production forever. This repo has paid for that class twice: the
`BattleStatComposer`/`ActorHub` dual compose (`DESIGN-GATE.md` §2.15, fused and deleted 2026-09-13) and the
`Analytic.cs`/`Simulator.cs` pair inside `CombatSim`, which is safe *only* because both read the same
tuning and one adds nothing but the expectation (`gk-core/tools/CombatSim/README.md:113-124`).

**Rules, mirroring `CombatSim`'s own:** the runner contains **no domain math**; it calls endpoints and
services. If a scenario needs a number the API does not return, the fix is a route or a service call, not
a copy of the formula. And the simulator is a **driver over existing routes** — it does **not** add a
parallel endpoint family, for the same reason `AGENTS.md` forbids a parallel MCP toolset ("debug tooling
must adapter-wrap the same endpoints/services").

### 6.3 Anti-goals — what this is not

- **Not a game-engine simulator.** No Unity, no injector, no PVZ. `SimEngine` (`SimEngine.cs:11`) already
  covers the board; the simulator drives the *RPG*, which lives above it.
- **Not a balance tool.** `gk-core/tools/CombatSim` and `gk-core/tools/SquadHarness` own balance, determinism hashes and
  sweeps. A simulator that also optimizes is two tools fighting over one report.
- **Not a UI.** No browser, no screenshots. The web FE's Playwright suite already covers what a player
  sees; a simulator asserts *state*.
- **Not a new debug surface.** No new `/api/sim/*`, no new `/api/debug/*`. The `/api/test/*` group stays
  the seeding surface it already is.
- **Not a licence to delete the live path.** A simulator green never replaces a live probe for an
  injector claim (`live-probe-standard.md:25-37`).
- **Not a new loop, and not a new player-facing route.** Per `the-loops.md:170`, a feature owes this page
  a loop; an instrument owes it nothing and must not invent one. Slice 1's socket defect is fixed by a
  **sanctioned acquisition route** (a product decision, SSH4.9-P2's own ask) — the simulator *proves* that
  route, it must never *be* the route. If it becomes the only way to reach a feature, we have built a new
  instance of the defect we set out to detect.

### 6.4 Smaller risks

| Risk | Shape | Mitigation |
|---|---|---|
| **CI cost** | a real host boot per scenario | one host per collection, as `[Collection("e2e")]` already does (`FoundationE2ETests.cs:307`); scenarios are cheap once booted |
| **Non-determinism** | a scenario fails on a coin flip | seeds are required and recorded — `SquadHarness/Program.cs:35-39`'s rule, and `WebMatchService` already logs seed + content hash per match (`WebMatchService.cs:125-128`) |
| **A faked clock leaking into production** | the sim's clock becomes the player's | the seam is `SimFlags`-gated, and a real server's `TimeProvider` is `TimeProvider.System` by construction |
| **Store bypass becoming the norm** | `ForceExpeditionDue`'s `UPDATE` spreading to more tables | §5.3 slice 2 retires the one that exists; a new one should be refused in review |
| **Test-only substrate** | `DataTestStore` living in a test project forces a `<Compile Include>` link | name it as the friction it is (§2.3); a proper shared home is a small, separable change |
| **Scenario rot** | a scenario that passes for the wrong reason | assert the *subject's identity* (the instance id, the specimen id) in the read-back, not just a value |

---

## 7. Open Questions — decisions only the owner can make

Each is answerable in one line.

1. **Where does it live** — a `gk-core/tools/RpgSim` CLI (the `CombatSim`/`SquadHarness` precedent, agent-runnable),
   or an E2E fixture inside `gk-core/tests/FusionRpg.E2E.Tests` (no new project, CI-native)?
2. **Is the first slice allowed to be a test file** with no product code, or must the simulator be a tool
   from day one?
3. **Is a `TimeProvider` seam approved** for the wall-clock consumers (expedition due, notification
   cursor), retiring `ForceExpeditionDue`'s `UPDATE` — or must the simulator keep using the store rewrite?
4. **May a scenario run while a live injector is connected** (read-only, no `/api/test/*`), or must the
   simulator hard-refuse exactly as `SimService.Guard()` does (`SimService.cs:26`)?
5. **Is a sanctioned acquisition route in scope for this program** (SSH4.9-P2's ask, a real player-facing
   grant path), or does that belong to the item program with the simulator only proving it?
6. **Where do scenarios live** — `gk-core/tests/fixtures/rpg-scenarios/**` (the effect-scenario precedent,
   `EffectScenarioRunner.cs:81`), `gk-data/packs/fusion/data/seed/**` (content, committed, generator-owned), or `tools/**`?
7. **Golden files or assertion-only?** The effect scenarios compare golden plans; a long RPG session's
   golden would be a large artifact. Assertion-only is cheaper but weaker.
8. **Does the scenario suite join CI** as a test project (making it gate #61), or run nightly?
9. **Is the browser in scope at all** — HTTP-only (state) or also the Playwright surface (what the player
   sees)?
10. **Does wave 1 model the injector's *contract* at all** (Option D, refused in §5.1) — or is "no game,
    HTTP only" the whole first program?
11. **Does the simulator own a shared, non-test home for `DataTestStore`** (so a `tools/` consumer can use
    it without a `<Compile Include>` link), or is the compile link acceptable?
12. **Who reviews a scenario's honesty** — is "the subject was created by a real route" a checklist item on
    the scenario file itself, or an automated guard?

---

## 8. Evidence, and what is NOT proved

### 8.1 Evidence contract

Every factual claim in this document carries a `file:line`. Where a claim is a count, it was counted, not
recalled — see §8.3 for the counts that are readings rather than constants.

### 8.2 NOT proved — read this before acting on any of the above

- **No test suite was run.** This lane's fence is `docs/architecture/**` + `tasks/**`; nothing was built,
  executed, or probed. Every claim about what the code *does* is a read, not a run.
- **No server was booted**, no simulator exists, no scenario was written.
- **The tools-project content-root question is unverified.** `Program` is public (`gk-core/src/FusionRpg.Server/Program.cs:2129`) and
  `Microsoft.AspNetCore.Mvc.Testing` is a normal package, so a `tools/` project *should* be able to host
  the real server — but the content root that the E2E project gets for free was **not attempted** here.
  Option B's cost line is therefore an estimate.
- **Whether `DataTestStore` can be consumed by a non-test project** was not attempted; only the current
  `<Compile Include>` link was read (`FusionRpg.E2E.Tests.csproj`).
- **I did not read `RpgStore` in full**, nor every endpoint. §3 names each family's *entry points*, which
  is what a simulator must drive; it is not an exhaustive file list.
- **I did not verify that every scenario step in §5.3 exists as a working route today** — the routes are
  cited, but a "create a player → summon → dispatch → collect" chain was not executed end to end. The
  claim is "every step is cited and E2E-covered individually", not "the chain runs".
- **The 60-project CI count is a `grep` over `ci.yml`**, not a CI run.
- **The E2E coverage gaps are `grep` results** over `gk-core/tests/FusionRpg.E2E.Tests/*.cs`; a family could be
  exercised indirectly through a helper whose name does not contain the family word.
- **`[Collection("e2e")]` sharing semantics** (one factory per collection, serialized) were read from
  `FoundationE2ETests.cs:307-308`; I did not confirm that every E2E class joins that collection.
- **No comparison was made against the sibling idea lane's document.** If a sibling
  `docs/architecture/rpg-simulator-idea-a.md` exists in another worktree, it was not visible here.

### 8.3 Readings, not constants

- **CI test-project count = 60.** A reading of `.github/workflows/ci.yml` at `574418ab4`; the file is
  machine-guarded (`CoreTestProjectPolicyTests.cs:18`) so it grows with the repo. `AGENTS.md:155`'s
  **13** is stale and filed in `tasks/rpg-simulator-todo.md`.
- **E2E project = 49 `.cs` files, 47 referencing the factory.** A reading; the project grows.
- **Effect scenario fixtures = 49.** A reading of `gk-core/tests/fixtures/effects/scenarios/`; scenarios are
  content and the count grows.

### 8.4 Design gate §5 checklist

```
[x] I identified the subsystem(s) this touches: none — this is an idea document; it changes no code.
    The subsystems it *describes* are the RPG server surface, the E2E/test substrate, and the tools tree.
[x] Session boundary recorded: tasks/sessions/rpg-sim-idea-a.json (mode worktree, branch cmdc/sim-idea-a,
    ABSOLUTE worktree path, paths = this doc + tasks/rpg-simulator-todo.md + the record itself).
    `verify-change.ps1 -Session rpg-sim-idea-a` reported `[session-boundary] clean for 'rpg-sim-idea-a'`.
[x] Read every doc in the §1 rows for those subsystems, this session: DESIGN-GATE.md (full),
    guide/the-game.md, guide/the-loops.md, architecture/standalone-rpg-map.md,
    architecture/actor-hub-ssot.md (the sim/one-compose-gate lines), contributing/live-probe-standard.md
    (§1-§4), plus the tools' own READMEs and the CI workflow.
[x] Checked decisions.md for a lock covering this: no decision covers an RPG simulator; the locks this
    idea must respect are named in §6 (SOLID §2.15, ActorHub sole compose gate, never-fabricate,
    standalone-first).
[x] Every factual claim cites file:line.
[x] `python scripts/audit-doc-citations.py --scope docs/architecture/rpg-simulator-idea.md` reports
    no HIGH finding: 137 resolvable citations checked, 0 D1 / 0 D2 / 0 D3 / 0 D4. (First run found 11
    D3 "ambiguous basename" on bare `Program.cs:NNN`; all eleven were re-cited with a full path.)
    `scripts/guard-doc-citations.ps1 -Strict` was NOT run — that guard covers a code move that
    invalidates citations, and this change moves nothing.
[x] The path-owned verification for this lane's three paths ran green:
    `.\scripts\verify-change.ps1 -Paths 'docs/architecture/rpg-simulator-idea.md',
    'tasks/rpg-simulator-todo.md','tasks/sessions/rpg-sim-idea-a.json' -Session 'rpg-sim-idea-a'` →
    exit 0; plan selected docs-and-assistant-config (focused), session-and-program-records (module),
    `doc-citations` for both docs, `guard: session-boundary`, `test: guard` and
    `test: guard guard.doc-boundary`. Results: session-boundary **clean**; doc-citations 0 HIGH;
    `FusionRpg.Guard.Tests` **591 passed / 0 failed** (5 m 5 s); the `guard.doc-boundary` filter
    **4 passed / 0 failed**. "full evidence: CI/nightly/release" was printed, not run — correct for a
    docs-only change.
[x] Verified claims against CODE, not comments (e.g. the sim guard was read at SimService.cs:26-30, not
    inferred from its name; the CI project count was counted, not quoted).
[x] Read the surrounding section of every rule quoted (the live-probe standard's §1-§4 were read in full;
    the §2.16 rule was read with its corollary and its three incidents).
[x] Tested any constraint I am reporting: none reported as a constraint. The measured numbers (60
    projects, 49 E2E files, 49 fixtures) were counted; nothing was asserted about what "would break".
[x] Nothing here contradicts a §2 invariant. The idea *depends* on §2.9 (standalone-first) and §2.15.
[x] No assertion in this document pins a derived-population count. The counts in §8.3 are labelled
    readings, not constants.
[x] §2.16 (edge-refreshed caches): the idea's slice 1 is aimed *at* this invariant — the aptitude and
    bind ordering — and §6.1's rule 1 keeps scenarios from fabricating the state whose ordering is
    under test.
[x] No acceptance criterion fixes an ordering that can vary in real play: §6.1 and Open Question 12 name
    both-orders as the requirement, not a single order.
[x] Nothing here invents a second actor combat compose or a private derived fold. §6.2 forbids the
    simulator from owning any domain math at all.
[x] Does not invent or extend a SOLID-violating parallel path: §6.2 and §6.3 refuse a parallel endpoint
    family, a second boot path and a second debug surface.
[ ] A new rule has a registry row: this document adds no rule and no guard. If Open Question 12 lands a
    guard, that guard owes a row in gk-core/scripts/enforcement-registry.v1.json — named there, not here.
```
