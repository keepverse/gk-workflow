# TVB5.7 precondition — the four pre-existing `FusionRpg.Core.Tests` reds

`FileMove split --apply` (TVB5.7's own gate) builds and tests the residual `FusionRpg.Core.Tests`
before keeping an increment. That project is red at HEAD for four reasons unrelated to any move, so
the gate reverted. All four are stale pins invalidated by work already landed in HEAD. Three are
repaired here; the fourth needs a generator rerun outside this lane's fence.

| # | Failing test (line after repair) | Cause read from the code/data | Result |
|---|---|---|---|
| 1 | `tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs:313` `No_shipped_gem_declares_an_omni_affinity` | `39fbed34` stopped forwarding the element pick into `affinityElement`, so the offender list is legitimately empty | repaired to `Assert.Empty`; passes |
| 2 | `tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs:334` `The_legacy_socket_word_corpus_...` | `e79c0fde8` (SSH2.6) deleted `sockwords.json`; the test still opened it | rewritten as a retirement guard; passes |
| 3 | `tests/FusionRpg.Core.Tests/Items/UniqueCorpusTests.cs:522` `Three_shipped_uniques_...` | `12175b3d` regenerated the corpus, so `UniqueCorpusValidator.Validate` returns zero | renamed + `Assert.Empty`; passes |
| 4 | `tests/FusionRpg.Core.Tests/Atoms/Generation/FamilyExpansionTests.cs:213` `Committed_generated_files_match_the_generator_byte_for_byte` | `e1d9103e` dropped the `utility` tag from `gk-data/packs/fusion/data/seed/items/affix-families/g-evade.json:82-83`; `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json:507` was not regenerated | repaired in `tvb58`: regenerated via `dotnet run --project gk-forge/tools/FamilyExpandGen` (+5/−10, five rows lose `"utility": "1"`), committed with AFE-F1/ISG-F3 closed — see `tvb5-7-regen.md` |

The `FamilyExpansionTests` change also adds `RealStatusAnchor()`, mirroring
`gk-forge/tools/FamilyExpandGen/Program.cs:187-207`, so the byte-compare now exercises the `status.apply` rows
the committed tree was produced with (previously they refused and were not compared).

| Criterion | Command | Result |
|---|---|---|
| The four reds pre-date any repair | `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --filter "FullyQualifiedName~FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte\|FullyQualifiedName~UniqueCorpusTests.Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute\|FullyQualifiedName~SocketOperationsTests.The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement\|FullyQualifiedName~SocketOperationsTests.No_shipped_gem_declares_an_omni_affinity"` | 0 passed / 4 failed |
| Repaired tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --filter "FullyQualifiedName~FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte\|FullyQualifiedName~No_shipped_unique_carries_a_family_its_own_frame_cannot_execute\|FullyQualifiedName~The_legacy_socket_word_corpus_is_retired_and_combination_is_the_only_kind\|FullyQualifiedName~No_shipped_gem_declares_an_omni_affinity"` | 3 passed / 1 failed (only #4) |
| Stale generated tree | `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | exit 1, `family-expand.g-evade.json` |
| Doc citations (rule 3, shrink committed) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0 |
| Boundary guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` |

Findings routed per rules.md (rule 2): `tasks/item-seedgen-todo.md` (ISG-F1/F2/F3),
`tasks/strain-splice-host-todo.md` (SSH-F1), `tasks/atom-family-expansion-todo.md` (AFE-F1).

No commit for the three repaired pins: they landed in `1fa3cef0` (this fragment is that commit's
record). Row 4 was fixed by `tvb58` in its own commit (the regen above), after the pipeline
`.github/workflows/*.yml` guard was lifted for that lane and `gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs`
+ `FusionRpg.slnx` were added to its fence. The manifest correction `gk-core/tests/core-test-projects.v1.json`
(`coreInternals` → true, proved by the gate's new-project build+test) shipped in `c9e1c902`.
