# Battle engine — the SSOT

**Status: binding law, 2026-09-16 (owner ruling).** This page states what the battle engine *is*, what it
owns, and what every battle mode owes it. It is the gate a feature that touches battle logic must pass.

Companion pages: [actor-hub-ssot.md](actor-hub-ssot.md) (one compose for an actor's numbers) ·
[software-architecture.md](software-architecture.md) (the three FSMs, the control loops) ·
[decisions.md](decisions.md) (the row this page expands).

---

## 1. The law

The owner's ruling, in their own words, is the law and is quoted rather than paraphrased:

> *"This repo follow SOLID so anything violate it is defect. The decision that violate solid is defect
> too. What is battle engine? A battle resolver that build on the top of atom effect engine and fsm. What
> is it do? Solve every battle logic. Any feature that change battle mechanism is an extension of battle
> engine and must be build on the top of battle engine. Every battle mode in the game share ssot battle
> engine logic. Delve, siege, world assault, lawn are share battle engine logic."*

Stated as rules:

1. **The battle engine is a battle resolver built on top of the atom effect engine and the FSM.** It is
   not a mode. It is not "the web match". It is the layer every mode resolves through.
2. **It solves every battle logic.** A battle question has exactly one answer, in one place.
3. **A feature that changes a battle mechanism is an extension of the battle engine**, and is built on
   top of it — never beside it, never inside a mode.
4. **Every battle mode shares the SSOT battle engine logic: delve, siege, world assault, lawn.** A mode
   is a *driver*, not an *owner*.
5. **The battle engine is deterministic** (owner, 2026-09-16: *"our battle engine is a determinic
   engine"*). Same setup, same seed, same platform produces a byte-identical report — `BattleEngine`'s own
   contract already says *"No I/O, no clock, no ambient state."* **This is the defining property, not a
   nice-to-have**, and §3c derives the engine's boundary from it: anything non-deterministic is not the
   engine, and enters as an input through a named seam.
6. **SOLID is binding, and a decision that locks a SOLID violation is itself a defect** — overturn and
   fix. Owner confirmation, an ADR, or a prior spec does not convert a violation into intentional design.
   This restates the standing rule in `CLAUDE.md`; it is repeated here because this page is where battle
   work will look.

**The failure this prevents**, stated as the wrong sentence and the right one:

- ❌ *"Siege needs a hit-chance estimate, so `SiegeHitChance` implements the sigmoid contest."*
- ✅ *"Hit chance is a battle mechanism. It has one implementation. Siege calls it."*

---

## 2. The one precision this law needs — loop versus mechanism

**Read this before applying rule 4, or it will collide with a locked invariant.**

`overlay-control-loops.md` §6.10 and §7 are locked: **no server round-trip on the hit path**, and **no
Server FSM may sit between `combat.hit` and FA\* apply.** The lawn is real-time and PvZ-driven; we observe
its events and contribute signed deltas afterwards. `BattleEngine.Resolve` is a pure, deterministic,
turn-ordered resolver: status ticks → initiative-ordered attacks → death cleanup → shield upkeep → round
end. **The lawn has no turns, and cannot be given any.**

So "every mode shares the battle engine" resolves into two statements, and only the second is negotiable
per mode:

| | **The mechanisms** | **The loop** |
|---|---|---|
| What it is | damage math, elements, status, shields, targeting, resources, procs, actions, derived stats | what decides *when* a mechanism is invoked, and in what order |
| Rule | **exactly one implementation, shared by every mode. No exceptions.** | mode-specific by necessity — a turn-based delve and a real-time lawn cannot share a scheduler |
| Today | mostly shared, with named defects in §4 | `BattleEngine` round loop (battle/delve/siege/web) vs the injector's event stream (lawn) |

**A mode may own its loop. A mode may never own a mechanism.** That is the operative form of the law, and
every defect in §4 is a mode owning a mechanism.

#### The clock is a mechanism, not a loop — owner ruling 2026-09-16

The first cut of this section said a mode owns "its loop", which was too loose. The owner sharpened it:

> *"Shared, loop per mode, because we have realtime battle, synchronous turn base, hybrid turn base,
> cannot control lawn time clock. So because we have many mode, they need engine build above battle
> engine to resolve time clock. But we need ship unify one, so whatever they change, the rule is only
> one — and we already ship that virtual time clock for all mode. Only we cannot control lawn run; we
> work around with attack capture, but the tick still belong battle engine unify time clock. That mean
> damage deal by DoT will be calculate by battle engine timeclock module, same as status."*

Three things follow, and they tighten the law rather than loosening it:

1. **A mode's scheduler is built ABOVE the battle engine, not beside it.** It is an adapter that decides
   when to advance; it is not a second implementation of what advancing means.
2. **The clock itself is a battle-engine module, unified across every mode.** Four modes exist —
   real-time battle, synchronous turn-based, hybrid turn-based, and the lawn — and they differ in *how
   time advances*, never in *what a tick means*.
3. **The lawn is not an exception to the clock, only to its control.** PvZ owns the wall clock and we
   cannot drive it, so we observe hits through capture — but **a DoT pulse and a status expiry are still
   computed by the engine's clock module**, not by whatever PvZ happened to do.

**This is already the shipped abstraction, and it is worth naming because it is exactly right.**
`Battle/Timeline/SimulationClock.cs` declares `ITimeAdvance` with a doc comment that could have been
written for this ruling — *"How simulated time moves. The two discrete-event-simulation mechanisms, and
the only thing that distinguishes a turn-based battle from a real-time one."* It has exactly two
implementations: `NextEventAdvance` (jump to the next scheduled event — turn-based) and
`FixedIncrementAdvance` (fixed step — real-time). **The advance policy is the per-mode part; the clock is
the shared part.** That is the loop/mechanism split, already expressed in code, for time.

⚠️ What is *not* unified is which time base the lawn actually reads — see **D15** in §4.

**VFX is the one place the owner accepts drift** (*"only thing that maybe inconsistent is vfx, but I
think we can sync it or we don't really need"*). That is consistent with §3c: VFX is presentation, not
the engine, so a frame of skew changes no outcome.

**Determinism (rule 5) is what makes this split necessary rather than merely convenient.** The engine is a
pure function of its inputs. The lawn is the opposite by construction — PvZ owns its timing, we observe
past events and contribute deltas afterwards — so the lawn can never *be* the deterministic resolver. What
it can do, and must, is drive the **same pure mechanisms**, which return the same answers for the same
inputs whoever calls them. A deterministic core with a non-deterministic driver is the normal shape for
this; a second copy of the mechanism for the driver's convenience is the defect.

> ⚠️ **This distinction is my reading, not the owner's words.** It is the only reading I can find that
> satisfies rule 4 without breaking the locked hot-path invariant. If the owner means something stronger —
> that the lawn must literally resolve through `BattleEngine` — that is a much larger change and it needs
> `decisions.md` to overturn §6.10/§7 first. **Flagged for confirmation.**

---

## 3. The responsibility register

The owner's list, plus the gaps they invited me to find (*"I think that i have but maybe i gaps"*).
**This is a closed register: a battle mechanism not on this list does not have permission to exist yet.**

### 3a. Named by the owner

| # | Responsibility | SSOT today |
|---|---|---|
| 1 | Damage calculator | `OverlayCombatCalculator.Compute` — **one**, two call sites |
| 2 | Elemental system | `IElementHub` / `ElementHub.Default`, `ElementRingMatrix` |
| 3 | Status system | `StatusRuntime`, `StatusEffectBridge` |
| 4 | Shield | `ShieldRuntime` / `ShieldGate` |
| 5 | Targeting and area effect | `TargetResolver.Resolve` — genuinely shared |
| 6 | Resource resolve and consume | `LawnActorResourcePools`, `ResourcePoolState`, `CostLedger` |
| 7 | Proc and trigger condition (atom runtime scope) | `AtomRunner`, `EffectBag`, `AtomTriggers` |
| 8 | Action system | `ActionRunner`, `ActionEnvelope`, `CooldownLedger` |
| 9 | Injury and permanent death | **fragmented — see §4** |
| 10 | Equipment damage in battle | **does not exist — see §4** |
| 11 | All battle derived stats and their mechanisms | `ActorHub` compose + the 28 channel families |

### 3b. Additions — **accepted by the owner 2026-09-16**

Each is battle logic by the law's own test (*"a feature that changes a battle mechanism"*), and each was
forked or absent when the register was written. **The owner accepted all eight, so §3a and §3b together
are now the closed register** — a battle mechanism not on this list has no permission to exist.

| # | Proposed responsibility | Why it belongs | State today |
|---|---|---|---|
| 12 | **The unified virtual clock — initiative, turn order and scheduling** | It decides *when* every other mechanism fires. Per the owner's clock ruling in §2 this is emphatically the engine's: one clock module for every mode, with `ITimeAdvance` as the only per-mode part. A DoT pulse and a status expiry are computed here, on every board, including the lawn | `SimulationClock.cs` (`ITimeAdvance`, two policies) + `BattleEngine` round order; the lawn reads a second time base today — **D15** |
| 14 | **Movement and board position** | Range and reach gate targeting; a mechanism that changes what can be hit is battle logic | A9/A10 `TryMoveTowardNearestEnemy`, siege board — battle-only |
| 15 | **Death, cleanup and body state** | Distinct from permanent death: corpse, death-refusal charges, grant withdrawal on death | `ImmortalCharges`, `entity:{ptr}` withdrawal — different per mode |
| 16 | **Summon / spawn during battle** | Adds combatants mid-resolution; changes every other mechanism's input set | `spawn.entity` atom |
| 17 | **Kill attribution** | Who gets credit for a death. **This is exactly where empire species progression breaks** — see the species-progression audit | `CreatureProgressionSource` claim; correct on the lawn, absent elsewhere |
| 18 | **Retaliation / reflect** | A separate resolution step after mitigation, not part of the damage calculator | `CombatDamageDispatcher.TryReflect` — **lawn-only** |
| 19 | **Determinism and seeded RNG streams** | Not a feature — a *property* the law needs. A mode whose randomness is not seeded per stream cannot be replayed or proven | `SeededRng`, per-system streams; battle only |
| 20 | **Victory / defeat and settlement** | What the battle *meant* — who won, what persists, what is lost | Per mode today; delve has `ExtractionSettlement`, others differ |

### 3c. What the battle engine is NOT — the determinism boundary

**Owner correction, 2026-09-16:** *"battle AI is not battle engine, it is player control and AI system —
not a battle of battle engine."*

This is the sharpest boundary on the page, and rule 5 is why it holds. **The engine RESOLVES; it does not
DECIDE.** Deciding is non-deterministic — a player clicks, an AI policy weighs, a difficulty setting
changes its mind — and a deterministic engine cannot contain any of that. So every deciding system sits
**outside** the engine and hands it **data** through a named seam.

| | **Player control / AI system** | **Battle engine** |
|---|---|---|
| Answers | *"what does this actor try to do?"* | *"what happens when it does?"* |
| Nature | a policy — may change, may be interactive, may be re-tuned | deterministic — same inputs, byte-identical output |
| Examples | target choice, ability choice, hold vs advance, difficulty behaviour | hit roll, mitigation, status application, shield absorption, death |
| Seam | `IIntentSource.TryDeclare(actorKey, nowTick)` returns an `ActionIntent` | consumes that intent and resolves it |

**The seam already exists and is already correct.** `IIntentSource` is one method
(`Battle/Timeline/IntentSource.cs:29-37`) with five implementations —
`StubIntentSource` (the default policy), `SiegeAiIntentSource`, `InteractiveIntentSource` (a real player),
`RaidIntentSource` (delve), and a replay trace source. `BattleEngine` takes one; it never constructs an AI.
`DeclareBasicAttack` picks `intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)`.

**This is also the test for replay.** A recorded battle replays by substituting a trace source for the live
AI and getting an identical report. That only works because deciding was never inside the engine. If a
mechanism cannot be replayed from a recorded intent stream, something non-deterministic leaked in.

**Consequences for the register.** Every responsibility in §3 splits the same way, and only the right half
is the engine's:

| Mechanism | Deciding (control/AI — **not** the engine) | Resolving (**the engine**) |
|---|---|---|
| Targeting | which target to pick | whether the pick is legal, who is in the area |
| Movement | where to move | whether the move is legal, what it costs, what it changes |
| Actions | which action to use | cost, cooldown, effect, outcome |
| Summon | whether to summon | what spawns, with what stats, when it acts |

So **"where to move" is AI and "whether that move is legal" is engine** — and a feature that changes the
second is a battle-engine extension even when it arrived as an AI feature.

**Other systems that are adjacent but not the engine**, for the same reason: presentation (VFX, HUD),
persistence, matchmaking/encounter selection, loot and reward generation, and progression *credit* —
though **kill attribution itself (responsibility 17) is the engine's**, because who dealt the fatal blow is
a deterministic fact the engine already knows, and only what is *done* with that fact lives elsewhere.

---

## 4. Conformance audit — 2026-09-16

Measured against the two audits committed the same day
([battle-derived-wire](../research/battle-derived-wire-audit-2026-09-16.md),
[combat-math-dedup](../research/combat-math-dedup-audit-2026-09-16.md)) and verified against code.

**Under the old framing these were "wiring gaps". Under this law most are SOLID defects**, because the
law names a single owner for each mechanism and the code has more than one, or none.

### Conforming — say so plainly

| Mechanism | Evidence |
|---|---|
| **Damage calculator** | `OverlayCombatCalculator` is the only resolver repo-wide; exactly two `Compute` call sites (`BasicAttack.cs:364`, `OverlayCombatMath.cs:62`). `BattleStatComposer` was deleted 2026-09-13 |
| **Mitigation primitives** | `PierceFactor`, `AmpFactor`, `DivisiveMitigation`, `CapAvoidanceBand`, `ResolveBand`, `CombatProbability.Sigmoid` — each declared **once**, called by every estimator. Nobody re-derives a curve |
| **Targeting** | `TargetResolver.Resolve` is called by the dispatcher, `EffectBag`, `StatusEffectBridge`, `StatusSpread` and `ActionTargetResolver` alike |
| **Resource pools** | `BattleRunState.cs:129` uses `LawnActorResourcePools` **verbatim**, with a comment saying it deliberately avoided a near-duplicate type. This is the law already applied correctly, by someone, before it was written down |
| **Shield** | `DamageApplyPipeline` → `ShieldGate` on both the battle and lawn apply paths |
| **Trigger vocabulary** | 13 strings, one declaration since 2026-09-16, guarded |

### Defects — a mode owning a mechanism, or no owner at all

| # | Defect | Law broken | Evidence |
|---|---|---|---|
| **D1** | ✅ **FIXED (solid-remediation T2.5) — retained as a slot, no longer open.** Was: *battle's `EffectBag` never set `CombatMath`, so `CombatDamageDispatcher` fell back to `PassThroughCombatMath`, whose `Finalize` returns the amount unchanged; battle's basic attack used the resolver while every **effect-driven** hit applied its authored number verbatim — no hit roll, crit, element matchup, penetration, parry or block* | Rule 2 — battle logic with no resolver at all on that path | **Fix: `BattleRunState.cs:497`** wires `Host.Bag.CombatMath = OverlayCombatMath.Create(resolveActor, rng: effectCombatRng)`; `:495` wires `Bag.ActorResolve` (which `OverlayCombatMath` resolves both sides through, and which `EffectBag`'s owner-element fallback needs to know what the acting actor is made of) and `:496` wires the battle-seeded `effect-combat` stream, whose `SeededRng.DeriveStream` is what makes a battle's rolls replayable. The pre-fix evidence is still true of the code that was replaced: `BattleEffects.cs:55-64` (never set it), `CombatDamageDispatcher.cs:28` (fallback), `ICombatMath.cs:15-16` (pass-through). ⚠️ `CombatMath` **alone** was measured to move 0 of 13,943 tests — `Finalize` returns the amount unchanged on an empty payload — so `ActorResolve` is not optional beside it |
| **D2** | **Reflect is lawn-only.** Four registered channel families are inert in battle, delve, siege and web match | Rule 4 — a mechanism one mode has and the others do not | `TryReflect` lives inside `DispatchInstant`, which battle never enters. ⚠️ **This row's second support is now stale:** it also claimed *"battle's bag also never sets `ActorResolve`, so the `:84` guard would fail anyway"* — `ActorResolve` **is** wired since solid-remediation T2.5 (`BattleRunState.cs:495`, the same commit that fixed D1), so that half no longer holds and the defect rests on the `DispatchInstant` half alone. Zero occurrences of "Reflect" under `Battle/` or `Actions/` |
| **D3** | **9 of 13 atom triggers never fire in battle** — `OnDamageTaken`, `OnDeath`, `OnSpawn`, `OnTimer` and the five match/board-economy triggers. The lawn raises all 13 | Rule 2 — the same authored content behaves differently by mode | Battle raises `OnActivate`, `OnDamageDealt` (`BasicAttack.cs`), `OnGranted`/`OnRemoved` (`EffectBag.cs:277-301`) |
| **D4** | **Delve and siege compose with no `HubInputs` at all** — the same specimen fights with different numbers depending on the mode | Rule 4 | `Encounter.cs:206-212`, `DistrictAssaultResolver.cs:360-385`; only `WebMatchService.cs:600-609` populates them |
| **D5** | **The compose paths do not share registration.** `BattleHubCompose` bypasses `ActorHubBootstrap.CreateDefault` and registers neither `RpgProgressionSubsystem` nor `StatusDerivedSubsystem`; the lawn registers no `StarLoyaltySubsystem` | Rule 4 — per-mode stat vocabulary | `BattleHubCompose.cs:15-17,41-64` vs `CheatState.cs:49-81` vs `UniqueActorHubCompose.cs:70-76` |
| **D6** | **The mid-battle derived recompose is a permanent no-op** — it runs every round against an input with zero production writers | Rule 2 | `BattleEngine.cs:481`; `BattleDerivedModifierLedger` has one construction-time writer (`BattleRunState.cs:460`); `ActiveAuras` has none; `Host.AddDerivedContribution` is test-only |
| **D7** | **`SiegeExpectedDamage` uses subtractive defense** against a shipped `"defenseShape": "divisive"` default, has no base-damage term and no amp/crit — while its own comment claims it is "identical to" the resolver | Rule 3 — an extension re-deciding a mechanism | `SiegeExpectedDamage.cs:40` vs `combat.v1.json:24`; §6.3a records subtractive was dropped because 17.1% of landed hits dealt nothing |
| **D8** | **The reflect formula is written twice verbatim**, no shared function | Rule 2 | `CombatDamageDispatcher.cs:113-118` (real damage) vs `PhaseModel.cs:152-157` |
| **D9** | **Kill attribution is absent outside the lawn**, and on the lawn the general horde has no owner row — so no empire earns from it | Rule 2 (responsibility 17) | `MatchHost.cs:322-324`; see the species-progression ideal |
| **D10** | **Permanent death is delve-local.** `ExtractionSettlement` decides Retire/Recover/Roster for a delve; no other mode has an equivalent | Rule 4 (responsibility 9) | `Delve/Attrition/ExtractionSettlement.cs:7,36-44` |
| **D11** | **Equipment damage in battle does not exist** — no durability mechanic anywhere; every "durability" hit in source is an unrelated word-sense. ✅ **Owner ruling 2026-09-16: owned by the `species-gear-chain` program, not this one.** That program is half-built (`worktree-species-gear-chain-20260915-9afc`); it merges into the remediation branch, is refactored with everything else, and then continues its own plan and builds this. **Struck from the remediation fix list; it stays on the register as responsibility 10 with a named owner** | Rule 2 — a named responsibility, now with an owner | measured 2026-09-16 |
| **D12** | **Capture is built inside the Delve, not as a battle-engine extension** — the owner named it as *"definitely an extension of battle engine"* | Rule 3 | `Delve/Wild/CaptureAction.cs`, refused behind `CrossProgramLandedFlags.ItemCostRowLanded = false` |
| **D14** | **72 per-element parry/block/reflect channels have no reader in any mode** — those readers are omni-only | Rule 2 — registered vocabulary with no implementation | `CombatDerivedReader.cs:53-57,67-68` |
| **D15** | **The lawn runs two time bases at once.** Found by following the owner's clock ruling into code. The engine's clock abstraction is shipped and correct, and the kernel drives the lawn's DoT and shield upkeep as scheduled **100 ms** events — but the injector wires `EffectBag.UtcNow` to `SystemEffectClock`, the raw wall clock, so **status timing reads wall time while DoT scheduling reads the kernel's event queue.** One board, two notions of when. ⚠️ Report this precisely: the injector's wall-clock wiring is a **documented deliberate choice**, not an accident — `EffectBag`'s own error text says a live host *"wires it to the real wall clock explicitly, on purpose, at its own composition root."* The defect is not that choice; it is that the choice was made for the *time source* and then silently became the *scheduler* for one half of the tick vocabulary. Under the clock ruling the engine's module owns when a pulse happens; the wall clock may only be what feeds it | Rule 2 + responsibility 12 | `EffectRuntime.cs:58` · `EffectBag.cs:236-246` · `KernelDriveHost` 100 ms events · `SimulationClock.cs:16-27` · ⚠️ **the T4.14 fix was inert on every live board until `backlog-clean-up` BCU8.3 (2026-09-20) re-wired it**: the advance sat in the accumulator B26 had already gated behind the kernel, so `AdvancedEffectClock` was frozen on-board — see `tasks/solid-remediation-todo.md` T4.14's correction |

> ⚠️ **Retracted: what was D13.** The first cut of this page listed *"intent declaration is forked — siege
> ships its own AI source rather than extending one"* as a defect. **That was wrong, and it was wrong in the
> most expensive direction: it called a correct design a violation.** Under §3c the AI is not the engine, so
> five `IIntentSource` implementations are five policies plugged into one seam — exactly the shape the law
> wants — not five copies of a mechanism. Corrected on the owner's ruling the same day. The numbering skips
> D13 rather than renumbering, so the retraction stays visible.

**D1 is fixed, and it was the one to fix first.** It was a single property on an already-constructed
object, using components that already ship, and it made the largest share of the existing stat
vocabulary start mattering in battle. `BattleRunState.cs:497` is that one line (with `ActorResolve`
at `:495` and the seeded stream at `:496`); the wiring is measured, not assumed — see the D1 row.
**This page kept listing it as the open defect after it was fixed**, which is the one way an SSOT
here can do real damage: a reader re-deriving battle-engine gaps would budget against a property that
is already set.

---

## 5. What a feature owes this engine

Modelled on `the-loops.md`'s *"What a feature owes this page"* and `actor-layer-compose-ideal.md`'s five
questions. **If your feature changes what happens in a battle, answer these in the feature's own spec:**

| | Question | Why it exists |
|---|---|---|
| 1 | **Which responsibility is it** (§3), or is it a new one? | The register is a closed vocabulary; adding to it is a reviewed change, like `ActionCategory` or `AtomKind` |
| 2 | **Does it DECIDE or RESOLVE?** (§3c) | Deciding is the player-control/AI system and belongs outside the engine, entering through `IIntentSource`. Resolving is the engine. "Where to move" is AI; "whether that move is legal" is the engine |
| 3 | **Is it a mechanism or a loop?** | A mechanism has one implementation for every mode. A loop may be mode-specific. Getting this backwards is how §4 happened |
| 4 | **Which existing implementation does it extend?** | "Built on top of the battle engine" means calling it, not copying it. `SiegeExpectedDamage` is what copying looks like |
| 5 | **Does every mode get it?** | If the answer is "only in battle" or "only on the lawn", say why, and expect that reason to be refused |
| 6 | **Is it deterministic and seeded?** | Rule 5. If it reads a clock, ambient state, or an unseeded RNG, it is not engine code — find its seam. A battle that cannot be replayed from a recorded intent stream cannot be proven |

**And one rule that is not a question:** the feature **calls the engine's mechanism**. It never
re-implements it, never estimates it with a private formula, and never decides a battle number itself.

---

## 6. What would enforce this

Prose does not stop anything. Both of these belong in the spec phase and are in this repo's idiom:

- **A responsibility registry with a membership test** — §3 as a real closed list, so a new battle
  mechanism fails a test until someone reviews it. `guard-actor-hub.py` already refuses a second
  composer; this refuses a second *owner* of a battle responsibility.
- **A mode-conformance test** — assert that every registered mode drives the same mechanism set, so D4
  and D5 (a mode composing with a different subsystem set) fail in CI rather than in a live run.

⚠️ **`guard-class-system.py:129-150` is not that test.** It is a *positive presence* check — one symbol
reference anywhere passes it — which is why `PhaseModel`'s hand-copied reflect formula passes today. It
also covers two filenames and never scans `tools/`.

---

## 7. Rulings — 2026-09-16

| # | Question | Ruling |
|---|---|---|
| 1 | Confirm §2's loop/mechanism split | **Confirmed and sharpened.** Mechanisms shared; a mode's scheduler is built *above* the engine; **the clock is a unified engine module**, with `ITimeAdvance` the only per-mode part. The lawn is an exception to clock *control*, never to clock *ownership* — its DoT and status ticks are the engine's to compute. VFX may drift. This produced **D15** |
| 2 | Close the §3 register | **All eight additions accepted.** §3a + §3b are now the closed register |
| 3 | D11 — equipment damage | **Owned by `species-gear-chain`**, a half-built program that merges into the remediation branch, gets refactored with everything else, then continues its own plan. Struck from remediation's fix list; stays on the register with a named owner |
| 4 | Order of attack | **Delegated to me.** Recorded in `solid-remediation-ideal.md` §Order of attack |

### What the rulings changed

- **§2 got stronger, not weaker.** "A mode owns its loop" was too loose; the clock is a mechanism, and the
  shipped `ITimeAdvance` abstraction already expresses the split exactly.
- **The register closed**, which is what lets the §6 membership test be written at all.
- **D11 left the fix list and gained an owner**, which is the difference between a gap and a plan.
- **D15 appeared** — and it appeared *because* of the ruling. The clock question is what sent me into
  `SimulationClock.cs` and `EffectRuntime.cs:58`, and the two time bases on the lawn would not otherwise
  have been found.
