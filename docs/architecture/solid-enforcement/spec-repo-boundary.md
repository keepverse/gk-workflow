# Spec: `repo-boundary`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 2** · depends on:
`guard-runner`.

## Objective

Two structural rules hold today and have no guard:

1. **Standalone-first and layering.** `DESIGN-GATE.md` §2.9: every RPG feature must stay playable
   with the game closed. Structurally, that means the assemblies that make up the standalone game
   (`Contracts`, `Core`, `CheatCore`, `Data`, `Server`) never reference Unity, the injector, or the
   mod loaders, and depend on each other in one direction only. That direction is the D in SOLID made
   physical: `Core` depends on the `Contracts` abstraction, never on `Data`'s SQL.
2. **Frozen planning paths.** `CLAUDE.md` and `AGENTS.md` make it unconditional: `/plan` output goes to
   `tasks/<program>-{plan,todo}.md`. `tasks/plan.md` and `tasks/todo.md` are the perf stream's history,
   *"not a default and not a fallback"*, and `SPEC.md` at the root is *"not a default"*. The incident
   behind the rule (2026-08-23, a plan delivered to the wrong path) was caught by the owner, not by a
   check.

**Measured on 2026-09-18, both rules hold:** 0 Unity/Il2Cpp/MelonLoader/BepInEx/Harmony `using`s and
0 forbidden project references across the five assemblies; `tasks/plan.md` / `todo.md` last touched
`2c406652` (2026-09-05); no `SPEC.md`. **There is no backlog.** This module pins a state that is
already true, so it is the cheapest possible gate and lands green on day one.

## Design

### `gk-core/scripts/guard-repo-boundary.py`

**B1 — the allowed dependency graph** (the guard parses `<ProjectReference Include=…>` elements):

| Project | May reference (projects) |
|---|---|
| `FusionRpg.Contracts` | — |
| `FusionRpg.Core` | `Contracts` |
| `FusionRpg.CheatCore` | `Contracts` |
| `FusionRpg.Data` | `Contracts`, `Core`, `CheatCore` |
| `FusionRpg.Server` | `Contracts`, `Core`, `CheatCore`, `Data` |

The table is **read from the csproj files at build time and pinned as measured**. The cells above are
today's reading, and the build confirms them before committing the pin. The graph is a closed,
reviewed structure, so pinning it is correct. A new edge is an architecture change that belongs in
`decisions.md` first (AGENTS.md hard boundary: *"Architecture changes that lock behavior need
`decisions.md` first"*).

**B2 — no host assemblies.** None of the five may carry a `<Reference>` or `<PackageReference>` whose
include matches `UnityEngine`, `Il2Cpp`, `MelonLoader`, `BepInEx`, `HarmonyLib` or `0Harmony`, and no
`.cs` file under their folders may have a `using` of those namespaces.

**B3 — frozen paths.** In the diff against the base (`-Range` / `-BaseRef`, the same convention as
`guard-generated-seed` and `guard-tuning-immutability`):
- `tasks/plan.md` and `tasks/todo.md` must not be **modified or added to**,
- `SPEC.md` must not be **added** at the repository root.

**Why element-parsing, not substring scanning.** The repo has already been bitten by this exact
thing. A naive substring guard once flagged `FusionRpg.Core.csproj` because an `InternalsVisibleTo`
item names `FusionRpg.Data.Tests` (the memory `core-data-guard-substring-scan` records it). Today
`Core.csproj` carries `Include="FusionRpg.Core.Tests"` and two more non-project `Include`s. B1 reads
**only** `ProjectReference` elements through an XML parser (`[xml]` in PowerShell), so those can never
be mistaken for dependencies.

### Registry

Two invariant rows: `dg-9-standalone-first` → `repo-boundary`, and `claude-plan-paths` →
`repo-boundary`. It lands directly as `ci` / `gating`, since there is no backlog.

## Commands

```powershell
python gk-core/scripts/guard-repo-boundary.py
python gk-core/scripts/guard-repo-boundary.py -Range HEAD~1..HEAD
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~RepoBoundaryGuardTests"
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/guard-repo-boundary.py` | **new** |
| `gk-core/tests/FusionRpg.Guard.Tests/RepoBoundaryGuardTests.cs` | **new** |
| `gk-core/scripts/enforcement-registry.v1.json` | guard row plus two invariant rows |

## Testing strategy

Falsifiers run against a **temporary copy** of a minimal fake `src/` layout (checked cleanup):

- `Core.csproj` gaining `<ProjectReference Include="..\FusionRpg.Data\…">` fails B1.
- `Core.csproj` gaining an `InternalsVisibleTo`-style `Include="FusionRpg.Data.Tests"` **passes**.
  This is the regression the memory records.
- A `using UnityEngine;` in a `Server/*.cs` fails B2.
- In a temporary git repository, modifying `tasks/plan.md` fails B3, and adding
  `tasks/foo-plan.md` passes.

The real tree passes.

## Boundaries

- **Always:** add a dependency edge through `decisions.md`, then the guard's pinned graph.
- **Ask first:** any new project joining the five.
- **Never:** substring-scan csproj files. Never write to `tasks/plan.md`, `tasks/todo.md` or `SPEC.md`.

## Success criteria

- [ ] B1–B3 enforced, and each has a failing falsifier and the InternalsVisibleTo non-regression.
- [ ] The real tree passes, and the guard gates in CI from its first commit.

## Self-audit — the debate

**Objection: "Everything passes. Why spend a module?"** That is exactly why. A rule that holds and is
unguarded is one careless `ProjectReference` from breaking, and the break would not show until the
game-closed path failed in someone's hands. Pinning a green state costs one small script and cannot
produce a backlog.

**Objection: "Pinning the graph blocks legitimate refactors."** It routes them through `decisions.md`,
which the hard boundaries already require for architecture changes. The guard just makes that
requirement mechanical.

**Objection: "B3 is trivial. Fold it elsewhere?"** It has no better home: it is a path-boundary rule,
the same kind as B1/B2's assembly boundary, and a separate script for three lines would be ceremony.
One guard with three numbered rules keeps the failure message precise.

## Gaps found and closed while writing

- **The first draft listed `Server` as allowed to reference nothing Unity-related "except
  `wwwroot`".** Checked: `Server.csproj`'s non-project `Include`s are content globs
  (`gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/dungeon/**`, the generated creature JSON). Those are content, not
  code, and B1's element-level parse ignores them correctly.
- **Should B3 cover "the file must never change at all"?** No. The files keep their history, and a
  deletion by the owner would be a legitimate cleanup. B3 blocks writes and additions only, which is
  what the rule says.
