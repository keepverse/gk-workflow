# Resume 08 — PassiveTree binder/resolver seam

**Session:** `resume-08-passive-tree-binder-20260925`
**Worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/opencode-resume-08-passive-tree-binder-20260925`
**Date:** 2026-09-25
**Status:** **PARTIAL** — one local report/read-seam defect is repaired; the committed corpus and the primary resolver route remain outside this fence.

## Scope and result

This lane did not edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, tuning, CI, Server, or any generated vocabulary output. It did not run a model or a corpus regeneration.

The exact binder reproduction is still red. The red output is not one crash and not one code bug. It is a stale/incomplete passive-tree corpus crossing three existing boundaries:

1. the tree-language corpus still names affixes that the current FamilyExpand generator does not emit;
2. generated pool-channel rows are correctly refused at bake time because the shared runtime channel resolver is not exposed to this bake path; and
3. one planned node has never been generated.

The one local code defect proven in this lane was report/read drift: `TreeResolveReport.Build` called a node “contributing” even when the only atom was a kind the resolver drops. The resolver and report now share one kind/op admission predicate. The underlying `stat.modify` execution route is **not** widened here: that would require the owner/design seam already filed as P11.1r, and primary channels cannot be fed through the derived composer as if they were derived channels.

## Exact reproduction

Command run from this worktree:

```powershell
dotnet run --project gk-forge/tools/TreeBinder -- --check
```

Result: **exit 1**. The command emitted 42 `tree-binder:` lines. A deterministic read-back of that same command produced:

```text
trees=42  bound=561  refused=1119
affix-missing=611  pool-reference=507  empty-affix=1  other=0  stale=1
```

The one stale path is:

```text
STALE  gk-data/packs/fusion/data/generated/passive-tree/command.json does not match a fresh regeneration from gk-data/packs/fusion/data/seed/passive-tree
```

A read-only diagnostic regeneration was written only under the ignored `tools/TreeBinder/bin/` area and removed afterward. Its `command.json` differed because the fresh binder now binds `command-def-t8-n0` from `atom.arm-riveting` / `atom.mending`, while the committed file still records the old `atom.ward-brace` refusal. This is stale generated evidence (D), not a reason to hand-edit the generated file.

The diagnostic command used for the counts was:

```powershell
$lines = & dotnet run --project gk-forge/tools/TreeBinder -- --check 2>&1; $exit = $LASTEXITCODE; $treeLines = @($lines | Where-Object { [string]$_ -match '^tree-binder: ' }); $refusalLines = @($lines | Where-Object { [string]$_ -match '^\s+REFUSED\s+' }); $missing = @($refusalLines | Where-Object { [string]$_ -match "does not exist in the shipped seed content" }); $pool = @($refusalLines | Where-Object { [string]$_ -match "channel is a pool reference" }); $empty = @($refusalLines | Where-Object { [string]$_ -match "affixIds must be 1\.\.3, got 0" }); $other = @($refusalLines | Where-Object { [string]$_ -notmatch "does not exist in the shipped seed content|channel is a pool reference|affixIds must be 1\.\.3, got 0" }); $bound = 0; $refused = 0; foreach ($line in $treeLines) { if ([string]$line -match 'bound=(\d+)\s+refused=(\d+)') { $bound += [int]$Matches[1]; $refused += [int]$Matches[2] } }; $stale = @($lines | Where-Object { [string]$_ -match 'STALE' }); Write-Output "exit=$exit trees=$($treeLines.Count) bound=$bound refused=$refused refusalLines=$($refusalLines.Count)"; Write-Output "affix-missing=$($missing.Count) pool-reference=$($pool.Count) empty-affix=$($empty.Count) other=$($other.Count) stale=$($stale.Count)"; $stale | ForEach-Object { [string]$_ }
```

## Refusal/crash classification

| Observation | Count at this head | Class | Responsible source/symbol | Disposition |
|---|---:|---|---|---|
| `affix '…' does not exist in the shipped seed content` | 611 | **D — stale evidence at the tree-language/generated-corpus seam** (with the underlying current generator refusal already represented in the FamilyExpand manifest) | `gk-forge/tools/TreeBinder/Program.cs:149-183` loads generated family files; `gk-core/src/FusionRpg.Core/PassiveTree/Binding/AffixFamilySynthesis.cs:24-35` synthesizes only families with emitted atom rows; current `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/vocab.py:102-125` filters `permitted_for_branch` to `resolvable` options | Do not edit the old tree nodes or generated catalog. The owning follow-up is a real tree-language regeneration after the vocabulary/anchor decisions. The current FamilyExpand check is clean, so this is not a proven binder reader defect. |
| `channel is a pool reference … resolves at roll time` | 507 | **B — persistence/wiring/capability boundary** | `gk-core/src/FusionRpg.Core/PassiveTree/Binding/AffixComposer.cs:122-138` correctly turns a pool object into a named `BindRefusal`; `docs/architecture/effect-atom/spec-channel-pool.md:6-10,262-273` assigns the roll-time resolver to effect-pipeline module 2 | Keep the refusal. Do not choose a pool member at bake time and do not build a second resolver here. Owner: effect-pipeline module 2 / shared resolver seam. |
| Any non-`BindRefusal` crash | 0 | **No current crash** | The current run completed all 42 trees. The old pool-object crash path is now handled by `AffixComposer.ReadChannelOrRefuse`; malformed JSON is also converted to `BindRefusal` at `AffixComposer.cs:67-75`. | No crash repair claimed. |
| `affixIds must be 1..3, got 0` | 1 | **E — incomplete run** | `gk-forge/tools/TreeBinder/PlanReader.cs:167-180,183-224` overlays generated `nodes/<treeId>.json`; `skill.wither-def-t9-n1` is in the plan but absent from the language seed | Owner: the language-generation/resume lane. No hand-authored node was added. |
| `STALE command.json` | 1 file | **D — stale generated evidence** | `gk-forge/tools/TreeBinder/Program.cs:126-138` compares fresh serialized output with the committed file | Do not regenerate the BCU2.12 corpus in this lane. The owning regeneration lane must decide when to refresh it. |
| Binder `verdict=Fail` on every tree | 42 trees | **C consequence, not a threshold to weaken** | `gk-core/src/FusionRpg.Core/PassiveTree/Binding/BinderRunReport.cs:55-58` fails on any non-deliberate refusal; pool refusals are currently non-deliberate | This lane did not turn pool refusals into passes or `DeliberateHole`s. The verdict semantics is an owner/content decision. |
| Binder emits `stat.modify`, while the derived resolver admits only `stat.derived` | Current priced set: `stat.modify` only | **B underlying route gap; C report drift repaired locally** | `TreeBinderRun.BindNode` (`gk-core/src/FusionRpg.Core/PassiveTree/Binding/TreeBinderRun.cs:44-90`) preserves the resolved kind; `TreeAtomSource.BoundAtomsFor` (`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:42-77`) admits the derived kind/op only | The report now uses the same predicate. The primary route remains open owner work; this lane did not route primary channels through `DerivedComposer`. |

The committed-catalog census is a separate read and must not be silently substituted for the fresh binder run:

```text
trees=42  expected=1680  bound=560  refused=1120
boundWithPricedAtoms=250  boundWithoutPricedAtoms=310  pricedAtoms=344
boundWithReadableAtoms=0  unreadableBoundNodes=560  readable=0.0% of bound
stat.modify: 344
DEFECT: no 'stat.derived' atom bound
wither: skill.wither-def-t9-n1 (class E)
```

That census reads the committed `gk-data/packs/fusion/data/generated/passive-tree` files; the current fresh binder has one additional bound node because `command.json` is stale. Neither reading establishes a healthy population.

## Resolver verification and the narrow repair

`dotnet run --project gk-forge/tools/TreeBinder -- --explain skill.might-off-t1-n0` showed the real emitted shape:

```text
atom kind=stat.modify channel='atk' op='flat' ...
stored kMicro 608
```

The current `TreeAtomSource` contract is intentionally the shared derived fan-in: `stat.modify` uses primary channels from `StatChannels.All`, while `BoundDerivedAtom` is consumed by `DerivedComposer` after derived-channel validation (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedComposer.cs:40-47`). `AtomKindRegistry` likewise keeps `stat.modify` and `stat.derived` as separate kinds (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs:496-533`). Lifting the kind filter without a reviewed primary-route design would be a false fix.

The local seam repair is therefore:

- `TreeAtomSource.TryReadOp` is the one kind/op predicate used by the live read loop.
- `TreeAtomSource.HasReadableAtom` exposes the same predicate to the report without widening runtime behavior.
- `TreeResolveReport.Build` now reports a node as contributing only when it has an atom the actual resolver can read. An owned `stat.modify` or mechanism/status-only node is not falsely called a derived contribution.
- `TreeBinderResolverParityTests` binds a real synthetic `stat.modify` row, proves `TreeAtomSource` returns no derived contribution, and proves the report no longer claims that node is contributing.

The repair is report/read parity, not a claim that the primary tree route is playable. P11.1r in `tasks/passive-tree-repair-todo.md` remains the named owner/design follow-up for that route.

## Generator and vocabulary evidence

The accepted FamilyExpand outputs were not changed.

```powershell
dotnet run --project gk-forge/tools/FamilyExpandGen -- --check
```

Result: **exit 0**.

```text
144 families read, 370 row(s) emitted across 11 family file(s), 70 family(ies) refused
--check: clean, 11 generated file(s), 70 recorded refusal(s), and provenance manifest match ...
```

```powershell
dotnet run --project gk-forge/tools/PassiveTreeRosterGen -- --atom-vocab-check
```

Result: **exit 0**.

```text
gk-data/packs/fusion/data/seed/passive-tree/vocabulary.json agrees with the live registries (9 attach point(s), 18 kind(s), 13 trigger(s)).
```

The current generator refusal reasons are content/capability evidence, not a reason to weaken the binder: missing verb bases, structural Replace/Flag exclusions, unregistered/unsupported channel families, and pool gaps. They are already carried by the generator's refusal/provenance manifest.

## Code/test changes

1. `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs`
   - extracted the existing kind/op admission check into `TryReadOp`;
   - added `HasReadableAtom` for the report projection;
   - kept `BoundAtomsFor` behavior unchanged and kept the one-ActorHub/no-new-composer boundary.
2. `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeResolveReport.cs`
   - stopped reporting unreadable binder-emitted kinds as live contributions.
3. `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeBinderResolverParityTests.cs`
   - added the binder-to-resolver-to-report regression seam.
4. `tasks/reports/resume-08-passive-tree-binder-20260925.md`
   - this evidence report.

No generated or tuning file is in the diff. No commit, push, merge, or branch operation was performed.

## Verification

| Command | Result |
|---|---|
| `dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests --filter "FullyQualifiedName~TreeBinderResolverParityTests" --no-restore` (before the fix) | **RED as intended:** 1 failed; the report contained `skill.might-off-t5-n0` although the resolver returned no atom. |
| `dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests --no-restore` | **406 passed, 0 failed, 0 skipped.** |
| `dotnet test gk-forge/tests/FusionRpg.TreeBinder.Tests --no-restore` | **45 passed, 0 failed, 0 skipped.** |
| `dotnet test gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests` | **25 passed, 0 failed, 0 skipped.** |
| `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~TreeAtomSourceParityTests"` | **5 passed, 0 failed, 0 skipped.** |
| `dotnet run --project gk-forge/tools/TreeBinder -- --check` | **Expected red:** 42 trees, 561 bound, 1119 refused, one stale `command.json`; no unhandled crash. |
| `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | **Passed.** |
| `dotnet run --project gk-forge/tools/PassiveTreeRosterGen -- --atom-vocab-check` | **Passed.** |
| `python -m seedsmith trees census` (from `gk-forge/tools/seedsmith`) | **Read succeeded:** committed census reports 344 `stat.modify`, 0 readable atoms, 1 class-E wither node. It is not a health claim. |
| `dotnet run --project gk-forge/tools/TreeBinder -- --explain skill.might-off-t1-n0` | **Passed:** explains a real `stat.modify`/`atk` bind. |
| `.\scripts\guard-single-writer.ps1` | **Passed.** |
| `.\scripts\guard-secondary-no-unity.ps1` | **Passed.** |
| `.\scripts\guard-funnel-delta.ps1` | **Passed.** |
| `.\scripts\guard-dal.ps1` | **Passed.** |
| `.\scripts\guard-actor-hub.ps1` | **Passed.** |
| `python gk-core/scripts/guard-power.py` | **Passed.** |
| `python gk-core/scripts/guard-test-substrate.py` | **Passed.** |
| `python gk-core/scripts/guard-generated-seed.py` | **Passed.** |
| `python gk-core/scripts/audit-overflow.py` | **Passed:** 0 findings, 0 critical. |
| `python gk-core/scripts/audit-magic-numbers.py --summary` | **Passed:** 0 M1/M2/M3/M4. |
| `python scripts/session-boundary-check.py --repo-root . --session resume-08-passive-tree-binder-20260925` | **Clean for this session.** |
| `$changed = @('gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs','gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeResolveReport.cs','gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeBinderResolverParityTests.cs'); .\scripts\verify-change.ps1 -Paths $changed -Session resume-08-passive-tree-binder-20260925 -PlanOnly` | **PlanOnly passed** and selected `core-passivetree`, the `core-area-passivetree-owners` group, and the unique-allocation reader seam. |
| The same path-owned `verify-change.ps1` without `-PlanOnly` | Core.PassiveTree **406/406** and Core.Tests **9752/9752** passed. The selected Data.Tests module stopped at **1 failure / 1791** in `RpgStoreStoragePlanTests.Memory_schema_is_identical_to_the_file_store`: SQLite could not open the backup file (`SaveIdentity.Backup`, SQLite error 14). The failure is outside the three changed paths and was not reclassified as a lane defect; the runner did not reach the remaining selected group/guard, and no broad retry was run. |
| `git diff --check` | **Passed.** |

The path-owned runner's broad selection is recorded rather than hidden. The focused project tests and all relevant guards are green; the Data.Tests failure is outside the allowed fence and is named for manager review.

## Open decisions and owning follow-ups

1. **Primary `stat.modify` tree route (B, unresolved here):** mechanism-wiring/passive-tree owner must decide the reviewed mapping into the existing Hub/primary path. Do not register a fourth composer or reinterpret primary channels as derived channels. The local report seam is fixed, but the route remains unreadable.
2. **Pool-channel resolution (B):** effect-pipeline module 2 must expose the shared bake-time-safe channel-draw seam described by `spec-channel-pool.md`; the passive-tree binder must not implement a second resolver.
3. **Stale tree-language/generated corpus (D):** the owning regeneration lane must re-run the real language/binder pipeline after the vocabulary decisions. This lane did not regenerate BCU2.12 data.
4. **Incomplete `wither` node (E):** the language-generation owner must produce `skill.wither-def-t9-n1` through the real CLI or explicitly carry the incomplete-run exception.
5. **Binder verdict semantics for roll-time pool refusals (C):** owner must decide whether a deferred pool refusal is a deliberate hole or remains a hard content failure. This lane did not weaken `BinderRunReport` or change thresholds.
6. **FamilyExpand refusal families (A/content capability):** the item/FamilyExpand owner must supply the missing authored bases/anchors or retain the named refusals. The accepted manifest and generated outputs remain untouched.

## Manager next step

Review the three code/test paths plus this report. Do not merge on the claim that the corpus is healthy: the current check is red at the stale/content boundary, and the primary tree route is still owner-blocked. After owners resolve the route/pool/content decisions, regenerate through the owning CLIs and rerun the same binder/census/verification boundary.

<<<REPORT {"status":"partial","summary":"Diagnosed the current TreeBinder red run without editing generated data. The dominant 611 missing-affix refusals are stale tree-language/generated evidence, 507 pool refusals are a shared resolver wiring boundary, one wither node is an incomplete run, and there is no current crash. Repaired the proven TreeResolveReport/TreeAtomSource parity defect: the report now shares the resolver's kind/op predicate and no longer calls dropped stat.modify/mechanism-only nodes contributing. The underlying primary stat.modify route remains an owner/design follow-up; TreeBinder remains red on one stale command.json and the named content boundaries.","changed_files":["gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs","gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeResolveReport.cs","gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeBinderResolverParityTests.cs","tasks/reports/resume-08-passive-tree-binder-20260925.md"],"verification":["dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests --no-restore — 406 passed","dotnet test gk-forge/tests/FusionRpg.TreeBinder.Tests --no-restore — 45 passed","dotnet test gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests — 25 passed","dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~TreeAtomSourceParityTests — 5 passed","dotnet run --project gk-forge/tools/FamilyExpandGen -- --check — passed","dotnet run --project gk-forge/tools/PassiveTreeRosterGen -- --atom-vocab-check — passed","dotnet run --project gk-forge/tools/TreeBinder -- --check — expected red, 42 trees, 561 bound, 1119 refused, one stale command.json, no crash","relevant guards, overflow audit, magic-number audit, session boundary, and diff check — passed","path-owned verify-change PlanOnly — passed; full selected runner stopped on Data.Tests SQLite backup failure outside the changed paths"],"open_issues":["TreeBinder remains red because the committed corpus is stale/incomplete and pool rows await effect-pipeline module 2.","stat.modify tree atoms still have no primary resolver route; the local fix is report/read parity only.","BCU2.12 regeneration and the missing wither node are owned by the language/content follow-up.","Binder verdict semantics for deferred pool refusals require an owner decision; no gate was weakened."],"next_steps":["Manager review the dirty code/test/report set.","Owners resolve primary-route and pool-resolver design seams.","Regenerate only through the owning CLIs, then rerun binder/census and path-owned verification."]} REPORT>>>
