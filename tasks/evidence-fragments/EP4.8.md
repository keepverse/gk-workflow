# EP4.8 — FE: every unfiltered progression reader filters by kind

Commit `@EP4.8` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-empire-level.md` (test 10)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A grep for unfiltered progression consumers finds each one filtering by kind | `rg -n "rpg/progression|RpgProgressionList|progressionList" gk-web/web/fusion-rpg-web/src` | the page's two list readers already pass `kind` ("plant"/"zombie"); the **ledger** readers did not — two tables (`RpgProgressionPage.tsx:262` compact, `:614` advanced) rendered `ledger.data.items` unfiltered with an "all kinds" filter, so an `empire` row would have appeared there | `gk-web/web/fusion-rpg-web/src/features/rpg-progression/RpgProgressionPage.tsx` |
| A vitest over the fold shows an `empire` row never appears where only actor kinds are expected | `cd webusion-rpg-web; npm test -- --run progression` | `Test Files 2 passed (2)`, `Tests 10 passed (10)` — 4 of them `actorProgressionFold.test.ts`: an empire row is dropped, the fold is generic over `kind` (species/specimen dropped too), the closed actor set is pinned as `["player","plant","zombie"]`, and a mixed ledger page keeps only its actor rows | `gk-web/web/fusion-rpg-web/src/features/rpg-progression/actorProgressionFold.ts` (new), `…/actorProgressionFold.test.ts` (new) |
| The fold is wired into every unfiltered reader on the page | `cd webusion-rpg-web; npm run build` | `tsc --noEmit` clean and `built in 12.77s` | `RpgProgressionPage.tsx` — both ledger tables' rows, both empty-state predicates and both pager counts now fold |
| The FE toolchain can be driven in this worktree | `npm ci` | this row's own first attempt failed (`esbuild` postinstall: `"node" is not recognized`) because bash's POSIX PATH reaches `cmd.exe`; running npm from PowerShell with a Windows node dir prepended installs cleanly: `added 433 packages in 18s` | — |

**What the fold is, and why it is a module rather than an inline filter.** `empire` joined the server's closed actor-kind
vocabulary in EP4.1 (R19: an empire's level is a `kind='empire'` row of the same `rpg_actor_progression` table), so any read that
omits `kind` now returns a row that is **not an actor**. The page's list panes always passed a kind; its two ledger tables did not,
and they are exactly the "where only actor kinds are expected" surface — `player`/`plant`/`zombie` are what the columns, the
row-click and the filter select all assume. `actorProgressionFold.ts` states that set once and both tables (plus their empty
states and pager labels) fold through it, so the omission cannot come back through a third table.

**Reviewed and deliberately NOT changed:** `useRpgProgressionSummary`/`Stats` are unfiltered aggregates over the save's whole
progression by design (they are totals, not actor lists), and `species`/`specimen` rows are non-actor too but have their own
surfaces — the fold drops those as well rather than naming only `empire`, which is what the vitest's second case pins.

**Not proved:** nothing in the FE renders an `empire` row on purpose yet (EP4.7's route is the read; a player-facing empire panel
is not specced), so this row's proof is that the actor surfaces cannot grow one by accident — the positive rendering path is
future work when a surface actually means to show the empire track.
