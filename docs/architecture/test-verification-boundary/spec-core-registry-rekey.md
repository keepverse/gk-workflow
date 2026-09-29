# Spec: `core-registry-rekey`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
[`registry-contract`](spec-registry-contract.md) (groups, derived levels, orphan reading),
[`core-split-wiring`](spec-core-split-wiring.md) (the split has landed) · closes map gaps G11, G12,
and the Core half of R-TV2 that the ideal deferred ("R-TV2 execution — deliberately not done").

## Objective

R-TV2 deepened Data, Server and Launcher; Core was deliberately left because every focused boundary
names the project that owns its `VerificationId`, and the split was about to change those projects
(ideal, "R-TV2 execution"). Once the split has landed, this module does the Core half:

1. **Per-area production owners.** Today 969 of Core's production files resolve to `core-fallback`
   (`-Report` reading, map §2) and run **every** Core test. After the split, a change under
   `gk-core/src/FusionRpg.Core/<Area>/**` can run the one test project that owns that area.
2. **Re-key the focused `core.*` boundaries that already exist** (`battle-effect-math`,
   `elemental-resolver`, `core-lawn-attrition`, `core-creature-catalog-generator`,
   `core-creature-corpus-dump`, `tools-combat-sim`, `tools-prove-predictor`) to the project(s) now
   holding their traits.
3. **Give the orphan `core.*` traits boundaries** where a production owner exists
   (`core.battle-mode-parity`, `core.kill-attribution`, `core.siege-estimator-parity`,
   `core.species-term-compose`, `core.species-passive-atoms`, `core.advanced-effect-clock`,
   `core.vocabulary-single-declaration` — map G12).

**User:** every contributor changing Core production code.

## Design

### K1 — per-area owners, evidence-based

For each new Core test project `P` holding area `A`, add an owner boundary
`gk-core/src/FusionRpg.Core/<A>/**` → `P` (module level) **only if** the analyzer report shows that the tests
exercising `gk-core/src/FusionRpg.Core/<A>/**` live in `P` and nowhere else. The evidence is the analyzer's
required-assembly/symbol data, re-run against the split tree: which projects reference symbols
declared under `gk-core/src/FusionRpg.Core/<A>/`. If tests in several projects reference area `A`, its owner
is a **group** of exactly those projects (`registry-contract` C7), not the single area-named project.
Mapping `Combat/**` to `Combat.Tests` because the names match would be the "boundary by coincidence"
the ideal warns about.

This needs one analyzer addition: a `--production-map` mode that, for each `gk-core/src/FusionRpg.Core/<dir>`,
lists the test projects referencing its symbols. It lives in `gk-core/tools/TestSplitAnalyzer` (read-only,
same compilation model).

`core-fallback` stays as the residual owner of `gk-core/src/FusionRpg.Core/**` on the full `core` group — a
file under no mapped area still runs everything.

### K2 — re-keying existing focused boundaries

A focused boundary's `project` becomes the project (or smallest group) whose directory holds its trait.
`core.battle-effect-math` lives in both `Combat/OwnerElementFallbackTests.cs` and
`Battle/BattleEffectMathTests.cs`; if those land in different projects its boundary names a group of
the two, and group focused selection runs only members holding the trait (`registry-contract` C7).
Its `paths` (`verification-boundaries.v1.json:592-610`) name two test files whose locations move. Those
path strings, and every other exact Core test path in the registry, are **already** rewritten by
`core-split-wiring` in the increment that moved them (`registry-contract` C8 fails the guard
otherwise). Until this module runs, the boundary still names the `core` group, and group focused
selection finds the trait wherever it moved, so nothing verifies less in between. This module only
narrows `project`.

### K3 — orphan traits

For each orphan, add a focused boundary when a production file exists whose change that trait's
tests are the direct proof of (read the test class to find it; e.g. `core.siege-estimator-parity` →
the siege estimator source). An orphan with no such file stays an orphan and remains in the `-Report`
reading; `server.lawn-quick-start` is the precedent (ideal, "R-TV2 execution").

## Commands

```powershell
dotnet run --project tools\TestSplitAnalyzer -c Release -- --project <each Core test csproj> --production-map --format md
python gk-core/scripts/guard-verification-boundaries.py --report        # depth + orphan readings, before and after
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/<Area>/<File>.cs -PlanOnly -AllowUnscoped
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/tools/TestSplitAnalyzer/ProductionMap.cs` | (new) `--production-map` |
| `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/` | production-map cases |
| `gk-core/scripts/verification-boundaries.v1.json` | K1 owners, K2 re-keys, K3 boundaries |
| `docs/architecture/test-verification-boundary-ideal.md` | "R-TV2 execution": Core half done (one line) |

## Code style

```jsonc
{ "id": "core-world", "kind": "owner", "paths": ["gk-core/src/FusionRpg.Core/World/**"],
  "project": "core-world", "level": "module", "guards": [] }
```

## Testing

| # | Case | Asserts |
|---|---|---|
| K-T1 | analyzer fixture: area symbols referenced from two synthetic projects | production map lists both |
| K-T2 | real registry after K1–K3 | guard passes; every re-keyed `VerificationId` has its trait in ≥1 member of its project/group |
| K-T3 | planner on one file per new area owner | plans that owner's project/group only |
| K-T4 | planner on an unmapped `gk-core/src/FusionRpg.Core/` path | plans the full `core` group (never less than before) |

The `-Report` before/after numbers go in the commit body as readings. No test pins them.

## Boundaries

- **Always:** derive every area owner from the production map; keep `core-fallback` on the full group;
  keep every guard a re-keyed boundary carried (`battle-effect-math` keeps `battle-responsibility` and
  `funnel-delta`).
- **Ask first:** none.
- **Never:** map an area to a project by name alone; narrow a boundary below the set of projects that
  reference the area; add a focused boundary for an orphan without a production file its tests directly prove.

## Success criteria

- [ ] A one-area Core production change plans that area's project (or group), not every Core test.
- [ ] Every pre-existing `core.*` focused boundary still selects its tests after the split.
- [ ] Orphans with a production owner have boundaries; the rest appear in `-Report`.
- [ ] K-T1–K-T4 green, verified with `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,<changed gk-core/tools/TestSplitAnalyzer paths> -Session <id>`.

## Open questions

None.
