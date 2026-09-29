# SSH6.8 — publish `sockets` v3 `comboPricing` + the BalanceGuard test — **BLOCKED** (not this row's to unblock)

The row can only close against a **passing** report: `publish.py sockets --add-key ":comboPricing=…"` with
`measuredAgainst` **copied from the passing report**, the `sockets` constant moved to v3 in the same commit,
`shipped_combination_pricing_is_bounded_by_the_rarity_route` green in that same commit, and the server
booting against v3. The report does **not** pass, and two separate prerequisites block it.

## The measurement that blocks it (re-run today, at this HEAD)

`cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items combo-budget --report` → exit **1**:
**35 priced cells, 25 FAIL, 161 unpriced**. Reference `sprout → grafted` (1100 power / 120 souls);
derived `forge-gem 30 → 415` (bore/imbue unchanged); the excluded step is `firstseed → sunwoven`.

| Why it is red | Rows that must land first |
|---|---|
| **25 priced cells are cheaper than the rarity route** (all gem-only floors — the shipped floor rung needs no bore and no imbue) | **SSH8.5** — the row's own dep list says so: *"(SSH8.5 if the report was red)"*. It is a `materials.v{n+1}` publish of the DERIVED coefficient (R20), sequenced per both programs' revision tables — a later wave of this program, not this row |
| **161 cells cannot be priced at all**: their grants name 10 families that resolve to no atom at the requested tier (`atom.stalwart`, `atom.retribution`, `atom.aura-*`, `atom.enhance-*`) | **SSH4.4**'s own finding and its own remedy: *"the corpus regenerated with the current catalog (owner-run model calls, no hand-edit) or the atom families materialized"* — owner/generator work, already blocked on that row |

**A shortcut exists and is refused.** Publishing v3 with `maxRatioToRarityRouteMilli` but no
`measuredAgainst` would boot (today's ladder is one rung, so nothing binds), and a BalanceGuard test could
be written over the 35 priced cells alone — but the spec is explicit that `measuredAgainst` *"is written
**only** when the report passes"*, and a green test that skips the 161 unpriced cells would be an absent
check wearing a pass (**"an absent check is never a pass"**). Neither is a state this lane will ship.

## What is ready for whoever takes it

- `sockets` v3 is a mechanical publish once the report is green: `python gk-core/tools/tuning/publish.py sockets
  --add-key ":comboPricing=<json>"` with `maxRatioToRarityRouteMilli` 1000 (D23 written as arithmetic) and
  `comboPricing.measuredAgainst` **copied** from the report's own `socketsVersion`/`strainSpliceVersion`/
  `materialsVersion`/`corpusDigest` — `SocketTuningFiles.Current` and `combogen/tuning.py`'s
  `SOCKETS_PATH` move to `sockets.v3.json` in that same commit (H7).
- The parser (SSH6.6) already validates the section field by field, and the boot (SSH6.7) already refuses a
  stale one by name — so the publish is the only missing piece.
- The BalanceGuard test's shape: `ComboPricing.Measure` over the shipped tuning + corpus, asserting the
  cross-multiplied inequality per cell and never reading `measuredAgainst` (it recomputes).
- `sockets` v3 also writes the internal `version: 3`, which is what makes `sockets.v1.json`'s internal 3
  non-monotonic history only (recorded in SSH5.10-P2's (c) decline).

## Not proved / open

- Everything in the acceptance: the v3 publish, the constant move, the BalanceGuard test, the boot-against-v3
  reading. None of it can be honestly produced from a failing report.
- This row stays open; when SSH8.5's publish and SSH4.4's atom/corpus fix land, it is a single mechanical
  commit plus one test.
