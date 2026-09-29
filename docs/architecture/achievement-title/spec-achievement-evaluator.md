# Spec: achievement-evaluator

Module `achievement-evaluator` (map: `docs/architecture/achievement-title-map.md`,
depends on `achievement-registry`). Reading gate as registry spec + overlay
control loops, match/unique-actor lifecycle, economy P13/P14, power ladder.

## Objective

Evaluate durable facts in a Cold worker and append exactly-once unlock rows —
never on any Hot path. Consumers: reward-bundles fan-out, Hall/actor-title
inventory. Success: replays, re-ingests, turn recomputes, and Snapshot re-runs
grant nothing new; grants never re-trigger evaluation (no self-loop).

## Tech Stack

C# net8 Server worker + `FusionRpg.Data` ledger; facts: Activity ledger,
soul/XP ledger, world-turn records, `match.result` (`GameOver`, never ghost
`board.end`). No Hot/Injector code.

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj
Test: dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AchievementEval"
Guards: python gk-core/scripts/guard-dal.py
Verify: powershell -File scripts/verify-change.ps1 -Paths <changed> -Session <id>
```

## Project Structure

```
gk-core/src/FusionRpg.Server/Achievements/AchievementEvaluator.cs → Cold worker (NEW)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Achievements.cs        → unlock ledger (NEW)
gk-core/tests/FusionRpg.Data.Tests/**/AchievementEval*            → idempotence tests (NEW)
```

## Code Style

```csharp
// Exactly-once key carries owner + scope identity + revision. Repeat facts are no-ops.
// scopeKey is the player id; world/season folds in iff reearnScope != never.
// Single-fact definitions dedupe on factId; composite definitions dedupe on a stable
// function of durable fact ids: (def, scope, count, maxFactId, world_id, turn).
// Re-earnable definitions (reearnScope world|season) fold the world/season id into
// dedupe; `never` (default) does not.
var key = (playerId, scopeKind, scopeKey, def.Id, def.Revision, dedupe);
if (!ledger.TryAppendUnlock(key, out var unlock, out var replayed)) return unlock; // canonical receipt both paths
if (!replayed) fanout.Enqueue(unlock); // bundles only; never re-enters evaluation
```

## Testing Strategy

xUnit: double-append same fact grants once and returns the canonical receipt;
out-of-order facts converge; composite triggers (e.g. wins across turns) use
watermarks — two different fact subsets reaching the same watermark grant
once (composite key is a stable function of durable fact ids, never a single
contributing fact); FULL trigger set enumerated incl. key-set moves (new
revision, new player, bind, corpse move, scope move) plus replay, re-ingest,
turn-recompute, and Snapshot re-run — each with its own order-independent
criterion tested in both directions (allocate→bind and bind→allocate).
Cold world-turn drain only (budgeted Server drain — never Injector Hot, never
on `combat.hit`); set→meta DAG loads reject cycles with cause naming ids and
evaluate in one topological pass (guard owned by registry spec). Facts use
real recorded rows (debug scope rule); no fabricated preconditions.

## Tunables & Catalogs

None owned (reads registry tuning: watermarks, windows). No new numbers here.

## Numeric Types

Counters `long`, `checked`; thresholds compare in `Θ`/per-mille units owned
by registry tuning — no local curve, no local money math.

## ActorHub Gate

Consume-only: reads facts/ledger, never composes actor numbers.

## Boundaries

- Always: Cold only — never between `combat.hit` and FA*; deltas via existing
  paths; ledger dedupe keys on every mutation.
- Ask first: new fact source (new table/event kind).
- Never: Hot evaluation; wall-clock accrual on world scope; loop-closing
  grants; guessing live PvZ state.

## Success Criteria

- [ ] Same fact evaluated twice → one unlock row.
- [ ] Out-of-order/composite facts converge to the same ledger state.
- [ ] Grant output never feeds evaluation input (loop test).

## Open Questions

None.
