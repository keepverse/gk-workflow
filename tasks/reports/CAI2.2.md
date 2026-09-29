# CAI2.2 — `replay-identity` B: the Server's version-addressed profile source

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. This is the one piece of the row that needs no denied
path: `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs` — the host-side `ICombatAiProfileSource` the spec's
§2 puts on the Server. The row's other two thirds (the `combat_ai_profile` column in `gk-core/src/FusionRpg.Data/**`,
and the three stamping sites + five-step pin resolution + boot-sweep guard that read and write it) are
**not** in this lane's fence and stay owed. Evidence lives here rather than in `tasks/evidence-fragments/`
because that directory is not in this lane's allowed paths.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Current` is the newest published set; every published version is addressable by its own number; the version field agrees with the file it was filed under | `dotnet test gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj --filter "FullyQualifiedName~CombatAiProfileFilesTests"` | **8 passed / 0 failed** — `Current_is_the_newest_published_version_and_every_version_round_trips_by_number` runs against the repo's own real `gk-core/data/tuning` tree and asserts no version COUNT, only the ordering contract | `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs` |
| An unresolvable pin returns `null`, never `Current` (the refusal, not a fallback) | same run | **8 passed / 0 failed** — `An_unknown_version_returns_null_never_the_current_set` (`Current.Version + 1000`, `int.MinValue`, `0`) | `ForVersion` |
| A file whose name version disagrees with its document is refused, naming the file | same run | **8 passed / 0 failed** — `A_file_whose_name_version_disagrees_with_its_document_is_refused_naming_it` (named `v3`, carrying `version: 2`) | constructor |
| A version published twice is refused, naming both files | same run | **8 passed / 0 failed** — `A_version_published_twice_is_refused_naming_both_files` (`v2` + `v02`) | constructor |
| A directory with no published combat-ai file, a malformed document, and a missing/empty directory are each refused loudly | same run | **8 passed / 0 failed** — `A_tuning_directory_with_no_combat_ai_file_is_refused` (another domain's `ai.v9.json` and the glob-matching `combat-ai.vault.json` are both ignored), `A_malformed_document_is_refused_by_the_loader_not_silently_skipped`, `A_missing_or_empty_directory_is_refused` | constructor |
| The newest wins and the older stays addressable — enumeration order cannot change it | same run | **8 passed / 0 failed** — `The_newest_version_is_current_and_the_older_one_is_still_addressable` (`v1` + `v7`: `Current.Version == 7`, `Versions == [1,7]`, `ForVersion(1).Version == 1`) | constructor |
| The module-level boundary for `gk-core/src/FusionRpg.Server/**` (`server-fallback`: the `server` project + `dal`) | `dotnet test gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj` | **814 passed / 0 failed** (3 m 22 s) | — |
| The same boundary's guard | `pwsh -NoProfile -File scripts/guard-dal.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data`, exit 0 | — |
| Test substrate (a temp dir IS the thing under test here, so the delete must not be swallowed) | `python gk-core/scripts/guard-test-substrate.py` | `TEST SUBSTRATE GUARD OK — no new swallowed deletes or temp-backed stores in tests/`, exit 0 | `gk-core/tests/FusionRpg.Server.Tests/CombatAiProfileFilesTests.cs` |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | 1686 documents / 25408 citations, **D1 869, D2 7, D3 56, D4 0 — all 0 HIGH** | — |

## Why the row stays OPEN

`CombatAiProfileFiles` has **no production caller yet**, and that is stated rather than papered over. The
pin it exists for needs three things this lane cannot land together:

1. **`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs`** — the nullable `combat_ai_profile` TEXT column
   (and `WebMatchLogEntry.CombatAiProfile` / `AppendWebMatchLog` / `SelectLog` / `MapLog`). **Outside this
   lane's fence.**
2. **The three stamping sites** (`WebMatchService.cs` ×2, `DelveBattleSessionManager.cs`) — each needs the
   column to pass `combatAiProfile:` to `AppendWebMatchLog`, so the Server third cannot compile without (1).
3. **The five-step pin resolution + the boot sweep's fifth guard** — they read `entry.CombatAiProfile`.

Wiring `CombatAiProfileFiles` into `Program.cs`'s `CombatAiProfilePolicy.Configure` call would make it
reached today, and it is deliberately **not** done: with only `combat-ai.v1.json` on disk the behaviour
would be identical, but the Server would then auto-pick the newest published version while
`Injector/Host/RpgHost.cs:97-99` still names `combat-ai.v1.json` by hand — a Server/Injector profile
divergence introduced on the next publish. That is the H7 hazard, not a fix for it. The two readers must
move in the same commit as the column, which is the remainder this row records.

## Correction carried in this commit — doc citations the CAI2.5 edit moved

`InjectorEntityRegistry.cs` grew 14 lines inside `Remove` and 4 inside `Clear`, so every `file:line`
citation below those points shifted by **+18**. Re-anchored here, in the same commit as the change that
moved them: `docs/architecture/combat-ai/spec-lawn-actor-view.md:218` (`Resync` `:163-180` → `:180-199`),
`spec-lawn-cast-trigger.md:232` and `spec-lawn-held-actions.md:134` (`Remove` `:129-146` → `:129-159`).
The three files outside this lane's fence are filed as `CAI-cite-4` rather than edited.

## Correction (lane `cai3`, session `combat-ai-3`, 2026-09-23)

The paragraph above says the `Configure` call was not switched because the Server would then auto-pick the
newest while the Injector named `combat-ai.v1.json` by hand — an H7 hazard. **That hazard no longer
exists.** `CAI-F1` landed `CombatAiTuningFiles.Current` and moved both hosts onto it:
`Injector/Host/RpgHost.cs:97-99` reads `CombatAiTuningFiles.Current` (`combat-ai.v2.json`), not a literal,
and `SiegeKeyMigrationTests.Both_hosts_load_the_same_file` asserts neither host contains a `"combat-ai.v`
literal. Measured this session:

```
grep -n "CombatAiTuningFiles\|combat-ai.v1" gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs
  99:  ... CombatAiTuningFiles.Current))));

grep -rn "CombatAiProfileFiles" src/ tests/
  gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs:35,49      (the class itself)
  gk-core/tests/FusionRpg.Server.Tests/CombatAiProfileFilesTests.cs  (its tests)
```

So wiring the version-addressed source is no longer an H7 hazard — it is only *useless* until the pin
resolution exists, and the pin resolution reads `entry.CombatAiProfile`, which needs the denied `Data`
column. The row's only remaining blocker is that column plus the three stamping sites and the five-step
pin resolution that read it.
