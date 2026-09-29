# Piece: `build-preset-payment-choice`

**Program:** `gui-lego` (first consumer: `build-preset` BP3.x) · **Kind:** chrome ·
**ERM rung:** Row  
**Draft:** debt (this pass is layout-only; authoring.md steps 6-8 are a later wave)  
**Shared types:** [payload-types.md](payload-types.md) · **Composition:** [spec-composition.md](spec-composition.md)

## Role

One species aptitude target's unanswered payment choice — pay souls, or spend a free empire respec —
shown with **both options and no default** (ruling R18: the player chooses, the surface never fills a
choice on the player's behalf, `spec-preset-surface.md`'s own bus contract). One mounted instance per
unanswered choice; a preset with no species targets, or whose species targets already resolve without
a choice, mounts none.

## Structure

| | |
|---|---|
| Landmark / root | `fieldset.build-preset-payment-choice` (a real fieldset — GG-21, two radio-shaped controls, one programmatic group) |
| Slots | _none_ |
| CSS `>` parents | `build-preset-preview` container, above the price-line list |

**Ban:** illicit wrappers between a `>` parent and its declared child. Never a `ConfirmDialog` (band
3) for this choice — it is part of the preview, not a decision popped on top of it (GG-63).

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"build-preset-payment-choice"` | yes | Registry id |
| `instanceId` | `string` | yes | Stable mount / testid — one per `targetRef` |
| `phase` | `Phase` | yes | See payload-types |
| `targetLabel` | `string` | yes | Player words: the species/specimen name this choice is for |
| `soulPrice` | `MagnitudeDisplay` | yes | The souls option's cost |
| `freeStock` | `MagnitudeDisplay` | yes | The empire's remaining free-respec count (whole units — never fractional) |
| `selected` | `"souls" \| "freeRespec" \| null` | yes | `null` is the unanswered state; `build.apply` stays unreachable while any instance is `null` |

## Theme slots

- Pack kind(s): `neutral`
- Reads: `--piece-select-glow` (selected option)
- Vfx keys: none

## Data flow

- **Bind:** `vm.preview.choices[]` (`spec-preset-surface.md`'s own `preview.choices` slice)
- **Bus out:** `build.respec.choose` → `{ targetRef, payWith: "souls" | "freeRespec" }`; the host
  re-previews on receipt (the price of one choice can affect another target's own free-stock
  remainder — `spec-piece-appliers.md`'s "the choice stays sequential" rule) — this piece never
  computes what the re-preview will say.

## Focus (GG-19)

Yes — two real radio-shaped controls in one fieldset, arrow-navigable, labelled by `targetLabel`.

## Motion (GG-31/32)

Selection highlight transitions; reduced-motion instant.

## Empty / error

Not applicable — the piece does not mount when there is nothing to choose (§Role).

## Sample payload

```json
{
  "piece": "build-preset-payment-choice",
  "instanceId": "build:choice:species-fire-imp",
  "phase": "ready",
  "targetLabel": "Fire Imp (species)",
  "soulPrice": { "valueRaw": 240, "valueText": "240 souls", "formatterId": "integer" },
  "freeStock": { "valueRaw": 1, "valueText": "1 free respec left", "formatterId": "integer" },
  "selected": null
}
```
