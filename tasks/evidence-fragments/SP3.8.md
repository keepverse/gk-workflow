# SP3.8 — One scope↔text vocabulary in Core; the `Aptitude(scope, share)` SourceId helper

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The scope↔text mapping moves from `RpgStore.ScopeToText` to Core beside `AllocationScope`, and Data delegates to it | code edit | done | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AllocationScopeText.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs` |
| `ContributionSourceIds.Aptitude(scope, share)` gives `aptitude.{Share}` for Commander (unchanged) and `aptitude.{scopeText}.{Share}` for every other scope, each with a `FictionLabel` arm | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContributionSourceIds\|FullyQualifiedName~AllocationScopeText"` | **16/16 passed** | `tests/FusionRpg.Core.Tests/Stats/ContributionSourceIdsTests.cs`, `tests/FusionRpg.Core.Tests/ClassSystem/AptitudeAllocationTests.cs` (`AllocationScopeTextTests`, new) |
| `RpgStore.ScopeToText`/`.ScopeFromText`'s existing callers and tests stay unaffected by the move | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore"` | **18/18 passed** | test output |
| Data + Core build clean | `dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj` | 0 errors | build log |

## What shipped

- `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AllocationScopeText.cs` (new): `ToText(AllocationScope)` /
  `FromText(string)`, moved verbatim from `RpgStore.Aptitudes.cs:53-67`'s own switch expressions —
  same four-scope mapping, same "unknown scope rejects, names the value" contract.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`: `ScopeToText`/`ScopeFromText` keep their existing
  public signatures (every call site in `RpgStore.Aptitudes.cs`/`RpgStore.PassiveTree.cs` and
  `AllocationStoreTests.cs` is unchanged) but are now one-line delegates to `AllocationScopeText` — one
  vocabulary, not two.
- `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs`: new `Aptitude(AllocationScope scope,
  string share)` overload. `Commander` returns the unchanged, unscoped `aptitude.{Share}` form (every
  existing commander-scope contribution stays byte-identical — proven by
  `Commander_scope_keeps_the_unchanged_unscoped_form`); every other scope returns
  `aptitude.{scopeText}.{Share}`. `FictionLabel`'s `aptitude.` arm now branches on whether a second `.`
  follows the prefix, giving the two-segment form its own label (`Aptitude · creatureType · Might`)
  distinct from the one-segment Commander form (`Aptitude · Might`).
- Nothing in `src/` calls the new `Aptitude(scope, share)` overload yet — per the acceptance line
  "Nothing emits the per-scope ids until SP6.1" (species-layer-delivery step 6.1 is the actual wiring;
  this task only builds the helper it will call).

## Reviewed-vocabulary note

No closed-vocabulary or SourceId-count pin needed updating: `ContributionSourceIds` has no test
asserting a fixed count of producer helpers (unlike `ContainerKind`'s member-count pins, SP3.2's own
follow-up), and the new overload is additive (the existing `Aptitude(string)` single-arg form is
untouched and still used by every existing Commander-only caller).
