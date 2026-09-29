# Evidence — D4.31's second blocker: cell diversity and the budget-scope mismatch (lane `pd-d3`, 2026-09-23)

No code. One measurement pass; D4.31 keeps `[ ]` and now has two named blockers instead of one.

| Criterion | Printed reading | Conclusion |
|---|---|---|
| how many distinct cells do the six domains reach? | real `DomainEncounterCoverage.Report`'s own seed derivation, `sampleSeeds: 32` | `air=9 dark=9 earth=9 fire=9 ice=9 light=8`, **`UNION_OVER_SIX=11`** |
| is it a sampling artefact? | same rooms over **256** seeds instead of 32 | `9` per domain — the same set; the constraint is the corpus, not the seed count |
| what does the budget row actually say? | `gk-data/packs/fusion/data/seed/dungeon/_plan/budget.v1.json`'s `dungeon-encounter` row | `{cells: 9, target: 81, perCell: null, tolerance: {under: 0, over: 1}, firstShip: 40, dimension: [formation, elementSpread]}` |
| what is `firstShip` for? | the same file's `dungeon-domain` row's own rationale | "First ship is six many-domains at shallow, one per climate" — so `firstShip` is the **six-domain** figure |
| what does the test compare against? | `grep -n budgetTarget gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainEncounterCoverageTests.cs` | `budgetTarget: 81` at `:74`, `:99`, `:126` — the **corpus-wide** figure, passed to a **per-domain** call |

**The finding, stated once**

The metric is short by ~3.6x against the budget row's own first-ship figure (11 measured, 40 expected for the
six domains together) and ~7x against the 81 the test actually uses. Because the six domains' cells barely
differ (union 11 vs per-domain 8-9), no amount of per-domain sampling fixes it: the `dungeon-encounter`
corpus and the species tuples its slots can draw simply do not produce 40 distinct
`(postureMultiset, elementSpread, formation)` shapes today.

**NOT proved**

- D4.31 was not closed and no fix was attempted: F15's routing is not this lane's, and the diversity/budget
  question is a content-plus-budget-owner decision.
- I did not prove 40 is unreachable *in principle* — only that the current corpus reaches 11. A content pass
  could still get there; the row says so rather than declaring the budget wrong.
- The scope mismatch (81 per-domain vs 40 six-domain) is a reading of the budget file and the test's call
  sites, not an owner ruling on which scope the metric *should* use. Both readings are in the row.
- No probe was committed: the two throwaway tests were removed before this commit and `git diff` for that file
  is empty.
