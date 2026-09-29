# Spec: structural-rows — ⛔ SUPERSEDED 2026-09-15 (ladder principle)

**Do not implement.** Owner verdict after reading `ssot-power-scale.md`: Replace contradicts the
ladder at principle level — every number is `f(Θ)` (linear for contests, `P(Θ)` for magnitudes);
Replace substitutes a constant, which freezes one side of a parity contest or rots as `P(Θ)`
climbs past it. A pin *anchors the function* (§4.3); Replace *discards* it. Retained as a
reasoning trail only. Successor decision: A2 → option (b), exclude — see P2.3/P5.1 in
`tasks/passive-tree-repair-todo.md`. The one surviving half (Flag on `status.immune`, a
presence, not a magnitude) needs no spec: the Flag class already carries it.

## Objective (original, retained for reference)

## Objective

Emit the 19 refused `stat.derived` Replace/Flag families (12 Replace + 7 Flag, element-templated
channels, live census 2026-09-15) as **amount-less rows**: E43 skips the tier-magnitude ladder
for structural ops (frozen rule: Replace/Flag carry no tier-band magnitude) and emits the row
with channel + op + tier and NO amount; `AtomRowValidator` accepts an amount-less row exactly
when op is Replace/Flag on `stat.derived` (extending `ValidateOp`'s kind-aware discipline,
`AtomRowValidator.cs:299-315` — `StatOps`/`DerivedOps` stay the vocabularies). Success: the 19
refusals become rows; every other refusal is unchanged; no amount is invented anywhere.

ASSUMPTIONS: (1) amount-less is an emission shape, not a schema change — `stat.derived`'s
`amount` ParamDef stays Required, and the validator exempts structural ops explicitly (the
exemption names Replace/Flag, never a null blanket); (2) opWeight gate: structural ops bypass
the `opWeightPermille` lookup (a verb-like bypass, same discipline as P2.2's `OwnsModifierOp`
— weight identity, share from channel only); (3) element-templated channels stay templates
here — pool resolution is `tree-pool-resolve`'s job, not this module's.

## Tech Stack

.NET 8, C# 12. `gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs` (emission),
`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomRowValidator.cs` (exemption).

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Core
Expander gate: dotnet run --project gk-forge/tools/FamilyExpandGen -- --check
Focused tests: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~FamilyExpansionTests"
Validator tests: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AtomRowValidator"
Verify: powershell -File scripts/verify-change.ps1 -Paths @('<changed>') -Session <sid>
```

## Project Structure

```
src/.../Generation/FamilyExpansion.cs → structural-op emission branch in TryReferenceBaseM1/callers
src/.../Atoms/AtomRowValidator.cs     → amount exemption for Replace/Flag on stat.derived
tests/.../Atoms/Generation/           → emission tests (19-family shape, no-amount proof)
tests/.../Atoms/ (validator)          → exemption tests + negative tests (amount-less Flat still refused)
```

## Code Style

The branch is explicit and kind-aware, following `OwnsModifierOp`'s precedent:

```csharp
// Structural ops carry no tier-band magnitude (bands.v1.json, frozen): the row is emitted
// amount-less. The amount is genuinely absent — never zero, never a default.
if (family.KindId is "stat.derived" && family.Op is "Replace" or "Flag")
    return EmitStructuralRow(family, sharePermille /* priced, not measured */);
```

## Testing Strategy

xUnit: (a) all 19 live families emit rows with NO amount key and op verbatim; (b) an amount-less
Flat/Increased/More row is still refused (the exemption is op-shaped, not null-shaped); (c) an
amount-less Replace on a NON-derived kind is still refused; (d) `FamilyExpandGen --check`
exits 0 with exactly the 19 families moved from refused to emitted (census delta asserted as a
set-difference on family ids the corpus owns — stable across generations, not a count).
Committed generated files regenerate through the real CLI (never hand-edited).

## Tunables

None — this module authors no number. The share ladder is unchanged.

## Numeric types

No new magnitudes. `sharePermille` stays `long`/`checked` as today.

## ActorHub gate

N/A — rows are emitted, not composed. Composition is `mechanism-carriage`'s spec and must pass
this gate there.

## Boundaries

- Always: assert absence of amount (key missing), never amount==0; run the expander gate;
  regenerate through the CLI.
- Ask first: extending the exemption past Replace/Flag (new op = reviewed vocabulary change).
- Never: invent a magnitude for a structural op; hand-edit `gk-data/packs/fusion/data/seed/atoms/generated/**`.

## Success Criteria

- [ ] 19 families emit amount-less rows; all other refusals byte-identical.
- [ ] Negatives (amount-less Flat; Replace off-derived) refuse by name.
- [ ] `--check` exits 0; regenerated corpus committed via CLI.

## Open Questions

None.
