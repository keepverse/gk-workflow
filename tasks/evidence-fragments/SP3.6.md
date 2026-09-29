# SP3.6 — Retire `SpeciesPassiveAtomSource`; the interim sheet join goes through the projector

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SpeciesPassiveAtomSource.cs` is deleted | `git rm` | done | `src/FusionRpg.Core/Battle/SpeciesPassiveAtomSource.cs` (deleted) |
| Its tests move to `SpeciesLayerProjectorTests` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector"` | **19/19 passed** | `tests/FusionRpg.Core.Tests/Battle/SpeciesPassiveAtomSourceTests.cs` deleted; equivalent coverage already landed in SP3.5's `SpeciesLayerProjectorOneTwoBTests` |
| No `species-passive:` SourceId minted anywhere in `src/` | `grep -rn '"species-passive:' src/ --include="*.cs"` | **zero hits** | grep output |
| The interim sheet join emits `ProjectBase` + `ProjectPlayerMod` rows | code edit | done | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs` |
| Sheet regression stays green | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet"` | **12/12 passed** | test output |
| `guard-actor-hub.ps1` green | `.\scripts\guard-actor-hub.ps1` | **ACTOR-HUB GUARD OK** | script output |
| `GetSpecimenLedgerRoll`'s own regression stays green after its return-type widening | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenMaterialisedRoll"` | **5/5 passed** | test output |
| Server + Data + Core build clean | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` | 0 errors | build log |

## What shipped

- **`src/FusionRpg.Core/Battle/SpeciesPassiveAtomSource.cs`** and
  **`tests/FusionRpg.Core.Tests/Battle/SpeciesPassiveAtomSourceTests.cs`**: deleted. The map's own C3
  defect (a SourceId minted outside `ContributionSourceIds`, with no `FictionLabel` arm, unable to tell
  1a from 1b) is closed.
- **`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.PlayerSpecies.cs`**: new `RpgStore.LedgerRoll(SpeciesId,
  Instance, Mechanism)` record — `GetSpecimenLedgerRoll`'s return type widens from the shared
  `MaterialisedRoll` (SpeciesId + Instance only, also used by the unrelated eager-boot
  `SpeciesMaterialiser`) to also carry the ledger row's `SpeciesModMechanism`, which
  `SpeciesLayerProjector.ProjectPlayerMod` needs and `MaterialisedRoll` had no reason to carry.
- **`gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`**: the interim species join now calls
  `store.GetContainer("species-passive." + roll.SpeciesId)` for the template, then
  `SpeciesLayerProjector.ProjectBase(...)` + `.ProjectPlayerMod(...)`, converting each
  `ProjectedLayerRow` (always `LayerValue.Fixed` for 1a/1b, per rule 2) into the existing
  `BoundDerivedAtom` shape the compose pipeline already expects. A missing template is skipped
  silently (same "null answer, no guess" discipline the rest of this file already follows).
- **`gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs`**: the `SpeciesBase` doc comment's
  citation of the now-deleted `SpeciesPassiveAtomSource.cs:42` is updated to say "now-retired... SP3.6
  deleted it" rather than pointing at a file that no longer exists.

## Addendum (found by a later whole-Guard.Tests run, not by the scoped Verify command above): a
## Guard.Tests regression this task caused, blocked by the add-only rule, not fixed here

`dotnet test gk-core/tests/FusionRpg.Guard.Tests` (whole suite, run for the coordinator's separate
whole-project re-verification) is **442/443** — the one failure is
`PlayerSpeciesMaterialiseCallerGuardTests.The_rolled_species_instance_reaches_a_composer`
(`gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:78-79`), which asserts
`UniqueActorHubCompose.cs`'s source text contains the literal substring
`"SpeciesPassiveAtomSource.DerivedAtomsFor"`. This SP3.6 commit replaced that exact call with
`SpeciesLayerProjector.ProjectBase`/`.ProjectPlayerMod`, so the literal no longer appears.

The guard's own comment (lines 72-74) already anticipated exactly this shape of change once before
("SP0.5 repointed the join... the composer requirement this test guards is unchanged, only the method
name moved") — the correct fix is a **one-line string update** (the literal it checks for), the same
kind of rename the guard's own history already accepts as legitimate. It is **not fixed here**: the
coordinator's standing rule for this session is that existing Guard.Tests files are add-only while the
manager reviews this lane's two prior edits to them — recorded as a ledger blocker note instead
(`tasks/summoner-convergence-lane-b-ledger.jsonl`, "Guard.Tests add-only regression, SP3.6").
`gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet"` (the todo's own SP3.6 Verify
command) does not run this file, which is why it was not caught until the broader run.

## Why "for a fuser the values are equal" holds, verified rather than assumed

`ProjectBase` reads the template's core atoms at their DEFINITION values, never touching the instance's
own frozen copy of that same core row. This is only value-neutral versus the old single-pass
`SpeciesPassiveAtomSource` (which read `instance.Atoms` uniformly, instance-value-first) if the
content-scale ratio baked into a real fuser's frozen core row is always ×1.000 — traced this through
`RpgStore.Fusion.cs:329`: the real fusion-pick pipeline always calls `InstanceProducer.Compose` with
`thetaContent = PowerTuningHub.Tuning.Curve.PinIndex` (the SAME pin every time, never a per-player or
per-species value), so `ContentScale.Milli(PinIndex, tuning)` is a fixed constant for every real
species-passive materialisation in this domain today — confirmed, not assumed, before relying on it.

## Follow-up noted, not fixed here

`SpeciesModRow.Mechanism` has exactly one member (`SpeciesModMechanism.FusionPick`) today — the
`.Token()` call in `UniqueActorHubCompose.cs` is future-proofed against a second mechanism landing
later (the enum's own doc comment: "a second mechanism is a reviewed change"), not exercising branching
logic that does not exist yet.
