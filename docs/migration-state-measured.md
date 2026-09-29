# Migration state, measured

Written by the context-collector lane. Read-only: this lane edited no repository, ran no
`apply`, passed no `--confirm-migration-start`, and issued no `reset`/`checkout`/`stash`/`clean`.

Every number below comes from a command listed beside it. Where a figure was supplied to this
lane by the manager it is marked **[manager]** and is not re-derived. Where a figure exists only
as a written claim and this lane did not reproduce it, it is marked **UNVERIFIED** — a valid
answer, not a gap to be filled with an estimate.

Measurements taken 2026-09-30 against source `effc51d9b55f78aa7a5c47e14eef0e61b690e5eb`.

---

## CORRECTIONS — read before the tables below

The lane's snapshot was accurate when taken. Four claims in it were made stale within the
hour by the manager, and two of them were the lane's most valuable findings. The lane's
reasoning stands; only the state moved. Nothing below has been edited, so the snapshot
remains auditable.

| The lane says | Now | Why |
|---|---|---|
| §0.1 and conditions 1, 12: **"the authoritative plan is missing"** | **FALSE — it was deleted, and is restored** | The import's delete loop removed `docs/keepverse-migration-plan.md`: it existed before the import, the source repo has no such file, and it was not `preserve`d. This is hazard H1 in the goal prompt, firing on the manager's own file. Restored byte-identical from `1a3e508` (35,951 bytes, 630 lines, sha256 verified) and committed `be7d335`, which also **preserves** the plan, the goal prompt, the lane-setup notes, the measured state and `docs/migration-*.md` at the root, so it cannot recur. The lane's finding was correct and load-bearing. |
| Condition 13: **"six repositories are +1 ahead — NOT MET"** | **MET** | The manager pushed them under authorization 7 after the lane measured: gk-core `34bf27d`, gk-forge `2c2978c`, gk-web `c732330`, gk-fusion `d740f2d`, gk-content `d2337d8`, gk-data `9467b58`. All nine repositories are now 0 behind / 0 ahead and clean. No force was used. |
| Condition 2 caveat: **"the charter ledger record is uncommitted"** | **RESOLVED** | The five uncommitted ledger rows are committed in the source repo as `11eff9c4c`, which also leaves that repository clean — the lane correctly identified that five uncommitted lines were standing between the migration and Phase A's clean-tree exit check. Deliberately not pushed: Phase A is the owner's separate stream working in that repository. |
| Conditions 3, 4, 6, 7: artefact **not on disk** | **partly resolved** | The lane is right that no on-disk artefact carried the import-SHA figures. The lossy-check run and its report now exist on disk, and the preservation fix is verified by computing what a re-apply would delete rather than running one: root is in scope and **0** tracked control documents would be removed. |

**A lesson worth carrying, in the lane's own words:** it recorded that a first, looser A7
scan reported four contaminated public repositories and that those hits were code and
documentation paths merely *mentioning* creatures. A needle that matches a word is not a
check. That is the same failure as reporting "unplaced 0" from a count that excludes
copies — arithmetic that looks like evidence.

---

## 0. Four things a reader must know before using this file

**0.1 — The authoritative plan is not on disk.** `docs/keepverse-migration-plan.md` does not
exist in `Keepverse/docs/`, in the source `docs/`, or at the source root. It is named as
authoritative by `docs/migration-goal-prompt.md` and by
`tasks/keepverse-split-plan.md:3-27` ("The authoritative version is
`Keepverse/docs/keepverse-migration-plan.md`", and Phase A is "§2 of the authoritative plan").
What is on disk instead is the **superseded** `tasks/keepverse-split-plan.md` in the source repo,
whose own header disclaims itself. Anything that cites "the authoritative plan §N" — including
Phase A's five exit checks, which this lane was asked to assess — **cannot be checked against a
source document**, only against the todo's restatement of it.

**0.2 — Every `report.json` on disk is a stale rehearsal, none at the import SHA.** All three
were read:

| Artifact | `sourceSha` | `rulesDigest` | `outputDigest` | tracked | dropped | unplaced | balanced |
|---|---|---|---|--:|--:|--:|---|
| `.staging/report.json` | `50d174e0…` | `eca1fc35…` | `b66faf49…` | 11066 | 2 | 0 | true |
| `.staging-verify/run-1/report.json` | `7dcbf38d…` | `f4295df0…` | `62b2d922…` | 11026 | 2 | 0 | true |
| `.staging-verify/run-2/report.json` | `7dcbf38d…` | `f4295df0…` | `62b2d922…` | 11026 | 2 | 0 | true |

Compare [manager]: `effc51d9…` / `0fe37c77…` / `b464968f…` / tracked 15020 / dropped 482.
**None of the three matches the import run.** A reader who opens `.staging/report.json` to check
the migration reads rehearsal numbers from an older source tree — the same class of trap as H2
in the goal prompt, where a row that reads plausible is not the row that matters.

One determinism fact *is* on disk and is real: `run-1/report.json` and `run-2/report.json` are
byte-identical (SHA256 `33450ADE3730763F27D0D85F870F65FE33C9243CD94E79FF1B0604BD24051BFB`).
That proves repeat-run determinism **at `7dcbf38d`**, not at the import SHA.

The two stale reports also predate the topology: their `placedPerRepo` names six targets and has
no `gk-web` and no `gk-content` row at all.

**0.3 — An on-disk ledger asserts the pushes happened. They have not.** The source repo's one
dirty file, `tasks/keepverse-split-ledger.jsonl`, carries five **uncommitted** records
(`git diff --stat`: `1 file changed, 5 insertions(+)`; HEAD holds 17 records, the working tree
22; the last committed record is dated 2026-09-24). Record 22 (`mark: import-pushed-20260930`)
states:

> "Import commits pushed, no force: gk-workflow 8944671 (already on origin), gk-core 34bf27d,
> gk-forge 2c2978c, gk-web c732330, gk-fusion d740f2d, gk-content d2337d8, gk-data 9467b58.
> **All nine repositories now 0 behind / 0 ahead and clean.**"

Measured (§B): **six** repositories are `+1 / -0`, not `0 / 0`. The claim is false as of this
measurement. It is also uncommitted, so no lane can inherit it as fact. This is recorded here
rather than corrected in place because the file is outside this lane's write fence.

**0.4 — The goal prompt's push count is off by one.** `docs/migration-goal-prompt.md:30` says
"Import commits are **local and unpushed** in 7 repos." Seven repositories hold an import commit;
**six** of those are unpushed. `gk-workflow`'s import commit `8944671` is already on `origin`:
`git merge-base --is-ancestor 8944671 @{u}` exits `0`.

---

## A. Source repository

`D:\Works\source\plant-vs-zombie-rise-of-summoner`

### A.1 Identity and cleanliness

| Item | Value | Command |
|---|---|---|
| Branch | `main` | `git rev-parse --abbrev-ref HEAD` |
| HEAD | `effc51d9b55f78aa7a5c47e14eef0e61b690e5eb` | `git rev-parse HEAD` |
| Subject | `Merge branch 'features/mega-merge'` | `git log -1 --format=%s` |
| Date | `2026-09-30 03:39:45 +0700` | `git log -1 --format=%ad --date=iso` |
| Author | `letuhao1994` | `git log -1 --format=%an` |
| Tracked files | **15020** | `git ls-files \| Measure-Object -Line` |
| Dirty entries | **1** | `git status --porcelain=v1 \| Measure-Object -Line` |
| Upstream | `origin/main`, `+0 / -0` | `git rev-list --left-right --count HEAD...@{u}` |
| Worktrees | 1 | `git worktree list` |

HEAD matches **[manager]**'s source SHA exactly, and the tracked count matches
**[manager]**'s `tracked 15020`.

The single dirty entry is ` M tasks/keepverse-split-ledger.jsonl` — the file in §0.3. It is a
tracked modification, not untracked: `program_status.py` reports `untracked 0, conflicted 0`.

### A.2 Branches, remote heads, worktrees

`git branch -a` — **one** local branch:

```
* main
```

`git ls-remote --heads origin` — **nine** remote heads (exit `0`):

| Remote head | SHA |
|---|---|
| `main` | `effc51d9b55f78aa7a5c47e14eef0e61b690e5eb` |
| `features/derived-stat-extension` | `9533336e8d07c2fd415e6545a7bbc290960ad4e1` |
| `features/mega-merge` | `d057ad359d25edc24c1ce1a66cc02425885af622` |
| `worktree-achievement-title-20260915-7f3a` | `65d6c96e1365e022b4825803fb0351ec7cdacd9d` |
| `worktree-action-dist-phaseA-20260915-9d2b` | `094ca0286279b5f92473f92e30c8863abafdcc4f` |
| `worktree-empire-development-20260915-b7e2` | `2e28fdc9226c897ef5ab6378ca3b66b20739836d` |
| `worktree-passive-tree-repair-20260915-7a1c` | `1c2e87afe9e1b5c49eb0621e463a22ca9effada2` |
| `worktree-rift-gate-20260914` | `f976f3577c9482e6440e22060990953de48a9243` |
| `worktree-species-gear-chain-20260915-9afc` | `ccd8e353526deaa701bc47ad579b2daa1db4a95b` |

`git worktree list` — **one**:

```
D:/Works/source/plant-vs-zombie-rise-of-summoner  effc51d9b [main]
```

`git remote` prints exactly one remote, `origin`
(`https://github.com/letuhao/plant-vs-zombie-rise-of-summoner.git`). But `git branch -a` also
lists tracking refs under **`remotes/local/*`** (2) and **`remotes/origin-local/*`** (3). Those
two remotes are not configured, so those five refs are **stale** — a reader counting branches
from `git branch -a` will over-count by five and will not learn they point nowhere.

Phase A (`KS-A`, todo line 169) requires the source to hold exactly one `main`, with every other
**local branch, remote branch and linked worktree** deleted. Measured: local ✓ (1), worktrees ✓
(1), **remote branches ✗ (9)**.

### A.3 Session-boundary DRIFT

Run as `python scripts/session-boundary-check.py 1>sbc.out 2>sbc.err` in the source repo.
**Exit code `1`.** stdout is 93 688 bytes and ends with the summary line
`[session-boundary] DRIFT (6):` — but the **DRIFT items themselves are on stderr** (932 bytes, six
lines). Reading stdout alone yields an empty list under a heading that says six. Verbatim stderr:

```
  ! ps1-ban-l4-artifacts-20260926.json: branch 'ps1ban/l4-artifacts' does not exist
  ! ps1-ban-manager-20260926.json: branch 'features/mega-merge' does not exist
  ! resume-34-cai2-2-20260925.json: branch 'opencode/resume-34-cai2-2-20260925' does not exist
  ! ps1-ban-l4-artifacts-20260926.json and ps1-ban-manager-20260926.json both claim 'tasks/reports/f13-schema-upgrade-proof.ps1' / 'tasks/reports/f13-schema-upgrade-proof.ps1' while active — narrow the scope or move one to a worktree
  ! ps1-ban-manager-20260926.json and resume-34-cai2-2-20260925.json both claim 'src/FusionRpg.Data/Sqlite/RpgStore.cs' / 'src/FusionRpg.Data/Sqlite/RpgStore.cs' while active — narrow the scope or move one to a worktree
  ! ps1-ban-manager-20260926.json and resume-34-cai2-2-20260925.json both claim 'src/FusionRpg.Server/Program.cs' / 'src/FusionRpg.Server/Program.cs' while active — narrow the scope or move one to a worktree
```

Three classes: three records name a branch that no longer exists; three record pairs claim the
same file while both are active. stdout header: `261 record(s), 3 active`. The three active
records are the ones in the overlap rows.

### A.4 `program_status.py` headline

Run as `python scripts/program_status.py` — **exit `0`**, stderr empty. Headline lines, verbatim:

```
**Head** `effc51d9b` · branch `main` · upstream `origin/main` +0/-0 · dirty 1
         (untracked 0, conflicted 0) · worktrees 0

**122 programs** — 117 measured, 5 unmeasured · **715 open task blocks**, 2892 done
         (164 open blocks carry a blocking signal in their own text).

**Of the 2892 done: 342 have a GREEN acceptance naming a SHA in this head;
         2550 are ticked with nothing behind them.**
```

Note the tension this program itself names: **2 550 of 2 892 "done" blocks have no acceptance
naming a SHA.** For `keepverse-split` the ratio is total — `doneVerified 0`, `doneUnverified 24`.

---

## B. The nine repositories — the push-state record for authorization 7

All on branch `main`, all with upstream `origin/main`, all `dirty 0`. `ahead/behind` is
`git rev-list --left-right --count HEAD...@{u}`; the import-commit column is
`git log --all --oneline --grep='Import snapshot from legacy repo'`.

| Repository | Tracked | HEAD | Subject | Dirty | Ahead / behind | Import commit in history |
|---|--:|---|---|--:|---|---|
| `gk-workflow` (root) | 5157 | `d1bd6a2b` | `kvsplit: lossy-check now tells explained from unaccounted, and passes` | 0 | **0 / 0** | **yes** — `8944671`, already on origin |
| `gk-core` | 3863 | `34bf27d0` | `Import snapshot from legacy repo effc51d9b…` | 0 | **1 / 0** | yes — `34bf27d0` (HEAD) |
| `gk-forge` | 800 | `2c2978ca` | `Import snapshot from legacy repo effc51d9b…` | 0 | **1 / 0** | yes — `2c2978ca` (HEAD) |
| `gk-web` | 1112 | `c732330f` | `Import snapshot from legacy repo effc51d9b…` | 0 | **1 / 0** | yes — `c732330f` (HEAD) |
| `gk-fusion` | 447 | `d740f2d9` | `Import snapshot from legacy repo effc51d9b…` | 0 | **1 / 0** | yes — `d740f2d9` (HEAD) |
| `gk-content` | 5 | `d2337d89` | `Import snapshot from legacy repo effc51d9b…` | 0 | **1 / 0** | yes — `d2337d89` (HEAD) |
| `gk-data` | 3237 | `9467b587` | `Import snapshot from legacy repo effc51d9b…` | 0 | **1 / 0** | yes — `9467b587` (HEAD) |
| `gk-tests` | 4 | `0b3672ac` | `docs: the test platform, and the one decision still open about it` | 0 | 0 / 0 | **none** |
| `gk-assets` | 228 | `b02db755` | `update stale files` | 0 | 0 / 0 | **none** |

**Authorization 7 status: NOT YET EXERCISED.** Six repositories hold an unpushed import commit —
`gk-core`, `gk-forge`, `gk-web`, `gk-fusion`, `gk-content`, `gk-data` — each exactly `+1` ahead of
`origin/main` and `0` behind, so a plain fast-forward push is available in all six and none
requires a force. `gk-workflow` is already published. `gk-assets` and `gk-tests` correctly hold
nothing to push.

Baselines confirmed unchanged, as required: **gk-assets 228 tracked at `b02db75`**, **gk-tests 4
tracked at `0b3672a`**, both clean, both with no import commit. Neither was modified by this lane.

Two supporting readings. `gk-assets`' tracked count and HEAD match **[manager]** exactly.
`gk-tests`' four tracked files are `.gitignore`, `AGENTS.md`, `LICENSE`, `README.md` — the
`AGENTS.md` preserved under H3, with no test platform content. `gk-content`'s five are the same
four plus `content/display/en.json`, consistent with an import commit that places one file.

The root's tracked count is **5157**, where the goal prompt records 5 155 for the import commit;
the two extra files are the post-import `lossy-check` work, whose commit is the root's current
HEAD subject.

---

## C. TODO blocks

From `tasks/keepverse-split-todo.md` in the source repo (363 lines). Shape-map figures from
`python scripts/program_status.py --json`, program `keepverse-split`, declared shape **`R-bold`**.

### C.1 Open KS block ids, grouped by phase

| Phase | Open block ids | Count |
|---|---|--:|
| Phase 0 — decide | — | 0 |
| Phase 1 — build kvsplit | `KS1.4`, `KS1.5` | 2 |
| Phase 1b — move-first tools | — | 0 |
| Phase 2 — author rules | — | 0 |
| Phase 3 — pre-move reduction | `KS3.0`, `KS3.1`, `KS-F3`, `KS3.2` | 4 |
| Phase A — consolidate to one branch | `KS-A` | 1 |
| Phase 4 — freeze and move | `KS4.1`, `KS4.2`, `KS4.3` | 3 |
| Phase 5 — lossy check, index, reindex | `KS5.1`, `KS5.2` | 2 |
| Phase 6 — final check and reconcile | `KS6.0`, `KS6.1`, `KS6.2` | 3 |
| Phase 7 — cutover | `KS7.1`, `KS7.2`, `KS7.3` | 3 |
| **Total** | | **18** |

Line numbers, for citation: `KS1.4`:16, `KS1.5`:18, `KS3.0`:69, `KS3.1`:84, `KS-F3`:145,
`KS3.2`:162, `KS-A`:169, `KS4.1`:179, `KS4.2`:182, `KS4.3`:184, `KS5.1`:187, `KS5.2`:188,
`KS6.0`:190, `KS6.1`:191, `KS6.2`:193, `KS7.1`:197, `KS7.2`:199, `KS7.3`:200.

### C.2 The count is not a work estimate, and the line count is not the block count

**An unchecked `- [ ]` line is not a unit of work.** In this todo a block is a heading-like row
carrying its own `*Accept:*` clause, and a single line of that clause can be ten times the size
of a neighbour. `KS3.1` is one open box and carries five named sub-lanes (L1–L5) with their own
per-slice test evidence; `KS7.3` is one open box and is a gate. Counting boxes measures neither
size nor sequence.

**The raw line count and the shape-map count are different quantities, and for this program they
happen to coincide — 18 and 18 — which is a coincidence, not a rule.** Measured both ways:

| Measure | Value | How |
|---|--:|---|
| Raw `- [ ]` lines in the file | **18** | `Select-String '^\s*- \[ \]'` |
| Raw `- [x]` lines in the file | **24** | `Select-String '^\s*- \[x\]'` |
| Shape-map `openBlocks` | **18** | `program_status.py --json` |
| Shape-map `doneBlocks` | **24** | `program_status.py --json` |
| Shape-map `untickedBoxes` | **18** | `program_status.py --json` |

The raw and shape-map readings agree here. **The same report's other programs show they are
independent**, and in both directions, so the agreement must not be generalised:

| Program | `openBlocks` | `untickedBoxes` |
|---|--:|--:|
| `trade-network` | 162 | **4** |
| `species-gear-chain` | 3 | **287** |
| `npc-story-events` | 93 | 103 |
| `onboarding-rift` | 26 | 111 |
| `keepverse-split` | 18 | 18 |

`species-gear-chain` has 3 blocks and 287 open boxes; `trade-network` has 162 blocks and 4 open
boxes. A burn-down driven by `- [ ]` lines would read those two programs as near-empty and
near-complete respectively — the inverse of the truth. `program_status.py` states the rule itself:
*"A block is a task, not a checkbox line… Every count is a reading of this tree, not a constant and
not a work estimate: an `L` and an `XS` block count the same."*

**A third figure is stale in the documents themselves.** `tasks/keepverse-split-plan.md:13` and the
todo's READINESS note (`keepverse-split-todo.md:332`) both cite "the 24-done / **17**-open block
counts". Measured open is **18**. The `17` predates the addition of `KS-A` (todo line 169), which
is the Phase A block the 2026-09-28 owner ruling created. Anyone reconciling against 17 will
silently drop `KS-A` — the block that gates the entire migration.

### C.3 Acceptance state for this program

`doneVerified 0`, `doneUnverified 24`, `fencedByActiveSessions []`,
`acceptanceArtefactsNamingIt []`, `greenAcceptancesInThisHead []`. All 24 done blocks are ticked
with nothing behind them, and no acceptance artefact anywhere names this program.

Two shape-reading defects, recorded so no lane keys off the tool's ids: the tool truncates the
decimal suffix for this shape, reporting `KS3` for both `KS3.0` (line 69) and `KS3.1` (line 84),
`KS4` for `KS4.1`/`KS4.2`/`KS4.3`, `KS5` for both `KS5.x`, `KS6` for `KS6.0`/`KS6.1`, `KS7` for
all three `KS7.x`; and it reports an **empty id** for `KS-A` (line 169), parsing no identifier at
all. **The todo line number is the only unambiguous identifier.** Residue workers must key on
line numbers, not on these ids.

---

## D. The 14 completion conditions

Verdicts use the goal prompt's `[ADDED 8]` list. **UNVERIFIED is the expected answer for most**;
it means this lane has no evidence either way, and it does not mean the condition failed.

| # | Condition | Verdict | Evidence this lane actually has |
|--:|---|---|---|
| 1 | Phase A's five exit checks pass, owner-verified and recorded | **NOT MET** | Measured against the todo's restatement of Phase A (`KS-A`, A.1–A.6), since the authoritative plan is absent (§0.1). Local branches 1 ✓ · linked worktrees 1 ✓ · **remote branches 9 ✗** · **working tree dirty 1 ✗** · **3 active sessions holding fences ✗** (`session-boundary-check.py`: `261 record(s), 3 active`). `KS-A` is open. No owner-stream record found. The count "five exit checks" could not be checked against any source. |
| 2 | Reconciliation charter on disk | **MET, with a caveat** | Three places: the goal prompt `[ADDED 6]` table; `.claude/opencode-agents/allowed-models.json` (committed — `opencode/space-bunny-free`, `tokensPerLane: null`, `maxConcurrentLanes: null`, no fallback, stop on quota errors, disk-backed exact-SHA evidence); and source ledger record 18 (`kind: charter`, `mark: charter-20260930`). **Caveat:** that ledger record is one of the five **uncommitted** lines (§0.3), so the charter's own home is uncommitted. The two configured agent profiles use `pi` and `anthropic/claude-opus-5` and are **not** chartered for this run. |
| 3 | `stage` at the pinned SHA: `tracked = placed + dropped + unplaced`, `unplaced 0`, `balanced True`, same SHA + same rules ⇒ same output digest | **UNVERIFIED** | [manager] reports 15020 = 14538 + 482 + 0, balanced True, digest `b464968f`. **No artefact on disk carries those figures** — all three `report.json` files are older runs at other SHAs (§0.2). The determinism clause is evidenced on disk only at `7dcbf38d`, where run-1 and run-2 are byte-identical. |
| 4 | `lossy-check` reports zero findings | **MET as reported; artefact uncommitted** | [manager] reports 0 losses, exit 0, with 2 post-import additions not counted as loss. The only `lossy-check` record is source ledger record 19 (`mark: lossy-check-repaired-20260930`, uncommitted), which states the checker first reported 221 findings — 209 of them gk-assets — and that all 221 were accounting failures, not loss. No `lossy-check` output artefact exists on disk. |
| 5 | Every residue id closed with no replacement, **or** named in a report as an open item with owner and reason | **NOT MET** | [manager] measures 2 494 open residue ids: `path-literal-moves` 2 100, `content-root-consumer` 393, `content-in-public-repo` 1. On-disk `residue.json` totals are 926 (`.staging`, at `50d174e0`) and 1 544 (`.staging-verify`, at `7dcbf38d`) — neither matches. The three kinds are **not** named with owners and reasons in any report found; the only residue-named file in `tasks/reports/` is `bcu2-11-residue-map.md`, which belongs to another program. Per the condition's own wording, a carried residue is an open item, not a pass. |
| 6 | A6: gk-assets and gk-tests tracked counts and HEADs unchanged; every other repo's tracked count matches its `report.json` count | **NOT MET (split)** | **First half MET.** gk-assets 228 @ `b02db75`, gk-tests 4 @ `0b3672a`, both `dirty 0`, both with no import commit — identical to [manager]'s baseline. **Second half UNVERIFIED.** The only `report.json` on disk is at `50d174e0` with a **six-target** `placedPerRepo` that has no `gk-web` and no `gk-content` row at all, so no per-repo comparison against the import run is possible from disk. The live tracked counts also include each repo's own preserved files and post-import commits, so they are not the `placed` counts even in principle. |
| 7 | A7: no derived content in any public repository's working tree **or history** | **UNVERIFIED** | Source ledger record 21 (`mark: a7-history-check-20260930`, **uncommitted**) states the check used `git rev-list --objects --all` and found 0 hits for `data/seed/**`, `data/generated/**`, `packs/fusion/**`, `packs/keepverse/**` across root, gk-core, gk-forge, gk-web, gk-tests, gk-fusion, gk-assets; and exactly 1 generator-provenance hit in a public `.json` — the synthetic fixture `gk-core/tools/ip-censor/tests/fixtures/registry/remediation/top-level-meta.json`, carrying `"model": "fixture-model"`, which is the same single item residue reports as `content-in-public-repo`. It also records that a first, looser pass reported 4 contaminated repos and that those hits were code and doc paths merely mentioning creatures or almanac. This lane did **not** re-run the scan. |
| 8 | gk-core builds and tests with every private sibling absent | **UNVERIFIED** | No build or test was run. `gk-core` is 3 863 tracked at `34bf27d0`, `dirty 0`, the import commit is its HEAD. |
| 9 | Per-repository build and test results at the lock SHAs | **UNVERIFIED** | No build or test was run. There is also **no lock file to test at**: `workspace.json` and `workspace.lock.json` are both **absent** from the Keepverse root, so `KS4.3` is unstarted and "the lock SHAs" have no referent yet. |
| 10 | Generators `--check` byte-identical to the import SHA; goldens unchanged | **UNVERIFIED** | No generator was run. The `ks1.15` rehearsal note (`keepverse-split-todo.md:65-67`) records a past clean-clone result at a different SHA, which is not evidence for the import SHA. |
| 11 | Web served from the server; real live lawn entered from the Keepverse layout; a real allocation read back through the normal path | **UNVERIFIED** | No server was started and no live probe was run. |
| 12 | gk-tests topology reconciliation complete **as one change set**, and `stage`/`check` demonstrably enforce it | **NOT MET** | gk-tests is 4 files at `0b3672a`, dated 2026-09-27 — **before** the 2026-09-30 import — holding only `.gitignore`, `AGENTS.md`, `LICENSE`, `README.md`, with no import commit. The change set `[ADDED 5]` names (authoritative plan, topology decision, ownership rules, transforms, templates, task criteria, principles) is not present: the authoritative plan does not exist (§0.1), the topology documents are untouched by the root's one post-import commit (a `lossy-check` change), and no `stage`/`check` enforcement demonstration exists. Nothing in `[ADDED 5]`'s "do not invent work" clause is triggered: an honest reconciliation of gk-tests at 4 files is a valid endpoint. |
| 13 | Import commits and cutover commits pushed, without force | **NOT MET** | Measured (§B): **six** repositories are `+1` ahead of `origin/main` — `gk-core` `34bf27d0`, `gk-forge` `2c2978ca`, `gk-web` `c732330f`, `gk-fusion` `d740f2d9`, `gk-content` `d2337d89`, `gk-data` `9467b587`. `gk-workflow`'s `8944671` is on origin (`merge-base --is-ancestor` exit `0`). Each of the six is `0` behind, so all six are fast-forwardable and none needs a force. No cutover commits exist. An uncommitted ledger record asserts the opposite (§0.3) and is contradicted. |
| 14 | Every authorized todo block carries evidence matching its original criterion | **NOT MET** | `keepverse-split`: 18 open blocks (§C.1), and of 24 done blocks `doneVerified 0` / `doneUnverified 24`, with `acceptanceArtefactsNamingIt []` and `greenAcceptancesInThisHead []`. Repo-wide, 2 550 of 2 892 done blocks have no acceptance naming a SHA. |

**Tally: 2 MET (one with a caveat), 5 NOT MET, 7 UNVERIFIED.** The migration is **not complete**,
and the conditions that are UNVERIFIED are the expensive ones — every build, test, generator and
live-probe condition is unproven, not failed.

### D.1 Dependencies the other lanes will hit

1. **The authoritative plan is missing.** Phase A's exit checks, the topology of record and
   `KS7`'s cutover criteria are all cited to a file that is not on disk. Until it is restored,
   condition 1 and condition 12 cannot be closed on evidence, only on restatement.
2. **The import-SHA staging evidence is not on disk.** Any audit or reconciliation lane that
   re-runs `stage` will regenerate it; any lane that *reads* `.staging/` will read a rehearsal at
   `50d174e0` with a six-repo topology and 11 066 tracked files.
3. **The five uncommitted ledger records are this migration's only written record** of the
   charter, the import-SHA correction, the `lossy-check` repair, the A7 check and the push. They
   are uncommitted in the **source** repo — the repository Phase A requires to be clean before
   the migration proceeds. Committing them is a source-repo write, outside this lane's fence, and
   it is the first thing that would make those five claims inheritable.
4. **Residue ids must be keyed by todo line number**, not by `program_status.py`'s parsed ids
   (§C.3), or `KS3.0` and `KS3.1` will be closed as one row and `KS-A` will have no id at all.
5. **The `17`-open figure in `keepverse-split-plan.md:13` and `keepverse-split-todo.md:332` is
   stale by one** and understates the gate that matters.

---

## What this lane did not measure

- No build, test, generator `--check`, server start or live probe (conditions 8–11).
- No re-run of the A7 history scan (condition 7); the finding is reported as the uncommitted
  ledger's claim, not as this lane's result.
- No re-run of `stage`, `check`, `hash`, `index`, `reindex` or `lossy-check` (conditions 3–4).
  `apply` was never invoked and `--confirm-migration-start` was never passed.
- The five exit checks of Phase A, and the topology of record, because the authoritative plan is
  absent (§0.1).
- `git log --all` for import commits was run per repository; no attempt was made to audit the
  content of those commits.
- Per-file residue identity inside the 2 494 ids — [manager]'s composition is accepted as given.
