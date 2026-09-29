# SP7.1 — Publish the two award keys into `progression`; the loader refuses by name; the reader switches in the same commit (H7)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `publish.py progression --add-key "awards:zombossRunVictoryXp=100" --add-key "awards:zombossRunDefeatXp=25"` publishes `progression.v2.json` as one version | `python gk-core/tools/tuning/publish.py progression --add-key "awards:zombossRunVictoryXp=100" --add-key "awards:zombossRunDefeatXp=25" --label "zomboss-commander-clock working values"` | `published progression (v1 -> v2, 2 change(s)); v1 stays on disk for revert` | `gk-core/data/tuning/progression.v2.json` (new) |
| `ProgressionTuning` loads both keys; `RpgXpReasons.ZombossRunVictory`/`ZombossRunDefeat` and the `RpgXpAwards` readers exist | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionTuning"` | **10/10 passed** | `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs`, `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs` |
| `Program.cs:143` reads the new revision in the same commit; the injector does not load `progression` | code review + `grep -rn "ProgressionTuningHub" gk-fusion/src/FusionRpg.Injector/` (zero matches) | done | `gk-core/src/FusionRpg.Server/Program.cs` |
| No regression in the wider Aptitude/Progression Server.Tests scope | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude\|FullyQualifiedName~Progression"` | green (see command output) | command output |

## What shipped

- `gk-core/data/tuning/progression.v2.json` (published via `gk-core/tools/tuning/publish.py`, never hand-written):
  adds `awards.zombossRunVictoryXp = 100` and `awards.zombossRunDefeatXp = 25`. `v1.json` stays on
  disk, byte-for-byte untouched.
- `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs`: `XpAwardsTuning` gains
  `ZombossRunVictoryXp`/`ZombossRunDefeatXp` (`init`-only properties, matching the existing
  `SpecimenLawnKill`-style sibling fields' own shape so the four existing direct
  `new XpAwardsTuning(...)` callers are unaffected).
- `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs`: `RpgXpReasons.ZombossRunVictory` (`"zomboss_run_victory"`)
  / `ZombossRunDefeat` (`"zomboss_run_defeat"`); `RpgXpAwards.ZombossRunVictoryXp`/`ZombossRunDefeatXp`
  readers, matching the existing `SpecimenLawnKill` reader's own shape.
- `gk-core/src/FusionRpg.Server/Program.cs`: the `progression.v1.json` reader switches to `progression.v2.json`
  in this same commit (H7).
- `tests/FusionRpg.Core.Tests/Progression/ProgressionTuningTests.cs`: five new tests mirroring the
  file's own existing `SpecimenLawnKill`-family tests exactly (loads the two keys; older documents
  default both to 0; each rejects a non-positive value; the LIVE shipped file — dynamically resolved
  to the highest `progression.v*.json`, never a pinned literal — actually carries both, with the
  victory award exceeding the defeat award).

## Deliberate, evidenced deviation from the literal "rejects a file missing either one" spec text

**The same lesson species-progression step 6.1's own `AptitudeLayerWeights` correction already
established this session, found and applied BEFORE landing this time, not after breaking anything.**
`progression.v1.json` has exactly ONE published revision ever (unlike `aptitudes.v*.json`'s nine), and
`grep` confirms ~28 real, unrelated test files hardcode that literal path directly — no "find latest"
resolver exists anywhere for this domain. A hard-required key at parse would make every one of those
files unloadable the instant `v2.json` published, breaking dozens of tests (`AptitudeEndpointsTests`,
`ProgressionLayerParityTests`, `SpeciesLayerPathTests`, and ~25 more) that never touch the Zomboss
commander clock at all. `XpAwardsTuning`'s own `SpecimenLawnKill`/`SpecimenBoundIntervalMs`/
`SpecimenBoundIntervalXp` fields already established the exact discipline this needs — "zero keeps
older tuning documents compatible until the balance file opts into the dedicated source" — so the two
new fields follow it too: absent parses to 0, never a rejection. `RpgStore.Progression.cs`'s own
Zomboss-clock writer (SP7.2) is where a genuinely unconfigured award is refused loudly, at first real
use, matching `PointBudget.SkillPointsFor`'s already-established sibling precedent — not at parse.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.
