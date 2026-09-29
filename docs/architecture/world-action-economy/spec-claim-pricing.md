# Spec: `claim-pricing`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `claim-pricing`, row 4 of the
[world-action-economy map](../world-action-economy-map.md) (wave 2; depends on `budget-debit`).
Ideals: [world-action-economy-ideal.md](../world-action-economy-ideal.md) Locked constraints
§3 (deposit pipe) + §4 (precedence + idempotency mapping). Dependencies consumed exactly:
[spec-budget-debit.md](spec-budget-debit.md) IN FULL (debit-after-refill locked; attempt-pays /
refusal-free precedence; replay-once-per-`CommandId`; `RulesetVersion` 11 → 12);
[spec-act-price-table.md](spec-act-price-table.md) (key names, per-mille units, provisional values);
[../empire-inventory-surfaces/spec-cargo-commands.md](../empire-inventory-surfaces/spec-cargo-commands.md)
(`claim-cache` converged kind + five sibling kinds + post-Step pass + `correlationId :=
CommandId`); [../empire-inventory-surfaces/spec-claim-endpoints.md](../empire-inventory-surfaces/spec-claim-endpoints.md)
§Design 3 (`correlationId := CommandId` end to end, with evidence — converged, §Design 4).
House style: `spec-legion-cargo.md`.

## Objective

`budget-debit` built the spend — one seam (`DebitActCostUnlocked`) that subtracts a table cost
from the post-refill budget, refuses `entity.spent` when short, charges an attempt once, and
debits once per `CommandId`. But nothing routes the priced verbs through it yet: the six
cargo/cache kinds exist only in `spec-cargo-commands.md` §Design 1 (zero of them in
`WorldCommand.cs:83-84`, verified this session), and the debit seam exists only in that same
spec's §Design 6 as an accept-always stub (zero hits for `DebitActCostUnlocked` under `src/`,
verified this session). This module wires the priced verbs onto the spend: claim-cache,
deposit-cargo, withdraw-cargo, load-cargo, unload-cargo each resolve their cost key, call the
seam at the locked site, and inherit the locked precedence — without re-deciding the order, the
refusal shape, the version bump, or any number.

Success looks like: a filed `claim-cache` that reaches its per-row loop leaves the legion's
next-turn `MovementRemaining` exactly `claimCostMilli` lower than the refill wrote, and the
left-behind rows it skipped decay in the same commit; a `cache.unreachable` claim leaves the
budget untouched and retries free next turn; a re-committed `CommandId` returns the recorded
`cache.claimed:<c>+<s>` detail with no second subtract; an old log with none of the six kinds
replays `StateHash`-identical on version 11.

## Locked anchors

- **Debit-after-refill is locked and already implemented by `budget-debit` — this module calls
  the seam, never the budget.** The cargo pass runs Data-side post-Step post-Diff where the DB
  row already holds the refilled next-turn budget (`TurnEngine.cs:405-423`, read this session).
  This spec adds no budget read, no second gate, no reservation — one call per priced command
  at the §Design 2 site, inside the same per-command scope `budget-debit` §Design 2 owns.
- **Attempt-pays / refusal-free precedence is locked (budget-debit §Design 4, converging
  ideal §4).** Whole-act refusal (`entity.gone`, `entity.routed`, `cache.unreachable`) returns
  before the seam — free retry. An attempt that reaches the per-row claim loop charges once
  (250 provisional) even at `claimed:0+N` — left-behind rows decay same turn, pay-for-nothing
  by construction. Deposit/withdraw/load/unload are whole-act: gate-fail refuses with no
  charge, gate-pass charges once before the move.
- **Replay-once-per-`CommandId` is locked and CONVERGENT with `claim-endpoints`.**
  `spec-cargo-commands.md` §Design 4 locks `correlationId := CommandId`; `spec-claim-endpoints.md`
  §Design 3 re-derives the same mapping end to end with evidence (submit idempotency on
  `(commander, command)`, `RpgStore.WorldTurns.cs:84-153`; claim-log replay key
  `(cache_id, world_id, entity_id, correlation_id)`, `RpgStore.CacheFieldAccess.cs:149-152,223-256`;
  re-commit returns the byte-identical recorded result, `:296-300,363-365`). This session
  re-opened all three code sites and agrees: no second key, no discrepancy to document — the
  debit row rides the same key (§Design 4). Had the code shown a divergent key (e.g. a
  `claim-<uuid>` distinct from `CommandId`), this section would name it; it does not.
- **`RulesetVersion` 11 → 12 rides with `budget-debit`, not here (AS BUILT: 4A.7 took 10→11
  first).** The bump is that module's
  §Design 6 consequence (first *pricing* behavioral change: a priced act changes `MovementRemaining`
  where an unpriced replay did not). This module lands on 12 and bumps nothing further unless
  its own wiring moves a golden — wiring a priced verb onto an already-priced seam changes
  which rows pay, which IS a golden move for logs containing the newly-wired kinds, re-blessed
  in the same change (§Design 6).
- **No pricing here owns numbers.** Costs are tunables owned by `act-price-table`; this module
  reads them through the seam's lookup (`WorldTuningHub.Tuning.Movement.*`) and never mints a
  `const`, a second file, or a parallel loader (act-price-table Locked anchors; tunables-ssot T1/T3).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Closed 12-kind vocabulary — zero cargo/cache kinds in code | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:7-88` (`All` `:83-84` lists exactly the twelve; no `claim-cache`, no `deposit-cargo`) |
| Engine version live value 10; new-kind-no-bump precedent | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:94` (`RulesetVersion = 10`); `:101-109` (Assaults no-bump comment) |
| Snapshot refill overwrites every legion's budget post-resolvers | `TurnEngine.cs:405-423` (comment `:405-407`, overwrite `:420`) — read this session |
| Submit idempotent on `(commander, command)`; replay returns recorded outcome | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:119-130` (`Replayed: true` / `ok` arms; existence check `:139-153`) |
| Claim-log replay key carries `correlation_id`; replay read + insert | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:149-152` (log schema, PK includes `correlation_id`), `:232` (replay `SELECT … correlation_id = $corr`), `:251` (insert), `:296-300` (replay short-circuit, cited via claim-endpoints) |
| Claim verb: reachability re-check before per-row loop; per-row fit/skip | `RpgStore.CacheFieldAccess.cs:302-304` (re-check), per-row gates `:326-337` (cited via cargo-commands §Design 4; file opened this session, schema + replay lines verified) |
| `MovementRemaining` persisted per entity; diff compares it | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:380,639`; `RpgStore.WorldGraphDiff.cs:328,389` |
| Tuning: exactly one movement price (`dowseBudgetMilli: 250`); zero `*CostMilli` act keys | `gk-core/data/tuning/world.v5.json:83-85` (grep this session: no `claimCost`/`depositCost` in any `world.v{n}.json`) |
| No `DebitActCostUnlocked` anywhere under `src/` (seam is spec-only until budget-debit lands) | Verified by grep this session over `gk-core/src/FusionRpg.Data/Sqlite` — zero hits |
| Claim-before-decay pipeline slot (pass before decay tick `:586`) | `spec-cargo-commands.md` §Design 5 (consumed; `CommitWorldTurn` `:510-591` structure verified via that spec's citations) |

### Real gap (this module closes it)

| Gap | What this module builds |
|---|---|
| Priced verbs have no pipe to the seam — and no kinds in code to file them under | §Design 1: kind→cost-key wiring table; filing order follows `cargo-commands` §Design 1–3 (that spec owns kind creation, this spec owns price attachment) |
| Deposit pipe completeness unproven end to end (ideal §3 named it: "deposit is priced with no pipe") | §Design 3: deposit/withdraw/load/unload pipe proof — kind (cargo-commands) → admission arm → verb → seam call → report string, one row per verb |
| Claim-vs-decay cost half needs its implementation site, not just its rule | §Design 2: seam-call placement relative to the reachability gate and the per-row loop (before-loop for claim, before-move for the rest) |
| Replay↔`CommandId` debit idempotency needs convergence proof against `claim-endpoints` | §Design 4: debit row keyed `(worldId, turn, commandId)` in the same tx; convergent with `correlationId := CommandId` — evidence re-verified this session, no discrepancy |
| Golden consequence of wiring each priced verb (who moves, who stays identical) | §Design 6: per-verb golden delta; ride on 11, re-bless in the same change |

### Named gap this module does NOT close

**`load-cargo` / `unload-cargo` priced-by-table but unpriced-by-`cargo-commands`.**
`spec-cargo-commands.md` §Design 6 reserves cost keys for claim + deposit/withdraw only
("Load/unload/transfer pass the seam with no charge even after pricing lands"), while
`spec-act-price-table.md` §Design 1 ships `loadCostMilli` / `unloadCostMilli` (50 provisional)
and `spec-budget-debit.md` §Design 2 prices all five ("the table is the newer lock and wins
on names/units; transfer stays 0"). The precedence is settled — the table wins, load/unload
are priced at 50 — and this spec wires all five accordingly (§Design 1). What remains open is
the `cargo-commands` text drift (its §Design 6 says "no charge" where this program now
charges); `budget-debit` already records the override, and implementation updates that one
paragraph when the seam lands. `transfer-cargo` stays 0 under every lock (Q3; both specs agree).

## Design

### 1. Price wiring — kind → cost key → seam (the whole module in one table)

Each row is wired at the locked site (§Design 2). Cost values are provisional content owned
by `act-price-table` (250 / 100 / 100 / 50 / 50); key names and per-mille units are the lock
this table consumes:

| Kind (`cargo-commands` §Design 1) | Cost key (`movement` section) | Provisional | Seam call |
|---|---|---|---|
| `claim-cache` | `claimCostMilli` | 250 | Before the per-row loop, after the reachability re-check (§Design 2) |
| `deposit-cargo` | `depositCostMilli` | 100 | After gates pass, before the move (§Design 2) |
| `withdraw-cargo` | `withdrawCostMilli` | 100 | After gates pass, before the move |
| `load-cargo` | `loadCostMilli` | 50 | After gates pass, before the move (table-wins override, see Named gap) |
| `unload-cargo` | `unloadCostMilli` | 50 | After gates pass, before the move (same override) |
| `transfer-cargo` | — (unpriced, Q3) | 0 | Passes the seam with no charge; same-legion no-op preserved |

- Kind existence: all six kinds are defined by `cargo-commands` §Design 1 and admitted by its
  §Design 3 — confirmed present in spec, confirmed absent in code (`WorldCommand.cs:83-84`
  lists twelve, verified this session). Filing order (submit → admit → commit pass) is that
  spec's §Design 5; this spec adds the spend inside the per-command scope, never a new phase.
- Cost source: the seam's lookup only (`WorldTuningHub.Tuning.Movement.*CostMilli`, the
  `BudgetFor` dowse-read precedent `LaneCost.cs:47-57` via budget-debit §Design 2). A missing
  key fails loudly at boot (act-price-table T5) — this module never defaults, never catches.
- `transfer-cargo` is not "free by omission": the seam is still entered (one call site, one
  audit trail) and returns charged-0, so a future price needs only a table row, never a new
  call site. Same-legion no-op success (`RpgStore.LegionCargo.cs:474-480` via cargo-commands
  §Design 4) charges 0 like any transfer — moving nothing costs nothing.
- `clear` / `sustain` / `build` are NOT wired here (Q3: claim+deposit only; build stacks
  nothing). `clearCostMilli` / `sustainCostMilli` remain reserved names (act-price-table
  §Design 3); wiring one is a later spec's decision (Boundaries: ask first).

### 2. Seam-call placement — where the spend lands per verb

Inside the per-command scope (`cargo-commands` §Design 5 order: stable `(commander, command)`;
claims before the decay tick), the pass calls the seam exactly once per priced command:

```
claim-cache:
  stale-legion drops (entity.gone / entity.routed) → refuse, no seam call (free retry)
  reachability re-check fails (cache.unreachable)  → refuse, no seam call (free retry)
  reaches per-row loop                             → DebitActCostUnlocked(...) FIRST,
     short budget → entity.spent, rows untouched, decay sees the full cache
     else charge 250, then run the per-row fit/skip loop;
     claimed rows gone before decay, skipped rows remain and decay normally

deposit / withdraw / load / unload (whole-act, no skip shape):
  any gate fails (cargo.not-present / wrong-faction / sector-full / over-weight / no-slots /
  not-found / not-owned / cross-empire)            → refuse, no seam call
  all gates pass                                   → DebitActCostUnlocked(...),
     short budget → entity.spent, zero writes
     else charge once, then the move in the same tx (gate-before-write, atomic)
```

- The claim seam call sits BETWEEN the reachability gate and the loop: fog interaction
  (ideal "What this deliberately does not decide") falls out answered — a claim attempt on
  unobserved/forged ground costs nothing, because the verb checks reachability first today
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:302-304`) and cost-after-admit preserves that for free under the
  command-kind seam (Q4). No separate fog rule is needed or added.
- `entity.spent` appends as `TurnReportKinds.CommandDropped` with the verb's would-be effect
  unwritten — same-tx atomicity (budget-debit §Design 2). The reason vocabulary stays the
  verbs' own strings verbatim; `entity.spent` joins the `entity.held` / `entity.routed`
  family (no new vocabulary invented).
- Hold-stance legions read the refilled allowance budget (hold-allowance owns the number);
  until it lands, a 0-budget garrison refuses `entity.spent` like any short budget
  (budget-debit §Design 2 — no free-acts hole, no crash, no special case here).

### 3. Deposit pipe completeness proof

Ideal §3 ("Deposit is priced with no pipe") is closed by three specs jointly; this section
proves the pipe exists end to end for each priced verb. Each row names the five links; every
link is decided (spec) except where marked CODE (shipped, verified this session or via the
consumed spec's in-session verification):

| Verb | Kind | Admission arm | Resolve verb (CODE) | Seam + report |
|---|---|---|---|---|
| claim | `claim-cache` (cargo-commands §D1) | `entity.missing` / `cache.missing` (cargo-commands §D3) | `ClaimCorpseCacheIntoCargoUnlocked(…, correlationId := CommandId, …)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:280-387`; log key `:149-152`, re-check `:302-304`) | Seam before loop (§Design 2); `cache.claimed:<c>+<s>` / `cache.unreachable` / `entity.spent` |
| deposit | `deposit-cargo` | `entity.missing` / `sector.missing` / `cargo.seq-missing` | `DepositUnlocked(…, entityId, sectorId, seq)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:62-96`; refusals `not-found → not-present → wrong-faction → sector-full`) | Seam before move; `cargo.deposited:<newSeq>` / verb refusal / `entity.spent` |
| withdraw | `withdraw-cargo` | same deposit shape | `WithdrawUnlocked(…, sectorId, entityId, seq, weightEach←server)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:136-147`; refusals `:149-175`) | Seam before move; `cargo.withdrawn:<newSeq>` / verb refusal / `entity.spent` |
| load | `load-cargo` | `entity.missing` / `cargo.kind-unknown` / `cargo.ref-missing` | `LoadCargoUnlocked(…)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:253-304`) | Seam before move; `cargo.loaded:<newSeq>` / verb refusal / `entity.spent` |
| unload | `unload-cargo` | `entity.missing` / `cargo.seq-missing` | `UnloadCargoUnlocked(…)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:395-402`) | Seam before move; `cargo.unloaded:<seq>` / verb refusal / `entity.spent` |

- Wire fields (`Seq`, `CacheId`, `CargoKind`, `InstanceId`, `ContainerId`, `Qty`) ride the
  `CommandPayload` / `ReadCommandRow` / `WorldCommandRequest` / `/commands` mapping that
  `cargo-commands` §Design 2 extends field-for-field; `weightEach` is never on the wire
  (server-side resolution, loud `cargo.weight-unknown` on lookup failure — that spec's D3).
- The pipe's three program-internal joints are each owned exactly once: kinds + admission +
  pass (`cargo-commands`), keys + loader (`act-price-table`), seam body + order + refusal
  (`budget-debit`). This module owns only the attachment rows (§Design 1) and the claim
  placement rule (§Design 2) — no joint is re-decided, no second seam, no parallel engine.

### 4. Replay ↔ `CommandId` mapping — debit once (CONVERGENT, with evidence)

**Conclusion: converge with `claim-endpoints`' `correlationId := CommandId`. No discrepancy.**
Three independent code readings, all re-opened this session, point at the same key:

1. Submit is idempotent on `(commander, command)` (`RpgStore.WorldTurns.cs:119-130` —
   a retried filing returns `Replayed: true` with zero new rows). The claim POST filer
   (`claim-endpoints` §Design 3) constructs one `claim-cache` command per `CommandId` and
   delegates to `SubmitWorldCommands`, so a double-tapped pick-up button files once.
2. The claim replay log is keyed `(cache_id, delve_id, party_index, world_id, entity_id,
   correlation_id)` (`RpgStore.CacheFieldAccess.cs:149-152`); the replay read filters
   `correlation_id = $corr` (`:232`) and the short-circuit returns the recorded result with
   no `DELETE`/no `INSERT` (`:296-300` via claim-endpoints §Design 3). With
   `correlationId := command.CommandId`, a re-commit is a read-back by construction.
3. The debit row rides the same key: `(worldId, turn, commandId)` written in the same tx as
   the cargo move (budget-debit §Design 5). A second arrival of a recorded `CommandId`
   returns the stored report detail without re-running the verb and without re-debiting.

Why not a distinctive `claim-<uuid>`: the log key already contains
`(cache_id, world_id, entity_id)` — the only remaining disambiguator a retry needs is "which
filing", and `CommandId` already is that, unique per commander per turn
(`WorldCommand.cs:103-104` via claim-endpoints §Design 3). A second key would need its own
uniqueness proof and its own absent→empty discipline for zero gain. Post-trim
re-derivation replays Step + the post-Step pass from the never-trimmed command log and
converges (budget-debit §Design 5 corrected 2026-09-15: the pass re-hashes after debiting
because `MovementRemaining` IS hashed — the old "unaffected" sentence was wrong); the stored
hot-tail report plus the never-trimmed command log remain the audit trail.

### 5. Numeric types

Costs are `int` per-mille at rest (act-price-table §Design 4, matching `DowseBudgetMilli`,
`WorldTuning.cs:19`); budget points are `int` on `WorldEntity.MovementRemaining` (the
existing frame, `WorldState.cs:311` via the ideal). Debit arithmetic widens to `long`,
`checked`, subtract-only — no multiply/divide on this path, so the divide-by-1000-last
discipline (`LaneCost.cs:131-144`) is satisfied vacuously and cited, not re-proven.
Integer overflow throws, never wraps; narrowing is checked (DESIGN-GATE §2.13). Wire `Qty`
is `long?`, `Seq` is `int?` (cargo-commands §Numeric types) — untouched.

### 6. RulesetVersion 11 → 12 + golden re-bless (consequence named per priced verb)

The bump itself is `budget-debit` §Design 6 (lands with the seam body; `TurnEngine.cs`
`RulesetVersion = 12` is the live value verified this session — 4A.7 took 10→11 first). This module's wiring
determines WHICH goldens the re-bless covers:

| Log population | Golden consequence |
|---|---|
| Zero of the six kinds | Byte-identical on 12 (Assaults-phase precedent, `TurnEngine.cs:101-109`); the bump exists only for the case below |
| Any priced kind (`claim-cache`, `deposit/withdraw`, `load/unload` after the table-wins override) | Diverges by exactly the debit — re-blessed in the same change; the divergence is the bump justification, not an accident |
| `transfer-cargo` only | Identical (charge 0, no budget write) — proves the seam-entered-but-unpriced path moves nothing |

`claim-pricing` rides on 12; it bumps again only if it moves a golden itself. `act-price-table` moves no golden by lock (nothing reads the keys until the
seam body + this wiring land).

## Tunables

Owned by act-price-table, read here — no values set, no file touched:

| Tunable | Home | This module's use |
|---|---|---|
| `claimCostMilli` (250 provisional), `depositCostMilli` / `withdrawCostMilli` (100), `loadCostMilli` / `unloadCostMilli` (50) | `data/tuning/world.v{n+1}.json` `movement` | §Design 1 wiring table, read via the seam's `WorldTuningHub` lookup |
| `holdAllowanceMilli` (250 provisional) | same file | Read indirectly — the refill writes it, the seam reads the row |
| Refill frame (`PointsPerTurn` 1000, scout 500, hold 0, `dowseBudgetMilli` 250) | NOT retuned — fixed frame | Measured against, never moved (T7) |
| `entity.spent` + `cache.claimed:<c>+<s>` / `cache.unreachable` / `cargo.*` sentences | Authored copy catalog (GG-62); authored at claim-endpoints/legion-sheet spec time | Report reason strings only; copy owned by empire-inventory-surfaces wave 2 |

## Numeric types

Per §Design 5: `int` at rest (costs, budget points), `long` + `checked` at the subtraction.
`Qty` / `weightEach` types are cargo-commands' lock, untouched.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurn"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CargoCommands"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldClaimEndpoints"
python gk-core/scripts/guard-dal.py        # every new SQL string lives in FusionRpg.Data
python gk-fusion/scripts/guard-single-writer.py   # untouched, but this spec's non-touch list overlaps its seam
```

## Structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs   EXTEND — per-verb seam calls (§Design 1–2);
                                                       claim call between re-check and loop,
                                                       whole-act calls after gates before moves;
                                                       debit-once key (worldId, turn, commandId) (§Design 4)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs          EXTENDED BY cargo-commands (six kinds — consumed, not re-decided)
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs            UNTOUCHED by this module (11 already landed with budget-debit;
                                                       no phase, refill, or resolver change)
data/tuning/world.v{n+1}.json                          UNTOUCHED (keys owned by act-price-table)
gk-core/tests/FusionRpg.Data.Tests/CargoCommands/              EXTEND — per-verb wiring (5 charged + 1 unpriced),
                                                       attempt-pays (0+N charged), refusal-free (unreachable
                                                       uncharged), replay-no-redebit, per-verb golden delta
UNTOUCHED: WorldCommandAdmission.cs (arms owned by cargo-commands), MovementPhase.cs,
           MarchResolver.cs, LaneCost.cs (no BudgetFor change), WorldTuning.cs (keys owned by
           act-price-table), WorldEndpoints.cs / WorldDtos.cs (filers owned by claim-endpoints),
           RpgStore.LegionCargo.cs / CargoTransfer.cs / CacheFieldAccess.cs verb bodies,
           decay tick, Intel/belief projection, web/.
```

## Code style

```csharp
// Claim: the reachability gate already ran (forged/stale ids refuse free above),
// so reaching the loop means the legion really pried — charge once, then fit/skip.
var (ok, spent) = DebitActCostUnlocked(db, tx, worldId, command.EntityId, command.Kind);
if (!ok) report.Add(phase, TurnReportKinds.CommandDropped, command.CommandId, spent); // entity.spent
```

## Testing strategy

- **Per-verb wiring:** one `deposit-cargo` (100), one `withdraw-cargo` (100), one
  `load-cargo` (50), one `unload-cargo` (50), one `claim-cache` (250) — each leaves the
  post-refill budget exactly `cost` lower; one `transfer-cargo` leaves it unchanged.
- **Flat per-act:** two identical `claim-cache` attempts cost 250 + 250 regardless of member
  count, level, or faction; transfer costs 0.
- **Attempt-pays:** `cache.claimed:0+N` (cargo full, all rows skipped) still debits the full
  250; skipped rows remain subject to decay in the same commit (claim-before-decay with its
  cost half — left-behind rows are pay-for-nothing by construction).
- **Refusal-free:** `cache.unreachable` (stale/forged cache), `entity.gone`,
  `entity.routed` — zero budget change, free retry next turn after scouting.
- **Short budget refuses:** remaining < cost → `entity.spent`, zero writes on cargo tables
  and zero change to the budget row.
- **Replay debits once:** re-commit of a recorded `CommandId` returns the byte-identical
  detail (`cache.claimed:<c>+<s>` incl. per-row lists) with no second subtract; double-POST
  of the same `CommandId` returns `Replayed: true` with one stored command row.
- **Per-verb golden delta:** zero-kind logs hash-identical on 11; transfer-only logs
  identical; each priced kind diverges by exactly its debit (bump justification table,
  §Design 6).
- **Deposit pipe proof as tests:** each §Design 3 row is a filed→admitted→committed→reported
  round trip asserting the exact detail string plus the exact post-refill budget.

## Boundaries

- **Always:** gates before writes; one transaction (the commit's); debit after refill, never
  before; seam between reachability and loop for claim, after gates before moves for the
  rest; verb reasons verbatim; `correlationId := CommandId` for move and spend alike.
- **Ask first:** pricing `clear`/`sustain`/`build` (reserved-or-excluded per act-price-table
  §Design 3 — a later spec's decision); a count cap alongside the pool (Fork C needs observed
  spam, ideal §The shape); widening the seam signature beyond
  `(db, tx, worldId, entityId, kind)`.
- **Never:** a `const` cost in code; a second pool, count cap by default, or level curve; a
  refill-frame or `BudgetFor` change; a new `WorldCommandKind` or wire field (cargo-commands
  owns kinds); resolving or debiting inside `TurnEngine.Step`; a fog/position/capacity
  recomputation on the FE; touching Status/ActorHub/Combat/Injector surfaces.

## Success criteria

1. Each priced verb spends exactly its table cost from the post-refill budget; transfer
   spends 0 through the same call site. 2. Refused claims retry free; all-skipped claims
   pay; decay sees only left-behind rows. 3. Replay of a `CommandId` never double-spends —
   convergent with `claim-endpoints`, no divergent key. 4. Deposit pipe proven per §Design 3
   (five round trips, exact strings, exact budgets). 5. Version 11 with per-verb golden
   delta (§Design 6); zero-kind and transfer-only logs hash-identical. 6. `guard-dal.py`
   green; zero edits to every path in the Non-touch list (verified by diff).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Kind→cost-key wiring (§Design 1) + seam-call placement (§Design 2) | `claim-endpoints` — prices the filed kinds without touching its four routes; the filer response contract ("filed / replayed / refused-at-submit") is unchanged, only the commit-time spend is newly attached |
| Attempt-pays / refusal-free implementation (§Design 2) | `storage-cache-ui` (wave 2) — partial-success vs stale-pin copy is authored against charged-`0+N` vs free-`unreachable`, locked here |
| Debit-once per `CommandId` + convergence proof (§Design 4) | `legion-sheet` / `storage-cache-ui` — safe retry buttons (double-POST replays at submit, re-commit replays at resolve, both byte-identical) |
| Per-verb golden delta (§Design 6) | release — the re-bless scope for the 11 → 12 bump |

## Non-touch list (explicit)

No new `WorldCommandKind`s, payload fields, or admission arms (cargo-commands owns kinds);
no refill, `BudgetFor`, `LaneCost`, `MovementPhase`/`MarchResolver` leftover, or stance-frame
change; no `LaneCost` re-mint or ley/banner discount for acts; no tuning file edit (keys
owned by act-price-table); no `TurnEngine.cs` edit (12 already landed with budget-debit); no
`WorldEndpoints`/`WorldDtos` field (filers owned by claim-endpoints); no verb-body edit; no
decay-tick, Intel, AI-policy, Status/ActorHub/Combat/Injector/FE change.

## Design-gate checklist

```
[x] Subsystems: world-map turn engine + movement budget (Core), cargo/cache Data verbs,
    world tuning names, Server filer idempotency (read-only). No Status/ActorHub/Combat/
    Injector/FE subsystem touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
    (Spec-only session: one new file under docs/architecture/world-action-economy/.)
[ ] Session-boundary record + scripts/session-boundary-check.py — NOT run this session
    (no code edited, no commit attempted; honest gap, one sentence).
[x] Read this session: spec-budget-debit.md IN FULL (debit-after-refill, attempt-pays/
    refusal-free, replay-once-per-CommandId, 10→11); spec-act-price-table.md (key names,
    per-mille units, provisional values); spec-cargo-commands.md (claim-cache converged kind,
    six kinds, post-Step pass, correlationId:=CommandId, debit seam); spec-claim-endpoints.md
    §Design 3 (correlationId:=CommandId end to end WITH EVIDENCE — converged, §Design 4);
    world-action-economy-map.md (module claim-pricing row 4, wave 2); world-action-economy-
    ideal.md Locked constraints §3 (deposit pipe) + §4 (precedence + mapping) + Owner
    resolutions Q1–Q6; DESIGN-GATE.md §1 rows + §2 invariants + §5 checklist.
[x] Checked decisions.md for a lock: Owner resolutions 2026-09-15 (Q1 extend-budget, Q2 small
    allowance, Q3 claim+deposit, Q4 command-kind, Q5 flat, Q6 march-free) are the governing
    locks; phase-order + RulesetVersion-history rows reused for the ride-on-11 call.
[x] Every factual claim cites file:line (see §What already exists table + §§Design 1–6).
[x] Verified claims against CODE, not comments: WorldCommand.cs (:7-88 kinds, :83-84 twelve,
    zero cargo kinds), TurnEngine.cs (:94 RulesetVersion 10, :101-109 no-bump precedent,
    :405-423 Snapshot refill), RpgStore.WorldTurns.cs (:119-130 submit idempotency,
    :139-153 existence check), RpgStore.CacheFieldAccess.cs (:149-152 log key,
    :232 replay read, :251 insert), RpgStore.World.cs (:380,:639 MovementRemaining),
    RpgStore.WorldGraphDiff.cs (:328,:389 diff compare), gk-core/data/tuning/world.v5.json (:83-85
    dowse-only movement, zero *CostMilli keys by grep), src-wide zero hits for
    DebitActCostUnlocked — all opened/grepped in-session in the worktree.
[x] Read the surrounding section of every rule quoted (refill comment :405-407 with its
    posture-then-refill section; Assaults no-bump comment :101-109; claim-log schema with
    its delve-sentinel columns :149-152; submit arms :119-130 with the world.unknown /
    not-a-map guards :92-102).
[x] Tested (not assumed) constraints: no suite run — spec phase; the bump-ride and
    per-verb-divergence claims are staked on named new tests (§Testing strategy), not
    asserted as measured. The correlationId:=CommandId convergence is a code reading
    (three sites, §Design 4), not a test result — stated as such.
[x] Nothing contradicts a §2 invariant: SQL only in FusionRpg.Data (guard-dal); no magnitude
    cap (spends refuse with reason, never clamp); no f(level) (flat per-act, no ladder read);
    no second pool/composer/path (Fork B/C rejections restated in Boundaries, not
    relitigated); SOLID: one seam, one call site per verb, one hub — the parallel price
    engine named in ideal §Rejected stays rejected.
[x] Corrections propagated: flat + march-free + command-kind + claim+deposit scope appear in
    Locked anchors, Design, Tunables-equivalent, Interface, and Non-touch list identically;
    the load/unload table-wins override is named identically in Real gap, §Design 1, and
    Boundaries-never (no new kind to smuggle it through).
[x] No assertion pins a derived-population count, item total, generated name/description
    text, or per-cycle outcome. (Integers named: 250/100/50 costs + 1000/500/0/250 frame are
    consumed live-code/tuning readings with stated owners, not guardrails; 12 kinds + 6 new
    — closed code-owned vocabularies with stated reasons.)
[x] No event-refreshed cache introduced. (AsOfTurn staleness + stored-report audit trail
    cited as built behavior; post-trim re-derivation gap stated in §Design 4, not hidden.)
[x] No acceptance criterion fixes an ordering that can vary in real play. (Commit-internal
    order — diff→cargo→log→decay — is a fixed pipeline sequence, asserted; stable
    (commander, command) order reused from cargo-commands, never reinvented; per-row seq
    order is the verb's own deterministic tie-break.)
[x] No actor combat/derived magnitude produced or consumed — no Hub-adjacent subsystem touched.
[x] No SOLID-violating parallel path: no second admit path, no parallel price engine, no
    forked capacity/reachability math; transfer's zero-charge rides the one seam, not a
    bypass.
```
