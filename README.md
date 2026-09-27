# gk-workflow

The workspace root: the rules, the specs, the migration tool, and the multi-agent
machinery. It holds no game code.

- **Working rules:** [AGENTS.md](AGENTS.md)
- **Locked decisions:** `docs/architecture/decisions.md`
- **Design gate:** `docs/DESIGN-GATE.md` — read before proposing anything

> `docs/` has not migrated yet. It is still in the source monorepo
> (`plant-vs-zombie-rise-of-summoner/docs/`); `kvsplit` routes `docs/**` here
> (D1) but `apply` has not run. The paths above are where the docs belong, not
> where they are today.

## The sub-repos

| Repo | Holds | Licence |
|---|---|---|
| [`gk-core`](https://github.com/keepverse/gk-core) | Contracts, Core, Data, Server, balance numbers | AGPL-3.0 |
| [`gk-forge`](https://github.com/keepverse/gk-forge) | seedsmith + the generator family | AGPL-3.0 |
| [`gk-web`](https://github.com/keepverse/gk-web) | Browser control room | AGPL-3.0 |
| [`gk-fusion`](https://github.com/keepverse/gk-fusion) | Injector, hosts, launcher, live-probe | AGPL-3.0 |
| [`gk-tests`](https://github.com/keepverse/gk-tests) | Test platform and gate definitions | AGPL-3.0 |
| [`gk-content`](https://github.com/keepverse/gk-content) | Original names, flavour, registries | AGPL-3.0, private |
| [`gk-data`](https://github.com/keepverse/gk-data) | Content packs / derived corpus | MIT, **private** |
| [`gk-assets`](https://github.com/keepverse/gk-assets) | Art pipeline | MIT |

The sub-repos are **independent repositories**, not submodules: they are untracked
here and each has its own remote. Nothing in this repo compiles.

## The original-IP test

Every repo except `gk-fusion` must build, run, test and make sense **if Plants vs.
Zombies does not exist**. `gk-fusion` is the single, permanent exception.

## kvsplit — the migration tool

`tools/kvsplit/` is a deterministic Python tool that splits the old monorepo into
the repos above.

- Reads the source repo at a **pinned SHA** through git. Never the working tree, so
  it cannot collide with work in flight.
- Writes to `staging/<repo>/`. Only `apply` writes into a sub-repo, and it refuses
  a dirty one.
- **Unclassifiable input is residue, never a silent pass-through.** Residue is the
  work queue: an agent closes an item by adding a rule or a transform, never by
  editing output.
- Re-running from the same inputs is byte-identical. That is the proof.

```bash
python -m kvsplit stage --source <path> --sha <sha> --rules tools/kvsplit/rules
python -m kvsplit check
python -m kvsplit residue          # the agent work queue
```

## Current state

The topology exists; the migration has not run. Only `gk-assets` has content.
`ownership.v1.json` still names four targets, so `apply` would route everything to
`gk-core`, `gk-forge`, `gk-fusion` and `gk-data` — **`gk-web`, `gk-tests` and
`gk-content` would receive nothing.** Extend the rules before staging.

## Docs

`docs/architecture/decisions.md` and `docs/DESIGN-GATE.md` are **indexes**: one row
per decision or topic, with the rule text in a per-category file. Read the index,
then open the one file the row names.
