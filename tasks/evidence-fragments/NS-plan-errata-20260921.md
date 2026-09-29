# NS plan status errata (2026-09-21) — the program's own plan, 10 statements

The plan is what a reader (or the manager) opens for program state, and it still sold A1/A2 as open gates
whose "default: waits". Corrected to what the ledger says, with the same dated style as the specs and the
map:

| Where | Was | Now |
|---|---|---|
| Relationship to the parent | "Feeds parent checkpoint CC7 (\"notifications wave 1–4\")" | waves 1–6, except Gate G2 (blocked) and the gated centre |
| Dependency diagram | "(catalog v2; G0 A1/A2)" / "(catalog v3; G0 A5)" / "(/idea-ui → owner review)" | A1/A2 landed · A5 · gated on the gui-lego row |
| Module table | "A1/A2 hold only their named tasks" | answered 2026-09-21, both accepted; their tasks landed |
| Phases | no status | new **Wave status (2026-09-21)** paragraph naming every open row and its blocker |
| CP5 | "Map G2 live probe …, after one full-suite run; … both hosts load v2" | fog tests unmodified/green ✓, both hosts load **v3** ✓, **G2 BLOCKED** (`WS-live-1`), full suite `not_run` |
| CP6 | "Map G3 (NS6.5 + the centre's capped history); owner review dated; full suite once" | G3's first half landed (NS6.5 `7/7`), centre gated, review not dated, suite owed |
| Cross-program edges | A1/A2: "sequencing edge; default: waits" | ANSWERED 2026-09-21: accepted, with what landed next to each |
| Risks | "A1/A2 unanswered stalls the world consumer — Med" | struck through as **resolved 2026-09-21**, residual blockers named |
| Defaults shipped behind | "A1, A2: no default; only their named tasks wait" | answered (both accepted); the tasks they held landed |

| Criterion | Command | Numbers printed |
|---|---|---|
| the plan's own boundary check | `powershell -NoProfile -Command ".\scripts\verify-change.ps1 -Paths 'tasks/notification-ssot-plan.md' -Session notification-ssot-20260920"` | plan maps to `session-and-program-records` -> `guard: session-boundary` + `test: guard`: `Failed! - Failed: 2, Passed: 578, Skipped: 0, Total: 580, Duration: 6 m 51 s` on `FusionRpg.Guard.Tests` — the two reds are `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (`:112`) and `SubprocessPipeDrainGuardTests.No_test_file_reads_stdout_then_stderr_synchronously` (offender `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs`), i.e. the board's own `CAI-guard-1` and `TVB-F2` rows, neither touched by this commit |
| citations in the edited file | the same run | `doc-citations` was not selected for this path; the file's own citations were checked by `guard-doc-citations.ps1 -Strict` in the previous segment (0 HIGH in this lane's fence) |

**Finding for the record:** a docs-only change inside this program **cannot** read green through
`verify-change` — the path maps to the whole `FusionRpg.Guard.Tests` project, whose two pre-existing reds
are owned elsewhere (`CAI-guard-1`, `TVB-F2`). That is why "verify-change is clean" claims are hard to
sustain for this lane; the per-row evidence quotes focused filters instead.

## Addendum — the centre spec's gate wording (2026-09-21)

`spec-notify-centre.md` opened with "awaiting owner review" and its contract list said "**Owner gate**
on pieces, payloads and the assembled look (step 7) **before** React". The owner declined to be that
reviewer and named the **gui-lego program** as the resolver (2026-09-21, recorded in
`tasks/notification-ssot-todo.md` NS6.8 and the map's gate-status paragraph), so a reader of this spec
was waiting for a personal review that is not what is outstanding. Both places now say what the gate
actually is — that program accepting the module's queue row (P4 · Notices) and dating it.

| Claim | Command | Numbers printed |
|---|---|---|
| the edited spec passes its own boundary check | `.\scripts\verify-change.ps1 -Paths 'docs/architecture/notification-ssot/spec-notify-centre.md' -Session notification-ssot-20260920` | maps to `docs-and-assistant-config (focused)` + `guard: doc-boundary`; `doc-citations` `D1 0 (0 HIGH)` / `D3 0 (0 HIGH)`; `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4, Duration: 32 s` |
