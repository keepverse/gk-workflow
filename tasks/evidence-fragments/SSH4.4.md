# SSH4.4 / SSH4.6 — the shipped corpus grants 10 families `FamilyExpansion` refuses (ROUTED)

**Measured 2026-09-22 (lane `ssh29`), not guessed.** Over the shipped `gk-data/packs/fusion/data/seed/items/combinations/**`,
against the materialised catalog (`gk-data/packs/fusion/data/seed/atoms/**/*.json`, 105 families):

```
python -c "import json,glob,collections;fams={r['family'] for f in glob.glob('gk-data/packs/fusion/data/seed/atoms/**/*.json',recursive=True) for r in json.load(open(f,encoding='utf-8')).get('entries',[]) if isinstance(r,dict) and isinstance(r.get('family'),str)};miss=collections.Counter();ent=set();[ (miss.update([g]) if g not in fams else None, ent.add(e['id']) if g not in fams else None) for f in glob.glob('gk-data/packs/fusion/data/seed/items/combinations/*.json') for e in json.load(open(f,encoding='utf-8')).get('entries',[]) for g in (e.get('grants') or []) ];print('families',len(fams),'grants',sum(1 for f in glob.glob('gk-data/packs/fusion/data/seed/items/combinations/*.json') for e in json.load(open(f,encoding='utf-8')).get('entries',[]) for g in (e.get('grants') or [])),'missingOcc',sum(miss.values()),'missingDistinct',len(miss),'entries',len(ent));print(dict(miss.most_common()))"
```

prints `families 105 grants 185 missingOcc 69 missingDistinct 10 entries 63`, then the ten families.

| Reading | Number |
|---|---|
| grants that resolve to a materialised atom family | 116 of 185 |
| **grant occurrences on a family with no atom** | **69** |
| entries affected | **63** |
| distinct missing families | **10** |

The 10, with occurrence counts: `atom.retribution` 46 · `atom.stalwart` 9 · `atom.swiftness` 4 ·
`atom.hit-retort` 4 · `atom.death-salvo` 1 · `atom.elpw-pierce` 1 · `atom.hit-followthrough` 1 ·
`atom.prec-sync` 1 · `atom.evd-brace` 1 · `atom.lifesteal` 1.

**All ten ARE authored affix families** (`gk-data/packs/fusion/data/seed/items/affix-families/*.json` — e.g. `g-ward.json`'s
`atom.stalwart`, `g-on-hit.json`'s `atom.retribution`) that `FamilyExpansion.Expand` REFUSES by name, so
`gk-data/packs/fusion/data/seed/atoms/generated/**` has no row for them. The refusals are named, not silent: e.g. `atom.stalwart`
declares `channel: "status.resist"`, a bare stem the expansion refuses because a concrete
`status.<family>.<category>` must be authored (`FamilyExpansion.cs:194-206`). `atom.swiftness` /
`atom.hit-retort` are refused for their own channel/params reasons.

## Why this is not fixed here (routing, per the brief)

- **The corpus regeneration is owner-run** (model calls) and is not a lane's to hand-edit: the fix is to
  re-author those 63 entries against a catalog that resolves every grant, then commit the generator's
  output. Hand-editing `gk-data/packs/fusion/data/seed/items/combinations/**` is forbidden.
- **The generator half belongs to `item-seed-gen` (seedsmith combogen).** `run.granted_family_vocabulary()`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py:110`) returns
  `registries.load_authored_affix_family_ids()` — the AUTHORED ids — while the consumer is
  `FamilyExpansion`'s ACCEPTED set. SSH2.1's `deps.preflight` closes the OFFERED enum against the catalog
  built from that same function, so it is tautological over the corpus and stayed green while 63 entries
  granted families no atom exists for. Closing it against `FamilyExpansion.Expand`'s accepted set (then
  regenerating) is the SSOT-correct fix; it is item-seed-gen's row, not this program's.
- **The content half belongs to the affix-family/atom program**: either those ten rows are re-authored to
  channels `FamilyExpansion` accepts, or the expansion's refusal is revisited. Naming that decision is the
  owner's, not a lane's.

## Rows this blocks (not closed by this lane)

`SSH4.4` (one acceptance set) and its dependents `SSH4.6`, `SSH4.7`, `SSH4.8`, `SSH4.9` (live probe), and
`SSH5.9` (combo-bind carries the circuit, deps SSH4.6). Each needs the corpus to resolve every grant before
its shipped-corpus test (`the_shipped_corpus_has_no_refusal` over the container build) can pass.

## Not proved / open

- The container build + boot wiring itself is NOT in the tree: SSH4.4's own note records the mechanism was
  built and held back, and nothing was committed. Building it now would leave
  `the_shipped_corpus_has_no_refusal` red on 63 entries — a red shipped test is worse than an openly
  blocked row, so it was not attempted.
- The 2026-09-20 note's family list (`atom.aura-*`, `atom.enhance-*`) is **stale**: SSH5.13's R11 re-run
  regenerated those away. The list above is the current reading.

## The parked blocked set (2026-09-22, lane `ssh29`) — all external, none actionable here

Re-read against the ledger after SSH8.5 landed. SSH8.5's derived `materials` publish moved the
combo-budget report from **47 failing cells to 0** (126 unpriced remain), so the priced half of the
`combo-budget` gate is now green and three rows' reasons are refreshed:

| Row | External dependency | State of that dependency |
|---|---|---|
| SSH4.4 | owner-run combination-corpus regeneration | **open** — 69 grant occurrences / 63 entries / 10 families; `FamilyExpandGen --check` shows each refusal is a NAMED content decision, not a generator bug |
| SSH4.6 | SSH4.4 | open |
| SSH4.7 | SSH4.6 | open |
| SSH4.8 | SSH4.7 | open |
| SSH4.9 | SSH4.8 + the live probe | open |
| SSH5.9 | SSH4.6 (no seam to build on — `ComboBindTarget`/`combosOf` absent) | open |
| SSH6.8 | a PASSING report (= SSH4.4's 126 unpriced cells) | open |
| SSH7.7 | SSH6.8 | open |
| SSH8.5 | one acceptance line: `combo-budget --report` exits 0 | open (erratum requested) |
| SSH7.1 | pipeline lane `tvb58` — an edit to `TuningRevisionLiteralGuardTests.cs`, refused by the pipeline guard | open |
| SSH8.4 | pipeline lane `tvb58` — same file | open |

SSH6.4, SSH7.8, SSH2.8, SSH2.9 are DONE (committed); re-verified at HEAD 2026-09-22:
`combo-budget --report` 70 cells / 0 failing; ItemSocketStore 13/0 + `guard-dal` OK + no `min_tier`
member left; 0 naming findings + 44 repair tests; the six `run.py:80`/`:125` citations re-anchored with
no D2/D3 finding on either doc.

## 2026-09-22 (lane `ssh29`, after the owner cleared the regeneration to run alongside J9)

**Landed: the generator half of the fix — the offer set is now the BUILDABLE set.**
`run.granted_family_vocabulary()` used to return every AUTHORED affix id (125); `FamilyExpansion.Expand`
refuses 70 of them by name, so a grant on a refused family passes the C# `ReferenceCheck` and then cannot
build its container at boot. New `registries.load_materialised_affix_family_ids()` =
`load_authored_affix_family_ids() ∩ families in gk-data/packs/fusion/data/seed/atoms/generated/**`, and `run.py`, `deps.preflight`,
`deps.validate_entries` and `grant_repair.run_batch` all use it.

| Criterion | Command | Result |
|---|---|---|
| the offer set is exactly the buildable set | `PYTHONPATH=gk-forge/tools/seedsmith python -c "..."` | offered **61**, authored 125, materialised 61; offered ⊆ the container-build atom catalog; all **10** refused grant families excluded |
| the combogen/deps/repair suites stay green | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_items_adapter.py gk-forge/tools/seedsmith/tests/test_combination_repair_ledger.py gk-forge/tools/seedsmith/tests/test_namekey_repair.py gk-forge/tools/seedsmith/tests/test_naming_grammar_repair.py -q` | **155 passed, 11 subtests** (the one updated test is `test_the_offered_grant_vocabulary_is_the_production_atom_catalog`, now asserting both consumers resolve) |

**NOT landed: the regeneration itself — the write path dies before any model call.**
`python -m seedsmith items generate --kind combination --shape splice --write --endpoint
http://localhost:1234/v1/chat/completions --out-dir _probe --overwrite combo.splice-bulwark-retribution
--allow-production-tree` exits **1 in ~1 s** with
`FileNotFoundError: [WinError 2] The system cannot find the file specified` at
`report/cli.py:1723` → `setgen/name_repair.py:109 shipped_name_keys()` → `:90 validator_keys()` →
`subprocess.run(["dotnet", "run", "--project", <validator>, "--", <items>, "--normalize-names"],
cwd=str(root.parents[2]))`. **The exact same `shipped_name_keys()` call succeeds standalone**
(`python -c "from seedsmith.adapters.items.setgen import name_repair;
name_repair.shipped_name_keys()"` → `ok keys 3931`), and the cwd it resolves to exists, so the failure is
inside the CLI process's `CreateProcess`, not the paths. The model is up (`GET /v1/models` lists
`google/gemma-4-26b-a4b-qat`), so **no contended latency could be measured — the run never reached the
model.** Owning program: **item-seed-gen (seedsmith)** — `report/cli.py`'s combination write path.

**Status of the three rows:** SSH4.4's boot mechanism (container build + upsert before the seed, accepted
set = grid-valid ∩ buildable, refusals printed and the recipe disabled) is NOT implemented — landing it
now would turn `CombinationBoot`'s own `Boot_seeds_the_real_corpus_end_to_end` (`Assert.Empty(result.Refusals)`)
and `the_shipped_corpus_has_no_refusal` red on the 63 unbuildable entries, so the corpus must be
regenerated first. SSH4.6 and SSH5.9 were not reached: both need the container rows SSH4.4 builds.

## 2026-09-22 — THE CORPUS IS REGENERATED (contended with J9, as the owner cleared)

The 63 entries that granted a refused family were re-authored by the model with the closed offer set,
in bounded batches, **in the same session as the J9 run**:

| Batch | Command (common prefix: `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith items generate --kind combination --shape <S> --write --endpoint http://localhost:1234/v1/chat/completions --model google/gemma-4-26b-a4b-qat --out-dir gk-data/packs/fusion/data/seed/items/combinations --overwrite <ids> --allow-production-tree`) | Cells | Elapsed | Contended s/cell |
|---|---|---|---|---|
| splice 1 | `--shape splice --overwrite` first 10 ids | 10 | 191 s | 19.1 |
| splice 2 | `--shape splice` ids 11–28 | 18 | 335 s | 18.6 |
| splice 3 | `--shape splice` ids 29–45 | 17 | 355 s | 20.9 |
| strain | `--shape strain` all 18 | 18 | 255 s | 14.2 |
| names | `items repair-names --write …` (6 collisions) | 6 | 52 s | 8.7 |

**Total ~19.8 min for 69 model calls ≈ 17 s/cell, contended.** (A `timeout`-wrapped invocation failed
instantly with `FileNotFoundError [WinError 2]`; without the msys `timeout` wrapper the same command
runs — that was the earlier "write path is broken" reading, now corrected: the path is fine, the wrapper
was the problem.)

**Results, all re-run after the regeneration:**

| Criterion | Command | Result |
|---|---|---|
| no entry grants an unbuildable family | `combo-budget --report` | **exit 0**, `PASS — every cell is at or under the rarity route (164 priced, 0 refused)` — the report's FIRST passing run, 0 refused |
| no combination-corpus validator errors | `dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/items --findings-json` | **0 errors in `combinations/**`** (was 35 `UnknownKey` + 6 `NameCollision`) |
| the generator keeps offering only buildable families | seedsmith suites | **279 passed / 91 subtests** |

**Two defects found and fixed on the way (both real, both in the write path):**
1. `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py`'s `combination` row still listed `grantedTier` in
   `required` AND `extra` after the C# `KindCatalog` dropped it (SSH7.5/7.6) — so the schema asked the
   model for it and `--write` re-emitted **35 rows** the C# gate then rejected as `UnknownKey`. Fixed to
   mirror the C# row; `test_the_kind_is_renamed_not_removed` now asserts its absence.
2. Six name collisions were minted across batches (the name guard checks the shipped corpus + its own
   run, not other batches) — repaired through `items repair-names --write` (SSH2.8's own tool), 6 rows.

**Still red, and NOT this lane's:** `ItemSeedValidator` reports **498 `SameStageReference` errors**, all
in `gk-data/packs/fusion/data/seed/items/base-types/**` — introduced by `f671cc5ad feat(t37): author the per-base-type armour
successor edges and regenerate the corpus` (species-gear-chain, merged in mega-merge). Owning program:
**species-gear-chain**.
