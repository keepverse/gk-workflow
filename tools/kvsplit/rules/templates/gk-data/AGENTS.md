# gk-data

The derived content corpus: `packs/fusion/data/seed`, `packs/fusion/data/generated`. **Private,
always** (decision D8).

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` (loaded
automatically for any agent working inside this folder). Docs live in `../docs/`. This file was emitted
by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Entries with generator provenance (`_meta.model` / `promptVersion` / `batch`) are gk-forge output:
  never hand-edit them; regenerate from gk-forge.
- **This repository is the derived corpus only.** Authored content — the game's own names, flavour and
  registries — is **gk-content**. A pack mirrors the legacy repository root, so a repo-relative
  content path inside `packs/fusion/` stays byte-identical to what it was.
- Pack and path names never use the word "pvz".
- Never copy files from this repo into a public repo.
- A missing content root **throws**; it never falls back silently.
