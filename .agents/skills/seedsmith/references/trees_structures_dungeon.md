# Seedsmith: Passive Trees, Structures & Party Dungeon

This reference covers the pipelines for Passive Skill Trees, Base-Defense Structures, and Party-Dungeon Delve content.

---

## 1. Passive Skill Trees (`seedsmith trees`)

Passive trees are generated in three distinct phases: **Plan** (deterministic cell quotas & manifest), **Generate** (model-driven node authoring within strict quotas), and **Review / Census** (audit against power budgets).

### A. Tree Planning (`trees plan`)
```bash
# Check existing tree plan against committed manifest:
python -m seedsmith trees plan --check --tree might

# Emit a tree plan:
python -m seedsmith trees plan --emit --tree might

# Operate across the full manifest (plan.v1.json):
python -m seedsmith trees plan --manifest --emit

# Diff two plans to view quota and budget shifts:
python -m seedsmith trees plan --diff plan.old.json plan.new.json
```

### B. Tree Node Generation (`trees generate`)
```bash
# Preview node generation and gate report (dry-run):
python -m seedsmith trees generate --tree might --dry-run

# Inspect a rendered sample brief:
python -m seedsmith trees generate --tree might --sample-brief

# Generate nodes for a tree with local model:
python -m seedsmith trees generate --tree might --write --workers 4

# Generate across all trees:
python -m seedsmith trees generate --all --write --workers 4
```

### C. Tree Review & Census (`trees review`)
```bash
# Run a census on a review lot:
python -m seedsmith trees review --lot lot-01 --census
```

### D. Species Trees Batch Runner
Species-specific passive trees are handled via `_j9_batch_run.py`:
```powershell
cd gk-forge/tools/seedsmith
python _j9_batch_run.py 30    # runs batch over first 30 species
```

---

## 2. Base-Defense Structures (`seedsmith structures`)

Base-defense structures represent obstacles, emplacements, yields, and defense installations.

### Schema Contract & Numeric Smuggling Audit:
```bash
# Print structure anchor JSON schema:
python -m seedsmith structures contract --print

# Run numeric smuggling audit (structures hold identity and roles, not numbers):
python -m seedsmith structures contract --audit
```

### Anchor & Corpus Generation:
Modules under `seedsmith.adapters.structures`:
- `generate_anchor.py`: Authors structure anchors with 3-sample majority vote on roles, acquisition paths, and strength bands.
- `generate_corpus.py`: Generates the 25-structure corpus (obstacles and economic roles) into `gk-data/packs/fusion/data/seed/structures/`.

---

## 3. Party Dungeon (`seedsmith.adapters.dungeon`)

Party-dungeon content is generated for Delve runs and dungeon crawl sequences. Content is partitioned into 5 domains:

1. **Rooms**: Grid cells with climate, terrain, and hazards (`briefs.build_room_brief`).
2. **Encounters**: Combat formations, threat bands, and enemy rosters (`briefs.build_encounter_brief`).
3. **Events**: Non-combat decisions, altars, merchants, and discoveries (`briefs.build_event_brief`).
4. **Quests**: Dungeon-specific run objectives and rewards (`briefs.build_quest_brief`).
5. **Supply Extensions**: Camp supplies, provisions, and delve tool kits (`briefs.build_supply_ext_brief`).

### Running Dungeon Schema Audits:
```python
from seedsmith.adapters.dungeon import DungeonAdapter

adapter = DungeonAdapter()
findings = adapter.audit()
for f in findings:
    print(f)
```

### Dungeon Corpus Emission:
Generated entries are emitted as individual JSON documents with indexed directories via `emit.write_corpus`:
```text
gk-data/packs/fusion/data/seed/dungeon/
├── rooms/
│   ├── _index.json
│   └── <roomId>.json
├── encounters/
├── events/
├── quests/
└── supplies/
```
All emitted files stamp `_provenance` (`stalenessKey`, `briefHash`, `modelId`) for automated staleness tracking.
