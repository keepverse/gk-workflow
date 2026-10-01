# Architecture decisions

Locked for v1. Change here before changing code. **This table is an index**: one row per decision, in the original order, so a `decisions.md:<line>` citation still resolves to the same decision it always did. The rule text lives in the category file the row links to.

| Topic | Decision |
|---|---|
| World turn phase order | [world](decisions/world.md) |
| Live channel | [transport](decisions/transport.md) |
| HTTP fallback | [transport](decisions/transport.md) |
| Frontend | [presentation](decisions/presentation.md) |
| Web UI kit / bus | [presentation](decisions/presentation.md) |
| First-session progression reveals (2026-09-08) | [launcher](decisions/launcher.md) |
| Player entry | [launcher](decisions/launcher.md) |
| Player runtime | [launcher](decisions/launcher.md) |
| Server URL | [transport](decisions/transport.md) |
| Game folder | [launcher](decisions/launcher.md) |
| Game / web overlay | [launcher](decisions/launcher.md) |
| FusionRpg update | [transport](decisions/transport.md) |
| Loader installs | [game-host](decisions/game-host.md) |
| Injector host | [game-host](decisions/game-host.md) |
| Stats | [stats](decisions/stats.md) |
| Stat compose | [stats](decisions/stats.md) |
| Stat extension | [stats](decisions/stats.md) |
| Stats transport | [stats](decisions/stats.md) |
| Cheats SSOT | [stats](decisions/stats.md) |
| PvzStats | [game-host](decisions/game-host.md) |
| Pvz middle layer | [game-host](decisions/game-host.md) |
| PvzActivity | [game-host](decisions/game-host.md) |
| PvzIntent | [game-host](decisions/game-host.md) |
| Game id | [game-host](decisions/game-host.md) |
| Game × loader matrix | [game-host](decisions/game-host.md) |
| TakeDamage log | [game-host](decisions/game-host.md) |
| Defense | [combat](decisions/combat.md) |
| HP / ATK write | [combat](decisions/combat.md) |
| Single Unity writer | [combat](decisions/combat.md) |
| Foundation Effects | [combat](decisions/combat.md) |
| VFX | [presentation](decisions/presentation.md) |
| **Unity Actor HUD placement (2026-09-17)** | [presentation](decisions/presentation.md) |
| **Async canvas art — one loader seam, and what a draw site may do before a texture arrives (2026-09-26)** | [presentation](decisions/presentation.md) |
| Effect Funnel + Guard | [combat](decisions/combat.md) |
| Combat damage SSOT | [combat](decisions/combat.md) |
| Element Hub SSOT | [combat](decisions/combat.md) |
| Combat resolution SSOT | [combat](decisions/combat.md) |
| Shield layer | [combat](decisions/combat.md) |
| Battle time model | [combat](decisions/combat.md) |
| Action selection (battle adoption) | [combat](decisions/combat.md) |
| Status SSOT | [combat](decisions/combat.md) |
| **Deployment hierarchy SSOT (2026-09-13)** | [world](decisions/world.md) |
| **Scoped inventory hierarchy SSOT (2026-09-13)** | [world](decisions/world.md) |
| **Loam relics and wonders SSOT (2026-09-13)** | [world](decisions/world.md) |
| **Actor-surface catalogs (2026-09-07)** | [stats](decisions/stats.md) |
| Actor Hub SSOT | [stats](decisions/stats.md) |
| **ActorHub sole Hot compose gate (2026-09-07)** | [stats](decisions/stats.md) |
| **Actor layer stack (2026-09-16)** | [stats](decisions/stats.md) |
| **Battle engine is the SSOT for every battle mode (2026-09-16)** | [combat](decisions/combat.md) |
| **The injector never writes a term of the damage equation into PvZ (2026-09-16)** | [combat](decisions/combat.md) |
| **SOLID non-negotiable (2026-09-12)** | [stats](decisions/stats.md) |
| P1 UpdatePower | [power-caps](decisions/power-caps.md) |
| **Power scale (project-wide)** | [power-caps](decisions/power-caps.md) |
| **Combat power number (2026-09-12)** | [power-caps](decisions/power-caps.md) |
| **Power dial (`B` 0 → 400)** | [power-caps](decisions/power-caps.md) |
| **Caps (project-wide)** | [power-caps](decisions/power-caps.md) |
| **Battle engine open questions (2026-09-04)** | [combat](decisions/combat.md) |
| **`RulesetVersion` history (battle)** | [combat](decisions/combat.md) |
| **Magic numbers (project-wide)** | [power-caps](decisions/power-caps.md) |
| P2 progression.bonus.* | [progression](decisions/progression.md) |
| MatchRuntime | [world](decisions/world.md) |
| UniqueActor (dual FSM) | [world](decisions/world.md) |
| Overlay control loops | [game-host](decisions/game-host.md) |
| Overlay P0 hardening | [game-host](decisions/game-host.md) |
| Lawn projector (FE) | [game-host](decisions/game-host.md) |
| Overlay implement roadmap | [game-host](decisions/game-host.md) |
| LimHealth stickiness | [game-host](decisions/game-host.md) |
| Apply once | [game-host](decisions/game-host.md) |
| Match identity | [world](decisions/world.md) |
| Match end | [world](decisions/world.md) |
| Mower used | [world](decisions/world.md) |
| Events vs projections | [world](decisions/world.md) |
| Type catalog | [world](decisions/world.md) |
| Spawn dump | [world](decisions/world.md) |
| Plants planted | [world](decisions/world.md) |
| Players (save identity, R3 + R17, 2026-09-18) | [world](decisions/world.md) |
| Mid-match switch | [world](decisions/world.md) |
| RPG reads | [world](decisions/world.md) |
| Match XP later | [world](decisions/world.md) |
| RpgProgression | [progression](decisions/progression.md) |
| Metrics | [progression](decisions/progression.md) |
| Contracts | [persistence](decisions/persistence.md) |
| TFMs | [persistence](decisions/persistence.md) |
| SQLite | [persistence](decisions/persistence.md) |
| DAL single gate | [persistence](decisions/persistence.md) |
| Key-widening schema migration (2026-09-18) | [persistence](decisions/persistence.md) |
| **`RpgStore` storage plan (2026-09-12)** | [persistence](decisions/persistence.md) |
| Ledger snapshots | [persistence](decisions/persistence.md) |
| Compact / archive timing | [persistence](decisions/persistence.md) |
| Cold archive | [persistence](decisions/persistence.md) |
| Auth | [transport](decisions/transport.md) |
| Docs language | [repo-tooling](decisions/repo-tooling.md) |
| Third-party clients | [transport](decisions/transport.md) |
| Leftover `RpgPlugin/` | [repo-tooling](decisions/repo-tooling.md) |
| Simulator | [repo-tooling](decisions/repo-tooling.md) |
| Test probes | [repo-tooling](decisions/repo-tooling.md) |
| Sim vs injector | [game-host](decisions/game-host.md) |
| CI | [transport](decisions/transport.md) |
| Capture fps | [repo-tooling](decisions/repo-tooling.md) |
| Event ingest | [transport](decisions/transport.md) |
| Live web | [transport](decisions/transport.md) |
| Test snapshot | [repo-tooling](decisions/repo-tooling.md) |
| Standalone-first (2026-08-21) | [repo-tooling](decisions/repo-tooling.md) |
| **Empire resource registry (2026-09-16)** | [progression](decisions/progression.md) |
| Product vision (2026-09-05, amended 2026-09-16, renamed 2026-09-22) | [repo-tooling](decisions/repo-tooling.md) |
| Game GUI (2026-08-22) | [presentation](decisions/presentation.md) |
| Web game profile | [presentation](decisions/presentation.md) |
| Creature program | [progression](decisions/progression.md) |
| Creature progression source and spawn ownership (2026-09-08) | [progression](decisions/progression.md) |
| Unique lawn XP receipts (2026-09-08, strengthened) | [progression](decisions/progression.md) |
| **Commander role (2026-09-18)** | [progression](decisions/progression.md) |
| **Empire level (2026-09-18)** | [progression](decisions/progression.md) |
| Resource model (2026-08-22, **six** 2026-08-26) | [progression](decisions/progression.md) |
| Action model (2026-08-22) | [progression](decisions/progression.md) |
| Golden ordering across streams (2026-08-22) | [progression](decisions/progression.md) |
| Combat mitigation shapes (2026-08-25) | [combat](decisions/combat.md) |
| Class system (2026-08-26) | [progression](decisions/progression.md) |
| Class system real-data collection (2026-08-27) | [progression](decisions/progression.md) |
| Buff/debuff scope (2026-08-29) | [progression](decisions/progression.md) |
| Derived-write lawn executor (2026-08-30) | [stats](decisions/stats.md) |
| Lawn position write (2026-09-02) | [stats](decisions/stats.md) |
| `OwnerKind.UniqueActor` (2026-09-02) | [stats](decisions/stats.md) |
| `SectorView.typeId` narrowing (2026-09-04) | [stats](decisions/stats.md) |
| `LoamUnits` + `Magnitude.op.absolute` (2026-09-04) | [stats](decisions/stats.md) |
| Action eligibility axis (2026-09-03) | [combat](decisions/combat.md) |
| Atom attach points (2026-09-04) | [combat](decisions/combat.md) |
| **GUI Lego — menu composition (2026-09-09)** | [presentation](decisions/presentation.md) |
| **Game GUI — sixth stage `delve` (2026-09-05)** | [presentation](decisions/presentation.md) |
| **World store — delve worlds (2026-09-05)** | [world](decisions/world.md) |
| **Status SSOT + Resource model — nerve (2026-09-05)** | [combat](decisions/combat.md) |
| **Action model — extended action slots (2026-09-05)** | [combat](decisions/combat.md) |
| **Battle timeline dispatch — landed on two profiles (2026-09-05)** | [combat](decisions/combat.md) |
| **`naming.v1.json` registryVersion 4→5 — a `combination` kind, additive (2026-09-07)** | [repo-tooling](decisions/repo-tooling.md) |
| **`naming.v1.json` registryVersion 5→6 — 36 `build`-population set themeIds, additive (2026-09-07)** | [repo-tooling](decisions/repo-tooling.md) |
| **Battle death attribution (2026-09-08)** | [combat](decisions/combat.md) |
| **Set topology classes (2026-09-10)** | [combat](decisions/combat.md) |
| **Eight-socket topology (2026-09-10)** | [combat](decisions/combat.md) |
| Repository topology — Keepverse split (2026-09-19) | [world](decisions/world.md) |
| **World lifecycle — world-continuity (2026-09-19)** | [world](decisions/world.md) |
| **Actor layer 5c — legion (2026-09-19)** | [progression](decisions/progression.md) |
| **Legion equipment scope (2026-09-19)** | [progression](decisions/progression.md) |
| **Structure corpus owner — empire-seed (2026-09-19)** | [progression](decisions/progression.md) |
| **`exchange` structure role (2026-09-19)** | [progression](decisions/progression.md) |
| **Treaties, Diplomacy rail layer, flow lens (2026-09-19)** | [progression](decisions/progression.md) |
| **Structured story text (2026-09-19)** | [content-gen](decisions/content-gen.md) |
| **Narrative names are tokens (2026-09-19)** | [content-gen](decisions/content-gen.md) |
| **Generated antagonist content obeys counter-doctrine (2026-09-19)** | [content-gen](decisions/content-gen.md) |
| **No hard-coded model in seedsmith (2026-09-19)** | [content-gen](decisions/content-gen.md) |
| **Seedsmith authors in two modes: a delegated agent, or an API (2026-10-02)** | [content-gen](decisions/content-gen.md) |
| **The spine is a generated seed kind with a planned frame (2026-09-19)** | [content-gen](decisions/content-gen.md) |

## Why REST and SignalR together

REST survives page refresh and is easy to inspect (`GET /api/stats`). SignalR pushes spawn/die/metrics and `reload-stats` without polling. Raw WebSocket would need reconnect and rooms built by hand.

## Why HTTP fallback on the injector

`Microsoft.AspNetCore.SignalR.Client` may fail to load inside this BepInEx IL2CPP host. The game must still apply last-known stats and ship events over HTTP.

## Why no SQLite in the injector

The plugin must stay a thin hook. Persistence belongs to the server so the web UI works with the game closed.

## Why in-process queues, not Memcached

Localhost, one game, one server. Extra processes add failure modes. Injector `ConcurrentQueue` + server `Channel` + one SQLite writer is the cache.

## Why batch SignalR `Events`, not per-event `Event`

At 120fps a fight is thousands of events/s. One `InvokeAsync("Event")` per row waits on the previous persist. HTTP already posts `{ events: [] }`. The hub must match.

## Why the server stamps `player_id`

The game does not know saves. Later RPG is per-save, not per-PC. Current player lives in SQLite; child rows copy `player_id` from the run opened at `board.start`.

## The server can be told what time it is -- product surface, not a test seam

Owner ruling 2026-09-22 (`tasks/rpg-simulator-decisions.md`, B2 -> product). Hibernating worlds are specified to
catch up lazily on the world-turn clock, and a player can move their machine clock -- so "the server can be told
what time it is" is behaviour a *player* can reach, not a test-only convenience. It therefore needs this row
before any spec that locks its shape.

Consequences, recorded so the next reader does not re-derive them:

- The seam is **product surface**: named, gated and documented as such -- not hidden behind a SIM flag a release
  build does not compile in.
- `ForceExpeditionDue`'s SIM-only `UPDATE` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202`) is retired
  in favour of the seam (owner ruling B3 -> A): a store bypass that rewrites time is exactly what this row
  forbids going forward.
- The migration is the **full** one (owner ruling B1 -> A): `DateTime.UtcNow` / `DateTimeOffset.UtcNow` on the
  **203 real call sites** measured by lane `sim-idea-b` (Data 142 - Server 38 - Injector 17 - Core 3 -
  Launcher 2 - CheatCore 1). Of those, 143 are mechanical ISO emissions, 25 are already injectable
  (`utcNow ?? UtcNow`), 24 are other stamps, and **9 are deadline or wait loops that must not be simulated at
  all** -- faking those tests nothing and one of them is a trap.

## Assistant configuration is tracked; per-machine permission state is not

Owner ruling 2026-09-25 (relayed through the resumed manager; review:
`tasks/reports/resume-30-commandcode-config-review-20260925.md`). Assistant-configuration files
(`.commandcode/**`, like `.claude/`, `.kilo/`, `.cursor/`, `.agents/`) are **tracked**: they are
portable, gate-clean, secret-free, and part of how this repo is worked. The one exception is
**per-machine permission state** — `.commandcode/settings.json` and `settings.local.json` — which
carries a wildcard shell grant, is owned by no verification boundary, and is kept local-only by a
narrow `.gitignore` rule. The durable learned-preference notes under `.commandcode/taste/**` are
tracked knowledge, so every clone agrees with the author's; the policy lives here rather than in chat.
The documented `.commandcode` bypass-vs-default wording divergence is a historical note, not a
permission policy.

## Risks (do not block v1)

See [research/open-questions.md](../research/open-questions.md):

- Whether `Plant.Start` HP is final
- Whether `attackDamage` or `Bullet.Damage` is the real ATK
- Whether SignalR.Client loads in BepInEx (HTTP fallback covers this)
