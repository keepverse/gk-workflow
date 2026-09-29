# SSH1.4 — `host-gate` d: rulings 1 and 2 as enforced contracts

Task: tasks/strain-splice-host-todo.md SSH1.4 · spec: docs/architecture/strain-splice-host/spec-host-gate.md §4 rows 1-2

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `filling_a_strain_leaves_the_host_fingerprint_and_rarity_unchanged` through the real workbench, reading `ContentFingerprint()` and `item_generation.rarity_ordinal` back through the store | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints"` | exit=0 :: 59 passed | `ItemWorkbenchEndpointsTests.cs` |
| `no_combination_contract_carries_a_base_or_slot_key` — C# `ComboRecipe` reflection | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher"` | exit=0 :: 14 passed | `ComboMatcherTests.cs` |
| ...`KindCatalog` extra-field set | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` | exit=0 :: 87 passed | `CombinationKindTests.cs` (new test) |
| ...Python `combination_schema` (`test_the_schema_offers_no_base_type_or_slot_pin`) | `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | exit=0 :: 55 passed | `test_strain_splice_gen.py` |
| Audits | `audit-overflow.py`/`audit-magic-numbers.py --targets <3 files>` | both clean | — |

## Ruling 1 — proven against a combo that actually fires

`RpgStore.Sockets.cs`'s own doc comment already claimed *"Nothing here writes the host's atom rows...
`ContentFingerprint()` are untouched"* — a documented claim, not an enforced one. The new test seeds a
real Strain recipe, bores a socket and inserts a real gem through the REAL `/api/workbench/socket-add`
and `/api/workbench/socket-insert` HTTP routes (the same fixture shape `SocketInsert_consumes...`
already uses), then reads the host's `InstanceRow.ContentFingerprint()` and
`item_generation.rarity_ordinal` back through the store before and after. It first confirms the Strain
actually FIRED — reading the real post-insert `item_socket` rows into a fill and calling
`CombinationEvaluator.Evaluate` directly — so "unchanged" is proven against a real state change on the
socket side, not a no-op.

## Ruling 2 — three languages, one claim

A combination pins role/frame/size and never a specific base type or slot. Three independently-owned
checks, each against the REAL artefact that would carry the leak:
- **C#** (`ComboMatcherTests.cs`): reflection over `ComboRecipe`'s own public properties finds no
  name containing `basetype`/`slot`.
- **The generator's registry** (`CombinationKindTests.cs`, `FusionRpg.ItemSeedValidator.Tests` — the
  real home for a `KindCatalog` check, since `FusionRpg.Core.Tests` carries no reference to the
  `ItemSeedValidator` tool project and the todo's own Files list did not name this test project):
  `KindCatalog.All["combination"].AllowedFields` carries no such field either.
- **Python** (`test_strain_splice_gen.py`): `combination_schema`'s own field names, via the existing
  `schema_mod.schema_field_names` helper the sibling `test_the_schema_offers_no_tier_no_cost_and_no_min_tier`
  already established the pattern for.

## Verification-boundary gap, named rather than papered over

`gk-core/scripts/verification-boundaries.v1.json` carries no entry, and no `projects` mapping, for ANY path
under `gk-forge/tools/seedsmith/tests/**` — `verify-change.ps1 -PlanOnly` refuses
`gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` outright with `VERIFICATION BOUNDARY MISSING`. This
is a real, pre-existing, structural gap (the registry's own `checks` execution only knows how to run a
`dotnet test <project>`-shaped check; wiring a `pytest`-shaped check kind is a tool change bigger than
this S-sized task's own scope, not a JSON row). Verified this file the only way available — directly,
via `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q`
(55/55, see table above) — and named here per AGENTS.md's own rule ("add/repair its mapping or report
it; never compensate by running the full suite") rather than silently working around it.
`verify-change.ps1` itself was run for the three C#/tool files it CAN resolve.

## Status

All SSH1.4 acceptance criteria met. Ledger marked done; todo checkbox ticked.
