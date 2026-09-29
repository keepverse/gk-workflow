# Spec: `rift-facts`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19). Module 8 of `rift-trade`, wave 3. Every `file:line` below was opened this session.
Docs only. **House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Every departure, arrival, loss, return, strand and suspension is written, once, as a fact in the report of the
world where it happened — readable by the player, invisible to every other faction, and folded into the *"while
you were away"* digest when it happened in a sleeping world. The kinds extend `logistics-flow`'s closed report
vocabulary, so `trade-surface`'s status line reads cross-world flow the way it reads lane flow.

## Scope and non-goals

**In scope:** the rift report kinds and their token sets; which existing logistics kinds are reused; audience and
sector scoping; reconciliation with the crossing ledger; the digest lines for coarse and idle records.

**Not in scope:** the digest itself and notification delivery (`world-continuity` `away-digest`; notification
program); translation of tokens into player text (`trade-surface` `trade-lexicon`); storylets reacting to the facts
(`trade-stories`).

## Locked anchors

- **The report is the engine's log:** the engine writes nowhere else (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-35`).
- **Fog is per faction:** every entry carries an `Audience`; a projection for faction A never shows an entry for
  faction B (`logistics-flow` `logistics-facts`).
- **One vocabulary:** loss and delivery-waste reuse `logistics.loss` and `logistics.overflow`; nothing is
  duplicated.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The report kinds are a short closed list | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10` |
| An entry carries phase, kind, subject, detail, sector and audience | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:30-31` |
| A committed report is stored with the turn and re-derivable by replay | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:667-678`, `:769-775` |

### Wiring gap

None.

### Real gap

The rift kinds and their token sets; digest lines for sleeping resolutions.

## Design

### 1. Kinds

New kinds (closed, added to `TurnReportKinds` by a reviewed change):

| Kind | Written by | Subject | Detail tokens |
|---|---|---|---|
| `rift.depart` | Source resolution (`crossing-handoff`, `sleeping-endpoint`) | `rift:<routeId>` | good, departed, carried, arrive counter, far world id |
| `rift.arrive` | Destination resolution | `rift:<routeId>` | good, arrived, queued, leg (`out`/`return`) |
| `rift.suspend` | Source resolution (`endpoint-loss`) | `rift:<routeId>` | reason from `endpoint-loss`'s closed set |
| `rift.return` | Destination resolution that refuses (`endpoint-loss`) | `rift:<routeId>` | good, refused quantity, reason |
| `rift.strand` | Origin resolution that cannot take a return | `rift:<routeId>` | good, balance |

Reused kinds: `logistics.loss` (crossing loss with cause `hazard` or `perishability`; strand loss with cause
`stranded`), `logistics.overflow` (a delivery wasted at a full warehouse). A short arrival carries one bottleneck
reason from `crossing-leg`'s set (`crossing.near-capacity`, `crossing.far-capacity`, `crossing.no-stock`).

### 2. Scoping

- `Audience` = the world's `Player`-kind faction id. Routes are the player's; no other faction ever receives an
  entry.
- `SectorId` = the **own** anchor sector in this world.
- The detail names the far **world** id and the route id, never a sector id of the other world.

### 3. Sleeping resolutions

A `CoarseStep` or idle resolution writes the same kinds into its own record (the coarse record or the idle record
`world-continuity` defines), not into a full-step report. `away-digest` folds them into the *"while you were away"*
summary for that world (ask A3), in resolution order, deduped on `(save, world, record, fact)` as that module
already specifies.

### 4. Reconciliation with the ledger

For each good and resolution counter, the reported quantities equal the crossing-ledger events of the same
resolution: `Σ rift.depart.departed = Σ depart`, `Σ logistics.loss (rift subjects) = Σ loss + Σ strand-lost`,
`Σ rift.arrive.arrived = Σ arrive`, `Σ logistics.overflow (rift subjects) = Σ waste`, `Σ rift.return = Σ refuse`.

## Tunables

None.

## Numeric types

Quantities rendered from `long`; no arithmetic here.

## Contract-level acceptance

1. Every departure, arrival, loss, return, strand and suspension produces exactly one entry in the world (or
   sleeping record) where it happened, and none elsewhere.
2. Reconciliation (Design 4) holds per good and counter over a scripted two-world run.
3. Every entry has a non-null `Audience` equal to the world's player faction; a projection for any other faction
   contains no rift entry (fog test).
4. No entry's detail contains a sector id of the other world.
5. The rift kind list and each token set are pinned as closed vocabularies with a comment saying why; no test counts
   entries.
6. A coarse record with rift activity yields digest lines through `away-digest`, once each.

## Test plan and verification boundary

| Test | Project |
|---|---|
| Kinds, scoping, fog, reconciliation against a fixture ledger | `gk-core/tests/FusionRpg.Core.Tests` (World/Turn, World/Logistics/Rift) |
| Reconciliation over a committed two-world run | `gk-core/tests/FusionRpg.Data.Tests` |
| Digest lines | `gk-core/tests/FusionRpg.Server.Tests` (with `away-digest`) |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
```

## Hard edges

- **Always:** write facts from inside the resolution that caused them; reuse logistics kinds for loss and waste.
- **Ask first:** showing a rift fact to any faction other than the route's owner.
- **Never:** a second loss or overflow kind; a Data-side report write outside a resolution; a far-world sector id in
  a detail.

## Dependencies

| Consumes | From |
|---|---|
| `logistics.loss`, `logistics.overflow`, their cause sets | `logistics-flow` `logistics-facts` |
| Typed rift outcomes | `crossing-handoff`, `sleeping-endpoint`, `endpoint-loss` |
| Digest folding | `world-continuity` `away-digest` (ask A3) |

| Exposes | To |
|---|---|
| The rift kinds and token sets | `trade-surface` (`trade-lexicon`, status line), `trade-stories`, `away-digest` |

## Files

```
gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs               MODIFIED — five kinds
src/FusionRpg.Core/World/Logistics/Rift/RiftFacts.cs      NEW — entry builders, token sets
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn report, fog/intel projection, digest.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: as spec-rift-route.md; logistics-flow logistics-facts; world-continuity
    away-digest.
[x] decisions.md: no lock on report kinds.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: the kind list and the entry record.
[x] Read surrounding sections: TurnReport's class comment.
[x] Constraints tested: none claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none needed.
[x] No population count pinned: closed kind and token sets only.
[x] Event-refreshed cache: none.
[x] Orderings: digest lines in resolution order, deduped; no order-dependent criterion.
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: logistics kinds reused.
[ ] Registry row: the fog test is a test; an invariants row lands with it.
```

## Audit 2026-09-20

Checked and clean: the rift report kinds widen `logistics-facts`' closed kind list by a reviewed change (as that
spec's *Widenings requested by other programs* row records); loss and waste reuse `logistics.loss` and
`logistics.overflow`; every entry carries an `Audience` and never names a far-world sector; reconciliation with
the ledger is asserted per good and counter, never as a count. Consistency note: `fleet`'s caravan and cache facts
are `TurnReportKinds.Event` detail tokens (`FleetFacts`), while logistics and rift facts are report kinds; both
are closed vocabularies with one owner each, and `trade-surface` `trade-lexicon` reads both.
**Verification boundary:** the `core-world-logistics-rift` owner boundary (`spec-crossing-anchor.md`
*Audit 2026-09-20*); the digest test is Server-side.
