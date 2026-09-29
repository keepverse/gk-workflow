# TVB-F21 — the two gating guards reddened by SSH6.7 (`6628381d8`), fixed at the cause

Both guards exit 1 at the integration head; both findings trace to ONE commit, `6628381d8`
("feat(SSH6.7): the boot checks the pricing's provenance before anything binds"), which added
`gk-core/src/FusionRpg.Server/ComboPricingBoot.cs` and `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs`.

| Guard | Before | Cause read from the source | Fix | After |
|---|---|---|---|---|
| `scripts/guard-magic-numbers.ps1` | **exit 1** — `M2 [HIGH] gk-core/src/FusionRpg.Server/ComboPricingBoot.cs:46 public const int TierLadderRungCount = 1;` (+ M4 LOW, same line) | a balance-worded const **in code** whose own doc comment says it mirrors what the tuning publishes — the file's own `StrainSpliceTuning.TierLadder` already derives that ladder from `minTierPlan`, so the const was the second source of truth it claimed not to be (tunables-ssot T1) | the const is deleted; `RequireVerified` now takes the `StrainSpliceTuning` the boot already loaded and reads `strainSpliceTuning.TierLadder.Count`; `Program.cs` passes `strainSpliceTuning` | **exit 0** — `M1=0 M2=0 M3=0 M4=0`, `0 finding(s)` |
| `scripts/guard-population-pin.ps1` | **exit 1** — `P1 gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:70 Assert.Equal(64, loaded.CombinationCorpusDigest.Length) has no pin: marker` | `64` is SHA-256's hex width, not a population; the marker vocabulary is closed (`closed-vocabulary <Owner>` / `immutable <gk-core/data/tuning/…v<n>>`) and the spec says an unmarked pin is a population pin whose fix is to **rewrite it as the contract**, never to add a marker | the assertion is now `Assert.Equal(SHA256.HashSizeInBytes * 2, loaded.CombinationCorpusDigest.Length)` with a comment naming the rule, keeping the existing `All(Uri.IsHexDigit)` assertion | **exit 0** — `0 finding(s)` |

| Criterion | Command | Result |
|---|---|---|
| the affected tests | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ComboPricing"` | **Failed 0 / Passed 3 / Total 3** (425 ms) |
| the boot still refuses what it should | same file, `Boot_refuses_a_revision_or_corpus_the_pricing_was_not_measured_against` | green — the five one-field-at-a-time refusals still fire, now with the rung count read from the tuning |
| the tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | see the report; the two guards this row owns are green |

Not a marker, not an allowlist, not a silenced finding: the const's value now comes from the tuning that owns
it, and the count assertion is the algorithm's contract. `gk-core/data/tuning/` was not touched.
