# TVB5.1.k — Fix `BLOCKS SPLIT` own-path literal k

No fix needed. Re-ran the analyzer fresh against the current tree (post-mega-merge, well after
TVB1.10's original run) rather than trusting a stale reading.

| Criterion | Command | Result |
|---|---|---|
| Build | `dotnet build tests\FusionRpg.Core.Tests -c Release` | succeeded, 58 warnings, 0 errors |
| Fresh run | `dotnet run --project tools\TestSplitAnalyzer -c Release -- --project tests\FusionRpg.Core.Tests\FusionRpg.Core.Tests.csproj --configuration Release --format md/json --out <path>` | exit 0 |
| `BLOCKS SPLIT` findings | inspect `blocksSplit` in the JSON output | `[]` — empty, matching TVB1.10's original zero-finding result |

**Readings from this fresh run** (never asserted, printed for scale — comparison against TVB1.10's
2026-09-19 reading, tasks/evidence-fragments/tvb1-10.md): 68 proposed clean projects (was 65 — three
new clean candidates appeared from work merged since TVB1.10, most visibly `Saves` and `Workspace`,
new folders from the save-identity/species-progression lane); the 10-candidate residual is
**unchanged**: `Actions, Battle, Combat, Creatures, Delve, EffectBagAuditTests, EffectBagTests,
EffectFunnelTests, Scope, World`.

**A real, load-bearing finding for later increments (not this task's job to fix):** `Workspace` is
now a proposed clean candidate, and `tasks/sessions/keepverse-split.json` (a separate, active,
direct-mode session on `features/mega-merge`) claims `tests/FusionRpg.Core.Tests/Workspace/**` for an
unrelated multi-repo-split change. TVB5.5's manifest and TVB5.7/5.8.k's increment ordering must not
pick `Workspace` as an early increment while that session is live — recorded here and in the ledger
so a later increment does not rediscover it.

The known instance the map/spec cite,
`PassiveTree/GateCounters/GateCounterBoundaryGuardTests.cs:97`, is confirmed (again) not to cross a
candidate boundary at today's top-level-folder granularity — both the reading file and the referenced
file live under `PassiveTree/`.

Files: none — no test file needed a fix. Evidence fragment + ledger + todo checkbox only.
