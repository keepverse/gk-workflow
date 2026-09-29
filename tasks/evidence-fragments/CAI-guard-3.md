# CAI-guard-3 — the lawn AI's Core contract, enforced instead of asserted in prose

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## Why

Four specs state the same rules in their Code-style / Boundaries sections — *the lawn reads exactly one
time base*, *randomness comes only from `SeededRng.DeriveStream`*, *Core reads no file*, *Core is
Unity-free*, *the decision path never awaits* — and every one of them recorded the same honest gap:
`spec-lawn-cast-trigger.md`'s design-gate checklist, last line, says *"the rule 'the lawn reads exactly
one time base' … and 'per-actor AI state is dropped before ptr reuse' … are currently covered only by
this module's tests"*. A rule carried only by prose drifts the moment someone adds `DateTime.UtcNow` to a
lawn file and nothing notices — which is the defect D15 exists to prevent.

## The scan

`tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCoreContractScanTests.cs` — 7 tests over **every `.cs`
under `gk-core/src/FusionRpg.Core/Match/Ai/`, enumerated from the directory, never listed**:

| Test | Banned forms | Why |
|---|---|---|
| `…reads_no_wall_clock` | `DateTime`, `DateTimeOffset`, `Stopwatch`, `Environment.TickCount` | one time base; a tick is passed in as `nowTick` (`CAI4.7` §6, D15) |
| `…uses_only_the_owned_rng` | `System.Random`, `new Random(`, `Random.Shared` | `SeededRng.DeriveStream` only |
| `…reads_no_file` | `File.`, `Directory.`, `FileStream`, `StreamReader`, `StreamWriter`, `Path.Combine` | Core reads no file (`tunables-ssot.md` §7.2) |
| `…is_Unity_free` | `UnityEngine` | Core is CI-built without the game |
| `…never_awaits_or_spawns_a_thread` | `Task.Run`, `ThreadPool`, `new Thread(`, `await ` | Hot rule 3; main-thread-only frame slot |
| `The_scanned_surface_is_the_whole_lawn_directory_and_every_file_is_readable` | — | non-empty, and the seven wave-4 files are named once so their disappearance is a failure rather than a quieter scan |
| `The_scan_strips_comments_so_prose_that_promises_the_ban_does_not_trip_it` | — | the stripper, proven in both directions (below) |

**Enumerating the directory is the design, not a convenience**: a file added tomorrow is covered with no
edit, and there is no allowlist for a future session to widen — the failure mode `CAI-guard-1`'s re-pin and
the atom vocabulary's four stale counts both name. All 11 files were verified clean before the scan landed,
so no file needed exempting.

**Comment-stripping is load-bearing, not tidiness.** Two of these files contain the word `DateTime` in a
doc comment that *promises* the ban (`LawnDecisionTrigger.cs` — "no `DateTime` appears anywhere on its
path"; `LawnOrderQueue.cs` — "nothing here reads a `DateTime` or a `DateTimeOffset`"). The stripper's own
test asserts **on real content** that the raw text contains the token and the stripped text does not, and
that a planted `var now = DateTime.Now;` still trips while a comment about it does not. The pattern mirrors
the test-local strippers already used for the same reason (`NamingBanTests`,
`LegacyEquipTableRetirementGuardTests`); Core has no shared one, so this file carries its own three-line
copy rather than reaching across test assemblies.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| The scan | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnCoreContractScan"` | **7 passed / 0 failed** |
| Row Verify line | `verify-change.ps1 -Paths @('tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCoreContractScanTests.cs') -Session combat-ai-4` | exit 0, **299 passed / 0 failed** (`core-balance`) |
| Guards | `guard-actor-hub.ps1` | ACTOR-HUB GUARD OK |
| **Mutation**: a planted `System.DateTime.UtcNow` in `LawnDecisionBudget.cs` | planted, run, reverted | 1 red — the wall-clock test |
| **Mutation**: a planted `new Random(7)` in `LawnCastTokenPool.cs` | planted, run, reverted | 1 red — the owned-RNG test |

Both plants are in files this lane owns (`gk-core/src/FusionRpg.Core/Match/Ai/**`), reverted cleanly — no file
outside the fence was touched.

## What this does not cover

The *second* rule the same checklist line names — "per-actor AI state is dropped before ptr reuse" — is
**not** covered here and could not be: the drops live in `InjectorEntityRegistry.Remove`/`Clear`
(`gk-fusion/src/FusionRpg.Injector/**`, outside this fence) and the Core side of the rule is only that the four
per-actor types expose `Remove`/`Clear` at all. The injector half is `CAI4.3`/`CAI4.8`'s, and
`R-INJ` in the todo is where it is routed.
