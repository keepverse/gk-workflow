# Implementation plan: `action-enrich` (AE)

**Map:** [action-enrich-map.md](../docs/architecture/action-enrich-map.md) ·
**Specs:** [action-base](../docs/architecture/action-enrich/spec-action-base.md) ·
[lawn-action-base](../docs/architecture/action-enrich/spec-lawn-action-base.md) ·
**Ideal:** [action-enrich-ideal.md](../docs/architecture/action-enrich-ideal.md) ·
**Tasks:** [action-enrich-todo.md](action-enrich-todo.md) ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md), lane A. This plan owns the AE
tasks and must honour three parent hard edges: H1 (it is the third re-bless), H6 (the `LiveAtk` read is
replaced in the same change that feeds the new base) and H7 (`action-base` v1 lands with its reader). It
is also the build that closes the parent's checkpoint CC3 ("damage from the action").

**Task id scheme.** `AE<m>.<n>`: `AE1.x` is module `action-base`, `AE2.x` is module `lawn-action-base`.

## Overview

The hit's base moves from the actor's `atk` to the action:
`BaseOverlayDamage = basePowerMilli(action, effectiveRung) × P(Θ_attacker) / 1000`. For a skill or innate
the base is the rung table's `qPowerMilli` at the holder's effective rung. For the basic attack it is a
new tunable, `action-base.v1.json`. `Θ` is Hub output (`progression.power`). The lawn's `act.attack`
grant bakes the same base × the owner's `P(Θ)` as a plain amount, and rebinds whenever `Θ` changes.
Nothing downstream changes: the element split, the matrix, defense, crit and the effect chain all stay
as they are.

## Architecture decisions (from the map and specs, not re-litigated)

- **One derivation, nothing stored.** `ActionBaseDerivation.BasePowerMilli` is resolved at hit time.
  There is no `CompiledAction` field. `ActionCompiler`, `BasicAttackFactory` and `CompiledAction` are
  not touched. `ActionCompiler.cs:61` belongs to ST2.
- **One rung resolver.** `BattleRunState.EffectiveRungOf` becomes the public instance method that both
  `CostLedger` and the hit call. `AE1.2` creates it unless `ST2.5` already has. The second of the two
  adds only its own line: here, the held-row fallback.
- **The swung row comes from `HeldActionsOf`,** never a catalog lookup. That covers the basic attack,
  catalog-less battles, siege and lent actions.
- **`Θ` is Hub output** (`progression.power`, the `CostLedger.cs:153` precedent). This keeps ActorHub as
  the one compose.
- **`P(Θ)` goes through `PowerLadder`** by way of a `BattleRuleset.PowerValue(int)` sibling of `BaseHp`.
  It is the same ladder, not a new curve. The `qPower(r)` ladder gets its own `ssot-power-scale.md`
  §10.2 row.
- **Instakill refusal has one owner:** the `excludeInstakill` key of `PassesOverlayFilters`.
- **Lawn refresh is record-then-drain.** `ApplyPowerSnapshot` only marks the binder dirty. The
  main-thread `Tick` rebinds, and the deterministic `GrantId` makes the rebind an idempotent upsert.
- **`atk` retirement stays with `SE`.** This program stops *reading* `atk` for damage. Deleting
  `LiveAtk`, `Setup.Atk` and the channel is `SE1.7`'s job. Regenerating content that grants `atk` is
  `SE1.6`'s. `SE5.1` (the spec) is already done.

## Dependency graph (modules and tasks)

```
AE1.1 tuning + hub + server host ─┐
AE1.2 one instance resolver ──────┼─► AE1.4 swap the read (H6) ─► AE1.5 re-bless #3 (H1; after ST1.3) ─► SP C1 fix …
AE1.3 derivation + math + P(Θ) ───┘                    │
                                                       └─► AE1.6 §10.2 row
AE2.1 excludeInstakill filter ─┐
AE1.3 ─────────────────────────┼─► AE2.2 grant amount at bind + injector host ─► AE2.3 record-then-drain refresh ─► AE2.4 live probe
                               │                      └─► ST5.4 (action-base guard row, action-skill-tiers)
```

## Suggested order and parallel lanes (suggested, not enforced)

**Hard edges from the parent:**

- **H1:** `ST2.3` → `ST1.3` → **`AE1.5`** → `SP` C1 fix → `SP` 6.1 → `EP` R23. AE1.5 is its own commit.
  The base is calibrated against the goldens as they stand after ST2 and ST1, so AE1.1's measurement is
  **re-checked** just before AE1.4 if either of those moved a golden.
- **H6:** AE1.4 introduces the base as a damage input and removes the `LiveAtk` damage read in **one**
  commit. AE1.1–AE1.3 add pure code and tuning that no damage path reads, so there is never a window in
  which both feed damage.
- **H7:** AE1.1 creates `action-base.v1.json` in the same commit as the `Program.cs` configure. The
  injector loads it for the first time in AE2.2, and ST5.4's guard then keeps the two hosts together.

**Suggested:**

| Lane | Sequence | Note |
|---|---|---|
| AE-battle | (AE1.1 → AE1.3) ∥ AE1.2 → AE1.4 → AE1.5 → AE1.6 | AE1.1–1.3 can be built during ST waves 1–2. AE1.4 and AE1.5 land back to back once ST1.3 is in |
| AE-lawn | AE2.1 (any time) → AE2.2 (after AE1.3) → AE2.3 → AE2.4 | AE2.2 needs only the pure derivation and math, not the battle swap. AE2.4 needs AE1.5 (the full suite runs before a live probe) |

## Phases

| Wave | Module | Tasks | Sizes | Parallel-safe with |
|---|---|---|---|---|
| 1 | `action-base` | AE1.1–AE1.6 | S, S, S, M, XS, XS | ST waves 1–4 for AE1.1–1.3; wave 2 |
| 2 | `lawn-action-base` | AE2.1–AE2.4 | XS, M, M, S | wave 1 up to AE1.3 |

10 tasks. None is L, and none goes over five files.

## Checkpoints (review points, not gates)

- **Checkpoint 1 — battle reads the action** (map Checkpoint 1): no production call of `LiveAtk(` on a
  damage path (guard); two actions of different effective rung on one attacker deal different base
  damage; cost and base use one resolver; the goldens are re-blessed once, in H1 order.
- **Checkpoint 2 — the lawn reads the action** (map Checkpoint 2): for the same action at the same `Θ`,
  the lawn's rider amount equals the battle base; a `Θ` refresh rebinds live grants in the drain; an
  instakill hit does not ride the rider; the live probe passes per `live-probe-standard.md`.

Together these are the parent's **CC3**.

## Cross-program edges

| Edge | With | Kind |
|---|---|---|
| `ST2.3` → `ST1.3` → **AE1.5** → `SP` C1 fix → `SP` 6.1 | action-skill-tiers, species-progression | **H1** |
| `EffectiveRungOf` instance resolver (AE1.2 or `ST2.5`, whichever lands first) | action-skill-tiers | shared seam |
| `action-base` row of the version-agreement guard is `ST5.4`, after AE2.2 | action-skill-tiers | soft |
| Content that grants an `atk` `stat.modify` is listed by id in AE1.4 and handed to `SE1.6` | solid-enforcement | handoff, not a dependency |
| Deleting `LiveAtk`, `Setup.Atk` and the `atk` channel; retiring AE1.4's one-line guard allowlist | solid-enforcement `SE1.7` | downstream |
| A **held** skill reads its effective rung in production only after action `T74` (A33) and `T62` (A26). Before that it reads the authored rung (the window ceiling) | action | not a blocker (map "Cross-program") |
| The stronger held action wins tag ties: action `T67` (A31) | action | not a blocker |
| The zombie side's `Θ` source changes when `SE` save-identity lands. One more trigger row is written with that build | solid-enforcement (save-identity) | named future edge (spec, R3) |
| Switching the basic attack **on** mid-match binds nothing for actors already on the board (an existing key-set gap) | lawn-combat-wire | reported, not built here |
| The `action-base` retune uses the A20 synthetic-loadout sweep once holder wiring (`T74`) lands | action | the event that tunes it later |

## Tuning publishes owned (parent §5, row `action-base`)

| Version | Task | How |
|---|---|---|
| `action-base` v1 | AE1.1 | Authored once, as the first version of a new domain. `_meta` says it is **untuned**, names the event that will tune it (the A20 sweep after `T74`), and records how the first value was measured. Every later change goes through `publish.py action-base …` → v{n+1} |

This plan publishes no `action-rungs` version. It reads `qPowerMilli`, which is identical in v1–v4.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| The goldens move by a balance swing as well as the re-bless | AE1.1 calibrates the basic base so that base × `P(20)` sits near the median `Setup.Atk` of the golden actors. AE1.4 re-checks that value if ST2 or ST1 moved a golden |
| Two causes end up in one re-bless | AE1.5 depends on `ST1.3`. If both land in one working tree, the later one rebases and re-blesses separately |
| A siege or lent held row resolves rung 0, so a skill is priced as rung 0 | AE1.2 reads the fallback from the held row, and the result is byte-identical for catalog actions. A skill whose rung has no row throws, naming it |
| The injector hub is left unconfigured, so the lawn base is silently zero (the 2026-09-14 swing-charging incident) | AE2.2 configures it in `RpgHost` and adds an "unconfigured throws" test. `ST5.4`'s guard holds both hosts to one version |
| Grant calls run off the Unity main thread | AE2.3: the snapshot path only records, and the drain rebinds. A test proves `MarkThetaDirty` makes no grant call |
| The live probe is "proven" through a debug-bound grant | AE2.4 reads `Θ` through the RPG Server's normal path and uses real injector telemetry, as `live-probe-standard.md` requires |
| `Injector.Tests` are not in CI | AE2.3 runs them locally, and the injector build is part of AE2.2/AE2.3's verify (`deploy-play.ps1 -NoServer`) |

## Defaults shipped behind (no gates)

- `basicAttack.basePowerMilli` ships **stated untuned** at the calibrated value, and the A20 sweep tunes
  it later.
- Until `T74`, every production skill reads the authored rung (the A23 fallback). Base and cost stay
  paired because they share one resolver.
- A multi-hit split of the base is out of scope. It is a named follow-up for whoever authors multi-offset
  content (`ActionRunner.cs:226-233`).
