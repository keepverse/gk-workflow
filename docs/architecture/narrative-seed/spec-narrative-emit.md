# Spec: `narrative-emit`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `narrative-emit` · **Map row:** 11 · **Wave:** 2 (after `narrative-contract`)
**Depends on:** `narrative-contract` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.

---

## Objective

Turn accepted drafts into committed seed files so that the corpus is **reproducible, auditable and safe
for saves in progress**:

- canonical JSON, so a hash means something;
- `_provenance` on every generated seed — the resolved model, the prompt versions and the input hashes;
- a run ledger, so a resumed run never redoes finished work;
- `stale_ids`, naming exactly the seeds whose inputs changed;
- `revision` bumped when, and only when, a seed's content changes, with the superseded revision kept;
- tombstones instead of deletions, and ids never reused;
- a rerun over unchanged inputs that is **byte-identical by hash**.

The runtime needs `(id, revision)` to keep an in-progress arc stable when the corpus is regenerated
(`npc-story-events-ideal.md` §11 item 3; `npc-story-events-map.md` success criterion "revision pinning").
This repo has already shipped the non-idempotent version of an emitter once: the commander-effect
generator rewrote all 84 entries every run (`docs/research/ai-native-generation/README.md` §6).

**Done means:** `emit`, `withdraw` and `stamp_authored` exist as deterministic functions; every rule below
has a test; a second emit over unchanged inputs changes no byte.

---

## Design

### 1. What exists and is reused

| Piece | Evidence | Use here |
|---|---|---|
| Canonical rendering rules: sorted keys, two-space indent, `\n`, non-ASCII unescaped, explicit nulls | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/emit.py:24-28` | same rules, stated in this adapter's own writer |
| `_index.json` per directory | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/emit.py:60-70` | same shape |
| Shared staleness key and brief hash | `gk-forge/tools/seedsmith/seedsmith/pipeline/staleness.py:25`, `:32` | the recorded key |
| Staleness is reporting only; regeneration of a stale seed is an explicit forced run | `gk-forge/tools/seedsmith/seedsmith/pipeline/staleness.py:11-15` | `stale_ids` reports; it never triggers a write |
| Run ledger with atomic writes and terminal rows | `gk-forge/tools/seedsmith/seedsmith/pipeline/run_ledger.py:25`, atomic write `:38-55`, terminal rows `:62-94` | one ledger per pipeline |
| "A plan that adds a cell must not stale untouched entries" | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/provenance.py:37-47` | the plan hash is recorded, never part of the staleness key |

### 2. Input

`emit(accepted: Sequence[AcceptedSeed], *, out_root, ledger, config) -> EmitReport`. An `AcceptedSeed`
carries the planner's work item (every PLANNED value), the drafts from each call (every VALIDATED and
AUTHORED value), and one `CallRecord` per call: pipeline id, prompt version, rendered-brief hash, lore
packet hash, vote results and attempts. `config` is the resolved transport config
(`model-config-resolve`); emit reads `config.model` and never constructs a config.

### 3. Assembly — every DERIVED field, in one place

| Field | Rule |
|---|---|
| text `key` | `narrative-contract` §4: `ns.<namespace>.<id body>.<field path>.<h8>` |
| text `text` | the draft's short forms through `token-grammar`'s `expand` |
| `chainRef` | the next link's storylet id in the arc's work order; `none` for the last link and for non-arc storylets |
| character `side`, `element` | from the species anchor (`speciesId`, `side`, `elementPrimary` in `gk-data/packs/fusion/data/seed/creatures/species/`) |
| character `allegiance` | from `character-vocab` (role or leads block) |
| character `anchorReview` | from the recorded review verdicts (`review-render`); `pending` when none |
| `provenance` | `generated` — emit never writes an authored seed (§8) |
| `status`, `revision` | §5 |

The assembled entry passes `narrative-contract`'s `validate_entry` before anything is written. A refusal
writes nothing and is returned in the report with the field path; it never reaches the corpus
(`seedsmith/spec-pipeline.md` §3.5).

### 4. `_meta` and `_provenance`

File-level `_meta` (the envelope, `narrative-contract` §2): `contractVersion`, `partition` (the cell key),
`batch` (the run id), `model` (the resolved model), `promptVersion` (the joined, sorted prompt versions of
the calls that wrote the seed). These are the keys the generated-seed guard reads
(`gk-core/scripts/guard-generated-seed.py:117-124`) and the ones the core loader records
(`gk-forge/tools/seedsmith/seedsmith/corpus/model.py:189-190`).

Entry-level `_provenance`:

```json
{
  "model": "<resolved model id>",
  "calls": { "<call>": { "promptVersion": "<v>", "briefHash": "<sha256>", "attempts": 1 } },
  "inputs": { "lorePacketHash": "<sha256>", "registryVersions": { "<registry>": 1 }, "planHash": "<sha256>" },
  "votes": { "<field path>": { "confidence": "high | split", "minority": "<value> | none" } },
  "contentHash": "<sha256>",
  "stalenessKey": "<sha256>"
}
```

| Field | Meaning | Negative clause |
|---|---|---|
| `model` | the model the calls used, from resolved config; equals `_meta.model` | never a default string (`model-config-resolve`) |
| `calls` | per call: prompt version, hash of the rendered brief, attempts to acceptance | not the brief text; not a timestamp |
| `inputs.planHash` | the planner's work-order hash, for audit | **not** part of the staleness key |
| `votes` | per voted field: the resolution (`high` 3-0 or `split` 2-1) and the minority value | not a quality score; it measures contract stability. Audit 2026-09-19: `unresolved` is removed from this enum — a 1-1-1 field ends its work item before emit (`resolve_vote`, `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26-43`), so an emitted seed can never carry it; `unresolved` is a ledger terminal row (§7) |
| `contentHash` | SHA-256 of the canonical entry with `revision`, `status` and `_provenance` removed and each text object reduced to its `text` | not a file hash |
| `stalenessKey` | `staleness_key(brief_hash, prompt_version, schema_version, model_id)` (`gk-forge/tools/seedsmith/seedsmith/pipeline/staleness.py:32`), where `brief_hash` is the hash of the sorted call brief hashes plus the lore packet hash, `prompt_version` the joined sorted call versions, and `schema_version` the contract version plus the sorted registry versions | not the content hash; two seeds with equal content can differ in staleness |

**No wall-clock time anywhere.** A timestamp is the one field that makes a generated file
non-reproducible; the item generators already inject it for that reason
(`gk-forge/tools/seedsmith/seedsmith/report/cli.py:2840-2843`). The run id comes from the ledger, not the clock.

### 5. Revisions, the archive and tombstones

| Situation | Action |
|---|---|
| a new id | write it at `revision: 1`, `status: live` |
| an existing live id, same `contentHash` | **write nothing** — the file keeps its bytes (idempotence) |
| an existing live id, different `contentHash` | copy the current file's bytes to `data/seed/narrative/_revisions/<directory>/<id>.r<n>.json`, then write `revision: n+1` |
| `withdraw(id, reason)` | archive the current file as above, then replace it with a tombstone row |
| a draft for a tombstoned id | refused — ids are never reused (`docs/architecture/item/seed-contract.md` §4) |
| an archive path that already exists with different bytes | refused — archives are immutable |

A tombstone row: `{ "id", "revision": n+1, "status": "tombstone", "provenance", "withdrawnReason" }` — a
closed shape of its own that `narrative-contract`'s `validate_entry` checks instead of the kind's full field
list (Audit 2026-09-19: aligned with `spec-narrative-contract.md` §11) — where
`withdrawnReason` is closed — `defect` (a flaw found after commit), `retired` (the content no longer
fits), `superseded` (a different seed now covers the cell). Negative clause: *a tombstone is not a
deletion and not a pause; it never becomes live again.*

The archive exists for the runtime: an arc started on revision `r` resolves against `r` after the corpus
moves on (`npc-story-events-map.md` row 4). Whether the runtime reads the archive or snapshots the seed
into the save is that program's choice; this module guarantees every revision a save can have pinned
still exists in the repository tree.

### 6. Ids and minting

The planner mints ids from a high-water mark (the dungeon's `IdMinter`,
`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/planner.py:60`). Emit exposes
`high_water_marks(out_root)`, computed over live files, tombstones and archives, so the planner can never
reissue an id that existed in any form.

### 7. Run ledger and staleness

- One `RunLedger` per pipeline at `data/seed/narrative/_runs/<pipeline>.ledger.json`. A done row records
  `{entryId, revision, contentHash}`; `is_valid` re-reads the file and compares the hash, so a file changed
  out of band is re-planned rather than silently trusted (`gk-forge/tools/seedsmith/seedsmith/pipeline/run_ledger.py:96-115`).
  Blocked, escalated and `unresolved` work items get terminal rows with their reason, never "done"; a
  `blocked` row is the call schema's `blocked` escape (`spec-narrative-contract.md` §9) and is never retried.
- `stale_ids(current: Mapping[str, str]) -> list[str]` returns the sorted ids whose recorded
  `stalenessKey` differs from the current one; a generated seed with no `_provenance` is stale (it cannot
  be proven current). Authored seeds are never listed: they have no generator to be stale against.
  The result is a report; regenerating a stale seed is an explicit forced run.

### 8. Write safety

- **Path allowlist:** emit writes only under `storylets/`, `characters/`, `arcs/`, `spine/`, `quests/`,
  `_revisions/` and `_runs/` of `gk-data/packs/fusion/data/seed/narrative/` (Audit 2026-09-19: `quests/`, the fifth kind's tree
  from `spec-quest-vocab.md`, was missing, so a generated quest anchor could never have been written). It never writes `authored/`, `_registry/`,
  `_exemplars/`, `_plan/` or another adapter's tree (`seedsmith/spec-pipeline.md` §7).
- **Atomic writes:** temp file then `os.replace`, the ledger's own pattern
  (`gk-forge/tools/seedsmith/seedsmith/pipeline/run_ledger.py:47-54`).
- **All or nothing per seed:** the archive copy, the new file and the index update for one seed either
  all land or none do.
- **No git:** emit writes files; a person commits them (`seedsmith/spec-pipeline.md` §7).

### 9. Authored seeds — `stamp_authored`

A hand-written seed under `authored/` needs keys and a revision too. `stamp_authored(paths)` is an
explicit command an author runs after editing: it derives keys, computes the content hash, bumps
`revision` and archives the previous revision under the same rules as §5 — writing only the named authored
files and their archives. It adds no `_meta.model`, so the generated-seed guard keeps ignoring authored
files, and regeneration never touches them (`narrative-seed-ideal.md` §11 item 5).

### 10. `decisions.md` row (drafted; appended in the build change — map §11 item 5)

> **Narrative seed identity over regeneration** (narrative-seed, 2026-09-19). Every narrative seed
> carries `revision`, bumped by emit only when its content hash changes; the superseded revision is kept,
> immutable, under `data/seed/narrative/_revisions/`; a withdrawn seed becomes a tombstone row with a
> closed reason; ids are never reused; `provenance: generated | authored` with authored seeds under
> `data/seed/narrative/authored/`, which regeneration never touches. A rerun over unchanged inputs is
> byte-identical.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_emit.py -q
cd tools\seedsmith; python -m seedsmith narrative stale                         # report: ids whose inputs changed
cd tools\seedsmith; python -m seedsmith narrative withdraw <id> --reason defect
cd tools\seedsmith; python -m seedsmith narrative stamp-authored <path> [<path> ...]
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/emit.py         (new) emit, render_file, content_hash, high_water_marks
tools/seedsmith/seedsmith/adapters/narrative/revisions.py    (new) archive, withdraw, stamp_authored
tools/seedsmith/seedsmith/adapters/narrative/staleness.py    (new) staleness key composition, stale_ids
gk-forge/tools/seedsmith/seedsmith/report/cli.py                      `narrative stale | withdraw | stamp-authored`
data/seed/narrative/_revisions/                              (new) empty
data/seed/narrative/_runs/                                   (new) empty
tools/seedsmith/tests/test_narrative_emit.py                 (new)
```

## Code style

Pure functions for assembly and hashing; the only I/O is in `render_file`'s writer and the archive copy.
Every refusal names the id and the rule. Match the ledger's docstring discipline: each non-obvious rule
says which defect it prevents.

## Testing strategy

Temporary trees are created **in memory or under pytest's `tmp_path` and removed by pytest**, never by a
swallowed delete (`docs/contributing/testing-standard.md`; `gk-core/scripts/guard-test-substrate.py`). Drafts are
fixtures; the transport is stubbed to raise.

| Test | Asserts |
|---|---|
| `rerun_is_byte_identical` | emit twice over the same accepted seeds; the SHA-256 of every file is unchanged and no file's mtime-independent bytes differ |
| `unchanged_content_is_not_rewritten` | the second emit reports zero writes |
| `changed_content_bumps_revision_and_archives` | `r1` lands in `_revisions/`, the live file is `r2`, the archive bytes equal the old file |
| `archive_is_immutable` | a conflicting archive write is refused |
| `withdraw_writes_tombstone_with_closed_reason` | tombstone shape; an unknown reason is refused |
| `tombstoned_id_is_never_reused` | a draft for it is refused; `high_water_marks` counts it |
| `keys_change_only_with_text` | a changed label gets a new key; unchanged labels keep theirs across a revision |
| `chain_ref_follows_arc_work_order` | links chain in order, last `none`, all resolve |
| `invalid_entry_writes_nothing` | a digit in a label → refusal in the report, no file, no ledger row |
| `meta_and_provenance_agree` | `_meta.model == _provenance.model == config.model` |
| `no_timestamp_in_output` | no key named like a time and no ISO-8601 value in any written file |
| `plan_hash_does_not_stale` | changing only the plan hash leaves `stale_ids` empty |
| `brief_change_stales_exactly_that_seed` | one fixture brief changes; `stale_ids` names that id alone |
| `authored_seed_is_never_stale_and_never_written_by_emit` | path allowlist and staleness both proven |
| `stamp_authored_bumps_and_archives` | same rules as §5, only for the named files |
| `ledger_reconciles_out_of_band_edit` | a hand-changed file fails `is_valid` and is re-planned |
| `write_is_atomic` | an injected failure between archive and write leaves the old live file intact |
| `quest_tree_is_in_the_allowlist` | a fixture quest anchor is written under `quests/`; a path outside the allowlist is refused (Audit 2026-09-19) |
| `unresolved_never_reaches_emit` | an accepted seed whose vote record says `unresolved` is refused by emit |

## Boundaries

- **Always:** validate before write; archive before bump; derive every DERIVED field here; record the
  resolved model.
- **Ask first:** a new `withdrawnReason`; any change to the key rule or the content-hash definition (both
  change every key or every revision).
- **Never:** delete a seed file; reuse an id; write a timestamp; write outside the allowlist; regenerate on
  staleness without an explicit forced run.

## Success criteria

- [ ] A second emit over unchanged inputs is byte-identical, proven by hash.
- [ ] Revisions bump only on content change; every superseded revision is archived and immutable.
- [ ] Withdrawal writes a tombstone with a closed reason; ids are never reused.
- [ ] `stale_ids` names exactly the seeds whose inputs changed, and is reporting only.
- [ ] `_provenance` records the resolved model, prompt versions and input hashes; no timestamp appears.
- [ ] Emit never writes outside its allowlist; authored seeds are stamped only by the explicit command.

## Open questions

None.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | medium | The write allowlist omitted `quests/`, so a generated quest anchor could never be written | fixed |
| 2 | low | `votes.confidence` admitted `unresolved`, which never reaches emit | fixed |
| 3 | low | Tombstone shape and `blocked`/`unresolved` terminal rows aligned with the contract | fixed |
| 4 | low | Canonical JSON, no timestamp, byte-identical rerun by hash, staleness by recorded key (README §6) | verified |
