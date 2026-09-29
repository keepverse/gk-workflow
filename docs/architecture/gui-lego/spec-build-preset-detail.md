# Piece: `build-preset-detail`

**Program:** `gui-lego` (first consumer: `build-preset` BP3.x) · **Kind:** entity ·
**ERM rung:** Row list  
**Draft:** debt (this pass is layout-only; authoring.md steps 6-8 are a later wave)  
**Shared types:** [payload-types.md](payload-types.md) · **Composition:** [spec-composition.md](spec-composition.md)

## Role

One row per piece kind in the selected build preset — the closed five-kind vocabulary
(`BuildPresetPieceKind`: patron, field, skills, aptitudes, gear) in that order, each naming its
target, its reference, and whether it still resolves.

## Structure

| | |
|---|---|
| Landmark / root | `ul.build-preset-detail` |
| Slots | _none_ |
| CSS `>` parents | `split-inspect.slots.detail` (right pane, list side) |

**Ban:** illicit wrappers between a `>` parent and its declared child.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"build-preset-detail"` | yes | Registry id |
| `instanceId` | `string` | yes | Stable mount / testid |
| `phase` | `Phase` | yes | See payload-types |
| `rows` | `BuildPresetDetailRow[]` | yes | Always five, in the closed vocabulary's own order — never re-sorted |

```ts
interface BuildPresetDetailRow {
  kind: "patron" | "field" | "skills" | "aptitudes" | "gear"; // closed, five values
  targetLabel: string;    // player words: "Your patron", "Bound creatures (6)", "Commander", a specimen name
  referenceLabel: string; // what this piece names, e.g. "Emberling", "Fire lean (aptitude preset)"
  present: boolean;
  missingReason?: string; // player sentence, present only when !present -- never the wire code alone
}
```

## Theme slots

- Pack kind(s): `neutral`
- Reads: `--piece-warn` (missing row), `--piece-ok` (present row)
- Vfx keys: none

## Data flow

- **Bind:** `vm.detail.rows` (the selected gallery item's own detail, per `spec-preset-surface.md`'s
  `detail` VM slice)
- **Bus out:** none — this piece is read-only; a missing row does not offer an inline fix (the fix is
  re-capturing or editing the referenced library from its own surface, GG-9)

## Focus (GG-19)

No — static list, read alongside the gallery selection.

## Motion (GG-31/32)

None.

## Empty / error

Never empty once a preset is selected (all five kinds always render, even a piece the preset never
set — that row reads "Not part of this build," never omitted, matching the loadout library's own
"never a silently shorter loadout" rule).

## Sample payloads

```json
{
  "piece": "build-preset-detail",
  "instanceId": "build:detail",
  "phase": "ready",
  "rows": [
    { "kind": "patron", "targetLabel": "Your patron", "referenceLabel": "Emberling", "present": true },
    { "kind": "field", "targetLabel": "Bound creatures", "referenceLabel": "6 bound (excl. wardens)", "present": true },
    { "kind": "skills", "targetLabel": "Commander loadout", "referenceLabel": "3 skills", "present": true },
    {
      "kind": "aptitudes",
      "targetLabel": "Commander aptitudes",
      "referenceLabel": "Fire lean",
      "present": false,
      "missingReason": "This preset no longer exists in your aptitude library."
    },
    { "kind": "gear", "targetLabel": "Commander gear", "referenceLabel": "Ashen Reliquary + 2 more", "present": true }
  ]
}
```
