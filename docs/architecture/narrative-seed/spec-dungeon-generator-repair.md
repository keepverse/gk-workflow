# Spec: `dungeon-generator-repair`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `dungeon-generator-repair` · **Map row:** 4 · **Wave:** 0
**Depends on:** `script-check`, `gloss-registry`; for the regeneration run (§8) also `gloss-fill` and `model-config-resolve` · **Model calls:** one bounded regeneration run of the legacy (Owner ruling 2026-09-20: all, `story` included; was: non-story) events (§8, Owner ruling 2026-09-19 (round 4)); the code repair itself is built and tested against stubs
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.

---

## Objective

Fix the current Delve event generator's known defects with **no new design**, so it can no longer leak
motif tokens, can no longer forge chain ids, and records what produced each entry:

1. briefs carry glossed motifs, never raw ones;
2. the widened script check runs inside the event retry loop;
3. the event prompt has a `PROMPT_VERSION`, and emitted entries carry provenance;
4. `climateAffinity` moves from AUTHORED to PLANNED;
5. the generator stops forging chain ids;
6. every legacy event carries a text key for its `name` and its `flavor` (§9);
7. the repaired generator **regenerates the contaminated legacy events** — Owner ruling 2026-09-20: the four `story` events included, keeping ids and committed `chainRef`s (§6, §8).

Owner ruling 2026-09-19 (round 4): *players must never see a blank Delve event.* Items 6 and 7 replace this
spec's earlier "not in scope: regenerating the 54 committed events", which relied on the runtime showing
legacy text as `Pending` (`npc-story-events/spec-delve-live-rooms.md` §4). The live Delve now shows clean,
keyed legacy text from day one, rendered through `npc-story-events`' `narrative-text` lingui codegen bridge;
`delve-event-regen` (Wave 6) later replaces the whole legacy tree with storylets in the same change as the
loader switch. No committed event file is edited by hand — every change reaches the tree through the
repaired generator's committer (map §2 principle 8).

---

## Design

### 1. What is broken today (verified 2026-09-19)

| Defect | Evidence |
|---|---|
| The system prompt demands a listed motif verbatim | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:324` |
| The brief injects the theme's raw motifs and anti-motifs | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:351-355`; allocated at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:318` |
| The retry loop checks motifs and name collision only | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334-337` |
| No prompt version exists; no committed orchestrator stamps provenance | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py:19-30` |
| `climateAffinity` is model-authored | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:123`; free enum at `:240` and per-cell at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:304` |
| The last story event's `chainRef` is invented as `-{n+1}` | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:300-310` |

The motif check itself matches by case-sensitive substring
(`gk-forge/tools/seedsmith/seedsmith/workflow/validators/motif.py:24`, `:34-35`). That is fine for Chinese motifs
and wrong for English glosses: `Ash` would miss `ash`, and `ash` would falsely match `crash` — the
word-list failure AI Dungeon shipped (`narrative-seed-ideal.md` §5.1).

### 2. Glossed motifs in the event brief

In `run_event_draws`, after `motif_brief_for_slot` partitions the theme's motifs
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/planner.py:135`), both lists pass through
`GlossTable.gloss_all` (`gloss-registry`). Then:

- **An unglossed motif makes that slot `unresolved`** with reason `gloss_missing: <motifs>` and **zero
  model calls** for that slot. The refusal is the design: a raw motif never reaches a brief.
- **Anti-motifs minus motifs.** Two distinct motifs can share an English gloss; if a gloss lands in both
  the slot's motifs and its anti-motifs, it is removed from the anti-motifs (the slot's own assignment
  wins) and the removal is recorded on the draw result. Without this rule a slot could be told to use and
  avoid the same word, which is unsatisfiable.
- `build_event_brief` (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:346`) receives the glossed
  lists; its wording names them as "motif words" in the target language. The system prompt keeps its
  rule — use at least one listed motif word, never an anti-motif word — now over English words.

`motif_coverage` and `anti_motif_violation` gain script-aware matching: a motif whose characters are all
`latin` (per `script-check`'s classifier) matches case-insensitively on word boundaries; any other motif
keeps today's substring match, so the Chinese-motif consumers (commander effects, tree nodes) are
unchanged. This is a small change to a shared validator, proven by a positive and negative test in each
direction.

### 3. The script check in the retry loop

The loop at `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334` adds
`script_policy(draft, {"scriptPolicy": EVENT_SCRIPT_POLICY})`. The policy map is declared once in
`briefs.py`:

| Field path | Policy |
|---|---|
| `name`, `flavor`, `reason` | `latin` |
| every other string leaf (`eventId`, `kind`, `theme`, `climateAffinity`, `repeatScope`, `supplyOverride`, `chainRef`, `outcomes[].ordinal`, `outcomes[].consequence`, `outcomes[].dropBand`, `outcomes[].effects[].family`, `outcomes[].effects[].powerBand`) | `none` |

A script defect joins the other named problems and is fed back through the existing bounded QUALITY
retry (`MAX_QUALITY_RETRY = 2`, `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:239`). An
undeclared string field is itself a defect, so a future event field cannot slip past.

### 4. Prompt version and provenance

- `EVENT_PROMPT_VERSION = "dungeon-event/1"` in `briefs.py` — the first versioned prompt; the committed
  corpus predates versioning. It is bumped on any change to `EVENT_SYSTEM_PROMPT`, `build_event_brief`,
  `build_event_schema_for_cell` or `EVENT_SCRIPT_POLICY`. A test holds a sha256 of those four sources'
  rendered output for a fixture cell next to the version string, so an edit without a bump fails. That
  hash is of code-owned prompt text — a declaration, not generated content.
- `EventDrawResult` gains `brief_hash` (the rendered user brief, `gk-forge/tools/seedsmith/seedsmith/pipeline/staleness.py:25`)
  and `anti_motifs_removed`.
- A thin committer, `commit_event_draws(results, out_dir, *, config)`, writes accepted entries through
  the existing writer (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/emit.py:73`) with
  `build_provenance(brief_hash, prompt_version=EVENT_PROMPT_VERSION, schema_version, model_id=config.model)`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/emit.py:31`). `config` is the resolved transport config;
  this module accepts it and never constructs one. This is the minimum wiring that lets a repaired run
  carry provenance at all (the gap `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py:19-30` records); it adds no CLI.

### 5. Climate becomes PLANNED

- `EVENT_OWNERSHIP["climateAffinity"]` changes from `AUTHORED` to `PLANNED`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:123`); the generic schema pins it `const`
  (`:240` moves to `_enum(..., const=True)`); the per-cell schema pins the planned value
  (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:304`); the audit's `planned_const_audit` then proves it
  (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/audit.py:158`).
- A new pure function, `planner.assign_event_climates(planned_ids_by_cell) -> dict[event_id, climate]`,
  assigns climates **inside today's kind × theme cells** — the grid change to host × kind × climate is
  `narrative-planner`'s, with its `decisions.md` row (map §3.5 item 5, §11 item 1). The rule: within each
  event kind, sort that kind's planned ids, then assign the seven climate values (the six elements, then
  `none`) in rotation. The rotation order is structural (a fixed ordering over a closed vocabulary, not a
  balance number) and says so in a comment. Every kind with seven or more slots covers every climate;
  the model no longer decides.

### 6. No more forged chain ids

The legacy contract makes a finite chain impossible without a dangling tail: `EventCatalog.Load` refuses
a `story` row with no `chainRef` (`gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:181-185`), and the
preflight refuses a cycle while silently skipping an unresolved target
(`gk-core/src/FusionRpg.Core/Delve/Events/EventDeckPreflight.cs:53-69`). So the last link of any legacy chain
must point at an id that does not exist — which is exactly what `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:300-310` forges.

The repair therefore **generates no new `story` events**:

- `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:300-310` is deleted.
- `run_event_draws` raises `ValueError` naming the cell when handed a `story` cell: *"story events are arc
  links under the narrative adapter (arc-shapes); the legacy contract cannot express a chain's last link
  without a dangling chainRef."* The first-ship kind list already excludes `story`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:225`); this makes it a refusal rather than a
  default.
- Every non-story event keeps `chainRef: "none"` (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:310`).

Story beats return as arc links in the widened contract (`arc-shapes`, `narrative-contract`), where a link
can never point past its arc.

**One exception, the committed ones (Owner ruling 2026-09-20).** The refusal above is for **new** story cells. The
§8 regeneration run also regenerates the four **committed** legacy `story` events, keeping their ids: for them the
driver passes each event's committed `chainRef` as a PLANNED `const` (`committed_chain_refs`, read from the committed
file), so `run_event_draws` accepts a `story` cell only when that value is supplied and never mints or forges one.
Their chain links still dangle exactly as the legacy contract forces — accepted by the owner; `npc-story-events`'
preflight tolerates it only as named entries on its known-defect list until `delve-event-regen` replaces the legacy
tree (`npc-story-events/spec-storylet-contract.md` §6).

### 7. What does not change

The outcome count stays at two (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:236`); widening it
is the storylet contract's job. The dungeon adapter's other six kinds are untouched. Under
`gk-data/packs/fusion/data/seed/dungeon/` only `events/` changes, and only through §8's committer (Audit 2026-09-19: this line
said "no committed file changes", which the round-4 ruling reversed).

### 8. The legacy regeneration run (Owner ruling 2026-09-19 (round 4))

**What is regenerated.** Owner ruling 2026-09-20: **every** committed legacy event, the four `story` events
included — measured 2026-09-19 as 54 events, 53 of them carrying Han characters in `name` or `flavor` (a reading,
never asserted). The one clean event is regenerated too, because its text key can only come from the generator's
committer (§9) and a key is never added by hand. A `story` event is regenerated clean and keyed under its own id
with its committed `chainRef` passed through unchanged (§6); the dangling tail is the committed one, never a newly
forged id. (Owner ruling 2026-09-19 (round 4) had scoped this to non-story events; the 2026-09-20 ruling widens it.)

**Same identity, same id.** A regenerated event is the same entry made correctly — same cell, same slot —
so it keeps its committed `eventId` (`docs/architecture/item/seed-contract.md` §7.2, first row). The run
passes the committed ids as `planned_ids_by_cell` instead of minting new ones, so every room `eventPool`
reference (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/kinds.py:27`) still resolves. The cells are the
committed batch's kind × theme cells; the climate is re-assigned by `assign_event_climates` (§5), which is
the point. `existing_names` for the collision check excludes the batch being regenerated, so an event does
not collide with its own old name.

**How it runs.** `seedsmith dungeon events regen` (new), `--dry-run` by default: it reads the committed
events, rebuilds their cells, renders every brief through the gloss lookup and prints the call count before
anything is spent (`docs/research/ai-native-generation/README.md` §9: base one call per event, worst three —
one call plus `MAX_QUALITY_RETRY` repairs; no vote, because this is the legacy contract with no new design).
`narrative preflight` (`gloss-fill`) proves constrained decoding with one real call first. `--write` runs the
draws with the resolved config (`model-config-resolve`; never `DEFAULT_CONFIG`), writes accepted drafts to a
scratch run file, and `commit_event_draws` writes them only after review. An `unresolved` slot keeps its
committed file untouched and is listed in the run report; the run never writes a partial event.

**Review before commit.** A seeded stratified sample over event kind (`stratified_sample`,
`gk-forge/tools/seedsmith/seedsmith/sampling/__init__.py:38`), verdicts `accept · reject` recorded in the run file
(append-only). A rejected event is regenerated with the reviewer's reason named in its brief; it is never
edited. Sample size is `event.regenReviewSample` in `data/seed/dungeon/_plan/budget.v{n+1}.json` (published
through the budget's own version bump, never a code constant).

**The committed legacy `story` events — answered (Owner ruling 2026-09-20).** They are **regenerated clean, not
retired**: the wild rooms' `eventPool`s keep naming them (for example
`gk-data/packs/fusion/data/seed/dungeon/rooms/room.wild-air-001.json`, lines 5–9), so the room generator's refusal of a wild room with no
story event (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:589`) is never met, and no kind this program does
not own changes. Their `chainRef`s are carried over, not re-forged (§6).

### 9. Text keys for legacy events (Owner ruling 2026-09-19 (round 4))

Every event file `commit_event_draws` writes carries `nameKey` and `flavorKey` beside `name` and `flavor`
— the key and its string authored together, in the same file, from row one
(`docs/architecture/item/seed-contract.md` §6). The key rule is `narrative-contract` §4's, so the runtime's
codegen bridge reads legacy and storylet keys the same way: `ns.event.<eventId body>.<field>.<h8>`, where
`h8` is the first eight hex digits of the SHA-256 of the string; it matches `^[a-z0-9.-]+$`, is globally
unique, and a changed string is a new key. Both keys are DERIVED at commit (never in a model-facing schema;
ownership rows in `schema.py`). The legacy loader reads fields by name and ignores unknown ones
(`gk-core/src/FusionRpg.Core/Delve/Events/EventSeedFile.cs:40-74`), so the added keys load without a runtime change;
putting the keyed text on the wire is `npc-story-events`' (`narrative-text`, `delve-live-rooms`).

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py gk-forge/tools/seedsmith/tests/test_dungeon_event_briefs.py gk-forge/tools/seedsmith/tests/test_dungeon_planner.py gk-forge/tools/seedsmith/tests/test_dungeon_contract.py -q
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/workflow/validators -q
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_dungeon_idempotency.py -q
# Owner ruling 2026-09-19 (round 4): the legacy regeneration run (§8)
cd tools\seedsmith; python -m seedsmith narrative preflight                       # one real call proves constrained decoding (gloss-fill builds it)
cd tools\seedsmith; python -m seedsmith dungeon events regen --dry-run           # DEFAULT: rebuild cells, render every glossed brief, print calls, call nothing
cd tools\seedsmith; python -m seedsmith dungeon events regen --write             # draws into a scratch run file; never the corpus
cd tools\seedsmith; python -m seedsmith dungeon events regen --review --run <runId>   # seeded sample, accept/reject verdicts
cd tools\seedsmith; python -m seedsmith dungeon events regen --commit --run <runId>   # accepted drafts through commit_event_draws
```

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py     gloss step, script check, chain forge removed, story refusal, brief_hash
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py        EVENT_PROMPT_VERSION, EVENT_SCRIPT_POLICY, glossed brief, climate const
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/planner.py       assign_event_climates
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py        climateAffinity -> PLANNED, const
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/commit.py        (new) commit_event_draws, text keys (§9)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/regen.py         (new) legacy regeneration driver: committed ids, dry run, review sample (§8)
gk-forge/tools/seedsmith/seedsmith/report/cli.py                     `dungeon events regen` verb (§8)
gk-data/packs/fusion/data/seed/dungeon/events/**                                 every regenerated legacy event, `story` included (Owner ruling 2026-09-20), keyed (committed diff of the §8 run)
data/seed/dungeon/_plan/budget.v{n+1}.json                  `event.regenReviewSample` row (published, never edited in place)
gk-forge/tools/seedsmith/seedsmith/workflow/validators/motif.py      script-aware matching
gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py       extended
gk-forge/tools/seedsmith/tests/test_dungeon_event_briefs.py          extended
gk-forge/tools/seedsmith/tests/test_dungeon_planner.py               extended
gk-forge/tools/seedsmith/tests/test_dungeon_commit.py                (new)
gk-forge/tools/seedsmith/tests/workflow/validators/test_motif.py     (new)
```

## Code style

Follow the dungeon adapter's conventions: `call` is injected, never imported
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:1-4`); registries read fresh; every refusal
names the id and the reason; the stub pattern is `FakeCall` from
`gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py:49-58`.

## Testing strategy

All with the transport stubbed; a real call raises.

| Test | Asserts |
|---|---|
| `brief_contains_glosses_not_raw_motifs` | with a fixture gloss table, the rendered brief contains every gloss and no character the classifier puts outside `latin`/`digit`/`common` |
| `unglossed_motif_makes_slot_unresolved_without_a_call` | `FakeCall` with zero responses is never invoked; reason starts `gloss_missing:` and names the motif |
| `shared_gloss_is_dropped_from_anti_motifs` | a gloss in both lists leaves the anti list and is recorded |
| `script_defect_triggers_named_quality_retry` | first draft has `分配` in `flavor`; the second prompt names the field and class; the clean second draft is accepted |
| `script_defect_exhausts_to_unresolved` | three contaminated drafts → `unresolved`, bounded at `MAX_QUALITY_RETRY` |
| `undeclared_string_field_is_a_defect` | a draft carrying an extra string field is rejected by the policy |
| `motif_match_is_word_bounded_for_latin` | `ash` does not match `crash`; `Ash` matches `ash` |
| `motif_match_unchanged_for_chinese` | existing substring behaviour for a Chinese motif |
| `prompt_version_moves_with_prompt_text` | the pinned hash matches the rendered prompt for the fixture cell at `dungeon-event/1` |
| `climate_is_planned_const` | the per-cell schema offers `climateAffinity` as `const`; `run_audit("dungeon-event")` is clean |
| `climate_rotation_covers_all_seven_per_kind` | a fixture of seven slots of one kind gets seven distinct climates; the assignment is identical across two calls |
| `story_cell_is_refused` | `run_event_draws` raises naming the cell when no committed `chainRef` is supplied; no call is made |
| `no_forged_chain_ref` | no emitted entry's `chainRef` names an id outside the batch |
| `commit_stamps_provenance_from_resolved_config` | `_provenance.modelId` equals the passed config's model; `promptVersion` is `dungeon-event/1` |
| `commit_is_byte_identical_on_rerun` | two commits of the same results hash identically (extends `test_dungeon_idempotency.py`) |
| `commit_writes_name_and_flavor_keys` | every committed fixture event carries `nameKey` and `flavorKey` matching `^[a-z0-9.-]+$` and the §9 rule; a changed string yields a new key, an unchanged one keeps its key (Owner ruling 2026-09-19 (round 4)) |
| `keys_are_not_model_facing` | no event call schema contains `nameKey` or `flavorKey`; the ownership table marks both DERIVED |
| `regen_reuses_committed_ids` | a fixture legacy tree regenerates with the same `eventId`s; no new id is minted and no room `eventPool` reference dangles |
| `regen_regenerates_story_events_keeping_chain` | a fixture tree with a `story` event: the run regenerates it under its own id, clean and keyed, with its committed `chainRef` byte-identical; the brief shows the `chainRef` as `const` (Owner ruling 2026-09-20) |
| `regen_dry_run_makes_no_call` | the regen dry run renders every brief with a transport that raises and prints base and worst-case calls |
| `regen_unresolved_keeps_committed_file` | an event whose draws end `unresolved` keeps its committed bytes and is listed in the run report |
| `regen_commits_only_accepted_after_review` | commit writes only drafts with an `accept` verdict or an unsampled draft of a batch whose sample has no open rejection; a `reject` regenerates with the reason named |
| `regen_uses_resolved_config` | the run's transport receives the model resolved by `load_config` (fixture `.env`); no `DEFAULT_CONFIG` reference in `regen.py` |

## Boundaries

- **Always:** gloss before brief; refuse an unglossed slot; name every defect in the retry prompt; keep
  climate const.
- **Ask first:** any live batch beyond §8's legacy regeneration; changing the outcome count; retiring a committed
  legacy `story` event (Owner ruling 2026-09-20: they are regenerated, §8).
- **Never:** pass a raw motif to a brief; generate a **new** `story` event, or forge a `chainRef` (a committed one is
  carried over, §6); hand-edit a committed event (a key included); mint new ids for regenerated events; change the
  event cell grid here.

## Success criteria

- [ ] No rendered event brief contains a non-Latin character from a motif.
- [ ] The script check runs in the event retry loop and its defect is repaired or ends `unresolved`.
- [ ] `EVENT_PROMPT_VERSION` exists and its drift test is green; committed entries carry `_provenance`
      with the resolved model.
- [ ] `climateAffinity` is PLANNED and const; the audit is clean.
- [ ] The generator refuses `story` cells; no chain id is forged.
- [ ] Owner ruling 2026-09-19 (round 4), widened by Owner ruling 2026-09-20: every committed legacy event, the
      `story` events included, has been regenerated through the repaired generator under its own id, passes the
      `latin` script policy on `name` and `flavor`, and carries `nameKey` and `flavorKey`; `story` events keep their
      committed `chainRef`; the share of events still leaking a foreign script is a printed reading (expected zero),
      never an asserted count.
- [ ] The seedsmith suite is green with the transport stubbed to raise.

## Open questions

None. ~~1. **The four committed legacy `story` events.**~~ **Answered — Owner ruling 2026-09-20:** regenerate them
clean and keyed with the other 50, keeping their ids; their chain links still dangle as the legacy contract forces
(accepted), and the runtime preflight tolerates that only as named known defects until `delve-event-regen` replaces
the legacy tree. The recommended default (b), retiring them, is withdrawn (§6, §8).

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Owner ruling 2026-09-19 (round 4): regenerate the contaminated legacy non-story events clean and key `name`/`flavor` from row one | fixed (§8, §9, commands, tests, criteria) |
| 2 | high | The four legacy `story` events stay contaminated; retiring them dangles the wild rooms' `eventPool` and hits the room generator's refusal (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:589`) | **resolved — Owner ruling 2026-09-20:** regenerated clean and keyed, ids and committed `chainRef`s kept (§6, §8) |
| 3 | medium | A regeneration that minted new ids would dangle every room `eventPool` reference | fixed (committed ids reused, `item/seed-contract.md` §7.2) |
| 4 | medium | The legacy event pipeline votes no field (README §10 vote set) | deferred — no new design in the legacy contract; `delve-event-regen` replaces it |
| 5 | low | "No committed file under `gk-data/packs/fusion/data/seed/dungeon/` changes" became false | fixed (§7) |
| 6 | low | Citations sampled: `briefs.py:324/:236/:589`, `schema.py:123/:240`, `pipelines.py:239/:334`, `EventSeedFile.cs:40-74`, `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/kinds.py:27` — resolve | verified |

## Cross-lane alignment (2026-09-20)

Owner ruling 2026-09-20 — **legacy story events are regenerated clean, not retired.** §8 now regenerates all 54
committed legacy events, the four `story` events included, clean and keyed under their own ids; a `story` event's
committed `chainRef` is passed through as a PLANNED `const` (§6), so no id is forged and the wild rooms' `eventPool`
references keep resolving. The dangling tails are accepted and are listed on `npc-story-events`' known-defect list
until `delve-event-regen`. The "retire" option and the open question are removed.
