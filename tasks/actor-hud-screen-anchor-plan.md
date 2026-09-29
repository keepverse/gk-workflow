# Actor HUD screen-anchor plan

1. Define and unit-test rectangle-to-anchor math.
2. Project the actor SpriteRenderer union through an eligible camera; do not reuse VFX UnitFrame.
3. Use a pooled screen-space Canvas with rows flowing downward from the sprite bottom.
4. Publish v3 screen layout tuning and inject it from the host.
5. Replace world-anchor guards, build against MelonLoader 3.9, and copy only the DLL.

Out of scope: game-binary changes, game restart, HUD data semantics, or per-prefab offsets.
