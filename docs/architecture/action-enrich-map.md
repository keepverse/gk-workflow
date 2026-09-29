# Capability map: `action-enrich`

**Status:** proposed 2026-09-18 from [action-enrich-ideal.md](action-enrich-ideal.md); strengthened the
same day (findings below). The owner asked for specs covering every idea from 2026-09-17 to 2026-09-18
with no further questions. Specs live at [`action-enrich/`](action-enrich/). Plan →
`tasks/action-enrich-plan.md` (new) + `tasks/action-enrich-todo.md` (new).

**Scope, in one sentence:** the hit's base moves from the actor's `atk` to the action. The damage
formula, the hybrid element split, per-element power, the element matrix and the action's effect chain
are already built and do not change.

This map **is** the spec target `solid-enforcement` SE5.1 names (*"Spec `action-base-stats` from its
ideal"*); SE5.1 is marked done on these specs' writing (`tasks/solid-enforcement-todo.md:313`).

## Modules

| Id | Responsibility | Depends on |
|---|---|---|
| `action-base` | One function, `ActionBaseDerivation.BasePowerMilli` (skills/innates: `qPowerMilli` at the holder's `effectiveRung`; basic: tuning), resolved at hit time — nothing stored on `CompiledAction`. `BattleRunState.EffectiveRungOf` becomes the one instance resolver shared by `CostLedger` and the hit. `Θ` is Hub output (`progression.power`). Battle's hit reads base × `P(Θ)` instead of `LiveAtk`. One golden re-bless | — |
| `lawn-action-base` | The lawn's `act.attack` grant bakes the same base × the owner's `P(Θ)` as a plain `amount`, replacing `{"eventField":"damage"}`, rebound on every edge that changes it (record on the snapshot edge, rebind in the main-thread drain); instakill refused through the overlay filter grammar | `action-base` |

Build order: `action-base` → `lawn-action-base`.

## Checkpoints

- **Checkpoint 1 — battle reads the action.** No production call of `LiveAtk(` on a damage path; two
  actions of different effective rung on one attacker deal different base damage; cost and base read one
  resolver; goldens re-blessed once for this module with the reason recorded.
- **Checkpoint 2 — the lawn reads the action.** A lawn hit's rider amount equals the battle base for the
  same action at the same `Θ`; a `Θ` refresh rebinds live grants in the drain; an instakill hit does not
  ride the rider.

## Golden re-bless order (cross-program, fixed here and in `action-skill-tiers-map.md` §7)

Three changes can move battle goldens, each for a different cause. Tunables T7 (`tunables-ssot.md:114-118`)
requires a golden move to be attributable to exactly one cause, so each re-blesses in **its own commit**,
in this order, and a module that finds no golden moved says so instead of re-blessing:

1. `action-skill-tiers` **ST2** — cost stops being scaled twice (a defect fix; moves only a golden that
   commits a costed action with authored rung > 1).
2. `action-skill-tiers` **ST1** — a corpus action's drawn atoms change (content).
3. **`action-base`** — the hit's base moves from `atk` to the action (every damage-dealing golden).
4. `species-progression` **module 1 C1 fix** — a defect correction (a unique stops receiving the empire
   species fallback in world battles), **not** a re-bless; any golden it moves is a defect to fix.
5. `species-progression` **step 6.1** — each aptitude layer resolves alone (R2/R16); the one explained
   re-bless of that program (`species-progression-map.md` §3 "Re-bless order").

The two maps record the same sequence; reconciled 2026-09-18 by the orchestrator.

Why `action-base` last: its basic-attack base is calibrated against the goldens' then-current state
(`spec-action-base.md` §Tunables), so it must measure after the two smaller moves have landed.
`solid-enforcement` SE1.7 also records sim goldens "before and after" (`tasks/solid-enforcement-todo.md:127-131`);
it is independent of this order and re-blesses under its own cause. Two changes never share a re-bless
commit; if two land in one working tree, the later one rebases and re-blesses separately.

## Cross-program dependencies

| Needs | From | State |
|---|---|---|
| `atk` retirement bookkeeping (channel removal, guard gates, content that grants `atk`) | `solid-enforcement` SE1.6/SE1.7 (`retire-atk`) | open. **Not a blocker**: this program stops *reading* `atk` for damage; deleting the channel and regenerating content that grants it stay SE1.6/SE1.7's (one owner) |
| Cost scaled once, and the window-bounded `effectiveRung` | `action-skill-tiers` ST2 | proposed. Ordered before `action-base` for goldens (above). ST2 edits `UnlockLadder.EffectiveRung` and the band on the held row; `action-base` makes the resolver reachable. Neither re-implements the other |
| A granted action (grant rows exist in production) | `action` **A26** (T62: `UnlockTuningPolicy.Configure` in `Program.cs`) | **open** (`tasks/action-todo.md:3002-3006`; verified: no `UnlockTuningPolicy.Configure` call in `gk-core/src/FusionRpg.Server/Program.cs`) |
| Stronger held action preferred when tags tie | `action` **A31** (T67: rung tiebreak) | **open** (`tasks/action-todo.md:3082-3096`; verified: `ActionTagPreference.cs:47` still ties on `action_id` only) |
| **Holders wired into production battles** (`unlockStateFor` supplied by a production caller) | `action` program — ~~no task owns it~~ **owner id `A33` `battle-holder-wiring`** (proposed row in [action-map.md](action-map.md) §17, filed 2026-09-18, session `rulings-r20-r24-20260918`; spec and plan task still owed) | **gap, now owned.** `BattleEngine.Resolve`'s `unlockStateFor` has no production caller (only `ActionCostsCooldownsAdoptionTests.cs:308,313`); none of A26–A32 (`tasks/action-todo.md:2994-3190`) adds one. Until it lands, every skill's base and cost read the **authored** rung (= its window ceiling) through the A23 fallback. Reported to the action program as a missing module; A26 is the point where it starts to matter (grants make skills held) |
| Lawn owner `Θ` hydrated | `CheatState.PowerIndex` / `ApplyPowerSnapshot` (`CheatState.cs:244-257`) | built |
| Injector loads the same tuning version as the server | `action-skill-tiers` ST5's version-agreement guard (parameterised by domain, `action-base` row) | proposed with ST5 |
| Lawn attack stays vanilla-scaled today | `lawn-tuning-profile` `base-relative-read` §scope (attack half removed 2026-09-16) | built; this program replaces the vanilla amount, so no conflict |
| `ssot-power-scale.md` §10.2 row for the rung table's `qPower(r)` ladder | power program (file owner) | owed by `action-base`'s build (the ladder had no row; it becomes a damage multiplier here) |

A second held action **fired in a real match** therefore needs A26 + the holder wiring gap closed; A31
decides which of two tagged actions is chosen. None of the three is needed to build or test these
modules.

## Strengthen pass 2026-09-18 — what changed and why

| Finding | Fix |
|---|---|
| `EffectiveRungOf` was claimed reusable at the hit site; it is a private static reachable only inside `CostLedger`'s closure (`BattleRunState.cs:611-612,636-649`) | One instance resolver on `BattleRunState`, passed to `CostLedger` as `rungOf` |
| The magnitude `Θ` was named `Setup.ThetaActor ?? Setup.Index` from a contest-side comment | Hub output `progression.power` (`BattleHubCompose.cs:56`, `CostLedger.cs:153` precedent) |
| `action-base` derived at `ActionCompiler.cs:61`, ST2's seam, and added a field only the basic attack used | No stored field; one derivation called at the hit; ST2 sole owner of that line |
| A catalog lookup at the hit would miss siege/lent actions and the basic attack | Resolve the swung row from `HeldActionsOf` |
| Instakill refusal had two candidate owners ("binder or bag filter") and the binder cannot see events | One owner: `PassesOverlayFilters` gains `excludeInstakill` |
| Snapshot edge ran grant calls off the main thread; "toggle on" and "tuning reload" triggers did not exist in code | Record-then-drain rebind; trigger table rebuilt from the real call sites |
| A26/A31 were the only named dependencies | Holder wiring gap added (no owning task) |

## Deliberately out

Hit count, proc coefficient, crit/accuracy per move, a delivery-profile enum, any seedsmith change: rejected
by the owner 2026-09-18 as over-scope. Multi-hit base splitting is a named follow-up for whoever authors
multi-offset content (`ActionRunner.cs:226-233`).
