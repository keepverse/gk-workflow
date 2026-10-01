# Spec: `specimen-respec-price`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave A** · depends on: nothing.
**Scope: every unique creature, the commander included.** The id says "specimen" because a specimen is a
unique creature; the module prices re-allocation for both allocation scopes a unique creature's points
live in: `UniqueCreature` (a specimen's own points) and `Commander` (the commander's pool).
**Rulings honoured:** R18 of [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md): *"A unique
creature (specimen) always pays to respec… **A commander is a unique creature, so a commander respec is
paid too** (the owner, correcting a first reading that kept it free: 'commander is unique creature, it
pays for respec'). Only the empire respec draws on earned free respecs. Presets still charge exactly the
by-hand price."* Also consistent with `decisions.md` — 'Class system (2026-08-26)' (Class system): *"respec is available,
unlimited, and priced in a resource fighting also costs."*
**Status:** spec, not reviewed, no build authorized.

## Objective

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


Re-allocating a unique creature's points, or the commander's, is free today. A build preset would make
that free re-allocation one click, which turns a build into a menu selection. R18 prices it: taking
points back out of an aptitude costs souls, through the **same** price function the species respec uses,
never a second curve.

What ships today, read in code:

| Piece | Where |
|---|---|
| Commander re-allocation: budget check, then a plain `SaveAllocation`, no price | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:29-55` (write at `:51`) |
| Specimen re-allocation: the same, no price | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:64-94` (write at `:89`) |
| Preset activation writes commander and unique allocations free | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:374-391` |
| `SaveAllocation` is a full upsert-and-prune of one `(scope, scopeKey)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:72-89` (method at `:76`) |
| The one respec price function, souls, linear in a churn count, `checked` | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs:23-48` |
| Why souls: `spec-species-respec.md` decision 1, recorded in the policy's own doc comment | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs:14-16` |
| The species churn counter and its decay-on-read | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:31-72` (`DecayedRespecCount` at `:66`) |
| The species spend: replay check, balance check, soul-ledger debit, counter bump, in one transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:198-243` |
| The soul-ledger respec reason | `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:79` |
| The commander pool's key is `player:{id}` | `gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:68-70`; `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:123` |
| A non-player writer: the derived-audit debug seed writes both scopes directly | `gk-core/src/FusionRpg.Server/DerivedAuditActor.cs:50-51` |

## Design

### What counts as a respec

```csharp
// gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs
/// A re-allocation is a respec when it takes points back: some aptitude holds fewer points in
/// `proposed` than in `current`. Spending unspent points is not a respec.
public static bool IsRespec(AllocationScope scope, AptitudeAllocation current, AptitudeAllocation proposed);   // (new)
```

- **Adding points is free.** Spending points a level-up granted, or a first allocation, only raises
  aptitudes. Nothing is taken back, so nothing is priced. This matches the species rule that a first
  override is free (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:168-173`).
- **`current` is the stored explicit allocation, never a computed default.** A specimen with no explicit
  allocation reads a default at read time (`default-build`, map D1). Its first explicit allocation starts
  from Empty, so it is additions only and free. That is `default-build`'s *"replacing a default is not a
  respec, because nothing was spent"*, which this module keeps.
- **Clearing is a respec.** Returning to Empty takes points back, so it is priced. Otherwise clear-then-
  allocate would be a free respec, the bypass the species path's "ever touched" marker exists to stop
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:44-47`).

### One price function, re-typed to take its parameters

`PriceOf` keeps its formula and its `checked` arithmetic. It stops taking the whole species tuning
record and takes only the three numbers it reads:

```csharp
public sealed record RespecPriceTuning(long BasePrice, long EscalationPermille, int DecayDays);   // (new)

public static RespecPrice PriceOf(RespecPriceTuning tuning, long count);          // was (SpeciesBuildTuning, long)

public readonly record struct RespecQuote(RespecPrice Souls, long FreeStock)      // (new)
{
    public bool FreeAvailable => FreeStock > 0;
}
public static RespecQuote Quote(RespecPriceTuning tuning, long effectiveCount, long freeStock);  // (new)
```

`SpeciesBuildTuning` exposes two views, `SpeciesRespec` and `UniqueRespec`, each a `RespecPriceTuning`.
The species price is byte-identical after the re-type: the existing `SpeciesRespecTests` prove it
unchanged. **There is one formula, one quote and two parameter sets.** Two parameter sets are not two
curves; they are the same line with a different base, so a balance pass can price a single creature
differently from a whole species without touching code (tunables-ssot's "both readings defensible → tunable").

Every quote a unique-creature respec produces passes `freeStock: 0`. R18 is explicit that only the empire
respec draws on earned free respecs; `respec-free-counter` is the one caller that passes a real stock.

### The counter: one per specimen, one per commander pool

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


```sql
CREATE TABLE IF NOT EXISTS rpg_allocation_respec (      -- (new)
  scope           TEXT    NOT NULL,     -- 'uniqueCreature' | 'commander'
  scope_key       TEXT    NOT NULL,     -- the instanceId, or the commander pool key
  count           INTEGER NOT NULL,
  last_respec_utc TEXT    NOT NULL,
  PRIMARY KEY (scope, scope_key)
);
```

- **Keyed by the same `(scope, scope_key)` the allocation row uses**, so the counter follows exactly what
  was re-allocated. A specimen's key is its `instance_id`, which is unique across saves. The commander
  pool's key already carries the save (`player:{save}`, `CommanderId.cs:68-70`); `save-identity` keeps the
  string and only re-types its encoder to take an `EmpireRef`.
- **A creature commander is priced as a specimen.** Once `commander-roster` lets a unique creature lead,
  that creature's own points are its `UniqueCreature` allocation, priced by its own counter. The
  `Commander` pool is the empire's side-wide pool (ruling R4), priced by its own counter. Two counters for
  two allocations; no allocation is priced twice.
- **Decay:** the existing `DecayedRespecCount` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:66`),
  a static on the same `RpgStore` partial, reused as is with `UniqueRespec.DecayDays`.
- **Why not reuse `rpg_species_respec`.** Its key is `(player_id, species_id)` and its row doubles as the
  "ever overridden" marker that species semantics need (`:44-47`). A specimen and a commander pool need
  neither. Folding species into this table is possible later; it is a migration of a working table and
  is not needed for R18.
- A removed specimen leaves a counter row nobody reads. Each row is a few bytes, and a fused or salvaged
  specimen never returns under the same id, so it is not cleaned up.

### The gate: one store method for both scopes

```csharp
// gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs (new)
public sealed record ReallocationOutcome(bool Ok, string Reason, bool Priced, long PriceAmount,
                                         long RespecCount, SoulBalanceDto Balance);

internal ReallocationOutcome TryReallocateUnlocked(SqliteConnection db, SqliteTransaction tx,
    long payerPlayerId, AllocationScope scope, string scopeKey, AptitudeAllocation proposed,
    string? correlationId, DateTimeOffset? utcNow = null);

public ReallocationOutcome TryReallocate(...);                         // own connection + transaction
public RespecQuote QuoteReallocation(long payerPlayerId, AllocationScope scope, string scopeKey,
                                     AptitudeAllocation proposed, out bool isRespec);   // read-only
```

`scope` must be `Commander` or `UniqueCreature`; any other scope throws, because species has its own
gate with its own free rules. Inside one transaction:

1. Read the stored allocation. If `!IsRespec`, save and return `Priced = false`. No counter, no
   correlation id needed.
2. A respec needs a correlation id (`correlation.missing` otherwise).
3. **Replay check first**: a soul-ledger row with this module's reason and `dedupe_key = correlationId`
   returns the original outcome. Same order and reason as the species path (`:198-215`).
4. Decay the counter, `PriceOf(UniqueRespec, effectiveCount)`, check the balance
   (`souls.insufficient`, nothing written).
5. Debit through `AppendSoulLedgerUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139`), bump the
   counter, save the allocation.

Soul-ledger reasons are new, one per scope: `SoulEarnPolicy.Reasons.RespecUnique = "respec-unique"` and
`RespecCommander = "respec-commander"`. A shared reason with the species `respec` would let a correlation
id reused across two gates read as a replay of the other.

**Who pays.** The empire that owns the target, resolved through `save-identity`'s one ownership predicate,
`OwnsSpecimenUnlocked(db, EmpireRef owner, instanceId)` (`spec-save-identity.md` §"Seams this module
provides to consumers"), never from the specimen row's `player_id` alone. After that migration a Zomboss
specimen of the same save carries the same `player_id` (`UniqueActorDto.PlayerId`,
`gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs:15`) as the human's, so reading the payer from it would quote
and charge the human for Zomboss's specimen (`save-identity` cross-program sweep, mismatch 2). The gate
takes the caller's `EmpireRef`; a specimen that empire does not own is refused
(`respec.target.not-owned`), and a non-human empire is refused before any read, because souls are Tier B
and an AI empire has no re-allocation surface, as for species. The commander pool's payer is the human
empire of the save its key names.

**Landing order against `save-identity`.** This module is Wave A and does not wait for `save-identity`.
`rpg_allocation_respec` is Tier B by that spec's own rule (human-empire-only build state, beside
`rpg_species_respec`), so no key changes. If this lands first, `save-identity`'s Tier B signature sweep
(`spec-save-identity.md` §"Project structure", *"Tier B store files … respec …"*) covers
`RpgStore.AllocationRespec.cs` too: its public methods take an `EmpireRef` and refuse a non-human empire.
If `save-identity` lands first, this module is born with that signature. Either way, no SQL change.

### Callers

| Caller | Change |
|---|---|
| `POST /api/aptitudes/allocate` (`gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:29-55`) | budget check unchanged, then `TryReallocate(Commander, …)`. Body gains `correlationId?`. Response gains `priced`, `priceAmount`, `respecCount`, `soulBalance` |
| `POST /api/aptitudes/unique/allocate` (`:64-94`) | the same with `UniqueCreature` and the instance id |
| `POST /api/aptitudes/respec-quote` (new) | `{ scope: "commander" \| "unique", playerId?, instanceId?, shares }` → `{ isRespec, soulPrice, respecCount }`. Read-only, calls `QuoteReallocation` |
| Preset activation, commander and unique branches (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:374-391`) | call `TryReallocateUnlocked` in the activation's transaction, as the species branch calls `TryRespecSpeciesUnlocked`. A respec needs the activation's `correlationId`, which today is required only for species (`:398-402`) |
| `DerivedAuditActor.Seed` (`gk-core/src/FusionRpg.Server/DerivedAuditActor.cs:50-51`) | **unchanged.** An RPG Server Debug fixture that seeds a fresh actor; its writes are first allocations, which are free under this rule anyway. It is the only other allowed writer (test 9) |

Refusal strings reuse the species ones (`correlation.missing`, `souls.insufficient`), so the FE handles
them in one place.

### Build presets

A build preset's aptitude piece prices a commander or unique target through `QuoteReallocation`, and
applies it through the activation branch above. So the preset price for those targets equals the by-hand
price by construction ([`build-preset`](../build-preset-map.md) D4).

### FE contract

- The aptitude sheet (`gk-web/web/fusion-rpg-web/src/ui/actor/AptitudesTab.tsx`) keeps its draft-then-confirm
  flow. On confirm, the host calls `respec-quote`. When `isRespec` is true it shows the soul price before
  saving, and sends a fresh `correlationId` with the save.
- The FE never decides whether a change is a respec and never computes a price. `IsRespec` and
  `PriceOf` exist once, on the server.
- The mutations already in use (`gk-web/web/fusion-rpg-web/src/lib/bus/mutations.ts:254`, `:267`) gain the
  `correlationId` field and the priced response fields in `gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`.

## Seedsmith / generator

**None.** Three tuning keys. `gk-forge/tools/CreatureBuildPlanGen` reads `species-build` for its band values and
ignores these, so its `--check` stays green.

## Tunables

`data/tuning/species-build.v{n+1}.json`, published, never hand-edited:

```powershell
python gk-core/tools/tuning/publish.py species-build --label "R18 unique creature respec price" `
  --add-key ':uniqueRespecBasePrice=50' `
  --add-key ':uniqueRespecEscalationPermille=500' `
  --add-key ':uniqueRespecDecayDays=3'
```

- Souls, per mille, days (tunables-ssot T6). Working values equal the species keys shipped in
  `species-build.v1.json` (`respecBasePrice 50`, `respecEscalationPermille 500`, `respecDecayDays 3`), so
  a specimen re-spec starts at the price a player already knows. Not a balance decision.
- In `species-build` because that file already holds the respec economy and `RespecPolicy` already reads
  its hub (`gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs:90-100`). A missing key is a load
  rejection naming it (T5).
- The three keys are required, so the version they replace stops loading and every pin of it moves in the
  same change, found by search: `rg -l "species-build\.v[0-9]+\.json" src tools tests --glob "*.cs"`. On
  2026-09-18 the v1 pins are `gk-core/src/FusionRpg.Server/Program.cs:153`, `gk-forge/tools/CreatureBuildPlanGen/Program.cs:47`,
  `gk-forge/tools/ProveHubCombat/Program.cs:101`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs:175`
  and `gk-forge/tools/_TempSeedSpecies/Program.cs:121` (its owner decides at build).
- **Version.** This is Wave A, so it normally publishes the first new `species-build` version; the map's
  "Tuning version sequence" table orders every `species-build` publish in this program. If a Wave B publish
  lands first, this takes the next free number. Two modules never claim the same number.

## ActorHub gate

**Not applicable.** A price is an economy number. The allocation it guards reaches Hub through the
existing commander and specimen allocation seams, unchanged.

## Integer widths and the power ladder

`long` for counts and prices; `checked` in `PriceOf` (unchanged). **No level curve, no `Θ` read**: the
price reads a churn count, never a level (decision 15), so no `ssot-power-scale.md` §10 row is involved.
The counter is a bounded churn count, the same PS-8 exemption the species counter states
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:60-65`), and the price never refuses a respec for
its count.

## Commands

```powershell
python gk-core/tools/tuning/publish.py species-build --add-key ':uniqueRespecBasePrice=50' --add-key ':uniqueRespecEscalationPermille=500' --add-key ':uniqueRespecDecayDays=3'
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RespecPolicy|FullyQualifiedName~SpeciesBuildTuning"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationRespec|FullyQualifiedName~SpeciesRespec|FullyQualifiedName~AptitudePreset"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"
dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `data/tuning/species-build.v{n+1}.json` (new) | published |
| `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs` | three keys, `SpeciesRespec` and `UniqueRespec` views |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs` | `RespecPriceTuning`, `PriceOf` re-typed, `Quote`, `IsRespec` |
| `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs` | `Reasons.RespecUnique`, `Reasons.RespecCommander` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs` (new) | schema, gate, quote |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs` | `PriceOf(tuning.SpeciesRespec, …)`; no behaviour change |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs` | commander and unique branches call the gate |
| `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs` | two routes call the gate; `respec-quote` route |
| `gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs` | preview passes `SpeciesRespec` |
| `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/CreatureBuildPlanGen/Program.cs`, `gk-forge/tools/ProveHubCombat/Program.cs` | pin moved |
| `gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`, `mutations.ts`, `queries.ts`, `src/ui/actor/AptitudesTab.tsx` | quote before confirm, correlation id |
| `tests/FusionRpg.Core.Tests/Stats/RespecPolicyTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs` (new) | below |

## Code style

The species path is the style: one pure policy in Core, the Data layer deciding priced-or-not inside the
same transaction as the debit and the write, and the replay check before the price.

## Testing strategy

Prices are read from the loaded tuning and `PriceOf`, never literals.

1. **`IsRespec`.** Additions only → false; any single decrease → true; Empty → anything → false; anything
   non-empty → Empty → true. Property test over random pairs: `IsRespec` is true exactly when some
   aptitude decreases.
2. **Adding is free.** Spending new points, a first allocation, and a first explicit allocation over a
   default each write with no soul-ledger row and no counter row.
3. **Respec is priced.** A decrease charges `PriceOf(UniqueRespec, effectiveCount)`, bumps the counter,
   and the next one costs the next step; after `DecayDays × k` idle days the count has fallen by `k`.
4. **Commander pool.** The same three cases on the `Commander` scope, on its own counter. A creature
   commander's specimen counter and the empire's commander pool counter never move each other.
5. **Replay.** The same correlation id twice charges once and returns the original price.
6. **Refusals write nothing.** Insufficient souls, a missing correlation id on a respec, a specimen the
   caller's empire does not own (a Zomboss specimen of the same save included), and a non-human
   `EmpireRef` each leave the allocation, the counter and the ledger unchanged.
7. **Species unchanged.** Every existing `SpeciesRespecTests` case passes with no edit after the
   `PriceOf` re-type.
8. **Preview equals spend.** For counts in `[0, 3]`, `respec-quote` equals what the save charges.
9. **One writer.** An architecture test: outside `RpgStore.AllocationRespec.cs`, the only callers of
   `SaveAllocation`/`SaveAllocationUnlocked` with `Commander` or `UniqueCreature` are
   `RpgStore.Aptitudes.cs` itself and `DerivedAuditActor.Seed`. Species keeps its own gate. This is the
   contract that stops a free bypass from reappearing.
10. **Preset equals by hand (the gate-level half of one contract).** Activating an aptitude preset over a
    commander or specimen charges exactly what the same change via the route charges: equal soul-ledger
    deltas entry for entry, and equal `rpg_allocation_respec` rows (count and `last_respec_utc` read at the
    same injected clock). `build-preset` `piece-appliers` test 1 asserts the same equality one level up,
    through a whole build preset; neither replaces the other.
11. **No free stock.** No path of this module reads or writes `respec-free-counter`'s stock.

## Boundaries

- **Always:** one price function; decide priced-or-not in the store transaction; replay before price.
- **Ask first:** letting earned free empire respecs pay for a unique or commander respec (R18 says no);
  a different currency; a price that reads a level.
- **Never:** a second price formula; price an addition of unspent points; refuse a respec for its count.

## Success criteria

- [ ] Taking points back from a specimen or the commander pool costs souls through `PriceOf`.
- [ ] Spending unspent points stays free.
- [ ] Preset activation and the by-hand routes charge the same.
- [ ] The species price is byte-identical.
- [ ] `verify-change.py` green; `CreatureBuildPlanGen --check` green.

## Open questions

None. R18 and its correction fixed which scopes pay and that the empire's free respecs do not reach them.

## Self-audit — the debate

- **"Price every save, even pure additions."** Then a level-up forces a payment to spend the points it
  granted, which taxes playing rather than churning. Decision 15 prices churn.
- **"Compare against the default, not the stored explicit allocation."** Then a player could never make a
  first choice for a specimen without paying, because any choice differs from the default somewhere.
  `default-build` already rules that replacing a default is not a respec.
- **"A cheaper price for the commander, since it is the player's own sheet."** The owner's correction says
  a commander is a unique creature and pays. One parameter set for all unique creatures is the plain
  reading; a balance pass can split it with one publish if play shows a reason.
- **"This makes auto-assign expensive."** Auto-assign fills a draft (`aptitude-sheet` E1) and fills unspent
  points; a draft that only adds points is free. A draft that re-distributes spent points is a respec, and
  that is the ruling.
- **"The debug seed bypasses the price."** It is an RPG Server Debug fixture that creates a fresh actor, so
  its writes are first allocations and would be free anyway. It is named in the writer allowlist so that
  any new bypass fails a test.
