# Capability Map: world-action-economy

**Status: APPROVED 2026-09-15 (owner: "Approve all"). All 4 module specs written against this map as approved.**
**Ideal:** `docs/architecture/world-action-economy-ideal.md` (strengthened; owner resolutions locked; four locked `/spec` constraints).
**Specs land:** `docs/architecture/world-action-economy/spec-<module-id>.md`.
**Plan:** extends `tasks/empire-development-plan.md` Phase 4A (this map does not re-plan; it only bounds modules).

## Assumptions (correct before approving)

1. Shape is extend-`MovementRemaining` (locked) — no second pool, no `LaneCost` re-mint, no Admit-Reveal fork.
2. This map PRICES verbs owned by `empire-inventory-surfaces` (claim-cache/deposit kinds); it does not create command kinds — except where the debit site requires new payload (decided per module).
3. Numbers (per-act costs, hold allowance) are tunables in `world.v{n}.json` movement; exact values are spec-time content, not locked here.
4. Engine bump (`RulesetVersion` + golden re-bless) rides with the first behavioral change.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | act-price-table | `*CostMilli` rows + hold-allowance number in `world.v{n}.json` movement; loader wiring | — | 1 |
| 2 | budget-debit | Debit site honoring debit-after-refill (or refill-minus-spent); command-path integration | act-price-table; ext inventory cargo-commands | 1 |
| 3 | hold-allowance | Garrison allowance rule + number; `ReachMap`/admission/AI-slot/comment/fixture fan-out | act-price-table | 1 |
| 4 | claim-pricing | Claim (+deposit) price wiring; claim-vs-decay precedence; replay↔`CommandId` mapping | budget-debit | 2 |

Build order: `act-price-table` → `budget-debit` + `hold-allowance` → `claim-pricing`.
External dependencies: `empire-inventory-surfaces` (`cargo-commands`, `claim-endpoints` — the verbs being priced).
