# Implementation plan: narrative-seed

**Status: plan, written 2026-09-20. Awaiting owner approval. No task started.**
Task list: [narrative-seed-todo.md](narrative-seed-todo.md). Program id: `narrative-seed`.
Written under session `narrative-plan-20260920` (docs only). The implementing session records its own
boundary at NS0.

**Inputs, read in full this session and not reopened here:**
[narrative-seed-map.md](../docs/architecture/narrative-seed-map.md) (approved 2026-09-19, its `:3`; module
table §4, build order §6, ownership §7), the 23 module specs under
[docs/architecture/narrative-seed/](../docs/architecture/narrative-seed/) including every "Standards audit
(2026-09-19)" and "Cross-lane alignment (2026-09-20)" section, `narrative-seed-ideal.md` §8, §10 (R6, R7)
and §11, `npc-story-events-ideal.md` §10 (R1–R23), `npc-story-events-map.md` (modules, build order, gates),
[ip-censor-plan.md](ip-censor-plan.md), [identity-rename-plan.md](identity-rename-plan.md),
`docs/research/ai-native-generation/README.md` (§2–§10), the `planning-and-task-breakdown` and
`seedsmith-design` skills, `.claude/commands/plan.md`, `docs/contributing/agent-git.md`,
`docs/contributing/session-boundary.md`, `docs/contributing/testing-standard.md` and AGENTS.md's
verification boundary section. Where code disagrees with a spec, §5 names the disagreement and the task
that absorbs it.

---

## 1. What this program builds, in one paragraph

A new seedsmith adapter, `narrative`, that generates storylets with player choices, characters with
voices and lines, arcs, spine chapters and narrative quest anchors offline, under a closed contract in
which the model writes identity and text and never a number; plus the Wave-0 repair of the existing Delve
event generator (model literals, script check, motif glosses, planned climate, no forged chain ids, text
keys) and the regeneration of the 54 committed legacy Delve events clean and keyed. The game runtime
resolves every seed without calling a model; that runtime is `npc-story-events`', not this program's.

## 2. Principles every task obeys (restated, because a pointer does not survive a long session)

1. **The model writes identity; deterministic code writes magnitude.** No numeric field in any call
   schema; no digit in the literal text of any prose field. Enforced by the schema audit and the no-digit
   validator, never by review.
2. **Seed, then concrete, then per-player.** No task designs a roll; outcomes are `{family, powerBand}`
   and bands, resolved at runtime through `Instantiator.TryInstantiate`.
3. **No model literal** (R6). Every call resolves through `.env` `SEEDSMITH_LLM_MODEL` over
   `seedsmith.toml` over `LlmCallerConfig`'s default. No adapter, helper or CLI flag carries a model id.
4. **Generated data is never hand-edited.** Every change to a generated tree (the legacy Delve events,
   the gloss rows, every narrative seed) comes from a generator run and its committer. Registries under
   `_registry/` and `_exemplars/` are authored and reviewed.
5. **A test asserts the contract, never a population.** Corpus sizes, per-cell counts, accepted and
   rejected counts, call totals and generated text are readings, printed by `report` or a dry run. A
   closed vocabulary's member list (choice kinds, `ChoiceType`, sense, script classes, the three lead
   tokens, the seven chapter slots) is a declaration and is pinned with its reason.
6. **Tests never call a model.** Every test stubs the transport so a real call raises.
7. **Every model run has a dry run that prints its call count first, a small first batch, and a human
   review sample before it scales** (ai-native README §9; the owner's phased rollout,
   `tasks/item-todo.md:9590-9591`).
8. **Every RPG feature lives in the RPG layer; one generator per content kind; SOLID.** The Delve's event
   kind moves into the `narrative` adapter at the cutover; no second storylet generator ever exists
   beside it.

## 3. Architecture decisions

### D1 — Wave order is the map's; model-free first

Waves 0–4 spend zero tokens except Wave 0's two bounded runs (`gloss-fill` and the legacy regeneration),
each behind its own dry run (map §6). Wave 5 is the first narrative spend and is gated on the planner's
printed call budget (NSG2). Wave 6 switches the Delve's corpus in the same change as the runtime loader (NSG3).

### D2 — One task = one commit

Each task is one module slice: code, tests, evidence (the command output quoted in the commit body) and
its status line in the todo, committed together with explicit paths, no push, no amend. A task that
would exceed about five files is split along the spec's own seams (contract per seed kind, dungeon repair
per defect, pipelines per stage). The two exceptions are stated where they occur: NS19 (a regenerated
tree is one generator run) and NS69 (the cutover must move every reader in one change, map §6).

### D3 — Verification: what `verify-change.ps1` can select today

`gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/dungeon/**` and `gk-data/packs/fusion/data/seed/narrative/**` have no verification boundary:
`verify-change.ps1` throws `VERIFICATION BOUNDARY MISSING` for them (`scripts/verify-change.ps1:118`).
The registry is at `schemaVersion` 2 and has no pytest runner; the python lane is
`test-verification-boundary`'s TVB3.1–TVB3.3 (`tasks/test-verification-boundary-todo.md:182`) and the
`gk-data/packs/fusion/data/seed/**` mapping is TVB4.7 (`:273`), both built by the active worktree lane D2
(`tasks/sessions/summoner-convergence-lane-d2-20260919.json`).

Rules every task follows:

1. Pass **only mapped paths** to `.\scripts\verify-change.ps1 -Paths … -Session <sid>`: today that is
   `gk-core/scripts/enforcement-registry.v1.json` (boundary `enforcement-registry`), `docs/**` (including
   `decisions.md`) and `tasks/**`. For every seedsmith path run the named focused pytest command:
   `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/<file> -q` from the repo
   root. Seedsmith's whole suite runs in CI (`.github/workflows/ci.yml:337`).
2. **NS1 and NS2 add the narrative boundary rows** as soon as TVB3.3 and TVB4.7 land (owner instruction
   for this plan: mapping tasks belong in the plan). From then on every task also passes its seedsmith
   and `gk-data/packs/fusion/data/seed/narrative/**` paths to `verify-change.ps1`. Until then the focused pytest command is
   the verification, and each task's ledger line names its unmapped paths. Never compensate with a broad
   suite.
3. The whole seedsmith suite (`python -m pytest gk-forge/tools/seedsmith/tests -q`) runs only where a task crosses
   adapters (NS6, the model-literal guard) and at each checkpoint. The whole C# suite runs once, at NS69,
   because the cutover crosses `tools/`, `data/` and the runtime programs' C# (AGENTS.md's three points).
4. **Plan audit 2026-09-20 — a guard script this program writes or edits gets its own boundary row.**
   `scripts/guard-*.ps1` has no glob row; each guard that has one is mapped by name (`overflow-audit`,
   `magic-number-audit`, `battle-responsibility-guard`). Measured this session:
   `verify-change.ps1 -PlanOnly -AllowUnscoped -Paths gk-core/scripts/guard-generated-seed.py` throws
   `VERIFICATION BOUNDARY MISSING`. AGENTS.md calls an unmapped production path a **boundary defect to
   fix**, never a reason to skip or widen, so NS6b adds a `guard-narrative-seed` row (paths:
   `scripts/guard-narrative-seed.ps1`; project `guard`; `level: module`; no `verificationId` until a test
   carrying that trait exists) and NS34 adds the missing `guard-generated-seed` row in the same shape.
   The sibling program already does this for `gk-core/scripts/guard-narrative.py` and
   `scripts/narrative-readings.ps1` (its plan §4 D2) — the two programs now match.
   **A boundary row may only carry `verificationId` once a `[Trait("VerificationId", "<id>")]` test
   exists in that project**: `guard-verification-boundaries.py:83-91` greps the project directory and
   fails the row otherwise. It does **not** check that a `paths` pattern exists on disk, so a glob over a
   directory this program has not created yet is legal. `notify-core-domain` is the precedent for a
   `level: module` row with no `verificationId`.

Map §7 names `test-verification-boundary` as the owner of the seedsmith mapping. NS1/NS2 add only the
narrative rows, on top of the lane that TVB builds, and NS70 records that reconciliation in the map.

### D4 — Enforcement-registry rows land with the test that makes them true

`gk-core/scripts/enforcement-registry.v1.json` has a meta-test (`gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs`):
every invariant carries guard ids **xor** an `unguardableReason` (R6, `:177`), every catalogued guard's
script exists (R1, `:53`), and every catalogued guard is named by an invariant (R8, `:199`). An
invariant's `guards` are ids from the registry's `guards` catalog, which holds guard **scripts**
(`scripts/guard-*.ps1`); a pytest file has no catalog id.

**Alignment 2026-09-20.** The sibling program answered this: `npc-story-events` lands its rows through
**one new catalogued guard script**, so this program does the same. NS6b creates
`scripts/guard-narrative-seed.ps1`, catalogues it as guard id `narrative-seed` (tier `ci`, status
`gating`, so `run-guards.ps1` runs it in CI), and runs the pytest checks that actually enforce each row.
Its check table is one committed line per row — the row's pytest node ids — and each later row task
appends its own line in the same commit as its test. So an invariant is guarded, not excused.

**Two scripts, one per program, not one shared script with a scope flag.** They run different runners
over different trees: this one runs `python -m pytest` over `gk-forge/tools/seedsmith/tests/**`, the runtime one
runs its own checks over C# and the runtime corpus. A shared script would make every row of either
program edit the other program's file while both programs are active (plan §8), would need a scope
vocabulary no other guard has, and would fail as one unit when only one side is red. Two small scripts,
two catalog ids, two invariant sets is the smaller correct shape; `guard-narrative.py` and
`guard-narrative-seed.ps1` share no code and never run each other.

- `narrative-no-hand-edit-generated` keeps the existing catalog guard `generated-seed` (NS34): the guard
  that makes it true already exists, and pointing it at a second script would double-run nothing.
- `narrative-voice-quality` keeps a genuine `unguardableReason` (NS45): whether a line is in character is
  open-loop, and no scan can pass it.
- Each row lands in the same commit as the test **and** the guard check line that makes the invariant true
  on the real tree, which is not always the spec's named test file (§5 items 5–7).
- **Plan audit 2026-09-20 — the guard cannot pass vacuously for a row that forgot its check line.** The
  enforcement meta-test proves only R1 (the script exists), R6 (guards xor reason) and R8 (a catalogued
  guard is named); none of them looks inside the script. So `guard-narrative-seed.ps1` **derives** the row
  set it must cover by reading `gk-core/scripts/enforcement-registry.v1.json` for every invariant whose `guards`
  contains `narrative-seed`, compares that set with its own committed check table, and exits non-zero
  naming any row with no check line (and any check line naming no row). It also exits non-zero when a
  check selects **zero** pytest node ids. Without that, adding `guards: ["narrative-seed"]` to a row and
  forgetting its check line is a green build that enforces nothing.

| Row id | Source | Enforced by | Task |
|---|---|---|---|
| `seedsmith-no-model-literal` | map §2 principle 13 (R6) | guard `narrative-seed` → `gk-forge/tools/seedsmith/tests/test_no_model_literal.py` (new) | NS6b |
| `narrative-no-raw-motif-in-brief` | map §2, §3.4 | guard `narrative-seed` → `test_briefkit_gloss.py` (new) + `test_dungeon_event_briefs.py` `brief_contains_glosses_not_raw_motifs` | NS9 |
| `legacy-delve-event-keyed-text` | map §6 (Owner ruling 2026-09-19 round 4) | guard `narrative-seed` → `gk-forge/tools/seedsmith/tests/test_dungeon_commit.py` (new), tree test over `gk-data/packs/fusion/data/seed/dungeon/events/` | NS19 |
| `narrative-call-schema-blocked-and-closed` | `spec-narrative-contract.md` §9–§10 | guard `narrative-seed` → `test_narrative_contract.py` (new) | NS31 |
| `narrative-no-digit-in-prose` | map §2 principle 2 | guard `narrative-seed` → `test_narrative_contract.py` (new) | NS33 |
| `narrative-no-hand-edit-generated` | map §2 principle 8 | catalog guard `generated-seed` | NS34 |
| `narrative-r13-counter-doctrine` | R13; map §8 item 11 | guard `narrative-seed` → `test_narrative_character_vocab.py` + `test_narrative_validators_structure.py` (new) | NS40 |
| `narrative-no-literal-name` | R8–R11; map §2 principle 14 | guard `narrative-seed` → `test_narrative_validators_text.py` (new) | NS41 |
| `narrative-open-loop-never-gates` | map §2 principle 7 | guard `narrative-seed` → `test_narrative_metrics.py` (new) | NS43 |
| `narrative-voice-quality` | map §2 principle 7 | `unguardableReason`: *whether a line is in character is open-loop; review verdicts record it and no scan can pass it* | NS45 |

**One CI ordering consequence.** `run-guards.ps1 -Tier ci` runs at `.github/workflows/ci.yml:241`, before
the seedsmith lockfile install at `:295`, so a guard that shells out to pytest would fail there for want
of pytest. NS6b therefore moves the install step above the guards step (one step, clean-or-skip against
the CI-owning lanes) and the guard fails loudly, naming the missing interpreter, rather than passing
vacuously when it cannot run its checks.

`quest-vocab` adds no row: its lawn-only refusal mirrors the runtime's `ns-quest-no-lawn-only-objective`
(`spec-quest-vocab.md` design-gate checklist).

### D5 — `decisions.md` rows land once, in the change that makes them true

| Row (map §11) | Task |
|---|---|
| 2 No hard-coded model in seedsmith | NS6 |
| 6 Generated antagonist content obeys counter-doctrine | NS23 |
| 3 Structured story text | NS25 |
| Narrative names are tokens (shared with `npc-story-events` NS5; one row, not two) | NS26 |
| 4 The spine is a generated seed kind; generated scenes are data | NS28 (§5 item 3) |
| 5 Narrative seed identity over regeneration | NS36 |
| 1 Narrative seed adapter and the storylet contract (grid change) | NS49 |

`decisions.md` is shared with two direct sessions (§8); each of these tasks applies the clean-or-skip rule.

### D6 — Model runs: dry run, first batch, review, then scale

Every run task states its call budget from the call-shape table (`spec-narrative-planner.md` §7; README
§9), prints it with `--dry-run` before anything is spent, proves constrained decoding with
`narrative preflight` (one real call), runs a first batch small enough for one review sitting, records
review verdicts append-only, and commits only accepted output. Scaling a pipeline past its first batch is
gate NSG4. The model is whatever `.env` resolves; no task names one. The budget figures in the todo are
formulas with illustrations; the dry run's printed figure is the number the owner approves.

These runs are seedsmith generator runs on the owner's configured endpoint, not agent workers. If the
implementation itself is delegated to agent runtimes (Claude Code subagents, cmdc, pi), the owner charter
comes first (CLAUDE.md "Multi-agent runs start with the owner's charter"); this plan starts no worker.

### D6b — Agent types (Plan audit 2026-09-20; this section was missing)

Execution by any agent needs the owner charter first — runtimes, exact models, budget, stop rule
(CLAUDE.md *Multi-agent runs start with the owner's charter*; the `project-manager` skill). Within an
approved charter, and matching the sibling plan's §5:

| Agent type | Tasks | Why |
|---|---|---|
| `implementer-hard` | NS18, NS19 (a model run that **overwrites a committed generated tree** other programs and players read), NS69 (the cutover: a cross-program delete plus the runtime loader switch in one change), NS6b (it re-orders a CI job step, so a wrong order turns every guard red for the whole repo) | A wrong ordering corrupts committed content or CI for other lanes |
| `refactorer` | none — this program adds an adapter and never re-seams an existing one | — |
| `implementer` | every other build task, including every Wave 1–4 registry, validator, metric and planner task | — |
| `test-engineer` or the implementing session | none: this program has no live probe (generation is offline; the runtime probes are `npc-story-events`' NR-LP1/NR-LP2) | — |
| `locator` | any file search inside a task, instead of spending an implementer's context | — |

**Goldens are measured, never assumed.** No task here moves a C# golden; NS69 is the one change that
could, and it runs the whole C# suite (AGENTS.md point 2) and lists any moved hash in its commit body
rather than asserting none moved.

### D7 — Cross-program seams are named files, never edits across the fence

This program edits no runtime file (`gk-core/src/FusionRpg.Core/Delve/**`, `DelveWildEndpoints.cs`, the loader,
`EventRow`, the preflight) and no shipped surface (identity-rename's). It publishes registries and
corpora the runtime reads. The one change that edits another program's adapter kind is the NS69 cutover,
landed together with its owners' edits.

---

## 4. Phases and task index

Full detail, acceptance criteria, verification and budgets: [narrative-seed-todo.md](narrative-seed-todo.md).

**Phase 0 — Boundary and verification**
- NS0 Session record
- NS1 Verification boundary: the narrative seedsmith area (after TVB3.3)
- NS2 Verification boundary: `gk-data/packs/fusion/data/seed/narrative/**` and the legacy events tree (after TVB4.7)

**Phase 1 — Wave 0: repair and shared foundations** (two bounded model runs)
- NS3–NS6 `model-config-resolve` (transport, class A, class B, class C + the model-literal test)
- NS6b The program's catalogued guard script `scripts/guard-narrative-seed.ps1` + its first row
  (Alignment 2026-09-20)
- NS7 `script-check`
- NS8 `gloss-registry`
- NS9–NS13 `dungeon-generator-repair` code (glossed briefs, retry-loop script check and prompt version,
  planned climate and no forged chains, committer and keys, regeneration driver)
- NS14–NS15 `gloss-fill` code (pipeline; commit, preflight and CLI)
- NS16–NS17 runs: gloss batch 1, then the full gloss pass (NSG4)
- NS18–NS19 runs: legacy regeneration batch 1 (NSG1), then the remaining events (NSG4)
- **Checkpoint 0**

**Phase 2 — Wave 1: registries** (no model)
- NS20–NS22 `storylet-vocab`; NS23–NS24 `character-vocab`; NS25 `token-grammar`; NS26 `names-registry`;
  NS27 `arc-shapes`; NS28 spine frame; NS29 the seven chapters' authored scene structure
- **Checkpoint 1** (hand-off: `npc-story-events` `narrative-vocabulary` and `narrative-text` may build)

**Phase 3 — Wave 2: contract and emit** (no model)
- NS30–NS34 `narrative-contract`; NS35–NS36 `narrative-emit`; NS37–NS38 `quest-vocab`
- **Checkpoint 2** (hand-off: `storylet-contract` fixture corpus, `quest-sources` anchors)

**Phase 4 — Wave 3: validators, metrics, review** (no model)
- NS39–NS41 `narrative-validators`; NS42–NS43 `narrative-metrics`; NS44–NS45 `review-render`
- **Checkpoint 3**

**Phase 5 — Wave 4: grounding and planning** (no model)
- NS46 `lore-packet`; NS47–NS49 `narrative-planner`
- **Checkpoint 4** (the dry run prints the Wave-5 budget; gate NSG2)

**Phase 6 — Wave 5: model pipelines**
- Code: NS50–NS51 `storylet-pipeline`; NS52–NS54 `character-pipeline`; NS55 quest-text call;
  NS56 `arc-pipeline`; NS57 `spine-pipeline`
- First batches: NS58 storylets, NS59 characters, NS60 one arc, NS61 spine chapter 1
- Scale (NSG4): NS62 storylets, NS63 characters, NS64 arcs, NS65 spine
- **Checkpoint 5**

**Phase 7 — Wave 6: the Delve corpus**
- NS66 `delve-event-regen` code; NS67 Delve batch 1; NS68 remaining Delve cells (NSG4)
- NS69 Cutover (NSG3), with `npc-story-events`' loader and `party-dungeon`'s room pools
- NS70 Program doc propagation
- **Final checkpoint**

72 tasks (NS0–NS70 plus NS6b), 7 checkpoints, 4 gates.

**Parallel work.** After NS8, the Wave-1 registries (NS20–NS29) touch only `gk-data/packs/fusion/data/seed/narrative/_registry/**`,
`_exemplars/**` and new reader files, so they can run beside the Wave-0 dungeon repair (NS9–NS13), which
touches only `adapters/dungeon/**` and `workflow/validators/motif.py`. `gk-forge/tools/seedsmith/seedsmith/report/cli.py`
is edited by NS13, NS15, NS31, NS36, NS41, NS45, NS46, NS49 and every pipeline task, so those tasks are
serial with respect to each other. Model runs wait on the endpoint only; code tasks never wait on a run
except where the todo says so.

---

## 5. Findings from verification that change a task

| # | Finding | Evidence | Task |
|---|---|---|---|
| 1 | Registry invariants name guard-catalog ids (scripts), not test files; the specs' proposed rows named pytest files as guards. **Alignment 2026-09-20:** answered by the sibling program — one new catalogued guard script per program runs the enforcing tests, so no row is excused | `EnforcementRegistryGuardTests.cs` R1 (`:53`), R6 (`:177`), R8 (`:199`); `.github/workflows/ci.yml:241` vs `:295` | D4, NS6b |
| 2 | `narrative-contract` §10 rule 7 needs `text.lengthBounds` for each text field's `maxLength`, but `narrative-validators` (Wave 3) was to add that block | `spec-narrative-contract.md` §10 rule 7; `spec-narrative-validators.md` §5 | NS31 adds the block; NS41 reads it |
| 3 | Two specs append the same `decisions.md` row (map §11 item 4): `spec-arc-shapes.md` §7 and `spec-spine-pipeline.md` §4 | both specs | NS28 lands it; NS57 checks it exists |
| 4 | The names row is shared with `npc-story-events` NS5 ("one row, not two") | `spec-names-registry.md` §5 | NS26 appends only if absent |
| 5 | `narrative-no-raw-motif-in-brief` is not true when the lookup lands (NS8), because the dungeon brief still injects raw motifs until NS9 | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:324` | row in NS9 |
| 6 | `legacy-delve-event-keyed-text` is true of the committed tree only after the last regeneration commit | `spec-dungeon-generator-repair.md` §8–§9 | row in NS19 with a tree test |
| 7 | `narrative-r13-counter-doctrine` names two tests; the second (`enemy-consequence`) lands in Wave 3 | map audit proposed rows | row in NS40 |
| 8 | `call_model` itself defaults to `DEFAULT_CONFIG` | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:298` | NS3 |
| 9 | `identity-rename` T1 may land `names.en.v1.json` first, in a minimal shape without `registryVersion` | `tasks/identity-rename-plan.md` D1 (`:94-126`) | NS26 adopts the file; adds `registryVersion` and proves the C# parser still loads |
| 10 | `seedsmith.briefkit.avoid_list` does not exist until `ip-censor` T14 (`tasks/ip-censor-todo.md:328`) | `gk-forge/tools/seedsmith/seedsmith/briefkit/` holds `__init__.py` and `render.py` only | NS46 default: absent helper = empty `avoid`, recorded in provenance; NS24's exemplar IP test skips |
| 11 | The gloss rows are generated but live under `_registry/`, which the narrative guard row treats as a source path; the guard also reads only a top-level `_meta` | `gk-core/scripts/guard-generated-seed.py:117-124` | reported in NS34; the no-hand-edit protection for glosses is NS15's commit-only-accepted test |
| 12 | Quest anchors are not planned work items, and the `quest-text` call is in no pipeline's work order | `spec-narrative-planner.md` audit #4; `spec-quest-vocab.md` §4 | NS48, NS55 |
| 13 | Each of the seven spine chapters' scenes, beats and cast is authored structure with no task | `spec-arc-shapes.md` audit #3 | NS29 |
| 14 | `gk-data/packs/fusion/data/seed/narrative/` does not exist | directory listing, 2026-09-20 | NS8 creates it |
| 15 | `test_actions_description_completeness` fails on a clean HEAD (AGENTS.md "Seedsmith") | AGENTS.md | NS4 records it as pre-existing before editing the actions adapters |
| 16 | The narrative budget file is created by `gloss-registry` and grown by nine later modules | module specs' "Tunables" sections | every budget edit appends its own block; a changed value publishes `budget.v{n+1}.json` |

---

## 6. Coordination with other programs

| Program | Relationship | Contract |
|---|---|---|
| `npc-story-events` (runtime consumer) | Reads this program's registries and corpora. Its `narrative-vocabulary` (wave 0) needs NS20–NS24 and NS27; `narrative-text` needs NS25–NS26; `delve-live-rooms` needs the keyed legacy tree (NS19); `storylet-contract` needs NS30–NS33 for its fixture corpus; `quest-sources` needs NS37–NS38; `spine-progress` reads the frame's fragments (NS28); `scene-script-loader` reads the spine chapter schema (NS32). Its map gate G2 — the `npc-story-events` map’s, not this plan’s — (dangling `chainRef`) lists the four regenerated legacy `story` events as named known defects until NS69 | Hand-offs at Checkpoints 0–2; the cutover NS69 lands with `storylet-contract`'s loader switch. **Plan audit 2026-09-20:** that program also **writes one file into this tree** — `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (its NR1.3 creates it empty, its NR6.1 authors the rows), which its own plan §2 carves out of its out-of-scope list. It is an authored registry, so NS34's `generated-seed` row treats it as a source and never as output; no narrative-seed task edits it. Its NR0.2 also maps `gk-data/packs/fusion/data/seed/narrative/_registry/**` in the `core-narrative` boundary row, so NS2's `gk-data/packs/fusion/data/seed/narrative/**` row must be **less** specific than that one (most-specific-wins) and must not repeat its pattern verbatim, which `guard-verification-boundaries.py:74-77` refuses as an *ambiguous owner pattern* |
| `party-dungeon` | Owns the dungeon adapter's other six kinds and the room archetype contract | NS9–NS13 edit only the event kind's code; NS69 retires the event kind in the same change as its room-pool change |
| `ip-censor` ([plan](ip-censor-plan.md)) | Owns the avoid-list helper (its T14) and the release gate; scans `names.en.v1.json`, the gloss registry and `gk-data/packs/fusion/data/seed/narrative/**` | NS46 and NS24 read `load_avoid_terms`/`render_avoid_line` and never keep a list; absent helper or registry is never a blocker (IC-3). **Plan audit 2026-09-20 — two uncoordinated file collisions with this program, both now clean-or-skip:** (1) its **T16** adds `--node` to `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, the file §4's *Parallel work* paragraph serialises **only against this program's own tasks**; every task here that touches `report/cli.py` (NS13, NS15, NS31, NS36, NS41, NS45, NS46, NS49 and every pipeline task) runs `git status --porcelain -- gk-forge/tools/seedsmith/seedsmith/report/cli.py` first and skips on a dirty file, and each edit is a new verb registration, so different regions merge. (2) its **T1** and **T11** add steps to `.github/workflows/ci.yml`; **NS6b moves a step in that file**, so NS6b's clean-or-skip check names `ip-censor` explicitly, and whichever lands second re-reads the step order and re-asserts that the seedsmith install precedes both the guards step and ip-censor's scan step |
| `identity-rename` ([plan](identity-rename-plan.md)) | Consumes `names.en.v1.json`; may land it first (its D1 default) | Whichever lands second adopts the other's file; one file (NS26) |
| `test-verification-boundary` (lane D2, worktree) | Builds the python lane TVB3.1–TVB3.3 and the `gk-data/packs/fusion/data/seed/**` mapping TVB4.7 | NS1, NS2 wait on them; nothing else does |
| `creature-seed` | Owns the motif list and species anchors this program reads | Read only; species English display names are out of scope (map §7) |
| `story-scene` | `gk-core/data/tuning/story-scene-ui.v1.json:13` bounds beats per scene | NS28 reads it, never copies it |
| `keepverse-split` (direct) | Claims `gk-forge/tools/seedsmith/seedsmith/workspace_roots.py`, `decisions.md` and the boundary registry | This program reads `workspace_roots.py`, never edits it; if its migration gate opens, unfinished tasks retarget moved paths |

---

## 7. Gates

Only irreversible actions are gated. Every other owner input (review verdicts, anchor picks, chapter
structure review) is an ordinary review step with a stated default in its task.

| Gate | Blocks | Why irreversible | Resolver | Default if unanswered |
|---|---|---|---|---|
| **NSG1** First commit of regenerated legacy Delve events over the committed tree | NS18's commit step (and so NS19) | It overwrites a committed generated tree read by `party-dungeon` and, from `delve-live-rooms`, by players; the model output cannot be reproduced, and once `narrative-text`'s codegen has emitted catalog ids from the new keys a revert orphans them | Owner, from NS18's review sample | The reviewed run stays uncommitted in `data/seed/dungeon/_runs/`; NS18 is recorded "awaiting NSG1"; every task outside NS19 continues (no Wave 1–5 task reads the regenerated tree) |
| **NSG2** Start Wave-5 model spend | NS58–NS65 (runs only) | Spent calls cannot be unspent | Owner, from Checkpoint 4's printed dry run | Pipeline code tasks NS50–NS57 proceed against stubs; no run starts |
| **NSG3** Delve cutover: delete `gk-data/packs/fusion/data/seed/dungeon/events/**` and retire the `dungeon-event` kind | NS69 | Saves may reference legacy event ids once `delve-live-rooms` is live; the runtime must switch in the same change | Owner, with `npc-story-events` (`storylet-contract`) and `party-dungeon` reviewers | The Delve storylets stay committed in the narrative tree, unread; the legacy tree and kind remain; nothing is deleted |
| **NSG4** Scale a pipeline from its first batch to the full run | NS17, NS19, NS62–NS65, NS68 | Spent calls; the owner's standing rule is small batch, then playtest, before the full run (`tasks/item-todo.md:9590-9591`) | Owner, after reviewing the batch (and playing it where a runtime host exists) | No full run; the first batch stays committed; other lanes continue |

---

## 8. Shared files — active sessions and the clean-or-skip rule

Read from `tasks/sessions/*.json` on 2026-09-20, **active records only**. A worktree lane meets this
program only at its merge; a direct session shares this working tree.

| File(s) this plan edits | Also claimed by | Mode |
|---|---|---|
| `gk-forge/tools/seedsmith/**` | `summoner-convergence-lane-b` (`tools/**`), `-lane-c` (`gk-forge/tools/seedsmith/**`), `-lane-d` (`tools/**`); `keepverse-split` claims only `workspace_roots.py` and its test (read here, never edited) | worktree; direct (not edited) |
| `gk-data/packs/fusion/data/seed/dungeon/**`, `gk-data/packs/fusion/data/seed/narrative/**` (new) | lanes C (`gk-data/packs/fusion/data/seed/**`), D (`data/**`) | worktree |
| `gk-core/scripts/enforcement-registry.v1.json` | lanes B, D, D2 | worktree |
| `gk-core/scripts/verification-boundaries.v1.json` | `keepverse-split`; lanes A2, B, C, D, D2, D3 | direct; worktree |
| `gk-core/scripts/guard-generated-seed.py`, `scripts/guard-narrative-seed.ps1` (new) | lane D (`scripts/**`) | worktree |
| `.github/workflows/ci.yml` (NS6b) | `ip-censor` T1, T11 (step additions); lanes C, D | direct; worktree |
| `gk-forge/tools/seedsmith/seedsmith/report/cli.py` | `ip-censor` T16 (`--node`); lanes B, C, D | direct; worktree |
| `docs/architecture/decisions.md` | `keepverse-split`, `trade-network-idea-20260919`; lanes B, C, D (`docs/**`) | direct; worktree |
| `docs/architecture/narrative-seed-map.md`, `narrative-seed-ideal.md` (NS70) | lanes B, C, D (`docs/**`) | worktree |
| `tasks/narrative-seed-plan.md`, `tasks/narrative-seed-todo.md` | `narrative-plan-20260920` (this plan's author) | direct; released to the implementing session at NS0 |

**Clean-or-skip, for every shared file, before the edit:**

1. `git status --porcelain -- <file>` is empty. If the file is dirty (another direct session's uncommitted
   work), **skip it**: commit the task's other files only if they stand alone, otherwise defer the whole
   task, and record the skip in the task's status line.
2. For each worktree lane that claims it, `git diff $(git merge-base HEAD <branch>)..<branch> -- <file>`
   does not touch the region being edited (`session-boundary.md` §5). A region overlap goes to the owner;
   a different region merges cleanly.
3. **Never** `git stash`, `git checkout -- <file>`, `git reset` around another session's work, and never
   `git add -A` / `git commit -a`. Stage the task's explicit paths only.

---

## 9. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| The class-C `DEFAULT_CONFIG` bypass has more sites than the spec's examples | Medium: NS6's guard stays red | NS6 runs the guard in report mode first and fixes every listed site in the same commit; no site list is pinned |
| The local endpoint ignores `response_format` | High: every schema guarantee decorative | `narrative preflight` (NS15) before every run task |
| Glosses surface a third-party mark | Medium | Release scan covers the gloss registry (IC-3); no in-loop check |
| A regenerated legacy event ends `unresolved` | Low | Its committed file keeps its bytes and is listed in the run report (`spec-dungeon-generator-repair.md` §8) |
| The runtime loader is not ready at the Delve cutover | Medium | NSG3 default: storylets committed, unread; nothing deleted |
| Lane merges rewrite the boundary or enforcement registry around new rows | Medium | Clean-or-skip region check; the registries' own meta-tests catch a dropped row |
| A voted field shows high disagreement in the first batch | Medium: quality | `Narrative/VoteDisagreement` reading; the fix is a description change, which stales only affected items |

## 10. External dependencies

| Dependency | Needed by | If not ready |
|---|---|---|
| TVB3.1–TVB3.3 (python lane) | NS1 | Focused pytest per task (D3) |
| TVB4.7 (`gk-data/packs/fusion/data/seed/**` mapping) | NS2 | Same |
| `ip-censor` T14 (`briefkit.avoid_list`) | NS46 (soft), NS24 (soft) | Empty `avoid`, recorded; the exemplar IP test skips with a note |
| `identity-rename` T1 | NS26 (coordination only) | NS26 lands the file |
| `npc-story-events` `storylet-contract` loader switch; `party-dungeon` room pools | NS69 | NSG3 default |
| The configured local model endpoint | run tasks only | Run tasks wait; code tasks continue |
| Owner review sittings | NS16–NS19, NS29, NS58–NS68 | Stated per task; never blocks code |

## 11. DESIGN-GATE §5 checklist

```
[x] Subsystems: seedsmith core touch-points (transport, validators, briefkit, report CLI), the dungeon
    adapter's event kind, a new narrative adapter and corpus, two shared registries, runtime programs as
    consumers only.
[x] Session boundary: this plan is written under narrative-plan-20260920 (paths: the two plan files);
    the implementing session records its own boundary at NS0.
[x] Read this session: the map, all 23 specs with their audit and alignment sections, both ideals' §10,
    the ai-native README, the plan skill and command, seedsmith-design, agent-git, session-boundary,
    testing-standard, AGENTS.md verification boundary, ip-censor and identity-rename plans,
    npc-story-events map.
[x] Verified against code: verify-change.ps1 (:118), the boundary registry (schemaVersion 2, no pytest
    runner), the enforcement registry shape and its meta-test, guard-generated-seed.py, llm_caller.py
    (:63, :298, :504), ci.yml (:337), story-scene tuning (:13), the absence of gk-data/packs/fusion/data/seed/narrative and
    briefkit/avoid_list.py, active session records.
[x] No assertion pins a population; closed vocabularies are pinned with reasons.
[x] No SOLID-violating parallel path: one storylet generator after NS69, one avoid-list helper, one
    names file, one sampler, one renderer.
[x] Registry rows: ten rows, each in the task that makes it true (D4); eight are guarded by the new
    catalogued script `scripts/guard-narrative-seed.ps1` (NS6b), one by `generated-seed`, and one
    carries a genuine unguardableReason (open-loop voice).
[x] Gates: four, each irreversible, each with resolver and default (§7).
```

---

## Plan audit (2026-09-20)

Independent adversarial standards audit of this plan and [narrative-seed-todo.md](narrative-seed-todo.md),
fix-in-place. Standards read this session: `.claude/skills/planning-and-task-breakdown/SKILL.md`,
`.claude/commands/plan.md`, AGENTS.md *Verification boundary*, `docs/contributing/agent-git.md`,
`session-boundary.md`, `testing-standard.md`, `live-probe-standard.md`,
`docs/architecture/validation-ssot.md`, `tunables-ssot.md`, `gk-core/scripts/enforcement-registry.v1.json` with
`gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs`, `DESIGN-GATE.md` §5. Every boundary claim
below was **measured**, not read: `verify-change.ps1 -PlanOnly -AllowUnscoped` per path,
`gk-core/scripts/verification-boundaries.v1.json` (124 rows), `gk-core/scripts/guard-verification-boundaries.py`,
`.github/workflows/ci.yml`.

Every finding is fixed in this file or the todo unless marked deferred.

| # | Sev | Finding | Status |
|---|---|---|---|
| A1 | High | **Two new/edited guard scripts had no verification boundary.** `scripts/guard-*.ps1` has no glob row; each mapped guard is named individually. Measured: `-PlanOnly -Paths gk-core/scripts/guard-generated-seed.py` throws `VERIFICATION BOUNDARY MISSING`. NS34 recorded that as a note ("`scripts/guard-*.ps1` is unmapped") — AGENTS.md makes it a **defect to fix**. The sibling program already maps its own `guard-narrative.py` | **Fixed** — D3 rule 4; NS6b adds `guard-narrative-seed`, NS34 adds `guard-generated-seed`, both `level: module`, no `verificationId` (`notify-core-domain` precedent) |
| A2 | High | **The single catalogued guard could pass vacuously.** The enforcement meta-test proves R1/R6/R8 only; none looks inside the script. A row given `guards: ["narrative-seed"]` whose check line was forgotten is green and enforces nothing | **Fixed** — D4 and NS6b: the guard derives its required row set from the registry, fails on any row with no check line (and any check line with no row), fails a check selecting zero node ids, and NS6b's verify runs that falsifier |
| A3 | High | **No agent-type assignment at all**, though the plan has four hard-edge tasks (two model runs that overwrite a committed generated tree, a cross-program delete, a CI job re-order). The sibling plan has §5 | **Fixed** — new §D6b; NS18, NS19, NS69 and NS6b marked `implementer-hard` in the todo |
| A4 | High | **Two uncoordinated cross-plan file collisions.** `ip-censor` **T16** edits `report/cli.py`, which nine tasks here edit and which §4 serialised only against itself; `ip-censor` **T1/T11** add steps to `.github/workflows/ci.yml`, which **NS6b re-orders** | **Fixed** — §6 `ip-censor` row, §8 table gains both files, todo conventions and NS6b carry the clean-or-skip rule |
| A5 | Medium | **Gate ids collided.** This plan's `G1`–`G4` share a namespace with the `npc-story-events` map's `G0`–`G7`, which §6 of this very plan cites — "G2" meant two different things one page apart. The sibling renamed its own to `PG1`–`PG3` for exactly this reason. The approved `narrative-seed-map.md` names no gate ids, so nothing upstream is contradicted | **Fixed** — renamed `NSG1`–`NSG4` throughout both files; the one true cross-reference is labelled as the other map's |
| A6 | Medium | **The four scale tasks (NS62–NS65) carried a budget line but not the dry-run / preflight / review / commit-accepted steps** that principle 7 and D6 require of every model run; two of them (NS64, NS65) had no `Accept:` or `Verify:` at all | **Fixed** — todo: a shared step rule plus per-task Steps/Accept/Verify |
| A7 | Medium | **NS62 and NS63's illustrations did not subtract batch 1**, unlike NS17, NS19 and NS68 — they over-stated the remaining spend by 48 and 96 base calls | **Fixed** — both restated net of batch 1 (288 / 336 base), and the dry run's figure is restated as the number NSG4 approves |
| A8 | Medium | **Five specs were implemented by tasks that never cite them** — `spec-lore-packet.md`, `spec-storylet-pipeline.md`, `spec-character-pipeline.md`, `spec-arc-pipeline.md`, `spec-delve-event-regen.md` — because the todo drops its `### <module> (spec: …)` headers after Phase 4. Coverage was real; traceability was not | **Fixed** — headers added for Phases 5–7 (including `narrative-planner` and `spine-pipeline`) |
| A9 | Low | **`npc-story-events` writes one file into this program's tree** (`_registry/doctrines.v1.json`, its NR1.3/NR6.1) and maps `gk-data/packs/fusion/data/seed/narrative/_registry/**` in its own boundary row; §6 did not say so, and NS2 could have landed a duplicate owner pattern, which `guard-verification-boundaries.py:74-77` refuses as *ambiguous* | **Fixed** — §6 `npc-story-events` row |
| A10 | Low | D3 asserted `gk-data/packs/fusion/data/seed/narrative/**` and `gk-forge/tools/seedsmith/**` are unmapped without saying the claim was measured | **Fixed** — all four claims re-measured this session and confirmed; `.github/workflows/**` added to the mapped list (boundary `ci-workflows`) |
| A11 | Info | **NS1/NS2 edit `gk-core/scripts/verification-boundaries.v1.json`, which `narrative-seed-map.md` §7 assigns to `test-verification-boundary`.** The plan already names the owner instruction, scopes NS1/NS2 to additive narrative rows only, and schedules NS70 to reconcile the map row | **No change** — the conflict is named and sequenced, which is what the gate asks for |

**Checked and found correct** (no change needed): every module of the approved map has at least one task
(23/23); no task invents a module the map or a spec does not have; wave order and the two cross-program
seams (seed module → runtime module, the Delve cutover as **one** change across both programs) match the
specs; all four gates are genuinely irreversible with a resolver and a stated default, and nothing else is
gated; no acceptance criterion pins a population — corpus sizes, per-cell counts, call totals and
generated text are printed as readings and the pinned counts are closed vocabularies with their reason;
no task hand-edits generated seed data (NS19 regenerates through the generator; NS24, NS29 and NS41 author
only under `_registry/`/`_exemplars/`, which the NS34 guard row treats as source); the model-spend tasks
carry call budgets whose arithmetic checks out (NS17 77/231, NS19 48/144, NS58 48/144, NS59 93/279,
NS68 288/864); the `ci.yml:241` vs `:295` citation and the single-job structure are correct; the
`ip-censor` T14 / IC-3 and `identity-rename` T1/D1 citations are correct.

`python scripts/audit-doc-citations.py --scope tasks/narrative-seed-plan.md` — **0 HIGH** (26 resolvable
citations; the D1 count is future files this plan creates, which the audit does not rank HIGH).

**Owner decisions that genuinely remain:** none introduced by this audit. The plan's own four gates
(NSG1–NSG4) and the owner-review steps already named in §7 and §10 stand unchanged.
