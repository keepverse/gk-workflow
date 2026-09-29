# Mega-merge QC 18 — Core split-project sweep on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Every `FusionRpg.Core.*.Tests` project run individually. No live game.

## Verdict: GREEN (67/68 projects; Expeditions tracked separately)

All projects below: `Failed: 0`. Full per-project counts were recorded in-session;
largest: Atoms 1356, ActorHub 498, PassiveTree 405, Stats 291, ClassSystem 238,
Match 182, Status 170, Vfx 172, Power 145, Overlay 131, Commanders 66, Dungeon 61,
plus 46 smaller projects (1–131 tests each) — all green.

Projects covered in earlier QC reports (not re-listed): Core.Tests 9746,
Core.Items.Tests 1470, Core.Progression.Tests 33, RpgProgressionBalance 4,
Core.Notify 41, Core.Lawn 15, Combat splits 23, Core.Expeditions (see below).

## Sole exception

`FusionRpg.Core.Expeditions.Tests`: order-flaky 11/38 (see
`mega-merge-qc-15-expeditions-flaky.md` — global Almanac-floor window vs parallel
classes; deterministic 37/37 minus the poisoner). Product code exonerated.
Routed, not fixed here.
