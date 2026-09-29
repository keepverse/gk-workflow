# CS-F2 — the player pack keeps its content tree (the delete is gone, and it is now required)

Lane `findings-2`, row `tasks/content-stack-todo.md` CS-F2 (filed by lane `findings-1`; restated there in
closed form). Row verdict: **`[x]`, closed 2026-09-23** — the delete half landed here, and the `/health`
Verify line became reachable on a fresh install when CS-F3 landed the owner's ruling the same day
(`tasks/reports/findings-2-csf3.md`: `SMOKE PASSED`, `contentSource='imported'`).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The publish output really carries the tree | `dotnet publish gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -p:PublishTrimmed=false -o <pack>/Server` | exit 0; `<pack>/Server/data/seed/**` = **1386** `.json`, `<pack>/Server/data/tuning/*.json` = **182** — beside `FusionRpg.Server.exe` | `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` |
| The pack boots on imported content | `./FusionRpg.Server.exe` from `<pack>/Server` with `FUSIONRPG_URLS=http://127.0.0.1:5301`, `FUSIONRPG_DATA=<dir with the roster imported by gk-forge/tools/CreatureSpeciesImport>`; `curl :5301/health` | `{'ok': True, 'contentSource': 'imported', 'catalogRevision': 1, 'contentImportError': None}`; log: `[content] imported the seed tree — catalog now at revision 1`, `Content root path: <pack>/Server` | — |
| Negative control: the pre-fix shape dies | same boot with `<pack>/Server/data` moved aside | `Unhandled exception. System.IO.DirectoryNotFoundException: Could not find a part of the path '...\Server\data\tuning\contracts.v1.json'` at `gk-core/src/FusionRpg.Server/Program.cs:32` — the delete did not degrade to a fallback, it removed a file the boot reads unconditionally | — |
| The pack layout now refuses a pack without it | `dotnet test gk-fusion/tests/FusionRpg.Launcher.Tests -c Release --filter "FullyQualifiedName~PlayerPackProbe|FullyQualifiedName~MelonHostGap" --verbosity minimal` | `Passed! - Failed: 0, Passed: 12` — including the planted-violation case that names `Server\data\seed` and `Server\data\tuning` | `gk-fusion/tests/FusionRpg.Launcher.Tests/PlayerPackProbeTests.cs` |
| Nothing else in the project moved | `dotnet test gk-fusion/tests/FusionRpg.Launcher.Tests -c Release --verbosity minimal` | `Passed! - Failed: 0, Passed: 166, Skipped: 0, Total: 166` | — |
| The release smoke reads the boot's own mode | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/smoke-player-pack.ps1 -PackDir <pack>` | at this row's own commit: `SMOKE FAILED` — `server_boot: GET /health did not return ok within timeout`, because the script's own fresh `%TEMP%` data dir had an empty species roster (**CS-F3**, filed). **Superseded 2026-09-23 by CS-F3's landing:** the same command now reports `SMOKE PASSED` with `contentSource='imported'` — see `tasks/reports/findings-2-csf3.md` | `scripts/smoke-player-pack.ps1` |
| The packaging surface has a boundary at all | `python gk-core/scripts/guard-verification-boundaries.py --skip-coverage-walk` | exit 0, `VERIFICATION BOUNDARY GUARD OK` (`player-pack-packaging` added — `scripts/publish-player.ps1` and `scripts/smoke-player-pack.ps1` had **no** owner mapping before this) | `gk-core/scripts/verification-boundaries.v1.json` |
| Scoped verification (code + report paths) | `pwsh -NoProfile -ExecutionPolicy Bypass -Command "& ./scripts/verify-change.ps1 -Paths @('scripts/publish-player.ps1','scripts/smoke-player-pack.ps1','gk-core/scripts/verification-boundaries.v1.json','gk-fusion/src/FusionRpg.Launcher/Services/PlayerPackProbe.cs','gk-fusion/tests/FusionRpg.Launcher.Tests/PlayerPackProbeTests.cs','gk-fusion/tests/FusionRpg.Launcher.Tests/MelonHostGapTests.cs','tasks/reports/findings-2-csf2.md') -AllowUnscoped"` | **exit 0** — `FusionRpg.Guard.Tests 599/599`, `Guard.Tests (focused) 57/57`, `FusionRpg.Launcher.Tests 166/166` | — |
| Scoped verification (adding `tasks/content-stack-todo.md`) | same command with that path added | **exit 1**, stopped at `doc-citations: tasks/content-stack-todo.md` **before any guard or test ran**: 30 findings (27 HIGH) on lines **566–4169**, all pre-existing (this lane's diff is one pure append at `+4316`). Filed as **CS-F4** in the same todo | `tasks/reports/findings-2-csf2.md` |

**Not proved.** (1) A full `pwsh -File scripts/publish-player.ps1` run: it needs a game install or
`artifacts/ci-drop-into-game` for the injector half, and this worktree has neither (`artifacts/` is empty,
`FUSIONRPG_GAME_DIR` unset), so the server half above is the strongest achievable form of its own Verify
line. (2) The `/health` reading was taken with the species roster pre-imported by
`dotnet run --project gk-forge/tools/CreatureSpeciesImport -c Release -- --db <dir>`, because the pack ships no
roster — that is CS-F3, not this row's cause. (3) `docs/testing/player-pack-smoke.md`'s "What it checks"
list now understates the probe (it does not name the content-tree requirement); that file is outside this
lane's allowed paths (`docs/architecture/**` only) — reported, not patched. (4) The brief's named command
is `verify-change.ps1 ... -Session findings-2`, which refuses with `session record not found: findings-2`:
`tasks/sessions/**` is not in this lane's allowed paths, so no record could be written. Every plan above
was executed with `-AllowUnscoped`, which skips only the session-scope check — the paths still resolve
through the registry and every selected check still runs and still gates.
