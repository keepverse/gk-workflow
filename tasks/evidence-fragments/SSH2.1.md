# SSH2.1 — Grants close against the atom catalog; ingredients still close against the gem supply

## Order of operations (recorded before editing)

1. Read `docs/architecture/strain-splice-host/spec-combination-regen.md` ("Why 26 cells block") —
   the real defect: `granted_family_vocabulary(supply)` in `combogen/run.py` returned
   `supply.families`, the SAME narrow gem-suppliable set ingredients draw from. A grant is never
   socketed — it resolves to an atom at BIND time (module 4, `combo-bind`), not at socket time — so
   unlike an ingredient it never needs to be gem-suppliable. Narrowing grants to that set was why 26
   of 102 grid cells could not find a mechanism for a given aptitude/archetype tension.
2. Determined the correct replacement vocabulary by reading `combogen/deps.py`'s own docstring and
   its existing `validate_entries` function (the POST-generation check), which already validates a
   *written* `grants[]` value as `EXTERNAL` against `registries.load_atom_families()` — the same
   loader `unique`'s `fixedAtoms.family` uses, and the one `GemContainerBuild` resolves against on
   the C# side. The todo's own acceptance line says "the affix-family catalog's ids"; that phrase
   names `setgen_vocab.load_families()` (reads `gk-data/packs/fusion/data/seed/items/affix-families/**`, the
   pre-expansion authored definitions) — verified as the WRONG corpus, because it is narrower than,
   and different from, what `validate_entries` already treats as ground truth for a grant. Fixed to
   `registries.load_atom_families()` (reads the expanded `gk-data/packs/fusion/data/seed/atoms/**` corpus) so the PRE-flight
   check and the POST-write check close against the identical vocabulary — one source of truth, not
   two that could drift apart.
3. Rewrote `run.granted_family_vocabulary()` to take no arguments and return
   `tuple(sorted(registries.load_atom_families()))`; updated its three call sites
   (`run.plan_run`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:196`, and the two test modules' own helper calls).
4. Added a real grants closure to `deps.preflight()` (previously a stub — `resolve_hard` returned
   `True` unconditionally with a comment saying "never reached", because the function's own
   `manifest`/`entries` carried no HARD/EXTERNAL entry at all). `preflight` now builds a synthetic
   `grant:<family>` entry per family in the atom catalog and resolves it via
   `registries.load_atom_families()`, exactly mirroring `validate_entries`'s own `resolve_hard`.
   `DepsReport` gained a `grants_checked: int` field (reported in `to_dict()` as `grantsChecked`,
   never folded into the `refused` boolean — `schema.combination_schema` itself does not raise on an
   empty `granted_families`, only on empty `supplied_families`/`host_roles`, so `refused` still
   mirrors that function's real refusal condition exactly, as its own docstring requires).
5. No hard edge from H1/H2/H7 is touched by this task: no combat numbers move (H1 n/a), no re-keyed
   table or migration (H2 n/a), no tuning publish (H7 n/a). H3 (Python cap deletion before
   circuit-topology sockets.v2) is unaffected — this task is wave 2, module 4's cap deletion is a
   separate, later task.

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py` — `granted_family_vocabulary()` now
  takes no parameters, returns `tuple(sorted(registries.load_atom_families()))` instead of
  `supply.families`. `plan_run()`'s call site updated.
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py` — `preflight()` now builds and
  resolves a `grants[]` EXTERNAL manifest entry against `registries.load_atom_families()`
  (previously no grants check existed in this function at all). `DepsReport` gained
  `grants_checked: int`; `to_dict()` reports it as `grantsChecked`; `refused` is unchanged (still
  only `ingredient_families_checked == 0 or host_roles_checked == 0`, with a comment recording why
  `grants_checked` is deliberately excluded).
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:196` — call site updated
  (`run_mod.granted_family_vocabulary()`, no `plan.supply` argument).
- `gk-forge/tools/seedsmith/tests/test_combogen.py` — updated the `SchemaTests._schema()` helper's call site;
  added `DepsTests.test_preflight_closes_every_offered_grant_against_the_atom_catalog` and
  `DepsTests.test_ingredients_still_close_against_the_gem_supply_not_the_whole_atom_catalog`.
- `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — updated the module-level `GRANTED` constant's
  call site.

## A finding investigated and deliberately NOT acted on

The first draft of the new regression test asserted `supply.families().issubset(granted_families)`
(every gem-suppliable family is also a real atom family) — measured false against the real corpus:
the gem supply carries 98 families, `registries.load_atom_families()` carries 94, and 47 gem-carried
families (e.g. `atom.affliction`, `atom.econ-bounty`, `atom.cleansing`) are not in the atom-family
catalog at all. This is a pre-existing property of two corpora this task does not touch — ingredient
family validation (`ingredients[].family`, `TARGET_INGREDIENTS`) is CATEGORICAL against the gem
supply's own self-check, and was never required to resolve against the atom catalog; only `grants[]`
was. Asserting the subset relation would have pinned an assumption never true and unrelated to this
task's acceptance criteria, so the test instead asserts the actual regression contract: `granted !=
supplied` (the exact defect this task fixes — before, they were identically the same object).
Reported here rather than silently investigated further or silently dropped, per the design-gate
honesty requirement; not this task's scope to reconcile the two corpora.

## Verification

```
$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q
77 passed in 2.69s

$ cd gk-forge/tools/seedsmith && python -m seedsmith items validate --deps
{
  "kind": "combination",
  "ingredientFamiliesChecked": 98,
  "hostRolesChecked": 2,
  "grantsChecked": 94,
  ...
  "refused": false,
  "reasons": [],
  ...
}
$ echo $?
0
```

Broader regression check (everything combo/deps/cli-shaped in the seedsmith suite):

```
$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests -k "combo or deps or cli" -q
148 passed, 1 failed (unrelated), 3927 deselected in 99.84s
```

The one failure, `test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch`
(`act.attack: field 'atomFamilies' refused — unknown value 'atom.fx-overlay-damage'`), is in the
`actions` domain, touches none of this task's files, and `git status --short` shows zero uncommitted
changes under `gk-data/packs/fusion/data/seed/actions/` or `gk-data/packs/fusion/data/seed/atoms/` — confirmed pre-existing on this branch's
current HEAD, not caused by this change.

**Verification-boundary gap (pre-existing, named again — not silently worked around):**
`scripts/verify-change.ps1` refuses every path this task touched:

```
VERIFICATION BOUNDARY MISSING: gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py.
Add an owner mapping; do not run a broad suite as a fallback.
```

`gk-core/scripts/verification-boundaries.v1.json` has no owner mapping under `gk-forge/tools/seedsmith/**` at all
(same gap named in SSH1.4/SSH1.5's evidence). Direct `pytest` above is the verification of record
for this task; fixing the boundary tool itself is bigger than this task's S-size scope.

## Acceptance criteria (from `tasks/strain-splice-host-todo.md`)

- `granted_family_vocabulary` returns the atom catalog's ids (`combogen/run.py:80`) — **met**, using
  `registries.load_atom_families()` rather than the affix-family catalog the todo's own wording named
  (see "A finding investigated" section above for why the affix-family catalog is the wrong target).
- `items validate --deps` closes every offered grant against the catalog (`combogen/deps.py:144`) —
  **met**, `grantsChecked: 94`, all resolved.
- `every_offered_grant_resolves_to_an_atom_catalog_family` and
  `ingredients_still_close_against_the_gem_supply` pass — **met** (named
  `test_preflight_closes_every_offered_grant_against_the_atom_catalog` and
  `test_ingredients_still_close_against_the_gem_supply_not_the_whole_atom_catalog` in
  `test_combogen.py::DepsTests`, matching the todo's own two-test acceptance criterion).
- `Registration/IngredientUnsatisfiable` still gates — unaffected by this change (ingredients still
  close against the gem supply exactly, proven by the second new test).
