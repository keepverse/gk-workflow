# Spec: `rider-default-on` (lawn-playable module 5)

**Program:** [lawn-playable](../lawn-playable-map.md) ·
**Depends on:** `actor-liveness-refresh`, `hub-snapshot-cache`, `rider-hit-cost`,
`summon-pool-integrity`, `exhaustion-event`, **and cross-program on
[`lawn-scale-live-proof`](../lawn-tuning-profile/spec-lawn-scale-live-proof.md)**
**Status:** spec, 2026-09-16. Not built.

## Objective

Flip `LawnBasicAttackFeature.DefaultEnabled` to `true` — and be able to defend it with a number.

⚠️ **Affordable is not sufficient — added by the 2026-09-16 audit.** This module originally depended only
on the cost chain, which would have let the switch default on while a Peashooter still hits for 2,939
and no allocated actor can ever run out of stamina. A player would then meet the RPG layer at its worst:
fast, and wrong. So the flip also gates on `lawn-tuning-profile`'s `lawn-scale-live-proof` — the lawn
must be both affordable and a game before it is on by default.

This is the module the whole program exists for. The RPG combat loop is built and proven live; it is off
because the owner ruled *ship behind the switch, defaulted off* after the isolated A/B measured
**26.73% / 27.22% of the pipeline on vs 0.10% / 0.09% off** at 300 zombies against a 6% ceiling, and
about 37% after L-N36 (`_baseline-lcw-300z-env-*.json`, fps 17.8 vs 31.1–38.6).

That ruling is not reversed by an argument. It is reversed by the same measurement coming back under the
ceiling.

## Tech stack

`FusionRpg.Injector` (`LawnBasicAttackFeature`), `scripts/probe-perf.ps1`, the existing PerfProbe
pipeline-share metric. Plus one tuning file, because a ceiling written in a task list is not a ceiling
anyone can change.

## Commands

```powershell
# the A/B, one fresh process per arm, env set before start — the L-N8 discipline
.\scripts\probe-perf.ps1 -Scenario lcw-300z-env-off-final -DurationSec 60
.\scripts\probe-perf.ps1 -Scenario lcw-300z-env-on-final  -DurationSec 60
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Feature|KillSwitch"
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

## Project structure

| What | Where |
|---|---|
| The switch | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs` |
| The ceiling | `gk-core/data/tuning/lawn-perf-budget.v1.json` (new) |
| Evidence | `docs/research/perf/_baseline-lcw-300z-env-{off,on}-final.json` |
| Verdict | `tasks/lawn-playable-todo.md`, with both files cited |

## Tunables

`gk-core/data/tuning/lawn-perf-budget.v1.json`, owner this spec, published via `gk-core/tools/tuning/publish.py`:

| Key | Meaning | v1 |
|---|---|---|
| `ceiling.pipelineSharePercent` | the share the feature may take at the reference scenario | `6` — the number the program has been measured against since the start |
| `ceiling.referenceZombies` | what "the reference scenario" means | `300` |
| `ceiling.minFpsRatioOfOff` | the on-arm's fps as a fraction of the same scenario's off-arm | `UNMEASURED` — **a required gate, not an optional one** |

The ceiling has lived in a plan document as a proposal. A number that decides whether a feature ships is
a balance-surface number by this repo's own test — *would a pass ever want to change it?* — so it moves
to data here, and the module that reads it is this one.

## The shape

1. **The switch stays.** Defaulting on does not delete the kill switch; a player on a weak machine, and
   any future regression hunt, still needs `FUSIONRPG_LAWN_BASIC_ATTACK=0`.
2. **The flip is a one-line change and a four-file evidence package**: two committed baselines, the
   observer run file, and the verdict line quoting the measured share against the tuned ceiling.
3. **Fail loudly rather than ship a lie.** If the measurement comes back over the ceiling, this module's
   outcome is *"still off, here is the new number and the next lever"* — reported, not reworded. The
   program's value is the first three modules either way.
4. **Two gates, both required — owner ruling 2026-09-16.** Share under the ceiling **and** fps within
   `minFpsRatioOfOff` of the off-arm, on the same scenario. Share alone can pass while the board is
   unplayable for an unrelated reason; fps alone cannot attribute the cost to this feature, which is the
   confusion the isolated A/B was built to end. Today's numbers fail both: share 26.7–37%, fps 17.8 on
   against 31.1–38.6 off.
5. **The reference scenario is fixed and named.** 300 zombies, the same scenario ids, fresh process per
   arm, env set before launch. Anything else is not comparable to the breach that started this.

## Testing strategy

- ✅ With the switch off, behaviour is byte-identical to the pre-program build (the off arm is a
  regression test, not just a control).
- ✅ The feature reads its default from the built value, and a guard asserts the default is stated in
  exactly one place.
- ✅ The ceiling is read from tuning, not a `const` — a guard for that too, since that is the rule this
  module exists to stop breaking.
- ❌ No test asserts the share. It is a reading, produced by `probe-perf.ps1` and committed as a file.

## Boundaries

- **Always:** measure before flipping; commit both arms; quote the number in the verdict.
- **Ask first:** flipping the default **is** the owner-facing decision. The measurement decides whether
  it is *allowed*; the owner decides whether it *happens*, exactly as the original ruling did.
- **Never:** flip it on an argument, a partial window, or a scenario other than the reference one;
  remove the kill switch; re-bless the ceiling upward to fit the measurement.

## Numeric types

Shares and fps are ratios — `double`, allowed (2026-09-15 ruling). No magnitude.

## ActorHub gate

None — this module changes a default and reads a budget.

## Success criteria

1. Two committed 60 s baselines at 300 zombies, fresh process per arm.
2. **Both** gates pass: on-arm pipeline share under `ceiling.pipelineSharePercent`, **and** on-arm fps
   at least `ceiling.minFpsRatioOfOff` of the off-arm's, same scenario.
3. `LawnBasicAttackFeature.DefaultEnabled = true`, with the switch still present and tested.
4. The verdict line in `tasks/lawn-playable-todo.md` cites both files and both numbers.
5. If (2) fails: the module closes as a measured FAIL with the new numbers named — and that is a
   successful outcome for this spec, not a failed one.

## Open questions

None. The owner's flip decision is a gate at the end, not a question at the start.
