# Spec: `throttle-forecast`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 4, wave 2). **UI-gate (forecast chip):** data, ranking and contract are fixed
here; the chip's layout is not (see *Layout pending `/idea-ui`*). Every `file:line` below was opened this
session. Docs only.

## Objective

Give most End Turns a decision (trade-network ideal §14b: *"most End Turns held no decision"*). Before End
Turn the player sees each **throttle** the next Logistics step will hit under current orders — *"next turn
a sector halts: 40 fire essence has nowhere to go"* — with two or three one-click **answers**. One click
files a real command; the resolved result arrives with the turn report.

Success looks like: a halt that will happen is on the turn cluster as a nag (never a block) and in the
trade panel's forecast row; picking "sell it at Brineport" files an `order-set`; the next state read
shows the throttle reduced or gone.

## Locked anchors

- **The dry run is `logistics-flow`'s, not this module's.** `forecast-facts` (logistics-flow map §11) is
  the one side-effect-free run of the Logistics step: faithful both ways, pure, calling the same flow,
  loss and transit functions. This module ranks answers over its output and presents them; it never
  re-implements a flow rule.
- **Nag, never block.** `HARD_BLOCKING_EVENTS` ships empty and stays empty
  (`gk-web/web/fusion-rpg-web/src/stages/world/turn/blockingClasses.ts:3-8`; `spec-world-turn.md` §2). A trade
  throttle joins the nag class only (`:10-11`), as a reviewed list change.
- **Acknowledge, never paint authority early** (GG-15). A filed answer is "filed", not "solved".
- **Closed answer vocabulary** (ideal §14b, widened by round 4): `reprioritise`, `escort`, `widen`,
  `trade-away`, **`build-feature`**. At most three answers per throttle — a structural presentation limit,
  commented as such.
- **Round 4 Q3 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)):** the first-throttle answer
  (*"no path to a bank point"*) is a one-click **"build a Counting House"**. That needs a fifth answer
  kind, `build-feature` (the id `logistics-flow` `forecast-facts` §2 asked this spec for); this spec adds
  it as the reviewed widening its own hard edge anticipated.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Per-sector forecast sentence with one-click answers that file real orders | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/NextTurnBlock.tsx:24-59` (keep / release-first → `stand-fast` / `cede`, `:12-14`) |
| Nag class with a turn-scoped dismissal | `gk-web/web/fusion-rpg-web/src/stages/world/turn/blockingClasses.ts:1,11`; `gk-web/web/fusion-rpg-web/src/stages/world/turn/TurnCluster.tsx:41-43` (fresh turn clears the nag), `:86` (nag state) |
| The loam forecast, the pure-projection precedent | `gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:9,25` |
| Command filing hook | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:629` (`useSubmitWorldCommands`) |

### Real gap

No Logistics step to forecast; no answer commands (`route-set`, `widen` from `logistics-flow`; the escort
stance from `legion-build`; `order-set` from `exchange`); no nag kind for trade.

## Design

### 1. Throttle kinds (closed, this module's declaration)

| Kind | From `forecast-facts` | Meaning |
|---|---|---|
| `halt` | a sector whose production will stop at a full warehouse | goods will not be produced |
| `waste` | a delivery that will overflow a full destination | goods will be destroyed |
| `strand` | goods a known cut will leave in transit | goods will stop moving |
| `loss-alert` | a route whose forecast loss share crosses `forecast.lossAlertMilli` | goods will leak |

Four kinds, pinned: each maps to one fact family `forecast-facts` publishes; a fifth is a reviewed change.

### 2. Answers and ranking

```csharp
// src/FusionRpg.Core/World/Logistics/ThrottleAnswers.cs (new)
public sealed record Throttle(string Kind, string SectorOrLaneId, string GoodId, long Amount /* goodsUnits */,
                              string? BottleneckReasonId, IReadOnlyList<ThrottleAnswer> Answers);
public sealed record ThrottleAnswer(string AnswerId, IReadOnlyList<WorldCommand> Commands, long UnitsSaved);
// one click files the whole list in one submit (audit 2026-09-20: `trade-away` needs more than one command)

public static class ThrottleAnswers
{
    // Pure. Candidates per throttle from the closed vocabulary; each admissible candidate is scored by
    // re-running LogisticsForecast on a copy with that one command applied; keep UnitsSaved > 0;
    // order by UnitsSaved desc, then AnswerId ordinal; take at most MaxAnswersShown.
    public static IReadOnlyList<Throttle> For(WorldState committed, string factionId, WorldTuning tuning);
    public const int MaxAnswersShown = 3; // structural: a presentation limit on choices, not a balance number
}
```

| Answer | Command filed | Owner of the kind | Candidate when |
|---|---|---|---|
| `reprioritise` | `route-set` (raise this flow's route priority, or send it to another bank point) | `logistics-flow` `auto-banking` | a halt/waste/strand whose flow shares a lane or has another reachable bank point |
| `escort` | the `stance` command with stance `escort` naming the charge | `legion-build` `escort-stance` (consumed by `fleet` `escort-link`) | a `loss-alert` whose dominant cause is hostile presence, with an idle own legion in reach |
| `widen` | `widen` on the bottleneck lane | `logistics-flow` `lane-verbs` | bottleneck reason `lane-capacity` |
| `trade-away` | a **list**: `route-set` sending the halted good from its sector into the faction's consignment at the nearest foreign hub where `LevelAt ≥ market`, plus a paired `order-set` sell of it **and** `order-set` buy of the faction's highest-want good in the same pool at that hub (round 4: the hub's tier and the faction's own Trading Post count) | `logistics-flow` `auto-banking` (`route-set` into a consignment, exchange ask E-A5), `exchange` `order-book`, `trade-access` | a halt or waste of a tradeable good, with a reachable foreign hub and a wanted good it sells |
| `build-feature` (round 4) | `build` of the row carrying the named **sector feature** (or its next tier on the slot that holds it) | the world `build` command (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:34`); the feature and the upgrade rule: `trade-foundation` `sector-features` ([spec](../trade-foundation/spec-sector-features.md)) | `forecast-facts` names `build` [feature] for this fact |

**Why `trade-away` is a list (audit 2026-09-20).** Exchange payment is barter at one hub: a sell with no
buy there delivers nothing (`exchange` `settlement-payment` §2, `order.sell-no-counter-leg`), a sell is
capped by the trader's consignment at that hub at pass start (`order-book` §Design 6), and no order may
sit at the trader's own hub (`order.own-hub`). A lone sell order therefore relieves no halt. The answer
moves the goods out (the `route-set`, which is what the forecast re-run sees relieve the halt) and pairs
the sale so it settles when they arrive. It is offered only when all three commands are admissible.

**Which feature a `build-feature` answer names is not decided here.** `logistics-flow` `forecast-facts`
§2 owns the closed fact → answer table (the first throttle, `no-path` → `build` [`banking`], *"a Counting
House makes it a bank point"* — round 4 Q3; a full warehouse → `build` [`storage`]). This module
**consumes** that table and ranks it — it keeps no second cause → building table (corrected in the
round-4 reconciliation: a first draft here duplicated it). What this module adds is the lookup
`forecast-facts` leaves to the surface: which row carries the feature, which free or upgradable slot in
the sector takes it, and which legion files it.

`build` is admissible only when an own legion stands in the sector with the carried loam the row costs
(`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:47`, `:134`). **When none stands there**, the
answer is still shown, as *"send a legion to build a Counting House"*: one click files `move` for the
nearest idle own legion to that sector, and the next turn's forecast offers the `build` click. Both are
real commands; neither is a debug path. Upgrades use `sector-features`' rule (a `build` of the structure
already on the slot raises its tier).

Admissibility is `WorldCommandAdmission`'s (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs`), run
on the candidate before scoring; an inadmissible candidate is dropped, never shown disabled. An answer
whose command kind has not landed is never a candidate.

### 3. Placement (two homes, one list)

- **Turn cluster:** a new nag kind `trade.will-halt` — `BlockingEventKind` widens by one member
  (`blockingClasses.ts:1`) and joins `NAGGING_EVENTS` (`:11`), a reviewed change under
  `spec-world-turn.md` §2 filed on world-stage `world-turn`. The nag names the count of throttles and
  opens the forecast chip. It clears on a fresh turn like every nag (`TurnCluster.tsx:41-43`).
- **Trade panel forecast row:** the sector's throttles with their answers, the `NextTurnBlock` pattern.

### 4. Filing

One click files the answer's command list in one submit through `useSubmitWorldCommands`. The chip shows *filed*
(GG-15); `trade-wire` refetches on "own command filed", so the forecast re-runs against the new orders.

## Tunables

`data/tuning/trade.v1.json` (new) key `forecast.lossAlertMilli` (per-mille of a route's flow, `long`): the
loss share that raises a `loss-alert`. Starting value by principle: a route leaking a tenth or more of its
flow is worth a decision. `MaxAnswersShown` is structural (commented), not tunable.

## Numeric types

`Amount`, `UnitsSaved`: `long`, `checked` (goods scale with `P(Θ)`). `forecast.lossAlertMilli`: `long`
per-mille, compared as `loss × 1000 ≥ flow × alertMilli` — widen before multiplying.

## Contract exposed

| Member | Consumer |
|---|---|
| `ThrottleAnswers.For`, `Throttle`, `ThrottleAnswer` | `trade-wire` W3 (`ThrottleForecastDto`) |
| Nag kind `trade.will-halt` | world-stage `world-turn` |
| Answer vocabulary (5, round 4 adds `build-feature`) and throttle kinds (4) | `trade-lexicon` rows; `trade-click-budget` |

## Acceptance (contract level)

1. **Faithful (inherited, both directions):** every throttle shown occurs when the turn is committed with
   no new orders **from any faction and the same logged step inputs**, and every halt/waste/strand that
   occurs under those conditions was shown — asserted over seeded fixture worlds, reusing
   `forecast-facts`' property harness. *(Audit 2026-09-20: without the condition this was false — the
   same commit runs every AI policy's orders and a new band snapshot, which the forecast cannot see; in
   live play a throttle may also arise from an AI move, and that is the report's job, not a forecast
   defect.)*
2. **Answers work:** committing the top-ranked answer's command reduces that throttle's `Amount` in the
   same fixture by at least the reported `UnitsSaved`.
3. **Order-independent:** filing two answers for two throttles in either order yields the same committed
   state (both orders tested).
4. **Never blocks:** `HARD_BLOCKING_EVENTS` is still empty after this module; the nag clears on a fresh turn.
5. **At most three answers**, each admissible; no disabled answer is ever rendered (GG-55 by construction).
6. **Pure:** `ThrottleAnswers.For` leaves the committed state hash unchanged.
7. **Filing ≠ resolving:** after a click the chip shows the filed state; no throttle is removed from the
   view until the next state read.

## Layout pending `/idea-ui`

Not decided here: the chip's piece shape and rung, how several throttles group (by sector, by kind),
where the answer buttons sit, the nag's wording in the turn cluster, and motion. The trade panel row
follows `trade-panel`'s recipe. Both go through [idea-ui-phase.md](../../idea-ui-phase.md) before build.

## Test plan and verification boundary

- Core: ranking determinism, admissibility filter, faithful/answers-work property tests, purity —
  `core-fallback` (`FusionRpg.Core.Tests`, World/Logistics).
- Web: nag membership, filed state, no-disabled-answer scan — vitest. **Gap, stated:** no `web/`
  verification boundary exists (`gk-core/scripts/verification-boundaries.v1.json`); report, never run the full
  suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- The nag list edit is world-stage's reviewed change; if refused, the forecast lives in the trade panel
  only (map §8 default).
- The fifth answer kind, `build-feature`, **is** that reviewed vocabulary change (round 4 Q3); a sixth is
  another.
  The teaching throttle's `no-path` reason now has a real answer (`trade-unlock` §Design 3).

## Dependencies

`trade-wire`; `logistics-flow` `forecast-facts`, `auto-banking` (`route-set`), `lane-verbs` (`widen`);
`legion-build` `escort-stance`; `fleet` `escort-link`; `exchange` `order-book`, `trade-access`;
world-stage `world-turn` (ask); round 4: `logistics-flow` `forecast-facts` §2 (the `build` [feature]
answers), `trade-foundation` `sector-features` (features, tiers, upgrade), `empire-seed` (rows).

## Boundaries

- **Always:** rank by forecast units saved; drop inadmissible candidates; nag only.
- **Ask first:** a per-player loss alert setting (v1 is one tunable).
- **Never:** a hard block; a second copy of the flow rules; painting a throttle solved before the commit.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn cluster, logistics dry run (read), command admission, tunables.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: spec-world-turn §2, game-gui-principles GG-15/53/55, logistics-flow-map §11, legion-build-map §5.9.
[x] decisions.md: Game GUI (:110).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: blocking classes, nag clear, NextTurnBlock, LoamForecast, submit hook.
[x] Surrounding sections read (world-turn §2 ES2 argument).
[x] No untested constraint claimed; purity and faithfulness are acceptance tests.
[x] No §2 invariant contradicted.
[x] Corrections propagated: escort command owner is legion-build (map said fleet); map note updated.
[x] No population pinned: 4 kinds and 5 answers are declarations with reasons.
[x] Round 4 reconciliation (2026-09-19): `build-feature` answer (Q3: build a Counting House), fed by
    forecast-facts' answer table (no second table here); move-then-build when no legion stands there;
    trade-away reads LevelAt.
[x] Cache: none owned (trade-wire's triggers include "own command filed").
[x] Ordering: filing order stated order-independent and tested both ways.
[x] No actor magnitude.
[x] No parallel path: one dry run (forecast-facts), one admission.
[ ] Registry row: "trade never hard-blocks End Turn" needs a guard or unguardableReason when built.
```
