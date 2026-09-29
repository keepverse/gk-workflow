# `CAI-find-3` — a bare interpreter name is a pattern, not one test

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Found while verifying `CAI2.3`: the suite that holds one of
its four named acceptance suites is environment-dependent.

## Measured

`gk-core/tests/FusionRpg.Core.Balance.Tests`, same commit, only the ambient PATH differing:

| PATH | Result |
|---|---|
| without `python` (the agent shell) | **2 failed / 208 passed** — `ResidualFitLoopTests.FullChain_onAThrowawayDomain_actuallyPublishes_andTheResultParsesAndBinds`, `ResidualFitLoopTests.PostPublishVerification_warnsHonestly_whenTheFitDidNotFullyCloseTermination` |
| with `python` prepended | **210 passed / 0 failed** |

The cause is `gk-core/tools/ResidualFitLoop/Program.cs:227` — `new ProcessStartInfo("python")`. The test drives the
TOOL's own publish step by design (`--domain` exists precisely so it can), so the tool's bare interpreter
name decides whether the suite can run at all. The failure is a `Win32Exception: cannot find the file
specified` from `Process.Start`, not an assertion.

This matters beyond tidiness: `ResidualFitLoopTests` is one of the four suites `CAI2.3`'s acceptance names
("`DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests` green and
unchanged"), so on such a PATH that line cannot be evaluated at all.

## The four sites, and where each can be fixed

| Site | Name | Fix location |
|---|---|---|
| `gk-core/tools/ResidualFitLoop/Program.cs:227` | bare `python` | `tools/**` — **out of every combat-ai lane's fence** |
| `gk-core/tests/FusionRpg.Server.Tests/RealRunCollectorTests.cs:162` | bare `powershell` | `tests/**` — **in every combat-ai lane's fence** |
| `scripts/guard-doc-citations.ps1:15` | bare `python` | pipeline/protected — no lane may edit |
| `scripts/verify-change.ps1:27` | bare `powershell` | pipeline/protected — no lane may edit |

The last two were hit directly this session: the doc-citation guard could not start until `python` was
prepended to PATH, and `verify-change` could not start until the Windows PowerShell directory was.

## The remedy, and the choice

**(a)** resolve the host explicitly at each site — a `%SystemRoot%`-anchored PowerShell path, `sys.executable`
for a Python child — which makes an agent shell and a minimal CI runner behave like the owner's machine; or
**(b)** declare the PATH precondition once (the guards and `verify-change` already assume it) and keep the
sites as they are, documenting the fragility.

Both are defensible; (b) is cheaper and (a) is what stops this class recurring. **Not chosen here:** the
sites span three fences including two protected pipeline paths, so it is a repo-wide ruling rather than a
lane's edit.

## NOT proved

- **Nothing was changed**, so no build or test beyond the two Balance runs above.
- **The four sites were found by the ones this session hit, not by a repo-wide scan for
  `ProcessStartInfo` with a bare name.** There may be more; a scan is the first step for whoever takes this.
- **CI was not checked.** `ci.yml` may already provide both interpreters on PATH, in which case this is an
  agent-shell and minimal-runner problem rather than a CI one — which changes the remedy's urgency, not its
  shape.

## The original instance, re-measured — it is green when PATH is right

The row's original reading (cai2, 2026-09-23) was `gk-core/tests/FusionRpg.Server.Tests` **823 passed / 2 failed**,
both failures being `RealRunCollectorTests`. Re-run on the merged head with the Windows PowerShell
directory on PATH:

```
gk-core/tests/FusionRpg.Server.Tests   ->  Passed!  - Failed: 0, Passed: 858, Skipped: 0, Total: 858
```

**858 / 0** — so the two cases are not broken, they are environment-dependent, and the suite has since
grown from 825 to 858 tests (other lanes' work landed). That sharpens the finding rather than softening it:
nothing here is a failing assertion, which is exactly why it went unnoticed — a suite that passes on the
owner's machine and cannot start on another is invisible until someone else runs it.

## The full inventory (the scan the four sites implied)

A repo-wide scan of `*.cs` (`new ProcessStartInfo("…")`, `FileName = "…"`, `Process.Start("…")`), `*.ps1`
(`& name`, `Start-Process name`) and `*.py` (`subprocess.*([ "name"`) for a spawn whose command is a bare
interpreter name — excluding comments, and excluding `bin`/`obj`/`node_modules`/`dist`:

| Interpreter | Sites |
|---|---|
| `dotnet` | 32 |
| `powershell` | 27 |
| `python` | 18 |
| `npm` | 1 |
| **total** | **78** |

By location, the three blocks that matter:

| Location | Sites | Why it matters |
|---|---|---|
| `gk-core/tests/FusionRpg.Guard.Tests/**` | 27 (23 files with `FileName = "powershell"`) | the whole guard suite is un-runnable without `powershell` on PATH — and `guard-*` is what `verify-change` selects for most changes |
| `gk-core/scripts/checks/**` | 15 | the generator `--check` steps |
| `scripts/verify-change.ps1` | 4 — `:27` `powershell`, `:248`, `:266`, `:279` `python` | **the mandated verification gate for every lane** |

Plus the two tests this lane hit: `gk-core/tools/ResidualFitLoop/Program.cs:227` (bare `python`, gating
`ResidualFitLoopTests`, one of `CAI2.3`'s four named suites) and
`gk-core/tests/FusionRpg.Server.Tests/RealRunCollectorTests.cs:162` (bare `powershell`).

## What the inventory changes

It makes remedy **(a)** — resolve the host explicitly at each site — a 78-site change spanning `scripts/**`
(protected pipeline paths), `tests/**` and `tools/**`, rather than a four-site tidy-up. That does not make
(a) wrong; it makes it a deliberate repo-wide programme rather than a drive-by, and it makes **(b)** — state
the PATH precondition once, where a lane reads it — the proportionate answer. Either way the precondition is
currently *implicit*, which is why an agent shell missing `powershell` and `python` breaks the gate that
tells it whether its work is acceptable.

**What the scan cannot see, stated so the inventory is not over-trusted:** a spawn built from a variable
(`& $interpreter …`), a `ProcessStartInfo` whose `FileName` is assigned later, or a script invoked through a
wrapper is invisible to it. 78 is a floor, not a total.

## The Guard project: 15 reds, 12 of them this pattern

The strongest confirmation of the pattern came from running a CI project in this shell. `dotnet test
gk-core/tests/FusionRpg.Guard.Tests`, same commit, only PATH differing:

| Interpreters on PATH | Result |
|---|---|
| `python` + `powershell` (the agent shell as it starts) | **15 failed / 658 passed** |
| `+ pwsh` | **5 failed / 668 passed** |
| `+ pwsh` + `dotnet` | **3 failed / 670 passed** |

So **12 of the 15** were this pattern, and it names two interpreters the scan's regexes did not catch —
`pwsh` (spawned in `gk-core/tests/FusionRpg.Guard.Tests` via `TestSupport/ExternalProcess.cs`, whose failure is
`Win32Exception: cannot find the file specified` for `pwsh`) and `dotnet` (spawned by
`scripts/regen-class-system-baselines.ps1:107`, which is why both `ClassSystemBaselineRegenTests` cases
failed with `The term 'dotnet' is not recognized`). The scan's own caveat — "a spawn built from a variable
is invisible to it" — is exactly what these two are.

The remaining three are real and are **`CAI-find-6`**: `CAI-guard-1`'s `BattleEffects` baseline, a new
pytest project with no CI step, and a grown pick-refusal vocabulary whose guard was not updated.

That reading is the useful form of this finding: **a CI project that passes on the owner's machine reports
15 reds to anyone else**, and only three of them are defects.

## The merged head, every project this lane can reach

Run with `dotnet`, `pwsh`, `powershell` and `python` all on PATH, so the bare-interpreter pattern above is
out of the way and only real reds remain:

| Project | Result |
|---|---|
| `gk-core/tests/FusionRpg.Core.Tests` | **9720 / 0** |
| `gk-core/tests/FusionRpg.Core.Balance.Tests` | **210 / 0** (goldens byte-identical across this lane's four Core changes) |
| `gk-core/tests/FusionRpg.Core.Match.Tests` | **182 / 0** |
| `gk-core/tests/FusionRpg.Server.Tests` | **858 / 0** |
| `gk-core/tests/FusionRpg.Data.Tests` | **1885 / 0** |
| `gk-fusion/tests/FusionRpg.Injector.Tests` | **114 / 3** — the three are `CAI-find-1`'s stale flag assertions |
| `gk-core/tests/FusionRpg.Guard.Tests` | **670 / 3** — `CAI-guard-1` plus `CAI-find-6`'s two |

So the merged head is green everywhere except **five** named reds, four of which are filed in this program's
todo (`CAI-find-1`, `CAI-guard-1`, and `CAI-find-6`'s two) and one of which is `CAI-guard-1`. The same
projects report **12 further reds** to a shell without the interpreters, which is this report's subject.
