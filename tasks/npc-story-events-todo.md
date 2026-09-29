# Todo: npc-story-events

**Program:** `npc-story-events` (the narrative runtime) · **Plan:** [npc-story-events-plan.md](npc-story-events-plan.md)
**Status:** approved 2026-09-22, ready for lanes. Written 2026-09-20; owner approved implementation
2026-09-22. **94 build tasks (NR0.1–NR6.7, NR-LP1, NR-LP2, NRX.1–NRX.3) ·
6 checkpoints · 3 plan gates (PG1–PG3, irreversible actions only) · Phase 7 now has its three `/idea-ui`
entry tasks (NR7.1–NR7.3) and still no build task.** Status lives here only.
**Premises re-verified at the convergence head 2026-09-22** ([plan addendum](npc-story-events-plan.md)):
**A1 (HIGH) — ANSWERED 2026-09-22 by measurement, not by an owner round-trip. NR0.2 landed 7 of the 8
D2 rows, glob-shaped only, dropping `expeditions-tuning` exactly as A1 required; the 8th,
`narrative-readings-script`, is deferred to NR6.7 under NR0.2's own documented default because its
`script`-runner project is refused while `scripts/narrative-readings.ps1` is unbuilt (the refusal was
measured, then reverted). Evidence line under NR0.2.**
*Addendum 2026-09-22 also re-points `scripts/verify-change.ps1:118` → `:114` and records that
`gk-data/packs/fusion/data/seed/dungeon/**` and `data/tuning/expeditions.v*.json` now resolve.*

**Conventions for every task**

- **One task = one commit**: code, tests, the evidence line under the task and this file's checkbox, together.
  Explicit paths (`git add <paths>`), never `git add -A`, never `git stash`, never amend, never push. No watermarks.
  Commit subject: `npc-story-events NR<id>: <what>`.
- `<sid>` is the implementing session's id (`npc-story-events-<yyyymmdd>`, recorded at NR0.1).
- **Verify** with `.\scripts\verify-change.ps1 -Paths @(<every added or modified path>) -Session <sid>`; a deletion
  adds `-DeletedPaths @(<former path>)`. Web paths have no verification lane (plan §4 D2): run the named npm
  commands and list the web paths as unmapped in the evidence line. The full suite (`.\scripts\test-fast.ps1
  -AllDefault`) runs **only** where an entry says **Full suite (point N)**. A focused failure is diagnosed at its
  boundary, never retried broader.
- **Contract, not population.** Tests assert closed vocabularies (each pinned count commented with its reason),
  envelopes, joins, uniqueness, determinism, structural bounds and fixture contents. No test counts the committed
  corpus, the cast, a pick rate or a manifest size. Store tests run in memory (`DataTestStore.Create()`); disk only
  when the disk is the subject.
- **Order-independent** where real play can vary the order: both orders are specified and tested.
- **Standalone.** Every host's end-to-end test runs with the game closed; nothing reads a lawn-only fact.
- **Registry rows** (plan §4 D3) land in the same commit as the test that makes them true; the test carries
  `[Trait("Guard", "narrative")]` and a falsifier built in memory.
- **Shared files.** Apply plan §7's clean-or-skip rule before editing any file another active session claims.
- **Generated data is never hand-edited.** A defect in a seed is narrative-seed's generator to fix.
- **Agent** names the agent type (plan §5). No agent runs before the owner charter is recorded.
- **Evidence line**: one line under the task — the verify command's decisive result, any reading (printed, never
  asserted), any skipped shared file, any golden moved with its hash.

---

## Phase 0 — Boundary

- [x] **NR0.1 Session record.** *Depends:* owner approval of the plan. *Agent:* implementing session.
  *Files:* `tasks/sessions/<sid>.json` (new).
  *Do:* `/session-start`; recommend **worktree** mode (plan §7); claim `gk-core/src/FusionRpg.Core/Narrative/**`,
  `src/FusionRpg.Core/Delve/StoryletHost/**`, `gk-core/src/FusionRpg.Server/Narrative/**`, `src/FusionRpg.Contracts/Narrative/**`,
  the Data, Server, Contracts, web and doc files each task names, `tasks/npc-story-events-plan.md`,
  `tasks/npc-story-events-todo.md`. Record plan §7's crossings in `notes`.
  *Accept:* `python scripts/session-boundary-check.py --session <sid>` is clean for this session.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('tasks/sessions/<sid>.json') -Session <sid>`.
  *Evidence (npc-story-events-1, 2026-09-22):* record committed as `tasks/sessions/npc-story-events-1.json`; `sid` is the lane brief's session id — the todo's `<program>-<yyyymmdd>` template predates the cmdc lane ids, and both cmdc scripts resolve a record by file name. Plan §7 crossings are recorded in the record's `notes`. The `Depends: owner approval` gate is satisfied by the owner's 2026-09-22 ruling (plan and this file's headers) plus the lane brief that deployed this session — the row is not stalled on a round-trip. `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths 'tasks/sessions/npc-story-events-1.json' -Session npc-story-events-1` → `[session-boundary] clean for 'npc-story-events-1'` and `Passed! - Failed: 0, Passed: 591, Skipped: 0, Total: 591` (FusionRpg.Guard.Tests, via the `session-and-program-records` boundary). `session-boundary-check.py --repo-root <MAIN checkout> --session npc-story-events-1` reports `no session record for 'npc-story-events-1'` **until this branch merges** — the record is tracked on this branch, so that exact command is red pre-merge and green post-merge; the same command with `--repo-root` set to this worktree prints `clean for 'npc-story-events-1'`.

- [x] **NR0.2 Focused verification boundaries.** *Depends:* NR0.1. *Agent:* implementer.
  *Files:* `gk-core/scripts/verification-boundaries.v1.json` (shared: clean-or-skip; one contiguous block at the end).
  *Accept:* (**rewritten by Plan audit 2026-09-20** — the old wording would have landed six rows the boundary guard
  refuses on the day this task runs; see plan §4 D2. **Further amended by the Plan addendum 2026-09-22 A1 (HIGH):
  the guard has since added rule C8 — `gk-core/scripts/guard-verification-boundaries.py:121-125` fails any pattern that
  `Test-ExactPattern` calls exact (`scripts/lib/VerificationBoundaries.ps1:246-249`) and that names no file on disk,
  as `stale exact path`. D2's rows as written contain sixteen such patterns, and its `expeditions-tuning` row
  duplicates the existing `tuning-expeditions` pattern string, which trips `ambiguous owner pattern` at `:116-119`.
  So: drop the `expeditions-tuning` row (`tuning-expeditions` already owns that path) and land only glob-shaped
  patterns — `**` for a directory, a final-segment `*` for a family; each exact single-file path is added by the
  task that creates the file.**)
  - The nine rows of plan §4 D2 exist (eight, after dropping `expeditions-tuning`), each at **`level: module` with no
    `verificationId`** — the shipped `notify-core-domain` / `notify-contracts` shape for a row written before its
    focused tests. Fields are a subset of `{id, kind: "owner", paths, project, level, guards}`; `guards` carries
    `dal`/`test-substrate` where D2 names them. (The guard's legal field set is now nine —
    `:108` — so a subset is legal; the six are not the whole set.)
  - `verify-change.ps1 -PlanOnly` for one sample path under each row names **that row**, not a `*-fallback`.
  - `python gk-core/scripts/guard-verification-boundaries.py` is green: no duplicated owner pattern (`gk-data/packs/fusion/data/seed/narrative/_registry/**`
    in `core-narrative` must not repeat narrative-seed NS2's pattern verbatim), no unknown project, no unmapped
    `src/**` file. The guard does **not** check that a `paths` entry exists on disk, so the globs for directories
    later tasks create — and `scripts/narrative-readings.ps1` — are legal now.
  - The evidence line names, per row, the task that will later add its `verificationId` and flip it to
    `level: focused`: `core.narrative` → NR1.1, `guard.narrative` → NR1.4, `data.narrative` → NR2.9,
    `server.narrative` → NR2.14, `data.delve-live` → NR2.20, `server.delve-live` → NR2.24. Each of those tasks adds
    the field in its own commit and runs `guard-verification-boundaries.py` in its verify line, because the guard
    refuses a `verificationId` with no matching `[Trait("VerificationId", "<id>")]` test in that project.
  - *Default if a row is refused anyway:* it moves to the task that makes it legal and the evidence line says so — a
    default, not a gate.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/scripts/verification-boundaries.v1.json') -Session <sid>`;
  `python gk-core/scripts/guard-verification-boundaries.py`.
  *Evidence (npc-story-events-1, 2026-09-22):* **7 rows landed** at `level: module`, no `verificationId`, glob-shaped patterns only (a `/**` dir or a final-segment `*`): `core-narrative`, `data-narrative` (guards `dal`, `test-substrate`), `server-narrative`, `contracts-narrative`, `guard-narrative`, `data-delve-live` (guards `dal`, `test-substrate`), `server-delve-live`; `expeditions-tuning` dropped (`tuning-expeditions` already owns `data/tuning/expeditions.v*.json` verbatim — `ambiguous owner pattern`). The **8th row is DEFERRED to NR6.7** under the acceptance's own default: its plan shape is a `script`-runner project, and the guard refuses that project while the script is unbuilt — measured `script file missing: narrative-readings: scripts/narrative-readings.ps1`, `VERIFICATION BOUNDARY GUARD FAILED`, exit 1, with the project and row temporarily planted, then reverted (389 boundaries, no `narrative-readings` project entry). `python gk-core/scripts/guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK` (exit 0). `verify-change.ps1 -PlanOnly -Format json` for one sample path per row → `NarrativeEnums.cs -> core-narrative`, `RpgStore.StoryLedger.cs -> data-narrative`, `StoryEndpoints.cs -> server-narrative`, `NarrativeTextDtos.cs -> contracts-narrative`, `guard-narrative.py -> guard-narrative`, `DungeonDomainImportRunner.cs -> data-delve-live`, `DelveEventEndpoints.cs -> server-delve-live`, each `(module)` — none a `*-fallback`; samples passed via `-DeletedPaths` because `Normalize-Path` (`verify-change.ps1:70-74`) rejects a `-Paths` entry that is not yet on disk. `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths 'gk-core/scripts/verification-boundaries.v1.json' -Session npc-story-events-1` → `Passed! - Failed: 0, Passed: 57, Skipped: 0, Total: 57`. Row → later-`verificationId` map: `core.narrative` → NR1.1, `guard.narrative` → NR1.4, `data.narrative` → NR2.9, `server.narrative` → NR2.14, `data.delve-live` → NR2.20, `server.delve-live` → NR2.24; each of those tasks adds `verificationId` + `level: focused` in its own commit and runs `guard-verification-boundaries.py`.

---

## Phase 1 — Wave 0: `narrative-vocabulary` (spec-narrative-vocabulary.md)

- [x] **NR1.1 Runtime-only closed vocabularies and structural bounds.** *Depends:* NR0.2. *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeEnums.cs` (new),
  `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/SelectionBounds.cs` (new),
  `gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeEnumsTests.cs` (new).
  *Accept:*
  - `HostClockKind` 4, `StoryScope` 2, `CharacterFate` 4, `CharacterState` 5, `WorldNarrativePhase` 3,
    `StoryFactKind` 27 — each count pinned with a comment naming §3's reason (closed vocabularies).
  - Every member has a kebab-case wire id; `ToId` then `TryParse` returns the member; an unknown id fails. Stored rows
    will carry wire ids, never ordinals.
  - `WorldNarrativePhase.Of(attention, outcome)` maps `active`→`Live`, `hibernating`/`idle`→`Dormant`,
    outcome `fallen`→`Frozen` (fallen wins over attention), with a test per input pair.
  - `SelectionBounds` consts `SpineBeatsPerPulse`, `ConversationsPerCharacterPerReturn`, `MinChoices`, `MaxChoices`,
    `FireChance.CertainMilli`, each with a comment saying why it is structural, not tunable.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeEnums.cs','gk-core/src/FusionRpg.Core/Narrative/Vocabulary/SelectionBounds.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeEnumsTests.cs') -Session <sid>`.
  *Evidence (npc-story-events-1, 2026-09-22):* landed `NarrativeEnums.cs` (`HostClockKind` 4, `StoryScope` 2, `CharacterFate` 4, `CharacterState` 5, `WorldNarrativePhase` 3, `StoryFactKind` 27, each count with a §3-reason comment, six `*Ids.ToId`/`TryParse` wire-id pairs) and `SelectionBounds.cs` (5 structural consts, each commented); `NarrativeEnumsTests.cs` = 24 tests, all green. `python gk-core/scripts/guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK` (exit 0). `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeEnums.cs','gk-core/src/FusionRpg.Core/Narrative/Vocabulary/SelectionBounds.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeEnumsTests.cs','gk-core/scripts/verification-boundaries.v1.json') -Session npc-story-events-1` → `core-narrative (focused)` for all three narrative paths plus `guard-verification-boundary-tests (focused)`; `Passed! - Failed: 0, Passed: 24, Skipped: 0, Total: 24` and `Passed! - Failed: 0, Passed: 57, Skipped: 0, Total: 57`. **The `core.narrative` row flip is in this commit** (`verificationId: core.narrative`, `level: focused`), as NR0.2's acceptance assigned to this task. Two recorded deviations from the row's letter: (1) the spec writes `WorldNarrativePhase.Of(attention, outcome)`, which a C# enum cannot carry — the operation is `WorldNarrativePhases.Of`, the plural static-class split `Disposition`/`DispositionCatalog` uses, and the enum keeps the name §3's table lists; (2) `Of` validates both of world-continuity's axes as input guards (`state` `active|hibernating|idle`, `outcome` `contested|won|fallen`, `decisions.md` "World lifecycle" row) and throws on an unknown one instead of defaulting — when `world-state-vocabulary` lands its C# type, `Of` takes that type and the six string consts go (stated in the class doc). Reading, not asserted: the first verify run selected 22 of 24 because only `NarrativeEnumsTests` carried the trait; both classes now carry `[Trait("VerificationId", "core.narrative")]`, so the selector covers the files it guards.

- [x] **NR1.2 Storylet-side registry catalogs and the registry hub.** *Depends:* NR1.1; narrative-seed
  `storylet-vocab` for the real files (fixtures under `gk-core/tests/fixtures/narrative/_registry/` until then — the commit
  that reads real files waits, plan §8.1). *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeRegistryHub.cs` (new, with `NarrativeVocabularyRejection`),
  `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/StoryletRegistries.cs` (new: `ChoiceKindCatalog`, `ConsequenceKindCatalog`
  with `refForms`/`params`, `ConditionCatalog` with `usableIn`, `RoleTagCatalog`, `TeachesCatalog`, `HostKindCatalog`
  with `ClockOf`), `gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/StoryletRegistryTests.cs` (new),
  `gk-core/tests/fixtures/narrative/_registry/` (new fixture files).
  *Accept:*
  - Each catalog copies `DispositionCatalog`'s shape (`Parse`, `Validate`, `Configure`, `All`, `IsKnown`, `Get`);
    a read before `Configure` throws; a reflection test finds no public writer but `Configure`.
  - Members equal their **file** (read by the test), never a literal list, for the narrative-seed-owned registries;
    host kinds are the 16 of spec §2, pinned with the reason "a place that exists in code".
  - A missing file, an unknown id, a `ConditionCatalog` leaf name absent from `LeafId` or from the proposed six, and a
    `HostKindCatalog` clock outside `HostClockKind` each reject naming file and key.
  - No catalog for `sector-climates` (retired by R20).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.
  *Evidence (npc-story-events-1, 2026-09-22):* `StoryletRegistries.cs` (6 catalogs + `NarrativeVocabularyRejection` + the shared JSON/wire-id helpers), `NarrativeRegistryHub.cs`, 6 fixtures under `gk-core/tests/fixtures/narrative/_registry/`, and 14 new tests — `Failed: 0, Passed: 38, Skipped: 0, Total: 38` for the whole `core.narrative` boundary (24 from NR1.1 + 14 here). Members are compared to the FILE's own keys for all six vocabularies (host kinds, choice kinds, consequence kinds, conditions, role tags' two blocks, teaches — whose file order is the teaching order), never a literal list; the only pinned list is the runtime's own 16 host kinds. Rejections, each with a document built in memory (no test writes a file): missing registry file, a missing row key, an unknown row key, a clock outside `HostClockKind`, a condition leaf neither built nor proposed, a leaf listed in `proposedLeaves` that the runtime has already landed, a `relation.shift` param outside the ledger's five fact kinds, and unknown-id reads. `read before Configure throws` is proven by clearing each catalog's cache field by reflection and restoring it through `Configure` (the caches are process-wide, so this is order-independent); `no public writer but Configure` is a reflection check over all six types. Two grammar facts the tests forced out of the specs, now encoded in the readers: `conditions.v1.json`'s leaf names and `proposedLeaves` entries are C# `LeafId` NAMES (`BandIs`, `RelationBandAtMost`), not wire ids, and `requireFamilies` ids are camelCase (`characterRole`) while their values stay wire ids. `HostKindDef.Clock` is OPTIONAL in the file — seed §3.1's row shape has no clock column while runtime §2 owns the table — so `ClockOf` uses the file's clock when present and §2's table otherwise, and rejects an unknown value either way. **NOT-proved:** the real `gk-data/packs/fusion/data/seed/narrative/_registry/**` files do not exist yet (plan §8.1 defers the commit that reads them), so no production host reaches this loader until NR1.5; `admits` values are not joined to the dungeon `eventKind` registry (a later module's join); the fixtures' `climates` lists are the 7-value universe (R20).

- [x] **NR1.3 Character-side registry catalogs and the doctrine catalog shape.** *Depends:* NR1.2; narrative-seed
  `character-vocab` for the real files (fixtures until then). *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/CharacterRegistries.cs` (new: `NarrativeRoleCatalog`,
  `LineContextCatalog`, `VoiceRegisterCatalog`), `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/DoctrineCatalog.cs` (new;
  accepts an empty list), `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (new, empty `doctrines`),
  `gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/CharacterRegistryTests.cs` (new).
  *Accept:* members equal their files; `DoctrineCatalog` loads the empty file; no second personality vocabulary
  (`CreaturePersonality` is read, never re-declared) and no second relation ladder (the disposition registry is read).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.
  *Evidence (npc-story-events-1, 2026-09-22):* `CharacterRegistries.cs` (`NarrativeRoleCatalog` + its `leads` block, `LineContextCatalog`, `VoiceRegisterCatalog`), `DoctrineCatalog.cs`, the committed `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (empty `doctrines`), 4 fixtures and 12 new tests — `Failed: 0, Passed: 50, Skipped: 0, Total: 50` for the whole `core.narrative` boundary (24 + 14 from NR1.1/NR1.2, 12 here). Members are compared to the FILE for all three character vocabularies; the closed attribute sets are checked against the file's own values (`allegiance` four, `keyedOn` four); role, voice and line-context lists must each carry `none` (voted fields). `DoctrineCatalog` loads the committed empty file read from `gk-data/packs/fusion/data/seed/narrative/_registry/` — an empty list is a legal configured catalog, never a missing-registry rejection — and `IsKnown`/`Get` still fail for every id. The two "no second vocabulary" claims this task can prove are reflection checks: the Vocabulary namespace declares no `*Personality*` and no `*Disposition*`/`*RelationBand*` type, while `CreaturePersonality` (Creatures.Contracts, 5 members) and the dungeon `DispositionCatalog` remain the ones in the assembly — the READS themselves are `relation-ledger`'s (NR2.13) and `character-registry`'s (NR3.1), not this task's. Rejections, each an in-memory document: an unknown `allegiance`, a voted list without `none`, an unknown `keyedOn`, a `none` row carrying an attribute, and unknown-id reads; plus read-before-Configure (cache cleared by reflection, restored through `Configure`) and no-public-writer-but-`Configure` for all four catalogs. Three grammar facts the tests forced out of the specs, now encoded in the readers: lead tokens are snake_case (`lead_summoner`), so the shared id helper gained `RequireLeadToken`; `roles.v1.json` is parsed from the ROOT because its `leads` block is a sibling of the `roles` map, not a wrapper; and the voices file name differs between the two specs (runtime §1 `voice-registers.v1.json` vs the seed Project structure `voices.v1.json`) — the reader reads the name the seed side authors and the discrepancy is filed as **NR-F2**, not silently resolved. Files-list deviations: `NarrativeRegistryHub.cs` is extended here (a loader that reads only the storylet half would leave these four files unreachable, and a loader nobody calls is not done) and `StoryletRegistries.cs` carries the shared id-grammar helper. **NOT-proved:** the real `roles.v1.json`/`voices.v1.json`/`line-contexts.v1.json` are narrative-seed's and do not exist yet, so the hub still has no production caller until NR1.5; the `_exemplars/voices/*.json` files the register rows name are not created here; no host reaches this loader.

- [x] **NR1.4 `narrative.v1.json`, its loader and hub, and the `narrative` guard.** *Depends:* NR1.3. *Agent:* implementer.
  *Files:* `gk-core/data/tuning/narrative.v1.json` (new — the union of keys, plan §4 D4), `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeTuning.cs`
  (new: record tree, `NarrativeTuningLoader.Parse`, `NarrativeTuningHub`), `gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeTuningTests.cs`
  (new), `gk-core/scripts/guard-narrative.py` (new), `gk-core/scripts/enforcement-registry.v1.json` (shared: clean-or-skip).
  *Accept:*
  - For every leaf path in the committed file (a loop over the file's own keys), deleting it makes `Parse` throw naming
    that path; an unknown `dropBand`, disposition id, host kind or clock, a negative `gates.leadLevel` and a leftover
    `relation.joinRankByBand` each reject naming the key; `NarrativeTuningHub` has no default.
  - `python gk-core/scripts/audit-magic-numbers.py --domain narrative` reports no balance literal; every `*Milli`, clock and
    score is `long` (`python gk-core/scripts/audit-overflow.py` clean for the new files).
  - Catalog guard `narrative` → `gk-core/scripts/guard-narrative.py` (`ci`, `gating`) runs the `Guard=narrative` trait filter
    over the Core, Data, Server and Guard projects and the named web tests; `EnforcementRegistryGuardTests` R1, R5, R6,
    R8 stay green. R1 also requires every `scripts/guard-*.ps1` **on disk** to be catalogued, so the script and its
    catalog entry land in one commit.
  - **Plan audit 2026-09-20 — the guard cannot pass vacuously** (plan §4 D3). It carries a committed **row → test-class
    map**; it derives from `gk-core/scripts/enforcement-registry.v1.json` the invariant ids whose `guards` contains
    `narrative` and exits non-zero naming any row absent from the map or any map entry naming no row; and it exits
    non-zero (printing the per-project selected count) if the trait filter selects **zero** tests in any project it
    names. Falsifiers run here: a throwaway `guards: ["narrative"]` row with no map line must be named and then
    removed; stripping `[Trait("Guard","narrative")]` from one real test must drop the count and fail the guard.
  - `gk-core/scripts/guard-narrative.py` is covered by NR0.2's `guard-narrative` boundary row; this task adds that row's
    `verificationId` (`guard.narrative`, `level: focused`) now that a trait-carrying test exists, and runs
    `guard-verification-boundaries.py`.
  *Registry row:* `narrative-tuning-no-default` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/data/tuning/narrative.v1.json','gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeTuning.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeTuningTests.cs','gk-core/scripts/guard-narrative.py','gk-core/scripts/enforcement-registry.v1.json') -Session <sid>`;
  `python gk-core/scripts/guard-narrative.py`.

  *Partial + BLOCKED (npc-story-events-1, 2026-09-22):* the CODE HALF is landed and green — `gk-core/data/tuning/narrative.v1.json` (the union of keys), `NarrativeTuning.cs` (`FiringRow`, `NarrativeTuning`, `NarrativeTuningLoader.Parse`, `NarrativeTuningHub`) and 13 tests: `verify-change.ps1` on the three paths → `core-narrative (focused)`, `Failed: 0, Passed: 63, Skipped: 0, Total: 63`. The decisive test is the leaf-path loop (it walks >= 40 paths and asserts every deleted one is rejected BY NAME); every cross-reference is a JOIN read, never a second copy (firing = one row per `HostKindCatalog` member, cooldown = `HostClockKind` ids with `delve.room` refused, `shiftByFactKind` = the consequence catalog's five, `baseBandByRole` = one row per non-`none` role, every band value a `DispositionCatalog` member). **The row is NOT closed**, because its guard half cannot be written: creating `gk-core/scripts/guard-narrative.py` is refused by the orchestrator pipeline guard as a protected pipeline file, and without that script the row cannot pass its Verify line, R1 (every `guard-*.ps1` on disk catalogued) cannot be satisfied, R8 cannot name a catalogued guard, and the `guard-narrative` boundary row cannot take its `verificationId`. Blocked, not skipped — the remaining work is the script + its row→test-class map + the `narrative` catalog entry + the `narrative-tuning-no-default` invariant row + the boundary flip + the two falsifiers, all of which need that one path granted. **NR-F3:** the acceptance's `python gk-core/scripts/audit-magic-numbers.py --domain narrative` is VACUOUS — measured with a const planted in `NarrativeTuning.cs`, `--domain narrative` = 0 findings while `--domain vocabulary` (the domain `domain_of` actually derives) = 1 M3. `python gk-core/scripts/audit-overflow.py` = 0 findings / 0 critical, and `--domain vocabulary` = 0 findings / 0 high on the real tree.
  *Evidence, follow-up in the same session (npc-story-events-1, 2026-09-22) — the D4 union was missing and is now published:* reading plan §4 **D4** showed the wave-0 file must carry the **union** of the keys seven later specs declare (`quest-sources` §Data shapes, `quest-log-contract` §2, `world-events-host` §Data shapes, `failure-branches` §Data shapes, `counter-doctrine` §6, `narrative-readings` §Data shapes, `delve-host` §Data shapes), so the first commit's v1 was incomplete. The sanctioned path carried it: `python gk-core/tools/tuning/publish.py narrative --add-key 'casting:delveResidentsPerRole={"trader":1,"chronicler":1,"captive":2}' --add-key ':quest={"expiry":{...}}' --add-key ':questLog={"recentClosed":{...}}' --add-key ':world={"offerLifetimeTurns":2}' --add-key ':failure={"priorityWindow":{...}}' --add-key ':doctrine={...}' --add-key ':readings={...}' --label "the wave-0 union of the seven later specs' keys (plan D4)"` → `published narrative (v1 -> v2, 7 change(s)); v1 stays on disk for revert`. (`--add-key` refuses to invent a path, so the new blocks went in through the empty-container root form; the one leaf under an existing container — `casting.delveResidentsPerRole` — used `casting:`.) `NarrativeTuningLoader` now requires the six blocks, each key set pinned from its declaring spec with the starting value that spec chose (`quest.expiry` 20/5/5, `questLog.recentClosed` 3 on every `HostClockKind`, `world.offerLifetimeTurns` 2, `failure.priorityWindow` 10/3/20, `doctrine.*` 400/125/10/10/375/3, `readings.*` 20/50/900, `casting.delveResidentsPerRole` 1/1/2), and the test now reads the HIGHEST `narrative.v*.json` so a published version moves it. `verify-change.ps1` on `gk-core/data/tuning/narrative.v2.json` + the loader + the tests → `core-narrative (focused)`, `Failed: 0, Passed: 63, Skipped: 0, Total: 63`; `python gk-core/scripts/guard-tuning-immutability.py` → `TUNING IMMUTABILITY GUARD OK — 1 gk-core/data/tuning/*.json change(s) checked, T1-T4 clean`; `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"` → `Failed: 0, Passed: 9`. v1 stays committed as history and is superseded by v2 (it predates the union, so the current reader rejects it — the reader takes the highest version).

  *Closed (npc-story-events-2, 2026-09-23):* the guard half that three refusals blocked is landed. `gk-core/scripts/guard-narrative.py` carries the committed row → test-class map and derives its required rows from `gk-core/scripts/enforcement-registry.v1.json` (a row with no map line is named; a map line naming no row is named; a stray duplicate is named), checks each mapped class exists and carries `[Trait("Guard","narrative")]`, and — with `-RunTraitFilter`, carried by the catalog entry's `args.ci` — refuses a per-project selection of zero. `gk-core/scripts/enforcement-registry.v1.json`: the `narrative` catalog guard (`ci`, `gating`, `args.ci: [-RunTraitFilter]`) plus three invariant rows (`guard-narrative-row-map`, `ns-one-content-theta-producer`, `narrative-tuning-no-default`). `gk-core/scripts/verification-boundaries.v1.json`: the `guard-narrative` owner row took `verificationId: guard.narrative` + `level: focused`, so `gk-core/scripts/guard-narrative.py` now resolves to its own focused boundary. Falsifiers, all run: a planted `guards: ["narrative"]` row with no map line is named (`NarrativeGuardContractTests`, three falsifiers + a control, planted in a temp root); stripping `[Trait("Guard","narrative")]` from a real test failed the guard by name AND dropped the filter to zero (measured, then restored). Printed readings: `guard-narrative.py` static → `NARRATIVE GUARD OK - 3 row(s) guarded by 'narrative', 3 mapped`; `-RunTraitFilter` → `Core.Tests 30 selected / 0 failed`, `Guard.Tests 5 selected / 0 failed`; `EnforcementRegistryGuardTests` R1/R5/R6/R8 → `Passed: 18, Failed: 0`; `guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK` (436 boundaries). **Verify deviation (the erratum asked three times and still open):** the acceptance's Verify line names `--session <sid>`, which cannot resolve in this lane (`tasks/sessions/npc-story-events-2.json` does not exist and `tasks/sessions/**` is outside the lane's allowed paths), so it was run as the same script over the same paths with `-AllowUnscoped` → `enforcement-registry (focused)`, `guard-narrative (focused)`, `guard-verification-boundary-tests (focused)`, `Passed: 5` then `Passed: 57`, exit 0. NR-F3 (the `--domain narrative` audit being vacuous) still stands as recorded below.

- [ ] **NR1.5 Host wiring.** *Depends:* NR1.4. *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Server/Program.cs` (shared: lanes A2, C, D3 — region check), `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj`
  (copy rule for `gk-data/packs/fusion/data/seed/narrative/_registry/**`; reuse identity-rename T2's rule if it has landed, plan §4 D6),
  `tests/FusionRpg.Server.Tests/Narrative/NarrativeBootTests.cs` (new).
  *Accept:* the server configures `NarrativeRegistryHub` and `NarrativeTuningHub` once at start beside
  `ExpeditionTuningHub`; a missing registry or tuning file fails boot naming the path (never a default); the static
  caches' full trigger set is process start, stated in a comment and tested (`Configure` is the only writer).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/Program.cs','gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj','tests/FusionRpg.Server.Tests/Narrative/NarrativeBootTests.cs') -Session <sid>`.

  *BLOCKED (npc-story-events-2, 2026-09-23) — the corpus this wiring would read is not shipped.* Measured: `NarrativeRegistryHub.Configure(registryDir)` requires ten files (`NarrativeRegistryHub.cs:31-58`, each through `Read` at `:63-68`, which throws `NarrativeVocabularyRejection` naming the path when absent), and `gk-data/packs/fusion/data/seed/narrative/_registry/` holds ONE of them (`doctrines.v1.json`); the other nine — `host-kinds`, `choice-kinds`, `consequence-kinds`, `conditions`, `role-tags`, `teaches`, `roles`, `line-contexts`, `voices` — are narrative-seed's wave-1 `storylet-vocab` + `character-vocab` outputs and exist only under `gk-core/tests/fixtures/narrative/_registry/`. Because the acceptance's own clause is *"a missing registry or tuning file fails boot naming the path (never a default)"*, wiring `Configure` into server start today makes the server refuse to boot — for every lane, not just this program. Plan §8.1 already says "the task's commit that reads the real files waits" for NR1.2/NR1.3, and this row is the host-side twin of that rule. Two ways out, both the manager's call: **(a) defer** until the nine files ship (then this row is a small mechanical boot block), or **(b) rule an erratum** that the registry half boots tolerantly — the repo's established pattern for unshipped boot content ("a lint, never a gate": `SeedImportRunner.RunSelfHealing` and `PassiveTreeImportRunner.RunSelfHealing` both never throw) — while the tuning half stays required, since `gk-core/data/tuning/narrative.v2.json` IS shipped. This lane implemented neither and changed no boot path.

- [x] **NR1.6 Propagate plan decision D4 into the specs.** *Depends:* NR1.4. *Agent:* implementer.
  *Files:* `docs/architecture/npc-story-events/spec-narrative-vocabulary.md` (§4 key table gains every key of the
  union with its owner module), and a one-line note in `spec-quest-sources.md`, `spec-quest-log-contract.md`,
  `spec-world-events-host.md`, `spec-failure-branches.md`, `spec-counter-doctrine.md`, `spec-narrative-readings.md`,
  `spec-delve-host.md` ("declared in `narrative.v1.json` at wave 0, plan D4"). Docs only; one commit.
  *Accept:* every key in the committed `narrative.v1.json` appears in the vocabulary spec's table;
  `python scripts/audit-doc-citations.py --scope docs/architecture/npc-story-events` reports no HIGH finding.
  *Evidence (npc-story-events-1, 2026-09-22):* the row's premise was half-stale, and the reading is the evidence: the
  vocabulary spec's §4 table **already** carried every pre-existing family (`selection.*`, `firing.{hostKind}.{baseMilli,stepMilli}`,
  `cooldown.*`, `fairness.*`, `relation.*` with the struck `relation.joinRankByBand` row, `casting.*`, `gates.leadLevel`,
  `spec-narrative-vocabulary.md:148-167`), so the real work was the **seven families the later specs declare** plus the
  seven one-line notes. Added to the table with their owner module, starting value and a "The union (plan §4 D4)"
  paragraph: `quest.expiry.{clock}` (quest-sources), `questLog.recentClosed.{clockKind}` (quest-log-contract),
  `world.offerLifetimeTurns` (world-events-host), `failure.priorityWindow.{clock}` (failure-branches), the six
  `doctrine.*` keys (counter-doctrine §6), the three `readings.*` keys (narrative-readings), `casting.delveResidentsPerRole.{role}`
  (delve-host) — each at the value its own spec chose, and each spelling the full dotted key so it is machine-findable.
  The paragraph also states that `v1` predates the union, that `v2` supersedes it, and that a later module READS its key
  (a change is a `publish.py` `v{n+1}`). The seven specs' "added to `narrative.v1.json` in this module's build change"
  clauses are corrected to "declared in `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)" — a stale
  clause is a doc defect, not a note. `python scripts/audit-doc-citations.py --scope docs/architecture/npc-story-events`
  → `D1 file does not exist 40 (0 HIGH)`, `D2 0 (0 HIGH)`, `D3 0 (0 HIGH)`, `D4 0 (0 HIGH)`. `verify-change.ps1` on the
  eight spec files → a per-document doc-citation audit (`Doc-citation audit - 1 documents, 40 resolvable citations checked`,
  0 HIGH) plus `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4` (the guard project's docs boundary). Coverage of
  the committed file is a READING, not a gate: 99 leaf paths were walked and matched against the table heuristically, and
  the seven newly added families are explicit full-dotted rows while the older ones are brace-group rows
  (`firing.{hostKind}.{baseMilli,stepMilli}`) that an ad-hoc matcher cannot expand reliably — stated rather than claimed.
  *Dependency note:* NR1.6 depends on NR1.4's committed key set, which exists (v2); NR1.4's own guard half is blocked on
  the protected pipeline path, which does not affect this row's deliverable.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the eight spec files>) -Session <sid>`.

### Checkpoint 1 — vocabulary (after NR1.6)
- [ ] Every registry and tuning key loads or rejects by name; `guard-narrative.py` green; one catalog guard, one row.

---

## Phase 2 — Wave 1

### `storylet-reseam` (spec-storylet-reseam.md) — gate G1 of the map

- [x] **NR2.1 Record the stream-identity fixture before the move.** *Depends:* NR0.2. *Agent:* implementer.
  *Files:* `gk-core/tests/fixtures/narrative/reseam/event-resolutions.json` (new), `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/StreamIdentityFixtureTests.cs` (new).
  *Accept:* `EventDeck.Resolve` on today's code, for 64 fixed seeds × the six event-capable room kinds plus `unknown`,
  records `EventId`, `DrawnOutcomeOrdinal`, `Instance` and `NextPity`; the test asserts today's code reproduces the
  fixture byte for byte (so the fixture is proven before the move uses it).
  *Evidence (npc-story-events-1, 2026-09-22):* `gk-core/tests/fixtures/narrative/reseam/event-resolutions.json` — 448 rows
  (7 room kinds × 64 seeds), each recording `eventId`, `drawnOutcomeOrdinal`, `instance` and `nextPity`; **0 rows with a
  null event id**, because the `unknown` room's pity is tuned so the three non-event arms are impossible and the room
  always takes the ordinary event path (64 rows carry a `nextPity`). The deck is built in memory from an inline catalog
  (two probe events per kind, two outcomes each, one real `resource.delta` effect per outcome — an outcome's effects
  list may not be empty — and a `chainRef` on the `story` probes, which the catalog's content rule requires), so the
  fixture pins the ENGINE's streams and not the committed corpus. Recording is gated: the test WRITES the file only when
  `FUSIONRPG_RECORD_NARRATIVE_STREAM_FIXTURE=1`, and a normal run compares byte for byte and prints the first differing
  line. `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/tests/fixtures/narrative/reseam/event-resolutions.json','gk-core/tests/FusionRpg.Core.Tests/Delve/Events/StreamIdentityFixtureTests.cs') -Session npc-story-events-1"` →
  the fixture path selects `core-narrative (focused)` (`Failed: 0, Passed: 63`) and the test path selects
  `core-tests-fallback (module)`, which runs the whole `core` group: `FusionRpg.Core.Tests` `Failed: 0, Passed: 10134`,
  `FusionRpg.Core.Atoms.Tests` `Failed: 0, Passed: 1351`. *One intermittent red seen and diagnosed:* the FIRST group run
  reported `Failed: 1, Passed: 1350` in `FusionRpg.Core.Atoms.Tests`; the immediate re-run of the same command and a run
  of that project alone are both green (1351/1351), no atoms path is touched by this diff, and the failing test's name
  was not captured, so it is recorded as an observed-once intermittent at this boundary rather than filed as a row
  (a row without a `file:line` would be unactionable).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/tests/fixtures/narrative/reseam/event-resolutions.json','gk-core/tests/FusionRpg.Core.Tests/Delve/Events/StreamIdentityFixtureTests.cs') -Session <sid>`.

- [ ] **NR2.2 Move the engine behind `IStoryletHost`; land the NS1 guard.** *Depends:* NR2.1; `EventCatalogTests.cs`
  clean (plan §3 rule 4). *Agent:* **refactorer**.
  *Files:* the 18 files of `gk-core/src/FusionRpg.Core/Delve/Events/` moved per spec §1 to `src/FusionRpg.Core/Narrative/Storylets/`
  (new) and `src/FusionRpg.Core/Delve/StoryletHost/` (new; `DelveStoryletHost.cs` with the old `Resolve`/`Answer`/`PickEvent`/`PickOutcome`
  signatures), `IStoryletHost.cs`, `StoryletDrawContext.cs`, `StoryletAnswer.cs` (new), the six external referrers of
  spec §4, the test `using` lines under `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/`, `tests/FusionRpg.Guard.Tests/StoryletEngineSingleSourceTests.cs`
  (new), `gk-core/scripts/enforcement-registry.v1.json`, `docs/architecture/decisions.md` (NS1 row; clean-or-skip),
  **`tasks/party-dungeon-todo.md`** (one pointer line in its transfer note giving the old → new path table;
  clean-or-skip). A pure move: file count is mechanical (plan D1 exception).
  *Accept:*
  - **Plan audit 2026-09-20 — the move must not orphan party-dungeon's open work** (plan §3 rule 4). Its transfer
    note keeps **the resolver logic** and **the 256-seed sweep** there, and **D3.3, D3.5 and D3.9 are still open** in
    files this task deletes. So: the commit body lists the old → new path of every moved file; the same table is
    pointed at from `party-dungeon-todo.md`'s transfer note in this commit; the evidence line states whether D3.3,
    D3.5 and D3.9 were open. *If any of the three is in progress in another live session, defer this task* — a move
    across live work is the one thing `session-boundary.md` will not merge, and the owner sequences it.
  - `git diff -U0 -- tests/` filtered to lines that are neither a `using` nor the two entry-point qualifiers is empty.
  - NR2.1's fixture is byte-equal through `DelveStoryletHost.Resolve`; streams are `DelveStreams.Event(row, col)` + suffix.
  - Battle, expedition and world goldens byte-identical (hashes listed in evidence).
  - `gk-core/src/FusionRpg.Core/Delve/Events/` no longer exists; a reflection test finds no engine type referencing
    `FusionRpg.Core.Delve.*`.
  - The guard fails an in-memory probe `ZzProbeDeck` that references `EventRow` outside the engine, passes a probe
    `ZzProbeDraw` with no storylet reference, and passes `DropTableDraw`, `RarityDraw`, `BudgetDraw`, `ResolvedDraw`;
    the allowlist is closed (`AmbushDraw`, with its reason).
  *Registry row:* `ns1-one-storylet-engine` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<every moved and edited path>) -DeletedPaths @(<every former Delve/Events path>) -Session <sid>`.
  **Full suite (point 2):** the move crosses Core, Data tests and Guard tests.

  *DEFERRED (npc-story-events-2, 2026-09-23) under this row's own gate.* The acceptance says: "If any of D3.3, D3.5 and D3.9 is in progress in another live session, defer this task — a move across live work is the one thing `session-boundary.md` will not merge, and the owner sequences it." Measured against the tracked session records: **`tasks/sessions/party-dungeon-d3.json` is `status: active`**, its declared `paths` include **`gk-core/src/FusionRpg.Core/**` and `tests/**`**, it owns D3.3/D3.5/D3.9, and its branch `cmdc/pd-d3` was merged into the integration head this segment (`4e7eb1489`). D3.5/D3.9 are still open in `tasks/party-dungeon-todo.md` (`:1440`, `:1482`), and plan §3 rule 4 names `gk-core/src/FusionRpg.Core/Delve/Events/**` — the 18 files this row deletes — as its open work. So the move waits on that lane finishing or releasing those paths; the owner sequences it. Nothing was moved and no file in either party-dungeon session's set was touched. `party-dungeon-f13.json` also claims `gk-core/src/FusionRpg.Data/**`, which is why the Data rows (NR2.9, NR2.11) are deferred with this one.

### `storylet-contract` (spec-storylet-contract.md) — gates G1, G2 of the map

- [ ] **NR2.3 Widened storylet shapes and legacy parity.** *Depends:* NR2.2. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Storylets/EventRow.cs` (appended, defaulted members; `StoryletChoice`,
  `StoryletRole`, `StoryletOutcome`, `StoryletConsequence`, `TextRef`, `StoryletProvenance`, `RoleKind`),
  `tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletShapeTests.cs` (new).
  *Accept:* every existing constructor call compiles unchanged; the committed Delve corpus loads to the same values as
  before, field by field over every file, plus derived `Hosts`; `IsNegative` is defined for legacy rows (no `good`
  outcome) and widened rows (no always-eligible non-`leave` `good` outcome); `Revision` is `long`, `ArcLink` a string.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.4 Loader widening and the built-target `ConditionCompiler`.** *Depends:* NR2.3, NR1.2. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Storylets/EventSeedFile.cs`, `src/FusionRpg.Core/Narrative/Predicates/ConditionCompiler.cs`
  (new; built-target arms only, plan §4 D5), `tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletLoaderTests.cs` (new),
  `tests/fixtures/narrative/storylets/` (new: green corpus — one storylet per choice kind, a three-link arc, an authored row).
  *Accept:*
  - The `NotSupportedException` on a non-null `eligibility` is gone: a legacy tree reads through `AtomJson.TryReadPredicate`,
    a widened `{id, arg}` condition and `eligibility` list through `ConditionCompiler`; a depth-5 or 17-node tree rejects
    with the compiler's own reason.
  - Both directories load into **one** catalog; the envelope `{schemaVersion, kind: "storylet", _meta, entries: [one]}`
    is read; the seed's names map to the C# names (spec §1); a legacy row's hosts come from the room-kind fit only.
  - A condition id whose leaf is not built yet refuses `storylet.condition-unknown` naming it.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.5 Preflight, structural rules.** *Depends:* NR2.4. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs`, `tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletContractTests.cs`
  (new), `tests/fixtures/narrative/storylets/red/` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* rules `storylet.choice-count`, `leave-count`, `lose-lose`, `dominated-choice`,
  `conditional-below-unconditional`, `mixed-shape`, `envelope`, `status`, `provenance-path`, `digit-in-text` each have
  a red fixture failing with exactly its rule id; ordinals rank `good > mixed > bad > nothing` as `OutcomeResolver`
  does; the seed side's own `validate_entry` green fixtures load green (once narrative-seed `narrative-contract`
  lands; until then spec-derived fixtures).
  *Registry row:* `ns-storylet-preflight-at-load` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.6 Preflight, consequence, role, condition and `teaches` rules.** *Depends:* NR2.5. *Agent:* implementer.
  *Files:* `EventDeckPreflight.cs`, `StoryletContractTests.cs`, red fixtures.
  *Accept:* `storylet.role-undeclared`, `consequence-shape`, `consequence-ref-missing`, `consequence-ref-forbidden`
  (including `battle.start` and `doctrine.setback`), `consequence-param` (including `none` on `relation.shift`),
  `condition-unknown`, `condition-context`, `teaches` each fail a red fixture with their id; `refForms`/`params` are
  read through `ConsequenceKindCatalog`, never restated.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.7 Canonical form, revision and tombstones.** *Depends:* NR2.5. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Storylets/StoryletCanonical.cs` (new), `EventCatalog.cs` (`Resolve`,
  `ChoiceConditionFor`, tombstones), `tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletCanonicalTests.cs` (new).
  *Accept:* `Serialize → Parse → Serialize` is byte-identical for every fixture; the hash is stable across two process
  runs and under key reordering in the source file; a tombstone's five-field row loads undrawable; a live row reusing a
  tombstoned id refuses `storylet.id-reused`; legacy rows have revision 0 and cannot be pinned.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.8 Gate G2: dangling chains fail; NS7 lands.** *Depends:* NR2.5. *Agent:* implementer.
  *Files:* `EventDeckPreflight.cs` (`event.chain-ref-dangling` a failure), `data/seed/dungeon/events/_known-defects.json`
  (new, authored: ids, rule, owner `narrative-seed`, task `delve-event-regen`), `StoryletContractTests.cs`,
  `docs/architecture/party-dungeon/spec-event-deck.md` (NS7 text and the stale §Structure paths; shared with
  `narrative-seed-idea-20260919`: clean-or-skip), `docs/architecture/decisions.md` (NS7 row; clean-or-skip).
  *Accept:* the committed corpus fails `event.chain-ref-dangling` for exactly the known-defect ids and passes otherwise;
  a stale entry (an id that no longer fails) fails the list's own test; the list may only shrink; the preflight reports
  each as a named defect, never a skip; `guard-generated-seed.py` stays green (the list is authored, not generated —
  it carries no `_meta.model`, which is what that guard reads).
  **Plan audit 2026-09-20 — this authored file sits inside a tree another program deletes.** narrative-seed **NS69**
  (its gate **NSG3**) deletes `gk-data/packs/fusion/data/seed/dungeon/events/**`, so `_known-defects.json` goes with it. That is correct
  and intended — the four dangling `story` tails cease to exist at the cutover — but state it here so the file is not
  later "restored" by reflex: the list is **born to shrink to zero and be removed**, and NS69's own accept ("the four
  legacy `story` events' known-defect entries are removed on the runtime side in the same change") is satisfied by
  deleting the file together with the tree, not by editing it. Record that in the evidence line.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `python gk-core/scripts/guard-generated-seed.py`.

### `story-ledger` (spec-story-ledger.md)

- [ ] **NR2.9 The ledger: schema, append, query, the world write gate.** *Depends:* NR1.1. *Agent:* **implementer-hard**
  (new tables in `FusionRpg.Data`).
  *Files:* `src/FusionRpg.Core/Narrative/Ledger/StoryFact.cs` (new), `src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs`
  (new: `rpg_story_fact`, `rpg_story_pin` DDL, `AppendStoryFact(s)[Unlocked]`, `ListStoryFacts`, `HasStoryFact`,
  `WorldNarrativePhaseOf`, plan §4 D7), `tests/FusionRpg.Data.Tests/Narrative/StoryLedgerStoreTests.cs` (new),
  `gk-core/scripts/enforcement-registry.v1.json`, `docs/architecture/decisions.md` (NS3; clean-or-skip).
  *Accept:*
  - A repeated append returns `(false, firstSeq)` and one row; reads order by `seq`; two independent facts appended in
    either order give the same set; world A's facts are invisible to world B and to another player.
  - `attrs_json` is closed per kind; a band on a relation fact is refused (a band is derived).
  - One test per lifecycle edge through a fixture phase reader, both orders of "append then hibernate" and "hibernate
    then append": dormant refuses a host-sourced append (`story.world-dormant`) and accepts a `coarse:` one; frozen
    refuses every world-scope append (`story.world-frozen`); save scope is never gated; no row is ever deleted or rewritten.
  - A text scan finds no `UPDATE`/`DELETE` against `rpg_story_fact` in Data source; `created_utc` is read by no decision.
  *Registry rows:* `ns3-story-ledger-append-only` → `["narrative"]`; `ns3-story-sql-in-data` → `["dal"]`;
  `ns-world-scope-never-deleted` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py`.

- [ ] **NR2.10 Pins.** *Depends:* NR2.9, NR2.7. *Agent:* implementer.
  *Files:* `RpgStore.StoryLedger.cs` (`WriteStoryPins`, `GetStoryPin`), `StoryLedgerStoreTests.cs`.
  *Accept:* a pin round-trips byte-identically and its hash matches; a tampered `content_json` is refused; a tombstoned
  storylet resolves through its pin; a pin written before or after a corpus bump resolves the same arc link.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs','tests/FusionRpg.Data.Tests/Narrative/StoryLedgerStoreTests.cs') -Session <sid>`.

- [ ] **NR2.11 Absorb the Delve's event-seen table (plan gate PG1).** *Depends:* NR2.9. *Agent:* **implementer-hard** (migration + drop).
  *Files:* `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs` (`RecordEventSeen`/`LoadPersistedEventSeen` wrap the ledger;
  DDL removed), `RpgStore.StoryLedger.cs` (the migration), `tests/FusionRpg.Data.Tests/Narrative/StoryLedgerMigrationTests.cs` (new).
  *Accept:* pre-seeded rows (`DataTestStore.CreateWithPreInitHot`) reappear as `storylet.seen` facts with equal read
  results; the copy is re-read and compared inside the transaction and the drop runs only on equality (PG1 default); a
  backup of a file-backed save is taken first (the one disk-semantics test, tagged `DiskSemantics`); `Init` twice is
  idempotent; `gk-core/tests/FusionRpg.Data.Tests/Delve/EventSeenStoreTests.cs` passes unchanged; first write still wins.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.12 Onboarding acknowledgement mirrors into the ledger.** *Depends:* NR2.9. *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs`, `tests/FusionRpg.Data.Tests/Narrative/OnboardingMirrorTests.cs` (new).
  *Accept:* acknowledging `rift-prologue`/`1` appends exactly one `scene.acknowledged` fact in the same transaction; a
  re-acknowledgement appends none; `rpg_onboarding_story` rows are byte-identical to before; every onboarding test passes.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs','tests/FusionRpg.Data.Tests/Narrative/OnboardingMirrorTests.cs') -Session <sid>`.

### `relation-ledger` (spec-relation-ledger.md)

- [ ] **NR2.13 One ladder arithmetic and the derived relation read model.** *Depends:* NR2.9, NR1.4. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Relations/DispositionLadder.cs` (new), `src/FusionRpg.Core/Narrative/Relations/RelationLedger.cs`
  (new), `gk-core/src/FusionRpg.Core/Delve/Wild/Disposition.cs` (`Shift` delegates), `tests/FusionRpg.Core.Tests/Narrative/Relations/RelationLedgerTests.cs`
  (new), `tests/FusionRpg.Guard.Tests/NarrativeRelationLadderGuardTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`,
  `docs/architecture/decisions.md` (NS2; clean-or-skip).
  *Accept:*
  - All 120 orders of the five relation facts give one band; 0 and 1,000 host-clock ticks with no new fact give the
    same band; ten `betrayed` end at `hostile` (the final-sum clamp, commented as structural).
  - `eager` reads `open` until the subject's unlock flag exists; `character.joined` yields `Joined`; `CanJoin` is true
    for `eager`/`open`/`wary`, false for `hostile` and `Joined`; a `Player` faction subject throws.
  - Every `gk-core/tests/FusionRpg.Core.Tests/Delve/Wild/` test passes unchanged.
  - A contract test finds no `FusionRpg.Core.Narrative` type reading a `LoyaltyRank` threshold or writing a loyalty or
    actor value; a Guard scan finds no disposition or reputation ladder type outside `Narrative.Relations` and `Dungeon/Registry`.
  *Registry rows:* `ns2-one-relation-ladder`, `ns2-relations-access-not-stats` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.14 `RelationReader` with the world phase.** *Depends:* NR2.13. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/RelationReader.cs` (new), `tests/FusionRpg.Server.Tests/Narrative/RelationReaderTests.cs` (new).
  *Accept:* one fact query per call; `RelationRead.Phase` from `WorldNarrativePhaseOf`; a clan's band is identical
  across fixture `active` → `hibernating` → `idle` → `active` → `fallen`, only the phase changes, no fact appended or
  deleted; `FactionBand(playerId, worldId, factionId)` is the method trade-network will call; no cache (spec §5's
  future trigger list kept in a comment).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `narrative-text` (spec-narrative-text.md)

- [x] **NR2.15 Token grammar, binder and the one wire text shape.** *Depends:* NR1.2; narrative-seed `token-grammar`
  for the real grammar (fixtures until then). *Agent:* implementer.
  *Done (npc-story-events-2, 2026-09-23):* `TokenGrammar` (the closed token and markup grammar — the three leads,
  `c_<slug>`/`_epithet`, the five suffixes, `role_<id>`, the four placeholders, the four markup tags — with one rule
  id per refusal: `storylet.stray-brace`, `unknown-token`, `role-undeclared`, `character-unknown`, `markup-unknown`,
  `markup-unbalanced`, `digit-in-text`); `StoryTextBinder` + `StoryletCast`/`CastBinding` (one binder for every text
  field; `role_<id>` binds to what the role was cast to; an unbound token throws `StoryTextBindingFailure` naming it);
  `NarrativeTextDto`/`TokenRefDto` in Contracts (references only — no display member, and a reflection test asserts
  exactly one Contracts type carries a key plus a token map). Printed readings: `NarrativeTextTests` 23/23;
  `guard-narrative.py` `4 row(s) guarded by 'narrative', 4 mapped`; `-RunTraitFilter` selects 53 Core + 5 Guard tests,
  0 failed (30 before this row); `EnforcementRegistryGuardTests` 18/18; `guard-verification-boundaries`
  `VERIFICATION BOUNDARY GUARD OK`; `verify-change` over the five paths exit 0 with **70 project runs, 15966 passed,
  0 failed**; `audit-overflow.py` 0 critical. The row's refusal tests caught two real defects while implementing
  (an optional regex group reports `Success` even when it matched the empty string, so every tag looked self-closing
  and every unbalanced-markup case returned an empty issue list). *Verify deviation:* `-Session <sid>` cannot resolve
  in this lane; run as `-AllowUnscoped`. The web half (codegen, second lingui catalog, `useNarrativeText`) is NR2.16/2.17
  and `web/**` is outside this lane's fence. Evidence: `tasks/reports/npc-story-events-2-nr215-evidence-20260923.md`.
  *Registry row:* `ns-one-narrative-text-dto` → `["narrative"]` (landed with its guard map line).
  *Files:* `gk-core/src/FusionRpg.Core/Narrative/Text/TokenGrammar.cs` (new), `gk-core/src/FusionRpg.Core/Narrative/Text/StoryTextBinder.cs`
  (new), `gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Narrative/Text/NarrativeTextTests.cs`
  (new), `gk-core/scripts/enforcement-registry.v1.json`, **`gk-core/src/FusionRpg.Core/Narrative/LeadNames.cs`** (identity-rename T1's
  file: use it if T1 has landed, otherwise create it at that exact path with T1's acceptance criteria, plan §4 D6 —
  **Plan audit 2026-09-20:** the prose said this but the *Files* list omitted it, so the file would have been written
  outside the task's declared fence and outside its `-Paths`). Lead names read through `LeadNames.cs` (plan §4 D6).
  *Accept:* unknown token, stray brace, undeclared role, unknown `c_<slug>`, unbalanced markup and a digit each reject
  with their rule id; every token in a fixture storylet binds from a fixture cast or binding fails naming it; a
  magnitude carries `long`; no display string crosses the wire; a Contracts reflection test finds no DTO other than
  `NarrativeTextDto` carrying a key plus a token map.
  *Registry row:* `ns-one-narrative-text-dto` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.16 The lingui codegen bridge over narrative seeds.** *Depends:* NR2.15. *Agent:* implementer.
  *Files:* `web/fusion-rpg-web/scripts/gen-narrative-messages.mjs` (new), `web/fusion-rpg-web/src/features/narrative/generated/narrativeMessages.generated.ts`
  (new, generated), `gk-web/web/fusion-rpg-web/lingui.config.ts` (second catalog), `web/fusion-rpg-web/src/features/narrative/generatedMessages.test.ts`
  (new), `gk-web/web/fusion-rpg-web/src/i18n/locales/{en,pseudo}/narrative.*` (new, extracted).
  *Accept:* one literal `msg({ id, message })` per key, sorted, with a do-not-edit header; `--check` passes on the
  committed file, fails after a fixture seed's text changes, and runs inside `npm test` (the `gen-tokens` precedent);
  two seeds with one key and different text fail generation; the named-tag probe (spec §5 step 2) is run first and its
  result recorded; the narrative catalog is excluded from the main catalog.
  *Verify (unmapped web paths):* `cd gk-web/web/fusion-rpg-web; node scripts/gen-narrative-messages.mjs --check; npx vitest run src/features/narrative; npm run extract; npm run build; npm run check:bundle`.

- [ ] **NR2.17 Web rendering on tokens.** *Depends:* NR2.16. *Agent:* implementer.
  *Files:* `web/fusion-rpg-web/src/features/narrative/renderNarrative.tsx` (new), `gk-web/web/fusion-rpg-web/src/i18n/leadNames.ts`
  (identity-rename T3's file: use it, or create it at that path with T3's acceptance, plan §4 D6),
  `web/fusion-rpg-web/src/features/narrative/narrativeText.test.ts` (new), `gk-core/scripts/enforcement-registry.v1.json`,
  `docs/architecture/decisions.md` (NS5; clean-or-skip).
  *Accept:* each fixture message renders with the real lead rows and with a test registry of different names, and the
  outputs differ exactly at token positions; no test-registry display string appears in output that does not use its
  token; `article` selects "The Rotwright" sentence-initially and "the Rotwright" mid-sentence; an unknown token kind
  throws; switching `en` → `pseudo` reloads the narrative catalog and re-resolves lead names without a page reload
  (the key-set edge of both static caches); the narrative module stays out of the entry chunk.
  *Registry row:* `ns5-names-are-tokens` → `["narrative"]` (the C# half in NR2.15's binder test, the web half here).
  *Verify:* NR2.16's npm commands plus `npx vitest run src/features/narrative src/i18n`; `.\scripts\verify-change.ps1 -Paths @('gk-core/scripts/enforcement-registry.v1.json','docs/architecture/decisions.md') -Session <sid>`.

### `host-content-theta` (spec-host-content-theta.md)

- [x] **NR2.18 Θ per host through the one composer.** *Depends:* NR0.2. *Agent:* implementer.
  *Done (npc-story-events-2, 2026-09-23; code landed 2026-09-22 in 2e7d5ba61):* `HostContentTheta` (ForSector /
  ForHomeworld / ForDelveRoom, later ForExpedition) composes every host's Θ through the one
  `PowerIndexComposer.ContentExplain`, and `ParentWorldTermsSource` is the only producer of the parent terms with each
  missing term's owner named in code; two source scans with planted-violation falsifiers enforce the SOLID rule; the
  registry row `ns-one-content-theta-producer` landed with its guard map line. Printed readings:
  `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Hosts|FullyQualifiedName~Expedition|FullyQualifiedName~Power"` 69/69;
  `guard-narrative.py -RunTraitFilter` selects 30 (Core) + 5 (Guard), 0 failed; `verify-change` over the five
  changed paths exited 0 with 63 project runs and 16134 passed previously, and 9588/9588 on the whole Core project
  in this segment. *Verify deviation:* the row's Verify line names `-Session <sid>`, which cannot resolve in this lane
  (`tasks/sessions/**` is outside its allowed paths), so it was run as `-AllowUnscoped` — the erratum asked for in the
  NR2.18 evidence fragment stands. Evidence: `tasks/reports/npc-story-events-2-nr218-evidence-20260922.md`.
  *Files:* `gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs` (new), `gk-core/src/FusionRpg.Core/Narrative/Hosts/ParentWorldTermsSource.cs`
  (new), `gk-core/tests/FusionRpg.Core.Tests/Narrative/Hosts/HostContentThetaTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* for bands 0–6 and non-zero parent terms `ForSector` equals `PowerIndexComposer.ContentExplain(...).Total`;
  `ForDelveRoom` passes the room's Θ and context through; `ForHomeworld` equals a band-0 sector; Θ does not decrease as
  the band rises (a relation); a source scan finds `new ParentWorldTerms(` only in `ParentWorldTermsSource` and tests,
  and `new ContentContext(` in `Narrative/` only in `HostContentTheta`; each missing term's owner is named in code.
  Files ask A5 (`ssot-power-scale.md` §8 row 6) in the evidence line.
  *Registry row:* `ns-one-content-theta-producer` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `python scripts\audit-overflow.py`.

- [x] **NR2.19 Publish `expeditions.v2.json` (danger bands and encounter chances).** *Depends:* NR2.18. *Agent:*
  **implementer-hard** (a publish whose readers switch in the same commit).
  *Done (npc-story-events-2, 2026-09-23):* `expeditions.v2.json` published through `gk-core/tools/tuning/publish.py
  --add-key` (four `tiers.*.dangerBand` 1–4 and the `encounter` block, 250/50); `ExpeditionTierNumbers.DangerBand`
  and `ExpeditionEncounterTuning` are required by the loader; `ExpeditionTierDef.DangerBand` and
  `HostContentTheta.ForExpedition` consume it; all five reader call sites (Server host, Injector host,
  `ProveHubCombat`, `_TempSeedSpecies`, `AptitudeChannelModsTests`) and the shared test bootstrap moved to v2, and
  `ExpeditionTuningTests` proves a reader left on v1 now throws. **Blocked sub-item:** the `expeditions` real-tree row
  in `gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs` is refused by the pipeline guard (protected
  guard-test file, outside this lane's grant) — recorded as a blocker for the orchestrator. Evidence:
  `tasks/reports/npc-story-events-2-nr219-evidence-20260923.md`.
  *Files:* `gk-core/data/tuning/expeditions.v2.json` (new, via `python gk-core/tools/tuning/publish.py expeditions --add-key ...`),
  `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs`, `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTierCatalog.cs`
  (`DangerBand`), the expedition tuning tests (shared with lane C: region check).
  *Accept:* `tiers.{tierId}.dangerBand` (1, 2, 3, 4 for the four tiers) and `encounter.wildCreatureMetMilli` (250),
  `encounter.quietMilli` (50) are required keys (plan §4 D4); deleting `tiers.hunt-8h.dangerBand` rejects naming it; the
  expedition resolver's tier hashes are byte-identical with v2 loaded; every loader reads v2.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/data/tuning/expeditions.v2.json','gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs','gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTierCatalog.cs',<the test file>) -Session <sid>`.

### `delve-live-start` (spec-delve-live-start.md) — party-dungeon D4.16, D4.22, D4.14 (offer half)

- [ ] **NR2.20 Boot import of the domain corpus.** *Depends:* NR0.2. *Agent:* implementer.
  *Files:* `src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs` (one call
  after `PassiveTreeImportRunner`; shared: region check), `tests/FusionRpg.Data.Tests/Seed/DungeonDomainImportRunnerTests.cs`
  (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* a fixture tree of passing domains imports them; a tree with one refusing domain imports none and returns
  the refusal without throwing; a missing tree returns a not-found status; two runs are idempotent; the boot prints the
  outcome in the `[content]` voice; which real domains pass is printed, never asserted.
  *Registry row:* `ns-delve-boot-import-never-throws` → `unguardableReason` (plan §4 D3).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.21 The five `/start` delegates.** *Depends:* NR2.20, NR2.18. *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Server/DelveEndpoints.cs` (`BuildDelveStartLive` delegates only), `src/FusionRpg.Server/Delve/DelveParentTerms.cs`
  (new: chooses the world, calls `ParentWorldTermsSource.For`), `gk-core/tests/FusionRpg.Server.Tests/DelveDomainsAndStartEndpointsTests.cs`.
  *Accept:* against an imported fixture domain `HandleStart` returns `{delveId, worldId}` and the header carries
  `content_terms_json` and the first decision; a replay returns the same delve; a stale fixture refuses `domain.stale`,
  an unoffered rung `rung.not-offered`, unaffordable provisioning `delve.souls-insufficient` — each through the real
  handler; the three `GET /domains` display delegates are untouched (D4.19 stays party-dungeon's).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.22 The quest offer at `CreateDelve` and the tracker route.** *Depends:* NR2.21. *Agent:* implementer.
  *Files:* `DelveEndpoints.cs` (offer inside the start transaction; `GET /api/delve/{delveId}/quests`),
  `tests/FusionRpg.Server.Tests/DelveQuestTrackerEndpointTests.cs` (new).
  *Accept:* a start persists a non-empty `quests_json` drawn by `QuestOffer.Draw` on `dungeon:quest`; a replayed start
  returns the stored offer and draws nothing; the route returns `QuestDto`s; another player's delve is refused; the
  `QuestDto` engine-word reflection scan stays green; verdicts at `CloseDelve` are not written here.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/DelveEndpoints.cs','tests/FusionRpg.Server.Tests/DelveQuestTrackerEndpointTests.cs') -Session <sid>`.

### `delve-live-rooms` (spec-delve-live-rooms.md) — party-dungeon D3.9, D3.3/D3.5 live call site

- [x] **NR2.23 `EnterRoomWithDraw`: move, mark and seen writes in one transaction.** *Depends:* NR2.11 (or the
  pre-migration store; the signatures are unchanged). *Agent:* implementer.
  *Done (npc-story-events-2, 2026-09-23):* `EnterRoomWithDraw` composes the three writes in ONE transaction —
  the move (`MovePartyUnlocked`), the mark (`MarkRoomUnlocked`: `visited` + the drawn `event_id`) and every
  persisted seen scope (`RecordEventSeenUnlocked`, `per-domain` + `once-per-player`, the two
  `LoadPersistedEventSeen` reads back) — and returns the stored id WITHOUT writing when the room already
  carries an `event_id` (`event.already-drawn`). The dependency's own escape hatch was taken: NR2.11 is not
  done, and the pre-migration `rpg_delve_event_seen` table with unchanged signatures is what this composes
  against. `MoveParty`/`RecordEventSeen` keep their signatures and now delegate to the unlocked variants, so
  there is one SQL text per write; `MarkRoom` keeps its wider column set. Fault seam is the repo's own idiom
  (`internal Action? EnterRoomMidTestHook`, like `FusionMidTestHook`). Printed readings:
  `EnterRoomWithDrawTests` 5/5; the Delve-filtered Data suite 187/187; `verify-change` exit 0 with
  `TEST-SHARDED OK: 4 shards, 1746 tests, no overlap`; `guard-dal` `DAL GUARD OK`; `test-substrate` OK.
  *Verify deviation:* `-Session <sid>` cannot resolve in this lane; run as `-AllowUnscoped`. Cross-program:
  party-dungeon's `pd-d3` lane named this row as a dependency of D4.14/D4.32 (`1fc9d1fea`). Evidence:
  `tasks/reports/npc-story-events-2-nr223-evidence-20260923.md`.
  *Files:* `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs` (unlocked variants and the composed method),
  `gk-core/tests/FusionRpg.Data.Tests/Delve/EnterRoomWithDrawTests.cs` (new).
  *Accept:* one call moves the party, marks the room with its drawn id and records each persisted scope; a room with a
  stored `event_id` writes nothing and returns it; a fault injected after the mark leaves neither the move, the mark nor
  a seen row.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs','gk-core/tests/FusionRpg.Data.Tests/Delve/EnterRoomWithDrawTests.cs') -Session <sid>`.

- [ ] **NR2.24 `POST /api/delve/rooms/{id}/enter` with the pack-sourced override fact.** *Depends:* NR2.23, NR2.22, NR2.2. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/DelveEventEndpoints.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs` (`MapDelveEvents`),
  `tests/FusionRpg.Server.Tests/DelveEventEndpointsTests.cs` (new).
  *Accept:* entering an event-capable room draws once through `DelveStoryletHost.Resolve`; re-entry returns the same id;
  a gated door refuses with `LaneGate`'s reason and writes nothing; `holdsOverrideStock` comes from the party's pack (a
  pack with the supply tag draws the forced outcome, one without draws the ordinary one); `DelveUpdated` fires; a wipe
  after the draw leaves the event seen, in both orders of "draw then wipe" and "wipe then re-enter"; a replayed
  `correlationId` returns the first result.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.25 `POST /api/delve/rooms/{id}/answer`.** *Depends:* NR2.24. *Agent:* implementer.
  *Files:* `DelveEventEndpoints.cs`, `DelveEventEndpointsTests.cs`, `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* a non-steered party (seam stubbed false) and a room with no drawn event are refused; the rebuilt resolution
  must equal the stored `event_id` or the answer refuses naming the room; the answer is in `decisions_json` before its
  effects apply; a replay applies nothing twice; a route-table test finds this the only event-answer route.
  *Registry row:* `ns-delve-one-answer-path` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR2.26 The bridge reads the keyed legacy Delve events.** *Depends:* NR2.16; narrative-seed
  `dungeon-generator-repair` including its regeneration run. *Agent:* implementer.
  *Files:* `gen-narrative-messages.mjs`, `narrativeMessages.generated.ts` (regenerated), `generatedMessages.test.ts`,
  the extracted narrative catalogs.
  *Accept:* every legacy event's keyed `name` and `flavor` is emitted; a fixture legacy row without a key refuses
  generation naming the file; `--check` green on the committed tree.
  *Verify:* NR2.16's npm commands.

- [ ] **NR2.27 Event text on the wire: `DelveEventDto`.** *Depends:* NR2.26, NR2.25, NR2.15. *Agent:* implementer.
  *Files:* `src/FusionRpg.Contracts/Delve/DelveEventDto.cs` (new), `DelveEventEndpoints.cs`, `gk-web/web/fusion-rpg-web/src/contract/types.ts`
  and `adapt.ts` (`EventView` from the DTO; the stale adapter comment at the `EventView` block removed),
  `gk-web/web/fusion-rpg-web/src/contract/delveViews.test.ts`, `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* a widened fixture row's and a keyed legacy fixture row's `name`/`situation` both arrive as
  `NarrativeTextDto`s; an unkeyed legacy fixture row is refused at load naming the file; no raw seed string reaches the
  DTO; no `EventView` field is `Pending`.
  *Registry row:* `ns-no-blank-event-text` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Contracts/Delve/DelveEventDto.cs','src/FusionRpg.Server/DelveEventEndpoints.cs','gk-core/scripts/enforcement-registry.v1.json',<server test>) -Session <sid>`; `cd gk-web/web/fusion-rpg-web; npx vitest run src/contract/delveViews.test.ts; npm run build`.

### `world-claim-loot` (spec-world-claim-loot.md) — reviewed with world-map-program and the item program

- [ ] **NR2.28 R22: the mythic claim bonus seeds from the world seed (plan gate PG3).** *Depends:* NR0.2. *Agent:*
  **implementer-hard** (a change that can move stored values).
  *Files:* `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs`, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (`Snapshot`
  passes the seed), `gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs`.
  *Accept:* before and after the edit: the world golden suite's state hashes and stored reports byte-identical; the
  mechanism test `A_boss_lair_claim_can_roll_an_independent_mythic_bonus_reproducibly` green; a scan of a real server
  data directory's `rpg_world_turn_log.report_json` for `claim.mythic:` (PG3: zero rows → commit; rows → report world
  ids and hold the commit). New tests: replay determinism with the rate set; turn independence (turn 3 vs 9); world
  independence over a fixed seed list (a relation, never a pinned rate). Stream name unchanged.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs') -Session <sid>`.

- [ ] **NR2.29 Turn the claim seam on at commit and replay.** *Depends:* NR2.28. *Agent:* **implementer-hard**.
  *Files:* `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (pass `PowerTuningHub.Tuning` to `Step` at commit and
  replay), `tests/FusionRpg.Data.Tests/World/ClaimSeamTests.cs` (new).
  *Accept:* a player claim on danger ≥ 1 writes `claim.loot:{tableId}`; band 0 writes none; replay re-derives the same
  lines; state hashes are byte-identical (the report is not hashed); a turn without such a claim stores a
  byte-identical report; any report golden that gains a line is listed and re-blessed under world-map-program review in
  this commit (measured); no `RulesetVersion` bump is proposed here (spec §4).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','tests/FusionRpg.Data.Tests/World/ClaimSeamTests.cs') -Session <sid>`.

- [ ] **NR2.30 `ClaimLootPass`: mint once per sector per world; the take-a-line API.** *Depends:* NR2.29. *Agent:* **implementer-hard**.
  *Files:* `src/FusionRpg.Data/Sqlite/RpgStore.ClaimLoot.cs` (new: the pass, `UnusedClaimLootLinesUnlocked`,
  `MintClaimLootLineUnlocked`), `RpgStore.WorldTurns.cs` (call after cargo, before the log insert; Θ_actor delegate),
  `gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (passes the delegate; shared with lane D3: region check),
  `tests/FusionRpg.Data.Tests/World/ClaimLootPassTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* a band-3 player claim writes one `item_drop_log` row with correlation `loot:sector:{worldId}:{sectorId}`
  and items owned by the player with origin `world-claim`; two stores with one seed and log give identical manifests;
  re-running the pass and replaying mint nothing; lose and retake mints nothing the second time; two worlds from one
  template each mint their own; a Zomboss-kind claim writes its line and mints nothing; a fixture narrative pass that
  takes one of two lines with a window leaves the claim pass minting only the other, and the item-roll count equals the
  line count; a pipeline refusal leaves the line unused and the turn commits; sinks named in the evidence line (spec §5).
  *Registry row:* `ns-world-claim-loot-once` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `.\scripts\guard-dal.ps1`.
  **Full suite (point 2):** the pass crosses Data, Server and the world goldens.

### `world-anomaly-sites` (spec-world-anomaly-sites.md) — reviewed with world-map-program and world-continuity

- [x] **NR2.31 Anomaly allow-list (catalog half).** *Depends:* NR0.2. *Agent:* implementer.
  *Done (npc-story-events-2, 2026-09-23):* `"anomaly"` added to `storm`, `nexus` and `barren` `AllowedSlotTypes`
  (`SectorTypeCatalog.cs`), each with its own reason comment; the id itself already existed
  (`SlotTypeCatalog.cs:76`, `SlotKind.Anomaly`), so no slot-type row changed. New
  `gk-core/tests/FusionRpg.Core.Tests/World/AnomalySiteTests.cs` (6 tests): the allowing set asserted equal to
  `barren`/`nexus`/`storm`; `stable` and `boss-lair` keep `vault` and gain no second study site; a `stable` sector
  given an `anomaly` slot is refused by `WorldValidation` naming sector + slot type, with the same edit on `barren`
  as the positive control; and no shipped template places one yet. Printed readings: `AnomalySiteTests` 6/6;
  whole `gk-core/tests/FusionRpg.Core.Tests` 9588/9588 (1 m); `gk-core/tests/FusionRpg.Core.Items.Tests` 1468/1468;
  `gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~World"` 93/93;
  `gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~LoamPersistence"` 2/2; `audit-overflow.py` 0 critical.
  `verify-change -PlanOnly` resolves both paths to `core-fallback`/`core-tests-fallback` (the whole `core` group),
  so the three projects that can read the catalog were run in full instead — a named deviation in the evidence
  fragment, as is the `-Session <sid>` -> `-AllowUnscoped` rename. Evidence:
  `tasks/reports/npc-story-events-2-nr231-evidence-20260923.md`.
  *Files:* `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs`, `gk-core/tests/FusionRpg.Core.Tests/World/AnomalySiteTests.cs` (new).
  *Accept:* `anomaly` is allowed exactly on `storm`, `nexus`, `barren` (a declared set, pinned with its reason); a
  fixture `stable` sector with an `anomaly` slot is refused by `WorldValidation`; every existing world test and golden
  is byte-identical (the list is validation only).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs','gk-core/tests/FusionRpg.Core.Tests/World/AnomalySiteTests.cs') -Session <sid>`.

- [ ] **NR2.32 New template versions: three anomaly and three vault slots.** *Depends:* NR2.31; world-continuity
  `world-creation`'s `WorldCreation.Rebuild` (versioned replay). *Agent:* **implementer-hard** (template versions and
  their golden re-bless).
  *Files:* `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs`,
  `AnomalySiteTests.cs`, the new-version goldens, **`docs/architecture/npc-story-events-map.md`** (row 31: R23 is
  answered, not "still open") and **`docs/architecture/npc-story-events/spec-world-anomaly-sites.md`** (§4 and §6
  rewritten to plan D8's three picks — they still carry the pre-R23 text and contradict the spec's own R23 note;
  **Plan audit 2026-09-20**, plan §4 D8). Docs are `docs-and-assistant-config`-mapped, shared: clean-or-skip.
  **Shared with identity-rename T13**, which edits the same two catalog files and re-blesses the same goldens: run
  clean-or-skip first; whichever lands second re-runs the golden suite after the first and lists the **full** moved
  set, never only its own delta (plan §8.2).
  *Accept:*
  - The current `first-light` version adds unguarded `anomaly` at `black-gate` index 3 and `ash-waste` index 3, and a
    guarded `vault` at `frost-mire` index 3; the current `two-hearths` version adds unguarded `anomaly` at `corridor-4`
    index 2 and guarded `vault` at `d-flank-2` index 3 and `z-flank-2` index 3 (plan §4 D8); both validate; indexes stay
    contiguous.
  - Each new version places at least one `vault` reachable over lanes from its start sector (R23's test).
  - A world stamped with a pre-change version rebuilds and replays byte-identically (state hash and stored report).
  - A sector whose other guards are cleared is claimable with its anomaly present; `ValueMap` for the new `black-gate`
    differs from the old by the anomaly term alone (a relation).
  - New-version goldens re-blessed in this commit under world-map-program review, every moved hash listed
    (**measured**: the suite is run before and after, and the before-run is quoted — a re-bless never assumes which
    hashes moved).
  - The map row 31 and `spec-world-anomaly-sites.md` §4/§6 no longer say the vault question is open;
    `python scripts/audit-doc-citations.py --scope docs/architecture/npc-story-events` reports no HIGH finding.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.
  **Full suite (point 2):** template versions cross Core, Data replay and the world goldens.

### Checkpoint 2 — one engine; the Delve starts and plays (after NR2.32)
- [ ] G1: engine moved, event-deck tests unchanged, goldens byte-identical, legacy and widened shapes in one catalog.
- [ ] G2: dangling chains fail or are listed owned defects.
- [ ] Record which of NR2.26, NR2.27, NR2.32 still wait on an external module; the checkpoint does not wait for them.
- [ ] **Full suite (point 3)**, then NR-LP1.

- [ ] **NR-LP1 Live probe: the Delve starts and its rooms play.** *Depends:* Checkpoint 2's full suite; NR2.20–NR2.25
  (and NR2.27 if landed). *Agent:* test-engineer or the implementing session.
  *Files:* `tasks/evidence-fragments/NR-LP1.md` (new).
  *Do (RPG Server scope only, `live-probe-standard.md`):* start the published server as its own process
  (`Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`); read the boot's `[content]` domain line; for a real
  player created through the real onboarding flow, `GET /api/delve/domains/{playerId}`; `POST /api/delve/start` with a
  real roster; read the delve back with `GET /api/delve/{id}` and `GET /api/delve/{id}/quests`; `POST
  /api/delve/rooms/{id}/enter` on an event-capable room; read the room back through `GET /api/delve/{id}`; `POST
  .../answer`; read `decisions_json` back through the normal delve read.
  *Accept:* every subject was created by a real flow; every result was read back through the normal query route; no
  `debug.*` command and no hand-inserted row; the file states each call's scope and that the Injector half was not
  claimed. Display fields still `Pending` from D4.19 are a reading, not a failure.

---

## Phase 3 — Wave 2

### `character-registry` (spec-character-registry.md)

- [ ] **NR3.1 Character seed catalog and the fate fold.** *Depends:* NR1.3, NR2.7; narrative-seed `narrative-contract`
  character schema (fixtures until then). *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Characters/CharacterCatalog.cs` (new), `src/FusionRpg.Core/Narrative/Characters/NarrativeCharacter.cs`
  (new: row record, fate and state fold), `tests/FusionRpg.Core.Tests/Narrative/Characters/CharacterCatalogTests.cs` (new).
  *Accept:* species validated through `CreatureSpeciesCatalog.IsKnown`, role and voice through their catalogs; a reused
  tombstone id refused; fate is the latest of `character.joined`/`fell`/`departed` by `seq`, else `Present`, and a
  world transition never produces `Departed` or `Fallen`; `CharacterState` adds `Unmet`/`Met` from the `met` fact.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.2 The character table, the cast owner row and casting operations.** *Depends:* NR3.1, NR2.9. *Agent:*
  **implementer-hard** (new table; specimens minted under a non-player owner).
  *Files:* `src/FusionRpg.Data/Sqlite/RpgStore.NarrativeCharacters.cs` (new: `rpg_narrative_character`,
  `EnsureNarrativeCastPlayer`, `MintForNarrativeCast`, `CastCreatureCharacter`, `EnsureLeadCharacters`, `GetCharacter`,
  `ListCharacters`), `tests/FusionRpg.Data.Tests/Narrative/NarrativeCharacterStoreTests.cs` (new),
  `docs/architecture/decisions.md` (NS4; clean-or-skip).
  *Accept:* a cast creates one row and one specimen owned by the cast owner row with `origin = narrative`, traits rolled
  on `narrative:cast:mint`, row + specimen + cast fact in one transaction; a second cast with the same source is a
  no-op; the character's personality equals `ContractPolicy.PersonalityFor(instanceId)` and no personality column
  exists; `EnsureLeadCharacters` creates three save-scoped rows with no specimen, idempotently; no fate column.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py`.

- [ ] **NR3.3 Join by ownership transfer; the adopt variant.** *Depends:* NR3.2. *Agent:* **implementer-hard**
  (rewrites `rpg_unique_actors.player_id` on the owner's save).
  *Files:* `RpgStore.NarrativeCharacters.cs` (`TransferCharacterToRoster`; `CastCreatureCharacter` adopt variant for an
  existing player-owned specimen, filed by `expedition-lead-host` §4), `NarrativeCharacterStoreTests.cs`.
  *Accept:* after a transfer the roster holds the **same** `instanceId`, the owner row no longer owns it, one
  `character.joined` fact exists, a second transfer and a transfer of a `Departed`/`Fallen` character refuse; a
  per-player side row for the specimen refuses; "join then fall" keeps the creature with the player and "fall then
  join" refuses `character.world-not-live`, and the same pair for hibernation (refused while `Dormant`, allowed after
  return); every world-lifecycle edge leaves rows, specimens and facts byte-identical; the adopt variant binds a
  character to the player's existing specimen with fate `Joined` and mints nothing.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.4 Anti-Nemesis guards, rules 1–3 and 5.** *Depends:* NR3.3. *Agent:* implementer.
  *Files:* `tests/FusionRpg.Guard.Tests/NarrativeNoEnemyGrowthTests.cs` (new), `RpgStore.StoryLedger.cs` (the narrative
  append wrapper refuses a relation fact about an enemy-role subject), `NarrativeCharacterStoreTests.cs`,
  `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* the scan fails an in-memory probe that writes `rpg_unique_actors.level`/`xp`, `rpg_creature_profiles.star`,
  trait ids or a title grant from `gk-core/src/FusionRpg.Core/Narrative/**`, `RpgStore.Narrative*.cs` or `RpgStore.StoryLedger.cs`,
  and fails a probe type named `*Rank*`, `*Captain*` or `*Hierarchy*` under `Narrative/` (`LoyaltyRank` outside the
  scan untouched); an enemy-role subject refuses `met`/`helped`/`refused`/`betrayed`/`spared`; an enemy specimen's
  `(level, xp, star, traits)` is identical before and after every operation of this module.
  *Registry rows:* `ns6-no-enemy-growth`, `ns6-no-enemy-memory`, `ns6-no-enemy-hierarchy` → `["narrative"]`;
  `ns6-no-enemy-data-sharing` → `unguardableReason` "the game has no network upload path to scan" (upgraded at NR6.5).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `cast-resolver` (spec-cast-resolver.md)

- [ ] **NR3.5 Role casting per storylet and resource binding.** *Depends:* NR3.2, NR2.13, NR2.6. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Casting/CastResolver.cs` (new), `src/FusionRpg.Core/Narrative/Casting/EntityRef.cs`
  (new), `EventDeckPreflight.cs` (`storylet.optional-role-in-situation`), `tests/FusionRpg.Core.Tests/Narrative/Casting/CastResolverTests.cs`
  (new), `tests/FusionRpg.Guard.Tests/NarrativeStreamNamesTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* candidates are `Present` characters whose world phase is `Live`, the arc's cast, and party creatures only
  when `source` admits `party`; `requires` filters on the four `RoleTagCatalog` families; required uncastable →
  `Uncastable`, castable forbidden → `Forbidden`, optional unbound makes its gated choices ineligible; a met, friendlier
  candidate outscores an unmet one; ties break by the seeded `narrative:cast:role` draw, the same on every run and
  different across two host clock values; scores `long`, `checked`; the recency `min` is commented as a bounded
  window; a character in a `Dormant` or `Frozen` world is never a candidate and is castable again after return (both
  orders); `{place}`/`{supply}` bind to `EntityRef`s, `{reward}`/`{cost}` to `Pending`; a Guard scan over
  `gk-core/src/FusionRpg.Core/Narrative/**` fails any narrative roll whose stream name does not start `narrative:` or that
  names a `battle:`/`dungeon:` stream.
  *Registry row:* `ns-narrative-streams-named` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.6 Arc casting.** *Depends:* NR3.5, NR2.10. *Agent:* implementer.
  *Files:* `CastResolver.cs`, `CastResolverTests.cs`.
  *Accept:* the first link's cast is written into the `arc.started` attrs with the pins in one ledger transaction;
  link 2 names link 1's character; a fallen cast character makes a later link ineligible without recasting.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Casting/CastResolver.cs','tests/FusionRpg.Core.Tests/Narrative/Casting/CastResolverTests.cs') -Session <sid>`.

- [ ] **NR3.7 World and save casting at world creation.** *Depends:* NR3.5. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Casting/WorldCast.cs` (new, pure plan), `data/tuning/narrative-cast-catalog.v1.json`
  (new: `residentRolesBySlot` and `residentRolesByRoomKind`, plan §4 D4), `src/FusionRpg.Server/Narrative/WorldCastStep.cs`
  (new, called after world creation), `tests/FusionRpg.Server.Tests/Narrative/WorldCastTests.cs` (new).
  *Accept:* one world seed, ledger and corpus give one cast on two runs; over 64 fixed world seeds the resident casts
  are not all identical (a property); the save seed is the fixed-root `narrative:save:{playerId}` derivation; the step
  run twice adds no row; companions are cast on the save's first world with `casting.saveCastPerRole`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `python scripts\audit-magic-numbers.py --domain narrative`.

### `narrative-predicates` (spec-narrative-predicates.md)

- [ ] **NR3.8 Six narrative leaves: enum, validation, context rule.** *Depends:* NR2.4. *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs` (six members appended), `PredicateCompiler.cs`
  (`NarrativeCompileContext`, `ValidateLeaf` arms), `AtomRejection.cs` (`LeafNotInContext`),
  `docs/architecture/effect-atom/definitions.md` (the rejection list), `docs/architecture/effect-atom/spec-predicate-tree.md`
  (leaf table, 22), `tests/FusionRpg.Core.Tests/Narrative/Predicates/NarrativeLeafTests.cs` (new).
  *Accept:* `Enum.GetValues<LeafId>().Length == 22`, commented as a closed vocabulary with this spec as the reason;
  existing ordinals unmoved; each leaf compiles a valid argument and rejects empty text, a negative value, a zero
  threshold and a wrong subject with the compiler's reason; a narrative leaf compiled without a context rejects
  `LeafNotInContext`; every atom, action and event test passes unchanged.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.9 Evaluation: the narrative frame, both compiled forms.** *Depends:* NR3.8. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Effects/Atoms/NarrativeFrame.cs` (new), `FactReader.cs` (one reference field and three
  readers), `CompiledAtom.cs` (intern and evaluate arms, `NarrativeSlots`), `PredicateCompiler.cs` (typed nodes),
  `NarrativeLeafTests.cs`, `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* the flat-vs-typed equivalence fuzz includes the six leaves and agrees on every case; a combat `FactReader`
  evaluates a narrative leaf false without throwing; `EntityFacts` has the same members; battle goldens byte-identical;
  `tests/FusionRpg.Core.Tests/Atoms/AtomBenchGuardTests.cs` within budget; a 16-reference tree compiles and interning
  never exceeds `SlotCount`; a reflection test finds no `FusionRpg.Core.Narrative` type referenced by `Effects.Atoms`
  except through the context delegates.
  *Registry row:* `ns-narrative-leaf-context` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.10 `ConditionCompiler` narrative arms and the frame builder.** *Depends:* NR3.9, NR2.14. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Predicates/ConditionCompiler.cs`, `src/FusionRpg.Core/Narrative/Predicates/NarrativeFrameBuilder.cs`
  (new), `tests/FusionRpg.Core.Tests/Narrative/Predicates/ConditionCompilerTests.cs` (new).
  *Accept:* each id of a fixture `conditions.v1.json` compiles to its leaf or role gate per spec §5's table; unknown
  id, band, state or gate id rejects naming it; a slot-only id in an eligibility list and an eligibility-only id on a
  slot reject; the set of leaves in the table equals the seed file's `proposedLeaves` plus the built leaves it names;
  `lead-level-at-least` reads `gates.leadLevel`; the frame builder fills one int per slot from a `NarrativeFactView`
  with no I/O.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `storylet-selection` (spec-storylet-selection.md)

- [ ] **NR3.11 Selection filters and fire chance.** *Depends:* NR3.10, NR3.5. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Selection/SelectionTypes.cs` (new), `SelectionFilters.cs` (new), `FireChance.cs`
  (new), `tests/FusionRpg.Core.Tests/Narrative/Selection/SelectionFilterTests.cs` (new), `tests/fixtures/narrative/selection/` (new).
  *Accept:* every permutation of the five filters leaves the same survivors; cooldowns count on the host clock (seen at
  turn 10 with a 10-turn cooldown: absent at 19, present at 20; wall time has no input); repeat scopes per host follow
  spec §3's table; pity `n` is derived from the last `storylet.seen` at the site, rises one per quiet pulse, resets after
  a fire, reaches 1000 at `n = 190` with `50/5` and the `min` holds it (commented as a bounded ratio); a `1000/0` host
  always fires.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.12 The selection procedure.** *Depends:* NR3.11. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Selection/StoryletSelector.cs` (new), `tests/FusionRpg.Core.Tests/Narrative/Selection/StoryletSelectorTests.cs`
  (new), `tests/FusionRpg.Guard.Tests/StoryletEngineSingleSourceTests.cs` (extended to `*Selector`), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* a spine beat pre-empts priority, which pre-empts the pool, at most one spine beat per pulse; link 2 is
  priority only after link 1's `storylet.seen`, in both room/pulse orders; a flag-required storylet is priority, one
  with the flag under an `Or` is not; a storylet teaching a mechanic with no `mechanic.first-seen` is priority, and
  after the fact it is not; `Teaches` is read nowhere else (a reference scan); the weight is computed in `long`,
  `checked`, divided once, and its bound computed from the loaded tuning, never a literal; unplayed first, pool reset
  keeps cooldowns; dense empty pool throws naming the emptying filter, and fairness yields and records
  `fairnessYielded`; sparse empty pool is `Quiet`; a `Dormant`/`Frozen` world returns `Quiet` and derives no stream;
  the same request selects the same storylet twice.
  *Registry row:* `ns-no-per-host-selection` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `python scripts\audit-overflow.py`.

### `scene-script-loader` (spec-scene-script-loader.md)

- [ ] **NR3.13 Scene catalog: spine chapters and line scenes.** *Depends:* NR2.15, NR3.1; narrative-seed
  `narrative-contract` spine schema (fixtures until then). *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Scenes/SceneScriptCatalog.cs` (new), `tests/FusionRpg.Core.Tests/Narrative/Scenes/SceneScriptCatalogTests.cs` (new).
  *Accept:* zero beats, over-cap beats (cap read from `story-scene-ui.v1.json`, never a literal) and an empty line reject
  in `assertSceneScript`'s wording class; an unknown character, a bad token, an undeclared speaker and
  `sceneId = rift-prologue` reject; `LineScene` builds a one-beat scene with id `line.<body>.<context>.<band>`;
  `teaches` maps to `teaching` on the last beat only, from the registry's authored sentence.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.14 Story scene routes and acknowledgement.** *Depends:* NR3.13, NR3.10, NR2.12. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/StoryEndpoints.cs` (new), `src/FusionRpg.Contracts/StorySceneDtos.cs` (new),
  `tests/FusionRpg.Server.Tests/Narrative/StorySceneRoutesTests.cs` (new).
  *Accept:* rows carry exactly `{storyId, version, state, eligible}`; eligibility is a `StoryFlagSet` leaf on
  `flag:scene.due.{sceneId}` (or the spine rule) and no `scene.acknowledged` at the revision; a new revision is eligible
  again; the first ack appends one fact, a repeat with the same outcome is `ok` with none, a different outcome is `409`;
  acknowledging (or skipping) a teaching scene appends one `mechanic.first-seen` per value, a second ack none; a line
  scene's ack source is per return; `rift-prologue` never appears on these routes and its route is unchanged.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR3.15 The reviewed story-scene widening.** *Depends:* NR3.14; story-scene review; ask A2. *Agent:* implementer.
  *Files:* `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts` (`SceneId` a string, speaker union),
  `actorCast.ts` (antagonist lead member, cast speakers), `gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx`
  (optional `renderBeat`, `acknowledge`, chrome props with today's defaults), `docs/architecture/story-scene-map.md`
  (R2 pointer on the out-of-scope row).
  *Accept:* every existing story-scene and Sanctum test passes with the defaults; the antagonist member id is A2's
  answer or its default; a data scene can pass `useNarrativeText` and an injected `acknowledge`.
  *Verify:* `cd gk-web/web/fusion-rpg-web; npx vitest run src/features/story-scene src/ui/story-scene src/stages/sanctum; npm run build`;
  `.\scripts\verify-change.ps1 -Paths @('docs/architecture/story-scene-map.md') -Session <sid>`.

- [ ] **NR3.16 Web scene loader, Sanctum rows and the scene-rows cache.** *Depends:* NR3.15. *Agent:* implementer.
  *Files:* `web/fusion-rpg-web/src/features/narrative/scenes/useStoryScenes.ts` (new), `toSceneScript.ts` (new),
  `gk-web/web/fusion-rpg-web/src/lib/bus/keys.ts` and `invalidate.ts` (`storyScenes` key and triggers; shared with lane D3:
  region check), `gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx`, `gk-core/scripts/enforcement-registry.v1.json`,
  `docs/architecture/decisions.md` (the S3 split row drafted in `narrative-seed-map.md`; clean-or-skip).
  *Accept:* a fixture DTO becomes a `SceneScript` that passes `assertSceneScript` and plays in the host with rendered
  tokens and the injected `acknowledge`; a row the server marks `eligible: false` never plays whatever `when` returns;
  one test per trigger — profile switch, ack success, each outing-return event kind (delve close, collect, world turn
  commit), SignalR reconnect, the `scene.play` hook — asserts the rows refetch; a web test finds `StorySceneHost` the
  only component rendering beats (`features/narrative/scenes` imports it).
  *Registry row:* `ns-one-scene-player` → `["narrative"]`.
  *Verify:* `cd gk-web/web/fusion-rpg-web; npx vitest run src/features/narrative/scenes src/features/story-scene src/ui/story-scene src/lib/bus; npm run extract; npm run build; npm run check:bundle`;
  `.\scripts\verify-change.ps1 -Paths @('gk-core/scripts/enforcement-registry.v1.json','docs/architecture/decisions.md') -Session <sid>`.
  **Full suite (point 2):** the module crosses Core, Server and web.

### Checkpoint 3 — cast and select (after NR3.16)
- [ ] Casting, predicates, selection and scenes pass over fixture corpora with the game closed; the Rift prologue is unchanged.

---

## Phase 4 — Wave 3

### `choice-resolution` (spec-choice-resolution.md)

- [ ] **NR4.1 The resolver: eligibility, odds, contests, prices, fight handoffs.** *Depends:* NR3.12, NR2.18. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Choices/ChoiceResolver.cs` (new: `Present`, `Resolve`, `ResolveFromViews`,
  `OddsFor`), `ChoiceContext.cs` (new), `ChoiceResolution.cs` (new), `EventDeckPreflight.cs` (`choice.fight-host-has-no-battle`),
  `tests/FusionRpg.Core.Tests/Narrative/Choices/ChoiceResolverTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* one fixture choice per kind; each refusal id fires for exactly its missing precondition and the choice is
  shown with its reason; `Resolve`'s threshold **is** `Present`'s `SuccessMilli`, and over 10,000 fixed seeds the success
  share is within a stated tolerance; the contest argument is `BaseDodge(Θa) − BaseDodge(Θc)` (a relation test against
  the battle hit contest at the same gap), 500‰ at parity, non-decreasing in the gap; a relation-only choice uses
  `wild.talk.flatterMilli` and ignores Θ; `offer:souls` prices through `OfferPricing.Souls` and every other stock is
  `choice.offer-unpriced`; `fight` returns a `FightHandoff` and no applied effect; `ResolveFromViews` equals `Resolve`
  on the same views, slot and stream; `leave` resolves to no outcome; no Θ field on any projection; a scan finds no
  `battle:` or `dungeon:quest:` literal in `Narrative/Choices/`. No narrative tuning key added.
  *Registry row:* `ns-choice-stream-literal` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `python scripts\audit-overflow.py`.

- [ ] **NR4.2 `ChoiceAnswerService`: the idempotent answer.** *Depends:* NR4.1, NR2.10. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/ChoiceAnswerService.cs` (new), `RpgStore.StoryLedger.cs` (the reviewed
  attribute additions: `choice.picked` gains `thetaActor`, `thetaContent`, `rolledMilli`; `storylet.seen` gains the
  offer's `slotKey`, `revision`, `pinKey`, cast), `tests/FusionRpg.Server.Tests/Narrative/ChoiceAnswerServiceTests.cs` (new).
  *Accept:* a second answer to one offer returns the identical resolution and leaves one fact; a live revision that
  moved refuses `choice.revision-moved`, an arc link resolves from its pin in both orders of pin write and corpus bump;
  answering a teaching storylet (any choice, `leave` included) appends `mechanic.first-seen` in the same transaction;
  legacy rows are never answered here.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `quest-sources` (spec-quest-sources.md)

- [ ] **NR4.3 One quest catalog widened; the objective registry.** *Depends:* NR2.9; narrative-seed `quest-vocab`
  (fixtures until then). *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Core/Delve/Quests/QuestCatalog.cs` (the three changes of `spec-quest-vocab.md` §1),
  `src/FusionRpg.Core/Narrative/Quests/QuestObjectiveRegistry.cs` (new), `src/FusionRpg.Core/Narrative/Quests/NarrativeQuestAnchor.cs`
  (new: the seed → `QuestRow` mapping of `spec-quest-vocab.md` §3.1), `tests/FusionRpg.Core.Tests/Narrative/Quests/QuestObjectiveRegistryTests.cs`
  (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* `save`/`world` scopes load through the one catalog; a registry row whose sources are only `[pvz]` refuses
  `quest.objective-lawn-only`, and every template has a standalone source; `gk-core/tests/FusionRpg.Core.Tests/Delve/Quests/`
  passes unchanged.
  *Registry row:* `ns-quest-no-lawn-only-objective` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR4.4 Mode-agnostic progress, the reward request, achievement evidence.** *Depends:* NR4.3. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Quests/IQuestFactSource.cs` (new), `NarrativeQuestProgress.cs` (new),
  `QuestRewardSource.cs` (new), `QuestAchievementEvidence.cs` (new), `tests/FusionRpg.Core.Tests/Narrative/Quests/NarrativeQuestProgressTests.cs` (new).
  *Accept:* a `defeat-creatures` quest counts a fixture expedition battle and a fixture world battle alike; the same
  facts in reversed order give the same verdict; a duplicate `(sourceKind, durableId)` counts once; facts before the
  offer never count; counts `long`, `checked`; the reward request carries the anchor's window and names a source kind
  in `DropTableValidator.KnownSourceKinds`; a `quest.completed` fact maps to evidence with `FactId = seq`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR4.5 Quest sources and the lifecycle.** *Depends:* NR4.4. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/QuestSources/QuestSources.cs` (new: battle, world-turn, expedition, delve,
  story, pvz readers over existing store reads), `src/FusionRpg.Server/Narrative/QuestLifecycle.cs` (new: `Offer`,
  `Capture`, `Settle`, `Abandon`, the Delve verdict mirror), `tests/FusionRpg.Server.Tests/Narrative/QuestLifecycleTests.cs` (new).
  *Accept:* a no-expiry world quest keeps its `have` after the fixture trims report bodies past the hot tail (from
  `quest.progressed` facts), and re-capturing a turn adds nothing; a world quest expires at `offeredAt + expiry` full-step
  turns and not before, with no time input; completion beats expiry in one settlement, both arrival orders; abandon
  writes exactly one fact and nothing else; a quest in a hibernating fixture world keeps its `Remaining` through a
  coarse catch-up; settling a completed quest twice yields one `reward.owed`; a mirrored Delve verdict yields one
  `quest.completed` (inert until `CloseDelve` has a production caller, plan §8.2).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `outcome-routing` (spec-outcome-routing.md)

- [ ] **NR4.6 The router and host budgets.** *Depends:* NR4.1, NR4.5, NR3.3, NR3.14. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Outcomes/OutcomeStep.cs` (new), `OutcomeRouter.cs` (new), `IHostBudget.cs` (new),
  `EventDeckPreflight.cs` (`storylet.host-has-no-loot-budget`, `host-effect-unsupported`, `enemy-relation-shift`,
  `recruit-target`), `tests/FusionRpg.Core.Tests/Narrative/Outcomes/OutcomeRouterTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* each consequence kind plans exactly the step of spec §2; `relation.shift` writes a fact of kind `param`
  (a `good` outcome with `param: betrayed` writes `betrayed`), and `param: none` refuses at preflight and at `Plan`; an
  enemy-role subject refuses `outcome.enemy-relation`; a `loot` outcome on the homeworld and on `expedition.return`
  fails preflight; no world or homeworld plan contains `AwardSouls`; `doctrine.setback` plans no executor step; a world
  effect plans a container with a `narrative:` SourceId at `Player`/`Sector`/`Slot` scope.
  *Registry row:* `ns-outcome-host-budget` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `.\scripts\guard-actor-hub.ps1`.

- [ ] **NR4.7 The executor and the owed queue.** *Depends:* NR4.6, NR2.30. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/OutcomeExecutor.cs` (new), `tests/FusionRpg.Server.Tests/Narrative/OutcomeExecutorTests.cs` (new).
  *Accept:* a spy store records exactly one owner call per kind; a plan executed twice leaves one fact, one soul spend,
  one manifest, one transfer; an unaffordable spend rolls back the flag and the quest in the same plan; a fixture world
  turn with two claim lines and three owed payouts mints exactly two rolls under the lines' correlations with the
  payouts' windows, leaves the third owed, the claim mint of that turn mints nothing, the next turn with a line pays the
  third, and the item-roll count equals the line count; the same for collects; replaying either settlement mints
  nothing; a fight's `onWin` runs only after a fixture win report and `onLoss` only after a loss, both orders of
  "report then commit" and "commit then report" settling once; `scene.play` writes one `scene.due` flag and never
  touches `rpg_onboarding_story`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`; `.\scripts\guard-dal.ps1`; `python tools\tuning\resource_ownership.py --check`.

### `quest-log-contract` (spec-quest-log-contract.md)

- [ ] **NR4.8 The quest-log read model and routes.** *Depends:* NR4.5, NR3.3. *Agent:* implementer.
  *Files:* `src/FusionRpg.Contracts/Narrative/QuestLogDto.cs` (new), `src/FusionRpg.Server/Narrative/QuestLogReadModel.cs`
  (new), `src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs` (new: `GET quest-log`, `POST abandon`),
  `tests/FusionRpg.Server.Tests/Narrative/QuestLogReadModelTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* a fixture save returns each section with the right `have/need` and `Remaining`; a world-A quest is absent
  for world B and a save quest present in both; a reflection test fails any property named `Theta*`, `*Seed`,
  `PartyIndex`, `Rung*`, `InstanceId` or `*Id` other than `QuestKey` (the `TokenRefDto.Id` exempt by type), and the
  serialized JSON contains no `StoryFactKind` wire id; a corpus bump leaves an offered quest's `Name` key unchanged;
  only the next unreached chapter is listed; found fragments sort by `SortKey` whatever order they were found in;
  abandon → `200`, again → `409`, a Delve quest → `CanAbandon = false`; a hibernating world's quest reads `paused` and
  a fallen one's `failed`; an enemy-role character shows its faction band.
  *Registry row:* `ns-quest-log-dto-vocabulary` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR4.9 `NarrativeNotify` and the refresh edges.** *Depends:* NR4.8, NR4.7. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/NarrativeNotify.cs` (new), `tests/FusionRpg.Server.Tests/Narrative/NarrativeNotifyTests.cs` (new),
  the call sites in `OutcomeExecutor.cs` and `QuestLifecycle.cs`.
  *Accept:* one test per trigger of spec §4 that exists at this point (1, 2, 4, 5, 6, 7, 9, 10, 11) asserts
  `NarrativeUpdated` after commit through a spy hub, key-set edges included; triggers 3, 8 and 12 are wired and tested
  by the host tasks that own their commit paths (NR5.7, NR5.11, NR5.13, NRX.3), each listed there.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### Checkpoint 4 — a storylet resolves (G3; after NR4.9)
- [ ] With the game closed, a fixture storylet is selected by tier and specificity, a choice answered with shown odds,
  every outcome kind routed through its existing path, rewards taken from the host budget with a dedupe key, the pick
  in the ledger; deterministic on replay.
- [ ] **Full suite (point 1).**

---

## Phase 5 — Wave 4

### `delve-host` (spec-delve-host.md) — map gate G5

- [ ] **NR5.1 `EnterRoom`: legacy and widened in one pool.** *Depends:* NR4.7, NR2.25. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Delve/StoryletHost/DelveStoryletHost.cs` (`EnterRoom`, `DelveRoomStory`),
  `src/FusionRpg.Core/Delve/StoryletHost/DelveHostBudget.cs` (new), `tests/FusionRpg.Core.Tests/Delve/StoryletHost/DelveHostTests.cs` (new).
  *Accept:* for 64 seeds × every event-capable room kind a legacy-only corpus returns `Legacy` byte-equal to NR2.1's
  fixture; a widened `delve.merchant` storylet is offered in a merchant room; link 2 of a fixture arc is drawn in the
  priority tier after link 1's `storylet.seen`, in both room orders; every legacy resolution carries resolvable keys;
  a reflection test finds the Delve route tables unchanged by this module.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.2 Delve residents and the routes' widened branch.** *Depends:* NR5.1, NR3.7. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/DelveResidentCast.cs` (new), `src/FusionRpg.Server/DelveEventEndpoints.cs`
  (enter calls `EnterRoom`; answer routes widened rows through `ChoiceAnswerService` then `OutcomeExecutor`),
  `DelveEndpoints.cs` (`EnsureDomainResidents` on a domain's first delve), `tests/FusionRpg.Server.Tests/Narrative/DelveResidentCastTests.cs` (new).
  *Accept:* a domain's first delve casts `casting.delveResidentsPerRole` residents once on
  `narrative:cast:delve-resident`, save-scoped; a second delve casts none and meets the same `characterId`s; a merchant
  room casts its trader; a cage room with a cast captive yields a widened storylet, one without falls through to the
  shipped wild path whose tests pass unchanged; freeing the captive transfers the same `instanceId`; route signatures unchanged.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `world-events-host` (spec-world-events-host.md) — map gate G4 world half; plan gate PG2

- [ ] **NR5.3 The story seam in `TurnEngine.Step`.** *Depends:* NR4.9, NR2.30, NR2.31. *Agent:* **implementer-hard**.
  *Files:* `src/FusionRpg.Core/World/Turn/IWorldStoryHost.cs` (new), `TurnEngine.cs` (optional `story` parameter;
  `Events` takes revealed commands and the resolver; calls the seam after the calendar roll),
  `tests/FusionRpg.Core.Tests/Narrative/Hosts/WorldStorySeamTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* with `story = null` and with the seam attached over an empty input, every world test and golden is
  byte-identical (hashes listed); the edit is the only change inside `TurnEngine.cs`; reviewed with world-map-program.
  *Registry row:* `ns-world-story-seam-null` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.4 `event.choose` and the typed report kinds.** *Depends:* NR5.3. *Agent:* implementer.
  *Files:* `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs` (`EventChoose`, `OfferRef`, `ChoiceSlot`),
  `WorldCommandAdmission.cs` (the arm), `TurnReport.cs` (`story.offered`, `story.answered`, `story.lapsed`),
  `tests/FusionRpg.Core.Tests/Narrative/Hosts/EventChooseTests.cs` (new), `docs/architecture/decisions.md` (NS8, joint with
  world-map-program; clean-or-skip).
  *Accept:* `offer.missing`, `offer.too-long`, `choice.slot-out-of-range` each fire for their malformed order; a
  well-formed order for a closed offer is admitted (admission never judges reveal legality); the playback rows are
  filed on world-stage (ask A3) in the evidence line.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.5 `WorldStoryPhase`: resolve orders, then fire.** *Depends:* NR5.4. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Hosts/WorldStoryPhase.cs` (new), `WorldStoryInput.cs` (new, canonical),
  `WorldHostBudget.cs` (new), `tests/FusionRpg.Core.Tests/Narrative/Hosts/WorldStoryPhaseTests.cs` (new).
  *Accept:* a storylet at a sector the player neither owns nor saw last turn never fires, the same sector fires once
  owned; the fire roll is reinterpreted as `ulong` before `% 1000` and, over a fixed seed list including negative
  `DeriveRollSeed` values, the fire share tracks `p` (a relation) and rises with `n`; at most one offer per sector and
  one spine beat per turn; the site climate is `sector.Climate` (R20), `null` climate-blind; a legal `event.choose`
  resolves through `ResolveFromViews` on its named stream; a stale order drops with `story.offer-closed` or
  `story.choice-ineligible` and the turn continues; a `fight` produces a `Guard` `BattleRequest` to a spy resolver,
  and a resolver refusal reports the answer without the fight-conditional steps; two orders resolve the same whatever
  the submission order; an unanswered offer lapses after `world.offerLifetimeTurns` with no negative fact.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.6 Persist the story input for replay.** *Depends:* NR5.5. *Agent:* **implementer-hard** (a world turn log column).
  *Files:* `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (`story_input_json TEXT NULL`, written in the same insert
  as `report_json`, never trimmed with the hot tail; replay passes it back; `NULL` replays with `story = null`),
  `tests/FusionRpg.Data.Tests/Narrative/NarrativeWorldCommitTests.cs` (new).
  *Accept:* a committed turn with content replays to the same report and state hash through the store's replay path;
  every turn committed before this change replays unchanged; the hot-tail trim never touches the column; reviewed with
  world-map-program.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','tests/FusionRpg.Data.Tests/Narrative/NarrativeWorldCommitTests.cs') -Session <sid>`.

- [ ] **NR5.7 `NarrativeWorldPass`: settle in the commit; content on (plan gate PG2).** *Depends:* NR5.6, NR4.7, NR4.9.
  *Agent:* **implementer-hard** (`RulesetVersion` and golden re-bless).
  *Files:* `src/FusionRpg.Server/Narrative/NarrativeWorldPass.cs` (new, invoked through a delegate the commit takes),
  `RpgStore.WorldTurns.cs` (the delegate call before the claim pass), `TurnEngine.cs` (`RulesetVersion` per PG2's
  default), `NarrativeWorldCommitTests.cs`, the re-blessed goldens.
  *Accept:* `story.offered` → one world-scope `storylet.seen` carrying the offer; `story.answered` → `choice.picked`
  plus the executed plan with `WorldHostBudget`, loot taking claim lines oldest `seq` first; quests captured and
  settled; `NarrativeNotify` fires (triggers 3 and 8 wired and tested here); re-running the pass adds no fact, loot or
  quest; every moved golden hash listed and re-blessed in this commit under world-map-program review.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.
  **Full suite (point 2):** Core, Data, Server and the world goldens.

- [ ] **NR5.8 Warlords as characters; the open-offers route.** *Depends:* NR5.7, NR3.7. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/WorldCastStep.cs` (warlord casting, home `world-entity:{entityId}`),
  `NarrativeEndpoints.cs` (`GET /api/narrative/{playerId}/offers?worldId=` with `ChoiceView`s),
  `tests/FusionRpg.Server.Tests/Narrative/WarlordCharacterTests.cs` (new).
  *Accept:* a warlord character's specimen is unchanged by any story outcome; no relation fact about it is ever
  written; its defeat writes only a world-scope `flag.set`; the offers DTO carries odds and prices, never Θ. The rule-6
  constraint on world-map's future warlord growth is filed in the evidence line.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `petition-host` (spec-petition-host.md)

- [ ] **NR5.9 Petitions from computed needs.** *Depends:* NR5.7; ask A1. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Hosts/SectorNeeds.cs` (new), `WorldStoryPhase.cs` (petition candidates in the
  phase), `SelectionBounds.cs` (`PetitionsPerTurn = 1`, commented), `EventDeckPreflight.cs` (`petition.no-need-condition`,
  `petition.pays-loam`, `petition.no-resolution-path`), `tests/FusionRpg.Core.Tests/Narrative/Hosts/PetitionTests.cs`
  (new), `gk-core/scripts/enforcement-registry.v1.json`; with A1's default, the `SectorNeedIs` leaf and the leaf-count test (22 → 23).
  *Accept:* a releasing component reads `loam-fading` and a `sustain` that saves it clears it; a `Hazard` slot reads
  `hazard-standing` and `develop.completed` clears it; needs and ownership are read on the post-`Pressure` world, so a
  sector lost or a need met this turn fires nothing; an unheld sector never petitions; with `UniformNeeds` no clan
  request fires, with a fixture vector whose `Market` need is highest one fires; at most one petition per turn across
  the empire; each preflight rule has a red fixture; answering a `loam-fading` petition offers a `hold-sector` quest
  completing after N held turns end to end; no petition plan contains a loam debit; the reward takes a claim line.
  *Registry row:* `ns-petition-no-loam-payment` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `expedition-lead-host` (spec-expedition-lead-host.md) — map gate G4 expedition half

- [ ] **NR5.10 Lead plan on a disjoint stream.** *Depends:* NR4.7, NR2.19. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Hosts/ExpeditionLeadPlan.cs` (new), `EventDeckPreflight.cs` (`expedition.no-fight`,
  `expedition.no-spend`), `tests/FusionRpg.Core.Tests/Narrative/Hosts/ExpeditionLeadPlanTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* the existing expedition hash tests pass with `encounter.* = 0` and `= 1000`, and `ExpeditionResolution` is
  byte-identical in both; rolls use `narrative:expedition:encounter:{t}`; the first eligible non-`leave` choice is
  taken, else `leave`; `fight`, `offer` and `loot` on `expedition.return` fail with their rule ids; the resolver is not edited.
  *Registry row:* `ns-expedition-lead-disjoint-stream` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.11 Seal at dispatch, reveal at collect.** *Depends:* NR5.10, NR3.3. *Agent:* **implementer-hard** (an
  expedition table column).
  *Files:* `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs` (`leads_json` write-once), `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs`
  (`DispatchAsync` seals; `CollectAsync` delivers; `CollectResult.Leads` appended), `src/FusionRpg.Server/Narrative/ExpeditionLeads.cs`
  (new), `tests/FusionRpg.Server.Tests/Narrative/ExpeditionLeadTests.cs` (new).
  *Accept:* a lead sealed at dispatch is revealed unchanged at collect though the ledger gained facts in between (both
  orders specified); a recall at `k` reveals exactly the leads with `tick ≤ k`; a tuning swap that turns a sealed wild
  tick quiet reveals no lead and writes no fact; a retried collect returns no second lead set; a joined tick's lead
  binds the same `instanceId` through NR3.3's adopt variant, a slipped-away tick mints one narrative-owned specimen and
  grants nothing; no expedition answer route exists (reflection); `NarrativeNotify` fires after the collect.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `sanctum-hub-host` (spec-sanctum-hub-host.md) — map gate G4 hub clause

- [ ] **NR5.12 Returns, presence and conversation selection.** *Depends:* NR4.7, NR3.14. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/SanctumReturns.cs` (new), `SanctumHub.cs` (new), `src/FusionRpg.Core/Narrative/Hosts/SanctumHostBudget.cs`
  (new), `SelectionBounds.cs` (`VisitorsPerReturn = 1`), `tests/FusionRpg.Server.Tests/Narrative/SanctumHubTests.cs` (new).
  *Accept:* a closed delve, a committed active-world turn and a collected expedition each make the next entry a return;
  a coarse catch-up is not an outing; one outing then entry and two outings then one entry each give one return; at
  most one conversation per present character; entering again with no outing gives an empty queue; with no hub
  storylet, a `delve.wiped` return makes Hourbloom say its `return-wiped` line, `sector.lost` plus an extraction picks
  the most serious, a `wary` companion falls back to `greet`; an enemy-role character is never present; `offer:{stock}`
  on `sanctum.hub` fails `sanctum.no-spend`; no hub plan holds a loot or soul step.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.13 The Sanctum entry route and stage.** *Depends:* NR5.12, NR3.16. *Agent:* implementer.
  *Files:* `NarrativeEndpoints.cs` (`POST .../sanctum/enter`, conversation answer), `gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx`,
  the stage's test.
  *Accept:* two `enter` calls for one return give the same queue minus acknowledged entries; a skipped hub scene is
  spent for that return; with the Rift prologue eligible, hub rows are evaluated after it through `isSceneEligible`;
  with a layer open nothing plays; with a lawn run in progress (no match record) no return is recorded; trigger 11
  (`sanctum.returned`) of the quest log is tested here. The "first character met" slot is filed on
  `spec-first-session-progression.md` in the evidence line.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs',<server test>) -Session <sid>`; `cd gk-web/web/fusion-rpg-web; npx vitest run src/stages/sanctum src/features/story-scene; npm run build`.

### `spine-progress` (spec-spine-progress.md)

- [ ] **NR5.14 Spine catalog and due beats.** *Depends:* NR3.13, NR3.12; narrative-seed `arc-shapes` spine frame (fixtures until then). *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Spine/SpineCatalog.cs` (new), `SpineBeats.cs` (new), `IWorldOutcomeSource.cs`
  (new seam), `tests/FusionRpg.Core.Tests/Narrative/Spine/SpineProgressTests.cs` (new).
  *Accept:* ordinals derive from the `after` chain, never from the seed; a broken or cyclic chain and two chapters on
  one `pieceId` refuse; with piece 1 and chapter 1 reached, chapter 2 is due, and not without chapter 1; a due spine scene
  pre-empts a priority storylet at the hub; two due scenes never play on one pulse; with every fixture chapter reached a
  pool storylet is still offered at every host (no ceiling); no test counts the committed spine.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.15 Pieces, chapters and fragments.** *Depends:* NR5.14. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/SpineProgress.cs` (new), `tests/FusionRpg.Server.Tests/Narrative/SpineProgressStoreTests.cs` (new).
  *Accept:* a fixture win appends one `flag:spine.piece.{k}` with `k` read and appended in one transaction; re-reading
  the same win appends none; two wins give ordinals 1 and 2 whichever is read first (the count order-independent;
  ordinals follow append order, as stated); a won then fallen world keeps its piece; acknowledging or skipping the last
  scene writes one `chapter.reached`; a fragment is ineligible before its chapter and eligible after; three fragments
  found in reverse list sorted. Production wins arrive with NRX.2.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `failure-branches` (spec-failure-branches.md)

- [ ] **NR5.16 Failure facts and the no-second-penalty preflight.** *Depends:* NR5.7. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Failure/FailureFacts.cs` (new), `NarrativeWorldPass.cs` (calls it),
  `EventDeckPreflight.cs` (`failure.takes-back`, `failure.no-way-back`, `failure.enemy-personal`),
  `tests/FusionRpg.Core.Tests/Narrative/Failure/FailureFactsTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* `loam.lost:S` on a player sector writes one `sector.lost` with cause `fade`; `district:S:CoreTaken` writes
  `siege.failed` and `sector.lost` with cause `conquest`; the same change with a `cede` order writes nothing; replaying
  the pass writes nothing more; a failure-eligible storylet is priority inside `failure.priorityWindow` and pool after;
  after the player re-holds S its branch is ineligible; a world-A loss is invisible to world B; each preflight rule has a
  red fixture, and a green branch's plans hold no negative resource step or roster removal; a warlord cast into a
  speaking role fails `failure.enemy-personal`, a faction voice reading `byFactionId` passes.
  *Registry rows:* `ns-failure-no-second-penalty`, `ns-failure-enemy-personal` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR5.17 The delve failure scan.** *Depends:* NR5.16, NR5.12. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/FailureScan.cs` (new; called at Sanctum entry and delve room entry),
  `tests/FusionRpg.Server.Tests/Narrative/FailureScanTests.cs` (new).
  *Accept:* a fixture delve closed `Wiped` writes one `delve.wiped` at the next scan, an `Extracted` delve none;
  scanning before and after a second delve closes gives the same total (order-independent); a wipe is visible across
  worlds. Live wipes appear once party-dungeon's `CloseDelve` has a production caller (plan §8.2).
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### Checkpoint 5 — places play (G4, G5; after NR5.17)
- [ ] G4: a player claim mints once and a world payout takes a line; the world host fires fog-correct and an
  `event.choose` resolves at End Turn; goldens byte-identical with no eligible storylet, moved ones re-blessed under
  review; an expedition lead arrives in a collect summary with tier hashes unchanged; a hub conversation plays once per
  character per return.
- [ ] **Full suite (point 3)**, then NR-LP2.

- [ ] **NR-LP2 Live probe: the Delve plays with people; the world turn tells a story.** *Depends:* Checkpoint 5's
  full suite. *Agent:* test-engineer or the implementing session.
  *Files:* `tasks/evidence-fragments/NR-LP2.md` (new).
  *Do (RPG Server scope only):* server started as its own process. **G5:** a real player starts a real delve through
  `POST /api/delve/start`; enters a merchant room through `POST /api/delve/rooms/{id}/enter`; reads the room back
  through `GET /api/delve/{id}` (its event id) and reads the cast trader and `storylet.seen` back through
  `GET /api/narrative/{playerId}/quest-log`. **World:** a real world created through the web's own creation route;
  a real claim command and End Turn through the real world routes; the report (with its `claim.loot:` line) read back
  through `GET /api/world/{playerId}`; the minted items read back through the inventory route the web uses; a
  `story.offered` entry answered with a real `event.choose` next turn and the result read back through the quest log.
  **Expedition:** the shortest real tier dispatched and collected after its real duration, or reported "not probed" —
  never a fabricated collect.
  *Accept:* as NR-LP1: real subjects, real routes, read-back through the normal query path, no `debug.*`, no
  hand-inserted row, each call's scope stated, the Injector half not claimed, any unprobed half named.

---

## Phase 6 — Wave 5

### `counter-doctrine` (spec-counter-doctrine.md) — map gate G6; plan gate PG2

- [x] **NR6.1 The doctrine catalog and view.** *Depends:* NR1.3. *Agent:* implementer.
  *Done (npc-story-events-2, 2026-09-23):* the reviewed vocabulary is authored in
  `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` — six `ward.{element}` (one per shipped element, each biasing
  toward the element that resists it) plus `siegecraft` and `raiders` — and `DoctrinesCatalog` pins that closed set
  (`ReviewedIds`, with the reason in the doc), refusing an id outside it, a duplicate and a row that changes nothing.
  `DoctrineView` exposes exactly `DoctrineId` + the two per-mille maps (a reflection test asserts the member set and
  that no member name carries Hp/Attack/Damage/Rarity), with unnamed elements/order kinds reading the neutral 1000.
  The file's SHAPE and its key closure live in the ONE reader (`Vocabulary/DoctrineCatalog.cs`, extended here — see
  the evidence's named deviation): a row key outside `description`/`negative`/the two effect families refuses
  `doctrine.magnitude-key`, the families key against the shipped element table's six ids and `WorldCommandKinds.All`,
  and a duplicate key is now refused instead of letting the last value win. Printed readings:
  `DoctrineCatalogTests` 14/14; the `core.narrative` selector 118/118; `guard-narrative.py`
  `5 row(s) guarded by 'narrative', 5 mapped` with `-RunTraitFilter` selecting 67 Core + 5 Guard tests, 0 failed;
  `EnforcementRegistryGuardTests` 18/18; `guard-verification-boundaries` `VERIFICATION BOUNDARY GUARD OK`;
  `verify-change` exit 0 with all seven paths resolving FOCUSED and 136 passed / 0 failed; audits 0 high / 0 critical.
  One stale assertion from NR1.3 was fixed in this commit (it pinned the committed file as empty; the file is an
  authored registry, so the emptiness was that ship's state — the shape property moved to an in-memory empty list).
  *Verify deviation:* `-Session <sid>` cannot resolve in this lane; run as `-AllowUnscoped`. `DoctrineView.For(world,
  factionId)` waits on the faction's own doctrine field (adoption is the study bar's row). Evidence:
  `tasks/reports/npc-story-events-2-nr61-evidence-20260923.md`.
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (the authored rows: six `ward.{element}`, `siegecraft`,
  `raiders`), `gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrinesCatalog.cs` (new), `DoctrineView.cs` (new),
  `gk-core/tests/FusionRpg.Core.Tests/Narrative/Doctrine/DoctrineCatalogTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* the vocabulary is closed and pinned with its reason; a row with any key other than
  `speciesElementBiasMilli.{element}` or `orderWeightMilli.{orderKind}` refuses `doctrine.magnitude-key`; `DoctrineView`
  exposes only biases and weights.
  *Registry row:* `ns6-doctrine-no-magnitude` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [x] **NR6.2 The fog-correct reading (R18).** *Depends:* NR6.1. *Agent:* implementer.
  *Done (npc-story-events-2, 2026-09-23):* `DoctrineReading.Of(world, turnBattles, antagonistFactionId, playerFactionId)`
  reads exactly two observation sources and nothing else — his faction's latest observation (`LastSeenTurn ==
  turn − 1`, one turn late because the study step runs in `Events` before `Intel`) and this turn's battle entries he
  took part in or saw, whose sides come from `BattleKinds.IdFor`'s id shape. The winner is never read, an enemy
  identity is never read, no character is read; `Exact` forces count (a glimpse records only a strength band) and
  members are read from the entity as it stands. Shares are per family (elements over observed members, posture over
  observed legions, ground over observed player-held sector slots) and a **lean** is the top share at or above the
  SHIPPED threshold (400‰, from `NarrativeTuningHub`) and strictly above every other — so a 300/300 tie is no lean and
  an empty observed set is no lean. The output is aggregate-only and a guard scans its own file for any per-entity
  member, with a planted falsifier. Printed readings: `DoctrineReadingTests` 12/12; `NarrativeDoctrineReadingGuardTests`
  + `EnforcementRegistryGuardTests` 22/22; `guard-narrative.py` `6 row(s) guarded by 'narrative', 6 mapped`;
  `-RunTraitFilter` selects 79 Core + 9 Guard tests, 0 failed (67/5 before); `guard-verification-boundaries`
  `VERIFICATION BOUNDARY GUARD OK`; `verify-change` exit 0 with every path focused and **153 passed, 0 failed**.
  *Verify deviation:* `-Session <sid>` cannot resolve in this lane; run as `-AllowUnscoped`. *Named dependency:*
  nothing stores a doctrine yet, so NR6.3 (the study bar as hashed faction state) is this reading's first production
  caller. Evidence: `tasks/reports/npc-story-events-2-nr62-evidence-20260923.md`.
  *Files:* `gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrineReading.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Narrative/Doctrine/DoctrineReadingTests.cs`
  (new), `gk-core/tests/FusionRpg.Guard.Tests/NarrativeDoctrineReadingGuardTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* 60% observed fire members read `element:fire`; 30% fire and 30% ice read no lean; a fire lean kept off his
  `Exact` observation and out of every battle he fought or saw reads no lean, the same lean on observed ground does, a
  glimpsed force adds nothing, a battle he fought out of sight counts; nothing observed is no lean; a reflection test
  pins `DoctrineReading.Of`'s parameters to world state, this turn's battle entries and two faction ids; two worlds
  differing only in battle winners, or in which antagonist entity fought, read identically, and identically to a world
  where he saw the same forces without a battle.
  *Registry row:* `ns6-reading-aggregate-only` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR6.3 The study bar as hashed faction state (plan gate PG2).** *Depends:* NR6.2, NR5.7, NR2.32 (or its
  recorded wait). *Agent:* **implementer-hard**.
  *Files:* `gk-core/src/FusionRpg.Core/World/WorldState.cs` (`WorldFaction.Doctrine`), `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs`,
  `src/FusionRpg.Core/Narrative/Doctrine/DoctrineStudy.cs` (new; called from `WorldStoryPhase`), `TurnReport.cs`
  (`doctrine.studying`, `doctrine.adopted`, `doctrine.ended`), `tests/FusionRpg.Core.Tests/Narrative/Doctrine/DoctrineTests.cs`
  (new), `docs/architecture/decisions.md` (NS6; clean-or-skip).
  *Accept:* with the field null every world hashes as before (goldens byte-identical, listed); eight turns of a held
  observed fire lean fill the bar, a switch to ice on turn 5 resets it, no lean holds it at zero; a full bar adopts
  `ward.fire` with its window and cooldown and no second doctrine lands during the cooldown; a lost and a won player
  battle against the antagonist give the same `StudyMilli` as no battle; a won raid lowers `StudyMilli` by the tuned
  amount, never below 0, and a lost raid changes nothing; a hibernating fixture world keeps `DoctrineState`
  byte-identical; the same command log replays to the same state and hash; the `min(1000, …)` is commented as a
  progress ratio; the playback rows and the consumption asks (A3, A4) filed; any moved golden re-blessed under PG2.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.
  **Full suite (point 2):** hashed world state across Core and the world goldens.

- [ ] **NR6.4 The voice and "never how strong".** *Depends:* NR6.3, NR3.14. *Agent:* implementer.
  *Files:* `NarrativeWorldPass.cs` (adoption writes `scene.due.doctrine.{id}`), `SceneScriptCatalog.cs`
  (`doctrine.scene-personal`), `tests/FusionRpg.Core.Tests/Narrative/Doctrine/DoctrineSameRungTests.cs` (new),
  `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* adoption writes one flag; a doctrine scene fixture naming a battle, an antagonist character fact or a
  warlord fails the loader; for the same species and Θ every fixture unit's magnitude is identical with and without
  the doctrine; over a fixed seed list the doctrined draw's threat-rung and rarity histogram equals the undoctrined one.
  *Registry row:* `ns6-doctrine-same-rung` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR6.5 R13 guards, rules 4–6.** *Depends:* NR6.3. *Agent:* implementer.
  *Files:* `tests/FusionRpg.Guard.Tests/NarrativeAntiNemesisTests.cs` (new: `NarrativeNoTraitBaseTests`,
  `NarrativeNoNetworkTests`, `NarrativeNoWarlordWriteTests`), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* each scan fails an in-memory probe source and passes on the tree: no `Narrative` type references
  structure, district-layout or siege-construction types; no file under `gk-core/src/FusionRpg.Core/Narrative/**` or
  `gk-core/src/FusionRpg.Server/Narrative/**` references `HttpClient`, sockets or an upload API; no narrative code writes a
  `Warlord` entity's level, members or lairs.
  *Registry rows:* `ns6-no-trait-base`, `ns6-warlord-world-rules-only` → `["narrative"]`; `ns6-no-enemy-data-sharing`
  changes from its `unguardableReason` (NR3.4) to `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

### `narrative-readings` (spec-narrative-readings.md)

- [ ] **NR6.6 Reading computations.** *Depends:* NR4.2. *Agent:* implementer.
  *Files:* `src/FusionRpg.Core/Narrative/Readings/NarrativeReadings.cs` (new), `src/FusionRpg.Contracts/Narrative/NarrativeReadingsDto.cs`
  (new), `tests/FusionRpg.Core.Tests/Narrative/Readings/NarrativeReadingsTests.cs` (new), `gk-core/scripts/enforcement-registry.v1.json`.
  *Accept:* 3 of 30 answers on slot 1 give 100‰ and no flag; 1 in 30 flags `nobody`; 28 of 30 on a non-`leave` slot flags
  `everybody`, on `leave` `leave-dominant`; below `readings.minAnswers` the rate is null; sightings at ticks 3 and 11
  give distance 8; a pool of 12 at 250‰ per tick reports 48; shuffled facts give the same report; the hourly figure is
  labelled an audit-clock estimate; a reference scan finds `NarrativeReadings` used only by the endpoint and tests; no
  test runs over the committed corpus or a real save.
  *Registry row:* `ns-readings-no-decision-reader` → `["narrative"]`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR6.7 The readings route and script.** *Depends:* NR6.6. *Agent:* implementer.
  *Files:* `NarrativeEndpoints.cs` (`GET /api/narrative/{playerId}/readings`, a developer surface outside game
  navigation), `scripts/narrative-readings.ps1` (new), its test, `gk-core/scripts/verification-boundaries.v1.json` (only if
  NR0.2 deferred the script row).
  *Accept:* the route is read-only and binds to the local server; the script writes
  `docs/research/narrative/_readings-<yyyymmdd>-<playerId>.json` and prints a table; nothing is uploaded; whether a
  report is committed is the owner's call.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs','scripts/narrative-readings.ps1',<its test>) -Session <sid>`.

### Checkpoint 6 — doctrine and program close (G6; after NR6.7)
- [ ] G6: an observed lean advances the bar and a hidden one does not; a doctrine changes draws and weights, never a
  magnitude; the six anti-Nemesis rules each have a row, all green.
- [ ] Every row of plan §4 D3 is in the registry with its guard or reason; `guard-narrative.py` green.
- [ ] G7 recorded as blocked on `/idea-ui` (Phase 7).
- [ ] **Full suite (point 1).**

---

## Phase 7 — Wave 6 (two `/idea-ui` entry tasks; the build tasks follow their ideals)

Two surfaces, two modules, two ideals (`docs/architecture/idea-ui-phase.md` §1 "module unit of work"; map rows 26 and 27).
Each row below is an **idea-phase entry task**: it produces an ideal doc and stops. **No build task exists until each ideal
is accepted and its `/idea-ui` gate (map gate G7) is recorded** — the build tasks are written by a later `/spec`/`/plan`
pass against the accepted ideals, exactly as `condition-glance`, `achievement-title` and `notify-centre` did.

- [ ] **NR7.1 `/idea-ui` pass over `storylet-card` (map row 26).** *Depends:* NR5.8 (the offers route) — the pass designs
  against real DTOs; *Agent:* implementer (the deliverable is a document, no product code).
  *Files:* `docs/architecture/storylet-card-ideal.md` (new); `docs/architecture/gui-lego/menu-refactor-queue.md` (one row,
  if the surface enters the refactor stream); `tasks/evidence-fragments/NR7.md` (new).
  *Do:* read and follow `docs/architecture/idea-ui-phase.md` in that session — it is binding; the skill entry is
  `.claude/skills/idea-ui/SKILL.md`. Design the band-2 storylet card that generalizes the Delve's `EventPanel`
  (`gk-web/web/fusion-rpg-web/src/stages/delve/layers/EventPanel.tsx`), and resolve the stale placeholder comment the map's
  *Conflicts* item 3 names.
  *Accept:* the ideal doc carries every section `idea-ui-phase.md` §5 requires — which loop it extends (named from
  `docs/guide/the-loops.md`); the load-bearing principles restated **inline**, not linked; what this is, in player
  language; the four-bucket inventory (**built / wiring gap / real gap / built-defective**) with `file:line` and what
  proves each; the module breakdown of the surface (one row per piece: `pieceId`, reused or new) plus the shared reuse
  map; prior art with numbers and failure modes and sources; **the shape** (chosen vs rejected, and the rejection of
  "one CSS pass / one god TSX"); the tunables with the catalog or theme-pack file that owns each; what it deliberately
  does not decide; and open questions for the owner only. It reads `DelveEventDto`, the NR5.8 offers route and
  `ChoiceView` rather than inventing a contract, and it names every reused piece from `docs/design/gui-lego/` before
  proposing a new one.
  *Questions the pass must put to the owner* (not answered here — the pass does the inventory first and may withdraw
  any that the code answers): where the card mounts for each host (Delve, world, petition, expedition) and whether that
  is one recipe with host binds or one recipe per host; whether a choice's odds and costs are shown by default or on
  inspect; whether the card replaces or sits beside the existing `EventPanel`; and which of the surface's strings belong
  in the lingui catalog versus the narrative-text renderer.
  *Verify:* `python scripts/audit-doc-citations.py --scope docs/architecture --strict` reports no HIGH finding for
  `storylet-card-ideal.md`; `.\scripts\verify-change.ps1 -Paths @('docs/architecture/storylet-card-ideal.md') -Session <sid>` (docs paths map to
  `docs-and-assistant-config`). **No reference to the web surface is passed to `verify-change.ps1`** — `web/**` has no
  verification lane (plan §4 D2).
  *Commit:* `npc-story-events NR7.1: the storylet card ideal`.

- [ ] **NR7.2 `/idea-ui` pass over `quest-log-layer` (map row 27).** *Depends:* NR4.8 (`QuestLogDto`), NR4.9
  (`NarrativeUpdated`). *Agent:* implementer (the deliverable is a document, no product code).
  *Files:* `docs/architecture/quest-log-layer-ideal.md` (new); `docs/design/gui-lego/recipes/*.json` (only if the pass
  finds an existing recipe fits and records the binds); `tasks/evidence-fragments/NR7.md`.
  *Do:* the same binding procedure as NR7.1, for the quest log as a layer openable from any stage: quests, cast met, the
  story so far.
  *Accept:* the same `idea-ui-phase.md` §5 section list; the inventory cites the real `QuestLogDto` and the
  `NarrativeUpdated` push path rather than a guessed payload; the doc names the host recipe and the layers it must not
  fork (GG-1 — a layer over the current stage, never a new route); every piece is either an existing `docs/design/gui-lego/`
  piece or a new `pieceId` with its contract; the tunables name their catalog file; open questions for the owner only.
  *Questions the pass must put to the owner* (same rule): what the log does at first open with no quest history; whether
  "cast met" is a tab of this layer or a separate surface; and how much of the story-so-far is summary text versus links
  back into the scene logs.
  *Verify:* `python scripts/audit-doc-citations.py --scope docs/architecture --strict` reports no HIGH finding for
  `quest-log-layer-ideal.md`; `.\scripts\verify-change.ps1 -Paths @('docs/architecture/quest-log-layer-ideal.md') -Session <sid>`.
  *Commit:* `npc-story-events NR7.2: the quest log layer ideal`.

- [ ] **NR7.3 The two `/idea-ui` gate records (map gate G7, plan §6).** *Depends:* NR7.1, NR7.2. *Agent:* the
  implementing session.
  *Files:* `docs/architecture/npc-story-events-map.md` (the G7 row and the two module rows), this file.
  *Accept:* G7's row records, per surface, that its ideal is accepted and its band/engine-vocabulary check passed; the
  map's rows 26 and 27 point at the ideals and at the `/spec` pass that follows; the todo's Phase 7 gains the build tasks
  (or states that they are still to be written) — **no build task is ticked here**. If either ideal is rejected, G7 stays
  open and this row says so.
  *Verify:* `python scripts/audit-doc-citations.py --scope docs/architecture --strict`; then
  `.\scripts\verify-change.ps1 -Paths @('docs/architecture/npc-story-events-map.md','tasks/npc-story-events-todo.md') -Session <sid>`.
  *Commit:* `npc-story-events NR7.3: the idea-ui gate records for wave 6`.

No build task is written until each surface passes its `/idea-ui` gate (map gate G7). The build tasks, when they come,
are written by a `/spec` + `/plan` pass against the accepted ideals — not by extending this phase from the map rows alone.

---

## Phase X — follow-ups that wait on another program's module

- [ ] **NRX.1 The production world-phase reader.** *Depends:* world-continuity `world-state-vocabulary`. *Agent:* implementer.
  *Files:* `RpgStore.StoryLedger.cs` (`WorldNarrativePhaseOf` reads `state` and `outcome`), `StoryLedgerStoreTests.cs`.
  *Accept:* every lifecycle test of NR2.9, NR2.14, NR3.3, NR3.5, NR3.12 and NR4.5 passes against real `rpg_worlds`
  rows in each state instead of the fixture reader; no other file reads world state for the phase.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs','tests/FusionRpg.Data.Tests/Narrative/StoryLedgerStoreTests.cs') -Session <sid>`.

- [ ] **NRX.2 The production `IWorldOutcomeSource`.** *Depends:* world-continuity `world-victory`. *Agent:* implementer.
  *Files:* `src/FusionRpg.Server/Narrative/WorldOutcomeSource.cs` (new, over `rpg_world_won_facts`), `SpineProgress.cs`,
  `SpineProgressStoreTests.cs`.
  *Accept:* a real won-world fact appends one piece; a fall never fires the win edge; re-reading appends nothing.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NRX.3 The fall edge: quests fail by fall; coarse-step losses open branches.** *Depends:* world-continuity
  `world-fall` (and its per-loss digest record shape). *Agent:* implementer.
  *Files:* `QuestLifecycle.cs` (one `quest.failed {cause: world-fallen}` per open world quest at the fall),
  `FailureScan.cs` (reads the digest facts), `NarrativeNotify.cs` (trigger 12), their tests.
  *Accept:* a fixture fall closes every open world quest with one fact and no other cost; nothing is deleted; a
  coarse-step loss digest writes `sector.lost` by the same read-not-hook rule; trigger 12 raises `NarrativeUpdated`.
  *Verify:* `.\scripts\verify-change.ps1 -Paths @(<the files above>) -Session <sid>`.

- [ ] **NR-F1 · `docs/DESIGN-GATE.md` §1's topic index has no narrative row** · S · *(filed by lane `npc-story-events-1`
  at NR1.1, 2026-09-22.)* §1 is the gate's entry point — "find the row for what you are about to touch" — and it
  indexes combat-ai, world-map, effects, items, actions and the GUI streams, but nothing for this program's 28 specs,
  so a session about to touch narrative vocabulary has no row to find and no reason to read
  `spec-narrative-vocabulary.md` before proposing. The counts this program now owns (`HostClockKind` 4,
  `StoryFactKind` 27, the 16 host kinds, the structural bounds) are the closed-vocabulary kind §1 tracks for other
  programs. Owning program is unclear — `docs/DESIGN-GATE.md` is repo-level, not this program's — so this row is the
  finding and the manager routes it (candidate: the standards/design-gate stream).
  *Accept:* §1 gains a narrative row naming this program's closed vocabularies with their counts, their spec files
  and the "widening one is a reviewed change" rule; or the manager records that the gate indexes a subsystem only
  once it is built, and this row is withdrawn.

- [ ] **NR-F2 · the voices registry file has two names across the two specs** · S · *(filed by lane
  `npc-story-events-1` at NR1.3, 2026-09-22.)* This program's spec calls it `voice-registers.v1.json`
  (`docs/architecture/npc-story-events/spec-narrative-vocabulary.md` §1 table, row `VoiceRegisterCatalog`),
  while the program that AUTHORS it calls it `voices.v1.json`
  (`docs/architecture/narrative-seed/spec-character-vocab.md` §4 and its Project structure) — one
  vocabulary, two committed file names, so whichever side lands first decides what the other must read. The
  runtime reader now reads `voices.v1.json` (the authoring side's name) with the key `voices`, and
  `NarrativeRegistryHub.VoicesFile` carries the discrepancy in a comment. Owning program: **narrative-seed**
  (its todo is outside this lane's fence, so the row is filed here and the manager routes it).
  *Accept:* one name is chosen and the other spec's text is re-anchored (or both sides state the alias
  explicitly); `NarrativeRegistryHub.VoicesFile` and the seed's Project structure agree, and the NR1.3
  evidence line's note is replaced by the ruling.

- [ ] **NR-F3 · `audit-magic-numbers.py --domain narrative` is a vacuous filter** · S · *(filed by lane
  `npc-story-events-1` at NR1.4, 2026-09-22.)* `gk-core/scripts/audit-magic-numbers.py:214-221` (`domain_of`)
  recognises 18 subsystem keys and has none for `Narrative`; a path under `gk-core/src/FusionRpg.Core/Narrative/**`
  falls through to `os.path.basename(os.path.dirname(path)).lower()` — `vocabulary` — so `--domain narrative`
  filters on a domain no file has and always reports 0. Measured, not inferred: with `const int ProbeMagic =
  4242;` planted in `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/NarrativeTuning.cs`, `--domain narrative` printed
  `M1=0 M2=0 M3=0 M4=0 / total 0 finding(s), 0 high` while `--domain vocabulary` printed `M3=1 / total 1
  finding(s)`. So NR1.4's acceptance line — and every later row that names `--domain narrative` — proves
  nothing as written. Owning program: the audit script is a pipeline file (`scripts/**`) this lane may not
  edit and its owner is the standards/solid-enforcement stream, so the manager routes it.
  *Accept:* `Narrative` joins `domain_of`'s key list (so the filter selects the narrative tree), or the
  acceptance lines name `--domain vocabulary`; either way a falsifier proves the filter sees a planted literal.

---

## Plan audit (2026-09-20)

Findings and severities are in [npc-story-events-plan.md](npc-story-events-plan.md) *Plan audit (2026-09-20)*
(B1–B8). What changed **in this file**, all fixed, none deferred:

| Ref | Sev | Change |
|---|---|---|
| B1 | High | **NR0.2's acceptance rewritten.** Rows land at `level: module` with no `verificationId` (the `notify-core-domain` shape), because `guard-verification-boundaries.py:82-92` refuses a `verificationId` with no trait-carrying test and NR0.2 runs before any narrative test exists. Each row's `verificationId` is named with the later task that adds it (NR1.1, NR1.4, NR2.9, NR2.14, NR2.20, NR2.24). The old "not-yet-existing file" default is kept but demoted: the guard does not check path existence |
| B2 | High | NR1.4 gains the anti-vacuous criteria for `guard-narrative.py` — a committed row → test-class map derived against the registry, a non-zero exit on an uncovered row, and a non-zero exit when the trait filter selects zero tests — plus both falsifiers, and it adds the `guard.narrative` `verificationId` |
| B3 | High | NR2.2 gains a party-dungeon hand-off step: the old → new path table in the commit body and in `party-dungeon-todo.md`'s transfer note, D3.3/D3.5/D3.9 open-state recorded, and **defer** if any of the three is live elsewhere |
| B4 | High | NR2.32 is marked shared with identity-rename **T13** over the same template files and goldens: clean-or-skip, second lander re-runs the suite after the first and lists the full moved set |
| B6 | Medium | NR2.15's *Files* list gains `gk-core/src/FusionRpg.Core/Narrative/LeadNames.cs` under §4 D6's use-or-create rule |
| B7 | Medium | NR2.32 also lands the map row 31 correction and the `spec-world-anomaly-sites.md` §4/§6 rewrite, with a doc-citation check, and its golden re-bless is explicitly **measured before and after** |
| B8 | Low | NR2.8 states that `_known-defects.json` lives inside the tree narrative-seed's cutover (NSG3/NS69) deletes, and is meant to go with it |

`python scripts/audit-doc-citations.py --scope tasks/npc-story-events-todo.md` — **0 HIGH**.

- [ ] **DOC-NS5.7** (routed by notification-ssot, 2026-09-21) Two citations into the world's old
  `stages/world/notify/notifyRailStore.ts` are a dead citation — that file moved to
  `gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts` (owner-accepted ask A1, notification-ssot
  NS5.7) and its `flush`/`onCommit` were retired in favour of the `worldLatestTurn` mount policy:
  `docs/architecture/npc-story-events/spec-petition-host.md:39` and `:113`. The petition row's own claim
  ("flushes at End Turn like every other non-blocking item") is that mount policy now, so the wording and
  the re-anchor are this program's; `scripts/guard-doc-citations.ps1 -Strict` reports both as D1 until
  they are fixed. Filed here rather than edited by a lane outside its fence.

---

## Finding routed from `test-verification-boundary` (TVB-F15, 2026-09-21)

- [ ] **TVB-F15 (your share) — `doc-citations` is red on this program's docs at the merged head** ·
  `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` exits 1 with HIGH findings in this program's
  documents: citations of `notifyRailStore.ts` (that path does not exist — the file moved) / `categories.ts` (also
  a dead citation, path does not exist) / `notify/clickBudget.test.tsx`, all resolving to no
  tracked file at the cited path (D1) — and `docs/architecture/legion-build/spec-legion-count-cost.md:26`
  cites `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:1013` in a 1003-line file (D2 — stale, the file grew past the
  cited line). The guard is gating in CI, so
  CC8 stays red until the citations are re-anchored to the file's current path or the line says the file
  moved. Full list: `tasks/verification-boundaries-todo.md`'s TVB-F15 row (owning program:
  test-verification-boundary). Owning program here: this one.

- [ ] **NSE-cite-1 — a dead `doc-citations` cite after the notification rail move (A1)** · XS ·
  *(filed by the manager 2026-09-21 from `scripts/guard-doc-citations.ps1`, red at the integration head.)*
  - `docs/architecture/npc-story-events/spec-petition-host.md:113` — D1 stale citation `` `notifyRailStore.ts:16-25` `` — no
    tracked file with this name (the cited path does not exist since the A1 move). The `notification-ssot` program's A1 move relocated the world rail to
    `gk-web/web/fusion-rpg-web/src/shell/notify/rail/`; this program owns the citing line.
  - Fix: re-point the cite at the live path, or say on the line that the file is gone.
  - Verify: `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` → 0 HIGH.

- [ ] **RECON-F5 — the header count and the row count disagree** · XS · *(routed by the manager 2026-09-22 from `tasks/reports/backlog-reconciliation-20260921.md` §9, which lists it and deliberately does not file it: the lane's fence is `tasks/reports/**`.)*
  `tasks/npc-story-events-todo.md:4` says 94 tasks; the file carries 101 open bold-ID rows. Seven checkpoints/sub-items are counted as rows but not in the header. Reconcile the two rather than picking one.
