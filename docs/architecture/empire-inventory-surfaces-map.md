# Capability Map: empire-inventory-surfaces

**Status: APPROVED 2026-09-15 (owner: "Approve all"). All 5 module specs written against this map as approved.**
**Ideal:** `docs/architecture/empire-inventory-surfaces-ideal.md` (strengthened; owner resolutions locked).
**Specs land:** `docs/architecture/empire-inventory-surfaces/spec-<module-id>.md`.
**Plan:** extends `tasks/empire-development-plan.md` Phase 4A/4B.2/4D (this map does not re-plan; it only bounds modules).

## Assumptions (correct before approving)

1. Backend trigger modules live in THIS map (commands serve these surfaces; the verbs were built by `scoped-inventory-hierarchy` but never triggerable).
2. This program owns `stock-row`, `capacity-meter`, and the relic shelf (CONFIRMED by owner 2026-09-16: "Approve") — the wonder program consumes by name.
3. AP pricing shape comes from `world-action-economy` (separate map); this map's command modules expose the debit site but do not price.
4. Phase 4C deployment gaps (lawn-death producer, wipe, delve claim, retrieval-mission) are NOT in this map — they extend `deployment-hierarchy`'s own specs.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | cargo-commands | `WorldCommand` kinds + payload + admission + resolver for load/unload/transfer/deposit/withdraw/claim-cache; closes the 3 audit-found spec drifts (shared capacity helpers, `playerId` decision, server-side `weightEach`) | — | 1 |
| 2 | claim-endpoints | REST: list claimable caches, post claim (production `weightEachFor` resolver), cargo contents/capacities read-back DTOs | cargo-commands | 1 |
| 3 | storage-content | One `ItemStorage` seed row via the structures authoring path (never hand-edited if generated) | — | 1 |
| 4 | legion-sheet | Sheet-menu + cargo sub-tab spec (UI): tabs, `cargo-fold` binds, `cargo-actions` bus, refusal copy | cargo-commands, claim-endpoints | 2 |
| 5 | storage-cache-ui | Storage panel block, cache-claim flow, `cache-pin` (hidden-until-found), capture header + toast (UI) | claim-endpoints, storage-content | 2 |

Build order: `cargo-commands` + `storage-content` → `claim-endpoints` → `legion-sheet` + `storage-cache-ui`.
External dependents (not this map): `empire-wonder-surfaces` (shared pieces, shelf), `world-action-economy` (prices these verbs).
