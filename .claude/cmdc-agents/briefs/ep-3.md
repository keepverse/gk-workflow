# Lane brief — `ep-3` · empire-progression, wave 3 (EP3 tail + EP4)

**Program**: `empire-progression` (anchor `tasks/empire-progression-anchor.md`; todo
`tasks/empire-progression-todo.md`; ledger `tasks/empire-progression-ledger.jsonl`; map
`docs/architecture/empire-progression-map.md`).
**Session id**: `empire-progression-3`. **Branch**: `cmdc/ep-3`, cut from `features/mega-merge`.

## Why this lane exists

`ep2-1` finished and was retired on scope completion — it covered **EP2.1–EP2.6 only** ("Lane complete: 7
commits EP2.1..EP2.6 + one doc re-anchor commit", merged `50a8e5e3`). The program still holds open work and
**no lane has it**. Unlike most programs here, its remaining rows are **not owner-gated**: the owner raised
the fleet ceiling to 8 on 2026-09-21 and this lane is one of the two additions.

## Your slice, in the todo's own order

The currently open named rows (read each row's own Acceptance/Verify lines before you start — the todo is
the contract, this list is only orientation):

- **`EP3.11`** — Siege: a commander fights as its own specimen with no `CreatureType` points;
  `commander.away` skip; goldens.
- **`EP3.12`** — Casualty: a fallen commander member is detached and set `Recovering` (until
  `injury-tiers`).
- **`EP4.1`** — Core: `RpgActorKinds.Empire`, `EmpireSpeciesLevelUp` reason, the `ParamsFor` arm,
  `EmpireLevelGrants`.
- **`EP4.2`** — Publish `progression` (next free version): `xpCurve.empire` and `awards.speciesLevelUp`;
  move pins (**H7**); land the readers.
- **`EP4.3`** — Credit an empire level-up inside `TryApplyXpUnlocked` for each new `highest_level` of its
  own species.
- **`EP4.4`** — Publish `species-build` (sequence order 5): `freeRespecsPerEmpireLevel`; tuning field;
  `EmpireLevelTuning` wiring (**H7**).
- **`EP4.5`** — `rpg_empire_free_respec_ledger` (keyed for every empire) and the `FreeEmpireRespec` grant,
  applied in the level-change transaction.
- **`EP4.6`** — Empire-level backfill at store start, for every empire with no `kind = 'empire'` row.
- **`EP4.7`** — `GET /api/players/{playerId}/empires/{empireId}/level` and the `EmpireLevelUp` broadcast.
- **`EP4.8`** — FE: every unfiltered progression reader filters by kind.
- **`EP4.9`** — The species respec spend takes `payWith` (souls or a free respec); replay is checked on both
  ledgers; `QuoteSpeciesRespecUnlocked`.
- **`EP4.10`** — The routes carry the choice: `/species-build/respec`, `/respec-price` and the species
  branch of preset activation.

Work them **worst-first / in the todo's order**, several per segment, **one task = one commit**, each with
its numbers in a fragment. `EP4.5`–`EP4.7` sit on the same level-change transaction: if you take them,
take them in order and say so, because a half-applied level change is worse than none.

## Hard edges (the ones that have bitten this program)

- **H2 — migration before writes.** Any new table (`rpg_empire_free_respec_ledger`) lands as a migration
  **before** the code that writes it; a re-keyed table needs its data moved in the same commit.
- **H7 — a publish switches its readers in one commit.** `progression` and `species-build` are published
  through `gk-core/tools/tuning/publish.py`; the new version's readers move with it, and a self-referencing literal
  is not a reader.
- **H1 — a golden moves in its own commit with one named cause.** EP3.11 names goldens; if one moves, the
  fragment records the cause and that commit does nothing else.
- **No hard progression ceilings**: a cap is removed or made a configurable soft cap; an absolute bound is
  *derived and throws*, never clamps (`docs/architecture/power/ssot-power-scale.md` §11).
- **One power ladder**: any level-derived magnitude goes through `P(Θ)` from the power-scale SSOT; a private
  `f(level)` is the defect that let three incompatible curves ship at once.
- **No magic numbers on the balance surface** — thresholds live in `gk-core/data/tuning/<domain>.v{n}.json`.
- **Numeric types**: an integer magnitude that grows with `Θ` is `long`; widen before multiplying; integer
  overflow throws (`checked`); per-mille math divides by 1000 last.
- **A new `gk-core/data/tuning/**` or `gk-data/packs/fusion/data/generated/**` file needs its `boundaries[]` owner row** in
  `gk-core/scripts/verification-boundaries.v1.json` in the same commit (`EnforcedRoots`; ask the manager if your
  fence excludes `scripts/`).
- **Findings route out**; code stays in. A finding outside your fence becomes a row in the OWNING program's
  todo in the same commit as the fragment.

## Fence (`--allow`)

`gk-core/src/FusionRpg.Core/**`, `gk-forge/tools/CreatureBuildPlanGen/**`, `gk-forge/tools/seedsmith/**`, `gk-core/tools/tuning/**`,
`gk-core/data/tuning/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/creatures/**`, `tests/**`,
`docs/architecture/empire-progression/**`, `docs/architecture/empire-progression-map.md`, `tasks/**`.

Note: `gk-core/tests/FusionRpg.Core.Tests` was split into per-area projects by lane `tvb58` (merged) — put a test in
the project whose subject it covers and check it is wired in `FusionRpg.slnx` + `.github/workflows/ci.yml`.

## Verification

Put the printed numbers in each fragment:

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Aptitude|FullyQualifiedName~SpeciesBuild|FullyQualifiedName~Respec"` and, for the server-side rows, `gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Species|FullyQualifiedName~Aptitude"`.
- `python gk-core/tools/tuning/resource_ownership.py --check` and `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check` when you touch tuning or the build plan.
- `python gk-core/scripts/anchor-ledger.py tasks/empire-progression-ledger.jsonl check` after every ledger line.
- `.\scripts\verify-change.ps1 -Paths <your real changed paths> -Session empire-progression-3` — run it
  yourself; read the **numbers printed**, never the exit code alone (TVB-F3).

## Evidence contract (binding)

One fragment per task at `tasks/evidence-fragments/<task-id>.md` with
`| Criterion | Command | Result | Artifact |`, the exact commands, the numbers printed, the committed
artefact, an explicit **Not proved** list, and every finding routed to its owning row in the same commit.
