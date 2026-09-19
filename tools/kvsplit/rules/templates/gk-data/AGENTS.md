# gk-data

All content data: `packs/<pack>/seed`, `packs/<pack>/generated`, `packs/<pack>/content`. **Private, always**
(decision D8). Packs: `fusion` (current corpus), `keepverse` (original, starts empty).

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` and
`../CLAUDE.md` (loaded automatically for any agent working inside this folder). Docs live in `../docs/`.
This file was emitted by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Entries with generator provenance (`_meta.model` / `promptVersion`) are gk-forge output: never hand-edit;
  regenerate from gk-forge.
- Never copy files from this repo into a public repo.
