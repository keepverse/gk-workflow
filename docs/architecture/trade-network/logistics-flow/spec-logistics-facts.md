# Spec: `logistics-facts`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `logistics-facts`, row 10 of the
[logistics-flow map](../logistics-flow-map.md) (wave 2; depends on `lane-flow`, `transit-buffer`,
`lane-loss`). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §14b (*"every loss carries a
readable cause from `logistics-flow` onward; lane cuts and lost caravans write story facts at once"*;
the one-sentence status line *banked N · lost M (main cause) · stuck K (worst bottleneck)*), §8.5
(visibility). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Say what logistics did, every turn, in a closed vocabulary other programs can read without parsing
prose: what was cut, what was lost and why, what is stuck, what was wasted at a full warehouse, which
flows fell short and why, which policies fell back. Written from the first turn the phase runs, scoped
to the faction it is about, so it never leaks through the fog.

Success looks like: every loss the phase applied appears in the report exactly once with one cause; the
report's losses sum to the losses applied; a faction's projection never contains another faction's
logistics entry; and the kinds and token sets are pinned as closed vocabularies with a reason.

## Locked anchors

- **The report is the log** (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-35`). Facts are report
  entries, nothing else.
- **Structured scoping, never prose filtering.** An entry about somewhere names it in `SectorId`; an
  entry about someone names them in `Audience` (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:12-31`).
- **Banking and halts are not this module's.** `banking-fact` writes banking entries; `production-halt`
  writes halt entries (`sector-yield-map.md` §2.5, §2.9). This module never duplicates them.
- **Translation is not this module's.** The tokens are closed sets; `trade-surface` `trade-lexicon`
  translates them (map ask A6).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Report entry: phase, kind, subject, detail, `SectorId`, `Audience` | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:31-32` |
| Report kinds are string constants in one static class — five today | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10` |
| Hot-tail reports are stored with their phase list; older ones are re-derived | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:475-476`, `:750-760` |

### Wiring gap

None.

### Real gap (this module closes it)

The logistics kinds, their token grammar, the L8 emission step and its fog scoping.

## Design

### 1. The kinds — a closed vocabulary

| Kind | One entry per | Subject | `SectorId` | Detail tokens |
|---|---|---|---|---|
| `lane.cut` | (faction, lane) where a packet became `Stranded` this turn | lane id | lane's `FromSectorId` | `good=…;qty=…` (qty newly stranded) |
| `logistics.loss` | (faction, lane, good, cause) with non-zero loss | lane id | lane's `FromSectorId` | `good=…;qty=…;cause=…` |
| `logistics.strand` | (faction, lane, good) with goods `Stranded` at turn end | lane id | lane's `FromSectorId` | `good=…;qty=…` |
| `logistics.overflow` | (faction, sector, good) with delivery waste | sector id | that sector | `good=…;qty=…` |
| `logistics.short` | route whose departure was short | source sector id | source | `good=…;qty=…;reason=…[;lane=…]` (`qty` = demand not departed; `trade-surface` `trade-status` ask) |
| `logistics.route` | route whose policy fell back or whose goods were returned | source sector id | source | `good=…;detail=destination-lost` or `detail=returned;qty=…` |

`Audience` is always the faction. `lane.cut` fires only on the transition to `Stranded` — derived from
the packets' status at the start of the turn, never from a runtime memo — so it appears the turn a cut
bites and not on the turns after (those carry `logistics.strand`).

**Closed token sets** (each pinned by a test that names this reason: *a reviewed change adds a member*):

| Set | Members |
|---|---|
| Loss causes | `stranded`, `hazard`, `hostile-presence`, `perishability` (`lane-loss`) |
| Short reasons | `lane-capacity`, `no-path`, `contested`, `too-far`, `buffer-full` (`lane-flow`, `transit-buffer`). `no-path` includes *no reachable bank point* — the round-4 first throttle, answered by building a Counting House (`forecast-facts`) |
| Route details | `destination-lost`, `returned` (`auto-banking`, `transit-buffer`) |

**Widenings requested by other programs** (each lands in the owning program's change, as a reviewed
change to the pinned set): `rift-trade` `rift-facts` adds its rift report kinds and `crossing.*` short
reasons (`rift-trade-map.md` report vocabulary; `spec-crossing-leg.md`). No `trade.` prefix family is
added (`trade-surface-map.md` S1). *(Table repaired in the audit of 2026-09-20: this paragraph sat inside
the token-set table and cut the "Route details" row off it.)*

The map listed five bottleneck reasons including `destination full`; here "destination full" is not a
short reason — a full destination makes goods wait `AtDoor` and waste (`logistics.overflow`), it never
shortens a departure. `too-far` and `buffer-full` join from `transit-buffer`.

**Per-lane utilisation is not a report entry.** It would add an entry per busy lane per faction per turn
to a log the store persists. The flow lens reads it from `forecast-facts`' read model instead; the report
keeps the entries a player or a storylet acts on. (Deviation from the map's "per-lane per-turn flow
records"; see `spec-logistics-canonical.md`.)

### 2. Emission (L8)

The flow steps record events into runtime arrays as they happen (no allocation); L8 turns them into
entries in a fixed order — kinds in the table's order, then (faction, subject, good) ordinal — under the
phase name `Logistics`. Entry order is therefore a function of state.

### 3. Who reads them

- `trade-surface`: the status line — *banked N* from `banking-fact`'s entries; *lost M (main cause)* from
  `logistics.loss` (the cause with the largest quantity); *stuck K (worst bottleneck)* from
  `logistics.strand` plus the most frequent `logistics.short` reason.
- `npc-story-events` `failure-branches` and `quest-sources` read committed durable records other programs
  write (`docs/architecture/npc-story-events-map.md`, modules 14 and 23); `trade-stories` registers trade
  story kinds through `counterparties`' fact projection (umbrella §1a CM2). These entries are the source
  facts; this module writes no story row.

### 4. Numbers

`qty` tokens are `long` in invariant culture. Σ over `logistics.loss` qty per turn equals Σ applied loss
(reconciliation, asserted every turn).

## Tunables

None.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LogisticsFacts|FullyQualifiedName~World.TurnReportEntry"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs              MODIFIED — six kind constants
src/FusionRpg.Core/World/Logistics/LogisticsFacts.cs     (new) — token sets, L8 emission
tests/FusionRpg.Core.Tests/World/Logistics/LogisticsFactsTests.cs   (new)
```

## Testing strategy

- **Reconciliation:** over seeded runs, Σ reported loss = Σ applied loss per turn; Σ reported waste =
  Σ applied waste.
- **Exactly one:** every non-zero (faction, lane, good, cause) loss has exactly one entry.
- **Cuts:** a path cut produces `lane.cut` on the turn goods strand and not on later turns; a turn with no
  new strand has none.
- **Fog:** every entry has a non-null `Audience`; a projection for faction A contains no entry with
  audience B (the existing projection path, fed a two-faction logistics world).
- **Closed vocabularies:** the kind list and each token set are pinned with the reason in the test's
  own comment; no test counts entries.
- **Order:** the same state produces the same entry sequence, byte for byte.

Verification boundary: `FusionRpg.Core.Tests` (World/Turn, World/Logistics).

## Acceptance (contract)

1. Every non-zero loss in a turn has exactly one `logistics.loss` entry with one cause; Σ reported = Σ
   applied.
2. A cut produces `lane.cut` the turn it strands goods, and never on a turn with no new strand.
3. Every entry carries its faction as `Audience`; a faction's projection never contains another
   faction's logistics entry.
4. The kinds and each token set are closed vocabularies with a stated reason; no test counts entries.

## Hard edges

- **Ruleset / goldens:** entries appear only on **`trade.logisticsLanes`** worlds (round 6 C1:
  `logistics-flow` wave 2, one bump for the wave — landing order row 6); no existing report golden
  moves. Stored hot-tail reports gain the new kinds only for such worlds.
- **Deviation from the map:** no per-lane utilisation entries; one reason set member moved (see §1).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| The six kinds and three token sets | `trade-surface` `trade-lexicon` and status line; `trade-stories`; `npc-story-events` readers |
| Record arrays (pre-emission) | `forecast-facts` (the dry run reads the same records) |

## Boundaries

- **Always:** faction `Audience`; tokens from the closed sets; fixed emission order.
- **Ask first:** a new kind or token; per-lane utilisation in the report.
- **Never:** prose that carries a fact only a parser could extract; a banking or halt entry; a story row.

## Design-gate checklist

```
[x] Subsystems: turn report (kinds, fog scoping), logistics steps (records).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md. Gap: npc-story-events-map.md modules 14 and 23
    taken from the logistics-flow map's citation, not read this session.
[x] decisions.md: no lock on report kinds beyond the phase list.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: TurnReportEntry's fields and fog doc; the five existing kinds; hot-tail storage.
[x] Surrounding sections read: TurnReportEntry's class doc in full.
[x] Constraints tested, not assumed: none claimed.
[x] §2 invariants: none contradicted.
[x] Corrections propagated: reason-set change and dropped utilisation entries recorded here and in the
    session report.
[x] No population pinned: closed vocabularies only, each with a reason.
[x] Event-refreshed cache: none.
[x] Orderings: emission order is a function of state; tested.
[x] Actor magnitudes: none.
[x] No SOLID fork: the one report; no second log.
[x] Registry row: none owed (the vocabulary tests are ordinary contract tests).
```
