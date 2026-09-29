# Spec: rung-table-activation (ST5)

**Status: proposed 2026-09-18.** Module **ST5** of [action-skill-tiers-map.md](../action-skill-tiers-map.md).
Depends on **ST3** and **ST4**. Not approved; no build authorized.

## Objective

**Make A-G1's budget check run in production, and keep every reader of the rung table on one version.**

A-G1 is recorded as *"FULLY BUILT + WIRED"* (`action-corpus-map.md`, verified-status table) and the ideal
repeats it (ideal, Built: *"Tier-access-gate A-G1 built and wired"*). The caller is real —
`RpgStore.ActionCatalog.cs:105-110` — but every production process loads the table **without** the
budget column:

| Reader | File it loads | Evidence |
|---|---|---|
| Server (`RungPolicy.Configure`) | `action-rungs.v1.json` | `gk-core/src/FusionRpg.Server/Program.cs:260` |
| Injector host | `action-rungs.v1.json` | `RpgHost.cs:225-227` |
| Seedsmith A-S0 characteristic pool | `action-rungs.v1.json` | `characteristic_pool/pool.py:31` |
| Seedsmith A-S1 planner | `action-rungs.v1.json` (→ v3 by ST3) | `generate_distribution_planner.py:60` |
| Seedsmith A-S4 validate-heal | `action-rungs.v1.json` | `generate_validate_heal.py:54` |

v1 has no `powerBudgetMilli`, so `RungRow.PowerBudgetMilli` is `null` (`RungRow.cs:14-18`) and the check
**skips every action** (`RpgStore.ActionCatalog.cs:96-101`: *"A container the loaded rung table cannot
price … is skipped, not failed"*). A-G1 is inert in production. v2 exists with the column
(`action-rungs.v2.json`, published by A-G1) and nothing in production reads it.

The pinned-filename pattern is the repo's own (every `*Policy.Configure` in `Program.cs` names a
version, and reverting is pointing back — `gk-core/src/FusionRpg.Server/Program.cs`). The defect is not the pinning; it is that
publishing v2 moved no reader, and nothing noticed.

## Contract

1. **One version.** The server, the injector and every seedsmith reader load the same
   `action-rungs.v{n}.json` — **v4**: ST3's v3 (`scopeWindows`) with the budget repriced at ST4's R8
   value (map §5.1). Pointing production at v3 would switch on the budget at the untuned
   `referencePower = 1000`, which R8 rules out.
2. **That version carries the budget.** Every row of the version production loads has
   `powerBudgetMilli`, so A-G1's check evaluates every containered action.
3. **Guard — parameterised by domain.** One Guard.Tests theory, `TuningVersionAgreement(domain)`, finds
   every `<domain>.v<n>.json` token inside a **string literal** in `src/` (not tests, not `bin`/`obj`) and
   in `gk-forge/tools/seedsmith/seedsmith/`, and asserts they name **one** version. Comment lines (`//`, `///`,
   `#`) are skipped; string literals are not, whatever precedes the filename inside them — so
   `pool.py:85`'s `"gk-core/data/tuning/action-rungs.v1.json"` provenance string is matched (it is emitted into
   generated data and must move with the readers), while `AuraTuning.cs:86`'s message
   `"(action-rungs.v1.json's own cap)"` is matched too and is corrected to name no version (a message
   that names a stale file is the drift this guard exists for). Rows: `action-rungs` (this module) and
   `action-base` (`action-enrich` `lawn-action-base`: the server and the injector load one version).
   For `action-rungs` it then loads the agreed file through `RungTableLoader.Parse` and asserts every
   row's `PowerBudgetMilli` is present. The guard asserts agreement, not "latest": pointing every reader
   back at an older version to revert a balance pass stays legal.
4. **Activation precondition.** v4 exists, published by ST4 at the first report's
   `recommendedReferencePower` (R8; ST4 contract 6). By that rule no committed containered action exceeds
   the live budget; the change description re-runs the report against v4 and states "0 rejected", or lists
   by id any action imported **after** the report that now exceeds it. Activation never silently drops
   content nobody saw.
5. **The injector moves with the server.** It reads the rung table for swing charging
   (`RpgHost.cs:216-227`); it must not price a swing from a different table than the server compiles
   actions from.

## Tunables

None new. The version pointer is not a tunable; it is which published tunable file is live.

## Numeric types

No arithmetic added. The budget arithmetic is A-G1's, already `long` (`RungRow.cs:29`).

## Seedsmith / generator

| Stage | File:line | Change |
|---|---|---|
| A-S0 characteristic pool | `characteristic_pool/pool.py:31` | Path → the one version |
| A-S0 characteristic pool | `characteristic_pool/pool.py:85` | Provenance string → the one version (it is written into `gk-data/packs/fusion/data/seed/actions/_generated/characteristic-pool.json`'s `sourceVocabulary`) |
| A-S1 planner | `generate_distribution_planner.py:60` | Already moved by ST3; guarded here |
| A-S4 validate-heal | `generate_validate_heal.py:54` | Path → the one version |
| Seed fields | — | None. No seed file changes |

All three read `rows[].structureBudget` only, and those are identical across v1–v4, so the regenerated
output must be **byte-identical except one line**: the characteristic pool's `sourceVocabulary` string,
which names the rung-table file (`pool.py:85`). (Corrected 2026-09-18, strengthen pass: an earlier draft
claimed full byte-identity.)

```powershell
cd gk-forge/tools/seedsmith
python -m seedsmith.adapters.actions.generate_characteristic_pool --dry-run
python -m seedsmith.adapters.actions.generate_distribution_planner --dry-run
python -m seedsmith.adapters.actions.generate_validate_heal --round 1 --dry-run
```

Model stages A-P1/A-P2/A-P3 are not run and are not affected.

## Commands

```powershell
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCatalog"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ActionCorpusImport|FullyQualifiedName~UnlockTuningActivation"
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m pytest gk-forge/tools/seedsmith/tests/test_characteristic_pool.py gk-forge/tools/seedsmith/tests/test_distribution_planner.py gk-forge/tools/seedsmith/tests/test_validate_heal.py -q
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

This change crosses Server, Injector and seedsmith, so it is one of the three points `AGENTS.md`
names for the full suite (*"a change that crosses program or module boundaries"*). An injector build
needs the game's interop references (`FUSIONRPG_GAME_DIR` / the MelonLoader default).

## Project structure

```
gk-core/src/FusionRpg.Server/Program.cs                                           (one path)
gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs                                    (one path)
gk-forge/tools/seedsmith/seedsmith/adapters/actions/characteristic_pool/pool.py    (one path)
gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_validate_heal.py      (one path)
gk-forge/tools/seedsmith/seedsmith/adapters/actions/characteristic_pool/pool.py    (:85 provenance string)
gk-core/src/FusionRpg.Core/Aura/AuraTuning.cs                                     (:86 message stops naming a version)
gk-data/packs/fusion/data/seed/actions/_generated/characteristic-pool.json                      (regenerated, one line)
gk-core/tests/FusionRpg.Guard.Tests/…TuningVersionAgreementGuardTests.cs          (new, parameterised by domain)
```

## Code style

```csharp
// ST5 (action-skill-tiers): v1 -> v4. v4 = v3's scopeWindows (ST3) + powerBudgetMilli repriced at the
// first calibration report's referencePower (ST4, R8).
// Every rung-table reader names the same version (TuningVersionAgreementGuardTests). v1/v2 stay on disk --
// reverting is pointing every reader back, together.
FusionRpg.Core.Actions.Rungs.RungPolicy.Configure(
    FusionRpg.Core.Actions.Rungs.RungTableLoader.Parse(
        File.ReadAllText(Path.Combine(tuningDir, "action-rungs.v4.json"))));
```

## Testing strategy

| # | Test | Proves |
|---|---|---|
| 1 | Guard: every quoted rung-table filename in `src/` and seedsmith names one version | Contract 1, 3 |
| 2 | Guard: that version's every row carries `powerBudgetMilli` | Contract 2 |
| 3 | **Planted violation:** a probe file with a second version literal fails the guard (written and removed inside the test, never left on disk — `guard-probe-leftovers` is a known hazard) | Contract 3 |
| 4 | A real store, real import, real `BuildActionCatalog` with the live table: a planted over-budget container is rejected with `PowerBudgetExceeded` naming its id | Contract 2 — the check is live, not skipped |
| 5 | The three seedsmith `--dry-run` outputs equal their pre-change outputs, except the pool's `sourceVocabulary` line, which names the new version | Regeneration is content-neutral |
| 6 | `TuningVersionAgreement("action-base")` passes with the server and injector on one version, and fails on a planted mismatch | Contract 3, `action-base` row |

No test pins which version is live, how many actions pass the budget, or a budget value.

## Boundaries

- **Always:** move every reader together; state in the change description which actions (if any) the
  live budget now rejects.
- **Ask first:** activating against any version other than the R8-tuned one.
- **Never:** hand-edit any `action-rungs.v*.json`; delete v1/v2 (they are the revert path); make the
  guard demand the latest version.

## Success criteria

1. Production loads a rung table whose every row carries `powerBudgetMilli`.
2. A-G1's check evaluates every containered action in production.
3. Every rung-table reader names the same version, and a mismatch fails CI.

## Follow-ups this module owes other programs (named, not done here)

- `action-corpus-map.md`'s A-G1 status line and the five specs that restate the gate
  (`spec-tier-access-gate.md` §7) should say **live** after this lands. Those files are action-corpus's.
- The ideal's "Built" bullet on A-G1 (ideal line 50) is corrected by the status line this program adds
  to the ideal.

## Self-audit (debate pass)

- *"Just point the server at v2 now — why wait for ST4?"* Because the check rejects content: turning it
  on unmeasured can drop real actions from every battle's catalog, visible only as `onRejected`
  callbacks. Ruling 3 accepted a neutral scalar; it did not accept an unmeasured rejection.
- *"A const shared across Server and Injector instead of a guard?"* Every other policy file in
  `Program.cs` is named inline; a one-off shared const for one domain would be a second convention.
  The guard enforces the property the convention needs without changing it.

## Open questions

None. R8 removed the precondition's owner branch.
