# CAI3.1 — `stance-wiring`: the two dead keys deleted, with their reader (H7)

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The seam half landed in lane `combat-ai-2`/`combat-ai-3`;
this is **Outcomes 2/3** — the deletion of `ai.stanceDefault` and `ai.autoResolveHandicapMilli`, which was
routed as blocked because "a publish that cannot switch its reader in the same commit is what H7 forbids, so
the *file* is in fence and the *change* is not". Re-read this session, **both readers are in this lane's
fence** (`gk-core/data/tuning/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector/**`), so H7 is satisfiable
here and the row closes. Evidence lives here rather than in `tasks/evidence-fragments/` because that
directory is not in this lane's allowed paths.

## The criterion's answer, restated as the commit body states it

**No held action is a stance action today** (the seam half's own finding). So this is Outcome 1's seam
already landed plus Outcome 2/3's deletion: nothing reads either dead key, which is what makes removing them
a FILE change rather than a behaviour change. The commit names each file change's outcome.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `siege.v3.json` produced by **one** `--remove-key ×2` invocation (not two publishes, not by hand, not by extending the tool) | `python gk-core/tools/tuning/publish.py siege --remove-key ai:stanceDefault --remove-key ai:autoResolveHandicapMilli --label "..."` | one publish: `published siege (v2 -> v3, 2 change(s)); v2 stays on disk for revert`. A JSON diff of v2→v3 shows exactly `REMOVED /ai/autoResolveHandicapMilli`, `REMOVED /ai/stanceDefault`, `CHANGED /version 2 -> 3` and the publish label — nothing else | `gk-core/data/tuning/siege.v3.json` |
| `AiTuning` has **two** members | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Siege"` | **333 passed / 0 failed** — `public sealed record AiTuning(int ObjectiveReferenceDistanceCells, int ThreatRadiusCells)` | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:64-66` |
| `SiegeTuning.Parse` reads exactly those, and rejects **neither** an older file carrying the two removed keys **nor** a newer one that does not | same run | **333 passed / 0 failed** — `SiegeTuningContractTests.A_file_with_the_two_dead_keys_and_one_without_parse_to_the_same_record` now compares the SHIPPED `siege.v3.json` against v3-with-the-keys-put-back, and asserts the `Ai` records are equal | `gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs` (`ValidateRemovedKeys`) |
| A MALFORMED removed key is still refused (absent is legal, wrong is not) | same run | **333 passed / 0 failed** — `A_malformed_dead_key_is_still_rejected` (`"Bogus"`), `A_non_integer_handicap_is_still_rejected` (`"not a number"`). The validation stayed with the fields removed, deliberately: dropping it would make a typo in a key nobody reads invisible | same |
| The three `ContractTuningTestBootstrap` constructions lose two arguments each | build + focused run | `gk-core/tests/FusionRpg.Core.Tests.Shared`, `gk-core/tests/FusionRpg.Data.Tests` (**24 passed / 0 failed** on a focused filter), `gk-core/tests/FusionRpg.E2E.Tests` (**Build succeeded**); a fourth site the row did not name, `SiegeAiLiveWiringTests.SiegeAiTuningForTest`, lost the same two | four files |
| The reader switched in the SAME commit (H7) | same run | **333 passed / 0 failed** — `SiegeKeyMigrationTests.Both_hosts_load_the_same_file` now asserts `siege.v3.json` in `Program.cs`; the new `Siege_v3_is_the_shipped_file_and_no_longer_carries_the_two_dead_keys` pins that v3 lacks both keys and parses to v2's `Ai` | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/PowerAndAptitudeTuningTestBootstrap.cs` |
| `Siege_v2_still_carries_the_two_dead_keys` deleted here; migration-fidelity assertions untouched | same run | **333 passed / 0 failed** — the test is replaced by the v3 pin above; `Siege_v2_no_longer_carries_the_ten` and `Siege_v2_still_carries_the_two_geometry_keys` are untouched | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/SiegeKeyMigrationTests.cs` |
| `StanceRuntime.cs`, `PoiseLedger.cs`, `Riposte.cs` unmodified; the three stance/aura suites pass unchanged | `git diff --name-only HEAD`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Stance\|FullyQualifiedName~AuraRuntime"` | all three files untouched; **186 passed / 0 failed** (StanceSeamTests, DefenceActionStanceTests, DefenceActionStanceSlotTests, AuraRuntimeTests) | — |
| Golden: byte-identical; `RulesetVersion` stays 5 | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Siege\|FullyQualifiedName~BattleGolden"` | **338 passed / 0 failed** (333 siege + 5 goldens) — no golden moved, and `BattleModels.cs:284` still reads `RulesetVersion = 5` | — |
| The rest of the boundary | guards; `BootContentCopyRuleTests`; audits | `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-secondary-no-unity`, `guard-test-substrate`, `guard-doc-citations -Strict` **all exit 0**; `BootContentCopyRuleTests` **2 passed / 0 failed** (v3 is copied to the boot dir); `resource_ownership.py --check` OK (166/166 edges); `audit-magic-numbers.py --summary` TOTAL 0 | — |

## Doc citations the edit moved, and one stale claim it exposed

Re-anchored in the same commit: `spec-aggression-tier-map.md:38` cited `siege.v1.json`'s `ai.aggressionRange`
"parsed at `SiegeTuning.cs:361-363`" — stale since CAI1.8 moved the ten keys; it now names
`combat-ai.v1.json` and `CombatAiTuningLoader.cs:167-170`, where the `> 0` refusal actually lives.

**`SiegeAi.cs`, `CandidateScorer.cs` and `SiegeAiIntentSource.cs` were re-edited to preserve their line
counts exactly** (the record keeps three lines with two members; the two doc comments were trimmed back to
their original heights), so the ~20 `file:line` citations into those three files did **not** move and needed
no re-anchoring. Only `SiegeTuning.cs` shifted (-1 to -9 depending on region), and it carries two citations,
both handled above.

`CAI-find-2` (filed in `tasks/combat-ai-todo.md`): `spec-ai-tiers-personality.md:200` claimed "the loader
already refuses a negative weight, `SiegeTuning.cs:346-349` is the shipped precedent". That anchor was
inside the removed block, and read against the code the claim is **false as of CAI1.8** —
`CombatAiTuningLoader.ParseScoring` (`:161-177`) has no sign check for any of the seven weights. The spec
row now says so and points at the finding.
