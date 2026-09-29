# Task list: creature progression sources

Plan: [creature-progression-plan.md](creature-progression-plan.md). Specs:
[spec-progression-source-contract.md](../docs/architecture/creatures/spec-progression-source-contract.md),
[spec-general-empire-fallback.md](../docs/architecture/creatures/spec-general-empire-fallback.md), and
[spec-dedicated-progression-isolation.md](../docs/architecture/creatures/spec-dedicated-progression-isolation.md).
The dependent lawn consumer is tracked in [creature-lawn-deploy-todo.md](creature-lawn-deploy-todo.md) as Phase 4.

Dependency order: D0 → (D1 || D2) → checkpoint → dependent lawn progression.

## Build status (2026-09-08)

The first implementation slice is landed in the working tree: Core now has the closed source-value
grammar; death captures carry a per-match lifecycle occurrence; Data returns canonical fact ids on
replay, excludes `source=extra` facts from empire species projection, and records dedicated unique
specimen lawn-kill receipts; unique ActorHub and web squads read `uniqueCreature` allocation only; and
expedition specimen rewards no longer mirror into species rows. Atomic provenance ownership validation,
crash-safe terminal settlement, and the full guard sweep remain open below.

## Phase 0 — `progression-source-contract`

### D0.1 — Typed source model and closed grammar · **M** · 4-5 files — **BUILT, closed 2026-09-20**

Implement the three source variants and Data-owned parser/serializer for the versioned
`creature.progression.v1` `source_kind/source_id` grammar. Validate ownership, catalog species, Commander
selection, instance/correlation, and contradictory inputs. Unknown or missing values fail closed with an
observable diagnostic.

- **Acceptance** — closed 2026-09-20 by pointer (`backlog-clean-up` `paperwork-reconcile` P6):
  `gk-core/src/FusionRpg.Core/Creatures/CreatureProgressionSource.cs` (created `061e0651e`, 2026-09-08); cited
  as landed by `species-progression-ideal.md:137` ("closed, versioned"):
  - [x] All three variants round-trip without type inference.
  - [x] A client/Injector-provided instance id cannot impersonate an owned `UniqueSpecimen`.
  - [x] Unknown, missing, cross-player, or contradictory claims earn neither species progression nor allocation.
- **Verification:** Core parser tests and Data provenance round-trip tests; `dotnet test gk-core/tests/FusionRpg.Core.Tests
  --filter ProgressionSource`; `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter ProgressionSource`.
- **Dependencies:** None.
- **Files likely touched:** `gk-core/src/FusionRpg.Core/Creatures/`, `gk-core/src/FusionRpg.Contracts/`,
  `gk-core/src/FusionRpg.Data/Sqlite/`, `gk-core/tests/FusionRpg.Core.Tests/`, `gk-core/tests/FusionRpg.Data.Tests/`.
- **Estimated scope:** Medium.

### D0.2 — Activity propagation and canonical replay identity · **M** · 4 files — **PARTIAL 2026-09-08**

Carry the typed claim through every activity fact used by source-specific progression. Replace ptr-only
death identity with an Injector-emitted per-match lifecycle occurrence id; a duplicate returns the existing
canonical fact id, while pointer reuse creates a new fact. Keep capture origin separate from progression
source in the existing fields.

- **Acceptance:**
  - [ ] Spawn/death/result facts preserve source claim and occurrence id through Data projection.
  - [ ] Duplicate delivery is the same canonical fact; reused ptr is a distinct fact.
  - [ ] Existing settled ledgers remain unchanged and malformed new provenance is visible/fail-closed.
- **Verification:** activity projection/replay tests plus `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter Activity`.
- **Dependencies:** D0.1.
- **Files likely touched:** `gk-core/src/FusionRpg.Core/Activity/PvzActivityKinds.cs`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`, `gk-core/src/FusionRpg.Contracts/EffectDtos.cs`,
  `gk-core/tests/FusionRpg.Data.Tests/`.
- **Estimated scope:** Medium.

### Checkpoint D0 — source contract ready

- [ ] Source grammar, ownership validation, activity propagation, and replay identity tests pass.
- [ ] `guard-dal.ps1` and `guard-secondary-no-unity.ps1` pass.
- [ ] No downstream consumer still guesses a source from `typeId`.

## Phase 1 — `general-empire-fallback`

### D1.1 — Source-gated species XP projector · **M** · 3-4 files — **BUILT, closed 2026-09-20**

Update normal lawn species XP and run-completion selection to consume only parsed `EmpireGeneral` facts.
Preserve the existing per-player/per-species progression row, automatic allocation, run dedupe, and
PowerLadder arithmetic. A `UniqueSpecimen` or `Commander` fact is excluded even when it shares a species.

- **Acceptance** — closed 2026-09-20 by pointer (P6): `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:100-129`
  `IsEmpireGeneralSource`/`WithSpeciesPlacement` gates species-award placement strictly on
  `CreatureProgressionSource.EmpireGeneralKind`, matching the same species id:
  - [x] General lawn spawns earn the expected species XP once per configured rule.
  - [x] Unique/Commander spawns with the same type/species never enter the species completion set.
  - [x] Missing/invalid source earns no species XP and records a diagnostic.
- **Verification:** Data tests for same-species cross-credit, run replay, and per-player isolation;
  `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter Species`.
- **Dependencies:** D0.2.
- **Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`,
  `gk-core/src/FusionRpg.Core/Progression/`, `gk-core/tests/FusionRpg.Data.Tests/`.
- **Estimated scope:** Medium.

### D1.2 — Source-aware general allocation adapter · **M** · 3-5 files — **BUILT, verified and closed 2026-09-20**

Make the general-creature allocation path explicit at composition boundaries. Retain the empire-wide,
per-player/per-species row and automatic primary-stat distribution; reject unique/Commander source input
instead of falling through to it.

- **Acceptance** — verified live 2026-09-20 (`backlog-clean-up` `paperwork-reconcile` P6), reading
  `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs:99-136` directly rather than only
  its consumer: `Resolve` early-returns `commander + uniqueAllocation` the moment
  `_resolveBoundInstanceId` finds a bound instance (line 118-123), skipping the species lookup
  entirely — that is exactly "unique/Commander never fall through to species":
  - [x] `EmpireGeneral` resolves the existing automatic allocation unchanged (the species-lookup path,
    lines 125-136, reached only when unbound).
  - [x] `UniqueSpecimen` and `Commander` cannot resolve this adapter as a fallback (early return above).
  - [x] The same type id resolves differently when the declared source changes (bound vs. unbound
    takes a different branch of the same method).
- **Verification:** Core allocation tests and Server composition tests; `dotnet test gk-core/tests/FusionRpg.Server.Tests
  --filter Progression`.
- **Dependencies:** D0.2.
- **Files likely touched:** `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs`,
  `gk-core/src/FusionRpg.Server/`, `gk-core/tests/FusionRpg.Core.Tests/`, `gk-core/tests/FusionRpg.Server.Tests/`.
- **Estimated scope:** Medium.

## Phase 2 — `dedicated-progression-isolation`

### D2.1 — Unique ActorHub dedicated input · **M** · 3-5 files — **BUILT, closed 2026-09-20**

Route unique composition through the authoritative specimen row and `UniqueCreatureAllocation` when a valid
plan exists. Remove `EffectiveSpeciesAllocation` from `UniqueActorHubCompose` and web battle composition;
empty dedicated input is explicit and diagnosed until a plan exists.

- **Acceptance** — closed 2026-09-20 by pointer (P6): `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:48-84`
  (`aptitudeAllocation: _ => commanderAllocation + uniqueAllocation` — no species term anywhere in the
  file):
  - [x] A unique sharing a species with a general creature has no species allocation contribution.
  - [x] A valid owned unique allocation is consumed through ActorHub only.
  - [x] Missing dedicated state is empty/diagnosed, never a general fallback.
- **Verification:** Server and squad composition tests; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter
  "UniqueActor|WebMatch"`.
- **Dependencies:** D0.2, D1.2.
- **Files likely touched:** `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`,
  `gk-core/src/FusionRpg.Server/WebMatchService.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/UniqueCreatureAllocation.cs`,
  `gk-core/tests/FusionRpg.Server.Tests/`.
- **Estimated scope:** Medium.

### D2.2 — Dedicated rewards and expedition isolation · **M** · 3-4 files — ✅ **DONE-IN-CODE 2026-09-20; the boxes were stale, found by reading the code, not the todo**

Remove species XP from unique/Commander outcomes while retaining specimen XP and existing level-gain action
unlock handling. Keep each reward in its existing transaction and preserve settled history.

- **Acceptance:**
  - [x] Expedition/web-battle unique rewards update only the specimen progression. — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:332-336`: *"Dedicated specimen progression is intentionally isolated from the empire species row. Expedition rewards level the specimen only; species progression is awarded by its own general-spawn activity projector."*
  - [x] Level-gain unlocks still run through the existing transactional helper. — same block, `:330` calls `TryRollActionUnlocks(..., tx)` inside the reward transaction.
  - [x] Replays remain idempotent and never create a species ledger row. — the species row is discovery-only and once-ever: `:347-355` dedupes on `species:{id}`, and the write is `INSERT OR IGNORE INTO rpg_xp_ledger` (`RpgStore.Progression.cs:284`).

**Who found this:** `backlog-clean-up` BCU4.2 (2026-09-20), re-checking the blocked row's premise. The
"PARTIAL 2026-09-08" header above the boxes was three unchecked boxes and no code evidence — the same
stale-premise class this run found in the P11 gate, the `cmdc/lane-c` fence and the naming-grammar row.
- **Verification:** Data expedition/reward tests and progression-ledger assertions; `dotnet test
  gk-core/tests/FusionRpg.Data.Tests --filter "Expedition|UniqueActor|Progression"`.
- **Dependencies:** D0.2, D1.1.
- **Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`, `gk-core/tests/FusionRpg.Data.Tests/`.
- **Estimated scope:** Medium.

### D2.3 — Isolation regression sweep · **M** · 4-5 files — **⬆ UNBLOCKED 2026-09-20 (D2.2 is done-in-code); clauses 2 is already guarded, (1) and (3) remain**

Exercise all three source variants across lawn, web battle, and expedition consumers. Confirm ActorHub is the
only composition gate, no private level formula exists, and old unrelated paths remain byte-identical.

- **Acceptance:**
  - [ ] Every production source consumer handles all three variants explicitly. — **remaining; this is the sweep.**
  - [x] No unique/Commander path awards species XP or reads `EffectiveSpeciesAllocation`. — **already enforced, and green:** `gk-core/tests/FusionRpg.Guard.Tests/ProgressionLayerSelectorGuardTests.cs` ("2a and 2b are mutually exclusive" — every `*SpeciesAllocation*` caller must ask `ProgressionLayerSelector.Select` first) plus `SpeciesAllocationSeamTests.cs` (the one named entry point). Re-run 2026-09-20 for `backlog-clean-up` BCU4.2: 6/6 green.
  - [ ] General-creature behavior remains unchanged under valid `EmpireGeneral` provenance. — **remaining; a test, not a read.**
- **Verification:** Core/Data/Server/Guard suites; `python gk-core/scripts/audit-overflow.py`;
  `python gk-core/scripts/audit-magic-numbers.py --summary`.
- **Dependencies:** D2.1, D2.2.
- **Files likely touched:** `gk-core/tests/FusionRpg.Core.Tests/`, `gk-core/tests/FusionRpg.Data.Tests/`,
  `gk-core/tests/FusionRpg.Server.Tests/`, `gk-core/tests/FusionRpg.Guard.Tests/`.
- **Estimated scope:** Medium.

### Checkpoint D2 — progression sources complete

- [ ] D0, D1, and D2 acceptance criteria pass with no source-inference path remaining.
- [ ] Existing settled history is preserved; new source-gated replays are exact-once.
- [ ] [creature-lawn-deploy-todo.md](creature-lawn-deploy-todo.md) Phase 4 is unblocked.
