# SSH1.3 — `host-gate` c: fix first (F6) — `SocketHost.Capacity`, reachability reads capacity

Task: tasks/strain-splice-host-todo.md SSH1.3 · spec: docs/architecture/strain-splice-host/spec-host-gate.md §1-§2

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SocketHost` gains `Capacity`, filled by `SocketHostFor` from the `BaseTypeSocketMaxCorpus` lookup; `0 <= SocketCount <= Capacity` violated throws | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher"` | exit=0 :: 13 passed, incl. `Socket_host_refuses_opened_above_capacity` | `SocketModel.cs`, `RpgStore.ItemCard.cs` |
| `ComboMatcher.CanEverHold` reads `Capacity`; `Fits` reads the opened count | same | `CanEverHold_reads_capacity_not_the_opened_count` passed | `ComboMatcher.cs` |
| `an_unbored_chassis_with_capacity_reads_reachable_not_undiscovered` (0 opened, capacity 4 → reachable, distance 4) | same | passed | `ComboMatcherTests.cs` |
| `a_host_whose_capacity_is_below_the_recipe_is_undiscovered` | same | passed | `ComboMatcherTests.cs` |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints"` (widened to the route's own real test files) | `~SocketHostFor\|~ItemInsertElement\|~ItemCardEndpoints\|~ItemPreviewEndpoints\|~GemTier` | exit=0 :: 52 passed | — |
| Full Core.Tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` | exit=0 :: 14531/14531 | — |
| Scoped Data.Tests (`data.item-card`) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "VerificationId=data.item-card"` | exit=0 :: 23/23 | — |
| Guards / audits | `guard-dal.ps1`; `guard-test-substrate.py`; `audit-overflow.py`/`audit-magic-numbers.py --targets <4 files>` | all clean | — |

## `Capacity` vs `SocketCount` — two axes, not one

`SocketCount` is how many sockets are OPENED right now — what an actual `SocketFill` list can ever
carry, and the right question for `CombinationEvaluator.Evaluate`'s "does this fire on the real fill"
(unchanged: `HostAdmits` still reads `SocketCount`). `Capacity` is how many the chassis could EVER
hold — the right question for `CombinationDistance.Reachable`'s "is this a real goal, or
Undiscovered". Before this task the two were conflated: `HostAdmits` (SSH1.1) fed BOTH questions, so an
unbored chassis (0 opened) with real capacity would incorrectly read `Undiscovered` for anything
needing more than 0 sockets. New `ComboMatcher.CanEverHold` is `HostAdmits`'s same role/frame checks
plus a `Capacity` bound instead of a `SocketCount` one; `CombinationDistance.Reachable` now calls it,
and its own three remaining checks (ingredient count, Pure/Diversity threshold, Ring/Eclipse's
two-socket minimum) switched from `SocketCount` to `Capacity` for the identical reason.

## The invariant throws, never clamps

`SocketHost.SocketCount`'s own property initializer validates `0 <= SocketCount <= Capacity` and
throws `ArgumentOutOfRangeException` otherwise — an opened count above the chassis's own ceiling is a
caller bug (a corrupt row, or two builders disagreeing), and D1's own "throw, never clamp" rule applies
here exactly as everywhere else in this codebase. `Capacity` defaults to `int.MaxValue` so every
pre-existing caller that never named a ceiling — dozens of test fixtures across three files — keeps
behaving exactly as before rather than being forced to declare one.

## Two stale test fixtures fixed (Capacity's own consequence)

`ItemSurfaceTests.cs` and `CombinationEvaluatorTests.cs` each carry a shared `Host(sockets, ...)`
helper that built a host with an implicit, unbounded capacity. Two real `ItemSurfaceTests` failures
surfaced immediately (`A_two_socket_item_never_shows_a_four_insert_recipe_as_one_away`,
`Every_row_of_the_real_generated_catalog_gets_exactly_one_of_the_four_states`): a 2-socket host used to
correctly show a 4-ingredient recipe as `Undiscovered` via `SocketCount`, but with `Capacity` defaulting
to unbounded, the SAME recipe now read as merely `KnownInactive`. Fixed at the fixture, not the
production code: `Host(sockets, ...)` now also passes `Capacity: sockets` — a "fully-bored chassis" is
exactly what every existing caller already meant by "N sockets" before `Capacity` existed as a separate
axis; a test that wants an unbored one (`SocketCount < Capacity`) passes both explicitly, as the three
new `ComboMatcherTests.cs` cases do. `ComboMatcherTests.cs`'s own `Host()` helper got the same fix
pre-emptively, for the same reason, before it could hide the identical class of bug in its own file.

## `SocketHostFor` reads a real `socketMaxFor` when handed one — named gap: nobody hands it one yet

`SocketHostFor` now computes `Capacity` as `socketMaxFor(generation.BaseTypeId) ?? int.MaxValue` — a
real, working mechanism, tested via `ComboMatcherTests.cs`'s direct `ComboMatcher`/`SocketHost` cases.
**Honest gap, carried forward from SSH1.2's own evidence fragment and not yet closed:** both of
`SocketHostFor`'s two production callers (`RpgStore.ItemCard.cs`'s own `GetItemCardInput`, and
`ItemSurfaceEndpoints.cs`'s `/combinations` route) still pass the literal `_ => null` stub SSH1.2
introduced — `ItemCardCorpus` carries no socket-max delegate of its own, and
`Program.cs`'s only existing `BaseTypeSocketMaxCorpus.Load` call sits inside the workbench's own
`if (recipeCatalog is { } workbenchRecipes)` block, out of scope for either route's registration.
Neither this task's nor SSH1.2's own Files list names `Program.cs` or a `MapItemSurfaces`/
`ItemCardEndpoints` signature change, and reaching into either would cross this task's stated scope on
an S-sized ticket. **Result: `Capacity` is mechanically correct and fully proven at the `ComboMatcher`/
`SocketHost` level today, but is `int.MaxValue` (unbounded) in production for both real routes until
that wiring lands** — named here rather than left to be discovered as a silent gap later.

## Status

All four SSH1.3 acceptance criteria met at the mechanism level; the wiring gap above is named, not
hidden. Ledger marked done; todo checkbox ticked.
