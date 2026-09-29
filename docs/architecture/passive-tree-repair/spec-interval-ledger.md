# Spec: interval-ledger

## Objective

Classify `attackInterval` / `produceInterval` as `Milliseconds` (owner decision 2026-09-15 —
intervals are durations between events) in the UnitClass ledger, and grow real
`channel-policy/defaults.json` entries for them beyond the 2-entry stub. Success: a Flat
family on either channel prices through E43's Flat path against a documented ms reference;
the ledger's thirteen classes become fourteen only if the implementer proves Milliseconds
cannot hold them (default: it holds — no new class).

ASSUMPTIONS: (1) Milliseconds semantics = authored ms (`definitions.md §2`), consumed as a
duration, never scaled by Θ or P(Θ) (intervals do not grow with power — a faster attacker at
high Θ is a balance effect authored per channel, not ladder math); (2) the stub's two rows
(`direction: 1`) are kept and completed, not replaced.

## Tech Stack

.NET 8, C# 12. Docs-led module: `docs/design/spec-magnitude-and-units.md` (ledger row),
`gk-data/packs/fusion/data/seed/channel-policy/defaults.json` (entries), `gk-forge/tools/FamilyExpandGen/Program.cs`
(ms reference arm, only if E43 needs one beyond the pin table).

## Commands

```
Build: dotnet build gk-forge/tools/FamilyExpandGen
Expander gate: dotnet run --project gk-forge/tools/FamilyExpandGen -- --check
Ledger check: grep -n "attackInterval" docs/design/spec-magnitude-and-units.md
Verify: powershell -File scripts/verify-change.ps1 -Paths @('<changed>') -Session <sid>
```

## Project Structure

```
docs/design/spec-magnitude-and-units.md → Milliseconds row gains the two channels + consumer
gk-data/packs/fusion/data/seed/channel-policy/defaults.json → completed entries (direction + reference + reason)
gk-forge/tools/FamilyExpandGen/Program.cs → ms referenceBase arm (only if pin-table-v3 doesn't cover it)
```

## Code Style

Policy entries carry their reason inline (T3 — no bare literals on the balance surface):

```jsonc
{ "channel": "attackInterval", "direction": 1, // lower ms = faster; never ladder-scaled
  "referenceMs": 1500 }
```

## Testing Strategy

xUnit: (a) ledger test asserts both channels resolve to `Milliseconds` (closed vocabulary the
ledger owns — pinning literals allowed with the why comment); (b) a Flat family on each
channel expands with an ms magnitude; (c) channel-policy loads with reasons present.
`FamilyExpandGen --check` exits 0.

## Tunables

`referenceMs` per interval channel, in `channel-policy/defaults.json` (authored registry,
tracked). Unit ms. Missing row = T5 refusal.

## Numeric types

`long` ms end to end. Intervals near zero are a divide risk downstream — the spec requires the
reference to state its floor and the consumer to guard it, but no clamp on authored values
(no silent clamps; a below-floor value refuses by name).

## ActorHub gate

N/A — classification + policy data. No actor number produced or consumed.

## Boundaries

- Always: name the verified consumer in the ledger row (ledger rule — every class has one).
- Ask first: creating a fourteenth UnitClass (default is Milliseconds; new class needs proof).
- Never: ladder-scale an interval; hand-edit generated outputs.

## Success Criteria

- [x] DONE 2026-09-15: Both channels classified with a verified consumer cited.
- [x] DONE 2026-09-15: Policy entries completed with reasons; stub status gone.
- [x] DONE 2026-09-15: Flat families on both channels price; `--check` exits 0.

## Open Questions

None.
