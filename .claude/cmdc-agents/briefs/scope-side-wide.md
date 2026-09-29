# Task: a side-wide owner key in StatApplyScope (fixes the patron aura buffing the enemy)

## The defect, already diagnosed — do not re-investigate it

A live probe read `combat.power.fire` back at 47 on the plant side (the correct magnitude), then
read the identical value back on the **zombie** side. `docs/architecture/creature-standalone/spec-patron-creature.md:27`
says the aura is for plant-side reads. So the aura buffs the enemy. Evidence:
`tasks/evidence-fragments/creature-standalone-pt7-live.md`.

Cause, already read in the code:

- `PatronSecondaryPlugin.cs` grants `OwnerKey = EffectOwnerKeys.Match`.
- `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs:52-53` returns `true` unconditionally for `"match"`,
  regardless of `StatSide`.
- `StatApplyScope` can express `plant:N` / `zombie:N` (side AND type id) and `match` (everything).
  It has **no side-wide key** — no way to say "every plant, any type". The aura asks for the only
  thing the grammar can express.

## The decision, already made by the owner's manager — do not re-litigate it

**Extend `StatApplyScope` with a side-wide owner key.** Do **not** re-platform the patron aura onto
`BattlefieldOwnSideReactor`. Reason: `StatApplyScope` is the single gate deciding whether a session
modifier applies to a resolve context. Moving one feature to a second mechanism because the first
cannot express its need leaves the gap for the next feature and creates a second place where
"which side does this apply to" is answered. SOLID's O is to extend the existing gate.

## What to build, in this order, one commit each

1. **The grammar.** Add the side-wide key to `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs`.
   `Normalize`, `Matches`, `IsKnownOwnerKey` and `IsMatchWide` must all agree about it.
   - Pick ONE spelling and use it everywhere. `plant:*` / `zombie:*` and `side:plant` / `side:zombie`
     are both defensible. Write a comment saying which you chose and why.
   - Decide deliberately whether the new key is match-wide for `IsMatchWide`. It is **not**
     (match-wide means "both sides"; this key means one side). Put the reason in a comment.
   - Add the matching constants to `EffectOwnerKeys` in the SAME commit.
2. **The fix.** Switch `PatronSecondaryPlugin` from `EffectOwnerKeys.Match` to the plant-side key.
3. **Tests.** In `gk-core/tests/FusionRpg.Core.Tests`, pin the CONTRACT (never a population count):
   - a side-wide plant key matches every plant regardless of type id;
   - it never matches a zombie;
   - `match` still matches both sides;
   - a patron-shaped grant does not apply on the zombie side (the case that would have caught this).

## Rules that bind this change

- **Do not touch** the `instance:` Hot guard (`IsInstanceOwnerKey`, lines 47-49). It is a separate
  invariant (S-INSTANCE-KEY-HOT).
- **Do not touch** the `player:` stub at lines 82-83. It returns match-wide on purpose. It is not
  your defect and changing it moves behaviour you are not proving.
- **A moved golden means your change is wrong.** Do not re-bless any golden. If a hash moves, stop
  and report it as a blocker.
- Do not run the live game. A separate QA pass re-proves this against the real game afterwards.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~Dominance|Category=BalanceGuard"`
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1`

Run them in the FOREGROUND. Never end a turn waiting on your own background job.
If a write fails with `user-mapped section open`, run `dotnet build-server shutdown` and retry —
that error is another lane's MSBuild holding the file handle, not a hang.
