# SSH5.1 — host-set and max-`socketMax` pins rewritten as three role-free contracts

## What changed

- `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs` — the two role-pinned tests replaced by
  `The_host_set_is_every_role_whose_ceiling_reaches_the_ingredient_count` (the tuning host set equals
  `{ role | ceiling >= ingredientCount }`, derived from `SocketTuning.SocketCeiling`, agreeing with
  `SocketGeometry.RolesThatCanHostAStrain`) and
  `The_corpus_host_set_is_a_subset_of_the_tuning_host_set_and_no_row_exceeds_its_ceiling` (the corpus
  subset contract + no base row above its role ceiling). No role is named.
- `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — the same two contracts on the Python side; the
  literal `("armament-primary", "core-guard")` is gone.
- `docs/architecture/strain-splice-host/spec-circuit-topology.md` §5 — the pin table marked landed
  (its cited lines are the pre-rewrite pins). `tasks/evidence-fragments/SSH4.1.md`'s C#-mirror citation
  re-anchored (`:228` → `:236`) for the rewrite's line shift.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| three role-free contracts, no role named | `dotnet test tests.FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid"` | 22 passed, 0 failed |
| same contracts, Python side | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | 66 passed |
| `the_host_set_is_every_role_whose_ceiling_reaches_the_ingredient_count` (C#) agrees with Python | both runs | green under v1 |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |
