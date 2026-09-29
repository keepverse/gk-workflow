# Task list: narrative-seed

Plan: [narrative-seed-plan.md](narrative-seed-plan.md). Program id: `narrative-seed`. Specs:
`docs/architecture/narrative-seed/spec-<module-id>.md`.

**Conventions for every task.**

- **One task = one commit**: code, tests, evidence (the verification output's decisive lines in the
  commit body) and this file's status line for the task, staged by explicit path. No push, no amend, no
  watermark. Clean-or-skip on every shared file (plan §8).
- **`<sid>`** is the implementing session id recorded at NS0.
- **Seedsmith verification**, from the repo root:
  `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/<file> -q`
  (written `SS <file>` below). Until NS1/NS2 land, `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/dungeon/**` and
  `gk-data/packs/fusion/data/seed/narrative/**` are unmapped (`scripts/verify-change.ps1:118`); after they land, also pass
  those paths to `verify-change.ps1`.
- **Mapped paths** go to `.\scripts\verify-change.ps1 -Paths <paths> -Session <sid>`:
  `gk-core/scripts/enforcement-registry.v1.json`, `gk-core/scripts/verification-boundaries.v1.json`, `.github/workflows/**`
  (boundary `ci-workflows`), `docs/**`, `tasks/**` — all four confirmed against the registry on 2026-09-20.
- **Plan audit 2026-09-20 — `gk-forge/tools/seedsmith/seedsmith/report/cli.py` is shared with `ip-censor` T16.**
  Every task below that edits it runs `git status --porcelain -- gk-forge/tools/seedsmith/seedsmith/report/cli.py`
  first and **skips on a dirty file** (plan §6, §8). Each edit registers a new verb, so distinct regions
  merge cleanly; a region overlap goes to the owner.
- **Every test** stubs the model transport so a real call raises (`FakeCall`,
  `gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py`; `test_offline_guarantee.py`), and asserts
  contracts and closed vocabularies only — never a corpus size, a per-cell count, a call total or
  generated text.
- **Model tasks** (marked **[model]**) state the budget as base / worst calls from the call-shape table,
  run `--dry-run` first (it prints the real figure; that figure is what is approved), run
  `narrative preflight` (one real call) before spending, review a sample, and commit only accepted output.
- **Status line** per task: `Status: open` → `Status: done <short sha> — <one line>` (or `skipped: <file>
  dirty`, `awaiting G<n>`, `waiting on <dependency>`).

---

## Phase 0 — Boundary and verification

- [ ] **NS0 Session record.**
  *Files:* `tasks/sessions/narrative-seed-build-<yyyymmdd>.json` (new), this file (status line).
  *Accept:* record lists mode, branch, the one problem, and `paths` covering this program's files
  (plan §8 table); `session-boundary-check.py --session <sid>` reports no drift naming this session.
  *Verify:* `python scripts/session-boundary-check.py --session <sid>`;
  `.\scripts\verify-change.ps1 -Paths tasks/sessions/<sid>.json,tasks/narrative-seed-todo.md -Session <sid>`.
  *Commit:* `narrative-seed NS0: session record`. Status: blocked — `tasks/sessions/**` is **outside this run's
  allowed paths**, so the record cannot be written from this lane; `verify-change.ps1 -Session
  narrative-seed-1` consequently reports `session record not found` for every row, and every row in this
  lane has been verified with the strongest achievable form instead (`-AllowUnscoped`, or the focused
  `-PlanOnly` reading). **What the manager must grant** (one line): add `tasks/sessions/**` to this lane's
  allowed paths, or create `tasks/sessions/narrative-seed-build-20260923.json` itself. The exact record
  body is ready and needs no further reading: `{"session": "narrative-seed-1", "program":
  "narrative-seed", "problem": "Build Wave 0 of the narrative-seed program: seedsmith model-config
  resolution, script check, gloss registry and the Delve event generator repair.", "mode": "worktree",
  "branch": "cmdc/narrative-seed-1", "paths": ["gk-forge/tools/seedsmith/**",
  "docs/architecture/narrative-seed/**", "docs/architecture/narrative-seed-map.md",
  "docs/architecture/narrative-seed-ideal.md", "tasks/narrative-seed-todo.md",
  "tasks/narrative-seed-ledger.jsonl", "gk-data/packs/fusion/data/seed/**", "gk-core/data/tuning/**", "scripts/**"],
  "started": "2026-09-22T22:00:00Z", "status": "active"}`

- [x] **NS1 Verification boundary: the narrative seedsmith area.** *Depends:* NS0; external
  TVB3.3 (`tasks/test-verification-boundary-todo.md:182`, lane D2). Early in the list, executed when its
  dependency lands; nothing waits on it.
  *Files:* `gk-core/scripts/verification-boundaries.v1.json` (rows for `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/**`,
  `gk-forge/tools/seedsmith/seedsmith/briefkit/gloss.py`, `gk-forge/tools/seedsmith/seedsmith/workflow/validators/scripts.py`,
  `workflow/validators/prose.py` and `tools/seedsmith/tests/test_narrative_*.py`,
  `test_briefkit_gloss.py`, `test_no_model_literal.py`; added through TVB3.3's area derivation if it
  ships one, otherwise as one reviewed row per area), `gk-core/scripts/enforcement-registry.v1.json` (switch the
  D4 pytest-enforced rows to the python lane's catalog form, if TVB publishes one).
  *Accept:* `verify-change.ps1 -PlanOnly` resolves every listed path to a narrative boundary that selects
  its own pytest files, not the whole seedsmith suite; the registry's guard tests are green.
  *Verify:* `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Default if TVB3.3 has not landed:* stays open; every task uses `SS <file>`.
  *Commit:* `narrative-seed NS1: verification boundary for the narrative seedsmith area`. Status: done f6b9187d1 + this commit —
  TVB3.3 **has** landed (registry `schemaVersion` 5, `seedsmith` project with 25 boundaries, TVB
  checkpoint 3 all `[x]`), and two of the three areas now resolve: `briefkit/**` →
  `seedsmith-narrative-briefkit` → `tests/test_briefkit.py`, `workflow/validators/**` →
  `seedsmith-narrative-validators` → `tests/workflow/validators/test_language.py`; the test paths
  (`test_narrative_*.py`, `test_briefkit_gloss.py`, `test_no_model_literal.py`) already resolve through
  `seedsmith-tests` (selfSelect, focused). **The `adapters/narrative/**` row cannot land**: the
  integrity guard hard-fails a `testFiles` pattern matching no real test file (planted run:
  `testFiles pattern matches no test file: seedsmith-narrative: tools/seedsmith/tests/test_narrative_*.py`),
  and the first narrative test file arrives with NS14/NS31 — no task's *Files* line names this registry
  row, so it needs an erratum (map it with the test that creates it, or accept a `level: module` row
  now). **CLOSED when NS14 created the path**: `seedsmith-narrative` now owns
  `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/**` and its `test_narrative_*.py` pattern matches a
  real test file, so the erratum's own condition is met; NS14 also added `seed-narrative-exemplars`
  for `gk-data/packs/fusion/data/seed/narrative/_exemplars/**` (the `gk-data/packs/fusion/data/seed/**` enforced-root walk required it). `enforcement-registry.v1.json` needs **no** change: TVB published no python-lane catalog form
  (all 25 guard entries are `.ps1` scripts; invariant rows carry guard ids, not pytest node ids).

- [ ] **NS2 Verification boundary: `gk-data/packs/fusion/data/seed/narrative/**` and `gk-data/packs/fusion/data/seed/dungeon/events/**`.**
  *Depends:* NS1; external TVB4.7 (`tasks/test-verification-boundary-todo.md:273`).
  *Files:* `gk-core/scripts/verification-boundaries.v1.json`.
  *Accept:* a registry or corpus path under `gk-data/packs/fusion/data/seed/narrative/**` selects the narrative reader and
  contract tests (and, once `npc-story-events`' `narrative-vocabulary` exists, its C# reader tests);
  `gk-data/packs/fusion/data/seed/dungeon/events/**` selects the dungeon event tests.
  *Verify:* `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json -Session <sid>`.
  *Default:* as NS1. *Commit:* `narrative-seed NS2: verification boundary for the narrative corpus`. Status: blocked a5329cb1f —
  TVB4.7 (the `gk-data/packs/fusion/data/seed/**` mapping) **has** landed, and `gk-data/packs/fusion/data/seed/dungeon/events/**` now resolves to a
  new `seed-dungeon-events` owner row (focused, `generated-seed` guard) selecting the four dungeon
  event/contract tests (57 passed) instead of the whole `seedsmith` module run. The
  `gk-data/packs/fusion/data/seed/narrative/**` row cannot land yet for the same reason NS1's `adapters/narrative/**` cannot:
  the integrity guard hard-fails a `testFiles` pattern matching no real test file, and the narrative
  reader/contract test (`test_narrative_contract.py`) arrives with NS30/NS31. **Partly closed by NS8**: the
  `_registry/**` and `_plan/**` halves now resolve to `seed-narrative-registry` / `seed-narrative-plan`
  (focused, via `test_briefkit_gloss.py`, which reads both files); only the storylet/character/arc/spine
  corpus readers remain, and they arrive with NS30/NS31/NS33. Same erratum ruling for that remainder.

---

## Phase 1 — Wave 0: repair and shared foundations

### `model-config-resolve` (spec: `spec-model-config-resolve.md`)

- [x] **NS3 The transport resolves late.** *Depends:* NS0.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py` (`call_model`, `call_with_self_heal` take
  `config: LlmCallerConfig | None = None`; `None` → `load_config()` at call time),
  `gk-forge/tools/seedsmith/tests/test_llm_caller.py`.
  *Accept:* `call_model_resolves_env_when_config_omitted` (hermetic `.env` fixture sets
  `SEEDSMITH_LLM_MODEL`; the stub transport receives it); `DEFAULT_CONFIG` stays only as the bottom
  layer inside `llm_caller.py`; existing transport tests unchanged.
  *Verify:* `SS test_llm_caller.py`. *Commit:* `narrative-seed NS3: seedsmith transport resolves its config at call time`. Status: done 3a0616a9f — transport resolves late; `DEFAULT_CONFIG` is now only `load_config`'s bottom layer in `llm_caller.py`

- [x] **NS4 Class A literals and the families CLI.** *Depends:* NS3.
  *Files:* the five `tools/seedsmith/seedsmith/adapters/actions/generate_*.py` files,
  `adapters/creatures/generate_commander_effects.py`, `adapters/effects/affix/generate_affixes.py`,
  `adapters/creatures/generate_families.py` (`--model`/`--endpoint` default `""` via
  `resolve_live_transport`), their existing tests.
  *Accept:* no adapter builds `LlmCallerConfig(model=<literal>)`; each entry point forwards
  `config: LlmCallerConfig | None`; a stubbed call from each entry point receives the resolved model.
  Before editing, run `SS test_actions_description_completeness.py` on HEAD and record it as pre-existing red
  (AGENTS.md "Seedsmith").
  *Verify:* each touched adapter's own test file with `SS`. *Commit:* `narrative-seed NS4: remove model literals from action, commander and affix generators`. Status: done 4acf906a3 — eight entry points resolve through `resolve_live_transport` (CLI flags default `""`), none builds `LlmCallerConfig(model=<literal>)`, no `DEFAULT_CONFIG` reference remains in them

- [x] **NS5 Class B provenance records what ran.** *Depends:* NS3.
  *Files:* `adapters/items/{affixfamgen,basetypegen,recipegen}/emit.py`,
  `adapters/items/{basetypegen,droptablegen,gemgen}/run.py`, their tests.
  *Accept:* every emitter's `model` is a required keyword; the closed sentinels are a resolved id,
  `unrecorded`, `none` (`provenance_sentinels_are_closed`); calling without `model` raises `TypeError`
  (`provenance_model_is_the_resolved_model`); no committed seed changes.
  *Verify:* `SS test_affix_families_gen.py` and each touched generator's test. *Commit:* `narrative-seed NS5: item emitters stamp the resolved model or a closed sentinel`. Status: done 3ff951918 — seven emitters require `model` (no default), validate it through `provenance_model` (`unrecorded`/`none` closed sentinels), and every production caller passes the resolved `config.model` or `none`; no committed seed changes

- [x] **NS6 Class C and the model-literal test.** *Depends:* NS4, NS5.
  *Files:* every function or CLI default referencing `DEFAULT_CONFIG` outside `llm_caller.py` (the test
  lists them; e.g. `adapters/dungeon/pipelines.py`, `workflow/nodes/generate.py`),
  `gk-forge/tools/seedsmith/tests/test_no_model_literal.py` (new), `docs/architecture/decisions.md` (map §11 row 2).
  *Accept:* the five shapes S1–S5 each proven by a positive and a negative fixture (docstring and comment
  pass; stems match on token boundaries only); `package_has_no_model_literal` green. The
  `seedsmith-no-model-literal` row lands with the guard script in NS6b (Alignment 2026-09-20, plan D4).
  *Verify:* `SS test_no_model_literal.py`; the whole seedsmith suite once (this task crosses adapters):
  `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q`;
  `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS6: no model literal in seedsmith`. Status: done 2026-09-23 — the guard
  (`test_no_model_literal.py`, 7 tests) and the Class-C removal (26 files, zero `DEFAULT_CONFIG`
  outside `llm_caller.py`) landed; the `docs/architecture/decisions.md` row the *Files* line names is
  **outside this session's fence** (the runner's allowed paths do not include it), so it needs a fence
  grant or an erratum ruling. `verify-change.ps1 -Session narrative-seed-1` cannot run at all for the
  same reason: NS0's record under `tasks/sessions/**` is also outside the fence — the strongest
  achievable check (`-Paths docs/architecture/decisions.md -AllowUnscoped`) is recorded instead.
  **Closed by lane `ns-2`:** that path IS in this lane's allowed paths, so the drafted R6 row (map §11 item 2)
  landed with the resolution order and the guard test named; `verify-change.ps1 -Paths
  docs/architecture/decisions.md -AllowUnscoped` → exit 0, doc-citation 0 findings, `guard.doc-boundary`
  4 passed; `SS test_no_model_literal.py` → 7 passed; `DEFAULT_CONFIG` outside `llm_caller.py` → 0. The
  whole-suite line stays the predecessor's reading (4353 passed / 19 pre-existing failures, ledger
  `mk1-c150d350553754f0`), attributed, not re-run for a doc-only increment. Evidence:
  `tasks/evidence-fragments/narrative-seed-NS6.md`.

- [ ] **NS6b The program's catalogued guard script and its first row** (Alignment 2026-09-20).
  *Depends:* NS6. *Agent:* **implementer-hard** (plan D6b — it re-orders a CI job step, so a wrong order
  turns every guard red for every lane in the repo).
  *Files:* `scripts/guard-narrative-seed.ps1` (new), `gk-core/scripts/enforcement-registry.v1.json` (guard catalog
  entry `narrative-seed` — `script`, `tier: ci`, `status: gating`, `backlogModule: null`,
  `localReason: null` — plus the invariant row `seedsmith-no-model-literal` with
  `guards: ["narrative-seed"]`), `.github/workflows/ci.yml` (move the "Install seedsmith from the
  lockfile" step above the "Boundary guards" step, `:241` vs `:295`; both are steps of the single `test`
  job, `:14`, so the move is within one job — verified 2026-09-20),
  `gk-core/scripts/verification-boundaries.v1.json` (**Plan audit 2026-09-20**, plan D3 rule 4: the new row
  `guard-narrative-seed`, paths `scripts/guard-narrative-seed.ps1`, project `guard`, `level: module`, no
  `verificationId` — an unmapped production path is a boundary defect, and this task creates one).
  *Shape (plan D4):* one guard script per program. `npc-story-events` lands its rows through
  `gk-core/scripts/guard-narrative.py`; the two share no code, run different runners over different trees, and
  never invoke each other, so neither program edits the other's file while both are active.
  *Accept:*
  - The script holds one committed check line per invariant row (row id → pytest node ids) and runs them
    with `python -m pytest … -q -p no:cacheprovider` and `PYTHONPATH=gk-forge/tools/seedsmith`; it exits non-zero
    naming the row whose check failed.
  - It **fails loudly**, naming the missing interpreter or package, when it cannot run a check — it never
    passes vacuously (the same reason the release scan resolves its root explicitly).
  - **Plan audit 2026-09-20 — no row can be guarded on paper only.** The script reads
    `gk-core/scripts/enforcement-registry.v1.json`, derives the set of invariant ids whose `guards` contains
    `narrative-seed`, and exits non-zero naming (a) any such row with no check line in its own table and
    (b) any check line naming no such row. A check that selects **zero** pytest node ids also exits
    non-zero. Falsifier, run in the verify step: add a throwaway row with `guards: ["narrative-seed"]`
    and no check line, confirm the guard names it, remove it. Without this the enforcement meta-test's
    R1/R6/R8 pass while the invariant enforces nothing.
  - `run-guards.ps1 -Tier ci` runs it; the registry meta-test is green (R1 script exists **and every
    `scripts/guard-*.ps1` on disk is catalogued** — so the script and its catalog entry must land in one
    commit; R6 xor, R8 the catalogued guard is named by an invariant — so the catalog entry and the
    first row land together).
  - `guard-verification-boundaries.py` green with the new row (it checks pattern shape and owner-pattern
    uniqueness, not path existence; the row carries no `verificationId`, so its trait check does not
    apply — plan D3 rule 4).
  - In CI the guards step runs after the seedsmith install step. *If the CI-owning lane — or
    **`ip-censor` T1/T11**, which add their own steps to this file (plan §6, audit 2026-09-20) — has it
    dirty:* skip the whole task (clean-or-skip, plan §8) rather than land a catalog entry that is red in
    CI; record the skip. Whichever of NS6b and ip-censor T1/T11 lands second re-reads the step order and
    re-asserts that the seedsmith install precedes both the guards step and ip-censor's scan step.
  *Verify:* `.\scripts\guard-narrative-seed.ps1`; planted-failure run (temporarily break one assertion,
  confirm the guard names the row, restore); the uncovered-row falsifier above;
  `.\scripts\run-guards.ps1 -Tier ci`; `python gk-core/scripts/guard-verification-boundaries.py`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json,.github/workflows/ci.yml,gk-core/scripts/verification-boundaries.v1.json,scripts/guard-narrative-seed.ps1 -Session <sid>`.
  *Commit:* `narrative-seed NS6b: one catalogued guard for this program's invariants`. Status: **skipped under this row's own clean-or-skip rule, and recorded** — the CI-owning check is dirty and stays dirty for this lane. Re-measured 2026-09-23 (lane `ns-2`), because the citations have drifted twice: `Boundary guards` is `.github/workflows/ci.yml:372` and `Install seedsmith from the lockfile` is `:434` (this row says `:241`/`:295`; the 2026-09-23 predecessor note says `:346`/`:408` — both stale, the ORDER is unchanged), and the file states the constraint in its own comment at `:454`: *"pytest is installed by the seedsmith lockfile step above; this step must stay after it."* Landing a pytest-based guard before that install would be red for every lane, which is exactly what the rule refuses. `gk-core/scripts/guard-narrative.py` is no precedent — it runs `dotnet test` with a `Guard=narrative` trait filter, so it needs no pip install. The re-read stays owed to whichever of NS6b and `ip-censor` T1/T11 lands second.

### `script-check` (spec: `spec-script-check.md`)

- [x] **NS7 Per-character script classifier and target-script policy.** *Depends:* NS0.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/workflow/validators/scripts.py` (new), `language.py`,
  `registry.py` (TIER row), `__init__.py`, `gk-forge/tools/seedsmith/tests/workflow/validators/test_scripts.py` (new).
  *Accept:* one pinned code point per `ScriptClass`; NFC normalisation (`decomposed_accent_is_normalised`);
  `latin` rejects each foreign class and accepts typographic English; an undeclared string leaf is a
  defect; `language_consistency`'s existing tests unchanged and it now catches kana and Extension A;
  `ScriptClass` and `Policy` members pinned as declarations; tier 2.
  *Verify:* `SS workflow/validators/test_scripts.py` and `SS workflow/validators/test_language.py`.
  *Commit:* `narrative-seed NS7: script-property check with a declared policy per field`. Status: done —
  `scripts.py` (11 `ScriptClass` members, 3 `Policy` members, `script_of`, `is_cjk_side`, `script_policy`)
  + `registry.py` TIER row + `__init__.py` export; `language.py`'s `language_consistency` now detects the
  CJK side per character (kana, Hangul, Extension A/B, compatibility ideographs, ideographic punctuation,
  fullwidth letters) behind the same signature; 18 new tests + `test_language.py` unchanged, 23 passed;
  the path-owned run resolves all five changed files to `seedsmith-narrative-validators`/`seedsmith-tests`

### `gloss-registry` (spec: `spec-gloss-registry.md`)

- [x] **NS8 Gloss registry contract and refusing lookup.** *Depends:* NS0.
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_registry/motif-glosses.en.v1.json` (new, header and empty `glosses`),
  `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new, block `gloss` with `maxWords` only),
  `gk-forge/tools/seedsmith/seedsmith/briefkit/gloss.py` (new), `briefkit/__init__.py`,
  `gk-forge/tools/seedsmith/tests/test_briefkit_gloss.py` (new).
  *Accept:* the lookup never returns a motif; `GlossMissing` lists every missing motif and subclasses
  `BriefRefusal`; the loader refuses unknown/missing keys, locale mismatch, digit, foreign script, empty,
  over-`maxWords`, and a row without `model`/`promptVersion`; `sense` members pinned; the committed file
  loads (its row count printed, never asserted).
  *Verify:* `SS test_briefkit_gloss.py`. *Commit:* `narrative-seed NS8: motif gloss registry and refusing lookup`. Status: done —
  `briefkit/gloss.py` (Sense/SENSE closed enum, `GlossRow`, `GlossTable` with refusing `gloss`/`gloss_all`/`missing`,
  `GlossMissing(BriefRefusal)` listing every unglossed motif, `load_glosses` with all nine refusals,
  `coverage_report`), the committed `_registry/motif-glosses.en.v1.json` (header + empty `glosses`; reading:
  rows=0 unglossed=1586 orphans=0, source version current) and `_plan/budget.v1.json` (`gloss.maxWords` 4);
  18 tests; the two new narrative data paths got their own boundary rows (`seed-narrative-registry`,
  `seed-narrative-plan`) because an unmapped production path is a boundary defect (plan D3 rule 4)

### `dungeon-generator-repair` code (spec: `spec-dungeon-generator-repair.md`; built against a fixture gloss table)

- [ ] **NS9 Glossed motifs in the event brief.** *Depends:* NS7, NS8, NS6b (the guard script).  *Files:* `adapters/dungeon/pipelines.py` (gloss step in `run_event_draws`), `adapters/dungeon/briefs.py`
  (`build_event_brief` wording), `workflow/validators/motif.py` (script-aware matching),
  `gk-forge/tools/seedsmith/tests/workflow/validators/test_motif.py` (new), `test_dungeon_event_briefs.py`,
  `test_dungeon_event_pipelines.py`, `gk-core/scripts/enforcement-registry.v1.json` (`narrative-no-raw-motif-in-brief`,
  `guards: ["narrative-seed"]`), `scripts/guard-narrative-seed.ps1` (its check line).
  *Accept:* `brief_contains_glosses_not_raw_motifs`; `unglossed_motif_makes_slot_unresolved_without_a_call`;
  `shared_gloss_is_dropped_from_anti_motifs`; `motif_match_is_word_bounded_for_latin` and
  `motif_match_unchanged_for_chinese`; the guard's check line runs both tests (plan D4, §5 item 5).
  *Verify:* `SS workflow/validators/test_motif.py`, `SS test_dungeon_event_briefs.py`,
  `SS test_dungeon_event_pipelines.py`; `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS9: Delve event briefs carry glosses, never raw motifs`. Status: blocked 8f12bd519 + 297541913 —
  **every acceptance line but the guard's landed**: (1) script-aware matching in `workflow/validators/motif.py`
  (word-bounded + case-insensitive for `latin`/`digit`/`common` motifs, substring unchanged otherwise);
  (2) the gloss step in `run_event_draws` — `glossed_motif_words` resolves both lists through
  `GlossTable`, records dropped anti-motifs on the draw result, and an unglossed motif makes the slot
  `unresolved` with reason `gloss_missing: <motifs>` and **zero** model calls; (3) anti-motifs minus motifs
  by shared gloss (the slot's own assignment wins); (4) `build_event_brief` now names "motif words" in the
  target language and receives the glossed lists. Tests: `brief_contains_glosses_not_raw_motifs`,
  `unglossed_motif_makes_slot_unresolved_without_a_call`, `shared_gloss_is_dropped_from_anti_motifs`,
  `motif_match_is_word_bounded_for_latin`, `motif_match_unchanged_for_chinese` — 31 passed in the two event
  files, 305 in the whole `seedsmith-dungeon` boundary. The one line left, *"the guard's check line runs
  both tests"*, is **blocked on NS6b**: `narrative-no-raw-motif-in-brief` needs a
  `scripts/guard-narrative-seed.ps1` check line, that script cannot land without its catalog entry, and the
  entry would be red in CI until the seedsmith-install step moves above the guards step
  (`.github/workflows/ci.yml`, outside the fence).

- [x] **NS10 Script check in the retry loop and the prompt version.** *Depends:* NS9.
  *Files:* `adapters/dungeon/pipelines.py`, `adapters/dungeon/briefs.py` (`EVENT_SCRIPT_POLICY`,
  `EVENT_PROMPT_VERSION = "dungeon-event/1"`), `test_dungeon_event_pipelines.py`, `test_dungeon_event_briefs.py`.
  *Accept:* `script_defect_triggers_named_quality_retry`; `script_defect_exhausts_to_unresolved` within
  `MAX_QUALITY_RETRY`; `undeclared_string_field_is_a_defect`; `prompt_version_moves_with_prompt_text`
  (a pinned hash of the code-owned prompt, a declaration); `EventDrawResult` carries `brief_hash`.
  *Verify:* `SS test_dungeon_event_pipelines.py`, `SS test_dungeon_event_briefs.py`.
  *Commit:* `narrative-seed NS10: script check in the event retry loop; versioned event prompt`. Status: done —
  `EVENT_SCRIPT_POLICY` (16 dotted paths: `latin` for `name`/`flavor`/`reason`, `none` for every
  non-prose leaf), `EVENT_PROMPT_VERSION = "dungeon-event/1"`, `event_prompt_fingerprint` (sha256 over the
  system prompt + rendered brief + rendered schema + the policy map, pinned at
  `7449b535…6f78` for the fixture cell and proven to track the text by patching two of the four sources),
  the script check joined to the bounded `MAX_QUALITY_RETRY` loop, and `EventDrawResult.brief_hash`
  (`pipeline.staleness.brief_hash` of the rendered brief, `""` for a slot refused before any brief).
  Tests: `script_defect_triggers_named_quality_retry` (the retry prompt names `'flavor'` and `han`),
  `script_defect_exhausts_to_unresolved`, `undeclared_string_field_is_a_defect`,
  `prompt_version_moves_with_prompt_text`, `the_script_policy_is_the_closed_table` — 39 passed in the two
  event files, 313 in the `seedsmith-dungeon` boundary, ruff clean (the two `briefs.py` findings predate
  this change)

- [x] **NS11 Planned climate; no forged chain ids.** *Depends:* NS10.
  *Files:* `adapters/dungeon/schema.py` (`climateAffinity` PLANNED, const), `adapters/dungeon/planner.py`
  (`assign_event_climates`), `adapters/dungeon/briefs.py` (per-cell const), `adapters/dungeon/pipelines.py`
  (forge deleted; `story` cell refused unless a committed `chainRef` is supplied as PLANNED const),
  `test_dungeon_planner.py`, `test_dungeon_contract.py`.
  *Accept:* `climate_is_planned_const` (audit clean); `climate_rotation_covers_all_seven_per_kind`
  (deterministic); `story_cell_is_refused` with no call; `no_forged_chain_ref`; a supplied committed
  `chainRef` passes through byte-identical.
  *Verify:* `SS test_dungeon_planner.py`, `SS test_dungeon_contract.py`, `SS test_dungeon_event_pipelines.py`.
  *Commit:* `narrative-seed NS11: Delve event climate is planned; chain ids are never forged`. Status: done 6398757fd —
  `EVENT_OWNERSHIP["climateAffinity"]` AUTHORED → PLANNED, the generic schema pins it `const`
  (`_enum(..., nullable=True, const=True)`) and the per-cell schema pins the planner's value;
  `planner.assign_event_climates` (seven climates in rotation, per kind, sorted ids, deterministic) with
  `event_kind_of` matching the closed kind vocabulary by LONGEST prefix (so `encounter-event` is not read
  as `encounter`); the legacy chain forge is **deleted** and `run_event_draws` now raises `ValueError`
  naming the cell for a `story` cell with no committed `chainRef`, accepting one (`committed_chain_refs`)
  and pinning it byte-identical when supplied. Tests: `climate_is_planned_const` (`run_audit("dungeon-event")`
  clean), `climate_rotation_covers_all_seven_per_kind` (7 slots → all seven, identical across calls),
  `story_cell_is_refused` (no call), `no_forged_chain_ref`, `a_committed_chain_ref_passes_through_byte_identical`
  — 105 passed in the four named files, 323 in the `seedsmith-dungeon` boundary. **Side effect, by the NS10
  contract:** pinning the climate changed `build_event_schema_for_cell`, so the pinned digest moved and
  `EVENT_PROMPT_VERSION` was bumped `dungeon-event/1` → `dungeon-event/2` (the mechanism's first real
  exercise). ⚠️ NS12's spec text *"promptVersion is `dungeon-event/1`"* is therefore stale: its test must
  assert the current `EVENT_PROMPT_VERSION` constant, not the literal.

- [x] **NS12 Committer with provenance and text keys.** *Depends:* NS11, NS6.
  *Files:* `adapters/dungeon/commit.py` (new, `commit_event_draws`), `adapters/dungeon/schema.py`
  (`nameKey`/`flavorKey` DERIVED rows), `gk-forge/tools/seedsmith/tests/test_dungeon_commit.py` (new),
  `test_dungeon_idempotency.py`.
  *Accept:* `commit_stamps_provenance_from_resolved_config`; `commit_is_byte_identical_on_rerun`;
  `commit_writes_name_and_flavor_keys` (key rule `ns.event.<id body>.<field>.<h8>`, `^[a-z0-9.-]+$`; a
  changed string is a new key); `keys_are_not_model_facing`.
  *Verify:* `SS test_dungeon_commit.py`, `SS test_dungeon_idempotency.py`.
  *Commit:* `narrative-seed NS12: Delve event committer with provenance and text keys`. Status: done —
  new `adapters/dungeon/commit.py` (`text_key` — `ns.event.<eventId body>.<field>.<h8>`, h8 = the first
  eight hex digits of the string's SHA-256, checked against `^[a-z0-9.-]+$`; `commit_event_draws(results,
  out_dir, *, config)` stamping `nameKey`/`flavorKey` plus `_provenance` from the RESOLVED config via
  `emit.build_provenance`, writing through `emit.write_corpus`; a run that resolved nothing writes
  nothing at all, not even an empty index), `schema.DERIVED_FIELDS_BY_KIND` (the keys are DERIVED at
  commit and deliberately absent from `EVENT_OWNERSHIP`, whose no-stray-entry test constrains it to the
  KindSpec's real fields), and `EVENT_SCHEMA_VERSION = "dungeon-event/1"` for the entry shape.
  Tests: `commit_stamps_provenance_from_resolved_config` (`modelId` = the passed model, `promptVersion` =
  the current `EVENT_PROMPT_VERSION`, `stalenessKey` present), `commit_writes_name_and_flavor_keys`
  (charset, the exact key rule, a changed string → a new key), `keys_are_not_model_facing` (absent from
  both the generic and the per-cell call schema), `unresolved_draws_write_nothing`, and
  `commit_is_byte_identical_on_rerun` in `test_dungeon_idempotency.py` (file lists equal, concatenated
  SHA-256 equal) — 22 passed in the two named files, 329 in the `seedsmith-dungeon` boundary; ruff clean

- [x] **NS13 Legacy regeneration driver.** *Depends:* NS12.
  *Files:* `adapters/dungeon/regen.py` (new), `gk-forge/tools/seedsmith/seedsmith/report/cli.py`
  (`dungeon events regen` with `--dry-run` default, `--write`, `--review`, `--commit`, `--ids`),
  `gk-data/packs/fusion/data/seed/dungeon/_plan/budget.v2.json` (new: v1 plus `event.regenReviewSample`), `test_dungeon_commit.py`.
  *Accept:* `regen_reuses_committed_ids` (no room `eventPool` reference dangles);
  `regen_regenerates_story_events_keeping_chain`; `regen_dry_run_makes_no_call` and prints base and worst
  calls; `regen_unresolved_keeps_committed_file`; `regen_commits_only_accepted_after_review`;
  `regen_uses_resolved_config`; `existing_names` excludes the batch being regenerated.
  *Verify:* `SS test_dungeon_commit.py`, `SS test_dungeon_idempotency.py`.
  *Commit:* `narrative-seed NS13: legacy Delve event regeneration driver`. Status: done 2026-09-23 — the **read-only
  planning half** landed: `adapters/dungeon/regen.py` (`load_committed_events`, `plan_legacy_regen(events_dir,
  ids=…)` → the batch's kind × theme cells, the COMMITTED ids reused per cell, the committed story
  `chainRef`s carried over, `existing_names` holding every event OUTSIDE the batch, and `base`/`worst` call
  counts at 1 and `1 + MAX_QUALITY_RETRY` per event; `render_plan` formats that reading), `gk-data/packs/fusion/data/seed/dungeon/
  _plan/budget.v2.json` (v1's rows verbatim plus `event.regenReviewSample: 6`), and the new
  `seed-dungeon-plan` boundary row so `gk-data/packs/fusion/data/seed/dungeon/_plan/**` resolves FOCUSED instead of falling to
  the whole seedsmith module run. Tests in `test_dungeon_commit.py`: `regen_reuses_committed_ids_and_no_room_
  pool_reference_dangles`, `regen_regenerates_story_events_keeping_chain`, `regen_dry_run_makes_no_call_and_
  reports_both_bounds` (with `call_model` patched to raise), `existing_names_excludes_the_batch_being_
  regenerated`, `an_id_that_is_not_committed_is_refused`, `the_committed_budget_publishes_the_review_sample`
  — 28 passed in the two named files, 335 in the dungeon suite, `guard-verification-boundaries.py` OK.
  **Draw/review/commit half landed** (`RegenRun`, `run_legacy_regen`, `write_run`, `record_verdict`,
  `commit_reviewed`, `review_sample`): a real run draws every committed event under its own id with the
  RESOLVED config, the committed chainRefs and the planner's climates; an unresolved slot and a
  rejected event keep their committed bytes; only `accept`ed events are written, and a rejection must
  name its reason. Tests: `a_run_uses_the_resolved_config_and_commits_only_accepted_events`,
  `the_committed_story_chain_ref_reaches_the_schema`, `a_reject_requires_a_reason`,
  `the_review_sample_is_seeded_and_stratified`, `a_dry_run_object_holds_no_events` — 33 passed in the two
  named files, 340 in the dungeon suite. **Remaining** (the rest of this row, and the reason it is not
  closed): the `--write`/`--review`/`--commit` half has **no production caller yet** — the
  `dungeon events regen` verb must be added to the shared `report/cli.py`, which currently has NO
  `dungeon` subcommand tree at all (only `--adapter dungeon` for `check`/`report`), so this is a new
  parser tree rather than a one-line addition; `ip-censor` T16's clean-or-skip rule applies to that file.
  The earlier plan-half notes follow: the draw half — `--write` running `run_event_draws` with the resolved
  config and the plan's cells/ids/chainRefs against a scratch run file (`regen_uses_resolved_config`,
  `regen_unresolved_keeps_committed_file`), the seeded stratified review sample + append-only verdicts with a
  rejected event regenerated under its reason (`regen_commits_only_accepted_after_review`), and the
  `dungeon events regen --dry-run|--write|--review|--commit|--ids` verb in the shared `report/cli.py` (clean at
  this commit; the plan's clean-or-skip rule for `ip-censor` T16 applies when it is taken).
  **Live reading over the committed tree, re-run and read** (corrects the figure first written into the
  commit body): **54 events in 44 cells, 54 base / 162 worst calls, 4 committed chainRefs carried over,
  0 existing names** — the commit body says 42 cells; this line is the corrected number.
  **Closed by lane `ns-2`:** the missing production host landed — a `dungeon events regen` tree in
  `gk-forge/tools/seedsmith/seedsmith/report/cli.py` (`--dry-run` default, `--write`, `--review`, `--commit`, `--ids`,
  plus `--accept`/`--reject` because `--commit` reads only verdicts and would otherwise never write anything),
  with `load_run`/`latest_run_id` in `regen.py` so review and commit read the run a `--write` wrote. Three new
  `DungeonRegenCliTests` enter through `main([...])` and prove the whole loop: the plan prints 4 base / 16 worst
  calls and spends nothing, `--write` draws with the RESOLVED config and leaves every committed event's bytes
  untouched, `--review` prints the seeded strata `[bargain, story]`, `--accept`/`--reject` record verdicts, and
  `--commit` writes `_index.json` + the accepted event only, stamping `_provenance.modelId`. A commit with no
  accepted event refuses (exit 3) rather than rewriting the index. `SS test_dungeon_commit.py` → 24 passed;
  both named files → 41 passed; the `seedsmith-dungeon` boundary (which was MISSING `test_dungeon_commit.py` and
  now selects it) → 348 passed. `verify-change.ps1` on `report/cli.py` exits 1 because that path maps to
  `seedsmith-fallback` (the whole suite) and 16 tests are red — all pre-existing and proven independent of this
  change (11 reproduce with `cli.py` reverted to HEAD: `11 failed, 1 passed`; causes read in the fragment).
  Evidence: `tasks/evidence-fragments/narrative-seed-NS13.md`.

### `gloss-fill` code (spec: `spec-gloss-fill.md`)

- [x] **NS14 Gloss pipeline: chunking, verify, heal, no-source fallback.** *Depends:* NS6, NS7, NS8.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/__init__.py` (new, package marker),
  `adapters/narrative/gloss/{__init__,prompt,fill}.py` (new), `gk-data/packs/fusion/data/seed/narrative/_exemplars/gloss.en.v1.json`
  (new, authored pairs), `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (block `gloss`: `chunkSize`,
  `exemplarCount`, `temperaturePermille`, `reviewSample`), `gk-forge/tools/seedsmith/tests/test_narrative_gloss_fill.py` (new).
  *Accept:* chunk schema has root `blocked`, `maxLength`, `additionalProperties: false`, every key
  required, a negative clause per field; `sense` permuted per motif (`order_for`), vote set empty and
  justified; `max_heal=2` passed explicitly with a comment; `exhausted_heal_never_writes_the_source`;
  `two_repairs_then_unresolved`; `already_glossed_motifs_are_not_sent`; `dry_run_makes_no_call`; a
  `--limit <chunks>` option bounds a run.
  *Verify:* `SS test_narrative_gloss_fill.py`. *Commit:* `narrative-seed NS14: motif gloss pipeline`. Status: done —
  `adapters/narrative/gloss/{prompt,fill}.py` (closed chunk schema with `blocked` required, `maxLength`,
  `additionalProperties: false` and a negative clause on every field; `order_for`-permuted sense options
  per motif; one call per chunk with `max_heal=MAX_HEAL=2` passed explicitly; an exhausted heal leaves the
  motif UNRESOLVED, never substituting the source text; a `blocked` reply ends the chunk without a retry;
  `already_glossed` motifs are not sent; `limit` bounds the chunks; a justified-empty `votes` key),
  `gk-data/packs/fusion/data/seed/narrative/_exemplars/gloss.en.v1.json` (8 authored pairs) and the budget's `gloss` block
  (chunkSize 20, exemplarCount 8, temperaturePermille 200, reviewSample 60). 13 new tests (printed
  reading: exemplar pairs=8 chunkSize=20 reviewSample=60); the path-owned run resolved every changed path
  focused and ran 31 passed, Guard.Tests 57 passed, guard OK

- [x] **NS15 Gloss commit, preflight and CLI verbs.** *Depends:* NS14.
  *Files:* `adapters/narrative/gloss/commit.py` (new), `adapters/narrative/preflight.py` (new),
  `report/cli.py` (`narrative gloss fill|commit`, `narrative preflight`), `test_narrative_gloss_fill.py`.
  *Accept:* `commit_writes_only_accepted_rows` and refuses while a rejection has no accepted replacement;
  `commit_is_byte_identical_on_rerun`; `rejected_gloss_regenerates_with_reason`;
  `review_sample_is_seeded_and_stratified` (core `stratified_sample`); `transient_replay_makes_no_new_call`;
  preflight makes exactly one call and fails loudly on a non-conforming reply (tested with a stub).
  *Verify:* `SS test_narrative_gloss_fill.py`. *Commit:* `narrative-seed NS15: gloss commit, preflight and CLI`. Status: done 2026-09-23 —
  `gloss/commit.py` (`commit_glosses` writing only the rows it is given, refusing while a rejected motif has
  no accepted replacement, each row stamped with the resolved model and the prompt version, byte-identical
  bytes on a rerun because there is no timestamp; `regeneration_requests` carrying the LATEST rejection reason
  for the motif a rerun must regenerate; `review_sample` stratified by sense and seeded from the run id) and
  `adapters/narrative/preflight.py` (ONE call, failing loudly — `BriefRefusal` — on a dead endpoint, an
  unparseable body, a `blocked` reply, a missing entry, an identity gloss or a digit; each failing case still
  spends exactly one call) are landed with 7 new tests in `test_narrative_gloss_commit.py`. **Remaining**: the
  `narrative gloss fill|commit` and `narrative preflight` verbs, which need a NEW `narrative` subcommand tree in
  the shared `report/cli.py` (no `narrative` verb exists today — the same shape as NS13's missing `dungeon`
  tree), so no production host reaches the commit or the preflight yet; `ip-censor` T16's clean-or-skip rule
  applies to that file.
  **Correction 2026-09-23 (lane `ns-2`): the box was ticked while this row's own Status line and the ledger
  both say `blocked`; unticked — a tick whose evidence does not match is the failure mode the repo warns
  about (NS21's 2026-09-23 correction is the precedent).** The reason is unchanged and is the only thing
  left: `report/cli.py` has no `narrative` subcommand tree, so no production host reaches `commit.py` or
  `preflight.py`, and "a mechanism no production host reaches is NOT done".
  **Closed by lane `ns-2`:** the production host landed — a `narrative` subcommand tree in
  `gk-forge/tools/seedsmith/seedsmith/report/cli.py`: `narrative gloss fill` (`--dry-run` default: chunks + calls,
  no call; `--write`: the resolved config, a scratch run file, the registry untouched; `--limit`,
  `--regenerate`), `narrative gloss commit` (`--run`, `--accept`, `--reject`, `--registry`) and
  `narrative preflight` (ONE call). `GLOSS_PROMPT_VERSION = "gloss/1"` moved beside the prompt text it
  versions, and `fill.py` gained `gloss_run_id`/`write_gloss_run`/`load_gloss_run`/`latest_gloss_run_id` so
  commit reads the run a fill wrote. Six new `NarrativeCliTests` enter through `main([...])`; the file is 13
  passed in 0.29s and the seven narrative files are 136 passed. `test_cli.py` is 23 passed / 1 failed (the
  pre-existing `atom.fx-overlay-damage` GAP). **`verify-change.ps1`'s whole-suite stage is NOT RUN:**
  `report/cli.py` maps to `seedsmith-fallback` (4585 tests, ~14 min) and it was killed by an infrastructure
  error twice, at 71% and 97%; the focused boundaries are green and the whole-suite failures are the
  pre-existing set proved independent in `a5c849802`. Evidence:
  `tasks/evidence-fragments/narrative-seed-NS15.md`.

### Wave-0 runs

**Status (2026-09-23, updated by lane `ns-2`): the VERB blocker is gone for all four; what remains is the owner's spend go.** Both missing subcommand trees landed — `narrative gloss fill|preflight|commit` (NS15's closure) and `dungeon events regen` (`a5c849802`, NS13's) — so NS16/NS17/NS18/NS19 can now be run end to end from the CLI. What still blocks them is (b): each is a real model spend, the gates NSG1 (commit regenerated legacy events) and NSG4 (scale past a first batch) are the owner's to give, and the owner charter for this lane names no model budget. NS16 is the one row whose only remaining dependency is that go.

- [ ] **NS16 [model] Gloss batch 1.** *Depends:* NS15.
  *Budget:* `calls = ceil(M/chunkSize)`, worst ×3 (README §9); batch 1 is `--limit 3`: 3 base / 9 worst,
  plus 1 preflight call.
  *Steps:* `narrative gloss fill --dry-run` (record the printed figure for the whole list) →
  `narrative preflight` → `narrative gloss fill --write --limit 3` → review **every** row of the batch
  (accept/reject, append-only) → regenerate rejections with the reason → `narrative gloss commit --run <runId>`.
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_registry/motif-glosses.en.v1.json`, `data/seed/narrative/_runs/gloss-<runId>.json`.
  *Accept:* every committed row is script-clean, digit-free, within `maxWords`, carries the resolved
  model and prompt version; no raw motif stored; unresolved motifs listed in the run file. Readings
  printed: rows, unresolved, soft defects.
  *Verify:* `SS test_briefkit_gloss.py` (`committed_file_loads`). *Commit:* `narrative-seed NS16: first gloss batch`. Status: blocked — the verbs now exist (NS15 closed 2026-09-23: `narrative gloss fill --dry-run|--write`, `narrative preflight`, `narrative gloss commit`, all reached through `main([...])`), so the ONLY thing left is the owner's go for a real model spend; the charter for this lane names no model budget.
  **The printed figure this row asks for, read 2026-09-23 through the verb (no call, nothing written):**
  `narrative gloss fill --dry-run` → `{chunks: 80, calls: 0, toGloss: 1586, alreadyGlossed: 0, chunkSize: 20}`,
  so the whole list is **80 base / 240 worst** calls; `--dry-run --limit 3` → `chunks: 3`, so batch 1 is
  **3 base / 9 worst plus 1 preflight**. NS17's row estimated 80 for the whole list, now confirmed against the corpus.

- [ ] **NS17 [model] Gloss full pass.** *Depends:* NS16, **NSG4** (owner go after batch 1).
  *Budget:* the dry run's figure for the remaining motifs (illustration: 1,586 motifs at 20 per chunk is 80
  base calls in total, so about 77 base / 231 worst after batch 1).
  *Steps:* dry run → preflight → `--write` → review `gloss.reviewSample` rows stratified by `sense` → commit.
  *Accept:* as NS16; the coverage report lists motifs still unglossed (a reading).
  *Verify:* `SS test_briefkit_gloss.py`. *Commit:* `narrative-seed NS17: full motif gloss pass`. Status: blocked — verbs exist (NS15 closed); needs NS16 committed and the owner's **NSG4** go.

- [ ] **NS18 [model] Legacy regeneration batch 1.** *Depends:* NS13, NS17. Commit step behind **NSG1**.
  *Agent:* **implementer-hard** (plan D6b — the commit overwrites a committed generated tree other
  programs and players read).
  *Budget:* base 1 call per event, worst 3 (1 + `MAX_QUALITY_RETRY`); batch 1 is one event per kind
  (`--ids`, six events, one `story` included): 6 base / 18 worst, plus 1 preflight call.
  *Steps:* `dungeon events regen --dry-run` (record the whole-tree figure) → `narrative preflight` →
  `--write --ids <six>` → `--review` (every event of the batch) → regenerate rejections with the reason →
  on NSG1, `--commit`.
  *Files:* `gk-data/packs/fusion/data/seed/dungeon/events/<six files>`, `data/seed/dungeon/_runs/<runId>.json`.
  *Accept:* each committed event keeps its `eventId`, passes the `latin` policy on `name` and `flavor`,
  carries `nameKey`/`flavorKey` and `_provenance`; the `story` event keeps its committed `chainRef`.
  *Verify:* `SS test_dungeon_commit.py`, `SS test_dungeon_contract.py`.
  *NSG1 default:* the run stays uncommitted in `_runs/`; status `awaiting NSG1`.
  *Commit:* `narrative-seed NS18: first regenerated legacy Delve events`. Status: open

- [ ] **NS19 [model] Legacy regeneration, remaining events.** *Depends:* NS18 committed, **NSG4**.
  *Agent:* **implementer-hard** (plan D6b — it rewrites the whole committed event tree in one run).
  *Budget:* the dry run's figure (illustration: 54 events measured 2026-09-19, so 48 base / 144 worst after
  batch 1).
  *Files:* `gk-data/packs/fusion/data/seed/dungeon/events/**` (one generator run, one commit — plan D2 exception),
  `data/seed/dungeon/_runs/<runId>.json`, `test_dungeon_commit.py` (tree test
  `committed_legacy_events_carry_keys`: every file under the events tree has both keys matching the key
  rule and a `_provenance` block — a contract over every file, no count), `gk-core/scripts/enforcement-registry.v1.json`
  (`legacy-delve-event-keyed-text`, `guards: ["narrative-seed"]`), `scripts/guard-narrative-seed.ps1`
  (its check line).
  *Accept:* tree test green; an `unresolved` event keeps its committed bytes and is listed; readings
  printed (share still leaking a foreign script, expected zero; the four `story` events' dangling
  `chainRef`s listed for `npc-story-events`' known-defect list).
  *Verify:* `SS test_dungeon_commit.py`, `SS test_dungeon_contract.py`; `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS19: all legacy Delve events regenerated clean and keyed`. Status: open

### Checkpoint 0 — Wave 0

- [ ] Whole seedsmith suite green with the transport stubbed to raise.
- [ ] `seedsmith-no-model-literal`, `narrative-no-raw-motif-in-brief`, `legacy-delve-event-keyed-text` in
      the registry, each with `guards: ["narrative-seed"]`; `scripts/guard-narrative-seed.ps1`,
      `run-guards.ps1 -Tier ci` and the registry meta-test green.
- [ ] Hand-off recorded for `npc-story-events` `delve-live-rooms`: the keyed legacy tree exists (or NS18
      awaits NSG1 — then say so).
- [ ] Owner reviews the Wave-0 readings before Phase 2 is declared done (Phase 2 may already be running).

---

## Phase 2 — Wave 1: registries (no model)

### `storylet-vocab` (spec: `spec-storylet-vocab.md`)

- [x] **NS20 Host kinds, choice kinds, choice patterns and the reader.** *Depends:* NS8 (tree exists).
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_registry/{host-kinds,choice-kinds,choice-patterns}.v1.json` (new),
  `adapters/narrative/storylet_vocab.py` (new), `gk-forge/tools/seedsmith/tests/test_narrative_storylet_vocab.py` (new).
  *Accept:* every value has `description` and `negative`; `host_kinds_join_room_kinds`;
  `world_rows_read_sector_climate` (R20: `climateSource: sector`, all seven climates; no sector-climate
  registry file); `patterns_obey_the_shape_rules`; `every_choice_kind_and_storylet_kind_is_covered_by_a_pattern`;
  member lists pinned as declarations; `unknown_key_is_refused`.
  *Verify:* `SS test_narrative_storylet_vocab.py`. *Commit:* `narrative-seed NS20: host kinds, choice kinds and patterns`. Status: done —
  the three registries (16 host rows, 8 choice kinds, 13 patterns) each carry `description` + `negative`, and
  `adapters/narrative/storylet_vocab.py` reads them and validates the contract: the Delve rows join the real
  room-kind registry with `climateNeutral` equal to that row's own flag, world rows read `climateSource: sector`
  with all seven climates (R20, the sector-type registry retired), every other row carries no climates of its
  own, and the §3.3 pattern rules each get an assertion (2-4 slots, positions in vote order, no kind twice,
  outcomes 1-3, exactly one `leave` with one outcome, exactly two unconditioned slots, at most two intrinsic,
  every choice kind used and every storylet kind fitted). 10 tests; the registry subtree's owner row
  (`seed-narrative-registry`) now selects this test alongside the gloss one.

- [x] **NS21 Conditions, consequence kinds, role tags.** *Depends:* NS20.
  *Files:* `_registry/{conditions,consequence-kinds,role-tags}.v1.json` (new), `storylet_vocab.py`, the test.
  *Accept:* `leaves_are_built_or_proposed_never_both` (parses `LeafId` from `PredicateNode.cs`);
  `condition_usable_in_closes`; `consequence_ref_and_param_rules_close` (the `{kind, ref, param}` rules;
  `relation.shift` params equal the relation fact kinds); `consequence_kinds_cover_the_legacy_four`;
  `role_kinds_admit_none`; `requires_is_one_string_shape`; `arg_families_close`.
  *Verify:* `SS test_narrative_storylet_vocab.py`. *Commit:* `narrative-seed NS21: conditions, consequences and role tags`. Status: partial —
  the three registries are authored: `conditions.v1.json` (8 rows: none, danger-band-is, disposition-is,
  character-state-is, story-flag-set, lead-level-at-least, doctrine-studying, role-cast, each with
  `argFamily`/`usableIn`/`compilesTo`, plus a `proposedLeaves` block naming RelationBandAtMost,
  CharacterStateIs, StoryFlagSet, LeadLevelAtLeast, DoctrineStudying and PartyCarriesTag),
  `consequence-kinds.v1.json` (11 rows: the legacy four plus quest.offer, relation.shift, story.flag,
  recruit, scene.play, battle.start, doctrine.setback, with `refForms`/`params`/`routesTo`) and
  `role-tags.v1.json` (the four role kinds, the four `requireFamilies`, `requirementShape`).
  **Remaining** (the rest of this row, in order): the reader half in `adapters/narrative/storylet_vocab.py`
  — `load_conditions`/`load_consequence_kinds`/`load_role_tags`, `built_leaves()` parsing the real
  `LeafId` enum from `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs` (16 members measured;
  BandIs and HoldsStock are the only condition/gate leaves already built), `validate_conditions`
  (built XOR proposed, never both, and `role requirement` is neither), `validate_consequence_kinds`
  (`refForms` non-empty exactly where `ref` is required; `relation.shift` params == the five relation
  fact kinds), `validate_role_tags`, `requirement_defects` (one `<family>:<value>` shape) and the
  `all_defects()` composition — plus the seven acceptance tests in `test_narrative_storylet_vocab.py`.
  **Reader half landed**: `load_conditions`/`load_consequence_kinds`/`load_role_tags`/`proposed_leaves`,
  `built_leaves()` parsing the runtime's real `LeafId` (16 members, measured), `validate_conditions`
  (built XOR proposed, never both; a `role requirement` and the `none` condition are neither),
  `validate_consequence_kinds` (`refForms` non-empty exactly where `ref` is required, each form
  `<prefix>:<id>`; `relation.shift`'s params are the five relation fact kinds),
  `validate_role_tags` (the four role kinds, the four requirement families, the element family == the six
  elements, `valuesFrom: roles.v1.json`), `requirement_defects` (one `<family>:<value>` shape) and the
  `all_defects()` composition, which now reports **0** defects over the committed files. 7 new tests
  (`leaves_are_built_or_proposed_never_both` with a planted both-ways leaf, `condition_usable_in_closes`,
  `arg_families_close`, `consequence_ref_and_param_rules_close`, `consequence_kinds_cover_the_legacy_four`,
  `role_kinds_admit_none`, `requires_is_one_string_shape`); 17 passed in this file, 55 in the four
  narrative files, ruff clean, guard OK, and the path-owned plan resolves all five changed paths focused.

- [x] **NS22 Value notes and the `teaches` registry.** *Depends:* NS21.
  *Files:* `_registry/{value-notes,teaches}.v1.json` (new), `storylet_vocab.py`, the test.
  *Accept:* `value_notes_match_their_sources` (note keys = source members + `none`);
  `model_facing_lists_have_none`; `teaches_close_and_order` (authored `teachingLine` with no digit, loop
  heading exists, no first-session checkpoint mechanic, order pinned as a declaration). The call-schema
  coverage test lands in NS31.
  *Verify:* `SS test_narrative_storylet_vocab.py`. *Commit:* `narrative-seed NS22: value notes and the teaches registry`. Status: done —
  `value-notes.v1.json` (119 rows over 9 borrowed lists: outcomeOrdinal, dropBand, eventKind, atomFamily,
  powerBand, conditionArgFamily, requirementFamily, relationFact, choiceGate — keys `<list>.<value>`, each
  with a note and a negative clause, each list carrying a `none`) and `teaches.v1.json` (10 rows in teaching
  order, each with `loop`, `carriers`, `requires`, an authored digit-free `teachingLine` and a negative
  clause). Readers: `load_value_notes`/`load_teaches`, `value_note_sources()` (members read from the event
  schema and the dungeon registries, not copied), `loop_headings()` (parsed from `docs/guide/the-loops.md`),
  `validate_value_notes` (keys == source members + `none` EXACTLY, every list has `none`) and
  `validate_teaches` (unique ids, `teachingOrder` == file position, every `loop` an actual heading, carriers
  closed, digit-free authored line, no first-session checkpoint mechanic). `all_defects()` now covers all
  eight registries and reports **0** defects. 3 new tests; 20 passed in this file, 58 across the narrative
  files; the path-owned plan resolves `seed-narrative-registry` focused with both narrative tests. **Owed to
  NS31**: its call-schema coverage test must prove every borrowed list a call schema shows has notes — this
  module covers the nine lists whose members have a readable source today; `characterState`, `storyFlag`,
  `levelGate`, `disposition` and `dangerBand` values get their notes when their registries land.

### `character-vocab` (spec: `spec-character-vocab.md`)

- [x] **NS23 Roles, voices, line contexts, required pairs and R13 rules.** *Depends:* NS8.
  *Files:* `_registry/{roles,voices,line-contexts,line-pairs}.v1.json` (new),
  `adapters/narrative/character_vocab.py` (new), `gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py` (new),
  `docs/architecture/decisions.md` (map §11 row 6).
  *Accept:* `roles_match_the_runtime_list` (nine, pinned with reason); `voted_lists_have_none`;
  `bands_are_the_disposition_file`; `every_pair_names_known_context_and_band`;
  `antagonist_pairs_have_no_personal_history`; `joins_is_never_an_antagonist_pair`;
  `leads_block_matches_the_three_lead_tokens`; `required_pairs_is_a_pure_function`.
  *Verify:* `SS test_narrative_character_vocab.py`; `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS23: character registries and counter-doctrine rules`. Status: done 2026-09-23 —
  the four registries and their reader landed (`roles.v1.json` 10 rows pinned to the runtime's nine plus
  `none` with `warlord` the one antagonist; `voices.v1.json` 7; `line-contexts.v1.json` 15 with buckets;
  `line-pairs.v1.json` four allegiance rows whose bands JOIN `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`
  (eager/open/wary/hostile) plus the R11 `leads` declaration; `character_vocab.py` with `required_pairs`
  as a pure function and validators for every acceptance line — `all_defects()` reports 0 over the
  committed files; 11 tests pass). **Blocked on the same denied path as NS6**: the row's Files line also
  names `docs/architecture/decisions.md` (map §11 item 6) for the drafted counter-doctrine row, which is
  outside this run's allowed paths, so that half cannot be committed from this lane.
  **Closed by lane `ns-2`:** that path IS in this lane's allowed paths, so the drafted counter-doctrine row
  (map §11 item 6, `spec-character-vocab.md` §8) landed in `docs/architecture/decisions.md` with the §6.12
  cross-reference and the enforcing registry named; `verify-change.ps1 -Paths docs/architecture/decisions.md
  -AllowUnscoped` → exit 0, doc-citation 0 findings, `guard.doc-boundary` 4 passed; the row's own suite still
  13 passed. Evidence: `tasks/evidence-fragments/narrative-seed-NS23.md`.

- [x] **NS24 Voice exemplars.** *Depends:* NS23. Soft: `ip-censor` T14.
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_exemplars/voices/<register>.en.json` (six, new, authored),
  `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (block `character.exemplarLines`), the test.
  *Accept:* `every_register_has_an_exemplar_that_loads` (line count within budget bounds, Latin, no digit,
  no brace); `exemplar_lines_cite_no_other_franchise` reads `load_avoid_terms` and skips with a printed
  note when the helper or registry is absent (IC-3).
  *Verify:* `SS test_narrative_character_vocab.py`. *Commit:* `narrative-seed NS24: voice exemplars`. Status: done —
  six authored exemplar files (`gk-data/packs/fusion/data/seed/narrative/_exemplars/voices/{formal,blunt,playful,grim,sly,gentle}.en.json`,
  five lines each plus `lexicon.signature`/`lexicon.forbidden`), the budget's new
  `character.exemplarLines` block (`min` 4 / `max` 8 — measured, `exemplar_line_bounds()` returns (4, 8)),
  and the readers `load_voice_exemplar`/`validate_voice_exemplars`/`avoid_terms` in `character_vocab.py`.
  `all_defects()` now also covers the exemplars and reports **0** defects; 13 tests pass. The IC-3 line
  works as designed: `avoid_terms()` returns an empty tuple because ip-censor's `load_avoid_terms` helper
  is not in this tree, and the test prints `skipping the mark check (IC-3)` and returns instead of failing.

### Grammar and names (specs: `spec-token-grammar.md`, `spec-names-registry.md`)

- [x] **NS25 Token grammar, `parse` and `expand`.** *Depends:* NS8.
  *Files:* `_registry/tokens.v1.json` (new), `adapters/narrative/token_grammar.py` (new),
  `gk-forge/tools/seedsmith/tests/test_narrative_token_grammar.py` (new), `docs/architecture/decisions.md` (row 3).
  *Accept:* `parse_accepts_every_form`; `parse_refuses_outside_the_grammar` (each a named refusal);
  `expand_matches_the_table`; `expand_is_idempotent`; `expanded_arguments_are_closed`;
  `apostrophes_survive_expansion`; `literal_text_excludes_tokens`; `slug_for_is_deterministic_and_refuses_collisions`;
  `features_are_closed`; fixtures contain no real name.
  *Verify:* `SS test_narrative_token_grammar.py`; `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS25: story text token grammar`. Status: done 2026-09-23 —
  `token_grammar.py` (`load_grammar` with all nine registry refusals, `parse` with 16 named reasons,
  `expand` per §5's table exactly, `tokens_used`, `literal_text`, `slug_for` with the reserved-suffix and
  collision refusals, `render_for_brief`), the committed `tokens.v1.json` (3 families, 3 leads, 3 forms,
  3 pronouns, 4 slots, 4 tags, 20 rows each carrying both clauses) and the decisions.md row; 37 tests in
  the named file, all eleven spec tests plus `render_for_brief_inlines_descriptions`.
  **The §5 `_bare` boundary (proven, not glossed):** §5 gives `{T_bare}` → `{T}` while `{T}` (running)
  expands to the article `select`, so a bare-only message's output is textually the running short form;
  `expand` is idempotent on already-expanded text (the spec's own wording) and every message carrying an
  article/pronoun form, and the test asserts both the property and that one boundary.
  **`docs/architecture/decisions.md` is inside this lane's allowed paths**, so the row landed here; NS6 and
  NS23, whose only remaining blocker was that same path, are unblocked.
  Evidence: `tasks/evidence-fragments/narrative-seed-NS25.md`; `verify-change.ps1` ran with `-AllowUnscoped`
  because `tasks/sessions/narrative-seed-2.json` does not exist and `tasks/sessions/**` is outside the fence.

- [x] **NS26 Names registry.** *Depends:* NS25. Coordination: `identity-rename` T1 (plan §5 item 9).
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (new, or adopted from identity-rename T1),
  `adapters/narrative/names.py` (new), `gk-forge/tools/seedsmith/tests/test_narrative_names_registry.py` (new),
  `docs/architecture/decisions.md` (names row, only if absent).
  *Accept:* `lead_rows_are_exactly_the_three_leads`; `lead_display_strings_follow_R11` (an owner ruling);
  display refusal fixtures; `english_rows_are_singular`; `union_includes_character_seeds`;
  `normalised_collision_is_refused`; `missing_corpus_is_an_empty_source`; `rename_changes_no_brief_hash`.
  If identity-rename's file exists, adding `registryVersion` keeps its C# parser green.
  *Verify:* `SS test_narrative_names_registry.py`; if the C# parser exists,
  `.\scripts\verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json -Session <sid>` (its
  `core.lead-names` row); `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS26: lead names registry`. Status: done 2026-09-23 —
  `names.py` (`NameRow`/`NameSet`/`NameMissing`, `load_names` with the display, tag, lead-closure,
  character-seed, collision and locale-parity refusals, `normalise_display` per `item/seed-contract.md` §5),
  22 tests, and the decisions.md row; the authored file was **adopted unchanged** from identity-rename T1
  (`c6f51a159`) — it already carries `registryVersion` and its C# parser stayed green (`core-lead-names`
  27 passed). Reading: `committed registry rows=3 authored=3 locale=en registryVersion=1`.
  Two spec details the code does not follow, with the cause read: (a) a character named `The Rot Wright`
  does **not** collide with `Rotwright` under §5's algorithm (token counts differ), so the collision fixture
  is `Vane Examplar` vs `Examplar Vane`, which genuinely normalise together; (b) a display beginning with
  `The` is refused earlier as `display_article`, so that spelling can never reach the collision check.
  Evidence: `tasks/evidence-fragments/narrative-seed-NS26.md`.

### Arcs and the spine frame (spec: `spec-arc-shapes.md`)

- [x] **NS27 Arc-shape registry.** *Depends:* NS21, NS23.
  *Files:* `_registry/arc-shapes.v1.json` (new, four shapes), `adapters/narrative/arc_shapes.py` (new),
  `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (block `arc.linkCount`), `gk-forge/tools/seedsmith/tests/test_narrative_arc_shapes.py` (new).
  *Accept:* rules 1–6 of §4 each with a passing test and a failing fixture (`flags_read_are_set_earlier`,
  `roles_close`, `rival_has_only_progress_flags`, `antagonist_shape_has_one_antagonist_role`,
  `antagonist_role_requires_antagonist_rules`, `required_choice_kinds_are_allocatable`); `shape_ids_pinned`.
  *Verify:* `SS test_narrative_arc_shapes.py`. *Commit:* `narrative-seed NS27: arc shapes`. Status: done 2026-09-23 —
  `arc-shapes.v1.json` with the four v1 shapes (rescue 4 links / debt 3 / rival 3 / lost-piece 4, every link
  a Delve host, every flag closed and every role closed) and `arc_shapes.py` (`load_arc_shapes`,
  `load_link_count_bounds`, one validator function per §4 rule so a failure names it, `all_defects`, `shape`,
  `links_in_order`); the budget gained `arc.linkCount {min: 3, max: 5}` read from the file, never a constant.
  10 tests, each rule with a passing case and a crafted failing fixture, plus `shape_ids_pinned`; the file is
  10 passed and the eight narrative files are 146 passed. `verify-change.ps1 -Paths <5> -AllowUnscoped` →
  **exit 0** (all focused, `guard.verification-boundaries` 57 passed); `guard-verification-boundaries.py` →
  OK after adding the test to `seed-narrative-registry` and `seed-narrative-plan`; ruff clean.
  Evidence: `tasks/evidence-fragments/narrative-seed-NS27.md`.

- [x] **NS28 Spine frame: seven chapter slots and fragments.** *Depends:* NS27, NS22.
  *Files:* `_registry/spine-frame.v1.json` (new, seven chapter rows chained by `after`, scenes empty,
  `fragments[]`), `arc_shapes.py`, the test, `docs/architecture/decisions.md` (map §11 row 4, landed once
  here — plan §5 item 3).
  *Accept:* `spine_chain_is_single_and_acyclic`; `frame_has_seven_chapter_slots` (owner answer,
  declaration); `chapter_row_without_scenes_plans_nothing`; `scene_beats_within_tuning_cap` reading
  `gk-core/data/tuning/story-scene-ui.v1.json`; `antagonist_speaks_when_chapters_exist`; `frame_teaching_order`;
  fragment ids unique, `after` acyclic, every `afterChapter` a frame chapter.
  *Verify:* `SS test_narrative_arc_shapes.py`; `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS28: spine frame`. Status: done 2026-09-23 —
  `spine-frame.v1.json` (seven chapter rows `chapter.one`..`chapter.seven` chained by `after`, scenes empty,
  cast carrying the three lead tokens, and seven fragment rows chained the same way with every `afterChapter`
  a frame chapter) + the spine half of `arc_shapes.py` (`load_spine_frame`, `scene_beats_cap`,
  `spine_chain`, `validate_spine_frame`, `all_defects` now covering both committed files) + the decisions.md
  row 4. 18 tests in the file (8 new spine tests), every §5 rule with a passing case and a crafted failing
  fixture: a cycle, a gap, two roots, a duplicate id, beats over the tuning cap read from
  `story-scene-ui.v1.json` (printed 6), a silent antagonist, out-of-order teaching, a twice-taught value and
  a fragment pointing at no chapter. Readings printed: chain `chapter.one`…`chapter.seven`, 7 chapters,
  7 fragments, 0 chapters with scenes. `verify-change.ps1 -Paths <4> -AllowUnscoped` → **exit 0** (all
  focused, doc-citation 0 findings, pytest 154 passed, `guard.doc-boundary` 4 passed); ruff clean.
  **One rule is scoped and says so in the code:** R2's antagonist-speaks rule applies from the first SCENE,
  not the first chapter, because an empty chapter row has no speakers — NS29 fills them and the rule then
  applies to the committed frame.
  Evidence: `tasks/evidence-fragments/narrative-seed-NS28.md`.

- [ ] **NS29 Author the seven chapters' scene structure.** *Depends:* NS28, NS26.
  *Files:* `_registry/spine-frame.v1.json` (scenes, beat counts, speakers, cast, `teaches` per scene).
  *Accept:* every §5 rule green on the filled frame; structural slugs only (no lore in ids); the owner
  reviews the structure as a registry change. *Default if the owner has not reviewed:* the rows ship
  empty, which plans no spine work; only NS61/NS65 wait.
  *Verify:* `SS test_narrative_arc_shapes.py`. *Commit:* `narrative-seed NS29: spine chapter structure`. Status: blocked — **an owner review, which this lane cannot perform.** The row's own default applies meanwhile: the seven rows ship with empty `scenes` (NS28, `1624ed92f`), which the frame's rules accept because a chapter row with no scenes plans no spine cell, so only NS61/NS65 wait. Authoring the scenes without that review would go against the row's stated default rather than satisfy it; what the owner reviews is the authored structure — per-scene `beats`, `speakers` and `teaches` — as a registry change.

### Checkpoint 1 — Wave 1

- [x] `test_narrative_*` registry suites green; no registry file carries a weight, probability or price.
      **Checked 2026-09-23 (lane `ns-2`):** the eight narrative files are green (154 passed in the path-owned
      run), and `gk-forge/tools/seedsmith/tests/test_narrative_registry_hygiene.py` scans the directory — printed
      `owned registries scanned=17 keys=1752 forbidden-key hits=0`. **One file is excluded BY NAME**, with
      its owner read: `doctrines.v1.json` carries `speciesElementBiasMilli` / `orderWeightMilli` by design
      and its `_meta.owner` is `docs/architecture/npc-story-events/spec-counter-doctrine.md#3`, so it is
      `npc-story-events`' registry, placed here by their counter-doctrine module — filed as a finding for the
      manager to route, not silently rescoped (the scan asserts every OTHER registry here declares no
      `_meta.owner`).
- [x] Hand-off recorded: `npc-story-events` `narrative-vocabulary` may read the shared files;
      `narrative-text` may read `tokens.v1.json` and `names.en.v1.json`; `spine-progress` may read
      `fragments[]`. **Recorded 2026-09-23 (lane `ns-2`) in `docs/architecture/narrative-seed-map.md` §7,
      "Hand-off (Checkpoint 1)", listing every shared vocabulary file by name, the two files
      `narrative-text` may read, and the spine frame's `fragments[]` for `spine-progress` — together with
      the `doctrines.v1.json` ownership exception.**
- [ ] Owner reviews the registries (every value's description and negative clause).
      **This is the ONLY line of CP1 still open, and the reason NS30–NS38 wait (NS30's `*Depends:* CP1`):
      it is an owner action this lane cannot perform. Measured 2026-09-23 (lane `ns-2`) so the review is a
      READ, not a repair: across the 17 owned registries, **267 rows carry a `negative` clause and every one
      of them also carries its prose clause — 138 `description`, 10 `teachingLine` (`teaches.v1.json`) and
      119 `note` (`value-notes.v1.json`); 0 rows carry one without the other.** The prose field differs by
      registry, which is why this line says "description" and three files spell it otherwise. Every reader
      already refuses a row with a missing clause, and the hygiene scan proves none carries a magnitude.**

---

## Phase 3 — Wave 2: contract and emit (no model)

### `narrative-contract` (spec: `spec-narrative-contract.md`)

- [ ] **NS30 Adapter shell and corpus tree.** *Depends:* CP1.
  *Files:* `adapters/narrative/__init__.py` (`NarrativeAdapter`), `adapters/narrative/kinds.py` (new),
  `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py` (one line), `gk-data/packs/fusion/data/seed/narrative/{storylets,characters,arcs,spine}/`
  and `authored/…` (new, empty with index), `tools/seedsmith/tests/test_narrative_contract.py` (new).
  *Accept:* `adapter_is_registered_and_satisfies_the_protocol`; `core_corpus_loader_reads_the_envelope`;
  `channels()` is empty; `legal_combinations` follows host `admits` and R20 climates.
  *Verify:* `SS test_narrative_contract.py`. *Commit:* `narrative-seed NS30: narrative adapter shell`. Status: open

- [ ] **NS31 Storylet document and call schemas, descriptions, the audit.** *Depends:* NS30.
  *Files:* `adapters/narrative/{schema,descriptions,audit}.py` (new), `report/cli.py` (`narrative contract
  --print|--audit`), `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (`storylet.maxRoles`, `text.schemaSlack`,
  `text.lengthBounds` — plan §5 item 2), `test_narrative_contract.py`, `test_narrative_storylet_vocab.py`
  (`every_borrowed_model_facing_list_has_notes`), `gk-core/scripts/enforcement-registry.v1.json`
  (`narrative-call-schema-blocked-and-closed`, `guards: ["narrative-seed"]`),
  `scripts/guard-narrative-seed.ps1` (its check line).
  *Accept:* `every_field_has_exactly_one_level`; `every_field_has_meaning_and_negative`;
  `audit_catches_all_four_smuggling_shapes`; `every_call_schema_has_blocked_variant`;
  `model_facing_enums_admit_none`; `planned_fields_are_const_in_calls`; `text_fields_carry_max_length`;
  `per_item_consequence_enum_excludes_unfillable_kinds`; `contract --audit` exits 0 for the storylet kind.
  *Verify:* `SS test_narrative_contract.py`, `SS test_narrative_storylet_vocab.py`;
  `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS31: storylet contract and schema audit`. Status: open

- [ ] **NS32 Character, arc and spine-chapter schemas.** *Depends:* NS31.
  *Files:* `schema.py`, `descriptions.py`, `kinds.py`, budget (`character.anchorLines`), the test.
  *Accept:* audit clean for all four kinds and eight call schemas; `lead_identity_writes_voice_and_bio_only`;
  `no_character_field_changes_a_character` (R13); spine chapter carries `title`, `synopsis`, `scenes[].teaches`.
  *Verify:* `SS test_narrative_contract.py`. *Commit:* `narrative-seed NS32: character, arc and spine chapter contracts`. Status: open

- [ ] **NS33 `validate_entry`, the key rule and tombstones.** *Depends:* NS32.
  *Files:* `adapters/narrative/validate.py` (new), the test, `gk-core/scripts/enforcement-registry.v1.json`
  (`narrative-no-digit-in-prose`, `guards: ["narrative-seed"]`), `scripts/guard-narrative-seed.ps1`
  (its check line).
  *Accept:* `key_rule_is_deterministic_and_hash_bearing`; `digit_in_literal_text_is_refused` (a digit in a
  token slug is not prose); `undeclared_token_is_refused`; `leave_slot_is_const`;
  `consequence_is_kind_ref_param`; `pattern_slots_and_outcome_counts_enforced`; `arc_link_consistency`;
  `chain_ref_is_derived_and_resolves`; `character_lines_cover_required_pairs_exactly`;
  `lead_character_has_no_name_or_grammar`; `eligibility_follows_flags_read`; `teaches_meets_requires`;
  `consequence_ref_derivation`; `tombstone_row_shape`; `revision_is_the_only_allowlisted_integer`;
  `document_walk_skips_derived_fields`; `authored_and_generated_ids_cannot_collide`.
  *Verify:* `SS test_narrative_contract.py`; `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS33: narrative on-disk validation and the no-digit rule`. Status: open

- [ ] **NS34 Generated-seed guard row for the narrative tree.** *Depends:* NS33.
  *Files:* `gk-core/scripts/guard-generated-seed.py` (tree row: generated `^gk-data/packs/fusion/data/seed/narrative/`; sources the
  adapter, `_registry/`, `_exemplars/`, `_plan/`), `gk-core/scripts/enforcement-registry.v1.json`
  (`narrative-no-hand-edit-generated`, `guards: ["generated-seed"]` — the guard that makes it true already
  exists, so this row does not go through `narrative-seed`), `gk-core/scripts/verification-boundaries.v1.json`
  (**Plan audit 2026-09-20**: add the missing `guard-generated-seed` row — paths
  `gk-core/scripts/guard-generated-seed.py`, project `guard`, `level: module`, no `verificationId`. Measured this
  session: `verify-change.ps1 -PlanOnly -AllowUnscoped -Paths gk-core/scripts/guard-generated-seed.py` throws
  `VERIFICATION BOUNDARY MISSING`; AGENTS.md makes that a boundary defect this task fixes, not a note it
  records. Shared file: clean-or-skip, one contiguous block).
  *Accept:* a planted change to a fixture generated narrative file (with `_meta.model`) and no source
  change fails the guard; an authored file (no `_meta.model`) passes; the planted file is removed and the
  guard is green on the real tree. Plan §5 item 11 recorded in the commit body.
  *Verify:* `python gk-core/scripts/guard-generated-seed.py` (planted, then clean); `.\scripts\run-guards.ps1 -Tier ci`;
  `python gk-core/scripts/guard-verification-boundaries.py`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json,gk-core/scripts/verification-boundaries.v1.json,gk-core/scripts/guard-generated-seed.py -Session <sid>`
  (the third path is mapped by the row this task adds).
  *Commit:* `narrative-seed NS34: generated-seed guard covers the narrative tree`. Status: open

### `narrative-emit` (spec: `spec-narrative-emit.md`)

- [ ] **NS35 Emit, revisions and tombstones.** *Depends:* NS33.
  *Files:* `adapters/narrative/{emit,revisions}.py` (new), `data/seed/narrative/_revisions/` (new),
  `tools/seedsmith/tests/test_narrative_emit.py` (new).
  *Accept:* `rerun_is_byte_identical`; `unchanged_content_is_not_rewritten`;
  `changed_content_bumps_revision_and_archives`; `archive_is_immutable`;
  `withdraw_writes_tombstone_with_closed_reason`; `tombstoned_id_is_never_reused`; `keys_change_only_with_text`;
  `invalid_entry_writes_nothing`; `meta_and_provenance_agree`; `no_timestamp_in_output`;
  `write_is_atomic`; `quest_tree_is_in_the_allowlist`; `unresolved_never_reaches_emit`; temp trees under
  pytest's `tmp_path`, never a swallowed delete.
  *Verify:* `SS test_narrative_emit.py`. *Commit:* `narrative-seed NS35: narrative emit with revisions and tombstones`. Status: open

- [ ] **NS36 Staleness, run ledger and CLI.** *Depends:* NS35.
  *Files:* `adapters/narrative/staleness.py` (new), `report/cli.py` (`narrative stale|withdraw|stamp-authored`),
  `data/seed/narrative/_runs/` (new), the test, `docs/architecture/decisions.md` (row 5).
  *Accept:* `plan_hash_does_not_stale`; `brief_change_stales_exactly_that_seed`;
  `authored_seed_is_never_stale_and_never_written_by_emit`; `stamp_authored_bumps_and_archives`;
  `ledger_reconciles_out_of_band_edit`.
  *Verify:* `SS test_narrative_emit.py`; `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS36: staleness and run ledger for narrative seeds`. Status: open

### `quest-vocab` (spec: `spec-quest-vocab.md`)

- [ ] **NS37 Objective-template registry.** *Depends:* NS30.
  *Files:* `_registry/quest-objectives.v1.json` (new), `adapters/narrative/quest_vocab.py` (new),
  `tools/seedsmith/tests/test_narrative_quest_vocab.py` (new).
  *Accept:* `every_template_has_description_and_negative`; `no_template_is_lawn_only` (rule id
  `quest.objective-lawn-only`); `template_ids_disjoint_from_the_delve_registry`;
  `template_ids_match_quest_sources` (declaration); `bands_close`.
  *Verify:* `SS test_narrative_quest_vocab.py`. *Commit:* `narrative-seed NS37: narrative quest objective templates`. Status: open

- [ ] **NS38 The `quest` kind.** *Depends:* NS37, NS33.
  *Files:* `kinds.py`, `schema.py`, `descriptions.py`, `validate.py`, `gk-data/packs/fusion/data/seed/narrative/{quests,authored/quests}/` (new), the test.
  *Accept:* `audit_is_clean_for_quest_schemas` (root `blocked`, empty vote set); `bound_at_offer_templates_carry_none`;
  `counted_rule`; `ids_are_namespaced`; `quest_offer_ref_resolves`; `no_number_in_quest`; the §3.1
  `QuestRow` mapping is the documented shape (fixture per template accepted).
  *Verify:* `SS test_narrative_quest_vocab.py`, `SS test_narrative_contract.py`.
  *Commit:* `narrative-seed NS38: narrative quest anchor kind`. Status: open

### Checkpoint 2 — Wave 2

- [ ] `contract --audit` exits 0 for five kinds and nine call schemas; `validate_entry` refuses a crafted
      violation of every §11 rule.
- [ ] Registry rows `narrative-call-schema-blocked-and-closed`, `narrative-no-digit-in-prose`,
      `narrative-no-hand-edit-generated` present; meta-test and `run-guards.ps1 -Tier ci` green.
- [ ] Hand-off recorded: `npc-story-events` `storylet-contract` builds its fixture corpus from NS33's
      shape; `quest-sources` reads NS37–NS38.

---

## Phase 4 — Wave 3: validators, metrics, review (no model)

### `narrative-validators` (spec: `spec-narrative-validators.md`)

- [ ] **NS39 Feature-agnostic prose validators and tier rows.** *Depends:* CP2.
  *Files:* `workflow/validators/prose.py` (new), `workflow/validators/registry.py` (rows incl.
  `name_collision`), `tools/seedsmith/tests/test_prose_validators.py` (new).
  *Accept:* `no_digit` (category `Nd`, literal text only), `length_bound` (budget), `word_list_hits`
  (word boundaries: a list word inside a longer word does not match); `every_validator_has_a_tier_row`.
  *Verify:* `SS test_prose_validators.py`. *Commit:* `narrative-seed NS39: prose validators`. Status: open

- [ ] **NS40 Structural validators and the choice-type classifier.** *Depends:* NS39.
  *Files:* `adapters/narrative/validators/{__init__,structure,choice_type}.py` (new),
  `tools/seedsmith/tests/test_narrative_validators_structure.py` (new), `gk-core/scripts/enforcement-registry.v1.json`
  (`narrative-r13-counter-doctrine`, `guards: ["narrative-seed"]`), `scripts/guard-narrative-seed.ps1`
  (its check line, running both R13 tests).
  *Accept:* `choice_type_members_are_pinned`; `choice_type_worked_cases`;
  `conditional_choices_do_not_make_a_storylet_obvious`; `conditional_worse_than_unconditional_is_rejected`;
  `leave_is_never_the_dominated_party`; `lose_lose_rejected` (excludes `leave`);
  `enemy_consequence_rejected`; `consequence_ref_unfillable_rejected`; `names_good_option_is_soft`.
  *Verify:* `SS test_narrative_validators_structure.py`, `SS test_narrative_character_vocab.py`;
  `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS40: storylet structural gate and counter-doctrine rule`. Status: open

- [ ] **NS41 Text validators, name sets and the validate verb.** *Depends:* NS40, NS26.
  *Files:* `adapters/narrative/validators/{text,name_sets}.py` (new), `_registry/out-of-world.v1.json`
  (new, authored), `report/cli.py` (`narrative validate`), `tools/seedsmith/tests/test_narrative_validators_text.py` (new),
  `gk-core/scripts/enforcement-registry.v1.json` (`narrative-no-literal-name`, `guards: ["narrative-seed"]`),
  `scripts/guard-narrative-seed.ps1` (its check line).
  *Accept:* `literal_name_rejected_on_word_boundary` with the token repair message;
  `digit_inside_a_token_is_not_prose`; `token_closure`; `round_trip_detects_a_baked_name`;
  `round_trip_set_b_shares_no_word_with_set_a`; `out_of_world_word_boundary`;
  `out_of_world_list_holds_no_ip_mark`; `allowed_entities_come_from_context`;
  `enemy_side_line_keyed_to_own_encounters_rejected`; `defect_strings_name_field_and_value`;
  `pass_is_reported_as_mechanically_valid`.
  *Verify:* `SS test_narrative_validators_text.py`; `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS41: narrative text validators and the no-literal-name rule`. Status: open

### `narrative-metrics` (spec: `spec-narrative-metrics.md`)

- [ ] **NS42 Coverage and linkage metrics; the report's narrative budget branch.** *Depends:* CP2.
  *Files:* `adapters/narrative/metrics/{__init__,coverage,linkage}.py` (new), `report/cli.py`
  (`build_registry` lines; `cmd_report` narrative budget branch), `tools/seedsmith/tests/test_narrative_metrics.py` (new).
  *Accept:* `cell_coverage_trips_and_clears`; `missing_budget_row_is_not_measured`;
  `climate_skew_is_visible_per_cell`; `line_pair_coverage_names_the_missing_pair`; `arc_integrity`;
  `tombstone_reference_is_a_gap`; every metric `gates=False`.
  *Verify:* `SS test_narrative_metrics.py`. *Commit:* `narrative-seed NS42: narrative coverage and linkage metrics`. Status: open

- [ ] **NS43 Distribution, diversity and voice metrics.** *Depends:* NS42.
  *Files:* `metrics/{distribution,diversity,voice}.py` (new), budget block `metrics`
  (`pending-calibration` rows), the test, `gk-core/scripts/enforcement-registry.v1.json`
  (`narrative-open-loop-never-gates`, `guards: ["narrative-seed"]`), `scripts/guard-narrative-seed.ps1`
  (its check line).
  *Accept:* `open_loop_metrics_cannot_gate`; `every_metric_declares_loop_and_starts_ungated`;
  `diversity_is_name_length_invariant`; `self_repetition_trips_on_template_reuse`;
  `voice_distinctness_is_deterministic`; `vote_disagreement_reads_provenance`;
  `no_metric_reads_another_metrics_output`.
  *Verify:* `SS test_narrative_metrics.py`; `.\scripts\guard-narrative-seed.ps1`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS43: narrative distribution, diversity and voice readings`. Status: open

### `review-render` (spec: `spec-review-render.md`)

- [ ] **NS44 Sampling, casts and the render model.** *Depends:* CP2, NS40 (choice type passed in).
  *Files:* `adapters/narrative/review/{__init__,sample,casts,render}.py` (new), budget block `review`,
  `tools/seedsmith/tests/test_narrative_review_render.py` (new).
  *Accept:* `render_is_deterministic`; `sample_reuses_stratified_sample`; `spine_is_a_census`;
  `no_digit_in_any_render`; `casts_differ_in_a_feature_tag`; `unfilled_role_renders_a_labelled_stand_in`;
  `storylet_shows_choice_type_and_profiles`; `lead_tier_shows_both_candidates`.
  *Verify:* `SS test_narrative_review_render.py`. *Commit:* `narrative-seed NS44: review render`. Status: open

- [ ] **NS45 Verdicts, CLI and the open-loop voice row.** *Depends:* NS44.
  *Files:* `review/verdicts.py` (new), `report/cli.py` (`narrative review render|verdict|status`),
  `data/seed/narrative/_review/` (new), the test, `gk-core/scripts/enforcement-registry.v1.json` (`narrative-voice-quality`,
  a genuine `unguardableReason` — whether a line is in character is open-loop, so no check goes into
  `guard-narrative-seed.ps1` for it; plan D4).
  *Accept:* `verdict_is_append_only`; `reject_requires_a_reason`; `verdict_never_touches_the_seed`;
  `verdict_vocabularies_are_pinned`.
  *Verify:* `SS test_narrative_review_render.py`; `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json -Session <sid>`.
  *Commit:* `narrative-seed NS45: review verdict queue`. Status: open

### Checkpoint 3 — Wave 3

- [ ] Whole seedsmith suite green with the transport stubbed to raise.
- [ ] Registry rows `narrative-r13-counter-doctrine`, `narrative-no-literal-name`,
      `narrative-open-loop-never-gates`, `narrative-voice-quality` present; `guard-narrative-seed.ps1`
      and the meta-test green (only the voice row carries an unguardableReason).

---

## Phase 5 — Wave 4: grounding and planning (no model)

### `lore-packet` (spec: `spec-lore-packet.md`)

- [ ] **NS46 Lore packet.** *Depends:* CP3. Soft: `ip-censor` T14 (plan §5 item 10).
  *Files:* `adapters/narrative/packet.py` (new), budget block `packet`, `report/cli.py` (`narrative packet`),
  `tools/seedsmith/tests/test_narrative_lore_packet.py` (new).
  *Accept:* `packet_is_deterministic`; `motif_selection_is_seeded_from_the_subject`;
  `unglossed_motif_refuses_naming_it`; `no_raw_motif_in_any_packet`; `no_display_string_in_any_packet`;
  `feature_tags_ride_with_tokens`; `allowed_entities_match_declared_tokens`;
  `avoid_list_absent_is_not_a_blocker` (also covers an absent helper module: empty `avoid`, provenance
  records it); `no_franchise_style_reference`; `no_digit_in_packet`; `gloss_change_stales_exactly_its_subjects`.
  No private IP list.
  *Verify:* `SS test_narrative_lore_packet.py`. *Commit:* `narrative-seed NS46: lore packet`. Status: open

### `narrative-planner` (spec: `spec-narrative-planner.md`)

- [ ] **NS47 Planner: cells, pattern allocation, teaching allocation.** *Depends:* NS46, NS43.
  *Files:* `adapters/narrative/planner/{__init__,cells,patterns}.py` (new),
  `tools/seedsmith/tests/test_narrative_planner.py` (new).
  *Accept:* `cells_follow_host_legality` (R20: world hosts all seven climates; neutral hosts `none` only);
  `undefined_hosts_have_no_cells`; `pattern_floors_met_or_refused` (named binding constraint, never a
  partial plan); teaching values land on items meeting `requires`, a value no item can carry is a named
  refusal; study-site raid items carry `doctrine-studying` eligibility.
  *Verify:* `SS test_narrative_planner.py`. *Commit:* `narrative-seed NS47: narrative planner cells and patterns`. Status: open

- [ ] **NS48 Planner: species picks, work order, ids, quest and scene attachment.** *Depends:* NS47.
  *Files:* `planner/{species,work_order}.py` (new), the test.
  *Accept:* `species_one_character_each`; `species_spread_across_elements`; `arc_links_are_one_unit_and_close`;
  `ids_continue_and_skip_tombstones`; `minted_ids_match_the_contract_grammar`;
  `arc_link_flag_positions_are_planned`; `adding_a_cell_stales_nothing_else`; `plan_is_deterministic`;
  work items that offer a quest or play a scene carry the anchor or scene id (plan §5 item 12).
  *Verify:* `SS test_narrative_planner.py`. *Commit:* `narrative-seed NS48: narrative work order`. Status: open

- [ ] **NS49 Call-shape table, dry run, budget and the committed plan.** *Depends:* NS48.
  *Files:* `adapters/narrative/call_shape.py` (new), `planner/dry_run.py` (new), `report/cli.py`
  (`narrative plan --dry-run|--write`), budget (coverage rows, `coverage.*`, `calls.*`),
  `data/seed/narrative/_plan/plan.v1.json` (new), the test, `docs/architecture/decisions.md` (map §11 row 1).
  *Accept:* `dry_run_makes_no_call`; `dry_run_reports_unregistered_renderers`;
  `dry_run_call_table_matches_formula`; `over_cap_exits_non_zero`; `call_shape_is_single_source`;
  `climate_is_planned_const`; full-target rows carry `derivation: pending-pulse-rates`.
  *Verify:* `SS test_narrative_planner.py`; `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md -Session <sid>`.
  *Commit:* `narrative-seed NS49: narrative plan and its call budget`. Status: open

### Checkpoint 4 — Wave 4, and gate NSG2

- [ ] `narrative plan --dry-run` prints per kind: items, base calls, heal allowance, worst case, wall
      time, and `calls.capPerRun`; the output is quoted in the checkpoint note.
- [ ] `narrative packet --all --check` exits 0 (no unglossed motif in any planned item).
- [ ] **NSG2**: the owner approves the Wave-5 spend against the printed figure. Default: NS50–NS57 proceed;
      no run starts.

---

## Phase 6 — Wave 5: model pipelines

Code tasks run against stubs; each registers its prompt renderer so the planner's dry run renders its
prompts. Run tasks follow plan D6 and each needs NSG2.

### `storylet-pipeline` (spec: `spec-storylet-pipeline.md`)

- [ ] **NS50 Storylet pipeline: the structure call.** *Depends:* CP4.
  *Files:* `adapters/narrative/pipelines/{__init__,storylet}.py` (new), `pipelines/prompts/storylet.py`
  (new), `tools/seedsmith/tests/test_narrative_storylet_pipeline.py` (new).
  *Accept:* `three_samples_see_three_orders`; `planned_fields_are_const`; `vote_3_0_2_1_1_1`;
  `unresolved_is_not_retried`; `carrier_is_lowest_matching_sample`; `no_coherent_sample_is_a_quality_retry`;
  `structural_defect_redraws_with_defect_named`; `ref_is_filled_after_the_vote`;
  `unfillable_kinds_are_not_offered`; `pinned_flag_position_leaves_the_vote`; `blocked_sample_ends_the_item`.
  *Verify:* `SS test_narrative_storylet_pipeline.py`. *Commit:* `narrative-seed NS50: storylet structure call`. Status: open

- [ ] **NS51 Storylet pipeline: the text call, graph and CLI.** *Depends:* NS50.
  *Files:* `pipelines/storylet.py`, `pipelines/prompts/storylet.py`, `workflow/graphs/narrative_storylet.py`
  (new), `report/cli.py` (`narrative storylets run|status`), budget block `storylet`, the test.
  *Accept:* `text_sees_structure_as_const`; `literal_name_repairs_with_token`; `two_repairs_then_unresolved`;
  `worst_case_is_twelve_calls`; `transient_replay_makes_no_new_generation`; `rerun_is_byte_identical`;
  `dry_run_makes_no_call`; `no_model_literal`.
  *Verify:* `SS test_narrative_storylet_pipeline.py`, `SS test_offline_guarantee.py`.
  *Commit:* `narrative-seed NS51: storylet text call and pipeline graph`. Status: open

### `character-pipeline` (spec: `spec-character-pipeline.md`)

- [ ] **NS52 Character pipeline: identity.** *Depends:* CP4.
  *Files:* `pipelines/character.py` (new), `pipelines/prompts/character.py` (new),
  `tools/seedsmith/tests/test_narrative_character_pipeline.py` (new).
  *Accept:* `species_name_never_in_identity_prompt`; `role_and_voice_voted_with_permutation`;
  `planned_role_not_shown`; `voted_role_differs_legal_is_accepted`; `enemy_restricted_role_redraws`;
  `carrier_always_exists_when_both_resolve`; `lead_identity_votes_voice_only`; `blocked_reply_ends_the_stage`.
  *Verify:* `SS test_narrative_character_pipeline.py`. *Commit:* `narrative-seed NS52: character identity stage`. Status: open

- [ ] **NS53 Character pipeline: anchors and the human gate.** *Depends:* NS52, NS45.
  *Files:* `pipelines/character.py`, `pipelines/prompts/character.py`, the test.
  *Accept:* `lines_refused_without_anchor_verdict` (no call); `lead_gets_two_anchor_candidates_and_pick_recorded`;
  `lexicon_field_names_match_the_contract`.
  *Verify:* `SS test_narrative_character_pipeline.py`. *Commit:* `narrative-seed NS53: character anchors behind a recorded verdict`. Status: open

- [ ] **NS54 Character pipeline: lines, prior turns, graph and CLI.** *Depends:* NS53.
  *Files:* `pipelines/character.py`, `pipeline/llm_caller.py` (optional `prior_turns`),
  `workflow/graphs/narrative_character.py` (new), `report/cli.py` (`narrative characters run`), budget
  block `character`, `test_narrative_character_pipeline.py`, `test_llm_caller.py`.
  *Accept:* `prior_turns_absent_is_byte_identical`; `anchors_sent_as_prior_turns`;
  `one_line_per_required_context_per_band`; `forbidden_lexicon_word_rejected`;
  `enemy_personal_memory_never_requested_or_accepted`; `lines_per_allegiance`; `worst_case_bounds`.
  *Verify:* `SS test_narrative_character_pipeline.py`, `SS test_llm_caller.py`.
  *Commit:* `narrative-seed NS54: character lines with anchors as prior turns`. Status: open

- [ ] **NS55 The `quest-text` call in the storylet and arc work orders.** *Depends:* NS51, NS38.
  *Files:* `pipelines/storylet.py`, `pipelines/prompts/storylet.py` (quest-text prompt), `emit.py`
  (writes `quests/`), the storylet pipeline test.
  *Accept:* an item with an attached quest anchor produces a quest seed whose `name`/`flavor` pass the text
  battery; the quest call's vote set is empty; a `quest.offer` ref resolves to the emitted anchor.
  *Verify:* `SS test_narrative_storylet_pipeline.py`, `SS test_narrative_quest_vocab.py`.
  *Commit:* `narrative-seed NS55: quest text generated with the offering storylet`. Status: open

### `arc-pipeline` (spec: `spec-arc-pipeline.md`)

- [ ] **NS56 Arc pipeline.** *Depends:* NS51.
  *Files:* `pipelines/arc.py` (new), `pipelines/prompts/arc.py` (new), `workflow/graphs/narrative_arc.py`
  (new), `report/cli.py` (`narrative arcs run`), budget block `arc`,
  `tools/seedsmith/tests/test_narrative_arc_pipeline.py` (new).
  *Accept:* `links_cannot_point_past_the_arc`; `unresolved_link_emits_nothing`; `resume_reuses_accepted_parts`;
  `persistent_roles_copied_from_the_shape`; `flags_are_planned`; `flags_read_become_eligibility`;
  `continuity_context_is_one_link_back`; `rival_links_carry_only_planned_progress_flags`;
  `counter_doctrine_rejects_enemy_consequence`; `call_bounds` (L=4: 17 clean, 51 worst).
  *Verify:* `SS test_narrative_arc_pipeline.py`. *Commit:* `narrative-seed NS56: arc pipeline`. Status: open

### `spine-pipeline` (spec: `spec-spine-pipeline.md`)

- [ ] **NS57 Spine pipeline.** *Depends:* NS56, NS54, NS29.
  *Files:* `pipelines/spine.py` (new), `pipelines/prompts/spine.py` (new), `workflow/graphs/narrative_spine.py`
  (new), `report/cli.py` (`narrative spine run|commit`), budget block `spine`,
  `tools/seedsmith/tests/test_narrative_spine_pipeline.py` (new).
  *Accept:* `beats_and_speakers_are_const`; `speakers_are_tokens`; `candidates_are_not_spliced`;
  `nothing_commits_without_a_pick`; `pick_emits_exactly_one_candidate`; `antagonist_personal_memory_rejected`;
  `markup_outside_closed_tags_rejected`; `unresolved_candidate_does_not_block_the_other`;
  `chapter_schema_is_the_contracts`; `slot_without_scenes_plans_nothing`; `call_bounds`. The map §11 row 4
  landed in NS28 (checked, not re-appended).
  *Verify:* `SS test_narrative_spine_pipeline.py`. *Commit:* `narrative-seed NS57: spine pipeline`. Status: open

### First batches (each after NSG2)

- [ ] **NS58 [model] Storylets batch 1.** *Depends:* NS51, NS55, NSG2.
  *Budget:* 4 base / 12 worst per storylet; `--limit 12`: 48 base / 144 worst, plus 1 preflight.
  *Steps:* `narrative storylets run --dry-run` → `narrative preflight` → `--write --limit 12` →
  `narrative review render --batch <runId> --kind storylet` (all twelve) → verdicts → rejected seeds
  regenerated with the reason (next run's dry run counts them) → commit the emitted seeds.
  *Accept:* every committed storylet passed both gates; readings printed (vote disagreement per field,
  choice-type and choice-kind distribution, repairs per defect).
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative` exits 0; `SS test_narrative_emit.py`.
  *Commit:* `narrative-seed NS58: first storylet batch`. Status: open

- [ ] **NS59 [model] Characters batch 1: the three leads and nine texture characters.** *Depends:* NS54, NSG2.
  *Budget:* texture 4+B base / 12+3B worst (B=4: 8/24); leads 5+B / 15+3B with B = 0, 4, 2 for the
  summoner, companion and antagonist. Batch: 93 base / 279 worst, plus 1 preflight.
  *Steps:* identity dry run → preflight → `--stage identity --write` → `--stage anchors --write` → review:
  accept (texture) or pick (leads) every anchor set → `--stage lines --write` → review render → commit.
  *Accept:* no line call ran before its anchor verdict; every committed character covers its required
  pairs or is listed `unresolved`.
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative` exits 0.
  *Commit:* `narrative-seed NS59: first character batch with the three leads`. Status: open

- [ ] **NS60 [model] One arc (`rescue`).** *Depends:* NS56, NS59 (a cast to draw on), NSG2.
  *Budget:* 1 + 4L base / 3 + 12L worst; L=4: 17 / 51, plus 1 preflight.
  *Steps:* dry run → preflight → `narrative arcs run --write --shape rescue --limit 1` → census review → commit.
  *Accept:* all or nothing; `Narrative/ArcIntegrity` clean.
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative`. *Commit:* `narrative-seed NS60: first arc`. Status: open

- [ ] **NS61 [model] Spine chapter 1.** *Depends:* NS57, NS59, NSG2.
  *Budget:* 2 + 2s base / 6 + 6s worst at two candidates (s = chapter 1's scene count from NS29; s=3 gives
  8 / 24), plus 1 preflight.
  *Steps:* dry run → preflight → `narrative spine run --write --chapter <slot 1>` → side-by-side render →
  owner `pick` → `narrative spine commit --run <runId>`.
  *Accept:* the corpus holds exactly the picked candidate; the other stays in the ledger.
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative`. *Commit:* `narrative-seed NS61: spine chapter one`. Status: open

### Scale (each after NSG4)

**Plan audit 2026-09-20 — every scale task carries the same four steps as its first batch** (plan D6 and
principle 7, which the four entries below previously stated only as a budget line): `--dry-run` first and
its printed figure recorded in the ledger → `narrative preflight` (one real call; the endpoint may have
changed since the batch) → `--write` → review the named sample → commit only accepted seeds. The
illustrations below are **net of batch 1**, as NS17, NS19 and NS68 already are; the dry run's figure, not
the illustration, is what NSG4 approves.

- [ ] **NS62 [model] Storylets to the first-ship target.** *Depends:* NS58, NSG4. *Budget:* the dry run's
  figure for the planned storylet items still unwritten (illustration: 84 planned − 12 in batch 1 = 72 at
  4 base / 12 worst each → **288 base / 864 worst**), plus 1 preflight.
  *Steps:* dry run → preflight → `narrative storylets run --write` → review `review.samplePerBatch.storylet`
  rows, stratified → verdicts → commit only accepted seeds.
  *Accept:* every committed storylet passed both gates; no item is regenerated without its rejection
  reason; readings printed, never asserted (coverage per cell, vote disagreement, repairs per defect).
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative` exits 0; `SS test_narrative_emit.py`.
  *Commit:* `narrative-seed NS62: storylets to first-ship coverage`. Status: open
- [ ] **NS63 [model] Characters to the first-ship target.** *Depends:* NS59, NSG4. *Budget:* the dry run's
  figure (illustration: 54 planned − 12 in batch 1 = 42 texture characters at 8 base / 24 worst →
  **336 base / 1,008 worst**), plus 1 preflight.
  *Steps:* dry run → preflight → `--stage identity --write` → `--stage anchors --write` → **every anchor
  set reviewed before any line call** → `--stage lines --write` → review render → commit.
  *Accept:* no line call ran before its anchor verdict (the pipeline refuses it, NS53); every committed
  character covers its required pairs or is listed `unresolved`.
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative` exits 0.
  *Commit:* `narrative-seed NS63: characters to first-ship coverage`. Status: open
- [ ] **NS64 [model] One arc per remaining shape.** *Depends:* NS60, NSG4. *Budget:* the dry run's figure
  (illustration: 3 remaining shapes at 1 + 4L base / 3 + 12L worst, L=4 → **51 base / 153 worst**), plus 1
  preflight. *Steps:* dry run → preflight → `narrative arcs run --write --shape <id>` per shape → census
  review (every link) → commit.
  *Accept:* each arc is all-or-nothing; `Narrative/ArcIntegrity` clean; an unresolved link emits nothing.
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative`.
  *Commit:* `narrative-seed NS64: one arc per shape`. Status: open
- [ ] **NS65 [model] Remaining spine chapters.** *Depends:* NS61, NSG4, NS29 (scenes authored for each
  chapter). *Budget:* the dry run's figure (illustration: 6 remaining chapters at 2 + 2s base / 6 + 6s
  worst, s=3 → **48 base / 144 worst**), plus 1 preflight. *Steps:* dry run → preflight → one
  `narrative spine run --write --chapter <slot>` per chapter → side-by-side render → owner `pick` per
  chapter → `narrative spine commit`.
  *Accept:* one committed candidate per chapter, the other in the ledger; nothing commits without a pick;
  a chapter whose scenes NS29 left empty is skipped and named, never generated blind.
  *Verify:* `narrative validate --corpus ..\..\data\seed\narrative`.
  *Commit:* `narrative-seed NS65: remaining spine chapters`. Status: open

Each scale task verifies with `narrative validate --corpus ..\..\data\seed\narrative` and
`seedsmith report --adapter narrative` (readings quoted, never asserted), and commits only accepted seeds.

### Checkpoint 5 — Wave 5

- [ ] Whole seedsmith suite green with the transport stubbed to raise; a second emit over the committed
      corpus writes no byte (`narrative stale` empty for unchanged inputs).
- [ ] Readings reviewed by the owner: coverage per cell, vote disagreement, register acceptance.

---

## Phase 7 — Wave 6: the Delve corpus

### `delve-event-regen` (spec: `spec-delve-event-regen.md`)

- [ ] **NS66 Delve regeneration driver and cutover check.** *Depends:* NS51, NS19.
  *Files:* `adapters/narrative/delve.py` (new), `report/cli.py` (`narrative delve regen|cutover --check`),
  `tools/seedsmith/tests/test_narrative_delve_regen.py` (new).
  *Accept:* `uses_only_the_storylet_pipeline`; `climate_is_planned_for_every_delve_storylet`;
  `no_chain_reference_in_delve_storylets`; `legacy_ids_are_retired_and_never_reissued`;
  `cutover_check_fails_on_leftover_event_file`; `cutover_check_never_passes_runtime_rows`;
  `no_brief_contains_a_raw_motif`; `dry_run_makes_no_call`.
  *Verify:* `SS test_narrative_delve_regen.py`. *Commit:* `narrative-seed NS66: Delve storylet regeneration driver`. Status: open

- [ ] **NS67 [model] Delve storylets batch 1.** *Depends:* NS66, NSG2.
  *Budget:* 4 base / 12 worst per storylet; `--limit 12`: 48 / 144, plus 1 preflight.
  *Steps:* `narrative delve regen --dry-run` (record the whole-Delve figure) → preflight → `--write --limit 12`
  → review render → verdicts → commit into `data/seed/narrative/storylets/` (read by nothing yet).
  *Verify:* `SS test_narrative_delve_regen.py`; `narrative validate --corpus ..\..\data\seed\narrative`.
  *Commit:* `narrative-seed NS67: first Delve storylet batch`. Status: open

- [ ] **NS68 [model] Remaining Delve cells.** *Depends:* NS67, NSG4.
  *Budget:* `C × 2 × 4` base, `C × 2 × 12` worst minus batch 1 (illustration at 42 cells: 288 base / 864
  worst after batch 1). *Commit:* `narrative-seed NS68: Delve storylets to first-ship coverage`. Status: open

- [ ] **NS69 Cutover: retire the `dungeon-event` kind with the loader switch.** *Agent:*
  **implementer-hard** (plan D6b — a cross-program delete landed with the runtime loader switch in one
  change). *Depends:* NS68, **NSG3**;
  external: `npc-story-events` `storylet-contract` reads the storylet tree, `party-dungeon` room pools are
  host-kind pools, NS7 leave on every storylet, preflight fails on a dangling link, the C# tests that read
  `gk-data/packs/fusion/data/seed/dungeon/events/` moved by their owners.
  *Files (this program's half, one change with the owners' halves — plan D2 exception):*
  `adapters/dungeon/{kinds,schema,briefs,pipelines,planner,completeness}.py` (event kind removed),
  `data/seed/dungeon/_plan/budget.v3.json` (new, without the event row), `gk-data/packs/fusion/data/seed/dungeon/events/**`
  (deleted), `data/seed/narrative/_runs/delve-cutover.json` (retired legacy ids), the dungeon adapter tests.
  *Accept:* `narrative delve cutover --check` passes every seed-side row and lists the runtime rows for the
  reviewers to tick; `dungeon_adapter_kinds_after_cutover` (the six other kinds remain); the four legacy
  `story` events' known-defect entries are removed on the runtime side in the same change.
  *Verify:* `SS test_narrative_delve_regen.py`, the dungeon adapter test files with `SS`, the whole seedsmith
  suite, and the whole C# suite once (`.\scripts\test-fast.ps1 -AllDefault`, AGENTS.md point 2: this change
  crosses programs), plus `.\scripts\verify-change.ps1 -DeletedPaths <a former event file> -Session <sid>`.
  *NSG3 default:* nothing is deleted; the storylets stay committed and unread.
  *Commit:* `narrative-seed NS69: Delve events move to the narrative adapter`. Status: open

- [x] **NS70 Program doc propagation.** *Depends:* none (may land any time after NS1).
  *Files:* `docs/architecture/narrative-seed-map.md` (§7 row on `verification-boundaries.v1.json` reconciled
  with NS1/NS2; §13 checklist row ticked for the registry rows), `docs/architecture/narrative-seed-ideal.md`
  (the §3.5 stale claims of the map: model-literal count, `Instantiator.cs` line, `layouts.py` lines).
  *Accept:* `python scripts/audit-doc-citations.py --scope docs/architecture/narrative-seed-map.md` and on the
  ideal report 0 HIGH.
  *Verify:* `.\scripts\verify-change.ps1 -Paths docs/architecture/narrative-seed-map.md,docs/architecture/narrative-seed-ideal.md -Session <sid>`.
  *Commit:* `narrative-seed NS70: reconcile map and ideal with what was built`. Status: done 2026-09-23 —
  every listed claim re-read against the code this session: the ideal's §4.2 model-literal row is marked
  **CLOSED** by NS3–NS6 (0 literals and 0 `DEFAULT_CONFIG` outside `llm_caller.py`, enforced by
  `test_no_model_literal.py`) and the contradicting sentence in its R6 row is gone; the `TryInstantiate`
  citation was re-verified at `Instantiator.cs:98` and `layouts.py:35-42`; the map's §3.5 gained a
  "Reconciled 2026-09-23 (NS70)" paragraph naming what is fixed and that items 4–5 were never stale
  citations, §13's audit reading became `94 citations; 9 D1 (0 HIGH)`, §7's `verification-boundaries` row now
  records the grant this program's NS1/NS2 rows landed under, and §11 marks decisions rows 2/3/4/6 landed.
  Audits: ideal `67 citations, 0 HIGH`; map `96 citations, 9 D1 all 0 HIGH`. `verify-change.ps1 -Paths <2>` →
  exit 0, `guard.doc-boundary` 4 passed. Evidence: `tasks/evidence-fragments/narrative-seed-NS70.md`.

### Final checkpoint

- [ ] Every map §10 contract check has a passing test; every §10 reading prints from `report`.
- [ ] All ten registry rows present — eight guarded by `narrative-seed`, one by `generated-seed`, one
      open-loop; `guard-narrative-seed.ps1`, the enforcement meta-test and `run-guards.ps1 -Tier ci` green.
- [ ] One storylet generator remains; no `dungeon-event` kind; no file under `gk-data/packs/fusion/data/seed/dungeon/events/`
      (or NSG3 recorded as unanswered, with its default in force).
- [ ] Session record closed (`status: merged`) in a new commit.

---

## Gates (see plan §7)

| Gate | Task | Resolver | Default |
|---|---|---|---|
| NSG1 commit of regenerated legacy events | NS18 | Owner | run stays in `_runs/`, uncommitted |
| NSG2 Wave-5 spend | CP4 → NS58–NS68 runs | Owner | code proceeds, no run |
| NSG3 Delve cutover | NS69 | Owner + `npc-story-events` + `party-dungeon` reviewers | nothing deleted |
| NSG4 scale past a first batch | NS17, NS19, NS62–NS65, NS68 | Owner | first batch only |

---

## Plan audit (2026-09-20)

Findings and severities are in [narrative-seed-plan.md](narrative-seed-plan.md) *Plan audit (2026-09-20)*
(A1–A11). What changed **in this file**, all fixed, none deferred:

| Ref | Sev | Change |
|---|---|---|
| A1 | High | NS6b adds the `guard-narrative-seed` boundary row; NS34 adds the missing `guard-generated-seed` row. Both verify lines now pass the guard script itself and run `guard-verification-boundaries.py`. NS34's "`scripts/guard-*.ps1` is unmapped" note is gone — an unmapped production path is a defect to fix |
| A2 | High | NS6b gains the anti-vacuous criterion: the guard derives its required row set from `enforcement-registry.v1.json`, fails on an uncovered row, a check line naming no row, or a check selecting zero node ids — with that falsifier in the verify step |
| A3 | High | NS6b, NS18, NS19 and NS69 marked `implementer-hard` (plan D6b) |
| A4 | High | Conventions gain the `report/cli.py` clean-or-skip rule against `ip-censor` T16; NS6b's CI clean-or-skip now names `ip-censor` T1/T11 |
| A5 | Medium | Gates renamed `G1`–`G4` → **`NSG1`–`NSG4`** throughout, so they no longer collide with the `npc-story-events` map's `G0`–`G7` |
| A6, A7 | Medium | NS62–NS65 each gain Steps (dry run → preflight → write → review → commit accepted), Accept and Verify, and their illustrations are restated net of batch 1 (NS62 288/864, NS63 336/1,008, NS64 51/153, NS65 48/144) |
| A8 | Medium | `### <module> (spec: …)` headers added for Phases 5–7: `lore-packet`, `narrative-planner`, `storylet-pipeline`, `character-pipeline`, `arc-pipeline`, `spine-pipeline`, `delve-event-regen` |
| A10 | Low | The mapped-path list gains `.github/workflows/**` (boundary `ci-workflows`), confirmed by measurement |

`python scripts/audit-doc-citations.py --scope tasks/narrative-seed-todo.md` — **0 HIGH**.
