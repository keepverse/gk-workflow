# Seedsmith generator repair — task list

Plan: [seedsmith-generated-seed-repair-plan.md](seedsmith-generated-seed-repair-plan.md).
Hard rule: generated seed is regenerated, never hand-edited (AGENTS.md / CLAUDE.md);
guard `gk-core/scripts/guard-generated-seed.py` enforces it.

## Done (this session)

- [x] **Hard rule in AGENTS.md + CLAUDE.md** — generated seed is never hand-edited; fix the
      generator and regenerate. Includes the 2026-09-12 incident.
- [x] **`gk-core/scripts/guard-generated-seed.py`** — fails when a provenance-carrying file under a
      generated tree changes without its generator/tuning/registry. Proven to block a real
      hand-edit and to pass an authored `_registry/` edit.
- [x] **Wired the guard** into `.github/workflows/ci.yml` (with `fetch-depth: 2`) and
      `scripts/deploy-play.ps1`.
- [x] **Investigation** — both defects root-caused to the generator, not the data.

## S1 — corpus-wide existing names in the base-type brief

- [x] `basetypegen/run.py`: `load_corpus_names` reads **all** `base-types/**`; `run_draws` takes the
      map, re-asks once on a hit, then refuses the draw by name (prompt bloat avoided — 860 names
      would add ~16k chars per brief). Tests added; 60 pass.
- [x] `setgen/seedfile.py`: an unsluggable name raises `NameKeyUnsluggable` instead of minting the
      shared `set.item` placeholder key.

## S2 — per-frame implicit slate

- [x] Minted `gk-data/packs/fusion/data/seed/items/_registry/classes.v3.json` (registryVersion 5) with
      `legalFamiliesByFrame`; v2 stays frozen on disk.
- [x] `basetypegen/tuning.py`: `load_legal_implicit_families(role, frame)`; v2-shaped fixtures fall
      back to the union.
- [x] `FrameDirectionCheck` validates against the frame slate; `RegistrySet` reads v3.
- [x] Test: the two frames are offered disjoint slates for every role.

## S3 — re-slate generation run

- [x] New `basetypegen/reslate.py` (a generator verb, not a data edit): 649 rows re-slated onto
      their frame slate, identity + powerBand + class preserved (seed-contract §7.2).
- [x] Core `BaseTypeCorpusTests` 8/8; validator 0 frame errors.
- [x] `ImplicitFlavourDrift` warning wired (312 rows) — re-flavour stays the authoring fleet's, per
      spec-base-types.md.

## S4 — name collisions beyond set/charm

- [x] `ItemSeedValidator --collision-groups` prints the authoritative groups (its own
      NameNormalizer); exemplars excluded.
- [x] `name_repair` consumes the groups and covers every kind; per-row bounded retry names the
      rejected candidates; a failed row no longer discards the batch.
- [x] `NameCollision` + `NameKeyDuplicate`: **848 → 0**.
- [x] `recipegen`: nameKey minted from the unique `recipe.NNN` id (a recipe name repeats by design).
- [x] `iconKey` re-derived with `nameKey` (gemgen derives it); 343 stale rows fixed.

## S5 — placeholders

- [x] The 51 rows carrying `set.item`/`charm.item` renamed (their names are CJK, so the key cannot
      be re-derived; the name is what must change).

## S6 — gates

- [x] `guard-generated-seed.py` (CI + `deploy-play.ps1`) blocks a hand-edit of generated seed.
- [x] seedsmith suite: 3791 passed, 0 failed. Core 13361/13361. Guard 248/248 (flaky regen test
      fixed: temp OutDir + serial collection).

## Follow-ups (not this module)

- [~] `NameGrammarViolation` (808), `PossessiveForbidden` (159), `InventedConnective` (158),
      `PluralForbidden` (31), `FusionNotDecomposable` (27), `GeneratedOnlyNamePattern` (26): a
      separate naming-grammar pass over the same corpus.
      **SPECD 2026-09-20 by `backlog-clean-up` BCU8.7** →
      [`docs/architecture/item-seedgen/spec-naming-grammar-repair.md`](../docs/architecture/item-seedgen/spec-naming-grammar-repair.md)
      (item-seedgen module 13). The pass's code already shipped the same day (`d401f446`, `750b0dfd`):
      `naming_grammar.py` states the grammar in every authoring brief, `naming_grammar_repair.py`
      (`findings`/`plan`/`brief`/`validate_answer`/`run_batch`/`apply`) repairs what already shipped,
      driven by real `ItemSeedValidator --findings-json` output — never a hand-derived list, never a
      hand-edit of a generated `name`.
  - [ ] **WIRE 1 — a `seedsmith items` verb must reach `naming_grammar_repair`.** ⛔ **Owner: `seedsmith-cli-ux`.**
    `rg -n "naming_grammar_repair" gk-forge/tools/seedsmith/seedsmith/report/cli.py` returns no hits; the module's
    only importer is its own test, and `750b0dfd`'s own message says the corpus batches ran through a
    **still-uncommitted driver script**. By the repo rule that a mechanism no production host reaches is
    not done, this is the module's open half — the fix is a second verb beside `items repair-names`
    (`gk-forge/tools/seedsmith/seedsmith/report/cli.py:895-985`, parser `:3109`) with the same
    dry-run/`--write`/`--answers`/`--endpoint`/production-gate shape. Acceptance is the spec's §5 CLI test
    + its §8.1.
  - [ ] **WIRE 2 — finish the corpus through that verb.** **Owner: `item-seed-regen`.** The remaining rows
    are a reading, not a constant (811 at `750b0dfd`); the acceptance is `ItemSeedValidator` reporting 0
    for the six codes, reached through WIRE 1, with `guard-generated-seed.py` green.
- [ ] 312 `ImplicitFlavourDrift` rows — authoring fleet re-flavour.

- [x] **The seedsmith suite has 15 unregistered pre-existing failures (measured 2026-09-21). — REGISTERED 2026-09-21 (`seed-corpus-1`); per-test causes appended at the end of this row.**
  Attributed by the manager's base run (`tasks/reports/seedsmith-baseline-e0f1375d.json`): the suite at
  `e0f1375d` prints **22 failed / 4109 passed / 3 skipped** and at `cmdc/item-seed-gen`'s tip
  **20 failed / 4142 passed** — set difference empty, so no lane introduced these; the lane fixed two.
  Five more are registered `knownRed` (`SR-25`, all in `test_actions_description_completeness.py`), so
  the suite cannot read green until these 15 either pass or get an owning row each. Each is a
  real-corpus assertion (`python -m pytest gk-forge/tools/seedsmith/tests -q`), not a flake:

  - `tests/adapters/trees/test_nodegen_vocab.py::RealCorpusCountsTests::test_counts_125_families_and_their_tag_values`
  - `tests/test_affix_authoring.py::test_slot_eligible_families_are_derived_from_the_real_variant_axis`
  - `tests/test_channel_weight_backfill.py::test_real_corpus_missing_against_latest_is_empty_after_v5_backfill`
  - `tests/test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch`
  - `tests/test_corpus_loader.py::ConfigFilesSurviveTests::test_loading_the_live_corpus_raises_no_findings_today`
  - `tests/test_fusion_recipe.py::test_real_corpus_end_to_end`
  - `tests/test_general_propose.py::RealWorkedExampleTests::test_real_pipeline_entrypoint_threads_the_worked_example_into_the_dry_run_brief`
  - `tests/test_general_propose.py::RealWorkedExampleTests::test_real_worked_example_carries_the_real_pinned_answer_fields`
  - `tests/test_general_propose.py::RealWorkedExampleTests::test_real_worked_example_composes_with_the_real_family_glossary`
  - `tests/test_general_propose.py::RealWorkedExampleTests::test_real_worked_example_is_genuine_non_empty_content`
  - `tests/test_general_propose.py::RealWorkedExampleTests::test_real_worked_example_never_leaks_a_numeric_magnitude`
  - `tests/test_preflight.py::test_hash_matches_the_real_committed_dump`
  - `tests/test_themes_v2.py::test_publish_is_idempotent`
  - `tests/test_tree_plan_emit.py::RosterAndVocabularyTests::test_property_vocabulary_counts_match_the_spec_table`
  - `tests/test_usage_stats.py::TestRealCorpusTests::test_the_real_corpus_loads_and_reports_without_error`

  - **Why one row and not fifteen:** every one is the same contract — a test that asserts a property of
    the *committed* corpus while the corpus has drifted from what the test pins (vocabulary counts,
    dump hash, channel backfill, themes publish idempotence, general_propose worked example, cli
    domain loader, corpus loader findings). Fix by regenerating the corpus from its generator, or by
    re-pinning the test to the contract rather than a population reading — never by editing seed JSON.
    `docs/architecture/validation-ssot.md` is the standard.
  - **Owner:** this program (the seedsmith runbooks are its plan). Acceptance: each named test is green
    or individually registered with a row that names its cause; `dotnet run --project gk-forge/tools/ItemSeedValidator`
    stays green (it is 41 -> 0 on this line, so the validator is not the gate here).

  - **Cause read for `test_themes_v2.py::test_publish_is_idempotent`** (routed by the manager
    2026-09-21 from a finding of lane `sgc-2`; the finding is row T51 on that lane's branch,
    `cmdc/sgc-2`, and arrives on the integration branch with its merge): the three creature theme
    writers open the file for text WITHOUT `newline="
"`, so on Windows `
` becomes CRLF and a full
    pytest run dirties `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` (17,491 CRLF against 17,491 LF at
    HEAD; parsed JSON identical, bytes differ). Sites: `generate_themes.py:164` and `:250`
    (`Path.write_text`), `theme_enrich.py:148` (`os.fdopen(handle, "w", ...)`); the reachable caller is
    `test_themes_v2.py:49-52`, which calls `publish_v2(write=True)` against the production
    `CREATURES_ROOT`. Two sibling writers already shipped this fix (`name_repair._atomic_json`,
    `species_repair.py`). Fix = one `newline="
"` per writer plus a private-copy registry for the
    idempotency assertion.

  **REGISTERED 2026-09-21 (`seed-corpus-1`, base `00baecb5`) — re-measured, each cause named below.**
  The row's own alternate acceptance is *"green or individually registered with a row that names its
  cause"*, so each still-failing test gets its printed cause here. **Of the row's 15 named tests, 14
  still fail** — `test_themes_v2.py::test_publish_is_idempotent` now PASSES, because the CRLF cause
  this row names was fixed by lane `sgc-2` (row T51) and is in the base. **The measurement also finds a
  15th unregistered red this row's own list omitted** (`test_strain_splice_gen.py::ChassisTests::…`, in
  the table below), so the unregistered set is 15 and the suite reads `20 failed` = 15 + the 5
  registered `knownRed`. `dotnet run --project gk-forge/tools/ItemSeedValidator` is green
  (`partitions 1129 allocated prefixes`, `errors 0`, exit `0`), so the validator is not the gate.

  **One shared cause explains three of the fourteen.** `gk-data/packs/fusion/data/seed/actions/authored-basics.json`'s
  hand-authored `act.attack` spends `atom.fx-overlay-damage`, an id in `gk-data/packs/fusion/data/seed/atoms/fx-core.json`
  (the 17 demo families) but NOT in the 98 authored affix families the actions loader resolves
  (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/vocab.py:86`, `load_family_ids`). The result is
  `[GAP] Actions/Loader — act.attack: field 'atomFamilies' refused — unknown value
  'atom.fx-overlay-damage'`. This is already a **known, deliberately-not-fixed** condition:
  `gk-forge/tools/seedsmith/tests/test_coverage_report.py:888` records it and states that *"whether a
  hand-authored basic may spend a non-98 atom id is the action program's spec question, not this
  generator's"*. The three reds below are the staler side of that decision (tests still asserting the
  live corpus is finding-free), not a generator defect.

  | Test | Printed cause (verbatim) | Reading |
  |---|---|---|
  | `test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` | `assert 1 == 0` | `check --adapter actions --metric Actions/Loader gk-data/packs/fusion/data/seed/actions` returns exit 1: the `act.attack` GAP above. |
  | `test_corpus_loader.py::ConfigFilesSurviveTests::test_loading_the_live_corpus_raises_no_findings_today` | `Finding(code='unknown-family', path='authored-basics.json', message="act.attack: field 'atomFamilies' refused — unknown value 'atom.fx-overlay-damage'")` | Same root cause. |
  | `test_usage_stats.py::TestRealCorpusTests::test_the_real_corpus_loads_and_reports_without_error` | `assert 0 > 0` at `:220` | `populationSize` is 125 (first assert passed), `acceptedCount` is 0. Probable same `act.attack` load refusal; not read further. |
  | `test_strain_splice_gen.py::ChassisTests::test_the_corpus_host_set_is_a_subset_of_the_tuning_host_set_and_no_row_exceeds_its_ceiling` | `AssertionError: 4 != 8` at `:294` | **Not in this row's own list.** The corpus host set reaches 4 distinct roles while the tuning set's max is 8; the test asserts the corpus reaches the tuning set's own max (a coverage claim), and it no longer does. |
  | `test_general_propose.py::RealWorkedExampleTests` (all 5) | `'' is not true : the real pinned brief/answer pair must be found in this checkout`; `IndexError: list index out of range` at `:448`; `'atom.evd-brace:' not found in ''`; `'Worked example' not found in '…'` | `render_worked_example()` returns `""` because `test_general_propose.py:69` reads `data/seed/actions/_candidates/general/round-1.json` — **gitignored scratch** (`.gitignore:113`). A test-isolation defect: the "real pinned" pair was never committed. |
  | `test_nodegen_vocab.py::RealCorpusCountsTests::test_counts_125_families_and_their_tag_values` | `AssertionError: 17 != 19` | `tag_counts["utility"]` is 17, pinned 19 — a per-tag **population reading** still pinned after the total was relaxed (validation-ssot.md). |
  | `test_tree_plan_emit.py::RosterAndVocabularyTests::test_property_vocabulary_counts_match_the_spec_table` | `AssertionError: 54 != 55` | Committed property vocabulary is 54, the spec table names 55. |
  | `test_affix_authoring.py::test_slot_eligible_families_are_derived_from_the_real_variant_axis` | `assert {'atom.aura-b…d-grant', …} == {'atom.fx-gri…n-aura-power'}` | The real variant-axis family set no longer equals the pinned expectation. |
  | `test_channel_weight_backfill.py::test_real_corpus_missing_against_latest_is_empty_after_v5_backfill` | `assert 6 == 5` | The live missing-weight residual is 6 rows, the test pins 5. |
  | `test_fusion_recipe.py::test_real_corpus_end_to_end` | `json.decoder.JSONDecodeError: Extra data: line 2 column 1 (char 639)` | A committed file read as one JSON document holds more than one. |
  | `test_preflight.py::test_hash_matches_the_real_committed_dump` | `CheckResult(id=2, name='dump-is-current', ok=False, observed='6181dc2d5393e446…' … recorded hash cc322647cd0118c72d2dc80826cfe7cea7d02077a59aedfb0bb167319d38a10d)` | The creature dump moved past its recorded hash. |

  Re-measured command: `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest <each test> -q --tb=line`; the full
  suite reading at this base is `20 failed, 4260 passed, 3 skipped` (`15` unregistered = `14` from this
  row's list + `1` it omitted, + `5` registered `knownRed` `SR-25` in
  `test_actions_description_completeness.py`). Evidence: `tasks/evidence-fragments/SGR-register.md`.

## 2026-09-26 — SR-25 is CLOSED; its five `knownRed` registrations are now stale exemptions

Appended, not rewritten: the `20 failed` reading above stands as the historical measurement at its
base. This section records a later, narrower measurement that changes what those five entries mean.

**Measured.** The five `SR-25` node ids in `gk-core/scripts/verification-boundaries.v1.json` were run
directly: `5 passed in 159.67s`. The whole file: `12 passed in 296.55s` — so
`test_actions_description_completeness` is green end to end, not partially.

**Not vacuous.** A content-completeness test that passes because it read nothing is the worst shape
of green here, so the corpus was measured through the test's own loader rather than assumed:
`LIVE_ACTIONS_ROOT` resolves to `gk-data/packs/fusion/data/seed/actions` (79 json files), and `load_committed` returns
**33,073 entries** with `findings == []`. The pass is over real content.

**How it closed.** By correcting an assertion, not by filling a corpus. One of the five carries
`⚠ CORRECTED 2026-09-23 (lane sgc-6)`: it had demanded a `description_backfill._provenance` on every
`action-seed` entry, which contradicts `gk-data/packs/fusion/data/seed/actions/authored-basics.json` — that file's own
`_meta.authored` records that the row deliberately carries no `_provenance`, because that absence is
what marks authored content apart from generator output. The blanket assertion therefore demanded
the hand-edit the authored-content rule forbids. Correcting it is the sanctioned resolution for a
stale test, so SR-25 is genuinely closed.

**Correction of an intermediate wrong reading.** A first pass measured `0 of 79` action files
carrying a top-level `description` or `content` and read it as a corpus defect. That was a shape
error, not a defect: those 79 files are aggregates, the field is per entry, and the corpus holds
33,073 of them. Recorded because the wrong number is the one that would have been quoted.

**The defect this exposes.** `guard-verification-boundaries.py` validates each `knownRed` entry for
field shape, a known project, an existing test file, and a `debt` id that resolves — and **never
that the entry is still red**. So a green test stays exempted indefinitely, reported as tolerated
debt, and the closure is invisible. Five such entries exist today. The blast radius is bounded: the
match derives classname from the file part, so a stale entry cannot exempt a different file
(`known_red_test_matches_node`, `gk-core/scripts/lib/verification_boundaries.py:384-394`). The consequence is
a lie in the report, not a cross-file false exemption.

**Open, and not this ledger's to close.** Removing the five entries is a seedsmith-programme decision
(they mirror SR-25 here); adding a "still red" check belongs to the registry/guard plane. The
registry itself was unclaimed when measured, and `scripts/**` sits with `ps1-ban-manager-20260926`
per the manager session's `ps1BanSplit` — so both are routed rather than taken.
