# Spec: mechanism-carriage — ⛔ SUPERSEDED 2026-09-15 (ladder principle)

**Do not implement.** Same verdict as `spec-structural-rows.md`: ladder-valued Replace is dead —
on FlatSum channels the composer never reads Replace at all (silent zero or D6 load refusal),
and on principle a pinned absolute severs the channel from Θ. Retained as a reasoning trail
only. What P6.1 still needs (mechanism-*class* carriage — verbs, `status.apply`, priced by the
status anchor through the existing resolve path) is covered by `spec-status-anchor.md` +
`spec-tree-resolve.md`; no new spec required for it.

## Objective (original, retained for reference)

## Objective

Carry amount-less Replace/Flag rows (produced by `structural-rows`) from the tree catalog into
live `BoundDerivedAtom`s: the binder stores them as `NodeAtom`s, `TreeAtomSource.BoundAtomsFor`
resolves them, and the value a Replace asserts comes from the shared ladder — never an
invented number. Success: a real allocated structural node changes a number on lawn AND battle
through the existing Hub path; the 164-bound-empty-node gap closes for structural families.

ASSUMPTIONS: (1) Replace semantics = pin the channel TO the ladder value at θ_node
(`ChannelLadder`/`PowerLadder` read at the actor's own θ — "normalize to the curve"), Flag =
presence marker (amount 1 into `MaxFlag`); (2) per-family authored replacement values are
REJECTED — an authored absolute is an invented magnitude with no pin behind it; (3) multiple
structural atoms on one channel resolve in tier order, later tier wins, documented and
deterministic (this sidesteps the missing `Priority` field on `BoundDerivedAtom` without
changing its shape).

## Tech Stack

.NET 8, C# 12. `gk-core/src/FusionRpg.Core/PassiveTree/Catalog/NodeAtom.cs` (storage),
`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:42-96` (resolve),
`gk-core/src/FusionRpg.Core/Power/*Ladder*.cs` (value source, unchanged),
`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedComposer.cs` (FlatReplace/MaxFlag, unchanged).

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Core
TreeBinder gate: dotnet run --project gk-forge/tools/TreeBinder -- --check
Focused tests: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~TreeAtomSource|FullyQualifiedName~TreeBinder"
Live proof: deploy-play.py --paths @('<changed>') per local-dev runbook, then allocate a structural node and read back through the normal sheet path (never injector telemetry alone)
Verify: powershell -File scripts/verify-change.ps1 -Paths @('<changed>') -Session <sid>
```

## Project Structure

```
src/.../PassiveTree/Catalog/NodeAtom.cs → structural storage (ScaleAxis arm or KMicro convention)
src/.../PassiveTree/Resolve/TreeAtomSource.cs → structural branch in BoundAtomsFor/ResolveAmount
tests/.../PassiveTree/ → structural resolution tests (ladder-valued Replace, Flag presence, tier-order)
```

## Code Style

The structural branch reads the ladder the actor already reads — same call, no new curve:

```csharp
// Structural Replace pins the channel TO the ladder at this actor's own θ — the value is read,
// never authored. Later tier wins; order is documented, deterministic, and tested.
ScaleAxis.Structural when atom.Op is NodeAtomOp.Replace =>
    (double)ladder.Value(checked((int)thetaNode)) * fMultiplier,
```

## Testing Strategy

xUnit: (a) Replace resolves to exactly `ladder.Value(θ)` (no invented constant — assert against
the ladder's own output); (b) two structural atoms, higher tier wins; (c) Flag composes presence
through `MaxFlag`; (d) unknown op still refuses by name (keep the `:70-71` discipline loud, never
a silent `continue` for a NEW shape). Live: allocate a structural node on a test actor, read the
sheet value back through the normal path (live-probe standard — response body alone is not
proof). Never assert node counts.

## Tunables

None — the ladder pins come from `pin-table-v3`. This module authors no number.

## Numeric types

`long` θ, `double` ladder read (matches `ResolveAmount`'s existing arms); `checked((int)thetaNode)`
as today. Replace values are ladder magnitudes — same RANGE standing as every P(Θ) read.

## ActorHub gate

**Contribute** via the existing path: `BoundDerivedAtom` with `ContributionSourceIds.Tree(treeId,
nodeId)` (GG-49 FULL grammar, already shipped at `TreeAtomSource.cs:74`). No new producer, no
private fold, `BattleStatComposer` untouched (it is debt until fused, never a template).

## Boundaries

- Always: resolve Replace from the ladder at the actor's θ; tier-order documented in code;
  live-proof through the normal sheet read-back.
- Ask first: changing `BoundDerivedAtom`'s shape (e.g. adding Priority — default is to NOT change it).
- Never: author a replacement value; fabricate probe evidence (debug-API rule — RPG Server Debug
  scope, real record, normal-path read-back).

## Success Criteria

- [ ] Structural nodes bind, resolve ladder-valued (Replace) / presence (Flag).
- [ ] Tier-order deterministic and tested; unknown ops still named-refused.
- [ ] Live lawn AND battle read-back of one allocated structural node.
- [ ] `TreeBinder --check` exits 0; no magnitude-family row moves.

## Open Questions

None — the normalize-to-curve semantics is the reviewed core of this spec; alternatives
(authored values) are rejected above with reasons.
