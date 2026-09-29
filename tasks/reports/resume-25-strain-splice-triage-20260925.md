# Resume 25 — `strain-splice-host` dependency triage

**Date:** 2026-09-25
**Branch:** `opencode/resume-25-strain-splice-triage-20260925`
**Scope:** read-only triage; this report is the only file written, and no tracked file was changed. No product code, generated corpus, tuning, CI, ledger, or session-record changes were made. No model call or tuning publication was run.

## Decision

Dispatch **`SSH7.1`** as the primary row, with **`SSH8.4`** as the explicitly named companion in the same guard-only change. Both remaining lines live in the same protected guard and need no publish; combining them avoids reopening the same path twice while keeping the row bookkeeping separate. The parser and current-revision reader contracts are already landed, so the missing work is a guard and the current test-reader conversions that the guard exposes. It needs neither a live save/game probe nor a tuning publish.

If the manager wants one-row accounting, dispatch `SSH7.1` first and carry `SSH8.4` as a named companion, not as a hidden scope expansion. `SSH7.7` remains a publish/H7 slice, and `SSH4.9` remains live-only.

## Baseline and task-block accounting

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` reports for `strain-splice-host`:

- **9 open task blocks**, **69 done blocks**;
- **32 unticked boxes**, **19 shaded**.

The checkbox counts are not the work count. The nine open task blocks are the four implementation rows (`SSH4.9`, `SSH7.1`, `SSH7.7`, `SSH8.4`) plus `TVB-F18`, `SSH4.9-P1`, `SSH4.9-F3`, `SSH4.9-F4`, and `SSH-F7`.

## Current contract readback

The current code supports a guard-only next step; the stale todo prose does not need to be trusted for this conclusion.

| Surface | Current evidence | Consequence |
|---|---|---|
| C# filename SSOT | `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs:25-38` defines `Current = sockets.v3.json`, `StrainSplice = strain-splice.v1.json`, and `Materials = materials.v6.json`. | The strain-splice constant and its current revision are already present. |
| Server boot reader | `gk-core/src/FusionRpg.Server/Program.cs:443-454` loads `SocketTuningFiles.Current` and `SocketTuningFiles.StrainSplice` and cross-validates the parsed strain tuning against socket tuning. | The production server reader is already on the constant; there is no server filename edit in this slice. |
| Python reader | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:23-26,192-210` defines `STRAIN_SPLICE_PATH` and makes it the default input to `load`. | The Python mirror is present. Its existing path-literal test still covers only `sockets`; the full “every reader” claim needs a Python scan extension. |
| Parser | `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs:117-163,172-231` parses the optional ladder, maps an absent ladder to the one-rung floor, and throws on invalid ladders. | Do not reimplement the parser half of `SSH7.1`; its focused tests are already green. |
| Runtime target/read path | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EquipCombinations.cs:72-120` evaluates the current fill and ensures the corresponding combination container instance; `gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs:45-75` recognizes bindings only against current targets. | The reader/writer seam is already coherent. This is not evidence for a real persisted-save/game probe. |
| Workbench/card inputs | `gk-core/src/FusionRpg.Server/ItemWorkbench.cs:222-260` receives the material tuning by injection; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemCard.cs:243-252` threads the base-type socket capacity. | No live-only write path needs changing for the guard slice. |

### Guard gap found at the current head

`gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs:21-101` currently has only:

```text
sockets\.v[0-9]+\.json
```

It has no `strain-splice.v{n}.json` rule and no `materials.v{n}.json` rule; the latter is the exact remaining guard line for the companion `SSH8.4`. The existing C# scan covers `src`, `tools`, and `tests`, while the existing Python scan in `gk-forge/tools/seedsmith/tests/test_combogen.py:602-621` covers only Python path joins for `sockets`.

A blind regex extension is not sufficient for a truthful full-reader closure: the current tree still has these real strain-splice test readers, not comments:

- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs:105`
- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs:29`
- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:39,225,250,298,590`
- `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:43,51`
- `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs:43`

The companion materials scan currently exposes these additional shipped-file readers (the `SocketTuningFiles.Materials` declaration itself is the one allowed constant):

- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs:22`
- `gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs:43`
- `gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs:43`
- `gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs:72,706,747`
- `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs:82`
- `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs:83,686`
- `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs:135`

`gk-core/src/FusionRpg.Core/Items/Materials/MaterialRecipeCatalog.cs:437` contains the stale-looking `materials.v1.json` in an exception message, not a reader. A new guard should distinguish path literals from prose (or explicitly test that distinction), not turn that message into a hidden allowlist entry. The Python materials mirror is `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/brief.py:38`.

They should use `SocketTuningFiles.StrainSplice` or `SocketTuningFiles.Materials`, just as the already-converted tests use `SocketTuningFiles.Current`. Do not add a blanket allowlist that hides these readers. The row’s listed `gk-core/tests/FusionRpg.Core.Tests/...` path is also stale after the Core test-project split; the current paths are under `gk-core/tests/FusionRpg.Core.Items.Tests/...`.

## Recommended slice: `SSH7.1` primary, with `SSH8.4` as the same guard-file companion

**Primary row:** `SSH7.1` in `tasks/strain-splice-host-todo.md:621-642`
**Primary acceptance line:** `every_reader_loads_the_current_strain_splice_revision`
**Companion row:** `SSH8.4` in `tasks/strain-splice-host-todo.md:794-812`; its only remaining line is `every_reader_loads_the_current_materials_revision`.
**Why it is next:** both parsers/constants/readers are already present; no value, revision, corpus, or runtime behavior needs to change. The two remaining lines share the same protected guard file, so one explicitly named guard unit is smaller and safer than reopening that path twice.

### Exact path fence

**Expected edits for the complete guard contract:**

1. `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`
   - Extend the current revision-literal guard to both `strain-splice.v{n}.json` and `materials.v{n}.json`.
   - Keep `SocketTuningFiles.cs` as the sole C# filename-constant file and keep comment/prose handling; the new rules must not mistake the `MaterialRecipeCatalog` exception prose for a reader.
   - Add the server-reader assertions for `SocketTuningFiles.StrainSplice` and `SocketTuningFiles.Materials` using the same source-text discipline as the sockets rule.
   - Do not weaken the existing sockets guard or add a population-count assertion.

2. `gk-forge/tools/seedsmith/tests/test_combogen.py` (and the existing seedsmith literal-test fixture if the owner assigns it separately)
   - Extend the existing Python path-literal test to cover both `strain-splice.v{n}.json` and `materials.v{n}.json`.
   - Allow only the canonical `STRAIN_SPLICE_PATH` in `combogen/tuning.py` and `MATERIALS_TUNING_PATH` in `recipegen/brief.py`.
   - This is needed if `every_reader` is meant literally across both language readers; a C#-only pass is partial, not full closure.

3. The current strain and materials test-reader files listed above.
   - Replace shipped-file literals with `SocketTuningFiles.StrainSplice` or `SocketTuningFiles.Materials` as appropriate.
   - This is a test-reader conformance conversion, not a behavior change. Do not add a blanket allowlist.

**Read-only contracts (no edit expected):**

- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`
- `gk-core/src/FusionRpg.Server/Program.cs`
- `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs`
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/brief.py`

If the implementing lane deliberately narrows the guard to production C# only, it must record that narrower contract and leave the test-reader conversion as an explicit follow-up; it must not call the C#-only check a complete every-reader closure.

### Focused verification

Run only the path-owned checks after the change:

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter "FullyQualifiedName~TuningRevisionLiteral"
dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter "FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus|FullyQualifiedName~ItemUpgradeCostContract"
dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter "FullyQualifiedName~CraftWearInstanceOp|FullyQualifiedName~MaterialSpend"
dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --filter "FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport|FullyQualifiedName~ItemWorkbench|FullyQualifiedName~ItemUpgradeEndpoint"
$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q
```

The parser/provenance baseline is already green: the current Core focused filter reports **43 passed / 0**, and the two seedsmith files previously reported **112 passed, 11 subtests passed**. No full suite is justified for this report-only triage or for the bounded guard slice.

### Stop condition

Stop when all of the following are true:

- the only C# path-reader literals for strain-splice and materials are `SocketTuningFiles.StrainSplice` and `SocketTuningFiles.Materials`; prose/history literals are explicitly not readers;
- the current test readers use those constants, with no new temporary allowlist;
- each Python reader has one canonical path constant (`STRAIN_SPLICE_PATH` and `MATERIALS_TUNING_PATH`) and the Python scan proves no second path join;
- the guard, parser/provenance, affected Core/Data/Server tests, and Python literal test are green.

Stop **before** any of these:

- publishing `data/tuning/strain-splice.v2.json` or another tuning revision;
- changing `minTierPlan`, ladder values, combo pricing, or provenance;
- running a model call, `combogen-reemit --write`, or editing generated corpus data;
- starting a live game, acquiring a slot, or claiming `SSH4.9` from this slice.

If a new production reader is found outside the listed path fence, stop and route a fence/ownership decision rather than adding an unexplained exception.

### Dependencies and ownership

- **Required dependency:** a pipeline / verification-boundary owner for `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`. The path is pipeline-protected and outside the earlier strain lane fence; this is an ownership blocker, not a live or publish dependency.
- **Python ownership:** the `combogen/tuning.py` and `recipegen/brief.py` mirrors plus their literal test must be in the same fence if the two rows are to claim all readers. If that cannot be assigned, report the slice as partial rather than silently narrowing the acceptance.
- **No H7, tuning publish, owner balance decision, or live-save dependency** is required for this guard slice.
- `SSH8.4` is included only as the named companion guard rule; its materials-reader conversions are still separate from any publish or H7 work.

## Disposition of every open task block

| Block | Current reading | Decision |
|---|---|---|
| `SSH4.9` | Real-game/real-save probe remains open. The prior E2E route proof is not a persisted-save or live-sheet proof. | **Live-only; not selected.** |
| `SSH7.1` | Parser/constant/readers landed; only the literal-guard acceptance and its currently visible test-reader conversions remain. | **Recommended next slice.** |
| `SSH7.7` | Requires `strain-splice.v2.json`, a re-measure, sockets provenance republish, and H7 in one publish unit. | **Not selected; publish-dependent.** |
| `SSH8.4` | `SocketTuningFiles.Materials` and current readers are landed; the materials guard rule is still absent. | **Same guard-file companion; close only after the materials scan is green.** |
| `TVB-F18` | Current `spec-tier-ladder.md` citation audit is clean: 29 citations, 0 HIGH. The cited `emit.py` line was already re-anchored by `0e266806a` / `f2bf05723`. | **Stale row; no implementation.** |
| `SSH4.9-P1` | Incident containment and deploy guard are complete; the row still records the live probe obligation. | **Not a deterministic implementation slice.** |
| `SSH4.9-F3` | Already fixed by `1be4d20b3`; current `FusionRpg.Server.csproj` carries the rarity copy rule and `BootContentCopyRuleTests` is 4/4. | **Stale row; reconcile/close elsewhere.** |
| `SSH4.9-F4` | Still real: `atom.regeneration` is a recorded `FamilyExpandGen` refusal and no generated atom row is emitted. | **Not selected; generator/generated-corpus ownership is unresolved.** Generated data must not be hand-edited. |
| `SSH-F7` | The E2E scenario passes alone but fails in shared/full runs on the XP-ledger read-back; the row explicitly says the writer/collect contract has not been read yet. | **Not selected; investigate the substrate contract before changing an assertion.** |

## Evidence already run for this triage

- `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` — `strain-splice-host`: 9 open / 69 done / 32 unticked / 19 shaded.
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --no-build --filter "FullyQualifiedName~TuningRevisionLiteral"` — **2 passed / 0** (the existing sockets-only guard).
- `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --no-build --filter "FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing"` — **43 passed / 0**.
- `$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` — **112 passed, 11 subtests passed**.
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --no-build --filter "FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport"` — **7 passed / 0**.
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --no-build --filter "FullyQualifiedName~BootContentCopyRuleTests"` — **4 passed / 0**.
- `python scripts/audit-doc-citations.py --strict --scope docs/architecture/strain-splice-host/spec-tier-ladder.md` — **29 resolvable citations, 0 HIGH**.
- `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` — **144 families, 370 rows, 70 recorded refusals; manifest clean**; `atom.regeneration` remains a refusal.
- `git diff --check` — exit 0 after this report was written (the report is still untracked, so this checks the tracked diff; the report itself has no trailing whitespace).

No live probe, model call, generated-data write, or tuning publication was performed.

<<<REPORT
{"status":"done","summary":"Triaged strain-splice-host at the current head and selected the bounded SSH7.1 revision-literal guard slice with SSH8.4 as its same-file companion. Parser and current reader contracts are already landed; the remaining work is deterministic guard/test-reader conformance work with no live save or tuning publish. Nine open task blocks were accounted for, and stale/live/generated-corpus rows were separated from the recommendation.","changed_files":["tasks/reports/resume-25-strain-splice-triage-20260925.md"],"verification":["python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks — strain-splice-host: 9 open, 69 done, 32 unticked, 19 shaded","dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --no-build --filter \"FullyQualifiedName~TuningRevisionLiteral\" — 2 passed / 0","dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --no-build --filter \"FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing\" — 43 passed / 0","$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q — 112 passed, 11 subtests passed","dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --no-build --filter \"FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport\" — 7 passed / 0","dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --no-build --filter \"FullyQualifiedName~BootContentCopyRuleTests\" — 4 passed / 0","python scripts/audit-doc-citations.py --strict --scope docs/architecture/strain-splice-host/spec-tier-ladder.md — 29 citations, 0 HIGH","dotnet run --project gk-forge/tools/FamilyExpandGen -- --check — clean manifest, 144 families, 370 rows, 70 recorded refusals; atom.regeneration remains refused","git diff --check — exit 0 (tracked diff; report is untracked)"],"open_issues":["SSH7.1/SSH8.4 guard path gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs needs pipeline/verification-boundary ownership; the full reader contract also includes the current strain/materials test-reader conversions and Python literal scan listed in the report.","SSH8.4 is included as the named materials guard companion; any remaining materials-reader conversion must stay within the same fence and stop before a publish.","SSH7.7 remains H7 and tuning-publish dependent.","SSH4.9 remains a real-game/real-save live probe only.","SSH4.9-F4 remains a generator/generated-corpus ownership issue; do not hand-edit generated data.","SSH-F7 remains an unresolved shared E2E substrate/root-cause investigation.","SSH4.9-F3 and TVB-F18 are stale/already-fixed rows requiring bookkeeping reconciliation outside this report."]}
REPORT>>>
