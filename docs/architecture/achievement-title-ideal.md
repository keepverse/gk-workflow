# Achievement + Title — the ideal

**Status:** idea phase, 2026-09-15. Not a spec. No build authorized.

Session: `achievement-title-20260915-7f3a` (worktree). Reading gate satisfied this
session: `docs/guide/the-game.md`, `docs/guide/the-loops.md`, `CLAUDE.md` RPG-layer
+ ActorHub + SOLID rules, `docs/DESIGN-GATE.md` §1 rows (Product vision, Effects
atom, Actions/corpus, Economy, Resources, Status, Elements, Data/SQL, Match/actor
lifecycle, Power/scale, Tunables, Caps), `docs/architecture/software-architecture.md:55-68`,
`docs/architecture/effect-atom/definitions.md:§0-§2`,
`docs/architecture/effect-atom/atom-catalog-ssot.md:§0-§2`,
`docs/architecture/effect-atom/spec-container-schema.md:E5`,
`docs/architecture/power/ssot-power-scale.md:§1-§2`,
`docs/architecture/tunables-ssot.md:§1-§2`,
`docs/architecture/data-architecture.md:§1-§2`,
`docs/architecture/unique-actor-runtime.md:§1-§2`,
`docs/architecture/validation-ssot.md:§0-§1`,
`docs/architecture/economy-principles.md:P1-P15`,
`docs/architecture/empire-economy-ssot.md:§2-§7a`.

## Step 0 — principles, in our own words (binding on every choice below)

- **RPG + empire, lawn first.** The game is an RPG plus empire-building game; the
  lawn is the first core loop that feeds almost everything, not the whole war.
  This idea extends named loops; it never invents a parallel pitch, never makes
  the lawn the whole game, never adds a fourth stock, a player class, a stamina
  gate, or a prestige wipe.
- **Every RPG feature lives in the RPG layer, never by changing what PvZ is.**
  We observe PvZ events and contribute signed deltas back through guarded paths.
  The narrow Unity write surface constrains exactly one thing — persistent
  vanilla stat changes — and says nothing about what an achievement or title may
  do, because titles resolve in the RPG stack (`DamagePacket` → dispatcher →
  shield/combat math → Funnel → FA10) during a match. "Does the lawn support
  titles" is the wrong question; the right ones are: does the RPG layer have the
  channel/atom/runtime (usually yes), and is it wired end to end or inert?
- **Two async systems, deltas not absolutes, record-then-drain.** Hooks record
  and return; decisions happen in a later budgeted drain. Delay is the designed
  degradation mode. No Server FSM sits between `combat.hit` and FA* apply —
  so achievement evaluation is Cold/event-driven, never on the hit path.
- **One power ladder.** Contests read `Θ` (linear, difference-based);
  magnitudes read `P(Θ)`. The §10 inventory is closed: a power-shaped number not
  in it has no permission to exist. Title buffs contribute to existing channels;
  they never invent a second curve.
- **Balance surface is data.** Any number a balance pass would touch lives in
  `gk-core/data/tuning/<domain>.v{n}.json`, versioned, hosts inject, Core reads no file.
  Identity/English lives in sibling `*-catalog.v{n}.json`, never mixed into the
  number file.
- **No hard progression ceilings.** Slot limits are structural (with a comment
  saying why they are not tunable); magnitude caps are soft/configurable;
  absolute bounds throw, never silently clamp.
- **Gameless-first is capability, not the pitch.** Every achievement/title
  surface stays usable with Fusion closed after unlock; the injector may enrich
  (lawn-earned progress), never permanently gate.
- **One ActorHub compose / one read; SOLID is binding.** Title buffs contribute
  via registered Hub subsystems / atom readers or consume Hub output only —
  never a private fold. A second composer, a private ChannelMods writer, or an
  "adapters forever" seam is a defect even with approval. Extend the gate, don't
  fork it.
- **Ledger before balance; determinism is economic.** Every stock mutation
  carries a dedupe key from a durable fact; yields compute inside the turn step
  from state (virtual turns for world scope), never wall-clock accrual the hash
  cannot see.
- **Contract + closed enums, never populations.** Achievement/title *kinds,
  scopes, trigger names* are closed vocabularies a developer changes (pin them).
  Achievement *rows, title rows, earned counts* are derived populations content
  ships (never pin counts).

## Which loops this extends

- **Spine A — level up and power** (titles as build expression, no class).
- **Spine B — creature summon and fusion** (actor titles on unique specimens).
- **Spine C — item collection and progression** (reward bundles: demons, items,
  titles; fixed vs randomized pools).
- **Places 3/4/5 — farm/hunt/defend + world-map adventure + world stage**
  (empire-scope achievements/titles, virtual-turn clock).
- **Place 7 — quests and events** (hidden achievements, failure-branch curses).
- Combat depth hangs on places; titles feed it, they are not an eleventh loop.

## What this is

A plugin-based achievement system with a central Achievement Hub. Game
mechanisms (building, combat, collection, world turns, delves later) register
achievement definitions and title definitions as data. Earning an achievement
grants an optional or mandatory reward bundle (unique demons, items, titles;
fixed sets or randomized pools). Titles are atom effect containers: empire
titles equip in the Empire Achievement Hall for empire-wide buffs (multi-slot);
actor titles equip on unique actors instead of physical items (dedicated menu,
slot-limited); some titles are permanent un-equippable passives (honors) or
negative curses (e.g. killing innocents). Any mechanism can register custom
titles. Scopes today: **empire** and **unique-actor** only; the registry is
shaped for future scopes without a rewrite.

Player language: "do notable things, earn named titles, wear the ones that fit
the plan — and live with the ones you can't take off."

## What already exists

### Built

- **Container mechanism.** `effect_container` / `effect_container_atom` /
  `effect_container_pool` + `rarity` + `effect_affix` tables ship with kind
  index — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:20-63`. Fixed core
  (determinism) + weighted pool with per-class rolls and one-per-group
  (loot) — `docs/architecture/effect-atom/spec-container-schema.md:17-64`.
  Containers are mechanism, not content (`RpgStore.Containers.cs:12-13`).
- **Atom vocabulary.** Closed kinds (18) with attach points and runtime table —
  `docs/architecture/effect-atom/atom-catalog-ssot.md:58-80`. Selection is
  seeded `Instantiator.Draw` over `container.Pool`; models author affixes
  (bundles of existing atom ids), never magnitudes or new ids —
  `atom-catalog-ssot.md:24-36`. Units fixed: power/defense/shield in game
  units, accuracy/dodge/crit in resolver points (÷100), chance per-mille,
  durations ms — `docs/architecture/effect-atom/definitions.md:75-83`.
- **Durable specimens + ownership roots.** UniqueActor Cold FSM +
  `rpg_unique_*` DDL + deploy/bind/loadout + equipment→`mods_json` grants +
  specimen XP + roster FE —
  `docs/architecture/unique-actor-runtime.md:1-6`. Single item ownership root
  (`rpg_item`/`rpg_item_stock`; scopes are overlays, never second ownership
  tables) per scoped-inventory SSOT (`decisions.md` Scoped inventory row).
- **Ledger/dedupe pattern.** Soul ledger `UNIQUE(player_id, reason, dedupe_key)`
  — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:661-675`; activity/XP same shape
  (`:443-444`, `:521-522`); contract tribute one dedupe-keyed row/day —
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:108-158`.
- **Clocks.** World virtual turns (End Turn commits all orders); expeditions
  wall-clock by design; lawn live time — `docs/guide/the-loops.md:11-21`.
  Yields compute inside step from state (determinism lock).

### Wiring gap

- **Achievement seam reserved but inert.** `AchievementStatPlugin`
  (`rpg.achievement`, Order 200) registered with empty `Contribute` and
  `InertReason "Achievement system unbuilt; seam reserved, not yet a P0 for any
  program."` — `gk-core/src/FusionRpg.Core/Stats/Plugins/StubStatPlugins.cs:39-46`
  (sibling inert seams: `rpg.item`, `rpg.buff` `:48-64`; seam-coverage contract
  `IDeclaredInertContributor` `:7-10`). This is a wiring gap: the contribution
  point exists, nothing flows through it. Never report as an architectural
  limit.
- **`stat.derived` execution is runtime-dependent.** Lawn Full, battle Full,
  sim Partial (Replace/Flag miscomposed as Flat — needs `Priority` on
  `BoundDerivedAtom`) —
  `docs/architecture/effect-atom/atom-catalog-ssot.md:65`. Title buffs on
  derived channels inherit this exact shape.
- **Container-kind vocabulary is convention-closed, not SQL-closed.** Grammar
  pins `item|trait|skill|species-passive|patron|world-buff` —
  `docs/architecture/effect-atom/definitions.md:41`,
  `gk-data/packs/fusion/data/seed/items/_registry/naming.v1.json:36`; SQL has `ix_effect_container_kind`
  but no CHECK — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:36`. Adding
  title kinds is a reviewed vocabulary widening (DESIGN-GATE atom row), not a
  migration surprise. No `title.*` / `achievement.*` kinds exist today (grep
  `src/`: only assembly/window `Title=` and almanac `title` promotion prose).

### Real gap

- No Achievement Hub (registry + evaluation + grant fan-out), no achievement /
  bundle / title tables or JSON contracts, no empire-hall or actor-title equip
  surfaces, no multi-title stacking rule, no virtual-turn expiry, no
  fixed-vs-pool bundle roller for achievement rewards, no hidden/tiered/
  prestige shapes, no curse/removal ritual, no per-scope slot grammar beyond
  the 15-role gear precedent.

## Prior art (numbers, formulas, documented failure modes — with sources)

- **Anatomy: signifier + completion logic + reward.** 1000+ hrs observation over
  9 games; every achievement needs ≥1 signifier, completion logic, ≥1 reward;
  multi-requirement logics common. Habbo tiers: forced order, badge replaced per
  level, progress resets, cost rises per level. (Hamari et al., 2011,
  academia.edu/20684792.)
- **Failure catalog.** Grind without purpose ("Kill 10,000 Goblins"); divorced
  from core loop/narrative; completionist-only tuning; vague text; punishing
  failure/restrictive play; technical: fails to trigger, no retroactive credit,
  platform inconsistency. Spectrum: introductory → mid → mastery → secret;
  always show progress ("50/1000"). (designthegame.com, Avoiding Common
  Achievement Failures.)
- **Platform budgets (Google Play Games).** Max 400 achievements lifetime; 2000
  pts total; multiples of 5; ≤200 per achievement; reserve headroom for future
  content. ≥4 achievable in first hour; ≥40 lifetime; incremental over standard;
  hidden sparsely (spoilers only); tier marathons need ≥10 sessions (e.g.
  1k/5k/10k). States: hidden / revealed / unlocked; offline unlock + sync.
  (developer.android.com/games/pgs/achievements.)
- **Graduated layers beat binary.** 3-star count-up (Angry Birds 2009 → Candy
  Crush/Two Dots/Marvel Snap): 1 good, 2 better, 3 exceptional; replay effect
  proves growth (Octalysis CD2). Badges = difficulty/scarcity (CD2). Collection
  sets = visible incompleteness, empty slots do the work (CD4); tier
  collectibles Bronze/Silver/Gold/Platinum; show `???` slots, never which tier
  goes where; badge-from-collection is the bridge but a minority of badges.
  Hidden 4th star only after 3 (Hades Titan Blood, Balatro Gold Stake, Spire
  Ascension 20). (Yu-kai Chou, Graduated Achievement Design.)
- **Cogmind (GDM, 2018).** 6 categories + tiers 1–3; records highest difficulty
  per achievement (no list bloat: don't duplicate per difficulty); Events
  category entirely hidden; **31.2% hidden overall**; no negative-experience
  achievements except hidden ones earned naturally ("don't reward tedium");
  vague-but-guessable middle ground when full hiding kills discovery; first-death
  achievement as sting-remover + play-base census.
  (gamedeveloper.com/design/designing-and-building-a-robust-comprehensive-achievement-system.)
- **WoW titles.** One displayed at a time via Titles tab despite many earned
  (warcraft.wiki.gg/wiki/Title). Feats of Strength: 0 pts, unearned hidden
  (warcraft.wiki.gg/wiki/Feats_of_Strength). Seasonal: Gladiator 2300+,
  removed end of season unless re-qualified; season-unique permanent but
  time-gated (wowhead Keystone Victor 2026-04-08: weekly region-best keeps
  title only while holding record; achievement permanent). Account-wide with
  named exceptions; meta-achievement progress shared (wowhead The Entitled).
  Prestige ladder economics: P1 22k honor, +44k each; max 25+50 ≈ 1.12M
  (wowhead Prestige guide).
- **CK3 traits/modifiers.** Data-driven `common/traits`: categories
  (personality/education/commander/lifestyle/fame/health…), leveled commander
  traits ×4 (L2 doubles, L3 triples +1 Advantage, L4 quadruples +2 Advantage
  +1 Martial); flat vs percent modifier types; custom modifiers with
  `show_as_percent/is_good/is_hidden/max_decimals` presentation flags
  (ck3.paradoxwikis.com/Traits; ck3cheats.com/trait; ck2.paradoxwikis.com/Static_modifiers).
- **RetroAchievements discipline.** No achievement spam (group stages by theme,
  not per-stage); clear > reach (code "clear stage", not "reach stage");
  progression order is synergy/show-off signal; challenge > progression >
  grind; grind only with second purpose (FFV Chicken Knife); collections need
  judgment (9999→500 if unfun). (docs.retroachievements.org achievement-design.)

## The shape

### Hub + registry (Cold, event-driven — never Hot)

There is no new "Hub" composer. The achievement program is a Cold service that
evaluates durable facts and writes ledger rows; anything that changes an actor
combat/derived magnitude contributes through the one existing gate — registered
`IActorStatSubsystem` / atom readers with non-empty ContributionSourceIds — or
consumes Hub output only, never a private fold (one ActorHub compose, SOLID
binding). Empire-scoped magnitudes (yields, upkeep shares, conduit rates) are
not ActorHub inputs at all: they flow through the existing economy harness
(`loam-calc` style measurement, Production/Pressure steps), where loam remains
the throttle on every map faucet. The service never sits between `combat.hit`
and FA* apply (overlay lock). Lawn progress arrives as past events, same as
every RPG input.

Unlocks are exactly-once on `(scope, definitionId, definitionRevision, factId)`
— the same discipline as soul-ledger `UNIQUE(player_id, reason, dedupe_key)`.
Evaluation is at-least-once Cold with idempotent ledger appends, so replays,
re-ingests, world-turn recomputes and Snapshot re-runs grant nothing new.
Achievement grants never re-trigger evaluation themselves (no self-loop: a
soul/XP grant from an achievement is a faucet that already named its sink in
the same definition). Triggers enumerate their FULL set including the key-set
move (new definition revision, new player, specimen bind, corpse-cache move,
scope-to-scope move), each with its own order-independent criterion.

### Definitions are data, Seedsmith-compatible JSON

- `achievement_id` grammar `^achievement\.[a-z0-9-]{1,64}$` (closed prefix,
  bounded length, no leading/trailing dash, no tier suffix inside the id —
  tiers are rows, not id hacks; open population of rows — validation-ssot:
  pin the grammar, never the count). Empire and actor scopes share one
  namespace with a collision rule: same id in two scopes is rejected at load.
- Registration is versioned data, not code: number shapes in
  `data/tuning/achievement-titles.v{n}.json`, identity/English in the sibling
  `*-catalog.v{n}.json` (never mixed), hosts inject, Core reads no file; a
  missing tunable or catalog is a load rejection naming it, never a default.
- Each definition: `scope` (`empire` | `unique-actor` today; each new scope a
  reviewed registry change with migration + old-build behavior stated — never
  silent reservation), `scopeKey` (player id vs specimen instance id —
  unique-actor binds the durable instance, not the live ptr), `trigger`
  (closed verb vocabulary with per-verb payload schema:
  `counter-reach{counter, window}`, `threshold-cross{channel, thetaRef}`,
  `collection-complete{setId}`,   `turn-reach{turn}`, `event-seen{factKind}`,
  `challenge-flag{flag}`), `persistence`
  (`permanent` | `ladder` | `turn-window`), `reearnScope`
  (`never` default | `world` | `season`), `visibility`
  (`revealed` | `hidden` | `vague` — vague shows teaser text only),
  `tier` (ladder rung, forced order à la Habbo; highest tier recorded, never
  one row per difficulty), `rewards` (bundle ref with dangling-ref rejection,
  optional/mandatory flag with default `optional`), and per faucet a
  mandatory `sink:{stock, reason}` (economy P1).
- Seedsmith authors identity only (names, flavor, family picks); all magnitudes
  table-owned — same split as item pipelines. Model picks existing atom ids for
  title bundles, never new ids or magnitudes (atom-catalog pool rule).

### Reward bundles: fixed sets + randomized pools

Reuse the container shape, don't invent a second roller: a bundle is
`fixed core` (deterministic grants) + `weighted pool` drawn by the one
existing roll path (`Instantiator.Draw` semantics — seeded, per-budget RNG,
one-per-group exclusion; the roll unit is an affix bundle, not a bare atom),
wired through the effect-pipeline program's instantiate call, never a parallel
draw. Determinism inputs are stated: roll seed, catalog revision, content
`Θ`, content fingerprint — same inputs, byte-identical outputs. Grants reach
the game only through existing apply paths (Funnel → FA* / Intent after
Admit / CapPolicy); PowerVector stays a scale-free authoring budget (never
multiplied by content scale, or it double-counts).
Contents address existing ownership roots only: unique-demon mint enters the
specimen FSM at `Roster` (never straight to `ActiveBound` or a live ptr —
children carry snapshot pools/status/flags with exactly-once settlement, and
`entity:{ptr}` grants withdraw on death before ptr reuse); item mint enters
the single `rpg_item` root with its scope overlay + capacity check (empire
uncapped, unique-actor 15-role, corpse-cache moves never copy); title grant
enters the title registry below.
Randomized pools show odds tier (`Bronze/Silver/Gold/Platinum`-style slots as
`???` until earned — Chou) and never promise what the pool can't draw: an
undrawable promise is a load-time rejection naming the group, never a runtime
fallback or clamp (absolute bounds throw).
Every reward faucet names its sink in the same definition (economy P1); soul /
essence rewards compete with existing sinks (P6), bulked through loam
throttle where territorial (P2).

### Titles are atom containers with a scope and a slot grammar

- Container identity splits two axes that must not be smuggled into one:
  `container_kind` (`empire-title`, `actor-title` today — reviewed widening,
  convention + registry + DESIGN-GATE atom row move together) and a separate
  `scope` field (`empire` | `unique-actor`). Future names are never
  "reserved but rejecting": a new scope ships with its registry change,
  migration, and old-build behavior, or it does not ship. Titles reuse the
  18 existing atom kinds — no new kind for "title damage." Family vs group
  vs variant membership is explicit per title row: family = balance family,
  group = one-per-group exclusion key (defaults to `(family_id, variant)`),
  variant = element/channel discriminator — so "additive within a family,
  one-per-group across variants" has a membership rule, and a title in two
  families is rejected at load.
- **Empire titles:** earned → Hall inventory; equip **multiple** (multi-slot);
  each contributes through the economy path to empire-scoped magnitudes
  (yields, upkeep shares, conduit rates) — magnitudes read `P(Θ)` exactly
  once at a single owned site (no base-scale + share double-scale; per-mille
  shares divide last). Additive stacking across slots is bounded by soft caps
  in tuning, never open-ended.
- **Actor titles:** unique specimens earn titles; dedicated equip/unequip menu
  (FE via `/idea-ui` later); slot-limited (structural limit with comment, e.g.
  N title slots alongside the 15-role gear grammar — capacity, not a
  progression ceiling; gear validation, FE, and contest accounting migrate
  together, including closed-set sentinels). Equip writes a binding
  (bookkeeping, withdrawable); the single owner of list order, reorder
  determinism, and reorder replay is stated at spec time (container `seq`
  stays authoring order only).
  Display vs mechanics separate by tuning decision (one worn display title,
  stacking benefits underneath — WoW tab): the worn-selection rule (highest
  tier wins) is stated, so sheet, HUD, and telemetry agree.
- **Lifecycle:** `permanent` or `turn-window` on the **virtual** clock.
  Windows are relative (`validTurns` from equip/grant, evaluated inside the
  turn step — P13), never absolute turn ranges and never wall-clock on world
  scope (expedition wall-clock stays expedition-only). Save/load mid-window
  and replay of the granting turn are idempotent on distinct dedupe keys for
  grant vs equip vs expire. Expiry states its destination (back to Hall,
  re-equippable; Hall-full and dead/fused-actor behavior stated) and is
  withdraw + telemetry, never a silent snap.
- **Un-equippable permanents + curses:** honors bind as passive containers
  without occupying a slot, keyed to a durable grading fact (injury-style
  grading time, attacker-less applies excluded from the power contest by
  construction — `wound.*`/`nerve.*` precedent is grading-time application,
  not loadout equip, and honors follow that shape: no Hot path, no contest
  input). Curses are **hidden**, earned naturally for Cold-recorded
  transgression facts (never detected between hit and FA), removable only via
  a priced ritual (soul + essence sink — P1/P6; insufficient funds, partial
  payment, repeat-offense-while-cursed, and deleted-actor cases stated at spec
  time), with vague-but-guessable text. Any mechanism registers custom titles
  through the same registry + validation with per-row isolation (one bad row
  rejects with cause, never fails the whole load closed) and cross-mechanism
  duplicate-id rejection; unknown kind/scope rejects at load with cause (7
  silent failures → rejections discipline).

### Advanced shapes adopted (industry-standard, fitted to this repo)

- **Hidden + vague tiers:** `revealed` (default), `hidden` (spoiler/organic —
  ~30% ceiling per Cogmind 31.2%), `vague` middle ground (teaser text, e.g.
  "Discover what you really are").
- **Tiered ladders:** forced order, badge replaced per rung, progress resets,
  cost rises (Habbo); record highest difficulty/tier per achievement, don't
  duplicate rows per difficulty (Cogmind).
- **One-worn-many-owned (WoW Titles tab):** actor scope wears one display
  title but benefits stack per tuning — display vs mechanics separated, decided
  in tuning not code.
- **Seasonal/temporary (WoW Gladiator/Keystone Victor):** `turn-window`
  titles for ladder seasons; achievement permanent, title held while record
  holds. Permanent-unique (`Realm First`-style) reserved, not built.
  World-scoped bundles never sink loam (optional pools included — load
  rejection); bundle seeds carry `world_id` (+turn for pools).
- **Prestige without wipe (loops forbid wipes):** prestige is a new ladder
  rung set on the same permanent record (4th star invisible until 3 earned —
  Hades/Balatro/Spire), never a reset of the summoner. The permanent record
  is player-scoped and banks across worlds (roster/souls/essence do; loam and
  holdings do not): empire achievements about non-banking holdings are
  per-world feats with highest-tier memory (Cogmind highest-difficulty
  record), re-earnable each world without becoming dead unlocks. Turn-window
  titles are world-scoped and die with the map; no loam in any world-scoped
  bundle, optional or mandatory (load rejection).
- **Meta-achievements:** collection-complete triggers Hall sets; completing a
  set earns a badge-title, but set-completion badges stay a minority of all
  titles (Chou bridge constraint). Set→meta loads build a DAG and reject
  cycles with cause naming ids; evaluation runs one topological pass.
- **Anti-spam + order-as-signal:** group by theme, clear-not-reach,
  progression order recorded for show-off (RetroAchievements).

### Alternatives rejected (with reason)

- **Titles as statuses:** statuses are timed actor instances with ICD/
  resistance/contagion (`status-ssot`); titles are loadout choices with slots
  and ledger provenance. Forcing titles through StatusRuntime invents a second
  equip system inside the wrong runtime (SOLID fork).
- **Titles as items in the vault:** items have economy/salvage/craft semantics;
  actor titles explicitly replace physical items per requirements. Sharing the
  ownership table is fine; sharing the item lifecycle is the defect.
- **Hot evaluation on hit/kill:** violates the Server-between-hit-and-FA ban
  and G5 record-then-drain; achievements read facts, never the live hit.
- **Wall-clock title expiry on world scope:** breaks replay determinism (P13);
  virtual turns only.
- **Fourth stock / title XP currency:** fails P4 (no bottleneck pair) and the
  loops page (exactly three stocks). Title costs price in souls/essence/loam.

## Tunables (every number this introduces, and who owns it)

All in `data/tuning/achievement-titles.v{n}.json` (numbers) +
`data/tuning/achievement-titles-catalog.v{n}.json` (displayName, reading,
icon/hudToken, flavor — never in the number file):

- `hallSlots` (structural capacity, commented non-tunable rationale per slot
  grammar) vs `equipShareMilli` per title family (tunable magnitude shares).
- `tierNeedCounts[]` (counts per rung), `poolWeightsMilli` per bundle (per-mille), `group`
  exclusions, `dropOddsDisplay` tiers.
- `validTurns` per time-limited title (turns, integer), `titleRitualPrice.{souls, essence}`
  for curse removal (per element, `omni` fallback), `respecPrice` analogue for
  title unequip if priced.
- `hiddenShareCapMilli` (operational guideline ≈312‰ from Cogmind 31.2% —
  a design reading, never a CI gate over a population ratio),
  `firstSessionBeats` (first-session onboarding Beats, never wall-clock
  hours on world scope).
- `stackRule` (additive / one-per-group / unique), `seasonTurnWindows` (relative
  turn ranges — never calendar seasons on world scope), `powerRef` (always `Θ`/`P(Θ)` —
  no new curve; coefficients live in existing power tables).
- `lifetimeBreadth` is an operational canary/reading (like the hidden share),
  never a versioned tuning key and never asserted in tests.

## What this deliberately does not decide

- Exact achievement list / title names / flavor (Seedsmith content passes).
- FE composition (Hall layout, actor menu, gauges, chips) — `/idea-ui` phase.
- Spec tables, endpoints, guard tests, rollout waves — `/spec` phase.
- Drop rates beyond shape (measured via economy harness, `loam-calc` style).
- Future scopes (`legion`, `sector`, delve `party`) beyond reserving names.

## Open questions — decided 2026-09-15 (owner delegated: "free creative, choose best")

1. **Scope of v1: BOTH scopes.** Empire + unique-actor ship together. Reason:
   the requirements demand both, the registry shape costs the same once, and
   shipping one would prove nothing about the scope split — the load-bearing
   risk. Future scopes stay registry-changes, not rewrites.
2. **Hall slots N = 3.** Three loadout choices mirror the three stocks and
   force real tension (which doctrine, not whether). Tunable shares do the
   balancing; capacity stays structural with comment.
3. **Actor: one worn display, stacking benefits.** Fiction (the name you wear)
   separates from mechanics (what computes); worn rule = highest tier wins so
   sheet, HUD, and telemetry agree. Full contribution expansion lives in the
   later sheet audit.
4. **Curse ritual: souls + transgression-matched essence** (≈ one fusion-tier
   cost — hurts, never gates). Repeat offenses climb the ladder rung (forced
   order, cost rises). Unmatched transgressions price in `omni`.
5. **Hidden share: adopted** — ≈30% hidden ceiling as guideline (never a gate),
   `vague` teaser middle ground, full-hiding only for spoilers and organic
   moments.

## Gaps in the supplied logic (found during enrichment)

- No evaluator placement (fixed: Cold service on facts, never Hot; no new
  composer — Hub/SOLID § reconciled above).
- No dedupe/replay story (fixed: `(scope, definitionId, revision, factId)`
  exactly-once; grants never re-trigger; distinct grant/equip/expire keys).
- No clock choice (fixed: relative virtual-turn windows, in-step).
- No stacking/slot rule (fixed: family/group/variant membership + structural
  slots + soft caps + worn-selection rule).
- No registry openness (fixed: closed kind/scope/trigger + payload schemas,
  per-row isolation, duplicate rejection, versioned tuning/catalog split).
- No failure-mode handling (fixed: hidden/vague caps as guidelines,
  anti-spam, no tedium-reward, priced curse ritual with edge cases, seasonal
  title-vs-achievement split, cycle guard).

## Audit 2026-09-15 — doubt-driven reconciliation (cross-model skipped by owner)

Three fresh-context adversarial reviews returned ~30 findings. Classification:
2 contract-misreads (fixed by stating single-owner list order and worn-title
rule), 24 valid + actionable (folded above: Hub→service rename, kind/scope
split, P(Θ)-once site, membership rule, relative windows, expiry destination,
honor/curse facts, per-row isolation, banked semantics, guideline-not-gate
reframe, cycle guard), 3 valid trade-offs documented (minimal 2-scope v1
widens the container vocab before any consumer proves it — accepted: kinds
land with the registry change or not at all; vague visibility stays
subjective by design; curse transgression taxonomy stays open until first
content pass), 2 noise (a "second Hub" that the rename removes; a "difficulty
axis" the doc never introduces — highest-tier memory is per-ladder, not a
global difficulty). Stop condition met: findings folded, no open actionable
item. Honest gaps remaining: transgression fact taxonomy, Hall-full and
dead-actor destinations at spec granularity, exact N slots (owner Q2), exact
curse prices (owner Q4).
