# Seedsmith: Items & Effects Pipeline Reference

The `items` and `effects` pipelines govern equipment, sets, charms, combination gear (strains and splices), unique items, consumables, materials, recipes, and secondary effect affixes.

---

## 0. Preferred path — `items fill` + `.env`

Configure `tools/seedsmith/.env` (`SEEDSMITH_LLM_*` + `SEEDSMITH_ALLOW_PRODUCTION_TREE=1`), then:

```powershell
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1 --dry-run
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1
```

That walks all eleven generate kinds in item-seedgen-map dependency order (topo-correct), caps discovered partitions, and requires `--limit` (or `--full`) for set/charm/combination so a first run cannot spend thousands of model calls. Resume via each kind's `RunLedger`. Single-kind remains:

```powershell
python -m seedsmith items generate --kind set --write
```

Empty `--endpoint` / `--out-dir` fall through to `.env` / production kind dirs. `--write` stays required on `generate`; `fill` implies write.

Eleven kinds: `set`, `charm`, `combination`, `base-type`, `enhancement-milestone`, `recipe`, `drop-table`, `gem`, `material`, `consumable`, `affix-family`. (`unique` is hand-authored — not accepted.)

---

## 1. Item Generation (`seedsmith items generate`)

The CLI provides unified planning and generation for sets, charms, combination, and passthrough kinds.

### Kind: `set`
Generates equipment sets partitioned by species or archetypal build:

```bash
# Preview plan for set items:
python -m seedsmith items generate --kind set --population species

# Generate first 5 sets (endpoint/out-dir from .env when configured):
python -m seedsmith items generate --kind set --population species --limit 5 --write

# Deterministic write using authored answers file:
python -m seedsmith items generate --kind set --population species \
  --answers answers.json \
  --out-dir gk-data/packs/fusion/data/seed/items/sets \
  --allow-production-tree \
  --write
```

### Kind: `charm`
Generates accessory charms:

```bash
python -m seedsmith items generate --kind charm --population species
python -m seedsmith items generate --kind charm --population species --limit 5 --write
```

### Kind: `combination`
Generates combination gear across the 12 aptitudes and 3 archetypes:
- **`strain`**: 36 Strains (12 aptitudes $\times$ 3 archetypes).
- **`splice`**: 66 Splices ($C(12, 2)$ pairwise combinations).

```bash
# Validate dependencies before generation:
python -m seedsmith items validate --deps

# Preview strain combination generation:
python -m seedsmith items generate --kind combination --shape strain

# Execute live (defaults from .env):
python -m seedsmith items generate --kind combination --shape strain --write
```

---

## 2. Passthrough kinds (same `items generate --kind …`)

These modules also run through the unified CLI (and `items fill` discovers their partitions where applicable):

- **`base-type`**, **`enhancement-milestone`**, **`recipe`**, **`drop-table`**, **`gem`**, **`material`**, **`consumable`**, **`affix-family`**
- **`uniques`** stay hand-authored — not a `--kind` choice

---

## 3. Effects & Affix Generation (`seedsmith effects`)

The effects pipeline authors named affix bundles from the closed atom vocabulary (9 attach points, 18 kinds, 13 triggers).

```bash
# Preview drawing a random affix bundle:
python -m seedsmith effects generate --kind affix --dry-run

# Generate affixes narrowed to specific atom IDs:
python -m seedsmith effects generate --kind affix --only atom.damage.phys,atom.bleed.proc --dry-run

# Generate affixes with a thematic bias:
python -m seedsmith effects generate --kind affix --theme "frost-and-decay" --count 5 --dry-run

# Author species-specific affixes (affix.species.<speciesId>.*):
python -m seedsmith effects generate --kind affix --species-id peashooter --count 3 --dry-run

# Live generation against local model:
python -m seedsmith effects generate --kind affix \
  --count 10 \
  --endpoint http://localhost:1234/v1/chat/completions \
  --model google/gemma-4-26b-a4b-qat
```

### Constraints & Quality Rules:
- An affix is a named bundle of atom references and condition attachments.
- Affixes never author concrete numeric damage/healing values. Values resolve at runtime via `Instantiator.Draw`.
