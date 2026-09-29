# Piece: `preset-gallery`

**Program:** `gui-lego` (first shipped consumer: `aptitude-sheet`, AS-3.4) · **Kind:** entity ·
**ERM rung:** Row list  
**Draft:** none yet — shipped without one; this spec is the first canonical contract (build-preset
BP3.1 idea-ui pass, filling a gap the aptitude console shipped without)  
**Shared types:** [payload-types.md](payload-types.md) · **Composition:** [spec-composition.md](spec-composition.md)  
**Consumers:** `aptitude-preset-console.json` (`vm.gallery`, unchanged shape below) ·
`build-preset-console.json` (`vm.gallery`, uses the two new optional fields)

## Role

The list of saved presets a console lets the player pick from — one row per preset, name + a short
identity, selection and active state. **Reused, not forked**: build-preset's own gallery is a second
consumer of the exact same piece, not a new one, per "reuse before invent" (gui-lego-authoring.md §2
step 2) — the widening below is additive and does not change the aptitude console's existing payload
or behaviour.

## Structure

| | |
|---|---|
| Landmark / root | `ul.preset-gallery` |
| Slots | _none_ (each row is data, not a child slot) |
| CSS `>` parents | `preset-console-layout.slots.gallery` (aptitude console) · `build-preset-console.slots.gallery` (this program) |

**Ban:** illicit wrappers between a `>` parent and its declared child.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"preset-gallery"` | yes | Registry id |
| `instanceId` | `string` | yes | Stable mount / testid |
| `phase` | `Phase` | yes | See payload-types |
| `items` | `PresetGalleryItem[]` | yes | See below |
| `canNew` | `boolean` | yes | Whether a "new preset" affordance renders (unchanged from the shipped aptitude console) |

```ts
interface PresetGalleryItem {
  presetId: string;
  name: string;
  kind: string;           // shipped field (aptitude console: e.g. "player" | preset source); unused by build-preset today
  selected: boolean;
  active: boolean;
  /** New, optional. A build preset's own one-line "what this changed last" (e.g. "Patron ·
   *  6 bound · 3 skills · gear · aptitudes"). Absent for the aptitude console's own rows — no
   *  behaviour change there. */
  summary?: string;
  /** New, optional. Count of pieces this preset references that no longer resolve (a salvaged
   *  item, a released creature) — named, never silently dropped (spec-item-loadout-apply.md's own
   *  "never a silently shorter loadout" rule, generalized to the whole build). Absent or 0 renders
   *  no badge. */
  missingCount?: number;
}
```

## Theme slots

- Pack kind(s): `neutral`
- Reads: `--piece-select-glow` (selected row), `--piece-accent` (active row)
- Vfx keys: none

## Data flow

- **Bind:** `vm.gallery.items`, `vm.gallery.canNew`
- **Bus out:** row select → `preset.open` equivalent per consumer (aptitude console: its own
  selection event; build-preset: `build.select`). The piece never fetches; selection is the host's
  job.

## Focus (GG-19)

Yes — list is arrow-navigable; Enter/Space selects the focused row.

## Motion (GG-31/32)

Row selection highlight transitions; reduced-motion collapses to instant.

## Empty / error

Empty list renders `phase-empty` (host-owned overlay, not this piece's own markup) — "No builds
saved yet" / "No aptitude presets yet" per consumer, authored per surface, never a shared string.

## Sample payloads

```json
{
  "piece": "preset-gallery",
  "instanceId": "preset:gallery",
  "phase": "ready",
  "canNew": true,
  "items": [
    { "presetId": "ap-1", "name": "Fire lean", "kind": "player", "selected": true, "active": true }
  ]
}
```

```json
{
  "piece": "preset-gallery",
  "instanceId": "build:gallery",
  "phase": "ready",
  "canNew": true,
  "items": [
    {
      "presetId": "bp-1",
      "name": "Fire lean",
      "kind": "player",
      "selected": true,
      "active": false,
      "summary": "Patron · 6 bound · 3 skills · gear · aptitudes",
      "missingCount": 1
    }
  ]
}
```
