# TVB5.8.k close — the drain's reading, and Checkpoint 5 lines 1–2

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| manifest project count | `python -c "len(json.load(open('gk-core/tests/core-test-projects.v1.json'))['projects'])"` | **68** | `gk-core/tests/core-test-projects.v1.json` |
| applied count | 68× `dotnet tools/FileMove/bin/Release/net8.0/FileMove.dll split gk-core/tests/core-test-projects.v1.json --project <name>` | **67 refused** (`[<name>] tests/<name> already exists`), **1 planned** (5 ops) | this fragment |
| the 1 not applied | same loop | project 30 `FusionRpg.Core.GlobalUsings.Tests` — TVB-F17, skipped in `8f3513c7c` | TVB-F17 |
| Core test csproj on disk | `glob tests/FusionRpg.Core*/FusionRpg.Core*.csproj` | **68** (67 + residual) | — |
| increment evidence | `ls tasks/evidence-fragments/tvb5-8-*.md` | **66** increment fragments; every applied name appears in one | `tasks/evidence-fragments/` |
| increment commits | `git log --all --format=%s --grep='TVB5\.8\.'` | **77** commits naming an increment | — |
| re-verified at `4369eda29` (orchestrator: "continue the increment stream in manifest order") — **no increment left** | `dotnet run --project gk-core/tools/FileMove -c Release --no-build -- split gk-core/tests/core-test-projects.v1.json --project <name>` for the **first** and the **last** `projects` entry | both `REFUSED: manifest fails 2 A1 rule(s)` — first cause `gk-core/tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests already exists`, same for `gk-core/tests/FusionRpg.Core.Workspace.Tests` | this fragment |
| re-verified: manifest against the disk | `python -c` over `gk-core/tests/core-test-projects.v1.json` + `os.path.isdir('tests/'+name)` | **67** `projects` entries, **67/67** directories present, **0** missing; `tests/FusionRpg.Core.*` = **69** = 67 + residual + `FusionRpg.Core.Tests.Shared`; **68** Core csprojs = 67 + residual | this fragment |
| re-verified: the wiring too | `grep` for `tests/FusionRpg.Core.*/*.csproj` in `scripts/test-fast.ps1`, `.github/workflows/ci.yml`, `.github/workflows/release.yml` | **68** Core csprojs in each, **0** manifest projects missing, residual present in all three | this fragment |
| re-verified: the **shared set** (`manifest.shared`, 4 entries) | `find gk-core/tests/FusionRpg.Core.Tests.Shared -type f` + `grep -l CoreTests.Shared.props tests/FusionRpg.Core*/FusionRpg.Core*.csproj` | **4/4** moved (`AssemblyInfo.cs`, `ContractTuningTestBootstrap.cs`, `TestSupport/ExternalProcess.cs`, `TestSupport/ToolProcess.cs`), **none** left in the residual, **68/68** Core csprojs import `CoreTests.Shared.props` | this fragment |
| re-verified: every applied project is structurally whole | `python -c` over the manifest: each `tests/<name>` has its own csproj and at least one `.cs` | **67/67**: 0 dirs without a csproj, 0 without a `.cs`; 6 projects carry `links`, 5 carry `content` | this fragment |
| re-verified: the one include pattern still matching the residual | `glob(gk-core/tests/FusionRpg.Core.Tests/<include>)` for all 67 entries | 1 hit: `FusionRpg.Core.Stats.Tests`' `Stats/**` → 3 files, and all 3 were added **after** that increment (`cb0f048fb` is an ancestor of each): `Stats/ActorLivenessRevisionTests.cs` (lawn LW1.4 `2f9a4fc60`), `Stats/ResourceRegenUnitTests.cs` (lawn LW2.1 `423579089`), `Stats/TurnChannelDeclarationTests.cs` (battle T17 `18139aec6`) | this fragment |
| the split's own definition of done | `docs/architecture/test-verification-boundary/spec-core-split-apply.md:157-159` (A5) | *"The split is **done** when every project in the approved manifest is applied; whatever the manifest leaves in the residual stays there. Emptying the residual is not a goal of this module."* → **67/67 applied = done** | — |
| Checkpoint 5 line 1 (W2/W3) | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary\|FullyQualifiedName~CoreTestProjectPolicy"` | `Passed! Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 6 m 36 s` | — |
| Checkpoint 5 line 2 (W5/W6) | same run | green; `ci.yml` 68 project pairs + 1 BalanceGuard pair, `release.yml` 68 | — |
| registry integrity | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` (438 boundaries) | — |
| citations the split's own move broke | `python scripts/audit-doc-citations.py --scope tasks/test-verification-boundary-todo.md` | `D1 8 (0 HIGH), D2 0, D3 0` — was `D1 9 (1 HIGH), D2 1 (1 HIGH), D3 2 (2 HIGH)` | this fragment |
| `verify-change` Guard module | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths @('tasks/test-verification-boundary-todo.md','tasks/evidence-fragments/tvb5-8-k-close.md','tasks/test-verification-boundary-ledger.jsonl') -Session tvb58` | `Failed: 2, Passed: 667, Total: 669` — both reds pre-existing and owned elsewhere (below) | — |

**Doc citations.** The split's own `Items` move broke two `file:line` citations in this todo
(`gk-core/tests/FusionRpg.Core.Tests/Items/{SocketOperationsTests,UniqueCorpusTests}.cs` →
`gk-core/tests/FusionRpg.Core.Items.Tests/...`) — the re-anchor rule was not applied when the move landed.
Also removed the stale first copy of the `TVB-F15-TPL` body (the fixed copy below it supersedes it).

**The two `verify-change` reds are not this change's** (a docs-only delta cannot move a hash or a
refusal-code count) and are already investigated and routed by lane `findings-2`:
`tasks/reports/findings-2-head-guard-reds.md` — `PlantSideStatusGuardTests` (W11 / `battle-derived-wire`)
and `PlayerSpeciesMaterialiseCallerGuardTests` (creature-seed T8).

Checkpoint 5 line 1 is true as **67/68**; the exception is one project with its own open row
(TVB-F17) and was recorded when the skip happened, not later. **Updated 2026-09-23:** TVB-F17 then
closed by option (b), so the manifest holds **67** `projects` entries and **all 67 are applied** — the
`68` in the first rows above is now 67 projects + the residual `FusionRpg.Core.Tests`. The stream is
therefore complete by the spec's own criterion (`spec-core-split-apply.md:157-159`, A5) at three
granularities: the 67 project directories, the 4-entry shared set (all moved, no residual duplicates,
68/68 csprojs importing `CoreTests.Shared.props`), and project structure (every dir has its csproj and
at least one `.cs`). The single include pattern that still matches a residual path —
`FusionRpg.Core.Stats.Tests`' `Stats/**` — matches only three files added *after* its increment by
other programs (lawn LW1.4, lawn LW2.1, battle T17), which is exactly the arrival A5 says the residual
keeps. The stale duplicate
`- [ ] **TVB5.7 …**` line above the lane's done copy was removed in this change: two rows shared one
id, so the census counted a finished task as open.
