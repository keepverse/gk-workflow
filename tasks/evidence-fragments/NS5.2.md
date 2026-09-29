# NS5.2 — Move the fog rule into Core `WorldReportVisibility` (ask A2)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `VisibleTo(TurnReportEntry, …)`, `IsStaticFact`, `StaticFactDetailPrefixes` moved unchanged; `WorldEndpoints.cs` calls the Core type and the moved code is removed | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldTurnReportFog"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5` | gk-core/src/FusionRpg.Core/World/Intel/WorldReportVisibility.cs, gk-core/src/FusionRpg.Server/WorldEndpoints.cs |
| `WorldTurnReportFogTests` pass **without edits** (diff of the test file is empty) | `git status --short gk-core/tests/FusionRpg.Server.Tests/WorldTurnReportFogTests.cs` | empty output — the file is unmodified | gk-core/tests/FusionRpg.Server.Tests/WorldTurnReportFogTests.cs |
| the row's second Verify line (Core rule asserted directly) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldReportVisibility"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7, Duration: 49 ms` | gk-core/tests/FusionRpg.Core.Tests/World/Intel/WorldReportVisibilityTests.cs |
| the boundary's server scope, run directly to keep its tally | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | `Passed! - Failed: 0, Passed: 741, Skipped: 0, Total: 741, Duration: 2 m 14 s` | — |
| boundary command + guards | `.\scripts\verify-change.ps1 -Paths 'gk-core/src/FusionRpg.Core/World/Intel/WorldReportVisibility.cs','gk-core/src/FusionRpg.Server/WorldEndpoints.cs','gk-core/tests/FusionRpg.Core.Tests/World/Intel/WorldReportVisibilityTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK`; Core scope `Failed: 4, Passed: 14903, Skipped: 0, Total: 14907, Duration: 1 m 45 s` (the 4 are pre-existing, below) | — |

**Rule body copied verbatim.** The only edits inside it: two cross-assembly references in the doc
comment (`<see cref="WorldTurnReportFogTests"/>` -> `<c>`, and "this same endpoint" -> "the turn-report
projection"), which cannot resolve from Core. `VisibleTo(WorldCommand, …)` deliberately stayed in
`WorldEndpoints.cs` — the ruling moves the report-line rule, not the order rule.

**Re-read 2026-09-21 (after the integration head 4bce1fe5):** the boundary's Core scope still reports
`Failed! - Failed: 4, Passed: 15047, Skipped: 0, Total: 15051, Duration: 1 m 13 s`, i.e. the same
four tests below and nothing new; the swap in the passing count is the merged tree growing. They are
**not** registered as known-red either — `gk-core/scripts/verification-boundaries.v1.json`'s `knownRed` holds
5 entries and none matches `UniqueCorpus`/`FamilyExpansion`/`SocketOperations` (checked 2026-09-21).

**The 4 Core failures are not this task's:** `Items.UniqueCorpusTests.Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute`,
`Atoms.Generation.FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte`,
`Items.SocketOperationsTests.The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement`
and `…No_shipped_gem_declares_an_omni_affinity`. Already owned and filed:
`tasks/atom-family-expansion-todo.md:624-632` (the byte-for-byte drift, with its own repro) and
`tasks/action-todo.md:2552` (the item-corpus cluster, another session's files). No item/atom/socket
path is in this task's diff.

**NOT proved:** no live probe (the moved rule is exercised through the real endpoint and the Core
tests); the 11 non-fog Server tests that call the same rule were not re-run individually — the fog
filter and the boundary's Server scope cover them.

**Correction 2026-09-21 (head 287a3256):** the four Core reds this fragment records are **fixed** — the
whole Core project now reads `Passed! - Failed: 0, Passed: 13180, Skipped: 0, Total: 13180`, and the three
classes in question (`UniqueCorpusTests`, `FamilyExpansionTests`' byte-for-byte case,
`SocketOperationsTests` x2) pass `Passed! 41/41` on their own filter.

**Superseded 2026-09-21 by tvb58's Core test-project split:** see the post-split re-measure in `tasks/evidence-fragments/NS-reverify-20260921.md` Addendum 8 — this lane's tests stayed in `gk-core/tests/FusionRpg.Core.Tests` (83/83 on our scope), while the project total is now 12,704 with 2,404 more across eleven split projects.
