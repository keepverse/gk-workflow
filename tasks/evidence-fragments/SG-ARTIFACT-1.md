# SG-ARTIFACT-1 — a cross-lane merge reverted two `Program.cs` reader lines; one stopped the boot (2026-09-22)

Lane `sgc-4` · session `species-gear-chain-4` · found by merging `features/mega-merge` (`8e1ece9cc`) into `cmdc/sgc-4`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The merge dropped lines | `git diff 8b81e395d^:gk-core/src/FusionRpg.Server/Program.cs 8b81e395d:gk-core/src/FusionRpg.Server/Program.cs` | 1 file, **2 insertions / 15 deletions**: the `items` block removed (2 `ItemsTuningHub` occurrences before, **0** after) and `ai.v3.json` reverted to `ai.v2.json` | `8b81e395d` |
| The `items` half is my T59 fix | `git show 3e06b1fd7:gk-core/src/FusionRpg.Server/Program.cs \| grep -c ItemsTuningHub`; same at `8e1ece9cc` | `2` at the previous tip, **`0`** at the new one | — |
| The `ai` half breaks the BOOT | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~UnlockTuningActivation"` | **Failed: 2** — `WorldAiTuningRejection: ai tuning: missing or non-object 'buildScorer'` at `Program.cs:285` (`WorldAiTuning.cs:81` requires it; only `ai.v3.json` carries it, `ai.v1`/`v2` do not) | — |
| EP5.2 had switched it in the same commit as the publish | `git show 2114445b6 -- gk-core/src/FusionRpg.Server/Program.cs` | `-ai.v2.json` / `+ai.v3.json` (1 insertion, 1 deletion) — so the later merge reverted a landed H7 switch | `2114445b6` |
| Both lines restored | `grep -n "ai.v3.json\|items.v1.json" gk-core/src/FusionRpg.Server/Program.cs` | `items.v1.json` (T59) and `ai.v3.json` (EP5.2), each with the incident named in the source | `gk-core/src/FusionRpg.Server/Program.cs` |
| The boot works again | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~UnlockTuningActivation"` | **Passed: 2** (was 2 failed before the restore) — `RpgApiFactory` is `WebApplicationFactory<Program>` (`RpgApiFactory.cs:9`) | — |
| Regression tripwire, revision-agnostic | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ContentBootStartupWiring\|FullyQualifiedName~ItemCard\|FullyQualifiedName~WorldAi"` | **30 passed** — the new test reads the latest `items.vN`/`ai.vN` on disk and requires the boot to name it (H7's real contract), so the next publish stays green and a reverted pin fails in a test | `ContentBootStartupWiringTests.cs` |
| Path-owned verification | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/Program.cs','gk-core/tests/FusionRpg.Server.Tests/ContentBootStartupWiringTests.cs') -Session species-gear-chain-4"` | **EXIT 0** — `server-fallback` + `server-tests-fallback`, `DAL GUARD OK`, Server.Tests **797 passed / 0 failed** | — |
| How widespread is the stale-reader class? | domain sweep over `gk-core/data/tuning/*.v*.json` vs the revisions named in `src`/`tools`/`web`/`scripts` | **101 fine, 1 stale** (`actor-hud`: latest v2, code names v1 — already filed `tasks/actor-hud-todo.md:196`), **9 no literal** (constructed reader name or genuinely unread) | this fragment |

**Owner of the routed half:** `empire-progression` (EP5.2). Its reader line is restored here; the row is filed in
`tasks/species-gear-chain-todo.md` § "Filed by other lanes" as **SG-ARTIFACT-1** because
`tasks/empire-progression-todo.md` is outside this lane's fence.
**NOT proved:** that `8b81e395d`'s resolution dropped nothing else — I checked this lane's own artefacts (T57 parser +
test, T37 registry/edges/replay/endpoint test/validator patch, T58 doc) and they are intact, and the domain sweep above
finds no other stale reader beyond the filed `actor-hud` one; a repo-wide "did any merge lose a line" audit is the
pipeline's job, not this lane's.
