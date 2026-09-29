# Principles, standards and business rules

**Status: digest, not a source of truth.** One page that gathers every rule a contributor — human or
automated — must follow in this repo, each with a link to the document that owns it. When this page
and its linked source disagree, **the source wins**; fix this page in the same change.

Who this is for: anyone starting work here, with or without the assistant setup. `AGENTS.md` and
`CLAUDE.md` at the repo root are tracked assistant config written for automated sessions; every rule
they carry that is not written anywhere else is copied into this page, so the rules read in one place.

Read order before you design anything: this page → [DESIGN-GATE.md](DESIGN-GATE.md) §1 row for your
subsystem → the documents that row names.

This page never states counts that grow with content (species, items, tests, channels). Those are
readings — look them up in their source.

---

## Contents

1. [What the project is](#1-what-the-project-is)
2. [How to work](#2-how-to-work)
3. [Architecture invariants](#3-architecture-invariants)
4. [Stats, combat and effects](#4-stats-combat-and-effects)
5. [Numbers: types, tunables, caps, power](#5-numbers-types-tunables-caps-power)
6. [Data and generated content](#6-data-and-generated-content)
7. [Testing and verification](#7-testing-and-verification)
8. [Guard scripts](#8-guard-scripts)
9. [Frontend and player surfaces](#9-frontend-and-player-surfaces)
10. [Live probes and debug APIs](#10-live-probes-and-debug-apis)
11. [Business rules — the game](#11-business-rules--the-game)
12. [Known drift](#12-known-drift-as-of-2026-09-16)
13. [Keeping this page current](#13-keeping-this-page-current)

---

## 1. What the project is

- **Garden Keeper and his Multiverse is an RPG and empire-building extension for Fusion.** It stays
  inside Fusion's own world — its plants and zombies — and adds a
  persistent RPG and empire layer on top. Its leads are the game's own: the Garden Keeper and
  Hourbloom, against the Rotwright, read from `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`
  (owner rulings R8–R12, 2026-09-19; IC-1b for the host game's name). It never replaces or patches the
  Fusion game.
  Owner ruling 2026-09-16 on tone; product vision: [guide/the-game.md](guide/the-game.md),
  [guide/the-loops.md](guide/the-loops.md).
- **The lawn is the first core loop, not the whole war, and not optional flavor.** Fusion matches feed
  souls, levels, almanac and deploy. [decisions.md](architecture/decisions.md) *Product vision* row.
- **Standalone-first is a capability rule, not the pitch.** After a feature unlocks, it keeps working
  with the Fusion game closed; the injector *enriches* a feature and never permanently *gates* it.
  Quoting this as "Fusion is optional DLC" is a misread. [decisions.md](architecture/decisions.md)
  *Standalone-first* row.
- **Two names, one project.** *Garden Keeper and his Multiverse* is player-facing; `FusionRpg` is the internal prefix
  for assemblies, env vars and the release zip. Do not rename `FusionRpg.*` unless asked.
- **Modules:** Launcher (WPF), Injector (Harmony, BepInEx or MelonLoader host), Server (ASP.NET +
  SignalR), Web (Vite + React + Phaser), plus Core (Unity-free domain), Data (the only SQL), Contracts
  (DTOs), CheatCore. [architecture/software-architecture.md](architecture/software-architecture.md).

## 2. How to work

**Design gate.** Before any spec, plan, proposal, ADR, audit finding or "we should": read the
[DESIGN-GATE.md](DESIGN-GATE.md) §1 row for your subsystem *in this session*, verify against code, then
propose — never propose, get corrected, then read. Complete the §5 checklist; say which boxes you
cannot tick.

**Evidence rules** ([DESIGN-GATE.md](DESIGN-GATE.md) §3):
- Cite `file:line`. A claim without a location is an opinion.
- Code beats docs; docs beat comments. A comment is not evidence.
- Read the section, not the line, before quoting a rule as a general law.
- Test a constraint ("moves goldens", "needs sign-off") before declaring it.
- Verify counts by counting.
- When you correct something, propagate it to every sibling doc, map and task list.

**The RPG-layer question.** An RPG feature is designed against the RPG's own stat/effect/combat stack,
never against what PvZ's Unity fields can hold. Ask in order: does the RPG layer already have a
channel/atom/runtime for it? Is it wired end-to-end, or inert (a default-off toggle, null delegate,
debug-only entry)? An inert path is a **wiring gap**, not an architectural wall. Only then: is it a new
capability? *(Previously local-only in `CLAUDE.md`; incident 2026-08-29.)*

**SOLID is binding.** An ADR, decision or owner confirmation that locks a SOLID violation is still a
defect — overturn and fix. Do not extend a feature along a violating seam until a remediation plan is
named and sequenced. Grandfathered debt is never a template. [DESIGN-GATE.md](DESIGN-GATE.md) §2.15.

**Session boundary.** Several sessions run at once, one problem each. Before the first edit, write
`tasks/sessions/<session>.json` (`paths` fences both edits and commits) and run
`scripts/session-boundary-check.py`. Never `git stash` / `checkout` / `reset` around another
session's dirty files. [contributing/session-boundary.md](contributing/session-boundary.md).

**Git.**
- Automated assistants commit with plain `git` (the git gate was retired 2026-09-19), staging explicit
  paths (never `-A`/`-a`), one logical change per commit, never amending. Push only when asked.
- No vendor names, "AI-generated", `Co-authored-by:` or watermark phrasing in docs, comments or
  history. Subjects are imperative and say why.
- Never commit secrets, game binaries, `dist/`, or machine-local paths (`H:\Games\...`).
  Assistant config (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `.kilo/`, `.cursor/`, `.agents/`,
  `.mcp.json`) **is** tracked, so every path committed in it stays portable (repo-relative or
  `${workspaceFolder}`). `gk-core/data/tuning/`, `gk-data/packs/fusion/data/seed/` and `gk-data/packs/fusion/data/generated/` **are** tracked and belong
  in commits.
- [contributing/agent-git.md](contributing/agent-git.md) · [../CONTRIBUTING.md](../CONTRIBUTING.md).

**Multi-agent runs start with the owner's charter** (2026-09-19). Work delegated to agent runtimes
(Claude Code native subagents, cmdc, pi) starts only after the owner has named, in the current
conversation, the runtimes, the exact models, the budget and the stop rule. Only owner-named models;
no fallback model; a credit or quota error stops the lane and is reported to the owner. The runner
enforces the charter for cmdc and pi; the manager enforces it for native subagents. Procedure:
`.claude/skills/project-manager/SKILL.md`. Full rule: [../CLAUDE.md](../CLAUDE.md). A creative program
collects the charter once at its intake; a session that resumes that program reads the stored charter
instead of re-asking.

**Where specs and plans live** *(previously local-only)*:

| Artifact | Path |
|---|---|
| Idea capture | `docs/architecture/<program>-ideal.md` |
| Capability map | `docs/architecture/<program>-map.md` |
| Module spec | `docs/architecture/<program>/spec-<module-id>.md` |
| Plan / task list | `tasks/<program>-plan.md` / `tasks/<program>-todo.md` |

`tasks/plan.md` and `tasks/todo.md` belong to the perf stream's history — never a default, never a
fallback. A plan drafted in a tool's scratch location is not delivered until it is in `tasks/`.

**Plan gates.** Only gate a plan on a genuinely irreversible action, with a named resolver and a
default if unanswered; everything else ships behind a reversible default as a non-blocking follow-up.

**Creative mode** (2026-09-19). The owner is the customer and a creative project manager is hired:
one intake collects the brief, the charter, the landing branch, the creative game install and the
content-generation terms, and after it the program runs from idea to ship with no human. A written
filter and rubric plus independent reviewer agents stand in for the owner's idea gate; screenshots
judged by a fresh gate stand in for the owner's eyes. A program may ship several sub-programs, landed
by the director on the intake's landing branch. It invents mechanisms inside the product vision, never
the frame — no new loop, element, class, clock or fiction — and never touches the owner's own server,
save or game install. [contributing/creative-mode.md](contributing/creative-mode.md).

**Architecture locks** go in [architecture/decisions.md](architecture/decisions.md) first.

**Docs language** is English. `docs/design/spec-*.md` files are normative for how a number reaches a
player, even when a DESIGN-GATE row does not name them.

**Durable knowledge lives in committed `docs/`.** A local skill or assistant file may *load* it; never
let a fact exist only in a gitignored file.

## 3. Architecture invariants

[DESIGN-GATE.md](DESIGN-GATE.md) §2 and [architecture/software-architecture.md](architecture/software-architecture.md).

- **Two async systems.** The RPG and PvZ share no clock. The RPG works from *past* events, never reads
  or guesses PvZ's current state, and contributes **signed deltas** back.
- **Record-then-drain.** Hooks record a struct and return; decisions run in a later budgeted drain.
  Delay is the designed degradation mode, never frame drops.
- **No Server round-trip on the hit path.** In-process hit-time math in the injector is the design.
- **Module boundaries.** Core: no Unity, no SQL. Server: no SQL. Web talks through its bus only.
- **Foundation effects are sealed** at their contract version; Secondary builds on top.
- **Never collapse the three ids** (`typeId` / `ptr` / `instanceId`). IL2CPP reuses pointers:
  withdraw `entity:{ptr}` grants on death before reuse.
- **An edge-refreshed cache lists its full trigger set** — including the edge where its *key set*
  changes — with one test per trigger. Acceptance criteria that fix an ordering test only that
  ordering; say "order-independent" and test both when play can vary. [DESIGN-GATE.md](DESIGN-GATE.md) §2.16.
- **Perf is a main-thread problem** (per-hit scans, uncached resolves) — not SignalR or the server.
  Do not re-litigate transport without new probe data. [runbook/perf-probe-plan.md](runbook/perf-probe-plan.md).
- **Never download or patch the game binary. Never dual-load BepInEx and MelonLoader.**
- **Unity write surface** (foundation only): `EntityStatWriter` for stats, the CC executor for
  statuses, the effect Funnel → FA10 for HP deltas, `pvz.*` intents for spawns. Any new write path
  needs a `decisions.md` row and a guard extension first.

## 4. Stats, combat and effects

- **Single writer.** All Unity combat field writes go through `EntityStatWriter`.
- **One battle engine, every mode** (2026-09-16, owner ruling). The battle engine is a battle resolver
  built on the atom effect engine and the FSM, and it **solves every battle logic**. A feature that changes
  a battle mechanism is an **extension** of it, built on top — never beside it, never inside a mode. Delve,
  siege, world assault and lawn all share it. A mode is a **driver, never an owner**: it may own its
  **loop** (a turn-ordered delve and a real-time lawn cannot share a scheduler) and may **never** own a
  **mechanism** — damage math, elements, status, shields, targeting, resources, procs, actions, derived
  stats. **The engine is deterministic** — same setup, seed and platform give a byte-identical report — and
  that is where its boundary comes from: **it RESOLVES, it never DECIDES.** Player control and battle AI
  are a separate system that hands the engine data through `IIntentSource`; *where* to move is AI, *whether
  that move is legal* is the engine. Replay works because deciding was never inside. The responsibility
  register is a closed vocabulary; a battle mechanism not on it has no permission to exist. **A decision that locks a SOLID violation is itself a defect** — including this repo's own
  prior ones. Fourteen conformance defects are named, not grandfathered; the headline is that battle's
  `EffectBag` never sets `CombatMath`, so every effect-driven hit in a battle applies its authored amount
  verbatim with no hit roll, crit, element matchup, penetration, parry or block.
  Law and audit: [architecture/battle-engine-ssot.md](architecture/battle-engine-ssot.md).
- **The injector never writes a term of the damage equation** (2026-09-16). `EntityStatWriter` does not
  assign `attackDamage`/`theAttackDamage` (offence), `theShieldHealth` (absorption), or `theArmor` /
  `takeDmgMultiplier` (mitigation) — every one is commented out with the reason inline, and the guard
  `EntityFields12PlusGuardTests` strips comments before asserting, so a retired write cannot pass as a
  live one. The RPG's own battle engine and damage calculator resolve damage: `DamagePacket` →
  `CombatDamageDispatcher` → `ShieldGate` / `OverlayCombatCalculator` → Funnel → FA10, with the lawn
  rider carrying the result onto a real hit. Writing a composed value into PvZ's field as well paid the
  same progression twice and made the engine redundant. It was also a **second decision site for the
  same number** — the dual-compose defect expressed in a Unity field. `takeDmgMultiplier` shows the cost
  is not hypothetical: it is a legal passive-tree target (`ChannelLegality.LowerIsBetterPrimaries`), so
  the first node touching it would have been paid twice with no code change anywhere.
  The lawn transport is a **delta over `hp` / `armor1` / `armor2`**, and every RPG stat PvZ has no field
  for stays in the RPG layer. **All four stay composed** — the sheet, the power price and every proof
  still read them; only the Unity write is gone.
  The nine fields the writer still assigns are the ones whose concept exists **only** in PvZ and that no
  RPG resolver owns: firing and producing cadence, attack-speed adder, plant and zombie movement, and the
  two display levels. Writing those is not a second payment of anything.
- **An actor's numbers come from a closed stack of layers** (2026-09-16): base species, player-modified
  species, specimen progression, empire species progression, equipment, passive tree, titles, aura,
  buff. Each is a **source** of contributions into the one `ActorHub` fold — never a stacking tier, since
  the per-channel `DerivedStatDef.Compose` owns how contributions combine. A feature that changes what an
  actor's numbers are **is a layer**, and owes its scope, lifetime, carrier and provenance before it is
  built. [architecture/actor-layer-compose-ideal.md](architecture/actor-layer-compose-ideal.md),
  `decisions.md` **Actor layer stack**.
- **The Funnel is the only Secondary → Bag path.** Secondary code never touches Unity, Harmony,
  `TakeDamage` or `Bag.Grant`. [architecture/effect-funnel.md](architecture/effect-funnel.md).
- **Deltas, not absolutes.** FA10 is `Add` on live HP; `mode=set` on current HP is rejected; FA10 never
  calls Unity `TakeDamage`. [architecture/combat-damage-ssot.md](architecture/combat-damage-ssot.md).
- **Stats are forward-only.** Persist the base and modifiers, never the final value.
  [architecture/stat-system.md](architecture/stat-system.md).
- **Catalog discipline.** An unknown channel, status id or key is rejected, logged and skipped.
- **One ActorHub compose, one read.** Actor combat derived values and AppliedCombat are composed once
  in `ActorHub`, for every mode (lawn, sheet, battle, delve, siege, sim). Modules contribute through
  registered `IActorStatSubsystem` / atom readers with non-empty SourceIds, or consume Hub output.
  No second `*Composer*`, no private fold, no persisting derived values as a SQLite SSOT.
  Guard: `gk-core/scripts/guard-actor-hub.py`. [architecture/actor-hub-ssot.md](architecture/actor-hub-ssot.md) ·
  [architecture/combat-power-number-ideal.md](architecture/combat-power-number-ideal.md).
- **Closed vocabularies** — atom kinds, attach points and triggers
  ([architecture/effect-atom/definitions.md](architecture/effect-atom/definitions.md), which wins over
  any spec), action enums, status kinds — widen only by a reviewed change, and the change is not done
  until DESIGN-GATE's row moves with it.
- **Battle's plan-item executor** consumes a fixed allowlist of actions (`BattleEffects.cs`); widen the
  allowlist, never add a parallel mechanism.

## 5. Numbers: types, tunables, caps, power

**Overflow is range; precision is separate** *(full table previously local-only)*.
- Overflow = the value exceeds what the type holds; C# integers wrap silently unless `checked`.
  Precision = how finely a type represents values. **Floating point is allowed** for any quantity
  (owner ruling 2026-09-15).
- The power ladder is quadratic, so magnitudes grow far. `int` holding per-mille of a magnitude
  overflows at `Θ` 3,213; `int` whole units at `Θ` 103,557; `long` at `Θ` ≈ 214.7 million.
- Rules: integer magnitudes are `long`; widen before multiplying (`(long)a * b`, never
  `(long)(a * b)`); integer overflow throws (`checked`); narrowing is checked or reported (Unity's `int`
  fields: `EntityStatWriter.ClampToInt32Reporting`); in integer per-mille math divide by 1000 last.
- A `double` feeding a hashed or persisted golden records a platform stamp.
- Audit: `python gk-core/scripts/audit-overflow.py`.

**One power ladder.** Contests read `Θ` (linear, difference-based); magnitudes read `P(Θ)`; a magnitude
is scaled once. No subsystem writes its own `f(level)`. The §10 inventory is closed — a power-shaped
number not in it has no permission to exist. [architecture/power/ssot-power-scale.md](architecture/power/ssot-power-scale.md).

**No hard progression ceilings.** Endless grind is the SSOT. A cap on a magnitude is removed or becomes
a configurable soft cap. Absolute bounds are derived and **throw, never clamp**. Structural limits,
bounded ratios and per-frame caps are exempt and must say so in a comment. An inline `Math.Min`, a
narrowing cast, a flat rate facing a scaling sink, or a payout-halving threshold are all caps.
Register: ssot-power-scale §11.

**The balance surface is config.** Test: would a balance pass change this number? Then it lives in
`gk-core/data/tuning/<domain>.v{n}.json` with units; a missing tunable is a load rejection, never a default.
A structural constant stays `const` with a comment saying why. Policy, Catalog, Rules, Ruleset and Math
files carry no bare literals. Display names and rosters go in sibling `*-catalog.v{n}.json` files, never
the number file. Core never reads a file; hosts load and inject. A tuning change never lands in the
same commit as a refactor. [architecture/tunables-ssot.md](architecture/tunables-ssot.md) ·
`python gk-core/scripts/audit-magic-numbers.py`.

## 6. Data and generated content

- **SQL only inside `FusionRpg.Data`** (`guard-dal.py` scans `src/` only — `tools/` is a blind spot).
  [architecture/data-architecture.md](architecture/data-architecture.md).
- **`RpgStore`** is file-backed in production and in-memory as a first-class test substrate.
- **Contracts.** Web TypeScript types are hand-written; drift is caught by shared JSON fixtures.
  Narrowing or renaming a field bumps `CONTRACT_VERSION`.
- **Generated data is never hand-edited** *(previously local-only)*. Files carrying generator
  provenance (`_meta.model` / `promptVersion` / `batch`) are output: `gk-data/packs/fusion/data/seed/items/**`,
  `gk-data/packs/fusion/data/seed/actions/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/atoms/generated/**`,
  `gk-data/packs/fusion/data/generated/passive-tree/**`. Fix the generator, its tuning or registry, regenerate, commit the
  diff. A failing seed test is a stale test or a generator defect — never a prompt to edit the JSON.
  Hand-author only `**/_registry/**`, `**/_exemplars/**` and hand-authored kinds. `gk-core/data/tuning/**` is
  authored but never hand-edited in place: publish `v{n+1}` through `gk-core/tools/tuning/publish.py`, extending
  the tool when a domain lacks support.
  Guard: `guard-generated-seed.py`.
- **Generated trees are committed and CI checks drift.** After changing a generator or its input, run
  it (`CreatureSpeciesGen`, CreatureBuildPlanGen`, `FamilyExpandGen`, `TreeBinder`); each has `--check`.
- **Seed → concrete → per-player.** Seedsmith emits seeds; the in-game runtime rolls concrete per-player
  objects. LLMs author identity only (names, flavor, family picks); magnitudes are table-owned.
- **Checkouts use LF**; tests compare bytes.

- **Keepverse split (2026-09-19).** The repo moves into the Keepverse multi-repo workspace. All content data (`gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`) goes to the private `gk-data` repo so public repos cannot leak content by accident. The move is the output of the deterministic Python tool `kvsplit`; agents reconcile only its residue (rules, transforms, or normal source commits), never its output. Row: `architecture/decisions.md` *Repository topology — Keepverse split*.

## 7. Testing and verification

- **A guardrail validates the contract, never a population.** Assert envelope, closed-enum membership,
  joins, uniqueness, reconciliation, hashes, determinism, structural bounds. Never assert a derived
  population count, item total, generated name/description text, or per-cycle outcome — print the scale.
  Pin a literal only for a closed vocabulary the code owns, and say why.
  [architecture/validation-ssot.md](architecture/validation-ssot.md).
- **Store tests run in memory.** Disk only when disk is the subject; a failed temp delete is a failure,
  never `catch { }`. [contributing/testing-standard.md](contributing/testing-standard.md).
- **Verify the change you made, at its boundary.**
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>` selects focused tests and
  guards. An unmapped path is a boundary defect to fix, never a reason to run everything.
- **The full suite** runs only when finishing a large feature, for a change crossing modules, or right
  before a live probe *(previously local-only)*. CI, nightly and release gates run unfiltered.
  [architecture/test-verification-boundary-ideal.md](architecture/test-verification-boundary-ideal.md).
- **Coverage says what tests touched; mutation says what they would notice.** `scripts/coverage.ps1`,
  `scripts/mutate.ps1`; every surviving mutant needs an explanation next to the code.
- **Web:** `npm test`, `npm run build` (type errors fail it), `npm run test:e2e`.

## 8. Guard scripts

Seventeen `scripts/guard-*.ps1` scripts enforce the invariants above; each fails individually, and
`verify-change.ps1` selects the ones a change needs. The table of what each enforces lives in
[architecture/software-architecture.md](architecture/software-architecture.md) §10.

## 9. Frontend and player surfaces

- **Stack:** React + Vite + TypeScript; TanStack Query owns server state, zustand owns UI state; one
  SignalR hub; Lingui for i18n. [design/tech-stack.md](design/tech-stack.md).
- **Buy before build.** Prefer a maintained library for icons, charts, gauges, graphs and motion.
  A fat bundle is a code-splitting failure (`React.lazy`, dynamic `import()`), never a reason to ban
  the library. Phaser-class canvases stay stage-lazy. Ask only before adding a *second* library that
  overlaps a locked one.
- **A game is a stage with layers, not pages** (GG-1): menus open over where the player is; home always
  exists; changing stage is explicit travel. [architecture/game-gui-principles.md](architecture/game-gui-principles.md).
- **Menus are recipe + fold + bus** — never a god component; pieces never fetch.
  [architecture/gui-lego-ideal.md](architecture/gui-lego-ideal.md).
- **Player vocabulary.** [guide/glossary.md](guide/glossary.md) is the dictionary — a term not in it
  does not belong on a player surface. Never show `typeId`, `ptr`, `Intent`, `UniqueActor`, `Cold`,
  `mods_json`, `Admit`, `revision`, `ingest queue` or `matchKey` (GG-23). Display names are authored
  catalog rows, never title-cased ids (GG-62). "Creature" is the player word; "demon" is internal.
- **Numbers state their meaning** (GG-46); gauges never paint a false cap (GG-64); complexity unlocks
  and is taught once, in place (GG-44/45). Developer and cheat surfaces live in a separate tree.
- **Porting an approved `docs/design/*.html` draft** follows
  [architecture/html-design-implementation.md](architecture/html-design-implementation.md).

## 10. Live probes and debug APIs

[contributing/live-probe-standard.md](contributing/live-probe-standard.md).

- **Name the scope before treating a response as proof.** *Game Injector Debug* (`debug.*` commands,
  most of `DebugEndpoints.cs`) can fabricate engine state and proves only that Unity reflects it.
  *RPG Server Debug* (`derived-audit-actor`, `derived-audit-coverage`, the real `/api/aptitudes/*` endpoints)
  must run the real domain and persistence path against a record real gameplay could have created.
- **A response body is never proof.** Read the changed state back through the normal query path; check
  the engine half separately. A pass in one scope never proves the other.
- **Debug tooling adapter-wraps the same endpoints** — never a second debug surface that re-implements
  them.
- **From an automated session,** start the server as its own process
  (`Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`) and deploy the injector with
  `deploy-play.py --no-server`; a server started inside a tool call dies with that call.

## 11. Business rules — the game

### Identity, win and loops
- **You are the Garden Keeper.** The Rotwright's broken time machine scattered shards across eras; where a shard
  landed, plant and zombie fused into creatures. Hourbloom carries legions between eras.
  [guide/the-game.md](guide/the-game.md).
- **Win:** take the seat of the world's dominant enemy empire — the world does not end; it becomes
  *developing* and keeps running. **Lose:** enemy empires take your seat — that world becomes *fallen*
  (hostile ground, revisitable) and the save continues. **You keep who you are; the worlds you leave
  keep going** — roster, souls and essence bank across worlds; advance to a new world at any time,
  carrying legions and cargo up to a carry limit (larger after a win); loam never crosses. Old worlds
  hibernate or idle and can fall (amended 2026-09-19,
  [architecture/world-continuity-ideal.md](architecture/world-continuity-ideal.md)).
- **Ten named loops.** Spine: power, summon/fusion, items. Places: lawn, idle expeditions,
  farm/hunt/defend, world-map adventure, world-stage empire, Delve, quests/events. Every feature names
  at least one; only the owner adds a loop. [guide/the-loops.md](guide/the-loops.md).
- **Three clocks, never a fourth:** lawn live time, expedition wall-clock (30 min–20 h), world virtual
  turns (End Turn).
- **Forbidden:** making the lawn the whole game, a currency or material that fails the bottleneck test
  or skips its registry row, a player class, a stamina gate, a prestige wipe, replacing expeditions
  with delves.

### Progression and power
- **Free build — the player has no class.** Aptitude points go anywhere at one price; classes exist only
  as Zomboss AI patterns. [architecture/class-system-ideal.md](architecture/class-system-ideal.md).
- **Dave's level has no cap.** Endless grind; see §5.
- **Win rate is the balance metric** — never fight length or damage.
- **The first session is authored, server-owned and monotonic;** UI acknowledgement never grants a
  reward.

### Creatures
- **General creature** = troop-stack shaped, no persistent instance. **General and unique creatures share
  one progression** (amended 2026-09-17): only equipment, then title, then later layers separate them. General
  stacks wear **legion equipment** — a separate equipment scope: fixed stats, building-produced, counted
  stock, weaker than unique items (owner, 2026-09-19; `architecture/legion-build-ideal.md` §6.7).
  **Unique creature** = a persistent specimen, individually levelled and equipped.
  [architecture/creature-system-map.md](architecture/creature-system-map.md) *Vocabulary*.
- **A Commander fights everywhere except the lawn run; a Patron never fights** (amended 2026-09-17).
  Both designate one unique creature for a side-wide aura. The Commander stands outside the board only
  on a lawn run (aura 100%); it fights as a party member in the Delve (aura 10–15%) and in siege and
  world assault (aura 100%). The same specimen can be a lawn commander in one run and a fighting party
  member in a delve — the roles exclude each other per place, not per creature.
  [architecture/creature-system-map.md](architecture/creature-system-map.md) *Vocabulary* amendment;
  `empire-progression-ideal.md` R-C3–R-C5.
- **The spawn mechanism owns the progression source;** a `typeId` never selects it.
- **Unique XP comes only from proven kills and scaled active-match participation.**
- **Gacha is never the only path;** duplicates keep value; fusion creates builds, not just bigger
  numbers.
- **Species stats are deterministic and shared; only effects roll, per player, at runtime.**

### Economy
- **Every quantity is registered** in [architecture/empire-resource-ssot.md](architecture/empire-resource-ssot.md):
  wallets and materials bank across worlds (souls, essence, shards, substrates, catalysts); world stocks
  (loam, rubble, ironwork, recruits) are map-scoped, never auto-bank, and stay with their world, which
  persists; rubble and ironwork cross worlds only as legion cargo, loam and recruits never. There is no fixed count — a new quantity passes
  P4 (a real bottleneck cost) and P6 (two competing sinks) and lands its row in the same change.
- **Every faucet names its sink in the same change;** territorial income needs territorial upkeep;
  conversions are lossy, rate-capped or gated. [architecture/economy-principles.md](architecture/economy-principles.md).
- **Loam is moved, never traded or converted;** unanchored ground fades. Zomboss runs the same economy.
- **Soul earn scales with enemy value;** the old per-kill and victory caps are removed.

### Combat
- **Six elements** — fire, ice, air, earth, light, dark — plus an omni baseline. Ring
  fire → ice → earth → air → fire; light and dark counter each other. Actors carry 0–2 types; void and
  chaos are traits, not elements. Element math is overlay-only.
  [architecture/element-hub-ssot.md](architecture/element-hub-ssot.md).
- **Six actor resources in one shared set:** `hp`, `stamina`, `hunger`, `spirit`, `qi`, `poise`.
  Faction differences are display labels. All are legal action costs, and a derived-stat family touching
  resources covers all of them. The lawn sun bank is `pvz.*` and match-scoped — not `hunger`.
  [architecture/resource-hub-ssot.md](architecture/resource-hub-ssot.md).
- **Mitigation never reaches zero damage.**

### Items and rarity
- **One ten-rung ladder** shared by items and creatures (Chaff → … → Almanac).
  [architecture/item/ssot-rarity.md](architecture/item/ssot-rarity.md).
- **Rarity never touches a magnitude** — it sets affix count and tier window. Item level is the
  strength axis. Rarity is not an equip gate.

### Actions
- **Three kinds:** basic (free), innate (free, per creature type), earned skills in equipped slots
  (5 base, extendable through the `loadout.slots` channel).
  Guard is a stance, not a reaction. [architecture/action-ideal.md](architecture/action-ideal.md).
- **Actions are seeded, never handcrafted;** one monotonic earn-history counter drives the unlock
  ladder; `rung = min(earnCount, cap)` — rung is progression, never an action property.
- **Discard, never reroll;** only the levelling faucet is capped — paid sources are uncapped.
- **No action scheduling on the lawn;** only an activation edge.

### Fairness and safety
- **Local play:** no account, no cloud, no telemetry; localhost only.
- **Bring a legal copy of Fusion;** the binary is never patched; uninstalling is
  deleting a folder.
- **Injector enrichment is guardrailed** (capped exclusive capture, blessing booster, limited shared
  deploys, cosmetic trophies); web and lawn write one economy through the same ingest.

## 12. Known drift

**Reconciled 2026-09-16** — every contradiction found while assembling this page was ruled on by the
owner and fixed in its source document: the BattleStatComposer fusion recorded as closed; the bundle
check and the repo-root test marker repaired; `spirit` as an action cost; removed soul caps; the power
axis table and status headers; six elements; extendable action slots; tuning published through the
tool; tracked `data/` trees; the product-vision wording; the item-chapter exception; GG-39 "once
unlocked"; element-typed absorb; the empire resource registry; guard table, game profile, Node 22 and
the stale line citation.

Still open, each with an owner:

| Open item | Owner / next step |
|---|---|
| `TreeBinder --check` reports `gk-data/packs/fusion/data/generated/passive-tree/wither.json` stale | The passive-tree program: regenerate through TreeBinder, never hand-edit |
| About fifteen older ideal and spec documents still say "no fourth stock" | Superseded by [DESIGN-GATE.md](DESIGN-GATE.md)'s Economy row note; fix each when its program next touches it |

## 13. Keeping this page current

- A change that adds, overturns or amends a rule updates its source document **and** this page in the
  same commit.
- When you find drift, fix it in the owning document if it is inside your session's `paths`; otherwise
  add a row to §12.
- Keep entries to one or two sentences plus a link. If a rule needs more, it belongs in its source
  document.
- Never add a count that grows with content.
