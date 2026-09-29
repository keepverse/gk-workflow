# SP7.3 — The level is readable through one seam; `checked` narrowing; one reader (R23)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `CommanderLevelOf(save, EmpireId.Zomboss)` returns the level the clock wrote | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderClock"` | **10/10 passed** (2 new: `CommanderLevelOf_returns_the_level_the_clock_wrote`, `Narrowing_...checked...never_clamps`) | `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs` |
| Narrowing into `ContentContext.ZombossLevel` (`int`) is `checked` — throws past `int`, never clamps | same run, `Narrowing_the_returned_level_into_an_int_is_checked_and_throws_past_int_MaxValue_never_clamps` | pass | same file |
| No second Zomboss commander-level reader | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ZombossCommanderLevelSingleReader"` | **2/2 passed** | `gk-core/tests/FusionRpg.Guard.Tests/ZombossCommanderLevelSingleReaderGuardTests.cs` (new) |
| No regression, wider progression scope | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Progression"` | **20/20 passed** | command output |
| No regression, power/content-index scope | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Power"` | **406/406 passed** | command output |
| `guard-dal.ps1` | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` | command output |

## What shipped (tests only — no production wiring, per the spec's own boundary)

`spec-zomboss-commander-clock.md`'s own "Ask first: any consumer wiring (delve, lawn) — those are
other programs'" and "no production code constructs a `ContentContext` or `ParentWorldTerms` from
live state ... wiring a consumer is the delve program's and `lawn-tuning-profile`'s" rule out building
a real `ContentContext`/`ParentWorldTerms` construction site here — that is explicitly out of this
module's scope (delve/lawn own it; `ai-empire-species`, in `empire-progression`, owns the R23 commander
pool consumer). SP7.3's own deliverable is therefore test-only, exactly matching the todo's own
`Files:` line (no production `.cs` listed):

- `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs`: two new tests.
  - `CommanderLevelOf_returns_the_level_the_clock_wrote` — a direct, explicit proof of the read seam
    (level 1 before any run, level 2 after one `defeat`), distinct from every other test in the file
    that only reads the level incidentally while proving an award outcome.
  - `Narrowing_the_returned_level_into_an_int_is_checked_and_throws_past_int_MaxValue_never_clamps` —
    proves the NUMERIC CONTRACT the spec's "Numeric" section states: the seam itself stays `long` end
    to end (a level of `int.MaxValue + 1`, planted directly via the store's own hot connection since no
    realistic amount of play reaches it, round-trips through `CommanderLevelOf` exactly, no clamp); a
    caller narrowing that value with `checked((int)level)` — the SAME pattern
    `ServerPowerIndexProvider.ReadSnapshot` already establishes for the player's own commander level
    (`checked((int)player.Level)`) — throws `OverflowException`, never silently wraps.
- `gk-core/tests/FusionRpg.Guard.Tests/ZombossCommanderLevelSingleReaderGuardTests.cs` (new, 2 tests) —
  mirrors `LegacyEquipTableRetirementGuardTests`'s exact allowlist shape: scans every production `.cs`
  file for the distinctive `SELECT level FROM rpg_actor_progression` (single-column) shape only
  `CommanderLevelOfUnlocked` uses (`ReadActorStateUnlocked`/`ReadEmpireActorUnlocked` select a wider
  column list, so this shape is not a coincidence of the generic actor reader) and asserts it appears
  in exactly one file (`RpgStore.Progression.cs`) and exactly once inside it. `ai-empire-species`
  (`empire-progression`) is not built yet, so today this guard's job is to keep it that way and to trip
  the instant a second reader is added, per the spec's own "a guard test asserts no second Zomboss
  commander-level reader" line.

## Spec verify-command correction (checked against the real test names, not quoted blind)

The spec's own `Commands` block names `--filter "...|FullyQualifiedName~PowerIndexComposer"`, but the
actual test class is `PowerIndexTests` (`tests/FusionRpg.Core.Tests/Power/PowerIndexTests.cs`) —
`PowerIndexComposer` never appears in a class name, so that filter matches zero tests. Ran the broader
`--filter "FullyQualifiedName~Power"` instead (406/406 passed) to get real coverage of the content-index
surface `ContentContext`/`PowerIndexComposer` feed, rather than silently accepting a filter that
matched nothing.

## R23 / EP notification

`ai-empire-species` (`empire-progression`, R23's own consumer) is the next reader this seam expects —
recorded here and in `tasks/species-progression-todo.md`'s own SP7.3 entry so the empire-progression
session picks it up from the todo/evidence trail rather than re-deriving it; `spec-zomboss-commander-clock.md`
already names the seam contract in full, so no edit to that spec or to `empire-progression`'s own docs
is made from this session (species-progression does not own those documents).

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.
