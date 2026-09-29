# ISG4 — repair the 19 `ReferenceUnresolved` grants through the generator

Sub-agent task `item-seed-gen`. The data half of ISG2's generator fix.

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/grant_repair.py` (new) — a findings-driven,
  grant-only, model-authored repair, modelled on `tag_axis_repair`/`unique_frame_repair`:
  `findings()` reads the real validator's `--findings-json --codes=ReferenceUnresolved`;
  `plan()` intersects each finding with the shipped row (so a stale finding is dropped, and two
  findings on one entry collapse to one call); the schema asks for one `replacements` entry per BAD
  SLOT — no more — with the whole affix-family catalog as its `enum`, so the already-resolvable
  grants never leave the code's hands and an out-of-catalog answer cannot validate; `apply()` writes
  the result into BOTH the ledger row and the shipped row, in place.
- `gk-forge/tools/seedsmith/tests/test_grant_repair.py` (new) — 13 tests.
- `gk-data/packs/fusion/data/seed/items/combinations/splices.json`, `strains.json` — 15 entries' `grants` replaced
  (9 splice + 6 strain); `combination-gen.ledger.json` carries the same change.

## Why grant-only and not a cell re-run

Re-running a cell through the generation graph re-authors name, flavor and ingredients. Measured
first with `--overwrite` (ISG3) and the owner's local model on 2026-09-20: the ten re-authored cells
took the corpus from 37 to **41** errors — `FusionNotDecomposable` 1 -> 14, `NameGrammarViolation`
1 -> 7, `PossessiveForbidden` 2 — while removing the 19 grants. A small quantized model under many
similar briefs has a narrow creative range (SSH2.5 finding 2). The repair was restored and re-done
grant-only; the diff is now provably grant-only (`git show HEAD:...` vs on-disk: `{'grants': 9}`
splices, `{'grants': 6}` strains, no other field).

## Model

`google/gemma-4-26b-a4b-qat` at `http://localhost:1234/v1/chat/completions`, verified before the
batch by reading the response's own `model` and `system_fingerprint` fields (both
`google/gemma-4-26b-a4b-qat`). 15 entries, 15 answered, 0 failed; every answer validated against the
catalog enum. The model only ever chose the replacement for the broken slot, e.g.
`atom.aura-precision` -> `atom.precision`, `atom.aura-retribution` -> `atom.retribution`,
`atom.aura-pierce` -> `atom.shld-breach`, `atom.aura-onslaught` -> `atom.death-salvo`,
`atom.aura-composure` -> `atom.stoicism`, `atom.fx-overlay-damage` -> `atom.retribution`.

## Verification

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ReferenceUnresolved` is 0 | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release --no-build -- gk-data/packs/fusion/data/seed/items` | FAIL — 37 errors before, **18** after (entries 3957 both runs, no content lost) | stdout |
| The diff is grant-only and surgical | `git show HEAD:gk-data/packs/fusion/data/seed/items/combinations/{splices,strains}.json` vs on-disk | `{'grants': 9}` / `{'grants': 6}`, no other field; every `atom.enhance-*` grant preserved verbatim | stdout |
| Ledger and file agree on the new grants | direct read of `combination-gen.ledger.json` vs the two seed files, per entry | 0 mismatches | stdout |
| The new module's tests pass | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_grant_repair.py -q` | pass — 14 passed | stdout |
| The combination suites stay green | `... pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_grant_repair.py -q` | pass | stdout |

## What remains (out of this task's scope, recorded)

18 errors: `NameCollision` 13, `NamespaceUncovered` 1, `NamespaceUnexpandable` 1,
`InventedConnective` 1, `NameGrammarViolation` 1, `FusionNotDecomposable` 1.

- The 16 naming findings are `fae533a519`'s reverted set — the ledger still holds the old names
  (`authored.entries_from_ledger` would revert them), which is SSH2.5 finding 1's open follow-up.
  Fixing it means making the combination name repair write through `RunLedger`, then re-running it;
  deliberately not attempted here because re-emitting from the ledger without that fix costs 7
  errors (measured: 37 -> 44).
- The 2 namespace findings are `naming.v1.json`'s `idNamespaces.socketWords`, whose removal SSH2.6
  explicitly calls ask-first ("dropping the allocation needs a new registry version").
