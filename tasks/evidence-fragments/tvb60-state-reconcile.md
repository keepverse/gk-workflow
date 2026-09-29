# tvb60 — the state surface reconciled: why "continue the increment stream" kept being asked

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the queue that kept the loop alive | `python gk-core/scripts/anchor-ledger.py tasks/test-verification-boundary-ledger.jsonl resume` **before** | `queue   : TVB4.7, TVB5.7, TVB5.8, TVB5.9, TVB6.1, TVB6.2, TVB6.3, TVB6.4, TVB6.5` — **eight already-done ids plus one blocked**, so the one line a dispatcher reads first still named `TVB5.8`, the increment stream, as queued work; `next    : pick the next task in todo order` | this fragment |
| the ledger/todo disagreement | the ledger's `task` events for `TVB-F3`/`TVB-F25`/`TVB-F26` vs their todo rows | `done` listed all three while their rows are still `- [ ]` (`:589`, `:1176`, `:1202`) — each row names its own residual, so the ledger and the todo disagreed on three ids | this fragment |
| the open rows the ledger did not know | `resume`'s `blocked:` list vs `grep -n "^- \[ \]" tasks/test-verification-boundary-todo.md` | **6** blocked ids against **15** open blocks: `TVB-F1`, `TVB-F5`, `TVB-F6`, `TVB-F7`, `TVB-F24` and the three re-opened rows had no ledger event at all, so a reader of `resume` alone under-counted the open set by more than half | this fragment |
| the reconciliation | `anchor-ledger.py <ledger> queue --ids "…"` plus `task --state started` then `--state blocked` for the eight, each with its exact blocker | ledger 186 → **203** events; `check` → `LEDGER OK (203 events)` | this fragment |
| the state surface after | `resume` | `queue` = the **14** remaining rows and no drained wave; `done` = only genuinely closed ids; `blocked` = **14** rows each with its exact reason; `active  : none` | this fragment |
| the header, and the census still counts the rows | `python .claude/cmdc-agents/scripts/convergence-census.py --json "$TEMP/tvb-census.json"` | `test-verification-boundary: blocks 15, blocks_unfiltered 15, residue 1, closed_by_header None`, and the program is absent from the header-closed list (`header-closed programs … (0 by construction)`) — the new dated header line deliberately avoids the census's closed-by-header vocabulary, so the **15** open blocks stay counted | this fragment |
| the drain itself, unchanged | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/… --filter "FullyQualifiedName~SplitManifestReconciliationTests"` | `Failed: 0, Passed: 3, Skipped: 0, Total: 3` — no increment exists (67/67 applied, re-measured in `tvb5-8-k-drain.md`) | this fragment |

No code changed here: this is the program's own state surface, and the ledger is append-only, so the earlier
`done` events stay in the log and the re-open is a new `started`/`blocked` pair beside them.
