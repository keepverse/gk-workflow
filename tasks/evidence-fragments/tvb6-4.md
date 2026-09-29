# TVB6.4 — K3 orphan boundaries (2 of 6 landed)

K3: give an orphan `core.*` trait a focused boundary when a production file exists whose change the
trait's tests are the direct proof of, found by reading the test class. Two orphans are decisive at this
head and are now boundaries; four need the class body read and stay in the `-Report` reading.

| Orphan | Production file (evidence) | Boundary |
|---|---|---|
| `core.advanced-effect-clock` | `gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs` — the only exact-name declaration the test class references | `core-advanced-effect-clock` (focused, project `core`) |
| `core.kill-attribution` | `gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs` — same | `core-kill-attribution` (focused, project `core`) |

Command: `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths
'gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs','gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs'
-AllowUnscoped -PlanOnly"` now prints, where it printed `core-fallback (module)` before:

```
gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs -> core-kill-attribution (focused)
gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs -> core-advanced-effect-clock (focused)
test: core core.advanced-effect-clock
test: core core.kill-attribution
```

`guard-verification-boundaries.py` -> `VERIFICATION BOUNDARY GUARD OK` (356 boundaries; the guard's own
VerificationId check proves each trait exists in a member of `core`).

## Still open (`-Report` reading, no boundary written)

`core.battle-mode-parity` (BattleTriggerCoverageTests), `core.siege-estimator-parity`
(SiegeEstimatorParityTests), `core.species-term-compose` (SpeciesTermReachesComposeTests),
`core.vocabulary-single-declaration` (SingleDeclarationTests) — each references several plausible
production files (e.g. BattleEngine vs BattleRunState; ElementTable vs StatusCategoryRegistry), and the
choice needs the class body read. None of the six test files cites its production file by `.cs` path, so
inference from citations is not available.

The ideal's "Core half done" line is deliberately NOT written: the Core half includes K1 (still gated by
TVB-F18), so that sentence would be false today.

## Second pass (split 43/68, merged head 37ff59445)

Three more orphans landed, each from its own test class's summary:

| Orphan | Production file(s) | Test | Boundary |
|---|---|---|---|
| `core.battle-mode-parity` | `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs`, `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKind.cs` | `BattleTriggerCoverageTests.cs` (its summary names `BasicAttack` as what raised the triggers) | `core-battle-mode-parity` |
| `core.species-term-compose` | `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs`, `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs` | `SpeciesTermReachesComposeTests.cs` | `core-species-term-compose` |
| `core.vocabulary-single-declaration` | `gk-core/src/FusionRpg.Core/Combat/Element/ElementTable.cs`, `gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs` | `SingleDeclarationTests.cs` (its `using` set is exactly these two vocabularies) | `core-vocabulary-single-declaration` |

Guard: `VERIFICATION BOUNDARY GUARD OK` at **369 boundaries**. `-PlanOnly` on the production paths now
prints `-> core-vocabulary-single-declaration (focused)` (and the same shape for the other two) plus
`test: core core.battle-mode-parity` / `core.species-term-compose` / `core.vocabulary-single-declaration`.

**Still open:** `core.siege-estimator-parity` - the split at this head has no `*stimat*` file under
`gk-core/src/FusionRpg.Core/Battle/Siege/`, so the estimator's declaring file needs one more search before a
boundary can name it (K3: "the rest stay in the `-Report` reading").

**TVB6.3 at this head:** all five `core.*` traits are still under `gk-core/tests/FusionRpg.Core.Tests/**`
(`Battle/`, `Combat/`, `Creatures/`) at 43/68, so the K2 re-key remains a no-op (see tvb6-3.md).

## Third pass — K3 complete (all six orphans owned)

`core.siege-estimator-parity` -> `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeExpectedDamage.cs` + its test
(`SiegeEstimatorParityTests.cs`). The first search looked for `*stimat*` under `Battle/Siege/` and missed
it because the type is `SiegeExpectedDamage`; the declaring file is the one the test's own remarks name
("`SiegeExpectedDamage` computed `power - effectiveDefense`..."). Guard: **370 boundaries**, OK.

So all six orphan `core.*` traits now select a VerificationId instead of `core-fallback`:
advanced-effect-clock, battle-mode-parity, kill-attribution, siege-estimator-parity,
species-term-compose, vocabulary-single-declaration.

The ideal's "Core half done" line stays unwritten until K1 lands (TVB-F18), because that sentence covers
the whole Core half, not just K3.

## TVB-F18 instrumentation (measured, not guessed)

`--probe-references` (a temporary probe, since removed - see the ledger) printed:

```
TPA runtime type = String
TPA entries = 172; first exists = True
loaded assemblies = 13
corelib location = C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.31\System.Private.CoreLib.dll
```

So the trusted-platform-assembly list is present, is a `string`, has 172 entries and they exist - the
framework references ARE supplied. TVB-F18's cause is therefore downstream of the reference set (the
compilation binds nothing even with the right references), which rules out the whole
"missing reference source" family of hypotheses for good and points at the compilation itself.
