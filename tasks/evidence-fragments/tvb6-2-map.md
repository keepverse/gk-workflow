# TVB6.2 — the production map now binds; the per-area owner set it supports

TVB-F18's fix (b75d8096a) plus building 21 test projects turns the map from a floor into real
evidence: `dotnet run --project gk-core/tools/TestSplitAnalyzer -c Debug -- --production-map --project
gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --test-projects tests --configuration Debug --format md`
reports **2741 declared types across 27 referenced areas**, 59 test projects scanned (37 skipped for no
build output).

| Reading | Result |
|---|---|
| areas referenced | **27** |
| areas referenced by exactly ONE project | **11**, all the residual `gk-core/tests/FusionRpg.Core.Tests` — Activity, Creatures, Delve, Expeditions, Items, Notify, PassiveTree, Progression, Scope, Vfx, World |
| areas referenced by SEVERAL projects | **16** — Effects 12, Stats 9, Battle 7, Combat 7, Match 6, Power 6, ... |

## What that means for K1

The 11 single-project areas can take a real owner row (`gk-core/src/FusionRpg.Core/<Area>/**` -> the residual
project), which narrows them from the whole `core` group to one project. The 16 multi-project areas need
a group of exactly the projects the map shows (K1's own rule), and for the widest of them (`Effects` 12
members) that group is close to the whole `core` group, so the narrowing there is small by evidence
rather than by choice.

## Two blockers a first attempt hit (registry reverted, nothing landed)

1. `gk-core/src/FusionRpg.Core/Notify/**` already has a narrower owner (`notify-core-domain`), so a blanket
   per-area row is ambiguous there - the area list must be intersected with the areas that have no
   owner today.
2. Adding the residual as a project id (`core-residual`) needs the insertion anchored inside the
   `projects` object; the first attempt landed it where the guard reported `unknown project`, so the
   row set is not written until that is done properly.

No registry change in this commit: the guard is green on the unchanged registry and the row is not
half-written.

## Landed: the seven single-project areas (K1, additive)

`core-residual` (`gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj`) is now a project id, and seven
areas the map shows referenced ONLY by it own their subtree:

`gk-core/src/FusionRpg.Core/{Activity,Delve,Expeditions,PassiveTree,Progression,Scope,Vfx}/**` -> `core-residual`.

Guard: `VERIFICATION BOUNDARY GUARD OK` at **377 boundaries** (370 + 7; the project id is not a boundary).
Four further candidates were skipped because they already have narrower owners - `Creatures`, `Items`,
`Notify` (`notify-core-domain`) and `World` - which is the intersection K1 needs: a blanket per-area row
there would be ambiguous.

Still open: the 16 multi-project areas need a group of exactly the projects the map shows (Effects 12,
Stats 9, Battle 7, Combat 7, Match 6, Power 6, ...); each group is a new project id plus one owner row.
