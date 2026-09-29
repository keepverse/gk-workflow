# TVB-F19 — `InScopeFile` accepts any file a session may write, and a code-free session is skipped

| Acceptance | Command | Result |
|---|---|---|
| the rule, not the record | `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` | `InScopeFile` now enumerates `"*"` (still skipping `obj`/`bin`), **prefers** a `.cs` file and falls back to any file, and returns `null` instead of throwing; an `internal` overload takes the root so a planted tree can pin it |
| a session with no code path is skipped | same file | new `ActiveSessionWithScope()` returns the first ACTIVE record whose fence resolves to a file; `Planner_accepts_an_explicit_path_within_the_active_session_scope` uses it and returns early when none does — no allowlist, no record edit, no population assertion |
| the behaviour is pinned by a fixture | `verification...In_scope_file_search_prefers_a_code_file_but_accepts_a_documentation_fence` | planted temp tree: `tasks/reports/note.md` only → that Markdown; add `Helper.cs` → the `.cs`; a literal path still wins; a fence that resolves to nothing → `null`; temp tree deleted in `finally` with the throwing `Directory.Delete` |
| the class that failed | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter FullyQualifiedName~VerificationBoundaryWorkflow` | **Passed! Failed: 0, Passed: 57, Skipped: 0, Total: 57, 4 m 19 s** — including the previously-failing `Planner_accepts_an_explicit_path_within_the_active_session_scope` and both load-fragile timeout cases |

Process lesson (the manager's own instruction, recorded so the next lane does not repeat it): a protected-path
refusal is a **GRANT REQUEST** — stop, say so in the fragment, and wait for the grant: this file and
`PlantSideStatusGuardTests.cs` were refused twelve times over several segments before one grant request's worth
of waiting would have cost nothing.
