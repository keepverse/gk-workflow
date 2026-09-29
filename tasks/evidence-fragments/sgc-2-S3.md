# S3 — forward emission: `set-charm-gen` emits `setClass`

Task: `species-gear-chain` T27 `setClass` half, lane `sgc-2`, queue step S3 ·
spec: `docs/architecture/species-gear-chain/spec-set-species-binding.md` rev 2 § The set-planning system

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A newly emitted entry carries `setClass`, resolved through the S2 data | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_set_charm_gen.py -q` | exit=0 :: **104 passed, 2677 subtests passed in 5.45s** | `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/seedfile.py` |
| The emitted class is the class the emitted entry resolves to (one resolver, no second opinion) | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_set_charm_gen.py gk-forge/tools/seedsmith/tests/test_set_topology.py -q` | exit=0 :: **137 passed, 2677 subtests passed in 30.35s** | `gk-forge/tools/seedsmith/tests/test_set_charm_gen.py` (`SetClassEmissionTests`) |
| The ladder is exercised forward: 4 roles → `general`, 5 and 6 roles → `family` | same run | 4/5/6-role drafts emit `general`/`family`/`family`; `validate_entry` returns `()` for each | idem |
| A shape no class admits **refuses at emission** rather than shipping | same run | a 4-role 5-threshold plan raises `SetTopologyError` naming `set.topology-002` | idem |
| `setClass` is idempotent, sits beside `themeKey`, and moves no `SetEvaluator` field | same run | re-stamping changes no key order; `keys[themeKey+1] == "setClass"`; `members`/`thresholds` untouched | idem |
| The field is optional in the KindSpec (so a pre-repair row is not rejected before the repair runs) but always written | same run | `setClass ∈ optional`, `∉ required`, and every emitted entry has one | `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py` |
| The corpus gate gains nothing: no new gap names the field | `cd gk-forge/tools/seedsmith; python -m seedsmith check ../../data/seed/items --adapter items` | exit=0 :: **63 gap, 580 note, 153 not_measured**; `grep setClass` over the gap lines → 0 hits (the 63 are the pre-existing flavour/coverage/dedup/`SetCompletability` readings) | — |
| No balance number added | `python gk-core/scripts/audit-magic-numbers.py --summary` | `TOTAL 0 0 0 0 0` | — |
| Docs re-anchored with the code | `powershell -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit=0 | `docs/architecture/item/spec-set-charm-gen.md`, `docs/architecture/item/seed-contract.md` |
| Path-owned boundary for the changed paths | `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py,gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/seedfile.py,gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology.py,gk-forge/tools/seedsmith/tests/test_set_charm_gen.py,docs/architecture/item/spec-set-charm-gen.md,docs/architecture/item/seed-contract.md,docs/architecture/species-gear-chain/spec-set-species-binding.md -Session sgc-2` | exit=1 (`$LASTEXITCODE`) :: **3 failed, 1077 passed, 3786 subtests** — the same three pre-existing failures S2 recorded (`UNEXPECTED FAILURE:` × 3, all in the pre-change baseline of 21) and none in a path this lane touched | T55 |

## Not proved

- `unique-species` is **unreachable from this emitter today**, and the test says so rather than
  pretending otherwise: `distribute_set` still refuses more than `maxRoles` (6) member roles
  (`SetRoleForbidden`) while the class's closed parameterization is 10 or 15. Re-planning what the
  generator *authors* is the set-planning planner's row, not this field's.
- `verify-change` green is unreachable for a seedsmith path until T55 lands (diagnosed at the selected
  boundary — no broad retry).
