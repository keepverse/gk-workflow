# CAI1.12 — `resolvable-here`: the per-place executor allowlist

Session `cai-sink` (the injector/lawn half). The Core/battle half landed in the combat-ai lane; its rows
and the run behind them are preserved at `git show 3cbb0ba2:tasks/evidence-fragments/CAI1.12.md` and are
**not restated here** — one pointer row below. This session closed the two path families that lane was
fenced out of: `gk-core/src/FusionRpg.Core/Effects/**` and `gk-fusion/src/FusionRpg.Injector/**`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Battle half (dispatch table, 11 declared triggers, `Of`/`Veto`, footprint-once, zero-alloc, tuning scan) | combat-ai lane, commit `3cbb0ba2` | **green before this session; behaviour unchanged** — `git show 3cbb0ba2:tasks/evidence-fragments/CAI1.12.md` | — |
| `IDeclaresExecution` at its spec'd home, no second copy left behind | `grep -rn "interface IDeclaresExecution" src/ tests/ --include=*.cs` | **1 hit only** — `gk-core/src/FusionRpg.Core/Effects/EffectModels.cs:139`; removed from `Actions/ResolvableHere.cs`. Three implementers compile: `BattleEffectHost`, `BattleEffectSink`, `InjectorEffectActionSink` | `EffectModels.cs` |
| The injector sink declares its set | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ResolvableHere"` | **13 passed, 0 failed** — 12 pre-existing + the new lawn test | `InjectorEffectActionSink.Executes` (13 arms) |
| `The_lawn_sinks_declared_allowlist_matches_every_EffectActions_constant_its_dispatch_references` | same run | **passes** — 13 declared vs 13 referenced, and the `ExecutedActions` body is asserted to read `Executes` | `tests/.../Actions/ResolvableHereTests.cs` |
| Injector still compiles (not built by CI) | `$env:FUSIONRPG_ML_GAMEDIR="H:\Games\PVZ-Fusion-3.9_MelonLoader"; $env:FUSIONRPG_GAME_PROFILE="pvzrh-3.9"; dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Release` | **0 Error(s)** (25 pre-existing warnings) | — |
| Golden: byte-identical — a moved hash is a stop-and-report blocker | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~Dominance\|Category=BalanceGuard"` | **36 passed, 0 failed** — no hash moved | — |
| `No_file_under_data_tuning_names_an_opcode` | manager ruled **erratum granted** | substituted `No_file_under_data_tuning_authors_a_place_allowlist` **passes**; not re-opened | — |
| Guards | `python gk-core/scripts/guard-battle-responsibility.py` / `guard-actor-hub.ps1` / `guard-secondary-no-unity.ps1` / `guard-doc-citations.ps1 -Strict` | **all exit 0**; doc-citations `0 HIGH` of 24,842 citations / 1,681 docs | — |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ResolvableHere"` | as written | **0 tests matched** — named honestly, not a pass. The spec's Testing strategy puts both anti-drift scans in `gk-core/tests/FusionRpg.Core.Tests/Actions/ResolvableHereTests.cs`; Guard.Tests has no ResolvableHere test to filter to | — |

## Pre-existing red found while running the boundary (not this change — the merge base is dirty)

`verify-change.ps1` selected the whole `FusionRpg.Core.Tests` project for these paths (the
`gk-core/src/FusionRpg.Core/**` glob boundary) and reported **14,878 passed / 4 failed**. The four are
**pre-existing on `features/mega-merge`**, proven not mine: the entire `data/**` tree is byte-identical
to HEAD (`git status --short -- data/` empty), and this change touches no item/atom/socket code.

- `SocketOperationsTests.The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement`
  (`tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs:340`) and
  `No_shipped_gem_declares_an_omni_affinity` (`:329`). Cause read: SSH2.6 (`e79c0fde8`, 2026-09-20)
  deleted `data/seed/items/socket-words/sockwords.json` (425 rows) and updated `KindCatalog.cs`,
  `migrate.py` and `linkage.py` — but not this test, last touched by `12122abf`. Filed in
  `tasks/strain-splice-host-todo.md`.
- `UniqueCorpusTests.Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute`
  (`UniqueCorpusTests.cs:524`, expected 4 / actual 0). Filed in `tasks/item-todo.md`.
- `FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte`
  (`FamilyExpansionTests.cs:193`, committed `gk-data/packs/fusion/data/seed/atoms/generated/**` differs from the generator).
  Filed in `tasks/atom-family-expansion-todo.md`.

None of the four is in `gk-core/scripts/verification-boundaries.v1.json`'s `knownRed` (which lists only five
seedsmith rows), so `features/mega-merge` is red-and-unregistered at four Core.Tests facts.

## Citation note

`IDeclaresExecution` occupies `EffectModels.cs:125-144` — inserted **after** `IEffectActionSink`
(`:120-124`, which therefore stays correct, as do `:10` and `:97`). It was appended at the **end** of
`InjectorEffectActionSink.cs`, so all 38 citations into that file stay correct. The insert shifts by
**+20** everything that used to sit at `>=125`, which catches exactly two citations, both outside this
session's fence and both filed with their corrected target:

- `docs/architecture/action/spec-battle-live-stat-modifiers.md:159` — `EffectModels.cs:126-131`
  (`EffectExecuteContext.Grant`) is now **`:146-151`**. Filed in `tasks/action-todo.md`.
- `docs/architecture/lawn-combat-wire/spec-lawn-combat-calibration.md:81` — `EffectModels.cs:234-238`
  (`GetDouble`, the `fallback`-returning helper) is now **`:254-258`**. Filed in
  `tasks/lawn-combat-wire-todo.md`.

## Lane `combat-ai-2` closure (2026-09-20, tip `0f77d670`)

No code was owed. Both halves are present at this tip, and the row already carried the manager's
erratum and the injector/lawn hand-off; this section is the closure record, not new work.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Both halves present in code | read of `git status --short -- src/` (empty) + `grep -rn "interface IDeclaresExecution" src/ tests/ --include=*.cs` | **1 hit** (`gk-core/src/FusionRpg.Core/Effects/EffectModels.cs:139`); the battle sink's `Executes` table is `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` and the lawn sink's is `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEffectActionSink.cs:1035`, each held to its own dispatch by the source-scan tests | `ResolvableHere.cs:21` (the only construction path) |
| The module's acceptance suite, including the substituted erratum test | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ResolvableHere"` | **13 passed, 0 failed, 0 skipped** — includes `No_file_under_data_tuning_authors_a_place_allowlist`, the erratum substitution for the literal `No_file_under_data_tuning_names_an_opcode` | `tests/.../Actions/ResolvableHereTests.cs` |
| Erratum stands, not re-opened | manager ruling recorded on the todo row | `No_file_under_data_tuning_names_an_opcode` remains substituted; the literal form is unverifiable (`gk-core/data/tuning/status-catalog.v1.json:62,94,126,223,239` names `"ModifyStat"` as a status payload kind) | `tasks/combat-ai-todo.md` CAI1.12 row |

**NOT proved.** The literal acceptance line `No_file_under_data_tuning_names_an_opcode` is false at HEAD
by design and is closed as the granted erratum, not by a green literal. The injector build is not
re-run here (no injector path changed in this lane); `cai-sink`'s 0-error MelonLoader build stands.

**No code owed:** the row's code landed in `c3bb0ba2` (Core half) and the `cai-sink` commits
(injector/lawn half). This commit's deliverable IS the status line above — no source or test file is
touched by it.


## Erratum 4 re-measured 2026-09-27 — `EffectFootprints` still has no consumer

The draft of this fragment recorded that the battle half is golden-neutral because nothing reads the
footprint map yet. A later `cai-sink` session rewrote this file to record the *other* two errata's
resolutions and did not restate this one, and `EffectFootprints` appears in no todo row — so a
negative result survived nowhere, which is the class of record most likely to be lost and least
likely to be re-derived.

Re-measured a week later, on 2026-09-27, the claim still holds. `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`
carries exactly three occurrences of the symbol:

- `281` — `public readonly IReadOnlyDictionary<string, ActionEffectFootprint> EffectFootprints;`
- `729` — `EffectFootprints = BuildEffectFootprints(containerResolver);` in setup
- `840` — `IReadOnlyDictionary<string, ActionEffectFootprint> BuildEffectFootprints(...)`

A declaration, an assignment and a builder. No call site reads the map. The first consumer is
`CAI3.6` (`auto-policy-switch`), which already depends on CAI1.12, so the cross-reference lives on
that row rather than in a row opened here.

For completeness, the same pass re-verified that erratum 1's resolution held: `grep` for
`interface IDeclaresExecution` across `src/` and `tests/` returns **one** declaration, at
`gk-core/src/FusionRpg.Core/Effects/EffectModels.cs:139`, which is the contract's spec'd home.
