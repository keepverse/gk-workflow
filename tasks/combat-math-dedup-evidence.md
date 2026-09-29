# Evidence — combat-math-dedup (lane `cmd-1`)

Verification profile: the brief's `-Session cmd-1` is unusable — no `tasks/sessions/cmd-1.json`
exists and creating it is outside this lane's fence — so every `verify-change.ps1` call below uses
`-AllowUnscoped` (the same fallback `tasks/evidence-fragments/tvb6-4.md` records). The owner
boundary is still resolved per path; only the session-scope check is skipped.

## Task 9 — `UiPresentTagValues` derives from `DamageFxTag` (D13)

The removed copy: the eleven lowercased tag literals inside `AtomKindRegistry.UiPresentTagValues`.
The surviving declaration: `FusionRpg.Contracts.DamageFxTag`, read through
`Enum.GetNames<DamageFxTag>()`. No caller had to be left behind — the vocabulary is consumed only by
the `ui.present.tag` `ParamDef`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| no tag literal of its own | `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj -c Release --filter "FullyQualifiedName~UiPresent_tag_vocabulary_declares_no_literal_of_its_own"` | 1/1 pass | `UiPresentTests.cs:203` |
| the same guard bites | planted `"neutral"` in the declaration, re-ran the filter | 1 failed (message quoted the literal); reverted | — |
| 11-member set is `DamageFxTag`'s names | `--filter "FullyQualifiedName~UiPresent_tag_vocabulary_is_exactly_the_DamageFxTag_names_lowercased"` | 1/1 pass | `UiPresentTests.cs:182` |
| `ui.present` behaviour unchanged | `--filter "FullyQualifiedName~UiPresentTests"` | 48/48 pass | — |
| path-owned verification | `verify-change.ps1 -Paths @(...) -AllowUnscoped` | exit 0; Core.Tests 9541/0, Atoms.Tests 1355/0 | — |

## Task 10 — area shapes declared once (D14)

The removed copies: the four lowercase literals in `ActionAreaShapes.Name`/`TryParse`, and the
`ActionAreaShape` → `AreaShapes` switch in `TargetSpecCompiler.ToWireShape`. The surviving
declaration: `ActionAreaShape`'s member names, whose equality with `FusionRpg.Contracts.AreaShapes`'s
consts is asserted by the guard. No caller was left behind.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| enum names == `AreaShapes` consts | `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --filter "FullyQualifiedName~ActionTargetingTests"` | 17/17 pass | `ActionTargetingTests.cs` |
| no shape literal of its own | same filter, `ActionAreaShapes_declares_no_shape_literal_of_its_own` | pass | same |
| the guard bites | planted `"row"` in `Name`, re-ran the filter | 1 failed; reverted | — |
| lowercase-only parse preserved | `ActionAreaShapes_TryParse_still_refuses_a_wrong_case_and_an_unknown_name` | pass | same |
| path-owned verification | `verify-change.ps1 -Paths @(...) -AllowUnscoped` | exit 0; Core.Tests 9541/0 | — |

## Task 11 — the ten rung ids declared once (D15)

The removed copies: `RarityLadder.RungIds`' ten-literal array, `RarityLadder.IsPityGuarded`'s
`"heirloom"`/`"sunwoven"`, and `RarityDraw.HeirloomId`/`SunwovenId`'s const pair. The surviving
declaration: `CreatureRarityIds.ToId` over `CreatureRarityLadder.All`. Callers left behind: none.
`RarityDraw.HeirloomId`/`SunwovenId` became `static readonly` (was `const`) — the only source change;
no `case`/attribute/optional-default consumer exists.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| item ladder == creature ladder ids | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests/FusionRpg.Core.Items.Tests.csproj -c Release --filter "FullyQualifiedName~ItemRarityLadderTests\|FullyQualifiedName~DropVolumeTests\|FullyQualifiedName~RarityLadderSeedAgreement\|FullyQualifiedName~Rarity"` | 108/108 pass | `ItemRarityLadderTests.cs` |
| no rung literal in the two files | same filter, `The_item_rarity_files_declare_no_rung_id_literal_of_their_own` | pass | same |
| the guard bites | planted `"heirloom"` in `IsPityGuarded`, re-ran the filter | 1 failed; reverted | — |
| seed agreement still holds | `RarityLadderSeedAgreementTests` (in the 108) | pass | — |
| path-owned verification | `verify-change.ps1 -Paths @(...) -AllowUnscoped` | exit 0; Items.Tests 1411/0 | — |

Blocked follow-up: `gk-core/tests/FusionRpg.Guard.Tests/LadderRestatementGuardTests.cs` still allowlists
`RarityLadder.cs`; the file is hook-protected so the now-obsolete allowlist could not be removed.
The new source scan above covers that file, so no coverage is lost.

## Task 12 — the 28 combat channel families listed once (D16)

The removed copy: the two 13/15-element arrays in `AuthoredCategoryOverrides` that re-listed all 28
families. The surviving declaration: `DerivedStatChannels.CombatChannelFamilies` (the family list)
plus `CombatFamilyRole` (the 16 role-carrying families). Survivability is the complement over the
family list, so the two sides are disjoint by construction. No caller was left behind.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| two sides partition the family list | `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj -c Release --filter "FullyQualifiedName~CoefficientTableCategoryOverrideTests"` | 3/3 pass | `CoefficientTableCategoryOverrideTests.cs` |
| role-carrying families on their side | same filter, `Every_role_carrying_family_lands_on_the_side_its_role_names` | pass | same |
| the guard bites | planted `combat.dodge` into the offense set, re-ran the filter | 1 failed (classification test); reverted | — |
| power pricing unchanged | `--filter "FullyQualifiedName~Power"` on the same project | 116/116 pass | — |
| import parity unchanged | `dotnet test gk-core/tests/FusionRpg.Data.Tests/... --filter "FullyQualifiedName~PowerCoefficientImport"` | 8/8 pass | — |
| whole Atoms project after the test edit | `dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/...` | 1356/0 | — |
| path-owned verification (production code) | `verify-change.ps1 -Paths @(...) -AllowUnscoped` | exit 0; Atoms 1355/0 at that revision | — |

## Task 13 — `DerivedStatSurfaceCatalog` references, does not re-literalise (D19)

The removed copies: `StatusCategoryIds`' three L2b literals, `ElementLeafIds`' six element literals,
`ActionCategoryFamilyIds`' two action-family literals, and the inline
`prefix == "skill.cooldown" || prefix == "skill.effectiveness"` comparison. The surviving
declarations: `StatusL2bCategory`, `ElementRoster`, `DerivedStatChannels.SkillCooldownPrefix` /
`SkillEffectivenessPrefix`. `omni` stays an explicit, commented addition in each set (the surface's
own non-specific variant). No caller was left behind.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| sets == the referenced constants | `dotnet test gk-core/tests/FusionRpg.Core.ActorSurface.Tests/FusionRpg.Core.ActorSurface.Tests.csproj -c Release --filter "FullyQualifiedName~DerivedStatSurfaceVocabularyTests"` | pass (reflection set-equality) | `DerivedStatSurfaceVocabularyTests.cs` |
| no re-literalised vocabulary | same filter, `The_surface_catalog_declares_no_reliteralised_vocabulary_of_its_own` | pass | same |
| the guard bites | planted `"dot"` into `StatusCategoryIds`, re-ran the filter | 1 failed; reverted | — |
| loader rejections unchanged | same project, `FullyQualifiedName~DerivedStatSurfaceCatalogRejectionTests` | pass (16/16 together) | — |
| path-owned verification | `verify-change.ps1 -Paths @(...) -AllowUnscoped` | exit 0; ActorSurface 33/0 | — |

## Task 17 — sigmoid display read (D11, D12) — PARTIAL (C# half only)

The defect: `ItemDisplayRenderer.FormatSigmoidContext` returned `deltaPoints / scale` pp — not a
sigmoid. `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:153` is the correct read
(`(sigmoid(delta/scale) − sigmoid(0)) × 100`), which reproduces `docs/design/spec-magnitude-and-units.md`
§4.1's `p = 1/(1 + e^(−delta/100))` and §14 D.1's card row (`+150 crit rate` → `≈ +31.8 pp`). The C#
helper now computes that same shift; its only caller is the test below (the read has no production C#
caller today, which is itself the open wire).

Remaining on T17 (out of this lane's fence, `gk-web/web/fusion-rpg-web/**`): the cross-language parity
fixture, the `SIGMOID_STEEPNESS` / `CombatProbabilityScale` check against `gk-core/data/tuning/stats.v1.json`,
and the `web/**` verification boundary. Row left open.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| pp fixture matches the spec's worked example | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests/... --filter "FullyQualifiedName~FormatSigmoidContext"` | 4/4 pass (`0→0.0`, `30→7.4`, `150→31.8`, `-150→-31.8`) | `ItemDisplayTests.cs` |
| no display regression | `--filter "FullyQualifiedName~ItemDisplayTests"` | 35/35 pass | — |
| path-owned verification | `verify-change.ps1 -Paths @(...) -AllowUnscoped` | exit 0; 67 green project runs, 0 failed; Items 1415/0 | — |

## Task 4 — G7 becomes a real guard (D3) — guard landed, committed falsifier BLOCKED

The duplicate: `PhaseModel.ReflectRateAndShare`'s inline `Math.Clamp(Math.Max(0.0, …)/…Scale, 0.0, 1.0)`
(the second copy `PhaseModel`'s own comment used to admit). The surviving declaration:
`ElementalResolver.RateFromZero`, called by both `CombatDamageDispatcher.TryReflect` and
`PhaseModel.ReflectRateAndShare` (extraction landed earlier by solid-remediation T2.7 — verified against
code in this session, not against the pointer). This task's own deliverable was the guard.

The old G7 was a **positive-presence** check over `Balance/Analytic/{StrikeMixture,PhaseModel}.cs`: a
file passed if it mentioned any shipped symbol anywhere — which is exactly how a hand-copied formula
survived. Rewritten in `gk-core/scripts/guard-class-system.py` as a positive **and negative** pair:

- positive (kept — removing it would weaken coverage: a file could re-derive via a locally-defined
  helper and reference no symbol at all);
- negative (new, explicit file list): flag `Math.Exp(`, a bare `1/(1+…)`, and the
  `Math.Clamp(Math.Max(` clamp-and-scale shape in `StrikeMixture.cs`, `PhaseModel.cs`,
  `ActionSchedule.cs`, `Battle/Siege/SiegeExpectedDamage.cs`, `Battle/Siege/SiegeHitChance.cs`.
  The list is explicit, not a glob: `Race.cs` legitimately uses `Math.Exp`/`1.0/(1.0+…)` for the A&S
  normal CDF and `Predictor.cs` legitimately clamps a correlation to [−1,1].

Wiring: no registry/runner change needed — `class-system` is already `tier: ci`, `status: gating` in
`gk-core/scripts/enforcement-registry.v1.json`, invoked through `scripts/run-guards.ps1`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| real tree still green | `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK` | `gk-core/scripts/guard-class-system.py` |
| existing guard tests still green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~ClassSystemGuardTests"` | 16/16 pass (with System32 on PATH; see below) | `ClassSystemGuardTests.cs` |
| G7 bites — planted clamp-and-scale | `guard-class-system.py -Root <synthetic fixture>` with the shape in `PhaseModel.cs` and `SiegeExpectedDamage.cs` | exit 1, one G7 line per file naming `ElementalResolver.RateFromZero` | evidence below |
| G7 bites — planted sigmoid literal | same, `1.0 / (1.0 + Math.Exp(-d))` | exit 1, two G7 lines (`Math.Exp`, bare `1/(1+)`) | evidence below |
| G7 no false positive | same, `(int)Math.Clamp(Math.Round(p * 1000.0), 0.0, 1000.0)` | exit 0 `GUARD OK` | evidence below |

Raw planted-violation output (fixture roots under `%TEMP%`):

```
CLASS-SYSTEM GUARD FAILED:
  G7 ...\Balance\Analytic\PhaseModel.cs:3 re-derives the linear clamp-and-scale rate shape (ElementalResolver.RateFromZero) — call the shipped owner (ElementalResolver / CombatProbability) instead
  G7 ...\Battle\Siege\SiegeExpectedDamage.cs:2 re-derives the linear clamp-and-scale rate shape (ElementalResolver.RateFromZero) — call the shipped owner (ElementalResolver / CombatProbability) instead
exit=1
```

⛔ **Blocker (erratum needed).** The committed falsifier belongs in
`gk-core/tests/FusionRpg.Guard.Tests/ClassSystemGuardTests.cs` (next to the existing `G7_fails_*` cases). The
orchestrator pipeline hook refuses every edit to `gk-core/tests/FusionRpg.Guard.Tests/**` ("protected pipeline
file"), so the case could not be committed. The exact case to add: a fixture `PhaseModel.cs` that
*does* call `CombatProbability.Sigmoid` (so the positive half passes) **and** writes
`Math.Clamp(Math.Max(0.0, a - b) / s, 0.0, 1.0)`, asserting `exit == 1` and `stdout` contains
`"G7 "`, `"PhaseModel.cs"`, `"RateFromZero"`. A second case should cover a widened Siege file. The
guard behaviour itself is proven above; only the committed regression case is missing.

## Post-merge verification (after `features/mega-merge` @ 0ad112952)

Merged clean (`94050e2f1`, no conflicts). Re-ran the path-owned command over every file this lane
changed, plus the new `class-system-guard` boundary:

| Check | Printed reading |
|---|---|
| `verify-change.ps1 -Paths @(<all 17>) -AllowUnscoped` | 72 project runs, **0 `Failed!` lines**; `FusionRpg.Core.Tests` 9582/0, `Core.Items.Tests` 1468/0, `Core.Atoms.Tests` 1356/0, `Core.ActorSurface.Tests` 33/0, `Core.Balance.Tests` 301/0, `Core.ClassSystem.Tests` 238/0 |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "VerificationId=guard.doc-boundary"` | Passed! Failed: 0, Passed: 4, Total: 4 |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "VerificationId=guard.verification-boundaries"` | Passed! Failed: 0, Passed: 57, Total: 57 |
| `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK` |
| `gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` (437 boundaries) |

The first pass of the full command was interrupted by the environment twice mid-`Guard.Tests`; the
readings above are the completed runs.

### Cross-lane findings on the merged head (NOT this lane's changes)

`git diff --name-only 0ad112952..HEAD` shows this lane changed only
`docs/architecture/combat-ai/spec-resolvable-here.md`, `gk-core/scripts/verification-boundaries.v1.json`,
`tasks/combat-math-dedup-{evidence,todo}.md` and the ledger. Three `FusionRpg.Guard.Tests` cases are
red on the merged head and read files this lane never touched:

| Failing test | Cause (read from the code) |
|---|---|
| `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (`PlantSideStatusGuardTests.cs:115`) | It pins `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` at SHA-256 `02B04A25…`; the merged file hashes `E1444DB1…`. `5e33ad647 fix(battle): T6 (W11) one gate owns combat.defense.omni` changed the file without re-pinning. Owner: the battle/combat-ai program (the test's own comment names `tasks/combat-ai-todo.md`). |
| `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` (`…:121`) | The guard pins a nine-code closed set; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:305` now returns a tenth, `picks.source-below-rank-floor`. Owner: the picks/player-species program. |
| `PlayerSpeciesMaterialiseCallerGuardTests.The_status_clock_costs_no_round_trip_on_the_injector_hot_path` (`…:148`) | It asserts `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs` contains `new(DateTimeOffset.UtcNow)`; the merged file does not. Owner: the injector status-clock lane. |

Fixes for all three live in the hook-protected `gk-core/tests/FusionRpg.Guard.Tests/**`, outside this lane.

## Task 3 — siege kill estimate uses the shipped defense shape (D4) — guard completed

The estimator half was built by `solid-remediation` T4.11/T4.12 and verified against code this
session: `Battle/Siege/SiegeExpectedDamage.cs` calls
`OverlayCombatCalculator.DivisiveMitigation` under `DefenseShape.Divisive` and keeps the subtractive
branch only as the configured alternative; the false "identical to the resolver" header comment is
gone; `IsKillingBlow` takes a base-damage argument. The one acceptance line still open was G7's
coverage, now landed.

The removed copy: none new — this task's own gap was that `guard-class-system.py`'s G7 positive half
scanned only `Balance/Analytic`, so a siege estimator that stopped calling the shipped resolver was
unwatched. `$DamageComputingFiles` is now explicit full paths across both trees
(`StrikeMixture.cs`, `PhaseModel.cs`, `Battle/Siege/SiegeExpectedDamage.cs`,
`Battle/Siege/SiegeHitChance.cs`).

| Criterion | Command | Result |
|---|---|---|
| siege suite | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Siege"` | Passed! Failed: 0, Passed: 333, Total: 333 |
| guard tests unchanged | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~ClassSystemGuardTests"` | Passed! Failed: 0, Passed: 16, Total: 16 |
| guard green on the real tree | `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK` |
| path-owned verification | `verify-change.ps1 -Paths @('gk-core/scripts/guard-class-system.py') -AllowUnscoped` | `CLASS-SYSTEM GUARD OK` (class-system-guard, module) |
| the new coverage bites | synthetic `-Root` fixture with `SiegeExpectedDamage.cs` calling no shipped symbol | exit 1, `G7 …SiegeExpectedDamage.cs: no reference to a shipped combat symbol found` |

Before/after on one fixed triple is recorded in the task body.

## Task 2 — one element-enum → element-id switch (D2) — consumer tests + guard completed

The dedup was built by `solid-remediation` T5.2 and verified against code this session:
`ElementTable.IdOf` is `=> id.ToElementId();`, and `ToElementId`'s throwing default is intact. The
two acceptance lines still open were the consumer tests and the source-scan guard, both landed here.

The removed copy: none new — `IdOf` was already the alias. The guard is the new negative half: only
`ActorElementTypes.cs` may map `ElementTypeId` to an element-id string.

| Criterion | Command | Result |
|---|---|---|
| six members agree, unknown throws | `dotnet test gk-core/tests/FusionRpg.Core.Vocabulary.Tests -c Release --filter "FullyQualifiedName~SingleDeclarationTests"` | Passed! Failed: 0, Passed: 8, Total: 8 |
| the three former call sites throw | same suite, `An_unknown_element_throws_at_each_of_the_three_former_IdOf_call_sites` | pass (`ElementRingMatrix` both arms, `ShieldElementMatrix`, `ActorHudShieldStacks.AggregateByElement`) |
| the source-scan guard bites | planted `ElementTypeId.Fire => "fire"` in `Combat/Element/ElementTable.cs`, re-ran the filter | Failed! 1 failed; reverted (`git diff` empty) |
| no shipped behaviour change | all six enum members covered, so `IdOf` returns the same ids; only the out-of-range arm moved `""` → throw | stated in the task body |

## Task 1 — status id → L2b category declared once (D1) — closed in the landed direction

`solid-remediation` T5.1 made the **registry** the owner and the bootstrap read
`GetRequiredCategory`; verified against code this session. T1's AC-1/AC-2 and its proposed guard
describe the reverse direction and cannot pass without reverting T5.1 and its test — flagged as an
erratum in the task body and closed against the existing pointer's ruling (code beats docs).

The residual removed here: `StatusCatalogBootstrap.RegisterWithOptions` still took `primaryCategory`,
and `leech` was the only call site passing `StatusL2bCategory.Dot` explicitly. It now reads
`GetRequiredCategory` like the other helper, so the bootstrap names no `StatusL2bCategory` value.

| Criterion | Command | Result |
|---|---|---|
| guard + set pin + consumers | `dotnet test gk-core/tests/FusionRpg.Core.Vocabulary.Tests -c Release --filter "FullyQualifiedName~SingleDeclarationTests"` | Passed! Failed: 0, Passed: 10, Total: 10 |
| the new guard bites | planted `_ = StatusL2bCategory.Dot;` in `StatusCatalogBootstrap.cs`, re-ran the filter | Failed! 1 failed; reverted |
| `Register` / additive ids unchanged | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~ExhaustionPolicyTests\|FullyQualifiedName~DefenceActionStanceTests\|FullyQualifiedName~ExhaustionEdgeTests"` | Passed! Failed: 0, Passed: 28, Total: 28 |
| no golden moves | `dotnet test gk-core/tests/FusionRpg.Core.Status.Tests -c Release` | Passed! Failed: 0, Passed: 170, Total: 170 |
| path-owned verification | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Status/StatusCatalogBootstrap.cs','gk-core/tests/FusionRpg.Core.Vocabulary.Tests/Vocabulary/SingleDeclarationTests.cs') -AllowUnscoped` | 0 `Failed!` lines; Vocabulary 10/0 |

## Task 6 — CombatSim's per-swing mixture calls `StrikeMixture` (D5) — partial: guard added, row open

The call-through was built by `solid-remediation` T4.13 and verified against code this session:
`gk-core/tools/CombatSim/Analytic.cs:141-171` (`Strike`) calls
`FusionRpg.Core.Balance.Analytic.StrikeMixture.Compute` and maps the atoms to `StrikeStats`; the
forbidden per-swing symbols appear nowhere in that method. The guard AC was still open, and is
landed here in the guard itself (its proposed home is hook-protected).

| Criterion | Command | Result |
|---|---|---|
| `Strike` calls only the owner | `sed -n '141,171p' gk-core/tools/CombatSim/Analytic.cs`; `grep -nE "CombatProbability\.Sigmoid\|CapAvoidanceBand\|PierceFactor\|DivisiveMitigation\|AmpFactor\|ClampedContest\.Apply"` | the method body calls `StrikeMixture.Compute` only; the `ClampedContest.Apply` hits are `:234`/`:615`, other methods |
| guard green | `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK` |
| the new check bites | synthetic `-Root` fixture with `gk-core/tools/CombatSim/Analytic.cs` lacking `StrikeMixture.Compute` | exit 1, `G7 …Analytic.cs: CombatSim's per-swing Strike must call StrikeMixture.Compute` |
| guard tests unchanged | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~ClassSystemGuardTests"` | Passed! Failed: 0, Passed: 16, Total: 16 |
| path-owned verification | `verify-change.ps1 -Paths @('gk-core/scripts/guard-class-system.py') -AllowUnscoped` | `CLASS-SYSTEM GUARD OK` |

Still open on T6: the baseline-regen check and `ProvePredictor` residuals, both requiring
`gk-core/tools/CombatSim` / the baseline artifacts, outside this lane's allowed paths.

## Task 4 — G7 negative guard (D3) — CLOSED: the committed falsifier was in the register all along

Correction to the section above. The earlier note said T4's committed falsifier was blocked because it
had to go in the hook-protected `ClassSystemGuardTests`. It was not blocked: the same rule is already a
`shape: "banned"` decision in the **battle-responsibility register**, which is the stronger mechanism
and whose falsifiers are already committed.

| Criterion | Command | Result |
|---|---|---|
| the register enforces D3 | `gk-core/scripts/guard-battle-responsibility.py` | `BATTLE RESPONSIBILITY GUARD OK (19 mechanisms, 1683 files scanned)` — mechanism 18 `reflect-scale-inline`, `shape: "banned"`, only the POC allowlisted |
| the banned-shape falsifier is committed | `gk-core/tests/FusionRpg.Guard.Tests/BattleResponsibilityGuardTests.cs:274,304` | `A_banned_shape_fails_even_in_the_registered_owner_file`, `A_banned_shape_passes_when_nobody_writes_it` — its own doc names `ElementalResolver.RateFromZero` as the extraction that motivated it |
| both callers use the one shape | `grep -rn RateFromZero src/` | `CombatDamageDispatcher.cs:131,134` and `PhaseModel.cs:160,165`; no inline `/…ReflectScale` in Core (the register would fail) |
| reflect behaviour | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests -c Release --filter "FullyQualifiedName~PhaseModelTests"` | Passed! Failed: 0, Passed: 34, Total: 34 |
| rate shape + reflection chain | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~ElementalResolverTests|FullyQualifiedName~ReflectionTests"` | Passed! Failed: 0, Passed: 36, Total: 36 |
| G7 negative half | `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK` |

## Remaining program work — every open acceptance line is under `gk-core/tools/CombatSim/**`

After T1–T4 closed and T5/T6 advanced as far as this lane's allowed paths permit, the 16 still-open
checkbox lines are all in four rows, and every one of them needs a path outside the fence:

| Row | Open lines | Needs |
|---|---|---|
| T5 (D7, Phi/Erf) | 4 (AC-3/4/5 + guard) | `gk-core/tools/CombatSim/Analytic.cs` + `gk-core/tools/CombatSim/CombatSim.csproj`; the guard's one-literal check cannot pass while that copy exists |
| T6 (D5) | 2 (baseline regen, ProvePredictor) | `gk-core/tools/CombatSim` + the baseline artifacts |
| T7 (D8) | 4 (AC-1/2/3 + guard) | `gk-core/tools/CombatSim/StatusModel.cs` |
| T8 (D6/D9) | 6 (AC-1–5 + guard) | `gk-core/tools/CombatSim/ActionEconomy.cs` for the call-through, and the baseline artifacts for the before/after the AC demands; the Core copy is in fence but a per-mille `long` rewrite that moves `Predictor`'s predicted numbers cannot be measured here |

T14/T16/T17 have no checkbox lines (their ACs are prose); their remaining work is
`gk-core/src/FusionRpg.Contracts/**` / `gk-fusion/src/FusionRpg.Injector/**` / `gk-web/web/fusion-rpg-web/**` respectively.

Re-checked on the merged head `b744f0bb6` (`features/mega-merge` @ 62ca07758): every copy the four
rows name is still present — `gk-core/tools/CombatSim/Analytic.cs:628,633` (Phi + the A&S coefficient),
`gk-core/tools/CombatSim/StatusModel.cs:146,163`, `ActionSchedule.cs:146`, `DebugEndpoints.cs:404` +
`ControlInspect.cs:249`, the two `Injector/Hud` folds, and the web `SIGMOID_STEEPNESS`. No other lane
has taken them. Moving any of these needs this lane's allowed paths widened to include
`gk-core/tools/CombatSim/**`, `gk-core/src/FusionRpg.Contracts/**`, `gk-fusion/src/FusionRpg.Injector/**` or
`gk-web/web/fusion-rpg-web/**`.

## Task 5 — one Phi, and CombatSim's boundary (D7) — CLOSED under the manager's tools grant

The removed copy: `gk-core/tools/CombatSim/Analytic.cs`'s own `Phi` (and its six A&S 7.1.26 constants). The
surviving declaration: `Race.Phi`/`Race.Erf` (`gk-core/src/FusionRpg.Core/Balance/Analytic/Race.cs`), which
already guarded NaN and ±∞ where the copy did not. The three call sites (`Analytic.cs:441,458,459`)
now call `Race.Phi`; the coefficient literal appears in exactly one file.

| Criterion | Command | Result |
|---|---|---|
| boundary present | `verify-change.ps1 -Paths @('gk-core/tools/CombatSim/Analytic.cs','gk-core/tools/ProvePredictor/Program.cs') -AllowUnscoped -PlanOnly` | `tools-combat-sim (focused)`, `tools-prove-predictor (focused)` |
| Phi deleted, callers migrated | `grep -n "Phi(" gk-core/tools/CombatSim/Analytic.cs` | no member definition; `Race.Phi` at 441,458,459 |
| residuals unchanged | `dotnet run --project gk-core/tools/ProvePredictor -c Release --no-build` | `MAX ABS DIFF in WinShareA` = **8.836E-007** actions-only and actions+status (same as T6's record); all PASS |
| one-literal guard | `dotnet test gk-core/tests/FusionRpg.Core.Vocabulary.Tests -c Release --filter "FullyQualifiedName~SingleDeclarationTests"` | Passed! Failed: 0, Passed: 11, Total: 11 |
| the guard bites | planted `0.254829592` in `gk-core/tools/CombatSim/Analytic.cs`, re-ran the filter | Failed! 1 failed; reverted |
| path-owned verification | `verify-change.ps1 -Paths @('gk-core/tools/CombatSim/Analytic.cs','gk-core/tools/CombatSim/CombatSim.csproj','gk-core/tests/FusionRpg.Core.Vocabulary.Tests/Vocabulary/SingleDeclarationTests.cs') -AllowUnscoped` | exit 0; Balance 2/0, ClassSystem 3/0, Vocabulary 11/0 |

`CombatSim.csproj`'s comment now names the Core shapes actually called and the two walks still to
migrate (T7/T8).

## Task 6 — CombatSim's per-swing mixture calls `StrikeMixture` (D5) — CLOSED

The duplicate: `tools/CombatSim/Analytic.Strike` was a fourth copy of the omni swing assembly. The
surviving owner: `Balance/Analytic/StrikeMixture.Compute` (bound to the real resolver by three CI
parity tests). Verified against code, and the guard landed earlier; the two verification lines were
run here.

| Criterion | Command | Result |
|---|---|---|
| call-through | `sed -n '141,171p' gk-core/tools/CombatSim/Analytic.cs` | `Strike` calls only `StrikeMixture.Compute`; no forbidden per-swing symbol in the method |
| baselines unchanged | `pwsh scripts/regen-class-system-baselines.ps1 -OutDir <temp> -Configuration Release` then JSON compare vs `docs/research/class-system/_baseline-*.json` (stripping `_meta`) | `_baseline-residual`: IDENTICAL; `_baseline-dominance`: IDENTICAL; `_baseline-goldens`: IDENTICAL |
| residuals unchanged | `dotnet run --project gk-core/tools/ProvePredictor -c Release --no-build` | `MAX ABS DIFF in WinShareA` = **8.836E-007** actions-only and actions+status; both PASS |
| guard | `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK`; a planted `Analytic.cs` lacking `StrikeMixture.Compute` exits 1 |

## Task 7 — CombatSim's status model calls `StatusUptime` (D8) — CLOSED

The removed copy: `StatusMath`'s own `Expected`, `ExpectedDotPerRound`, `CcDisabledShare` and the
`Uptime(double, double)` (`1 − (1−p)^duration`). The surviving declaration:
`Balance/Analytic/StatusUptime.cs`. `StatusMath` now only adapts `Archetype` →
`CombatActorSnapshot` and delegates; `FixedRng` became dead and was removed, `SeededRng` stays for
`Roll`'s real draw.

| Criterion | Command | Result |
|---|---|---|
| uptime formula once | `grep -n "Math.Pow" gk-core/tools/CombatSim/StatusModel.cs` | no match |
| residuals unchanged (post) | `dotnet run --project gk-core/tools/ProvePredictor -c Release --no-build` | 2.827E-007 / 3.495E-006 / 8.836E-007 / 8.836E-007 |
| residuals unchanged (pre, controlled) | same command with `HEAD:gk-core/tools/CombatSim/StatusModel.cs` restored, then the file re-applied | identical four readings |
| guard green | `gk-core/scripts/guard-class-system.py` | `CLASS-SYSTEM GUARD OK` |
| the guard bites | fixture `StatusModel.cs` = `1.0 - Math.Pow(1.0 - p, d)` | exit 1, both messages (`must call StatusUptime` and `contains an uptime formula of its own`) |
| guard tests unchanged | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~ClassSystemGuardTests"` | Passed! Failed: 0, Passed: 16, Total: 16 |
| path-owned verification | `verify-change.ps1 -Paths @('gk-core/tools/CombatSim/StatusModel.cs','gk-core/scripts/guard-class-system.py') -AllowUnscoped` | guard OK; Balance 2/0; ClassSystem 3/0 |

## Task 8 — pool regen has one implementation (D6, D9) — CLOSED

The removed copies: `ActionSchedule`'s local `Math.Clamp(p.Value + p.Regen, 0, p.Max)` advance, and
`ActionEconomy`'s own `ActorPools.Tick` clamp plus `ActionPolicy.Choose` walk. The surviving
declarations: `Actions/Cost/ResourcePoolState.Settle` (reached through `ActionSchedule.Advance`) and
`ActionSchedule.Choose` (called by `ActionPolicy.Choose`). `PoolState` gained a `long CarryMilli`
(default 0, so every existing constructor still compiles).

| Criterion | Command | Result |
|---|---|---|
| advance goes through the gate | `grep -n "ResourcePoolState" gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs`; `gk-core/scripts/guard-class-system.py` | `Advance` calls `Settle`; `CLASS-SYSTEM GUARD OK` |
| call-through, not mirror | `grep -n "ActionSchedule\." gk-core/tools/CombatSim/ActionEconomy.cs` | `ActionSchedule.Advance` in `Tick`, `ActionSchedule.Choose` in `ActionPolicy.Choose` |
| no residual/baseline movement | `dotnet run --project gk-core/tools/ProvePredictor -c Release --no-build` | 2.827E-007 / 3.495E-006 / **8.836E-007** / **8.836E-007** — identical to before T8 |
| baselines reproduce | `pwsh scripts/regen-class-system-baselines.ps1 -OutDir <temp> -Configuration Release` + JSON compare (strip `_meta`) | residual IDENTICAL, dominance IDENTICAL, goldens IDENTICAL |
| guard bites | fixture with `ActionSchedule.cs` lacking `ResourcePoolState`; fixture with `ActionEconomy.cs` lacking `ActionSchedule.Choose/Advance` | each exits 1 with its G7 line |
| guard tests unchanged | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~ClassSystemGuardTests"` | Passed! Failed: 0, Passed: 16, Total: 16 |
| analytic suite | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests -c Release` | Passed! Failed: 0, Passed: 210, Total: 210 |
| analytic heads | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Dominance\|FullyQualifiedName~Termination\|FullyQualifiedName~Predictor\|FullyQualifiedName~ResidualFitLoop"` | Passed! Failed: 0, Passed: 5, Total: 5 |

Before/after on the synthetic sub-unit case (recorded in the task body): `(0, 10, 0.6)` over 3 rounds
— 1.8 (old continuous clamp) vs 1.0 (gate, per-mille 600 + carry).

### Pre-existing red on the merged head (NOT this lane)

`verify-change.ps1` stops at the first failing check, and `FusionRpg.Core.Expeditions.Tests` is red:
**11 failed / 27 passed / 38 total**, `System.InvalidOperationException: Sequence contains no
elements` at `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:186` (`PlannedRungFor` calls
`.Max()` on an empty wave), reached from `Resolve` at `:101`. Reproduced with `HEAD:` versions of this
lane's two changed files written back, so it is inherited, not introduced here. `balance` and
`class-system` (this task's own `core.combat-sim` boundary) are green.

## Checkpoints 3 and 4 — ticked

Re-run on the merged head (`55de2a358`). Everything an in-fence check can settle is green; the two
document rows in each checkpoint are blocked by the docs fence.

| Check | Printed reading |
|---|---|
| boundary guards (Checkpoint 4) | `ACTOR-HUB GUARD OK`; `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data`; `SECONDARY NO-UNITY GUARD OK` |
| Phase 4 task path sets | `Core.Atoms.Tests` 1356/0 (four runs; one transient failure on the first, not reproduced — see below); `Core.Items.Tests` 1469/0; `Core.ActorSurface.Tests` 33/0; `Core.Vocabulary.Tests` 11/0; `Core.Status.Tests` 170/0; `ActionTargetingTests` 17/0 |
| no golden moved | the three class-system baselines regenerate IDENTICAL; `Core.Balance.Tests` 210/0 |
| Phase 3 residuals + baselines | `ProvePredictor` 2.827E-007 / 3.495E-006 / 8.836E-007 / 8.836E-007; baselines IDENTICAL (×2) |
| boundary resolves | `verify-change -PlanOnly` prints `tools-combat-sim (focused)` and `tools-prove-predictor (focused)` |

Blocked (not green, not defeatable inside this fence): Checkpoint 3's
`spec-deterministic-core.md` line (`docs/architecture/class-system/**`) and both checkpoints' audit
§2 row ( `docs/research/combat-math-dedup-audit-2026-09-16.md` ). The actual remaining gap the doc row
asks to name: after T5–T8 the only CombatSim-local logic left is the JSON/`Archetype` adapter layer.

Transient: the first `Core.Atoms.Tests` run in this session reported 1 failure; four consecutive
re-runs are 1356/0 and it did not reproduce. Recorded rather than silently dropped — an
intermittently-green suite is its own defect class, and it is not attributable to a declaration move.

## Checkpoint 5 — guards green; the full-suite item attempted and not completed

All eight boundary guards, re-run on the merged head:

```
guard-single-writer            SINGLE-WRITER GUARD OK
guard-secondary-no-unity       SECONDARY NO-UNITY GUARD OK — plugins Grant/Withdraw only
guard-funnel-delta             FUNNEL DELTA GUARD OK — Secondary enqueue via Funnel only
guard-actor-hub                ACTOR-HUB GUARD OK
guard-dal                      DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data
guard-test-substrate           TEST SUBSTRATE GUARD OK
guard-class-system             CLASS-SYSTEM GUARD OK
guard-verification-boundaries  VERIFICATION BOUNDARY GUARD OK
```

`test-fast.ps1 -AllDefault` was attempted twice; both runs were killed by environment errors before
completing (~48 KB of log each). The partial log shows
`FusionRpg.E2E.Tests.ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto` failing at
`ContractFixtureTests.cs:76` (a JSON fixture vs live-DTO mismatch). This program touched no DTO, so
that is another stream's drift — and it means the full suite would not have been green even if the run
had survived. Not completed, not retried a third time (the host cannot currently hold a 9-minute run).
`npm run build` / `npm test` remain blocked: `gk-web/web/fusion-rpg-web/**` is outside the fence.

### Checkpoint 5 full suite — completed as five `-Project` batches

A single `-AllDefault` run was cut off twice by the host, so the whole `$DefaultProjects` list was run
in five shorter calls. Every project was covered:

| Batch | Printed reading |
|---|---|
| Data / Server / E2E | `Data.Tests` **1777/0**; `Server.Tests` **856/0**; `E2E.Tests` **273 passed / 3 failed / 276** |
| Core A–E (27 projects) | all `Failed: 0` |
| Core E–S (26 projects) | 25 projects `Failed: 0`; `Core.Expeditions.Tests` **27 passed / 11 failed / 38** |
| Core S–W (14 projects) | all `Failed: 0` |
| `Core.Tests` | **9723/0** |

The 14 reds, none this program's:
- `FusionRpg.E2E.Tests` — `ContractFixtureTests.Commander_list_fixture_matches_live_dto`,
  `ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto` (`ContractFixtureTests.cs:76`),
  `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening` — checked-in
  JSON fixtures vs the live DTO (`displayName`, `playerId`/`empireId`, `stateHash` all differ).
- `FusionRpg.Core.Expeditions.Tests` — the `ExpeditionResolver.cs:186` empty-wave `.Max()` crash
  recorded in the T8 evidence.

This program changed no DTO, endpoint, SQL or expedition input, so none of the 14 is attributable to it.

## T5-T8 re-verified on the merged head (3ed6ef3c0)

`features/mega-merge` merged clean; all four rows' changes are intact and re-verified:

| Check | Printed reading |
|---|---|
| T5 `Analytic.Phi` gone / `Race.Phi` used | `grep -c "public static double Phi" gk-core/tools/CombatSim/Analytic.cs` = 0; `grep -c "Race.Phi"` = 4 |
| T7 `StatusMath` delegates | `grep -c "StatusUptime." gk-core/tools/CombatSim/StatusModel.cs` = 7; `grep -c "Math.Pow"` = 0 |
| T8 advance + call-through | `grep -c "ResourcePoolState" ActionSchedule.cs` = 6; `grep -c "ActionSchedule\.Choose|ActionSchedule\.Advance" ActionEconomy.cs` = 5 |
| guard | `CLASS-SYSTEM GUARD OK` |
| residuals | `ProvePredictor` 2.827E-007 / 3.495E-006 / **8.836E-007** / **8.836E-007** (unchanged) |
| focused suites | `Core.Vocabulary.Tests` 11/0; `Core.Balance.Tests` 210/0; `ClassSystemGuardTests` 16/0 |

## G7 negative coverage widened to every Balance/Analytic file (Race excepted)

The plan's G7 line read "all five `Balance/Analytic` damage files plus the two siege estimators". The
scan covered only `StrikeMixture`, `PhaseModel`, `ActionSchedule` + the two siege files. It now covers
`StatusUptime`, `Predictor` and `FirstPassage` too — every file under `Balance/Analytic` except
`Race.cs`, which alone writes the A&S `Math.Exp`/`1.0/(1.0 + ...)` normal CDF. `Predictor`'s
correlation clamp is `Math.Clamp(cov / Math.Sqrt(...), -1.0, 1.0)` (no `Math.Max(`), so it does not
match the clamp-and-scale shape.

| Check | Printed reading |
|---|---|
| real tree | `CLASS-SYSTEM GUARD OK` |
| new coverage bites | fixture `Predictor.cs` = `1.0 / (1.0 + Math.Exp(-d))` → exit 1 with both G7 lines (`re-derives a sigmoid (Math.Exp)`, `re-derives a bare 1/(1+...) sigmoid`) |
| existing fixtures | `ClassSystemGuardTests` 16/0 |

## Checkpoint 5 — npm build/test (grant #3)

`gk-web/web/fusion-rpg-web`: `npm ci`, then the two scripts the checkpoint names.

| Check | Printed reading |
|---|---|
| build | `npm run build` → `✓ built in 8.54s`, exit 0 (tsc --noEmit + vite) |
| tests | `npm test` → `Test Files 387 passed (387)`, `Tests 3258 passed (3258)`, exit 0 |

Two stale-catalog defects surfaced and were fixed to reach that green, both fallout of the
lead-token migration (`identity-rename` T6) that the web suite had not absorbed:

1. `src/i18n/locales/en/messages.po` — the source-locale msgstrs for `actor.dave.name`,
   `actor.penny.name`, `onboarding.reveal.title.dave` and `onboarding.reveal.title.gear` still held
   the pre-token English ("Dave", "Penny", "Crazy Dave joins your side", "Dave found a first piece
   of gear") while the source messages are now `{lead_summoner}` / `{lead_companion}` /
   `…{lead_summoner} joins your side`. `npm run extract` adds and reorders entries but preserves an
   existing msgstr, so the four were synced to their source messages. That took `npm test` from
   4 failed / 3254 passed to 1 failed, and surfaced the next one.
2. `src/ui/story-scene/StorySceneHost.pseudo.test.tsx` — it still expected the actor name tag and the
   sprite placeholder's interpolated name to be **pseudo-wrapped** (`pseudoTextOf(actorNameMessageId)`)
   and swept for "no leaf renders the English name". Both premises died with the token migration: a
   lead name is registry **data** (`registryFor` falls back to English for any locale without a names
   file), not a catalog msgstr, so under the pseudo locale the tag reads the registry display. The
   expectations now use `actorDefinition(id).displayName`, and the sweep asserts no actor
   **identifier** leaks as a name (`Dave`/`Penny`/`dave`/`penny`) — which is the defect the original
   sweep existed for.

`npm run extract` also reordered/added catalog entries from other lanes' source changes; both
`en/messages.po` and `pseudo/messages.po` are committed as its output.

## Task 14 — the inspect-scope vocabulary gets a declaring type (D18)

The removed copies: the byte-identical scope-normalisation line in `Server/DebugEndpoints.cs` and
`Injector/ControlInspect.cs`, plus the three scope literals in `ControlInspect.cs`'s two branch tests.
The surviving declaration: the new `gk-core/src/FusionRpg.Contracts/InspectScopes.cs` (`Menu` / `Lawn` / `All`,
a `Known` set, and `Normalize`).

| Criterion | Command | Result |
|---|---|---|
| no scope literal in either consumer | `grep -nE '"(menu\|lawn\|all)"' gk-core/src/FusionRpg.Server/DebugEndpoints.cs gk-fusion/src/FusionRpg.Injector/ControlInspect.cs` | no match in either file |
| both call the one declaration | `grep -n "InspectScopes" gk-core/src/FusionRpg.Server/DebugEndpoints.cs gk-fusion/src/FusionRpg.Injector/ControlInspect.cs` | `Normalize` once each; `Menu`/`Lawn`/`All` in the branch tests |
| guard | `dotnet test gk-core/tests/FusionRpg.Core.Vocabulary.Tests -c Release` | Passed! Failed: 0, Passed: 12, Total: 12 (was 11; +1 for the new scan) |
| server compiles | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj -c Release` | 0 Errors |
| injector compiles | `dotnet build gk-fusion/src/FusionRpg.Injector.BepInEx/...` and `scripts/guard-injector-compile.ps1` | **SKIPPED, not verified**: no game/interop dir on this host (`FUSIONRPG_GAME_DIR` unset), so the build drowns in 888 missing-`Assembly-CSharp`/`BepInEx` reference errors and the repo's own guard prints `INJECTOR COMPILE GUARD SKIPPED — no MelonLoader game dir`. The edit is a `using FusionRpg.Contracts;` plus three constant references; the Contracts project it names built cleanly. |

`InspectScopes` is the lowest common assembly both hosts already reference (Server → Contracts;
Injector → Core → Contracts), so this is the one home the graph allows.

## Task 16 — the two HUD folds call the shared helper (D20, D21)

The removed copies: `ActorHudDirector.CaptureStatus`'s own shield HP/max sum, and both inline
`hp / max` "true ratio" expressions. The surviving declarations: `Core/Hud/ActorHudShieldStacks.Totals`
and the new `Core/Vfx/ShieldBarVisual.TrueRatio`.

| Criterion | Command | Result |
|---|---|---|
| no inline shield fold in `Injector/Hud/**` | `grep -rnE "hp *\+=|\(float\).*Hp */" gk-fusion/src/FusionRpg.Injector/Hud/*.cs` | no match |
| both folds call the helper | `grep -n "ActorHudShieldStacks.Totals\|ShieldBarVisual.TrueRatio" gk-fusion/src/FusionRpg.Injector/Hud/*.cs` | `Totals` + `TrueRatio` in Director; `TrueRatio` in Pool |
| guard | `dotnet test gk-core/tests/FusionRpg.Core.Vocabulary.Tests -c Release` | Passed! Failed: 0, Passed: 13, Total: 13 (was 12; +1) |
| Core compiles | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj -c Release` | 0 Errors |
| boundary guards | `guard-secondary-no-unity`, `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-test-substrate`, `guard-verification-boundaries` | all OK |
| injector compiles | `scripts/guard-injector-compile.ps1` | **SKIPPED, not verified**: no game/interop dir on this host, same as T14. The two edits are a `using FusionRpg.Core.Hud;`, a call to `Totals(snapshots)`, and two `ShieldBarVisual.TrueRatio` calls. |

Byte-identical payload: `ShieldRuntime` clamps `Hp ≤ MaxHp` on every write, so the Director's old
unclamped form and the Pool's old `Clamp01` form agreed on every reachable value and `TrueRatio`
returns it unchanged.

## Task 17 — the sigmoid context read agrees across C# and TS (D11, D12) — CLOSED

The wrong side: `ItemDisplayRenderer.FormatSigmoidContext` (C#) rendered `deltaPoints / scale` pp,
which is not a sigmoid; `magnitude.ts` was already `(sigmoid(delta/scale) − sigmoid(0)) × 100`, the
read `docs/design/spec-magnitude-and-units.md` §4.1 defines and §14 D.1's worked example pins. The C#
side was fixed in `62e56f160`; this commit adds the parity and tuning checks on the TS side.

| Criterion | Command | Result |
|---|---|---|
| C# fixture | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests -c Release --filter "FullyQualifiedName~ItemDisplayTests"` | Passed! Failed: 0, Passed: 35, Total: 35 (0→0.0, 30→7.4, 150→31.8, −150→−31.8) |
| TS parity + tuning check | `npx vitest run src/i18n/magnitude.test.ts` | Test Files 1 passed; Tests 37 passed — the same four-delta fixture, plus `SIGMOID_STEEPNESS` and all three `CombatProbabilityScale` values against `gk-core/data/tuning/stats.v1.json` |
| whole web suite | `npm test` | Test Files 387 passed; Tests 3258 passed |
| web boundary resolves | `verify-change -Paths gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts -PlanOnly` | `gk-web/web/fusion-rpg-web -> web-fusion-rpg-web (module)`, `script: web-fusion-rpg-web` |

The parity table is the binding because no shared implementation crosses the C#/TS boundary; the
test's own comment says so.

## Manager grants #1-#6 — all landed

The six erratum grants were issued and all six rows landed, each with its own commit:

| # | Row | Commit | Reading |
|---|---|---|---|
| 1 | Audit §2 landing commits (+ §4 reasons) | `d0d61bcfc` (+ `85e704821`) | 19 reconciled rows annotated; §4 already held the keep-reasons |
| 2 | `spec-deterministic-core.md` §1 port status | `1849b949b` | each shape a Core call-through; only the adapter layer remains |
| 3 | `npm run build` / `npm test` | `30751ce7e` | build exit 0; 387 files / 3258 tests, 0 failed |
| 4 | T14 inspect-scope vocabulary | `a4d8062d0` | `InspectScopes` in Contracts; both hosts call it; Vocabulary 12/12 |
| 5 | T16 two HUD folds | `8dd4a665a` | `Totals` + `TrueRatio`; Vocabulary 13/13 |
| 6 | T17 C#/TS parity + tuning check | `de5f4b0aa` | C# 35/35; TS 37/37; full web suite green; `web-fusion-rpg-web` boundary already existed |

`combat-math-dedup` now has **zero open checkbox lines**; the audit §2 table carries a landing commit
on every reconciled row.

One blemish, recorded rather than hidden: the commit message of `85e704821` lost the SHA literals in
its prose (bash backtick substitution ate them — the message reads "D12 , D11 +TS , D18 , D20 , D21"
where the SHAs belong). The commit's *content* is correct; only its message is affected, and amending
is forbidden, so it stays as-is.

## Injector verification, deepened (T14/T16) — no game dir on this host

`guard-injector-compile.ps1` still SKIPS (no `FUSIONRPG_ML_GAMEDIR`, no `FUSIONRPG_GAME_DIR`), so a
full compile is impossible here. A direct BepInEx build was used to get the most the host allows; its
error profile shows the edits are sound even though the tree cannot link:

```
$ dotnet build src/FusionRpg.Injector.BepInEx/....csproj -c Release
exit=1
    216 error CS0103     (name does not exist)
   1552 error CS0246     (type or namespace not found)
      2 error CS0400
      6 error CS1061
```

- **No `CS1xxx` syntax error**, so `ControlInspect.cs`, `ActorHudDirector.cs` and `ActorHudPool.cs`
  parse cleanly.
- **Zero errors name `InspectScopes`, `ActorHudShieldStacks` or `TrueRatio`** — the new symbols resolve
  against Contracts/Core, which the host references. Every error names a Unity/IL2CPP type
  (`UnityEngine`, `GameObject`, `Material`, `BepInEx`, `Assembly-CSharp`, …), which is exactly the
  missing-game-dir set.

That is the strongest claim this host supports: the changes parse and their new references resolve;
only the Unity link step is unavailable.

## Optional improvement from the audit's §4 — the matrices.json divergence marker

The audit's §2.1c/§4 named one gap it did **not** ask a task to close, because the duplication there
is deliberate: `gk-data/packs/fusion/data/seed/elements/matrices.json`'s `combat` and `shield` blocks are independently
editable, and diverging them is an Ask-first balance decision — but nothing distinguished an intended
divergence from a typo. Landed here as the audit's own recommended shape (assert the contract, never
the content): `gk-core/tests/FusionRpg.Core.Tests/Combat/Element/ElementMatrixSeedDivergenceTests.cs`.

| Criterion | Command | Result |
|---|---|---|
| blocks identical → green | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~ElementMatrixSeedDivergenceTests"` | Passed! Failed: 0, Passed: 1, Total: 1 |
| diverged, no note → red | planted `unit: 9` on one shield row, re-ran the filter | Failed! 1 with `the combat and shield matrix blocks differ with no explicit _divergence note`; reverted |
| diverged, `_divergence` note → green | same planting plus a `_divergence` string, re-ran | Passed! 1; reverted |
| non-vacuity | the test asserts both blocks are non-empty and the same width before comparing | in the test body |
