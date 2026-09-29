# Spec: `structure-upkeep`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.7 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §5 real gap *"Structure
upkeep"*, §8.3 (*"Buildings pay loam through the structure upkeep term"*), §10 C9, §13
(`upkeep.structureTermByRole`). Economy rule P2 ([../../economy-principles.md](../../economy-principles.md)).

## Objective

Every active structure costs loam every turn. `LoamUpkeep` names the gap in its own comment — *"No
structure term yet"* (`gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:34-35`) — and P2 says territorial
income needs territorial upkeep. Without this term, yield buildings would be a faucet with no
territorial sink, and the soul conduit's own design (*"it pays loam upkeep like everything else"*,
`empire-economy-ssot.md:197-201`) would be false.

Success: one more additive operand in the existing upkeep sum, visible in the existing breakdown,
zero on legacy worlds, and zero everywhere while every role's term is zero.

## Scope and non-goals

**In scope:** the term, its tunables, the role field it reads, its place in the breakdown and the W10
projection's DTO.

**Not in scope:** goods upkeep (a doctrine's goods upkeep is `legion-build`'s; AI goods sinks are
`counterparties` `empire-goods-sinks`); trade legions' upkeep (they pay burn and action budget like
every legion, ideal §8.3); the belief-side estimate (below).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| Upkeep = (base + garrison + development + danger + wonder) × intensity × handicap × season, one divide | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:11-26`, formula comment `:28-36` |
| The truth side reads the breakdown, never a second formula | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:40`, `:47-80` |
| The one place the additive terms are named | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:93-106` |
| Belief-side overload leaves structure-sourced detail at 0 on purpose | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:90-97` |
| Readers of the breakdown: the W10 endpoint and the AI's frontier estimate | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:915`, DTO mapping `:785-802`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:177` |
| Upkeep is drawn per component in `Pressure` | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:158-165` |
| A structure's role is parsed from the corpus, then dropped | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:58` (`Role`); `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:289-326` (`ToStructureDef` copies no role) |
| Existing upkeep tests | `gk-core/tests/FusionRpg.Core.Tests/World/Loam/LoamUpkeepTests.cs`, `WonderUpkeepTests.cs`, `LoamUpkeepSeasonCallSiteTests.cs` |

### Wiring gap

| What is inert | Evidence | What closes it |
|---|---|---|
| The corpus row's `Role` never reaches `StructureDef` | above | `StructureDef.Role`, copied in `ToStructureDef` |

### Real gap

The structure term.

## Design

### 1. The role on `StructureDef`

`StructureDef.Role` (`string`), copied from `StructureCorpusRow.Role` in `ToStructureDef`. The
vocabulary is the corpus's closed role registry (`empire-seed` `band-reader` validates it; `exchange`
joins it by `empire-seed` `exchange-role`). This is a VALIDATED identity field, not a number.

### 2. The term

`LoamUpkeepBreakdown` gains `long StructureUpkeep`, and `Sum` adds it — so it is multiplied by
intensity, handicap and season exactly like every other operand, with one divide at the end
(`LoamUpkeep.cs:25`).

```
StructureUpkeep(sector) = Σ over slots with an active, known structure of
                          trade.Upkeep.StructureTermByRole[structure.Role]
```

- **Active only.** A structure under first construction pays nothing; the gate is
  `SectorFeatures.ActiveTier(slot) >= 1` (`trade-foundation` `sector-features` §3), which today equals the
  slot gate every reader uses (`gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:19-21`) and keeps a
  building mid-upgrade paying (and working) at its current tier.
- **Stamp-gated.** `BreakdownFor` reads the term only when the world's stamp grants
  `trade.structureUpkeep`; on a legacy stamp the term is 0 and the tuning is never read.
- **Its own wave, its own flag, its own bump (round 6 C1).** This module is `sector-yield` wave 2, row 2 of
  [../landing-order.md](../landing-order.md) §2. It used to gate on `trade.sectorYield`, which three other
  modules in three other waves also gated on — so a world stamped after wave 1 would have gained the loam
  term mid-life when this module merged (audit C1). Under round 6 C1 the flag is `trade.structureUpkeep`,
  registered here with the one `RulesetVersion` bump this wave takes, and the *"it can land first"* claim
  below is now true as written rather than blocked on an unregistered flag.
- **Charged to the hosting sector**, like the wonder term (`LoamUpkeep.cs:70-77`), so it joins that
  sector's component draw in `Pressure` with no new code there.
- **One row, one role, every tier.** Round 4's tier variants are one structure row (§B), so every tier of
  a building pays its row's role term; a per-tier upkeep factor, if a balance pass wants one, is a later
  published key, not a second formula.
- **Flat, not scaled.** Loam is Θ-invariant (`ssot-power-scale.md` §10.4, *"Decided: neither"*).
- **Belief side stays 0**, the stated precedent for structure-sourced detail (`LoamUpkeep.cs:93-96`).
  The AI's frontier estimate reads the truth-side breakdown already (`FrontierRulesPolicy.cs:177`), so
  it sees the term.

### 3. The projection

The W10 endpoint maps `StructureUpkeep` into the upkeep DTO beside `WonderUpkeep`
(`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:785-802`): one additive field, no rename or narrowing, so no
contract-version bump (`PRINCIPLES.md` §6). Showing it on screen is `trade-surface`'s.

### 4. The tuning file

`upkeep.structureTermByRole` lives in the `trade` tuning domain. **Creator (settled 2026-09-20,
reconciliation R-19.3):** there is no race with `warehouse-axis` — [landing-order.md](../landing-order.md)
§5 fixes `trade-foundation` `economy-report` (row 0a) as the one creator of `data/tuning/trade.v1.json`,
the `TradeTuning` parser, the host-injected hub and the `trade` domain in `gk-core/tools/tuning/publish.py`. **This
module publishes `v{n+1}`** with its own key. **Every role has a key**; a
missing role is a load rejection, never a default. The published starting values are decided by
principle (P2: a yield building's upkeep is a share of its own yield's loam-equivalent throttle) and
published as tunables; they are not owner questions.

## Tunables

| Key | Unit | Meaning |
|---|---|---|
| `upkeep.structureTermByRole.<role>` | loam per turn per active structure, flat | The structure term, one entry per corpus role |

## Numeric types

`long`, `checked` sum; the term enters `Sum` before the existing four-factor multiply, which is already
`long` and `checked` with one divide by `1_000_000_000` (`LoamUpkeep.cs:25`). Loam is Θ-invariant, so
no range growth comes from this term.

## Acceptance (contract)

1. With every role's term at 0, upkeep is byte-identical to today on any stamp, for every sector of
   every shipped template over a scripted run (`LoamUpkeepTests` and its siblings stay green with no
   expected value changed).
2. On a legacy stamp the term is 0 whatever the tuning says, and `TradeTuning` is never read on that
   path.
3. On a `trade.structureUpkeep` stamp, each active structure adds exactly its role's term to `Sum`, once;
   `BreakdownFor(...).Total == LoamUpkeep.For(...)` still holds (the existing no-second-formula test
   extends to the new operand).
4. A structure under construction adds nothing; it starts paying the turn it becomes active.
5. A tuning file missing any role is a load rejection naming the role.
6. The W10 DTO carries the term; its value equals the breakdown's.
7. `StructureDef.Role` equals the corpus row's role for every loaded row (asserted per row, not by
   count).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Loam/StructureUpkeepTests.cs` (new): items 2–5, 7.
- Existing `LoamUpkeepTests`, `WonderUpkeepTests`, `LoamUpkeepSeasonCallSiteTests`: item 1, unchanged.
- A server test beside the existing W10 projection test: item 6.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs',
  'gk-core/src/FusionRpg.Core/World/StructureCatalog.cs',
  'gk-core/src/FusionRpg.Server/WorldEndpoints.cs',
  'gk-core/src/FusionRpg.Contracts/WorldDtos.cs',
  'tests/FusionRpg.Core.Tests/World/Loam/StructureUpkeepTests.cs') -Session <active-session-id>
python gk-core/scripts/audit-magic-numbers.py --summary
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs      MODIFIED — StructureUpkeep operand, stamp-gated
gk-core/src/FusionRpg.Core/World/StructureCatalog.cs     MODIFIED — StructureDef.Role, copied in ToStructureDef
gk-core/src/FusionRpg.Contracts/WorldDtos.cs             MODIFIED — one additive field
gk-core/src/FusionRpg.Server/WorldEndpoints.cs           MODIFIED — maps it
data/tuning/trade.v1.json (or v{n+1})            upkeep.structureTermByRole
tests/FusionRpg.Core.Tests/World/Loam/StructureUpkeepTests.cs   (new)
```

## Boundaries and hard edges

- **Always:** extend the one breakdown; stamp gate; every role keyed.
- **Ask first:** scaling the term by `P(Θ)` (would break §10.4's "neither" for loam); a per-structure
  override table (a per-row magnitude under another name — `empire-seed-map.md` §5.4 obligation 2).
- **Never:** a second upkeep formula; a term on the belief side that the truth side lacks; a default for
  a missing role.
- **Hard edge — golden safety.** The term changes loam outcomes on any world that grants the flag, which
  is why it is stamp-gated; no legacy golden may move.

## Dependencies and interface

**Depends on:** `trade-foundation` `world-stamp`. Independent of every goods module — it can land first,
as its own wave with its own flag and bump (round 6 C1; landing order row 2).

| Exposed | Consumer |
|---|---|
| `LoamUpkeepBreakdown.StructureUpkeep` | W10 projection; `trade-surface`; the AI's frontier estimate |
| `StructureDef.Role` | this term only; `bank-points` does not use it (a bank point is the Counting House's `banking` feature through `sector-features`, round 4 §B — never a role) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: loam upkeep (world economy), structures catalog, tunables, a server DTO.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: economy-principles P2; empire-economy-ssot §5; ssot-power-scale §10.4; the
    ideal §8.3, §13; LoamUpkeep whole.
[x] decisions.md: magic-numbers row; empire resource registry (loam row unchanged).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: the formula and breakdown, the belief-side 0, both breakdown readers, the
    role dropped in ToStructureDef.
[x] Surrounding sections read: the formula comment's "no distance term" and "no structure term yet".
[x] Constraints tested, not assumed: "no expected value changed" is acceptance 1, to be proven.
[x] No §2 invariant contradicted: loam stays Θ-invariant; the number is tuning.
[x] Corrections propagated: none needed.
[x] No population pinned (per-row assertion for Role).
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one breakdown extended, one role field.
[x] Registry row: no new rule; the no-second-formula test already exists and is extended.
```
