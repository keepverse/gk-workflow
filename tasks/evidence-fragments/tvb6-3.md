# TVB6.3 — K2 re-key: no change is correct at this head

K2 narrows each focused `core.*` boundary's `project` to the project (or smallest group) whose
directory holds its trait. Measured at the merged head (`2a270ad81`, split 33/68), **every one of the
seven named boundaries' traits still lives in the residual `gk-core/tests/FusionRpg.Core.Tests/**`**, so the
`core` group is already the correct owner and there is nothing to re-key:

| Boundary | Trait | Trait site(s) at this head |
|---|---|---|
| `battle-effect-math` | `core.battle-effect-math` | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleEffectMathTests.cs:30`, `gk-core/tests/FusionRpg.Core.Tests/Combat/OwnerElementFallbackTests.cs:24` |
| `elemental-resolver` | `core.elemental-resolver` | `gk-core/tests/FusionRpg.Core.Tests/Combat/ElementalResolverTests.cs:18`, `gk-core/tests/FusionRpg.Core.Tests/Combat/PerElementAvoidanceTests.cs:23` |
| `core-lawn-attrition` | `core.lawn-attrition-ladder` | `gk-core/tests/FusionRpg.Core.Tests/Battle/LawnPermadeathLadderTests.cs:16` |
| `core-creature-catalog-generator` | `core.creature-catalog-generator` | `gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureCatalogTests.cs:8` |
| `core-creature-corpus-dump` | `core.creature-corpus-dump` | `gk-core/tests/FusionRpg.Core.Tests/Creatures/CorpusDumpTests.cs:15` |
| `tools-combat-sim` | `core.combat-sim` | none in `tests/**` or `tools/*.Tests/**` at this head |
| `tools-prove-predictor` | `core.prove-predictor` | none in `tests/**` or `tools/*.Tests/**` at this head |

Command: `rg -n --no-heading 'Trait\("VerificationId"' tests tools --glob '*.cs'` filtered to the five
`core.*` ids (printed above), plus the registry read for the seven boundaries' current
`project`/`verificationId`/`guards` (all still `project: core`, guards preserved).

**Why no narrowing now.** Narrowing a boundary to the residual project *before* the split has moved
those folders would make it stale the moment `Battle/`, `Combat/` or `Creatures/` moves — the trait
would no longer be found and the boundary would verify less, which is the exact hazard
`core-registry-rekey` exists to avoid ("depends on `core-split-wiring`: the split has landed"). The
`core` group finds the trait wherever it is, so nothing verifies less in between; this task closes when
the split lands, at which point each trait's new project directory is the re-key target.

## Rows this task records

- **TVB6.3** — no change; evidence above. Re-open with the split (33/68 at this head).
- **TVB6.4** — not attempted: K3 needs a per-orphan production file read from its test class
  (`core.advanced-effect-clock`, `core.battle-mode-parity`, `core.kill-attribution`,
  `core.siege-estimator-parity`, `core.species-term-compose`, `core.vocabulary-single-declaration`), and
  its Verify line is the registry plus `docs/architecture/test-verification-boundary-ideal.md`.
- **TVB-F18** — the standing gate for TVB6.2's owners; instrument the compilation, do not add a sixth
  reference source.

No commit for a re-key: there is no re-key to make.

---

# TVB6.3 (K2) — the re-key, 2026-09-23 (lane `tvb60`, split 67/68)

The 2026-09-21 reading above says this task closes when the split lands, and it has: 67 of the 68
manifest projects are applied. The same scan, re-run, finds **24** focused boundaries still on the full
`core` group — the 7 the acceptance names plus 17 more the identical rule finds.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the set to re-key | trait scan: every focused boundary with `project: core`, then `Trait("VerificationId", …)` in `tests/**/*.cs` | **24** boundaries, not 7 — the same rule finds the rest | this file |
| re-keyed | the scan's own mapping written into the registry | 24/24; `focused` boundaries still on the full `core` group: **0** | `gk-core/scripts/verification-boundaries.v1.json` |
| K-T2 (C7 group rule) | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` — the guard's own rule (`:151-161`) requires ≥1 group member to carry the boundary's trait, so the re-key is checked, not asserted | — |
| one path per new owner | `verify-change.ps1 -Paths <p> -PlanOnly` | `LawnPermadeathLadder.cs -> core-lawn-attrition (focused)`, `test: core-residual core.lawn-attrition-ladder`; `EffectBag.cs -> battle-effect-math (focused)`, `test: core-residual core.battle-effect-math`; `gk-core/tools/CombatSim/Program.cs -> tools-combat-sim (focused)`, `test: core-combat-sim-tests core.combat-sim [Balance, ClassSystem]` | — |
| K-T4, an unmapped Core path | `verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Saves/SaveId.cs -PlanOnly` | `core-fallback (module)`, `test: core` with all 68 members — never less than before | — |
| guards kept | registry diff | `battle-effect-math` still carries `battle-responsibility` + `funnel-delta`; no boundary lost a guard | — |
| the workflow/group cases | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary\|FullyQualifiedName~CoreTestProjectPolicy"` | `Passed!  - Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 5 m 48 s` | — |

Two new project groups were needed for traits that live in two directories: `core-combat-sim-tests`
(`Balance` + `ClassSystem`) and `core-drop-tables-tests` (`Items` + the residual) — the shape C7
already provides. `registry-contract` C8 is satisfied by construction: no path string moved, only
`project`; `level: focused` is unchanged everywhere, so the guard's derived-`level` rule still holds.
15 boundaries went to `core-residual`, `keepverse-roots` → `core-workspace`,
`core-advanced-effect-clock` → `core-effectclock`, `core-vocabulary-single-declaration` →
`core-vocabulary`, `creature-kill-loot` → `core-items`, `creature-yield-tuning` →
`core-expeditions`, `tools-prove-predictor` → `core-balance`.

`core-lawn-attrition` and `lawn-attrition-tuning` (production-only paths) share the
`core.lawn-attrition-ladder` trait with `core-lawn-attrition-test`, so all three now name the residual
— the trait, not the boundary's name, decides the owner.
