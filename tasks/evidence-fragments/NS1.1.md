# NS1.1 — Verification mapping for the notify path families

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| C# path families mapped (10 new owner rows: Core Notify/World-Notify, Contracts, Server Notifications/Endpoints/PlayerPush/PlayerConnectionRegistry, Data store, Guard catalog test, tuning v1) | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | gk-core/scripts/verification-boundaries.v1.json |
| registry's own validation passes | `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json -Session summoner-convergence-lane-d3-20260919` | `Passed! - Failed: 0, Passed: 14, Skipped: 0, Total: 14` | FusionRpg.Guard.Tests.dll |

**Finding, not fixed here (blocked — protected pipeline file):** `verify-change.ps1` has zero
`web/**` execution support repo-wide, for every program, not just this one — its `projects` map
holds only `.csproj` files and its execution step always runs `dotnet test`. There is no npm/vitest
branch. Confirmed live: `verify-change.ps1 -Paths gk-web/web/fusion-rpg-web/src/shell/Toasts.tsx -PlanOnly`
throws `VERIFICATION BOUNDARY MISSING` for an existing, already-shipped file. Adding a `web` pseudo
"project" entry would make `verify-change.ps1` call `dotnet test` on a non-project path — worse than
the current loud failure. `verify-change.ps1` is a listed protected pipeline file
(`.claude/cmdc-agents/rules.md`), so it is not edited here. Per the brief, NS web changes are
verified directly: `cd web\fusion-rpg-web; npx vitest run <dir>; npm run build` — never through
`verify-change.ps1`. Web-owning boundary rows are intentionally not added to this registry, since a
row that cannot execute is worse than an honest gap.
