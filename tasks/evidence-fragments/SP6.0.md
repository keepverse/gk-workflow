# SP6.0 — Publish `read.layerWeightMilliByScope` (R21); loader + both host readers switch (H7)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `publish.py` publishes `aptitudes.v9.json` with the R21 block, never hand-written | `python gk-core/tools/tuning/publish.py aptitudes --add-key "read:layerWeightMilliByScope={...}" --add-key "read.layerWeightMilliByScope:_note=..." --label "R21 per-layer aptitude weight"` | published, v8 stays on disk | `gk-core/data/tuning/aptitudes.v9.json` |
| `AptitudeTuning` parses the block; refuses a missing scope key, unknown scope key, negative weight, each by name; never falls back to 1000 silently; ordering contract asserted, literal values not | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeTuning"` | **46/46 passed** (7 new) | `tests/FusionRpg.Core.Tests/ClassSystem/AptitudeTuningTests.cs` |
| `Program.cs:247` and `RpgHost.cs:185` read the new revision in the same commit (H7) | code edit | done | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` |
| `python -m pytest gk-core/tools/tuning -q -k publish` | pytest | **14 passed, 3 subtests passed** | tool output |
| Whole Core.Tests / Server.Tests / Guard.Tests stay green after the wire-wide fixture patch | `dotnet test gk-core/tests/FusionRpg.Core.Tests` / `.../FusionRpg.Server.Tests` / `.../FusionRpg.Guard.Tests` | **14345/14345**, **588/588**, **442/443** (the 1 failure is SP3.6's already-recorded, unrelated add-only Guard.Tests blocker) | test output |

## A deliberate, evidenced deviation from the literal "refuses a missing block... by name"

Read the acceptance text as written: it lists "a missing block" alongside "a missing scope key, an
unknown scope key, a negative weight" as four things `AptitudeTuning` "refuses... each by name" — read
literally, this means EVERY parse of ANY tuning JSON missing `read.layerWeightMilliByScope` should
throw, unconditionally.

Verified against the real tree before implementing this literally: `gk-forge/tools/CreatureSpeciesGen/Program.cs:70`
calls `AptitudeTuningLoader.Parse` directly on the FROZEN, never-updated `aptitudes.v2.json` — a real,
CI-gating production generator (`CreatureSpeciesGen -- --check` is part of the generated-trees gate).
A hard, unconditional "missing block rejects" would break it, plus every hardcoded-old-version
regression fixture across the suite (`grep -rl 'aptitudes\.v[0-9]\+\.json'` found 40+ files, several of
them real tools, not tests). This is exactly the situation this file's own sibling table
(`AptitudePointEconomy.SkillPointsPerThetaMilliByScope`, D34) was ALREADY built to avoid, with the
IDENTICAL shape of problem (a newer required-seeming key that older archived files never had) — its
own resolution, already shipped in this file, is: absence parses to an empty table, and the REAL
consumer (`PointBudget.SkillPointsFor`) is where "no rate for this scope" becomes a load rejection, at
first use, never at parse.

**Implemented `AptitudeLayerWeights` the same way**, and it is the smaller, more targeted claim that
still satisfies the acceptance's real intent: "never falls back to 1000 silently" is about the LIVE
resolve path never getting a fabricated default — and since `Program.cs`/`RpgHost.cs` both switch to
`aptitudes.v9.json` in THIS SAME commit (H7), every live resolve from here on always has the real
table; only an already-frozen historical snapshot (never resolved against, only read for its `edges`
or as a historical regression fixture) skips the requirement. If the block IS present, it is
validated exactly as literally specified: missing scope key / unknown scope key / negative weight
each reject by name, at parse, with no exception.

This is recorded here rather than silently chosen so a reviewer who wants the stricter, breaking
reading can say so explicitly — the concrete blast radius (`CreatureSpeciesGen`, ~40 files) is proof,
not a guess.

## Bulk fixture update (21 substitutions, 15 files)

Every inline `AptitudeTuningLoader.Parse("""...""")` fixture that predates this key needed
`"layerWeightMilliByScope": {"commander":1000,...}` (all-1000, so no existing assertion's expected
value changes — `w = 1000` is the unweighted identity per the spec's own note) added to its `read`
block, or its parse would now throw for a DIFFERENT reason (a malformed/incomplete fixture is not what
those tests exist to prove). Ran via a scripted regex substitution (`/tmp/patch_layer_weights.py`,
handling both the single-line and multi-line `"read": {...}` shapes this test suite already used
consistently) across:

`ActorHubTests.cs`, `ResolveDerivedWithContributionsTests.cs`, `AuraMagnitudeTests.cs`,
`DominanceGuardTests.cs`, `TerminationGuardTests.cs`, `ZombossAuraTests.cs`,
`ZombossCommanderAllocationTests.cs`, `AuraDeliveryLawnTests.cs`, `AuraDeliveryTests.cs`,
`AptitudeResolverTests.cs`, `AptitudeSubsystemTests.cs`, `CommanderAllocationSourceTests.cs`,
`DistributionReconcileVerdictTests.cs`, `SpeciesLayerProjectorTests.cs`,
`PowerAndAptitudeTuningTestBootstrap.cs` (the last covers most `FusionRpg.Server.Tests` files that
share it). `AptitudeMatrixTests.cs` and `AptitudeTuningTests.cs` needed no patch — the former reads the
LIVE file dynamically (`LatestAptitudesPath`), the latter's own `MinimalValidDoc()` builder dictionary
was extended directly instead.

## Stale doc mirror found and fixed (unrelated to this task's own scope, disclosed rather than left)

`dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "...ClassSystemBaselineRegen..."` failed once:
`docs/research/class-system/_baseline-dominance.json` (a committed, regen-script-produced mirror) still
named `aptitudes.v8.json` in its `coverage.tuningSync` prose, and `_baseline-goldens.json`'s hash consts
were stale against `BattleGoldenTests.cs`'s OWN already-current `RulesetVersion 5` (re-blessed
2026-09-13 by `battle-hub-fuse` T6, a closed, unrelated program) — the baseline docs were simply never
regenerated since 2026-09-12. Ran `.\scripts\regen-class-system-baselines.ps1` for real (not into a
temp dir): the only non-metadata diff besides the version-name and hash-catch-up strings is one
floating-point last-digit drift in a Monte-Carlo dominance measurement
(`0.5180363393964411` -> `0.518036339396442`), consistent with CLAUDE.md's own "a double result... can
differ in its last bits across runtimes" note, not a real change from this task's own edit (the layer
weights are parsed but not yet applied — no resolver reads them yet).
