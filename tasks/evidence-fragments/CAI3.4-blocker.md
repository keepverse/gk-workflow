# `CAI3.4-blocker` — the two owed tests need both halves of one fact, and the halves never meet

Lane `combat-ai-3`, 2026-09-21. CAI3.4's blocker was recorded as "needs to observe a live `BattleRunState` —
a private nested class … whose own lines 20-31 record that the nesting exists to avoid a visibility change".
After CAI3.1's blocker turned out to be mis-stated (its seam had a reader and no writer), the same
re-reading was applied here. The answer is different, and the reason is worth having in the row.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The **read** half already has an in-fence pattern | `grep -n "internal static" gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | four `…ForTest` helpers at **`:1507, :1521, :1535, :1547`** that construct a run state and return view reads — `HeldActionIdsForTest` → `HeldActionsOf`, `EffectiveRungForTest`, `PositionAndSnapshotForTest` → `PositionOf`, `TryMoveTowardNearestEnemyForTest` → movement. So "read a view member from a test" is established house style, not a new mechanism | — |
| The read half cannot cover this | same read of those four | each constructs a **fresh** state and never runs a round loop, and `WentDowned` is only ever set by combat | — |
| …and no setup can start an actor downed | `grep -n "record BattleActorSetup" -A 45 gk-core/src/FusionRpg.Core/Battle/BattleModels.cs \| grep "get; init;"` | fields are `Key, Side, SpeciesId, TypeId, Level, ElementPrimary/Secondary, TraitIds, SpecimenId, MaxHp, Atk, Defense` — **`MaxHp` but no current HP and no downed/status field**. So a fixture cannot express "this ally is already down" | `BattleModels.cs:9-44` |
| The **combat** half has no hand-out | `sed -n '225,236p' gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs \| grep -cE "IBattleView\|Action<IBattleView>"` | **0** — `Resolve` runs the loop and discards the run state it built; there is no view probe, task parameter, or callback | — |
| Nothing else carries the fact | `grep -rn "DownedAllyKeysOf" --include=*.cs src/ tests/` | only the four implementors (`BattleRunState:874`, `FoggedBattleView:83`, `TraitAwareBattleView:80`, `BasicAttack:652`), `IBattleView`'s default at `:136`, `LawnBattleView:194`, and two test files. **No trace, sink or decision record carries live keys** — CAI2.4's records carry candidates and gate verdicts, not the view's live sets | — |

## What this means for the row

The two owed tests each need a *downed* actor **and** a live view read. `WentDowned` only arises from combat,
combat only runs inside `Resolve`, and `Resolve` hands nothing out — so the halves are in different places
and neither existing pattern spans them. The owner therefore chooses between two concrete options, and the
row now says so:

- **(a) A trailing optional view probe on `Resolve`** — the same shape as the `IStanceCheck? stance` seam
  `CAI3.1` gained this same day, and **one call after the round loop suffices** because the run state still
  holds `WentDowned` at that point. Cost: test-only surface on a public API (the repo's `…ForTest` convention
  exists to keep such surface `internal`, which a `Resolve` parameter cannot be).
- **(b) Make `BattleRunState` `internal`** — what `BattleRunState.cs:20-31` explicitly records as the thing
  the nesting was chosen *to avoid*. Cost: reversing a documented decision rather than adding a parameter.

Both are decisions, so neither was taken here. What changed is that the row now names them with `file:line`,
instead of asking for "a live `BattleRunState`" as if that were the only route.

## Not proved

- **The two tests were not written**, and nothing was changed in `BattleRunState.cs`, `BattleModels.cs` or
  `BattleEngine.cs`.
- **Option (a) was not prototyped**, so its "one call after the round loop suffices" claim rests on reading
  the code (the state outlives the loop and holds `WentDowned`) rather than on a run. If the owner takes (a),
  that is the first thing to confirm.
- **`RoleOf` still has no production caller** — its caller is `CAI3.5`'s `RpgHub.Resume` composition root in
  `gk-core/src/FusionRpg.Server/**`, outside this lane. Unchanged by this analysis.
