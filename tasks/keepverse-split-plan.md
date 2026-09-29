# Plan: keepverse-split — move this monorepo into the Keepverse multi-repo workspace

> **Superseded in part (2026-09-27).** The authoritative version is
> `Keepverse/docs/keepverse-migration-plan.md`, versioned with the tool that performs the split.
> This file is kept as the original design record. Where the two disagree, the extension wins —
> and it disagrees on **topology**: this file lists six repositories and says "Web stays in
> gk-core", but the workspace now has nine and `web/**` routes to `gk-web`. Following this file
> would undo the split. Read the extension first.

**Status: superseded 2026-09-28. Gate G1 is MET** — `docs/architecture/decisions/world.md:27`
reads *"Locked (owner-approved plan, gate G1)"* (it was `decisions.md:144` before the lock
file was split into per-category files). This line previously read "Not started", which the
24-done / 17-open block counts refuted three ways; the blocker map in
`tasks/keepverse-split-todo.md` flagged the header as the defect on 2026-09-27.

> **The authoritative plan is `Keepverse/docs/keepverse-migration-plan.md`**, versioned with
> the tool that performs the split. It is self-contained and replaces this file. This file is
> kept as the original design record. Where the two disagree, the authoritative version wins —
> and it disagrees on **topology**: this file lists six repositories and says "Web stays in
> gk-core", while the workspace has nine and `web/**` routes to `gk-web`. Following this file
> would undo the split.
>
> **Its first phase is Phase A, and Phase A is the owner's precondition: the source repository
> must hold exactly one `main` branch, with every other branch, remote branch and linked
> worktree deleted, before any migration work begins.** `KS4.1` below is one line and does not
> cover it; Phase A does.
Task list: [keepverse-split-todo.md](keepverse-split-todo.md).

## Why

The repo name and product identity are tied to Plants vs. Zombies Fusion, and the name
"Rise of Summoner" is already used by a published mobile game. The owner is turning the RPG layer
into an original IP (**Keepverse**) and keeping the PvZ Fusion integration as a separate mod.
The target workspace already exists at `D:\Works\source\Keepverse` (see "Target layout").

The original-IP test for every repo except `gk-fusion`: **it builds, runs, tests and makes sense if
Plants vs. Zombies does not exist.**

## How the migration is executed — a deterministic tool, agents reconcile its residue

Owner ruling (2026-09-19): *"we will build a deterministic tool to migrate and use agents to reconcile
something that the deterministic tool cannot cover. We don't do manual, ad hoc work. The tool will be
built in Python."*

This is the same discipline as the generated-seed rule: **the migrated repos are the tool's OUTPUT.**

| | Allowed | Not allowed |
|---|---|---|
| Moving, rewriting, templating files | The tool, from its versioned rules | Hand-copying, hand-editing a staged or imported file |
| A case the tool cannot handle | The tool reports it as a **residue item**; an agent resolves it by (a) adding/changing a tool rule, or (b) a normal source commit in the old repo; then the tool re-runs | Patching the output to make the residue disappear |
| Proof | Tool re-run from the same inputs is byte-identical; residue list is empty; verification passes | "Looks right", a one-off script in `%TEMP%` |

Consequences:

- **Inputs are pinned:** old-repo SHA + rules files + tool version. Same inputs ⇒ byte-identical staged
  trees and report (hash recorded). Reads blobs at the SHA through git, never the working tree.
- **Output is staged, then applied.** The tool writes to a staging directory; only the `apply` verb
  commits a staged tree into a sub-repo, and it refuses a dirty sub-repo.
- **Idempotent and re-runnable any time.** Dry runs start now, while Phase 3 decoupling proceeds, so
  the residue list is the migration's live to-do list.
- **An agent never edits output.** A residue item is closed only when a re-run no longer emits it and
  emits nothing new.

## Scope

In scope: the tool, repository topology, file ownership, build/test/CI rewiring, workspace tooling,
agent config, docs placement, history policy, cutover.

**Out of scope — owned by other programs:**

- **Detecting** PvZ / third-party marks: `ip-censor` (map `docs/architecture/ip-censor-map.md`,
  seven module specs). Spec phase, unbuilt.
- **Applying** renames (`pvz.*` namespace, `CasterSide/BoardSide/StatSide.Plant|Zombie`, character
  names, species names): the ip-censor **execute** program (`ip-censor-map.md:13-22`). Not yet planned.
- The new faction/organism vocabulary and the product name. Owner-led naming work.
- Renaming `FusionRpg.*` namespaces/binaries (itself an ip-censor execute target). This program moves
  files and rewrites paths; it never renames a type.

## Owner decisions recorded (2026-09-19, this conversation)

| # | Decision |
|---|---|
| D1 | Workflow and docs go to the Keepverse root repo (`gk-workflow`). |
| D2 | Source code goes to sub-repos. The game injector goes to `gk-fusion`. Assets go to `gk-assets`. |
| D3 | Generator **code** goes to `gk-forge` (seedsmith, the `tools/*Gen` family). |
| D4 | Original-IP repos start from a **fresh snapshot**, not imported history. The old repo is archived. |
| D5 | The migration is done by a **deterministic Python tool**; agents only reconcile its residue, through tool rules or source commits. No manual, ad hoc work. |
| D6 | **All content data goes to `gk-data`**: `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**`, including hand-authored registries/exemplars and seedsmith ledgers — anything carrying names or flavor text. Purpose: the public core repo can never leak IP by an accidental commit. `gk-core/data/tuning/**` (numbers, Server-loaded) stays in gk-core. |
| D7 | The current (derived) corpus moves into gk-data as the **`fusion` pack**; the original pack is **`keepverse`** and starts empty. Pack and path names never use the word "pvz". |
| D8 | **gk-data is private, always.** It is outside gate G2. |
| D9 | **kvsplit is built in the Keepverse root** (`gk-workflow`, `tools/kvsplit/`), not in the old repo. |

## The tool: `kvsplit`

**Shape: an independent Python tool mirroring `gk-forge/tools/seedsmith`**, exactly as ip-censor's `wiring`
spec does (`docs/architecture/ip-censor/spec-wiring.md:38-49`): package `kvsplit/`, `pyproject.toml`
with exact pins, committed `requirements.lock`, `tests/` with pytest, CLI `python -m kvsplit <verb>`.
Standard library first (`xml.etree`, `json`, `pathlib`, `subprocess` for git). No LLM anywhere in the
tool — nondeterminism belongs to the agent reconcile step, never to the tool.

Location (D9): `D:\Works\source\Keepverse\tools\kvsplit\`, committed to `gk-workflow`. It reads the
old repo by path at a pinned SHA and never writes to it, so it cannot collide with lanes running there,
and the tool itself never needs migrating. Its verification is its own pytest suite plus a root CI
workflow (`.github/workflows/kvsplit.yml`); the old repo's `verify-change.ps1` registry is not involved.
Rules files live beside it in `tools/kvsplit/rules/`.

### Modules

| Module | Responsibility | Depends on |
|---|---|---|
| `source` | Tracked-file list and blob bytes at a pinned SHA (`git ls-tree -r`, `git cat-file --batch`). Pure I/O. | — |
| `rules` | Parses the authored rule files: ownership manifest, transform config, templates. A missing or mistyped field **throws, never defaults**. | — |
| `classify` | path → exactly one target (`root`, `gk-core`, `gk-forge`, `gk-data`, `gk-assets`, `gk-fusion`, `drop`); for gk-data also the pack (`fusion` / `keepverse`). Unmatched, double-matched, or dead rule ⇒ residue. | `source`, `rules` |
| `graph` | Parses every `.csproj`/`.slnx`/`Directory.Build.props`/`package.json`/`pyproject.toml` into a dependency graph with each node's target repo. Cross-repo edge that violates the direction contract ⇒ residue. | `source`, `classify` |
| `transform` | Registered, pure transforms, each `bytes -> bytes` or residue: MSBuild path rewrite (XML-aware: `ProjectReference`, `Content Include`/`Link`, `..\..\data\seed` → `$(GkDataRoot)\packs\<pack>\seed`), per-repo solution generation, doc citation prefixing (`src/...` → `gk-core/src/...`), per-repo `AGENTS.md`/`.gitignore`/props templating, CI workflow split. A file a transform cannot parse is residue, never passed through half-rewritten. | `classify`, `graph`, `rules` |
| `scan` | Text references that cross a repo boundary and no transform owns: hard-coded paths in `.cs`/`.ps1`/`.py`/`.ts`, tests reading `docs/`, repo-root discovery via `FusionRpg.slnx`. Each hit ⇒ residue with file:line. | `source`, `classify` |
| `stage` | Writes each target tree to `staging/<repo>/`, plus `report.json` (every file: source path, blob id, target, transforms applied, output hash) and `residue.json`. Deterministic ordering; LF/CRLF preserved from the blob. | all above |
| `check` | Static verification of staged trees: every reference resolves inside the workspace layout, the direction contract holds, only gk-fusion references Unity/Il2Cpp/Harmony, `Σ files per target + dropped == tracked files` (reconciliation, printed not pinned), re-run hash equality. | `stage` |
| `apply` | Commits `staging/<repo>` into the sub-repo as one snapshot commit (message: source SHA, tool version, rules hash). Refuses a dirty or diverged sub-repo. The only verb that writes outside `staging/`. | `check` |

### Residue contract (what agents consume)

`residue.json` items: `{id, kind, path, line?, detail, allowedFix}` where `id` is stable across runs
(hash of kind + path + anchor) and `allowedFix` is one of:

- `rule` — add or change an ownership rule / transform config / template. Agent edits `Keepverse/tools/kvsplit/rules/**`.
- `transform` — the case is a new, general pattern. Agent adds a transform with a pytest.
- `source` — the old repo's code must change (for example a test that reads `docs/` needs a fixture).
  Agent makes a normal, verified commit in the old repo.

An agent brief is one residue kind at a time. Done = re-run shows the item gone and no new id.
Agent runs follow the owner-charter rule (runtimes, models, budget) before any worker starts.

## Target layout

Verified on disk 2026-09-19: `D:\Works\source\Keepverse` is repo `keepverse/gk-workflow` (AGPL-3.0),
with nested independent repos `gk-core` (AGPL-3.0), `gk-forge`, `gk-data` (MIT file, private),
`gk-assets` (MIT), `gk-fusion` (AGPL-3.0), each with its own `origin` under `github.com/keepverse/`,
**untracked** in the root, not submodules. `Keepverse.code-workspace` lists only core/assets/fusion;
kvsplit's template emits the full list.

```
Keepverse/                     gk-workflow   workflow, docs, agent config, tasks, kvsplit, cross-repo scripts
├── gk-core/                   gk-core       Contracts, Core, Data, CheatCore, Server, web, gk-core/data/tuning,
│                                            balance/probe tools, their tests, core guards, test fixtures
├── gk-forge/                  gk-forge      seedsmith, generator tools (code only)
├── gk-data/    (PRIVATE)      gk-data       packs/fusion/data/{seed,generated}/**, packs/fusion/content/**
│                                            (current derived corpus, almanac dump, zomboss, registries,
│                                            ledgers); packs/keepverse/** (original, starts empty)
├── gk-assets/                 gk-assets     original art, icons, display content
└── gk-fusion/                 gk-fusion     Injector + 3 hosts, Launcher, game-profiles, live-probe and
                                             debug tools, release (code only)
```

Web stays in gk-core: the Server serves it from `wwwroot`, both ship in one release, and both bind to
`FusionRpg.Contracts` DTOs.

## Dependency direction (the contract `graph` and `check` enforce)

Measured 2026-09-19 from `ProjectReference`s: Contracts ← Core ← Data ← Server; CheatCore ← Contracts;
the three injector hosts → Contracts, Core, CheatCore; Launcher → nothing. No Unity dependency exists
below the injector.

- gk-forge → gk-core (code); reads and writes gk-data packs.
- gk-fusion → gk-core (code), gk-data `fusion` pack (runtime/release), gk-assets (files).
- gk-core → gk-data **runtime only**, through `GkDataRoot` + a configured pack name, never compiled.
- gk-core never references gk-fusion. **gk-core's own tests never need gk-data**: gk-core is public
  and gk-data is private, so public CI cannot read it. A core test that needs real content either uses
  a fixture in gk-core or moves to a `ContentIntegration` test category that runs only where gk-data is
  checked out (local, private CI job). Each such test is `scan` residue classified per test.

**Tool placement rule: a tool lives where its output's owner lives** — generator code → gk-forge
(its output → gk-data), code emitting `src/**` → gk-core, live-game tools → gk-fusion. Encoded as
ownership rules, each with a reason field.

## Cross-repo mechanics

- **Workspace manifest + lock, not submodules.** `workspace.json` lists repos and remotes;
  `workspace.lock.json` records SHAs last proven green together; `scripts/bootstrap.ps1` clones.
  Submodules would force a root commit for every sub-repo commit; the lock moves at checkpoints.
- **Sibling paths, not packages.** One MSBuild property per repo (`GkCoreRoot`, `GkForgeRoot`,
  `GkDataRoot`, `GkAssetsRoot`, `GkWorkflowRoot`), default = sibling folder. CI checks out siblings
  at lock SHAs; checking out private gk-data needs a token and exists only in private CI jobs.
- **Content packs (D7).** Every generator and every runtime data reader takes a pack (`fusion` or
  `keepverse`) instead of a hard-coded `gk-data/packs/fusion/data/seed` path. Server config selects the pack; the release in
  gk-fusion ships the `fusion` pack. Routing generators and readers through the pack path is expected to
  be the biggest `source` residue kind.
- **Agent config inherits by directory.** Root `CLAUDE.md` loads for any agent working inside a
  sub-repo; each sub-repo carries a thin, tool-templated `AGENTS.md`. One CodeGraph index at the root.

## Resolver contract (Phase 3, added 2026-09-19)

**A pack mirrors the legacy repo root.** `packs/<pack>/` contains `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**` and
`content/**` at the same relative paths the legacy repo had. A repo-relative content literal such as
`data/seed/items/x.json` therefore stays byte-identical; only the root it is resolved from changes. The same
holds for `gk-core/data/tuning/**`, which stays at the same path inside gk-core.

Every language gets exactly one resolver per root, and kvsplit recognises it (`scan.v1.json` `resolvers`):

| Root | Env override | Legacy default | Split default | Python | C# | PowerShell |
|---|---|---|---|---|---|---|
| content (gk-data pack) | `KEEPVERSE_CONTENT_ROOT` | legacy repo root | `<workspace>/gk-data/packs/<KEEPVERSE_PACK or fusion>` | `content_root()` | `ContentRoot.Path` | `Get-ContentRoot` |
| core (tuning, engine) | `KEEPVERSE_CORE_ROOT` | legacy repo root | `<workspace>/gk-core` | `core_root()` | `CoreRoot.Path` | `Get-CoreRoot` |
| workspace (docs, tasks) | `KEEPVERSE_WORKSPACE_ROOT` | legacy repo root | directory holding `gk-core/` and `gk-data/` | `workspace_root()` | `WorkspaceRoot.Path` | `Get-WorkspaceRoot` |

Discovery is deterministic: the env override wins; otherwise walk up from the caller to the first directory
that is either the legacy repo (contains `FusionRpg.slnx` and `gk-data/packs/fusion/data/seed/`) or the workspace (contains
`gk-core/`). A missing root **throws**; it never falls back silently. Runtime code under
`src/FusionRpg.{Core,Data,Server}` is exempt: it resolves content against its build output, whose layout the
`<Content Link="data\...">` items preserve (`outputRelativeGlobs`).

## Docs placement (D1)

Root holds workflow and docs; PvZ-host docs (`gk-fusion/docs/injector/**`, lawn/live-probe runbooks, game
profiles) go to `gk-fusion/docs/`. Citation prefixing is a `transform`. The 17 test files that read
`docs/` (measured) are `scan` residue with `allowedFix: source`. "Doc and code in the same change"
becomes "same task, one commit per repo, linked by task id".

## Phases

**Phase 0 — decide.** ADR in `decisions.md` (topology, D1-D9, direction contract, placement rule).

**Phase 1 — build kvsplit** (`source` → `rules` → `classify` → `graph` → `transform` → `scan` →
`stage` → `check` → `apply`, plus wiring). Each module with pytest over fixture repos built in memory /
in pytest's tmp dir (testing-standard: failed cleanup is a failure).

**Phase 2 — author rules and run dry.** Ownership manifest, transform config, templates. Run `stage`
against HEAD repeatedly; residue becomes the work queue.

**Phase 3 — reconcile.** Agents close residue by kind, one brief per kind. Source-kind fixes land in
the old repo as normal verified commits (these are the "decouple in place" changes: pack-path
routing where a transform cannot reach, test fixtures / `ContentIntegration` category, repo-root
discovery). Runs beside normal
development — kvsplit reads a SHA, not the working tree.
**Checkpoint A:** `stage` + `check` at a candidate SHA: residue empty, re-run byte-identical, each
staged repo builds and tests green **in the staging layout** with absent siblings where the contract
says it must not need them.

**Phase 4 — freeze and apply.** `features/mega-merge` merged to `main`, lanes closed, import SHA
recorded. `apply` into gk-data, gk-fusion, gk-forge, gk-assets, gk-core, root. First `workspace.lock.json`.

**Phase 5 — prove.** Per-repo CI green with sibling checkout. **Checkpoint B:** full suite green per
repo; every generator `--check` byte-identical to the import SHA; goldens unchanged; live lawn entered
from the Keepverse layout and a real `/api/aptitudes/unique/allocate` allocation read back through the
normal path.

**Phase 6 — cutover.** Tool-templated path updates for CLAUDE/AGENTS/PRINCIPLES, runner repo root,
CodeGraph re-index at the root. Old repo archived (G3). Per original-IP repo, when the ip-censor guard
is clean: public `main` is an orphan snapshot of the clean tree (G2).

## Gates (only irreversible actions)

| Gate | Action | Resolver | Default if unanswered |
|---|---|---|---|
| G1 | Approve this plan + ADR | owner | Phase 0 does not start |
| GM | **Start migration** — owner's explicit command | owner | Work stops after Phase 3 (tool + rules + dry runs ready). No `apply`, no freeze, nothing written into Keepverse repos |
| G2 | Make a repo public (never gk-data, D8) | owner, per repo | stays private |
| G3 | Archive the old repo | owner | old repo frozen by convention, stays writable |

Push is owner-only (AGENTS.md). `apply` commits locally only.

## Risks with a named handling

| Risk | Handling |
|---|---|
| A transform silently mangles a file | Transforms are pure and unit-tested; unparseable ⇒ residue, never pass-through; `report.json` hashes every output |
| In-flight lanes diverge from the import SHA | kvsplit reads a pinned SHA; Phase 4 freeze; re-run at the final SHA is cheap |
| A core test depends on gk-data/gk-fusion through a path nothing caught | Checkpoint A builds and tests gk-core staging with every sibling absent (public-CI condition); failures become residue |
| Content text lands in a public repo | Every `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**` path routes to private gk-data (D6); `check` fails if any staged public repo contains a seed/generated-shaped file (`_meta.model`/`promptVersion` provenance, species/name corpora); G2 also needs the ip-censor guard |
| Agent "reconciles" by editing output | `stage` regenerates from scratch each run; an output edit is overwritten and visible as a hash change in `report.json` |

## Notes for the owner (not gates)

- **`gk-assets` is MIT.** MIT on art lets anyone reuse Keepverse art commercially; IP art usually uses a
  CC or proprietary license. The plan does not depend on it.
- **The creature corpus is PvZ Fusion's roster** (`gk-data/packs/fusion/data/seed/creatures/creature/plant/rare.json` →
  `卷心菜投手`; anchors derive from the almanac dump), hence it becomes the `fusion` pack in private gk-data.
- `data/icons/dump/**` (ripped game art) is untracked (0 tracked files). kvsplit reads only the git
  tree at the SHA, so untracked files can never be staged.
