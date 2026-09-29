# Spec: status-anchor — CONTAINER RULE 2026-09-15, refined same day

**Boundary:** the tree is a container, the atom system is the runtime. This spec authors data
plus data-driven row content — never runtime semantics (no dispatch, validation, compose, or
resolve change). Chance rides in the emitted row's `WhenJson` (the carrier
AtomCompiler/AtomRunner/CostFunction already read; the importer defaults absent `when` to
`{}`, so the serializer emits it only for status rows). The `effectiveApplyScale` rescale
EVAPORATED as a follow-up: netFactor is already linear (`status.v1.json` netFactorScale 10,
T3.2) — SA-2 is now the ledger §4.3 re-verify, not an external build.

## Objective

Give `status.apply` families balanced numbers: (a) a chance-t1 and duration-t1 per member
family (20 named in
`bands.v1.json:powerBand.channelFamilyGroups.statusMagnitudeAndDuration.memberFamilies.statusApply`),
keeping the locked 1.75 (chance) / 1.40 (duration) ratios; (b) the deferred
`sharePermilleOwnership` entry (`spec-numerics.md:210-212` — rides existing tier-bands stems
unless P9 names more); (c) E43 resolves `status.apply` from the anchor (duration t1 direct —
durations don't take the share factor — with chance ladder beside it, scalar duration per the
fx-status.json precedent, no op/amount keys); (d) status m1 floor as data.
Success: the authored families expand with chance+duration (14/20 in v1 — 6 map to statuses
but have no family entries yet, a P1.2-class content gap, not refusals); nothing in atom
runtime semantics changes.

ASSUMPTIONS: (1) PoE's shape — flat duration base per family, chance quoted against the
power-vs-resist delta the resolver already computes (`ResistanceEvaluator.cs:190-217`); (2) the
anchor lives in a NEW file beside frozen `bands.v1.json` (never an edit); (3) duration unit is
ms (`Milliseconds` class), chance unit is ‰ (`PerMilleRatio` class).

## Tech Stack

.NET 8, C# 12. `StatusAnchorFile.cs` (parser), `FamilyExpansion.cs` (status branch),
`FamilyExpansionSeedFile.cs` (`when` arm), `FamilyExpandGen/Program.cs` (anchor wiring),
new anchor data file. Validator, composer, `StatusPolicy`, resolve folds: untouched.

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Core
Expander gate: dotnet run --project gk-forge/tools/FamilyExpandGen -- --check
Focused tests: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~FamilyExpansionTests"
Lint+validator: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContentValidationTests|FullyQualifiedName~AtomRowValidator"
Verify: powershell -File scripts/verify-change.ps1 -Paths @('<changed>') -Session <sid>
Audit (magnitude touched): python gk-core/scripts/audit-overflow.py ; python gk-core/scripts/audit-magic-numbers.py
```

## Project Structure

```
gk-data/packs/fusion/data/seed/items/_registry/status-anchor.v1.json (new, beside frozen bands.v1.json)
  → chanceT1Permille + durationT1Ms + familyStatus mapping + status m1 floor note
gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/StatusAnchorFile.cs → pure parser (data in, rows out)
gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs → status.apply branch (anchor read,
  duration ladder 1.40, scalar duration, no op/amount keys, when.chance stamped) + DurationRatioPermille
gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansionSeedFile.cs → emit `when` only when present
gk-forge/tools/FamilyExpandGen/Program.cs → load latest anchor, pass AnchorFor delegate
tests/.../Atoms/Generation/ → anchor parsing + branch + serializer-arm tests
```

## Code Style

The branch reads data and shapes rows — the same discipline as the Flat path, one rung narrower:

```csharp
// Durations do NOT take the share factor (share prices selection; the duration ladder prices
// growth). Scalar duration per the hand-authored fx-status.json precedent (2-5s floats).
if (family.KindId == "status.apply")
{
    var anchor = statusAnchorFor?.Invoke(family.Id); // null → refuse naming the anchor row
    m1 = anchor.DurationT1Ms; // ms direct
}
```

## Testing Strategy

xUnit: (a) a synthetic `status.apply` family expands with scalar duration == tier-scaled t1,
`status` id verbatim, no op/amount keys, `WhenJson.chance` == tier-scaled t1; (b) ratios 1.75
(chance) / 1.40 (duration) hold stepwise across tiers; (c) unmapped family refuses naming the
anchor file; (d) serializer omits `when` for plain rows, keeps it for status rows.
`FamilyExpandGen --check` exits 0. Never assert family
counts.

## Tunables

`chanceT1Permille` (‰), `durationT1Ms` (ms), per-family overrides, `sharePermilleOwnership` (‰),
status m1 floor (points). All in the new anchor file. T4
versioned; T5 missing-row rejection.

## Numeric types

`long` for chance ‰ and duration ms; `checked` tier scaling (`t1 × 1.75^(t−1)` overflows
`int` by tier 5 for large t1 — `long`, divide by 1000 last). Duration ms fits `int` physically
but travels the `long`-only pipeline — no narrowing.

## ActorHub gate

N/A — data + container stamping. No actor number produced, none consumed, no resolver read
changed. `BattleStatComposer` untouched.

## Boundaries

- Always: keep the 1.75/1.40 ratios (frozen shape); run the expander gate; map every statusId from SS3.4 (never inferred); serializer emits `when` only when present (T7).
- Ask first: per-family t1 overrides (tuning, not structure).
- Never: edit `bands.v1.json`; put chance in atom params; change dispatch/validation/compose/resolve semantics from this spec; ship a default anchor.

## Success Criteria

- [x] DONE 2026-09-15: 14/20 expand (6 map to statuses but have no family entries — P1.2-class gap); ratios hold stepwise; `WhenJson.chance` persisted through the file the binder reads; unmapped refusal names the anchor; `--check` exits 0.
- [ ] SA-2 (ledger §4.3 re-verify): confirm the suppression reason against linear netFactor and update the verdict — separate small task, same program.

## Open Questions

None — t1 values and the scale are the reviewed authorship in the diff.
