# ST4.5a — the suspicious zeros in the ST4.5 reading, diagnosed against the real published DB

**Status: diagnosed. No commit to the pricing path; the two causes are outside this lane's fence.**
Manager's ask: *"for each zero-priced action say whether it is genuinely powerless (e.g. act.attack /
utility) or has unresolved atoms. If unresolved atoms exist, that is a real defect: make it loud (a
finding, never a silent 0) with a test, and fix the cause if it is in this lane's code."*

**Answer: no unresolved atoms exist.** The zeros come from two other silent-0 paths, neither of them in
lane A's code. Because the mechanism is outside this lane's `paths` fence, the fix is a manager ruling,
not an unattended edit — this fragment is the proof and the ask.

## Method

Read-only against the owner's published DB (`dist/` of the main checkout; never written, no server
started or stopped), plus the source paths that price it.

```powershell
@'
import sqlite3
DB = "file:D:/Works/source/plant-vs-zombie-rise-of-summoner/dist/FusionRpg.Server/data/rpg-hot.sqlite?mode=ro"
c = sqlite3.connect(DB, uri=True)
def q(sql): return list(c.execute(sql))
print("actions total:", q("select count(*) from rpg_action")[0][0])
print("enabled=0:", q("select count(*) from rpg_action where enabled=0")[0][0])
print("empty container_id:", q("select count(*) from rpg_action where container_id is null or container_id=''")[0][0])
print("container row MISSING:", q("select count(*) from rpg_action a left join effect_container c on c.container_id=a.container_id where a.container_id is not null and a.container_id<>'' and c.container_id is null")[0][0])
print("container with ZERO atoms:", q("select count(*) from rpg_action a join effect_container c on c.container_id=a.container_id left join effect_container_atom ca on ca.container_id=c.container_id where ca.container_id is null")[0][0])
print("actions naming MISSING atoms:", q("select count(distinct a.action_id) from rpg_action a join effect_container_atom ca on ca.container_id=a.container_id left join effect_atom ea on ea.atom_id=ca.atom_id where ea.atom_id is null")[0][0])
print("distinct missing atom ids:", q("select count(distinct ca.atom_id) from effect_container_atom ca left join effect_atom ea on ea.atom_id=ca.atom_id where ea.atom_id is null")[0][0])
print("container atoms disabled=0:", q("select count(*) from effect_container_atom ca join effect_atom ea on ea.atom_id=ca.atom_id where ea.enabled=0")[0][0])
'@ | python -
```

Result:

```
actions total: 18
enabled=0: 0
empty container_id: 0
container row MISSING: 0
container with ZERO atoms: 0
actions naming MISSING atoms: 0
distinct missing atom ids: 0
container atoms disabled=0: 0
```

`PriceContainer`'s `.Where(a => a is not null)` therefore drops **nothing** on this data, and every
`GetContainer`/`GetAtom` resolves. The manager's hypothesis is disproven for the real corpus: these
zeros are not unresolved atoms.

Second read — the table the pricing reads, and the shape of every atom a container names:

```powershell
@'
import sqlite3
DB = "file:D:/Works/source/plant-vs-zombie-rise-of-summoner/dist/FusionRpg.Server/data/rpg-hot.sqlite?mode=ro"
c = sqlite3.connect(DB, uri=True)
def q(sql): return list(c.execute(sql))
print("power_trigger_frequency rows:", q("select count(*) from power_trigger_frequency")[0][0])
print("power_coefficient rows:", q("select count(*) from power_coefficient")[0][0])
print("power_predicate_frequency rows:", q("select count(*) from power_predicate_frequency")[0][0])
for r in q("select ea.trigger_id, count(*) from effect_container_atom ca join effect_atom ea on ea.atom_id=ca.atom_id group by ea.trigger_id"):
    print("   trigger used by container atoms:", r)
'@ | python -
```

Result:

```
power_trigger_frequency rows: 0
power_coefficient rows: 34
power_predicate_frequency rows: 0
   trigger used by container atoms: (None, 41) ('OnDamageDealt', 14) ('OnSpawn', 2) ('OnTimer', 1)
```

Third read — every action's atoms, their kind, their trigger, and whether `params.channel` is a string
or a pool object (`select a.action_id, a.rung, ca.seq, ea.atom_id, ea.kind_id, ea.trigger_id,
ea.params_json from rpg_action a join effect_container_atom ca ... order by a.rung, a.action_id, ca.seq`)
produced the 18 actions below.

## The classification — 10 of 18 actions price 0, in two groups

| # | Action | Rung | Its atom(s) | Why it prices 0 | Genuinely powerless? |
|---|---|---|---|---|---|
| 1 | `act.attack` | 1 | `resource.delta`, channel `hp`, `trigger: OnDamageDealt` | Cause 1 | No — an overlay damage atom |
| 2 | `action.general.0005` | 4 | `stat.derived`, channel **pool object** | Cause 2 | No — a pooled resolver channel |
| 3 | `action.family.academic.004` | 7 | `status.apply` (rot), `OnDamageDealt` | Cause 1 | No — a real status application |
| 4 | `action.family.cactus.001` | 7 | `status.apply` (spore), `OnDamageDealt` | Cause 1 | No |
| 5 | `action.family.fruit.001` | 7 | 2× `stat.derived`, channel **pool objects** | Cause 2 | No |
| 6 | `action.family.garlic.001` | 7 | 2× `status.apply` (wither+poison), `OnDamageDealt` | Cause 1 | No |
| 7 | `action.family.garlic.002` | 7 | `status.apply` (poison), `OnDamageDealt` | Cause 1 | No |
| 8 | `action.family.hypno.001` | 7 | `status.apply` (hypno), `OnDamageDealt` | Cause 1 | No |
| 9 | `action.family.hypno.002` | 7 | `stat.derived`, channel **pool object** | Cause 2 | No |
| 10 | `action.family.pea.001` | 7 | `status.apply` (spore), `OnDamageDealt` | Cause 1 | No |

The 8 non-zero actions are exactly the ones whose atom carries **no trigger** and a **string** channel:
`action.general.0003` (maxHp), `action.general.0004` (zombieSpeed), `action.family.nut.001` (arm2Max),
`action.family.pea.002` (zombieSpeed), `action.species.bucketnutzombie.001` (arm1Max),
`action.species.cabbagepult.001`/`.002` (maxHp), `action.species.cactusblover.001` (defense).

### Cause 1 — every triggered atom prices 0, because `power_trigger_frequency` is empty in the real server

`CostFunction.Conditionality` (`CostFunction.cs:187-213`) is
`CombineMilli(chance, frequencyMilli)` where `frequencyMilli = DivRound(perMinute * 1000, 60)` and
`perMinute = tables.FrequencyOf(trigger)`. `PowerTables.FrequencyOf` returns 0 for an unlisted trigger
(`CoefficientTable.cs:174-176`), `PowerMath.CombineMilli(a, 0) = DivRound(a * 0, 1000) = 0`
(`PowerVector.cs:141`), and `points = MulMilli(basePoints, 0) = 0`. The verdict returned is
`PriceVerdict.Priced` — a zero vector that looks like a legitimate price, so nothing flags it.

The table is empty because of how the table pair loads (`RpgStore.Power.cs:61-72`):

```csharp
var coefficients = ReadCoefficients(db, "power_coefficient");
if (coefficients.Count == 0) return PowerTables.Authored();   // <- the ONLY path that has frequencies
return new PowerTables(coefficients, ReadFrequencies(db), ReadPredicateFrequencies(db));
```

`PowerTables.Authored()` (`CoefficientTable.cs:240-247`) is the only place the five trigger rows live
(`OnDamageDealt 60`, `OnDamageTaken 40`, `OnSpawn 4`, `OnDeath 6`, `OnTimer 12`). Nothing else ever
writes `power_trigger_frequency`:

- the coefficients seed's writer re-reads and re-writes the stored frequency rows
  (`RpgStore.Power.cs:172`), so it preserves them — but never authors any;
- `gk-data/packs/fusion/data/seed/power/coefficients.v1.json` **cannot** carry them: `AtomSeedFile.cs:584` accepts
  `atom | container | affix | curve | rarity | element | element-matrix | power-coefficient`, with no
  frequency kind;
- the published DB holds 34 coefficient rows (this seed) and **0** frequency rows.

So: the moment the coefficients seed imports, `coefficients.Count != 0`, the `Authored()` fallback is
skipped, and the frequency table comes back empty. Every triggered atom in the game — items and atoms
included, not just actions — prices 0 on any DB-backed server. This is the identical DB-fallback-bypass
defect the seed file's own `arm1` row already documents for the *coefficient* table
(`coefficients.v1.json`, "SILENTLY UNPRICED in any DB-backed pricing path"); the frequency half was
never closed with it. `CoefficientTable.Find`'s own doc names the class: *"A missing coefficient
silently pricing at zero is how a whole family becomes free."*

### Cause 2 — an atom whose `channel` is a pool reference prices 0, because the pool catalog is never supplied

`ActorPowerCache.Compose` (`ActorPowerCache.cs:68-78`) treats a channel as a channel only when
`params.channel` is a JSON **string**; a pool object falls through to `CostFunction.Price(atom, t)`
with no `lookupPool`, which returns `PriceVerdict.No("… channel is a pool reference and no pool catalog
was supplied to price it")` (`CostFunction.cs:65-67`). `Compose` then does `if (priced.Ok) total += …`
and drops the verdict, so an explicitly *unpriced* atom contributes 0 with no trace.

`RpgStore` cannot supply a pool catalog today: there is no `channel_pool` table and no reader anywhere
in `FusionRpg.Data` — the gap `SeedContentCoverageTests.cs:37-48` records as a known pre-existing one
(`gk-data/packs/fusion/data/seed/channel-pools/pools.v1.json` is authored, and `SeedContent.ChannelPools` is never imported).
`ContentValidation.Budget` prices the same way, so A-G1's check and the report agree at 0 by
construction (contract 1 is intact) — they are consistently wrong together.

## Corroboration: the rung shape this predicts is the rung shape the manager measured

| Rung | Actions | Predicted | Manager's live reading |
|---|---|---|---|
| 1 | `act.attack` | n=1, all 0 → min=p50=p90=max=0 | `n=1 max 0` ✓ |
| 4 | general.0003, .0004, .0005 | n=3, one 0 → min 0, p50/max > 0 | (max sets `recommendedReferencePower 1512`) ✓ |
| 7 | 10 actions | 8 zeros + 2 positives → min 0, **p50 0**, p90/max > 0 | `n=10 p50 0` ✓ |
| 10 | 4 actions | n=4, all positive → min > 0 | not flagged ✓ |

The prediction matches the measured report on every rung the manager named, which is what makes the two
mechanisms the explanation rather than a hypothesis.

## Correction 2026-09-19: `act.attack` is a THIRD cause, and the frequency count is 6, not 7

The table above puts ground 1 (`act.attack`, rung 1) under Cause 1. That is wrong, and the counting
follows from it: the reading is **6 frequency + 3 pooled + 1 overlay**, not 7 + 3.

`act.attack`'s one atom is `atom.fx-overlay-damage.t1` — `resource.delta` with
`params.channel: "hp"`, a **string** channel. `ActorPowerCache.Compose` prices a string channel through
its `byChannel` accumulation, which **never calls `CostFunction.Price` and never applies
`Conditionality` at all**, so no missing frequency can reach it. Its zero comes from the magnitude
instead: `AtomJson.TryReadValueSpec` accepts the event-linked form
(`{"eventField":"damage","multiplierMilli":-1000}`) and returns it as `ValueSpec(0, 0, Fixed,
EventField:…, MultiplierMilli:…)` — `Min = Max = 0` — so `MeanMagnitude` reads **0** rather than taking
the "one reference unit" fallback it documents for exactly this case ("a shield whose amount rides the
overlay"). `ChannelRefJson`/`KindId` are `resource.delta` + `hp`, which `Find` resolves through the
channel-less row, so the coefficient is not the problem either.

Consequences, both recorded rather than fixed (neither is in this lane's fence, and both are price
movements a manager should rule on):

1. **`MeanMagnitude` prices an event-linked overlay amount at 0**, not at the reference unit its own doc
   promises. That understates every overlay-driven atom (`fx.overlay_damage` is the shipped one), and it
   is invisible for the same reason Cause 1 was: the verdict is `Priced`.
2. **`Compose`'s string-channel path ignores conditionality entirely** — a triggered atom with a concrete
   `channel` string is priced as if unconditional, which *over*-states it, while the same atom on the
   `Price` path would apply chance × frequency × ICD × targets. So `Compose` and `CostFunction.Price`
   disagree about triggered atoms, in opposite directions for the two shapes.

The rung shape this correction predicts is still the rung shape the manager measured — rung 1 is n=1 and
0 either way, and rung 7's eight zeros are 6 status.apply + 2 pooled — so nothing else in the diagnosis
moves.

## Consequence — the ST4.5 reading cannot be used as R8's source

R8 makes the first reading the value `action-rungs.v4.json` is published at, and ST5.2 publishes it with
`--mark-tuned` in one commit (H7). This reading prices **10 of 18** actions at 0, at least 3 of which
are provably not powerless, so the implied scalar is systematically **understated** — publishing v4 from
it would set the rung budgets below real content and start rejecting actions nobody intended to reject
(the very outcome ST5's contract 4 forbids). ST4.5's own acceptance (*"a reading of implied
`referencePower` per rung exists for the real imported catalog"*) is met only in the sense that a file
exists; the number in it is not the corpus's.

## Why this stops here rather than being fixed in this lane

Both causes live outside this lane's `paths` fence, so neither is an unattended edit:

- Cause 1 needs `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Power.cs` (the fallback must also cover an empty
  frequency table) and/or `gk-data/packs/fusion/data/seed/power/**` plus a seed kind able to carry frequencies
  (`AtomSeedFile.cs`/`SeedKind`) — none of those paths are in `summoner-convergence-impl-20260918`.
- Cause 2 needs a channel-pool source in `FusionRpg.Data` plus wiring in `PriceContainer`, again
  outside the fence.

Ran the strongest check that is achievable from inside the fence: the exhaustive read-only query above
over the real DB, plus the code-path proof, plus the rung-shape corroboration. **Asking the manager for
a ruling**: (a) whether the frequency-table fix is lane A's to make (which would mean widening this
session's `paths`), and (b) whether ST4.5's acceptance is amended to *"the reading is taken after the
trigger-frequency table is populated, and no priced action is 0 without a named cause"*.

## Commands

```powershell
# the two diagnostic reads above (read-only; no server start/stop, no write)
@'…'@ | python -      # see Method — sqlite3 against rpg-hot.sqlite with uri=True and mode=ro
dir /b "D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-lane-a-ds\data\seed"
dir /b /s "D:\Works\source\plant-vs-zombie-rise-of-summoner\dist\FusionRpg.Server\data\seed"
```

`dist/FusionRpg.Server/data/seed` holds `actions`, `dungeon`, `items`, `loot`, `structures`; the repo's
`gk-data/packs/fusion/data/seed` holds 22 folders, `power` among them — the coefficients reach the server through
`SeedImportRunner.FindUp` walking up out of `dist/` into the repo, which is also why the dev deployment
and a player install disagree about which power tables load.
