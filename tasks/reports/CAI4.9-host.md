# CAI4.9 owed item (3) — the injector admission host

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. I had recorded this half as blocked on CAI4.3's missing
`ActionCatalog`. Re-read against the code, **that was wrong**: the queue is Core and admission is
`LawnOrderQueue.Offer`, which needs no catalog — only the FIRE path needs the held set (row 14's hook,
whose gate check is what compiles an action). So the verb, the host and the registry drops landed, and the
remaining blocker is narrower than the row said.

| Criterion | Command | Result |
|---|---|---|
| The order reaches the Core queue with the tick and the run identity stamped | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnOrderHostTests"` | **10 passed / 0 failed** — `A_complete_order_reaches_the_queue_with_its_tick_and_run_identity_stamped` asserts `ScopeId == "match.7"` and `IssuedTick >= 0` (the engine clock's stamp, never a wall clock) |
| An incomplete payload is a REFUSAL, never an exception into the frame | same run | **10 / 0** — the `[Theory]` covers a null/blank `matchKey`/`actorKey`/`actionId`: nothing queued, one refusal counted |
| The death edge drops exactly that actor's order; a reused ptr starts clean | same run | **10 / 0** — `Remove_drops_exactly_that_actors_order` and `A_reused_ptr_starts_with_no_order` |
| The board edge clears every order | same run | **10 / 0** — `Clear_drops_every_order_and_the_counters` |
| A second order supersedes rather than queues behind | same run | **10 / 0** — the Core queue's rule, reached through the adapter |
| The verb the Server relays is the name the host dispatches on | same run | **10 / 0** — pinned by value, because the injector does not reference the Server assembly |
| The injector still compiles (a skip-stub is not a build) | `pwsh -NoProfile -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK — MelonLoader host compiled to %TEMP%\fusionrpg-injector-compile\` |
| The project, and the program's guards | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests`; the seven guards | **87 passed / 3 failed** — all three are the pre-existing stale `LawnBasicAttackFeatureFlagTests` (`CAI-find-1`); guard-dal, guard-single-writer, guard-funnel-delta, guard-actor-hub, guard-secondary-no-unity, guard-test-substrate, guard-debug-scope **all exit 0** |

## The two lookups, and the one visibility change

- The TICK is `KernelDriveHost.NowTicks` — the engine clock the lawn's cooldowns and status expiry already
  read (D15), never `DateTime`; the queue compares it and holds no clock of its own.
- The IDENTITY is `CheatState.ResolveBoundInstanceId`, the shipped ptr→Bound-instance lookup. It was
  `private`; it is now `public`, which is the *"reuses what already exists"* rule taken literally — the
  alternative was a second copy of its four lines in the injector.
- The run identity (`ScopeId`) is the live match key the Server already stamped, so a stale order is
  refusable by `DirectOrderAdmission.CheckScope`.

## What remains, precisely

**The fire path, and only that.** Module 19's frame slot marks the actor due (`CAI4.8`, blocked on the lawn
plan's `lawn-perf-budget.v1.json` = `LW1.1`), and the composition root supplies row 14's forced-intent hook
(`IntentRouter.forcedIntent`), whose gate check needs module 16's held set and therefore the `ActionCatalog`
feed — still `CAI4.3`'s unowned blocker, which needs a routing or erratum decision rather than more code.
The two `web/**` files are outside this lane's fence.
