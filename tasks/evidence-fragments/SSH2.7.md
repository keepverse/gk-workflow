# SSH2.7 — `Coverage/HostRoleDiversity` (a reading) and the R11-step preflight

## What changed

- `metrics/coverage.py` — `HostRoleDiversityMetric` (report-only: `gates = False`, every finding
  `Severity.NOTE`), registered in `report/cli.py`'s `build_registry`. One row per `(shape, offered
  role)`, one for "no role", one for a pin the current ceilings no longer offer. It asserts no share.
- `combogen/deps.py` — `base_type_reach` / `roles_without_a_base`: the base-type closure
  `TARGET_HOST_ROLE`'s docstring promised but its resolver stubbed (`1 if value in host_roles`).
  `preflight` now names an offered role no shipped base type can host; `refused` includes it.
- `report/cli.py` — under `--retry-blocked`, refuse by role name before `plan_run` / any model call.
- Citations displaced by the cli.py move re-anchored in this commit (`+5` / `+20`) across
  `docs/architecture/**`, plus the SSH specs/map/todo to their real symbols.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| share per offered role + no role; reading not a gate | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_metrics_coverage_cli.py -q` | 5 passed (`host_role_diversity_is_a_reading_not_a_gate`) |
| R11 preflight refuses by name before any model call | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q -k "r11 or host_role_enum or host_role_diversity"` | 3 passed |
| enum derived from loaded ceilings | same run | 3 passed (`the_host_role_enum_is_derived_from_the_loaded_ceilings`) |
| metric prints, never fails the gate | `python -m seedsmith check ../../data/seed/items --adapter items --gate --metric Coverage/HostRoleDiversity` | exit 0, 5 note |
| `--deps` still clean under v1 | `python -m seedsmith items validate --deps` | exit 0, `refused: false` |
| Python modules | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_linkage.py -q` | 106 passed |
| C# host/combination filter | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Combination|FullyQualifiedName~Host"` | 225 passed, 0 failed |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |
| static guards | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | 21 guards, 0 red, exit 0 |

`verify-change.ps1` aborts on its `session-boundary` step: 13 pre-existing DRIFT pairs between
`keepverse-split.json` and `summoner-convergence-lane-c-20260919.json` / lane-d2 / lane-d3 /
`tvb-wave5-20260920.json` on files this task did not touch. Its `pytest: seedsmith` group therefore
did not run (the full `gk-forge/tools/seedsmith/tests` tree hangs; killed at 5 min and CI-owned).
