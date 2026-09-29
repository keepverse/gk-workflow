# SSH5.10 — THE FLIP: `sockets.v2.json` published, `SocketMaxCeiling` 8, both constants v2

## What changed (one commit)

- `gk-core/data/tuning/sockets.v2.json` — PUBLISHED by the tool, never hand-written:
  `python gk-core/tools/tuning/publish.py sockets structuralCeiling=8 socketCeiling.<role>=… rarityGrant.<rung>.socketMin/Max=… --remove-key :maxCombosPerActor --remove-key :maxCombosPerActorNote`
  → `published sockets (v1 -> v2, 32 change(s)); v1 stays on disk for revert`. Ceilings 0–8 (helm 4,
  R11); `rarityGrant` `0/0 · 0/2 · 2/4 · 2/6 · 4/8`; the per-actor cap removed (R12). v1 untouched.
- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs` — `SocketLimits.SocketMaxCeiling` 4 → 8.
- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs` — `Current` → `sockets.v2.json`.
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` — `SOCKETS_PATH` → `sockets.v2.json`
  (its messages now name `SOCKETS_PATH.name`); `basetypegen/tuning.py` imports it unchanged.
- Tests updated to v2: `SocketGeometryTests` (four named SSH5.10 tests + doubled values),
  `SocketAllowanceTests` (v2 windows), `BaseTypeCorpusTests` (pre-restamp subset contract),
  `ItemSocketStoreTests` (`existing_items_keep_their_socket_rows`), Python `test_base_types_gen.py`,
  `test_combogen.py`, `test_strain_splice_gen.py`.

## Evidence

| Criterion | Command | Result |
|---|---|---|
| publish | `python gk-core/tools/tuning/publish.py sockets …` | `v1 -> v2, 32 change(s)`; v1 on disk |
| Core (named filter) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry\|FullyQualifiedName~CombinationEvaluator\|FullyQualifiedName~SocketAllowance\|FullyQualifiedName~StrainSpliceGrid\|FullyQualifiedName~BaseTypeCorpus"` | 105 passed, 0 failed |
| the four named tests | same run | `the_current_socket_revision_carries_no_combination_cap`, `sockets_zero_to_eight_are_capacity_for_every_role_ceiling`, `head_guard_ceiling_is_read_from_tuning_only`, `a_four_socket_helm_has_one_complete_circuit_and_no_remainder` |
| Data | `dotnet test tests.FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore\|FullyQualifiedName~ItemCardStore"` | 35 passed (`existing_items_keep_their_socket_rows`) |
| Server | `dotnet test tests.FusionRpg.Server.Tests --filter "FullyQualifiedName~GemTier\|FullyQualifiedName~ItemWorkbenchEndpoints\|FullyQualifiedName~ItemPreviewEndpoints"` | 78 passed |
| Seedsmith | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_base_types_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | 159 passed |
| validator, socket check | `dotnet run --project gk-forge/tools/ItemSeedValidator` | exit 1, 41 PRE-EXISTING errors, **0 `SocketMax*`/`SocketCeiling*`** — v2 loaded, no row above its ceiling |
| literal guard | `dotnet test tests.FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | 2 passed |
| guards + citations | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`; `scripts/guard-doc-citations.ps1 -Strict` | 21/0; exit 0, 0 HIGH |

## NOT proved / still open

- `the_shipped_corpus_has_no_refusal` (container refusals) stays red: the combination corpus still
  grants families with no atom (SSH4.4's finding; item-seed-gen owns the regen).
- `deps.preflight` (Python) now REFUSES on the real corpus by design in this window: v2 offers roles
  the un-restamped corpus cannot host, so SSH2.7's R11 arm names them. `SocketAllowanceTests`/Python
  tests assert that refusal; SSH5.13's owner-run re-stamp (after SSH5.12) clears it.
- `gk-forge/tools/ItemSeedValidator` overall exit is FAIL on 41 pre-existing non-socket errors
  (`PartitionMetaMismatch`/registry drift); only the socket-ceiling half of it is green.
- SSH5.12 (`resocket --write`) and SSH5.13 (the R11 owner re-run) are owner rows, not run.
- `verify-change` not run: it still aborts on other sessions' session-boundary drift.
