# Seedsmith: Action Corpus 15-Stage Pipeline Reference

The `action-corpus` pipeline authors creature action seeds across three eligibility tiers:
1. **General**: Any creature can hold. Role and mechanical slot only, no anchor required.
2. **Family**: Actions representing one of the demon families (motifs, anti-motifs, themes).
3. **Signature**: Actions unique to one species (motifs, element, and family actions).

Action seeds contain **pool references**, never concrete numbers or layer-4 rolled values.

---

## 1. Complete 15-Stage Execution Sequence

For a complete run, use the orchestrator. It reads the live seed roster through A-S0, uses the
current full plan, fills each proposal partition in resumable batches, validates before signature
assembly, and then runs the deterministic selection stages:

```powershell
python -m seedsmith.adapters.actions.generate_action_pipeline --batch-size 25 --max-passes 8
```

The command is safe to restart. Existing `accepted`, `blocked`, and `escalated` proposal rows are
kept; unresolved rows are retried in brief order. Use `--fresh` only when intentionally replacing
the first proposal batch. Preview the entire dependency sequence without model calls with:

```powershell
python -m seedsmith.adapters.actions.generate_action_pipeline --dry-run --batch-size 25
```

The `--dry-run` path is a wiring and provenance check. It does not create the full LLM corpus and
does not make a failing coverage report pass.

| Stage | Script / Module | Nature | Output |
|:---:|---|:---:|---|
| **A-S0** | `generate_characteristic_pool.py` | Model-free | `gk-data/packs/fusion/data/seed/actions/_generated/role-lean.json` |
| **A-S1** | `generate_distribution_planner.py` | Model-free | `data/seed/actions/_briefs/round-<n>.json` |
| **A-S7** | `generate_coverage_assignment.py` | Model-free | Injected atom family per brief (roster balance) |
| **A-T1** | `generate_type_weights.py` | Model-free | `gk-data/packs/fusion/data/seed/actions/type-weights.json` |
| **A-S2** | `generate_brief_assembly.py` | Model-free | Signature briefs enriched with accepted `familyActions` |
| **A-P1** | `generate_general_actions.py` | **LLM** | `_candidates/general/round-<n>.json` |
| **A-P2** | `generate_family_actions.py` | **LLM** | `_candidates/family/round-<n>.json` |
| **A-P3** | `generate_signature_actions.py` | **LLM** | `_candidates/signature/round-<n>.json` |
| **A-S4a** | `generate_validate_heal.py` | Mixed (Repair) | First validation of general and family candidates |
| **Collate** | `generate_candidate_assembly.py` | Model-free | Combined candidate set for validation |
| **A-S4b** | `generate_validate_heal.py` | Mixed (Repair) | Final `_rounds/round-<n>/` (accepted, healed, rejected) |
| **A-S3** | `generate_dedup_select.py` | Model-free | Hard hash deduplication + token-overlap advisory |
| **A-S6** | `generate_innate_picker.py` | Model-free | `species-innate.json` (one innate per species) |
| **FC1** | `generate_usage_stats.py` | Model-free | Family usage & distribution analytics |
| **A-S5** | `generate_coverage_report.py` | Model-free | `_reports/coverage-round-<n>.json` |
| **Backfill** | `generate_action_descriptions.py` | Model-free / LLM | Authored flavour text backfill |

---

## 2. Model-Free Foundation Steps (A-S0 to A-T1)

Run these before any model calls:

```powershell
# 1. Generate characteristic pool & species role lean (A-S0):
python -m seedsmith.adapters.actions.generate_characteristic_pool

# 2. Generate Engine 1 distribution plan & round briefs (A-S1):
python -m seedsmith.adapters.actions.generate_distribution_planner --round 1

# 3. Generate type weights (A-T1):
python -m seedsmith.adapters.actions.generate_type_weights

# 4. Run guaranteed coverage assignment (A-S7):
python -m seedsmith.adapters.actions.generate_coverage_assignment --round 1
```

---

## 3. Proposal Stages (A-P1, A-P2, A-P3)

Each generation stage supports `--dry-run` and `--count <N>`:

```powershell
# General Actions (A-P1):
# Preview assembled briefs:
python -m seedsmith.adapters.actions.generate_general_actions --dry-run
# Generate first 5 general actions:
python -m seedsmith.adapters.actions.generate_general_actions --count 5

# Family Actions (A-P2):
python -m seedsmith.adapters.actions.generate_family_actions --dry-run
python -m seedsmith.adapters.actions.generate_family_actions --count 5

# Brief Assembly for Signature Actions (A-S2):
# Must run AFTER family actions are accepted, so signatures know their family context:
python -m seedsmith.adapters.actions.generate_brief_assembly --round 1

# Signature Actions (A-P3):
python -m seedsmith.adapters.actions.generate_signature_actions --dry-run
python -m seedsmith.adapters.actions.generate_signature_actions --count 5
```

For manual staged work, add `--resume` to continue an interrupted partition. The orchestrator
passes it automatically and assigns candidate IDs from the global brief index, so later batches do
not overwrite earlier rows or restart at `candidate.*.001`.

---

## 4. Collation, Validation, Deduplication, and Promotion

After candidate generation, run the pipeline filters:

```powershell
# 1. Assemble candidate outputs:
python -m seedsmith.adapters.actions.generate_candidate_assembly --round 1

# 2. Schema audit, quality gates, and self-repair (A-S4):
python -m seedsmith.adapters.actions.generate_validate_heal --round 1

# 3. Deduplication and final selection (A-S3):
python -m seedsmith.adapters.actions.generate_dedup_select --round 1

# 4. Promote Innate actions per species (A-S6):
python -m seedsmith.adapters.actions.generate_innate_picker

# 5. Review usage statistics and generate coverage report (A-S5):
python -m seedsmith.adapters.actions.generate_usage_stats
python -m seedsmith.adapters.actions.generate_coverage_report --round 1
```

---

## 5. Description Backfill

Backfill authored descriptions for action seeds lacking flavour text:

```powershell
# Check missing descriptions:
python -m seedsmith check gk-data/packs/fusion/data/seed/actions --adapter actions --metric Content/FieldMissing

# Run description generator / backfill:
python -m seedsmith.adapters.actions.generate_action_descriptions --dry-run
python -m seedsmith.adapters.actions.generate_action_descriptions --write
```
