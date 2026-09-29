# Spec: `regen-unit-trace` (lawn-tuning-profile module 1)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) · **Ideal:**
[lawn-tuning-profile-ideal.md](../lawn-tuning-profile-ideal.md) (defect M3) ·
**Depends on:** nothing · **Unblocks:** `lawn-resource-scale`
**Status:** spec, 2026-09-16. Not built.

## Objective

Settle, in writing and in a test, what unit the aptitude `resource.regen.*` coefficients were authored
in, and reconcile that with the unit the runtime reads them as. Until this is settled, every number in
`lawn-resource-scale` is sized against a rate whose meaning is unknown — which is how M2 (an aptitude
edge that dwarfs the pool it refills) happened in the first place.

This module is a **trace first**. It may end in a value change, but it is not allowed to start with one.

### What is already known (verified in code, 2026-09-16)

| Fact | Where |
|---|---|
| The runtime channel means **units per tick**, tick = 100 ms | `ResourceChannelReader.RegenPerMilleTick` doc + `BattleModels.TicksPerSecond = 10` |
| The baseline subsystem authors per tick: `regenPerSecond / TicksPerSecond` | `BattleModels.BaseResourceRegen` |
| The reader carries per-mille resolution, and the single `/1000` back to whole units happens at `ResourcePoolState`, which keeps the remainder | `ResourceChannelReader` |
| The POC that fitted the aptitude coefficients accrued `regen × rounds` — a **round**, not a tick | `gk-core/tools/CombatSim/ActionEconomy.cs:113-117` |
| `aptitudes.v8.json` was "ported verbatim from `gk-core/tools/CombatSim/tuning/aptitudes.v1.json`, this program's own POC" | `gk-core/data/tuning/aptitudes.v8.json` `_meta.status` |
| A basic attack is 150 wind-up + 50 recovery **ticks** | `gk-core/data/tuning/action-timing.v1.json` |

So the arithmetic that has to be either confirmed or refuted is: a coefficient fitted per **round**
(~200 ticks for a basic attack) is being applied per **tick**, which would make the aptitude half of
sustain about **200× larger than it was fitted to be**. That is the same order as the measured M2
symptom (a clean actor regenerates 0.2/tick; three points take it to 29.2/tick against a pool that
also grew).

⚠️ This is a **hypothesis with a number attached**, not a finding. The module's first task is to prove
or disprove it against the POC's own harness, not to assume it.

## Tech stack

C# (`FusionRpg.Core`), the existing `gk-core/tools/CombatSim` POC, `data/tuning/aptitudes.v{n}.json` published
through `gk-core/tools/tuning/publish.py`. No new dependency.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ResourceSubTickRegen|BattleResourceSeed|AptitudeRead"
dotnet run --project gk-core/tools/CombatSim -- <the POC's own economy scenario>
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
python gk-core/tools/tuning/publish.py aptitudes <dotted.key>=<value>      # ONLY if the trace proves a change
```

## Project structure

| What | Where |
|---|---|
| The trace itself (the deliverable) | `docs/architecture/lawn-tuning-profile/regen-unit-trace.md` — a findings note, committed |
| The unit assertion | `gk-core/tests/FusionRpg.Core.Tests/Stats/ResourceRegenUnitTests.cs` (new) |
| A value change, only if proven | `gk-core/data/tuning/aptitudes.v9.json` via `publish.py` |

## Code style

The unit belongs in the type's own doc comment, next to the number, in the same voice
`ResourceChannelReader` already uses:

```csharp
/// <summary>Regen in units per TICK (100 ms), never per round and never per second. An aptitude
/// coefficient authored per round is 200× this at a basic attack's cadence — see
/// docs/architecture/lawn-tuning-profile/regen-unit-trace.md.</summary>
```

## Testing strategy

The guard validates the **contract**, never a population or a balance reading
(`validation-ssot.md`):

- ✅ Assert that one authored unit of `resource.regen.{id}` accrues exactly one unit over ten ticks
  (the tick/second contract), for every resource id in the closed six-resource vocabulary.
- ✅ Assert the per-mille round trip: `RegenPerMilleTick` × ticks ÷ 1000 equals the authored rate with
  the remainder carried, not truncated per tick.
- ✅ Assert that the POC harness and the runtime agree on accrual over the SAME wall-clock interval —
  that is the reconciliation, expressed as a test rather than as prose.
- ❌ Never assert a specific `kMilli`, a pool size, or how many ticks an exhausted actor takes to
  recover. Those are readings a balance pass moves.

## Boundaries

- **Always:** state the unit at every seam the number crosses; keep the trace committed next to the
  change; treat the POC file as a frozen reference copy, never edit it to fit.
- **Ask first:** nothing in this module blocks on an owner answer. If the trace proves the coefficients
  are wrong by a factor, publishing `aptitudes.v9.json` is a balance change that touches **battle as
  well as lawn** — land it alone, measured, and say so in its own commit.
- **Never:** hand-edit `aptitudes.v{n}.json` in place (publish `v{n+1}`); change `TicksPerSecond`
  (structural, its own doc comment says why); "fix" the mismatch by scaling in the lawn profile — that
  would leave battle reading the wrong unit and hide the defect one layer down.

## Numeric types

Per-mille rates stay `long` (`ResourceChannelReader` already rounds to `long` at the boundary, and
`checked`). The accrual remainder stays where it is, in `ResourcePoolState`. No new magnitude is
introduced by this module, so no new range decision is needed.

## ActorHub gate

This module **consumes** Hub output only (`resource.regen.*` off the composed snapshot). It adds no
subsystem, no private fold, and no second composer.

## Success criteria

1. `docs/architecture/lawn-tuning-profile/regen-unit-trace.md` states, with file:line, what unit the
   POC fitted, what unit the runtime reads, and whether they agree.
2. A test in `FusionRpg.Core.Tests` fails if the tick contract is ever changed silently.
3. If the two units disagree, exactly one of these is true and is written down: the coefficients are
   republished as `aptitudes.v9.json` with the conversion applied, **or** the trace proves the runtime
   reading is the intended one and M3 is closed as "no defect, the POC was the odd one out".
4. Battle's own measured behaviour is stated either way — a value change here moves battle too, and
   that must be an observed consequence, not a surprise.

## Open questions

None. The one question this module exists to answer is a measurement, not an owner decision.
