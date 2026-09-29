# Resume 21b — effect-pipeline dependency triage

**Scope:** worktree-local read-only triage. No product, test, generated-data, tuning, CI,
todo/plan/spec, ledger, or session-record file was edited. The only intended change is this report.

## Result

**First dependency-ready bounded row: `EPL1.1 — The closed enum + registry + C# mirror`.**

The current program head is modules 1–10 shipped; modules 11–12 are the only remaining program gap
(`docs/architecture/effect-pipeline-map.md:28-34`, `tasks/effect-pipeline-plan.md:8-16`). The next row,
`EPL1.1`, has no prerequisite and introduces no model call
(`tasks/effect-pipeline-todo.md:16-21`). The checked state was verified against the current tree, not
inferred from the unchecked box: the registry, C# mirror, Python classifier directory, and registry
test are all absent.

`EPL1.1` is ready, but its bounded test fence should use the atom test project rather than the todo's
stale `gk-core/tests/FusionRpg.Core.Tests` command:

```text
gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json
gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs
gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs
gk-forge/tools/seedsmith/tests/test_power_class_registry.py
```

The first two are the row's declared production artifacts; the latter two are the smallest exact test
fence that proves the registry and C# mirror agree. `gk-core/scripts/verification-boundaries.v1.json:878-885`
owns atom tests, and the existing affix tests are under `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/`
(`AffixValidatorTests.cs`, `AffixLibraryGeneratorTests.cs`). Adding a test to the todo's named Core
project would split the atom suite without adding coverage.

## Exact producer / consumer path for `EPL1.1`

### Current family-to-affix chain, verified in code

```text
gk-data/packs/fusion/data/seed/items/affix-families/*.json
  -> gk-forge/tools/FamilyExpandGen/Program.cs
  -> gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs
  -> data/seed/atoms/generated/family-expand.*.json
  -> gk-forge/tools/AtomImporter/Program.cs + SeedImportRunner
  -> RpgStore.ImportContent
  -> effect_atom / effect_affix
  -> AffixLibraryGenerator (single-atom affixes derived in memory)
  -> Instantiator.Draw / InstanceProducer -> Resolver.Resolve
```

Evidence:

- `gk-forge/tools/FamilyExpandGen/Program.cs:191-207` reads the authored family files.
- `gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs:339-365` writes real family tags plus
  generator provenance into every emitted atom row.
- `gk-forge/tools/AtomImporter/Program.cs:52-57,69-108` sweeps and imports the committed seed tree.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Import.cs:94-107,157-165` validates authored affixes and derives
  single-atom affixes through `AffixLibraryGenerator`; only authored affixes are persisted.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:469-502` reads stored affixes.
- `gk-core/src/FusionRpg.Core/Effects/Atoms/InstanceProducer.cs:136-142` is the current production resolution
  path into `Resolver.Resolve`; `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:207-229` is the
  secondary draw surface.

### `EPL1.1` artifact path

```text
gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json
  -> registry contract test
  -> gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs (closed mirror)
```

`EPL1.1` intentionally defines the vocabulary only. It has **no runtime consumer yet**: the family
classifier and `MAX` derivation arrive in `EPL1.2`, the real classification run in `EPL1.3`, and the
weighted consumer in module 12. The row must not pre-wire `RpgStore.Containers.cs`, the classifier, or
channel weights.

## Hard edges for the next implementation

1. **Closed structural vocabulary:** exactly `filler`, `notable`, `potent`, `defining`, `pinnacle`, with
   consecutive ordinals `0..4`; adding a sixth is owner-reviewed
   (`docs/architecture/effect-pipeline/spec-affix-power-class.md:63-88,169-180`).
2. **Identity, not magnitude:** the model's classification output may not carry a numeric power class,
   weight, rate, probability, or magnitude (`spec-affix-power-class.md:14-17,177-180`). The registry may
   carry the five structural ordinals; the later balance targets belong in
   `data/tuning/affix-power-class.v1.json` (new) — absent (`spec-affix-power-class.md:86-88`).
3. **No rarity-axis collision:** compare the registry against
   `gk-data/packs/fusion/data/seed/rarity/ladder.v1.json:11-21`; the test must fail on any shared id
   (`spec-affix-power-class.md:80-88,165`).
4. **No population pin:** the family corpus is content-owned and grows. This worktree has 16 authored
   family files / 125 source entries, while the committed atom catalog—the actual classification
   domain—has 105 unique families across 419 atom rows. `validation-ssot.md:132-136` independently
   identifies 125 as today's authored affix-family population. Assert that every family in the live
   atom catalog has a terminal registry row, never `98`, `105`, or a replacement literal
   (`validation-ssot.md:36-55,59-89`).
5. **One mirror contract:** registry ids/ordinals and `AffixPowerClass` must match exactly; unknown ids
   fail rather than defaulting. An unclassified family is a later, visible `notable + unclassified`
   state, not a silent `filler` (`spec-affix-power-class.md:90-99`).
6. **Stop at the vocabulary boundary:** no model call, no generated affix rows, no Data columns, no
   channel policy, and no `Instantiator`/`Resolver` signature change in `EPL1.1`.

## Candidate rows

Paths below are repository-relative. A row marked **not bounded as written** must not be started until
its stale fence is repaired; unchecked boxes were not used as readiness evidence.

| Row | Dependency status | Exact / minimum relative path fence | Focused verification | Stop condition | Owner decision |
|---|---|---|---|---|---|
| **EPL1.1** | **READY NOW**; modules 1 and 3 are shipped; no model run | `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (new); `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs` (new); `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs` (new); `gk-forge/tools/seedsmith/tests/test_power_class_registry.py` (new) | `python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q`; `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --filter "FullyQualifiedName~AffixPowerClass"` | Five closed ids/ordinals match across JSON and C#; rarity collision test passes; no classifier/Data/runtime wiring | **No** |
| **EPL1.2** | Blocked by EPL1.1. Minimum fence is also over the todo's five-file budget | `tools/seedsmith/seedsmith/adapters/effects/power_class/classify.py` (new); `tools/seedsmith/seedsmith/adapters/effects/power_class/derive.py` (new); `tools/seedsmith/seedsmith/adapters/effects/power_class/registry.py` (new); `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs`; `tools/seedsmith/tests/test_power_class_classify.py` (new); `gk-core/tests/FusionRpg.Data.Tests/ContainerStoreTests.cs` | `python -m pytest tools/seedsmith/tests/test_power_class_classify.py -q`; `dotnet test gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj --filter "FullyQualifiedName~ContainerStore"` | `MAX` derivation, visible unclassified default, nullable one-way floor, and numeric-output rejection proven; no model call | No design question; row fence needs repair before assignment |
| **EPL1.3** | Blocked by EPL1.2 **and an owner charter**. Its `98` acceptance is stale | `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (new in EPL1.1, populated here); `data/tuning/affix-power-class.v1.json` (new); `tools/seedsmith/seedsmith/metrics/power_class.py` (new); `tools/seedsmith/tests/test_power_class_metrics.py` (new) | `python -m pytest tools/seedsmith/tests/test_power_class_metrics.py -q`; deterministic rerun/check for unchanged inputs | Every family in the live atom catalog has a terminal row; `basis` present; `blocked` separate; distribution finding visible; no fixed population literal | **Yes — exact runtime(s), model id(s), token budget, concurrency, and stop rule** |
| **EPL2.1** | Blocked by EPL1.1; additionally not ready because current code already owns an `AffixChannels` vocabulary | Intended minimum: `data/tuning/affix-channels.v1.json` (new); `src/FusionRpg.Core/Effects/Atoms/AffixChannel.cs` (new); `src/FusionRpg.Core/Effects/Atoms/AffixChannelPolicy.cs` (new); `src/FusionRpg.Core/Effects/Atoms/AffixChannelTuningHub.cs` (new); `tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixChannelPolicyTests.cs` (new) | `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --filter "FullyQualifiedName~AffixChannel"`; `python gk-core/scripts/audit-magic-numbers.py --targets M1` | Six-channel policy parses from injected data, every class×channel cell exists, drop floor is named; no composer or draw wiring | **Yes — resolve the existing-vs-new channel SSOT collision first** |
| **EPL2.2** | Blocked by EPL2.1 and the real EPL1.3 classifications | `src/FusionRpg.Core/Effects/Atoms/AffixChannelComposer.cs` (new); `tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixChannelComposerTests.cs` (new) | `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --filter "FullyQualifiedName~AffixChannelComposer"` | Eligibility runs first; policy weights follow; zero-weight filtering follows; RNG state is unchanged; no `Instantiator` edit | No after the SSOT ruling |
| **EPL2.3** | Blocked by EPL2.2; **not bounded as written** because the cited production caller is stale | Declared: `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs` plus tests. Actual production seam starts at `gk-core/src/FusionRpg.Core/Effects/Atoms/InstanceProducer.cs:70-83,136-142`; the real channel-bearing acquisition caller is not named by the row | `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --filter "FullyQualifiedName~Instantiator"` plus the repaired call-site test | Flat/no-channel path is byte-identical; one named call site supplies one channel; no RNG advancement in composition; no golden is re-blessed | No product balance question; architecture row repair required first |

## Stale or contradictory rows

1. **`98 families` is stale and must not become a test pin.** The todo/checkpoint and module spec still
   say 98 (`tasks/effect-pipeline-todo.md:32-44`;
   `docs/architecture/effect-pipeline/spec-affix-power-class.md:184-189`). This worktree has 125 authored
   source entries but 105 unique families in the committed atom catalog that actually backs generated
   affixes. The binding validation standard calls 125 a population reading
   (`docs/architecture/validation-ssot.md:132-136`). Repair EPL1.3/CEP1 to reconcile classification
   coverage against the live atom-catalog family set, not either current count.
2. **The “no historical roll shift / no golden moves” claim is stale in map/plan/todo.** The channel
   spec explicitly corrects it: a non-flat policy changes which candidate a given seed selects; frozen
   `effect_instance_atom` rows protect already-owned instances
   (`docs/architecture/effect-pipeline/spec-affix-channel-weights.md:79-95`). The corrected stop
   condition is “no unowned-channel behavior changes and no RNG stream position changes,” not “the same
   seed resolves the same affix.”
3. **EPL2.3 names the wrong live seam.** `spec-affix-channel-weights.md:126-140` cites
   `RpgStore.UniqueActors.cs:756`, but current `Instantiator.Draw` production references are
   `ActionCorpusComposer.cs:149` and `ActionSeeder.cs:47`; the shipped instance path is
   `InstanceProducer -> Resolver.Resolve` (`InstanceProducer.cs:136-142`). The row must name the actual
   channel-bearing item/acquisition call site before implementation.
4. **Module 12 would create parallel channel vocabulary unless corrected.** Current
   `gk-core/src/FusionRpg.Core/Items/Drops/DropTableModel.cs:34-53` owns `AffixChannels` with `drop` and `boss`,
   and `DropTableEntryRow` carries it (`:117-124`). The module-12 spec proposes a separate six-value
   `AffixChannel` enum. One owner must be selected/extended; a second overlapping enum would violate
   the repository's one-SSOT/SOLID rule.
5. **Later row file lists are not bounded as written.** EPL1.2's minimum implementation plus Data proof
   is at least six concrete files, contradicting the todo header's five-file ceiling
   (`tasks/effect-pipeline-todo.md:9-10`). EPL1.3 names a metrics test but omits the production metrics
   module named by the spec (`spec-affix-power-class.md:124-136`).
6. **The target-share publish owner is contradictory.** The plan's H7 says each tuning file lands with
   every reader, and its publish table assigns `affix-power-class.v1.json` (new) — absent — to EPL1.1
   (`tasks/effect-pipeline-plan.md:72-76,100-106`); the todo assigns that file to EPL1.3
   (`tasks/effect-pipeline-todo.md:32-40`). The reader is the metrics implementation, so the file and
   reader need one explicit row before EPL1.3; the file must be published, not hand-edited.
7. **The map's filed eligibility-tag defect is closed, not current.** `effect-pipeline-map.md:253-260`
   says generated rows carry provenance only. Current code stamps real family tags
   (`FamilyExpansion.cs:339-365`) and supplies them in production through
   `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixTags.cs:61-92`. This does not block EPL1.1, but the map row
   should not be used as a current dependency claim.

## Verification boundary for `EPL1.1`

Focused proof:

```powershell
python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q
dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --filter "FullyQualifiedName~AffixPowerClass"
```

The implementation runner must also use the repository's path-owned command with every concrete path
and its real active session id:

```powershell
$changed = @(
  'gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json',
  'gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs',
  'gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs',
  'gk-forge/tools/seedsmith/tests/test_power_class_registry.py'
)
.\scripts\verify-change.ps1 -Paths $changed -Session <implementation-session-id>
```

That registry path selects the seed-items corpus/validator checks
(`gk-core/scripts/verification-boundaries.v1.json:4953-4973`); the Core source selects the effects-owner
boundary (`:5995-6003`); the atom test selects `core-atoms` (`:878-885`). No unfiltered suite is needed
for this row.

## Owner questions that remain open

- **For EPL1.1:** none. Its vocabulary and boundaries are already specified, and it spends no credits.
- **For EPL1.3:** the owner charter remains mandatory: exact runtime(s), exact model id(s), token budget
  per lane, concurrency, and stop rule. It was not supplied here.
- **Before EPL2.1:** name one owner for the six-channel vocabulary relative to the existing
  `Items.Drops.AffixChannels`; do not add a parallel enum.

## Design-gate completion

- [x] Subsystem and current head identified from the capability map, all 12 module specs, plan, and todo.
- [x] Authoritative effect-pipeline documents and binding validation/tunable rules read this session.
- [x] Current producer/consumer path checked in code.
- [x] Claims cite repository-relative `file:line` evidence.
- [x] Population counts are reported as readings, not proposed test constants.
- [x] No implementation, regeneration, product edit, or runtime/live claim was made.
- [ ] A tracked session record for this triage session was not found. The user supplied the boundary
  (`tasks/reports/resume-21b-effect-pipeline-triage-20260925.md` only) but also prohibited editing a
  session record, so an unscoped boundary check that could probe other worktrees was not run.

## Commands run for this triage

```powershell
python -c "import json,pathlib; files=sorted(pathlib.Path('gk-data/packs/fusion/data/seed/items/affix-families').glob('*.json')); entries=[]; [entries.extend(json.loads(p.read_text(encoding='utf-8')).get('entries',[])) for p in files]; print('files',len(files)); print('entries',len(entries)); print('ids',len({e.get('id') for e in entries})); print('tagged',sum(bool(e.get('tags')) for e in entries))"
# result: files 16; entries 125; ids 125; tagged 125

python -c "import json,pathlib; rows=[]; [(lambda d,p: rows.extend((p,e) for e in d.get('entries',[])) if d.get('kind')=='atom' else None)(json.loads(p.read_text(encoding='utf-8')),p) for p in sorted(pathlib.Path('gk-data/packs/fusion/data/seed/atoms').rglob('*.json'))]; print('atom_rows',len(rows)); print('atom_families',len({e.get('family') for _,e in rows if e.get('family')}))"
# result: atom_rows 419; atom_families 105

python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
# result: exit 0; effect-pipeline has 6 open task blocks, 0 done blocks

git diff --check
# result: exit 0
```

## Report-only verification

- `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` — **PASS** (exit 0; task-block
  metric only, explicitly not a readiness proof).
- `python scripts/audit-doc-citations.py --strict --scope tasks/reports/resume-21b-effect-pipeline-triage-20260925.md`
  — **PASS** (0 HIGH; proposed absent files explicitly marked `(new)`).
- `git diff --check` — **PASS** (exit 0).

<<<REPORT {"status":"done","summary":"Triaged the worktree-local effect-pipeline head. EPL1.1 is the first dependency-ready bounded row; documented its exact four-file fence, producer/consumer contract, hard edges, focused and path-owned verification, and the later owner gates/charter. Named stale population, caller, channel-SSOT, publish-owner, and task-fence contradictions separately. No implementation or regeneration performed.","changed_files":["tasks/reports/resume-21b-effect-pipeline-triage-20260925.md"],"verification":[{"command":"python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks","result":"PASS (exit 0); effect-pipeline reported 6 open task blocks and 0 done blocks"},{"command":"python scripts/audit-doc-citations.py --strict --scope tasks/reports/resume-21b-effect-pipeline-triage-20260925.md","result":"PASS (0 HIGH findings)"},{"command":"git diff --check","result":"PASS (exit 0)"}],"open_issues":["EPL1.3 still requires an owner charter with exact runtimes, model ids, token budget, concurrency, and stop rule.","EPL2.1 requires an SSOT ruling against the existing Items.Drops.AffixChannels vocabulary before implementation.","Later row fences/call sites, target-share publish ownership, and the stale 98-family acceptance require repair before those rows start."]} REPORT>>>
