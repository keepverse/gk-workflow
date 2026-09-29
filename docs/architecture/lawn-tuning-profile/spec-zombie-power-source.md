# Spec: `zombie-power-source` (lawn-tuning-profile module 5)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) · **Ideal:**
[lawn-tuning-profile-ideal.md](../lawn-tuning-profile-ideal.md) (defect **M5**; owner **ruling 1**,
2026-09-16, and its ⭐ sharpening the same day) ·
**Depends on:** [`mode-profile`](spec-mode-profile.md) · **Unblocks:**
[`species-flavour-lawn`](spec-species-flavour-lawn.md), [`lawn-scale-live-proof`](spec-lawn-scale-live-proof.md) ·
**Named external dependency:** `empire-progression`
[`ai-empire-species`](../empire-progression/spec-ai-empire-species.md) for the species layer (spec,
not reviewed, no build authorized — `spec-ai-empire-species.md:8-9`) ·
**Authored by:** backlog-clean-up **BCU2.3** (`orphan-plan-authoring`) ·
**Implementation home:** `lawn-tuning-profile`, scheduled once in the backlog-clean-up **lawn plan**
(BCU2.4). ·
**Consumer, not owner:** [combat-ai](../combat-ai-map.md) lists this spec as a prerequisite only. ·
**Status:** spec, 2026-09-20. Not built.

## Objective

Owner **ruling 1** (`lawn-tuning-profile-map.md:46-55`): *"Lawn zombies carry Zomboss's build at the
player's Θ plus a tunable offset."* Sharpened the same day against `actor-layer-compose-ideal.md`:
*"'Zomboss's build' is his **EMPIRE SPECIES PROGRESSION**, not his commander build. A lawn zombie reads
the empire that owns the species — Zomboss — through the same `AllocationScope.CreatureType` layer a
plant reads from the player's empire. His commander build stays a commander aura, a different layer."*

**This module is wiring, and the first thing it owes is a correction: M5's headline is already fixed,
and its remaining half has the opposite sign.**

M5 is recorded as *"the player's Might makes enemy zombies hit harder"*
(`lawn-tuning-profile-ideal.md:171-175`, `lawn-tuning-profile-map.md:68`, both citing
`CheatState.cs:186`). That was true when it was written. It is not true in the code now.
`solid-remediation` T4.1 (S1/S3) put the empire into the resolve:

```csharp
// gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs:106
var empire = SpeciesAllocation.EmpireForSide(ctx.Side);
// :114-116
var commander = empire == Commanders.EmpireId.Dave
    ? _resolveCommanderAllocation(ctx.PlayerId)
    : AptitudeAllocation.Empty;
```

with the file's own note at `:108-113` naming the defect it closed: *"a lawn zombie merged the HUMAN
PLAYER's commander allocation … Zomboss's empire has no commander allocation on the lawn yet, so a
zombie resolves empty rather than someone else's — strictly more correct than the wrong empire's, and
the point at which Zomboss's own allocation lands is the point this stops being empty."* The species
half is gated the same way: the injector cache answers a non-Dave empire with `Empty`
(`gk-fusion/src/FusionRpg.Injector/CheatState.cs:182-185`), and so would the server
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:238-242`: *"the species LEVEL row is per-player, and
no Zomboss species level exists anywhere"*).

**So the live defect today is that a lawn zombie carries no RPG build at all — both layers resolve
`Empty`.** The player's Might no longer leaks; nothing replaced it. This module is *"the point at
which Zomboss's own allocation lands"*, and it is a wiring job because every piece it needs is built
and inert:

| Piece | Built | Lawn callers today |
|---|---|---|
| `ZombossCommanderAllocation` — Zomboss's pattern → an `AptitudeAllocation` through the same `PointBudget` a commander uses | `gk-core/src/FusionRpg.Core/Battle/Ai/ZombossCommanderAllocation.cs:15-61` | **Zero.** Its one production caller is `WebMatchService.ApplyZombossPattern` (`gk-core/src/FusionRpg.Server/WebMatchService.cs:505-510`), the web-battle path. |
| The per-match pattern selector | `RpgStore.SelectZombossPattern` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossAdaptive.cs:47`) | Zero on the lawn; used by `ApplyZombossPattern` (`WebMatchService.cs:501`). |
| The empire axis in the resolve | `SpeciesAllocationSource.cs:106,114-116`; `SpeciesAllocation.EmpireForSide` | Live — and it is what makes the zombie answer `Empty` rather than wrong. |
| Θ per actor | `HydratedPowerIndexProvider`, keyed by player id (`gk-core/src/FusionRpg.Core/Power/IPowerIndexProvider.cs:44-75`) | Live. Both lawn sides read the **same** Θ; there is no per-side term and no offset. |

## Tech stack

`FusionRpg.Core` (one delegate widening, one `IPowerIndexProvider` decorator, `ModeProfile` rows),
`FusionRpg.Injector` (`CheatState` wiring + one cache), `FusionRpg.Server` (one field on an existing
response), `data/tuning/mode-profiles.v1.json` (new; does not exist yet — owned by
[`mode-profile`](spec-mode-profile.md), which is specced but not built). No
new dependency, no new endpoint, no new table.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocation|ZombossCommanderAllocation|PowerIndex|ModeProfile"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ChannelModsHubParity"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ActorHub|Golden"
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/tools/tuning/publish.py mode-profiles modes.lawn.theta.zombie.thetaOffset=0
```

## Project structure

| What | Where |
|---|---|
| `resolveCommanderAllocation` widens to take the empire | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs:36,55-58,72-89,114-116` (changed) |
| Per-side Θ offset, as a decorator | `src/FusionRpg.Core/Power/SideThetaOffsetPowerIndexProvider.cs` (new; does not exist yet) |
| The mode row's `theta` / `allocation` blocks | `src/FusionRpg.Core/Stats/Derived/ModeProfile.cs` (new; does not exist yet — `mode-profile`'s file) |
| Zomboss's lawn allocation cache, beside the commander one | `gk-fusion/src/FusionRpg.Injector/CheatState.cs:88-95, 174-190` (changed) |
| The wiring that picks a source per empire | `gk-fusion/src/FusionRpg.Injector/CheatState.cs:186` (changed) |
| The pattern id on the existing refresh response | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:23` (changed) and its client parse in `RpgClient.RefreshCommanderAllocationAsync` (changed) |
| Tests | `tests/FusionRpg.Core.Tests/Stats/ZombieAllocationSourceTests.cs`, `tests/FusionRpg.Core.Power.Tests/Power/SideThetaOffsetTests.cs` (both new; do not exist yet) |

## The shape

Three independent pieces. Each is a seam that exists.

### 1. Θ per side — a decorator, never a key change

Ruling 1 is `Θ_zombie = Θ_player + thetaOffset`. `HydratedPowerIndexProvider.Key(ctx)` is
`(ctx.PlayerId ?? 0)` and **must stay that way** — `IPowerIndexProvider.cs:69-73` records why the key
lost its side and type-id terms: *"a player-level hydration then reached only plants whose type id is
0, and every other lawn plant and every zombie read Θ = 0"* (L-N38, found 2026-09-16). Re-adding a
side term to the key would reintroduce exactly that miss.

So the offset is applied **outside** the lookup:

```csharp
/// <summary>
/// lawn-tuning-profile ruling 1: the zombie side's Θ is the player's Θ plus a per-mode offset.
/// A DECORATOR, never a second ladder — Θ stays the one index (ssot-power-scale.md §10), and an
/// offset is a Θ SHIFT, the same shape the delve's `θ_enemy = Θ_room + thetaOffset` and the threat
/// rung already use. There is no f(level) here and nothing reads summonLevel (R-LT2's hard
/// requirement: `summonLevel` may supply a rung, never a private curve).
/// </summary>
public sealed class SideThetaOffsetPowerIndexProvider : IPowerIndexProvider
{
    public SideThetaOffsetPowerIndexProvider(IPowerIndexProvider inner, int zombieOffset);
    public int ActorIndex(StatContext ctx);            // inner + offset when ctx.Side == Zombie
    public int ContentIndex(ContentContext ctx);       // delegated unchanged
    public PowerAxisReport Explain(StatContext ctx);   // inner's report + one named contribution
}
```

Three properties it must hold:

- **`Explain` shows the offset.** It appends a named `PowerAxisContribution` rather than silently
  adjusting `Total`. A Θ that cannot be explained on a sheet is the shape of bug
  `derived-audit-actor` exists to catch.
- **The add is `checked`.** Θ and the offset are both `int`; the sum is far inside `int` range at any
  reachable Θ, but an integer add on a magnitude axis throws rather than wraps (CLAUDE.md numeric
  rule 3).
- **The result floors at 0.** `P(Θ)` is not defined below the ladder's domain, so a large negative
  offset must not produce a negative index. Flooring is **structural** — the ladder's own domain, not
  a progression ceiling — and carries that comment, matching the precedent already in the tree
  (`ResourceBaselineSubsystem` uses `Θ = max(1, ActorIndex)`, `lawn-tuning-profile-ideal.md:94`).

The injector wraps its existing provider when the lawn row sets a non-zero offset; at the shipped `0`
the decorator is the identity and can be skipped entirely, so nothing changes until a balance pass
moves the number.

### 2. Allocation per empire — move the empire test out of the resolver

`SpeciesAllocationSource` currently hard-codes which empire may have a commander allocation
(`:114-116`, `empire == Commanders.EmpireId.Dave`). That is a **per-empire policy living inside a Core
resolver** — the resolver deciding a question its host should answer (SOLID D). The delegate widens by
one argument and the branch disappears:

```csharp
// before: Func<long?, AptitudeAllocation> resolveCommanderAllocation
// after:  Func<Commanders.EmpireId, long?, AptitudeAllocation> resolveCommanderAllocation
var commander = _resolveCommanderAllocation(empire, ctx.PlayerId);
```

The resolver keeps doing exactly what it already documents — *"Commander and species points merge into
ONE `AptitudeAllocation` (`operator+`), resolved once by the caller"* (`:22-25`) — and **which**
allocation an empire gets becomes the host's, where the mode row already lives. Behaviour for Dave is
identical. Behaviour for Zomboss is `Empty` until step 3 supplies a source, so this widening lands
**behaviour-neutral, in its own commit**, and the wiring follows.

The injector then reads the mode row:

| `modes.lawn.allocation.<side>` | Delegate returns |
|---|---|
| `commander` | `CheatState.CommanderAllocation.Resolve(...)` — today's line (`CheatState.cs:186`) |
| `zombossCommander` | the Zomboss cache below |
| `none` | `AptitudeAllocation.Empty` |

The lawn row ships `plant: commander`, `zombie: zombossCommander` — the ideal's own tunable table
(`lawn-tuning-profile-ideal.md:492`).

### 3. Zomboss's lawn cache — the second production caller of a type built for it

Beside `CheatState.CommanderAllocation` (`CheatState.cs:88-95`), a `ZombossCommanderAllocation`
instance held at the same cadence. `ZombossCommanderAllocation`'s own doc says this is what it is
for: *"Mirrors `CommanderAllocationSource`'s own shape (T5) for Dave: a small cache the hot path
reads, refreshed explicitly rather than reading the tuning/Θ pipeline per stat resolve"*
(`ZombossCommanderAllocation.cs:9-13`). The hot path reads a field (`:58-60`); `Refresh(scope, theta,
tuning)` (`:51-56`) runs on an edge, never per resolve.

- **Scope is `AllocationScope.Commander`** — the same argument `WebMatchService.cs:506` passes, and
  the type's own doc insists it stay an argument rather than a constant (`:47-50`).
- **Θ passed to `Refresh` is `Θ_zombie`** (player Θ + offset), so Zomboss's point budget is the one
  the human commander spends from at the same index — `ApplyZombossPattern`'s own stated principle:
  *"a harder Zomboss is a higher Θ or a better allocation, never a stat nobody could have had"*
  (`WebMatchService.cs:488-492`).

**Transport: one field on the existing refresh, not a new endpoint.** `AptitudeEndpoints` has no
Zomboss route (`gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:23,29,57,64,96` are all player-scoped), and
`RpgClient.RefreshCommanderAllocationAsync` already parses two caches from one response — the
injector's own comment: *"extended to parse the SAME response's new `species` map alongside `shares`
— one fetch, both caches, never a second HTTP round trip"* (`CheatState.cs:192-196`). The same
response gains a `zomboss: { patternId }` block, chosen server-side by the **same**
`SelectZombossPattern(playerId, level, seed, tuning)` the web battle uses
(`RpgStore.ZombossAdaptive.cs:47`) — one selector, not a lawn-only second one.

**The refresh trigger set, enumerated in full (DESIGN-GATE §2.16).** This repo has paid three times
for a cache whose trigger set was copied from a cache with different key-set behaviour
(`CheatState.cs:98-102`, `RpgClient.cs:143-147`, and `unique-lawn-wire` AS-1.1 — DESIGN-GATE §4,
2026-09-13). This cache's value depends on **two** things that move independently, so both edges are
required:

| Trigger | Why it is in the set | Test |
|---|---|---|
| Session start | The cache is empty until something fills it | yes |
| Reconnect | The injector may have missed edges while disconnected | yes |
| `AptitudesUpdated` broadcast | The commander cache's existing edge; the response carries both | yes |
| **Match start** | The pattern is chosen per match (`SelectZombossPattern` takes a per-match seed). Without this edge every match after the first runs the previous match's pattern. This is the edge a copied trigger set would omit. | yes |
| **Θ revision** (`ApplyPowerSnapshot`, `CheatState.cs:251-262`) | `Refresh` takes Θ as an argument, so a Θ change invalidates the cached allocation. The commander cache does not need this edge; this one does. | yes |

Each trigger calls `Refresh` and then `Stats.Invalidate()`, exactly as `ApplyCommanderAllocation`
already does and for the stated reason (`CheatState.cs:100-106`: a reallocation *"changes what every
living entity resolves to"*).

### 4. The species layer is named, not invented

The ⭐ sharpening says Zomboss's build is his **empire species progression**
(`AllocationScope.CreatureType`). That layer's read already asks the right question — the injector
passes `(empire, speciesId)` (`CheatState.cs:182-185`) and the store's
`EffectiveSpeciesAllocationUnlocked` takes an `EmpireId` (`RpgStore.Aptitudes.cs:224-233`). It returns
`Empty` for a non-Dave empire because **no Zomboss species level row exists anywhere**
(`:238-242`), and creating somewhere to store one is `empire-progression`'s
[`ai-empire-species`](../empire-progression/spec-ai-empire-species.md), which states its own gap in the
same terms: *"the missing pieces are: **somewhere to store** a non-player empire's species level, **the
crediting rule** R1 fixes … and **the read** that stops returning Empty."*

**This module changes nothing on that path and builds no store for it.** It wires the commander/pattern
layer, which exists and is inert, and records that the ruling is fully satisfied only when
`ai-empire-species` lands. Inventing a Zomboss species-level table here would be a second carrier for
a layer that already has an owner — the "third carrier invented per feature is the defect" failure
DESIGN-GATE §1's actor-layer row names.

Stated as a table so the boundary is unambiguous:

| Layer | Carrier | Zomboss on the lawn today | After this module | Owner of the rest |
|---|---|---|---|---|
| Commander (his pattern / aura) | `resolveCommanderAllocation` | `Empty` (`SpeciesAllocationSource.cs:114-116`) | Zomboss's pattern at `Θ_zombie` | this module |
| Species / `CreatureType` | `resolveSpeciesAllocation(empire, speciesId)` | `Empty` (no Zomboss level row) | still `Empty` | `ai-empire-species` (R1) |
| Θ | `IPowerIndexProvider` | `Θ_player` | `Θ_player + thetaOffset` | this module |

## Tunables

In `mode-profile`'s file (`data/tuning/mode-profiles.v1.json`), published `v{n+1}` through
`gk-core/tools/tuning/publish.py` — never hand-edited.

| Key | Unit | Battle row | Lawn row | Why |
|---|---|---|---|---|
| `modes.<m>.theta.plant.source` | enum `player`/`content`/`fixed` | `player` | `player` | today's behaviour |
| `modes.<m>.theta.zombie.source` | enum | `content` | `player` | ruling 1 — the lawn tracks the player's level; the vanilla-PvZ content-Θ signal stays a separate unbuilt follow-up (`lawn-tuning-profile-ideal.md` §"What this deliberately does not decide") |
| `modes.<m>.theta.zombie.thetaOffset` | Θ (int) | 0 | **0, `UNMEASURED`** | ruling 1's own starting point. This is also where the later Zomboss "reflection" feature plugs in. A non-zero value moves the accuracy contest by `26 ×` offset — see [`lawn-combat-baseline`](spec-lawn-combat-baseline.md) §4. |
| `modes.<m>.allocation.plant` | enum `commander`/`zombossCommander`/`none` | `commander` | `commander` | — |
| `modes.<m>.allocation.zombie` | enum | `zombossCommander` | `zombossCommander` | ruling 1 |

The Θ floor at 0 is a **structural** bound (the ladder's domain) and carries that comment in code, not
in the tuning file.

Nothing here adds a coefficient, a curve or a per-species number. Ruling 2 is explicit that *"the lawn
profile holds **mode-level dials only** and never flattens or copies per-species numbers"*
(`lawn-tuning-profile-ideal.md:551-552`).

## Code style

- The decorator's doc comment states what it is **not** (a second ladder, an `f(summonLevel)`) as
  plainly as what it is. R-LT2 is a hard requirement with a named failure behind it
  (`ssot-power-scale.md` §10 — *"the exact defect that let three incompatible curves ship at once"*),
  and the next reader meets the class before they meet the ruling.
- The widened delegate keeps its parameter order (`empire, playerId`) matching
  `resolveSpeciesAllocation(empire, speciesId)`'s existing shape (`SpeciesAllocationSource.cs:36`), so
  the two read alike at the call site.
- The Zomboss cache is declared beside the commander cache, with its trigger set listed in its own doc
  comment — the same place `CommanderAllocationSource`'s is (`CheatState.cs:88-95`). A trigger set
  that lives only in a spec is a trigger set that gets copied wrong.
- No number in this module is a literal at a call site; the offset and the two selectors come from the
  mode row.

## Testing strategy

Contract assertions and closed vocabularies only (`validation-ssot.md`). Store-touching tests run in
memory (`guard-test-substrate.py`).

`SpeciesAllocationSource`:
- ✅ With a Dave-side ctx, the widened delegate is called with `EmpireId.Dave` and the merged result is
  **identical to today's** — the behaviour-neutral property of the widening commit, asserted.
- ✅ With a zombie-side ctx, the delegate is called with `EmpireId.Zomboss` (it is now called at all,
  which it never was before) and the host's answer is what merges.
- ✅ A host that returns `Empty` for Zomboss reproduces today's behaviour exactly — so the widening
  cannot silently change anything before the wiring lands.
- ✅ A Bound unique still takes absolute priority over the species lookup (`:118-124`), unchanged.

`SideThetaOffsetPowerIndexProvider`:
- ✅ Plant-side Θ is the inner provider's, unchanged.
- ✅ Zombie-side Θ is inner + offset; `Explain` names the offset as its own contribution.
- ✅ A negative offset larger than Θ floors at 0 rather than going negative.
- ✅ `ContentIndex` delegates untouched.
- ✅ At offset 0 the decorator is the identity on all three members.

Wiring:
- ✅ Each of the **five** triggers in the table refreshes the Zomboss cache — one test per trigger,
  named for the trigger, including **match start** and **Θ revision**. Not one test that exercises a
  convenient ordering.
- ✅ Two matches in a row select and apply **different** patterns when the seed differs, and the second
  match does not run the first's pattern (the match-start-edge property, stated as the thing that
  fails when the edge is missing).
- ✅ The mode-row enum is a **closed vocabulary**: an unknown `allocation` value is a refusal naming the
  value, never a silent fallback (`mode-profile`'s own rule 1).
- ❌ Never asserts a zombie's resolved attack, HP, or any composed magnitude — those are readings that
  move with every tuning publish. The assertions are about **which source answered**, not what it
  answered with.
- ❌ Never asserts the number of Zomboss patterns (`ZombossPatterns.All` is a population that content
  grows); the closed thing here is `AllocationScope`
  (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAllocation.cs:8`, four members) and the three-value
  allocation-source enum, and those may be pinned with the reason stated.

**Golden impact.** Battle is byte-identical: `ApplyZombossPattern` (`WebMatchService.cs:496-521`) is
untouched, `ZombossCommanderAllocation` gains a second caller rather than a changed body, and the
battle mode row is the identity. The `SpeciesAllocationSource` **signature** change touches every
caller and test that constructs one, which is a compile-level edit with no behavioural delta — that is
the reason it lands as its own commit, before any wiring. The lawn has no golden
(`docs/research/combat-ai/S4-lawn.md:65-68`). **If a battle golden moves, this module is wrong.** This
is an argument from code, not a measurement: no suite was run in this spec session.

## Boundaries

- **Always:** keep `HydratedPowerIndexProvider.Key` as the player id alone; apply the offset in a
  decorator; land the delegate widening behaviour-neutral in its own commit; refresh the Zomboss cache
  on all five edges; publish `v{n+1}`.
- **Ask first:** a non-zero `thetaOffset` — it is a difficulty change and a measured one
  (`lawn-scale-live-proof`), and the owner has already named the Zomboss "reflection" feature as the
  later home for reactive adjustment.
- **Never:** read `summonLevel` or any other field as a private `f(level)` — R-LT2 is explicit that
  *"`summonLevel` supplies a **rung**; the ladder supplies the magnitude"*, and this module needs no
  rung at all; invent a Zomboss species-level store (`ai-empire-species` owns it); add a Zomboss
  aptitude REST endpoint when an existing response already carries both caches; give the lawn a second
  pattern selector; compose a zombie anywhere but the one ActorHub.

## battle-engine-ssot §5 — the six answers

| | Question | Answer |
|---|---|---|
| 1 | Which responsibility (§3), or is it new? | **None, and not new.** This is the **actor layer stack's** source selection — which empire's allocation and which Θ an actor inherits (DESIGN-GATE §1 actor-layer row). It changes an *input* to compose, never a battle mechanism, so the §3 register is untouched. |
| 2 | Does it DECIDE or RESOLVE? | **Neither.** It is upstream of both: it determines what the Hub is handed before any turn or hit exists. |
| 3 | Mechanism or loop? | **One mechanism, wired per loop.** The allocation resolver, `PointBudget` and the power ladder are single implementations shared by battle and the lawn; the mode row picks which *source* each place reads. No formula is duplicated — that is the whole reason ruling 1's ⭐ sharpening says the model is *"the same layer, read from the other empire"*, and why `zombie-power-source` stopped being a zombie-side model of its own. |
| 4 | Which existing implementation does it extend? | `SpeciesAllocationSource` (one delegate widened), `ZombossCommanderAllocation` (`:15-61`, second production caller), `HydratedPowerIndexProvider` (decorated, not replaced), `RpgStore.SelectZombossPattern` (`:47`, reused). Nothing is copied and nothing is estimated privately. |
| 5 | Does every mode get it? | The **seam** is every mode's — the profile row exists for battle, delve, siege and sim too. The **values** are the lawn's, because battle already resolves Zomboss's pattern at `WebMatchService.cs:505` and its row is the identity. There is no "only on the lawn" mechanism here to refuse. |
| 6 | Is it deterministic and seeded? | **Yes.** The pattern is `SelectZombossPattern(playerId, level, seed, tuning)` — seeded, no clock. Θ is an integer add. `ZombossCommanderAllocation.Resolve` is a field read (`:58-60`). Nothing reads a wall clock or an unseeded RNG. |

**And the rule that is not a question:** the lawn calls the same allocation and ladder mechanisms
battle calls. It does not re-implement them and does not decide a battle number itself.

## Success criteria

1. `SpeciesAllocationSource.resolveCommanderAllocation` takes the empire; the `EmpireId.Dave` test is
   gone from the resolver body; Dave's behaviour is byte-identical.
2. A lawn zombie's composed allocation is Zomboss's pattern allocation, read back through
   `derived-audit-actor` on a real match against a real specimen — RPG Server Debug scope, and the
   change is read back through the normal query path, never from the call's own response
   (`live-probe-standard.md`).
3. `Θ_zombie = Θ_player + thetaOffset`, and `Explain` names the offset.
4. All five refresh triggers are covered by their own named tests, including match start and Θ revision.
5. `modes.lawn.allocation.zombie = zombossCommander` and `theta.zombie.thetaOffset = 0` ship in
   `mode-profiles.v1.json`, marked `UNMEASURED`.
6. The species layer is untouched and still resolves `Empty` for Zomboss, with
   `ai-empire-species` named in the code comment as its owner.
7. Battle goldens byte-identical; `guard-actor-hub.py` green.
8. `lawn-tuning-profile-map.md:68` and `lawn-tuning-profile-ideal.md:171-175` are corrected: M5's
   commander half was fixed by `solid-remediation` T4.1, and what remains is `Empty` on both layers.

## Open questions

1. **Does Zomboss's empire level from every wave the game spawns?** The map raises this as this
   module's *"first question"* (`lawn-tuning-profile-map.md:53-55`): *"an empire that levels from every
   wave the game spawns grows on a clock the player does not control, and whether that is difficulty
   scaling with play or an escalation nobody asked for."* **It is not answerable here**, because the
   thing that would level is the **species** layer, whose crediting rule is `ai-empire-species` R1
   (*"Plant species progress for the player's empire, zombie species for Zomboss's"*,
   `spec-ai-empire-species.md:42-45`). **Options:** (a) let it level and control the result with
   `thetaOffset`; (b) cap Zomboss's species level against the player's; (c) decide it inside
   `ai-empire-species` with the crediting rule. **Recommended default: (c), with (a) as the lawn's
   dial** — the escalation question belongs to whoever owns the faucet, and this module's contribution
   is that `thetaOffset` exists and ships at 0 so the lawn can be corrected without a schema change.
   (b) is a cap on a progression axis and would need the Caps row's test before anyone proposed it.
2. **Cross-module note:** ruling 1's ⭐ sharpening says *"his commander build stays a commander aura, a
   different layer."* This module delivers Zomboss's pattern through the **commander allocation**
   seam, which is that layer's carrier on the lawn today
   (`SpeciesAllocationSource.resolveCommanderAllocation`). Whether an aura should instead ride the
   `aura` carrier (`ZombossCommanderAllocation.ActiveAuraId`, `:29-31`, already authored and
   unconsumed on the lawn) is `actor-layer-compose-ideal.md`'s question, not this spec's.
   **Recommended default:** use the existing carrier — inventing a second one for the same
   contribution is the defect DESIGN-GATE §1's actor-layer row names by number.

## Design gate checklist (DESIGN-GATE §5)

```
[x] Subsystems identified: aptitude allocation / actor layer stack, power index, lawn tuning profile,
    empire progression (named as external).
[x] Session boundary: backlog-clean-up-20260920. This spec writes one new file under
    docs/architecture/lawn-tuning-profile/ and edits nothing else.
[~] §1 rows read this session: actor-layer (via DESIGN-GATE §1's own row, read in full), Stats /
    ActorHub (via the one-compose rule and ContributionSourceIds), power/PS-3 and ssot-power-scale §10
    (via CLAUDE.md's one-power-ladder rule and the ideal's R-LT2, read in full), battle-engine-ssot §5
    (read in full), tunables-ssot and validation-ssot (as restated in CLAUDE.md).
    GAP: actor-layer-compose-ideal.md itself was NOT opened this session — the ⭐ sharpening is quoted
    from lawn-tuning-profile-map.md:48-55, which carries it verbatim. Open question 2 is therefore
    raised as a cross-module note rather than answered.
[x] decisions.md checked for a lock covering this: the Caps row (:60) is cited for the structural Θ
    floor; nothing locks the allocation source. No conflict.
[x] Every factual claim cites file:line, and every file cited was opened this session.
[x] audit-doc-citations.py --scope <this file> --strict: 0 HIGH findings, exit 0. The 4 remaining
    D1 (LOW) are mode-profile's own files and this spec's two proposed test files, all marked
    "new; does not exist yet".
[x] Verified against CODE, not comments — and this is the spec's headline finding: M5's own wording in
    TWO documents is stale, because SpeciesAllocationSource.cs:106,114-116 already gates the commander
    term by empire. That was established by reading the resolver, not by trusting the map.
[x] I read the surrounding section of every rule quoted (SpeciesAllocationSource.cs:99-138 in full;
    IPowerIndexProvider.cs:44-75 in full before claiming the key must not change).
[~] I tested (not assumed) the constraints I report. NOT RUN: no build or suite was executed this
    session (the brief forbids it). The byte-identical-goldens claim is argued from the untouched
    battle path, not measured, and is marked as an argument.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated: success criterion 8 requires the stale M5 wording in the map and the ideal
    to be fixed by the implementing task. Both files are outside this spec's write scope, so the
    correction is scheduled rather than made.
[x] No assertion pins a derived population count or generated text. Pattern count is explicitly
    banned from assertions; AllocationScope (4 members) is named as the closed vocabulary that may be.
[x] Event-refreshed cache (§2.16): YES, and its FULL trigger set is enumerated in a table with the
    key-set-moving edge (match start) and the value-invalidating edge (Θ revision) both named, each
    with a required test. The set is deliberately NOT copied from the commander cache, whose triggers
    do not include either — that copy is exactly the 2026-09-13 failure.
[x] No acceptance criterion fixes an ordering that can vary in real play: the trigger tests are one
    per trigger, not one convenient sequence.
[x] Actor combat/derived magnitude: YES. Layer = actor layer stack (allocation source + Θ). Scope =
    per empire. Lifetime = per match (the pattern) and live (Θ). Carrier = the existing registered
    AptitudeSubsystem via ActorHub's injected allocation delegate — no third carrier invented.
    Provenance = the existing aptitude SourceId grammar, unchanged.
[x] Does not invent or extend a SOLID-violating parallel path: it REMOVES a hard-coded empire policy
    from a Core resolver and hands it to the host that already owns the mode row.
[x] New rule has a registry row: none needed — this module adds no new rule, only a source selector.
    The "one power ladder" rule it must not break is already covered by scripts/guard-power.
```
