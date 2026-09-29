# BCU8.6 — live-probe Task 21: item provenance on the armoury DTO

**No code change: already delivered and merged by the `live-qa` lane's own Task 21 fix**
(`tasks/live-probe-todo.md` `[x]`, 2026-09-20). BCU8.6's job is to stop the backlog row sitting open as
unbuilt work — verified against the tree, not the other lane's note.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `origin_kind` reaches the armoury DTO | `rg -n "OriginKind" gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs` | `:63` field on `ArmouryRowDto`, `:164` populated from `item.OriginKind` | `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs` |
| Its regression exists and passes here | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Armoury_carriesTheItemsRealOriginKind"` | Passed — 1/1 | `gk-core/tests/FusionRpg.Server.Tests/ItemEquipEndpointsTests.cs:712` |
| Row closed with a pointer | `git diff tasks/backlog-clean-up-todo.md` | BCU8.6 ticked, naming the owning lane and both artifacts | `tasks/backlog-clean-up-todo.md` |

No code commit for this row: the production change is the `live-qa` lane's, already on HEAD. BCU8.6's
own commit carries the closed row + this fragment. `acquiredVia` is not a symbol anywhere in the repo
(`rg -n "acquiredVia" src/ tests/`), so `origin_kind` is the whole transport surface the row named.
