# LO0 — read spec-loam-fe-2.md S1 and L44-L50; Phase 6 is stale

**Finding: Phase 6 (LO0 + L44-L50) is not a remaining gap — read first, corrected before building
anything.** `backlog-clear-plan.md` was written 2026-08-31; `spec-loam-fe-2.md` and `loam-todo.md:1361`
record the owner superseding `loam-fe-2` on **2026-09-03** (three days later) in favour of `world-stage`,
which owns the write-surface work too. `backlog-clear-todo.md`'s Phase 6 was never refreshed against
that and still framed L44-L50 as live work.

| L-task | Verified delivered under `world-stage` | Citation |
|---|---|---|
| L44 (5 fields + TS mirror) | `carriedLoam`/`role`/`constructionTurnsRemaining`/`wardenBindingId`/`neglectedTurns` all present | `world-stage-todo.md:128,780-781,2933` |
| L45 (turn-playback narration) | `turnPlayback.ts` moved to `stages/world/`, loam/legion vocabulary covered | `world-stage-todo.md:3405-3462` |
| L46 (Sustain/Build UI) | Real `WorldCommand` kinds wired into the unified targeting/command surface | `stages/world/targeting/targetingState.ts`, `worldSelection.ts`, `lib/bus/world.ts` |
| L47/L48 (Ward Core+endpoint) | `WardenResolver.cs`, `WorldCommandKinds.BindWarden`, endpoint tests | `world-stage-todo.md:1180-1262` |
| L49 (Ward web UI) | `BindWardenDialog.tsx` + test, on disk | confirmed via `find` |
| L50 (Prospecting wire+UI) | `WorldStateDto.ProspectedSectorIds`, `MovementPolicy.Dowse` | `world-stage-todo.md:637-660,1282-1317` |

`world-stage-todo.md` independently checked: **0 open checkboxes, 141 done.**

**Disposition:** Phase 6 closed as superseded-and-delivered, not attempted here — building L44-L50
under `backlog-clear` now would fork already-shipped `world-stage` work. No code change; docs-only
correction to `backlog-clear-todo.md`.
