# Combat / stat math duplication audit — 2026-09-16

**Status:** research finding, read-only. No source was edited producing this document.
**Question asked:** *"Where is combat/stat math implemented more than once? I don't want to write
duplicated code. We only have one place to resolve everything."*
**Scope:** formula and closed-vocabulary duplication. **Out of scope:** actor stat *composition*
duplication — that is `tasks/actor-hub-and-combat-power-solid-fixing-plan.md`'s program, and the
`BattleStatComposer` incident it closed on 2026-09-13 is not re-litigated here.
**Plan:** [tasks/combat-math-dedup-plan.md](../../tasks/combat-math-dedup-plan.md) ·
[tasks/combat-math-dedup-todo.md](../../tasks/combat-math-dedup-todo.md)

---

## 0. Design-gate record (DESIGN-GATE.md §0, §5)

Read in this session, before forming any view:

| Row | Documents read |
|---|---|
| Combat damage / HP | `architecture/combat-damage-ssot.md` (§1–§6.7 in full) |
| Stats | `architecture/actor-hub-ssot.md` (§8.1, §Q6, §828–830), `architecture/combat-power-number-ideal.md` |
| Elements | `architecture/element-hub-ssot.md` row + `ElementTable.cs`/`ElementRingMatrix.cs`/`ShieldElementMatrix.cs` source |
| Resources | DESIGN-GATE §1 Resources row + `DerivedStatChannels.cs:521` |
| Anything at all | `CLAUDE.md`, `AGENTS.md`, `docs/DESIGN-GATE.md` §1/§2/§5, `gk-core/scripts/guard-actor-hub.py`, `gk-core/scripts/guard-class-system.py` |

§5 checklist — honest gaps stated up front:

- [x] Read the surrounding section of every rule quoted.
- [ ] **Not ticked at audit time:** I did **not** run the test suite or build anything. Another session owns the
  source tree, and the brief is documents-only. Every divergence below is established by reading the
  code, not by executing it. Where I claim two implementations disagree numerically, I say whether
  that is *structural* (a missing term / different branch, provable from the source) or *measured*
  (it is never measured in this document).

  *(Closed by the program, 2026-09-23: `combat-math-dedup` ran every piece of this — `ProvePredictor`,
  `scripts/regen-class-system-baselines.ps1`, the full `test-fast -AllDefault` project list and the
  `gk-web/web/fusion-rpg-web` suite — and execution contradicted none of the audit's structural findings. The
  one numeric claim the program had to change was the audit's own D11, where the C# sigmoid read was
  the wrong side. The box stays unticked because it records the audit session's own scope, not the
  program's.)*
- [x] Nothing contradicts a §2 invariant. §2.15 (SOLID) and the one-ActorHub rule are the frame, not
  a target.
- [x] No assertion pins a derived-population count. Every count below is a **closed vocabulary**
  (an enum / registry a human edits) and is pinned deliberately, with its declaring file named.
- [x] This audit produces and consumes **no** actor combat magnitude. It invents no composer and no
  private fold.
- [x] Does not extend a SOLID-violating path. Every recommendation either removes a duplicate or
  explicitly recommends keeping one, with the reason.

---

## 1. The verdict on the five named files

The brief's hypothesis was that `SiegeExpectedDamage`, `SiegeHitChance`, `StrikeMixture`,
`PhaseModel` and `Predictor` are **estimators** — they produce a score or a prediction, never a real
damage number — so their duplication is a drift risk rather than a dual-compose defect.

**That hypothesis is correct for all five, and I tested it rather than assuming it.** Each one's
output was traced to its consumer:

| File | Output reaches | Real damage or persisted outcome? |
|---|---|---|
| `SiegeHitChance.EstimateMilli` | `SiegeAiIntentSource.cs:191` → `AiCandidate.HitChanceMilli` → `SiegeAi.cs:117` weighted score | **No.** A targeting score. |
| `SiegeExpectedDamage.IsKillingBlow` | `SiegeAiIntentSource.cs:214` → `AiCandidate.IsKillingBlow` → `SiegeAi.cs:117,159` `WeightKill × (bool ? 1000 : 0)` | **No.** A boolean term in a score. |
| `StrikeMixture.Compute` | `Predictor.Predict` → `DuelPrediction` (balance tooling, `PerfProbe` telemetry) | **No.** |
| `PhaseModel.*` | `Predictor.Predict` | **No.** |
| `Predictor.Predict` | `DominanceBaselineTests`, balance guards, `PerfProbe.RecordValue` | **No.** |

The real damage path is single and unforked: `ICombatMath` → `OverlayCombatMath.Finalize`
(`gk-core/src/FusionRpg.Core/Combat/OverlayCombatMath.cs:37`) → `OverlayCombatCalculator.Compute`
(`gk-core/src/FusionRpg.Core/Combat/OverlayCombatCalculator.cs:88`) → Funnel → FA10. There is exactly one
`ICombatMath` implementation that computes anything (`OverlayCombatMath`); the other two
(`PassThroughCombatMath`, `ConditionalOverlayCombatMath`) are a no-op and a toggle.

**So the answer to "is there a second damage resolver" is no.** That part is **built**.

**But the brief's second half — "if so, the fix may be extracting the shared pure functions" — is
already done, and that is the more useful finding.** `PierceFactor`, `AmpFactor`,
`AmpFactorReciprocal`, `DivisiveMitigation`, `CapAvoidanceBand`, `ResolveBand` are all declared
exactly once, as `public static` on `OverlayCombatCalculator`
(`OverlayCombatCalculator.cs:375,393,431,440,451,475`), and `CombatProbability.Sigmoid`
(`CombatProbability.cs:8`) and `ClampedContest.Apply` (`ClampedContest.cs:40`) likewise. Every
estimator calls them. **The mitigation-function family is clean — nobody re-derives those curves.**

What *is* duplicated is the **assembly**: the ~25-line sequence that reads the omni channels, calls
those primitives in order, and produces one swing. That sequence exists **four times**, and one of
the four has already drifted. That is the real subject of this audit. *(Closed 2026-09-23: the four
assemblies are now one `StrikeMixture` and its callers — see §3.)*

### 1.1 The one that has drifted: `SiegeExpectedDamage`

`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeExpectedDamage.cs:40`:

```csharp
var expectedDamage = attacker.Get(DerivedStatChannels.CombatPowerOmni) - effectiveDefense;
```

The shipped resolver's equivalent line is `OverlayCombatCalculator.cs:253-262`:

```csharp
var powerAdjusted = CombatPolicy.Default.DefenseShape == DefenseShape.Divisive
    ? DivisiveMitigation(offense: effectiveBaseDamage + weightedOffense, ...)
    : effectiveBaseDamage + weightedDelta;
```

Three structural divergences, all readable off the source:

1. **Wrong defense shape.** The estimator subtracts. `gk-core/data/tuning/combat.v1.json:24` ships
   `"defenseShape": "divisive"`, and `combat-damage-ssot.md` §6.3a records *why* subtractive was
   abandoned: it floors at zero the moment defense outruns offense, and **17.1% of landed hits dealt
   nothing** before the change. The estimator reproduces exactly that defect.
2. **No base-damage term at all.** `IsKillingBlow(attacker, defender, targetCurrentHp)` has no
   parameter for the authored hit. The resolver's damage is `base + power`-driven; the estimator's
   is `power` alone. An actor with `combat.power.omni = 0` swinging an authored 50-damage attack is
   scored as dealing `0 - defense` — never a killing blow, ever.
3. **No `ampFactor`, no crit.** `combat.amplification`/`combat.reduction` (`§6.7`) are ignored.

This is a **wiring gap**, not a real gap: `OverlayCombatCalculator.DivisiveMitigation` is `public
static` and already called from `StrikeMixture.cs:95`. The bypassing line is
`SiegeExpectedDamage.cs:40`. Its own file header (`SiegeExpectedDamage.cs:33-35`) claims the line is
*"Identical to OverlayCombatCalculator.Compute's own Omni-fallback branch
(Combat/OverlayCombatCalculator.cs:108-112)"* — that comment is **false today**, and the cited line
numbers no longer point at that branch either. Code beats comments.

### 1.2 The ones that are honest: `StrikeMixture`, `PhaseModel`, `Predictor`

`StrikeMixture.Compute` (`StrikeMixture.cs:55-125`) duplicates the omni assembly's *order* but calls
the shipped primitive at every step, and it is **bound to the real resolver by three parity tests**:

- `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/StrikeMixtureTests.cs:75` `CleanHit_damageMatchesOverlayCombatCalculator_forcedHitNoCrit`
- `...:108` `CleanCrit_damageMatchesOverlayCombatCalculator_forcedHitForcedCrit`
- `...:140` `Parried_damageMatchesOverlayCombatCalculator`

Each constructs the same snapshots, runs both paths, and asserts `-delta == round(mixture.X.Damage)`.
That is a real binding, and `FusionRpg.Core.Tests` runs in CI (`.github/workflows/ci.yml:153`).
`StrikeMixture` is **built** and should be left alone.

`PhaseModel` and `Predictor` are the same shape — composition over shipped primitives — with one
exception each, covered as D2 and D6 below.

---

## 2. Every duplicate found, ranked by blast radius if the two copies drift

Ranking rule: **silently wrong damage > silently wrong score > cosmetic.** "Silently wrong damage"
means a divergence changes a number that reaches HP or is persisted.

> **Landing commits.** A `landed <sha>` at the end of a row's *Reconcile shape* is the
> `combat-math-dedup` (lane `cmd-1`) commit that closed that row, pasted here 2026-09-23. Rows whose
> reconciliation shipped earlier carry their original `CLOSED, …` note and then the commit recording
> this program's verification. D10/D17/D22 are deliberately kept or owned elsewhere — see §4. Every
> reconciled row now carries a commit.

| # | What | Site A (authoritative) | Site B (the copy) | Parity test today? | Blast radius | Bucket | Reconcile shape |
|---|---|---|---|---|---|---|---|
| **D1** | Status id → L2b category, 24 ids stated twice | `Status/StatusCatalogBootstrap.cs:18-68` (`Register(..., StatusL2bCategory.X, ...)` per row) | `Status/StatusCategoryRegistry.cs:6-35` (`Map`) | **No** | 🔴 **silently wrong damage** | **wiring gap** | ~~Derive `Map` by seeding from the catalog; keep `Register` for additive ids~~ — **CLOSED, `solid-remediation` T5.1** (2026-09-20, `backlog-clean-up` `paperwork-reconcile` P5) — **landed `0b9ac6775`** (combat-math-dedup T1) |
| **D2** | Element enum → element id string, 6 arms twice | `Stats/Derived/ActorElementTypes.cs:93` `ToElementId` (throws on unknown) | `Combat/Element/ElementTable.cs:159` `IdOf` (**returns `""`** on unknown) | **No** | 🔴 **silently wrong damage** | **wiring gap** | ~~`IdOf` → `id.ToElementId()`; same assembly, 3 call sites~~ — **CLOSED, `solid-remediation` T5.2** (2026-09-20) — **landed `6be389a78`** (combat-math-dedup T2) |
| **D3** | Reflect chance + share formula, verbatim | `Combat/CombatDamageDispatcher.cs:113-118` | `Balance/Analytic/PhaseModel.cs:152-157` | **No** | 🟠 wrong score (balance model) | **real gap** (no shared function exists) | ~~Extract `CombatReflect.RateAndShare(...)` into `Core/Combat/`; same assembly~~ — **CLOSED, `solid-remediation` T2.7** (2026-09-20); a **3rd copy** was found in `gk-core/tools/CombatSim/Analytic.cs:250`, extracted to `ElementalResolver.RateFromZero`; `gk-core/tools/CombatSim`'s own copy deliberately kept as the `estimator-parity` reference, allowlisted — **landed `5e34197f5`** (combat-math-dedup T4; guard `ff39c519c`) |
| **D4** | Omni damage estimate vs shipped defense shape | `Combat/OverlayCombatCalculator.cs:253-262` | `Battle/Siege/SiegeExpectedDamage.cs:40` | **No** | 🟠 wrong score (siege AI targeting) | **wiring gap** | ~~Route through `DivisiveMitigation`, or better through `StrikeMixture.Compute(...).Mean`~~ — **CLOSED, `solid-remediation` T4.11/T4.12** (2026-09-20); parity test at a stated tolerance (10/10) — **landed `845301e76`** (combat-math-dedup T3) |
| **D5** | Whole omni swing assembly, 4th copy | `Balance/Analytic/StrikeMixture.cs:55-125` | `gk-core/tools/CombatSim/Analytic.cs:126-180` (`Strike`) | **No automated test.** Manual CLI only (`gk-core/tools/ProvePredictor`), run by no script and no CI workflow | 🟠 wrong score (every balance reading) | **real gap — stale migration** | ~~`Analytic.Strike` → `StrikeMixture.Compute`; CombatSim already references Core~~ — **CLOSED, `solid-remediation` T4.13** (2026-09-20); `ProvePredictor` actions-only diff unchanged (8.836E-007) — **landed `ddd074f1a`** (combat-math-dedup T6) |
| **D6** | Resource-pool lazy regen | `Actions/Cost/ResourcePoolState.cs:55` `Settle` (long, per-mille, carry-corrected, `checked`) | `Balance/Analytic/ActionSchedule.cs:87` `Math.Clamp(p.Value + p.Regen, 0, p.Max)` (double, no carry) | **No** | 🟠 wrong score (affordability walk) | **wiring gap** — `ActionSchedule.cs:7-15` still claims "there is no shipped resolver to call here"; that is stale since the action program closed 2026-09-07 | Read through `ResourcePoolState` / `ActorResourcePools` — **landed `ab07621e0`** (combat-math-dedup T8) |
| **D7** | `Phi` / `Erf` (A&S 7.1.26), same six coefficients | `Balance/Analytic/Race.cs:60,71` (guards NaN / ±∞) | `gk-core/tools/CombatSim/Analytic.cs:626` (**no guards**) | **No** | 🟡 cosmetic-to-score | **wiring gap** | Delete the CombatSim copy, call `Race.Phi` — **landed `b9f7df79f`** (combat-math-dedup T5) |
| **D8** | Status uptime + expected DoT per round | `Balance/Analytic/StatusUptime.cs:32` | `gk-core/tools/CombatSim/StatusModel.cs:65` (`StatusMath`) | **No** | 🟡 wrong score | **wiring gap** | CombatSim calls `StatusUptime` — **landed `264912eec`** (combat-math-dedup T7) |
| **D9** | Action-affordability walk | `Balance/Analytic/ActionSchedule.cs` | `gk-core/tools/CombatSim/ActionEconomy.cs` | **No** | 🟡 wrong score | **wiring gap** | CombatSim calls `ActionSchedule` — **landed `ab07621e0`** (combat-math-dedup T8) |
| **D10** | Aptitude → derived resolve | `Stats/Aptitudes/AptitudeResolver.cs` | `gk-core/tools/CombatSim/AptitudeModel.cs` | ✅ **Yes** — `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ResolverMatchesSimulatorTests.cs:53`, runs CombatSim as a real subprocess against live tuning, tolerance sized to the measured gap | 🟡 wrong score | **built (keep, with the parity test)** | **Leave alone** — see §4 |
| **D11** | Sigmoid **display** read, C# vs TS, **already numerically inconsistent** | `Items/Display/ItemDisplayRenderer.cs:41` — `delta/scale` pp (**not a sigmoid**) | `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:153` — `(sigmoid(delta/scale) − sigmoid(0)) × 100` pp | **No** | 🟡 cosmetic, but **player-facing and wrong today** | **real gap** (language boundary) | Decide which is correct per `docs/design/spec-magnitude-and-units.md` §5, fix the other, pin both to one fixture table — **landed `62e56f160`** (C# half) + **`de5f4b0aa`** (TS parity fixture) (combat-math-dedup T17) |
| **D12** | `CombatProbabilityPolicy` scales + steepness, hardcoded in TS | `Stats/Derived/CombatPolicies.cs:10-13` ← `gk-core/data/tuning/stats.v1.json` | `web/.../magnitude.ts:122,131-135` (`SIGMOID_STEEPNESS = 1.0`, all three scales `100.0`) | **No** | 🟡 cosmetic, latent | **real gap** | A test that reads `data/tuning/stats.v*.json` and asserts the TS constants match — **landed `de5f4b0aa`** (combat-math-dedup T17) |
| **D13** | `DamageFxTag` outcome vocabulary, 11 members twice | `gk-core/src/FusionRpg.Contracts/DamageFxDtos.cs:3-16` (enum, 11) | `Core/Effects/Atoms/AtomKindRegistry.cs:236-241` (`UiPresentTagValues`, 11 lowercased literals — its own comment at `:233` admits the mirror) | **No** | 🟡 cosmetic (atom validation) | **wiring gap** | Derive from `Enum.GetNames<DamageFxTag>()`. Core → Contracts, so the alias is legal — **landed `8be2dd0d4`** (combat-math-dedup T9) |
| **D14** | Area shapes, 4 members in 3 places | `gk-core/src/FusionRpg.Contracts/CombatDtos.cs:17-23` (`AreaShapes`, 4 string consts) | `Core/Actions/ActionTargetSpec.cs:42-48` (enum, 4) + `:132-155` (4 more lowercase literals) | **No** | 🟡 cosmetic | **wiring gap** | Not a straight `global using` — enum vs string consts. Replace the hand-written `Name`/`TryParse` literals with `Enum.GetName`/`Enum.TryParse`, add a test asserting enum names ≡ `AreaShapes` consts — **landed `ae0312308`** (combat-math-dedup T10) |
| **D15** | Rarity ladder, 10 rungs in 4 places | `Creatures/CreatureRarity.cs:16-28` (enum) + `:52-65` `ToId` | `Items/RarityLadder.cs:16-20` (`RungIds`, 10 literals) | **No** | 🟡 cosmetic | **wiring gap** | `RungIds` → `CreatureRarityLadder.All.Select(r => r.ToId())` (`CreatureRarityLadder.cs:51`) — **landed `144bd9292`** (combat-math-dedup T11) |
| **D16** | 28 combat channel families, listed twice | `Stats/Derived/DerivedStatChannels.cs:186-214` (`CombatChannelFamilies`) | `Effects/Atoms/Power/CoefficientTable.cs:271-286` (offense 13 + survivability 15) | **No** | 🟡 cosmetic (a new family gets no coefficient category) | **wiring gap** | Express B as a partition/lookup over A — **landed `56065ff51`** (combat-math-dedup T12) |
| **D17** | VFX status roster, **already drifted 21 vs 24** | `Status/StatusCategoryRegistry.cs:6-35` (24) | `Vfx/VfxCatalog.cs:87-97` (`StatusFx`, 21 — missing `nerve.unsettled`, `nerve.shaken`, `nerve.afflicted`; its own comment at `:85` says "one row per catalog status", which is now false) | **No** | 🟡 cosmetic (three statuses have no apply cue) | **wiring gap, already realized** | Add the three rows; make the roster derived or guarded |
| **D18** | `"menu"/"lawn"/"all"` inspect scope, byte-identical line in two assemblies | `gk-core/src/FusionRpg.Server/DebugEndpoints.cs:351` | `gk-fusion/src/FusionRpg.Injector/ControlInspect.cs:248` | **No** | 🟡 cosmetic | **real gap** (no declaring type exists anywhere) | Declare once in Contracts (both reference it) — **landed `a4d8062d0`** (combat-math-dedup T14) |
| **D19** | `DerivedStatSurfaceCatalog` re-literalises three vocabularies | `StatusPolicy.cs:70-75`, `DerivedStatChannels.cs:482-483`, `ActorElementTypes.cs:21` | `ActorSurface/DerivedStatSurfaceCatalog.cs:75-78`, `:98`, `:452-456` | **No** | 🟡 cosmetic | **wiring gap** | Reference the constants — **landed `19b950291`** (combat-math-dedup T13) |
| **D20** | Shield HP/max fold, byte-for-byte | `gk-core/src/FusionRpg.Core/Hud/ActorHudShieldStacks.cs:52-65` (`Totals`) | `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudDirector.cs:34-41` | **No** | 🟡 cosmetic (debug payload) | **wiring gap** — Injector → Core, so the call is available | Call `Totals` — **landed `8dd4a665a`** (combat-math-dedup T16) |
| **D21** | `trueRatio` = `hp/max`, written twice | *(no shared helper — `Vfx/ShieldBarVisual.cs` exposes only `DisplayRatio`)* | `Injector/Hud/ActorHudDirector.cs:55` and `Injector/Hud/ActorHudPool.cs:375` | **No** | 🟡 cosmetic | **real gap** | Add `ShieldBarVisual.TrueRatio` beside `DisplayRatio`, call from both — **landed `8dd4a665a`** (combat-math-dedup T16) |
| **D22** | `ClampToInt32`, identical bodies in two game-profile bridges | `Injector/Bridges/pvzrh-3.9/ZombieCombatFields.cs:23-28` | `Injector/Bridges/pvzrh-3.8.1/ZombieCombatFields.cs:26-31` | **No** | 🟡 cosmetic — only one compiles per build (`FusionRpg.Injector.BepInEx.csproj:33-35` selects by `$(GameProfile)`) | **structurally forced — keep** | See §4: the arithmetic is profile-independent but the *file* is profile-conditional by design. A parity test is the only available answer |

### 2.1 Things I checked and found genuinely **built** — no action

| What | Why it is one implementation |
|---|---|
| The four mitigation curves | `PierceFactor`/`AmpFactor`/`AmpFactorReciprocal`/`DivisiveMitigation` declared once each at `OverlayCombatCalculator.cs:431,440,451,475`. Every other site calls them. |
| The logistic | `ResistanceEvaluator.cs:124` is the only `1.0/(1.0 + Math.Exp(-x*steepness))` in `src/`. `CombatProbability.Sigmoid` is a thin wrapper. |
| `ClampedContest` | One declaration (`ClampedContest.cs:40`); shield, parry, block and both analytic models all call it. This is the repo's own best example of the extraction pattern working. |
| `ICombatMath` | One computing implementation. No second damage resolver. |
| Resource ids | `DerivedStatChannels.cs:521` is the single site; 30+ consumers read it. Already guarded against the JSON mirror at `ActorSurface/ActorSurfaceCatalogHub.cs:107-112`. **This is the pattern to copy.** |
| Attach points / atom kinds | `Effects/Atoms/AtomKind.cs:10-55` (9) and `AtomKindRegistry.Build()` (18), each declared once; parsed reflectively, never hand-listed. |
| `AtomTriggers` / `EffectTriggers` | Already fixed this session; guarded by `TriggerVocabularyTests.AtomTriggers_declares_no_string_literal_of_its_own`. |
| `RelationKind` / `RelationKinds` | Already aliased at `Actions/ActionTargetSpec.cs:4-5` via `global using`. The second precedent for the technique. |
| Element matchup matrices | The 36-pair table data is declared **once** — `ElementTable.cs:135` (`ring`) — and handed to the shield slot as a copy at `:155`. `ElementRingMatrix` and `ShieldElementMatrix` are two *accessors* with deliberately different contracts (`Same`-vs-`Neutral`, K baked in vs applied downstream). DESIGN-GATE §1 Elements already records this and the 2026-09-13 correction. **Leave alone.** |
| `ActorThetaSeam.HitChance/CritChance` | `Delve/Difficulty/ActorThetaSeam.cs:29,36` call the shared `CombatProbability.Sigmoid` over `BattleRuleset` base curves. Same function, different input domain — not a duplicate. |
| The four inline per-mille rolls | `gk-core/src/FusionRpg.Core/Battle/Capture/CaptureAction.cs:127`, `Match/LawnDeployEventEvaluator.cs:57`, `Effects/Atoms/AtomRunner.cs:151`, `Items/Drops/DropVolume.cs:108` use a different RNG interface (`NextPerMille()`, integer) than `CombatProbability.RollSuccess` (`ICombatRng`, double). Different streams, different units. **Leave alone.** |

### 2.1b The injector side is clean — a positive finding worth recording

`gk-fusion/src/FusionRpg.Injector`, `gk-core/src/FusionRpg.Server` and `gk-core/src/FusionRpg.CheatCore` were swept for any
arithmetic that re-derives a number Core already computes. **Nothing in the injector re-derives
damage, hit chance, crit, defense, or a stat total from parts.** Every combat number it touches is
obtained by calling Core:

| Site | What it does |
|---|---|
| `Injector/GameHooks.cs:742-761` (`EnsureDamageScaleCache`) | Reads `DefensePercent`/`DefenseFlat` from `CheatState.ActorHub.Resolve(...).AppliedCombat` (`:753`, `:757`). A **cache** of the resolve, keyed on `DocumentRevision`/`PvzStatsRevision` — not a second computation. |
| `Injector/GameHooks.cs:780-781`, `:929-930` | `StatMath.ScaleIncoming` (`gk-core/src/FusionRpg.Core/StatMath.cs:13`). The damage-scale formula has exactly one implementation and four callers (those two plus `SimEngine.cs:350,387`). |
| `Injector/Stats/EntityApply.cs:90,223,383` | `ActorHub.Resolve` / `ResolveDerivedWithContributions`. **Zero arithmetic in the whole file.** |
| `Injector/Stats/EntityStatWriter.cs` | HP deltas via `ResourceDeltaMath.Apply`. |
| `Injector/Effects/EffectRuntime.cs:527-540` | `OverlayCombatMath.Create` wrapped in Core's `ConditionalOverlayCombatMath`. |
| `Injector/DebugCombatActions.cs:183-199`, `CheatCommandRunner.cs:1403-1412`, `CheatPrefixes.cs:91-99` | `OverlayCombatCalculator.Compute`, `CombatDamageDispatcher.DispatchInstant`, `BulletFireResolver.Resolve` respectively. |
| `gk-core/src/FusionRpg.CheatCore/**` | **No arithmetic at all** — registry / schema / probe-pack declarations only. |

`LiveAtk` exists exactly once (`Core/Battle/BattleEngine.cs:101` → `BattleStatModifierLedger.Recompose`);
there is no `LiveHp` symbol anywhere. `ClampToInt32Reporting` (`EntityStatWriter.cs:49-51`) is a
single implementation.

Two contract inconsistencies found on the injector side, both real but small:

- **D20 / D21** above — two HUD folds, both in the debug/diagnostic payload path.
- **Bypass of the reporting clamp.** `EntityStatWriter.cs:46-48`'s own doc says every site should
  use `ClampToInt32Reporting` so saturation emits a `stat.writer.clampBoundary` proof event. Three
  sites call the bare `ZombieCombatFields.ClampToInt32` instead: `EntityStatWriter.cs:500-501`
  (LimHealth gate), `GameHooks.cs:780`, `GameHooks.cs:929`. Behaviourally identical; contractually
  inconsistent — a saturation on the damage path is currently silent. **Not a duplication finding**
  (it is the *same* function, called without its wrapper), recorded here because it was found in the
  same sweep and it is the kind of gap a reader of this audit would otherwise re-discover.
  **Resolved 2026-09-20** by `backlog-clean-up` BCU8.2: all four calls now reach
  `EntityStatWriter.ClampToInt32Reporting` (the wrapper is `internal` so `GameHooks` shares it), and
  `gk-core/tests/FusionRpg.Guard.Tests/InjectorWritePathHonestyGuardTests.cs` fails the build if the raw clamp
  is ever called from outside the wrapper again.

### 2.1c The element matrix seed data is duplicated — deliberately, and it shows

Verified by parsing `gk-data/packs/fusion/data/seed/elements/matrices.json`: `entries` holds **20 rows — 10 `matrix:
"combat"` and 10 `matrix: "shield"`, and the two sets are identical** on
`(attacker, defender, unit)`. In code the data is single-sourced
(`ElementTable.cs:135-151`'s `ring`, cloned into the shield slot at `:155` with
`ring.Select(r => r with { })`), but **that is only the fallback path** — once a host imports the DB,
the two matrices load independently from these two JSON blocks
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Elements.cs:61-62`).

This duplication is **intended**: `element-hub-ssot.md` and DESIGN-GATE §1 both record that the two
tables are independently editable and that diverging is an Ask-first balance decision. **Keep it.**
The honest gap is that nothing distinguishes an *intended* divergence from a typo — see §4.

### 2.2 Test-side duplication — in scope only where it hides drift

Checked; none of it hides drift, because every test-side copy calls the same shared primitive and
would move with it:

- `tests/.../Battle/BattleAdoptionTests.cs:15,19` `HitAtParity`/`CritAtParity` re-derive what
  `ActorThetaSeam.HitChance`/`CritChance` already expose. Both call `CombatProbability.Sigmoid`. A
  change to the curve moves both. Cosmetic; optional tidy, not a defect.
- `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/Resolve/ConcentrationApplicationTests.cs:362` — same shape.
- `tests/.../Combat/{EvasionChainTests,MitigationChainTests}.cs` assert **on** the canonical
  functions rather than copying them. Correct.

### 2.3 Documentation that is wrong *because* of a duplicate

> **CLOSED 2026-09-23** (`combat-math-dedup`, lane `cmd-1`): all four comments are fixed (the section
> said "three" and listed four). The table is kept as the finding.

Four comments asserted a property the code no longer had; each was fixed in the same task as its
duplicate, per the workflow rule "if what you verified contradicts a doc or comment, fix that
text in the same change":

| Claim | Where | Why it was false | Fixed by |
|---|---|---|---|
| *"A reimplementation of the math here would drift from src/ and make every balance reading a lie, so there is deliberately none."* | `gk-core/tools/CombatSim/CombatSim.csproj:12-14` | `Analytic.cs`, `StatusModel.cs`, `AptitudeModel.cs` and `ActionEconomy.cs` were exactly that. | T5 `b9f7df79f` |
| *"Identical to OverlayCombatCalculator.Compute's own Omni-fallback branch (…cs:108-112)"* | `Battle/Siege/SiegeExpectedDamage.cs:33-35` | It was not identical (D4), and the line numbers no longer pointed at that branch. | T3 `845301e76` |
| *"one row per catalog status"* | `Vfx/VfxCatalog.cs:85` | 21 rows vs the catalog's 24 (D17). | T15 (`backlog-clean-up` BCU8.1) |
| *"there is no shipped resolver to call here"* | `Balance/Analytic/ActionSchedule.cs:7-15` | `Actions/Cost/ActorResourcePools.cs` shipped when the action program closed (2026-09-07). | T8 `ab07621e0` |

---

## 3. The structural finding: `Balance/Analytic` is a migration that stopped halfway

> **CLOSED 2026-09-23** (`combat-math-dedup`, lane `cmd-1`): five of the seven pairs below are now
> call-throughs; the sixth (`Analytic.Predict`) is the reference `ProvePredictor` measures the port
> against, and the seventh (`AptitudeModel`) is a deliberate keep. The two "facts sharpen the risk"
> are both addressed. The section is kept as the finding that motivated T5–T8.

`docs/architecture/class-system/spec-deterministic-core.md:12` states the objective in its own
words:

> Move the closed form out of `gk-core/tools/CombatSim` and into `FusionRpg.Core`

It was **copied, not moved.** Seven pairs existed:

| `gk-core/src/FusionRpg.Core/Balance/Analytic/` | `gk-core/tools/CombatSim/` | Status |
|---|---|---|
| `StrikeMixture.Compute` | `Analytic.Strike` (D5) | **CLOSED** — call-through, `ddd074f1a` (T6) |
| `PhaseModel` shield/reflect terms | `Analytic` shield/reflect terms | **CLOSED** — `ElementalResolver.RateFromZero`, `5e34197f5` (T4) |
| `StatusUptime` | `StatusModel.StatusMath` (D8) | **CLOSED** — call-through, `264912eec` (T7) |
| `Race.Phi` / `Race.Erf` | `Analytic.Phi` (D7) | **CLOSED** — deleted, calls `Race.Phi`, `b9f7df79f` (T5) |
| `Predictor.Predict` | `Analytic.Predict` | **KEPT** — the reference `ProvePredictor` measures the port against; the `tools-prove-predictor` boundary now reaches it |
| `ActionSchedule` | `ActionEconomy` (D9) | **CLOSED** — call-through, `ab07621e0` (T8) |
| (`Stats/Aptitudes/AptitudeResolver`) | `AptitudeModel` (D10 — **this one has a parity test**) | **KEPT** — deliberate precision divergence, bound by `ResolverMatchesSimulatorTests` |

`gk-core/tools/CombatSim/CombatSim.csproj:11` already carries
`<ProjectReference Include="..\..\src\FusionRpg.Core\FusionRpg.Core.csproj" />`. **The assembly
graph permits deleting every copy above and calling Core directly.** Nothing structural is blocking
this; it is unfinished work.

Two facts sharpened the risk (**both addressed 2026-09-23**):

1. **Only one of the seven pairs was bound by an automated test** (D10,
   `ResolverMatchesSimulatorTests`). The others were bound by `gk-core/tools/ProvePredictor`, a manual CLI.
   *(After T5–T8 five pairs are call-throughs — drift is impossible by construction — and the two
   remaining keeps each have a binding: `ResolverMatchesSimulatorTests` for `AptitudeModel`,
   `ProvePredictor` for `Analytic.Predict`.)*
2. **`gk-core/tools/CombatSim/**` and `gk-core/tools/ProvePredictor/**` had no entry in
   `gk-core/scripts/verification-boundaries.v1.json`** (verified at the time: the only `tools/` boundaries
   were `ElementEnumGen`, `LawnCombatObserver`, `ProveLiveProbe` and their test projects). *(They do
   now: `tools-combat-sim` and `tools-prove-predictor`, both focused;
   `guard-verification-boundaries.py` prints OK.)*

---

## 4. What to leave alone, and why

The repo's own rule is that SOLID is "not a license to refactor everything for purity." Four
duplicates are legitimate keeps:

**D10 — `AptitudeModel` vs `AptitudeResolver`. Keep, with its existing parity test.**
The divergence is deliberate and load-bearing in both directions: Core discretizes `share^gamma` to
per-mille before multiplying and applies the recovery scale by integer division, because it ships in
the game and must reproduce exactly; CombatSim carries full-precision doubles because it is a
prototyping tool. Fusing them would force one of those choices onto the other. The tolerance in
`ResolverMatchesSimulatorTests.cs` is documented as *sized to the measured gap on the live config*,
not guessed, and the test runs CombatSim as a real subprocess against the live tuning file. That is
a correct "keep, with a parity test."

**Element ring vs shield matrix. Keep.** The data is already one declaration
(`ElementTable.cs:135`). The two accessors differ in *contract* — `ElementMatchupRelation.Same`
distinct from `Neutral` and K baked in, versus a bare `int ∈ {−1,0,+1}` with K applied once
downstream in `ShieldMath.cs:80`. One component cannot serve both without collapsing a distinction
the shield math depends on. DESIGN-GATE §1 already records this, including the 2026-09-13
correction to an earlier wrong reading of it.

**The four inline per-mille rolls. Keep.** Different RNG interface, different unit, different
streams. Routing them through `CombatProbability.RollSuccess` would change which RNG stream they
draw from — a behaviour change, not a dedup.

**`StrikeMixture`'s mirroring of the resolver's omni branch. Keep.** It duplicates the *order* but
calls the shared primitive at every step and is pinned to the real resolver by three parity tests
that run in CI. Collapsing the resolver's own branch and the closed form into one function would
mean the resolver — the thing that decides real damage — takes a dependency on a balance-tooling
abstraction. That trade is worse than the drift risk the parity tests already close.

**`BattleRateTests.HitAtParity`. Optional at most.** It duplicates `ActorThetaSeam.HitChance`, but
both call the shared sigmoid, so drift is impossible. Not worth a task on its own.

**D22 — the two `ZombieCombatFields.ClampToInt32` bodies. Keep, with a parity test.**
`Injector/Bridges/pvzrh-3.9/ZombieCombatFields.cs:23-28` and
`Injector/Bridges/pvzrh-3.8.1/ZombieCombatFields.cs:26-31` are identical code, but they are
**mutually exclusive at compile time** — `FusionRpg.Injector.BepInEx.csproj:33-35` excludes
`Bridges\**` and re-includes only `Bridges\$(GameProfile)\**`. Hoisting the clamp out of the
profile directory means creating a profile-independent file inside a directory tree whose entire
contract is "one profile per build", which is a worse shape than the duplicate. This is a
**structurally forced duplicate**: a parity test asserting the two bodies agree is the only
available answer, and it is cheap.

**The `matrices.json` combat/shield blocks. Keep, with a *divergence marker*, not a parity test.**
A plain parity test here would be wrong — it would fail the day a balance pass legitimately
diverges the shield matrix, and the "fix" would be to delete the test. What the file lacks is a way
to tell an intended divergence from a typo. The right shape is a test that asserts *either* the two
blocks are identical *or* the file carries an explicit `"_divergence"` note naming the decision —
so the guard stays green across generations, and diverging costs one line of intent rather than a
test edit. (This is the `validation-ssot.md` rule applied: assert the contract, never the content.)

**Landed 2026-09-23** (`combat-math-dedup`):
`gk-core/tests/FusionRpg.Core.Tests/Combat/Element/ElementMatrixSeedDivergenceTests.cs`. Proven both ways —
a planted divergence with no note fails with the note's own message, and the same divergence plus a
`_divergence` string passes.

---

## 5. Guard coverage today, and where it is thin

> **Superseded for G7, 2026-09-23** (`combat-math-dedup`, lane `cmd-1`): the G7 row below records the
> pre-program state. All three gaps it names are closed, and the entry now says how. The row is kept
> as the finding that motivated T3/T4/T6/T7/T8.

| Guard | Covers | Gap |
|---|---|---|
| `gk-core/scripts/guard-actor-hub.py` | Parallel *composers* and `BattleChannelMod` producers. **Allowlist:** `Core/Stats/Derived/**`, `Stats/PvzStatsSheetComposer.cs`, `Stats/StatComposer.cs` (composer ban) and `Battle/TraitAtomSource.cs` (the one surviving `BattleChannelMod` producer — the other two were deleted as proven-dead folds at `battle-ops-parity` T7). | Says nothing about **formula** duplication. Correct scope; noted so nobody assumes it covers this audit. |
| `gk-core/scripts/guard-class-system.py` (G7) | Every file the guard names, both trees. | **All three named gaps CLOSED 2026-09-23 by `combat-math-dedup`; this cell is the pre-program finding.** (a) a *negative* half now rejects an inline `Math.Exp(` / bare `1/(1+…)` / `Math.Clamp(Math.Max(` over each covered file, and was seen to fail on a planted `Math.Exp`; (b) the positive list is explicit full paths — `StrikeMixture`, `PhaseModel`, `Battle/Siege/SiegeExpectedDamage`, `Battle/Siege/SiegeHitChance`; (c) the negative scan also covers `ActionSchedule`, `StatusUptime`, `Predictor` and `FirstPassage` (only `Race` is excluded — its A&S `Math.Exp` is legitimate), and the `gk-core/tools/CombatSim` call-throughs are checked by name (`Analytic.Strike` → `StrikeMixture`, `StatusModel` → `StatusUptime`, `ActionEconomy` → `ActionSchedule`). |
| `TriggerVocabularyTests.AtomTriggers_declares_no_string_literal_of_its_own` | The trigger vocabulary. | The **right shape** — a *negative* check ("declares no literal of its own"). This is the template every vocabulary task below should copy, not G7's positive one. |

---

## 6. Recommended reconcile shapes, and the reason the assembly graph forces each

Verified project references:

```
FusionRpg.Contracts  → (nothing)
FusionRpg.Core       → Contracts
FusionRpg.CheatCore  → Contracts            ← does NOT reference Core
FusionRpg.Data       → Contracts, Core, CheatCore
FusionRpg.Server     → Contracts, Core, CheatCore, Data
gk-core/tools/CombatSim      → Core
gk-web/web/fusion-rpg-web   → (no assembly relationship at all)
```

| Situation | Available fix | Duplicates it applies to |
|---|---|---|
| Both copies in **Core** | Delete one outright; same-assembly extraction is free | D1, D2, D3, D4, D6, D15, D16, D17, D19 |
| **Contracts** declares it, **Core** mirrors it | `global using` alias or `Enum.GetNames` derivation — the `AtomTriggers`/`RelationKind` template | D13, D14 |
| **CombatSim** mirrors **Core** | CombatSim already references Core: call through | D5, D7, D8, D9 |
| **Core** and **CheatCore**, or **Server** and **Injector**, with no shared declaring type | Move the declaration **down into Contracts** (the only assembly both see) | D18 |
| **C# and TypeScript** | No shared implementation is possible. Only a parity test that reads the C#-side source of truth (the tuning JSON) and asserts the TS constant | D11, D12 |

> **All applied 2026-09-23** (`combat-math-dedup`, lane `cmd-1`): every row's recommended shape is in
> the tree. The duplicates deliberately kept (D10, D22, the element matrices, the four inline rolls,
> `StrikeMixture`'s mirroring, `BattleRateTests`' helpers) are listed with their reasons in §4.

---

## 7. Summary

> **Outcome 2026-09-23** (`combat-math-dedup`, lane `cmd-1`): every reconcile-worthy row below landed,
> and §7.1's three are all committed. The bullets are the pre-program reading, kept as the finding;
> where a sentence is now false it is marked inline.

- **No second damage resolver exists.** The five named files are estimators, confirmed by tracing
  each one's consumer. The shared mitigation and probability functions are already extracted and
  declared exactly once.
- **The duplication that remains is assembly-level and vocabulary-level**, and two instances have
  already drifted in ways that reach real combat numbers: D1 (status category, feeds
  `ResistanceEvaluator.cs:166`) and D2 (element id, feeds the matchup bonus, and the two copies
  disagree on whether an unknown element throws or silently reads neutral). *(Both closed: D1
  `0b9ac6775`, D2 `6be389a78`.)*
- **`Balance/Analytic` vs `gk-core/tools/CombatSim` is an unfinished migration**, not a design. Its own spec
  says "move"; what happened was "copy". Six of seven pairs have no automated parity test.
  *(Closed: five pairs are call-throughs, one is a deliberate keep with a parity test, and the last
  is the reference `ProvePredictor` measures — see §3.)*
- **The injector re-derives nothing.** Damage scale, `LiveAtk`, the crit-damage scale, `ClampedContest`
  and both element matrix readers are each single-implementation, and `EntityApply.cs` contains zero
  arithmetic. The only injector-side folds found are two HUD diagnostic ones (D20, D21).
- **Six duplicates should be left alone**, each for a stated reason, not for purity's sake: D10,
  D22, the element matrices (code and seed), the four inline per-mille rolls, `StrikeMixture`'s
  mirroring of the resolver, and `BattleRateTests`' helpers.

### 7.1 The three that were worth doing first — all landed

1. **D1 — status category declared twice.** The only duplicate on this list whose drift reaches a
   real combat number: `ResistanceEvaluator.cs:166` reads `StatusCategoryRegistry.GetRequiredCategory`
   to pick the resist category for a status apply. A status registered in the catalog under one
   category and in the registry under another silently resolves the wrong `status.resist.*` channel.
2. **D2 — element id switch declared twice, and the two copies disagree on failure.**
   `ToElementId` throws on an unknown element; `ElementTable.IdOf` returns `""`. `IdOf` feeds
   `ElementRingMatrix.GetRelation` (real matchup bonus → real damage) and
   `ShieldElementMatrix.RelationUnit`. A seventh element added to the enum and missed in `IdOf`
   reads as `""`, the matchup silently falls through to neutral, and nothing fails.
3. **D4 — the siege AI's damage estimate uses a defense shape the game abandoned.** Not a damage
   number, but a wrong one with a known cause and a shipped fix already sitting `public static` one
   call away.

Everything else is a score or cosmetic, and several are one-line derivations.

*(D1 `0b9ac6775`, D2 `6be389a78`, D4 `845301e76` — all committed 2026-09-23.)*
