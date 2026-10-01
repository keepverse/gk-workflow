# Spec: `apply-orchestrator`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave B** · depends on: `piece-appliers`.
**Status:** spec, not reviewed, no build authorized.

## Objective

"Swap to Fire lean" is one request. The orchestrator turns a stored build preset into a plan, shows the
player the whole plan with every price and every refusal named, and then applies it in an order that the
gates accept. It adds no rule and no price (map D4); it owns only **order, the whole-plan refusal, the
price sum, and convergence**.

## Design

### Two routes (`gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`, extended)

| Method | Route | Body | Returns | Writes |
|---|---|---|---|---|
| POST | `/api/build-presets/{presetId}/preview` | `{ playerId, force?, respecPayment? }` | `{ presetRevision, pieces: PiecePreview[], choices: PaymentChoice[], totals: {resource: amount}, balance, freeRespecStock, affordable, refusals }` | **never** |
| POST | `/api/build-presets/{presetId}/apply` | `{ playerId, correlationId, presetRevision, acceptedTotals, respecPayment?, force? }` | `{ applied: PieceOutcome[], refused?, totals }` | yes |

`force` passes through to the gear pieces only, with the item library's meaning (strip and report,
`docs/architecture/item/spec-armoury.md:112-114`). Default `false`.

`respecPayment` is `{ "<species targetRef>": "souls" | "freeRespec" }`, the player's choice per species
target (ruling R18: *"at each empire respec the player chooses to spend a free respec or pay"*). The
preview returns `choices` for every species target that is a respec while the empire holds a free respec;
the surface shows both options and sends the player's picks back to preview (to see the totals) and then
to apply. Commander and unique targets never appear in `choices`: they always pay (R18).

### The piece order is structural

| Step | Piece | Why here |
|---|---|---|
| 1 | `field` releases (not deferred) | frees capacity before binds (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:257-258` refuses a bind at capacity) |
| 2 | `field` binds | the patron gate refuses an unbound creature (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:38-39`) |
| 3 | `patron` | needs step 2 |
| 4 | `field` deferred release (the old patron) | release refuses a creature while it is patron (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:360`) |
| 5 | `aptitudes`, one target at a time, ordered by `target_ref` | independent of each other and of 6–7 |
| 6 | `gear`, one target at a time, ordered by `target_ref` | the relic wire needs a specimen in `Roster` (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:59-60`); runs after field changes settle |
| 7 | `skills` | independent |

This order is a **structural** constant, not a tunable: changing it breaks whether an apply works, not how
the game feels (tunables-ssot's test). The code carries that comment. Steps 5–7 are mutually independent,
and a test applies them in every permutation to prove it.

### Preview

1. Read the preset through `GetBuildPresetValidated`. Any `Missing` row is a refusal.
2. Build a `PlanState` from the current patron, bound set and balance.
3. Walk the steps. Each applier previews against the `PlanState` the earlier steps would produce.
4. Sum `PriceLine.Amount` per `Resource` with `checked` `long` addition. A species target with an
   unanswered choice contributes no line yet.
5. `affordable = totals.souls ≤ balance && totals.freeRespec ≤ freeRespecStock`. An unaffordable plan is a
   refusal (`build-preset.souls.insufficient` or `build-preset.free-respec.insufficient`, with the
   shortfall), because the gates would refuse part-way.
6. Any unanswered choice is a refusal for **apply** (`build-preset.respec.choice-required:{targetRef}`),
   never a default. Preview still returns the rest of the plan, so the player sees both options in context.

### Apply

1. **Stale guard.** `presetRevision` must equal the stored revision (`build-preset.revision.stale`).
2. **Re-preview.** Recompute the plan. If it refuses, refuse the apply with the same refusals. Nothing
   is written.
3. **Price guard.** If any recomputed total exceeds `acceptedTotals` for its resource, refuse
   (`build-preset.price.changed`, with both numbers). A player never pays more than the preview showed,
   in souls or in free respecs. A total that went **down** passes, which is what makes a retry work
   (below). The re-preview uses the same `respecPayment`, so the choice made at preview is the one applied.
4. **Execute** the steps in order. Each write gets a derived correlation id (below). Stop at the first
   refused write, and return every outcome so far plus the refusal.

### Convergence instead of one transaction (map D5)

The gates own separate transactions, and two own runtime side effects in Server services. The apply is
therefore made **convergent**:

- **Derived correlation ids.** Each priced or replay-guarded write gets
  `bp-` + the first 32 hex characters of `SHA-256(correlationId | kind | target_ref | step)`, which stays
  inside the patron route's 64-character limit (`gk-core/src/FusionRpg.Server/PatronEndpoints.cs:31-32`). The same
  apply request always derives the same ids.
- **What a retry does.** Re-sending the same `correlationId` after an interrupted apply recomputes the
  plan against the new state: a patron already switched reads as a replay (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:43-47`);
  a creature already bound is a replay (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:249-253`) and a
  same-day re-bind is not charged twice (`:266-268`); a species respec with the same correlation id is
  a replay by its own contract, whether it was paid in souls or with a free respec (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:203`,
  and `respec-free-counter`'s both-ledger replay check); a commander or unique respec likewise
  (`specimen-respec-price`); equip upserts on `(target, role)`. The remaining total is lower, so the
  price guard passes, and the apply finishes. **Nothing is charged twice.**
- **What the player sees if it stops half-way.** The response lists every write applied, and the refusal
  that stopped it. A later preview shows exactly the pieces still to do.

**One apply per player at a time.** An in-process lock keyed by `playerId` serialises preview-then-apply
for one player, so two tabs cannot interleave two presets' steps. It is a structural limit, commented as
such.

### Actor numbers

The orchestrator writes nothing itself. After an apply, each layer is read back through its own normal
read path (patron route, contracts route, aptitude sheet, item assignments, loadout route), never from
the apply response. That is also how CP2 is proven (live-probe standard: a response body is not proof).

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildPresetPlan"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetApply"
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `src/FusionRpg.Core/BuildPresets/BuildPresetPlan.cs` (new) | the step order, the price sum, the derived-id function; pure |
| `src/FusionRpg.Server/BuildPresets/BuildPresetOrchestrator.cs` (new) | preview/apply over the appliers |
| `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs` | the two routes |
| `tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetPlanTests.cs` (new), `tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetApplyTests.cs` (new) | below |

## Code style

```csharp
public static class BuildPresetPlan
{
    /// Structural, not tunable: the gates refuse any other order (see spec-apply-orchestrator.md).
    public static readonly IReadOnlyList<PlanStep> Steps =
    [
        PlanStep.FieldRelease, PlanStep.FieldBind, PlanStep.Patron, PlanStep.FieldDeferredRelease,
        PlanStep.Aptitudes, PlanStep.Gear, PlanStep.Skills,
    ];

    public static string DerivedCorrelation(string corr, BuildPresetPieceKind kind, string targetRef, PlanStep step)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes($"{corr}|{BuildPresetPieceKinds.Id(kind)}|{targetRef}|{step}"));
        return "bp-" + Convert.ToHexString(bytes)[..32].ToLowerInvariant();
    }
}
```

## Testing strategy

1. **Whole-plan refusal writes nothing.** A preset with one refusing piece among five valid ones leaves
   every table unchanged, and the response names the refusing piece.
2. **Unaffordable refuses before writing,** with the shortfall.
3. **Price guard.** A preview, then a change that raises the price (a by-hand respec of a specimen
   between preview and apply, so its escalated price is higher), then apply with the old
   `acceptedTotals` refuses with both numbers.
3a. **Stock moved under the choice.** A preview choosing `freeRespec` for a species target, then a by-hand
   species respec that spends the last free respec, then apply: refuses with
   `build-preset.free-respec.insufficient` and writes nothing. It never silently switches that target to
   souls.
3b. **Choice required.** With a free respec available, an apply without a choice for a species respec
   target refuses by name and writes nothing; the same apply with the choice succeeds.
4. **Retry converges.** Inject a failure after step 3; the second apply with the same `correlationId`
   completes, and the soul-ledger and free-stock totals each equal a single uninterrupted apply's.
5. **Order-independence of steps 5–7.** Applying them in every permutation yields identical stored rows.
6. **Patron swap with release.** A preset replacing the patron and dropping the old one ends with the new
   patron set and the old one released, in one apply.
7. **Read-back.** Every assertion of "applied" reads the layer through its normal route, not the apply
   response.
8. **Plan function is pure.** `Steps` membership and order are pinned with the structural reason in the
   test comment; `DerivedCorrelation` is deterministic and ≤ 64 characters.

## Boundaries

- **Always:** preview before apply; refuse whole plans; name every refusal; never charge above the
  previewed total.
- **Ask first:** making the apply transactional across gates (a Data-layer composite writer), or adding
  an apply journal table.
- **Never:** write a layer's table from the orchestrator; hide a partial apply; add a fee.

## Tunables

**None.** The step order is structural (above). Prices are the gates' tunables.

## ActorHub gate

**Neither contributes nor consumes.** Answered in the map's five-question table; the architecture test in
`piece-appliers` covers this module's namespace too.

## Integer widths

`long` totals, `checked` summation; `acceptedTotals` is `long` per resource on the wire.

## Seedsmith / generator

**None.**

## Success criteria

- [ ] Preview names every price and refusal; apply refuses whole plans and stale or dearer ones.
- [ ] An interrupted apply converges on retry without a second charge.
- [ ] Steps 5–7 proven order-independent.
- [ ] `verify-change.py` and `guard-actor-hub.py` green.

## Open questions

None.

## Self-audit — the debate

- **"A half-applied build is a bad state."** It is visible, costs nothing extra to finish, and a retry
  finishes it. The alternative, one transaction across patron, contracts, aptitudes and equip, needs the
  equip executor and the patron runtime push moved into a Data-layer composite: a second implementation
  of four gates. The preview makes the half-applied case rare: it happens only when state changes between
  preview and apply, which the price and revision guards narrow further.
- **"Why not let the player choose the order?"** Only one order is accepted by the gates. Exposing it
  would be exposing a way to fail.
- **"The in-process lock does not survive two server processes."** The server is a single process by
  design (one SQLite writer); the lock is scoped to that, and the gates' own replay guards still hold if it
  ever were not.
