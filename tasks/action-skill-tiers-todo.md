# Todo: `action-skill-tiers` (ST)

Plan: [action-skill-tiers-plan.md](action-skill-tiers-plan.md) · Map:
[action-skill-tiers-map.md](../docs/architecture/action-skill-tiers-map.md) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane A).

Id scheme: `ST<module>.<n>`. Order is **suggested, not enforced**, except where an entry marks a parent
hard edge (H1, H7). `<session>` is the building session's id. Every task is verified once with
`verify-change.ps1` over all the paths it touched. The full suite runs only at Checkpoint 5.

---

## Wave 1 — ST2 `holder-rung-pricing` (lane A's first task; fixes a live defect)

- [x] **ST2.1 — Rename `CompiledActionCost.ScaledAmount` → `Amount` (no behaviour change)** · XS · deps: — · *(spec: holder-rung-pricing)*
  - Acceptance: no `ScaledAmount` identifier is left in `src/`, `tests/` or `tools/`. Every existing
    test stays green and `BattleGoldenTests` shows no change.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Actions/CompiledAction.cs,gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs,gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs,gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,gk-core/tests/FusionRpg.Core.Tests/Actions/ActionCatalogTests.cs,gk-core/tests/FusionRpg.Core.Tests/Actions/PoiseLedgerTests.cs,gk-core/tools/PoiseProbe/Program.cs -Session <session>`
  - Files: the 7 above. This is **over 5 on purpose**: it is an atomic mechanical rename and does not
    compile if split. The spec listed only 4 of these files. `CostLedger.cs`, `PoiseLedgerTests.cs` and
    `gk-core/tools/PoiseProbe/Program.cs` also read the field (grep, 2026-09-18).

- [x] **ST2.2 — Cost is scaled once, in `CostLedger` only (fixes the live `costMulti²` defect)** · S · deps: ST2.1 · *(spec: holder-rung-pricing, contract 5)*
  - Acceptance: `ActionCompiler` no longer pre-scales cost, and `Costs[0].Amount` equals the authored
    `ValueSpec` (spec test 8; the stale `ActionCatalogTests.cs:360-376` assertion is rewritten to the
    contract).
  - Acceptance: a non-held action at authored rung `r` pays `base × costMulti(r)` exactly once, with
    `costMulti` read from the loaded row and never written as a literal. **Planted violation:** putting
    the compile-time pre-scale back fails this test (spec test 5).
  - Acceptance: `ActionCostsCooldownsAdoptionTests` pass unchanged (spec test 6). Run
    `BattleGoldenTests` and **record** whether any golden moved. Do not re-bless here.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CostLedger|FullyQualifiedName~ActionCostsCooldownsAdoption|FullyQualifiedName~ActionCatalog"` then `.\scripts\verify-change.ps1 -Paths <files> -Session <session>` and `python scripts\audit-overflow.py --targets A3`
  - Files: `gk-core/src/FusionRpg.Core/Actions/ActionCompiler.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionCatalogTests.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/HolderRungPricingTests.cs` (new)

- [x] **ST2.3 — Golden re-bless #1 (H1): cost scaled once** · XS · deps: ST2.2 · *(spec: holder-rung-pricing, Goldens)*
  - Acceptance: every battle golden that moved in ST2.2 is re-blessed in **its own commit**. The commit
    message and the golden note name ST2 and the cause (cost is now scaled by `costMulti`, not
    `costMulti²`). If nothing moved, the commit or the task says "ST2 moved no golden" and nothing is
    re-blessed.
  - Acceptance: this is the first commit in the parent's H1 chain. No other cause's golden change is in
    it.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"`
  - Files: `tests/FusionRpg.Core.Tests/Goldens/**` (only the files that moved)

- [x] **ST2.4 — `UnlockLadder.EffectiveRung` gains a window bound** · S · deps: — · *(spec: holder-rung-pricing, contracts 1–3)*
  - Acceptance: with window `[1,4]`, an `earnCount` above 4 gives 4 and one below 4 gives `earnCount`.
    With a `null` window the result equals the 2-argument form over a spread of inputs (spec tests 1, 2).
  - Acceptance: the window's `Floor` never raises the result (`earnCount 1`, window `[3,10]` → 1; spec
    test 3). The 2-argument form delegates with `null`, so no current caller changes.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~UnlockLadder|FullyQualifiedName~RungSemantics"`
  - Files: `gk-core/src/FusionRpg.Core/Actions/Unlock/UnlockLadder.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/UnlockLadderTests.cs`

- [x] **ST2.5 — The band reaches the battle through the one instance resolver** · S · deps: ST2.4 · *(spec: holder-rung-pricing, contract 4)*
  - Acceptance: `CompiledAction` carries `RungBand? RungBand`, copied by `ActionCompiler`.
    `BattleRunState.EffectiveRungOf` is a public **instance** method (created here unless `AE1.2`
    already created it; if so, add only the band line) and is passed to `CostLedger` as `rungOf`.
  - Acceptance: a held corpus action priced through a real `BattleEngine.Resolve` pays at
    `min(earnCount, ceiling)` (spec test 4). `RungSemanticsTests`' guard-reads-authored test passes
    unchanged, and `StructureBudgetGuard` is not edited (spec test 7).
  - Acceptance: `BattleGoldenTests` show no change. Production passes no `unlockStateFor` today, so the
    bound is inert there until action `T74`.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~HolderRungPricing|FullyQualifiedName~RungSemantics|FullyQualifiedName~BattleGolden"` then `.\scripts\verify-change.ps1 -Paths <files> -Session <session>`
  - Files: `gk-core/src/FusionRpg.Core/Actions/CompiledAction.cs`, `gk-core/src/FusionRpg.Core/Actions/ActionCompiler.cs`, `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/HolderRungPricingTests.cs`

### Checkpoint 2 — one rung reading prices one holder
- [x] ST2.1–ST2.5 green. A cost is scaled once, and a held action's effective rung never exceeds its
  window ceiling.
- [x] The ST2.3 re-bless commit exists (or "no golden moved" is recorded), and it is the first commit
  of the H1 chain.
- [x] `audit-overflow.py --targets A3` is clean for the touched files.

---

## Wave 2 — ST1 `composer-tier-window`

- [x] **ST1.1 — Composer filters by the rung's tier window, stamps it, and checks itself** · M · deps: — · *(spec: composer-tier-window, contracts 1, 2 (refusal), 3, 4, 5)*
  - Acceptance: a brief whose families hold atoms from t1 to t5 composes only in-window atoms. The
    container carries `MinTier`/`MaxTier`, and every out-of-window atom appears in `Dropped` with the
    tier reason (spec tests 1, 2).
  - Acceptance: a brief with no in-window atom is refused naming the window. A two-tier rung window is
    refused naming the missing weight source. **Planted violation:** keeping an out-of-window atom trips
    the post-condition (spec tests 3, 4, 5).
  - Acceptance: composing the same brief twice gives a byte-identical container (spec test 6). No test
    asserts a corpus count or which atom was drawn.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionCorpusComposer|FullyQualifiedName~ComposerTierWindow"`
  - Files: `gk-core/src/FusionRpg.Core/Actions/Corpus/ActionCorpusComposer.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Corpus/ComposerTierWindowTests.cs` (new)

- [x] **ST1.2 — A stored action whose brief now refuses is disabled, and the catalog skips it** · S · deps: ST1.1 · *(spec: composer-tier-window, contract 2 second half, contract 3)*
  - Acceptance: re-importing over a store that holds the pre-window container bumps its revision. It is
    neither a no-op nor a failure (spec test 7).
  - Acceptance: when a previously imported brief now refuses, the stored row is upserted with
    `Enabled = false` (a revision bump, never a delete) and reported as its own outcome. It is absent
    from `BuildActionCatalog` (spec test 8). No new `ActionRejectionReason` member is added.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCorpusImport"` then `.\scripts\guard-dal.ps1` and `python gk-core/scripts/guard-test-substrate.py`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/ActionCorpusImporter.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionCatalog.cs`, `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionCorpusImporterTests.cs`

- [x] **ST1.3 — Golden re-bless #2 (H1): corpus action content changed** · XS · deps: ST1.2, **ST2.3 (H1)** · *(spec: composer-tier-window, Goldens)*
  - Acceptance: any golden moved by ST1 is re-blessed in its own commit, which names ST1 and the cause
    (the drawn atoms are now inside the window). If nothing moved, record "ST1 moved no golden".
  - Acceptance: the commit comes after ST2.3's and shares no cause with it.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"`
  - Files: `tests/FusionRpg.Core.Tests/Goldens/**` (only the files that moved)

### Checkpoint 1 — the tier window is real
- [x] After a server re-import, every imported action's fixed atoms lie inside its authored rung's
  `[MinTier, MaxTier]`, and the container carries that window. Show this with a test over the real
  import path, not a count.
- [x] Refused briefs are reported by id, and the disabled rows are absent from the catalog.
- [x] The ST1.3 re-bless commit (or its no-move note) comes after ST2.3's.

---

## Wave 3 — ST3 `scope-window-tunables` (Python; parallel with waves 1–2)

- [x] **ST3.1 — Publish `action-rungs.v3` `scopeWindows`, and the planner reads it through one loader (H7)** · M · deps: — · *(spec: scope-window-tunables, contracts 1, 2, 5)*
  - Acceptance: v3 is written **by `publish.py --add-key`** (never by hand), with `{floor, ceiling}`
    objects at the shipped values and the `_meta` line. `set scopeWindows.family.ceiling=6` writes an
    `int`, and a second `--add-key` is refused (spec test 7).
  - Acceptance: `load_scope_windows` refuses each of these, naming the key: a missing scope, a
    non-`int` bound, a floor other than 1, a ceiling outside `1..cap`, and non-monotone ceilings. A
    12-row contiguous fixture loads, so the `cap == 10` literal is gone (spec tests 2, 2b, 3, 4).
  - Acceptance: the planner's windows **equal the file's block**. The literal pin at
    `test_distribution_planner.py:510` is replaced, and a `family [1,6]` fixture yields `rungBand [1,6]`
    briefs (spec tests 1, 5). `generate_distribution_planner.py:60` points at v3 in the same commit as
    the publish (H7).
  - Verify: `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_distribution_planner.py -q; python -m pytest gk-core/tools/tuning -q`
  - Files: `gk-core/data/tuning/action-rungs.v3.json` (published), `gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_distribution_planner.py`, `gk-forge/tools/seedsmith/tests/test_distribution_planner.py`, `gk-core/tools/tuning/test_publish_add_key.py`

- [x] **ST3.2 — Coverage report and innate picker take the loaded windows, and `RUN_WINDOW` is deleted** · S · deps: ST3.1 · *(spec: scope-window-tunables, contract 3)*
  - Acceptance: `coverage_report/derive.py:45,180,671` and `innate_picker/derive.py:65,103` receive
    windows from their entrypoints. `grep RUN_WINDOW gk-forge/tools/seedsmith` returns nothing.
  - Acceptance: both suites pass, and a retuned-window fixture reaches each stage's output.
  - Verify: `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_coverage_report.py gk-forge/tools/seedsmith/tests/test_innate_picker.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/actions/coverage_report/derive.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/innate_picker/derive.py`, `generate_coverage_report.py`, `generate_innate_picker.py`, `gk-forge/tools/seedsmith/tests/test_coverage_report.py`, `gk-forge/tools/seedsmith/tests/test_innate_picker.py`. That is 6 files: two stages, each with its derive, entrypoint and test. Deleting `RUN_WINDOW` needs both stages in one change.

- [x] **ST3.3 — General and family propose prompts label by scope** · S · deps: ST3.1 · *(spec: scope-window-tunables, contract 4)*
  - Acceptance: each `_RUNG_BAND_LABELS` becomes `{scope: label}` with a direct index, so an unknown
    scope raises. A fixture brief of each scope renders byte-identical to its pre-change output (spec
    test 6).
  - Acceptance: with `family.ceiling = 6`, the family prompt renders the family label and never the
    "outside the three known scope windows" fallback (spec test 6b). No model is called.
  - Verify: `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_general_propose.py gk-forge/tools/seedsmith/tests/test_family_propose.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/actions/general_propose/prompts.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/family_propose/prompts.py`, `gk-forge/tools/seedsmith/tests/test_general_propose.py`, `gk-forge/tools/seedsmith/tests/test_family_propose.py`

- [x] **ST3.4 — Signature propose prompt labels by scope** · S · deps: ST3.1 · *(spec: scope-window-tunables, contract 4)*
  - Acceptance: the same contract as ST3.3 for `signature_propose`: byte-identical at the shipped
    windows, and an unknown scope raises. No model is called.
  - Verify: `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_signature_propose.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/actions/signature_propose/prompts.py`, `gk-forge/tools/seedsmith/tests/test_signature_propose.py`

- [x] **ST3.5 — Model-free regenerate proves byte-identity, and the `ssot-power-scale.md` §11 row is written** · S · deps: ST3.2, ST3.3, ST3.4 · *(spec: scope-window-tunables, contract 6, Seedsmith)*
  - **ERRATUM (manager ruling 2026-09-19; amends the acceptance below and the spec's contract 6 /
    success criterion 3).** Two corrections, both from the ST3.5 run:
    1. **Byte-identity means identical CONTENT modulo the provenance hash**, not an empty diff. The
       rung table's version is folded into `_corpus_hash`, so pointing the planner at v3 moves
       `_meta.corpusHash` and every brief's `_provenance.corpusHash` by design (H7 taken seriously:
       the artifact's provenance now names its real input). Nothing else may differ.
    2. **The regenerate chain is the real pipeline order, not the three commands below.** That order is
       `generate_action_pipeline.run_pipeline`'s: characteristic_pool → type_weights → distribution
       planner (`--full`) → **`coverage_assignment` (A-S7)** → … → innate_picker → coverage_report.
       A-S7 is the one the acceptance omitted, and it is load-bearing here: it is what splices
       `requiredFamilies` into the plan, so a planner-only "real" run *drops* that splice and looks
       like a content regression when it is a missing pipeline stage.
  - Acceptance: the model-free chain runs for real in the order above, and every file it rewrites is
    **content-identical to HEAD with every `corpusHash` field removed**. A difference in any other
    field is a defect in ST3, never new content.
  - Acceptance: §11 gains the `scopeWindows` row (A-U1 §3.4), written with the power program's review.
    `audit-magic-numbers.py --summary` shows no new window literal.
  - Verify: `cd gk-forge/tools/seedsmith; python -m seedsmith.adapters.actions.generate_distribution_planner --dry-run; python -m seedsmith.adapters.actions.generate_coverage_report --round 1 --dry-run; python -m seedsmith.adapters.actions.generate_innate_picker --round 1 --dry-run` then `git diff --stat gk-data/packs/fusion/data/seed/actions/` — note the planner's own `--dry-run` refuses without `--full`
    (`refuse_full_run_if_ungated`), so the dry-run form can only cover two of the three.
  - Files: `docs/architecture/power/ssot-power-scale.md`

### Checkpoint 3 — the windows are tunable
- [x] No rung window value is left in seedsmith code or tests (grep). A retune is one `publish.py` call
  plus a planner re-run.
- [x] At the shipped values, every regenerated seed file and every propose prompt is byte-identical.

---

## Wave 4 — ST4 `budget-calibration-report`

- [x] **ST4.1 — One pricing helper shared by the catalog check and the report** · S · deps: — · *(spec: budget-calibration-report, contracts 1, 3)*
  - Acceptance: the atom fetch + `ActorPowerCache.Compose` block (`RpgStore.ActionCatalog.cs:84-90`) is
    one private helper. `ListActionPricing` returns every containered action, **including** ones the
    budget rejects (spec test 4).
  - Acceptance: **planted violation:** swapping in a second pricing function fails a test that compares
    the report's realized power with the catalog check's realized power (spec test 5).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCatalog|FullyQualifiedName~ActionPricing"` then `.\scripts\guard-dal.ps1` and `python gk-core/scripts/guard-test-substrate.py`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionCatalog.cs`, `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionPricingTests.cs` (new)

- [x] **ST4.2 — Pure `BudgetCalibration.Read` and `recommendedReferencePower`** · S · deps: — · *(spec: budget-calibration-report, contracts 2, 6)*
  - Acceptance: an action priced exactly on budget at `REF` reads `REF`. Σ per-rung `n` equals the
    number of priced actions, and each id appears once. `min ≤ p50 ≤ p90 ≤ max`, and an empty rung
    reports no percentiles (spec tests 1–3).
  - Acceptance: repricing at `recommendedReferencePower` rejects no priced action, and repricing at
    that value − 1 rejects the action that set the max (spec test 9; this tests a property, not a value).
  - Acceptance: the arithmetic is `checked` `long`, and it throws on overflow and on a zero divisor (spec
    test 6). No test pins a percentile or a `referencePower`.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BudgetCalibration"` then `python scripts\audit-overflow.py --targets A3`
  - Files: `gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Actions/Rungs/BudgetCalibrationTests.cs` (new)

- [x] **ST4.3 — `GET /api/debug/action-budget-report` (RPG Server Debug, read-only)** · S · deps: ST4.1, ST4.2 · *(spec: budget-calibration-report, contract 4)*
  - Acceptance: against a store seeded through the **real** import path, the endpoint returns the report
    and performs no write (spec test 7). It is labelled RPG Server Debug per `live-probe-standard.md`.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ActionBudgetReport"` then `.\scripts\guard-dal.ps1`
  - Files: `gk-core/src/FusionRpg.Server/DebugEndpoints.cs`, `tests/FusionRpg.Server.Tests/Actions/ActionBudgetReportTests.cs` (new)

- [x] **ST4.4 — `publish.py --reprice-rung-power-budget REF` + `--mark-tuned`** · S · deps: — · *(spec: budget-calibration-report, contract 5)*
  - Acceptance: `--reprice-rung-power-budget 800` writes v{n+1}. Every row equals the published
    derivation at 800, `_meta.referencePower == 800`, and `referencePowerUntuned` stays `true` unless
    `--mark-tuned` is given. A table without the column is refused (spec test 8).
  - Verify: `python -m pytest gk-core/tools/tuning -q`
  - Files: `gk-core/tools/tuning/publish.py`, `gk-core/tools/tuning/test_publish_reprice.py` (new)

- [x] **ST4.5 — The first reading over the real imported catalog (R8 input)** · S · deps: ST4.3, ST4.4, **ST1.2** · *(spec: budget-calibration-report, contract 6)*
  - Acceptance: the server has re-imported the corpus with ST1 in place, and that is confirmed **before**
    the reading. The report is saved to `docs/research/action-corpus/_budget-<date>.json` and committed.
  - Acceptance: the task records `recommendedReferencePower` and lists by id the actions above the
    report's p90. It does **not** publish v4: that happens in ST5.2's commit (H7; see the plan's
    "Reconciling H7").
  - Verify: `curl.exe -s http://127.0.0.1:5088/api/debug/action-budget-report > docs\research\action-corpus\_budget-<date>.json` (server started with `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`, not `deploy-play`)
  - Files: `docs/research/action-corpus/_budget-<date>.json` (new)

### Checkpoint 4 — the budget is measured before it bites
- [x] The report is committed for the real imported catalog, and its realized power matches the catalog
  check by construction (ST4.1's planted test is green).
- [x] `recommendedReferencePower` is stated, and the outliers above p90 are listed by id.
- [x] `publish.py --reprice-rung-power-budget … --mark-tuned` is tested and ready for ST5.2.

---

## Wave 5 — ST5 `rung-table-activation`

- [x] **ST5.1 — `TuningVersionAgreement(domain)` guard, fixture-driven, plus the `AuraTuning` message fix** · S · deps: — · *(spec: rung-table-activation, contract 3)*
  - Acceptance: the scan takes its roots as parameters. It matches `<domain>.v<n>.json` inside string
    literals, skips comment lines, and asserts one version. **Planted violation:** a probe that holds a
    second version fails. The probe is written and removed inside the test, and a failed delete fails
    the test (spec test 3).
  - Acceptance: `AuraTuning.cs:86`'s message no longer names a version. The real-tree `action-rungs` row
    is **not** added here. It lands in ST5.2, where the readers start agreeing.
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"`
  - Files: `gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs` (new), `gk-core/src/FusionRpg.Core/Aura/AuraTuning.cs`

- [x] **ST5.2 — Publish v4 at the R8 value, and switch every reader in the same commit (H7)** · M · deps: ST3.1, ST4.5, ST5.1 · *(spec: rung-table-activation, contracts 1, 2, 4, 5; budget-calibration-report contract 6)*
  - Acceptance: v4 is published by `publish.py action-rungs --label "R8 first calibration (<report>)"
    --reprice-rung-power-budget <ST4.5 value> --mark-tuned` on top of v3. `Program.cs`, `RpgHost.cs`,
    `pool.py:31,85`, `generate_validate_heal.py:54` and `generate_distribution_planner.py:60` all name v4
    in the **same commit**, and the guard's `action-rungs` row is added and green (spec tests 1, 2).
  - Acceptance: the three seedsmith `--dry-run` outputs are byte-identical except the
    `characteristic-pool.json` `sourceVocabulary` line, which is regenerated and not hand-edited (spec
    test 5).
  - Acceptance: the change description re-runs the ST4 report against v4 and states "0 rejected", or
    lists by id any action imported after the reading.
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"`; `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_characteristic_pool.py gk-forge/tools/seedsmith/tests/test_distribution_planner.py gk-forge/tools/seedsmith/tests/test_validate_heal.py -q`; then `.\scripts\deploy-play.ps1 -NoServer -Paths <files>` (injector build)
  - Files: `gk-core/data/tuning/action-rungs.v4.json` (published), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/characteristic_pool/pool.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_validate_heal.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_distribution_planner.py`, `gk-data/packs/fusion/data/seed/actions/_generated/characteristic-pool.json` (regenerated), `gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs`. This is **over 5 files on purpose**: H7 and contract 1 require one atomic switch, and each source edit is a single filename token.

- [x] **ST5.3 — The budget check is live against the real table** · S · deps: ST5.2 · *(spec: rung-table-activation, contract 2)*
  - Acceptance: with a real store, the real import and a real `BuildActionCatalog` loading the table
    production loads, a planted over-budget container is rejected with `PowerBudgetExceeded` naming its
    id (spec test 4). No test pins a version, a pass count or a budget value.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCatalog"` then `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ActionCorpusImport|FullyQualifiedName~UnlockTuningActivation"`
  - Files: `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionBudgetLiveTests.cs` (new)

- [x] **ST5.4 — `action-base` row of the version-agreement guard** · XS · deps: ST5.1, `AE2.2` · *(spec: rung-table-activation, contract 3 / test 6)*
  - Acceptance: `TuningVersionAgreement("action-base")` passes with `Program.cs` and `RpgHost.cs` on one
    version, and fails on a planted mismatch.
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"`
  - Files: `gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs`

- [x] **ST5.5 — Status lines, and the follow-up owed to action-corpus** · XS · deps: ST5.3 · *(spec: rung-table-activation, "Follow-ups")*
  - Acceptance: `action-skill-tiers-ideal.md` gains a status line saying A-G1 is **live** as of ST5, which
    corrects its line-50 "built and wired" claim. The map's module table marks ST1–ST5 built, with commit
    ids.
  - Acceptance: the follow-up for action-corpus is recorded as a named item, not an edit to its files.
    `action-corpus-map.md`'s A-G1 status and the five specs in `spec-tier-access-gate.md` §7 need to say
    "live".
  - Verify: manual re-read. `grep -n "built and wired" docs/architecture/action-skill-tiers-ideal.md` shows the corrected status beside it.
  - Files: `docs/architecture/action-skill-tiers-ideal.md`, `docs/architecture/action-skill-tiers-map.md`

### Checkpoint 5 — A-G1 is live (program final checkpoint)
- [x] The server, the injector and every seedsmith reader load v4, and the guard is green for
  `action-rungs` (and for `action-base` once ST5.4 lands).
- [x] "0 rejected" (or the rejected ids) is stated in ST5.2's change description, and ST5.3 proves the
  check actually evaluates.
- [x] **Full suite** (`.\scripts\test-fast.ps1 -AllDefault`), run once here: ST5 crosses Server, Injector
  and seedsmith (AGENTS.md full-suite point 2). All six boundary guards are green.
- [x] Map success criteria 1–7 hold: no `tier` column or field, no new curve, no model call, no
  hand-edited seed, and no test that pins a population or a tunable.
