# Lane `csf3-1` — content-stack CS-F3: the player pack ships a roster and self-heals its boot

**Session:** `content-stack-csf3` · **Program:** `content-stack` · **Mode:** worktree
**Todo:** `tasks/content-stack-todo.md` — rows **CS-F2** (its delete-half is landed and guarded) and **CS-F3**
**Spec:** `docs/architecture/effect-atom/spec-player-content-boot.md` (§3.1 the three shipping shapes, §3.2/§4 the boot's loud-and-non-fatal self-heal)
**Fence:** `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Launcher/**`, `tests/**`, `scripts/**`, `tools/**`, `gk-data/packs/fusion/data/generated/**`, `docs/architecture/effect-atom/**`, `tasks/content-stack-*`
**Protected, granted to this lane:** `scripts/publish-player.ps1`, `scripts/smoke-player-pack.ps1`

## Why this lane exists

Lane `findings-2` measured this against a real `dotnet publish`, and the numbers are the row:

- a publish of `gk-core/src/FusionRpg.Server` puts **1386** `gk-data/packs/fusion/data/seed/**.json` and **182** `gk-core/data/tuning/*.json` beside
  the exe — the CS-F2 half that used to delete them is fixed and guarded;
- the pack still **cannot boot**: since the `catalog-runtime` flip the roster is store-backed
  (`gk-core/src/FusionRpg.Server/Program.cs:612` — `CreatureSpeciesCatalog.Configure(store.BuildCreatureSpeciesSnapshot())`)
  and that call **throws** on an empty roster (`gk-core/src/FusionRpg.Core/Creatures/SpeciesSnapshot.cs:40-49`). The only
  writer of that table is `gk-forge/tools/CreatureSpeciesImport`, a dev CLI;
- measured on the publish output: the server dies with
  `Unhandled exception. System.InvalidOperationException: CreatureSpeciesCatalog.Configure received an empty species roster`.
  The *same* pack boots and reports `contentSource: imported` once that import has been run against the data
  directory by hand.

So `scripts/smoke-player-pack.ps1`'s `server_boot` step fails for this reason independently of CS-F2.

## The owner's ruling (2026-09-23) — implement exactly this

**Ship the species tree and self-heal the boot.** `gk-data/packs/fusion/data/generated/creatures/**` ships inside the pack and the
**boot self-heals the roster once**, mirroring `SeedImportRunner.RunSelfHealing`. **No launcher change** — the
fix stays inside this program.

**Acceptance (unchanged):** a published player folder boots on a fresh data directory with a non-empty roster,
and `pwsh -File scripts/smoke-player-pack.ps1` reads `contentSource: imported`. The pack gets larger and the
first boot does the import — **say both** in the doc sentence that lands with it.

## Work

1. The `<Content>` rule that carries `gk-data/packs/fusion/data/generated/creatures/**` into the publish. The sibling work already
   added eight such rules for `gk-data/packs/fusion/data/seed/**`; follow that shape, and keep
   `tests/FusionRpg.Server.Tests/BootContentCopyRuleTests.Every_seed_folder_the_boot_import_sweeps_is_covered_by_a_copy_rule`
   green (extend it if the new tree is swept by the same importer).
2. The boot self-heal: on an empty roster, import the shipped species tree once. Mirror
   `SeedImportRunner.RunSelfHealing`'s shape — loud, non-fatal where the spec says so, never a silent fallback
   to code. A second boot must be a no-op (the roster is no longer empty).
3. Prove it and put the printed line in the evidence: `pwsh -File scripts/publish-player.ps1`, then
   `pwsh -File scripts/smoke-player-pack.ps1` on a **fresh** data directory → `SMOKE PASSED` with
   `contentSource: imported`. Tick CS-F3 and assert the id is still present after the tick.

## Rules

- One logical change per commit: code + its test + the evidence fragment **in the same commit**.
- Never hand-edit generated JSON. `gk-data/packs/fusion/data/generated/**` and `gk-data/packs/fusion/data/seed/**` are enforced roots: a new file under
  one needs its boundary row in `gk-core/scripts/verification-boundaries.v1.json` in the same commit (TVB-F24).
- A row you end still open must name **exactly** what blocks it — never "needs investigation".
- Foreground commands only; never end a turn waiting on your own background job.
- **Every segment ends with the report block.** The provider sometimes returns `429 GoUsageLimitError`: end the
  segment with your report rather than retrying in a loop.

## Verification

- `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <files you changed> -Session content-stack-csf3`
- `python gk-core/scripts/guard-verification-boundaries.py`
- `dotnet test gk-core/tests/FusionRpg.Server.Tests` (the boot's own project) — the focused project, not the whole suite
- the publish + smoke pair above, on a fresh data dir

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

## Evidence contract

The **printed reading**, never an exit code: the smoke script's own `SMOKE PASSED` line with `contentSource`,
the boot's log line, a row count for the imported roster. Write the fragment under `tasks/evidence-fragments/`.

## Boundaries

Do not widen the fence. Do not touch another session's files. Never commit conflict markers. SQL lives only in
`FusionRpg.Data`. Merge `features/mega-merge` freely — the integration head moves several times an hour.
