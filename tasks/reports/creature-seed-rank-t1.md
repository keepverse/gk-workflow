# Task 1 — rank tuning table + loader validation

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 1. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §2, §6.
New: `gk-core/data/tuning/creature-rank.v1.json`, `gk-core/src/FusionRpg.Core/Creatures/CreatureRankTuning.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureRankTuningTests.cs`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 10 ids + 100 cells, diagonal-default | `python -c "import json;d=json.load(open('gk-core/data/tuning/creature-rank.v1.json'));g=d['grid'];print('ranks',len(d['ranks']),'cells',len(g),'floors',len(d['floors']));print('diagonal_default',all(c['rank']==c['rarity'] for c in g));print('distinct_pairs',len({(c['threatBand'],c['rarity']) for c in g}))"` | `ranks 10 cells 100 floors 5` / `diagonal_default True` / `distinct_pairs 100` | `gk-core/data/tuning/creature-rank.v1.json` |
| Loader rejects an unknown id, naming table + cell | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~CreatureRankTuning"` | **Passed! — Failed 0, Passed 15, Skipped 0, Total 15, 107 ms**; the rejection message carries `grid[1] (threatBand 'pest', rarity 'almanac')` and `'ranks'` | `gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureRankTuningTests.cs` |
| Unresolved inputs never reach the table | same filter (same run) | planted `unresolved` cell rejects; `RankIdFor` refuses `unresolved` on either axis; `unresolved` is refused before the vocabulary checks so the message names the real cause | same |
| Path-owned verification | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Creatures/CreatureRankTuning.cs','gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureRankTuningTests.cs') -Session creature-seed-rank"` | exit 0 — 55 `Passed!` / 0 `Failed!`; `FusionRpg.Core.Tests` alone 10085 passed | — |
| Tuning immutability | `python gk-core/scripts/guard-tuning-immutability.py` | `OK — 1 gk-core/data/tuning/*.json change(s) checked, T1-T4 clean` (a new v1 is an ADD, not an in-place edit) | — |
| Population pin | `pwsh -NoProfile -File scripts/guard-population-pin.ps1` | `total 0 finding(s)` — no cell count is pinned; the grid's size is `threatBands × rarities` | — |
| Vocabulary mirror | `pwsh -NoProfile -File scripts/guard-vocabulary-mirror.ps1` | `OK — 9 pair(s) checked, no drift` | — |
| Magic numbers | `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` | `M1=0 M2=0 M3=0 M4=0`, `total 0 finding(s)` | — |
| Boundary | `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/cmdc-cs-rank --session creature-seed-rank` | `clean for 'creature-seed-rank'` | `tasks/sessions/creature-seed-rank.json` |

## NOT proved / findings

- **CS-R1 (filed, `tasks/creature-seed-todo.md`).** `gk-core/data/tuning/creature-rank.v1.json` has **no**
  verification-boundary owner mapping: the same verify-change call *including* that path aborts
  `VERIFICATION BOUNDARY MISSING: gk-core/data/tuning/creature-rank.v1.json`. The registry is per-domain
  (`tuning-creature-threat` at `gk-core/scripts/verification-boundaries.v1.json#tuning-creature-threat` is the sibling row),
  not a `gk-core/data/tuning/**` glob; `scripts/**` is outside this lane's fence, hence the row.
- `gk-core/src/FusionRpg.Core/Creatures/CreatureRankTuning.cs` resolves to `core-fallback (module)`, which plans the
  **whole** split Core group (55 projects, 10085 tests) — the registry's own known Core-fallback reading
  (`tasks/test-verification-boundary-todo.md`), not a property of this change.
- The brief's session-boundary command passes `-RepoRoot` = the **main** checkout, where this lane's record
  does not exist until the orchestrator merges the branch; that run reports `no session record for
  'creature-seed-rank'`. The run against the record's own worktree is clean. **Not proved:** the
  main-checkout run.
- The five gate floors are parsed and validated but read by no gate yet (Tasks 8-12): zero behavior change
  by construction. Task 1's acceptance claims no reader.
- `publish.py` cannot create a domain (`gk-core/tools/tuning/publish.py:780-784` refuses when no version exists), so
  v1 is authored directly; every later revision goes through `publish.py`.
