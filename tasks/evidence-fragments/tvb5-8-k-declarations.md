# TVB5.8.k — every declaration the manifest makes is now checked against the tree it was applied to

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the `include` closure (A1's own rule) | a walk of `gk-core/tests/core-test-projects.v1.json` resolving every `include` pattern against its **own** project directory | **234** patterns across **67** projects, **0** matching nothing; **0** projects without a `.cs` under their directory | this fragment |
| `links` | the same walk, repo-relative (`SplitProject`'s contract) | **16** entries, **0** missing | this fragment |
| `content` globs | the same walk, resolved **relative to the project directory** (MSBuild semantics) | **5** entries, all resolve: `../fixtures/effects/**/*` ×3 → **65** files each, `Goldens\actor-hud\**\*` → **1**, `../fixtures/combat/**/*` → **2** | this fragment |
| `references` | the same walk | **0** missing | this fragment |
| the new contract, green | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release --filter "FullyQualifiedName~SplitManifestReconciliationTests"` | `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4, Duration: 298 ms` | this fragment |
| it is a contract, not a tautology | the same filter with three bad declarations planted on `FusionRpg.Core.Lawn.Tests` (a bogus include pattern, link **and** content glob) — **reverted in the same step**, `git status --short gk-core/tests/core-test-projects.v1.json` empty and the manifest byte-identical to HEAD | `Failed! - Failed: 1, Passed: 3, Skipped: 0, Total: 4`, one message naming all three: `include 'ZZNoSuchFolder/**' matches nothing under gk-core/tests/FusionRpg.Core.Lawn.Tests/; link 'tests/FusionRpg.Core.Tests/ZZNoSuchLinkedFile.cs' does not exist; content 'ZZNoSuchFixtures/**/*' resolves to no file under 'ZZNoSuchFixtures'` | this fragment |
| the scoped run | `verify-change -Paths @('gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestReconciliationTests.cs') -Session tvb58` | `filemove-fallback (module)`; `TEST SUBSTRATE GUARD OK`; `Passed! - Failed: 0, Passed: 52, Total: 52` | this fragment |
| why this half had no witness | the code, read | A1 validates `include` against the **residual**, and after the increment the residual no longer holds those files, so the rule became uncheckable there; `links` are build-witnessed, but `content` are `None` items read at **run** time, so a missing one breaks only the test that reads it | this fragment |

**A correction to my own first measurement, recorded because it is the trap this repo warns about.** The first
pass resolved `content` against the repository root and reported **5 missing**. That was the check's bug: the
entries are MSBuild globs relative to the *project* directory (`../fixtures/effects/**/*` means
`gk-core/tests/fixtures/effects/`). Reading the entry's own shape — not the "missing file" symptom — is what found it.
