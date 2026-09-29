# SGC5-F1 — track a minimal actions fixture (owner ruling 2026-09-23)

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, which is OUTSIDE this
lane's allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the six tests pass on a clean checkout | `python -m pytest tests/test_usage_stats.py tests/test_general_propose.py -q` (cwd `gk-forge/tools/seedsmith`) | **104 passed, 12 subtests passed in 10.16s** (was `6 failed, 98 passed in 8.94s`) | this checkout has NO `data/seed/actions/_candidates/` |
| fixture committed in the same commit that removes the dependency | `git show --stat HEAD` | `gk-data/packs/fusion/data/seed/actions/_fixtures/general/round-1.json` — 1441 B, tracked, copied verbatim from the real accepted draft | |
| the gitignored path is no longer read | `grep -rn "_candidates" gk-forge/tools/seedsmith/seedsmith/adapters/actions/general_propose/prompts.py gk-forge/tools/seedsmith/tests/test_general_propose.py` | no hit; both name `_fixtures/general/round-1.json` | |
| a machine that ran the pipeline still reads the LIVE corpus | `derive._round_corpus_root` | runtime `_candidates/` wins whenever it holds a non-excluded round file; the fixture is used only when it is absent — no double-count | |
| the live corpus load gains no finding from the new prefix | `python -m pytest tests/test_corpus_loader.py -q` | same single failure as before the fixture (`unknown-family act.attack`, SGC5-F2) — **no `undeclared-prefix`** | `_manifest.json` declares `_fixtures/` `exclude` |
| registry `seedsmith-actions` selected test files | `python -m pytest <the 23 files in the seedsmith-actions boundary> -q`, 3 chunks | 155 passed / 2 skipped; 735 passed / 1 skipped / 1167 subtests; 7 failed (= 5 pre-existing `test_actions_description_completeness` + SGC5-F2's 2) | |
| boundary registry | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | |
| generated-seed guard | `verify-change.ps1` plan step | `[guard-generated-seed] clean (7 changed file(s) inspected)` | |
| registry `test: core` / `test: data` seams | not run | `not_run` — no C# code reads `gk-data/packs/fusion/data/seed/actions/_manifest.json` or globs that tree; `gk-core/src/FusionRpg.Server/Program.cs:752` reads named `committed-round-*.json` files only, so an excluded prefix + one fixture file cannot reach them. The whole-group selection (**68** Core projects + Data + Guard, no `VerificationId`) exceeds the segment budget. ⚠ *Re-measured 2026-09-23 at the end of this lane:* the plan still names the same three boundaries and the whole `core` group, and that is now known to be **deliberate, not an unowned defect** — TVB4.7 (`tasks/test-verification-boundary-todo.md:212`) mapped `gk-data/packs/fusion/data/seed/**` and set `actions/**` → `seedsmith` on 2026-09-21, and TVB6.2/6.3 landed 2026-09-23 (lane tvb60) narrowing 24 *focused* `core.*` boundaries while leaving the seam's `project: core` alone. So this is TVB's accepted seam shape and TVB's todo owns any change to it, not this lane's. | |

## Extension 2026-09-23 — the fallback branch is now pinned by tests (it was not)

The first pass changed `usage_stats/derive.py` (the new `_round_corpus_root` / `_has_real_round_file`
seam) and leaned on the existing tests to exercise it implicitly — this checkout has no `_candidates/`,
so only the FIXTURE branch ever ran. The runtime-authoritative branch, and the reason the fixture is
never mixed in, were untested. Six cases now pin both (`TestRoundCorpusRoot` x4,
`TestTrackedWorkedExampleFixture` x2):

| Criterion | Command | Result |
|---|---|---|
| the new seam is covered | `python -m pytest gk-forge/tools/seedsmith/tests/test_usage_stats.py -q -p no:cacheprovider` | **28 passed** (was 22) |
| the ruled acceptance, unchanged | `python -m pytest gk-forge/tools/seedsmith/tests/test_usage_stats.py gk-forge/tools/seedsmith/tests/test_general_propose.py -q -p no:cacheprovider` | **110 passed, 12 subtests passed** (was 104 + 12) |
| what the four branch cases assert | read | the runtime `_candidates/` root wins whenever it holds a real round file (and the fixture is not mixed in); the fixture is used when that dir is absent; a dir holding ONLY the model-experiment file (the name `_EXCLUDED_SUFFIX` matches, a gitignored runtime file) is not a corpus (the excluded-by-name case) and still falls back; and `build_report` on a fixture root counts exactly its one accepted row (`acceptedCount == 1`, `latestRoundNumbers == {"general": 1}`) |
| what the two fixture cases assert | read | the committed fixture still carries the pinned accepted `candidate.general.003` for `brief.general.general.004`, and every family it names is a member of the real affix-family corpus (a membership join, never a count) |

## The fixture's faithfulness, re-verified and stated exactly (2026-09-23, lane sgc-6)

The fixture is the authoritative pinned pair now, so "copied verbatim" is a claim worth reproducing —
and it was slightly too broad. Compared against the real source (`data/seed/actions/_candidates/general/
round-1.json`, present in the main checkout), `candidate.general.003`'s draft:

| Field | Identical? |
|---|---|
| `name` | ✅ |
| `flavor` | ✅ |
| `atomFamilies` | ✅ |
| `rationale` | ✅ |

So the four CONTENT fields are byte-identical. The fixture's draft has five keys against the real
draft's eight: it deliberately drops the plumbing (`_provenance`, `briefId`, `candidateId`, `scope`) —
`prompts._WORKED_EXAMPLE_ANSWER_KEYS` shows the model only the schema-required fields — and it ADDS
`blocked: ""`, because the action schema requires that key while the real accepted draft leaves it
absent (which the code reads as falsy). The fixture's own `_meta.note` now says exactly that instead of
the blanket "verbatim", so the next reader is not misled about which half is a copy.

Re-measured after the note edit: the file parses, the fixture's draft keys are
`['atomFamilies', 'blocked', 'flavor', 'name', 'rationale']`, and SGC5-F1's acceptance pair still reads
**110 passed, 12 subtests passed**.
