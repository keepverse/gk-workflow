# Spec: `auto-policy-switch` (combat-ai module 14)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md)
§7 + owner ruling **D1** · **Depends on:** `ai-tiers-personality` (3), `resolvable-here` (5),
`decision-perf` (7), `replay-identity` (8), `action-schedule-twin` (9) · **Unblocks:** nothing — it is
the last module of wave 3 · **Status:** spec, 2026-09-20. Not built.

## Objective

Battle and expedition auto-resolve run on `StubIntentSource`: nearest enemy, first usable action in
preference order (`StubIntentSource.cs:43-97`), reached through
`intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)` (`BasicAttack.cs:175-180`)
and, on reselect, through `intentSource ?? new StubIntentSource(...)` (`TimelineDispatch.cs:79-80`).
`WebMatchService` passes no `intentSource` on any of its five `BattleEngine.Resolve` calls
(`:136-165`, `:208-235`, `:391-410`), so **both sides** of every web battle and every expedition
collect are the stub today.

Owner ruling **D1**: *"Switch now, with the bump"* — the battle and expedition default becomes the
profiled policy, as **one cause, one commit, one re-bless**: `RulesetVersion` 5 → 6, a predicted-delta
writeup, the `action-schedule-twin` re-fit, and the dominance baseline re-measured (ideal §7, §10).

`decisions.md:44` already required this and named its own trigger: *"Trigger for the next bump: a real
divergent multi-action loadout reaching a live battle … bump `RulesetVersion` then with a
predicted-delta writeup."* The row's reasoning for **not** bumping in 2026-08 is precisely what this
module ends: *"the intent source's no-board `NearestEnemy` fallback is provably the same
first-in-list-order pick `SelectTarget` made."* A profiled policy is not that pick. The row is amended
in the same commit.

`RulesetVersion` is 5 today (`BattleModels.cs:284`), and it is part of the hashed payload — the v5
paragraph says so in its own words: *"the hash moves on the version stamp alone
(`BattleReport.RulesetVersion` is part of the hashed payload), independent of whether any actual
magnitude changed"* (`:277-284`). So the four constants in `BattleGoldenTests.cs:77-80` move by
construction, and the question this spec must answer honestly is what **else** moves.

⚠️ **This is an economy lever, not only an engine change.** Expeditions auto-resolve at collect
(`ExpeditionEndpoints.cs:136` → `WebMatchService.RunPlannedMatchAsync`), and their rewards read the
battle outcomes. Ideal §1 flags it; D1 rules that the switch happens anyway, with the reward-rate change
**stated in the writeup**. Stating it is this module's deliverable.

## Tech stack

`FusionRpg.Core` (`BattleModels.cs`, `BasicAttack.cs`/`TimelineDispatch.cs` via module 4's router,
`BattleRunState`'s default-policy construction), `gk-core/tests/FusionRpg.Core.Tests` (the re-bless),
`docs/research/combat-ai/` (the writeup), `docs/architecture/decisions.md` (row 44 amendment). No new
dependency, no new project, **no tuning publish** (see Tunables).

## Commands

```powershell
# 1. TRIAGE, BEFORE any constant is touched -- the whole battle suite, unfiltered.
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Battle"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Category=BalanceGuard"

# 2. Evidence the writeup needs.
dotnet run --project gk-core/tools/ProvePredictor                      # twin<->port parity, both scopes
dotnet run --project gk-forge/tools/DominanceBaseline -- --theta 100    # record; expected UNCHANGED (see below)

# 3. After the re-bless: the full suite, because this crosses program/module boundaries
#    (AGENTS.md "Verification boundary", case 2).
.\scripts\test-fast.ps1 -AllDefault
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
```

## Project structure

| What | Where |
|---|---|
| `RulesetVersion` 5 → 6 + its v6 doc paragraph | `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:270-284` |
| The default policy the router falls back to | `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:175-180` and `gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs:79-80`, both owned by `intent-router` (module 4) after wave 1 |
| Where `DefaultAiIntentSource` is set (siege opt-in today) | `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` construction (`if (aiTuning != null)`, S1-battle-core.md §"Who decides") |
| The four golden constants | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:77-80` |
| The running re-bless ledger (a new dated paragraph) | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:18-76` |
| Predicted-delta writeup | `docs/research/combat-ai/predicted-delta-rulesetversion-6.md` (new; does not exist yet) |
| Row 44 amendment | `docs/architecture/decisions.md:44` |
| The twin's re-fit call sites | `gk-core/src/FusionRpg.Core/Balance/Analytic/Predictor.cs:38-42`, `gk-core/tools/ProvePredictor/Program.cs:114-137` |
| Expedition reward path (measured, not changed) | `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:136-163,207` |

## The shape

### 1. What actually changes

Exactly one thing: **which policy the battle default resolves to.** After module 4 the fallback chain is
the router's, owned once; module 14 changes its terminal entry from `StubIntentSource` to the profiled
core policy under the `battle/*` place × role profiles (D5), with tier by actor class (D6) and the
seeded personality offsets (module 3).

Everything else is already in place when this lands, which is why it is last in wave 3:

| Prerequisite | Why the switch is wrong without it |
|---|---|
| 3 `ai-tiers-personality` | Decides which tier an actor runs. Without it the switch has no answer for a general creature and would run the full scorer for everything. |
| 5 `resolvable-here` | Battle's executor consumes only `ApplyResourceDelta`/`ApplyStatus`/`ModifyStat`/`PlaceStructure` (DESIGN-GATE §1 battle/turns row, `BattleEffects.cs:241-264`), and 9 of 13 atom triggers never fire in battle (`battle-engine-ssot.md` §4 D3). Without the filter the "smarter" policy picks actions that are **inert in battle**, spends the turn and the resources, and is strictly *worse* than the stub. The predicted delta would then measure a defect. |
| 7 `decision-perf` | Every expedition collect resolves several battles inline (`ExpeditionEndpoints.cs:124-163`). Switching to a scoring policy with `CostLedger.RowsFor` still allocating per `Check` (`AUDIT.md` C4) makes the bump a perf regression on the idle economy's own path. |
| 8 `replay-identity` | §3 below — the irreversible one. |
| 9 `action-schedule-twin` | §3 below. |

Siege is untouched: `core-scorer` (module 1) already re-expressed it byte-identically. The delve's
automated arm is module 13. The lawn is wave 4. **The blast radius of this module is exactly: ad-hoc
web battle, expedition collect, and the reselect fallback.**

### 2. One commit, one cause — the manifest

The commit contains all of these and nothing else:

1. `BattleRuleset.RulesetVersion` 5 → 6, with a v6 paragraph appended to the running doc comment in the
   established style (`BattleModels.cs:270-284` holds v4 and v5).
2. The default-policy flip.
3. The four re-blessed constants (`BattleGoldenTests.cs:77-80`) plus a dated paragraph in that file's
   ledger (`:18-76`), written in the same shape as the five that precede it: what moved, what held,
   what was triaged **before** the bless.
4. Any literal `RulesetVersion == 5` assertion updated — the 2026-08-24 re-bless names *"the two literal
   `RulesetVersion==2` assertions"* as part of its own triage (`BattleGoldenTests.cs:34-36`), so they
   exist and must be found by the triage run, not discovered afterwards.
5. `docs/research/combat-ai/predicted-delta-rulesetversion-6.md` (§4).
6. `decisions.md:44` amended: the trigger fired, the bump landed, and the row's next-bump trigger is
   restated for whatever follows.
7. The twin's re-fit: the `Predictor`/`ProvePredictor`/CombatSim call sites stop passing
   `SchedulePolicy.Greedy` and pass the shipped `battle/auto` profile's policy instead (module 9 §2).

**Not in this commit**, because each would be a second cause:

- A `combat-ai.v{n+1}` publish. The profile rows ship with `profile-schema` (module 2); this module
  changes a *reader default*, not a tuning key. H7 ("a tuning publish lands with its reader") is
  satisfied because that publish already landed with its reader.
- Any weight, floor or threshold change. Tuning the new policy is a balance pass **after** the bump, and
  a tuned number moving a golden again is a separate bump decision.
- The delve or lawn wiring.
- The decision inspector (module 10). It is off by default and golden-neutral, and it is the instrument
  that makes this triage cheap — land it before, not inside.

### 3. Ordering against modules 8 and 9 — why both are strict, not preferences

**8 `replay-identity` must land first, and this one is irreversible.**

Once the default is profiled, a `combat-ai.v{n+1}` publish changes every re-derived automated decision:
automated decisions are not recorded (`DecisionTrace.cs:5-20` holds `Player`/`Timeout` only), both
correlation-replay branches re-run `BattleEngine.Resolve` over the stored setup
(`WebMatchService.cs:136-151`, `:208-223`), and `ComputeContentHash` cannot see `gk-core/data/tuning/*`
(`RpgStore.ContentHash.cs:21-42`). Module 8 is what makes a match's profile version recoverable.

The reason the order cannot be swapped is not merely "it would be nice to have": every match logged
between 14 and 8 would be a **`RulesetVersion` 6 row with a NULL profile stamp**. Module 8's own rule —
NULL means "predates combat-ai profiles", i.e. the stub — is then false for those rows, permanently,
and no later commit can repair them because nobody knows which published profile they ran. Rows on disk
are not refactorable. This is the sharpest ordering constraint in the program and it belongs in the
plan as a hard edge, which the map already records (map §2 "Hard edges").

**9 `action-schedule-twin` must land first, for the one-cause rule.**

D1 requires the predictor re-fit **in this change**. It cannot be in this change unless `ActionSchedule`
can already express a reserve floor, waste guards and tier — otherwise the commit contains both the
twin's new expressiveness and the policy flip, and a moved `ProvePredictor` number is unattributable.
Module 9 lands with `SchedulePolicy.Greedy` as its identity row, so it moves nothing on its own
(module 9 §"What must be re-measured"); module 14 then changes one thing: which policy the callers pass.

**10 `decision-inspector` is recommended but not required.** It is the instrument that turns "the close
golden moved" into "the close golden moved because `squad:1` now targets `wave:0` first". Off by
default and out of `Digest`, so it cannot itself be the cause.

### 4. The predicted-delta writeup — required contents

`decisions.md:44` requires it; `BattleGoldenTests`' own ledger shows what a good one looks like
(*"outcomes/shapes held (stomp Victory, wipe Defeat with the coward retreating — verified pre-bless);
mirror-match symmetry 48–56%"*, `:20-23`). The document is written **before** the re-bless and states
its predictions, then records what was measured.

**(a) Why the hashes move at all.** By the version stamp alone, independent of any magnitude —
`BattleModels.cs:277-284` establishes this for v5 and it applies unchanged. State it first so a reader
does not mistake the hash diff for the behavioural delta.

**(b) What can behaviourally move, bounded by the fixtures' own shape.** The golden actors are built by
`BattleGoldenTests.Actor(...)` (`:82-92`), which sets `Key`, `Side`, `SpeciesId`, `TypeId`, `Level`,
`ElementPrimary`, `TraitIds`, `MaxHp`, `Atk`, `Defense` — and **no `EquippedActionIds`**. Per
`decisions.md:44`, *"empty/null falls back to a single hand-built basic attack"* whose envelope is
all-`Always`/all-zero. Three consequences, each checkable:

1. **Action choice cannot move.** One held action per actor.
2. **The reserve floor cannot bind.** A zero-cost envelope charges nothing, so no floor can refuse it.
3. **Only target selection can move** — stomp is 2 v 3, close 2 v 2, wipe 2 v 2, so the candidate sets
   are two or three deep and a scored pick can legitimately differ from `NearestEnemy`'s
   first-in-list-order pick.

That is a narrow, falsifiable prediction, and it is the writeup's spine.

**(c) What must hold, and stops the bump if it does not.**

- `Golden_outcomes_hold_their_shapes` (`BattleGoldenTests.cs:215-224`) green **unchanged**: stomp
  Victory, wipe Defeat, the coward retreats. Every previous re-bless asserted this held
  (`:41-44`, `:57-60`, `:70-76`).
- Every **rate** test green and untouched — PS-3 (`ssot-power-scale.md`): a rate golden must not move.
  The 2026-08-25 pass names them: `Parity_hit_rate_is_ninety_percent`, `Parity_crit_rate_is_five_to_ten_percent`,
  the locked bands 0.90±0.02 and 0.05–0.10 (`BattleGoldenTests.cs:53-58`).
- `Goldens_do_not_depend_on_the_platform` and `Goldens_do_not_depend_on_the_content_stamp`
  (`:180-212`) green — they are portability guards, not outcome pins.

**If a shape moves, the module stops and reports.** A moved shape means the switch is a balance change,
not a representation change, and that is an owner call — D1 approved a *policy* switch with a bump, not
a change to which golden fight is won.

**(d) The expedition reward-rate impact — the required half.** Traced through code, three channels:

| Channel | Site | Moves? |
|---|---|---|
| Specimen XP | `ExpeditionEndpoints.cs:148-163` — on `BattleOutcome.Victory`, each **surviving** squad actor earns `SpecimenXpPerBattleWon × actor.XpMilli` | **Yes**, on two axes at once: more victories, and more survivors per victory. |
| Contract loyalty | `:207` `ApplyContractResults(playerId, squadIds, victories * 2 >= battleResults.Count)` — a majority-of-victories flag | **Yes, and discontinuously.** It is a threshold at 50%, so a small victory-rate shift flips it for the runs sitting on the boundary. The writeup must report the share of tiers near that boundary, not only the mean. |
| Wild joins, greedy multiplier, the rest of the manifest | `:109` `ExpeditionResolver.Resolve(...)` runs **before** any battle, and `:168+` maps its manifest onto store writes | **No.** Outcome-independent by construction. Say so — it bounds the blast radius. |

The ad-hoc web match has the same loyalty channel (`WebMatchService.cs:174-175`,
`ApplyContractResults(..., report.Outcome == BattleOutcome.Victory)`).

**The direction is not assumed.** Expeditions pass no `intentSource`, so **both sides** get the new
policy — symmetric, per D2 (*"the same for all"*). A smarter squad and a smarter wave do not obviously
net out in the player's favour, and the writeup must report a **measurement**, not an intuition:
resolve each expedition tier's planned setups over a fixed seed sweep before and after, and report the
victory-rate delta per tier plus the share of runs that cross the `victories * 2 >= count` threshold.
This is offline, deterministic and cheap — `RunPlannedMatchAsync` is a pure resolve over a sealed
`(setup, seed)` once the log row exists.

**(e) The twin and the baselines.**

- `gk-core/tools/ProvePredictor`, both scopes, under `1e-4` after the re-fit (`gk-core/tools/ProvePredictor/Program.cs:152-160`).
- **The dominance baseline is expected to be UNCHANGED, and that is a verified claim, not an
  assumption.** `DominanceGuard.cs:64` and `TerminationGuard.cs:100` call `Predictor.Predict(a, b)` —
  the two-argument overload, which passes `economy: null` (`Predictor.cs:73-74`) — so the action
  economy is not on the dominance path at all. Re-run `gk-forge/tools/DominanceBaseline --theta 100` and record
  the result as confirmation. **If it moves, stop**: it means the economy reached a path nobody
  expected, and the fit being re-measured is not the fit that moved.
- `ResidualFitLoopTests`' own gate is *"0 change(s) computed … nothing to publish"*
  (`ResidualFitLoopTests.cs:17-26`). Still zero, or the twin leaked into the aptitude fit.

### 5. Triage before bless — the procedure, not a suggestion

Every previous re-bless in this file triaged first and recorded what it found
(`BattleGoldenTests.cs:36-44`: *"Triaged BEFORE this re-bless, not after: the full CORE suite's only
failures were these hash goldens, the two literal `RulesetVersion==2` assertions, and the three
B=0-specific `BattleMagnitudeParityTests`"*). Same procedure:

1. Make the policy change and the version bump. Do **not** touch a constant.
2. Run the whole battle suite and the `BalanceGuard` category.
3. Enumerate every failure. The allowed set is: the four hash constants, and literal `RulesetVersion`
   assertions. **Anything else is a finding**, and it goes in the writeup before it is touched.
4. Confirm the must-holds in §4(c) are green.
5. Only then re-bless the four constants, in one edit, with the ledger paragraph.
6. Run the full suite (`test-fast.ps1 -AllDefault`) — this change crosses Core/Server/tools, which is
   AGENTS.md's case 2 for the unfiltered suite.

A golden that is re-blessed before it is explained is a re-bless of an unknown, which is what the
file's own header forbids: *"A diff here is a determinism break or a balance change and MUST be a
conscious `RulesetVersion`/`EngineVersion` bump, never a silent re-bless"* (`:10-14`).

## Tunables

**None published by this module.** It changes a reader default; it adds no key and publishes no
`v{n+1}`. Every number the new default reads is `profile-schema`'s (module 2) in
`gk-core/data/tuning/combat-ai.v1.json` (new — **landed**, CAI1.8 — module 2 publishes it) — weights,
`keepPct`, reserve floors, waste-guard thresholds,
anti-repeat, `maxCandidatesScored`, `aggressionRange`, `retargetLatencyTicks` (ideal §8).

| Value | Where | Class |
|---|---|---|
| `BattleRuleset.RulesetVersion = 6` | `BattleModels.cs:284` | **Structural** — a determinism marker, never a balance number. It is a `const` and stays one; its doc comment carries the per-version history that explains every re-bless. |
| The `battle/*` profile rows | `combat-ai.v1.json` (module 2) | **Tunable**, and deliberately not touched here. Tuning them after the bump is a balance pass; whether a tuned row needs its own bump is that pass's question. |

**Numeric types.** Nothing new is computed here. The policy's own arithmetic is module 1's, and
`AiScoring.Score` is already `long`-widened and `checked` throughout with the reason stated —
*"an overflow throws rather than silently inverting a comparison, which is the hardest possible bug to
attribute in an AI (it would reliably pick the WORST option and look correct while doing it)"*
(`Actions/Ai/CandidateScorer.cs:88-96`, moved from SiegeAi.cs by CAI1.1). That property is inherited, and the switch is the moment it starts mattering
outside siege.

## Code style

- The version doc comment gains a paragraph, never a rewrite: v2, v4 and v5 are each still readable at
  `BattleModels.cs:270-284`, and a reader needs the whole chain to decode an old stamp.
- The golden ledger gains a dated paragraph in the same voice: what moved, what held, what was triaged
  first (`BattleGoldenTests.cs:18-76`).
- `decisions.md` row 44 is **amended in place with the date and the cause**, matching how every other
  row in that table records an overturn or a landing; the old reasoning stays readable, because it is
  the evidence for why the previous non-bump was correct.
- One commit, explicit paths, no `git add -A` (AGENTS.md).

## Testing strategy

**Re-blessed (exactly four, exactly once)**
- `StompHash`, `CloseHash`, `WipeHash`, `SeedSweepHash` (`BattleGoldenTests.cs:77-80`).

**Must hold, unchanged — the acceptance**
- ✅ `Golden_outcomes_hold_their_shapes` (`:215-224`).
- ✅ Every rate test in its locked band (PS-3).
- ✅ `Goldens_do_not_depend_on_the_platform`, `Goldens_do_not_depend_on_the_content_stamp` (`:180-212`).
- ✅ `DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests`
  green and **unchanged** (§4(e)).
- ✅ `gk-core/tools/ProvePredictor` both scopes under `1e-4`.
- ✅ Siege goldens unchanged — module 1 made siege byte-identical and this module does not touch it.

**New**
- ✅ `RulesetVersion` is 6, and the web-match log stamps 6 (`WebMatchService.cs:127`, `:199`).
- ✅ A battle resolved with no `intentSource` now runs the profiled policy, not `StubIntentSource` —
  the switch itself, asserted rather than inferred from a moved hash.
- ✅ `TimelineDispatch.Reselect`'s fallback reaches the same policy (module 4 owns the chain; this is
  the assertion that the switch did not miss the second site — `AUDIT.md` M5 is the reason it can).
- ✅ Every match logged after the bump carries a non-NULL `combat_ai_profile` — module 8's invariant,
  re-asserted here because this module is what makes it load-bearing.
- ✅ A pre-bump row (`RulesetVersion` 5, NULL profile) is refused by the sweep's existing version guard
  (`WebMatchService.cs:259-268`) rather than re-resolved under the new policy.

**Never**
- ❌ Assert what the new policy decides in a golden fixture ("the AI always targets `wave:0`"). No test
  pins an AI decision today and none should: S1-battle-core.md §"Replay/goldens" records that *"no test
  pins what the AI decides … only that a recorded decision replays identically"*, and that matches
  DESIGN-GATE §3 rule 7.
- ❌ Assert an expedition reward total. It is a reading that content and tuning move; the writeup
  reports the measured delta, the suite asserts the contract.

## Boundaries

**Always**
- Triage before blessing, and write down every failure that is not one of the allowed set.
- One commit, one cause, one re-bless.
- Land 8 and 9 first (§3).
- Measure the expedition delta; never estimate it.
- Amend `decisions.md:44` in the same commit.

**Ask first**
- **A moved outcome shape.** D1 approved a policy switch with a bump; it did not approve changing which
  golden fight is won. Stop and report with the writeup.
- **A moved rate golden.** PS-3 says a rate must not move; if one does, the cause is not the policy and
  must be found first.
- **A moved dominance baseline.** Verified not to be on the path; a movement means an unexpected
  coupling, not a re-bless.
- Tuning any profile row to make a golden land somewhere nicer. That is fitting the balance to the
  fixture.

**Never**
- Re-bless a golden that has not been explained (`BattleGoldenTests.cs:10-14`).
- Bump `RulesetVersion` without the writeup (`decisions.md:44`).
- Put a tuning publish, a weight change, the delve wiring or the lawn in this commit.
- Switch the default before the profile version can be recorded (§3 — the irreversible one).
- Let `Golden_outcomes_hold_their_shapes` be edited. It is the acceptance; editing it deletes the test
  that says the switch was a representation change.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** None is added. The switch changes which **policy** the engine is
   handed, and §3c places policy outside the engine. What it *does* touch is responsibility **19,
   determinism and seeded RNG streams**, because it moves the version that identifies a resolve — which
   is exactly why it is a `RulesetVersion` bump and not a quiet change.
2. **Decide or resolve (§3c)?** **Decide, entirely.** It changes what an actor tries to do; it changes
   nothing about what happens when it does. No damage math, no mitigation, no status, no shield, no
   death rule moves. That is why the predicted delta is bounded to target selection (§4(b)) — the
   resolver is untouched.
3. **Mechanism or loop?** **Neither is being added.** The mechanism (one scorer) is module 1's and
   already shipped by the time this lands; the loop (the engine pulls per turn, `S1-battle-core.md`
   §"Trigger") is unchanged. This module changes a **binding**: which policy the fallback chain ends at.
4. **Which existing implementation does it extend?** The router's fallback chain (module 4, owning
   `BasicAttack.cs:175-180` and `TimelineDispatch.cs:79-80`) and `BattleRunState`'s
   `DefaultAiIntentSource`, which already exists and is already set for siege. It adds no seam and no
   parameter to `BattleEngine.Resolve`.
5. **Does every mode get it?** Siege already had a profiled policy; battle and expedition get it here;
   delve gets it through module 13; the lawn through wave 4. So the answer is **yes, by the end of the
   program** — and this module is the one that ends the *"only siege is smart"* asymmetry
   (`AUDIT.md` B2: *"Only `SiegeAiIntentSource.cs:258` reads `AggressionOf`"*). No mode is left with a
   private default.
6. **Is it deterministic and seeded?** Yes, and the bump is how that is proven. Selection is argmax
   with an ordinal tie-break and reads no RNG (ideal §3 principle 4); the optional weighted pick draws
   from a battle-owned seeded stream; the personality offsets derive from `SeededRng.DeriveStream` over
   an instance id or `(match seed, actor key)` (ideal §6.2a). Cross-platform identity continues to rest
   on `BattleEnvironment.Stamp` (`BattleModels.cs:658-684`), since the inputs are doubles. And the
   profile version now rides the match stamp (module 8), which is what makes a replay of a v6 match
   reproducible at all.

## Success criteria

1. `RulesetVersion` is 6 with a v6 paragraph in its doc comment; `decisions.md:44` is amended in the
   same commit.
2. Battle and expedition auto-resolve run the profiled policy through the router's single fallback
   chain, at both `BasicAttack` and `Reselect`.
3. Exactly four golden constants are re-blessed, exactly once, with a ledger paragraph that records the
   triage.
4. `Golden_outcomes_hold_their_shapes` and every rate golden are green **and unedited**.
5. `docs/research/combat-ai/predicted-delta-rulesetversion-6.md` exists and contains (a) why the hashes
   move, (b) the bounded behavioural prediction with its fixture-shape evidence, (c) what held,
   (d) the **measured** expedition reward-rate delta per tier including the loyalty-threshold crossings,
   (e) the twin and baseline results.
6. `gk-core/tools/ProvePredictor` under `1e-4`; the dominance baseline re-run and recorded as unchanged.
7. Every match logged after the bump carries a non-NULL `combat_ai_profile`.
8. The full suite is green (`test-fast.ps1 -AllDefault`), and this is one of the three occasions
   AGENTS.md sanctions running it.

## Open questions

1. ~~**Does the expedition reward-rate measurement need a tuning response in the same program?**~~
   **CLOSED — owner ruling 2026-09-20: accept the drift.** A smarter auto-resolve earning more is the
   intended outcome, so there is no compensating expedition retune, in this commit or as a follow-up.
   The writeup still measures and records the per-tier delta, because the economy's owner needs the
   number even when nothing is being corrected. The record below is the reasoning that led there.

   **Does the expedition reward-rate measurement need a tuning response in the same program?** If the
   measured victory rate moves enough to change the idle economy's pace, the fix is an expedition
   tuning pass, not an AI change. Options: (a) report the delta and let the economy owner decide;
   (b) pre-emptively retune `SpecimenXpPerBattleWon` in the same commit. **Recommended default: (a)** —
   (b) is a second cause in a one-cause commit, and the economy's own owner has the calibration target.
   The writeup's per-tier table is the handoff.
2. **Whether `EngineVersion` should move too.** It has not moved through five ruleset bumps
   (`BattleGoldenTests.cs:18-76` records `RulesetVersion` 1→5 with `EngineVersion` referenced only for
   decodability). The policy is not the engine (§3c), so it should not. **Recommended default: no
   `EngineVersion` change**, stated in the writeup so the next reader does not wonder.
3. *(Cross-module note, outside this module's responsibility.)* The golden fixtures carry no
   `EquippedActionIds`, which is what bounds this module's predicted delta to target selection
   (§4(b)). That also means **the goldens cannot exercise the reserve floor, the waste guards, or
   action choice at all** — the very things D1 is switching on. A fixture with a real divergent
   multi-action loadout would be a genuinely stronger guard, and `decisions.md:44` names exactly that
   as its own bump trigger. Adding one is its own change with its own bump decision, and it belongs to
   whoever owns the battle golden set — named here so it is not attempted inside this commit.

## Design gate checklist (DESIGN-GATE §5)

```
[x] Subsystems identified: battle engine (determinism/RulesetVersion), goldens, balance analytics,
    expedition economy, replay identity, tunables.
[x] Session boundary: backlog-clean-up-20260920; this session wrote only the four
    docs/architecture/combat-ai/spec-*.md files, edited nothing else, ran no git mutation and no build.
[x] Read this session: combat-ai-map.md, combat-ai-ideal.md rev 3 (§1, §7, §10 D1/D2/D6), AUDIT.md
    (M2/M3/M4/M15, D1), S1-battle-core.md, battle-engine-ssot.md §2/§3c/§5, DESIGN-GATE §1 (battle,
    battle/turns, caps, tunables, economy rows) + §5, decisions.md rows 43-44, CLAUDE.md + AGENTS.md
    hard rules (verification boundary, one-cause commits, no watermarks).
[x] decisions.md checked: row 44 is the governing lock -- it REQUIRES this bump and a predicted-delta
    writeup, and its 2026-08-28 non-bump reasoning is quoted and shown to stop holding. Row 43's
    T9 precedent (bump only when a change is live and sweep-measurable) is honoured: this change IS
    live and measurable, which is the difference.
[x] Every factual claim cites file:line; every cited file was opened this session.
[~] audit-doc-citations.py reports no HIGH finding for this file -- run after writing; the one new
    file (the writeup) is marked "(new; does not exist yet)".
[x] Verified against CODE, not comments: WebMatchService passes no intentSource on any Resolve call;
    BattleGoldenTests.Actor sets no EquippedActionIds (:82-92), which is what bounds the predicted
    delta; ExpeditionEndpoints' three reward channels at :148-163 and :207; DominanceGuard/
    TerminationGuard use the economy-free Predict overload.
[x] Read the surrounding section of every rule quoted (decisions.md:44's whole row, not just the
    trigger sentence; BattleGoldenTests' header AND its five ledger paragraphs; AGENTS.md's
    "when the whole suite is actually the right call").
[~] Constraints tested, not assumed: the "goldens move" claim is GROUNDED (the v5 paragraph states
    the version stamp is in the hashed payload) but the measurement -- which goldens, by how much,
    and the expedition delta -- is the module's own deliverable and is specified as a procedure to
    RUN, explicitly before any constant is touched. This session ran no suite (spec-only lane).
[x] Nothing contradicts a §2 invariant. Invariant 12 is why no tuning publish rides along; 15 (SOLID)
    is satisfied because the switch changes a binding, not a mechanism; the no-hard-ceiling rule is
    untouched (no cap added).
[x] Corrections propagated: the ideal/map imply the dominance baseline moves with this switch. It is
    verified not to be on the path, so §4(e) restates it as a confirmation run with a stop-and-report
    if it DOES move, and spec-action-schedule-twin.md carries the same correction.
[x] No assertion pins a derived population, item total, generated text, or per-cycle outcome. The
    testing section explicitly bans pinning an AI decision and an expedition reward total, citing
    S1's own finding that no test pins what the AI decides.
[x] §2.16 event-refreshed cache: this module introduces none.
[x] No acceptance criterion silently fixes an ordering: the 8-before-14 and 9-before-14 orderings are
    stated AS orderings with their mechanism, and the triage-before-bless order is a procedure with
    its own numbered steps rather than an implied sequence.
[x] Produces/consumes no actor combat or derived magnitude itself; the policy it switches to reads
    Hub-composed numbers (ideal §3 principle 6) and folds nothing of its own.
[x] Extends no SOLID-violating path: by the time this lands there is one scorer (module 1) and one
    fallback chain (module 4); this module changes which policy that chain ends at.
[x] New rule has a guard: the bump is guarded by BattleGoldenTests (four constants + the shape and
    rate tests) and by the existing sweep version guard; no new repo-wide rule is added, so no
    enforcement-registry row is owed.
```
