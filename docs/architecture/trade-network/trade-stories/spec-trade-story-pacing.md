# Spec: `trade-story-pacing`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 5, wave 3). Every `file:line` below was opened this session. Docs only.

## Objective

How often trade stories fire, entirely in data and **independent of empire size** — the grand-strategy
lesson the trade ideal cites (§6: a size-scaling flag against event spam in large countries). An empire with
twenty hubs does not hear twenty times more trade stories than one with two.

## Locked anchors

- **Owner decision OD-5 (2026-09-19): event frequency gets a per-empire budget in the one selection
  engine.** It is a request to npc-story-events `storylet-selection`, **recorded as decided**: the budget
  is a selection rule, so it lives in the engine every host shares; trade builds no private limiter
  (SOLID; map contradiction 2, now closed). The map's fallback ("fire only through `trade-turn`") is
  retired.
- **Selection is the engine's** (`spec-storylet-selection.md` §2: tiers, fire chance with pity, cooldowns,
  fairness). This module supplies rows and the budget group; it changes no procedure step.
- **The balance surface is data** (tunables-ssot T1, T5). A number a balance pass would change is a row in
  `gk-core/data/tuning/narrative.v1.json` (npc's file, new), published through `gk-core/tools/tuning/publish.py`; a missing
  key rejects the load.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Repeat scopes validated at load, the repeat-scope filter | `gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:93-129`; `gk-core/src/FusionRpg.Core/Delve/Events/EventFilters.cs:76` |
| Pity resolution in the engine (Delve) | `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:252` |

### Real gap

No empire-scoped budget anywhere: npc `world-events-host` asks per sector holding a host slot, so pulses
grow with holdings (trade-stories map §5 Real gap). No trade rows in any tuning file.

## Design

### 1. The engine rule (the OD-5 request, as decided)

`storylet-selection` gains a **budget group** per host kind (`firing.{hostKind}.budgetGroup`) and a
per-empire, per-turn budget per group. Within one world turn, the engine collects every pulse of an
empire's hosts in the group, runs each through the existing procedure up to the fire decision, and grants
at most `budget` Chosen results for that empire and group, in **tier order** (spine, then priority, then
pool), ties by host kind then slot key ordinal. Pulses past the budget are `Quiet("budget")` and count for
pity like any quiet pulse. Spine and priority storylets still bypass the fire roll (`spec-storylet-selection.md`
§2), but not the budget; a priority storylet over budget waits a turn (it is eligible next turn by
construction — its predicate still holds).

### 2. Trade's rows

```jsonc
// gk-core/data/tuning/narrative.v1.json (new; npc's file) — rows this module supplies
"firing": {
  "world.trade-hub":   { "baseMilli": 50, "stepMilli": 5, "budgetGroup": "trade" },
  "world.depot":       { "baseMilli": 50, "stepMilli": 5, "budgetGroup": "trade" },
  "world.trade-lane":  { "baseMilli": 30, "stepMilli": 3, "budgetGroup": "trade" },
  "world.trade-turn":  { "baseMilli": 100, "stepMilli": 10, "budgetGroup": "trade" }
},
"cooldown": { "perKind": { "world.turn": { "<trade storylet kind>": 5 } } },
"budget":   { "perEmpirePerTurn": { "trade": 1 } },
"perHostQuota": { "world.trade-hub": { "count": 1, "windowTurns": 5 } }
```

Starting values by principle and the ideal's prior-art anchors (§6, §13: sparse world hosts 50/5;
5-turn cooldowns; ~750‰ quiet world turns): **none is an owner question**. The per-host quota
is a structural pacing limit (one storylet per host per window) and says so in its loader comment; the
budget is a tunable because a balance pass changes it.

### 3. Why this bounds frequency

Per empire and turn, the count of trade Chosen results is ≤ `budget.perEmpirePerTurn.trade`, whatever the
number of hubs, depots and lanes; the chance that *some* trade storylet fires is governed by the budget,
the firing rows and pity, not by holdings. More holdings mean more candidates (more texture), never more
fires.

## Numeric types

`baseMilli`, `stepMilli`: `long` per-mille (npc's type); budget and quotas: `int` counts; cooldowns: `long`
world turns (unbounded clock).

## Contract exposed

Trade's rows in `narrative.v1.json`; the `trade` budget group. Consumers: `storylet-selection`,
`trade-hosts`, `narrative-readings` (reports pick rates; never asserts them).

## Acceptance (contract level)

1. **Size independence:** on seeded fixture worlds identical except that one empire holds twice the hubs,
   that empire's trade Chosen count per turn never exceeds the budget in either world (structural
   property; no rate asserted to a number).
2. **Cooldown:** a trade storylet never re-fires inside its cooldown on the world-turn clock.
3. **Quiet:** with every trade `baseMilli` and `stepMilli` at 0 and no priority storylet, no trade
   storylet fires.
4. **Tier order under budget:** with budget 1 and both a priority and a pool candidate, the priority one
   is chosen.
5. **Load:** a missing trade row or a `budgetGroup` naming no budget rejects the load (T5).
6. **Pity counts budget quiets:** a pulse quieted by the budget advances pity like a fire miss.

## Test plan and verification boundary

Core selection tests with trade rows (the properties above) — `core-fallback`. The tuning file has no
mapped boundary; npc `narrative-vocabulary` (the file's owner) adds it — this module states the gap.

## Hard edges

- The budget rule is a change to `storylet-selection` (npc); this module waits for it and never ships a
  private limiter.
- Values change only through `gk-core/tools/tuning/publish.py`.

## Dependencies

`trade-hosts`; npc-story-events `storylet-selection` (the budget rule), `narrative-vocabulary` (the tuning
loader and file).

## Boundaries

- **Always:** rows in data; budget in the engine.
- **Ask first:** a budget that scales with anything (it is flat per empire by design).
- **Never:** a trade-local limiter; a `const` frequency.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: storylet selection (npc), tuning (narrative domain).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: spec-storylet-selection §2–§7, spec-narrative-vocabulary §4, npc-story-events-ideal §7, tunables-ssot T1/T5.
[x] decisions.md: Magic numbers row (:63) — numbers in data.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: repeat-scope validation, filter, pity call.
[x] Surrounding sections read (selection tiers; pacing tuning-vs-const contradiction in npc's spec).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted (no magnitude cap: a count of stories per turn is a pacing limit).
[x] Corrections propagated: OD-5 recorded in the map; contradiction 2 closed.
[x] No population pinned: fire counts are readings.
[x] No cache.
[x] Ordering: budget allocation order is the engine's tier order, stated.
[x] No actor magnitude.
[x] No parallel path: one engine rule.
[ ] Registry row: "no trade-local story limiter" needs a guard row when built.
```
