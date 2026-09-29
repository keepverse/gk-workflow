# Spec: `preset-surface`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave C** · depends on: `apply-orchestrator`,
`capture-current`, and an **`/idea-ui` pass** ([idea-ui-phase.md](../idea-ui-phase.md)) that decides
host, layout and pieces — **done** (BP3.1, 2026-09-20):
[build-preset-console-ideal.md](../build-preset-console-ideal.md).
**Status:** contract only. Layout, placement and visuals are deliberately **not** specified here.

## Objective

The player can see their build presets, capture the current build, see exactly what applying one would
do (every price, every refusal, by name), and apply it. This spec fixes the **contract** the surface is
built against, per the GUI Lego rule: *"Player menus are recipe + pure fold + closed bus — never a god
TSX"* (`docs/architecture/decisions.md` — 'GUI Lego — menu composition (2026-09-09)'; `docs/architecture/gui-lego-ideal.md:49-66`). The
`/idea-ui` pass fills in the recipe tree, host and piece choices — see
[build-preset-console-ideal.md](../build-preset-console-ideal.md).

## Contract

### Model (host fetches; pieces never fetch)

| Source | Route | Owner |
|---|---|---|
| Library with validated pieces | `GET /api/build-presets/{playerId}` | `preset-store` |
| Preview | `POST /api/build-presets/{id}/preview` | `apply-orchestrator` |
| Apply | `POST /api/build-presets/{id}/apply` | `apply-orchestrator` |
| Capture | `POST /api/build-presets/capture` | `capture-current` |
| Create / update / delete | `POST`, `PUT`, `DELETE /api/build-presets…` | `preset-store` |
| Names for references | the existing aptitude-preset, item-loadout, patron, contracts and loadout reads | their programs |

The host refreshes on the SignalR events the gates already send (patron, souls, contracts, aptitudes).
No new event is required.

### ViewModel: `foldBuildPresetConsoleVm(input) → BuildPresetConsoleVm` (new, pure)

`web/fusion-rpg-web/src/features/gui-lego/foldBuildPresetConsoleVm.ts` (new), same shape as the shipped
`foldPresetConsoleVm` (`gk-web/web/fusion-rpg-web/src/features/gui-lego/foldPresetConsoleVm.ts:84`):

| VM slice | Carries | Rule |
|---|---|---|
| `gallery` | one item per preset: name, piece summary, a `missing` count | every stored piece counted; a `Missing` piece is visible, never hidden |
| `detail` | per piece kind: target label, reference label, `present` or `missing` with its reason | the five kinds in the closed vocabulary's order |
| `preview` | per piece: refusals and price lines; the species **payment choices** (soul price and free empire respec stock per target); totals per resource (souls, free respecs); balance and stock; `affordable` | magnitudes as `valueRaw` + `valueText`, formatted in the fold (GG-46), never in a piece. A choice shows **both** options and no default (ruling R18: the player chooses); commander and unique targets show a price only |
| `apply` | `phase` ∈ `ready`, `pending`, `partial`, `done`, `error`, and the per-write outcomes | `partial` lists what applied and what stopped it (orchestrator convergence) |

Every payload carries `phase ∈ ready|loading|empty|error|pending` (`docs/architecture/gui-lego-ideal.md:164-179`).
The fold invents no number: every price comes from the preview response.

### Closed bus: `buildPresetConsoleBus.ts` (new)

Modelled on `presetConsoleBus.ts` (`gk-web/web/fusion-rpg-web/src/features/gui-lego/presetConsoleBus.ts:4-13`):

```ts
export type BuildPresetConsoleEvent =
  | "build.close"
  | "build.select"
  | "build.capture"
  | "build.rename"
  | "build.piece.set"
  | "build.piece.clear"
  | "build.preview"
  | "build.respec.choose"      // { targetRef, payWith: "souls" | "freeRespec" }; re-previews
  | "build.apply"
  | "build.delete";
```

Commands go host → API only. **`build.apply` is only reachable after a `build.preview`** whose
`presetRevision` and totals it sends as `acceptedTotals`, so the player can never apply a price they were
not shown. **`build.apply` is also unreachable while any species payment choice is unanswered**; the
choices the player made are sent as `respecPayment`, exactly as the last preview used them. The surface
never fills a choice on the player's behalf.

### Recipe

`docs/design/gui-lego/recipes/build-preset-console.json` (new). Its tree is the `/idea-ui` output. The
contract it must meet: mounts inside the existing panel host, never a forked `PanelShell`
(`docs/architecture/gui-lego-ideal.md:61-62`); stable `instanceId` per mount; reuses shipped pieces where
they fit (the aptitude preset console's gallery is the obvious candidate,
`docs/design/gui-lego/recipes/aptitude-preset-console.json`) before adding new ones; each new piece ships
its `spec-<piece-id>.md` per the per-piece checklist (`docs/architecture/gui-lego-ideal.md:164-179`).

### The name collision (map X1)

"Build presets" is the aptitude preset console's title today
(`gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx:384`, entry labels
`gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts:205,262`). The product-vision SSOT
gives the name to this surface (`docs/guide/the-loops.md:55`). This module relabels the aptitude console
"Aptitude presets" in the same change that ships "Build presets". The `/idea-ui` pass confirms the copy.

### Player copy

No engine vocabulary on the surface (`docs/architecture/idea-ui-phase.md` §0 rule 7). Refusal codes map to
player sentences in the fold; the code stays available for support. The guide page
`docs/guide/mechanisms/build-presets.md` is rewritten from "Vision" when CP4 passes.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- foldBuildPresetConsoleVm buildPresetConsoleBus
npm run build
npm run extract
npm run test:e2e -- build-preset
```

## Project structure

| Path | Change |
|---|---|
| `web/fusion-rpg-web/src/features/gui-lego/foldBuildPresetConsoleVm.ts` (new) | pure fold |
| `web/fusion-rpg-web/src/features/gui-lego/buildPresetConsoleBus.ts` (new) | closed bus |
| `web/fusion-rpg-web/src/lib/bus/buildPresets.ts` (new) | API client, the `lib/bus/aptitudePresets.ts` pattern |
| `docs/design/gui-lego/recipes/build-preset-console.json` (new) | from `/idea-ui` |
| host component (new, location from `/idea-ui`) | fetch, fold, bind recipe; no layout of its own |
| `gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx`, `foldAptitudesSurfaceVm.ts` | relabel (X1) |
| `web/fusion-rpg-web/e2e/build-preset.spec.ts` (new) | CP4 |

## Testing strategy

1. **Fold is pure and total.** Vitest: every `phase`; a preset with a `Missing` piece shows it; preview
   prices render from `valueRaw` with fold-owned `valueText`.
2. **Bus is closed.** The event list equals the declared union (a closed vocabulary, pinned with its
   reason).
3. **Apply needs a preview.** The host refuses `build.apply` without a preview for the current revision.
4. **Playwright (CP4).** Capture, preview (a price and a refusal visible by name), apply, then the patron,
   contracts and aptitude surfaces show the new state from their own reads.

## Boundaries

- **Always:** recipe + fold + bus; host fetches, pieces render; prices only from the preview.
- **Ask first:** a second overlapping presentation library; any new density rung.
- **Never:** a god TSX; fetch or SignalR inside a piece; compute a price or a refusal in the FE; ship
  layout before the `/idea-ui` pass.

## Tunables, ActorHub, integer widths

- **Tunables:** none.
- **ActorHub:** consumes nothing from Hub; it presents library and preview data.
- **Integer widths:** prices arrive as JSON integers; the fold formats them and never does arithmetic
  beyond display.

## Seedsmith / generator

**None.**

## Success criteria

- [x] `/idea-ui` pass done; recipe committed. — [build-preset-console-ideal.md](../build-preset-console-ideal.md), `docs/design/gui-lego/recipes/build-preset-console.json` (BP3.1, 2026-09-20).
- [ ] Fold, bus and host meet the contract above; vitest green.
- [ ] The aptitude console is relabelled; "Build presets" names this surface.
- [ ] CP4 Playwright green; the guide page is updated.

## Open questions

None for the owner. Layout is the `/idea-ui` pass's job, not a question.

## Self-audit — the debate

- **"Just extend the aptitude preset console."** It is a single-library editor with a distribution
  chart; a build preset is a composite over five libraries with a price preview. Folding both into one
  surface is the god-TSX shape the GUI Lego row bans. Reusing its gallery piece is the right amount of
  sharing.
- **"Show prices computed client-side for snappiness."** Then the FE owns a copy of three price
  functions and drifts from them. The preview route is the only price source.
