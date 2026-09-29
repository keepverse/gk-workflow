# Tasks — `solid-enforcement`

Plan: [solid-enforcement-plan.md](solid-enforcement-plan.md) · Map:
[../docs/architecture/solid-enforcement-map.md](../docs/architecture/solid-enforcement-map.md)

**Every task verifies with** `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <lane>`.
Full suite **only** at Checkpoint 1, SE4.4, SE4.30, SE4.43 and Checkpoint 4. **A module ends when its registry row
reads `gating`** (or `local`/`unguardable` with a reason). Quote the measured output in the commit
body, never the intent.

---

## Wave 0 — the spine

- [x] **SE0.1 — Seed `gk-core/scripts/enforcement-registry.v1.json`** · M · deps: —
  - Acceptance: every current guard catalogued (18 `guard-*.ps1` + `session-boundary`) with
    tier/status/backlogModule/localReason **from a fresh measurement** (re-run each guard, check
    `ci.yml`); one invariant row per `DESIGN-GATE.md` §2 item and per uncovered `CLAUDE.md` hard rule,
    each guarded or carrying `unguardableReason`
  - Verify: JSON parses; every `script` path exists
  - Files: `gk-core/scripts/enforcement-registry.v1.json`

- [x] **SE0.2 — `EnforcementRegistryGuardTests` R1–R8, with a falsifier each** · M · deps: SE0.1
  - Acceptance: eight facts green on the real tree; eight falsifiers fail on in-memory broken
    registries; R5 in transitional form (checks `ci.yml` when no runner exists); one shared
    `EnforcementMap.ModuleIds` parser that **fails loudly** if the map's module table can't be found
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistry"`
  - Files: `gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs`, `…/EnforcementMap.cs`

- [x] **SE0.3 — Map the new files and add the DESIGN-GATE line** · XS · deps: SE0.2
  - Acceptance: `verify-change` resolves both new files; `DESIGN-GATE.md` §5 has *"A new rule has a
    registry row: a guard, or an `unguardableReason`"*
  - Files: `gk-core/scripts/verification-boundaries.v1.json`, `docs/DESIGN-GATE.md`

- [x] **SE0.4 — `scripts/run-guards.ps1` plus `GuardRunnerTests`** · M · deps: SE0.2
  - Acceptance: child process per guard; runs all, then fails; backlog guards never fail and print
    under `BACKLOG`; unknown `-Only` id throws; `-Only` on a backlog guard reports and never fails;
    registry `args` with `{ciRange}` substitution; summary table
  - Verify: the no-masking falsifier (red guard, then a second guard still runs); an `exit 3` guard
    does not stop the next
  - Files: `scripts/run-guards.ps1`, `gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs`

- [x] **SE0.5 — CI cutover** · S · deps: SE0.4
  - Acceptance: the "Boundary guards" step is one `run-guards.ps1 -Tier ci` call; the
    `guard-generated-seed` range moves into registry `args`; the integrity step stays separate with
    its comment; one real CI run green with the summary table in the log
  - Files: `.github/workflows/ci.yml`, `gk-core/scripts/enforcement-registry.v1.json`

- [x] **SE0.6 — `deploy-play` cutover** · S · deps: SE0.4
  - Acceptance: the hand list is replaced by `run-guards.ps1 -Tier local`; `game-profile` stays
    positioned via `-Only game-profile -LocalArgs`; the G3 tolerance block is removed (the registry's
    backlog row now carries that fact); Guard.Tests that grep `deploy-play` for guard names are
    re-pointed at the registry and runner
  - Verify: `deploy-play.ps1 -NoServer -NoGame` on this machine runs the runner and prints the table
  - Files: `scripts/deploy-play.ps1`, the affected Guard.Tests

- [x] **SE0.7 — `verify-change` onto the catalog; remove the duplicate map** · M · deps: SE0.4
  - Acceptance: `verify-change` resolves guard ids through the enforcement registry;
    `verification-boundaries.v1.json` has **no** `guards` section; its integrity guard requires the
    absence and checks every `boundaries[].guards` id exists in the catalog; R7 deleted; R5 in
    post-runner form (no `guard-*.ps1` path elsewhere in `ci.yml`)
  - Acceptance: the same commit bumps `verification-boundaries.v1.json` `schemaVersion` **1 → 2**
    (`test-verification-boundary-map.md` §3.2; parent hard edge **H5**: `TVB registry-contract` starts
    from schema 2 and takes 3); catalog ids equal today's `guards` keys (all of them, incl.
    `magic-numbers` and `session-boundary`), or are renamed in `boundaries[].guards` in the same commit;
    the fixture in `VerificationBoundaryWorkflowTests.cs:200-202` (`"schemaVersion": 1` plus its
    `"guards"` map) is rewritten to the schema-2 shape with the bump
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~EnforcementRegistry"`;
    `python gk-core/scripts/guard-verification-boundaries.py`
  - Files: `scripts/verify-change.ps1`, `gk-core/scripts/verification-boundaries.v1.json`,
    `gk-core/scripts/guard-verification-boundaries.py`, `EnforcementRegistryGuardTests.cs`,
    `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`

- [x] **SE0.8 — Debt ledger: `solid` kind and rows** · S · deps: SE0.2
  - Acceptance: `solid` documented; `StubRegisterTests` kind pin 3 → 4 with its reason; rows for
    atk, `CommanderId`, tuning pollution, commit-policy and god files (ids = current max + 1…); the
    phase 1 close and T4.4 S7 in Hand-off as owner items; the new fact (an open `solid` row waits on
    a real module) plus its falsifier
  - Files: `docs/architecture/stub-register.md`, `gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs`

### Checkpoint 0
- [ ] CI green with the runner as the only guard entry point
- [ ] Registry meta-test and runner tests green, falsifiers included
- [ ] **Owner shown the map** (non-blocking review; a redrawn boundary edits specs)

---

## Wave 1 — green what exists

- [x] **SE1.1 — Wire the five green guards** · S · deps: SE0.5
  - Acceptance: `debug-scope`, `magic-numbers`, `overflow`, `power`, `stat-pairs` re-run on a clean
    checkout, then flipped to `ci`/`gating`; `local` reasons must name the game install (R4 extension);
    five scratch-branch falsifier runs recorded in the commit body
  - Files: `gk-core/scripts/enforcement-registry.v1.json`, `EnforcementRegistryGuardTests.cs`

- [x] **SE1.2 — Commit policy accepts GitHub web merges, narrowly** · S · deps: SE0.5 · *(owner ruled Q3: yes, 2026-09-18)* · **RETIRED 2026-09-19:** the owner retired the whole git gate (`scripts/commit-tool/`, `.githooks`, the `commit-policy` guard), so there is no commit policy left to extend. Nothing to build.
  - Acceptance: alias author plus `allowedMergeCommitters`; the merge rule runs **before**
    `validate_identity` (`scripts/commit-tool/validate.py`, once at `:86`, since retired); the four smoke cases (2-parent pass; 1-parent fail;
    non-allowlisted author fail; spoofed committer email fail); a UTF-8 `Lê Tú Hào` case; the guard
    green on the real tree and flipped to `gating`; `agent-git.md` paragraph
  - Files (all retired with the gate): `scripts/commit-tool/policy.json`, `check_history.py`, `validate.py`, smoke tests,
    `docs/contributing/agent-git.md`, registry

- [x] **SE1.3 — `retire-atk` R1+R2: the retired registry state, dropped at load** · M · deps: SE0.2
  - Acceptance: `DerivedStatChannels.Retired` closed set with the dated ruling; `AptitudeTuning.Parse`
    drops retired edges and `familyRead` keys, counted in `DroppedRetiredEdges`; **an unknown channel
    still throws** (existing test green); a theory loads every `aptitudes.v*.json` on disk
  - Files: `DerivedStatChannels.cs`, `AptitudeTuning.cs`, tests

- [x] **SE1.4 — `retire-atk` R3: `publish.py` removal ops, then publish `aptitudes.v9`** · M · deps: SE1.3
  - Acceptance: `--remove-edge` and `--remove-key`, each refusing zero or ambiguous matches, with tool
    tests; `aptitudes.v9.json` published through the tool; every host loading `aptitudes.v8` moved to
    v9 (measure the hits); `CreatureSpeciesGen`'s v2 pin **untouched**
  - Files: `gk-core/tools/tuning/publish.py` (+ tests), `gk-core/data/tuning/aptitudes.v9.json`, host loaders

- [x] **SE1.5 — `retire-atk` R4: code removals and the catalog** · M · deps: SE1.4
  - Acceptance: const and registration removed; `MergeAppliedCombat` without the atk term;
    `UniqueBoundLoadout` atk grants gone (both sides); `DerivedAuditActor` row and `EntityApply`
    telemetry gone; `derived-stat-catalog.v3.json` published and hosts moved;
    `gk-data/packs/fusion/data/seed/derived-stats/catalog.json` handled by its provenance (authored → edit; generated → fix
    the generator)
  - Files: `ActorHub.cs`, `DerivedStatRegistry.cs`, `UniqueBoundLoadout.cs`, `DerivedAuditActor.cs`,
    `EntityApply.cs`, catalog files, loaders

- [x] **SE1.6 — `retire-atk` R5: regenerate generated content** · M · deps: SE1.5
  - Acceptance: `dotnet run --project gk-forge/tools/CreatureSpeciesGen` → the 11 creature files lose the
    `atk` magnitude, `--check` clean, nothing hand-edited; **tree: `RETIRED_FAMILY_SUCCESSOR`
    (`progression.bonus.atk → combat.power`, keeping each cell's element) added to
    `nodegen/quota.py` with a test, then the deterministic stages re-run with no model call, and all 16
    nodes keep id, name, flavour, tier and budget while their `quotaCell.channelFamily` reads
    `combat.power`** (owner ruling, map question 2); the retired family removed from the plan's pool
    at its source; FE bundle rebuilt; `grep -rn progression.bonus.atk src gk-data/packs/fusion/data/generated`
    empty (historical tuning excepted)
  - Files: generator inputs, `gk-data/packs/fusion/data/generated/creatures/**`, tree plan source, FE build output

- [x] **SE1.7 — `retire-atk` R6/R7: guard gates, decision closed, pins moved** · M · deps: SE1.6
  - Acceptance: `guard-class-system` exits 0; `…_permanentlyByDesign` replaced by `…_exitsZero…`
    plus a G3 falsifier; `class-system-plan.md` decision 12 marked superseded; the six `269` pins → 268
    with the dated reason; registry `class-system` → `gating`; SR-19 struck with the SHA;
    **BalanceGuard and sim goldens before and after, and any move explained as the sim-only bonus
    removal**
  - Files: `ClassSystemGuardTests.cs`, `tasks/class-system-plan.md`, the six pin sites, registry,
    ledger

### Checkpoint 1 (full suite)
- [ ] Every guard that existed at program start is `gating` or `local`
- [ ] **Full suite green** (`test-fast.ps1 -AllDefault`), one run, output quoted
- [ ] No moved golden without a written explanation

---

## Wave 2 — new guards, small backlogs

- [x] **SE2.1 — `guard-tuning-immutability.py` (T1–T4) plus temp-repo tests** · M · deps: SE0.5
  - Acceptance: `_meta`-only edits pass; value edits, gaps, deletions and denylisted domains fail; the
    correction marker scoped to named files and printed loudly; `ConvertTo-Json` key-order round-trip
    verified (fallback: recursive key sort); registry row `backlog`
  - Files: the guard, `gk-core/scripts/tuning-domain-denylist.v1.json`, `TuningImmutabilityGuardTests.cs`

- [x] **SE2.2 — Stop the pollution at its source; delete the four files** · M · deps: SE2.1
  - Acceptance: the residual-fit tool gains `--tuning-dir` (publish target derived from the same
    input as the measurement); `ResidualFitLoopTests` publishes into a temp dir with a **checked**
    delete; the four `loopwarntest*` files deleted under the correction marker; the guard gates
  - Files: the residual-fit tool, `ResidualFitLoopTests.cs`, `data/tuning/loopwarntest*.json`,
    registry

- [x] **SE2.3 — Extend `guard-test-substrate` to swallowed `File.Delete`** · S · deps: SE2.2
  - Acceptance: an empty or comment-only `catch` around `File.Delete` fails the guard; any other hits
    fixed in the same commit (green-first); falsifier
  - Files: `gk-core/scripts/guard-test-substrate.py`, the fixed tests

- [x] **SE2.4 — `guard-repo-boundary.py` (B1–B3)** · S · deps: SE0.5
  - Acceptance: the dependency graph read from csproj (XML parse of `ProjectReference` only) and pinned
    as measured; host-assembly refs and `using`s refused; frozen paths refused in the diff; the
    `InternalsVisibleTo` non-regression passes; lands directly as `gating`
  - Files: the guard, `RepoBoundaryGuardTests.cs`, registry

- [x] **SE2.5 — `pvz-write-surface`: extend `guard-single-writer` (W2/W3)** · S · deps: SE1.7
  - Acceptance: comment stripping; per-writer-file field lists **measured after `retire-atk`** and
    pinned with the RPG-layer reason; five retired fields refused everywhere; falsifier: an
    uncommented `p.attackDamage` fails
  - Files: `scripts/guard-single-writer.ps1`, single-writer tests, registry invariant row

- [x] **SE2.6 — `vocabulary-mirror` manifest and checker** · M · deps: SE0.5
  - Acceptance: `vocabulary-mirrors.v1.json` with every C#-owned vocabulary mirrored in seedsmith
    (walk all seven vocab modules); C# enum parser fails loudly on an unparseable block; V1–V4
    falsifiers; registry row `backlog`
  - Files: the manifest, `gk-core/scripts/guard-vocabulary-mirror.py`/`.ps1`, seedsmith test

- [x] **SE2.7 — `vocabulary-mirror` backlog, then gate** · S · deps: SE2.6
  - Acceptance: `STATUSES` 21 vs 24 resolved **on the record** (read `vocab.py`'s comment: equal plus
    3 `nerve.*` ids, or `subset` plus a quoted reason); transcription tests (`test_nine_tags` etc.)
    assert owner-equality instead of literals; the guard gates
  - Files: `adapters/actions/vocab.py`, `test_actions_adapter.py`, registry

### Checkpoint 2
- [x] `tuning-immutability`, `repo-boundary`, `vocabulary-mirror` gating; `single-writer` extended
- [ ] No `loopwarntest*` file in the tree (verified); a **full** local test run creates none under
      `data/` -- blocked on the orchestrator's full-suite gate (`test-fast.ps1 -AllDefault`); the one
      test that could write there (`ResidualFitLoopTests`) is verified isolated to a temp dir (SE2.2)

---

## Wave 3 — backlog-heavy guards

- [x] **SE3.1 — `guard-population-pin.py` (P1–P3) plus falsifiers** · M · deps: SE0.5
  - Acceptance: C# and Python scanning; content-reading detection; the two marker kinds; `minLiteral`
    10 as a commented structural const with its measurement; `--summary`/`--targets`; registry row
    `backlog`; `validation-ssot.md` documents the markers
  - Files: the guard, falsifier tests, `docs/architecture/validation-ssot.md`

- [x] **SE3.2 — Pin backlog: `Core.Tests/ActorHub` + `ActorSurface` (the six-fold `269`)** · M · deps: SE3.1, SE1.7
- [x] **SE3.3 — Pin backlog: the rest of `Core.Tests`** · M · deps: SE3.1
- [x] **SE3.4 — Pin backlog: `Data`/`Server`/`Guard`/other C# test projects** · M · deps: SE3.1
- [x] **SE3.5 — Pin backlog: seedsmith tests (`904`, `775`, `125` → contracts)** · M · deps: SE3.1
  - Acceptance for SE3.2–3.5: every site in the batch dispositioned (marker at the owner, equality
    with the owner, or a contract rewrite); each contract rewrite records the mutation that proved it
    still fails; the batch's `--targets` count is 0 and quoted

- [x] **SE3.6 — `population-pin` gates** · XS · deps: SE3.2–SE3.5
  - Acceptance: `--summary` 0 findings; registry `gating`

- [x] **SE3.7 — `audit-doc-citations.py`: D3 promoted, D4 added, `.ps1` wrapper** · M · deps: SE0.5
  - Acceptance: D3 gating outside `docs/research/`; D4 (ideal vs approved map without a banner);
    wrapper `guard-doc-citations.ps1 --strict`; falsifiers for D1–D4 and all exemptions; registry row
    `backlog`
  - Files: `scripts/audit-doc-citations.py`, the wrapper, tests

- [x] **SE3.8 — Doc backlog: `docs/architecture/*.md` root** · M · deps: SE3.7
- [x] **SE3.9 — Doc backlog: `world-stage/`, `world-map-runtime/`, `story-scene/`, `rift-gate/`** · M · deps: SE3.7
- [x] **SE3.10 — Doc backlog: `item/`, `seedsmith/`, `passive-tree/`** · M · deps: SE3.7
- [x] **SE3.11 — Doc backlog: every remaining `docs/architecture/<program>/`** · M · deps: SE3.7
- [x] **SE3.12 — Doc backlog: D3 path-qualification outside architecture** · M · deps: SE3.7
  - Acceptance for SE3.8–3.12: the batch's scope reports 0 HIGH / 0 D3 / 0 D4, quoted **after** the
    edit; every *corrected* (not merely repointed) claim listed in the commit body; no guessed line
    numbers

- [x] **SE3.13 — `doc-citations` gates** · XS · deps: SE3.8–SE3.12
  - Acceptance: `--strict` exits 0 on the tree; registry `gating`

- [x] **SE3.14 — M3 backlog: every balance-surface `const` says why it isn't tunable** · S · deps: SE1.1 · *(owner: "clear them completely", 2026-09-18)*
  - **Done 2026-09-18, ahead of wave order on the owner's instruction.** Of the 28 sites: 13 already
    carried their reason in a trailing or group-header comment the audit could not see (the audit now
    reads both shapes); 8 were balance numbers and moved to `gk-core/data/tuning/deployment-hierarchy.v2.json`
    (`cacheDecay`, `cacheRetrieval`, published with the new `publish.py --add-key`, loaded at server
    startup through `DeploymentHierarchyTuningHub`); 2 were a test's acceptance band and moved into
    the test; `RiftMenuOverlayLayout` was dead code and was deleted; the rest gained a T2 comment.
    M1–M4 all report 0. **Still open:** flipping M3 to gating waits for `guard-runner` (SE0.4), same
    as SE3.15. Found on the way: the item head-field tables are dark (`stub-register.md` `SR-19`)
  - Acceptance: each of the 28 M3 sites either gains the T2 comment (*structural because…*, e.g. a
    buffer size) or moves to `gk-core/data/tuning/` if a balance pass would change it; `guard-magic-numbers`
    fails on M3 afterwards
  - Verify: `python gk-core/scripts/audit-magic-numbers.py --targets M3` prints nothing

- [x] **SE3.15 — A3 backlog: re-triage the 46 `int`-magnitude sites, then gate** · M · deps: SE1.1 · *(owner: "help me fix them", 2026-09-18)*
  - **Done 2026-09-18, ahead of wave order on the owner's instruction** (`5a22698b`, `172a163a`): 46 + 33 newly visible sites resolved, and the audit reports 0 findings in every category over `src/` and `tools/`. **Still open:** flipping A3 to gating in `guard-overflow.ps1` waits for `guard-runner` (SE0.4), so it lands through the registry rather than as a fourth hand-edited list
  - Acceptance: each site dispositioned the way `docs/architecture/power/overflow-triage.md` did in
    2026-08: **LADDER**, widen to `long` (widen before multiplying; `checked`); **BOUNDED**, a
    `// bounded: <proven cap>` marker the audit honours; **NOT-A-MAGNITUDE**, fix the audit's regex (the
    triage's own precedent, e.g. `SiegeAi.cs:61` weights); the triage doc updated with today's split;
    `guard-overflow` fails on A3 afterwards
  - Verify: `python gk-core/scripts/audit-overflow.py --targets A3` prints nothing

### Checkpoint 3
- [x] `population-pin` and `doc-citations` gating with 0 findings
- [ ] M3 and A3 gating (if the owner confirms Q4) — owner-gated, not resolved this session

---

## Wave 4 — structural instances (serial)

*`commander-identity` tasks re-checked 2026-09-18 against the strengthened spec (R3/R17 pass): the
directory now takes the save for display names, the first commander shows the player's name, the
string switch and the closed list are named, and nine `== CommanderId.Dave` sites are handed to
`save-identity` (SE4.35/SE4.36) instead of being re-typed twice.*

- [x] **SE4.1 — `EmpireId`, `CommanderRef`, `ICommanderDirectory` and the default-commanders registry** · M · deps: SE0.8 · *(spec: commander-identity)*
  - Acceptance: both open value types (`EmpireId.Dave`/`.Zomboss` as well-known values, no "all
    empires" list); `ICommanderDirectory` with `TryResolve`, `EmpireOf`, `DisplayName(commander,
    playerId)`, `AllocationScopeKey(commander, playerId)`, `DefaultFor`, data-backed by the authored
    registry: two rows, stable ids and scope keys `player:{id}` / `zomboss:{id}` byte-identical to
    today; display "Dr. Zomboss" for Zomboss and **the player's own name** for `commander:dave` (the
    one ruled change)
  - Acceptance: no callers moved yet; directory unit tests incl. the display-name rule and an unknown
    stable id refused
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Commander"`, then
    `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Core/Commanders/EmpireId.cs`, `CommanderRef.cs`, `ICommanderDirectory.cs`,
    `DataCommanderDirectory.cs`, `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`

- [x] **SE4.2 — Migrate Core call sites, by meaning** · M · deps: SE4.1 · *(spec: commander-identity)*
  - Acceptance: every Core use typed `EmpireId` or `CommanderRef` **by meaning**, recorded per file in
    the commit body; the four enum `switch` expressions **and** the string switch in
    `TryParseStableId` deleted (→ `TryResolve`); `CommanderIds.All` deleted; Core builds
  - Acceptance: the Core `== CommanderId.Dave` sites (`PlayerEmpireCommanders.cs:19`,
    `SpeciesAllocation.cs:29`, `SpeciesAllocationSource.cs:114`) become `== EmpireId.Dave`; the commit
    body tags the "the save's human empire" ones for SE4.35 (`SpeciesAllocation.cs:29` stays
    `EmpireId.Dave` for good: it picks a persisted string shape)
  - Verify: `dotnet build src\FusionRpg.Core`; `verify-change.ps1 -Paths <files>`
  - Files: `Commanders/`, `Stats/Aptitudes/`, `Battle/KillAttribution.cs`, `Combat/`, `Match/`,
    `Creatures/`, `World/**` enum uses (39 `src/` files at spec time, a reading; re-measure)

- [x] **SE4.3 — Migrate Data, Server, Injector, Contracts** · M · deps: SE4.2 · *(spec: commander-identity)*
  - Acceptance: every remaining `src/` use migrated by meaning; `enum CommanderId` deleted; persisted
    strings unchanged (no migration); the remaining `==` sites (`CommanderEndpoints.cs:78`, `:93`,
    `ItemEquipEndpoints.cs:307`, `RpgStore.Aptitudes.cs:232`, `:266`, `RpgStore.WorldTurns.cs:573`,
    `CheatState.cs:183`) read `== EmpireId.Dave`, tagged for SE4.35/SE4.36
  - Acceptance: `CommanderEndpoints.ProjectList` passes the save to `DisplayName`, so
    `/api/commanders/{id}` shows the player's name; the "player unknown" fallbacks
    (`MatchCommanderSessionCache.cs:14`, `:43`, `RpgClient.cs`) use a **neutral** label, never a name
  - Verify: `dotnet build src\FusionRpg.Server`; `.\scripts\guard-injector-compile.ps1`;
    `verify-change.ps1 -Paths <files>`

- [x] **SE4.4 — Tests, the Open/Closed proof, the guard, the seed name, the doc move** · M · deps: SE4.3 · *(spec: commander-identity)*
  - Acceptance: tests migrated; `CommanderIdTests`' count pin (`Assert.Equal(2, CommanderIds.All.Count)`)
    deleted with its reason (a population now), `KillAttributionTests` assert membership in the
    directory's rows; the **third-commander test** (an in-memory directory row runs a lawn allocation
    plus kill attribution with zero production edits)
  - Acceptance: `SeedPlayerIfEmpty` names an empty-save player **"Crazy Dave"** (declared once, with a
    comment naming the owner's onboarding idea; `'Player 1'` gone), and a test reads the player's
    name back through `/api/commanders/{id}`; `guard-open-identity.ps1` (I1/I2) with falsifiers,
    registry row `gating`; `empire-progression-ideal.md` section marked moved; SR-20 struck
  - Acceptance: **full suite green once, and any moved golden stops the module until explained**
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Commander|FullyQualifiedName~KillAttribution|FullyQualifiedName~SpeciesAllocation"`;
    Guard.Tests falsifiers; `test-fast.ps1 -AllDefault` (sanctioned: module end, cross-boundary)
  - Files: tests, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` (seed name only), `scripts/guard-open-identity.ps1`,
    `docs/architecture/empire-progression-ideal.md`, `docs/architecture/stub-register.md`
  - **Gap closed 2026-09-20** (found during `convergence-checkpoints` CC2 verification: this task was
    ticked but `scripts/guard-open-identity.ps1` did not exist anywhere in `features/mega-merge`).
    Built the guard (I1/I2, textual, matching `guard-dal.ps1`'s own style), its 6 Guard.Tests
    falsifiers (`OpenIdentityGuardTests.cs`, including the inverse-compliant fixture), and its
    `enforcement-registry.v1.json` row (`"open-identity"`, `dg-15-solid`). Exits 0 on the real tree;
    every other SE4.4 acceptance clause spot-checked and found already correct (no further drift).
    See `tasks/evidence-fragments/SE4.4-guard-gap-closure.md`.

### `save-identity` (rulings R3 + R17) — SE4.11–SE4.43

Spec: [spec-save-identity.md](../docs/architecture/solid-enforcement/spec-save-identity.md). The
`decisions.md` rows S1–S4 it owed landed on 2026-09-18 (`1575db58` series), so no task writes them.
Numbering continues after SE4.10; SE4.5–SE4.10 (`srp-file-budget`) keep their ids and still run last.
Three stages, in this order: **(a) first slice** (additive, deployable on its own; what other
programs build against) → **(b) the migration unit** (the one irreversible step, plus every consumer
that is wrong without it) → **(c) surfaces and hardening** (safe after the unit is merged). Counts in
the spec (tables, routes, sites) are **readings**: re-measure at build, never pin them in a test.

#### (a) First slice — the seams other programs start on

- [x] **SE4.11 — `SaveId`, `EmpireRef`, `EmpireController`, and the new-save registry** · S · deps: SE4.1 · *(spec: save-identity)*
  - Acceptance: the three types in `FusionRpg.Core.Saves`; `EmpireController` pinned at two members
    **with the closed-vocabulary reason**; the authored registry has the two rows (`dave`/`human`,
    `zomboss`/`ai`)
  - Acceptance: its validator checks schema, closed `controller` membership, exactly one `human` row
    and `empireId` shape, **never a row count**; a falsifier per rule
  - Acceptance: the debt ledger gains the `solid` row "empire is a player row / Zomboss is a player
    found by name" (next SR id), struck by SE4.43
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Saves"`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Core/Saves/SaveId.cs`, `gk-core/src/FusionRpg.Core/Saves/NewSaveEmpires.cs`,
    `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json`, `tests/FusionRpg.Core.Tests/Saves/*`,
    `docs/architecture/stub-register.md`

- [x] **SE4.12 — `rpg_save_empires`, the one seeder, `HumanEmpireOf` / `EmpiresOf` / `IsLiveSave`** · M · deps: SE4.11 · *(spec: save-identity)*
  - Acceptance: table as specced; **one** `SeedSaveEmpiresUnlocked(db, save)` called by
    `SeedPlayerIfEmpty` and by `CreatePlayer` in the same transaction as the row, **and** idempotently
    for the current save at `Init` and on `SetCurrentPlayer` (plan default, see plan "Defaults");
    `EnsureZombossPlayer`'s row is created **without** empires (it is not a save)
  - Acceptance: `HumanEmpireOf` reads the `human` row and throws `SaveEmpiresNotSeeded` on an unseeded
    save (never guesses `"dave"`); `players.archived_utc` added via `EnsureColumn`; `IsLiveSave` =
    exists and not archived
  - Acceptance: contract test: every seeded save has exactly one `human` empire; a fresh boot yields
    save 1 with both registry empires and no Zomboss player row
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveEmpires"`; `.\scripts\guard-dal.ps1`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SaveEmpires.cs` (new), `RpgStore.cs` (seed, `CreatePlayer`,
    `SetCurrentPlayer`, `Init` call), `RpgStore.ZombossDeploy.cs`, `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveEmpiresStoreTests.cs`

- [x] **SE4.13 — `SaveOfRunUnlocked` / `SaveOfMatchUnlocked`** · S · deps: SE4.11 · *(spec: save-identity, G4/X11)*
  - Acceptance: `GetRunPlayerId` (`RpgStore.cs:3835`) **renamed and typed** to `SaveOfRunUnlocked`, its
    callers moved, no second lookup; `SaveOfMatchUnlocked` reads `runs.match_key → player_id`
  - Acceptance: unknown run or match → `null`, never the current save; tests for both
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveEmpires"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.SaveEmpires.cs`, `RpgStore.cs`, the test file

- [x] **SE4.14 — `rpg_unique_actors.empire_id` and `OwnsSpecimenUnlocked`** · M · deps: SE4.12 · *(spec: save-identity, "One ownership predicate")*
  - Acceptance: `empire_id` added via `EnsureColumn`; a mint on a seeded save stamps
    `HumanEmpireOf(save)`; rows on an unseeded row (pre-migration history, the legacy Zomboss row)
    stay `null` until SE4.18 backfills them
  - Acceptance: `OwnsSpecimenUnlocked(db, EmpireRef, instanceId)` compares `(player_id, empire_id)`
    strictly (`null` never matches); **no production caller yet** (SE4.24/SE4.25 wire it after the
    migration); tests: own specimen true, other save false, other empire of the same save false
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.cs` (column), `RpgStore.Creatures.cs`, `RpgStore.SaveEmpires.cs`,
    `gk-core/tests/FusionRpg.Data.Tests/Saves/SpecimenOwnershipTests.cs`

### Checkpoint 4a — first slice (lane B foundation)
- [x] SE4.11–SE4.14 green and on `features/mega-merge`; a fresh boot and `POST /api/players` both
      produce a save with its registry empires
- [x] The seams `SaveId`, `EmpireRef`, `HumanEmpireOf`, `EmpiresOf`, `IsLiveSave`, `SaveOfRunUnlocked`,
      `SaveOfMatchUnlocked`, `OwnsSpecimenUnlocked` exist with tests, so `SP species-mod-ledger`,
      `SP empire-species-container`, `EP commander-roster`, `EP respec-free-counter` and
      `NS notify-store`/`player-routing` can build against them
- [x] No existing number moved (`verify-change` on every touched path green)

#### (b) The migration unit — irreversible; parent hard edge H2

**Owner ruling R27: direct on the branch, SE4.20 last.** (Superseded suggestion: one worktree for SE4.15–SE4.30.) `Init` runs the
migration on every boot, and the owner deploys from the shared branch, so half this unit on the shared
branch would migrate real data while Zomboss's mint, the ownership predicate and the injector still
compare player ids (spec: *"an old injector against a migrated server would … call Zomboss's specimen
an ally"*). If the owner prefers direct mode instead, SE4.20 must be the last commit of the unit to
land. Either way SE4.15–SE4.19 build the steps **dormant** (called only by tests) and SE4.20 is the
one task that makes `Init` call them.

- [x] **SE4.15 — `SaveIdentity.Migrate`: gate, backup, one transaction, marker** · M · deps: SE4.12 · *(spec: save-identity, migration steps 0, 1, 7)*
  - Acceptance: step 0 returns when `settings['schema.save-identity']` exists; step 1 `VACUUM INTO` a
    **new, never-reused** `rpg-hot.sqlite.pre-save-identity.{utcStamp}.bak` before any write (memory
    store skips it); a failed backup writes nothing and makes `Init` refuse to start
  - Acceptance: steps 2–7 run in one transaction whose last statement writes the marker with the JSON
    report (mirrored to the console); an injected failure leaves schema, rows and marker unchanged; a
    second run changes nothing
  - Acceptance: disk test `DiskSemantics`-tagged and leak-proof (`.bak` exists before the first write; a
    second attempt after a failed one writes a new `.bak`, first untouched); all others in memory
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity"`; `python gk-core/scripts/guard-test-substrate.py`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityMigrationTests.cs` (new), `…/Saves/SaveIdentityBackupDiskTests.cs` (new)

- [x] **SE4.16 — Step 2: is the legacy Zomboss row a save? Evidence, and a tie goes to "save"** · M · deps: SE4.15 · *(spec: save-identity, step 2)*
  - Acceptance: finds the lowest-id `"Zomboss"` row (the one historical name lookup, allowed only here);
    Zomboss-only **iff** every reference is on the spec's allowlist of Zomboss-path writes, read from
    code; an `rpg_save_empires` row counts as **save** evidence (since SE4.12 only the save path writes
    it); anything else makes it a save
  - Acceptance: fixtures built once from **real production calls** (`CreatePlayer`, `MintCreature`,
    `EnsureZombossPlayer` as it exists before SE4.22, `TryApplyXpUnlocked`); one test per evidence kind
    alone; the name collision **both ways** (a "Zomboss" save with runs; one created before the first
    deploy, holding a summon and no run)
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity"`; `verify-change.ps1 -Paths <files>`
  - Files: `Migrations/SaveIdentity.cs`, `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityFixtures.cs` (new), the migration test file

- [x] **SE4.17 — Steps 3–4: seed every save's empires; rebuild the two Tier A tables** · M · deps: SE4.16 · *(spec: save-identity, steps 3–4; decisions S2/S3)*
  - Acceptance: step 3 seeds every save (all rows but a Zomboss-only legacy row) through
    `SeedSaveEmpiresUnlocked`, idempotent with SE4.12's current-save seeding
  - Acceptance: `rpg_actor_progression` / `rpg_xp_ledger` renamed to `<name>__pre_save_identity` and kept;
    new tables `(save_id, empire_id, kind, type_id)` / `UNIQUE (save_id, empire_id, kind, type_id,
    reason, dedupe_key)` with **new** index names; every row copied onto `HumanEmpireOf(save)`, history
    never re-attributed; a Zomboss-only row's rows stay behind and are counted in the report
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity"`; `verify-change.ps1 -Paths <files>`
  - Files: `Migrations/SaveIdentity.cs`, the migration test file

- [x] **SE4.18 — Step 5: `empire_id` backfill and legacy Zomboss specimens re-homed by provenance** · M · deps: SE4.17, SE4.14 · *(spec: save-identity, step 5)*
  - Acceptance: every save's own specimens get `HumanEmpireOf(save)` whatever their `origin` (counted);
    a Zomboss-only row's specimens get `zomboss` and a save by (a) match provenance (specimen, lawn
    session or lawn-XP receipt `match_key` → `runs`), (b) the only save, else (c) stay `Retired` on the
    legacy row, ids in the report; the backfill **sets** every row, not only nulls
  - Acceptance: re-homing moves `rpg_unique_lawn_sessions` / `rpg_unique_actor_recovery` with the
    specimen and releases its legacy contract (`bound = 0`); nothing deleted
  - Acceptance: tests: one save + no provenance → (b); two saves via receipt and via session → (a); two
    saves, no provenance → (c); **provenance survives the sweep** (an `ActiveBound` specimen of an open
    run is attributed before `SweepStaleActiveBoundUnlocked` clears its `match_key`)
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity"`; `verify-change.ps1 -Paths <files>`
  - Files: `Migrations/SaveIdentity.cs`, the fixtures file, the migration test file

- [x] **SE4.19 — Step 6 and the full report; byte-identical human numbers** · M · deps: SE4.18 · *(spec: save-identity, steps 6–7)*
  - Acceptance: a Zomboss-only legacy row gets `archived_utc` and is kept (its codex rows stay); a
    legacy row that is a save keeps both empires; the report carries every field the spec lists
    (saves migrated, evidence that decided, (a)/(b) counts, unattributed ids, zomboss-origin specimens
    kept on a save, legacy progression rows left, backup path)
  - Acceptance: **byte-identical**: for every save, every `rpg_actor_progression` value and every
    resolved allocation equals the pre-migration read for the human empire; atomic test with a failure
    injected at step 5
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity"`; `verify-change.ps1 -Paths <files>`
  - Files: `Migrations/SaveIdentity.cs`, the migration test file

- [x] **SE4.20 — Activate: `Init` runs the migration; Tier A DDL and SQL move to `(save_id, empire_id)`** · M · deps: SE4.19 · *(spec: save-identity; parent **H2** anchor)*
  - Acceptance: `Init` calls `SaveIdentity.Migrate` after every `CREATE TABLE`/`EnsureColumn` of the
    classified tables and **before** `CloseAbandonedRunsUnlocked` / `SweepStaleActiveBoundUnlocked`;
    a fresh database is created in the widened shape, gets the marker at seed with an empty report and
    never renames a table
  - Acceptance: every read/write of the two Tier A tables uses `save_id` + `empire_id` (human empire for
    every writer today); the existing progression tests pass unchanged except for type renames in their
    own setup
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity|FullyQualifiedName~Progression"`; `.\scripts\guard-dal.ps1`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.cs` (DDL, `Init`, Tier A SQL), `RpgStore.Progression.cs`, `RpgStore.Compaction.cs`,
    `RpgStore.Storage.cs`, the migration test file. *(Six with the test: the SQL readers cannot split
    from the DDL without a broken window.)*

- [x] **SE4.21 — Tier A store API takes `EmpireRef`; every award names its owner (G4)** · M · deps: SE4.20 · *(spec: save-identity, G4/X11 and the seams list)*
  - Acceptance: `TryApplyXpUnlocked(EmpireRef …)`, `ReadEmpireActorUnlocked`, `CommanderLevelOf(SaveId,
    EmpireId)`; `ApplyRpgProgressionFromActivityUnlocked` takes `SaveId` and **throws** when
    `save != SaveOfRunUnlocked(runId)`; both species-XP paths (per placement, run completion) pass an
    `EmpireRef`
  - Acceptance: a fact whose run resolves to no save awards nothing and is reported; which empire earns
    stays `EP ai-empire-species`'s rule (this task passes the human empire, today's behaviour)
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Progression|FullyQualifiedName~SaveEmpires"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.Progression.cs`, `RpgStore.cs`, `RpgStore.SaveEmpires.cs`, progression tests

- [x] **SE4.22 — Zomboss is an empire of the match's save** · M · deps: SE4.21 · *(spec: save-identity, "Zomboss stops being a player row", G5/X12)*
  - Acceptance: `MintForEmpire(EmpireRef, speciesId, seed)` replaces `MintForZomboss` (mint mapping and
    `origin: "zomboss"` unchanged); `EnsureZombossPlayer` and `ZombossPlayerName` deleted
  - Acceptance: `/api/zomboss/deploy` requires `matchKey`; `SaveOfMatchUnlocked` resolves the save
    **before** the mint; unresolved → `409 match_unresolved` and nothing minted (test)
  - Acceptance: Zomboss minted into save 1 is not save 2's (test)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ZombossDeploy"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.ZombossDeploy.cs`, `gk-core/src/FusionRpg.Server/ZombossDeployEndpoints.cs`, its request DTO,
    `gk-core/tests/FusionRpg.Server.Tests/…ZombossDeploy…`

- [x] **SE4.23 — AI-empire specimens never touch a human-only table (fixes D6)** · M · deps: SE4.22 · *(spec: save-identity, "AI-empire specimens never touch a human-only table")*
  - Acceptance: an AI-empire mint writes no `rpg_creature_codex`, `rpg_creature_contracts` or
    `rpg_contract_state` row; `TryBeginUniqueDeploy`'s contract gate applies to human-empire
    specimens only; `DeployAsync` records no `ExtraSpawnFired` for a non-human empire
  - Acceptance: **D6 regression test**: a 13th Zomboss deploy in one save still deploys
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AiEmpireSpecimen"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.Creatures.cs`, `RpgStore.Contracts.cs`, `RpgStore.UniqueActors.cs`,
    `gk-core/src/FusionRpg.Server/UniqueActorService.cs`, `gk-core/tests/FusionRpg.Data.Tests/Saves/AiEmpireSpecimenTests.cs`

- [x] **SE4.24 — Ownership predicate at six specimen-write sites in five Data files** · M · deps: SE4.20, SE4.14 · *(spec: save-identity, "One ownership predicate")*
  - Acceptance: `RpgStore.Contracts.cs:539`, `RpgStore.Expeditions.cs:59`, `RpgStore.Fusion.cs:471`,
    `:496`, `RpgStore.Patron.cs:33`, `RpgStore.UniqueActors.cs:565` call `OwnsSpecimenUnlocked`, each
    keeping its existing refusal reason (line numbers re-measured)
  - Acceptance: each site called by save 1's human with a Zomboss specimen of save 1 is refused and its
    tables are unchanged (one test per site)
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.Contracts.cs`, `RpgStore.Expeditions.cs`, `RpgStore.Fusion.cs`, `RpgStore.Patron.cs`, `RpgStore.UniqueActors.cs`

- [x] **SE4.25 — Ownership predicate at the last two sites, and kill credit by `EmpireRef`** · S · deps: SE4.24 · *(spec: save-identity)*
  - Acceptance: species XP from a specimen source (`RpgStore.cs:3913`) and item equip
    (`ItemEquipEndpoints.cs:344`) use the predicate; a Zomboss specimen never credits the human's
    zombie species XP (test)
  - Acceptance: `ResolveLawnKillCreditPlayerUnlocked` returns the killer's `EmpireRef`; a non-human
    killer earns no kill souls, is logged, and ingest never throws
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.cs`, `gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs`, `RpgStore.Souls.cs`, the ownership test file

- [x] **SE4.26 — Specimen reads by purpose: an empire's roster vs the match's runtime** · M · deps: SE4.22 · *(spec: save-identity, "Specimen reads are classified by purpose")*
  - Acceptance: `ListUniqueActors` and the unique-actor endpoints read by `EmpireRef` (routes default to
    `HumanEmpireOf(save)`); **roster test**: a Zomboss specimen of save 1 is absent from save 1's human
    roster
  - Acceptance: `OwnersForSave(save)` feeds the atom push, the stale-`ActiveBound` sweep and kill-credit
    lookup; **runtime test**: an `ActiveBound` Zomboss specimen of save 1 keeps its pushed atoms
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AtomPush"`; Data filter `SpecimenOwnership`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.UniqueActors.cs`, `gk-core/src/FusionRpg.Server/AtomPushService.cs`, `UniqueActorService.cs`, `UniqueActorEndpoints.cs`, tests

- [x] **SE4.27 — Core ownership by empire: `SpecimenOwnershipOracle`, `KillCredit`** · S · deps: SE4.11 · *(spec: save-identity, D4, G5)*
  - Acceptance: the oracle answers `Ally` iff the registered owner's controller is `Human`, `Enemy` for
    any other registered owner, `null` when none (mechanical side decides); it needs no "my id"
  - Acceptance: **a third registered empire resolves as an enemy with no code edit** (the D4 fix made
    executable); `KillCredit` carries `EmpireRef? SpecimenOwner`
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpecimenOwnership|FullyQualifiedName~KillAttribution"`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Core/Battle/SpecimenOwnershipOracle.cs`, `KillAttribution.cs`, their tests
  - *Pure Core and callable early; lands in the unit because SE4.28 is its only production caller.*

- [x] **SE4.28 — Spawn-command ownership fields; the injector reads, never infers** · M · deps: SE4.27, SE4.22 · *(spec: save-identity, "Injector ownership"; decisions S4)*
  - Acceptance: `pvz.spawn.extra` carries `empireId` and `controller` (from the specimen's row, in the
    call that decides the deploy) beside `playerId`; `CheatState` maps `ptr → (EmpireId,
    EmpireController)` for the entity's life, never refreshed
  - Acceptance: a payload without the fields registers as unknown and the mechanical side decides, never
    `Ally`; `MatchHost` finds Zomboss's unit by `EmpireId.Zomboss`, and the elimination rule
    (`MatchHost.cs:304-310`) is deleted
  - Verify: `.\scripts\guard-injector-compile.ps1`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~UniqueActor"`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Server/UniqueActorService.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`,
    `CheatActions.cs`, `Match/MatchHost.cs`, the server test

- [x] **SE4.29 — Archived rows are never listed or selected (fixes D2)** · S · deps: SE4.12 · *(spec: save-identity, step 6, Contracts)*
  - Acceptance: `ListPlayers`, `SetCurrentPlayer` and the lowest-id fallback in
    `GetCurrentPlayerIdUnlocked` skip archived rows through `IsLiveSave`; `GET /api/players` therefore
    omits them
  - Acceptance: test: after the migration archives a Zomboss-only row, the save list has no "Zomboss"
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveEmpires"`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.cs`, `RpgStore.SaveEmpires.cs`, the store test
  - *Safe to land any time after SE4.12 (nothing is archived before SE4.20).*

- [x] **SE4.30 — Run the migration on a copy of a real save; rehearse the rollback** · S · deps: SE4.20–SE4.29 · *(spec: save-identity, migration + Rollback; parent CC2)*
  - Acceptance: **full suite green once** (sanctioned: end of a cross-module unit and immediately
    before a live check); then a copy of the owner's `dist\FusionRpg.Server\data\rpg-hot.sqlite`
    (never the original) booted by the real server build (`Start-Process` with `FUSIONRPG_DATA` pointing at the copy, on a spare port):
    report quoted, `.bak` present, human numbers read back through the normal REST reads equal the
    pre-boot reads
  - Acceptance: a second boot is a no-op (no second marker, no new rename); restoring the `.bak` over the
    copy (and deleting `-wal`/`-shm`) boots the previous build cleanly
  - Acceptance: evidence (report, the two reads, the no-op line) in the merge commit body; this is **RPG
    Server** scope, real persistence on a real record (`live-probe-standard.md`)
  - Verify: `test-fast.ps1 -AllDefault`; the operator + script steps above
  - Files: none in `src/` (evidence only)
  - **CLOSED 2026-09-20 by owner ruling** (`8aba2900f`, mirrored on the parent's row in
    `tasks/summoner-convergence-todo.md:74-79`), ticked here 2026-09-22 by `cmdc/se4-1` so the row and
    its ruling agree (routed as RECON-F1). **The migration probe itself PASSED**: `live-qa` booted a
    copy of the real save with the real server build on a spare port and read the human numbers back
    through `/api/players/current` + `/api/rpg/progression/1/summary` byte-identical, `.bak` present,
    one `.bak` after a second boot and no second migration line — `tasks/evidence-fragments/CC2-SE4.30-live-probe.md`,
    `CC2.md`. The two accepted-but-not-green clauses are **recorded, not dropped**: the full suite was
    red on four pre-existing facts (three stale corpus pins and `FamilyExpandGen --check`
    stale, all handed to their owning programs) which the ruling routes to `test-verification-boundary`
    as a knownRed registration, and the in-worktree rollback rehearsal could not run (no pre-`SaveIdentity`
    binary there); the rollback itself was rehearsed by the earlier live lane (that fragment's step 7).
    **Not deferred by this tick:** Checkpoint 4b's own boxes stay open — item 2 (closure: no null
    `empire_id`, exactly one `human` per save) is SE4.41's deliverable and item 3 (no golden moved) is
    the orchestrator's full-suite reading. Evidence: `tasks/evidence-fragments/SE4.30.md`.

### Checkpoint 4b — migration unit merged (parent CC2)
- [ ] The unit (SE4.15–SE4.30) merged to `features/mega-merge` in one merge; the owner's next
      `deploy-play` migrates the real save with a `.bak` beside it
- [x] Every save has exactly one `human` empire; no `empire_id` is null; no player row represents
      Zomboss; a Zomboss deploy past the 12th deploys — **closed 2026-09-23 (`cmdc/se4-1`)**: one human
      per save by `SaveEmpiresStoreTests.Every_save_has_exactly_one_human_empire`, no null `empire_id`
      and full Tier A closure by SE4.41's `SaveEmpireClosureTests`, no Zomboss player row by
      `A_fresh_boot_has_save_1_with_the_registry_empires_and_no_zomboss_player_row` (SE4.22 deleted
      `EnsureZombossPlayer`), and the 13th deploy by SE4.23's D6 regression test
- [ ] No golden moved, or every move explained (a move **stops the module**)

#### (c) Surfaces and hardening — safe after the merge

- [ ] **SE4.31 — REST: a save's empires, `empireId` on specimens, `?empire=` where a consumer needs it** · M · deps: SE4.30 · *(spec: save-identity, Contracts)*
  - Acceptance: `GET /api/players/{playerId}/empires` → `[{ empireId, controller }]` (`SaveEmpireDto`);
    `POST /api/players` creates the save and its empires in one transaction (REST-level test);
    `UniqueActorDto.empireId` (new; `playerId` stays and means the save)
  - Acceptance: optional `?empire=` on the unique-actor list only (the one consumer today: a Zomboss
    specimen is present under `?empire=zomboss`), default `HumanEmpireOf(save)`; a Tier B route asked for
    a non-human empire returns `409 empire_scope_not_widened`
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Players|FullyQualifiedName~UniqueActor"`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/src/FusionRpg.Contracts/Dtos.cs`, `UniqueActorDtos.cs`,
    `UniqueActorEndpoints.cs`, the server test
  - **Code + tests landed 2026-09-23 by `cmdc/se4-1`; row stays OPEN on ONE out-of-fence artefact.**
    `tasks/evidence-fragments/SE4.31.md` carries the printed readings: focused Server 25/25, E2E
    `~SaveEmpire` 2/2 through the real host, `data` sharded 1741/1741, `server` module 832/832, both
    selected guards green. **The blocker, exactly:** `UniqueActorDto.empireId` moves the live
    `POST /api/unique/actors` payload, so `FusionRpg.E2E.Tests.ContractFixtureTests` — the FE view
    contract's own drift detector — fails until `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json`
    carries `"empireId": "dave"` (bless with `FUSIONRPG_BLESS_CONTRACT_FIXTURES=1`). `web/**` is not in
    this lane's allowed paths, and weakening the fixture test instead would be the guard-widening move
    the brief forbids. **Ask: a one-file fence grant for that fixture, or the manager's own re-bless.**
  - **Two more reds this lane found and cannot file (fence), both pre-existing at HEAD:**
    `verify-change` aborts at `test: core` on `ActionsPurityGuardTests` —
    `gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionEdgeDetector.cs:85` enumerates a dictionary (`.Values`),
    added by `467cfa058` (LW1.3) which is an ancestor of HEAD and whose file is inside active session
    `cmdc/adg-f5`'s fence (`gk-core/src/FusionRpg.Core/Actions/**`); and 2 full-E2E fixture drifts
    (`ContractFixtureTests.Commander_list_fixture_matches_live_dto`,
    `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening`) whose
    fixtures were last blessed 2026-09-13 while `CommanderEndpoints.cs` changed 2026-09-19/09-21.
    Owner programs: `action-distribution-gaps` (or `lawn`), `empire-progression`, `world-map-*`.

- [ ] **SE4.32 — One aptitudes fetch covers every empire; commander listing per `EmpireRef`** · M · deps: SE4.31 · *(spec: save-identity, Contracts, X11)*
  - Acceptance: `/api/aptitudes/{playerId}` stays one fetch: the commander block is the human empire's
    pool, and every empire-keyed section covers all of `EmpiresOf(save)` (no `?empire=`)
  - Acceptance: `CommanderEndpoints.ProjectList` lists per `EmpireRef`, route default `HumanEmpireOf(save)`;
    `?empire=` only when a consumer lands (`EP commander-roster` owns `ForEmpire(EmpireRef)`)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude|FullyQualifiedName~Commander"`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `CommanderEndpoints.cs`, their tests

- [ ] **SE4.33 — SignalR: `empireId` on the three empire-scoped invalidations** · S · deps: SE4.31 · *(spec: save-identity, SignalR)*
  - Acceptance: `CreaturesUpdated` (creature, expedition and fusion endpoints), `RpgProgressionUpdated`
    and `CommandersUpdated` add `empireId`; Tier B and save-scoped events unchanged; a listener ignoring
    `empireId` keeps today's behaviour
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~SignalR|FullyQualifiedName~Creature"`; `verify-change.ps1 -Paths <files>`
  - Files: `CreatureEndpoints.cs`, `Program.cs`, `CommanderEndpoints.cs`, `ExpeditionEndpoints.cs`, `FusionEndpoints.cs`

- [ ] **SE4.34 — X9: one commander-pool key encoder** · S · deps: SE4.30, SE4.4 · *(spec: save-identity, X9)*
  - Acceptance: `AptitudeEndpoints.cs:123`, `RpgStore.AptitudePresets.cs:432` and the literal at
    `RpgStore.WorldTurns.cs:575` route through `CommanderScopeKey(EmpireRef)` (the directory's
    `AllocationScopeKey`); persisted strings byte-identical (test); `EffectOwnerKeys.Player` /
    `GateCounterHost` untouched (a different key)
  - Acceptance: coordinate with `SP layer-source-selector` (same world-turn provider): this task owns only
    the key encoder; whichever lands second rebases
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Commander"`; Data filter `Aptitude`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `RpgStore.AptitudePresets.cs`, `RpgStore.WorldTurns.cs`, directory file, a test

- [ ] **SE4.35 — "The save's human empire", typed: Data and Core sites** · S · deps: SE4.34 · *(spec: save-identity, the hand-off table)*
  - Acceptance: `RpgStore.Aptitudes.cs:232`, `:266`, `RpgStore.WorldTurns.cs:573` compare with
    `HumanEmpireOf(save)`; `SpeciesAllocationSource.cs:114` takes an injected `humanEmpire`;
    `SpeciesAllocation.cs:29` stays `EmpireId.Dave` (commented why); per-site meaning in the commit body
  - Acceptance: behaviour byte-identical (human members get the human pool, others Empty)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocation"`; Data filter `Aptitude`; `verify-change.ps1 -Paths <files>`
  - Files: `RpgStore.Aptitudes.cs`, `RpgStore.WorldTurns.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs`, `SpeciesAllocation.cs`, a test

- [ ] **SE4.36 — "The save's human empire", typed: Server and injector sites** · S · deps: SE4.35 · *(spec: save-identity, the hand-off table)*
  - Acceptance: `CommanderEndpoints.cs:78`, `:93`, `ItemEquipEndpoints.cs:307`, `PlayerEmpireCommanders.cs:19`
    ask `HumanEmpireOf(save)` through the directory; `CheatState.cs:183` takes an injected `humanEmpire`
  - Acceptance: no `EmpireId.Dave` left in `src/` outside well-known-value declarations, `SpeciesAllocation.cs:29`,
    the new-save registry and the migration's historical step (grep quoted in the commit body)
  - Verify: `dotnet build src\FusionRpg.Server`; `.\scripts\guard-injector-compile.ps1`; `verify-change.ps1 -Paths <files>`
  - Files: `CommanderEndpoints.cs`, `ItemEquipEndpoints.cs`, `PlayerEmpireCommanders.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`

- [ ] **SE4.37 — Tier B typed, batch 1: items, charms, loot** · M · deps: SE4.30 · *(spec: save-identity, Tier B)*
- [ ] **SE4.38 — Tier B typed, batch 2: materials, souls, summons, fusion, `player_species`** · M · deps: SE4.37
- [ ] **SE4.39 — Tier B typed, batch 3: patron, contracts, expeditions, delves, domains, cache retrieval/decay** · M · deps: SE4.37
- [ ] **SE4.40 — Tier B typed, batch 4: presets, respec, titles, PvZ stats, player commander** · M · deps: SE4.37
  - Acceptance for SE4.37–4.40: every public store method of the batch takes `EmpireRef` and calls one
    shared `RequireHumanEmpire(owner, table)` (added in SE4.37), which throws `EmpireScopeNotWidened`;
    **signature change only, no SQL change**; callers pass `EmpireRef(save, HumanEmpireOf(save))`
  - Acceptance: per batch, a non-human call throws and the table's row count is unchanged; if a batch's
    callers exceed five files, split it per store before starting
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~<store names>"`; `.\scripts\guard-dal.ps1`; `verify-change.ps1 -Paths <files>`
  - Batches 2–4 are parallel-safe with one another (disjoint stores)

- [x] **SE4.41 — Closure contracts: every Tier A owner and every world faction resolves to a save's empire** · S · deps: SE4.30 · *(spec: save-identity, Contracts tests)*
  - Acceptance: every Tier A `(save_id, empire_id)` exists in `rpg_save_empires`, and no `empire_id` is
    null; every `rpg_world_factions.faction_id` that names an empire is an empire of its world's save
  - Acceptance: contract tests only; no row count asserted anywhere
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveEmpires"`; `verify-change.ps1 -Paths <files>`
  - Files: `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveEmpireClosureTests.cs` (new)
  - **Done 2026-09-23 (`cmdc/se4-1`).** Six facts, two closure checks written as violation LISTS (never
    counts) plus the planted violation each check exists to catch: a null `empire_id`; a specimen owned
    by an empire no save seeded; progression and ledger rows owned by the same; and a world belonging to
    an unseeded legacy save whose authored template factions name `dave`/`zomboss`. Non-vacuity is
    asserted separately (each classified table carries rows; a seeded save's world really does name its
    own empires), so the green cases are not passing over an empty database. Read:
    `Passed! - Failed: 0, Passed: 6, Total: 6` for
    `--filter "FullyQualifiedName~SaveEmpireClosure"`. Evidence: `tasks/evidence-fragments/SE4.41.md`.

- [ ] **SE4.42 — `guard-open-identity` gains I3 and I4** · S · deps: SE4.4, SE4.25, SE4.22 · *(spec: save-identity, Guard I3/I4)*
  - Acceptance: **I3** no `players` row looked up by `Name` in `src/`, and `EnsureZombossPlayer` /
    `ZombossPlayerName` do not exist; **I4** no `<actor|row|specimen>.PlayerId ==`/`!=` in
    `gk-core/src/FusionRpg.Data` or `gk-core/src/FusionRpg.Server` outside `OwnsSpecimenUnlocked`
  - Acceptance: falsifiers plant each pattern and fail; the non-specimen `PlayerId` comparisons I4 would
    hit today (presets, delves, expeditions by their own row) are measured first and either scoped out
    by the rule's shape or listed in the guard with the reason; registry row stays `gating`
  - Verify: `.\scripts\guard-open-identity.ps1`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~OpenIdentity"`
  - Files: `scripts/guard-open-identity.ps1`, `gk-core/tests/FusionRpg.Guard.Tests/OpenIdentityGuardTests.cs`, `gk-core/scripts/enforcement-registry.v1.json`

- [ ] **SE4.43 — Docs, and `save-identity` closes** · S · deps: SE4.31–SE4.42 · *(spec: save-identity, Project structure, Success criteria)*
  - Acceptance: `data-architecture.md` (the save/empire model, the `xp-*` archive rule, and §2's
    *"`EnsureColumn` … only"* line pointing at the S3 row), `docs/database/schema.md`,
    `docs/protocol/rest.md` (`{playerId}` = the `SaveId`, the new route and `?empire=`),
    `docs/protocol/signalr.md`
  - Acceptance: the SE4.11 ledger row struck with its SHA; the keying-sweep mismatches 1–3 closed by their
    owners or still listed in the spec; **full suite green once** (module end, cross-boundary), no golden
    moved or every move explained
  - Verify: `python scripts/audit-doc-citations.py` on the touched docs (0 HIGH); `test-fast.ps1 -AllDefault`
  - Files: the four docs, `docs/architecture/stub-register.md`

### Checkpoint 4c — `save-identity` closed
- [ ] Every success criterion in `spec-save-identity.md` ticked, with the SHA that met it
- [ ] `guard-open-identity` I1–I4 gating
- [ ] Consumers in `species-progression` and `empire-progression` build against these seams with no second key

- [ ] **SE4.5 — `guard-file-budget.ps1` (F1–F3)** · S · deps: SE0.5
  - Acceptance: budgets 1,500 C# / 600 non-test TSX as commented structural limits; exempt marker
    plus registry list (empty); falsifiers; registry `backlog`

- [ ] **SE4.6 — Split Data: `RpgStore.cs`, `RpgStore.UniqueActors.cs`, `RpgStore.Delve.cs`** · M · deps: SE4.5, SE4.4, SE4.43
- [ ] **SE4.7 — Split Server: `Program.cs`, `DebugEndpoints.cs`, plus a boot smoke** · M · deps: SE4.5, SE4.4, SE4.43
- [ ] **SE4.8 — Split FE: `LawnPage`, `RelicsLayer`, `RpgProgressionPage`, `CheatsPage`, `WorldStage`** · M · deps: SE4.5
- [ ] **SE4.9 — Split Injector: `CheatCommandRunner`, `DebugActions`, `GameHooks`, plus a live boot** · M · deps: SE4.5, SE4.4, SE4.43
  - Acceptance for SE4.6–4.9: move-only (member-union comparison shows zero added or removed members);
    the kind's verification bar from the spec; each file ≤ budget; no file another session is editing
    (session records checked first)

- [ ] **SE4.10 — `file-budget` gates** · XS · deps: SE4.6–SE4.9
  - Acceptance: 0 files over budget; registry `gating`; SR-23 struck

### Checkpoint 4 — program close
- [ ] Registry holds **zero** `status: backlog` rows
- [ ] Full suite green, quoted
- [ ] SR-19..SR-23 and the `save-identity` row (SE4.11) struck with SHAs
- [ ] Owner shown: the phase 1 close item, T4.4 S7 (deferred), and Q1–Q5 with the defaults that
      shipped

---

## Wave 5 — action base stats (idea phase; owner ruling 2026-09-18)

Ideal: [../docs/architecture/action-base-stats-ideal.md](../docs/architecture/action-base-stats-ideal.md).
Its build tasks are written **when its spec lands**, never guessed ahead of it.

- [x] **SE5.1 — Spec `action-base-stats` from its ideal** · M · deps: SE1.7
  - **Done 2026-09-18, in its own program on the owner's narrowing.** Both questions are closed: the lawn
    already runs the basic action (lawn-combat-wire T10) and moves to the action base; skills take the
    rung's `qPowerMilli` (the owner's "deterministic function" ruling). The specs live at
    `docs/architecture/action-enrich-map.md` (`action-base`, `lawn-action-base`), not at the path named
    below. SE1.7 is no longer a prerequisite: `action-base` stops *reading* `atk`; deleting it stays SE1.7's.
  - Acceptance: the ideal's two open questions answered by the owner (lawn damage source; skill base
    from rung versus authored), then `docs/architecture/solid-enforcement/spec-action-base-stats.md`
    written against the shipped code, with a self-audit and gap analysis like the other 14; the build
    tasks live in `action-enrich-todo.md` (`AE1.1`–`AE2.4`, not SE5.2…); the golden re-bless is `AE1.5` (parent H1)
  - Files: the spec, this todo, the map's module row

### Checkpoint 5
- [ ] Battle, Delve and siege damage read the action's base; `BattleActorSetup.Atk` no longer feeds
      damage; goldens re-blessed once with the reason written down

- [ ] **SE4.4-followup — `PlayerEmpireCommanders.ForPlayer` lost its last production caller to
  `commander-roster`.** **Filed by:** lane `cmdc-ep2-1` (`empire-progression`), 2026-09-20, when EP3.3
  projected the commander list from `ICommanderRoster.ForEmpire`.
  **Cause:** `CommanderEndpoints.ProjectList` was its only production caller
  (`gk-core/src/FusionRpg.Server/CommanderEndpoints.cs:77` before EP3.3), and the list now reads
  `ICommanderRoster.ForEmpire(new EmpireRef(SaveId, HumanEmpireOf(save)))` — the interface this module's
  own spec asked `commander-roster` to provide. Its only remaining reference is its own test
  (`tests/FusionRpg.Core.Tests/Commanders/PlayerEmpireCommandersTests.cs`), plus a comment in
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:210`.
  **Fix (a choice for this module, not for the lane that filed it):** either retire the helper and its
  test — the roster's `ForEmpire` answers the same question from the same directory — or keep it and give
  it a caller, saying which. Left in place rather than deleted from another program's surface.

- [ ] **SE3.7-followup — `tracked_files()`/`deleted_paths()` in `audit-doc-citations.py` are
  cwd-sensitive, so an audit launched from a subdirectory silently finds zero documents.**
  **Filed by:** lane `seed-corpus-1` (`seed-corpus`), 2026-09-21, while verifying `item-seedgen`
  ISG7-F2.
  **Cause:** `scripts/audit-doc-citations.py:232` runs `git ls-files --cached --others
  --exclude-standard` with no `cwd=`, and `:241` runs `git log --all` the same way, so both resolve
  against the PROCESS working directory. `git ls-files` from a subdirectory returns
  **subdirectory-relative** paths, so `audit("docs/")` launched from `gk-forge/tools/seedsmith` returns
  `doc_count == 0` and the real check then reports "clean" over nothing — a green that looked at
  nothing, the exact failure mode the audit's own D-checks exist to prevent.
  **Measured:** `cd gk-forge/tools/seedsmith && PYTHONPATH=. python -m pytest
  tests/test_audit_doc_citations.py::RealTreeTests` fails `0 not greater than 0`; the same test passes
  from the repo root. `scripts/verify-change.ps1` runs its own audit from the repo root, which is why
  this never surfaced there.
  **Fix (this module's call, not the filing lane's):** pass `cwd=REPO_ROOT` (or `--full-name`) in both
  `tracked_files()` and `deleted_paths()`, so the checker is cwd-independent.
  A test-side chdir in `gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py:316` was tried and
  **reverted**: that file maps to the `doc-citations-guard` boundary, whose `guard: doc-citations`
  step runs `scripts/audit-doc-citations.py --strict` over the WHOLE repo, and the tree carries a
  pre-existing **20 HIGH** backlog (D1 918 findings/18 HIGH, D2 13/1, D3 58/1, every one under
  `docs/architecture/**`). Changing the test therefore aborts `verify-change.ps1` at a boundary no
  lane can repair (`docs/**` is outside most lanes' fences) — so the fix belongs in the script, not
  beside it.

- [x] **RECON-F1 — SE4.30 is unticked under an owner ruling that already closes it** · XS · *(routed by the manager 2026-09-22 from `tasks/reports/backlog-reconciliation-20260921.md` §9, which lists it and deliberately does not file it: the lane's fence is `tasks/reports/**`.)*
  `tasks/solid-enforcement-todo.md:568`. The ruling landed in `features/mega-merge` as a **commit**, not as a row edit, so the row still reads open. Tick it or add the closure note so the row and its ruling agree.
  **Closed 2026-09-22** (`cmdc/se4-1`): SE4.30 is ticked with the closure note naming ruling commit
  `8aba2900f` and both recorded clauses. The row id `SE4.30` is still present (grepped after the tick).

---

## Findings carried by lane `cmdc/se4-1` — filed here because the owning todos are outside this lane's fence

The brief asks for a row in the OWNING program's todo. This lane's allowed paths are
`tasks/solid-enforcement-*` only, so a row there is impossible without failing the run's path check.
Routed to the manager instead, with `file:line` and the cause read, as in the SE4.31 row above.

- **`F-CORE-PURITY` — `verify-change` cannot run to completion for any `Contracts`/`Core` path.**
  `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` → `Failed: 1, Passed: 9637, Total: 9638`;
  `ActionsPurityGuardTests.Action_sources_contain_no_wall_clock_ambient_rng_or_dictionary_enumeration`
  names `gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionEdgeDetector.cs:85 → .Values`. Cause read: the
  `WindowCount` getter sums `_byPtr.Values` — a dictionary enumeration, which that guard forbids in the
  action layer. Introduced by `467cfa058` ("feat(lawn): LW1.3 … ExhaustionPolicy", 2026-09-23, an
  ancestor of HEAD) whose lane verified with a `~Exhaustion` filter and so never ran the purity guard
  in the same project. **The file is inside active session `cmdc/adg-f5`'s fence
  (`gk-core/src/FusionRpg.Core/Actions/**`)**, so this lane must not repair it. Owner: the LW1.3 lane
  (`lawn`/`lawn-combat-wire` numbering) with `action-distribution-gaps` holding the reconciliation.
  Blast radius: `verify-change.ps1` aborts at `test: core` and every later check in the plan is skipped
  for every lane that touches `gk-core/src/FusionRpg.Contracts/**` or `gk-core/src/FusionRpg.Core/**`.
- **`F-E2E-FIXTURES` — two full-E2E contract-fixture drifts, pre-existing.**
  `ContractFixtureTests.Commander_list_fixture_matches_live_dto` and
  `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening` fail on
  `Failed: 3, Passed: 273, Total: 276` (the third IS this lane's SE4.31 blocker, below). Both fixtures
  were last blessed 2026-09-13 (`f2f67caa9`) while `gk-core/src/FusionRpg.Server/CommanderEndpoints.cs` changed
  on 2026-09-19 (commander-identity SE4.2/SE4.3) and 2026-09-21 (EP3.3). Owner:
  `empire-progression` (commander list) and the world-map program (turn fixture). Fix is a re-bless
  under `FUSIONRPG_BLESS_CONTRACT_FIXTURES=1`, in `gk-web/web/fusion-rpg-web/e2e/fixtures/**` — outside this
  lane's fence.
- **`F-DOC-CITATIONS-HIGH` — `guard-doc-citations.ps1 -Strict` exits non-zero at HEAD.** 2 HIGH, both
  D3 (ambiguous basename): `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76`
  citing `fill.py:293-302` and `fill.py:532-540` where two files share the basename. Cause read: the
  citation is a bare basename, so the audited line number cannot be resolved to one file. Owner: `loam`
  (`docs/architecture/loam-relics-and-wonders/**`). Not this lane's file; measured 1688 documents /
  25695 citations checked.
- **`F-TODO-LINE-CITATIONS` — seven `docs/` citations into `tasks/solid-enforcement-todo.md` point at
  the wrong line, and were already wrong before this lane touched the file.** Measured at `42f371afb`
  (the integration head this lane fast-forwarded to, before any of its edits): `:116` is SE1.5's row
  though `action-enrich/spec-action-base.md:150` cites it as SE1.6; `:313` is blank though
  `action-enrich/spec-action-base.md:5` and `action-enrich-map.md:13` cite it as SE5.1's "done" note;
  `:634` is inside SE4.32's acceptance though `trade-network/audit-2026-09-20-global.md:136`,
  `trade-network/landing-order.md:323` and `trade-foundation/spec-material-ledger.md:129` cite it as
  SE4.38. Same class at `spec-action-base.md:150` (`:127-131` → SE1.6 not SE1.7),
  `spec-ledger-keys.md:38` (`:339-348` → not the SE4.11 row) and `sector-yield/spec-banking-fact.md:342`
  (`:352` → SE4.11's acceptance, not SE4.38). Cause read: every task tick appends acceptance notes, so
  a line number into a live program todo rots within one wave; the audit's D2 ("line past end of file")
  does not catch it because the lines still exist. **Fix is a doc edit in `action-enrich` and
  `trade-network`, both outside this lane's fence; the durable fix is to cite a task id
  (`SE4.38`), never a line number, into a live todo.**
