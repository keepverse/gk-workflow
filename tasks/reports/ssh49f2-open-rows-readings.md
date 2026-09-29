# ssh49f2 — printed readings for the open strain-splice-host rows closed this session

One section per row, added in the commit that ticks it. Every reading below is a command that was run in
this worktree; the command text is copied verbatim.

## SSH-F1 — the Core.Tests socket-word pin was not retired with the corpus

**Verdict: done (verification only — the repair was already in the tree; the row was never ticked).**

| Command | Result |
|---|---|
| `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter "FullyQualifiedName~SocketOperationsTests"` | `Passed! - Failed: 0, Passed: 22, Skipped: 0, Total: 22` |
| `ls gk-data/packs/fusion/data/seed/items/socket-words/` | `combogen-migrate.ledger.json` — the retired `sockwords.json` is gone, as the row's fix asserts |

⚠ The row's own citation (the pre-split `gk-core/tests/FusionRpg.Core.Tests` path, line 334) is **stale**:
the Core.Tests split moved the file to `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs`
(now line 336) and the retirement test is named
`The_legacy_socket_word_corpus_is_retired_not_merely_unread`. Both facts are re-anchored by this row's tick
note, which is also one of the D3 sources `SSH4.9-F6` tracks.

## SSH-route-1 — `guard-magic-numbers` M2 HIGH + M4 LOW at `gk-core/src/FusionRpg.Server/ComboPricingBoot.cs:46`

**Verdict: done (verification only — SSH8.5's remedy removed the const).**

| Command | Result |
|---|---|
| `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` | `M1=0  M2=0  M3=0  M4=0` / `total 0 finding(s), 0 high` / `MAGIC-NUMBER GUARD OK — no M1/M2 findings` |
| `python gk-core/scripts/audit-magic-numbers.py --summary` | `TOTAL  0  0  0  0  0` |

The const the finding named is gone from the balance surface: `gk-core/src/FusionRpg.Server/ComboPricingBoot.cs:46-51`
now documents that the rung count is read from the LOADED `StrainSpliceTuning.TierLadder` and that the old
`const int TierLadderRungCount = 1` was "exactly what the magic-number guard's M2 flags". No audit
exemption and no scan widening was needed — remedy (a) in the row's own two options.

## SSH-route-2 — `guard-population-pin` P1 at `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:70`

**Verdict: done (verification only).**

| Command | Result |
|---|---|
| `pwsh -NoProfile -File scripts/guard-population-pin.ps1` | `total 0 finding(s)` — the P1 finding on `Assert.Equal(64, loaded.CombinationCorpusDigest.Length);` is gone |

## SSH-RED-1 — two `FusionRpg.Server.Tests` reds at the merged head `287a3256`

**Verdict: done (verification only — both named tests pass now).**

| Command | Result |
|---|---|
| `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo --filter "FullyQualifiedName~CombinationImportTests|FullyQualifiedName~BaseTypeSocketMaxCorpusTests"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7` |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo --no-build --filter "FullyQualifiedName~A_refused_recipe_is_never_seeded|FullyQualifiedName~A_base_row_above_its_role_ceiling_is_refused_at_load"` | `Passed FusionRpg.Server.Tests.CombinationImportTests.A_refused_recipe_is_never_seeded`, `Passed FusionRpg.Server.Tests.BaseTypeSocketMaxCorpusTests.A_base_row_above_its_role_ceiling_is_refused_at_load`, `Total tests: 2` |

Both methods the row named are green individually, so the row's "two reds at the merged head" no longer
holds at this HEAD.

## SSH4.9-F6 — the todo's own 14 pre-existing doc-citation HIGHs (this is the fix, not a reading)

**Verdict: done — every citation re-anchored; the file audits clean and no exemption was added.**

| Command | Result |
|---|---|
| `python scripts/audit-doc-citations.py --strict --scope tasks/strain-splice-host-todo.md` (before) | `14` HIGHs: 1 D2 + 13 D3 |
| `python scripts/audit-doc-citations.py --strict --scope tasks/strain-splice-host-todo.md` (after) | `377 resolvable citations checked`, `D1 0 / D2 0 / D3 0 / D4 0`, **exit 0** |
| `python scripts/audit-doc-citations.py --strict --scope tasks/reports/ssh49f2-open-rows-readings.md` | `0 HIGH`, exit 0 |
| `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | **exit 0** — `1686 documents, 25405 resolvable citations checked`, `869 D1 / 7 D2 / 56 D3`, **0 HIGH**. Repo-wide, not just this file: the 14 HIGHs were the difference |

The 14, and what each became:

| Citation | Fix |
|---|---|
| `tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs` (`:340`, line 124) and its `:334` sibling in SSH-F1's row | re-anchored to the post-split `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs:336`, with the old test name kept as prose |
| `tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs` (`:340`, SSH-F1's struck-through history) | current path, line-less, with `(then :340)` |
| six bare `run.py` line references (`:79`, `:105`) in SSH2.9's row | the full `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py` path for the NEW line numbers; the OLD numbers are prose ("line 79 -> 80"), so nothing points at a line that moved |
| two bare `deps.py` line references (`:85`, `:173`) in the same row | line-less, same grounds |
| `Program.cs` (`:374`, SSH5.10-P2's note) | `gk-core/src/FusionRpg.Server/Program.cs` + `(then :374)` — the line has moved since the note was written |
| `emit.py` (`:185`, in SSH2.9's note and TVB-F18's own row) | the full path with the line's disappearance stated on the line (it is past the file's 175 lines) |

⛔ No `citations-historical` marker, no audit exemption and no scan widening: the audit still reports D2/D3
as codes and simply finds none.

## SSH4.9-F5 — `/api/test/reset` did not clear `rpg_material_spend_log` (this is the fix)

**Verdict: done — the store resets the ledger, and a test reproduces the defect pre-fix and passes post-fix.**

| Step | Command | Result |
|---|---|---|
| reproduce, pre-fix | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --filter "FullyQualifiedName~A_reset_clears_the_spend_ledger"` | **FAIL** — `correlation 'ssh49f2-f85a7660-replay' was replayed after a reset: {"ok":true,"verb":"socket-add","reason":"replay","instanceId":"01c949851c764e00b074f7692fd3f2a9","opSeq":0,"replayed":true,"outcome":"replay",...}` — the second attempt named the FIRST chassis |
| prove, post-fix | same command | `Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1` |
| regression sweep | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | `Failed: 1, Passed: 236, Skipped: 0, Total: 237` — the single failure is `RpgScenarioSlice0E2ETests.First_session_forward_runs_green_and_its_squad_came_from_its_own_roster`, the pre-existing shared-factory flake named below, unrelated to this change (it fails with and without it) |

The fix is one line in `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`'s `Reset()` — `DELETE FROM rpg_material_spend_log;`
beside the souls and materials that reset already clears — with the why-comment that a reset which clears
what a verb spent must clear the ledger that says "this correlation already paid". The proof is
`tests/FusionRpg.E2E.Tests/SocketedGemCombinationE2ETests.A_reset_clears_the_spend_ledger_so_a_correlation_id_is_not_replayed`:
two real chassis, one correlation id, one reset between them, asserting `replayed == false` and that the
outcome names the second chassis.
