# gk-content

Authored content: the game's own names, flavour, narrative and registries. **Private, always** — it
carries the written identity, and it is outside any "make this public" gate.

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` (loaded
automatically for any agent working inside this folder). Docs live in `../docs/`. This file was emitted
by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Authored by hand only where the shape says so: `**/_registry/**`, `**/_exemplars/**`, and
  hand-authored kinds.
- **Never hand-edit generated content.** Anything carrying `_meta.model` / `promptVersion` / `batch` is
  a gk-forge output; fix the generator there, regenerate, commit the diff.
- The derived corpus is **gk-data**. This repo is ours; that one is derived from another game.
- Numbers a balance pass would change are `gk-core/data/tuning`, not here.
- A pack is not a licence to invent vocabulary: a new content kind is a reviewed change to a closed
  enumeration, with its own test, exactly like a code enum.
