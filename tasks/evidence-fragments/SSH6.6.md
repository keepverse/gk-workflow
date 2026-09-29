# SSH6.6 — the optional `comboPricing` section and `ComboPricingProvenance.Check` (pure)

New `gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricingProvenance.cs`; `SocketTuning.Parse` gains the ONE
optional section and exposes `ComboPricingMaxRatioToRarityRouteMilli` +
`ComboPricingMeasuredAgainst`; the dump reads the parsed bound instead of the raw JSON.

`Check(measuredAgainst, loaded, ladderRungCount)` compares the FILENAME revision of each domain, the
structural `circuitSize` and the corpus digest, and names every field that moved (`socket.combo-pricing-stale`);
a multi-rung ladder with no measurement is refused by name (`socket.combo-pricing-unmeasured`). A
one-rung ladder with no `comboPricing` at all is the shipped state and is unaffected.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `SocketTuning` parses the optional `comboPricing` and exposes `ComboPricingMeasuredAgainst` | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~ComboPricing\|FullyQualifiedName~SocketGeometry"` | **48 passed / 0 failed**. `The_optional_combo_pricing_section_parses_and_is_absent_today`: the shipped revision exposes `null`/`null`; a mutated copy with the section exposes `1000` and all five provenance fields; a non-SHA-256 digest is refused by name |
| `a_multi_rung_ladder_refuses_unmeasured_pricing` | (above) | 3 rungs + no provenance → `UnmeasuredRule`, detail contains `3 rungs` and `combo-budget` |
| `a_ladder_published_after_the_measurement_is_refused_until_re_measured` | (above) | `strainSpliceVersion measured 1, loaded 2` → `StaleRule`; the same check passes at `2/2`; `materialsVersion`, `circuitSize`, `combinationCorpusDigest` and `socketsVersion` are each called out by name |
| `provenance_versions_are_filename_revisions_not_the_internal_version_field` | (above) | reads the PREVIOUS sockets revision by listing (never a filename literal — the SSH5.2 guard catches those), asserts its internal `version` is **above** the current one's, then refuses a measurement recorded against that internal field while the loaded filename revision is 2, and passes the same measurement at the filename revision |
| `a_single_rung_ladder_loads_without_provenance` | (above) | `Check(null, loaded, 1)` is `null`; a matching provenance at one rung is `null` too |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs','gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricingProvenance.cs','tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs','gk-forge/tools/ItemSeedValidator/ComboBudgetDump.cs') -Session strain-splice-host-20260921"` | exit **0** — `core-fallback` → **FusionRpg.Core.Tests 15091 passed / 0 failed**; `itemseedvalidator-fallback` → **97 passed / 0**; `test-substrate` guard OK |
| overflow audit still clean | `python gk-core/scripts/audit-overflow.py` | exit **0**, `A2=0 A3=0 A4=0 A5=0 A6=1` (pre-existing), 0 findings naming the new file |
| the report still runs against the parsed bound | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release -- gk-data/packs/fusion/data/seed/items --combo-budget-dump` | `maxRatioToRarityRouteMilli: 1000` (the plan's default, now read through the parser rather than the raw JSON) |

## Not proved / open

- **The boot does not call `Check` yet** — that is SSH6.7 (it computes the corpus digest and the loaded
  revisions after every input is loaded). Nothing here is wired into `Program.cs` on purpose.
- No `sockets.v3.json` exists, so the section has never been published: SSH6.8 writes it with
  `measuredAgainst` copied from a passing report.
- The digest's own computation is SSH6.7's; this row only validates its SHAPE.
