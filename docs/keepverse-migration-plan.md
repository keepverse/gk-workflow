# Keepverse migration plan

Move the `plant-vs-zombie-rise-of-summoner` monorepo into the Keepverse multi-repo
workspace: one `gk-workflow` root plus eight sub-repositories, split by a deterministic
tool (`kvsplit`) whose residue is the work queue.

This document **supersedes** `tasks/keepverse-split-plan.md` (2026-09-19) and its 2026-09-27
extension. Both are historical: where they disagree with this document, this document is
right, and a citation to either is a stale authority. It is self-contained — a fresh agent can
execute it end to end without reading the superseded files. It is versioned in the workspace it
builds, next to the tool that performs the move, because the source repository is archived at
G3 and a plan describing the move *out* of a repository dies with it.

**A citation to a superseded plan is itself a defect, and one survives in a repository this
plan cannot edit.** `gk-core/Directory.Build.props:27` names `tasks/keepverse-split-plan.md` as
the authority for the resolver contract. The file it should name is this one. It is not fixed
here because `gk-core` is outside the fence of the change that found it, and its source of
truth is the legacy repository; the fix is a one-line comment and belongs to whoever owns that
line. Recorded, not silently left.

**Task blocks live in `tasks/keepverse-split-todo.md` in the source repository.** Every
step below carries its `KS*` id. This document is the narrative and the ordering; the todo
is the unit of work. A block is a task; a `- [ ]` line is not — a shipped task keeps
permanently-unchecked acceptance boxes.

---

## 1. Measured state

Reproduced by running the tools, not carried forward. Two stamps: **source `b212e868`**
(2026-09-28, branch `features/mega-merge`) and **gk-workflow `5d0df61`**.

> **§1.1 is a pre-merge reproduction and its per-repository figures are stale.** It is kept
> unedited because it is a reproduction at a named SHA, and rewriting a measurement to match a
> later one falsifies it. The current figures are the remeasured import-SHA ones in §6A.1
> (`tracked 15020 = 14538 + 482 + 0`; root 5108, gk-core 3860, gk-data 3232, gk-web 1108,
> gk-forge 791, gk-fusion 438) — the merge of `features/mega-merge` into `main` moved every one
> of them. Read §6A.1, not the block below, for a current number.

> The source branch is still moving. Every figure below was reproduced against the stamped
> SHA, and the stamp moved three times while this document was written
> (`421cac07b` → `0923dfe03` → `26e6d75aa` → `75f64001f`). Each move added and deleted
> **zero** files, so the placement figures are stable; **re-read the SHA before relying on
> it**, and re-run §1.1 rather than quoting this table.

### 1.1 The split reconciles

`python -m kvsplit stage --source <src> --rev b212e868 --rules rules --out <dir>`

```
source b212e868…  rules b4a328ac0a62  output 2655c5543cd0
tracked 14900   dropped 482   unplaced 0   balanced True
  root        5105    gk-data     3172
  gk-core     3784    gk-web      1108
  gk-forge     785    gk-tests       0
  gk-fusion    463    gk-content     1
                     gk-assets      0   (art already migrated; blender/ dropped)
residue 2514:  path-literal-moves 2119 · content-root-consumer 388 ·
              dead-rule 6 · content-in-public-repo 1
```

`unplaced 0` means every tracked path has an owner. The reconciliation identity is
`tracked 14900 = placed 14418 + dropped 482 + unplaced 0`, and it holds.

**A property worth preserving:** staging tracks file *paths*, so a content-only commit
cannot invalidate the rules. HEAD moved three times during the writing of this document
(`421cac07b` → `0923dfe03` → `26e6d75aa`) and produced byte-identical placement every time.
Residue was unchanged across all three for the same reason. It reads 2,514 today, the one
change being the `blender/` decision in §6.1 rather than anything a branch move did.

`dropped 482` is 222 skill symlinks, 258 `blender/` files (the art already lives in
gk-assets, so importing them again would revert the improved copies) and 2 build
artifacts. Every one is named in `report.json`'s `dropped` list.

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

> The **Receives** column is the pre-merge projection and is stale for six of the nine repos.
> The remeasured import-SHA column is A4 in §6A.1. Read A4, not this table.

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
├── gk-tests/             SEALED — cross-repo suites only; the split places 0 files and check enforces it
├── gk-fusion/            Injector + 3 hosts, Launcher, game-profiles, live-probe, release
├── gk-content/  PRIVATE  authored content: our names, flavour, registries
├── gk-data/    PRIVATE  the derived corpus: packs/fusion/data/{seed,generated}/
└── gk-assets/            art and icons. Already migrated; receives 0 split files
```

Four boundaries the 2026-09-19 plan left open, now decided:

- **Web is `gk-web`, not gk-core.** Separate toolchain, separate bundle, separate failure
  mode; Node is developer-only and never ships. It still *serves* from the Server's
  `wwwroot` and binds the same `Contracts` DTOs, so web and server ship as one release.
  That is a cross-repo note, not a reason to merge the trees.
- **`gk-content` vs `gk-data` is authored vs derived.** One repository may not carry the
  game's own written identity and a corpus derived from another game and stay honestly
  private.
- **`gk-tests` is sealed, and it is empty by decision rather than by accident.**
  It deliberately receives **zero** migrated files: path-owned verification co-locates a test
  with the code it tests, and a cross-repo lookup rots. `apply` reports it `unchanged`.
  Shared gate definitions, shared harness logic and workspace policy are **gk-workflow's**
  single source of truth, and a second copy of one inside a sub-repository is the competing
  copy the ownership principle forbids — so they do not move to gk-tests. They are gk-workflow's,
  which is a different statement from where they are today: `report.json` at the import SHA puts
  `scripts/verification-boundaries.v1.json`, `scripts/enforcement-registry.v1.json` and
  `scripts/guard-verification-boundaries.py` in **gk-core**, under the blanket `scripts/**` rule.
  Re-routing that shared-gate surface to the root is the same class of defect and is **not**
  changed here — see §6.4, which names it as an open item with the file that owns it. Nothing in
  the legacy monorepo is a cross-repo suite, because before the split there were no
  repositories to span.
  This is enforced, not described: `gk-tests` carries a `seal` in `layout.v1.json`, `load_rules`
  refuses any rule targeting it unless the rule sets `"entrypoint": true` **and** carries its
  own reason, and `check` asserts the staged tree on every route (primary, `copies`, `template`).
  See [gk-tests-topology-reconciliation.md](gk-tests-topology-reconciliation.md).
- **`gk-assets` is CC BY 4.0 for art, MIT for `tools/**`.** The 2026-09-19 plan flagged
  this itself — "MIT on art lets anyone reuse Keepverse art commercially". Splitting code
  from art is deliberate: CC BY on source code is an anti-pattern.

`blender/**` (258 tracked files) had no owner at all until 2026-09-27. It was then given six
migration rules, and on 2026-09-28 the owner ruled the art **already merged** and the folder
is theirs to clean up. It is now a single `drop` rule, so gk-assets receives 0 split files and
its improved copies cannot be reverted. See §6.1 for what that discards.

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

kvsplit is 15 implementation modules in Python plus `__main__`, **94 tests green** across 5
test files (measured 2026-09-30: `python -m pytest tests/ -q` → `94 passed`; it was 80 across
4 before the gk-tests seal added `tests/test_topology_seal.py`), CI at
`.github/workflows/kvsplit.yml`. Two runs from the same SHA and the same rules produce the
same output digest.

Six contracts were added on 2026-09-27, each discovered by measuring the real workspace
rather than by design, and none of them is in the 2026-09-19 plan:

| Contract | Why it exists |
|---|---|
| `testProjectGlobs` waives the direction contract for test projects | §1.7 |
| a `drop` rule also authorises dropping a non-blob entry | a symlink never reached ordinary classification, so 222 were unresolvable |
| `apply` refuses to overwrite a committed file that differs | `preserve` stopped deletion, never overwriting: 38 files, 28 in gk-assets including 7 `.blend` scenes and 8 rendered sheets |
| `apply` reports a repo that receives nothing as `unchanged` | `git commit` on an empty index is an error, and gk-tests is that case |
| `preserve` must list every live file the split does not produce | measured, not guessed: 96 hand-authored files would have been deleted, 84 in gk-assets |
| `preserve` also stops apply **writing** a path, not only deleting it | it stopped deletion but not overwriting, so the 25-line template `AGENTS.md` would have replaced 7 hand-authored 40-line guides. A preserved path is the repo's, not the split's |
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

## 2. Phase A — the precondition: one branch

**No migration work starts until the source repository holds exactly one branch, `main`,
with every other branch — local, remote, and every linked worktree — deleted.**

**This phase belongs to the owner and their other agents, not to this program.** It is
recorded here as a gate condition with an exit test, and nothing more: the branch-by-branch
merge-or-abandon decisions, the session closures and the deletions are that stream's work,
carried out under their own fences. This program does not touch a branch, a worktree or a
session record.

### A.0 Why it gates the migration

`kvsplit` reads a pinned SHA, so a moving branch cannot corrupt a stage. But a *branch* is a
claim about what the import contains, and while several exist the repository makes several
contradictory ones: a green rehearsal against an older SHA, a 201-commit gap between `main`
and the working branch, four unpushed commits, and three session records that still read
`active`. Phase A removes the ambiguity so the import SHA is a fact rather than a guess.

### A.1 Exit test — five checks, all must hold

Run against the source repository when the owner declares Phase A met:

| # | Check | Command | Passes when |
|---|---|---|---|
| 1 | One local branch | `git branch` | exactly one line: `main` |
| 2 | One remote branch | `git ls-remote --heads origin` | exactly one ref: `refs/heads/main` |
| 3 | No linked worktrees | `git worktree list` | exactly one entry, the main checkout |
| 4 | Clean tree on main | `git status --porcelain` | empty, on `main` |
| 5 | No active fences | `python scripts/session-boundary-check.py` | no record reads `active`; `DRIFT (n)` is 0 |

Measured when this was written, for reference only — **re-read, do not quote**:

```
current branch   features/mega-merge   (upstream +4)
local branches   5      remote branches  9 under origin/, plus 5 stale refs
worktrees        3      main vs working  201 behind, 4 ahead (merge markers #18-21 only)
active records   3      dirty            1 untracked file
```

Four branches held work that is not in the working branch — `ps1ban/l3-checks` (3
commits), `ps1ban/l4-artifacts` (1), `rescue/corpus-bcu211-itemseedgen-run` (1) and
`origin/worktree-rift-gate-20260914` (1). One of them, `ps1ban/l3-checks`, is **not**
redundant: it carries 17 ports built on a shared 426-line `checks_lib.py` harness with a
408-line test, against 16 standalone ports on the working branch, and neither imports the
other's approach. That is flagged here as **information for that stream**, not a
recommendation from this one. `origin/worktree-rift-gate-20260914` is provably empty — 0
files differ from the working branch.

### A.2 What is NOT re-pinned here

**The import candidate is not the import SHA.** Phase 3 still runs after Phase A and still
lands source commits, so the import SHA is re-read at KS4.1 (§4.1). Re-running is cheap
because staging is deterministic and tracks paths: four branch moves during the writing of
this document each added and deleted zero files and left the placement figures identical.

---

## 3. Phases 0–2 — done

| Phase | Block | Evidence |
|---|---|---|
| 0 — decide | KS0.1 | `docs/architecture/decisions/world.md:27` "Locked (owner-approved plan, gate G1)" |
| 1 — build kvsplit | KS1.1–1.3, 1.10–1.15 | 15 implementation modules; `hash`, `lossy-check`, `index`, `reindex`, `apply`; rehearsal 2026-09-19 with **0 lossy findings over 11,133 files**, second run a no-op |
| 1b — move-first tools | D10 ruling | the `hash` → `lossy-check` → `index` → `reindex` chain above |
| 2 — rules, dry runs | — | `unplaced 0`, `balanced True`, deterministic, 94 tests green (2026-09-30) |

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
with the tree and is reconciled in Phase 6; KS3.2 says so in as many words. The 2,514
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

### 6.1 The 3 remaining overwrite clashes — all three are `.gitignore`

This was 38 and is now 3, for two separate reasons worth keeping distinct.

**28 of them were `blender/` and are gone by decision.** The art was already merged into
gk-assets and improved there; the split re-importing the legacy copies would have reverted
7 `.blend` scenes and 8 rendered sheets. `blender/**` is now a single `drop` rule, so
gk-assets receives nothing and its improved files are untouchable. The owner accepted that
this also discards what was never migrated: 102 superseded `v2` renders, 42 lookdev
reference renders, 3 ice-shield authoring workbenches, and the whole `vfx/hit_impact/`
sub-program (README, `effect.json`, `.blend`, 4 sheets). That is recoverable from the source
repository's history for as long as it is not archived, which makes **G3 a real deadline for
that one decision** rather than a formality.

**7 were `AGENTS.md` and are gone by fixing the tool.** `preserve` stopped apply *deleting*
a file but not *writing over* it, so the split's 25-line template would have replaced the
hand-authored 40-line guide in seven repos. `preserve` now means what everyone assumed:
**this path is the repo's, not the split's.** A preserved staged path is kept, not written,
and is reported on the result line. `AGENTS.md` is preserved in all nine repos.

**The 3 that remain are `.gitignore` in gk-core, gk-forge and gk-fusion, and the staged
version should win.** The live ones are 57-line generic templates; the staged one is 208
lines carrying `**/dist/`, `**/node_modules/`, `**/data/icons/`, the live SQLite databases
and the `artifacts/*` + `!artifacts/ci-drop-into-game/` nuance. Overwriting the template with
it is a correction, not a loss — without it, build output and a live database appear as
untracked in three repos. So KS4.2 runs with `--accept-overwrites`, and the commit message
should say why those three were accepted.

### 6.2 gk-assets is dirty

**36 entries, and it moves** — 9 modified (`SKILL.md` × 2, `.gitignore`, two
`assets/vfx/ice_shield/` READMEs, `tools/build.py`, `tools/verify_all.py`, `vfx/README.md`,
`vfx/index.json`) and 27 untracked (earth_shield VFX sub-programs, ice mirror textures, new
`tools/*.py`). This is live authored work, not debris. `apply` refuses on a dirty tree,
correctly. It must be committed under its own session before KS4.2 — and re-measured then,
because the count is growing while the art session works.

### 6.3 The 2,514 residue items

| Kind | Count | Nature |
|---|--:|---|
| `path-literal-moves` | 2,120 | mechanical but voluminous; mostly L2 (seedsmith) and L4 (scripts + CI) |
| `content-root-consumer` | 388 | files resolving a content root; 160 in seedsmith, the rest across test projects |
| `dead-rule` | 6 | **pre-existing and not ours**: 6 ownership rules name `.ps1` files the ps1-ban program already ported to `.py` |
| `content-in-public-repo` | 1 | a **synthetic test fixture** — `tools/ip-censor/tests/fixtures/registry/remediation/top-level-meta.json` carries `"model": "fixture-model"`, `"promptVersion": "fixture/1"` |

Residue is **growing, not regressing**: 951 → 383 at legacy `50d174e0`, and 2,514 now,
because the repository added content and paths while the residue work was in progress. The
6 dead rules are the one class that should be *removed* rather than reconciled — the rules
name files that no longer exist.

The 1 fixture is a false positive by intent, not by accident: 1,321 real files carry
generator provenance and all of them are in private repos; only this synthetic one sits in a
public one. Either the guard learns a fixture from its `fixture/` path, or the fixture's
values stop looking like provenance. Both are one-line changes; neither is urgent.

### 6.4 gk-tests is sealed and empty, and that is the whole design

`apply` reports it `unchanged` because the split places nothing there, and that is now a
**rule** rather than the absence of a matching pattern. `gk-tests` carries a `seal` in
`layout.v1.json` carrying its own reason; `load_rules` refuses any ownership rule that targets
it unless the rule sets `"entrypoint": true` and carries its own reason; and `check` asserts
the staged tree on every route — primary placement, `copies` row and `template` row alike.

**It does not need the gate definitions, and moving them there would be the defect.** The
earlier revision of this section proposed handing gk-tests the per-repo verification boundary
declarations, the cross-repo suite and a `ContentIntegration` category. That is wrong, and the
error is the one the workspace ownership principle exists to prevent: a second copy of shared
gate policy inside a sub-repository is a competing copy, and two copies of a boundary map
diverge silently. Those declarations are workflow-owned path rules, so they belong to
`gk-workflow` — one copy, reachable by every repository's CI.

What legitimately belongs in gk-tests is only a suite that **spans repositories**, and nothing
in the legacy monorepo qualifies: before the split there were no repositories to span. If a
genuinely cross-repository suite is ever written it is committed to `gk-tests` directly, as
`README.md` and `AGENTS.md` already were — never routed there by the split, because no
ownership rule may name a sealed repo. The `entrypoint` exception is for a CI file, not for
content.

The one capability a platform can force is a CI file inside a sub-repository. That stays a thin
entrypoint to workflow-owned policy and tooling — never a copy of it.

See [gk-tests-topology-reconciliation.md](gk-tests-topology-reconciliation.md), which also
records the larger finding this section's correction exposed: the same principle violation
exists at `scripts/**` in gk-core, and it is not confined to gk-tests.

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

## 6A. Auditing the migration

Everything below is a **measurement with a stated threshold**, not a judgement. Each row
names what would make it fail, so a reader can disagree with the threshold rather than
guess at the intent. "It looks fine" is not a row.

### 6A.1 Completeness — did everything arrive?

| # | Check | Command | Passes when |
|---|---|---|---|
| A1 | The reconciliation balances | `stage` | `tracked = placed + dropped + unplaced` and `unplaced 0`. Remeasured at import SHA `effc51d9b`: `15020 = 14538 + 482 + 0`, balanced True. The figures this row originally carried (`14900 = 14418 + 482 + 0`) predate the merge of `features/mega-merge` into `main` and were stale |
| A2 | Nothing is unaccounted for | `hash --source <sha>` then `lossy-check` | **0 findings.** Every legacy file is placed with its staged bytes or dropped by a rule; every moved file is explained by a report row, a template or a preserve glob. **Met at 0 losses** — see the note below this table |
| A3 | Every drop is deliberate | `report.json` → `dropped[]` | 482 entries, each traceable to a rule. 258 are `blender/` (art already in gk-assets), 222 are skill symlinks |
| A4 | Per-repo arrivals match the plan | `report.json` → `placedPerRepo` | Remeasured at import SHA `effc51d9b`: root 5108, gk-core 3860, gk-data 3232, gk-web 1108, gk-forge 791, gk-fusion 438, gk-content 1, gk-tests 0, gk-assets 0. This row originally read root 5105, gk-core 3784, gk-data 3172, gk-forge 785, gk-fusion 463 — all pre-merge and stale |
| A5 | Byte-for-byte, not just present | sha256 in `report.json` | the staged sha256 of each file matches the file in the target repo after `apply` |

A5 is the one that catches a partial write, which a file count never would.

**A2 needed the checker repaired before it could report anything true.** Run against the
applied workspace it produced **221 findings where the rehearsal had produced zero**, and not
one of the 221 was data loss: 209 were gk-assets (out of scope, so correctly untouched, but
`lossy_check` derived "in scope" from the report's rows without the primary-placement rule
`apply` uses), 9 were `preserve`d paths reported as `altered` (where different bytes is the
design working), 1 was a `copies` row planned for an out-of-scope repository that `apply` never
writes, and 2 were documents committed after the import. A gate that cannot pass on a workspace
anyone has done any work in is not a gate. After the repair: **0 losses, exit 0**, with the 2
post-import additions reported under their own kind and not counted as loss.

### 6A.2 Fidelity — is it the same content?

| # | Check | Passes when |
|---|---|---|
| B1 | Determinism | Two `stage` runs from the same SHA and rules give the same `outputDigest`. Verified today: `2655c5543cd0` twice |
| B2 | Rule stability under content churn | Re-stage at a newer SHA: placement is unchanged when the new commits add and delete no paths. This held across 4 branch moves today |
| B3 | Generators reproduce | every `*Gen --check` is byte-identical to the import SHA |
| B4 | Goldens unchanged | the guard suite's golden files compare equal pre- and post-move |
| B5 | No silent overwrite | `apply` refuses on any committed file that differs, except the 3 accepted `.gitignore` in §6.1 |

### 6A.3 Function — does it actually work?

| # | Check | Passes when |
|---|---|---|
| C1 | gk-core builds and tests with **every sibling absent** | green. This is the public-CI condition: gk-core is public and gk-data/gk-content are private, so a core test that needs real content is a defect, not a local pass |
| C2 | Each repo builds and tests with siblings at lock SHAs | green per repo |
| C3 | Content resolves through the pack root | the 45 routed C# readers and 4 of 6 Python consumers resolve `ContentRoot` / `content_root()` in the split layout. A **missing root throws**; a silent fallback is a failure |
| C4 | gk-web ships as one release with the server | its static build is served from the server's `wwwroot` and binds the same `Contracts` DTOs |
| C5 | Public repos contain no derived content | no `data/seed/**` or `data/generated/**` path in a public repo; no generator provenance (`_meta.model` / `promptVersion`) outside a fixture |
| C6 | The private boundary holds | gk-data and gk-content are private and stay private; no public repo's history contains their content |

C1 and C6 are the two that catch the failure this migration is most likely to have: content
leaking into a repo the public can read, or a core test that only passes because a private
sibling happens to be checked out on the author's machine.

### 6A.4 Live — does the game run from the new layout?

| # | Check | Passes when |
|---|---|---|
| D1 | The lawn is entered from the Keepverse layout | a real level loads, not a fixture |
| D2 | A real write is read back through the normal path | `/api/aptitudes/unique/allocate` allocates, then the allocation is read back through the ordinary endpoint — not through a debug surface |
| D3 | The injector connects to the server in its own slot | the slot's own port on both sides, never a hard-coded one |

**A response body is not proof of any of D1–D3.** Read the changed state back through
the normal path. The `bound-loadout-hub` incident shipped end-to-end `ok:true`-shaped
evidence for a feature that was broken, because the probe read back through the same
injector that produced it. That is the failure mode this section exists to prevent.

### 6A.5 What the audit does not prove

- That the residue is *closed*, only that it is counted. 2,514 items move to Phase 6.
- That a preserved file is *correct*, only that the repo's own copy survived.
- That a private repo's content is legally clean. That is the ip-censor guard and it is a
  gate (G2), not an audit row.
- Anything about whether the split was the right call. That is the owner's.

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
2. **KS3.0 / KS6.0 owner charter** — runtimes, models, budget, stop rule, recorded before
   any reconcile worker starts.
3. **Docs placement (D1)** — 2,145 files currently all route to the root. Host docs going to
   `gk-fusion/docs/` is a decision that has not been expressed as rules. Confirm the
   boundary, or accept everything in the root.
4. **The 3 `.gitignore` overwrites** — §6.1 argues the staged version must win. Confirm, so
   KS4.2's `--accept-overwrites` is a decision on the record rather than a convenience.
5. **G3 as a deadline for `vfx/hit_impact/`** — dropping `blender/` discards that sub-program
   recoverably only while the source repository exists. Archiving at G3 makes it gone.
