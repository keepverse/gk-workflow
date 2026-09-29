# Todo: `action-enrich` (AE)

Plan: [action-enrich-plan.md](action-enrich-plan.md) · Map:
[action-enrich-map.md](../docs/architecture/action-enrich-map.md) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane A).

Id scheme: `AE1.x` is module `action-base`, `AE2.x` is module `lawn-action-base`. Order is **suggested,
not enforced**, except where an entry marks a parent hard edge (H1, H6, H7). `<session>` is the building
session's id. Every task is verified once with `verify-change.ps1` over all the paths it touched.

---

## Wave 1 — `action-base` (battle)

- [x] **AE1.1 — `action-base.v1.json` + `ActionBaseTuning` hub, configured by the server host (H7)** · S · deps: — · *(spec: action-base, Tunables)*
  - Acceptance: `gk-core/data/tuning/action-base.v1.json` holds `basicAttack.basePowerMilli`. Its `_meta` says
    it is **untuned**, names the event that will tune it (the A20 sweep after action `T74`), and records
    the measurement: the median `Setup.Atk` of the battle-golden actors, divided by `P(20)/1000`.
  - Acceptance: `ActionBaseTuningHub` follows `LawnAttritionTuningHub`'s shape: configured once, it
    throws when unconfigured, and it has no built-in default. `Program.cs` configures it **in the same
    commit** that creates the file (H7). The Core and Data test bootstraps configure it from the real
    file.
  - Acceptance: no damage path reads the hub yet, so goldens do not change (H6 holds by construction).
  - Verify: `dotnet build src\FusionRpg.Server` then `.\scripts\verify-change.ps1 -Paths <files> -Session <session>` and `python scripts\audit-magic-numbers.py --summary`
  - Files: `gk-core/data/tuning/action-base.v1.json` (new), `gk-core/src/FusionRpg.Core/Actions/ActionBaseTuning.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Core.Tests/ContractTuningTestBootstrap.cs`, `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs`

- [x] **AE1.2 — `EffectiveRungOf` becomes the one instance resolver, with a held-row fallback** · S · deps: — (coordinate with `ST2.5`) · *(spec: action-base, §Which rung)*
  - Acceptance: `BattleRunState` stores `unlockStateFor` and `unlockTuning` in private readonly fields
    and exposes `public int EffectiveRungOf(actorKey, actionId)`. `CostLedger` receives that method
    group as `rungOf`. If `ST2.5` landed first, this task adds only the fallback line. `HeldActionOf` is
    a thin lookup over `HeldActionsOf`.
  - Acceptance: the non-held fallback reads the **held row's** `Rung`. It is byte-identical to
    `actionCatalog.Get(id).Rung` for every catalog action, and it is correct for siege
    `AdditionalHeldActions` and lent garrison rows.
  - Acceptance: a call-counting double proves the ledger calls the resolver. All existing
    `ActionCostsCooldownsAdoption` tests and goldens pass unchanged.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionBase|FullyQualifiedName~ActionCostsCooldownsAdoption|FullyQualifiedName~BattleGolden"`
  - Files: `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionBaseTests.cs` (new)

- [x] **AE1.3 — Pure `ActionBaseDerivation`, `ActionBaseMath` and `BattleRuleset.PowerValue`** · S · deps: AE1.1 · *(spec: action-base, §Derivation, §The read, P(Θ))*
  - Acceptance: a skill or innate at effective rung `r` gives `RungRow(r).QPowerMilli` for every row of
    the loaded table, read from the table and never written as a literal. A basic attack gives the tuning
    value. A skill whose rung has no row throws, naming the action.
  - Acceptance: `BasePerHit` is `checked` `long` and divides by 1000 once, last. It stays exact past
    `int` range, and a `long` overflow throws. `PowerValue(int)` uses `BaseHp`'s cached ladder, with no
    new curve.
  - Acceptance: an unconfigured `ActionBaseTuningHub` throws, naming the file. No damage path calls any
    of this yet.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionBase"` then `python scripts\audit-overflow.py --targets A3`
  - Files: `gk-core/src/FusionRpg.Core/Actions/ActionBaseDerivation.cs` (new), `gk-core/src/FusionRpg.Core/Actions/ActionBaseMath.cs` (new), `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionBaseTests.cs`

- [x] **AE1.4 — Swap the hit's base: `BasicAttack.cs:369` reads base × `P(Θ)` and `LiveAtk` stops feeding damage (H6)** · M · deps: AE1.2, AE1.3 · *(spec: action-base, acceptance 1–3)*
  - Acceptance: **in one commit (H6)**, the swung row comes from `HeldActionOf` (an unheld envelope
    throws, naming the actor and the action). `Θ` comes from `attacker.Derived` `progression.power`
    through a `checked` narrowing. The guard `ActionBaseNoAtkRead` allows exactly the `LiveAtk` definition
    line (`BattleEngine.cs:101`) and nothing else under `gk-core/src/FusionRpg.Core/**`.
  - Acceptance: with effective rungs 1 and 9 on one attacker, the rung-9 hit is larger by
    `qPower(9)/qPower(1)` read from the table. Two setups that differ only in `ThetaActor` scale by
    `P(Θ₁)/P(Θ₂)`. The hybrid split, the matrix (through `OverlayCombatCalculator`) and the
    `OnDamageDealt` rider all still apply. The one-resolver test fails on a planted second rung
    computation at the hit.
  - Acceptance: every non-golden test is green. Goldens are expected to move, and they are re-blessed
    **only** in AE1.5. Any shipped content that grants an `atk` `stat.modify` is listed by id in the
    change description and handed to `SE1.6`, with no edit to generated JSON. If ST2 or ST1 moved a
    golden, AE1.1's calibration is re-measured first.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionBase|FullyQualifiedName~ActionCostsCooldownsAdoption"`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ActionBaseNoAtkRead"`; `.\scripts\guard-actor-hub.ps1`; `.\scripts\verify-change.ps1 -Paths <files> -Session <session>`
  - Files: `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs`, `gk-core/src/FusionRpg.Core/Combat/OverlayCombatCalculator.cs` (the `:12` doc comment that names `LiveAtk`), `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionBaseTests.cs`, `gk-core/tests/FusionRpg.Guard.Tests/ActionBaseNoAtkReadGuardTests.cs` (new)

- [x] **AE1.5 — Golden re-bless #3 (H1): the hit's base moves from `atk` to the action** · XS · deps: AE1.4, **`ST1.3` (H1)** · *(spec: action-base, acceptance 4)*
  - Acceptance: every moved battle golden is re-blessed in **its own commit**. The commit and the golden
    file's note name `action-base` and give the reason. The commit comes after `ST2.3` and `ST1.3`, and
    shares no cause with them or with `SP`'s.
  - Acceptance: `BattleGoldenTests` are green. Land this directly after AE1.4, so the tree is never left
    with only the red-golden commit.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"`
  - Files: `tests/FusionRpg.Core.Tests/Goldens/**` (only the files that moved)

- [x] **AE1.6 — `ssot-power-scale.md` §10.2 row for the rung `qPower(r)` ladder** · XS · deps: AE1.4 · *(spec: action-base, §Power-ladder registration)*
  - Acceptance: §10.2 gains the row the spec words: `qPower(r) = 1.75^((r-1)/2)`, 10 rows, bounded at
    the rung cap, multiplying `P(Θ)` exactly once at the hit, and reading row 19's `effectiveRung`. It
    is written with the power program's review.
  - Verify: manual re-read of §10.2 against `action-rungs.v{n}.json`'s `qPowerMilli` rows
  - Files: `docs/architecture/power/ssot-power-scale.md`

### Checkpoint 1 — battle reads the action
- [x] The `ActionBaseNoAtkRead` guard is green. No production damage path calls `LiveAtk(`.
- [x] Two effective rungs give two bases, and cost and base share one resolver (the call-counting test).
- [x] The AE1.5 re-bless commit exists and comes **third** in H1 (after `ST2.3` and `ST1.3`).
- [x] `guard-actor-hub.ps1` is green, `audit-overflow.py --targets A3` and `audit-magic-numbers.py` show
  no new finding, and the §10.2 row is written.

---

## Wave 2 — `lawn-action-base`

- [x] **AE2.1 — `PassesOverlayFilters` gains `excludeInstakill`** · XS · deps: — · *(spec: lawn-action-base, §Instakill refusal)*
  - Acceptance: a grant with `excludeInstakill: true` does not fire on an `InstakillShaped` event and
    does fire on an ordinary hit. A plain-amount grant **without** the filter behaves as before on an
    instakill event.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~OverlayFilterInstakill"`
  - Files: `gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs`, `tests/FusionRpg.Core.Tests/Effects/OverlayFilterInstakillTests.cs` (new)

- [x] **AE2.2 — The lawn grant bakes base × `P(Θ_owner)` at bind, and the injector host loads `action-base`** · M · deps: AE1.3, AE2.1 · *(spec: lawn-action-base, §Design, Host configuration)*
  - Acceptance: `BasicAttackGrantBuilder.Build(…, long amount)` writes `amount = -BasePerHit(base, P(Θ))`
    and `filters.excludeInstakill = true`. `elementPayload` and `icd_ms` are unchanged. A neutral owner
    gets an amount and no payload. The `fx.overlay_damage` def and generated atoms are not edited.
  - Acceptance: **parity.** For the same action at the same `Θ`, the lawn amount equals the battle
    `BaseOverlayDamage` before defense (shared `ActionBaseMath`/`ActionBaseDerivation`). The binder's `Θ`
    equals `ActorHub.ResolveDerived(ctx).Get(progression.power)`, and a **planted** second contributor
    to that channel fails the parity test.
  - Acceptance: `RpgHost.Initialize` configures `ActionBaseTuningHub` from the version `Program.cs`
    loads. An unconfigured hub makes bind throw, and `TryBindOrRequeue`'s existing path reports it
    (never a silent zero). This unblocks `ST5.4`.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BasicAttackGrant"`; `.\scripts\deploy-play.ps1 -NoServer -Paths <files>` (injector build); `.\scripts\guard-single-writer.ps1; .\scripts\guard-funnel-delta.ps1; .\scripts\guard-secondary-no-unity.ps1`
  - Files: `gk-core/src/FusionRpg.Core/Combat/BasicAttackGrantBuilder.cs`, `gk-core/tests/FusionRpg.Core.Tests/Combat/BasicAttackGrantBuilderTests.cs`, `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs`, `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs`

- [x] **AE2.3 — Record-then-drain `Θ` refresh for live grants** · M · deps: AE2.2 · *(spec: lawn-action-base, §Refresh triggers)*
  - Acceptance: `ApplyPowerSnapshot` makes one call, `MarkThetaDirty()`, which is lock-protected and
    O(1) and makes **no** grant call. The next main-thread `Tick` re-runs `Bind(ptr)` for every live
    grant it owns (enumerated as `WithdrawAllBound` does).
  - Acceptance: there is one test per trigger row: spawn binds; session start, reconnect,
    `power.index.reload` and an identity change each dirty the binder so the next drain rebinds to the
    new `Θ`; the off-switch leaves nothing to rebind. Bind→snapshot, snapshot→bind and
    snapshot-between-queue-and-drain all give the same amount.
  - Acceptance: two dirty drains in a row leave exactly one grant per ptr with the same amount
    (idempotent).
  - Verify: `dotnet test tests\FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnBasicAttackGrantBinder"` (needs interop refs; not in CI); `.\scripts\deploy-play.ps1 -NoServer -Paths <files>`
  - Files: `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `tests/FusionRpg.Injector.Tests/Effects/LawnBasicAttackGrantBinderRefreshTests.cs` (new)

- [x] **AE2.4 — Live probe: the lawn hit follows the action base and `Θ`** · S · deps: AE2.3, AE1.5 · *(spec: lawn-action-base, Live probe)*
  - Acceptance: the full suite runs green first (`test-fast.ps1 -AllDefault`; the AGENTS.md "before a
    live probe" point). Then read the commander's `Θ` through the RPG Server's **normal** query path.
    A real lawn hit's delta in real injector telemetry must equal `BasePerHit(base, P(Θ))` before defense.
  - Acceptance: change `Θ` through the real progression path (never a debug-fabricated value). Without
    a respawn, the next hit must follow. The evidence note names the scope (RPG Server for `Θ`, Game
    Injector for the hit) and quotes the decisive lines.
  - Verify: `.\scripts\deploy-play.ps1 -NoServer -Paths <files>` (server via `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`), then the probe per `docs/contributing/live-probe-standard.md`
  - Files: `docs/research/action-enrich/live-probe-<date>.md` (new, the evidence)

### Checkpoint 2 — the lawn reads the action (with Checkpoint 1, closes parent CC3)
- [x] For the same action at the same `Θ`, the lawn rider amount equals the battle base (the parity
  test), and the Hub-parity planted test is green.
- [x] Every trigger row is tested, and no grant call happens off the main thread.
- [x] An instakill hit does not ride the rider, and unrelated plain-amount riders are unchanged.
- [x] The live probe has passed and its evidence is committed. `ST5.4` (the `action-base` guard row) is
  green once it lands.
- [x] Named and not built here: the switch-on mid-match key-set gap (reported to `lawn-combat-wire`),
  and the zombie-side `Θ` trigger row (written with `SE` save-identity's build).
