# TVB5.8 — the manifest validator refused every increment after the first

Found by trying to plan increment 2 (`--apply` was never reached):

```
$ dotnet run --project gk-core/tools/FileMove -- split gk-core/tests/core-test-projects.v1.json --project FusionRpg.Core.ActorHub.Tests
REFUSED: manifest fails 2 A1 rule(s):
  [FusionRpg.Core.AchievementTitlesTuningTests.Tests] gk-core/tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests already exists
  [FusionRpg.Core.AchievementTitlesTuningTests.Tests] include pattern 'AchievementTitlesTuningTests.cs' matches no file
```

A1's "the project directory does not exist yet" and "every `include` matches ≥1 file" are preconditions of
the **increment being applied**, not properties of the manifest as a whole. Read as global rules they are
self-defeating under A5 ("One manifest project per increment, in manifest order"): the moment the first
increment is kept, every earlier project's directory exists and its files have left the residual, so the
manifest is invalid forever. The split could never have reached increment 2 in any lane.

Fix: `SplitManifestValidator.Validate` takes the target project — the one this call is about to apply —
and exempts every OTHER project whose directory already exists from those two rules. Everything else is
unchanged: name rules, reference rules, the shared-file rule, and the double-claim rule still apply to
every project, and a later project with an empty `include` is still refused. `targetProject: null` (the
default, and what the F11 cases pass) keeps the previous whole-manifest reading.

| Criterion | Command | Result |
|---|---|---|
| A partially applied manifest validates for the next increment | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release --filter "FullyQualifiedName~An_already_applied_project_no_longer_blocks_the_next_increment"` | 1 passed |
| The TARGET's directory must still not exist | `…--filter "FullyQualifiedName~The_target_project_directory_must_still_not_exist"` | 1 passed |
| A later project's empty `include` is still refused | `…--filter "FullyQualifiedName~A_later_projects_empty_include_is_still_refused"` | 1 passed |
| Whole tool suite (F1–F11 intact) | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release` | **47 passed / 0 failed** |
| Increment 2 plans again | `dotnet run --project gk-core/tools/FileMove -- split gk-core/tests/core-test-projects.v1.json --project FusionRpg.Core.ActorHub.Tests` | exit 0, 17 operations |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitManifest.cs,gk-core/tools/FileMove/Program.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs -Session tvb58` | exit 0; `filemove-fallback` module run **47/47** |
