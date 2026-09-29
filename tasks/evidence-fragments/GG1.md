# GG1 — game-gui dead-code deletion (re-verification, no code change)

Fresh re-check of the 2026-08-31 finding, not inherited: **NOT executable as written.**

| Named component | Live importer, grepped 2026-09-20 |
|---|---|
| `CatalogPage` | `layers/almanac/AlmanacLayer.tsx:2,7` |
| `RecipesPage` | `layers/almanac/AlmanacLayer.tsx:3,8` |
| `MetricsPage` | `layers/chronicle/ChronicleLayer.tsx:2,8`, `dev/DeveloperTree.tsx:20,44` |
| `RpgProgressionPage` | `layers/chronicle/ChronicleLayer.tsx:3,9` |
| `PvzStatsPage` | `layers/chronicle/ChronicleLayer.tsx:4,10` |
| `ExpeditionsPage` | `layers/expeditions/ExpeditionsLayer.tsx:1` |
| `RosterPage` | gone (deleted 2026-08-31; confirmed absent) |

| Check | Command | Result |
|---|---|---|
| Typecheck + build | `npm run build` | clean, `✓ built in 9.29s` |
| Unit suite | `npm test` | 379/384 files, 3204/3209 tests |

**5 failures, all pre-existing/unrelated, none touching game-gui:** `disabledReasonGuard` (GG-55, known
since 2026-08-31, traced to commander-surface's `CommandersLayer.tsx`/`CommanderSheetFooter.tsx`) plus
**4 newly-observed** (`contractGuard`, `delveViews`, `pendingCopyGuard`, `hexGuard`) — all naming the
same `ui/actor/*.tsx` files (REST-DTO imports / hex literals / dev-jargon copy). New drift since
2026-08-31 from the commander-surface/actor-sheet work area; named here transparently, not fixed —
out of `backlog-clear`'s scope.

**Disposition:** closed at the limit the real dependency graph allows, matching the prior session's own
finding with no drift in the six live pages. What remains (retire vs. grow the layers) is a design
question for the owner, not a deletion task.
