# S4 — the shipped corpus, re-planned deterministically

Task: `species-gear-chain` T27 `setClass` half, lane `sgc-2`, queue step S4 ·
spec: `docs/architecture/species-gear-chain/spec-set-species-binding.md` rev 2 § The set-planning system

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The re-plan is deterministic and model-free, and refuses rather than guessing | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_topology_repair.py -q` | exit=0 :: **16 passed in 57.76s** | `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology_repair.py` |
| The write is applied to the shipped corpus | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items repair-set-class --write --allow-production-tree` | exit=0 :: `entries 910, changedEntries 910, changedFiles 884, resolvedByClass {family: 4, general: 906}` | `gk-data/packs/fusion/data/seed/items/sets/**` |
| Idempotent: a second identical run changes nothing | same command again | `changedEntries 0, changedFiles 0`; `git status` shows no further modification | idem |
| ⭐ The corpus diff is a PURE INSERTION — one `setClass` line per entry, nothing else | `git diff --numstat gk-data/packs/fusion/data/seed/items/sets \| awk '{a+=$1; d+=$2; n++} END {print "files="n" added="a" deleted="d}'` | `files=884 added=910 deleted=0`; `git diff -U0 … \| grep -E "^[+-]" \| grep -vc '"setClass"'` → **0** non-`setClass` diff lines | idem |
| No set bonus magnitude moved: `members`/`thresholds` untouched | same diff, plus `test_applying_the_plan_stamps_every_entry_and_keeps_every_other_key` | every entry's non-`setClass` keys compare equal to the pre-run copy; a fixture failure (`ensure_ascii=False` turning 6 `\u00a7`/`\u2014` sequences into literals) was found and fixed by deriving the escaping style from the file, which took `deleted` from 12 to 0 | idem |
| Every entry carries `speciesId` (real id or explicit absent) **and** `setClass` | `python - <<'PY' … census … PY` | `withSetClass 910/910`; `creature-withSpeciesId 844/844`, `build 0/36`, `theme 0/30` (explicit absence by omission, the spec's Ask 2) | idem |
| The class is the one the entry's own shape resolves to, over the real corpus | `test_every_written_class_satisfies_its_own_template` (same run) | every written class satisfies its template; the `family` count is printed, not asserted | idem |
| No new corpus gap | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items` | exit=0 :: **63 gap, 580 note, 153 not_measured**; `grep -c setClass` over the gap lines → **0** | — |
| The whole seedsmith suite, against the pre-change baseline | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests -q --tb=no` | **22 failed, 4173 passed, 3 skipped, 5003 subtests passed in 580.12s** vs baseline **21 failed, 4115 passed, 3 skipped, 4994 subtests**; `comm` of the two failure-name sets → **1 new** (`test_themes_v2::test_publish_is_idempotent`), **0 fixed** | this fragment, rows above |
| That one new failure is **not** this change | `git checkout -- gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json; PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_themes_v2.py -q` | **1 failed, 3 passed** with the lane's changes still in the tree and the file at its committed LF bytes — it is T51's CRLF writer, order-dependent: it passed in the baseline only because an earlier test in that run had already converted the file to CRLF | todo row T51 |
| Path-owned boundary — the code paths | `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology_repair.py,gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/species_repair.py,gk-forge/tools/seedsmith/seedsmith/report/cli.py,gk-forge/tools/seedsmith/tests/test_topology_repair.py,docs/architecture/species-gear-chain/spec-set-species-binding.md -Session sgc-2` | exit=1 :: **23 failed, 4172 passed, 3 skipped in 548.74s** — 22 are the pre-change baseline names and the 23rd is `test_audit_doc_citations::…_produces_a_report`, which fails only because this run's cwd is `gk-forge/tools/seedsmith` (no `docs/`): measured both ways, **1 failed** from `gk-forge/tools/seedsmith` vs **1 passed** from the repo root | todo row T55 |
| Path-owned boundary — the corpus path | `.\scripts\verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json -Session sgc-2` | **fail** :: `VERIFICATION BOUNDARY MISSING: gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json` — the item corpus tree has no owner mapping, so this lane's S4 path has no path-owned command at all | todo row T55 |
| Doc citations and the magic-number audit stay clean | `powershell -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` · `python gk-core/scripts/audit-magic-numbers.py --summary` | exit=0 · `TOTAL 0 0 0 0 0` | — |
| Ledger integrity after every line this task appended | `python gk-core/scripts/anchor-ledger.py tasks/species-gear-chain-ledger.jsonl check` | exit=0 :: `LEDGER OK` | `tasks/species-gear-chain-ledger.jsonl` |

## Not proved

- ⛔ **`dotnet run --project gk-forge/tools/ItemSeedValidator` is NOT green, and this task's own acceptance line
  for it is unmet.** Measured: **41 errors before -> 951 after**, exactly **910 new**, every one
  `UnknownKey [seed-contract.md §9] unknown key 'setClass' on kind 'set'`. Cause read directly: the C#
  validator carries its OWN hand-transcribed copy of the `set` kind's field list
  (`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:110-112`) and `setClass` is not in it. That file
  is **outside this lane's fence**, so the corpus was written and the one-line mirror filed as todo row
  **T56** (`extra: new[] { …, \"speciesId\", \"setClass\" }`). The SSOT-side schema is not the defect:
  `seedsmith check` is unharmed (0 gaps mention the field) and `kinds.py` declares `setClass` optional.
- `unique-species` remains unpopulated in the shipped corpus (0 entries) and unreachable from the
  generator — `species-craft-ideal.md:125` predicted exactly that, and re-planning the generator's
  shape policy is a row of its own.
- The four `family` entries carry a class whose module-25 identity contract (`requiredFamilyId`) no
  shipped entry declares; recorded in the spec as forward debt, not fabricated.
- Full `verify-change` coverage for the 884 rewritten corpus files is impossible until T55 maps the
  item corpus tree.
