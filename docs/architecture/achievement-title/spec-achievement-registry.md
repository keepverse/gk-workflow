# Spec: achievement-registry

Module `achievement-registry` (map: `docs/architecture/achievement-title-map.md`).
Reading gate (this session): DESIGN-GATE §1 rows Product vision, Effects atom,
Data/SQL, Tunables, Caps, Validation; `effect-atom/definitions.md`,
`effect-atom/spec-container-schema.md`, `validation-ssot.md`, `tunables-ssot.md`.
Honestly not yet read: full Stats row (stat-system.md, actor-hub-ssot §8.1,
spec-derived-stat-sheet, spec-magnitude-and-units, combat-power-number-ideal),
Injector timing rows (event-pipeline-v2-ssot, overlay-control-loops,
pvz-middle-layer), UI rows (game-gui-principles, gui-lego, idea-ui-phase),
world-map row, match/creature/standalone/resource/status/element/live-probe
rows — those checklist boxes stay unticked per GATE:239 until read.

## Objective

Own the data contracts every other achievement-title module builds on: JSON
grammars for achievement, title, and bundle definitions; the closed
scope/trigger/persistence/visibility vocabularies; the versioned tuning +
catalog files; and load-time validation that rejects with cause. Users: game
systems registering definitions (building, combat, collection, world turns)
and all downstream modules. Success: any mechanism can add rows without code;
one bad row rejects with cause and never fails the whole load silently.

## Tech Stack

C# net8 DAL (`FusionRpg.Data`, sole SQL owner), JSON seed + `gk-core/data/tuning`
versioned configs, xUnit + guard tests. No new packages.

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj
Test: dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AchievementRegistry"
Guards: python gk-core/scripts/guard-dal.py
Verify: powershell -File scripts/verify-change.ps1 -Paths <changed> -Session <id>
```

## Project Structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Achievements.cs  → registry tables + validation (NEW)
data/tuning/achievement-titles.v{n}.json            → numbers (NEW)
data/tuning/achievement-titles-catalog.v{n}.json    → identity/English (NEW)
data/seed/achievements/**                           → authored rows (NEW, Seedsmith-compatible)
gk-core/tests/FusionRpg.Data.Tests/**/AchievementRegistry*  → contract tests (NEW)
docs/architecture/achievement-title/spec-achievement-registry.md → this spec
```

## Code Style

```csharp
// Closed vocab as enum + grammar check; rows are data, never consts.
if (!AchievementId.IsValid(row.Id)) // ^achievement\.[a-z0-9-]{1,64}$, no leading/trailing dash
    throw new RegistryLoadException($"achievement id {row.Id}: IdMismatch");
```

Named consts carry a comment stating why not tunable; every balance number
comes from the injected tuning record — Core reads no files.

## Testing Strategy

xUnit in `gk-core/tests/FusionRpg.Data.Tests`. Assert contract + closed enums only:
grammar accept/reject matrix, duplicate-id-across-scopes rejection, dangling
 bundle-ref rejection, unknown kind/scope/trigger rejection with cause,
 faucet-without-named-`sink:{stock, reason}` rejection (economy P1),
 per-row isolation (one bad row ≠ whole-load failure). Never pin row counts or
 generated names (validation-ssot; canary for scale readings only).

## Tunables & Catalogs

Numbers: `data/tuning/achievement-titles.v{n}.json` (this registry owns
grammar/presence: `hallSlots` structural note, `tierNeedCounts[]` (counts per
rung — unit-carrying name),
`hiddenShareCapMilli` guideline, `reearnScope` per definition
`never|world|season`). Feature magnitudes live with their owners
(empire-titles: `equipShareMilli`, `stackRule`, soft caps,
`seasonTurnWindows`; lifecycle: `validTurns`, `titleRitualPrice.{souls,
essence}`; bundles: `poolWeights`, odds tiers; evaluator watermarks point at
these keys). Group/family membership identity lives in the catalog file, not
the numbers file. English: sibling `*-catalog.v{n}.json` (displayName,
reading, icon/hudToken, flavor). Missing key = load rejection naming it.
Unknown kind/scope/trigger throws naming the row (no `ParseKind`-style
silent default — absolute bounds throw); set→meta DAG cycles reject naming
ids. Bundle/container validation reuses the existing validator shape
(indexed, no CHECK); this registry extends rather than forks it.

## Numeric Types

IDs are text with 64-char bound (spec decision: fits index + logs, no
truncation). Counts/turns are `long`; per-mille shares divide last;
`checked` overflow throws (per-mille `int` breaks at Θ=3,213 — hence `long`).

## ActorHub Gate

N/A — registry produces/consumes no actor combat numbers.

## Boundaries

- Always: SQL only in `FusionRpg.Data`; explicit `paths` commits via
  `git commit`; verify-change before commit; guards green.
- Ask first: widening any closed vocab (kind/scope/trigger); new tuning file.
- Never: raw `git commit/push`; new `f(level)` curve; balance numbers as
  `const`; population-count assertions; second ownership table.

## Success Criteria

- [ ] Grammars + vocab + file shapes locked above load and reject correctly.
- [ ] One bad row rejects with cause; rest of load succeeds.
- [ ] No test pins a row count or generated string.

## Open Questions

None — vocab widening stays per-change review by policy.
