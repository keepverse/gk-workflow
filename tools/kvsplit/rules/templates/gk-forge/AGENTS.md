# gk-forge

Generator code: seedsmith and the C# generator/importer/validator tools. **Public.** Output goes to
gk-data packs; this repo holds no content.

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` and
`../CLAUDE.md` (loaded automatically for any agent working inside this folder). Docs live in `../docs/`.
This file was emitted by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Generated content is never hand-edited: fix the generator, regenerate, commit the diff in gk-data.
- Compile only against gk-core (`GkCoreRoot`).

## Build and test

```powershell
dotnet build FusionRpg.slnx
cd tools/seedsmith; python -m pip install -r requirements.lock; python -m pip install -e . --no-deps; python -m pytest -q
```
