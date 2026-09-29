# Seedsmith: Demons Pipeline Reference

The demon corpus pipeline (`seedsmith demons`) is responsible for species anchor extraction, classification, motif derivation, and effect authoring.

Demon generation follows the strict rule: **Seed $\rightarrow$ Concrete $\rightarrow$ Per-Player**. Species stats are deterministic and shared; effects roll per player at runtime.

---

## 1. Overview of the Demon Pipeline Stages

```
1. Dump Ingest (C# / Almanacs)
       │
       ▼
2. Preflight Checks & Contract Audit
       │
       ▼
3. Power-Parse & Threat-Banding (model-free)
       │
       ▼
4. Family Extraction & Consolidation (LLM)
       │
       ▼
5. Motif & Anti-Motif Derivation (model-free)
       │
       ▼
6. Anchor Classification Run-Control (LLM majority vote)
       │
       ▼
7. Commander & Species Effects Generation (LLM + constraints)
```

---

## 2. Preflight, Contracts, and Audits

Before running any model-based classification, execute the nine run-readiness preflight checks:

```bash
# Full preflight readiness check:
python -m seedsmith demons preflight

# Output as JSON:
python -m seedsmith demons preflight --json

# CI escape hatch (checks 1-4, 7-9 only; model endpoints skipped):
python -m seedsmith demons preflight --skip-model
```

### JSON Schema Contract & Smuggling Audit:
```bash
# Print species anchor JSON Schema:
python -m seedsmith demons contract --print

# Run numeric smuggling audit (exits 1 on finding):
python -m seedsmith demons contract --audit
```

---

## 3. Power-Parsing & Threat-Banding (Model-Free)

Derives numeric power seeds and threat rungs from raw game dump data with zero model calls:

```bash
# Parse power seeds and print basis histogram:
python -m seedsmith demons power-parse --dump data/seed/demons/_dump --report

# Compute threat rungs (Theta offsets) and print rung histogram:
python -m seedsmith demons threat-band --dump data/seed/demons/_dump --histogram
```

---

## 4. Family Vocabulary Extraction & Consolidation

Extracts demon families from name and description, consolidating into an append-only vocabulary:

```bash
# Preview extracted families (dry-run):
python -m seedsmith demons families --dry-run

# Commit consolidated families:
python -m seedsmith demons families --write --i-have-read-the-append-only-note
```

---

## 5. Motif & Anti-Motif Derivation

Re-derives motifs and anti-motifs per demon using Chinese word segmentation (`jieba`) and rule-based derivation:

```bash
python -m seedsmith demons motifs
```

---

## 6. Anchor Classification Run-Control

The anchor classification pipeline runs 3-sample permuted enum votes to determine demon properties (element, role, archetype, aptitude, traits).

Use the `run` command to manage execution:

```bash
# Check current classification run status:
python -m seedsmith demons run status

# Machine-readable status:
python -m seedsmith demons run status --json

# Start anchor classification for all species:
python -m seedsmith demons run start --all --workers 4

# Run for a specific side (plant or zombie):
python -m seedsmith demons run start --side plant --workers 4

# Run for a specific demon family:
python -m seedsmith demons run start --family aquatic --workers 4

# Run for specific species:
python -m seedsmith demons run start --species peashooter,conezombie

# Pause, Resume, Cancel:
python -m seedsmith demons run pause
python -m seedsmith demons run resume --workers 4
python -m seedsmith demons run cancel

# Re-run only stale entries (where inputs changed):
python -m seedsmith demons run rerun --stale

# Re-run only unresolved fields (where a 1-1-1 vote occurred):
python -m seedsmith demons run rerun --unresolved

# Fix unresolved fields using heuristic tie-breakers:
python -m seedsmith demons run fix-unresolved --dry-run

# Fix secondary element from fusion recipes:
python -m seedsmith demons run fix-secondary-from-fusion --dry-run
```

---

## 7. Demon Roster Metrics & Audits

Verify the overall shape of the generated anchors:

```bash
# Run roster-shape metrics:
python -m seedsmith demons metrics

# Print 21x12 element-aptitude grid occupancy:
python -m seedsmith demons metrics --grid

# Print threat-audit open-loop review queue:
python -m seedsmith demons metrics --queue

# Compare classifications against compiled legacy catalogs:
python -m seedsmith demons diff-legacy --legacy path/to/legacy-catalog.json
```

---

## 8. Effect Generation

### Commander Effects
Generate commander passive aura effects based on species anchor, motifs, and aptitude:

```bash
# Dry run for a single demon:
python -m seedsmith demons generate --kind commander-effect --only peashooter --dry-run

# Generate for stale motifs:
python -m seedsmith demons generate --kind commander-effect --stale --workers 2

# Force regenerate all commander effects:
python -m seedsmith demons generate --kind commander-effect --force --workers 4
```

### Species Effects
Authored picks and bindings between species anchors and the affix catalog live under `seedsmith.adapters.demons.effects` and batch scripts (e.g. `run_t53_claude_propose.py`).
