# `CAI-spec-status-4` — two combat-ai specs' status lines described a module that had shipped

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Same class as `CAI-status-3`: a Project-structure marker
or a status line that says a file "does not exist yet" when it exists, or names a revision that has been
superseded. It is not cosmetic — a lane plans from these tables, and `spec-commander-direct-orders.md`
would have sent a reader to a route that 404s.

## What was wrong, measured

| Spec | Claim | Measured |
|---|---|---|
| `spec-lawn-cast-trigger.md:6` | status "part built"; the Injector frame slot, its registry drops, `PerfSection.LawnAiDecide` and the lawn tuning keys all **owed**; `lawn-perf-budget.v1.json` "still does not exist"; `combat-ai.v1.json` "carries no lawn section" | All four landed (`CAI-perf-1`, `CAI4.8`, `CAI4.7`+`CAI-F1`); `CombatAiTuningFiles.Current` is `combat-ai.v2.json`; `LawnPerfBudgetFiles.Current` is `lawn-perf-budget.v2.json` |
| `spec-lawn-cast-trigger.md:66,67` | `LawnCombatAiFeature.cs` / `LawnDecisionHost.cs` "**new; does not exist yet**" | Both exist (CAI4.8), and this lane wired the latter's `board.start` edge |
| `spec-lawn-cast-trigger.md:65` | `PerfProbe.cs`: "`LawnAiDecide = 25`, `SectionCount` 25 → 26" | `AiDecide = 25`, `LawnAiDecide = 26`, `SectionCount = 27` (CAI-perf-1) |
| `spec-commander-direct-orders.md:73,91,379,628` | the endpoint is `POST /api/lawn/order/direct` | shipped route is `POST /api/lawn/order` (`LawnOrderEndpoints.cs:38`) |
| `spec-commander-direct-orders.md:74,394` | the verb is `lawn.order.direct` | shipped command name is `lawn.order` (`LawnOrderEndpoints.cs:26`, `LawnOrderHost.cs:40`, pinned on both sides by their tests) |
| `spec-commander-direct-orders.md:80` | `tests/FusionRpg.Server.Tests/Lawn/LawnOrderEndpointTests.cs` "**new; does not exist yet**" | the file is `gk-core/tests/FusionRpg.Server.Tests/LawnOrderEndpointTests.cs` — there is no `Lawn/` directory |
| `spec-commander-direct-orders.md:75` | `LawnOrderHost` "mark[s] the actor due" | its own class doc says the opposite: marking due is module 19's frame slot |
| both specs | `gk-core/data/tuning/combat-ai.v1.json`, and the H7 blocker "until `CAI-F1` lands" | `CAI-F1` landed; the revision is v2 |

The `.direct` name is a spec↔code divergence, and it is resolved **toward the code** because the code is
pinned on both sides of the wire by tests (`LawnOrderEndpointTests`, `LawnOrderHostTests`) while the spec
was pinned by nothing. The correction is dated and in place rather than silent, so a reader who remembers
the drafted name finds out what happened. No `web/**` file references either name yet (measured:
`grep -rn "lawn/order\|lawn.order" gk-web/web/fusion-rpg-web/src/` returns nothing), so nothing was 404ing — the
FE half is still owed and outside this lane's fence.

## Verified

| Criterion | Command | Result |
|---|---|---|
| The combat-ai scope is citation-clean | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **D1 0, D2 0, D3 0, D4 0** (was D3 4) |
| The repo-wide strict guard is unmoved | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | 1688 documents / 25719 citations — **all 0 HIGH**, exit 0 |
| No stale marker or `.direct` route survives in either spec | `grep -n "new; does not exist yet\|does not exist\|order/direct" docs/architecture/combat-ai/spec-{lawn-cast-trigger,commander-direct-orders}.md` | only the design-gate checklist notes that QUOTE the marker string |
| The tuning revision names are read through their own constants | `cat gk-core/src/FusionRpg.Core/Diagnostics/LawnPerfBudgetFiles.cs`, `.../CombatAiTuningFiles.cs` | `lawn-perf-budget.v2.json`, `combat-ai.v2.json` |

## NOT proved

- **No code changed**, so no build, test or guard beyond the two citation audits was run.
- **The two `web/**` rows in `spec-commander-direct-orders.md` are still marked owed** and were left
  alone: that half is outside every combat-ai lane's fence, and the markers are still true.
- **The tuning revision `spec-commander-direct-orders.md` says is owed is still owed** — the two
  `lawn.order.*` keys are not in `combat-ai.v2.json`. The spec now says the blocker is closed rather than
  that the keys have shipped, which is the true state (`CAI4.9`'s item 4).

## Second sweep — the remaining false markers, found by a script rather than by eye

A script over `docs/architecture/combat-ai/*.md` extracts every backticked path on a line containing
"does not exist" and tests it against the filesystem. It found six false markers; three were intentional
and three were not.

| Spec | Claim | Measured |
|---|---|---|
| `spec-lawn-actor-view.md:5` | "**no production host yet**" and `LawnActorViewHost.cs` "does not exist yet" | the host is in (CAI4.1) with seven seams and 10 tests, and `InjectorLoop` → `LawnDecisionHost.Tick` → `ViewFor` calls it |
| `spec-lawn-actor-view.md:72` | the same file "new; does not exist yet" | exists |
| `spec-stance-wiring.md:5` | "part built"; Outcomes 2/3 "await narrowing `AiTuning`, which breaks two out-of-fence test bootstraps" | landed 2026-09-23: `siege.v3.json` from one `--remove-key ×2`, `AiTuning` narrowed to two, the four constructions fixed in the same commit |
| `spec-stance-wiring.md:156` | `gk-core/data/tuning/siege.v3.json` "new; does not exist yet" | exists |
| `spec-profile-schema.md:84` | `gk-core/tools/tuning/test_publish_remove_key.py` "new; does not exist yet" | exists (`113e52033`, SSH5.7) |
| `spec-profile-schema.md:5,40` | published as `combat-ai.v1.json`, hosts cited at `Server/Program.cs:237` / `RpgHost.cs:89`; `siege.v2.json` "does not exist yet" | current revision is v2 read through `CombatAiTuningFiles.Current`; `siege.v3.json` is the shipped siege file; both cited lines had moved |
| `spec-lawn-cost-authority.md:5,71` | "the lawn half … blocked on injector paths"; its test file "does not exist yet" | the Core half landed (`Actions/LawnCostRows.cs`, 5 tests); only the injector caller is still owed — the spec's Project-structure table now carries the Core file it never listed |
| `spec-replay-identity.md:5,60` | "the Data **and Server** thirds are filed"; `CombatAiProfileFiles.cs` "does not exist yet" | the Server source half landed (`CAI2.2`, 8 tests) and has no production caller; the Data third is the whole remainder |

**The three left alone, and why.** `spec-delve-automated-wiring.md:323` is a **quotation** of
`IBattleView.cs`'s own doc text, not a marker about that file — `CAI-status-3` already ruled it stays
exactly as it is, and a pattern match that "fixed" it would make the spec misquote the file it cites.
`spec-lawn-cast-trigger.md:456,468` are inside Open question 1 — the question as it was asked, and the
answer whose last two sentences the dated correction immediately below them supersedes.

| Criterion | Command | Result |
|---|---|---|
| No false marker survives, measured rather than eyeballed | `python - <<'PY' …` (the sweep above) | **3 remaining, all three named and intentional** |
| The combat-ai scope is citation-clean | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | D1 0, D2 0, D3 0, D4 0 |
| The repo-wide strict guard is unmoved | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** |

**NOT proved:** no code changed, so no build, test or guard beyond the two citation audits was run. The
sweep tests PATH EXISTENCE only — a marker about a file that exists but is empty, or about the wrong
revision of a file that exists, is invisible to it and was caught by reading.

## Third sweep — the two status lines that named landed work as remaining

| Spec | Claim | Measured |
|---|---|---|
| `spec-decision-inspector.md:78` | "no `debug.*` route reads `Recent()`/`LastFor()`" | `DebugCombatActions.cs:377,418` reads `Recent()` for `debug.combat.snapshot`'s `aiDecisionCount` / `aiDecisions` (landed 2026-09-23, `CAI2.5`) |
| `spec-action-schedule-twin.md:8-9` | "The parity test against the live core policy … and the `gk-forge/tools/DominanceBaseline` run remain" | the parity test landed (`ActionScheduleMatchesCorePolicyTests`, 3/0) and the dominance run is DONE (reproduces the checked-in baseline); only the projection remains, and it is an erratum |

Both corrected, with the remaining work stated precisely (the feed, not the route; the erratum, not the
work). The `:70` citation in `spec-decision-inspector.md`'s own status line was checked and still
resolves to the full-status paragraph.

**One self-inflicted D1, caught and fixed:** the first version of `spec-lawn-cost-authority.md`'s new
status line named `LawnCostRowSource.cs`, which does not exist, so the scope's D1 went 0 → 1. The
Project-structure table already carries that file with its own exemption; the status line now points at
the table instead. Scope re-run: D1 0, D2 0, D3 0, D4 0.
