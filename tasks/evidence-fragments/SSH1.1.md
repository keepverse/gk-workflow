# SSH1.1 — `host-gate` a: extract `ComboMatcher`; the evaluator and the preview both call it

Task: tasks/strain-splice-host-todo.md SSH1.1 · spec: docs/architecture/strain-splice-host-map.md (host-gate §1)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ComboMatcher.HostAdmits`/`Fits`/`Match` exist; `CombinationEvaluator` calls them, `HostMatches`/`MultisetSatisfied` deleted; `CombinationDistance` calls them, `Reachable`'s host arm/`MultisetShortfall` deleted | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher\|FullyQualifiedName~CombinationEvaluator\|FullyQualifiedName~ItemSurface"` | exit=0 :: 67 passed | `ComboMatcher.cs` (new), `CombinationEvaluator.cs`, `CombinationDistance.cs` |
| The evaluator's output is byte-for-byte unchanged (existing `CombinationEvaluatorTests` green) | same | 59 pre-existing evaluator/surface tests, all green, no assertion changed | — |
| `evaluator_and_preview_share_one_matcher` (reflection) passes | same, that test | passed — asserts `HostMatches`/`MultisetSatisfied` absent from `CombinationEvaluator`, `MultisetShortfall` absent from `CombinationDistance`, and `HostAdmits`/`Match`/`Fits` present on `ComboMatcher` | `ComboMatcherTests.cs` |
| Property test `a_fill_the_preview_reports_at_distance_zero_is_a_fill_the_evaluator_fires` over generated fills | same | passed, 900 trials (300 × 3 recipes) | `ComboMatcherTests.cs` |
| Full regression (new shared type, touches the evaluate/preview path broadly) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release`; `dotnet build gk-core/tests/FusionRpg.Server.Tests -c Release` | 14452/14452; Server.Tests builds clean, 0 errors | — |
| Audits | `audit-overflow.py --targets <3 files>`; `audit-magic-numbers.py --targets <3 files>` | both clean, 0 findings | — |

## The extraction, precisely

`ComboMatcher.HostAdmits` is `CombinationEvaluator.HostMatches` and `CombinationDistance.Reachable`'s
first three checks (`MinSockets`, `HostRole`, `HostFrame`) — verbatim identical before this change,
confirmed by reading both before writing the extraction. `Reachable` keeps its OWN remaining checks
(set-exclusivity D21, ingredient-count-vs-sockets, threshold-vs-sockets, ring/eclipse's two-socket
minimum) — those are per-SHAPE reachability rules, not host predicates, and `HostAdmits` is
deliberately the shared SUBSET, not the whole gate (SOLID I: a thin shared contract, not a fat one).

`ComboMatcher.Match` is ONE claiming pass (most-specific-first, lowest-qualifying-tier-first — both
rules carried over unchanged) that returns `Satisfied` + `Used` (the evaluator's old
`MultisetSatisfied` contract) AND `Missing` (the distance side's old `MultisetShortfall` contract)
together, so the SAME pass over the SAME fill against the SAME recipe now backs both callers — the
property test is the direct proof that this can no longer diverge. `Fits` is the boolean convenience
form the evaluator's `.Where` filters use.

## A genuine behavioural unification, not just a move

The two original functions disagreed on a zero-or-negative-quantity `ComboIngredient`:
`MultisetSatisfied` refused the WHOLE recipe immediately; `MultisetShortfall` silently skipped that one
ingredient and could report a full recipe as zero-distance around it. No real content authors a
zero-quantity ingredient (confirmed: no test or shipped recipe does), so this was unreachable in
practice, but it is exactly the class of divergence host-gate exists to close. `Match` now refuses the
whole recipe (adds a `MissingIngredient` for it) in both cases, matching the evaluator's real rule.

## `MissingIngredient` moved, not duplicated

The record lived in `CombinationDistance.cs` (`Items.Surfaces`). `Surfaces` already depends on
`Sockets` (`CombinationDistance.cs`'s own `using`), never the reverse, so a shared record consumed by a
`Sockets`-owned matcher had to live in `Sockets` — moved verbatim into `ComboMatcher.cs`; `Surfaces`'
existing `using FusionRpg.Core.Items.Sockets;` resolves it unchanged, confirmed by the unmodified
`ItemSurfaceTests.cs` staying green.

## No downstream break

`CombinationEvaluator.Evaluate`/`Preview`/`PreviewWithOneMore` and `CombinationDistance.Evaluate`'s own
public signatures are untouched — `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs` and three
`FusionRpg.Server.Tests` files call only these, confirmed unaffected by a clean `Server.Tests` build.

## Status

All SSH1.1 acceptance criteria met. Ledger marked done; todo checkboxes ticked.
