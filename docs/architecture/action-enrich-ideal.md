# Action enrichment — attack moves from the actor to the action — the ideal

**Status:** idea phase, 2026-09-18. Not a spec. No build authorized.

**Program:** `action-enrich`. Specs → `docs/architecture/action-enrich/spec-<module-id>.md`; plan →
`tasks/action-enrich-plan.md` + `tasks/action-enrich-todo.md`.

**Scope, as the owner set it (2026-09-18):** *"we already have everything, our damage calculating come
from rpg logic, not pvz engine logic, the action is trigger on rpg logic and calculate damage base on it
base stat multiplier with actor derived stats include power for each element, the basic attack need
resolve element matrix on power for each element (hybrid elements) we already have all formula and
build, just now we remove attack from actor and move to the action instead. This include effect chain
that apply by the action too."*

**Corrected the same day.** A first draft of this doc proposed a five-field stat block (hit count, proc
coefficient, base crit, accuracy offset), a new `deliveryProfile` enum and a seedsmith profile stage.
That was over-scoped: none of it is needed to move attack from the actor to the action, and the owner
rejected it. It is not carried forward. This doc supersedes the shape in
[action-base-stats-ideal.md](action-base-stats-ideal.md) only where they differ; that doc remains the
record of the `atk` retirement.

## The principles that bind this change

- **RPG layer, not PvZ.** Damage resolves in the RPG's own stack (`DamagePacket` → dispatcher →
  shield/`OverlayCombatCalculator` → Funnel → FA10). PvZ supplies a trigger, never the number.
- **One ActorHub compose.** The actor keeps its derived stats — per-element `combat.power.*`, defense,
  crit — composed once in the Hub. Only the flat `atk` leaves the actor.
- **One power ladder.** An action's base is a level-invariant coefficient scaled by `P(Θ)`; no new
  `f(level)`.
- **The balance surface is data.** Every base lives in `gk-core/data/tuning/`; generated seed JSON is never
  hand-edited.

## Which loop this extends

**Combat depth** and **Spine A — Level up and power** (`the-loops.md`): damage grows through one path,
the move's base scaled by the actor, instead of two.

## What already exists

### Built — the whole formula

| What | Where |
|---|---|
| The hit is resolved by the RPG, one calculator for every mode | `OverlayCombatCalculator` |
| Base × the action's effectiveness multiplier | `OverlayCombatCalculator.cs:99`; `BasicAttack.cs:377-378` feeds `skill.effectiveness.{category}` |
| **Hybrid elements**: the base is split across the attacker's element components, each resolved with that element's power and the element matrix | `OverlayCombatCalculator.cs:106-178` (`request.Components`, validated by `ElementPayload.Validate`); components from `attacker.AttackComponents` (`BasicAttack.cs:370`) |
| Actor derived stats, per element | `combat.power.*`, `combat.crit.*`, `combat.accuracy.*` — composed in ActorHub |
| **The effect chain applied by the action** | the action's container fires on `OnDamageDealt` after a landed hit (`BasicAttack.cs:380-400`), and on `OnActivate` for non-attack categories; event-linked magnitudes resolve from the hit (`AtomCompiler.cs:584-592`, `DamagePacketBuilder.cs:63-96`) |
| A legal level-invariant magnitude shape | `powerLadder` `kMilli × P(Θ) / 1000` (`AtomCompiler.cs:596-620`) |
| The rung's power per action | `qPowerMilli` in the loaded rung table (`action-rungs.v1.json` in production today; identical in every version) |

### Wiring gap — the one line

| What | Where |
|---|---|
| **The hit's base is the actor's `atk`** | `BasicAttack.cs:369` `BaseOverlayDamage = attacker.LiveAtk(state.Ledger)`, where `LiveAtk` recomposes `Setup.Atk` (`BattleEngine.cs:101`) |

### Real gap

| What | What to build |
|---|---|
| An action has no base attack number | one base per action, derived deterministically at the hit (below); not stored on the action (`spec-action-base.md`) |

## The shape

```
BaseOverlayDamage = basePowerMilli(action, effectiveRung) × P(Θ_attacker) / 1000     (long, checked, /1000 last)
```

Everything after it is unchanged: effectiveness, the hybrid element split with per-element power and
the element matrix, defense, crit, the effect chain.

**Where each action's base comes from — a deterministic function, per the owner's ruling (*"use
deterministic function to resolve power or regenerate"*):**

| Action | `BasePowerMilli` |
|---|---|
| Skills (rung ≥ 1) | `qPowerMilli` of the holder's **effective** rung (the loaded `action-rungs.v{n}.json`) |
| Basic attack (`act.attack`, rung 0) | `basicAttack.basePowerMilli` in `gk-core/data/tuning/action-base.v1.json` (new) |
| Innate | its rung's `qPowerMilli`, like any skill |

No seed row carries a number, so **seedsmith needs no change**: the seed's `rungBand` bounds the rung,
and the base reads the holder's `effectiveRung` inside it — the magnitude reading of A-U1
(`spec-rung-semantics.md` §3.1), through the same resolver as cost (reconciled 2026-09-18 with
`action-skill-tiers`; see `spec-action-base.md` §Which rung). If a later pass wants authored bases, the regenerate path is the generator,
never the committed JSON.

**What leaves the actor:** `BattleActorSetup.Atk` and `LiveAtk` stop feeding damage. Species
`attackBase` stays a seed-time signal only.

## Tunables

| Number | File |
|---|---|
| `basicAttack.basePowerMilli` | `gk-core/data/tuning/action-base.v1.json` (new) |
| `qPowerMilli` per rung | `data/tuning/action-rungs.v{n}.json`, the loaded version (existing) |

## Known follow-ups, named not scoped

- **Multi-hit.** `ActionRunner.cs:226-233` makes each resolve offset one full hit that also fires the
  effect chain. No content emits more than one offset today; whoever authors multi-hit content splits the
  base across hits.
- **Visibility.** `action` A26 (unlock tuning never loaded at startup) and A31 (alphabetical tiebreak,
  `ActionTagPreference.cs:47`) decide whether a stronger move is ever held and fired — and holders are
  not wired into production battles at all (`unlockStateFor` has no production caller; no A-task owns
  it — map §Cross-program).
- **Goldens** move when `atk` stops feeding damage; one re-bless for this cause, ordered after
  `action-skill-tiers` ST2 and ST1 (map §Golden re-bless order).

## The lawn — already on the basic action

**Built (lawn-combat-wire T10, `62ec0b9ee`, fixes through `0fb86c9dc`).** Every lawn actor gets the
`act.attack` effect grant at spawn (`BasicAttackGrantBuilder.cs`, effect `fx.overlay_damage`), with a
hybrid element payload from its own species element (`HybridPayload.BuildOverlay`). The lawn hit is
therefore resolved by the RPG through the basic action already.

**The one input that moves with this change:** the lawn grant's magnitude reads the hit event's amount
(`{"eventField":"damage"}`, `gk-data/packs/fusion/data/seed/atoms/fx-core.json:40`). Under the owner's ruling (*"remove attack
from actor and move to the action"*) it reads the action's base instead, so the same move deals the same
damage on the lawn and in battle. No open question remains.
