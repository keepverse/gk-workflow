# Spec: `trade-status`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 3, wave 2). **UI-gate (HUD strip):** this spec fixes the fold, the data and the
contract; the strip's layout is not decided here (see *Layout pending `/idea-ui`*). Every `file:line`
below was opened this session. Docs only.

## Objective

The trade situation said in one sentence (trade-network ideal §14b, P7): **banked N · lost M (main
cause) · stuck K (worst bottleneck)**, with the detail one step away. A pure Core fold computes it from
the turn's committed logistics facts; the world HUD shows it; the same fold feeds the turn report's
trade entries, so the two can never disagree.

Success looks like: after End Turn the HUD reads *"banked 140 · lost 12 (raiders) · stuck 30 (Ashfold
road full)"*, one select opens who lost what and where, and a quiet turn reads *"all goods banked"*.

## Locked anchors

- **One fold** for the strip and the turn-report trade entries of the same turn.
- **Attributable** (GG-49): every `lost` and `stuck` unit is traceable to a cause or bottleneck line.
- **A number states its meaning** (GG-46) in the `goodsUnits` family `trade-wire` files; never a local
  formatter.
- **Band 1, never band 3** (GG-5, GG-53). The strip never opens a dialog.
- **Reads, never decides.** Loss causes and bottleneck reasons are `logistics-flow`'s closed sets
  ([logistics-flow-map.md](../logistics-flow-map.md) §4, §6, §10); banking is `sector-yield`'s
  `banking-fact`.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| HUD top strip, the placement precedent (the loam summary strip) | `gk-web/web/fusion-rpg-web/src/stages/world/hud/TopStrip.tsx` (file); `world-stage-ideal.md` §8b decision 5 |
| A pure per-turn projection shape in Core | `gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:9` |
| Report entries scoped by sector and audience | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:30-31` |
| Magnitude renderer that refuses unknown classes | `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:59` |

### Real gap

No logistics facts exist yet (`logistics-flow` unbuilt); no fold; no strip.

## Design

### 1. The fold

```csharp
// src/FusionRpg.Core/World/Logistics/TradeStatusFold.cs (new, in the namespace logistics-flow creates)
public sealed record TradeStatus(
    long Banked, long Lost, long Stuck,                        // value-index units (Σ qty × ValueOf) — see below
    IReadOnlyList<CauseShare> LossCauses,                      // sorted: share desc, then causeId ordinal
    IReadOnlyList<BottleneckShare> Bottlenecks);               // sorted: share desc, then subject id ordinal
public sealed record CauseShare(string CauseId, long Amount, IReadOnlyList<AttributionLine> Lines);
public sealed record BottleneckShare(string ReasonId, string SubjectId /* lane or sector */, long Amount,
                                     IReadOnlyList<AttributionLine> Lines);
public sealed record AttributionLine(string GoodId, string? SectorId, string? LaneId, long Amount);

public static class TradeStatusFold
{
    // Pure. Input: one committed turn's report entries for one faction (already audience-filtered).
    public static TradeStatus For(string factionId, TurnReport report);
}
```

- **Headline units — value, not a sum of unlike goods (audit 2026-09-20).** Adding 10 fire essence to 40
  substrate as "50" is a sum of unlike units. The three headline totals are therefore **value-index
  units**, `Σ qty × goods-valuation.ValueOf(good)` (`exchange` `goods-valuation`, the one valuation),
  computed `checked`; every `AttributionLine` keeps its own good's quantity in `goodsUnits`. The value
  index is relative and held by nobody (never a currency), so a total of it is a size, not a balance.
  The unit class for the headline is filed with `goodsUnits` on `trade-wire` §3 (one reviewed widening
  covering both), never a local formatter.
- `Banked` = Σ banking-fact value for the faction this turn. **Round 6 C3 — this part waits on banking:**
  `banking-fact` waits on `material-ledger`, which waits on the save-identity re-key
  (`solid-enforcement` SE4.12–SE4.38). Stated default until then: `Banked` is **0** and the headline drops the
  part (the sentence already omits a zero part, so it reads *"lost 12 (raiders) · stuck 30"*), and the quiet
  case still reads *"all goods banked"* only when nothing was lost or stuck. The strip therefore ships with
  logistics and gains its first number when banking lands — never a second income read to fill the gap.
- `Lost` = Σ `logistics.loss` quantities; `LossCauses` groups them by cause.
- `Stuck` = goods stranded in transit at turn end (`logistics.strand` qty, attributed to reason `no-path`
  on its lane) plus goods refused at their source this turn (`logistics.short`, attributed to its short
  reason and source sector), grouped by reason and subject. **Ask filed on `logistics-flow`
  `logistics-facts`:** its `logistics.short` detail carries `good` and `reason` but no `qty`
  ([spec-logistics-facts.md](../logistics-flow/spec-logistics-facts.md), kind table); `lane-flow`'s
  conservation line already computes the refused quantity, so the entry gains `qty=`. Until it does,
  `Stuck` counts stranded goods only and short entries attribute reasons without amounts.
- **Main cause** = `LossCauses[0]`; **worst bottleneck** = `Bottlenecks[0]` — the (reason, subject) holding
  the largest **quantity** of stuck goods (map §6.3). `spec-logistics-facts.md`'s consumer note suggests
  "the most frequent `logistics.short` reason"; this fold is trade-surface's and weights by quantity,
  which is what the player lost. Ties break by stable id ordinal, so the sentence is deterministic.
- The fold reads the **committed report**, not live state, so it is the same fold the turn report's trade
  entries and `trade-notify` read.

### 2. Where it is served

`trade-wire` slice W2 puts the viewer's `TradeStatusDto` on `WorldTradeDto.Status`, computed by this fold
over the viewer's audience-filtered report. The turn-report view renders its trade entries from the same
DTO shape for the same turn.

### 3. The sentence

Three states, each a catalog sentence (`trade-lexicon`):

| State | When | Reads |
|---|---|---|
| quiet | `Lost = 0` and `Stuck = 0` | *all goods banked* (with `Banked` when > 0) |
| normal | otherwise | *banked N · lost M (main cause) · stuck K (worst bottleneck)*; a zero part is omitted |
| locked | trade not unlocked (`trade-unlock` capability false) | the strip is absent (GG-44), not "0 · 0 · 0" |

Selecting the strip opens the attribution (per cause and per bottleneck, then per line) one step away, in
place (GG-63: an inspector, never a dialog).

## Tunables

None. The fold has no balance number. Rounding for display is the magnitude renderer's.

## Numeric types

`Banked`, `Lost`, `Stuck`, and every `Amount` are `long`, summed `checked`: goods are value-normalised and
scale with `P(Θ)` (umbrella invariant 7), and `int` whole units leave range at `Θ` = 103,557 (CLAUDE.md
range table). Overflow throws, never wraps.

## Contract exposed

| Member | Consumer |
|---|---|
| `TradeStatusFold.For` / `TradeStatus` | `trade-wire` (W2), the turn-report trade entries, `trade-notify` (quiet-state rule) |
| `TradeStatusDto` (in `TradeDtos.cs`) | the HUD strip, `trade-panel`'s per-sector line |

## Acceptance (contract level)

1. **Reconciliation:** for any fixture turn, `Lost == Σ LossCauses.Amount`, `Stuck == Σ Bottlenecks.Amount`,
   and each share equals the sum of its lines.
2. **One fold:** the strip DTO and the turn-report trade entries for the same turn carry equal totals
   (a test builds both from one fixture).
3. **Determinism:** equal-share ties resolve by id ordinal; the fold is byte-stable across runs.
4. **Units:** headline totals render in the value unit class and attribution lines in `goodsUnits`;
   a render test fails on a bare number; a fixture with two goods of different `ValueOf` shows a headline
   equal to `Σ qty × ValueOf`, never `Σ qty`.
5. **Quiet and locked:** `Lost = Stuck = 0` renders the quiet sentence; a locked faction's strip is absent.
6. **Band:** opening the attribution pushes no band-3 layer.
7. **Fog:** the fold only sees the viewer's audience-filtered report; a fixture with a foreign loss line
   leaves the viewer's totals unchanged.

## Layout pending `/idea-ui`

Not decided here: where the strip sits in the HUD relative to the loam strip, its piece shape (ERM rung),
glyphs for cause and bottleneck, how the attribution inspector lays out, and the strip's reduced-motion
behaviour. These go through [idea-ui-phase.md](../../idea-ui-phase.md) (piece + theme + recipe, owner
accept) before this module's FE half is built. The HUD edit itself is filed as an ask on world-stage
`world-hud`; if unanswered, the line renders only in the trade panel (map §8).

## Test plan and verification boundary

- Core fold tests (reconciliation, ties, fog) — `core-fallback`.
- Server DTO test (the W2 slice) — `server-fallback`.
- Web strip render tests (three states, units, band) — vitest. **Gap, stated:** no `web/` verification
  boundary exists (`gk-core/scripts/verification-boundaries.v1.json`, grep count 0); report it, never run the
  full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- A goods unit class that is not accepted means no goods magnitude ships; the strip waits.
- The fold is not a second attribution engine for anything but trade goods.

## Dependencies

`trade-wire` (W2 slice, `goodsUnits`), `trade-lexicon` (sentences, cause/reason names), `trade-unlock`
(locked state); `logistics-flow` `logistics-facts`, `lane-flow`, `transit-buffer`; `sector-yield`
`banking-fact`; world-stage `world-hud` (ask).

## Boundaries

- **Always:** one fold; stable tie-break; audience-filtered input.
- **Ask first:** a per-good breakdown on the strip itself (the strip is one sentence by contract).
- **Never:** a second loss or bottleneck vocabulary; a band-3 open; a strip before unlock.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn report (read), logistics facts (read), world HUD, magnitude units.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: game-gui-principles GG-5/44/46/49/53/63/64, idea-ui-phase, gui-lego-ideal, logistics-flow-map §4/§6/§10.
[x] decisions.md: Game GUI (:110), GUI Lego (:132).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: TurnReportEntry fields, LoamForecast shape, magnitude exhaustiveness.
[x] Surrounding sections read (GG-63 Why, GG-64 cap rule).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted (long + checked per invariant 13).
[x] Corrections propagated: unit family decision lives in trade-wire; this spec consumes it.
[x] No population pinned.
[x] No cache (the DTO refresh triggers are trade-wire's).
[x] No ordering criterion (totals are order-independent sums).
[x] No actor magnitude.
[x] No parallel path: one fold for strip and report.
[x] Registry row: none new (no new rule beyond existing GG guards).
```
