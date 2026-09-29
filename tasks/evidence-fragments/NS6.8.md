# NS6.8 — Recipe `notices.json`, then the owner piece review (PARTIAL — recipe done, review blocked)

| Criterion | Command | Result |
|---|---|---|
| `docs/design/gui-lego/recipes/notices.json` beside the existing recipes, using only pieces from NS6.6's map; any new piece or density is an ERM amendment named, not invented | wrote `docs/design/gui-lego/recipes/notices.json` | Reuses `tool-search`, `chip`, `source-list`, `surface-shell`, `scroll-region`, `phase-*` verbatim (all pre-existing, cited in NS6.6's map). Names one genuinely NEW piece, `notice-row`, explicitly as a new piece at the ALREADY-EXISTING Row rung (`channel-row` is the precedent that rung is real) — never claimed as free, and its exact field set is left for the owner review to accept or amend, not invented as final |
| `cd web\fusion-rpg-web; npm test -- features/gui-lego` (recipe schema tests) | `npx vitest run features/gui-lego` | `Test Files 13 passed, Tests 119 passed` — no schema validator auto-discovers recipe JSON files (confirmed: the new file is pure data, not yet registered anywhere, since `NoticesSurface.tsx`/`registerRecipe` calls are NS6.11's job) |

**Blocked, not a default-resolvable ask:** "the owner has reviewed pieces, payloads and the
assembled look (GUI Lego step 7), recorded with a date in the recipe's meta or the queue row" has
**no stated default** anywhere in the spec or the authoring procedure — unlike NS6.7's queue-row ask,
which explicitly names "the row is added... if unanswered" as its resolution. This review is a real
owner action (per `gui-lego-authoring.md` step 7, "Owner gate — accept piece boundaries / payloads /
assembled look") that cannot be simulated or defaulted. Per the spec's own explicit design, **this
review holds only NS6.11's first React commit** — NS6.9, NS6.10 (already built) and NS6.12's fixture
work are unaffected and proceed. The todo checkbox for NS6.8 is left unticked; the recipe-authoring
half is done and evidenced here.
