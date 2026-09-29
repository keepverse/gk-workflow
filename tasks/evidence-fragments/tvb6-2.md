# TVB6.2 — after-reading at the merged head (no owner rows yet)

The after-reading TVB6.5 asked for, measured at `2a270ad81` (features/mega-merge merged, split 33 of
68 projects). **No narrowing exists yet, and the rows TVB6.2 would name cannot be named honestly:**

| Path | Plan at this head |
|---|---|
| `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs` | `battle-effect-math` (focused) - unchanged |
| `gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs` | `core-fallback` (module) |
| `gk-core/src/FusionRpg.Core/Effects/CombatHitEmitPolicy.cs` | `core-fallback` (module) |
| `gk-core/src/FusionRpg.Core/Effects/DamageFx.cs` | `core-fallback` (module) |
| `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs` | `core-fallback` (module) |
| guards selected | `battle-responsibility`, `funnel-delta` |
| test check | `test: core` - the whole Core group (34 members) |

Command: `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths
'gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs','gk-core/src/FusionRpg.Core/Effects/EffectBag.cs',
'gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs','gk-core/src/FusionRpg.Core/Effects/CombatHitEmitPolicy.cs',
'gk-core/src/FusionRpg.Core/Effects/DamageFx.cs' -AllowUnscoped -PlanOnly"`

## Why no rows

TVB6.2's owner rows must come from the production map ("never by name alone"),
`dotnet run --project gk-core/tools/TestSplitAnalyzer -- --production-map --project
gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --test-projects tests`, and that map still under-reports
(**TVB-F18**: every scanned compilation fails to bind framework types - first errors are CS0246 - while
output-dir references resolve; five reference-source hypotheses disproved, the next move is to
instrument the compilation). The split has also landed only 33 of 68 projects, so most areas' tests
still sit in the residual.

## Rows this task records

- **TVB6.2** - not closed: after-reading printed above shows **no** group narrower than `core`; blocked on
  TVB-F18 (in lane, needs an instrumented run) and on the split finishing.
- **TVB6.3/TVB6.4** - chained behind TVB6.2 for the same reason; no re-key or orphan boundary is written
  from an under-reporting map.
- **TVB-F17** - still the erratum for K-T3/K-T4: their named test file is
  `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`, outside this lane's fence.

No commit for owner rows: there are none to make yet; this fragment rides the merge commit's branch.

---

> **Superseded 2026-09-23 by the section below.** The reading above was taken while TVB-F18 was
> open and the split stood at 33/68; both are now closed (0 compilation errors, 67/68 applied), so the
> "no rows" conclusion above no longer holds.

# TVB6.2 (K1) — per-area Core production owners from the production map

Read at `d481597a0` (the commit that made the map usable), split 67/68, lane `tvb60`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the evidence | `TestSplitAnalyzer --project gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --production-map --configuration Release --format md` | 35 areas, **0 test projects with compilation errors**; two runs byte-identical | `tasks/evidence-fragments/tvb-f18.md` |
| area owners | the map's per-area project sets written into the registry | **35 areas owned**; `core-area-*` rows 8 → **32**, plus `notify-core-domain`, `core-server-clock` and `core-narrative` re-pointed at their area's group | `gk-core/scripts/verification-boundaries.v1.json` |
| registry after | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK`; boundaries **438 → 462**, projects **106 → 137** (31 new C7 groups) | — |
| K-T3 (one path per owner) | `verify-change.ps1 -Paths <p> -PlanOnly` | `Lawn/MoveQueue.cs -> core-area-lawn (module)`, `test: core-area-lawn-owners` (2 projects — was `core-fallback`, 68); `Events/EventDrain.cs -> core-area-events (module)`, `test: core-events` (1); `Effects/DamageFx.cs -> core-area-effects (module)` (32); `Stats/ModifierBag.cs -> core-area-stats (module)` (29) | — |
| K-T4 (unmapped Core path) | `verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/SimModels.cs -PlanOnly` | `core-fallback (module)`, `test: core` with all 68 members — a root file under no area still runs everything | — |
| focused still wins | `verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Effects/EffectBag.cs -PlanOnly` | `battle-effect-math (focused)`, `test: core-residual` — specificity is unchanged by the new module rows | — |
| `-Report` after | `guard-verification-boundaries.py --report` | orphan `VerificationId` traits **8** (was 7 before K1 — no `core.*` among them); 24 inputs at level `full` | — |

`-Report` before, from the record rather than a re-run (the predecessor's ledger, 2026-09-22): orphans
**7**, `none core.*`. The area rows that existed before K1 were derived from the UNDER-reporting map, so
8 of them named a project narrower than the referencing set (`core-area-activity` → `core-residual` while
the map now shows 5 projects) — the spec's "never narrow a boundary below the set of projects that
reference the area" makes that a defect, and each was widened to the map's exact set in this change.

Three areas already had an owner with the same `gk-core/src/FusionRpg.Core/<A>/**` pattern, so the guard's
ambiguity rule (`ambiguous owner pattern`) refused a second row: `notify-core-domain` (`Notify`),
`core-server-clock` (`Time`, already correct) and `core-narrative` (`Narrative`). Their `project` was
re-pointed at the area's group instead of adding a duplicate.

The group sizes are readings, not constants: Events/Onboarding/Settings/Time 1, Diagnostics/Lawn/Scope 2
… Stats 29, Effects 32. `core-fallback` still owns `gk-core/src/FusionRpg.Core/**` on the full `core` group.