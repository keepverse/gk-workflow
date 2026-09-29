# EP4.1 — Core: `RpgActorKinds.Empire`, `EmpireSpeciesLevelUp`, the `ParamsFor` arm, `EmpireLevelGrants`

Commit `@EP4.1` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-empire-level.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `RpgActorKinds` has 6 members, `EmpireLevelGrantKind` has 1, both pinned with the reason (test 7) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EmpireLevelGrants"` | `Passed! - Failed: 0, Passed: 10, Skipped: 0, Total: 10` | `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs` (`Empire`, `IsKnown`), `gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs`, `tests/FusionRpg.Core.Tests/Progression/EmpireLevelGrantsTests.cs` |
| `EmpireLevelGrants.For` is pure; `freeRespecsPerEmpireLevel = 0` gives no grant | same | `Passed: 10` (incl. `For_grants_nothing_when_the_published_stock_is_zero`, `For_grants_the_published_free_respec_stock`) | `gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs` |
| A reflection test shows `EmpireLevelGrants` declares no level-shaped curve method (test 5, reflection half) | same | `Passed: 10` (incl. `The_grant_rule_declares_no_level_shaped_curve`) | `tests/FusionRpg.Core.Tests/Progression/EmpireLevelGrantsTests.cs` |
| `ProgressionTuning` parses `xpCurve.empire` and `awards.speciesLevelUp`; `v1` not yet changed | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EmpireLevelGrants\|FullyQualifiedName~RpgActorKinds\|FullyQualifiedName~ProgressionTuning"` | `Passed! - Failed: 0, Passed: 20, Skipped: 0, Total: 20` | `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs` |
| One power ladder: no private `f(level)` | `python gk-core/scripts/guard-power.py` | `POWER GUARD OK — one ladder, pin holds, no private f(level)` (exit 0) | — |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths <the 4 paths above> -Session empire-progression-3` | exit 0; test: `core` -> `FusionRpg.Core.Tests 12752/12752` plus the 11 Core shards `15, 498, 31, 1351, 30, 210, 7, 12, 238, 4, 9` — **15157 passed, 0 failed**; no static guard selected for a Core-only change | — |

**Correction (2026-09-21, in EP3.11's commit; superseded again by EP4.2 — see below).** The run above is green, but it was taken *before* the last edit of this
row — the `spec-empire-level.md` deviation note — and that note names `progression.v2.json`, a concrete token
`SpecChannelClaimTests.NoSpecClaimsAnUnregisteredChannel` requires to be verified as a non-channel. It broke
`FusionRpg.Core.ActorHub.Tests` (1 failed, 497 passed) and the EP4.1 commit shipped with that guard red. EP3.11's
commit adds the token to that test's `KnownNonChannelTokens` with its own verified reason and re-runs the boundary.
The lesson kept: a doc edit is code as far as the guards are concerned, so the boundary run has to come last.

**Second correction (EP4.2's commit): the presence-tolerant parse this row shipped was superseded.** EP4.2 published
`progression.v3.json` with both keys, moved every pin of the previous version in the same commit (H7), and made
`xpCurve.empire` / `awards.speciesLevelUp` REQUIRED at parse — so the "presence-tolerant at parse, refused at first
use" behaviour described above is no longer the shipped behaviour, and this row's own `An_older_document_...` test
was replaced by two refusal tests plus one in-code-tuning test. The decision it recorded was right for EP4.1 and
is kept here as the record; the spec's final paragraph now describes EP4.2's stricter state.
| Ledger check | `python gk-core/scripts/anchor-ledger.py tasks/empire-progression-ledger.jsonl check` | `LEDGER OK (…)`, exit 0 | — |

**Decision (recorded, deviating from the spec's literal text).** The spec's §Tunables wants `xpCurve.empire` hard-required at
parse. `progression` is a multi-publisher domain with a single-revision pin topology and **no "find latest" resolver**: the live
host is `gk-core/src/FusionRpg.Server/Program.cs:149` reading `progression.v2.json`, and ~30 test fixtures pin a literal
`progression.v{n}.json` path. A parse-time requirement would make the shipped server and every one of those fixtures unloadable
in the commit that adds the key — before EP4.2 moves them. So both new keys are **presence-tolerant at parse and refused by name
at first use** (`RpgXpCurve.ParamsFor(RpgActorKinds.Empire)`, `RpgXpAwards.SpeciesLevelUp`), the discipline
`XpAwardsTuning.ZombossRunVictoryXp` already established in the same file. Nothing is defaulted: absent is `null`, and the read
throws naming the key. EP4.2 may tighten this to a parse requirement once its pins move.

**Not proved** (out of this lane's fence — see the session record; rows stay open in the program's todo):
- EP4.2: the publish, the pin moves (`gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ProveHubCombat`, `gk-forge/tools/_TempSeedSpecies`) and
  the `ssot-power-scale.md` §10.1 row — `gk-core/src/FusionRpg.Server/**` and `docs/architecture/power/**` are outside `--allow`.
- EP4.3/EP4.5/EP4.6/EP4.7: the store credit, the ledger and the routes — all `gk-core/src/FusionRpg.Data/**` / `gk-core/src/FusionRpg.Server/**`.
- EP3.11/EP3.12: the production half (`RpgStore.WorldTurns.cs`) is Data. Read this session for whoever takes them: the provider
  already composes `Aptitude = commander + specimen` (`RpgStore.WorldTurns.cs:559-592`), so "no `CreatureType` points" is
  already satisfied there; what is missing is the `commander.away` skip. And the spec's premise *"no writer set `InstanceId`
  before this module"* is **stale** — EP3.8's `attach-commander` writes it, so EP3.11's golden analysis must not assume it.
- No `gk-core/data/tuning` file was touched, so `resource_ownership.py --check` was not run.
