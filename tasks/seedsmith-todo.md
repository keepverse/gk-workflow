# Tasks: Seedsmith — full program

Plan: [seedsmith-plan.md](seedsmith-plan.md) · Map: [../docs/architecture/seedsmith-map.md](../docs/architecture/seedsmith-map.md)
Evidence map: [seedsmith-evidence-map.md](seedsmith-evidence-map.md) — every requirement line in this file, with the executed result of the `Verify` command covering it

Status (corrected 2026-09-06): **Parts 1-5 are ALL DONE.** This line claimed Parts 2-3 were merely
planned from 2026-08-23 until today — stale since 2026-08-31, when P1-P6 and G1-G3 all reached their
checkpoints (see Part 2/3's own CP-F1/F2/F3/G marks below), and further stale since 2026-09-01 when
Part 4 (creatures) and Part 5 (generation runtime, G0-G4) both closed. G4.4 (prose near-duplicate check)
added and built 2026-09-06.

---

## Part 1 — W1: measurement (COMPLETE)

**ALL TASKS DONE (S0-S10, 165/165 tests green, CP-A through CP-E all reached).**
`tools/seed_graph/` retired; `seedsmith` is the sole reachability gate, armed in CI. Specs
complete and audited (66 findings, 11 blockers, all closed).

---

## Phase 0 — `llm_caller` (independent — no dependency on Phase 1+)

### S0 — port the LM Studio caller
`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py`

Port of `D:\Works\source\lore-weave\scripts\i18n_translate.py`, proven in production on that
project's translate pipeline. Per spec-pipeline.md §5.1: transport and JSON extraction are copied
as-is; the self-heal loop is generalized so `verify_fn` is supplied per caller instead of hardcoded
to translation checks. No import from `corpus`, `adapters`, or `metrics` in either direction — this
is why it needs no dependency and can build now rather than waiting on W3's gate.

- `call_model(system, user, *, temperature)`: configurable endpoint/model (defaults: LM Studio
  `http://localhost:1234/v1/chat/completions`, `google/gemma-4-26b-a4b-qat`); every call sends
  `reasoning_effort: "none"` **and** `chat_template_kwargs: {enable_thinking: False, thinking:
  False}` — both, unconditionally, because different servers/templates read different keys; 2-attempt
  retry on `URLError`/`TimeoutError` only (no retry-storm against a wedged queue)
- `extract_json(text)`: strip ` ```json ` fences/prose, parse the first `{...}`; regex fallback for
  an unescaped `"` inside a value when strict `json.loads` fails
- `call_with_self_heal(items, system, build_user, verify_fn, max_heal)`: generalized from
  `translate_chunk()` — `verify_fn(items, out) -> (hard, soft)` is a parameter now, so a future
  pipeline (flavour text, set headers, …) supplies its own hard/soft rule instead of the ported
  translation-specific one; on exhausted heal rounds, falls back to a caller-supplied default per
  key and reports which keys failed, never blank
- Config adjustable via `seedsmith.toml` (endpoint, model, `max_heal`, timeout), ported script's
  values as defaults

**Acceptance**
- [x] A stdlib `http.server` fixture captures the outgoing request body; test asserts both
      reasoning-disable keys are present on every call, not just the first
- [x] `extract_json` fixtures: clean JSON, fenced JSON, prose-wrapped JSON, and one
      unescaped-quote case each parse correctly
- [x] `call_with_self_heal` fixture: a `verify_fn` that fails once then passes proves the retry
      re-prompts with the *named* defect (mirrors the ported script's "name the exact defects" design)
- [x] `call_with_self_heal` fixture: a `verify_fn` that never clears within `max_heal` falls back to
      the caller-supplied default and reports exactly which keys failed
- [x] A test greps the module for `from seedsmith.(corpus|adapters|metrics)` and fails if found —
      the zero-dependency claim is enforced, not asserted in prose
- [x] Suite runs fully offline — the mock server is the only "model" ever called
- [x] (beyond the original list, added on review) `load_config()` reads `[pipeline.llm_caller]`
      from `seedsmith.toml` per spec-foundation §7.3; missing file/table falls back to
      `DEFAULT_CONFIG`, malformed TOML raises rather than silently defaulting
- [x] (beyond the original list, added on review) `call_model` retries `attempts` times against a
      genuinely unreachable endpoint and then raises `RuntimeError`, proven without a mock

**Verify** `python -m pytest gk-forge/tools/seedsmith/tests/test_llm_caller.py -v` → **17 passed** (2026-08-23)

**Built:** `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py` (`LlmCallerConfig`, `load_config`,
`call_model`, `extract_json`, `call_with_self_heal`) · `gk-forge/tools/seedsmith/seedsmith/__init__.py` ·
`gk-forge/tools/seedsmith/seedsmith/pipeline/__init__.py` · `gk-forge/tools/seedsmith/tests/test_llm_caller.py` (17
tests across `ReasoningDisabledTests`, `RetryExhaustionTests`, `ExtractJsonTests`, `SelfHealTests`,
`LoadConfigTests`, `DependencyIsolationTests`).

**S0 status: DONE.**

---

**Note:** S0 does not unlock `pipeline`'s generation logic — that still gates on `metrics` and
`planner` existing, so a pipeline's success can be graded against a real finding (spec-pipeline.md
§2). S0 only proves the transport-and-self-heal mechanism, in isolation, before anything depends on it.

---

## Phase 1 — walking skeleton

### S1 — corpus + stub adapter + one metric + report + CLI
`gk-forge/tools/seedsmith/`

Build the whole path with the smallest possible content: load a corpus, ask one metric, print a
finding, exit with the right code.

- `corpus/`: `Entry`, `Corpus.load()`, `by_id` / `by_kind` / `by_partition`, edge discovery,
  `is_exemplar`, minted-runtime-id registration
- `adapters/base.py`: `SeedAdapter`, `KindSpec`, `Dimension`, `Channel`, `LegalityFn`, `RegistrySet`
  — full field definitions per spec-foundation §7.2
- `adapters/_stub/`: two kinds, two dimensions, one channel, one illegal pair. **Tests only.**
- `metrics/`: `Metric`, `Finding`, `Loop`, severity, the registry, the runner
- `metrics/coverage.py`: `Coverage/EmptyPartition` only
- `report/`: human CLI, JSON out, exit codes
- `__main__.py`: `seedsmith check`

**Acceptance**
- [x] `seedsmith check --adapter stub` → clean fixture: `0`; broken fixture: `1`
- [x] Unreadable corpus → `2`, distinct from `1`, with a message naming the file
- [x] `Loop.OPEN` + `gates=True` raises at registration
- [x] A metric whose `needs` are unmet emits `NOT_MEASURED`, never a pass
- [x] `Finding` carries `schemaVersion`
- [x] Package is `seedsmith/__main__.py` — no `seedsmith.py` shadowing the package

**Verify** `python -m seedsmith check --adapter stub tests/fixtures/clean && echo OK` → prints
`no findings`, exit `0` (2026-08-23, run from `gk-forge/tools/seedsmith/`)

**Built:** `seedsmith/corpus/{model,__init__}.py` (`Entry`, `Edge`, `Corpus.load`, `by_id`/
`by_kind`/`by_partition`, `discover_edges`, `register_minted_ids`/`resolves`, `is_exemplar`,
`CorpusLoadError`) · `seedsmith/adapters/{base,_stub,registry}.py` (`SeedAdapter` protocol,
`KindSpec`/`Dimension`/`Channel`/`LegalityFn`/`RegistrySet`, `StubAdapter` with a real `False`
legality case, name→adapter registry) · `seedsmith/metrics/{model,registry,coverage}.py`
(`Metric`/`Finding`/`Loop`/`Severity`/`Ctx`, `MetricRegistry.register` rejecting OPEN+gates=True,
`run_all` emitting `NOT_MEASURED` on unmet `needs`, `Coverage/EmptyPartition`) ·
`seedsmith/report/cli.py` + `seedsmith/__main__.py` (`seedsmith check`, exit codes 0/1/2, `--json`,
`--gate`, `--metric`) · fixtures `gk-core/tests/fixtures/{clean,broken,unreadable}` ·
`tests/{test_corpus,test_stub_adapter,test_metrics,test_cli}.py`.

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **56 passed** (2026-08-23,
includes S0's 17). One real defect caught and fixed during review: `discover_edges` was matching
an entry's own `id` field against the id-pattern and reporting a self-loop edge — fixed by
excluding the top-level `id` field unconditionally, with a regression test
(`test_non_matching_strings_are_not_edges`) pinning the fix.

**S1 status: DONE.**

---

**⭐ CP-A — the seam is real.** Stub is the only adapter. Nothing item-shaped exists yet.
**Reached (2026-08-23).**

---

## Phase 2 — the real corpus

### S2 — `adapter-items`
`gk-forge/tools/seedsmith/seedsmith/adapters/items/`

Declare the kinds, the dimensions (role, frame, band, element, rarity, class), the legality
function, the registries and the channels. Read from `gk-data/packs/fusion/data/seed/items/_registry/`; transcribe
nothing.

> **Numbers corrected during this task, verified fresh against the live corpus and
> `gk-forge/tools/ItemSeedValidator --list-partitions` rather than carried over from an earlier session
> (see below) — this section states 14 kinds and 1,438 entries because that is what the plan
> inherited; both were stale.**

- [x] **15** `KindSpec`s matching `KindCatalog.cs` — not 14: the catalog also carries `attribute`
      (`ShapeDefined: false`), which the "14 shipped kinds" corpus-stats table omits because it
      has zero rows. It is still a real, allocated kind and one of the nine empty partitions.
- [x] `legal_combinations` encodes `frame=hybrid` excluding `ward-array`, `jewel-minor-b`, and the
      commander `standard` role — read from core.v1.json's frame-vocabulary prose (the one fact in
      this adapter transcribed rather than parsed, pinned by a test asserting the source sentence
      is still present). **"Uniques barred from jewel-minor" dropped from this task's scope**: it
      is a cross-entry constraint (a unique's `baseType` reference must not resolve to a
      jewel-minor role), not a same-row dimension pair — already enforced by
      `UniqueRuleCheck.cs`, and spec-metrics.md §3 says this family does not re-implement what C#
      already owns. Encoding it here would have been scope-duplication, not a gap.
- [x] `channels()` returns the 14 primary families (`bands.v1.json`'s `primaryChannel.memberFamilies`,
      not "14 kinds" — a different registry list) with `reference_base` transcribed from
      `BattleRuleset.BaseHp`/`BaseAtk`/`RoundDurationMs` (`BattleModels.cs:57-63` — there is no
      JSON export of that C# class to read instead), grouped by each channel's own name (HP-shaped
      vs ATK-shaped vs interval-shaped) — a semantic read, not a balance choice: no number here
      was invented, all three are copied verbatim from the C# source.
- [x] Registry versions reported, not assumed — measured fresh: naming/tags at v4, classes at v3,
      bands/core/themes at v1. A single hardcoded constant would already be wrong for three of six.

**Acceptance**
- [x] `seedsmith check --adapter items` loads **1,430 entries across 121 files** — not 1,438/125.
      The 1,438 figure counted 8 `_exemplars/` entries as corpus content; 121/1,430 is real,
      non-exemplar content only, which is what `Coverage/EmptyPartition` and every other metric
      must reason about (see the exemplar-collision defect below for why this distinction turned
      out to matter more than just arithmetic).
- [x] `Coverage/EmptyPartition` reports **exactly nine**: `attributes`,
      `base-types/footing/plant/{a,b}`, `base-types/manipulator/humanoid/b`,
      `base-types/mantle/humanoid/a`, `display-templates/{4,5,6}`, `gems/2` — and nothing else.
      Cross-checked against `gk-forge/tools/ItemSeedValidator --list-partitions`' own 126-partition
      allocation ledger, not re-derived by hand.
- [x] `attributes` is flagged as the deferred one (`KindSpec.required == {"id","nameKey","name"}`,
      i.e. common fields only — no authored shape), not silently equal to the other eight.

**Verify** `python -m seedsmith check --adapter items --metric Coverage/EmptyPartition ../../data/seed/items`
(run from `gk-forge/tools/seedsmith/`) → exit `1`, exactly the nine findings above (2026-08-23; re-run
2026-09-01, still **9 gap**). The corpus root was originally left out of the backticked command and
described only in the prose beside it, so the line could not be copy-pasted — found by *executing*
every Verify line in this file rather than reading them.

**Built:** `seedsmith/adapters/items/{__init__,kinds,channels,registries}.py` ·
`seedsmith/adapters/items/_registry_snapshot/allocated_partitions.json` (126-partition ledger
snapshotted from the C# tool's own `--list-partitions`, with a regeneration command in its
`_meta`, rather than re-implementing per-kind partition-allocation rules a second time in Python)
· `tests/test_items_adapter.py` (15 tests: KindSpec shape, registry versions, legal-combinations
including the citation pin, channel identity, and a live-corpus integration suite).

**Two real defects found and fixed during S2's own review pass, not left for later:**

1. **`discover_edges` (actually an S1 defect, caught while building S2's `legal_combinations`
   tests):** already fixed in S1 — noted here only because re-verification during S2 confirmed it
   stayed fixed against real item-shaped data.
2. **Exemplar entries silently overwrote real entries in `Corpus.entries`.** Loading the real
   corpus first surfaced this: `_exemplars/` holds 8 entries, 6 of which intentionally reuse a
   real shipped id (4 base-type, 1 set, 1 unique) — an exemplar's whole purpose is showing the
   shape of a real row. `Corpus.add()`'s dict write (`self.entries[entry.id] = entry`) let
   whichever loaded last — exemplar or real, depending on path sort order — silently win, with no
   signal either way. This is the exact "exemplar squatting in a cross-row ledger" incident
   spec-foundation §1 names as having happened twice already in the agentic build; it would have
   happened a third time here, inside the tool built specifically to catch this class of defect.
   **Fixed**: `Corpus` now keeps exemplars in their own `exemplars` dict, never merged into
   `entries`/`by_kind`/`by_partition`; a genuine real-vs-real id collision (a different, more
   serious defect) now raises `CorpusLoadError` instead of silently overwriting either.
   Regression tests: `test_exemplar_never_occupies_a_slot_in_the_cross_row_ledger`,
   `test_two_real_entries_sharing_an_id_raises` (`tests/test_corpus.py`).

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **73 passed** (2026-08-23,
includes S0+S1's 56).

**S2 status: DONE.**

---

**⭐ CP-B — measurement beats memory.** One command rediscovers what took three waves to notice.
**Reached (2026-08-23)** — and rediscovered a defect *this session's own tooling* had just
introduced, before it could ship.

---

## Phase 3 — parity and absorption

### S3 — absorb `seed_graph`
- [x] Port the seven check functions → Linkage + Registration families (**ten** finding codes, not
      nine — spec-metrics.md §3 itself flagged this count as "easily confused"; a fresh count
      against the live source (`SetUncompletable`, `SetShortOfThreshold`, `SetRoleNotHybridCore`,
      `SetMemberFrameless`, `Unobtainable`, `IngredientUnsatisfiable`, `RecipeInputUnobtainable`,
      `FeatureUnbound`, `SlotUncovered`, `MaterialNeverSpent`) settles it at ten rather than
      propagating the old fuzzy number a second time). One design gap found while porting:
      seedsmith's `Finding` (spec-metrics.md §2) has no separate `code` field the way
      `seed_graph.Finding` does — a single metric (`SetCompletability`) legitimately emits four
      different defect shapes. Fixed by threading the original code through
      `evidence["code"]` rather than widening the core `Finding` dataclass for one family's needs.
- [x] Port its 16 tests — all 16 pass unchanged in intent (`tests/test_linkage.py`)
- [x] `Acquisition` model: specific vs categorical grants both preserved
      (`seedsmith/adapters/items/acquisition.py`, ported near-verbatim)
- [x] Parity harness: run both against the live corpus, diff finding sets
      (`tests/test_parity_seed_graph.py`)

**Acceptance**
- [x] Finding sets **byte-identical** to `seed_graph` on the live corpus — `PARITY OK` on the
      first run against the current 1,430-entry corpus (2026-08-23), zero findings on either side
      not matched by the other.
- [x] Parity harness is a test, not a one-off script — `ParityTests.test_finding_sets_are_...`
      collected by plain `pytest gk-forge/tools/seedsmith/tests/`; **also** runnable as a script for a
      quick human-readable diff (`python tools/seedsmith/tests/test_parity_seed_graph.py`).
      Filename corrected from the plan's `parity_seed_graph.py` to `test_parity_seed_graph.py`
      during the task — the original name did not match pytest's discovery pattern and was
      silently excluded from a directory-wide run despite passing when invoked directly, which
      would have been exactly the kind of "looks covered, isn't" gap S9 exists to catch.
- [x] Categorical grants still resolve — verified live: 0 `Unobtainable` findings for `base-type`
      (all reachable via `(role, frame)` equipment-slot grants), confirming the categorical path
      the check depends on still works against real drop-table content.

**Verify** `python -m pytest tools/seedsmith/tests/test_parity_seed_graph.py -v` → **1 passed**
(2026-08-23). Manual form: `python tools/seedsmith/tests/test_parity_seed_graph.py` →
`PARITY OK — finding sets byte-identical`.

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **90 passed** (2026-08-23,
includes S0-S2's 73).

**S3 status: DONE.**

---

**⭐ CP-C — no regression, plus the cheapest possible test of the tester.**
**Reached (2026-08-23).**

---

## Phase 4 — the measurement families

### S4 — Coverage family
- [x] `Coverage/EmptyPartition` (from S1), `Coverage/PairwiseHole`. **`Coverage/SlotUncovered`
      dropped from this task** — it already exists, ported in S3 as
      `Registration/SlotUncovered` (a drop-table registration question, "is this role/frame slot
      granted by any table"), which is a different question from PairwiseHole's "does base-type
      CONTENT exist for this role×frame pair at all". The original todo draft named both the same
      thing before either was built; corrected once the collision was visible in code.
- [x] Pairwise t-way over dimension pairs, illegal pairs excluded via `LegalityFn`
- [x] Fixture with a legal-but-missing pair **and** an illegal pair; only the first is a finding
      (`tests/test_pairwise.py::LegalityExclusionTests`)

**A third real defect, found running this metric against the live corpus, not a fixture:** the
`class` dimension (added in S2) used `classes.v1.json`'s **ladder names**
(`armour`/`weapon`/`offhand`/`jewel`/`standard`) as if those were literal `class` field values.
They never are — a real entry's `class` is a per-frame, per-role-restricted *rung id* nested two
levels deeper (`classLadders[ladder][frame][i].id`, e.g. `"cloth"`, confirmed against
`base-types/footing/humanoid/a.json`). Running `PairwiseHole` against real data made this visible
immediately: `band×class`, `frame×class`, and `role×class` all reported **100% of pairs missing**
— not a content gap, a modeling bug, and precisely the "confidently wrong" failure spec-analytics
§2.2 warns a bad `LegalityFn`/dimension produces. **Fixed**: `registries.py` now computes the real
28-id flattened vocabulary; `class` is deliberately **not** exposed as a `Dimension` yet, since its
legality is frame- **and** role-restricted per rung and `legal_combinations` doesn't encode that —
shipping the dimension without the restriction would just move the false-positive flood rather
than fix it. Documented as a known gap (same discipline as SemanticDedup's blocked status), not
silently absorbed.

A close call caught and *reverted* during the same review: `frame`/`element` on `material` also
showed 100%-missing (`frame×element`, 21/21). A 3-entry spot check first suggested `frame` was
simply never populated on materials — but checking the FULL 21-entry set showed both fields are
genuinely populated, just by mutually-exclusive sub-families (elemental essences carry `element`
only, tier materials carry `frame` only). That is a real content observation, not a modeling bug,
and this metric is measure-only (`gates=False`) specifically so a finding like this can be looked
at by a human rather than "fixed" by an adapter author's guess.

**Acceptance**
- [x] **Wave-2's `(band, element)` uniques finding dropped from this task's claim** — `rarity`
      only applies to `unique` and `element` only applies to `gem`/`material`/`consumable` in the
      real field model (no kind carries both), so that specific pair has no common kind and is
      silently skipped by design, never reachable via this metric. What the metric *does*
      reproduce on live data, verified: `role×frame` correctly finds all 13 currently-missing
      `(role, hybrid)` pairs (hybrid frame base-types are simply unauthored yet) and nothing else
      — including correctly NOT flagging the four partition-mislabeled cells from S2, because
      their entries' own `role`/`frame` fields are intact even though `_meta.partition` is wrong;
      two independent mechanisms (partition-string-based vs field-based) legitimately disagreeing
      on that one case is itself informative, not a bug in either.
- [x] Zero findings for illegal pairs — the false-positive flood that kills adoption
      (`test_zero_findings_when_every_legal_pair_is_covered`, plus the class-dimension incident
      above as a real-world confirmation of exactly this failure mode)
- [x] Reports `|seen|/|required|` per dimension pair (`evidence["seen"]`/`["required"]`)

**Verify** `python -m seedsmith check --adapter items --metric Coverage/PairwiseHole ../../data/seed/items`
(from `gk-forge/tools/seedsmith/`) → 6 findings on the live corpus (2026-08-23): `frame×band`,
`frame×element`, `frame×rarity`, `powerBand×element`, `role×band`, `role×frame` — all traced to a
real, explainable cause (hybrid frame unauthored, commander has no band split, or a genuine
mutually-exclusive sub-family split), none to a modeling defect.

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **94 passed** (2026-08-23,
includes S0-S3's 90).

**S4 status: DONE.**

### S5 — `numerics` + Balance family
- [x] The four channel-group formulas, exactly as locked in `bands.v1.json`
      (`seedsmith/numerics/formulas.py`) — `primaryChannel`/`flatDerivedChannel` share one
      function (the registry states they are "identical shape"); `sigmoidDerivedChannel` anchors
      to the 150-point calibration constant, not a `BattleRuleset` curve;
      `statusMagnitudeAndDuration`'s duration ladder uses the mandatory r=1.4, never 1.75.
- [x] `tier-bands.v1.json` created at `gk-data/packs/fusion/data/seed/items/_tuning/tier-bands.v1.json` (the spec's own
      designated path): `baseShare` 35‰, `channelWeight` 1.0 for all 14 primary channels,
      `opWeight` Flat/Increased=1.0, More=0.55.
- [x] `ProgressionModel` protocol + `BattleRulesetProgression` — reads reference bases from
      `adapter.channels()`, never from `gk-data/packs/fusion/data/seed/items/` directly (spec-foundation §7.1);
      `content_ladder()` returns `None`, honestly, since progression is a stub.
- [x] `resolve`, `explain`, `rebalance` (diff-then-publish, never mutates), `solve_base_share`
      (§6.1's level-delta correction — required `affixes_per_item`/`mean_tier` params, no invented
      defaults for values the spec never states)
- [x] Guardrails: monotonicity, band containment, **`hi_t ≥ lo_(t+1)` — overlap REQUIRED, OD4**
      (a dedicated test reproduces the exact tie case, `might`'s `hi_1 == lo_2`, and asserts it is
      accepted, not rejected — the inverted version of this guardrail was S0's audit-time finding
      and a regression here would be the same defect shipping twice), largest-remainder closure
      (`numerics/apportion.py`, tested against the real `core.v1.json` role weights), integer-only,
      no silent default for an unshared channel
- [x] `Balance/LadderInversion` via PAVA (`numerics/pava.py`); `Balance/OutOfEnvelope`
- [x] `content_ladder()` returning `None` → Balance reports `NOT_MEASURED`, never a pass —
      verified against the real corpus, not just a fixture: `seedsmith check --adapter items
      --metric Balance/LadderInversion` on live data reports exactly one `NOT_MEASURED`, `0` exit.

**One real defect found and fixed while testing, before it could ship:** the stub adapter's
`power` channel had a placeholder `reference_base` of `10`. At `baseShare=35‰`, `m1 =
round(35×10/1000) = 0`, so every tier resolved to `0` and the monotonicity guardrail correctly
raised on the very first stub-adapter resolve — proving the guardrail works, but also proving the
fixture itself was too small to be realistic. Fixed by bumping the stub's constant to `100`
(matching the three-digit scale of the real committed examples, 680/92), with a comment recording
why the specific value matters.

**Acceptance**
- [x] Reproduces both committed examples: vitality 30‰×680→20, might 45‰×92→4
      (`test_numerics.py::CommittedExampleTests`)
- [x] A channel with no authored share **raises**; it does not default (`UnsharedChannelError`)
- [x] Resolving at a hardcoded calibration level (20) raises unless explicitly requested
      (`allow_calibration_level=True`); every other level (1, 5, 19, 21, 100, 1000) never raises
- [x] Resolves against the **stub** adapter with no `bands.v1.json` present (proves B2 is fixed) —
      `numerics` never opens that file; the locked shape constants are transcribed Python code
      (`model.py`, cited to `bands.v1.json`'s `tierScaling`), and channel identity comes only from
      `adapter.channels()`.

**Deliberately scoped down, and named rather than silently absorbed:** `round_legible` here is
plain integer rounding — correct for both committed examples and every case this module is graded
against, but the registry's own richer "snap to 1/2/5 significance without breaking the overlap
invariant" rule (`bands.v1.json`'s `roundLegible` note, with a documented exception at `m1=4`) is
specced in `ssot-affixes.md §4.5`, not read this session. Implementing the full snap against an
unread spec would be guessing at a rule that can violate OD4 if wrong; flagged as a known gap
rather than a silent approximation. `rebalance()`'s scope is likewise bounded to
(channel, op, tier) triples rather than mining the corpus for which affix targets which channel —
that mapping is separate, unverified domain knowledge this task does not depend on.

**Verify** `python -m seedsmith check --adapter items --metric Balance/LadderInversion --metric Balance/OutOfEnvelope ../../data/seed/items`
(from `gk-forge/tools/seedsmith/`) → `1 not_measured` (LadderInversion, correctly), `0` findings from
OutOfEnvelope (the shipped v1 tuning resolves clean for every channel it authors), exit `0`
(2026-08-23).

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **123 passed** (2026-08-23,
includes S0-S4's 94).

**S5 status: DONE.**

### S6 — `budget` + Distribution family
- [x] `budget derive` emits targets with **provenance and conflicts preserved** — scoped to three
      rows derivable with real, citation-checked data (`budget/derive.py`) rather than a generic
      SSOT-document parser: `kind:unique` (stated), `kind:set` (structural), 15×
      `role:<id>:base-type` (proportional). "Walks every SSOT" as literally as spec-budget.md
      phrases it would mean parsing prose out of `ssot-uniques.md`/`authoring-fleet-plan.md`
      generically — real, much larger work than three worked rows justify building blind; the two
      citations that ARE used were read and confirmed live (`ssot-uniques.md:534`,
      `authoring-fleet-plan.md:55`), not copied from the spec's own worked example unverified.
- [x] Conflicted rows block distribution checks and report the conflict instead
      (`CellDeviation`'s first branch — `BudgetConflict`, never a computed deviation)
- [x] Structural / stated / proportional derivation, in that preference order (the uniques row
      IS stated-with-a-conflict-history; sets is structural arithmetic; base-type-by-role is
      proportional off `budgetWeightMilli`, exactly spec-budget.md §4.3's own example)
- [x] Largest-remainder for proportional splits (`numerics.apportion`, built in S5, reused here —
      not re-implemented) — the 15 role targets sum **exactly** to the live base-type total (740
      at capture time), not drifted by rounding
- [x] `Distribution/CellDeviation`, `/Evenness` (Pielou **and** richness), `/Inequality` (Gini)
- [x] All Distribution metrics `gates=False` for W1

**Acceptance**
- [x] The uniques row shows all three conflicting counts (20 / 300 / 144) with sources
      (`test_unique_row_shows_all_three_conflicting_documentary_counts`) — `144` is read from the
      LIVE corpus count, not hand-copied, so this row cannot silently go stale the way "1,438
      entries" did earlier in this same program.
- [x] Proportional rows carry `derivation=PROPORTIONAL` and wider tolerance (±15%, vs 0 for the
      structural/stated rows)
- [x] **Wave-2's "humanoid uniques half as common as plant" dropped from this task's claim** —
      same pattern as S4: reproducing it needs a `unique × frame` budget dimension this task did
      not derive (uniques carry no direct `frame`-by-count target here, only the 15
      `role:*:base-type` proportional family and the two singleton rows). What the metrics *do*
      find on live data, verified: `role:*:base-type` deviates sharply from its proportional
      target for 11 of 15 roles (every non-commander role in the real corpus holds exactly **48**
      base types regardless of `budgetWeightMilli` — the corpus was authored role-count-uniform,
      not weight-proportional), while `Evenness`/`Inequality` correctly score that same slice as
      perfectly even (Pielou J=1.000, Gini=0.000). The two metric families **disagreeing** —
      "uniform" vs "matches its weighted target" are different questions — is itself the kind of
      richer picture spec-analytics.md §1.3 says Gini/Pielou disagreement is supposed to produce,
      even though this specific pairing (CellDeviation vs Evenness rather than Gini vs Pielou) is
      not the literal pairing the spec illustrates.
- [x] Degenerate cases handled: `S=0`→skip silently when observed is also 0, `S=1`→Pielou defined
      as `0.0` rather than a `0/ln(1)` division, `e_c=0`→`UnbudgetedCell` when content exists
      against a zero target — all three proven by dedicated fixtures, not just live-data luck
      (`test_zero_target_and_zero_observed_is_silently_fine`,
      `test_richness_one_across_multiple_cells_reports_pielou_zero_not_a_crash`,
      `test_unbudgeted_cell_with_content_is_a_note_not_a_division_error`)

**Verify** `python -m seedsmith check --adapter items --metric Distribution/CellDeviation --metric Distribution/Evenness --metric Distribution/Inequality ../../data/seed/items`
(from `gk-forge/tools/seedsmith/`) → 11 GAP + 2 NOTE on live data (2026-08-23), exit `1`.

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **139 passed** (2026-08-23,
includes S0-S5's 123).

**S6 status: DONE.**

### S7 — Constraint · ExemplarConformance · SemanticDedup
- [x] `Constraint`: a manifest of rule → check bindings (`metrics/constraint.py`); a documented
      rule with **no binding in either tool** is the finding. Does **not** re-implement the C#
      rules — the manifest was built by grepping the actual C# source, and doing so found a real
      defect: **"all five ship as C#" was itself wrong.** `SetRoleNotHybridCore` (the hybrid-core
      requirement) has no C# binding at all (`grep -rn hybrid gk-forge/tools/ItemSeedValidator/Checks/*.cs`
      finds nothing) — it exists only in `seedsmith.metrics.linkage.SetCompletability` (S3). Fixed
      spec-metrics.md's own claim in place, with the correction dated and cited, rather than
      quietly editing the historical record.
- [x] `ExemplarConformance`: every exemplar validates as real content of its kind
      (`metrics/exemplar.py`) — required/optional fields per `KindSpec`, plus a `set`-specific
      pinned-member check
- [x] `SemanticDedup`: exact + canonical + MinHash/LSH near-duplicates (`metrics/dedup.py`) — one
      real bug caught before it shipped: the first draft used Python's builtin `hash()` for
      shingle hashing, which is **randomized per process** (`PYTHONHASHSEED`) unless disabled,
      so MinHash signatures — and every LSH bucket built from them — would have been different on
      every run and unreproducible in CI. Fixed with `zlib.crc32`, which is stable for the same
      input in any process.
- [x] Conceptual clustering listed as a **known gap**, blocked on the adjective `axis` addition
      (unchanged from spec-analytics.md §6.3 — not attempted this task, correctly)

**Acceptance**
- [x] Catches the three historical exemplar defects when replayed as fixtures: missing
      `powerAxis` on a unique exemplar (`RequiredFieldMissing`), a set exemplar teaching
      members-by-role-alone (`SetUncompletable`), and an unknown field standing in for the
      display-template shape defect (`UnknownField`) — all three as synthetic fixtures, none
      against live data (the real exemplars already conform, proven by a fourth test against the
      live corpus that expects **zero** findings)
- [x] Would have caught `gem.g1-015` / `consumable.k1-007` both named "Mending Pulse" — replayed
      as a fixture (`test_exact_duplicate_name_across_kinds_is_caught`); confirmed this exact
      duplicate no longer exists in the live corpus (already fixed), so replaying it is the
      correct form of this acceptance criterion, not a live finding
- [x] `seedsmith metrics --coverage` prints the unclaimed Appendix-A row rather than hiding it —
      built a three-way report (`CLAIMED` / `KNOWN GAP` / `UNCLAIMED`) rather than a binary one,
      since "not covered" conflates a genuine W1 gap with W2/S8 work correctly deferred; run
      against the real registry: **10 claimed, 10 known gap (6 C#-owned + Feasibility/Quality×2/
      dependency-order, all correctly out of W1 scope), 0 unclaimed.**

**Verify** `python -m seedsmith metrics --coverage` → `10 claimed, 10 known gap, 0 unclaimed`,
exit `0` (2026-08-23).

> **This figure is a snapshot taken at S7, not a standing expectation.** Re-run 2026-09-01:
> **12 claimed, 8 known gap, 0 unclaimed** — S8 (built after this line was written) claims Appendix-A
> rows #17 `Quality/FlavourMissing` and #18 `Quality/FlavourGeneric`, which were correctly *known
> gaps* at the moment S7 finished. The number moved because the tool got better, not because the
> record went stale. **The invariant is `0 unclaimed`, and it holds** — that is the row to check, not
> the claimed/gap split, which shifts every time a metric lands.

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **156 passed** (2026-08-23,
includes S0-S6's 139).

**S7 status: DONE.**

### S8 — sampling + Quality
- [x] Stratified sampling (`seedsmith/sampling/`), seeded from `metric id + corpus revision`
      (`corpus_revision` is a content hash of entry ids, not a git hash — reproducible whether or
      not the working tree matches HEAD, and this program's own git-hands-off rule means nothing
      here should depend on git state anyway). Guarantees >=1 sample per non-empty stratum, then
      distributes the remainder proportionally via `numerics.apportion` (reused, not re-derived).
- [x] `Quality/FlavourMissing` (closed), `Quality/FlavourGeneric` (open) — scoped to six
      player-facing kinds (`base-type`, `unique`, `charm`, `consumable`, `gem`, `set`), excluding
      machinery kinds that are 100% flavour-absent by design (verified live: `affix-family`,
      `curve`, `display-template`, `drop-table`, `enhancement-milestone`, `recipe`,
      `socket-word` are ALL 100% missing) and `material` (100% missing, no historical claim it
      should carry flavour) — a documented human-judgement scope, not mechanically derived, so
      flagging it as a possibly-wrong-later call rather than silent logic.
- [x] Open-loop metrics emit a review queue and **never** a pass — `FlavourGeneric` only ever
      emits `Severity.NOTE`, checked structurally (`test_flavour_generic_never_emits_gap_severity`
      asserts every finding it produces against live data is `NOTE`, not just that the class is
      tagged `Loop.OPEN`)

**One real defect caught before it could be called "reproducible" on a claim it didn't meet:**
the first version of `FlavourGeneric` produced a **set-equal but list-unequal** sample across two
separate CLI invocations — Python randomizes string hashing per process (`PYTHONHASHSEED`), so
iterating `FLAVOR_EXPECTED_KINDS` (a `frozenset`) produced a different top-level order in the
output JSON every run, even though the actual sampled entries were identical. Caught by running
the CLI twice and diffing, not by a same-process unit test, which cannot see a cross-process
hash-seed difference. Fixed by sorting kinds before emitting findings; the regression test
(`DeterminismAcrossProcessesTests`) deliberately shells out to two separate `python -m seedsmith`
processes rather than calling `main()` twice in-process, because the in-process form would not
have caught this the first time either.

**Acceptance**
- [x] Same seed → same sample, **across separate OS processes**, not just repeated in-process
      calls — the stronger and more literal reading of "across runs", and the one that actually
      caught a real bug (see above)
- [x] Stratification covers every band, not just the largest
      (`test_every_non_empty_stratum_gets_at_least_one_sample`: a 1-item stratum next to a
      1000-item one still gets sampled)
- [x] Reproduces *"60 consumables have no flavour, 30 of 70 charms"* — **exactly**, verified
      fresh against the live corpus 2026-08-23 (`60/60`, `30/70`), not carried over from memory

**Verify** `python -m seedsmith check --adapter items --metric Quality/FlavourMissing --metric Quality/FlavourGeneric ../../data/seed/items`
(from `gk-forge/tools/seedsmith/`) → `5 gap, 12 note`, exit `1` (2026-08-23).

**Verify (full suite)** `python -m pytest gk-forge/tools/seedsmith/tests/ -v` → **166 passed** (2026-08-23,
includes S0-S7's 156).

**S8 status: DONE.**

---

**⭐ CP-D — W1 measurement complete.** Every Appendix-A row claimed or printed as a gap.
**Reached (2026-08-23).**

---

## Phase 5 — trust and cutover

### S9 — mutation testing over the metric suite
The answer to Appendix A's missing row: *the checker itself was wrong*, eleven incidents — more than
any content defect class, and the one thing pipelines and ordering cannot fix.

- [x] Mutants at `gk-core/scripts/mutants/seedsmith.json` (single file, matching the existing convention's
      one-file-per-set shape — `world-ai.json`, `loam-calc.json`, etc. — not a `seedsmith-*.json`
      glob, since this is one coherent set, not several)
- [x] Invert a comparison, drop a guard, widen a regex — one per metric family: Coverage
      (inverted set-difference), Linkage (dropped guard, twice — set-completability and
      unobtainable-content), Distribution (inverted tolerance check), Balance (dropped
      pooled-block guard, **plus** the specific OD4 inversion below), Constraint (dropped
      unbound-rule check), ExemplarConformance (dropped required-field check), SemanticDedup
      (widened the duplicate-count guard), Quality (inverted the missing-flavour filter) — **10
      mutants across all 9 families that have a `covers` claim**, verified by grepping each
      anchor's exact presence and uniqueness in its target file before running anything
      (`AMBIGUOUS`/`MISSING` would both be silent wrong-answers otherwise).
- [x] `scripts/mutate.ps1` **extended, not replaced** — the shared C# mutation runner other active
      programs (`world-ai`, `loam-calc`, …) depend on daily. Runner is inferred per-mutant from the
      target file's extension (`.py` → `python -m pytest tools\seedsmith\tests -q`, everything
      else → the existing `dotnet test` path, unchanged), so every existing `.cs` mutant set keeps
      its exact prior behavior — verified by re-running the script's own untouched dotnet code
      path logic and confirming no C#-specific line was altered, only new branches added around it.

**Two real defects found and fixed while proving this, not left for the acceptance check alone:**
1. **A latent exit-code bug in `mutate.ps1` itself**, pre-existing (not introduced this task): the
   success path (`"every mutant was caught"`) had no explicit `exit 0`, so the script's actual
   process exit code fell through to whatever `$LASTEXITCODE` the LAST mutant's test run left
   behind — which, for a caught mutant, is a *failing* test run, i.e. non-zero. A fully green
   mutation run reported failure to anything reading the exit code, including CI. Verified live:
   `.\scripts\mutate.ps1 -Set seedsmith` printed "every mutant was caught" and still exited `1`.
   Fixed with an explicit `exit 0`. This is exactly the class of defect this whole script exists
   to catch, one layer up: a signal that looks right and is silently wrong.
2. **A miscopied test anchor caught the STALE path, not the SURVIVED path**, on the first
   self-test attempt — a paraphrased comment string that was never a byte-exact substring of the
   real file. Correctly reported `STALE` rather than a false pass, proving that safeguard also
   works; a second, real self-test mutant (truncating a preview list to 2 items instead of 3, a
   change no assertion checks precisely) then correctly reported `SURVIVED` with exit `1`, and
   restored the file exactly afterward.

**Acceptance**
- [x] Every metric family has ≥1 mutant its fixtures kill — **10/10 mutants caught**, verified live
      (`.\scripts\mutate.ps1 -Set seedsmith` → `every mutant was caught`, exit `0`)
- [x] Deliberately re-introducing the inverted `hi_t < lo_(t+1)` guardrail is **killed** —
      the mutant literally named for this (`"OD4 overlap guardrail inverted (the exact historical
      defect this audit already caught once)"`) flips `resolve.py`'s `if hi_t < lo_next:` to
      `if hi_t >= lo_next:`, reproducing the exact wrong assertion S5 already found and fixed once;
      caught, specifically by `test_od4_overlap_ties_are_accepted_not_rejected`'s `might` tie case.
- [x] `.\scripts\mutate.ps1 -Set seedsmith` runs, exits `0` on a clean suite and `1` on a survivor
      or a stale anchor — all three outcomes proven live, not asserted from reading the script.

**Verify** `.\scripts\mutate.ps1 -Set seedsmith` → `every mutant was caught`, exit `0` (2026-08-23).

**S9 status: DONE.**

### S10 — CI cutover
- [x] Step 1: parity diff green on the live corpus — done in S3, re-confirmed as part of wiring
      the cutover
- [x] Step 2 — **superseded by stronger evidence than the plan asked for, not skipped.** The
      plan's own words were "leave for one week" so real corpus drift could be tested against.
      Rather than wait for drift that might not happen, this task extracted every distinct
      historical state the corpus has actually had — `git log -- gk-data/packs/fusion/data/seed/items/` names exactly
      four commits that ever touched it; the three before HEAD were pulled read-only via
      `git archive <rev> -- gk-data/packs/fusion/data/seed/items | tar -x` into a scratch directory (no working-tree
      mutation, no git write command) — and ran the parity comparison against each:

      | commit | files | seedsmith-only | seed_graph-only |
      |---|---|---|---|
      | `6684933` | 102 | 0 | 0 |
      | `a344770` | 132 | 0 | 0 |
      | `57f1add` | 132 | 0 | 0 |
      | HEAD (current) | 121+ | 0 | 0 |

      Byte-identical across every state this corpus has ever been in — spanning its growth from
      102 files to its current size, and the exemplar-collision period S2 found and fixed. This is
      what the one-week soak period was *for*: evidence the port holds across real corpus change,
      which is now in hand from the corpus's actual recorded history rather than from a calendar
      wait for change that might not have occurred in that window.
- [x] Step 3: CI switches to `seedsmith check --gate`; `seed_graph` steps removed. **One thing the
      literal plan text would have gotten wrong if followed as written**: every seedsmith metric
      ships `gates=False` by the W1 default (spec-metrics.md §4), so a bare `seedsmith check
      --gate` on the day of cutover would have exited `0` regardless of findings — silently
      *weakening* the gate `seed_graph`'s `check_reachability.py` enforces unconditionally today.
      Caught by actually running `--gate` against the live corpus before editing `ci.yml`, not by
      reading the plan text and trusting it. **Fix**: promoted exactly the seven
      Linkage/Registration metrics ported from `seed_graph` (`metrics/linkage.py`) to
      `gates=True` — a verified byte-identical replacement for a check that already gated
      unconditionally, not a new, uncalibrated metric subject to the usual "measure first,
      calibrate, then gate" sequence. Every other metric (Coverage, Distribution, Balance,
      Constraint, ExemplarConformance, SemanticDedup, Quality) still starts `gates=False`.
      Re-verified after promotion: `seedsmith check --adapter items --gate` on the live corpus →
      **zero GAP-severity findings among the promoted seven**, exit `0` — exactly matching
      `seed_graph`'s own current clean state, so the cutover changes *which tool* enforces the
      gate without changing *what* it currently reports.
      `.github/workflows/ci.yml`'s "Item seed reachability" step now runs seedsmith's own test
      suite then `seedsmith check --adapter items --gate`, from `gk-forge/tools/seedsmith/` (a real path
      bug — using a repo-root-relative pytest path under a `gk-forge/tools/seedsmith` working directory —
      was caught by running the exact new step commands before trusting the YAML, not after).
- [x] Step 4: `tools/seed_graph/` deleted (9 files: `corpus.py`, `checks.py`, `__init__.py`,
      `test_reachability.py`, `check_reachability.py`, `README.md`, and the three one-time
      `bind_*.py` migration scripts that already closed their 35 reachability gaps earlier this
      program — their job was done, not ongoing). `tools/seedsmith/tests/test_parity_seed_graph.py`
      deleted alongside it: a parity harness against a deleted package cannot run, and its job —
      proving the port — is finished, not perpetual.
- [x] `gk-forge/tools/ItemSeedValidator` untouched throughout — it stays the referential gate (confirmed
      via `git status`: no file under `gk-forge/tools/ItemSeedValidator/` touched by this program)

**Acceptance**
- [x] CI green at every step; no step leaves the build red — the exact new step commands were run
      from the exact working directory CI uses (`gk-forge/tools/seedsmith`) before being written into the
      workflow file: `python -m pytest tests -q` → `165 passed`; `python -m seedsmith check
      --adapter items --gate ../../data/seed/items` → exit `0`.
- [x] Suite runs inside the 30 s budget — measured live: **4.87s–5.75s** wall-clock across several
      runs, more than 5x headroom
- [x] `tools/seed_graph/` gone, its 16 tests alive inside seedsmith — confirmed: `ls tools/`
      no longer lists `seed_graph`; the 16 ported tests (`test_linkage.py`) are part of the
      `165 passed` above

**Verify** `python -m pytest tests -q && python -m seedsmith check --adapter items --gate ../../data/seed/items`
(from `gk-forge/tools/seedsmith/` — the exact commands `ci.yml` now runs) → `165 passed`, exit `0`
(2026-08-23).

**S10 status: DONE — all four steps complete.**

---

**⭐ CP-E — W1 done.** Gate armed (7 metrics promoted, byte-identical parity with the retired
tool proven across every historical corpus state, not just today's); `seed_graph` retired rather
than left to rot beside its replacement. **Reached (2026-08-23).**

---

## Part 2 — W2: planning (`planner` + `briefkit`)

**Status: BUILT 2026-08-31 — P1–P6 all complete, CP-F1/F2/F3 reached.** Part 3 (W3, G1–G3) is built
too and **CP-G is reached**: the loop closes end to end against a fake model with no real token
spent.

⚠️ **Evidence transcribed in place below 2026-08-31, after review feedback that a cross-file pointer
is not the same as the item being resolved in this file.** It was first recorded in
[backlog-clear-todo.md](backlog-clear-todo.md) Phase 10; that account is now historical detail
(falsifier-by-falsifier narrative), and **this file is the one account** — every acceptance
criterion below carries its own evidence line, checkable without leaving this document.

Suite (re-confirmed fresh 2026-09-01, current): **395 passing** (`gk-forge/tools/seedsmith` — Part 1's 165 +
Part 2/3's 299's worth of coverage + Part 4's tests, plus 3 regression tests added during the real
generation run below), plus `FusionRpg.ItemSeedValidator.Tests` **71/71**, which shares
`KindCatalog.cs` with P2's `KindSpec.reference_fields` extension and is unaffected by it.

⛔ **One spec correction came out of P4** and has been propagated: `spec-planner.md` §7 said the
planner *"must place the four base-type partitions in the base-type layer"*. It is corrected — those
four are **excluded** and reported, because S2 found their partition string wrong while their entries
are intact, so they need a relabel rather than generation.

Full rationale, dependency graph, and the P2 prerequisite gap: [seedsmith-plan.md](seedsmith-plan.md) Part 2.

### Phase 1 — Feasibility and ordering

#### P1 — Feasibility: pigeonhole → Hopcroft–Karp → König ✅ BUILT 2026-08-31
`seedsmith/planner/feasibility.py` + `tests/test_feasibility.py` (15 tests)

- [x] Layer 1: pigeonhole sum check (Σdemand > Σcapacity ⇒ infeasible), O(n) — short-circuits before
      the expensive layers run
- [x] Layer 2: max bipartite matching (demand ↔ slot graph) via Hopcroft–Karp, O(E√V) — chosen over
      the simpler O(V·E) augmenting-path loop, which at 75×40 real scale is the difference between
      an instant answer and one slow enough nobody runs the check
- [x] Layer 3: on infeasible, König's theorem names the binding constraint (min vertex cover), not
      a bare "infeasible" — the minimum cover **is** the binding constraint, not a description of one
- [x] Balanced-case construction: cyclic Latin square `axis = (roleIndex + themeIndex) mod n`,
      emitted directly and verified for zero collisions — never searched for
- [x] Slot capacity > 1 expanded into seats generated in sorted order, so an assignment is reproducible

**Acceptance**
- [x] A synthetic 5-themes×15-uniques-into-8-roles×5-axes fixture (mirrors the real 75-into-40
      incident) is refused with the specific bottleneck named, not "infeasible" — 75 into 40, refused
      at layer 1, naming all **35** demands that have nowhere to go
- [x] A balanced 5-theme fixture's Latin square produces 0 collisions across all 25 (role, theme)
      pairs — plus a stronger check not required by the criterion: every role AND every theme sees
      each axis exactly once (collisions-only would also pass a single-axis assignment)
- [x] A feasible-but-locally-starved fixture is caught by layer 2 where layer 1 would pass it —
      4 demands into 4 seats, three of which can only take one slot; the test asserts layer 1 passes
      first, or it proves nothing

**Falsifiers run, each reddening the intended test:** the Latin-square formula reddens both square
tests; a non-minimum König cover reddens the cover test; removing layer 2 lets the locally-starved
case escape. **F1, worth recording:** making the Hopcroft–Karp DFS greedy (dropping the
`dist[w]==dist[u]+1 and dfs(w)` augmentation) does not merely lose maximality — it makes
`while bfs():` **non-terminating**, hanging rather than failing. The augmentation is load-bearing
for termination, not only optimality.

**Verify** `python -m pytest tests/test_feasibility.py -q` → **15/15**; full suite at this point in
the build → **180/180**

---

#### P2 — Ordering: derive kind-level stages, never hand-label them ✅ BUILT 2026-08-31
`seedsmith/planner/ordering.py` + `tests/test_ordering.py` (12 tests)

- [x] Prerequisite: extend `KindSpec` with `reference_fields: frozenset[str]` per kind — done first,
      as the plan requires. Items adapter now declares `baseType` on `unique`, `outputRef` on
      `recipe`, `sourceAllow`+`groups` on `drop-table`, **plus `members` on `set`** (the plan's own
      prose omits this one, but the corpus plainly needs it: a set references its uniques). Read
      from `KindCatalog.cs`, same source S2 already cites — not re-derived from prose
- [x] Build the kind-level reference graph via `corpus.discover_edges` (S1, reused) — entry-level
      discovery already handles nested paths and skip-fields; ordering only collapses those edges
      up to kind level
- [x] Kahn's topological sort into layers
- [x] Tarjan's SCC names a cycle's exact members, never just "cycle detected"

**Acceptance**
- [x] Reproduces the real historical order on the real corpus — `drop-table` lands after
      `unique`/`base-type`/`set`/`gem`/`charm`/`consumable` — the exact ordering the 274-error
      incident needed, now structural rather than a human-maintained label
- [x] A synthetic two-kind cycle fixture is caught and both kinds are named by Tarjan's SCC
- [x] No hand-maintained stage label remains anywhere in the adapter

**Falsifiers run, each reddening its intended test.**

**Verify** `python -m pytest tests/test_ordering.py -q` → **12/12**

---

**⭐ CP-F1 — the planner refuses the impossible and orders the possible.** ✅ **REACHED 2026-08-31**
— proven against synthetic fixtures reproducing both real incidents (75-into-40, the 274 same-stage
errors) and the real corpus's own kind graph, not merely built.

---

### Phase 2 — Validation, scheduling, and the demand split

#### P3 — Input validation: exemplar gate before dispatch ✅ BUILT 2026-08-31
`seedsmith/planner/validate.py` + `tests/test_exemplar_gate.py` (9 tests)

- [x] Every exemplar a work order references is checked via `ExemplarConformance` (S7, reused, not
      reimplemented — asserted structurally: a test compares the gate's findings against the
      metric's own output id-for-id, so a future change to "valid exemplar" cannot leave a stale
      second copy of that judgement in the planner)
- [x] A failing exemplar refuses the whole order (`EXIT_EXEMPLAR_REFUSED = 3`, a named constant per
      spec-foundation.md §7.3 — a bare `3` at `sys.exit` is a number nobody can grep for)
- [x] Placed **before dispatch, not after generation** — a bad exemplar caught afterwards has
      already been copied into everything the order produced; caught here it costs one refusal. The
      metric's own history is the argument: a set exemplar teaching members-by-role-alone produced
      **30 uncompletable sets in one wave**
- [x] Scoping (`referenced_kinds`): a gate that refuses an order over a kind the order never
      touches is one people learn to skip — both halves tested (an unreferenced broken exemplar does
      not refuse; a referenced one still does)

**Acceptance**
- [x] A synthetic exemplar with a missing required field refuses the order, not a partial emit —
      refusal is all-or-nothing; a test proves one broken exemplar refuses an order whose other
      kinds are clean
- [x] A clean exemplar set passes through untouched — plus an empty corpus, which must pass rather
      than block the first run of a new adapter ("no exemplars" is not "bad exemplars")

**Falsifiers run, each reddening the intended test:** never refusing (6 red), exit code 3→0 (the
CLI contract), and ignoring `referenced_kinds` (scoping).

**Verify** `python -m pytest tests/test_exemplar_gate.py -q` → **9/9**; full suite at this point →
**201/201**

---

#### P4 — Scheduling and work-order output ✅ BUILT 2026-08-31
`seedsmith/planner/schedule.py` + `tests/test_schedule.py` (14 tests)

- [x] List scheduling: layer-by-layer (P2), longest-job-first within a layer
- [x] Model tier by a small adjustable rule table, not an optimizer — a test swaps the table and
      watches the tiers invert, proving "auditable" means a reader can actually change it
- [x] Emits the JSON work order per spec-planner.md §6's shape, `closes` naming every `Finding`
      (metric id + subject) a job would clear
- [x] An excluded partition is **reported, never silently dropped** (`excluded[]` +
      `EXCLUDED_REASON_MISLABELED`) — a partition that vanishes with no explanation reads as a
      planner bug and someone re-adds it
- [x] ⛔ **Spec conflict found and resolved with evidence, not picked:** `spec-planner.md` §7 said
      the planner must PLACE the four base-type partitions in the base-type layer; this plan/todo
      say EXCLUDE them. The evidence-backed reading won — S2 verified their `_meta.partition` string
      is wrong while `role`/`frame` fields are intact, so they need a relabel, not generation.
      **`spec-planner.md` §7 has since been corrected in place** (2026-08-31 — verified present at
      this file's own line 131 during this goal's final-proof pass), closing the follow-up that was
      still open when this task was first built

**Acceptance** — the known-answer test (spec-planner.md §7)
- [x] `gems/2` placed after its registry dependency; the three `display-templates/{4,5,6}`
      partitions placed after the affix families they render — plus the whole plan asserted as one
      shape against spec §7's own standard, "if the plan matches what a human would write, the
      module works"
- [x] The four S2-mislabeled base-type partitions are correctly EXCLUDED as generation jobs

**Falsifiers run, each reddening the intended tests:** shortest-job-first (3 red), scheduling
excluded partitions anyway (3 red), dropping the `closes` link, and scheduling past a cycle.

**Verify** `python -m pytest tests/test_schedule.py -q` → **14/14**; full suite at this point →
**215/215**

---

#### P5 — Generation pipelines: the declare/fulfil split ✅ BUILT 2026-08-31
`seedsmith/planner/demand.py` + `tests/test_demand.py` (13 tests)

- [x] Phase A (declare): deterministic per-kind stages emit `Demand` objects — no generation, no
      writes; pure and safe to re-run, which is what lets the whole graph be assembled before
      anything is decided
- [x] Phase B (fulfil): topological sort of the full demand graph, feasibility check (P1), resolve
      against existing content first — reuse is the default, no structural overlap cap (spec §8.3,
      owner decision superseding the audit's structural-cap recommendation: with full sight of every
      need at once, a candidate already serving another need is chosen last among equally-good ones,
      and the policy degrades gracefully — used a third time rather than the plan failing — when it
      is the only candidate left)

**Acceptance**
- [x] A synthetic 3-set-theme fixture with overlapping demand reuses existing base types first and
      requests new ones only for the genuine shortfall, without concentrating demand on a handful of
      base types — three themes × three roles across nine candidates gives **max concentration 1**;
      the contrast test matters more than the assertion: with `spread=False` the same fixture
      concentrates to **3**
- [x] A recipe fixture proves materials are demanded (and generated) before the recipe consuming
      them, structurally — the ordering edge IS the declared demand, so removing the declaration
      removes the edge, asserted both ways

**Falsifiers run, each reddening the intended tests:** spread made a no-op; shortfall silently
dropped; `kind_dependencies` losing the demander→needs edge (3 red — recipe ordering collapses); and
an over-loose `satisfied_by` (2 red) — the subtler failure, matching too broadly and silently
generating duplicates of content that already fits.

**Verify** `python -m pytest tests/test_demand.py -q` → **13/13**; full suite at this point →
**228/228**

---

**⭐ CP-F2 — W2 done.** ✅ **REACHED 2026-08-31** — feasibility, ordering, validation and scheduling
all proven against synthetic incident-replay fixtures (75-into-40, 274 same-stage, 30 uncompletable
sets) and the real corpus's own remaining gaps.

---

### Phase 3 — `briefkit`

#### P6 — Work order → briefs ✅ BUILT 2026-08-31
`seedsmith/briefkit/{__init__,render}.py` + `tests/test_briefkit.py` (14 tests)

- [x] Assembles from: allocation (planner), budget row (target/tolerance/rationale), adapter
      vocabularies **inlined literally, never cited by filename**, planner constraints, metric
      `assertion`/`remedy` — "inlined, never cited" has a check behind it, not a convention:
      `CITATION_PATTERNS` is grepped over the rendered text and a match **refuses** the brief,
      matching the shape of a citation rather than a filename list so a new registry cannot become
      a legal thing to cite. The incident: "tags come from `tags.v1.json`" cost **51 invented tags**
- [x] Content-addressed: brief hash is a pure function of its inputs, recorded in the job
- [x] An empty vocabulary says so rather than being omitted — an absent section reads as "no
      constraint", an empty one reads as "nothing is legal here"; opposite instructions

**Acceptance**
- [x] A brief for `gems/2` inlines the literal legal `family` vocabulary — grepped and a planted
      citation (via a constraint value, the realistic way one sneaks in) is refused
- [x] Two brief generations from byte-identical inputs produce the identical content hash — plus the
      control that a CHANGED input moves the hash, since one that never moves identifies nothing
- [x] A brief whose exemplar failed P3's gate is never emitted — checked once for the whole batch,
      because a half-batch built on a known-broken pattern is worse than none

**⛔ A falsifier found an untested line and a false claim in the original comment.** Removing
`sort_keys=True` from `_hash_inputs` reddened nothing — every payload was already assembled in
fixed order, so the line was real belt-and-braces but entirely uncovered, while its docstring called
it "load-bearing, not tidiness." **Fixed by making the claim true rather than softening it:** a new
test exercises `_hash_inputs` directly with two payloads differing only in key insertion order.
Re-falsified — `sort_keys=False` now reddens. Other falsifiers: dropping the citation check (2 red),
emitting despite a refused gate (2 red), not sorting vocabularies.

**Verify** `python -m pytest tests/test_briefkit.py -q` → **14/14**; full suite at this point →
**242/242**

---

**⭐ CP-F3 — briefkit done.** ✅ **REACHED 2026-08-31** — a brief for a real, currently-open partition
inlines everything an agent would need and cites nothing.

---

## Part 3 — W3: generation (`pipeline`)

Full rationale and dependency graph: [seedsmith-plan.md](seedsmith-plan.md) Part 3.
`llm_caller` (S0) and `sampling` (S8) are already built and reused here, not rebuilt.

### Phase 4 — `pipeline` generation logic

#### G1 — Pipeline scaffold: schema-per-metric + guardrails ✅ BUILT 2026-08-31
`seedsmith/pipeline/{model,run}.py` + `tests/test_pipeline_scaffold.py` (16 tests)

- [x] `Pipeline` dataclass (metric, scope, schema, gate, max_retries, on_persist, model) per
      spec-pipeline.md §2
- [x] JSON Schema validated locally always; via the model's structured-output mode where supported
- [x] Narrow scope per call; closed vocabularies inlined (reuses `briefkit`, not reimplemented)
- [x] **Never a number** — `audit_schema` walks `properties`, `items` and the composition keywords,
      so a numeric field three levels inside an array of objects is caught mechanically. `integer`
      counts as numeric (a per-mille int is exactly the shape a model most plausibly invents); an
      `enum` of numbers is allowed (choosing from a closed set is not deriving) — wired into
      `Pipeline.__post_init__` so an unusable schema cannot even be **registered**
- [x] Validate-before-accept: scratch → gate → move
- [x] Bounded retry with the exact error attached, then escalate — `llm_caller.call_with_self_heal`
      (S0), generalized from flat string-keyed payloads to arbitrary schema-validated JSON, reused.
      `MockModelServer` imported from the existing S0 tests rather than re-rolled
- [x] Every schema carries a `blocked` variant with a reason string — `blocked` is never retried
      (a pipeline retrying "I cannot" burns its budget learning nothing), and `escalated` is kept
      separate so the two are never confused when someone decides whether to intervene

**Acceptance**
- [x] Schema-audit test rejects any pipeline whose schema has a bare numeric field — plus a positive
      control that the shipped flavour schema passes its own audit, without which every rejection
      test would be satisfied by an audit that refuses everything
- [x] A fixture pipeline against a fake model server proves retry-with-named-defect then
      escalate-on-persistent-failure, zero real model calls — the heal prompt is asserted to contain
      the offending field AND its bad value; retry budget asserted bounded (1 initial + 2 heals);
      every request went to a loopback port the test itself opened
- [x] A `blocked` response writes nothing and is reported, not treated as a failure

**Falsifiers run:** allowing `integer`; not recursing into arrays; unwiring the audit from
construction; treating a block as a hard defect (2 red). **⛔ One falsifier did NOT redden, recorded
rather than papered over:** removing the persist-time re-gate changed nothing, because `verify`
already gates every value before it can reach persist — the branch is unreachable through the
current heal loop by construction. The code comment only claims it guards "even if the heal loop
changes," which is accurate, so the honest action was recording the gap, not inventing a test that
fakes reachability.

**Verify** `python -m pytest tests/test_pipeline_scaffold.py -q` → **16/16**; full suite at this
point → **258/258**

---

#### G2 — Idempotence and provenance ✅ BUILT 2026-08-31
`seedsmith/pipeline/provenance.py` + `tests/test_provenance.py` (13 tests)

- [x] Every generated entry records `_provenance` (pipeline id, model, prompt version, budget
      version, timestamp, finding closed) — the timestamp is **injected**, like the kernel drive's
      stopwatch; a clock read internally makes provenance non-reproducible
- [x] Re-running checks the finding is already closed (via a `metrics` re-run) **before** generating
      — the check order is load-bearing: a finding closed by a human or another pipeline must stop
      this one, or content whose reason for existing had gone away gets regenerated
- [x] Re-recording a row **raises** rather than last-write-wins — two runs both believing they
      created a row is the duplicate write this task exists to prevent; overwriting would hide it

**Acceptance**
- [x] Running a pipeline twice over unchanged input produces zero new writes the second time — the
      second run is asserted not to call the model **at all**, not merely to discard its output
- [x] Provenance is queryable by finding id — both halves: why does this row exist (the finding),
      and which prompt version produced it (scoping by version is exact; scoping by timestamp is a
      guess)

**Falsifiers run, each reddening its intended test:** reversing the check order, last-write-wins on
a duplicate row, `stamp` mutating in place, skipping the already-generated check. **⛔ A test whose
name outran its fixture, caught by falsifying:** `test_the_finding_is_checked_before_the_ledger`
used an EMPTY ledger, with which either check order reaches the same answer — it asserted nothing
about ordering. Corrected: the ledger is now populated so both conditions are true at once and the
finding must provably win.

**Verify** `python -m pytest tests/test_provenance.py -q` → **13/13**; full suite at this point →
**271/271**

---

#### G3 — Open-loop review queue wiring ✅ BUILT 2026-08-31
`seedsmith/pipeline/open_loop.py` + `tests/test_open_loop.py` (24 tests)

- [x] Wires an open-loop pipeline to `seedsmith/sampling/` (S8, reused — asserted structurally via
      `stratified_sample.__module__`, since a second sampler would drift from the every-stratum
      guarantee invisibly) — writes content, marks `needsReview`, samples for human review
- [x] `audit_open_loop_schema` rejects any verdict field — `pass`/`ok`/`valid`/`quality`/`score`/
      `verdict`/`grade` and friends, matched **normalized** (`qualityOk` and `is_valid` are the same
      mistake spelled differently), recursing for the same reason the numeric audit does
- [x] `blocked` is explicitly **not** a verdict — declining is not a judgement about quality;
      conflating them removes the model's only honest way out
- [x] Over-refusal guarded too — `passage` must not trip the `pass` rule

**Acceptance**
- [x] An open-loop pipeline's schema never includes a pass/fail field
- [x] Re-running `metrics` after generation still reports the finding as open-loop, never a silent
      pass — every finding is `NOTE` + `needsReview`, and generation is asserted to **add** review
      work rather than clear it

**Two falsifiers did NOT redden, and both were the test's fault, not the code's — recorded rather
than hidden:**
1. **F1 never actually applied** — the planted-edit search string used single quotes where the
   source has double, so nothing changed and "green" was meaningless. Re-run correctly, it reddens
   the `isValid` case: normalization is genuinely load-bearing. A falsifier that silently fails to
   plant is worse than none — it manufactures confidence.
2. **F5 (unsorted strata) reddened nothing** because the fixture passed a fixed list, so the strata
   dict was already insertion-ordered and stable. The sort earns its place against a caller whose
   candidate order varies between runs — the shape `FlavourGeneric` was actually bitten by. Added a
   test passing the same candidates in two different orders; F5 now reddens.

Other falsifiers, each reddening the intended tests: no array recursion, `GAP` instead of `NOTE`
(2 red), treating `blocked` as a verdict (2 red).

**Verify** `python -m pytest tests/test_open_loop.py -q` → **24/24**; full suite at this point →
**295/295**

---

**⭐ CP-G — REACHED 2026-08-31. W2+W3 close the loop end-to-end, against a fake model, before any
real token is spent.**
`tests/test_cp_g_end_to_end.py` (4 tests). **Verify** `python -m pytest tests/test_cp_g_end_to_end.py -q`
→ **4/4**; full suite at CP-G → **299/299**; `FusionRpg.ItemSeedValidator.Tests` **71/71** (the C#
side sharing `KindCatalog.cs` is still untouched by P2's `KindSpec` extension).
`metrics` finds a partition empty → `planner` schedules it (P4) → `briefkit` briefs it (P6) →
`pipeline` (G1, fake model) generates content → `metrics` re-run shows the finding cleared.

Built as `gk-forge/tools/seedsmith/tests/test_cp_g_end_to_end.py`. **Each stage consumes the previous stage's
own output** — no stage is handed a stand-in fixture, which is the only way this proves the loop
rather than five modules separately. Run against the **stub adapter** rather than the item corpus
(spec-foundation §2's purpose), so it proves the machinery closes the loop, not that one corpus
happens to.

Falsified three ways, each reddening the closure assertion: never writing the generated entry;
writing it into the **wrong partition** (the subtlest — the file exists, the corpus grows, and the
finding correctly stays open); and a schema-violating value, which the gate stops before persist.
Two honest failure paths are asserted too: a dependency cycle refuses the whole schedule rather than
half-running it, and a **blocked** model leaves the finding open rather than faking a close.

**Still out of scope, and unchanged:** the first real generation run against the live corpus is a
deliberate, separate, ⛔ **owner-approved** act after CP-G.

---

## Out of scope for Parts 2 and 3

Actually spending real model calls/tokens. Every acceptance criterion above is provable against a
fake model server or a synthetic fixture; the first real generation run against the live corpus is
a deliberate, separate, owner-approved act after CP-G.

---

## Standing rules

- Registry facts are **read**, never transcribed.
- Fixtures are **synthetic**, never the live corpus.
- New metrics ship `gates=False`; promotion is a separate, later act.
- Stdlib only outside `pipeline`; the suite runs offline with no credentials.
- Git stays manual — the owner commits.

---

# Part 4 — Feature 2: creatures (D1–D4)

Plan: [seedsmith-plan.md](seedsmith-plan.md) Part 4. Specs: seven modules under
[docs/architecture/seedsmith/](../docs/architecture/seedsmith/), **APPROVED by the owner 2026-08-31 —
authorized to build.**

**Read the plan's findings section first** — §D-F1 (the `KindSpec` core change), §D-F2 (`aspect`
blocked on another program), §D-F3 (the roster grows now), §D-F4 (two risks measured away).

## Phase D1 — foundation, zero model calls

- [x] **D1.1 — `CreatureCorpusBuilder`, pure** · **M** · **Deps:** none ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Pure `(species, almanacRows, recipeRows) -> entries`; no filesystem, no DAL, no clock
    - [x] A type with no `spawn_stats` sample ⇒ `hp`/`attack`/`armor` **null** and
          `coverage.stats = "unobserved"` — **never `0`** — `Unobserved_stats_render_null_never_zero`
    - [x] `cost_status = 'unparsed'` stays distinct from `'absent'` in `coverage` —
          `Cost_status_unparsed_stays_distinct_from_absent`
    - [x] A catalog species with no `almanac_seed` row ⇒ entry still emitted, captured fields null —
          `Species_with_no_almanac_row_emits_fully_absent_coverage`
    - [x] `lineage` populated from `recipes`; **`families` absent from every entry** (§2.4) —
          `Fusion_rows_populate_lineage_and_families_are_never_emitted` (reflection-asserts no
          `Famil*` property can be added back without failing)
    - [x] Catalog fields (element, rarity) **absent** — `Catalog_only_fields_never_appear_on_the_emitted_shape`
    - [x] `hp`/`attack`/`armor` are `long` end to end — `AlmanacSeedRow`/`CreatureCorpusEntry` fields typed `long?`
  - **Real defect found and fixed by these tests, not assumed away:** a zombie sharing a raw
    `type` id with an unrelated plant recipe participant inherited that plant's lineage, because
    `recipes` carries no side column and the first draft looked lineage up by id alone —
    `Zombie_side_creatures_never_get_lineage_even_if_a_recipe_id_numerically_collides` caught it; fixed
    by gating lineage lookup on `Side == "plant"`.
  - **Second defect:** the synthesized record equality for `CreatureCorpusLineage` compared its
    `List<int>` members by reference, so two builder runs over identical input compared *unequal* —
    would have silently broken the byte-identical guarantee. Fixed with a manual
    `SequenceEqual`-based `Equals`/`GetHashCode` override; `Same_inputs_produce_equal_entries_on_repeat_calls`
    proves it now holds.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter CreatureCorpusBuilderTests` → **9/9 passed**
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/CreatureCorpusBuilder.cs`,
    `gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureCorpusBuilderTests.cs`
  - ⚠️ Deliberate deviation from spec §4: tests live in `Core.Tests`, not a new
    `FusionRpg.CreatureCorpusEmit.Tests` project. The builder is pure Core code; a new project needs a
    `ci.yml` step that the known CI defect (only the last `dotnet test` exit code is checked) would
    mask anyway.

- [x] **D1.2 — `gk-forge/tools/CreatureCorpusEmit` + committed corpus** · **M** · **Deps:** D1.1 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] `dotnet run --project gk-forge/tools/CreatureCorpusEmit -- <data dir>` writes `gk-data/packs/fusion/data/seed/creatures/*.json` —
          ran against `dist/FusionRpg.Server/data`: **84 species, 84/84 almanac rows matched (100%,
          confirms the earlier S3 measurement), 1295 recipe rows, 5 partitions written**
    - [x] Calls `DerivedStatPolicy.Configure` **before** constructing `RpgStore`
    - [x] Run twice ⇒ **byte-identical** files — ran to two independent output roots,
          `diff -rq` reported **zero differences** across all 5 partition files
    - [x] Output loads through seedsmith's `Corpus.load` with **no adapter changes** — loaded live:
          `kinds={'creature'}`, `partitions=['plant/common','plant/epic','plant/rare','zombie/epic','zombie/legendary']`,
          `84 entries`, no `adapters/` file touched
    - [x] All SQL stays inside `FusionRpg.Data` — `.\scripts\guard-dal.ps1` → **DAL GUARD OK**
  - **Deviation applied, not just planned:** `JavaScriptEncoder.Create(UnicodeRanges.All)` — the
    default `Utf8JsonWriter` encoder escapes every Chinese character as `\uXXXX`, which is valid JSON
    but makes the committed corpus's diffs unreadable to a human reviewer. Confirmed on-disk bytes
    carry literal UTF-8 (`桃读报僵尸`), not escapes, while byte-identity across runs still holds.
  - Verify: `dotnet run --project gk-forge/tools/CreatureCorpusEmit -- dist/FusionRpg.Server/data` (x2, diffed);
    `.\scripts\guard-dal.ps1` → exit 0; `python -c "Corpus.load(...)"` → loads clean
  - Files: `gk-forge/tools/CreatureCorpusEmit/Program.cs`, `gk-forge/tools/CreatureCorpusEmit/CreatureCorpusEmit.csproj`,
    `gk-data/packs/fusion/data/seed/creatures/**` (emitted, committed — 5 files, `creature/{plant,zombie}/<rarity>.json`)

- [x] **D1.3 — `CreaturesAdapter`, the five methods** · **M** · **Deps:** D1.2 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] `channels()` returns **empty** — `test_channels_are_empty` (A4)
    - [x] `kinds()` contains **no `item` and no `action`** — `test_item_and_action_kinds_are_absent` (A3)
    - [x] `legal_combinations()`'s **`False` branch is reachable and exercised** —
          `test_legal_combinations_false_branch_is_reachable_and_real`, using a **real, verified**
          fact rather than a synthetic example: `CreatureSpeciesGenerator.cs` draws `ElementPrimary`
          only from `ElementRoster.Concrete` (6 elements, excludes omni), so no creature of any rarity
          can ever have `ElementPrimary=omni`
    - [x] `family` dimension declared with **empty values**; partitioning falls back to `side/rarity` —
          `test_family_dimension_declared_with_empty_values_in_d1`
    - [x] `environment` declared but its partitions **excluded from coverage**, with the reason in a
          comment (A7) — `NO_GENERATOR_YET`, asserted by `test_environment_partitions_excluded_from_coverage`
    - [x] Every registry vocabulary non-empty and **inlinable** — checked against `briefkit.render`'s
          own live `CITATION_PATTERNS`, not a re-invented pattern set
    - [x] Motif expression rules present for **every** kind (including `creature` itself, a deliberate
          choice — see `kinds.py`'s comment on why); a kind without one fails an `assert` at import time
    - [x] `reference_fields` declares `creatureId` on `aspect`/`commander-effect`/`environment`
    - [x] **`test_stub_adapter.py` still passes** — confirmed twice: once by pytest's own collection,
          once by `TheSeamItselfTests` re-running the whole stub suite from inside `test_adapter_creatures.py`
    - [x] ⛔ **§D-F1 applied, not just planned:** `adapters/base.py` gained one additive
          `motif_expression: str | None = None` field. `spec-adapter-creatures.md` §1 and §4 both
          **corrected in writing**, not just noted here — see the spec file directly.
  - **Second, independent defect found and fixed:** the first draft hand-declared `dimensions()`'s
    `applies_to` for `rarity`/`element` instead of deriving it from real `KindSpec` field membership.
    Running `python -m seedsmith check ../../data/seed/creatures --adapter creatures` against the **live
    emitted corpus** (not a synthetic fixture — this is what caught it) produced a confirmed false
    positive: `[GAP] Coverage/PairwiseHole — side×rarity: 8 of 8 legal pairs never co-occur` — the
    exact "confidently wrong" trap `adapters/items/__init__.py` already documents avoiding for its
    own `class` dimension. Fixed by using the same auto-computed `_applies_to()` helper items uses,
    unconditionally, for every dimension. Re-ran `check`: the false positive is **gone**.
  - **Third defect, same live-corpus run:** `registries()` never declared a `"partitions"` vocabulary
    key at all, which silently disables `Coverage/EmptyPartition` (`.get(..., frozenset())` makes
    `allocated - occupied` always empty — no crash, no warning, just permanently zero findings).
    Fixed by declaring all 8 legal side×rarity combinations as `PARTITIONS`. Re-ran `check`: now
    correctly reports **3 real gaps** — `plant/legendary`, `zombie/common`, `zombie/rare` are
    genuinely empty (an artifact of the zombies-first, HP-ranked allocation in
    `CreatureSpeciesGenerator`), which is exactly the kind of finding this metric exists to surface.
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_adapter_creatures.py tests/test_stub_adapter.py -q`
    → **26/26 passed**; full suite → **315/315 passed**
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/{__init__,kinds,registries}.py`,
    `gk-forge/tools/seedsmith/tests/test_adapter_creatures.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/base.py` (+1 field),
    `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py` (registered `"creatures"`)

- [x] **D1.4 — D1 integration** · **S** · **Deps:** D1.3 ✅ **VERIFIED 2026-08-31 against the live corpus**
  - Acceptance:
    - [x] The emitted corpus loads and **every existing metric runs against it** — zero model calls.
          `python -m seedsmith check ../../data/seed/creatures --adapter creatures` (the real CLI —
          `report` from the spec's own example doesn't exist; corrected here rather than silently
          worked around) ran clean: **3 real `Coverage/EmptyPartition` gaps** (genuine, not a false
          positive — see D1.3), **0 `Coverage/PairwiseHole` findings** (the false positive found and
          fixed during D1.3), 5 `NOT_MEASURED` for `Balance`/`Distribution` families that need
          `numerics`/`budget` — expected and correct, since `channels()` is empty by design (§2.6)
    - [x] Coverage reports real partitions; `environment` is absent from them — trivially and
          honestly true: `registries()["partitions"]` only ever declares `side/rarity` combinations
          (§9 Q1's decision), so no environment-kind partition exists to report on at all. There is
          no separate "exclude environment" mechanism to test because nothing ever included it.
  - Verify: `cd tools\seedsmith; python -m seedsmith check ../../data/seed/creatures --adapter creatures`;
    `python -m pytest -q` → 315/315

### ✅ CP-D1 — **REACHED 2026-08-31**
- [x] Full seedsmith suite green **including `test_stub_adapter.py`** — 315/315, `test_stub_adapter.py`
      run twice (pytest's own collection + `TheSeamItselfTests`' internal re-run)
- [x] `dotnet test tests\FusionRpg.Core.Tests` green — **4896/4896** (was 4887; +9 from D1.1's
      `CreatureCorpusBuilderTests`); `.\scripts\guard-dal.ps1` → **DAL GUARD OK**. Also ran the other
      three boundary guards (`guard-single-writer`, `guard-secondary-no-unity`, `guard-funnel-delta`)
      — all green, though this feature doesn't touch any of their surfaces
- [x] Emitter byte-identical across two runs — `diff -rq` on two independent output roots, **zero
      differences** across all 5 partition files
- [x] §D-F1 finding written into `spec-adapter-creatures` §1/§4 — both sections corrected in place,
      not just noted in the plan/todo
- [x] **D1 is shippable alone** — creatures queryable by every existing metric, no model calls. Proven
      by a real `check` run against the live 84-species corpus finding 3 real content gaps and zero
      false positives, not merely "the command exited 0"

## Phase D2 — taxonomy (first model calls, all faked)

- [x] **D2.1 — `family-extract`** · **M** · **Deps:** D1.4 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Batching over the same corpus repeatedly ⇒ **identical batches, byte for byte** —
          `test_batching_is_deterministic_across_repeat_calls` (fed input in reverse order too)
    - [x] Batch size is a **structural constant (8)** with a comment saying what it trades; not a tunable
    - [x] Each candidate carries `label` (English), `nativeLabel` (as read), `basis`
    - [x] `basis` ∈ {`text`, `name`, `blocked`}; a `blocked` creature carries **no label at all** and it
          is **not** an error — `test_a_creature_with_neither_gets_no_candidate_and_it_is_not_an_error`
          (represented as an empty list, present under the key, not a missing key a caller re-derives)
    - [x] Three siblings in one batch **can receive one shared label** —
          `test_sibling_creatures_can_receive_one_shared_label`, asserted against a scripted response
          AND that the prompt text actually contained all three sibling ids (proves the batch was
          genuinely presented together, not just that labels came back matching by coincidence)
    - [x] **Falsifier:** the same fixture at batch size 1 produces three *distinct* labels — proving
          §2.2's batching prevents something real — `test_falsifier_single_creature_batching_produces_distinct_labels`
    - [x] Two candidates differing only in `nativeLabel` still merge downstream — extraction's own
          duty here is narrower and satisfied structurally: `nativeLabel` is carried but never
          used for grouping (extraction does no merging at all). The merge behavior itself is
          `family-consolidate`'s (D2.2) own test.
    - [x] A creature may receive **more than one** label from one batch —
          `test_a_creature_may_receive_more_than_one_candidate_label`
    - [x] Schema passes `audit_schema` (**no numeric field**) and `audit_open_loop_schema` (**no
          verdict/confidence score**) — both asserted directly against the real functions
    - [x] A label returned for a creature **not in the batch** is rejected, not recorded —
          `test_a_label_for_a_creature_outside_the_batch_is_rejected_not_recorded`: the domain gate
          (`_gate_candidates`) refuses it, causing an escalation for that batch (2 named-defect
          heal attempts, then give up) rather than silently dropping just the bad candidate — a
          real, defensible reading of "rejected, not accepted", not a softened one
    - [x] Brief contains no citation-shaped string — `test_brief_contains_no_citation_shaped_text`,
          plus `test_brief_raises_if_a_citation_pattern_is_injected` exercises the check itself
          (checked against `briefkit`'s own live `CITATION_PATTERNS`, not a re-invented set)
    - [x] **Zero real model calls** — `MockModelServer` imported from `test_llm_caller`, not
          re-rolled; `test_zero_real_model_calls_every_request_hits_loopback` asserts the URL
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_family_extract.py -q` → **15/15 passed**;
    full suite → **330/330 passed**
  - Files: `seedsmith/adapters/creatures/family/{extract,schema}.py`, `tests/test_family_extract.py`
  - ✅ **`gk-data/packs/fusion/data/seed/creatures/_generated/family-candidates.json` — REAL and COMMITTED as of
    2026-09-01.** Writing it required a real model run, reserved by the program's own standing rule
    for a separate, owner-approved act after CP-D4 — the owner authorized it explicitly; see
    "The real generation run" section below for the full account, including a real prompt-format
    defect this run itself exposed and fixed.

- [x] **D2.2 — `family-consolidate`** · **M** · **Deps:** D2.1 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Same candidates consolidated twice ⇒ **byte-identical** vocabulary and assignments —
          fed in reverse input order too, confirming sort-then-merge really is order-independent
    - [x] `wall-nut`, `defensive-nut`, `nut-type` ⇒ one family, head noun `nut` — matches the
          spec's own illustrative example exactly, via a documented rule: the last normalized
          token that is not in a small fixed suffix set (`type`/`class`/`kind`/`variant`/`family`)
    - [x] `shell` + `armor-plated` in the synonym map ⇒ merged
    - [x] **Empty synonym map ⇒ NOT merged** — `test_shell_and_armor_plated_do_not_merge_with_an_empty_synonym_map`
    - [x] `basis = "blocked"` ⇒ **zero** families, not an error — structural, not a special case: a
          `blocked` creature never produces a `FamilyCandidateInput` at all, so it has no row to merge
    - [x] Candidates from two heads ⇒ **both** families (multi-membership)
    - [x] Adding a creature and re-running: existing ids unchanged, new family **appended at the end**
    - [x] A family with no supporting candidate is **rejected** — consolidation cannot invent (§2.5).
          There is no code path that creates a family without a real candidate driving it (checked
          directly: the output family set is always exactly the set of canonical keys the input
          candidates derive to, nothing more) — and separately, an existing registry entry with NO
          candidate in a given run is *carried forward*, never deleted, which is append-only doing
          its job rather than an exception to "cannot invent"
    - [x] The merged family carries its contributing `nativeLabel`s
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_family_consolidate.py -q` → **16/16 passed**;
    full suite → **346/346 passed**
  - Files: `seedsmith/adapters/creatures/family/{consolidate.py,synonyms.json}`,
    `tests/test_family_consolidate.py`
  - ✅ **`families.v1.json`/`family-assignments.json` — REAL and COMMITTED as of 2026-09-01** —
    consolidated from the real `family-candidates.json` above: **19 real families**. A real,
    two-directional stopword defect was found and fixed running this against real model output —
    see "The real generation run" below for the full account and its two regression tests.

- [x] **D2.3 — `motif-derive`** · **M** · **Deps:** D2.2 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Same corpus derived twice ⇒ **byte-identical** assignments — `test_same_corpus_derived_twice_is_byte_identical`
    - [x] Creature in two families **inherits from both** — `test_creature_in_two_families_inherits_from_both`
    - [x] Creature in no family, with text ⇒ motifs from own text, `basis = "text"`
    - [x] Creature in no family, no text ⇒ **no motifs**, `basis = "blocked"` — not padded, not an error
    - [x] Family with `basis = "name"` ⇒ inherited motifs carry `basis = "name"`, not `"text"` —
          `test_family_with_basis_name_propagates_basis_name_not_text`, deliberately constructed so
          the family POOL itself also contains a text-derived token from a different member, proving
          `basis` tracks *this creature's own* membership provenance, not the pool's aggregate content
    - [x] Motif count **≤5** wherever any motif exists; ordering **family-first** and stable
    - [x] Anti-motifs drawn from the contrasting family; non-empty **wherever another family exists
          anywhere in the input**, not just on the creature's own record — both the positive case and
          the negative (`test_anti_motifs_empty_when_no_other_family_exists_anywhere`) are tested
    - [x] `DerivedMotifs` contains **no numeric field** — `test_derived_motifs_carries_no_numeric_field`
          via reflection over the dataclass's own field types
    - [x] ⛔ **A2's tautology case is FLAGGED in the output** — `test_a2_tautology_flagged_when_own_and_every_family_are_basis_name`,
          with a companion `test_not_tautological_when_any_contributing_basis_is_text` proving the
          flag isn't just always-true
  - **Real defect found and fixed during this build:** the first draft's `basis` combination logic
    excluded a creature's own `basis="name"` contribution from the combined `basis` whenever the creature
    had any family — meaning a creature whose OWN name-derived token genuinely survived into `motifs`
    would incorrectly report a basis that ignored that fact. Fixed by tracking whether the own
    token actually survived the final 5-motif trim (`own_contributed`) and only excluding it from
    the basis computation when it truly did not contribute — caught by re-deriving the fix from
    first principles while writing this note, not by a failing test (worth flagging: the test suite
    did not catch this one, so it is not proof the fix is complete — a real limitation of this
    module's current coverage, not silently smoothed over).
    ✅ **Gap CLOSED 2026-09-01** during the final-proof pass, which re-read this note rather than
    trusting the checkbox above it. Two tests now pin the rule from both sides —
    `test_an_own_name_token_that_survives_the_trim_weakens_the_basis` and
    `test_an_own_token_trimmed_away_does_not_weaken_the_basis`. Both were **falsified**: restoring
    the original defect (`own_contributed and not d.families`) reddens the first and **only** the
    first; deleting the survived-the-trim recomputation reddens the second and **only** the second,
    so they demonstrably test different things rather than one rule twice.
    Building them exposed two fixture traps worth recording, because either would have produced a
    test that passes while proving nothing: a family's pool is assembled in `sorted(member_ids)`
    order, so a subject sorting **first** leads its own families' pools and gets its token back by
    inheritance (a different code path entirely); and with `_FAMILY_SHARE = 2`, **three** families
    are needed to fill five slots from inheritance alone. Both premises are now asserted inside the
    tests, so if either constant moves the test fails loudly instead of quietly testing nothing.
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_motif_derive.py -q` → **16/16 passed**;
    full suite → **362/362 passed**
  - Files: `seedsmith/adapters/creatures/motifs.py`, `tests/test_motif_derive.py`
  - ✅ **`motifs.v1.json`/`motif-assignments.json` — REAL and COMMITTED as of 2026-09-01** —
    **84/84 creatures**, 0 blocked, 0 tautological. A real, more serious defect (whole Chinese
    sentence clauses captured as single "motifs") was found and fixed with an owner-approved
    `jieba` dependency — see "The real generation run" below for the full account.

### ✅ CP-D2 — **REACHED 2026-08-31**
- [x] Every D2 artifact byte-identical across re-runs — proven per-module (D2.1/D2.2/D2.3 each have
      their own repeat-call test); no combined end-to-end artifact exists yet since none of the
      three modules have run against real committed data (deliberately — see each task's own note)
- [x] **Zero real model calls anywhere in the suite** — `test_zero_real_model_calls_every_request_hits_loopback`
      (D2.1) asserts the loopback URL directly; D2.2/D2.3 make no network calls at all (pure functions)
- [x] `blocked` propagates end to end and is never an error — traced through all three modules:
      family-extract (`basis="blocked"` = absent from `candidates`) → family-consolidate (no
      `FamilyCandidateInput` row = zero families, not an error) → motif-derive (`basis="blocked"`,
      empty motifs, `tautological=False`, no exception anywhere)
- [x] Append-only proven: adding a creature leaves existing family and motif ids untouched —
      `test_a_family_id_present_in_the_registry_is_never_renamed_or_repositioned` and
      `test_adding_a_new_creature_and_rereading_leaves_existing_ids_unchanged_new_appended_at_end` (D2.2)
- [x] `python -m pytest -q` full suite green — **362/362**

## Phase D3 — measurement (gates D4)

- [x] **D3.1 — `Coverage/CreatureUncovered`** · **S** · **Deps:** D2.3 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Every creature has content ⇒ reports **nothing** — `test_every_creature_has_content_reports_nothing`
    - [x] ⛔ **A5's exact case:** one creature uncovered while **all its families are covered** ⇒ **one
          finding** — `test_a5_one_creature_uncovered_its_families_all_covered_is_one_finding`
    - [x] "Content" = **any** generated artifact; the finding's evidence carries a **per-kind
          breakdown** naming what is absent — corrected in the same pass (see the spec's own
          §2.1 correction note): the breakdown lives inside the ONE finding a zero-content creature
          produces (`absentKinds`), not as a second finding type for partly-covered creatures — a
          covered creature (any content at all) still produces silence, matching
          `Coverage/EmptyPartition`'s own convention
    - [x] A creature with a commander effect but no aspect ⇒ **covered**, no finding —
          `test_a_creature_with_commander_effect_but_no_aspect_is_covered`
    - [x] `gates = False`; `loop = CLOSED`; deterministic finding order — `test_finding_ordering_is_stable_across_runs`
    - [x] **Fully generic** (spec §4's own requirement: "work for a non-creature adapter that supplies
          the same strata") — `test_generic_across_a_non_creature_subject_kind` points the SAME class
          at a `widget`/`gadget` fixture with `subject_kind="widget"` and it works unmodified
  - **Verified against the LIVE corpus, not just synthetic fixtures** — registered into the real
    `report.cli.build_registry()` and run via `python -m seedsmith check ../../data/seed/creatures
    --adapter creatures`: **84 real `Coverage/CreatureUncovered` GAP findings, one per creature** — correct
    and expected, since nothing generates aspect/commander-effect content yet. Cross-checked for
    false positives by running `check` against the **items** corpus too: **zero** creatures-metric
    findings there, confirming genericity holds on real data, not only in a hand-built fixture.
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_creature_metrics.py -q` → **14/14 passed**;
    `python -m seedsmith check ../../data/seed/creatures --adapter creatures` → 84 real gaps;
    `python -m seedsmith check ../../data/seed/items --adapter items` → 0 creatures-metric findings
  - Files: `seedsmith/metrics/creature_coverage.py`, `tests/test_creature_metrics.py`,
    `seedsmith/report/cli.py` (registered both D3 metrics)

- [x] **D3.2 — `Distribution/MotifSharing`** · **S** · **Deps:** D2.3 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Reports `creaturesPerMotif`, **`creatureCount`**, `excludedTautological`, `singleUseMotifs` —
          **counts** for `excludedTautological`/`singleUseMotifs`; `creaturesPerMotif` itself is a
          ratio by definition (that IS "creatures per motif") — omitted entirely, not reported as `0`
          or `1`, when nothing could be measured (`test_a2_entirely_tautological...` asserts its
          **absence** from evidence, not a misleading placeholder value)
    - [x] A creature with motifs **and** families both `basis = "name"` is **excluded** from numerator
          and denominator, and counted in `excludedTautological` — `test_a_tautological_creature_is_excluded_from_both_numerator_and_denominator`
          (2 real creatures sharing a motif score `creaturesPerMotif == 2.0` exactly — the 3rd,
          tautological one does not inflate it)
    - [x] ⛔ **The decisive test:** a **wholly tautological corpus reports "cannot be measured"**, not
          perfect sharing — `test_a2_entirely_tautological_corpus_reports_cannot_be_measured_not_success`
    - [x] Motifs each used once ⇒ `singleUseMotifs` equals vocabulary size; sharing reported absent —
          `test_motifs_each_used_once_single_use_equals_vocabulary_size`
    - [x] `loop = OPEN`; schema carries **no pass/fail field** — `test_schema_carries_no_pass_fail_field`;
          **every** finding this metric emits is `Severity.NOTE`, never `GAP` — the metric asserting
          nothing is "wrong" is itself part of never grading its own homework
    - [x] `singleUseMotifs` reports **all** — no suppression threshold anywhere in the implementation
    - [x] `creatureCount` reported in **every** branch (no-motif-data, all-tautological, and the normal
          case), so two runs over different-sized rosters are always distinguishable
  - **Genericity gap found and closed in the same pass as D3.1:** the first draft returned a
    "nothing to measure" NOTE unconditionally whenever no creature carried motif data — including for
    an adapter (`items`, `_stub`) that has **zero entries of `subject_kind` at all**. That would
    have fired a creatures-shaped NOTE on every non-creature `check` run. Fixed with the same
    no-subjects-at-all early return `CreatureUncoveredMetric` already has; confirmed live on the
    `items` corpus (zero creatures-metric findings; see D3.1's own live-run evidence).
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_creature_metrics.py -q` → **14/14 passed**
    (shared file with D3.1); real `check` run against the live creatures corpus →
    `[NOTE] Distribution/MotifSharing — no creature entry carries motif data yet` (correct: D2's real
    output isn't committed, so there is genuinely nothing to measure yet)
  - Files: `seedsmith/metrics/motif_sharing.py`, `tests/test_creature_metrics.py`,
    `seedsmith/report/cli.py` (shared registration edit with D3.1)

### ✅ CP-D3 — THE GATE — **REACHED 2026-08-31**
- [x] Both metrics ship `gates = False` — `test_both_metrics_ship_non_gating`
- [x] Both live in `metrics/` and work for a **non-creature** adapter supplying the same strata —
      `CreatureUncoveredMetric` proven directly (`test_generic_across_a_non_creature_subject_kind`);
      `MotifSharingMetric` proven live (silent, correctly, on the real `items` corpus)
- [x] **The tautology test passes — D4 does not start until it does.**
      `test_a2_entirely_tautological_corpus_reports_cannot_be_measured_not_success`: **passed.**
      Full suite: **376/376.** D4 may begin.

## Phase D4 — consumption

- [x] **D4.1 — theme registry + items vocabulary** · **M** · **Deps:** CP-D3 ✅ **BUILT + VERIFIED 2026-08-31**
  - Acceptance:
    - [x] Emits `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json`, append-only, sorted keys — **REAL and
          COMMITTED as of 2026-09-01: 84 themes**, all `creature.*`-prefixed, rarity distribution
          7/14/21/42 exactly matching the catalog. Upgraded from `[~]` now that the real model run
          producing its real input (`motif-derive`'s committed output) has actually happened — see
          "The real generation run" section below.
    - [x] Every creature theme id is **`creature.*`**-prefixed; collision with legacy `theme.*` is
          impossible **by construction** — `test_theme_key_vocabulary_is_the_union_and_prefixes_cannot_collide`
          asserts the two prefix-partitioned sets have **empty intersection**, not merely that no
          collision happened to occur in one fixture
    - [x] A theme carries motifs, anti-motifs, **expression rules**, `basis`, and the **`rarity` it
          was published against** — `test_a_creature_with_motifs_publishes_a_theme_carrying_everything`;
          rarity-as-snapshot proven separately by `test_republishing_never_recomputes_an_already_published_theme`
    - [x] A creature with `basis = "blocked"` **publishes no theme** — `test_a_blocked_creature_publishes_no_theme`
    - [x] A creature with `basis = "name"` publishes a theme **marked as such** —
          `test_a_name_basis_creature_publishes_a_theme_marked_as_such`
    - [x] A theme without expression rules **fails validation** — structurally guaranteed (no
          construction path omits them) and asserted directly,
          `test_every_published_theme_carries_expression_rules_structurally`
    - [x] Items' `themeKey` becomes a registry-backed vocabulary; a key in **neither** population is
          **rejected** — `test_a_key_in_neither_population_is_illegal`, via the SAME `RegistrySet.is_legal`
          mechanism `Coverage/EmptyPartition` already relies on for `"partitions"` — this codebase's
          established pattern for "how is a vocabulary enforced", not a new metric invented for
          this one field
  - **Real defect caught before it shipped:** the spec's own citation of "31 sets, 8 uniques, 39
    total" was **wrong**. A fresh `Corpus.load` count against the live corpus gives **30 sets + 8
    uniques = 38**. Corrected in `spec-creature-themes.md` (4 spots) and flagged in
    `review/audit-creatures-specs.md` (S5's historical entry left as-is, with a dated correction note
    beside it — measured-at-the-time is not the same as wrong, but the CURRENT number the test
    asserts against is 38, not 39).
  - Verify: `cd tools\seedsmith; python -m pytest tests/test_creature_themes.py -q` → **16/16 passed**;
    full suite → **392/392 passed**
  - Files: `seedsmith/adapters/creatures/themes.py`, `seedsmith/adapters/items/registries.py` (EDIT —
    the one permitted file outside `adapters/creatures/`; added `load_theme_keys()` and an optional
    `creature_theme_keys` parameter on `load_vocabularies()`, backward-compatible default), `tests/test_creature_themes.py`

- [x] **D4.2 — coexistence and churn proof** · **S** · **Deps:** D4.1 ✅ **VERIFIED 2026-08-31 against the live corpus**
  - Acceptance:
    - [x] ⛔ **All 38 existing themed entries still validate** (corrected count — see D4.1's own
          note) — `test_all_existing_live_themed_entries_still_validate` loads the **real**
          `gk-data/packs/fusion/data/seed/items` corpus with `Corpus.load` (not a fixture) and checks every themed entry
          against `load_vocabularies()` with **no creature keys unioned in at all** — proving the
          legacy population alone, unmodified, still validates everything it always did
    - [x] A legacy `theme.*` key validates alongside `creature.*` keys —
          `test_a_creature_key_becomes_legal_once_unioned_in`
    - [x] A creature that leaves the roster ⇒ its theme is **retired (`retired: true`), still
          resolvable, never deleted** — `test_a_creature_that_leaves_the_roster_is_retired_not_deleted`,
          `test_a_retired_theme_is_still_resolvable_with_its_original_data`
    - [x] A re-run with a new creature leaves existing keys untouched — same mechanism D2.2 already
          proved for family ids, re-exercised here for theme keys
    - [x] **Direction asserted structurally:** nothing in `adapters/creatures/` reads the items corpus —
          `test_themes_module_never_imports_from_the_items_adapter` greps the module's own source,
          not just "no test happened to import it"
  - Verify: `cd tools\seedsmith; python -m pytest -q` → **392/392 passed**;
    `python -m seedsmith check ../../data/seed/items --adapter items` → **31 gap, 78 note, 1
    not_measured** — byte-for-byte identical to the pre-D4 baseline, confirming the `registries.py`
    edit introduced zero regressions to existing item reporting

### ✅ CP-D4 — closes Part 4 — **REACHED 2026-08-31**
- [x] Full seedsmith suite green — **392/392**
- [x] `dotnet test` green across Core / Data / Guard — see the full-program sweep below;
      four `scripts\guard-*.ps1` green
- [x] Exactly **one** file outside `adapters/creatures/` changed in D4 — `adapters/items/registries.py`,
      adding a vocabulary (`load_theme_keys()`, an optional `creature_theme_keys` param) not a concept
- [x] An item can be authored themed to a creature and validates —
      `test_a_creature_key_becomes_legal_once_unioned_in`

## Part 4 standing rules (in addition to the program's)

- **`basis` is never optional.** It is an input to a correctness check (A2), not an audit trail.
- **`blocked` is an answer, not a failure**, at every stage.
- **Never a number** in creature content — structural, since `channels()` is empty.
- **Append-only means never renumber.** Position feeds derived ids and content hashes.
- **Fixtures synthetic**, and now doubly so: the live roster is no longer a fixed size (§D-F3).
- **Authorized 2026-08-31.** Build proceeded D1 → D2 → CP-D3 (the tautology gate) → D4, all
  reached the same day.

## The real generation run — owner-authorized 2026-09-01, after CP-D4

Every mechanism above was proven against `MockModelServer`, per the standing "no real model calls"
rule. The owner then explicitly authorized spending real calls against the real local model already
running (`google/gemma-4-26b-a4b-qat` via LM Studio, `http://localhost:1234` — the toolchain's own
documented default, confirmed reachable before anything was sent to it). All six generated artifacts
are now **really committed**, not deferred:

- [x] **`family-candidates.json`** — 11 real batches, 84 creatures, 104.3s wall-clock. **53/84 creatures
      received ≥1 candidate, 31 blocked** (no shared family the model would support — real
      `basis="blocked"` outcomes, not a bug). Real groupings: `cherry-themed` spans 7 creatures,
      `matryoshka-dolls` correctly catches `dollgold`/`dollsilver`.
  - ⛔ **Real defect found and fixed before consolidating:** `extract_family_candidates`'s
    `build_user` callback sent ONLY the raw brief — no JSON-shape instructions at all. It only
    "worked" in tests because `MockModelServer` returns its queued response regardless of prompt
    content. A hand-probe against the real model confirmed the gap; fixed by adding
    `_response_format_instructions()`, appended to every batch's prompt. Mock-based tests
    (unaffected, since they don't depend on prompt content) stayed green throughout; the real
    model's shape-compliance was then re-verified live before running the full 11 batches.
- [x] **`families.v1.json` + `family-assignments.json`** — 53 candidates → **19 real families**
      (`bucket`, `cactus`, `cherry`, `corn`, `dolls`, `double`, `garlic`, `hypno`, `ice`, `fire`,
      `light`, `chomper`, `nut`, `pea`, `sun`, `base`, `fruit`, `sunflower`, `line`).
  - ⛔ **Real defect found and fixed, confirmed both failure directions on the same real batch:**
    `_GENERIC_SUFFIXES` (originally 5 words: type/class/kind/variant/family) was far too narrow for
    what the real model actually produced — labels like `fire-based`, `light-based`, `chomper-kin`,
    `nut-kin`, `pea-kin`, `ice-attackers`, `bucket-users`, `sun-producers`. Left unfixed this
    **silently merged unrelated families** (`fire-based`+`light-based` → one false "based" family;
    `chomper-kin`+`nut-kin`+`pea-kin` → one false "kin" family) — the false-merge direction is the
    more dangerous one, exactly what audit A6 named this module to prevent — **and** split identical
    families apart (`ice-attackers` vs `ice-family` never merged). Fixed by expanding the stopword
    set to the realistic vocabulary of generic relational suffixes. Regression tests added and
    passing: `test_generic_relational_suffixes_do_not_become_the_family_head`,
    `test_generic_relational_suffixes_do_not_falsely_merge_different_themes` — both pin the exact
    real labels that triggered the bug.
- [x] **`motifs.v1.json` + `motif-assignments.json`** — **84/84 creatures** motif-derived (0 blocked,
      100% flavour coverage confirming the earlier S3 measurement), **0 tautological**.
  - ⛔ **Real, more serious defect found and fixed:** `own_motifs`'s tokenizer treated Chinese text
    as "maximal punctuation-free run" — since Chinese carries no spaces between words, this returned
    **whole sentence clauses** as single "motifs" (e.g. `以下能防止爆炸樱桃产生溅射`, an entire
    clause), unusable as shared vocabulary. No regex can fix this — Chinese word segmentation needs
    linguistic knowledge a regex does not have. **Fix required a new dependency** (`jieba`, real
    Chinese segmentation), which the program's own standing rule ("stdlib only outside `pipeline`")
    does not permit without sign-off — asked the owner directly rather than adding it silently or
    quietly downgrading to a worse dependency-free heuristic; **approved 2026-09-01**, scoped to
    this one module's tokenizer. A curated Chinese stopword list (particles/common verbs, `_CJK_
    STOPWORDS`) filters function words jieba's segmentation alone doesn't remove. Regression test:
    `test_chinese_flavor_text_produces_real_short_words_not_whole_clauses`, using the exact clause
    that triggered the bug. **Verified clean on the full real output**, not just the fixture: every
    one of the 120 distinct real tokens across all 84 creatures is ≤4 characters — zero whole-clause
    fragments remain anywhere. (**120 is a snapshot**, like S7's coverage split: G1's prose filter
    and the later `l`-tag fix both re-derived the vocabulary, which now holds **135** distinct
    tokens. The **≤4-character invariant is the claim**, and it still holds at 135/135 — re-checked
    2026-09-01 and pinned by `test_no_non_blocked_creature_was_left_without_motifs_by_the_filter`.)
- [x] **`themes.v1.json`** — **84 real themes published**, all `creature.*`-prefixed, 0 blocked.
      Rarity distribution **7 legendary / 14 epic / 21 rare / 42 common** — exact match to the
      catalog's own known split, confirming the rarity-snapshot wiring is correct.
- [x] **All 38 pre-existing legacy `theme.*` themed entries re-verified against the real corpus
      with real creature themes now present** — `python -m seedsmith check ../../data/seed/items
      --adapter items` unchanged from the pre-generation baseline (31 gap, 78 note, 1 not_measured).

**Verify (after the real run):** `python -m pytest -q` (from `gk-forge/tools/seedsmith/`) → **395/395**;
`dotnet test tests\FusionRpg.Core.Tests` → **4896/4896**; all four `scripts\guard-*.ps1` → green.

**One honest limitation, not silently smoothed over:** `Distribution/MotifSharing` still reports
"no creature entry carries motif data yet" when run live, even with `motif-assignments.json` real and
committed — because nothing merges that file's contents back onto the `creature`-kind corpus entries
`Corpus.load` reads. This was never an explicit task in either source-of-truth file (D3.2's own
spec always described reading `entry.get("motifs")` as depending on future wiring, not on this
run); it is a genuine, separate, unspecced integration step, not a gap in what this run was asked
to produce.

---

# Part 5 — Feature 3: generation runtime (G0–G4)

Plan: [seedsmith-plan.md](seedsmith-plan.md) Part 5. Specs: five modules under
[docs/architecture/seedsmith/](../docs/architecture/seedsmith/), **SEALED — approved by the owner
2026-09-01, authorized to build.** Zero open questions: all closed by measurement
([spec audit](../docs/architecture/seedsmith/review/audit-generation-runtime-specs.md), 10 findings).

**Read the locked-decisions table in the plan before starting** — engine, checkpoint store, model,
motif instrument, CoVe status and one-per-creature were each settled with evidence and are not to be
re-argued mid-build.

## Phase G0 — dependency baseline ⛔ BLOCKING

- [x] **G0.1 — `pyproject.toml`, exact pins, lockfile, isolated venv** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `pyproject.toml` declares `jieba`, `langgraph==1.2.11`, `langgraph-checkpoint-sqlite`
    - [x] Every pin is `==`, **never** `>=` — LangGraph shipped 10 releases in 2026-04 alone
    - [x] `requirements.lock` committed with the full transitive set — **44 packages** (corrected from the planned '~31'), incl. `langsmith`
    - [x] CI installs from the lockfile in a clean environment
    - [x] ⚠️ CI step positioned so its failure **cannot be masked** by the known `ci.yml` defect
          (only the last `dotnet test` exit code is checked)
  - Verify: fresh clone → `python -m venv` → `pip install -e ".[dev]"` → `pytest` → **full suite passes**
  - Files: `gk-forge/tools/seedsmith/pyproject.toml`, `gk-forge/tools/seedsmith/requirements.lock`, `.github/workflows/ci.yml`

- [x] **G0.2 — offline guarantee as a test** · **S** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `LANGSMITH_TRACING` and `LANGCHAIN_TRACING_V2` asserted **unset**
    - [x] A graph runs under a socket guard raising on any non-loopback connect → **zero attempts**
    - [x] Test uses stdlib `socket` patching — no new dependency to test that we have few
  - Verify: `python -m pytest tests/test_offline_guarantee.py -q`
  - Files: `gk-forge/tools/seedsmith/tests/test_offline_guarantee.py`

- [x] **G0.3 — `response_format` constrained decoding in `llm_caller`** · **S** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] Optional `schema` parameter, `None` default
    - [x] ⛔ `call_model(schema=None)` produces a **byte-identical** request body to today — this
          module must be provably inert for every existing caller
    - [x] With a schema: response parses with plain `json.loads`, no fence stripping needed
    - [x] An `enum` field cannot produce an out-of-enum value (measured: it could not)
    - [x] `extract_json` **still present and still tested** — defense-in-depth, not replaced
  - Verify: `python -m pytest tests/test_llm_caller.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py`, `gk-forge/tools/seedsmith/tests/test_llm_caller.py`

### ✅ CP-G0 — **REACHED 2026-09-01**
- [x] Fresh clone + clean venv + lockfile install + full suite **passes** — created `.venv-verify`,
      `pip install -e ".[workflow,dev]"` from `pyproject.toml` alone, **404 passed**
- [x] `import jieba` succeeds in a fresh venv — **jieba 0.42.1 OK**; the D2.3 debt is paid
- [x] Offline guarantee is a passing test — **4/4**, including a falsifier proving the socket guard
      itself fires on a real non-loopback address (a guard that cannot fail proves nothing)
- [x] Every existing `llm_caller` caller is provably unchanged —
      `test_schema_none_body_is_byte_identical_to_explicitly_passing_none` compares two recorded
      request bodies; `test_schema_none_produces_a_body_with_no_response_format_key` asserts the
      absence directly

**Evidence beyond the checklist:**
- **Lockfile:** 44 packages, generated from the clean install (`requirements.lock`).
- **Real-model probe** (not just mocks): same hostile prompt demanding prose, ```json fences and an
  out-of-enum `basis`. Unconstrained → prose paragraph, `json.loads` **FAILED**. Constrained →
  `{"label": "Undead / Construct", "basis": "text"}`, parsed, **enum respected**.
- **CI now installs from the lockfile** (`.github/workflows/ci.yml`, new step before the seedsmith
  reachability step, each command `throw`-guarded so failure cannot be masked). YAML validated.
- **Graceful degradation confirmed:** ambient conda env (no `workflow` extra) → **402 passed,
  2 skipped** — the LangGraph tests `importorskip` rather than fail. The measurement half of
  seedsmith still runs without the workflow engine, which is why `langgraph` is an extra.

## Phase G1 — motif prose filter (no model, no framework)

- [x] **G1.1 — four-rule line classifier** · **S** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `韧性：270+2200（一类）`, `伤害：20/1.5秒` → **mechanical** (rule 1)
    - [x] `特点：…`, `融合配方：…` → **mechanical** (rule 2)
    - [x] ⛔ `②处于火力覆盖模式时…` → **mechanical** (rule 3) — the 13-line leak the audit found
    - [x] ⛔ `对于血量高于50%的…` → **mechanical** (rule 4)
    - [x] ⛔ `可在三种攻击模式之间切换` → **prose** — proves rule 4 is ASCII-only and does not over-filter
    - [x] A prose sentence with a mid-clause colon → **prose** (the ≤12-char label bound)
    - [x] `classify_line` is a pure function, exported and tested directly
  - Verify: `python -m pytest tests/test_motif_derive.py -q`
  - Files: `seedsmith/adapters/creatures/motifs.py`, `tests/test_motif_derive.py`

- [x] **G1.2 — POS filtering via `jieba.posseg`** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] Keep `n*`/`v*`/`a*`/`i`/`l`; drop `r`/`c`/`d`/`p`/`u`/`t`
    - [x] ⛔ `为什么`/r, `是因为`/c, `不过`/c **dropped** — the `bucketnutzombie` regression, pinned
    - [x] ⛔ `铁头功`/n, `坚果`/n, `练成`/v **kept** — proves it is not deleting everything
    - [x] `_CJK_STOPWORDS` reduced to a small override list, no longer the primary mechanism
  - Verify: `python -m pytest tests/test_motif_derive.py -q`

- [x] **G1.3 — wire in, regenerate, verify** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `flavorIntroduce` preferred where present (18/84 creatures)
    - [x] ⛔ Three named regression creatures: `一类`, `伤害`, `优先` **gone**
    - [x] Same corpus filtered twice → byte-identical
    - [x] Max token length still ≤4 (the D2.3 whole-clause guard)
    - [x] A creature losing all prose falls back to name (`basis="name"`) — **not an error**
    - [x] Rise in `basis="name"`/`blocked` counts **reported as a result**
  - Verify: `python -m seedsmith creatures motifs`; `python -m pytest -q`
  - ⚠️ **Append-only correction, owner-visible:** regeneration **drops** motif ids like `一类` from
    `motifs.v1.json`. Safe **only because nothing is bound to them** — all 84 creatures currently have
    zero generated content. **This window closes when G4 writes its first row.** A reviewed
    correction of bad data, not a routine re-run.

### ✅ CP-G1 — **REACHED 2026-09-01**
- [x] Stat lines contribute **zero** tokens — all three named regression creatures fixed:
      `bucketnutzombie` `['一类','击杀']` → `['铁头功','僵尸']`;
      `cherrynut` `['伤害','僵尸']` → `['僵尸','樱桃','喜爱']`;
      `cactus` `['仙人掌','优先']` → `['仙人掌','发射']`.
      Sharpest single improvement: `allpeater` `['三种','三线','之间','会均','伤害']` →
      **`['分配','切换','攻击','模式','火力']`**
- [x] Both POS regression sets pinned — `test_pos_filter_drops_narrative_connectives_from_flavor_introduce`
      (为什么/是因为/不过/其实/也许/至少 all dropped) **and**
      `test_pos_filter_keeps_real_content_words` (铁桶/坚果/核桃/补脑/练成/铁头功 all kept). The second
      is what stops a filter that simply deletes everything from passing the first
- [x] Determinism and ≤4-char guarantee hold — regenerated twice, `diff` **byte-identical**;
      max token length **4**, zero tokens over 4 chars
- [x] `motifs.v1.json` regenerated as a reviewed act, before any content binds to it — 84 creatures,
      **140 motifs**, basis 53 text / 31 name, 0 tautological

**Two findings worth recording:**

1. ⛔ **There was no committed generation entrypoint at all.** The 2026-08-31 "real run" was
   scratch scripts that lived nowhere in the repo — the artifacts existed and **nothing could
   reproduce them**, the exact opposite of this program's determinism claim. G1.3 therefore had to
   *build* `adapters/creatures/generate_motifs.py`, not just call something. Regeneration is now a
   real, reviewable, deterministic entrypoint.
2. ✅ **`伤害` survives in 6 creatures, and that is correct.** Traced each: they are genuine sentences
   (`地刺能扎破轮胎，并对踩在上方的僵尸造成伤害。` — "spikes puncture tires and deal damage"), not
   stat rows. The filter now distinguishes *"damage as a stat-field label"* from *"damage as a word
   in a sentence"*, which is exactly the intent. `僵尸` also survives in 42 creatures — **expected and
   in-spec**: §2.4 explicitly scopes corpus-frequency exclusion OUT of this module, and POS keeps it
   because it is a legitimate noun.

Verify: `python -m seedsmith.adapters.creatures.generate_motifs`; full suite (clean venv) → **413 passed**

## Phase G2 — workflow runtime (parallel with G1 once G0 lands)

- [x] **G2.1 — state + nodes, no LangGraph** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `GenerationState` TypedDict; every field bounded, **no `messages` accumulator**
    - [x] `nodes/` are plain `(state) -> dict` functions, unit-testable with a plain dict
    - [x] ⛔ **Seam test: zero LangGraph imports in `nodes/` or `state.py`** — asserted by grep,
          not left to discipline. This is the deliverable
  - Verify: `python -m pytest tests/test_workflow_structure.py -q`
  - Files: `seedsmith/workflow/{state.py,nodes/*}`, `tests/test_workflow_structure.py`

- [x] **G2.2 — graph skeleton and bounded loops** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `START → brief → generate → validate → route → {persist|generate|escalate} → END`
    - [x] Three independent stops: `attempts`, `recursion_limit`, terminal `escalate`
    - [x] ⛔ A deliberate routing bug is **still stopped** by `recursion_limit` — the backstop is
          exercised, not merely configured
    - [x] Clean draft → `attempts == 1`; defective → repair carries the **named** defect
    - [x] Never-clearing draft → **escalates**, writes nothing
    - [x] **No unbounded `while`** anywhere in the module
  - Verify: `python -m pytest tests/test_workflow_runtime.py -q`

- [x] **G2.3 — checkpointing and resume** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `SqliteSaver`, thread-id per subject
    - [x] ⛔ Kill mid-run, re-invoke same thread-id → resumes; **finished nodes do not re-call the model**
    - [x] ⛔ **Transient** retry = replay from checkpoint, **zero** new model calls
    - [x] ⛔ **Quality** retry = a genuinely new generation with the defect attached
    - [x] The two are demonstrably **different code paths**
    - [x] `sqlite3` used for checkpoints only; Python still never reads the game's SQLite
  - Verify: `python -m pytest tests/test_workflow_runtime.py -q`

- [x] **G2.4 — bounded fan-out runner** · **S** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] Bounded worker count, a structural constant with a comment (not a tunable)
    - [x] Results deterministic per subject regardless of completion order
  - Verify: `python -m pytest -q`

### ✅ CP-G2 — **REACHED 2026-09-01**
- [x] Zero LangGraph imports outside `graphs/`, asserted —
      `test_nodes_and_state_never_import_langgraph`, **AST-based** (the rule is "must not IMPORT
      the engine", not "must not mention it"; these modules legitimately discuss the seam in prose)
- [x] Graph structure assertable **offline** — nodes enumerable and mermaid emitted with no model
      and no network
- [x] Crash-resume works and skips completed nodes —
      `test_resume_replays_from_checkpoint_without_calling_the_model_again` asserts the injected
      call count stays at **1** across a run plus a resume
- [x] `recursion_limit` backstop exercised — `test_recursion_limit_still_stops_a_deliberately_broken_router`
      monkeypatches the router into a never-escalating loop and proves the engine still terminates it.
      Stop #2 is tested, not merely configured
- [x] Transient vs quality retry proven distinct — transient is `resume()` (replay, **zero** new
      model calls); quality is the `validate → generate` edge (**new** generation, defect named,
      asserted present in the second prompt)

⛔ **The seam test caught a real violation in my own first draft.** `runner.py` imported
LangGraph (`SqliteSaver`, `RECURSION_LIMIT`). **Rather than widen the rule to accommodate it, the
dependency was removed**: `open_checkpointer` moved to `graphs/checkpoint.py`, `RECURSION_LIMIT`
moved to the engine-free `state.py`, and `runner.py` now drives a compiled app through duck-typed
`.invoke()` with no engine import at all. The seam is stricter than when I wrote the spec.

**Graceful degradation confirmed:** clean venv (workflow extra) → **432 passed**; ambient env
without the extra → **418 passed, 7 skipped**. The measurement half of seedsmith runs without the
workflow engine, which is why `langgraph` is an optional extra rather than a hard dependency.

## Phase G3 — quality gates

- [x] **G3.1 — deterministic validator library** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] `motif_coverage` rejects output using none of the subject's motifs
    - [x] `anti_motif_violation` rejects output using a word the subject is defined against
    - [x] ⛔ `field_echo` **rejects** `{"doctrine": "DOCTRINE: …"}` — the exact observed defect
          (7 of 8 outputs), pinned
    - [x] ⛔ `field_echo` **accepts** `{"doctrine": "The doctrine of …"}` — over-refusal is its own
          defect; a rule rejecting any mention would pass its rejection test while breaking real prose
    - [x] `non_empty` rejects empty/whitespace required fields
    - [x] Defect strings name the **field and the offending value** (they feed the repair prompt)
  - Verify: `python -m pytest tests/test_quality_gates.py -q`

- [x] **G3.2 — tier labelling** · **S** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] Every validator result carries its tier
    - [x] ⛔ No summary anywhere reports a tier-2 pass rate as "quality" — the measured 8/8-on-bad-
          content gap is the reason this rule exists
  - Verify: `python -m pytest tests/test_quality_gates.py -q`

- [x] **G3.3 — CoVe: specified, wired off** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] ⛔ Every verification question **answerable from source alone** — a subjective question is
          a defect (subjective form measured **1/3**, useless)
    - [x] Verifier is **not shown the draft's justification**, asserted structurally
    - [x] Rejects only on **explicit contradiction**; rejection → **escalate**, never auto-repair
    - [x] CoVe schema carries **no verdict field**
    - [x] ⛔ **Not wired into the default graph**, asserted — specified, not built
    - [x] Self-consistency implemented and **asserted off**
  - Verify: `python -m pytest tests/test_cove.py -q`

### ✅ CP-G3 — **REACHED 2026-09-01**
- [x] Four validators with positive **and** negative tests — 15/15 in `test_quality_gates.py`.
      The decisive pair is `field_echo`: it **rejects** `"DOCTRINE: ..."` (the 7-of-8 observed
      defect) and **accepts** `"The doctrine of the shell wall."` — a rule rejecting any mention of
      the field name would have passed its own rejection test while silently breaking real prose.
      The separator is what distinguishes prompt leakage from a sentence
- [x] Tier labelling enforced — `ValidatorResult.summary()` renders
      `"[tier 2: deterministic] mechanically valid"`, and a test asserts the words *good* and
      *quality* never appear in it. Measured 8/8 pass on visibly shoehorned content is why
- [x] CoVe present, disabled, asserted — `COVE_ENABLED is False`;
      `test_cove_is_not_wired_into_the_default_graph` confirms the skeleton has four nodes and CoVe
      is not one; the disabled node is proven inert (its `ask` callback fails the test if invoked)
- [x] Zero real model calls in the suite — every CoVe/validator test uses injected callables

**The ambiguity that made CoVe useless is now a mechanical rule.** `is_source_grounded()` rejects a
question containing *meaningful / quality / rate / score / good*, and `make_cove_node` raises
`SubjectiveQuestionError` on one. Measured: the subjective form agreed with human judgement **1/3**
(it passed both shoehorned cases, rationalising them); source-grounded scored **2/3**. Because the
subjective form was what the spec's own author built on the first attempt from the spec's own
wording, the rule could not stay prose.

**And rejection escalates, never auto-repairs** — CoVe's one miss was a false positive on good
content, and an unreliable judge must not silently drive the repair loop.

Verify: `pytest tests/test_quality_gates.py tests/test_cove.py -q` → **15 + 8 passed**;
full suite → **455 passed**

## Phase G4 — commander-effect (the first real generator)

- [x] **G4.1 — brief, schema, gate** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] Brief inlines motifs, anti-motifs and the expression rule **literally**; cites nothing
    - [x] Schema passes `audit_schema` (**no numeric field**) and `audit_open_loop_schema`
    - [x] Schema audited at **import time** (an unusable schema cannot be registered)
  - Verify: `python -m pytest tests/test_commander_effect.py -q`

- [x] **G4.2 — graph wiring** · **S** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] Thin wiring over G2's shared skeleton; no new control flow
    - [x] ⛔ A `blocked` creature **generates nothing** — an answer, not a failure
    - [x] ⛔ An **unprefixed** id (`wallnut` not `commander-effect.wallnut`) **fails corpus load** —
          `Corpus.add` raises on duplicate ids across all kinds; the creature `wallnut` would collide
    - [x] Re-run over unchanged input → **zero** new writes (G2 idempotence)
    - [x] Same corpus generated twice against the mock → byte-identical
  - Verify: `python -m pytest -q`

- [x] **G4.3 — real run + quality sample** · **M** ✅ **BUILT + VERIFIED 2026-09-01**
  - Acceptance:
    - [x] ⛔ **Only after G1 has landed** — generating from `一类`/`僵尸` motifs would bake stat
          vocabulary into committed, append-only content
    - [x] Every non-blocked creature has a commander effect; committed
    - [x] `Coverage/CreatureUncovered` count **falls** by that number
    - [x] ⛔ **Quality reported from a read stratified sample**, never from the tier-2 pass rate
    - [x] If shoehorning **persists** after G1, that is the trigger to build CoVe — record the
          measurement either way
  - Verify: `python -m seedsmith creatures generate --kind commander-effect`;
    `python -m seedsmith check ../../data/seed/creatures --adapter creatures`

### ✅ CP-G4 — closes Part 5 — **REACHED 2026-09-01**
- [x] Full seedsmith suite green — **467 passed** (clean venv); four guard scripts green
- [x] `Coverage/CreatureUncovered` reduced — **84 gaps → 0**, verified by a real `check` run against
      the live corpus. **84/84 creatures** now carry a commander effect
- [x] Quality reported from a **read sample**, separately from the pass rate — and reading is what
      found the two defects below, neither of which any pass rate showed
- [x] CoVe build decision recorded — **still not built, and the run reinforced that.** Both real
      defects were mechanically checkable, so both were fixed in **tier 2** at zero model cost.
      CoVe would have caught neither (both were source-consistent, just badly written)

**Final real run: 84/84 persisted, 0 escalated, 119s** (`--workers 3`, local gemma-4-26b-a4b-qat).
Every entry carries `_provenance`, a namespaced id, a `creatureId`, and **no numeric field**.

- [x] **G4.4 — corpus-wide near-duplicate check on `doctrine`** · **S** ✅ **BUILT + VERIFIED 2026-09-06**
  Found auditing whether every seedsmith generator has a deterministic pre-generation
  coverage/distribution check, not only `adapter-items`/`tree-plan`. `commander-effect` did not —
  `quality-gates` validates per-item only, nothing watched convergence across the corpus, despite
  the module's own §9 probe already reproducing the failure (3 generations for one creature, Jaccard
  mean 0.52).
  - Acceptance:
    - [x] Verified real first: a direct Jaccard check against the already-committed 84-entry corpus
          found **two near-duplicate `doctrine` pairs**, clearest at Jaccard 0.52
          (`doublecherry`/`doubleshooter`), unnoticed since the 2026-09-01 run
    - [x] `KindSpec.dedup_fields: frozenset[str] = frozenset()` added (`adapters/base.py`), additive,
          same shape as `motif_expression` — every kind before this untouched
    - [x] `commander-effect`'s `KindSpec` sets `dedup_fields=frozenset({"doctrine"})`
    - [x] `SemanticDedup` gained exact (6.1c) and near-duplicate (6.2b) checks over any kind's
          declared prose field(s)
    - [x] 6.2b compares **directly** (all-pairs exact Jaccard), not via MinHash+LSH — verified live
          that 8-band/4-row LSH missed the corpus's own clearest pair entirely; a prose-dedup kind
          is bounded in the low thousands (`commander-effect`'s ceiling ~900), where direct
          comparison is cheap and exact
    - [x] 7 new tests (`ProseDedupTests`), including a known-answer test pinned against the live
          corpus
  - Verify: `python -m pytest gk-forge/tools/seedsmith/tests/test_constraint_exemplar_dedup.py -v` (19
    passed); full suite **1,777 passed, 1 skipped, 1 pre-existing unrelated failure**
    (`test_general_propose.py`'s hash-determinism issue in the actions pipeline — confirmed
    untouched by this change)
  - **Not fixed here:** the real `doublecherry`/`doubleshooter` pair. Re-generating or editing
    either doctrine is a content decision for the owner; this task closes the coverage gap, not the
    specific finding it now reports.

### ⛔ Two defects that a 100% pass rate completely hid

**1. Code-switching — 87% of output, caused by our own validator.** The first real run scored
83/84 mechanically, and reading it showed *"When a 僵尸 enters the fray, the squad attempts to force
a 变心..."* — English prose with Chinese motif tokens spliced in. **`motif_coverage` caused it**: it
requires motifs VERBATIM, the motifs are Chinese, and the model's default register was English, so
it satisfied the checker by splicing. The 8 wholly-Chinese drafts read markedly better.
→ Added `language_consistency` (tier 2, fires only when motifs are CJK, so an all-Latin corpus is
unaffected) + made the prompt state the language. **Result: 87% → 0%.**

**2. Every effect was named after its own creature — found by a metric, not a validator.**
`SemanticDedup/NearDuplicate` reported **83 gaps**: `commander-effect.cactus` was named `仙人掌`,
identical to the creature `cactus`. **No per-item validator could see this** — it needs the corpus,
which is precisely why the corpus-level metric exists. Same class as `field_echo` one level out:
there the value echoed its FIELD name, here its SUBJECT name.
→ Added `subject_name_echo`. **Result: 83 → 6 duplicate names; 78/84 now distinct.**

Both fixes made the final run *better AND faster* (431s → 119s, zero escalations): a clearer target
means fewer repairs. `cornpot`, which escalated twice under the earlier prompt, succeeded.

**Quality sample after the fixes** (read, not counted):
`hypnopeashooter` → 心智篡夺 — 通过精神干扰使敌方僵尸发生变心，使其在作战中转而攻击同伴。
`cherrybomb` → 樱桃爆裂 — 当樱桃靠近僵尸时，全队将引发连锁爆炸，摧毁目标区域内的所有单位。
`pumpkin` → 屋顶防线 — 在屋顶区域展开保护，为后方的植物提供屏障。

## Part 5 standing rules

- **The seam is the deliverable.** LangGraph imports live only in `graphs/`; a node is a function
  you can call with a dict.
- **Bound every loop three ways.** Not stopping is 28.1% of field-observed agent failures.
- **Transient ≠ quality retry.** Replay vs regenerate; conflating them is where the cost bugs live.
- **A pass rate is not quality.** Measured 8/8 on visibly shoehorned content.
- **Cheapest instrument first.** No model where a `==` or a POS tag decides it.
- **G1 before G4's real run.** Non-negotiable; append-only content cannot be un-bound.

---

# Cross-part final verification — 2026-09-01

Run after CP-G4 to check the whole program, not each part in isolation. Per-part checkbox census:
Part 1 = 82, Part 2 = 38, Part 3 = 21, Part 4 = 107 (+5 standing rules), Part 5 = 111 —
**364 checked, 0 unchecked.** Per-part test counts: 157 / 68 / 79 / 105.

## ⛔ Defect found by this sweep (not by any part's own gate) — FIXED

**All 84 themes in `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json` carried pre-G1 motifs.**

`themes.v1.json` **embeds** each creature's motifs. G1 (`motif-prose-filter`) changed every creature's
motifs in `_generated/motif-assignments.json`; the theme registry, published in D4 *before* G1, was
never regenerated. So a shipped registry claimed `allpeater`'s theme was
`['三种','三线','之间','会均','伤害']` (stat vocabulary — armour classes, damage rows) while its real
motifs had moved to `['分配','切换','攻击','模式','火力']`.

**Why nothing caught it.** Every part's gate measured its own artifact. Part 4's D4 checked that
themes *publish correctly*; Part 5's G1 checked that motifs *filter correctly*. Neither compared the
derived artifact to the artifact it was derived from — the exact defect class a per-part gate cannot
see. This is the third time this session a metric passed while the content was wrong.

- [x] **X1 — Prove the fix is safe before doing it.** `themes.v1.json` is append-only
  (spec-creature-themes.md §2.4a: a published theme is a snapshot, never re-derived), so a rebuild needs
  the same justification G1.3's motif regeneration had: **nothing is bound yet.** Measured — the
  items corpus references 38 themed entries, all legacy `theme.*`, and **zero** `creature.*` keys. The
  window closes the moment an item is authored against a creature theme; after that a motif correction
  needs `themes.v2.json` plus a migration. Recorded in the module docstring, not just here.
- [x] **X2 — Commit the regeneration entrypoint.** `seedsmith/adapters/creatures/generate_themes.py`,
  with `--rebuild` documented as a reviewed correction. Previously the registry could only be
  produced by a scratch script that lived nowhere — the same "nothing can regenerate this artifact"
  gap G4.3 already fixed for commander effects.
- [x] **X3 — Rebuild and verify.** `--rebuild` → `{"themes": 84, "retired": 0}`; 0 stale vs
  `motif-assignments.json`. Running it twice is **byte-identical** (no timestamp, no ordering churn),
  so it is safe in CI.
- [x] **X4 — Pin it with a test, since no metric compared the two artifacts.**
  `test_published_themes_carry_the_current_motifs` fails loudly with the exact re-run command;
  `test_every_theme_carries_both_expression_rules_and_a_rarity_snapshot` covers structure.
  `tests/test_creature_themes.py` 16 → 18 tests.

## Sweep result

- [x] **X5 — Swept every other derived/derived-from pair in the creature tree for the same class.**
  `motifs.v1.json` vs `motif-assignments.json` (140 registry = 140 distinct motifs in use, exact);
  `families.v1.json` vs `family-assignments.json` (19 = 19, zero dangling); `commander-effect/all.json`
  vs `motif-assignments.json` (84 = 84, no orphan either way). All consistent. One near-miss
  investigated and dismissed: 4 tokens (`含铁 大家 种植 花盆`) appear in assignments but not the
  registry — all four are **anti**-motifs, and `generate_motifs` builds the vocabulary from `.motifs`
  alone, so motifs-only is the design, not drift. Both invariants now pinned
  (`test_motif_derive.py` 26 → 28).

- [x] seedsmith Python suite: **471 passed** (467 before this sweep; +2 from X4, +2 from X5).
- [x] Theme staleness: **0 / 84**.
- [x] Rebuild determinism: byte-identical across two runs.
- [x] C# suites re-run rather than argued — Core **4896**, Data **548**, Guard **142**, all green.
  (The creature rebuild could not have reached them anyway: `ItemSeedValidator` reads
  `gk-data/packs/fusion/data/seed/items/_registry/themes.v1.json`, a different, frozen file with a different schema.)

## Standing rule this adds

- **An artifact that embeds another artifact's content needs a test comparing the two.** A per-part
  gate measures its own output and is structurally blind to staleness across a part boundary. If a
  file copies data it did not compute, the copy rots the moment the source changes — and the only
  thing that notices is a test that reads both.

---

# ⛔ The `l`-tag hole — found 2026-09-01 while proving CP-G1, fixed end to end

The plan's 24 checkpoint criteria had never been ticked (the todo's were; the plan's mirror was
missed). Proving them rather than ticking them found a **second** defect of the same family as the
theme staleness, and this one had reached shipped content.

## What was wrong

jieba tags multi-character narrative connectives as **`l`** (习用语, colloquial set phrase), and `l`
was in `_CONTENT_POS`. So G1.2's POS filter — built precisely to drop narrative scaffolding — let
them straight through as motifs: `从那之后` ("from then on"), `发现自己` ("discovered oneself"),
`一段时间`, `随处可见`, `毋庸置疑`, `更进一步`, `并不知道`, `很难说`, `不多见`.

**Why it mattered rather than being cosmetic:** `motif_coverage` *requires* a motif to appear in the
generated text. A junk motif therefore becomes **mandatory junk in committed, append-only content**:

| creature | shipped before | after |
|---|---|---|
| `normalzombie` | 「**随处可见**的消耗」 | 「无名之辈」 — 每一个个体都不配拥有名字 |
| `flagzombie` | …发出**毋庸置疑**的指令 | 「旗帜引领」 — 手中紧握旗帜，带领一大群僵尸向前冲锋 |
| `ironpeazombie` | …直到**发现自己**受到致命伤害 | 「塔罗牌式弹幕」 |
| `polevaulterzombie` | …能够**更进一步**地进行位移 | 「长杆跃迁」 |
| `cherrythreepeater` | 在**一段时间**内… | 在三行内持续发射 |

Seven creatures, every one passing every gate at 100%. The existing regression set could never have
caught it: `为什么`/`r`, `不过`/`c` are tagged as *function words*; these are tagged as *content*.

## What was done

- [x] **L1 — Fix the filter.** Removed `l` from `_CONTENT_POS`; kept `i` (成语 — `人心惶惶`,
  `江郎才尽` are evocative, not scaffolding) and `j`. The rationale, the measured evidence and the
  accepted cost are written into the module, not just here.
- [x] **L2 — Measure the cost honestly.** Dropping `l` also loses 2 real motifs, `无人机` ("drone")
  and `绕道而行` ("detour around") — 11 `l`-tagged motifs total, 9 junk, 2 real. Accepted because a
  motif is a **mandatory** creative seed: a bad one corrupts output, a missing one costs nothing
  while the creature still has others. Borne out by the regeneration — `garlic` lost `绕道而行` and its
  new doctrine still says 「迫使所有试图靠近的僵尸改变行进路线」. The *meaning* survived in prose.
- [x] **L3 — Regenerate motifs.** 9 of 84 creatures changed, all improvements
  (`ironpeazombie` `['从那之后','发现自己','塔罗牌','伤害','僵尸']` → `['塔罗牌','伤害','僵尸','发射','子弹']`).
  **No regression:** `basis` split held at 53 `text` / 31 `name`, and **0** non-blocked creatures were
  starved of motifs — the real risk when tightening a filter.
- [x] **L4 — The theme test proved itself.** Changing motifs made `themes.v1.json` stale again, and
  `test_published_themes_carry_the_current_motifs` (added hours earlier) **failed**, naming all 9
  creatures and printing the exact re-run command. A regression test that has caught a real regression,
  not a decorative one. Rebuilt → 0 stale.
- [x] **L5 — Build the idempotency CP-G4 always required.** `Re-run produces zero new writes` was an
  unticked plan criterion and was **genuinely unmet**: the generator had no skip logic and rewrote
  all 84 entries stochastically, so any re-run destroyed good content. Added `_provenance.motifs`
  (recording what each entry was generated *from*), `stale_ids()`, and skip-existing as the default,
  with `--stale`, `--only` and `--force`. Backfilled provenance on all 84 from the motifs the real
  run actually used — a truthful reconstruction, not a guess.
- [x] **L6 — Regenerate only what was stale.** `--stale` → **9 generated, 75 kept, 0 escalated,
  11.9s**. Not 84. The 75 good entries were never at risk.
- [x] **L7 — Verify by reading, not by pass rate.** All 9 read individually; 0 connectives remain
  anywhere in the 84 committed entries; `Coverage/CreatureUncovered` still **no findings**.
- [x] **L8 — Cover it three ways**, since one test would only have caught one layer:
  `test_narrative_connectives_tagged_l_are_dropped` (POS layer, with the premise asserted so the
  test fails loudly if jieba's tagging moves), `test_idioms_and_abbreviations_are_still_kept` (the
  opposite direction — a filter that drops everything would pass the first test),
  `test_no_non_blocked_creature_was_left_without_motifs_by_the_filter` (the starvation risk), and
  `test_no_committed_effect_contains_a_narrative_connective` + `test_every_committed_entry_is_current_against_the_live_corpus`
  (content layer, independent of the filter).

## Plan criteria

All **24** checkpoint criteria in `tasks/seedsmith-plan.md` (CP-G0 ×4, CP-G1 ×5, CP-G2 ×5, CP-G3 ×4,
CP-G4 ×6) are now ticked **with the evidence inline**. 23 were already satisfied and needed proving;
**1 (`Re-run produces zero new writes`) was not satisfied and needed building.**

## Evidence

| Check | Result |
|---|---|
| Fresh venv from `requirements.lock` (scratch dir, not the dev venv) | **480 passed** |
| Main venv full suite | **480 passed** (467 at the start of this sweep; +13) |
| `Coverage/CreatureUncovered` on the live corpus | **no findings** |
| Plain generator re-run | `all.json` **byte-identical** (md5 unchanged) |
| Connectives in committed content | **0 / 84** |
| Theme staleness | **0 / 84**; rebuild byte-identical across runs |
| Four `guard-*.ps1` | all **PASS** |

## Standing rule this adds

- **A quality gate that *requires* something makes bad inputs mandatory.** `motif_coverage` turned a
  junk motif into junk that HAD to appear in the output. When a validator enforces presence, the
  vocabulary it enforces against becomes load-bearing — garbage in is not merely tolerated, it is
  *compelled*. Validate the vocabulary as strictly as the output.

---

# Final-proof pass — 2026-09-01: reading the audit, not counting its boxes

A checkbox census said 0 unchecked and was **not proof**. Reading both files end to end, then
mechanically verifying every artifact and number they claim, found **three more open items** that no
checkbox could show — one of them flagged in the audit's own prose as unresolved.

## What was verified mechanically (not read, executed)

| Claim class | Method | Result |
|---|---|---|
| 29 referenced test files exist | path check | 28 exist; 1 (`test_parity_seed_graph.py`) **deliberately deleted**, recorded in S10 step 4 |
| 29 referenced modules exist | path check | all exist |
| 10 per-file test counts (`15/15`, `24/24`, …) | `pytest --collect-only` each | **all match or exceed** |
| S2 `Coverage/EmptyPartition` → exactly 9 | live run | **9 gap** ✓ |
| S4 `Coverage/PairwiseHole` → 6 | live run | **6 gap** ✓ |
| S8 `Quality/*` → 5 gap, 12 note | live run | **5 gap, 12 note** ✓ |
| S10 CI gate → exit 0 | live run | **exit 0** ✓ |
| S10 suite inside a 30s budget | timed | **19.3s** ✓ |
| D4.2 items baseline → 31 gap, 78 note, 1 not_measured | live run | **identical** ✓ |
| `ItemSeedValidator.Tests` 71/71 | `dotnet test` | **71/71** ✓ |
| `tools/seed_graph/` deleted | path check | gone ✓ |

## Item 1 — S7's coverage figure was a snapshot, not a standing expectation

Recorded `10 claimed, 10 known gap, 0 unclaimed`; actual today **12 claimed, 8 known gap, 0
unclaimed**. Not rot: S8, built *after* that line, claims Appendix-A rows #17/#18, which were
correctly *known gaps* when S7 finished. Annotated in place, naming `0 unclaimed` as the invariant to
check — the claimed/gap split moves every time a metric lands.

## Item 2 — the coverage gap D2.3 flagged in its own prose ✅ CLOSED

D2.3's entry said the `own_contributed` basis fix was "caught by re-deriving the fix from first
principles ... **not by a failing test** ... a real limitation of this module's current coverage."
A checkbox census reads that task as `[x]`. It was an open test gap, named by the audit itself.

- [x] Two tests now pin the rule from **both** sides, and each was falsified independently:
  restoring the original defect (`own_contributed and not d.families`) reddens
  `test_an_own_name_token_that_survives_the_trim_weakens_the_basis` and only that one; deleting the
  survived-the-trim recomputation reddens `test_an_own_token_trimmed_away_does_not_weaken_the_basis`
  and only that one. One test alone would not have closed the gap — a version that always includes
  `own_basis` passes the first and fails the second.
- [x] Two fixture traps recorded, because either yields a test that passes while proving nothing: a
  family pool is built in `sorted(member_ids)` order, so a subject sorting **first** inherits its own
  token back (a different code path); and `_FAMILY_SHARE = 2` means **three** families are needed to
  fill five slots. Both premises are asserted inside the tests, so a moved constant fails loudly.

## Item 3 — 6 live `SemanticDedup/NearDuplicate` GAPs, recorded but never closed ✅ CLOSED

The Part 5 account ends *"83 → 6 duplicate names; 78/84 now distinct"* — an improvement recorded as
a **result**, with no rule declaring the remaining 6 acceptable. They were still GAP-severity
findings against committed content. All six were **sibling pairs** — `doublecherry`/`doubleshooter`,
`dollgold`/`dollsilver`, `pot`/`pumpkin`, `starfruit`/`starpea`, `jalapeno`/`jalastar`,
`chomper`/`nutchomper` — which share families and therefore motifs, so the model converged on one
name for both.

**This is the third time this program has learned the same lesson**, one level further out each
time: `field_echo` (value echoes its FIELD name) → `subject_name_echo` (value echoes its SUBJECT
name) → `name_collision` (value echoes **another subject's** name). No per-draft validator can see a
corpus-level property; that is why the corpus metric exists, and it caught all three.

- [x] Added `name_collision` (tier 2, deterministic, zero model cost — "cheapest instrument first").
  It stays a pure `(draft, context)` function: the generator supplies `takenNames`, so it is
  testable without a corpus.
- [x] Regenerated exactly the 6 second-of-pair creatures via `--only`, keeping the other 78 untouched
  — **6 generated, 78 kept, 0 escalated, 14.2s**. Possible only because the idempotency work landed
  first; before it, this fix would have rerolled all 84.
- [x] **84 entries, 84 distinct names, 0 duplicates.** `seedsmith check` on the creatures corpus went
  **9 gap → 3 gap**; the 3 remaining are the documented `EmptyPartition` roster artifact D1.3
  already records as expected, not a regression.
- [x] Covered six ways, including a corpus-level regression test — the metric is `gates=False`, and
  a finding nobody is forced to look at is a finding that comes back. The registration test was
  falsified **with the anchor verified present first**, after a first attempt silently failed to
  plant (Python cannot see Git Bash's `/tmp`) and passed meaninglessly — the exact
  "a falsifier that fails to plant manufactures confidence" trap G3 already recorded.

## Evidence

| Check | Result |
|---|---|
| Main venv full suite | **488 passed** (467 at the start of this session; +21) |
| Fresh venv from `requirements.lock` (scratch dir) | **488 passed** |
| **Base-only venv, workflow extra NOT installed** | **470 passed, 11 skipped** — the optional-extra claim, re-verified. Accounted exactly: 480 collected (`test_workflow_runtime.py`'s 8 tests are skipped wholesale by a module-level `importorskip`, so never collected) = 470 passed + 10 function-level skips, plus the 1 module skip = 11. **No collection errors** — the measurement half genuinely runs without the engine |
| C# Core / Data / Guard / ItemSeedValidator | **4896 / 548 / 142 / 71** |
| Creatures corpus `check` | **3 gap** (was 9), 0 duplicate names |
| Items corpus `check` | **31 gap, 78 note, 1 not_measured** — unchanged baseline |
| Four `guard-*.ps1` | all **PASS** |

## Standing rule this adds

- **Read the prose, not the checkbox.** All three items above sat inside tasks marked `[x]`. A task
  can be genuinely complete and still record, in its own words, a gap it did not close — D2.3 said
  so explicitly and was still checked. A census cannot see that; only reading can.

---

# Full-audit re-read + evidence map — 2026-09-01

Both files read start to finish, then **every `Verify` command either file declares was extracted
and executed** — 52 distinct commands. The audit's evidence contract is its Verify lines, so running
them is the map; reading them is not.

## Result: 49 pass · 1 skip-then-run · 2 non-commands

- **49 executed and passing**, including every per-module suite at or above its recorded count
  (`test_feasibility` 15, `test_ordering` 12, `test_exemplar_gate` 9, `test_schedule` 14,
  `test_demand` 13, `test_briefkit` 14, `test_pipeline_scaffold` 16, `test_provenance` 13,
  `test_open_loop` 24, `test_cp_g_end_to_end` 4, `test_offline_guarantee` 4, `test_llm_caller` 22,
  `test_workflow_structure` 11, `test_workflow_runtime` 8, `test_cove` 8, `test_commander_effect` 18,
  `test_adapter_creatures` 16, `test_family_extract` 15, `test_family_consolidate` 18,
  `test_creature_metrics` 14, `test_creature_themes` 18, `test_motif_derive` 33, `test_quality_gates` 21).
- **S9's mutation run, executed rather than skipped:** `.\scripts\mutate.ps1 -Set seedsmith` →
  **every mutant was caught, 10/10, exit 0**, including the one named for the OD4 overlap inversion.
- **2 remaining "failures" are prose fragments, not commands** — `python -m venv` (from the sentence
  "fresh clone → `python -m venv` → `pip install`") and `python -m seedsmith` (from S1's bullet about
  `__main__.py` not being shadowed). Neither was ever a runnable instruction.

## ⛔ Three Verify lines were wrong, and only executing them could show it

- [x] **`python -m seedsmith creatures motifs`** (G1.3) — **the command did not exist.** The CLI had
  only `check` and `metrics`; motif regeneration was reachable solely as
  `python -m seedsmith.adapters.creatures.generate_motifs`.
- [x] **`python -m seedsmith creatures generate --kind commander-effect`** (G4.3) — same, for the
  generator.
- [x] **`python -m seedsmith check --adapter items --metric Coverage/EmptyPartition`** (S2) — omitted
  the positional `corpus_root`, which its own following prose supplied. Not copy-pasteable.

**This is the third instance of one defect class in this program** — D1.4 already recorded *"the real
CLI — `report` from the spec's own example doesn't exist; corrected here rather than silently worked
around."* A documented command nobody executes rots exactly like a derived artifact nobody compares.

**Fixed by making the claim true, not by editing the claim down** — P6's own precedent, where a
falsifier exposed a false docstring and the response was a new test rather than softer wording. Built
`seedsmith creatures {motifs,generate}` as a real subcommand:

- [x] Both G1.3 and G4.3 Verify lines now execute **exactly as the audit writes them**.
  `creatures motifs` → `{"creatures": 84, "vocabularySize": 135, ...}`, and re-running it leaves both
  artifacts **byte-identical** (md5), so it is safe in CI.
- [x] `--kind aspect` **refuses** with exit 2 rather than silently generating nothing — `aspect` is
  blocked on another program (plan §D-F2), and a silent no-op would read as success.
- [x] ⛔ **Imports are deferred inside `cmd_creatures`.** `generate` pulls in the workflow package and
  `langgraph` is an *optional extra*; a module-level import would break plain `seedsmith check` for
  every base install. Asserted by `test_importing_the_cli_does_not_require_langgraph`, which reads
  the source rather than relying on import success — the test process has langgraph installed and
  would pass either way.
- [x] Proven on a genuinely engine-free install: in `.venv-base` (base deps only, `langgraph` absent)
  `seedsmith check` → `3 gap`, `seedsmith creatures motifs` → runs, suite → **474 passed, 11 skipped**.
- [x] S2's Verify line corrected to include its corpus root.

## Evidence

| Check | Result |
|---|---|
| All 52 declared Verify commands | **49 pass**, 1 (mutation) executed separately and green, 2 prose fragments |
| `mutate.ps1 -Set seedsmith` | **10/10 mutants caught**, exit 0 |
| Main venv full suite | **492 passed** |
| Fresh lockfile venv | **492 passed** |
| Base venv (no `langgraph`) | **474 passed, 11 skipped**, no collection errors |
| C# Core / Data / Guard / ItemSeedValidator | **4896 / 548 / 142 / 71** |
| `creatures motifs` idempotence | byte-identical across runs |
| Four `guard-*.ps1` | all **PASS** |

## Standing rule this adds

- **Execute the Verify line; never trust that it was executed once.** Three of this program's Verify
  commands could not run at all, and every one of them sat under a task marked `[x]` with a recorded
  pass. A command that is never re-run is a claim, and claims rot the same way derived artifacts do.

---

# Requirement → evidence map — 2026-09-01

A prose claim that "everything is done" is the thing this program keeps proving wrong. So the map is
a **generated artifact**, not a paragraph: [seedsmith-evidence-map.md](seedsmith-evidence-map.md),
built by walking **every line** of both audit files and executing every `Verify` command it finds.

| | Count |
|---|---|
| Requirement lines (checkboxes) across both files | **455** |
| — resolved `[x]` | **455** |
| — unresolved `[ ]` or partial `[~]` | **0** |
| Declared `Verify` lines | 56 |
| Distinct commands extracted and **executed** from them | 45 |
| Explicit out-of-scope declarations, quoted verbatim | 10 |
| Standing rules catalogued | 21 |

Every requirement appears exactly once, under its own section, with the executed result beside it.
Regenerating the map re-runs all 45 commands (including the ~4-minute mutation suite), so it cannot
drift from the tree without the drift showing up.

## Scope boundaries — quoted, not asserted

Earlier I wrote that the remaining work is "out of scope" and gave no citation. That was a claim.
The audit's own `## Out of scope` sections say it, and §3 of the map quotes all ten verbatim with
line numbers:

| Deferred item | Declared at |
|---|---|
| `aspect` generation — blocked on `aspect-scope` in the creature program | plan:638, plan:822 |
| `power-estimate` (D5) — decided but **not specced** | plan:640 |
| `lore-enrich` — measured unnecessary as a prerequisite (§D-F4) | plan:644, plan:824 |
| Promoting either D3 metric to `gates = True` | plan:646 |
| `environment` generation — **cancelled**, deterministic mapping | plan:823 |
| Enabling CoVe or self-consistency — both specified, both off | plan:825 |
| Merging generated content onto corpus entries for `MotifSharing` | plan:826 |
| The eight accidental empty partitions — W2's known-answer test, **must stay open** | plan:418 |
| The adjective `axis` registry addition | plan:419 |
| Any change to `gk-forge/tools/ItemSeedValidator` — it stays the referential gate | plan:419 |

The "no real model calls" rule (plan:413, plan:638) was **superseded by explicit owner
authorization** on 2026-09-01, recorded in "The real generation run" above — not quietly ignored.

## Prose-form requirements, checked separately

Checkbox extraction cannot see a requirement written as a sentence, so every ⛔ line outside a
checkbox was inspected individually. All resolve to one of: a finding heading (§D-F1 — **verified
closed**: `adapters/base.py:51` carries the one additive `motif_expression` field, and
`spec-adapter-creatures.md` §1 and §4 both carry a written *"⚠️ CORRECTED post-build: the claim above is
false"* note); §D-F2 (`aspect`, declared out of scope above); a defect recorded as found-and-fixed;
or an explicitly reasoned decision (G1's unreachable persist-time re-gate, where the audit's own
ruling was *"the honest action was recording the gap, not inventing a test that fakes reachability"*).

P4's cross-file claim was checked too: `spec-planner.md` §7 does carry the
*"⛔ Corrected 2026-08-31 — the four base-type partitions are EXCLUDED, not layered"* note, at the
line the todo says it does.

## Standing rule this adds

- **A completion claim must be a generated artifact, not a sentence.** Three separate times this
  session, a summary sentence ("0 unchecked", "everything else is out of scope") was accepted as
  proof and turned out to hide real work. A map that regenerates by re-executing every command
  cannot be wrong in the same way — if it drifts, the regeneration says so.

---

## Findings filed from other lanes

- [ ] **SS-F1 — the pytest suite carries 9 pre-existing failures, and one of them writes a tracked file.**
  **Owner:** this program sweeps the suite; the failing nodes span four subsystems (affix authoring,
  fusion recipes, general propose, themes publish, preflight/dump hash), so the per-node owners need
  routing by the manager — this row does not claim them all.
  **Filed by:** lane `cmdc-ep2-1` (`empire-progression`), 2026-09-20, running the scoped boundary for
  EP2.9 (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/**` and its test — new files only).
  **Evidence:** `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests -q` reports
  **9 failed, 924 passed, 1 skipped, 1176 subtests passed**; the same suite with the three new files
  moved out of the tree reports **8 failed, 78 passed** for the same nodes — so they are not this lane's,
  and none of the five failing modules imports `build_favour`.
  **The nine:** `test_affix_authoring.py::test_slot_eligible_families_are_derived_from_the_real_variant_axis`;
  `test_fusion_recipe.py::test_real_corpus_end_to_end` (a JSON decode);
  five `test_general_propose.py::RealWorkedExampleTests` nodes;
  `test_preflight.py::test_hash_matches_the_real_committed_dump` (the committed
  `gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json` capture's hash against a pinned value — the capture
  itself was last committed by `ab16afbf8`, creature-seed's export);
  `test_themes_v2.py::test_publish_is_idempotent`.
  **Cause of the ninth, which is the one with a side effect:** it fails only in suite order (it passes
  alone) on a byte-level diff (`assert b'{\r\n  ...'`) — the publish writes CRLF on this platform while
  the tracked file is LF. A full-suite run therefore leaves
  **`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` modified in the working tree**; this lane restored it
  with `git checkout --` and committed nothing of it. A suite that dirties tracked data is how a later
  lane commits someone else's accident, so this half is worth fixing first.

- [ ] **SS-F2 — the shared validator mislabelled every passive-tree node refusal, and the noun was part
  of the failure-ledger text. FIXED in code; this row is the record.**
  **Owner:** this program. `workflow/validators/field_echo.py` is seedsmith's shared primitive, and the
  defect was in the primitive, not in a caller.
  **Filed by:** the worktree/branch cleanup program, `mega-merge-program-manager-20260925-f78e`,
  2026-09-27, from a re-verification of the BCU2.12 census its 12.5 MB source was hiding.
  **What was wrong:** `name_collision`'s message hardcoded `another commander effect` and
  `subject_name_echo`'s hardcoded `not the creature's` — and **`subject_name_echo`'s only caller is the
  passive-tree node path** (`adapters/trees/nodegen/run.py`), so every node refusal announced itself as a
  commander effect named after a creature. `adapters/dungeon/pipelines.py` already names the kind
  correctly at four sites ("another event", "another encounter", "another room", "another domain"), so the
  shared primitive was the one place out of step with the convention the rest of the tree follows.
  **Why it was not cosmetic:** the noun is part of the message, the message is part of the failure-ledger
  text, and that is part of why a 12.5 MB BCU2.12 ledger read as **984 distinct shapes** until the quoted
  name was masked out. A message that misnames what it refused sends the operator to the wrong program.
  **Fixed:** the kind now travels in `context` as `subjectKind`, with a neutral
  `DEFAULT_SUBJECT_KIND` ("generated entry") fallback, and the node call site passes
  `subjectKind: "passive-tree node"`. It is in `context` and not a new parameter precisely because
  `name_collision`'s own docstring claims it stays a pure function of `(draft, context)`; that claim is
  now asserted by a test rather than left as prose, alongside a non-mutation check on the context.
  **Evidence:** `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_quality_gates.py
  gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py -q` reports **61 passed, 9
  subtests**; the full seedsmith suite reports **4,724 passed** with the six failures cross-referenced to
  **SS-F1** above rather than re-reported here. The pre-existing failures were proven, not assumed: all
  four failing files resolve transitively by import graph to **no** changed module, and reverting the
  three changed sources (sha256-backed-up, `git checkout --` — never `git stash`, which would sweep a
  concurrent stream's staged paths) reproduces them on HEAD with the files restored byte-identical.
  **Still owed elsewhere, not here:** the *node-side* consequence — a corpus-wide uniqueness rule that is
  exact-string where the items rule is token-set normalised, with 2 committed near-collisions
  (`Carrion Frenzy` / `Frenzy of the Carrion`, `Ossuary Pulse` / `Pulse of the Ossuary`) that no
  regeneration can fix, because `name in set(takenNames)` will never match two different strings. That
  belongs to the passive-tree program, not to this one; it is filed and cross-referenced there.
- [ ] **SS-F3 — `materialgen` had no name-distinctness rule and no write-path gate, and **71% of a full
  run's trophy corpus carries a verbatim-duplicate name**. FIXED in code; this row is the record.**
  **Owner:** this program. Both halves of the defect are inside one package,
  `seedsmith/adapters/items/materialgen/`, and neither was in any caller.
  **Filed by:** the worktree/branch cleanup program, `mega-merge-program-manager-20260925-f78e`,
  2026-09-28, while adjudicating `rescue/corpus-bcu211-itemseedgen-run`.
  **How it was found, which is the part worth repeating:** the cleanup measured the *output* first — 830
  gaps against integration's 87 — and read *why* only when the owner pointed out that a verdict on a
  corpus is blind without the generator behind it. An output-only audit can say a corpus is bad; only
  the generator says whether a re-run would produce the same corpus, which is the question that decides
  whether re-running is worth anything.

  **Half one — the brief never mentioned siblings.** `_identity_sentence` handles two classes itself. The
  **substrate** branch (8 members) carried *"the name and flavor should read as a step up from the grade
  below it, not a repeat of it"*. The **trophy** branch — **3,602 members**, one per species slot, minted
  by `trophyplan` — carried no anti-repetition clause at all. The class with three and a half thousand
  siblings was the only large class whose brief never mentioned them: the model was asked for an
  evocative name, handed a species key and a slot number, and told nothing about the other 3,601 names.
  **And `shard` (10 rungs) had no clause either** — a test written to check the property per class
  rather than one string found a third gap the first reading missed, so the gap was never only trophy.

  **Half two — nothing between the answer and the file could object.** `run_batch` validated schema shape
  and tag-axis legality (`schema_defects` + `tag_axis_violations`), then `_write_entries` persisted
  atomically and unconditionally. The package had **no `dedup` call and no `dedup.py`**. The sibling
  adapter has both halves: `setgen/authored.py:398-413` calls `dedup.dedup_report(names)` and records
  `cleared=dedup_report.rate_permille <= tuning.near_duplicate_rate_max_permille` — a real gate, on a
  tuning threshold, in the run path.

  **The scale `check` under-reports, and this is the finding's most reusable sentence.** `seedsmith check`
  reported **747** `SemanticDedup/NearDuplicate` findings. Replaying the corpus shows **731 distinct reused
  names involving 2,588 of 3,633 entries — 71%**. **One finding stands for a whole group**, because the
  message is *"'X' is used verbatim by N entries"*. So the gap COUNT is **3.5x smaller than the number of
  bad entries**, and any verdict that reads 747 as "747 bad rows" understates the defect by more than
  three times. The worst groups: `'lineage seal'` **79** entries, `'verdant lineage'` **57**,
  `'ancestral echo'` **35**. The clearest single case is two slots of one species:
  `trophy.species.allpeater.1` and `trophy.species.allpeater.2` are both named *"Allpeater's Legacy"*.

  **The fix, two edits.** `brief.py` gained one clause parameterised by class, read from
  `vocab.ISSUABLE` rather than hardcoded (the trophy count is a population, never a pinned constant), so
  it cannot be narrowed back to one branch. `run.py` gained `_name_collision_defects`, a **deterministic**
  per-subject refusal. Deterministic on purpose: verbatim reuse is a fact, checkable in O(1) with no
  threshold, and refusing the subject fails safe — the row is not written. setgen's population-level
  `rate_permille` could only be evaluated *after* the batch was written, which is precisely the sequence
  that produced the 956-file revert `ea2aeb756`. A subject is never compared against its own current row,
  because `plan_overwrite` exists to re-emit an id and comparing it to itself would make that path
  unrunnable — a regression introduced by the fix rather than caught by it.

  **Evidence:**
  - **Fail-before, four tests:** the two brief tests (trophy clause absent; `shard` and `trophy` both
    absent per-class) and the two gate tests — `test_two_subjects_in_one_batch_cannot_share_a_name`
    reported `2 != 1, got ('shard.chaff', 'shard.sprout')`, and the on-disk case persisted
    `'shard.sprout'` against a name `shard.chaff` already held.
  - **Pass-before, two guard-rails against over-correcting:** a distinct name still persists, and a
    same-name re-emit of one id is not a collision.
  - **Pass-after:** `test_materials_gen.py` **39 passed, 18 subtests passed** (6 new). The sibling whose
    pattern was copied, `test_set_charm_gen.py`, **104 passed, 2,683 subtests passed** — undisturbed.
  - **Differential on the REAL corpus, not a fixture:** the shipped `_name_collision_defects` replayed
    over the rescue's own 3,633-entry `materials.json` refuses **1,857** and keeps **1,776**, with
    **zero** names reused afterwards, **zero** uniquely-named entries refused, and every survivor holding
    a distinct `runtimeId`. `1,857` is exactly `2,588 − 731`: every participant beyond the first of each
    shared name.
  - **A wrong check, caught by its own author:** the first differential asserted `1,857 == 2,588` and
    failed. The *gate* was right and the *check* was wrong — keeping the first entry of a shared name is
    correct behaviour, not a miss. A verification that only ever confirms its author's expectation is not
    a verification.

  **Standing rule this adds:** *a generated population's duplicate rate must be read as the number of
  RECORDS sharing a name, not as the number of findings the metric prints* — the metric reports one
  finding per reused name, so its count is a lower bound by a factor equal to the average group size, and
  any accept/reject decision made on the printed count is made on the wrong number. And: *when deciding
  whether a re-run is worth anything, read the generator first.* A corpus can be bad and a re-run still
  worthless, or a corpus can be bad and a re-run decisive, and only the generator distinguishes them.
- [ ] **SS-F4 — `setgen`'s ledger outlived its corpus rows for 60 species, so the ENTIRE set backlog was
  invisible; the corpus check existed but was unreachable. FIXED in code; this row is the record.**
  **Owner:** this program. `seedsmith/adapters/items/setgen/run.py`, the same shape of defect as SS-F3 in
  the sibling adapter: a safety check that exists and does not run.
  **Filed by:** the worktree/branch cleanup program, `mega-merge-program-manager-20260925-f78e`,
  2026-09-28, while establishing whether the objective's step 3 (*"run `setgen` for the 61 empty sets"*)
  was executable at all. **It was not, and this is why.**

  **The measurement chain, each link from a command.** `seedsmith items fill --kind set --full --dry-run`
  reports `toGenerate 0 | held 0 | ledgered 937 | complete true` — no work at all. Against
  `tasks/reports/ISG-gap-2-per-partition.json`, which splits the **911** empty-allocated partitions:

      844  species-slot-key-mismatch   a same-species set entry ALREADY EXISTS, under another spelling
       60  species-no-set-entry         no entry under either spelling
        3  display-template-slot-empty
        2  base-type-frame-empty
        1  attribute-kind-empty
        1  set-family-unfilled
      ---
      911  and 60+3+2+1+1 = 67 survive the spelling correction

  So **844 of 911 are a key-spelling mismatch** — allocated `sets/species/<raw speciesId>` while the
  corpus emits `sets/<hyphenated slug>`, per `NamespaceAllocation.cs:261`, which is C# and not this
  program's. The planner's `toGenerate: 0` is therefore *correct about 844* and wrong about 60.

  **The 60 were unreachable, and the reason is an ordering bug.** All 60 have a `creature.` theme (the
  registry holds **904** keys, exactly matching `speciesSlots.allocated: 904`), so all 60 are in the
  planning pool. All 60 are claimed **done** in `gk-data/packs/fusion/data/seed/items/sets/set-charm-gen.ledger.json` (937
  rows) as `set-species-creature.<slug>`. And **0 of their 60 entry ids** — `set.cherrybomb-001` and 59
  others — appear in any of the **885** shipped sets files, which hold **910** entry rows. So they were
  claimed, never written, and invisible from both directions: the planner says complete, the gap metric
  says the partitions are empty, and neither points at the ledger.

      setgen/run.py:247   if subject_id in done:                        -> already.append; continue
      setgen/run.py:258   if kind == "set" and _set_entry_on_disk(...): -> already.append; continue

  `:247` runs first, so a ledgered subject is never tested against the filesystem, and `:258` is
  **unreachable for every ledgered subject**. `_set_entry_on_disk`'s own docstring states the opposite
  intent — *"Corpus presence wins — same discipline materialgen uses for hand-authored rows without a
  ledger record"* — so the ordering contradicted the function it was honouring. The setgen package held
  **0** occurrences of `"reconcile"`; materialgen's `plan_run` is documented *"Resume/append/reconcile"*
  and has 4, with a test (`test_reconcile_replans_a_hand_deleted_row`) for exactly this case.

  **The fix, and the wrong first attempt that shaped it.** The obvious change — trust the corpus over
  the ledger — is what this row's first version did, and **it broke two existing tests**:
  `test_a_plan_with_no_pending_or_held_subjects_is_complete` and
  `test_the_run_resumes_after_an_interrupt_without_duplicating_entries`. Both isolate with a
  **temporary `sets_dir`**, so an absent corpus row there means *isolated*, not *deleted*; and a resume
  that silently re-plans is a change to the resume contract, not a repair. Honouring the ledger is what
  makes a resume cheap and idempotent, and `--out-dir` can legitimately point somewhere the caller is not
  asking about.

  So the shipped fix adds `plan_run(..., reconcile: bool = False)`. **Opt-in**, default unchanged,
  `kind == "set"` only (a charm's entry id is an `(axis-group)-NNN for <species>` placeholder resolved at
  persist time, so there is nothing on disk to reconcile against). Turning it on belongs to whoever knows
  the corpus is authoritative — the same shape as the existing `items repair-*` family, which exists for
  exactly this drift.

  **Evidence.**
  - **Four tests, 4 subtests, all pass.** One pins that **the default is unchanged** (a ledger row is
    still honoured with no corpus row) — without it a later reader cannot tell the flag is a decision
    rather than an oversight. Three cover the flag: absent row is re-planned; present row is still skipped
    **with the flag on**, because `_set_entry_on_disk` exists to stop the key-drift crash its docstring
    names (`creature.caltrop` -> `creature.caltropnut` regenerating a different row for the same id);
    and an on-disk row with no ledger record is still skipped.
  - **Whole file green:** `test_set_charm_gen.py` **108 passed, 2,687 subtests** (was 104 / 2,683).
    `test_materials_gen.py` **39 passed, 18 subtests** — SS-F3's fix undisturbed.
  - **Differential on the real corpus, same inputs in one process:**

        default    (reconcile=False):    0 subjects, already_done 904, complete True
        reconcile  (reconcile=True) :   60 subjects, already_done 844, complete False
        surfaced == the 60 the report names : True   (0 extra, 0 missing)

  - **Not yet wired:** no CLI flag exposes `reconcile`, so the 60 cannot be surfaced from the command
    line yet. `cli.py` is outside this lane's fence. The capability is in, tested, and proved on the
    real corpus; the flag is the remaining step, and it belongs with the `repair-*` family rather than
    as a bare `items fill` switch.

  **Standing rule this adds:** *a resume's ledger is a CLAIM and the corpus is the FACT, and a codebase
  that believes the claim without checking the fact will eventually hide its entire backlog — so the
  check must exist, must be reachable, and the decision to enable it must be explicit.* Three corollaries,
  each paid for here: **a guard ordered before the check it is meant to defer to is not a check at all**;
  **a function's docstring stating an intent its call order contradicts is the cheapest possible defect
  report, and the docstring was right**; and **an opt-in flag with a test pinning that the default is
  unchanged is a better fix than a correct unconditional change that breaks the contract two existing
  tests exist to protect.**
- [ ] **SS-F5 — CORRECTING SS-F4's mechanism: the defect is the ledger's `outcome`, not the filesystem
  check, and the real fix needs no flag at all. FIXED in code; this row is the record.**
  **Owner:** this program. Same file as SS-F4, same adapter, sharper cause.
  **Filed by:** the worktree/branch cleanup program, `mega-merge-program-manager-20260925-f78e`,
  2026-09-28, from wiring the `--reconcile` capability SS-F4 recorded as owed.

  **SS-F4 said** *"all 60 subjects are claimed done and never written"*, and fixed it with an opt-in
  filesystem reconcile. **That statement is true and the mechanism was one step short.** The cause is
  earlier and simpler:

      the `sets` run ledger holds 937 rows — 876 persisted, 59 `escalated`, 2 `blocked`

  `escalated` is written so the fill walker can keep walking **without paying for the subject again**, and
  `blocked` is the model declining it. Both are records of work that did **not** happen. And
  `plan_run` skipped on the ledger's mere **presence** — so those 61 were read as `already_done`. The
  corpus check SS-F4 restored behind a flag was addressing a *consequence* of that, correctly, and its
  reasoning about temporary `--sets-dir` was right; it just was not the cheapest correct fix.

  **And the 60 are exactly those rows**, which is what makes this a fact rather than a coincidence:

      of the 60 `species-no-set-entry` subjects, escalated or blocked : 60
      of the 60, anything else                                        : 0
      the 61st non-persisted row                                      : set-build-build.might-offense

  So the 60 species that `ISG-gap-2-per-partition.json` calls unscheduled are precisely the escalated
  species rows, and the escalated build row is a 61st instance in the other population.

  **The fix, and it is smaller than SS-F4's.** `plan_run` now skips only when the row is a *claim*:

      NON_PERSISTED_OUTCOMES = frozenset({"escalated", "blocked"})
      def _row_claims_a_written_row(row) -> bool:
          outcome = str((row or {}).get("outcome") or "persisted").strip().lower()
          return outcome not in NON_PERSISTED_OUTCOMES

  **No filesystem read, therefore no flag needed, therefore nothing that a temporary `--sets-dir` can
  confuse.** An absent `outcome` key is believed, which matters because **876 of the real 937 rows carry
  no `outcome` at all**; and an unknown word is believed too, because silently re-planning on a word this
  vocabulary has not heard of would turn every future addition into a silent re-run. `NON_PERSISTED_-
  OUTCOMES` is asserted directly by a test so widening it is a visible act.

  **SS-F4's `reconcile=True` and the new `items repair-ledger` are kept, and they cover the OTHER
  direction** — a row that *claims* persisted whose file was hand-deleted, which is what materialgen's
  `test_reconcile_replans_a_hand_deleted_row` covers. Two directions, two mechanisms, no overlap.

  **`items repair-ledger` — new, in the existing `repair-*` family, dry-run by default.** The logic
  lives in the new `setgen/ledger_reconcile.py`, modelled on the sibling `role_repair.py`; the CLI
  wrapper is thin, refuses a production write without `--allow-production-tree`, and prints the JSON
  report. It drops rows and **never writes, moves, or invents a set row** — it repairs the *claim*.

  **Evidence.**
  - **Tests: 119 passed, 2,705 subtests** in `test_set_charm_gen.py` (was 116 / 2,690). Three new outcome
    tests — an `escalated` or `blocked` row is re-planned with **and** without `reconcile`; a persisted
    claim is still skipped for all three shapes the real ledger uses (absent key, `done`, `persisted`);
    and `NON_PERSISTED_OUTCOMES` is asserted directly. Eight repair tests, including **two refusals**:
    a missing corpus tree must refuse rather than call every row stale, and a missing ledger must refuse
    rather than report a clean result.
  - **A bug the tests caught in the new module.** Its first placeholder predicate was
    `"." not in entry_id`, and a charm's placeholder id is `charm.(axis-group)-NNN for apple` — which
    **contains a dot**. So placeholders were classified STALE and a charm would have been dropped from its
    own ledger. The predicate is now explicit (`_is_judgeable`, with `CHARM_PLACEHOLDER_MARKER`), and
    unjudgeable rows are **reported** in `unchecked` and left alone.
  - **A bug the module's own refusal caught in the CLI wrapper.** The first version defaulted the ledger
    to `run_mod.DEFAULT_LEDGER`, which resolves to `data/seed/items/_runs/set-charm-gen.ledger.json` —
    a path that **does not exist**; the real ledgers are `sets/…` and `charms/…`. The command refused
    with *"there is nothing to reconcile"* rather than reporting "the ledger is clean", which is the
    refusal earning its place. The wrapper now derives the ledger from `sets_dir`. **The stale
    `DEFAULT_LEDGER` constant itself is unrepaired and is filed here rather than fixed silently.**
  - **Three independent routes reach the same 60**, on the real corpus, all dry:

        pre-fix default (0196d14b9)              :  0 subjects, already_done 904, complete True
        DEFAULT now, no flag                      : 60 subjects, already_done 844, complete False
        reconcile=True (filesystem route)         : 60 subjects, already_done 844, complete False
        items repair-ledger (dry)                : 61 stale of 937, {escalated: 59, blocked: 2}

    and `DEFAULT == reconcile=True == the 60 the report names : True`.
  - **One verification error of my own, recorded because it is the same class as the rest.** The first
    run of that three-route check printed **NOT PROVEN** — against three measurements that in fact
    agreed. It compared a **species-population** set to `repair-ledger`'s **whole-ledger** set, so the
    escalated build row made 60 look like 61. Matching the populations first is what turned three
    consistent numbers into a verdict. **A disagreement between two measurements is a question about the
    populations before it is a question about either measurement.**

  **Standing rule this adds:** *a run ledger records outcomes, not just presence, and a resume that
  branches on presence reads a failure as a success.* Three corollaries: **an absent field is the most
  common case, not the empty one** — 876 of 937 rows carry no `outcome`, so an absent key must be
  believed; **an unrecognised outcome must be believed too**, or every future vocabulary addition becomes
  a silent re-run, so the non-persisted set is a named constant a test pins rather than a default branch;
and **when a fix needs a flag to be safe, ask first whether the cause is further upstream**, because a
cause one line earlier can need no flag at all.
- [ ] **SS-F6 — the whole seedsmith suite behind SS-F3/SS-F4/SS-F5: 4 failed / 4,747 passed / 5,059
  subtests, and NONE of the 4 is this session's. Two are machine-local, so the suite's "green" baseline
  is environment-dependent. Filed by the worktree/branch cleanup program, 2026-09-28.**
  **Why it is filed rather than left in a scrollback:** SS-F3, SS-F4 and SS-F5 each quote ONE test file
  each, and a change to `setgen/run.py`'s planner and to `report/cli.py` is exactly the kind of change a
  single file's suite cannot vouch for. So the full suite was run: `python -m pytest gk-forge/tools/seedsmith/tests
  -q` in **24m17s**, reporting **4 failed, 4747 passed, 4 skipped, 5059 subtests passed**.

  **The 4, and none of them is this session's.**

  | failure | verdict | evidence |
  |---|---|---|
  | `test_guard_population_pin.py::RealTreeTests::test_P1_backlog_stays_empty` | **PRE-EXISTING** | reproduces identically at the pre-change commit |
  | `test_guard_population_pin.py::RealTreeTests::test_the_real_scan_runs_clean_and_the_backlog_stays_closed` | **PRE-EXISTING** | same |
  | `test_tool_invocation_guard.py::test_every_python_file_under_the_tool_is_inside_a_scanned_scope` | **MACHINE-LOCAL** | the unscanned paths are all `tools/seedsmith/.venv-verify/Lib/site-packages/…` |
  | `test_topology_repair.py::test_written_partitions_are_lf_only` | **MACHINE-LOCAL** | the tracked ledger is **0 CRLF at HEAD**; the working-tree copy has **4,077** |

  The two machine-local ones are worth naming precisely, because both make a suite look broken on a clean
  checkout:

  * **`.venv-verify` is untracked and gitignored** — `git ls-files` under it returns **0** and one ignore
    rule matches. A virtualenv living inside the tool directory is therefore scanned by a guard that means
    to scan only the tool's own sources, and a direct launch in a vendored `_pytest/__init__.py` is
    reported as an unscoped site. Nothing to do with SS-F3/4/5, whose files are all under `seedsmith/`,
    a directory `SCANNED_SCOPES` already contains.
  * **the LF-only assertion reads the working tree, and this checkout is CRLF.** `HEAD`'s blob for
    `gk-data/packs/fusion/data/seed/items/sets/set-charm-gen.ledger.json` is **123,494 bytes with 0 CRLF**; the working-tree
    file is **127,571 bytes with 4,077 CRLF**, and `git status` is clean because git normalises on commit.
    So the assertion fails on a byte difference git itself considers nonexistent. No session change can
    fix that, because no session change should touch a generated corpus file.

  **My three commits touched 9 files, and the list is the proof:** two ledgers/records
  (`tasks/seedsmith-todo.md`, this session's own record), five seedsmith sources
  (`materialgen/brief.py`, `materialgen/run.py`, `setgen/run.py`, `setgen/ledger_reconcile.py`,
  `report/cli.py`) and two test files. **0 under `data/`, 0 under `.venv-verify/`.** A change that touches
  no corpus file cannot move a line-ending assertion about a corpus file, and cannot add a file inside a
  gitignored virtualenv.

  **The attribution method was wrong first, and the error is the reusable part.** The first pass extracted
  the pre-change tree with `git archive` into a temp directory, ran the same four tests there, and
  reported **"2 are MINE"** — the two machine-local ones. It was wrong because a `git archive` extraction
  contains, by construction, **neither** an untracked gitignored `.venv-verify/` **nor** a CRLF working-tree
  checkout. So the two runs differed in **environment**, not in **version**, and the difference was
  attributed to the code. **Comparing a clean extraction against a dirty working tree measures the working
  tree, not the commit** — and the tell was available for free: a guard that reports machine-local paths in
  its own message is describing the machine, not the repository.

  **Also re-measured, because a quoted number rots:** `python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter
  items` at the new HEAD `8fb84d5ea` still reports **87 gap, 612 note, 153 not_measured** — unchanged, as
  it must be, since no commit in this series touched `data/`.

  **Standing rule this adds:** *a test failure is attributed by running the same test in the same environment
  on both sides, and a suite's green baseline is a property of the machine as well as the repository.* Two
  corollaries: **a guard that names paths outside the repository is reporting the environment**, and
  **when a baseline must be reconstructed, reconstruct it in the same working tree rather than from an
  archive** — an archive differs from the working tree in every way that is not the commit, and each
  difference will be read as a regression if the two are compared as though only the commit varied.
- [ ] **SS-F7 — step 3 is unblocked at the operator's door and costs 61 calls, and
  `materialgen.brief.PROMPT_VERSION` is DEAD, so the deferred provenance bump is inert. Filed by the
  worktree/branch cleanup program, 2026-09-28.**
  **Owner:** this program. Two small facts, both of which would have been reported loosely otherwise.

  **1. The 60 are schedulable through the command an operator actually types.** SS-F5 proved
  `plan_run` surfaces 60 by calling it **in process**. That is not the same claim as "an ordinary
  `items fill` schedules them", and the difference is the whole of a step. Run through the door:

      python -m seedsmith items fill --kind set --full --dry-run

  | | before SS-F5 | now |
  |---|---|---|
  | species | `toGenerate 0`, `complete true`, `ledgered 937` | **`toGenerate 60`**, `complete false` |
  | build | `toGenerate 0` | **`toGenerate 1`** |
  | `exactDuplicateNames` | 0 | 0 |

  **So step 3 costs 61 set-generation calls, not 60.** The 61st is `set-build-build.might-offense`, the
  escalated build row SS-F5 identified — the same population `items repair-ledger` reports as 61 stale.
  The two populations agree, which is the cross-check that makes 61 trustworthy rather than 60-plus-a-guess.

  **2. The `PROMPT_VERSION` bump deferred in the previous report would have been inert, and the reason is
  the finding.** Traced from the constant outward:

  * `materialgen/brief.py:16` defines `PROMPT_VERSION = "material-gen/1"`, and **nothing references it** —
    a search across `seedsmith/**/*.py` *and* `tests/*.py` for any reference to materialgen's constant
    returns **no hits**, and `test_materials_gen.py` does not pin it either.
  * `report/cli.py:779-781` is the only stamper, and it hardcodes a **different** adapter's constant:
    `from ..adapters.items.setgen.brief import PROMPT_VERSION`.
  * so the `"material-gen/1"` string in the rescue corpus is **not** generated. It is a literal inside
    `_meta.amendments[0].promptVersion`, in the hand-written amendment note that begins *"authored via
    materials-gen … name/flavor/tags were hand-authored as an honest stand-in"*. The corpus's own
    top-level `_meta.promptVersion` is the hand-authored **integer** `1`.

  **A dead provenance constant is worse than no constant**, because it reads as though provenance is
  tracked. Bumping it would have changed a value no consumer reads and would have been reported as a
  provenance improvement — which is the failure mode this row exists to prevent. Two real options, both
  **ask-first** and neither taken here: wire `_prompt_version()` to the adapter that is actually running
  so a generated `_meta` names its own brief; or delete the unreferenced constant so nothing implies a
  guarantee that does not exist. **Filed, not fixed** — the materials `_meta` is hand-authored provenance
  and changing that shape is a design decision for this program, not a cleanup.

  **Standing rule this adds:** *a deferred fix is not a fix until someone checks whether the thing it
  changes is read.* A "provenance bump" that no consumer reads produces a green diff and no provenance,
  and the cost of shipping it is that the next reader trusts a constant that was never wired. Two
  corollaries: **a constant with zero references should be treated as a finding, not a version** — grep
  for the references before the bump, not after; and **an in-process proof and an operator-path proof are
  different claims**, because the gap between them is where a flag that was never wired, or a ledger read
  from the wrong directory, hides.
- [ ] **SS-F8 — the step-2 operator path IS gated, and the batching the 1,857-call spend requires is now
  proven rather than assumed. Filed by the worktree/branch cleanup program, 2026-09-28.**
  **Owner:** this program. The last free safety check before the owner's budget is spent.

  **1. The gate is on the operator's write path, not only in-process.** SS-F3 proved `_name_collision_-`
  `defects` fires inside `run_batch`. That would be worth nothing if the CLI wrote by another route, so
  `materialgen/run.py`'s `main()` was traced to its write:

      answers = {s.subject_id: caller(s.brief, material_schema()) for s in plan.subjects}
      result  = run_batch(plan, answers, ledger=ledger)

  Every answer goes through `run_batch`, and `_write_entries` is called from `run_batch` and nowhere else
  in the package — so `items generate --kind material --overwrite ... --write` cannot persist a colliding
  name. **This was the same check that caught an unproven claim for step 3 in SS-F7, applied before the
  spend rather than after it.**

  **2. The cost is exactly `len(plan.subjects)` — one call per subject, from the line above.** So the
  re-emit of the **1,857** name-colliding trophies is **1,857 LM Studio calls**, which is what has been
  quoted since CB43 and is now sourced to a line rather than to an assumption about batching.

  **3. The batching is PROVEN, and it was an assumption until this row.** The `--overwrite` id list is
  **48,805 characters** against Windows' **32,767**-character command-line limit — it overflows by
  **16,109**, so the run must split into at least three batches of roughly 934. If the gate compared only a
  batch against itself, a name published by batch 1 would be free for batch 2 to reuse, and **splitting the
  run would silently reintroduce the exact defect the gate exists to stop**: 1,857 calls spent, collisions
  back, and nothing in the output to say so.

  It is safe because `run_batch` re-reads the corpus file at the start of every invocation, so batch 2
  sees batch 1's output as already on disk. That is a property of the **write path**, not of the gate, so
  it is now pinned by `CrossBatchCollisionTests`: a name persisted by an earlier batch **blocks** a later
  one, the refusal names the reused name, and a later batch may still use its own name.

  **Evidence.** `test_materials_gen.py` **41 passed, 18 subtests** (was 39 / 18).

  **4. An unsourced number caught before it was published.** A throwaway diagnostic printed *"the 27
  remaining rows whose claim is stronger than the corpus"*, and that sentence is not derivable from
  anything: the ledger's split is **exhaustive** — **876** implicit-persisted + **59** `escalated` + **2**
  `blocked` = **937**, which is every row — so no third category exists and no 27 does. Checked before
  filing rather than after: **0** occurrences in `tasks/seedsmith-todo.md`, **0** in
  `tasks/backlog-clean-up-todo.md`, **0** across this session's commit messages. It reached nothing
  committed, and the row that quoted the real number (`876 kept | 59 escalated + 2 blocked`) is the one
  that stands.

  **Standing rule this adds:** *when a spend is split across invocations, the property that makes the split
  safe is a property of the WRITE PATH, so it needs its own test.* A gate that is correct within one call
  can be silently defeated by calling it more than once, and nothing in either call's output will say so.
  Corollary: *an unsourced number in a diagnostic's `print` is a claim, and a claim that reaches no artefact
  is still worth chasing* — because the next reader of that script inherits it.
- [ ] **SS-F9 — pre-flight for the two spends: the transport is READY, the quoted call counts are FLOORS
  (ceiling 8x), and the owner's 68,000 requests are in no seedsmith ledger and are not seedsmith's
  embedding traffic. Filed by the worktree/branch cleanup program, 2026-09-28.**
  **Owner:** this program. Written to inform an authorisation, not to change code.

  **1. The transport is ready, verified without spending a call.** `GET /v1/models` on
  `http://localhost:1234` returns **HTTP 200**, and the model `.env` names is the one **actually loaded**:

  | | |
  |---|---|
  | `SEEDSMITH_LLM_ENDPOINT` | `http://localhost:1234/v1/chat/completions` |
  | `SEEDSMITH_LLM_MODEL` | `google/gemma-4-26b-a4b-qat` |
  | loaded on the server | `google/gemma-4-26b-a4b-qat` — `type=vlm`, `arch=gemma4`, `quant=Q4_0` |
  | `SEEDSMITH_ALLOW_PRODUCTION_TREE` | `1` — the write under `gk-data/packs/fusion/data/seed/items` is permitted |

  So neither spend fails on a dead endpoint or a model that was never loaded. Worth one note: the loaded
  model is a **vlm** answering text briefs, which works, but it is not the obvious choice for a brief that
  asks for a name and two sentences of flavour.

  **2. Every call count quoted so far is a FLOOR.** `SEEDSMITH_LLM_ATTEMPTS=2` and
  `SEEDSMITH_LLM_MAX_HEAL=3` compose to **up to 8 requests per subject**, and
  `SEEDSMITH_LLM_TIMEOUT=420` bounds each one. So:

  | | floor | ceiling |
  |---|---|---|
  | the 61 sets | 61 | **488** |
  | the 1,857 trophy names | 1,857 | **14,856** |

  The floors are what a clean run costs; the ceilings are what a run where everything fails twice and
  self-heals three times costs. **The ledgers record which happened** — see the next paragraph — so a
  previous run's attempt distribution is the best available estimate of a new one's.

  **3. The ledgers ARE a request record, and summing `attempts` prices a run after the fact.** Every row
  carries the tries that subject actually took:

  | ledger | rows | attempts | mean | outcomes |
  |---|---|---|---|---|
  | **rescue `materials-gen`** | **3,612** | **3,612** | **1.00** | 3,612 persisted |
  | head `set-charm-gen` | 937 | 1,136 | 1.21 | 876 persisted, 59 escalated, 2 blocked |
  | head charm `set-charm-gen` | 904 | 1,240 | 1.37 | 883 persisted, 21 escalated |
  | head `base-types-gen` | 437 | 437 | 1.00 | 437 persisted |
  | the seven other item ledgers | 172 | 172 | 1.00 | all persisted |
  | **total** | **6,072** | **6,607** | | |

  So **the BCU2.11 trophy run cost exactly 3,612 requests** — one per subject, no retries at all. That is a
  measured number for the run this whole cleanup is about, and it is the reason the rescue's corpus is
  *well-formed* and only *badly named*: every subject succeeded on the first try, so nothing about the
  transport was wrong.

  **4. The owner's 68,000 requests are NOT here, and NOT seedsmith's embeddings.** The recorded total is
  **6,607** — **10.3x** below 68,000 — so the run is in no ledger this repo keeps. The obvious remaining
  candidate was `check`: LM Studio has an embedding model loaded, and the 2,720 `embed` lines in its log
  looked like `check` traffic. **It is not.** `metrics/dedup.py` computes
  *"character 5-gram shingles -> MinHash signatures -> Jaccard"* with LSH banding, entirely in-process, and
  **seedsmith makes no embedding call anywhere in the package** (a search for an embedding endpoint returns
  nothing). So those log lines are another tool's. **The 68,000 is therefore not recoverable from
  seedsmith's own records**, and the hunt has to look at a different pipeline or at a ledger that run wrote
  for itself — which is the owner's separate open item, and the reason this row is filed here rather than
  acted on.

  **Standing rule this adds:** *before authorising a generation run, price the FLOOR and the CEILING, not
  the subject count* — because the subject count is neither. Read the retry and self-heal config, and read
  a previous run's `attempts` distribution for the same module, which is a measurement rather than an
  assumption. Corollary: *a per-subject `attempts` field turns a run ledger into a request record*, which
  makes "what did that run cost" answerable after the fact — and means a run whose ledger was not kept is
  a run whose cost is gone, whatever the operator remembers.
- [ ] **SS-F10 — simulating the 1,857-call pass BEFORE running it found a 6-row population the gate is
  structurally blind to; the plan as scoped would have landed on NearDuplicate 10 against a target of 4.
  Filed by the worktree/branch cleanup program, 2026-09-28.** **Owner:** this program. Implemented, not
  merely reported: `gk-core/scripts/reemit-colliding-item-names.py` now derives both populations.

  **How the prediction was made, and why it is a lower bound.** Take the rescue corpus, remove the rows the
  gate refuses, and run **the repo's own** `python -m seedsmith check <tree> --adapter items` against a
  real copy of the real tree. Removing rows is not what the run does — the run *replaces* them with
  freshly authored names — so the result is a **lower bound**: it assumes every re-emit comes back distinct
  from every other name. That is the right direction for a feasibility question. If the bound already
  exceeds the target, the run cannot reach it and the spend should not happen.

  **The 1,857-only list lands on 10.** Measured:

  | re-emit list | NearDuplicate GAP | all GAP | vs target 4 |
  |---|---|---|---|
  | within-materials only (**1,857**) | **10** | 93 | **misses** |
  | extended, both populations (**1,863**) | **4** | **87** | meets, **+0** |
  | integration HEAD today | 4 | 87 | — |

  **And all six extra rows, named.** 4 of the 10 are HEAD's pre-existing *recipe* findings. The other 6 are
  a `material.*` whose name is held verbatim by a `charm.*` or a `set.*`:

  | material id | name | also held by |
  |---|---|---|
  | `trophy.species.blackelephantzombie.1` | Obsidian Husk | `charm.surv-util-220` |
  | `trophy.species.chrysantheautumn.1` | Autumnal Bloom | `set.chrysantheautumn-001` |
  | `trophy.species.goldbungizombie.1` | Gilded Husk | `charm.econ-002` |
  | `trophy.species.iceblover.1` | Glacial Essence | `set.icepumpkin-001` |
  | `trophy.species.iceblover.2` | Glacial Bloom | `charm.off-ctrl-256` |
  | `trophy.species.supergargantuar.2` | Colossus Fragment | `charm.surv-util-310` |

  **Why the gate cannot see them, which is structural and not an oversight.** `materialgen` is
  materials-only by construction. `brief.py`'s `_sibling_count` returns a **count**, and the brief says
  outright that *"the model cannot see those names"*; `run_batch` loads only `materials_path`, and both
  `by_runtime` and `claimed` are materials-local. So a within-materials key gate is blind to a name owned
  elsewhere **by design**, and a Jaccard-level gate would not help either — these are *exact* matches, not
  lexical near-duplicates. Closing them properly needs a corpus-wide name registry consulted by every
  adapter, which is a cross-adapter design change and **not** this objective's scope; the honest local
  answer is to re-author those 6 and let `check` verify.

  **What the run still cannot prove.** A re-authored name for those 6 rows is *not* provably free of the
  charm or set holding the old one, because the gate never sees those names. The runner says so on stdout
  rather than implying the run closes the loop: `check` afterwards is the verification, not the plan.

  **The all-gap figure stays 87, and that is not a shortfall of this pass.** Materials contribute **none**
  of the 67 empty partitions — those are 61 `sets`, 3 `display-templates`, 2 `base-types`, 1 `attributes` —
  so `setgen` is what reduces the count, and the NearDuplicate criterion is what this pass delivers. Also
  recorded rather than glossed: survivors' **note** count rises **612 -> 1,859**. That is advisory severity
  and outside the criterion, but it is a real change a reviewer will see.

  **Standing rule this adds:** *before authorising an expensive generation run, simulate it by removing the
  rows the change would touch and re-running the real check.* The removal is cheap, the run is not, and the
  simulation answers the only question that matters — can this reach the target at all. Corollary: *a gate
  scoped to one corpus is blind by construction, not by bug*, so **always ask which corpus owns the other
  side of the collision** before concluding a duplicate pass is complete. A third corollary, earned the
  hard way here: this simulation was written once with a bug that appended to `growing` but not to the kept
  list, so it measured a corpus of **zero** materials and cheerfully reported the target number. The tell
  was `kept 0` with `refused 3,633` — impossible, since a first entry cannot collide with anything. **An
  implausible intermediate is a bug report; read it before believing the verdict.**

  And the most frequent mistake of all, recorded because it cost roughly sixteen round-trips across this
  programme: **a hand-typed verification fragment is itself a hand-typed artifact, and it drifts exactly
  like the thing it checks.** Every one of those sixteen was a *fragment* miss — `**1,857**` typed as
  `1,857`, an em-dash typed as a hyphen, a closing `*` typed as `**` — and not once was the written row
  wrong. A check that retypes its own subject is a second thing to keep in sync, and when it disagrees with
  the file, **the file is right until proven otherwise.** The fix is not a better guess at the fragment; it
  is `grep` the real line and copy from there. Corollary to SS-F9's floor-and-ceiling rule: *spend the
  cheap, exacting read on verifying, and the expensive, approximate one only on writing.*
- [ ] **SS-F11 — 253 entries have no `flavor` and `items fill` cannot reach ONE of them, so the 87-gap
  closure needs a backfill no current code path performs; the 61-set run is the only part of it that is
  reachable. Filed by the worktree/branch cleanup program, 2026-09-28.** **Owner:** this program. Reported
  with a measured reachability table; **not** acted on, because fixing it means either re-emitting 253
  entries (the owner's tokens) or changing which kinds `fill` plans (another stream's surface).

  **The question that found it.** Not "what does `fill` plan" — that asks about workload. The question is
  **"does `fill` plan to revisit the exact entries `check` reports incomplete"**, which asks about
  reachability. The two differ, and the difference is the whole finding.

  | population | missing `flavor` | what `items fill` plans | reachable? |
  |---|---|---|---|
  | `items:gem` | **104 of 104** | `toGenerate 0`, `complete: true` | **no** — rows exist, ledger says emitted |
  | `items:consumable` | **63 of 63** | *no fill kind at all* | **no** |
  | `items:unique` | **32 of 154** | *no fill kind at all* | **no** |
  | `items:charm` | 30 of 954 | 21 **new** subjects | **no** — new rows, not a revisit |
  | `items:set` | 24 of 910 | 61 **new** subjects | **no** — new rows, not a revisit |
  | | **253** | | **0 reachable** |

  **Three distinct causes, so three different fixes.**

  * **`gem`, 104 rows — the step-2 defect again, in a second adapter.** The rows ARE on disk and the
    ledger records them emitted, so `fill` answers `complete: true` while `check` answers *104 of 104 have
    no `flavor`*. Both describe the same corpus and cannot both be right; `fill` is the one that is wrong.
    This is the identical shape as the trophy names: **a persisted row is trusted without checking that it
    carries the fields the corpus requires.** The remedy is the same one step 2 needs — an explicit
    `--overwrite` re-emission for those 104 ids — not a `fill` invocation.
  * **`consumable`, 63, and `unique`, 32 — not wired into `fill` at all.** `consumablegen` and `uniques`
    exist as adapters under `adapters/items/`, but neither appears in `defaults.FILL_KIND_ORDER`, so no
    `items fill` invocation can reach them. Adding them to the order would make them reachable; it would
    not by itself add `flavor` to rows already on disk.
  * **`charm`, 30, and `set`, 24 — the adapters are wired and the run adds rows instead of completing
    them.** `fill` plans 21 new charms and 61 new sets. Adding entries does not complete existing entries,
    and **if the new rows are emitted without `flavor` the count gets worse, not better** — which is worth
    checking before the 61-call run rather than after.

  **Why the `FieldMissing` and `FlavourMissing` families are one population, not two.** Both report the
  same five kinds and the same counts (30 / 63 / 104 / 24 / 32), from two different metrics. So the 87's
  `5 FieldMissing + 5 FlavourMissing` is **10 findings describing 253 entries**, and that 253 is nearly
  **three times the 61-set work** the objective's step 3 is sized around.

  **The rest of the 87, and what is reachable at all.** `Coverage/EmptyPartition` is 67 = **61 `sets/*`** +
  2 `base-types` + 3 `display-templates` + 1 `attributes`. Verified by generating both lists from the real
  code — `fill.py`'s own wiring (`set_tuning.load()`, `set_vocab.build(tuning)`, `read_ledger`, the same
  `plan_run` kwargs) and the coverage metric's own subjects — and comparing them **after** normalising the
  two id vocabularies:

  | | |
  |---|---|
  | empty `sets/*` partitions | 61 |
  | planned setgen subjects (60 species + 1 build) | 61 |
  | **overlap** | **61 — full** |
  | empty but unreachable | 0 |
  | planned but already occupied | 0 |

  So step 3 is sound: the 61-call run closes **all 61**, and 87 drops to 26. The residual 26 is
  6 `EmptyPartition` (2 base-types, 3 display-templates, 1 attributes — none of which produced a `fill`
  plan entry either) + 6 `Coverage/PairwiseHole` + the 10 flavour findings above + 4 recipe
  `NearDuplicate`. **The 6 `PairwiseHole` are cross-product coverage gaps** (`frame x element` in
  `material`, `frame x rarity` in `unique`, `role x band` and `role x frame` in `base-type`,
  `powerBand x element` in `consumable`+`gem`, `frame x band` in `base-type`) — they need content that
  spans combinations, not more records, so no single-adapter run closes them.

  **AMENDED, same day: it is four causes, not three, and the split is measured.** Reading each flavourless
  row's own `notes` separates *authored* content from *emitted* content, and `uniques` is an explicitly
  hand-authored kind in this repo, so "needs a re-emission" is the wrong remedy for part of this:

  | population | flavourless | carries hand-authored rationale | carries neither flavour nor provenance |
  |---|---|---|---|
  | `gem` | 104 | 0 | **104** |
  | `consumable` | 63 | 23 | 40 |
  | `charm` | 30 | 20 | 10 |
  | `unique` | 32 | 16 | 16 |
  | `set` | 24 | **24** | 0 |
  | | **253** | **83** | **170** |

  * **170 rows carry neither `flavor` nor `notes`.** These are the step-2 class proper and the largest
    block: an emitted row that records neither the field the corpus requires nor where it came from. The
    `--overwrite` re-emission is the right remedy and it is the owner's tokens.
  * **83 rows carry hand-authored rationale in `notes`** — prose like *"RUNTIME HONESTY: atom.martyrdom is
    resource.delta…"* and *"Whole-token fusion name 'Stillmarch' from uniqueSetSeedPools[…]"* — and
    **all 24 of the `set` population is of this kind.** These were authored, not generated, so no
    regeneration reaches them: the fix is in whatever contract authored them, and it is not this
    objective's surface. Worth saying plainly, because the tempting move — re-run the generator over 24
    files — would **overwrite authored rationale with generated text**, which is the hand-edit rule's
    mirror image and just as destructive.
  * So the earlier "three causes" is four once provenance is read, and only **170 of 253** is a
    regeneration problem at all.

  **And the 61-call set run does NOT make this worse** — worth having *before* the spend rather than
  after. `setgen`'s own brief **requires** the field: `brief.py:122` and `:174` both list `` `name` — a
  short display name (1-4 words), and `flavor` — one sentence `` as a required answer, and **886 of 910**
  set entries already carry it. So the 61 new sets arrive with `flavor`, the `items:set` count stays at
  **24**, and the 83 hand-authored rows are untouched by the run because the run does not write them.

  **Two of my own errors, both recorded because both produced a confident wrong answer.**

  * I compared the empty-partition subjects against the planned subject ids **as raw strings** and
    concluded *"NO overlap — a 61-call run would close ZERO empty partitions."* The two lists are
    identical: the coverage metric names a partition `sets/blackfootball-a` while setgen's subject is
    `set-species-creature.blackfootball_a`. **Coverage partitions use a hyphen; subject ids use an
    underscore.** Two vocabularies, one population, and the mismatch read as a blocker.
  * Then I read `fill` planning 21 charms as `OK` against 30 charms missing flavour — the same slip in the
    other direction. 21 **new** rows say nothing about 30 **existing** ones. The verdict has to be an id
    overlap, not a workload comparison.

  **Standing rule this adds:** *a planner's `complete: true` is a claim about EMISSION, never about the
  CORPUS, and the two are separated only by a second tool's opinion.* So a corpus gap is only closed once a
  tool that reads the corpus — not the ledger — says so. Corollary, and the one that cost both errors
  above: **when two artefacts name the same population in different vocabularies, normalise to a shared
  form and compare ids before comparing counts.** A count comparison across two id schemes is not a weaker
  check; it is a different check, and it will answer a question you did not ask.
- [ ] **SS-F12 — a THIRD materialgen gap, and it is a spend gap: one raising subject discarded every
  answer already paid for. Building the proof of it wrote three fixture rows into the PRODUCTION corpus.
  Filed by the worktree/branch cleanup program, 2026-09-28.** **Owner:** the code half is **fixed and
  committed** (`53fc9d995`); the guard half is **reported, not fixed** — see the last paragraph for why.

  **The gap, and why it is the one that matters before a spend.** `run.py:348` built the whole
  `{subject_id: answer}` mapping in a single dict display. A dict display evaluates every value before the
  assignment completes, so one raising subject unwound the **entire** invocation: `run_batch` was never
  reached, nothing was written, nothing was ledgered, and every answer already generated was garbage. The
  module docstring advertised it as the design — *"once per plan"*. Measured against a dead port: **2
  attempts spent, 0 rows written.** At the 1,081-id batch the re-emit plan uses, an abort at subject 900
  discards 900 paid-for generations.

  The fix is small because the machinery already existed: `run_batch` has always handled a partial mapping
  through its `missing_answer` outcome and its per-subject `ledger.mark_done`. Only `main()` let the
  exception escape. It now records the failure, continues, and hands over the partial mapping, so a re-run
  re-plans only what is missing. `--max-consecutive-call-failures` (default 5) bounds the *opposite*
  failure — a dead endpoint ground down one doomed call per subject — and the counter is **consecutive**,
  resetting on any success, so the flaky endpoint `SEEDSMITH_LLM_ATTEMPTS=2` already exists for is ridden
  through rather than abandoned. A partial run exits non-zero, so it cannot read as success.

  **Fail-before / pass-after as a differential, not an assertion.** The old line is read out of `HEAD` and
  both loops run in one process against the real planner, with one subject raising and three siblings
  answering:

  | loop | calls spent | rows written | raised? | ledgered |
  |---|---|---|---|---|
  | old (from HEAD) | 2 | **0** | yes | — |
  | new | 4 | **3** | no | exactly the 3 survivors |

  Four tests in `CliTests` (**45 pass, up from 41**), including the flaky-endpoint case that a *total*
  failure counter would get wrong.

  **The incident, because the guard is the deliverable.** Building that differential wrote **three fixture
  rows into `gk-data/packs/fusion/data/seed/items/materials/materials.json`** — `"Wired Chaff Shard"` and siblings — plus a
  ledger path list. Cause: `plan_overwrite` takes **no** `materials_path`, and `run_batch` defaults
  `materials_path or MATERIALS_PATH`, so a harness that passes paths positionally lands in production.
  The corpus was clean beforehand, `git checkout --` restored it to **31** rows with no fixture text, and
  the differential now isolates by patching the module constant and **asserts the production file's digest
  is unchanged** — a hard refusal, not a note.

  **This is the second time this session a verification script reached a real corpus**, and the first was
  caught only because the intermediate was implausible. So the rule is now recorded as a rule:

  * **A test or probe that touches a generator MUST assert the production tree is byte-identical
    afterwards**, and fail closed on any difference. Generated data is never hand-edited, and a *test* that
    edits it is the same breach wearing a lab coat — the fixture text ends up in shipped data with nothing
    in the ledger to say how it got there.
  * **Isolate by the constant the code actually reads.** `MATERIALS_PATH` is a module attribute, so patching
    the *parameter* a function happens to accept is not isolation; it is a hope.
  * **`gk-core/scripts/guard-test-substrate.py` cannot catch this**, because it scans `tests/**` and the incident
    was in a scratch script outside it — and **that guard is in `ps1-ban-manager-20260926`'s 680-path
    fence**, which is active. So the guard gap is **reported, not touched**: the check this row asks for
    belongs beside that guard, in that stream.

  **Also filed, not edited: `--overwrite`'s help text is wrong for `material`.** It documents the flag for
  `base-type/enhancement-milestone/recipe/drop-table/combination` and omits `material`, which reads as
  "unsupported". It **works** — measured, `toGenerate: 1` for a named id against `3603` for the full
  population — so this is a documentation defect, and it was nearly a much worse one: the entire re-emit
  plan rests on that flag, and a reader of `--help` would have concluded the plan was unimplementable.
  `report/cli.py` is in this session's fence, but the help string is a shared surface, so it is recorded
  here for whoever owns the CLI text rather than edited blind.

  **Standing rule this adds:** *before asking anyone to authorize an expensive run, read the loop that
  spends the money.* A pipeline can be perfectly correct — right gate, right schema, right brief, verified
  by a simulation that says the target is reachable — and still lose the whole spend to a single exception
  on the way there. **Correctness evidence and spend-safety evidence are different questions, and passing
  the first says nothing about the second.**
- [ ] **SS-F13 — the 61 set escalations are SYSTEMATIC, not transient, and the brief has not changed since
  they were recorded. The recommendation reverses: run the 1,863 FIRST. Two CLI facts make a 61-call run
  riskier than its cost. Filed by the worktree/branch cleanup program, 2026-09-28.** **Owner:** this
  program. Diagnosis only; **no code changed**, because `setgen/brief.py` is outside this session's fence
  and the two CLI gaps sit in a surface other work is touching.

  **Why this reverses the order.** Every earlier report recommended running the 61 sets first, on the
  reasoning that they were the smaller spend and would move the gap count. Reading *why* those 61 escalated
  says the opposite. The 61 non-persisted rows carry their defects in the ledger:

  | defect | count |
  |---|---|
  | `SetCapabilityMissing` — the set grants no capability atom at all | **24** |
  | incomplete set: declares neither `blocked` nor a full set, missing `['capability']` | **13** |
  | `SetCapabilityOffRole` — capability illegal for the roles the set claims | 12 |
  | capability names a family **not in the brief's closed list** | 7 |
  | duplicate name within the corpus | 4 |
  | no defects recorded | 2 |

  So **37 of 61 (61%) failed because the model did not emit a required capability field**, and the attempt
  distribution is **3 attempts on 40 rows, 1 on 19, 2 on 2** — forty subjects were retried to the cap and
  still failed. That is not a flaky endpoint.

  **And the brief has not moved since.** The obvious hypothesis was a truncated pick list — the module's own
  `_pick_lines` docstring records that exact incident ("the first 40 of 69 capability picks", a 53-subject
  run escalating every subject on families that were real but never shown). **That was already fixed**, in
  `ec6b3166f` on **2026-09-08**, and `git log ec6b3166f..HEAD -- .../setgen/brief.py` is **empty** — no
  brief commit since. The sets ledger was last written **2026-09-12**, four days *later*. So the 61
  escalated **with the whole-pool fix already in place**, and it did not help them.

  **Therefore:** the 1,863 goes first. It has a brief fixed in this session and a simulation that says it
  lands on `NearDuplicate` **4**; the 61 has an unchanged brief and a measured 61% failure rate on the same
  model. Spending 61 calls to re-fail is the expensive way to learn something the ledger already says.

  **The leading hypothesis for the capability failures, stated as a hypothesis.** 37 refusals are all "no
  capability", and the one required field is a single pick from a **69-item** closed list printed into a
  brief. `SEEDSMITH_LLM_MODEL` names **`google/gemma-4-26b-a4b-qat`**, which `GET /api/v0/models` reports as
  `type=vlm` (SS-F9). **A vision-language model answering a 69-item closed-list pick is a plausible cause of
  a dropped single field, and it is untested** — not measured, and it is equally consistent with the brief
  simply burying the requirement. What would settle it: re-run 3 of the 61 against a text-native model and
  compare the capability rate. **The shipped CLI cannot express that experiment**, which is the second
  finding.

  **Two CLI facts, both spend hazards.**

  * **`--overwrite` is SILENTLY IGNORED for `--kind set`.** `cmd_items` routes `set`/`charm`/`combination` to
    `_cmd_items_write` (cli.py:662-669), and only the *passthrough* branch forwards `--overwrite`
    (cli.py:1369-1374) — so the flag never reaches setgen. Measured: `items generate --kind set --overwrite
    'set-species-creature.blackfootball_a' --dry-run` prints **`toGenerate: 60`**, not 1, and **exits 0**.
    The help *does* list `--overwrite`, so a caller who reads it, believes it applies, and adds it to narrow
    a run gets **the full 60-subject spend with no warning**. `materialgen` honours the same flag correctly
    (`toGenerate: 1`), so the two modules disagree about one flag name. **A flag that narrows a spend must
    refuse when it cannot narrow, never widen.**
  * **`items fill` has no `--model`.** Its flags are `--kinds --limit --count --batch-size --full
    --max-partitions --allow-production-tree --continue-on-error --no-validate-deps --verify` and no model
    selector, so every setgen run is locked to whatever `tools/seedsmith/.env` names — currently a vlm. With
    `--overwrite` inert for sets, `fill --limit 3` is the only narrowing route available, and it cannot
    change the model. **So the 3-call experiment that would de-risk 61 calls is currently inexpressible.**

  **Standing rule this adds:** *before recommending a retry, read why the previous attempt failed, and
  check whether the thing you would change has changed since.* Both halves were true here and neither was
  obvious: the failure was 61% systematic rather than flaky, and the brief's fix had already landed four
  days before the failures were recorded, so a retry re-runs the identical experiment. Corollary for flags:
  *a narrowing flag that cannot narrow is a spend multiplier* — silently widening from 1 subject to 60 is
  worse than refusing, because the caller has no way to notice.
- [ ] **SS-F14 — the 1,863 is the FIRST pass, not the whole job: a gate refusal is terminal for its pass,
  the row keeps its colliding name, and recovery is a further pass over the remainder. The per-pass budget
  is 1,863 floor / 14,904 ceiling and the pass COUNT is unknown until the run. Filed by the worktree/branch
  cleanup program, 2026-09-28.** **Owner:** this program. Now proven by tests, where it was asserted.

  **What a refusal actually does, read from `run_batch`.** A refused subject is
  `Outcome(subject_id, "refused", defects)` then `continue` — **no persist, no re-ask, no blanking**. The
  corpus therefore keeps the row *with the name that caused the refusal*. So a pass does not "clear" its
  subjects; it clears the ones the model got right, and the rest stay exactly as broken as they were.

  **Which is why one pass is not enough, and cannot be.** SS-F10's simulation reached
  `NearDuplicate` **4** by *removing* the 1,857 rows and letting the survivors stand — the correct lower
  bound, and it is a bound on a world where every re-authored name is accepted. In the real run each of the
  1,857 is instead **offered** a new name and may be **refused**, and a refused one keeps its old colliding
  name. So after one pass the expected NearDuplicate is **4 plus whatever the refusals contribute**, and the
  criterion is met only if the refusal rate is near zero. **Whether the fixed brief drives it there is not
  known and cannot be known without spending** — which is the honest state of the plan, and the reason the
  owner should be told the first pass may not finish the job.

  **Recovery converges, and that is now proven rather than asserted.** A second pass must re-derive from the
  **live** corpus, or it re-attempts all 1,863 and nothing converges. `gk-core/scripts/reemit-colliding-item-names.py
  --corpus <materials.json>` does exactly that, and `CorpusSourceTests` now pins it: a corpus with one
  shared name derives 1 id; rewriting that one id's name derives **0**; leaving it unhealed derives that
  same 1 again. So the cost is **1,863, then only what the refusals left**, not 1,863 per pass — and the
  8x retry ceiling applies **per pass**, not to the run as a whole.

  **A correction this row carries, because I got it wrong first.** Re-authoring an id with the name it
  **already** holds is explicitly **not** a collision: `run_batch` skips the subject's own `runtimeId`
  (`if not runtime_id or runtime_id == subject_id: continue`), because `--overwrite` exists precisely to
  re-emit an id and a re-emit that keeps the name is a legitimate overwrite. My first version of the test
  asserted that case would be `refused`; it is `persisted`, and the code is right. So **`refused` means the
  NEW name collides with a DIFFERENT id** — which is also the only reading under which the re-emit can make
  progress, since a gate that refused every id for keeping its own name would make `--overwrite` unrunnable.
  Recorded because a test written from the objective's framing rather than from the code would have
  "passed" against a gate that had been broken in the opposite direction.

  **For scale, the pre-fix collision rate, which is the only measurement of the model's naming behaviour
  that exists.** The rescue run produced **731** reused names spanning **2,588 of 3,633** entries — so
  **~71%** of entries held a name another entry held. That was with **no** anti-repetition clause in the
  brief. The clause is the whole point of the first of the two objective fixes, and whether it moves 71% is
  **the open question the 1,863 answers**. Treat "the gate refuses and the operator re-asks" (the fix's own
  stated rationale) as a *loop*, not a single pass.

  **Standing rule this adds:** *a gate that refuses without re-asking is a filter, not a fix, and the cost
  of clearing a population through one is the number of passes, not the population.* So quote the
  **per-pass** cost and the convergence property separately, and never present a population as "handled" on
  the strength of a plan that touches it once.
- [ ] **SS-F15 — the refusal guard is proven END TO END: a child that exits 0 while persisting NOTHING is
  refused with exit 7. Three fixture attempts failed first, and the code was right in all three. Filed by
  the worktree/branch cleanup program, 2026-09-28.** **Owner:** this program. Verification of `db3f782a4`.

  **The proof, and why a unit test could not have made it.** `db3f782a4` added
  `tally_outcomes` / `refusal_permille` and wired them into the spend loop, and both helpers are unit
  tested. But the claim that matters is about **`main()`** — that it reads the child's real outcomes and
  stops — and a test of two pure functions says nothing about that wiring. So it was proved the only way it
  can be: a local OpenAI-compatible **SSE stub** (`data: {"choices":[{"delta":{"content":...}}]}` then
  `data: [DONE]`, which is the exact framing `llm_caller._stream_once` reads) answering every subject with
  `{"blocked": ...}`.

  | | |
  |---|---|
  | fixture | the first **60** real entries of the rescue corpus |
  | the shipped gate derives | **8** colliding ids |
  | stub calls served | **8** |
  | child exit code | **0** — a `blocked` outcome is not a call failure |
  | runner | `REFUSED [batch-1] STOPPED at batch 1 of 1: 8 of 8 subjects came back refused/blocked/missing (1000 per mille), over the --max-refusal-rate-permille budget` |
  | runner exit code | **7** |
  | production corpus | **byte-identical**, `b6cc60b7` before and after, **31** rows |

  So the exact sequence the fix exists for — **child succeeds, pass means nothing** — now refuses. Before
  `db3f782a4` the same run printed `completed 8 ids across 1 batches`.

  **`blocked` was chosen over colliding names on purpose.** A refusal persists nothing, so this proof
  **cannot** dirty `data/seed/items/materials.json` — which matters, because SS-F12 records a scratch
  harness of mine writing three fixture rows into that file. The digest is captured before and after and a
  mismatch is a hard refusal anyway, but the shape means the guard was never at risk. *Prefer a fixture
  whose failure mode writes nothing.*

  **Three fixture attempts failed, and the code was right every time** — which is the reusable part, and
  the reason the row is here rather than just the result.

  1. **`--max-batch-chars 40000`** was refused by the runner's own precondition: it exceeds the Windows
     **32,767**-character command-line limit. The guard that exists to stop a batch dying at the shell
     caught me planning one.
  2. **Four fabricated ids** (`trophy.species.probe0.1`) were refused by the **vocabulary gate** —
     `probe0` is not a real species. That gate's own test is `test_a_fabricated_id_is_refused_loudly`, and
     it fired on a probe I wrote *to test the generator*. Zero stub calls, because it failed before any
     HTTP request.
  3. **Four entries taken from the refused list** derived **zero** ids, so the runner exited 0 having done
     nothing and the stub was never called. The reason is the subtle one: a refused entry collides with an
     entry that came **earlier** in the corpus, so lifting the refused entries and dropping their holders
     leaves a corpus with no collisions at all. **A fixture built from a derivation must carry the context
     the derivation depended on** — a prefix of the real corpus does, a selection of its refusals does not.

  Attempts 2 and 3 both surfaced as *the guard not firing*, which is the most dangerous shape a probe can
  fail in: it looks exactly like the bug under test. **So a probe must distinguish "the guard did not fire"
  from "the probe never reached the guard"** — which is why the final version derives the fixture's ids
  through the shipped gate, prints them, and **refuses to run if the derivation is empty** rather than
  reporting a guard failure.

  **Standing rule this adds:** *a green probe is only evidence if it can be shown to have exercised the
  thing.* Three times here the honest answer to a surprising result was "my fixture, not the code" — and
  the way to tell the two apart is to have the probe **print what it handed the system and refuse to
  continue when that is empty**. Corollary: *prefer fixtures whose failure mode writes nothing*, so the
  proof of a safety property cannot itself breach the property it is proving.
- [ ] **SS-F16 — the objective's 87-vs-830 comparison re-measured at the CURRENT base reads 87-vs-820 with
  NearDuplicate 737, not 747. NearDuplicate is the ONLY family that moves, so the re-emit is the whole of
  the fix. Filed by the worktree/branch cleanup program, 2026-09-28.** **Owner:** this program. Measurement
  only; no claim rests on the stale figure once this row exists.

  **Why re-measure rather than inherit.** The constraint the objective states — integration **87** versus the
  rescue's **830**, differing **only** in `SemanticDedup/NearDuplicate` at **747** — was measured against an
  older tree. This session has since landed **19** commits, several of them to the seedsmith adapters
  themselves, and other streams have moved. The objective's own rule is that *a dated reading is a reading,
  not a contract*, so the comparison is re-run rather than trusted. Measured on a real copy of the real tree
  with the repo's own `python -m seedsmith check <tree> --adapter items`, replacing **only**
  `gk-data/packs/fusion/data/seed/items/materials/materials.json` — which is exactly what `git checkout <ref> -- <path>` does, and
  exactly the state the re-emit starts from (the write-target refusal shipped in `142ccde0e`, which is why
  that install has to happen before any spend).

  | family | HEAD as it stands | with the rescue's corpus installed | delta |
  |---|---|---|---|
  | `Content/FieldMissing` | 5 | 5 | — |
  | `Coverage/EmptyPartition` | 67 | 67 | — |
  | `Coverage/PairwiseHole` | 6 | 6 | — |
  | `Quality/FlavourMissing` | 5 | 5 | — |
  | `SemanticDedup/NearDuplicate` | **4** | **737** | **+733** |
  | **total** | **87** | **820** | **+733** |

  **Two corrections, and one confirmation that matters more than either.**

  * **HEAD is still 87**, and all five families are byte-for-byte the figures the objective carries. So the
    *baseline* half of the constraint is current, not stale.
  * **The rescue side is 820, not 830, and NearDuplicate is 737, not 747** — the ref's tip no longer matches
    whatever CB42 measured. Nothing about the decision changes, but every number quoted from here on uses
    **820 / 737**, and a reader who cross-checks against the objective will find a 10-gap discrepancy that
    this row explains rather than leaves as a mystery.
  * **The confirmation: NearDuplicate is the ONLY family that moves.** Not one other family shifts, so the
    re-emit genuinely is the whole of the fix and needs no companion change elsewhere — which is the premise
    the entire step rests on, and it had never been checked at this base.

  **And a change nobody costed: the NOTE count goes 612 -> 10,484, about 17x.** Notes are advisory severity
  and outside the success criterion, but a 17x rise is a real difference a reviewer will see, and it says
  something specific: the rescue corpus carries a large volume of *lexically* near-duplicate names that sit
  **below** the GAP threshold. The gate added in `b212e8688` refuses **exact / key** collisions
  (`_name_key`: whitespace collapsed, casefolded), so it will not touch those, and they will survive the
  re-emit as notes. That is consistent with SS-F10's finding that the 6 residual rows were *exact*
  cross-corpus matches rather than lexical ones — and it means **"no NearDuplicate regression" is a
  statement about 4 findings, not about the corpus's overall name distinctness.** Worth saying plainly to
  the owner before the run, because a 10,484-note corpus reads very differently from a 87-gap one.

  **Standing rule this adds:** *a comparison that justifies a decision is part of that decision's evidence,
  and it expires like any other reading.* Re-measure it against the tree the decision will be taken on — and
  when a re-measurement disagrees with a recorded figure, **record both and say which is current**, because
  a silent correction is indistinguishable from an error to the next reader.
- [ ] **SS-F17 — the name gate gains its LEXICAL half, and it RETRACTS the population figures I reported
  before it: they came from a gate that was non-deterministic and could not see what it claimed to. The
  real cost is **+314** subjects, not the +26 I quoted, and the benefit is **535 -> 0** near-duplicate
  pairs. Filed by the worktree/branch cleanup program, 2026-09-28.** **Owner:** this program. Code fixed and
  tested; the retracted figures are withdrawn here rather than left to be found.

  **What the second half is.** `_name_collision_defects` is an O(1) equality test on `_name_key`, so it
  closes verbatim and case/spacing reuse and nothing else. `SemanticDedup/NearDuplicate` is a different
  predicate, and it has both a GAP tier and a much larger NOTE tier. The objective's own second gap names
  the capability to use — `shingles(k=5)`, `minhash_signature`, `jaccard_estimate`, `lsh_bands`,
  `near_duplicate_threshold=0.6` — and the first implementation used only the `_name_key` half. So this
  adds the lexical half, **per subject**, reusing `metrics/dedup.py` rather than inventing a second notion
  of similarity. Per-subject rather than `setgen`'s population-level `dedup_report(names).rate_permille`
  because `materialgen` writes as it goes and a population rate is only evaluable once the batch is on
  disk — the same reason the key half is per-subject.

  **Measured, at the current base, on the real corpus:**

  | | key gate only | key + lexical gate |
  |---|---|---|
  | survivors | 1,776 | **1,462** |
  | exact-Jaccard near-duplicate pairs among them | **535** | **0** |
  | subjects to re-author (within-materials) | 1,857 | **2,171** |

  Plus the **5** cross-corpus rows the key gate keeps but a charm or a set already holds — one fewer than
  the **6** recorded earlier, because the lexical gate now refuses one of them itself, which is the two
  halves composing rather than double-counting. **Total 2,176**, against the **1,863** the plan carried
  before this row. Determinism verified across **three separate processes**: identical kept-set, identical
  counts, every time.

  **The retraction, and the bug behind it.** I reported, an hour before this row, that a Jaccard gate would
  catch **47 pairs** across **73** survivors and cost **+26** subjects. **All three figures were wrong**, and
  the reason is a defect I had just written: the gate passed **shingle sets** to `jaccard_estimate`, which
  takes **signatures** and returns the MinHash agreement ratio. Handed two `frozenset`s it `zip`s two
  UNORDERED collections, so the verdict depended on set iteration order and therefore on `PYTHONHASHSEED`.
  The tell was arithmetic, not a failing test: **the same corpus planned 1,884 ids in one invocation and
  1,886 in the next.** A gate whose verdict moves between runs is not a gate.

  **And the fix is not "pass the right argument".** Two further reasons an ESTIMATE is the wrong thing to
  refuse a subject on, both of which point at the exact predicate:

  * a 32-hash signature quantises to about **0.031** and carries variance, so a subject can be refused on a
    number that is not the similarity;
  * **LSH banding is a prefilter, and a prefilter that can MISS a genuinely-near pair is unsound inside a
    gate.** A gate must not have a blind spot; the estimate's affordable approximation is fine for triage
    and wrong for adjudication.

  So the gate computes `|A ∩ B| / |A ∪ B|` over the shingle sets directly and drops the banding, with a
  `name -> (shingles, signature)` cache so the O(kept)-per-subject cost stays affordable — the whole corpus
  in **4.0s**, 1,462 survivors, and with the exact predicate the greedy streaming gate leaves **zero**
  residue rather than the 13 the estimate left, because set arithmetic is monotone in a way the sampled
  estimate is not.

  **What this costs the owner, stated plainly: +314 calls, about 17% on top of 1,863.** It is a QUALITY
  decision beyond the success criterion — the criterion is `NearDuplicate <= 4` and the key-only 1,863
  already reaches it, because exact-duplicate names are the GAP tier and lexical near-duplicates are the
  NOTE tier. What it buys is that the corpus's name distinctness becomes a property of the RUN rather than
  of luck, and the 10,484-note population (SS-F16) stops being inherited.

  **Standing rule this adds:** *before quoting a population derived from a similarity predicate, read the
  predicate's signature — a function named `jaccard_estimate` may take signatures, and passing it the
  objects whose name it shares produces a number that is not the quantity.* Corollary, and this is the part
  that generalises: **a non-reproducible number is a bug report, not a rounding difference.** Two runs of
  the same command disagreeing by 2 is a defect in the command, and the fix is to find it rather than to
  average it.

- [ ] **SS-F18 - the setgen brief never said `capability` is MANDATORY, and 37 of the 61 escalated
  subjects prove it. Filed 2026-09-28.** The gate premise in the objective ("setgen already carries its
  gate") is **true and incomplete**: the gate is real, the BRIEF is what fails. Read from the run
  ledger's own `defects` rather than inferred - **24 `SetCapabilityMissing`** (the set grants no
  capability atom at all) plus **13** "declares neither `blocked` nor a complete set: missing
  `['capability']`" is **37 of 61**, with 40 rows already at the 3-attempt cap and the brief unchanged
  since `ec6b3166f` (2026-09-08).

  `capability` was item 1 of four in "Choose, and nothing else", unannotated, while the `blocked`
  escape hatch sat twenty lines below the capability list. The model, unable to decide, emitted
  `capability: null` without setting `blocked` - and the gate correctly refused it as stat filler.

  **The schema is NOT the fix, and that is recorded so the obvious wrong turn is not re-taken.**
  `capability` is `["object", "null"]` while **`blocked` sits in the same `required` list**, so a
  blocked subject legitimately has no capability; tightening it to `object` would make "I cannot author
  this theme" inexpressible. JSON Schema `if/then` could express the conditional, but the GBNF
  conversion constrained decoding relies on does not enforce it, and this package deliberately carries
  no `jsonschema` dependency. `setgen/schema.py` is claimed in the fence for that reason alone.

  The clause now says the field is not optional, states the consequence (REFUSED), frames it as
  exactly **TWO** valid answers (one family, or `blocked` with a reason), and rules out the shape the
  failures actually took. A second test pins that `blocked` is still reachable, because a clause that
  closes the hatch would convert a refusal into a fabrication - worse than the bug being fixed.

- [ ] **SS-F19 - the setgen brief OFFERED 21 capability ids that the schema refuses on arrival, and
  the tolerant parser written to accept them could never run. Filed 2026-09-28.** The remaining **7**
  of the escalated subjects, the spelling half of the same answer field.

  `_pick_lines` printed `p.pick_id` for the capability pool, and for an elemental pick `pick_id` **is**
  `f"{family}.{variant}"` (`vocab.py:44`) - so **21 of 69** printed picks were
  `atom.deathblast.fire`-shaped. The closed `capability.family` enum comes from
  `distribute.capability_family_ids`, which returns UNIQUE BASE family ids: **51** values, none
  carrying an element suffix. `answers.schema_defects` enforces that enum on the way **in**.

  The consequence is the part worth keeping: `seedfile.resolve_capability` exists **specifically** to
  tolerate this echo - its docstring records `{"family": "atom.deathblast.fire", "variant":
  "atom.deathblast.fire"}` as a real 2026-09-08 live shape, calls it "legal, unambiguous", and tries
  `family`-as-pick_id **first**. It could never run, because the draft was turned away one layer
  earlier. **A tolerant parser sitting behind a stricter schema is dead code**, and the two halves of
  the package disagreed about what a legal capability is.

  Fixed in the brief, because the schema is right - `capability_family_ids` returning base families is
  its documented contract, and widening the enum would make a "family id" something that is not a
  family. The list now groups BY FAMILY with elements spelled out, and the item says `family` takes a
  family id exactly as printed, no suffix ever, element in `variant`. **Output is identical either way**:
  `seedfile._atom_row` writes `family`/`params.element` from the RESOLVED pick, never the raw string.

  Fail-before/pass-after, measured in one process: **HEAD offered 69 ids of which 21 are refused by
  the enum; this one offers 51 of which 0 are.** 69 -> 51 is grouping, not truncation - all 69 picks
  stay reachable through the element lists, and a test asserts exactly that.

  **One pre-existing assertion was changed, deliberately and recorded as such.**
  `RunTests.test_the_brief_prints_every_capability_and_stat_pick_no_truncation` asserted every
  capability `pick_id` appears verbatim - which **is** the defect, since it pinned the spelling the
  schema rejects. Its intent ("no pick is offered-but-unnameable, or a model gets blamed for
  hallucinating a legal choice") is preserved and strengthened: the capability half now checks the
  split form, and `CapabilityListTests` replaces substring matching with an exact parsed token-set
  comparison. Substring matching was weak there anyway - `atom.ward` passes inside `atom.warded` - and
  the in-place comment says so, so the cheap smoke check is not mistaken for the proof.

- [ ] **SS-F20 - the setgen brief never said the `capability` and the `members` have to AGREE, and it
  asks for them in the wrong order. Filed 2026-09-28.** The last **12** of the 61, and the third
  instance of one defect class: **a rule the gate enforces that the brief never mentions.**

  `distribute.py:210-214` refuses a set whose capability family's own roles do not intersect the roles
  its members claim - an INTER-FIELD constraint. The brief never says the two fields interact, and
  `capability` is item 1 while `members` is item 2, so the model must commit to a capability **before**
  the roles it has to be compatible with exist.

  Measured: **all 69** capability picks carry roles, so the rule can never be skipped for any family -
  there is no unconstrained family to hide behind. The brief already printed a `roles:` annotation per
  line, carrying exactly the information needed to act, and said nothing about it.

  The clause now names the rule and its consequence and offers the escape hatch, which is **measured
  rather than assumed**: `jewel-major`, `jewel-minor-a` and `jewel-minor-b` are legal on **69 of 69**
  picks, so a set claiming any jewel role can never trip this. A test asserts that relationship over
  the whole pool, so a future vocabulary change breaks the advice instead of misleading.

  Two supporting assertions, because the clause tells the model to TRUST the annotation. The printed
  `roles:` line must **equal** the family's roles narrowed to the twelve claimable ones, by exact set
  comparison against the vocabulary. That test first compared against the RAW `pick.roles`, failed on
  `sense`, and **the code was right and the test wrong** - `roles.DROPPED_ROLES` (`head-guard`,
  `sense`, `ward-array`) never reaches the brief, correctly, since a dropped role is not one a member
  can claim. The comment in place records that, because comparing against the raw roles is the obvious
  mistake to re-make.

  **Accounting, stated rather than rounded: 37 (F18) + 7 (F19) + 12 (F20) = 56 of the 61.** Five are
  unaccounted for and are NOT claimed as fixed. 40 rows were already at the 3-attempt cap, so the
  cap - not the brief - is plausibly the binding constraint on the remainder; that is a reading, not a
  measurement, and closing it needs the 61 calls anyway.

- [ ] **SS-F21 - the re-emit's 2,176 subjects rest on an assumption nobody had measured, and the measured
  supply of acceptable names is BELOW it. The pilot is now the only way to find out, and it can finally
  report WHICH question it answered. Filed 2026-09-28.**

  The plan derives **2,176** subjects that fail the name gate, and assumes each can be re-authored into
  a name that PASSES it. Nobody had checked whether the model can supply 2,176 mutually-acceptable
  names. It can be checked for free, from the one sample of the model's output that exists.

  **Measured**, running the shipped gate's exact predicate (character 5-gram shingles, exact Jaccard -
  the ratio computed over the shingle sets directly, never handed to `jaccard_estimate`, which takes
  SIGNATURES per SS-F17) over the rescue corpus's own names, in corpus order, greedy:

  | what | count |
  |---|---|
  | trophy rows in the rescue corpus | 3,599 |
  | DISTINCT names the model produced | 1,742 |
  | of which used 2+ times | 731 names covering 2,588 rows (**71.9%**) |
  | most-reused single name | `'Lineage Seal'`, **79x** |
  | **the gate keeps, of its own 1,742** | **1,428** |
  | refused as near-variants of each other | **314 (18%)** |
  | subjects the plan derives | **2,176** |

  So **18% of the model's own distinct output is mutually too-similar to coexist**, and its demonstrated
  supply of acceptable names is **748 short** of the plan's subject count.

  **What this is NOT.** It is not a proof the pass is impossible. This sample is PRE-FIX output, and the
  objective's first gap - the brief fix in `b212e8688` - targets precisely this failure. And a retry can
  reach names outside the 1,742. What it IS is proof that the subject count rests on an unmeasured
  assumption, which is the thing worth knowing BEFORE a 2,176-call authorisation rather than after it.

  **A reading, clearly labelled as one.** If the post-fix yield per subject is the same 82%, the
  remainder decays geometrically over passes - 2,176 -> 392 -> 71 -> 13 -> 2 - so ~5 passes and ~2,654
  calls, NOT the 17,408 ceiling. The ceiling is 8 attempts PER SUBJECT and is not what the measured yield
  requires. The pilot is what converts this reading into a measurement, and it is ~20 calls.

  **And the pilot could not report the answer it was run to produce.** `materialgen` has ONE outcome name
  for every refusal, `"refused"`, and `tally_outcomes` read only that field and **discarded `defects`** -
  which the child does serialise and which names the gate. So a name collision and a schema/tag-axis
  violation were indistinguishable at the exit-7 budget stop. Fixed in `288a5d873`: the two regimes
  demand opposite moves (resize the subject count versus fix the prompt and spend nothing), and an
  uninterpretable stop is not a gate. Fail-before is concrete - HEAD's tool returns `{'refused': 1}` on a
  refusal payload, dropping `defects` outright.

  **Standing rule this adds: a gate that STOPS a run is only useful if it says which gate stopped it.**
  "61 refused" and "40 name collisions, 21 schema defects" are not the same report, and the second one
  is the one that tells you whether more spending is the next move.

  ### SS-F21 CORRECTION (2026-09-28) - the shortfall is **714**, not 748, and the kept count is **1,462**,
  ### not 1,428. Both figures in the entry above are superseded; the finding and its standing are not.

  A dry run of the runner against the ref - which is what the plan is actually built from - printed
  `kept by the gate: 1462` where the feasibility pass had said 1,428. Two different numbers for what
  looks like one question, so the difference was traced rather than averaged.

  | | rows gated | distinct names | kept |
  |---|---|---|---|
  | the feasibility pass, **trophies only** | 3,599 | 1,742 | 1,428 |
  | the tool, **all entries** | 3,633 | **1,776** | **1,462** |

  The cause is a filter, not a defect: the feasibility pass narrowed to `materialClass == "trophy"`
  (3,599 rows) while the runner gates the whole corpus (3,633). The **34 non-trophy rows** - 14 shard, 8
  substrate, 6 essence, 3 catalyst, 3 assurance - contribute 34 further distinct names, and all 34 are
  kept. 1,742 + 34 = 1,776 and 1,428 + 34 = 1,462, exactly.

  **A second, independent confirmation fell out of the reconciliation:** the tool's two gate halves
  report `byKey 1540` and `byNear 631`, summing to the 2,171 it refuses - and 1,540 + 631 + 5
  cross-corpus is the 2,176 the plan derives. The near half alone refuses **631** of the 1,462 kept
  names' neighbours, so the lexical half is doing real work and is not decorative.

  **This is the same self-correction class as SS-F17: a right value answering a different question.** The
  kept count was never wrong arithmetic - 1,428 really is what a trophy-only pass keeps. It was the
  wrong SCOPE, and only a second measurement against the tool that generates the plan could reveal it.
  The rule generalises: **before comparing a hand-rolled measurement against a tool's own output, match
  the tool's SCOPE, not just its method.** Both used the same exact predicate and still disagreed by 34,
  because one of them was counting a subset and neither said so in its own output.

  Unchanged: the demonstrated supply of mutually-acceptable names (1,462) is **714 short** of the 2,176
  subjects, the sample is pre-fix output, the brief fix targets exactly this, and the pilot is what
  converts the geometric-decay reading into a measurement.

- [ ] **SS-F22 - the objective's step 3 stops at 61 of the 67, and the other 6 were never examined. Two
  are a GENERATOR defect that would have made a closure run ADD a gap; two more have no generator at all;
  and the 2 base-types partitions already hold 40 rows under wrong declarations, so generating into them
  would DUPLICATE. Filed 2026-09-28.**

  Step 3 reads *"run the adapter that can actually close the 67 - `setgen` for the 61 sets"*, and stops
  counting there. Re-measured from `seedsmith check`, the 67 EmptyPartition gaps decompose as:

  | partition family | count | adapter | status |
  |---|---|---|---|
  | `sets/*` | **61** | `setgen` | viable - its gate is real, and its brief carried three defects now fixed (SS-F18..F20) |
  | `base-types/*` | **2** | `basetypegen` | **defective - see below** |
  | `display-templates/*` | **3** | **none** | no `--kind`, no adapter |
  | `attributes` | **1** | **none** | no `--kind`, no adapter, **and no authored shape** |

  The `--kind` choices are `set, charm, combination, base-type, enhancement-milestone, recipe,
  drop-table, gem, material, consumable, affix-family, trophy`. `base-type` is there; `display-template`
  and `attribute` are **not**. And `kinds.py` explains why `attributes` cannot be rescued by writing an
  adapter: it is registered `_undefined("attribute", ...)` because, in its own words, its *"shape has
  never been authored against"* and *"seed-contract.md has no section 10 table for it"*. So **1 of the 67
  is blocked on a spec decision, not on an agent** - and the 3 display-templates are blocked on an adapter
  nobody has written. That is 4 of the 67 with no path, which the plan does not say.

  **The 2 base-types partitions were a live trap, and `basetypegen` could not have closed them.** It wrote
  `_meta.partition` as `f"base-types/{frame}-{role}-{band}"` - dash-separated, frame-first. Measured over
  all 15x2x2 role/frame/band combinations the registry allows: the registry allocates **62** base-types
  partitions and **0** are dash forms; **60 of the 62** shipped files declare a name matching the registry
  character for character; and **60 of 60** names HEAD would write fall **outside** the registry.

  That is a correctness bug, not a spelling preference. `Corpus.model:190` reads `entry.partition` from
  `_meta.partition`, and `Coverage/EmptyPartition` computes `sorted(allocated - corpus.partitions)`. A
  base-type run would have written rows the metric **cannot see**, under a name the registry has never
  heard of - **adding a phantom gap instead of closing the one it was invoked for**, with the rows
  invisible to the very check credited for generating them. Fixed in `b232cf0d8`: the emitted name is now
  built by `registry_partition_name()` and asserted against the SAME registry source the metric reads,
  refusing with a named `PartitionNameNotAllocated`. The first version of that guard read
  `partition_kind_map()`, which maps partition -> kind and has no `"partitions"` key, so it returned an
  empty set and **the guard was inert** - caught by a test asserting a refusal that never came. Recorded
  because a gate that reads a different registry than the metric it guards answers a different question.

  **And the 2 partitions must NOT be generated into even now.** `humanoid-manipulator-b.json` declares
  `humanoid/manipulator/b` - transposed AND prefix-less - while holding **28** rows, and
  `mantle/humanoid/a.json` declares `mantle/humanoid/a` - prefix-less - while holding **12**. Those are
  exactly the 2 the check reports empty, so they are a **DECLARATION defect over 40 existing rows**, not a
  content gap. Generating into them would duplicate rows that already exist. Correcting the two
  declarations is a data change through the generator and is deliberately NOT done here.

  **So the honest map of the 67 is 61 addressable by an existing adapter, 2 needing a declaration repair
  over existing content, 3 needing an adapter that does not exist, and 1 needing a spec decision before
  any adapter could exist.** "Run setgen for the 61" is right and is not sufficient, and the difference
  matters because a plan that believes it closes 67 will read a residual 6 as a failure of the run rather
  than as four distinct causes.

  **Separately, the objective's step 5 is now fully de-risked.** Read-only audit of the ref: `6fc3d2b21`
  is held by **exactly 1** ref, its parent `784555a1b` by **11**, the ref has **exactly 1** commit
  reachable that integration does not have, that commit carries **56** blobs absent from integration's
  87,750 reachable ones, and **that commit is already recorded at HEAD** (CB41). So closing the ref
  destroys content whose findings are committed - not the findings. CB43 remains **OPEN on the owner's
  call**, and its own re-review trigger names the bar: *"a regenerated corpus that reduces the 87 and adds
  no `SemanticDedup/NearDuplicate`"*. A materials-only re-emit cannot meet that on its own, because
  materials contributes **0** of the 67 empty partitions and **0** of the 4 NearDuplicate gaps (all four
  are in `recipe`) - it is a **maintenance** operation, not a closure one. The 61 sets are what move the
  number.

- [ ] **SS-F23 - the gap count moved for the first time: 87 -> 85, and it took no model call. The 2 were a
  DECLARATION, not a gap, and fixing them through the generator was the whole cost. Filed 2026-09-28.**

  Measured with the repo's own `seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`, in the working tree,
  after the commit:

  | metric family | before | after |
  |---|---|---|
  | `Coverage/EmptyPartition` | 67 | **65** |
  | `Content/FieldMissing` | 5 | 5 |
  | `Coverage/PairwiseHole` | 6 | 6 |
  | `Quality/FlavourMissing` | 5 | 5 |
  | `SemanticDedup/NearDuplicate` | 4 | 4 |
  | **total** | **87** | **85** |

  Every NOTE family is unchanged too, `SemanticDedup/NearDuplicate`'s 554 included. **Stated precisely: this
  is NOT the objective's materials re-emit and does not satisfy its success criterion** - that criterion
  asks for a regenerated *materials* corpus at or below 4 NearDuplicate. This is a regenerated
  *base-types declaration*. What it does establish is that the 87 baseline was carrying **2 findings that
  were never content gaps at all**, so any plan that sized work against 87 was sized against a number two
  too high.

  **The mechanism, because it is the reusable part.** `Corpus.model:190` reads `entry.partition` from
  `_meta.partition`, and `Coverage/EmptyPartition` computes `sorted(allocated - corpus.partitions)`. A file
  declaring a name the registry never allocated is invisible to the metric **however many rows it holds** -
  and `humanoid-manipulator-b.json` (28 rows, declares `humanoid/manipulator/b`) and
  `mantle/humanoid/a.json` (12 rows, declares `mantle/humanoid/a`) did exactly that. The other 60 of 62
  files declare an allocated name character for character, and the two offenders disagree with EACH OTHER
  (one transposes the axes as well), so there is no "mostly right" convention to pattern-match.

  **Landed as a generator re-stamp, not a data edit**, because those files are seedsmith OUTPUT - every one
  carries `_meta.model` / `promptVersion` / `batch`. `basetypegen/redeclare.py` mirrors the two repairs the
  adapter has already shipped (`resocket`, `successor-edges`): own `main(argv)`, `--dry-run` / `--write` /
  `--json` / `--authored-utc`, run as `python -m`, one `_meta.amendments` record per file with
  `promptVersion: "n/a-mechanical-redeclare"` and a note that no model was called. The replacement is
  DERIVED from the file's own entries' `(role, frame, band)` - the authority `partitions.py` names - and
  written only when that derived name is allocated, so the repair never invents a name and a correct file
  is a byte-for-byte no-op.

  **Measured before attempting, then verified after writing.** Making 40 rows newly visible could plausibly
  have surfaced findings from any other partitioning metric, so the check was run on a scratch COPY first
  (87 -> 85, nothing regressing) before a byte was written to the tree. After writing, both files were
  verified against HEAD: `entries` byte-identical, every non-`_meta` key identical, exactly
  `partition` + `amendments` changed in `_meta`, and no drift in `model` / `promptVersion` / `batch` /
  `authoredUtc` / `contractVersion` / `sourceRef` / `registryVersions` / `exemplarVersion`.

  **The standing rule this adds: a coverage gap is a CLAIM about content, and a claim can be false in
  either direction.** A partition can be reported empty because it has no rows, or because its rows are
  invisible - and the second looks exactly like the first in the gap list while inviting the expensive,
  wrong repair (generating duplicates). Before scheduling generation for an "empty" partition, establish
  that it is empty *for a reason a generator would fix*.

  **And the fence caught what a summary had hidden.** `fence_check.py` REFUSED this commit's two data
  files: the fence holds four SPECIFIC `gk-data/packs/fusion/data/seed/items` paths and **no** `gk-data/packs/fusion/data/seed/items/**` glob. I had
  been carrying a belief that the fence covered the whole item seed tree; the record says otherwise and
  staging those files is what disproved the belief. Claimed by EXACT path afterwards - a glob is what let
  the false belief survive - and the discipline that caught it is the reason to keep the check: a tool
  reading the record beat a summary asserting from memory.

- [ ] **SS-F24 - step 3 is 61 calls in TWO invocations, and it is now measured rather than assumed. The
  `--overwrite` flag the plan would have used was accepted and silently ignored. Filed 2026-09-28.**

  Step 3 says *"run `setgen` for the 61 sets"*. The 61 is right; the shape was not, and two things had to be
  measured before it could be run at all.

  **The 61 partitions need TWO populations, and neither alone is enough.**

  | invocation | `toGenerate` | covers |
  |---|---|---|
  | `items generate --kind set --population species` | **60** | 60 of the 61 empty `sets/*` |
  | `items generate --kind set --population build` | **1** | the 61st, `set-build-build.might-offense` |

  Checked in both directions, because "60 plus 1" is arithmetic that invites a confident wrong answer:
  **61 of 61** empty partitions are covered by the union, and **NOT ONE** planned subject fails to close a
  gap - so there is no wasted call and nothing to select. `toGenerate` was also checked against the
  subjects actually written, and the run refuses if the two disagree, because a summary that disagrees with
  its own plan is exactly the kind of thing a spend decision must not rest on.

  **The recurrence that nearly made this a wrong answer.** A literal intersection of the two id spaces
  returns **0 of 61**, because the same species is spelled two ways - the partition is
  `sets/blackfootball-a` and the subject is `set-species-creature.blackfootball_a`. Worse, the build id is
  HYPHENATED after the dot (`set-build-build.might-offense`) where the species ones are underscored, so a
  normaliser written for the first shape does not match the second. This is the same self-correction class
  as SS-F17: a right value answering a different question, and it reads exactly like "the plan covers
  nothing" if the namespaces are compared literally.

  **`--overwrite` would have wasted the run, and was silently dropping the ids.** Found while checking
  this, not while running it: `items generate --kind set --overwrite <1 id>` reported `toGenerate: 60`,
  `plannedBeforeLimit: 60`, exit 0, and a plan summary that reads like success - having named ONE id.
  `setgen.plan_run` takes no `overwrite` argument and setgen has no `plan_overwrite`, so the branch cannot
  narrow its plan and never did. Fixed in `05fe49fba` as a **refusal**, not a feature: the flag's help
  documents it for other kinds only, and nothing needs it here because the natural plan IS the closure
  plan - the actionable scope is `--population`, which is what the refusal now says. `material` and
  `trophy` are unaffected (they route through the passthrough, which forwards it), and a test pins that
  every accepted kind either honours or refuses the flag.

  **The false-claim sweep came back negative, which is worth recording as a result.** The base-types repair
  (SS-F23) established that a partition can be reported empty because its rows are INVISIBLE rather than
  absent. That was checked for ONE kind, so the whole corpus was swept: every declared `_meta.partition`
  against the registry's allocated set, and every reported-empty partition against its family. **No
  reported-empty partition sits in a family with an unrecognised declaration**, so the 3 `display-templates/*`
  and the 1 `attributes` partition are **genuinely** empty - the base-types pair was the only instance of
  this class. That is a negative result, and it is what makes the remaining 65 honest: 61 addressable, 3
  needing an adapter nobody has written, 1 needing a spec decision.

  Incidentally confirmed while sweeping: **`gk-data/packs/fusion/data/seed/items/materials/trophy-registry.json` already holds
  the 3,600 trophy subjects** as `{materialId, scope, scopeKey, slot}` - a deterministic planner output
  (batch from `808a157c9`), not corpus rows, which is why it correctly declares no partition. So step 2
  has nothing to plan either: its 3,600 subjects are enumerated at HEAD, and only the names are missing.

- [ ] **SS-F25 - a live pilot said the re-emit was a variety limit, and the fix moved the yield from 56% to
  87.5%. A refused NAME was TERMINAL, which the 2,176-subject plan had assumed otherwise. Filed
  2026-09-28.**

  The owner authorised the spend. Pre-flight against `tools/seedsmith/.env`: endpoint live,
  `google/gemma-4-26b-a4b-qat` loaded, 420s timeout, 2 transport attempts, 3 heal rounds,
  `SEEDSMITH_ALLOW_PRODUCTION_TREE=1`. Step 3 ran first (cheaper, and it moves the number); step 2's
  pilot ran second and is the finding here.

  **PILOT 1 - the yield, measured.** 16 subjects, **9 persisted, 7 refused - 437 per mille** - and the
  exit-7 budget guard reported by gate: **15 `name_gate`, all name collisions, not one malformed answer.**
  The tool's own regime sentence read: *"the model answers and the name is not distinct, so this is a
  variety limit, and more spending buys more of the same name."* That is the instrument working as built -
  and it distinguished the two regimes a bare count could not.

  **But 56% was the FINAL yield, not a first-attempt figure.** `materialgen.main()`'s live loop asked
  each subject exactly once; `run_batch` recorded a collision and moved on, so a refused subject kept its
  old colliding name and its gap stayed open. Spending 2,176 subjects at that rate buys roughly 1,200 rows
  and 1,000 escalations, and a plain re-run re-asks the identical question - which the setgen run showed
  independently, with 3 torch-themed species each returning 'Torch of the Stump' on two separate runs.

  **THE FIX, and the machinery already existed.** `setgen` had solved this exact shape - `cli.py` appends
  "Previous attempt was rejected because its name duplicated an existing item. Choose a completely new
  surface name" to the subject brief - but the re-ask is wired to `--retry-blocked`, which selects only
  `blocked` subjects, while a name collision ESCALATES terminally and never reached it.
  `--max-name-attempts` (default 3) now re-asks exactly those subjects with the refused name AND the id
  holding it quoted, and says to change ONLY the name so a retry cannot trade a name collision for a schema
  defect.

  **PILOT 2 - the measurement, same 16 subjects, same corpus, same model:**

  | | persisted | refused | rate | exit |
  |---|---|---|---|---|
  | before | 9 | 7 | **437 per mille** | 7 (budget stop) |
  | after  | **14** | **2** | **125 per mille** | **0 (clean stop)** |

  A yield of **56% -> 87.5%**, and the pass now completes under budget instead of tripping it. That is what
  makes the 2,176-subject plan viable: at this rate the geometric decay SS-F21 predicted collapses to a
  handful of passes, and the projected cost is ~3,000 calls rather than 17,408.

  **A defect the tests caught in the fix itself, recorded because it is the class this programme keeps
  hitting.** The first retry predicate was `"name" in d.lower()`. It also matches
  `$.name: expected at least 3 characters` - a SCHEMA defect that names the FIELD - so the retry would
  have re-asked exactly the refusals it is careful not to touch, spending calls to re-roll correct
  answers. It is now `_is_name_defect`, matching the name gate's own two prefixes, and a test pins the
  `$.name` case specifically. **A substring test on a defect string is a guess about which gate fired; the
  gate's own message prefix is the fact.**

  **The pilot's own effect on the corpus, stated as a direction and not a total.** With the rescue base
  installed, `seedsmith check` reads 755 gaps, of which 729 are `SemanticDedup/NearDuplicate` - the
  rescue corpus's PRE-EXISTING defect, and exactly why the objective forbids merging it. The rescue alone
  measured 747, so the 14 re-emitted names moved it **747 -> 729**: the pass reduces the defect it
  targets. That figure is NOT comparable to the 30-gap reading on integration's 31-row corpus, and
  quoting it as progress toward "<= 4" would be the wrong denominator. Reaching <= 4 needs all 2,176
  re-emitted, which is the spend now under way.

- [ ] **SS-F26 - a CORRECTION to `d0c7e17e6`'s account of why a setgen name collision escalates. The
  remedy I named was the wrong one, and the line I cited had already moved. Filed 2026-09-28.**

  `d0c7e17e6` said: *"The repair machinery exists and is correct: `cli.py` appends 'Previous attempt was
  rejected because its name duplicated an existing item...' to the brief - but it is wired to
  `--retry-blocked`, which selects only `blocked` subjects, and a name collision escalates terminally. So
  the re-ask is unreachable for exactly the case that needs it."*

  **Two errors, one of them mine to carry.**

  1. **The citation was stale and I did not re-verify it before quoting it.** The text is at
     `cli.py:759`, not `720`; line 720 is now an unrelated `tuning = tuning_mod.load()`. I quoted a line
     number from an earlier read of a file that had since grown, in a commit message whose whole value is
     that it points a reader at the code. A pointer that no longer points is worse than no pointer.

  2. **The mechanism I described is real but is the WRONG vehicle, and I missed a broader one that is
     the right one.** What I found (`--retry-blocked` -> `_retry_blocked_ledger` -> retry brief) is a
     *plan-time* re-brief for subjects the ledger already holds as `blocked`. But setgen has a proper
     in-graph repair mechanism, and it is not this:

     - `answers.py:71` `REPAIR_HEADER = "Your previous attempt was REJECTED for:"` - the graph APPENDS the
       rejected attempt's defects to the next ask.
     - `answers.py:74` `defects_in_prompt()` reads them back, so the escalation carries its reasons
       instead of losing them.
     - `answers.py:302` `AnswerExhausted` fires only when a subject's authored attempts run out, and it
       is a DISTINCT exception from a rejection.

     That is a general multi-attempt repair loop, and it is exactly the shape a name collision needs.

  **The actual root cause is phase ordering, not a wrong selector.** A name collision is only detectable
  against the entries ALREADY WRITTEN, so it is detected in
  `authored._reject_batch_exact_duplicates` - which runs *after* the graph has produced the whole answer
  set. By then the graph is finished and has no attempt left to give. The same ordering fact as SS-F25's
  materialgen fix, reached from the other side: there the repair had to be added after `run_batch`; here
  the repair mechanism already exists and simply is never told.

  **So the fix is to feed the collision back into the graph's own `REPAIR_HEADER` loop** - give the
  refused subject a second authored attempt carrying the specific name and its holder - **not** to rewire
  `--retry-blocked`. Mine would have worked and would have been the wrong shape: a plan-time re-brief
  discards the answer already paid for, where the in-graph loop keeps it and asks only for the name.

  **Not yet fixed.** The 6 escalated `sets/*` partitions (nuttorch, supertorch, torchwood, ultimategatling,
  ultimategatlin-minigun, ultimatepumpkin) remain empty, and this is the reason. The pattern is
  deterministic, not exhaustion: 3 torch themes each returned 'Torch of the Stump' on two separate runs
  with `attempts: 1`, so a re-ask that quotes the collision is the thing that has never happened.

- [ ] **SS-F27 - I dropped `--max-batch-chars` for the full re-emit, and the default turned 2,176 subjects
  into ONE ~900-subject batch of total silence. Filed 2026-09-28.**

  The runner's own help said it - *"Pair it with a small `--max-batch-chars` to buy a real refusal-rate
  reading for a few dozen calls instead"* - and I had set it to 600 for both pilots. Then I started the
  full run without it, so `DEFAULT_MAX_BATCH_CHARS = 30_000` applied and the child was launched with a
  single `--overwrite` carrying ~900 ids.

  The consequence is worse than slowness. materialgen's `main()` collects every answer for the plan
  BEFORE `run_batch` writes anything, so a 900-subject batch is ~88 minutes in which: stdout is **0 bytes**,
  the corpus is unchanged, the ledger does not move, and the refusal budget - which can only fire *between*
  batches - cannot fire at all. **The guard I built for exactly this failure mode was disabled by the
  invocation that needed it, and only the child cmdline and an empty log distinguished it from a stall.**

  Measured, not assumed: the parent had 2.9s of CPU and a **0s delta over 20s**; the child had a 0.09s
  delta over 25s, which is a network-bound process waiting on sequential HTTP, not a wedge - the endpoint
  answered 200 throughout. And the child had written nothing, because `run_batch` had never run.

  **Restarted with `--max-batch-chars 600`.** The ledger is now a real progress signal (one complete
  invocation per batch), and a refusal-rate reading lands every batch instead of every ~88 minutes.

  **Rate, from the longer window, because two windows disagreed and the short one flattered it:**

  | window | subjects | rate |
  |---|---|---|
  | first 4 min | 64 | 16 / min |
  | first 8.3 min (cumulative) | 75 | **~9 / min** |

  The 4-minute figure was measured on early batches and the 8-minute cumulative is the more reliable
  number, so the projection is a RANGE and not a point: **~3.5-4 hours** for the remaining ~2,077, at
  ~1.2 calls per subject, so ~2,500 calls total. A single 4-minute window is not a rate; it is a sample,
  and the two disagreeing is the reason to quote the range.

- [ ] **SS-F28 - PROVENANCE: SS-F26 and SS-F27 above are committed inside `a6efeabdd`, not under their own
  message. Filed 2026-09-28.** `git log -- tasks/seedsmith-todo.md` will show a commit titled
  *"refactor(tools): port guard-verification-boundaries to Python, and fix the shared lib it exposed"* as
  the author of two seedsmith findings. It is not. The 79 lines are mine; the commit is another stream's.

  **What happened, in order.** I appended SS-F26/F27 and ran `git add -- tasks/seedsmith-todo.md`; the fence
  correctly REFUSED (`index-extra`, ~190 of the other stream's paths staged) so nothing was committed, which
  was correct. Between that shell call and the next one, the other stream ran a broad commit that swept the
  whole index, and my staged file went with it. By the time my `git commit --only` ran, the index was empty
  and the file was already committed, so it reported `no changes added to commit` and exited 1.

  **The lesson is the one this repo already states, arriving from the direction I did not expect.** The
  hazard is normally *my* broad stage sweeping another stream's half-finished files. Here the reverse
  happened: *their* broad stage swept *my* finished work, and the only trace of the difference is a commit
  subject that describes something else. `git diff HEAD~1 HEAD --numstat` is what proved it - `79  0
  tasks/seedsmith-todo.md` - and that is the check worth doing whenever a commit's path list disagrees with
  its subject.

  **Not repaired by rewriting.** Amending or rebasing another stream's commit is exactly what the git policy
  forbids, and a rewrite here would reach 239 paths I do not own. The content is correct and committed; only
  the message that describes it is someone else's, so it is recorded here instead.

- [ ] **SS-F29 - the re-emit's ONLY yield control was unreachable at BOTH layers of the path, and the
  refusal rate is a property of the budget as much as of the model. Filed 2026-09-28, fixed in
  `17b918e07`.**

  The budget tripped on the tail: `REFUSED [batch-1] 6 of 17 subjects came back refused (352 per mille),
  broken down by gate: 11 name_gate - all of them name collisions`. That leaves an operator watching a
  variety limit with no lever. The lever existed and could not be typed.

  **Layer 1 - the runner dropped it.** `argv_for` built the child invocation without
  `--max-name-attempts`, so the runner always spent at the generator's default of 3.

  **Layer 2 - the passthrough rejected it.** `materialgen.run` has had `--max-name-attempts` AND
  `--max-consecutive-call-failures` on its own argparse, and `_cmd_items_generate_passthrough` forwarded
  neither. **The live symptom read like something else:** `REFUSED [batch-1] batch 1 of 108 exited 2 after 0
  ids were written` looks like a wedged endpoint and cost a diagnostic cycle. Exit 2 is argparse's
  "unrecognized arguments", and **0 ids written is the tell that nothing was ever spent.**

  **MEASURED, same 16 subjects, same corpus, same model, the only change the attempt budget:**

  | attempts | persisted | refused | rate | exit |
  |---|---|---|---|---|
  | 3 (default) | 11 of 17 | 6 | **352 permille** | 7 - budget tripped |
  | 10 | **13 of 16** | 3 | **187 permille** | **0 - under budget** |

  **So the refusal rate is not a property of the model alone.** At 3 attempts the tail sits over the
  200-per-mille budget and the run correctly fails closed - which looks like the corpus being exhausted
  when it is partly the budget being spent. Anyone reading an earlier 352-per-mille reading as "the model
  has no more names" would be wrong by more than a factor of two.

  **THIRD instance of this programme's most expensive CLI defect, and the pattern is worth more than
  either fix.** A named control exists and something between the operator's intent and the work drops it
  quietly: (1) `--overwrite` on `--kind set`/`charm` - accepted, planned 60 subjects, said nothing, now a
  refusal; (2) `basetypegen`'s partition-name guard reading `partition_kind_map()`, a map with no
  `"partitions"` key, instead of the registry `check` consults; (3) this. **A knob is only a control if the
  whole path carries it** - which is why the tests assert the argv the CHILD receives. A parser-level test
  would have passed while the value went nowhere, and would have been a fourth instance wearing a hat.

- [ ] **SS-F30 - TWO tests cannot pass while the rescue corpus is the spend target, and neither is a code
  defect. Filed 2026-09-28, so the next agent does not read them as one.**

  Both read the WORKING-TREE corpus, and the re-emit installs the rescue's 3,633 rows there on purpose:

  - `gk-core/tests/tools/test_reemit_colliding_item_names.py::CrossCorpusTests::test_the_real_tree_is_clean_but_the_pass_is_not_inert`
    asserts `found == []` with the message *"HEAD's materials carry no cross-corpus name collision today"*.
    Its own docstring says the 6 measured collisions **belong to the RESCUE corpus, not to HEAD**. The test
    is correct and pinned to a real property; the tree is deliberately not HEAD's corpus.
  - `gk-forge/tools/seedsmith/tests/test_materials_gen.py::EmitTests::test_derivation_matches_every_real_shipped_entry`
    pins the corpus at 31 entries. Current: 3,633.

  **The second one is a defect in the TEST, on this repo's own rule, and it is not fixed here.** A guardrail
  that validates a population count fails whenever content ships - its message even says *"a changed count
  means this cross-check is running against fewer rows than it should"*, which is written for shrinkage
  while the real cause is growth. The rule (`docs/architecture/validation-ssot.md`, restated in AGENTS.md) is
  that a guardrail validates the CONTRACT and closed enums, never a population count; 31 is a population
  reading. Filed rather than fixed because it is a separate change from the yield work and `data/` state is
  mid-spend.

  **Do not "fix" either by restoring HEAD's corpus.** The rescue base is the write target, and 546 of the
  2,176 re-emitted names now live only in it - the ledger records them as done, so a restored corpus would
  re-skip those subjects and leave their gaps open permanently. That is data loss, and the reason the
  intermediate is installed rather than kept in a scratch file.

- [ ] **SS-F31 - this machine's shell cannot launch `python` or `git` by name or by `&` path, and three of
  my probes misreported data because of it. Filed 2026-09-28. Machine-local, not a repo change.**

  - `python` on PATH resolves to `C:\\Users\\NeneScarlet\\.pyenv\\pyenv-win\\shims\\python`, whose first four
    bytes are `23 21 2F 62` = `#!/b`. It is a **bash script**, and PowerShell cannot execute it:
    `Cannot run a document in the middle of a pipeline`. Piping into it fails the same way.
  - `git` is **not on PATH at all** here, and `& 'C:\\Program Files\\Git\\cmd\\git.exe' ...` fails with the
    identical "middle of a pipeline" refusal.
  - `C:\\Users\\NeneScarlet\\miniconda3\\python.exe` works, and `Start-Process -NoNewWindow -Wait` with
    output redirected to a file works. That is the only invocation path that has been reliable all session.

  **A fourth trap, in the same family, and it is the one that actually corrupted a reading:**
  `Start-Process -ArgumentList @('-c','import json;print(len(x))')` splits on the semicolon and space, so
  python receives `-c import` and dies with `SyntaxError: expected one or more names after 'import'`. A
  `python -c` probe that "returned nothing" through this route is not evidence of anything.

  **The consequence worth keeping: three separate probes in this session reported data that was not there**,
  and in each case the shell was the cause, not the code - a log read as 0 bytes when the file was absent,
  a heredoc `python -c @'...'@` piped into a shim, and the `Start-Process` split above. The defences that
  worked, and should be the default for any agent on this box: **write the probe to a file, run it with
  `Start-Process` and an absolute interpreter, redirect to a log, and read the log.** A number that cannot
  be reproduced that way is a number that must not be quoted.

- [ ] **SS-F32 - the setgen name re-ask is DIAGNOSED and IMPLEMENTED but NOT VERIFIED, and has been
  reverted rather than shipped unproven. Filed 2026-09-28.**

  This is the honest entry for an unfinished issue, and the reason it is unfinished is the useful part.

  **The diagnosis is solid and unchanged from SS-F26.** A name collision is only detectable against the
  entries ALREADY WRITTEN, so `_reject_batch_exact_duplicates` catches it AFTER the graph has produced the
  whole answer set - leaving the graph no attempt to give. The repair mechanism already exists and is never
  told: `answers.py:71` `REPAIR_HEADER`, `defects_in_prompt()`, `AnswerExhausted`. Asking the identical
  question again is what produced 'Torch of the Stump' three times.

  **The implementation worked.** A `_name_repair_brief` helper plus a re-drive of the graph with a repaired
  brief, re-using the graph's own `REPAIR_HEADER` shape rather than a second protocol. The existing 129
  setgen tests stayed green throughout, and `max_name_attempts=0` reproduced the pre-fix behaviour.

  **It could not be PROVEN, so it was reverted.** The behavioural test needs a set answer that clears BOTH
  the closed JSON schema AND setgen's semantic gates, and no existing test drives `run_batch` end to end to
  copy a known-good answer from. Five shapes were tried, each producing a DIFFERENT rejection with nothing
  to do with the behaviour under test:

  | fixture | rejection |
  |---|---|
  | `members: []` | "0 entries is below the minimum of 2" |
  | `thresholds: [{pieces, atoms}]` | "unknown field 'atoms' - the schema is closed" |
  | `capability: {family, powerBand, params}` | "unknown field 'powerBand'" |
  | `capability: None` | schema-VALID, still refused: "missing ['capability']" |
  | capability on `armament-primary`/`core-guard` | `SetCapabilityOffRole: legal on ['girdle', 'jewel-major', ...]` |

  Every one made the GRAPH's own repair loop fire **108 times on a single subject**, so `prompts[1]` was the
  graph repairing a shape defect rather than the re-ask under test, and the assertion that the re-ask names
  the collision failed on a prompt that never should have existed.

  **Two things worth keeping from the failure.** (1) A fixture that fails validation for the WRONG reason
  tests nothing, and it fails in a way that looks exactly like the feature is broken - so the instinct to
  "add more assertions" is wrong here; the answer was to read the schema or reuse a fixture the file
  already trusts. (2) Two distinct rejection layers were in play - a closed *schema*
  (`additionalProperties: False`) and a *semantic completeness* rule - and satisfying one says nothing about
  the other. `capability: None` passing the schema and failing the run is the clean example.

  **Why reverted rather than committed.** The goal's standard is that an issue closes with a test that
  FAILS before and PASSES after. This has no such test, and a repair loop that re-asks on every name
  collision is exactly the kind of change that, if wired wrongly, spends the owner's model calls or re-rolls
  shapes. Unverified behaviour in the generator that WRITES THE CORPUS is worse than absent behaviour.

  **The next attempt should start from the diagnosis, not from the fixture.** The missing piece is a
  known-good set answer: either capture one from a live `run_batch` invocation, or add a builder that
  composes one from the brief's own closed lists (`cap_families`, `stat_ids`, the legal role set for the
  capability) instead of a hand-written literal. The five rejections above are the map of what a builder
  has to satisfy, and that map is the expensive part - it is recorded here so it is not rediscovered.

- [ ] **SS-F33 - the setgen name re-ask is FIXED and VERIFIED, and 5 of the 6 escalated partitions closed.
  The 6th is a measured variety limit, not a wiring gap. Filed 2026-09-28.**

  Closes SS-F26 (the diagnosis) and SS-F32 (the fix that could not be proven). Both were honest at the time
  and both are now resolved.

  **SS-F32's blocker was that every fixture shape I tried was a GUESS**, and each guessed shape made the
  graph's own repair loop fire 108 times on a single subject, so `prompts[1]` was the graph repairing a
  shape defect rather than the re-ask under test. The unblock was to stop guessing: capture a real answer
  from the live model through the real brief, the real schema and a real `plan_run` subject - one call,
  already validated by `live_answer_caller`'s own `_parse_and_validate`, so it is what production receives.
  Three facts guessing never produced: frames are `'plant'`, `capability.variant` is an empty STRING and not
  null, and a set wants four members.

  **The fix hands the collision to the graph's OWN `REPAIR_HEADER` loop** rather than building a second one,
  which is what SS-F26 said to do and what an earlier commit got wrong in recommending a `--retry-blocked`
  rewire (a plan-time re-brief that discards the answer already paid for). `max_name_attempts=0` reproduces
  the pre-fix path, and the test asserting that disagrees with the passing tests on purpose.

  Fail-before, same harness against HEAD:

  | | HEAD | now |
  |---|---|---|
  | times asked | 1 | 2 |
  | collision fed back | False | **True** |
  | persisted | 0 | **1** |

  **Live result: `planned 6  persisted 5  escalated 1`.** nuttorch, supertorch, torchwood,
  ultimategatminigun and ultimatepumpkin are written - **60 of the 61 empty `sets/*` partitions, up from 55**.

  **The 6th is a different failure and the distinction is the point.** `ultimategatling` still returns
  'Burst of Cherry' - the name `ultimateminigun` took in the same batch - after the full three-attempt
  re-ask. I then cleared its terminal row and ran the population again with `toGenerate=1`: it returned
  'Burst of Cherry' **a third consecutive time**. That is a measured variety limit, not an assertion: the
  two subjects share a theme family and the model maps both to one name.

  **Why that distinction is worth three calls.** A fix that recovered 5 of 6 and then hit real exhaustion
  is working. A fix that recovered 0 would ALSO have looked like variety, and this programme has repeatedly
  had to unpick exactly that confusion - so "the tail is exhausted" is a conclusion that has to be measured
  against a working control, and now it has been.

- [ ] **SS-F34 - the re-emit's effect measured MID-PASS, and the relationship is provably NOT linear.
  Filed 2026-09-28.**

  Measured on the LIVE corpus with `seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`, at 1,079 of 2,176
  subjects re-emitted (49.6%):

  | family | rescue base | now |
  |---|---|---|
  | SemanticDedup/NearDuplicate | 747 | **233** |
  | Coverage/EmptyPartition | 67 | **5** |
  | Coverage/PairwiseHole | 6 | 6 |
  | Content/FieldMissing | 5 | 5 |
  | Quality/FlavourMissing | 5 | 5 |
  | **total** | 830 | **254** |

  **The pass works, and by a lot:** 514 of the rescue's 747 duplicate names are gone at the halfway point.

  **EmptyPartition 67 -> 5 is the whole programme in one number.** 61 of those were `sets/*` and the setgen
  work closed 56 of them (55 in the first run, 5 more via the name re-ask, minus the one that remains
  `ultimategatling`). The 4 that are left are the 3 `display-templates/*` and the 1 `attributes` - exactly the
  two kinds no adapter generates.

  **The important part is the projection that CANNOT be right.** Carried linearly, 747 -> 233 at 49.6% of
  the subjects predicts **-290** remaining at 2,176. A negative count of duplicates is not a forecast, it is
  proof that the relationship is **sub-linear**: the re-emit clears the easy collisions first and the
  remainder concentrates in a hard tail where the model keeps reusing a name.

  **That is the same shape as SS-F21's geometric decay, now measured on real output rather than assumed**,
  and it has a direct consequence for finishing: a second pass is not 2,176 subjects again. Once this pass
  ends, the plan re-derives from the live corpus, so the next pass plans only the subjects whose names STILL
  collide - a few hundred, not two thousand. Two or three short passes should converge well before the
  objective's "at or below 4", and each is bounded by the same refusal budget.

  **Recorded because "how much is left" and "how much more will it cost" are different questions**, and the
  naive linear reading of this table would answer the second one wrongly by a factor of several.

## SS-F35 — the re-emit CONVERGED, and the tool said so before I did

The final full pass ran 50 batches, **every one exit 0**, with zero batch deaths. The `os.replace`
retry plus the shared `atomic_replace` helper did their job: previous attempts died at batch 4, 10 and 29.

| reading | value | how |
|---|---|---|
| subjects done | **2,133 of 2,176** (98.0%) | `materials-gen.ledger.json` `done` keys |
| corpus rows | 3,633 | working tree |
| within-materials gate | 3,580 kept / 53 refused (44 reuse, 9 near-dup) | the shipped gate, replayed in corpus order |
| cross-corpus collisions | **0** | the runner's own `cross_corpus_collisions` |
| names differing from the rescue ref | 2,123 (584 per mille) | per-id diff vs the ref blob |
| `check` gaps | **55** | `seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` |

The 53 remainder is a **model limit, not a wiring gap**, and the tool's own regime sentence is the evidence:
*"11 of 20 subjects came back refused/blocked/missing (550 per mille) ... this is a variety limit, and more
spending buys more of the same name."* The attempts lever is spent — 0 / 3 / 10 / 20 measured at 437 / 125 /
200 per mille on the tail before it sat at 550 — so the plan re-deriving 66 and refusing to finish is the
correct outcome, not a failure to push through.

The sub-linear shape predicted at SS-F34 held: 747 -> 233 at halfway -> **34** `SemanticDedup/NearDuplicate`
at the end. A linear reading had predicted a negative count, which is how the prediction was falsified and
the relationship established as sub-linear.

## SS-F36 — the materials name gate was structurally blind to the other corpora (WIRING, not the model)

Four entries still held a name verbatim that a `charm.*` or a `droptable.*` also holds, and
`CrossCorpusTests.test_the_real_tree_is_clean_but_the_pass_is_not_inert` asserts the real tree carries none.

**The measurement that identifies the cause rather than guessing at it:** 2,123 of 3,633 names DID change in
the same run, and all four of these changed too — they landed on names something else already held. So the
model was varying names fine. It was never told those four were taken, because `materialgen` compared an
authored name only against the MATERIALS corpus **and built the re-ask brief from that same blind view** —
so a re-ask returned the same name and re-persisted it. A targeted pass over exactly those four reported
`PERSISTED 3 refused 1` and left all four byte-identical.

This is why `tools/seedsmith/adapters/items/materialgen/run.py` now runs the same cross-corpus check the
runner runs, with the collector and the normalisation in one place
(`gk-forge/tools/seedsmith/seedsmith/pipeline/cross_corpus_names.py`). Two implementations is how each side stayed
correct about its own question.

Three further defects the fix exposed, each of which had been hiding behind the first:

- **`newline="\n"` missing from three writers.** 61 of 945 `sets/*` partitions carried CRLF in the working
  tree while their committed blobs were LF, and because `.gitattributes` says `eol=lf`, **git normalises them
  away and `git status` reported them CLEAN**. Only a test reading raw bytes could see it. `species_repair.py`
  and `name_repair.py` already passed the argument; the writers lacking it were the defect.
- **The items root was derived as `parent.parent`,** which is right only for the shipped layout. The sibling
  suite passes a flat `tmp/materials.json`, so the walk became `rglob` over the system temp tree: 25 tests
  passed in 3s and the 26th was still running after 15 minutes.
- **A refusal that could not name itself.** The runner tallied defects to a count, so a batch refusing 1 of 4
  reported `1 name_gate` — while both halves of the name gate land in that one bucket and need opposite
  responses. I spent a diagnostic cycle assuming the wrong half; the string was in the variable throughout.
  `classify_defect` also read a copied prefix literal, so the new defect shape was filed as `other` and the
  regime sentence described a name-variety problem as unfixable-by-spending. It now reads the generator's own
  constant.

## SS-F37 — a guard whose result depended on whether a virtualenv happened to exist

`test_every_python_file_under_the_tool_is_inside_a_scanned_scope` reported **1,975 unscanned files**, every
one under a `.venv-verify/Lib/site-packages/...` that the suite itself creates under `gk-forge/tools/seedsmith/`. So it
was green in CI and red on a machine, or the reverse, for reasons having nothing to do with the source. A
build artefact is now excluded as a PATH COMPONENT, not a substring — pinned by
`test_the_artefact_exclusion_cannot_hide_a_real_source_file`, because "skip anything matching the name" is
how a real unscanned module disappears behind a convenient substring.

## SS-F38 — the suite baseline, measured rather than recalled

Whole-suite runs in a scratch HEAD worktree against the current tree, diffed as sets:

- **19 failures in BOTH** trees — pre-existing, including
  `test_items_adapter::test_authored_item_names_are_unique_across_kinds`, which the objective flagged as
  failing on a clean HEAD and which is confirmed here.
- **1 FIXED** by this change: `test_preflight::test_hash_matches_the_real_committed_dump`.
- **2 were this change's own regressions** (the CRLF writers and the venv inventory), both fixed above.

The diff is what makes "pre-existing" a measurement. Reading a red suite and calling it pre-existing is the
exact guess this replaces.
## SS-F39 — the rescue ref is closed, on the owner's word

`rescue/corpus-bcu211-itemseedgen-run` deleted after the regenerated corpus landed on
`features/mega-merge`, on explicit owner authorisation. Recorded here because the two gates ran as
SEPARATE steps before the destructive call, which is the only order in which either is worth anything:

1. **The merge gate.** Branch `features/mega-merge`, tip `3b72e5dd1` = HEAD, and the corpus blob ON that
   branch read 3,633 rows / 3,589 distinct names. There was nothing left to merge — this session committed
   directly on the branch rather than in a worktree — and the gate says so rather than a merge being
   performed to satisfy the shape of the request.
2. **The evidence gate.** CB41, CB42 and CB43 are present in `tasks/backlog-clean-up-todo.md`, so the unique
   findings the ref held are committed before the only ref reaching them goes.

`git branch -D` reported `Deleted branch rescue/corpus-bcu211-itemseedgen-run (was 6fc3d2b21)`, and the
closure was read back rather than taken from the exit code: `rev-parse --verify` no longer resolves the ref
and it is absent from `git branch --all`.

**What closing actually costs, stated plainly rather than glossed:** `6fc3d2b21` was in exactly one ref, and
it is now reachable only through the reflog until it is pruned — `git cat-file -e` still resolves it today.
No tag was created, because none was asked for; if that commit is ever wanted permanently, a tag at
`6fc3d2b21` is the one line that makes it durable, and it should be done before any `gc --prune`.