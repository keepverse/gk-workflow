# TVB-F9 — no `knownRed` entry is warranted: all four are GREEN at the merged head

The row's measurement is from the integration head `0a5c7415` (and `ssh27`'s tip `4e94fd92`). Re-measured by
lane `tvb58` at the merged head `386a29c4` (this branch with `features/mega-merge` `30c585de` merged in):

```
dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release \
  --filter "FullyQualifiedName~SocketOperationsTests|FullyQualifiedName~UniqueCorpusTests|FullyQualifiedName~FamilyExpansionTests"
-> Passed! - Failed: 0, Passed: 77, Total: 77

dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release   # the suite that runs them
-> Failed: 1, Passed: 579, Total: 580    # the one failure is CAI-guard-1, not one of these four
```

| Fact the row names | State here | Why |
|---|---|---|
| `SocketOperationsTests.No_shipped_gem_declares_an_omni_affinity` | green | `1fa3cef0` (this branch) asserts the offender set is empty; `features/mega-merge` carries an equivalent repair — the merge kept the integration branch's prose, and both sides have identical assertions and the same 22 test methods |
| `SocketOperationsTests.The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement` | green | the name does not exist here: `1fa3cef0` renamed it to the positive contract (`…is_retired_and_combination_is_the_only_kind`), which asserts the retirement (`sockwords.json` absent) |
| `UniqueCorpusTests.Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute` | green | renamed by the same commit to `No_shipped_unique_carries_a_family_its_own_frame_cannot_execute`, asserting `Assert.Empty(findings)` |
| `FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte` | green | `be986658` regenerated `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json` (the tree was stale after `e1d9103e` dropped the `utility` tag) |

**No `knownRed` entry is added**, and that is the acceptance's own first branch ("either fixed … then the
entry is not needed"). Registering them would also be refused by the tooling: `scripts/lib/VerificationBoundaries.ps1`
D6 rule 3 fails any entry whose test RAN and PASSED — `stale knownRed entry <test>: remove it and its red row`
— so an entry here would turn a green suite red on the first run that executes them.

What is left for the manager is inventory wording, not code: a tip without `1fa3cef0`/`be986658` still prints
`RED (unregistered failure(s))` for these four, so CC8's inventory should cite *this* measurement (and the
tip it was taken at) rather than register debt for tests that pass. The routing to `tasks/item-seedgen-todo.md`
(`ISG-F1`) is unchanged and still correct for those older tips.
