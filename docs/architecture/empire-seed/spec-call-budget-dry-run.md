# Spec: `call-budget-dry-run`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `call-budget-dry-run` · **Map row:** 10 ·
**Wave:** 2
**Depends on:** `world-exemplars`, `world-name-index` (and `corpus-metrics`, whose report the dry run
runs first) · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

Before anyone approves Wave 3, the planner states exactly what a naming run will make and what it will
cost, and a dry run proves it by rendering every prompt with zero model calls. The AI-native rule applies:
*"compute the call budget before choosing a decomposition — it decides the architecture, not the
schedule"* and *"ship a `--dry-run` that renders prompts and calls nothing"* (ai-native README §9).

**Done means:**
- The committed plan carries **planned entries**. Each is a `(role, requiredSlotKind)` cell to fill,
  with every enum already drawn by the planner.
- The plan carries an invention-shaped call budget computed from its declared parts.
- `seedsmith structures plan --dry-run` renders one complete naming prompt per planned entry,
  byte-identically across reruns, with the transport stubbed to raise.

## 2. Scope and non-goals

**In scope.**
- The planner stage that draws each new entry's enums.
- The invention budget formula.
- The dry-run command.
- Replacing the classification-shaped budget.

**Not in scope.**
- The model stage (`world-namer`).
- Legion planning. `legion-seed-rows` reuses this module's planner shape over its own grids.
- Choosing how many rows to make. That is the published budget (`world-budgets`), and the planner
  reads it.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | A committed plan with `callBudget`, `targetNewRows`, `voteFields` | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:102-112`; `gk-data/packs/fusion/data/seed/structures/_plan.json` |
| Built | `check_plan` raises before any call | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:134-166` |
| Built | `briefkit.render_brief`, content-addressed and citation-refusing | `gk-forge/tools/seedsmith/seedsmith/briefkit/render.py:72`, `:82` |
| Wiring gap | The budget formula is classification-shaped: one call plus three votes on each of five fields, for every new row (`estimatedCalls = rows × stages × (1 + 5 × 3)`). The invention pipeline fixes those five fields in the planner and votes none of them | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:94-112` |
| Wiring gap | `targetNewRows` ignores `roleCountTolerance`, while `check_plan` applies it | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:105` against `:143` |
| Real gap | Planned entries with drawn enums; a prompt-rendering dry run | — |

Today's committed plan reads `targetNewRows: 0` and `estimatedCalls: 0`, because every floor equals its
count. That is a reading. After `exchange-role` publishes `budget.Exchange`, the deficit is non-zero.

## 4. Principles as they bind this module

- **The planner runs first** (base-defense decision 33; P4). No model decides what to make, which role
  it fills, which slot it sits on, or which band it takes.
- **Enums drawn, then named** (`empire-seed-ideal.md` §7 step 4). A planned entry reaches the model with
  every enum fixed. The model writes `name`, `flavor` and `reason` only.
- **Vote only what the model chooses** (ai-native README §2). For a planned invented entry, the vote set
  is **empty**. It is named and justified as empty, and never left empty by default. The
  `check_plan` rule *"a vote set must be named"* (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:162-163`)
  becomes *"a vote set must be declared, and an empty one carries its reason"*.
- **Permutation is free and deterministic.** Seeded from `(entity_id, field, sample_index)`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`), it applies only to fields a model
  selects among. With an empty vote set, no enum is offered to the model, so nothing is permuted in this
  pipeline. That is stated, not omitted.
- **Tests never call a model; the dry run proves it.**

## 5. Design

### 5.1 Planned entries

`build_plan` gains `plannedEntries: list[PlannedEntry]`. For each role with a deficit
(`max(0, budget[role] - actual[role])`), it draws that many entries:

| Field | Drawn how |
|---|---|
| `planKey` | `"{role}:{slot}:{ordinal}"`. Stable, and the provenance key (`world-namer`) |
| `role` | the deficit role |
| `requiredSlotKind` | the legal slot for that role with the fewest existing rows, ties broken by slot name |
| every other anchor enum and ordinal | from a per-role **template row** in the role registry (a hand-authored default per role), else the role's exemplar values; `structureKind` is `none` unless the registry names a kind for the role (round 6 C2: a feature role's template names the neutral `Feature`) |
| `seed` | `blake2b(plan.seed, planKey)`. Recorded, and consumed only if a future draw needs a tie-break beyond the rules above |

The draw is a pure function of `(disk rows, tuning, registry, exemplars, plan seed)`. Nothing about it
is random.

#### 5.1a A planned entry is never a template copy with a new name (round 6, audit A-ES6)

The global audit's A-ES6 finding stands as written: with `voteFields = []` the model authors identity only,
so an entry drawn wholly from a per-role template is *the template renamed* — and while its
`structureKind` is `none` it is identity-only content nothing reads. That spends naming calls on
*"a catalog for a mechanic that does not exist"* (map §2). **Decided by principle, not by an owner question**
(two repo rules decide it: a seed exists for a consumer, and a band or field with no reader is a converter
with no consumer, `gk-core/src/FusionRpg.Core/World/Bands.cs:7-8`):

1. **A deficit is planned only where the role can produce loadable content.** A deficit row is drawn only if
   the drawn entry would carry `structureKind != none` — after round 6 C2 that includes the neutral `Feature`
   for a feature role. A deficit in a role whose template names no kind is **reported, not planned**: it
   appears in the plan as `unplannedDeficits: [{role, count, reason: "no consuming structure kind"}]`, a
   reading, and it draws no `PlannedEntry`, no prompt and no naming call.
2. **A planned entry must differ from existing content in something a reader sees.** If a drawn entry is
   field-for-field equal to a row already in that role except for identity, the planner drops it and records
   it in `unplannedDeficits` with `reason: "duplicate shape"`. Renaming a template is not new content.
3. **`targetNewRows` counts only planned entries** (§5.3 unchanged), so a reported deficit never inflates
   the call budget. `check_plan` keeps failing on tolerance only, and `unplannedDeficits` is printed by
   `report`, never asserted.

The seven — now eight — feature buildings are unaffected: they are authored, need no namer
(`spec-trade-structure-rows.md` §1), and their roles meet rule 1 by construction.

### 5.2 The invention budget

```text
proofCalls      = 1                                  (constrained decoding, once per run)
namingCalls     = len(plannedEntries) × 1
repairCalls_max = len(plannedEntries) × maxRepairs   (maxRepairs = 2, ai-native README §5)
voteCalls       = len(plannedEntries) × len(voteFields) × (samples − 1)   (= 0; voteFields = [])
estimatedCalls  = { "min": proofCalls + namingCalls,
                    "max": proofCalls + namingCalls + repairCalls_max + voteCalls }
```

`maxRepairs` and `samples` are read from a `generation` block in `structure-seed` tuning (published via
`--add-key`). The plan records every term, and `estimatedCalls` is computed from them, never typed.

### 5.3 `targetNewRows` and tolerance

`targetNewRows = len(plannedEntries)`. Tolerance governs whether `check_plan` *fails*. It does not govern
what the planner *fills*. The planner fills the whole deficit, and the difference is stated in the plan's
`_meta.note`.

### 5.4 The dry run

`python -m seedsmith structures plan --dry-run --out <dir>`, a new `plan` subcommand beside `contract` in
the existing `structures` group (`gk-forge/tools/seedsmith/seedsmith/report/cli.py:2973-2981`, `:2222-2229`):

1. Runs `corpus-metrics` and `check_plan`, and stops on a closed-loop failure.
2. Builds the `NameIndex` (`world-name-index`).
3. For each planned entry, renders the naming prompt `world-namer` will send:
   - the system rules
   - the tone section (`spec-world-exemplars.md` §5.4)
   - the role's exemplars
   - the drawn enums with their descriptions and negative clauses
   - the output schema (`name`, `flavor`, `reason`)
   - a statement of the dedup input's size, not the full list. The full index goes to the validator,
     not the prompt.
4. Writes `<dir>/<planKey>.prompt.json` (canonical JSON), then prints the call budget and one line per
   entry.

With `--dry-run`, the transport is replaced by a stub that raises, so any call aborts the dry run as a
defect.

`world-namer` imports the same prompt builder, so the dry run renders what will actually be sent. A
second prompt builder is the drift this prevents.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith structures plan --dry-run --out $env:TEMP\structures-dry-run
python -m seedsmith.adapters.structures.planner            # writes _plan.json with plannedEntries
python -m pytest gk-forge/tools/seedsmith/tests/test_structure_planner.py tools/seedsmith/tests/test_structure_dry_run.py -q
```

## 7. Acceptance (contract level)

1. `estimatedCalls.min` and `.max` equal the §5.2 formula over the plan's own recorded terms. The test
   recomputes; there are no literals.
2. `len(plannedEntries) + Σ unplannedDeficits.count == Σ_role max(0, budget[role] − actual[role])`, a
   reconciliation against tuning and disk (round 6 §5.1a: a deficit is either planned or reported, never
   dropped).
3. Every planned entry's `(role, requiredSlotKind)` is in `legalRoleSlotPairs`, and every drawn enum is
   a member of its vocabulary.
4. The dry run writes exactly one prompt per planned entry and makes **zero** model calls. The transport
   stub raises, and the offline network guard is active.
5. Two dry runs over unchanged inputs produce byte-identical prompt files, and so do two plan builds.
6. `voteFields` is `[]`, with a `voteFieldsReason` string in the plan, and `check_plan` accepts an empty
   vote set only when the reason is present.
7. No test asserts a prompt's text beyond structural presence: the tone section present, the exemplar
   present, the enum list present, no citation.
8. (Round 6, A-ES6) **No planned entry is unreadable or a renamed template.** Every `PlannedEntry` would
   carry `structureKind != none`, and none is field-for-field equal to an existing row of its role except for
   identity. Every deficit not planned appears in `unplannedDeficits` with one of the two declared reasons,
   and `len(plannedEntries) + Σ unplannedDeficits.count` reconciles to the deficit sum of criterion 2 (which
   becomes that reconciliation).

## 8. Test plan and verification boundary

`test_structure_planner.py` covers criteria 1-3 and 6. The new `test_structure_dry_run.py` covers 4, 5
and 7. Fixtures use a `tmp_path` budget with a deficit so entries exist.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/structures/_plan.json` are
unmapped (`gk-core/scripts/verify-change.py:771`). The owner of the fix is `test-verification-boundary`
`python-test-lane`. The pytest command in §6 is the boundary.

## 9. Hard edges

- **The plan file's schema changes** (new keys). Its only readers are the structures adapter's legality
  function and `generate_anchor.field_options_for`, which read existing keys that are unchanged.
- **The role registry gains per-role template rows.** They are hand-authored, and a reviewer reads them
  as content. After round 6 a template that names no `structureKind` declares, by that fact, that its role
  plans nothing (§5.1a rule 1) — so a reviewer reads the absence as a decision, not an omission.

## 10. Dependencies

- Upstream: `world-exemplars` (exemplars and tone section), `world-name-index` (dedup input),
  `corpus-metrics` (the pre-run gate), `exchange-role` (the first real deficit), transitively.
- Downstream: `world-namer` (the model stage over `plannedEntries`, using this prompt builder),
  `legion-seed-rows` (same planner shape).

## 11. Open questions

None.

## 12. DESIGN-GATE §5 checklist

```
[x] Round 6 (2026-09-20): A-ES6 answered by principle in §5.1a (plan only loadable roles; never a renamed
    template; the rest is a reported reading) with criterion 8; C2's neutral `Feature` named in §5.1.
[x] Subsystems: structure planner, seedsmith structures CLI, briefkit.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: ai-native README §2, §5, §9; base-defense decision 33; planner.py in full.
[x] decisions.md: no lock beyond decision 33 (quoted).
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: the classification-shaped formula; tolerance ignored in targetNewRows.
[x] Read surrounding sections.
[x] Tested: read the committed plan (targetNewRows 0, estimatedCalls 0).
[x] No §2 invariant contradicted.
[x] Correction propagated: map §11 item 3 (density is a reading, not an input) holds here.
[x] No population pin; every count is a reconciliation.
[x] No cache, no ordering dependence (criterion 5), no actor magnitude.
[x] SOLID: one prompt builder shared by the dry run and the namer.
[ ] New rule registry row: none.
```
