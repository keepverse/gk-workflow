# Mega-merge QC 15 — expeditions test project on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Full project + bisection. No live game.

## Verdict: RED — flaky by construction, cause identified, product code exonerated

| Check | Command | Result |
|---|---|---|
| Full project | `dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests` (×4 runs) | 11/38 failed, 11/38 failed, **38/38 passed once**, 11/38 failed — nondeterministic |
| Minus one test | same, `--filter FullyQualifiedName!~empties_every` (×2) | **37/37 twice, deterministic** |
| Suspect alone | `Tier_goldens_are_locked` ×3, `Same_inputs` ×1, pairs | all green in isolation |

## Root cause (measured, not inferred)

`ExpeditionResolverTests.A_floor_that_empties_every_wild_band…` configures the
**process-global** `CreatureRankFloors` to Almanac for ~40 `Resolve` calls.
xUnit runs the project's test classes in parallel; any wild-band resolution in
another class inside that window gets empty bands and dies in `Max()` over the
empty wave (`ExpeditionResolver.cs:186`). The product wire is innocent: floors
stick as configured (proven by direct assert), the gate refuses exactly as
specified, and every victim passes with the poisoner excluded.

## Fix (QC fix cycle 1, 2026-09-24) — DONE, proven by test

One shared non-parallel xUnit collection (`ExpeditionsSequentialCollection`,
`DisableParallelization = true`) across the project's three test classes; product
code untouched. Proof: full project 5 consecutive runs **38/38, 38/38, 38/38, 38/38,
38/38** (previously flipped 11-fail ↔ 38-pass). The Almanac-window test keeps its
exact assertions — serialization only removes the cross-thread window.

Supersedes the routing below (kept for history): the defect was fixed in-test
rather than routed, since the fix touches only test attributes.
Test-isolation defect owned by creature-seed/expeditions: give the Almanac test
its own collection (`DisableParallelization`), scope floors per async context,
or equivalent. Introduced with the T10 merge (the test is new there); the
project was 38/38 in-lane because lane timing serialized the threads. Do NOT
"fix" by weakening the refusal assertion or deleting the test.
