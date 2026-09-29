# Implementation plan: Elemental Action VFX V2 — Earth Pilot

**Status:** Proposed.  
**Spec:** [Earth pilot](../docs/architecture/elemental-action-vfx/spec-earth-pilot.md).  
**Capability:** `earth-pilot` in [the capability map](../docs/architecture/elemental-action-vfx-map.md).

## Overview

Build three asset-backed, pooled Earth phases — source `Charge`, source-to-target `Travel`, and
target-ground `ImpactStamp` — inside the existing VFX cue → recipe → primitive path.
It appears only for a single-element Earth `combat.hit`, is triggered for review through the existing
`POST /api/debug/fx/play` Game Injector Debug relay, and is accepted or rejected from a real lawn
review before any other element, action moment, or catalog work begins.

## Dependency graph

```text
approved Earth art + manifest
        │
        ├── Core primitive contract + versioned tuning
        │         │
        └── host asset embedding ─────┐
                                    ├── injector pooled ImpactStamp + director dispatch
                                    │                 │
existing debug.fx.play relay ───────┘                 └── focused validation + live Earth review
```

`debug.fx.play` already accepts an Earth payload and is relayed by `/api/debug/fx/play`; it is a
consumed test surface, not a new endpoint task.

## Architecture decisions

- Extend `VfxPrimitiveKind` with the three Earth phases; keep `VfxDirector` as the single sink and
  lifecycle owner. No action renderer, second queue, or new host tick.
- Render through a fixed, shared-material SpriteRenderer pool. The texture decodes once and is cached;
  there is no per-hit GameObject, texture decode, `FindObjectsOfType`, `renderer.material`, shader, or
  AssetBundle.
- Add the phases to the existing `combat.hit` recipe and select Earth art only when resolved payload is
  concrete, single-element Earth. Preserve current mixed-color hybrid rendering without an Earth
  stamp.
- Preserve every V1 Earth source asset. The selected jade/moss/ochre art lands in `earth/v2/` with
  its master, 512/256/128 variants, and manifest.
- Tune impact behavior in `vfx.v4` and source-phase behavior in the published `vfx.v5` revision. Pool sizes and other runtime presentation
  values never become compiled constants.

## Phases

### Phase 1 — Art and data contract

1. **Earth V2 art package** — Finalize the selected Earth visual, generate the three runtime sizes,
   preserve its source master, and add an alpha/dimension/palette manifest.
2. **Primitive contract and tuning** — Add the Core recipe model/validation and the versioned VFX
   tuning shape/loader/tests required by a bounded stamp pool.

**Checkpoint — contract ready**

- V1 art remains untouched.
- New art manifest and `vfx.v4` parse/load tests pass.
- No existing recipe or element behavior changes yet.

### Phase 2 — Injector vertical slice

3. **Embed Earth art in all hosts** — Package only the V2 runtime art as manifest resources across
   supported injector hosts and add a focused host-injection regression test.
4. **Pooled stamp renderer** — Build `ImpactStampPool` plus cached resource acquisition; enforce its
   cap, fade/scale lifecycle, sorting, board clear, and visual-toggle cleanup.
5. **Recipe dispatch and selection** — Dispatch the new primitive through the already-admitted
   `combat.hit` path, restricting it to concrete Earth payloads and emitting the standard shown/skip
   events.

**Checkpoint — offline vertical slice**

- Focused Core and guard tests pass.
- MelonLoader 3.9 injector build succeeds against the legal local install.
- Repeated debug cue plays cannot allocate unbounded objects or materials.

### Phase 3 — Real-lawn proof

6. **Debug-triggered Earth review** — Deploy only after the above checkpoint, invoke
   `POST /api/debug/fx/play` against both a plant and zombie pointer, collect `debug.fx.shown` and a
   lawn screenshot, then repeat with `SYS-ELEMENT-FX` disabled.

**Checkpoint — owner decision**

- Earth identity, size, anchor, lifetime, and crowded-lawn readability are accepted in the real game.
- Disabled-element fallback preserves ordinary hit feedback.
- If the look fails, iterate V2 art/tuning only; do not start the multi-element catalog.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Earth art reads as fire, ice, or generic rock | High | Use the actor-HUD stone palette as the review reference; stop at Phase 3 and revise art before expanding scope. |
| Sprite looks detached across plant/zombie scales | High | Resolve location and size only through existing `UnitFrameResolver`; review both sides in the same live checkpoint. |
| Asset load or host packaging fails | Medium | Validate manifest and embedded resource names in a focused guard before deployment; skip safely at runtime. |
| VFX causes repeated allocation or leaks | High | Fixed renderer pool, cached texture/material, cap test, and toggle/board-clear tests before live play. |
| Debug relay is mistaken for domain proof | Medium | Label endpoint use Game Injector Debug; require event + screenshot and make no gameplay correctness claim. |

## Deferred work

- The Action VFX Presentation Catalog. Its reusable action-timeline direction is now captured in
  [Action presentation VFX ideal](../docs/architecture/action-presentation-vfx-ideal.md): actions
  compose existing phase primitives at semantic moments; the existing director remains the only
  presentation path. This pilot deliberately does not implement that future program.
- Earth cast, sustain, critical, or overload moments.
- The remaining five elements and hybrid authored art.
- Any server/web settings or endpoint changes.

## Completion criteria

The pilot completes only when every spec success criterion passes and the owner accepts the on-screen
Earth result. A green build or a `200 OK` debug response alone does not complete the pilot.
