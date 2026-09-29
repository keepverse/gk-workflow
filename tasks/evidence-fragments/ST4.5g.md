# ST4.5g — bounds for the two pricing findings (F1, F2): neither can move the scalar

**Status: bounded, neither moves `recommendedReferencePower`. Both recorded as follow-ups for the power
program (`spec-power-vector` owner).** Manager: *"before I commit the ST4.5 reading I must know whether
either moves recommendedReferencePower=1512 ... Bound BOTH the way you bounded the pools, from real data
on the published DB (read-only)."*

## The answer in one line

Both findings touch **the same single atom in the whole 417-atom catalog** — `atom.fx-overlay-damage.t1`,
owned by **`act.attack` (rung 1)**. Priced at the one-reference-unit fallback, that action goes from 0 to
**100**, against a rung-1 threshold of **1512**. F2 changes **no** action's price at all, because the only
triggered string-channel atom in the corpus has a conditionality of exactly 1000‰. **Nothing moves.**

## The affected set (read-only, against the published DB)

```powershell
@'
import sqlite3, json
c = sqlite3.connect("file:.../dist/FusionRpg.Server/data/rpg-hot.sqlite?mode=ro", uri=True)
def q(s): return list(c.execute(s))
# F1: event-linked / powerLadder value specs
for r in q("""select atom_id, kind_id, params_json from effect_atom
              where params_json like '%eventField%' or params_json like '%powerLadder%'"""):
    print(r)
# F2: a trigger AND a STRING channel
for r in q("""select a.action_id, a.rung, ea.atom_id, ea.trigger_id, ea.params_json
              from rpg_action a join effect_container_atom ca on ca.container_id=a.container_id
              join effect_atom ea on ea.atom_id=ca.atom_id where ea.trigger_id is not null"""):
    print(r)
'@ | python -
```

```
F1:  atom.fx-overlay-damage.t1 | resource.delta
       {"amount":{"eventField":"damage","multiplierMilli":-1000},"channel":"hp"}
     owned by:  ('act.attack', 1, 'atom.fx-overlay-damage.t1')

F2:  r 1 act.attack                 atom.fx-overlay-damage.t1  trig=OnDamageDealt  channel=STRING:hp
     r 7 action.family.academic.004 atom.rotting.t4             trig=OnDamageDealt  channel=none
     r 7 action.family.cactus.001   atom.sporing.t4             trig=OnDamageDealt  channel=none
     r 7 action.family.garlic.001   atom.withering.t4           trig=OnDamageDealt  channel=none
     r 7 action.family.garlic.001   atom.venomous.t4            trig=OnDamageDealt  channel=none
     r 7 action.family.garlic.002   atom.venomous.t4            trig=OnDamageDealt  channel=none
     r 7 action.family.hypno.001    atom.mesmerizing.t4         trig=OnDamageDealt  channel=none
     r 7 action.family.pea.001      atom.sporing.t4             trig=OnDamageDealt  channel=none
```

**F1 has exactly one owner and F2 has exactly one string channel**, and they are the same atom. Every
other triggered atom carries **no** `channel` param, so it takes the `CostFunction.Price` path where
conditionality is already applied — F2 is a no-op for it.

## Rung thresholds — the realized power each rung needs to push the scalar above 1512

`threshold(r) = ceil(1512 × poolRolls × qPowerMilli / 1000)`, from `gk-core/data/tuning/action-rungs.v3.json`:

| rung | poolRolls × qPowerMilli | threshold |
|---|---|---|
| 1 | 1 × 1000 | **1512** |
| 4 | 1 × 2315 | **3501** |
| 7 | 2 × 5359 | **16206** |
| 10 | 3 × 12407 | **56279** |

**Sanity check on the setter, which the arithmetic reproduces exactly.** `action.general.0004` (rung 4)
prices through `stat.modify`/`zombieSpeed` → the channel-less coefficient row (1000‰, referenceScale 10):
its `amount` 23–47 means magnitude **35** → normalised **3500** → points **3500**. So its **realized is
3500**, giving implied `floor(3500×1000/2315) = 1511` and ceiling `ceil(…) = **1512**` — the reading's own
numbers. (The manager's "realized 1511" is the *implied*; the realized is 3500, exactly one point below
its rung's 3501 threshold.) That correspondence is what makes the thresholds below trustworthy.

## F1 — `MeanMagnitude` reads 0 for event-linked specs

Priced at the documented one-reference-unit fallback, `act.attack`'s atom is magnitude 1 instead of 0:
`channel "hp"` is a **string**, so it goes through `Compose`'s channel accumulation →
`Find("resource.delta","hp")` resolves the channel-less row (1000‰, referenceScale 10) →
`DivRound(1 × 1000, 10) = 100` → `MulMilli(100, 1000) = 100` points.

**`act.attack`: realized 0 → 100. Its rung-1 threshold is 1512.** Implied 100, ceiling 100 — two orders of
magnitude short. **No crossing, and no other action is affected.**

## F2 — `Compose`'s string-channel path skips `Conditionality`

**The setter is not overpriced.** `action.general.0004`'s only atom is `atom.tempo-surge.t2` with
`when: {}` — a **triggerless** atom. `Conditionality` returns 1000‰ for a triggerless atom by its own
early return, so the skipped factor is the neutral value and the string path and the `Price` path give the
**same** number. F2 cannot be inflating the setter.

**And F2 changes no other action either.** The only triggered string-channel atom is `act.attack`'s, and
its conditionality is exactly neutral: `chance` is absent → 1000; `OnDamageDealt` is 60/min (now seeded)
→ `DivRound(60×1000, 60) = 1000`; no `icd_ms` → `IcdFactorMilli(0, 60) = 1000`; one target → 1000; no
predicate → 1000. `CombineMilli` of all four is **1000**.

**So the resulting `recommendedReferencePower` if F2 were fixed is unchanged: 1512.** Even F1+F2 fixed
together (which is the only way either shows up) leaves `act.attack` at 100.

## Disposition

Neither bound shows the scalar moving, so per the ruling the fixes are **not** in scope here:

- **Follow-up 1 — `MeanMagnitude` prices an event-linked `ValueSpec` at 0.** Owner: the power program
  (`spec-power-vector`). It understates every overlay-driven atom, `fx.overlay_damage` being the shipped
  one. Bound: +100 realized on rung 1, ceiling 100, vs a 1512 threshold — it cannot reach the scalar even
  if every affected action were the only one on its rung.
- **Follow-up 2 — `Compose`'s string-channel path skips `Conditionality`.** Owner: the same program. On
  this corpus it is inert (one atom, neutral conditionality); what it would do on future content is
  over-state a triggered atom that has a concrete channel — the opposite direction from F1, which is why
  the two are one finding about `Compose` and `Price` disagreeing rather than two price bugs.

Both are named here, both are bounded, and neither blocks `v4`.
