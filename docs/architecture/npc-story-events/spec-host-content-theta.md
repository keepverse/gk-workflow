# Spec: host-content-theta

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `host-content-theta`, row 6 of the [npc-story-events map](../npc-story-events-map.md) (`:212`), wave 1.
Depends on party-dungeon's `difficulty-ladder` (external: `RoomTheta`, `RoomThetaComposer`). Consumed by
`choice-resolution` (contests and prices), `outcome-routing` (magnitudes) and the wave 4 hosts. Implements ideal
§11 item 2 (`npc-story-events-ideal.md:675`). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Give every storylet host a `Θ_content` through the **one** composer and the SSOT formula, with that host's own
inputs: a world sector's danger band for world hosts, the dispatch tier for expeditions, the room Θ the Delve
already composes, and danger 0 for the homeworld. A wiring module: no new curve, no new weight, no second composer.

Success looks like: every host's Θ is `PowerIndexComposer.ContentExplain(power, ctx).Total` for a
`ContentContext` built by exactly one producer per input; the Delve's Θ is `RoomTheta.Theta` passed through
unchanged; no type in `FusionRpg.Core.Narrative` constructs a `ContentContext` except this module.

## Locked anchors

- The SSOT formula: `Θ_content = Wz·zombossLevel + Wm·mapLevel(M) + Ww·worldTier + Wf·realmsAdvanced`
  (`docs/architecture/power/ssot-power-scale.md:230`); contests read `Θ_actor − Θ_content`, magnitudes read
  `P(Θ_content)` (`:232-233`).
- The one composer: `PowerIndexComposer.ContentExplain(PowerTuning, ContentContext)`
  (`gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:63-74`) over `ContentContext(DangerBand, WorldTier,
  ZombossLevel, RealmsAdvanced)` (`gk-core/src/FusionRpg.Core/Power/ContentContext.cs:16`); Θ is an `int`
  (`gk-core/src/FusionRpg.Core/Power/PowerAxisReport.cs:11`). `mapLevel` is `Wm · DangerBand`, one function
  (`PowerIndexComposer.cs:77-97`).
- The Delve already composes Θ per room: `RoomThetaComposer.Compose` (`gk-core/src/FusionRpg.Core/Delve/Difficulty/RoomTheta.cs:44-70`)
  returns `RoomTheta(Context, Theta, Band)` (`:36`).
- A sector's danger: `WorldSector.DangerBand` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:156`).
- One power ladder (DESIGN-GATE §2.14; map principle 5, `:86-90`): a new `f(level)` is the defect.

## Design

### 1. What exists and what is missing, read against the code

| Input | Live source today | Evidence |
|---|---|---|
| `DangerBand` for a world sector | `WorldSector.DangerBand` | `WorldState.cs:156` |
| `DangerBand` for a Delve room | `RoomThetaComposer` from the domain entrance band, depth, rung and tail | `RoomTheta.cs:50-56` |
| `WorldTier`, `ZombossLevel`, `RealmsAdvanced` (`ParentWorldTerms`, `RoomTheta.cs:12`) | **none.** No production code constructs a `ParentWorldTerms` from live state; every construction is a test literal | `gk-core/src/FusionRpg.Core/Delve/Domains/DelveStart.cs:48-51`; `WorldState` has no tier or level field (`WorldState.cs:332-352`); `realmsAdvanced` has no column and reads 0 (`gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs:12-18`) |
| expedition danger | **none.** A tier has duration, ticks, battles and slots only | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTierCatalog.cs:7-8`; `gk-core/data/tuning/expeditions.v1.json` `tiers` |

So the only live content input outside the Delve is a sector's danger band. This module adds **one** producer for
each missing input and names the owner of each gap; it invents no value.

### 2. One producer of `ParentWorldTerms`

`ParentWorldTermsSource.For(WorldState? world)` (new, Core, pure) is the single place a `ParentWorldTerms` is built
from state. Today it returns `new ParentWorldTerms(WorldTier: 0, ZombossLevel: 0, RealmsAdvanced: 0)` for every
world, with a comment naming each term's missing source and owner: `WorldTier` and `ZombossLevel` (world-map
program; no field on `WorldState`), `RealmsAdvanced` (power/empire program; no column). This is the same
"absence, not corruption" reading `PowerIndexComposer` already applies (`ClampNonNegative`,
`PowerIndexComposer.cs:108`; documented at `ServerPowerIndexProvider.cs:16-18`). The Delve's `DelveStart` wiring
is pointed at the same producer — Audit 2026-09-19: that wiring is now this program's `delve-live-start` (Owner ruling
2026-09-19 (round 3)), whose `DelveParentTerms.For` only chooses which world to read and calls this function
(`spec-delve-live-start.md` §3) — so the Delve and every narrative host read one set of parent terms. When a term gains a source, this function is the only edit.

### 3. Θ per host

```csharp
namespace FusionRpg.Core.Narrative.Hosts;

public sealed record HostTheta(ContentContext Context, int Theta);

public static class HostContentTheta
{
    /// World slot hosts and world.petition: the sector's own danger band.
    public static HostTheta ForSector(PowerTuning power, WorldSector sector, ParentWorldTerms world);

    /// expedition.return: the dispatch tier's danger band (expeditions tuning, §4).
    public static HostTheta ForExpedition(PowerTuning power, ExpeditionTierDef tier, ParentWorldTerms world);

    /// sanctum.hub: danger 0 — the homeworld is safe ground (a band, not a special case).
    public static HostTheta ForHomeworld(PowerTuning power, ParentWorldTerms world);

    /// delve.*: the room's already-composed Θ, passed through; never recomposed here.
    public static HostTheta ForDelveRoom(RoomTheta room) => new(room.Context, room.Theta);
}
```

Each of the first three builds one `ContentContext(dangerBand, world.WorldTier, world.ZombossLevel,
world.RealmsAdvanced)` and returns `PowerIndexComposer.ContentExplain(power, ctx).Total`. The homeworld's band 0 is
the shipped homeworld danger band (`PowerIndexComposer.cs:80`: *"homeworld 0"*), not a new constant.

### 4. The expedition tier's danger band

A new required key `tiers.{tierId}.dangerBand` joins the expeditions tuning, published as `expeditions.v2.json`
through `python gk-core/tools/tuning/publish.py expeditions --add-key tiers.<tierId>:dangerBand=<n>` for each tier.
`ExpeditionTuningLoader.Parse` (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs:30-65`) reads it as a required
`int` like its siblings, and `ExpeditionTierDef` gains `DangerBand` (`ExpeditionTierCatalog.cs:7-8`). The value is a
property of the tier, so it belongs to the tier's domain file, beside the encounter chance ideal §7 also puts there
(`npc-story-events-ideal.md:602`). Starting shapes by principle — a tier's danger matches the sector bands its
battles resemble (`PowerIndexComposer.cs:80`): `scout-30m` 1, `forage-4h` 2, `hunt-8h` 3, `warpath-20h` 4. The
expedition resolver never reads the key, so expedition tier hashes are unchanged (G4, `npc-story-events-map.md:300`).

### 5. No cache

Θ is computed per call from values the caller already holds. Nothing is stored.

## Data shapes

- `expeditions.v2.json` (new version): `tiers.{tierId}.dangerBand` (int, a danger band index).
- No SQL, no seed field.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| Θ | `int` | the composer's own type (`PowerAxisReport.cs:11`); the composer widens to `long` per-mille internally and divides once (`PowerIndexComposer.cs:90-94`, `:103`) |
| danger band, world tier, levels | `int` | bounded indices, `ContentContext`'s own types (`ContentContext.cs:16`) |

## SOLID notes

- **S:** one composer (`PowerIndexComposer`), one parent-terms producer, one room-Θ composer (the Delve's, reused).
- **O:** a new host adds one `For*` arm that builds a `ContentContext`; the formula never changes here.
- **D:** hosts depend on `HostContentTheta`, never on the weights.
- No private curve: a test fails if any `Narrative` type calls `new ContentContext(` outside this file.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs','gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs','gk-core/data/tuning/expeditions.v2.json','gk-core/tests/FusionRpg.Core.Tests/Narrative/Hosts/HostContentThetaTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Hosts|FullyQualifiedName~Expedition|FullyQualifiedName~Power"
python scripts\audit-overflow.py ; python scripts\audit-magic-numbers.py --domain narrative
```

`gk-core/data/tuning/expeditions.v2.json` has no verification boundary today (only named tuning files are mapped); the
build task adds it to the expedition owner boundary or to `core-narrative`.

## Structure

```
gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs        (new)
gk-core/src/FusionRpg.Core/Narrative/Hosts/ParentWorldTermsSource.cs  (new)
gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs            (edited: required tiers.*.dangerBand)
gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTierCatalog.cs       (edited: ExpeditionTierDef.DangerBand)
gk-core/data/tuning/expeditions.v2.json                               (new, published by gk-core/tools/tuning/publish.py)
gk-core/tests/FusionRpg.Core.Tests/Narrative/Hosts/HostContentThetaTests.cs     (new)
```

## Testing strategy

- **Same composer:** for sector bands 0–6 and non-zero parent terms, `ForSector(...).Theta` equals
  `PowerIndexComposer.ContentExplain(power, ctx).Total` for the same context.
- **Delve pass-through:** `ForDelveRoom(room).Theta == room.Theta` and the context is the same reference.
- **Homeworld:** `ForHomeworld` equals `ForSector` over a band-0 sector.
- **Monotone in danger:** Θ does not decrease as the band rises with the other terms fixed (a property of the
  shipped weights, asserted as a relation, not as numbers).
- **Expedition key required:** deleting `tiers.hunt-8h.dangerBand` rejects naming it; the expedition resolver's
  tier hashes are byte-identical with v2 loaded.
- **One producer:** a source scan finds `new ParentWorldTerms(` only in `ParentWorldTermsSource` and tests, and
  `new ContentContext(` in `Narrative/` only in `HostContentTheta`.

## Success criteria

1. Every host kind has a Θ path through the one composer. 2. No new weight, curve or composer. 3. One
`ParentWorldTerms` producer, with each missing term's owner named in code. 4. Expedition hashes unchanged.

## Boundaries

- **Always:** compose through `PowerIndexComposer.ContentExplain`; reuse `RoomTheta` for the Delve.
- **Ask first:** giving `WorldTier`/`ZombossLevel` a source here (they are world-map's); changing a weight.
- **Never:** a private `f(level)`; a wealth-scaled threat (RimWorld's failure, ideal §4.1); a second room-Θ composer.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `HostContentTheta.ForSector/ForExpedition/ForHomeworld/ForDelveRoom` | `choice-resolution`, `outcome-routing`, wave 4 hosts |
| `ParentWorldTermsSource.For` | `delve-live-start`'s `DelveParentTerms` (Audit 2026-09-19: was a filed ask on party-dungeon), wave 4 hosts |

## Contradictions found (report; not fixed here)

1. **The formula has four inputs; only one is live outside the Delve.** The ideal §11 item 2 resolution
   (`npc-story-events-ideal.md:675`) reads as if every input were available. Three are not (§1). This is a wiring
   gap owned by world-map (tier, level) and power/empire (realms), not a design wall; until they land, world and
   expedition Θ vary with danger band only.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: power ladder, world map (reader), expeditions tuning, Delve difficulty (reader).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: ssot-power-scale.md §formula; PowerIndexComposer, ContentContext, PowerAxisReport,
    RoomTheta, DelveStart (the ParentWorldTerms gap), ServerPowerIndexProvider, WorldState, ExpeditionTierCatalog,
    ExpeditionTuning, expeditions.v1.json.
[x] Every claim cites file:line.
[x] One power ladder: no new curve; the only new number is a tier's danger index, a tuning key.
[x] No cache. No population pinned. Actor numbers: Θ_content only; no actor magnitude.
[x] No parallel composer.
[ ] Registry row: the source-scan test is local; no enforcement-registry row proposed. (Audit 2026-09-19: row
    proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | `spec-delve-live-start.md` §3 introduced its own `DelveParentTerms.For` read "over the power program's content-side inputs" — a second `ParentWorldTerms` producer this spec's one-producer scan (`new ParentWorldTerms(` only in `ParentWorldTermsSource`) would fail, and a SOLID S fork of the parent terms. It arose because the Delve wiring moved to this program after this spec named party-dungeon as the caller | **Fixed** (both specs): `DelveParentTerms` selects the world and delegates here; `delve-live-start` now depends on this module (map row 28 updated) |
| 2 | medium | `ssot-power-scale.md` §8 row 6 says expedition content is "authored as `Θ_content`"; this spec authors a tier `dangerBand` and composes Θ through row 23's `mapLevel = Wm·DangerBand` (§10 row 23). It stays inside the one composer and the closed §10 inventory (no new scale), but the SSOT's §8 wording differs | **Deferred:** propagation owed to `power/ssot-power-scale.md` §8 row 6 (outside this fence): "authored as a danger band composed through `ContentExplain`" |
| 3 | low | Map citations one line early (`:211`, `:299`) | **Fixed** |

Checked and clean: one composer (`PowerIndexComposer.ContentExplain`), contests read Θ and magnitudes `P(Θ)` (not
computed here), Θ `int` is the composer's own type with `long` per-mille inside, the new expedition key goes through
`gk-core/tools/tuning/publish.py --add-key` (verified the flag exists), expedition tier hashes asserted unchanged, no cache.

**Proposed enforcement-registry row:** `ns-one-content-theta-producer` — one `ParentWorldTerms` producer and no
`ContentContext` built in Narrative outside `HostContentTheta`; guard `HostContentThetaTests` source scan (promote to
Guard.Tests when a second consumer appears).
