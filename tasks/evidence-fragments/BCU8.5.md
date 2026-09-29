# BCU8.5 — route `data-test-substrate` BU2–BU4

Read the owning program instead of guessing. `test-verification-boundary`'s `data-tests-sharding`
module covers BU2 and **already delivered it** (TVB1.1–TVB1.5 all `[x]`); BU3/BU4 are `FusionRpg.Data`
store-timing questions with no sharding content and stay `data-test-substrate`'s, now scheduled with
that stated. No code changed — the deliverable is the routing decision and the two todos that carry it.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| BU2 covered by TVB, and delivered | `cat gk-core/scripts/test-shards.v1.json` | schemaVersion 1, `data` project, 3 class-prefix shards + remainder, `maxParallelThreads: 2`, `_meta.measured` 98.49s (2) / 86.45s (4) | `gk-core/scripts/test-shards.v1.json`, `scripts/test-sharded.ps1` |
| CI actually adopted it | `rg -n "test-sharded" .github/workflows/ci.yml` | 1 hit — `:152` (`-Project gk-core/tests/FusionRpg.Data.Tests/...`) | `.github/workflows/ci.yml` |
| TVB sharding track complete | `sed -n '44,72p' tasks/test-verification-boundary-todo.md` | TVB1.1–TVB1.5 all `[x]` | `tasks/test-verification-boundary-todo.md` |
| Routing recorded both ways | `git diff tasks/data-test-substrate-todo.md tasks/test-verification-boundary-todo.md` | BU2 ticked against TVB's artifacts; BU3/BU4 marked scheduled with owner + the idle-machine gate; TVB gets a "received from BCU8.5" verdict | those two files |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('tasks/data-test-substrate-todo.md','tasks/test-verification-boundary-todo.md') -Session bcu8"` | guard module 575 passed / 3 failed (the same 3 pre-existing ones — lane D's `FusionRpg.FileMove.Tests/SplitExecutorTests.cs:262-263`; two `VerificationBoundaryWorkflowTests` 120 s timeouts vs a 3m05s guard script). Doc-citation step: **0 HIGH** for both files (`python scripts/audit-doc-citations.py --strict --scope …` also 0 HIGH) | — |
| Doc-citation fix in the touched file | `git diff tasks/data-test-substrate-todo.md` | `Program.cs:327` (D3 ambiguous basename, pre-existing at `:218`) → `gk-core/src/FusionRpg.Server/Program.cs:423`, which is the line that actually reads `FUSIONRPG_DATA` | same file |

BCU8.4 is **blocked**, not skipped: its fix is `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4260-4264`
(`EnsureColumn`'s `try { ALTER TABLE … } catch { }`), outside this lane's allowed paths
(`gk-fusion/src/FusionRpg.Injector/**`, `gk-core/src/FusionRpg.Core/**`, `tests/**`, `docs/**`, `tasks/**`). A tests-only
half would land a red suite, so nothing was written. Ledger note filed; needs a Data-owned lane or a
path grant.
