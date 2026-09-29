# CP2 — the player can reach it

Checkpoint of `tasks/empire-progression-plan.md` (Wave A), closed inside EP1.21's commit — the last
task it depends on — per the commit-hygiene rule.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| EP1.21's Playwright run is green | `cd gk-web/web/fusion-rpg-web; npm run test:e2e -- aptitude-auto-assign` | pass — 4 passed / 0 failed (1.4s); the same run also green as part of `npm run test:e2e -- aptitude` (14 passed / 0 failed) | `gk-web/web/fusion-rpg-web/e2e/aptitude-auto-assign.spec.ts` |
| Nothing persists before Confirm | same run | pass — `POST /api/aptitudes/unique/**` is observed 0 times in every case: after an `even` fill, after the reload in the same case, after a `species-favour` fill, and after a refused `species-favour`. Only Confirm posts | same file |

Both clauses are independent: the first is the Playwright run's exit status, the second is a request
count asserted inside that run rather than inferred from the first.
