# TVB-F32 — a `tasks/**` docs edit plans the whole 673-test Guard project, and almost none of it can see the edit

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the selection | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/test-verification-boundary-todo.md','tasks/evidence-fragments/tvb60-lane-close.md') -PlanOnly -Session tvb58"` | both paths → `session-and-program-records (module)`; then `guard: session-boundary` and **`test: guard`** — the whole project, no filter | this fragment |
| what it costs | the same two paths through `verify-change` at this head (a docs-only change: one todo tick + one fragment) | `Failed: 1, Passed: 672, Skipped: 0, Total: 673, Duration: 9 m 38 s` — ~10 minutes, and the one red is the pre-existing routed `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` | this fragment |
| the coupling it protects, measured | `grep -rn "tasks/" gk-core/tests/FusionRpg.Guard.Tests/*.cs` | **5 of 114** files mention `tasks/` at all. Four are doc-comments (`NarrativeGuardContractTests.cs:8`, `PlantSideStatusGuardTests.cs:109`, `TestContentRootGuardTests.cs:8,11`). The only real dependency is `RepoBoundaryGuardTests.cs:13,114,115` — the B3 test freezes `tasks/plan.md` + `tasks/todo.md`, both frozen history files. `VerificationBoundaryWorkflowTests.cs:185-195` uses `tasks/reports/**` / `tasks/absent/**` as in-memory fixture strings | this fragment |
| no Guard test reads a session record | `grep -rn "tasks/sessions" gk-core/tests/FusionRpg.Guard.Tests/*.cs` | **0** matches, across all 114 files | this fragment |
| the one real contract is already guarded, so the test leg only re-proves it | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` table | `repo-boundary ci gating 0 2.30` — B3 runs as its own CI-tier guard; `RepoBoundaryGuardTests` only re-proves that guard fails on a planted violation in a temp repo | this fragment |
| why the narrowing is a ruling, not a lane's edit | `tasks/test-verification-boundary-todo.md:104` | TVB2.1's acceptance pins `session-and-program-records → module` as an asserted label, so re-labelling it `focused` overturns a test in `VerificationBoundaryWorkflowTests`; the other shapes drop the test leg for todos/fragments/plans | this fragment |

The registry has no `filter` field at all (`grep -c '"filter"' gk-core/scripts/verification-boundaries.v1.json` → 0), and
`testFiles` is the **pytest** selector (`scripts/lib/VerificationBoundaries.ps1:235` derives `focused` from
`verificationId` / `testFiles` / `selfSelect`), so for a dotnet `guard` project the only narrowing mechanism
is a `verificationId` trait — which lives in `gk-core/tests/FusionRpg.Guard.Tests/**`, the project this lane's edits
are refused on (the same refusal as `TVB-F26`).
