# DM-F2 — `/api/sim/effect/*` gated like its siblings

Lane `dmf2` (session `debug-mcp-f2-20260922`), worktree `.claude/worktrees/cmdc-dmf2` (branch `cmdc/dmf2`),
2026-09-22. Row: `tasks/debug-mcp-todo.md` DM-F2. Owner ruling:
`tasks/rpg-simulator-decisions.md` F1 → **(b) drift, gate it**.

**Cause (read from the code, not the citation).** `gk-core/src/FusionRpg.Server/Program.cs:2050` mapped
`/api/sim` + `/api/test` behind `if (SimFlags.Enabled)` (`:2051`), while `:2053` called
`app.MapSimEffect()` on the next statement *outside* that block — so the six `/api/sim/effect/*` routes
(`gk-core/src/FusionRpg.Server/SimEffectEndpoints.cs:12`) existed on every server, a live owner run included.
Owner ruling: drift, not intent.

**Gated, not documented-ungated.** `app.MapSimEffect()` now sits inside the same
`if (SimFlags.Enabled)` block as `app.MapSimAndProbes()`. `SimEffectHost` stays registered
unconditionally (`gk-core/src/FusionRpg.Server/Program.cs:501`) — it is the DI singleton the gate-off host simply never routes to, and
`SecondaryEffectE2ETests` reaches it through the shared fixture, which boots with `FUSIONRPG_SIM=1`.

**No ungated consumer exists** (the brief's hand-back condition, checked before gating):
`grep -rn "sim/effect\|simEffect" --include=*.cs --include=*.ts --include=*.tsx --include=*.py --include=*.ps1 .`
returns only `SimEffectEndpoints.cs` (the registration) and
`gk-core/tests/FusionRpg.E2E.Tests/SecondaryEffectE2ETests.cs`
(three `POST`s, through `RpgApiFactory`, whose constructor sets `FUSIONRPG_SIM=1`). No web, `tools/` or
Python caller. Nothing needs the surface while the sim is off.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Gate ON: the real bootstrap serves the effect route | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~SimEffectGateHostTests"` | 2 passed / 0 failed | `With_the_sim_flag_set_the_effect_routes_serve` — `POST /api/sim/effect/clear` → 200 + `revision` |
| Gate OFF: the effect route is absent | same | 2 passed / 0 failed | `Without_the_sim_flag_the_effect_routes_are_absent` — a **second real `Program` boot** with `FUSIONRPG_SIM` cleared: `/health` 200 (host booted), then the effect route answers exactly like a control bogus route, and the booted host's `EndpointDataSource` holds **no** `/api/sim/effect` pattern |
| **RED proof** — the test fails on the pre-fix shape | planted `app.MapSimEffect()` back outside the guard, ran the gate-OFF test, reverted | **1 red**: `Expected: MethodNotAllowed, Actual: OK`; both green again after revert | no assert removed, no `Skip` added |
| Whole E2E project | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <3 changed paths> -AllowUnscoped` | `Failed: 0, Passed: 233, Total: 233` (2 m 17 s) | new tests are 2 of the 233 |
| Whole Server project (`server-fallback`) | same | `Failed: 0, Passed: 803, Total: 803` (2 m 59 s) | — |
| Doc citations (the gate moves lines 2053+) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` | exit 0 — 25345 citations checked, D2 7 (0 HIGH), **no** new breakage | `docs/architecture/rpg-simulator-idea.md:141` / `-shape-idea.md:64,469` still resolve; they are the *finding* record and `docs/**` is outside this lane's fence, so they are left as filed |

**Why "absent" is asserted as 405 + an empty route table, not 404 (the acceptance's literal wording).**
`Program.cs` ends with `MapFallbackToFile("index.html")`, whose catch-all pattern matches every non-dotted
path and whose method metadata is `GET,HEAD`. A `POST` to a path the host does not serve is therefore
answered `405 Method Not Allowed` with `Allow: GET,HEAD` — measured on a control route
(`/api/definitely-not-a-route-xyz` → 405, same `Allow`) in the same test. A literal 404 is unreachable on any
host with an SPA fallback, and a `GET` probe would be *worse*: on a real server it gets 200 + `index.html`
from the fallback regardless of the gate. So the test asserts the effect route's status against that control
and reads the route table directly, which is the precise claim ("no `/api/sim/effect` endpoint is
registered").

**NOT PROVED / deviation.**
1. **The brief's verification line cannot run as written.** `verify-change.ps1 -Session debug-mcp-f2-20260922`
   hard-throws at `scripts/verify-change.ps1:98` — `session record not found: debug-mcp-f2-20260922`; no such
   record exists for this lane anywhere in the repo (`ls tasks/sessions/ | grep -i "debug-mcp"` → only the
   2026-09-13/14 records `debug-mcp-build`, `debug-mcp-idea`, `debug-mcp-live-readiness`). `tasks/sessions/**` is
   **outside** this lane's allowed paths, so the lane cannot write it (the `/session-start` /
   session-and-program-records owner does). The strongest achievable equivalent was run instead — the same
   command with `-AllowUnscoped`, which resolves the same owners, tests and guards and skips only the
   session-scope assertion. An erratum ruling is requested from the manager.
2. Not run: a real `FusionRpg.Server.exe` process probe (the E2E host is the in-process real bootstrap; the
   out-of-process lane is the simulator program's own). No live deploy — the sim surface is a developer
   surface, nothing injector-side reads it.
