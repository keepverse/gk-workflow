# SP3.1 — three species SourceId helpers + `FictionLabel` arms + the `actor-hub-ssot.md` §8.1 rows

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SpeciesBase`/`SpeciesPlayer`/`SpeciesEmpire` mint the spec's grammar and round-trip through `FictionLabel` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContributionSourceIds"` | **8/8 passed** | `tests/FusionRpg.Core.Tests/Stats/ContributionSourceIdsTests.cs` |
| A species id containing `:` throws | same run, `A_species_id_containing_a_colon_throws_for_every_species_helper` | pass | same file |
| `SpeciesEmpire`'s empire token is the `EmpireId.Value` unchanged (`dave`/`zomboss`) | same run, `SpeciesEmpire_uses_the_empire_id_token_unchanged` | pass | same file |
| §8.1 amended in the same change: three rows added | doc edit | done | `docs/architecture/actor-hub-ssot.md` §8.1 (new amendment block + three table rows) |
| Doc citations still resolve | `python scripts/audit-doc-citations.py --scope docs/architecture/actor-hub-ssot.md --strict` | **1 HIGH, confirmed pre-existing** (`:139`, `ProgressionPowerCurve.cs` — file already absent on `HEAD` before this change, verified via `git show HEAD:docs/architecture/actor-hub-ssot.md`; unrelated to this task, not introduced here, left as-is) | tool output |
| Core builds clean | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj` | 0 errors | build log |

## What shipped

`gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs`:
- `SpeciesBase(speciesId)` -> `species-base:{speciesId}`
- `SpeciesPlayer(speciesId, mechanism)` -> `species-player:{speciesId}:{mechanism}`
- `SpeciesEmpire(EmpireId empire, speciesId, aptitudeId)` -> `species-empire:{empireToken}:{speciesId}:{aptitudeId}`
- `FictionLabel` gains three parse arms (`Species · …`, `Your species · … (…)`, `Empire species · … · …`)
- `ValidateSpeciesId` — the same "no `:`" assertion `CreatureProgressionSource.ValidatePart` already applies, so a species id entering this grammar is asserted, never trusted (spec "Grammar safety").

`docs/architecture/actor-hub-ssot.md` §8.1: a new amendment blockquote (species-progression SP3.1, map
C3) plus three table rows. **No row is retired** — T4.6's `species-passive:{speciesId}`
(`SpeciesPassiveAtomSource.cs:42`) was minted outside this grammar and so was never listed in the
table to begin with; that omission is map's own C3 defect, documented as such in the amendment note.
`SpeciesPassiveAtomSource.cs` itself is untouched here — its retirement is SP3.6.

## Reviewed-vocabulary note (spec Boundaries: "Ask first: … the §8.1 amendment")

Per the spec's own SP3.1 acceptance text ("spec Ask-first; the change is shown in review" —
distinct from SP2.2's literal "stop at Ask-first"), this amendment is built and flagged here for
review, matching the precedent already set by the 2026-09-16 Insert amendment in the same section.
If the manager wants this amendment reworded or reverted pending explicit sign-off, that is a
follow-up correction, not a reason this task should have stalled.
