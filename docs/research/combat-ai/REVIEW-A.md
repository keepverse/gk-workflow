# Independent review: combat-ai module specs (set A, 10 specs)

Reviewer: independent agent, read-only, standing in for owner approval per owner ruling.
Reviewed against: combat-ai-map.md (approved), combat-ai-ideal.md rev 3 (D1-D6 binding),
research/combat-ai/AUDIT.md, battle-engine-ssot.md §2/§3c/§5, CLAUDE.md hard rules, DESIGN-GATE §5.

Method: read all 10 specs plus the four reference docs in full. Dispatched 5 parallel read-only
locator agents to open and verify ~110 file:line citations across the 10 specs against the actual
source tree (at least 4+ per spec, most specs got 15-25 checked). Did cross-spec consistency analysis
by hand (types, signatures, dependency graph, tunable file shapes, byte-identity arguments).

## Citation audit result (summary)

Roughly 110 citations checked. The overwhelming majority are CONFIRMED exactly. The only misses are
trivial line-drift (a comment vs. the field/call it describes, a few lines to ~90 lines apart in the
same function/file) or one imprecise-but-substantively-correct phrasing. None of the ~110 checked
citations was fabricated or pointed at genuinely wrong content. This is an unusually high citation
accuracy rate for a 10-spec batch.

Misses found (all LOW severity, cosmetic fixes only):
- spec-profile-schema.md: `gk-core/src/FusionRpg.Server/Program.cs:240` for `SiegeTuningPolicy.Configure` -> the spec cited an unqualified Program.cs line number there (ambiguous — 42 files share that basename) and the call site has moved since; re-read 2026-09-22.
- spec-core-scorer.md: `DerivedComposer.cs:60-80` for the Cap-clamp logic -> the clamp itself is at
  `:83-100`; 60-80 is the calling loop (the claim is still true, just cites the wrong sub-range).
- spec-core-scorer.md / spec-profile-schema.md: `SiegeTuning.cs:333-375` for "parses into `Siege.AiTuning`"
  -> the actual `new Siege.AiTuning(...)` construction call is at `:432-439`; 333-375 is the parse body
  that feeds it. Not wrong, just describes the wrong sub-line for "constructs."
- spec-resolvable-here.md: "gate 3 calls `CostLedger.Check`" -> the call site invokes the
  `IAffordabilityCheck` interface method; `CostLedger` is the production implementation reached
  polymorphically, not named at the call site. Substance correct, phrasing imprecise.
- spec-delve-automated-wiring.md / spec-siege-loadout-wiring.md: `SupplyUse.cs:48-53` comment ("the one
  legal Downed -> Charging trigger...") is actually at line 39, ~10 lines outside the cited range.
- spec-delve-automated-wiring.md: `BattleModels.cs:84-160` for `BattleActorSetup` -> record starts at
  line 7; `PartyIndex` itself is at line 176, not inside the cited 157-160 (157-160 is a comment
  discussing it elsewhere).

None of these change any spec's argument or conclusion. No required-change item below is a citation fix
by itself; they are noted for completeness only.

## Verdicts

| Spec | Verdict |
|---|---|
| spec-core-scorer.md | APPROVE-WITH-CHANGES |
| spec-profile-schema.md | APPROVE-WITH-CHANGES |
| spec-ai-tiers-personality.md | APPROVE-WITH-CHANGES |
| spec-aggression-tier-map.md | **APPROVE** |
| spec-intent-router.md | APPROVE-WITH-CHANGES |
| spec-resolvable-here.md | **APPROVE** |
| spec-decision-perf.md | **APPROVE** |
| spec-stance-wiring.md | APPROVE-WITH-CHANGES |
| spec-siege-loadout-wiring.md | **APPROVE** |
| spec-delve-automated-wiring.md | APPROVE-WITH-CHANGES |

All 10 specs stay inside their declared module responsibility and respect the map's dependency
directions exactly (I checked every spec's "Depends on" line against the map's table 1:1 — all ten
match). All 10 correctly refuse a second mechanism/private estimator/parallel composer, and every
"structural, not a cap" claim is commented as CLAUDE.md requires. Tests are contract-shaped throughout;
I found zero instances of a population count or generated-text assertion smuggled into a "Testing
strategy" section. The "byte-identical" claims are argued from code (default values = today's
singleton/behaviour, trailing optional parameters, `WhenWritingDefault` suppression, etc.), not just
asserted — every one I checked cites the specific mechanism that makes it true, and every spec is
honest that it did not (because it could not) run a build to confirm it, naming that gap explicitly in
its own DESIGN-GATE checklist. That discipline is consistent across all 10 and is the strongest thing
about this batch.

## Required changes (numbered)

1. **[stance-wiring, blocking] `AiTuning` "after" record is wrong — it un-migrates ten fields
   `profile-schema` already removed.** spec-stance-wiring.md §"The `AiTuning` shrink" shows, as the
   "after" state of `SiegeAi.cs:60-64`:
   ```csharp
   public sealed record AiTuning(
       int WeightHitChance, int WeightObjective, int WeightKill, int WeightLowHp, int WeightCannotCounter,
       int WeightRound, int WeightRisk,
       long RetargetLatencyTicks, int AggressionRange, int MaxCandidatesScored,
       int ObjectiveReferenceDistanceCells, int ThreatRadiusCells);
   ```
   twelve fields (all 7 weights + RetargetLatencyTicks + AggressionRange + MaxCandidatesScored, plus the
   2 geometry fields). But `spec-profile-schema.md` §6 "H7" explicitly states, and stance-wiring's own
   prose quotes: *"`SiegeTuningLoader.Parse` stops reading the ten (`SiegeTuning.cs:333-366`), and
   `Siege.AiTuning` (`SiegeAi.cs:60-64`) **narrows to the two geometry values plus the two dead ones**"*
   — i.e. **4** fields after module 2's commit. Stance-wiring (module 11, which depends on module 2 and
   runs after it) removes only the 2 dead ones from that 4-field record, so its own "after" should have
   **2** fields (`ObjectiveReferenceDistanceCells`, `ThreatRadiusCells`), not 12. This also breaks
   stance-wiring's Success Criterion 4 ("`AiTuning` has twelve members") and its
   `Ai_tuning_names_exactly_the_channels_the_scorer_reads` test, and the `ContractTuningTestBootstrap`
   diff description ("loses two arguments" should be "loses two arguments **from a four-argument
   constructor**"). **Fix:** rewrite §"The `AiTuning` shrink" to start from module 2's already-narrowed
   4-field record, not from the original 14-field one; correct Success Criterion 4 to "two members"; fix
   the bootstrap-diff description.

2. **[intent-router / delve-automated-wiring, blocking] `IntentRouter.Compose(...)` is invoked by
   module 13 but never defined by module 4, and its signature doesn't match module 4's constructor.**
   spec-delve-automated-wiring.md §1 writes:
   ```csharp
   DefaultAiIntentSource = IntentRouter.Compose(steered, automated, steeredKeys);   // module 4
   ```
   spec-intent-router.md defines `IntentRouter` with only a **constructor**:
   `IntentRouter(IIntentSource policy, IIntentSource fallback, IIntentSource? steered = null,
   IReadOnlySet<string>? steeredKeys = null, ...)` — no static `Compose` method anywhere, and even the
   positional order differs (module 4: policy, fallback, steered; module 13's call: steered, automated,
   steeredKeys — omits `fallback` entirely). A builder implementing module 13 cannot compile this line
   against module 4's spec as written. **Fix:** either module 4 adds a `Compose` factory with a stated
   signature that covers module 13's call (and states what `fallback` defaults to when omitted), or
   module 13's code sample is corrected to use the actual constructor. This is the same seam module 13's
   own Open Question 1 already flags as unresolved ("`steered` must be a factory, not a built source, for
   the delve") — that question should be resolved in module 4's spec, not left as a note in module 13's.

3. **[core-scorer / ai-tiers-personality / delve-automated-wiring, blocking — missing signature] No
   module defines the concrete `IIntentSource` class that assembles the reusable core (TargetStage +
   ActionStage + tier/personality) into a callable policy for a non-siege, non-trivial profile.**
   spec-delve-automated-wiring.md §1 calls `CoreIntentPolicy.Create(this, Cooldowns, Stance, CostLedger,
   profileId, retarget: new RetargetLedger(), trace: trace) // module 1 + 3's type` — but neither
   spec-core-scorer.md (module 1: ships `CandidateScorer`, `TargetStage`, `ActionStage`,
   `ReserveFloorAffordability`, `RetargetLedger` — building blocks, not an `IIntentSource`) nor
   spec-ai-tiers-personality.md (module 3: ships `AiTierResolver`, `AiPersonalityFactory`,
   `AiPersonalityApply` — pure functions, not an `IIntentSource`) ever names or specs a
   `CoreIntentPolicy` type. Siege's own consumption is fine (module 1 keeps `SiegeAiIntentSource` as
   "consumer #1," so siege needs no new wrapper), but battle/expedition (module 14, not in this batch)
   and delve (module 13, in this batch) both need a *generic scored policy* class that does not yet
   exist in any reviewed spec. **Fix:** module 1 or module 3 must name and spec this type (constructor
   signature, what it does with `profileId` to resolve a `CombatAiProfile`, how it walks
   `CombatAiProfile.Rows` — see item 4) — or the map/one of the specs must explicitly assign this as a
   named open task before module 13/14 can be built as specced.

4. **[core-scorer / profile-schema, non-blocking but real — missing glue] No spec shows the code that
   walks `CombatAiProfile.Rows` in rank order, evaluates `AiRowCondition`/`AiCensusCondition`, and
   selects the `TargetSelector`/`AiActionFilter` to hand to `TargetStage`/`ActionStage`.**
   spec-core-scorer.md §5 explicitly punts this: *"Which **rank row** it must come from is module 2's
   profile; this module only guarantees one pass over held actions."* spec-profile-schema.md's own spec
   is the data shape and the *place x role* profile-selection chain, but never describes iterating
   `Rows` by rank/condition to pick a row. This is the row-selection algorithm implied by the ideal's
   FF12-gambit framing ("first match wins") and by `AiProfileRow`'s own doc ("Rank is the row's INDEX...
   lower wins"), and it is currently unowned by any of the ten specs. **Fix:** name the owning module
   (most naturally module 1, since it already owns `TargetStage`/`ActionStage`) and add the
   row-evaluation loop's shape and its interaction with tier (item 5 below).

5. **[core-scorer / ai-tiers-personality, non-blocking but real] Module 3 assumes module 1's
   `ActionStage` has a tier-conditioned branch that module 1's own spec never describes.**
   spec-ai-tiers-personality.md §2's table states the performance tier's action stage is
   "gates -> resolvable-here -> **reserve floor**, first survivor wins" (waste guards explicitly
   skipped, because they "need a live-count census... exactly the work the performance tier exists not
   to do"). spec-core-scorer.md §5 describes `ActionStage` as one fixed sequence — gates,
   resolvable-here, reserve floor, **waste guards** — with no tier parameter, no flag, and no branch
   documented anywhere. If waste guards are meant to be skipped by *authoring* (guard values at their
   off/identity thresholds) rather than by *code branching*, module 3's claim that this "costs nothing
   extra" and "is exactly the work performance exists not to do" is inconsistent — evaluating a
   guard's threshold still requires the live-count census it says performance tier avoids. **Fix:**
   module 1 must add the tier-gated branch to `ActionStage`'s spec (a bool parameter or an
   `AiTier`-driven flag), or module 3 must restate that performance tier profiles are simply authored
   with guards at identity and drop the "computes no live-count census" framing.

6. **[profile-schema, non-blocking] `CombatAiTuning` (the type `CombatAiTuningLoader.Parse` returns) is
   referenced throughout but never given a field list.** The spec shows `CombatAiProfile` in full, and
   shows `CombatAiTuningLoader.Parse(string json) -> CombatAiTuning` and
   `CombatAiProfilePolicy.Configure(CombatAiTuning tuning)`, but the root `CombatAiTuning` record itself
   (presumably `schemaVersion`, `version`, a `Dictionary<string, CombatAiProfile> Profiles`, and — per
   item 7 below — a `router` block) is never defined. **Fix:** add the record.

7. **[profile-schema / intent-router, non-blocking] `router.orderTimeoutTicks` and
   `router.reactionsPerRoundExpected` (spec-intent-router.md's Tunables table) assume a top-level
   `router` block in `combat-ai.v1.json`, but spec-profile-schema.md's own JSON example and record
   definitions (§1-2, the Tunables section's example file) never show such a block.** **Fix:** module 2
   should add the `router` shape to its schema (or module 4 states which existing block it lives under).

8. **[profile-schema, non-blocking, internal] The stated ten-key H7 migration path is inconsistent with
   its own tool constraint.** §"Tunables" states `publish.py --drop-key` "refuses more than one key per
   invocation" and "writes `v{n+1}`" per call — which, run ten times to drop ten keys from
   `siege.v1.json`, would produce `v2` through `v11`, not stop at the single `siege.v2.json` the rest of
   the spec (project structure table, §6 H7, boundaries, success criteria) treats as the migration's
   result. spec-stance-wiring.md then builds `siege.v3.json` "from module 2's v2," compounding the same
   assumption. **Fix:** either state that `--drop-key` accepts multiple flags in one invocation (one
   version bump, multiple reviewable diff lines), or renumber the downstream version references
   consistently (module 2's result is `v11`, module 11 produces `v12`, etc.).

9. **[intent-router, non-blocking] The `poise` reserve-floor contract module 4 "publishes to
   profile-schema" (`max(profileFloor, expectedReactionSpend)`) has no stated implementer.**
   `profile-schema`'s `AiReserveFloor(string ResourceId, int FloorMilliOfMax)` is a flat per-resource
   value; `core-scorer`'s `ReserveFloorAffordability` decorator (module 1) reads that flat value with no
   mention of combining it with `router.reactionsPerRoundExpected` × `PoiseSpend`. **Fix:** name which
   module computes the max — most naturally module 1's decorator, taking the router's exposed
   `PoiseSpend` read as a constructor input — or fold it into profile-schema's authored value directly
   and drop the runtime max().

## Cross-spec contradictions (the highest-value check, summarized)

- **#1 above** (stance-wiring vs profile-schema) is the clearest same-type-two-ways contradiction in the
  batch: the same declaration site (`SiegeAi.cs:60-64`, the `AiTuning` record) is given two different
  "after" field counts by two specs in direct dependency order (11 depends on 2).
- **#2 above** (intent-router vs delve-automated-wiring) is an incompatible-signature contradiction: a
  static factory method invoked by one spec does not exist, under that name or shape, in the spec that
  is supposed to define it.
- **#3 above** is a duplicate-ownership gap in the opposite direction — a type two specs jointly imply
  exists ("module 1 + 3's type") that neither actually declares.
- No other same-key/same-type contradictions were found. Every other cross-module reference I checked
  (aggression sum in module 3 vs module 6, dependency arrows vs the map, tunable key ownership in
  module 2's migration table vs module 11's disposition of the two dead keys, the `EquippedActionIds`
  null-vs-empty convention shared by siege-loadout-wiring and referenced correctly elsewhere) is
  internally consistent and, where two specs discuss the same fact, they agree.

## Optional suggestions (not required)

- Several specs (`intent-router`, `resolvable-here`, `decision-perf`) leave their DESIGN-GATE checklist
  line `python scripts/audit-doc-citations.py --scope <this file>` as `[ ]` ("run after writing; result
  reported in the lane's final message"), while the other seven mark it `[x]` with a stated 0-HIGH
  result. Worth running and closing out before these three are called done, for consistency with the
  rest of the batch (not because the citations I checked found a problem — they didn't).
- `spec-core-scorer.md` Open Question 1 ("does `StubIntentSource` survive as a class") and the
  `CoreIntentPolicy` gap (item 3) are closely related and would be cheaper to resolve together in one
  pass over module 1 than separately.
