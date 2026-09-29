# Spec: `wire-green-guards`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 1** · depends on:
`guard-runner`.

## Objective

Five guards pass today and CI has never run them: `debug-scope`, `magic-numbers`, `overflow`, `power`
and `stat-pairs`. Each one enforces a `CLAUDE.md` hard rule (debug-API scope, balance surface as data,
numeric range, one power ladder, contest pairing). On any branch that skips `deploy-play.py`, which
means every PR merge, those rules are unenforced. This is the cheapest enforcement in the repo: **a
wiring gap, not a capability gap.** After `guard-runner` lands, closing it is five registry edits.

This module also settles the two guards that **cannot** run in CI (`game-profile`,
`injector-compile`), so that "not in CI" stops being ambiguous and becomes one of two stated states.

## Design

### Measured baseline (2026-09-18; the build re-runs every guard first)

| Guard | Exit | Non-gating output | Rule it enforces |
|---|---|---|---|
| `debug-scope` | 0 | 102 routes, 0 banner mismatches | Debug API may trigger, never fabricate |
| `magic-numbers` | 0 | 28 M3 findings, 0 M1/M2 | The balance surface is data |
| `overflow` | 0 | 46 A3 findings, 0 critical | Numeric range |
| `power` | 0 | — | One power ladder, no private `f(level)` |
| `stat-pairs` | 0 | — | Every Contest paired and symmetric |

**M3 and A3 do not gate today, and this module only wires what does.** Each guard fails the build on
its severe codes (`audit-magic-numbers.py`: M1/M2; `audit-overflow.py`: A2/A4 and critical casts) and
prints the rest. Flipping a guard to `gating` in CI keeps that split. Both named tools were once
fronted by thin `.ps1` wrappers, retired 2026-09-26; the runner now dispatches the `.py` directly.

> ⚠️ **Corrected 2026-09-18.** An earlier draft of this spec called M3/A3 "informational, non-gating
> by each audit's own severity model". For A3 that is wrong. `audit-overflow.py` labels A3
> **`[HIGH]`** (*"int on a magnitude - overflows at Theta 103,557"*). The guard does not block it
> for a different reason: its header says the sites were *"triaged, currently-BOUNDED"*
> (`docs/architecture/power/overflow-triage.md`, 2026-08-23: 75 findings = 56 LADDER to widen +
> 19 BOUNDED with a proven cap). Today's count is **46**, a mix nobody has re-triaged since. Under
> ruling 2 (no permanent report-only), both M3 and A3 get their own backlog tasks (SE3.14, SE3.15).

### The registry edits

| Row | Before | After |
|---|---|---|
| `debug-scope`, `magic-numbers`, `overflow`, `power`, `stat-pairs` | `ci` / `backlog` → `wire-green-guards` | `ci` / `gating` |
| `game-profile` | `local` / `gating` + reason (seeded) | unchanged, and the reason is confirmed |
| `injector-compile` | `local` / `gating` + reason (seeded) | unchanged, and the reason cites `CiWiringGuardTests.ExemptFromCiWiring`'s identical exemption for `Injector.Tests` |
| `verification-boundaries`, `session-boundary` | seeded from measurement | `ci` / `gating` if `ci.yml` runs them, otherwise wired here |

### What "local" means, precisely

`tier: local` has **one** legal reason: the guard needs the game install. The CLAUDE.md hard boundary
(*"Never download or patch the PVZ Fusion game binary"*) keeps game binaries off a CI runner, so these
guards can only run where the game is. `enforcement-registry`'s R4 already refuses an empty reason.
This module adds a check that the reason mentions the game install, so "local" cannot quietly turn
into "too slow for CI".

## Commands

```powershell
.\scripts\run-guards.ps1 -Tier ci           # must exit 0 with the five newly gating
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistry"
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/enforcement-registry.v1.json` | five rows flip; local reasons confirmed |
| `gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs` | R4 extension: a `local` reason names the game install |

## Testing strategy

- **Before flipping,** run each of the five on a clean checkout of the branch tip and record its exit
  code in the commit body. A guard that is green on this machine and red on CI (a path, encoding or
  locale difference) must be caught here, not on the first PR.
- **After flipping,** one CI run must show all five in the runner's summary table with exit 0.
- **One falsifier per guard,** proving the gate is live. On a scratch branch, introduce a single
  violation the guard's own docs name (a bare magic literal in a `*Policy.cs`, an unchecked
  `int*int` magnitude, and so on), confirm `run-guards -Tier ci` fails, then discard the branch. It is
  recorded in the commit body, never committed.

## Boundaries

- **Always:** re-measure before flipping. The table above is a reading.
- **Ask first:** promoting a guard's informational codes (M3, A3) to gating.
- **Never:** mark a guard `local` for speed or flakiness.

## Success criteria

- [ ] Five rows `ci` / `gating`, and CI green with them running.
- [ ] Every `local` row's reason names the game install, and the test enforces it.
- [ ] Five falsifier runs recorded in the commit body.

## Self-audit — the debate

**Objection: "CI on the Windows runner might not have Python, or the modules these audits import."**
`magic-numbers` and `overflow` are Python. `ci.yml` already sets up Python for seedsmith tests
(verify at build time). If the runner lacks Python on the guard step, the fix is a `setup-python`
step before the runner, not demoting the guards.

**Objection: "28 M3 and 46 A3 findings are a backlog. Ruling 2 says clear before gating."** It does,
and this spec's first answer ("not this guard's backlog") dodged that. The *wiring* here is
independent: the gating codes are green and can gate today. The two non-gating codes are a
permanent report-only state, which ruling 2 rules out. So they are cleared and promoted in their
own tasks (SE3.14 for M3, SE3.15 for A3), rather than blocking this cheap wiring win.

**Objection: "`power` and `stat-pairs` are green now. What stops them rotting?"** Gating does. That is
the whole point of this module.

## Gaps found and closed while writing

- **"Green on this machine" is not "green on CI".** Added the clean-checkout re-run before flipping.
- **"local" was undefined** and could have become a dumping ground. Now it has exactly one legal
  reason, checked by a test.
- **The two runs-through-`verify-change` guards** (`verification-boundaries`, `session-boundary`) were
  guessed in an early draft. Now they are measured at build time and seeded from that measurement.
