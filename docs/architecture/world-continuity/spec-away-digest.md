# Spec: `away-digest`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 13 of the
[world-continuity map](../world-continuity-map.md) (wave 4; depends on `coarse-step`, `world-fall`,
external notification-ssot `world-notify-source`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §5 ("a clear 'while you were away' report"),
§6.5 (losses reported as they happen, never a surprise wipe). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

"While you were away": every coarse record and every idle collect produces a **digest** — sectors lost
and gained, yields landed, warden fights, events resolved, turns credited versus elapsed — shown in the
turn report and sent as notification drafts. The digest is **derived from the stored record**, never
recomputed, and each fact appears once.

## Scope and non-goals

**In scope:** the digest's fact list and its derivation from a coarse record; the report entries; the
notification drafts handed to the notification seam; dedupe.

**Not in scope:** delivery, repeat windows and toasts (notification-ssot `notify-service`); the FE layer
(`multiverse-surface`); playback translation rows beyond the new prefixes (world-stage `world-playback`
gets the rows as an ask).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Turn report kinds: accepted, dropped, calendar, event, battle | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10` |
| The report is stored with the turn log row (entries + phases) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:663-681` |
| World-stage playback: one translation table for event prefixes | `docs/architecture/world-stage-map.md:82` |
| notification-ssot: a world-turn notification source seam and a pump with a per-world cursor, one batch per save | `docs/architecture/notification-ssot-map.md:126` (`notify-service`) |

### Real gap

No digest; no coarse record to derive one from until `coarse-step`; notification delivery is a draft map.

## Design

### 1. Facts — derived from the record, in record order

A coarse record's `TurnReport` (`coarse-step` §1 `CoarseResult.Digest`) already holds typed entries
under `TurnReportKinds.Event`. This module fixes their vocabulary (closed, prefixed like the shipped
event lines):

| Fact prefix | Emitted by | Carries |
|---|---|---|
| `away.credited` | `coarse-step` | `n` credited, turns elapsed (`hibernation-clock` §3 forfeit made visible) |
| `sector.lost` | `coarse-step` §5 | sector, turn, cause (`captured:<faction>` / `faded`) |
| `sector.gained` | `coarse-step` §5 | sector, turn (enemy lost ground to a third empire, or a neutral) |
| `yield.landed` | `coarse-step` §2 / `background-yield` | stock or located good, amount, sector |
| `warden.fought` | `world-warden` | frontier sector, loss chance applied, outcome |
| `storylet.resolved` | `world-event-budget` | storylet id, outcome |
| `world.won` / `world.fallen` | `world-victory` / `world-fall` | turn, sector |
| `rift.*` (departures, arrivals, crossing loss, suspension) | `rift-trade` `rift-facts` — folded in (answers `rift-trade-map.md` ask A3, round-4 reconciliation) | the entry as `rift-facts` defines it; `away-digest` adds no field and orders it by the same key |

`away-digest` is a **projection**: `AwayDigest.From(CoarseRecord)` reads those entries and orders them by
`(turn, prefix order above, sector id)`. It never re-runs `CoarseStep`, never reads the world graph, and
never reads the Hub.

### 2. Where it shows

- **Turn report:** the coarse row's stored report *is* the digest (`coarse-step` §4: a turn inside a
  coarse span returns the record's report). The world-stage playback table gains translation rows for the
  prefixes in §1 (an ask to `world-playback`, which owns the table and its golden).
- **Notifications:** one draft per fact with the dedupe key `(save, world, coarseRecordTurn, prefix,
  sector-or-subject)`, handed to the `IWorldTurnNotificationSource` seam. A coarse catch-up is not a live
  End Turn, so its drafts are **catch-up**, never a toast (notification-ssot map: catch-up never toasts,
  `notification-ssot-map.md:126`).

### 3. Dedupe and idempotency

The dedupe key is derived from the stored record's identity, so re-reading a record, replaying it, or a
retried catch-up never produces a second draft. A record is written once (its turn-log key), so the
digest is written once.

## Acceptance (contract)

1. Every sector lost, warden fight and storylet resolved in a coarse record appears **exactly once** in
   its digest, deduped on `(save, world, record, fact)`.
2. The digest is derived from the stored record: deleting nothing and re-running `AwayDigest.From` on the
   stored row gives a byte-identical digest; no world graph or Hub read occurs (asserted with the store
   and Hub seams absent).
3. Losses appear in capture order, before `world.fallen` when the record contains a fall.
4. `away.credited` always appears and states credited and elapsed turns.
5. Coarse drafts are catch-up, never live.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/AwayDigestTests.cs` (new): 1–4 over synthetic records.
- `gk-core/tests/FusionRpg.Server.Tests` (new `AwayDigestNotificationTests.cs`, once `notify-service` exists): 5.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
```

## Hard edges

- **`rpg_worlds` schema:** none.
- **Replay:** none — a projection of stored rows.
- **Corpse-cache tick key:** none.

## Dependencies

`coarse-step`, `world-fall`, `world-victory`, `idle-world`, `world-warden`, `background-yield`,
`world-event-budget` (fact producers); external notification-ssot `world-notify-source`/`notify-service`
(delivery), world-stage `world-playback` (translation rows). Consumed by `multiverse-surface`.

## Boundaries

- **Always:** derive from the record; one fact once.
- **Ask first:** a digest fact that needs a live read.
- **Never:** recomputing a coarse step to build a digest; a toast for a catch-up.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `AwayDigest.From(record)` and the fact prefixes | `multiverse-surface`, `world-playback`, notifications |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn report, turn log, notifications (external), playback (external).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: notification-ssot-map.md row 126; world-stage-map.md row 82; see
    spec-world-state-vocabulary.md.
[x] decisions.md checked: none.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: TurnReport kinds, log insert.
[x] Surrounding sections read.
[ ] Constraint tested: none run.
[x] No §2 invariant contradicted.
[x] Corrections propagated.
[x] No population pinned; the fact-prefix list is a closed vocabulary owned here.
[x] Cache: none; the digest is derived per read and deduped by stored identity.
[x] Ordering: capture order is the contract, not an accident.
[x] No actor magnitude.
[x] No SOLID fork: one projection.
[x] No new cross-cutting rule.
```
