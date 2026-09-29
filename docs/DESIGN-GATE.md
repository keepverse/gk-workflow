# Design gate — read before you propose anything

**Status: binding.** Applies to every session, human or automated, before any spec, plan, proposal,
ADR, audit finding, or sentence beginning "we should".

---

## 0. The rule

**Before you propose a change to a subsystem, you must have read that subsystem's authoritative
documents in the current session, and you must cite them.**

Not skimmed. Not recalled from a summary. Not inferred from a code comment or a filename.

If you have not read them, you do not yet have an opinion. Say *"I need to read X first"* and read it.
That costs one tool call. Proposing against a system you have not read costs the owner an hour of
correcting you, and it is the single most common failure in this repo's history.

**The sequence is: read → verify against code → then propose.** Never propose → get corrected → read.

---

## 1. The reading gate — topic index

Find the row for what you are about to touch. **This table is an index**: one row per topic, in the original order, so a `DESIGN-GATE.md:<line>` citation still resolves to the topic it named. The documents you MUST read, and the mistake sessions actually make, are in the category file the row links to.
Categories are the same 12 used by [architecture/decisions.md](architecture/decisions.md). A topic with no row here falls to **Anything at all**. Categories with no reading row: `transport`, `launcher`.

| If you are about to touch… | You MUST have read | What sessions get wrong |
|---|---|---|
| **Anything at all** | [repo-tooling](design-gate/repo-tooling.md) | |
| **Product vision / what the game is / which loops exist** | [repo-tooling](design-gate/repo-tooling.md) | |
| **How the injector talks to the game** | [game-host](design-gate/game-host.md) | |
| **Where logic may live (server vs injector)** | [game-host](design-gate/game-host.md) | |
| **Combat damage / HP** | [combat](design-gate/combat.md) | |
| **Stats** | [stats](design-gate/stats.md) | |
| **Anything that changes what an actor's numbers ARE — a new stat source, a species/race trait, a title, an aura, a buff, a progression axis, an empire-wide bonus** | [stats](design-gate/stats.md) | |
| **Any cap, ceiling, limit or throttle** | [power-caps](design-gate/power-caps.md) | |
| **Any tunable number (costs, rates, yields, chances)** | [power-caps](design-gate/power-caps.md) | |
| **Any numeric magnitude (types, widths, overflow)** | [power-caps](design-gate/power-caps.md) | |
| **Power / scaling / any magnitude from a level** | [power-caps](design-gate/power-caps.md) | |
| **Effects (Foundation)** | [combat](design-gate/combat.md) | |
| **The atom / Secondary effect layer** | [combat](design-gate/combat.md) | |
| **Affix/container authoring, rolled instances, the L1-L4 resolution model** | [combat](design-gate/combat.md) | |
| **Item rarity, the ten-rung ladder, creature rarity** | [progression](design-gate/progression.md) | |
| **Actions, skills, targeting, action costs or the action corpus** | [combat](design-gate/combat.md) | |
| **PvZ mechanics, the host game's own systems, or "how do other games do X"** | [game-host](design-gate/game-host.md) | |
| **Creature species generation / seedsmith's creature pipelines** | [content-gen](design-gate/content-gen.md) | |
| **General creature vs. unique creature; Commander vs. Patron vs. a Delve party member** | [progression](design-gate/progression.md) | |
| **Economy / currencies / yields** | [progression](design-gate/progression.md) | |
| **Resources / actor pools** | [progression](design-gate/progression.md) | |
| **Status effects** | [combat](design-gate/combat.md) | |
| **Elements** | [combat](design-gate/combat.md) | |
| **Data / SQL / schema** | [persistence](design-gate/persistence.md) | |
| **Match / actor lifecycle** | [world](design-gate/world.md) | |
| **Performance** | [repo-tooling](design-gate/repo-tooling.md) | |
| **Anything that changes what happens in a BATTLE — damage, elements, status, shields, targeting, resources, procs, actions, death, capture, or a new battle mode** | [combat](design-gate/combat.md) | |
| **Anything that decides what an actor does — AI, intent sources, target or action choice** | [combat](design-gate/combat.md) | |
| **Battle / turns** | [combat](design-gate/combat.md) | |
| **World map** | [world](design-gate/world.md) | |
| **Anything a player sees (UI)** | [presentation](design-gate/presentation.md) | |
| **Player menus (band-2 layer bodies, ActorSheet tabs, filter/inspect panels)** | [presentation](design-gate/presentation.md) | |
| **Lawn stage chrome (match HUD, cell stack, occupancy dock, spawn tray, commander combat book, ActorCollection)** | [presentation](design-gate/presentation.md) | |
| **Standalone / web RPG** | [world](design-gate/world.md) | |
| **Proving a feature works live / any `/api/debug/*` or Injector `debug.*` call used as evidence** | [repo-tooling](design-gate/repo-tooling.md) | |
| **A creative run — an agent invents a mechanism and carries it from idea to ship with no human gate (`/creative`)** | [repo-tooling](design-gate/repo-tooling.md) | |

Full map: [README.md](README.md). The capability map of a program is the index of what exists for it —
never guess which spec is active from a filename.

> **⚠️ `docs/design/` is a parallel spec set, and most rows above do not name it.** The rows were
> written from `docs/architecture/`, but `docs/design/` holds per-surface specs — `spec-derived-stat-sheet.md`,
> `spec-magnitude-and-units.md`, `spec-shield-and-elements.md`, `spec-action-layer.md`,
> `spec-equip-and-paperdoll.md`, `spec-item-card.md`, `spec-sockets-and-sets.md`,
> `spec-inventory-and-workshop.md`, `spec-comparison.md` — that **verify their claims against `src/`**
> and are normative for how a number reaches a player.
>
> **Before proposing in any subsystem, check `docs/design/` for a matching `spec-*.md` even when your
> row does not name one.** Added 2026-08-24 after a session wrote twelve specs against derived stats
> without reading either of the two that already covered them — see §4's last two rows.

---

## 2. Load-bearing invariants

These are settled. Re-deriving them from scratch is how sessions arrive at confident wrong answers.
If your proposal contradicts one, you have found either a real architectural change (say so
explicitly, and expect a decision) or your own misunderstanding (far more likely).

1. **Two async systems.** The RPG and PvZ do not share a clock and do not wait for each other. The RPG
   works from **past events**, never current game state, and never guesses it.
2. **Record-then-drain.** Hooks record and return. Decisions happen in a later budgeted drain.
   **Delay is the designed degradation mode**, not a failure to engineer around.
3. **Deltas, not absolutes.** Overlay mutations are signed deltas through the Funnel. Absolute HP/ATK
   from an overlay snapshot is rejected by contract.
4. **Single writer.** All combat writes go through `EntityStatWriter`.
5. **The Funnel is the only Secondary → Bag path.**
6. **SQL only inside `FusionRpg.Data`.**
7. **The game is the simulation, not a thin client** — but that does *not* make the overlay
   latency-bound. See invariant 2. Both halves of this sentence matter.
8. **Foundation is sealed** at its contract version. Secondary builds on top; it does not edit it.
9. **Standalone-first (capability).** Every RPG feature must be playable with the game closed. The
   injector may *enrich* a feature, never *permanently gate* one. This is a **capability and CI**
   rule, not a claim that the lawn is optional flavor — product loops (lawn first core, idle,
   empire, …) live in [guide/the-loops.md](guide/the-loops.md). See `decisions.md` Standalone-first
   and Product vision rows.
10. **Perf is a main-thread problem.** Settled by measurement in 2026-08.
11. **No hard progression ceilings.** Endless grind is the SSOT; caps on magnitudes are removed or
    made configurable soft caps, and absolute bounds throw rather than clamp
    ([architecture/power/ssot-power-scale.md](architecture/power/ssot-power-scale.md) §11).
12. **The balance surface is data.** A number a balance pass would change lives in
    `gk-core/data/tuning/<domain>.v{n}.json`; a structural constant stays a `const` and says why it is not
    tunable ([architecture/tunables-ssot.md](architecture/tunables-ssot.md)).
13. **Magnitudes fit their type's range.** The power ladder is quadratic; per-mille `int` exceeds its
    range at an index reachable in normal play (3,213), so integer magnitudes are `long`. Widen before
    multiplying, divide by 1000 last in integer per-mille math, let integer overflow throw.
    Floating-point is allowed (owner ruling 2026-09-15) — precision is not overflow.
14. **One power ladder.** Every magnitude derives from `P(Θ)` and every contest from `Θ`
    ([architecture/power/ssot-power-scale.md](architecture/power/ssot-power-scale.md)). No subsystem
    owns a private level curve. Contests are decided by *differences*, which is why the contest read
    must stay linear — a geometric curve makes a fixed level gap unboundedly decisive.
15. **SOLID is non-negotiable.** Architecture shape must keep one SSOT per responsibility, extend by
    contribution (not parallel forks), honor Hub/Funnel/Writer contracts, prefer thin contribution
    APIs, and depend on those abstractions — not mode-local concrete composers. An ADR, decision, or
    **PO confirmation that locks a SOLID violation is still a defect** — overturn and fix; never copy
    as “by design.” New proposals that violate SOLID are not allowed. Extending a feature along a
    SOLID-violating seam is not allowed until a remediation plan for that debt is named and sequenced
    first (or the work waits). Grandfathered debt may remain until a named fix program lands — it is
    never a template. First recorded SOLID ADR defect: ActorHub vs `BattleStatComposer`
    (`decisions.md` ActorHub sole Hot overturn; [combat-power-number-ideal.md](architecture/combat-power-number-ideal.md)) —
    closed: fused 2026-09-13 (battle-hub-fuse T6, `69ba6a7b3`).
16. **An edge-refreshed cache must enumerate its FULL trigger set — including the state-entry edge —
    and test every one.** Any cache the injector hydrates from the server on discrete events (not a
    per-frame poll) must, in its spec, list every trigger that can invalidate it, and each trigger
    needs its own test. **The trigger that gets forgotten is the one where the cache's KEY SET moves,
    not its values**: a cache keyed by "currently Bound specimens" is stale the instant a specimen
    binds, even though no allocation changed. Copying a trigger set from a sibling cache is the
    specific trap — a *global* cache (commander allocation) is complete with "refresh on change",
    while a *per-entity* cache with the same shape is not.

    **Corollary for acceptance criteria: a criterion that encodes an ordering only tests that
    ordering.** "After allocate + `AptitudesUpdated`, the Bound unique includes its shares" silently
    assumes the specimen was already Bound; the reverse order (allocate, then bind) is a different
    execution and needs its own criterion. Where order can vary in real play, say **order-independent**
    and test both directions.

    Three shipped instances, all the same shape — cache populated on trigger X, state changed on
    trigger Y: commander reallocation reaching only entities spawned after it
    (`CheatState.cs:98-102`, owner-caught live 2026-08-30); a SignalR reconnect re-joining the group
    without re-syncing caches (`RpgClient.cs:143-147`); and `unique-lawn-wire`'s missing bind edge
    (2026-09-13, §4). Prior art for doing it right:
    [architecture/species-build/spec-allocation-transport.md](architecture/species-build/spec-allocation-transport.md)
    enumerates four refresh paths and makes a stale cache after any of them a **failure**.

---

## 3. Evidence rules

1. **Cite `file:line`.** A claim without a location is an opinion.
2. **Code beats documentation; documentation beats comments. A comment is not evidence.**
   A file comment saying it mirrors another file is not a coupling — open the file and check.
3. **Read the section, not the line.** Before quoting a rule as a general law, read its heading and
   its neighbours. A rule under *"What the Server may do during a run"* constrains the server during a
   run; it is not a universal principle.
4. **Test the constraint before you declare it.** "This would move the goldens" and "this needs owner
   sign-off" are *claims*. Run the suite. An assumed constraint that costs the owner a decision they
   did not need to make is the same defect as a wrong line of code.
5. **Verify counts by counting.** Not by trusting a number written elsewhere in the same doc set.
6. **When you correct something, propagate it.** A fix that lands in prose but not in the sibling
   Structure / Testing / Boundaries block, the map, and the task list has not landed. Re-grep after.
7. **A guardrail validates the contract and closed enums — never a population count or generated
   text.** A test that asserts `len(species) == 904` guards nothing; it fails when a species ships (the
   normal case) and the "fix" is to bump the number. The creature-seed corpus is a **population** that
   grows every time content ships, so its size is a **reading, not a constant** — as are item totals,
   per-cycle accepted/rejected counts, and authored `name`/`description` strings. Assert the envelope,
   closed-enum membership, joins/closure, uniqueness, internal reconciliation, cross-artifact hashes,
   determinism, and structural bounds — all stable across generations. Pin a literal only for a
   **closed vocabulary** (an enum/registry the code owns and a human changes) and say why. Standard:
   [architecture/validation-ssot.md](architecture/validation-ssot.md).

---

## 4. Failure log

Real incidents. Added to whenever a session burns owner time on a misconception. This section is the
argument for the gate — keep it factual and keep it growing.

| Date | The misconception | Root cause | What would have caught it |
|---|---|---|---|
| 2026-08-22 | "The proc roll must happen in the injector because a server round-trip cannot complete inside a frame." | Never read `event-pipeline-v2-ssot.md`. The pipeline is record-then-drain and **G5 explicitly makes delayed effects the designed worst case**. Argued from a constraint the architecture rejects | Reading the pipeline SSOT before reasoning about pipeline timing |
| 2026-08-22 | Quoted *"Server must not own authoritative proc RNG for lawn hits"* as a general architectural law | It sits under *"What Server **in a run** may do"* and concerns the UniqueActor FSM, not a ban on server-side rolling. Read the line, not the section | Evidence rule 3 |
| 2026-08-22 | "Fixing the effect RNG will move goldens, so it needs owner sign-off" | Assumed rather than tested. All 7 chance-gated fixtures use `chance: 1.0`, and the code short-circuits the draw at `chance >= 1.0` — the RNG was never consulted. **Zero goldens moved** | Evidence rule 4 — run the suite before escalating |
| 2026-08-22 | Treated a `VfxCatalog` comment (*"mirroring EffectSeedCatalog"*) as a cross-stream blocker | The file contains zero `fx.*` ids and keys on statusIds. The comment was stale prose | Evidence rule 2 |
| 2026-08-22 | "Plants have no armor" | Asserted from vanilla `arm1`/`arm2` being zombie-only, without reading the shield/resistance layer, which is side-agnostic | Reading `status-ssot.md` / the shield program before claiming a mechanic does not exist |
| 2026-08-23 | A power-scale SSOT was drafted asserting *"player level enters the formula nowhere"* and *"`scaleAt` shape is open — pick exponential, polynomial or soft-cap"* | Written without reading the shipped curves. `decisions.md` P1 already locked level → power; `BattleRuleset.BaseHp` already **was** the shared curve; the overflow analysis solved a problem the shipped linear math does not have | Opening `BattleModels.cs` and `IProgressionPowerProvider.cs` (deleted 2026-08-24 by the power program, `137968103`) before writing a document about level curves. The sweep that followed found **14** power-shaped scales, three of them mutually incompatible |
| 2026-08-23 | `ProgressionPowerCurve = 2^min(L,12)` shipped as a "POC curve" and went unexamined | An exponential feeding a *difference*-based contest. At L12 a matched pair produces `netFactor = 4096` — a base-20 status deals 81,920. Latent only because `SetLevel` has no caller. **The stub value `1.0` is the one value at which broken and correct agree**, so a green test sat on top of it | Probing the evaluator across levels instead of trusting a passing test at the stub value |
| 2026-08-24 | A 12-spec program for derived stats concluded *"no UI surface exists for 157 new channels"* and proposed a fresh `magnitude`/`bounded-ratio` classification | **Both already existed in `docs/design/`.** `spec-derived-stat-sheet.md` designs the surface (six render states, the `no-producer` state these channels land in); `spec-magnitude-and-units.md` §3 is a **nine-class `UnitClass` ledger, each class verified against its consumer in `src/`**, already bound in the web contract. The §1 *Stats* row named only the two `architecture/` docs, so neither was ever opened | The `docs/design/` note under §1's table — added because of this |
| 2026-08-24 | *"`DerivedStatRegistryTests.cs:22` asserts a literal 84; replace it with the formula"* | The test **already computes** `families.Count × (roster.Count + 1)`; the literal on the line above is a deliberate canary asserting what the formula currently equals. A sibling test is named `The_channel_count_is_the_formula_not_the_literal_eighty_four`. The spec would have had someone rewrite tests that were already correct | Reading the whole test body, not the cited line. **Evidence rule 3 applies to code, not just prose** |
| 2026-09-12 | Dual compose (ActorHub vs `BattleStatComposer`) locked as intentional ADR exception | SOLID/DRY fork of the same actor combat numbers treated as “by design” because an ADR / class-system decision said so | §2.15 SOLID — PO/ADR confirmation does not bless a SOLID defect; overturn + fuse (FUSE-battle-hub owed) |
| 2026-09-11 | Correcting the stale `84` roster by replacing it with `904` — then propagating `904`/`227`/`1,183` into specs and tests | The roster is a **population that grows per shipped species**, not a constant. Both `84` and `904` are readings; a pinned literal is stale-by-design and turns every successful seed extension into a red suite | Evidence rule 7 + [architecture/validation-ssot.md](architecture/validation-ssot.md). The same class as the 2026-08-24 literal-84 incident below, from the other direction |
| 2026-09-13 | `unique-lawn-wire` (AS-1.1) shipped with aptitude allocations that silently never reached a Bound lawn specimen — read on the live board as "ActorHub is broken / does nothing" | **Not** an ActorHub defect: the compose chain was provably correct (the same specimen resolved `bonusAtk 1330` the moment its cache entry existed). The cache is keyed by Bound `instanceId`, so its **key set moves when a specimen binds** — but its trigger set was copied from the commander cache (session start / reconnect / `AptitudesUpdated`), which is global and whose key set never moves. Allocating *before* deploying therefore loaded nothing, forever. The spec named only those three triggers; `aptitude-sheet-map.md` said "on reload/**bind**" and the bind half was lost in map→spec. **Third instance of this exact class** (see `CheatState.cs:98-102`, `RpgClient.cs:143-147`) | The new §2 invariant below: enumerate an edge-refreshed cache's FULL trigger set including the state-entry edge, and test each one. Also: an acceptance criterion that names an *ordering* ("allocate + AptitudesUpdated") tests only that ordering — the reverse order was never specified or tested |
| 2026-09-13 | A live probe for `bound-loadout-hub` (T14) "confirmed" a stat-buff feature by binding a debug loadout JSON straight into the Injector and reading the result back from the same injector's own telemetry | Both the fabricated precondition (no real `UniqueActor`/deployment behind it) and the read-back (injector-only, not the RPG server's persisted/derived state) were in the same untrustworthy scope. The sibling T12 probe happened to use a real Server endpoint (`POST /api/aptitudes/unique/allocate`) and real Injector telemetry for two *different* claims, which is why it caught the T14 defect (Hub-bonus grants never reaching Unity) instead of also hiding it | [contributing/live-probe-standard.md](contributing/live-probe-standard.md) — Game Injector Debug vs RPG Server Debug, named explicitly, before treating any debug response as proof |

---

## 5. Pre-proposal checklist

Paste and complete before presenting any design work.

```
[ ] I identified the subsystem(s) this touches.
[ ] I established and recorded this session's boundary (contributing/session-boundary.md):
    one problem, mode/branch chosen by the owner, and the `paths` I own — before any edit.
    `python scripts/session-boundary-check.py --session <id>` is clean for my session. (A creative
    program: its intake stands in for the owner's answers — contributing/creative-mode.md §0, §11.)
[ ] I read every doc in the §1 row(s) for those subsystems, this session.
[ ] I checked decisions.md for a lock covering this.
[ ] Every factual claim cites file:line.
[ ] `python scripts/audit-doc-citations.py --scope <the doc I touched>` reports no HIGH finding
    for it. A citation nobody can open is not evidence, whatever it claims.
[ ] I verified claims against CODE, not comments.
[ ] I read the surrounding section of every rule I quoted.
[ ] I tested (not assumed) any constraint I am reporting - "moves goldens",
    "needs sign-off", "breaks X" - and said what I ran.
[ ] Nothing contradicts a §2 invariant, or I named the contradiction explicitly.
[ ] Corrections are propagated to prose, Structure, Testing, Boundaries, map, and tasks.
[ ] No assertion pins a derived-population count, an item total, generated `name`/`description`
    text, or a per-cycle outcome. Population scale is a reading; guardrails assert the contract and
    closed enums only (validation-ssot.md). A pinned literal has a named closed vocabulary and a
    stated reason.
[ ] If this introduces or touches an event-refreshed cache (§2.16): I listed EVERY trigger that
    invalidates it, including the edge where its KEY SET changes (an entity entering the state the
    cache is keyed by), and each trigger has a test. I did not copy a trigger set from a cache
    with different key-set behaviour.
[ ] No acceptance criterion silently fixes an ordering that can vary in real play. Where both
    orders are reachable, the criterion says order-independent and both are tested.
[ ] If this feature produces or consumes an actor combat/derived magnitude: it either
    contributes via ActorHub (`IActorStatSubsystem` / registered atom reader) with a
    non-empty ContributionSourceIds grammar id, or it consumes Hub output only —
    never a private fold. Does not invent a second actor combat compose or private
    derived fold. BattleStatComposer (fused and deleted 2026-09-13) is a closed
    incident, not a precedent; citing it as permission for a new design = fail this checklist.
[ ] Does not invent or extend a SOLID-violating parallel path (§2.15). If the change
    would deepen known debt (for example a guard-allowlisted ChannelMods producer), a remediation plan is named
    first — PO/ADR blessing is not enough.
[ ] A new rule has a registry row: a guard, or an `unguardableReason`
    (`gk-core/scripts/enforcement-registry.v1.json`; the meta-test fails on a rule covered by nothing).
```

**If you cannot tick a box, say so in the proposal.** An honest gap costs a sentence. A hidden one
costs the owner an hour.
