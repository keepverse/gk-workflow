# gk-workflow — agent guide

The workspace root. It holds the **rules, the specs and the migration tool**, and
no game code. If you are here to change gameplay, this is the wrong repo.

## The workspace

Eight independent repositories, not submodules. They are untracked here and each
has its own remote:

| Repo | Holds | Licence |
|---|---|---|
| `gk-core` | Contracts, Core, Data, Server, balance numbers | AGPL-3.0 |
| `gk-forge` | seedsmith + the generator family | AGPL-3.0 |
| `gk-web` | Browser control room | AGPL-3.0 |
| `gk-fusion` | Injector, hosts, launcher, live-probe | AGPL-3.0 |
| `gk-tests` | Test platform and gate definitions | AGPL-3.0 |
| `gk-content` | Original names, flavour, registries | AGPL-3.0, private |
| `gk-data` | Content packs / derived corpus | MIT, **private** |
| `gk-assets` | Art pipeline | MIT |

## Read before you propose anything

- **docs/DESIGN-GATE.md** — binding. Find your subsystem in its §1 topic index
  and read the documents that row names, **in this session**.
- **docs/architecture/decisions.md** — locked choices. Change here before changing
  code.

> `docs/` has not migrated yet — it is still in the source monorepo
> (`plant-vs-zombie-rise-of-summoner/docs/`). `kvsplit` routes `docs/**` to this
> root (D1) but `apply` has not run. Both paths above are where the docs belong,
> not where they are today.

Both are **indexes**: one row per decision or topic, with the rule text in a
per-category file beside them. Read the index, then open the one file the row
names. Do not read all twelve categories.

Categories are the same twelve in both files: `combat` · `content-gen` ·
`game-host` · `launcher` · `persistence` · `power-caps` · `presentation` ·
`progression` · `repo-tooling` · `stats` · `transport` · `world`.

## The original-IP test

Every repo except `gk-fusion` must build, run, test and make sense **if Plants vs.
Zombies does not exist**. `gk-fusion` is the single permanent exception.

## Rules that hold everywhere

1. **A comment is not evidence.** Code beats docs; docs beat comments. Open the
   file and check.
2. **Read the section, not the line.** A rule scoped to one context is not a
   universal law.
3. **Test the constraint before you declare it.** "This moves goldens" is a claim.
   Run it.
4. **A tick is a claim, not evidence.** A closed task block means the document
   claims completion, not that a gate ran.
5. **Generated seed data is never hand-edited.** Fix the generator, regenerate,
   commit the diff. Editing output forks the corpus from its source and the next
   run reverts you.
6. **No watermarks.** No assistant or vendor names, no `Co-authored-by:` trailers,
   no "AI-generated" text in docs, comments or commit messages. The author is the
   owner's own identity.
7. **Never commit secrets, game binaries, or machine-local paths.** Committed
   paths stay portable: repo-relative or `${workspaceFolder}`, never a drive
   letter.

## New tooling is Python

Every new script is Python. No new PowerShell.

- PowerShell stream capture is a silent-data-loss surface: `Write-Host` writes
  the INFORMATION stream, so `2>&1` captures nothing from a script that is
  working correctly. This has cost four wrong diagnoses in this workspace already.
- `$env:` set in one agent call does not survive to the next. Each call is a new
  process.
- A `.ps1` body cannot be imported as a library or unit-tested without spawning a
  process per call. Python tools import each other and are tested with
  `python -m unittest`.
- Every Python tool: a hard `--timeout` on every external call, a **named refusal
  the moment a precondition fails** (fail closed, never "continue and report
  empty"), a machine-readable `--json`, and a non-zero exit naming the stage that
  failed. A tool that can hang, or whose empty output reads as success, is a
  defect.

Existing `.ps1` files are not rewritten wholesale. A `.ps1` touched for a fix is a
candidate to port.

## Git

Plain git. `git add <explicit paths>`, then `git commit`. Never `git add -A`:
these repos are shared, and a broad stage sweeps another stream's half-finished
files. Push and pull requests only when the owner asks.

## kvsplit

The migration tool in `tools/kvsplit/`. Reads the source repo at a **pinned SHA**
through git — never the working tree. Writes to `staging/`. Only `apply` writes
into a sub-repo, and it refuses a dirty one. Unclassifiable input becomes
**residue**, never a silent pass-through. Same inputs ⇒ byte-identical output.

**Current state:** the topology exists, the migration has not run. Only
`gk-assets` has content, and `ownership.v1.json` still names four targets, so
`apply` would send everything to `gk-core`/`gk-forge`/`gk-fusion`/`gk-data` and
the three new repos would receive nothing. Extend the rules before staging.
