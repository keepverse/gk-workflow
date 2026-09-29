# Spec: `bank-points`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`; **revised 2026-09-19 for
round 4** (bank point = the Counting House building); **round 5 applied 2026-09-20** (A1 start kit, X13). Every `file:line` below
was opened in this session. Module 2.8 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19; its owner decision **Q1** is superseded by round 4 §B). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md)
§8.5 (*"flows are not a star through one capital"*), §8.6. Umbrella contradiction X2.

## Objective

Answer one question, purely, every turn: **which sectors are this faction's bank points?** A bank
point is where a located good may leave the map (`banking-fact`) and where auto-banking flows head
(`logistics-flow` `auto-banking`). Bank points are many: every sector the faction owns that holds an
active **banking building** — the Counting House, whatever its tier.

## Round-4 decision (2026-09-19) — supersedes Q1

> *"Bank point is the Counting House building (replaces the earlier 'capability granted by default on
> the Vault slot'). The `bank` structure role keeps its meaning (a currency source)."*
> — [../decisions-round-4.md](../decisions-round-4.md) §B. Tiers: Counting House → Treasury → Vault;
> T1 makes the sector a bank point; T2+ adds the per-good hold and faster banking (both `banking-fact`'s).

Superseded: the map's Q1/D1 capability (`StructureDef.GrantsBankPoint`, defaulted from the `Vault` slot)
and the capital rule (an owned `Home`/`Boss` sector as an implicit bank point). Principle B says a feature
with no unlocking building in the sector is not available there, so a capital is a bank point only when
it holds a Counting House. The `bank` role keeps its meaning — a currency faucet (the soul conduit, the
reliquary; umbrella X2) — and never makes a bank point.

## Scope and non-goals

**In scope:** the query and its building rule.

**Not in scope:** the building rows (`empire-seed` `trade-structure-rows`); the tier read
(`trade-foundation` `sector-features`); what banking does at each tier (`banking-fact`); which bank point a
flow chooses (`logistics-flow` `auto-banking`); placing a starting Counting House (see *Start of play*).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| Exactly one `Home` sector per world, owned by the player at creation, holding a Seat slot | `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:200-217` |
| No shipped template places a structure on any slot | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs` (no `StructureId =` in either) |
| `build` founds a structure on an empty compatible slot | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:69-88` |

### Wiring gap

None in this module's path; the tier read is `sector-features`'.

### Real gap

The query. No structure takes goods off the map today, and no banking building row exists yet.

## Design

### 1. The rule

A sector *s* is a bank point of faction *f* when
`SectorFeatures.TierFor(s, f, SectorFeature.banking) >= 1` (`trade-foundation` `sector-features` §5a).
Nothing else grants it: no slot kind, no role, no sector flag.

**Round 6 S1 — one faction owns both the sector and the slot.** The read is `TierFor`, not `TierOf`,
because *"a building whose sector and slot have different owners counts for nobody until one faction owns
both"* ([../decisions-round-4.md](../decisions-round-4.md) Round 6 S1). `TierFor` applies that rule once,
in `sector-features`; this module adds no owner test of its own (it used to read *"f owns s"* separately,
which would have counted a Counting House on a slot the previous owner still held). Consequence on the
board: the turn a sector flips while its Counting House slot does not, the sector is a bank point for
**neither** side, and goods wait in the warehouse until the slot falls.

### 2. The query

```csharp
// src/FusionRpg.Core/World/Goods/BankPoints.cs (new)
public static IReadOnlyList<string> For(WorldState world, string factionId);   // ordinal sector-id order
public static int TierAt(WorldSector sector, string factionId);   // = SectorFeatures.TierFor(sector, factionId, banking); 0 = not a bank point
```

Pure over `WorldState`; computed each call, never cached (a stored bank-point set would go stale on the
first capture — the same reason `SupplyGraph` recomputes, `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:5-11`).
It takes no faction kind and branches on none. Which kinds bank at all is `banking-fact`'s.

### 3. Start of play (round 5, A1 — decided)

> *"Every empire's seat (player and AI) starts with a **tier-1 Counting House and a tier-1 Storehouse**;
> everything else is built."* — [../decisions-round-4.md](../decisions-round-4.md) R5-A A1.

So every empire has exactly one bank point at turn 0 — its seat sector — and the rule here still does not
special-case the start: the seat is a bank point because it holds a Counting House, read through
`SectorFeatures.TierFor` like any other (X13; round 6 S1 — §1). **Who places the buildings:** the world-creation seat
seeding belongs to `world-continuity` (the player's seat and every seat a template or world creation
places); `counterparties` `empire-roster` and `clan-seeding` carry the same start kit on the AI empires and
clans they seed. This module places nothing. Today no shipped template places any structure (table
above), so the start kit is a real gap in those owners' modules, not here.

## Tunables

None. The banking building's tier bands are `empire-seed`'s; the per-tier banking numbers are
`banking-fact`'s.

## Numeric types

None.

## Acceptance (contract)

1. A sector holding an active banking building of any tier is in its owner's result; the same sector
   after capture is in the captor's result and not the loser's.
2. A banking building under first construction, or unknown to the catalog, grants nothing; an upgrade in
   progress keeps the sector a bank point.
3. An owned `Home` or `Boss` sector **without** a banking building is not a bank point.
4. No `bank`-role row makes a bank point by its role (the soul conduit's sector is not one).
5. The result is in ordinal sector-id order with no duplicates (two banking buildings in one sector
   appear once).
6. Two factions with identical holdings get identical results whatever their `WorldFactionKind`.

## Test plan and verification boundary

`tests/FusionRpg.Core.Tests/World/Goods/BankPointsTests.cs` (new): items 1–6, on synthetic worlds
with a fixture banking row (no banking row is generated yet).

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Goods/BankPoints.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/BankPointsTests.cs') -Session <active-session-id>
```

## Structure

```
src/FusionRpg.Core/World/Goods/BankPoints.cs         (new)
tests/FusionRpg.Core.Tests/World/Goods/BankPointsTests.cs   (new)
```

## Boundaries and hard edges

- **Always:** recompute per call; the banking building is the only grant; tier from `sector-features`.
- **Ask first:** any implicit bank point (a capital rule, a slot default) — round 4 removed them.
- **Never:** cache the set; branch on faction kind; read the `bank` role as a bank point; place a
  building in a template from this module.

## Dependencies and interface

**Depends on:** `trade-foundation` `sector-features`. External: `empire-seed` `trade-structure-rows` (the
Counting House row with `featureUnlock: banking` and its two tier variants, `spec-trade-structure-rows.md` §5.2).

| Exposed | Consumer |
|---|---|
| `BankPoints.For(world, factionId)` | `banking-fact`; `logistics-flow` `auto-banking`, `path-cache` (roots, trigger T7); `trade-ai` (where an AI builds a Counting House); `trade-surface` |
| `BankPoints.TierAt(sector)` | `banking-fact` (rate, hold gate); `logistics-flow` `auto-banking` (the `bank-hold` admission) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: structures and corpus (feature tiers), world state (ownership).
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: decisions-round-4 (B, Q3); trade-network-ideal §8.5-§8.6; umbrella X2 and §1a;
    empire-seed spec-trade-structure-rows (through the cross-cluster sweep); sector-features.
[x] decisions.md checked: no lock on bank points.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (round-4 reconciliation).
[x] Verified against code: the Home rule; no template places a structure; BuildResolver's found path.
[x] Surrounding sections read: SupplyGraph's no-cache note.
[x] Constraints tested, not assumed: no golden claim (a pure query).
[x] No §2 invariant contradicted. Named correction (round 4): the Vault-slot capability and the capital
    rule are removed; the Counting House is the only grant.
[x] Corrections propagated: sector-yield map §5c; the start-of-play placement was an owner question
    there, answered by R5-A A1 (2026-09-20) and applied in §3.
[x] No population pinned.
[x] No event-refreshed cache (computed per call).
[x] Capture criteria hold in either order of capture and build (acceptance 1-2 are state-based).
[x] No actor magnitude.
[x] No SOLID fork: one query over the one feature read.
[x] Registry row: no new rule beyond the feature gate (sector-features owns its row).
```
