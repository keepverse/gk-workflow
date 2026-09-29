# Mega-merge QC 13 — rpg-simulator (in-process E2E) on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Full E2E suite (in-process server, no live game) + one re-bless. No live game.

## Verdict: GREEN after one legitimate re-bless (this QC caught a real drift)

| Check | Command | Result |
|---|---|---|
| Full E2E | `dotnet test gk-core/tests/FusionRpg.E2E.Tests` | first run 292/293 → **293/293** after re-bless |
| Web adapter | `npx vitest run src/contract/adapt.test.ts` | 17/17 |

## The catch (merge-interaction defect, fixed in this QC)

`ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto` failed:
checked-in fixture lacked `empireId`, live DTO carries `empireId: "dave"`. Cause:
SE4.31 save-identity ("an empire on every specimen", `0770c0f81`) changed the
DTO after the fixture was blessed — classic cross-lane drift, no lane at fault.
Fix: re-blessed via the sanctioned `FUSIONRPG_BLESS_CONTRACT_FIXTURES=1`
(one additive line, diff-verified), clean re-run green, full suite 293/293,
committed as `3c930595d`. Web readers (`adapt.test.ts`, mocks, demo pages)
unaffected (additive field).
