# BCU2.11 / ISG-gap-2 — the 911-partition residue, mapped

Lane `cmdc/bcu8-4` (fence: `gk-core/src/FusionRpg.Data/**`, `gk-core/tests/FusionRpg.Data.Tests/**`,
`tasks/backlog-clean-up-todo.md`, its ledger, `tasks/data-test-substrate-todo.md`, `tasks/reports/**`,
`scripts/**`). Base `3e7a51d16`. Owner of the row: `tasks/item-seedgen-todo.md` ISG-gap-2.

ISG-gap-2's acceptance is *"either the EmptyPartition count drops … **or** the residue is enumerated
partition-by-partition with a reason per partition"*. The merge it was gated on never happened
(`ea2aeb756` reverted `corpus/bcu211`: 956 files, −130,881), so this is the enumeration. It is
model-free; nothing here writes under `data/`.

## The reading

```
cd gk-forge/tools/seedsmith && PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items \
    --metric Coverage/EmptyPartition --json ../../tasks/reports/ISG-gap-2-residue.json
→ 911 findings
```

All 911 are named, with their metric evidence, in `tasks/reports/ISG-gap-2-residue.json`
(`metrics/coverage.py:23-46`'s own `Finding` records). Grouped by the allocation kind:

| group | allocated | empty | empty partitions |
|---|---:|---:|---|
| `set` — `sets/species/<id>` | 904 | **904** | one per roster species (`sets/species/abyssswordstar` … `sets/species/zombieloonnut`) |
| `set` — build/theme families | 41 | 1 | `sets/might-offense` |
| `attribute` | 1 | 1 | `attributes` |
| `base-type` | 62 | 2 | `base-types/manipulator/humanoid/b`, `base-types/mantle/humanoid/a` |
| `display-template` | 6 | 3 | `display-templates/4`, `/5`, `/6` |
| **total** | 1,069 | **911** | |

## Where "allocated" comes from, and the reason per partition

`Coverage/EmptyPartition` is a set difference between the adapter's allocated set and the corpus's
occupied partitions — *"allocated is adapter knowledge, not corpus knowledge"*
(`gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py:9-14`), read from the items adapter's own snapshot:

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/registries.py:14` — `SNAPSHOT_PATH =
  …/items/_registry_snapshot/allocated_partitions.json`.
- That snapshot's `_meta` names its source and its regeneration:
  `dotnet run --project gk-forge/tools/ItemSeedValidator -- --list-partitions-json gk-data/packs/fusion/data/seed/items`
  (`refresh_allocated_partitions.py --write`), captured 2026-09-21 — i.e. the allocation rule is
  `KindCatalog.cs` + `naming.v1.json`, per kind, not a corpus fact.

So the reason each named partition is in the residue is the reason its group is:

| partitions | reason (each named partition carries this one) |
|---|---|
| the 904 `sets/species/<id>` | The kind's allocation rule reserves a species-scoped set partition for **every** roster species; none holds an entry. The only fill attempt, BCU2.11's reverted run, produced **747 `SemanticDedup/NearDuplicate`** findings against these partitions rather than 904 distinct entries — so this residue is a generation-quality defect, not an unstaffed slot. |
| `sets/might-offense` | A build-family set partition the other build families filled (40 occupied family/theme partitions) and this one did not. |
| `attributes` | The `attribute` kind's single allocated partition; the corpus holds no `attribute` row. |
| `base-types/manipulator/humanoid/b`, `base-types/mantle/humanoid/a` | Two of the 62 allocated base-type frame/race/slot partitions; the other 60 are occupied. |
| `display-templates/4,5,6` | Three of the 6 allocated template index slots; the other three are occupied. |

## Correction (same lane, next commit) — the residue is mostly a KEY mismatch, not 911 unfilled slots

The table above stops one measurement too early. Comparing the two id spaces directly
(`PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-11-partition-key-map.py --out tasks/reports/ISG-gap-2-per-partition.json`)
splits the 911 into:

| group | count | what it is |
|---|---:|---|
| `species-slot-key-mismatch` | **844** | the set entry EXISTS, under the other spelling — `counterpartPartition` names it in the per-partition JSON |
| `species-no-set-entry` | 60 | no set entry for that species under either spelling (variant/`_a` ids and enum-shaped ids dominate) |
| `set-family-unfilled` | 1 | `sets/might-offense` |
| `attribute-kind-empty` | 1 | `attributes` |
| `base-type-frame-empty` | 2 | `base-types/manipulator/humanoid/b`, `base-types/mantle/humanoid/a` |
| `display-template-slot-empty` | 3 | `display-templates/4,5,6` |

The two spellings, each read at its source:

- **allocation** — `gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261`
  `Add(kind, $"{kind.Directory}/species/{speciesId}", $"set.{idSlug}-", …)`: the PARTITION keeps the raw
  `speciesId` (`sets/species/elephantzombie_a`), while the ID PREFIX hyphenates it
  (`set.elephantzombie-a-`) — the method's own doc comment (lines 250-259) explains the hyphenation for
  the prefix, and the partition path kept the raw id.
- **emission** — `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/authored.py:99-100`: a set's partition is
  its own id's body minus the numeric tail, so `set.elephantzombie-a-001` lands in `sets/elephantzombie-a`
  and `set.might-offense-001` in `sets/might-offense`. No `species/` segment, hyphenated slug.

Measured consequences, all model-free on the same corpus:

- of the 904 allocated `sets/species/<id>` slots, **844** have a same-species set entry under the other
  spelling; **60** have none. Folded to one key (lowercase, alphanumerics only) there are **zero slug
  collisions**, so the corrected key stays unambiguous.
- Re-reading the metric with the allocation key corrected gives a residue of **67**, not 911 — the 60
  genuine absences plus the 7 non-species slots (`projectedEmptyUnderCorrectedSpelling` in the JSON).
- This also explains the reverted run: a fill aimed at `sets/species/<id>` would have written the same
  species' sets a second time under a different key — the shape of the **747 `SemanticDedup/NearDuplicate`**
  findings that got the corpus reverted (`ea2aeb756`). The metric that fired lives in
  `gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py:9-14` (*"allocated is adapter knowledge"*), and the
  adapter's knowledge is the C# tool's snapshot — so nothing in the corpus side could see the clash.

## The question this map hands to `item-seedgen` (owner)

Which spelling is canonical — fix the allocation key (`NamespaceAllocation.cs:261`, then regenerate the
snapshot with `refresh_allocated_partitions.py --write`) or the emitter's partition key
(`setgen/authored.py`, which would move 844 corpus partitions)? Both sides are outside lane
`cmdc/bcu8-4`'s fence (`gk-forge/tools/ItemSeedValidator/**`, `gk-forge/tools/seedsmith/**`), and this is a contract call,
not a fill: **do not** resolve it by filling the 904 slots, which is what produced the near-duplicates.
