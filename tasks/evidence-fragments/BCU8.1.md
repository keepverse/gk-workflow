# BCU8.1 — nerve.* VFX apply cues (live bug fix)

Added 3 missing StatusFx rows (nerve.unsettled/shaken/afflicted) to VfxCatalog.cs. Fixed the stale
"one row per catalog status" comment.

**Real hazard found and fixed before landing**: first draft's join-closure test asserted against
StatusCategoryRegistry.AllStatusIds -- a SHARED, MUTABLE, process-wide static dictionary
(ExhaustionPolicy/StanceRuntime instance constructors call Register() at construction time, not
compile time). Full-suite run failed with 3 extra ids from unrelated tests; Vfx-only run did not --
pure test-order pollution. Rewrote to pin the static 24-entry vocabulary from the source's own Map
initializer instead -- deterministic regardless of process-wide test order.

Also fixed StatusVfxCuesTests's now-stale exclusion comment, and bumped VfxRulesAndCatalogTests's
closed-vocabulary catalog-count pin (29->32, sanctioned by the test's own comment).

```
$ dotnet test gk-core/tests/FusionRpg.Core.Tests            (full suite, 14790 tests)
1 failure: SocketOperationsTests (pre-existing, save-share-hierarchy SSH2.6's own retirement gap)
$ dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Vfx   (second run, 174 tests)
174/174 green
```

Two unrelated pre-existing failures found and correctly left alone (AtomBenchGuardTests perf flake,
SocketOperationsTests file-not-found from another lane's file retirement, git-log confirmed).
