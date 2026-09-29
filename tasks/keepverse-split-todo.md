# Todo: keepverse-split
Plan: [keepverse-split-plan.md](keepverse-split-plan.md). Status lives here only.
Rule D5: migrated repos are **kvsplit output**. No task edits staged or imported files by hand.
## Phase 0 — decide
- [x] **KS0.1 ADR.** Done `7dcbf38d` (decisions.md row + PRINCIPLES + software-architecture §11). `docs/architecture/decisions.md` row: root + six sub-repos, D1-D9, direction contract,
  tool placement rule, manifest+lock, sibling paths. Point `docs/PRINCIPLES.md` and
  `software-architecture.md` §1/§11 at it. *Accept:* `audit-doc-citations.py --scope` clean. **Gate G1.**
## Phase 1 — build kvsplit (`Keepverse/tools/kvsplit/`, Python, seedsmith shape, committed to gk-workflow)
- [x] **KS1.0 wiring.** Package skeleton in the Keepverse root, `pyproject.toml` exact pins,
  `requirements.lock`, pytest config, `python -m kvsplit` entry, root CI workflow `kvsplit.yml`.
  *Accept:* clean clone of gk-workflow + lockfile install runs the suite green.
- [x] **KS1.1 `source`.** Tracked list + blob bytes at a SHA via `git ls-tree -r` / `cat-file --batch`.
  *Accept:* reads a pinned SHA while the working tree is dirty and returns the committed bytes.
- [x] **KS1.2 `rules`.** Parse ownership manifest, transform config, templates; missing/mistyped field throws.
- [x] **KS1.3 `classify`.** Exactly-one-target (+ pack for gk-data); unmatched / double-matched / dead rule ⇒ residue.
- [ ] **KS1.4 `graph`.** csproj/slnx/props/package.json/pyproject graph; direction-contract violations ⇒ residue.
  *Partial:* MSBuild ProjectReference + host-assembly references done; `package.json`/`pyproject.toml` edges not yet.
- [ ] **KS1.5 `transform`.** Registry + first transforms: MSBuild path rewrite (XML-aware), per-repo
  solution generation, citation prefixing, templated `AGENTS.md`/`.gitignore`/props, CI split.
  *Accept:* each transform pure, pytest per transform, unparseable input ⇒ residue.
  *Partial:* MSBuild paths, props inject, solution split, markdown + comment citations, root `.gitignore`
  template, per-repo `AGENTS.md` templates (gk-workflow `c60a1dc`) done. The CI workflow split is not built:
  `.github/workflows/*` references are in the residue queue (`path-literal-moves`).
- [x] **KS1.6 `scan`.** Cross-boundary text references (hard-coded paths, doc-reading tests, slnx
  root discovery) ⇒ residue with file:line.
- [x] **KS1.7 `stage`.** Staging trees + `report.json` + `residue.json`, stable residue ids.
  *Accept:* two runs from the same inputs are byte-identical (hash equal).
- [x] **KS1.8 `check`.** References resolve in layout; direction contract; Unity only in gk-fusion;
  no seed/generated-shaped file in any public repo;
  reconciliation `Σ targets + drop == tracked` (printed, not pinned).
- [x] **KS1.9 `apply`.** Snapshot commit into a sub-repo; refuses dirty/diverged repo; message carries
  source SHA, tool version, rules hash.
**Phase 1 status (2026-09-19):** built and committed in gk-workflow `8004c3a` + `9a48e08` (LF pin so the
rules digest is clone-independent). 41 pytest green locally. Transforms: `msbuild-paths`,
`msbuild-props-inject`, `solution-split`, `comment-citations`, `markdown-citations`. Known gaps, stated:
`graph` reads MSBuild projects only (`package.json`/`pyproject.toml` edges are not checked yet); the root CI
workflow is written but not yet run (nothing pushed); a clean-clone install was not run.
## Phase 2 — author rules, run dry
- [x] **KS2.1** Ownership manifest covering all targets, reason field per tool rule (placement rule).
  Seeds: forge ← `seedsmith`, `Creature*Gen/Emit/Import/Dump`, `FamilyExpandGen`, `TreeBinder`,
  `PassiveTreeRosterGen`, `AtomImporter`, `ItemSeedValidator`; core ← `CombatSim`,
  `DominanceBaseline`, non-live `Prove*`, `*Probe`, `tuning`; fusion ← `LawnCombatObserver`,
  `ProveLiveProbe`, `debug-mcp`, `live_test`, `sprite-debug`, `GameMetaDump`, `AlmanacSeedBackfill`,
  `FusionRpg.PackSmoke`, injectors, Launcher, `game-profiles*`, `gk-fusion/docs/injector/**`;
  gk-data `packs/fusion` ← all of `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**`; gk-core ← `gk-core/data/tuning/**`.
  Each tool verified by reading its output path.
- [x] **KS2.2** Transform config + templates for each repo.
- [x] **KS2.3** First dry `stage` at HEAD; publish `residue.json` grouped by kind as the Phase 3 queue.
**Phase 2 status:** rules in `Keepverse/tools/kvsplit/rules/`. Dry run at legacy `7dcbf38d`: 11,026 tracked,
reconciliation balanced, 2 dropped; `verify` = two runs byte-identical (same output digest and residue ids).
Residue queue (a reading, re-run for current): `direction-violation` 5 (Core.Tests/Data.Tests reference forge
tools), `repo-root-discovery` 6, `path-literal-moves` 940 in 467 files (largest: `gk-forge/tools/seedsmith` 392,
`scripts` 159). Regenerate: `python -m kvsplit stage --source <legacy> --rev <sha> --out <Keepverse>\.staging`.
## Phase 1b — move-first tools (owner ruling D10, 2026-09-19)
- [x] **KS1.10 `hash`** — sha256 manifest of the legacy tree at the SHA (from git) or of the moved workspace.
- [x] **KS1.11 `lossy-check`** — every legacy file placed with its staged bytes or dropped by rule; every
  moved file explained (report row, template, preserve glob); source drift caught.
- [x] **KS1.12 `index`** — every file that now exists + the legacy -> new move map (primary placements only).
- [x] **KS1.13 `reindex`** — rewrites document path references (`rules/reindex.v1.json`); bare slugs are
  in-app routes and left alone; links already broken before the move are reported apart (`preExisting`);
  the rest that cannot be resolved are `stale` — the agents' queue. Idempotent.
- [x] **KS1.14 `apply` hardening** — preflights every repo before writing any (no half-applied workspace);
  `core.longpaths`; extended-length paths on Windows; force-adds planned files so a copied `.gitignore`
  cannot drop a tracked legacy file; `--allow-residue` for the move-first flow.
- [x] **KS1.15 Rehearsal** — full Phase 4-5 flow from the real legacy repo into a scratch workspace; lossy
  check must be zero. Done 2026-09-19: 0 findings over 11,133 legacy files; reindex 0 stale, 128 links already
  broken before the move (reported apart); second run a no-op. Four rehearsal-found defects fixed first.
## Phase 3 — pre-move reduction (optional under D10, not a gate)
- [ ] **KS3.0** Owner charter for reconcile agents (runtimes, models, budget) recorded before any worker.
- [x] **KS3.0a Tool precision pass (no agents).** Packs mirror the legacy root; docstrings, block comments and
  research JSON treated as citations; resolver tokens; output-relative runtime code; wrong `FusionRpg.slnx` token
  dropped. gk-workflow `8e63f07`..`4009cd3`, 45 tests. Residue at `7dcbf38d`: 951 -> 383
  (`path-literal-moves` 285, `content-root-consumer` 93, `direction-violation` 5).
- [x] **KS3.0b L1 resolvers** (legacy `bdb2a9a1`): `workspace_roots.py` (seedsmith) + `gk-core/scripts/lib/keepverse_roots.py`,
  `scripts/lib/KeepverseRoots.ps1`, `gk-core/tests/Shared/KeepverseRoots.cs` linked into every `*.Tests`; tokens registered in
  kvsplit (gk-workflow `6100d93`).
- [x] **KS3.0c L3 first batch** (legacy `50d174e0`): 45 C# test content readers routed through `ContentRoot`/`CoreRoot`;
  563 tests across 7 projects pass.
- [x] **KS3.0d Scanner accuracy** (gk-workflow `35a706c`): paths spelled as separate string literals
  (`Path.Combine(dir, "src", "FusionRpg.Injector")`, `ROOT / "data" / "seed"`) now detected; `accept[]` rules
  with mandatory reasons. This surfaced a hidden class: **169 test files find the repo root by the
  `gk-fusion/src/FusionRpg.Injector` directory**, which will not exist in gk-core.
  Residue at legacy `50d174e0`: 926 in 576 files (seedsmith 213, Core.Tests 152, Guard.Tests 137, scripts 131).
- [ ] **KS3.1** One agent brief per residue kind; fix only via `rule` / `transform` / `source`.
  Expected kinds from the plan: pack-path routing in generators and runtime data readers, `..\..\data`
  sites outside csproj, slnx repo-root discovery in tests, 17 doc-reading test files, core tests reading
  real content (fixture in gk-core vs `ContentIntegration` category).
  Lanes (each re-runs `kvsplit stage` and closes only its own ids):
  - **L1 resolvers (first, blocks L2-L4):** implement the plan's resolver contract once per language
    (Python module in seedsmith + one for `scripts/*.py`, C# helper shared by test projects, PowerShell
    function), then add their tokens to `scan.v1.json` `resolvers`.
  - **L2 seedsmith:** route `REPO_ROOT / "data/..."` through `content_root()` / `core_root()`.
  - **L3 C# tests + tools:** route `RepoRoot()` content/tuning reads through the helpers; decide per test
    fixture vs `ContentIntegration`; fix the 5 `direction-violation` references (move those tests to gk-forge).
  - **L4 scripts + CI:** PowerShell/Python scripts through the resolvers; split `.github/workflows/*` per repo.
    **L4's Python half LANDED 2026-09-23 (lane `findings-2`) — 4 of the 6 consumers, and the other 2 are blocked
    by a contract gap filed as KS-F3 below.** Measured first: `scripts/**/*.py` is 13 files, 7 of which locate a
    repo root by a private `..` walk (`__file__`-relative), one of those being the resolver itself. Routed
    through `gk-core/scripts/lib/keepverse_roots.py`, each path to the root the contract names for it:
    `audit-program-pipeline.py` and `fix-doc-citations.py` → `workspace_root()` (`docs/`, `tasks/`, `scripts/`);
    `audit-reader-census.py` → `core_root()` for `gk-core/data/tuning/**` + `src/**` and `content_root()` for
    `gk-data/packs/fusion/data/seed/derived-stats/catalog.json`; `verify-golden-attribution.py` → `core_root()` for `src/**` +
    `tests/**` and `workspace_root()` for `docs/**`. Two of them needed TWO roots, which is the point — one
    private walk was serving both. Evidence, per script, is the same command's output **byte-identical before
    and after** (`python scripts/<name>.py`, exit 0 in all four, `diff` empty), so this is behaviour-preserving
    in the legacy layout while now carrying the `core_root(` / `content_root(` / `workspace_root(` tokens
    `rules/scan.v1.json` `resolvers` looks for; no private `..` root walk remains in any of the four.
    **Still open in L4:** `guard-population-pin.py` and `guard-vocabulary-mirror.py` (KS-F3), and the
    `.github/workflows/*` split (out of this lane's fence — a protected pipeline path).
  - **L3b injector-marker roots (169 files):** a test that only needs the repo root switches to `CoreRoot`;
    a Guard test that reads `gk-fusion/src/FusionRpg.Injector/**` source moves to a gk-fusion guard test project
    (ownership rule + csproj template), since that source moves there.
    **L3b's first slice LANDED 2026-09-23 (lane `findings-2`) — 9 files, and the classification is now a
    measurement rather than a per-file read.** Re-measured at this head: **235** `tests/**/*.cs` files name the
    injector directory at all, and of those **172 mention it exactly once** — i.e. the only mention is the
    root-finding helper's marker, which is what "a test that only needs the repo root" means mechanically.
    The other 63 mention it more than once and are the subject case (L5: they move to gk-fusion or read via
    `WorkspaceRoot`), so they are not this lane's to route. First slice taken: `FusionRpg.Core.Tests`' nine
    CORE-only files — `Actions/ActionTagPreferenceTests.cs`, `Battle/WaveCatalogLoaderTests.cs`,
    `Combat/NamingBanTests.cs`, `Creatures/CreatureRankTuningTests.cs`, `Creatures/Fusion/FusionRankFloorTests.cs`,
    `Creatures/RarityTuningCoverageTests.cs`, `Delve/Encounter/BossBuildTests.cs`, `Items/DropVolumeTests.cs`,
    `Items/SetRequirementReconciliationTests.cs`. Each helper body (the `DirectoryInfo(AppContext.BaseDirectory)`
    walk that returned on `gk-fusion/src/FusionRpg.Injector`) is now `return FusionRpg.TestSupport.CoreRoot.Path;` — the
    resolver `Directory.Build.props` already compiles into every `*.Tests` project — so the file reads
    `gk-core/data/tuning`/`src` from the engine root and survives the injector source moving to gk-fusion. Verified by
    the project's own suite: `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` -> `Passed! - Failed: 0,
    Passed: 9705, Skipped: 0, Total: 9705` (4 m 13 s). No marker string remains in any of the nine, so the
    172/63 reading stays meaningful for the next slice.
    **Still open in L3b, named exactly:** the other 163 pure-signal files, in 13 projects. Twelve of the
    twenty-one `FusionRpg.Core.Tests` files are the reason this is per-slice work rather than one sweep: they
    need TWO roots (`gk-data/packs/fusion/data/generated/creatures/**` or `gk-data/packs/fusion/data/seed/**` is CONTENT while `src/**` is CORE), so the
    helper cannot be swapped for one root — each needs its content paths moved to `ContentRoot.Path`. The
    same shape will repeat in `FusionRpg.Server.Tests` (53), `FusionRpg.Guard.Tests` (28),
    `FusionRpg.Core.Items.Tests` (24) and `FusionRpg.Data.Tests` (19).
    **L3b's second slice LANDED 2026-09-24 (opencode `findings-2d` lane restaged + manager close): the twelve
    two-root `FusionRpg.Core.Tests` files now resolve content paths via `ContentRoot.Path`
    (`Creatures/BuildFavourMeasureTests.cs`, `ConcreteSpeciesSeedReaderTests.cs`,
    `CreatureAdmissionTests.cs`, `CreatureRecipeCatalogTests.cs`, `Fusion/RealCorpusFixture.cs`,
    `Patron/PatronAbsorptionGridEqualityTests.cs`, `SpeciesBuildPlanCatalogRealFileTests.cs`,
    `SpeciesBuildPlannerTests.cs`, `SpeciesCatalogDiffTests.cs`, `SpeciesExpanderTests.cs`,
    `Delve/Encounter/RealAnchorCorpusFixture.cs`, `Match/UniqueEquipmentAtomMappingTests.cs`).
    Merged-head gate: `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` -> `Failed: 0, Passed: 9740`.
  - **L5 web + Guard.Tests + rest:** relative `../../data/...` imports in web tests, Guard tests reading
    injector files (move to gk-fusion or read via `WorkspaceRoot`).
- [ ] **KS-F3 — the resolver contract names three roots, and two `scripts/*.py` consumers read a fourth** · S ·
  **Filed by:** lane `findings-2`, 2026-09-23, while landing L4's Python half (KS3.1). **Cause, measured:**
  `tasks/keepverse-split-plan.md`'s resolver table and `Keepverse/tools/kvsplit/rules/scan.v1.json`'s
  `resolvers` node name exactly three roots — `gk-data` (`content_root\(|ContentRoot\.|Get-ContentRoot`),
  `gk-core` (`core_root\(|CoreRoot\.|Get-CoreRoot`) and `root`
  (`workspace_root\(|WorkspaceRoot\.|Get-WorkspaceRoot`) — and none of them is the **forge** repo. Two of the
  six Python consumers read forge paths as well as core ones, so they cannot be routed through the contract as
  it stands: `gk-core/scripts/guard-population-pin.py:47` `SCAN_ROOTS = ("tests", "gk-forge/tools/seedsmith/tests")` and
  `:115` `repo_root / "tools" / "seedsmith" / "seedsmith"`; `gk-core/scripts/guard-vocabulary-mirror.py:266`
  `repo_root / "tools" / "seedsmith"` (the Python mirror it compares the C# enums against). Each still carries
  a private `..` walk (`:38` and `:250` respectively). **Acceptance:** either the resolver contract gains a
  fourth root (`forge_root()` / `KEEPVERSE_FORGE_ROOT`, mirrored in `gk-core/scripts/lib/keepverse_roots.py`,
  `gk-forge/tools/seedsmith/seedsmith/workspace_roots.py` and kvsplit's `resolvers`) and those two scripts route through
  it, or the ruling is that they move to gk-forge and their in-repo copies go with them. **Owner:**
  `keepverse-split` for the contract, with `seedsmith`/`forge` as the callers. **Verify:** after the ruling,
  `python gk-core/scripts/guard-population-pin.py` and `python gk-core/scripts/guard-vocabulary-mirror.py` exit 0 with output
  identical to today's, and `grep -n "parent.parent" scripts/guard-*.py` is empty.
- [ ] **KS3.2 Checkpoint A (revised for D10).** Tools built; rehearsal lossless; `verify` byte-identical.
  Residue need not be empty: it moves with the tree and is reconciled in Phase 6.
---
**⛔ HOLD — Gate GM.** Owner ruling 2026-09-19: prepare the tools and plan, then stop. Phases 4-7 start
only on the owner's explicit "start migration" command. Until then nothing is applied to Keepverse repos.
## Phase A — consolidate to one branch (owner's precondition; the authoritative plan is
`Keepverse/docs/keepverse-migration-plan.md` §2, which supersedes the one-line KS4.1 below)
- [ ] **KS-A** Source repo holds exactly one `main` branch; every other local branch, remote
  branch and linked worktree deleted. Owner ruling 2026-09-28: the migration does not begin
  until this holds. Phase A §2 of the authoritative plan carries the per-step evidence:
  A.1 freeze the inputs (push 4 unpushed commits, resolve the 1 dirty untracked file), A.2
  close the 3 sessions still holding active fences, A.3 decide the 4 branches holding
  unmerged work (`ps1ban/l3-checks` 3 commits, `ps1ban/l4-artifacts` 1,
  `rescue/corpus-bcu211-itemseedgen-run` 1, `origin/worktree-rift-gate-20260914` 1),
  A.4 merge `features/mega-merge` into `main` behind a dry run, A.5 remove worktrees BEFORE
  branches, A.6 six checked exit criteria.
## Phase 4 — freeze and move
- [ ] **KS4.1** `features/mega-merge` merged to `main`; lanes closed; import SHA recorded here.
  Satisfied by **KS-A**; this line stays as the todo's own record of the import SHA, which is
  re-read after Phase 3 because Phase 3 still lands source commits.
- [ ] **KS4.2** `hash --source` at the import SHA; `stage`; `apply --confirm-migration-start --allow-residue` into
  gk-data, gk-fusion, gk-forge, gk-assets, gk-core, root (one snapshot commit each).
- [ ] **KS4.3** Root `workspace.json`, first `workspace.lock.json`, `scripts/bootstrap.ps1` — emitted by kvsplit
  templates, not hand-written.
## Phase 5 — lossy check, index, reindex
- [ ] **KS5.1** `hash --workspace`; `lossy-check` = **zero findings**, else roll back the import commits and fix the tool.
- [ ] **KS5.2** `index`; `reindex` dry run reviewed; `reindex --apply`; one commit per repo.
## Phase 6 — agent final check and reconcile — Checkpoint B
- [ ] **KS6.0** Owner charter for reconcile agents (runtimes, models, budget) recorded before any worker.
- [ ] **KS6.1** Queue = carried residue + reindex `stale` + per-repo build/test failures. Fix by source commits in
  the new repos or rule/tool changes with a documented re-run.
- [ ] **KS6.2 Checkpoint B.** Full suite per repo; every generator `--check` byte-identical to the import SHA;
  goldens unchanged; live lawn from the Keepverse layout + real `/api/aptitudes/unique/allocate` read back through
  the normal path.
## Phase 7 — cutover
- [ ] **KS7.1** Path updates in CLAUDE/AGENTS/PRINCIPLES, memory entries, runner repo root; CodeGraph re-index at
  the Keepverse root.
- [ ] **KS7.2** Old repo pointer commit, archive. **Gate G3.**
- [ ] **KS7.3** Per original-IP repo with ip-censor guard clean: orphan snapshot public `main`. **Gate G2.**
  Never gk-data (private always, D8).
## External dependencies
- ip-censor detect + execute programs: needed only for KS6.3.
- Original species / faction naming: needed for gk-data's `keepverse` pack to have content, not for the move.
## Findings routed to this program (owning program = keepverse-split)
Both were filed by lane `cs-f1` on 2026-09-22 while closing `CS-F1` (a fixture defect: a test's private
`..\..\..` walk resolved above the repo root in the main checkout but into it from a worktree, so the boot
answered the absence sentinel correctly for the directory it was handed). The lane named this program as owner
and recorded the rows in `tasks/creature-seed-todo.md`; they are restated here so the owning program's own todo
carries them, per the routing rule.
- [x] **KS-F1** The production boot's seed-tree discovery has no Keepverse content-root awareness · S ·
  *(= `CS-F1-a` in `tasks/creature-seed-todo.md`; the caller is `content-stack`.)* The test now resolves content
  through `FusionRpg.TestSupport.ContentRoot.Path`, but the boot's own discovery still has no notion of the
  Keepverse content root — so a real boot in the split world has nothing to consult.
  **ENDED 2026-09-23 (lane `findings-1`) — the boot cannot own a content-root resolver, and the question is
  sharpened with the alternative named. Read, not inferred:**
  - **The plan already decided this.** `tasks/keepverse-split-plan.md` §"Resolver contract" (line 185):
    *"Runtime code under `src/FusionRpg.{Core,Data,Server}` is exempt: it resolves content against its build
    output, whose layout the `<Content Link="data\...">` items preserve (`outputRelativeGlobs`)."* The C#
    column of its resolver table is `ContentRoot.Path` — the **test** resolver in `gk-core/tests/Shared/KeepverseRoots.cs`,
    compiled into `*.Tests` only by `Directory.Build.props:19-22`. There is no production C# resolver to point
    the boot at, and writing one is the "second content-root concept" the row forbids.
  - **A resolver on the seed import alone would be a half-wire.** The server resolves content against its own
    directory at **~40 sites** (`grep -c AppContext.BaseDirectory gk-core/src/FusionRpg.Server/Program.cs`), including
    `gk-core/data/tuning`, items, structures, dungeon, actions, loot, charms and combinations — and some of those reads
    are runtime state (the SQLite dir), which must stay beside the exe. Making one of them env-aware while the
    other 39 stay exe-relative is the "mechanism no production host reaches" shape, not a fix.
  - **What the row's alternative actually needs — and the premise is broken.** The exemption's premise is
    "the build output carries the content beside the exe". Measured here: `SeedScanner.OwnedFolders`
    (`gk-core/src/FusionRpg.Data/Seed/SeedScanner.cs:44-58`) sweeps **18** seed folders; the Server csproj had copy
    rules for **10** of them, so a publish-dir-only install (where `FindUp` finds the exe's own `gk-data/packs/fusion/data/seed`
    first and never walks up to a checkout) would sweep a **partial** tree and report `Imported` — 12 committed
    files under `containers`, `curves`, `rarity`, `elements`, `channel-policy`, `channel-pools`,
    `effects/affixes` and `creatures/species-effects` inert with nothing saying so. And the player zip ships no
    content at all: `scripts/publish-player.ps1:200-203` **deletes `Server\data`** after publish, so
    `gk-core/data/tuning/**` and `gk-data/packs/fusion/data/seed/**` are both stripped from the shipped server. That packaging half is filed
    as its own row in `tasks/content-stack-todo.md` (content-stack owns `publish-player.ps1`; this lane's fence
    is `scripts/**` guards only).
  - **Landed here (production code, this fence):** the eight missing `<Content>` rules in
    `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj`, plus a contract case in
    `gk-core/tests/FusionRpg.Server.Tests/BootContentCopyRuleTests.cs` that reads `SeedScanner.OwnedFolders` and fails
    when a swept folder has no rule — so the plan's exemption is true for the seed tree and stays true.
    Evidence: the commit `fix(keepverse): KS-F1 ...`.
  **Sharpened question (for the owner / the plan's author, since `tasks/keepverse-split-plan.md` is outside
  this lane's fence):** in the split world, which mechanism puts `gk-data/packs/fusion/data/seed` beside the server exe, and does
  `kvsplit`'s `outputRelativeGlobs` rewrite these rules to point into `gk-data/packs/<pack>`? If the answer is
  "the packaging ships it", then `publish-player.ps1`'s `Remove-Item $ServerData` is the defect, not the boot.
  If the answer is "the boot reads a content root outside its own directory", then the plan's runtime exemption
  must be amended and a production resolver named — a plan/ADR change, not a lane decision. **Named
  alternative:** keep the exemption and make packaging ship the tree (the filed content-stack row).
  **Erratum requested:** this row's acceptance line (`creature-seed-todo.md` CS-F1-a) asks for "the plan
  records that a player install ships `gk-data/packs/fusion/data/seed` beside the binary" — the plan is not in this fence, so that
  half is recorded here and in the filed packaging row instead.
  **RESOLVED 2026-09-23 (lane `findings-2`, through `CS-F2`) — the named alternative was taken, and the
  erratum's half is now measured rather than requested.** `scripts/publish-player.ps1`'s delete is gone, so
  *the packaging ships the tree*. Measured on a real `dotnet publish` of `gk-core/src/FusionRpg.Server`: the publish
  output carries `gk-data/packs/fusion/data/seed/**` (**1386** `.json`) and `gk-core/data/tuning/*.json` (**182**) beside
  `FusionRpg.Server.exe`, and booting that pack answers `{"ok":true,"contentSource":"imported","catalogRevision":1}`;
  the same pack with `Server\data` moved aside (the pre-fix shape) dies at
  `gk-core/src/FusionRpg.Server/Program.cs:32` with
  `Unhandled exception. System.IO.DirectoryNotFoundException: ...\Server\data\tuning\contracts.v1.json`.
  The requirement is now a contract with a falsifier rather than a property of one script:
  `PlayerPackProbe` requires `Server\data\seed` and `Server\data\tuning` with a planted-violation case
  (`gk-fusion/tests/FusionRpg.Launcher.Tests/PlayerPackProbeTests.cs`), and `scripts/smoke-player-pack.ps1` asserts the
  boot's own `contentSource` reads `imported`. Evidence: `tasks/reports/findings-2-csf2.md`.
  **One caveat, filed as `CS-F3` in `tasks/content-stack-todo.md` and not reopening this row's answer:** a
  fresh player install still cannot reach `/health` at all, because the pack ships no species roster and no
  boot or launcher step imports one — `CreatureSpeciesCatalog.Configure` throws on an empty roster at
  `gk-core/src/FusionRpg.Server/Program.cs:612`. That is a different tree (`gk-data/packs/fusion/data/generated/creatures/**`) and a
  different defect; this row's acceptance (a player install ships `gk-data/packs/fusion/data/seed` beside the binary) is proven,
  while the install is not yet bootable end to end.
  **Still owed, and blocked by this lane's fence:** the acceptance's literal half is one sentence in
  `tasks/keepverse-split-plan.md`'s "Resolver contract" ("a player install ships `gk-data/packs/fusion/data/seed` beside the
  binary"), and that file is not among lane `findings-2`'s allowed paths — the measurement above is recorded
  here instead, which is what the row's own erratum note asked for.
- [x] **KS-F2** Nothing forbids a private repo-root walk in a test · S · **CLOSED 2026-09-23 (lane `findings-2`)**
  **Delivered:** `scripts/guard-test-content-root.ps1` (tier `ci`, status `gating`; catalogued in
  `gk-core/scripts/enforcement-registry.v1.json` under the new invariant row `pr-test-content-root`, and mapped for
  `verify-change.ps1` by the `test-content-root-guard` boundary in `gk-core/scripts/verification-boundaries.v1.json`),
  with its planted-violation cases in `gk-core/tests/FusionRpg.Guard.Tests/TestContentRootGuardTests.cs`. Evidence:
  `tasks/reports/findings-2-ksf2.md`.
  **The rule, and why it is stated over the resolution rather than over the `..`.** A
  `[CallerFilePath]`-anchored walk is the only one whose depth is statically knowable — the anchor IS the
  source file's own directory — so the guard resolves it exactly and refuses two shapes that are wrong *by
  construction*: **`walk-escapes-root`** (the walk climbs past the repository root — the CS-F1 shape:
  `..` x N from a directory D segments below the root escapes when N > D) and **`walk-misses-root`** (the
  walk lands inside the repository while being used as a Keepverse root, e.g. `..` x 2 from a depth-3 test
  directory naming `tests/data`).
  **It is deliberately not a ban on `..` in `tests/**`.** Most walks in this tree are correct and are not
  repo-root walks at all (`Path.Combine(goldenDir, "..")`, a walk to `gk-core/tests/fixtures`, a *runtime* walk-up
  loop). Banning them would need the ~30-file rewrite plus a per-file choice between
  `ContentRoot`/`CoreRoot`/`WorkspaceRoot` — and a baseline on a depth-fragile walk is the exact thing this
  guard exists to prevent. The rule therefore bites on a planted wrong-depth walk without touching any of
  them; `guard-test-content-root.ps1`'s own control case (a correct depth-3 walk passes) is what keeps it
  from being indistinguishable from a blanket ban.
  **Population — a READING, never pinned (the erratum `findings-1` recorded, re-measured here).** At this
  head the guard scans **1,596** `tests/**/*.cs` files; **47** declare `[CallerFilePath]`; **60** anchored
  walks resolve against the repository root; **0** violations. The guard prints those counts and asserts
  none of them.
  **Bounds, stated rather than hidden.** Only `[CallerFilePath]`-anchored walks are in scope (an
  `AppContext.BaseDirectory` walk's depth depends on the build layout, so no static rule can resolve it and
  a rule that guessed would be a false positive); a local assigned more than once (a walk-up loop's cursor)
  is opaque and never flagged; the scanner strips comments but keeps string literals, because the `".."`
  literals and the `[CallerFilePath]` attribute are the subject.

## Open-row blocker map (2026-09-23, lane `findings-2`)

Every row still open above is stopped by one of five things, each named exactly. No row below is waiting on
work this lane simply has not done yet.

| Row(s) | Blocked by |
|---|---|
| **KS1.4 `graph`** | **A** — its remaining half (`package.json` / `pyproject.toml` graph edges) is kvsplit Python source, and kvsplit does not live in this repository. |
| **KS1.5 `transform`** | **A** — its remaining half is the CI-workflow split *transform* (kvsplit code); the `.github/workflows/*` outputs it would rewrite are also protected pipeline paths. |
| **KS3.0**, **KS6.0** | **C** — an owner charter (runtimes, models, budget, stop rule) recorded before any reconcile worker; AGENTS.md makes that the manager's to ask and the owner's to give. |
| **KS3.1** | **D** — optional under D10 (“pre-move reduction … optional under D10, not a gate”), and every lane in it is defined by kvsplit residue ids that only `kvsplit stage` regenerates (**A**). Its in-fence parts would be `tests/**` and `scripts/**`; its other parts are not: L2 `gk-forge/tools/seedsmith/**`, L4's `.github/workflows/*` split, L5's `web/**`. |
| **KS3.2 Checkpoint A** | **A** — “`verify` byte-identical” *is* a kvsplit run (`python -m kvsplit verify`), plus KS3.1. |
| **KS4.1–4.3**, **KS5.1–5.2**, **KS6.1–6.2**, **KS7.1–7.3** | **B** — the todo's own `⛔ HOLD — Gate GM` (owner ruling 2026-09-19): phases 4–7 start only on the owner's explicit “start migration” command, and until then nothing is applied to Keepverse repos. |
| **KS-F1** | Closed by measurement on this branch (see the row). One half remains and is **E**: its acceptance line's literal sentence belongs in `tasks/keepverse-split-plan.md`, which is outside lane `findings-2`'s allowed paths. |
| **KS-F2** | Closed (`[x]`) — guard landed, merged, `run-guards.ps1 -Tier ci` green. |

**A — a sibling git repository.** `D:\Works\source\Keepverse` is its **own git toplevel** (`git -C D:/Works/source/Keepverse rev-parse --show-toplevel` prints that path). It holds `tools/kvsplit/` (`kvsplit/`, `rules/`, `tests/`, `pyproject.toml`), `.github/workflows/kvsplit.yml`, and the `gk-{assets,core,data,forge,fusion}` sub-repos. Lane `findings-2`'s workspace is `…\.claude\worktrees\cmdc-findings-2`, and the operating protocol allows writes only inside it (plus the notes file), so no kvsplit source, rule, template or workflow can be edited from here. **Exact next step for whoever holds that fence:** run the lane in the Keepverse repo.

**D — measured today, because the todo's figure is stale.** Its L3b line records “**169** test files find the repo root by the `gk-fusion/src/FusionRpg.Injector` directory”. At this head the reading is **228** of **1638** `tests/**/*.cs` files naming the `"src", "FusionRpg.Injector"` literal pair (Guard.Tests 74, Server.Tests 51, Core.Items.Tests 24, Core.Tests 23, Data.Tests 21, the rest spread over 13 projects). A reading, never a pin — and the reason this is not a bounded increment: the distinction L3b actually asks for is “uses the marker only as a repo-root signal” vs “has the injector as its subject”, which is a per-file read across 228 files in projects other lanes are editing right now.

**Also open, and routed rather than owned here:** the two pre-existing `FusionRpg.Guard.Tests` reds at this head (`667 passed / 2 failed` — the stale `BattleEffects` byte pin and the nine-code pick-refusal pin) are filed with `file:line` and cause in `tasks/reports/findings-2-head-guard-reds.md` for the manager to route to W11 / `battle-derived-wire` and to `creature-seed` T8. Until one lands, `verify-change.ps1` is red for every `tasks/**` path in this program.

    **READINESS 2026-09-27 — gate G1 is MET, and the plan header is the defect.** `docs/architecture/
    decisions.md:144` reads *"Locked (owner-approved plan, gate G1)"*, added by `7dcbf38d6` — the same
    commit `KS0.1` cites. The plan's line 3 (*"Status: plan, revised 2026-09-19. Not started. Owner
    approval of this plan is gate G1."*) was written in the file's **first** commit and never revised;
    `git log -S` returns exactly one commit. The 24-done / 17-open block counts refute "Not started" three
    ways. **The ledger carries no approval event**, so the evidence is that one decisions.md line — which
    is enough, but should be mirrored here so the program is self-contained.

    **The deterministic migration tool EXISTS; it is not the critical path.** `Keepverse/tools/kvsplit/`
    carries all nine plan modules plus `hashes`/`index`/`reindex` (Phase 1b). **`stage` has run**
    (`.staging/report.json`, a populated `workspace/`, and both `.staging-verify/run-1` and `run-2`).
    **`apply` has never run** — all five sub-repos hold only `.git`, `.gitignore`, `LICENSE`, `README.md`.
    The staged output is also older than the tool's last edit and 3,388 commits behind `HEAD`, so it is a
    rehearsal, not a candidate to apply. The target workspace exists and is correctly shaped, unapplied.
    (`.codegraph/` appears inside the staged tree — a possible missing `drop` rule, flagged, not measured.)

    **KS5.1's "zero findings" is satisfiable while everything unlanded is silently lost. This is the
    finding that should gate the migration.** The tool *"reads blobs at the SHA through git, never the
    working tree"*, and residue items describe **staged-tree** problems. So content that was never
    committed to the pinned SHA is simply absent from the output and **no mechanism names it**:
    `lossy-check`'s unit is the *legacy file* set, `apply` checks the **target** repo's dirtiness and
    never the source's, and "lanes closed" is a human step with no falsifier.

    Measured exposure: **4,197 distinct pieces / 231.98 MB** that no commit, ref or record preserves —
    338 tracked-modified pieces across 22 worktrees, plus 3,859 untracked across 13 (of which 3,030 are
    `tmp/**` scratch, leaving **829 pieces / 49.9 MB** of real content). The sharpest case is the **main
    worktree on the integration branch itself**: 57 modified + 2 untracked, including a brand-new 17.7 KB
    `gk-core/scripts/guard-debug-scope.py` and its 28 KB test. **Cleanup is therefore a deadline rather than a
    preference, and the deadline is worktree deletion** — which is the whole reason the leftover walk
    exists, stated as a migration risk rather than as tidiness.

    **"One main branch" is 7 branches, not 0.** Measured: 7 non-rescue branches unmerged against
    `features/mega-merge` out of 12 unmerged total, plus 5 rescue refs under `refs/heads/rescue/`. Two
    of the 7 are **exact SHA twins of a rescue ref**, so they are already preserved and need a decision
    rather than a rescue. `main`'s tree is **byte-identical to its merge-base**, so it needs a *merge*,
    not a rescue — the distinction matters because a rescue ref would preserve nothing.
