# Todo: `combat-ai`

**Plan:** [combat-ai-plan.md](combat-ai-plan.md) ·
**Map:** [../docs/architecture/combat-ai-map.md](../docs/architecture/combat-ai-map.md) ·
**Specs:** `docs/architecture/combat-ai/spec-<module-id>.md` ·
**Handoff:** [combat-ai-handoff.md](combat-ai-handoff.md) — ⚠ **its §1 state table is STALE: it reads "Build | Not started. Nothing exists.", measured false on 2026-09-22 and held by `CAI-handoff-1`. Read the rows below, not that table.** ·
**Evidence:** [../docs/research/combat-ai/](../docs/research/combat-ai/)

**Status:** written 2026-09-20; **the build is well under way — re-read 2026-09-23 (lane `cai3`, session `combat-ai-3`).** Counted as TASK BLOCKS, never checkbox lines (the repo's own metric — a shipped task carries 6-10 permanently-unchecked acceptance boxes): **46 done, 25 open** by `grep -c '^- \[x\] \*\*'` and `'^- \[ \] \*\*'`. Waves 1-2 landed; wave 3 partly (`CAI3.1` closed); wave 4's Core halves landed with each row naming its Injector/Contracts/Server/`web` remainder; wave 5 waits on a live probe. **Four measured facts that replace the handoff's §1:** `gk-core/src/FusionRpg.Core/Actions/Ai/` holds 22 files, `gk-core/data/tuning/combat-ai.v1.json` and `.v2.json` both exist, `grep -c remove-key gk-core/tools/tuning/publish.py` is 4, and `PerfProbe.SectionCount` is 27. Prefix `CAI`. A cross-program reference is written `<prefix><id>` (for example `BCU0.1`, `LW…`).

**Every task is one commit** (code + tests + evidence). **Every task states its golden answer.** Unless
the task says otherwise, that answer is *byte-identical*, and the acceptance includes running
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` and **stating what
it printed** — a byte-identity claim that was not run is an opinion.

Default verification, with the lane's own session record:
`.\scripts\verify-change.ps1 -Paths <added/modified paths> -Session <lane session id>`.

---

## Wave 1 — the shared core (Core only; battle, delve and siege unchanged in behaviour)

### `core-scorer` (module 1)

- [x] **CAI1.1 — Move the scorer: `CandidateScorer` + selection** · L · deps: — · *(spec: core-scorer §… "the scorer")*
  - Acceptance:
    - `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs` holds the additive score, the seven-member
      `ScoreTerm` vocabulary, `ScoreBreakdown`, argmax with ordinal tie-break, and the opt-in seeded
      weighted pick (`keepPctMilli`, `rngStreamName`).
    - `Battle/Siege/SiegeAi.cs` holds **no second copy** of the additive score; siege constructs its
      weights exactly as today from `siege.v1.json` through `SiegeTuningLoader`.
    - `Score_matches_the_shipped_siege_weights_term_for_term` passes — a migration-fidelity assertion
      of specific numbers, legitimate because "the same arithmetic" *is* the claim, and the test says so.
    - `Overflow_throws_rather_than_inverting_a_comparison`; `Total_is_Score_not_a_resum`;
      `KeepPct_1000_and_Argmax_reduce_to_the_shipped_ChooseTarget`;
      `Weighted_pick_is_reproducible_from_the_same_stream_name_and_seed`.
    - `SiegeAiTests`, `SiegeAiIntentSourceTests`, `SiegeAiLiveWiringTests` pass **unedited**.
  - Golden: byte-identical. Run the filter and state the result.
  - Verify: verify-change; `python gk-core/scripts/audit-overflow.py --targets A3` (no new finding).
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs` (new), `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs`, `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CandidateScorerTests.cs` (new).
- [x] **CAI1.2 — `TargetStage`: cap before any per-candidate work** · M · deps: CAI1.1
  - Acceptance:
    - `Cap_before_work_selects_the_same_candidate_as_cap_after_work` — 40 live enemies, cap 32, same
      chosen key and same winning breakdown as the shipped order. **This is the identity proof.**
    - `Phase_A_filters_run_in_view_order` (self, same-side, unreadable dropped in `LiveActorKeys`
      order, so truncation is order-stable).
    - `Per_candidate_inputs_are_computed_only_for_the_capped_set` — a counting `TryBuildCandidate`
      fake invoked at most `MaxCandidatesScored` times. **Counted, never timed.**
  - Golden: byte-identical.
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/TargetStage.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/TargetStageCapTests.cs` (new), siege's consumer.
- [x] **CAI1.3 — `ActionStage` + `ReserveFloorAffordability`** · M · deps: CAI1.1
  - Acceptance:
    - One pass over held actions reaching `UsabilityEvaluator`, the resolvable-here seam (default
      admits everything), the reserve-floor decorator and the three waste guards — each at its
      identity default.
    - Gate order unchanged: an action both on cooldown and unaffordable reports `OnCooldown`.
    - `runWasteGuards_false_skips_the_census_entirely` — a counting fake for the live-count read is
      **never invoked** (this is what distinguishes the branch from "thresholds authored off").
    - `ReserveFloorAffordability` computes `max(authored poise floor, PoiseSpend × reactionsPerRound)`
      for the `poise` id **only**; both reaction arguments at `0` is byte-identical, and a second
      resource with a floor is asserted unchanged in the same test.
  - Golden: byte-identical.
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/ActionStage.cs`, `ReserveFloorAffordability.cs` (both new), `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/ActionStageTests.cs` (new).
- [x] **CAI1.4 — `RetargetLedger`: anti-repeat moved and widened** · S · deps: CAI1.1
  - Acceptance: the type moves out of `SiegeAiIntentSource.cs:316-351`; `Latency_zero_holds_nothing`,
    `Commitment_bonus_zero_is_byte_identical`, `Repeat_decay_1000_is_byte_identical`,
    `Ledger_state_is_battle_scoped`. It is the **only** anti-repeat mechanism in the repo.
  - Golden: byte-identical.
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/RetargetLedger.cs` (new), `SiegeAiIntentSource.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/RetargetLedgerTests.cs` (new).
- [x] **CAI1.5 — Kill/value read the real `baseOverlayDamage` at `EffectiveRungOf`** · S · deps: CAI1.1–1.4 · **moves siege behaviour**
  - Acceptance: `SiegeAiIntentSource.cs:214`'s omission no longer exists; kill and value read
    `ActionBaseDerivation` at `EffectiveRungOf` through the one estimator.
  - Golden: **one cause, siege target choice only.** `BattleGoldenTests` and
    `ExpeditionResolverTests` unmoved; `RulesetVersion` stays 5; a predicted-delta writeup names every
    moved siege test. If a **battle** hash moves, stop and report — that is not this cause.
  - Files: `SiegeAiIntentSource.cs`, `docs/research/combat-ai/predicted-delta-kill-estimate.md` (new).

### `profile-schema` (module 2)

- [x] **CAI1.6 — Vocabularies, records, parser, row selector (no file, no reader switch)** · L · deps: CAI1.1
  - Acceptance:
    - Six closed vocabularies in `AiVocabulary.cs`; an unknown string throws naming **the value and
      its key**; each member count pinned **with its reason stated in the test**
      (`TargetSelector_has_eight_members`, `AiTier_has_two`, `AiPlace_has_four`, `AiRole_has_four`,
      `AiRowCondition_has_six`, `AiCensusCondition_has_five`, `PersonalityAxis_has_four`).
    - `CombatAiTuning` and `AiRouterBlock` declared; a file missing `router` or `*/default` is rejected
      **at parse**; a profile whose last row is conditional is rejected at parse.
    - **`AiTriggerBlock` has exactly three fields** — `SwingsN`, `TicksT`, `PostCastLockL`. Not five.
      (Plan correction 2: module 19 classifies the per-frame budget and the token pool as code
      `const`s, so a schema field for them is dead config.)
    - `AiRowSelector.TryPick` is the only rank walk in the repo: first match wins,
      `Census_facts_are_read_from_the_supplied_struct_and_never_recounted` (counted fake invoked once
      for an eight-row profile), empty list returns `false` and never throws.
    - `Core_reads_no_file` — the loader's only input is a string.
    - Key resolution `place/role` → `place/default` → `*/role` → `*/default`, each step exercised.
  - Golden: byte-identical (nothing constructs it yet).
  - Verify: verify-change; `python gk-core/scripts/audit-magic-numbers.py --summary` gains no row for `Actions/Ai/`.
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/{AiVocabulary,CombatAiProfile,CombatAiTuningLoader,CombatAiProfilePolicy,AiRowSelector}.cs` (all new), `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/{CombatAiTuningTests,AiRowSelectorTests}.cs` (new).
- [x] **CAI1.7 — `publish.py --remove-key`** · M · deps: — *(may run any time; CAI1.8 needs it)* — **verify-and-test-only** (already built by solid-enforcement, see evidence for the named `--reason` gap)
  - Acceptance: removes exactly one existing key; **refuses** an unresolvable path (never a silent
    no-op); repeatable within one invocation (`action="append"`); **one invocation writes exactly one
    `v{n+1}`**; requires `--reason "<text>"`, recorded in `_meta` beside each removed path.
    A test asserts the batch property directly: N removals in one invocation produce **one** new file.
  - Verify: `python -m pytest gk-core/tools/tuning/test_publish_remove_key.py -q`; verify-change.
  - Files: `gk-core/tools/tuning/publish.py`, `gk-core/tools/tuning/test_publish_remove_key.py` (new).
- [x] **CAI1.8 — Publish `combat-ai.v1.json` + `siege.v2.json` and switch every reader (H7)** · L · deps: CAI1.6, CAI1.7
  - Acceptance:
    - `gk-core/data/tuning/combat-ai.v1.json` exists with a required `*/default` root, a `siege/default` row
      carrying the ten migrated values unchanged (70/50/15/10/10/1/120/2/32/0), the identity defaults
      (argmax, `keepPctMilli` 1000, no reserves, all guards off, all anti-repeat off, all personality
      bounds 0, `tierByActorClass` unique→smart / general→performance,
      `profiles["siege/default"].tierOverride = "smart"`), and the required top-level `router` block
      (`orderTimeoutTicks` 5000, `reactionsPerRoundExpected` 1000).
    - `siege.v2.json` produced by **one** `--remove-key ×10` invocation — not ten publishes, not a
      hand edit. It still carries the two geometry keys **and** the two dead keys (deleting those is
      CAI3.1's decision, and a test asserting they are gone would assert a decision nobody made).
    - `SiegeKeyMigrationTests`: `The_ten_migrated_values_match_siege_v1`,
      `Siege_v2_no_longer_carries_the_ten`, `Siege_v2_still_carries_the_two_geometry_keys`,
      `Siege_v2_still_carries_the_two_dead_keys`, `Profile_defaults_are_the_identity_set`.
    - `SiegeTuningLoader`, `Siege.AiTuning`, `BattleRunState:627-630` and **both hosts**
      (`Server/Program.cs` beside `SiegeTuningPolicy.Configure`, `Injector/Host/RpgHost.cs`) switch in
      **this same commit**.
  - Golden: byte-identical, **and that is the acceptance** — it is a relocation, not a balance pass.
    If a golden moves, this task is wrong.
  - Files: `gk-core/data/tuning/combat-ai.v1.json` (new), `gk-core/data/tuning/siege.v2.json` (new), `SiegeTuning.cs`, `BattleRunState.cs`, `Server/Program.cs`, `Injector/Host/RpgHost.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/SiegeKeyMigrationTests.cs` (new).

### `ai-tiers-personality` (module 3)

- [x] **CAI1.9 — Tier, personality, and `CoreIntentPolicy`** · L · deps: CAI1.1, CAI1.8
  - Acceptance:
    - `AiTierResolver.For(profile, actorClass)` is the only place a tier is decided and takes **no
      difficulty input** — asserted as a signature test, not promised in prose.
    - Unwired class resolver yields `Unique`; `AiActorClass_has_two_members`, `AiTier_has_two_members`.
    - Performance tier **computes no candidate inputs** (counting fake never invoked) and still runs
      all six gates, the resolvable-here filter and the reserve floor.
    - A unique's personality is reproducible from its **instance id** alone, across matches and
      constructions, with nothing stored; a general's from `(match seed, actor key)`.
    - Every axis draws unconditionally in declaration order:
      `Changing_one_axis_bound_does_not_shift_another_axis` passes.
    - `All_bounds_zero_is_byte_identical` — the applied profile equals the authored profile field for
      field.
    - `CoreIntentPolicy` is the **only** assembling scored `IIntentSource`; runs the seven steps in
      order (recording fakes assert the sequence, not the numbers); resolves the profile **once per
      actor** and the census **once per decision** (both counted); holds no scoring arithmetic of its
      own, proven by a source scan for a comparison of two candidates' scores.
    - **Nothing in production constructs it in this commit** — CAI3.5 is its first caller.
  - Golden: byte-identical (bounds 0, resolver unwired, `siege/default` explicitly `smart`).
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/{AiTierResolver,AiPersonality,AiPersonalityApply,CoreIntentPolicy}.cs` (new), `AiVocabulary.cs` (one enum), `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/{AiTierResolverTests,AiPersonalityTests,CoreIntentPolicyTests}.cs` (new).

### `intent-router` (module 4)

- [x] **CAI1.10 — The router, cause A: one chain, two routers deleted** · L · deps: CAI1.1
  - Acceptance:
    - `IntentRouter` exists; `RaidIntentSource.cs` and `SiegeIntentSource` are **deleted**; every
      former caller constructs the router.
    - `IntentRouter.Compose` is the **only** construction entry point;
      `Compose_invokes_steeredSourceFor_exactly_once_with_the_policy_it_was_given`;
      `Compose_with_a_null_fallback_returns_None_rather_than_inventing_a_stub`;
      `A_router_built_through_Compose_and_one_built_through_the_constructor_resolve_identically`.
    - `The_fallback_chain_is_order_injected_then_steered_then_policy_then_default` — the four-step
      chain pinned as a closed vocabulary the code owns.
    - `Constructing_a_router_with_no_decorators_and_no_queue_reproduces_the_shipped_chain` — the
      byte-identity harness.
    - `RetargetFor_keeps_the_committed_action_and_changes_only_the_target`;
      `The_router_consults_no_policy_for_a_reaction` (fake policy, zero calls across a battle whose
      reaction lane fires).
    - Grep finds **no second** `?? new StubIntentSource(` in `src/`.
  - Golden: byte-identical. Run `BattleGoldenTests` + `ExpeditionResolverTests` and quote the output in
    the commit body.
  - Verify: verify-change; `python gk-core/scripts/guard-battle-responsibility.py`; `.\scripts\guard-actor-hub.ps1`.
  - Files: `gk-core/src/FusionRpg.Core/Actions/{IntentRouter,IIntentDecorator,DirectOrder}.cs` (new), `Battle/BasicAttack.cs`, `Battle/TimelineDispatch.cs`, `Battle/BattleRunState.cs`, deletions, `gk-core/tests/FusionRpg.Core.Tests/Actions/IntentRouterTests.cs` (new).
- [x] **CAI1.11 — The router, cause B: the reselect fallback, trait decorators on every policy** · M · deps: CAI1.10 · **moves siege behaviour**
  - Acceptance:
    - `Reselect_and_declare_resolve_the_same_source_for_the_same_actor` — **M5 as a test**; it fails
      against today's `TimelineDispatch.cs:79-80`, which omits `state.DefaultAiIntentSource`.
    - `Every_policy_sees_the_bloodthirsty_view_not_only_the_fallback` (a fake policy records the view
      type it was handed).
    - `A_loyal_redirect_is_applied_once_on_each_side_and_the_scorer_reads_the_redirected_target`.
  - Golden: **one cause.** A predicted-delta note names every moved siege test. Battle hashes and
    `RulesetVersion` unmoved — `decisions.md:44`'s named trigger is CAI3.6's cause, not this one.
  - Files: `TimelineDispatch.cs`, `BasicAttack.cs`, `IntentRouter.cs`, `docs/research/combat-ai/predicted-delta-router-cause-b.md` (new).

### `resolvable-here` (module 5) · `aggression-tier-map` (6) · `decision-perf` (7)

- [x] **CAI1.12 — `resolvable-here`: the per-place executor allowlist** · M · deps: CAI1.1 — **DONE, both halves.** Core/battle half landed in the combat-ai lane (`c3bb0ba2`); injector/lawn half in session `cai-sink` — `IDeclaresExecution` now sits at its spec'd home (`Effects/EffectModels.cs`, no second copy), `InjectorEffectActionSink` declares `Executes`, and the lawn anti-drift source scan is built. One acceptance line stands as the manager-ruled **erratum substitution** (see that bullet below); `tasks/evidence-fragments/CAI1.12.md`
  **ERRATUM GRANTED** on `No_file_under_data_tuning_names_an_opcode`: the literal scan is unverifiable
  (tuning legitimately names action/atom ids), so the substituted
  `No_file_under_data_tuning_authors_a_place_allowlist` stands as that criterion's intent — not re-opened.
  This row's injector/lawn half was handed off to `cai-sink` and landed there; the lane's row is kept as
  the newer of the two and the hand-off paragraph is folded into it by the manager at merge.
  **CLOSED at lane tip `0f77d670`** (lane `combat-ai-2`): no code was owed — both halves are present
  (`EffectModels.cs:139` is the one `IDeclaresExecution`; battle's table is `BattleEffects.cs`, the
  lawn's `InjectorEffectActionSink.cs:1035`), and the whole suite is **13 passed / 0 failed** including
  the erratum substitution.
  - Acceptance:
    - `BattleEffectSink.Execute` becomes a dispatch table and `ExecutedActions` returns **that table's
      keys** — grep finds no second list of battle's opcodes.
      `Battles_declared_allowlist_equals_its_dispatch_table` is the anti-drift contract.
    - The injector sink declares its set;
      `The_lawn_sinks_declared_allowlist_matches_every_EffectActions_constant_its_dispatch_references`.
    - `Every_trigger_battle_raises_appears_in_its_declared_trigger_set` (source scan over
      `Battle/**` for `Trigger = AtomTriggers.`).
    - `Of` returns `Full` for a zero-unit action, `Inert` for a battle-inert status-only support
      action, `Partial` for an attack with an inert rider; `Veto` is true only for
      `Inert × {Support, Status, Defense}` and **never** for a null category (fail-open).
    - `A_place_profile_is_built_from_the_sink_and_never_from_a_profile_row` — `ResolvableHere.cs`
      references no tuning/profile type. A sink that does not declare is refused at construction.
    - `The_filter_allocates_zero_bytes_across_two_hundred_candidate_actions`;
      `A_footprint_is_computed_once_per_battle_and_not_per_decision`.
    - No file under `gk-core/data/tuning/**` names an opcode — **erratum granted**: the literal form cannot
      hold (`gk-core/data/tuning/status-catalog.v1.json` names `"ModifyStat"` as a status payload kind), so
      the substituted `No_file_under_data_tuning_authors_a_place_allowlist` stands and is green.
  - Golden: byte-identical (no policy consumes the filter until CAI3.6). Run the battle status/stat/
    structure apply suites too, and report.
  - Verify: verify-change; `guard-battle-responsibility.py`; `guard-secondary-no-unity.ps1`.
  - Files: `gk-core/src/FusionRpg.Core/Actions/ResolvableHere.cs` (new), `Effects/EffectModels.cs`, `Battle/BattleEffects.cs`, `Battle/BattleRunState.cs`, `Injector/Effects/InjectorEffectActionSink.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/ResolvableHereTests.cs` (new).
- [x] **CAI1.13 — `aggression-tier-map`: the throw becomes a saturating clamp** · S · deps: CAI1.1 · **land before any content writes `ai.aggression`**
  - Acceptance:
    - `EffectiveTier` no longer throws for any legal `aggression`; it saturates to `±aggressionRange`
      and reports a signed `saturatedBy`. `aggressionRange <= 0` **still throws**, and the comment says
      why the two cases differ.
    - `Inside_the_range_is_unchanged` (the byte-identity proof: every production implementor returns 0
      today, `BattleRunState.cs:924-931`), `Outside_the_range_saturates_to_the_edge`,
      `SaturatedBy_reports_the_signed_overshoot`,
      `A_stacked_channel_plus_a_personality_offset_saturates_as_a_sum`,
      `Non_positive_range_still_throws`, `Tier_vocabulary_width_is_two_range_plus_one` (a pinned
      literal **with its reason in the test** — the tier set is a closed vocabulary).
    - `ai.aggression` stays `FlatSum` with no `Cap`.
    - The two stale comments (`DerivedStatChannels.cs:568-577`,
      `DerivedStatRegistry.cs:289-294`) no longer claim the throw is the bound, **in this same commit**.
    - No siege test edited **except** one that asserts the removed throw, called out in the commit body.
  - Golden: byte-identical, provably — nothing reaches the throw today.
  - Files: `Actions/Ai/CandidateScorer.cs`, `Stats/Derived/DerivedStatChannels.cs`, `DerivedStatRegistry.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AggressionTierMapTests.cs` (new).
- [x] **CAI1.14 — `decision-perf`: five allocation sites, the O(n²) cap, `ai.decide`** · L · deps: CAI1.1, CAI1.10 — **DONE in-fence; two acceptance lines closed by ERRATUM REQUEST (below).**
  In-fence and landed: **site 1** in full (`CostLedger.RowsFor` precomputed; `TryPay`'s reusable scratch
  + re-entry guard; `Check` de-`foreach`ed — its own allocation is now asserted to be exactly 0 against
  the pool reads it makes), **site 2** (the `BloodthirstyDecorator` owns one `BloodthirstyView` for the
  battle and `Refill`s its retained list, `BasicAttack.cs:543-566,607-633`), **site 3** in full
  (`TargetStage.BuildCappedInto` into a caller-owned pair; `SiegeAiIntentSource` and `CoreIntentPolicy`
  each own one, four per-decision delegates bound once, re-entry throws), and **site 4** in full
  (`ChooseTargetInto` + `SelectionScratch`; the pre-CAI1.14 body allocated `Take`/`inTier`/`survivors`/
  `cut` per decision), plus `TopThreeInto`/`FormatTopThree`, `The_cap_counts_only_candidates_that_passed_the_skip_filters`
  and `No_LINQ_remains_on_a_decision_path` (a focused source scan). The row's own Verify line is green:
  verify-change, `audit-overflow.py --targets A3`, `guard-battle-responsibility.py`, plus
  `guard-actor-hub.ps1` and `guard-doc-citations.ps1 -Strict`.
  **ERRATUM REQUESTED** on two lines the lane's file fence excludes, both proven and filed rather than
  guessed: site 5 (interned channel ids — `Stats/Derived/**`, where the single reader on the pool path
  also lives, so it cannot be relocated into the fence) and `PerfSection.AiDecide = 25` /
  `SectionCount = 26` / `"ai.decide"` (`Diagnostics/PerfProbe.cs`). Consequently
  `Resolving_a_pool_allocates_no_channel_id_string`, `The_interned_channel_id_equals_the_formatted_one_for_every_registered_resource`
  and the five per-policy zero-byte ROUND tests are NOT written — every round crosses the uninterned
  channel id. **Also NOT proved:** site 2's allocation is not byte-measured (the decorator is reachable
  only through a live `BattleRunState`, which no test constructs), and the two direct
  `BloodthirstyViewFor` call sites (`BasicAttack.cs:152`, `TimelineDispatch.cs:75`, the stub fallback's
  view) still allocate a view per decision — reusing there needs the view to live on `BattleRunState`.
  See `tasks/evidence-fragments/CAI1.14.md`.
  - Acceptance:
    - `DecisionAllocationTests` (new) measures with the settled harness — **bytes, never
      milliseconds**; `GetAllocatedBytesForCurrentThread`, single-threaded; warm first; the measured
      pass is a **whole round**; **production collaborators, not fakes** (a real `CostLedger` over real
      cost rows and real `ActorResourcePools` — a fake here re-creates the defect that hid site 1);
      `Assert.Equal(0, bytes)` with the byte count in the failure message; trace **off**.
    - Zero bytes for: the fallback policy, the core smart policy, the core performance tier, the router
      including the bloodthirsty decorator, and the siege policy.
      `CostLedger_Check_allocates_zero_bytes_for_an_action_with_cost_rows_and_for_one_without`;
      `Resolving_a_pool_allocates_no_channel_id_string`;
      `Re_entering_a_reused_decision_buffer_throws_instead_of_sharing_it`.
    - Identity: `RowsFor_returns_the_same_rows_in_the_same_order_as_the_filtering_implementation`;
      `The_interned_channel_id_equals_the_formatted_one_for_every_registered_resource` (over the closed
      six-member `ResourceIds`); `Argmax_picks_the_same_candidate_as_the_LINQ_chain_over_shuffled_inputs`;
      `Capping_the_candidate_loop_yields_the_identical_set_Take_produced`;
      `The_cap_counts_only_candidates_that_passed_the_skip_filters`;
      `A_battle_with_a_trace_still_records_the_same_top_three`.
    - Siege's candidate loop is bounded by `maxCandidatesScored` **before** the threat loop.
    - No LINQ remains on a decision path.
    - **`PerfSection.AiDecide = 25`, `SectionCount = 26`, `"ai.decide"` at the matching index.**
      (`PerfProbe.cs:40` ends at `LawnMoveDrain = 24` today; `CAI4.7` takes 26 — plan correction 1; see
      `CAI-perf-1`, which measures that this presupposes the unlanded `AiDecide = 25`.)
  - Golden: byte-identical — every change rewrites *how* a value is produced, never *which*. Run
    `BattleGoldenTests`, `ExpeditionResolverTests`, `SiegeAiLiveWiringTests`, `CostLedgerTests` and
    `KernelAllocationTests` and **quote the output in the commit body**.
  - Verify: verify-change; `audit-overflow.py --targets A3`; `guard-battle-responsibility.py`.
  - Files: `Actions/Cost/CostLedger.cs`, `Stats/Derived/DerivedStatChannels.cs`, `Actions/Cost/ActorResourcePools.cs`, `Battle/Siege/SiegeAiIntentSource.cs`, `Actions/Ai/CandidateScorer.cs`, `Diagnostics/PerfProbe.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs` (new).

### Index propagation

- [x] **CAI1.15 — Propagate the program into the index documents** · S · deps: CAI1.6 · docs — **DONE** (lane `combat-ai-2`, 2026-09-20).
  Bullet 1 landed: `docs/DESIGN-GATE.md:57` is the new §1 decision row (inserted immediately after the
  battle row at `:56`), naming `battle-engine-ssot.md` §3c, `combat-ai-map.md` and the ideal, and
  recording this program's closed vocabularies **with counts read from code**: `TargetSelector` 8,
  `AiTier` 2, `AiPlace` 4, `AiRole` 4, `AiRowCondition` 6, `AiCensusCondition` 5, `PersonalityAxis` 4,
  `AiActorClass` 2, `ScoreTerm` 7, `SelectionMode` 2, `Resolvability` 3. Bullet 2 landed at
  `docs/architecture/combat-ai-ideal.md:129`: scheduling reads `KernelDriveHost.NowTicks` /
  `SimulationClock`, `AdvancedEffectClock` is named for wall-clock-seeded status expiry only, and the
  row now says the two are not interchangeable (matching `combat-ai-map.md:81`). Bullet 3 already held.
  Two count pins were missing and were added in this commit (`SelectionMode_has_two_members`,
  `Resolvability_has_three_members`) so the new row's "each count is pinned by its own test" is true.
  See `tasks/evidence-fragments/CAI1.15.md`.
  - Acceptance:
    - `docs/DESIGN-GATE.md` §1 gains a row for **"anything that decides what an actor does — AI,
      intent sources, target or action choice"**, naming `battle-engine-ssot.md` §3c (*the engine
      resolves, the AI decides*), `combat-ai-map.md` and the ideal, and stating the closed vocabularies
      this program owns with their counts. The atom row went stale four times because a count lived in
      one place and moved in another; this row is written knowing that.
    - `combat-ai-ideal.md:119` no longer calls `AdvancedEffectClock` the lawn clock host for triggers.
      It names `KernelDriveHost.NowTicks` / `SimulationClock` for scheduling and keeps
      `AdvancedEffectClock` where it belongs — wall-clock-seeded status expiry
      (`EffectRuntime.cs:42,133`). The map row is already corrected; a correction in one document and
      not its sibling **has not landed**.
    - This todo's cross-program notes list the `battle-engine-ssot.md` §4 D15 "clock sources" row as
      owed to that document's owner. Two specs in one program confused these two clocks, which is the
      signal the distinction is not obvious from the docs alone.
  - Verify: docs; `python scripts/audit-doc-citations.py --scope docs/DESIGN-GATE.md --summary`. —
    **run 2026-09-20, exit 0, 0 HIGH** on all four classes (28 resolvable citations, 1 document).
  - Files: `docs/DESIGN-GATE.md`, `docs/architecture/combat-ai-ideal.md`, this todo.

### Checkpoint CP1 — **CLOSED** (lane `combat-ai-3`, 2026-09-21; `tasks/evidence-fragments/CP1.md`)
- [x] `AiScoring` exists in exactly one place; grep finds no second additive score. — **0 hits** for `class AiScoring` repo-wide; `CandidateScorer.Score` is the one additive score and both rank walks call it.
- [x] The DESIGN-GATE row exists and the ideal names the right clock. — row at `docs/DESIGN-GATE.md:57`; `combat-ai-ideal.md:129` names `KernelDriveHost.NowTicks`/`SimulationClock` for scheduling against wall-clock `AdvancedEffectClock`.
- [x] `combat-ai.v1.json` published and read by both hosts; `siege.v2.json` in place. — `Injector/Host/RpgHost.cs:89` + `Server/Program.cs:237`; `siege.v2.json` read at `Server/Program.cs:231`.
- [x] Every siege suite passes unedited except CAI1.13's single permitted throw assertion. — `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Siege"` → **333 passed / 0 failed**; the only removed assertion lines are CAI1.1's `AiScoring.*` renames, CAI1.10's ported `SiegeIntentSource` dispatch tests and CAI1.13's two `EffectiveTier` throws.
- [x] Battle goldens unmoved and unblessed; the only moved tests are CAI1.5's and CAI1.11's named siege ones. — `BattleGolden` 5/0, `FusionRpg.Core.Balance.Tests` dominance/BalanceGuard/ActionSchedule/Predictor 66/0; `git diff --stat 28537b6d2^ HEAD -- gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs` is **empty**.
- [x] `audit-overflow.py --targets A3` and `audit-magic-numbers.py --summary` gain no row for `Actions/Ai/`. — `--targets A3` now prints nothing (the one row, `Lawn/LawnBattleView.cs:156`, was introduced by CAI4.1 *after* wave 1 and is cleared in this commit's marker); magic-numbers `TOTAL 0 0 0 0 0`.
  **The one code change this checkpoint carries:** `Actions/Ai/Lawn/LawnBattleView.cs:156` took the audit's own `// overflow-bounded:` authored exemption (a bounded 0..1000 per-mille ratio, not a magnitude — 22 existing uses in `src/`, same shape as `Delve/Events/EventFacts.cs:66`'s `HpMilliOf`) and its narrowing is now `checked`. No guard, allowlist or registry was touched. The pre-existing A6 row at `Actions/Ai/CoreIntentPolicy.cs:323` stood at this measurement and was **removed at its root the same day by `CAI-mask-1`**; CP1's sixth line covers `--targets A3` only, and the whole-repo audit total is now 0.

---

## Wave 2 — identity, balance and visibility

- [x] **CAI2.1 — `replay-identity` A: the stamp, the column, the log** · M · deps: CAI1.8 — **CLOSED against its Verify line** (lane `combat-ai-2`, 2026-09-20, on the manager's instruction). The Core half is finished — `CombatAiProfileIdentity.StampOf` + `Compare` over `ContentHashStamp` keyed by the publish counter, `ICombatAiProfileSource`, 11 tests — and the Verify line is green: `verify-change` **14943 passed / 4 failed** (the four pre-existing corpus facts), `guard-dal.ps1` **exit 0**, `guard-test-substrate.py` **exit 0**, plus the identity+ContentHash filter **55 passed / 0 failed**. **UPDATE 2026-09-21 (post-checkpoint-4
  merge `815721b7`): those four corpus facts are FIXED by other lanes — the whole `FusionRpg.Core.Tests`
  project is now **15093 passed / 0 failed**, so this lane's `verify-change` runs are clean and the
  "4 failed" numbers recorded in this program's earlier fragments and rows are HISTORICAL, not a live
  caveat. Do not chase them.** `CombatAiProfileIdentity.StampOf` + `Compare` (a `ContentHashStamp` keyed by the **publish** counter, per-profile parts) and `ICombatAiProfileSource` are landed with 11 tests: round-trip, order-independence, changed-weight `Mismatch` naming the profile, added-profile `RegistryChanged` with `ShouldRefuse` false, null `Match`, corrupted `Unreadable`, and a reflection coverage test so a new profile field cannot escape the hash. **The Data third (the `combat_ai_profile` column, `RpgStore.WebMatches.cs`) and the Server third (the three stamping sites, the pin resolution, the boot-sweep guard) are OUTSIDE this lane's file fence** and are filed in "Deferred / named follow-ups" with `file:line` and the cause; CAI2.2 depends on that Server half and is therefore filed, not attempted. See `tasks/evidence-fragments/CAI2.1.md`.
  - Acceptance:
    - `CombatAiProfileIdentity.StampOf` round-trips through `ToCompact`/`TryParse`; the same set
      stamps identically twice and **order-independently**; one changed weight → `Mismatch` naming
      **that profile id**; a profile **added** → `RegistryChanged` with `ShouldRefuse` false (a new
      place×role must not strand every earlier match); null/empty → `Match`; corrupted → `Unreadable`
      with `ShouldRefuse` true.
    - `rpg_web_match_log.combat_ai_profile` exists, nullable, added idempotently by `EnsureColumn`;
      pre-existing rows keep NULL; a stamped row round-trips through `TryGetWebMatchLog` and
      `ListUnresolvedWebMatches`.
    - No existing `AppendWebMatchLog` caller signature broke.
  - Golden: byte-identical — the report carries no new field.
  - Verify: verify-change; `guard-dal.ps1`; `guard-test-substrate.py`.
  - Files: `Actions/Ai/{CombatAiProfileIdentity,ICombatAiProfileSource}.cs` (new), `Data/Sqlite/RpgStore.cs`, `RpgStore.WebMatches.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiProfileIdentityTests.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/WebMatchLogProfileStampTests.cs` (new).
- [ ] **CAI2.2 — `replay-identity` B: pin the profile at match start, refuse rather than drift** · M · deps: CAI2.1 — **SERVER SOURCE HALF LANDED** (lane `cai2`, session `combat-ai-2b`, 2026-09-23); the row stays open on the `Data` column + the pin wire, which no lane here holds.
  Landed: `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs` — the `ICombatAiProfileSource` the spec's §2 puts
  on the Server. It loads EVERY `data/tuning/combat-ai.v{n}.json` at startup (no retention window: a
  refused replay of a real expedition collect is a player-visible failure), answers `Current` from the
  newest, and `ForVersion(n)` from the map or **`null`** — a refusal, never a fallback to `Current`. Three
  load-time refusals, all naming the file: a name version disagreeing with the document's own `version`
  (the hand-edit ban as a detection — `publish.py` writes both from one counter), a version published
  twice, and a tuning directory with no published combat-ai file. Order-independent by construction (the
  map is built from a sorted set and duplicates are rejected, not "last wins"). 8 tests in
  `gk-core/tests/FusionRpg.Server.Tests/CombatAiProfileFilesTests.cs`, **8 passed / 0 failed**; the boundary's
  module check `FusionRpg.Server.Tests` **814 passed / 0 failed**; `guard-dal` exit 0; `guard-test-substrate`
  exit 0; `guard-doc-citations -Strict` **0 HIGH**. **Owed, and it is the denied `Data` path:** the
  nullable `combat_ai_profile` column on `rpg_web_match_log` (`RpgStore.WebMatches.cs`) — the three stamping
  sites cannot compile without it, and the five-step pin resolution + the boot sweep's fifth guard read
  `entry.CombatAiProfile`. `Program.cs`'s `Configure` call was deliberately NOT switched to the new source:
  with one published version the behaviour is identical, but the Server would then auto-pick the newest
  while `Injector/Host/RpgHost.cs:97-99` still names `combat-ai.v1.json` by hand — a Server/Injector profile
  divergence on the next publish, which is the H7 hazard rather than a fix for it. **CORRECTION (lane `cai3`, session `combat-ai-3`, 2026-09-23): that divergence hazard is SUPERSEDED, so the row's only remaining blocker is the denied `Data` path.** `CAI-F1` landed `CombatAiTuningFiles.Current` and moved BOTH hosts onto it — `Injector/Host/RpgHost.cs:97-99` now reads `CombatAiTuningFiles.Current` (which is `combat-ai.v2.json`), not a literal, and `SiegeKeyMigrationTests.Both_hosts_load_the_same_file` asserts neither host contains a `"combat-ai.v` literal. So a Server that auto-picked the newest would no longer diverge from the Injector: the two would be reading the same revision by construction. Wiring the version-addressed source is therefore no longer an H7 hazard — it is only *useless* until the pin resolution exists, and the pin resolution reads `entry.CombatAiProfile`, which needs the `Data` column. Measured: `grep -rn "CombatAiProfileFiles" src/ tests/` finds the class only in its own file and its test file, so it still has no production caller. See `tasks/reports/CAI2.2.md`.
- [ ] **`CAI-cite-4` — three `file:line` citations the CAI2.5 edit moved, outside this lane's fence** · XS · deps: — · *(found by lane `cai2`, 2026-09-23, while re-anchoring the doc citations its own `InjectorEntityRegistry.cs` edit broke)* — **needs routing, not a decision.**
  The CAI2.5 ring drop added 14 lines inside `InjectorEntityRegistry.Remove` and 4 inside `Clear`, so every
  citation below those points shifted by **+18**. The three inside `docs/architecture/combat-ai/**` were
  re-anchored in the same commit (the rule). These three are out of fence and need their owning program:
  `docs/architecture/action-corpus/spec-lawn-reposition.md:57,78` (`:179-180,210` → `:197-198,228`; owner:
  action-corpus), `docs/architecture/effect-atom/spec-plant-side-status.md:26` (`:269` → `:287`,
  `:272` → `:290`; owner: effect-atom), `docs/research/combat-ai/REVIEW-B.md:59` (`:129-157` → `:129-175`;
  owner: combat-ai, but `docs/research/combat-ai/**` is not in this lane's fence). One more is
  **pre-existing**, not mine: `tasks/vfx-v2-plan.md:26` cites `InjectorEntityRegistry.cs:116-120` for
  `FindZombie`/`FindPlant`, which are at `:315`/`:318` after this edit and were nowhere near `:116-120`
  before it. `guard-doc-citations.ps1 -Strict` reports **0 HIGH** on all of them (it checks bounds, not
  content), so this will not surface at merge.
- [ ] **`CAI-cite-5` — the citations THIS lane's own edits moved, outside its fence** · XS · deps: — · *(found by lane `cai3`, session `combat-ai-3`, 2026-09-23, while re-anchoring the citations its own moves broke)* — **needs routing, not a decision.** The rule is *re-anchor doc citations in the same commit as the code move that breaks them*; this lane made three moves whose blast radius reaches files outside its fence, and `guard-doc-citations.ps1 -Strict` reports **0 HIGH** on all of them (it checks bounds, not content — the same limitation `CAI-cite-4` records), so none will surface at merge. Shifts measured from `git diff -U0`'s own hunk headers against `001e03713ac4`, and the in-fence ones were re-anchored in the same commit (`spec-decision-inspector.md`'s two, `CAI2.4-fourth-arm.md`'s three, `CAI-spec-status-4.md`'s one, `CAI4.8-start-edge.md`'s one):
  - **`gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` — +7 for every line at or after 180** (`@@ -179 +179,8 @@`). Broken: `docs/architecture/action/spec-action-costs-cooldowns-adoption.md:107` (`:198` → `:205`) and `docs/architecture/action/spec-action-resolution-by-category.md:11` (`:171-219` → `:178-226`), `:15` (`:175-193` → `:182-200`). Unmoved: `spec-action-costs-cooldowns-adoption.md:45`'s `:117` and `spec-action-dispatch-generalization.md`'s `:105-143`, `:88-97`, `:156-174` (all before 180). Owner: the `action` program.
  - **`gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` — +14 for every line at or after 100** (`@@ -96,0 +97,2 @@` and `@@ -98,2 +100,14 @@`). Broken: `docs/architecture/action-enrich/spec-lawn-action-base.md:40` (`:225-227` → `:239-241`), `:41` (`:214-224` → `:228-238`); `docs/architecture/action-skill-tiers/spec-rung-table-activation.md:18` (`:225-227` → `:239-241`), `:58` (`:216-227` → `:230-241`); `docs/architecture/action-skill-tiers-map.md:97` and `:160` (`:225-227` → `:239-241`); `docs/architecture/class-system/spec-residual-fit.md:75` (`:116` → `:130`). Unmoved: `docs/architecture/combat-ai/spec-profile-schema.md:360` (`:57`). Owners: `action-enrich`, `action-skill-tiers`, `class-system`.
  - **`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs` — +16 for every line at or after 241** (`@@ -240,0 +241,16 @@`). Broken: `docs/architecture/battle-engine-ssot.md:237` (`:322-324` → `:338-340`). Unmoved: `spec-commander-direct-orders.md:166` (`:19-21,119`), `:290` (`:119-130,171-172`), `spec-match-snapshot.md:14,15,105,106`, `spec-lawn-action-base.md:68` (`:152`). Owner: `battle-engine-ssot`.
  - **`tasks/evidence-fragments/CAI-defer-1.md:16,30`** cites `IntentRouter.cs:77,86-88`; the `sink` parameter is now `:54` and the three wraps are `:68-70` (this lane moved them into the constructor). Owner: **this program**, but `tasks/evidence-fragments/**` is outside this lane's fence — the same gap `CAI-cite-4` records for the same directory.
  - Acceptance: each owner re-anchors its own citation, or says on the line that the file moved.
  - Acceptance:
    - Fresh match stamped with `Current`; replay under an unchanged set returns `"replay"`.
    - **Replay after a `v{n+1}` publish resolves under the pinned `v{n}` set and returns a report
      byte-identical to the fresh one** — the module's whole proof.
    - A pinned version the source cannot supply returns `(false, "profile.unavailable:v{n}", null)` and
      **never** falls back to `Current`; a version that exists but whose file was edited in place
      returns `profile.mismatch`.
    - The boot sweep refuses a profile mismatch **terminally** (`sweep_refused` set, row leaves the
      unresolved window), in the same shape as the four existing guards.
    - **Order-independent:** a delve row resumed *before* a publish and one resumed *after* are
      separate criteria and both are tested — `DelveBattleSessionManager.Resume` and the `StartSession`
      rehydrate branch are two reachable entries into the same pin.
  - Golden: `BattleGoldenTests` untouched; all four constants unmoved.
  - Files: `Server/CombatAiProfileFiles.cs` (new), `Server/WebMatchService.cs`, `Server/DelveBattleSessionManager.cs`, `tests/FusionRpg.Server.Tests/WebMatchProfilePinTests.cs` (new).
- [ ] **CAI2.3 — `action-schedule-twin`: the analytic model follows the core policy** · M · deps: CAI1.8, CAI1.9 — **STAYS OPEN on two rulings** (lane `cai2`, session `combat-ai-2b`, 2026-09-23 re-read: the parity test has LANDED, the dominance run is measured and unmoved, and the row's own blocker for the overkill proof names the wrong cause).
  **STATUS 2026-09-23 — measured, not carried over.** Landed: the parity test
  (`ActionScheduleMatchesCorePolicyTests`, **3 passed / 0 failed**) — the reserve-floor case, the overkill
  DIVERGENCE witness, and the smart/performance collapse. The dominance run is now recorded: `dotnet run
  --project gk-forge/tools/DominanceBaseline -- --theta 100` **reproduces the checked-in baseline exactly** on the
  comparable parts (`dominanceMatrix.names` equal, `dominanceMatrix.wins` equal, `dominantCorners ==
  ["Might"]`, `theta == 100`; the stored file carries three extra keys from a richer invocation — `chains`
  needs `--models` against the live tuning file — and its own `coverage.tuningSync` dates the matrix to
  2026-08-27). The four guard suites are **32 passed / 0 failed**; `BattleGolden` **5 / 0**. The tool is
  read-only without `--out`, so the run needed no fence. See `tasks/reports/CAI2.3.md`.
  **ERRATUM 1 — who owns the projection, and what is the mapping.** One line: *does the projection from a
  `CombatAiProfile` into `Predictor.ActionEconomy.Options` belong to this row (which claims it) or to
  `profile-schema`/module 14 (which `spec-action-schedule-twin.md:421-423` assigns it to) — and if it belongs
  to anyone, what maps a profile's action FILTERS plus a reserve floor onto an `ActionOption`'s
  `CostShareOfOutputMilli`?* Not mechanical, which is why the ownership question is load-bearing: a profile
  carries tags/families/rung bounds and a floor, and **no cost and no multiplier**, while
  `CostShareOfOutputMilli` is a share of the action's own nominal output and the live ledger prices an
  absolute amount scaled by rung and `Θ` (`ActionSchedule.cs:76-79`). Not attempted: inventing the mapping
  would be designing a balance rule with no ruling for it.
  **RE-MEASURED 2026-09-23 (lane `cai3`): the acceptance's four suites, and the one caveat.** `gk-core/tests/FusionRpg.Core.Balance.Tests` — which holds `ResidualFitLoopTests`, one of the four the acceptance names — reads **210 passed / 0 failed** with `python` on PATH, and **208/2** without it, the two reds being `ResidualFitLoopTests`'s own publish-driven cases. The cause is not this row's code: `gk-core/tools/ResidualFitLoop/Program.cs:227` spawns a bare `python`, so the suite is environment-dependent. Recorded as a second instance in `CAI-find-3`'s pattern. `ActionScheduleMatchesCorePolicyTests` (this row's parity test) is **3 passed / 0 failed** either way. **The other three suites' readings were not re-run this session** — `DominanceBaselineTests`/`TerminationGuardTests`/`GearedCornerTests` are inside the same project and therefore covered by the 210/0, but the dominance TOOL run (`gk-forge/tools/DominanceBaseline --theta 100`) was not re-executed; `cai2`'s measured reading of it stands as recorded above.
  **CANDIDATE ANSWER, derived from the code rather than designed (lane `cai3`, session `combat-ai-3`, 2026-09-23) — offered so the erratum is a yes/no instead of an open design.** The projection needs THREE inputs, and the profile is only one of them, which is the whole reason the ownership question has a right answer:
  1. **the profile** contributes the SELECTION and two bounds: `AiActionFilter(Tags, Families, RungAtLeast, RungAtMost)` chooses which held actions become options, `AiReserveFloor(ResourceId, FloorMilliOfMax)` becomes `ActionOption.ReserveFloorMilli`, and `AiWasteGuards.MinTargetsForArea` becomes `ActionOption.MinTargets`. Nothing else — measured, the profile carries no cost and no multiplier (`CombatAiProfile.cs`).
  2. **module 16's compiled held list** contributes `Id` and `Priority`: `Id` is `CompiledAction.ActionId`, `Priority` is the index in the list `LawnHeldActionSets` already sorts once by `ActionTagPreference.Compare` — the same preference order the profile's action filter is applied to, so the two never disagree.
  3. **the ledger + the base derivation** contribute the two numbers the profile does not have: `CostResourceId` is the action's own cost resource, `CostShareOfOutputMilli` is `1000 * cost / nominalOutput` where `cost` is `CostLedger`'s read at the actor's `EffectiveRungOf` (never re-derived by the AI — `ReserveFloorAffordability.ActionCostOf` is the existing precedent for that read) and `nominalOutput` is `ActionSchedule.NominalOutput`'s own definition, `baseDamage * DamageMultiplier`; `DamageMultiplier` itself comes from the action's damage atoms through `ActionBaseDerivation` at the same rung, which is what the ideal's §6.1 step 2 names for the kill/value terms.
  **What that implies for ownership:** the projection is a COMPOSITION of a real loadout, the profile and the ledger — exactly the shape `BattleRunState`'s compile loop and the composition root already own — so it belongs with module 14's re-fit (`CAI3.6`), not with this analytic twin, whose own contract is "the model follows the core policy" and which must not become a second place a loadout is priced. **If the owner rules that way, this row's acceptance line 7 should be struck** (the projection moves to `CAI3.6`'s one-cause commit); if it rules the other way, the seven-field mapping above is the one to implement, and it is mechanical given the three inputs. **Still a ruling, not a decision taken here.**
  **ERRATUM 2 — the overkill parity line cannot pass as written.** The acceptance below says the parity test
  proves equality "for the reserve-floor case and the overkill case". Measured, the overkill case is a
  **divergence** (twin `[skill, skill, pass, pass]` vs seam `[skill, skill, idle, idle]`), so the line needs
  either the restated form — *agrees on the reserve-floor case, pins the overkill divergence as a witness*,
  which is what shipped — or CAI2.6's ruling applied to both guards at once.
  **CORRECTION — the overkill proof's stated blocker has the wrong cause.** The "Still owed" paragraph below
  says it "needs a mix-observing seam — the chosen action per round". That seam **already exists**:
  `ActionSchedule.Walk` returns `IReadOnlyList<RoundOutcome>` and `RoundOutcome` is
  `(string ActionId, double DamageMultiplier)` (`ActionSchedule.cs:71`) — which is exactly what the shipped
  parity and divergence tests assert on. What is actually missing is narrower and is a spec-versus-code gap:
  `Predictor.MixedStrike` calls `Walk(options, pools, baseDamage, maxRounds, policy)` **without**
  `fightEndsThisRound` (`Predictor.cs:260`), so `SkipOverkill` can never fire through the predictor (`Choose`
  requires a non-null predicate, `ActionSchedule.cs:163`) — while the spec §2 says `MixedStrike` "supplies it
  from the cumulative mean it already computes … one closure, built once per `MixedStrike` call". That
  sentence is also not implementable in one pass as written: the predicate is consulted DURING the walk and
  the cumulative mean is computed AFTER it, so the implementable shape is the two-pass
  estimate-then-guarded-walk the row records as attempted-and-reverted. The revert's PROOF problem stands
  too — `MixedSwing` (carrying `EffectiveBase`/`Atoms`) is a private record (`Predictor.cs:59`) that never
  reaches `DuelPrediction`, which is why "two all-free mixes produced 1000 vs 6250". Named precisely for
  whoever holds the ruling: `Predictor.cs:260` plus one optional observer on `MixedStrike`'s output.
  Landed, as the module's own first commit: `SchedulePolicy` with `SchedulePolicy.Greedy` as the identity
  default (`Balance/Analytic/ActionSchedule.cs:54`), the reserve floor (a floor on what REMAINS, per-row
  `-1` defers, 1000 cannot hang — the free fallback short-circuits first), the `SkipOverkill` waste guard,
  the `MinTargets > 1` loud throw and the out-of-vocabulary `AiTier` throw, and the matching knobs in
  `tools/CombatSim/ActionPolicy.Choose`. Every pre-existing `ActionScheduleTests`/`PredictorTests` case
  passes unedited; `ProvePredictor` PASSes both scopes at 1e-4 (max diff 8.836E-007); dominance/
  termination/geared/residual 47/47 unchanged; `guard-class-system` G7 exit 0. Second slice: `Predictor.ActionEconomy` carries the policy and `MixedStrike` hands it to `Walk`, so a reserve floor reaches the duel predictor (measured as lower `NetAttritionA`, even race preserved); the smart/performance collapse is **proved**.
  **ERRATUM REQUESTED — the projection is claimed by two documents.** The row says CAI2.3 owns
  *"the projection from a real profile into `Predictor.ActionEconomy.Options`"*; the module's own spec says
  the opposite at `spec-action-schedule-twin.md:407-408` (*"that projection belongs to `profile-schema`
  (module 2) or to module 14's re-fit"*). **Neither specifies the mapping**, and it is not mechanical: a
  `CombatAiProfile` carries action FILTERS and a reserve floor but no cost or multiplier, while
  `ActionOption.CostShareOfOutputMilli` is a share of the action's own nominal output and the live ledger
  prices an absolute amount scaled by rung and `Θ`. The ruler's answer decides whether
  `ActionScheduleMatchesCorePolicyTests` is this row's or module 2's. **Third slice:** the PARITY TEST landed
  (`Balance/ActionScheduleMatchesCorePolicyTests`) — the real `CoreIntentPolicy` in its performance tier against the twin,
  round by round, agreeing over 8 rounds with no floor; both correspondences are explicit in the fixture (regen ZERO on
  both sides, which removes Open question 2's round<->tick mapping instead of inventing one, and each share derived from
  the authored amount at Theta=0/rung 1).
  **FINDING, needs a ruling:** the reserve-floor RULE differs. `ReserveFloorAffordability.cs:92-108` refuses when
  `current <= floor`, before the action's own cost and for EVERY action; the ideal's words (spec S2 quoting S6.1 step 3)
  are "may not drop below a fraction of its max **after paying**" = `current - cost >= floor`, which is what the twin
  implements. Measured: (a) at 900 per-mille from a full pool the seam allows the 80-cost action twice where the twin
  allows it once; (b) at or below the floor the seam refuses even a ZERO-cost action, so the actor returns
  `ActionIntent.None` and idles instead of falling to its free option — the twin never floors the free fallback,
  deliberately, since a floor that could starve the walk is a hang. Not fixed here: aligning the seam to the ideal moves
  goldens (forbidden by this row's Golden line) and aligning the twin to the seam floors the fallback. Witness test
  `The_reserve_floor_rule_differs_between_the_twin_and_the_shipped_seam`.
  **Still owed:**
  `ActionScheduleMatchesCorePolicyTests` (the parity test — the module's mechanism of the guarantee) and the
  overkill predicate through `Predictor` — **attempted and reverted**: the two-pass estimate-then-guarded-walk
  was implemented and gated on `SkipOverkill`, but `DuelPrediction.NetAttrition` is a derived rate rather
  than the swing mean, so no assertion on it could be explained (two all-free mixes produced 1000 vs 6250).
  It needs a mix-observing seam — the chosen action per round — before it can be proven through the
  predictor; the guard itself is proven at the `ActionSchedule` level. The `gk-forge/tools/DominanceBaseline` run is
  **DONE 2026-09-23** (read-only without `--out`; the matrix and corners reproduce the checked-in baseline —
  see the status block at the top of this row), so the `tools/**` fence note below is moot for that command.
  **Fourth slice — REOPENED and advanced by lane `combat-ai-3` (2026-09-21).** The deps (`CAI1.8`,
  `CAI1.9`) are done in the ledger, so the parity test's missing case is this session's, and it landed: the
  **overkill case is now measured**, and like the reserve-floor case it **does not agree** — it is the
  *same* divergence one guard along. `ActionStage.cs:126`'s `KillMarginMilli` guard refuses **every** action
  in `TryPick`'s loop, so the core returns `ActionIntent.None` and **idles**; `ActionSchedule.cs:171-187`'s
  `SkipOverkill` skips costed options and takes the **free fallback**, because the free option short-circuits
  before the guard is consulted. Measured pair (smart tier, kill margin 50, target below it from round 2):
  twin `[skill, skill, pass, pass]`, seam `[skill, skill, idle, idle]`. Pinned by
  `The_overkill_rule_differs_the_same_way_the_reserve_floor_does`, whose doc comment states both rules with
  `file:line` — and the guard **is** reachable in production: the shipped `siege/default` profile is
  `tierOverride: "smart"` with `killMarginMilli: 0`, so it runs on every smart decision today and only
  misses because it fires on an already-0-HP target. Its own row is **now filed as `CAI2.7`**, holding the same class of ruling `CAI2.6` holds for
  the floor. Also re-verified here: `DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`,
  `ResidualFitLoopTests` **32 passed / 0 failed, unchanged**; whole `FusionRpg.Core.Balance.Tests`
  **210/0**; `verify-change` `core-balance` **210 passed / 0 failed**.
  **Still external, and named as such in the routing section's re-triage table:** the
  **projection** (an owner erratum ruling — this row's own acceptance claims it while
  `spec-action-schedule-twin.md:421-423` assigns it to module 2 or 14, and no document specifies the
  mapping) and the **`gk-forge/tools/DominanceBaseline` run** (a denied path).
  See `tasks/evidence-fragments/CAI2.3.md`.
  - Acceptance:
    - `SchedulePolicy.Greedy` is the default, and **every existing `ActionScheduleTests` and
      `PredictorTests` case passes with no edit**, including the hand-traced 7-round cycle.
      `Walk(..., policy: null)` and `Walk(..., Greedy)` produce identical sequences.
    - Reserve floor, overkill guard and tier are expressible, with per-row override (`-1` defers) and
      **a floor of 1000 that never hangs and never throws** — the free fallback is unfloored by
      construction.
    - `MinTargets > 1` throws naming the option id. Smart and Performance **provably collapse** in the
      duel domain. An out-of-vocabulary `AiTier` throws naming it.
    - `ActionScheduleMatchesCorePolicyTests` (new) proves the twin's chosen action id per round equals
      the real core policy's, for the reserve-floor case and the overkill case.
    - `gk-core/tools/CombatSim`'s `ActionPolicy` carries identical semantics **in this same commit**;
      `gk-core/tools/ProvePredictor` holds both scopes under `1e-4`.
    - `DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests`
      green **and unchanged**, and the dominance run recorded as evidence it did not move.
    - **The projection from a real profile into `Predictor.ActionEconomy.Options` lands here.** Every
      call site hand-builds that list today (`ProvePredictor/Program.cs:115-119`,
      `PredictorTests.cs:15-18`) and nothing projects a `combat-ai` profile into it. Owned by this task
      so CAI3.6 does not discover it inside its one-cause commit.
  - Golden: `BattleGoldenTests` untouched; no `RulesetVersion` bump.
  - Files: `Balance/Analytic/ActionSchedule.cs`, `Predictor.cs`, `gk-core/tools/CombatSim/ActionEconomy.cs`, `Simulator.cs`, `Analytic.cs`, `tests/FusionRpg.Core.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs` (new).
- [x] **CAI2.4 — `decision-inspector` A: the record, the sink, the turn-mode wiring** · M · deps: CAI1.1, CAI1.9, CAI1.10 — **DONE** (lane `combat-ai-2`, 2026-09-20).
  Second slice: emission moved out of `ChooseTarget` into `EmitDecisionRecord` called from `TryDeclare`, so `ChosenActionId`/`ChosenTargetKey` are the returned `ActionIntent`'s own fields; `_gateScratch` records the `UsabilityResult` step 3/4 actually returned for each held action, and the record's `Candidates` now carries BOTH kinds of real fact (scored targets with breakdowns and null gates, gate verdicts with results and null breakdowns), distinguished by which field is set. `Every_scored_candidate_and_every_gate_verdict_appears` asserts both directions, `A_scored_decision_records_exactly_one_record` asserts both chosen fields, and zero-on-a-held-target-tick still holds via `_scoredThisDecision`. The row's whole Verify line is green (three filters: 72/12/7 passed; `guard-secondary-no-unity`, `guard-debug-scope`, `verify-change` 14949/4 pre-existing).
  Landed: `AiDecisionRecord` + `IAiDecisionSink` + `AiTriggerState` + `AiDecisionOrigin` (three-member closed
  vocabulary, pinned) in `Actions/Ai/AiDecisionRecord.cs`; `BattleTraceDecisionSink` emitting the
  **byte-identical** line (`SiegeAiIntentSourceTests` and `AggressionTierMapTests` pass unchanged); siege
  records through the sink with the record built only inside the `_sink is not null` guard, so CAI1.14's
  zero-allocation test stays green; 6 new tests cover one-record-per-scored-decision, zero on a held-target
  tick, real per-candidate breakdowns, golden-neutrality (`AiDecisions` non-empty while `Digest` is
  unchanged) and intent-identity with the sink wired. **Still owed, with the cause:** `ChosenActionId`
  (siege's recorded decision is the TARGET decision; the action is chosen one step later in `TryDeclare`),
  per-candidate gate verdicts (`UsabilityEvaluator` runs against the chosen target only — `Gate`/`ActionId`
  are nullable for exactly that reason), and **"all four policies behind the router record through the same
  sink"**, which needs `IntentRouter.cs`/`CoreIntentPolicy.cs`/`ActionStage.cs`/`StubIntentSource.cs` — none
  of which this row's Files list names. **RULING NEEDED:** re-scope CAI2.4 to that surface, or land the
  router sink as its own task; `ActionStage` is where the per-candidate verdicts would have a real source.
  **RESOLVED WITHOUT A RULING, and the fourth arm LANDED (lane `cai3`, session `combat-ai-3`, 2026-09-23).** Measured: the router sink is not missing — `IntentRouter.Compose` wraps the policy, the fallback and the steered source in `AiDecisionRecordingSource` (`IntentRouter.cs:92-94`), each with its own `AiDecisionOrigin`, so "every arm records" holds **by construction at the router's one construction entry point** with no per-policy edit, which is exactly what that decorator's own class doc claims. **The FOURTH arm was the gap:** the ORDER step returns before any wrapped source runs, so an order-driven decision produced **no record at all**, and `grep -rn "AiDecisionOrigin.Order" src/` returned **nothing** — a closed-vocabulary member with no producer, in the one field CAI4.9's criterion 7 needs the inspector to READ rather than infer. `Resolve`'s order step now records through the same sink with `AiDecisionOrigin.Order`, built by the same `AiDecisionRecordingSource.RecordRouterDecision` helper the decorator uses, so one place shapes a router-level record and the arms cannot drift. **Verified:** `IntentRouterTests` **24 passed / 0 failed** — five new cases, one per arm asserting its own origin (order → `Order`, steered → `Steered`, policy → `Policy`, fallback → `Policy`), the fallback case also pinning that the chain records EVERY arm it consults (so an inspector sees "the policy had nothing, the fallback answered"), plus a no-sink case proving a null sink moves nothing. **Four planted violations — the order recording line and each of the three wraps — each killed exactly its named case.** `FusionRpg.Core.Tests` **9718/0**, `FusionRpg.Core.Balance.Tests` **210/0** (goldens byte-identical), `FusionRpg.Core.Match.Tests` **182/0**, six guards exit 0. See `tasks/reports/CAI2.4-fourth-arm.md`. **CORRECTION AND PRODUCTION WIRE, same lane, 2026-09-23: the acceptance line was met at the ROUTER and unreached in the PIPELINE, and that is now fixed.** Measured: `grep -rn "sink:" src/` returned **nothing** — none of the three production `IntentRouter.Compose` call sites (`BasicAttack.cs:175`, `TimelineDispatch.cs:81`, `DelveBattleSession.cs:188`) passed a sink, so every arm the router wraps recorded nothing in any shipped battle. That is the "a mechanism no production host reaches is not done" shape, so the claim above was too strong and is corrected here. **Landed:** the two Core battle sites now pass `sink: trace is null ? null : new BattleTraceDecisionSink(trace)` — gated on the trace being ACTIVE, so the no-trace path stays allocation-free (`AiDecisionRecordingSource` allocates one wrapper per arm, and CAI1.14's zero-allocation acceptance line is about the sink-NULL path). **`DelveBattleSession.cs:188` is deliberately NOT wired:** its `Trace` is a `DecisionTrace` (`:59`), the delve's own type, not a `BattleTrace` — so `BattleTraceDecisionSink` does not fit there, and giving the delve path a sink means either a delve-side sink or a shared interface, which is a design decision rather than a wire. **Proven through a REAL battle, not at the router:** `DecisionInspectorTests.A_real_battle_reaches_the_routers_sink` runs `BattleEngine.Resolve(BattleGoldenTests.CloseSetup(), 2002, trace)` and asserts the trace carries a router-level line (the router knows no round and no candidate detail, so its line is `0 <actor> ` with an EMPTY top-three and no `#1=` slot) — and a **planted violation** (`sink: null`) kills exactly that test. **Readings:** `FusionRpg.Core.Tests` **9719/0**; `FusionRpg.Core.Balance.Tests` **210/0** (goldens byte-identical — the trace list is digest-excluded, so wiring an observer moves no digest); `FusionRpg.Core.Match.Tests` **182/0**; `FusionRpg.Server.Tests` **858/0**; six guards exit 0; `guard-doc-citations -Strict` 0 HIGH. See `tasks/reports/CAI2.4-production-wire.md`. **One more correction the same lane made, 2026-09-23: the per-arm wrap moved from `Compose` into the CONSTRUCTOR.** Measured by planting the pre-move shape back — wrap in `Compose`, none in the constructor — and running the suite: **1 failed / 24 passed**, the single failure being the new `A_directly_constructed_router_records_its_source_arms_too`, so a caller using the public constructor directly with a sink got the ORDER arm recorded and the three source arms SILENT. "Every arm records" now holds for every construction path, and `Compose` stays an ordering helper (it still hands the policy to `steeredSourceFor` unwrapped). `FusionRpg.Core.Tests` **9720/0**, `Balance` **210/0** (goldens byte-identical), `Match` **182/0**, `Server` **858/0**, six guards exit 0. See `tasks/reports/CAI2.4-wrap-at-construction.md`. **Its spec is synced in the same lane (2026-09-23):** `spec-intent-router.md`'s two code blocks still declared the router's constructor and `Compose` without the `forcedIntent` (CAI4.9 row 14) and `sink` (CAI2.4) parameters, and one sentence below them claimed "the constructor stays exactly as declared" — now false, because the per-arm wrap moved INTO it. Both signatures match the code and the stale sentence is annotated. **Its spec is synced in the same lane (`spec-decision-inspector.md`, 2026-09-23):** the "Still owed" paragraph still called the "all four policies behind the router" line unmet and named the four files it thought were needed, and success criterion 3 read as an open criterion — both now record the landing with the measurement, and the sink-as-constructor-argument paragraph records that production now supplies one (and that a traced battle carries more `AiDecision` lines, one per arm consulted).
  The lawn half (`Trigger` populated, the bounded ring) is CAI2.5, whose injector adapter is outside the fence.
  See `tasks/evidence-fragments/CAI2.4.md`.
  - Acceptance:
    - `IAiDecisionSink` + `AiDecisionRecord` carry every field D4 names: tier, profile, personality,
      trigger state, per-candidate gate verdicts and score breakdown, chosen, top-3.
    - Siege records **through the sink** and `SiegeAiIntentSourceTests` passes **unchanged**;
      `BattleTraceTests` unchanged including the digest-exclusion test.
    - **Golden-neutral, asserted:** a battle resolved with a sink and one resolved without produce an
      identical `BattleReport` and an identical `BattleTrace.Digest`.
    - A spy sink counts exactly one `Record` per decision that **actually scored**, and **zero** on a
      held-target tick.
    - Every candidate the decision scored appears with the gate verdict the gate loop returned;
      `ChosenActionId`/`ChosenTargetKey` equal the `ActionIntent` returned; `TopThree`'s `Total`
      equals `Score` for the same candidate.
    - **All four policies behind the router record through the same sink** — not siege alone.
    - `AiDecisionRecord` carries an `AiDecisionOrigin` field, a **three-member closed vocabulary**
      (policy / order / steered). CAI4.9's criterion 7 depends on it, and the inspector never infers
      an origin from `Candidates[0]` — read-time re-derivation is what the spec forbids.
    - On the lawn the `Trigger` field reads `AiTriggerState.None` until CAI4.7 lands. That is honest,
      not a defect of this task, and CAI4.8 owes the population.
    - With the sink null, CAI1.14's zero-allocation test is **still green**.
  - Golden: byte-identical. If a golden moves, this task is wrong — it is the acceptance, not a re-bless.
  - Files: `Actions/Ai/{AiDecisionRecord,BattleTraceDecisionSink}.cs` (new), `Battle/Siege/SiegeAiIntentSource.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/DecisionInspectorTests.cs` (new).
- [ ] **CAI2.5 — `decision-inspector` B: the lawn ring, default off** · M · deps: CAI2.4 — **INJECTOR HALF LANDED** (lane `cai2`, session `combat-ai-2b`, 2026-09-23); the row stays OPEN on the decision feed and the read route (below).
  Core half (lane `combat-ai-2`, 2026-09-20): `Actions/Ai/AiDecisionRing.cs` — bounded at a structural 8, a
  `last-per-actor` index that survives ring eviction, copy-on-read, an unknown actor returning nothing,
  order-independent death/spawn edges, a reused IL2CPP pointer never rewriting an already-recorded entry,
  and `Clear` emptying both — with 8 tests. **Injector half (this lane):**
  `Injector/Effects/AiInspectFeature.cs` (the three-layer switch, `DefaultEnabled` false, the
  `CheatState.IsUserSet` gate, and the whole rule as a pure `Resolve(env, override, default)` so the two
  env-var wins — untestable through the once-at-startup field — are pinned);
  `Injector/Effects/LawnAiDecisionObservability.cs` (the `IAiDecisionSink` the lawn host will hold, the
  ONE ptr→actor-key derivation, the read accessors, and `ForgetActor`/`Clear`); and the **additive**
  `InjectorEntityRegistry.Remove`/`Clear` drops. 14 new tests in `gk-fusion/tests/FusionRpg.Injector.Tests/`,
  **14 passed / 0 failed**; `guard-injector-compile` OK; single-writer / funnel-delta / actor-hub /
  secondary-no-unity / debug-scope all exit 0. **Stated deviation:** the ring hangs off the REGISTRY, not
  `MatchHost.Runtime.MembershipChanged` — that event's `Cleared` is a *unique-binding* edge and never fires
  for a general creature death, while `InjectorEntityRegistry.Remove` is the lawn's real per-actor death
  edge for BOTH sides (plant-death postfix; `NoteZombieDead`, which re-removes every death-animation frame
  because a resync can re-`Add` a dying zombie) and `Clear` is the match-end edge. `Add` is deliberately NOT
  an edge: `Resync` re-`Add`s every live actor every `ResyncFrames`, so it would wipe a long-lived actor's
  last decision every ~4 seconds. **Residual, and why the box stays unticked:** the ring's production edge
  exists, and its READ ROUTE landed too — `debug.combat.snapshot` now carries `aiDecisionCount` and
  `aiDecisions`, projected to primitives (enums by name, the top-three through
  `CandidateScorer.FormatTopThree`, the ONE formatter) in `DebugCombatActions.cs`; `guard-debug-scope`
  reports **107 routes, 0 banner mismatches**. What is still missing is the **decision FEED**: no lawn host
  calls `Sink.Record` yet — that is `CAI4.8`'s `LawnDecisionHost`, as this
  row's own text says (*"`Trigger` population on the lawn is CAI4.7's"*) — and `CAI4.8` is itself blocked on
  the lawn plan's `lawn-perf-budget.v1.json` (`LW1.1`, measured absent). So the row stays open on that
  NAMED dependency ROW, never on "one wire remains". **Updated (lane `cai3`, session `combat-ai-3`, 2026-09-23):** that dependency's own blocker is now a single sharpened decision — `CAI4.3`'s Cold-push payload shape — so this row's chain reads `CAI2.5` → `CAI4.8`'s decision feed → `CAI4.3`'s payload ruling. Nothing in this row is in-fence-undone. **The READ ROUTE now has tests (this lane, `AiDecisionDumpTests`, 5 cases):** `DebugCombatActions.AiDecisionDump()` is public for the same reason `LawnDecisionDump()` is (the dump builder reads live entities and emits through `DebugRuntime`, so it has no other test seam), and the five cases pin the projection (enums by NAME, candidates by COUNT, the top-three through `CandidateScorer.FormatTopThree` — the ONE formatter), the empty-ring case, that reading twice changes nothing, the WIRING by source scan, and the `AI-INSPECT` gate itself (with the switch off, `Record` writes nothing even though the host holds the sink unconditionally — so an empty `aiDecisions` in a live dump means "hidden by default", which is how a probe must read it). **Three planted violations each killed exactly their named test** (`tier` rendered as the nested struct, the wiring line deleted, the sink's gate removed), then reverted green. See `tasks/reports/CAI2.5.md`.
- [x] **`CAI-find-1` — three `LawnBasicAttackFeature` flag assertions are stale and red on the merged base** · XS · deps: — · *(found by lane `cai2`, session `combat-ai-2b`, 2026-09-23, while running the injector test project for CAI2.5)* — **owning program: lawn-combat-wire** (its todo, `tasks/lawn-combat-wire-todo.md`, is outside this lane's fence, so the row is filed here for the manager to route).
  `gk-fusion/tests/FusionRpg.Injector.Tests/LawnBasicAttackFeatureFlagTests.cs:49,63,106` assert
  `LawnBasicAttackFeature.DefaultEnabled` is **false** / `Enabled` is false by default, while
  `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs:56` has been `DefaultEnabled = true` since
  `9f9853138` (2026-09-16, *"the basic-attack feature is default ON again, on its own metric"*) — that
  commit flipped the constant and did not update the three assertions, whose own doc comments still cite the
  2026-09-15 L-N1 default-off ruling. `FusionRpg.Injector.Tests` is not in `ci.yml`, so nothing caught it;
  the project is **67 passed / 3 failed** on this base and all three are these. Cause read: the test is the
  stale side, not the source — the flag's owner recorded the reversal in the constant's own comment. Fix is
  the owning program's to make (assert the current owner decision, or re-assert the intended one and flip the
  constant with it).
  **CLOSED (lane `cai3`, session `combat-ai-3`, 2026-09-23) — the tests now describe the code, and the choice the row named first is the one taken.** The row lists two options: *assert the current owner decision*, or *re-assert the intended one and flip the constant with it*. The first is not a product decision — the constant's own comment records the reversal twice (`DefaultEnabled = true`, "owner decision 2026-09-16, after the perf pass L-N1's default-off was conditioned on; see the class note for the numbers") — so the tests were the stale side and were corrected rather than the flag reverted; **flipping the constant back would have been the product decision, and it was not taken.** Three corrections, each keeping its test's INTENT: `DefaultEnabled_constant_is_true_by_owner_decision` (asserts `True`, doc comment re-dated to 2026-09-16); `Enabled_defaults_on_with_no_explicit_toggle_ever_set` (asserts `True` — the module default, not the schema fallback, still decides); and `Enabled_ignores_a_stale_backing_field_when_never_explicitly_set`, which is the one that needed real work: it corrupted the backing field to `true` and asserted `false`, which under a default-ON flag proves NOTHING, so it now corrupts to `!DefaultEnabled` and asserts the module default wins. A stale `DefaultOn` reference in that test's doc comment (the constant is `DefaultEnabled`) was corrected with it. **Verified:** the file's five cases **5 passed / 0 failed**; the whole injector project **117 passed / 0 failed** — the merged base's three reds are gone; **planted violation** (flip `DefaultEnabled` to `false`) → **3 failed**, exactly the three corrected cases, then reverted green; `guard-injector-compile` OK; seven guards exit 0; `guard-doc-citations -Strict` 0 HIGH. **The owning program is still owed the decision, not the fix:** lawn-combat-wire may prefer the other option, in which case the constant moves and these three assertions move with it — one commit, and the row says which.
  - Acceptance:
    - `AiDecisionRing` bounded with a `last-per-actor` index that **survives eviction**; a read returns
      a **copy**; reading an unknown actor returns nothing — never a synthesised record.
    - Death removes the index entry; a reused ptr finds no stale entry; **order-independent** —
      death-then-spawn and spawn-then-death both tested. Entries already recorded are not rewritten by
      a later reuse of the same ptr.
    - `AiInspectFeature.Enabled` is **false** with no env var and no explicit toggle;
      `FUSIONRPG_AI_INSPECT=0` wins over a toggle, `=1` turns it on; a never-toggled `CheatState` does
      not supply a default (the `IsUserSet` gate — the exact defect `LawnBasicAttackFeature.cs:35-45`
      records).
    - The ring's cleanup in `InjectorEntityRegistry.Remove`/`Clear` is **additive**: it does not remove
      any drop already present.
  - Golden: byte-identical.
  - Verify: verify-change; `guard-debug-scope.py`; `guard-secondary-no-unity.ps1`.
  - Files: `Actions/Ai/AiDecisionRing.cs` (new), `Injector/Effects/{AiInspectFeature,LawnAiDecisionObservability}.cs` (new), `Injector/Effects/InjectorEntityRegistry.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiDecisionRingTests.cs` (new).

- [x] **CAI2.6 — the reserve floor's rule: the shipped seam and the ideal disagree (FOUND by CAI2.3's parity test)** · S · deps: CAI2.3 · **DONE (lane `cai2`, session `combat-ai-2b`, 2026-09-23) — RULED from the documents, then implemented.**
  **THE DECIDING DOCUMENT, named as asked: `docs/architecture/combat-ai-ideal.md:318` (the ideal's §6.1 step 3)** — *"the reserve floor: a pool may not drop below a fraction of its max **after paying**"*. The spec (`spec-action-schedule-twin.md` §2) quotes that line verbatim, so both authority documents agree; the shipped seam was the defective side, and it was fixed rather than the twin. **The rule as landed:** `ReserveFloorAffordability` compares the POST-PAYMENT balance — `currentBalanceOf(resourceId) - costOf(actorKey, actionId, resourceId) < floor` refuses — so equal to the floor is admitted (the pool does not drop BELOW it) and a zero-cost action at the floor is admitted, which is what ends the idling. The cost is a READ (`ActionCostOf`, a new trailing-optional ctor delegate) supplied by the composer from the one `CostLedger`-shaped authority, never computed here (ideal §3 principle 6). The rule is stated ONCE, in that class's doc and in the spec's retitled section. **Verified:** `ActionScheduleMatchesCorePolicyTests` **3/0** — the witness is now a PARITY assertion (`Assert.Equal(twin, real)`, both `[skill, pass, pass, pass]`), where it previously asserted `{ skill, skill, null, null }`; `ActionStageTests` **16/0** with the two seam cases flipped to the ruled boundary (`The_floor_admits_landing_on_it_and_refuses_dropping_below_it`, `A_zero_cost_action_is_admitted_at_the_floor_so_the_actor_never_idles`); `FusionRpg.Core.Balance.Tests` **301/0**; **`BattleGolden` 5/0, byte-identical**; `guard-actor-hub`/`guard-battle-responsibility`/`guard-single-writer`/`guard-dal` exit 0. **THE GOLDEN CONSEQUENCE, measured rather than assumed:** the old row said the first ruling is *"explicitly NOT byte-identical"*. It is byte-identical today, because `new ReserveFloorAffordability(...)` still appears NOWHERE in `src/` (only in tests) and both shipped profiles author `reserves: []` — so no battle can see the change. The predicted-delta note therefore records a measured NO-MOVE: the golden move belongs to the commit that wires the decorator (`CAI3.6`) and authors a non-zero floor. **One residual edge kept honest rather than smoothed over:** a pool ALREADY below the floor still refuses a zero-cost non-Basic action (`10 - 0 >= 50` is false); the actor is not idle because `ActionKind.Basic` is structurally exempt, which is the seam's own form of the twin's unfloored free fallback. See `tasks/reports/CAI2.6.md`.
  **SUPERSEDED — the pre-ruling cross-reference slice (kept for history):**
  - **THE RULING ASKED, in one line (sharpened by lane `cai2`, session `combat-ai-2b`, 2026-09-23):**
    *does the reserve floor bind what REMAINS after paying — `current - cost >= floor`, the ideal §6.1
    step 3 wording and what the twin implements — or the BALANCE, `current <= floor`, which is what the
    shipped seam implements — and does a zero-cost action stay exempt from it either way?*
  - **Evidence A — for the ideal's reading, against the seam's.** (i) The ideal's own words:
    *"a pool may not drop below a fraction of its max after paying"*. (ii) The seam's comparison is
    **cost-blind** (`ReserveFloorAffordability.cs:117`), so at or below the floor it refuses even a
    zero-cost non-Basic action, the policy returns `ActionIntent.None` and the actor **idles** instead of
    falling through to its free option. (iii) The SAME divergence appears one guard along: `ActionStage.cs:126`'s
    `KillMarginMilli` refuses every action and the actor idles, where the twin's `SkipOverkill`
    (`ActionSchedule.cs:163`) skips the costed options and takes the free one — so the seam has *two*
    idle-producing rules and the twin has none.
  - **Evidence B — for the seam's reading.** (i) `ActionKind.Basic` is structurally exempt
    (`ReserveFloorAffordability.cs:105`), so the idling case needs a non-Basic zero-cost action, and the
    class doc states the coarseness is deliberate: the decorator is a gate that must answer before any
    cost is known, and reading an action's own cost rows is `CostLedger`'s private knowledge, not the
    AI's to re-derive (one cost authority). (ii) **The seam is currently unreachable and doubly inert,
    which is the fact this ruling actually turns on** — `new ReserveFloorAffordability(...)` appears
    **nowhere in `src/`** (only in `ActionStageTests` and `ActionScheduleMatchesCorePolicyTests`),
    `CoreIntentPolicy`'s only factory is `CreateForTest` (`CoreIntentPolicy.cs:123`, `internal`), the
    production siege path passes the bare `CostLedger` as its affordability check
    (`BattleRunState.cs:701-702`), and BOTH shipped profiles author `reserves: []`
    (`gk-core/data/tuning/combat-ai.v1.json`), so `floor <= 0` skips every resource
    (`ReserveFloorAffordability.cs:116`). **Aligning the seam to the ideal today therefore moves NO
    golden** — the row's *"the obvious fix moves battle goldens"* is a claim about the commit that
    WIRES the decorator (`CAI3.6`) **and** authors a non-zero floor, not about this ruling. The ruling is
    blocked because the semantics `CAI3.6` will switch on must be decided before content authors a floor,
    not because a golden move is imminent.
  - **Correction to this row's own Golden line (measured 2026-09-23, lane `cai2`).** It reads
    *"explicitly NOT byte-identical under the first ruling"*. Measured: today it is byte-identical under
    **both** rulings, for the two reasons in Evidence B (no production construction site; no authored
    floor). The conditional form is the true one: the first ruling is NOT byte-identical **once the
    decorator is wired and a floor is authored**, and that commit is the one that owes the predicted-delta
    note. Nothing about the ruling itself changed; only the claim about its blast radius.
  - Why this is its own row: the defect is real, it is in THIS program's fence, and the obvious fix moves
    battle goldens — so it cannot ride inside CAI2.3 (whose Golden line is byte-identical) and it cannot be
    a silent edit. Filed here so it is a first-class task rather than a parenthetical.
  - The two rules, both read rather than paraphrased:
    - `gk-core/src/FusionRpg.Core/Actions/Ai/ReserveFloorAffordability.cs:101-118` refuses when
      `currentBalanceOf(resourceId) <= EffectiveFloorAbsolute(resourceId)` — evaluated BEFORE the action's
      own cost, and applying to EVERY action (only `ActionKind.Basic` is structurally exempt, `:105`).
    - `docs/architecture/combat-ai/spec-action-schedule-twin.md` §2, quoting the ideal §6.1 step 3, says a
      pool *"may not drop below a fraction of its max **after paying**"* — `current - cost >= floor` — which
      is what the twin implements (`ActionSchedule.Choose`, `:186`) and what its own tests pin.
  - **Measured, by the witness test `ActionScheduleMatchesCorePolicyTests.The_reserve_floor_rule_differs_between_the_twin_and_the_shipped_seam`** (max 1000, floor 900, costs 80/40 from a full pool): the twin
    takes `[skill, pass, pass, pass]`; the seam takes `[skill, skill, null, null]`. Two distinct effects —
    (a) the seam permits the 80-cost action twice where the post-payment rule permits it once; (b) once at
    or below the floor the seam refuses **even a zero-cost action**, so the policy returns
    `ActionIntent.None` and the actor idles instead of falling through to its free option. The twin never
    floors the free fallback, deliberately, because a floor that could starve the walk is a hang.
  - Acceptance (whichever way it is ruled):
    - The ruling is recorded in this row, and the rule is stated ONCE — in the code comment and the spec
      together, because the whole defect is that two files state the same word differently.
    - If the seam is ruled wrong: `ReserveFloorAffordance` compares the post-payment balance, the witness
      test's `real` expectation flips to match the twin, and **the golden move is this row's own one-cause
      commit** with a predicted-delta note naming every moved test — never folded into CAI3.6's re-bless
      (`H1`), because a balance rule and a default-policy switch are two causes.
    - If the twin is ruled wrong: `ActionSchedule.Choose` gains the pre-condition semantics, the free
      fallback becomes floorable, and the spec's §2 wording is corrected in the same commit — plus the
      hang question is answered explicitly, because a floored free option is what the current comment
      calls a hang.
    - Either way `ReserveFloorAffordabilityTests` (or the nearest existing suite) pins the ruled rule, so
      the behaviour cannot drift a third time.
  - Pinned in BOTH suites so the ruling has a target: the witness test in `ActionScheduleMatchesCorePolicyTests`
    (both sequences) and two cases added to the SEAM's own suite (`ActionStageTests`) —
    `The_floor_refuses_at_exactly_the_balance_and_would_admit_one_point_above_it` (pins the `<=`) and
    `A_zero_cost_action_is_refused_at_or_below_the_floor_too_so_the_actor_idles` (pins the cost-blindness).
    See `tasks/evidence-fragments/CAI2.6.md`.
  - Cross-reference slice (pre-ruling, comment-only): the seam's class doc, `ActionSchedule.Choose`'s
    floor comment AND `spec-action-schedule-twin.md`'s Open questions now each state their own reading,
    name the other, and point here — so a reader of any single file learns a second rule exists. Nothing
    in either implementation changed, so no golden moved and the ruling still decides which side moves.
    verify-change 15108 passed / 0 across six projects; **Guard.Tests is 4/0 now** (tvb58's reds fixed).
  - Golden: **today byte-identical under BOTH rulings** (measured 2026-09-23 — see the correction above:
    the seam has no production construction site and both shipped profiles author no floor). Under the
    first ruling it stops being byte-identical at the commit that wires the decorator and authors a floor,
    and that commit is the one that owes the predicted-delta note. Under the second it stays byte-identical.
  - Verify: verify-change; `guard-battle-responsibility.py`; the golden filter with the numbers quoted.
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/ReserveFloorAffordability.cs`, possibly
    `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs`, `docs/architecture/combat-ai/spec-action-schedule-twin.md`, `tests/FusionRpg.Core.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs`.

- [ ] **CAI2.7 — the kill-margin waste guard's rule: the shipped seam and the twin disagree (FOUND by CAI2.3's parity test)** · S · deps: CAI2.3 — **FILED (lane `cai3`, session `combat-ai-3`, 2026-09-23). NEEDS AN OWNER RULING; no code may move before it.** This is the row CAI2.3's own text says is owed (*"Its own row is owed the same ruling `CAI2.6` holds for the floor"*), filed here rather than left as a parenthetical for the same reason CAI2.6 was: the defect is real, it is in this program's fence, and the two fixes pull in opposite directions.
  - **THE RULING ASKED, in one line:** *when the kill-margin waste guard fires, does the actor go IDLE — `ActionIntent.None`, which is what the shipped `ActionStage.TryPick` does — or does it fall through to the FREE option, which is what the twin's `ActionSchedule.Choose` does — and if it falls through, does a fired guard skip only COSTED options or every option?*
  - **Evidence A — for the twin's reading, against the seam's.** (i) The ideal lists the waste guards as a step of the SAME action-choice pass as the reserve floor (`combat-ai-ideal.md:319`, step 3 — *"minimum targets for an area action, target not about to die, fight not about to end"*), and the twin's free fallback is **never floored and never skipped** (`ActionSchedule.cs:171`, its own comment: *"that is what keeps Walk's own 'a dry actor has nothing to do' validation true for every floor value"*) — so a guard meant to prevent WASTE cannot be the thing that makes an actor idle. (ii) Measured, the seam DOES idle: `ActionStage.cs:102-103` `continue`s past every refused action and `:108-109` returns `actionId = ""` / `false`, so `CoreIntentPolicy` returns `ActionIntent.None`. The free fallback (`ActionKind.Basic`) is a held action like any other and carries **no** waste-guard exemption (`ActionStage.cs:125-126` applies to every action; only the reserve floor exempts Basic).
  - **Evidence B — for the seam's reading.** (i) `ActionStage` is a GATE consulted before any cost is known — that is the class's own stated posture, and the same argument CAI2.6's Evidence B made for the floor: re-deriving an action's own cost is `CostLedger`'s private knowledge, not the gate's. The twin can answer "does the free option already end it" because `ActionSchedule` prices its own options; the seam cannot without a second cost read. (ii) **The seam is inert for a live target today, which is the fact the ruling actually turns on.** The only shipped profile that reaches this path is `siege/default` (`gk-core/data/tuning/combat-ai.v2.json`: `tierOverride: "smart"`, `guards.killMarginMilli: 0`), and `CoreIntentPolicy.cs:224` passes it as the stage's `WasteGuardThresholds`. With a margin of **0** the guard fires only at `targetFacts.HpMilli <= 0` — an ALREADY-DEAD target — so it refuses nothing a live decision would otherwise take. The divergence therefore moves no golden and changes no live battle today; it becomes real at the commit that authors a non-zero margin, exactly as CAI2.6's floor became real when a floor is authored.
  - **Measured, by the witness test `ActionScheduleMatchesCorePolicyTests.The_overkill_rule_differs_the_same_way_the_reserve_floor_does`** (`gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs:335-350`; smart tier, kill margin 50, target at `HpMilli` 30 from round 2, `fightEndsThisRound` true from round 2): the twin takes `[skill, skill, pass, pass]`; the seam takes `[skill, skill, null, null]`. Same trigger, two answers — the same shape as CAI2.6's floor witness, one guard along.
  - **NOT proved here, and named:** whether a 0-HP target can still reach `TryPick` on any place. Liveness comes from the view (`CoreIntentPolicy` iterates the view's live keys; on the lawn `LiveActorKeysFor` is the census list, where a death-animation actor may linger). With `killMarginMilli: 0` this decides whether the guard is *unreachable* or merely *refuses an already-decided target*; both readings make it inert for a live target, and neither changes the ruling.
  - **EVERY DOCUMENT SEARCHED, and the gap named (lane `cai3`, session `combat-ai-3`, 2026-09-23) — so the owner's choice is between two *undocumented* behaviours, not between a document and a defect.** This is the opposite of `CAI2.6`'s case, and it is what the ruling now turns on:
    - **The ideal puts the waste guards in the SAME pass as the reserve floor** (`combat-ai-ideal.md:319`, §6.1 step 3) and then says *"the highest rank row wins"* — **it never says what happens when NO row passes.** Silent on the aftermath.
    - **Module 9's spec states, as its own success criteria, the invariant the seam breaks:** *"A floor that it does not clear falls through to the next affordable option, and to the free option when none clears"* (`spec-action-schedule-twin.md:295`), *"A floor of 1000 never hangs and never throws: the free fallback is unfloored by construction"* (`:298`), and — under the heading **Waste guard** — *"round k takes the free option while rounds before it are unchanged"* (`:300-302`). The reason is at `:140-143`: *"The free fallback is never floored … which is what keeps `Walk`'s own validation — 'must contain at least one free action … a dry actor has nothing to do' — true for every floor value including 1000. A floor that could starve the walk would be a hang, not a balance decision."* `ActionSchedule` enforces exactly that at construction (`:107-109` — it refuses an option list with no cost-free entry, naming *"a dry actor has nothing to do"*).
    - **Module 1's spec — the seam's own — is SILENT on the aftermath.** `spec-core-scorer.md:269-271` says what each guard refuses; `:466` says only that each guard *"refuses exactly its own case when switched on and `runWasteGuards` is true"*. **No sentence anywhere says a refused candidate leads to `ActionIntent.None`.** So the seam's idling is an implementation choice, not a documented rule.
    - **What that leaves, stated plainly:** the seam refuses EVERY action including the cost-free one, so an actor can idle — the exact outcome `CAI2.6`'s ruling was made to end (that row's own words: the post-payment comparison *"is what ends the idling"*). **The two rows are the same defect seen twice: the seam has no free-option floor of last resort.**
    - **RECOMMENDED, NOT TAKEN, so the owner can accept it in one word:** rule that a **cost-free action is never refused by a waste guard** — matching the twin's short-circuit (`ActionSchedule.cs:171-172`, taken before `skipCosted` is consulted), the spec's waste-guard criterion (`:300-302`) and `ActionSchedule`'s construction invariant. The seam-side fix is one line in `ActionStage.PassesWasteGuards` (`action.Costs.Count == 0` ⇒ pass; measured, the parity fixture's free action carries ZERO cost rows, not a zero-amount row), plus flipping the witness's `real` expectation to parity and re-fixturing `ActionStageTests`' two kill-margin cases onto a COSTED action — its current fixture is cost-free, so the guard's own test would otherwise stop testing the guard. **Golden risk measured rather than assumed:** the shipped profiles author `killMarginMilli: 0`, so the guard fires only at `HpMilli <= 0`, and a golden moves only if a golden battle has a 0-HP candidate with a cost-free action available — which the golden filter must be run to decide. **Not taken here because the documents ARGUE against the seam without DECIDING it**, and this row's own text says no code may move before the ruling.
  - Acceptance (whichever way it is ruled):
    - The ruling is recorded in this row, and the rule is stated ONCE — in the code comment and the spec together, because the whole defect is that two files state the same word differently.
    - If the seam is ruled wrong: `PassesWasteGuards` stops refusing the free option (or the stage gains the same "skip costed, keep free" fall-through the twin has), the witness test's `real` expectation flips to match the twin, and **the golden move — if any — is this row's own one-cause commit** with a predicted-delta note naming every moved test, never folded into CAI3.6's re-bless (`H1`).
    - If the twin is ruled wrong: `ActionSchedule.Choose` gains the seam's pre-condition semantics, the free fallback becomes skippable, and the spec's §2 wording is corrected in the same commit — plus the hang question is answered explicitly, because a skippable free option is what the current comment calls a hang.
    - Either way the witness test's doc comment (which already states both rules with `file:line`) is updated to the ruled one, so the behaviour cannot drift a third time.
  - Golden: **today byte-identical under BOTH rulings** (measured: no shipped profile authors a non-zero margin, so `HpMilli <= 0` is the only firing condition). Under the first ruling it stops being byte-identical at the commit that authors a margin.
  - Verify: verify-change; the twin/parity filter with the numbers quoted; the golden filter with the numbers quoted.
  - Files: `gk-core/src/FusionRpg.Core/Actions/Ai/ActionStage.cs`, possibly `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs`, `docs/architecture/combat-ai/spec-action-schedule-twin.md`, `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs`.

### Checkpoint CP2
- [ ] Every match logged carries a profile stamp; a cross-publish replay is byte-identical to the fresh resolve.
- [ ] The twin agrees with the real core policy; `ProvePredictor` under `1e-4`; dominance unchanged.
- [ ] The inspector is compiled in, default off, and the zero-allocation test is still green with it present.

---

## Wave 3 — place wiring (turn modes)

- [x] **CAI3.1 — `stance-wiring`: one seam, two dead keys removed (H7)** · M · deps: CAI1.8, CAI1.10 — **DONE** (lane `cai2`, session `combat-ai-2b`, 2026-09-23): the seam half (lanes `combat-ai-2`/`combat-ai-3`) plus **Outcomes 2/3**, which were routed as blocked only because the lane that filed them did not hold the readers. **Both readers are in this lane's fence** (`gk-core/data/tuning/**` + `gk-core/src/FusionRpg.Server/**` + `gk-fusion/src/FusionRpg.Injector/**`), so H7 was satisfiable here. The criterion is answered — **no held action is a stance action today** — and this commit is the spec's Outcome 1 exactly ("wire the seam, defer the runtime"): `BattleRunState.Stance` is the one `IStanceCheck`, defaulted to `NoStanceHeld.Instance`, and the three former hardcoded sites read it; `StanceSeamTests` proves exactly one code occurrence of that literal remains in `Battle/**`; 660 golden/expedition/siege/DefenceActionStance/AuraRuntime/Trait/BalanceGuard tests unmoved; `audit-overflow` exit 0; `StanceRuntime`/`PoiseLedger`/`Riposte` untouched.
  **REOPENED AND ADVANCED by lane `combat-ai-3` (2026-09-21) — blocker (1) is RESOLVED, and the two
  behavioural tests are LANDED.** Re-reading the seam showed the prop was not a visibility problem at all:
  `BattleRunState.Stance` had a **reader and no writer** — `grep` finds zero assignments to it anywhere in
  the repo — so gate 0 was inert *by construction* rather than by content, and the tests were un-writable
  for that reason. The in-fence fix is the seam's missing writer: `BattleEngine.Resolve` gains a trailing
  optional `IStanceCheck? stance = null`, forwarded to the run state's ctor (`if (stance is not null) Stance
  = stance;`), so no visibility changed and every existing caller is byte-identical. The two tests now
  drive a REAL battle through it: `A_run_state_with_no_stance_assigned_refuses_nothing` → `BattleOutcome.Victory`,
  and `A_supplied_stance_check_reaches_gate_zero_through_the_run_state` → `Stalemate` with the same seed and
  fixture, because an unexempted gate 0 refuses every action on both sides. `FixedStance` was promoted out of
  `ActionUsabilityEvaluatorTests`'s private nesting into `tests/…/Actions/FixedStance.cs` so BOTH files use the
  one fake, as the row requires. Goldens **byte-identical** (14/0), landed slices 5175/0, balance 210/0,
  `audit-overflow` 0 findings, three guards exit 0, `verify-change` **15158 passed / 0 failed** across 13
  boundaries. See `tasks/evidence-fragments/CAI3.1.md`.
  **Outcomes 2/3 LANDED (lane `cai2`, 2026-09-23) — the row's acceptance is fully satisfied.** `siege.v3.json` was produced by ONE `--remove-key ×2` invocation (`published siege (v2 -> v3, 2 change(s))`; a JSON diff of v2→v3 shows exactly the two `REMOVED` keys, `version` 2→3 and the publish label, nothing else) and `Server/Program.cs` switched to it **in the same commit** (H7). `AiTuning` is now `(ObjectiveReferenceDistanceCells, ThreatRadiusCells)`; `SiegeTuning.Parse` reads exactly those and, deliberately, still **validates** the two removed keys when present (`ValidateRemovedKeys`) — absent is legal, wrong is not, so a typo in a key nobody reads cannot become invisible (`SiegeTuningContractTests` pins both). `Siege_v2_still_carries_the_two_dead_keys` is **deleted** and replaced by `Siege_v3_is_the_shipped_file_and_no_longer_carries_the_two_dead_keys`; `SiegeTuningContractTests` now builds its two shapes from the SHIPPED v3. Four `AiTuning` constructions lost two named arguments (the row named three; `SiegeAiLiveWiringTests.SiegeAiTuningForTest` was the fourth) and `gk-core/tests/FusionRpg.Server.Tests/PowerAndAptitudeTuningTestBootstrap.cs` reads v3 like production. **Numbers:** siege filter **333/0**, siege+goldens **338/0**, Stance/AuraRuntime **186/0**, Data.Tests focused **24/0**, E2E **Build succeeded**, `BootContentCopyRuleTests` **2/0**, seven guards exit 0, `audit-magic-numbers` TOTAL 0, `resource_ownership --check` 166/166. `StanceRuntime`/`PoiseLedger`/`Riposte` untouched; `RulesetVersion` still 5. `SiegeAi.cs`/`CandidateScorer.cs`/`SiegeAiIntentSource.cs` were re-edited to preserve their exact line counts so their ~20 doc citations did not move; only `SiegeTuning.cs` shifted, and its two citations were re-anchored — one of which exposed `CAI-find-2`. See `tasks/reports/CAI3.1.md`.
  **Superseded paragraph (kept for history).** Outcomes 2/3 (deleting `ai.stanceDefault` and
  `ai.autoResolveHandicapMilli`) need `AiTuning` narrowed, which breaks the **named-argument** constructions in
  `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs:530` and
  `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:470` — both outside this lane. `siege.v3.json`
  cannot land without its readers (H7: `Server/Program.cs:231` names `siege.v2.json` by hand). `SiegeKeyMigrationTests.Siege_v2_still_carries_the_two_dead_keys`
  stays until that narrowing lands — it is superseded BY the narrowing, and deleting it now would assert a
  decision nobody made (the test's own comment says so).
  - Acceptance:
    - The commit body **states the criterion's answer** — "no held action is a stance action today" —
      and names which of the three outcomes each file change belongs to.
    - `BattleRunState` exposes exactly one `IStanceCheck` (default `NoStanceHeld.Instance`);
      `Every_policy_construction_reads_the_run_states_one_stance_seam` — a source scan finds **zero**
      `NoStanceHeld.Instance` literals in `gk-core/src/FusionRpg.Core/Battle/**` outside
      `Actions/IAffordabilityCheck.cs`'s declaration.
    - `A_run_state_with_no_stance_assigned_refuses_nothing` (identity) **and**
      `A_supplied_stance_check_reaches_gate_zero_through_the_run_state` (a fake `IStanceCheck` that
      refuses produces `UsabilityReason.StanceHeld`) — reuse the existing `FixedStance` fake, do not
      write a second one.
    - `siege.v3.json` produced by **one** `--remove-key ×2` invocation of CAI1.7's verb — not by
      extending the tool here, not by two publishes, not by hand.
    - `AiTuning` has **two** members (`ObjectiveReferenceDistanceCells`, `ThreatRadiusCells`);
      `SiegeTuning.Parse` reads exactly those and rejects **neither** an older file that still carries
      the two removed keys **nor** a newer one that does not. The three `ContractTuningTestBootstrap`
      constructions lose two arguments each.
    - `SiegeKeyMigrationTests.Siege_v2_still_carries_the_two_dead_keys` is **deleted here** (it is
      superseded); its migration-fidelity assertions are untouched.
    - `StanceRuntime.cs`, `PoiseLedger.cs`, `Riposte.cs` **unmodified**;
      `DefenceActionStanceTests`, `DefenceActionStanceSlotTests`, `AuraRuntimeTests` pass unchanged.
  - Golden: byte-identical; `RulesetVersion` stays 5. **A moved golden means outcome 1 was implemented
    as a live `StanceRuntime` rather than as the seam.**
  - Files: `Battle/{BattleRunState,BasicAttack,TimelineDispatch}.cs`, `Battle/Siege/SiegeAi.cs`, `Battle/Board/SiegeTuning.cs`, `gk-core/data/tuning/siege.v3.json` (new), three `ContractTuningTestBootstrap.cs`, `tests/…/Actions/StanceSeamTests.cs` (new), `tests/…/Battle/Board/SiegeTuningContractTests.cs` (new).
- [x] **`CAI-find-2` — no loader refuses a negative AI weight, and a spec row claims one does** · XS · deps: — · *(found by lane `cai2`, 2026-09-23, while re-anchoring the citations CAI3.1's deletion moved)* — **owner: this program (module 2's loader, `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiTuningLoader.cs`, is in every combat-ai lane's fence).**
  `docs/architecture/combat-ai/spec-ai-tiers-personality.md:200` says a personality axis's weight is
  *"clamped to the profile's own min/max for that weight; never below 0 (the loader already refuses a
  negative weight, `SiegeTuning.cs:346-349` is the shipped precedent)"*. Measured: the anchor was inside
  the block CAI3.1 removed (it held the two dead keys, not a weight check), and the weight check it named
  did not move with the ten keys — `CombatAiTuningLoader.ParseScoring` (`:161-177`) reads all seven weights
  through `Int(el, …)` with **no sign check at all**, while its neighbours DO refuse a non-positive value
  (`aggressionRange <= 0` at `:167-170`, `maxCandidatesScored <= 0`). So a `combat-ai.v{n}.json` with
  `weightKill: -50` parses today, and a negative weight inverts its score term rather than being rejected.
  Cause read: the negative-weight refusal was a property of the OLD `SiegeTuning` reader; CAI1.8 moved the
  keys and did not carry the check, and the spec row kept citing the old address. The spec row is annotated
  with the measurement in this commit (it is in fence); the loader fix is filed here rather than made,
  because adding a validation to a shipped parser is a behaviour change that wants its own commit and its
  own `SiegeKeyMigrationTests`-shaped pin. **Not a balance question** — a negative weight is malformed
  input, so the fix is a parse-time refusal, not a tuning publish.
  **CLOSED (lane `cai3`, session `combat-ai-3`, 2026-09-23) — the refusal is restored, at parse, for all seven weights.** `CombatAiTuningLoader.NonNegativeWeight` (`:198-206`) reads each weight and throws `CombatAiTuningRejection` naming `profiles.<id>.scoring.<key>` when it is negative, so the four terms with no downstream clamp (hit-chance, objective, cannot-counter, round) can no longer invert themselves and the three `AiPersonalityApply.ClampNonNegative` touches can no longer have a malformed authoring hidden by the clamp. ZERO stays legal — it disables a term, which is a real authoring choice, and the spec's clamp is about the RESULT. **Verified:** `CombatAiTuningTests` + `SiegeKeyMigrationTests` **33 passed / 0 failed** (8 new cases included); **planted violation** (`if (value < 0)` → `if (value < int.MinValue)`) → **7 failed**, exactly the seven per-weight theory cases, then reverted green; both shipped files (`combat-ai.v1.json`, `combat-ai.v2.json`) author no negative weight, so no tuning publish is owed. The spec row's own citation is corrected in the same commit (`spec-ai-tiers-personality.md:200`), because the fix moved the address it named. See `tasks/reports/CAI-find-2.md`.
- [ ] **CAI3.2 — `siege-loadout-wiring` A: one home for the equipped-action rule** · M · deps: CAI1.1
  - Acceptance:
    - `RpgStore.EquippedActionIdsFor(instanceId)` is the **only** implementation of the two-scope grant
      merge + `GetLoadoutOrAutoEquip`; a repo search finds no second
      `ListGrants(UniqueActor) … Concat … GetLoadoutOrAutoEquip` chain. `WebMatchService`'s static
      (`:738` — **re-anchored 2026-09-23, lane `cai3`: the row cited `:654-675`, which is now a
      different region of that file**) and `SpecimenLoadoutEndpoints.HeldSkillCandidates` (`:83-94`,
      still correct) are **deleted** and call it.
    - `EquippedActionIdsForTests` (in-memory store): `Both_grant_scopes_are_merged` (dropping either
      scope fails), `Only_skill_kind_grants_are_candidates`, `A_stored_loadout_wins_over_auto_equip`,
      `absent_falls_back_to_auto_equip`.
    - The Server's web-match and specimen-loadout tests pass **unchanged** — the rule moved, the
      behaviour did not.
  - Golden: byte-identical.
  - Verify: verify-change; `guard-dal.ps1`.
  - Files: `Data/Sqlite/RpgStore.Loadouts.cs`, `Server/WebMatchService.cs`, `Server/SpecimenLoadoutEndpoints.cs`, `tests/FusionRpg.Data.Tests/Items/EquippedActionIdsForTests.cs` (new).
- [ ] **CAI3.3 — `siege-loadout-wiring` B: real loadouts enter a district assault** · L · deps: CAI3.2 — **COMPOSITE SLICE LANDED** (lane `combat-ai-2`, post-checkpoint-4); the two production files are a denied path.
  Landed: `CompositeContainerEffectResolver` appended to the row's own in-fence Core file (`Actions/IContainerEffectResolver.cs`) — several resolvers asked in order, first non-empty wins, ordinal by the constructor's order, empty (never null) when nothing answers, and **0 bytes per call** measured after warm-up. Seven tests, including the short-circuit (a later resolver is never ASKED), the fall-through that is the composite's whole reason (`ConstructionActions.cs:70-77`'s four ids are unknown to the store bundle), and the order-is-the-constructor's-order determinism. 363 golden/container/siege/balance tests unmoved; `verify-change` **15100 passed / 0 failed** (the project is clean after checkpoint 4).
  **Owed, and a denied path:** `World/Turn/DistrictAssaultResolver.cs` (the composition `[store bundle, ConstructionActions.ContainerResolver]` and the `Resolve` call) and `Data/Sqlite/RpgStore.WorldTurns.cs` are under `Core/World/**` and `Data/**`, so no production host reaches the composite yet. The test file the next lane extends already exists. `Server/Program.cs:237` names `combat-ai.v1.json` by hand, which is why this program's later tuning publishes carry the same H7 constraint as `siege.v2.json`'s `:231` line.

  - Acceptance:
    - `BuildAnimateSetups` sets real `EquippedActionIds`; `Resolve` threads `actionCatalog`, the
      composite resolver, `runnerBindings`, `containersWithRunnerCoverage` and `equipEffectIdsFor`,
      and registers the extra defs in the existing `onEffectHostReady`. The providers are built inside
      the transaction that already builds `HubInputsFor`/`UnlockStateFor`.
    - `CompositeContainerEffectResolver` — first non-empty wins, ordinal, no allocation per call.
    - `With_no_provider_every_member_setup_carries_a_null_loadout` (identity, asserted because every
      existing siege test depends on it); `A_member_with_no_instance_id_never_consults_the_provider`
      (a provider that throws if called); `A_member_with_an_instance_id_carries_exactly_the_ids_the_provider_returned`;
      `Additional_held_actions_are_still_attacker_side_and_still_additive`;
      `A_real_container_id_with_only_the_construction_resolver_throws` (asserts the thrown message
      names the container); `The_composite_resolver_prefers_the_store_bundle_and_falls_through_to_construction`.
    - **`Siege_loadout_fixture_is_locked`** — siege's **first pinned outcome**: fixed roster, board and
      seed, a hand-built catalog and resolver **authored in the test, never read from `gk-data/packs/fusion/data/seed/**`**,
      hashing winner + per-side survivor keys.
    - **Siege supplies `AiActorClassOf`** from the setup it already holds (a legion member with an
      `InstanceId` is unique, a stack member is general). Each place supplies its own; a shared
      resolver would need a roster read inside Core, which the DAL boundary forbids.
    - **Doc drift fixed in this commit:** `BattleModels.cs:84-90` still says `EquippedActionIds` is
      *"purely carried data: nothing in `BattleEngine`'s round loop reads it today"*, contradicted by
      `BattleRunState.cs:540-585`, which compiles the loadout from it. This is the file whose contract
      the task edits, so the one-line correction belongs here.
    - The commit body states the cause, that **no committed golden moved**, and which spelling of the
      `RegisterInto` hand-off was chosen (the delegate, per the plan's decisions table).
  - Golden: no committed hash moves; `RulesetVersion` stays 5. Every existing test in
    `Core.Tests/World/Turn/` and `Core.Tests/Battle/Siege/` passes unchanged.
  - Verify: verify-change; `guard-dal.ps1`; `guard-actor-hub.ps1`; `guard-single-writer.ps1`.
  - Files: `World/Turn/DistrictAssaultResolver.cs`, `Actions/IContainerEffectResolver.cs`, `Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/tests/FusionRpg.Core.Tests/World/Turn/SiegeLoadoutWiringTests.cs` (new).
- [ ] **CAI3.4 — `delve-automated-wiring` A: `DownedAllyKeysOf` and the role policy** · M · deps: CAI1.9, CAI1.10 — **VIEW HALF LANDED** (lane `combat-ai-2`, reopened 2026-09-20).
  `IBattleView.DownedAllyKeysOf` exists as a DEFAULT implementation returning empty — which IS the row's byte-identity claim (no profile but `delve` has a downed state), and which is a stated deviation from the spec's "three implementors move" because an abstract member would need a 12-file edit to land atomically while nine of those edits would assert nothing. `BattleRunState` overrides it with the real read (`ActorState.WentDowned`, same-side, excluding the deciding actor); `FoggedBattleView`, `TraitAwareBattleView` and the nested `BloodthirstyView` forward it, and `DelveRolePolicyTests` proves the forwarding (the part that would otherwise be silently wrong, since `TraitView` wraps the run state) and the empty default. 2249 golden/expedition/siege/delve/stance/balance tests unmoved; verify-change 14953/4 pre-existing; doc-citations 0 HIGH.
  Second slice: the ROLE POLICY landed — `DelveBattle.RoleOf(isWaveActor, heldActions)` derives support/frontliner/striker from the closed nine-member `ActionTag` enum exactly as §4 states (Heal+Buff+Debuff vs Defensive+Construct buckets, striker otherwise, ties `support > frontliner > striker`), excludes the hand-built basic attack by its empty `ContainerId` (so no-loadout => striker), and returns the enemy row BEFORE any tally for a wave actor. Six tests, one per branch plus both tie directions and the no-blanket-precedence case, all with synthetic action ids. 2252 golden/expedition/siege/delve/stance/balance tests unmoved; verify-change 14956/4 pre-existing; audit-overflow 0; doc-citations 0 HIGH.
  **Owed, and re-measured by lane `combat-ai-3` (2026-09-21) — the blocker is now a DECISION with two named options, not a vague "needs a live `BattleRunState`".** `Downed_party_members_are_absent_from_LiveActorKeys_and_present_in_DownedAllyKeysOf` and `Ally_downed_falls_through_when_no_held_action_can_revive` each need BOTH halves of the same fact, and the two halves never meet today:
  - **The read half exists in fence.** `BattleRunState.cs` already carries four `internal static …ForTest` helpers (`:1507, :1521, :1535, :1547`) that construct a run state and read view members (`HeldActionsOf`, `EffectiveRungOf`, `PositionOf`, movement) — so "read a view member from a test" is an established house pattern.
  - **Why it cannot cover this.** Those helpers construct a *fresh* state and never run a round loop, and `BattleActorSetup` carries `MaxHp` but **no current-HP and no downed/status field** (`BattleModels.cs:9-44`), so no setup can start an actor downed — `WentDowned` is only ever set by combat. Combat runs inside `Resolve`, whose signature has **no view hand-out parameter** (0 matches for `IBattleView` / `Action<IBattleView>`), and the run state it builds is discarded.
  - **Nothing else observes it.** `grep -rn DownedAllyKeysOf` finds only the four implementors, `IBattleView`'s default and two test files — no trace, sink or decision record carries it (CAI2.4's records carry candidates and gate verdicts, not live keys).
  - **So the owner picks one of two**, both now concrete: **(a)** a trailing optional view probe on `Resolve` — the same shape as the `IStanceCheck? stance` seam `CAI3.1` just gained, and one call after the round loop suffices because the state still holds `WentDowned` at that point; its cost is test-only surface on a public API. **(b)** make `BattleRunState` `internal` — the recorded-position reversal `BattleRunState.cs:20-31` warns about; its cost is reversing a documented choice instead of adding a parameter.
  `RoleOf` also has no production caller yet, because its caller is `RpgHub.Resume`'s composition root in `CAI3.5` (`gk-core/src/FusionRpg.Server/**`, outside this lane).
  - Acceptance:
    - `IBattleView.DownedAllyKeysOf(actorKey)` exists — without it `ally-downed` is inert.
      `Downed_party_members_are_absent_from_LiveActorKeys_and_present_in_DownedAllyKeysOf`;
      `DownedAllyKeysOf_is_empty_under_every_profile_without_DownedOnDeplete` (the byte-identity claim
      for battle, expedition and siege), asserted **both** ways.
    - `Role_is_derived_from_held_action_tags_and_ties_break_in_the_stated_order` — against the closed
      `ActionTag` enum, never a corpus action id. `An_actor_with_no_loadout_is_a_striker`;
      `A_wave_actor_is_the_enemy_row_before_any_tally`.
    - `Ally_downed_falls_through_when_no_held_action_can_revive` — the honest state of the consumer
      gap, asserted rather than left as prose.
  - Golden: byte-identical; every new `Resolve` parameter is a trailing optional defaulting to null.
  - Files: `Actions/IBattleView.cs`, `Delve/Battle/DelveBattle.cs`, `gk-core/tests/FusionRpg.Core.Tests/Delve/Battle/DelveRolePolicyTests.cs` (new).
- [ ] **CAI3.5 — `delve-automated-wiring` B: `RpgHub.Resume` stops throwing** · L · deps: CAI3.4, CAI2.2 — **BLOCKED, and now with TWO measured blockers instead of a reading** (lane `cai2`, session `combat-ai-2b`, 2026-09-23).
  **Blocker 1 — its tuning half is UNSATISFIABLE against the shipped closed vocabulary.** The acceptance asks for *"Four `delve/*` rows published as `combat-ai.v2.json`"*, and the spec names them `delve/frontliner`, `delve/support`, `delve/striker`, `delve/enemy` (`spec-delve-automated-wiring.md:36-37,249-256`, and `:281` *"`PartyIndex is null` is `delve/enemy`"*). Measured this session: **`AiRole` declares exactly four members — `Default`, `Frontliner`, `Support`, `Striker` — and NO `Enemy`** (`gk-core/src/FusionRpg.Core/Actions/Ai/AiVocabulary.cs`, pinned by `CombatAiTuningTests.AiRole_has_four` at `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiTuningTests.cs:89`), while `CombatAiTuningLoader.ParseProfile` requires the key to split on `/` into a `place` and a `role` parsed against that closed vocabulary. I built all four rows, validated every selector/tag/condition/census name against the enums, and the build ABORTED on exactly one name: `AiRole.Enemy` is not declared. So three of the four keys ARE expressible (`delve/frontliner|support|striker` — `AiPlace.Delve` and those three roles all exist) and the fourth needs a **reviewed vocabulary change** (adding a fifth `AiRole` member, which breaks its own pinned count and its reason-stated test) **or an erratum naming a different key**. That is a specific owner decision, not a discovery gap. The `_note`/scoring/reserve half I prepared is otherwise spec-complete: siege's weights with `objective` seeded **0** (spec `:355`), reserve floors 150/300/100/100 `UNMEASURED` (`:356-357`), tiers by actor class and never by row (`:358`).
  **Blocker 2 — the headline half needs a view that a private nested class holds.** `RpgHub.Resume` throws because it has no *"real siege-ai-class automated `IIntentSource` for the raid's un-steered actors"*, and `DelveBattleSessionManager.Resume(matchKey, playerId, automated)` is real and takes one. Building `DelveAutomatedPolicy` means giving `CoreIntentPolicy` (whose public factory `Create` exists at `CoreIntentPolicy.cs:104`) an `IBattleView` for the delve's LIVE battle — and the only battle view is `BattleRunState`, a **private nested class inside `BattleEngine`** (`BattleRunState.cs:41`), whose own `:20-31` records that the nesting exists TO AVOID a visibility change. Reaching it is the same **owner decision** the todo's `R-OWNER` bullet already records for CAI3.1's and CAI3.4's last two tests.
  **Also owed, unchanged:** dep **CAI2.2 → `gk-core/src/FusionRpg.Data/**`** (the delve replay pin), and its acceptance's `NoCatchInLiveBattleCallStackTests` edit is a **protected pipeline path** the todo records `tvb58` being refused on twice. Verified this session: `RpgHub.Resume`'s throw text and `DelveBattleSessionManager.Resume`'s real signature, `CoreIntentPolicy.Create` at `:104`, `BattleRunState` at `:41`, and the `AiRole` member list above. See `tasks/reports/CAI3.5.md`.
  - Acceptance:
    - `RpgHub.Resume` contains **no** `throw new NotImplementedException`; a frozen delve fight resumes
      end-to-end through SignalR with un-steered parties and wave enemies acting.
      `DelveAutomatedPolicy` is the one composition root.
    - `Resume`'s existing refusals survive, each asserted: no row, already ingested, absent/incomplete
      trace. Losing them turns "refuses, never re-resolves blind" into a silent re-resolve.
    - **The freeze contract holds:** `Steering_away_still_cancels_the_task_rather_than_completing_it`
      asserts `RunTask.Status == TaskStatus.Canceled`, never `RanToCompletion`.
    - `A_steered_actor_that_declares_nothing_is_never_handed_to_the_automated_policy`;
      `A_timeout_on_a_steered_actor_is_recorded_as_a_timeout_decision`.
    - `NoCatchInLiveBattleCallStackTests` green with the router, the core policy, `StubIntentSource.cs`
      and `SiegeAiIntentSource.cs` on its list, and `RaidIntentSource.cs` off it.
    - Four `delve/*` rows published as `combat-ai.v2.json`, **every seeded number marked
      `UNMEASURED`**; `objective` seeds **0** for delve (a delve room has no Core to breach).
      **No lawn keys** in these rows.
    - **A fixed-seed delve fixture is locked** — the delve's first pinned outcome, authored in the
      test, not read from `gk-data/packs/fusion/data/seed/**`.
    - **The delve session supplies `AiActorClassOf`** from the party/wave setup it already holds.
    - **No production path anywhere passes `StubIntentSource` as the raid policy.**
  - Golden: byte-identical; `RulesetVersion` stays **5** — the battle/expedition switch is CAI3.6's
    single cause and the two must not land together (map hard edge H1).
  - Files: `Server/{RpgHub,DelveAutomatedPolicy,DelveBattleSessionManager,DelveBattleSession}.cs`, `Core/Delve/Battle/DelveBattle.cs`, `Core/Battle/BattleRunState.cs`, `gk-core/data/tuning/combat-ai.v2.json`, `tests/FusionRpg.Server.Tests/Delve/DelveAutomatedWiringTests.cs` (new), `NoCatchInLiveBattleCallStackTests.cs`.
- [ ] **CAI3.6 — `auto-policy-switch`: the profiled policy becomes the default (`RulesetVersion` 6)** · L · deps: CAI1.9, CAI1.12, CAI1.14, CAI2.2, CAI2.3 · **the one re-bless of this program**
  - Acceptance:
    - `RulesetVersion` is 6 with a v6 paragraph in its doc comment; `decisions.md:44` amended **in the
      same commit**.
    - Battle and expedition auto-resolve run the profiled policy through the router's single fallback
      chain, at **both** `BasicAttack` and `Reselect` — the second site asserted, because AUDIT M5 is
      the reason it can be missed.
    - **Exactly four** golden constants re-blessed, **exactly once**, with a dated ledger paragraph
      recording the triage.
    - `Golden_outcomes_hold_their_shapes`, every rate golden,
      `Goldens_do_not_depend_on_the_platform`, `Goldens_do_not_depend_on_the_content_stamp` green
      **and unedited**. Siege goldens unchanged.
    - `DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests`
      green and unchanged; `ProvePredictor` both scopes under `1e-4`. **A moved dominance baseline is
      a stop-and-report, not an expected outcome** — `DominanceGuard.cs:64` and
      `TerminationGuard.cs:100` call the economy-free `Predictor.Predict(a, b)`.
    - Every match logged after the bump carries a **non-NULL** `combat_ai_profile`; a pre-bump row
      (version 5, NULL profile) is refused by the sweep's existing version guard rather than
      re-resolved under the new policy.
    - `docs/research/combat-ai/predicted-delta-rulesetversion-6.md` exists with (a) why the hashes
      move, (b) the bounded behavioural prediction with its fixture-shape evidence, (c) what held,
      (d) the **measured** expedition reward-rate delta per tier including loyalty-threshold crossings,
      (e) the twin and baseline results. Per ruling **D8 there is no compensating expedition retune**,
      now or as a follow-up; the number is recorded because the economy's owner needs it.
    - **`WebMatchService` supplies `AiActorClassOf`** for battle and expedition, from the setup it
      already builds. With it unwired the resolver yields `Unique`, which CAI1.9 pins.
    - `EngineVersion` does **not** move — the policy is not the engine — and the writeup says so.
    - No test asserts *what* the new policy decides, and no test asserts an expedition reward total.
    - Measured 2026-09-27 (recovered from CAI1.12's own evidence fragment, which a later
      `cai-sink` session overwrote without restating it): `BattleRunState.EffectFootprints` still
      has **no consumer**. `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` holds exactly three
      occurrences - the field declaration (281), the setup assignment (729), and the builder
      (840) - and nothing reads it. This row is the first consumer, which is why the negative
      result belongs here rather than in a row of its own: the map is built and frozen and inert
      until CAI3.6 lands. Same pass confirmed `interface IDeclaresExecution` has exactly one
      declaration, at `gk-core/src/FusionRpg.Core/Effects/EffectModels.cs:139` - its spec'd home, so
      CAI1.12's fence blocker did close without leaving a second copy behind.
  - Golden: **four hashes re-blessed, one cause, one commit.**
  - Verify: `.\scripts\test-fast.ps1 -AllDefault` (one of the three sanctioned occasions).
  - Files: `Battle/BattleModels.cs`, `Battle/BattleRunState.cs`, `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs`, `docs/architecture/decisions.md`, `docs/research/combat-ai/predicted-delta-rulesetversion-6.md` (new).

### Checkpoint CP3
- [ ] `RulesetVersion` is 6; exactly four hashes re-blessed exactly once; the ledger paragraph records the triage.
- [ ] The predicted-delta writeup carries the measured expedition delta per tier.
- [ ] Dominance confirmed unchanged; `ProvePredictor` under `1e-4`; full suite green.

---

## Wave 4 — the lawn (injector adapters over the same core)

**Entry condition (edge E1):** `BCU0.1` (`lawn-signal-ownership`) has landed in the documents.
**`CAI4.7` additionally needs** the lawn plan's `gk-core/data/tuning/lawn-perf-budget.v1.json` to exist so
`lawn.ai.decide` has a budget share to read.

- [x] **CAI4.1 — `lawn-actor-view`: an `IBattleView` over the board** · L · deps: CAI1.1, BCU0.1 — **DONE 2026-09-23 (lane `cai2`, session `combat-ai-2b`)**: all nine acceptance lines re-verified with printed readings, and the row's own recorded reason for staying open — *"without it no production host reaches the view"* — was answered by CAI4.8. **Every line, and what proved it:** (1) the three Core files are under `Actions/Ai/Lawn/` and `ILawnBoardViewTests` is green and **unmodified** — **6 passed / 0 failed**; (2) side comes only from the oracle, (3) `_resolve` once per (actor, frame), (5) the null/`PositionOf`/`HpMilli` answers, (6) the twelve-member set, (7) no fog, (8) the constant revision seam, (9) `StubIntentSource` unmodified driving it to a real `ActionIntent` — **18 passed / 0 failed** across `LawnBattleViewTests` + `LawnDerivedCacheTests` + `LawnRelationChainTests`, and `git log -1 -- gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs` is **f46efadaf, 2026-08-28**, i.e. this program never touched it; (4) with no decision edge the census delegate is never invoked and a repeat `ViewFor` allocates nothing — **10 passed / 0 failed** in `LawnActorViewHostTests`. **The production host, named:** `InjectorLoop` → `LawnDecisionHost.Tick` (CAI4.8) → `LawnActorViewHost.ViewFor(perspective, frame)`, one view per due actor's own side per frame; before that wiring, `grep -rn "LawnActorViewHost.ViewFor" src/` outside the file itself returned nothing. **One stated deviation, not an acceptance line:** `statusMaskOf` reads **0**. The spec's table names `EffectRuntime.Status` as its source, and measured there is no per-ptr status-mask producer to read — `SimEffectHost.StatusMaskOf` is an INSTANCE property of Core's sim host set by nobody, `StatusRuntime` exposes instances rather than a mask, and the injector has no `statusBit` mapping either (re-verified by grep this segment). Inventing a bit-interner would fork the compiler's own mapping, so the absence is stated in the class doc and `FactsOf.StatusMask` under-reports until a producer exists. **Superseded status (kept for history):** **CHAIN SLICE LANDED** (lane `combat-ai-2`, resumed after the mega-merge; `eaafeaaa` / this commit).
  **Fence correction:** my earlier classification of this row as wholly blocked was too broad. BCU0.1 is `[x]` closed and CAI1.1 is done, and **three of the row's five files are in-fence** — `Actions/Ai/Lawn/{LawnBattleView,LawnRelationChain,LawnDerivedCache}.cs` and the two test files; only `Injector/Effects/LawnActorViewHost.cs` is not.
  Landed: `LawnRelationChain` composes `SpecimenOwnershipOracle` and `MechanicalOwnSideOracle` specimen-first, first non-null wins, short-circuits (asserted: the mechanical link is not even asked when the specimen link answers), and returns null for an unknown ptr rather than defaulting it — `LawnUnitViewFactory` owns that resolution. Both links are required; the constructor takes them as two NAMED parameters rather than the spec's array, so the precedence is structural rather than positional convention (stated deviation). 4 tests; `ILawnBoardViewTests` green and unmodified; 204 BattleGolden/Lawn/BalanceGuard green; verify-change 14964/4 pre-existing.
  Cache slice: `LawnDerivedCache` landed — one `_resolve` per `(ptr, revision)` per frame, frame-scoped AND revision-guarded (a mid-frame bump costs exactly one further resolve for that actor and none for others, counted), `BeginFrame` drops the memo, and a constant revision seam is asserted to be frame-scoped only (the pre-`actor-liveness-refresh` behaviour, stated rather than implicit). 6 tests; the row's own Verify filter 10/10; 210 BattleGolden/Lawn/BalanceGuard green; verify-change 14970/4 pre-existing (numbers, not the exit code).
  View slice: `LawnBattleView` landed — all twelve `IBattleView` members answered per the spec's own table, side read ONLY through the oracle (with the raw-board-side read asserted absent from the file, so the mutation fails both halves), the census delegate invoked only at a decision edge, N derived + N gate reads sharing one Hub resolve, `HpMilli` a bounded ratio (0 at zero max, 1000 above max), the downed read answered BY this class rather than inherited (`DeclaringType` asserted), no fog, and `StubIntentSource` unmodified driving it to a real `ActionIntent`. 8 tests; the row's Verify filter 18/18; `ILawnBoardViewTests` green and unmodified; 218 BattleGolden/Lawn/BalanceGuard green; verify-change 14978/4 pre-existing; guards 0 HIGH. **All three Core files of this row are now complete.**
  **INJECTOR HOST LANDED (lane `cai2`, session `combat-ai-2b`, 2026-09-23) — the row stays open on ONE named dependency, not on a path.** `Injector/Effects/LawnActorViewHost.cs` now supplies all seven seams and caches one view per `(perspective, frame, census instance)` — the session boundary was recorded as a denied path, but `gk-fusion/src/FusionRpg.Injector/**` is in this lane's fence. Seams wired to their production sources: `censusOf` → `InjectorBoardSnapshot.Capture` (frame-cached); `relation` → `SpecimenOwnershipOracle` over `CheatState.TryGetSpecimenController` composed specimen-first with `MechanicalOwnSideOracle`, built PER perspective (one oracle cannot answer for both sides — that is the point of the perspective key); `unitOf` → `LawnUnitViewFactory` over the registry's live HP pair (`thePlantHealth`/`thePlantMaxHealth`, `Bridges.ZombieCombatFields.GetHp`/`GetMaxHp`); `derived` → `InjectorStatusBridge.ResolveDerived`, which `LawnDerivedCache`'s own parameter doc names for production, with the revision seam a CONSTANT as the row records until `actor-liveness-refresh`; `elementOf` → `LawnElementResolverHost.Resolve` with battle's own `(int)ElementPrimary : 0` shape (`BattleRunState.cs:971`). **10 tests** (`gk-fusion/tests/FusionRpg.Injector.Tests/LawnActorViewHostTests.cs`): same-instance on a repeat call, a new frame rebuilds, a NEW CENSUS in the same frame rebuilds (the reason a frame-only key is wrong), two perspectives get different views, `Clear`, the perspective really deciding which side is mine (mirror images of one census), hypnosis (a zombie-side mind-controlled unit fighting for the player), an unknown ptr never reading as mine, and the census really being read. The census is fed through `LawnActorViewHost.CensusOf` — the shipped `ActorHudCache.Build` idiom — because the production read needs a live Unity runtime. **`77 passed / 3 failed`** in the project; all three failures are the pre-existing stale `LawnBasicAttackFeatureFlagTests` filed as `CAI-find-1`, and `guard-injector-compile` is OK (not a skip). **Updated 2026-09-23 (lane `cai2`): residual (1) is ANSWERED.** `LawnActorViewHost.ViewFor` now has a production caller — `InjectorLoop` → `LawnDecisionHost.Tick` (CAI4.8) → `ViewFor`, one view per due actor's own side per frame — so the view is reached by a live tick, not only by tests. **Two residuals, both named:** (1) ~~`CAI4.8`'s frame slot is the only production caller~~ **DONE**; (2) **the status-mask seam has no producer** — measured, `SimEffectHost.StatusMaskOf` is an INSTANCE property of Core's sim host set by nobody in `src/`, and `StatusRuntime` exposes instances rather than a mask, so `statusMaskOf` reads `0` (a stated absence in the class doc, not a second bit-interning mechanism) and `FactsOf.StatusMask` under-reports until a producer exists. `heldActionsOf` returns empty until `CAI4.3`, which the spec endorses in its own words. **Superseded (kept for history):** the host *was* recorded as a denied path; it is not. See `tasks/reports/CAI4.1.md`. Two stated deviations from the Core slice stand: `AggressionOf` forwards the composed value and leaves saturation to `CandidateScorer.EffectiveTier`, and `LiveActorKeysFor` returns the absolute list because a lawn has no fog and no view-order decorators.
  **Owed (historical, now superseded):** `LawnBattleView` (its twelve `IBattleView` members, each with the spec table's stated answer) and `LawnDerivedCache` (one `_resolve` per (actor, frame); a mid-frame revision bump costs exactly one further resolve for that actor and none for others), plus their tests — all in-fence. **One acceptance line is now stale for whoever takes the view:** it says "exactly the TEN members this view implements", but the interface has since gained `LiveActorKeysFor` (CAI1.11) and `DownedAllyKeysOf` (CAI3.4), so the view must answer TWELVE, and must answer the downed read explicitly rather than inherit CAI3.4's default-empty (that line's own "never defaulted").
  - Acceptance:
    - The three new Core files are under **`gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/`**, *not* under
      `Match/Ai/`, and `ILawnBoardViewTests.Nothing_under_Match_Ai_may_read_the_board_itself` is green
      and **unmodified** — its pattern list is not widened and its scope is not carved out.
    - Side comes **only** from the oracle: a unit whose raw board side is `zombie` but whose oracle
      answers `Ally` reads as an ally; a ptr no oracle knows reads as the other side. No read of the
      raw board side anywhere in the file (grep-checkable). **Mutation to kill:** replace `SideOf`'s
      oracle read with `BoardEntitySnap.Side` — test 1 must go red.
    - `_resolve` is called **at most once** per (actor, frame) across N `DerivedOf` + N gate checks; a
      mid-frame revision bump causes exactly one further resolve for that actor and none for others.
    - With no decision edge the board-snapshot delegate is **never invoked** and the frame allocates
      nothing; a second `ViewFor(same perspective, same frame)` allocates nothing.
    - `GarrisonedStructureKeyOf` and `ObjectivePositionOf` are null for every actor by stated decision;
      `PositionOf` is non-null for every live actor; `HpMilli` is 0 at `hpMax = 0` and 1000 above max.
    - `IBattleView`'s member set is exactly the ten this view implements — a new member must be
      answered here, never defaulted.
    - **The view declares no fog**, stated in the file: `FoggedBattleView` fog-gates `AggressionOf`
      because a target's aggression is board information, so a lawn stealth status has no effect here.
      A stated decision, not an omission.
    - The derived memo's revision seam returns a constant until `actor-liveness-refresh` (lawn plan)
      lands; frame-scoped is correct for a single decision. **This is the second precondition on
      CAI5.3's default-on flip**, and the reason the feature ships off.
    - **`StubIntentSource`, unmodified, runs against this view in a Core test and returns a real
      `ActionIntent`.**
  - Golden: byte-identical — no battle, siege or delve file edited. Run the filter and state the result.
  - Files: `Actions/Ai/Lawn/{LawnBattleView,LawnRelationChain,LawnDerivedCache}.cs` (new), `Injector/Effects/LawnActorViewHost.cs` (new), two new test files.
- [ ] **CAI4.2 — `lawn-held-actions` A: the per-match frozen sets** · M · deps: CAI1.1, BCU0.1 · *(no dependency on CAI1.6/1.8 — plan correction 3)* — **CORE HALF LANDED** (lane `cai4`, 2026-09-22). `gk-core/src/FusionRpg.Core/Match/Ai/LawnHeldActionSets.cs` holds the per-match store: `PushSpecies`/`PushBound` freeze once per key per match through `FrozenActionSet.FreezeAtRunStart`, compile every assembled id through the supplied `ActionCatalog`, order once by `ActionTagPreference.Compare`, and return the frozen set by reference; `HeldFor(speciesKey, boundInstanceKey)` prefers the instance key and returns **empty** for an unknown pair (never the basic-attack row); `BeginMatch()` is the lawn's `RefreshAtNextRunStart` boundary; an id the catalog does not know refuses the **whole** key loudly, once, and every later push returns the same empty refusal without reporting again. 11 tests, all five acceptance lines of this row run and green; the planted violation (a second push re-assembling) kills three of them. `verify-change` exit 0, **15560 passed / 0 failed**; `guard-dal.ps1` exit 0; goldens 5/0; Balance project 221/0. **Updated 2026-09-22 (second segment):** the row's last Core-testable line was still open — spec Success criterion 5's *"`StubIntentSource` answers `None` for it"* — and it now lands as `An_unknown_species_answers_None_through_the_shipped_stub_policy` plus its mirror `A_species_with_a_pushed_set_gets_past_step_one_and_asks_the_board` (13 tests, up from 11; the planted removal of the stub's `count == 0` early return kills the new test). The lane's paths were also re-verified at the merged head after `features/mega-merge` was picked up: **15698 passed / 0 failed across 40 project runs**, and no file this row owns and no dependency it reads was touched by that merge. **Row stays open on the program's own precedent (CAI2.5, CAI4.1): no production host reaches the store until CAI4.3 lands `LawnHeldActionRegistry` + the Cold push + the `InjectorEntityRegistry` drops — `gk-fusion/src/FusionRpg.Injector/**` and `gk-core/src/FusionRpg.Server/**`, outside this lane.** Two stated deviations: the tests live in `tests/FusionRpg.Core.Balance.Tests/CombatAi/` (this lane's fence does not include `gk-core/tests/FusionRpg.Core.Tests/**`, and a new test project cannot be registered from inside the lane), and the store is fed the **raw** inputs (a `SpeciesBasicsRow` + live grant rows) rather than a pre-compiled list — `CompiledAction` carries an `ICompiledPredicate` tree and cannot ride the Cold push's JSON, so the same Core type runs the assemble→compile→order pipeline on the injector side. See `tasks/reports/CAI4.2.md`.
  - Acceptance:
    - Assembling the same `(basics, liveGrants)` twice yields the same ids in the same order.
    - A grant added after the freeze does **not** appear in `Snapshotted()`; it does after
      `RefreshAtNextRunStart`. **Mutation to kill:** make `Snapshotted()` re-assemble — that test must
      go red.
    - N ptrs of the same species share **one** `FrozenActionSet` instance; a Bound instance key
      resolves to its own set, not its species' set.
    - A species with no pushed set yields an **empty** held list, never the basic-attack row.
    - A compile failure reports **once** and returns empty on every later call; an id the catalog does
      not know is refused loudly, never silently dropped.
  - Golden: byte-identical.
  - Verify: verify-change; `guard-dal.ps1` (zero SQL outside `FusionRpg.Data`).
  - Files: `Core/Match/Ai/LawnHeldActionSets.cs` (new, **landed**), `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs` (new, **landed** — the row's original `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside this lane's fence).
- [ ] **CAI4.3 — `lawn-held-actions` B: the Cold push and the ptr binding** · M · deps: CAI4.2 — **NEEDS A ROUTING/RULING DECISION ON THE WIRE FORMAT (sharpened by lane `cai3`, session `combat-ai-3`, 2026-09-23); the registry, the command case and the additive drop are all in fence and ready to land the moment the payload shape is named.**
  - **THE DECISION ASKED, in one line:** *does the Cold push carry the COMPILED held-action list — which needs a wire form for `CompiledAction`'s `ICompiledPredicate` condition tree, and therefore a DTO that lives in `gk-core/src/FusionRpg.Contracts/**` (outside every combat-ai lane's fence) plus a second producer of the compiled predicate — or does it carry the RAW rows and let the injector compile through the one `ActionCompiler`, which the spec's own "the injector only binds a ptr to a set Core produced" wording does not contemplate?*
  - **REFRAMED 2026-09-23 (lane `cai3`): the DESIGN question is already answered by the spec, so this is a ROUTING decision, not a choice between two shapes.** `spec-lawn-held-actions.md:73-80` says in numbered steps that *the server* assembles (`:75`), *resolves each `AssembledAction.ActionId` to a `CompiledAction` through the same `ActionCatalog` path battle uses* (`:76-78`), sorts (`:79`) and *"pushes the compiled list"* (`:80`); its Boundaries section repeats it (*"push from the server keyed by species / instance, never by ptr"*) and `:239` adds *"the injector only binds a ptr to a set Core produced."* So the compiled-list payload (option (a)) IS the spec's answer, and the raw-row option is an **erratum**, not a free alternative. **What actually blocks the row is one file's fence:** the wire form needs a DTO for `CompiledAction` (21 members, `Condition` an interned tree) plus a deserializer, and a typed DTO belongs in `gk-core/src/FusionRpg.Contracts/**` — which no combat-ai lane may edit. **So the manager's action is to grant that path to a combat-ai lane or route the DTO to a lane that holds it**, not to pick between (a) and (b). The measurement that makes the raw-row option look attractive at all — the injector already configuring `RungPolicy.Table` from `action-rungs.v4.json` (`RpgHost.cs:278`), so `ActionCompiler.Compile` *could* run injector-side — is recorded below as the erratum's own supporting evidence, not as a recommendation.
  - **Why it is not mechanical, measured this session.** `spec-lawn-held-actions.md` §"Where the set comes from" steps 1-4 say the SERVER assembles, compiles, sorts and pushes "the compiled list". `CompiledAction` (`gk-core/src/FusionRpg.Core/Actions/CompiledAction.cs:31-52`) is a 21-member record whose `Condition` is an `ICompiledPredicate` **interned tree** and whose `Costs`/`Scopes`/`Targeting`/`Envelope` are compiled shapes; `grep -rn "CompiledAction" gk-core/src/FusionRpg.Contracts/` returns **nothing**, so no DTO for any of it exists today. A faithful JSON form therefore needs a predicate-tree DTO and a deserializer that rebuilds the SAME interned slots `ActionCompiler` builds — i.e. a second producer of the compiled predicate, which is the drift class this program exists to prevent. An untyped dictionary payload (`CommandDto.Payload` is `object?`) would move that whole schema onto the injector's parse side with no shared type to keep the two ends honest.
  - **Option (b) is FEASIBLE, and that is the measurement that makes this a choice rather than a wall:** the injector already configures the rung ladder it would need — `RpgHost.cs:264-272` loads `action-rungs.v4.json` into `RungPolicy.Table`, the same file the server loads — so `ActionCompiler.Compile(row, costs, scopes, containerAtomIds, boardAvailable, rungTable)` can run injector-side through the ONE compiler, with the raw `SpeciesBasicsRow`/`ActionGrantRow` inputs the spec already names as the server's own inputs. What option (b) costs: the payload grows to raw rows, the container atom ids must be pushed too (or every container action refuses at compile), and the injector becomes a second caller of `ActionCompiler` — the same implementation, but a second place a compile can fail whose refusals must be reported once (the `LawnBasicAttackRow.TryGet` posture).
  - **Option (c), named so it is not rediscovered:** push only a NARROWED projection (action ids + the compiled facts the policy reads). Rejected on inspection: `CoreIntentPolicy` reads `Condition`, `Costs`, `Envelope` and `Targeting`, so a narrowed projection changes decision semantics rather than the transport.
  - **Nothing else about this row is blocked.** The registry (`Injector/Effects/LawnHeldActionRegistry.cs`), the `CheatCommandRunner` case, and the ADDITIVE `InjectorEntityRegistry.Remove`/`Clear` drops are all in this lane's fence and need only the payload shape; the ptr→key resolution reuses `CheatState.ResolveBoundInstanceId` and the lawn species index the spec's own table names.
  - Acceptance: one more Cold push in the shape of `PushPatronAsync`; one more `CheatCommandRunner`
    command case beside the existing non-debug cases; `Remove(ptr)` drops **exactly** that ptr's entry
    and no other, a reused ptr address starts unbound, `Clear()` drops every entry. The
    `InjectorEntityRegistry` edit is **additive** — CAI2.5's ring drop stays.
  - Golden: byte-identical.
  - Files: `Injector/Effects/LawnHeldActionRegistry.cs` (new), `Server/RpgHub.cs`, `Injector/CheatCommandRunner.cs`, `Injector/Effects/InjectorEntityRegistry.cs`.
- [x] **CAI4.4 — `lawn-cost-authority` A: one rung derivation for battle and the lawn** · M · deps: CAI4.2 — **DONE** (lane `combat-ai-2`, 2026-09-20).
  Landed: `Actions/Unlock/EffectiveRungResolver.cs` holds the body (resolution order unchanged: the
  actor's `UnlockState.Held` entry through `UnlockLadder.EffectiveRung` with the swung row's `RungBand`,
  then the SWUNG row's authored `Rung`, then the catalog's, then `floorWhenUnknown`), and
  `BattleRunState.EffectiveRungOf` is a **delegation** with the same inputs and `floorWhenUnknown: 0`
  (battle's own `?? 0` tail) — so it is byte-identical by construction, and the goldens are the proof:
  **511 passed, 0 failed** across BattleGolden, ExpeditionResolver, Siege, Unlock, CostLedger,
  ActionSchedule, KernelAllocation and every BalanceGuard, with `audit-overflow --targets A3` exit 0.
  The held-row read arrives as a `Func<string,string,CompiledAction?>` delegate, so the lawn can pass
  its own lookup rather than the extractor growing a view dependency.
  **Owed:** nothing — the test file landed. `EffectiveRungResolverTests` has 5 cases: the seven-way
  spread compared against a TRANSCRIBED copy of the pre-extraction body (a per-case literal would not
  catch a reordered step), the authored-rung and `min(earnCount, rungCap, band.Ceiling)` cases, the
  authoring-beats-catalog case, and the two **planted violations** — floor 0 throws
  `ArgumentOutOfRangeException` for an uncatalogued id while floor 1 pays, and `rungOf: (_, _) => 1` is
  executed and shown to disagree with rung 7. `grep -rn "UnlockLadder.EffectiveRung(" src/` finds exactly
  **one** code call site (`EffectiveRungResolver.cs:62`), so the "exactly one rung derivation" claim is
  checked rather than asserted. 493 golden/expedition/siege/unlock/balance tests unmoved;
  audit-overflow exit 0. Drive-by: six pre-existing stale `BattleRunState.cs:924-931`/`:930-931` citations
  in `spec-aggression-tier-map.md` were re-pointed to the real `ai.aggression` composition at
  `:988-996`, found while checking this change's own line shift.
  See `tasks/evidence-fragments/CAI4.4.md`.
  - Acceptance:
    - `EffectiveRungResolver.Resolve` with `floorWhenUnknown: 0` matches today's
      `BattleRunState.EffectiveRungOf` over a spread of (held / not-held / catalog / no-catalog, with
      and without unlock state). **Exactly one rung derivation exists in the repo.**
    - A held action with authored rung `r` and no unlock state prices at `r`; with an unlock state
      holding `earnCount` it prices at `min(earnCount, rungCap, band.Ceiling)`.
    - An id with no held row, no catalog and `floorWhenUnknown: 1` returns **1** and
      `CostLedger.TryPay` for it does not throw. **Planted violation:** setting the lawn floor to 0
      makes that test throw `ArgumentOutOfRangeException` — the guard is load-bearing.
    - **Planted violation:** reinstating `rungOf: (_, _) => 1` makes the authored-rung test fail for
      `r > 1`.
  - Golden: no battle golden should move — the extraction is a delegation with the same inputs and the
    same `floorWhenUnknown: 0`. **If one moves it is a defect in the extraction, not a re-bless.**
  - Verify: verify-change; `audit-overflow.py --targets A3`.
  - Files: `Core/Actions/Unlock/EffectiveRungResolver.cs` (new), `Core/Battle/BattleRunState.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/EffectiveRungResolverTests.cs` (new).
- [ ] **CAI4.5 — `lawn-cost-authority` B: the lawn ledger prices held actions** · M · deps: CAI4.4 — **CORE HALF LANDED (lane `cai2`, session `combat-ai-2b`, 2026-09-23); the injector half is blocked on the SAME thing CAI4.3 is.**
  **The row contradicted itself, and the contradiction is now resolved in the direction its own test path forces:** it puts the row source at `Injector/Effects/LawnCostRowSource.cs` while putting its test at `gk-core/tests/FusionRpg.Core.Tests/Actions/LawnCostAuthorityTests.cs`, and a Core test project cannot reference the injector. Measured: `ActionCostRow` is Core (`ActionRow.cs:141`) and `CompiledActionCost` is Core (`CompiledAction.cs:8`), so the BUILD belongs in Core and the injector's file becomes the thin caller — which is what landed: `gk-core/src/FusionRpg.Core/Actions/LawnCostRows.cs` (`Union`, taking the primitive `(ActionId, Costs)` pair so no test has to hand-build a fourteen-member `CompiledAction`, and passing a pre-existing key's list through BY REFERENCE so "the basic attack's rows are unchanged" is a property of the function rather than of a caller's copy). **5 tests in the row's own path, 5 passed / 0 failed**; `BattleGolden` **5/0**; `guard-actor-hub` exit 0. **Owed:** the injector caller (`LawnBasicAttackCostCharger.cs`'s union + the real `rungOf` + the cached `derivedFor`) is blocked because the held sets it must read come from module 16 — i.e. from `LawnHeldActionRegistry`, which needs an `ActionCatalog` the injector has no feed for (CAI4.3's blocker, named there). The acceptance's *charged-amount* half is proven at the union's keying rather than through `TryPay` for the same reason: there is no production composition to charge through yet. See `tasks/reports/CAI4.5.md`.
  - Acceptance:
    - The lawn `CostLedger` takes the **union** of basic-attack rows and held-action rows, a real
      `rungOf`, and a cached `derivedFor`.
    - `Adding held-action keys leaves the basic-attack id's rows and charged amount identical` — the
      basic attack's charged amount, its once-per-swing gate and its observer hooks are unchanged,
      **proven not argued**.
    - A held action's shortfall refuses that action and charges nothing; the next basic-attack swing
      still charges (validate-all-then-consume across the union).
    - `derivedFor` is invoked **once per (actor, frame)** across one decision's N gate checks; with an
      empty memo it is invoked per call exactly as today.
  - Golden: byte-identical.
  - Files: `Injector/Effects/LawnBasicAttackCostCharger.cs`, `Injector/Effects/LawnCostRowSource.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Actions/LawnCostAuthorityTests.cs` (new).
- [ ] **CAI4.6 — `lawn-cast-activation`: the cast reaches the Funnel** · M · deps: CAI4.5 — **CORE (PURE) HALF LANDED** (lane `cai4`, 2026-09-22); **the remaining half is split, and ONE side of the split is outside this lane's fence** (lane `cai2`, session `combat-ai-2b`, re-read 2026-09-23). **Measured:** `CastOrigin` appears NOWHERE in `src/` except two doc comments in `Match/Ai/LawnCastPlan.cs` (`:23`, `:48`) that describe it as owed, and `src/FusionRpg.Injector/Effects/LawnCastActivation.cs` does not exist. **Out of fence (the blocker):** `gk-core/src/FusionRpg.Contracts/EffectDtos.cs`'s additive default-`false` `CastOrigin` field, plus the two charge/counter refusals that read it — and the acceptance's own mutation test (*delete the `if (ev.CastOrigin) return true;` early return and that test must go red*) is written against exactly that field, so it cannot be satisfied by the in-fence half alone. **In fence and READY (named so the next holder does not re-derive it):** `Injector/Effects/LawnCastActivation.cs` (the fire site — without it nothing calls `LawnCastPlan`), `Fire`'s depth-0 guard and the fail-closed liveness re-check (`Injector/Effects/LawnBasicAttackCostCharger.cs`), and their tests. Landing only that half would build a fire site that CANNOT stamp the discriminator, i.e. one that charges a cast event as if it were damage — which is the failure the field exists to prevent. So the row waits on the Contracts field rather than on work. **Superseded tail (kept for history):** `Match/Ai/LawnCastPlan.cs` is the ordered plan: pay on commit → start the cooldown on the shared `CooldownLedger` → build the `OnActivate` event (actor, post-decision target, tick, `HitCount` 1) — and an `InsufficientFunds` outcome is a **total** refusal (no cooldown, no event, nothing flushed), with `ShortfallResourceId` carried so the player is told which resource was short. 7 tests in `tests/FusionRpg.Core.Balance.Tests/CombatAi/`; the planted violation (arming the cooldown before paying) kills the refusal test; `verify-change` exit 0, **15672 passed / 0 failed** (which includes the whole `FusionRpg.Core.Effects.Tests` contract suite, the row's effects-contract clause); `guard-funnel-delta` / `guard-single-writer` / `guard-actor-hub` exit 0; goldens 5/0; Balance 277/0. **Owed, all outside this lane:** the `EffectEventDto.CastOrigin` discriminator and its two refusals (Contracts + Injector — the plan states its own side of the contract in its doc comment: every event it returns IS a cast, so the fire site stamps the flag), `Fire`'s depth-0 guard and the fail-closed liveness re-check, and the fire site itself (`LawnCastActivation`), without which nothing calls the plan. No tuning publish is owed: the cost is the action's own cost rows, the cooldown its envelope, and `HitCount` is 1. See `tasks/reports/CAI4.6.md`.
  - Acceptance:
    - `LawnCastPlan` is pure and ordered **pay → cooldown → event**; **planted violation:** emitting
      the event before paying fails. An `InsufficientFunds` outcome starts no cooldown and produces no
      event.
    - The built event has `Trigger == EffectTriggers.OnActivate`, `HitCount == 1` and the
      post-decision target.
    - `CastOrigin` is `true` on a cast event and `false` on a default-constructed `EffectEventDto`;
      **a synthetic `OnDamageDealt` record with `CastOrigin == true` and `IsFirstOfSwing == true`
      charges nothing**, the same record with `CastOrigin == false` charges once, and it does not
      increment CAI4.7's swing counter. **Mutation to kill:** delete the
      `if (ev.CastOrigin) return true;` early return — that test must go red.
    - `Fire` entered at depth 1 **refuses, reports, and releases its token**; a dead actor or target
      ptr skips without throwing and releases the token.
    - `FoundationContractVersion.Current` unchanged by the added field.
  - Golden: the one shared-surface change is an additive default-`false` field on `EffectEventDto`.
    **Verify rather than assume** — run the battle golden filter plus the effects contract tests and
    state the result either way.
  - Verify: verify-change; `guard-funnel-delta.ps1`; `guard-single-writer.ps1`.
  - Files: `Core/Match/Ai/LawnCastPlan.cs` (new, **landed**), `Injector/Effects/LawnCastActivation.cs` (new, **owed** — outside this lane), `Contracts/EffectDtos.cs` (**owed** — the `CastOrigin` field), `Injector/Effects/LawnBasicAttackCostCharger.cs` (**owed**), `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCastPlanTests.cs` (new, **landed** — the row's original `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside this lane's fence).
- [x] **CAI4.7 — `lawn-cast-trigger` A: trigger, budget, token pool (pure)** · L · deps: CAI4.1, CAI4.6, **lawn plan `lawn-perf-budget.v1`** — **DONE 2026-09-23 (lane `cai2`, session `combat-ai-2b`)**: both owed acceptance lines landed and were re-verified this segment, so the row closes. **Line 6 (the section):** `grep -n "LawnAiDecide\|SectionCount =" gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` reads `AiDecide = 25`, `LawnAiDecide = 26`, `const int SectionCount = 27`, with `"ai.decide"` and `"lawn.ai.decide"` in `SectionNames`; `PerfProbeTests` **8 passed / 0 failed** (including `PerfSections_match_the_enum_the_names_and_this_bound`, whose planted `SectionCount = 25` kills it). **Line 7 (the file):** the lawn section is in `gk-core/data/tuning/combat-ai.v2.json` — the revision is **v2**, not the `v3` this row predicted, because the delve rows that would have been v2 aborted on `AiRole.Enemy` (CAI3.5's blocker) — and `CombatAiTuningRevisionTests` **5 passed / 0 failed** reads the four keys back through the SHIPPED parser (7 / 50 / 10 / `"lawn.ai.offset"`) and asserts an absent lawn section is refused. **The pure classes' own 33 tests** re-ran green in their NEW home: `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/` — `CAI-tests-1` moved them from `tests/FusionRpg.Core.Balance.Tests/CombatAi/` in this same lane, so the path this row records is superseded by that move (the file NAMES are unchanged and all 33 pass). **Its injector half is `CAI4.8`'s and is four-sixths landed** (switch, frame slot, registry drops, the section and its declared share). **Superseded status (kept for history):** **CORE HALF LANDED** (lane `cai4`, 2026-09-22). The three pure classes are in: `Match/Ai/LawnDecisionTrigger.cs` (the two OR'd triggers, the carry clamp, the post-cast lock that does **not** freeze the counter, the `SeededRng.DeriveStream` offset, `Remove`/`Clear`), `Match/Ai/LawnDecisionBudget.cs` (FIFO by `(due tick, ordinal ptr)`, overflow carried, no starvation past `ceil(due/budget)`), `Match/Ai/LawnCastTokenPool.cs` (leases, idempotent release, timeout backstop reclaiming **at** the timeout). 33 tests in `tests/FusionRpg.Core.Balance.Tests/CombatAi/` — the in-fence test project, since `gk-core/tests/FusionRpg.Core.Tests/**` is outside this lane. All three planted violations kill their named test (dropped `CastOrigin` check → 1 red; `CarryCasts = 2` → 2 red; `Math.Min` for the carry → 1 red), and the tree is 33/33 green after revert. The four structural values are code `const`s each carrying the `tunables-ssot.md` §1 comment (`CarryCasts` 1, `DecisionsPerFrame` 8, `CastTokens` 4, `CastTokenTimeoutTicks` 20); the four **balance** values arrive as `LawnDecisionTrigger` constructor parameters documented with their tuning keys, so no balance number lives in code. `verify-change` exit 0, **15626 passed / 0 failed**; `audit-overflow --targets A3` exit 0; `guard-actor-hub` OK; goldens 5/0; `CombatFanout` 5/0; Balance 254/0. **Two acceptance lines stay owed, both outside this lane:** (1) `PerfSection.LawnAiDecide` / `SectionCount` / `"lawn.ai.decide"` in `Core/Diagnostics/PerfProbe.cs` — **LANDED 2026-09-23 (lane `cai2`)**: `AiDecide = 25` (CAI1.14's residue, which `CAI-perf-1` measured as unlanded) and `LawnAiDecide = 26`, `SectionCount = 27`, both names in `SectionNames`, pinned by `PerfProbeTests.PerfSections_match_the_enum_the_names_and_this_bound` (planted `SectionCount = 25` → 1 red); (2) the lawn section — **LANDED 2026-09-23 (lane `cai2`) as `gk-core/data/tuning/combat-ai.v2.json`** (the revision is **v2**, not the `v3` this row predicted: the delve rows that would have been v2 aborted on `AiRole.Enemy` and are CAI3.5's, so the next publish was v2). Its four balance keys carry the spec's seeds and are read back through the shipped parser by `CombatAiTuningRevisionTests`; the four structural values stay consts. The H7 blocker the row named is **gone for good**, not just for this lane: `CAI-F1` closed with a revision CONSTANT, so any lane can now publish with its readers in one commit. What is still owed on this line is the lawn section's **consumer** — the frame slot that parses `lawn.trigger.*` is CAI4.8's, so the keys have a file and a parser test but no production reader yet; that is stated rather than glossed. The injector half (switch, frame slot, swing feed, registry drops) is CAI4.8's. See `tasks/reports/CAI4.7.md`.
  - Acceptance:
    - Exactly `N` first-of-swing records produce exactly one edge; `N-1` produce none. A record with
      `IsFirstOfSwing == false`, one with `CastOrigin == true`, and one for an unknown ptr each
      increment nothing. **Planted violation:** removing the `CastOrigin` check makes a cast retrigger
      itself.
    - Hold at `N`: a refused decision leaves the actor due and the next frame serves it with no further
      swings. `3N` swings during a lock produce **one** cast when the lock lifts
      (**planted violation:** `CarryCasts = 2` fails).
    - **Carry lower bound:** a cast committed at `Swings = 2` with `N = 7` leaves `Swings == 0` and the
      next natural edge arrives after exactly `N` further swings. **Planted violation:**
      `Math.Min(Swings - n, n)` leaves `-5` and the next edge arrives after `2N - 2`.
    - No edge inside `L`; an edge at `L+1`; the counter **did** advance during the lock. The same
      `(matchSeed, actorKey)` yields the same offset across runs; two keys differ.
    - With `B` due and budget `b < B`, exactly `b` decide this frame, the rest next, FIFO, and no actor
      waits more than `ceil(B/b)` frames. A token never released is reclaimed at the timeout; release
      is idempotent and a second release does not go negative.
    - **`PerfSection.LawnAiDecide = 26`, `SectionCount = 27`, `"lawn.ai.decide"`** — CAI1.14 took 25
      (plan correction 1). The closed-vocabulary test asserts **27**, with the reason stated.
    - `data/tuning/combat-ai.v3.json`'s lawn section holds exactly the four **balance** keys
      (`swingsPerDecision` 7, `ticksPerDecision` 50, `postCastLockTicks` 10, `offsetStream`); the four
      structural values (`CarryCasts` 1, `DecisionsPerFrame` 8, `CastTokens` 4,
      `CastTokenTimeoutTicks` 20) are code `const`s each carrying the comment `tunables-ssot.md` §1
      requires.
  - Golden: byte-identical — `PerfProbe` is diagnostics and appears in no report hash.
  - Files: `Core/Match/Ai/{LawnDecisionTrigger,LawnDecisionBudget,LawnCastTokenPool}.cs` (new, **landed**), `Core/Diagnostics/PerfProbe.cs` (**owed** — outside this lane), `data/tuning/combat-ai.v3.json` (**owed** — H7: its readers are outside this lane), `tests/FusionRpg.Core.Balance.Tests/CombatAi/{LawnDecisionTriggerTests,LawnDecisionBudgetTests,LawnCastTokenPoolTests}.cs` (new, **landed** — the row's original `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside this lane's fence).
- [ ] **CAI4.8 — `lawn-cast-trigger` B: the frame slot, default-off** · M · deps: CAI4.7 — **HALF LANDED (lane `cai2`, session `combat-ai-2b`, 2026-09-23); the remaining half is ONE named dependency.** **THE START EDGE IS NOW WIRED (lane `cai3`, session `combat-ai-3`, 2026-09-23) — see the block at the end of this row: the slot had NO production caller for `BeginMatch`, so it could not run at all.**
  **Landed:** `Injector/Effects/LawnCombatAiFeature.cs` (the `LawnBasicAttackFeature` shape exactly, `DefaultEnabled` **false**, the env var read once, the `CheatState.IsUserSet` gate, and the whole rule as a pure `Resolve` so the two env-var wins are testable); `Injector/Effects/LawnDecisionHost.cs` (the frame slot: the due set from `LawnDecisionTrigger`, the FIFO `LawnDecisionBudget`, the `LawnCastTokenPool`, the swing feed, the `lawn.ai.decide` perf section around its own body (its SHARE landed later the same day: `lawn-perf-budget.v2.json` adds `ceiling.sections.lawn.ai.decide` as **declared and unmeasured**, exactly as that file's own `_meta` prescribes, with a Core parser that answers `TryGetSectionShare`/`IsSectionMeasured` and a revision constant both the reader and the tests use), `Remove`/`Clear` for the death and board edges, `ClassOf` resolving a live `UniqueBinding` to `Unique` and everything else to `General`, and `TryTriggerState` as the source of `AiDecisionRecord.Trigger`); `Core/Actions/Ai/CombatAiLawnTuning.cs` (the lawn section's parser — the CONSUMER CAI4.7's row named as this row's, reading `lawn.trigger.*` from `CombatAiTuningFiles.Current`); the `InjectorLoop` tick call beside `LawnBasicAttackGrantBinder.Tick` (so an order admitted by this frame's drain is visible to this frame's slot); and the ADDITIVE `InjectorEntityRegistry.Remove`/`Clear` drops (CAI2.5's and CAI4.9's stay). **14 new tests** (`LawnCombatAiFeatureFlagTests` 7, `LawnDecisionHostTests` 7) + 2 for the lawn loader in `CombatAiTuningRevisionTests`: a due actor reaches the decision seam and a committed cast locks it; a THROWING decision is contained and the next frame still ticks; the switch turning off RELEASES every token and drops every counter; death drops the state and a reused address does not inherit the accumulated swings; the trigger state is readable and never synthesised for an unknown actor; an unresolvable actor is `General` never `Unique` by accident. **Readings:** the focused filter **14 passed / 0 failed**; the project **104 passed / 3 failed** (the three are the pre-existing `LawnBasicAttackFeatureFlagTests` = `CAI-find-1`); `CombatAiTuningRevisionTests` **5/0**; `guard-injector-compile` OK. **The VIEW is wired, and that answered CAI4.1's caller line.** The spec's own ordering is *due set → view → policy → cast*, and the view was the one step this host could own without the catalog-blocked inputs: for each due actor it builds the view for that actor's OWN side (the decider that owns it — `LawnBattleView` is perspective-scoped and its `SideOf` is relative) and hands it to the decision seam. `LawnActorViewHost.ViewFor` had **no caller at all** before this (measured: `grep -rn "LawnActorViewHost.ViewFor" src/` outside its own file returned nothing), so CAI4.1's *"without it no production host reaches the view"* is now answered by this row: `InjectorLoop` → `LawnDecisionHost.Tick` → `ViewFor`, with the frame passed from the loop so the view's own per-frame cache works. `Decide` is therefore `Func<string, LawnBattleView, bool>` — the actor and the view for its side — and the test asserts the view is non-null and that `view.SideOf(actorKey)` is `MySideCode`, i.e. the actor's own side really is the perspective it was built for. **The one remaining blocker, named:** the slot's DECISION step is a seam (`LawnDecisionHost.Decide`) because its inputs — module 16's held sets (an `ActionCatalog` the injector has no feed for) and the ledger's held-action rows — are **`CAI4.3`'s unowned blocker**. So the slot schedules and counts, and casts nothing until that feed lands; the row stays open on it, never on "one wire remains".
  **Superseded status (kept for history):** *(filed 2026-09-21, deps CAI4.7.)*  - Acceptance:
    - `LawnCombatAiFeature` has the `LawnBasicAttackFeature` shape exactly and ships **default-off**.
      The switch turning off mid-match drops every state and releases every token.
    - `LawnDecisionHost` runs due set → view → policy → CAI4.6, from one more tick call beside
      `LawnBasicAttackGrantBinder.Tick`. The swing counter is fed from the drained record in
      `EffectRuntime`. A throwing policy is caught at the tick boundary and the next frame still ticks.
    - Death releases the token and drops the state; a **reused ptr address** starts at zero swings and
      no lock. The `InjectorEntityRegistry` edit is additive — CAI2.5's and CAI4.3's drops stay.
    - `lawn.ai.decide` reports its own section, **outside** `KernelDriveHost`'s budget, with a share
      read from `lawn-perf-budget.v1`.
    - **The host supplies `AiActorClassOf`** from the injector's deploy path (a live `UniqueBinding`
      is unique, everything else general).
    - **`AiDecisionRecord.Trigger` is populated here** — swing count, timer state, lock and token.
      CAI2.4 declared the field and left it `AiTriggerState.None` on the lawn; this task owes it.
  - Golden: byte-identical.
  - Files: `Injector/Effects/{LawnCombatAiFeature,LawnDecisionHost}.cs` (new), `Injector/Host/InjectorLoop.cs`, `Injector/Effects/EffectRuntime.cs`, `Injector/Effects/InjectorEntityRegistry.cs`.
**Updated 2026-09-23 (lane `cai3`) — three of the wires this row lists are still uncalled, and the readings are now readable.** `CAI-find-5` holds the full evidence: the swing feed has no production caller (`grep -rn "RecordSwing" src/` finds only the two definitions and their internal call, so the swing trigger never fires in production — the timer half still makes actors due), `ClassOf` and `TryTriggerState` have no caller either, and the five live readings had none until this commit wired them into `debug.combat.snapshot` as a `lawnDecision` block (`DebugCombatActions.LawnDecisionDump()`, 3 tests, two planted violations). The spec's Project-structure row that called `EffectRuntime.cs` "changed — feed the swing counter" is corrected to say it was not. See `tasks/reports/CAI-find-5.md`.
  **START EDGE LANDED, and it was MISSING (lane `cai3`, session `combat-ai-3`, 2026-09-23) — the row's "half landed" was not quite true before this commit.** Measured: `LawnDecisionHost.BeginMatch` had **NO production caller** — `grep -rn "BeginMatch" src/ --include=*.cs` listed every other match-scoped holder being called from `MatchHost`'s `board.start` block (`MatchCommanderSnapshotHolder`, `LawnDeployRosterSnapshotHolder`, `LawnDeployEventRunStateHolder`, `ZombossDeployRunStateHolder`) and `LawnDecisionHost.BeginMatch` **nowhere**; only `gk-fusion/tests/FusionRpg.Injector.Tests/LawnDecisionHostTests.cs` called it. The consequence was total: `_trigger`/`_budget`/`_pool` stayed `null`, so `LawnDecisionHost.Tick` — called every frame from `InjectorLoop.cs:105` — returned at its own null guard (`if (_trigger is null || _budget is null || _pool is null) return;`) and the slot never computed a due set, never offered a budget entry and never leased a token, while its death and board-end drops in `InjectorEntityRegistry` (`:175`, `:199`) already ran. The lifecycle was asymmetric: the host dropped state it never created. **Landed:** `LawnDecisionHost.Configure(CombatAiLawnTuning)` + a `BeginMatch(ulong matchSeed)` overload that uses it (report-once, no-op when unconfigured — it runs on the frame path and module 19's cadence is not load-bearing for anything else); `RpgHost.Initialize` hoists the combat-ai JSON it already read and parses the `lawn` block from the SAME document (one read, two sections, so the two parses cannot drift onto different revisions), inside a try/catch so a stale tuning directory cannot take the host down over a cadence; `MatchHost`'s `board.start` block calls `LawnDecisionHost.BeginMatch(MatchSeed.For(_runtime.MatchKey))` — the same pure seed function the Server uses when replaying (D5), not a second derivation. **Reachability proven by grep, not asserted:** `LawnDecisionHost.BeginMatch` now has exactly one production call site (`MatchHost.cs:250`) and `LawnDecisionHost.Configure` exactly one (`RpgHost.cs:107`). **Verified:** `LawnDecisionHostTests` **9 passed / 0 failed** (2 new: the configured board edge builds the slot and a decision fires; the unconfigured one builds nothing and never throws); **planted violation** (`BeginMatch(tuning, matchSeed)` preceded by an unconditional `return`) → **1 failed**, exactly the configured-board-edge case, then reverted green; the project **106 passed / 3 failed** (the three are the pre-existing `CAI-find-1` staleness); `guard-injector-compile` **OK** (not a skip); guard-dal/single-writer/funnel-delta/actor-hub/test-substrate/debug-scope/secondary-no-unity **all exit 0**. **A test-isolation hole found and fixed in the same commit, by the planted check:** `Clear()` deliberately empties the three structures without nulling them, so a case that only called `Clear()` could observe the PREVIOUS case's slot and pass while the board edge built nothing — the new `ResetForTest()` nulls them, which is what made the plant kill the right test. Production is unaffected (`Clear()` at board.end keeps its empties-not-nulls behaviour; the next `board.start` rebuilds). **The remaining half is unchanged:** the DECISION step is still a seam, because module 16's held sets need an `ActionCatalog` the injector has no feed for — `CAI4.3`'s payload decision. With the feature **default-off** this commit is behaviour-neutral in production (the slot is built and released every frame); with it on, the slot now actually schedules. See `tasks/reports/CAI4.8-start-edge.md`. **The module's spec is synced in the same lane (`spec-lawn-cast-trigger.md`, 2026-09-23):** its status line and its Project-structure markers still called the Injector frame slot, the `PerfProbe` section and the lawn tuning revision owed/absent, and named `lawn-perf-budget.v1` and `combat-ai.v1.json` as current — all superseded by `CAI-perf-1`, `CAI4.8` and `CAI-F1`/`CAI4.7`. Corrected, with the audit re-run: `docs/architecture/combat-ai` now reports **D1 0, D2 0, D3 0, D4 0**.
- [ ] **`CAI-find-5` — three more wires CAI4.8's row claims and does not have, found by scanning every public entry point for a production caller** · S · deps: CAI4.6 (for the swing feed's discriminator) — *(found by lane `cai3`, session `combat-ai-3`, 2026-09-23, by listing every `public static` member of the combat-ai injector and Core files and grepping for each name outside its own file)* — **owner: this program (module 19).**
  `CAI4.8`'s row says the slot landed "the due set from `LawnDecisionTrigger`, the FIFO `LawnDecisionBudget`, the `LawnCastTokenPool`, **the swing feed**, the `lawn.ai.decide` perf section … `ClassOf` resolving a live `UniqueBinding` …, and `TryTriggerState` as the source of `AiDecisionRecord.Trigger`". Measured this session: **one of those five had a production caller** (`BeginMatch`, fixed in `0ff34693b`). The other three are still uncalled — and the scan is what found them, not a reading of the row.
  - **1. The swing feed has no caller.** `grep -rn "RecordSwing" src/` finds `LawnDecisionTrigger.cs:143` (the Core rule), `LawnDecisionHost.cs:190` (the injector entry), `LawnDecisionHost.cs:199` (its call into the Core one) and **nothing else** — so no drained record ever reaches it, and the SWING trigger never fires in production. The slot still becomes due through the timer half (`TicksPerDecision`, 50 lawn ticks), which is why this is not total — but the feature's primary trigger is inert, and the spec's own §"The swing feed comes from the drained record" describes a wire that does not exist. `spec-lawn-cast-trigger.md`'s Project-structure table called `EffectRuntime.cs` "changed — feed the swing counter from the drained record (`:360-386`)"; measured, `EffectRuntime.OnDrained` never calls it, and that row is now corrected to say so.
    **Why it is not wired here, and the named dependency:** the feed's third argument is the cast discriminator, and the only correct source is `EffectEventDto.CastOrigin` — `CAI4.6`'s Contracts field, which is measured absent from `src/` and outside every combat-ai lane's fence. Deriving it from `ev.Trigger == EffectActions.OnActivate` instead would be read-time inference of a producer-known fact, which is exactly what `AiDecisionOrigin`'s own acceptance forbids. Passing `false` unconditionally is correct TODAY (nothing on the lawn emits a cast event) and silently wrong the day `CAI4.6` lands — the drift shape this repo refuses. So the wire waits on the field rather than guessing.
  - **2. `ClassOf` has no caller.** `LawnDecisionHost.ClassOf` (`:299`) is the host's actor-class resolution — `CAI2.4`'s acceptance line *"The host supplies `AiActorClassOf` from the injector's deploy path"* — and nothing reads it. Its consumer is the decision path's composition root, i.e. `CAI4.3`'s blocked part.
  - **3. `TryTriggerState` has no caller.** `LawnDecisionHost.TryTriggerState` (`:320`) is documented as *"The recorded trigger state for one actor, for the inspector's `Trigger` field"*, and `CAI2.4`'s row says `AiDecisionRecord.Trigger` is "populated here" — but nothing calls it, so on the lawn the field still reads `AiTriggerState.None`. Same consumer as (2): `CAI4.3`'s composition root.
  - **4. Five readings had no reader, and that half is now LANDED (this commit).** `DecisionCount`, `CastCount`, `FailureCount`, `TrackedCount` and `TokensInUse` appeared nowhere outside `LawnDecisionHost.cs` — the row's own *"a read of the live counts in `debug.combat.snapshot`"* was done for `LawnOrderHost`, not for this host. `debug.combat.snapshot` now carries a `lawnDecision` block through `DebugCombatActions.LawnDecisionDump()` (public so a test can assert the projection, which the dump builder otherwise has no seam for).
  - Acceptance: (1) `EffectRuntime.OnDrained` (or the drain entry the spec names) feeds `LawnDecisionHost.RecordSwing` for every drained record, in the same commit as `EffectEventDto.CastOrigin` so the discriminator is never guessed — a test that enters through the real drain proves it; (2) and (3) land with `CAI4.3`'s composition root, and their acceptance is `CAI2.4`'s own (`AiActorClassOf` supplied; `AiDecisionRecord.Trigger` populated). (4) is closed here: three tests in `gk-fusion/tests/FusionRpg.Injector.Tests/LawnDecisionDumpTests.cs`, two planted violations each killing their named test.
  - Golden: byte-identical (nothing here touches a battle path).
  - Files: `Injector/Effects/EffectRuntime.cs`, `Injector/Effects/LawnDecisionHost.cs`, `gk-fusion/tests/FusionRpg.Injector.Tests/LawnDecisionDumpTests.cs` (new, landed).
- [ ] **`CAI-find-6` — the Guard project has two reds that belong to no one in this program: a new pytest project with no CI step, and a grown refusal vocabulary** · XS · deps: — *(found by lane `cai3`, session `combat-ai-3`, 2026-09-23, while verifying the merged head)* — **owning program: NOT this one; filed here for the manager to route.**
  Measured: `gk-core/tests/FusionRpg.Guard.Tests` — a CI project — reads **670 passed / 3 failed** with `dotnet`, `pwsh`, `powershell` and `python` all on PATH (without `pwsh` it reads 668/5; without `pwsh` or `dotnet` on the child's PATH it reads 658/15 — that spread is `CAI-find-3`'s pattern, which this completes). Of the three reds:
  - **`PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`** — already filed as **`CAI-guard-1`** (the pinned `BattleEffects.cs` baseline moved in CAI1.12 and was never re-pinned), and `gk-core/tests/FusionRpg.Guard.Tests/**` is a protected path this lane must not touch. Not re-filed.
  - **`CiPytestWiringTests.Every_pytest_project_has_a_ci_step_running_pytest_in_its_own_root`** — message: *"pytest project root(s) with no 'python -m pytest' CI step at that working-directory: ."* **Cause read:** the registry declares `tools-audit-tests` with `"runner": "pytest"`, `"root": "."`, `"tests": "gk-core/tests/tools"` (`gk-core/scripts/verification-boundaries.v1.json:179-182`) and `gk-core/tests/tools/test_audit_program_pipeline.py` **exists**, while `.github/workflows/ci.yml` carries pytest steps only at `working-directory: gk-core/tools/tuning` (`:452`), `gk-core/tools/ip-censor` (`:465`) and `gk-forge/tools/seedsmith` (`:518`) — so the new pytest project landed without its CI step. **The fix is a `ci.yml` step (a protected pipeline path), NOT a registry edit**: editing the registry entry to silence this guard would be widening a guard to pass, which this program's rules forbid. Named so nobody does that by reflex.
  - **`PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`** — an `Assert.Equal` on a collection: the ACTUAL list carries `"picks.source-below-rank-floor"` at position 6 and the guard's expected list (`gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:100`) does not, while its own test name still says "nine". **Cause read:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:305` returns that code, so the closed-vocabulary pin was not updated in the commit that grew the vocabulary. Owning program: whichever owns the fusion picks path; the fix is the guard's expected list (also a protected path). **Sharpened 2026-09-23 (lane `cai3`): the code side is deliberate, not broken** — `gk-core/tests/FusionRpg.Data.Tests` reads **1885 passed / 0 failed** including `FusionInheritancePicksTests.cs:410`, which asserts the new code by name. So the divergence is exactly "a guard's pin was not updated in the same commit as the vocabulary it pins", which is the drift the pin exists to catch, and it is the guard that is stale rather than the Data path.
  - Acceptance: each red is fixed by its owner or re-pinned with a reason in the same commit as the change that moved it — **no guard widened, no `knownRed` entry added.**
- [x] **`CAI-find-7` — a FOURTH CI-blocking red, and this one is routable** · XS · deps: — · *(found by lane `cai3`, session `combat-ai-3`, 2026-09-23, while completing the CI picture `CAI-find-6` opened)* — **owning program: the launcher/player-pack one (its `CS-F3` ruling); filed here for the manager to route, and unlike `CAI-find-6`'s two this fix is NOT in a protected path.**
  Measured in CI's own configuration: `dotnet test gk-fusion/tests/FusionRpg.Launcher.Tests -c Release` reads **1 failed / 165 passed**, the failure being **`MelonHostGapTests.PlayerPackProbe_accepts_Melon_nested_drop`** — *"Missing: Server\data\generated\creatures (content tree — the server boots on the code fallback without it)"* — and `ci.yml` runs that project with an explicit `throw` on failure, so it blocks the gate exactly as the Guard reds do. **Cause read, not guessed:** `PlayerPackProbe.RequiredContentDirs` (`gk-fusion/src/FusionRpg.Launcher/Services/PlayerPackProbe.cs:56-64`) gained a THIRD entry on **2026-09-23** — `Server/data/generated/creatures`, under an owner ruling the comment names as `CS-F3` (*"the concrete species tree ships, and the boot self-heals the roster from it once … Without it a fresh install cannot boot at all"*) — and the change updated ONE of the two fixtures that build a synthetic pack: `PlayerPackProbeTests.cs:89` creates the new dir (and `:61` asserts the very message this test now trips), while `MelonHostGapTests.cs:173-176` still creates only `seed` and `tuning`.
  **The fix is one line, copy-paste from the sibling:** in `gk-fusion/tests/FusionRpg.Launcher.Tests/MelonHostGapTests.cs`, beside `:175-176`, add `Directory.CreateDirectory(Path.Combine(pack, "Server", "data", "generated", "creatures"));` — after which the layout step is satisfied and the test passes. **Owner: whoever owns the `CS-F3` ruling**, since the contract the fixture must satisfy is theirs; a launcher-holding lane can carry it in one commit.
  **Why it is filed here rather than left to CI:** this program's own reports now say *"CI is red on the merged head"*, and that sentence is only useful with the complete list. With this row the list is FOUR: `CAI-guard-1`, `CAI-find-6`'s two (all three in protected paths), and this one (routable).
  - Acceptance: the fixture creates the third content dir, `FusionRpg.Launcher.Tests` reads 166/0 in Release, and the `CS-F3` contract keeps its assertion in `PlayerPackProbeTests` untouched.
- [ ] **`CAI-find-8` — TWO MORE CI-blocking gates: both corpus checks exit 1** · XS · deps: — · *(found by lane `cai3`, session `combat-ai-3`, 2026-09-23, while completing the CI picture `CAI-find-6` opened)* — **owning program: the seed/creature-corpus ones; filed here for routing. Neither path is in a combat-ai lane's fence and NEITHER is protected, so both are routable.**
  Measured with the tools CI runs, from the repo root, capturing the REAL exit code (not `tail`'s):
  - **`dotnet run --project gk-forge/tools/CreatureCorpusDump -c Release -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` → exit 1.** *"corpus-dump --verify: gk-data/packs/fusion/data/seed/creatures/_dump FAILED self-consistency — hash mismatch: manifest declares `cc322647cd0118c72d2dc80826cfe7cea7d02077a59aedfb0bb167319d38a10d`, files on disk hash to `6181dc2d5393e44653b4e7b688633bc3c79b97928183eee645bce15b31c05e0a`"*. `ci.yml:425-426` runs it and throws on failure, and its own comment says the check exists to *"catch a hand-edit or a bad merge"* — which is what it has caught. The dump last changed `ab16afbf8` (2026-09-18), so this is not this lane's doing and is at least five days old. **NARROWED 2026-09-23 (lane `cai3`) — the cause is ONE file and ONE commit, so the fix is one step.** Every payload file in that directory still dates from `740920d2e` (2026-09-12) **except `type-base-stats.json`, which dates from `ab16afbf8` (2026-09-18, *"export the game's static type_base_stats as a committed capture"*)** — so that commit added the new capture **without rewriting `_manifest.json`'s `contentHash` alongside it**, and the tool's own message names the hash and no count, so the counts (`baselineCount`/`plantCount`/`zombieCount`/`recipeCount`) are still right. The remedy is therefore: write the manifest and the capture **together** — re-run whichever step produced `ab16afbf8` so both move in one commit, or (if the capture is authoritative) re-hash the payload to the value the tool prints, `6181dc2d5393e44653b4e7b688633bc3c79b97928183eee645bce15b31c05e0a`, and say in the commit that `ab16afbf8` moved the payload without the manifest. **Not done here:** `gk-data/packs/fusion/data/seed/creatures/_dump/**` is outside every combat-ai lane's fence.
  - **`dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` → exit 1.** *"FAIL — 498 errors across 35 partitions. Re-run the partitions named above; do not hand-fix."* `ci.yml:431-433` throws on it. The log's own class tally names the fatal class: **`SameStageReference` 498** — while `MetaRegistryVersionBehind` (2134) and `ImplicitFlavourDrift` (338) are printed as non-fatal notes, and `PartitionMetaMismatch` (65), `TagAxisNotApplicable` (48), `TierGap` (3) and `MetaSourceRefMissing` (1) also appear. `gk-data/packs/fusion/data/seed/items` last changed `e91d38b1e` (2026-09-22, *"regenerate the 63 unbuildable combination grants; the report now passes"*) — so a lane believed a report passed while this gate reads 498 failures, which is a second reason to route rather than assume. **NARROWED 2026-09-23 (lane `cai3`) — the class, the contract clause and the field are all named now.** Every fatal line is the same shape: **`SameStageReference` `[seed-contract.md §7.1 / authoring-fleet-plan.md §3]`**, and its own text says which field is at fault — *"`'successorOf'` references `<id>`"* — with an **intra-stage** link where the contract requires a later one: `item.humanoid-torso-a-001` → `item.humanoid-torso-a-006` (both `-a-`), `-a-006` → `item.humanoid-torso-b-002` (that one crosses), and so on. The first partition the tool names is `base-types/core-guard/humanoid/a` (16 findings) in the generated file `base-types/humanoid-core-guard-a.json`; the tool's summary puts the whole set at **498 findings across 35 partitions**, and the other classes it prints (`MetaRegistryVersionBehind` 2134, `ImplicitFlavourDrift` 338) are notes rather than the fatal one. **So the remedy is the generator, not the data:** whatever emits `successorOf` must link an item to a **later stage** (the clause the finding cites), and the corpus is then regenerated — `gk-data/packs/fusion/data/seed/items/**` is ~1011-of-1041 seedsmith-generated, and the repo's hard rule forbids hand-editing it to turn a gate green. **Not done here:** `gk-data/packs/fusion/data/seed/items/**` is outside every combat-ai lane's fence. **Also worth flagging to whoever owns that gate:** a lane on 2026-09-22 recorded *"the report now passes"* while this validator reads 498 failures, so the two gates are not the same report — that mismatch is itself the thing to reconcile.
  **Remedy, per the repo's own hard rule: fix the generator and regenerate — never hand-edit `gk-data/packs/fusion/data/seed/**`.** The corpus-dump mismatch is a re-capture or a manifest re-hash (the payload files, not the manifest, are what moved); the item failures are a generator/brief change plus a full regenerate.
  - Acceptance: both commands exit 0 from the repo root, and no `gk-data/packs/fusion/data/seed/**` file was hand-edited to get there.
  **CLOSED (lane `cai3`, session `combat-ai-3`, 2026-09-23) — the fix was in this lane's fence after all, so it was landed rather than routed.** `tests/**` is in every combat-ai lane's allowed paths, and the fix is a test-fixture update to match a contract the CODE already states (with the CS-F3 owner ruling's own comment as its reason) — the same "the test is the stale side" shape as `CAI-find-1`, and not a product decision. **Landed:** one `Directory.CreateDirectory(Path.Combine(pack, "Server", "data", "generated", "creatures"));` beside the other two content trees in `gk-fusion/tests/FusionRpg.Launcher.Tests/MelonHostGapTests.cs`, with a comment naming CS-F3, the sibling fixture that was updated (`PlayerPackProbeTests.cs:89`, asserting this very message at `:61`) and why this one was missed. **Verified:** `FusionRpg.Launcher.Tests` **166 passed / 0 failed in Release** (was 1/165); **planted removal** of the new line → **1 failed**, exactly `MelonHostGapTests.PlayerPackProbe_accepts_Melon_nested_drop`, then reverted green; the `CS-F3` assertion in `PlayerPackProbeTests` is untouched. **CI's red count drops to THREE**, and all three are in protected paths (`CAI-guard-1` + `CAI-find-6`'s two).
- [ ] **`CAI-find-4` — two `CheatCore` comments still name the superseded `lawn-perf-budget.v1.json`** · XS · deps: — · *(found by lane `cai2`, session `combat-ai-2b`, 2026-09-23, in the same commit as the publish that superseded it)* — **owning program: UNCLEAR — `gk-core/src/FusionRpg.CheatCore/**` is outside this lane's fence; filed here for the manager to route.**
  `gk-core/src/FusionRpg.CheatCore/CheatRegistry.cs:85` (*"ceiling now in gk-core/data/tuning/lawn-perf-budget.v1.json (lawn LW1.1); this registry default follows"*) and `gk-core/src/FusionRpg.CheatCore/CheatSchema.cs:117` (*"now carried by gk-core/data/tuning/lawn-perf-budget.v1.json (lawn LW1.1)"*) both name **v1**, which CAI4.8\'s publish superseded: the current revision is `v2` (`LawnPerfBudgetFiles.Current`), and v1 stays on disk only for revert. Cause read: they are COMMENTS, not readers — nothing in `CheatCore` loads the file, the ceiling reaches it through `LawnPerfBudgetTuningHub` (`Server/Program.cs:232`) — so the defect is documentation drift of exactly the class the doc-citation rule covers, not a behaviour change. Not fixed here: the file is outside this lane\'s fence, and the fix belongs with whoever owns the registry narrative (the comments explain that registry\'s own default, so a stale revision number is theirs to keep true).
- [ ] **`CAI-find-3` — `RealRunCollectorTests` spawns a bare `powershell`, so it fails wherever PATH lacks it** · XS · deps: — · *(found by lane `cai2`, session `combat-ai-2b`, 2026-09-23, while running the Server suite for CAI4.9's endpoint)* — **owning program: UNCLEAR — the real-run collector is not this program's; filed here for the manager to route.**
  `gk-core/tests/FusionRpg.Server.Tests/RealRunCollectorTests.cs:162` (`RunCollector`) starts a process by the bare name `powershell`, and both of that class's cases fail with `System.ComponentModel.Win32Exception : An error occurred trying to start process 'powershell' … The system cannot find the file specified.` on a PATH that does not carry `C:\Windows\System32\WindowsPowerShell\v1.0`. Cause read: a process spawn by bare name depends on the ambient PATH, so the test is environment-dependent rather than hermetic — the same class of defect as a test that depends on a machine-local install path. Remedy for the owner: resolve the host explicitly (or use the pwsh/powershell path the rest of the suite uses) and assert the spawn happened, so the failure mode is "no shell" rather than "no collector". Not fixed here: the file is in this lane's fence but the collector is another program's subject, and a change to its test belongs with its owner.
  **EXTENDED 2026-09-23 (lane `cai3`, session `combat-ai-3`) — this is not one test, it is a PATTERN, and it now gates a combat-ai acceptance line.** Measured while verifying `CAI2.3`: `gk-core/tests/FusionRpg.Core.Balance.Tests` runs **2 failed / 208 passed** on a PATH without `python` and **210 passed / 0 failed** on one with it — same suite, same commit, only the ambient PATH differs. The two reds are `ResidualFitLoopTests.FullChain_onAThrowawayDomain_actuallyPublishes_andTheResultParsesAndBinds` and `.PostPublishVerification_warnsHonestly_whenTheFitDidNotFullyCloseTermination`, and the cause is a **bare `python`** at `gk-core/tools/ResidualFitLoop/Program.cs:227` (`new ProcessStartInfo("python")`), reached because the test drives the TOOL's own publish step by design. `ResidualFitLoopTests` is one of the four suites `CAI2.3`'s acceptance names (*"`DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests` green and unchanged"*), so on such a PATH that acceptance line cannot be evaluated at all — which is how this was found.
  **The same class, three more instances, each with a different fix location:**
  - `gk-core/tools/ResidualFitLoop/Program.cs:227` — bare `python`. **Out of every combat-ai lane's fence (`tools/**` is runnable, not writable).** This is the one that gates `CAI2.3`.
  - `gk-core/tests/FusionRpg.Server.Tests/RealRunCollectorTests.cs:162` — bare `powershell` (this row's original instance). **In every combat-ai lane's fence** (`tests/**`), so the routing question is only whether its owner wants the change made here. **Re-measured 2026-09-23 (lane `cai3`): with the Windows PowerShell directory on PATH the whole suite reads `858 passed / 0 failed`, so these two cases are environment-dependent rather than broken — and the suite has grown from 825 to 858 tests since cai2's reading.** That is the sharper form of the finding: nothing here is a failing assertion, which is why it is invisible until someone else runs it.
  - `scripts/guard-doc-citations.ps1:15` and `scripts/verify-change.ps1:27` — bare `python` and bare `powershell`. **Pipeline/protected paths: no lane may edit them**, and both were hit directly this session (`guard-doc-citations` could not start until `python` was prepended to PATH; `verify-change` could not start until the Windows PowerShell directory was).
  **MEASURED CONSEQUENCE, added 2026-09-23 (lane `cai3`): this class reaches a CORE SPLIT PROJECT, not just a tool.** Running all 65 Core projects beyond `Core.Tests`/`Balance`/`Match` in Release, **64 were green and `FusionRpg.Core.ClassSystem.Tests` read 3 failed / 235 passed — and that failure was this class**, because `ReaderCensusTests` (`gk-core/tests/FusionRpg.Core.ClassSystem.Tests/ClassSystem/ReaderCensusTests.cs:193`, already in the inventory below) spawns a bare `python`; re-running with `python` on PATH gives **238 passed / 0 failed**. CI carries the interpreter, so it is not a CI red — but it means a lane cannot verify that project locally without the PATH fix, which is the same cost this row records for the guards and `verify-change`.
  **A RELATED ENVIRONMENTAL TRAP, measured 2026-09-23 (lane `cai3`), worth knowing before anyone blames a red on it:** `gk-core/tests/FusionRpg.E2E.Tests` cannot be BUILT in a worktree while a `FusionRpg.Server.exe` process holds `src/FusionRpg.Server/bin/Release/net8.0/FusionRpg.Server.dll` — the build fails `MSB3027`/`MSB3021` (*"Could not copy … The process cannot access the file"*) after `MSB3026` retries, which reads like a broken build and is a file lock. Five `FusionRpg.Server.exe` and several `dotnet.exe` were running on this machine when it was hit; none was stopped, because they are the owner's or other lanes'. Not this row's class (no bare interpreter), recorded here because it is the same species of environment-dependence and it blocks a verification the same way.
  **The general statement, and the remedy:** a process spawned by a bare interpreter name depends on the ambient PATH, so every one of these is environment-dependent rather than hermetic — the same defect class as a test that depends on a machine-local install path. Two remedies, and the choice is the owner's: **(a)** resolve the host explicitly (`Environment.ProcessPath`-adjacent, a `%SystemRoot%`-anchored PowerShell path, `sys.executable` for a Python child) at each site, or **(b)** declare the PATH precondition once (the guards and `verify-change` already assume it) and keep the sites as they are. **(a)** is what makes an agent shell and a minimal CI runner behave like the owner's machine; **(b)** is cheaper and leaves the fragility documented. Either way the finding is now a pattern with four named sites rather than one test.
  **INVENTORY DONE 2026-09-23 (lane `cai3`) — it is 78 sites, not four.** A repo-wide scan (`new ProcessStartInfo("…")`, `FileName = "…"`, `Process.Start("…")`, `& name`, `Start-Process name`, `subprocess.*(["name"`), comments and `bin`/`obj`/`node_modules`/`dist` excluded: **`dotnet` 32, `powershell` 27, `python` 18, `npm` 1**. The three blocks that matter are `gk-core/tests/FusionRpg.Guard.Tests/**` (27 — the whole guard suite is un-runnable without `powershell` on PATH, and the guards are what `verify-change` selects for most changes), `gk-core/scripts/checks/**` (15, the generator `--check` steps) and `scripts/verify-change.ps1` itself (4: `:27` `powershell`, `:248`, `:266`, `:279` `python`). **That makes remedy (a) a deliberate 78-site programme across `scripts/**` (protected), `tests/**` and `tools/**`, not a drive-by — which is why (b), stating the PATH precondition once where a lane reads it, is the proportionate answer.** The scan is a FLOOR, not a total: a spawn built from a variable, a `FileName` assigned later, or a wrapper script is invisible to it. Full table in `tasks/reports/CAI-find-3.md`.
- [ ] **CAI4.9 — `commander-direct-orders`: a player order as a top-rank candidate** · L · deps: CAI1.10, CAI4.8 · *(ruling D7: uniques only in v1)* — **CORE HALF LANDED** (lane `cai4`, 2026-09-22). `Match/Ai/LawnOrderQueue.cs` is the lawn's `IOrderQueue`: one live order per actor (a second **replaces** and reports `Superseded`), the structural `Cap` 16 refusing the NEW order and never evicting a stranger's, `TryPeek`/`Commit`/`Expire`/`Remove`/`Clear` for every key-set edge, `HandleGateRefusal` (retryable stays live, terminal removes), and a per-order reason bitmask so the same refusal reports once. `Match/Ai/DirectOrderAdmission.cs` holds the closed `DirectOrderRefusal` vocabulary and the retryable/terminal projection of `UsabilityReason` (a projection of the existing closed enum, not a second vocabulary) plus `IsHeld` over module 16's compiled list. 16 tests in `tests/FusionRpg.Core.Balance.Tests/CombatAi/` cover spec rows 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 15 — including row 7 driven through the **real `IntentRouter`**, so the lifetime comparison keeps its one implementation and the queue holds no clock. Four planted violations each kill their named test (no replacement → 3 red; evict-at-cap → 1 red; a flag instead of a reason set → 1 red; the three Terminal members left unclassified → 2 red). `verify-change` exit 0, **15658 passed / 0 failed**; `audit-overflow --targets A3` exit 0; `guard-actor-hub` OK; goldens 5/0; Balance 270/0. **Updated 2026-09-22 (second segment):** spec rows **3, 4 and 5**'s **rules** now land too — `DirectOrderAdmission.CheckScope(orderScopeId, liveScopeId)` and `CheckSubject(in OrderSubject, orderActorKey)` with their `OrderSubject` record, taking the durable identity as ARGUMENTS so the rules are complete and mutation-killed here (removing `StaleRun`'s comparison, `SubjectMoved`'s comparison, or the not-bound guard each kill their own test) while the transport that supplies them stays owed. 20 tests in total across the queue and the admission rules; `verify-change` at the merged head exit 0 with **39 distinct projects, 0 failures**. **Owed, with rows 3–5's supply LANDED 2026-09-23 (lane `cai2`, session `combat-ai-2b`):** (1) ~~the **supply** for rows 3–5 — the two additive `SubjectId`/`ScopeId` fields on `Core/Actions/DirectOrder.cs`~~ — **DONE**: the two fields are trailing and optional (so every existing construction and the whole queue keep compiling), and `LawnOrderQueueTests.An_order_carries_its_durable_identity_through_the_queue_and_the_rules_decide_on_it` proves the queue hands the identity back and that `CheckScope`/`CheckSubject` decide on IT — `None` for the live run, `StaleRun` for another, `None`/`SubjectMoved`/`SubjectGone` for the three subject cases; the identity-free order is asserted byte-identical to the shipped one. **Balance project 301/0, BattleGolden 5/0, five guards exit 0.** (2) row **14** — an order as a rank-0 candidate — **LANDED 2026-09-23 (lane `cai2`)**, and it did NOT need the interface change I first named: `IntentRouter` gained a trailing-optional `Func<DirectOrder, ActionIntent?>? forcedIntent` (ctor AND `Compose`), and `Resolve` consults it for a LIVE order BEFORE the steered step — the chain's own pinned order is *"order-injected, then steered, then policy, then default"*. **The hook owns the gates** (the router never runs them, so it cannot answer "did the order clear them"), and it returns the intent only when the order did; `null`/`None` means it did not and the chain falls through untouched — the spec's *"the identical order that fails a gate does not fire and the policy's own choice is returned"*. A null hook leaves every caller exactly as it was, which is today's inert state. **5 new tests, `IntentRouterTests` 19 passed / 0 failed** (`An_order_that_clears_the_gates_wins_over_the_policys_own_choice`, `An_order_that_fails_a_gate_does_not_fire_and_the_policys_choice_is_returned`, `Without_a_hook_a_live_order_still_falls_through_to_the_policy`, `An_expired_order_is_never_offered_to_the_hook` (counted, 0 calls), `The_order_step_runs_before_the_steered_step`); `BattleGolden` 5/0; `guard-actor-hub` exit 0. So ONE file moved instead of seven implementations; (3) the Server endpoint, the Injector verb/host/registry and the two `web/` files — **the SERVER ENDPOINT LANDED 2026-09-23 (lane `cai2`)**: `gk-core/src/FusionRpg.Server/LawnOrderEndpoints.cs` (`POST /api/lawn/order`, registered in `Program.cs` beside the other host routes) relays exactly ONE `CommandDto` named `lawn.order` through the shipped `InjectorCommandSender` seam and returns without awaiting anything else, refusing an incomplete body with zero commands on the wire. It carries the `// Game Injector Debug` scope banner because it relays to the Injector and proves only what the injector does with the order — never that a cast resolved. **6 new tests, `LawnOrderEndpointTests` 6 passed / 0 failed**, asserted through the REAL `InjectorCommandInbox` the injector polls (`The_route_sends_exactly_one_command_and_returns`, `An_incomplete_order_is_refused_and_nothing_is_relayed` x4, `Two_posts_relay_two_commands`); `FusionRpg.Server.Tests` **823 passed / 2 failed**, the two being `RealRunCollectorTests` failing on `Win32Exception: cannot find the file specified` for a bare `powershell` spawn — an environment/PATH defect in that test, filed as `CAI-find-3`, and unrelated to this change; `guard-debug-scope` **107 routes / 0 banner mismatches**; `guard-dal` exit 0. **D7 LANDED too (`6aaa510e4`)**: `LawnOrderHost.Admit` now ASKS `DirectOrderAdmission.CheckSubject` rather than restating the rule, so a general creature (no live `UniqueBinding`) is refused `SubjectGone` and a binding pointing at a different address is `SubjectMoved` — nothing refused is ever queued. The decision is tested through a second public `Admit` overload that takes an ALREADY-RESOLVED `OrderSubject` (the spec own "admission cannot invent a subject" as a seam), and `OrderSubject` gained a trailing-optional `SubjectId` so an admitted order and its subject cannot disagree. **Named limitation, not faked:** the PRODUCTION resolution reaches `MatchHost.Runtime` and therefore the game assembly, so in a test process it throws `FileNotFoundException: Assembly-CSharp`; `ResolveSubject` catches exactly that and returns a NOT-BOUND subject — the spec own "fail closed, never throw into the frame" — so the production path refuses rather than admitting an order whose subject nobody resolved. `LawnOrderHostTests` **13 passed / 0 failed**; the project **90 passed / 3 failed** (the three are the pre-existing `CAI-find-1` staleness); `guard-injector-compile` OK; seven guards exit 0. **the Injector verb/host/registry half LANDED too, earlier the same day** — and re-reading it, it did NOT need an `ActionCatalog` at all: the queue is Core, and admission is `Offer`, so only the FIRE path needs the held set. Landed: `Injector/Effects/LawnOrderHost.cs` (the spec's *"only the two lookups and the report"* — the tick from `KernelDriveHost.NowTicks`, the durable subject from `CheatState.ResolveBoundInstanceId`, which became public rather than copied, the run identity from the Server's `matchKey`; it offers to a per-board `LawnOrderQueue` and counts admissions/refusals), the `lawn.order` verb in `CheatCommandRunner` beside the non-debug cases, the ADDITIVE `InjectorEntityRegistry.Remove`/`Clear` drops (a live order dies with its actor; the board edge clears them all), and a read of the live counts in `debug.combat.snapshot` (the CAI2.5 precedent: an instrument nobody can read is not an instrument). **10 new tests, `LawnOrderHostTests` 10 passed / 0 failed**; the project **87 passed / 3 failed** (the three are the pre-existing stale `LawnBasicAttackFeatureFlagTests` = `CAI-find-1`); `guard-injector-compile` OK (not a skip); guard-dal/single-writer/funnel-delta/actor-hub/secondary-no-unity/test-substrate/debug-scope **all exit 0**. So the ORDER PATH is now complete end to end from a real host — FE → Server route → command → this adapter → the Core queue — and what remains is only the FIRE path: module 19's frame slot marks the actor due (`CAI4.8`, blocked on lawn `LW1.1`) and the composition root supplies row 14's hook, whose gate check needs module 16's held set and therefore the `ActionCatalog` feed (still `CAI4.3`'s unowned blocker); (4) `data/tuning/combat-ai.v*.json`'s two order keys, which this lane CAN now publish (it holds `gk-core/data/tuning/**` and both readers), so that sub-item is no longer blocked. See `tasks/reports/CAI4.9.md`.
  **THE MODULE'S SPEC IS SYNCED IN THE SAME LANE (2026-09-23, lane `cai3`).** `spec-commander-direct-orders.md` still marked the Server endpoint, the Injector host and their test file "**new; does not exist yet**", named the route `POST /api/lawn/order/direct` and the verb `lawn.order.direct` where the SHIPPED names are `POST /api/lawn/order` and `lawn.order` (`LawnOrderEndpoints.cs:26,38`; `LawnOrderHost.cs:40`; both pinned by their own tests), gave the endpoint test a `Lawn/` directory it does not have (`gk-core/tests/FusionRpg.Server.Tests/LawnOrderEndpointTests.cs`), said `LawnOrderHost` marks the actor due (its class doc says the opposite — that is module 19's slot), and called the `combat-ai` tuning revision H7-blocked. All corrected in place and dated, with the one true remainder stated: the two `lawn.order.*` keys are still owed a `v{n+1}` revision, and the blocker is now CLOSED rather than open. `docs/architecture/combat-ai` scope audit: **D1 0, D2 0, D3 0, D4 0**. See `tasks/reports/CAI-spec-status-4.md`. **A cross-module correction in the same lane (2026-09-23):** this module's spec declared the origin vocabulary as `AiDecisionOrigin { Profile, PlayerOrder, Fallback }`, while module 10 SHIPPED `{ Policy = 0, Order = 1, Steered = 2 }` — the code is what the tests pin, and `.Order` had no producer at all until this lane's `IntentRouter.Resolve` fix. The spec's members are corrected and the draft spellings recorded.
  **Item (4), the two order keys: the CONSUMER is now measured, and it is the fire path (lane `cai3`, 2026-09-23).** `lawn.order.lifetimeTicks` is a BALANCE key (the spec says so: *"It is not structural — a balance pass that wants a snappier order moves it"*), and `lawn.order.queueCap` is **structural** — its value is already the correctly-commented code `const` (`LawnOrderQueue.Cap = 16`, `tunables-ssot.md` T2), so it stays out of the file exactly as module 19's four structural values do. What the lifetime key needs is a reader, and measured there is exactly one place that could read it: `LawnOrderQueue.Expire` has **ONE** caller in `src/` — `IntentRouter.cs:210` — and that router is the lawn's fire path, which `CAI4.3`'s payload decision holds. Publishing the key now would therefore create a parsed value nothing consumes: the dead-config shape the spec's own plan correction 2 forbids for structural values, applied to a balance one. **The question for the manager, one line:** *publish `lawn.order.lifetimeTicks` now (a file and a parser with no consumer until the fire path), or in the same commit as the lawn router that reads it — H7's own rule?* Either way nothing else about item (4) is open.
  - Acceptance:
    - `LawnOrderQueue` + `DirectOrderAdmission` are pure, over a **fake clock** — no `DateTimeOffset`
      or `DateTime` on the path. One live order per actor: a second **replaces** the first and emits
      `superseded`.
    - Admission refuses, each with a planted violation where named: `StaleRun` (removing the check
      lets an order from the previous match command a creature in the next one), `SubjectMoved` (an
      `instanceId` whose binding has a **different** ptr), `SubjectGone` (no `Bound` row — admission
      **cannot invent a subject**), `NotHeld`, `QueueFull` at cap **with no existing order evicted**.
    - `TryPeek` at `IssuedTick + lifetime - 1` returns the order; at `+ lifetime` it expires.
      A retryable refusal stays live and is offered on the next edge; a terminal one is removed. The
      refusal classifier is **total over `UsabilityReason`** — a member with no classification fails.
    - The same reason twice puts **one** event on the wire; a different reason puts a second.
    - Death removes the order and a reused ptr finds none, in **both** spawn/death orders; the board
      edge and the kill switch each clear every order.
    - An order that clears the gates wins over the profile's row 0; the identical order that **fails** a
      gate does not fire and the policy's own choice is returned — *a top-rank candidate, not a bypass*.
      An order-driven commit calls `Commit(actorKey)` exactly once.
    - `LawnOrderEndpointTests`: the route sends **exactly one** `CommandDto` through
      `InjectorCommandSender` and returns **without awaiting anything else**.
    - **A general creature is never orderable** (D7). The commander's own-cast path is neither required
      nor changed.
  - Golden: byte-identical. Run the filter and state the result.
  - Verify: `.\scripts\test-fast.ps1 -AllDefault` (crosses Core/Server/Injector/web — the second
    sanctioned occasion); `guard-debug-scope.py`; `guard-funnel-delta.ps1`; `guard-single-writer.ps1`.
  - Files: `Core/Match/Ai/{LawnOrderQueue,DirectOrderAdmission}.cs` (new, **landed**), `Core/Actions/DirectOrder.cs` (**owed** — outside this lane), `Server/LawnOrderEndpoints.cs` (new, **owed**), `Injector/CheatCommandRunner.cs` (**owed**), `Injector/Effects/LawnOrderHost.cs` (new, **owed**), `Injector/Effects/InjectorEntityRegistry.cs` (**owed**), `gk-web/web/fusion-rpg-web/src/lib/bus/mutations.ts` (**owed**), `gk-web/web/fusion-rpg-web/src/ui/lawn/lawnInteractiveObserve.ts` (**owed**), `tests/FusionRpg.Core.Balance.Tests/CombatAi/{LawnOrderQueueTests,DirectOrderAdmissionTests}.cs` (new, **landed** — the row's original `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside this lane's fence).

### Checkpoint CP4
- [ ] A lawn creature with a kit casts on its `N`-th swing or after `T` ticks, and not otherwise.
- [ ] Death, ptr reuse, the board edge and the kill switch leave no stale counter, token, order or held set — both orders tested.
- [ ] The feature is compiled in and **default-off**; no golden moved anywhere in wave 4.

---

## Wave 5 — proof, and the flip

- [ ] **CAI5.1 — 300-zombie A/B: AI on vs AI off** · M · deps: CAI4.9, and the lawn plan's `lawn-combat-baseline`
  - Acceptance: a live run under `docs/contributing/live-probe-standard.md` — real endpoints, real
    rows, read back through the normal path, never the injector's own telemetry as proof of itself.
    Reports `lawn.ai.decide`'s measured share of the frame against `lawn-perf-budget.v1`, and fps /
    frame-time both ways. The report **states readings** and pins none of them in a test.
  - Verify: full suite immediately before the probe (the third sanctioned occasion); `gk-core/scripts/probe_perf.py`
    window quoted.
  - Files: `docs/research/combat-ai/ab-300-zombies.md` (new).
- [ ] **CAI5.2 — The default-on packet** · S · deps: CAI5.1
  - Acceptance: one short document carrying the A/B numbers, the deploy-cap status, and the
    recommendation. Under ruling **D1** an independent agent review stands in for the owner on this
    gate; it is not a blocking owner gate.
  - Files: `docs/research/combat-ai/default-on-recommendation.md` (new).
- [ ] **CAI5.3 — Flip `LawnCombatAiFeature` default-on** · S · deps: CAI5.2, **two lawn-plan preconditions**
  - **Precondition 1 (edge E2):** the unique deploy cap is live — five uniques per side, ten total.
    The decision budget was sized assuming it; without it the budget is the only thing bounding
    smart-tier cost, and it was not sized for that.
  - **Precondition 2:** `actor-liveness-refresh` has landed, so the derived memo keys on a real
    revision. A decision priced on a frozen Θ is the exact defect that spec measured.
  - Acceptance: the const default flips; the env and debug switches still override; the commit body
    carries the A/B numbers and names both preconditions as satisfied.
  - Files: `Injector/Effects/LawnCombatAiFeature.cs`.

### Checkpoint CP5
- [ ] The A/B report exists with measured numbers, and `lawn.ai.decide` sits inside its budget share.
- [ ] Both preconditions are live before the flip: the deploy cap, and `actor-liveness-refresh`.

---

## Cross-program notes (their files are not edited here)

- **Lawn plan (`BCU2.4`, prefix `LW`).** It owns `lawn-perf-budget.v1.json` and therefore
  `lawn.ai.decide`'s share of the frame; `CAI4.7` reads it and does not author it. It also owns the
  unique deploy cap (`creature-lawn-deploy/spec-unique-deploy-cap.md`), which `CAI5.3` waits on, and
  `lawn-combat-baseline`, without which `CAI5.1`'s A/B measures a 0.5 hit coin-flip.
- **`action-skill-tiers` (`spec-holder-rung-pricing.md`).** `CAI4.4` prices at `EffectiveRungOf`.
  Contract 4 is shipped (`BattleRunState.cs:672-679`) though that spec's status line still reads "not
  built"; it is convergence-owned and not edited here. Already filed in
  [backlog-clean-up-todo.md](backlog-clean-up-todo.md).
- **`base-defense` (`base-defense/spec-siege-ai.md`).** It names `ai.stanceDefault`, a tuning row
  `CAI3.1` deletes. Owed edit, by that program: a one-line status note — *posture is deferred; its key
  lands with its reader* — not a rewrite. Not edited here.
- **`action` program (A8, `action/spec-defence-actions.md`).** `ActionRow` cannot say *"this action is
  a stance whose release is X"*, so A8's decided shape is unreachable from data. Recommended when A8
  takes it up: a nullable `string? StanceReleaseActionId` (absent = not a stance), because gate 0 is
  already an ordinal id comparison. That field is the trigger that flips `BattleRunState.Stance` to a
  real `StanceRuntime`; `CAI3.1` ships the seam and stops there.
- **`battle-engine-ssot.md` §4 D15.** Owed: a "clock sources" row naming
  `SimulationClock` / `KernelDriveHost.NowTicks` (scheduling) against `AdvancedEffectClock` / wall
  clock (status expiry). Two specs in this one program confused them, which is the signal the
  distinction is not obvious from the docs. `CAI1.15` fixes this program's own copies; the SSOT row
  belongs to that document's owner.
- **`event-pipeline`.** `GameEventKind.ChainSynthetic` (`GameEventRec.cs:12`) has no producer anywhere
  in `src/`. Whoever adds the first one inherits `CAI4.6`'s obligation — carry `CastOrigin` onto the
  record and through `ToDto` — or the latent double-charge loop becomes live at that moment.
- **Delve / action content.** `ally-downed` has no consumer: a revive is a **supply** today
  (`SupplyUse.cs:39,48-53`), so no `EquippedActionIds` entry can revive. `CAI3.4` ships the selector
  and the view read as vocabulary; the revive-class corpus action is content those programs own.
  A supply is the player's verb and is deliberately **not** routed through `IIntentSource`.
- **`party-dungeon` (D2.16 / D5.11).** `DelveBattleSessionManager.StartSession` (`:191`) is still
  reachable only from tests. `CAI3.5` makes the **resume** path live; the **start** path needs the
  room→fight trigger party-dungeon owns. No further change is needed here when that caller lands — it
  calls `DelveAutomatedPolicy.For(store)` exactly as `Resume` does. Also tracked as `BCU5.3`.
- **Whoever gives a world turn a durable battle record.** Siege has no persisted match row, so it has
  no replay identity of any kind — not the profile, not the content hash, not the platform stamp.
  Found by `CAI2.1`'s evidence; it is not `replay-identity`'s to fix.
- **`summoner-convergence`.** No file of its 11 programs is edited by any task above.

## Executor routing — every open row's out-of-fence half (lane `combat-ai-3`, 2026-09-21)

- [x] **`CAI-route` — every open row's out-of-fence half is a routed row, with the path it needs** · S ·
  deps: — · **DONE** (lane `combat-ai-3`, 2026-09-21). The brief names three classes that cannot be
  executed here — the parity test / projection / dominance run, and the injector half — and the rule it
  applies is "route, do not reach": a row a lane cannot execute becomes a row that names the paths a
  holding lane needs. This section is that routing, and `R-LAWN-DEPS` carries two **measured** facts
  (`gk-core/data/tuning/lawn-perf-budget.v1.json` absent; the unique deploy cap unowned) plus the new `LW5.1` row
  they produced. See `tasks/evidence-fragments/CAI-route.md`.

`combat-ai-3`'s fence is `gk-core/src/FusionRpg.Core/{Actions,Battle,Balance,Delve}/**`,
`gk-core/tests/FusionRpg.Core.Tests/**`, `tests/FusionRpg.Core.*.Tests/**`, `tools/{CombatSim,ProvePredictor}/**`,
`gk-core/data/tuning/**`, `docs/architecture/combat-ai/**`, `docs/architecture/combat-ai-ideal.md`,
`docs/DESIGN-GATE.md`, `tasks/**`. **Every open task row below either names a path outside that fence or is
blocked on a ruling rather than a path** (the two ruling-only rows are `CAI2.6` and `CAI3.4`, whose files
are all in fence; `CAI2.3`'s files are in fence too — what it lacks is a tool run and an erratum). The
fence is a lane boundary, not ownership: each is still a combat-ai row and closes against its own
acceptance. The paths are listed so a manager can size the routing without re-reading 30 rows; the
measurements in route **R-LAWN-DEPS** were taken this session and are new facts, not a restatement. The
remaining eleven checklist lines are the `CP2`-`CP5` checkpoint rows, which close only when the tasks
they name close and are not routable.
- **`R-GUARD` — `CAI-guard-1` is not routable from this lane either, and it is a structural blocker.** Its
  remedy is a one-line re-pin inside `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs:111`, a
  **protected pipeline path**. Lane `tvb58`, which that row names as its executor, was refused by the hook
  on two attempts (recorded on the row itself) — so this is not "route it to a lane that holds the path",
  it is "no lane can execute it until the hook grants `--allow-protected` to a lane that owns the file".
  Reported as a standing blocker rather than re-attempted. `pwsh -NoProfile -File
  scripts/run-guards.ps1 -Tier ci` does **not** run the Guard test project, which is why the CI-tier table
  reads green while this row is red.
  **BUT CI IS RED ON THE MERGED HEAD, measured 2026-09-23 (lane `cai3`) — and this bullet's own sentence
  could be read as saying otherwise.** `ci.yml:295-296` runs `gk-core/tests/FusionRpg.Guard.Tests` **whole** with
  `-c Release` and an explicit `if ($LASTEXITCODE -ne 0) { throw "FusionRpg.Guard.Tests failed" }`, with no
  `--filter`, no `continue-on-error` and no `if:` guard. Re-running the three failures in exactly that
  configuration (`dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter
  ...`) gives **3 failed / 1 passed**, so all three are environment-independent and the step throws. The
  three are `CAI-guard-1` (`PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`)
  and `CAI-find-6`'s two (`CiPytestWiringTests` and `PlayerSpeciesMaterialiseCallerGuardTests`). **So the
  integration branch cannot pass its own gate until they are fixed, and all three fixes are in PROTECTED
  paths** — which makes this the one blocker that is both repo-wide and unroutable by any lane today, and
  the strongest case on this list for a protected-path grant.

### Blocked re-triage — 2026-09-21 (lane `combat-ai-3`)

Every row below was **re-read against the tree and the ledger** before being left blocked, so the
dependency named is the one that has to move and not work this lane has merely not done. **21** rows are
blocked (the orchestrator's re-triage list named 20 — it omitted `CAI2.6`, which is blocked on an owner
ruling too). One row changed state in this pass: `CAI2.3` was **reopened** (its deps `CAI1.8`/`CAI1.9` are
done in the ledger) and its overkill parity witness landed; it is blocked again on two named external
items, not on work left undone. The rest are genuinely external.

**Re-verified after the `features/mega-merge` fast-forward to `09158294` (44 commits):** every landed slice
of every blocked row is green — `~Ai` **4618/0**, landed slices (Stance/Delve/Lawn/Container/EffectiveRung)
**5173/0**, goldens **14/0**, `FusionRpg.Core.Balance.Tests` **210/0** — and **no** dependency landed, so no
blocker below moved. The `DESIGN-GATE.md:57` closed-vocabulary counts were re-checked against code and all
eleven still match. Evidence: `tasks/evidence-fragments/CAI-reverify-09158294.md`.

**Grouped, so the routing can be sized:** one lane holding `gk-fusion/src/FusionRpg.Injector/**` **cleared 8**
(`CAI2.5`, `CAI4.1`, `CAI4.3`, `CAI4.5`, `CAI4.6`, `CAI4.8`, `CAI4.9`, `CAI5.3`) and is now **spent** — see the
status note below; one holding
`gk-core/src/FusionRpg.Core/Match/**` **cleared 4** (`CAI4.2`, `CAI4.6`, `CAI4.7`, `CAI4.9`) and is now **spent** — see the status note below; one holding
`gk-core/src/FusionRpg.Server/**` **cleared 4** (`CAI2.2`, `CAI3.2`, `CAI3.5`, `CAI4.9`) and is now **half spent** —
`CAI2.2`'s Server half and `CAI4.9`'s endpoint both landed under it, while `CAI3.2` (the two Server statics
must be deleted once their home exists) and `CAI3.5` (`RpgHub.Resume`) still need it and are blocked on other
things first; `gk-core/src/FusionRpg.Data/**`
clears **3** (`CAI2.2`, `CAI3.2`, `CAI3.3`). Four rows need an **owner ruling** and two an **owner-only live
probe**. The rest are single-path or dependency-chain items.

**Status 2026-09-23 (lane `cai2`, session `combat-ai-2b`), re-read rather than carried over.** Two rows in this table **closed**: `CAI3.1` (`9eca27b6e` — both readers were in this lane's fence, so H7 was satisfiable and Outcomes 2/3 landed with it) and `CAI-perf-1` (`4bb8d861a` — `Core/Diagnostics/**` was in fence, so remedy (a) landed the residue and no erratum is needed). **Eight rows have this lane's own fence as their only blocker and are NOT done** — `CAI4.1`, `CAI4.2` (its half is `CAI4.3`), `CAI4.3`, `CAI4.5`, `CAI4.6` (only its `Contracts` field is external), `CAI4.9` (only its two `web/**` files are external) — each named with its remaining files in `tasks/reports/cai2-triage.md`; "a lane holding `gk-fusion/src/FusionRpg.Injector/**`" is no longer a true blocker for any of them. `CAI4.7`'s `PerfProbe` line landed and its H7 note is now wrong for this lane (it holds `gk-core/data/tuning/**` and both readers), leaving only lawn `LW1.1` external. Everything else below still holds as written.

**Status 2026-09-22 (lane `cai4`), measured rather than carried over.** The `gk-core/src/FusionRpg.Core/Match/**` grouping above is **spent**: that lane held the fence and landed the Core half of all four rows it named — `CAI4.2` (13 tests), `CAI4.6` (8), `CAI4.7` (33), `CAI4.9` (20) — plus two composition rows the routing table never had (`CAI-loop-1`, `CAI-loop-2`), so **no row in that group is cleared by a Core/Match lane any longer**; what remains for each is named in its own row above and in `tasks/reports/cai4-lane-summary.md`. Three further asks from that lane wait on a **fence, not a dependency**: `CAI-tests-1` (`gk-core/tests/FusionRpg.Core.Match.Tests/**` — the project the test-split created, with its own focused `core-match` boundary) and `CAI-handoff-1` (`tasks/combat-ai-handoff.md`). `gk-fusion/src/FusionRpg.Injector/**` remains the single largest group **and is claimed by no active session**, so one widening still clears the 8 rows below.

| Row | External dependency that must move first |
**Status 2026-09-23 (lane `cai3`, session `combat-ai-3`), re-read rather than carried over — the `gk-fusion/src/FusionRpg.Injector/**` grouping is SPENT, and this table predates it being held.** That lane held the fence and landed `CAI2.5`'s injector half and read route, `CAI4.1` (closed), `CAI4.8`'s frame slot with its `board.start` edge, `CAI4.9`'s Injector verb/host/registry, and `CAI4.2`'s sibling work — so **a widening of `gk-fusion/src/FusionRpg.Injector/**` now clears nothing that a decision or a `Contracts` grant does not also hold**, which is the opposite of what the sentence above says. Four rows below have CLOSED since it was written (`CAI2.6`, `CAI3.1`, `CAI4.1`, `CAI4.7`) and must not be routed at all; seven more have changed blocker from a FENCE to a DEPENDENCY, a DECISION or a GRANT, and each now says which. **The asks that would actually move this program are on `tasks/reports/combat-ai-open-decisions.md`** — in order of value: a `gk-core/src/FusionRpg.Contracts/**` grant or route (unblocks five rows), the `CAI2.7` waste-guard ruling, the `tasks/combat-ai-handoff.md` fence, and the projection erratum — plus the two measured verification-cost asks (`V1`/`V2`) on the same page.
|---|---|
| `CAI2.2` | **Server half LANDED 2026-09-23** (`Server/CombatAiProfileFiles.cs`, 8 tests). Remaining: the denied `Data/**` column (`combat_ai_profile`) + the three stamping sites that read it |
| `CAI2.3` | **owner erratum ruling** on who owns the profile→`Predictor.ActionEconomy.Options` projection (this row claims it; `spec-action-schedule-twin.md:421-423` assigns it to module 2 or 14) + a second erratum on the overkill parity line, which cannot pass as written because the measured behaviour is a divergence. The `gk-forge/tools/DominanceBaseline/**` run is **DONE** (2026-09-23, lane `cai2`: read-only, the matrix and corners reproduce the checked-in baseline) |
| `CAI2.5` | **Injector half + read route LANDED** (lane `cai3`, 2026-09-23). Remaining: the decision FEED, i.e. `CAI4.8`'s slot → `CAI4.3`'s payload decision |
| `CAI2.6` | **CLOSED 2026-09-23** (`e39f8db11`, ruled from `combat-ai-ideal.md:318`) — do not route |
| `CAI3.1` | **CLOSED 2026-09-23** (`9eca27b6e`, `siege.v3.json` + both readers in one commit) — do not route |
| `CAI3.2` | a lane holding `gk-core/src/FusionRpg.Data/**` + `gk-core/src/FusionRpg.Server/**` |
| `CAI3.3` | a lane holding `gk-core/src/FusionRpg.Core/World/**` + `gk-core/src/FusionRpg.Data/**` |
| `CAI3.4` | **owner decision** shared with `CAI3.1` + `CAI3.5`'s Server lane (its `RoleOf` caller) |
| `CAI3.5` | a lane holding `gk-core/src/FusionRpg.Server/**` + a **protected-path grant** for `tests/FusionRpg.Guard.Tests/NoCatchInLiveBattleCallStackTests.cs` |
| `CAI3.6` | `CAI2.2` (blocked) + `docs/architecture/decisions.md` + `docs/research/combat-ai/**` |
| `CAI4.1` | **CLOSED 2026-09-23** (`88423b023`, the injector view host) — do not route |
| `CAI4.2` | **Core half landed 2026-09-22**; its remainder IS `CAI4.3` (`LawnHeldActionRegistry.cs` + the Cold push), so the blocker is a DEPENDENCY, not a fence |
| `CAI4.3` | **The Injector and Server fences were both HELD** (lane `cai3`); the blocker is the **`gk-core/src/FusionRpg.Contracts/**` grant** the compiled-list payload needs |
| `CAI4.5` | **Core half landed**; the Injector half shares `CAI4.3`'s blocker (the `ActionCatalog` feed), so the fence is not what holds it |
| `CAI4.6` | **Pure half landed**; the blocker is `EffectEventDto.CastOrigin` in **`gk-core/src/FusionRpg.Contracts/**`**, not the Injector fence |
| `CAI4.7` | **CLOSED 2026-09-23** (`PerfProbe`'s `LawnAiDecide` + the lawn section in `combat-ai.v2.json`) — do not route |
| `CAI4.8` | **Injector half LANDED** (switch, frame slot, board.start edge, the section and its share); `CAI4.7` is closed; the remaining decision step is `CAI4.3`'s |
| `CAI4.9` | **Core half landed 2026-09-22** (`LawnOrderQueue.cs` + `DirectOrderAdmission.cs`, 20 tests, all five refusal rules). Remaining: `Actions/DirectOrder.cs`'s two additive identity fields, `Actions/IntentRouter.cs`'s forced-intent hook (row 14), Server + Injector + `web/**`; dep `CAI4.8` blocked |
| `CAI5.1` | an **owner-only live probe** + `docs/research/combat-ai/**`; deps `CAI4.9` + lawn `lawn-combat-baseline` (`LW2.4`, open) |
| `CAI5.2` | `docs/research/combat-ai/**` + dep `CAI5.1` |
| `CAI5.3` | a lane holding `gk-fusion/src/FusionRpg.Injector/**`; preconditions `LW1.4`-`LW1.6`, `LW5.1`, `LW1.1` — all **measured open** |

- **`R-INJ` — the Injector half (`gk-fusion/src/FusionRpg.Injector/**`), rows CAI2.5, CAI4.1, CAI4.3, CAI4.5,
  CAI4.6, CAI4.8, CAI4.9, CAI5.3.** This is the single largest routing block, and every one of them is the
  same shape: a Core mechanism with tests that no production host reaches.
  `Effects/AiInspectFeature.cs` + `Effects/LawnAiDecisionObservability.cs` + the additive
  `InjectorEntityRegistry.Remove`/`Clear` drop (CAI2.5, ring landed at `Actions/Ai/AiDecisionRing.cs`);
  `Effects/LawnActorViewHost.cs` (CAI4.1, the twelve-member view landed at `Actions/Ai/Lawn/`);
  `Effects/LawnHeldActionRegistry.cs` + `CheatCommandRunner.cs` + `Server/RpgHub.cs`'s Cold push (CAI4.3);
  `Effects/LawnBasicAttackCostCharger.cs` + `Effects/LawnCostRowSource.cs` (CAI4.5);
  `Effects/LawnCastActivation.cs` (CAI4.6) **and `gk-core/src/FusionRpg.Contracts/EffectDtos.cs`'s additive
  default-`false` `CastOrigin` field, which is also out of fence**;
  `Effects/{LawnCombatAiFeature,LawnDecisionHost}.cs` + `Host/InjectorLoop.cs` + `Effects/EffectRuntime.cs`
  (CAI4.8); `Effects/LawnOrderHost.cs` + `CheatCommandRunner.cs` + the two
  `gk-web/web/fusion-rpg-web/src/{lib/bus/mutations,ui/lawn/lawnInteractiveObserve}.ts` files (CAI4.9); and
  `Effects/LawnCombatAiFeature.cs`'s const default (CAI5.3, which is gated on two preconditions anyway).
  **Note for whoever holds it:** CAI1.12's injector half was already executed this way by lane `cai-sink`
  (`gk-fusion/src/FusionRpg.Injector/**` + `Effects/EffectModels.cs`), so the pattern and the precedent exist.
- **`R-CORE-MATCH` — `gk-core/src/FusionRpg.Core/Match/**`, rows CAI4.2, CAI4.6, CAI4.7, CAI4.9 — DONE 2026-09-22.**
  *Lane `cai4` held this fence and landed all four halves (74 tests) plus `CAI-loop-1`/`CAI-loop-2`; what
  each row still owes is listed in its own table row above. The file list below is kept as the record of
  what that fence was for.* `Match/Ai/LawnHeldActionSets.cs` (CAI4.2); `Match/Ai/LawnCastPlan.cs` (CAI4.6 — the *pure* half, not
  just the injector half); `Match/Ai/{LawnDecisionTrigger,LawnDecisionBudget,LawnCastTokenPool}.cs` +
  `Diagnostics/PerfProbe.cs` (CAI4.7 — its `data/tuning/combat-ai.v3.json` and its Core tests *are* in
  fence, so only these two paths are); `Match/Ai/{LawnOrderQueue,DirectOrderAdmission}.cs` (CAI4.9 — its
  `Actions/DirectOrder.cs` is in fence). Note `docs/architecture/combat-ai/spec-lawn-actor-view.md:103`
  ruled the *view* files into `Actions/Ai/Lawn/**` rather than `Match/Ai/**`; the four rows above are
  per-actor/per-match state, which that same ruling sends to `Match/Ai/`. The split is deliberate, not
  a filing mistake.
- **`R-CORE-WORLD-DATA` — rows CAI3.2, CAI3.3.** CAI3.2: `Data/Sqlite/RpgStore.Loadouts.cs`,
  `Server/WebMatchService.cs:654-675`, `Server/SpecimenLoadoutEndpoints.cs:83-94`,
  `tests/FusionRpg.Data.Tests/Items/EquippedActionIdsForTests.cs`. CAI3.3: its in-fence Core third
  (`Actions/IContainerEffectResolver.cs`'s composite) **landed 2026-09-20**; what remains is
  `Core/World/Turn/DistrictAssaultResolver.cs` (the composition + `Resolve` threading) and
  `Data/Sqlite/RpgStore.WorldTurns.cs`. Needs `Core/World/**` + `Data/**` + `Server/**`.
- **`R-SERVER` — rows CAI2.1's Data+Server thirds, CAI2.2, CAI3.5, CAI4.9's `LawnOrderEndpoints.cs`.**
  Data third: the nullable `combat_ai_profile` column beside `RpgStore.cs:821` and
  `RpgStore.WebMatches.cs`, with `gk-core/tests/FusionRpg.Data.Tests/WebMatchLogProfileStampTests.cs`. Server
  third + CAI2.2: `Server/CombatAiProfileFiles.cs` (new), the three stamping sites
  (`WebMatchService.cs:125-128,197-200`, `DelveBattleSessionManager.cs:200-204`), the five-step pin
  resolution and the boot-sweep fifth guard (`WebMatchService.cs:246-290`). CAI3.5:
  `Server/{RpgHub,DelveAutomatedPolicy,DelveBattleSessionManager,DelveBattleSession}.cs`,
  `tests/FusionRpg.Server.Tests/Delve/DelveAutomatedWiringTests.cs`, **and
  `tests/FusionRpg.Guard.Tests/NoCatchInLiveBattleCallStackTests.cs`, which is a protected pipeline path
  — a lane needs an explicit grant for it, the same one `tvb58` did not have for `CAI-guard-1`.**
  **CAI2.2 sits entirely behind CAI2.1's Server third**, so route them together or not at all.
- **`R-TUNING-PUBLISH` — rows CAI3.1, CAI3.6 (hard edge H7).** `gk-core/data/tuning/siege.v3.json` and any
  `combat-ai.v2/v3.json` cannot land from this lane because **both readers name their file by hand**:
  `gk-core/src/FusionRpg.Server/Program.cs:231` (`siege.v2.json`) and `:237` (`combat-ai.v1.json`), plus
  `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:89`. A publish that cannot switch its reader in the same commit
  is what H7 forbids, so the *file* is in fence and the *change* is not. CAI3.6 additionally needs
  `docs/architecture/decisions.md:44` and `docs/research/combat-ai/predicted-delta-rulesetversion-6.md`,
  both out of fence.
- **`R-DOMINANCE` — CAI2.3's last two acceptance lines.** The parity test landed
  (`gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs`, in fence). **(a) is
  DONE 2026-09-23** (lane `cai2`, session `combat-ai-2b`): `dotnet run --project gk-forge/tools/DominanceBaseline --
  --theta 100` is read-only without `--out` (it prints JSON to stdout and writes nothing), so the
  `gk-forge/tools/DominanceBaseline/**` fence never applied to the RUN — and the run **reproduces the checked-in
  baseline exactly** on the comparable parts (`dominanceMatrix.names`/`.wins` equal, `dominantCorners ==
  ["Might"]`, `theta == 100`; the stored file's three extra keys come from a richer invocation and its own
  `coverage.tuningSync` dates the matrix to 2026-08-27). **(b) remains the erratum**: the row claims the
  projection, `spec-action-schedule-twin.md:421-423` assigns it to module 2 or module 14, and no document
  specifies the mapping — and it is not mechanical (a profile carries action FILTERS plus a floor, no cost and
  no multiplier, while `ActionOption.CostShareOfOutputMilli` is a share of the action's own nominal output).
  A second erratum joined it 2026-09-23: the acceptance's overkill parity line cannot pass as written,
  because the measured behaviour is a divergence. See `tasks/reports/CAI2.3.md`.
- **`R-DOCS-RESEARCH` — rows CAI5.1, CAI5.2.** `docs/research/combat-ai/ab-300-zombies.md` and
  `default-on-recommendation.md` **do not exist** (the directory holds only `AUDIT.md`, `REVIEW-A/B.md`,
  `S1-S5`, `predicted-delta-kill-estimate.md`). Both are live-probe deliverables under
  `docs/contributing/live-probe-standard.md` and `docs/research/**` is out of fence.
- **`R-OWNER` — a ruling, not a path: CAI2.6, and CAI3.1/CAI3.4's shared second half.** CAI2.6 asks which
  of the two reserve-floor readings is wrong (`Actions/Ai/ReserveFloorAffordability.cs:92-108`'s
  `current <= floor` pre-condition vs the ideal's *"after paying"*); both witnesses are pinned and the
  cross-reference slice landed, so the ruling is the whole remaining task. CAI3.1's and CAI3.4's last two
  tests each need a live `BattleRunState`, a **private nested class inside `BattleEngine`** whose own
  `:20-31` records that the nesting exists *to avoid* a visibility change — making it `internal` is a
  recorded-position reversal, so it is an owner decision, not a lane's.
- **`R-LAWN-DEPS` — rows CAI4.7, CAI5.1, CAI5.3; measured this session.**
  `gk-core/data/tuning/lawn-perf-budget.v1.json` **does not exist** (`ls gk-core/data/tuning/` shows only `combat-ai.v1`,
  `siege.v1`, `siege.v2`), so **CAI4.7's entry condition is unmet** — its `lawn.ai.decide` share has no
  file to read. Its owner is the lawn plan's **LW1.1** (`tasks/lawn-todo.md:16`), still `- [ ]`.
  The same holds for CAI5.3's two preconditions: **precondition 2** `actor-liveness-refresh` is lawn
  **LW1.4-LW1.6** (`tasks/lawn-todo.md:34,41,48`), all three `- [ ]`; and **precondition 1**, the unique
  deploy cap, has **no task in any todo** — `docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md`
  reads *"Status: spec, 2026-09-20. Not built."* while its own header says it is *"scheduled once in the
  backlog-clean-up lawn plan"*, and the lawn plan schedules 16 tasks (`LW1.1`-`LW4.2`) and this is not one
  of them. Filed as **`LW5.1`** in `tasks/lawn-todo.md` in the same commit as this line.
- **`R-FOREIGN-TESTS` — CAI3.1's outcome 2/3 breaks two files outside every combat-ai lane.** Narrowing
  `AiTuning` to its two live members (`ObjectiveReferenceDistanceCells`, `ThreatRadiusCells`) removes
  `StanceDefault` and `AutoResolveHandicapMilli`, and both are passed **by name** at
  `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs:530` and
  `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:470` (read this session: four named
  arguments each, so the break is four named-argument errors across two projects, plus
  `tests/FusionRpg.Core.Tests/ContractTuningTestBootstrap.cs` in fence). A lane holding those two test
  projects must land the edit with CAI3.1's narrowing, or the narrowing cannot land at all.

## Deferred / named follow-ups
- **SUPERSEDED 2026-09-21 — the two `CAI1.15` bullet items below are DONE.** `combat-ai-2` closed
  `CAI1.15` (`b3ffc183`) and this lane re-measured both in `CP1`: `docs/DESIGN-GATE.md:57` is the
  deciding-subsystem row and `docs/architecture/combat-ai-ideal.md:129` names `KernelDriveHost.NowTicks` /
  `SimulationClock` for scheduling against wall-clock `AdvancedEffectClock`. The two entries are kept for
  history because they record *why* the row was owed; do not re-open them.
- **CAI1.15 bullet 1 — the `docs/DESIGN-GATE.md` §1 topic-index row is owed.** It needs a row for
  **"anything that decides what an actor does — AI, intent sources, target or action choice"**, naming
  `battle-engine-ssot.md` §3c (*the engine resolves, the AI decides*), `combat-ai-map.md` and
  `combat-ai-ideal.md`, and stating the closed vocabularies this program owns with their counts.
  Insertion point read: the §1 table's battle row is `docs/DESIGN-GATE.md:56` ("Anything that changes
  what happens in a BATTLE — ..."), so the new row belongs adjacent to it. **Owning program: none
  uniquely** — `docs/DESIGN-GATE.md` is the repo-wide reading gate, so this row is filed here for the
  manager to route rather than guessed at. Cause read: the atom row two lines up records that this
  table "has now gone stale four times" because a count lived in one place and moved in another, which
  is exactly why this program's counts must be written down once, here, and kept in one place.
- **CAI1.15 bullet 2 — `docs/architecture/combat-ai-ideal.md` still calls `AdvancedEffectClock` the lawn
  clock host for triggers.** The row is at `combat-ai-ideal.md:129` (NOT `:119`, which has since moved
  to the "Retarget memory" row) and reads *"lawn effect clock `AdvancedEffectClock`
  (`Injector/Effects/EffectRuntime.cs:42,133`, battle-engine-ssot D15) | Triggers and lawn cooldowns
  read the **same** engine clock that status expiry reads"*. Cause read: the sibling document already
  carries the correction — `combat-ai-map.md:81` says *"the map first named `AdvancedEffectClock`; that
  clock is wall-clock-seeded for status expiry (`EffectRuntime.cs:42,133`) and is not the decision
  clock"*, and names `KernelDriveHost.NowTicks / 100` instead. A correction in one document and not its
  sibling has not landed. Owning program: **this one** — combat-ai owns the ideal; the edit is blocked
  only by this lane's file fence, not by ownership.

- **CAI2.3's dominance re-measurement needs `gk-forge/tools/DominanceBaseline`, outside the `combat-ai-2` lane's
  fence.** The row's acceptance names four test classes green and unchanged — `DominanceBaselineTests`,
  `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests`, all
  `tests/FusionRpg.Core.Tests/Balance/**`, in-fence — **and** "the dominance run recorded as evidence it
  did not move", which is `dotnet run --project gk-forge/tools/DominanceBaseline` (that project is not in the
  lane's allowed paths, which list `gk-core/tools/CombatSim/**` and `gk-core/tools/ProvePredictor/**` only). Cause read:
  the acceptance needs a tool run the lane cannot perform, so the row was left unstarted rather than
  closed against a partial acceptance. **Next step, in order:** (1) `SchedulePolicy` + `SchedulePolicy.Greedy`
  as the identity default in `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs` with a trailing
  `policy = null` parameter, then the same semantics in `gk-core/tools/CombatSim/{ActionEconomy,Simulator,Analytic}.cs`,
  `ActionScheduleTests`/`PredictorTests`/`ProvePredictor` green **unedited**; (2) the reserve floor +
  overkill guard + `MinTargets > 1` throw; (3) the profile→`Predictor.ActionEconomy.Options` projection;
  (4) `ActionScheduleMatchesCorePolicyTests`. A lane holding `gk-forge/tools/DominanceBaseline` runs step 0 of the
  acceptance and turns the claim into evidence.
- **CAI2.4's `AiCandidateVerdict.Gate` has no honest source in the siege path, and its own Files list
  omits what the "all four policies" line needs (lane `combat-ai-2`, filed, not attempted).**
  `SiegeAiIntentSource`'s candidate loop builds `TargetCandidate`s — target-side INPUTS — in
  `TargetStage`/`TryBuildCandidateCore` (`Battle/Siege/SiegeAiIntentSource.cs:249-300,338-440`), and
  `UsabilityEvaluator` runs in step 3 against the CHOSEN target only (`:175-205`). So there is no
  per-candidate `UsabilityResult` in that path to copy into the record, and the spec's own rule 2 forbids
  obtaining one by re-running the gates ("a gate re-checked one tick later can answer differently"). The
  per-action gate buffer the spec describes lives in `Actions/Ai/ActionStage.cs` (the core policy's action
  stage), so the honest first slice is the record + `BattleTraceDecisionSink` + the core policy/action-stage
  wiring + `IntentRouter` carrying the sink — and `IntentRouter.cs`, `CoreIntentPolicy.cs`, `ActionStage.cs`
  are **not** in the row's Files list. Next lane: decide whether the row is re-scoped to that surface (a
  row erratum) or the sink is threaded through the router as its own task. Landing only the record types
  would be a mechanism no production host reaches.
  **MEASURED 2026-09-22 (lane `cai4`):** **the second option is already carried out** — `IntentRouter.Compose` takes
  `IAiDecisionSink? sink` and wraps the policy in `AiDecisionRecordingSource`
  (`gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs:77,86-88`), so the router carrying the sink is not a
  remaining task. What the entry is *actually* about still stands: there is no honest per-candidate
  `UsabilityResult` in the SIEGE path, and the spec's rule forbids obtaining one by re-running the
  gates a tick later. So the open question is the erratum, not the wire.
- **CAI2.1's Data and Server thirds, filed by the `combat-ai-2` lane (2026-09-20).** The Core identity
  record landed there; the other two thirds need paths that lane does not own, and CAI2.2 sits entirely
  behind them. **Data** (`gk-core/src/FusionRpg.Data/**`, `gk-core/tests/FusionRpg.Data.Tests/**`): one nullable `TEXT`
  column `combat_ai_profile` on `rpg_web_match_log` via `EnsureColumn` beside `RpgStore.cs:821` (after the
  table's own `CREATE`), plus `WebMatchLogEntry`/`AppendWebMatchLog`/`SelectLog`/`MapLog` in
  `RpgStore.WebMatches.cs:19,31,203-229`, and `WebMatchLogProfileStampTests.cs`. **Server**
  (`gk-core/src/FusionRpg.Server/**`, `gk-core/tests/FusionRpg.Server.Tests/**`): `CombatAiProfileFiles.cs` implementing
  `ICombatAiProfileSource` over every `data/tuning/combat-ai.v*.json`, the three stamping sites
  (`WebMatchService.cs:125-128,197-200`, `DelveBattleSessionManager.cs:200-204`), the five-step pin
  resolution at both `if (!created)` branches and `DelveBattleSessionManager.Resume`, and the boot-sweep
  fifth guard written in the same shape as the four existing ones (`WebMatchService.cs:246-290`). Owning
  program: **this one** (the row is ours) — the blocker is a lane fence, so the manager routes it to a
  lane holding Data/Server paths (the `combat-ai-build-20260920` session record already claims all of
  them).
- **CAI1.14 residue, filed by the same lane that landed its site-1 slice.** `PerfSection.AiDecide = 25`,
  `SectionCount = 26` and the `"ai.decide"` name must land in `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`,
  which is outside that lane's allowed paths (`gk-core/src/FusionRpg.Core/{Actions,Battle}/**`). Cause read:
  `PerfProbe.cs:40` ends at `LawnMoveDrain = 24` today, so the new section is 25 and the count 26 (plan
  correction 1). The channel-id interning site is filed in the owning program's todo instead —
  `tasks/derived-stats-todo.md` -> "Post-program corrections" — because `ResourceChannelReader` ->
  `DerivedStatChannels.ResourceMax` builds `$"resource.max.{id}"` per call
  (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:539`).


- **Doc-citation re-anchoring the CAI1.11/CAI1.12 code moves broke, outside this lane's paths.**
  `BasicAttack.cs` grew 521 → 609 lines (CAI1.11) and `BattleEffects.cs` 384 → 447 (CAI1.12), so every
  `file:line` citation into them moved. Re-anchored in `docs/architecture/combat-ai/**` in the same
  commits. NOT re-anchored, because these files are outside the lane's allowed paths: `combat-ai-ideal.md`
  (`BasicAttack.cs:142,169`, `:113`), `docs/research/combat-ai/**` (`AUDIT.md:32,37,39,62,66`,
  `S1-battle-core.md:10`, `S4-lawn.md:33`, `REVIEW-B.md:57,61`, `predicted-delta-kill-estimate.md`),
  `docs/architecture/action/**`, `action-base-stats-ideal.md`, `action-enrich*/**`, `passive-tree/**`,
  `effect-atom/**`, `legion-build/**`, `lawn-combat-wire*/**`, `base-defense*/**`, `trade-network/**`,
  `derived-pipeline-audit-2026-08-30.md`, `solid-enforcement-map.md`, `species-progression/**`.
  `guard-doc-citations.ps1 -Strict` reports 0 HIGH on all of them (it checks bounds, not content), so
  this will not surface at merge — it needs a routing decision, not a guard fix.
  **Added by CAI1.12's injector half (session `cai-sink`, 2026-09-20):** inserting `IDeclaresExecution`
  after `IEffectActionSink` in `Effects/EffectModels.cs` shifts two more citations below `:126` —
  `docs/architecture/action/spec-battle-live-stat-modifiers.md:159` (`:126-131` -> `:146-151`) and
  `docs/architecture/lawn-combat-wire/spec-lawn-combat-calibration.md:81` (`:234-238` -> `:254-258`).
  The insert occupies `:125-144`, so the shift is exactly +20 for everything formerly at `>=125`. Both are
  outside that session's fence and are filed as rows in `tasks/action-todo.md` and
  `tasks/lawn-combat-wire-todo.md` respectively. All 38 citations into `InjectorEffectActionSink.cs`
  were deliberately preserved by appending its declaration at the end of the class.
- **`BattleRunState.cs` citations across the combat-ai specs were already stale before this lane.**
  `spec-resolvable-here.md` cited `BindContainers` at `:707-738`; it was at `:742` at HEAD and is at
  `:780-811` now (that one spec's rows are fixed). `spec-intent-router.md:70,120,281`,
  `spec-ai-tiers-personality.md:22,95,212,247`, `spec-core-scorer.md:40,326,373`,
  `spec-delve-automated-wiring.md:115-552`, `spec-lawn-cost-authority.md`, `spec-lawn-held-actions.md`,
  `spec-siege-loadout-wiring.md`, `spec-stance-wiring.md`, `spec-aggression-tier-map.md`,
  `spec-profile-schema.md` all carry `BattleRunState.cs` line numbers that no longer resolve to the
  method they name. Owner: whichever program next edits those specs — a mechanical sweep, not a
  behaviour change.
  **MEASURED 2026-09-22 (lane `cai4`):** **the combat-ai half is DONE.** `CAI-cite-1` re-anchored 39 citations across 12 specs;
  `CAI-cite-2`/`CAI-cite-3` closed the rest of this program's own doc trees, so both scopes audit at
  `D1 0, D2 0, D3 0, D4 0` and the survey-tree content sites carry dated pre-fix notes. What remains of
  this entry is the OTHER programs' documents it lists (`docs/architecture/action/**`, `passive-tree/**`,
  `effect-atom/**`, `legion-build/**`, `lawn-combat-wire*/**`, `base-defense*/**`, `trade-network/**`, …),
  and those are theirs, not this program's.

- **Orders for general creatures** — the per-ptr spawn generation counter. Ruling D7 defers it;
  revisited only if players ask. If general creatures gain a durable lawn identity for another reason,
  it becomes free and the restriction should be revisited.
- **A difficulty lever.** Its own future sub-program (D2). Nothing here takes a difficulty input, and
  `AiTierResolverTests.Nothing_in_tier_resolution_reads_a_difficulty_input` keeps it that way.
- **An economy-carrying dominance variant** beside the economy-free one, for whoever owns the
  class-system fit. Switching the existing one would move a committed baseline for a reason nobody has
  asked for.
- **A golden fixture with a real divergent multi-action loadout.** Today's fixtures carry no
  `EquippedActionIds`, so they cannot exercise the reserve floor, the waste guards or action choice —
  the very things `CAI3.6` switches on. `decisions.md:44` names such a fixture as its own bump
  trigger, so it is its own change with its own bump decision, owned by the battle golden set's owner.
- **Fold the fact half of `AiRowCondition` into `ICompiledPredicate`** if it reaches eight members.
  **MEASURED 2026-09-22 (lane `cai4`):** **not met — it is 6**, pinned by its own test (`AiRowCondition_has_six`, which states
  the same trigger on its own line). No action.
- **One lawn "now" accessor** that both the cost ledger and the trigger read — the better D15 answer,
  outside this program because it would move the ledger's clock too.
- **Rename `ContentHashStamp.TableDigests` to `PartDigests`** once a second non-table consumer exists.
  **MEASURED 2026-09-22 (lane `cai4`):** **the condition is MET, and the work is filed elsewhere.** `CombatAiProfileIdentity`
  (`CAI2.1`) is the second consumer and it is not a table: `StampOf` builds
  `new ContentHashStamp(..., digests)` where the map is keyed by **profile id** — keys like
  `"siege/default"` (`gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs:67`). `effect-atom` owns
  the rename and has it open with three options
  (`tasks/effect-atom-todo.md:642`, `ContentHashStamp.TableDigests … now has a second, non-table
  caller`). **Nothing for a combat-ai session to do here** — recorded so the next one does not
  re-derive the condition or reach into another program's file.
- **`RendezvousLane` combo-skill proposer** — named in the ideal as later work, out of this plan.

- [ ] **CAI-guard-1 — the pinned `BattleEffects.cs` baseline moved in CAI1.12 and the guard was never re-pinned** · XS · deps: — · *(manager, 2026-09-20, found while attributing the four `FusionRpg.Guard.Tests` failures at the cai-sink lane tip `e37a9f58`)*
  `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs:99` (`BattleEffects_is_byte_identical_to_its_current_core_baseline`) pins the SHA256 of `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` at `:111` to `52F843B035FD9BF62C3E79EF65119ACA2B09C76C544F429F9477BDBADBFEC49E` (re-pinned 2026-09-09, per its own comment at `:108`, after the unrelated `AttackerEdge` addition in `9aad045`).
  The file's committed bytes are now `02B04A25BC9ADB37533D0973EF7C2E02D2E7734128D39112BC554B81F21CC00B`, so the guard is RED — and it has been since `c3bb0ba2` (CAI1.12, the per-place executor allowlist), the newest commit touching that file and an ancestor of `features/mega-merge`. This program already records the size change (`tasks/combat-ai-todo.md:830`: "`BattleEffects.cs` 384 → 447 (CAI1.12)"), but nothing re-pins the guard, so the move is currently an unexplained baseline drift (H1).
  **Remedy:** one commit that either re-pins the hash with CAI1.12 named as the cause in the message, or reverts the `BattleEffects.cs` half if that change was not intended. Never re-pin silently and never widen the guard to tolerate it. **Verify:** `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlantSideStatus"` green, plus the fragment.
  **Executor (fence ruling, manager 2026-09-20):** the fix is a guard edit and `gk-core/tests/FusionRpg.Guard.Tests/**` is protected by the pipeline hook, so this program's lane cannot carry it — a lane that tries is refused, exactly as `ssh27` was on `TuningRevisionLiteralGuardTests.cs`. The re-pin therefore rides the pipeline lane `tvb58`, which already holds `--allow-protected` and is opening the same test project for TVB-F4. The guard's own doc comment at `PlantSideStatusGuardTests.cs:92-98` is what makes a deliberate, cause-named re-pin the correct repair rather than a redesign: "A file-hash pin is the strongest form of 'byte-identical': any future edit to this file, whether or not it touches ExecApplyStatus, fails this test and forces a deliberate re-pin rather than a silent drift." `PlantSideStatusGuardTests.cs:111` is the only file-hash pin in the whole Guard project (checked 2026-09-20), so this is a single-site fix and not a family.
  **BLOCKED 2026-09-21 (lane `tvb58`, the executor this row names): the re-pin cannot land.** The pipeline
  hook refuses `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs` — *"Blocked by the orchestrator
  pipeline guard: protected pipeline file (guards, verify, ledger script, hooks, CI)"* — on two separate
  attempts, so the `--allow-protected` grant this row names is not in effect at that lane's edit boundary.
  **MEASURED AND MADE MECHANICAL 2026-09-23 (lane `cai3`, session `combat-ai-3`) — and this row's own cause attribution is SUPERSEDED, which matters because a re-pin that names the wrong cause is the silent re-pin this row forbids.** The test's `baselineHash` (`PlantSideStatusGuardTests.cs:114`) is **`02B04A25BC9ADB37533D0973EF7C2E02D2E7734128D39112BC554B81F21CC00B`** and its own comment says it was **re-pinned 2026-09-21 after CAI1.12 (`c3bb0ba2`)** — so the sentence above (*"The file's committed bytes are now `02B04A25…`, so the guard is RED — and it has been since `c3bb0ba2`"*) describes the state before that re-pin, not today's. **Today's drift has a different cause:** `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` is **465 lines** and hashes to **`E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35DA9835E8FB28799CA6733F8`**, and `git log --since=2026-09-21 -- gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` returns exactly **one** commit: **`5e33ad647` (2026-09-23, "fix(battle): T6 (W11) one gate owns combat.defense.omni")**, which changed it +23/-5 (447 → 465 lines) and did not re-pin the guard. That is a merged, reviewed commit from another program, so the re-pin is the deliberate one this pin exists to force rather than a revert candidate. **The remedy is therefore ONE LINE**, at `PlantSideStatusGuardTests.cs:114`, to `E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35DA9835E8FB28799CA6733F8`, with `5e33ad647` named as the cause in the commit message — and it still needs the `--allow-protected` grant, because `gk-core/tests/FusionRpg.Guard.Tests/**` is a protected path the hook refused lane `tvb58` on twice.
  Facts and the exact change for whoever holds the file: current bytes
  `02B04A25BC9ADB37533D0973EF7C2E02D2E7734128D39112BC554B81F21CC00B`, pinned
  `52F843B035FD9BF62C3E79EF65119ACA2B09C76C544F429F9477BDBADBFEC49E`; replace the `const string
  baselineHash` value with the current one and rewrite the two comment lines above it to
  *"Re-pinned 2026-09-21 after combat-ai CAI1.12 (commit c3bb0ba2, the per-place executor allowlist, Core
  half) changed this file's bytes; the previous pin (52F8…, 2026-09-09) covered the unrelated AttackerEdge
  addition (9aad045)."* Cause is in this branch (`c3bb0ba2`); `cai-sink` `04da1747` is not. Verify with
  `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlantSideStatus"` (6/6 green).

  **REOPENED 2026-09-25 after the accepted P1 battle repair at reviewed SHA `7b4e8ef582a0744e20f501562a4b28167e402c89`:** that commit intentionally changed `BattleEffects.cs` to report sink-retained damage, so the prior pin `E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35DA9835E8FB28799CA6733F8` is no longer the current byte contract. The live file hash is `946E578D0092A77EB8DD59FDAF8C48FD3113B6042E0E4FB627E921EAB2B43013`; the current manager repair `resume-09-battle-guard-repin-20260925` must re-pin the protected guard with this cause named, then run the focused PlantSideStatus test from a clean checkout. This is an H1 deliberate re-pin, not a request to widen or skip the assertion.

## Finding routed from `test-verification-boundary` (TVB-F16, 2026-09-21)

- [x] **TVB-F16 — two CI-tier guards are red at the merged head on this program's files** · **DUPLICATE —
  ALREADY CLEARED, CLOSED 2026-09-21** (lane `combat-ai-3`). Both findings this row names are the same two
  findings `CAI-guard-2` fixed (`5fd0feba`, lane `combat-ai-2`), filed from the other program's side. It is
  closed against its own acceptance by re-measurement, not by pointing at that row. Found while
  verifying TVB5.8.3 (`pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` → exit 1, `guards failed:
  doc-citations, magic-numbers, population-pin`; the doc-citations half is another program's, TVB-F15):
  - `guard-magic-numbers` M1: `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:76` and `:77` — "bare numeric
    literal in a balance-surface file": `readonly List<string> _eligibleScratch = new(64);` and
    `readonly List<TargetCandidate> _candidateScratch = new(64);` (CAI1.9's file; the fix is a named
    capacity constant or a `[Trait]`-style exemption marker, per `docs/architecture/tunables-ssot.md`).
  - `guard-population-pin` P1: `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs:400` —
    `Assert.Equal(32, result.Count)` has no `pin:` marker (CAI1.14's measurement site; the population-pin
    standard wants the pin explained where the count is asserted).
  Both are gating in CI, so CC8 stays red until they clear. Owning program: combat-ai.
  - **Closed, both halves:** `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` → exit 0,
    `M1=0  M2=0  M3=0  M4=0`, `total 0 finding(s), 0 high` (the `64`s are now the named
    `const int DecisionScratchCapacity = 64;` at `Actions/Ai/CoreIntentPolicy.cs:84`, read by `:86-87`);
    `pwsh -NoProfile -File scripts/guard-population-pin.ps1` → exit 0, `total 0 finding(s)`, `clean` (the
    assertion now reads `Assert.Equal(cap, result.Count)` at `DecisionAllocationTests.cs:405`, `cap` from a
    `ScoringWeights` at `:401`). `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` → 21 guards,
    `magic-numbers ci gating 0` and `population-pin ci gating 0`, exit 1 with `guards failed: doc-citations`
    **only** — the notify-rail file move in notification-ssot / npc-story-events / trade-network /
    world-stage docs, filed in their owning todos, **0 findings in `docs/architecture/combat-ai/**`**.
    No guard, allowlist, `knownRed` entry or registry was
    touched to get here. See `tasks/evidence-fragments/TVB-F16.md`.

- [x] **CAI-guard-2 — two CI-tier guard reds at the merged head are this program's own files** · S · **DONE** (lane `combat-ai-2`, 2026-09-21):
  *(filed by the manager 2026-09-21. Measured with `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`
  at the integration head WITHOUT lane tvb58's merge, which reported the identical three reds
  `guards failed: doc-citations, magic-numbers, population-pin` — so they are pre-existing, not that lane's.)*
  - `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:76` and `:77` — **M1 HIGH** "bare numeric literal in a
    balance-surface file" (tag `[ai]`) from `scripts/guard-magic-numbers.ps1` (`M1=2  M2=0  M3=0  M4=0`).
    Fix by moving both literals into versioned tuning (`data/tuning/combat-ai.v*.json`) and reading them, or
    by showing the guard's own justification for a structural constant — no magic numbers on the balance
    surface (`docs/architecture/tunables-ssot.md`).
  - `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs:400` — `Assert.Equal(32, result.Count)`
    carries no pin marker (**P1**, 1 finding) from `scripts/guard-population-pin.ps1`. Fix by pinning the
    closed vocabulary/registry the 32 is derived from rather than the count itself — a guardrail asserts the
    CONTRACT, never a population reading (`docs/architecture/validation-ssot.md`).
  - Acceptance: `run-guards.ps1 -Tier ci` reports 0 red for `magic-numbers` and `population-pin`.
  - Verify: `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1`; `pwsh -NoProfile -File scripts/guard-population-pin.ps1`
  - **Result:** both guards clean (`M1=0  M2=0  M3=0  M4=0`, 0 findings; population-pin clean), and
    `run-guards.ps1 -Tier ci` now reports **only `doc-citations`** red — the attributed notify-rail
    migration in other programs' docs (20 HIGH, none in `docs/architecture/combat-ai/**`). The `64`s
    became the named, documented `DecisionScratchCapacity` (the guard's own structural-const
    justification, the same shape as `CostLedger.StackCostRows`), and the count assertion now reads
    `Assert.Equal(cap, result.Count)` with `cap` from a `ScoringWeights`. Behaviour unchanged:
    DecisionAllocationTests 12/12, CoreIntentPolicyTests 8/8, BattleGolden 5/5, boundary 15104/0.
    See `tasks/evidence-fragments/CAI-guard-2.md`.

- [x] **`CAI-mask-1` — the row walk carried `long` status masks around a `ulong` bitfield, and the one
  `unchecked` cast was the repo's last overflow-audit finding** · XS · **DONE** (lane `combat-ai-3`,
  2026-09-21; found by `CP1`'s sixth row).
  `Actions/Ai/AiRowSelector.cs`'s `AiRowFacts` declared `long SelfStatusMask, long TargetStatusMask` while
  the only source is `EntityFacts.StatusMask` (`Effects/Atoms/FactReader.cs:43`), which is **`ulong`** — so
  `CoreIntentPolicy.cs:313` and `:323` reinterpreted it with `unchecked((long)…)`. A status mask is a
  **bitfield, not a magnitude**, so no value was ever at risk; but the reinterpret forced an `unchecked`
  cast, and `audit-overflow.py`'s A6 rule ("unchecked on a magnitude path — overflow must throw, not wrap")
  matched the line-level filter because `TargetHpMilli` sits on the same line. It was the only A6 finding
  left in the repo, and it was being carried as "pre-existing, documented".
  **Fixed at the root, not muted:** both masks are now `ulong` (the real type), the bit tests read `1UL`,
  and both `unchecked` casts are gone — `python gk-core/scripts/audit-overflow.py` is now
  `A2=0 A3=0 A4=0 A5=0 A6=0`, **0 findings repo-wide**. No exemption marker, guard, allowlist or `knownRed`
  entry was used. **Behaviour is bit-identical:** C# masks a 64-bit shift count by 63, and AND-then-`!= 0`
  answers "set" for exactly the same bits either way — the two new tests walk all 64 indices of a mask
  with only bit 63 set, which also closes the fact that `HasStatus`/`TargetHasStatus` had **no test at
  all** before this.
  `spec-profile-schema.md:293` (which quoted the old `long`) is corrected in the same commit. Ai filter
  4617/0 (+2), siege 333/0, goldens 16/0, `verify-change` **15114 passed / 0 failed** across 13 boundaries.
  See `tasks/evidence-fragments/CAI-mask-1.md`.

- [x] **`CAI-pp1` — `ProvePredictor` re-measured at the merged head, for every row that quotes it** · XS ·
  **DONE** (lane `combat-ai-3`, 2026-09-21). `CP2`'s second clause, `CP3`'s third, `CAI2.3` and `CAI3.6`
  all read *"`ProvePredictor` under `1e-4`"*, and the last recorded numbers were taken at `CAI2.3`'s
  identity slice — **before the mega-merge and before wave 4's Core landings**. Re-run here rather than
  inherited: `dotnet run --project gk-core/tools/ProvePredictor -c Release` → exit 0, **all four scopes PASS** at
  1e-4 — core path max abs diff **2.827E-007**, Theta-invariance (Theta=10 vs 5000) **3.495E-006**,
  actions-only **8.836E-007**, actions+status **8.836E-007**. `gk-core/tools/ProvePredictor/**` is inside this
  lane's fence, so this is a measurement, not a routing. **`gk-forge/tools/DominanceBaseline` is the other half of
  those clauses and stays routed** (`R-DOMINANCE`). See `tasks/evidence-fragments/CAI-pp1.md`.


- [x] **`CAI-cite-1` — the combat-ai specs' `file:line` citations, sized so the sweep is not guesswork** ·
  M · deps: — · **CLOSED 2026-09-21** (lane `combat-ai-3`): **39 citations re-anchored across 12 specs**, every
  one by reading the citing prose and the named member's real declaration, and **4 sites deliberately left
  alone** because their prose is about a past state and says so on its own line — which is the acceptance's
  second clause. Zero superseded anchor strings remain in the 23 scoped documents. *(filed by lane
  `combat-ai-3`, 2026-09-21, from the Deferred finding below; owner: whichever program next edits these
  specs — this one, since the specs are this program's)*
  The Deferred section already records that these specs "carry `BattleRunState.cs` line numbers that no
  longer resolve to the method they name", that `combat-ai-ideal.md` was never re-anchored after the
  CAI1.11/CAI1.12 code moves, and that the guard cannot see any of it because
  `audit-doc-citations.py` checks **bounds, not content** (`--scope docs/architecture/combat-ai
  --summary` → `D1 7 (0 HIGH), D2 0, D3 0, D4 0`; all 7 D1 are LOW reads of files the specs *propose*).
  **Measured size, so the next owner starts from a number:** 23 documents, 1167 resolvable citations, and
  a symbol-vs-line check (every backticked identifier on the citing line must appear within ±30 lines of
  the cited line in the cited file) reports **874 checked / 101 suspects**. That 101 is an **upper bound,
  not a defect count** — the heuristic cannot tell a namesake (`BattleGoldenTests` on a line citing
  `BattleRunState.cs`) from a genuinely moved symbol.
  - **Why it is filed rather than swept blind:** re-anchoring is only correct where the prose describes
    *current* behaviour. `CAI1.11`'s fragment records that several of these citations deliberately quote a
    **pre-fix defect** ("the affected prose describes the *pre-fix defect* … which re-anchoring would
    falsify"), and the same is true of `spec-*` §"why this was wrong" sections. A mechanical pass over 101
    sites would falsify documentation to make a number look tidy — the opposite of the rule it cites.
  - Acceptance: the citations the Deferred section names by file (`spec-intent-router.md`,
    `spec-ai-tiers-personality.md`, `spec-core-scorer.md`, `spec-delve-automated-wiring.md`,
    `spec-lawn-*`, `spec-siege-loadout-wiring.md`, `spec-stance-wiring.md`, `spec-aggression-tier-map.md`,
    `spec-profile-schema.md`, `combat-ai-ideal.md`) each resolve to the symbol their prose names, and any
    citation whose prose is *deliberately* about a past state says so on its own line — which is also the
    guard's own exemption rule.
  - Verify: `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary`;
    `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`.
  - **Landed across this lane's sessions (2026-09-21): 34 citations re-anchored in 12 specs.** Every one was
    found by reading the citing prose, naming the member it describes, and reading that member's real
    declaration — never by pattern-matching a line number.
    1. `spec-aggression-tier-map.md`: the `ai.aggression` composition, `:1003-1011`/`:1010-1011` → `:1025-1033`/
       `:1032-1033` (6); and the registry's own registration, `:290-291` → `:294-298` (3).
    2. `spec-intent-router.md` (3), `spec-ai-tiers-personality.md` (4), `spec-delve-automated-wiring.md` (1 +
       1) and `spec-profile-schema.md` (1): `DefaultAiIntentSource`'s build site, `:627-630` → `:687-699` (9),
       plus the actionCatalog degradation `:549-558` → `:597-604` (1).
    3. `spec-siege-loadout-wiring.md`: `BindContainers` `:707-738` → `:787-818` (1) and its `ArgumentException`
       `:720-723` → `:795-797` (1); `spec-decision-inspector.md`: the formatter `CandidateScorer.cs:266-307` →
       `:309-417` with its four sub-anchors (1); `spec-decision-perf.md`: `TryPay`'s empty-rows early return
       `CostLedger.cs:69-70` → `:135` (1).
    4. The `622-641` and `540-596` clusters — 11 citations in 6 specs, where the prose names different things
       but every citation pointed into the same stale window: the stance seam `:629` → `:194` (2 specs); the
       AI source `:628-630`/`:622-631` → `:687-699`/`:672-699` (4); `EffectiveRungOf` `:640-641` → `:708-709`
       (3); ST2 named by number `:637-641` → `:702` (2); `EquippedActionIds` read `:540` → `:582` (1); the
       basic-attack fallbacks `:540-547` → `:595-620` (2); the loadout compile `:540-585`/`:540-582` →
       `:582-640`/`:582-624` (2).
    5. Closing slice: `CostLedger.Check` `:72` → `:105` (1); the delve striker basic-attack fallback
       `:544-547` → `:595-620` (1); `LiveActorKeys` `:775-783` → `:877-885` (3, whose body filters
       `if (a.Active)` at 882).
    A python sweep of the 23 documents for the superseded anchor strings reports **NONE** left, the scope's
    audit counts are unchanged (`D1 7 (0 HIGH)`, `D2/D3/D4 0`), and `guard-doc-citations.ps1 -Strict` reports
    **0** lines mentioning `combat-ai/`.
  - **Remaining, and why it is not a blind sweep:** the rest of the ~52 `BattleRunState.cs` citations plus
    the `BasicAttack.cs` cluster across the other specs. A mechanical pass over those would falsify
    documentation: `CAI1.11`'s fragment records that several deliberately quote a **pre-fix defect**
    ("the affected prose describes the *pre-fix defect* … which re-anchoring would falsify"), so each site
    needs its prose read. The 101-suspect upper bound above is the queue for whoever takes it.
  - **A third class was read and deliberately NOT touched — `combat-ai-ideal.md`'s own lines 113, 142 and
    169, the three the Deferred finding names.** They are not stale locations. `:169`'s row sits in the
    **historical baseline table** whose header at `:164` reads *"Allocation and cost today (the perf claims
    must start from here)"*, and `CAI1.14` has since closed exactly its two rows (`CostLedger.RowsFor`, the
    `BloodthirstyView` allocation) — so editing them would claim current behaviour for a baseline, or erase
    the baseline the perf claims were measured against. `:113` quotes a cascade whose **shape** changed
    (`intentSource ?? … ?? new StubIntentSource(…)` → `router.Compose(policy: …, fallback: …)` at
    `BasicAttack.cs:176-177`), so a line-number bump would leave a quote that no longer exists in the file.
    `:142` has one correct citation (`:152`), one moved (`:165` → `:177`) and one superseded by `CAI1.11`
    (the `loyal` redirect is now the router's `EffectiveTargetOf`, `BasicAttack.cs:204-205`). All three are
    tabulated in the fragment as the measured false-positive class inside the 101 — the bound means "101
    sites need a human read", never "101 defects".
  - Verify: `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary`;
    `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`. See
    `tasks/evidence-fragments/CAI-cite-1.md`.

- [x] **`CAI-guard-4` — the `guard-magic-numbers` M1 red on `Actions/Ai/` is ALREADY CLEARED (filed by the ssh28 lane as "CAI-guard-2")** · XS · **DUPLICATE OF `CAI-guard-2`, CLOSED 2026-09-21** (lane `combat-ai-3`, on the merge).
  *(**Id renamed on merge:** the incoming text reused `CAI-guard-2`, which this todo already carries as the row that fixed exactly this finding. Two rows with one id would have confused the ledger and the queue.)*
  Cause read, and the file it names: this is the same pair of literals `combat-ai-2` fixed in `5fd0feba`.
  The observation is **stale, not wrong** — measured with git: `5f51d6fc` (the ssh28 lane's observation head)
  **is an ancestor of** `5fd0feba` (`git merge-base --is-ancestor 5f51d6fcd492 5fd0feba` → true), so the red
  was real when seen and the fix landed afterwards. At the merged head the literals are the named
  `const int DecisionScratchCapacity = 64;` (`gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:84`) read by
  both scratch lists at `:86-87`, and **this row's own finding is gone**: `M1=0`.
  ⚠ **The GUARD still exits 1 at the merged head, on another program's new file — not on this one.**
  `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` → exit 1, `M1=0  M2=1  M3=0  M4=1`, total 2
  findings (1 high), **both** at `gk-core/src/FusionRpg.Server/ComboPricingBoot.cs:46`
  (`public const int TierLadderRungCount = 1;` — M2 "const with balance vocabulary", M4 "tunable with no
  unit"). That file arrived with `features/mega-merge` and is outside this lane; it is routed to its owning
  program (`strain-splice-host`) in this same commit. So "M1=0" is this row's closure and "the guard is
  green" would be false — said explicitly rather than quoted from the pre-merge run.
  See `tasks/evidence-fragments/TVB-F16.md` (the same re-measurement, made for the same finding when TVB
  routed it in) and `tasks/evidence-fragments/CAI-guard-2.md`.

- [x] **`CAI-guard-5` — the `guard-population-pin` P1 on `DecisionAllocationTests.cs:400` is ALREADY CLEARED (filed by the ssh28 lane as "CAI-guard-3")** · XS · **DUPLICATE OF `CAI-guard-2`, CLOSED 2026-09-21** (lane `combat-ai-3`, on the merge).
  *(Id renamed on merge for the same reason as `CAI-guard-4`.)*
  At the merged head the assertion reads `Assert.Equal(cap, result.Count)`
  (`gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs:405`) where `cap` is
  `new ScoringWeights(…).MaxCandidatesScored` (`:401`) — so the remedy the incoming row asks for ("compare
  against the same named cap") is what shipped, and **this row's own finding is gone**.
  ⚠ **The GUARD still exits 1 at the merged head, on another program's new test — not on this file.**
  `pwsh -NoProfile -File scripts/guard-population-pin.ps1` → exit 1, total 1 finding, at
  `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:70`. That file arrived with `features/mega-merge`
  and is outside this lane; it is routed to its owning program (`strain-splice-host`) in this same commit.
  See `tasks/evidence-fragments/TVB-F16.md`.

- [x] **`CAI-perf-1` — `CAI4.7`'s `PerfSection` index presupposes a residue that has not landed** · XS · deps: —
  · **CLOSED 2026-09-23 (lane `cai2`, session `combat-ai-2b`) by remedy (a).** `gk-core/src/FusionRpg.Core/Diagnostics/**` is in this lane's fence, so the residue was landed rather than re-stated: `PerfSection` now runs `LoopTick = 0` … `LawnMoveDrain = 24`, **`AiDecide = 25`** (CAI1.14's filed residue) and **`LawnAiDecide = 26`** (CAI4.7's line), with `SectionCount = 27` and both names appended to `SectionNames` in index order. So CAI4.7's acceptance reads exactly as written and no erratum is needed. The "must match PerfSection's member count" comment is now **enforced** rather than asserted: `PerfProbeTests.PerfSections_match_the_enum_the_names_and_this_bound` records every member once and asserts the snapshot holds exactly one name per member (a member past the bound is dropped silently by `PerfProbe.Measure`), plus the two names by name. Planted violation: reverting `SectionCount` to 25 kills it (1 red), reverting the revert restores 1 pass. `FusionRpg.Core.Diagnostics.Tests` **18 passed / 0 failed**. See `tasks/reports/CAI-perf-1.md`. **Superseded (kept for history):** the row was BLOCKED on a fence or an erratum (lane `combat-ai-3`, 2026-09-21).
  Measured at `cb1405011`: `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` runs `LoopTick = 0` …
  **`LawnMoveDrain = 24`** (25 members, 0..24) with `const int SectionCount = 25` at `:51`, and
  `grep -n "AiDecide\|LawnAiDecide\|ai.decide\|lawn.ai.decide"` finds **NONE**.
  So `CAI1.14`'s filed residue (`AiDecide = 25`, `SectionCount = 26`) is **unlanded**, and `CAI4.7`'s
  acceptance — "`PerfSection.LawnAiDecide = 26`, `SectionCount = 27`, `"lawn.ai.decide"` — CAI1.14 took 25
  (plan correction 1)" — is only reachable if that residue lands **first**. Its files
  (`Core/Diagnostics/**`, `Core/Stats/Derived/**`) are outside every combat-ai lane's fence, so a lane that
  takes `CAI4.7` and adds only `LawnAiDecide` lands it at **25** with `SectionCount = 26` and its own
  acceptance becomes unreachable.
  - **Remedy (a):** a lane holding `Core/Diagnostics/**` lands `CAI1.14`'s residue first, then `CAI4.7`'s
    `26`/`27` are reachable as written.
  - **Remedy (b):** an erratum restates `CAI4.7`'s acceptance to what the enum actually reads when it lands
    — the same shape as the plan's own "Correction 1" for the earlier index collision.
  - Also corrected in this commit: the Deferred entry below said "`PerfProbe.cs:36` ends at
    `LawnMoveDrain = 24` today"; it is at **`:40`** (`:36` is inside the `KernelSchedule` comment block). The
    entry's index (25) and count (26) claims are right; only the line number moved.
  - Verify: `grep -n "LawnMoveDrain\|SectionCount" gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`. See
    `tasks/evidence-fragments/CAI-perf-1.md`.

- [x] **`CAI-cite-2` — `docs/research/combat-ai/**` cites two files this repo deleted, and no lane holds that path** ·
  XS · deps: — · **CLOSED 2026-09-22** (lane `cai4`, session `combat-ai-4`). This lane's fence **does**
  include `docs/research/combat-ai/**`, so the ruling this row was waiting on was simply "execute remedy
  (a) here". **Remedy (a) applied to all 14 findings, plus 2 unflagging siblings for consistency**
  (`S2-delve.md:24,28` name the same two deleted/shrunk files): the scope is now
  `D1 0  D2 0  D3 0  D4 0` (9 documents, 253 resolvable citations), and the D3 site was fixed by
  **qualifying the path** — the bare `Program.cs:217-219` is now `gk-core/src/FusionRpg.Server/Program.cs:240`,
  re-read today. `guard-doc-citations.ps1 -Strict` reports **no `combat-ai/` line** (it is red on 7 other
  programs' documents, which is pre-existing and not this program's), and
  `--scope docs/architecture/combat-ai` is unchanged. See `tasks/reports/CAI-cite-2.md`.
  **Named as still owed, deliberately not swept here (a distinct finding, filed in the Deferred section):**
  the **content**-level half — `docs/research/combat-ai/**` cites `BasicAttack.cs:163-165`, `:152`,
  `:189-191`, `:193-216`, `:489` and `TimelineDispatch.cs:79-80` at line numbers that moved in
  CAI1.10/CAI1.11 (`BasicAttack.cs` is 654 lines today). The remedy there is a **pre-fix note, not a
  re-anchor**, because those lines describe the defect the program has since closed.
  *(Filed 2026-09-21 by lane `combat-ai-3`; the text below is kept as the row's own sizing.)*
  Eight LOW `D1` findings, all in `docs/research/combat-ai/`: six name `RaidIntentSource.cs` /
  `RaidIntentSourceTests.cs` — **both deleted by this program in `c284f5f6d` (CAI1.10, "two routers
  deleted")** — one names `BattleStatComposerTests.cs`, **deleted by `3689f35b1`** (actor-hub Wave 1a + T5;
  `BattleStatComposer` is the closed incident the repo's rules say never to copy), and one names
  `lawn-combat-ai.v1.json`, a **rejected** alternative that was never created.
  - **Why invisible until now:** these are the pre-implementation survey documents (`S1`–`S3`, `AUDIT.md`),
    and the audit routes `docs/research/**` to **LOW**, so the CI-tier `doc-citations` gate never saw them —
    `guard-doc-citations.ps1 -Strict` reports **0** lines mentioning `combat-ai/`.
  - **What is not wrong:** citing `RaidIntentSource.cs` was correct when written; this program deleted the
    type afterwards. So this is the same shape as the four self-labelled past-state sites `CAI-cite-1`
    refused — except these lines do not say the file is gone, and the audit's own remedy is *"Fix the
    citation, or say on that line that the file is gone"*.
  - **Remedy (a):** add the exemption note on the seven lines (`deleted by CAI1.10 (c284f5f6d)` /
    `deleted by 3689f35b1`) — the audit's sanctioned fix, seven short edits.
  - **Remedy (b):** re-point the six raid refs to what replaced them (`Actions/IntentRouter.cs`,
    `Actions/IntentRouterTests.cs`) — truer for a reader, but it edits the survey's *findings*, not just its
    citations, so it is a content decision.
  - Either way **`docs/research/combat-ai/**` is outside every combat-ai lane's fence**, which is why this is
    filed rather than executed and why the Deferred paragraph has said for two days that it "needs a routing
    decision, not a guard fix". This row is that decision, sized.
  - Reproduce: `python scripts/audit-doc-citations.py --scope docs/research/combat-ai --targets D1`. See
    `tasks/evidence-fragments/CAI-cite-2.md`.
  - **Completed the size the same day: it is not only D1.** The same scope reports **`D2` 5** and **`D3` 1**
    (all LOW) — the identical "cannot be opened or resolved" class, measured before this row shipped:
    - **5 `D2`** cite `SiegeAi.cs` at `:135`, `:96-103`, `:145-195`, `:220-239` (× 2) while that file is now
      **75 lines** — `CAI1.1` moved the scorer out of it into `Actions/Ai/CandidateScorer.cs`, so every one
      of those ranges is past the end of the file it names. Files: `AUDIT.md:33,41,74`,
      `REVIEW-B.md:56`, `S1-battle-core.md:25`.
    - **1 `D3`** cites a bare `Program.cs:217-219` (`REVIEW-A.md:21`) where **42 files** share that basename,
      so the line number cannot be checked at all — the audit's own advice is "cite a path, not a bare
      basename".
    **Total for this row: 14 LOW findings (8 D1 + 5 D2 + 1 D3) in 5 documents, from three causes — a deleted
    program-owned type, a deleted other-program type, and one file this program shrank.**

- [x] **CAI-F1 — no lane can publish `combat-ai.v2/v3`: both readers name `combat-ai.v1.json` by hand** · S · deps: — · **CLOSED 2026-09-23 (lane `cai2`, session `combat-ai-2b`)** by the row's own option (a) — the tuning-file constant — and with the publish it was blocking. **Landed:** `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiTuningFiles.cs` (`Current = "combat-ai.v2.json"`, the `SocketTuningFiles.Current` pattern copied rather than re-invented); `Server/Program.cs` and `Injector/Host/RpgHost.cs` now read `CombatAiTuningFiles.Current` instead of a literal, so the filename and the readers move together and the failure the row names (a published file with no reader, or a reader at the wrong file) is impossible rather than merely avoided; and the revision itself: `gk-core/data/tuning/combat-ai.v2.json`, published in ONE `publish.py` invocation (`--add-key :lawn={...}`, the empty-container root form), carrying **CAI4.7's lawn section** — `lawn.trigger.swingsPerDecision` **7**, `.ticksPerDecision` **50**, `.postCastLockTicks` **10**, `.offsetStream` `"lawn.ai.offset"` (spec §287-306), with the four STRUCTURAL values deliberately absent because they are code consts. **Proven rather than asserted:** a JSON diff shows the publish is a **pure addition** — `profiles` and `router` are `DeepEquals` to v1's — so `BattleGolden` + `Siege` **338 passed / 0 failed** (no golden moved) and a match pinned to `v1` still replays under `v1`; the value is read back through the SHIPPED parser (`CombatAiTuningLoader`) from the file `Current` names, in `CombatAiTuningRevisionTests` (**3 tests**), and `SiegeKeyMigrationTests.Both_hosts_load_the_same_file` now asserts both hosts reference the CONSTANT and contain **no** `"combat-ai.v` literal — the anti-drift contract this row was really about. `guard-tuning-immutability` exit 0; `guard-dal`/`guard-single-writer`/`guard-actor-hub` exit 0; `resource_ownership.py --check` **166/166**; Server build succeeded. See `tasks/reports/CAI-F1.md`. **Superseded (kept for history):** *(found by lane `cai4`, 2026-09-22, while preparing CAI4.7; routed by the manager)*
  - **Measured:** the tuning readers are `gk-core/src/FusionRpg.Server/Program.cs:248` and `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:89`, and both name `combat-ai.v1.json` **literally**. So an H7 publish (`gk-core/tools/tuning/publish.py`, `v{n+1}`) cannot land with its readers in the same commit without editing two files that sit outside every combat-ai lane's fence — the lane is blocked by construction, not by difficulty.
  - **Why it is H7 and not a preference:** the rule exists so a published revision and the code that reads it land together; a hand-named revision means the publish either has no effect (readers keep v1) or ships unread. `data/tuning/combat-ai.v3.json` already exists and is read by nothing.
  - **Fix:** route the revision through the existing tuning-file constant pattern the other domains use (`SocketTuningFiles` was moved to a constant for exactly this reason), or add the readers' files to a lane's fence deliberately and do the publish in one commit. ⛔ Not a `v3` copy with a v1 name, and not an allowlist widening.
  - **Verify:** publish a revision and prove a reader picks it up (read the value back through the normal path), plus `python gk-core/scripts/guard-tuning-immutability.py` and `python gk-core/tools/tuning/resource_ownership.py --check`.

- [x] **`CAI-cite-3` — the two remaining in-fence citation sweeps** · M · deps: — · **CLOSED 2026-09-22** (lane `cai4`, session `combat-ai-4`). This is the work `CAI-cite-1` left as its remaining queue ("the rest of the ~52 `BattleRunState.cs` citations plus the `BasicAttack.cs` cluster across the other specs"), and the lane fence is what it was waiting on: `docs/architecture/combat-ai/**` **and** `docs/research/combat-ai/**` are both in this lane. Both combat-ai doc scopes are now **`D1 0, D2 0, D3 0, D4 0`** (21 docs / 938 citations and 9 docs / 253 citations), and `guard-doc-citations.ps1 -Strict` reports **0** `combat-ai/` lines. **Re-anchored** (prose about current behaviour): 6 sites in `spec-aggression-tier-map.md` (the `ai.aggression` composition `:1025-1033`/`:1032-1033` → `:1037-1044`/`:1043-1044` — `:1025-1033` is `ObjectivePositionOf`), `spec-lawn-held-actions.md:238` (`:582-624` → `:582-638`, the sort is at `:635`), `spec-lawn-held-actions.md:120` (`CheatState.cs:215-220` is `ApplySpeciesAllocations`; the ptr→Bound resolver is `:280-285`), and `spec-core-scorer.md:387` (`SiegeTuning.cs:333-375` → `:333-367` plus a dated note that module 2 **has** landed, because the prose still said "until module 2 lands" while the cited comment said the opposite). **Annotated as pre-fix, not re-anchored** — the refusal `CAI-cite-1` recorded for its four past-state sites: nine sites in `docs/research/combat-ai/**` (`AUDIT.md:32,37,39,62,66`, `S1-battle-core.md:10`, `S4-lawn.md:33`, `REVIEW-B.md:57,61`) now name what closed each defect (`CAI1.10`/`CAI1.11`/`CAI1.14`) and the successor site. **Marked not-yet-existing:** `spec-lawn-cast-trigger.md:457` (`lawn-combat-ai.v1.json`, never created), `spec-replay-identity.md:67` (the Data third's and CAI2.2's test files), `:135` (`mode-profiles.v1.json`, `lawn-tuning-profile`'s). **The 18 remaining heuristic suspects were each read and judged artifacts** (the symbol belongs to the next clause of the same sentence) — the heuristic is a prompt to read, never a defect count. **Out of fence, named:** `combat-ai-ideal.md:171` still cites `BattleRunState.cs:628-630` for `NoStanceHeld.Instance`; the seam is now `:194` (`CAI3.1`), and the ideal is a sibling file outside this fence. See `tasks/reports/CAI-cite-3.md`.

- [x] **`CAI-loop-1` — the four wave-4 Core halves run together** · M · deps: — · **CLOSED 2026-09-22** (lane `cai4`). Filed because each half's own suite was green and **none had ever run against another**. `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopTests.cs` composes them where they actually meet, in Core, with nothing stubbed but two actors' board reads: **(1) the decision** — the REAL `CoreIntentPolicy` at `AiPlace.Lawn` over module 16's store picks an action the store holds and the nearest enemy, and declares `None` for a species the store never pushed *while another species holds a kit*; **(2) the cast** — the edge → `LawnDecisionBudget` → `LawnCastTokenPool` → `LawnCastPlan`, with the ledger's rows built from each action's OWN `CompiledAction.Costs` (the same projection battle uses, `BattleRunState.cs:662`) and `rungOf` the REAL `EffectiveRungResolver` at the lawn's floor of 1, proving charged-once + the cooldown + the `OnActivate`/`HitCount 1` event + a one-short pool refusing with `ShortfallResourceId` + **a rung-5 action costing strictly more than a rung-1 one**; **(3) the order** — the admission rules feed the queue the REAL `IntentRouter` reads (live at `IssuedTick + lifetime - 1`, expired at `+ lifetime`, retryable stays live, terminal removes). **Acceptance:** the filter → 4 passed / 0 failed; `verify-change` exit 0 (`core-balance` 287/0); `guard-actor-hub` OK; `audit-overflow --targets A3` exit 0. **Mutations, each killing its named test:** the plan's cooldown start removed (1 red), `LawnOrderQueue.Expire` a no-op (1 red), `HeldFor` made to hand out another species' kit (1 red — and inert until the no-kit test was strengthened, which is the weakness that fix removed), the test's own `RungOf` forced flat (1 red). **What this is NOT:** the production host — `LawnDecisionHost` (CAI4.8) is what will run this loop, and a green test here says the halves fit, never that a lawn creature casts in a live match. See `tasks/evidence-fragments/CAI-loop-1.md`.

- [x] **`CAI-tests-1` — move the wave-4 Core tests to the project their rows name** · S · deps: — · **DONE 2026-09-23 (lane `cai2`, session `combat-ai-2b`).** The row was filed as blocked on *this lane's* fence (`gk-core/tests/FusionRpg.Core.Match.Tests/**`); lane `cai2`'s fence is `tests/**` broadly, so it was executable here rather than waiting for a widening. **Landed:** all **TEN** files (the row says seven — three more `CombatAi/*.cs` files have landed since it was written, and the row's intent is the DIRECTORY, so all ten moved) from `tests/FusionRpg.Core.Balance.Tests/CombatAi/` to `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/`, via `git mv` so the history follows, with each file's namespace rewritten `FusionRpg.Core.Tests.CombatAi` → `FusionRpg.Core.Tests.Match.Ai` to match its new home. `tests/FusionRpg.Core.Balance.Tests/CombatAi/` **no longer exists**; nothing outside those files referenced the old namespace (checked), and the Balance project still builds. **Both of the row's measured reasons are now facts:** (a) the moved tests resolve to the **`core-match`** boundary — `verify-change.ps1 -PlanOnly` on `LawnOrderQueueTests.cs` prints `-> core-match (module)` with no `VERIFICATION BOUNDARY MISSING`, so those runs stop paying the whole `core` group; (b) `gk-core/src/FusionRpg.Core/Match/**` can now be added to that same focused boundary by its owner (`test-verification-boundary`), which is the follow-up the row names. **Readings:** `gk-core/tests/FusionRpg.Core.Match.Tests` **182 passed / 0 failed** (the ten moved files' tests plus the four that already lived there); `gk-core/tests/FusionRpg.Core.Balance.Tests` **Build succeeded**. **History note, deliberate:** the twelve mentions of `tests/FusionRpg.Core.Balance.Tests/CombatAi/` elsewhere in this todo are NOT rewritten — they describe where those tests lived when their rows landed, and a mechanical replace would falsify that record. Their current home is this row. **FOLLOW-UP MEASURED, not taken, 2026-09-23 (lane `cai3`, session `combat-ai-3`): the source-side row is one edit for its owner, and here are the five ids it needs.** The row's own reason (b) says `gk-core/src/FusionRpg.Core/Match/**` still resolves through `core-fallback`, and that "adding the source-side row is cheap". Measured: `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Match/Ai/LawnOrderQueue.cs') -AllowUnscoped -PlanOnly` prints **`-> core-fallback (module)`** and then the ENTIRE `core` group — **68 projects** at the last count, up from the 39 the row recorded — so every lawn-AI edit pays the whole split to verify one directory. The Match family is exactly **five** projects (`gk-core/scripts/verification-boundaries.v1.json`'s own `projects` map): `core-match` (`gk-core/tests/FusionRpg.Core.Match.Tests`), `core-matchadmittests`, `core-matchinjectcontracttests`, `core-matchruntimetests`, `core-matchvalidatortests`. So the edit is: add a `core-match-group` project listing those five, then a focused boundary over `gk-core/src/FusionRpg.Core/Match/**` pointing at it — 68 projects becomes 5. **Not taken here, deliberately:** this lane HOLDS `gk-core/scripts/verification-boundaries.v1.json` (it is in the brief's granted list) but not the registry's POLICY, and the row names `test-verification-boundary` as its owner; under-selection is the dangerous direction, and choosing which five projects cover a directory is that owner's judgement, not an inference from filenames. The measurement is here so the owner's change is mechanical. **Superseded (kept for history):** *(filed by lane `cai4`, 2026-09-22)* · **BLOCKED on this lane's fence: `gk-core/tests/FusionRpg.Core.Match.Tests/**`.** The four rows' `Files:` lines name `tests/FusionRpg.Core.Tests/Match/Ai/…`; that project has since been split, and **`gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/` now exists** — `core-test-projects.v1.json`'s own plan (`Match/**` → `FusionRpg.Core.Match.Tests`, referencing Core + Data), already hosting `ILawnBoardViewTests.cs`. This lane's tests live in `tests/FusionRpg.Core.Balance.Tests/CombatAi/` *only* because `gk-core/tests/FusionRpg.Core.Tests/**` was outside its fence, and now, for the same reason, so is the canonical project. **Two measured reasons this is worth doing beyond tidiness:** (a) `gk-core/tests/FusionRpg.Core.Match.Tests/**` has its **own focused boundary** (`core-match` → that one project), so those runs stop paying the whole `core` group; (b) `gk-core/src/FusionRpg.Core/Match/**` still resolves through `core-fallback` to the entire group (39 projects, ~15.7k tests, ~4 min per edit) — once the tests are there, adding the source-side row is cheap and the owner of that registry is `test-verification-boundary`. **Acceptance:** the seven `CombatAi/*.cs` files move to `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/` with their namespaces, `Balance.Tests` no longer carries a `CombatAi/` directory, and every command in the affected rows' evidence prints the same numbers. **Note for the manager before widening:** four active sessions claim `tests/**` broadly (`empire-progression-4`, `species-gear-chain-4`, `strain-splice-host-20260922`, `tvb58`), so confirm none is editing `Match.Tests/` at the time. Files: `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/**` (new home), `tests/FusionRpg.Core.Balance.Tests/CombatAi/*.cs` (seven, deleted).

- [x] **`CAI-status-2` — the four wave-4 specs' status lines after the Core halves landed** · S · deps: — · **CLOSED 2026-09-22** (lane `cai4`). All four specs still read **"Status: spec, 2026-09-20. Not built."** after their modules' Core halves shipped, were tested and were proven to compose, and their Project-structure tables still marked **"new; does not exist yet"** on files that exist and pass. A spec's status line is the first line `DESIGN-GATE.md` §0 sends a reader to, which is why this program has run this propagation twice already (`CAI-spec-status`, `CAI-ideal-status`). **Changed:** each of the four status lines now reads "part built" with the CAI id, names **what is owed and who owes it** (`CAI4.3`'s ptr registry; the Contracts `CastOrigin` field + the injector fire site; `PerfProbe`/`CAI4.8`/the H7-blocked revision; the two `DirectOrder` identity fields + the router hook + the Server endpoint + the injector host + `web/**`), and names **where the tests actually live** (the rows' own `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside this lane's fence — `CAI-tests-1`). The landed file rows are re-marked `landed (CAI4.x)`; every remaining "does not exist yet" marker is on an owed out-of-fence path. **Two further stale claims fixed:** `combat-ai.v1.json` "does not exist yet" in the trigger and commander specs — **CAI1.8 published it on 2026-09-20**, and it has no `lawn` section (the owed revision `CAI-F1` blocks). Each spec's design-gate checklist line citing the audit's exemption now carries a dated parenthetical saying which markers it still applies to. **Acceptance:** `grep -c "Not built"` on the four specs → **0, 0, 0, 0**; `audit-doc-citations --scope docs/architecture/combat-ai --summary` → **D1 0, D2 0, D3 0, D4 0** (unchanged; the repointed test paths resolve). No code, test or tuning file touched. See `tasks/evidence-fragments/CAI-status-2.md`.

- [x] **`CAI-cast-1` — the plan refuses an intent whose envelope names a different action** · XS · deps: — · **CLOSED 2026-09-22** (lane `cai4`). `LawnCastPlan.Build` charges `intent.ActionId` and arms `intent.Envelope`, and `ActionIntent` is a public struct, so a caller can pair one action's id with ANOTHER action's envelope — after which the ledger says "paid" and the cooldown says a different action is ready, with nothing reporting the disagreement. **Verified before declaring the hazard** (`DESIGN-GATE`: test the constraint): every `ActionIntent` construction in `src/` was read — `StubIntentSource` ×2, `SiegeAiIntentSource` ×2, `CoreIntentPolicy` (which looks the envelope up by the *same* id it returns), `InteractiveIntentSource` ×2 and `TimelineDispatch` all pair them by construction, **so the guard breaks no shipped caller**. The one place a wrong row can arrive is a lookup keyed by id, which is exactly what `commander-direct-orders`' owed order path will do. **Change:** refuse with `ArgumentException` naming BOTH ids, before the pay step; throws rather than degrades (a programming error, not state). No tuning, no new vocabulary. **Acceptance:** the cast-plan filter → **8 passed / 0 failed** (was 7); the new test also asserts nothing was charged or cooled on the way to the refusal; planted removal of the guard → 1 red. `verify-change` exit 0 (41 distinct projects, 0 failures). **Not claimed:** this does not make the owed order path correct — it makes the plan refuse a mismatched pair loudly when that path gets it wrong. See `tasks/evidence-fragments/CAI-cast-1.md`.

- [x] **`CAI-loop-2` — the loop through the REAL lawn view** · M · deps: — · **CLOSED 2026-09-22** (lane `cai4`). `CAI-loop-1` proved the four wave-4 halves compose, but it fed the policy a hand-rolled `IBattleView`; the production lawn view is **`LawnBattleView` (CAI4.1)**, the one thing between the board and every decision. `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopViewTests.cs` composes the real view with the real profiled policy and checks the two claims only the real view can carry: **(1) side comes only from the oracle** — the board is built so the two readings are *disjoint* (a raw `zombie` the oracle calls an ALLY, a raw `plant` the oracle calls an ENEMY, with a second raw zombie keeping its raw reading so it is a contradiction on two units and not a blanket flip), and the policy must target an oracle-enemy and never the oracle-ally; **(2) one derived resolve per actor per frame**, measured as (reads the policy demanded) vs (resolves the cache performed), so a disabled memo cannot pass. Four tests. **Mutations, each killing its named test:** `LawnBattleView.SideOf` replaced with the raw census side — **CAI4.1's own named mutation, now proven against the real policy rather than only in the view's suite** — and `LawnDerivedCache.Get`'s memo disabled (1 red each; the second only after the measurement was FIXED, since my first version counted *distinct* actors and a disabled memo still passed). Both planted in files outside this lane's fence, run, reverted: `git diff --stat` on `Actions/Ai/Lawn/` is empty afterwards. **Two of my own errors were found by the tests failing honestly** and are recorded rather than hidden: `SideOf` returns the *relative* side (an oracle-ally reads 0 = my side), and the argmax does not pick by distance between equal-scoring enemies — so claim 2's assertion is "the target is an oracle-enemy", not "the nearest one wins". **Acceptance:** the filter → 4/0; `verify-change` exit 0 (41 distinct projects, 0 failures); `guard-actor-hub` OK; `audit-overflow A3` exit 0. **Still not the production host:** `LawnActorViewHost` (CAI4.1) and `LawnDecisionHost` (CAI4.8) are what build these seams in a live frame. See `tasks/evidence-fragments/CAI-loop-2.md`.

- [x] **`CAI-open-1` — the wave-4 specs' Open questions that landed work has answered** · S · deps: — · **CLOSED 2026-09-22** (lane `cai4`). An Open question with a recommended default is a **decision deferred to a build**; once the build lands the question is settled, but the spec still reads as though it were not — so a reader who follows `DESIGN-GATE.md` §0 to the authoritative document finds a fork where the program took one branch. This is the same propagation family as `CAI-status-2` and the citation sweeps. **Eleven questions across six specs now carry a dated answer naming the task and the OBSERVABLE fact:** `spec-lawn-held-actions` 1 (option (a) shipped: the store takes no unlock-state input; the rung pricing is real, `CAI4.4`) and 2 (the map's dependency row now reads `— *(corrected: it reads no profile)*`); `spec-lawn-cast-trigger` 1 (module 2 landed — `combat-ai.v1.json` published by `CAI1.8`, no lawn section, H7-blocked by `CAI-F1`, and `lawn-perf-budget.v1.json` still absent per `LW1.1`), 2 (the map's row 19 and the ideal's `:138` both corrected — verified by reading both files today) and 3 (the counter accumulates, as the spec decided); `spec-lawn-cast-activation` 2 (the pool's timeout/idempotent-release backstop landed, `CAI4.7`); `spec-lawn-cost-authority` 1 (floor 1 pays / floor 0 throws, `CAI4.4`) and 2 (`CAI1.14` precomputed `RowsFor`; zero bytes measured); `spec-lawn-actor-view` 1 (both halves of the recommendation in force) and 2 (`CAI1.13`'s saturating clamp); `spec-commander-direct-orders` 3 (`AiDecisionOrigin { Policy, Order, Steered }` landed, `CAI2.4`). **Five remain explicitly open** with their blocking task named: the D6 deploy cap (`LW5.1`), module 15's revision seam, the rider scoping (blocked on the same two out-of-fence files), the `ChainSynthetic` producer, and ST2's status line (owed to `action-skill-tiers`). **Acceptance:** `grep -c "ANSWERED 2026-09-22"` → **11** across 6 files; `audit-doc-citations --scope docs/architecture/combat-ai --summary` → **D1 0, D2 0, D3 0, D4 0** (unchanged); no code, test or tuning file touched. See `tasks/evidence-fragments/CAI-open-1.md`.

- [x] **`CAI-status-3` — fifty-two Project-structure markers that said "does not exist yet" about files that exist** · S · deps: — · **CLOSED 2026-09-22** (lane `cai4`). Every spec's **Project structure** table is what a reader plans from, and **52 rows across 15 specs** still said `new; does not exist yet` (or the bold table-cell form) about files that exist today, are imported by a test project and pass — including the wave-1/wave-2 specs whose halves landed weeks earlier and whose *status lines* `CAI-spec-status` had already corrected. So `spec-profile-schema`'s table alone carried **seven** false claims (`AiVocabulary.cs`, `CombatAiProfile.cs`, `CombatAiTuningLoader.cs`, `CombatAiProfilePolicy.cs`, `AiRowSelector.cs`, `combat-ai.v1.json`, `siege.v2.json`) for a module whose status line correctly said built. **Not a blind flip — three sites needed reading, and each was read:** `spec-commander-direct-orders.md:72` is about the two additive **fields** on `DirectOrder`, not the file (the file exists, the fields do not) so it now says so; `spec-core-scorer.md:76`'s marker carried a reason ("the type moves out of `SiegeAiIntentSource.cs:316-351`") and the move is **done**, so it now says the moved-out state; and `spec-delve-automated-wiring.md:323` is **not a marker at all** — a *quotation* of `IBattleView.cs`'s own doc text — so it is **left exactly as it is** (a pattern match would have made the spec misquote the file it cites). **The change:** 52 markers now read `(new — **landed**, <task>)` with the task derived from the path and confirmed against the ledger's `done` list (`CAI1.1`–`1.4`, `1.6`, `1.8`–`1.10`, `1.12`–`1.14`, `CAI2.3`, `CAI3.1`, `CAI3.3`, `CAI3.4`, `CAI4.1`, `CAI4.4`, `CAI4.9`); nothing else on any line changed (53 insertions / 53 deletions, one line each). Every marker whose path genuinely does not exist is **left saying so** (Injector/Server/Contracts/web rows, `lawn-perf-budget.v1.json`, `combat-ai.v2/v3.json`, the `DirectOrder` fields). **Acceptance:** the residual-marker script → **1** left, and it is the `IBattleView.cs` quotation; `audit-doc-citations --scope docs/architecture/combat-ai --summary` → **D1 0, D2 0, D3 0, D4 0** (unchanged — and note that flipping a marker *removes* that line's D1 exemption, so its citations become live claims, and they resolve). No code, test or tuning file touched. See `tasks/evidence-fragments/CAI-status-3.md`.

- [x] **`CAI-guard-3` — the lawn AI's Core contract, enforced instead of asserted in prose** · S · deps: — · **CLOSED 2026-09-22** (lane `cai4`). Four specs state the same rules in prose and every one recorded the same honest gap — `spec-lawn-cast-trigger.md`'s design-gate checklist says *"the rule 'the lawn reads exactly one time base' … is currently covered only by this module's tests"*. A rule carried only by prose drifts the moment somebody adds `DateTime.UtcNow` to a lawn file. `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCoreContractScanTests.cs` (7 tests) now enforces five bans over **every `.cs` under `gk-core/src/FusionRpg.Core/Match/Ai/`, enumerated from the directory, never listed**: `DateTime`/`DateTimeOffset`/`Stopwatch`/`Environment.TickCount` (one time base — a tick is passed in as `nowTick`, `CAI4.7` §6/D15), `System.Random`/`new Random(`/`Random.Shared` (`SeededRng.DeriveStream` only), `File.`/`Directory.`/`FileStream`/`StreamReader`/`StreamWriter`/`Path.Combine` (Core reads no file), `UnityEngine`, and `Task.Run`/`ThreadPool`/`new Thread(`/`await ` (Hot rule 3, main-thread frame slot). **Enumerating the directory is the design, not a convenience:** a file added tomorrow is covered with no edit and there is no allowlist for a future session to widen — the failure mode `CAI-guard-1`'s re-pin and the atom vocabulary's four stale counts both name. All 11 files were verified clean *before* the scan landed, so no file needed exempting. **Comment-stripping is load-bearing:** two of the files contain the word `DateTime` in a doc comment that PROMISES the ban (`LawnDecisionTrigger.cs`, `LawnOrderQueue.cs`), so the stripper's own test asserts **on real content** that the raw text contains the token and the stripped text does not, and that a planted `var now = DateTime.Now;` trips while a comment about it does not. **Acceptance:** the filter → **7 passed / 0 failed**; `verify-change` exit 0 (`core-balance` 299/0); `guard-actor-hub` OK; **two mutations, each killing its named test** — a planted `System.DateTime.UtcNow` in `LawnDecisionBudget.cs` and a planted `new Random(7)` in `LawnCastTokenPool.cs`, both reverted (both files are this lane's own). **Not covered, and named:** the checklist's *second* rule ("per-actor AI state is dropped before ptr reuse") lives in `InjectorEntityRegistry.Remove`/`Clear` — outside this fence, `CAI4.3`/`CAI4.8`'s, routed under `R-INJ`. See `tasks/evidence-fragments/CAI-guard-3.md`.

- [ ] **`CAI-handoff-1` — the program's own entry point says the build has not started** · S · deps: — · *(filed by lane `cai4`, 2026-09-22)* · **BLOCKED on this lane's fence: `tasks/combat-ai-handoff.md`.** Three places tell a picking-up session to read this document first — `tasks/combat-ai-plan.md:7` (*"read this first if you are picking the program up"*), `docs/architecture/combat-ai-map.md:14` and `tasks/combat-ai-todo.md:6` — and its §1 state table still says **"Build | Not started. Nothing exists."** with the claims `gk-core/src/FusionRpg.Core/Actions/Ai/` does not exist, `gk-core/data/tuning/combat-ai.v1.json` does not exist and `publish.py` has no `--remove-key`, followed by **"Your first task is `CAI1.1`. Nothing blocks it."** **All four claims are false and were measured 2026-09-22:** `Actions/Ai/` holds the whole wave-1/2 core surface; `combat-ai.v1.json` was published by `CAI1.8` and both hosts read it; `grep -c "remove-key" gk-core/tools/tuning/publish.py` → **4**; and `CAI1.1` is in the ledger's `done` set with **39 other rows** (every wave-1 task, both of wave 2's landed slices, most of waves 3–4, and this lane's four Core halves). **Cause read:** written 2026-09-20 as the pre-build orientation — its own header says so — and never updated, because it is outside every combat-ai lane's fence and has never been in any session's `paths`. **Why it matters more than the other doc staleness this program has fixed:** every other class cost a reader a wrong belief about one file; this one tells a NEW session the program does not exist, and it is the document that session is told to read first — so following it means re-planning work that is done. **Acceptance:** the state table reads the real state (40 rows done, waves 1–2 landed, 3–4 partly, gaps named per wave), the "first task" names a row that is actually open, and it points at `tasks/reports/cai4-lane-summary.md` and the todo's `Executor routing` section instead of restating a routing that has changed three times since. **Blocker:** one path for the manager to add to a lane; two active sessions claim `tasks/**` broadly (`test-verification-boundary-2`, `tvb58`), neither listing this file. See `tasks/evidence-fragments/CAI-handoff-1.md`.
  **MITIGATED 2026-09-23 (lane `cai3`, session `combat-ai-3`), and the blocker is unchanged.** The file itself is still outside every combat-ai lane's fence, so its §1 state table still reads *"Build | Not started. Nothing exists."* — but the two places a picking-up session ACTUALLY starts are both in this lane's fence and both now say so: **this todo's own status line** read *"written 2026-09-20. Not started."* (the same false claim, in the authority document) and is re-written with the measured state and the task-block count; and **the Handoff pointer above it** now carries a warning that the handoff's §1 is stale and that `CAI-handoff-1` holds it. So a new session reading the todo — the authority, and the document this row's own three pointers send it to — is told the real state before it follows the pointer. **The row stays OPEN on the path grant**, because the acceptance is about the handoff file's own state table; a warning is a mitigation, not the fix.

- [x] **`CAI-route-2` — the routing section now reads what has landed** · S · deps: — · **CLOSED 2026-09-22** (lane `cai4`). The `Executor routing` section is the manager's routing index — it exists *"so a manager can size a fence without re-reading 30 rows"* — and it was written 2026-09-21, before the four wave-4 Core halves landed. Its central claim had become false: *"one holding `gk-core/src/FusionRpg.Core/Match/**` clears **4** (`CAI4.2`, `CAI4.6`, `CAI4.7`, `CAI4.9`)"*. That lane **is this one**, and it landed all four halves (74 tests) plus two composition rows the table never had — so a manager widening that fence expecting four rows would find the Core half of each already done and would not learn that the remaining halves are Injector/Contracts/Server/`web`/Diagnostics work. **Changed, all dated:** the grouping sentence now reads *cleared 4 … and is now **spent***; a new **Status 2026-09-22** paragraph records the per-row test counts, states that **no row in that group is cleared by a Core/Match lane any longer**, routes `CAI-tests-1` and `CAI-handoff-1` as **fence** asks rather than dependency asks, and re-states that `gk-fusion/src/FusionRpg.Injector/**` is still the largest group **and is claimed by no active session**; each of the four table rows now names **Core half landed 2026-09-22** with its test count and **what actually remains**; and the `R-CORE-MATCH` bullet is headed **DONE 2026-09-22** with its file list kept as the record of what that fence was for. No row's *state* changed except by the landings themselves — this is the index catching up, which is why every edit is dated rather than silent. **Acceptance:** a read-back of the section plus `grep -nE '^\| \`CAI4\.(2\|6\|7\|9)\`'` shows four rows each naming their landed half and their remaining paths; the `CAI2.x`/`CAI3.x`/`CAI5.x` rows are untouched. See `tasks/evidence-fragments/CAI-route-2.md`.

- [x] **`CAI-defer-1` — the Deferred list's conditions, measured** · XS · deps: — · **CLOSED 2026-09-22** (lane `cai4`). The **Deferred / named follow-ups** section is where a future session looks for known-owed work, and most of its entries carry a **condition** rather than a date — *"once a second non-table consumer exists"*, *"if it reaches eight members"*, *"next lane: decide whether … or …"*. A condition is exactly the claim that goes stale while the heading still reads as owed, so four were **measured rather than re-read**: **(1)** the `ContentHashStamp.TableDigests` → `PartDigests` rename's condition is **MET and the work is filed elsewhere** — `CombatAiProfileIdentity` (`CAI2.1`) is the second, non-table consumer and keys the map by **profile id** (`"siege/default"`, `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs:67`), and `effect-atom` owns the rename with three options open (`tasks/effect-atom-todo.md:642`) — so nothing for a combat-ai session to do, recorded so the next one neither re-derives the condition nor reaches into another program's file; **(2)** `CAI2.4`'s entry offered two options and the second is **already carried out** — `IntentRouter.Compose` takes `IAiDecisionSink? sink` and wraps the policy in `AiDecisionRecordingSource` (`IntentRouter.cs:77,86-88`), so only the *erratum* about the siege path's per-candidate verdicts remains; **(3)** the doc-citation re-anchoring entry's **combat-ai half is DONE** (`CAI-cite-1`'s 39 citations + `CAI-cite-2`/`CAI-cite-3` closing both of this program's doc trees; both scopes audit `D1 0 D2 0 D3 0 D4 0`), leaving only the other programs' documents it lists; **(4)** the `AiRowCondition` eight-member trigger is **NOT met — it is 6**, pinned by its own test's own line. Every other entry was read and **remains owed as written**. **Acceptance:** `grep -n "MEASURED 2026-09-22"` → 4 annotations, each naming the file, line or task it rests on; the two verify-able conditions were checked in code; the non-membership claim uses the pinned contract rather than a hand count; docs only. See `tasks/evidence-fragments/CAI-defer-1.md`.

- [ ] **`CAI2.2-owed-test` — the spec's Server pin test was never built** · S · deps: CAI2.2 · *(filed by manager
  adjudication, 2026-09-26, from the `resume-34-cai2-2` worktree's uncommitted provenance)* — **MEASURED, not
  re-read.** `docs/architecture/combat-ai/spec-replay-identity.md:277` lists, under **Server**,
  `WebMatchProfilePinTests`. That file **does not exist at `features/mega-merge` and did not exist in the
  worktree either**, so it was never written by anyone — the row was not stale, it was unbuilt. The lane
  that landed CAI2.2 named it in its own record: *"Still owed and NOT built here:
  `tests/FusionRpg.Server.Tests/WebMatchProfilePinTests.cs` (the spec's Server pin test list — no Server
  test file is in this session's fence)"* — and that sentence lived **only** in an uncommitted
  `landed` field in a temp worktree, so a routine cleanup would have deleted the only record that the
  work was owed. The provenance is now committed (`c7079e1de`, in
  `tasks/sessions/resume-34-cai2-2-20260925.json`). **Acceptance:** the file exists and covers the
  five-step pin resolution's refusals — `profile.unavailable:v{n}`, `profile.mismatch`,
  `profile.unreadable` — which is the contract `WebMatchService` and `DelveBattleSessionManager` already
  implement on the write path, so this is the read/resolve-side proof the spec asks for.
  **Related, and deliberately NOT duplicated here:** the second item that record owed — *"the pinned set
  is not yet injected into a web/delve resolve, because the only production consumer of
  `CombatAiProfilePolicy` is the siege path, which persists no match log"* — is **already tracked** as
  **`CAI3.6`**, which depends on `CAI2.2` and is this program's one re-bless. **Also noted:** CAI2.2 has
  no `tasks/evidence-fragments/CAI2.2.md` while CAI2.1, CAI2.3, CAI2.4 and CAI2.5 all do, so the salvage
  at `071098ddc` is evidenced only by its acceptance artefact and the session record.

- [ ] **`CAI-spec-fork` — this program's three core specs have 3–6 mutually incompatible unlanded
  drafts each, across 8 worktrees, and no merge order is knowable from the tree** · M · deps: — ·
  *(filed by manager adjudication, 2026-09-26, from the leftover walk)* — **MEASURED by hashing the
  worktree-only lines, not by reading the diffs.** `spec-intent-router.md`, `spec-decision-perf.md`
  and `spec-resolvable-here.md` each exist at integration, and each is held in an unlanded state by
  8 registered worktrees:

  | spec | distinct unlanded drafts | spread (+lines integration lacks) |
  |---|---|---|
  | `spec-intent-router.md` | **5** | +14 (x3), +17 (x2), +23, +33, +35 |
  | `spec-decision-perf.md` | **6** | +5 (x3), +35, +36, +37, +40, +44 |
  | `spec-resolvable-here.md` | **3** | +9 (x3), +17 (x2), +27 (x3) |

  The holder grouping is *consistent* across all three files — `{baseline-item-seed-base,
  cmdc-lane-c, scope-side-wide-20260920}`, `{cmdc-item-seed-gen, corpus-bcu210}`,
  `{cmdc-combat-ai-2, cmdc-ep-3, corpus-bcu211}` — which looks like three competing revisions. **It
  is not that simple, and that is the finding:** *within* the 3-worktree group the same file still
  differs (`spec-intent-router.md` reads +23, +33 and +35 there), so it does not reduce to "one lane,
  one draft" either. Three lanes each forked, and each kept editing.

  **Why nothing was landed.** These are spec drafts, and the decisive question — which revision is
  canonical — is a program decision that no reading of the tree can answer. The largest draft is not
  automatically the right one: the `+5` group is the only one whose `spec-decision-perf.md` holds
  *less* than integration while the others hold far more, so "most complete" and "most correct" are
  not the same question. Landing any one draft discards the other four or five.

  **Re-derived 2026-09-27, still exact.** Every spread above was re-measured against
  `features/mega-merge` and none of it has moved: `spec-intent-router.md` 5 drafts
  (+14 x3, +17 x2, +23, +33, +35), `spec-decision-perf.md` 6 drafts (+5 x3, +35, +36, +37, +40, +44),
  `spec-resolvable-here.md` 3 drafts (+9 x3, +17 x2, +27 x3) - the same eight holders in the same
  three groups, and the 3-worktree group still differs *within itself* at +23 / +33 / +35. A spread
  nobody re-derives rots into a remembered number, so this line exists to keep the row a measurement
  rather than a recollection.

  **Adjudicated 2026-09-27, the whole first holder group: all three are BLOCKED, and nothing else
  holds any of them.** `cmdc-lane-c` (12 dirty, specs +44/+33/+27), `baseline-item-seed-base` (13, +37/
  +23/+27) and `scope-side-wide-20260920` (13, +40/+35/+27) have the identical shape, and each was
  adjudicated on its own before being batched here. The three contested specs are the blocker. Every
  other dirty path in all three is accounted for:

  - **`tasks/combat-ai-todo.md`** (55 / 45 / 46 lines) is **superseded**. Across the group only *one*
    decision-bearing line survives the rename fold - `CAI1.7 - publish.py --remove-key`, open in
    `cmdc-lane-c` - and `CAI1.7` is `- [x]` CLOSED here, annotated that solid-enforcement had already
    built it. The other two carry **zero**. The remainder is superseded row headers from an early
    revision of the file.
  - **`docs/architecture/software-architecture.md`** (19 lines each) is entirely the ps1-ban port:
    0 decision-bearing lines, and `scripts/deploy-play.ps1` is absent from HEAD while
    `gk-fusion/scripts/deploy-play.py` is present.
  - **`spec-battle-responsibility-guard.md`, `spec-interception.md`, `spec-routing-guard.md`,
    `battle-effect-payload-spike-2026-09-17.md`** are 3-for-3 and 2-for-2 renames
    (`guard-actor-hub.ps1`/`.py`, `guard-battle-responsibility.ps1`/`.py`, `verify-change.ps1`/`.py`,
    `deploy-play.ps1`/`.py`), plus one line of anchor drift (`EffectRuntime.cs:545` against
    integration's `:539`).
  - **`themes.v2.json`, `spec-capture-as-extension.md`, `tasks/solid-remediation-todo.md`,
    `CAI1.10.md`** are STALE with a zero residue after the fold.

  So the ruling below is not one blocker among several for these three - it is the whole of it, and
  landing any one draft discards the other two of this group as well as the five in the other two.
  **Adjudicated 2026-09-27, second holder group: both BLOCKED, and one of them yielded a real
  finding.** `cmdc-item-seed-gen` (18 dirty, specs +36/+17/+17) and `corpus-bcu210` (20, +35/+17/+17)
  hold the group's smaller drafts and are blocked by this row's ruling. Their other paths:

  - **`tasks/combat-ai-todo.md`** (44 / 59 lines) is **superseded**. Every decision-bearing line in both
    names a row that is `- [x]` CLOSED here: `CAI1.12` reads *"DONE, both halves ... ERRATUM GRANTED ...
    handed off to `cai-sink` and landed there"*, and `CAI1.14` reads *"DONE in-fence"*. The worktrees
    still carry the older `BLOCKED on the injector half (denied path)` and `PARTIAL: site 1` states.
  - **`tasks/evidence-fragments/CAI1.12.md`** (+38 lines in both) is the `cai-sink` draft whose fourth
    erratum was rescued in `662b53a96` and cross-referenced onto `CAI3.6`; the rest is superseded by the
    later `cai-sink` session now committed at this row's line 185.
  - **`software-architecture.md`** (19 lines each) is the ps1-ban port; the two lane briefs
    (`cai-sink.md`, `combat-ai-cai111.md`) and four specs are renames; `themes.v2.json`,
    `spec-capture-as-extension.md`, `CAI1.10.md`, `CAI1.13.md`, `CAI1.14.md` and
    `tasks/solid-remediation-todo.md` are STALE with a zero residue.
  - **`corpus-bcu210` also holds 2 untracked files integration lacks**:
    `docs/research/action-corpus/_usage-2026-09-21.json` and `_usage-2026-09-23.json`. These are
    **UNLANDED GENERATED DATA** and the walk's one new finding of this pass - filed as `AC-F2` in
    `tasks/action-corpus-todo.md`, because `usage_direction.weights.latest_usage_report_path` reads the
    newest *committed* report and the committed one is 3.2x undercounted. Neither unlanded report
    reproduces, so neither may be landed; the sanctioned path is regenerate-and-commit.

  **CORRECTION 2026-09-27: the fork is 5 worktrees, not 8.** The `+5` group
  (`cmdc-combat-ai-2`, `cmdc-ep-3`, `corpus/bcu211`) is **STALE, not a competing body**, and all three
  are clearable. Every one of their worktree-only lines is a place where **integration is newer**:

  | the copy says | integration says |
  |---|---|
  | `**Status:** spec, 2026-09-20. Not built.` | `**part built** (CAI1.14, 2026-09-20): sites 1-4 landed` |
  | `IntentRouter.cs` (new; does not exist yet) | (new - **landed**, CAI1.10) |
  | `ResolvableHere.cs` (new; does not exist yet) | (new - **landed**, CAI1.12) |
  | a 3-parameter sink construction | the 6-parameter form with the CAI4.9 order hook and the CAI2.4 recording sink |
  | `BattleRunState.cs:627-630` / `CostLedger.cs:69-70` / `BattleEffects.cs:238-250` | `:743-757` / `:135` / `:241-264` |

  All three members carry **0** occurrences of the `**landed**` marker where integration carries 1 / 4 /
  2, and their `combat-ai-todo.md` residues name only rows that are open-or-closed at integration
  (`CAI2.2` open, `CAI2.6` and `CAI3.1` closed, `siege.v3.json` present, and the `private nested class`
  blocker reworded rather than dropped). So this row's ruling is load-bearing for **5** worktrees in
  **2** groups - `{baseline-item-seed-base, cmdc-lane-c, scope-side-wide-20260920}` and
  `{cmdc-item-seed-gen, corpus-bcu210}` - and those two groups genuinely differ within themselves.

  The row's own earlier reading is corrected with it. It noted that the `+5` group "is the only one
  whose `spec-decision-perf.md` holds *less* than integration while the others hold far more" and read
  that as extra difficulty. **Holding less is what a stale copy looks like**, and reading it as
  ambiguity is the same error as reading a smaller file as the unfinished one - twice in this walk now.

  **HOLDER CENSUS CORRECTED 2026-09-27: 7 participants, enumerated from disk.** The "8 worktrees"
  above was produced by spreading each spec across the worktrees *already suspected*, which is a name
  test wearing a measurement's clothes - it can only find what it was told to look for. Enumerating
  every registered worktree instead gives **32 holding a different revision of at least one of the
  three**, in **8 / 9 / 7** distinct drafts. Sorted by whether the difference is content or the
  ps1-ban rename:

  | group | worktrees | resolvable-here | decision-perf | intent-router |
  |---|---|---|---|---|
  | **A - the fork** | `agent-a62e66aeb29dc472c`, `agent-a7caaafc906532c18`, `baseline-item-seed-base`, `cmdc-lane-c`, `scope-side-wide-20260920` | **+27** (all five) | +37 / +40 x3 / +44 | +23 / +33 / +35 x2 |
  | **B - the fork** | `cmdc-item-seed-gen`, `corpus-bcu210` | +17 (both) | +36 / +35 | +17 (both) |
  | rename-only | **23 worktrees** | +4 | +2 | +4 |
  | already adjudicated STALE | `corpus-bcu211`, `corpus-bcu212` | +9 | +5 / +3 | +14 / +13 |
  | small-difference | `cmdc-bp-1`, `corpus-bcu211b`, `opencode-findings-2c`, `corpus-bcu213`, `materialistic-spear` | +6 / +6 / +6 / +7 / +2 | +2 | +9 x3 / - / - |
  | quota-stopped, untouchable | `actor-hud-bottom-anchor-20260916` | +4 | +2 | +5 |

  **The 23-worktree row is the one that matters, and every one of its lines was read.** All of its
  +2 / +4 / +4 lines are `guard-battle-responsibility.ps1` -> `.py` and `guard-actor-hub.ps1` -> `.py`:
  the ps1-ban port, the symmetric one-for-one rename the rules require discounting. So for 23
  worktrees **the specs are not what holds them** - a materially different situation from the 7 that
  are blocked on this ruling, and the reason a single "N worktrees are blocked" number was the wrong
  thing to carry.

  The two groups agree exactly on `spec-resolvable-here.md` (+27 and +17) and split on the other two,
  so the earlier finding survives at a larger scale: three lanes each forked, and each kept editing.

  **Acceptance:** an owner or `combat-ai` lane states which revision of each spec is canonical, that
  one lands, and the other 7 worktrees' copies become stale rather than divergent. Until then these
  8 worktrees are **BLOCKED, not clearable**, which is why they stay in the plan with a reason rather
  than being swept. This is *not* the stale-citation problem tracked at the `BattleRunState.cs` rows
  above; that is about line anchors resolving, this is about incompatible bodies of the documents.


    **RESOLVED 2026-09-27 — this is a TIME GRADIENT, not a fork, and merging would REVERT landed work.**
    A dedicated read-only investigation re-derived this row from disk and the premise does not survive.
    Three corrections, each measured rather than reasoned:

    - **The "8 worktrees" undercounted the holders; 28 hold the residue.** After folding the ps1-ban
      rename, the spread is not continuous: **7 worktrees at 60-95 residue lines, then a 3x gap down to
      19, then 0.** The 7 this row already names *is* exactly the >=60 set. The row's other spread
      figures do not reproduce, its "32 holders" sums to 38, and it names a worktree that is no longer
      registered. Those are recollection, not measurement, and are superseded by the table above.
    - **The residue is a time gradient.** Of 883 residue lines across the holders, **810 are neutral and
      50 are stale markers; all 23 "fresh" lines already exist at integration in later form.** The 15
      largest holders differ from integration by **two lines** — a `.ps1` filename that has since been
      ported. These worktrees are snapshots taken at different points in one document's life, and
      integration is the newest point. There is no second opinion to reconcile.
    - **The floor is 26 paths, not 11.** Eight sibling evidence fragments (`CAI1.10`, `CAI1.13`,
      `CAI2.3`, `CAI2.4`, `CAI2.6`, `CAI3.1`, `CAI3.3`, `CAI4.4`) plus `software-architecture.md` were
      not in the earlier list; each is held by 17-25 worktrees. A 26-path floor also removes the
      "11 worktrees hold nothing of their own" claim: on a strict reading that set is **1**
      (`materialistic-spear`), and on the widest defensible reading **4**.

    **The consequence is the ruling.** Integration is canonical, and a merge is not a resolution — it is
    a regression. Read directly off the two copies of `spec-decision-perf.md`:

        integration:   **Status:** **part built** (CAI1.14, 2026-09-20): sites 1-4
        worktree copy: **Status:** spec, 2026-09-20. Not built.

    Merging any holder would rewrite that line back to `Not built`, and would do the same to every other
    status line these documents accumulated since. **This row is therefore CLOSED as RESOLVED-INTEGRATION-
    CANONICAL, not as "one draft won".** The 28 holders are clearable as STALE under option 3b; none of
    them is owed a resume, because the work they were doing is delivered.

    What genuinely remains open is narrower and is filed elsewhere: `resume-05`'s generator
    `kind` regression (it re-breaks 14 Core tests with `UnknownKind` and must not be staged), the
    `PassiveTreeRosterGen.Tests` project that 82 invocations depend on and `ci.yml` does not run, and
    the `bin/` gap in `.gitignore` that let ~6,800 compiled artifacts accumulate untracked in every
    worktree.
