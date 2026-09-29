# CAI4.1 — `lawn-actor-view`: an `IBattleView` over the board (CHAIN SLICE)

Lane `combat-ai-2`, resumed after the `features/mega-merge` merge (integration head `b0e0ff95`, merged as
`eaafeaaa`). The row's dependencies are both satisfiable now — CAI1.1 is `done` and **BCU0.1 is `[x]`
closed** — so my earlier "PARTIAL FENCE / blocked" classification for this row was too broad and is
corrected here: **three of its five files are in-fence** (`Actions/Ai/Lawn/{LawnBattleView,LawnRelationChain,LawnDerivedCache}.cs`
and the two test files), and only `Injector/Effects/LawnActorViewHost.cs` is not.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The relation chain composes the two shipped oracles, specimen-first | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnRelationChainTests"` | **4 passed, 0 failed** — `Specimen_ownership_wins_when_both_links_can_answer` is the hypnosis case (the player DEPLOYED `hypno:1` but it sits on the zombie side, so the oracles disagree and both are individually right); the specimen link wins, and the mechanical link is asserted NOT to have been asked at all, so a second read cannot contradict the first. `The_chain_falls_through_to_the_mechanical_link_when_the_specimen_links_answer_is_null` covers the ordinary plant | `Actions/Ai/Lawn/LawnRelationChain.cs` |
| Null means unknown, and the chain does not resolve it | same run | passes — `An_unknown_ptr_returns_null_and_is_never_defaulted`: both links are asked, both answer nothing, and the chain returns null. Resolving it to Enemy is `LawnUnitViewFactory.Build`'s job ("never silently dropped, never mis-read as Self/Ally"); defaulting here would erase the difference between "not mine" and "I cannot tell" | — |
| Both links are required | same run | passes — a null link throws, so a caller cannot silently ship a one-link chain whose order is then meaningless | — |
| Acceptance line 1: the new files are under `Actions/Ai/Lawn/`, NOT `Match/Ai/`, and the guard is green and UNMODIFIED | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ILawnBoardView"` | **6 passed, 0 failed** — `ILawnBoardViewTests` was not touched by this commit (its pattern list is not widened and its scope is not carved out); the new file is at `Actions/Ai/Lawn/LawnRelationChain.cs` | — |
| Golden: byte-identical, no battle/siege/delve file edited | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~Lawn\|Category=BalanceGuard"` | **204 passed, 0 failed** | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnRelationChain.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/Lawn/LawnRelationChainTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14964 passed, 4 failed** — the four pre-existing corpus facts | — |

## A stated deviation from the spec's snippet, with its reason

The spec sketches `IOwnSideOracle[] _links  // structural: exactly the two shipped oracles` and loops
them. This takes `(IOwnSideOracle specimenOwnership, IOwnSideOracle mechanicalOwnSide)` instead, both by
name at every call site. The precedence IS the class's whole content — "which player deployed it" outranks
"which mechanical side is it on" — and an array leaves that to positional convention plus whoever appends
a third link. Two named parameters make the order structural; the behaviour is identical.

## Post-merge verification (why this slice starts from a verified base)

The merge brought 51 commits from other lanes. It touched **none** of the trees this program's blocked rows
name (`git log 43a1b5ae..HEAD -- gk-core/src/FusionRpg.Data gk-core/src/FusionRpg.Server gk-core/src/FusionRpg.Core/Stats gk-core/src/FusionRpg.Core/Diagnostics gk-fusion/src/FusionRpg.Injector` is empty), and none of the files this lane wrote — the
incoming side's only changes under my areas were three `gk-core/tests/FusionRpg.Core.Tests/Items/**` files. The
merged tree re-ran **2265 passed / 0 failed** across every battle golden, expedition, siege, delve, stance,
decision-inspector, rung-resolver and balance-guard suite. The single merge conflict was my own session
record, resolved by taking the manager's re-seeded version and adding only what this lane actually wrote
(`gk-core/tools/CombatSim/**`, plus the note recording the brief's narrower fence).

## NOT done — the rest of the row

`LawnBattleView` (the view itself: twelve `IBattleView` members, each with a stated answer per the spec's
own table) and `LawnDerivedCache` (the revision-seam memo: at most one `_resolve` per (actor, frame), a
mid-frame revision bump costing exactly one further resolve for that actor and none for others) are not
built, nor are their tests. `Injector/Effects/LawnActorViewHost.cs` is out of this lane's fence. The row
also carries one now-stale acceptance line for whoever takes the view: it says "`IBattleView`'s member set
is exactly the TEN this view implements", but the interface has since gained `LiveActorKeysFor` (CAI1.11)
and `DownedAllyKeysOf` (CAI3.4), so the view must answer TWELVE — and it must answer the downed read
explicitly rather than inherit CAI3.4's default-empty, per that same line's "never defaulted".

## Cache slice — `LawnDerivedCache`, and the two reds the manager's ruling named

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `_resolve` is called at most once per (actor, frame) across many reads | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnDerivedCacheTests"` | **6 passed, 0 failed** — 20 reads cost ONE resolve, and `It_returns_the_very_instance_the_resolver_produced` asserts `Assert.Same`, so a hit is visible as the same instance rather than only as a call count | `Actions/Ai/Lawn/LawnDerivedCache.cs` |
| A mid-frame revision bump costs exactly one further resolve for that actor and none for others | same run | passes — counted: two actors resolve once each, one actor's revision moves mid-frame, and the total goes 2 → 3 while the steady actor stays at one | — |
| `BeginFrame` drops the memo; a constant seam is frame-scoped only | same run | passes — `BeginFrame_drops_the_memo_so_the_next_read_resolves_again` and `A_constant_revision_seam_makes_the_memo_frame_scoped_only`, the latter asserting the pre-`actor-liveness-refresh` behaviour explicitly rather than leaving it implicit | — |
| Golden: byte-identical | `--filter "FullyQualifiedName~BattleGolden\|~Lawn\|Category=BalanceGuard"` | **210 passed, 0 failed** | — |
| The row's own Verify filter | `--filter "FullyQualifiedName~LawnBattleView\|~LawnRelationChain\|~LawnDerivedCache"` | **10 passed, 0 failed** (`LawnBattleView` matches nothing yet — the view is the row's remaining piece) | — |
| Boundary (real paths, no placeholders) | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnDerivedCache.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/Lawn/LawnDerivedCacheTests.cs') -Session combat-ai-20260920"` | **14970 passed, 4 failed** (the four pre-existing corpus facts), rc 1 — the NUMBERS, per TVB-F3, not the exit code | — |
| Doc citations | `guard-doc-citations.ps1 -Strict` | exit 0, **0 HIGH** | — |

### The two reds the manager's ruling raised, re-run with their real numbers

1. **`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Battle"` → 1404 passed / 0
   failed**, and **`guard-actor-hub.ps1` → exit 0** ("ACTOR-HUB GUARD OK"). Both confirmed here.
2. **`SubprocessPipeDrainGuardTests.No_test_file_reads_stdout_then_stderr_synchronously` FAILS IN
   ISOLATION** — and the ruling's premise ("load-fragile, passes alone") does not hold at this head, so
   it should not be filed under that family without a look. Run alone it is `1 failed / 0 passed` in
   154 ms, deterministically, and the message names a FILE, not a timeout:

   > sequential stdout-then-stderr `ReadToEnd()` is a pipe deadlock and makes `WaitForExit` unreachable;
   > use TestSupport/ExternalProcess.Run (concurrent drain) instead:
   > `tests\FusionRpg.FileMove.Tests\SplitExecutorTests.cs`

   So the cause is a content violation in **`gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs`**, read
   at `SubprocessPipeDrainGuardTests.cs:55` — a fast, deterministic scan, which is why load has nothing to
   do with it. It is already filed (`tasks/test-verification-boundary-todo.md:424` TVB-F2, naming
   `SubprocessPipeDrainGuardTests.cs:55`) but described there as load-fragile; **my reading says the
   description is wrong and the fix is a one-file drain change in the FileMove tests** — reported, not
   touched, since both files are outside this lane and the ruling says not to "fix" it by widening
   anything.

## NOT done — the row's remaining piece

`LawnBattleView` itself (its twelve `IBattleView` members, each with the spec table's stated answer, with
the now-stale "exactly TEN" acceptance line corrected as recorded above) and its tests. In-fence.

## View slice — `LawnBattleView`, and the row's in-fence work is COMPLETE

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The row's own Verify filter | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnBattleView\|~LawnRelationChain\|~LawnDerivedCache"` | **18 passed, 0 failed** (8 view + 4 chain + 6 cache) | `Actions/Ai/Lawn/LawnBattleView.cs` |
| Acceptance line 1: the files are under `Actions/Ai/Lawn/`, NOT `Match/Ai/`, and the guard is green and UNMODIFIED | `--filter "FullyQualifiedName~ILawnBoardView"` | **6 passed, 0 failed** — `ILawnBoardViewTests` untouched: no widened pattern list, no carved-out scope | — |
| Side comes ONLY from the oracle, with the mutation killed | `--filter "FullyQualifiedName~LawnBattleViewTests"` | passes — `Side_comes_only_from_the_oracle_never_from_the_raw_board_side`: a unit whose raw board side says `zombie` but whose oracle answers `Ally` reads as MY side, and a ptr no oracle knows reads as the other side. `No_member_reads_the_raw_board_side` then asserts the FILE contains no `snap.Side`/`snap?.Side`/`entity.Side`/`e.Side` read, so replacing the oracle read with the raw field fails both halves | — |
| No decision edge → the census delegate is never invoked, and the frame reuses one materialisation | same run | passes — `The_census_delegate_is_never_invoked_until_a_member_asks`: 0 calls after construction and after `BeginFrame`, 1 after the first read, still 1 for the rest of the frame | — |
| N `DerivedOf` + N gate reads cost ONE Hub resolve | same run | passes — `Derived_and_Aggression_reads_share_one_memoised_resolve` (16 reads, 1 resolve) | — |
| `GarrisonedStructureKeyOf`/`ObjectivePositionOf` null; `PositionOf` non-null; `HpMilli` 0 at zero max and 1000 above max | same run | passes — all three asserted, plus `HpMilli` 250 at exactly a quarter | — |
| Twelve members answered, and the downed read is NOT inherited | same run | passes — `All_members_are_answered_and_the_downed_read_is_not_inherited` calls every member and asserts `typeof(LawnBattleView).GetMethod("DownedAllyKeysOf").DeclaringType == typeof(LawnBattleView)`, which is what "never defaulted" means after CAI3.4 added the default-empty member | — |
| The view declares no fog, and the row's last line: `StubIntentSource` runs against it UNMODIFIED | same run | passes — `DerivedOf` is non-null for a live actor (null on this seam means hidden, and nothing on a lawn is hidden); `StubIntentSource_unmodified_runs_against_this_view` asserts a real `ActionIntent` (`act.hit` at `zombie:9`) straight out of the shipped stub with no test-only seam | — |
| Golden: byte-identical, no battle/siege/delve file edited | `--filter "FullyQualifiedName~BattleGolden\|~Lawn\|Category=BalanceGuard"` | **218 passed, 0 failed** | — |
| Boundary (real paths, numbers not exit code) | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnBattleView.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/Lawn/LawnBattleViewTests.cs') -Session combat-ai-20260920"` | **14978 passed, 4 failed** (the four pre-existing corpus facts) | — |
| Guards | `guard-actor-hub.ps1`; `guard-doc-citations.ps1 -Strict` | both exit 0, doc-citations **0 HIGH** | — |

### The row's in-fence work is now COMPLETE

All three Core files exist with their acceptance lines covered by tests: `LawnRelationChain` (4), `LawnDerivedCache` (6) and `LawnBattleView` (8). The only file from the row's Files list not built is
**`Injector/Effects/LawnActorViewHost.cs`** — the adapter that would cache one view per perspective per
frame and supply the seven seams (`IOwnSideOracle` chain, census, unit HP pair, held actions, element,
status mask, derived resolver). It is under `gk-fusion/src/FusionRpg.Injector/**`, outside this lane's fence, and
without it no production host reaches the view — so the row stays blocked on that path rather than
declared done, exactly as CAI2.5 is.

**Two deviations from the spec's own words, both stated:**
1. `AggressionOf` forwards the Hub-composed `ai.aggression` and does NOT saturate it here. The spec's
   table says "saturated onto the closed tier range by module 6", but `aggressionRange` is a PROFILE value
   this view is never given, and `IBattleView.AggressionOf`'s own doc says an implementor "need only
   forward its own already-held Derived snapshot". Saturation happens in `CandidateScorer.EffectiveTier`
   at the scoring site, which is where the range lives.
2. `LiveActorKeysFor` returns the absolute list. A lawn has no fog and no view-order decorators (the
   bloodthirsty reorder is a battle/siege trait), so the viewer-relative read IS the absolute one — stated
   in the member's doc rather than left to look like an oversight.
