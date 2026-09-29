# BCU2.12 / J9 — the species-corpus run read at `7209d9f57`: 4 of 904 complete, and the stall is mechanical

Lane `cmdc/bcu8-4`. Owner: `tasks/passive-tree-todo.md` **J9: The species corpus run** (the run itself is
a manager-run model job — `tasks/run-board-20260920.md:1562`, `2004b5a42`, in flight; its outputs are
`gk-data/packs/fusion/data/seed/passive-tree/**`, outside this lane's fence). Everything below is model-free; nothing under
`data/` was written.

## J9's own acceptance, quoted

> **Acceptance:**
> - [ ] 840 trees × 40 nodes committed as catalog data (D45)
> - [ ] The plan regenerates byte-identically (`--check`), for species as well as the generic corpus
> - [ ] The uniqueness gate holds across all 840; no near-duplicate cluster
> **Verification:** `--check` green; the reverse index reports no cross-namespace reference.

## The progress reading

`python tasks/reports/bcu2-12-j9-progress-census.py --out tasks/reports/bcu2-12-j9-progress-census.json`

| reading | value |
|---|---:|
| roster (`_index.json`; J9's own acceptance says 840 — PT-J9-F2's stale figure) | **904** |
| species with ledger rows | 16 |
| species with a committed node file | 9 |
| species with a metadata file (codex resolved) | 8 |
| **species complete (40/40 nodes)** | **4** — `AbyssSwordStar`, `AllPeater`, `Apple`, `ArmoredImpZombie` |
| filed but short of 40 | `AcientSunNut` 39, `AshThreePeater` 39, `BalloonZombie` 39, `ArmedGargantuar` 38, `BambooDragon` 25 |
| ledger rows, no node file | **7** — `Bamboo`, `BambooFurnace`, `BambooSpruce`, `BedRockSnowZombie`, `BedRockTallNut`, `BigChomper`, `BigGatling` |

So clause 1 is red by a wide margin (4 of 904 complete; 9 of 904 filed at all), and clause 3 is red too
(`SpeciesUniqueness` **67** gaps, `NameCollision` **388/1679**, `NearDuplicate` **116/1679** — both read in
full in [bcu2-12-census.md](bcu2-12-census.md) and [bcu2-12-namecollision-finding.md](bcu2-12-namecollision-finding.md)).

## The Verify line, clause by clause — **both clauses are green**

**Correction (same lane, next commit):** an earlier revision of this page said the reverse-index clause was
red because `SpeciesUniqueness` reports findings. That conflated two clauses: the findings are the
*acceptance's* uniqueness bar, while the Verify line's reverse-index clause is specifically the
**cross-namespace** strength (U3). Split properly:

| clause | state | evidence |
|---|---|---|
| *"`--check` green"* | **green** | `dotnet run --project gk-forge/tools/TreeBinder -c Release -- --check` → exit 0, **0 `STALE`** lines (committed bound reports byte-identical to a fresh run, `gk-forge/tools/TreeBinder/Program.cs:131-141`); and `python -m seedsmith trees plan --check --manifest` → *"byte-identical to a fresh regeneration"*. The species half has no artifact to check — verified: `gk-data/packs/fusion/data/seed/passive-tree/plan/` holds **42** files, all shared-tree ids and no species plan — so it is pinned by `tests/adapters/trees/test_tree_species_generate_tree.py` (`4 passed`). |
| *"the reverse index reports no cross-namespace reference"* | **green** | the reverse index is `SpeciesUniqueness` (`metrics/passive_tree.py:1427`); its U3 strength is the leak check — *"any `affix.species.<speciesId>.*` id referenced by a node whose OWN tree is not `speciesId`"* (`:1441`, implemented `:1508-1524`) — and a targeted run counts **U3 = 0** findings, with no line anywhere in the family report naming a namespace leak. |

So the row's Verify line is green **while its acceptance is red**, which is exactly why the two must not be
confused: the same run that satisfies the cross-namespace clause reports the 67 `SpeciesUniqueness` findings
that break the *acceptance* — **U1 12** (a `(name, flavor)` pair on more than one node) and **U2 55**
(an `(affixIds multiset, quotaCell)` fingerprint shared by more than one tree). U2 carries its own caveat
from the code: a node's committed seed record does not persist its `quotaCell` (*"H4's own documented
wiring gap, still open — a tree with no supplied quota cells simply contributes nothing to this half of the
index"*, `:1432-1435`), so its 55 findings are measured against the cells the caller supplies.

Clause 1 (the tree's own metric half) and clause 3 are red by a wide margin: 4 of 904 species complete
(9 of 904 filed at all), `NameCollision` **388/1679**, `NearDuplicate` **116/1679**, and every one of the
42 shared trees carries a binder `verdict=Fail`
([bcu2-12-treebinder-check.md](bcu2-12-treebinder-check.md)). The full family readings live in
[bcu2-12-census.md](bcu2-12-census.md) and [bcu2-12-namecollision-finding.md](bcu2-12-namecollision-finding.md).

## The stall is mechanical, not throughput

**All seven unfiled species carry a duplicate `nameKey` inside their own ledger rows** — and those are the
only species that do:

| species | ledger rows | duplicate `nameKey`s (samples) |
|---|---:|---|
| `Bamboo` | 30 | 2 (`tree.node.thorned-momentum-2`, `tree.node.resilient-pith`) |
| `BambooFurnace` | 31 | 1 (`tree.node.searing-embers`) |
| `BambooSpruce` | 37 | 2 (`tree.node.overgrowth-surge-8`, `tree.node.sap-fed-capacitor`) |
| `BedRockSnowZombie` | 25 | 1 (`tree.node.permafrost-bastion`) |
| `BedRockTallNut` | 35 | 1 (`tree.node.layered-bark-10`) |
| `BigChomper` | 32 | 2 (`tree.node.kinetic-osmosis-6`, `…-7` ×3) |
| `BigGatling` | 35 | 2 (`tree.node.ironclad-rhythm`, `tree.node.kinetic-recirculation-13`) |

`build_seed_document` refuses exactly that shape — `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/emit.py:246`
calls `assert_no_duplicate_name_keys` (`emit.py:48-60`), which raises `NodeKeyRefused` and writes no
document — and the records it receives are the ledger's, which already hold both colliding rows and are
never rewritten by a failed attempt. So each of those seven species rebuilds the same duplicate document on
every pass and can never be written; the driver reports it as a named outcome rather than crashing
(`run_species_tree`'s own `node_key_refused_reason`, the J9 narrative's fix), which is why the run survives
and why the progress reading looks like slowness.

This is the same contract as PT-J9-F1 ("a duplicate `nameKey` inside one species tree refuses the WHOLE
tree, permanently", with the named repair: *re-ask that one node / supersede its ledger row*), and it is
the same root as this lane's NameCollision finding: the corpus-wide name gate is not holding, so the
duplicates exist to be refused. **The seven species are the population PT-J9-F1 asked for.**

## Audit finding — PT-J9-F1 is ticked for *reporting* the refusal, not for the repair it names

`tasks/passive-tree-todo.md:7140` marks PT-J9-F1 **`[x]`** *"FIXED 2026-09-21 with J9-B1(b)"*, and the
fix that landed there was `run_species_tree` catching `NodeKeyRefused` into a reported
`node_key_refused_reason` — the batch survives and the refusal is named. That is **not** what the row's own
body specifies: *"**Fix (this program's):** a node-level repair for the colliding subject — re-ask that one
node (supersede its ledger row) rather than refusing the tree"*, with the consequence of not having it
stated two sentences earlier — *"every later pass rebuilds the identical duplicate-name document and
therefuses again — the species can never complete"*.

Measured at this head that is exactly the state: the seven species with a self-duplicate `nameKey` in their
own ledger rows are precisely the seven with **no node file**
(`tasks/reports/bcu2-12-j9-progress-census.json`). So the tick means *"the refusal is visible"*, never
*"the species can complete"* — and the seven are the population the unticked half of that row needs. Anyone
reading a green tick as "this blocker is gone" will run the corpus for another 23–28 hours and grow the
unfileable backlog rather than the tree count.

## What this lane cannot do

Unblocking them is the repair PT-J9-F1 names (a node-level re-ask that supersedes one ledger row) plus the
gate fix behind it — both `gk-forge/tools/seedsmith/**`, and a model call for the re-ask. Re-run the census command
after the run for the delta.
