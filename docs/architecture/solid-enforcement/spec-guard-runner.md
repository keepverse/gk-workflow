# Spec: `guard-runner`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 0** · depends on:
`enforcement-registry`.

## Objective

**One place decides which guards run where.** Before this module, three hand-kept lists disagreed:
`ci.yml` ran 8 guards, `deploy-play` ran 16, and `verify-change.py` resolved guard ids through a
third map inside `verification-boundaries.v1.json`. Every new guard had to be added to all three by
hand, and nothing noticed when one was missed. That is the mechanism that left nine guards unwired.

After this module, `gk-core/scripts/run_guards.py` reads `enforcement-registry.v1.json` and every caller
invokes it. Wiring a guard means editing one registry row, which is Open/Closed applied to the
enforcement layer: extend by data, never by editing three scripts.

### AMENDED 2026-09-26 — which callers exist, and why the deploy is not one of them

The module above removed the hand lists but left the runner wired into the **deploy**, and that was
wrong: it made every deploy pay the whole suite. Owner ruling 2026-09-26, and the measurement behind
it — `--tier local --include-backlog` selects the WIDEST tier (every `ci` guard plus the machine-only
ones, plus the report-only rows): **28 guards, 203 seconds**, run before a deploy whose
measured stages come to **28.3 seconds** up to the publish (game lock 0.14s, game-profile
0.62s, FE build 21.5s, injector build 5.8s, freshness 0.24s — 2026-09-26, default MelonLoader
install), and green on all four occasions it ran. A gate that is green every time it runs
before an operation it cannot be broken by is not a gate; it is a tax, and paying it
repeatedly while diagnosing an unrelated failure is what made one deploy cost 16 minutes.

**The 28.3s is a partial reading, not a deploy total.** The publish and every stage after it
were unmeasured that day: another session's server held `dist/` open, so the publish refused
with MSB3021 and the deploy stopped there — which is itself the correct behaviour, named and
non-zero. The FE build dominates what was measured and moves with the web tree; it is the
stage to look at first when a deploy feels slow, and `--no-rebuild-ui` skips it. Measure
before citing: `deploy-play.py --json` prints per-stage seconds for the run you actually did.

**The rule now:**

| Caller | Guards it runs | Why |
|---|---|---|
| `.github/workflows/ci.yml` | `run-guards.ps1 -Tier ci -CiRange …` | the merge gate |
| `.github/workflows/release.yml`, `nightly.yml` | `run-guards.ps1 -Tier ci -CiRange …` | the release gate |
| `gk-core/scripts/verify-change.py` | the ids `verification-boundaries.v1.json` assigns to the **touched paths** | the implement phase's gate — where a change is verified, once |
| `gk-fusion/scripts/deploy-play.py` | **`-Only game-profile -Tier local`** and nothing else | a deploy PRECONDITION (right bridge into the right install), not a suite. Running it is part of deploying correctly |

So `deploy-play` appears in the runner's callers for exactly one id whose *position* is part of its
meaning, and it must never run a tier batch. `GuardWiring.AssertDeployRunsNoGuardSuite` in
`gk-core/tests/FusionRpg.Guard.Tests/TestSupport/GuardWiring.cs` pins that: it scans the deploy's CODE
(docstring and comments dropped, string literals kept) and fails on any `-IncludeBacklog`, or on an
invocation of `run_guards.py` that does not name one id via `--only`. A `local`-tier guard can never
run in CI (it needs a game install or interop assemblies), which is why `injector-compile` is gated
by the implement phase through `verification-boundaries.v1.json` and `game-profile` by the deploy
precondition.

## Design

### `gk-core/scripts/run_guards.py`

```powershell
.\scripts\run-guards.ps1 -Tier ci              # every tier=ci, status=gating guard      (CI, merge gate)
.\scripts\run-guards.ps1 -Tier local           # ci + local gating guards               (the widest tier; NOT the deploy)
.\scripts\run-guards.ps1 -Only dal,test-substrate   # the named ids                      (verify-change)
.\scripts\run-guards.ps1 -Tier ci -IncludeBacklog   # also run backlog guards, report-only (module work)
```

Behaviour, and why each rule exists:

1. **Each guard runs in its own child process** (`pwsh -NoProfile -File <script>`), and its exit code
   is read from that process. `ci.yml` already records the hazard in a comment: guard scripts call
   `exit`, so running two in one shared pwsh block can make the second one unreachable. A child
   process makes that structurally impossible.
2. **Run all of them, then fail.** Every selected guard runs even after one fails, and the runner
   prints a summary table (`id · tier · status · exit · seconds`) before it exits non-zero. One red
   guard must not hide a second: that is the masking defect this repo already met in `ci.yml`'s old
   `dotnet test` step, which only checked the last exit code.
3. **`status: backlog` guards never fail the run.** With `-IncludeBacklog` they run and print under
   a `BACKLOG (not gating)` header. Without it they are skipped. This is the "report-only is a step,
   never a finish" rule: the registry, not the runner, is where a guard moves from backlog to gating.
4. **Per-guard arguments come from the registry,** never from the caller. `guard-generated-seed`
   needs `-Range HEAD~1..HEAD` in CI, so its row gains an optional
   `"args": { "ci": ["-Range", "{ciRange}"] }`. The runner substitutes `{ciRange}` with CI's existing
   fallback logic (`HEAD~1..HEAD`, or none on a root commit), moved here unchanged.
   `guard-game-profile` needs `-GameDir`/`-ExpectedProfile`, which `deploy-play` passes through
   `-LocalArgs @{ 'game-profile' = @{...} }`. That is the one caller-supplied exception, because
   the values are machine-local by definition and must never be committed.
5. **Unknown ids fail loudly.** `-Only foo` for an id not in the catalog throws. `verify-change`
   already does this through its own map (`throw "unknown guard: $id"`).

### Removing the three lists

| Caller | Before | After |
|---|---|---|
| `.github/workflows/ci.yml` "Boundary guards" step | 8 hand-written calls | `.\scripts\run-guards.ps1 -Tier ci` |
| `ci.yml` "Verification-boundary integrity" step | its own step, deliberately | **stays its own step.** It guards the registry `verify-change` reads, and the existing comment explains why it must not share a block |
| `scripts/deploy-play.ps1` lines ~168–250 (retired 2026-09-26; `gk-fusion/scripts/deploy-play.py` replaced it) | 14 hand-written calls plus a bespoke class-system G3 tolerance block | **removed entirely** — a deploy runs no guard suite. The G3 tolerance the block encoded is the registry's `class-system: backlog` row, which the runner reports without failing |
| `gk-fusion/scripts/deploy-play.py` (replaced `deploy-play.ps1`, retired 2026-09-26) | the game-profile precondition runs inline before the injector build | stays inline, and is the deploy's ONLY runner call. Its position is its meaning: it validates the install after the loader host is known and immediately before the injector build consumes it — `-Only game-profile -Tier local -LocalArgs …` |
| `gk-core/scripts/verify-change.py` | `$registry.guards.($check.id)` from `verification-boundaries.v1.json` | resolves through the enforcement registry's catalog, and is where a change's guards actually gate |
| `gk-core/scripts/verification-boundaries.v1.json` | carries a `guards` map | **the `guards` section is removed.** `boundaries[].guards` keeps listing guard *ids*, now resolved against the catalog |
| `gk-core/scripts/guard-verification-boundaries.py` | requires the `guards` section | requires it **absent**, and requires every `boundaries[].guards` id to exist in the enforcement registry |

`EnforcementRegistryGuardTests` R5 switches to its post-runner form: CI invokes `run-guards.ps1 -Tier
ci`, and no `scripts/guard-*.ps1` path appears anywhere else in `ci.yml` (catching a guard wired by
hand *beside* the runner), **except** a guard whose registry row carries
`"ciEntry": "own-step"` plus a non-empty `ciEntryReason`. Exactly one row qualifies today:
`verification-boundaries`, whose reason is the existing `ci.yml` comment (*"Guard scripts use `exit`,
so putting it after another guard in a shared pwsh block could make it unreachable; this script's exit
code directly gates the step"*). The runner **skips** `own-step` rows under `-Tier ci`, so the guard
never runs twice. R7 is deleted, since the duplicate map it policed no longer exists.

## Commands

```powershell
.\scripts\run-guards.ps1 -Tier ci
.\scripts\run-guards.ps1 -Tier local -IncludeBacklog
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~GuardRunner|FullyQualifiedName~EnforcementRegistry|FullyQualifiedName~CiWiring"
.\scripts\verify-change.ps1 -Paths <changed> -Session <id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/run_guards.py` | **new** |
| `gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs` | **new** |
| `.github/workflows/ci.yml` | Boundary guards step → one runner call |
| `gk-fusion/scripts/deploy-play.py` | hand list → the positioned `-Only game-profile` precondition (2026-09-26: the tier batch was removed from the deploy; it gated nothing a deploy could break and cost 203s per deploy) |
| `gk-core/scripts/verify-change.py` | guard lookup → catalog |
| `gk-core/scripts/verification-boundaries.v1.json` | `guards` section removed |
| `gk-core/scripts/guard-verification-boundaries.py` | schema updated |
| `gk-core/scripts/enforcement-registry.v1.json` | optional per-row `args` |
| `gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs` | R5 post-runner form, R7 deleted |
| `gk-core/tests/FusionRpg.Guard.Tests/TestSupport/GuardWiring.cs` | 2026-09-26: `AssertDeployPlayRunsItLocally` → `AssertGuardReachableInItsOwningPhase` (CI for `ci`-tier guards; `verification-boundaries.v1.json` for the `local`-tier ones CI can never run; the one positioned deploy precondition), plus `AssertDeployRunsNoGuardSuite` |
| existing Guard.Tests that grepped the deploy for a guard name | re-pointed to `AssertGuardReachableInItsOwningPhase` |

## Code style

```powershell
foreach ($id in $selected) {
    $row = $catalog.$id
    $sw  = [Diagnostics.Stopwatch]::StartNew()
    & pwsh -NoProfile -File (Join-Path $Root $row.script) @(Resolve-Args $id $row)
    $results += [pscustomobject]@{ id = $id; tier = $row.tier; status = $row.status; exit = $LASTEXITCODE; s = [math]::Round($sw.Elapsed.TotalSeconds, 1) }
}
$results | Format-Table -AutoSize | Out-String | Write-Host
$gatingRed = @($results | Where-Object { $_.status -eq 'gating' -and $_.exit -ne 0 })
if ($gatingRed.Count -gt 0) { throw "guards failed: $($gatingRed.id -join ', ')" }
```

## Testing strategy

`GuardRunnerTests` drives the runner against a **temporary registry and fake guard scripts** in a temp
directory, with a checked delete (test-substrate rule: this *is* the disk under test):

- A red gating guard fails the run, **and** a second guard after it still ran (no masking).
- A red backlog guard does not fail the run, and is reported under `BACKLOG`.
- An unknown `-Only` id throws.
- A guard that calls `exit 3` after printing does not stop the next guard from running.
- `{ciRange}` substitution yields `HEAD~1..HEAD` when a parent exists and no arg on a root commit.

The real-tree check is simply `run-guards.ps1 -Tier ci` exiting 0 in CI.

## Boundaries

- **Always:** run every selected guard before failing. Take arguments from the registry.
- **Ask first:** letting a caller pass arguments for anything except machine-local paths.
- **Never:** hand-add a `guard-*.ps1` call to `ci.yml`, `gk-fusion/scripts/deploy-play.py` or
  `verify-change.py`. Never let the runner decide status: the registry decides.
- **Never (2026-09-26):** give the deploy a guard TIER BATCH. A deploy runs exactly one guard, by
  id, when running it is a deploy precondition. Verification is the implement phase's and CI's.

## Success criteria

- [x] `ci.yml`, `gk-fusion/scripts/deploy-play.py` and `verify-change.py` contain no hand-listed guard scripts,
      except the integrity step and the positioned `game-profile` call, each commented with why.
- [x] `verification-boundaries.v1.json` has no `guards` section, and its integrity guard enforces that.
- [x] One CI run is green with the runner's summary table visible in the log.
- [x] `GuardRunnerTests` green, including the no-masking falsifier.
- [x] **2026-09-26:** the deploy runs no guard suite — one positioned `-Only game-profile`
      precondition only — and `GuardWiring.AssertDeployRunsNoGuardSuite` pins that in CI
      (whole `FusionRpg.Guard.Tests` 694/694 green after the re-point).

## Self-audit — the debate

**Objection: "A child process per guard is slower."** About 0.3–0.5 s of pwsh startup per guard,
roughly 5–8 s across 19 guards, against a CI job that already runs a ~9-minute test profile. The
alternative, running in-process, is the documented `exit` hazard. Correctness wins, and the runner's
per-guard timing column keeps the cost visible.

**Objection: "Removing `verification-boundaries.v1.json`'s `guards` section breaks anyone reading it."**
The only readers are `verify-change.py` and `guard-verification-boundaries.py`, and both change in
this module. The integrity guard then *requires* the section's absence, so it cannot come back
quietly as a second map.

**Objection: "deploy-play's G3 tolerance block encodes a real decision (class-system decision 12). The
runner drops it."** It doesn't drop the decision. It moves it to where decisions live: the
`class-system` registry row is `status: backlog → retire-atk`, so the runner neither fails the deploy
on it nor hides it (it prints under `BACKLOG`). The bespoke text-matching block was a second copy of
policy in a script. When `retire-atk` lands, the row flips to `gating` and the guard gates like any
other.

**Objection: "Why keep game-profile inline?"** Because its position is part of its meaning: it
validates the game directory immediately before the injector build that consumes it. Moving it into
the pre-build batch would check a directory before the host is chosen. It still resolves *through*
the runner (`-Only`), so there's one catalog and no second invocation convention.

## Gaps found and closed while writing

- **`guard-generated-seed`'s CI range logic lives inline in `ci.yml`.** A runner with no argument
  channel would have silently run it without `-Range`, which falls back to working-tree mode, and that
  is always clean on CI. That would be a guard that can never fail. Closed with registry `args` and
  the `{ciRange}` placeholder.
- **Existing Guard.Tests pin the old wiring by grepping `deploy-play.py` for guard names.** Left
  alone, they would go red the moment the lists are deleted, or push someone into keeping a dead call
  "for the test". Named in project structure as tests to re-point in this module, not later.
- **`-Only` must still honour the registry's `status`.** Otherwise `verify-change` could fail an edit
  on a backlog guard's pre-existing findings, the exact "a module can't go green on failures it didn't
  cause" defect `solid-remediation`'s green-baseline was written against. Rule: a backlog guard named
  by `-Only` runs and reports, and never fails the verification.
