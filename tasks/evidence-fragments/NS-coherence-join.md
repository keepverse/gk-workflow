# Item: catalogue-coherence join for the cache domain (+ the closure that keeps joins honest)

Program `notification-ssot` · spec `docs/architecture/notification-ssot/spec-cache-notify-source.md` (its own module) ·
`notify-vocabulary` §1's rule: *a catalogue row no producer can emit can never fire, and a producer category with no
catalogue row throws at publish time*.

| Criterion | Command | Numbers printed |
|---|---|---|
| the cache domain's join, and the closure over all domains | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~NotificationCatalogCoherence"` | `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3, Duration: 56 ms` |
| the closure actually bites (mutation) | same filter with `JoinedDomains` reduced to `{ "world" }` | `Failed! - Failed: 1, Passed: 0, Total: 1` — `Collection: ["corpse-cache (cache.created, cache.decayed)"]`; reverted, `Passed! 3/3` again |
| boundary command | `.\scripts\verify-change.ps1 -Paths 'gk-core/src/FusionRpg.Server/Notifications/CacheNotificationSource.cs','gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationCatalogCoherenceTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK`; Server scope `Failed! - Failed: 1, Passed: 762, Skipped: 0, Total: 763, Duration: 2 m 6 s` |
| the same project, unfiltered | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | `Failed! - Failed: 2, Passed: 764, Skipped: 0, Total: 766, Duration: 2 m 5 s` — the two reds are `CombinationImportTests.A_refused_recipe_is_never_seeded` and `BaseTypeSocketMaxCorpusTests.A_base_row_above_its_role_ceiling_is_refused_at_load`, both other programs' (`SSH-RED-1`) |

**What was missing before this change.** The join existed for the `world` domain only
(`gk-core/tests/FusionRpg.Core.Tests/World/Notify/WorldNotifyCatalogCoherenceTests.cs`). A `corpse-cache` row that
no source emits — or a third domain added later with no join at all — would have passed every green suite.
`CacheNotificationSource` now names its two categories (`CreatedCategory`/`DecayedCategory` +
`KnownCategories`, the shape `WorldTurnNotificationClassifier.KnownCategories` already gives the world
domain) and the new Server test asserts both directions plus the closure.

**Open discrepancy for whoever owns the verification registry (not resolved here):** the boundary's
server scope reports **763** tests while the unfiltered project reports **766**, and the difference (3) is
exactly the new test file. The mapping for its path family exists
(`gk-core/tests/FusionRpg.Server.Tests/Notifications/**` -> `notify-server-domain`), so either the module scope
excludes untraited new tests or the counts differ for another reason; determining which would mean reading
the pipeline script, which this lane's rules forbid. The focused filter above is the evidence relied on,
and the boundary count is reported as printed.

**NOT proved:** not run at this head — the Guard catalogue contract (unchanged by this change) and the FE
coverage guard; the two known Server reds are not this program's and are tracked as `SSH-RED-1`.

### The specs now carry the widened rule (2026-09-21)

| Criterion | Command | Numbers printed |
|---|---|---|
| the two specs that state the join | `.\scripts\verify-change.ps1 -Paths 'docs/architecture/notification-ssot/spec-cache-notify-source.md','docs/architecture/notification-ssot/spec-world-notify-source.md' -Session notification-ssot-20260920` | `docs-and-assistant-config (focused)` + `guard: doc-boundary`; doc-citation audits `D1 0 (0 HIGH)` on both; `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4, Duration: 38 s` |

`spec-cache-notify-source.md` gains its own Testing row (both directions for `corpse-cache`, plus the
closure), and `spec-world-notify-source.md`'s Testing 9 now names the closure beside its world-domain
join, so the two half-guards read as one rule: every registered category joins to the code that emits it.
