# Piece: `build-preset-price-line`

**Program:** `gui-lego` (first consumer: `build-preset` BP3.x) · **Kind:** entity ·
**ERM rung:** Row list  
**Draft:** debt (this pass is layout-only; authoring.md steps 6-8 are a later wave)  
**Shared types:** [payload-types.md](payload-types.md) · **Composition:** [spec-composition.md](spec-composition.md)

## Role

Every price and every refusal a preview reports, in one generic list — a preset preview never
invents a number (`spec-preset-surface.md`'s own "the fold invents no number: every price comes from
the preview response"), so this piece renders exactly what the preview VM slice carries, formatted.

## Structure

| | |
|---|---|
| Landmark / root | `ul.build-preset-price-lines` |
| Slots | _none_ |
| CSS `>` parents | `split-inspect.slots.detail` (below `build-preset-detail`, or its own scroll region) |

**Ban:** illicit wrappers between a `>` parent and its declared child.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"build-preset-price-line"` | yes | Registry id |
| `instanceId` | `string` | yes | Stable mount / testid |
| `phase` | `Phase` | yes | See payload-types |
| `lines` | `BuildPresetPriceLine[]` | yes | One per price line **and** one per named refusal — never merged into one string |

```ts
interface BuildPresetPriceLine {
  kind: "price" | "refusal";
  resource?: "souls" | "freeRespec"; // present only when kind === "price"
  amount: MagnitudeDisplay;          // { valueRaw, valueText, unitLabel, formatterId } -- GG-46
  reasonLabel: string;               // player sentence: "Patron switch", "Commander aptitude respec"
  free: boolean;                     // true renders "Free" instead of an amount (first designation, a replay)
  refusalCode?: string;              // present only when kind === "refusal"; developer-support only, never rendered
}
```

## Theme slots

- Pack kind(s): `neutral`
- Reads: `--piece-warn` (refusal rows), `--piece-accent` (price rows)
- Vfx keys: none

## Data flow

- **Bind:** `vm.preview.prices` + `vm.preview.refusals`, concatenated by the fold into one ordered
  list (refusals first — the player sees what stops the apply before what it would cost)
- **Bus out:** none — read-only

## Focus (GG-19)

No.

## Motion (GG-31/32)

None.

## Empty / error

An empty list (no prices, no refusals — a free, clean apply) renders a single authored line ("This
build applies for free" / equivalent), never a blank region (GG-17).

## Sample payloads

```json
{
  "piece": "build-preset-price-line",
  "instanceId": "build:preview:prices",
  "phase": "ready",
  "lines": [
    {
      "kind": "refusal",
      "amount": { "valueRaw": 0, "valueText": "", "formatterId": "none" },
      "reasonLabel": "Gear: two pieces both name your Ashen Reliquary.",
      "free": false,
      "refusalCode": "build-preset.gear.double-claim"
    },
    {
      "kind": "price",
      "resource": "souls",
      "amount": { "valueRaw": 500, "valueText": "500 souls", "formatterId": "integer" },
      "reasonLabel": "Patron switch",
      "free": false
    },
    {
      "kind": "price",
      "resource": "freeRespec",
      "amount": { "valueRaw": 1, "valueText": "1 free respec", "formatterId": "integer" },
      "reasonLabel": "Commander aptitude respec",
      "free": true
    }
  ]
}
```
