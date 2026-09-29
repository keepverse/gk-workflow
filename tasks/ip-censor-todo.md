# Todo: ip-censor

**Program:** `ip-censor` · **Plan:** [ip-censor-plan.md](ip-censor-plan.md)
**Status:** approved 2026-09-22, ready for lanes. Written 2026-09-19; owner approved implementation
2026-09-22. **25 tasks (T0–T23 plus T19b) · 7 checkpoints ·
1 gate (G1, answered yes 2026-09-19 — it adds T19b and blocks nothing else).** Status lives here only.
Premises re-verified at the convergence head 2026-09-22 ([plan §13](ip-censor-plan.md) addendum): three
citation anchors moved, and **T13's external dependency closed** (TVB3.1/TVB3.2 landed), so the `ipcensor`
pytest lane is no longer waiting on anything.
One task = one commit (code + tests + evidence + this ledger line), explicit paths, never `git add -A`,
never `git stash`, never push, never amend. No watermarks in commit messages. *Audit 2026-09-19: count
and G1 state corrected; T19b moved into Phase 6.*

## Lane status (2026-09-22, lane `ip-censor-1`, branch `cmdc/ip-censor-1`)

**Done (8 rows):** T0, T1, T2, T3, T5, T6, T7, T9 — plus the in-fence halves of T4 (classifier and
remediation derivation), T8 (curate import and the USPTO adapter) and T10 (composition root, CLI and
plan). Every row's readings are in `tasks/ip-censor-ledger.jsonl`.

**Blocked at this lane's runner allowed-path list (17 rows):** T4 (part 2), T8 (part 2), T10 (one
acceptance line — the shipped registry), and T11–T23. Each blocked row's ledger line names the path it
needs; the grant that unblocks them is the same for all of them:

- `gk-data/packs/fusion/data/seed/ip-censor/**` (T4 part 2, T8 part 2, T18, T21, T22 — the authored registry and the
  import filter, which this file's own T0 says the session claims)
- `tasks/ip-censor/**` (T10's plan/report outputs, T17, T21, T22, T23)
- `gk-forge/tools/seedsmith/**` (T14–T16, T18, T19)
- `.github/workflows/release.yml`, `gk-core/scripts/enforcement-registry.v1.json` (T12)
- `gk-core/scripts/verification-boundaries.v1.json` (T13)
- `gk-data/packs/fusion/data/seed/passive-tree/**`, `gk-data/packs/fusion/data/seed/creatures/**`, `gk-data/packs/fusion/data/generated/**` (T16, T19, T19b)
- `gk-core/src/FusionRpg.Data/**`, `gk-core/tests/FusionRpg.Data.Tests/**` (T19b, T20)

The fence currently grants `gk-core/tools/ip-censor/**`, `.github/workflows/ci.yml`, `tests/**`,
`docs/architecture/ip-censor/**`, `tasks/ip-censor-todo.md`, `tasks/ip-censor-ledger.jsonl` and
`tasks/reports/**` only.

**Nothing was written outside that list**, with one exception the brief itself mandates: T0's
`tasks/sessions/ip-censor-1.json`.

---

## Lane status (2026-09-23, lane `ip-censor-2`, branch `cmdc/ip-censor-2`)

This lane carries the grants that unblock those 17 rows: `tasks/ip-censor/**`,
`gk-data/packs/fusion/data/seed/ip-censor/**`, `gk-core/tools/ip-censor/**`, `docs/architecture/**`, `scripts/**` and
`.github/workflows/ci.yml`. Still outside it: `gk-forge/tools/seedsmith/**` (T14–T16, T18's reader, T19),
`.github/workflows/release.yml` + `gk-core/tests/FusionRpg.Guard.Tests/**` (T12), `gk-data/packs/fusion/data/seed/creatures/**`,
`gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/passive-tree/**` (T16, T19, T19b), `gk-core/src/FusionRpg.Data/**` +
`gk-core/tests/FusionRpg.Data.Tests/**` (T19b, T20).

**Closed here:** T4 (both parts), T8 (both parts), T10 (its last acceptance line now passes against
  the shipped registry), T11, T13, T17, T18 (part 1 — the `registry.py` half), Checkpoint 3 (the first
  real plan and report, committed as evidence), and T20 (skipped by its own licensed default). T22's
  reading is recorded and the row waits on the owner.

  **Blocked here, and the path each one needs:** T12 needs `.github/workflows/release.yml` +
  `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs`; T14–T16 need `gk-forge/tools/seedsmith/**` (T16 also
  `gk-data/packs/fusion/data/seed/passive-tree/**`); T18's remaining half is the seedsmith reader
  (`tools/seedsmith/seedsmith/briefkit/import_renames.py`) plus the owner's replacement strings for the
  real `import-renames.v1.json`; T19/T19b need `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/creatures/**`,
  `gk-data/packs/fusion/data/generated/**`, `gk-core/src/FusionRpg.Data/**`; T21 needs the downloaded USPTO export; T22 needs the
  owner's candidate-source ruling; T23 needs all of the above.

  **Closing readings (2026-09-23, at this lane's head):** `python -m pytest -q` in `gk-core/tools/ip-censor` →
  **218 passed**; `scripts/run-guards.ps1 -Tier ci` → **21 guards, 0 red**;
  `gk-core/scripts/guard-verification-boundaries.py` → OK; `Guard.Tests` → **593 passed, 0 failed**;
  `verify-change.ps1 -PlanOnly -Paths gk-core/tools/ip-censor/ipcensor/report.py` → the `ipcensor` lane.
  ⚠ **`verify-change.ps1 -Session ip-censor-2` could not be used on this lane:** it requires
  `tasks/sessions/ip-censor-2.json`, and `tasks/sessions/**` is outside the lane's allowed paths, so
  every run used `-AllowUnscoped`, which selects the same projects, guards and doc-citation checks and
  only skips the session-scope fence check. Grant `tasks/sessions/**` or pre-create the record.

  **The one design defect this lane found and fixed:** the gate enforced on the surface alone, so 44
  `pvz`/`dr-zomboss` hits under `gk-forge/tools/seedsmith/**` were enforced although neither group declares
  `generator-prompt` scope — all of them code comments or identifiers, owning no fix. IC-1b scopes `pvz`
  to player-facing surfaces only, so `Registry.enforces` now requires the surface **and** the mark's
  scope; the enforced set fell from 325 to 281, every one owned. See the T4 row and the ledger.

---

**Conventions for every task**

- `<sid>` is the implementing session's id (`ip-censor-<yyyymmdd>`, recorded at T0).
- `$PY` below means: `$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest` (the specs' own form).
  `$SS` means: `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest`.
- **Verification (plan D3).** Pass only mapped paths to
  `.\scripts\verify-change.ps1 -Paths <paths> -Session <sid>`. Today that is `tasks/**`,
  `.github/workflows/**`, `docs/**`, `gk-core/src/FusionRpg.Server/**`, `gk-core/src/FusionRpg.Data/**`,
  `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json`,
  `gk-core/tests/FusionRpg.Guard.Tests/**`, `gk-core/tests/FusionRpg.Data.Tests/**`, **and — as of the 2026-09-22
  addendum — `gk-forge/tools/seedsmith/**` (`seedsmith-trees` + the `seedsmith` pytest lane), `gk-data/packs/fusion/data/seed/**`,
  `gk-data/packs/fusion/data/generated/**` and `gk-data/packs/fusion/data/seed/passive-tree/**`** (TVB3.3/TVB4.6/TVB4.7 landed 2026-09-21;
  `scripts/guard-*.ps1` remains unmapped). Every other path runs its named focused command, and the
  ledger line lists it as unmapped. Never fall back to a broad suite. *Addendum 2026-09-22: this bullet
  listed the four newly-mapped roots as unmapped; the plan §13 table is the current reading.*
- **Contract, not population.** Tests assert envelopes, closed vocabularies (`Category`, `Surface`,
  `Remediation`, `Stage`, `Evidence`, `Bucket`, `source`), fixture contents, determinism and joins.
  No test asserts a hit count, a token count or a registry size over the real tree. Counts go in the
  ledger as readings.
- **Fixtures.** Real marks appear only under `gk-core/tools/ip-censor/tests/fixtures/**` (a `self_paths`
  member). Seedsmith tests use invented marks such as `Examplemark` (`gk-forge/tools/seedsmith/**` is an
  enforced `generator-prompt` surface). `gk-core/tools/ip-censor/ipcensor/*.py` carries no real mark: marks live
  in data.
- **Shared files.** Apply plan §8's clean-or-skip rule before editing any file another active session
  claims. A dirty shared file is skipped and recorded, never stashed.
- **Generated data.** Never hand-edit a row with generator provenance. The only route is generator
  change, regenerate, commit the pair.

---

## Phase 0 — Boundary

- [x] **T0 Session record.** *Depends:* owner approval of this plan. **Done 2026-09-22** (lane
  `ip-censor-1`; the runner-assigned lane id is the session id, superseding the `<program>-<yyyymmdd>`
  form this file's conventions assumed). The row's dependency is the owner's 2026-09-22 approval
  recorded in the plan status line, not a further approval.
  *Files:* `tasks/sessions/<sid>.json` (new).
  *Do:* run `/session-start`; claim `gk-core/tools/ip-censor/**`, `gk-data/packs/fusion/data/seed/ip-censor/**`,
  `tasks/ip-censor/**`, `tasks/ip-censor-plan.md`, `tasks/ip-censor-todo.md`, and the shared files of
  plan §8 per task as it starts (or all at once in `direct` mode unless the owner picks a worktree).
  Record the §8 crossings in `notes`.
  *Accept:* `python scripts/session-boundary-check.py --session <sid>` is clean for this session.
  *Verify:* `.\scripts\verify-change.ps1 -Paths tasks/sessions/<sid>.json -Session <sid>`.
  *Note (2026-09-22):* run the boundary check from the lane's own worktree — the script reads
  `<RepoRoot>/tasks/sessions`, so `-RepoRoot` at the main checkout cannot see an unmerged record.
  *Commit:* `ip-censor T0: session record`.

## Phase 1 — Foundation

- [x] **T1 Tool package, lockfile, wiring test, CI pytest step (`wiring` half 1).** *Depends:* T0.
  **Done 2026-09-22.** Note: the TVB0.3 precedent step is at `ci.yml:424-431` now (the row cited
  `:311-317`); the new step sits directly after it. `pyahocorasick`'s import name is `ahocorasick`
  (the distribution name is what `requirements.lock` pins), so `test_wiring.py` asserts the
  distribution version from the lockfile and imports `ahocorasick`.
  *Files:* `gk-core/tools/ip-censor/pyproject.toml`, `gk-core/tools/ip-censor/requirements.lock`,
  `gk-core/tools/ip-censor/ipcensor/__init__.py`, `gk-core/tools/ip-censor/tests/test_wiring.py`,
  `gk-core/tools/ip-censor/.env.example`, `.github/workflows/ci.yml`.
  *Accept:*
  - `pyproject.toml`: `requires-python = ">=3.11"`, exact pins `pyahocorasick==2.3.1`,
    `regex==2026.3.32`, `pytest==9.0.2` in a `dev` extra, `[tool.pytest.ini_options]` with
    `testpaths = ["tests"]`, `pythonpath = ["."]` (seedsmith's shape, `spec-wiring.md` §Tool shape).
  - `test_wiring.py` asserts each installed version equals its line in `requirements.lock` (read from
    the file, not restated in the test) and that `import ipcensor` works.
  - `.env.example` documents the `IPCENSOR_LLM_*` keys (`spec-suggest.md` §Configuration); no `.env`
    is committed.
  - `ci.yml` gains, after the tuning step (`ci.yml:311-317`), one step in the TVB0.3 form with
    `working-directory: gk-core/tools/ip-censor`: lockfile install, editable install, then
    `python -m pytest tests -q -p no:cacheprovider`, each followed by its exit check.
  *Verify:* `cd gk-core/tools/ip-censor; python -m pip install -r requirements.lock; python -m pip install -e . --no-deps`;
  `$PY gk-core/tools/ip-censor/tests/test_wiring.py -q`;
  `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,tasks/ip-censor-todo.md -Session <sid>`
  (selects `guard.workflows`, which proves the new step's exit checks). `gk-core/tools/ip-censor/**` unmapped
  until T13.
  *Commit:* `ip-censor T1: tool package, pinned lockfile and CI pytest step`.

- [x] **T2 `source` — tracked-tree reader.** *Depends:* T1. **Done 2026-09-22.** Reading: 12,856
  tracked paths, 12,832 scannable under the allowlist; the real-tree walk (which decodes every one)
  takes ~73 s — a reading, not an assertion. `locate()` takes a character offset into the
  CRLF-normalised text (the unit `regex` spans use), and a column is a character count so it matches
  an editor.
  *Files:* `gk-core/tools/ip-censor/ipcensor/source.py`, `gk-core/tools/ip-censor/tests/test_source.py`,
  `gk-core/tools/ip-censor/tests/fixtures/source/**`.
  *Accept (spec-source.md):*
  - `iter_files()` enumerates `git ls-files`, filters by an extension **allowlist** and an ignore list,
    and yields in sorted order; `self_paths` are passed in, never known to the module.
  - `SourceFile.locate(offset)` maps to 1-based `(line, column)` on CRLF-normalised text at offsets 0,
    a line start, across `\n`, and past EOF (throws).
  - A file that is not valid UTF-8 **throws** naming the path (A8); no fallback decode.
  - Determinism: two enumerations of a fixture tree give identical order and locations.
  - Real-tree smoke: the enumeration is non-empty, and every yielded file decodes (the A8 tripwire).
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_source.py -q`.
  *Commit:* `ip-censor T2: source reader with deterministic line index`.

- [x] **T3 `registry` — the pure parser.** *Depends:* T1. **Done 2026-09-22.** `parse_registry(files)` takes a mapping of file
  name -> JSON text (so an error names both the file and the key); `load_registry(directory)` reads the four
  `*.v1.json`. The boundary policy is parsed first because `minAliasLength` is a marks-validation input
  (IC-6) and lives in data.
  *Files:* `gk-core/tools/ip-censor/ipcensor/registry.py`, `gk-core/tools/ip-censor/tests/test_registry.py`,
  `gk-core/tools/ip-censor/tests/fixtures/registry/**`.
  *Accept (spec-registry.md):*
  - Parses `marks`, `scope-policy`, `boundary-policy`, `replacements` into the frozen dataclasses;
    every missing, empty or mistyped field throws naming the key and file.
  - Closed vocabularies: `Category` = {`franchise-mark`, `real-person`, `company-brand`}; a `title`
    category is rejected (IC-1). `Surface`, `Remediation`, `Stage`, `Evidence` equal their declared
    sets.
  - IC-6: an alias shorter than `minAliasLength` (read from `boundary-policy`, never a code constant)
    without its own non-empty scope is rejected; with a subset scope it is accepted; an alias scope
    wider than its group's is rejected.
  - IC-2: a group without `admission`, with `stage: "import"` + `evidence: "census"`, or without
    `confirmedBy`/`confirmedOn` is rejected.
  - Duplicate mark or a spelling under two groups is rejected; a boundary policy that names no
    separators (a `\b`-only value) is rejected.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_registry.py -q`.
  *Commit:* `ip-censor T3: registry parser with closed vocabularies and IC-2/IC-6 rules`.

- [x] **T4 Shipped registry files, surface classifier, remediation derivation.** *Depends:* T2, T3.
  **DONE 2026-09-23** (lane `ip-censor-2`, branch `cmdc/ip-censor-2`; part 1 landed 2026-09-22 in
  `ip-censor-1`). Part 2 ships the four authored files and the shipped-registry tests. Two findings
  came out of the real-tree reading and are recorded here:
  1. **`Registry.enforces` was missing its second half.** The gate enforced on the surface alone
     (`report.enforced_findings` asked `is_enforced(finding.surface)`), so a `pvz` or `dr-zomboss` hit
     in a `gk-forge/tools/seedsmith/**` file was *enforced* although neither group declares `generator-prompt`
     scope — 44 enforced findings with no owner, in code comments and identifiers
     (`zomboss_pattern_ids`, `ZombossPatterns.cs`). IC-1b is explicit that `pvz` is "in scope on
     player-facing surfaces only", and CP3's audit calls an enforced finding with no owner a
     classifier defect. Fixed in `registry.py`: `Registry.scope_for` / `Registry.enforces` require the
     surface **and** the mark's scope, and `report.enforced_findings` uses it. Reading: 6,818 findings,
     **281 enforced**, every one owned (273 identity-rename's player guide and locale catalogs, 4 its
     `default-commanders` row, 4 this program's T16).
  2. `gk-core/scripts/guard-generated-seed.py:117-124` reads only a top-level `_meta` (plan D8/§5), for that
     guard's owner. Carried forward from part 1.
  *Files:* `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json`, `scope-policy.v1.json`,
  `boundary-policy.v1.json`, `replacements.v1.json` (all new), `gk-core/tools/ip-censor/ipcensor/registry.py`,
  `gk-core/tools/ip-censor/tests/test_registry.py`.
  *Accept:*
  - `marks.v1.json` holds exactly the owner-confirmed day-one groups of plan D5: `pvz`,
    `crazy-dave`, `penny`, `dr-zomboss`, `overwatch`, with the scopes of `spec-registry.md`
    §Categories and surfaces (`pvz` only `player-name` + `player-prose`, its 3-character alias carrying
    its own scope) and `overwatch` scoped `player-name`, `player-prose`, `generator-prompt`.
    The test pins **this member list** (a closed vocabulary a person edits) and says why.
  - `replacements.v1.json` holds only the owner-authored pairs (IC-1b, R11): `pvz` /
    `Plants vs. Zombies` → `Fusion`; `Crazy Dave` → `the Garden Keeper`; `Penny` → `Hourbloom`;
    `Dr. Zomboss` → `the Rotwright`.
  - `scope-policy.v1.json` carries the enforced set {`player-name`, `player-prose`,
    `generator-prompt`} (IC-3), the path rules of the surface classifier (including
    `gk-data/packs/fusion/data/seed/narrative/**` and `docs/guide/**`), and `self_paths` classes 1–3 **plus**
    `tasks/ip-censor-plan.md` and `tasks/ip-censor-todo.md` in class 2 (plan D9).
  - The surface classifier is a pure function in `registry` (A10), shared by `census` and `scan`.
  - Remediation derivation recognises the three provenance shapes present in the tree (plan D8):
    top-level `_meta`, top-level `_provenance` with `promptVersion`/`model`, per-row `_provenance` or
    `promptVersion`. One fixture per shape yields `generator-owned`; the same file without provenance
    yields `authored`; a path under `gk-data/packs/fusion/data/seed/external-reference/**` yields `upstream-imported`.
  - The shipped registry parses; parsing it twice is byte-identical.
  - *Audit 2026-09-19 (plan D10).* The classifier gives every tracked root a surface. Source-code roots
    (`src/**`, `web/**/src/**/*.ts`/`*.tsx`, `tests/**`, `tools/**` except `gk-forge/tools/seedsmith/**`, which stays the enforced `generator-prompt` surface) are
    `code-identifier`; player surfaces are pure display files only (`*.po`, `docs/guide/**`,
    `gk-data/packs/fusion/data/seed/**/_registry/**` display registries, `gk-data/packs/fusion/data/seed/narrative/**`, rendered site pages). A
    fixture holding every identity-rename allow-list form (`WorldFactionKind.Zomboss`, `EmpireId.Dave`,
    `ZombossDeployEndpoints`, `commander:dave`, `drop.pvz.run`, `PVZRH`, `PvZ2`) yields **no enforced**
    finding.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_registry.py -q`. `gk-data/packs/fusion/data/seed/ip-censor/**` unmapped until T13.
  *Ledger:* report that `gk-core/scripts/guard-generated-seed.py:117-124` reads only a top-level `_meta`
  (plan §5), for that guard's owner.
  *Commit:* `ip-censor T4: day-one registry, surface classifier and remediation derivation`.

### Checkpoint 1 — Foundation
- [ ] `$PY gk-core/tools/ip-censor/tests -q` green from a clean install of the lockfile.
- [ ] The CI step from T1 is present and `guard.workflows` is green.
- [ ] The day-one registry rows match plan D5 exactly; no row lacks `confirmedBy`.

## Phase 2 — Readings

- [x] **T5 `census` — distinct-token census.** *Depends:* T4. **Done 2026-09-22** (the T4 part-1
  classifier is the dependency; the shipped registry only affects readings, not this module's contract).
  `census(files, registry)` takes the `Registry` rather than the spec sample's bare `BoundaryPolicy`,
  because each occurrence is also reported per surface and the classifier is registry policy. Token
  counts are a reading; the fixture counts are the only exact numbers asserted.
  *Files:* `gk-core/tools/ip-censor/ipcensor/census.py`, `gk-core/tools/ip-censor/tests/test_census.py`,
  `gk-core/tools/ip-censor/tests/fixtures/census/**`.
  *Accept (spec-census.md):*
  - Per token: `total`, `by_tree`, `by_surface`, dominant-casing `display`; sorted by
    `(total desc, token asc)`; byte-identical across two runs.
  - Tokenisation uses the registry boundary policy and `str.casefold()`; `demonstrate` never yields
    `demon`; `PVZ`, `PvZ`, `pvz` collapse to one token.
  - The boundary fixture (`PvZ融合版`, `pvz-fusion-almanac`, `PVZRH`, `drop.pvz.run`) classifies as
    the policy declares.
  - Shape assertions only: keys present, counts non-negative, `by_tree` sums to `total`.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_census.py -q`.
  *Commit:* `ip-censor T5: census over the tracked tree`.

- [x] **T6 `scan` — match, bucket, remediation.** *Depends:* T4 (part 1). (Parallel with T5.)
  **Done 2026-09-22.** Readings over the real tree with the fixture registry (the day-one set plus
  `overwatch`): 12,871 scannable files, **113 findings**, 49 of them inside `self_paths` classes — which
  is what makes the exclusion load-bearing. Full-tree wall time: **105.7 s** and **190.1 s** on two runs of
  the same commit, of which the read alone was 11.6 s / 31.3 s — the machine was shared with other lanes,
  so the ideal's 2,046 ms *matching-only* figure is not reproducible here. `fold()` gained an ASCII fast
  path (1:1 folding needs no per-character Python loop); the before/after full-tree numbers cannot be
  compared because the load differed by more than the change. Row 5 of spec-scan's boundary table is read
  as: the `pvz` token IS a hit, and its bucket follows the path's surface, so in a code path it is
  `code-identifier` — the fixture asserts exactly that. A `registry-self` bucket is reachable through a
  non-self registry file (`gk-data/packs/fusion/data/seed/**/_registry/**`), since the registry's own files are excluded
  outright; the fixture tree shows both.
  *Files:* `gk-core/tools/ip-censor/ipcensor/scan.py`, `gk-core/tools/ip-censor/tests/test_scan.py`,
  `gk-core/tools/ip-censor/tests/fixtures/scan/**` (including a fixture copy of the pre-fix
  `skill.command-def-t8-n0` node with its provenance, from `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:537-542`).
  *Accept (spec-scan.md):*
  - `pyahocorasick` automaton built once from the registry; longest-match-first; a named boundary
    function; never bare `\b`, never `.lower()`.
  - The seven boundary cases of spec-scan §Testing behave exactly as its table says.
  - One canonical fixture per `Bucket` lands in that bucket only; a PvZ hit in an architecture doc is
    `deliberate-identity`; in `docs/guide/**` it is `player-prose`; `{lead_antagonist}` yields nothing.
  - **Known-collision acceptance (A9):** the fixture node is reported as `bucket: "player-name"`,
    `remediation: "generator-owned"`, at its fixture line.
  - Self-exclusion: over the real tree, zero findings inside any `self_paths` class (a relationship,
    not a count of findings elsewhere).
  - Determinism: two runs byte-identical, ordered by `(path, line, column, mark)`.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_scan.py -q`.
  *Ledger:* the full-tree scan's wall time (a reading; the ideal measured about 2 s).
  *Commit:* `ip-censor T6: scan with boundary policy, buckets and remediation`.

- [x] **T7 `suggest` and the tool's one LLM client.** *Depends:* T6. **Done 2026-09-22.**
  `Suggestion` gains a `remediation` field (the row's "carried through unchanged" line needs it on the
  value); proposals are cached per distinct mark, so a mark hit 400 times is one model call. `llm.py`
  resolves env -> committed layer -> built-in and takes its transport as an injected seam, so the request
  shape is provable with a fake opener and no network. The authored-only path is proven never to reach
  `llm` at all (a monkeypatched `load_config`/`build_proposer` that raises if called).
  *Files:* `gk-core/tools/ip-censor/ipcensor/suggest.py`, `gk-core/tools/ip-censor/ipcensor/llm.py`,
  `gk-core/tools/ip-censor/tests/test_suggest.py`, `gk-core/tools/ip-censor/tests/fixtures/replacements.v1.json`.
  *Accept (spec-suggest.md):*
  - An authored pair wins and the stub proposer is not called.
  - A mark without a pair gets `source: "proposed"` and exactly `PROPOSAL_MARKER` in `note`; proposals
    are made per distinct mark.
  - A `code-identifier` finding or a `code-change` remediation gets `source: "none"` and the proposer is
    not called.
  - `remediation` is carried through unchanged; a raising proposer yields `source: "none"` with the
    error recorded.
  - `llm.py` reads `IPCENSOR_LLM_*` with env → committed default → built-in precedence; `propose=None`
    never touches it (a test makes it raise if called).
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_suggest.py -q`.
  *Commit:* `ip-censor T7: suggest with authored-first resolution and an injected LLM client`.

### Checkpoint 2 — Readings
- [ ] `$PY gk-core/tools/ip-censor/tests -q` green.
- [ ] Owner reads one sample finding per bucket (from a fixture run) and agrees with the bucketing.
  If the owner has not read it when T8 starts, T8 proceeds; any disagreement becomes a scope-policy
  row change later (authored data, reversible).

## Phase 3 — Curation and composition

- [x] **T8 `curate import` and the USPTO adapter.** *Depends:* T5. **DONE 2026-09-23** (lane
  `ip-censor-2`; part 1 landed 2026-09-22 in `ip-censor-1`). Part 2 ships the authored
  `gk-data/packs/fusion/data/seed/ip-censor/_registry/import-filter.v1.json` and the test that it satisfies the schema the
  module enforces and still names the adapter's own pinned format. `tasks/ip-censor/curate/` is now in
  the lane's allowed paths (T17 writes a candidate file there). **STILL NOT PROVED, and T21's first
  step:** the adapter's element map (`ROOT_ELEMENT`, `ELEMENT_MAP`) and the filter's Nice classes,
  status codes and goods terms are pinned but **UNVERIFIED against a real export** — none is
  downloaded; T21 must confirm or correct them against the download. `admit`/`reconfirm` (T9) are
  done. The filter's values are a starting point tuned against candidate output at T21; a wrong value
  is a one-line data change, which is why they live in the authored file.
  *Files:* `gk-core/tools/ip-censor/ipcensor/curate.py`, `gk-core/tools/ip-censor/ipcensor/datasets/uspto.py`,
  `gk-core/tools/ip-censor/tests/test_curate.py`, `gk-core/tools/ip-censor/tests/fixtures/curate/**`,
  `gk-data/packs/fusion/data/seed/ip-censor/_registry/import-filter.v1.json`.
  *Accept (spec-curate.md):*
  - `import` applies only the authored filter; a filter missing a key throws naming it.
  - Each candidate has `stage: "import"`, `evidence: "dataset"`, and a `source` naming dataset id,
    version and record id; `decision`, `confirmedBy`, `scope` are null.
  - The adapter pins the export format it was written against and refuses an unknown one.
  - Candidate files go only under `tasks/ip-censor/curate/`; byte-identical across two runs.
  - Fixtures use invented marks.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_curate.py -q`.
  *Commit:* `ip-censor T8: curate import with the USPTO adapter and an authored filter`.

- [x] **T9 `curate reconfirm` and `curate admit`.** *Depends:* T7, T8. **Done 2026-09-22** (its files are
  all under `gk-core/tools/ip-censor/**`, so this row closes inside the fence). `registry.render_marks` — the
  serializer this row's acceptance names — landed with it, because T3/T4 shipped the parser without one.
  `Candidate` gained `confirmedOn`, `remediation` and `recheck` beyond the spec's shape: an `Admission`
  needs a date, an `AliasGroup` needs a remediation, and a re-check must not overwrite a row's admitting
  stage. A candidate's `category` is `None` until a person sets it — the model must never set a category,
  so the import stage takes it from the authored filter and the reconfirm stage leaves it to `admit`.
  The `--no-model` FLAG spelling lands with T10's CLI; the module behaviour it names (no proposer, census
  evidence only) is what this row tests. `admit`'s real target (`marks.v1.json`) is written by T21/T22's
  rounds, not here.
  *Files:* `gk-core/tools/ip-censor/ipcensor/curate.py`, `gk-core/tools/ip-censor/tests/test_curate.py`,
  `gk-core/tools/ip-censor/tests/fixtures/curate/**`.
  *Accept:*
  - `reconfirm --no-model` yields census candidates for in-scope tokens not in the registry and a
    re-check entry for rows the census still finds; the proposer is not called.
  - With a stub model, proposals carry `evidence: "model-proposal"` and the model id; a raising model is
    recorded, not fatal.
  - `admit` refuses a row without `decision`, `confirmedBy` or `scope`; writes through the `registry`
    serializer and re-parses; a re-checked import row keeps `stage: "import"` and gains
    `reconfirmedOn`.
  - `admit` writes only `marks.v1.json`.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_curate.py -q`.
  *Commit:* `ip-censor T9: curate reconfirm and admit`.

- [x] **T10 `report` — composition root, CLI, plan and report writers.** *Depends:* T5, T6, T7, T9.
  **DONE 2026-09-23** (lane `ip-censor-2`; part 1 landed 2026-09-22 in `ip-censor-1`). The one
  acceptance line that could not pass as written now passes with the shipped registry: the module
  entry point is invoked as a subprocess with the root resolved from the git working tree (no
  `--root`) and exits 0 — the erratum ask is withdrawn, `gk-data/packs/fusion/data/seed/ip-censor/_registry/**` is in this
  lane's allowed paths. The fixture-registry subprocess check and the missing-registry exit 2 stay.
  `report.enforced_findings` gained its missing second half with T4's fix (an enforced surface **and**
  the mark's scope), and the exit-code tests now cover an out-of-scope hit on an enforced surface.
  `curate.candidate_from_dict` landed here because the `admit` verb reads a candidate file back.
  *Files:* `gk-core/tools/ip-censor/ipcensor/report.py`, `gk-core/tools/ip-censor/ipcensor/cli.py`,
  `gk-core/tools/ip-censor/tests/test_report.py`, `gk-core/tools/ip-censor/tests/test_wiring.py`.
  *Accept (spec-report.md):*
  - Verbs: `census`, `scan`, `suggest` (`--authored-only`), `curate import|reconfirm|admit`, `all`,
    `registry-check`.
  - Plan JSON: `schema_version == PLAN_SCHEMA_VERSION`, `generated_from_commit`, `registry_version`,
    `model` (null in `--authored-only`), findings grouped by file with every required field including
    `remediation`; a `--by remediation` view loses no finding; sorted keys, LF, byte-stable excluding
    `generated_at`.
  - Exit codes: 0 with findings by default; non-zero with `--fail-on enforced` and an enforced
    finding; 0 with `--fail-on enforced` when only report-only buckets are present.
  - `--authored-only` succeeds with the proposer patched to raise.
  - Class-4 self-exclusion: a plan written under `tasks/ip-censor/` is not a finding source on the
    next scan.
  - `test_wiring.py` gains: `python -m ipcensor.report registry-check` exits 0 on the shipped registry.
  - *Audit 2026-09-19.* `report` resolves the scanned tree and the registry from
    `git rev-parse --show-toplevel` (or an explicit `--root`), never the working directory: a scan
    started inside `gk-core/tools/ip-censor` enumerates the whole repository (test with a fixture repo and a
    nested working directory). Output paths such as `--plan` resolve against that root.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_report.py gk-core/tools/ip-censor/tests/test_wiring.py -q`.
  *Commit:* `ip-censor T10: report composition root, CLI and versioned plan`.

### Checkpoint 3 — First real plan
- [x] Run `$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report all --authored-only --plan tasks/ip-censor/plan.json --report tasks/ip-censor/report.md`. **Done 2026-09-23:** 1,260 files, 6,818 findings, model `(none)`, registry `v1`.
- [x] `report.md` shows `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` as `player-name` / `generator-owned`, and the player-facing
  PvZ and lead-name hits as enforced; citations in `docs/research/**` as `docs-prose-citation`. **Checked in the committed plan:** command.json `:538`/`:539` are `player-name` / `generator-owned`; `docs/research/**` is `docs-prose-citation` (549 findings); every enforced finding is player-name/player-prose.
- [x] Commit the plan and report as evidence (`tasks/ip-censor/**` is self-excluded and maps to
  `session-and-program-records`), with the enforced-bucket reading in the ledger:
  `ip-censor CP3: first plan and report (evidence)`. **Committed with T10.** Reading: 6,818 findings, enforced = **281** (player-name 8, player-prose 273) after T4's scope fix.
- [ ] Owner reviews `report.md`. **Not reviewed when T11 starts, so T11 proceeds** (the CI step is
  advisory and reversible); the review is the owner's and is carried into T23's readiness file.
- [x] *Audit 2026-09-19 (plan D10).* Every enforced finding in `report.md` names its owner: an
  identity-rename task id, a generator task here, or a curate row. An enforced finding with no owner
  is a classifier defect, fixed by a `scope-policy.v1.json` path rule before T12 lands. **Closed by
  T4's enforcement fix, not by a path rule:** with `Registry.enforces`, the 44 `gk-forge/tools/seedsmith/**`
  hits of `pvz`/`dr-zomboss` leave the enforced set (neither group scopes `generator-prompt`; IC-1b
  scopes `pvz` to player-facing surfaces only). The remaining 281 are owned — 277 by identity-rename
  (R9's player guide and locale catalogs plus its `default-commanders.v1.json` row) and 4 by this
  program's T16 (IC-4.1).

## Phase 4 — Gate wiring

- [x] **T11 Advisory CI scan.** *Depends:* T10. **Done 2026-09-23** (lane `ip-censor-2`). The step
  runs from the repository root and writes to `tasks/ip-censor/ci-scan.json`, which is uploaded with
  `actions/upload-artifact@v4` under `if: always()` so the plan is inspectable even when the step
  throws. `guard.workflows` passes: the command is not one of the prefixes `WorkflowExitCheckTests`
  recognises yet, so T12's prefix addition is still the change that makes the exit check itself
  guarded — the check is present here regardless. It lands after T13 because the unmapped
  `gk-data/packs/fusion/data/seed/ip-censor/**` made `guard.workflows` red for any path until T13 registered the lane.
  *Files:* `.github/workflows/ci.yml`.
  *Accept:*
  - A step after T1's pytest step runs, **from the repository root** (audit 2026-09-19: the package is
    already installed by T1's step; a `gk-core/tools/ip-censor` working directory would scan only the tool),
    `python -m ipcensor.report scan --format json` into `tasks/ip-censor/ci-scan.json` on the runner
    (never committed) and uploads it with `actions/upload-artifact`.
  - The command's exit is checked; it is non-zero only on a tool crash (a code defect), never on a
    finding. No `--fail-on` flag appears in `ci.yml` (IC-3).
  *Verify:* `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,tasks/ip-censor-todo.md -Session <sid>`.
  *Commit:* `ip-censor T11: advisory scan in CI`.

- [ ] **T12 Release gate step, checklist line, exit-check guard, enforcement row.** *Depends:* T10.
  *Files:* `.github/workflows/release.yml`, `docs/runbook/release-prove.md`,
  `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs`, `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:*
  - `release.yml` gains a step named `IP release gate (ip-censor, IC-3)` after
    `Unit tests (pre-publish)` (`:40`) and before `Prepare injector refs` (`:236`; this said `:59`
    before this commit's own step landed at `:212`), so before
    `Publish player pack` (`:258`; said `:81`): lockfile install, editable install, then
    `python -m ipcensor.report scan --format json --fail-on enforced --authored-only`, each followed by
    `if ($LASTEXITCODE -ne 0) { throw … }` (plan D4). The installs run in `gk-core/tools/ip-censor`; the scan
    runs from the repository root (audit 2026-09-19). *Added 2026-09-23:* `--authored-only` is not in
    this row's or `spec-report.md`'s command line, but it is required by the same spec's
    §Success criteria — see the erratum there; without it the gate blocks on a model round-trip per
    unauthored mark.
  - `release-prove.md` §"Before tagging" (`:5`) gains one line with the same command.
  - `WorkflowExitCheckTests.TestCommandPrefixes` (`:17-22`) gains `python -m ipcensor.report scan `,
    and its planted-workflow test gains a missing-check case for it.
  - `enforcement-registry.v1.json` gains an `invariants` row for "an enforced IP finding blocks a
    release", sourced to `docs/architecture/ip-censor-map.md` (release gate), naming the release step
    in its `unguardableReason` (no per-change guard, by IC-3).
  *Verify:* `.\scripts\verify-change.ps1 -Paths .github/workflows/release.yml,docs/runbook/release-prove.md,gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs,gk-core/scripts/enforcement-registry.v1.json,tasks/ip-censor-todo.md -Session <sid>`
  (if a path is reported unmapped, drop it from the list, run its named check, and ledger it).
  *Commit:* `ip-censor T12: release gate before publish, checklist line and guard`.
  **PARTIAL 2026-09-23 (lane `ip-censor-3`): three of the four files landed; the guard test is a DENIED
  PATH.** `release.yml`'s gate step (`:212`) and its findings step (`:224`), the `release-prove.md:8`
  checklist line and the `ip-enforcement-registry` invariants row are in. **Blocked, exactly:**
  `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` cannot be edited — the orchestrator's
  pipeline hook refuses it as a protected guard file ("protected pipeline file (guards, verify,
  ledger script, hooks, CI)"), on both the `TestCommandPrefixes` addition and the planted-workflow
  case. The brief's protected-grant list names `.github/workflows/release.yml`,
  `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json` and
  `scripts/run-guards.ps1`, not `gk-core/tests/FusionRpg.Guard.Tests/**`. Until that path is granted, the new
  command is not itself guarded — the exit check IS present in `release.yml`, but nothing catches a
  later edit that drops it. The row stays open on that one line.
  **Gate reading (the printed reading, at HEAD `4d6993b5`):**
  `python -m ipcensor.report scan --format json --fail-on enforced --authored-only` → **exit 1**;
  **7,119 findings in 1,243 files; 111 enforced in 42 files** (`player-name` 7, `player-prose` 60,
  `generator-prompt` 44), `model: None`. IC-4.1's target reads
  `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538,539` (`Overwatch`, `player-name`, enforced), plus the
  same two lines in `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json`.
  *Finding (routed, ci.yml is outside this lane's fence):* see the `T11` row below.

- [x] **T13 `wiring` half 2 — the `ipcensor` pytest lane.** *Depends:* T10; **external:** TVB3.1,
  TVB3.2 — **LANDED 2026-09-22** (`tasks/test-verification-boundary-todo.md:135,139`, both `[x]`; the
  registry's Python runner projects are `gk-core/scripts/verification-boundaries.v1.json:68-76`). This task
  **no longer waits on anything** (plan §13). **Done 2026-09-23** (lane `ip-censor-2`). The registry
  schema is 5 at this head, not the 4 the row names, and `level` is derived: a boundary carrying
  `testFiles` is `focused`, so the one boundary is stored as `focused` even though its paths cover the
  whole tool. `testFiles` is the D4 derivation — the union of the test files that import each
  `ipcensor.*` module (7 files), plus `test_wiring.py`, which imports the package itself and is the
  project-level install/lockfile test; the union alone would have dropped it. This runner was also
  **required** to make the tree green: the guard's completeness walk failed on `gk-data/packs/fusion/data/seed/ip-censor/**`
  as an unmapped enforced root the moment T4/T8 landed the registry files, and it is why T13 lands
  before T11 here.
  *Files:* `gk-core/scripts/verification-boundaries.v1.json`.
  *Accept (spec-wiring.md half 2):*
  - One project `ipcensor` with `runner: "pytest"`, `root: "gk-core/tools/ip-censor"`, `tests: "tests"`, in the
    schema TVB3.1 publishes; one owner boundary `ip-censor-tool` over `gk-core/tools/ip-censor/**` and
    `gk-data/packs/fusion/data/seed/ip-censor/**`, with `testFiles` derived from which test file imports each module (D4
    rule), in one contiguous block at the end of `boundaries`.
  - `.\scripts\verify-change.ps1 -Paths gk-core/tools/ip-censor/ipcensor/report.py -Session <sid> -PlanOnly`
    exits 0 and names the `ipcensor` lane.
  - TVB3.3's `CiPytestWiringTests` covers the new project (T1's step already has
    `working-directory: gk-core/tools/ip-censor`). No `knownRed` entry.
  *Verify:* `python gk-core/scripts/guard-verification-boundaries.py`;
  `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,gk-core/tools/ip-censor/ipcensor/report.py -Session <sid>`.
  *Commit:* `ip-censor T13: ipcensor pytest verification lane`.

### Checkpoint 4 — Gate wired
- [ ] `guard.workflows` green over both workflows.
- [ ] A local run of the release step's command on the current tree exits non-zero with the enforced
  findings listed (expected until identity-rename and the IC-4 fixes land); the reading is ledgered.
- [ ] T13 open or closed is recorded; if open, the remaining unmapped paths are named.

## Phase 5 — Avoid-list and IC-4.1 (may start after T4)

- [ ] **T14 `seedsmith.briefkit.avoid_list`.** *Depends:* T4.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py`,
  `gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py`, `gk-forge/tools/seedsmith/tests/fixtures/avoid_list/**`.
  *Accept (spec-avoid-list.md):*
  - `load_avoid_terms()` returns every alias whose group scope includes `player-name` or
    `player-prose`, casefold-unique and sorted; a `code-identifier`-only group is absent; a short alias
    with its own scope is included.
  - Throws naming the key on a missing `groups` or `scope`; no import of `ipcensor`.
  - `render_avoid_line(())` returns an empty string; two renders are byte-identical.
  - Fixtures use invented marks only.
  *Verify:* `$SS gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py -q`. `gk-forge/tools/seedsmith/**` unmapped
  until TVB3.3.
  *Commit:* `ip-censor T14: shared seedsmith avoid-list helper`.

- [ ] **T15 Uniques brief adopts the avoid line and drops its franchise citation.** *Depends:* T14.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py`,
  `gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py`.
  *Accept:*
  - The uniques system text no longer names a franchise (`gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:284`, "a Diablo-style unique
    item"); style is carried by the adapter's own exemplars.
  - The rendered uniques brief (fixture registry) contains the avoid line, and no fixture
    `franchise-mark` spelling appears outside that line.
  - If the uniques pipeline records a prompt version, it is bumped; if it records none (none found in
    `adapters/items/uniques/` on 2026-09-19), the ledger says so. No uniques row is regenerated: no
    shipped uniques row is a finding.
  *Verify:* `$SS gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py -q` and the uniques adapter's own
  test files (named in the ledger).
  *Commit:* `ip-censor T15: uniques brief carries the avoid-list and cites no franchise`.

- [x] **T16 Tree brief adopts the avoid line; `--node` selector; regenerate the Overwatch node (IC-4.1).**
  *Depends:* T14, T6 (scan for the post-check). *Environment:* the local model endpoint seedsmith uses.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py`,
  `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py`
  (only if the selector needs it), the nodegen tests that cover brief and CLI,
  `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json`, `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json`.
  *Do, in order, all in one commit (plan D6):*
  1. `render_brief` (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py:114`) prints the IP avoid line as a separate line from
     `Avoid entirely:` (`:157`); `PROMPT_VERSION` (`:57`) moves from `tree-language/3` to
     `tree-language/4`.
  2. `trees generate` gains `--node <id>` (`report/cli.py:2985`), restricting `--supersede` to that
     subject; without `--node`, behaviour is unchanged.
  3. `python -m seedsmith trees generate --tree command --dry-run` first: confirm the `--write`
     precondition and that only `skill.command-def-t8-n0` is selected.
  4. `python -m seedsmith trees generate --tree command --node skill.command-def-t8-n0 --write --supersede`.
  5. `python -m ipcensor.report scan --tree data --bucket player-name` reports no `overwatch` finding
     under `gk-data/packs/fusion/data/seed/passive-tree/**`; if the new name is another registry mark, re-run step 4.
  *Accept:*
  - The regenerated node carries `promptVersion: "tree-language/4"`; its `nameKey` is the generator's
    own derivation (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:665`), not typed by hand; the prior row sits under `supersededRecord` in the
    ledger (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:462`).
  - Tests: the brief contains the avoid line (fixture registry, invented mark); `--node` restricts a
    supersede run to one subject (fixture ledger via `--ledger-path`); without `--node` the old
    behaviour holds.
  - Every other node in `command.json` is unchanged (diff shows only that node and the provenance
    bookkeeping).
  *Verify:* `$SS <nodegen brief and CLI test files> -q`; the scan in step 5; `git diff --stat` limited to
  the files above. `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/passive-tree/**` unmapped (TVB3.3, TVB4.7).
  **DONE 2026-09-24 (mega-merge QC fix cycle 9).** Resumed the four dead opencode lanes' work
  (helper + fixture tests recovered from branch `opencode/ipc-3d-staged`, commit `f4769a660`).
  - Step 1: `render_brief` prints the IP avoid line as its own line, `PROMPT_VERSION` →
    `tree-language/4`.
  - Step 2: `trees generate --node <id>` restricts generation to one subject; without it behaviour
    is unchanged; an unknown id is refused by name (both dry-run and write).
  - Step 3/4: dry-run confirmed `totalSubjects: 1`, then the real regeneration ran through the
    generator's supersede path. Node `skill.command-def-t8-n0` is now
    **`Structural Integrity Protocol`** (`tree.node.structural-integrity-protocol`,
    `promptVersion: tree-language/4`); its `nameKey` is the generator's own derivation; the prior
    row (`Overwatch Protocol`) sits under `supersededRecord`. Exactly one ledger row and one node
    changed; every other `command` node is byte-identical.
  - Step 5: scan `--tree data --bucket player-name` reports **no `overwatch` finding in
    `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json`** — the live generator output is clean.
  - ⚠ **Real defect found and fixed during step 4 (the reason all four prior attempts could not
    land this):** the first `--node` implementation trimmed `plan.already_done` too, so the emitted
    seed document was rebuilt from one record and `command.json` shrank from 40 nodes to 1. `--node`
    must narrow **generation**, never the REPLAY set (`already_done`) that keeps the document whole;
    fixed in `plan_run` with a regression test
    (`test_only_node_leaves_the_other_rows_replayable_not_generated`).
  - **Residual (accepted by design, not a T16 miss):** the *ledger* still carries `Overwatch` twice
    under `command:skill.command-def-t8-n0`'s `supersededRecord` — `record_superseded` **requires**
    the prior row be preserved ("struck through in place", spec-tree-review §8), and the plan's own
    risk table (`tasks/ip-censor-plan.md:301`) anticipates exactly this ("T16 commits the ledger
    with the row"). Step 5's target — the live node — is clean. A run-ledger is machine bookkeeping,
    never a player surface; if the release gate should stop counting it, that is a
    `scope-policy.v1.json` classifier change (owner-gated enforced set), not a T16 edit.
  - *Evidence:* `python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/ gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py -q` → **589 passed, 27 subtests**; scan step 5 above.
  *Files:* `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py`,
  `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py`,
  `gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py`, the nodegen/briefkit tests,
  `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json`, `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json`.
  *Commit:* `ip-censor T16: tree brief avoid-list and regenerate skill.command-def-t8-n0 (IC-4.1)`.
  **DEFERRED 2026-09-24 (owner: resume later):** four opencode lanes died on this row (3b staged-then-destroyed by a manager cleanup defect, 3c blocked, 3d failed after staging the avoid_list helper, 3e dead-empty at 12 turns — runtime too flaky). Staged helper + tests preserved on branch `opencode/ipc-3d-staged` (commit `f4769a660`); T16 REPORT prose (nodegen design, regen commands) in `.claude/opencode-agents/agents/ipc-3b/result.json`. Resume needs a shelled runtime.
  *Commit:* `ip-censor T16: tree brief avoid-list and regenerate skill.command-def-t8-n0 (IC-4.1)`.

### Checkpoint 5 — IC-4.1 closed
- [ ] The release-gate reading shows no `overwatch` finding under `gk-data/packs/fusion/data/seed/passive-tree/**`.
- [ ] `$SS gk-forge/tools/seedsmith/tests -q` green for the touched areas (named test files, not the whole tree).

## Phase 6 — IC-4.2 `Jackson*` (may start after T5)

- [x] **T17 Trace every entry point and player-visible surface.** *Depends:* T5. **Done 2026-09-23**
  (lane `ip-censor-2`). The trace is `tasks/ip-censor/jackson-trace.md`, the proposal is
  `tasks/ip-censor/curate/jackson-candidates.json`. Four readings worth carrying forward:
  (1) the full name `Michael Jackson` enters our tree at **one** place — the dump's `flavorIntroduce`
  (`_dump/almanac/zombie.json:134,218`, and `迈克尔·杰克逊` at `:217`) — and appears **nowhere** in the
  almanac export, whose `Michael …`/`Jackson Worldwide` strings are display names and one boss label;
  (2) the blast radius is **74 files** (19 with the id in their path), not the nine species the row
  reasoned about — the id also reaches item sets, trophies, actions, motifs and themes;
  (3) the name reaches the player through the **host game's `types` table**, never through an RPG
  name field; (4) with the shipped scope policy the whole family is **report-only** (zero enforced
  findings), so IC-4.2 is closed by T19's import-output test exactly as `ip-censor-map.md:132` says.
  Three of the row's citations had drifted and are re-anchored in the trace (§5), including
  `gk-core/src/FusionRpg.Server/Program.cs:1423-1445`, which now holds the PvzActivity section.
  *Files:* `tasks/ip-censor/jackson-trace.md` (new, evidence; `self_paths` class 3),
  `tasks/ip-censor/curate/jackson-candidates.json` (new).
  *Accept:*
  - Every site where upstream text naming the real person enters the corpus, cited file:line: at
    least the creature dump's flavor text (`gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:134,218`),
    the seedsmith creature adapters that read it (`adapters/creatures/family/extract.py:61-65`,
    `generate_motifs.py:45`, `generate_themes.py:94`, and any other reader found), the almanac export
    (`pvz-fusion-almanac-3.6.1.json:5247,5677,5772`) and its endpoint (`gk-core/src/FusionRpg.Server/Program.cs:1423-1445`), and the
    display-name source (`RpgStore.AlmanacSeed.cs:474`).
  - Every derived artifact classified as **player-visible name**, **player-visible prose**, or
    **identifier**: species ids (`species/_index.json:382-387`), species rows and traits
    (`species/zombie/undead.json:2290`, `performer-undead.json:75,80`), `gk-data/packs/fusion/data/generated/creatures/*Jackson*.json`,
    action and recipe seeds that carry the ids.
  - A decision line on T20: does any upstream name reach a player through the server import path?
  - The candidate file proposes a `real-person` group (for example `michael jackson`) for the owner's
    decision in T22, with `evidence: "census"`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths tasks/ip-censor/jackson-trace.md,tasks/ip-censor/curate/jackson-candidates.json,tasks/ip-censor-todo.md -Session <sid>`.
  *Commit:* `ip-censor T17: trace the Jackson family entry points and surfaces`.

- [ ] **T18 The authored rename map, its validation, and its seedsmith reader.** *Depends:* T17, T3.
  **PART 1 DONE 2026-09-23 (lane `ip-censor-2`): `registry.py` half.** `parse_import_renames` /
  `load_import_renames` / `IMPORT_RENAMES_FILE` and their tests landed, on fixture pairs — the row's own
  default. The parser validates the shape (`schemaVersion`, required `names` and `ids` sections, every
  pair carrying `confirmedBy`/`confirmedOn`), rejects a duplicate `match`, a pair that maps a name to
  itself, and two pairs claiming the same replacement, and lets `ids` be present-but-empty because
  T19b fills it. **PART 2 OUTSIDE THIS LANE'S FENCE:** the seedsmith reader
  (`tools/seedsmith/seedsmith/briefkit/import_renames.py` + its test) needs `gk-forge/tools/seedsmith/**`.
  **AND the real file cannot be authored here:** its keys are the owner's replacement strings
  (principle 4 — this program never invents a replacement), so
  `data/seed/ip-censor/_registry/import-renames.v1.json` lands with the owner's confirmations and
  IC-4.2 stays open. T17 put the group's *shape* to the owner as a candidate
  (`tasks/ip-censor/curate/jackson-candidates.json`); the strings are still the owner's.
  *Owner input:* the replacement strings. `suggest` may propose them (marked
  `proposed — needs owner confirm`); only owner-confirmed pairs enter the file.
  *Files:* `data/seed/ip-censor/_registry/import-renames.v1.json` (new), `gk-core/tools/ip-censor/ipcensor/registry.py`,
  `gk-core/tools/ip-censor/tests/test_registry.py`, `tools/seedsmith/seedsmith/briefkit/import_renames.py` (new),
  `tools/seedsmith/tests/test_briefkit_import_renames.py` (new).
  *Accept:*
  - The file lives in `self_paths` class 1 (its keys are the real names); each pair carries
    `confirmedBy` and `confirmedOn`; `registry.py` validates it and throws on a pair without them.
  - The seedsmith reader applies the map to a text value deterministically (exact, boundary-anchored,
    case-mapped), reads the data file only (no `ipcensor` import), and throws on an unknown shape.
  - Tests use invented names in fixtures.
  *Verify:* `$PY gk-core/tools/ip-censor/tests/test_registry.py -q`; `$SS tools/seedsmith/tests/test_briefkit_import_renames.py -q`.
  *Commit:* `ip-censor T18: authored import-time rename map and its reader`.

- [ ] **T19 Apply the map in the creature adapters; regenerate the derived trees.** *Depends:* T18
  (with owner-confirmed pairs). *Environment:* the local model endpoint, for the adapters that call it.
  *Files:* the creature-adapter readers T17 named (under `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/`),
  their tests, a new import-output test, and the regenerated `gk-data/packs/fusion/data/seed/creatures/**` and
  `gk-data/packs/fusion/data/generated/creatures/**` rows T17 classified as player-visible.
  *Do:* apply the map where the dump text is read; re-run the affected generation steps and then the
  full downstream chain (species generation, build plan, fusion recipes and any `--check` generator that
  reads species rows), per the chain T17 recorded; commit generator change and outputs together.
  *Accept:*
  - A test over the adapters' import output asserts that no key of the rename map survives in a
    player-visible name or prose field (the map's done-when, `ip-censor-map.md:132`). Species ids are
    not in this test **yet**: T19b re-keys them and extends the same test to id fields (audit
    2026-09-19: was "excluded by gate G1's default", which the owner's yes superseded).
  - Every generator `--check` that reads these trees passes (`dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check`,
    `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`, and the others T17 listed).
  *Verify:* `$SS <adapter test files> -q`; the `--check` commands above. `gk-data/packs/fusion/data/seed/creatures/**`,
  `gk-data/packs/fusion/data/generated/**` unmapped (TVB4.6, TVB4.7).
  *Commit:* `ip-censor T19: apply the rename map at creature import and regenerate (IC-4.2)`.

- [ ] **T19b Re-key the `Jackson*` species ids (owner answer to gate G1, 2026-09-19).** *Depends:* T17
  (its id list and its schema sweep), T18, T19. *Audit 2026-09-19: moved here from an appendix after the
  ledger and completed to the plan standard (files, exact verify, commit, checkbox).*
  **Why:** the owner chose to rename the ids themselves, not only the names players see. Species ids are
  persisted in saves (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs:73`) and are the host game's own
  type names in the almanac dump (`gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:225`), so this is the
  program's one irreversible step, and the **only** save migration in either this program or
  identity-rename (plan §6).
  *Files:* `data/seed/ip-censor/_registry/import-renames.v1.json` (`ids` section),
  `gk-core/tools/ip-censor/ipcensor/registry.py`, `gk-core/tools/ip-censor/tests/test_registry.py`; the species-id
  derivation T17 names (seedsmith creature adapters and/or `gk-forge/tools/CreatureSpeciesGen/**`) and its tests;
  the regenerated `gk-data/packs/fusion/data/seed/creatures/**` and `gk-data/packs/fusion/data/generated/creatures/**` rows;
  `src/FusionRpg.Data/Sqlite/Migrations/JacksonSpeciesIds.cs` (new), its one call site in
  `RpgStore.Init` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`), the host loader that injects the map;
  `tests/FusionRpg.Data.Tests/Migrations/JacksonSpeciesIdsTests.cs` (new); this todo.
  *Do:*
  1. Extend the authored map with an `ids` section: old id → new id for every `Jackson*` species T17
     listed, each pair with `confirmedBy`/`confirmedOn` (owner-confirmed strings, as T18). A new id that
     already exists anywhere in the corpus is a load rejection.
  2. **Seed side — generator, never a JSON edit.** The species-id derivation reads the `ids` section and
     emits the new id; then re-run the whole downstream chain T17 recorded (species generation, build
     plan, fusion recipes, every `--check` generator that reads species ids) and commit generator change
     and outputs together. Each re-keyed row keeps its `gameTypeId`.
  3. **Host link.** The importer maps the host's type name and `gameTypeId` to the new id. The host's
     `types` table (`RpgStore.AlmanacSeed.cs:474`) and the dump are read, never written.
  4. **Save side — one migration in `FusionRpg.Data`**, on the `Migrations/ShardRungs.cs` precedent
     (idempotent re-key called from `RpgStore.Init`): re-key every stored reference in **one
     transaction**; the target tables come from a live-schema sweep of text columns (T17's list is the
     cross-check, not the source); where a row with the new id already exists, refuse and roll back
     (never merge silently).
  5. **Backup first.** Before the first write, and only when an old id is present, the migration takes a
     backup through an injected seam whose file implementation copies the store once with a named suffix
     (the `LegacyMonoMigrator.cs` `BakSuffix` precedent) and logs the path. A failed backup aborts with no
     write. A clean or already-migrated store takes no backup and writes nothing.
  *Accept:*
  - An **in-memory** store (`testing-standard.md` R1) seeded with an old id in every species-id column the
    sweep finds migrates; afterwards the sweep finds no old id in any text column (a contract over the id
    set, not a row count).
  - Running the migration a second time changes nothing and requests no backup (idempotent).
  - A backup seam that throws leaves the store byte-for-byte unchanged (in memory; no temp file). A real
    file-copy test is a file-semantics case (R2) and needs an owner-approved baseline line (R4); default:
    not added, and the ledger says so.
  - A pre-existing new id makes the migration refuse and roll back.
  - The import of the almanac dump yields the new ids, and each still resolves to its host `gameTypeId`.
  - T19's import-output test is extended to species ids: no key of the map's `ids` section survives in
    any id field of the generated trees.
  - `guard-dal.ps1` passes (SQL stays in `FusionRpg.Data`); the host injects the map, Core reads no file.
  *Verify:* `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Data/Sqlite/Migrations/JacksonSpeciesIds.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs,tests/FusionRpg.Data.Tests/Migrations/JacksonSpeciesIdsTests.cs,tasks/ip-censor-todo.md -Session <sid>`
  (`data-fallback`); `.\scripts\guard-dal.ps1`; `$PY gk-core/tools/ip-censor/tests/test_registry.py -q`;
  the generator `--check` commands T19 names. `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `gk-forge/tools/seedsmith/**`
  are unmapped (TVB4.6, TVB4.7, TVB3.3) and named in the ledger.
  *Before the first real run:* the owner's live save is migrated only by booting a build that contains
  this task; confirm the backup file exists afterwards and record its path in the ledger.
  *Commit:* `ip-censor T19b: re-key the Jackson species ids with a backed-up idempotent migration (IC-4.2)`.

- [x] **T20 Apply the map on the server import path (conditional).** *Depends:* T18, T17's decision
  line. **SKIPPED 2026-09-23 by T17's decision line** (which this row licenses): the export's `name`
  is used only as a match key (`RpgStore.AlmanacSeedEnrichment.cs:47-65` builds `byNormName` from
  `almanac_seed` and stores no incoming name), the stored `weaknesses` text reaches the committed dump
  and no player surface (`git grep weaknessesText -- web/` is empty), and the name a player reads
  comes from the host's `types` table (`RpgStore.AlmanacSeed.cs:474-486`). The full name never passes
  through the import path at all. See `tasks/ip-censor/jackson-trace.md` §4.
  *Files:* the server/data import site T17 named (for example
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AlmanacSeedEnrichment.cs`, `gk-core/src/FusionRpg.Server/Program.cs`),
  one Data test on an **in-memory** store (`testing-standard.md` R1).
  *Accept:* the host loads the rename map and injects it (Core never reads a file); an import of a
  fixture row carrying a map key stores the replacement; the test uses an invented name.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <the changed src and test paths>,tasks/ip-censor-todo.md -Session <sid>`
  (`server-fallback` / `data-fallback`).
  *Commit:* `ip-censor T20: apply the rename map on the almanac import path`.

### Checkpoint 6 — IC-4.2 closed (names and ids)
- [ ] T19's import-output test green, including id fields after T19b; the generator checks green.
- [ ] T19b's migration tests green; G1's answer (yes, 2026-09-19) is recorded in the ledger with the
  backup path of the first real run. *Audit 2026-09-19: was "default: no re-key".*

## Phase 7 — Registry content, with the owner

- [ ] **T21 First dataset import round.** *Depends:* T10; the downloaded USPTO export.
  *Files:* `tasks/ip-censor/curate/<dataset>-<date>.json` (candidate file), then
  `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json` (admitted rows).
  *Do:* `curate import --dataset uspto --input <export path>`; the owner records a decision, scope and
  `confirmedBy` per row; `curate admit`. The raw export is never committed.
  *Accept:* every admitted row carries its `import` admission; `registry-check` exits 0; the candidate
  file and the admitted rows are committed together. **Default if the owner has not decided:** nothing
  is admitted; the candidate file is committed as evidence and the task stays open.
  *Verify:* `$PY gk-core/tools/ip-censor/tests -q`;
  `.\scripts\verify-change.ps1 -Paths <candidate file>,tasks/ip-censor-todo.md -Session <sid>`.
  *Commit:* `ip-censor T21: first dataset import round`.

- [ ] **T22 First reconfirm round.** *Depends:* T10, T17; identity-rename T18's hand-off note if it
  exists.
  **BLOCKED 2026-09-23 (lane `ip-censor-2`): the round's candidate source has no relevance filter, and
  the owner's decision is the row's own gate.** Measured reading at this head (`curate reconfirm
  --no-model`, run in-process so no artifact was written): census tokens **129,165**; candidates
  **16,985** — **4 re-checks** (`dr-zomboss`, `overwatch`, `penny`, `pvz` — exactly the shipped rows
  the census still finds) and **16,981 new**, of which **1,605 are shorter than `minAliasLength` 4**
  (`0`, `00`, `000`, …) and the rest are ordinary English words and numbers occurring anywhere under
  `docs/guide/**`. Rendered size: **6,013,482 bytes**. Cause: `curate.reconfirm` proposes every census
  token **not in the registry** that occurs on **any** enforced surface (`curate.py:339-348`), and the
  enforced surfaces include the whole player guide and `gk-forge/tools/seedsmith/**`.
  **The row's "commit the candidate file as evidence" default is deliberately not taken:**
  `spec-census.md` §Open Questions 2 already recommends a census snapshot is *generated on demand, not
  committed* ("it is a population, so it goes stale on every content ship"), and a 6 MB pool of
  numeric literals is not a review input. No authored knob exists to narrow it — `import-filter.v1.json`
  is the **import** filter, and the boundary policy's `minAliasLength` is an alias-admission rule, never
  a candidate rule.
  **Question for the manager/owner:** what narrows `reconfirm`'s candidate source before a real round —
  a second authored filter (an interest list or a token-frequency floor), the model half only, or a
  census-pool artifact the owner browses instead of a candidate file? That is a `curate` change and
  belongs to its own row; inventing a filter here would be inventing a policy the owner has not
  authored (principle 4).
  *What is achieved and committed:* the readings above, and T17's
  `tasks/ip-censor/curate/jackson-candidates.json` (the `real-person` group's shape, awaiting the
  owner's strings).
  *Do:* `curate reconfirm` (with the model when available; `--no-model` otherwise), adding the
  Jackson candidates (T17), a `diablo` candidate (plan D5), and identity-rename's candidate rows; owner
  decides; `curate admit`.
  *Accept:* as T21, with `stage: "reconfirm"` and the right `evidence`; any imported row the census
  still finds gains `reconfirmedOn`. Same default.
  *Verify:* as T21.
  *Commit:* `ip-censor T22: first reconfirm round`.

## Phase 8 — Release readiness

- [ ] **T23 Release-gate reading, residue list, full suite.** *Depends:* T12, T16, T19, T19b (T20 if
  taken), T22. *Audit 2026-09-19: T19b added.* **BLOCKED 2026-09-23 (lane `ip-censor-2`):** four of its
  five dependencies are outside this lane's allowed paths — T12 needs `.github/workflows/release.yml`
  and `gk-core/tests/FusionRpg.Guard.Tests/**`, T16 needs `gk-forge/tools/seedsmith/**` + `gk-data/packs/fusion/data/seed/passive-tree/**`,
  T19/T19b need `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/creatures/**`, `gk-data/packs/fusion/data/generated/**` and
  `gk-core/src/FusionRpg.Data/**` — and T22 is blocked on the owner (above). T20 was skipped, not taken. The
  release-gate reading itself is recorded in CP3's commit instead: 6,818 findings, **281 enforced**,
  every one owned.
  *Files:* `tasks/ip-censor/release-readiness.md` (new, evidence), this todo.
  *Do:* run the release step's commands locally; list every remaining enforced finding with its owner
  (identity-rename phases, a curate round, a generator) and plan §9's four items with their state.
  This is the program's last checkpoint across `tools/`, `data/`, `.github/` and possibly
  `gk-core/src/FusionRpg.Data`, so it runs the full suite once: `.\scripts\test-fast.ps1 -AllDefault`, plus
  `$PY gk-core/tools/ip-censor/tests -q` and `$SS gk-forge/tools/seedsmith/tests -q`.
  *Accept:* the readiness file states, per plan §9 item, met or not met with the blocking owner; the
  gate's exit code is recorded as a reading, never asserted in a test.
  *Commit:* `ip-censor T23: release readiness reading`.

### Final checkpoint
- [ ] Every task's acceptance criteria met and ledgered, or marked skipped with the reason.
- [ ] `release.yml` runs the gate before `Publish player pack`; the checklist line exists.
- [ ] IC-4.1 and IC-4.2 (names **and** ids, T19b) closed. *Audit 2026-09-19.*
- [ ] Session record closed (`status: merged`) in a new commit.

---

## Gate

| Gate | Resolver | Default | Blocks |
|---|---|---|---|
| G1 Re-key the `Jackson*` species ids (persisted, host-game type names) | Owner | **Answered yes 2026-09-19** (the former default "no re-key" is superseded) | Nothing; the yes added T19b after T19 |

## Ledger

(Empty. Each task appends one line: task, commit, unmapped paths, readings, anything skipped and why.)

---

---

## Standards audit (2026-09-19)

Findings and fixes are recorded in [ip-censor-plan.md](ip-censor-plan.md) §"Standards audit
(2026-09-19)"; the todo-side items are:

| # | Severity | Finding | Status |
|---|---|---|---|
| A1 | HIGH | Header, T19, CP6, Final checkpoint and the Gate table still used G1's "no re-key" default after the owner's yes; T23 did not depend on T19b | Fixed |
| A2 | HIGH | T19b sat after the ledger without a checkbox, files, an exact `-Session` verify command, a commit message, the generator route for generated species rows, a transaction/refusal rule or an in-memory backup test | Fixed: T19b rewritten in Phase 6 |
| A3 | HIGH | No task made the path-based classifier consistent with identity-rename's kept identifiers | Fixed: T4 acceptance, CP3 owner check |
| A4 | MEDIUM | T11/T12 scanned from `gk-core/tools/ip-censor` (vacuous `git ls-files`) | Fixed: T10, T11, T12 |
| A5 | MEDIUM | `ci.yml:300-306` drifted (now `:311-317`) | Fixed |
| A6 | LOW | Convention list of mapped paths incomplete; "never stash" missing from the header | Fixed |

---

## Finding routed from `test-verification-boundary` (TVB-F22, 2026-09-22)

- [ ] **TVB-F22 — five `gk-data/packs/fusion/data/seed/ip-censor/_registry/*.json` files have no verification-boundary owner** ·
  `python gk-core/scripts/guard-verification-boundaries.py` fails its completeness walk with
  `unmapped enforced-root file: gk-data/packs/fusion/data/seed/ip-censor/_registry/{boundary-policy,import-filter,marks,replacements,scope-policy}.v1.json`
  (5 of the 6 lines; the sixth is `gk-core/data/tuning/creature-rank.v1.json`, routed to its own owner). `gk-data/packs/fusion/data/seed/**`
  is an enforced root (`seam-coverage` S4), so every file under it must resolve to an owner boundary — a new
  program's seed tree landing without its registry rows turns the guard red for every lane, which is how this
  was found (during increment 66 of the Core test split, whose own checks were green).
  **Fix:** add owner rows for the ip-censor seed tree in `gk-core/scripts/verification-boundaries.v1.json` —
  `gk-data/packs/fusion/data/seed/ip-censor/**` → the project that proves it (the runner vocabulary is `dotnet|pytest|script`, so a
  `pytest`/`script` project over this program's tests is fine), or one row per `_registry/**` subtree if the
  readers differ. Owning program: ip-censor.
  *2026-09-23, lane `ip-censor-3`:* T13 landed that boundary (`ip-censor-tool`, project `ipcensor`,
  `paths: ["gk-core/tools/ip-censor/**", "gk-data/packs/fusion/data/seed/ip-censor/**"]`), so the gap this row points at is closed;
  `gk-core/scripts/guard-verification-boundaries.py` is green at this lane's head. The row itself belongs to
  `test-verification-boundary`'s todo (outside this lane's fence), so it is left for that program to tick.

---

## Findings routed from lane `ip-censor-3` (2026-09-23)

- [ ] **IPC3-F1 — the advisory CI scan (T11) reaches the LLM proposer, because it has no `--authored-only`** ·
  `.github/workflows/ci.yml:485` runs `python -m ipcensor.report scan --format json > tasks/ip-censor/ci-scan.json`.
  Cause read: `gk-core/tools/ip-censor/ipcensor/cli.py:154-160` (`_scan`) builds the proposer whenever
  `--authored-only` is absent — `propose=None if args.authored_only else _proposer()` — and
  `gk-core/tools/ip-censor/ipcensor/suggest.py:60-71` then asks it once per distinct mark with no authored
  replacement pair. That contradicts the same spec's §Success criteria (`spec-report.md:39`, "the gate
  needs no model and no network by construction") and `suggest.py:11` ("`propose=None` is the authored-only
  mode … That is the mode CI and the release gate use"). Measured on this machine: without the flag the
  scan waited past 600 s on a live `IPCENSOR_LLM_*` endpoint; with it, `model: None` and exit 1 in ~3 min.
  **Fix:** add `--authored-only` to the `ci.yml` step (T12's `release.yml` step and the checklist line
  already carry it). **Owning program:** ip-censor — but the fix path `.github/workflows/ci.yml` is
  outside lane `ip-censor-3`'s fence, which is why this is a row and not a change.
