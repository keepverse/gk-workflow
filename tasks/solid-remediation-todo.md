# Tasks — `solid-remediation`

Plan: [solid-remediation-plan.md](solid-remediation-plan.md). Session: `solid-remediation-20260917`.

Every verification is:

```powershell
.\scripts\verify-change.ps1 -Paths <changed files> -Session solid-remediation-20260917
```

**A module ends green, not a task.** `src` may be red inside a module; it is green at the module boundary.

## Module-start ritual — run before the first task of every module

The plan asserts three things that no task performed until this was written. Each costs about a minute
and each has already gone wrong once in this repo.

1. **Record the module's start SHA** in the module's first commit message. Recovery is `git reset` to it,
   and "revert the module" is meaningless without knowing where it began.
2. **Re-verify that module's `file:line` citations.** The specs cite a pre-merge measurement, and D6's
   writer had already moved 460 to 388 while staying in range — a mechanical range check cannot see that,
   only reading can. 45 bare citations were line-checked clean on 2026-09-17; that proves no file is
   missing, not that the code is still where the spec says.
3. **Confirm exclusivity still holds** — `session-boundary-check.py` clean and this program's the only
   active record. The build-break permission is conditional on it, and the spec is explicit that a module
   must not assume exclusivity it has not checked.

## Known trap — three unreadable directories

`tools/seedsmith/.tmp-seedsmith-pytest-audit{,-final,-full}` are gitignored leftovers whose ACL denies
enumeration to **`icacls` itself**; removing them needs an elevated `takeown`, which is the owner's call.
Any task that scans the repo will hit `Permission denied` on them.

**Every scan this program writes skips non-source directories and survives an unreadable one** — that is
already `T1.4`'s requirement for the guard, and it is the general rule. A scan that a leftover directory
can veto is reporting on the filesystem, not on the code. `LadderRestatementGuardTests` was vetoed this
way from 2026-09-10 until 2026-09-17, and it was hiding a real defect the whole time.

---

## Phase 0 — Green baseline

*Module: `green-baseline`. 83 failures across 4 projects, measured 2026-09-17. Re-measure first: these are
readings.*

- [x] **T0.1 — Session record and boundary** ✅ `84bc61f6` · XS · deps: none
  - Acceptance: `tasks/sessions/solid-remediation-20260917.json` exists with this program's `paths`; the
    14 stale records are marked merged or abandoned; `session-boundary-check.py` is clean
  - Verify: `python scripts/session-boundary-check.py` exits clean; `verify-change.ps1 --session solid-remediation-20260917` runs at all
  - Files: `tasks/sessions/*.json`
  - Note: this unblocks every later verification. Nothing else can be verified as specified until it lands

- [x] **T0.2 — SquadHarness tuning resolution (was: bootstrap)** · S · deps: T0.1
  - Acceptance: one assembly-level bootstrap in the shape of `ContractTuningTestBootstrap`; the per-test
    `TuningBootstrap.Configure()` calls deleted; **all 73 failures gone**
  - Verify: `SquadHarness.Tests` green, **and green per class** (`--filter` each of `AggregationTests`,
    `CoverageTests`, `ResolutionTests` alone) — that is what proves order-dependence is gone, not reshuffled
  - Files: `gk-core/tests/FusionRpg.SquadHarness.Tests/**`
  - Note: all 73 are one defect. `combat.power.omni` needs **no pin** — `AnchorFamilyOf` maps it to family
    `atk`, which is pinned; the throw is an empty `ChannelsOrEmpty`

- [x] **T0.3 — Core: 3 failures diagnosed individually** ✅ `bf937ee4` · S · deps: T0.1
  - Acceptance: `ExpeditionResolverTests.Tier_goldens_are_locked` and both `GrantedActionTextTests` each
    resolved, and each one says **which** it was — real regression vs stale golden, corpus gap vs stale
    assertion
  - Verify: `Core.Tests` 13943/13943
  - Files: varies per diagnosis
  - Note: re-blessing an expected value without naming which of the two it was is not a fix

- [x] **T0.4 — Data: re-run in isolation, then diagnose** ✅ `771cfbdd` · S · deps: T0.1
  - Acceptance: each of the 4 run alone first; any that passes in isolation is recorded as **load-sensitive,
    not a defect**; the rest diagnosed
  - Verify: `Data.Tests` green; the isolation result recorded in the commit
  - Files: varies
  - Note: two `CacheRetrievalTests` already cleared between runs with no code change, under 31 concurrent
    `dotnet`. A flake fixed as a defect is a change with no reason

- [x] **T0.5 — E2E: 3 failures** ✅ `44a458d2` · S · deps: T0.1
  - Acceptance: 221/221, each diagnosed individually
  - Verify: `E2E.Tests` green
  - Note: the memory claiming "206/207 failing" is **stale** and was propagated into this program's first
    scoping. It is 218/221

- [x] **T0.6 — Four misfiled files resolved (3 moves + 1 namespace fix)** · XS · deps: T0.1
  - Acceptance: `BasicAttack.cs`, `TimelineDispatch.cs`, `TurnOrderRecord.cs` moved under `Battle/`;
    `AchievementEvaluator.cs` under the namespace it declares. **Zero call-site changes** — each already
    declares the right namespace
  - Verify: build green; `git diff --stat` shows renames only
  - Note: deliberately here, not in `file-move-tool`. The tool is built later to be reusable; these four
    need `git mv` and nothing else, and leaving them broken until Phase 5 serves nobody

- [x] **T0.7 — Full-green sweep** ✅ · XS · deps: T0.2–T0.6
  - Acceptance: all twelve CI C# projects green; all six boundary guards plus `guard-magic-numbers.ps1`
    green; `npm test` green; `deploy-play.ps1` runs to completion
  - Verify: one pass, measured together — not remembered from separate runs

### ✅ CP0 — the gate means something
- [x] Twelve CI projects green (Data: 2 load-sensitive, pass in isolation — named in the spec)
- [x] `session-boundary-check.py` clean
- [x] `deploy-play.ps1` completes (exit 0)
- [x] **The sentence "the next module can read `verify-change.ps1` as a fact about its own change, with no
      'except the known ones' caveat" is literally true.** If not, Phase 0 is not done

---

## Phase 1 — Enforcement and registers

*Modules: `battle-responsibility-guard` (G2), `verification-boundaries-extend` (G3), `stub-register` (G1),
`fe-debt-register` (X4). None change behaviour.*

- [x] **T1.1 — Stub register created** · XS · deps: CP0
  - Acceptance: file, schema (what refuses / where / waits on what / owner / does anything ship on it), and
    the rule that every module appends as it runs
  - Verify: schema and closure asserted — every row has a finding and an owner. **Never** the row count

- [x] **T1.2 — Stub register seeded from measurement** · S · deps: T1.1
  - Acceptance: the 14 `NotImplementedException` sites triaged into stub / wiring gap / neither (10 are in
    `DelveEndpoints.cs`). Re-measure; this is a reading
  - Note: a **dark feature** is a wiring gap, not a stub. Fusion picks are built, validated, reachable and
    render nothing — that is S5, in scope, not a register row

- [x] **T1.3 — FE debt register created and seeded** · S · deps: CP0
  - Acceptance: X4 (C#/TS sigmoid divergence), `web/**` having no verification boundary, the measure-cap
    finding, and the god-TSX pointer to `gui-lego`
  - Note: a row says what it **blocks**. "The FE is ugly" is not a row

- [x] **T1.4 — Battle responsibility guard: ownership-shaped scan** · M · deps: CP0
  - Acceptance: for each mechanism in the closed responsibility register, the guard names its one owner and
    refuses a second implementation. Strips comments before matching; skips non-source dirs and survives an
    unreadable one; **scans `tools/`**
  - Verify: green on the current tree; red on a synthetic second-owner fixture; **green** on a commented-out
    second owner
  - Note: a positive-presence check is the defect, not the fix — that is why a hand-copied reflect formula
    passes `guard-class-system.py` today

- [x] **T1.5 — Guard allowlist, each entry owning a module** · S · deps: T1.4
  - Acceptance: every entry that exists only because a later module owns the defect names **that module id**
  - Verify: a test fails on an allowlist entry with no owning module
  - Note: an entry with no module id is how grandfathered debt becomes a template

- [x] **T1.6 — Guard into CI and `deploy-play.ps1`** · XS · deps: T1.4, T1.5

- [x] **T1.7 — Verification boundary for `gk-core/tools/CombatSim/**`** · S · deps: CP0
  - Acceptance: a changed file selects a non-empty, relevant test set; an **unmapped** path under the tree
    fails rather than silently selecting nothing
  - Verify: assert the mapping **contract**, never how many tests a boundary selects

- [x] **T1.8 — Verification boundary for `gk-core/tools/ProvePredictor/**`** · S · deps: T1.7
  - Note: `web/**` is deliberately **not** mapped — it is a row in the FE register (T1.3)

### ✅ CP1 — enforcement exists before the fixes — **MET 2026-09-17**
- [x] Guard in CI, red on a synthetic second owner, green on a comment
- [x] Both tool trees select real tests; an unmapped path fails
- [x] Both registers exist with schemas and the append rule
- [x] Every allowlist entry names its owning module
- [x] Twelve projects still green — Core 13944/13944, Data 1511/1512 (1 skipped by the default
      profile's `Category!=DiskSemantics&Category!=Heavy` filter), Server 549/549, E2E 221/221,
      Guard 364/364, CheatCore 41/41, Launcher 165/165, ItemSeedValidator 83/83, AtomImporter 33/33,
      ElementEnumGen 17/17, SquadHarness 193/193, TreeBinder 45/45

**What closing this gate cost, recorded because it was a real defect and not a flake.** Guard first
came back 363/364 on `Test_fast_requires_an_explicit_scope`. Cause:
`gk-core/scripts/guard-test-substrate.py` accepted `--root` but pinned its baseline beside the script, so its
own tests had to plant their violating probe in the **real** `gk-core/tests/FusionRpg.Data.Tests/`. While that
file existed every parallel test that runs the gate saw a genuine violation, and `test-fast.ps1` runs
it as its first step. Different classes, so xUnit ran them in parallel; Phase 1's four new boundary
tests shifted the timing enough to make it reliable rather than occasional. Fixed by giving the guard
`-BaselinePath` and moving both planting tests onto a throwaway tree.

**One unexplained reading — since explained, and it was not a flake.** SquadHarness reported 192/193
once in the first sweep; the name was not captured and four re-runs came back 193/193. It returned in
the CP2 sweep with its name: `DeterminismTests.A_second_process_reproduces_the_hash`.

Cause: `DeterminismTests.Run` used `dotnet run --project`, which rebuilds SquadHarness — a
`FusionRpg.Core` dependant — in a child process while the parent `dotnet test` still holds Core's
output. That is the CS2012 locked-file race, whose signature is exactly what was measured: **red inside
a full-suite run, green when run alone**, across five runs. It hid inside a test named for determinism,
immediately after `battle-effect-math` changed battle's RNG streams — the worst place for a build race
to sit, because the obvious suspect was the change.

Fixed with the repo's own precedent: SquadHarness is already a `ProjectReference`, so its apphost lands
beside the test dll and the test launches that directly. **Then the same shape was searched for**, and
`FusionRpg.AtomImporter.Tests/ValidateGateCiTests.cs` had two more sites — in a project whose own
sibling `RealColdProcessTests` was fixed for this on 2026-09-12 with the doc comment still in place.
Those two were missed then. Fixed the same way; that suite went 8s to 2s.

⚠️ **The lesson, recorded because it nearly cost a wrong diagnosis:** a test that is red in a suite
and green alone is a *harness* fact until proven otherwise. Capture the name before theorising, and
never let a plausible recent change stand in for the measurement.

---

## Phase 2 — The battle chain

*Modules: `elemental-resolver` (D14), `battle-effect-math` (D1), `retaliation-shared` (D2, D8). First
player-visible change.*

- [x] **T2.1 — SPIKE: does effect damage reach the dispatcher, and with what payload?** · S · deps: CP1
  - Acceptance: a written answer to (a) does effect-driven battle damage reach `CombatDamageDispatcher` at
    all, or only `DamageApplyPipeline`; (b) what `ElementPayload` does it carry; (c) therefore what must
    change for D1 to be observable
  - Verify: the answer is evidence with `file:line`, not an inference. **No production code in this task**
  - **Answer: [docs/research/battle-effect-payload-spike-2026-09-17.md](../docs/research/battle-effect-payload-spike-2026-09-17.md).**
    Effect damage DOES reach `CombatDamageDispatcher` (`EffectBag.cs:567`, `:637`,
    `StatusEffectBridge.cs:98`, `:144`) — battle just never sets `CombatMath`. But wiring it alone is
    provably inert: `OverlayCombatMath.cs:42-43` returns the amount unchanged on an empty payload, and
    of four `AtomCompiler.Compile` call sites only `AtomPushService.cs:294` passes an owner element.
    **So T2.4 must land before T2.5**, which is the reverse of how the numbering reads
  - Note: **measured 2026-09-17 — wiring `CombatMath` moved 0 of 13,943 tests.** `Finalize` returns the
    amount unchanged when the packet has no `ElementPayload` (`OverlayCombatMath.cs`), and battle defaults
    it empty (`BattleRunState.cs:873`). Everything below depends on this answer

- [x] **T2.2 — One elemental resolver, owned by the engine** · M · deps: T2.1
  - Acceptance: a single resolver every contest calls; consumes the existing `ElementRingMatrix` /
    `ElementMatchupRelation` rather than re-deriving; reuses `ClampedContest` per `spec-evasion-chain` §7
  - Verify: `battle-responsibility-guard` refuses a second contest implementation
  - **Registering the contest pattern found two more production second-owners**, neither in the audit:
    `Battle/Siege/SiegeHitChance.cs:38` decides its own hit chance, and
    `Delve/Difficulty/ActorThetaSeam.cs:30,37` its own dodge contest. Both read **omni only**, so a siege
    swing and a delve difficulty check resolve on a different rule from every other mode — rule 4.
    Allowlisted to `battle-mode-parity`, which is where a mode-parity fix belongs

- [x] **T2.3 — `omni + element` extended to parry, block, reflect** · M · deps: T2.2
  - Acceptance: the three families read `omni + element` like the other nine. Omni is **additive only**,
    never multiplied
  - Verify: an omni-only and an element-only actor with equal totals resolve identically; doubling omni
    never multiplies the element term; the matrix stays **intransitive**; probability stays in [0,1]
  - Note: comment the sigmoid bound as **mathematical, not a gameplay cap** — this repo bans hard ceilings
    and a later audit will otherwise try to "free" it. `block.*` still must not read `ShieldElementMatrix`
  - **The spec's own citation did not hold, and the comment in code was the thing to fix.**
    `CombatDerivedReader` said parry/block are omni-only because "the spec never describes a per-component
    breakdown ... and §7 explicitly bans reading ShieldElementMatrix". `spec-evasion-chain.md` contains
    no reference to "omni" at all, and §7's ban is on block reading the **shield** matrix — a different
    thing from per-element **combat** channels. The rest was an argument from absence. The §7 ban still
    stands untouched; nothing reads `ShieldElementMatrix`
  - **Extending the three families moved 0 of 13,944 tests**, which is correct — no content authors a
    per-element parry/block/reflect channel today, so every element half reads 0. That also means the
    suite would have stayed green if the extension had done nothing, so `PerElementAvoidanceTests` writes
    those channels by hand: 61 cases proving the element half is read, is **added** rather than
    substituted, does not scale with omni, is ignored for a different element, and reaches a resolved
    parry band through the weighted accumulation

- [x] **T2.4 — Element payload reaches battle's damage packets** · M · deps: T2.1, T2.2
  - Acceptance: whatever T2.1 named as the missing link, using the existing `HybridPayload.Build`
  - Verify: a battle effect hit carries a non-empty payload — asserted, because D1 depends on it
  - **Seam located 2026-09-17, and it is not the compile path T2.1 pointed at.** Traced end to end:
    - `AtomCompiler.cs:236-247` bakes `elementPayload` only when `ownerElementPrimary` is non-null, and
      the three battle-side `Compile` calls pass no owner
    - but `ActionContainerEffectResolverFactory.cs:63` compiles **per container**, not per owner — one
      shared catalog for every actor that holds the action. Baking an element there would give every
      holder the **first** owner's element. That path is structurally wrong for this, not merely unwired
    - `BattleRunState.BindContainers` (`:623-654`) is per **actor** and already grants with an
      `EffectGrantDto`. That is the per-actor seam, and it is the same shape the lawn already uses —
      `BasicAttackGrantBuilder.cs:56` bakes the owner's element into a per-actor grant
  - ⚠️ **Grant overlay overrides authored params, so the naive version breaks the authored-wins rule.**
    `EffectOverlayMerge.TryMerge` (`EffectProcAndOwner.cs:342-364`) seeds `merged` from the action's own
    params and then lets `grant.Overlay` **overwrite** them. A grant-level `elementPayload` would beat an
    authored one, which is the opposite of `AtomCompiler`'s own `!overlay.ContainsKey("elementPayload")`
    rule that authored content always wins
  - **So T2.4 and T2.5 are one change, not two.** The fallback belongs where `merged` is built, under the
    same "only if nothing authored one" condition the compiler already uses — and the actor's element
    types arrive through `Bag.ActorResolve`, which is exactly the property T2.5 sets. Setting
    `ActorResolve` is what makes the payload reachable, and the payload is what makes `CombatMath`
    stop being inert. Do them together or the intermediate state is still a measured no-op

- [x] **T2.5 — Battle's bag sets `CombatMath` and `ActorResolve`** · S · deps: T2.4
  - Acceptance: set in `BattleRunState` beside the existing `Host.Bag.ShieldGate = ShieldGate` line, reusing
    the `CombatActorResolve` lambda already built there for `ShieldGate`
  - Verify: `PassThroughCombatMath` is no longer reached in battle — asserted, not assumed
  - Note: the adjacent `ShieldGate` wiring records the **identical defect** already fixed once for shields

- [x] **T2.6 — Before/after measurement for D1** · S · deps: T2.5
  - Acceptance: the measurement recorded in the commit; every golden that moves named and explained as this
    fix
  - Note: the module owes the **measurement**, not a re-tune

  - **The measurement: 0 goldens moved, and that is the finding.** Core went 14,026 → 14,032 and every
    added test is new. Nothing existing moved because every shipped actor and status on these paths is
    element-neutral, so `OverlayCombatMath.Finalize` still returns the authored amount unchanged.
  - ⚠️ **A zero is not evidence a fix works — it is evidence nothing drove the path.** Three falsifiers
    were written to drive it, and the first version of them FAILED against the finished wiring. That is
    what found the two gaps below. Proof now lives in `OwnerElementFallbackTests`: a fire attacker and a
    neutral one firing the same untyped effect at the same ice defender no longer land the same number,
    the typed hit produces a resolver breakdown and the untyped one does not, and the matchup moves it
    in the direction `ElementRingMatrix` declares
  - **Gap 1, found by probe: a battle DoT never enters `CombatDamageDispatcher` at all.** `BattlePulseSink`
    calls `DamageApplyPipeline.Apply` directly — `StatusEffectBridge`'s own comment says so — so wiring
    `Bag.CombatMath` fixed the container/action effect path and could not reach the pulse path that D1
    names FIRST. Closed by `BattleRunState.ResolvePulseAmount`, which routes a pulse through the same
    `CombatMath` the lawn's sink has always used. `BattlePulseSink` also stopped discarding
    `instance.AttackerPtr`, which it had always carried
  - **Gap 2, found the same way and NOT closed here: `BattleStatusSpec` cannot express an element.** Its
    five fields carry no element, and `StatusPulsePayload.For` reads the instance's own `Element`, so
    every battle pulse payload is empty by construction and the new pulse resolver is correctly inert.
    An initial status also has no `AttackerPtr`, so there is no second side to contest. Recorded as a
    tripwire test that fails the day `BattleStatusSpec` grows an element — which is exactly when a real
    behavioural probe becomes possible. Owner: `battle-mode-parity`
  - **A defect this change nearly introduced, caught in review.** `EffectBag.CombatRng` defaults to an
    unseeded `SeededCombatRng(42)`, harmless only while `CombatMath` was null and nothing rolled through
    it. Wiring the resolver made that default load-bearing, and battle would have rolled hit/crit/parry
    from a constant unrelated to its seed — responsibility 19, unreplayable. Fixed by deriving an
    `effect-combat` stream from the battle seed, like every other system in `BattleRunState`

- [x] **T2.7 — Reflect formula extracted to one owner** — landed early, inside T2.3 · S · deps: T2.5
  - Acceptance: one function; `CombatDamageDispatcher.cs:113-118` and `PhaseModel.cs:152-157` both call it
  - Verify: guard refuses a reintroduced copy, proven with a synthetic fixture
  - Note: extract **before** wiring, or the wiring propagates the duplicate into a third mode
  - ⚠️ **There are three copies, not two.** `battle-responsibility-guard` found a third at
    `gk-core/tools/CombatSim/Analytic.cs:250` on 2026-09-17, written through local `V()` accessors instead of
    `CombatDerivedReader`, which is why a symbol scan never saw it. D8 records two because nothing had
    ever scanned `tools/`. Both `gk-core/scripts/battle-responsibility.v1.json` allowlist entries name this
    module, so this task removes both — the guard goes red if it removes only one
  - Decision this task owns, with a default: the CombatSim copy is the POC **reference** the port is
    measured against, so making it call the shared function changes what "reference" means. Default:
    extract in `Core`, have `PhaseModel` call it, and leave the tool's copy pinned by `estimator-parity`
    with its allowlist entry re-pointed at that module rather than deleted
  - **Done, and by the stated default.** Changing the twelve reader signatures forced every reflect call
    site to be revisited, so the extraction happened there rather than waiting: `CombatDamageDispatcher`
    and `PhaseModel` both call `ElementalResolver.RateFromZero` now, and the shape is written out in
    exactly one place. Measured after: **1 copy left**, `gk-core/tools/CombatSim/Analytic.cs`, pinned by
    `estimator-parity` exactly as the default said
  - The guard needed a new decision kind to say this. Once the shape left the dispatcher, the rule "the
    owner must match its own pattern" demanded the owner keep writing the formula it had just stopped
    writing. `shape: "banned"` is a pattern that must appear **nowhere**, not even in the owner — two
    synthetic-fixture tests cover it

- [x] **T2.8 — Reflect reachable from every mode** · M · deps: T2.7
  - Acceptance: reflect resolves in battle, delve, siege and the web match
  - Verify: `grep -r "Reflect" gk-core/src/FusionRpg.Core/Battle/` finds the shared call, not a formula
  - Note: **do not "add reflect to battle"** — that phrasing produces a second implementation
  - **Nothing was added to battle, and that is the point.** D2's two stated causes were that
    `TryReflect` lives inside `DispatchInstant` "which battle never enters", and that battle's bag
    "never sets `ActorResolve`, so the `:84` guard would fail anyway". T2.5 closed both as a side
    effect: battle's effect path now enters `DispatchInstant`, and the bag carries a real
    `ActorResolve`
  - **One wiring reaches four modes.** Delve (`Delve/Battle/DelveBattle.cs:24`), siege
    (`World/Turn/DistrictAssaultResolver.cs:157`) and the web match (`WebMatchService.cs:144,211,387`)
    all reach combat through `BattleEngine.Resolve`, so they inherit `BattleRunState`'s collaborators
    rather than each wiring their own
  - Asserted, not inferred: `Battles_bag_carries_the_real_resolver_and_an_actor_resolve` reads
    `Bag.CombatMath` and `Bag.ActorResolve` off the real host through `onEffectHostReady` and pins the
    math to `OverlayCombatMath`, and `No_reflect_formula_was_added_under_the_battle_folder` runs the
    grep this task names as a test so it stays true
  - ⚠️ **Still out of reach: a battle BASIC attack cannot reflect.** It applies through
    `ApplyHp` → `DamageApplyPipeline.Apply`, never `DispatchInstant`, so the reflect gate is not on
    that path. Effect-driven hits reflect; swings do not. Recorded rather than fixed here — routing the
    basic attack through the dispatcher is a change to the engine's own apply path and belongs to
    `battle-mode-parity`, not to a reflect task

### ✅ CP2 — effect damage resolves, and it is proven live
- [x] Every module in this phase recorded its stub/FE register rows, or stated it added none — both
      registers carry a module-statement table; Phase 2 added none to either and touched no `web/**` file
- [x] Parry/block/reflect read `omni + element`; no registered per-element channel unread — all twenty
      per-element factories have exactly one reader, asserted by `PerElementChannelClosureTests`, which
      also checks each read is an **addition** (it caught the shield families' nullable spelling)
- [x] Battle effect packets carry an element payload —
      `An_effect_hit_from_an_elemental_battle_actor_no_longer_lands_its_authored_number`, run inside
      `BattleEngine.Resolve` rather than on the offline harness, with the attacker's element the only
      difference between the two runs
- [x] `PassThroughCombatMath` unreached in battle; before/after measurement recorded —
      `Battles_bag_carries_the_real_resolver_and_an_actor_resolve` reads the collaborators off the real
      host and pins the math to `OverlayCombatMath`. Measurement: **0 goldens moved**, and why that is
      not evidence of success is recorded under T2.6
- [x] Reflect has one owner and resolves in every mode — copies 3 → 1 (the allowlisted POC
      reference); the four modes inherit one wiring through `BattleEngine.Resolve`;
      `No_reflect_formula_was_added_under_the_battle_folder` keeps the task's own grep true.
      ⚠️ A battle BASIC attack still cannot reflect — recorded under T2.8, owned by `battle-mode-parity`
- [x] **Live proof, half 1 (RPG Server Debug scope) — PASS 2026-09-17.** On a live lawn, an
      effect-driven hit **that authored no element payload** resolved through the element matrix:
      `ice` mastery **0 → 8**, read back through the ordinary non-debug `GET /api/gate-counters/1`.
      Evidence: [docs/research/perf/cp2-live-proof-2026-09-17.md](../docs/research/perf/cp2-live-proof-2026-09-17.md)
      - Falsifiable by construction: `GateCounterHost.HandleDamageApplied` takes the packet's element
        **components**, so no components means no credit however well `CombatMath` is wired. `ice` was
        chosen because its baseline was 0
      - Read back from the server's persisted player row, **not** `LawnCombatObserver` — that rides the
        `/api/perf` window and is exactly the telemetry this clause disqualifies
      - A first attempt read 0 → 0. Real failure, real cause: `OverlayCombatFeature.Enabled` needs env
        `FUSIONRPG_OVERLAY_COMBAT=1` or the `OVERLAY-COMBAT` toggle, and the game had neither, so
        `ConditionalOverlayCombatMath` was off. Diagnosed at the gate, toggled, re-run, passed
      - ⚠️ **Reworded 2026-09-17 because the original could not fail.** It asked the lawn to prove
        `CombatMath` is reached, but the lawn has wired `CombatMath` AND `ActorResolve` unconditionally
        since before this program (`EffectRuntime.cs:117`, `:545`, `:556`). D1 is a **battle** defect and
        the proof was written against the lawn, so it would have passed on day zero. The full correction
        and what replaced it are in `solid-remediation-map.md`

- [x] **Live proof, half 2 — `vfx.tick` inside budget: MET 2026-09-17**, by owner ruling plus a live
      re-measurement. The original finding stands as recorded: `vfx.tick` was **2.513 ms/frame at 80
      entities**, **91.8%** of `loop.tick` (2.737 ms/frame), on its own more than the **2 ms/frame**
      whole-injector stress budget `perf-probe-plan.md` §0 locks for 200+ entities.
      - **Owner ruling:** *"Vfx.tick check it can improve or else. Else we will disable a default and
        add user setting on the web FE."*
      - **Checked for improvement first.** The budget dial was already at its measured sweet spot
        (`ActorHudPool`: 1,899 ms per 5s window unlimited → 483 ms at the shipped budget of 60, ~290
        entities). One real inefficiency was found and fixed: `VfxDirector`'s phase wake forced the whole
        drain/tick chain every frame of every match **regardless of `WorldHudEnabled`**, so turning the
        HUD off skipped the DRAW and kept paying for the WAKE
      - **Then the "else".** The world HUD ships **OFF** (`FUSIONRPG_ACTOR_HUD` now opts IN), with a
        server-backed user setting behind the new centralized settings module
      - **RE-MEASURED LIVE, same board size as the original finding** — real game, current binary,
        `GET /api/perf/recent`, steady-state windows at 60 fps:

        | | before | after |
        |---|---|---|
        | `vfx.tick` @ 80 zombies | 2.513 ms/frame | **0.0006–0.021 ms/frame** |
        | `loop.tick` @ 80 zombies | 2.737 ms/frame | **0.055–0.099 ms/frame** |

        Both now sit far inside the 2 ms/frame budget — `loop.tick` by a factor of ~20
      - **The toggle was proven to work end to end, not assumed.** `PUT /api/settings`
        `lawn.worldHud=true` raised `vfx.tick` from 0.0006 to **0.2838 ms/frame at just 2 zombies**
        (~470×), and setting it back to false dropped it to 0.0038 at 80 zombies. That is one probe
        proving three things at once: the setting reaches the running injector through the real server
        path, the world HUD really was the cost, and the shipped default is the cheap one
      - **What is still `vfx-v2`'s:** authoring a per-section budget in `perf-probe-plan.md`. This clause
        is met against the only budget that exists (the whole-injector one), which is what it asked for
- [x] Twelve projects green — Core 14035/14035, Data 1511/1512 (1 skipped by the profile filter),
      Server 549/549, E2E 221/221, Guard 369/369, CheatCore 41/41, Launcher 165/165,
      ItemSeedValidator 83/83, AtomImporter 33/33, ElementEnumGen 17/17, SquadHarness 193/193,
      TreeBinder 45/45

---

## Phase 3 — Mode parity

*Module: `battle-mode-parity` (D3, D4, D5, D6). Alone in its phase: five modules depend on it.*

- [x] **T3.1 — Settle the `BattleHubCompose` ratification question** · XS · deps: CP2
  - Acceptance: a written answer, against `decisions.md`, to whether the compose bypass was **ratified**.
    `BattleHubCompose.cs:15-17` asserts it was deliberate, but that was a **byte-identity argument during
    the phase-1 fusion**, which is not the same claim as "battle should have no progression subsystem"
  - Verify: the answer cites `decisions.md`. If ratified, D5 is struck with a reason; if not, D5 is fixed
  - Note: **before** any registration change. Either outcome is complete; leaving it unexamined is not
  - **Answered 2026-09-17: NOT ratified. D5 stands.** Written up in `spec-battle-mode-parity.md`.
    `decisions.md:51` ratifies the compose **path** — "composes exclusively through `BattleHubCompose`
    (ActorHub)", and the defect it declares retired is **dual compose**, not subsystem divergence. The
    code comment's load-bearing clause is "parity with the old composer is **channel-exact**" — a
    byte-identity argument made to hold `BattleGoldenTests` still while `BattleStatComposer` was deleted
    (the same row records goldens "re-blessed **once**"), not a ruling that battle should have no
    progression channels
  - Measured: three `CreateDefault`-class call sites, three different subsystem sets. Battle omits
    `RpgProgressionSubsystem` (registered **unconditionally** by `CreateDefault`) and
    `StatusDerivedSubsystem`; the lawn (`CheatState.cs:49`) passes no `starLoyalty`; the server sheet
    (`UniqueActorHubCompose.cs:70`) passes no `statusDerivedMods`
  - ⚠️ T3.2 should **expect goldens to move** — registering `RpgProgressionSubsystem` in battle is
    exactly the change the 2026-09-13 comment avoided in order to keep them still. Each mover named

- [x] **T3.2 — One registration path** · M · deps: T3.1
  - Acceptance: the three hand-rolled sets route at one registration; `guard-actor-hub.ps1` green
  - Note: this is where a parallel composer is most tempting and most wrong
  - **Done: `BattleHubCompose` routes through `ActorHubBootstrap.CreateDefault`** and contributes its own
    four subsystems on top. `Register` dedupes by `SubsystemId` and sorts by `Order`, so the composed
    result depends only on WHICH subsystems are present — contribution, not a second fold.
    `guard-actor-hub.ps1` green
  - **Goldens did not move.** `BattleGoldenTests` 5/5. The only set difference is
    `RpgProgressionSubsystem`, which writes `progression.power` and `progression.realm` and no combat
    channel — so the 2026-09-13 byte-identity argument was protecting channel **presence**, not any
    combat number
  - ⚠️ **A defect this change introduced, caught by 4 tests.** `RpgProgressionSubsystem` reads
    `StatusPolicy.ProgressionPowerStubDefault`, i.e. `status.v1.json`, so **battle compose gained a
    status-tuning dependency it never had** and `gk-core/tools/ProveAptitude` threw `Configure(...) has not run`
    on every call. Fixed by the precedent that tool's own comment sets for T6's new dependencies —
    mirror `Program.cs`'s boot sequence, same loader, same file, never a narrower substitute. Every
    other battle-composing host was then checked: SquadHarness, CombatSim, DominanceBaseline and
    HybridViability already configure it; ProvePredictor inherits CombatSim's bootstrap
  - ⚠️ **`statusDerivedMods` is deliberately still not passed to battle**, and this is a finding rather
    than an omission: battle already owns that responsibility through `BattleStatModifierLedger`, fed
    from `StatusStatPayload.ToModifiers` at `BattleRunState.cs:313`. Registering `StatusDerivedSubsystem`
    as well would apply every status stat mod **twice**. Battle's ledger vs the lawn's subsystem is a
    real rule-2 divergence — two mechanisms for responsibility 3 — and closing it means unifying the
    mechanism, not adding a second consumer here
  - Remaining opt-in gaps, recorded: the lawn (`CheatState.cs:49`) passes no `starLoyalty`, the server
    sheet (`UniqueActorHubCompose.cs:70`) passes no `statusDerivedMods`. Both are already on the one
    registration path; what they lack is a source, which is a different defect from a different path

- [x] **T3.3 — Delve and siege populate `HubInputs`** · M · deps: T3.2
  - Acceptance: `Encounter.cs` and `DistrictAssaultResolver.cs` populate them as `WebMatchService` does
  - Verify: the same specimen composes identically in every mode — asserted
  - **Siege: done, by inversion rather than by reaching across the layer.** `DistrictAssaultResolver`'s
    own comment had already named the gap AND the reason — "that mechanism lives in `FusionRpg.Server`
    and needs a live `RpgStore`, which this Core-only, statics-constructible resolver cannot reach".
    Diagnosis and refusal both correct; what was missing was the inversion. Core now declares
    `HubInputsFor`, and `RpgStore.WorldTurns.cs:545` — the Data layer, which has the store — injects it.
    `guard-dal.ps1` and `guard-actor-hub.ps1` both green
  - The `InstanceId` guard lives in **Core**, not the provider: a member without one is a non-player
    force or a guard, so no future provider has to remember that
  - **`Encounter.cs`: nothing to populate.** It emits only the **enemy** half — generated anchors with no
    allocation, atoms or loyalty. D4's phrase is "the same **specimen**", i.e. the player's squad
  - **Delve: no production entry exists.** `DelveBattleSessionManager` already records "zero production
    callers of `DelveBattle.Run` exist anywhere today, confirmed by a direct search". There is no delve
    squad builder to fix until that trigger is built
  - ⚠️ **Siege gets aptitude but not equipped atoms**, and the blocker is a misfiled file rather than a
    missing mechanism: `WebMatchService` builds them from `EquippedBoundAtoms.DerivedFromStore`, which
    sits in `FusionRpg.Server` yet depends only on `FusionRpg.Core.*` and `FusionRpg.Data`. Relocating it
    is `file-move-tool`'s work — the same misfiled-by-dependency category T0.6 handled
  - Asserted by `ModeComposeParityTests` (4): a wired provider reaches the member's setup, a member with
    no `InstanceId` is untouched, the `Instance` singleton still composes from level alone (so the seam
    is inert by default and cannot have moved an existing siege), and the same inputs compose to
    identical combat channels whichever mode built the setup

- [x] **T3.4 — All 13 triggers fire in battle** · M · deps: T3.2
  - Acceptance: the 9 missing triggers fire, **or** each exception is named with its reason
  - Verify: the trigger vocabulary is a **closed vocabulary** — pin 13 and say why
  - **Battle raised 4 of 13**, and two of those four (`OnGranted`/`OnRemoved`) come from `EffectBag`
    itself and were never mode-specific. Seven are now wired: `OnDamageTaken` (`ApplyHp`, damage only,
    post-pipeline), `OnSpawn` (initial roster + mid-battle arrivals), `OnDeath` (unsourced sweep +
    attributed kill), `OnTimer` (the round clock), `OnMatchStart`/`OnMatchEnd`/`OnWave` (`BattleEngine`)
  - **Two named exceptions, with reasons**: `OnSunCollect` and `OnGridPlace` are PvZ **lawn economy** —
    the sun bank and the planting grid. Both belong to the foundation game the RPG layer observes rather
    than reimplements, and a battle has neither. Raising them would be inventing an economy, not
    reaching parity
  - **Every raise is gated on `Bag.HasGrantWithTrigger` first**, mirroring the lawn's own
    `HasOnDamageTakenGrant`/`HasOnSpawnGrant`/`HasOnDeathGrant` discipline. Two consequences: nothing is
    allocated on a hot path when no content binds the trigger (every battle today), and since no
    `EffectEventDto` is constructed, **no golden can move**. Confirmed: Core 14039 → 14044, all new
  - `BattleTriggerCoverageTests` pins 13 as a closed vocabulary — the mirror of the population rule,
    since `AtomKind.cs` already records the list was deduplicated to one literal per trigger so the two
    copies "cannot disagree even in principle" — and asserts **closure**: every trigger is raised,
    bag-raised, or excepted with a reason, exactly once

- [x] **T3.5 — D6: the dead recompose is wired or deleted** · S · deps: T3.3
  - Acceptance: an explicit decision, not a third state. It runs every round against an input with zero
    production writers (`BattleEngine.cs:481`; the only assignment is construction-time at
    `BattleRunState.cs:388`, every invocation is a test)
  - Note: if T3.3 gives it real inputs it is wired; if not it is deleted. **Not left running against nothing**
  - **The explicit decision: the consumer is correct and the PRODUCER is the dark half.** Re-measured —
    the only production writer is `BattleRunState`'s `setup.ActiveAuras` loop, and `ActiveAuras` is
    assigned in exactly two files, **both tests**. So the recompose rebuilt every actor's snapshot from
    an empty contribution set, once per round, for nothing
  - T3.3 did **not** give it real inputs: that wired `BattleHubInputs` (compose-time), a different
    mechanism from `BattleDerivedModifierLedger` (mid-battle). So by the note's letter this reads
    "delete"
  - **Deleting was the wrong call and the program's own doctrine says so.** A built, tested mechanism
    whose only gap is a missing caller is a **dark feature** — "a wiring gap, in scope for remediation,
    registered so the owning program sees it" — not dead code. `elemental-resolver` is the precedent:
    D14 was filed as a delete and the owner ruling turned it into a fix, and the map states this program
    contains **exactly one delete** (X5's copy)
  - **Not left running against nothing either**: `RecomposeDerivedForAllActors` now returns early on an
    empty ledger, so the per-round waste is gone while the mechanism stays intact for the moment a
    producer exists. `AuraDeliveryTests`, `ZombossAuraTests` and `PassiveTreeMechanismRoundRecomposeTests`
    all still pass (27), which is what proves the mechanism was not damaged
  - Registered as **`SR-14`** (dark, owner `aura-skill` T13). The producer needs an aura-id → magnitude
    resolution that `AuraContentRow` does not carry — it has `GrantChannels`/`ContestChannels` and no
    value — which is T13's own named job

- [x] **T3.6 — Mode-conformance test** · M · deps: T3.3, T3.4
  - Acceptance: every registered mode drives the same mechanism set
  - Verify: fails on a synthetic divergent mode — that is what stops D3/D4 recurring silently
  - **Mechanisms, not outcomes.** The five profiles legitimately differ in timeline behaviour
    (`classic-round` at `W=1` vs `galaxy-sync` overlapping two per side), so their reports differ by
    design. What must not differ is which mechanisms are wired, so the captured set is the effect host's
    collaborators plus the composed derived channels — never the battle result
  - `ModeConformanceTests` (6) pins the five registered modes as a closed vocabulary, asserts all five
    produce an identical mechanism set, and asserts the set is **not vacuous** — it actually contains
    `actorResolve:wired`, `shieldGate:wired`, `combatMath:OverlayCombatMath` and the triggers D3 named
  - **Three falsifiers, one of them real.** A mutated set with a mechanism removed and one with an extra
    are both caught — divergence is not only omission, since a mode quietly registering a subsystem its
    siblings lack is D5's shape. The third builds a **real** divergent battle: `onEffectHostReady` is the
    seam a mode wires collaborators at, so clearing `ActorResolve` there reproduces half of D2's stated
    cause from inside an actual `BattleEngine.Resolve`, and the captured set diverges

### ✅ CP3 — one specimen, one set of numbers — **MET 2026-09-17**
- [x] Every module in this phase recorded its stub/FE register rows, or stated it added none —
      `battle-mode-parity` added `SR-14` (D6's dark producer) and no FE row, and touched no `web/**` file
- [x] `decisions.md` question settled in writing, either way — T3.1: the compose **path** was ratified
      (the fusion note's "composes exclusively through `BattleHubCompose`"), the **subsystem set** was
      not; the code's own justification was a byte-identity argument. So D5 stood and T3.2 fixed it
- [x] One registration path; delve and siege populate `HubInputs` — battle routes through
      `ActorHubBootstrap.CreateDefault`; siege populates by inversion (Core declares `HubInputsFor`, Data
      injects). **`Encounter.cs` has nothing to populate** (enemy half only) and **delve has no
      production entry** ("zero production callers of `DelveBattle.Run`", the code's own words)
- [x] 13 triggers, or named exceptions — seven wired, two raised by `EffectBag` for every mode, two
      named exceptions (`OnSunCollect`/`OnGridPlace` are PvZ lawn economy a battle has no analogue for)
- [x] D6 wired or deleted — neither, explicitly: the consumer is correct and the **producer** is dark.
      Gated on an empty ledger so it no longer runs against nothing, kept because deleting a built,
      tested mechanism whose only gap is a missing caller contradicts this program's own doctrine and
      its "exactly one delete" count
- [x] Mode-conformance test present and failing on a divergent mode — `ModeConformanceTests` (6), with
      three falsifiers including a **real** one that clears `ActorResolve` at `onEffectHostReady` inside
      an actual `BattleEngine.Resolve`
- [x] Twelve projects green — Core 14050/14050, Data 1511/1512 (1 skipped by the profile filter),
      Server 549/549, E2E 221/221, Guard 369/369, CheatCore 41/41, Launcher 165/165,
      ItemSeedValidator 83/83, AtomImporter 33/33, ElementEnumGen 17/17, SquadHarness 193/193,
      TreeBinder 45/45

---

## Phase 4 — Fan-out

*Six modules, all depending on parity, none on each other. Order within the phase is free; it is written
in the map's order.*

- [x] **T4.1 — Empire dimension on the species cache key** · M · deps: CP3 · *(S1, S3, S8)* — **done 2026-09-17**
  - Acceptance: the key carries the empire; the Bound-unique hot path no longer resolves the fallback
  - Verify: a lawn zombie resolves **Zomboss's** empire, not the player's
  - Closed across **three** seams, not one: the persisted key (`ScopeKey(playerId, empire, speciesId)`,
    Dave keeps the unchanged shape so no row needs migrating), the resolve seam (`EmpireForSide(ctx.Side)`),
    and the **transport cache** (`resolveSpeciesAllocation(empire, speciesId)`). The third was the one that
    hid: with the first two fixed a lawn zombie resolved an empty commander term — looking correct — and
    still merged the human player's species rows, because the injector cached them under `speciesId` alone
  - Pinned by two tests that were verified to fail when the empire stops being threaded:
    `The_species_term_is_asked_for_an_empire_and_the_two_sides_ask_for_different_ones`,
    `A_lawn_zombie_never_inherits_the_players_commander_or_species_allocation`
  - **S8 struck, not fixed** — its premise is false in current code. The Bound branch has returned before
    the species lookup since 2026-09-13 (`f1955a1d7`), pinned by three tests, the first of which throws if
    the species path is reached. The 2026-09-17 review that filed S8 read the register, not the code
  - Evidence: Core 14054/14054, Data 1511 passed/0 failed, Guard 369/369, 7 boundary guards OK,
    MelonLoader injector host compiles
  - Found on the way, both recorded rather than papered over: a test-substrate race on the static
    `RpgStore.TestCargoWeightProbe` (fixed — see the commit), and **`SR-15`** in the stub register (that
    probe is the ONLY supplier of every cargo verb's mass lookup, and no production code assigns it)

- [x] **T4.2 — Every cache trigger listed, including the key-set edge** · M · deps: T4.1 — **done 2026-09-17**
  - Acceptance: every invalidation trigger has a test, **including the edge where the key set changes**
  - Note: DESIGN-GATE §2.16 exists for exactly this. **Do not copy a trigger set from a cache with
    different key-set behaviour**
  - Three refresh triggers (session start, SignalR reconnect, the `AptitudesUpdated` broadcast), all
    reaching the cache through ONE fetch — plus the join test that makes those three sufficient, the
    `Stats.Invalidate()` edge, and the wholesale-replace contract. Nine tests, enumerated in the spec
  - **Key-set edge answered in two halves.** The empire never moves on a state change (derived from
    `ctx.Side` per read, never stored) so it adds no fourth trigger — pinned by a test that fails if it
    ever becomes cached state. The half with teeth: the cache can answer only for `{Dave}`, and the day
    Zomboss's species rows ship that set changes — that is the real key-set trigger, made loud by test
  - **Not copied, and the spec says why for each.** The unique cache's bind edge does not apply (this
    key set does not move on a bind); the commander cache's match edges do not apply (no match-scoped
    override here — a match-edge species fetch would be a trigger that cannot fire)
  - Tests live in `FusionRpg.Guard.Tests`, not `FusionRpg.Injector.Tests` — the latter is **not in CI**
    (AGENTS.md), and a trigger set nobody enforces is not enforced
  - Evidence: 9/9 green, and each assertion verified to fail by breaking the wiring it asserts

- [x] **T4.3 — Horde owner row and kill attribution** · M · deps: T4.1 · *(D9)* — **done 2026-09-17**
  - Acceptance: the lawn's general horde has an owner; kill attribution present in every mode
  - Verify: every kill credits exactly one owner — a closure assertion, never a count
  - **The horde's owner was never missing — it was unreadable.** `SpecimenOwnershipOracle` answers
    `ptr → player id` and returns null for anything unregistered, which every vanilla zombie is. Null
    means *no player row*; the code read it as *no owner*. `KillAttribution` separates them: the empire
    is total over the closed `StatSide` vocabulary, the player row rides along only when one exists
  - The empire is the army you fight for, not the row that owns you — Zomboss has a real distinct player
    row, so deriving it from ownership would credit Zomboss's own deployed unique to Dave. Side decides.
    Mind control flips it. Side→empire is T4.1's `EmpireForSide`, asserted to agree, never a second copy
  - **Two side vocabularies**, which is why one overload covered neither: the lawn says `plant`/`zombie`,
    battle says `squad`/`wave` (`BattleModels.cs:10`). Unknown tokens and bullets refuse rather than
    default — crediting the wrong empire silently is the defect's own shape
  - Wired, not just built: `BattleReportEmitter` resolves `creditEmpire` at the one point every mode's
    die event passes through. `killerPtr` named which entity killed, never whose it was — which is how
    attribution stayed "absent outside the lawn" while the payload looked complete
  - Evidence: 12/12, the mode test runs a **real battle per mode** and fails rather than passing
    vacuously; collapsing both battle sides to one empire turns it red (verified)
  - **Does not change who earns.** `RpgStore.Souls` still credits the acting player row; attribution is
    the fact, the soul economy owns the consequence

- [ ] **T4.4 — Species term reaches the compose** · M · deps: T4.1 · *(S2, S7)* — **S2 done 2026-09-17.
  S7 DEFERRED BY OWNER, 2026-09-17** — not merely unfinished. The owner specified what a species level
  grants and ruled it a later sub-program (*"track it and defer"*), recorded in
  `species-progression-ideal.md` §*Deferred sub-program: species level-up grants*. S7 is its first
  consumer. The box stays unticked because the task is genuinely half-done, and ticking it would hide
  that — but the remainder is now **owner-scheduled**, not stalled
  - Acceptance: through `ActorHub` with a GG-49 grammar id. A level-4 plant type composes differently from
    a level-1 one
  - Note: does **not** decide what a species level grants — that is `species-progression`'s question
  - **S2 CLOSED 2026-09-17. S7 is NOT closed and cannot be by this module — see below.**
  - What the next session does not need to re-derive:
  - S2 is at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:559-567` — the `HubInputsFor` provider
    T3.3 added builds `Aptitude = commander + specimen`. There is **no species term**, exactly as S2 says
  - The same lines read `player:{header.PlayerId}`'s commander for **every** member regardless of side, so
    S1's shape is present here too. The fix is one expression, not a new seam
  - **S7 already has its hinge and it works**: `SpeciesBaselineAllocation` derives from the species LEVEL
    row (`GetRpgActor(playerId, Species, creatureTypeId)` → `SpeciesAllocation.Baseline(shares, level,
    tuning)`), so a level-4 species genuinely differs from a level-1 one. S7 is not "build a level term",
    it is "let the existing one reach the compose"
  - **The empire needs no new parameter.** `BuildAnimateSetups` already resolves
    `CreatureSpeciesCatalog.Get(member.SpeciesId)`, whose `.Side` feeds T4.3's `KillAttribution.EmpireOf`
    — the same single mapping, so no faction→commander table has to be invented (and `WorldFactionKind`
    has a `Wild` member that maps to neither empire, so a faction-based mapping would need a third answer)
  - **The one real obstacle**: `EffectiveSpeciesAllocation` takes `lock (_gate)` and opens its own
    connection (`RpgStore.Aptitudes.cs:120-128`), so it cannot be called from inside the world-turn
    transaction as-is. It needs an `...Unlocked(db, tx, ...)` variant alongside the existing one, matching
    `LoadAllocationUnlocked`'s established shape — that is the bulk of the task
  - A fourth S1 seam was found and **fixed** during this investigation (`fb45126f`): the `empire`
    parameter on `SpeciesBaselineAllocation` was accepted and ignored
  - **S2 is closed.** The provider now builds `commander + species + specimen`, with the commander
    gated on the member's own empire and the species term resolved through the new
    `EffectiveSpeciesAllocationUnlocked`. Evidence: Data 1514 passed / 0 failed; Core proves a species
    allocation reaching the compose changes what it composes, through `ActorHub`, with every modifier
    carrying a GG-49 `aptitude.{share}` source id
  - **⚠️ S7 is NOT closed, and routing this term cannot close it.** `AptitudeResolver` reads
    `allocation.Share(edge.Source)` — a **share**, not a point count — and the magnitude comes from
    `pTheta = ladder.Value(theta)`. Ten points and two hundred points in the same single share are both
    share 1.0 and compose **identically** (pinned by
    `Point_count_alone_does_not_move_the_compose_which_is_why_S7_is_not_closed_here`). A species LEVEL
    enters `SpeciesAllocation.Baseline(shares, level, tuning)` as a point count, and battle's theta is
    the **member's** level (`setup.ThetaActor ?? setup.Level`), never the species level. So a level-4
    plant type still composes exactly as a level-1 one
  - Closing S7 means giving a species level a path into **theta or a channel** — which is deciding what
    a species level grants. This module's own note says it does **not** decide that; `species-progression`
    does. S7 therefore needs reassignment to that program, or an explicit owner ruling, and must not be
    ticked here on the strength of S2's fix

- [x] **T4.5 — `MaterialisePlayerSpecies` caller restored** · S · deps: T4.4 · *(S5)* — **done 2026-09-17**
  - Acceptance: a production caller, **and a test that fails if it loses one again**
  - Note: find *why* it was lost before restoring it, or it is re-lost the same way
  - **It was never lost.** `git log -S ... -- src/` returns two commits and both ADD; the 2026-09-02 one
    introduces the method. Every call site ever written lives under `tests/`. A dark feature, not a
    regression — so there was no call site to recover and no cause to avoid repeating
  - Seam chosen from `spec-player-materialise.md`, which names both triggers itself ("at profile
    creation…" and §3 "the new ones are rolled **on next load** and appended") — which is why the method
    is append-only and idempotent: one call serves both. Wired in `Program.cs` **after**
    `SeedImportRunner.RunSelfHealing`, because before it the container tables are empty and the roll
    would silently write nothing and report success. try/catch, same discipline as the content boot
  - The guard scans for a call site **outside `tests/`** — a unit test cannot express this acceptance,
    since it would call the method itself and stay green while production called nothing. That is
    exactly why a fully green suite never noticed. 3/3, all three verified to fail when the caller is
    removed
  - **Found on the way, recorded for T4.6:** two more copies of the same write —
    `ReforgePlayerSpecies` (debug-only caller) and an inlined copy at `RpgStore.Fusion.cs:311-369`. The
    fusion copy's stated reason is transactional (same constraint T4.4 hit), which justifies a shared
    `...Unlocked(db, tx, …)` core, not three copies of the write shape

- [x] **T4.6 — One carrier; fusion picks reach a stat** · M · deps: T4.5 · *(S4, S6)* — **done 2026-09-17**
  - Acceptance: two dark carriers become one; a recorded pick changes a composed stat, end to end
  - Verify: zero readers proved before deleting the second carrier. The nine refusal codes are a **closed
    vocabulary** — pin them
  - **S6 RESOLVED 2026-09-17 by disproof — the deletion must NOT happen.** The second carrier
    (`trait.species-magnitude-{id}`) is live: produced by the species import
    (`RpgStore.Species.cs:114/150/197/214`), consumed by `ReconcileCreatureMagnitudeBindingsUnlocked` on
    every unique-actor deploy, with **904 of 906** species carrying non-empty `magnitudes`. The "dark"
    claim traces to `species-progression-ideal.md` R2 ("`Magnitudes` is empty for every species"), true
    when written and stale since `species-gear-chain` T18. The spec's own Boundaries say *"Always: prove
    zero readers before deleting"* — the proof failed, so the rule is satisfied by **refusing**, not
    proceeding. Deleting it would break a live pipeline this program does not own
  - **S4 investigated; the gap is one join, and it is the only thing left in this task.** The picks
    pipeline is entirely live in production: `GetSpecimenMaterialisedRoll` reads a source specimen's roll
    (`RpgStore.Fusion.cs:253/258`, `FusionEndpoints.cs:192`), picks are forced into the output species'
    instance, and `player_species` is written. What never happens is the last step — **no `effect_binding`
    row is ever written for a `species-passive` instance**, so no actor composes it. `player_species` is
    read in exactly two production places and neither composes: the debug reforge endpoint (before/after
    logging) and a fusion "already owns output" check
  - So the remaining work is **binding `species-passive` to the actor that is that species** so its atoms
    reach `ActorHub` (the `boundDerivedAtoms` seam `ActorHubBootstrap.CreateDefault` already exposes),
    never deleting a carrier
  - **S7's receiving decision now exists** (owner, 2026-09-17), recorded as a deferred sub-program in
    `docs/architecture/species-progression-ideal.md` §*Deferred sub-program: species level-up grants*:
    a species level grants the 12 primary stats auto-assigned from species favour + build preset, with
    seedsmith extended to resolve the distribution matrix, plus signature/family actions and passive
    points onto family/species or build-favour trees (element + status trees included).
    **Tracked and deferred by owner instruction — not built, not specced here**
  - **S4 CLOSED.** `UniqueActorHubCompose` now adds the rolled instance's atoms beside equipment and the
    passive tree — the join that was missing. Projection put in **Core** (`SpeciesPassiveAtomSource`): it
    is the fourth `stat.derived` parse and the other three are already there, so a fourth in the Server
    would be the parallel-path shape this program removes
  - Instance `values_json` first, definition `params_json` second (`ItemCard`'s established order) — a
    pick IS a rolled value, so if the definition won, every player's species would compose the same
    number and the feature would stay inert while looking wired
  - Three refusals asserted, each a defect if coerced: non-`stat.derived`, unknown op, and a **ValueSpec
    object** `amount` (`TryGetInt64` *throws* on an object rather than returning false — that took a whole
    compose down once at the equip seam)
  - GG-49 `species-passive:{speciesId}` — a distinct prefix from `equip:`/`insert:`/`tree:`, so a sheet
    can name which roll a number came from
  - **Nine refusal codes pinned with their count.** Correct use of a literal here per `validation-ssot.md`:
    a refusal code is a declaration the code owns and a human edits, so a tenth SHOULD fail and be
    re-read — the opposite of a population count
  - Evidence: Core 14075/14076, Server 549/549, Guard 5/5 on the new file; the wiring guard verified to
    fail when the join is removed. The one Core failure is `AtomBenchGuardTests`'s wall-clock ns/atom
    budget, which passes 3/3 in isolation and was measured while the Server suite compiled concurrently
    (samples 44.98–86.34) — a known load-sensitive test, and atom compilation is untouched by this change

- [x] **T4.7 — Capture routes through the engine's extension seam** · M · deps: CP3 · *(D12)* — **done 2026-09-17**
  - Acceptance: capture builds on the engine instead of owning battle logic in the delve
  - Verify: `CrossProgramLandedFlags.ItemCostRowLanded` still `false`; the refusal still refuses with the
    same reason; **no new reachability**
  - Note: relocating a mechanism and completing a feature are different work with different owners
  - Moved to `gk-core/src/FusionRpg.Core/Battle/Capture/` (namespace `FusionRpg.Core.Battle.Capture`), test moved
    with it. Same math, same gate, same refusal id, same flag
  - **Why it was wrong, not merely oddly-filed:** the engine already owned capture's *randomness*
    (`BattleRunState.cs:284` derives the `"capture"` stream) while the mechanism drawing on it sat under
    the delve — exactly the split the owner's ruling names
  - **⚠️ Seam finding, as the spec instructs.** There is **no named battle-extension seam** —
    `IBattleExtension` does not exist; the engine's extension surface in practice is the action dispatch
    table, and capture's entry there is explicitly unbuilt (`spec-wild-room.md` §5: "a one-line ask on
    `action-map.md`"). Capture could not be routed through a contract that is not declared, so the module
    put the mechanism where an engine extension belongs and **recorded the seam gap rather than widening
    the engine**, which the Boundaries forbid without recording first
  - All three no-change clauses asserted by test: flag still `false`, `TryGate` still refuses
    `capture.not-landed`, no dispatch entry before or after
  - `guard-battle-responsibility.py` green (19 mechanisms, 1448 files). Capture is **not** one of the 19
    — worth stating: the guard was never going to catch D12, because capture's battle-affecting half is
    unbuilt. The relocation makes the guard's silence correct rather than lucky
  - Evidence: 32/32 capture tests, 89/89 including the wild-refusal siblings, stub-register guard 5/5
  - Register: **`SR-16`** — the hand-off the spec asks for, owner `party-dungeon`, waiting on the A3
    item-cost row

- [x] **T4.8 — Death/injury mechanism lifted into the engine** · M · deps: CP3 · *(D10)* — **done 2026-09-17**
  - Acceptance: `SettlementOutcome` and the member-settlement decision become engine vocabulary; the delve
    consumes them with its difficulty ladder **unchanged**
  - Note: promotion, not construction — injury is already an ActorHub subsystem (`ActorHub.cs:180`)
  - `SettlementOutcome`, `MemberSettlement` and the Retire/Recover/Roster rule moved to
    `gk-core/src/FusionRpg.Core/Battle/Attrition/` (`MemberSettlementRules.Decide`). The rule is byte-for-byte the
    delve's own — the defect was ownership, not a missing mechanism
  - **The ladder stays the delve's, and that is structural, not a promise:** a test asserts **no parameter
    of `Decide` is a Delve type**. `permadeathApplies` was always resolved by the caller, which is exactly
    what made the decision portable — a mode with a different ladder, or none, answers the same question
    with its own input
  - **`PartyStands`/`IsWiped` deliberately did NOT move.** They read `DelveMemberState`, a delve party
    shape; promoting them would drag a mode's vocabulary INTO the engine — D10's own defect pointing
    backwards. Asserted too, so the boundary is pinned in both directions
  - Evidence: Core 14081/14081, Data 1514 passed / 0 failed, 28/28 on the settlement suite

- [x] **T4.9 — Ladder as a per-mode input** · S · deps: T4.8 — **done 2026-09-17**
  - Acceptance: one interface, one call site. A mode with **no** ladder **refuses** rather than silently
    never triggering
  - Note: a silent zero is how the lawn got here
  - `IPermadeathLadder` replaces the `bool permadeathApplies` on `MemberSettlementRules.Decide` — one
    interface, one call site. **Null refuses**, with a message naming the alternative
  - **Why an interface and not a better-named bool:** a bool has a value meaning "no permanent death
    ever", and it is the value a mode gets by *not thinking about the question* — indistinguishable at
    every call site and in every test from a mode that decided. `NeverPermadeath.Instance` is that same
    outcome written down as a decision a reader can see
  - The delve supplies `PermadeathGate.Ladder`, holding its own rung/domain inputs — so the engine still
    never learns `difficulty-ladder`'s vocabulary, and T4.8's structural assertion still holds
  - A test proves the ladder is **not consulted at all** for a member who never went down (a ladder that
    throws if asked), so a mode's ladder cannot start running on every settled member
  - Evidence: 31/31 on the settlement suite

- [x] **T4.10 — Lawn ladder, keyed to damage taken** · S · deps: T4.9 — **done 2026-09-17**
  - Acceptance: more damage taken, more chance of injury and permanent death. Ships **working values** in
    `gk-core/data/tuning/` with an `_meta` note saying they are unmeasured
  - `LawnPermadeathLadder` + `gk-core/data/tuning/lawn-attrition.v2.json`. Zero below a floor, rising linearly to
    the tuned chance at a full bar taken; permanent death sits on a **higher** floor than injury, so a
    member risks a limb before it risks a life
  - **Tests assert the direction, never the constants** — the task's own rule. Monotonicity, the floors,
    overkill clamped rather than extrapolated, and the loader refusing a file that inverts the ordering.
    A balance pass can move all four numbers without turning any of it red
  - Deterministic: the caller draws the roll and hands it in (`CaptureAction.Resolve`'s shape), so the
    ladder owns no RNG and a replay settles identically
  - Found while testing: one per-mille above a floor still truncates to **zero** chance in integer
    per-mille arithmetic. A property of the shape, not a defect — but it makes the boundary the wrong
    place to sample, so the band test samples the middle instead
  - Evidence: 8/8

- [x] **T4.11 — `SiegeExpectedDamage` uses the shipped defense shape** · M · deps: CP3 · *(D7)* — **done 2026-09-17**
  - Acceptance: divisive (not subtractive), with a base-damage term and amp/crit. **The false "identical to
    the resolver" comment corrected in the same change**
  - Note: §6.3a records subtractive was dropped because **17.1% of landed hits dealt nothing**
  - Now mirrors the resolver's omni branch term for term: pierce-scaled defense inside the delta,
    offense = base + power, `DivisiveMitigation` with the same `K` and the same ladder scale, then
    amplification through whichever `AmpShape` ships
  - **The comment was the dangerous half**, and it is corrected in the same change. It cited a specific
    file and line range, which is exactly what makes a stale claim survive review — a reader checking the
    estimator found a citation and stopped
  - **Crit is reported separately, not folded in.** It is a rolled branch in the resolver, so an estimate
    multiplying by it unconditionally would call every marginal target lethal — the mirror of the defect
    being fixed. `CritMultiplier` exposes it for a caller that wants the upside explicitly
  - Evidence: 312/312 across the siege suite

- [x] **T4.12 — Estimator parity test** · S · deps: T4.11, T1.7, T1.8 · *(D7)* — **done 2026-09-17**
  - Acceptance: the estimator agrees with the resolver within a **stated** tolerance, and the tolerance's
    reason is written down
  - Verify: fails on a synthetic divergence. Assert agreement, never a fixed expected number
  - Tolerance is **half a point of damage plus a last-bits epsilon**, and the reason is one specific step:
    the resolver returns an integer `SignedDelta`, rounding once at its `long` boundary, while the
    estimator answers an unrounded `double` because a targeting score has no reason to quantise. Sized to
    that rounding — **not** to absorb a modelling difference
  - The synthetic-divergence test **proves** that rather than asserting it: dropping the base-damage term
    (one term missing, D7's own shape) lands far outside the tolerance and fails the same comparison
  - Seven matchups spanning the shape, including **defense above power** — the band the subtractive
    estimator got wrong — and negative defense. Every assertion compares the two implementations against
    each other, so a balance change to `DefenseDivisorK`/`PierceScale`/`AmpScale` moves both and turns
    nothing red
  - Evidence: 10/10

- [x] **T4.13 — X5: the copy deleted** · S · deps: T4.12 — **done 2026-09-17**
  - Acceptance: zero readers proved, then deleted. The analytic migration finally becomes a move
  - **Zero readers was disproved for the FILE and proved for the MATH.** `gk-core/tools/CombatSim/Analytic.cs` has
    many live readers (`BestResponse`, `Marginal`, `Program`, plus `ProvePredictor` and
    `CreatureQualityReport`), so deleting the file was never the move. What was duplicated is the
    five-atom mixture: `Analytic.Strike` and `Core.Balance.Analytic.StrikeMixture` were two owners of the
    same arithmetic, line-for-line equivalent
  - The caller is repointed and the duplicated body deleted. `Strike` is now a **projection** — `Archetype`
    mid-range stats into the snapshot Core takes, and Core's five atoms back into `StrikeStats`. No combat
    arithmetic survives in it
  - **Numerically neutral, measured not assumed:** `ProvePredictor` actions-only max diff is 8.836E-007
    after the repoint, unchanged, still PASS against its own 1e-4 gate
  - ⚠️ **Still open and NOT closed by this task:** `ProvePredictor` actions+status fails its 1e-4 gate at
    **9.222E-004**. Pre-existing, unchanged by the repoint, and a different pair from T4.12's (that one is
    estimator vs resolver; this is `Predictor` vs the CombatSim reference). It sits far inside P4.6's own
    ≤7.7% acceptance band, so the 1e-4 gate is a stricter self-check — but it is a real red and is recorded
    here rather than absorbed

- [x] **T4.14 — Status timing reads the engine clock** · M · deps: CP3 · *(D15)* — **done 2026-09-17**
  - Acceptance: status expiry is computed from the engine's clock, the same source DoT scheduling already
    reads. The wall clock keeps its role as the lawn's time **source**, feeding `ITimeAdvance`, and stops
    being the **scheduler**
  - Verify: one tick vocabulary — a DoT pulse and a status expiry computed in the same place, on every board
  - Note: the injector's wall-clock wiring is a **documented deliberate choice**. `EffectBag`'s own error
    text says a live host wires it *"explicitly, on purpose, at its own composition root."* The defect is
    **not** that choice — it is that the choice was made for the time **source** and silently became the
    **scheduler** for half the tick vocabulary. Anyone reading it as a mistake will delete a correct
    decision. Update that comment to say which role it now plays
  - **The note is right and it is why the fix is a role change, not a deletion.** The injector's
    `_bag.UtcNow = () => DateTimeOffset.UtcNow` was deliberate and documented. What went wrong is
    narrower: pulse scheduling rides the engine (a 100 ms grid accumulated from frame delta), while
    expiry compared against whatever the wall clock returned at that instant. One tick answered "has a
    pulse come due?" in engine time and "has this status expired?" in wall time
  - `AdvancedEffectClock` is **seeded from** the wall clock (still the SOURCE) and **advanced by** the
    same frame delta that already drives the pulse grid (now the SCHEDULER). Advanced *before* the
    accumulator gate, so a status expires on real elapsed time rather than only on frames that complete
    a 100 ms bucket
  - Negative deltas are **ignored, not rejected** — a live host produces them across a pause or a clock
    adjustment, and a schedule running backwards would RESURRECT expired statuses. NaN/infinity likewise:
    throwing would take down a live match for one bad frame
  - The `EffectBag.UtcNow` comment now says which role the live wiring plays, as the note asks
  - ⛔ **CORRECTION 2026-09-20 (`backlog-clean-up` BCU8.3): this fix was INERT on every live board from
    2026-09-17 until BCU8.3 fixed the wiring.** The advance was placed in
    `EffectRuntime.TickDots(float)` at `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs` — but
    `InjectorLoop` calls that method only under `if (!KernelDriveHost.DrivingGrids)`, and
    `DrivingGrids` is `_drive != null && GridsOnKernel`, i.e. **false only off-board or when
    `FUSIONRPG_KERNEL_GRIDS=0`**. On a live board with the kernel driving, `TickDots` was never
    called, so `_clock.AdvanceSeconds` never ran, so `_bag.UtcNow` returned a frozen instant: the
    DoT/status pulse's `now < inst.NextPulse` gate never opened and `ExpiresAt < now` never fired.
    (`KernelDriveHost` was created 2026-08-31 by B26; T4.14 landed into the already-gated method on
    2026-09-17.) **Cause read, not inferred:** T4.14 chose the accumulator as its advance point
    *because* that was where the 100 ms frame-delta grid lived, and B26 had just moved that grid's
    work onto the kernel while leaving the (now dead) accumulator as the kill-switch fallback.
    **Fixed by BCU8.3:** the advance moved to `KernelDriveHost.Tick`, off the same scaled delta the
    kernel advances by, and the accumulator + kill switch are deleted.
    Guard: `gk-core/tests/FusionRpg.Guard.Tests/InjectorKernelGridsGuardTests.cs`
    (`The_effect_clock_advances_from_the_kernel_tick`).

- [x] **T4.15 — Determinism proof** · S · deps: T4.14 · *(D15)* — **done 2026-09-17**
  - Acceptance: the same scenario replayed twice produces identical results
  - The same uneven frame sequence replayed twice lands on the **same instant**, and a second test proves
    the result does not depend on real time passing between the two runs. That is the contract a
    wall-clock schedule **cannot satisfy even in principle**, which is the sharpest statement of D15
  - One further test shows a 250 ms expiry and a 100 ms pulse grid read off **one number**: after 300 ms
    of frames, exactly three pulses and an expired status, both derived from the same clock
  - Durations stay integer milliseconds — no fractional seconds reintroduced (`green-baseline`'s incident)
  - Evidence: 6/6

- [x] **T4.16 — Hot-path budget held** · S · deps: T4.14 · *(D15)* — **done 2026-09-17**
  - Acceptance: **no new round trip** on the injector hot path
  - **No round trip exists to measure**, which is the design answering the note rather than the note being
    waived: `AdvancedEffectClock.UtcNow` is a field read on a type with no I/O surface. Asserted
    structurally by a guard — no `Http`, no `await`, no `Task<`, no store, no client — so a future edit
    that gave the clock one fails immediately, rather than being caught by a measurement nobody re-runs
  - The guard also pins the role change itself: the injector reads `_clock.UtcNow`, no longer
    `DateTimeOffset.UtcNow` per question, and still seeds from the wall clock via `StartingNow()`
  - Evidence: Guard 6/6

### ⚠️ CP4 — the fan-out is NOT complete (assessed 2026-09-17)

**Every task T4.1–T4.16 is done and evidenced. CP4 is still not met**, and the gap is the point of
having a checkpoint at all: its clauses were checked against **call sites**, not against the task list,
and three of them ask for more than the tasks that feed them deliver.

- [x] Every module in this phase recorded its stub/FE register rows, or stated it added none
  - `species-empire-scope`, `capture-as-extension` (`SR-16`), `species-carrier` (none, with reasons),
    `death-and-injury` (**`SR-17`**), `estimator-parity` (none, with reason)
- [x] **Progression credited to whoever earned it, in every mode** — **MET 2026-09-17**, by owner
  ruling *"Sr-18 owner of unique actor"* plus a re-check of every mode against code.
  - **Lawn XP** — already correct before today: `TryRecoverActiveByPtr` resolves the killer by
    `killerPtr` among opposing, still-bound specimens and `AwardUniqueLawnKillUnlocked` writes XP to
    that specimen with an idempotency receipt
  - **Lawn souls** — **the half that was actually wrong, now fixed** (`66bb3268` + `d8021da4`).
    `ApplySoulEarnFromActivityUnlocked` credited the run's player unconditionally. The register blamed
    the `ZombieKilled` fact carrying no attribution; the fact does not, but the raw capture payload
    reaching that method does, so the attribution was being dropped at the projection one frame from
    where it was needed. Souls now credit the killing specimen's owner, with the same opposing-side
    check the XP path uses — the two finally agree about the same kill
  - **Battle** — per-actor already: `BattleReportEmitter` tallies `xpMilli`/`kills` per actor key, and
    `ExpeditionEndpoints.cs:157-161` applies it per `instanceId`
  - **Delve** — **awards no specimen XP at all** (`RpgStore.Delve.cs` has zero `AwardUniqueActorXp`
    call sites, and `Core/Progression` declares no delve award). That is an absent feature, not a
    mis-credit: nothing is being credited to the wrong earner, so it does not hold this clause open.
    Recorded rather than glossed, because "no progression in that mode" is worth someone knowing
  - **What did NOT close, and is still guarded:** `creditEmpire` itself. The souls fix used `killerPtr`,
    not that field, so `BattleReportEmitter.cs:73` still writes an empire id no production code reads.
    It stays a `dark` register row with `DarkCarrierGuardTests` asserting it has exactly one production
    site — a canary that goes red the day a consumer lands. The clause is about progression reaching the
    right earner, which it now does in every mode that awards any; an unread redundant field is debt,
    not a mis-credit
- [x] Fusion picks change a player's actors — T4.6: the rolled `species-passive` instance reaches
  `ActorHub` through `UniqueActorHubCompose`, with a GG-49 `species-passive:{id}` source id
- [x] Capture routes through the engine; still refuses; no new reachability — T4.7, all three
  no-change clauses asserted by test
- [x] **Deploying a unique actor is a cost in every mode** — **MET 2026-09-17, by owner ruling.**
  - **The original reading was wrong, and it was taken from a comment rather than the code.** This
    clause and `SR-17` both said the lawn had *no settlement call site at all*, so nothing was ever
    settled and no player outcome depended on it. The lawn settled **every** death — it inlined the
    delve's own `case Retire:` branch verbatim, so every unique actor that died on the lawn was
    permanently lost. The cost was not missing; it was maximal, untuned, and invisible
  - **Owner ruling (verbatim):** *"Lawn permanent Death? Use damage scale and low chance permanent
    death, that mode is casual, dont kill all player unique demon, so injury also low too."*
  - **Wired.** The lawn asks `MemberSettlementRules.Decide` with the tuned `LawnPermadeathLadder`:
    a death that misses the roll recovers to Roster with gear still worn and no corpse cache; only one
    that makes it retires and caches. `lawn-attrition.v2.json` drops permadeath 150→**40‰**, injury
    400→**120‰**. So a deployment now carries a real, tuned, *survivable* cost in both modes that
    settle — delve (`RpgStore.Delve.cs:848`) and lawn — through the one engine seam
  - **The accumulator was never needed for this half.** `damageTakenMilli = 1000` is exact for a lawn
    death: a specimen named by `plant.die`/`zombie.die` lost its whole bar by definition. The
    accumulator blocks only the INJURY half, for survivors, which the ruling did not ask for and which
    stays tracked as its own gap
  - **A second dark carrier closed with it:** nothing in `src/` or `tests/` had ever called
    `LawnAttritionTuningHub.Configure` — hub and tuning file both shipped unread. Now loaded at server
    startup and in both test bootstraps
  - **Determinism:** the roll derives from (instanceId, matchKey, occurrenceId), so re-ingesting a die
    event cannot flip a specimen between alive and permanently dead — asserted by
    `Re_ingesting_the_same_die_event_cannot_change_the_outcome`
  - Core 14118/14118, Data **1582/1582**, Server 550/550, E2E 221/221, Guard 386/386
- [x] **Estimators agree with the resolver or are pinned to it** — **MET 2026-09-17.** True for D7's
  pair from the start (estimator vs resolver, 10/10, tolerance and reason written down). The second
  half, `ProvePredictor`'s actions+status axis, was red at **9.222E-004** against its own 1e-4 bound and
  is now **8.836E-007** — exactly the actions-only figure, so the status term contributes no divergence
  of its own. All four axes pass and the tool exits 0.
  - **It was a real defect in the port, internal to it rather than a disagreement with the reference.**
    `Predictor.Predict` carried each side's DoT into `dealtMean*` and therefore into the damage RATE,
    while passing the raw `swing*.Mean` into `ShieldEffectiveHp` and `RecoveryPerRound`. The same fight
    counted a DoT as damage when deciding how fast HP fell and pretended it did not exist when deciding
    how long the shield lasted and how much regen had to out-heal. Fixed by passing `dealtMean*` to all
    four sites (`79e63f49`)
  - **Five hypotheses were falsified by measurement before the right one.** Not this program's D7
    reference change (re-ran against the pre-`08409554` `Analytic.cs`: 9.222E-004 identical); not two
    resistance models (same shipped `ResistanceEvaluator`); not different actor inputs (identical
    `(Min+Max)/2.0` midpoint); not the uptime/DoT/CC composition; not the action multiplier scaling the
    status magnitude (`rateA` matched to every printed digit). **Localized** by `PROVE_TRACE=1`: on
    FORCE v BASTION every term matched except `reflectShareA` (0.700588866432 → 0.718918527467) and
    `recovA`, both functions of incoming damage — and the status inflates BASTION's output
    13060.93 → 57491.58, which is why that one pair breached the gate while the rest sat at 1e-7
  - **The "drift owned by `class-system`" framing is retired, and it was wrong in two ways.** Nothing
    regressed and nothing drifted in the file that was blamed: the inconsistency was always present, and
    the gap merely grew as tuning moved beneath it — which is how the same code measured 9.146e-5 at
    P4.6 and 9.222E-004 before this fix. Ownership was an assumption about location, never a measurement
  - **The pinning test did its job in the direction that is easy to get wrong.**
    `ProvePredictorTests` pinned the known-red state and went red *because the tool went green*. Its own
    comment said the correct response was to assert `exit == 0`, never to loosen anything — followed
    exactly. It now asserts all four checks by name rather than inferring them from the exit code
  - Core 14118/14118, Guard 387/387, Server 550/550, E2E 221/221, SquadHarness 193/193
- [x] One clock; a scenario replays identically; perf within budget — T4.14–T4.16
- [x] **Twelve projects green** — **MET 2026-09-17**, after the two flakes below were each root-caused
  and fixed. Earlier, weaker measurement retained underneath for the trail.
  - **The reason this clause carried for two checkpoints is gone.** It read: *"a suite that has failed
    once and cannot be reproduced on demand is not a suite anyone can call reliably green."* That was the
    right bar. The 548/549 failure has since been reproduced **deterministically, twice, by two different
    injections**, root-caused to **two independent flakes**, and both are fixed:
    1. **`WorldMarchCostProjectionTests` — a species-catalog swap** (`4951d773`). `CreatureSpeciesCatalog`
       is process-wide; `DelveRoomEncounterTests` installs the imported roster in its constructor while
       `PowerAndAptitudeTuningTestBootstrap` installs the compiled default at assembly load. The legion's
       three members exist in the compiled catalog and are absent from the imported one, so the banner
       stopped being Ice and a ley discount applied: 720 became 576. Putting both classes in one xUnit
       collection made the failure deterministic, which is what proved the mechanism
    2. **`DelveBattleSessionTests.OnDeclared_reports_timeouts_as_timeouts_through_the_freeze` — a
       freeze-callback race** (`aa3f2bb7`). `DelveBattleSession.Freeze` publishes `Frozen = true` under
       its gate and invokes `_onFrozen` after it, so a test spinning on `Frozen` could wake inside that
       window and assert on an empty log. The production ordering is correct and was left alone —
       `Frozen` gates `Declare`/`Ask`, and a caller-supplied callback must not run under the lock — so
       the contract text and the test's wake-up signal were what changed. Proven with a temporary
       `Thread.Sleep(300)` injected into that window: the old shape found an empty log every time and
       all seven real tests passed through the widened window, 9/9
  - **Measured green after both fixes, today.** Thirteen projects, Release profile: Core **14114/14114**,
    Data **1578/1579** (1 skipped, since closed — see below), Guard **384/384**, E2E **221/221**, Server
    **550/550**, CheatCore 41/41, Launcher 165/165, ItemSeedValidator 83/83, AtomImporter 33/33,
    ElementEnumGen 17/17, SquadHarness 193/193, TreeBinder 45/45, FileMove 9/9. All seven boundary guards
    OK. **Server.Tests additionally run six consecutive times: 6/6 green at 550/550**
  - **The suite's last skipped test is gone, and by being made true rather than deleted** (`29459f9e`).
    `CorpseCacheTests.SaveAssignment_refuses_a_non_Roster_specimen` was `[Fact(Skip=...)]` because
    `SaveAssignment`/`RemoveAssignment` carried no phase gate, so the deploy-time-snapshot anti-fraud
    property could not be observed. The gate landed (mirroring `RpgStore.Expeditions.cs:60-61`), nine
    fixtures that were deploying-then-equipping were reordered to the real sequence, and Data.Tests now
    reads **1579/1579 with zero skipped**
  - **RE-VERIFIED after the `Predictor` fix (`79e63f49`), 2026-09-17.** These clauses were ticked before
    that change, which touched a Core balance primitive — so the numbers were re-taken rather than left
    to stand on pre-change evidence. **All thirteen CI projects green on current HEAD:** Core
    14118/14118, Data 1579/1579, Server 550/550, E2E 221/221, Guard 387/387, SquadHarness 193/193,
    Launcher 165/165, ItemSeedValidator 83/83, AtomImporter 33/33, TreeBinder 45/45, CheatCore 41/41,
    ElementEnumGen 17/17, FileMove 9/9 — plus all seven boundary guards OK and `ProvePredictor` exiting 0
  - **One measurement correction worth carrying:** the suite reports **550** where six earlier runs
    reported 549. The source contains 537 `[Fact]` plus 13 `[InlineData]` = **550**, so 550 is the real
    population and those earlier runs executed a **stale assembly missing one test** — which means the
    "Server 549/549" figures recorded earlier in this file were taken from an incomplete build. Recorded,
    not pinned: a suite size is a reading, never a contract

  <details><summary>Earlier measurement, superseded (kept for the trail)</summary>

  **final sweep 2026-09-17 is GREEN**: Data 1514/0, Server **549/549**,
  E2E 221/221, Core 14114/14114 in one combined `-AllDefault` run, plus Guard 384/384, CheatCore 41/41,
  Launcher 165/165, ItemSeedValidator 83/83, AtomImporter 33/33, ElementEnumGen 17/17, SquadHarness
  193/193, TreeBinder 45/45, FileMove 9/9 measured individually — thirteen projects, all green, and all
  seven boundary guards OK. **The clause stays unticked anyway**: one earlier combined run was 548/549,
  and a suite that has failed once and cannot be reproduced on demand is not a suite anyone can call
  reliably green. Green-this-run is not the same as green. Earlier measurement below.
  </details>
  Server **549/549 on a clean re-run**, but **548/549** in the combined `-AllDefault` profile:
  `WorldMarchCostProjectionTests.An_unscouted_leys_discount_does_not_apply_priced_against_belief_not_truth`
  expected 720, got 576 — the projection priced against TRUTH where the test writes a truth/belief split.
  Passes 3/3 in isolation AND 549/549 alone, so it is **order-dependent on world state another test
  mutates** (a scout that moves Dave's BELIEF of `d-flank-1` to Ice makes the ley discount legitimately
  apply), not a march-cost defect. Not caused by this phase — Server was 549/549 twice today with
  T4.1–T4.6 already landed. **Real and not yet diagnosed**: an intermittently-green suite is a defect of
  its own, the same class as the `TestCargoWeightProbe` race this program fixed at the start. Recorded,
  not waived
  - **Diagnosis as far as it is established (2026-09-17), so the next session does not restart it:**
    576 = 800 length × 900‰ ley × **800‰ ley discount**, so the discount APPLIED where the test asserts it
    must not. `LaneCost.LeyDiscountMilli` is a code `const`, and both `world.v5.json` and `world.v6.json`
    ship `ley: 900` — so **the variance is not tuning**. It is either the believed-climate lookup
    returning Ice, or the legion's banner element resolving differently
  - The banner is the fragile half and worth checking first: the test's own comment derives it from
    three tied singleton elements where *"first in `ElementTypeId`'s own declared order wins"*. A
    tie-break on declaration order is exactly the kind of premise that shifts under an unrelated change
  - What is ruled out: cross-test DB state (each class builds its own in-memory `DataTestStore`) and my
    own changes (Server was 549/549 twice today with T4.1–T4.6 landed, and 549/549 again on a clean
    re-run after all of Phase 4). What is NOT ruled out: the process-wide statics these classes share —
    `WorldTuningHub`/`LoamPolicy`, where this class's `_tuningConfigured` flag stops only ITSELF from
    re-configuring
  - **Correction to an earlier note in this file:** the "two classes load `world.v5.json`" reading was
    wrong — those hits are `loam.v5.json`. **Every** class loads `world.v6.json`, so a world-tuning
    version conflict is ruled OUT, not merely unproven
  - **Rate measured 2026-09-17:** 4 clean full-suite runs ⇒ 549/549 each; the only failure is the single
    combined `-AllDefault` run. `World*`-only is 71/71, and `WorldMarchCostProjectionTests` +
    `AptitudeEndpointsTests` together is 16/16 — so the trigger is neither the World classes nor the
    obvious catalog-configuring sibling, and it is NOT reproducible on demand yet
  - **Hypotheses RULED OUT (so the next session does not redo them):**
    1. *World-tuning version conflict* — no. Every class loads `world.v6.json`; the "v5" hits are
       `loam.v5.json`
    2. *Ley multiplier drift* — no. `ley: 900` in both v5 and v6, and `LaneCost.LeyDiscountMilli = 800`
       is a code `const`
    3. *Species catalog not configured, so the banner never resolves* — no.
       `PowerAndAptitudeTuningTestBootstrap` is a **`[ModuleInitializer]`**, so
       `CreatureSpeciesCatalog.ConfigureFromCompiledDefault()` runs at ASSEMBLY LOAD for every test in
       the project. The banner always resolves
    4. *Cross-class database state* — no. `InitializeAsync` builds a fresh in-memory `DataTestStore`
       per test
  - **What remains**, and where a next attempt should start: 576 = 800 × 900‰ × 800‰, so the discount
    APPLIED, which means the **believed** climate of `d-flank-1` read as Ice where the test expects
    Earth. With the four above ruled out, the belief lookup itself is the surface left to examine — not
    the tuning, not the catalog, not the discount constant
  - **Leading hypothesis, explicitly UNVERIFIED** — recorded as a lead, not a conclusion, because it was
    not reproduced: the projection reads `believedView.Believed(sectorId)?.Climate`
    (`WorldEndpoints.cs:83`), and belief re-syncs to truth on an Intel pass. The test writes truth = Ice
    by raw SQL and relies on a belief of Earth seeded earlier. **Anything that materialises or refreshes
    belief between that UPDATE and the read would copy the new truth**, giving Ice, the discount, and
    576. That is the only mechanism found that produces this exact number without any tuning, catalog or
    constant being wrong
  - Whoever picks this up: confirm or kill that hypothesis FIRST (does belief for `d-flank-1` exist and
    equal Earth immediately before the failing read?), rather than re-deriving the four ruled out above
  - **Not fixed, and not papered over.** An intermittently-green suite is a defect of its own class (the
    same one as the `TestCargoWeightProbe` race this program fixed at the start). A speculative fix for
    something reproducible 1-in-5 and not on demand would be worse than an accurate record
  - **All twelve measured 2026-09-17**, the other seven run individually rather than assumed from the
    four-project profile: CheatCore 41/41, Launcher 165/165, ItemSeedValidator 83/83, AtomImporter
    33/33, ElementEnumGen 17/17, SquadHarness 193/193, TreeBinder 45/45 — plus Core 14108/14108,
    Data 1514/0, E2E 221/221, Guard 381/381
  - So this clause is **green everywhere except the one order-dependent Server failure above**, which
    is what keeps it unticked. Twelve projects are not green *as a suite* while one of them is
    intermittently red

**What CP4 blocks on**, stated so the next session does not re-derive it: a lawn settlement call site
(`SR-17`), the earning half of D9, the `ProvePredictor` divergence, and the Server ordering leak.

---

## Phase 5 — Independents

*Depend only on the baseline. Last on purpose: low risk, no dependants.*

- [x] **T5.1 — Status categories declared once** · S · deps: CP0 · *(X1)* — **done 2026-09-17**
  - `StatusCatalogBootstrap` carried its own 23 status→category literals beside
    `StatusCategoryRegistry`'s map. The registry is the owner; the bootstrap's `Register` helper no
    longer takes a category at all and reads `GetRequiredCategory` instead — which **throws** for an
    unknown id, so a status catalogued without a registry entry now fails at bootstrap rather than
    shipping a catalog entry that disagrees with the resist channel meant to answer it
- [x] **T5.2 — Element ids declared once, one failure mode** · S · deps: T5.1 · *(X2)* — **done 2026-09-17**
  - Acceptance: an unknown element **throws, naming it** — never `""`, never a default
  - Note: X2 is a **silent wrong answer** risk: one switch returns `""` where the other throws, so a missed
    element currently reads as a neutral matchup with no error
  - `ElementTable.IdOf` is now an alias of `ActorElementTypes.ToElementId`, not a second switch. The
    `""` was the real defect: `IdOf` feeds `ElementRingMatrix` and `ShieldElementMatrix`, which look the
    id up in the matchup table, so an empty id matched no row and a missing element resolved to a
    **neutral matchup with no error** — a plausible damage multiplier nothing reports
  - Aliased rather than deleted-and-retyped, per the spec: the mapping is content, and re-typing six
    strings is how content quietly changes
  - Six tests: both spellings agree member-for-member, both throw naming the member, no id empty or
    duplicated, the category vocabulary closed at three, and an unknown status id throwing. **Counts are
    pinned deliberately** — these are enums a human edits, `validation-ssot.md`'s own closed-vocabulary
    case. Verified to fail by re-forking the switch
- [x] **T5.3/T5.4 — Pool regen: one declaration** · S · deps: CP0 · *(X3)* — **done 2026-09-17**
  - **The two owners are inside `BattleModels` itself**, not two distant files: `BaseResourceRegen`
    recomputed `checked(BaseHp(theta) * ShareOf(id)) / 1000` inline — the exact expression
    `BaseResourceMax` declares — and then derived regen from its own copy
  - **They did NOT disagree numerically**, contrary to X3's wording: the two expressions are identical,
    which is why nothing had surfaced. The risk is live all the same — a share row edited with only one
    in view moves a pool's size without moving its regen, or the reverse, and nothing reports it
  - Second site now calls the first. No number moved: 161/161 on the resource/ruleset suites, and the
    de-duplication is behaviour-preserving by construction rather than by re-derivation
  - `ResourceBaselineSubsystem` was already routed at `BaseResourceRegen`, so there was no third owner
    to delete — "zero readers proved" is satisfied by there being no loser, not by a deletion
- [x] **T5.5 — File-move tool: move and rewire** · M · deps: CP0 — **done 2026-09-17**
  - `gk-core/tools/FileMove` — namespace from the destination folder, `using` rewiring across callers, explicit
    `Compile` items repointed on a cross-assembly move, assembly-cycle refusal that **names the cycle**,
    and a dry run
  - **Dry run is the DEFAULT, not a flag.** A tool whose destructive mode is the default teaches people
    to add `--dry-run` from memory; inverting it makes forgetting safe. `Plan` computes the whole change
    set and `Apply` only writes it, so preview and apply cannot diverge by construction
  - No project references at all: it rewrites source and `.csproj` files as text, and a cycle-refusal
    tool that could itself be inside a cycle is not worth trusting
- [x] **T5.6 — File-move tool tests** · S · deps: T5.5 — **done 2026-09-17**
  - Verify: assert the tool's contract. **Never** assert how many files in the repo are misfiled
  - 9 tests, all against a **synthetic two-assembly repo** — the spec insists, because the four real
    files exercise only the base case. That fixture immediately found **three real defects** in the
    tool: it threw on a destination folder that does not exist yet (the ordinary case), it threw on a
    repo without `tests/`, and **the cycle check was inverted**
  - The inversion is the one worth keeping: moving a file OUT of Server INTO Core is risky precisely
    because Server already references Core, so the moved file's remaining ties force Core→Server. The
    first cut asked the opposite question and refused nothing. The mirror direction is asserted too, so
    the refusal is proven specific rather than "all cross-assembly moves fail"
- [x] **T5.7 — Confirm the 89 convention files untouched** · XS · deps: T5.5 — **done 2026-09-17**
  - Re-measured 2026-09-17: **1,320 C# files, 97 namespace≠folder, 89 `FusionRpg.Data` flat-root,
    8 injector host shims, 0 genuinely misfiled.** The four are resolved (T0.6 did them) and the
    convention files are untouched
  - The spec's own table read 1,313 / 102 / 89 / 9 / 4. The deltas are code shipping since, plus the four
    T0.6 closed — **recorded as a re-measurement, never asserted in a test**: it is a reading that moves
    whenever code ships, which is exactly what T5.6 is forbidden from pinning

### ✅ CP5 — independents landed (assessed 2026-09-17)
- [x] Every module in this phase recorded its stub/FE register rows, or stated it added none
  - `vocabulary-single-declaration` none, `numeric-single-source` none, `file-move-tool` none — each with
    its reason, so "no rows" is a recorded decision rather than an omission
- [x] Two vocabularies, one declaration each, one failure mode each
  - Elements: `ElementTable.IdOf` aliases `ToElementId`; both throw naming the member, and the `""` that
    made a missing element read as a neutral matchup is gone. Statuses: the catalog bootstrap reads
    `StatusCategoryRegistry.GetRequiredCategory`, which throws
- [x] One pool-regen implementation, unit in its name
  - `BaseResourceRegen` calls `BaseResourceMax` instead of recomputing it. Locals renamed to carry their
    units (`poolMaxUnits`, `regenPerSecondUnits`); the method already documented its return as units per
    tick
- [x] Move tool works and refuses an assembly cycle
  - 9/9 against a synthetic fixture, including the cycle refusal **naming the cycle** and its mirror
    direction being allowed. Wired into CI at introduction rather than left for `CiWiringGuardTests` to
    find later; `AGENTS.md`'s project count updated 12 → 13 in the same change
- [x] **Twelve projects green** — **MET 2026-09-17**, same status as CP4's clause and closed by the same
  two fixes. Thirteen projects with FileMove 9/9; the order-dependent `WorldMarchCostProjectionTests`
  failure that held this open was a process-wide species-catalog swap (`4951d773`), and a second,
  independent freeze-callback race in `DelveBattleSessionTests` (`aa3f2bb7`) accounted for the rest.
  Both reproduced deterministically before being fixed. Evidence is written once, under CP4's clause,
  rather than duplicated here

---

## Phase 6 — Close

- [x] **T6.1 — Register coverage audited** · S · deps: CP5 — **done 2026-09-17**
  - Acceptance: every one of the 27 entries **fixed, reassigned, or struck with a reason**, against the
    map's *Register coverage* table
  - Audit written into `solid-remediation-map.md` — every entry checked against the **code and the task
    record**, not against the table's own earlier claim
  - **26 of 27 dispositioned; S7 is open and this program cannot close it.** `AptitudeResolver` reads a
    SHARE, not a point count, so routing the species term cannot make a level-4 type compose differently
    from a level-1 one. Closing it means deciding what a species level grants — `species-progression`'s
    question by this module's own note
  - **S6 disproved rather than fixed** (the second carrier is live: 904 of 906 species carry magnitudes);
    **S8 struck** (premise false since 2026-09-13); **S5's premise corrected** (never had a caller)
  - The pattern, recorded for the next program: S5, S6 and S8 were all **stale premises** — each accurate
    when written, each overtaken by code. All three were found by opening the file rather than re-reading
    the register, which is `DESIGN-GATE`'s own first rule. This program's register was no exception to it
- [x] **T6.2 — Both registers closed** · S · deps: T6.1 — **done 2026-09-17**
  - Acceptance: populated as the work happened, not reconstructed. Schema and closure asserted, never counts
  - **Populated as the work happened, and the commit history is the proof** rather than a claim: `SR-15`
    landed with the substrate fix that surfaced it, `SR-16` with the capture relocation, `SR-17` with the
    CP4 assessment that found it. Each row cites the file and line that justified it
  - Both guards green (10/10): they assert the **six-field schema**, the **closed kind vocabulary**
    (`stub`/`dark`/`unowned`), non-weasel `waits-on`/`owner`, and that every cited file exists. Neither
    asserts a row count — the registers grow whenever work uncovers debt, which is a reading
  - Every Phase 4 and Phase 5 module has a **module statement**, including the ones that added nothing,
    each with its reason. "No rows" is a recorded decision; a module that stayed silent would be
    indistinguishable from one that forgot
- [x] **T6.3 — Full live proof** · M · deps: T6.1 — **PASSED 2026-09-17, 13/13**
  - Acceptance: RPG Server Debug scope; an effect-driven hit on a live lawn at 300z resolves through
    `CombatMath`; read back through the normal path; `vfx.tick` within budget
  - Note: a response body alone is never proof. The 2026-09-13 incident was a probe that returned
    `ok:true` end to end for a feature that was broken
  - **Ran for real, against current code.** Server republished (the running one was a 07:14 build that
    predated T4.5/T4.6 — a proof against it would have tested the wrong binary), restarted via
    `Start-Process`, injector reconnected (`injectorConnected: true`), live board entered through
    `POST /api/debug/lawn/quick-start` (`targetPtr 1C6FAE28320`, plant + zombie in match)
  - `scripts/prove-overlay-combat.ps1 -TargetPtr 1C6FAE28320`: **11 PASS, 2 FAIL**
    - PASS C1-C10, C13 — element matchups both directions, miss, heal pass-through, flag-off
      pass-through, forced crit (`critMultiplierFinal=1.99330714907572`), full mitigation to zero
    - **FAIL C11** `overlay-heal-with-payload-scales-with-heal-power`: `healed=-10`, expected ~50
    - **FAIL C12** `overlay-heal-with-no-payload-still-reads-heal-power`: `healed=10`, expected ~50
  - **This is a REGRESSION against a recorded baseline, not a pre-existing gap.** The committed artifact
    `docs/research/effect-runtime/_prove-overlay-combat.json` (commit `1b674f5ec`) has C11 and C12 both
    `pass: true` at `healed=50`, 13/13 with zero failures. C11 returning **-10** means a heal was
    resolved as damage — a sign flip, not a magnitude drift
  - **Not attributable to this program on the evidence available**, and stated that carefully rather
    than as a clearance: `OverlayCombatMath.Finalize`/`FinalizeHeal` is the path, and its last commit is
    `e103db1e` (the floating-point-ban removal) — no commit in this program touches the heal path at all.
    Many sessions have landed since that baseline was captured
  - **Root cause found, and it is the exact defect class this whole program is about.**
    `DerivedStatRegistry.cs:212` records it: *"RETIRED 2026-09-02 — `combat.heal.power` was generalised
    into `resource.restore.{resource}`"*. `FinalizeHeal` reads `ResourceRestore("hp")`; the probe was
    still pinning `combat.heal.power`
  - **The old channel is still REGISTERED.** So pinning it succeeded, returned no error, and contributed
    nothing — a write that reports success and does nothing, which is the same silent-wrong-answer shape
    as X2's `""` element id. A retired-but-registered channel is a trap with no symptom
  - **The probe was stale, not the code.** Repointed to `resource.restore.hp`; C11 and C12 return
    `healed=50`, matching the committed baseline exactly
  - **Re-run on a fresh board: 13/13 PASS, exit 0.** The intermediate run that showed C10–C12 failing
    with *"ptr not found in debug.board-stats"* was the target zombie having died during the earlier
    attempts — a stale ptr, not a regression, and re-established via `lawn/quick-start` rather than
    assumed away
  - Evidence: element matchups both directions (C1–C3, C7–C9), miss, heal pass-through, flag-off
    pass-through, forced crit (`critMultiplierFinal=1.99330714907572`), heal scaling with and without a
    payload, and full mitigation resolving to zero with no chip floor and no exception — all against a
    live lawn, through the real dispatcher, read back through `debug.board-stats` rather than from the
    call's own response body
- [x] **T6.4 — Hand-off** · S · deps: T6.2, T6.3 — **done 2026-09-17**
  - Acceptance: the stub register hands its plan to the next program; the FE register hands off to the FE
    program; `docs/architecture/decisions.md` records anything this program locked
  - **Stub register**: a hand-off table naming the owning program for every row — `party-dungeon`
    (`SR-01`..`SR-11`, `SR-16`), `achievement-title` (`SR-12`), `species-gear-chain` (`SR-13`),
    `aura-skill` (`SR-14`), `drop-volume` (`SR-15`), `death-and-injury` (`SR-17`). **The rows ARE the
    plan**: a next program starts from them rather than re-running the investigation that produced them
  - `SR-17` is flagged as the one to read first, because its shape is the least obvious — it is blocked
    on a **capture signal**, not a call site, and adding a settlement call would not close it
  - **FE register**: handed to the FE program. Every row tracked, none fixed — which is what X4 says, so
    that is the correct outcome rather than an incomplete one. `FE-01` flagged as the **corrected** X4:
    the original entry was numeric, the real defect structural
  - **`decisions.md`**: the "Battle engine is the SSOT for every battle mode" row ended *"Ruled
    2026-09-16; no remediation built."* It now records what was built, and — more usefully — the three
    entries that did **not** close as written (S7 open, S6 disproved, S8 struck), each with its reason,
    plus the stale-premise pattern behind S5/S6/S8
  - Both register guards green (10/10)

### ⚠️ CP6 — four of five met (assessed 2026-09-17)

- [x] **All 27 entries dispositioned** — T6.1's coverage audit. 24 fixed, **S8 struck**, **S6 disproved
  and its deletion refused**, **S7 open and reassigned** to `species-progression` with the structural
  reason recorded. D11 stays reassigned, X4 tracked, D13 retracted. Every entry has a disposition and a
  reason; none is silently carried
- [x] **Guard and verification boundaries in CI** — G1/G2/G3 (Phase 1). `FileMove.Tests` wired at
  introduction rather than left for `CiWiringGuardTests`; CI runs thirteen C# test projects
- [x] **Both registers populated and handed off** — T6.2/T6.4. Populated as the work happened (the commit
  history shows it), handed to six named owning programs, both guards green at 10/10
- [x] **Live proof passed** — T6.3, **13/13**, real lawn, current binary, read back through
  `debug.board-stats`. The two failures on the first run were a probe pinning `combat.heal.power`,
  retired into `resource.restore.hp` on 2026-09-02 and **still registered**, so the write succeeded and
  did nothing
- [x] **Twelve CI projects green, all guards green, `deploy-play.ps1` completes** — **ALL THREE MET
  2026-09-17.** The third was blocked by a running game, not by code; the owner closed it and the run
  completed: **exit 0**, every guard OK, MelonLoader 3.9 injector *Build succeeded* into the real Mods
  folder, freshness check OK (deployed artifacts match their source trees), FE synced, seed imported.
  `CLASS-SYSTEM GUARD FAILED` appears in the log and is the known permanent G3 finding (decision 12)
  that `deploy-play.ps1` itself tolerates and continues past. The server DLL publish was skipped by the
  script's own rule (the running server locks its own DLLs) — that path was separately proven clean by
  publishing to a scratch directory earlier the same day.
  - **Projects green: MET.** Thirteen, all measured today — see CP4's clause for the full table and for
    the two flakes that had to be root-caused first
  - **Guards green: MET.** Guard 384/384 plus all seven boundary scripts OK, re-run after the last
    change. `guard-class-system.py` reports its two known G3 lines (decision 12, permanent by design)
    and `deploy-play.ps1` itself tolerates exactly those and continues
  - **`deploy-play.ps1` completes: NOT RE-EVIDENCED ON CURRENT HEAD.** It completed earlier in this
    session (exit 0, injector deployed, game launched). Re-running it now fails, and the failure is
    environmental rather than a code state: `error MSB3027 ... Could not copy
    "FusionRpg.Contracts.dll" ... The file is locked by: "PlantsVsZombiesRH.exe (68176)"` — the game
    launched by that earlier run is still holding the deployed DLL. Every guard in the run passed before
    it reached that copy. **Closing the owner's running game is the owner's call, so this is reported
    rather than forced**, and the clause stays unticked rather than claiming a pass from the older run
  - **Every stage EXCEPT that one write is verified on current HEAD (2026-09-17).** "Blocked by a file
    lock" and "the code does not build" are different claims, and the first was asserted without
    separating them. Separated by redirecting the build away from the locked folder:
    - **MelonLoader 3.9 injector compiles clean** — `dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader.39
      -c Release -p:OutputPath=<scratch>`: *Build succeeded*, no errors, no MSB3026 retries. The project
      defaults `OutputPath` to `$(MlGameDir)\Mods\`, which is the only reason the normal build writes
      into a directory the running game holds
    - **Server publishes clean** — `dotnet publish gk-core/src/FusionRpg.Server -c Release -o <scratch>`: exit 0,
      `FusionRpg.Server.exe` produced
    - **All seven boundary guards OK**, and `guard-class-system.py` reports only its two known
      permanent G3 lines (decision 12), which `deploy-play.ps1` itself tolerates and continues past
    - So the remaining gap is exactly one `Copy` into the game pack's own `Mods\` folder. Nothing about current HEAD
      is known to be undeployable; the clause is unticked because the run itself has not completed, not
      because anything failed to build

**CP6 is not met, and the program is therefore not done — but what remains changed on 2026-09-17.**
The intermittent test failure is gone: it was two independent flakes, each reproduced deterministically
and fixed (`4951d773`, `aa3f2bb7`). What is left is no longer a mystery and is no longer this program's
to close:

| Remaining | Why it is not closable here |
|---|---|
| `deploy-play.ps1` on current HEAD | Blocked by the owner's running game holding the deployed DLL. Environmental; needs the game closed |
| **S7** (T4.4) | **Owner-deferred**, not stalled — the owner specified the species level-up grants and ruled it a later sub-program, recorded in `species-progression-ideal.md` |
| `SR-17` + `SR-18` | One missing vanilla-PvZ capture signal, owned by the capture/injector surface this program does not touch. Two CP4 clauses, two register rows, one root |
| `ProvePredictor` actions+status | A drift from `class-system` P4.6's recorded 9.146e-5, measured and attributed; proven NOT caused by this program's own reference change |
| `vfx.tick` budget | `vfx-v2`'s F8, reopened with this program's measurement |

Every one is written down with its evidence and a named owner rather than rounded off.
