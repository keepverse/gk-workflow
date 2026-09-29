# Implementation plan: `lawn`

**Map:** [../docs/architecture/lawn-playable-map.md](../docs/architecture/lawn-playable-map.md) +
[../docs/architecture/lawn-tuning-profile-map.md](../docs/architecture/lawn-tuning-profile-map.md)
(one plan over both — they share the lawn surface and a cross-gate at `rider-default-on`) ·
**Specs:** `docs/architecture/lawn-playable/spec-*.md` (6), `docs/architecture/lawn-tuning-profile/spec-*.md` (7) ·
**Tasks:** [lawn-todo.md](lawn-todo.md) ·
**Written by:** `backlog-clean-up` `orphan-plan-authoring` (BCU2.4), per
[spec-orphan-plan-authoring.md](../docs/architecture/backlog-clean-up/spec-orphan-plan-authoring.md).

**Relationship to `backlog-clean-up`.** This plan is `orphan-plan-authoring`'s deliverable for map
modules `lawn-playable` and `lawn-tuning-profile` — two capability maps written 2026-09-16, specced,
and never planned (cause C1 in `program-pipeline-audit-2026-09-20.md`). After this commit, `lawn`
builds through this plan like any other program; `backlog-clean-up` only routes to it.

## Overview

The RPG combat loop is live on the lawn (`LawnBasicAttackFeature.DefaultEnabled = true`, `9f985313`)
and affordable (`effect.onCapture` 3.46% of wall, under the 6% ceiling). What remains is **freshness**
(an actor's live state follows the player's), **two silent failures** (exhaustion, unsummonable
species), and **scale** (the lawn is a game, not just a live overlay — hit/crit sit at a 50/50 coin
flip, stamina never empties, zombie Θ never moves). Thirteen specced modules across two programs close
these; none is built.

## Architecture decisions (from the maps; not re-litigated)

1. **`actor-liveness-refresh` extends `SP6.6`, never a second `Player`-kind channel** — hard edge E2,
   recorded 2026-09-20 by `backlog-clean-up` `lawn-signal-ownership` (BCU0.1) in both maps and this
   module's own spec.
2. **The lawn adopts battle's rates, never a lawn-only accuracy curve** — `lawn-combat-baseline`'s own
   ruling (`battle-engine-ssot.md` §1 rule 2: one implementation per mechanism).
3. **`base-relative-read` is narrowed to `maxHp`/`defense`/`arm1`/`arm2`** — the attack half was removed
   from scope by `2b9fb2c2` (RPG stopped writing `attackDamage` into PvZ), an owner ruling, not a defect.
4. **Contests read Θ directly, magnitudes read `P(Θ)`** (PS-3) — every module that touches Θ follows
   `ssot-power-scale.md`; no private `f(level)`.
5. **One ActorHub compose** — every new subsystem here registers through `ActorHubBootstrap.CreateDefault`'s
   existing opt-in seam or a registered `IActorStatSubsystem`; none forks a second composer.
6. **Repo hard rules apply unchanged**: no hand-edited generated data; tunables publish `v{n+1}`; SOLID;
   tests assert contracts, not populations; the session boundary.

## Already shipped (pointers, not tasks)

| What | Evidence |
|---|---|
| `LawnBasicAttackFeature.DefaultEnabled = true` | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs:56`, commit `9f985313` (2026-09-16) |
| `hub-snapshot-cache` (module 2, fixes P1) | **SUPERSEDED** by `83054adb` — the derived fold became one pass, not one scan per channel. No `ActorSnapshotCache.cs` needed for the number this module chased. |
| `rider-hit-cost` (module 3, fixes P2) | **SUPERSEDED** by `5a3e941c` (`ActorHudCache` dirty-set) + `b48f0e7e` (world-HUD walk stopped rescanning). `effect.onCapture` 4214µs/26.7-37% → 3.46% of wall. |
| The attack write into PvZ | **Removed** by `2b9fb2c2` (2026-09-16) — narrows `base-relative-read` to `maxHp`/`defense`/`arm1`/`arm2`. |
| `lawn-combat-baseline`, `zombie-power-source` specs | Written 2026-09-20 by `backlog-clean-up` BCU2.3, at `docs/architecture/lawn-tuning-profile/spec-{lawn-combat-baseline,zombie-power-source}.md`. |
| `SP6.6` signal-ownership split | Recorded 2026-09-20 by `backlog-clean-up` BCU0.1, in both maps and `spec-actor-liveness-refresh.md`. |

## Dependency graph

```
lawn-perf-budget.v1 (tunable, first — LW1.1)
    │
    ├─► summon-pool-integrity (LW1.2, independent)
    ├─► exhaustion-event (LW1.3, independent)
    └─► actor-liveness-refresh (LW1.4-1.6, after lawn-signal-ownership — already landed)

regen-unit-trace (LW2.1) ─┐
mode-profile (LW2.2) ─────┼─► base-relative-read (LW2.3, hp/armour only) ──┐
                          ├─► lawn-combat-baseline (LW2.4)                 ├─► species-flavour-lawn (LW3.1) ─┐
                          ├─► zombie-power-source (LW2.5)                  │                                  ├─► lawn-scale-live-proof (LW4.1)
                          └─► lawn-resource-scale (LW2.6) ─► basic-attack-cost-scale (LW3.2) ────────────────┘

rider-default-on (LW4.2 — finishes the module: lawn-perf-budget as the real ceiling, gated on
  lawn-scale-live-proof passing, not just the cost half already shipped)
```

`regen-unit-trace` and `mode-profile` are independent and can run in parallel (no deps). `summon-pool-
integrity` and `exhaustion-event` are independent of the cost/scale chain and of each other.

## Suggested order and parallel lanes (suggested, not enforced)

| Lane | Tasks | Notes |
|---|---|---|
| α tunable | LW1.1 | First — the ceiling stops living in a commit message. |
| β freshness | LW1.2, LW1.3, LW1.4-1.6 | Parallel-safe (disjoint files); LW1.4-1.6 depend on E1 (already satisfied). |
| γ scale foundation | LW2.1, LW2.2 | Parallel-safe, no deps. |
| δ scale chain | LW2.3 → LW2.4/LW2.5 (parallel) → LW2.6 → LW3.1/LW3.2 (parallel) → LW4.1 | Sequential per the map's own build order. |
| ε close-out | LW4.2 | After LW4.1 (needs the scale proof to size the real ceiling). |

**Hard edges this plan honours:**
- **E1/E2:** no lawn build task starts before `lawn-signal-ownership` (BCU0.1) landed — it has (see
  Already shipped). `actor-liveness-refresh` extends `SP6.6`, never a second `Player`-kind channel.
- **H7:** `lawn-perf-budget.v1.json` (LW1.1) and `mode-profiles.v1.json` (LW2.2) each land with every
  reader that consumes them in the same commit.
- No golden move: `lawn-combat-baseline`'s own spec states the lawn has no golden
  (`docs/research/combat-ai/S4-lawn.md:65-68`) — if a golden moves, that module is wrong, not something
  to re-bless.

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 1 | `lawn-perf-budget` (new tunable), `summon-pool-integrity`, `exhaustion-event`, `actor-liveness-refresh` | LW1.1–LW1.6 | S–M | yes (disjoint files) |
| 2 | `regen-unit-trace`, `mode-profile`, `base-relative-read`, `lawn-combat-baseline`, `zombie-power-source`, `lawn-resource-scale` | LW2.1–LW2.6 | S–M | LW2.1/2.2 parallel; 2.3-2.6 sequential per the graph |
| 3 | `species-flavour-lawn`, `basic-attack-cost-scale` | LW3.1–LW3.2 | S–M | parallel (both depend only on wave 2) |
| 4 | `lawn-scale-live-proof`, `rider-default-on` close-out | LW4.1–LW4.2 | M, live | sequential |

## Checkpoints

| # | Checkpoint | Evidence |
|---|---|---|
| CL1 | **The lawn stops silently failing.** `summon-pool-integrity` and `exhaustion-event` ship; `actor-liveness-refresh` closes live-probe Tasks 23/24/25. | focused test suites per task; live-probe re-run |
| CL2 | **The lawn is priced, not guessed.** `lawn-perf-budget.v1.json` exists and every perf gate reads it, not a commit message. | `guard-tuning-immutability.py`, the tunable's own readers |
| CL3 | **The lawn is a game.** `lawn-scale-live-proof` measures hit/crit at battle parity and a real exhaustion edge on a clean, in-budget player — closes `lawn-combat-wire` proof 5 / L-N2 and live-probe Task 22 (via `summon-pool-integrity`). | live telemetry read back through the normal path, per `live-probe-standard.md` |
| CL4 | **`rider-default-on` ships on its full contract.** Both halves (cost, already shipped; scale, CL3) are true before the module is called closed. | this plan's own LW4.2 |

## Cross-program edges

- `SP6.6` (lane B, `species-progression-todo.md:340`) — `actor-liveness-refresh` extends it; never a
  second `Player`-kind notice. Not edited here.
- `SE4.31`–`SE4.36` (save-identity SignalR `empireId`) — `actor-liveness-refresh`'s payload reserves an
  `empireId` field for it. Not edited here.
- `species-progression-map.md` §5 names `lawn-resource-scale`'s chain as the owner of Θ freshness (L5)
  and lawn zombie Θ, and `species-flavour-lawn` for layer-1a magnitude reach to general lawn actors —
  convergence delegates to this plan; this plan does not edit convergence's files.
- `empire-progression/spec-ai-empire-species.md` already builds the empire-keyed Θ read
  `zombie-power-source` (LW2.5) consumes.
- `lawn.ai.decide` (the `combat-ai` program's own PerfSection 26) shares this plan's perf budget as a
  **budget share**, not a separate ceiling — `lawn-perf-budget.v1` (LW1.1) is the one number both read.
- `combat-ai`'s `CAI4.1`/`CAI4.2` (`lawn-actor-view`, `lawn-held-actions`) depend on `lawn-signal-
  ownership` (already landed) but not on this plan's own tasks landing first.

## Tuning publishes

| Tunable | Owner task | Readers landing in the same commit |
|---|---|---|
| `lawn-perf-budget.v1.json` (new) | LW1.1 | Every perf gate that currently reads a ceiling from a commit message or a hardcoded constant. |
| `mode-profiles.v1.json` (new) | LW2.2 | `ActorHubBootstrap.CreateDefault`'s mode-row consumer; `lawn-combat-baseline`'s `combatBaseline` flag (LW2.4) is a later key added to the same file, not a second file. |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| A second lawn Θ source appears (private `f(level)`) | Rule 4 above; every task reads Θ through the one `IPowerIndexProvider`. |
| `actor-liveness-refresh` recomposes every actor on every invalidation, reintroducing the P1 cost spike `hub-snapshot-cache`/`rider-hit-cost` were built to fix | The spec's own rule 3 (lazy recompose, bounded) — asserted in test, not assumed. |
| `rider-default-on`'s scale gate never actually runs, and the loop stays on "because it already is" | LW4.2 is a named task with its own acceptance (both halves true), not a checkbox that closes by default. |

## Defaults shipped behind (no gates)

- **K3.1** (`owner-decision-batch`): the combat loop's default-on status pending the scale gate is
  **already answered by D2** — keep on, tune later. This plan's own LW4.2 measures and records the
  gap; it does not block the loop staying on.
- **No new owner gate is introduced by this plan.** Every module here is agent-buildable against its
  own spec; the one live measurement (LW4.1) reads real telemetry per `live-probe-standard.md`, not a
  fabricated debug response.
