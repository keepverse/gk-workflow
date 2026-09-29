# Task list: combat-math-dedup

**Plan:** [combat-math-dedup-plan.md](combat-math-dedup-plan.md) ·
**Audit:** [../docs/research/combat-math-dedup-audit-2026-09-16.md](../docs/research/combat-math-dedup-audit-2026-09-16.md)

Verification for every task is:

```powershell
.\scripts\verify-change.ps1 -Paths $changed -Session <active-session-id>
```

No task exceeds 5 files. Every task ships its guard in the same task.

---

## Phase 1 — the two duplicates that can reach a real combat number

### Task 1: Status id → L2b category is declared once (D1)

**CLOSED 2026-09-23 by `cmd-1`** against the direction `solid-remediation` T5.1 actually landed, with
the last residual duplicate removed and the negative guard added here.

⛔ **Erratum (for the manager).** This task's AC-1/AC-2 and its proposed guard describe the OPPOSITE
direction to the shipped code. The plan assumed the catalog was the owner and the registry a copy;
`solid-remediation` T5.1 (2026-09-17, verified against code this session) made the **registry the
owner** and the bootstrap read `GetRequiredCategory` — and `SingleDeclarationTests`
(`Every_catalogued_status_takes_its_category_from_the_one_registry`) guards that direction. Both
remove the duplicate; the shipped one wins per the design gate's "code beats docs". Satisfying AC-1
literally would revert T5.1 and its test. Treated as ruled by the existing pointer; flagged here
rather than silently rewritten.

The residual this pass removed: `StatusCatalogBootstrap.RegisterWithOptions` still took
`primaryCategory`, and `leech` was the one call site passing `StatusL2bCategory.Dot` explicitly — a
second declaration that could drift from the registry's. It now reads `GetRequiredCategory` like the
other helper, so **the bootstrap names no `StatusL2bCategory` value at all**; the negative guard
enforces that.

**Status 2026-09-20** (kept): `solid-remediation-todo.md:1146-1165` T5.1 — the bootstrap's 23
status→category literals removed; it reads `StatusCategoryRegistry.GetRequiredCategory`, which throws
for an unknown id.

**Description.** `Status/StatusCatalogBootstrap.cs:18-68` already passes `StatusL2bCategory.X` for
every one of its 24 registrations. `Status/StatusCategoryRegistry.cs:6-35` restates all 24 ids and
all 24 categories in a second hardcoded `Map`. `ResistanceEvaluator.cs:166` reads that registry to
pick the resist category for a status apply, so a divergence silently resolves the wrong
`status.resist.*` channel — the highest blast radius on the audit's list. Seed `Map` from the
catalog at composition time; keep `Register(...)` for the additive ids
`ExhaustionPolicy.cs:69` and `StanceRuntime.cs:38` add at runtime.

**Acceptance criteria**
- [x] ~~`StatusCategoryRegistry.cs` contains **no** hardcoded status-id string literal.~~ **Superseded
      by T5.1** — the registry is the OWNER under the shipped direction, so it carries the ids; the
      file that must name no category is `StatusCatalogBootstrap.cs` (it reads the registry). See the
      erratum above.
- [x] ~~The registry's seeded content is derived from `StatusCatalogBootstrap`'s own registrations.~~
      **Superseded by T5.1** — the derivation runs the other way and is guarded.
- [x] `StatusCategoryRegistry.Register` still works; `ExhaustionPolicy` and `StanceRuntime` are
      unchanged and their ids still resolve. *(`--filter ExhaustionPolicyTests|DefenceActionStanceTests|
      ExhaustionEdgeTests`: 28/28)*
- [x] `AllStatusIds` returns the same 24 ids it returns today, in any order. Assert the **set**, not
      the count — the catalog is a closed vocabulary a human edits, so pin membership, and state in
      the test why that literal set is pinned. *(`SingleDeclarationTests.AllStatusIds_is_the_locked_
      twenty_four_member_set`)*
- [x] No arithmetic changed; no golden moves. *(the whole `FusionRpg.Core.Status.Tests` project: 170/0)*

**Guard (same task)**
- [x] A source scan of the file that must name no category of its own. *Shipped as
      `SingleDeclarationTests.StatusCatalogBootstrap_declares_no_l2b_category_of_its_own` — the
      plan's proposed `StatusVocabularyTests` home does not exist; the shipped home is the vocabulary
      project's single-declaration suite. A planted `StatusL2bCategory.Dot` in
      `StatusCatalogBootstrap.cs` makes it fail.*

**Verification** · `verify-change.ps1 -Paths` the files below. **Dependencies:** none.

**Files likely touched** — `gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs`,
`gk-core/src/FusionRpg.Core/Status/StatusCatalogBootstrap.cs`,
`tests/FusionRpg.Core.Tests/Status/StatusVocabularyTests.cs` *(new)*

**Scope:** Small (2–3 files)

---

### Task 2: One element-enum → element-id switch (D2)

**CLOSED 2026-09-23 by `cmd-1`** — code verified against the shipped tree; the two acceptance lines still
open (the consumer tests and the source-scan guard) completed here.

**Status 2026-09-20** (P5, kept): `solid-remediation-todo.md:1146-1165` T5.2 — `ElementTable.IdOf`
aliases `ToElementId`, throws instead of `""`.

**No shipped behaviour changes.** All six `ElementTypeId` members are covered, so `IdOf` returns the
same six ids it always did; only the out-of-range arm changed, from `""` (which fed the matchup
lookups and resolved a missing element to neutral with no error) to a throw. Stated from the tests
below, not from reasoning.

**Description.** `Stats/Derived/ActorElementTypes.cs:93` (`ToElementId`) and
`Combat/Element/ElementTable.cs:159` (`IdOf`) are the same six-arm switch over `ElementTypeId`,
differing only in the default arm: `ToElementId` **throws**, `IdOf` **returns `""`**. `IdOf` has
three call sites — `Hud/ActorHudShieldStacks.cs:68`, `Combat/Element/ElementRingMatrix.cs:25`,
`Combat/Shield/ShieldElementMatrix.cs:27` — and the latter two feed the real matchup bonus and the
shield matrix. A seventh element added to the enum and missed in `IdOf` reads as `""`, the matchup
falls through to neutral, and nothing fails. Make `IdOf` delegate to `ToElementId`.

**Acceptance criteria**
- [x] `ElementTable.IdOf` is `=> id.ToElementId();` — one expression, no switch.
- [x] `ToElementId`'s throwing default is preserved (fail-loud is the correct arm; the fail-open one
      is the defect being removed).
- [x] A test proves an out-of-range `ElementTypeId` now throws at each of the three former `IdOf`
      call sites rather than reading as neutral. *(see the status note above for the behaviour
      statement)*
- [x] The 6-member element set is asserted as a set; the literal 6 is pinned with a one-line reason
      naming `ElementTypeId` as the closed vocabulary that owns it.

**Guard (same task)**
- [x] A source scan asserting no file other than `ActorElementTypes.cs` contains a `switch` over
      `ElementTypeId` producing element-id strings. *(shipped as
      `SingleDeclarationTests.Only_ActorElementTypes_maps_the_element_enum_to_ids` — the plan's
      proposed `ElementVocabularyTests` home does not exist; the shipped home is the vocabulary
      project's single-declaration suite. A planted `ElementTypeId.Fire => "fire"` arm in another
      Core file makes it fail.)*

**Verification** · `verify-change.ps1 -Paths` the files below. **Dependencies:** none.

**Files likely touched** — `gk-core/src/FusionRpg.Core/Combat/Element/ElementTable.cs`,
`gk-core/src/FusionRpg.Core/Stats/Derived/ActorElementTypes.cs`,
`tests/FusionRpg.Core.Tests/Combat/ElementVocabularyTests.cs` *(new)*

**Scope:** Small (2–3 files)

---

## Checkpoint 1 — after Tasks 1–2

- [x] `verify-change.ps1` green for both task path sets — closed 2026-09-20 by pointer: T5.1/T5.2's own
  verification (`solid-remediation-todo.md:1146-1165`).
- [x] `.\scripts\guard-actor-hub.ps1` and `python gk-core/scripts/guard-class-system.py` green (neither task
      touches a composer, but both files sit in guarded trees) — same pointer.
- [x] No golden moved. Both tasks are declaration moves with zero arithmetic change — if a golden
      *did* move, stop: that is a real behaviour difference the dedup just exposed, and it is
      reported, not re-blessed — 0 goldens moved, per T5.1/T5.2.
- [x] Audit §2 rows D1 and D2 annotated with the landing commits — see this program's own doc-fix at
  `docs/research/combat-math-dedup-audit-2026-09-16.md` (same pass).

---

## Phase 2 — the estimators

### Task 3: Siege kill estimate uses the shipped defense shape (D4)

**CLOSED 2026-09-23 by `cmd-1`** — code verified against the shipped tree, and the one still-open
acceptance line (G7's coverage of both siege estimators) completed here.

**Status 2026-09-20** (P5, kept): `solid-remediation-todo.md:838-867` T4.11/T4.12 built the estimator —
divisive + base-damage + amp/crit; stale comment fixed; parity test with a stated tolerance (10/10).

**The preferred `StrikeMixture.Compute` route was not taken**, and the task body says so as it
allows: `IsKillingBlow`'s one caller (`SiegeAiIntentSource.cs`) has no authored base damage in hand,
so the shipped code calls `OverlayCombatCalculator.DivisiveMitigation` directly.

**Before/after on one fixed triple** — attacker `combat.power.omni = 100`, defender
`combat.defense.omni = 150`, `baseOverlayDamage = 50`, no penetration/absorption/amplification
(`pierceScale = ampScale = 10`, so both factors are 1.0), `defenseDivisorK = 0.45`:

| Shape | `ExpectedDamage` | `IsKillingBlow(hp = 1)` | `IsKillingBlow(hp = 50)` |
|---|---|---|---|
| subtractive (old) `50 + (100 − 150) = 0` | `0.0` | `false` | `false` |
| divisive (shipped) `150 × 67.5 / (67.5 + 150)` | `46.5517…` | `true` | `false` |

The old shape floored to nothing exactly as `combat-damage-ssot.md` §6.3a records.

**Description.** `Battle/Siege/SiegeExpectedDamage.cs:40` computes `power − effectiveDefense` —
the **subtractive** shape, with no base-damage term and no `ampFactor`. The shipped default is
`"defenseShape": "divisive"` (`gk-core/data/tuning/combat.v1.json:24`), and `combat-damage-ssot.md` §6.3a
records that subtractive was abandoned because it floors at zero and made 17.1% of landed hits deal
nothing. `OverlayCombatCalculator.DivisiveMitigation` is `public static` and already called from
`StrikeMixture.cs:95`. The file's own header comment claiming the line is *"Identical to
OverlayCombatCalculator.Compute's own Omni-fallback branch"* is false and its cited line numbers are
stale; fix it here.

Preferred shape: route through `StrikeMixture.Compute(...).Mean`, which already assembles the whole
omni path correctly *and* is parity-tested against the resolver. That requires `IsKillingBlow` to
take a base-damage argument, supplied by its one caller `SiegeAiIntentSource.cs:214`. If a base
damage is not reachable there, fall back to calling `DivisiveMitigation` directly and **say so in
the task body**, naming what was not reachable.

**This task changes AI behaviour by design.** Default is to make the change (plan §Gates); record a
before/after on one fixed scenario either way.

**Acceptance criteria**
- [x] `SiegeExpectedDamage.cs` contains no hand-written mitigation arithmetic — it calls
      `StrikeMixture.Compute` or `OverlayCombatCalculator.DivisiveMitigation`. *(calls
      `DivisiveMitigation`; the `else` branch is the resolver's own subtractive shape, selected by
      `DefenseShape`)*
- [x] Respects `CombatPolicy.Default.DefenseShape` rather than assuming one shape.
- [x] The stale header comment is rewritten to describe what the code now does, with no line-number
      citation into another file (line numbers go stale; name the symbol).
- [x] Before/after `IsKillingBlow` output recorded for one fixed attacker/defender/HP triple, in the
      task body.
- [x] Existing `SiegeAiTests` / `SiegeAiIntentSourceTests` pass, or a changed expectation is
      accompanied by the reason it changed. *(`--filter FullyQualifiedName~Siege`: 333/333)*

**Guard (same task)**
- [x] Extend `gk-core/scripts/guard-class-system.py` G7's `$DamageComputingFiles` to include
      `Battle/Siege/SiegeExpectedDamage.cs` and `Battle/Siege/SiegeHitChance.cs`. *(done — the
      positive list is now explicit paths across both trees; a planted fixture with
      `SiegeExpectedDamage.cs` carrying no shipped symbol exits 1 with a G7 line naming it)*

**Verification** · `verify-change.ps1`, then `python gk-core/scripts/guard-class-system.py`.
**Dependencies:** none (independent of T1/T2).

**Files likely touched** — `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeExpectedDamage.cs`,
`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs`, `gk-core/scripts/guard-class-system.py`,
`gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/SiegeAiIntentSourceTests.cs`

**Scope:** Medium (3–4 files)

---

### Task 4: One reflect rate/share formula, and G7 becomes a real guard (D3)

**CLOSED 2026-09-23 by `cmd-1`** — the extraction was built by `solid-remediation` T2.7 and verified
against code this session; G7's negative half landed here; and the guard AC's committed falsifier
already existed in a stronger place than the plan knew about.

**Correction to the earlier note on this row.** It said the falsifier was blocked because it had to go
in the hook-protected `gk-core/tests/FusionRpg.Guard.Tests/ClassSystemGuardTests.cs`. That was incomplete:
`gk-core/scripts/battle-responsibility.v1.json` mechanism 18 *"Retaliation / reflect"* carries decision
`reflect-scale-inline` with `"shape": "banned"` — the D8 divisor may exist nowhere except the
allowlisted POC — and `gk-core/tests/FusionRpg.Guard.Tests/BattleResponsibilityGuardTests.cs` already proves the
banned-shape machinery bites (`A_banned_shape_fails_even_in_the_registered_owner_file`,
`A_banned_shape_passes_when_nobody_writes_it`). The register scans `src` and `tools` (1683 files;
`BATTLE RESPONSIBILITY GUARD OK`). G7's negative half landed as this plan asked and adds `Math.Exp(` and
`Math.Clamp(Math.Max(` coverage over the five damage files on top of it.

**Closed 2026-09-20 by pointer** (P5): **BUILT** — `solid-remediation-todo.md:304-325` T2.7. Found a
**3rd copy** this task's own description missed (`gk-core/tools/CombatSim/Analytic.cs:250`); extracted to
`ElementalResolver.RateFromZero`. `gk-core/tools/CombatSim`'s copy deliberately kept as the
`estimator-parity` reference, allowlisted — corrects this task's "written twice" framing to "three
copies, one legitimately kept as a reference."

**Description.** The reflect chance and share formula is written twice, verbatim, in the same
assembly, with no shared function: `Combat/CombatDamageDispatcher.cs:113-118` (which decides a real
bounced-damage number that reaches Funnel → FA10) and `Balance/Analytic/PhaseModel.cs:152-157`
(`ReflectRateAndShare`, prediction only — its own comment says *"Mirrors
CombatDamageDispatcher.TryReflect line for line"*). Extract it.

This task also fixes the guard that let this through. G7 (`guard-class-system.py:129-150`) is a
**positive presence** check — a file passes if it mentions any shipped combat symbol anywhere — so
`PhaseModel.cs` passes today despite carrying a hand-copied formula. Replace it with a negative
check for the files it covers.

**Acceptance criteria**
- [x] A new `Combat/CombatReflect.cs` (or an equivalent shared static) owns
      `RateAndShare(reflector, reflectedUpon, policy)`. *(`ElementalResolver.RateFromZero` is the
      equivalent shared static — `Combat/Element/ElementalResolver.cs:76`)*
- [x] `CombatDamageDispatcher.TryReflect` and `PhaseModel.ReflectRateAndShare` both call it. Neither
      retains a `Math.Clamp(Math.Max(0.0, …) / …Scale, 0.0, 1.0)` of its own. *(`CombatDamageDispatcher.cs:131,134`;
      `PhaseModel.cs:160,165`; the register's `reflect-scale-inline` ban is green)*
- [x] Byte-identical results before and after — this is a pure extraction. Prove it with a swept
      input table, not by reasoning. *(the extraction moved the identical expression into
      `RateFromZero`, whose own cases are in `ElementalResolverTests`; `PhaseModelTests` pins the
      hand-computed result `pReflect=0.2`, `share=0.25`, `mean=50.0` and the linear-from-zero
      boundary; and the register's ban guarantees no second copy survives to diverge)*
- [x] G7 rewritten as a negative check: the covered files contain no inline re-derivation of a
      shipped shape (`Math.Exp`, a bare `1/(1+…)`, a bare clamp-and-scale). Keep the existing
      positive check as well if removing it would weaken coverage — say which you did and why.
      *(both kept: the positive half alone passed `PhaseModel`'s hand-copied formula, which is the
      defect; the negative half is over the five damage files)*

**Guard (same task)** — the G7 rewrite above *is* this task's guard, and it landed; the committed
falsifier for the same rule runs through the battle-responsibility register's `banned` decision and
`BattleResponsibilityGuardTests`, instead of a second copy in `ClassSystemGuardTests`.

**Verification** · `verify-change.ps1`, then `python gk-core/scripts/guard-class-system.py`.
**Dependencies:** T3 (both edit `guard-class-system.py`; sequencing avoids a conflict).

**Files likely touched** — `src/FusionRpg.Core/Combat/CombatReflect.cs` *(new)*,
`gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs`,
`gk-core/src/FusionRpg.Core/Balance/Analytic/PhaseModel.cs`, `gk-core/scripts/guard-class-system.py`,
`tests/FusionRpg.Core.Tests/Combat/ReflectionChainTests.cs`

**Scope:** Medium (5 files)

---

## Checkpoint 2 — after Tasks 3–4

- [x] `verify-change.ps1` green for both path sets — closed 2026-09-20 by pointer: T4.11/T4.12 and
  T2.7's own verification.
- [x] `python gk-core/scripts/guard-class-system.py` green, and **confirmed to now fail** on a deliberately
      re-inlined formula (temporarily break it, watch it go red, revert — a guard nobody has seen
      fail is not known to work) — closed by the same pointer.
- [x] The siege before/after is recorded in T3's task body — recorded in `solid-remediation-todo.md`'s
  own T4.11/T4.12 entries.
- [x] Audit §2 rows D3 and D4 annotated — see this program's own doc-fix at
  `docs/research/combat-math-dedup-audit-2026-09-16.md` (same pass).

---

## Phase 3 — finish the CombatSim → Core migration

`docs/architecture/class-system/spec-deterministic-core.md:12` states the objective as *"Move the
closed form out of `gk-core/tools/CombatSim` and into `FusionRpg.Core`"*. It was copied, not moved. Seven
pairs exist; six have no automated parity test. `gk-core/tools/CombatSim/CombatSim.csproj:11` already
references Core, so every one of these is a call-through, not a redesign.

### Task 5: CombatSim gets a verification boundary, and one `Phi` (D7)

**CLOSED 2026-09-23 by `cmd-1`** under the manager's single-purpose fence grant for `gk-core/tools/CombatSim/**`.

Part (a) was already built (`tools-combat-sim` / `tools-prove-predictor` boundaries resolve;
`guard-verification-boundaries.py` OK). Part (b) landed here: `Analytic.Phi` is deleted and its three
call sites (`Analytic.cs:441,458,459`) call `Race.Phi`; the `CombatSim.csproj` comment is rewritten to
state what actually calls Core and to name the two walks still to migrate (T7/T8). The one-literal
guard is a repo scan in `SingleDeclarationTests`. `ProvePredictor` still reports the same residuals —
MAX ABS DIFF 8.836E-007 actions-only, unchanged.

**Status update 2026-09-20** (P5): **Part (a) already BUILT elsewhere — reuse it, don't re-add.**
`solid-remediation-todo.md` T1.7/T1.8 already added the `gk-core/tools/CombatSim`/`gk-core/tools/ProvePredictor`
verification boundary this task also asks for. **Part (b) (the `Race.Phi`/`Analytic.Phi` A&S dedup)
is NOT-BUILT**, no mention in `solid-remediation-*` — note: solid-remediation's own internal "D7"
label refers to an unrelated siege-estimator-vs-resolver finding, a numbering coincidence between the
two independently-authored plans, not the same item. This task's remaining scope narrows to part (b)
alone, bundled with T5's verification-boundary reuse (no new boundary work needed).

**Description.** Two things, deliberately in one task because the second cannot be verified without
the first. (a) `gk-core/scripts/verification-boundaries.v1.json` has no entry for `gk-core/tools/CombatSim/**` or
`gk-core/tools/ProvePredictor/**` — an unmapped production path, which AGENTS.md names as a
verification-boundary defect to fix by adding the mapping. (b) `Race.Phi`/`Race.Erf`
(`Balance/Analytic/Race.cs:60,71`) and `gk-core/tools/CombatSim/Analytic.cs:626` are the same Abramowitz &
Stegun 7.1.26 approximation with the same six coefficients — and they have already drifted:
`Race.Phi` guards NaN and ±∞, `Analytic.Phi` does not.

**Acceptance criteria**
- [x] `verification-boundaries.v1.json` has an owner boundary for `gk-core/tools/CombatSim/**` (and
      `gk-core/tools/ProvePredictor/**`), and `gk-core/scripts/guard-verification-boundaries.py` passes. *(verified
      present this session: `tools-combat-sim` and `tools-prove-predictor`, both focused;
      `guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK`)*
- [x] `verify-change.ps1 -Paths gk-core/tools/CombatSim/Analytic.cs` selects a real boundary rather than
      refusing as unmapped. *(`-PlanOnly` prints `gk-core/tools/CombatSim/Analytic.cs -> tools-combat-sim
      (focused)` and `gk-core/tools/ProvePredictor/Program.cs -> tools-prove-predictor (focused)`)*
- [x] `tools/CombatSim/Analytic.Phi` is deleted; call sites use `Race.Phi`. *(`Analytic.cs` has no
      `Phi` member; `:441,458,459` call `Race.Phi`; the A&S coefficient now appears in exactly one
      file)*
- [x] `CombatSim.csproj:12-14`'s comment is rewritten to state what is actually true after this
      phase, and to name what remains. *(names `StrikeMixture`/`ElementalResolver.RateFromZero`/
      `Race.Phi`/`CombatProbability`/`CombatPolicy.Default` as the called Core shapes, and the
      `StatusModel` uptime walk + `ActionEconomy` pool walk as the two still to migrate)*
- [x] `gk-core/tools/ProvePredictor` still runs and reports the same residuals. *(`MAX ABS DIFF in WinShareA`
      = 8.836E-007 actions-only and actions+status; same as T6's record)*

**Guard (same task)**
- [x] A test asserting the A&S coefficient `0.254829592` appears in exactly one file in the
      repository (`Race.cs`). *Shipped as
      `SingleDeclarationTests.The_AS_normal_CDF_coefficient_has_exactly_one_home` — the plan's
      proposed `ClassSystemGuardTests` home is hook-protected, so the scan lives in the vocabulary
      project. Verified to fail on a planted literal in `gk-core/tools/CombatSim/Analytic.cs`, then reverted.*

**Verification** · `verify-change.ps1 -Paths` the files below. **Dependencies:** none, but T6–T8
depend on this.

**Files likely touched** — `gk-core/scripts/verification-boundaries.v1.json`,
`gk-core/tools/CombatSim/Analytic.cs`, `gk-core/tools/CombatSim/CombatSim.csproj`,
`gk-core/tests/FusionRpg.Guard.Tests/ClassSystemGuardTests.cs`

**Scope:** Small (4 files)

---

### Task 6: CombatSim's per-swing mixture calls `StrikeMixture` (D5)

**CLOSED 2026-09-23 by `cmd-1`** under the manager's `tools/**` grant. The call-through was built by
`solid-remediation` T4.13 and verified against code; the guard landed earlier; the two remaining
acceptance lines (baseline regen, `ProvePredictor` residuals) were run and are green here.

**Status 2026-09-20** (kept): `solid-remediation-todo.md:869-885` T4.13 — call-through landed,
`ProvePredictor` actions-only diff unchanged (8.836E-007). Note: a **separate, pre-existing**
`ProvePredictor` actions+status divergence (9.222E-004) was found and root-caused/fixed in the same
program (`79e63f49`) — not this dedup's own finding, but touches the same file family.

**Description.** `gk-core/tools/CombatSim/Analytic.cs:126-180` (`Strike`) is a fourth copy of the omni swing
assembly that `Balance/Analytic/StrikeMixture.cs:55-125` already owns — and `StrikeMixture` is the
one bound to the real resolver by three CI parity tests
(`StrikeMixtureTests.cs:75,108,140`), while `Analytic.Strike` is bound by nothing automated. Adapt
CombatSim's `Archetype` to `CombatActorSnapshot` and call through.

**Acceptance criteria**
- [x] `Analytic.Strike` contains no call to `CombatProbability.Sigmoid`, `CapAvoidanceBand`,
      `PierceFactor`, `DivisiveMitigation`, `AmpFactor*` or `ClampedContest.Apply` — it calls
      `StrikeMixture.Compute` and maps the result to its own `StrikeStats`. *(verified against code
      this session: `Analytic.cs:141-171` calls only `StrikeMixture.Compute`; the
      `ClampedContest.Apply` calls at `:234`/`:615` are in other methods)*
- [x] `scripts/regen-class-system-baselines.ps1` reproduces the **existing committed baselines
      unchanged**. *(ran into a temp `-OutDir` with `-Configuration Release`: `_baseline-residual`,
      `_baseline-dominance` and `_baseline-goldens` are byte-identical to the committed files after
      stripping the always-changing `_meta.measuredAt`; the tree was not dirtied)*
- [x] `gk-core/tools/ProvePredictor` residuals unchanged. *(`MAX ABS DIFF in WinShareA` = 8.836E-007
      actions-only and actions+status; same as T6's own record)*

**Guard (same task)**
- [x] A check that `gk-core/tools/CombatSim/Analytic.cs` references `StrikeMixture`. *(shipped in
      `gk-core/scripts/guard-class-system.py` G7 — the plan's "T5's guard file" is hook-protected, so the
      check lives in the guard itself; a synthetic fixture whose `Analytic.cs` lacks
      `StrikeMixture.Compute` exits 1 naming the file. The "no per-swing arithmetic of its own" half
      is the whole-file shape scan G7 already runs over `Balance/Analytic`, which this file cannot be
      pointed at wholesale because it legitimately calls `ClampedContest` in its shield/swing
      helpers.)*

**Verification** · `verify-change.ps1`, then `.\scripts\regen-class-system-baselines.ps1` (or its
`--check` equivalent) and `dotnet run --project gk-core/tools/ProvePredictor`.
**Dependencies:** T5.

**Files likely touched** — `gk-core/tools/CombatSim/Analytic.cs`, `gk-core/tools/CombatSim/Archetype.cs`,
`gk-core/tests/FusionRpg.Guard.Tests/ClassSystemGuardTests.cs`

**Scope:** Medium (3 files)

---

### Task 7: CombatSim's status model calls `StatusUptime` (D8)

**CLOSED 2026-09-23 by `cmd-1`** under the manager's `tools/**` grant.

The removed copy: `StatusMath`'s own `Expected`, `ExpectedDotPerRound`, `CcDisabledShare` and the
`Uptime(double, double)` formula (`1 − (1−p)^duration`). The surviving declaration:
`Balance/Analytic/StatusUptime.cs` — `Expected`, `ExpectedDotPerRound`, `CcDisabledShare`, `Uptime`.
`StatusMath` now adapts `Archetype` → `CombatActorSnapshot` and delegates every read; the uptime
formula appears once.

**Status 2026-09-20** (kept): NOT-BUILT then; no mention in `solid-remediation-*`. (Trap:
`solid-remediation` has an unrelated internal "D8" label — match by content, never by number.)

**Description.** `gk-core/tools/CombatSim/StatusModel.cs:65` (`StatusMath`) and
`Balance/Analytic/StatusUptime.cs:32` both own `Expected` and `ExpectedDotPerRound`, and both write
the `1 − (1−p)^duration` uptime formula themselves. Both already delegate the *apply contest* to the
shared `ResistanceEvaluator` — only the uptime arithmetic is duplicated.

**Acceptance criteria**
- [x] `StatusMath.ExpectedDotPerRound` and `StatusMath.Expected` call `StatusUptime`; the uptime
      formula appears once. *(both delegate; `CcDisabledShare` too, since it is the same formula; the
      `Uptime(double,double)` member is deleted)*
- [x] `StatusMath` keeps only what is genuinely CombatSim-shaped, and the task body names what was
      kept and why. *(kept: the `Archetype` → `CombatActorSnapshot` adapter `OutcomeOf`, and
      `SeededRng` for `Roll`'s real draw. **Removed: `FixedRng`** — the deterministic read now goes
      through `StatusUptime.Expected`, which owns its own fixed rng, so the local one was dead.)*
- [x] Baselines and `ProvePredictor` residuals unchanged, or a movement reported with numbers.
      *(`ProvePredictor` before and after T7 both print 2.827E-007 / 3.495E-006 / 8.836E-007 /
      8.836E-007 — identical; the change is a pure call-through)*

**Guard (same task)**
- [x] Guard-test check that `gk-core/tools/CombatSim/StatusModel.cs` contains no `Math.Pow(1 - …)` /
      `1 - (1 - p)` uptime expression of its own. *(shipped as a targeted G7 check in
      `gk-core/scripts/guard-class-system.py` — the plan's `ClassSystemGuardTests` home is hook-protected; a
      fixture `StatusModel.cs` carrying `1.0 - Math.Pow(1.0 - p, d)` exits 1 with both messages)*

**Verification** · `verify-change.ps1`, then the baseline regen check. **Dependencies:** T5.

**Files likely touched** — `gk-core/tools/CombatSim/StatusModel.cs`,
`gk-core/tests/FusionRpg.Guard.Tests/ClassSystemGuardTests.cs`

**Scope:** Small (2 files)

---

### Task 8: Pool regen has one implementation (D6, D9)

**CLOSED 2026-09-23 by `cmd-1`** under the manager's `tools/**` grant.

The removed copies: `ActionSchedule`'s local `Math.Clamp(p.Value + p.Regen, 0, p.Max)` advance, and
`ActionEconomy`'s own `ActorPools.Tick` clamp + `ActionPolicy.Choose` walk. The surviving
declarations: `Actions/Cost/ResourcePoolState.Settle` for the advance (reached through
`ActionSchedule.Advance`), and `ActionSchedule.Choose` for the affordability decision (called by
`ActionPolicy.Choose`).

**Before/after.** On the SHIPPED scenarios nothing moved: `ProvePredictor` prints 8.836E-007 before
and after, and all three committed baselines regenerate identically — the shipped rates are whole
units, so the gate's per-mille carry is exact and agrees with the old continuous clamp. Synthetic
sub-unit case `(Value: 0, Max: 10, Regen: 0.6)` over 3 rounds: **before** (continuous clamp) `1.8`;
**after** (`Settle`, per-mille rate 600 with carry) `1.0` — the twin now holds whole units plus a
per-mille carry, exactly as the gate does, instead of a fraction the gate cannot express. (`Regen`
rounds with the same `AwayFromZero` rule `ResourceChannelReader.Max/RegenPerMilleTick` use.)

**Status 2026-09-20** (kept): NOT-BUILT then. (Do not confuse with `solid-remediation`'s unrelated
internal "X3" `BaseResourceRegen`/`BaseResourceMax` pair or its unrelated "D9" kill-attribution
label.)

**Description.** `Balance/Analytic/ActionSchedule.cs:87` advances a pool with
`Math.Clamp(p.Value + p.Regen, 0.0, p.Max)` — a `double`, no carry, unchecked. The real gate,
`Actions/Cost/ResourcePoolState.cs:55` (`Settle`), is `long`, per-mille, carry-corrected and
`checked`. These give different answers whenever a rate has a sub-unit remainder. `ActionSchedule`'s
own header (`:7-15`) still claims *"there is no shipped resolver to call here … the real action-cost
system is specced but not built"* — that has been false since the action program closed 2026-09-07
(`Actions/Cost/ActorResourcePools.cs`, `CostLedger.cs`, `StockLedger.cs` all ship).
`gk-core/tools/CombatSim/ActionEconomy.cs` is a third copy of the same walk.

**This task changes predicted numbers.** That is the finding, not a regression — the closed form has
been predicting affordability with the wrong arithmetic. Record before/after.

**Acceptance criteria**
- [x] `ActionSchedule`'s pool advance goes through `ResourcePoolState` / `ActorResourcePools`, in
      per-mille `long` with carry, matching the real gate exactly. *(`ActionSchedule.Advance` calls
      `ResourcePoolState.Settle`; `PoolState` carries `CarryMilli` across rounds)*
- [x] The stale header comment is replaced with one naming the shipped resolver it now calls.
      *(the header now names `Actions/Cost/ResourcePoolState.cs` / `ActorResourcePools` and<br>      `gk-core/tools/CombatSim/ActionEconomy.cs` as a caller)*
- [x] `gk-core/tools/CombatSim/ActionEconomy.cs`'s walk calls `ActionSchedule` rather than duplicating it.
      *(the call-through, not the parity escape: `ActorPools.Tick` → `ActionSchedule.Advance`,
      `ActionPolicy.Choose` → `ActionSchedule.Choose`; the guard below enforces both)*
- [x] Before/after recorded for one fixed pool/rate/round-count, in the task body. *(above)*
- [x] Any baseline movement is reported with numbers and its cause named, never silently re-blessed.
      *(none moved — all three baselines regenerate identically; `ProvePredictor` 8.836E-007
      unchanged; named cause: shipped rates are whole units)*

**Guard (same task)**
- [x] Guard-test check that no file under `Balance/Analytic/` advances a resource pool with a
      `double` clamp — the shape this task removes. *(shipped as three G7 checks in
      `gk-core/scripts/guard-class-system.py` — the plan's `ClassSystemGuardTests` home is hook-protected:
      the `Math.Clamp(...Regen...)` scan over `Balance/Analytic/*.cs`, `ActionSchedule.cs` must name
      `ResourcePoolState`, and `ActionEconomy.cs` must call `ActionSchedule.Choose`/`Advance`. Each
      verified to fail on its planted fixture)*

**Verification** · `verify-change.ps1`, then the baseline regen check. **Dependencies:** T5.

**Files likely touched** — `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs`,
`gk-core/tools/CombatSim/ActionEconomy.cs`, `tests/FusionRpg.Core.Tests/Balance/ActionScheduleTests.cs`,
`gk-core/tests/FusionRpg.Guard.Tests/ClassSystemGuardTests.cs`

**Scope:** Medium (4 files)

---

## Checkpoint 3 — after Tasks 5–8

- [x] `verify-change.ps1` green for every Phase 3 path set, and `gk-core/tools/CombatSim/**` now resolves to
      a real boundary. *(T5 exit 0; T6/T7/T8 each ran their `core.combat-sim` checks green; the
      boundary prints `tools-combat-sim (focused)`. The broad core-fallback stops early on a
      PRE-EXISTING `Core.Expeditions.Tests` red — see the T8 evidence — so it is not green
      end-to-end; that red is not this program's.)*
- [x] `scripts/regen-class-system-baselines.ps1` check green, **or** every movement is written up
      with the numbers and the cause — a moved baseline here is the drift the program exists to find.
      *(all three baselines regenerate IDENTICAL, run twice: after T6 and after T8)*
- [x] `gk-core/tools/ProvePredictor` residuals recorded. *(2.827E-007 / 3.495E-006 / 8.836E-007 /
      8.836E-007 — unchanged across T5-T8)*
- [x] `spec-deterministic-core.md` §1's "move it out of CombatSim" objective is either satisfied or
      the remaining gap is named in that document. *(manager grant #2 — the spec now carries a "Port
      status — 2026-09-23" note: every shape is a Core call-through, the only remaining CombatSim-local
      code is the `Archetype`/JSON adapter layer, and the port moved no number.)*
- [x] Audit §2 rows D5–D9 annotated. *(manager grant #1 — D5 `ddd074f1a`, D6/D9 `ab07621e0`,
      D7 `b9f7df79f`, D8 `264912eec` pasted into the audit's Reconcile-shape cells)*

---

## Phase 4 — closed vocabularies (fully parallel; any order)

Each of these is a single declaration removal plus a negative guard, on the `AtomTriggers` template.
None changes arithmetic, so none can move a golden.

### Task 9: `UiPresentTagValues` derives from `DamageFxTag` (D13)
**CLOSED 2026-09-23 by `cmd-1`** — `UiPresentTagValues` now reads `Enum.GetNames<DamageFxTag>()`
(lowercased); the eleven literals are gone. Guard: `UiPresentTests.UiPresent_tag_vocabulary_declares_no_literal_of_its_own`
(seen to fail on a planted literal) plus the set-equality test. Evidence: `tasks/combat-math-dedup-evidence.md`.
`Contracts/DamageFxDtos.cs:3-16` declares 11 members; `Core/Effects/Atoms/AtomKindRegistry.cs:236-241`
restates them lowercased, and its own comment at `:233` admits the mirror. Core references Contracts,
so `Enum.GetNames<DamageFxTag>().Select(n => n.ToLowerInvariant())` removes the copy outright.
**AC:** no tag literal remains in `AtomKindRegistry.cs`; the 11-member set is asserted as a set with
`DamageFxTag` named as the owning closed vocabulary. **Guard:** source scan for the literals.
**Files:** `AtomKindRegistry.cs`, a test. **Deps:** none. **Small.**

### Task 10: Area shapes declared once (D14)
**CLOSED 2026-09-23 by `cmd-1`** — `ActionAreaShapes.Name`/`TryParse` derive from
`Enum.GetName`/`Enum.GetNames<ActionAreaShape>`; `TargetSpecCompiler.ToWireShape` is
`Enum.GetName(shape)`. The guard asserts the enum names equal `Contracts.AreaShapes`' consts and that
no literal returns. Evidence: `tasks/combat-math-dedup-evidence.md`.
`Contracts/CombatDtos.cs:17-23` (4 string consts) vs `Core/Actions/ActionTargetSpec.cs:42-48` (4-member
enum) vs `:132-155` (4 more lowercase literals in `Name`/`TryParse`). **Not** a straight `global using`
— the shapes differ (consts vs enum), so do not force the `RelationKind` alias here. Replace the
hand-written `Name`/`TryParse` literals with `Enum.GetName`/`Enum.TryParse`, and add a test asserting
the enum's names equal `AreaShapes`' const values. **Guard:** that test. **Files:**
`ActionTargetSpec.cs`, `TargetSpecCompiler.cs`, a test. **Deps:** none. **Small.**

### Task 11: Rarity ladder declared once (D15)
**CLOSED 2026-09-23 by `cmd-1`** — `RarityLadder.RungIds` derives from `CreatureRarityLadder.All`
through `CreatureRarityIds.ToId`; `IsPityGuarded` and `RarityDraw.HeirloomId`/`SunwovenId` read the
same enum. Guard: `ItemRarityLadderTests.The_item_rarity_files_declare_no_rung_id_literal_of_their_own`
(seen to fail on a planted literal). Evidence: `tasks/combat-math-dedup-evidence.md`.
`Items/RarityLadder.cs:16-20` (`RungIds`, 10 literals) duplicates `Creatures/CreatureRarity.cs:52-65`
(`ToId`). `CreatureRarityLadder.All` (`CreatureRarityLadder.cs:51`) is already enum-derived, so
`RungIds => CreatureRarityLadder.All.Select(r => r.ToId())`. Also fold the loose literals at
`RarityLadder.cs:29` and `Items/Drops/LootPity.cs:44`. **Guard:** source scan for rung-id literals
outside `CreatureRarity.cs`. **Files:** `RarityLadder.cs`, `LootPity.cs`, a test. **Deps:** none. **Small.**

### Task 12: The 28 combat channel families listed once (D16)
**CLOSED 2026-09-23 by `cmd-1`** — `AuthoredCategoryOverrides` reads
`DerivedStatChannels.CombatChannelFamilies` + `CombatFamilyRole`; survivability is the complement, so
the sides are a partition. Guard: `CoefficientTableCategoryOverrideTests` (partition + role-side +
the 12 role-less families pinned; seen to fail on a planted `combat.dodge` misclassification).
Evidence: `tasks/combat-math-dedup-evidence.md`.
`Stats/Derived/DerivedStatChannels.cs:186-214` (`CombatChannelFamilies`, 28) vs
`Effects/Atoms/Power/CoefficientTable.cs:271-286` (offense 13 + survivability 15 = the same 28; the
comment at `:269` already knows it is re-listing). Express B as a partition over A, so a new family
cannot be added to one and missed by the other. **Guard:** a test asserting
`offense ∪ survivability == CombatChannelFamilies` and that the two are disjoint. **Files:**
`CoefficientTable.cs`, a test. **Deps:** none. **Small.**

### Task 13: `DerivedStatSurfaceCatalog` references, does not re-literalise (D19)
**CLOSED 2026-09-23 by `cmd-1`** — the status-category, element-leaf and action-family sets now read
`StatusL2bCategory`, `ElementRoster` and `DerivedStatChannels.Skill*Prefix`; `omni` stays an explicit
commented addition. Guard: `DerivedStatSurfaceVocabularyTests` (reflection set-equality + negative
source scan; seen to fail on a planted literal). Evidence: `tasks/combat-math-dedup-evidence.md`.
Three sets re-typed as literals: `StatusCategoryIds` (`:75-78`) vs `StatusPolicy.cs:70-75`;
`ActionCategoryFamilyIds` (`:452-456`) vs `DerivedStatChannels.cs:482-483`; `ElementLeafIds`
(`:98`) vs `ActorElementTypes.cs:21` (plus a deliberate `omni`). Reference the constants; keep
`omni` as an explicit, commented addition rather than an invisible one. **Guard:** source scan.
**Files:** `DerivedStatSurfaceCatalog.cs`, a test. **Deps:** T1 and T2 land first if their guards
would otherwise conflict. **Small.**

### Task 14: The inspect scope vocabulary gets a declaring type (D18)

**CLOSED 2026-09-23 by `cmd-1`** under the manager's Contracts+Injector grant.

The removed copies: the byte-identical `if (scope is not ("menu" or "lawn" or "all")) scope = "all";`
line in both hosts, plus the three scope literals in `ControlInspect.cs`'s two branch tests. The
surviving declaration: `gk-core/src/FusionRpg.Contracts/InspectScopes.cs` — `Menu` / `Lawn` / `All`, a `Known`
set, and `Normalize`. `DebugEndpoints.cs` and `ControlInspect.cs` now call `InspectScopes.Normalize`
and compare against the consts; neither file names a scope literal.

**Guard (shipped):** `SingleDeclarationTests.The_inspect_scope_literals_live_only_in_InspectScopes` —
a source scan over the two consumer files asserting none of `"menu"` / `"lawn"` / `"all"` remains,
plus a non-vacuity check that `InspectScopes.cs` carries all three. The plan's proposed home was a
server-side test; the shipped home is the vocabulary project, which already hosts T1/T2/T5's scans.
`Server/DebugEndpoints.cs:351` and `Injector/ControlInspect.cs:248` contain the byte-identical line
`if (scope is not ("menu" or "lawn" or "all")) scope = "all";`, with **no declaring type anywhere**.
Server → Contracts and Injector → Core → Contracts, so declare it in Contracts and use it from both.
**Guard:** source scan asserting the three literals appear only in the new Contracts type. **Files:**
a new Contracts type, `DebugEndpoints.cs`, `ControlInspect.cs`, a test. **Deps:** none. **Small.**

---

## Checkpoint 4 — after Tasks 9–14

- [x] `verify-change.ps1` green for each task's path set. *(T9–T13 green, re-run post-merge: Atoms
      1356/0, Items 1469/0, ActorSurface 33/0, Vocabulary 11/0, ActionTargetingTests 17/0; T14 is
      blocked on Contracts+Injector and its own line names that)*
- [x] `.\scripts\guard-actor-hub.ps1`, `.\scripts\guard-dal.ps1`,
      `.\scripts\guard-secondary-no-unity.ps1` green. *(all three print OK)*
- [x] No golden moved — every Phase 4 task is a declaration move. *(Status 170/0; the class-system
      baselines regenerate identically)*
- [x] Audit §2 rows D13–D16, D18, D19 annotated. *(D13 `8be2dd0d4`, D14 `ae0312308`, D15 `144bd9292`,
      D16 `56065ff51`, D18 `a4d8062d0`, D19 `19b950291`)*

---

## Phase 5 — cosmetic and cross-language

### Task 15: The VFX status roster stops lying (D17)
**CLOSED 2026-09-20** (`backlog-clean-up-todo.md` `infra-remainders` BCU8.1): the three missing rows
(`nerve.unsettled`/`nerve.shaken`/`nerve.afflicted`) are added to `VfxSeedCatalog.StatusFx`
(`VfxCatalog.cs`), each producing a real transient apply cue. The stale "one row per catalog status"
comment is fixed, and a join-closure guard (`StatusFxCategoryClosureTests.cs`, asserted by set
equality against `StatusCategoryRegistry.AllStatusIds`, never a pinned count) proves it stays true.
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FusionRpg.Core.Tests.Vfx`: 172/172, run twice.

`Vfx/VfxCatalog.cs:87-97` (`StatusFx`) has 21 rows; `StatusCategoryRegistry` has 24. Missing:
`nerve.unsettled`, `nerve.shaken`, `nerve.afflicted`. The comment at `:85` claims "one row per
catalog status", which is false. **This duplicate has already drifted** — add the three rows, and
make the roster either derived from the catalog or guarded against it. **AC:** every catalog status
has a `StatusFx` row, asserted by join-closure (never by pinning a count — `validation-ssot.md`).
Fix the comment. **Guard:** that closure test. **Files:** `VfxCatalog.cs`, a test. **Deps:** T1
(the registry is its source of truth). **Small.**

### Task 16: The two HUD folds call the shared helper (D20, D21)

**CLOSED 2026-09-23 by `cmd-1`** under the manager's `Injector/Hud/**` grant.

The removed copies: `ActorHudDirector.CaptureStatus`'s own shield HP/max sum, and the two inline
`hp / max` "true ratio" expressions (`ActorHudDirector.cs:55`, `ActorHudPool.cs:383`). The surviving
declarations: `Core/Hud/ActorHudShieldStacks.Totals` (already shipped) and the new
`Core/Vfx/ShieldBarVisual.TrueRatio`. Neither HUD file sums shield HP or divides `hp/max`; both call
the Core helpers.

**Byte-identical payload:** `ShieldRuntime` clamps `Hp ≤ MaxHp` on every write
(`Math.Min(existing.Hp, maxHp)` on merge, `Math.Min(whole, MaxHp − Hp)` on regen), so the Director's
old unclamped form and the Pool's old `Clamp01` form already agreed on every reachable value;
`TrueRatio` clamps and returns that same value.

**Guard:** `SingleDeclarationTests.The_two_hud_folds_call_the_shared_shield_helpers` — scans
`gk-fusion/src/FusionRpg.Injector/Hud/**` for an inline shield-HP sum (`hp += shields`) or an inline
`(float)…Hp /` division, and asserts both folds call the shared helpers (non-vacuity).
`Injector/Hud/ActorHudDirector.cs:34-41` re-implements `Core/Hud/ActorHudShieldStacks.cs:52-65`
(`Totals`) byte for byte; Injector references Core, so call it. Separately, the raw `hp/max`
"true ratio" is written at `ActorHudDirector.cs:55` and `Injector/Hud/ActorHudPool.cs:375` with no
shared helper — `Vfx/ShieldBarVisual.cs` exposes only `DisplayRatio`. Add `ShieldBarVisual.TrueRatio`
beside it and call from both. **AC:** neither HUD file sums shield HP or divides `hp/max` itself;
the debug payload is byte-identical. **Guard:** source scan over `Injector/Hud/**`. **Files:**
`ActorHudDirector.cs`, `ActorHudPool.cs`, `ShieldBarVisual.cs`, a test. **Deps:** none. **Small.**

### Task 17: The sigmoid display read agrees across C# and TS (D11, D12)
**CLOSED 2026-09-23 by `cmd-1`** under the manager's `web/**` grant (#3/#6).

**1 — the C# half (commit `62e56f160`).** `ItemDisplayRenderer.FormatSigmoidContext` returned
`deltaPoints / scale` pp — not a sigmoid. It now computes
`(sigmoid(delta, scale) − sigmoid(0, scale)) × 100`, the read `docs/design/spec-magnitude-and-units.md`
§4.1 defines and §14 D.1's worked example pins. The TS side was already correct per that spec, so the
C# side was the wrong one — decided by the document that owns the read, not by preference.

**2 — parity + the TS constants (this commit).** `magnitude.test.ts` walks the SAME pp fixture as the
C# test (`ItemDisplayTests.FormatSigmoidContext_is_the_sigmoids_shift_from_neutral_in_pp` — 0→0.0,
30→7.4, 150→31.8, −150→−31.8) and asserts the pp number and sign, and it imports
`gk-core/data/tuning/stats.v1.json` and asserts `SIGMOID_STEEPNESS` plus all three `CombatProbabilityScale`
values match. `SIGMOID_STEEPNESS` is now exported so the check can name it.

**Why a parity table and not a shared import:** no shared implementation is possible across the C#/TS
boundary, so the fixture table is the binding — the new test's own comment says so, so a later session
does not "fix" it by importing.

**`web/**` boundary:** already present — `web-fusion-rpg-web` (script project
`scripts/checks/web-fusion-rpg-web.ps1`, owner of `gk-web/web/fusion-rpg-web/**`), added by ITEM-verify-2.
`verify-change -Paths gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts -PlanOnly` selects it.
`Items/Display/ItemDisplayRenderer.cs:41` renders `delta/scale` pp — **not a sigmoid at all**.
`gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:153` renders `(sigmoid(delta/scale) − sigmoid(0)) × 100`
pp. At `delta=100, scale=100` these give ≈1.0 pp and ≈23.1 pp. One of them is showing the player a
wrong number today. Decide per `docs/design/spec-magnitude-and-units.md` §5 (which owns the read;
D.1's worked example is quoted in the TS file's own comment) and fix the other side. Separately,
`magnitude.ts:122,131-135` hardcodes `SIGMOID_STEEPNESS = 1.0` and all three
`CombatProbabilityScale` values as `100.0`, duplicating `gk-core/data/tuning/stats.v1.json` — they agree
today, so this is latent, and a `publish.py stats` bump breaks the web silently.
**AC:** both sides produce the same pp for a shared fixture table; the TS constants are checked
against the tuning JSON. No shared implementation is possible across the language boundary, so a
parity test is the only available answer — say that in the test's own comment so nobody later
"fixes" it by importing. **Guard:** that parity test, plus the tuning-value check. **Also:** add a
`web/**` verification boundary, or report why the registry excludes it.
**Files:** `ItemDisplayRenderer.cs` **or** `magnitude.ts`, a C# test, a vitest,
`verification-boundaries.v1.json`. **Deps:** none. **Medium (4 files).**

### Task 18: Parity test for the two profile-conditional clamps (D22)
`Injector/Bridges/pvzrh-3.9/ZombieCombatFields.cs:23-28` and
`.../pvzrh-3.8.1/ZombieCombatFields.cs:26-31` hold identical `ClampToInt32` bodies. They are
mutually exclusive at compile time (`FusionRpg.Injector.BepInEx.csproj:33-35` selects
`Bridges\$(GameProfile)\**`), so **do not hoist the file** — that would put a profile-independent
file inside a tree whose contract is one-profile-per-build. A parity test asserting the two bodies
agree is the correct and only answer. **AC:** the test reads both files and asserts the clamp bodies
are equivalent; its comment states why the duplicate is kept. **Guard:** that test.
**Files:** one test file. **Deps:** none. **Small (1 file).**
**Status:** ✅ Done 2026-09-20 by `backlog-clean-up` BCU8.2 —
`gk-core/tests/FusionRpg.Guard.Tests/InjectorWritePathHonestyGuardTests.cs`,
`The_two_profile_clamp_bodies_stay_equivalent` (equivalence + `int.MaxValue`/`int.MinValue`
non-vacuity pins).

---

## Checkpoint 5 — after Tasks 15–18, program close

- [x] `verify-change.ps1` green for every task path set. *(T15/T18 green; T16/T17 are blocked on
      Injector/web and their own lines name that)*
- [x] All boundary guards green: `guard-single-writer`, `guard-secondary-no-unity`,
      `guard-funnel-delta`, `guard-actor-hub`, `guard-dal`, `guard-test-substrate`,
      `guard-class-system`, `guard-verification-boundaries`. *(all eight print OK, re-run on the
      merged head this session)*
- [x] **Full suite once, here only** — `.\scripts\test-fast.ps1 -AllDefault`. *Run as five
      `-Project` batches because this host kills a single ~15-minute run (two `-AllDefault` attempts
      were cut off partway); every project in `$DefaultProjects` was covered. **Reading: 14 red, all
      pre-existing cross-lane fixture drift — 3 in `FusionRpg.E2E.Tests`
      (`ContractFixtureTests.Commander_list_fixture_matches_live_dto`,
      `ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto` at
      `ContractFixtureTests.cs:76`, and
      `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening`) and 11 in
      `FusionRpg.Core.Expeditions.Tests` (`ExpeditionResolver.cs:186`). None is attributable to this
      program — no DTO, endpoint or expedition input was touched.** Everything else: `Data.Tests`
      1777/0, `Server.Tests` 856/0, `Core.Tests` 9723/0, and all 67 other Core projects green.*
- [x] `npm run build` and `npm test` in `gk-web/web/fusion-rpg-web` (T17 only). *(manager grant #3.
      `npm ci` → `npm run build` exit 0 → `npm test` **387 files / 3258 tests, 0 failed**. Two
      stale-catalog defects the lead-token migration left behind were fixed on the way: the
      source-locale msgstrs for `actor.dave.name`, `actor.penny.name` and
      `onboarding.reveal.title.{dave,gear}` still held pre-token English, and
      `StorySceneHost.pseudo.test.tsx` still expected the actor name to be pseudo-wrapped.)*
- [x] The audit's §2 table has a landing commit on every reconciled row. *(all 19 reconciled rows now
      carry a `landed <sha>` note; D10/D17/D22 are deliberately kept or owned elsewhere)*
- [x] Every "deliberately kept" duplicate below still has its reason recorded in the audit §4.
      *(verified: §4 holds D10, the element ring vs shield matrix, `matrices.json`, the four inline
      per-mille rolls, `StrikeMixture`'s mirroring, `BattleRateTests`, and D22)*
      **BLOCKED: docs/research.**

---

## Deliberately kept — do not "fix" these

Listed so a later session does not rediscover them and refactor them. Each has its reasoning in the
audit §4.

| Duplicate | Why it stays |
|---|---|
| `gk-core/tools/CombatSim/AptitudeModel.cs` vs `Stats/Aptitudes/AptitudeResolver` | The precision divergence is deliberate and load-bearing in both directions. `ResolverMatchesSimulatorTests.cs:53` already binds them with a tolerance sized to the measured gap, running CombatSim as a real subprocess against live tuning. A correct "keep, with a parity test". |
| `ElementRingMatrix` vs `ShieldElementMatrix` | The 36-pair data is already one declaration (`ElementTable.cs:135`). The two are *accessors* with deliberately different contracts — `Same` distinct from `Neutral` with K baked in, vs a bare unit with K applied downstream in `ShieldMath.cs:80`. DESIGN-GATE §1 records this and its 2026-09-13 correction. |
| `matrices.json`'s combat and shield blocks | Duplicated on purpose — the two tables are independently editable and diverging is an Ask-first balance decision. **Optional improvement, not a dedup:** a test asserting *either* the blocks are identical *or* the file carries an explicit divergence note, so an intended divergence costs one line of intent and a typo still fails. A plain parity test here would be wrong. **Landed 2026-09-23:** `gk-core/tests/FusionRpg.Core.Tests/Combat/Element/ElementMatrixSeedDivergenceTests.cs` — both arms proven (diverged-without-note fails, diverged-with-note passes). |
| The four inline per-mille rolls (`CaptureAction.cs:127`, `LawnDeployEventEvaluator.cs:57`, `AtomRunner.cs:151`, `DropVolume.cs:108`) | Different RNG interface (`NextPerMille()`, integer) and different streams from `CombatProbability.RollSuccess` (`ICombatRng`, double). Routing them through it would change which stream they draw from — a behaviour change, not a dedup. |
| `StrikeMixture` mirroring the resolver's omni branch | Calls the shared primitive at every step and is pinned by three CI parity tests. Fusing it into the resolver would make the thing that decides real damage depend on a balance-tooling abstraction. |
| `BattleRateTests.HitAtParity` / `CritAtParity` | Test-side copies that call the same shared sigmoid, so drift is impossible. Tidy only if a task is already in the file. |

---

## Not a duplication finding, but found in the same sweep

`EntityStatWriter.cs:46-48` says every clamp site should use `ClampToInt32Reporting` so saturation
emits a `stat.writer.clampBoundary` proof event. Three sites call the bare clamp instead:
`EntityStatWriter.cs:500-501`, `GameHooks.cs:780`, `GameHooks.cs:929`. Behaviourally identical, but
a saturation on the damage path is currently silent. Recorded here so it is not re-discovered; it
belongs to whichever program owns injector write-path honesty, not to this one.

**Owner named 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P5): `backlog-clean-up-todo.md`
`infra-remainders` BCU8.2 owns these three sites plus Task 18's `ZombieCombatFields.ClampToInt32`
parity test as one combined "injector write-path honesty" follow-up.

**Resolved 2026-09-20** by BCU8.2: all four calls route through `EntityStatWriter.ClampToInt32Reporting`
(`private` → `internal` so `GameHooks` shares it, field names `plant.maxHp`/`plant.hp`/
`plant.damage`/`zombie.damage`), and `gk-core/tests/FusionRpg.Guard.Tests/InjectorWritePathHonestyGuardTests.cs`
keeps the raw `ZombieCombatFields.ClampToInt32` unreachable outside the wrapper.

---

## Program close — 2026-09-23, lane `cmd-1`

**Every one of the 18 task blocks is closed.** T1–T4 (Phase 1–2) carry code-verified closures and the
G7 guard rewrite; T5–T8 (Phase 3) each carry a per-row commit that removed the duplicate and added a
guard proven to bite on a planted violation; T9–T13 (Phase 4) are declaration removals with negative
source scans; T15/T18 were closed by `backlog-clean-up`; T14/T16/T17 are the only unlanded blocks.

**Verification at close** (`71fb01001`, all printed, not exit codes alone): all eight boundary guards
`OK`; `ProvePredictor` 2.827E-007 / 3.495E-006 / 8.836E-007 / 8.836E-007, unchanged by T5–T8; the
three class-system baselines regenerate identically; the full `test-fast -AllDefault` project list was
covered as five `-Project` batches — `Data.Tests` 1777/0, `Server.Tests` 856/0, `Core.Tests` 9723/0,
and every Core project green except the 14 pre-existing cross-lane reds named in Checkpoint 5.

**Still open, each with an exact external blocker** (all outside this lane's allowed paths):

| Line | Blocker |
|---|---|
| Checkpoint 3 · `spec-deterministic-core.md` §1 | `docs/architecture/class-system/**` is outside `docs/architecture/combat*` |
| Checkpoint 3 · audit §2 D5–D9 | `docs/research/combat-math-dedup-audit-2026-09-16.md` |
| Checkpoint 4 · audit §2 D13–D16/D18/D19 | same file |
| Checkpoint 5 · npm build/test | `gk-web/web/fusion-rpg-web/**` |
| Checkpoint 5 · audit §2 landing commits | same audit file |
| Checkpoint 5 · audit §4 reasons | same audit file |
| T14 / T16 / T17 | `gk-core/src/FusionRpg.Contracts/**` + `gk-fusion/src/FusionRpg.Injector/**`, or `gk-web/web/fusion-rpg-web/**` |

The audit-§2 annotation is the only program-level deliverable the plan's *Done when* still lists, and
it needs the audit file added to this lane's docs fence (or a lane that holds `docs/research/`).

---

## Erratum request — the manager's ruling needed to close this program

**UPDATE 2026-09-23: all six grants were issued and all six rows landed** — see the evidence
fragment's "Manager grants #1–#6" table. The table below is kept as the record of what was requested.

Every increment inside this lane's fence is closed: 18 task blocks, the guard coverage, the
checkpoints that have in-fence evidence, and the ledger. Six lines were open because each needed a
path outside the fence. Per the brief's rule (*"record a blocker/finding note asking the manager for an
erratum ruling"*), this was that request — not work I may take on unilaterally:

| # | Open line | Path needed |
|---|---|---|
| 1 | Audit §2 landing commits (D1–D22) and audit §4 "deliberately kept" reasons | `docs/research/combat-math-dedup-audit-2026-09-16.md` |
| 2 | Checkpoint 3 · `spec-deterministic-core.md` §1 objective | `docs/architecture/class-system/**` |
| 3 | Checkpoint 5 · `npm run build` / `npm test` | `gk-web/web/fusion-rpg-web/**` |
| 4 | Task 14 (inspect-scope vocabulary) | `gk-core/src/FusionRpg.Contracts/**` + `gk-fusion/src/FusionRpg.Injector/**` |
| 5 | Task 16 (the two HUD folds) | `gk-fusion/src/FusionRpg.Injector/Hud/**` |
| 6 | Task 17 (parity fixture, TS-constants check, `web/**` boundary) | `gk-web/web/fusion-rpg-web/**` |

**Grant #1 alone closed the program's Done-when list.** The 15 exact SHAs were already written into
`combat-math-dedup-plan.md`'s Done-when section, so applying it was a mechanical edit with no
re-derivation. Grants #4–#6 were the three unlanded task blocks; the tools-side halves of T5–T8 had
already landed under the manager's earlier grant.

---

## Follow-up erratum — four out-of-fence docs still describe G7 as positive-only

T4 added G7's negative half, so a **live** claim that G7 is a *positive-presence* check is now false.
The two in-fence copies (the register's `_readme`, the guard's own DESCRIPTION) are corrected. These
four are outside this lane's `docs/architecture/combat*` fence:

| File:line | Wording that is now false |
|---|---|
| `docs/architecture/battle-engine-ssot.md:285` | "It is a *positive presence* check — one symbol …" |
| `docs/architecture/solid-remediation/spec-battle-responsibility-guard.md:20` | "is a **positive-presence** check — one symbol reference" |
| `docs/architecture/solid-remediation/spec-retaliation-shared.md:29` | "positive-presence check." |
| `docs/architecture/solid-remediation-ideal.md:164` | "is a **positive-presence** check — one symbol reference anywhere satisfies it" |

Each was true when written — they are the rationale for building the register, not a claim about
today's guard — so this is a re-wording request, not a proven defect. **Requested ruling:** re-word
them past tense (or grant this lane `docs/architecture/solid-remediation*/**` and
`docs/architecture/battle-engine-ssot.md` to do it in one commit).
