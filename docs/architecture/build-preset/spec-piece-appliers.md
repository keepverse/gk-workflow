# Spec: `piece-appliers`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave B** · depends on: `gate-services`,
`item-loadout-apply`, `preset-store`; external `empire-progression` `specimen-respec-price` and
`respec-free-counter` (`RespecPolicy.Quote` and the species payment choice, reached through
`AptitudePresetActivation.Preview`).
**Status:** spec, not reviewed, no build authorized.

## Objective

Each piece kind gets one applier that knows two things: what applying this piece *would* do (refusal or
price), and how to apply it by calling the gate that owns it. An applier holds **no rule of its own**:
every refusal comes from the gate's precondition, every price from the gate's policy. This is where the
program's price rule becomes a test:

> **The price of applying a preset equals the sum of what the same changes cost by hand, computed by the
> same functions** (map D4).

## Design

### The interface (`src/FusionRpg.Server/BuildPresets/IBuildPresetPieceApplier.cs`, new)

```csharp
public interface IBuildPresetPieceApplier
{
    BuildPresetPieceKind Kind { get; }

    /// Read-only. Never writes, never spends. `plan` carries the state earlier pieces will have
    /// produced (e.g. the bound set after the field piece), so a later piece is judged against it.
    PiecePreview Preview(ApplyContext ctx, IReadOnlyList<ValidatedPiece> rows, PlanState plan);

    /// Calls the owning gate(s). `correlationId` is derived by the orchestrator per write.
    Task<PieceOutcome> ApplyAsync(ApplyContext ctx, IReadOnlyList<ValidatedPiece> rows,
                                  PlanState plan, CorrelationScope corr);
}

public sealed record PriceLine(string Resource, long Amount, string Reason, bool Free, long? FreeRemaining);
/// A species target that is a respec while the empire holds a free respec: both options, for the player.
public sealed record PaymentChoice(string TargetRef, long SoulPrice, long FreeStock);
public sealed record PiecePreview(BuildPresetPieceKind Kind, IReadOnlyList<string> Refusals,
                                  IReadOnlyList<PriceLine> Prices, IReadOnlyList<PaymentChoice> Choices,
                                  IReadOnlyList<string> Writes);
public sealed record PieceOutcome(BuildPresetPieceKind Kind, IReadOnlyList<WriteOutcome> Writes);
```

A `Missing` piece row is a refusal at preview (`build-preset.piece.missing:{kind}`): the player chose
that piece, so applying without it would be the silently shorter preset the store refuses to show.

### The five appliers

| Kind | Preview asks | Price (by-hand function) | Apply calls |
|---|---|---|---|
| `patron` | `PatronPreconditions` (new, below) with `assumeBound = plan.WillBeBound(id)`; no-op when already patron | `PatronPolicy.SwitchCostSouls` when a different patron is set, 0 on first designation or replay (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:43-56`; `gk-core/src/FusionRpg.Core/Creatures/Patron/PatronPolicy.cs:35`) | `PatronService.SetAsync` (`gate-services`) |
| `field` | diff against the current bound set → `toBind`, `toRelease`; capacity after the diff (`ContractPolicy.Capacity`, `gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:171`); each release against the release gate's refusals (deployed, on expedition, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:356-359`) | per bind, `ContractPolicy.UpkeepPerDay(rarity, personality)`, free when that creature's day is already paid (the ledger dedupe key `bind:{id}:{day}`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:263-268`); release is free (`:329-330`) | `ContractService.ReleaseAsync` / `BindAsync` |
| `aptitudes` | per target, `AptitudePresetActivation.Preview` | **species** (ruling R18): not a respec (first override, revert) → no line; a respec with free stock 0 → souls `PriceOf`; a respec with free stock ≥ 1 → a `PaymentChoice` carrying both options, resolved by the player's choice in the request into either a `souls` line or a `freeRespec` line of amount 1 (`respec-free-counter`). **Commander and unique** (R18 and its correction): adding unspent points → no line; taking points back → souls `PriceOf(UniqueRespec, count)`, exactly as the by-hand route charges it (`specimen-respec-price`); never a `freeRespec` line | `AptitudePresetActivation.Activate`, passing the target's `payWith` |
| `gear` | per target, the item loadout preview (`item-loadout-apply`); across targets, the same rolled copy named by two gear pieces | 0 (equip is free by design, `gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:35-36`) | `ItemLoadoutApplyService.Apply(targetId, force)` |
| `skills` | `LoadoutSet.Validate` with the loadout route's own held and mid-run predicates | 0 | `ActionLoadoutService.Set` (`gate-services`) |

**Wardens are outside the field diff.** A warden contract is permanent for the life of the world and
refuses release unconditionally (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:351-353`). The field
applier never plans a warden release; wardens stay bound and count toward capacity. Without this, any
player holding a warden could not apply a field piece that omits it.

**The current patron is released last.** Release refuses a creature that is patron
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:360`). When the preset replaces the patron and drops the
old one from the field, the field applier marks that release **deferred**, and the orchestrator runs it
after the patron piece. When the preset has no patron piece and the field drops the current patron, the
preview refuses by the gate's own reason (`contract.is-patron`), so the player sees why.

### Read-only preconditions, one function per gate

A preview must refuse for the same reasons the write would, so each gate's precondition becomes one
function that the write and the preview both call, never a copy:

| Gate | Shared precondition (new, in Data, beside the write) | Used by |
|---|---|---|
| Patron | `PatronPreconditionsUnlocked(db, playerId, id, assumeBound)` extracted from `SetPatron`'s checks (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:30-40`) | `SetPatron` (with `assumeBound = false`) and `QuotePatron` |
| Contract bind | `BindPreconditionsUnlocked` + fee from `BindContract` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:245-268`) | `BindContract` and `QuoteBind` |
| Contract release | `ReleasePreconditionsUnlocked` from `ReleaseContract` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:345-360`) | `ReleaseContract` and `QuoteRelease` |
| Aptitude activate | already shared by `gate-services` (`Preview`) | — |
| Item loadout apply | `LoadoutReport.Plan` is already the shared judgement (`gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs:73`) | — |
| Action loadout | `LoadoutSet.Validate` is already pure | — |

The write methods keep their signatures and behaviour; their existing tests are the proof.

### Price arithmetic

Each `PriceLine.Amount` is `long`. The orchestrator sums them with `checked` addition; an overflow throws
rather than wraps (CLAUDE.md numeric rule 3). Two resources appear: `souls` (`RespecResource.Soul`,
`gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs:23`; patron and upkeep debit the soul ledger) and
`freeRespec`, the empire's earned free respec stock (R18; an Accrual meter, not a currency, per
`respec-free-counter`). The `Resource` field is what keeps a free respec from being summed into souls.

**The choice stays sequential.** Two species targets in one preset may both want the last free respec.
The applier resolves choices in the orchestrator's target order against a running stock in `PlanState`,
so a second `freeRespec` choice past the stock is a preview refusal
(`build-preset.free-respec.insufficient`), not a surprise at apply.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Patron|FullyQualifiedName~Contract"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetAppliers"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `src/FusionRpg.Server/BuildPresets/IBuildPresetPieceApplier.cs` (new) | interface + records |
| `src/FusionRpg.Server/BuildPresets/Appliers/{Patron,Field,Aptitudes,Gear,Skills}Applier.cs` (new) | five appliers |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs` | precondition extracted; `QuotePatron` (new) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs` | preconditions extracted; `QuoteBind`, `QuoteRelease` (new) |
| `gk-core/src/FusionRpg.Server/Program.cs` | register appliers as `IEnumerable<IBuildPresetPieceApplier>` |
| `tests/FusionRpg.Server.Tests/BuildPresets/*` (new) | below |

## Code style

```csharp
public sealed class PatronApplier(RpgStore store, PatronService patron) : IBuildPresetPieceApplier
{
    public BuildPresetPieceKind Kind => BuildPresetPieceKind.Patron;

    public PiecePreview Preview(ApplyContext ctx, IReadOnlyList<ValidatedPiece> rows, PlanState plan)
    {
        var id = rows.Single().RefId;
        var q = store.QuotePatron(ctx.PlayerId, id, assumeBound: plan.WillBeBound(id));
        return q.Ok
            ? PiecePreview.Priced(Kind, q.Replay ? [] : [new PriceLine("souls", q.Price, "patron.switch", q.Price == 0, null)])
            : PiecePreview.Refused(Kind, q.Reason);
    }
    …
}
```

## Testing strategy

1. **Price equality (the program's contract).** For each kind, and for a preset combining all five,
   run the preset apply on one in-memory store and the equivalent by-hand route calls on an identical
   store; the soul-ledger deltas are equal, entry for entry. Covered cases: first patron (free), patron
   switch (priced), species respec paid with a free empire respec and paid in souls, species respec with
   no free stock, commander and unique targets adding points (free) and taking points back (priced), a
   same-day re-bind (free) and a fresh bind (upkeep). The free-stock ledger deltas are equal too, and so
   are the churn counters the prices read (`rpg_species_respec`, and `specimen-respec-price`'s
   `rpg_allocation_respec`), compared at one injected clock so decay cannot split them. This is the
   program-level half of one contract; `specimen-respec-price` test 10 asserts the gate-level half.
2. **Preview equals apply.** Each applier's preview prices and refusals equal what its apply then does.
3. **Preview writes nothing.** Ledger, allocation, patron, contract, assignment and loadout tables are
   unchanged after any preview.
4. **Shared preconditions.** `SetPatron`, `BindContract`, `ReleaseContract` existing tests pass
   unchanged; each quote refuses for exactly the reasons its write refuses.
5. **Warden and patron edges.** A field piece omitting a warden applies and leaves the warden bound; a
   preset replacing the patron and dropping the old one releases it after the switch; a preset dropping
   the current patron without replacing it refuses with `contract.is-patron`.
6. **Gear double-claim.** Two gear pieces naming one rolled copy refuse at preview by name.
7. **No actor-number path.** An architecture test asserts `FusionRpg.Server.BuildPresets` references no
   `DerivedModifier`, `ActorHub` or `ContributionSourceIds` type (map D6).
8. **The player's choice is honoured, never made.** With a free respec available and no choice in the
   request, the aptitude applier returns a `PaymentChoice` and applies nothing for that target; the
   orchestrator refuses the apply by name. A unique or commander target never produces a `PaymentChoice`
   or a `freeRespec` line.

## Boundaries

- **Always:** refusals from the gate's own precondition, prices from the gate's own policy; one shared
  precondition per gate.
- **Ask first:** any price the by-hand path does not charge; a sixth applier.
- **Never:** a discount or surcharge for applying as a preset; an applier writing a table directly;
  re-implementing a gate's check inside an applier.

## Tunables

**None new.** Every price is already tunable where it lives: `switchCostSouls` (`gk-core/data/tuning/patron.v1.json`),
upkeep (`gk-core/data/tuning/contracts.v1.json`), the species and unique respec base, escalation and decay, and
`freeRespecsPerEmpireLevel` (`species-build.v{n}.json`, added by `specimen-respec-price` and
`respec-free-counter`).

## ActorHub gate

**Neither contributes nor consumes.** Appliers write the inputs of existing layers (map "actor-layer
five questions"). Test 7 enforces it.

## Integer widths

`long` for every price and the sum, `checked` summation. Counts (bind/release lists) are small
collections, not magnitudes.

## Seedsmith / generator

**None.** Runtime application over player-owned rows.

## Success criteria

- [ ] Five appliers behind one interface.
- [ ] Price-equality test green for every kind and the combined preset.
- [ ] Each gate's precondition is one function used by its write and its quote.
- [ ] `guard-actor-hub.py`, `guard-dal.py`, `verify-change.py` green.

## Open questions

None. The map's OWNER question 1 (price commander and specimen re-allocation?) was answered yes by
ruling R18. This module needed no structural change for it, because it prices through the gate.

## Self-audit — the debate

- **"A preset could offer a bundle discount so it feels good."** A discount is a new sink change nobody
  asked for, and it would make a preset cheaper than the same clicks, so players would route every change
  through a throwaway preset. Equality is the rule and the test.
- **"Quote functions duplicate the write's checks."** They share one extracted function with the write;
  duplication is exactly what the extraction prevents.
- **"Handle wardens by refusing, so the player decides."** A warden can never be released, so refusing
  would make every field piece unusable for a warden holder with nothing the player could do about it.
