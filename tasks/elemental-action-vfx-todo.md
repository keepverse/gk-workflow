# Tasks: Elemental Action VFX V2 — Earth Pilot

**Plan:** [elemental-action-vfx-plan.md](elemental-action-vfx-plan.md)  
**Spec:** [Earth pilot](../docs/architecture/elemental-action-vfx/spec-earth-pilot.md)

## Task 1: Finalize the Earth V2 asset package

**Status:** Complete — build-gate PASS (runtime 512/256/128 variants are RGBA with alpha 0..255;
manifest validation reported `element=earth`, `moment=resolve`, `palette=jade,moss,ochre,umber`).

**Description:** Save the approved jade/moss/ochre Earth stamp non-destructively with source master,
runtime variants, and manifest metadata.

**Acceptance criteria:**

- [x] V1 art remains byte-for-byte present.
- [x] V2 has source, 512, 256, and 128 PNGs with verified alpha and dimensions.
- [x] Manifest identifies the asset as an Earth resolve/impact stamp and records its palette.

**Verification:** Image dimension/alpha script and JSON validation.

**Dependencies:** None.  
**Files likely touched:** `gk-fusion/src/FusionRpg.Injector/Assets/elemental-action-vfx/earth/v2/**`  
**Estimated scope:** S.

## Task 2: Add the Core primitive contract and VFX V4 tuning

**Status:** Complete — focused VFX coverage passed; the previously blocking generated-loot
line-ending contract now has a generator-owned LF normalization regression test and passes.

**Description:** Add the `ImpactStamp` recipe model/validation and load the pilot's versioned stamp
tuning without changing any current recipe selection.

**Acceptance criteria:**

- [ ] Invalid stamp specs and absent V4 tuning fail loudly in Core tests.
- [ ] Every stamp presentation number is a V4 tuning key with an explicit unit.
- [ ] Existing VFX recipes remain valid and unchanged in behavior.

**Verification:** `verify-change.ps1` for the exact Core, tuning, and test paths.

**Dependencies:** Task 1.  
**Files likely touched:** `VfxRecipes.cs`, `VfxCatalog.cs`, VFX tuning model/loader/tests, `gk-core/data/tuning/vfx.v4.json`  
**Estimated scope:** M.

## Task 3: Embed the V2 runtime art in injector hosts

**Status:** Complete — build-gate PASS. The focused host contract passed 1/1, MelonLoader 3.9
compiled with 0 errors, and reflection found only the 128/256/512 V2 resources (no source master).

**Description:** Package V2 runtime PNGs as named manifest resources in all supported injector hosts
and pin their presence with a focused guard test.

**Acceptance criteria:**

- [x] Each host embeds the same V2 runtime resource names.
- [x] Source masters are not packaged as runtime resources.
- [x] Host-injection test fails if the package contract drifts.

**Verification:** Focused host-injection test and MelonLoader 3.9 compile.

**Dependencies:** Task 1.  
**Files likely touched:** three injector host `.csproj` files; `ActorHudHostInjectionTests.cs` or a
dedicated VFX host test  
**Estimated scope:** M.

## Task 4: Build the bounded ImpactStamp renderer

**Status:** Complete — focused source guard passed and the MelonLoader 3.9 host compiles with 0 errors.

**Description:** Add Unity-only cached resource loading and a fixed renderer pool that can animate,
release, clear, and disable Earth stamps safely.

**Acceptance criteria:**

- [ ] Texture and shared material are created once; each hit only leases/reuses a pooled renderer.
- [ ] Pool exhaustion, board end, and visual-toggle-off release every lease without throw.
- [ ] No forbidden material access or scene scan appears in the VFX source.

**Verification:** Focused guard tests, source scan, and MelonLoader 3.9 compile.

**Dependencies:** Tasks 2–3.  
**Files likely touched:** `ImpactStampPool.cs`, `FxResources.cs`, focused injector guard test  
**Estimated scope:** M.

## Task 5: Wire Earth-only hit dispatch

**Status:** Complete — Core selection coverage proves only a concrete Earth payload selects the stamp;
hybrid and element-disabled payloads preserve the existing visual behavior. MelonLoader 3.9 compiles
with 0 errors.

**Description:** Add the stamp to the admitted `combat.hit` recipe and VFX director dispatch while
retaining neutral and hybrid behavior.

**Acceptance criteria:**

- [ ] Only a concrete single Earth payload creates `impactStamp`.
- [ ] Hybrid/no-element and disabled-element cases never create Earth art.
- [ ] Standard `debug.fx.shown`/`debug.fx.skipped` telemetry identifies the outcome.

**Verification:** Core selection tests, focused VFX/guard verification, and MelonLoader 3.9 compile.

**Dependencies:** Tasks 2 and 4.  
**Files likely touched:** `VfxCatalog.cs`, `VfxDirector.cs`, VFX tests  
**Estimated scope:** M.

## Checkpoint: Offline Earth vertical slice

- [ ] Tasks 1–5 pass focused verification.
- [ ] All hosts package V2 art and the MelonLoader build is green.
- [ ] No gameplay, action, server, web, or actor-HUD behavior changed.

## Task 6: Run the Earth live presentation proof

**Status:** Game Injector Debug proof completed on the dedicated MelonLoader 4.0 install (2026-09-26).
Fresh controlled-lawn probes verified both directions: plant → zombie event `19204` and zombie → plant
event `19252`. Each recorded the concrete Earth RGB `#D2A046` and all six primitives:
`floater`, `burst`, `flash`, `impactStamp`, `charge`, and `travel`. This proves Unity presentation only;
it is not gameplay or persisted-domain evidence. A current fallback probe also recorded event `20146`:
with `SYS-ELEMENT-FX` off it retained only the ordinary `floater` (`#FFFFFF`) and emitted no Earth
phase. The toggle was restored to enabled and the dedicated game returned to its main menu. The owner
visual-acceptance checkpoint remains open.

**Description:** Trigger `combat.hit` with a concrete Earth payload through the existing Game Injector
Debug endpoint on a real plant and zombie, capture events/screenshots, and compare the toggle-off
fallback.

**Acceptance criteria:**

- [ ] `POST /api/debug/fx/play` emits `debug.fx.shown` with `impactStamp` for plant and zombie probes.
- [ ] Screenshots show Earth art aligned, readable, and cleaned up after expiry.
- [ ] `SYS-ELEMENT-FX` off removes only the stamp/element accent and ordinary hit feedback remains.

**Verification:** Live endpoint call, debug-event readback, lawn screenshots, owner visual review.

**Dependencies:** Offline Earth vertical slice.  
**Files likely touched:** `scripts/prove-vfx.ps1` only if the existing proof script needs one added
Earth case; otherwise none.  
**Estimated scope:** S.

## Task 7: Add the approved Earth charge and travel phases

**Status:** Complete — dedicated 4.0 Game Injector Debug proof on 2026-09-26 emitted
`floater`, `burst`, `flash`, `impactStamp`, `charge`, and `travel` for a concrete-Earth cue with
both live pointers. The same target-only cue emitted `impactStamp` without charge/travel.

**Description:** Reuse the existing Earth V1 runtime assets for an optional source-attached charge and source-to-target projectile travel. Extend only the existing cue → recipe → director → pooled primitive path, with `sourcePtr` as semantic debug input. Keep target-only production cues compatible.

**Acceptance:**
- [x] A concrete Earth debug cue with source and target renders `charge`, `travel`, and `impactStamp`.
- [x] Missing source skips only charge/travel; it retains impact and ordinary hit feedback.
- [x] Charge/travel are pooled, cache their assets once, and clear on expiry, board end, and VFX-off.
- [x] All injector hosts embed their V1 charge/travel runtime variants.
- [x] All Earth-phase presentation and sequence values load from current `vfx.v7.json` with explicit units; no runtime fallback values exist.

**Verification:** Focused VFX tuning/catalog and host-packaging tests, followed by the dedicated
MelonLoader 4.0 compile and live Game Injector Debug probes.

## Checkpoint: Earth decision

- [ ] Owner accepts the Earth visual in a real lawn.
- [ ] If not accepted, reopen Task 1 or Task 2 only; the catalog and other elements remain deferred.
