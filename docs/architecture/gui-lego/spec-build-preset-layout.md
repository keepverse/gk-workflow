# Piece: `build-preset-layout`

**Program:** `gui-lego` (first consumer: `build-preset` BP3.x) · **Kind:** layout · **ERM rung:** —  
**Draft:** debt (this pass is layout-only; authoring.md steps 6-8 are a later wave)  
**Shared types:** [payload-types.md](payload-types.md) · **Composition:** [spec-composition.md](spec-composition.md)

## Role

Outer frame and slot host for the build-preset console — the root piece
`docs/design/gui-lego/recipes/build-preset-console.json` binds. Deliberately small: this program has
no rail, no tools row, no identity header of its own (it mounts inside the existing rail `PanelShell`,
which already supplies the panel chrome) — same "reuse before invent" reasoning that keeps
`preset-console-layout` (the aptitude console's own root) to exactly its `gallery`/`editor`/`chart`
slots rather than cloning `surface-shell`'s six.

**Actions (Capture / Preview / Apply / Delete) are host-owned footer chrome, not a slot here** —
the exact same treatment `preset-console-layout` gives `allocate-decision-strip`'s Confirm/Cancel
(that recipe's own notes: *"Actions live in PanelShell footer... Activate via host → activate API
only"*). A sticky footer is `PanelShell`'s own chrome; this piece does not re-host it.

## Structure

| | |
|---|---|
| Landmark / root | `.build-preset-console` |
| Slots | `gallery` · `inspect` |
| CSS `>` parents | none (top of this recipe's tree) |

**Ban:** illicit wrappers between a `>` parent and its declared child. This piece never forks
`PanelShell` — the panel chrome (header, close, scrim, sticky footer) stays the host's; this piece
only lays out what goes **inside** the body.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"build-preset-layout"` | yes | Registry id |
| `instanceId` | `string` | yes | Stable mount / testid |
| `phase` | `Phase` | yes | Surface-level readiness |

## Theme slots

- Pack kind(s): `neutral`
- Reads: chrome tokens only
- Vfx keys: none

## Data flow

- **Bind:** `vm.layout`
- **Bus out:** none — pure frame

## Focus (GG-19)

No — delegates to its children; the host names the first-focus element on open (the gallery's first
row or the "capture" action when the gallery is empty).

## Motion (GG-31/32)

None of its own; children animate individually.

## Empty / error

Not applicable — always renders its three slots; each slot's own piece owns its empty/error state.

## Sample payload

```json
{
  "piece": "build-preset-layout",
  "instanceId": "build:layout",
  "phase": "ready"
}
```
