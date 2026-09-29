# live-probe Task 23 — a post-deploy aptitude change never reaches an already-Bound live entity

**Claim to test:** re-allocating a Bound unique specimen's own aptitude points, while it is already
deployed and fighting on a live board, should move its live combat stats. If it does not, that is the
real defect half of Task 23 (the commander-scope half is a settled design decision, not a bug — see
`lawn-playable-map.md`'s own correction, quoted below).

## Live sequence (real game, real endpoints, real board)

1. Real specimen (`allpeater`, typeId 1347, via `POST /api/creatures/debug/grant` — the same mint path
   every real summon uses), levelled to 4 via real kills.
2. `POST /api/aptitudes/unique/allocate {"instanceId":"...","shares":{"Might":2}}` → `200`, `budget:18
   spent:2`.
3. `POST /api/unique/actors/{id}/deploy` on a real live board → `phase:"ActiveBound"`, real ptr
   `3007A100B40`.
4. **Baseline read**, real injector telemetry (`GET /api/debug/actor-derived?ptr=...`, polled via
   `/api/debug/events`): `combat.power.omni = 233`.
5. `POST /api/aptitudes/unique/allocate {"instanceId":"...","shares":{"Might":16}}` (mid-match, same
   live specimen, no redeploy) → `200`, `budget:18 spent:16` — the real allocation DID change
   server-side (8x more Might than step 2).
6. **Re-read the SAME live ptr**, same normal path, ~4s later: **`combat.power.omni = 233`, unchanged.**

## Verdict: the defect still reproduces live today, exactly as described in 2026-09-16

The server's own allocation moved from 2 to 16 Might; the already-Bound live entity's resolved combat
stat did not move at all. This confirms Task 23's own diagnosis is still accurate on the current tree:
`RpgClient`'s `"AptitudesUpdated"` (scope `"unique"`) handler enqueues `aptitudes.allocation.reload` →
`RefreshUniqueAptitudesAsync()`, which refreshes a CACHE keyed by Bound instance ids — it does not
recompose the already-resolved live entity's own applied stats.

## Not attempted: no fix landed here

This is explicitly named, already-specced, unbuilt work in a different program:
`docs/architecture/lawn-playable/spec-actor-liveness-refresh.md` /
`docs/architecture/lawn-playable-map.md:58` — "One typed invalidation channel server → injector, and
one per-actor revision that every cache keys on... a player switch, a level-up, an allocation, an
equip and a deploy each bump what they actually change, and the injector refreshes exactly that."
That module's own correction (`lawn-playable-map.md:88-92`) already separates Task 23's two halves
correctly: the **commander**-scope half ("a commander allocation genuinely does not apply mid-match")
is a settled design decision (`MatchCommanderSnapshotHolder.ResolveAllocation`'s own doc comment:
"frozen snapshot during a match, live cache outside"), not a bug — the module's job there is to make
that freeze *legible*, not to remove it. The **unique-specimen** half this probe just reproduced is
the real, still-open defect that module is scoped to fix. Building even a narrow point-fix here (as
was done for Task 24/25's `power.index.reload`) would mean improvising a piece of that same
one-revision-per-actor mechanism ahead of its own design — reported instead of attempted, per the
`live-qa` charter's own "bigger gets reported with file:line and the owning program" rule.

## File:line for the owning program

- `gk-fusion/src/FusionRpg.Injector/RpgClient.cs:108-124` — `"AptitudesUpdated"` handler enqueues
  `aptitudes.allocation.reload` unconditionally; no recompose of an already-resolved live entity.
- `gk-fusion/src/FusionRpg.Injector/RpgClient.cs:664` (`RefreshUniqueAptitudesAsync`) — refreshes the
  Bound-instance-keyed cache `spec-unique-lawn-wire.md`'s own AS-1.1 already covers; does not touch
  whatever holds the live entity's currently-applied combat stats.
- `docs/architecture/lawn-playable/spec-actor-liveness-refresh.md` — the owning, unbuilt module.
