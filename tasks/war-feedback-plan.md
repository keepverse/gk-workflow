# War-feedback WIP tracker — creative mechanics (2026-09-15)

Source: design-gap assessment 2026-09-15. Each item names its loop from
`docs/guide/the-loops.md` — no new loop, no new stock, no class, no stamina,
no hard ceiling, contests `Θ` / magnitudes `P(Θ)` per
`docs/architecture/power/ssot-power-scale.md`.

Evidence base (read this session): `docs/DESIGN-GATE.md §1-§2`,
`docs/architecture/software-architecture.md:55-68`,
`docs/guide/the-game.md:11-15`, `docs/guide/the-loops.md:27-141`,
`docs/guide/combat.md:19-28,60-91`, `docs/guide/the-rift.md:24-25,82-114`,
`docs/architecture/economy-principles.md:P1-P15`,
`docs/architecture/empire-economy-ssot.md:§2-§7a`,
`docs/architecture/game-gui-principles.md:GG-1,GG-44,GG-46`.

Code verification owed before any spec: claims verified against docs, not `src/`.

## Status legend (this file only)

- `[ ]` proposed — needs `/idea` + `/spec` before build
- `[~]` spec drafting
- `[x]` built + verified (verify-change.ps1 + live probe per live-probe-standard)

## WIP list

### 1. Climate Echoes — `[ ]` proposed
- **Gap:** empire→lawn feedback one-way; holding ground never changes lawn feel.
- **Mechanic:** element-climate sector projects faint lawn aura (ice-hold = opening Chill pulse, fire-hold = Ember on first suns). Ring only (`combat.md:19-28`), max 2 types.
- **Loops:** farm/hunt/defend + lawn-first-core.
- **Economy:** opportunity cost — garrison pays upkeep (`empire-economy-ssot.md:100-114`); sever kills echo. No faucet.
- **GUI:** GG-1 layer over lawn pre-match; GG-46 renders meaning (“first wave slowed 12%”).
- **Next:** `/idea` → climate→aura table in `gk-core/data/tuning/` (numbers only, hosts inject).

### 2. Oath Cards — `[ ]` proposed
- **Gap:** lawn objectives never mutate; vanilla win only.
- **Mechanic:** 0-2 voluntary pre-match restrictions (no sun-bank 60s, no front-column, commander undeployed) × tunable `oathShareMilli` soul bonus.
- **Loops:** lawn + level/power.
- **Economy:** faucet `victory/kill` → sinks `summon/fusion/slots` (`economy-principles.md:20-29`) — P1 named, throttle is difficulty not cap.
- **Next:** `/idea` → oath catalog + soul-math spec; golden: oath=0 byte-identical.

### 3. Zomboss Ledger — `[ ]` proposed
- **Gap:** Zomboss has no memory; counter-development abstract (`the-loops.md:95`).
- **Mechanic:** records last 3 winning vectors (element, shield-break vs raw, summon-heavy?) from `match.result` facts only, shifts one doctrine/turn, announced in turn report, rebuildable counter.
- **Loops:** world-map adventure + farm/hunt/defend.
- **Constraints:** reads his fog only (`the-rift.md:24-25`); contests stay `Θ`-difference; no private curve.
- **Next:** `/idea` → ledger schema + doctrine catalog (3 doctrines max to start).

### 4. Fallow Lure — `[ ]` proposed
- **Gap:** neglect only mistake, never tool.
- **Mechanic:** release barren-adjacent sector to seed Unmade bloom: Tier-2 farm (essence/materials, never loam per `empire-economy-ssot.md:260-266`), spread-if-unculled + local depletion (`P9/P10`), farming burns carried loam/turn.
- **Loops:** farm/hunt/defend + expeditions (lure discovered via expedition).
- **Next:** `/idea` → bloom rate table + depletion constants as tuning.

### 5. Chronicle Challenges — `[ ]` proposed
- **Gap:** determinism unused as play (`economy-principles.md:P13-P14`).
- **Mechanic:** export settled run/world as `(seed,template,command-log+decision-trace)` file; import as “beat my Zomboss.” File share, localhost preserved, no server.
- **Loops:** quests/events + almanac.
- **GUI:** GG-1 layer over sanctum; GG-8 URL encodes `stage+challenge`.
- **Next:** `/idea` → export/import format + boot-sweep-refuses-incomplete-trace rule.

### 6. Gilding — `[ ]` proposed
- **Gap:** weak veteran soul sinks; P6 needs ≥2 competing horizons.
- **Mechanic:** completed almanac dossier → spend souls + matched essence to gild: tiny global perk, sharply diminishing. Bottleneck `min(souls,essence.x)` earns dimensionality (P4); keeps territory relevant (P12).
- **Loops:** item collection + almanac.
- **GUI:** relative gauge per GG-64, never CAP (no ceiling).
- **Next:** `/idea` → gild catalog (5 entries max to start) + cost curve in tuning.

## Cross-cutting rules for all six

- Balance numbers → `gk-core/data/tuning/<domain>.v{n}.json`, hosts inject, Core reads no file (tunables-ssot §7.2).
- No `int` per-mille past Θ=3,213; `long`, widen-before-multiply, divide-by-1000-last; float allowed, precision≠overflow.
- Player copy from runtime catalogs (`gk-core/data/tuning/*-catalog.v{n}.json`), never `idWords` (GG-62).
- Debug/live proof split per `contributing/live-probe-standard.md`: injector-debug proves reflection only; server-debug runs real path on real row + read-back via normal query.

## Promotion checklist (per item, before build)

```
[ ] /idea enrichment → docs/architecture/<program>-ideal.md
[ ] capability map entry + module id (kebab-case, stable)
[ ] /spec module spec(s) citing DESIGN-GATE §1 row docs + file:line code cites
[ ] plan at tasks/war-feedback-plan.md (this file) updated + tasks/war-feedback-todo.md split when active
[ ] verify-change.ps1 -Paths <changed> -Session <id>; guards green
```
