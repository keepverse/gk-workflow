# `CAI-find-1` — three flag assertions that described a decision the owner had reversed

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Filed by lane `cai2` and left to the owning program; closed
here because the fix is in this lane's fence and the choice the row named first is not a product decision.

## Which option was taken, and why

The row lists two: *"assert the current owner decision, or re-assert the intended one and flip the constant
with it."* The first is taken, and the evidence is the constant's own comment — which records the reversal
twice:

```csharp
/// <summary>This module's own default — true (owner decision 2026-09-16, after the perf pass
/// L-N1's default-off was conditioned on; see the class note for the numbers) …
public const bool DefaultEnabled = true;
```

So the flag's owner decided on 2026-09-16 and said so where the flag lives; the tests were asserting the
superseded 2026-09-15 ruling in their own doc comments. **Flipping the constant back would have been the
product decision, and it was not taken.** If lawn-combat-wire prefers that option instead, the constant moves
and these three assertions move with it in one commit — the row says which.

## The three corrections, each keeping its test's intent

| Test | Was | Now |
|---|---|---|
| `DefaultEnabled_constant_is_true_by_owner_decision` (renamed) | asserted `False`, doc cited 2026-09-15 | asserts `True`, doc re-dated to 2026-09-16 |
| `Enabled_defaults_on_with_no_explicit_toggle_ever_set` (renamed) | asserted `False` | asserts `True` — the module default, not the schema fallback, still decides |
| `Enabled_ignores_a_stale_backing_field_when_never_explicitly_set` | corrupted the backing field to `true`, asserted `false` | corrupts to `!DefaultEnabled`, asserts the module default wins |

**The third is the one that needed real work rather than a flipped assertion:** corrupting the field to
`true` and reading `true` proves nothing about a default-ON flag, so it now corrupts to the opposite of the
default. A stale `LawnBasicAttackFeature.DefaultOn` reference in that test's doc comment (the constant is
`DefaultEnabled`) was corrected with it.

| Criterion | Command | Result |
|---|---|---|
| The file's five cases | `FUSIONRPG_GAME_DIR=H:/Games/PVZ-Fusion-3.9_BepInEx_Full_Tools dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnBasicAttackFeatureFlagTests" --nologo --verbosity quiet` | **5 passed / 0 failed** |
| The three corrections are load-bearing (planted violation) | same command with `DefaultEnabled` flipped to `false` | **3 failed** — exactly the three corrected cases; reverted green |
| The whole injector project — the merged base's three reds are gone | `FUSIONRPG_GAME_DIR=... dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --nologo --verbosity quiet` | **117 passed / 0 failed** (was 114/3) |
| The injector host still compiles | `FUSIONRPG_ML_GAMEDIR=... FUSIONRPG_GAME_PROFILE=pvzrh-3.9 pwsh -NoProfile -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK` |
| The program's guards | `guard-debug-scope`, `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-dal`, `guard-test-substrate`, `guard-secondary-no-unity` | all **exit 0** |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** |

## NOT proved

- **No live probe.** This is a test-truth correction; the flag's live behaviour was not re-observed.
- **No CI consequence.** `ci.yml` never compiles `FusionRpg.Injector`, which is why the three assertions sat
  red unnoticed — so this commit does not turn any CI line green, it turns a project green for whoever runs
  it locally.
