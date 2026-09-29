# SP7.2 — Every resolved lawn run advances its save's Zomboss commander level exactly once, by outcome

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A human `defeat` gives `zombossRunVictoryXp`; a human `victory` gives `zombossRunDefeatXp`; no/unknown result or `pvzGame==false` gives nothing | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderClock"` | **8/8 passed** | `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs` |
| Identity (R3): the run's OWN save's Zomboss empire, never a human row/literal id; two saves advance two different levels; no Zomboss empire row awards nothing, creates no row | same run, `Two_saves_advance_two_different_levels` / `A_save_with_no_seeded_Zomboss_empire_awards_nothing_and_creates_no_row` | pass | same file |
| Replay-safe (dedupe `zomboss-run:{runId}`) | same run, `Replayed_MatchEnded_never_double_pays` | pass | same file |
| Level-up follows the `player` curve, asserted against the curve function | same run, `A_human_defeat_gives_Zombosss_commander_the_run_victory_award` (asserts `RpgXpCurve.XpToNext(Player,1) == RpgXpAwards.ZombossRunVictoryXp`, never a literal level) | pass | same file |
| No regression in the wider progression scope | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Progression"` | **20/20 passed** | command output |
| `guard-dal.ps1` (SQL only inside `FusionRpg.Data`) | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` | command output |
| Determinism of the shared static tuning bootstrap this task extends (extra rigor: process-wide state) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Progression\|FullyQualifiedName~UniqueActorStore"` run twice in a row | **58/58 both times** | command output |

## What shipped

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`: `ApplyRpgProgressionFromActivityUnlocked` gains a
  sibling block (after the species run-completion term) that, for a `MatchEnded` fact with `pvzGame`
  true and a real `runId`, calls the new `ApplyZombossCommanderClockUnlocked(db, save, runId, t,
  result, factId)`. That method:
  - normalizes `result` (`PvzActivityKinds.NormalizeMatchResult`) and maps `defeat` →
    `RpgXpAwards.ZombossRunVictoryXp`/`RpgXpReasons.ZombossRunVictory`, `victory` →
    `RpgXpAwards.ZombossRunDefeatXp`/`RpgXpReasons.ZombossRunDefeat`, anything else → nothing;
  - checks `rpg_save_empires` for a real `zomboss` row of THIS save before writing anything — a save
    with none awards nothing and creates no row on the fly (mirrors `AppendSpeciesModUnlocked`'s own
    check against the same table);
  - writes through the existing `TryApplyXpUnlocked(db, EmpireRef(save, EmpireId.Zomboss),
    RpgActorKinds.Player, 0, runId, t, delta, reason, "zomboss-run:{runId}", factId, null)` — the SAME
    write path every other award already uses, so replay-dedupe, the `player`-kind level curve, and
    the ledger/actor-progression tables are all shared, not reimplemented.
- `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs` (new, 8 tests): defeat award, victory
  (consolation) award, no-result, unknown-result, web-mode (`pvzGame=false`, driven through the real
  `InsertEvent`/`match.result` capture path since `AppendPvzActivityFact` always posts `pvzGame=true`),
  replay-safety, two-saves-two-levels (R3), and the no-seeded-Zomboss-empire case (row deleted from
  `rpg_save_empires` via the store's own hot connection, never a hand-built fixture).
- `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs`: `DefaultProgression.Awards` gains
  `ZombossRunVictoryXp = 100, ZombossRunDefeatXp = 25` (matching the real shipped
  `progression.v2.json`) — required because this module initializer configures `ProgressionTuningHub`
  ONCE, process-wide, for the whole `FusionRpg.Data.Tests` assembly; without it every test in the
  assembly would see `RpgXpAwards.ZombossRunVictoryXp/DefeatXp == 0` (the SP7.1 absence-tolerant
  default), and `ApplyZombossCommanderClockUnlocked`'s own `if (delta <= 0) return;` would silently
  never fire, making the new writer untestable.

## Correction of SP7.1's own doc comment (checked against evidence, not left as written)

SP7.1's `XpAwardsTuning.ZombossRunVictoryXp` doc comment (already committed) said the "first use"
refusal for a genuinely unconfigured/zeroed award would be a loud THROW, naming
`PointBudget.SkillPointsFor`'s precedent. Before implementing SP7.2's writer, I checked that claim
against this exact tuning class's OWN established consumers
(`AwardUniqueLawnKillUnlocked`/`AwardUniqueLawnDurationUnlocked` in `RpgStore.UniqueActors.cs`, which
read `RpgXpAwards.SpecimenLawnKill`/`SpecimenBoundIntervalMs`/`SpecimenBoundIntervalXp`) and found they
already do `if (delta <= 0) return;` — a SILENT skip, never a throw. `PointBudget.SkillPointsFor`'s
absence signal is a missing dictionary key (a structurally different condition); this tuning class's
own sibling precedent is the zeroed-scalar skip. Implementing the throwing version would have broken
every OTHER Data.Tests test that posts a `MatchEnded` "defeat"/"victory" fact without configuring the
new fields (confirmed: `ContractTuningTestBootstrap`'s own pre-this-task `DefaultProgression` omitted
them, and `SpeciesProgressionTests`'s `RunCompletion_*` tests post exactly such facts) — the SAME
"hard-reject breaks unrelated callers" mistake this session already caught once for
`AptitudeLayerWeights` (step 6.1) and once for SP7.1's own parse-time field. Corrected both
`ProgressionTuning.cs`'s doc comment and the actual writer to the silent-skip precedent BEFORE
shipping, not after a test failure exposed it.

## Confirmed pre-existing, unrelated flake (not caused by this task)

A full, unfiltered `dotnet test gk-core/tests/FusionRpg.Data.Tests` run (11m19s) showed 1 failure
(`CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree_succeeds_and_writes_a_real_store`,
"11 species stale against gk-data/packs/fusion/data/generated/creatures" — a committed-tree-freshness check, unrelated to
progression). A second full run (10m31s, required by the extra-rigor determinism rule for shared
static test state) additionally showed
`A_stale_committed_file_refuses_the_whole_import_and_writes_nothing` fail (2 total). Both tests are
`[Trait("Category","DiskSemantics")]`, spawn a REAL separate `CreatureSpeciesImport` child process, and
read/generate against `gk-data/packs/fusion/data/generated/creatures` on disk — a completely different subsystem than
progression/XP, touched by zero files in this diff (`git status --porcelain -- gk-data/packs/fusion/data/generated/creatures`
is clean). Multiple other agent sessions are confirmed running concurrently against this same repo
(background notifications for Lane C/D, TVB, backlog-clean-up, empire-progression, etc.), matching the
already-logged "Concurrent sessions, heavy machine load" pattern (full-suite crashes/hangs can be
inter-session) rather than anything this task changed. To isolate the actual affected surface from
that noise, `--filter "FullyQualifiedName~Progression|FullyQualifiedName~UniqueActorStore"` (the
tuning domain this task's shared-bootstrap edit touches, including `UniqueActorStoreTests`, which
reconfigures the same `ProgressionTuningHub` mid-run) was run twice in a row: **58/58 both times** —
the actual determinism proof this task's process-wide-state edit requires. Not fixed here (out of this
session's SP7.2 scope; the fix is `dotnet run --project gk-forge/tools/CreatureSpeciesGen` + commit, a separate,
unrelated task per the "generated seed data is never hand-edited" rule).

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.
