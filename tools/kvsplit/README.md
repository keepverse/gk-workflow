# kvsplit

Deterministic migration of the legacy monorepo into the Keepverse workspace. Plan and decisions:
the legacy repo's `tasks/keepverse-split-plan.md` (D1-D9) and its `decisions.md` row
*Repository topology — Keepverse split*.

**The migrated repositories are this tool's output.** Same source commit, same rules, same tool
version: byte-identical staged trees. What the tool cannot decide becomes **residue**. Residue is
closed by changing `rules/**`, adding a transform, or committing a fix in the legacy repo, then
re-running. Staged or imported files are never edited by hand.

## Install and test

```powershell
cd tools/kvsplit
python -m pip install -r requirements.lock
python -m pip install -e . --no-deps
python -m pytest -q
```

Runtime is standard library only.

## Use

```powershell
# stage from a pinned legacy commit (reads git objects, never the working tree)
python -m kvsplit stage --source ..\..\..\plant-vs-zombie-rise-of-summoner --rev <sha> --out ..\..\.staging

# residue grouped by kind (the reconcile queue)
python -m kvsplit residue --staging ..\..\.staging --limit 10

# determinism proof: two runs, identical output digest and residue ids
python -m kvsplit verify --source <legacy> --rev <sha> --out ..\..\.staging-verify

# HELD (gate GM): only on the owner's explicit migration-start command
python -m kvsplit apply --staging ..\..\.staging --workspace ..\.. --confirm-migration-start
```

`apply` also refuses while residue is non-empty, when a target repo is dirty, and when the staging
was produced by different rules. It commits locally; it never pushes.

## Pipeline

| Module | Does |
|---|---|
| `source` | tracked entries + blob bytes at a pinned commit (`git ls-tree`, `git cat-file --batch`) |
| `rules` | strict parse of `rules/*.v1.json` + `rules/templates/<repo>/**`; digest of all of it |
| `classify` | path -> exactly one repo (highest priority wins; tie, no match, dead rule, collision = residue) |
| `graph` | ProjectReference direction contract, game-host references outside `unityRepos` |
| `transforms` | `msbuild-paths`, `msbuild-props-inject`, `markdown-citations` |
| `scan` | configured tokens + path literals that move and no transform owns |
| `stage` | staged workspace, `report.json`, `residue.json` |
| `check` | staged ProjectReferences resolve, no content in public repos, no host imports outside the host repo |
| `apply` | snapshot commit per repo (held behind gate GM) |

## Residue fix kinds

- `rule` — edit `rules/**` (ownership, transform config, templates).
- `transform` — a new general pattern: add a transform with a test.
- `source` — the legacy repo must change: a normal, verified commit there.
