# Spec: `actor-hud-core`

**Module id:** `actor-hud-core` · **Program:** [../actor-hud-map.md](../actor-hud-map.md) ·
**Ideal:** [../actor-hud-ideal.md](../actor-hud-ideal.md)
**Depends on:** — · **Blocks:** all other actor-hud modules
**Status:** implemented 2026-08-31 — shipped; `ActorHudLayoutTests` green.

---

## Assumptions

1. **Pure Core** — no Unity, no SQL, no HTTP. Namespace `FusionRpg.Core.Hud`.
2. **Presentation-only DTO** — `ActorHudSnapshot` is a **view of Hot snapshot data**, not a new SSOT store.
   The injector builder fills DTOs from runtimes and pins; Core types carry no gameplay logic.
3. **Level display** uses [ssot-power-scale.md](../power/ssot-power-scale.md) — display band from Θ, not raw
   magnitude on the lawn (GG-60). **`PowerBandDisplay.FromTheta` input comes from pinned `progression.power`
   only** — builder passes Θ from `InjectorDerivedOverride` pin, never from Unity fields or REST.
4. **Tunables** live in `data/tuning/actor-hud.v{n}.json` — loaded via existing tuning hub pattern
   ([tunables-ssot.md](../tunables-ssot.md)).
5. **Status strip cap** and row offsets are tunable; priority order is structural (documented in code comment).
6. **Display tokens from catalogs (amend 2026-09-07):** player-visible status/resource glyphs resolve
   from injected `status-catalog` / `resource-catalog` (`hudToken`, `color`, `displayName`) —
   [actor-hud-ideal.md](../actor-hud-ideal.md) §4.1. **`StatusInitials(id)` and hashed RGB are not
   SSOT** — they are legacy until H1–H3 delete them. Until catalogs inject, unknown id → designed
   placeholder (GG-62), never id-slice English.
7. **V2 identity-line geometry:** visual scale is authored once in `actor-hud.v7.json`: primary
   element glyph = 36 screen pixels, secondary = 30 screen pixels at reference scale. This is
   presentation geometry, not a gameplay magnitude; both Unity and the Web renderer consume the
   same named fields rather than reproducing a hidden 80% rule.

---

## Objective

Provide the shared **Actor HUD vocabulary**: snapshot DTOs, slot priority, overflow math, level-band
display mapping, and (after H1) catalog **resolve** helpers used by dump, fold, Unity, and Phaser.

**Success:** Given fixture statuses + cap, `Prioritize` returns CC-first order with overflow count;
given Θ, `PowerBandDisplay` returns stable display int for badge.

---

## Program acceptance share

`gk-core/tests/FusionRpg.Core.Hud.Tests/Hud/ActorHudLayoutTests.cs` — priority ordering, overflow count, band mapping
edge cases (Θ=0, large Θ). Module not done until these tests pass.

---

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter ActorHud
python scripts\audit-magic-numbers.py --targets M1
```

---

## Project structure

| Path | Change |
|------|--------|
| `gk-core/src/FusionRpg.Core/Hud/ActorHudSnapshot.cs` | **new** — DTO records |
| `gk-core/src/FusionRpg.Core/Hud/ActorHudTier.cs` | **new** — tier enum |
| `gk-core/src/FusionRpg.Core/Hud/MagnitudeBand.cs` | **new** — low/mid/high |
| `gk-core/src/FusionRpg.Core/Hud/ActorHudLayout.cs` | **new** — `Prioritize`, overflow |
| `gk-core/src/FusionRpg.Core/Hud/PowerBandDisplay.cs` | **new** — Θ → display band |
| `gk-core/src/FusionRpg.Core/Hud/ActorHudTuning.cs` | **new** — tunable shape |
| `gk-core/src/FusionRpg.Core/Hud/ActorHudTuning.cs` | Tuning shape, loader, and hub |
| `gk-core/data/tuning/actor-hud.v1.json` | **new** — v1 defaults |
| `gk-core/tests/FusionRpg.Core.Hud.Tests/Hud/ActorHudLayoutTests.cs` | **new** |

---

## Design

### DTO shape (C# — mirrors TS in fold spec)

```csharp
public sealed record ActorHudSnapshot(
    ActorHudIdentity Identity,
    ActorHudResources? Resources,
    IReadOnlyList<ActorHudStatusToken> Statuses,
    ActorHudOverflow Overflow);

public sealed record ActorHudIdentity(
    ActorHudTier Tier,
    string Role,           // "specimen" | "vanilla"
    int? LevelBand,
    IReadOnlyList<string> Flags);

public sealed record ActorHudResources(
    ActorHudShield? Shield,
    ActorHudHpSliver? HpSliver,
    IReadOnlyList<ActorHudMeter>? Meters);

public sealed record ActorHudShield(
    long Hp, long Max,
    IReadOnlyList<ActorHudShieldStack> Stacks);

public sealed record ActorHudStatusToken(
    string Id, bool Cc, MagnitudeBand MagnitudeBand);
```

### Priority order (plate 10 §D)

`ActorHudLayout.Prioritize(statuses, maxVisible)`:

1. CC statuses first (`Cc == true`)
2. Remaining by stable id order (deterministic — no frame-to-frame shuffle)
3. Return `(visible, overflowCount)` where `overflowCount = max(0, total - maxVisible)`

Identity row slot priority when rows compete for space (unity/phaser use same ordering):

1. CC glyph / frozen status
2. Unique/creature pip
3. Shield segments
4. Top N status tokens
5. Level badge · tier frame

### Level band

`PowerBandDisplay.FromTheta(long theta)` — map Θ to compact display int (e.g. 1–99 cap for badge width).
Use power ladder SSOT; **never** emit raw Θ on lawn. Caller (dump builder) supplies Θ from pinned derived
`progression.power` only — Core does not read pins or runtimes directly.

**DTO is not SSOT:** if pin is missing, builder omits `LevelBand`; Core layout code does not invent defaults.

### Tunables (`gk-core/data/tuning/actor-hud.v1.json`)

| Key | v1 default | Notes |
|-----|------------|-------|
| `statusStripMax` | 3 | Visible status tokens before `+N` |
| `hpSliverEnabled` | false | When false, builder omits `hpSliver` |
| `rowOffsetIdentity` | tunable | World Y offset fractions (unity reads) |
| `rowOffsetResources` | tunable | |
| `rowOffsetStatuses` | tunable | |
| `eliteTierThreshold` | TBD | Structural placeholder for elite band |

### V2 identity-line layout

The three visual rows are `identity + elements`, `resources`, then `statuses`. The identity line is
one centred sequence in this stable order: `tier?`, `role?`, `level?`, `primary element?`,
`secondary element?`. Omitted slots consume neither width nor vertical space. `ActorHudElements`
remains part of the existing presentation DTO and uses catalog ids only; it does not create a new
element model or change combat typing.

`actor-hud.v6.json` introduced the identity-line fields; the current `actor-hud.v7.json` makes the
live-legibility adjustment:

| Key | Unit | Meaning |
|-----|------|---------|
| `screenIdentityElementPrimaryPixels` | screen px | Primary glyph extent at Unity reference scale (36px in v7) |
| `screenIdentityElementSecondaryPixels` | screen px | Secondary glyph extent at Unity reference scale (30px in v7) |
| `screenIdentityElementGapPixels` | screen px | Gap between adjacent identity-line slots |

The parser rejects a missing or non-positive glyph extent. Hosts point at v7 only after its focused
loader and host-injection tests are green. The Web runtime obtains the same values through the
injected HUD presentation payload; it must not own a second numeric table.

---

## Boundaries

- No Unity types, no injector references; no File I/O (hosts inject catalogs; Core resolves from hub).
- No status id validation beyond non-empty string — closed vocabulary enforced in dump builder.
- Boss tier enum value exists but builder **must not emit** until expedition signal wired.
- **Never** authorize `StatusInitials` / hash RGB as the player token path after H3.
- Catalog *membership* inject is actor-surface-catalog; this module owns resolve API shape only.

---

## Test plan

| Test | Assert |
|------|--------|
| `Prioritize_cc_first` | CC statuses precede non-CC at same cap |
| `Prioritize_overflow_count` | 5 statuses, cap 3 → overflow 2 |
| `FromTheta_monotonic` | Higher Θ → higher or equal band |
| `Tuning_loads_defaults` | Missing file throws or uses documented fallback |

---

## Related

- [spec-actor-hud-dump.md](spec-actor-hud-dump.md) — fills DTO from Hot read surface
- [actor-hud-data-pipeline-audit-2026-08-30.md](../../research/actor-hud-data-pipeline-audit-2026-08-30.md)
- [10-actor-hud.html](../../design/10-actor-hud.html) §B legend
