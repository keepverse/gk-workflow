# Action presentation VFX — the ideal

**Status:** Idea phase, 2026-09-26. Not a specification. No implementation is authorized by this document.

## Which loop this extends

This extends the **lawn — first core** and the shared **combat depth** language: it makes a resolved
action legible without changing its damage, targets, timing, state, or outcome. It is presentation
only, so it does not create a new gameplay loop and must not make an unlocked RPG feature lawn-only.

Garden Keeper is an RPG plus empire-building extension over a legal Fusion install. The RPG remains
in its own layer; Unity is only enriched by an overlay. Presentation observes a semantic outcome and
can be absent, delayed, or dropped without changing that outcome. The hot path remains local,
record-then-drain, and never waits for the Server. There is one power ladder, but this program does
not introduce any level-derived value. Presentation values that need tuning live in versioned VFX
tuning, not constants.

## What this is

An action may express one or more **presentation phases**. A phase selects a reusable VFX primitive,
a semantic anchor, and an offset from an action moment. For example, Earth may compose:

```text
commit/source  -> Charge
release        -> Travel
resolve/target -> ImpactStamp
```

These are not three Earth-only effects and not three gameplay actions. `Charge`, `Travel`, and
`ImpactStamp` are reusable presentation primitives. A different action can use one, two, or all
three; a defensive action can use a target-side phase only. The action declares *which semantic
moments it presents*, while the VFX catalog owns *how those phases look*.

## What already exists

### Built

- The VFX path is already singular: semantic cue -> Core recipe -> `VfxDirector` -> bounded pooled
  Unity primitive. `VfxDirector` is the production sink and its `Play` method only queues work;
  Unity work happens in its main-thread tick (`gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs:17-43,75-118`).
- Recipes already select multiple primitives with delays, and the director already owns unscaled
  lifetime, admission, anchor resolution, resource reuse, and board cleanup (`docs/architecture/vfx-ssot.md` §6-§9).
- The Earth pilot has reusable `Charge`, `Travel`, and `ImpactStamp` primitive implementations
  in the same director/pool seam (`gk-fusion/src/FusionRpg.Injector/Fx/EarthPhasePool.cs`,
  `gk-fusion/src/FusionRpg.Injector/Fx/ImpactStampPool.cs`).
- Current action taxonomy is intentionally closed: five categories, nine tags, and three action
  kinds (`gk-core/src/FusionRpg.Core/Actions/ActionEnums.cs:8-84`). Presentation phases must not become a
  category, tag, or subcategory.

### Wiring gap

- Funnel-originated `combat.hit` maps only target, amount, tag, and elements into its cue
  (`gk-core/src/FusionRpg.Core/Vfx/VfxCueMapper.cs:8-21`). It does not convey a source anchor, so its normal
  production path can render target feedback but cannot select source-attached charge or
  source-to-target travel.
- `DamageFxCueAdapter` is the existing bridge from Funnel feedback to the director
  (`gk-fusion/src/FusionRpg.Injector/Fx/DamageFxCueAdapter.cs:11-23`). It is not an action-presentation
  producer and supplies no action id or lifecycle moment.

### Real gap

- There is no Core, Unity-free contract that lets an action execution declare an ordered set of
  presentation phases with source/target anchors and semantic moments. Neither the current damage
  cue nor the action data model selects a phase timeline.

## Prior art

The useful convention is a short event-relative timeline, not an animation script per skill:

- Unity's animation-event guidance puts callbacks on meaningful animation frames, which makes an
  effect follow wind-up/release/impact rather than arbitrary wall-clock timing. The equivalent here
  is a semantic action moment, not a Unity `AnimationEvent`, because Core cannot reference Unity.
  Source: [Unity Manual — Using Animation Events](https://docs.unity3d.com/Manual/animeditor-AnimationEvents.html).
- Unreal Niagara separates an effect system from the gameplay event that activates it; reused systems
  are parameterized rather than copied per ability. The comparable boundary here is an action
  presentation request resolved by the existing director, not an emitter owned by every action.
  Source: [Unreal Engine — Niagara overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine).

The failure mode to avoid is effect wallpaper: if every basic hit always composes all three phases,
the phases stop communicating action identity and waste the existing bounded pool. Selection needs
to be data-driven, moment-specific, and subject to the director's current cap/rate-limit policy.

## The shape

Add one future Core-only **action presentation recipe** that maps an action/moment plus element or
variant policy to an ordered list of phase references. A phase reference contains only:

- an existing primitive kind (`Charge`, `Travel`, `ImpactStamp`, or an already-defined primitive);
- semantic anchor role (`source`, `target`, `cell`, or explicit world point);
- a delay relative to the named moment, life/scale profile reference, and optional element predicate;
- a degradation policy when its anchor is absent (normally skip that phase).

Action execution would emit one semantic presentation request with action identity, moment,
source/target identity, and elements. `VfxDirector` resolves that request through the same catalog,
queue, admission, shared `UnitFrameResolver`, cached resources, and fixed pools it owns today.
The normal `combat.hit` cue stays as backward-compatible target feedback; it must not be replaced by
an action renderer or a second queue.

This gives one action the ability to compose any number of phases with intentional timing while
preserving reuse: a projectile attack may use all three; a shield action might use charge plus a
target stamp; an instant hit uses impact only. It also keeps presentation independent from action
results: no VFX phase can delay, write, calculate, or fabricate gameplay.

Rejected shapes:

- **Per-action Unity renderer/prefab:** duplicates pools, anchors, and lifecycle ownership.
- **Hard-coded phase switches in every action executor:** makes timing an untestable code fork and
  prevents catalog reuse.
- **A new action vocabulary for VFX:** conflicts with the closed action taxonomy; a phase is
  presentation metadata, not an action classification.
- **Encoding visual timings in gameplay action timings:** couples cosmetic iteration to combat
  resolution and invites VFX to affect gameplay.

## Tunables

The timeline's delay, lifetime, scale, cap, and rate settings are presentation tuning. The future
spec must place them in a new published `data/tuning/vfx.v{n}.json` revision with explicit units.
Action data references stable profile ids; it does not embed arbitrary visual values per action.
Structural maximums protect the frame budget and must be documented as such, never as progression
ceilings.

## What this deliberately does not decide

- Which other elements ship, their art direction, or their asset catalog.
- A new primitive, shader, asset bundle, material strategy, or global VFX cap.
- How a particular action obtains `source`/`target` anchors; that is a future action-execution
  wiring decision proved through a real execution path.
- Combat timing, action categories/tags, targeting, damage, status, or Element Hub semantics.

## Owner decisions for the next phase

1. Approve the action-presentation timeline as the single reuse model, then graduate it through
   `/spec` into a capability map and module specs.
2. Choose which phase primitives and Earth assets should be reviewed next; those assets can be
   designed independently of the future wiring.

## Design-gate record

- Read product vision and loop SSOTs, VFX SSOT, event/overlay control-loop constraints, action
  ideal/map/seeding material, software architecture, decisions, and session-boundary policy in this
  session.
- Verified the actual presenter seam and the missing source/action fields in the current code.
- No architecture change is locked by this idea document; the proposed future program must complete
  its own design gate and specify tests before implementation.
