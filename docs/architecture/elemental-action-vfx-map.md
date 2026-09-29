# Capability map: Elemental Action VFX V2

**Status:** Proposed — Earth-only pilot. No runtime implementation is authorized by this map.

The existing VFX layer is the only presentation path: semantic cues enter `IVfxSink`, then the
injector's `VfxDirector` resolves a C#-seeded recipe into pooled primitives
([vfx-ssot.md](vfx-ssot.md):32-66, 215-334). This initiative extends that path; it does not create
an action renderer, a second VFX sink, or an element-combat system.

| Module id | Responsibility | Depends on |
|---|---|---|
| `earth-pilot` | Add one pooled, asset-backed impact-stamp primitive to the existing `combat.hit` element path; load only Earth art; prove it through the existing Game Injector Debug cue surface and a live lawn review. | Existing VFX SSOT and Earth asset approval |

Build order: `earth-pilot`.

The later multi-element catalog is intentionally absent. It is a separate decision after the Earth
pilot's visual and performance acceptance; it must not be inferred from this map.
