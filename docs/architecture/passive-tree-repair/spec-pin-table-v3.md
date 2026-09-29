# Spec: pin-table-v3

## Objective

Publish `gk-core/data/tuning/power-scale.v3.json`: per-channel `(CMilli, PinValue)` pins at the
Θ=20 reference for every GameUnits channel the expander can price today but has no base for
(`arm1Max`, `arm2Max`, `combat.shield.capacity/pen/toughness.*`), a per-second pin for
`combat.shield.regen.*`, and per-channel pins for the SigmoidPoints / SigmoidMultiplierPoints
rate channels (`combat.accuracy/dodge/crit.rate/crit.resist/crit.damage/crit.resist.damage.*`)
— owner decision 2026-09-15: rates get pins too, not the divisor shortcut. Extend
`FlatReferenceBase` (`gk-forge/tools/FamilyExpandGen/Program.cs:138-144`) to read the new file, and add
the §10 inventory rows. Success: `FamilyExpandGen --check` prices every Flat family on a
covered channel; uncovered channels still refuse naming the channel (T5).

ASSUMPTIONS: (1) pin semantics = `PowerChannelTuning(CMilli, PinValue)` exactly as
`ChannelLadder` consumes it (`ChannelLadder.cs:8,31`) — no new shape; (2) rate-channel pins
are quoted in sigmoid point units against the fixed 100.0 divisor (`CombatPolicies.cs:10-12`),
so a pin is a neutral-scale anchor, not a growth curve; (3) `v2.json` stays frozen.

## Tech Stack

.NET 8, C# 12. `FusionRpg.Core/Power/ChannelLadder.cs` (consumer, unchanged),
`gk-forge/tools/FamilyExpandGen/Program.cs` (reader, extended), `gk-core/data/tuning/power-scale.v3.json` (new).

## Commands

```
Build: dotnet build gk-forge/tools/FamilyExpandGen
Expander gate: dotnet run --project gk-forge/tools/FamilyExpandGen -- --check
Focused tests: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~FamilyExpansionTests"
Verify: powershell -File scripts/verify-change.ps1 -Paths @('<changed>') -Session <sid>
Audit (magnitude touched): python gk-core/scripts/audit-overflow.py ; python gk-core/scripts/audit-magic-numbers.py
```

## Project Structure

```
gk-core/data/tuning/power-scale.v3.json   → new pin table (authored, tracked)
gk-forge/tools/FamilyExpandGen/Program.cs  → FlatReferenceBase reads v3 after v2-shaped lookup
gk-core/src/FusionRpg.Core/Power/         → unchanged (ChannelLadder already consumes the shape)
docs/architecture/power/ssot-power-scale.md → §10 rows for the new pins
gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/Generation/ → pin-loading + pricing tests
```

## Code Style

Reader code follows the existing `FlatReferenceBase` shape — a pure channel→`long?` function,
null for unknown channels. No defaults, no fallback curve:

```csharp
// v3 pins are (channel → game units at Θ=20). Unknown channel → null → honest refusal.
static long? V3ReferenceBase(string channel) => V3Pins.TryGetValue(channel, out var p) ? p.PinValue : null;
```

## Testing Strategy

xUnit in `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/Generation/`: (a) every v3 row loads and is positive;
(b) a Flat family on each newly-covered channel expands (was: `no referenceBaseGameUnits`
refusal); (c) an uncovered channel still refuses naming the channel. `FamilyExpandGen --check`
must exit 0 with emitted rows byte-identical except the newly-priced families (their rows are
new, nothing existing moves — T7). Guard: closed-vocabulary asserts only (channel ids the code
owns); never assert row counts.

## Tunables

All pins live in `power-scale.v3.json`, units game-units-at-Θ20 (`PinValue`) and per-mille
curve constant (`CMilli`). Versioned (T4); missing row = load rejection naming the channel (T5).

## Numeric types

`long` end to end (`PinValue`, `m1 = share × base / 1000` in `checked`); per-mille math divides
by 1000 last. Pins are Θ=20 magnitudes — far below overflow, but the pipeline they feed is
`long`-only by the repo's RANGE rule, so no narrowing anywhere.

## ActorHub gate

N/A — this module publishes tuning data consumed at bake time. No actor number is produced or
consumed here.

## Boundaries

- Always: regenerate nothing by hand — pins are authored (tuning files are hand-authored by brief),
  generated outputs (`gk-data/packs/fusion/data/seed/atoms/generated/**`) only via the real CLI; run the expander gate.
- Ask first: adding a channel the UnitClass ledger does not classify (that is `interval-ledger`'s job).
- Never: edit `power-scale.v2.json` or `bands.v1.json`; invent a growth curve; ship a default pin.

## Success Criteria

- [ ] `power-scale.v3.json` carries a row per listed channel, units stated, versioned.
- [ ] `FlatReferenceBase` reads it; previously-refused Flat families on covered channels expand.
- [ ] `FamilyExpandGen --check` exits 0; no pre-existing row changes value (T7).
- [ ] §10 rows added; `guard-power.py` (if present) passes.

## Open Questions

None — pin VALUES are the balance authorship the implementer proposes and the reviewer approves
in the diff, not spec questions.
