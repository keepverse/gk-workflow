# Resume 11 — build-preset BP1.11 / BP1.12

**Status:** implementation complete within the session fence; intentionally left as an uncommitted dirty diff for review. No commit, push, or merge was performed.

**Snapshot:** branch `opencode/resume-11-build-preset-bp1112-20260925` at `a49453348667817c87b2b6fcc2e68242d93ef694`.

## Delivered

### BP1.11 — store and validation

- Added `rpg_build_preset` and `rpg_build_preset_piece` in `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`; all production SQL for the feature remains in `FusionRpg.Data`.
- The header is born with `save_id` and `empire_id`. Public store methods take `EmpireRef`, query by the strict pair, and derive no empire identity from request data.
- Create/update/delete are transactional. Create alone reads `BuildPresetTuningHub.Tuning.SoftMaxBuildPresets`; update replaces the piece set and increments revision; delete removes only the header and its own pieces.
- Save-time validation delegates to the shipped `BuildPresetShape`; the Data test covers every named shape refusal and proves no header or piece row was written.
- Validate-on-read returns every stored piece. The five shipped kinds resolve their specimen/aptitude/loadout/action-or-aura references; an unknown persisted kind remains present in the result with `kind = "unknown"`, `state = "missing"`, and `build-preset.piece.missing:unknown`.
- A non-human `EmpireRef` throws `EmpireScopeNotWidened` before a library write. This is the todo-authorized local form until save-identity SE4.37 supplies the shared `RequireHumanEmpire` helper.
- The focused Data tests prove all five kinds can read `Present`, deleted/retired references read `Missing` without shortening the list, deleting a preset does not cascade into aptitude/item libraries, soft max refuses, another save cannot update/delete, and a store reopen reads the new schema and rows.

### BP1.12 — HTTP routes

- Added `GET /api/build-presets/{playerId}`, `POST /api/build-presets`, `PUT /api/build-presets/{presetId}`, and `DELETE /api/build-presets/{presetId}?playerId=` in `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`.
- The wire `playerId` is the save id on every operation. Each route resolves the human owner through `EmpireScopeRequests.HumanOwnerOf`; no second empire identity was added to the wire.
- GET returns validated pieces. POST creates, PUT atomically replaces and bumps revision, and DELETE removes only this library's rows.
- Shape and transport refusals preserve their structural codes. Soft max/id collision/owner mismatch are 409; missing/not-found is 404; shape and malformed-kind refusals are 400. A refused POST/PUT writes nothing, proven against the real store.
- `gk-core/src/FusionRpg.Server/Program.cs` now calls `app.MapBuildPresets()` beside the aptitude-preset routes. The already-shipped BP1.10 tuning load was not changed.

## Schema and migration evidence

The exact feature schema is additive and contains no re-key migration:

```sql
CREATE TABLE IF NOT EXISTS rpg_build_preset (
  preset_id TEXT NOT NULL PRIMARY KEY,
  save_id INTEGER NOT NULL,
  empire_id TEXT NOT NULL,
  name TEXT NOT NULL,
  created_utc TEXT NOT NULL,
  revision INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_rpg_build_preset_empire
  ON rpg_build_preset(save_id, empire_id);

CREATE TABLE IF NOT EXISTS rpg_build_preset_piece (
  preset_id TEXT NOT NULL,
  piece_kind TEXT NOT NULL,
  target_ref TEXT NOT NULL DEFAULT '',
  ordinal INTEGER NOT NULL DEFAULT 0,
  ref_id TEXT NOT NULL,
  PRIMARY KEY (preset_id, piece_kind, target_ref, ordinal)
);
```

`RpgStore.cs` is outside this session's allowed-path fence, so the diff does not add a call to its boot-time `EnsureHotSchema`. Instead, every public build-preset store operation calls the idempotent `EnsureBuildPresetSchemaUnlocked` on its already-open connection before access. `The_new_schema_and_rows_survive_a_store_reopen` proves the additive schema and committed rows are visible through a second `RpgStore` over the same in-memory database. If boot-time table creation is required as a separate invariant, that needs an explicitly authorized `RpgStore.cs` follow-up rather than a silent fence crossing.

## Identity evidence

- Persistence columns and filters are strictly `(save_id, empire_id)`; the piece table reaches its owner through the globally unique preset header.
- `RequireHumanBuildPresetOwnerUnlocked` compares the supplied empire to `HumanEmpireOfOrNull` on the same connection and throws before insert/update/delete when it is absent, non-human, or unseeded.
- Specimen ownership uses the shipped strict `OwnsSpecimenUnlocked(save, empire, instance)` predicate rather than a save-only check.
- Server routes accept only the save-scoped `playerId` and use `EmpireScopeRequests.HumanOwnerOf`; the response does not expose an independently supplied empire id.
- The Server tests create a real second save, create/read its preset through HTTP, and prove the first save cannot list it. A second save also receives `build-preset.owner.mismatch` on PUT and 404 on DELETE while the original row and pieces remain unchanged.

## Changed files

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs` — new Data schema, CRUD, human-only guard, validation-on-read.
- `gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs` — focused in-memory store coverage.
- `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs` — new four-route HTTP surface.
- `gk-core/src/FusionRpg.Server/Program.cs` — one production route-composition call.
- `gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs` — real in-process HTTP coverage.
- `tasks/reports/resume-11-build-preset-bp1112-20260925.md` — this report.

No Contracts, Core build-preset types, tuning/generated data, CI, verification scripts, task ledgers, or unrelated paths were edited.

## Verification

Commands were run from the worktree root.

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~BuildPreset"
```

Result: **passed, 10/10**. Existing unrelated analyzer/nullability warnings remained; no build-preset test failed.

```powershell
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetEndpoints"
```

Result: **passed, 14/14**. Existing unrelated analyzer/nullability warnings remained; no build-preset endpoint test failed.

```powershell
.\scripts\guard-dal.ps1
```

Result:

```text
DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data
```

```powershell
python gk-core/scripts/guard-test-substrate.py
```

Result:

```text
TEST SUBSTRATE GUARD OK — no new swallowed deletes, temp-backed or untagged file-backed stores, or shipped-corpus copies / corpus writes into temp, in tests/
```

The all-path plan also selected the existing unique-allocation reader seam, so its focused verifier was run:

```powershell
dotnet test tests\FusionRpg.Guard.Tests --filter "VerificationId=guard.unique-allocation-reader"
```

Result: **passed, 2/2**.

```powershell
$changed = @(
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs',
  'gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs',
  'gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs',
  'gk-core/src/FusionRpg.Server/Program.cs',
  'gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs'
)
.\scripts\verify-change.ps1 -Paths $changed -Session resume-11-build-preset-bp1112-20260925 -PlanOnly
```

Result: the plan covered every executable path, `guard-dal`, `guard-test-substrate`, focused Data/Server tests, and `guard.unique-allocation-reader`. The registry still resolves the new production/test paths to broad Data/Server fallback owners rather than focused `data.build-preset` / `server.build-preset` owners:

```text
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs -> data-fallback (module)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs -> unique-allocation-reader-seam (seam)
gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs -> server-fallback (module)
gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs -> unique-allocation-reader-seam (seam)
gk-core/src/FusionRpg.Server/Program.cs -> server-fallback (module)
gk-core/src/FusionRpg.Server/Program.cs -> unique-allocation-reader-seam (seam)
gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs -> data-tests-fallback (module)
gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs -> server-tests-fallback (module)
guard: dal
guard: test-substrate
test: data  (sharded runner)
test: guard guard.unique-allocation-reader
test: server
full evidence: CI/nightly/release
```

```powershell
python scripts/session-boundary-check.py --session resume-11-build-preset-bp1112-20260925
```

Result: **clean for `resume-11-build-preset-bp1112-20260925`**.

```powershell
git diff --check
```

Result: **clean** (no whitespace errors).

## Open questions and named follow-ups

1. **Boot-time schema hook:** the fence excludes `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`. Current first-use additive ensure is tested and functional, but a reviewer may require a separate authorized one-line `EnsureBuildPresetSchemaUnlocked(db)` call in `EnsureHotSchema`.
2. **SE4.37 consolidation:** when the shared `RequireHumanEmpire` / `EmpireScopeNotWidened` lands, replace the local build-preset guard instead of keeping two policies.
3. **Verification registry:** new Data/Server paths still fall back to broad owners. Repairing `gk-core/scripts/verification-boundaries.v1.json` is outside this fence and remains a separate verification-boundary task.
4. **No full-suite claim:** the unfiltered suite was intentionally not run for this narrow slice; the report claims only the focused checks above. Full evidence remains CI/nightly/release-owned.

## Next steps

1. Review this dirty diff as two logical slices: BP1.11 (Data file + Data tests), then BP1.12 (Server endpoint + Program + Server tests).
2. Decide whether boot-time schema registration is mandatory; if yes, authorize the single `RpgStore.cs` follow-up and rerun the Data boundary.
3. Replace the local human-empire guard when SE4.37 lands.
4. Repair the focused verification mappings in their owning verification-boundary lane.
5. Commit/push/merge only under a separate explicit instruction; this session intentionally leaves all six paths uncommitted.

<<<REPORT {"status":"done","summary":"Implemented BP1.11 and BP1.12 in the allowed paths and left the complete dirty diff uncommitted. The Data store now has additive (save_id, empire_id) build-preset and piece tables, human-only EmpireRef ownership, atomic CRUD, shipped shape refusals, tuning soft max, strict ownership, no cross-library cascade, and validate-on-read that preserves present/missing/future-kind rows. Four Server routes derive the human owner from the wire save-scoped playerId, return validated pieces, preserve structural refusal codes, and write nothing on refusal; Program maps the new surface. Focused Data tests pass 10/10, Server tests pass 14/14, DAL and test-substrate guards pass, and the selected unique-allocation reader guard passes 2/2. The verification registry still uses broad Data/Server fallback mappings. RpgStore.cs was outside the fence, so schema registration is idempotent first-use ensure rather than an EnsureHotSchema call; reopen coverage proves persistence. SE4.37 should later replace the local human-empire exception.","changed_files":["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs","gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs","gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs","gk-core/src/FusionRpg.Server/Program.cs","gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs","tasks/reports/resume-11-build-preset-bp1112-20260925.md"],"verification":["dotnet test tests\\FusionRpg.Data.Tests --filter \"FullyQualifiedName~BuildPreset\" — passed 10/10","dotnet test tests\\FusionRpg.Server.Tests --filter \"FullyQualifiedName~BuildPresetEndpoints\" — passed 14/14",".\\scripts\\guard-dal.ps1 — DAL GUARD OK",".\\scripts\\guard-test-substrate.py — TEST SUBSTRATE GUARD OK","dotnet test tests\\FusionRpg.Guard.Tests --filter \"VerificationId=guard.unique-allocation-reader\" — passed 2/2","verify-change.ps1 -PlanOnly for all five executable paths — covered DAL, test-substrate, Data, Server, and guard.unique-allocation-reader; new paths resolve to broad fallback owners",".\\scripts\\session-boundary-check.py --session resume-11-build-preset-bp1112-20260925 — clean","git diff --check — clean"],"open_issues":["RpgStore.cs is outside the allowed paths, so the new schema is ensured on first public build-preset access rather than from EnsureHotSchema; a boot-registration follow-up needs explicit path authorization if mandatory","SE4.37 has not supplied the shared RequireHumanEmpire/EmpireScopeNotWidened helper; the local build-preset refusal must be folded into it later","gk-core/scripts/verification-boundaries.v1.json still maps the new Data/Server paths to broad fallback owners rather than focused build-preset owners","no unfiltered full-suite or merged-head claim is made"],"next_steps":["review BP1.11 and BP1.12 as separate logical slices","decide whether to authorize the one-line RpgStore.cs boot schema hook","replace the local human-empire guard when SE4.37 lands","repair verification mappings in their owning lane","leave commit, push, and merge for a separate explicit instruction"]} REPORT>>>
