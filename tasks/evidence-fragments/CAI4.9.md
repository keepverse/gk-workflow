# CAI4.9 — `commander-direct-orders`: the order queue and the refusal rules (Core half)

Lane `cai4` (session `combat-ai-4`). Row: `tasks/combat-ai-todo.md` CAI4.9.
Spec: `docs/architecture/combat-ai/spec-commander-direct-orders.md`.

**Canonical fragment.** The queue-and-classifier half was evidenced at `tasks/reports/CAI4.9.md`
before the manager widened this lane's fence to include `tasks/evidence-fragments/**`; this file is the
complete fragment and supersedes it.

## What landed

| File | What it is |
|---|---|
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnOrderQueue.cs` | The lawn's `IOrderQueue`: one live order per actor (a second **replaces** and reports `Superseded`), the structural `Cap` 16 refusing the NEW order and never evicting a stranger's, `TryPeek`/`Commit`/`Expire`/`Remove`/`Clear` for every key-set edge, `HandleGateRefusal` (retryable stays live, terminal removes), and a per-order reason bitmask so one refusal reports once |
| `gk-core/src/FusionRpg.Core/Match/Ai/DirectOrderAdmission.cs` | The closed `DirectOrderRefusal` vocabulary, the retryable/terminal projection of `UsabilityReason`, `IsHeld`, and — added in this segment — `CheckScope` / `CheckSubject` with their `OrderSubject` record |

Tests: `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnOrderQueueTests.cs` (11) and
`DirectOrderAdmissionTests.cs` (9) — 20 in all.

## The three identity refusals, and why they could land without the owed fields

`CAI4.9`'s row text said rows 3, 4 and 5 need the two additive `SubjectId`/`ScopeId` fields on
`Core/Actions/DirectOrder.cs`. That is true of the **transport** and false of the **rules**: the spec's
§2 steps 1–4 are pure comparisons over two facts, so `CheckScope(orderScopeId, liveScopeId)` and
`CheckSubject(in OrderSubject subject, string orderActorKey)` take them as arguments. The rule is
therefore complete, tested and mutation-killed here, and when the field lands there is still exactly one
implementation of each comparison for it to call. What remains owed is the *supply*: the two fields, the
injector host that resolves a subject, the Server endpoint, and the two `web/**` files.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| 1. An admitted order is returned for its own actor and no other | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnOrderQueue\|FullyQualifiedName~DirectOrderAdmission"` | **20 passed / 0 failed** |
| 2. A second order REPLACES the first and reports it | same | 20/0 |
| 3. An order issued in a different run is refused `StaleRun` | same | 20/0 |
| 4. A binding naming a different ptr is refused `SubjectMoved`; a matching one is admitted | same | 20/0 |
| 5. No `Bound` row ⇒ `SubjectGone`, and admission invents no subject | same | 20/0 |
| 6. An action outside the held set is refused `NotHeld` | same | 20/0 |
| 7. `TryPeek` at `IssuedTick + lifetime - 1` returns it; at `+ lifetime` it expires — no `DateTime` on the path | same | 20/0 — driven through the **real `IntentRouter`**, so the lifetime comparison keeps its one implementation |
| 8. A retryable refusal stays live; a terminal one is removed | same | 20/0 |
| 9. The classifier is total over `UsabilityReason` | same | 20/0 (walks the enum; pins 8 retryable / 3 terminal, so an unclassified member cannot default to retryable) |
| 10. The same reason twice ⇒ one report; a different reason ⇒ a second | same | 20/0 |
| 11. Death removes the order; a reused ptr finds none — both orders | same | 20/0 |
| 12. The board edge and the kill switch each clear every order | same | 20/0 |
| 13. At `Cap`, a new order is refused `QueueFull`, no existing order evicted | same | 20/0 |
| 15. `Commit` removes the order; a second `Commit` is a no-op | same | 20/0 |
| **Mutations** — no replacement; evict-at-cap; a reason flag instead of a set; the three Terminal members left unclassified; `StaleRun`'s comparison; `SubjectMoved`'s comparison; the not-bound guard | each planted, run, reverted | **3, 1, 1, 2, 1, 1, 1 red** respectively; 20/20 green after every revert |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | 5 passed / 0 failed |
| `verify-change` — the identity rules | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Match/Ai/DirectOrderAdmission.cs','tests/FusionRpg.Core.Balance.Tests/CombatAi/DirectOrderAdmissionTests.cs') -Session combat-ai-4` | exit 0; **39 distinct test projects, 0 with any failure** (summed per-project counts 15710 passed / 0 failed) |
| `audit-overflow.py --targets A3`; `guard-actor-hub.ps1` | see above | both exit 0 / OK |

## Re-verified at the merged head

See `tasks/evidence-fragments/CAI4.2.md` § "Re-verified at the merged head" — the same run covered all
four rows' paths; no file this row owns and no dependency it reads was touched by the merge.

## Still owed, all outside this lane's fence — the row stays open

1. The two additive `SubjectId`/`ScopeId` fields on `Core/Actions/DirectOrder.cs` (the supply for rows 3–5).
2. `Actions/IntentRouter.cs`'s forced-intent hook — row 14, *an order as a top-rank candidate* — which
   CAI1.10 explicitly reserved for this module ("no `IIntentSource` implementation exposes that hook today").
3. `Server/LawnOrderEndpoints.cs`, `Injector/CheatCommandRunner.cs`, `Injector/Effects/LawnOrderHost.cs`,
   `Injector/Effects/InjectorEntityRegistry.cs` and the two `web/**` files.
4. `data/tuning/combat-ai.v*.json`'s two order keys. **H7 forbids publishing them here**, and the manager
   has routed that as **CAI-F1** with the instruction not to publish a revision until it lands; the
   lifetime therefore arrives as the router's own `orderTimeoutTicks` argument and the cap is the
   structural `LawnOrderQueue.Cap`.
