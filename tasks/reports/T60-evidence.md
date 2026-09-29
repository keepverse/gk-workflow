# T60 — the upgrade launders wear and resets potential (potential half)

**Row:** `tasks/species-gear-chain-todo.md` T60 · **Lane:** `sgc-5` (session `species-gear-chain-5`)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The successor's used potential fraction crosses (Data layer, real store) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemUpgradeStoreTests" --nologo --verbosity quiet` | **Passed 9 / 0 failed** (was 7; +2 cases) | `gk-core/tests/FusionRpg.Data.Tests/Items/ItemUpgradeStoreTests.cs` |
| Both pairs cross; BOTH carries' arithmetic pinned through the real endpoint | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemUpgradeEndpointTests" --nologo --verbosity quiet` | **Passed 15 / 0 failed** (was 14; +1 case) | `gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs` |
| Path-owned verification over the 7 changed paths | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('<7 changed paths>') -Session species-gear-chain-5"` | **EXIT 0** — Guard 591 + 4, Server 804 + 70 passed; dal / session-boundary / test-substrate guards clean; doc-citations 0 HIGH | this fragment |
| The store project (brief's named command), 3rd of 3 runs | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet` | **Passed 1852 / 0 failed** (11 m 36 s) | Findings 3 |
| Session boundary | `python scripts/session-boundary-check.py --repo-root <worktree> --session species-gear-chain-5` | **clean for 'species-gear-chain-5'** | `tasks/sessions/species-gear-chain-5.json` |

**NOT proved:** no live/in-game probe (verb proven through the real endpoint + real store only);
`gk-core/tests/FusionRpg.Core.Tests` not run (no Core path changed; `verify-change` selected no Core boundary).

**Findings.** 1. The durability half's comment claimed its arithmetic was "pinned at the Server layer" and no
such test existed (only the Data write was pinned) — the new endpoint case pins both. Fixed here.
2. Two pre-existing HIGH doc-citation findings blocked the scoped `doc-citations` check for the todo
(`:1091` bare `kinds.py` basename, `:3195` bare `Program.cs`, both present at HEAD) — repaired to full paths
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:87`, `gk-core/src/FusionRpg.Server/Program.cs:294`); audit after:
**0 HIGH, exit 0**. 3. The full Data project is **load-flaky** (1851/1, 1850/2, 1852/0 across three runs; the
failing set moves; both tests pass in isolation) — routed to `data-test-substrate` in
`tasks/reports/sgc5-open-blocks-20260922.md` §3, cause NOT proved.
