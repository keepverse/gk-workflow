# CAI4.9 — rows 3–5's supply: the two additive durable-identity fields

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row recorded four owed items. This lands the first
one — *"the **supply** for rows 3–5 — the two additive `SubjectId`/`ScopeId` fields on
`Core/Actions/DirectOrder.cs`"* — and names the other three exactly. Evidence lives here rather than in
`tasks/evidence-fragments/` because that directory is not in this lane's allowed paths.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The two fields exist, are **trailing and optional**, and break no existing construction | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --nologo --verbosity quiet` | **301 passed / 0 failed** — the whole project, including every pre-existing `LawnOrderQueueTests`/`DirectOrderAdmissionTests`/`LawnDecisionLoopTests` case, compiles and passes untouched | `gk-core/src/FusionRpg.Core/Actions/DirectOrder.cs` |
| Rows 3–5's rules are now fed from the ORDER rather than from loose arguments | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnOrderQueueTests"` | **13 passed / 0 failed** (was 11) — `An_order_carries_its_durable_identity_through_the_queue_and_the_rules_decide_on_it`: `Offer` → `TryPeek` returns `SubjectId`/`ScopeId` intact, then `CheckScope(order.ScopeId, "match.7")` = `None` and against `"match.8"` = `StaleRun`; `CheckSubject` = `None` for the order's own ptr, `SubjectMoved` for a reused address, `SubjectGone` for a missing `Bound` row | `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnOrderQueueTests.cs` |
| The planted violation has teeth | (the second `CheckScope` assertion is the planted check) | dropping the scope comparison in `DirectOrderAdmission.CheckScope` — or feeding it the live run instead of the order's own — makes that one assertion red, which is what keeps "an order from another run" from commanding a creature in the next match | `DirectOrderAdmission.cs:107-110` |
| The identity-free order is the shipped order | same run | **13 / 0** — `An_order_without_the_durable_identity_is_still_the_shipped_order` asserts both fields read `null` and the peeked value equals the offered one, i.e. the two fields are additive and not a second order shape | same |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed / 0 failed** | — |
| Guards | `guard-actor-hub`, `guard-single-writer`, `guard-funnel-delta`, `guard-dal`, `guard-test-substrate` | all **exit 0** | — |

## The three items still owed, each named exactly

1. **Row 14 — an order as a rank-0 candidate.** Its blocker is specific and is a design boundary, not
   missing knowledge: firing a live order *through the gates* needs a forced-intent hook on
   `IIntentSource`, and **no implementation exposes one** — `CoreIntentPolicy`, `IntentRouter`,
   `StubIntentSource`, `SiegeAiIntentSource`, `NoneIntentSource`, `InteractiveIntentSource` and
   `AiDecisionRecordingSource` are seven implementations, so the hook is a reviewed interface change
   across all of them rather than a local edit. `IntentRouter.ConsumeExpiredOrder`'s own comment
   reserved this ("that plumbing is `commander-direct-orders`' own commit, named here rather than
   guessed at").
2. **The Server endpoint, the Injector verb/host/registry.** The Injector half **shares CAI4.3's
   blocker**: it compiles through an `ActionCatalog`, and the injector has no catalog and no feed for
   one (`ActionCatalogHost` has zero users in `src/`; the only builder is `RpgStore.BuildActionCatalog`,
   Data-side). The Server endpoint itself is in this lane's fence and is not blocked.
3. **The two `web/**` files** — outside this lane's fence (`gk-web/web/fusion-rpg-web/src/{lib/bus/mutations,ui/lawn/lawnInteractiveObservable}.ts`).

**No longer blocked:** item (4) on the row, `data/tuning/combat-ai.v*.json`'s two order keys, was recorded
as H7-forbidden because "both readers name `combat-ai.v1.json` by hand and both are out of fence". This
lane holds `gk-core/data/tuning/**` **and** both readers (`Server/Program.cs`, `Injector/Host/RpgHost.cs`), so a
publish can switch its readers in one commit — the same unblocking CAI3.1's `siege.v3.json` used.
