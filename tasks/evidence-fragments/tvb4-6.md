# TVB4.6 — Map `gk-data/packs/fusion/data/generated/**` with `generated-seed`; switch on

| Path | Owner | Seam | Guard |
|---|---|---|---|
| `gk-data/packs/fusion/data/generated/creatures/**` | `gen-creature-species-data` -> `gen-creature-species` (module) | — | `generated-seed` |
| `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json` (exact) | `gen-build-plan-data` -> `gen-build-plan` (module) | — | `generated-seed` |
| `gk-data/packs/fusion/data/generated/creatures/_fusion-recipes.json` (exact) | `gen-fusion-recipe-data` -> `gen-fusion-recipe` (module) | — | `generated-seed` |
| `gk-data/packs/fusion/data/generated/passive-tree/**` | `generated-trees` -> `treebinder` (kept, unchanged project/level) | `gen-passive-tree-data-seam` -> `gen-passive-tree` | `generated-seed` (added) |

`_fusion-recipes.json` is a real finding beyond the spec's own S2 table (which names only
`_species-build-plan.json`): `CreatureSpeciesGen --check` never touches it (a separate generator,
`seedsmith.adapters.creatures.fusion.reconcile`, owns it — TVB3.8's `gen-fusion-recipe` finding), so
leaving it under the broad `creatures/**` wildcard would have been an owner that does not read the
file (the boundary's own "Never"). Given its own exact override instead.

`generated-seed` (`gk-core/scripts/guard-generated-seed.py`) was already seeded in the enforcement catalog
(SE0.1) — no new guard registration needed, only attaching it to these four boundaries.

`gk-data/packs/fusion/data/generated/**` added to `$Script:EnforcedRoots` (third of the four roots switched on).

Real proof: full `guard-verification-boundaries.py` run (no `--skip-coverage-walk`) passes clean with
`gk-data/packs/fusion/data/generated/**` now enforced — every one of the 904 creature files, both exact overrides, and
every passive-tree file resolves.

## S-T8

`S8_the_real_registry_plans_a_generated_creature_file_with_its_script_check_and_generated_seed_guard`:
plans `gk-data/packs/fusion/data/generated/creatures/Apple.json` -> resolves to `gen-creature-species-data` (module), plans
both the `gen-creature-species` script check AND the `generated-seed` guard check. Passes.

No other test in the class references `gk-data/packs/fusion/data/generated/**`, so no collision risk from the new mappings.
