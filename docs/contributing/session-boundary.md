# Session boundary standard

**Status: binding for every automated session.** A session must establish and record its boundary
before its first edit. The boundary is what keeps concurrent agents from crossing paths, and it is
the contract `scripts/session-boundary-check.py` enforces.

This file is the *policy*. The *record* is one JSON file per session under
[`tasks/sessions/`](../../tasks/sessions/README.md). The *procedure* is the `/session-start` command.

---

## 1. What a session boundary is

One session = **one problem**, not one program. The owner assigns an individual problem to each
session precisely so two agents never work the same files. That is the unit this standard protects.

`features/derived-stat-extension` and `main` are long-lived integration branches; several programs
converge on them. A session boundary says, for this session only:

| Field | Meaning | Example |
|---|---|---|
| `session` | stable id | `actor-hub-20260912-a3f2` |
| `program` | which program from `AGENTS.md` | `actor-hub-and-combat-power-solid-fixing` |
| `problem` | the one problem this session solves | `T6: delete BattleStatComposer` |
| `mode` | `direct` or `worktree` | `direct` |
| `branch` | branch this session commits to | `features/derived-stat-extension` |
| `worktree` | absolute worktree path, or `null` | `null` |
| `paths` | paths this session OWNS and may edit/commit | `["gk-core/src/FusionRpg.Core/Battle/**"]` |
| `started` | ISO-8601 UTC | `2026-09-12T08:50:00Z` |
| `status` | `active` · `merged` · `abandoned` | `active` |

**`paths` is the load-bearing field.** It is both an edit fence and the `git add <paths>`
list. A path outside your boundary belongs to another session; do not edit it, do not revert it, do
not stash around it.

---

## 2. Defaults (owner chooses per session)

These are the repo's defaults; the owner may override any of them at session start.

| Question | Default | When to change |
|---|---|---|
| Mode | **`direct`** — edit the current branch in the main worktree | Choose `worktree` when the session is long, risky, or overlaps another active session's paths |
| Branch | **one shared integration branch** (`git branch --show-current`) | Choose a per-session branch when the session should not land until reviewed, or when the owner wants a separate merge point |
| Concurrency | **assume parallel sessions exist** | Never assume you are alone: read the other records first |
| Scope | **one problem**, with `paths` limited to what that problem touches | Split the problem or hand it to a worktree if it spans two programs |

Mode `direct` is cheap and needs no setup. Mode `worktree` is isolated but must be set up (see §5).

### Direct (default)

- Commit to the current branch with `git commit`, `paths` limited to your boundary.
- Before committing, `git status` will show other sessions' dirty files. **Include only your
  `paths`.** A broad `-a`/`all=true` is how another session's half-finished file gets swept in — the
  exact failure that produced this standard.

### Worktree (opt-in)

- Each worktree is a separate checkout on `worktree-<session>` off the chosen base.
- The session commits inside the worktree; the **owner merges the branch** when green. Worktrees are
  not shared, so there is no file-level interference at all.
- Setup is automated by [`.kilo/setup-script.ps1`](../../.kilo/setup-script.ps1).

---

## 3. The record — one file per session

Records live at `tasks/sessions/<session>.json` (tracked) and are committed with the session's first
change. **One file per session** — never a shared registry file — so two sessions starting at once
cannot conflict on the record itself. The "index" is the directory listing; it is read, never written
by two agents.

Template: [`tasks/sessions/_template.json`](../../tasks/sessions/_template.json).

Local runtime detail that churns (current task, next task, evidence pointer, pending command) lives
under `.kilo/sessions/<session>.json` (gitignored, machine-local). Keep the tracked record stable;
keep the local file honest. Neither is a substitute for the evidence ledger.

---

## 4. Starting a session (procedure)

Run `/session-start`, or do it by hand:

1. **Read** every `tasks/sessions/*.json`, `git worktree list`, `git branch --show-current`, and
   `git status --porcelain`.
2. **Check for crossing**: does any *active* record's `paths` overlap the paths you are about to
   touch, or claim the same branch in `direct`/`worktree` mode? If yes, stop and resolve with the
   owner — either take a worktree, or narrow your scope.
3. **Ask the owner** the §2 questions (mode, branch, one problem, paths). Record the answers. A
   creative program does not ask here: its intake already happened, and its procedure fixes the
   answers — `worktree` mode, one record per program and per sub-program, and paths that start at its
   own docs ([creative-mode.md](creative-mode.md) §11, §13).
4. **Write** `tasks/sessions/<session>.json`.
5. **Then** begin work. Commit inside your boundary as you go.

Re-run `/session-start` only to change the boundary or close it. On close, set `status` and commit
the record (a new commit, never an amend).

---

## 5. Worktree setup

`.kilo/setup-script.ps1` runs once when Agent Manager creates a worktree. It copies `.env`, restores
Python deps for `gk-forge/tools/seedsmith`, runs `npm ci` for the web, and prints what still needs the owner
(`FUSIONRPG_GAME_DIR` is machine-local and never committed). The script is itself machine-local — it
is excluded through `.git/info/exclude`, so it exists only in the main checkout. A session that
creates its own worktree runs it from there with `$env:WORKTREE_PATH` and `$env:REPO_PATH` set, or
does the same steps by hand.

### `AGENTS.md` and `CLAUDE.md` are load-bearing for tests

Both files are **tracked**, so `git worktree add` creates them in every new worktree. They are not only
instructions: **~36 test files use `AGENTS.md` as their repo-root marker** — they walk up from
`AppContext.BaseDirectory` looking for it and throw `"repo root not found"` without it.

History: until 2026-09-19 (`b979e496`) both files were gitignored, and a fresh worktree without copies of them failed
those tests for a reason unrelated to the change under test (found 2026-09-13, when a clone reported
367 Core.Tests failures that were all one missing marker). The setup script still copies them as a
fallback (machine-local `setup-script.ps1`, which does not exist in a clone or a new worktree).

### Before editing a file another stream might own

`git status` shows their dirty work; that is information, not permission. Check the concrete overlap
rather than assuming a whole-file conflict:

1. `git worktree list` and every active record in `tasks/sessions/*.json` — who claims the path.
2. If they do, compare the **region** on their branch:
   `git diff <base>..<their-branch> -- <file>`.
3. Only a real region overlap needs coordination; a file claimed by two sessions but changed in
   different regions merges cleanly.

Worked example (2026-09-13, `battle-timeline` B40): `gk-core/src/FusionRpg.Server/WebMatchService.cs` was
claimed by `solid-run-20260912-eb53`, but its commits touched only lines 449–572 while the edit was at
321–340, and the catch region was byte-identical on both branches — so the edit merged cleanly and was
committed without touching their work. **Recording the crossing in your own session record is what makes
that auditable**, not the assurance that it went fine.

`scripts/session-boundary-check.py` validates the records and reports drift:

- a record whose `worktree` no longer exists, or whose `branch` is gone;
- two active records claiming overlapping `paths` — unless **both** are in worktree mode
  (`session-boundary-check.py:106`): two worktrees cannot write each other's files, so they meet only
  at the merge, where the region check above applies;
- an orphan `worktree-*` branch that no record claims. `worktree-agent-<hex>` branches are the
  exception: the Claude Code harness creates them for an Agent call with worktree isolation, they
  belong to the session that spawned the agent, and the checker lists them for information only.

A session in `direct` mode whose `paths` fall under an active worktree session's globs is reported as
drift even when the regions differ. Take a worktree for that session.

Run it at session start; a clean run is the precondition for editing.

**`-Session <id>` scopes the verdict to one session.** Drift that names that session — its record,
its branch, an overlap with its paths — fails; drift that belongs only to other sessions is printed
under its own heading and does not fail. `verify-change.py` passes `-Session` to this guard, so
another session's leftovers never block your verification. They are still never yours to fix: a
record, branch or worktree you did not create is not yours to remove or re-mark.

---

## 6. Hard rules (restated)

- **Do not edit outside your `paths`.** Another session's dirty file is not yours; leave it.
- **Never** `git stash`/`checkout`/`reset` around another session's work, and never a bare
  `git checkout -- <path>` on a file your boundary does not own. Both destroy uncommitted work.
- **Never** `git add -A` / `git commit -a` unless the owner says the whole tree is one session's.
- **One problem per session.** If a second problem appears, start a second session or hand back.
- **Commit with plain git**, explicit paths only ([agent-git.md](agent-git.md)); push and pull
  requests only when the owner asks.
- A closed boundary is `status: merged` (or `abandoned`) in a new commit — not a deletion, so the
  history of who owned what survives.

---

## 7. Shared runtime resources

`paths` fences files. Some things every session shares are not files in its tree, and two sessions can
collide on them even when their `paths` never meet.

| Resource | Why it is shared | Rule |
|---|---|---|
| `dist/FusionRpg.Server/` and its `data/` | The owner's published server and their real save | Only the main checkout publishes there (`deploy-play.py`). A worktree session runs its own server from its worktree with `FUSIONRPG_DATA` set to a scratch directory and `FUSIONRPG_URLS` set to a free port (`gk-core/src/FusionRpg.Server/Program.cs:13-14`, `:378`) |
| Port 5088; port 5173; port 4173 | The owner's server; Vite's dev server; Playwright's preview server (`reuseExistingServer` outside CI) | A worktree session listens on another port |
| The game install | It holds one injector build at a time, and every session's live probe and the owner's own play see it | A deploy from a worktree replaces that build for everyone. Record it in the session's `notes`, say it in the hand-off, and never deploy while another active record names a live probe |

Creative runs apply these as hard limits ([creative-mode.md](creative-mode.md) §3, §8.3).
