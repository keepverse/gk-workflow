# EP1.17 — The sheet labels a default as a default (`isDefault`, `defaultRuleId`)

Spec: docs/architecture/empire-progression/spec-default-build.md

| Criterion | Command | Result |
|---|---|---|
| `ProjectUniqueState` returns `isDefault` and `defaultRuleId` | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudeEndpointsTests"` | pass (25/25) — 2 new tests: `IsDefault=true`/`DefaultRuleId="even"` for a bare audit actor with no explicit allocation and no species profile; `IsDefault=false`/`DefaultRuleId=null` after one explicit point |
| The aptitude sheet shows "Suggested build (\<rule\>)" from those fields, copy from the catalog, never an FE string union | `cd web\fusion-rpg-web; npm test -- --run AptitudesTab` | pass (7/7) |
| A vitest asserts the label follows the field | same run — 3 new tests: label text follows `RULE_LABELS[ruleId]` when `isDefault`; absent once explicit; absent for the commander scope (out of scope, map D1) | pass |
| Full Aptitude-filtered Server.Tests + broader aptitude vitest unaffected | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`; `npm test -- --run aptitude` | pass (60/60 Server.Tests; 31/31 vitest) |
| `npm run build` (tsc --noEmit + vite) | `cd web\fusion-rpg-web; npm run build` | pass, 0 type errors |

## Notes

- `ProjectUniqueState` now keeps the FULL `EffectiveAllocation` result (`effective`) instead of
  discarding everything but `.Allocation` — `isDefault`/`defaultRuleId` ride the same resolver call
  EP1.14 already wired, no second read.
- `gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.ts` (already the ONE file holding the closed
  `AutoAssignRule` vocabulary since EP1.5) gains `RULE_LABELS: Record<AutoAssignRule, string>` and a
  `ruleLabel()` accessor — the "catalog" the acceptance names. `Record<AutoAssignRule, string>`
  makes a missing label a TypeScript compile error the moment a seventh rule is ever added, rather
  than a silent gap; this is what "never an FE string union" rules out (an inline switch/ternary
  guessing the copy in the component, which a new rule could silently skip).
- `isDefault`/`defaultRuleId` are optional props on `AptitudesConsoleHost` (default `false`/`null`)
  because the feature is explicitly unique-scope only (map D1: "the player's own commander pool" is
  out of scope) — the commander call site in `AptitudesTab` never passes them, and a dedicated test
  confirms the label never renders for `role="commander"`.
- The label renders as a plain conditional element directly in `AptitudesConsoleHost`'s own JSX
  (`data-testid="aptitude-default-label"`), not threaded into the `foldAptitudesSurfaceVm`/gui-lego
  recipe system `activePresetName` uses for a similar chip — kept the change surface to exactly the
  three files the spec's own Files list names (`AptitudeEndpoints.cs`, `types.ts`, `AptitudesTab.tsx`)
  rather than also touching the VM fold and recipe registry for one label.
