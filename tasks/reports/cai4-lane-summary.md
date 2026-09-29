# Lane `cai4` — what this lane took, what it landed, and what remains

Session `combat-ai-4`, branch `cmdc/cai4`, base `3877bf3a545a`, 2026-09-22.
Fence: `gk-core/src/FusionRpg.Core/Match/**`, `data/tuning/combat-ai*.json`,
`gk-core/data/tuning/lawn-perf-budget.v1.json`, `docs/architecture/combat-ai/**`, `docs/research/combat-ai/**`,
`gk-core/tests/FusionRpg.Core.Balance.Tests/**`, `tests/FusionRpg.Core.Combat*Tests.Tests/**`,
`tasks/combat-ai-todo.md`, `tasks/combat-ai-ledger.jsonl`, `tasks/reports/**`.

## Rows taken, in dependency order

| Row | State after this lane | Evidence |
|---|---|---|
| **CAI-cite-2** — `docs/research/combat-ai/**` dead citations | **CLOSED** — 14 LOW findings cleared (D1 8→0, D2 5→0, D3 1→0) | `tasks/reports/CAI-cite-2.md` |
| **CAI-cite-3** (filed and closed in this session) — the citation sweeps `CAI-cite-1` left | **CLOSED** — both combat-ai doc scopes now `D1 0, D2 0, D3 0, D4 0`; 7 re-anchors, 3 not-yet-existing notes, 9 pre-fix notes | `tasks/reports/CAI-cite-3.md` |
| **CAI4.2** — `lawn-held-actions` A: the per-match frozen sets | **Core half landed** — all five acceptance lines run and green; the production caller is CAI4.3's | `tasks/reports/CAI4.2.md` |
| **CAI4.6** — `lawn-cast-activation`: the ordered cast plan | **Pure half landed** — acceptance rows 1 and 2 run and green | `tasks/reports/CAI4.6.md` |
| **CAI4.7** — `lawn-cast-trigger` A: trigger, budget, token pool | **Core half landed** — every pure acceptance line run, three planted violations kill their tests | `tasks/reports/CAI4.7.md` |
| **CAI4.9** — `commander-direct-orders`: the queue + refusal classifier | **Core half landed** — spec rows 1, 2, 6–13, 15 run and green; four planted violations kill their tests | `tasks/reports/CAI4.9.md` |

**Every row that stayed open is open because a named path outside this fence is owed — never because
work in-fence was skipped.** `tasks/combat-ai-ledger.jsonl` records each as `blocked` with the cause.

## Rows NOT taken, with the exact path that blocks each

| Row | What is owed, and by whom |
|---|---|
| `CAI2.2` replay-identity B | `Server/CombatAiProfileFiles.cs`, `Server/WebMatchService.cs`, `Server/DelveBattleSessionManager.cs`, `gk-core/tests/FusionRpg.Server.Tests/**` — and it sits behind CAI2.1's denied Data third (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs` + the nullable column). |
| `CAI2.3` action-schedule-twin | Its in-fence half is **already landed and green** (`gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs`, 3/3). Remaining: the profile→`Predictor.ActionEconomy.Options` **projection** (owner erratum — the row claims it, `spec-action-schedule-twin.md:421-423` assigns it to module 2/14) and `dotnet run --project gk-forge/tools/DominanceBaseline` (`gk-forge/tools/DominanceBaseline/**`, and `tools/**` at large, are outside this fence). |
| `CAI2.5` decision-inspector B | The Core ring landed earlier (`Actions/Ai/AiDecisionRing.cs`). Remaining: `Injector/Effects/{AiInspectFeature,LawnAiDecisionObservability}.cs` + the additive `InjectorEntityRegistry` cleanup. |
| `CAI2.6` the reserve-floor rule | **An owner ruling, not a path.** Its in-fence witness already exists and is green. The two seam-side cases its acceptance names are `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/ActionStageTests.cs` (outside this fence). |
| `CAI3.1` stance-wiring (H7) | Narrowing `AiTuning` breaks `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs:530` and `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:470` (both outside this fence), and `gk-core/data/tuning/siege.v3.json` is **not** in this fence and cannot land without its reader (`Server/Program.cs:231`). |
| `CAI4.1` lawn-actor-view | The three Core files landed earlier (`Actions/Ai/Lawn/**`, outside this fence). Remaining: `Injector/Effects/LawnActorViewHost.cs`. |
| `CAI4.3` lawn-held-actions B | `Injector/Effects/LawnHeldActionRegistry.cs`, `Server/RpgHub.cs`, `Injector/CheatCommandRunner.cs`, `Injector/Effects/InjectorEntityRegistry.cs`. **This is CAI4.2's wire.** |
| `CAI4.5` lawn-cost-authority B | `Injector/Effects/LawnBasicAttackCostCharger.cs` + the new `Injector/Effects/LawnCostRowSource.cs`. |
| `CAI4.8` lawn-cast-trigger B | `Injector/Effects/{LawnCombatAiFeature,LawnDecisionHost}.cs`, `Injector/Host/InjectorLoop.cs`, `Injector/Effects/EffectRuntime.cs`, `Injector/Effects/InjectorEntityRegistry.cs`. **This is CAI4.6's and CAI4.7's wire.** |
| `CAI5.1` / `CAI5.2` | An **owner-only live probe** (300-zombie A/B) plus the lawn plan's `lawn-combat-baseline` (`LW2.4`, open). Their two documents are inside this fence; the measurement is not something a lane can fabricate. |
| `CAI5.3` flip default-on | `Injector/Effects/LawnCombatAiFeature.cs` + two measured-unmet preconditions (`LW1.4`–`LW1.6`, `LW5.1`). |
| `CAI-perf-1` | Remedy (a) needs `gk-core/src/FusionRpg.Core/Diagnostics/**` (outside this fence); remedy (b) is an erratum for the manager. Measured today: `PerfProbe.cs` still ends at `LawnMoveDrain = 24`, `SectionCount = 25`. |
| the Deferred **content-level** citation sweep in `docs/research/combat-ai/**` | **Inside this fence and still owed**, measured: 9 sites citing `BasicAttack.cs:163-165,152,189-191,193-216,489` and `TimelineDispatch.cs:79-80` at pre-CAI1.10/1.11 line numbers. The remedy is a **pre-fix note, not a re-anchor** — those lines describe the defect the program has since closed. Deliberately not swept here so a documentation change does not ride a code commit. |

## NOT proved (do not read these as done)

- **No production host reaches any of the four Core halves.** CAI4.2's, CAI4.6's, CAI4.7's and CAI4.9's
  hosts are CAI4.3/CAI4.8's injector files. Each row's own acceptance lines are run; the *modules* are not
  reachable.
- **The `FusionRpg.Injector` build is unverified here** — this lane has no game dir / interop refs. The
  ledger already carries a recorded failing gate at an earlier head (`dotnet build FusionRpg.slnx -c
  Release -> 888 errors, ALL in FusionRpg.Injector*`), so every injector-half row above may be blocked by
  more than its fence.
- **No tuning file was published, and none can be from this fence (H7).** Four rows' tuning halves are
  owed: CAI4.7's `combat-ai.v3.json` lawn section, CAI4.9's two order keys, CAI3.5's `combat-ai.v2.json`,
  CAI3.1's `siege.v3.json`. Both readers name their file by hand and both are outside this fence
  (`gk-core/src/FusionRpg.Server/Program.cs:248`, `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:89`). Measured today:
  `gk-core/data/tuning/` holds `combat-ai.v1.json` only, and its top-level keys are
  `schemaVersion, version, _meta, profiles, router` — **no `lawn` section**.
- `gk-core/data/tuning/lawn-perf-budget.v1.json` **still does not exist**, so CAI4.7's `lawn.ai.decide` share has
  no file to read; its owner is the lawn plan's `LW1.1`.
- `gk-forge/tools/DominanceBaseline` was **not run** (outside this fence), so CAI2.3's dominance clause stays
  unproved.
- No live probe, no A/B, no fps/frame-time reading of any kind was taken.

## Second segment: merged onto `features/mega-merge`, then the last two in-fence slices

`features/mega-merge` was picked up as instructed (88 commits; this lane's 10 commits had already merged
at `6b7dfc0b9`; tip `3e06b1fd7`; the merge fast-forwarded cleanly).

**The merge unblocked none of this program's rows.** Measured at the merged head: no
`EffectEventDto.CastOrigin`, no `SubjectId`/`ScopeId` on `DirectOrder`, `PerfProbe.cs` still ending at
`LawnMoveDrain = 24` with `SectionCount = 25`, no forced-intent hook in `IntentRouter`, `AiTuning` still
four members. **No tuning revision was published** — CAI-F1 is unrouted by design, as instructed.

All four landed Core halves were re-verified at that head: `verify-change` exit 0, **39 distinct test
projects, 0 with any failure** (summed per-project counts 15698 passed / 0 failed). No file this lane owns
and no dependency its halves read was touched by the 88-commit merge.

Two in-fence slices remained once the tree was merged, and both are now landed:

| Increment | What it closed |
|---|---|
| `CAI4.2` + its spec **Success criterion 5** | *"an unknown species yields empty, and `StubIntentSource` answers `None` for it"* — proven through the SHIPPED stub with a board fake whose every member throws, so the test proves where it stopped. Planted removal of the stub's early return kills it. 13 tests (was 11). |
| `CAI4.9` + spec rows **3, 4, 5** | `CheckScope`/`CheckSubject` with the `OrderSubject` record: the identity refusals take the durable identity as ARGUMENTS, so the rules are complete and mutation-killed here while the two owed `DirectOrder` fields remain only their supply. 20 tests (was 16). |

A third in-fence slice was searched for and does **not** exist: every other blocked row's remaining work
is a path outside this fence, an owner decision, or an owner-only probe.

## Third segment: merged again, then three more rows

`features/mega-merge` picked up a second time — a real merge this time (this lane had 3 commits it did not,
`features/mega-merge` had 5), clean, landing as `8b81e395d`.

**The merge unblocked nothing again**, re-measured rather than assumed: no `EffectDto.CastOrigin`, no
`SubjectId`/`ScopeId` on `DirectOrder`, `PerfProbe.cs` still ending at `LawnMoveDrain = 24` /
`SectionCount = 25`, no forced-intent hook in `IntentRouter`, `AiTuning` still four members. **No tuning
revision was published** — `CAI-F1` is unrouted by design.

What the merge *did* change is where this lane's tests belong: the test-split created
**`gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/`** and re-pointed `spec-lawn-actor-view.md`'s citations into
it — the canonical home for `Match/**` tests, and it has its **own focused verification boundary**
(`core-match`, one project) while `gk-core/src/FusionRpg.Core/Match/**` still pays `core-fallback`'s whole
39-project, ~15.7k-test, ~4-minute group per edit. That is filed as **`CAI-tests-1`**, blocked on this
lane's fence.

| Row | State | What it is |
|---|---|---|
| `CAI-loop-1` | **CLOSED** | The four wave-4 Core halves run **together** for the first time: the real `CoreIntentPolicy` at `AiPlace.Lawn` over module 16's store; the edge → budget → token → `LawnCastPlan` chain paying each action's **own compiled cost** through the real `EffectiveRungResolver`; and the admission rules feeding the queue the **real `IntentRouter`** reads. 4 tests, four planted violations each killing their named test — one of which was **inert until a test was strengthened**, which is the finding that fix recorded. |
| `CAI-status-2` | **CLOSED** | The four wave-4 specs still read *"Status: … Not built."* after their Core halves shipped, and still marked landed files *"new; does not exist yet"*. Each status line now names what landed, what is owed and who owes it, and where the tests actually live; `combat-ai.v1.json`'s three stale "does not exist yet" claims are corrected (CAI1.8 published it; no lawn section). |
| `CAI-tests-1` | **filed, blocked on the fence** | Move the seven `CombatAi/*.cs` test files to `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/`, the path their rows name and the split created. |

Also verified this segment, and both came back clean: TVB5.8.33's own re-point of
`spec-lawn-actor-view.md`'s citations into `Match.Tests` matches `CAI-tests-1`'s target, and the
`lawn-playable` spec that `spec-lawn-actor-view.md:244` quotes still reads *"Status: spec, 2026-09-16. Not
built."*, so that quotation remains honest. One suspected defect — the map's module-16 dependency row —
was checked and **already carries its correction** (`— *(corrected: it reads no profile)*`).

## Fourth segment: the same merge again, then three more rows

`features/mega-merge` picked up a third time — a clean **fast-forward** to `8e1ece9cc`, the manager's merge
of this lane's own 7 commits. So no other lane's work arrived, and **nothing was unblocked**: re-measured,
there is still no `EffectEventDto.CastOrigin`, no `SubjectId`/`ScopeId` on `DirectOrder`, `PerfProbe.cs`
still ends at `LawnMoveDrain = 24`, `IntentRouter` has no forced-intent hook and `AiTuning` still has four
members. **No tuning revision published** — `CAI-F1` is unrouted by design.

| Row | State | What it is |
|---|---|---|
| `CAI-cast-1` | **CLOSED** | `LawnCastPlan` charges `intent.ActionId` and arms `intent.Envelope`, so a mismatched pair is a **silent mis-charge**. The guard was added only after reading **every** `ActionIntent` construction in `src/` and proving none breaks — and it protects exactly the lookup-by-id pattern the owed order path will use. |
| `CAI-loop-2` | **CLOSED** | The loop through the **real `LawnBattleView`** instead of a fake: the oracle-vs-raw-side discriminator (a raw zombie the oracle calls an ally must never be targeted) now proven through the real profiled policy, plus the derived memo measured as demand-vs-supply. Includes CAI4.1's **own named mutation**, which now kills a test when driven through the policy. |
| `CAI-open-1` | **CLOSED** | **Eleven** Open questions across six specs now carry a dated answer with its evidence — the same propagation family as `CAI-status-2` and the citation sweeps — and the five that are genuinely unresolved are explicitly left open with the blocking task named. |
| `CAI-status-3` | **CLOSED** | **52 Project-structure markers across 15 specs** said `new; does not exist yet` about files that exist. Three sites needed judgement rather than a flip — one row is about owed *fields* on an existing file, one marker's reason was already satisfied, and one is a **quotation** of a code file's own doc text, which a pattern match would have rewritten into a misquote. |

Two corrections this segment were **mine, not the product's**, and are recorded rather than hidden:
`SideOf` returns the *relative* side (an oracle-ally reads 0), and a memo measurement that counted
*distinct* resolved actors let a **disabled memo pass** until it counted resolve *calls*.

## Fifth segment: a 22-commit merge, then four rows

`features/mega-merge` picked up a fourth time — a clean fast-forward that brought **22 commits from other
lanes**. **Nothing was unblocked**, re-measured: still no `EffectEventDto.CastOrigin`, no
`SubjectId`/`ScopeId` on `DirectOrder`, `PerfProbe.cs` still ending at `LawnMoveDrain = 24`, no `AiTuning`
narrowing. **No tuning revision published** — `CAI-F1` is unrouted by design.

| Row | State | What it is |
|---|---|---|
| `CAI-guard-3` | **CLOSED** | The lawn AI's Core contract, **enforced rather than asserted in prose**: five bans (no wall clock, no ambient RNG, no file I/O, no Unity, no await/thread) over **every `.cs` under `gk-core/src/FusionRpg.Core/Match/Ai/`, enumerated from the directory** — so a file added tomorrow is covered with no edit and there is no allowlist to widen. Comment-stripping is load-bearing: two files contain the banned word in a comment that *promises* the ban. Two mutations, each killing its named test. |
| `CAI-handoff-1` | **filed, blocked on the fence** | The document three places call the picking-up entry point still says **"Build: Not started. Nothing exists."** and "Your first task is CAI1.1" — all four claims measured false (40 ledger rows done). |
| `CAI-route-2` | **CLOSED** | The routing index said a `gk-core/src/FusionRpg.Core/Match/**` fence **clears 4** rows; that fence is this lane and it is **spent**. Now dated, with per-row test counts, the remaining paths and the two fence asks. |
| `CAI-defer-1` | **CLOSED** | Four Deferred entries carry **conditions** rather than dates; each was measured. Two are **met or already done** (the `ContentHashStamp` rename, filed in `effect-atom`; the router carrying the decision sink), one is not (6 members, not 8). |

The pattern across this segment is one class: **a claim that was true when written and a reader who has no
way to know it stopped being true** — a status line, a marker, an index, a conditional. Each row's fix
names its evidence and its date, and each deliberately leaves the genuinely-open ones saying so.

## The blocked rows, re-read on instruction

All 19 stay blocked. 7 have a ledger dependency that is now `done` and an eighth (`CAI4.3`) has its
dependency's Core half landed this session, but **none has an in-fence path left**, so no row could be
reopened (reopening means implementing). `gk-fusion/src/FusionRpg.Injector/**` is claimed by **no active session**,
so one cheap fence widening clears 8 of them; `gk-core/src/FusionRpg.Server/**` and `gk-core/src/FusionRpg.Data/**` ARE
held; four rows need an owner decision or an owner-only probe and no fence can fix them. The full table,
per row, is `tasks/reports/cai4-blocked-reread.md`.

## Findings for other programs (named, with the cause)

1. **`gk-core/src/FusionRpg.Core/Match/**` has no focused verification boundary** — it resolves through
   `core-fallback` (`gk-core/scripts/verification-boundaries.v1.json`), which runs the whole `core` project group:
   **35 test projects, ~15.6k tests, ~4 minutes per verification call**. Every Core/Match edit pays it.
   Owning program: **test-verification-boundary** (the registry is held by the `tvb58`/`tvb59`
   single-writer chain, and `scripts/**` is outside this fence, so no row could be opened in their todo
   from here). Cause read: the `owner` boundary for `gk-core/src/FusionRpg.Core/**` is the module-level catch-all;
   `gk-core/tests/core-test-projects.v1.json` already *plans* a `FusionRpg.Core.Match.Tests` project for
   `Match/**`, so the missing piece is the focused mapping, not the test home.
2. **`guard-doc-citations.ps1 -Strict` is RED on 7 other programs' documents** (`legion-build`,
   `npc-story-events`, `strain-splice-host`, `trade-network` ×3, `world-stage`) with **0 `combat-ai/`
   lines**. Pre-existing and attributed in the ledger before this lane; recorded here only because an
   earlier line of this lane's own evidence mis-read it as green (a pipeline-exit artifact, corrected in
   `CAI-cite-2.md`).
3. **The `combat-ai` tuning domain cannot advance from any combat-ai lane** because both readers name
   `combat-ai.v1.json` by hand. Already filed as `R-TUNING-PUBLISH`; this lane re-measured it and confirms
   it blocks four rows.
4. **CAI2.3's erratum and CAI2.6's ruling are owner decisions, not paths** — both are already filed; this
   lane re-read them and confirms neither has an in-fence half left.

## Stated deviations from the rows' own file lists

Every row named `tests/FusionRpg.Core.Tests/Match/Ai/...` for its tests. That path is **outside this
lane's fence**, and a new test project cannot be registered from inside it (`FusionRpg.slnx` and
`gk-core/scripts/verification-boundaries.v1.json` are other sessions' paths). The new Core tests therefore live in
`tests/FusionRpg.Core.Balance.Tests/CombatAi/` — the in-fence project that already hosts this program's
decision/schedule policy tests. Each row's text and evidence fragment records the deviation.
