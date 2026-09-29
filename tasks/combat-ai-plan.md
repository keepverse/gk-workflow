# Implementation plan: `combat-ai`

**Map:** [../docs/architecture/combat-ai-map.md](../docs/architecture/combat-ai-map.md) ·
**Ideal:** [../docs/architecture/combat-ai-ideal.md](../docs/architecture/combat-ai-ideal.md) (revision 3) ·
**Specs:** `docs/architecture/combat-ai/spec-<module-id>.md` (20 modules) ·
**Tasks:** [combat-ai-todo.md](combat-ai-todo.md) ·
**Handoff:** [combat-ai-handoff.md](combat-ai-handoff.md) (read this first if you are picking the program up) ·
**Evidence:** [../docs/research/combat-ai/](../docs/research/combat-ai/) (S1–S5, AUDIT, REVIEW-A, REVIEW-B) ·
**Owner rulings:** ideal §10 D1–D6, and
[backlog-clean-up/rulings-2026-09-20.md](../docs/architecture/backlog-clean-up/rulings-2026-09-20.md)
D2 (lawn combat stays on), D7 (orders: uniques only in v1), D8 (accept the idle-reward drift).

**Status:** plan written 2026-09-20. Not started. Prefix `CAI`.

**Parent:** `backlog-clean-up` map module 12. This plan discharges task
[BCU2.9a](backlog-clean-up-todo.md). `backlog-clean-up` owns no build task of this program; it owned
taking it through `/idea` → map → specs, which is done.

---

## Overview

`combat-ai` gives every place that resolves a fight — battle, expedition, siege, the delve and the
lawn — one AI core and one profile per `place × role`. Today there are four separate deciders: siege's
scorer, the delve's raid router, the battle stub, and no lawn decider at all. The specs generalise
siege's shipped scorer into `Core/Actions/Ai/`, put its numbers in `gk-core/data/tuning/combat-ai.v1.json`,
and then wire each place to it.

The plan's shape follows from one property: **almost every task is byte-identical by design.** Only
three tasks are allowed to move a committed golden, and only one of them re-blesses a hash. Everything
else proves it moved nothing. That is why the waves are ordered the way they are — the single
behavioural switch (`CAI3.6`) lands last in wave 3, after the balance twin and the replay stamp exist
to describe it.

## Coverage — every spec has at least one task

| Wave | Module (map #) | Spec | Tasks |
|---|---|---|---|
| 1 | `core-scorer` (1) | [spec-core-scorer](../docs/architecture/combat-ai/spec-core-scorer.md) | CAI1.1–1.5 |
| 1 | `profile-schema` (2) | [spec-profile-schema](../docs/architecture/combat-ai/spec-profile-schema.md) | CAI1.6–1.8 |
| 1 | `ai-tiers-personality` (3) | [spec-ai-tiers-personality](../docs/architecture/combat-ai/spec-ai-tiers-personality.md) | CAI1.9 |
| 1 | `intent-router` (4) | [spec-intent-router](../docs/architecture/combat-ai/spec-intent-router.md) | CAI1.10–1.11 |
| 1 | `resolvable-here` (5) | [spec-resolvable-here](../docs/architecture/combat-ai/spec-resolvable-here.md) | CAI1.12 |
| 1 | `aggression-tier-map` (6) | [spec-aggression-tier-map](../docs/architecture/combat-ai/spec-aggression-tier-map.md) | CAI1.13 |
| 1 | `decision-perf` (7) | [spec-decision-perf](../docs/architecture/combat-ai/spec-decision-perf.md) | CAI1.14 |
| 2 | `replay-identity` (8) | [spec-replay-identity](../docs/architecture/combat-ai/spec-replay-identity.md) | CAI2.1–2.2 |
| 2 | `action-schedule-twin` (9) | [spec-action-schedule-twin](../docs/architecture/combat-ai/spec-action-schedule-twin.md) | CAI2.3 |
| 2 | `decision-inspector` (10) | [spec-decision-inspector](../docs/architecture/combat-ai/spec-decision-inspector.md) | CAI2.4–2.5 |
| 3 | `stance-wiring` (11) | [spec-stance-wiring](../docs/architecture/combat-ai/spec-stance-wiring.md) | CAI3.1 |
| 3 | `siege-loadout-wiring` (12) | [spec-siege-loadout-wiring](../docs/architecture/combat-ai/spec-siege-loadout-wiring.md) | CAI3.2–3.3 |
| 3 | `delve-automated-wiring` (13) | [spec-delve-automated-wiring](../docs/architecture/combat-ai/spec-delve-automated-wiring.md) | CAI3.4–3.5 |
| 3 | `auto-policy-switch` (14) | [spec-auto-policy-switch](../docs/architecture/combat-ai/spec-auto-policy-switch.md) | CAI3.6 |
| 4 | `lawn-actor-view` (15) | [spec-lawn-actor-view](../docs/architecture/combat-ai/spec-lawn-actor-view.md) | CAI4.1 |
| 4 | `lawn-held-actions` (16) | [spec-lawn-held-actions](../docs/architecture/combat-ai/spec-lawn-held-actions.md) | CAI4.2–4.3 |
| 4 | `lawn-cost-authority` (17) | [spec-lawn-cost-authority](../docs/architecture/combat-ai/spec-lawn-cost-authority.md) | CAI4.4–4.5 |
| 4 | `lawn-cast-activation` (18) | [spec-lawn-cast-activation](../docs/architecture/combat-ai/spec-lawn-cast-activation.md) | CAI4.6 |
| 4 | `lawn-cast-trigger` (19) | [spec-lawn-cast-trigger](../docs/architecture/combat-ai/spec-lawn-cast-trigger.md) | CAI4.7–4.8 |
| 4 | `commander-direct-orders` (20) | [spec-commander-direct-orders](../docs/architecture/combat-ai/spec-commander-direct-orders.md) | CAI4.9 |
| 1 | — (index propagation) | DESIGN-GATE §1, ideal §4.1 | CAI1.15 |
| 5 | — (proof and the default flip) | ideal §9, spec-lawn-cast-trigger criterion 9 | CAI5.1–5.3 |

The three **cross-program** specs the map lists (`creature-lawn-deploy/spec-unique-deploy-cap.md`,
`lawn-tuning-profile/spec-lawn-combat-baseline.md`, `spec-zombie-power-source.md`) are **not** tasks
here. They are built under the lawn plan (`backlog-clean-up` BCU2.4). This plan names them only as
edges.

## Architecture decisions (from the map and the ideal; not re-litigated)

1. **The engine resolves, the AI decides.** Everything is on the deciding side of
   `IIntentSource.TryDeclare`. The only engine-seam edits are the ones a spec names as a wiring gap,
   and each is byte-identical.
2. **One scorer, several policies.** `AiScoring` is generalised into `Core/Actions/Ai/` and is the only
   scorer. A second scorer anywhere is a SOLID defect, not a variant.
3. **Tiers are actor class, never difficulty** (D2, D6). `smart` = unique, `performance` = general.
   Nothing in tier resolution takes a difficulty input, and a test asserts the signature.
4. **Determinism.** A decision is a function of `(setup, seed, human trace, profile version,
   BattleEnvironment.Stamp)`. Randomness comes only from `SeededRng.DeriveStream`. No clock read on a
   decision path.
5. **The lawn is the Hot loop.** Logic in Core, the injector adapts; no server await, dead-ptr skip,
   grant withdrawal before ptr reuse, re-entry depth 0.
6. **Repo hard rules apply unchanged:** RPG layer only; one ActorHub compose; tunables published
   `v{n+1}` through `gk-core/tools/tuning/publish.py` and never hand-edited; structural limits carry a comment;
   `long` + `checked` for integer magnitudes; tests assert contracts and closed vocabularies, never
   population counts or generated text; store tests in memory; a debug API never fabricates a result.

## Dependency graph

```
W1  core-scorer (1.1→1.5) ─┬─► profile-schema (1.6→1.8) ─► ai-tiers-personality (1.9)
                           ├─► intent-router (1.10→1.11) ─► decision-perf (1.14)
                           ├─► resolvable-here (1.12)
                           └─► aggression-tier-map (1.13)
W2  replay-identity (2.1–2.2) · action-schedule-twin (2.3) · decision-inspector (2.4–2.5)
W3  stance-wiring (3.1) · siege-loadout-wiring (3.2–3.3) · delve-automated-wiring (3.4–3.5)
        └──────────────── all three land before ────────────────► auto-policy-switch (3.6)
W4  lawn-actor-view (4.1)   lawn-held-actions (4.2–4.3) ─► lawn-cost-authority (4.4–4.5)
                                                          ─► lawn-cast-activation (4.6)
        └───────────────────────────────────────────────► lawn-cast-trigger (4.7–4.8) ─► orders (4.9)
W5  300-zombie A/B (5.1) ─► owner packet (5.2) ─► default-on flip (5.3)
```

## Suggested order and parallel lanes (suggested, not enforced)

| Lane | Tasks | Notes |
|---|---|---|
| α core | CAI1.1–1.5 → 1.6–1.8 → 1.9 | One writer. Every task touches `Core/Actions/Ai/` and siege's consumer. |
| β router | CAI1.10–1.11 → 1.14 | Starts after CAI1.4. Touches `Battle/BasicAttack.cs`, `TimelineDispatch.cs`, siege's intent source. |
| γ filter | CAI1.12, CAI1.13 | Disjoint from α and β after CAI1.1. `BattleEffects.cs` and `CandidateScorer.cs` respectively. |
| δ identity | CAI2.1–2.3 | After CAI1.8. Data + Server + Balance; disjoint from wave 1's files. |
| ε places | CAI3.1, CAI3.2–3.3, CAI3.4–3.5 | Three independent lanes after wave 1. They converge on CAI3.6, which is one writer. |
| ζ lawn | CAI4.1, CAI4.2–4.9 | After wave 1 and the lawn plan's `lawn-perf-budget.v1`. Disjoint from ε. |

Waves 3 and 4 touch disjoint files and can run in parallel once wave 1 lands (map §2).

## Hard edges this plan honours

- **H1 — one golden cause per commit.** Exactly three tasks are permitted to move a committed golden
  hash: `CAI1.5` (siege target choice, predicted-delta writeup, no re-bless of battle hashes),
  `CAI1.11` (siege behaviour, its own commit and note) and `CAI3.6` (the four battle hashes, the one
  re-bless of this program). **Every other task's acceptance is that no golden moved**, and the suite
  is run and the result stated — an unrun byte-identity claim is an opinion (DESIGN-GATE §3 rule 4).
- **H7 — a publish switches its readers in the same commit.** `CAI1.8` (ten siege keys →
  `combat-ai.v1.json` + `siege.v2.json`) and `CAI3.1` (`siege.v3.json`) each publish and switch in one
  commit.
- **E1 — no lawn build task starts before `backlog-clean-up` BCU0.1** (`lawn-signal-ownership`) has
  landed in the documents. That is wave 4's entry condition, and it is cheap to satisfy.
- **E2 — the unique deploy cap lands before the lawn AI ships default-on**, not before it is built.
  The cap is the lawn plan's (`creature-lawn-deploy/spec-unique-deploy-cap.md`); `CAI5.3` waits on it.
- **RulesetVersion moves once.** 5 → 6 happens in `CAI3.6` and nowhere else. Every other task states
  that it stays 5.

## Corrections carried into this plan (found while planning; the specs are right about everything else)

These are the three places where two specs disagreed, or where a spec header contradicted its own
body. Each is resolved here so a builder does not have to rediscover it.

1. **`PerfSection` index collision.** `spec-decision-perf.md` claims `AiDecide = 25` with
   `SectionCount` 25 → 26, and `spec-lawn-cast-trigger.md` claims `LawnAiDecide = 25` with the same
   bump. Both cannot be 25: `PerfProbe.cs:36` ends the enum at `LawnMoveDrain = 24` and
   `PerfProbe.cs:51` reads `const int SectionCount = 25` today, so 25 is one free slot, not two.
   **Resolution:** `decision-perf` (CAI1.14) takes `AiDecide = 25`, `SectionCount = 26`;
   `lawn-cast-trigger` (CAI4.7) takes `LawnAiDecide = 26`, `SectionCount = 27`, and its test 11 and
   success criterion 3 read 27 rather than 26. Both are turn-mode and lawn sections of different
   loops, so both exist; only the numbers move.
2. **`AiTriggerBlock` has three fields from the start.** `spec-profile-schema.md` §2 reserved
   `PerFrameBudget` and `TokenPool`; `spec-lawn-cast-trigger.md` then classified both as code
   `const`s and dropped them. **Resolution:** `CAI1.6` declares the record with `SwingsN`, `TicksT`
   and `PostCastLockL` only. Nothing is added and later removed — a schema field for a value that
   lives in code is the dead-config shape the ideal §8 forbids.
3. **`lawn-held-actions` does not depend on `profile-schema`.** Its spec header names module 2, but
   its own Tunables section reads *"None"* and it touches no tuning file; the map already carries the
   correction (`combat-ai-map.md:74`, *"corrected: it reads no profile"*). **Resolution:** CAI4.2 has
   no dependency on CAI1.6/1.8. It still lands after wave 1 for lane reasons, not for a data reason.

4. **The ideal still names the wrong clock in one place.** The map row was corrected
   (`combat-ai-map.md:80`), but `combat-ai-ideal.md:119` still calls `AdvancedEffectClock` the lawn
   clock host for triggers. That clock is wall-clock-seeded for status expiry
   (`EffectRuntime.cs:42,133`); the decision clock is the kernel tick base. A correction that landed in
   one document and not its sibling **has not landed** (DESIGN-GATE's propagation rule).
   **Resolution:** `CAI1.15` carries it, together with the DESIGN-GATE §1 row this program owes.

A fifth item is a sequencing hazard rather than a contradiction: **`InjectorEntityRegistry.Remove`
and `Clear` (`:129-146`, `:148-157`) are edited by four modules** — the inspector's lawn ring (10),
held actions (16), the trigger's per-actor state (19) and the order queue (20). Each adds its own drop
call to the same two methods. They are sequenced in wave order in the todo, and each task's acceptance
names the drops already present so a later one cannot delete an earlier one.

## Decisions inherited from the specs' open questions (adopted, not re-opened)

Every spec's "Open questions" section was read while planning. Two were owner-shaped and are answered
(rulings D7 and D8). The rest carry a recommended default, and a build task inherits it rather than
re-deciding it. They are listed here because a default that lives only inside a spec's open-questions
section is a default the builder will re-litigate.

| Decision | Adopted | Task |
|---|---|---|
| `StubIntentSource` survives as a class, reimplemented over the core | yes — it is named at two production fallback sites, and touching those is module 4's cause | CAI1.1 / CAI1.10 |
| `AiRowCondition` is a closed enum for v1, not `ICompiledPredicate` | yes, **with a stated revisit trigger: if it reaches eight members, fold the fact half into the existing predicate engine** | CAI1.6 |
| `AiRole` is `Default` until a role source exists | yes. A role source, when it comes, is a **creature-program concept the AI reads** — never an AI-local classification | CAI1.6 |
| Who supplies `AiActorClassOf` | each wiring task supplies it in its own commit; a shared resolver would need a roster read inside Core, which the DAL boundary forbids | CAI3.3, CAI3.5, CAI3.6, CAI4.8 |
| A general's personality is stable within an encounter and re-drawn per encounter | yes — it falls out of the seed the encounter already has. Flagged rather than asserted: the expedition resolver was not opened | CAI1.9 |
| The zero-allocation tests stay in `FusionRpg.Core.Tests` | yes, matching the two shipped precedents. **If one ever flakes, the fix is to name the allocating frame, never to raise the budget** | CAI1.14 |
| The candidate cap reads the view's order | yes, byte-identical. Ordering by a cheap pre-score would be better AI and a golden-moving change — it is a profile question, its own cause, never inside a perf commit | CAI1.14 |
| The dominance matrix stays economy-free | yes. An economy-carrying variant is a named follow-up, not this program's | CAI2.3, CAI3.6 |
| The analytic twin models turn-mode profiles only | yes — the lawn is real-time and has no rounds; inventing a tick mapping would model a schedule the lawn does not run | CAI2.3 |
| `ContentHashStamp.TableDigests` is reused as-is | yes. A `PartDigests` rename is a cross-module cosmetic change for later, and a forked type is the SOLID defect the module exists to avoid | CAI2.1 |
| A host keeps every published `combat-ai.v*.json` loaded | yes — a refused replay of a real expedition collect is a player-visible failure, and disk is not the constraint | CAI2.2 |
| The basic-attack elemental rider fires on cast damage | yes (option a). Suppressing it would silently disable every on-hit proc for cast damage — a larger behaviour change than the one avoided | CAI4.6 |
| The lawn decision ring is readable from the injector debug surface only | yes. A server route adds no capability and would relay anyway | CAI2.5 |
| The turn-mode sink carries the formatted line only | yes — a second structured ring is the same ring twice | CAI2.4 |
| `ally-downed` stays a rank-1 row that falls through | yes. A revive is a **supply** today, and routing a supply through `IIntentSource` would be a second decision path | CAI3.4 |
| The swing counter accumulates during the post-cast lock | yes — freezing it makes `L` a hidden multiplier on `N`. A one-line behaviour switch, deliberately **not** a tunable | CAI4.7 |
| The lawn's unknown-id cost floor is 1 | yes, byte-identical to today; refusing would make the basic attack unchargeable | CAI4.4 |
| A `Partial` resolvable verdict is reported, never score-penalised | yes. A penalty later is a profile weight reading the footprint's existing counts — no new mechanism | CAI1.12 |
| The siege effect-registration hand-off is a delegate | yes, matching `HubInputsFor`'s "Core declares a need, Data injects" idiom. A build-task call | CAI3.3 |
| No `EngineVersion` change with the ruleset bump | yes — the policy is not the engine. Stated in the writeup so the next reader does not wonder | CAI3.6 |
| No debug-surface route that issues an order | yes. An injector-side "order this ptr" entry could fabricate a subject — the 2026-09-13 shape. If one is ever wanted it adapter-wraps `POST /api/lawn/order/direct` | CAI4.9 |

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 1 | core-scorer, profile-schema, tiers, router, resolvable-here, aggression, perf | CAI1.1–1.14 | S–L | lanes α/β/γ after CAI1.1 |
| 2 | replay-identity, schedule twin, inspector | CAI2.1–2.5 | M–L | yes, after CAI1.8 |
| 3 | stance, siege loadout, delve, the switch | CAI3.1–3.6 | M–L | 3.1 / 3.2–3.3 / 3.4–3.5 parallel; 3.6 alone |
| 4 | the lawn | CAI4.1–4.9 | S–L | 4.1 parallel to 4.2; the rest is a chain |
| 5 | proof and the flip | CAI5.1–5.3 | M | no |

## Checkpoints (review points, not gates)

| # | Checkpoint | Evidence |
|---|---|---|
| CP1 | **One core, no behaviour change.** `AiScoring` exists once, under `Core/Actions/Ai/`. `combat-ai.v1.json` is published and read by both hosts. Every siege suite passes unedited except the single permitted `EffectiveTier` throw assertion. `BattleGoldenTests` and `ExpeditionResolverTests` green and unblessed, apart from CAI1.5's and CAI1.11's stated siege causes. `audit-overflow.py --targets A3` and `audit-magic-numbers.py --summary` gain no row for `Actions/Ai/`. | quoted test output per task, commit hashes |
| CP2 | **A decision is identifiable and predictable.** Every logged match carries a profile stamp; a replay across a `v{n+1}` publish resolves under the pinned set and returns a byte-identical report. The analytic twin agrees with the real core policy. The inspector is compiled in, default off, and module 7's zero-allocation test is still green with it present. | `WebMatchProfilePinTests`, `ActionScheduleMatchesCorePolicyTests`, `DecisionAllocationTests` |
| CP3 | **The switch is made once, and described.** `RulesetVersion` is 6, exactly four hashes re-blessed exactly once, `predicted-delta-rulesetversion-6.md` exists with the measured expedition delta per tier, the dominance confirmation run recorded as unchanged, `ProvePredictor` under `1e-4`, and the full suite green (one of the three occasions AGENTS.md sanctions it). | the writeup, the ledger paragraph, full-suite output |
| CP4 | **The lawn casts, off by default.** A creature with a kit casts on its `N`-th swing or after `T` ticks, through the shared router and the existing Funnel → `EntityStatWriter` tail. Death and ptr reuse leave no stale counter, token, order or held set, in both orders. The feature ships default-off. | `LawnDecisionTriggerTests`, `LawnCastPlanTests`, `LawnOrderQueueTests`, live probe |
| CP5 | **The flip is an owner-facing change carrying numbers.** The 300-zombie A/B reports AI-on vs AI-off, `lawn.ai.decide`'s measured share sits inside `lawn-perf-budget.v1`, and the deploy cap is live. | A/B report, perf window, cap task in the lawn plan |

## Cross-program edges

- **`backlog-clean-up` BCU0.1 (`lawn-signal-ownership`)** — documents the `PUT /api/players/current`
  split. Wave 4 does not start before it lands. It edits documents only, so it is not a long wait.
- **The lawn plan (BCU2.4, prefix `LW`)** owns `gk-core/data/tuning/lawn-perf-budget.v1.json` and therefore
  `lawn.ai.decide`'s *share of the frame*. `CAI4.7` reads that share; it does not author it.
  `DecisionsPerFrame` (a count) is this program's code `const`; the share (a measured fraction) is the
  lawn plan's perf-domain tunable. Two different quantities, two owners.
- **`creature-lawn-deploy/spec-unique-deploy-cap.md`** (D6: five uniques per side) is implemented in
  the lawn plan. `CAI5.3` waits on it; nothing earlier does.
- **`lawn-tuning-profile/spec-lawn-combat-baseline.md`** — lawn actors sit at a 0.5 hit coin-flip until
  the shipped `BattleBaselineSubsystem` is registered on the lawn Hub. Wave 4 is buildable without it,
  but `CAI5.1`'s A/B is only meaningful with it, so the A/B names it as a precondition.
- **`action-skill-tiers/spec-holder-rung-pricing.md`** — `CAI4.4` prices at `EffectiveRungOf`. Contract
  4 is shipped (`BattleRunState.cs:672-679`); that spec's status line still says "not built" and is a
  convergence-owned document this program does not edit (`backlog-clean-up-todo.md` cross-program
  notes).
- **`summoner-convergence`** — no file of its 11 programs is edited here. `SP6.6` and `SE4.31`–`SE4.36`
  gate the lawn plan, not this one.

## Tuning publishes

| Publish | Task | Contents |
|---|---|---|
| `gk-core/data/tuning/combat-ai.v1.json` (new) | CAI1.8 | Authored, not published — creating v1 *is* the authoring act. Ten migrated siege values, the identity defaults, the required `*/default` root and the required top-level `router` block. |
| `gk-core/data/tuning/siege.v2.json` | CAI1.8 | One `publish.py --remove-key` invocation removing ten keys. One invocation, one version — never `v2..v11`. |
| `gk-core/data/tuning/siege.v3.json` | CAI3.1 | One invocation removing `ai.stanceDefault` and `ai.autoResolveHandicapMilli`. |
| `combat-ai.v2.json` | CAI3.5 | The four `delve/*` profile rows, every seeded number marked `UNMEASURED`. |
| `combat-ai.v3.json` | CAI4.7 | The lawn section: `swingsPerDecision` 7, `ticksPerDecision` 50, `postCastLockTicks` 10, `offsetStream`. |
| `combat-ai.v4.json` | CAI4.9 | `lawn.order.lifetimeTicks` 80, `lawn.order.queueCap` 16. |

`publish.py` gains exactly one verb, `--remove-key`, built in `CAI1.7` and called by `CAI1.8` and
`CAI3.1`. It refuses an unresolvable path, requires `--reason`, is repeatable within one invocation,
and one invocation writes exactly one `v{n+1}`.

Version numbers after `v1` are the order the tasks land in. A task that slips re-numbers the ones after
it; the rule is one publish per task, never a hand edit.

## Session boundary

`tasks/sessions/backlog-clean-up-20260920.json` is **documents only** ("no source code changes"). It
covers writing this plan and nothing in it. **Every build task here runs under its own session record**
(`tasks/sessions/combat-ai-<date>.json`, one per lane), whose `paths` fence is that task's files. Run
`python scripts/session-boundary-check.py` before the first edit of each lane.

## Verification

Per task: `.\scripts\verify-change.ps1 -Paths <every added/modified path> -Session <that lane's id>`,
plus the guards each spec names. The full suite (`test-fast.ps1 -AllDefault`) runs at exactly three
points, which are the three AGENTS.md sanctions: `CAI3.6` (the switch), `CAI4.9` (the last wave-4
feature, crossing Core/Server/Injector/web) and immediately before the `CAI5.1` live probe.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| The siege migration is claimed byte-identical and is not | `CAI1.1`'s acceptance is the three siege suites passing **unedited** plus `Score_matches_the_shipped_siege_weights_term_for_term`; the cap move has its own identity proof (`Cap_before_work_selects_the_same_candidate_as_cap_after_work`) |
| A golden moves under an unrelated task, and gets re-blessed to make it green | Only CAI3.6 re-blesses. Everywhere else a moved hash is a **defect**, stated in the task. A re-bless outside CAI3.6 is a stop-and-report |
| The dominance baseline is assumed to move and a real move is missed | `DominanceGuard.cs:64` and `TerminationGuard.cs:100` call the economy-free `Predictor.Predict(a, b)`, so no baseline should move. CAI3.6 runs the confirmation and **stops and reports** if one does |
| Wave 4 lands a per-frame cost nobody measured | `lawn.ai.decide` is its own `PerfSection` from CAI4.7, outside `KernelDriveHost`'s budget; CAI5.1 measures before CAI5.3 flips anything |
| Four modules edit the same two `InjectorEntityRegistry` methods and one deletes another's drop | Wave-ordered, and each task's acceptance lists the drops that must already be present |
| A tuning publish lands without its reader | Both publishes are single tasks whose acceptance is the reader switch in the same commit (H7) |
| Two lanes both edit `BattleRunState.cs` | It is touched by CAI1.8, CAI1.10, CAI1.12, CAI3.1, CAI3.5 and CAI4.4. Lane ε and ζ start after wave 1, and the todo names the seam each one owns |

## Out of scope

Difficulty (its own future sub-program, D2); vanilla PvZ unit control (deferred, D6); player-editable
AI (D4 is inspect-only); combo-skill content; strategic and world AI; balance values (every seed here
is identity or `UNMEASURED`). Orders for general creatures are out by ruling D7 — the per-ptr spawn
generation counter is a named follow-up, revisited only if players ask.
