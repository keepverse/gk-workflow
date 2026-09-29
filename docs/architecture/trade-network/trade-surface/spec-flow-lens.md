# Spec: `flow-lens`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 7, wave 3). **UI-gate:** the lens's id, key, data, encoding contract,
availability rule and acceptance are fixed here; its visual design is not (see *Layout pending
`/idea-ui`*). Every `file:line` below was opened this session. Docs only.

## Objective

Per-lane flow, utilisation, bottleneck reason and loss every turn (trade-network ideal §8.5
*Visibility*), readable at a glance on the world map as a lens. The same change makes lens availability
come from state, so a lens can be locked until its mechanic matters (GG-44) — today every lens is a
compile-time constant.

## Locked anchors

- **Owner decision OD-2 (2026-09-19): a seventh lens, `flow`, as a reviewed widening of the closed lens
  set.** The set's own comment makes this a spec decision (`gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensCatalog.ts:3-8`:
  *"Adding a seventh is a spec decision, not a convenience"*); this spec is that decision's record, and
  the edit is filed on world-stage `world-lenses` ([spec-world-lenses.md](../../world-stage/spec-world-lenses.md) §1).
  Rejected: folding trade flow into lens 4 — lens 4 means legion supply and lifelines and carries a
  server-cost gate (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:50-52`); two meanings on one lens is the
  ES2 failure world-stage cites.
- **Colour is never the only channel** (`lensCatalog.ts:27-35`; spec-world-lenses §7). The encoding has no
  colour field.
- **Unknown is not zero** (`lensCatalog.ts:48-55`).
- **Hotkeys: `1`–`9` are the stage's** (information-architecture §5 verb table), and duplicate
  registration throws (spec-world-lenses §6). Key `7` is free.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Six-lens closed set with keys `1`–`6` | `gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensCatalog.ts:9-16` |
| Pure colour-free encodings per lens | `lensCatalog.ts:27-35` and the encoders below it |
| Auto-activation with player-choice restore | `gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensState.ts:26,63`; `lensAutoActivate.test.ts` (W98 triggers) |
| Lane render channels | `gk-web/web/fusion-rpg-web/src/stages/world/render/laneChannels.ts:53` (`laneChannelsFor`) |

### Wiring gap

| What | Where |
|---|---|
| The picker renders every lens unconditionally | `gk-web/web/fusion-rpg-web/src/stages/world/lenses/LensPicker.tsx:33` (`LENSES.map`) |
| Hotkeys register every lens unconditionally | `gk-web/web/fusion-rpg-web/src/stages/world/lenses/useLensHotkeys.ts:19-20` |

### Real gap

No lane flow data (`trade-wire` W2); no flow encoding; no availability rule.

## Design

### 1. The declaration

```ts
// lensCatalog.ts — after this module (world-lenses edit, filed)
export const LENSES = [
  /* the six, unchanged */,
  { id: "flow", key: "7", label: "Trade flow", cost: "free" }
] as const;
```

The label is a catalog row in `trade-lexicon` once lens labels move to a catalog; until then it follows
the file's existing authored-label pattern.

### 2. Availability from state

```ts
// lensAvailability.ts (new, world-lenses) — pure
export type LensAvailability = { id: LensId; available: boolean; lockedReason?: string };
export function lensAvailability(input: { trade: TradeCapabilitiesView }): LensAvailability[];
```

The six shipped lenses stay always available. `flow` is available iff `trade.Logistics`
(`trade-unlock`). The picker renders a locked lens as a locked entry with its reason (GG-17), never as
active and never hidden; the hotkey hook registers **only available** lenses and re-registers when the
available set changes. That change is a **key-set edge** (DESIGN-GATE §2.16): the registration effect
depends on the availability list, unregisters the old set in cleanup, and a test flips availability
without a stage remount and asserts key `7` goes from inert to live with no duplicate-registration
throw.

### 3. Encoding (pure, colour-free)

```ts
export type FlowLensReading =
  | { known: false; label: "unknown" }
  | { known: true; weight: 0 | 1 | 2 | 3; pattern: "solid" | BottleneckPattern; lossGlyph: boolean; label: string };
export function encodeFlowLens(lane: LaneFlowView, siblings: LaneFlowView[]): FlowLensReading;
```

- **Weight** is relative to the viewer's own visible flows this turn (GG-64: an uncapped magnitude is drawn
  relative to its siblings, never against a false cap). Bucket edges are legibility thresholds on a
  UI-only visual — structural and commented, the precedent at `lensCatalog.ts:92-94`.
- **Pattern** encodes the bottleneck reason (one pattern per member of `logistics-flow`'s closed reason
  set); `solid` when the lane is not a bottleneck.
- **Loss glyph** when `Lost > 0`; the label names the cause from `trade-lexicon`.
- A lane with `Known = false` reads `unknown`.

### 4. Auto-activation

Two new triggers in `autoActivationAction`: selecting a sector with a trade hub, and selecting a legion on
a trade standing order (a caravan). Each selects `flow` and restores the player's own lens on deselect
(the existing W98 contract). Both fire only when `flow` is available.

## Contract exposed

`flow` lens id and key `7`; `lensAvailability`; `encodeFlowLens`; two auto-activation triggers.
Consumers: world-stage `world-lenses` (mount), `trade-panel` (`trade.block.flow.focus`),
`trade-click-budget`.

## Acceptance (contract level)

1. **Seven, declared:** `LENSES.length === 7`, pinned with the comment "closed set; a reviewed change adds
   one" (a declaration, not a population).
2. **Key `7`:** registered by the world stage only while `flow` is available; no rail or global verb uses
   `7`.
3. **Locked:** before unlock, `flow` shows in the picker with its reason, is not selectable, and key `7`
   does nothing.
4. **Key-set edge:** flipping availability in a mounted stage makes key `7` live with no throw and no
   duplicate verb.
5. **Colour-free:** `FlowLensReading` has no colour field (type-level test, the lens-7 row of the existing
   encoding tests).
6. **Unknown ≠ zero:** an unseen lane encodes `unknown`.
7. **Auto-activation restores** the player's chosen lens after a hub or caravan is deselected.
8. **Relative weight:** doubling every visible flow leaves every lane's weight unchanged.

## Layout pending `/idea-ui`

Not decided here: line weights in pixels, the pattern set's visuals, the loss glyph, the legend and
picker chip for lens 7, and reduced-motion flow animation (if any). Through
[idea-ui-phase.md](../../idea-ui-phase.md) and world-stage's lens review before build.

## Test plan and verification boundary

- Web: encoding tests, availability tests, hotkey key-set edge test, auto-activation tests — vitest.
  **Gap, stated:** no `web/` verification boundary (`gk-core/scripts/verification-boundaries.v1.json`, grep count 0);
  report it, never run the full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- The `LENSES` widening and the picker/hotkey change are world-stage's reviewed edits (ask filed).
- **Phaser stays stage-lazy.** The lens draws through a lane-channel function inside the world stage's
  Phaser plane (the `stage-map` chunk, `docs/design/tech-stack.md` §6); the encoding, availability and
  picker code are plain TS/React and import no Phaser, so the lens adds nothing to the entry chunk
  (`npm run check:bundle` stays green).
- `registerGlobalVerb` throws on duplicates; the re-registration path must unregister first — never a
  `try/catch` around it (spec-world-lenses §6).

## Dependencies

`trade-wire` (W2 `Lanes`), `trade-unlock` (`Logistics` flag), `trade-lexicon` (cause and reason names);
world-stage `world-lenses` (ask).

## Boundaries

- **Always:** colour-free encoding; locked lenses say why; relative weights.
- **Ask first:** an eighth lens; a server-cost lens.
- **Never:** overload lens 4; paint an unknown lane as zero flow.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world lenses, hotkeys/keymap, trade read model (consumer).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: spec-world-lenses §1/§3/§6/§7 (headings and §6 text), IA §5, GG-17/44/64.
[x] decisions.md: Game GUI (:110).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: LENSES, picker map, hotkey map, lensState triggers, laneChannels.
[x] Surrounding sections read (closed-set comment, intel threshold comment).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: OD-2 recorded in the map; Q2 closed.
[x] No population pinned: 7 lenses is a declaration.
[x] Event-refreshed state: hotkey registration's key set moves on unlock; that edge is tested.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: one lens system, one hotkey registry.
[ ] Registry row: the lens colour-free rule already has world-stage tests; the availability rule needs a row when built.
```
