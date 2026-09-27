# Keepverse migration plan

Move the `plant-vs-zombie-rise-of-summoner` monorepo into the Keepverse multi-repo
workspace: one `gk-workflow` root plus eight sub-repositories, split by a deterministic
tool (`kvsplit`) whose residue is the work queue.

This document replaces `tasks/keepverse-split-plan.md` (2026-09-19) and its 2026-09-27
extension. It is self-contained: a fresh agent can execute it end to end without reading
the superseded files. It is versioned in the workspace it builds, next to the tool that
performs the move, because the source repository is archived at G3 and a plan describing
the move *out* of a repository dies with it.

**Task blocks live in `tasks/keepverse-split-todo.md` in the source repository.** Every
step below carries its `KS*` id. This document is the narrative and the ordering; the todo
is the unit of work. A block is a task; a `- [ ]` line is not — a shipped task keeps
permanently-unchecked acceptance boxes.

---

## 1. Measured state

Reproduced by running the tools, not carried forward. Two stamps: **source `75f64001f`**
(2026-09-28, branch `features/mega-merge`) and **gk-workflow `5d0df61`**.

> The source branch is still moving. Every figure below was reproduced against the stamped
> SHA, and the stamp moved three times while this document was written
> (`421cac07b` → `0923dfe03` → `26e6d75aa` → `75f64001f`). Each move added and deleted
> **zero** files, so the placement figures are stable; **re-read the SHA before relying on
> it**, and re-run §1.1 rather than quoting this table.

### 1.1 The split reconciles

`python -m kvsplit stage --source <src> --rev 75f64001f --rules rules --out <dir>`

```
source 75f64001f…  rules 5a1de009e5c3
tracked 14900   dropped 224   unplaced 0   balanced True
  root        5105    gk-data     3172
  gk-core     3784    gk-web      1108
  gk-forge     785    gk-tests       0
  gk-fusion    463    gk-content     1
                     gk-assets    258
residue 2515:  path-literal-moves 2120 · content-root-consumer 388 ·
              dead-rule 6 · content-in-public-repo 1
```

`unplaced 0` means every tracked path has an owner. The reconciliation identity is
`tracked 14900 = placed 14676 + dropped 224 + unplaced 0`, and it holds.

**A property worth preserving:** staging tracks file *paths*, so a content-only commit
cannot invalidate the rules. HEAD moved three times during the writing of this document
(`421cac07b` → `0923dfe03` → `26e6d75aa`) and produced byte-identical placement every time.
Residue is also unchanged at 2,515 across all three, because the commits touched no paths.

`dropped 224` is 222 skill symlinks plus 2 build artifacts, and every one is named in
`report.json`'s `dropped` list.

### 1.2 The source repository is not yet on one branch

This is the plan's precondition; §2 is entirely about it.

```
current branch   features/mega-merge   (upstream origin/features/mega-merge, ahead 4)
dirty            1 file, untracked: scripts/guard-verification-boundaries.py
local branches   5
remote branches  9 under origin/, plus 5 stale refs under local/ and origin-local/
worktrees        3 (main + 2 linked, both clean)
main vs mega     main is 201 behind, 4 ahead
```

`main`'s four commits ahead are all `Merge pull request #NN from letuhao/features-mega-merge`
(#18–#21). mega-merge has been merged into main four times already; the divergence is merge
markers, not competing content. **The final merge is therefore expected to be trivial, and
that expectation must be tested, not assumed.**

### 1.3 Three sessions still hold active fences

`python scripts/program_status.py` reads the head as
`26e6d75aa · features/mega-merge · +4/-0 · dirty 1 · worktrees 2`.

| Record | Fence |
|---|---|
| `ps1-ban-manager-20260926` | 451 paths, including `ci.yml`, `scripts/guard-*.ps1`, `enforcement-registry.v1.json`, `AGENTS.md`, `README.md`, `blender/**` |
| `mega-merge-program-manager-20260925-f78e` | seedsmith validators, `post_merge_check.py`, three todo files |
| `resume-34-cai2-2-20260925` | `RpgStore.cs`, `RpgStore.WebMatches.cs`, `Program.cs`, one test file |

`session-boundary-check.py` reports `DRIFT (3)`. That is other sessions' unclaimed
worktree branches; it is not this program's to fix, and the tool is scoped so it does not
block our verification.

### 1.4 Programme standing

`program_status.py`: **122 programs**, 117 measured, 5 unmeasured. **682 open task
blocks**, 2,892 done — of which **342 have a GREEN acceptance naming a SHA in this head and
2,550 are ticked with nothing behind them**. A tick is a claim; the second number is the
one not yet shipped.

`keepverse-split` itself: **17 open, 24 done, 0/24 verified**, fenced by nobody. Gate G1
is met — `docs/architecture/decisions/world.md:27` reads *"Locked (owner-approved plan,
gate G1)"*. That line used to be `decisions.md:144`; the lock file was split into
per-category files on 2026-09-27 and the index row now points at the category. The
2026-09-19 plan's own header still reads "Not started", a defect flagged 2026-09-27 that
this document supersedes.

`tasks/keepverse-split-ledger.jsonl` has 17 rows and its last entry is **2026-09-24** —
days of repository churn with no ledger row. The ledger is the program's memory and
must be written as work lands, not reconstructed afterwards.

### 1.5 The target workspace

Nine repositories, each with its own `origin` under `github.com/keepverse/`, **untracked**
in the root rather than submodules. All were at `0 behind / 0 ahead` when measured.

| Repo | Visibility | Licence | Tracked now | Receives |
|---|---|---|--:|--:|
| `gk-workflow` | public | AGPL-3.0 | 47 | 5,105 |
| `gk-core` | public | AGPL-3.0 | 4 | 3,784 |
| `gk-forge` | public | AGPL-3.0 | 4 | 785 |
| `gk-web` | public | AGPL-3.0 | 4 | 1,108 |
| `gk-tests` | public | AGPL-3.0 | 4 | **0** |
| `gk-fusion` | public | AGPL-3.0 | 4 | 463 |
| `gk-content` | **private** | AGPL-3.0 | 4 | 1 |
| `gk-data` | **private** | MIT | 4 | 3,172 |
| `gk-assets` | public | **CC BY 4.0** art + **MIT** `tools/**` | 86 | 258 |

### 1.6 Topology, and why each boundary sits where it does

```
Keepverse/                gk-workflow   workflow, docs, agent config, tasks, kvsplit
├── gk-core/              Contracts, Core, Data, CheatCore, Server, data/tuning, engine tools + tests
├── gk-forge/             seedsmith, generator tools (code only)
├── gk-web/               the browser control room
├── gk-tests/             gate definitions and cross-repo suites — hand-written, zero migrated files
├── gk-fusion/            Injector + 3 hosts, Launcher, game-profiles, live-probe, release
├── gk-content/  PRIVATE  authored content: our names, flavour, registries
├── gk-data/    PRIVATE  the derived corpus: packs/fusion/data/{seed,generated}/
└── gk-assets/            art, icons, and the migrated blender/ tree
```

Four boundaries the 2026-09-19 plan left open, now decided:

- **Web is `gk-web`, not gk-core.** Separate toolchain, separate bundle, separate failure
  mode; Node is developer-only and never ships. It still *serves* from the Server's
  `wwwroot` and binds the same `Contracts` DTOs, so web and server ship as one release.
  That is a cross-repo note, not a reason to merge the trees.
- **`gk-content` vs `gk-data` is authored vs derived.** One repository may not carry the
  game's own written identity and a corpus derived from another game and stay honestly
  private.
- **`gk-tests` holds gate definitions and cross-repo suites only.** It deliberately
  receives **zero** migrated files: path-owned verification co-locates a test with the code
  it tests, and a cross-repo lookup rots. `apply` reports it `unchanged`.
- **`gk-assets` is CC BY 4.0 for art, MIT for `tools/**`.** The 2026-09-19 plan flagged
  this itself — "MIT on art lets anyone reuse Keepverse art commercially". Splitting code
  from art is deliberate: CC BY on source code is an anti-pattern.

`blender/**` (258 tracked files) had no owner at all until 2026-09-27; each subtree
relocates onto the layout already hand-migrated into gk-assets.

### 1.7 Direction contract

```
gk-forge  → gk-core   (code); reads and writes gk-data packs
gk-fusion → gk-core   (code), gk-data fusion pack (runtime), gk-assets (files)
gk-core   → gk-data   RUNTIME ONLY, through GkDataRoot + a pack name, never compiled
gk-core   ⇏ gk-fusion
```

**`layout.testProjectGlobs` waives `compileDeps` for a test project.** `compileDeps`
governs what *ships*; a test that invokes a generator to assert on its output is verifying
the forge, not depending on it. The waiver is opt-in, applies only to the referencing
project, and the graph edge is still recorded — it hides a residue row, never a dependency.
Four gk-core test projects ProjectReference five gk-forge tool projects; without the waiver
that is 7 direction-violations.

### 1.8 Tool state

kvsplit is 15 implementation modules in Python plus `__main__`, **74 tests green** across 4
test files, CI at `.github/workflows/kvsplit.yml`. Two runs from the same SHA and the same
rules produce the same output digest.

Six contracts were added on 2026-09-27, each discovered by measuring the real workspace
rather than by design, and none of them is in the 2026-09-19 plan:

| Contract | Why it exists |
|---|---|
| `testProjectGlobs` waives the direction contract for test projects | §1.7 |
| a `drop` rule also authorises dropping a non-blob entry | a symlink never reached ordinary classification, so 222 were unresolvable |
| `apply` refuses to overwrite a committed file that differs | `preserve` stopped deletion, never overwriting: 38 files, 28 in gk-assets including 7 `.blend` scenes and 8 rendered sheets |
| `apply` reports a repo that receives nothing as `unchanged` | `git commit` on an empty index is an error, and gk-tests is that case |
| `preserve` must list every live file the split does not produce | measured, not guessed: 96 hand-authored files would have been deleted, 84 in gk-assets |
| refusals are messages, not tracebacks | `main()` had no error handling, so gate GM and residue-not-empty printed a stack trace |

Two kvsplit modules are **partially** delivered, and both remaining halves matter here:

- **KS1.4 `graph`** — MSBuild `ProjectReference` and host-assembly edges are done;
  **`package.json` / `pyproject.toml` edges are not**. So gk-web's Node dependency graph is
  unmodelled and the direction contract does not cover it.
- **KS1.5 `transform`** — most transforms are done; **the CI workflow split transform is
  not built**. Nine repos need nine CI definitions and nothing produces them yet.

### 1.9 What the split will not do, and the honest reason

`docs/` is **2,145 tracked files** and `tasks/` is **1,707**. Both route to `gk-workflow`
today and that is correct — they are the workspace's own memory. The 2026-09-19 plan's
"Docs placement (D1)" that sends PvZ-host docs to `gk-fusion/docs/` has not been expressed
as rules, and until it is, every host doc lands in the root. That is a **known, unowned
gap**, not a completed decision: it is 1 item on the residue queue's successor list.

---

## 2. Phase A — consolidate the source repository to one branch

**This is the precondition for everything in §3 onward. No migration work starts until the
source repository has exactly one branch, `main`, and every other branch — local, remote,
and every linked worktree — is deleted.**

The rationale is specific, not procedural preference. `kvsplit` reads a pinned SHA, so a
moving branch cannot corrupt a stage; but a *branch* is a claim about what the import
contains, and this repository currently makes several contradictory ones. A green
rehearsal against a 3-day-old SHA, a `KS4.1` that merges 201 commits, and an import SHA
chosen from a branch that four unpushed commits are still moving are three different
things. Phase A removes the ambiguity so the import SHA is a fact rather than a guess.

### A.1 Freeze the inputs

| Step | Action | Evidence it worked |
|---|---|---|
| **A.1.1** | Push the 4 unpushed `features/mega-merge` commits | `git rev-list --count @{u}..HEAD` is 0 |
| **A.1.2** | Resolve the 1 dirty untracked file `scripts/guard-verification-boundaries.py` | It belongs to `ps1-ban-manager-20260926`. Commit it under that session, or record it abandoned. **Do not delete it and do not commit it under this program.** |
| **A.1.3** | Write a ledger row recording the head SHA Phase A froze at | `tasks/keepverse-split-ledger.jsonl` gains a row |

### A.2 Close the three active sessions

Each must end as `merged` or `abandoned` in its own record — a third status is invalid and
the boundary checker rejects it. An `active` worktree record must still own a live branch
and a resolvable worktree path.

| Record | What closing means |
|---|---|
| `ps1-ban-manager-20260926` | The largest fence (451 paths). Either its 8 open blocks land or they are explicitly deferred with the deferral recorded. Its work is **in flight and wanted** — do not abandon it silently. |
| `mega-merge-program-manager-20260925-f78e` | Manager session. Close after its programs are handed over. |
| `resume-34-cai2-2-20260925` | One data/server task (CAI2.2 replay-identity B). Land or abandon. |

Validate with `python scripts/session-boundary-check.py --session <id>`. Drift naming
another session is printed under its own heading and does not fail ours.

### A.3 Decide the branches that hold work nobody has merged

**These are the only destructive decisions in Phase A, and three of them have real work in
them. None may be deleted on a "probably merged" assumption.**

| Branch | Ahead of mega-merge | Verdict needed | What it holds |
|---|--:|---|---|
| `ps1ban/l3-checks` | **3** | merge or abandon | deletes the 16 PowerShell wrappers, repoints the registry at the `.py` |
| `ps1ban/l4-artifacts` | **1** | merge or abandon | opens the L4 artifacts lane |
| `rescue/corpus-bcu211-itemseedgen-run` | **1** | merge or abandon | the item-seedgen full run, 56 files, gaps 931 → 770 |
| `origin/worktree-rift-gate-20260914` | **1** | merge or abandon | 1 unmerged commit on a stale worktree branch |
| `origin/features/derived-stat-extension` | 0 | delete | fully merged |
| `origin/features/mega-merge` | 0 | delete after the merge | fully merged |
| 5 × `origin/worktree-*` | 0 | delete | fully merged worktree branches |
| `local/*`, `origin-local/*` (5 refs) | — | delete | stale refs from an earlier remote layout; no upstream worth keeping |

The first two belong to the `ps1-ban-manager` session and are that session's call. The
third is a corpus rescue whose value is measurable — `rescue/...` is 2,518 commits behind,
so merging it is a real merge, and its own subject line carries the number that decides it
(§A.6).

### A.4 Merge mega-merge into main and prove it is trivial

```
git switch main
git merge --no-ff features/mega-merge
```

Expect trivial. Expect it anyway to be checked:

| Step | Action | Evidence |
|---|---|---|
| **A.4.1** | Dry-run the merge on a scratch branch first | no conflict markers, no unexpected file count |
| **A.4.2** | Merge for real; if conflicts appear, **stop and report** — a conflict here means two programs touched one path and that is a finding, not a merge to resolve | `git log --oneline main..features/mega-merge` empty afterwards |
| **A.4.3** | Verify the merged `main` is content-identical to mega-merge | the 4 "ahead" commits are merge markers only; confirm the trees match |
| **A.4.4** | Run the build gate on the merged head. `post_merge_check.py` lives in the **source** repository, so run it from there: `python .claude/cmdc-agents/scripts/post_merge_check.py` with the source repo as cwd | Build is proven at HEAD (75/80 non-game projects); **tests are not** — this is the first time the merged head is test-gated |
| **A.4.5** | `git push origin main` | `origin/main` == local `main` |

`post_merge_check.py` is the merged-head gate and is the only evidence that the merge did
not break something that 201 commits of parallel work each believed was fine.

### A.5 Retire the worktrees, then delete the branches

Order matters: the branch cannot be deleted while a worktree holds it.

| Step | Action | Evidence |
|---|---|---|
| **A.5.1** | For each linked worktree, confirm it is clean **and** its branch is merged or decided in A.3 | `git -C <wt> status --porcelain` empty |
| **A.5.2** | Remove the worktrees | `git worktree list` shows only the main checkout |
| **A.5.3** | Delete the local branches | `git branch` lists only `main` |
| **A.5.4** | Delete the remote branches | `git ls-remote --heads origin` lists only `refs/heads/main` |
| **A.5.5** | Prune stale refs | `git remote prune origin`; the `local/*` and `origin-local/*` refs are gone |

Two worktrees exist and both are clean: `ps1ban-l3-checks` and `ps1ban-l4-artifacts`, each
under the temp opencode directory, each holding a branch from A.3. A branch with a live
worktree is the one way this phase can lose work silently, so A.5.1 runs before A.5.3.

### A.6 Phase A exit criteria

All five, checked, not asserted:

1. `git branch` → exactly one line: `main`.
2. `git ls-remote --heads origin` → exactly one ref: `refs/heads/main`.
3. `git worktree list` → exactly one entry, the main checkout.
4. `git status --porcelain` → empty, on `main`.
5. Every session record reads `merged` or `abandoned`; `session-boundary-check.py` is clean
   for this program.
6. A ledger row records the frozen `main` SHA. **That SHA is the migration's import
   candidate**, and §4 pins it.

**A.7 — the import candidate is not the import SHA.** Phase 3 still runs after Phase A and
still lands source commits. The import SHA is re-read at KS4.1, and the re-run is cheap
because staging is deterministic. What Phase A guarantees is that *one branch* carries the
work, so the candidate SHA means one thing.

---

## 3. Phases 0–2 — done

| Phase | Block | Evidence |
|---|---|---|
| 0 — decide | KS0.1 | `docs/architecture/decisions/world.md:27` "Locked (owner-approved plan, gate G1)" |
| 1 — build kvsplit | KS1.1–1.3, 1.10–1.15 | 15 implementation modules; `hash`, `lossy-check`, `index`, `reindex`, `apply`; rehearsal 2026-09-19 with **0 lossy findings over 11,133 files**, second run a no-op |
| 1b — move-first tools | D10 ruling | the `hash` → `lossy-check` → `index` → `reindex` chain above |
| 2 — rules, dry runs | — | `unplaced 0`, `balanced True`, deterministic, 74 tests green |

**Two modules are partial and are the only unfinished Phase 1 work:** KS1.4
(`package.json`/`pyproject.toml` graph edges — so gk-web's Node graph is unmodelled) and
KS1.5 (the CI workflow split transform — so nothing yet produces nine CI definitions).
Both are kvsplit code, both are in §7's queue, and neither blocks the move.

### 3.1 The resolver contract (Phase 1b/3, largely landed)

**A pack mirrors the legacy repository root.** `packs/<pack>/` holds `data/seed/**`,
`data/generated/**` and `content/**` at the legacy relative paths, so a repo-relative
literal such as `data/seed/items/x.json` stays byte-identical and only the root it resolves
from changes. `data/tuning/**` keeps its path inside gk-core.

| Root | Env override | Split default | Python | C# |
|---|---|---|---|---|
| content | `KEEPVERSE_CONTENT_ROOT` | `<ws>/gk-data/packs/<KEEPVERSE_PACK or fusion>` | `content_root()` | `ContentRoot.Path` |
| core | `KEEPVERSE_CORE_ROOT` | `<ws>/gk-core` | `core_root()` | `CoreRoot.Path` |
| workspace | `KEEPVERSE_WORKSPACE_ROOT` | the dir holding `gk-core/` and `gk-data/` | `workspace_root()` | `WorkspaceRoot.Path` |

Discovery is deterministic: the env override wins, else walk up to the first directory that
is the legacy repo (has `FusionRpg.slnx` and `data/seed/`) or the workspace (has
`gk-core/`). **A missing root throws; it never falls back silently.** Runtime code under
`src/FusionRpg.{Core,Data,Server}` is exempt — it resolves against its build output, whose
layout `<Content Link="data\...">` preserves.

Landed: `workspace_roots.py` (seedsmith) + `scripts/lib/keepverse_roots.py`,
`KeepverseRoots.ps1`, and `KeepverseRoots.cs` linked into every `*.Tests`; 45 C# test
content readers routed; 563 tests green across 7 projects; `scripts/**/*.py` is 13 files,
of which 4 of 6 consumers are routed.

---

## 4. Phase 4 — freeze and move

Held behind **Gate GM**. The 2026-09-19 todo is explicit: *prepare the tools and plan, then
stop. Phases 4–7 start only on the owner's explicit "start migration" command.*

### 4.1 KS4.1 — pin the import SHA

Phase A has already merged and deleted (§2). KS4.1 then re-reads the head, because Phase 3
lands source commits, and records the import SHA in the todo. `kvsplit` reads that SHA and
never the working tree, so a moving branch cannot corrupt a stage.

### 4.2 KS4.2 — stage, then apply

```
python -m kvsplit stage --source <src> --rev <IMPORT_SHA> --rules rules --out <staging>
python -m kvsplit apply --staging <staging> --workspace D:/Works/source/Keepverse \
       --confirm-migration-start --allow-residue
```

**`--allow-residue` is the designed flow, not a workaround.** Under D10 the residue moves
with the tree and is reconciled in Phase 6; KS3.2 says so in as many words. The 2,515
items are Phase 6's queue, **not a blocker on the move** — an earlier framing in this
workspace's plan extension had that backwards and this document corrects it.

Nine repos, one snapshot commit each. `apply` refuses for these reasons and each is a real
precondition, not a formality:

| Refusal | Meaning now |
|---|---|
| target is not a git repository | all nine exist |
| target is not clean | **gk-assets is dirty with 36 entries** (§6.2) |
| root `.gitignore` must exclude sub-repo dirs | satisfied by the staged template |
| staged file missing | re-run `stage` |
| would overwrite N committed files that differ | **38 clashes** (§6.1) — needs `--accept-overwrites`, which is a decision, not a convenience |
| residue not empty | expected; pass `--allow-residue` per D10 |

### 4.3 KS4.3 — workspace manifest and first lock

Root `workspace.json` listing repos and remotes, and `workspace.lock.json` recording the
SHAs last proven green together. Emitted by kvsplit templates, not hand-written. **The
bootstrap script is Python** (`tools/bootstrap_skills.py` plus a workspace bootstrap), not
the `.ps1` the 2026-09-19 plan named: new tooling in this repository is Python by owner
ruling, and the 2026-09-19 plan predates it.

Skill aliases are a mirror: `tools/bootstrap_skills.py` creates, repairs and prunes
`.claude/skills/*` and `.kiro/skills/*` from the canonical `.agents/skills/`. The 222
tracked symlinks are dropped because a symlink checks out as plain text without
`core.symlinks`; two alias sets of the same 111 skills would also drift apart on their own.
It refuses with exit 2 rather than guessing a root — a wrong root means writing symlinks
into an unrelated tree, which it did during development before the guard existed.

---

## 5. Phases 5–7

### 5.1 KS5.1–5.2 — lossy check, index, reindex

`hash --workspace`, then **`lossy-check` must report zero findings** or the import commits
are rolled back and the tool is fixed. Zero means: every legacy file is placed with its
staged bytes or dropped by rule, and every moved file is explained by a report row, a
template or a preserve glob. Then `index`; review the `reindex` dry run; `reindex --apply`;
one commit per repo.

The rehearsal achieved 0 findings over 11,133 files with 0 stale and 128 links already
broken before the move (reported apart as `preExisting`). The import is 14,900 tracked
files, so the rehearsal's ratio is the expectation, not its absolute number.

### 5.2 KS6.0–6.2 — Checkpoint B

- **KS6.0** An owner charter (runtimes, models, budget, stop rule) recorded **before** any
  reconcile worker starts.
- **KS6.1** The queue is carried residue + reindex `stale` + per-repo build/test failures.
  Fixed by source commits in the new repos, or by a rule/tool change with a documented
  re-run.
- **KS6.2 Checkpoint B** — all four, or the migration is not proven:
  1. Full suite green **per repo** with sibling checkout.
  2. Every generator `--check` byte-identical to the import SHA.
  3. Goldens unchanged.
  4. Live lawn entered from the Keepverse layout, and a real
     `/api/aptitudes/unique/allocate` read back through the normal path.

Item 4 is the one that cannot be faked: the `bound-loadout-hub` incident shipped
end-to-end `ok:true`-shaped evidence for a feature that was actually broken, and was caught
only because a human looked at the real screen.

### 5.3 KS7.1–7.3 — cutover

Path updates in `AGENTS.md` / `CLAUDE.md` / `PRINCIPLES.md`, memory entries, the runner's
repo root, and a CodeGraph re-index at the Keepverse root. Note the 2026-09-19 plan says
root `CLAUDE.md` loads for sub-repos; that is now inverted — **`AGENTS.md` is the primary
instruction file** and `CLAUDE.md` is a 23-line pointer, because two instruction files drift.

KS7.2 is **Gate G3** (archive). KS7.3 is **Gate G2** (make public), per original-IP repo,
only with the ip-censor guard clean. **Never gk-data; gk-content is private for the same
reason** (D8).

---

## 6. Work that is outstanding and still unowned

### 6.1 The 38 overwrite clashes — an owner decision, not an agent brief

The owner hand-migrated art into gk-assets and then improved it. The split now produces the
same paths from `blender/`. Of 77 staged paths that are already committed somewhere, **38
differ in content**, 28 of them in gk-assets: 7 `.blend` scenes, 8 rendered sheets,
`vfx/index.json`, `vfx/README.md`, four skill and tool files, and every `AGENTS.md`.

For each, one of two is canonical: the newer gk-assets file, or the legacy `blender/` one.
There is no rule that decides this and no transform can — it is authorship. `apply` refuses
until it is settled, which is the correct behaviour. Suggested order: `vfx/index.json` and
the 7 `.blend` files first, since a silently reverted scene is the hardest to notice.

### 6.2 gk-assets is dirty

**36 entries, and it moves** — 9 modified (`SKILL.md` × 2, `.gitignore`, two
`assets/vfx/ice_shield/` READMEs, `tools/build.py`, `tools/verify_all.py`, `vfx/README.md`,
`vfx/index.json`) and 27 untracked (earth_shield VFX sub-programs, ice mirror textures, new
`tools/*.py`). This is live authored work, not debris. `apply` refuses on a dirty tree,
correctly. It must be committed under its own session before KS4.2 — and re-measured then,
because the count is growing while the art session works.

### 6.3 The 2,515 residue items

| Kind | Count | Nature |
|---|--:|---|
| `path-literal-moves` | 2,120 | mechanical but voluminous; mostly L2 (seedsmith) and L4 (scripts + CI) |
| `content-root-consumer` | 388 | files resolving a content root; 160 in seedsmith, the rest across test projects |
| `dead-rule` | 6 | **pre-existing and not ours**: 6 ownership rules name `.ps1` files the ps1-ban program already ported to `.py` |
| `content-in-public-repo` | 1 | a **synthetic test fixture** — `tools/ip-censor/tests/fixtures/registry/remediation/top-level-meta.json` carries `"model": "fixture-model"`, `"promptVersion": "fixture/1"` |

Residue is **growing, not regressing**: 951 → 383 at legacy `50d174e0`, and 2,515 now,
because the repository added content and paths while the residue work was in progress. The
6 dead rules are the one class that should be *removed* rather than reconciled — the rules
name files that no longer exist.

The 1 fixture is a false positive by intent, not by accident: 1,321 real files carry
generator provenance and all of them are in private repos; only this synthetic one sits in a
public one. Either the guard learns a fixture from its `fixture/` path, or the fixture's
values stop looking like provenance. Both are one-line changes; neither is urgent.

### 6.4 gk-tests holds nothing yet

By design, and `apply` reports it `unchanged`. But its **gate definitions are unwritten**,
so the repository exists and is empty. It needs: the per-repo verification boundary
declarations (currently `scripts/verification-boundaries.v1.json` in the root, which is
wrong the moment there are nine repos), the cross-repo suite, and the `ContentIntegration`
category for the tests that genuinely need private gk-data.

### 6.5 The CI split is not built

KS1.5's remaining half. Nine repos need nine CI definitions and no transform produces them.
`ci.yml` is inside `ps1-ban-manager`'s fence, so this cannot start until that session
closes (§A.2).

### 6.6 gk-web's dependency graph is unmodelled

KS1.4's remaining half: `package.json` / `pyproject.toml` edges. The direction contract in
§1.7 covers MSBuild only, so nothing checks that gk-web imports only what it should.

### 6.7 KS-F3 — the resolver contract names three roots, two consumers read a fourth

`guard-population-pin.py` and `guard-vocabulary-mirror.py` remain unrouted, blocked on a
contract gap rather than on effort. This is the last open item in §1.8's L4 lane.

### 6.8 The ledger is stale

17 rows, last entry 2026-09-24, while HEAD moved three times since. The ledger is the
program's memory; a reader reconstructing it from git is doing work the ledger exists to
prevent.

---

## 7. Gates

Only irreversible actions carry a gate.

| Gate | Action | Resolver | Default if unanswered |
|---|---|---|---|
| G1 | Approve the plan | owner | **met** — `docs/architecture/decisions/world.md:27` |
| **GM** | **Start the migration** | owner | Work stops after Phase 3. No `apply`, no freeze, nothing written into the Keepverse repos |
| G2 | Make a repo public | owner, per repo | stays private |
| G3 | Archive the old repo | owner | old repo frozen by convention |

Push is owner-only in the source repository. `apply` commits locally only.

**The branch deletions in §A.3–A.5 are irreversible and are not behind a gate.** That is
deliberate and it is the one place this plan asks the owner to act without a second
confirmation, because Phase A was requested as a precondition and a gate on the
prerequisite would make it optional. Each deletion is still individually decided in A.3,
never batched.

---

## 8. Constraints that survive into execution

These hold for every agent that picks up a row. They are not advice.

1. **Residue ids are stable.** A brief is "re-run `stage`, the item is gone, and no new id
   appeared". An id that moves means the fix changed the shape of the problem, not that it
   was solved. Each lane re-runs `stage` and closes **only its own ids**.
2. **A block is a task, not a checkbox line.** A shipped task keeps 6–10 permanently
   unchecked acceptance boxes. Never measure remaining work by counting `- [ ]` lines: that
   has overstated a program at 286 open rows when it held 6 open blocks.
3. **Determinism is the correctness argument.** Same SHA + same rules must give the same
   output digest. If a re-run changes the digest without a rules change, that is a defect.
4. **Fail closed, name the reason.** A tool that cannot decide refuses with a specific
   message and a non-zero exit. Empty output must never read as success.
5. **Python for all new tooling.** No new `.ps1`.
6. **Never `git add -A` / `git commit -a`.** Stage explicit paths. Several agents share
   this tree; a broad stage sweeps another stream's half-finished files, and that has
   happened. Never `stash` / `checkout` / `reset` another session's work.
7. **Never touch another session's dirty files.** Leave them; report them.
8. **An unchecked `- [ ]` line is not a unit of work**, and **a tick is a claim** — 2,550
   of this repository's 2,892 "done" blocks have no GREEN acceptance behind them.
9. **Read `program_status.py` before reporting status**, and paste the reading used. Never
   quote a figure not just reproduced.
10. **Commit often, one logical change per commit**, at verified increments. Never amend.

---

## 9. Open owner questions

1. **Is the trademark/IP risk time-sensitive?** Unanswered since first raised, and it is
   the only open item with a clock on it. `gk-content` and `gk-data` are private for this
   reason, and G2 and G3 both wait on it. Every other item in this document is sequencing.
2. **The A.3 branch decisions** — merge or abandon, per branch, for the 4 holding unmerged
   work.
3. **KS3.0 / KS6.0 owner charter** — runtimes, models, budget, stop rule, recorded before
   any reconcile worker starts.
4. **Docs placement (D1)** — 2,145 files currently all route to the root. Host docs going to
   `gk-fusion/docs/` is a decision that has not been expressed as rules. Confirm the
   boundary, or accept everything in the root.
5. **gk-assets' 37 dirty entries** — commit under the art session, or park them.
