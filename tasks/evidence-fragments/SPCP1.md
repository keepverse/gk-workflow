# Checkpoint 1 — one rule, one product, one projector (CLOSED)

| Criterion | Command | Result |
|---|---|---|
| The six-cell selector matrix, the four-path parity (after SP1.5) and the C1 guard are green | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionLayerSelector\|FullyQualifiedName~SpeciesAllocationSource"` / `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionLayerParity"` / `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ProgressionLayerSelectorGuard"` | **24/24, 2/2, 4/4** — all green, unaffected by wave 2/3's later work |
| The aptitude read is byte-identical under `LadderScale`. The atom-side movement list is recorded in SP2.2's commit | SP2.1 (`AptitudeReadFunctions.Magnitude` calls `LadderScale.Micro`, 15/15 tests) done; SP2.2 blocked at Ask-first, with the exact moved values (`2575->2576`, `753->754`) named in `tasks/evidence-fragments/SP2.2.md` | done — the list exists, per the spec's own instruction that a moved value stops at Ask-first rather than being silently re-blessed |
| Projector parity is exact over the grid. The 1a/1b partition has no loss and no overlap. `SpeciesPassiveAtomSource` is gone | SP3.4 (27/27 parity tests), SP3.5 (25/25 partition tests, the "2-core/3-roll -> 2 base + 3 player, union matches" proof), SP3.6 (file deleted, `grep -rn '"species-passive:'` src/ = zero hits) | done |
| `actor-hub-ssot.md` §8.1 carries the three species rows. `guard-actor-hub.ps1` is green | SP3.1's amendment (three producer rows, `species-base:`/`species-player:`/`species-empire:`); `.\scripts\guard-actor-hub.ps1` | **ACTOR-HUB GUARD OK** |

## What this checkpoint closes

Module 1 (`layer-source-selector`) and module 2 (`ladder-scale-parity`, SP2.1's half) and module 3
(`species-layer-projector`) are all built: one selector deciding which layers an actor's progression
source carries, one `k·P(Θ)` function every magnitude read shares, and one projector mechanism serving
1a/1b/2b instead of three half-mechanisms. SP2.2 (the `AtomCompiler.cs` kMicro-branch wiring) remains
**blocked at Ask-first** — a real, named, isolated decision for the manager, not a gap in this
checkpoint's own scope (the checkpoint's own second bullet only asks that the movement list exist and
be recorded, which it is).

## One additional stale-doc fix folded in here

`docs/architecture/solid-remediation/spec-species-carrier.md:150` — the todo's own SP3.7 handoff line
("handed to the `solid-remediation` session, or recorded under Checkpoint 1 if that session has
merged") — checked against `solid-remediation-map.md`'s own register: S4/S5/S6 are already marked
`fixed` there, with no active session left to hand this to. Recorded here instead: the doc's own GG-49
claim ("every contribution carries `species-passive:{speciesId}`") is now stale (SP3.6 retired that
id and deleted the file the section describes) — a correction blockquote was added in place, naming
the replacement ids and the map C3 defect it was closing, rather than leaving the next reader of that
spec pointed at a deleted identifier.

## Wave 3 also fixed two pre-existing regressions found by re-verification, not part of Checkpoint 1's
## own criteria but recorded for completeness

- SP3.2 follow-up: 5 pre-existing `ContainerKind` member-count pins across Core.Tests bumped 14->15
  (`tasks/evidence-fragments/SP3.2-followup-closed-vocab-pins.md`).
- SP3.6's own Guard.Tests regression (`PlayerSpeciesMaterialiseCallerGuardTests`) is recorded as an
  add-only blocker, NOT fixed (existing Guard.Tests files are add-only this session) —
  `tasks/evidence-fragments/SP3.6.md`'s addendum names the exact one-line fix needed.
