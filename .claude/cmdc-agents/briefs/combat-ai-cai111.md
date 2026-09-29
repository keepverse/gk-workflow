# Task: combat-ai CAI1.11 (trait decorators) then CAI1.12 (resolvable-here)

Program: `tasks/combat-ai-plan.md` / `tasks/combat-ai-todo.md`. Read your task rows there first.
Spec: `docs/architecture/combat-ai/spec-intent-router.md`.

CAI1.1 through CAI1.10 are already merged into `features/mega-merge`. Start from HEAD.

## CAI1.11 — the design question is already answered

A previous lane recorded CAI1.11 blocked. It is **not** blocked. Its analysis of the constraint was
right, and its two proposed fixes were both wrong.

The constraint (correct): `SiegeAiIntentSource` binds `IBattleView` at construction
(`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs:113`) and owns a persistent
`RetargetLedger` / `BattleTrace`, so it cannot be cheaply rebuilt per decision the way
`StubIntentSource` can. So `bloodthirsty`'s pre-decision view decoration has no obvious way in.

The two rejected fixes: widening `IIntentSource.TryDeclare` with a view-override parameter, or
making a policy's view swappable per call. Both push "which view does this decision see" into the
intent-source contract, forcing every implementer to care about it.

**The ruling: decorate `IBattleView`, not `IIntentSource`.**

Why it works: every `IBattleView` method already takes an `actorKey`, and `TryDeclare` reads the
world exclusively through `_view` (`HeldActionsOf`, `PositionOf`, `FactsOf`, `SideOf`, `DerivedOf`,
`LiveActorKeys`, `GarrisonedStructureKeyOf`). A view that wraps the real one and applies a trait's
pre-decision decoration per actor therefore gives `bloodthirsty` exactly what it needs — no
interface change, no per-call swap, persistent ledgers untouched. The source keeps one view for its
whole life; that view is simply trait-aware.

This is an existing pattern, not a new one: `gk-core/src/FusionRpg.Core/Actions/FoggedBattleView.cs` is
already a decorating `IBattleView` with a per-actor `IsKnownToViewer` predicate. Composing two view
decorators is ordinary.

`loyal`'s post-decision redirect is a different seam and stays in `IntentRouter.TryDeclare`,
applied to the resolved target. Two traits, two seams, each at the layer that owns what it changes.

**Check the ruling against `spec-intent-router.md` §2 before you build.** The ruling is about where
the seam goes; it does not claim the spec already says so. If the spec actively forbids a decorating
view, or a trait needs something no `IBattleView` method exposes, STOP and report that with
`file:line`. That is a real spec gap, not something to work around.

**CAI1.11 is H1 — it may move siege behaviour.** So:
- Write a predicted-delta note in the commit body: what you expect to move and why.
- Run the golden filter and state exactly what it printed.
- Anything outside your predicted delta must stay byte-identical. If it does not, stop and report.

## CAI1.12 — resolvable-here

Its only dependency is CAI1.1, which is merged, so it is unblocked. Do it after CAI1.11, or first if
CAI1.11 turns out to be genuinely spec-blocked.

## Rules

- One logical change per commit: code + evidence + ledger line together.
- Re-anchor doc citations in the SAME commit as any code move that breaks them. The guard
  `scripts/guard-doc-citations.ps1 -Strict` will catch you otherwise, at merge time, in someone
  else's lane.
- Never delete a type without confirming zero production callers first, and say in the commit body
  how you confirmed it.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~IntentRouter|FullyQualifiedName~SiegeAi|FullyQualifiedName~CoreIntentPolicy"`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~Dominance|Category=BalanceGuard"`
- `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`
- `python gk-core/scripts/guard-battle-responsibility.py`

Run them in the FOREGROUND. Never end a turn waiting on your own background job.
On `user-mapped section open`, run `dotnet build-server shutdown` and retry — it is another lane's
MSBuild holding the handle, not a hang.
