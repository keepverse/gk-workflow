# SOLID remediation — capability map

**Status:** spec phase, Phase 0 (capability map). Approved 2026-09-17, then revised the same day by a
standards review that found ten gaps. Ideal doc: [solid-remediation-ideal.md](solid-remediation-ideal.md).

This is the index. Module ids are stable kebab-case and are what every downstream plan, task and commit
selects work by. Each module spec lands at `docs/architecture/solid-remediation/spec-<module-id>.md`.

---

## What changed between the ideal doc and this map

The ideal doc was measured **before** the merge, said so, and named re-measuring as required before this
map closed the module list. Re-measured on `features/mega-merge`, 2026-09-17:

| | Ideal doc (pre-merge) | Now |
|---|---|---|
| C# files | 1,246 | **1,313** |
| namespace ≠ folder | 85 | 102 |
| …`FusionRpg.Data` flat-root convention | 73 | 89 |
| …injector host shims | 9 | 9 |
| **genuinely misfiled** | **3** | **4** |

The fourth is `gk-core/src/FusionRpg.Server/Achievements/AchievementEvaluator.cs`, declaring `FusionRpg.Server`.
It arrived with `achievement-title` — the layer-5a/5b work the ideal doc predicted would land here. Measured again at T0.6 and **corrected**: it is *three* `git mv`s plus *one* namespace fix, not four
moves. `AchievementEvaluator.cs` declares `FusionRpg.Server` while sitting in `Server/Achievements/` —
but its own neighbour `RewardBundleService.cs` declares `FusionRpg.Server.Achievements`, so moving it to
the project root to satisfy its namespace would have been worse organisation than fixing the namespace.
It has no call sites at all (it is an unregistered `BackgroundService`), so the fix was free.

**All six architectural guards pass** on the merged tree — single-writer, secondary-no-unity,
funnel-delta, actor-hub, DAL, test-substrate. The invariants that already have enforcement are holding;
what is rotten is what has no guard, which is why the two guard modules sit at the front of the build
order rather than the end.

### Decisions this map records

**1. `green-baseline` is a real module, and it is first.** The per-module gate "ends green — builds,
guards pass, scoped `verify-change.ps1` passes" is unsatisfiable against a red baseline: a module could be
perfect and still fail its own exit criteria on failures it did not cause. Owner ruling 2026-09-17: clear
the reds and make "all green" literal, rather than freezing a known-red baseline and gating on "no new red".

**2. `file-move-tool`'s justification is void; the module is kept on the owner's instruction.** The ideal
doc justified it as free work during the merge window — *"that window is otherwise dead time"*. The merge
is done and there is no window, so it costs real time against a measured input of four files whose
namespaces are already correct. Owner ruling 2026-09-17, after seeing that measurement: keep it, scoped to
**move *and* rewire** (namespace, `using` directives across callers, and the project file when the move
crosses assemblies). Sequenced late, where its cost lands on nothing else.

---

## Modules

| Module id | Responsibility | Register entries | Depends on |
|---|---|---|---|
| `green-baseline` | Every CI suite and guard green, so "module ends green" means what it says | — | — |
| `battle-responsibility-guard` | Enforce the battle-engine responsibility register mechanically — ownership-shaped, not presence-shaped | G2 | `green-baseline` |
| `verification-boundaries-extend` | Scoped verification for `gk-core/tools/CombatSim/**` and `gk-core/tools/ProvePredictor/**` | G3 | `green-baseline` |
| `battle-effect-math` | Battle's `EffectBag` carries `CombatMath`, so registered channel families apply to effect-driven hits | D1 | `elemental-resolver` |
| `retaliation-shared` | Reflect becomes one shared mechanism instead of a lawn-local feature written twice | D2, D8 | `battle-effect-math` |
| `battle-mode-parity` | One subsystem set, one trigger set, one `HubInputs` shape across modes; retire the dead recompose | D3, D4, D5, D6 | `retaliation-shared` |
| `vocabulary-single-declaration` | Status categories and element ids declared once | X1, X2 | `green-baseline` |
| `estimator-parity` | Estimators call the resolver's primitives or are pinned to them | D7, X5 | `battle-mode-parity`, `verification-boundaries-extend` |
| `species-empire-scope` | The empire dimension, kill attribution, Zomboss earning | S1, S2, S3, S7, ~~S8~~ (struck 2026-09-17 — fixed 2026-09-13 by `f1955a1d7`, pinned by three tests), D9 | `battle-mode-parity` |
| `species-carrier` | Layer 1 binds; the fusion-picks feature stops being dark | S4, S5, S6 | `species-empire-scope` |
| `capture-as-extension` | Capture becomes an extension built on the battle engine, per the owner's ruling, instead of a delve-local action | D12 | `battle-mode-parity` |
| `unified-clock` | The engine's clock module owns when a pulse happens on every board, lawn included; the wall clock only feeds it | D15 | `battle-mode-parity`, `battle-responsibility-guard` |
| `numeric-single-source` | Pool regeneration reads one source | X3 | `green-baseline` |
| `elemental-resolver` | The battle engine's elemental sub-module: every contest — attack, dodge, block, parry, absorb, reflect, status apply — resolves from the element matrix with **omni as the additive base** | D14 | `battle-responsibility-guard` |
| `death-and-injury` | Permanent death and injury promoted to the battle engine; each mode ships its own ladder | D10 | `battle-mode-parity` |
| `file-move-tool` | Move **and** rewire a file across folders and assemblies; apply it to the four misfiled files | — | `green-baseline` |
| `stub-register` | Create the stub debt register and its own plan; every module appends to it as it runs | G1 | `green-baseline` |
| `fe-debt-register` | Create the FE debt register and the hand-off to the later FE program | X4 | `green-baseline` |

### Register coverage — all 27 entries have a disposition

The definition of done says every entry is **fixed, reassigned, or struck**. That is only checkable if
every entry appears here. Gap found by the 2026-09-17 standards review: four had no module at all.

| Disposition | Entries |
|---|---|
| Fixed by a module above | D1, D2, D3, D4, D5, D6, D7, D8, D9, D12, D14, D15, S1–S8, X1, X2, X3, X5, G1, G2, G3 |
| **Reassigned** — `species-gear-chain` owns it, half-built, continues its own plan after the refactor | D11 |
| **Tracked, not fixed** — `web/**` is out of scope for remediation and in scope for tracking | X4 |
| **Retracted** — never a real defect; kept as a numbered hole so the retraction stays visible | D13 |


## Register coverage audit (T6.1, 2026-09-17)

Every entry checked against the code and the task record, not against this table's own earlier claim.
**Three entries did not survive that check as written**, and they are the reason the audit is worth
doing rather than transcribing.

| Entry | Disposition | Where the evidence is |
|---|---|---|
| D1, D2, D8 | fixed | `battle-effect-math`, `retaliation-shared` — Phase 2 |
| D3, D4, D5, D6 | fixed | `battle-mode-parity` — Phase 3, T3.1–T3.6 |
| D7 | fixed | T4.11/T4.12 — estimator now divisive; parity test with a stated tolerance |
| D9 | fixed | T4.3 — attribution. **Earning is NOT included**, and CP4's clause says so; **and see `SR-18`** — the `creditEmpire` T4.3 resolves is read by nothing in production, the same inert shape `SR-17` carries below. Both stop at one missing vanilla-PvZ capture signal |
| D10 | fixed | T4.8–T4.10 — settlement promoted; **but see `SR-17`**, the lawn's TUNED ladder is unreached. (Corrected 2026-09-17: the lawn was never *unsettled* — it settled every death at the harshest outcome via an inlined copy of the delve's branch, now routed through the seam) |
| D11 | reassigned | `species-gear-chain`, half-built, continues its own plan |
| D12 | fixed | T4.7 — relocated into the engine; the **seam finding** is recorded in its spec |
| D13 | retracted | never a real defect; the numbered hole keeps the retraction visible |
| D14 | fixed | `elemental-resolver` — Phase 2 |
| D15 | fixed | T4.14–T4.16 — one clock, replay determinism, no round trip. ⚠️ **T4.14's advance was inert on every live board** (it sat in the accumulator B26 had already gated off); re-wired by `backlog-clean-up` BCU8.3, 2026-09-20 — see `tasks/solid-remediation-todo.md` T4.14's correction |
| S1, S3 | fixed | T4.1 — **three seams**, plus a fourth found later (`fb45126f`) |
| S2 | fixed | T4.4 — the species term reaches the compose |
| S4, S6 | fixed / ~~disproved~~ | T4.6 — S4 wired; **S6's premise is stale**, the second carrier is live and was NOT deleted |
| S5 | fixed | T4.5 — **premise corrected**: it never had a caller to lose |
| ~~S7~~ | **NOT fixed — open** | T4.4 proved routing the term cannot close it; see below |
| ~~S8~~ | **struck** | premise false since 2026-09-13 (`f1955a1d7`), pinned by three tests |
| X1, X2, X3 | fixed | T5.1–T5.4 — one declaration each; X2's `""` was a silent wrong answer |
| X4 | tracked, not fixed | FE register; `web/**` out of scope for remediation |
| X5 | fixed | T4.13 — the mixture de-duplicated; the FILE has many live readers and stays |
| G1, G2, G3 | fixed | Phase 1 — stub register, responsibility guard, verification boundaries |

### The three that did not survive the check

**S7 is open, and this program cannot close it.** T4.4 routed the species allocation into the battle
compose, which closed S2. It does not close S7, and the reason is structural rather than incomplete
work: `AptitudeResolver` reads `allocation.Share(edge.Source)` — a **share**, not a point count — while
the magnitude comes from `pTheta = ladder.Value(theta)`. Ten points and two hundred points in the same
single share are both share 1.0 and compose **identically**. A species LEVEL enters
`SpeciesAllocation.Baseline(shares, level, tuning)` as a point count, and battle's theta is the
**member's** level, never the species level. So a level-4 plant type still composes exactly as a level-1
one. Closing it means giving a species level a path into theta or a channel — *deciding what a species
level grants*, which this module's own note assigns to `species-progression`. Pinned by
`Point_count_alone_does_not_move_the_compose_which_is_why_S7_is_not_closed_here`.

**S6 was disproved, not fixed.** Its shape step said to delete the second of "two dark carriers" once
zero readers were proved. Zero readers is false: `trait.species-magnitude-{id}` is produced by the
species import and consumed on every unique-actor deploy, with **904 of 906** species carrying
magnitudes. The spec's Boundaries say to prove zero readers before deleting — the proof failed, so the
rule is satisfied by **refusing**, not by proceeding.

**S8 was struck.** Its premise had been false since 2026-09-13.

### The pattern worth carrying forward

S8, S5 and S6 were all **stale premises** — each described the code as it was when the entry was
written, and each had moved. All three were found by opening the file rather than by re-reading the
register, which is `DESIGN-GATE`'s own first rule: *code beats docs*. An audit entry is a claim until
someone checks it, and this program's own register was no exception to that.

**D10's entry is dispositioned but its CP4 clause is not.** Everything T4.8–T4.10 asked for shipped.

**⚠️ The sentence that used to follow here was wrong, and it is worth leaving the correction visible
because this page's own paragraph above it is about exactly this failure.** It read: *"the lawn still
has no settlement call site, so the ladder never runs."* That came from a code comment, not from the
code. Re-read 2026-09-17: the lawn settled **every** death, by inlining the delve's own `case Retire:`
branch verbatim — `RetireUniqueActorUnlocked` + `MoveAssignedGearToCorpseCacheUnlocked`,
unconditionally. So there was a settlement call site, it was simply not asking
`MemberSettlementRules.Decide` — a second decision path for a decision the engine already owns, which
is the SOLID shape this program exists to remove, sitting unnoticed *inside* a register entry that
claimed the opposite. The lawn now routes through the seam with `AlwaysPermadeath` (byte-identical),
and what remains is swapping in the tuned `LawnPermadeathLadder` — one line, blocked on a missing
per-actor damage-taken figure and on a balance decision. `SR-17` carries the full correction.

A register entry can be honestly closed while the checkpoint above it stays open, and conflating the
two is how a program reports completion it has not reached. **An entry can also be honestly written
and still be wrong about the code** — which is the stronger version of the same lesson, and the one
this row earned.

**D10 and D14 were ruled by the owner on 2026-09-17**, and both rulings made a module rather than a
strike — so every one of the 27 entries now has an owner.

**D10 — promote it to the battle engine.** Permanent death and injury are engine mechanisms; *each mode
ships its own ladder*. The delve already has one keyed to delve difficulty; the lawn's is keyed to damage
taken (more damage taken, more chance of injury and permanent death). The consequence the owner named:
**deploying a unique actor is a cost.** Module: `death-and-injury`.

**D14 — the channels are not dead; the reading is incomplete.** The per-element parry/block/reflect slots
are the element half of the omni-additive rule, unimplemented for three families while every other contest
family already reads `omni + element`. Module: `elemental-resolver`.

---

## Build order

```
green-baseline
  ├─ battle-responsibility-guard (G2)
  ├─ verification-boundaries-extend (G3)
  ├─ stub-register (G1)  ─┐  created EARLY, appended by every module, closed at the end
  ├─ fe-debt-register    ─┘
  │
  ├─ elemental-resolver (D14) → battle-effect-math (D1) → retaliation-shared (D2,D8)
  │                                   → battle-mode-parity (D3,D4,D5,D6)
  │        ├→ species-empire-scope (S1,S2,S3,S7,S8,D9) → species-carrier (S4,S5,S6)
  │        ├→ estimator-parity (D7,X5)
  │        ├→ capture-as-extension (D12)
  │        ├→ death-and-injury (D10)
  │        └→ unified-clock (D15)
  ├─ vocabulary-single-declaration (X1,X2)
  ├─ numeric-single-source (X3)
  └─ file-move-tool
```

Ordered by value per unit of risk, dependencies respected, enforcement deliberately early:

1. `green-baseline` — nothing can be gated until the gate means something
2. `battle-responsibility-guard` — changes no behaviour, so it is the safest first production change, and everything after it lands already protected
3. `verification-boundaries-extend` — same reasoning, and it *unblocks* `estimator-parity`
4. `stub-register`, `fe-debt-register` — created here, not at the end
5. **`elemental-resolver`** — moved to the front of the battle chain by the 2026-09-17 D14 ruling. It is the engine's elemental sub-module and, in the owner's words, *"plays almost role in the damage calculation and shield mechanism"*. It also owns the reason `battle-effect-math` measured inert: `OverlayCombatMath.Finalize` returns the amount unchanged when the packet carries no `ElementPayload`, so the matrix has to reach the packet before wiring `CombatMath` can do anything
6. `battle-effect-math` — now depends on 5. With the payload reaching the packet, this is the first player-visible change
7. `retaliation-shared` — same seam as 6; reflect is one of the contests 5 makes element-aware
8. `battle-mode-parity` — the big one, after the math and the bag are correct
9. `vocabulary-single-declaration` — independent; X2 is a silent-wrong-answer risk
10. `estimator-parity` — needs a correct resolver to bind to
11. `species-empire-scope` — needs battle to have a compose worth adding a species term to
12. `species-carrier` — the carrier is worth binding only once its scope is right
13. `capture-as-extension` — needs the engine's extension seam to be real first
14. `death-and-injury` — needs mode parity, because "each mode ships its own ladder" presupposes the modes agree on the mechanism
15. `unified-clock` — riskiest: the injector hot path, where the no-round-trip invariant lives
16. `numeric-single-source` — small, independent
17. `file-move-tool` — no dependants; its cost lands on nothing else

**`dead-vocabulary` is gone.** It existed to delete D14's 72 channels. The owner's ruling turned D14 from
a delete into a fix, so the module is replaced by `elemental-resolver` and the program now contains
**exactly one delete** (X5's copy, inside `estimator-parity`) rather than two.

**Why the registers moved to position 4.** The ideal doc says a register is *"only useful if written as
the work happens, not reconstructed at the end"*, and the first draft of this map sequenced both last —
a direct contradiction. They are now **created early** (file, schema, and the rule that every module
appends its rows), and the final pass only closes them.

**Two orderings rejected.** Guards last — the instinct, and how these defects got here. And
`elemental-resolver` late, on the old reading that D14 was a deletion waiting on every other module. The
ruling inverted that: it is a foundation the battle chain depends on, and the measured `ElementPayload`
gate proves `battle-effect-math` is inert without it.

---

## What every module spec must state

Beyond its own fix, from the ideal doc's §"Three things every module owes" plus the four standing gates
the 2026-09-17 review found missing:

1. **Which tests pinning the defect will be rewritten, and to what contract.** A test is rewritten to
   assert the contract, never edited to expect the new number. If the old test cannot be restated as a
   contract, that is a signal the change is wrong, not that the test is in the way.
2. **A before/after measurement** where the fix makes an inert number start applying. The module owes the
   measurement, not a re-tune.
3. **Which register it appended rows to**, if any.
4. **Assertions are contracts, never populations** (`validation-ssot.md`). No assertion pins a derived
   population count, an item total, generated `name`/`description` text, or a per-cycle outcome. A pinned
   literal names a closed vocabulary and says why. This is the repo's most-repeated defect.
5. **Numeric width and overflow behaviour** for any magnitude the module produces or consumes, with the
   threshold that justifies it — `long` for integer magnitudes `P(Θ)` can grow, widen before multiplying,
   integer overflow throws rather than wraps.
6. **ActorHub: contribute or consume, named explicitly.** Contribute via `IActorStatSubsystem` or a
   registered atom reader with a non-empty GG-49 `ContributionSourceIds` grammar id, or consume Hub output
   only. Never a private fold. Citing the fused-and-deleted `BattleStatComposer` as permission fails this.
7. **Generated seed data is never hand-edited.** A failing seed test is a stale test or a generator
   defect. Several modules touch generated corpora; `green-baseline` already hit this in
   `family-expand.g-affliction.json`.

**This program re-tunes nothing.** A remediation pass that starts changing balance numbers has stopped
being a remediation pass. Where a fix makes a previously-inert number start applying, the module owes a
before/after measurement, not a re-tune — any re-tune that measurement justifies belongs to
`lawn-tuning-profile` or the owning feature.

**That is not the same as shipping no numbers.** A module that introduces a genuinely new mechanism ships
**working values** for it, per this repo's own named precedent — *"default now, re-tune later"*
(`action-corpus-ideal.md` S36) — with an `_meta` note saying they are unmeasured and not a validated
balance decision, exactly as `action-corpus-cost-templates`, `contracts` and `action-rungs` already do.
Owner, 2026-09-17: *"because it is tunable, so just ship with random number and we play game and tuning
later — we don't really do tuning phase in this repo yet because we still not complete the build."*

`death-and-injury`'s lawn ladder is the one module this applies to. Editing an authored registry under
`**/_registry/**` is not a balance change either.

---

## The per-module gate, and how it is actually run

A module ends green: it builds, the guards pass, and its scoped verification passes.

`scripts/verify-change.ps1` **requires `-Session <id>`**, and DESIGN-GATE §5 requires
`session-boundary-check.py` to be clean. Both were unrunnable when this map was first written: no
`solid-remediation` session record existed, and 14 stale records with ~15 crossing claims made the
boundary check dirty.

**Ruling (owner, 2026-09-17):** there are no other active sessions and no other agents on this tree, so
the crossing claims are stale metadata rather than live conflicts. This program therefore:

- creates **one** session record, `tasks/sessions/solid-remediation-<date>.json`, as `green-baseline`'s
  first task, so `verify-change.ps1 -Session solid-remediation-<date>` is runnable for every module;
- marks the 14 stale records merged or abandoned in the same task, so the boundary check is clean and
  stays a real signal rather than noise everyone learns to ignore;
- does **not** treat a dirty boundary check as a reason to skip scoped verification.

A module that cannot get green is reverted to its start commit and re-planned, never left half-applied
for the next module to inherit. Inside a module the branch may be red — the granted build-break
permission — but a live probe never happens mid-module, because a live probe needs a build.

---

## Definition of done

Not "all defects fixed" — that is a task list. The program is done when:

1. Every entry on the register is **fixed, reassigned, or struck with a reason** — see *Register
   coverage*, which is the checklist for this
2. The battle responsibility guard and the verification boundaries are **in CI**
3. Both registers **exist and are populated**, so the next two programs inherit a measurement
4. **The live proof passes**, as defined below

### The live proof, stated so it can fail

The ideal doc's *"a live probe passes on the lawn with the feature on, at the 300-zombie tier"* is not
falsifiable: no named feature, no endpoint, no metric, and no scope label. `live-probe-standard.md`
requires naming the scope, and this repo's own 2026-09-13 incident was a probe that returned `ok:true`
end-to-end for a feature that was broken. This program's proof is instead:

- **Scope: RPG Server Debug.** The proof runs the real application/persistence path against a record real
  gameplay could have created. A Game Injector Debug call may set up the board; it never *is* the proof.
- **What must be true:** on a live lawn at the 300-zombie tier, an **effect-driven** hit (DoT tick or
  on-hit rider — not a basic attack) that authored **no element payload** resolves through the element
  matrix, instead of applying its authored number verbatim.

> ⚠️ **Corrected 2026-09-17, because the first wording could not fail.** It said the hit must
> "resolve through `CombatMath` rather than `PassThroughCombatMath` — before this program it is false
> by construction." That is true of **battle**, which is where D1 lives. It was never true of the
> **lawn**: `EffectRuntime.cs:117` calls `WireCombatMath` unconditionally at construction, and `:545`
> and `:556` set `bag.CombatMath` and `bag.ActorResolve`, all of it predating this program. A lawn probe
> phrased that way would have passed before a line was written — exactly the `ok:true`-for-a-broken-
> feature shape the paragraph above this one warns about, reproduced in the warning's own proof.
>
> What this program actually changes **on the lawn** is `EffectBag.ApplyOwnerElementFallback`: an
> effect packet carrying no authored `elementPayload` now picks up the acting actor's own element. Before
> it, `OverlayCombatMath.Finalize` returned the amount unchanged on an empty payload no matter how well
> `CombatMath` was wired. That is the claim that is false-before and true-after on a lawn, so that is
> what the probe asserts. The battle half of D1 is proven by
> `An_effect_hit_from_an_elemental_battle_actor_no_longer_lands_its_authored_number`, which runs inside
> `BattleEngine.Resolve`.
- **How it is read back:** through the normal path, not the injector telemetry that produced it. A
  response body alone is never proof.

> **The read-back path, named (2026-09-17).** `LawnCombatObserver` is NOT it: it rides the `/api/perf`
> window, so it is the telemetry this clause disqualifies. The path that qualifies is elemental mastery.
> `EffectRuntime.cs:555` wires `bag.OnDamageApplied = GateCounterHost.HandleDamageApplied`, which fires
> for every dispatch including DoT pulses and takes the packet's **element components**; no components
> means no elemental-mastery credit. Credits accumulate, flush on the 5s window to the server's own
> `POST /api/gate-counters/credit`, persist to SQLite, and read back through the ordinary
> `GET /api/gate-counters/{playerId}` — a real player row, the real persistence path, and a
> non-debug read.
>
> That makes the probe falsifiable in exactly the way this program needs: before
> `ApplyOwnerElementFallback`, an effect hit that authored no payload carried no components, so it
> earned no elemental credit no matter how well `CombatMath` was wired. After it, the same hit from an
> elemental actor earns one.
- **The perf budget holds:** `vfx.tick` stays within its locked share of wall time at 300z, measured by
  `PerfProbe`, so the fix is not paid for in frame time.
