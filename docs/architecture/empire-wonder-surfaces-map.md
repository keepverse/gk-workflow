# Capability Map: empire-wonder-surfaces

**Status: APPROVED 2026-09-15 (owner: "Approve all"). Strengthen-pass amendment same day: module 5 `wonder-wire` added (was an unowned orphan — no spec owned the catalog/slot REST fields); specs for modules 1-4 written against this map as approved, module 5 spec dispatched on the amendment.**
**Ideal:** `docs/architecture/empire-wonder-surfaces-ideal.md` (strengthened; owner resolutions locked).
**Specs land:** `docs/architecture/empire-wonder-surfaces/spec-<module-id>.md`.
**Plan:** extends `tasks/empire-development-plan.md` Phase 4B.1/4B.4/4D (this map does not re-plan; it only bounds modules).

## Assumptions (correct before approving)

1. Shared pieces (`stock-row`, `capacity-meter`, relic shelf) are CONSUMED from `empire-inventory-surfaces`, never re-specified here (ownership CONFIRMED by owner 2026-09-16: "Approve").
2. Reachable-first picking spans the legion sheet cargo tab + sector store (locked sibling direction).
3. Reserved tiers render as locked teasers; live cap counts shown; composer is a panel (all locked).
4. Runtime-corpus relic rows stay the §Design 4b item-program ask — not a module here.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | wonder-rest | `WorldCommandRequest.RelicInstanceIds` + endpoint mapping + the owed live proof (file → commit → `build.started` + consumed) | — | 1 |
| 2 | wonder-content | Sector + Empire Wonder seed rows via the structures authoring path (never hand-edited if generated) | — | 1 |
| 3 | wonder-wire | Catalog/slot REST wire fields (WonderScope/Rarity/RelicCost/ExistenceCap/LiveWonderCount/slot facet/upkeep/production/reachability) — the reads composer/display require | wonder-content | 1 |
| 4 | wonder-composer | Composer + cost-plate + refusal UI spec (reachable-first, live counts, locked teasers) | wonder-rest, wonder-content, wonder-wire; ext inventory shelf | 2 |
| 5 | wonder-display | Sector card, scope/rarity packs, construction-progress (backend reads from wonder-wire) | wonder-content, wonder-wire; ext inventory meter/row | 2 |

Build order: `wonder-rest` + `wonder-content` + `wonder-wire` → `wonder-composer` + `wonder-display`.
External dependencies: `empire-inventory-surfaces` (shared pieces, shelf, reachability Appendix: relic spend path).
