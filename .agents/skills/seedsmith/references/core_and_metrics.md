# Seedsmith: Core Commands & Metrics

The core commands in `seedsmith` provide validation, health measurement, and tuning adjustment across all corpora without executing LLM generation models.

---

## 1. `seedsmith check`

Run the metric suite against a seed corpus directory.

```bash
# Run local checks on an items corpus:
python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items

# Run checks on action seeds:
python -m seedsmith check gk-data/packs/fusion/data/seed/actions --adapter actions

# Run checks on demon seeds:
python -m seedsmith check data/seed/demons --adapter demons

# Scoped check for passive trees:
python -m seedsmith check --family PassiveTree

# Filter by a specific metric ID:
python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items --metric EmptyPartition

# Export findings to JSON:
python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items --json findings.json
```

### Arguments & Flags:
- `corpus_root`: Path to the seed directory (e.g. `gk-data/packs/fusion/data/seed/items`, `gk-data/packs/fusion/data/seed/actions`). Optional when `--family` is used.
- `--adapter`: Name of the registered adapter (`stub`, `items`, `demons`, `actions`, `dungeon`). Default is `stub`.
- `--gate`: CI-safe mode. Exits non-zero (`1`) **only** if a `GAP` finding originates from a metric with `gates=True` (calibrated and promoted in CI). Without `--gate`, any `GAP` exits `1`.
- `--family <name>`: Family-scoped check (e.g. `PassiveTree`), bypassing `corpus_root`.
- `--plan-root <dir>`: Used with `--family PassiveTree` to override the plan directory (default `gk-data/packs/fusion/data/seed`).
- `--metric <id>`: Repeatable flag to run only specified metric IDs.
- `--json <path>`: Write structured machine-readable findings to a JSON file.

### Finding Severity Levels:
- **`[GAP]`**: A violation of a structural rule, empty partition, broken link, or unfulfilled budget requirement.
- **`[NOTE]`**: Informational advisory finding or open-loop item.
- **`[NOT_MEASURED]`**: The metric requires a context (e.g. `numerics`, `budget`, or `demon_dump`) that was not provided in this run.

---

## 2. `seedsmith report`

Executes the **full metric registry**, evaluating both the file corpus and demon anchor/dump trees.

```bash
python -m seedsmith report \
  --corpus gk-data/packs/fusion/data/seed/items \
  --adapter items \
  --demon-dump data/seed/demons/_dump \
  --demon-anchors data/seed/demons/species
```

### Arguments:
- `--corpus <dir>`: Seed corpus directory.
- `--adapter <name>`: Registered adapter.
- `--demon-dump <dir>`: Corpus-dump tree root (defaults to `data/seed/demons/_dump`).
- `--demon-anchors <dir>`: Emitted species anchor tree root (defaults to `data/seed/demons/species`).
- `--gate`, `--json`, `--metric`: Same as in `check`.

---

## 3. `seedsmith metrics`

Lists all registered metrics in the registry and their configuration status.

```bash
# List all registered metrics:
python -m seedsmith metrics

# Check Appendix-A coverage status (claimed / known gap / unclaimed):
python -m seedsmith metrics --coverage
```

### Registered Metric Families:
- **Coverage**: `EmptyPartition`, `PairwiseHole`, `DemonUncovered`, `BasisHistogram`, `DumpCompleteness`.
- **Linkage**: All referential integrity metrics (`RefValid`, `ReverseIndex`, `Acyclic`, `OrphanEdge`).
- **Balance & Numerics**: `LadderInversion`, `OutOfEnvelope`, `CellDeviation`, `Evenness`, `Inequality`.
- **Quality & Content Completeness**:
  - `ContentFieldMissing` / `ContentFieldStale` / `ContentLanguageContamination`
  - `FlavourMissing` / `FlavourGeneric`
  - `SemanticDedup` / `ExemplarConformance`
- **Demon Roster**: `AptitudeDistribution`, `ThreatBandOccupancy`, `FamilySizeSpread`, `GridFill`, `PostureBalance`, `RarityMonotonicity`, `SingleElementShare`, `UnresolvedCount`.
- **Passive Tree**: `TreeEqualValue`, `CellOccupancy`, `MechanismRamp`, `NearDuplicate`, `QuotaDrift`, etc.

---

## 4. `seedsmith numerics`

Tools for inspecting and rebalancing tier bands (`tier-bands.v{n}.json`) without editing code numbers directly (strictly adhering to `docs/architecture/tunables-ssot.md`).

```bash
# Preview rebalancing a channel weight ratio:
python -m seedsmith numerics rebalance --set channelWeight.atk=1.15

# Preview rebalancing multiple values from a file:
python -m seedsmith numerics rebalance --set-file tuning-changes.txt

# Publish changes into the next tier-bands version (tier-bands.v{n+1}.json):
python -m seedsmith numerics rebalance --set baseShare=0.25 --publish
```

### Arguments:
- `--set <KEY=VALUE>`: Repeatable ratio override (e.g. `channelWeight.<id>=<ratio>` or `baseShare=<ratio>`). Note: `1.0` equals $1000‰$.
- `--set-file <PATH>`: Batch file of `KEY=VALUE` lines with comments (`#`).
- `--publish`: Writes the new incremented version file `tier-bands.v{n+1}.json` for review; preserves the prior version for rollback.
