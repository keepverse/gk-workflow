# Capability Map: achievement-title

Initiative: plugin-based achievement system with atom-container titles, empire +
unique-actor scopes (decisions locked 2026-09-15 in
`achievement-title-ideal.md`). Idea doc is the parent; this map is the index —
never guess the active spec from filenames.

| Module id | Responsibility | Depends on |
|---|---|---|
| `achievement-registry` | Definition JSON grammars (achievement/title/bundle), closed scope/trigger/persistence/visibility vocab, tuning + catalog files, load validation with cause | — |
| `achievement-evaluator` | Cold event-driven evaluation over durable facts, exactly-once unlock ledger `(scope, definitionId, revision, factId)`, trigger watermarks, order-independent criteria | `achievement-registry` |
| `reward-bundles` | Fixed-core + weighted-pool draws via the existing instantiate path, seeded determinism inputs, ownership-root fan-out (specimen Roster mint, single item root, title grant), faucet-sink naming | `achievement-registry` |
| `empire-titles` | Hall inventory, 3-slot multi-equip, economy-path contributions (`P(Θ)` once), family/group/variant stacking + soft caps | `achievement-registry`, `reward-bundles` |
| `actor-titles` | Specimen earn/bind/equip contract, structural slot grammar beside 15-role gear, worn-display rule (highest tier), withdrawable bindings | `achievement-registry`, `reward-bundles` |
| `title-lifecycle` | Relative turn-window expiry with destinations, honor passive binds, hidden curses + priced ritual removal, grant/equip/expire dedupe split | `empire-titles`, `actor-titles` |
| `hall-surface` | Hall fold + closed bus + 4 shared factories + mount in PanelShell rail layer (T7b React) | `empire-titles`, `title-lifecycle` |
| `actor-title-surface` | Actor title tab fold + closed bus + mount in ActorPanel ninth tab (T7b React); consumes hall-surface factories, never forks | `actor-titles`, `title-lifecycle`, `hall-surface` (factories only) |

Build order: `achievement-registry` → `achievement-evaluator`, `reward-bundles` → `empire-titles`, `actor-titles` → `title-lifecycle` → `hall-surface` → `actor-title-surface` (Hall pieces first; surfaces otherwise independent)

Cross-program edge: `reward-bundles` is a **client** of the effect-pipeline
instantiate path (`TryInstantiate`/`InstanceProducer` compose — owned by
effect-pipeline module 4), never a second roller. Binding tables are owned by
their providers (`empire-titles`, `actor-titles`); `title-lifecycle` computes
policy intents the providers apply — never the reverse.

Rules: module ids stable kebab-case, never renamed. Dependency arrows one way;
interfaces live in the provider's spec. Specs: `docs/architecture/achievement-title/spec-<module-id>.md`.
Plan/todo (later, `/plan` phase): `tasks/achievement-title-plan.md`, `tasks/achievement-title-todo.md`.
