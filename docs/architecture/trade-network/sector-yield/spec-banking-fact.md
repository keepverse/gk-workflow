# Spec: `banking-fact`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.9 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Cross-map decisions **CM3** (the AI treasury is `counterparties` `empire-treasury`'s;
round 5 **X3**: `empire-treasury` is its writer, registered into this module's hand-off point, the
destination seam of §2) and **CM4** (this module creates the `Logistics` phase slot; `logistics-flow`
extends it): [../../trade-network-map.md](../../trade-network-map.md) §1a. Ideal:
[../../trade-network-ideal.md](../../trade-network-ideal.md) §8.6 (*"a ledger fact … takes the goods off
the map into the unlocated wallet"*), §8.7, §10 C1–C2, §14b. Economy rules P13–P14.
**Round 4** ([../decisions-round-4.md](../decisions-round-4.md) §B, Q2): the bank point is the Counting
House building; its tiers (Counting House → Treasury → Vault) set a **banking rate** ("faster banking" at
T2+) and unlock a **per-good hold** at T2 (Treasury).
**Round 5** (R5-A A3, A4; X3, X13, X15): "faster banking" is a **per-turn banking rate that grows with the
bank tier, scaled like goods, never a cap** (A3); the hold's default is *"keep enough to fill **other
traders' open buy orders at this hub**"* (A4, which replaces round 4's "what open sell orders need"); the
banking tier is read through `sector-features` only (X13).

## Objective

Goods that sit in a bank point's warehouse **leave the map** as a ledger fact. Inside `Step` the stock
is decremented and a banking fact is recorded; in the turn commit, a human empire's fact credits its
wallet through the P14 ledgers. The wallet has no location, so losing any sector — the capital
included — never hands a banked good to anyone (ideal §3 principle 9; §10 C2). An AI empire's fact
credits its per-world treasury, which `counterparties` owns.

This module also creates the **`Logistics` phase** (after `Production`, before `Growth`), with banking
as its only step, on worlds whose stamp grants `trade.bankingPhase` (the step itself gates on `trade.banking` — §1a).

## Scope and non-goals

**In scope:** the phase slot; the banking step with its per-tier rate and the per-good hold; the hold
state and its hold-source seam; the banking-destination seam; the fact and its commit-time credit; the
reconciliation; the `decisions.md` phase-order amendment.

**Not in scope:** flow toward bank points, lane loss, deliveries, the `route-set`/`route-clear` policy
commands (`logistics-flow`, which adds its steps around banking in the same phase — the fixed step order of `logistics-flow` `logistics-phase` §1 (banking is L3: refresh, arrivals and fleet load/unload before it; delivery overflow, rift departures, flow, loss, refine and facts after it — round 5 X5)); the `bank-hold` policy
command (`logistics-flow` `auto-banking`, which owns the banking policy commands); open buy orders
(`exchange` `order-book`, which registers a hold source); the treasury's field, balance rules and sinks
(`counterparties` `empire-treasury`, which registers the AI destination; `empire-goods-sinks`); any notice
or panel (`trade-surface`).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| Ten phases, executed in order in `Step`; `Production` then `Growth` | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:127-157` (names), `:191-206` (calls) |
| The phase list is a locked decision and a spelled-out test | `docs/architecture/decisions.md:7`; `gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs:107` |
| A phase appears in the report only if it begins | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:44-45`, `:90` |
| `TurnResult` carries world, report and hash | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:8` |
| The commit: `Step`, then the diff, then post-step passes, then the log, all in one transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601-676` (the diff at `:605`) |
| Report replay re-runs `Step` only to rebuild a report; it writes nothing | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:759-773` |
| The soul ledger's append verb with a dedupe key | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-147` |
| The soul reason vocabulary (closed constants) | `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:49-83` |
| Materials are written by player id, with no ledger | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:182-193` |
| Faction kinds | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18` |

### Wiring gap

None in this module's own code path. (The materials ledger is `trade-foundation` `material-ledger`'s.)

### Real gap

No code banks sector goods (ideal §10 C1). No `Logistics` phase exists.

## Design

### 1. The phase slot

`TurnEngine.Phases.Logistics = "Logistics"`, called between `Production` and `Growth`
(`TurnEngine.cs:196-197`). **The phase begins, and appears in the report, only when the world's stamp
grants `trade.bankingPhase`.** On a legacy stamp nothing runs and `report.Phases` is exactly today's ten,
so every stored `phases_json` and every golden stays as it is. **The gate is the per-world stamp**
(`trade-foundation` `world-stamp`), and the capability row that gate reads is born with a `RulesetVersion`
bump in this change (`spec-world-stamp.md` §2, "The bump is mandatory"): `trade.bankingPhase`'s
`IntroducedAtRuleset` is the new, bumped value, so no world stamped before this change is granted it.
*(Corrected in the audit of 2026-09-20: this paragraph said "`RulesetVersion` is not bumped". Without the
bump, the capability would sit at the current ruleset and every world already stamped at it — created
before banking existed — would gain banking mid-life, the D-C breach the stamp exists to prevent.)* The
bump changes no legacy world's hash; its one cost is that trimmed turn reports logged before it are no
longer re-derived, the cost every earlier bump paid.

### 1a. This module lands in two waves (round 6 C1 + C3)

Round 6 C1 makes the **wave** the unit of a flag and a bump, and round 6 C3 makes the banking of goods
wait for the save-identity re-key. Those two rulings together split this module's landing in two — a wave
split inside one owner, **not** a second owner of the phase (CM4 is unchanged, and no other module may
create the slot):

| Half | What lands | Flag | Landing-order row |
|---|---|---|---|
| **Slot** (§1) | `TurnEngine.Phases.Logistics`, the report phase, the `decisions.md:7` amendment. L3 is present and **empty** | `trade.bankingPhase` | 4 — needs no ledger |
| **Step** (§2 onward) | the L3 banking step, the per-tier rate, the per-good hold and its seam, the destination seam, the fact, the commit-time credit, the reconciliation | `trade.banking` | 8 — **after** `material-ledger`, which is after `save-identity` SE4.12 → SE4.38 |

Why the split rather than waiting as a whole: `logistics-flow` extends the phase this module creates
(CM4), so a single landing would put every logistics wave behind the save-identity re-key as well. The slot
has no ledger dependency — it is a phase name, a report phase and a `decisions.md` row — and round 6 C3
defers *"`material-ledger` and the banking work that needs it"*, which the slot is not.

**Interim behaviour between the two halves, stated so no consumer has to guess it.** The phase exists and
`logistics-flow` runs its steps around an empty L3: goods flow to the nearest bank point and **stay
there**. No banking fact is written, no wallet and no treasury is credited, and `economy-report` prints a
banked total of zero **with that reason**, never a silent zero. `bank-points` still answers, so the
first-throttle answer (*build a Counting House*) is buildable, visible in `forecast-facts`, and does raise
the tier the step half will read when it lands. The family is not shippable in this state, and
[../landing-order.md](../landing-order.md) §7 says so in one place.

The `decisions.md` phase-order row (`:7`) is amended **in this change**: the list becomes eleven phases,
with `Logistics` stamp-gated, and the row says so.

### 2. Who banks, and into what — the destination seam

Banking hands each fact to a **banking destination** through a seam this module owns and
`counterparties` extends (its ask A11; umbrella CM3 — the treasury's field is `counterparties`'):

```csharp
public interface IBankingDestination
{
    bool Accepts(WorldFaction owner);
    WorldState Land(WorldState world, BankingFact fact, StockDeltaRecorder deltas);  // inside Step
}
```

| Kind | Destination | Registered by |
|---|---|---|
| `Player` | The save's wallet: nothing moves inside `Step`; the fact is credited at commit (§4) | this module (built in) |
| `Zomboss`, `Rival` | The empire's per-world treasury, moved inside `Step` (P13) | `counterparties` `empire-treasury` |
| `Clan`, `Wild` | None — no destination accepts them, so their goods are never banked and stay for trade | — |

Destinations are ordered by a declared, stable id (ordinal), never by registration time — the host may
register them in any order and the result is the same; the first that `Accepts` lands the fact, and two
destinations that both accept one faction kind are a registration error at startup. A faction no destination accepts
banks nothing (its goods stay in the warehouse). This module writes no treasury field. Until
`empire-treasury` registers its destination, AI bank points hold their goods — a declared, temporary AI
handicap removed when it lands, and no longer a module-order dependency (the map's §5a D3 consequence is
retired by the seam).

### 3. The banking step (inside `Step`)

For each banking faction in ordinal id order, for each sector in `BankPoints.For(world, faction)` (its
banking tier `t = BankPoints.TierAt(sector)` is at least 1):

1. **Bankable quantity per good.** For each entry of the sector's `LocatedStock` in ordinal id order
   whose good `LocatedGoodCatalog.Banks`: `bankable = max(0, qty − hold(sector, good))`; the hold applies
   only at `t ≥ 2` (§3a) and is 0 at tier 1.
2. **The tier's rate.** `rate = LocatedScale.Apply(banking.rateAtTier(t), LocatedScale.Milli(sector, power))`
   — units of located goods per turn (one unit per good, the warehouse's unit, `spec-warehouse-axis.md`
   §4), scaled by the same read as the goods and the warehouse (umbrella invariant 7;
   `essence-loop-read`). **R5-A A3: a rate, never a cap.** It meters how fast goods leave the map; it never
   refuses or destroys a good — what does not bank this turn stays in the warehouse and banks on a later
   turn — and it grows with the bank tier, with the content scale, and **with the number of bank points a
   faction builds** (each Counting House banks its own rate; there is no ceiling on how many a faction
   holds), so it is not a progression ceiling. The code comment says so (a per-turn rate is a structural
   limit, CLAUDE.md caps rule). `t` is the sector's active banking tier (`BankPoints.TierAt`, through
   `sector-features`' `ActiveTier`): a Counting House mid-upgrade banks at its current tier.
3. **Split.** If `Σ bankable ≤ rate`, every good banks its whole bankable quantity. Otherwise `rate` is
   split pro rata by `bankable`, the remainder one unit each in ordinal id order — the rule
   `production-halt` uses (`spec-production-halt.md` §Design 1) — so no good is starved.
4. For each good with a non-zero banked amount: `LocatedStockOps.Add(sector, good, −banked, "bank",
   deltas)`; record `BankingFact(OwnerFactionId, SectorId, GoodId, Qty)` on `TurnResult.BankingFacts` (in
   the order produced); hand it to the owner's destination (§2).

What does not bank stays in the warehouse and banks on a later turn. Legion pieces (`BankedId = null`)
never bank. Goods produced at a bank point this turn bank this turn (`Production` runs first), up to the
rate.

### 3a. The per-good hold (Treasury tier and above)

`hold(sector, good) = max(policyHold(sector, good), Σ registered hold sources(sector, good))`, applied
only when the sector's banking tier is at least 2. **Round 5's default (A4, X15)** — *"keep enough to fill
other traders' open buy orders at this hub"* — is the source term: `exchange` `order-book` registers an
`IBankingHoldSource` returning, per (sector, good), the quantity still open on **buy** orders at the hub in
this sector placed by factions **other than the sector's owner** (the owner's own buy orders never hold its
own stock back). This replaces round 4's "what open sell orders need"; the seam is unchanged (E-A11 asked
for a hold source, and only its quantity rule moves). Until `exchange` lands, the source list is empty and
only policy holds apply.

- **State.** `WorldSector.BankHolds` — sparse, hashed `(GoodId, Qty : long, SetByFactionId)` entries;
  canonical row `sector-bank-hold|<sectorId>|<packed>` written only when non-empty (every existing world
  hashes as today); persisted as one packed column beside `located_goods` (`spec-located-stock.md` §4).
  Written only through `BankingHolds.Set(sector, good, qty, setBy)`; `Qty = 0` removes the entry.
- **Who sets it.** The `bank-hold` policy command, owned by `logistics-flow` `auto-banking` (which owns the
  banking policy commands, map §2.9), filed the same way by the player and by `trade-ai` for an AI owner.
  A hold survives a tier drop but is not applied below tier 2. **A policy hold belongs to its commander,
  not to the ground:** an entry applies only while its `SetByFactionId` owns the sector, so a capture makes
  it inert the same turn with no write in the phase that changes the owner, and a retake revives it — the
  rule `auto-banking` gives route policies (`logistics-flow/spec-auto-banking.md` §3). A new owner's
  `bank-hold` on the same good replaces the entry. *(Refined in the audit of 2026-09-20: "capture clears
  the holds" needed a write inside `ClaimResolver` and `LoamPhases`, other programs' phases, and had no
  order-independence criterion.)*
- A hold never moves goods; it only lowers what banks this turn.

### 4. The commit (Data)

In the commit transaction, after the diff (`RpgStore.WorldTurns.cs:605`) and before the log insert:

- For each fact whose destination is the player's (§2): credit the wallet of the world's save
  (`header.PlayerId`), keyed by `trade-foundation` `ledger-keys`:
  `(save_id, owner, world_id, turn, "bank", sector, good)`.
  - A material good: through `material-ledger`'s verb, and nothing else — an **account** fact with
    factKind `grant`, `sourceKind` `world-bank` and `sourceId` = the world `bank` key above
    (`spec-ledger-keys.md` §4a; `spec-material-ledger.md` §3). *(Added in the audit of 2026-09-20: the
    material ledger's account grammar had no source for a banking credit.)*
  - `souls`: `AppendSoulLedgerUnlocked(..., delta: qty, reason: "world-bank", refKind: "world_fact",
    refId: key, dedupeKey: key, ...)`. `world-bank` is a new member of `SoulEarnPolicy.Reasons`, a
    closed vocabulary the creature program owns; it is added in this change with that program's
    agreement (a faucet reason, P1: its sinks are the wallet's existing sinks).
- `world-stock-ledger` writes the `bank` deltas like any other.
- The report replay path (`:759-773`) credits nothing: it rebuilds reports only.

**Idempotence.** Re-committing the same `(world, turn)` re-derives the same keys; `INSERT OR IGNORE`
(souls) and the material ledger's dedupe credit once.

### 5. Capture and the unlocated wallet

A banked good is no longer on the map. Capturing a sector after a banking fact changes no wallet and
no treasury; capturing a bank point before banking takes what is still in its warehouse, because the
stock is on the sector.

### 6. Declared, not hidden

Until `counterparties` `empire-goods-sinks` lands, an AI treasury has no reader: nothing spends it, so it
cannot unbalance play, and the economy report prints it as monotone positive with that module named as
the follow-up. A world has no bank point until a Counting House stands (round 4 §B); every empire's seat
starts with a tier-1 Counting House (R5-A A1, placed by `world-continuity` world creation and
`counterparties` `empire-roster`), so each empire banks at home from turn 1. The rule is the same for every
faction.

## Tunables

| Key | Unit | Home | Meaning |
|---|---|---|---|
| `banking.ratePerTurnByTier` | units of located goods per turn at the pin, one entry per banking tier in tier order (entry *k* = tier *k*, 1..3; read through `rateAtTier(t)`) | `data/tuning/trade.v{n}.json` | How much one bank point banks per turn; strictly rises with the tier. Scaled by `LocatedScale` (PS-5). A missing tier entry, or more entries than the banking feature's maximum tier, is a load rejection |

Values are decided by principle (tier 1 banks at least one tier-1 storage building's capacity per turn,
so a lone Counting House never binds before storage does; each tier strictly raises it) and published;
they are not owner questions.

## Numeric types

Quantities `long`, `checked`; the pro-rata split widens before the multiply and divides once; the rate
is scaled once through `ContentScale.Apply`. The soul ledger's `delta` is already `long`
(`RpgStore.Souls.cs:140`).

## Acceptance (contract)

1. **Legacy:** on a legacy stamp the `Logistics` phase does not begin, `report.Phases` equals today's ten,
   and the state hash matches today turn for turn.
2. **Stamped phase order:** on a `trade.bankingPhase` stamp the report's phases are the eleven, with
   `Logistics` between `Production` and `Growth` (a new test beside `TurnEngineTests.cs:107`).
3. **Reconciliation:** for every good and turn, Σ warehouse decrements with factKind `bank` =
   Σ wallet credits + Σ destination credits.
4. **Idempotence:** committing the same turn twice credits the wallet once (souls and materials).
5. **Never loam:** no banking fact names `loam`, `rubble`, `ironwork`, `recruit` or a legion piece
   (closed-enum membership against `LocatedGoodCatalog`).
6. **Unlocated wallet:** capturing any sector, the capital included, after a banking fact leaves the
   wallet and every treasury unchanged; the same capture in the same turn as banking, in either filing
   order, resolves identically (order-independent, both tested).
7. **Destinations:** a `Player` fact credits the wallet; a faction no registered destination accepts
   banks nothing and keeps its goods; every `WorldFactionKind` member is covered by §2's table (the
   five-member domain pinned with its reason).
8. **Replay writes nothing:** the report replay path leaves every ledger unchanged.
9. The `decisions.md` phase-order row names `Logistics` and its stamp gate in the same change.
10. **Rate:** a bank point banks at most its tier's scaled rate per turn; raising the tier never lowers
    what banks; the split sums to exactly `min(rate, Σ bankable)` with the remainder by ordinal id.
11. **Hold:** at tier ≥ 2 banking never takes a good's stock below its hold; at tier 1 holds do not apply;
    a hold of 0 behaves exactly like no hold; with no hold source registered the source term is 0; a
    world with no holds hashes as today.
12. **A captured hold is inert, order-independent:** a sector captured in the same turn its owner files
    `bank-hold` banks next turn as if it had no policy hold, whichever the fixture resolves first (both
    orders tested); the captor's own `bank-hold` replaces the entry and applies; a retake by the setter
    revives its hold. No phase outside `BankingHolds` writes `BankHolds`.
13. **Destinations are order-free:** registering the destinations in either order lands every fact in the
    same place; two destinations accepting one faction kind fail at startup.
14. **Ruleset (two waves, round 6 C1):** `trade.bankingPhase`'s `IntroducedAtRuleset` is the value the
    slot change bumps `TurnEngine.RulesetVersion` to, and `trade.banking`'s is the value the step change
    bumps it to (§1a). A world stamped at the previous ruleset is granted neither
    (`spec-world-stamp.md` acceptance 11). A world granted `trade.bankingPhase` but not `trade.banking`
    runs the phase with an empty L3 and banks nothing — asserted in both directions.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Goods/BankingStepTests.cs` (new): items 1–3, 5–7.
- `tests/FusionRpg.Data.Tests/World/BankingCommitTests.cs` (new, in-memory store): items 3–4, 6, 8.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs',
  'src/FusionRpg.Core/World/Goods/BankingStep.cs',
  'gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/BankingStepTests.cs',
  'tests/FusionRpg.Data.Tests/World/BankingCommitTests.cs') -Session <active-session-id>
python gk-core/scripts/guard-dal.py
```

This module crosses Core and Data and changes the phase list: the full suite runs once at module end
(AGENTS.md "Verification boundary", point 2). Goldens are triaged under `decisions.md` *Golden ordering
across streams*; none is re-blessed to pass. Acceptance 1 says none should move.

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs            MODIFIED — Phases.Logistics; stamp-gated call; TurnResult.BankingFacts
src/FusionRpg.Core/World/Goods/BankingStep.cs          (new) — step, rate split, destination seam
src/FusionRpg.Core/World/Goods/BankingHolds.cs         (new) — hold state, hold-source seam
gk-core/src/FusionRpg.Core/World/WorldState.cs                 MODIFIED — WorldSector.BankHolds
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs             MODIFIED — conditional sector-bank-hold row
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs            MODIFIED — bank_holds column (write, load)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs   MODIFIED — equality, upsert
gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs         MODIFIED — Reasons.WorldBank (creature program's vocabulary)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs       MODIFIED — commit-time wallet credit
docs/architecture/decisions.md                         MODIFIED — phase-order row
tests/FusionRpg.Core.Tests/World/Goods/BankingStepTests.cs      (new)
tests/FusionRpg.Data.Tests/World/BankingCommitTests.cs          (new)
```

## Boundaries and hard edges

- **Always:** bank inside `Step`, credit in the same commit transaction; one key grammar; the whole
  phase gated by the stamp.
- **Ask first:** banking anywhere but a bank point; any rule that removes a good instead of deferring it.
- **Never:** write materials outside `material-ledger`'s verb; gate this phase on the global
  `RulesetVersion` instead of the stamp; register its capability at the current ruleset without a bump;
  credit on the replay path; hold banked goods in any sector field.
- **Hard edge — phase list and ruleset.** Adding a phase changes the ruleset (`decisions.md:7`); it is
  stamp-gated, the row is amended in the same change, and `RulesetVersion` is bumped once for the
  capability row (`spec-world-stamp.md` §2).
- **Hard edge — module order across sub-programs (retired, round 4).** The first draft needed
  `counterparties` `empire-treasury` before this module (CM3). The destination seam (§2) inverts it:
  `counterparties` registers into this module, so no arrow points back up the build order.

## Dependencies and interface

**Depends on:** `bank-points`, `located-stock`, `essence-loop-read` (the rate's scale); `trade-foundation`
`world-stamp`, `ledger-keys`, `stock-deltas`, `world-stock-ledger`, `material-ledger`, `sector-features`.
Nothing from a later sub-program.

**Round 6 C3 — the step half waits for save identity.** `material-ledger` waits on `save-identity` SE4.12 →
SE4.38 (`tasks/solid-enforcement-todo.md:352`, `:634`, both unchecked), and the owner's ruling is *"Wait …
`material-ledger` and the banking work that needs it start after it finishes"*
([../decisions-round-4.md](../decisions-round-4.md) Round 6 C3). The step half (§1a) is exactly that
banking work: it credits materials and may credit them **no other way**. The slot half does not depend on
the ledger and lands first, which is what keeps `logistics-flow` off the critical path. Ask X-1 of the
global audit reports the schedule need to the solid-enforcement lane; nothing here works around it, and the
audit's option (b) — land on today's Tier B `player_id` key and re-point the writer sites later — is not
taken.

| Exposed | Consumer |
|---|---|
| `TurnEngine.Phases.Logistics` and its stamp gate | `logistics-flow` `logistics-phase` (adds its steps around banking; banking is L3 of its canonical order, X5) |
| `TurnResult.BankingFacts` | `trade-surface` (status line: *banked N*), `trade-foundation` `economy-report`, `trade-ai` (`ai-spend-limit` income) |
| The banking step (L3 in `logistics-phase`'s order) | `logistics-flow` `auto-banking` (arrivals bank the same turn, up to the rate) |
| `IBankingDestination` | `counterparties` `empire-treasury` (registers the AI treasury) |
| `IBankingHoldSource` | `exchange` `order-book` (other traders' open buy orders at this hub — the R5-A A4 default hold) |
| `BankingHolds.Set` | `logistics-flow` `auto-banking` (`bank-hold` resolver) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (a new phase), economy (P13/P14 ledgers), soul ledger, materials,
    the world store.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: trade-network-ideal §8.6-§8.7, §10, §14b; umbrella §1a (CM3, CM4), §5;
    trade-foundation-map §2.4-§2.8; counterparties-map modules 4 and 10; logistics-flow-map modules 1
    and 7; economy-principles P13-P14.
[x] decisions.md: phase-order row (:7) — amended in this module's change; registry row (:108).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: the phase list and its test, the commit order, the replay path, the soul
    append verb, the reason constants, the faction kinds.
[x] Surrounding sections read: the commit's cargo/debit comments; the RulesetVersion history note.
[x] Constraints tested, not assumed: "no golden moves on a legacy stamp" is acceptance 1, to be proven by
    the full suite at module end.
[x] No §2 invariant contradicted: SQL only in Data; long; P13 (banking inside Step); P14 (keyed ledger).
[x] Corrections propagated: CM3/CM4 applied; the cross-sub-program order is stated as a hard edge and in
    the session report.
[x] No population pinned; the five-member faction-kind map is a closed enum with its reason.
[x] No event-refreshed cache.
[x] Ordering: capture vs banking in the same turn is order-independent (acceptance 6).
[x] No actor magnitude.
[x] No SOLID fork: one phase, one key grammar, one materials writer; destinations and hold sources are
    registered seams, never a second banking path.
[x] Round 4 applied (2026-09-19): Counting House tiers set the rate and gate the hold; the destination
    seam answers counterparties A11; the hold-source seam answers exchange E-A11.
[x] Round 5 applied (2026-09-20): A3 rate-not-cap wording; A4/X15 hold default = other traders' open
    buy orders at this hub; X3 empire-treasury writes through the destination seam; A1 seat start kit;
    TurnEngine/WorldTurns citations re-verified.
[x] Registry row: "materials only through material-ledger" is trade-foundation's guard; this module adds
    none.
```
