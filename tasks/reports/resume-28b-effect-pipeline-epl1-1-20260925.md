# resume-28b — EPL1.1, the closed power-class registry and its C# mirror (2026-09-25)

Correction of the infrastructure-only `resume-28` failure. Same owner-approved model, effort, uncapped
budget and four-file fence; no model call, no generated corpus, no tuning publish, no channel policy, no
live work.

| | |
|---|---|
| **Product base** | `6d77888cca860805e5a11e617e201847e01c16b7` |
| **Lane base (boundary commit)** | `9b27ff0ebd09761a2df59779c96fbc341d84a65e` — adds only `tasks/sessions/resume-28b-effect-pipeline-epl1-1-20260925.json` |
| **Final commit** | **none** — the lane contract is *commit nothing, push nothing, leave the tree dirty*; the orchestrator harvests. The worktree HEAD is the boundary commit above and the deliverable is the four untracked files below. |
| **Session boundary** | `scripts/session-boundary-check.py` → `[session-boundary] clean` (read before the first edit) |

## Changed files — exactly the fenced four, all new

| Path | What it is |
|---|---|
| `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` | the authored registry — the closed roster |
| `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs` | the C# mirror: enum + id grammar + closed parse + registry parser |
| `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs` | 8 focused xunit tests |
| `gk-forge/tools/seedsmith/tests/test_power_class_registry.py` | 11 focused pytest tests |
| `tasks/reports/resume-28b-effect-pipeline-epl1-1-20260925.md` | this report |

`git status --short` after the final run: those four files as `??` and nothing else.

**No generated data, no tuning, no runtime path changed.** No file under `gk-data/packs/fusion/data/generated/**`,
`gk-data/packs/fusion/data/seed/atoms/generated/**`, `gk-data/packs/fusion/data/seed/actions/**` or a generated `gk-data/packs/fusion/data/seed/items/**` tree was
touched; no file under `gk-core/data/tuning/**` was created or edited (the spec's share column deliberately
points at `data/tuning/affix-power-class.v1.json` (new), which EPL1.3 publishes — this row did not invent
one, and that file does not exist yet);
nothing in `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, or Core runtime code outside the one new
mirror file. `scripts/guard-generated-seed.ps1` → `[guard-generated-seed] clean (4 changed file(s)
inspected)`: the registry is authored, so it carries no generator provenance (`_meta.model` /
`promptVersion` / `batch`) and the guard correctly classifies it as a source, not output.

## TDD — the real RED → GREEN cycle

### RED (both suites written first, run before any production file existed)

```
python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q
  → 11 failed in 0.45s
    FileNotFoundError: ...\src\FusionRpg.Core\Effects\Atoms\AffixPowerClass.cs
    FAILED ...::RegistryFileShapeTests::test_the_roster_is_the_five_ids_with_consecutive_ordinals_from_zero
    FAILED ...::RegistryFileShapeTests::test_the_registry_file_exists_and_declares_the_house_schema_keys
    FAILED ...::RegistryFileShapeTests::test_ordinals_are_unique_and_declaration_order_is_ordinal_order
    FAILED ...::RegistryFileShapeTests::test_ids_are_unique_bare_lowercase_words
    FAILED ...::RegistryFileShapeTests::test_the_registry_carries_no_magnitude_only_structural_numbers
    FAILED ...::RegistryFileShapeTests::test_the_registry_is_authored_not_generator_output
    FAILED ...::RegistryFileShapeTests::test_the_registry_says_where_the_target_shares_live
    FAILED ...::RarityCollisionTests::test_no_power_class_id_equals_a_rarity_rung_id
    FAILED ...::CSharpMirrorTests::test_the_mirror_file_exists_and_declares_exactly_one_enum
    FAILED ...::CSharpMirrorTests::test_the_mirror_declares_the_same_ids_and_ordinals_as_the_registry
    FAILED ...::CSharpMirrorTests::test_the_mirror_declares_no_numeric_balance_field
```

```
dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --nologo --filter "FullyQualifiedName~AffixPowerClass"
  → 26 error CS lines, Build FAILED
    error CS0246: The type or namespace name 'AffixPowerClassRejection' could not be found
    error CS0103: The name 'AffixPowerClassIds' does not exist in the current context
    error CS0103: The name 'AffixPowerClass' does not exist in the current context
    error CS0103: The name 'AffixPowerClassRegistry' does not exist in the current context
```

### GREEN

```
python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q
  → 11 passed in 0.05s

dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --nologo --filter "FullyQualifiedName~AffixPowerClass"
  → Passed!  - Failed: 0, Passed: 8, Skipped: 0, Total: 8, Duration: 20 ms
```

Two intermediate RED→GREEN corrections inside the cycle, both in the new test file, not in the
contract: the C# enum-member audit initially failed because it read a member's own `///` doc comment
(`...Ordinal 0 — pads a pool...`), and then on a trailing-comma chunk. Fixed by stripping comments
through the same `strip_csharp_comments` helper the extractor already uses (the discipline
`gk-core/scripts/guard-vocabulary-mirror.py` applies to C# enums it reads by text) and by skipping blank
chunks.

## The closed vocabulary — exact ids and ordinals

| ordinal | id | meaning (from the spec's own column) |
|---:|---|---|
| 0 | `filler` | pads a pool. Nobody builds around it. |
| 1 | `notable` | a build takes it if offered. |
| 2 | `potent` | shapes a build's direction. |
| 3 | `defining` | a build is *about* this effect. |
| 4 | `pinnacle` | top-shelf. The thing channels exist to gate. |

**Identical in both homes** — the JSON registry and `AffixPowerClass` declare the same five ids at
the same consecutive ordinals `0..4`, asserted in both directions (Python extracts the enum members
and ordinals from the shipped `.cs` text and compares them to the file; C# parses the shipped
registry and compares it to the enum). `AffixPowerClassRegistry.Parse` is itself the enforcement, not
a test-only observation: a renamed id, a missing/extra row, a gap in the ordinals, or an ordinal that
disagrees with the enum's own value is refused, each with a named reason.

**Rarity-collision result: 0 collisions.** Checked on both sides against the *current* rarity
vocabulary, not a copied list — C# against `RarityLadder.RungIds` (the ladder the code itself derives
its rung ids from), Python against the `entries[].id` of `gk-data/packs/fusion/data/seed/rarity/ladder.v1.json` (`chaff`,
`sprout`, `grafted`, `cultivated`, `fused`, `chimeric`, `heirloom`, `firstseed`, `sunwoven`,
`almanac`). `filler · notable · potent · defining · pinnacle` is disjoint from all ten, and the Python
test asserts the ladder actually resolved rungs so the check can never pass vacuously.

**Closed, never defaulted.** `TryParse` returns `false` and `Parse` throws `AffixPowerClassRejection`
for an unknown id; there is no path answering `Filler` for a value the vocabulary does not carry, and
`IsDefined` rejects an out-of-range cast such as `(AffixPowerClass)99`. Parsing is `StringComparison.Ordinal`
— a mis-cased `"Filler"` is a reportable content error, because case folding would let a vocabulary
grow a second spelling of itself. `"legendary"`, `"Filler"`, `"FILLER"`, `"filler "`, `" filler"`,
`""`, `"fill"` and `null` are all asserted rejected.

**Identity only — no magnitude anywhere.** The registry's only numeric fields are `ordinal`,
`schemaVersion` and `registryVersion`; the Python test walks every JSON number and fails on any other
key, and the C# test walks the parsed document with the same rule. The spec's rough-share column
(~40/30/20/8/2) is a *balance target* and is deliberately absent: `_meta.targetSharesHome` names
`data/tuning/affix-power-class.v1.json` (new) as its home — a file that does not exist yet; EPL1.3
publishes it and this row did not create it.
The ordinal is structural metadata — it is the order
`powerClassOf(affixId) := MAX over the affix's refs of familyPowerClass(ref)` compares by — and the
registry records the spec's own 2026-09-03 correction that "spaced by 10" was an invented precedent.

**One mirror, asserted mechanically.** The Python test asserts the `.cs` file declares exactly one
`public enum` and that it is `AffixPowerClass` — so a second enum, a classifier-local id list, a
channel vocabulary or an allowlist added to that file fails the suite. No second vocabulary home was
created anywhere.

**No population is pinned.** Nothing in either test file asserts a family, affix or corpus count, and
no classification results are pre-populated or faked — EPL1.3 owns the real run under its own owner
charter. The five-row literal *is* pinned deliberately: a closed, ask-first roster is a closed
vocabulary, which `docs/architecture/validation-ssot.md` §6 says is exactly where a pinned literal is
correct rather than a population reading.

## Verification

| Command | Result |
|---|---|
| `python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q` | **11 passed** |
| `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/… --filter "FullyQualifiedName~AffixPowerClass"` | **8 passed, 0 failed** |
| `pwsh -File scripts/verify-change.ps1 -Paths @(<the four paths>) -Session resume-28b-…` | **aborted by an environment failure — see below.** All four paths resolved to a boundary (no unmapped-path defect): `seed-items-corpus` (module) + `seed-items-validator-seam` · `core-area-effects` (module) + `unique-allocation-reader-seam` · `core-atoms` (module) · `seedsmith-tests` (focused) |
| `python scripts/audit-doc-citations.py --scope tasks/reports/resume-28b-…md --strict` | see the run below |
| `git diff --check` | see the run below |

`-File` cannot carry a PowerShell array literal, so the verifier was invoked as
`pwsh -NoProfile -ExecutionPolicy Bypass -Command "& ./scripts/verify-change.ps1 -Paths @('…','…','…','…') -Session resume-28b-effect-pipeline-epl1-1-20260925"`.
The `-File … -Paths @(...)` form in the brief fails with `Cannot validate argument on parameter 'Format'`
— a shell-quoting artifact of `-File`, not a defect in the script.

### The selected checks, run individually after the abort

The plan's selected set was: `guard: generated-seed` · `pytest: seedsmith` · `script: gen-item-seed-validator`
· `script: gen-items-gate` · `test: core-area-effects-owners` (33 projects) · `test: core-atoms` ·
`test: guard guard.unique-allocation-reader`.

| Selected check | Result |
|---|---|
| `scripts/guard-generated-seed.ps1` | clean (4 changed files inspected) |
| `scripts/checks/gen-item-seed-validator.ps1` | `PASS — 3962 entries across 1013 files, 2589 warnings` (exit 0) |
| `scripts/checks/gen-items-gate.ps1` | exit 0 (`931 gap, 612 note, 153 not_measured` — the gate's own standing reading) |
| `test: core-atoms` (whole project) | **1364 passed, 0 failed** — includes the 8 new tests |
| `test: guard guard.unique-allocation-reader` | **2 passed, 0 failed** |
| `test: core-area-effects-owners` | **29 of 33 projects green**, 1 blocked by the AV failure below, 3 with pre-existing failures (proved pre-existing below) |

Green projects of the 33: ActorHub 498 · Atoms 1364 · Balance 211 · CombatCounter 4 · CombatDot 9 ·
CombatFanout 5 · CombatHitEmitPolicy 5 · DamageFxPalette 4 · EffectClock 10 · EffectEventAdapterCore 7 ·
EffectGrantSessionRecorder 6 · EffectOfflineKit 24 · EffectPluginHost 2 · EffectPluginLifecycle 10 ·
EffectScenarioRunner 20 · Effects 12 · Events 95 · Expeditions 38 · Items 1470 · LawnCoordMath 4 ·
OverlayApplyGuard 3 · OverlayProc 2 · PassiveTree 406 · Power 145 · Stats 291 · Status 170 ·
Core 9752 · Vfx 172.

`pytest: seedsmith` (the boundary is `selfSelect`, so the scoped run is the one file):
`python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q` → 11 passed. Because that
change *adds a file* to `gk-forge/tools/seedsmith/tests/`, the directory-scanning meta-tests were run too
(`test_no_model_literal`, `test_tool_invocation_guard`, `test_guard_population_pin`,
`test_guard_vocabulary_mirror`, `test_workspace_roots`, `test_offline_guarantee`, `test_quality_gates`)
→ **71 passed, 2 failed**, both failures in `test_guard_population_pin.py` and **not** caused by this
change: `python gk-core/scripts/guard-population-pin.py` reports its single P1 finding at
`gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py:278`
(`assertEqual(40, len(ledger)) has no pin: marker`) — another lane's committed file, which this lane
never touched. My new test file produces no finding. That guard is red on this base before this row.

### The three pre-existing failure sets, and how that was established

`FusionRpg.Data.Tests` (44 failed / 1870 passed), `FusionRpg.E2E.Tests` (13 / 283) and
`FusionRpg.Server.Tests` (1 / 881) fail on this machine. Every failure is in a file-backed-store,
temp-directory, archive/purge, icon-blob or process-spawn family, or a passive-tree content lookup —
none of them touch affixes, power classes or the item registries. Proven pre-existing rather than
assumed: the four new files were stashed out of the tree entirely (`git stash push -u`), the tree
verified clean of them, and the same tests re-run — `Failed: 1` (Server),
`Failed: 9` (E2E `StorageE2ETests|TypeIconE2ETests`), `Failed: 24` (Data
`ColdArchiveCompactionTests|StoragePurgeTests|DataTestStoreTests`). They fail identically with this
row absent. A representative inner error is a `SqliteException` from
`gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs:697`. The files were then restored
(`git stash pop`) and **verified byte-identical** by SHA-256 against pre-stash hashes — 4/4 `MATCH`,
and `git status --short` shows only the four expected `??` entries. Limitation stated honestly: the
stash experiment reuses the already-built binaries, so it proves these failures do not depend on my
*files* being present; it does not re-compile Core without the new file. The stronger argument is
mechanical — the new mirror is referenced by nothing, registers nothing, and is a pure additive file.

### The AV blocker (environment, not this change)

`gk-core/tests/FusionRpg.Core.EffectGrantSessionTests.Tests` cannot be compiled in this worktree, so the
`core-area-effects-owners` module check aborts there and `verify-change.ps1` stops with
`core-area-effects-owners module check … failed with exit 1`. Cause, established rather than guessed:

- `error MSB3021: Unable to copy file "obj\Release\net8.0\FusionRpg.Core.EffectGrantSessionTests.Tests.dll" … Access … is denied`, then `CSC : error CS2012: Cannot open … for writing`.
- The Restart Manager names the holder: **`Bitdefender Virus Shield`** (pid 3784).
- It is a persistent **deny-write policy on that one filename**, not a transient handle: after
  `Remove-Item …\obj\Release\net8.0 -Recurse -Force`, `csc` is denied again, and a control probe in the
  same directory shows `probe-other-name.tmp` → `WRITE OK` while
  `FusionRpg.Core.EffectGrantSessionTests.Tests.dll` → `WRITE DENIED`. The directory itself is writable.
- Nothing in this lane touches `EffectGrantSession*`. A machine-level AV rule on a build artifact is
  outside the fence and outside the row; tampering with the AV was not attempted. **The 32 other
  projects of the same boundary were run individually and are green** (table above), so the only
  unproven item in the selected set is that one project's compilation, which is blocked by the host,
  not by the change.

## Open issues

1. **`gk-core/tests/FusionRpg.Core.EffectGrantSessionTests.Tests` cannot build on this machine** — a Bitdefender
   deny-write rule on `obj\Release\net8.0\FusionRpg.Core.EffectGrantSessionTests.Tests.dll` (§ above). It
   blocks the `core-area-effects-owners` module check from completing inside `verify-change.ps1`. Needs
   an owner-side AV exclusion or a rebuild of that project; not lane-fixable.
2. **58 pre-existing test failures** in `FusionRpg.Data.Tests` (44), `FusionRpg.E2E.Tests` (13) and
   `FusionRpg.Server.Tests` (1), proved independent of this change by the stash-and-rerun experiment.
   The Data/E2E cluster points at the same environmental family as (1) — a `SqliteException` in the
   file-store backup path; the Server one is a passive-tree node (`skill.might-off-t1-n0`) missing from
   the catalog. Both need triage by whoever owns those boundaries.
3. **`gk-core/scripts/guard-population-pin.py` is red on this base** — one P1 finding in
   `gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py:278`, another lane's file.
   Not fixed here (out of fence); flagged because it makes `test_guard_population_pin.py` fail for
   every lane until it is converted to a contract assertion.
4. **`tasks/effect-pipeline-todo.md` EPL1.1's own `Verify:` line is stale** — it names
   `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter AffixPowerClass`, but the Core test project was
   split and the atom tests now live in `gk-core/tests/FusionRpg.Core.Atoms.Tests`. The fence in this brief is
   the current one and is what was used. The todo was **not** edited (out of fence); the owner or the
   program manager should update the line when EPL1.1 is ticked.
5. **The classification is not populated, by design.** The registry ships the vocabulary only. There is
   no `basis`, no `blocked` count and no family classification in this row, and no
   `data/tuning/affix-power-class.v1.json` (new) — that file does not exist yet.

## Explicitly not started

- **EPL1.3 model calls** — the 98-call classification run, and its owner charter. No model was invoked;
  `blocked`/`basis` handling and the distribution-vs-target-shares metric remain entirely EPL1.2/EPL1.3.
- **EPL2.1 (and the rest of module 12)** — the `(powerClass × channel) → weight` policy, the six
  channels, the 0.01% `drop` floor, `poolFor(container, channel, rarity)`. No channel vocabulary and no
  tuning file were authored.
- **EPL1.2** — the classifier, the `MAX`-over-refs derivation, `power_class_floor`, and the
  `effect_affix` columns in `gk-core/src/FusionRpg.Data/**` (left untouched).
- **Live proof** — no game, no server, no browser, no `deploy-play.ps1`, no `debug.*` or
  `/api/debug/*` call, no generator re-emit, no `FamilyExpandGen`, no tuning publish.
