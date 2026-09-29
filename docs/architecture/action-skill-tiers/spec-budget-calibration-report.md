# Spec: budget-calibration-report (ST4)

**Status: proposed 2026-09-18.** Module **ST4** of [action-skill-tiers-map.md](../action-skill-tiers-map.md).
Depends on **ST1**. Not approved; no build authorized.

## Objective

**Build the instrument ruling 3 waits on, so the neutral `referencePower` cannot quietly become the
value.**

Ruling 3 shipped `powerBudgetMilli` neutral and *stated untuned*, and the ideal names what would turn it
into the repo's fourth neutral-constant table: *"The smoke batch lands and the scalar stays neutral"*
(ideal, standing risk, trigger 1). `action-rungs.v2.json`'s `_meta` names the evidence:
*"what it tunes against is the smoke batch's accepted-container cost distribution (a later module's
output), not yet produced."* A-G1's spec describes the report (`spec-tier-access-gate.md` §3.1, "What the
smoke batch tunes it against"). **Nothing builds it** — grep for `referencePower` in `src/` and `tools/`
finds the tuning publisher, the planner's gate text and a throwaway timing probe
(`gk-core/tools/ActionTimingProbe/Program.cs`), none of which reads real content against the budget.

There is also no legal way to *apply* a tune. `gk-core/tools/tuning/publish.py`'s `--add-rung-power-budget`
refuses once the column exists (`publish.py:222-224`), and editing ten `rows[rung=N].powerBudgetMilli`
cells with `set` would break the one-scalar derivation the file's `_meta` promises.

## The measure

The budget is `powerBudgetMilli(r) = poolRolls(r) × referencePower × qPowerMilli(r) / 1000`
(`action-rungs.v2.json` `_meta.powerBudgetDerivation`). Solved for the scalar, each real action says
what `referencePower` it would need to sit exactly on budget:

```
impliedReferencePower(a) = realizedPowerMilli(a) × 1000 / (poolRolls(r) × qPowerMilli(r))
```

where `r` is the action's **authored** rung (the rung A-G1's check reads, `RpgStore.ActionCatalog.cs:105-109`)
and `realizedPowerMilli` is the price the check already computes, `ActorPowerCache.Compose` over the
container's fixed atoms (`RpgStore.ActionCatalog.cs:85-90`; `ContentValidation.cs:114`). This reads only
`poolRolls` and `qPowerMilli`, which v1 already carries, so the report works against whatever table the
server has loaded — no second table in the process, no new curve.

The distribution of that number per rung *is* the calibration: if the p-max over real content is below
the published scalar, no real action would be rejected; the gap says how much headroom the scalar has.

## Contract

1. **One pricing path.** The atom fetch + `ActorPowerCache.Compose` block in `BuildActionCatalog`
   (`RpgStore.ActionCatalog.cs:84-90`) moves into one private helper both the catalog build and the
   report call. The report must not price differently from the check it calibrates (SOLID S).
2. **Pure core.** `FusionRpg.Core.Actions.Rungs.BudgetCalibration.Read(IReadOnlyList<PricedAction>, RungTable)`
   (new) returns, per authored rung: `n`, `min`, nearest-rank `p50`, `p90`, `max` of
   `impliedReferencePower`, the rung's `poolRolls`/`qPowerMilli`/`powerBudgetMilli` (when loaded), and the
   ids above the loaded table's own implied scalar (when the column is loaded). `PricedAction` is
   `(ActionId, AuthoredRung, RealizedPowerMilli)`.
3. **Every action with a container is read**, including ones the budget would reject — the catalog
   build drops those (`RpgStore.ActionCatalog.cs:111-118`), which is exactly what must be measured.
4. **Read-only endpoint.** `GET /api/debug/action-budget-report` in `DebugEndpoints.cs`, labelled
   **RPG Server Debug** (`live-probe-standard.md`): it runs the real store read and the real pricing
   against real imported rows. It writes nothing and fabricates nothing.
5. **Retune in one edit.** `publish.py` gains `--reprice-rung-power-budget REF`: recomputes every row's
   `powerBudgetMilli` from its own `poolRolls`/`qPowerMilli` and `REF` (same arithmetic as
   `add_rung_power_budget`, `publish.py:205-240`), writes `_meta.referencePower = REF`, and refuses if any
   row lacks the column. `_meta.referencePowerUntuned` flips to `false` **only** with an explicit
   `--mark-tuned` flag, so "untuned" cannot be cleared by accident.
6. **The first reading tunes the scalar (R8, 2026-09-18).** The report also emits
   `recommendedReferencePower` = the **smallest** scalar at which no priced committed action exceeds its
   rung's budget: `max over actions of ceil(realizedPowerMilli × 1000 / (poolRolls × qPowerMilli))`.
   Ceiling division is exact against the publisher's floor division: `poolRolls × REF × q ≥ realized × 1000`
   implies `floor(poolRolls × REF × q / 1000) ≥ realized`. This rule is the technical reading of R8 plus
   ST5's contract 4 (*"activation never silently drops content nobody saw"*): it tunes the scalar to the
   real corpus without rejecting any content the owner has already accepted, and it makes the budget a
   ceiling for **future** content. The build then publishes, after ST3's v3 (map §5.1):

   ```powershell
   python gk-core/tools/tuning/publish.py action-rungs --label "R8 first calibration (<report file>)" `
     --reprice-rung-power-budget <recommendedReferencePower> --mark-tuned
   ```

   → `action-rungs.v4.json`, whose `_meta` names the report file committed under
   `docs/research/action-corpus/`. The change description lists the actions above the report's p90, so an
   outlier that drags the scalar up is visible, not silent. Leaving 1000 after the reading is the standing
   risk's trigger 1 and is not an option (R8). A different value is a later, ordinary tuning publish.

## Tunables

None new. Reads `rows[].poolRolls`, `rows[].qPowerMilli`, `rows[].powerBudgetMilli`,
`_meta.referencePower` from `data/tuning/action-rungs.v{n}.json`. The report's percentiles (p50, p90) are
fixed report columns, not balance numbers — structural, named constants with a comment.

## Numeric types

`realizedPowerMilli` is `long` (`RpgStore.ActionCatalog.cs:90`). The implied scalar is computed in
`checked` `long`: widen before multiplying (`(long)realized * 1000`), one division last by
`(long)poolRolls * qPowerMilli`. At the shipped table the divisor is at most `3 × 12407` and the
numerator stays far below `long` range for any reachable realized power (rung 10's budget is 37,221;
`ssot-power-scale.md:889`). A `poolRolls` or `qPowerMilli` of 0 throws naming the rung — the loader
already refuses non-positive `qPowerMilli` (`RungTableLoader.cs:70-71`). Percentiles are nearest-rank on
sorted `long`s — no interpolation, no floating point needed (floating point would be allowed; it is not
needed).

## Seedsmith / generator

**No generator change.** Pricing is C#; the report reads the catalog the server imported from the
committed seed. Model stages are not run. The only Python change is `gk-core/tools/tuning/publish.py`, which is
the tuning publisher, not seedsmith.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BudgetCalibration"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCatalog"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ActionBudgetReport"
python -m pytest gk-core/tools/tuning -q
python gk-core/scripts/guard-dal.py
# reading, against the running dev server:
curl.exe -s http://127.0.0.1:5088/api/debug/action-budget-report > docs\research\action-corpus\_budget-<date>.json
```

## Project structure

```
gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs        (new, pure)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionCatalog.cs          (shared pricing helper + ListActionPricing)
gk-core/src/FusionRpg.Server/DebugEndpoints.cs                       (GET /api/debug/action-budget-report)
gk-core/tools/tuning/publish.py                                      (--reprice-rung-power-budget, --mark-tuned)
gk-core/tests/FusionRpg.Core.Tests/Actions/Rungs/BudgetCalibrationTests.cs
gk-core/tests/FusionRpg.Data.Tests/…ActionPricingTests.cs
gk-core/tests/FusionRpg.Server.Tests/…ActionBudgetReportTests.cs
gk-core/tools/tuning/test_publish_reprice.py
gk-core/data/tuning/action-rungs.v4.json                             (published by the tool, R8 — never hand-edited)
docs/research/action-corpus/_budget-<date>.json              (the first report, cited by v4's _meta)
```

## Code style

```csharp
/// <summary>ST4: the referencePower an action would need to sit exactly on its authored rung's budget.
/// Inverts action-rungs.v{n}.json's own derivation -- reads poolRolls and qPowerMilli only, so it is not
/// a new curve and works against any loaded table version.</summary>
static long ImpliedReferencePower(long realizedPowerMilli, RungRow row) => checked(
    realizedPowerMilli * PowerMath.One / ((long)row.PoolRolls * row.QPowerMilli));
```

## Testing strategy

| # | Test | Proves |
|---|---|---|
| 1 | A priced action whose realized power equals its rung's budget at `REF` reads implied `REF` | The inversion matches the published derivation |
| 2 | Reconciliation: Σ per-rung `n` equals the number of priced actions; each action id appears once | Contract 2, 3 (reconciliation, not a count) |
| 3 | `min ≤ p50 ≤ p90 ≤ max` on every rung with `n > 0`; a rung with `n = 0` reports no percentiles rather than zeros | Report shape |
| 4 | An action the budget rejects still appears in the report | Contract 3 |
| 5 | **Planted violation:** a second pricing function substituted in the report makes a test comparing report realized power to the catalog check's realized power fail | Contract 1 |
| 6 | Arithmetic throws on `long` overflow and on a zero divisor | Numeric rule |
| 7 | Endpoint returns the report for a real store seeded through the real import path; it performs no write | Contract 4 |
| 8 | `publish.py --reprice-rung-power-budget 800` writes v{n+1} whose every row equals the derivation at 800, `_meta.referencePower == 800`, `referencePowerUntuned` still `true`; with `--mark-tuned` it is `false`; on a table without the column it refuses | Contract 5 |
| 9 | Repricing a fixture table at the report's `recommendedReferencePower` and re-running the budget check over the same priced actions rejects **none** of them; repricing at that value − 1 rejects at least the action that set the max | Contract 6 (a property of the rule, never a pinned value) |

No test pins a percentile, an action count, or the current `referencePower` value (ruling 3's trigger
2: *"a test pinning it"*).

## Boundaries

- **Always:** price through the one helper; report every containered action; keep "untuned" until a
  deliberate `--mark-tuned`.
- **Ask first:** publishing the first retune at any value other than the report's
  `recommendedReferencePower` (R8 fixes the source of the value; this module fixes the rule).
- **Never:** clamp or drop content from the report; add a canary that fails the build on a neutral
  scalar (the ideal records the canary was offered and not taken); read the report's numbers into a test
  or a second system (trigger 2).

## Success criteria

1. A reading of implied `referencePower` per rung exists for the real imported catalog.
2. The report and A-G1's check price identically, by construction.
3. Retuning the scalar is one publish call, and "untuned" is cleared only on purpose.
4. `action-rungs.v4.json` exists, published at the first report's `recommendedReferencePower` with
   `--mark-tuned`, before ST5 lands (R8).

## Self-audit (debate pass)

- *"Isn't this the canary the owner declined?"* No. A canary fails something when the scalar stays
  neutral. This is a report and a publish path; nothing fails on its numbers.
- *"Why authored rung and not effective?"* The budget is a content ceiling checked at catalog build on
  the authored rung (`RpgStore.ActionCatalog.cs:108`); calibrating against a different rung would tune a
  different check.
- *"Debug endpoint vs a console tool?"* The pricing needs the imported catalog and the atom store; the
  server already has both, and the live-probe standard allows an RPG Server Debug read that runs the real
  path. A console tool would need its own store bootstrap — a second way to build the same state.

## Open questions

None. R8 answered whether this reading tunes the scalar: it does, before ST5.
