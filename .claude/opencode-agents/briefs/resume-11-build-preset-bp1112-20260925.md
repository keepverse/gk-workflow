# Build-preset BP1.11 → BP1.12 — store and routes

Implement the two dependency-ready build-preset rows in order. BP1.9/BP1.10 are already shipped; do not
reopen them or edit tuning/generated data.

## Read first
- `docs/architecture/build-preset/spec-preset-store.md`
- `tasks/build-preset-todo.md` rows BP1.11 and BP1.12
- current Core BuildPreset types/tuning and existing Data/Server route patterns

## Allowed paths
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`
- `gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs`
- `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`
- `gk-core/src/FusionRpg.Server/Program.cs`
- `gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs`
- `tasks/reports/resume-11-build-preset-bp1112-20260925.md`

No Contracts, generated data, tuning, Core BuildPreset types, CI, verification scripts, or unrelated
Server/Data paths. Use the already-landed BP1.10 tuning; stop if a new tuning/DTO/semantic seam is
required.

## Required behavior
1. BP1.11: create the two-table `(save_id, empire_id)` store, CRUD, validate-on-read, human-only
   `EmpireRef` refusal, soft max from tuning, ownership checks, and no cascade into referenced libraries.
   Return every stored piece row with `Present`/`Missing` reasons; use the in-memory test substrate.
2. BP1.12: map the four routes GET/POST/PUT/DELETE through the existing Server composition, with
   structural refusal codes and no write on refusal. The wire `playerId` is the save id; do not invent
   a second identity vocabulary.
3. Commit each row as its own logical commit if the worker commits; otherwise leave a clearly separated
   dirty diff. No push or merge.

## Verification/report
Run restored focused Data/Server tests, `guard-dal`, `guard-test-substrate`, and path-owned
`verify-change -PlanOnly` for every executable path. Record exact commands/results, schema/migration
and identity evidence, changed files, open questions, and next steps in the report. Use only
`opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent, no external reads.
