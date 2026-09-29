# SSH6.4 — `python -m seedsmith items combo-budget --report` and the C# power-dump entry point

**Entry point chosen** (the plan's Defaults leave it to this row): `gk-forge/tools/ItemSeedValidator
--combo-budget-dump` — a new mode beside `--collision-groups` / `--normalize-names`, so the report
shells out to the same tool-and-authority pattern `items repair-names` already uses. It reads the
shipped sockets revision (`SocketTuningFiles.Current`), the newest `materials.v{n}.json` and
`strain-splice.v{n}.json` by FILENAME revision, the recipe corpus, the combination corpus (with
`CombinationCorpus.ReadGrants`, new — `ComboRecipe` deliberately carries no grants) and the atom +
rarity seed files through `AtomSeedFile.Collect`, then calls `ComboPricing.Measure`/`Derive`. A cell
whose container cannot build is REPORTED by name, never thrown.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| per frame: both geometry readings, the per-role circuit count and the enabled words per admitted role | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items combo-budget --report` | `humanoid` and `plant` (the corpus's own two frames, read from the base-type entries): **geometricCeiling 13 over 15 roles, reachableCeiling 15**; per role `ceiling` / `circuits` / `words` — `armament-primary` 8/2/40, `core-guard` 8/2/55, `manipulator` 4/1/1, helm `head-guard` 4/1/0 (+ the two unpinned words, which admit every role) |
| per cell: power, floor and every leg, ratio, reference, verdict | (above) | 35 priced cells printed, e.g. `combo.splice-agility-ferocity t1 plain power 5300 floor 180 ratio 29444 ref 9166 FAIL`, `floor rung 4  legs: gemx1=30@r0, gemx1=30@r0, gemx1=60@r1, gemx1=60@r1` |
| on failure it prints the derived coefficients; it asserts no reading's size | (above) | exit **1**: **25 cells cheaper than the rarity route**, **161 cells unpriced** (a grant family with no atom at the requested tier — SSH4.4's finding, now named per cell) and the derivation `forge-gem 30 -> 415` (bore/imbue unchanged) plus each cell's smallest lever and required coefficient. No assertion anywhere on any count |
| `power(c,k)` from the one C# computation, never a Python `Compose` | (above) + `grep -n "ActorPowerCache" gk-forge/tools/seedsmith/seedsmith/**/*.py` | the report renders the dump; no Python file names `ActorPowerCache`. `tuning.combo_budget_dump()` raises rather than guessing when the tool cannot run |
| parity test on price floor | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **31 passed**. `test_price_floor_parity_python_and_csharp_agree_on_a_gem_only_cell` re-derives `gem(t)` independently (the recipe's authored band scaling `coefficient x (rungIndex + 1)`, ceilinged, plus the upcycle-chain `min`) and asserts it equals the dump's FOUR gem legs and their sum, leg by leg |
| the owner reads a run on the shipped files; it passes or names the cells SSH8.5 fixes | (above) | it is RED today and names them: **25 failing cells** (each with its derived coefficient) and **161 unpriced cells**, with the distinct grant families grouped. SSH8.5 publishes the derived `materials` coefficient; the un-materialised families are SSH4.4's corpus/atom gap |
| boundary checks | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests`; `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` | **97 passed / 0** and **15086 passed / 0** |

## Not proved / open

- **`verify-change.ps1` exits 1 on this change for pre-existing reasons**: `report/cli.py` maps to
  `seedsmith-fallback (module)`, so its check is the WHOLE seedsmith project — **23 failed / 4195 passed
  / 3 skipped**, the same 23 as before this change (none in combogen, tuning or the report; one is a live
  model timeout from this lane's own LM Studio traffic). Its `test-substrate` guard printed OK, and the
  `core` / `itemseedvalidator` boundaries it never reached were run directly (above).
- **The report is red by design today**: the derived fix is a `materials.v{n+1}` publish (SSH8.5), and
  the 161 unpriced cells need the atom catalog materialised (SSH4.4's own finding). Nothing here
  suppresses either; R13's per-id rulings move the corpus digest and re-measure.
- `power 0` passes trivially for cells whose only grant atom is unpriceable by `PowerTables` (a reading
  in the report, not a defect this row owns).

## Re-verified 2026-09-22 (lane `ssh29`) — the entry point already exists at base

The SSH6.4 brief for lane `ssh29` said this row was never started; it is committed. `ComboBudgetDump.cs`
(the C# `--combo-budget-dump` entry point) landed in `0d53bd98f`, and it builds the shipped atom catalog
by walking `gk-data/packs/fusion/data/seed/atoms/**` recursively (`SeedFiles` = `SearchOption.AllDirectories`, so
`gk-data/packs/fusion/data/seed/atoms/generated/**` — the FamilyExpansion output — is included) through `AtomSeedFile.Collect`.

| Criterion | Command | Result |
|---|---|---|
| the report runs over the shipped files | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items combo-budget --report` | **exit 1** — sockets.v2 / materials.v5; frames `humanoid`/`plant` geometricCeiling 13 over 15 roles, reachableCeiling 15; **70 cells priced**, **47 FAIL**, **126 unpriced**; reference `sprout -> grafted` 1100 power / 120 souls; derived `forge-gem` coefficients printed per failing cell |
| names the cells SSH8.5 fixes | (above) | RED by design and names them: 47 cells cheaper than the rarity route each with its lever + required coefficient, 126 unpriced cells (SSH4.4's un-materialised families) |
