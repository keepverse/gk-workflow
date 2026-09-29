# SE4.29 — Archived rows are never listed or selected (fixes D2)

Spec: save-identity, step 6, Contracts. `ListPlayers` filters `WHERE archived_utc IS NULL`;
`SetCurrentPlayer` refuses (returns false) via the new `IsLiveSaveUnlocked` (the same predicate
`IsLiveSave` now delegates to, so a caller already holding `db` never opens a second connection);
`GetCurrentPlayerIdUnlocked`'s lowest-id fallback adds the same filter. `GET /api/players`
(`Program.cs:988-992`) calls `ListPlayers`/`GetCurrentPlayerId` directly — no endpoint change needed.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| After the migration archives a Zomboss-only row, the save list has no "Zomboss" | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveEmpires" --nologo` | pass 7/7 (6 existing + 1 new: `ListPlayers` omits it, `IsLiveSave` false, `SetCurrentPlayer` refused) | `RpgStore.cs`, `SaveEmpiresStoreTests.cs` |
| Lowest-id fallback never lands on an archived row | same | pass — with `current_player_id` cleared, `GetCurrentPlayerId()` resolves to the surviving live save, never the archived id | `RpgStore.cs` (`GetCurrentPlayerIdUnlocked`) |
| No regression | `--filter "FullyQualifiedName~SaveIdentity\|FullyQualifiedName~SaveOfRun\|FullyQualifiedName~SaveEmpires"` | pass 38/38 | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
