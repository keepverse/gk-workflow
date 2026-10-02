# Spec: `synthetic-graph`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `synthetic-graph`, §2.1 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; no dependencies). Umbrella:
[../../trade-network-map.md](../../trade-network-map.md) §5 invariants bind this module. Ideal:
[../../trade-network-ideal.md](../../trade-network-ideal.md) §9, §14b ("the giant tier cannot be tested
before the world generator"). House style: `world-action-economy/spec-budget-debit.md`.

## Objective

Every tier above `medium` is declared and unavailable, gated on a world generator that does not exist
(`gk-core/src/FusionRpg.Core/World/WorldSizeCatalog.cs:51-58`). So nothing can measure a turn, a flow or an
economy at the scale trade must survive. This module is a **test-only builder** that produces a
**valid, deterministic `WorldState` at any size tier** from `(tier, seed, options)`, plus a
**campaign driver** that steps it for N turns with the shipped AI policies filing every faction's
orders. `step-benchmark` and `economy-report` consume both; later sub-programs extend the builder
through decorators instead of writing a second one.

Success looks like: `SyntheticGraph.Build("giant", seed)` returns a world that passes every creation
rule except the template-size rule it cannot meet by construction, with every lane type present, and the
same inputs produce the same canonical bytes on every machine.

## Scope and non-goals

In scope: the builder, its options and decorator seam, the campaign driver, and their contract tests.

Not in scope: a production world generator (`world-map` wave 4 owns it); any change to `src/`; any
gameplay number; any persistence of a synthetic world through `RpgStore.CreateWorld` (see Design 5).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Five tiers; node range per tier loaded from tuning, `large`/`huge`/`giant` `Available = false` | `gk-core/src/FusionRpg.Core/World/WorldSizeCatalog.cs:41-58` |
| Sixteen creation rules; map profile runs all of them | `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:59-79`; profile record `:14-27` |
| Rule 13 looks the template id up in `WorldTemplateCatalog.SizeIdOf`, which throws for any id it does not know | `WorldValidation.cs:385-392`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:25-30` |
| Rules a synthetic world must meet: stable id order (`:82-88`), one lane per unordered pair (`:150-171`), undirected connectivity (`:173-199`), exactly one homeworld owned by the player with a Seat (`:201-218`), Seat count per base-capable sector (`:220-232`), allowed slot types and no intact unguarded slot (`:234-264`), entity placement (`:299-340`), rootbed on the homeworld (`:364-369`) | `WorldValidation.cs` as cited |
| Six lane types, two carrying no supply | `gk-core/src/FusionRpg.Core/World/LaneTypeCatalog.cs:51-65` |
| Eight sector types and their allowed slots | `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:59-100` |
| Five faction kinds; two AI policies | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-30`; `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18` |
| Opening belief seeded the same way for every template | `WorldTemplateCatalog.cs:39-53` (`IntelSeed.ForTemplate`, public, `gk-core/src/FusionRpg.Core/World/Intel/IntelSeed.cs:15`) |
| The store drives AI factions: `BelievedWorldView` per faction, seed stream `ai:{faction}:{turn}` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-247`; view ctor `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:89`; `SeededRng.DeriveStream` `gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26` |
| Hand-built raw graphs, deliberately not validated | `gk-core/tests/FusionRpg.Core.Tests/World/Topology/GraphShapes.cs:5-20` |
| A ring-with-chords lanes-only builder inside a bench | `gk-core/tests/FusionRpg.Core.Tests/World/Topology/ReconnectionCostBench.cs:22-40` |
| A second, shape-only `SyntheticWorld` class (not a `WorldState`) inside the Release bench | `gk-core/tests/FusionRpg.Bench/WorldGraphWriteBench.cs:548-575` |

### Real gap

Nothing builds a **valid** `WorldState` above the hand-authored `medium` tier, and nothing steps one with
every faction playing.

## Design

### 1. Types (test code, `tests/FusionRpg.Core.Tests/World/Synthetic/`)

```csharp
namespace FusionRpg.Core.Tests.World.Synthetic;

public sealed record SyntheticOptions
{
    public int? SectorCount { get; init; }          // null = drawn inside the tier's tuned range
    public int RivalEmpires { get; init; } = 2;      // WorldFactionKind.Rival, FrontierRules policy
    public int Clans { get; init; } = 3;             // WorldFactionKind.Clan, stand-fast policy
    public int LegionsPerEmpire { get; init; } = 2;
    public IReadOnlyList<ISyntheticDecorator> Decorators { get; init; } = Array.Empty<ISyntheticDecorator>();
}

public interface ISyntheticDecorator            // later sub-programs add goods, bank points, routes …
{
    string Id { get; }                           // kebab-case, unique per build
    WorldState Apply(WorldState world, SyntheticContext context);
}

public sealed record SyntheticContext(string TierId, ulong Seed, SeededRng Rng);

public static class SyntheticGraph
{
    public static WorldState Build(string tierId, ulong seed, SyntheticOptions? options = null);
    public static WorldValidationProfile Profile { get; }   // Map with RequireTemplateSize = false
}

public static class SyntheticCampaign
{
    public static IEnumerable<TurnResult> Run(WorldState world, int turns, ulong seed,
        IBattleResolver? resolver = null);
}
```

The files use **public Core API only**. `step-benchmark` compiles the same files into the Release bench
by source link, and `FusionRpg.Bench` has no `InternalsVisibleTo` (only `FusionRpg.Core.Tests` does,
`gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:18`). No file here references xunit, for the same reason.

The name `SyntheticGraph` is chosen to avoid the existing bench type `SyntheticWorld`
(`gk-core/tests/FusionRpg.Bench/WorldGraphWriteBench.cs:553`), which is a different, shape-only thing.

### 2. Construction, in order

All randomness comes from `SeededRng.DeriveStream(seed, "synthetic:" + tierId)`; no `System.Random`.
Every collection is emitted in ordinal id order. Ids are zero-padded (`s0001`, `l0001`, `e0001`) so
ordinal order equals numeric order.

1. **Size.** `n = options.SectorCount ?? rng.Range(tier.MinNodes, tier.MaxNodes)`, read from
   `WorldSizeCatalog.Get(tierId)`; an explicit count outside the tier's range throws.
2. **Factions.** `player` (`Player`, no policy), `zomboss` (`Zomboss`, `frontier-rules` — the one
   dominant enemy empire), `rival-01…` (`Rival`, `frontier-rules`), `clan-01…` (`Clan`, `stand-fast`),
   `wild` (`Wild`, `stand-fast`). Policy ids come from `FactionPolicies` constants, never literals.
3. **Sectors.** Sector 0 is the player's `homeworld` (Seat, rootbed, market). Each empire gets one
   base-capable capital with a Seat and a rootbed; `zomboss`'s capital is a `boss-lair`. Clans get one
   or two held sectors. The rest are drawn from the sector-type catalog, weighted toward the non-home
   types, each with a slot list drawn from that type's `AllowedSlotTypes` and a Seat exactly when the type
   `CanHostSeat`. Guarded slots carry an opaque guard id; an intact guard always has one (rule 6).
4. **Lanes.** A spanning tree first (connectivity by construction), then extra edges up to an average
   degree the tier's range implies, never two lanes on one unordered pair. Lane types are assigned so
   that at the `giant` tier every `LaneTypeCatalog.All` id appears at least once; `one-way` and `deep`
   are never the only path out of a capital, so supply is not severed at turn 0.
5. **Entities.** `LegionsPerEmpire` legions per empire at its capital, with members whose species ids
   are **read from a shipped template at build time** (`WorldTemplateCatalog.Build("first-light", …)`
   entities), so the battle resolver resolves them exactly as it does for `first-light`. At least one
   member per legion is a `Bearer`, so supply has capacity (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-21`).
6. **Stocks.** Opening loam on held sectors and carried loam on legions follow the templates' shape
   (`WorldTemplateCatalog.cs:142`, `:191`); the amounts come from `LoamPolicy` members, never literals.
7. **Belief.** `IntelSeed.ForTemplate(world)`, the templates' own step.
8. **Decorators**, in the order given, each with a child RNG stream `synthetic:{tier}:{decorator.Id}`,
   so adding a decorator never shifts the base world's draws.
9. **Validation.** `WorldValidation.Validate(world, SyntheticGraph.Profile)`, then the builder asserts
   rule 13's intent itself: `n` lies inside the tier's range.

`TemplateId` is `synthetic-{tierId}`.

### 3. Why rule 13 is skipped, not satisfied

Rule 13 exists so an authored template cannot drift outside the tier it claims. It resolves the tier
from the template id, and `SizeIdOf` throws for anything but the two shipped templates
(`WorldTemplateCatalog.cs:25-30`). Registering synthetic ids there would put test-only ids in a
production catalog. The profile is a public record, so the test builds
`WorldValidationProfile.Map with { RequireTemplateSize = false }` and checks the range directly, which
is the same invariant without a production edit.

### 4. The campaign driver

`SyntheticCampaign.Run` mirrors the store's AI loop (`RpgStore.WorldTurns.cs:218-247`) without the
store: for each turn, for each faction in ordinal order, it builds a `BelievedWorldView`, derives the
seed `SeededRng.DeriveStream(seed, $"ai:{faction}:{turn}").NextULong()`, calls the faction's policy
and collects the orders; then it calls `TurnEngine.Step`. The player faction is driven by
`frontier-rules` **through the driver's own faction → policy map**, never by writing a policy id onto
the player's `WorldFaction` (a null policy is what marks the human, `gk-core/src/FusionRpg.Core/World/WorldState.cs:76-77`).
Commands go through `WorldCommandAdmission` inside `Step`, exactly as the store's do.

### 5. Persistence boundary

A synthetic world never goes through `RpgStore.CreateWorld`: that path validates with the full map
profile (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:226`), so rule 13 would refuse it, and replay
rebuilds from the template id (`RpgStore.WorldTurns.cs:769`). Store-level tests in this sub-program use
the shipped `two-hearths` template.

### 6. Numeric types

Stocks are `long`, like the fields they fill (`WorldState.cs:173-187`, `:234`). No arithmetic here
beyond range draws.

## Tunables

None. Tier ranges are read from the existing world tuning; opening stocks from `LoamPolicy`. Option
defaults (`RivalEmpires`, `Clans`, `LegionsPerEmpire`) are test inputs, not balance numbers.

## Acceptance criteria (contract)

1. For every tier in `WorldSizeCatalog.All` and a spread of seeds, `Build` returns a world that passes
   `WorldValidation.Validate(world, SyntheticGraph.Profile)` and whose sector count lies in that tier's
   `[MinNodes, MaxNodes]`, **read from the catalog**, never a literal.
2. The same `(tier, seed, options)` produces byte-identical `WorldCanonical.Write` output across two
   builds; a different seed produces different output.
3. At the `giant` tier every `LaneTypeCatalog.All` id appears on at least one lane, and every
   `FactionKindCatalog` kind the options ask for is present with a policy `FactionPolicies.IsKnown`.
4. Exactly one `Zomboss`-kind faction exists, whatever `RivalEmpires` is (counterparties ask A4).
5. Adding a decorator leaves the base world's canonical rows identical except for what the decorator
   itself writes (child RNG streams).
6. `SyntheticCampaign.Run` over a `medium` world for a scripted run completes with no thrown exception,
   and re-running it with the same seed yields the same `StateHash` sequence.
7. The tests **print** tier, sector, lane, faction and entity counts; they assert no count of their own
   choosing.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Synthetic/SyntheticGraphTests.cs` (new), trait
  `[Trait("VerificationId", "core.world-synthetic")]`.
- `gk-core/scripts/verification-boundaries.v1.json` gains one owner row: `world-synthetic`, paths
  `tests/FusionRpg.Core.Tests/World/Synthetic/**`, project `core`, verificationId `core.world-synthetic`,
  level `focused`. Without it the path falls to `core-tests-fallback` (the whole Core suite), which
  `verify-change.py -PlanOnly` showed this session for `gk-core/tests/FusionRpg.Core.Tests/World/Topology/GraphShapes.cs`.
- Verify: `.\scripts\verify-change.py -Paths <changed files> -Session <id>`;
  `dotnet test tests\FusionRpg.Core.Tests --filter "VerificationId=core.world-synthetic"`.

## Hard edges

None: test-only, no schema, no golden, no ruleset stamp.

## Boundaries

- **Always:** public Core API only; owned RNG; ordinal id order; decorators for extension.
- **Ask first:** registering synthetic ids in any production catalog.
- **Never:** reference this code from `src/`; persist a synthetic world through the store; pin a
  population count in an assertion.

## Dependencies and interface

**Depends on:** nothing.

| Exposed | Consumer |
|---|---|
| `SyntheticGraph.Build`, `SyntheticOptions`, `SyntheticGraph.Profile` | `step-benchmark`, `economy-report`; `logistics-flow` `logistics-bench` (ask A1: its decorators seed located goods, bank points, route policies and hostile presence); `counterparties` (ask A4: N empires, M clans, one dominant enemy); `exchange` harness |
| `ISyntheticDecorator` | every later sub-program that needs a synthetic world with its own state |
| `SyntheticCampaign.Run` | `step-benchmark`, `economy-report` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world model and validation, world AI policy loop (read only), test infrastructure.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers docs/architecture/
    trade-network/**. session-boundary-check.py was not re-run for this file; the record's notes list
    the known crossing with summoner-convergence worktree lanes (new file, cannot conflict).
[x] Read this session: trade-foundation map, umbrella map, trade-network ideal (§9, §14b),
    DESIGN-GATE, PRINCIPLES, spec-budget-debit (house style). No DESIGN-GATE row names world
    validation beyond "World map"; the rules were read in code, not in spec-world-model.md.
[x] decisions.md checked: no lock on test builders; the phase-order row (:7) is untouched.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: rule 13's lookup and throw, the profile record's `with`-ability, the
    InternalsVisibleTo list, the AI loop's seed derivation.
[x] Surrounding sections read (WorldValidation's profile doc comment; GraphShapes' reason for skipping
    validation).
[x] No constraint claimed without a test: "rule 13 would refuse a synthetic id" is read from
    SizeIdOf's default arm, not assumed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the rule-13 finding and the SyntheticWorld name clash are recorded in the
    map's spec-time corrections section.
[x] No population pinned: counts are printed; only catalog-derived ranges and closed catalogs are
    asserted.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion: faction iteration order is the store's own ordinal order.
[x] ActorHub: not touched.
[x] No SOLID fork: one builder with a decorator seam instead of one builder per sub-program; the AI loop
    is mirrored for tests only, not re-implemented in src/.
[x] No new rule, so no registry row.
```
