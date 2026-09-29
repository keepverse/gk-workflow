# CAI4.4 — `lawn-cost-authority` A: one rung derivation (EXTRACTION HALF)

Lane `combat-ai-2`. The row's Files list is fully in-fence, so the extraction landed; the row stays open
on its new test file, which is where the two planted violations live.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Exactly one rung derivation exists | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj`; read of `BattleRunState.cs` | `EffectiveRungResolver.Resolve` holds the body; `BattleRunState.EffectiveRungOf` is a **delegation** with the same inputs and `floorWhenUnknown: 0` (battle's own `?? 0` tail) | `Actions/Unlock/EffectiveRungResolver.cs`, `Battle/BattleRunState.cs:712-717` |
| `floorWhenUnknown: 0` matches today's behaviour — **the goldens are the proof** | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|~ExpeditionResolver\|~Siege\|~Unlock\|~CostLedger\|~ActionSchedule\|~KernelAllocation\|Category=BalanceGuard"` | **511 passed, 0 failed** — no battle golden, expedition, siege or balance-guard number moved, which is this row's own Golden line ("if one moves it is a defect in the extraction, not a re-bless") | — |
| The resolution order is preserved | read of both bodies | steps unchanged and in order: (1) the actor's `UnlockState.Held` entry through `UnlockLadder.EffectiveRung` with the swung row's `RungBand`; (2) the SWUNG row's authored `Rung` (AE1.2's fix, before the catalog); (3) the catalog row's; (4) `floorWhenUnknown` | `EffectiveRungResolver.cs:51-79` |
| The held-row seam is a delegate, not a second view | same read | `heldActionOf` arrives as `Func<string,string,CompiledAction?>` from `BattleRunState.HeldActionOf` — the extractor reads no `IBattleView`, so the lawn can pass its own lookup | `EffectiveRungResolver.cs:38` |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Unlock/EffectiveRungResolver.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14943 passed, 4 failed** — the four pre-existing corpus facts | — |
| Overflow + guards | `python gk-core/scripts/audit-overflow.py --targets A3`; `guard-actor-hub.ps1`; `guard-doc-citations.ps1 -Strict`; `guard-battle-responsibility.py` | audit-overflow **exit 0**; all three guards **exit 0**, doc-citations 0 HIGH | — |

## NOT done — the row's own new test file

`gk-core/tests/FusionRpg.Core.Tests/Actions/EffectiveRungResolverTests.cs` is **not written**, and it is where
three of the row's acceptance lines live:

1. `Resolve_with_floor_zero_matches_the_battle_resolvers_spread_of_cases` over (held / not-held /
   catalog / no-catalog, with and without unlock state) — needs `ActionCatalog`, `UnlockState`,
   `UnlockTuning` and a `CompiledAction` with a `RungBand` fixture; the shapes exist in
   `UnlockLadderTests`/`CostLedgerTests`, but assembling them is the row's next session, not a
   five-minute add at the end of one.
2. `An_unknown_id_with_floor_one_returns_one_and_TryPay_does_not_throw` **and its planted violation** —
   setting the floor to 0 must make it throw `ArgumentOutOfRangeException` (the guard is load-bearing).
3. The second planted violation: reinstating `rungOf: (_, _) => 1` must fail the authored-rung case for
   `r > 1`.

**What IS proven instead, and why it is enough to commit the extraction:** the delegation's fidelity is
the row's own Golden acceptance — a changed rung would move a battle golden, and 511 tests including
every golden, expedition, siege and balance-guard suite did not move. So the extraction is verified
byte-identical; only the new fixture-based unit tests are owed, and they test the resolver's contract
rather than the extraction's fidelity.

## Second slice — the test file, both planted violations, and the row closes

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Resolve` with `floorWhenUnknown: 0` matches the pre-extraction body over the spread | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EffectiveRungResolverTests"` | **5 passed, 0 failed** — `Resolve_with_floor_zero_matches_the_original_body_across_the_spread` transcribes the old body and compares it over SEVEN cases (held+catalog / not-held+catalog / held-no-catalog / held+unlock-state / unlock-state-without-the-id / nothing anywhere / unlock-state-without-tuning). A per-case expected literal would not catch a reordered step; agreement with the transcribed body does | `gk-core/tests/FusionRpg.Core.Tests/Actions/EffectiveRungResolverTests.cs` |
| **Exactly one rung derivation** exists in the repo | `grep -rn "UnlockLadder.EffectiveRung(" src/ --include=*.cs` | **one code call site**: `EffectiveRungResolver.cs:62`. The only other hit is a doc comment in `UnlockState.cs:42` | — |
| Authored rung with no unlock state; `min(earnCount, rungCap, band.Ceiling)` with one | same run | passes — `A_held_action_with_no_unlock_state_prices_at_its_authored_rung` (r = 7 → 7) and `An_unlock_state_prices_at_min_earn_rungcap_and_band_ceiling` (9/10 → 9; 9/3 → 3; 9 with a `RungBand(1,4)` → 4) | — |
| The authoring path beats the catalog | same run | passes — `A_held_row_absent_from_the_catalog_resolves_its_own_rung_not_the_catalogs` (held rung 5, catalog rung 2 → 5; AE1.2's fix) | — |
| `floorWhenUnknown: 1` + `CostLedger.TryPay`, **and its planted violation** | same run | passes — `An_unknown_id_with_floor_one_prices_at_one_and_pays_while_floor_zero_throws`: floor 1 → rung 1 and `CostPayOutcome.Paid`; the SAME payment with floor 0 throws `ArgumentOutOfRangeException` (`RungPolicy.Table` has no rung-0 row), so the floor is load-bearing, not decoration | — |
| The `rungOf: (_, _) => 1` planted violation | same run | passes — `A_held_action_with_no_unlock_state_prices_at_its_authored_rung` asserts the resolver returns 7, that it is **not** 1, and that the old constant really does return 1 — the falsifier is executed, not described | — |
| Golden: nothing moved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|~ExpeditionResolver\|~Siege\|~Unlock\|~CostLedger\|~EffectiveRungResolver\|Category=BalanceGuard"` | **493 passed, 0 failed** | — |
| The row's Verify line | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Unlock/EffectiveRungResolver.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/EffectiveRungResolverTests.cs') -Session combat-ai-20260920"`; `python gk-core/scripts/audit-overflow.py --targets A3` | verify-change **14948 passed, 4 failed** (the four pre-existing corpus facts); audit-overflow **exit 0** | — |
| Guards + citations | `guard-doc-citations.ps1 -Strict`; `guard-actor-hub.ps1` | exit 0, **0 HIGH** | — |

**Drive-by correction, disclosed.** Checking whether the extraction's -8 line shift broke any citation, I
found the six `BattleRunState.cs:924-931` / `:930-931` citations in `spec-aggression-tier-map.md` had been
**stale before this change** — the `ai.aggression` composition is at `BattleRunState.cs:988-996`, ~60 lines
below what they named. They are re-pointed to the real lines in this commit rather than left as
differently-wrong numbers. `guard-doc-citations -Strict` is 0 HIGH.

**Not proved.** The `RungBand` path is exercised through `EffectiveRungResolver` (the 9 + `RungBand(1,4)` →
4 case), but the *unlock-acceptance* path that produces such a held row is `UnlockState.TryAccept`'s, and
its own coverage is `UnlockLadderTests`'/`UnlockStateTests`' — unchanged here, as the row requires.
