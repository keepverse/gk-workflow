# Step 6.3 (SP6.10, SP6.11) — the 2b cutover: BLOCKED, same root cause as wave 5

**Both tasks blocked, not started.** `SP6.10`'s own `deps:` line names `SP5.4` (module 5,
`empire-species-container`, trigger 3 — the boot reconcile over `EmpiresOf(save)`), which this lane
already recorded blocked (`tasks/evidence-fragments/SP5.1.md`, anchor7): `SpeciesLevelOf(SaveId,
EmpireId, typeId)` (`empire-progression` `EP4.13`) does not exist anywhere in `src/` (confirmed again
this session via `grep -rn "SpeciesLevelOf" gk-core/src/FusionRpg.Core/ gk-core/src/FusionRpg.Data/` — zero matches),
and `EP4.13` itself is still unchecked in `tasks/empire-progression-todo.md`. Nothing in this session's
work (SP6.1-SP6.9, nor the two `origin/features/mega-merge` merges) changed that — `empire-progression`
has not been touched by this lane or by any merged-in lane's work.

`SP6.10` cannot be built without `SP5.4`'s own output (`speciesLayers.empire`, the real 2b population
the transport's own field has stayed a hard-coded `{}` for since SP6.3, by this program's own explicit
scope boundary). `SP6.11` depends on `SP6.10` directly and is blocked transitively for the same reason,
plus its own live-proof requirement (a mid-run species level-up reaching a real lawn board) has the
SAME owner-only limitation SP6.9 already recorded.

**Per this lane's own hard-edge discipline: record the blocker precisely, never ship a partial
ordering.** Step 6.3 is left entirely unbuilt (no partial cutover), matching the todo's own explicit
warning: "Any moved value is a 6.3 defect, never a re-bless" — attempting a partial cutover without
module 5's real 2b population would either move nothing (a no-op that cannot be verified) or require
fabricating 2b content this program's own scope forbids.

This does not block the rest of wave 6: step 6.2 (SP6.2-SP6.9) is fully closed to the extent buildable,
and this lane proceeds to wave 7 next.
