# Spec: `lawn-combat-baseline` (lawn-tuning-profile module 4)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) · **Ideal:**
[lawn-tuning-profile-ideal.md](../lawn-tuning-profile-ideal.md) (§"Wiring gap" row *Combat baseline on
the lawn*; §"The shape" piece 5 `combatBaseline`) ·
**Depends on:** [`mode-profile`](spec-mode-profile.md) · **Unblocks:**
[`species-flavour-lawn`](spec-species-flavour-lawn.md), [`lawn-scale-live-proof`](spec-lawn-scale-live-proof.md) ·
**Authored by:** backlog-clean-up **BCU2.3** (`orphan-plan-authoring`) ·
**Implementation home:** `lawn-tuning-profile`, scheduled once in the backlog-clean-up **lawn plan**
(BCU2.4). ·
**Consumer, not owner:** [combat-ai](../combat-ai-map.md) lists this spec as a prerequisite only. ·
**Status:** spec, 2026-09-20. Not built.

## Objective

A lawn hit is decided by a contest between the attacker's accuracy and the defender's dodge, run
through the same sigmoid battle uses. On the lawn **both sides of that contest are zero**, so every
lawn hit is a coin flip — and so is every lawn crit.

The mechanism exists and is shipped. `BattleBaselineSubsystem`
(`gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/BattleBaselineSubsystem.cs:20`) is a registered
`IActorStatSubsystem` that seeds `combat.defense.omni`, `combat.accuracy.omni`, `combat.dodge.omni`,
`combat.crit.rate.omni` and `combat.crit.resist.omni` from Θ (`:40-44`). It is registered in exactly
one place — `BattleHubCompose.cs:81`, battle's own compose — and
`ActorHubBootstrap.CreateDefault` (`gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs:141-182`), the
lawn's Hub (`gk-fusion/src/FusionRpg.Injector/CheatState.cs:49-81`), **never registers it**.

Every combat channel is registered with `DefaultValue 0`
(`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs:298-311`: `Register(new(entry.ChannelId,
DerivedComposeKind.FlatSum, 0, …))` for every entry in `AllCombatChannelEntries`). So on the lawn:

| Contest | Battle, with the baseline | Lawn, today |
|---|---|---|
| hit | `σ((220 + 26Θ − 26Θ)/100)` = `σ(2.2)` ≈ **0.90** | `σ((0 − 0)/100)` = `σ(0)` = **0.50** |
| crit | `σ((10Θ − (10Θ + 250))/100)` = `σ(−2.5)` ≈ **0.076** | `σ(0)` = **0.50** |

The coefficients are `BattleRuleset.BaseAccuracy/BaseDodge/BaseCritRate/BaseCritResist`
(`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:367-370`) and the parity arithmetic is quoted from that
file's own doc block (`:351-357`), which records the owner's rate targets and says they are *"locked by
BattleRateTests"*. The lawn reads them through `OverlayCombatCalculator`
(`gk-core/src/FusionRpg.Core/Combat/OverlayCombatCalculator.cs:160-165`), which contests the same channel ids
via `ElementalResolver.Contest` → `CombatProbability.Sigmoid`
(`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8-9`).

**The miss half was measured; the crit half is worse and was not.** `lawn-tuning-profile-ideal.md:107`
records the wiring gap as *"lawn actors sit at accuracy 0 vs dodge 0, so `pHit = Sigmoid(0)` = 0.5 and
untuned riders miss half the time (L-N7, measured 3 misses of 13)"*, and the map's module row
(`lawn-tuning-profile-map.md:77`) repeats it. Reading the same four lines through `OverlayCombatCalculator`
shows the crit contest is zeroed identically: **a lawn actor crits ~50% of the time where battle's own
locked target is 5–10%.** This spec closes both with one registration, and the map row is corrected to
say so.

This module ships **the wiring and nothing else**. It moves no coefficient and invents no lawn
accuracy curve: the lawn adopts battle parity, because hit chance is a battle **mechanism** with one
implementation (`battle-engine-ssot.md` §1 rule 2, and its own named anti-example
*"Siege needs a hit-chance estimate, so `SiegeHitChance` implements the sigmoid contest"*).

## Tech stack

`FusionRpg.Core` (one new opt-in delegate arm on `ActorHubBootstrap.CreateDefault`; the `ModeProfile`
record gains one flag), `FusionRpg.Injector` (`CheatState.ActorHub` passes the arm),
`data/tuning/mode-profiles.v1.json` (new; does not exist yet — owned by
[`mode-profile`](spec-mode-profile.md), which is specced but not built; this module adds
one key to the lawn row). No new dependency, no new subsystem, no new channel.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActorHub|ModeProfile|BattleBaseline|OverlayCombat"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleRate"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ActorHub|Golden"
python gk-core/scripts/guard-actor-hub.py
python gk-fusion/scripts/guard-single-writer.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/tools/tuning/publish.py mode-profiles modes.lawn.combatBaseline=true
```

## Project structure

| What | Where |
|---|---|
| One more opt-in delegate arm on `CreateDefault` | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs:141-182` (changed) |
| The mode row's flag | `src/FusionRpg.Core/Stats/Derived/ModeProfile.cs` (new; does not exist yet — `mode-profile`'s file) |
| The lawn Hub passes the arm | `gk-fusion/src/FusionRpg.Injector/CheatState.cs:49-81` (changed) |
| Battle's own registration, **unchanged** | `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:81` |
| The tuning key | `data/tuning/mode-profiles.v1.json` (new; does not exist yet — `mode-profile`'s file) |
| Tests | `tests/FusionRpg.Core.Tests/Stats/LawnCombatBaselineTests.cs` (new; does not exist yet) |

## The shape

### 1. One more arm on the one bootstrap — not a second registration site

`ActorHubBootstrap.CreateDefault` already carries four optional per-context delegates that register a
subsystem only when supplied — `starLoyalty`, `boundDerivedAtoms`, `statusDerivedMods`, `draughts`,
`expeditionInjuries` (`ActorHub.cs:147-150`, `:156-181`), each with the same stated reason: *"Opt-in,
so bare CreateDefault callers are unaffected"* (`:159-160`). This adds a fifth of exactly that shape:

```csharp
/// <param name="combatBaseline">
/// lawn-combat-baseline: supplies (Θ, defense) for <see cref="Subsystems.BattleBaselineSubsystem"/>.
/// Opt-in for the same reason every arm above is: omitting it registers nothing, so the hundreds of
/// bare CreateDefault() callers are unaffected. Battle does NOT pass this — BattleHubCompose
/// registers the subsystem itself (BattleHubCompose.cs:81) because its seed closes over
/// setup.Defense, and passing it here as well would register the same subsystem twice.
/// </param>
Func<StatContext, (int Theta, long Defense)>? combatBaseline = null
```

registering `new BattleBaselineSubsystem(combatBaseline, registry)` when non-null, at the same point
in the method as the other opt-ins.

**Battle stays exactly as it is.** `BattleHubCompose` calls `CreateDefault(...)` and then registers
its own four (`BattleHubCompose.cs:64-84`), closing over `setup.Defense`, a value `CreateDefault`
cannot see. Moving that onto the new arm would move nothing and would risk a double registration for
no gain; the mode-profile boundary already says *"the battle row is the identity"*
([spec-mode-profile.md](spec-mode-profile.md) §Boundaries). A test asserts the subsystem appears
**exactly once** on a battle Hub.

### 2. The lawn's seed: Θ from the one provider, defense **zero**, and that is a ruling

The injector passes:

```csharp
combatBaseline: modeProfile.CombatBaseline ? (ctx => (PowerIndex.ActorIndex(ctx), 0L)) : null
```

Θ comes from the Hub's own `IPowerIndexProvider` — the same `InjectorPowerIndexProvider` already
handed to `CreateDefault` (`CheatState.cs:50`), keyed by player id
(`HydratedPowerIndexProvider.Key`, `gk-core/src/FusionRpg.Core/Power/IPowerIndexProvider.cs:74`). No second Θ
source, no `f(level)`.

**The defense term is `0` on the lawn deliberately, and the reason is PS-3, not laziness.**
`BattleBaselineSubsystem` seeds five channels from two inputs, and those two inputs are on opposite
sides of the power ladder:

- The four accuracy-family seeds read **Θ directly**. `BattleModels.cs:358-362`, in its own words:
  *"these four read Θ **directly** (PS-3: contests read Θ, magnitudes read P(Θ)), never through
  `PowerLadder`/`ChannelLadder`. Under B>0 both accuracy and dodge would grow quadratically, and so
  would their difference — the only thing the sigmoid sees — turning a fixed one-index gap into a
  dial-dependent blowout."* A contest term is **scale-free**: it is fed to a sigmoid as a difference,
  so it is safe on an actor whose base values are vanilla PvZ's.
- `BattleRuleset.BaseDefense(level)` reads **the ladder** — `(_defenseLadder ??=
  ChannelLadderFor("defense")).Value(level)` (`BattleModels.cs:340`), and the same doc block names it
  as one of *"the only three that may touch the ladder"*. It is a **magnitude**. Seeding a
  ladder-scale defense onto a lawn actor whose incoming damage is vanilla-scale is **M1's exact
  shape** — the defect this whole program exists to fix, whose attack half the owner already ruled a
  bug and removed from `EntityStatWriter` (`lawn-tuning-profile-ideal.md:130-136`).

So the lawn takes the contest half and declines the magnitude half. Its `combat.defense.omni` keeps
coming from the RPG contributions it already has (aptitudes, atoms, statuses), untouched by this
module. Sizing a lawn defense baseline is `base-relative-read`'s and `lawn-resource-scale`'s question,
behind their own modules.

`0L` is not a silent skip. `BattleBaselineSubsystem` emits every seed as `value − DefaultOf(channel)`
(`:40-44`), and `DefaultOf` reads the registry (`:47-48`), which is `0` for combat channels
(`DerivedStatRegistry.cs:308-310`) — so the lawn's defense contribution is a real, visible
`DerivedModifier` of `0` carrying SourceId `rpg.battle.base`. An honest zero on the sheet beats an
absent row, because the sheet can then say *the baseline ran and contributed nothing here*.

### 3. SourceId stays `rpg.battle.base`

`ContributionSourceIds.BattleBaseline = "rpg.battle.base"`
(`gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs:17`). The name is the **mechanism's**, not
the mode's — one subsystem, one GG-49 provenance id, on every Hub that registers it. Minting
`rpg.lawn.base` for the same code would be a second id for one contribution, which is exactly what the
SourceId grammar exists to prevent (`actor-hub-ssot.md` §8.1). The `_meta` note on the lawn row says
so, so nobody "fixes" the name later.

### 4. What actually moves on the lawn

Because `HydratedPowerIndexProvider.Key(ctx)` is the player id alone (`IPowerIndexProvider.cs:74`),
**both lawn sides resolve the same Θ today** — the fix recorded at `:69-73` after L-N38, where a key
that included side and type id left every zombie and every non-zero-type plant at Θ = 0. Equal Θ on
both sides means the contest lands on **exactly battle parity**:

| | before | after |
|---|---|---|
| lawn P(hit) | 0.50 | `σ(2.2)` ≈ **0.90** |
| lawn P(crit) | 0.50 | `σ(−2.5)` ≈ **0.076** |
| lawn `combat.defense.omni` | unchanged | unchanged |

0.90 and 5–10% are `decisions.md`'s own Combat resolution SSOT targets, quoted in
`BattleModels.cs:352-355`. The lawn is not being given a new number; it is being given the one that
already exists.

**Coupling to [`zombie-power-source`](spec-zombie-power-source.md), stated so the two are sized
together:** that module gives the zombie side `Θ_player + thetaOffset`. The moment the offset is
non-zero the two sides' Θ differ, and the contest moves by `26 × offset` accuracy points per Θ —
`σ((220 + 26·Θ_a − 26·Θ_d)/100)`. At `thetaOffset = 1` the zombie's attack lands at `σ(2.46)` ≈ 0.921
and the plant's at `σ(1.94)` ≈ 0.874. That is a real balance consequence of a number that currently
ships at `0`, and it belongs in `lawn-scale-live-proof`'s measured set rather than in either module's
head.

## Tunables

One key, in `mode-profile`'s file (`data/tuning/mode-profiles.v1.json`), published `v{n+1}` through
`gk-core/tools/tuning/publish.py` — never hand-edited (`tunables-ssot.md`).

| Key | Unit | Battle row | Lawn row | Why |
|---|---|---|---|---|
| `modes.<m>.combatBaseline` | bool | **`false`** | `true` | Whether the **Hub** registers `BattleBaselineSubsystem` for this mode. `false` on the battle row does **not** mean battle has no baseline — battle registers it itself at `BattleHubCompose.cs:81` with its own `setup.Defense` seed. The `_meta` note says exactly that, because the row reads backwards otherwise. |

No coefficient is added or moved. `BaseAccuracy`'s `220`/`26`, `BaseCritRate`'s `10` and
`BaseCritResist`'s `250` stay in `BattleModels.cs:367-370` where `BattleRateTests` locks them: they are
`battle-rates`' own calibration, and the lawn deliberately adopts them rather than forking a lawn
accuracy curve.

## Code style

- The new parameter's doc comment carries the two things that are not obvious at the call site: that
  it is opt-in like its four neighbours, and that battle must **not** pass it. Both are written where
  the next reader will be (`ActorHub.cs`), not only here.
- The lawn's seed lambda carries the PS-3 reason for `0L` inline, one sentence, citing
  `BattleModels.cs:340` vs `:358-362`. A bare `0` there reads as an oversight to every future reader,
  and this repo has paid for exactly that class of silent zero before
  (`lawn-tuning-profile-ideal.md:104`, the `seedResourceBaseline` gap: *"`resource.max.*`/
  `resource.regen.*` resolved to 0 for every lawn actor — indistinguishable from this whole feature's
  own bug"*).
- Θ is an `int` and the defense term a `long`, matching `BattleBaselineSubsystem`'s own tuple
  (`:22`, `:38`). Nothing is multiplied here, so no widening question arises.

## Testing strategy

Contract assertions (`validation-ssot.md`). No population count, no generated text, no per-run outcome.

- ✅ **The defect, asserted before the fix and inverted after it:** a Hub built the way the lawn builds
  it resolves `combat.accuracy.omni` and `combat.dodge.omni` equal, so `ElementalResolver.Contest` of
  the pair returns `0.5`; with `combatBaseline` on, the same pair returns the battle-parity value.
  Asserted as **"the lawn's contest equals the battle Hub's contest at the same Θ"** — a parity
  property between two composes, not a pinned float. That is the honest form: the target is *"the same
  as battle"*, and pinning `0.90` would re-encode a coefficient `BattleRateTests` already owns.
- ✅ Same parity assertion for the crit contest.
- ✅ `combat.defense.omni` on a lawn-shaped Hub is **unchanged** by turning the flag on — the zero-seed
  property, which is the whole defense ruling in one test.
- ✅ The contribution carries SourceId `rpg.battle.base` and is attributable on the snapshot.
- ✅ `CreateDefault` with no `combatBaseline` composes bit-identically to today — the opt-in property,
  asserted, not assumed (the same shape `mode-profile`'s own identity test uses).
- ✅ A battle Hub registers `BattleBaselineSubsystem` **exactly once** (the double-registration guard).
- ✅ `modes.battle.combatBaseline` is `false` in the shipped file, and a test states the reason in its
  name so the row is never "corrected" to `true`.
- ❌ Never asserts a hit or crit *outcome*, a miss count, or how many riders hit in N records. "3
  misses in 13" is a **reading** that motivated the work; it is not a criterion.

**Golden impact: byte-identical.** Battle's compose is untouched (it never passes the new arm), delve
and siege compose through Hub without it, and the lawn has no golden
(`docs/research/combat-ai/S4-lawn.md:65-68`). **If a golden moves, this module is wrong** — that is
the acceptance, not something to re-bless. This is an argument from code, not a measurement: no suite
was run in this spec session.

## Boundaries

- **Always:** register through the one Hub's opt-in seam; seed the four contest channels from Θ and
  the defense term from nothing; keep the SourceId; default to today's behaviour when the flag is
  absent (`mode-profile`'s missing-row fallback).
- **Ask first:** enabling `combatProfile.minChipShareKPm` on the lawn — a sibling knob in the same
  ideal section, and `lawn-tuning-profile-ideal.md`'s tunable table already marks it *"enabling on the
  lawn is ask-first"*. This module does not touch it.
- **Never:** seed the lawn's defense from `BattleRuleset.BaseDefense` (M1's shape); add a lawn-only
  accuracy formula or coefficient (`battle-engine-ssot.md` §1 rule 2 — one implementation per
  mechanism); register the subsystem a second time anywhere; mint a per-mode SourceId; write the
  accuracy channels from the injector (`guard-single-writer.py`, and the RPG layer contributes
  through Hub, never a private fold).

## battle-engine-ssot §5 — the six answers

| | Question | Answer |
|---|---|---|
| 1 | Which responsibility (§3), or is it new? | **Existing — combat resolution's accuracy/crit contest baseline.** Nothing is added to the register. The subsystem, the coefficients and the sigmoid all already exist and are already the engine's. |
| 2 | Does it DECIDE or RESOLVE? | **RESOLVE.** These are the numbers the engine resolves a hit with. This module changes *which modes are given them*, never how they are computed and never who chooses a target. |
| 3 | Mechanism or loop? | **Mechanism**, and that is the whole point. Hit chance has one implementation (`BattleRuleset.BaseAccuracy/BaseDodge` → `CombatProbability.Sigmoid`). The lawn was missing the *inputs*, and the wrong fix — a lawn hit-chance of its own — is the precise anti-example §1's law names. |
| 4 | Which existing implementation does it extend? | `BattleBaselineSubsystem` (`BattleBaselineSubsystem.cs:20`) via `ActorHubBootstrap.CreateDefault`'s established opt-in delegate seam (`ActorHub.cs:147-150`). Nothing is copied; no number is estimated privately. |
| 5 | Does every mode get it? | **Yes.** Battle has it (`BattleHubCompose.cs:81`); the lawn gains it here; delve and siege compose through Hub since the 2026-09-13 fusion and can take the same arm from their own mode rows with no new code. There is no "only on the lawn" claim to refuse. |
| 6 | Is it deterministic and seeded? | **Yes.** The contribution is a pure function of Θ — no clock, no ambient state, no RNG. The roll stays `CombatProbability.RollSuccess`'s injected `ICombatRng` (`CombatProbability.cs:11-16`), unchanged. `Math.Exp` is in the sigmoid, so the platform stamp caveat is `BattleEnvironment.Stamp`'s, already established and unaffected. |

**And the rule that is not a question:** the lawn calls the mechanism. It does not re-implement it,
does not estimate it, and does not decide a battle number itself.

## Success criteria

1. `ActorHubBootstrap.CreateDefault` takes an optional `combatBaseline` arm; bare callers unchanged.
2. `modes.lawn.combatBaseline = true` ships in `mode-profiles.v1.json` with the `_meta` sentence
   explaining the battle row's `false`.
3. A lawn-shaped Hub's accuracy and crit contests equal a battle Hub's at the same Θ.
4. A lawn-shaped Hub's `combat.defense.omni` is unchanged by the flag.
5. `BattleBaselineSubsystem` is registered exactly once per Hub, on every path.
6. Every golden and every existing test is byte-identical.
7. `guard-actor-hub.py` and `guard-single-writer.py` green.
8. The live measurement — lawn P(hit) and P(crit) at parity on a real board — is
   [`lawn-scale-live-proof`](spec-lawn-scale-live-proof.md)'s, read back through overlay telemetry on a
   real match, not from a debug response (`live-probe-standard.md`).

## Open questions

1. **Does the lawn want battle's *rates*, or only battle's *mechanism*?** This spec takes both: the
   lawn adopts `BaseAccuracy`/`BaseDodge` unchanged, so a lawn hit lands at 0.90 like a battle hit.
   **Options:** (a) adopt battle's rates, as specced; (b) give the lawn row its own accuracy
   coefficients, which would be a second calibration of one mechanism and needs its own justification.
   **Recommended default: (a)** — a rate difference between two places that share one engine is a
   balance claim nobody has made, and if the lawn later wants one it is a `familyScaleMilli`-shaped
   dial on the same channels, not a second formula.
2. **Cross-module note:** the map row and `lawn-tuning-profile-ideal.md:107` both describe this gap as
   a *hit* problem only. The crit half is the same zero and is further from its target in relative
   terms. Correcting those two lines is paperwork this spec's implementing task should carry, and it
   is named here rather than edited, because both files are outside this spec's write scope.

## Design gate checklist (DESIGN-GATE §5)

```
[x] Subsystems identified: Stats/ActorHub compose, battle combat resolution, lawn tuning profile.
[x] Session boundary: backlog-clean-up-20260920. This spec writes one new file under
    docs/architecture/lawn-tuning-profile/ and edits nothing else.
[~] §1 rows read this session: Stats / actor-hub (via actor-hub-ssot's SourceId grammar as restated in
    DESIGN-GATE §1 and CLAUDE.md's one-compose rule), battle-engine-ssot §1/§2/§5 (read in full),
    power/PS-3 (read in BattleModels.cs's own doc block and ssot-power-scale §11), tunables-ssot (as
    restated in CLAUDE.md and enforced by publish.py's header), validation-ssot (as restated).
    GAP: actor-hub-ssot.md §8.1 and stat-system.md were not opened in this session; the SourceId claim
    rests on ContributionSourceIds.cs:17 and the DESIGN-GATE §1 Stats row, both of which I did read.
[x] decisions.md checked: the "Combat resolution SSOT" targets are quoted through BattleModels.cs's own
    doc block (:352-355), which names decisions.md as their source. No lock conflicts.
[x] Every factual claim cites file:line, and every file cited was opened this session.
[x] audit-doc-citations.py --scope <this file> --strict: 0 HIGH findings, exit 0. The 2 remaining
    D1 (LOW) are mode-profile's own files, which that spec creates and which are marked
    "new; does not exist yet" here.
[x] Verified against CODE, not comments: the "never registered" claim comes from reading
    CreateDefault's body (ActorHub.cs:141-182) and finding the only Register call at
    BattleHubCompose.cs:81; the zero default from DerivedStatRegistry.cs:298-311, not from a comment.
[x] I read the surrounding section of every rule quoted (BattleModels.cs:351-370 in full before
    claiming the four read Θ directly and BaseDefense does not).
[~] I tested (not assumed) the constraints I report. NOT RUN: no build or suite was executed this
    session (the brief forbids it). The "byte-identical goldens" claim is argued from the opt-in
    seam's own established property, not measured; the parity arithmetic is computed from the
    coefficients at BattleModels.cs:367-370 and matches that file's own worked example at :352-355.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated: the crit half is named as an omission in the map row and the ideal, and
    listed as paperwork for the implementing task rather than silently left.
[x] No assertion pins a derived population count or generated text. The tests assert a PARITY
    property between two composes rather than the literal 0.90/0.076, so a future BattleRateTests
    recalibration moves one place, not two.
[x] Event-refreshed cache (§2.16): none introduced. The Θ read goes through the existing
    InjectorPowerIndexProvider, whose own trigger set (ApplyPowerSnapshot, CheatState.cs:251-262) is
    unchanged by this module.
[x] No acceptance criterion fixes an ordering that can vary in real play.
[x] Actor combat/derived magnitude: YES, and it contributes through ActorHub via an already-registered
    IActorStatSubsystem with a non-empty ContributionSourceIds id (rpg.battle.base). No private fold,
    no second composer, no new channel.
[x] Does not invent or extend a SOLID-violating parallel path: it removes a mode-ownership gap rather
    than forking the mechanism.
[x] New rule has a registry row: none needed — this module adds no rule, only a registration. The
    "exactly once" property is covered by a test rather than a guard, which is the appropriate
    instrument for a single call site.
```
