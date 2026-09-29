# Spec: `srp-file-budget`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 4 (last)** · depends on:
`guard-runner`. Runs after every other module, because it moves the most code.

## Objective

Single responsibility is the S in SOLID, and the repo has no mechanical check on it at all. Line
count is **not** single responsibility. It is the cheapest reliable *symptom* of its absence, and the
measurement is unambiguous (2026-09-18):

| File | Lines | What it appears to mix (inferred from its name and role; **confirm from the file's regions at build** before choosing seams) |
|---|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` | **4,163** | the store's root: schema bootstrap plus many tables' CRUD, next to **84** `RpgStore.*.cs` partials (measured) that already split the rest |
| `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs` | 2,208 | every `debug.*` / cheat command handler in one dispatch |
| `gk-fusion/src/FusionRpg.Injector/DebugActions.cs` | 2,172 | debug board manipulation across lawn, UI and spawning |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs` | 2,067 | unique-actor lifecycle, loadout, death, cache |
| `gk-fusion/src/FusionRpg.Injector/GameHooks.cs` | 1,816 | many unrelated Harmony hook families plus dumps |
| `gk-core/src/FusionRpg.Server/Program.cs` | 1,786 | the entire composition root: tuning loads, DI, endpoints, boot tasks |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs` | 1,702 | delve persistence |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs` | 1,633 | every debug route |
| `web/…/features/lawn/LawnPage.tsx` | **1,406** | the lawn page: layout, state and panels |
| `web/…/layers/relics/RelicsLayer.tsx` | 679 | |
| `web/…/features/rpg-progression/RpgProgressionPage.tsx` | 661 | |
| `web/…/features/cheats/CheatsPage.tsx` | 644 | |
| `web/…/stages/world/WorldStage.tsx` | 612 | |

The FE rows are in scope by the "one program" ruling (map D6), superseding `fe-debt-register`'s
hand-off **for file-size SRP only**.

## Design

### The guard: `scripts/guard-file-budget.ps1`

| Rule | Check |
|---|---|
| **F1** | Every tracked `src/**/*.cs` is ≤ **1,500** lines |
| **F2** | Every tracked non-test `gk-web/web/fusion-rpg-web/src/**/*.tsx` is ≤ **600** lines |
| **F3** | A file may opt out **only** with a first-line marker `// srp-budget-exempt: <reason>`, where the reason is non-empty and the file is on the registry's small exempt list (expected empty; see the debate) |

The budgets are **structural limits, not balance numbers.** Per `CLAUDE.md`'s caps section,
structural limits are exempt from the no-hard-ceilings rule *and must say so in a comment*, so the
script's header records why these two numbers. **1,500**: a judgement, not a proof. The eight C# files above it are each the root of a family
(a store, a command runner, a hook host, a composition root), and a file of that size is not one
responsibility. Below it, no single cut-off separates one responsibility from several, which is why
the guard treats line count as the symptom and never as the rule. **600**: the FE
component pattern the repo already uses leaves a page shell well under it. Measured 2026-09-18, the
94 non-test `src/ui/**/*.tsx` components have a median of **69** lines, a p90 of **258** and a maximum
of **573**. Test files are excluded from F2, because a test file's size follows its
subject.

### Splitting, per kind, with no behaviour change

Each split is **move-only**: no logic edits, same public surface, same namespaces. That is what makes
it verifiable.

| Kind | Technique | Verification |
|---|---|---|
| `RpgStore*.cs` (Data) | move regions into new `RpgStore.<Area>.cs` partials. The class is already partial, and 84 partials set the pattern | `dotnet test tests\FusionRpg.Data.Tests` plus `guard-dal` |
| `Program.cs` (Server) | extract cohesive blocks into `static partial class Program` files, or `IServiceCollection` / `WebApplication` extension methods (`Program.Tuning.cs`, `Program.Endpoints.cs`, `Program.Boot.cs`), called in the **same order** | `Server.Tests` plus `E2E.Tests`, then a boot smoke (`Start-Process` the server, `GET /health`) |
| `DebugEndpoints.cs` | split by route family into `DebugEndpoints.<Family>.cs` partials | `Server.Tests`, and `guard-debug-scope` (it scans these routes) |
| Injector (`CheatCommandRunner`, `DebugActions`, `GameHooks`) | partial classes by command, action or hook family | **not CI-buildable** (no game binaries). `guard-injector-compile` (tier `local`), plus one `deploy-play.py --no-server` boot and `live-lawn-quick-start` to confirm hooks still install |
| TSX pages | extract presentational sub-components into the feature folder (the `src/ui/**` pattern); state stays in the page | `npm run build` (tsc), `npm test`, `npm run test:e2e` for the touched page |

**Order inside the module:** Data first (the best test coverage), then Server, then FE, then
Injector (the weakest automated verification, so it goes last and is done alone).

### Registry

`file-budget`: `ci` / `backlog` → `srp-file-budget` while any file is over budget, then `ci` /
`gating`. Invariant row `dg-15-solid-single-responsibility` → `file-budget`, with its `source` noting
that line count is the proxy, not the rule.

## Commands

```powershell
.\scripts\guard-file-budget.ps1
.\scripts\run-guards.ps1 -Only file-budget
dotnet test tests\FusionRpg.Data.Tests
python gk-fusion/scripts/guard-injector-compile.py
cd gk-web/web/fusion-rpg-web; npm run build; npm test
```

## Project structure

| Path | Change |
|---|---|
| `scripts/guard-file-budget.ps1` | **new** |
| 13 over-budget files | split into partials or components, move-only |
| `gk-core/scripts/enforcement-registry.v1.json` | rows |
| `docs/architecture/solid-remediation/spec-fe-debt-register.md` | one line: file-size SRP moved to `solid-enforcement` |

## Testing strategy

- **Move-only proof per split.** For C#, `git diff --stat` shows the lines moved, and a
  normalised-whitespace comparison of the **union** of old and new files' members shows zero
  added or removed members. For TSX, the rendered output of each page's existing tests is unchanged.
- The **boot smoke** for `Program.cs` is mandatory, because DI registration *order* can matter, and
  no unit test covers the composition root end to end.
- **Guard falsifiers:** a temporary 1,501-line file fails F1. The same file with an exempt marker but
  not on the list fails F3.

## Boundaries

- **Always:** move-only. Split along the file's existing region or family seams.
- **Ask first:** any logic change discovered while splitting. Log it for its own change, never fold
  it in.
- **Never:** split a file another active session is editing (check `tasks/sessions/*.json` first).
  Never raise a budget to fit a file.

## Success criteria

- [ ] No production file over budget. `guard-file-budget` gating.
- [ ] Every split verified at its kind's bar; the Injector split also verified by a live boot.
- [ ] SR-23 struck through with the SHA.

## Self-audit — the debate

**Objection: "Line count isn't SRP. A 1,400-line file can do three jobs and a 1,600-line file one."**
Agreed, and the invariant row says so. The guard does not claim to detect SRP. It catches the one
symptom that is both cheap and never a false negative at the extremes: nothing at 4,163 lines is one
responsibility. The alternative, a cohesion metric such as LCOM, needs a Roslyn analysis pipeline the
repo does not have, for a marginal gain over the obvious cases.

**Objection: "Splitting into partials just moves the mess."** Partials split by responsibility
*are* the fix for a class that is legitimately one aggregate (`RpgStore` is the store facade by
design; `guard-dal` requires SQL to stay inside the `FusionRpg.Data` project, and one partial class is
how that project has kept it together). For classes that are not one aggregate
(`DebugActions`), the partial split exposes the seams, and turning a family into its own class is a
follow-on the split makes visible and cheap. It is deliberately not bundled here, to keep the change
move-only.

**Objection: "Why an exempt marker if the list is expected to stay empty?"** Because generated C# may
arrive one day (for example from a future `ElementEnumGen` output), and a guard with no legal
exemption would push someone into deleting the guard. The marker plus a registry list makes the
exemption reviewed, visible, and rare.

## Gaps found and closed while writing

- **The Injector can't be verified by CI,** so the first draft's "tests pass" was not a real bar for
  three of the thirteen files. It was replaced by the injector-compile guard plus a live boot, and
  those files moved to the end of the module.
- **Composition-root order** was a hidden behaviour dependency of splitting `Program.cs`. A boot smoke
  was added as mandatory.
- **Collision with other modules:** `commander-identity` edits several of these files (for example
  `RpgStore.UniqueActors.cs` and `CommanderEndpoints.cs`). The map puts this module last, and the
  "never split a file another session edits" boundary covers work outside the program.
