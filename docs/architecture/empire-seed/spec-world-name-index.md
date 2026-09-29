# Spec: `world-name-index`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `world-name-index` · **Map row:** 8 ·
**Wave:** 2
**Depends on:** `structures-adapter` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

One deterministic index of every existing name across every registered seed corpus, normalised one way,
which every naming call receives as its dedup input. The prior art is measured: a current model given 100
identical prompts named a developer "Marcus Chen" 100 times out of 100 (`empire-seed-ideal.md` §5.4).
Per-draft validation cannot see a corpus-level collision. `name_collision`'s own docstring records that
lesson three times over (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:69-86`).

**Done means:**
- `build_name_index()` returns the union of names on disk across every adapter that declares a corpus
  root, normalised and sorted.
- Building it twice is byte-identical.
- A new corpus joins by registering its adapter, with no edit to the index code.
- It calls no model.

## 2. Scope and non-goals

**In scope.** The index builder, the one normalisation function, a committed rendering of the index for
review, a `--check` drift mode, and the two optional adapter attributes it reads.

**Not in scope.**
- IP terms. `ip-censor`'s `avoid-list` owns them, and the tone section renders them
  (`spec-world-exemplars.md` §5.4). The index is dedup input only.
- Semantic near-duplicates. `SemanticDedup` already covers them
  (`gk-forge/tools/seedsmith/seedsmith/metrics/dedup.py:122`) and `corpus-metrics` runs it. This index is exact
  after normalisation.
- The narrative display-name registry. `narrative-seed` `names-registry` owns
  `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`. When the `narrative` adapter registers with a corpus
  root, its names join here with no code change.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | `name_collision(draft, {"takenNames": …})`, an exact-string check against a caller-supplied list | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:69-97` |
| Built | `SemanticDedup` over names and declared `dedup_fields` | `gk-forge/tools/seedsmith/seedsmith/metrics/dedup.py:122`; `gk-forge/tools/seedsmith/seedsmith/adapters/base.py:53-61` |
| Built | `Entry.name`, the entry's `name` or its id | `gk-forge/tools/seedsmith/seedsmith/corpus/model.py:51-53` |
| Built | The decision-43 normalisation (`[^a-z0-9]` stripped, lowercase) | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:249-250` |
| Wiring gap | Each generator assembles its own `takenNames` from its own corpus only. Example: commander effects gather siblings' names | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_commander_effects.py:125` |
| Real gap | A cross-corpus index | — |

## 4. Principles as they bind this module

- **P4: the plan is deterministic.** The index is a pure function of files on disk. There is no clock
  and no unordered iteration.
- **P5: feature knowledge lives in adapters.** The index reads each corpus through its adapter's own
  loader and knows no family.
- **A guardrail validates the contract** (`validation-ssot.md` §2). The acceptance is reconciliation
  (the index equals the union computed independently) and determinism, never a name count.
- **No model.**

## 5. Design

### 5.1 Adapter attributes (optional, duck-typed)

- `corpus_root: str`: the repository-relative default root (`"gk-data/packs/fusion/data/seed/structures"`,
  `"gk-data/packs/fusion/data/seed/items"`, …). An adapter without it does not contribute. `stub` never does.
- `load_corpus(root)`: the loader hook from `structures-adapter` §5.4. Without it, `Corpus.load(root)`
  is used.

Adding `corpus_root` to the five real adapters (`items`, `creatures`, `actions`, `dungeon`,
`structures`) is the only change outside `briefkit`. It is additive, and each is one line.

### 5.2 Normalisation: one function

`briefkit.names.normalize_name(s) = re.sub(r"[^a-z0-9]", "", s.casefold())`. That is the same rule as the
decision-43 guard, which then imports this function instead of keeping its own copy. The empty string is
never an index key.

### 5.3 The builder

```python
def build_name_index(repo_root: Path) -> NameIndex:
    # for adapter_name in sorted(ADAPTERS): adapter = resolve_adapter(name)
    #   skip if no corpus_root; load corpus; for entry in sorted(corpus entries AND exemplars, key=(kind, id)):
    #     add (normalize_name(entry.name), adapter_name, entry.kind, entry.id)
    # return NameIndex(keys=sorted set, owners=dict key -> sorted list of (adapter, kind, id))
```

Exemplar names are included, so a generated row never copies an example.

**Variant names are names (round 4, 2026-09-19).** A structure row's tiers are `variants` entries with their
own `name` (`spec-trade-structure-rows.md` §5.4 — for example the Storehouse row's *Warehouse* and *Granary
Complex*). The structures adapter yields each variant as an extra `(name, adapter, kind, id#variantId)` entry,
so a later row can never take a tier's name. This is an adapter-side projection; the builder is unchanged.

`NameIndex.is_taken(name, *, except_id=None) -> bool`: `except_id` excludes the row's own entry, so a
re-validation of an accepted row does not collide with itself.

### 5.4 The committed rendering

`data/seed/_registry/name-index.v1.json` holds the sorted `owners` map, canonical JSON (sorted keys,
indent 2, `\n`). It is **generated**, not authored. It is written only by
`python -m seedsmith.briefkit.names --write`, and `--check` fails when the file differs from a fresh
build. It exists so a reviewer can see what a naming batch was deduplicated against. The namer builds the
index live and never trusts the file alone.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith.briefkit.names --write
python -m seedsmith.briefkit.names --check
python -m pytest tools/seedsmith/tests/test_briefkit_names.py gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q
```

## 7. Acceptance (contract level)

1. **Reconciliation.** The index key set equals the set of `normalize_name(name)` over every entry and
   exemplar of every adapter with `corpus_root`. The test computes that set independently by walking
   the roots.
2. **Determinism.** Two builds are byte-identical when rendered. Shuffling adapter registration order
   does not change the output.
3. **No model.** The test runs with the transport stubbed to raise and a network guard
   (`gk-forge/tools/seedsmith/tests/test_offline_guarantee.py:31-43`).
4. **Open for extension.** A fixture adapter registered in a test with `corpus_root` pointing at a
   `tmp_path` corpus appears in the index with no change to `briefkit/names.py`.
5. **One normaliser.** The decision-43 test imports `normalize_name`, and a grep finds no second
   `re.sub(r"[^a-z0-9]"` over names in `gk-forge/tools/seedsmith/`.
6. **Drift.** `--check` exits non-zero after a corpus name changes and before `--write`.
7. No test asserts a name count or a particular name.

## 8. Test plan and verification boundary

`test_briefkit_names.py` covers criteria 1-6. The decision-43 test is edited for criterion 5. All
offline.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` and `data/seed/_registry/**` are unmapped
(`scripts/verify-change.ps1:118`). The owner of the fix is `test-verification-boundary` `python-test-lane`.
The pytest command in §6 is the boundary until then. `--check` joins CI's seedsmith gates once that lane
exists.

## 9. Hard edges

- **The index covers the whole seed tree, so it is slow to build on large corpora.** The actions corpus
  alone is large (`docs/DESIGN-GATE.md` §1 actions row: `type-weights.json` 889 KB). Build once per
  naming run, not per call. The namer receives a built `NameIndex`.
- **The committed file changes whenever any corpus gains a name.** That is expected for a generated
  file. It is regenerated, never edited.

## 10. Dependencies

- Upstream: `structures-adapter` (the loader hook and the structures `corpus_root`).
- Downstream: `call-budget-dry-run` (renders the dedup input size as a reading), `world-namer` (rejects a
  taken name), `corpus-metrics` (the cross-corpus uniqueness metric reads the same index).
- Cross-map (soft): `narrative-seed` joins by registering its adapter with a `corpus_root`.

## 11. Open questions

None.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: seedsmith briefkit, adapter attributes, one seed registry file.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: ai-native README §6 (idempotency), validation-ssot, seedsmith-map P4/P5, field_echo.py.
[x] decisions.md: no lock on name dedup.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: name_collision is exact-match on a caller list; Entry.name; decision-43 normaliser.
[x] Read surrounding sections of quoted rules.
[x] Tested: none claimed.
[x] No §2 invariant contradicted.
[x] Correction propagated: none needed.
[x] No population pin.
[x] No cache (built per run), no ordering dependence (criterion 2), no actor magnitude.
[x] SOLID: one normaliser, one index, open for new corpora by registration.
[ ] New rule registry row: none.
```
