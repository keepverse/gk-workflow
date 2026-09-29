# tvb60 lane close — the three named verifications, two findings, and the open-row count at `213291c01`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| boundary guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` (29.5 s) | this fragment |
| the brief's Guard filter | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~CoreTestProjectPolicy"` | `Passed!  - Failed:     0, Passed:    63, Skipped:     0, Total:    63, Duration: 10 m 19 s` | this fragment |
| every CI-tier guard | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | `GUARDS OK - 25 guard(s) run, 0 red` — **`doc-citations` is 0 red now**, so `RS-F18` is closed (`7464bf590`) and the routing register's "2 HIGH" is stale | this fragment |
| `doc-citations`, whole repo, both bars | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` and `... -Strict` | `1689 documents, 25809 resolvable citations`; D1 683 (0 HIGH), D2 7 (0), D3 56 (0), D4 0 (0); **exit 0 in both forms** | this fragment |
| **TVB-F31** — the census `--program` flag can never match | `python .claude/cmdc-agents/scripts/convergence-census.py --program {item, test-verification-boundary, item-todo}` | all three print `no such program: <name>` and exit 2. Cause read: `:137` sets `r["program"]` to the basename with `-todo.md` already stripped, `:162` **appends** `-todo` to the argument, so `:164`'s equality never holds | this fragment |
| the program's open rows, counted rather than trusted | `python .claude/cmdc-agents/scripts/convergence-census.py` | `test-verification-boundary   12 blocks   0 wip   1 residue` — the brief's "43 open task blocks" is stale | this fragment |
| TVB5.9's blocker is still live, read from the files at this head **and** in the main checkout @ `fe71dc15b` | `sed -n '1,10p' gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json`; `head -20 gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json`; `sed -n '1,8p' gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json` | `"displayName": "Crazy Dave"` against live `"display": "Garden Keeper"` (`gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json:7`); `unique-actor.json` carries no `empireId` against `gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs:22`; `"stateHash": "b41ce3ef4c7c6c814ccf05ad190a13b248496fee1192ddeeb26b1ac9ea529b54"`. Byte-identical in both trees, so no lane has re-blessed them | this fragment |
| run-board's own citation check, re-read | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/run-board-20260920.md') -Session tvb58"` | `10 HIGH` (9 D1 + 1 D3) on 86 resolvable citations — the row's filing reading was 4, the register's was 9 | this fragment |

The repo-wide `doc-citations` guard is green while the same audit on `tasks/run-board-20260920.md` alone
prints 10 HIGH: the guard does not walk `tasks/**` — that asymmetry is `TVB-F6ep`, and it is why this row
is only visible through `verify-change`.
