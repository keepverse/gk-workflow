# Manager acceptance review — build-preset BP1.11/BP1.12 and verification mapping

Review the completed dirty output of `resume-11-build-preset-bp1112-20260925` at a clean exact SHA.
Accept the Data store and Server routes only after repairing their focused verification-boundary
mappings; do not broaden into `RpgStore.cs`, Contracts, tuning, or SE4.37 consolidation.

## Allowed paths

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`
- `gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs`
- `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`
- `gk-core/src/FusionRpg.Server/Program.cs`
- `gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs`
- `gk-core/scripts/verification-boundaries.v1.json`
- `tasks/reports/resume-11-build-preset-bp1112-20260925.md`
- `tasks/reports/resume-17-build-preset-acceptance-20260925.md`

No Contracts, Core BuildPreset types, generated data, tuning, CI, or unrelated Server/Data paths.

## Acceptance boundary

1. Verify BP1.11's additive schema, strict `(save_id, empire_id)` ownership, human-empire refusal,
   transactional CRUD, shipped shape/soft-max refusals, validate-on-read missing/present projection,
   non-cascading delete, and reopen persistence.
2. Verify BP1.12's four routes use the wire playerId as save id, resolve the human owner, map
   structural refusal codes correctly, and write nothing on refusal.
3. Repair the focused verification registry for the new Data source/test and Server endpoint/test;
   add the matching Server test VerificationId trait. Keep shared `Program.cs` on the server fallback
   because it is not feature-exclusive.
4. Run focused Data/Server tests, DAL/test-substrate/unique-allocation guards, path-owned PlanOnly,
   boundary check, and the same checks from a clean detached checkout.
5. Write a schema-v2 artifact with exact reviewed/merged SHAs and preserve the first-use schema ensure,
   SE4.37, and full-aggregate boundaries as open follow-ups.
