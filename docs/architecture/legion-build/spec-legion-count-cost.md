# Spec: `legion-count-cost`

**Status: written against shipped code 2026-09-19.** Module id `legion-count-cost`, row 15 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `member-stack`). Ideal:
[legion-build-ideal.md](../legion-build-ideal.md) §5 (Total War: a steep flat per-army tax forces a
doomstack; price army count on a curve) and §11 (never capped).

## Objective

Fielding another legion costs more on a **curve**, inside the burn every legion already pays — no new
quantity, no second pricer, no cap.

Success looks like: with the curve flat at 1000‰, burn is exactly today's; the curve is monotone and has no
point where a legion cannot be fielded.

## Scope and non-goals

- **In:** one multiplier on `LegionSupply.Burn` from the owning faction's fielded-legion count.
- **Out:** garrison upkeep (`LoamUpkeep`, a sector cost); any cap on legion count.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | Burn per unit, paid only outside supply | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:24-25,64-131` |
| Built | Callers of `Burn` | `LegionSupply.cs:34,48,131`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:477`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:999` |
| Built | Curve shape `[x, multiplierMilli]`, clamp at end points, interpolate linearly | `docs/architecture/effect-atom/definitions.md` §2 *Curves* |
| Real gap | Nothing reads how many legions a faction fields | — |

## Design

`Fielded(faction)` = the number of the faction's entities with at least one member. `Burn(entity, world)` =
`units × BurnPerMember × curve(Fielded(owner)) / 1000`, checked, divide last. All callers pass the world.

The curve reads **legion count, not level**, so it is not a power-ladder curve and adds nothing to the
`ssot-power-scale` §10 inventory. **Past its last authored point it extends by its last segment's slope
(corrected by the 2026-09-20 audit).** The first draft clamped at the end point (the `definitions.md` §2
rule for *atom* curves). Here that would be a ceiling on an upkeep that must keep scaling with holdings:
past the last point every further legion would cost the same, which is the "flat rate facing a scaling
sink" PS-8 names as a cap, and a territorial faucet would outgrow its sink (economy-principles P2). The
same extension rule `legion-traditions` uses for its thresholds. A flat final segment remains legal, and
then the tail is flat **because the tuning says so**, stated in the file's `_meta.note`, never because code
clamps. Below the first point (one legion) the multiplier is the first point's.

## Tunables

`legion.v1.json` (proposed; the file does not exist yet) `countCost.curve` — points `[fieldedLegions,
multiplierMilli]`, validated monotone non-decreasing, first point ≥ 1000‰.

## Numeric types

`long`, `checked`, widened before multiplying, per-mille divided last.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Loam|FullyQualifiedName~TurnEngine"
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs      MODIFIED  curve term; world parameter
gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs MODIFIED  caller
gk-core/src/FusionRpg.Server/WorldEndpoints.cs             MODIFIED  caller (DTO burn)
```

## Testing strategy

- Flat curve ⇒ burn identical to today for every legion (property).
- Monotone: adding a legion never lowers any legion's burn.
- (Audit 2026-09-20) Past the last authored point the multiplier keeps rising by the last segment's slope
  (a fixture with a rising last segment); a flat last segment stays flat; the arithmetic is `long`,
  `checked`, divide last.
- No refusal path exists (a faction with 1,000 legions still fields the next one).
- Non-monotone or sub-1000 first point fails tuning load.

## Boundaries

- **Always:** one term, inside `Burn`.
- **Ask first:** a count term in garrison upkeep.
- **Never:** a cap; a second pricer.

## Success criteria

Flat-identical; monotone; uncapped; one term.

## Interface exposed to dependents

`Burn(entity, world)` — the AI's runway reads (`FrontierRulesPolicy.cs:477`) see the same number.

## Hard edges

**Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave** (owner decision C1, 2026-09-20): a world's rules never change mid-life, and the family keeps a single landing order in [landing-order.md](../trade-network/landing-order.md). The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1). This module is **wave 3**. It ships with a flat curve, riding **wave 3's single bump**; the
publish that bends the curve is its **own landing** with its own bump, and it re-blesses loam goldens with the
reason. Two landings, two bumps — a flag is never registered before the behaviour it gates exists.

## Dependencies

`member-stack` (units).

## Design-gate checklist

```
[x] Subsystems: world loam economy (burn), tunables.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal. NOT read: economy-principles.md, empire-economy-ssot.md, ssot-power-scale.md.
[x] decisions.md checked: no lock on burn.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: Burn and all its callers.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted: no cap, one pricer, not a level curve.
[x] Corrections propagated.
[x] No population count pinned.
[x] No cache.
[x] No ordering assumption.
[x] No actor magnitude.
[x] No parallel path.
[x] No new rule needing a registry row.
```
