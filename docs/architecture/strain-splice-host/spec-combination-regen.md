# Spec: `combination-regen`

**Module id:** `combination-regen` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 2 of 8, with one follow-up step after `circuit-topology` (5) · **Depends on:** — (5 for
the R11 step) · **Ruling:** 5, step 1 (*"regenerate migration (25→102) first"*); R11 (*"the helm becomes a
word host through regeneration with no code change"*) and R13 (*"Report by id; the owner rules each. No
automatic withdrawal from the 102"*) of [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md) ·
**Owner of the underlying work:** item module 21, [spec-strain-splice-gen.md](../item/spec-strain-splice-gen.md)
(sealed — referenced, not restated).

## Objective

Ruling 5 makes the 25→102 regenerate migration the first step of this program: the re-measure
(module 6 — combination power against price since R12 retired the count cap) and the tier ladder (module 7) must be tuned against the corpus that will actually ship,
**not** against 25 legacy words that are already ruled dead. Module 21 owns *how* combinations are
generated; this spec owns **the exit gate this program needs** and the one generator change that stands
between today's corpus and that gate.

State of the migration, read this session:

| Fact | Reading (2026-09-18) | Where |
|---|---|---|
| Generated combinations on disk | 25 strains + 51 splices | `gk-data/packs/fusion/data/seed/items/combinations/strains.json`, `gk-data/packs/fusion/data/seed/items/combinations/splices.json` |
| Grid cells ledgered `blocked` | 26 of the 102 (every one a model refusal, `outcome: blocked`) | `gk-data/packs/fusion/data/seed/items/combinations/combination-gen.ledger.json` |
| Legacy `socket-word` corpus | was still on disk with `_meta.model` present at the time; retired for real 2026-09-20 (strain-splice-host SSH2.6) | `data/seed/items/socket-words/sockwords.json` (path no longer resolves) |
| Python kind table | carries `socket-word`, **no `combination` kind** | `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:86`, assertion `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:120` |
| C# kind catalog | carries **both** | `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:113` (`socket-word`), `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132` (`combination`) |
| Gating metric | follows both kind ids, `gates = True` | `gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py:169` |
| Naming registry | `socketWords` allocation still present with a retirement note; registry `frozen: true` | `gk-data/packs/fusion/data/seed/items/_registry/naming.v1.json:427`, `gk-data/packs/fusion/data/seed/items/_registry/naming.v1.json:4` |

These counts are readings. The exit gate below is written as contracts, never as `== 102`.

### Why 26 cells block — and the generator input that causes it

Every blocked reason says the same thing in different words: the model could not find a **mechanism**
(a proc, a rider, a reactive conversion) among the families it is allowed to grant for that
aptitude/archetype tension. The grant vocabulary is deliberately narrowed to the families live gems
supply (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py:80`, `granted_family_vocabulary`
returns `supply.families`), with the stated reason that this keeps the whole combination inside one
closed list for `Registration/IngredientUnsatisfiable`.

That reason holds for **ingredients** and not for **grants**. A grant is never socketed; it is resolved
to an atom when the combination binds (module 4, `combo-bind`), and what it must close against is the
**atom catalog** — `gk-data/packs/fusion/data/seed/items/affix-families/**` expanded by `FamilyExpansion`, the same catalog
`GemContainerBuild` resolves against (`gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:24`). Measured
this session: all 18 families the shipped combinations grant, and all 30 they take as ingredients,
are ids in that catalog.

**Change (technical, resolved by closing each list against what consumes it):** the grant vocabulary
becomes the affix-family catalog's ids; the ingredient vocabulary stays the gem-supplied families. A
pre-flight check (`items validate --deps`) confirms every offered grant resolves to a catalog family.
The 26 blocked cells are then re-run with `--retry-blocked`; nothing already authored is re-run.

### Still-blocked cells — reported by id, ruled by the owner (R13)

A cell that still answers `blocked` after the widened re-run is **not withdrawn** from D20's 102 and is
**not** retried in a loop. The run writes a still-blocked report — one row per cell: grid id (from
`StrainSpliceGrid.AllIds`), shape, aptitudes / archetype, the model's own `blockedReason`, and which re-run
(widened grants, R11 helm offer) it survived — to the run summary and as a JSON artefact beside the run
ledger. The owner rules each id; a ruling (author by hand as an exemplar, re-brief, or withdraw) is
recorded against the id in the ledger and applied by the generator, never by editing the corpus. Until a
cell is ruled it stays `blocked` in the ledger, and the exit gate below reads *"every cell is `entry` or
listed in the still-blocked report"* — the report is the deliverable, not an empty list.

`_retry_blocked_ledger` (`gk-forge/tools/seedsmith/seedsmith/report/cli.py:607`) is the re-run path; the report is
a read over the same ledger, so it cannot disagree with what was re-run.

### The helm joins the host set — the R11 step, after `circuit-topology`

R11 puts `head-guard` at 4 sockets in `sockets.v2.json` (`circuit-topology` §1). **No code or schema
change here:** the schema's `hostRole` enum is `host_roles()`
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:75` docstring;
`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60`), computed as every role whose ceiling
reaches `ingredientCount` 4 (`gk-core/data/tuning/sockets.v1.json:67`). Once the combogen tuning reader points at
the current revision (`circuit-topology` §4), the helm is offered to the model automatically.

So this module has a second, short step that runs **after** `circuit-topology` — **after its
`resocket --write` has landed, not merely after v2 is published** — and **before** `combo-budget`
measures (ruling 5's order: the measurement must see the corpus that ships). The host set is derived from
the *tuning* ceilings (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py:125`), not from the base
types, so a re-run between the v2 publish and the re-stamp would author helm-hosted words while no helm
base yet holds four sockets. If the owner declines the ask-first re-stamp, this step does not run
(strengthen pass 2026-09-18):

1. Re-run with `--retry-blocked` under the current revision. Every cell still open is now offered
   `armament-primary`, `core-guard`, `head-guard` and every other role the doubled table lifts to 4+.
   Authored cells are **not** re-run (ledger discipline, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:65`)
   and keep their coarse pins (ruling 2).
2. Report **host-role diversity** — a new report-only metric `Coverage/HostRoleDiversity` in
   `gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py` beside `Coverage/EmptyPartition`
   (`gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py:23`; the new metric itself at `:49`): per shape, the share of entries pinned to each
   offered host role (weapon `armament-primary`, chest `core-guard`, helm `head-guard`, the other
   4-ceiling roles) and to no role. **A reading, never a gate** — it tells the owner whether the helm is
   actually chosen, and it asserts no share.
3. Re-print the still-blocked report (R13).

**Consequence stated, not hidden:** because authored cells are never re-run, the helm can only appear on
cells that were still open at this step. If the diversity reading shows the helm barely used, spreading
it onto authored cells needs a re-author path that does not exist today; that is a new, ask-first
generator verb, not something this module does quietly.

### The rename bundle (module 21's analysis, executed here as the exit gate)

`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py:9` lists five sites that must move together. Status and action:

| # | Site | Action in this module |
|---|---|---|
| 1 | gating metric kind lookup, `gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py:169` | ✅ already follows both ids; **after** step 5, drop `socket-word` from `COMBINATION_KINDS` so the metric reads one kind |
| 2 | Python `KindSpec`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:86` | rename `socket-word` → `combination` with the C# field shape (`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132`); the count assertion at `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:120` still holds because it is a rename |
| 3 | C# `KindCatalog`, `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:113` | remove the `socket-word` row (the `combination` row already exists) |
| 4 | `naming.v1.json` `socketWords` | **stays allocated** — the registry is frozen and *"no partition's namespace shrinks"* (`naming.v1.json:9`). The emptied partition reports through `Coverage/EmptyPartition`, which ssot-sockets and spec-strain-splice-gen both call *"the correct and visible outcome"*. Removing the allocation is a v2 registry and is ask-first |
| 5 | the 25 legacy rows | retired by a generator verb — `combogen-migrate --write` (built by SSH2.3; the subparser is `gk-forge/tools/seedsmith/seedsmith/report/cli.py:3146`) — which deletes the legacy partition file and writes a run-ledger record. **No hand deletion** |

## Seedsmith / generator

| Item | Detail |
|---|---|
| Adapter / stage | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py:80` (grant vocabulary); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py:173` (pre-flight also closes grants against the atom catalog); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py:1` (add a `--write` path); `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:86`; `gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py:169`; C# `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:113`; still-blocked report over the ledger (R13) in `gk-forge/tools/seedsmith/seedsmith/report/cli.py`; `Coverage/HostRoleDiversity` (new, report-only) in `gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py:49` (R11). **Not changed:** `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py` — the helm reaches `hostRole` by derivation |
| New seed fields | **none.** `combination` entries keep the shipped shape (`shape`, `aptitudes`, `archetype?`, `hostRole?`, `hostFrame?`, `minSockets`, `ingredients`, `grants`, `grantedTier`); the `grants` enum widens, it stays a closed enum. `audit_schema` still passes (no numeric field) |
| Magnitudes | none authored; `minTier`/`grantedTier` still come from `gk-core/data/tuning/strain-splice.v1.json` (module 7 moves them out); ingredient count from `gk-core/data/tuning/sockets.v1.json` |
| Regenerate | `python -m seedsmith items validate --deps` → `python -m seedsmith items generate --kind combination --shape strain --write --retry-blocked` → same with `--shape splice` → `python -m seedsmith items combogen-migrate --write` (new). **R11 step, after `circuit-topology`:** the same two `--retry-blocked` runs again under `sockets.v2.json` |
| Check | `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` · `--metric Registration/IngredientUnsatisfiable` · `--metric Coverage/EmptyPartition` · `--metric Coverage/HostRoleDiversity` (reading) · `--metric SemanticDedup/NearDuplicate` · `dotnet run --project gk-forge/tools/ItemSeedValidator` |
| Pytest | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`, `gk-forge/tools/seedsmith/tests/test_combogen.py`, `gk-forge/tools/seedsmith/tests/test_linkage.py` |

## Commands

```powershell
cd tools\seedsmith
python -m seedsmith items validate --deps
python -m seedsmith items generate --kind combination --shape strain --dry-run --retry-blocked
python -m seedsmith items generate --kind combination --shape splice --dry-run --retry-blocked
python -m seedsmith items generate --kind combination --shape strain --write --retry-blocked
python -m seedsmith items generate --kind combination --shape splice --write --retry-blocked
python -m seedsmith items combogen-migrate --dry-run
python -m seedsmith items combogen-migrate --write          # (new) retires the legacy partition
python -m seedsmith check ..\..\data\seed\items --adapter items --gate
# R11 step — only after circuit-topology has published sockets.v2.json (head-guard 4) AND its resocket --write landed:
python -m seedsmith items generate --kind combination --shape strain --write --retry-blocked
python -m seedsmith items generate --kind combination --shape splice --write --retry-blocked
python -m seedsmith check ..\..\data\seed\items --adapter items --metric Coverage/HostRoleDiversity
python -m pytest tests/test_strain_splice_gen.py tests/test_combogen.py tests/test_linkage.py -q
cd ..\..
dotnet run --project gk-forge/tools/ItemSeedValidator
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py         grant vocabulary = atom catalog ids
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py        pre-flight closes grants too
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py     --write path (new)
gk-forge/tools/seedsmith/seedsmith/report/cli.py                          combogen-migrate --write
gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py                socket-word -> combination
gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py                     one kind after the retire
gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py                    Coverage/HostRoleDiversity (new, report-only)
gk-forge/tools/seedsmith/seedsmith/report/cli.py                          still-blocked report by grid id (R13)
gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs                socket-word row removed
gk-data/packs/fusion/data/seed/items/combinations/*.json                              REGENERATED (blocked cells)
gk-data/packs/fusion/data/seed/items/socket-words/                                    RETIRED by the verb
```

## Code style

```python
def granted_family_vocabulary(catalog: AtomFamilyCatalog) -> "tuple[str, ...]":
    """What a combination may GRANT: every family the atom catalog can resolve.

    Ingredients close against the GEM supply (IngredientUnsatisfiable gates that). Grants are
    never socketed - they resolve to an atom when the combination binds - so they close against
    the atom catalog instead. Narrowing grants to the gem supply is what left 26 grid cells with
    no mechanism to offer.
    """
    return catalog.family_ids
```

## Testing strategy

| Test | Asserts |
|---|---|
| `every_offered_grant_resolves_to_an_atom_catalog_family` | the new closure, against the real catalog |
| `ingredients_still_close_against_the_gem_supply` | the unchanged closure; the gating metric agrees |
| `retry_blocked_never_reruns_an_authored_cell` | the ledger discipline (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:65`) |
| `the_kind_is_renamed_not_removed` | Python and C# kind tables name `combination`, neither names `socket-word`, the Python count assertion holds |
| `ingredient_unsatisfiable_still_gates_after_the_retire` | the migration's named risk (spec-strain-splice-gen.md) |
| `the_migrate_verb_writes_a_ledger_record_and_is_idempotent` | a second `--write` changes nothing |
| `every_generated_id_is_a_grid_cell` | against `StrainSpliceGrid.AllIds`, derived from `AptitudeCatalog.All` + the archetype registry |
| `no_id_name_or_brief_contains_the_banned_word` | the shipped ban, unchanged |
| `a_still_blocked_cell_is_reported_by_grid_id_and_never_withdrawn` | R13: fixture ledger with a blocked answer → report lists that grid id with its reason; the id stays `blocked` in the ledger and stays in `StrainSpliceGrid.AllIds` |
| `the_host_role_enum_is_derived_from_the_loaded_ceilings` | R11: a fixture tuning with `head-guard` 4 yields a schema whose `hostRole` enum includes `head-guard`; with 3 it does not — no role named in code |
| `host_role_diversity_is_a_reading_not_a_gate` | the metric reports shares and never fails the gate |
| `the_r11_step_refuses_while_a_tuning_host_role_has_no_base_reaching_four` | fixture: v2 ceilings, un-restamped corpus → the step refuses by name before any model call |

⛔ No test asserts 102 entries, 76, or 26, nor any host-role share or count of helm-hosted entries. The grid law is asserted from its inputs; how many cells are
authored today is printed by the run summary.

## Boundaries

**Always:** regenerate through the ledger; retire the legacy partition with the verb; keep the gating
metric gating at every commit.

**Ask first:** bumping `naming.v1.json` to drop the `socketWords` allocation (frozen registry); a
re-author path that would move authored cells onto the helm.

**Owner rules, per id (R13):** every still-blocked cell — the report is the input to that ruling.

**Never:** hand-edit or hand-delete a generated file; re-run an authored cell; widen the
**ingredient** vocabulary beyond the gem supply; use the banned word; withdraw a cell from the grid
automatically or by threshold (R13); add a helm case to the schema or generator (R11 — derivation only).

## Success criteria

- [ ] `socket-word` exists in neither kind table; `combination` exists in both with one shape.
- [ ] The legacy partition is retired by the verb, with a ledger record; `Coverage/EmptyPartition`
      reports it visibly.
- [ ] Every grid cell is either ledgered `entry` or listed **by id** in the still-blocked report after the
      widened re-run and the R11 re-run; no blocked cell is dropped or withdrawn (R13).
- [ ] The R11 re-run ran under `sockets.v2.json`, with `head-guard` in the offered host set by
      derivation, and `Coverage/HostRoleDiversity` printed across weapon / chest / helm / other roles.
- [ ] `Registration/IngredientUnsatisfiable` gates on the one remaining kind.
- [ ] Every grant in the corpus resolves to an atom-catalog family.

## Open questions

None. The withdrawal question (map §7, former O3) was answered by R13: report still-blocked cells by id;
the owner rules each; no automatic withdrawal. Each per-id ruling is an input this module waits for at its
exit, not an open design question — modules 3–5 are not blocked by it.
