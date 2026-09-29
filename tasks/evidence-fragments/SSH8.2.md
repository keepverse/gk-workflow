# SSH8.2 — emit the imbue rows into `recipes.json` — **BLOCKED on SSH8.3** (the executor guard)

The write itself is ready and was run to convergence: `--emit-deterministic --write` adds **18 imbue
rows** (`recipe.070`–`recipe.087`), `ItemSeedValidator` PASSes at **3978 entries** (+18), the Core
materials corpus loads them, and the new `record_deterministic_amendment` appends
`_meta.amendments: recipegen/deterministic-emit-1` recording exactly those 18 ids — the acceptance's own
provenance line, which `write_corpus` alone does NOT write (it merges entries and leaves an existing
document's `_meta` alone).

## Why it is not shipped

`dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~EveryRecipeOperationWithRowsHasAnExecutor"`:

```
Failed ItemWorkbenchEndpointsTests.EveryRecipeOperationWithRowsHasAnExecutorExceptElevate
  Expected: string[]  ["elevate"]
  Actual:   List<string> ["elevate", "imbue"]
```

The guard is CORRECT and it is doing its job: the corpus would carry `imbue` rows while the workbench has
no imbue executor. **SSH8.3** is the row that gives it one (`SocketImbue` refusing a mismatched essence by
name, plus `a_chaff_chassis_can_be_bored_imbued_and_filled_end_to_end` through the real endpoints) — the
very next row, and the reason the todo places it there. The two dishonest exits are refused: adding
`imbue` to that test's expected list would WEAKEN the guard to make a change pass, and shipping the rows
with no executor would put an unpriced verb in the corpus.

The write was therefore reverted (`git restore gk-data/packs/fusion/data/seed/items/recipes/recipes.json`; generated data, so a
revert is regeneration's inverse and no row was hand-touched), and the guard is green again at HEAD.

## What IS landed here (it is used by the SSH8.2 re-run, after SSH8.3)

| Piece | Command | Result |
|---|---|---|
| the amendment record the acceptance requires | `cd gk-forge/tools/seedsmith; SEEDSMITH_ALLOW_PRODUCTION_TREE=1 PYTHONPATH=. python -m seedsmith.adapters.items.recipegen.run --emit-deterministic --write` | appended `recipegen/deterministic-emit-1` with **18** entries (`recipe.070`–`recipe.087`); `write_corpus` alone records nothing, which is the generator-provenance gap this closes |
| the emitter's plan and idempotence, against a corpus WITHOUT imbue rows | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_recipes_gen.py -q` | **62 passed / 0** — the fixture now strips imbue rows first, so it tests the emitter rather than whatever the shipped file happens to carry |
| the written corpus validated while it existed | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **PASS — 3978 entries / 1013 files / 2589 warnings** (3960 + 18) |
| the real corpus still loads in Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~MaterialCorpus\|FullyQualifiedName~MaterialSpend\|FullyQualifiedName~ConsumableCorpus"` | **38 passed / 0** |
| the seedsmith gate while it existed | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --gate` | 57 gap / **607 note** / 153 not_measured — the 57 gaps are the pre-existing set (no imbue row appears in any GAP) |

## Not proved / open

- The acceptance's remaining line — "the server's boot import ... green" — is exactly what blocks it: the
  boot's catalog load is fine, but the *workbench executor* guard is not, and that is SSH8.3's deliverable.
- `SSH8.2` is a re-run once SSH8.3 lands: the emitter, the amendment record and the gates are all proven
  above; nothing else in it is unfinished.
