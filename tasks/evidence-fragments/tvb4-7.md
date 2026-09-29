# TVB4.7 — Map `gk-data/packs/fusion/data/seed/**`; switch the root on; doc paragraph

## Result

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Per-subtree owners per S2 (`items/creatures/_dump/structures/atoms+generated/passive-tree`), the rest by S1 | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` (331 boundaries, 293 -> 331: +38) | `gk-core/scripts/verification-boundaries.v1.json` |
| Root switched on; every `gk-data/packs/fusion/data/seed/**` file resolves | resolver over `Get-ChildItem -Recurse -File gk-data/packs/fusion/data/seed` vs `Resolve-Owner` | **2176 files, 0 unresolved** (before this commit: 2151 of 2176 unresolved) | `scripts/lib/VerificationBoundaries.ps1:46` |
| Authored sub-trees separated where the reader differs; generated trees carry `generated-seed` | same guard run | 13 new `generated-seed`-carrying owners (items, creatures, structures, passive-tree, atoms/generated, dungeon, actions) | `gk-core/scripts/verification-boundaries.v1.json` |
| S-T6 (real registry, all four roots) + S-T1..S-T5, S-T7, S-T8 | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~EnforcementRegistry"` | `Passed! - Failed: 0, Passed: 74, Skipped: 0, Total: 74` | this fragment |
| `testing-standard.md` §6 paragraph (data inputs select through the planner; `full` = CI-only) | read | added | `docs/contributing/testing-standard.md` |
| `-Report` "inputs with no local proof" printed | `python gk-core/scripts/guard-verification-boundaries.py --report` | 24 `full` boundaries (19 before; +5 `gk-data/packs/fusion/data/seed/**`) | this fragment |

## S1 evidence per new owner (one line each; full list in the commit body)

- `items/**` -> `gen-items-gate` + seam `gen-item-seed-validator`; `creatures/**` -> `gen-creature-contract` + seams report/metrics/preflight; `creatures/_dump/**` -> `gen-corpus-dump-verify`; `structures/**` -> `gen-structure-contract`; `passive-tree/**` -> `gen-passive-tree`; `atoms/generated/**` -> `gen-family-expand` (S2's own named set).
- `dungeon/**`/`actions/**` -> `seedsmith` (pytest): `gk-forge/tools/seedsmith/tests/test_dungeon_domain_content.py:1`, `test_actions_description_completeness.py:3` read the real trees; `zomboss/**` -> `seedsmith` (`test_dungeon_registries.py:318`).
- `channel-pools/**` -> `core-atoms` (`ContentValidationTests.cs:456`); `loot/**`,`containers/**`,`rarity/**`,`power/**`,`effects/**` -> `core`; `elements/**` -> `elementenumgen` (`ElementEnumCheckTests.cs`); `statuses/**` -> `passivetreerostergen` (`RosterMirrorTests.cs:64`); `resources/**`+`aptitudes/**` -> `gen-resource-ownership` (`resource_ownership.py:64-84`); `derived-stats/catalog.json` -> guard `stat-pairs` (`guard-stat-pairs.ps1:12`).
- `full` (no local proof): `derived-stats/lexicon.v1.json`, `external-reference/**`, `display/**`, `curves/**`, `README.md`.

## Guard-walk cost fix (required by S-T6)

`Resolve-Owner` scanned every boundary per file; with the whole `data/**` tree now under the enforced-root
walk, `Integrity_guard_passes_on_the_current_registry` timed out at the 120s test ceiling (2/74 red, re-run
alone still red). Fixed in the shared lib (the guard script is a protected pipeline file): boundaries are
indexed by first path segment, memoized on the boundary array instance.
`python gk-core/scripts/guard-verification-boundaries.py`: 145/151s -> **22.0/24.3s**.
Equivalence proof over every tracked file: **12722 paths, 0 differences** (indexed vs the pre-change scan).
`gk-core/scripts/guard-verification-boundaries.py` edit attempt was refused by the pipeline guard -> ledger `blocker` note; no retry, no alternate route.

## Not proved

- The 2176-file resolution check is a repo-tree reading, not a pinned contract (nothing asserts a file count).
- `seed-*.seam` projects are planned, not executed, in this task; the plan is proven, the runs are not.
- No test pins the `$Script:EnforcedRoots` membership; S-T4 proves the on/off mechanism, not this list.
