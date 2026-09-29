# species-gear-chain — the todo's own citations re-anchored (2 D1 → 0)

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result |
|---|---|---|
| the defect, measured | `python scripts/audit-doc-citations.py --scope tasks/species-gear-chain-todo.md --summary` | before: **2 D1** (`file does not exist`, 0 HIGH), 428 resolvable citations |
| T1's `Files:` line named a file that never existed | `git log --all --pretty=format: --name-only \| sort -u \| grep -i rarityladder` | no path ever named `tests/FusionRpg.Core.Tests/Creatures/CreatureRarityLadderTests.cs` on any branch — a planned name. The file that shipped is `gk-core/tests/FusionRpg.Core.Tests/Creatures/LadderDeclarationTests.cs`, which is also what T1's own verify filter (`~LadderDeclaration`) selects |
| slice 3k's citations were bare basenames | read | `classes.v3.json` resolves only as `gk-data/packs/fusion/data/seed/items/_registry/classes.v3.json`, and the spec's `UpgradePolicy.cs` placeholder shipped as `gk-core/src/FusionRpg.Core/Items/Mutation/ItemUpgradePolicy.cs`; both now carry the resolvable path beside the original name, and the line carries `unbuilt`/`renamed to` so the audit's deliberate-dead exemption applies (the regex is evaluated on the citation's OWN line) |
| the repair | `python scripts/audit-doc-citations.py --scope tasks/species-gear-chain-todo.md --summary` | after: **D1 0, D2 0, D3 0, D4 0** over **432** resolvable citations; `--strict` exits 0 |
| the repo-wide gate is unchanged | `python scripts/audit-doc-citations.py --summary` (default scope `docs/`) | 687 D1 / 7 D2 / 56 D3, all 0 HIGH — the standing repo state, untouched by this change (no `docs/**` file was edited) |

## This lane's OWN artifacts audited, and six dead citations in them fixed (2026-09-23, lane sgc-6)

DESIGN-GATE §5's checklist box is "`python scripts/audit-doc-citations.py --scope <the doc I touched>`
reports no HIGH finding for it". Run over all twelve artifacts this lane wrote, it did NOT hold — the
later commits had introduced six:

| Artifact | Finding | Citation | Fix |
|---|---|---|---|
| `todo.md:3371`, `t55-redset.md:96`, `summary.md:42` | D3 ambiguous basename ×3 | `Program.cs:765` | → `gk-core/src/FusionRpg.Server/Program.cs:765` (three `Program.cs` files exist) |
| `summary.md:44` | D1 file does not exist ×2 | `KindCount.cs:43`, `TriggerCount.cs:48` | → `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs` with `:43` and `:48` — the "file names" were shorthand for a field, and the audit reads them as files |
| `f1.md:30` | D1 | `round-1-model-experiment.json` | → named as `_EXCLUDED_SUFFIX`'s value, a gitignored runtime file, not a tracked one |
| `f3.md:9` | D3 | `DumpWriter.cs:143`, `preflight.py:79` | → both full paths |
| `tool-refusal.md:8` | D1 | `subprocess.py:1538` | → removed; it was CPython's own stdlib traceback frame, never a repo citation |

Re-run over all twelve: **D1 0, D2 0, D3 0, D4 0 — 0 HIGH in every one.** Recorded because the box was
unticked-by-omission: the first pass audited only the todo, not the fragments it went on to write, and the
fragments are where five of the six sat.
