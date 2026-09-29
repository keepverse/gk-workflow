# Spec: Elemental Action VFX V2 — Earth Pilot

**Status:** Proposed — specification only.  
**Module:** `earth-pilot` in [the capability map](../elemental-action-vfx-map.md).  
**Loop:** Lawn combat feedback, supporting the lawn first-core loop without changing the lawn game's
combat or lifecycle ([the-loops.md](../../guide/the-loops.md):59-66;
[the-game.md](../../guide/the-game.md):10-12).

## Objective

Make an Earth hit unmistakably read as the project's established Earth identity: mossy/ochre stone
with jade geomantic energy, visually consistent with the shipped `stone` actor-HUD icon. The pilot
adds a compact animated stamp under an already-elemental `combat.hit`; it is not an action system,
new element rule, damage effect, or a commitment to the other five elements.

The player must be able to compare the Earth stamp in a real lawn match before the project chooses
whether to fund the six-element catalog.

## Existing facts and constraints

- `VfxDirector` is the one production `IVfxSink`; it queues cues and does all Unity work on its
  main-thread drain ([vfx-ssot.md](../vfx-ssot.md):89-127;
  `gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs`:17-43, 75-84).
- `combat.hit` already carries element payload and only renders its Burst and Flash when an element
  is present (`gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs`: `CoreRecipes`; `VfxDirector.cs`:297-334).
  The existing `debug.fx.play` command already parses element payloads, so it can exercise this
  presentation pilot without fabricating any domain state (`CheatCommandRunner.cs`:1834-1860).
- The VFX contract permits a new primitive only when it is one injector class and a corresponding
  recipe row; it forbids extra VFX sinks, Unity work in `Play`, per-cue scene scans,
  `renderer.material`, and per-hit GameObject creation ([vfx-ssot.md](../vfx-ssot.md):124-143,
  285-323, 365-387).
- Action categories remain the closed five `Attack`, `Defense`, `Support`, `Movement`, and `Status`;
  this pilot creates no action subcategory, tag, or execution branch
  (`gk-core/src/FusionRpg.Core/Actions/ActionEnums.cs`:26-32, 153-156).

## Scope

### In

1. Three reusable Earth presentation phases in the existing `combat.hit` recipe: target-ground **`ImpactStamp`**, source-attached **`Charge`**, and source-to-target **`Travel`**. Each is a bounded pooled SpriteRenderer primitive; no phase changes combat timing or writes gameplay.
   It renders one cached, alpha-backed Earth sprite at the resolved target/cell anchor, fades and
   scales over its configured lifetime, and releases its pooled renderer when finished.
2. Earth-only selection inside `combat.hit` when its *dominant resolved element* is `earth` and
   `SYS-ELEMENT-FX` is enabled. Existing floater, burst, flash, caps, rate limit, and hybrid color
   behaviour remain unchanged.
3. A cached embedded PNG resource package from
   `gk-fusion/src/FusionRpg.Injector/Assets/elemental-action-vfx/earth/`. The selected art must be a
   non-destructive new version; current Earth V1 assets remain intact.
4. A versioned VFX tuning addition for stamp lifetime, relative unit-frame span, alpha/fade curve,
   global pool cap, and sorting offset. These are presentation balance values and must not be C#
   constants ([vfx-ssot.md](../vfx-ssot.md):226-251).
5. A documented `POST /api/debug/fx/play` Earth probe, core validation tests, injector
   packaging/compile proof, and a Game Injector Debug live review.

### Out

- No new cue ids, action categories, action tags, action timing, targeting, damage, HP/stat/status
  writes, or ActorHub contribution.
- No Action VFX Presentation Catalog. The pilot proves a single primitive and Earth art first; a
  catalog is a later, separately specified decision.
- No other element, shader, AssetBundle, material instance, per-hit asset decode, or scene-wide scan. Earth charge and travel are the approved exception to the original one-primitive pilot.
- No server, web, settings, game binary, or persistent schema change. The existing master and
  element VFX toggles continue to govern presentation.

## Debug API trigger

The pilot uses the already-shipped **Game Injector Debug** relay
`POST /api/debug/fx/play`; it maps to `debug.fx.play` in `DebugEndpoints.cs` and the injector already
parses `cueId`, an actor `ptr` or `col`/`row`, and an `elements` payload
(`gk-core/src/FusionRpg.Server/DebugEndpoints.cs`:1166-1172;
`gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs`:1834-1860, 1902-1920). No parallel endpoint or
server-side VFX renderer is added.

```http
POST /api/debug/fx/play
Content-Type: application/json

{
  "cueId": "combat.hit",
  "ptr": "<live plant-or-zombie pointer>",
  "amount": 120,
  "elements": [{ "element": "earth", "weight": 1.0 }]
}
```

The endpoint acknowledges that the command was relayed; it is not the proof. The proof records a
subsequent `debug.fx.shown` event containing `cueId`, pointer, and `impactStamp` in its primitive
list, plus an actual lawn screenshot. A disabled `SYS-ELEMENT-FX` run must instead omit the stamp.

This API is deliberately **Game Injector Debug**: it may render a visual on a live Unity actor, but
it cannot prove server action execution, damage calculation, persistence, or element-domain logic.
The live-review report must label it that way, as required by
[the live-probe standard](../../contributing/live-probe-standard.md):25-37.

## Design

### Primitive and lifecycle

`ImpactStamp` is a transient, pooled visual primitive. It receives a resolved world anchor and the
existing `VfxUnitFrame` span, takes an available pooled SpriteRenderer/GameObject, assigns the
already-cached Earth texture and cached shared material, then advances only age/transform/color until
expiry. A full pool steals/releases the oldest live stamp, matching the established drop-oldest VFX
policy ([vfx-ssot.md](../vfx-ssot.md):226-264).

The primitive does not read gameplay state. It does not modify a unit renderer; it is a separate
overlay object. Clearing the board or disabling visual effects returns all leased stamps immediately,
alongside existing VFX cleanup ([vfx-ssot.md](../vfx-ssot.md):265-323).

The Earth art is authored color, not a neutral runtime tint mask: jade, moss, ochre, and subdued
umber are part of its material identity. The system selects the art only for a dominant Earth payload.
Hybrid hits intentionally do **not** use this Earth-only stamp in the pilot; they retain the existing
mixed-color particle/floater treatment.

### Anchor and selection

For target-attached hits the stamp uses the existing `AnchorResolver` and `UnitFrameResolver`; it
does not reuse Actor HUD screen anchoring. For a cell-attached debug cue it uses the existing cell
world anchor. This preserves the VFX-owned world-anchor contract
([vfx-ssot.md](../vfx-ssot.md):324-347).

The `combat.hit` recipe receives Earth-only `Charge`, `Travel`, and `ImpactStamp` specs marked `RequireElement`. Charge and travel require an optional semantic `SourcePtr`; ordinary gameplay cues without one retain the target-only impact path, while the debug probe supplies both source and target pointers. The director admits
it through existing master toggle, global cap, per-cue rate-limit, mute, and anchor resolution before
it can allocate a pool lease. If the element toggle is off, the primitive is not selected; a neutral
or hybrid hit does not substitute Earth art.

The V1 charge and travel PNGs are grayscale alpha source art. Each pooled lease receives the existing
concrete Earth `VfxColorPlan` RGB at dispatch, so the phases use the same canonical Earth palette as
the cue rather than rendering as neutral white; no new palette or runtime material is introduced.

### Asset package

The Earth source master and 512/256/128 runtime variants reside beneath
`Assets/elemental-action-vfx/earth/v2/`, with a manifest describing dimensions, alpha requirement,
palette, and intended `resolve` moment. The host project embeds only the runtime variants and uses
one named manifest resource. Asset loading occurs once lazily on the main thread, validates the
manifest/dimensions, and caches the texture for the process lifetime. A failed load skips the stamp
and emits the existing `debug.fx.skipped` event with an enumerated `asset-missing` reason; it never
breaks damage feedback or the game loop.

## Tunables

`vfx.v4.json` owns the initial impact stamp, `vfx.v5.json` introduces the source phases, and
`vfx.v6.json` improves lawn readability. `vfx.v7.json` is the current phase-sequence revision,
published through `gk-core/tools/tuning/publish.py`; do not edit a published tuning file in place. It retains
both sections and their explicit units:

| Key | Unit | Meaning |
|---|---:|---|
| `impactStamp.poolCap` | instances | Maximum live Earth stamps; structural cap, not a power cap |
| `impactStamp.lifeSeconds` | seconds, unscaled | Stamp lifetime |
| `impactStamp.spanScale` | unit-frame spans | Render size relative to the target visual frame |
| `impactStamp.startAlpha` / `endAlpha` | 0–1 ratio | Fade endpoints |
| `impactStamp.startScale` / `endScale` | multiplier | Pop/settle scale curve |
| `impactStamp.sortOffset` | sorting-order delta | Position above the target sprite |
| `impactStamp.delaySeconds` | seconds, unscaled | Delay until travel reaches its target |
| `earthPhase.poolCap` | instances | Maximum shared charge/travel renderers; structural cap |
| `earthPhase.chargeLifeSeconds` / `travelLifeSeconds` | seconds, unscaled | Charge and projectile lifetimes |
| `earthPhase.chargeSpanScale` | unit-frame spans | Charge size relative to source frame |
| `earthPhase.travelLengthScale` | source-target distance multiplier | Projectile sprite length along its path |
| `earthPhase.travelThicknessScale` | unit-frame spans | Projectile thickness relative to source frame |
| `earthPhase.startAlpha` / `endAlpha` | 0–1 ratio | Shared phase fade endpoints |
| `earthPhase.sortOffset` | sorting-order delta | Layering relative to the target frame |
| `earthPhase.travelDelaySeconds` | seconds, unscaled | Delay until the source charge finishes |

The initial values are deliberately not locked in this spec: the first live Earth comparison sets
them, then the published tuning file makes the choice reviewable and reversible.

## Commands

```powershell
# focused validation selected after implementation
$changed = @(
  'gk-core/src/FusionRpg.Core/Vfx/VfxRecipes.cs',
  'gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs',
  'gk-fusion/src/FusionRpg.Injector/Fx/ImpactStampPool.cs',
  'gk-fusion/src/FusionRpg.Injector/Fx/EarthPhasePool.cs',
  'gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs',
  'gk-fusion/src/FusionRpg.Injector/Assets/elemental-action-vfx/earth/v2/manifest.json',
  'gk-core/data/tuning/vfx.v7.json'
)
.\scripts\verify-change.ps1 -Paths $changed -Session actor-hud-element-icons-20260917

# compile only, against the legal local game assemblies
$gameDir = 'H:\Games\PVZ-Fusion-4.0_MelonLoader'
dotnet build src\FusionRpg.Injector.MelonLoader.40\FusionRpg.Injector.MelonLoader.40.csproj -c Release -p:MlGameDir=$gameDir -p:GameProfile=pvzrh-4.0 -p:OutputPath="$gameDir\Mods\"

# live presentation check, with a real lawn open
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5088/api/debug/fx/play' `
  -ContentType 'application/json' `
  -Body '{"cueId":"combat.hit","ptr":"<live-target-pointer>","sourcePtr":"<live-source-pointer>","amount":120,"elements":[{"element":"earth","weight":1.0}]}'
```

## Project structure

```text
gk-core/src/FusionRpg.Core/Vfx/                         recipe kind/spec validation and tuning contract
gk-fusion/src/FusionRpg.Injector/Fx/ImpactStampPool.cs     pooled target-ground renderer lifecycle
gk-fusion/src/FusionRpg.Injector/Fx/EarthPhasePool.cs      pooled source charge and source-to-target travel lifecycle
gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs         existing admitted recipe dispatch only
gk-fusion/src/FusionRpg.Injector/Fx/FxResources.cs         one cached Earth texture/material resource
gk-fusion/src/FusionRpg.Injector/Assets/elemental-action-vfx/earth/v2/
                                                 master, variants, manifest
gk-core/data/tuning/vfx.v7.json                          current Earth-phase presentation and sequence values
tests/FusionRpg.Core.Tests/Vfx/                  pure recipe/selection/tuning tests
gk-core/tests/FusionRpg.Guard.Tests/                     packaging and no-forbidden-API guard
```

## Code style

```csharp
// Director selects an admitted recipe; the pool owns Unity lifetime.
case VfxPrimitiveKind.ImpactStamp:
    if (ImpactStampPool.Spawn(world, frame, spec, cue, out var reason))
        kinds.Add("impactStamp");
    else
        failReason = reason;
    break;
```

Core expresses selection, recipe validation, and tuning contracts without Unity references.
Injector code is a guarded adapter around cached resources and a bounded pool. It must never use
`renderer.material`, call `FindObjectsOfType`, or construct/decode a texture per hit.

## Testing strategy

- **Core:** recipe validation accepts `ImpactStamp`, `Charge`, and `Travel`; rejects presentation
  literals; Earth-only selection rejects no-element and hybrid payloads; all new tuning keys load with no fallback.
- **Guard/package:** all injector hosts embed the exact Earth runtime assets; VFX source has no
  forbidden scene scan or unit-renderer material access; asset manifest dimensions and alpha pass.
- **Compile:** MelonLoader 3.9 injector build against the configured game directory.
- **Game Injector Debug:** `debug.fx.play` with a target pointer and a concrete Earth element payload
  through `POST /api/debug/fx/play` proves the actual Unity render path. The follow-up
  `debug.fx.shown` event and a lawn screenshot are mandatory; an HTTP success response alone is not
  evidence. This is explicitly presentation proof only, not a claim that a server action or domain
  damage result occurred.
- **Live acceptance:** screenshots/video of Earth hit on both plant and zombie, with stamp alignment,
  readability, cleanup, and disabled-element fallback checked by the owner. Only a pass authorizes
  the multi-element catalog decision.

## Boundaries

- **Always:** retain the cue → recipe → primitive path; use unscaled time; pool every transient
  renderer; preserve V1 assets; fail visual loading as a skip; keep all numeric presentation values
  in versioned VFX tuning.
- **Ask first:** a new primitive after `ImpactStamp`; an AssetBundle/shader/dependency; changing
  global VFX caps/rate limits; adding any element beyond Earth; creating the deferred catalog.
- **Never:** gameplay writes/reads, another sink/host tick, an action vocabulary, a parallel anchor
  resolver, material instances, per-hit GameObjects/textures, or modification of vanilla art.

## Success criteria

1. An Earth `combat.hit` can show its charge, source-to-target shard travel, and jade/moss/ochre impact on either a plant or zombie through the existing debug cue surface; a normal, non-Earth or hybrid hit never shows Earth art.
2. Turning off existing element VFX removes the stamp while preserving ordinary damage feedback.
3. No VFX cap/rate limit, action semantics, combat result, entity transform, HUD anchor, or gameplay
   write path changes.
4. The stamp remains aligned to a moving sprite, expires/cleans up on board end and toggle-off, and
   does not leave live objects/materials after repeated plays.
5. Focused tests, asset validation, and host compilation pass; the owner accepts the live Earth look
   before any other element or catalog work begins.

## Open questions

None block the pilot. The owner review of the live Earth look decides whether the next specification
is a multi-element presentation catalog or a visual iteration of Earth only.

## Design-gate checklist

- [x] Subsystem identified: injector VFX presentation, touching lawn combat feedback only.
- [ ] Boundary checker is globally clean. It reports pre-existing stale broad claims from
  `solid-remediation-20260917`; this session is an isolated worktree and owns the two new spec paths.
- [x] Read current-session architecture and decision records, VFX SSOT/V2, product-loop guides, and
  action category code before this proposal.
- [x] Verified the claimed seam in code: one VFX director, `combat.hit` element gating, and
  element-aware `debug.fx.play` are present.
- [x] No gameplay magnitude, actor compose, cache, population assertion, or ordering-dependent
  acceptance criterion is introduced.
- [x] The proposal does not deepen a parallel architecture; it extends the existing primitive seam.
