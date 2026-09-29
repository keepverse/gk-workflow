# Task 3 — seedsmith derive + runner wiring

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 3. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §1.
Edited: `anchor/schema.py` (`rank` joins `DERIVED_FIELDS` + `RANK` vocabulary + schema property),
`anchor/descriptions.py` (`rank` entry — no `KeyError`), `anchor/derive.py` (`load_rank_grid` + `derive_rank`),
`run/runner.py` (three call sites), `tests/test_anchor_derive.py`, `tests/test_anchor_emit.py`,
`tests/test_run_runner.py`. `anchor/emit.py` needed **no** edit (it reads `DERIVED_FIELDS`), as the spec states.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `rank` joins `DERIVED_FIELDS` + schema property + `descriptions.py` (no KeyError) | `python -m pytest tests/test_anchor_contract.py tests/test_anchor_emit.py -q` (in `gk-forge/tools/seedsmith`) | green — `_derived` now `['basis','posture','pure','rank','speciesKind']`; every property has a description with a negative clause; the schema still audits clean | `tests/test_anchor_emit.py`, `tests/test_anchor_contract.py` |
| `audit_schema` clean | `python -m pytest tests/test_preflight.py -q` → `test_contract_audits_clean_against_the_real_schema` | **passed** (`numeric_audit(build_anchor_schema()) == []`, `anchor/preflight.py:151`); the file's one red is `test_hash_matches_the_real_committed_dump`, pre-existing (see below) | `tests/test_preflight.py` |
| `derive_rank` handles voted / fallback-stamped / unresolved | `python -m pytest tests/ -q -k "anchor or rank"` | **186 passed, 1 skipped, 4176 deselected, 1176 subtests passed, 8.97 s** — resolved pair → the grid's own cell; `"unresolved"`/`None` on either axis → `"unresolved"`; out-of-vocabulary pair → `"unresolved"`, never a crash; grid covers every `THREAT_BAND × RARITY` pair and is diagonal-by-default | `tests/test_anchor_derive.py` |
| Wired at `_finalize`, `fix_unresolved` recompute, scoped-rerun merge | `python -m pytest tests/test_run_runner.py -q` | green — `fix_unresolved` stamps the rung AND recomputes rank; a rarity-only `identity` scoped rerun moves rank with it and leaves nothing stale | `tests/test_run_runner.py::test_a_rarity_only_scoped_rerun_recomputes_rank_and_never_leaves_it_stale` |
| Every creature/anchor test that reads the touched modules | `python -m pytest tests/test_anchor_contract.py tests/test_anchor_derive.py tests/test_anchor_emit.py tests/test_species_kind_and_measured_basis.py tests/test_classify_pipelines.py tests/test_run_orchestrator.py tests/test_run_runner.py -q` | **170 passed in 74.94 s** | — |
| Consumers of `build_anchor_schema`/`DESCRIPTIONS` elsewhere | `python -m pytest tests/test_build_favour_relead.py tests/test_dungeon_contract.py tests/test_roster_metrics.py tests/test_structure_anchor_contract.py tests/test_structure_corpus.py tests/test_structure_planner.py tests/test_unique_briefs.py -q` | **154 passed in 11.93 s** | — |
| Creature adapter / corpus / metrics | `python -m pytest tests/test_adapter_creatures.py tests/test_creature_metrics.py tests/test_creature_themes.py tests/test_creatures_completeness.py -q` | **passed** (only `test_preflight.py`'s pre-existing dump-hash red in that batch) | — |
| Static guards | `pwsh -NoProfile -File scripts/guard-vocabulary-mirror.ps1` · `guard-population-pin.ps1` · `guard-test-substrate.py` | `OK — 9 pair(s), no drift` · `total 0 finding(s)` · `TEST SUBSTRATE GUARD OK` | — |
| No ladder restatement introduced | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~LadderRestatementGuardTests"` | **Passed! — Failed 0, Passed 13, Total 13, 739 ms** (`RANK = _RARITY_LADDER` is the declaring read, not a retyped tuple) | — |
| Task 1/2 files still green post-merge | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~CreatureRank"` | **Passed! — Failed 0, Passed 29, Total 29, 94 ms** | — |

## NOT proved / findings

- **The full `gk-forge/tools/seedsmith` suite is `not_run`.** It was started once and killed by an infrastructure
  interruption at ~56% (the same kill that ended two `verify-change` runs). The scope that covers this
  change was run instead — every test file that imports the anchor schema/`DESCRIPTIONS`/`derive`/`emit`
  or drives the runner, plus the corpus/metrics files — 324 passed across the two batches above.
- **Pre-existing red, not mine, with the evidence that proves it:**
  `tests/test_preflight.py::test_hash_matches_the_real_committed_dump` — the committed
  `gk-data/packs/fusion/data/seed/creatures/_dump` hashes to `6181dc2d…` while the recorded value is `cc322647…`.
  `git log --oneline 18972a5dc8f5..HEAD -- gk-data/packs/fusion/data/seed/creatures/_dump` is **empty** (this branch never
  touched the dump); the last commits touching it are `ab16afbf8` and `740920d2e`.
  `tests/test_actions_description_completeness.py` reads **5 failed, 6 passed** (the actions adapter,
  untouched here; AGENTS.md documents this file as failing pre-existing and 4 of its cases are the
  registry's own `knownRed`/SR-25 entries).
- `tests/test_anchor_emit.py::test_derived_fields_carry_the_derived_marker` needed its closed
  declaration widened by exactly one member (`rank`), with the reason in the comment — it pins a
  CLOSED vocabulary the code owns, so updating it is the intended maintenance, not a weakened guard.
- `derive_rank` never fabricates: an out-of-vocabulary pair derives `"unresolved"` rather than
  crashing (the shape `clamp_variant_count` already established), and the grid's own full coverage is
  asserted at load so that branch can only mean an anchor outside the closed vocabulary.
- `load_rank_grid` is `lru_cache`d (a pure read of a committed, versioned file); `derive_rank` runs
  once per species per write path. The cache cannot go stale inside a process.
- Task 4 (the anchor regen) is what makes the committed corpus carry rank; this task only wires the
  derivation, so `gk-data/packs/fusion/data/seed/creatures/species/**` is deliberately untouched here.
