# Battle effect damage — does it reach the resolver, and with what payload?

**`solid-remediation` T2.1. Measured 2026-09-17 against the tree at `0328347a`. No production code
changed in this task.**

D1 says battle's `EffectBag` never sets `CombatMath`, so every effect-driven hit in a battle applies
its authored number verbatim. The plan's own risk row records the reason this spike had to run first:
wiring `CombatMath` was measured and **moved 0 of 13,943 tests**. A fix that changes nothing is either
already done or aimed at the wrong seam, and this answers which.

It is the second. The wiring is one of **two** missing links, and it is the one that does nothing on
its own.

---

## (a) Does effect-driven battle damage reach `CombatDamageDispatcher`?

**Yes. Every mode goes through the same call, and always has.**

| Caller | Line |
|---|---|
| `EffectBag` — the instant-delivery packet path | `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:567` |
| `EffectBag` — the second dispatch site | `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:637` |
| `StatusEffectBridge` | `gk-core/src/FusionRpg.Core/Status/StatusEffectBridge.cs:98`, `:144` |

So there is no missing route and nothing to build. What differs by mode is the `math` argument:

```csharp
// gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs:27
math ??= PassThroughCombatMath.Instance;
```

`EffectBag.CombatMath` has exactly two production setters repo-wide — `FoundationHarness.cs:138`
(the overlay harness) and `EffectRuntime.cs:539` (injector-side). `BattleRunState` sets
`Host.Bag.ShieldGate`, `Host.Bag.Status`, `Host.Bag.StatusRng` and `Host.Bag.BoardSnapshot`
(`BattleRunState.cs:342`, `:367-368`, `:356`) and never `CombatMath` or `ActorResolve`. Battle
therefore resolves through `PassThroughCombatMath`, whose `Finalize` returns the amount it was given.

**This half is exactly as D1 describes it.**

## (b) What `ElementPayload` does the packet carry?

**None. Empty, on both battle paths, for two independent reasons — and either one alone is enough to
make the wiring inert.**

**Reason 1 — the resolver returns early on an empty payload.**

```csharp
// gk-core/src/FusionRpg.Core/Combat/OverlayCombatMath.cs:42-43
if (packet.ElementPayload == null || packet.ElementPayload.Count == 0)
    return signedAmount;
```

`OverlayCombatMath.Finalize` returns the amount **unchanged** before it reaches
`OverlayCombatCalculator.Compute`. This is the whole explanation of the 0-of-13,943 measurement:
setting `CombatMath` swaps `PassThroughCombatMath` (returns the amount unchanged) for
`OverlayCombatMath` (returns the amount unchanged, one branch later). Two different classes, the same
output, byte for byte.

**Reason 2 — nothing on the battle side ever bakes a payload.**

`AtomCompiler` builds one, correctly and from the shared implementation, but only under a condition
battle never satisfies:

```csharp
// gk-core/src/FusionRpg.Core/Effects/Atoms/AtomCompiler.cs:236-247
if (ownerElementPrimary is { } primary
    && !overlay.ContainsKey("elementPayload")
    && actions.Any(a => string.Equals(a.Action, EffectActions.ApplyResourceDelta, ...)))
{
    var built = HybridPayload.BuildOverlay(primary, ownerElementSecondary, hybridSecondaryWeightMilli);
    if (built != null) overlay["elementPayload"] = built;
}
```

Of the four production `AtomCompiler.Compile` call sites, **one** passes an owner element:

| Call site | Passes `ownerElementPrimary`? |
|---|---|
| `gk-core/src/FusionRpg.Server/AtomPushService.cs:294` | **yes** — `ownerElementPrimary: ownerElements?.Primary` |
| `gk-core/src/FusionRpg.Data/Sqlite/ActionContainerEffectResolverFactory.cs:63` | no |
| `gk-core/src/FusionRpg.Data/Sqlite/ActionContainerEffectResolverFactory.cs:153` | no |
| `gk-core/src/FusionRpg.Core/Battle/Siege/ConstructionActions.cs:185` | no |

The three that do not are the battle-side ones. Battle's own direct apply path defaults the same way:

```csharp
// gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:860-865
ElementPayloadComponent[]? components = null, ...
    components ?? Array.Empty<ElementPayloadComponent>(),
```

## (c) What must change, and in what order

**Two changes, and the order is the finding.** Doing the wiring first is the measured no-op; doing it
second is a fix.

1. **The payload seam first (T2.4).** The battle compile paths must pass the owner's element into
   `AtomCompiler.Compile`, the way `AtomPushService` already does. The arithmetic already exists —
   `HybridPayload.BuildOverlay` — and calling it is the only sanctioned way to produce this shape, per
   `AtomCompiler`'s own comment: *"Built by calling HybridPayload.Build directly — never a second
   implementation of its arithmetic."* A second implementation here would be a second owner of
   responsibility 2, which `guard-battle-responsibility.py` now refuses.

2. **The wiring second (T2.5).** `BattleRunState` sets `Host.Bag.CombatMath` and
   `Host.Bag.ActorResolve` beside the existing `Host.Bag.ShieldGate = ShieldGate` line
   (`BattleRunState.cs:342`). No new lambda is needed: the `CombatActorResolve`-shaped closure the
   `ShieldGate` constructor already takes at `BattleRunState.cs:332-335` is the same signature, and
   reusing it is what keeps one actor-resolve rule rather than two.

**The adjacent line records the identical defect, already fixed once.** `Host.Bag.ShieldGate` is
wired at `:342` with a comment saying neither `BattleEffectHost` nor `SimEffectHost` ever set it, so
a granted shield and a swing-dealt hit would otherwise land on two separate stacks. That is D1's shape
exactly, one property earlier, caught by someone who noticed a granted shield doing nothing.

### What this spike deliberately does not decide

Whether `elemental-resolver` (T2.2/T2.3) lands before or alongside T2.4. The build order in the map
already puts `elemental-resolver` first and this measurement does not disturb that: the payload seam
is where an element enters the packet, and the resolver is what reads it — the seam is useless without
a reader, and the reader is unreachable without the seam.

### Register rows added

None. Everything here is a wiring gap inside a module this program owns, not a stub, a dark feature or
an unowned responsibility.
