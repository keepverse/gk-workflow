# CC6 — Items converge (plan line 151)

Verdict: **PARTIAL.** Species materials 2/8/0, the 95 combination entries and the socket-words
retirement are green. Combination binding/pricing is green at contract level; **no live item was
reachable** for an end-to-end bind. Helm-hosts-words (R11) and the combo-budget report are **not
implemented** in the merged tree.

| Criterion | Command | Executed result | Scope |
|---|---|---|---|
| Species materials 2/8/0 (R9 trophy planner) | `python -m seedsmith.adapters.items.trophyplan.run --check` | `{"totals":{"species":1784,"family":1816},"drift":0}` = 892×2 + 227×8; `trophy-registry.json` 3600 entries | offline |
| 95 combination entries | count `gk-data/packs/fusion/data/seed/items/combinations/*.json` | `strains.json` 31 + `splices.json` 64 = **95** | offline |
| socket-words retirement | `gk-data/packs/fusion/data/seed/items/socket-words/` | only `combogen-migrate.ledger.json` remains; it names `deletedFile: 'data/seed/items/socket-words/sockwords.json'`, `legacyKind: socket-word` → `targetKind: combination` | offline |
| Combinations bind + are priced (contract) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher\|~CombinationEvaluator\|~StrainSpliceGrid\|~ComboPricing"` | `Failed: 0, Passed: 63` | offline |
| combo-budget report green | `python -m seedsmith items combo-budget --report` | **refused**: `argument items_command: invalid choice: 'combo-budget' (choose from generate, validate, fill, repair-sets, repair-species, repair-names, combogen-migrate)` — verb not built | offline |
| Helm hosts words (R11: head-guard 4) | read `gk-core/data/tuning/sockets.v1.json` + `tasks/strain-splice-host-todo.md` | `socketCeiling.head-guard=3`, `structuralCeiling=4`, **no `measuredAgainst`**; SSH8.x/SSH6.8/SSH7.7 all unticked; spec requires `sockets.v2` head-guard=4 | offline |
| Live bind + live pricing | `GET /api/items/surfaces/1`, `/api/items/armoury/1` | all six surfaces `Locked` (`first-container-acquired`), armoury `total: 0`; no real item-acquisition path from this save, and a debug-granted item would fabricate the subject (live-probe standard §4) | not reached |

Live-relevant note: `debug.screenshot` + event log confirm `item.drop` events on the lawn, but these
are engine pickups and create **no** server item row (`armoury total` stays 0) — they do not unlock
the item surfaces.

Falsified by: a trophy check with non-zero drift, a cross-kind count ≠95, a surviving
`sockwords.json`, or a live item bind that matched a combination.
