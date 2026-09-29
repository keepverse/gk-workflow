# Spec: `decision-perf` (combat-ai module 7)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) rev 3 ·
**Depends on:** `core-scorer` (module 1), `intent-router` (module 4) · **Unblocks:** `auto-policy-switch`
(14) and every wave-4 lawn module · **Status:** **part built** (CAI1.14, 2026-09-20): sites 1-4 landed, each with a zero-byte measurement where the path allows one (`CostLedger`, `CandidateScorer`, `TargetStage`, the bloodthirsty refill); site 5 (channel-id interning) and the `PerfProbe` section are `CAI-perf-1`, filed because `Core/Stats/**` and `Core/Diagnostics/**` are out of this lane's fence.

## Objective

*"Zero allocation per decision"* is the acceptance line `StubIntentSource` already claims for itself
(`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:23-25,61-63`) and the bar
`ActionSelectionTests.TryDeclareAllocatesZeroBytesAcrossTwoHundredActors`
(`gk-core/tests/FusionRpg.Core.Tests/Actions/ActionSelectionTests.cs:304-329`) already enforces — **against a
synthetic affordability check**. In production it is false, and the audit proved it (C4, C5). This module
makes it true, and makes it stay true, for every policy.

It also removes the one piece of genuine complexity in the decision path: siege builds an `AiCandidate`
for **every** live enemy and runs an **O(live) threat loop per candidate**
(`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs:284-502`), and only then truncates to the
structural `maxCandidatesScored` inside the scorer (`gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs:147-149`,
moved from Battle/Siege/SiegeAi.cs line 135 by CAI1.1).
That is O(n²) before the cap applies.

Four named sites, plus a fifth this spec found while checking the fourth:

| # | Site | What it allocates, per decision |
|---|---|---|
| 1 | `CostLedger.RowsFor` (`gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs:67-77`) | `new List<ActionCostRow>(rows.Count)` on **every** `Check`. `Check` is gate 3 of `UsabilityEvaluator` (`UsabilityEvaluator.cs:65-67`) in every mode, and production passes the real ledger (`BasicAttack.cs:177`, `TimelineDispatch.cs:80`) |
| 2 | `BloodthirstyView` (`gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:607-633`) | a `List<string>` sized to the live board **plus** the view object, per decision, for every `bloodthirsty` attacker |
| 3 | Siege candidate build (`SiegeAiIntentSource.cs:176,179,270`) | a capturing closure at `:176`, `new List<(string, AiCandidate)>(liveActorKeys.Count)` at `:179`, and `candidates.Select(c => c.Candidate).ToList()` at `:270`. **REWRITTEN by CAI1.14**: `TargetStage.BuildCappedInto` (`TargetStage.cs:84`) writes into the caller's warm pair, the closure's two captures are per-decision scratch fields with the delegate bound once (`SiegeAiIntentSource.cs:273-278`), and the same is done in `CoreIntentPolicy.ScoredTarget` (`CoreIntentPolicy.cs:321`) |
| 4 | `AiScoring`, moved to `Actions/Ai/CandidateScorer.cs` by CAI1.1 (was `SiegeAi.cs:135,137-145,169-176`) | `Take(...).ToList()` at `CandidateScorer.cs:147-149`, the rank/cut/select loops (LINQ replaced by manual loops in the move) at `:151-203`, and `TopThree`'s own `Select`/`OrderBy`/`Take`/`ToList` at `:256-264`. **REWRITTEN by CAI1.14**: `TopThreeInto` at `:349-384` (caller-supplied 3-slot buffer; `TopThree` at `:326` delegates to it) and the whole rank/cut/select pipeline is now `ChooseTargetInto` + `SelectionScratch` at `:188`, allocation-free once warm — the four per-decision `List` allocations (`Take`/`inTier`/`survivors`/`cut`) no longer exist, replaced by `poolCount` plus three reusable index lists. `ChooseTarget` at `:175` is the allocating convenience overload, kept for one-shot callers and tests |
| 5 | **Found here, previously unnamed:** `DerivedStatChannels.ResourceMax` / `ResourceRegen` (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:540-541`) are `$"{prefix}.{resourceId}"` — **two string allocations per cost row**, on the path `CostLedger.Check` → `ActorResourcePools.Resolve` (`gk-core/src/FusionRpg.Core/Actions/Cost/ActorResourcePools.cs:51-55`) → `ResourceChannelReader.Max`/`RegenPerMilleTick`. Site 1's fix alone would not have reached zero, and only a measurement would have shown it |

Site 5 is also the cheapest half of the lawn's *"uncached resolve"* cost the perf audit blames
(`CLAUDE.md` perf row; `LawnBasicAttackCostCharger.cs:62` sits on the same call), so fixing it pays twice.

**Why this matters beyond tidiness.** On the lawn the decision runs in the injector on the Unity main
thread; `KernelAllocationTests`' own header states the rule this repo already accepted —
*"allocation is a correctness constraint, not a tuning concern: GC pressure is what produces stutter"*
(`gk-core/tests/FusionRpg.Core.Tests/Battle/Timeline/KernelAllocationTests.cs:6-14`). In turn modes the same
allocations multiply by actors × rounds × expeditions resolved at collect.

## Tech stack

`FusionRpg.Core` only. No new dependency, no data file, no tuning row. One `PerfSection` member and its
name (`gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:6-41,53-80`), which are structural by that file's own
declaration (`:50-51`).

**Sequencing.** This module lands **after** `core-scorer` (module 1) and `intent-router` (module 4), which
is why the map gives it those dependencies: module 1 moves `AiScoring` out of `Battle/Siege/` into
`Core/Actions/`, and module 4 moves `BloodthirstyView` into a trait decorator. Fixing sites 2 and 4 before
those moves would fix them twice. Paths below name the **post-move** homes and say so.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocation|CostLedger|AiScoring|SiegeAi|ActionSelection|IntentRouter"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~KernelAllocation"
python gk-core/scripts/audit-overflow.py --targets A3
python gk-core/scripts/guard-battle-responsibility.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
```

No `publish.py`: this module adds no tunable.

## Project structure

| What | Where |
|---|---|
| Site 1 + the `TryPay` scratch array | `gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs:42-77,106-138` (as built by CAI1.14: `RowsFor` at `:96`, the precomputed table at `:50-58`, `TryPay` at `:126-185`) |
| Site 5 — interned channel ids | `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:540-541` (+ a by-index accessor) and `gk-core/src/FusionRpg.Core/Actions/Cost/ActorResourcePools.cs:44-55` |
| Site 2 — reusable bloodthirsty view | the trait decorator `intent-router` creates from `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:495-633` |
| Site 3 — siege candidate buffers + the closure | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs:250-506`, `RetargetLedger.TryGetHeld` (`RetargetLedger.cs:34-48`) |
| Site 4 — allocation-free argmax | `AiScoring`, moved by CAI1.1 to `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs` (`Argmax` at `:191-203`; was gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs lines 132-176) |
| The O(n²) cap | `SiegeAiIntentSource.cs:284-502` — the cap moves above the per-candidate work |
| Perf section | `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:6-41` (`AiDecide = 25`), `:50-51` (`SectionCount` 25 → 26), `:53-80` (`"ai.decide"`) |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs` (new — **landed**, CAI1.14) |

## The shape

### Site 1 — `CostLedger.RowsFor`

`RowsFor` filters the supplied rows by `ActionCostTiming` on every call. The input dictionary is
constructor-supplied and immutable for the ledger's life (`CostLedger.cs:44,51-65`), so the filter is a
**constant** and belongs in the constructor:

```csharp
readonly record struct CostKey(string ActionId, ActionCostTiming When);     // IEquatable by construction
readonly Dictionary<CostKey, IReadOnlyList<ActionCostRow>> _rowsByKey;      // built once, in the ctor

IReadOnlyList<ActionCostRow> RowsFor(string actionId, ActionCostTiming when) =>
    _rowsByKey.TryGetValue(new CostKey(actionId, when), out var rows) ? rows : Array.Empty<ActionCostRow>();
```

`Dictionary<CostKey, …>` with the default comparer devirtualises for a struct key that implements
`IEquatable<T>`, so the lookup boxes nothing. `Array.Empty` for a miss preserves today's behaviour for an
action with no cost rows exactly (`CostLedger.cs:135`), including `TryPay`'s `rows.Count == 0` early
return (`:113`).

`TryPay` also allocates `new long[rows.Count]` per call (`:118`). It is a commit-path call, not a
decision-path one, but it is the same file and the same test:

```csharp
// Structural (tunables-ssot.md T2): a per-call scratch bound, not a balance number and not a cap on
// any magnitude — an action with more rows than this allocates, it is never refused.
const int StackCostRows = 8;
Span<long> amounts = rows.Count <= StackCostRows ? stackalloc long[StackCostRows] : new long[rows.Count];
```

### Site 5 — interned resource channel ids

`ResourceMax(id)` / `ResourceRegen(id)` build a string per call (`DerivedStatChannels.cs:540-541`).
`ResourceIds` is a closed six-member vocabulary (`:550`), and `ActorResourcePools` already resolves a
resource to an index (`ActorResourcePools.cs:44-49`). So intern both id tables once, indexed the same way:

```csharp
// Six resources, two channels each — a closed vocabulary (DESIGN-GATE Resources row), so the ids are
// constants, not strings to rebuild. The per-id overloads stay and now return the interned instance,
// so every existing caller is byte-identical and nobody has to move to the index form.
static readonly string[] ResourceMaxIds  = BuildIds(ResourceMaxPrefix);
static readonly string[] ResourceRegenIds = BuildIds(ResourceRegenPrefix);
public static string ResourceMax(int index) => ResourceMaxIds[index];
```

`ActorResourcePools.Resolve`/`TrySpend` pass the index they already computed. The returned strings are
identical, so `ActorDerivedSnapshot.Get` reads the same channel — semantics byte-identical, allocation
gone.

### Sites 2, 3, 4 — reuse, don't rebuild

**Site 2 (bloodthirsty).** One instance per battle, owned by the trait decorator `intent-router` builds,
with its backing `List<string>` `Clear()`ed and refilled per decision — a cleared `List` keeps its
capacity, so once warm it allocates nothing. Safe as a single instance because a decision never nests:
re-entry depth is 0 (`overlay-control-loops.md` §6 rule 7), and the view is consumed synchronously inside
one `TryDeclare`. **Assert that**, do not assume it: a test re-enters the decorator and expects a throw
rather than a silently shared buffer.

**Site 3 (siege buffers and the closure) — as built by CAI1.14.** `TargetStage.BuildCappedInto`
(`Actions/Ai/TargetStage.cs:84`) is the phase A/B/C stage writing into a caller-supplied `List<string>`
and `List<TargetCandidate>`; `BuildCapped` (`:57`) is the allocating convenience overload. The siege
source and `CoreIntentPolicy` each own one warm pair, so the per-decision `List` allocations are gone.

- The closure `candidateKey => IsStillScoreable(candidateKey, mySide, liveActorKeys)`, which captured two
  locals and allocated a display class **and** a delegate per decision, is gone: `_scratchMySide`/
  `_scratchLive` are per-decision scratch fields and `_stillScoreable` is bound once in the constructor.
  The same is done for the three other per-decision delegates (`_sideOf`, `_isReadable`,
  `_tryBuildCandidate` — the last was a local function capturing two locals).
- The source's own guard makes a nested decision throw rather than share that scratch
  (`Re_entering_the_siege_decision_throws_instead_of_sharing_its_scratch`); the fields are documented as
  single-decision scratch with the same re-entry-depth-0 reasoning.
- `RetargetLedger.TryGetHeld`'s `Func<string, bool> stillValid` parameter (`RetargetLedger.cs:34-48`) is unchanged — the
  caller stops allocating one, the ledger keeps its clean signature.

**Site 4 (the LINQ chain) — as built by CAI1.14.** `ChooseTargetInto` (`Actions/Ai/CandidateScorer.cs:188`)
is the pipeline; `ChooseTarget` (`:175`) is the allocating convenience overload that hands it a fresh
`SelectionScratch`. It runs the same ordered passes the LINQ chain did — best tier, rank, min-shift cut,
`argmax(Score)` with the **same** ordinal `ActorKey` tie-break (`Argmax`, `:244`) — over candidate
INDICES, writing into the scratch's three reusable lists. `Take(maxCandidatesScored).ToList()`
(`:147-149`, was `:135`) is gone: `poolCount = min(Count, MaxCandidatesScored)` indexes the original
list, which is the same first-n set in the same order. The weighted mode's `List.Sort` delegate is gone
too — an in-place insertion sort over the scratch's own index list (`ActorKey` is unique, so the order is
the same). `TopThree` (`:326`) delegates to the caller-buffer `TopThreeInto` (`:349-384`) and is called
only when a `BattleTrace` is attached (`SiegeAiIntentSource.cs:340-373`) — **trace-on is explicitly out of
the zero-allocation envelope**, because `BattleTrace` is an opt-in observability object that allocates by
design.

**Byte-identity of site 4.** The LINQ chain is `Where(tier == best).OrderByDescending(score).ThenBy(key,
Ordinal).First()`. `OrderBy` in LINQ is a **stable** sort, but the explicit `ThenBy` on the ordinal actor
key makes the order a total one, so a hand-written argmax with the same two comparisons picks the same
element. Prove it as a property test over shuffled inputs, do not argue it.

### The O(n²) cap — and why it is byte-identical

Today: build one candidate per live enemy that passes the skip filters (self, same side, unreadable
derived — `TargetStage.cs:98-107`), each running an O(live) threat loop (`:410-424`); then
`AiScoring.ChooseTarget` takes the **first** `maxCandidatesScored` of that list in order
(`Actions/Ai/CandidateScorer.cs:147-149`, moved from SiegeAi.cs line 135 by CAI1.1).

Change: stop the candidate loop once `maxCandidatesScored` candidates have been built.

```csharp
// Structural work bound (AiTuning.MaxCandidatesScored, siege.v1.json:115 = 32, already commented
// structural at SiegeAi.cs:54-58). Applied BEFORE the per-candidate threat loop rather than after —
// the same set, a fraction of the work.
if (candidates.Count >= _tuning.MaxCandidatesScored) break;
```

**The identity argument, precisely.** `candidates` is appended in `liveActorKeys` order, and `Take(n)`
keeps the first `n` of that same order — so stopping the loop at `n` produces the *identical* list. The
one thing that must not move is **which enemies count toward `n`**: the break goes **after** the three
skip filters and after the `DerivedOf` null check (`:184-188`), i.e. exactly where a candidate is about to
be added, so the same enemies are skipped and the same 32 survive. Placing it earlier would count skipped
actors and select a different set.

Complexity after: the outer loop is bounded by 32, so the threat term is O(32 × live) — linear in board
size, not quadratic. The **inner** threat loop still scans all live actors, and that is correct and must
not be capped: threat is *"nearby same-side raw power around a candidate"* (`:217-230`), so restricting it
to the candidate set would change the number, not the cost model.

### The perf section

```
PerfSection.AiDecide = 25   // "ai.decide" — SectionCount 25 -> 26 (structural, PerfProbe.cs:50-51)
```

`PerfScope` is a struct and records nothing when `Enabled` is false (`PerfProbe.cs:111-121,257-274`), so a
`using` scope around a decision adds no allocation and is free when the probe is off.

⚠️ **Index collision hazard, stated so it does not happen.** `lawn-cast-trigger` (module 19) adds its own
`lawn.ai.decide` section (ideal §6.3). **This module takes 25; module 19 takes 26** and must re-read this
line before adding it, because `SectionCount` and `SectionNames` are two places that must move together
(`PerfProbe.cs:50-51,53-80`). Two sections, not one: turn-mode decisions and lawn decisions have different
budgets and different owners, and `lawn.ai.decide` is explicitly **not** inside `KernelDriveHost`'s
0.05–0.15 ms (ideal §6.3).

## Tunables

**None added.** Every number this module touches already exists and keeps its current home and meaning:

| Number | Where | Class |
|---|---|---|
| `ai.maxCandidatesScored` = 32 | `gk-core/data/tuning/siege.v1.json:115` today; moves to `gk-core/data/tuning/combat-ai.v1.json` (new; module 2 creates it) with `profile-schema` (module 2), in that module's own commit | **Structural** — a per-decision work bound, already commented as such (`SiegeAi.cs:54-58`, and the tuning file's own `_note` at `siege.v1.json:103`). Not a progression ceiling: it bounds work, refuses nothing, and caps no magnitude |
| `StackCostRows` = 8 | code `const`, `CostLedger.cs` | **Structural** — a scratch-buffer bound; more rows allocate, they are never refused. Comment says so |
| `SectionCount` = 26 | `PerfProbe.cs:50-51` | **Structural**, and that line already says *"must match `PerfSection`'s member count above, not balance"* |

`ssot-power-scale.md` §11 gains no row: nothing here caps a magnitude. `audit-magic-numbers.py` gains no
finding: no balance number is written in code.

## Code style

- Indexed `for` over `IReadOnlyList<T>`, never `foreach` — `StubIntentSource.cs:61-63` names the boxed
  interface enumerator as the exact per-decision allocation the acceptance line forbids.
- No LINQ on a decision path. LINQ stays legal in setup, trace and test code.
- `checked` stays on every integer accumulation it is on today (`Actions/Ai/CandidateScorer.cs:97-110`
  moved from SiegeAi.cs by CAI1.1, `SiegeAiIntentSource.cs:486-488`) — an argmax rewrite must not
  quietly drop it, and `gk-core/scripts/audit-overflow.py` is the check.
- `long` for every magnitude that the threat sum and the score touch, unchanged (`AiScoring.Score` is
  already `long`-widened before multiplying, `Actions/Ai/CandidateScorer.cs:102-108`, moved from
  SiegeAi.cs by CAI1.1).
- Scratch state is a documented per-decision field with its re-entry assumption written next to it, never
  an undocumented mutable field.
- Reuse means `Clear()` + refill on a retained-capacity collection, never a pool with a lifetime nobody
  owns.

## Testing strategy

### The zero-allocation-once-warm test, and how it is measured

`gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs` (new), using the harness this repo already
settled on — `KernelAllocationTests.BytesFor` (`:18-28`): run once to warm, `GC.Collect()` /
`WaitForPendingFinalizers()` / `GC.Collect()`, read `GC.GetAllocatedBytesForCurrentThread()`, run the
measured pass, subtract. `ActionSelectionTests.cs:304-329` is the same shape applied to a policy over a
200-actor board, and it is the fixture to copy.

The measurement rules, stated so a later reader does not weaken them:

1. **Bytes, never milliseconds.** `KernelAllocationTests.cs:11-13`: *"A wall-clock test in CI measures the
   build agent's mood; an allocation delta is deterministic, fast, and fails for exactly one reason."*
2. **`GetAllocatedBytesForCurrentThread`, single-threaded**, so a background thread's allocation cannot
   leak into the reading.
3. **Warm first**, because the first call JITs, resolves statics and grows every buffer once. "Once warm"
   is the claim; the warm pass is what makes it measurable.
4. **The measured pass is a whole round** — every actor declares once — so a per-actor allocation cannot
   hide under a per-round one.
5. **Production collaborators, not fakes, for anything on the path this module fixes.** The existing test
   passes a synthetic affordability check, which is exactly why C4 went unnoticed: the new tests build a
   **real** `CostLedger` over real cost rows and real `ActorResourcePools`. A fake here would re-create the
   defect.
6. **Budget 0, asserted as `Assert.Equal(0, bytes)`**, with the byte count in the failure message so a
   regression names its own size (`KernelAllocationTests.cs:54` is the phrasing).
7. **Trace off.** `BattleTrace` allocates by design and is opt-in (`SiegeAiIntentSource.cs:78-81`); a
   separate test asserts the trace path still works, and does not assert 0.

| Test | Asserts |
|---|---|
| `The_fallback_policy_allocates_zero_bytes_per_round_with_a_real_cost_ledger` | Sites 1 and 5 through the real gate 3. Fails today |
| `The_core_smart_policy_allocates_zero_bytes_per_round` | Sites 3 and 4 |
| `The_core_performance_tier_allocates_zero_bytes_per_round` | The cheap tier stays cheap |
| `The_router_allocates_zero_bytes_per_round_including_the_bloodthirsty_decorator` | Site 2 |
| `The_siege_policy_allocates_zero_bytes_per_round` | The shipped policy, unchanged in behaviour |
| `CostLedger_Check_allocates_zero_bytes_for_an_action_with_cost_rows_and_for_one_without` | Site 1 both branches |
| `Resolving_a_pool_allocates_no_channel_id_string` | Site 5, isolated, so a regression names the right file |
| `Re_entering_a_reused_decision_buffer_throws_instead_of_sharing_it` | The re-entry assumption behind sites 2 and 3 |

### Behaviour identity (this module changes no outcome)

| Test | Asserts |
|---|---|
| `RowsFor_returns_the_same_rows_in_the_same_order_as_the_filtering_implementation` | Site 1 |
| `The_interned_channel_id_equals_the_formatted_one_for_every_registered_resource` | Site 5, over `DerivedStatChannels.ResourceIds` — a **closed** six-member vocabulary, so iterating it is a contract assertion, not a population count |
| `Argmax_picks_the_same_candidate_as_the_LINQ_chain_over_shuffled_inputs` | Site 4, as a property test |
| `Capping_the_candidate_loop_yields_the_identical_set_Take_produced` | The O(n²) fix, with more than `maxCandidatesScored` live enemies |
| `The_cap_counts_only_candidates_that_passed_the_skip_filters` | The one way the cap could select a different set |
| `A_battle_with_a_trace_still_records_the_same_top_three` | `TopThree`'s buffer rewrite |

**Golden impact: byte-identical, claimed for one reason and testable.** Every change here is a rewrite of
*how* a value is produced, never *which*: the same rows, the same channel ids, the same argmax, the same
capped set. Run `BattleGoldenTests`, `ExpeditionResolverTests`, `SiegeAiLiveWiringTests`,
`CostLedgerTests` and `KernelAllocationTests`, and **report what they printed** — a byte-identity claim
that was not run is an opinion (DESIGN-GATE §3 rule 4). No `RulesetVersion` bump is claimed or needed.

## Boundaries

**Always**

- Fix the allocation by removing the work, not by pooling: a constructor-time table, an interned id, a
  reused buffer with a documented owner.
- Keep `checked` and `long` exactly where they are today.
- Measure with the established harness, with production collaborators.
- Write the re-entry assumption next to every reused buffer, and test it.

**Ask first**

- Any change that would move a number, a rounding, or a tie-break. This module's whole claim is that none
  moves.
- Converting `ActorResourcePools`' string-keyed API to index-only. This spec adds an index overload and
  keeps the string one; removing it is a wider refactor with callers outside this program.

**Never**

- Cap the **inner** threat loop. Threat is a property of the board, not of the candidate set, and
  narrowing it would change a number under a perf heading.
- Claim zero allocation from a test that uses a fake affordability check — that is how C4 survived.
- Assert milliseconds anywhere in CI.
- Add a `try/catch` or an `#if` around the measurement to make it pass on a slow agent.
- Start a second `PerfSection` numbering, or take index 26 (module 19's).
- Treat `maxCandidatesScored` as a balance dial — it is a structural work bound and stays commented as
  one.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** None new. It touches responsibility **6** (resource resolve
   and consume) at `CostLedger`/`ActorResourcePools`, and responsibility **5**'s deciding half through the
   siege candidate loop. Both are edits to *how* an existing owner computes, never to *what* it decides,
   and no second owner appears.
2. **Does it DECIDE or RESOLVE?** Neither — it changes the cost of both without changing either. The one
   resolving mechanism it edits (`CostLedger.Check`/`TryPay`) keeps identical semantics, asserted by the
   behaviour-identity tests above.
3. **Mechanism or loop?** Mechanism-preserving. Every fix lands inside the single existing implementation
   of the thing it speeds up — one ledger, one channel-id table, one scorer, one view decorator.
4. **Which existing implementation does it extend?** `CostLedger` (`CostLedger.cs:42-138`),
   `DerivedStatChannels` (`:540-541,550`), `ActorResourcePools` (`:44-55`), `AiScoring`
   (moved by module 1/CAI1.1 to `Actions/Ai/CandidateScorer.cs:140-262`; was SiegeAi.cs lines 132-176),
   `SiegeAiIntentSource` (`:167-281`),
   `PerfProbe` (`:6-41`). No new type owns any of these numbers.
5. **Does every mode get it?** Yes, and that is most of the point. Sites 1 and 5 are on **every** mode's
   gate 3, including the lawn's own charger (`LawnBasicAttackCostCharger.cs:62` reaches the same
   `CostLedger.Check` → `DerivedFor` path). Site 4 became shared when module 1/CAI1.1 moved `AiScoring` to
   `Core/Actions/Ai/CandidateScorer.cs`. Nothing here is battle-only or lawn-only.
6. **Is it deterministic and seeded?** Yes; it reads no RNG and no clock, and it must not start. The argmax
   rewrite preserves the ordinal tie-break that makes selection RNG-free
   (`Actions/Ai/CandidateScorer.cs:199`, moved from SiegeAi.cs line 143 by CAI1.1, ideal §3
   principle 4), and the property test over shuffled inputs is what proves determinism rather than
   asserting it.

## Success criteria

1. Every named site allocates zero bytes in the measured pass, with a **real** `CostLedger` and real pools.
2. The zero-allocation test exists for every policy the program ships: fallback, core smart, core
   performance, router (with decorators), siege.
3. `Resolving_a_pool_allocates_no_channel_id_string` passes — site 5, the one a measurement found.
4. Siege's candidate loop is bounded by `maxCandidatesScored` **before** the threat loop, and the capped
   set is provably the set `Take` produced.
5. No LINQ remains on a decision path (`AiScoring` in its post-module-1 home, the policies, `CostLedger.Check`).
6. `PerfSection.AiDecide` exists at index 25, `SectionCount` is 26, and `SectionNames` has `"ai.decide"`
   at the matching index.
7. `BattleGoldenTests`, `ExpeditionResolverTests`, `SiegeAiLiveWiringTests`, `CostLedgerTests` and
   `KernelAllocationTests` all green and unchanged, with the run output quoted in the commit body.
8. `python gk-core/scripts/audit-overflow.py --targets A3` reports no new finding — the argmax and threat rewrites
   kept `checked` and `long`.
9. `guard-battle-responsibility.py` green.

## Open questions

1. **Does the zero-allocation test belong in CI, or in `FusionRpg.Bench`?** `ActionSelectionTests` and
   `KernelAllocationTests` already assert 0 bytes inside `FusionRpg.Core.Tests`, which CI runs, and they
   have not been flaky — but a future runtime with a different JIT or a Server-GC agent could allocate on
   a path this code does not own. Options: (a) keep it in `Core.Tests` beside the two existing precedents;
   (b) move all three to `FusionRpg.Bench`, which CI does not gate on; (c) keep it in `Core.Tests` with a
   small non-zero budget. **Recommended default: (a)** — it matches the two shipped precedents exactly,
   and (c) is the shape that lets a regression in and then gets bumped, which is the population-count
   anti-pattern wearing a perf hat. If it ever does flake, the fix is to name the allocating frame, not to
   raise the budget.
2. **`maxCandidatesScored` reads from the view's order — is that order stable enough to cap on?**
   `IBattleView.LiveActorKeys` is the engine's live actor list, and siege freezes acting order per round
   (S3: *"Frozen acting order per round (R4) — recomputed only at round start"*), so the first 32 are
   stable within a round. Across rounds the set changes as actors die, which is correct and is what
   `Take(32)` already does today. Options: (a) cap on view order — today's behaviour, byte-identical, what
   this spec builds; (b) order candidates by a cheap pre-score first, which would be *better* AI and a
   golden-moving change. **Recommended default: (a)**; (b) is a **cross-module note for `core-scorer`
   (module 1) and `profile-schema` (module 2)** — "which 32" is a profile question, and it must land as its
   own cause with its own re-bless, never inside a perf commit.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: the action cost ledger, actor resource pools, the
    derived channel-id vocabulary, the siege AI policy and scorer, and PerfProbe.
[~] I established and recorded this session's boundary: /spec authoring lane under session
    backlog-clean-up-20260920 (record named by combat-ai-map.md). I did NOT run
    session-boundary-check.py — this lane runs no repo mutations and writes only this spec file.
    GAP NAMED.
[x] I read every doc in the §1 row(s) for those subsystems, this session: DESIGN-GATE.md
    (Performance row, Resources row, Any-cap row, Numeric-magnitude row, Battle row),
    battle-engine-ssot.md §2/§3c/§5, combat-ai-map.md, combat-ai-ideal.md rev 3 §4.4/§6.3,
    research/combat-ai/AUDIT.md (C4, C5, challenge 3), S1, S3, S4.
[x] I checked decisions.md for a lock covering this: row 44 (Action selection) pins the current
    targeting path and its no-bump reasoning; this module moves no outcome, so neither is disturbed.
[x] Every factual claim cites file:line, and every file cited was opened in this session —
    including site 5, which was found by opening ActorResourcePools.cs -> ResourceChannelReader.cs ->
    DerivedStatChannels.cs rather than by trusting the audit's four-site list.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE, not comments. In particular: StubIntentSource's own doc comment
    claims zero allocation, and it is TRUE ONLY OF ITS OWN BODY — gate 3 allocates. A comment is not
    evidence; this module exists because of that gap.
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. The "byte-identical" and "fails today"
    claims are stated as claims to RUN: this lane runs no builds or tests by instruction. Success
    criteria 1, 7 and 8 require the implementer to run and report.
[x] Nothing contradicts a §2 invariant. Invariant 10 (perf is a main-thread problem) is the reason
    this module exists; invariant 13 (magnitudes fit their range) is preserved by keeping every
    `checked`/`long` in place and re-running audit-overflow.py.
[x] Corrections propagated: the audit's C4 and C5 are answered here; the ideal's §4.4 table gains a
    fifth row (site 5) that this spec names, and the ideal's own §6.3 target is what these tests
    enforce. Anyone editing §4.4 should add site 5 there.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The pinned literals are: 0 bytes (a contract, not a reading), SectionCount 26 (a closed
    enum's member count, the file already calls it structural), and the six-member ResourceIds
    vocabulary (closed, DESIGN-GATE Resources row). Reasons stated for each.
[x] No event-refreshed cache is introduced (§2.16). _rowsByKey and the interned id arrays are built
    from immutable constructor input and a closed vocabulary; neither has a refresh trigger, and
    neither has a key set that can move at runtime. If a future caller makes the cost dictionary
    mutable, that caller introduces a cache and owns this checklist row.
[x] No acceptance criterion fixes an ordering that can vary in real play — the two order-sensitive
    claims (argmax identity, capped-set identity) are asserted over shuffled and over
    larger-than-cap inputs respectively, not on one arrangement.
[x] Produces/consumes no actor combat magnitude and composes nothing; ActorHub is untouched. It
    READS ActorDerivedSnapshot through the existing ResourceChannelReader and changes only the
    string used to key it.
[x] Does not invent or extend a SOLID-violating parallel path. No second ledger, no second scorer,
    no object pool with an unowned lifetime; every fix lands inside the single existing owner.
[x] A new rule has a registry row: "no allocation on a decision path" is enforced by the tests named
    above (the same enforcement class as the two shipped allocation tests, which also have no shell
    guard). If the implementer wants it mechanically swept across future policies, that is a guard
    script and a row in gk-core/scripts/enforcement-registry.v1.json; as specified, it is test-covered and
    not unguardable.
```
