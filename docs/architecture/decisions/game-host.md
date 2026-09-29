# Decisions — game-host

**Loader hosts, the injector, the PvZ middle layer, and the overlay control loops.**

Index: [../decisions.md](../decisions.md). Rows are listed with their original line number in `decisions.md`, so a `decisions.md:<line>` citation points at the same decision it did before the decisions.md split.

| Topic | Decision |
|---|---|
| Loader installs | Official GitHub only (pins in `loader-manifest.json`). BepInEx `v6.0.0-pre.2` IL2CPP win-x64; MelonLoader latest x64. Refuse dual-load | <!-- decisions.md:19 -->
| Injector host | **BepInEx 6 plugin and MelonLoader MelonMod** (same Harmony id `com.fusionrpg.injector`, shared `RpgHost` facade). Play installs the matching DropIntoGame payload. Never dual-load. Port plan: [injector/dual-host-roadmap.md](../injector/dual-host-roadmap.md) | <!-- decisions.md:20 -->
| PvzStats | Player-bound Xi SSOT (`pvz_stat_modifiers`) + derived sheet cache. Not RPG progression. Single plugin `pvz.stats`. Cheats stay separate. Sheet Y0=0 is monitor-only | <!-- decisions.md:26 -->
| Pvz middle layer | Three pillars: **PvzStats** (mutable Xi), **PvzActivity** (append facts + rollup cache), **PvzIntent** (`pvz.*` commands). RPG never touches Unity. Capture stays telemetry; progression reads Activity. See [pvz-middle-layer.md](pvz-middle-layer.md) | <!-- decisions.md:27 -->
| PvzActivity | Append-only `pvz_activity_facts`; rollups/revisions are cache. Project Match*/Kill*/Place*/ExtraSpawn from capture/intent. Not RPG quests | <!-- decisions.md:28 -->
| PvzIntent | Injector commands under `pvz.*` (v1: `pvz.spawn.extra`). Source-tagged capture; Activity fact on fire. Luck directors read PvzStats then enqueue Intent | <!-- decisions.md:29 -->
| Game id | Active profile from injector (`pvzrh-3.8.1`, `pvzrh-3.9`, …). Catalog: [game-profiles.json](../../game-profiles.json). Architecture: [game-versioning.md](game-versioning.md). Default / legacy constant `RpgConstants.GameId` = `pvzrh-3.8.1` | <!-- decisions.md:30 -->
| Game × loader matrix | Compile-time profiles + thin `Bridges/{profile}/` (zombie HP width, SetZombie arity). Ship one DLL per cell. Launcher fingerprints pack → installs matching DropIntoGame subtree. No reflection adapters; no dual-load | <!-- decisions.md:31 -->
| TakeDamage log | **On** by default this ingest dump (still togglable) | <!-- decisions.md:32 -->
| Overlay control loops | **Hot** = Injector `EffectBag` + Funnel mailbox + **StatusRuntime** (design) for timed status instances (combat procs; no Server RTT). **Cold** = UniqueActor / Data (equip, loadout push). **Intent** = `pvz.*` extras after Admit. Ban: Server FSM must not sit between `combat.hit` and FA* apply. Spec: [overlay-control-loops.md](overlay-control-loops.md), [effect-funnel.md](effect-funnel.md), [status-ssot.md](status-ssot.md). | <!-- decisions.md:69 -->
| Overlay P0 hardening | Before unique gear LIVE: (1) Withdraw entity grants on die before ptr reuse, (2) Admit/CapPolicy before FA4/our Create, (3) reject `instance:` in Hot Resolve, (4) FT* on-hit SSOT = TakeDamage + melee arm (not base Hit*), (5) rehydrate grants on injector hello. Reject Server on-hit RNG. Workshop: [../research/architecture-stress/05-p0-workshop-verdict.md](../research/architecture-stress/05-p0-workshop-verdict.md). Plan: [p0-hot-path-hardening.md](p0-hot-path-hardening.md). | <!-- decisions.md:70 -->
| Lawn projector (FE) | Phaser **4** `#/lawn` observes run grid/entities (MatchSnapshot or events fold); interact via Intent/debug bus only. Never Hot Admit, proc RNG, or Activity rollups as living SSOT. Spec: [lawn-projector.md](lawn-projector.md); foundation: [fe-game-foundation.md](fe-game-foundation.md). **Shipped (W6–W7)** — see [software-architecture.md](software-architecture.md) Lawn Projector row. A second canvas island (`#/world`) also ships under `src/game/`; lawn and world Games never coexist (GG-11 / D2). Kernel refactor: [phaser-kernel-map.md](phaser-kernel-map.md). | <!-- decisions.md:71 -->
| Overlay implement roadmap | Ordered W0–W12 checklist for P0 Hot, MatchRuntime, UniqueActor, lawn FE, guards — [implementation-roadmap.md](implementation-roadmap.md). Docs checklist; waves pending until code plans ship. | <!-- decisions.md:72 -->
| LimHealth stickiness | Observe via `stat.limhealth` when `SYS-EMIT-PROOF`; active gate `SYS-LIMHEALTH-GATE` default off until proof | <!-- decisions.md:73 -->
| Apply once | Entity key + Applied gate so Start + InitHealth cannot double-buff; reapply clears Applied but keeps Y0 | <!-- decisions.md:74 -->
| Sim vs injector | Live injector heartbeat → sim POST 409. Health `source` is `none` / `sim` / `injector` | <!-- decisions.md:103 -->
