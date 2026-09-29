# Spec: `budget-debit`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `budget-debit`, row 2 of the
[world-action-economy map](../world-action-economy-map.md) (wave 1; depends on `act-price-table`
+ ext `cargo-commands`). Ideals: [world-action-economy-ideal.md](../world-action-economy-ideal.md)
Locked constraints §1 (debit-vs-refill) + §3 (deposit pipe) + §4 (precedence); Owner resolutions
Q1 extend-budget, Q4 command-kind, Q5 flat, Q6 march-free. Dependencies consumed exactly:
[spec-act-price-table.md](spec-act-price-table.md) (six keys + units + provisional values);
[../empire-inventory-surfaces/spec-cargo-commands.md](../empire-inventory-surfaces/spec-cargo-commands.md)
(no-op `DebitActCostUnlocked` seam + debit-after-refill order — this module FILLS that seam).
House style: `spec-legion-cargo.md`.

## Objective

The six cargo/cache command kinds file and resolve for free today — the resolver exposes a
no-op `DebitActCostUnlocked(db, tx, worldId, entityId, kind)` seam inside the per-command scope
(cargo-commands §Design 6). This module gives that seam a body: every priced act spends flat
per-act-per-legion per-mille from the same `MovementRemaining` budget marching spends, after the
refill, with no reservation, no new kinds, and no refill-frame change.

Success looks like: a filed `claim-cache` that reaches its per-row loop leaves the legion's
next-turn `MovementRemaining` exactly `cost` lower than the refill wrote; a refused act leaves it
untouched; a marched-then-acting legion pays march from this turn and the act from next turn's
budget; an old log with none of the priced kinds replays with unchanged `StateHash` except for
the version bump.

## Locked anchors

- **Debit-after-refill is locked, refill-minus-spent is rejected with evidence** (§Design 1).
  The cargo pass runs post-Step post-Diff, so the DB already holds the refilled next-turn budget
  (`TurnEngine.cs:413-423`); an act spends next turn's march, never this turn's leftover. The
  alternative (subtract inside Snapshot before the overwrite) would rewrite the refill line itself
  — a refill-frame change this spec is forbidden to make, inside a `TurnEngine.cs` both this
  program and `cargo-commands` hold untouched.
- **Flat per-act-per-legion, key names and units consumed exactly** (act-price-table §Design 1):
  `claimCostMilli` 250, `depositCostMilli` 100, `withdrawCostMilli` 100, `loadCostMilli` 50,
  `unloadCostMilli` 50 (all per-mille, `movement` section, provisional content). No member-count
  scaling, no level curve (no ladder read — flat spends need none), no faction/stance discount.
- **March-then-act preserved, no reservation** (Owner resolutions Q6). Marching never sees the
  debit; the debit never reserves at Reveal. A band that sprinted all day cannot also strip a
  battlefield bare — the tradeoff is observed, not pre-booked.
- **No pricing here owns numbers.** Costs are tunables owned by `act-price-table`; this module
  reads them through `WorldTuningHub` like `BudgetFor` reads dowse (`LaneCost.cs:55`) and never
  mints a `const`, a second file, or a parallel loader.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Per-legion turn budget + Snapshot refill reads NEW posture: `MovementRemaining = BudgetFor(stance)` after resolvers run | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:405-423` (comment `:405-407`, overwrite `:420`) |
| Refill frame: march 1000 (`PointsPerTurn`), scout 500, hold 0, dowse tunable | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:32,35,47-57` |
| March spends `MovementRemaining` per-mille, leftover carried (`budget - spent`) | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:70-74,146-149`; applied `MovementPhase.cs:125-132`; crossing-stop `MovementPhase.cs:301-310` |
| One-move-last-wins; leftover belongs to nobody until Snapshot overwrites it | `MovementPhase.cs:36-41`; `TurnEngine.cs:413-423` (unconditional overwrite) |
| Phase order: Reveal → Movement → Sieges(/Assaults) → Production → Growth → Pressure → Events → Snapshot → Intel | `TurnEngine.cs:94-126` (phase names), executed `:160-177` |
| Claims settle in Snapshot AFTER movement; postures land just before refill | `TurnEngine.cs:380-385` (comment), `:405-411` (postures) |
| No-op debit seam + order lock: `DebitActCostUnlocked` accept-always, debit-after-refill, priced verbs claim+deposit/withdraw | `spec-cargo-commands.md` §Design 6 (consumed, not re-decided) |
| Claim-before-decay locked; per-row skip-not-refuse; replay key `correlationId := CommandId` | `spec-cargo-commands.md` §Design 4–5 |
| Closed 12-kind vocabulary; submit DTO + `/commands` mapping carry exactly the old fields | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:7-88,98-146`; `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:450-472`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:108-121` |
| Engine version live value 10; new-kind-no-bump precedent for pure additions | `TurnEngine.cs:94` (`RulesetVersion = 10`); `:101-109` (Assaults no-bump comment) |
| Per-mille arithmetic discipline: `long` widen, divide-by-1000-last | `LaneCost.cs:131-144` |
| Refusal vocabulary has no `*.spent` member yet | cargo-commands §Design 6 (short-budget shape is this module's content call) |

### Real gap (this module closes it)

| Gap | What this module builds |
|---|---|
| `DebitActCostUnlocked` accepts always; no budget read or write on the cargo path | §Design 2: the seam body — cost lookup + sufficiency gate + spend |
| No `entity.spent`-shaped refusal for a short budget | §Design 2: `entity.spent` refusal, report-verbatim |
| Claim-vs-decay precedence's cost half unnamed (pay-for-nothing vs free retry per left-behind row) | §Design 4: attempt-pays, refusal-retries-free |
| Replay↔`CommandId` debit idempotency unnamed on the cost side | §Design 5: debit once per `CommandId`, replay returns recorded result without re-debit |

## Design

### 1. Order decision — debit-after-refill (LOCKED, with evidence)

**Decided once: debit-after-refill. Refill-minus-spent is rejected.**

Evidence against `TurnEngine.cs:405-423`: Snapshot unconditionally overwrites every legion's
`MovementRemaining` with `BudgetFor(stance)` (`:420`) after all resolvers run. Any spend written
into the in-`Step` world before that line is wiped — free acts by construction. A
refill-minus-spent shape (`BudgetFor(stance) - spentThisTurn`) would have to edit that overwrite
line, changing the refill frame every other module measures against (act-price-table Locked
anchors: "fixed frame"; cargo-commands: "`TurnEngine.cs` is untouched"). The cargo pass instead
runs Data-side post-Step post-Diff inside the commit transaction, where the DB row already holds
the refilled next-turn budget — so the debit reads live `MovementRemaining` there and subtracts.
An act spends next turn's march; this turn's march leftover is already gone (overwritten), never
double-spent. The HOMM3 shape from the ideal (Dimension Door spends the same day's pool) is
preserved across the turn boundary: march-then-act in one commit = march spends this turn's
budget in `Step`, act spends next turn's budget in the post-Step pass.

Consequence owned here: between-turn immediacy. A same-turn "march 1000 then claim" always
succeeds its budget gate (the claim reads the fresh refill, not the exhausted leftover) — the
bill arrives next turn. That is Q6 march-free as decided, not a loophole to close later.

### 2. The seam body — lookup, gate, spend

Inside the per-command scope (cargo-commands §Design 5), after gates pass and before the move,
the pass calls `DebitActCostUnlocked(db, tx, worldId, entityId, kind)`:

```
cost = kind switch {
  "claim-cache"    => Tuning.Movement.ClaimCostMilli,    // 250 provisional
  "deposit-cargo"  => Tuning.Movement.DepositCostMilli,  // 100
  "withdraw-cargo" => Tuning.Movement.WithdrawCostMilli, // 100
  "load-cargo"     => Tuning.Movement.LoadCostMilli,     // 50
  "unload-cargo"   => Tuning.Movement.UnloadCostMilli,   // 50
  "transfer-cargo" => 0,                                  // unpriced entirely (Q3)
  _ => 0                                                  // non-cargo kinds never reach the seam
};
read live MovementRemaining for (worldId, entityId) in same tx;
if (remaining < cost) return (false, "entity.spent");
write remaining - cost in same tx (checked long arithmetic, divide-by-1000-last has no divisor here — costs are already budget points);
return (true, "");
```

- Cost source: `WorldTuningHub.Tuning.Movement.*` only — the `BudgetFor` dowse read
  (`LaneCost.cs:55`) is the precedent. Missing-key boot failure is act-price-table's lock (T5);
  this module never defaults, never catches.
- Priced verbs (Q3): claim + deposit/withdraw priced; load/unload priced at 50 per the table
  this spec consumes (act-price-table prices all five; cargo-commands reserved only three names —
  the table is the newer lock and wins on names/units; transfer stays 0).
- `transfer-cargo` passes the seam with no charge even after pricing lands (same-legion
  re-slotting is not an economy act).
- Refusal shape: `entity.spent` (recommended by cargo-commands §Design 6), appended as
  `TurnReportKinds.CommandDropped` with the verb's would-be effect unwritten — same-tx atomicity
  with the move (gate before any write, never a partial spend).
- Hold-stance legions read the refilled allowance budget (hold-allowance owns the number and the
  `BudgetFor(Hold) => 0` frame change); this seam reads whatever the refill wrote, never a
  special case. Until hold-allowance lands, a holding garrison with 0 remaining refuses
  `entity.spent` like any short budget — no free-acts hole, no crash.

### 3. March-then-act — no reservation (Q6 preserved)

No Reveal-time budget check, no earmark, no second march validation. `MovementPhase` leftover
semantics are untouched: march walks with `budget - spent` (`MarchResolver.cs:146-149`) and the
Snapshot overwrite discards whatever remains. The cargo debit never reads the in-`Step`
leftover — only the post-refill DB row — so marching and acting never contend for the same
integer. Filing order within a turn does not matter; per-legion multi-act ordering follows the
stable (commander, command) order the cargo pass already uses.

### 4. Claim-vs-decay precedence — attempt-pays, refusal-retries-free (LOCKED)

cargo-commands locks claim-before-decay (a claimed row is gone before decay sees it; skipped
rows remain and decay normally). The cost half locked here:

- **Whole-act refusal → no charge, free retry.** `entity.gone` / `entity.routed` /
  `cache.unreachable` (stale/forged cache, reachability re-check fails) returns before the seam —
  nothing was pried open, nothing is owed. Retrying next turn after scouting is free.
- **Attempt that reaches the per-row loop → charge once, regardless of claimed count.**
  `cache.claimed:<c>+<s>` with `c = 0, s > 0` (cargo full, all rows skipped) still pays the full
  250. Left-behind rows are pay-for-nothing by construction: the legion spent the turn prying and
  kept nothing. This is the anti-spam half of Fork C without a count cap — hammering a full
  pack against a rich cache burns 250 per retry while decay eats the cache.
- Deposit/withdraw/load/unload are whole-act (no skip shape): gate-fail refuses with no charge;
  gate-pass charges once before the move.

### 5. Replay ↔ `CommandId` mapping — debit once

`correlationId := CommandId` (cargo-commands §Design 4) is the idempotency key for both the
move and the spend. Re-commit / replay of a recorded `CommandId` returns the stored report
detail without re-running the verb and without re-debiting: the debit row is keyed
`(worldId, turn, commandId)` in the same tx as the cargo move, so a second arrival is a
read-back, never a second spend.

**StateHash correction (2026-09-15 strengthen pass — the prior text here was wrong).**
`MovementRemaining` IS hashed (`WorldCanonical.cs:61`), and `StateHasher.Hash` is computed at
`TurnEngine.Step` return (`TurnEngine.cs:178`) — BEFORE the post-Step cargo/debit pass runs
(`RpgStore.WorldTurns.cs:543-567`). So the stored hash covers the PRE-debit budget, and a
Step-only trim re-derivation restores the undebited budget. Corrected rules: (1) the pass
**re-hashes after debiting** and stores the post-debit hash — the hash always describes the
committed state, never the mid-commit state; (2) post-trim re-derivation replays Step + the
post-Step pass from the never-trimmed command log (the replay is debit-once per `CommandId` by
the rule above, so re-derivation converges); trim past a turn with priced acts WITHOUT the
command log is forbidden — name it in the trim code, don't assume it. Post-trim `Step`-only
re-derivation still omits cargo entries (stored report is the audit trail for contents).

### 6. RulesetVersion 11 → 12 + golden re-bless (consequence named)

AS BUILT 2026-09-15: `hold-allowance` (4A.7) landed first and took 10→11, so this module rides 11
and bumps 11→12. This is the first *pricing* behavioral change in the program (act-price-table
moves no golden by lock; cargo-commands holds version by proof — its no-bump test pins the live
`RulesetVersion` dynamically, never a literal). A priced act changes `MovementRemaining` where an
unpriced replay did not — old-log replay with the pass present diverges from the golden wherever
a priced kind appears. So: bump `TurnEngine.RulesetVersion` 11 → 12 with this module, and re-bless
the world-map golden set in the same change. Logs with zero priced kinds stay byte-identical (the
Assaults-phase precedent, `TurnEngine.cs:101-109`); the bump exists only for the case a real
priced order changes the outcome. `claim-pricing` rides on 12, it does not bump again unless it
moves a golden itself.

### 7. Numeric types

Costs are `int` per-mille at rest (act-price-table §Design 4, matching `DowseBudgetMilli`);
budget points are `int` on `WorldEntity.MovementRemaining` (the existing frame). Debit
arithmetic widens to `long`, `checked`, subtract-only — no multiply/divide on this path, so the
divide-by-1000-last discipline is satisfied vacuously and cited, not re-proven. Integer
overflow throws, never wraps; narrowing is checked (DESIGN-GATE §2.13).

## Tunables

Owned by act-price-table, read here — no values set, no file touched:

| Tunable | Home | This module's use |
|---|---|---|
| `claimCostMilli` (250 provisional), `depositCostMilli` / `withdrawCostMilli` (100), `loadCostMilli` / `unloadCostMilli` (50) | `data/tuning/world.v{n+1}.json` `movement` | §Design 2 lookup table, read via `WorldTuningHub` |
| `holdAllowanceMilli` (250 provisional) | same file | Read indirectly — the refill writes it, the seam reads the row |
| Refill frame (`PointsPerTurn` 1000, scout 500, hold 0, `dowseBudgetMilli` 250) | NOT retuned — fixed frame | Measured against, never moved (T7) |
| `entity.spent` sentence + meter states | Authored copy catalog (GG-62); authored at claim-endpoints/legion-sheet spec time | Report reason string only; copy owned by empire-inventory-surfaces wave 2 |

## Numeric types

Per §Design 7: `int` at rest (costs, budget points), `long` + `checked` at the subtraction. `Qty`/
`weightEach` types are cargo-commands' lock, untouched.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurn"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CargoCommands"
python gk-core/scripts/guard-dal.py        # every new SQL string lives in FusionRpg.Data
python gk-fusion/scripts/guard-single-writer.py   # untouched, but this spec's non-touch list overlaps its seam
```

## Structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs   MODIFIED — DebitActCostUnlocked body (§Design 2);
                                                       debit-once key (worldId, turn, commandId) (§Design 5)
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs            MODIFIED — RulesetVersion 10 → 11 ONLY (§Design 6);
                                                       no phase, refill, or resolver change
gk-core/tests/FusionRpg.Data.Tests/CargoCommands/              EXTEND — debit-after-refill, spent-refusal,
                                                       attempt-pays, replay-no-redebit, old-log hash
UNTOUCHED: WorldCommand.cs (no new kinds), WorldCommandAdmission.cs, MovementPhase.cs,
           MarchResolver.cs, LaneCost.cs (no BudgetFor change), WorldTuning.cs (keys owned by
           act-price-table), WorldEndpoints.cs / WorldDtos.cs (no new wire fields),
           RpgStore.LegionCargo.cs / CargoTransfer.cs / CacheFieldAccess.cs verb bodies,
           decay tick, Intel/belief projection, every tuning file, web/.
```

## Code style

```csharp
// Same-tx, gate-before-write, wonder-spend-shaped: the refill already landed (post-Step),
// so this spends next turn's march — never this turn's leftover, never a reservation.
var (ok, reason) = DebitActCostUnlocked(db, tx, worldId, command.EntityId, command.Kind);
if (!ok) report.Add(phase, TurnReportKinds.CommandDropped, command.CommandId, reason);
```

## Testing strategy

- **Debit-after-refill:** refill a legion to 1000, resolve one `deposit-cargo` (100) post-Step —
  DB reads 900. A legion that marched 1000-to-0 in `Step` still pays from the refill, not from
  the exhausted leftover.
- **Flat per-act:** two identical `claim-cache` attempts cost 250 + 250 regardless of member
  count, level, or faction; transfer costs 0.
- **Short budget refuses:** remaining < cost → `entity.spent`, zero writes on cargo tables and
  zero change to the budget row.
- **Attempt-pays / refusal-free:** `cache.unreachable` → no debit; `cache.claimed:0+N`
  (all-skipped) → full 250 debited; skipped rows remain subject to decay in the same commit.
- **Replay debits once:** re-commit of a recorded `CommandId` returns the byte-identical detail
  with no second subtract; post-trim re-derivation replays Step + post-Step pass from the
  untrimmed command log and converges (hash re-computed post-debit both times).
- **Old-log hash:** a golden log with zero priced kinds replays `StateHash`-identical on 11
  (no-bump proof for the unaffected population — no debit fires, re-hash is a fixed point);
  a log with a priced kind diverges by exactly the debit + re-hash (bump justification).
- **Hold-zero interim:** before hold-allowance lands, a 0-budget garrison refuses `entity.spent`
  (no hole, no crash).

## Boundaries

- **Always:** gates before writes; one transaction (the commit's); debit after refill, never
  before; verb reasons verbatim; `correlationId := CommandId` for move and spend alike.
- **Ask first:** pricing `clear`/`sustain`/`build` (reserved-or-excluded per act-price-table §Design 3 —
  a later spec's decision); a count cap alongside the pool (Fork C needs observed spam, ideal §The shape);
  widening the seam signature beyond `(db, tx, worldId, entityId, kind)`.
- **Never:** a `const` cost in code; a second pool, count cap by default, or level curve; a
  refill-frame or `BudgetFor` change; a new `WorldCommandKind` or wire field; resolving or
  debiting inside `TurnEngine.Step`; touching Status/ActorHub/Combat/Injector/FE surfaces.

## Success criteria

1. Priced acts spend exactly their table cost from the post-refill budget; short budgets refuse
   `entity.spent` with nothing written. 2. March-then-act works with no reservation in either
   direction. 3. Claim precedence holds: refused claims free, all-skipped claims paid, decay sees
   only left-behind rows. 4. Replay of a `CommandId` never double-spends. 5. `RulesetVersion` 11
   with re-blessed goldens; zero-priced-kind logs hash-identical. 6. `guard-dal.py` green; zero
   edits to every path in the Non-touch list (verified by diff).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `DebitActCostUnlocked` body + debit-after-refill order + `entity.spent` reason (§Design 1–2) | `claim-pricing` (module 4) — wires claim (+deposit) kinds onto this spend without re-deciding order or refusal shape |
| Attempt-pays / refusal-free precedence (§Design 4) | `claim-pricing` — the cost half of claim-vs-decay it inherits locked |
| Debit-once per `CommandId` (§Design 5) | `claim-endpoints` — the idempotency contract it relays to clients |
| `RulesetVersion` 12 (this module bumps 11→12; 4A.7 took 10→11) | `claim-pricing` — rides on 12, no second bump without a moved golden |

## Non-touch list (explicit)

No new `WorldCommandKind`s (cargo-commands owns kinds; claim-pricing owns wiring); no refill,
`BudgetFor`, `LaneCost`, `MovementPhase`/`MarchResolver` leftover, or stance-frame change;
no `LaneCost` re-mint or ley/banner discount for acts; no tuning file edit (keys owned by
act-price-table); no `WorldEndpoints`/`WorldDtos` field; no verb-body edit; no decay-tick,
Intel, AI-policy, Status/ActorHub/Combat/Injector/FE change.

## Design-gate checklist

```
[x] Subsystems: world-map turn engine + movement budget (Core), cargo/cache Data verbs,
    world tuning names. No Status/ActorHub/Combat/Injector/FE subsystem touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
    (Spec-only session: one new file under docs/architecture/world-action-economy/.)
[ ] Session-boundary record + scripts/session-boundary-check.py — NOT run this session
    (no code edited, no commit attempted; honest gap, one sentence).
[x] Read this session: spec-act-price-table.md + spec-cargo-commands.md IN FULL;
    world-action-economy-map.md (module budget-debit row); world-action-economy-ideal.md
    (Locked constraints §1 debit-vs-refill + §3 deposit pipe + §4 precedence; Owner
    resolutions extend-budget, command-kind, flat-march-free); DESIGN-GATE.md §1 rows +
    §2 invariants + §5 checklist.
[x] Checked decisions.md for a lock: Owner resolutions 2026-09-15 (Q1–Q6) are the governing
    locks; phase-order + RulesetVersion-history rows reused for the bump call.
[x] Every factual claim cites file:line (see §What already exists table + §Design 1).
[x] Verified claims against CODE, not comments: TurnEngine.cs (:94 RulesetVersion, :94-177
    phases/order, :188-233 Reveal, :380-423 Snapshot+refill), LaneCost.cs (:32-57 frame,
    :131-144 per-mille), MarchResolver.cs (:70-74 budget, :146-149 leftover),
    MovementPhase.cs (:36-41 last-wins, :125-132 leftover apply, :301-310 crossing spend),
    WorldCommand.cs (:7-88 kinds, :98-146 payload), WorldDtos.cs (:450-472 request),
    WorldEndpoints.cs (:108-121 mapping) all opened in-session in the worktree.
[x] Read the surrounding section of every rule quoted (refill comment :405-407 with its
    posture-then-refill section; Assaults no-bump comment :101-109; Reveal contract
    :181-190; Snapshot close-the-turn doc :372-376).
[x] Tested (not assumed) constraints: no suite run — spec phase; the bump claim is staked
    on named new tests (old-log hash + priced-divergence), not asserted as measured.
[x] Nothing contradicts a §2 invariant: SQL only in FusionRpg.Data (guard-dal); no magnitude
    cap (spends refuse with reason, allowance is a tuned number — structural turn boundary,
    throws/loud-refuses never clamps); no f(level); no second pool/composer/path (Fork B/C
    rejections restated in Boundaries, not relitigated); SOLID: one seam, one record, one
    hub — the parallel price engine named in ideal §Rejected stays rejected.
[x] Corrections propagated: flat + march-free + command-kind + claim+deposit scope appear in
    Locked anchors, Design, Tunables-equivalent, Interface, and Non-touch list identically.
[x] No assertion pins a derived-population count, item total, generated name/description
    text, or per-cycle outcome. (Integers named: 250/100/50 costs + 1000/500/0/250 frame are
    consumed live-code/tuning readings with stated owners, not guardrails; 12 kinds — a
    closed code-owned vocabulary with a stated reason.)
[x] No event-refreshed cache introduced. (Claim-log replay cited as built behavior;
    post-trim re-derivation gap stated in §Design 5, not hidden.)
[x] No acceptance criterion fixes an ordering that can vary in real play. (Commit-internal
    order — diff→cargo→log→decay — is a fixed pipeline sequence, asserted; stable
    (commander, command) order reused from Reveal, never reinvented.)
[x] No actor combat/derived magnitude produced or consumed — no Hub-adjacent subsystem touched.
[x] No SOLID-violating parallel path: no second admit path, no parallel price engine, no
    forked capacity math; the debit is the one seam's body, not a second pool.
```
