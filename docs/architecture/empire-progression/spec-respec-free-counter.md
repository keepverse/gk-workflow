# Spec: `respec-free-counter`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave D** · depends on:
[`empire-level`](spec-empire-level.md) (the grant), [`specimen-respec-price`](spec-specimen-respec-price.md)
(`RespecPriceTuning` and `RespecPolicy.Quote`); external `solid-enforcement`
[`save-identity`](../solid-enforcement/spec-save-identity.md) (`EmpireRef`).
**Rulings honoured:** R18 of [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md): *"The empire
respec (species scope, empire progression) is priced, but its free respecs are EARNED — one grant per
empire level-up — replacing the fixed `respecFreeCount` 25; at each empire respec the player chooses to
spend a free respec or pay."* **Only the empire respec draws on this stock**; a unique creature, commander
included, always pays (R18, owner correction). R19 supplies the empire level. R-Q3's fixed counter
(*"free for a tunable number of times… Free counter default 25"*) is **superseded** by R18 and was never
built. **Status:** spec, not reviewed, no build authorized.

The module id is kept (ids are chosen once). What it now owns is an **earned stock of free empire
respecs**, not a fixed counter.

## Objective

A player who grows their empire earns the right to reshape it. Each empire level pays one or more free
empire respecs into a stock. When the player replaces a species build, they choose: spend a free respec,
or pay souls at the usual price. The price itself is unchanged, and so is its churn escalation.

What ships today, read in code:

| Piece | Where |
|---|---|
| Free: first override ever, and any revert to baseline | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:167-196` |
| Priced: replacing a non-empty override with a different one | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:198-243` |
| Replay: a soul-ledger hit on `(reason = respec, dedupe_key = correlationId)` returns the original outcome | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:204-215` |
| `price(count) = base + base × count × escalation / 1000`, linear, `checked` | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs:36-48` |
| Per `(player, species)` churn counter, decayed on read by `respecDecayDays` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:31-72` |
| Spend route and price preview | `gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs:31-76`, `:81-100` |
| Preset activation's species branch runs the same respec in its own transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:392-423` (call at `:410-411`) |
| No free allowance of any kind exists in code; `respecFreeCount` was only ever specified | `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs:16-64` has no such field |

## Design

### The stock: a ledger per empire

```sql
CREATE TABLE IF NOT EXISTS rpg_empire_free_respec_ledger (      -- (new)
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  save_id     INTEGER NOT NULL,
  empire_id   TEXT    NOT NULL,
  delta       INTEGER NOT NULL,          -- +n per grant, -1 per spend
  reason      TEXT    NOT NULL,          -- 'empire-level' | 'species-respec'
  dedupe_key  TEXT    NOT NULL,          -- 'L{level}' for a grant, the correlation id for a spend
  species_id  TEXT,                      -- set on a spend
  t           TEXT    NOT NULL,
  UNIQUE (save_id, empire_id, reason, dedupe_key)
);
```

- **Stock = `SUM(delta)`** for `(save_id, empire_id)`. It is never negative: a spend is written only
  when the stock is at least 1, inside the same transaction.
- **Keyed `(SaveId, EmpireId)`**, per `save-identity`. Every empire accrues grants, Zomboss's included
  (R19 parity). Only the human empire has a spend surface.
- **A ledger, not a counter row.** The grant and the spend each need replay safety, and a ledger
  gives both the way `rpg_soul_ledger` does (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-150`). It
  also answers "where did my free respecs come from" with rows.
- **No decay, no expiry.** An earned grant stays until spent. The churn counter keeps its own decay.
- **Never trimmed.** The stock *is* the ledger's sum, so a compacted or archived row would silently
  change a balance. This ledger is not added to any compaction or archive sweep (unlike `rpg_xp_ledger`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Compaction.cs:541-560`). Its growth is one row per empire level plus
  one per free spend, small by construction. A test pins that no compaction path names the table.

**The faucet** is `empire-level`'s `FreeEmpireRespec` grant: `+freeRespecsPerEmpireLevel` at each
empire level, dedupe `L{n}`, in the same transaction as the level change. **The sink** is a species
respec paid with it. P1 is met in this change: the faucet names its sink.

### Is the stock a currency? No, and where it is registered

It is not a **wallet**: it is not fungible across sinks, it buys exactly one action (an empire respec),
and it is never traded or converted. It is not a material. It matches the registry's **Accrual meter**
class (`docs/architecture/empire-resource-ssot.md` §2: *"Progress toward one action; spent only by that
action… exempt from P4/P6 because it buys exactly one thing by design and is never traded"*), with one
difference the row must say: it is held by an **empire**, not a sector, so it survives a world.

The registry's widening rule (§5) says a quantity is not finished until its row lands. So the build lands
a §3 row in the same change: *free empire respec · Accrual meter · held by empire · faucet: empire
level-up (`empire-level`) · sink: species respec · no conversion · owner `empire-progression` ·
`rpg_empire_free_respec_ledger`*.

### The rule

| Event | Payment | Churn counter | Stock |
|---|---|---|---|
| First override ever for this species | free: not a respec (unchanged) | no | no |
| Revert to baseline | free: not a respec (unchanged) | no | no |
| Replace an override, `payWith = freeRespec`, stock ≥ 1 | one free respec | **no** | −1 |
| Replace an override, `payWith = freeRespec`, stock = 0 | refused `respec.free.none` | — | — |
| Replace an override, `payWith = souls` | `PriceOf(effectiveCount)`, as today | +1 | no |
| Replace an override, `payWith` omitted, stock = 0 | souls, exactly today's path | +1 | no |
| Replace an override, `payWith` omitted, stock ≥ 1 | refused `respec.payment.choice-required`, with the quote | — | — |

- **The player chooses, every time** (R18). When a free respec is available, the server will not pick
  for them: an omitted choice is a named refusal carrying both options. When none is available there is
  only one option, and the call behaves exactly as it does today. So existing clients keep working
  until a player has earned a free respec, and the FE change ships with this module.
- **A free respec does not move the churn counter.** The counter prices churn in souls
  (`spec-species-respec.md` decision 15). A free respec is paid for by an earned grant. Counting it would
  make an earned grant raise the next soul price, which is a hidden cost on a reward.
- **First override and revert stay free and are not respecs.** Neither is changed by R18, and neither
  touches the stock.

### One quote, used by the spend and the preview

`specimen-respec-price` introduces the one quote function, for every respec scope:

```csharp
// gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs (introduced by specimen-respec-price)
public readonly record struct RespecQuote(RespecPrice Souls, long FreeStock)
{
    public bool FreeAvailable => FreeStock > 0;
}
public static RespecQuote Quote(RespecPriceTuning tuning, long effectiveCount, long freeStock);
```

This module is the only caller that passes a non-zero `freeStock`. A unique creature's quote always
passes 0 (R18: only the empire respec draws on earned free respecs). There is one price function
(`PriceOf`) and one quote function; no scope has its own.

`TryRespecSpeciesUnlocked`, the `/respec-price` preview and `AptitudePresetActivation.Preview`
(`build-preset` `gate-services`) all call `Quote` through one private store read,
`QuoteSpeciesRespecUnlocked(db, owner, speciesId)` (new), which reads the decayed count and the stock.
So the preview cannot show one answer while the spend charges another.

### The spend, in one transaction

`TryRespecSpeciesUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:145`) gains a
`RespecPayment? payWith` parameter (`RespecPayment { Souls, FreeRespec }`, new, Core). Order inside the
transaction:

1. Free cases (first override, revert) exactly as today (`:167-196`).
2. **Replay check, both ledgers**: a soul-ledger row `(respec, corr)` (`:204-215`) or a stock-ledger row
   `(species-respec, corr)` returns the original outcome and its payment. Checked before pricing, for the
   reason the existing comment gives (`:198-203`).
3. Read the stock. Resolve the payment by the table above.
4. `FreeRespec`: append `-1` to the stock ledger with `species_id`, write the override. The churn counter
   is not touched.
5. `Souls`: today's path unchanged (`:217-243`).

`SpeciesRespecOutcome` (`:26-27`) gains `Payment` and `FreeStock`.

### Routes

| Route | Change |
|---|---|
| `POST /api/species-build/respec` (`gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs:31`) | body gains `payWith?: "souls" \| "freeRespec"`; response gains `paidWith`, `freeRespecStock`. `respec.payment.choice-required` returns 409 with `{ soulPrice, freeRespecStock }` |
| `GET /api/species-build/respec-price/{playerId}/{speciesId}` (`:81`) | response gains `freeRespecStock` and `freeAvailable`. `priceAmount` keeps meaning the soul price |
| `POST /api/aptitude-presets/activate` (`gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs:172`), species scope | passes `payWith` through `TryActivateAptitudePreset` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:341-351`) to the same store call |

**The FE shows both options** when `freeAvailable` is true and sends the player's pick. It computes no
price and no stock (`gk-web/web/fusion-rpg-web/src/lib/bus/queries.ts:151` and `mutations.ts:317` are the
existing reads and writes). Build presets surface the same choice per species target
([`build-preset`](../build-preset-map.md) D4).

### Not a ceiling

The stock only lowers a price; it refuses nothing a player could otherwise do. Respec stays *"never refused
for being a respec"* (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:119-121`). The churn counter is
unchanged and remains the PS-8 exemption it states (`:60-65`).

## Seedsmith / generator

**None.** One tuning key. `gk-forge/tools/CreatureBuildPlanGen` reads the same file for its band values and
ignores this key, so the committed plan stays byte-identical (`--check` proves it).

## Tunables

`data/tuning/species-build.v{n+1}.json`, published, never hand-edited:

```powershell
python gk-core/tools/tuning/publish.py species-build --label "R18 earned free empire respecs" `
  --add-key ':freeRespecsPerEmpireLevel=1'
```

- `freeRespecsPerEmpireLevel`: free empire respecs per empire level, `long`, ≥ 0. Working value 1, the
  ruling's *"one grant per empire level-up"*. A missing key is a load rejection naming it
  (`SpeciesBuildTuningLoader`, `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs:103-190`).
- **`respecFreeCount` is never published.** R18 replaced it before it was built.
- The version is the next free one when this lands (Wave D, after `specimen-respec-price` and the Wave B
  publishes; the map's "Tuning version sequence" table). Every pin of the version it replaces moves in the
  same change, found by search: `rg -l "species-build\.v[0-9]+\.json" src tools tests --glob "*.cs"`. On
  2026-09-18 the v1 pins are `gk-core/src/FusionRpg.Server/Program.cs:153`, `gk-forge/tools/CreatureBuildPlanGen/Program.cs:47`,
  `gk-forge/tools/ProveHubCombat/Program.cs:101`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs:175`,
  and `gk-forge/tools/_TempSeedSpecies/Program.cs:121` (whether it moves or is deleted is its owner's call at build).
- Older versions stay on disk untouched (tunables-ssot T4).

## Revert path

`freeRespecsPerEmpireLevel = 0` means no grant is ever written, so the stock is 0, an omitted `payWith`
resolves to souls, and every species respec behaves exactly as today. Tested.

## ActorHub gate

**Not applicable.** A price is an economy number, not an actor magnitude. The override it guards reaches
Hub through the species allocation seam, unchanged.

## Integer widths and the power ladder

`long` for stock, deltas, counts and prices; `checked` in `PriceOf` (unchanged) and in the stock sum.
Never level-scaled (decision 15): the stock is **granted** per empire level, but the price never reads
a level and nothing reads `Θ`.

## Commands

```powershell
python gk-core/tools/tuning/publish.py species-build --add-key ':freeRespecsPerEmpireLevel=1'
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesRespec|FullyQualifiedName~EmpireFreeRespec"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RespecPolicy|FullyQualifiedName~SpeciesBuildTuning"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~SpeciesBuild"
dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `data/tuning/species-build.v{n+1}.json` (new) | published |
| `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs` | `FreeRespecsPerEmpireLevel` field + loader |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs` | `RespecPayment` (the `Quote` itself comes from `specimen-respec-price`) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs` (new) | the ledger schema, stock read, grant apply (called by `empire-level`), spend |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs` | `payWith`, both-ledger replay, `QuoteSpeciesRespecUnlocked` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs` | species branch passes `payWith` |
| `gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs`, `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs` | request and response fields |
| `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/CreatureBuildPlanGen/Program.cs`, `gk-forge/tools/ProveHubCombat/Program.cs` | pin moved |
| `gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`, the species-build panel | the choice, rendered from the preview |
| `docs/architecture/empire-resource-ssot.md` | the §3 row, same change |
| `gk-core/tests/FusionRpg.Data.Tests/SpeciesRespecTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs` (new) | below |

## Code style

One pure quote in Core, `long` arithmetic, the Data layer deciding the payment inside the same
transaction as the spend, and a ledger whose dedupe keys say what they deduplicate.

## Testing strategy

Values are read from the loaded tuning, never a literal 1 or 25.

1. **Choice required.** With stock ≥ 1 and no `payWith`, a replacement refuses with
   `respec.payment.choice-required` and writes nothing; the response carries the soul price and the stock.
2. **Spend free.** `payWith = freeRespec` writes the override, lowers the stock by 1, charges no souls and
   leaves the churn counter unchanged.
3. **Pay souls with stock available.** `payWith = souls` charges `PriceOf(effectiveCount)`, bumps the
   counter and leaves the stock unchanged.
4. **No stock.** `payWith = freeRespec` refuses `respec.free.none`; an omitted `payWith` behaves exactly as
   today's `SpeciesRespecTests` cases.
5. **Revert path.** With `freeRespecsPerEmpireLevel = 0`, the existing `SpeciesRespecTests` pass unchanged.
6. **First override and revert** move neither the stock nor the counter.
7. **Replay.** A replayed correlation id returns the original payment for both kinds and moves neither
   stock nor souls twice. A correlation id used for a free spend and then resent with `payWith = souls`
   is still the original free outcome.
8. **Grant.** An `empire-level` level-up adds `freeRespecsPerEmpireLevel` once per level; a replayed
   level-up adds nothing.
9. **Preview equals spend.** For stock 0 and stock ≥ 1, and counts across `[0, 3]`, the preview's quote
   equals what each payment charges.
10. **Empire keying.** A human spend never touches Zomboss's stock; Zomboss's grants accrue under his own
    `EmpireRef`, and no route spends them.
11. **Plan unchanged.** `CreatureBuildPlanGen --check` passes after the pin move.
12. **The stock is never trimmed.** No compaction or archive method references
    `rpg_empire_free_respec_ledger` (an architecture test over `RpgStore.Compaction.cs` and the archive
    writers), and a stock read after a compaction run equals the read before it.

## Boundaries

- **Always:** the player picks the payment when both exist; one `Quote` for preview and spend; publish
  through the tool.
- **Ask first:** letting the stock pay for a unique or commander respec (R18 says it does not); a stock
  that decays or expires; granting free respecs from anything but an empire level.
- **Never:** choose the payment for the player when a free respec is available; refuse a respec for its
  count; scale the price by level; edit a published tuning version in place.

## Success criteria

- [ ] `species-build.v{n+1}.json` published with `freeRespecsPerEmpireLevel`, every pin moved.
- [ ] Empire level-ups fill the stock; a replacement asks the player to spend one or pay souls.
- [ ] Preview and spend share one quote.
- [ ] The registry row for the free empire respec landed.
- [ ] `verify-change.py` green; `CreatureBuildPlanGen --check` green.

## Open questions

None. R18 fixed the source of free respecs, the choice, and which scopes draw on them.

## Self-audit — the debate

- **"Spend the free respec automatically; nobody wants to pay when they have a free one."** R18 says the
  player chooses. There is a real reason to pay: a free respec is scarcer than souls late in a session,
  and a player may save it. The refusal carries both options, so the choice costs one click.
- **"Keep the old 25 free respecs as well, as a starter pack."** R18 replaces the fixed count. A starter
  allowance would be a second faucet nobody ruled on.
- **"Refund a free respec when the player reverts."** A revert is already free. A refund would let a player
  churn replace → revert → replace at no cost to the stock.
- **"One stock per species, like the counter."** The grant is per empire level, and an empire level is
  not about one species. A per-species stock would need a rule for which species a grant goes to.
- **"Zomboss accrues a stock he cannot spend."** R19 gives him the same track. The unspent stock is an
  honest reading of his progress and the natural input for `ai-build-scorer` later. Spending it is a
  separate decision, not made here.
