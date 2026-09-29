# The four pre-existing Core reds vs `knownRed` (manager task, 2026-09-20)

Deliverable as written: one row naming the four facts + the three registrable ones in `knownRed`, same
commit (H7). What the measurements say instead: **on this tip all four are already repaired**, and
`scripts/lib/VerificationBoundaries.ps1` D6 rule 3 fails any `knownRed` entry whose test RAN and PASSED
(`stale knownRed entry <test>: remove it and its red row`) — so registering them would turn a green tip
red. The registration is refused with proof, and an erratum is asked for in the row (TVB-F6).

| Criterion | Command | Result |
|---|---|---|
| The four facts named with `file:line` | `tasks/test-verification-boundary-todo.md` → TVB-F6 | row added |
| Pre-existing on the **integration branch** | independent audit of four lane tips + `live-qa`'s `cc2/core-tests.txt` | red there: 14833/14837 |
| Green on **this** tip | `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SocketOperationsTests\|FullyQualifiedName~UniqueCorpusTests\|FullyQualifiedName~FamilyExpansionTests"` | **77 passed / 0 failed** |
| Whole residual green on this tip | TVB5.7's `.\scripts\verify-change.ps1 … -Session tvb58` run | **14822 passed / 0 failed** |
| Two of the four names no longer exist here | `grep -rl The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement gk-core/tests/FusionRpg.Core.Tests` · `…Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute…` | no matches (renamed to their positive contract by `1fa3cef0`) |
| Why no entry can be registered | `grep -n "stale knownRed entry" scripts/lib/VerificationBoundaries.ps1` | the rule is present and fires on a passing entry |
| No `knownRed` change: the three are green here, so D6 rule 3 refuses them | `git diff --stat gk-core/scripts/verification-boundaries.v1.json` | empty — the registry is untouched, and its readers need no change |
| The sockwords fact routed as a stale test | `grep -n "ITEM-sockword-1" tasks/item-todo.md` | row added (asserts the retirement, not the corpus) |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths tasks/test-verification-boundary-todo.md,tasks/item-todo.md -Session tvb58` | **exit 1** — `doc-citations` scoped to `tasks/item-todo.md` reports **19 pre-existing HIGH** (D1/D3) at lines 275, 376, 3094, 3099, 5310, 6021, 6042, 7200, 7368, 7779, 8378, 8433, 8828, 8861, 8875, 8878, 9191, 9358, 9419 — none is this commit's row (10045); the run aborts there |

**NOT proved** (and not claimable): `guard: session-boundary` and `test: guard` never ran in that call —
verify-change stops at the first failing check, and the `doc-citations` check on `tasks/item-todo.md`
fails on the file's own inherited findings. `tasks/item-todo.md`'s 19 pre-existing HIGH citations are a
red this lane inherited, not one it caused, and they are not this task's to fix.
