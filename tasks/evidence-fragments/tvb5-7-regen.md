# TVB5.7 precondition — the last residual red: the stale `family-expand.g-evade.json`

`FamilyExpandGen --check` is red on a clean HEAD because `e1d9103e` (item-seedgen, tag-axis
exclusivity) dropped the `utility` tag from `gk-data/packs/fusion/data/seed/items/affix-families/g-evade.json:82-83` and the
committed `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json` was never regenerated. The generator
is authoritative for a tree whose entries carry `_meta` provenance, so the file is regenerated, never
hand-edited: the whole diff is the five rows that lost `"utility": "1"`.

| Criterion | Command | Result |
|---|---|---|
| The stale file, before | `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | exit 1, `1 generated file(s) stale ... family-expand.g-evade.json` |
| Regenerate (never hand-edit) | `dotnet run --project gk-forge/tools/FamilyExpandGen` | exit 0, `1 file(s) written, 0 stale file(s) removed`; `git diff --stat` = 1 file, +5/−10 |
| Path-owned verification | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json -Session tvb58` | exit 0 — `FusionRpg.Core.Tests` **14837 passed / 0 failed** (7m53s), `gen-family-expand` script check green |

Resolves `AFE-F1` (`tasks/atom-family-expansion-todo.md`) and `ISG-F3` (`tasks/item-seedgen-todo.md`),
and closes row 4 of `tvb5-7-residual-repair.md`.
