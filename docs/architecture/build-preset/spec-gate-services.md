# Spec: `gate-services`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave A** · depends on: external `empire-progression`
`specimen-respec-price` (`RespecPolicy.Quote`, the priced commander/unique branches) and `respec-free-counter`
(the species `payWith` choice and the free stock), both read by `AptitudePresetActivation.Preview`.
**Status:** spec, not reviewed, no build authorized. Built after `empire-progression` (R5).

## Objective

A build preset applies a patron, an aptitude preset, a field of bound creatures and a skill loadout by
calling the same
gates the player's own clicks call. Four of those gates cannot be called that way today, because their
post-write work lives inside an HTTP endpoint lambda:

| Gate | Where the logic lives | What an applier calling only the store would miss |
|---|---|---|
| Patron set | `gk-core/src/FusionRpg.Server/PatronEndpoints.cs:26-62` | `RefreshRuntimeState` (`:43`, defined `:106`), `PatronUpdated`/`SoulsUpdated` broadcasts, and the injector `patron.aura` command with its inbox fallback (`:44-53`) |
| Aptitude preset activate | `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs:172-240`, budget at `:295-331`, scope map `:287-293` | Budget resolve per scope, `AptitudePresetMaterialize.Materialize` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetMaterialize.cs:57`), the `PointBudget.CheckScope` re-check, and the scoped broadcast |
| Contract bind / release | `gk-core/src/FusionRpg.Server/ContractEndpoints.cs:26-46`, notify at `:109` | The contract/souls notification |
| Action (skill) loadout set | `gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs:50-71` | The held predicate that admits aura ids (`:60-63`) and the mid-run predicate; a caller of `RpgStore.SetLoadout` must pass both, so a second caller would copy them |

This module lifts each into a named service. **Behaviour is byte-identical**: the endpoints become thin
callers of the service, and every existing endpoint test passes unchanged. The applier in
`piece-appliers` then calls the same service, so there is one implementation per gate (S and L in SOLID).

This is a refactor with no player-visible change. It is its own module because it must land, and be
proven unchanged, before anything depends on it.

## Design

```csharp
// gk-core/src/FusionRpg.Server/Gates/PatronService.cs (new)
public sealed class PatronService
{
    public PatronService(RpgStore store, IHubContext<RpgHub> hub, InjectorCommandInbox inbox) { … }

    /// The whole of POST /api/patron/set after request validation: store write, runtime refresh,
    /// broadcasts, injector push. Refusals return the store's reason unchanged.
    public Task<PatronSetOutcome> SetAsync(long playerId, string instanceId, string correlationId);
}

public sealed record PatronSetOutcome(bool Ok, string Reason, PatronRow? Patron);   // (new)
```

```csharp
// gk-core/src/FusionRpg.Server/Gates/AptitudePresetActivation.cs (new)
public sealed class AptitudePresetActivation
{
    /// Budget → materialize → budget check → RpgStore.TryActivateAptitudePreset → scoped broadcast.
    /// Every branch charges inside the store transaction, where its by-hand route charges: species
    /// through TryRespecSpeciesUnlocked (with the player's payWith), commander and unique through
    /// TryReallocateUnlocked (R18, empire-progression specimen-respec-price).
    public ActivationResult Activate(long playerId, string presetId, string scope, string scopeKey,
                                     string? correlationId, RespecPayment? payWith);

    /// Read-only half for previews: same budget resolve and materialize, no write. Returns the shares,
    /// leftover, and the respec quote for every scope: for "species" the soul price AND the free empire
    /// respec stock (the player chooses); for "commander"/"unique" whether it is a respec and its price.
    public ActivationPreview Preview(long playerId, string presetId, string scope, string scopeKey);
}
```

`Preview` is the one addition. It is the read half the endpoint already computes before it writes,
exposed without the write; it adds no rule. For the species scope it calls `respec-free-counter`'s
`QuoteSpeciesRespecUnlocked` (the decayed count and the empire's free stock, through `RespecPolicy.Quote`);
for the commander and unique scopes it calls `specimen-respec-price`'s `QuoteReallocation`. Each is the
same read its write path makes, so the preview and the spend cannot disagree (the "one quote" rule).

**Pricing is not this module's change.** R18's pricing of commander and unique activation, and the species
`payWith` parameter, land in `empire-progression` (`specimen-respec-price`, `respec-free-counter`) before
this module is built. This module lifts whatever the route does at that point, byte-identically, and only
threads `payWith` from the request to the store call.

```csharp
// gk-core/src/FusionRpg.Server/Gates/ContractService.cs (new)
public sealed class ContractService
{
    public Task<ContractOutcome> BindAsync(long playerId, string instanceId);
    public Task<ContractOutcome> ReleaseAsync(long playerId, string instanceId);
}
```

**Registration.** The four services are registered once in `gk-core/src/FusionRpg.Server/Program.cs` and
injected into both the endpoints and, later, the appliers. No static state.

**What does not move.** Store methods (`RpgStore.SetPatron`, `TryActivateAptitudePreset`,
`BindContract`, `ReleaseContract`) are unchanged. Refusal reason strings are unchanged; they are a wire
contract the FE already reads.

```csharp
// gk-core/src/FusionRpg.Server/Gates/ActionLoadoutService.cs (new)
public sealed class ActionLoadoutService
{
    /// The route's own call: SetLoadout for the player's scope with the route's held and mid-run
    /// predicates, now named once. Preview runs LoadoutSet.Validate with the same predicates.
    public LoadoutValidation Set(long playerId, IReadOnlyList<string> actionIds);
    public LoadoutValidation Preview(long playerId, IReadOnlyList<string> actionIds);
}
```

## Commands

```powershell
dotnet build src\FusionRpg.Server
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset|FullyQualifiedName~Patron|FullyQualifiedName~Contract|FullyQualifiedName~Loadout"
dotnet test tests\FusionRpg.E2E.Tests --filter "FullyQualifiedName~PatronE2E|FullyQualifiedName~ContractE2E"
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Server/Gates/PatronService.cs` (new) | lifted from `PatronEndpoints.cs:26-62` |
| `gk-core/src/FusionRpg.Server/Gates/AptitudePresetActivation.cs` (new) | lifted from `AptitudePresetEndpoints.cs:172-240,287-331`, plus `Preview` |
| `gk-core/src/FusionRpg.Server/Gates/ContractService.cs` (new) | lifted from `ContractEndpoints.cs:26-46,109` |
| `gk-core/src/FusionRpg.Server/Gates/ActionLoadoutService.cs` (new) | lifted from `LoadoutEndpoints.cs:50-71` |
| `gk-core/src/FusionRpg.Server/PatronEndpoints.cs`, `AptitudePresetEndpoints.cs`, `ContractEndpoints.cs`, `LoadoutEndpoints.cs` | lambdas call the services |
| `gk-core/src/FusionRpg.Server/Program.cs` | registrations |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs`, `RpgStore.AllocationRespec.cs` | no change here: the read-only quotes are `respec-free-counter`'s and `specimen-respec-price`'s |
| `gk-core/tests/FusionRpg.Server.Tests/Gates/*` (new) | service-level tests below |

This module adds no Data method. The species quote is `respec-free-counter`'s `QuoteSpeciesRespecUnlocked`,
which reads exactly what `TryRespecSpeciesUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:145`)
reads; the commander/unique quote is `specimen-respec-price`'s `QuoteReallocation`. No write SQL is added
(`guard-dal.py` stays green).

## Code style

Endpoint after the lift, the whole handler:

```csharp
g.MapPost("/set", async (SetPatronRequest body, RpgStore store, PatronService patron) =>
{
    var pid = body.PlayerId ?? store.GetCurrentPlayerId();
    if (!store.PlayerExists(pid)) return Results.NotFound();
    if (string.IsNullOrWhiteSpace(body.CorrelationId)) return Results.BadRequest(new { reason = "correlation.missing" });
    if (body.CorrelationId.Trim().Length > 64) return Results.BadRequest(new { reason = "correlation.toolong" });

    var outcome = await patron.SetAsync(pid, body.InstanceId ?? "", body.CorrelationId!);
    if (!outcome.Ok)
        return outcome.Reason is "souls.insufficient" ? Results.Conflict(new { reason = outcome.Reason })
                                                      : Results.BadRequest(new { reason = outcome.Reason });
    return Results.Ok(PatronEndpoints.ProjectState(store, pid));
});
```

Request-shape validation (missing body fields, length limits) stays in the endpoint, because it is about
HTTP. Everything after it is the service.

## Testing strategy

1. **Unchanged.** Every existing test over the four route groups passes with no edit. This is the proof the
   lift is byte-identical, and it is run first.
2. **Service parity.** For each service, a test drives the service directly and the route over HTTP with
   the same inputs and asserts the same stored rows and the same reason.
3. **Side effects reach the runtime.** `PatronService.SetAsync` enqueues the injector command exactly as
   the route did (assert on `InjectorCommandInbox`).
4. **Preview equals activate.** For every scope, `Preview`'s shares, leftover and quote equal what
   `Activate` then writes and charges: species paid with a free respec and paid in souls, species with
   no choice while a free respec exists (refused by name, nothing written), and a commander and a unique
   target both adding points (free) and taking points back (priced).
5. **Preview writes nothing.** Row counts of the allocation, preset-active and soul-ledger tables are
   unchanged after `Preview`.

## Boundaries

- **Always:** keep reason strings identical; keep request validation in the endpoint; one service per
  gate.
- **Ask first:** changing any refusal code or status code.
- **Never:** add a rule, a price or a write inside a service that the route did not already perform;
  call a store write from an applier that skips its service.

## Tunables, ActorHub, integer widths

- **Tunables:** none. `switchCostSouls` stays in `gk-core/data/tuning/patron.v1.json`.
- **ActorHub:** not applicable. The allocation write reaches Hub through its existing seams, unchanged.
- **Integer widths:** unchanged; prices are `long` in the store paths today.

## Seedsmith / generator

**None.** A server refactor over runtime gates; no seed shape.

## Success criteria

- [ ] Four services exist; the four endpoint groups call them.
- [ ] Existing route tests are green with no edit.
- [ ] `AptitudePresetActivation.Preview` returns exactly what `Activate` writes and charges.
- [ ] `verify-change.py` green.

## Open questions

None.

## Self-audit — the debate

- **"This is refactoring for its own sake."** It is the precondition for not duplicating four gates.
  The alternative, an applier calling `RpgStore.SetPatron` directly, would change the patron without
  pushing the aura to the injector, which is exactly the class of defect the 2026-09-07 equip sync
  closed (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:447-459`).
- **"Put the side effects in the store instead."** The store is SQL-only and has no SignalR or injector
  inbox; putting them there would break the Data boundary.
- **"`Preview` is new behaviour."** It is the endpoint's existing read half, without the write. It
  introduces no number the route does not already compute.
