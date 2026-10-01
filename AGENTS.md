# gk-workflow — agent guide

The workspace root. It holds the **rules, the specs and the migration tool**, and
no game code. If you are here to change gameplay, this is the wrong repo.

## The workspace

**This repository is one of the nine** — it is the root, not a container for the
other eight. `docs/`, `.claude/`, `tasks/`, `tools/kvsplit/` and the migration
ledger are its; the eight below are untracked here and each has its own remote.

| Repo | Holds | Licence |
|---|---|---|
| `gk-core` | Contracts, Core, Data, Server, balance numbers | AGPL-3.0 |
| `gk-forge` | seedsmith + the generator family | AGPL-3.0 |
| `gk-web` | Browser control room | AGPL-3.0 |
| `gk-fusion` | Injector, hosts, launcher, live-probe | AGPL-3.0 |
| `gk-tests` | The cross-repository suites only | AGPL-3.0 |
| `gk-content` | Original names, flavour, registries | AGPL-3.0, private |
| `gk-data` | Content packs / derived corpus | MIT, **private** |
| `gk-assets` | Art pipeline | MIT |

`gk-tests` is deliberately nearly empty — four files, no suites. Shared gate
definitions, the guard suite, the verification harness, orchestration tooling,
path rules and CI policy are **this repository's**, because a second copy in a
sub-repository is the competing copy the ownership principle exists to prevent.
Its own `AGENTS.md`/`README.md` still describe it as holding "the gate
definitions": that text is emitted from a kvsplit template, it is wrong, and the
template is the defect to fix rather than the emitted file. Do not read it as the
current role.

## Read before you propose anything

- **docs/DESIGN-GATE.md** — binding. Find your subsystem in its §1 topic index
  and read the documents that row names, **in this session**.
- **docs/architecture/decisions.md** — locked choices. Change here before changing
  code.

> `docs/` is here and is **this repository's** — `kvsplit` routes `docs/**` to this
> root (D1) and the import brought it across. The exceptions are measured per
> FILE, never per directory: `docs/launcher/` is **gk-fusion's** (this root's
> `docs/` is development documentation; gk-fusion's holds the launcher contract),
> and `gk-core` has its own small `docs/research/class-system/real-runs`. Resolve
> every documentation path against the file.

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

## Verification

One entry point, and it lives in `gk-core` because gk-core owns the harness:

```powershell
python gk-core\scripts\verify-change.py --paths <repo-relative files> --session <id>
```

Run it from this root or from `gk-core`; both work, and `--paths` values are
repository-relative either way. A path this root owns (`docs/PRINCIPLES.md`) and a
path `gk-core` owns both resolve, and the plan names the repository that carries
a foreign one. `--plan-only` prints the plan without running anything;
`--format json` is the machine-readable form.

The boundary registry is `gk-core/scripts/verification-boundaries.v1.json`; the
enforcement registry and the guard catalog are
`gk-core/scripts/enforcement-registry.v1.json`. Neither is copied into a
sub-repository. Every real source file is either bounded by an owner row or
covered by a reasoned exemption — an unmapped path is a refusal, not a silent
pass — and the closure that keeps it that way is asserted by
`FusionRpg.Guard.Tests.No_real_source_file_is_silently_unhandled_by_the_registry`.

## Git

Plain git. `git add <explicit paths>`, then `git commit`. Never `git add -A`:
these repos are shared, and a broad stage sweeps another stream's half-finished
files. Push and pull requests only when the owner asks.

## kvsplit

The migration tool in `tools/kvsplit/`. Reads the source repo at a **pinned SHA**
through git — never the working tree. Writes to `staging/`. Only `apply` writes
into a sub-repo, and it refuses a dirty one. Unclassifiable input becomes
**residue**, never a silent pass-through. Same inputs ⇒ byte-identical output.

**Current state: the migration is APPLIED.** All eight sub-repositories carry
their placement and are pushed; this root carries `docs/`, `.claude/`, `tasks/`,
`tools/kvsplit/` and the ledger. Do not re-run `apply` against a repository that
already holds its placement — it deletes what it does not place, and a repository
receiving zero primary placements still has its unpreserved tracked files removed.
Re-verify with `stage`, the output digest and `lossy-check` instead.

For the measured per-repository state — tracked counts, HEADs, build and test
results, the residue ledger — read
[`docs/migration-state-measured.md`](docs/migration-state-measured.md) rather than
a figure quoted anywhere else, including here. A number restated in a guide is a
number that rots.
