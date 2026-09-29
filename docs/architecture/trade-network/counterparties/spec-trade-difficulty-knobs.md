# Spec: `trade-difficulty-knobs`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `trade-difficulty-knobs`, row 5 of the
[counterparties map](../counterparties-map.md) (wave 1). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §14b (*"One difficulty profile per world
(world-continuity W7): loss rates, AI bidding and AI spend limit are its knobs"*), §7.5 (*"A per-turn AI
purchasing limit is a structural limit, stated in a comment"*), principle 10. Session record:
`tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Own the **trade rows** of the world's one difficulty profile: a lane-loss multiplier, an AI bidding
aggressiveness and the AI per-turn spend limit, keyed by the profile id the per-world stamp records.
Difficulty here is **rules for everyone and parameters for the AI**, never a stat bonus
(`spec-ai-commander.md` assumption 3). A knob that changes a rule for only some factions is a handicap and
is declared in the turn report.

Success looks like: the default profile reproduces the un-knobbed arithmetic exactly; a harsher profile
raises lane loss for the player and every AI empire alike; a profile row missing a key refuses to load.

## Scope and non-goals

**In scope:** three keys per profile, their loader and hub, one read keyed by the stamp's profile id,
the handicap-declaration rule.

**Non-goals:** the profile catalog and its ids (`world-continuity` W7 owns it); applying lane loss
(`logistics-flow` `lane-loss` reads the knob); bidding and spending (`trade-ai` `ai-bidding`,
`ai-spend-limit` read the knobs); any difficulty outside trade.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The declared-handicap precedent: a per-mille faction lever, hashed, named in the turn report once per faction per turn whenever it is not 1000 | `gk-core/src/FusionRpg.Core/World/WorldState.cs:79-83`; `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:151-156` |
| The tuning load pattern: the host parses the file and configures a static hub; Core never reads a file | `gk-core/src/FusionRpg.Server/Program.cs:47-49`; `gk-core/src/FusionRpg.Core/World/WorldTuning.cs:245-249` |
| Difficulty is which policy, not a stat bonus | `docs/architecture/world/spec-ai-commander.md` assumption 3 |

### Wiring gap

None.

### Real gap

No difficulty profile exists anywhere in the world tree (the map's *What the code says* table); no trade
rows.

## Design

### 1. The rows

```jsonc
// data/tuning/trade.v{n}.json
"difficulty": {
  "<profileId>": {
    "laneLossMilli": 1000,           // multiplier on logistics-flow's lane loss; applies to EVERY faction
    "aiBidAggressionMilli": 1000,    // trade-ai bidding parameter; AI only, outside Step
    "aiMaxSpendPerTurnMilli": 1000   // trade-ai per-turn spend limit, ‰ of last turn's banked income
  }
}
```

- The profile ids are `world-continuity`'s catalog. The loader rejects a profile in that catalog with no
  trade row, and a trade row whose profile id is not in the catalog (T5; one closed list, no drift).
- v1 ships one default profile (`world-continuity-ideal.md` §6.10), so v1 has exactly one row.

### 2. Classification of each knob

| Knob | Read where | Class | Declared as a handicap? |
|---|---|---|---|
| `laneLossMilli` | inside `Step` (`logistics-flow` `lane-loss`) | a **rule** for every faction | No — symmetric by construction |
| `aiBidAggressionMilli` | outside `Step` (`trade-ai` policy) | an AI **policy parameter** | No — a policy parameter changes what the AI decides, never what the engine enforces; replay never re-runs a policy |
| `aiMaxSpendPerTurnMilli` | outside `Step` (`trade-ai` `ai-spend-limit`) | an AI policy parameter; the limit's *existence* is a structural per-turn rate (commented as such where it is enforced), its *value* is this tunable | No, for the same reason |

**The rule for any future knob:** a knob read inside `Step` that applies to a subset of factions writes a
report line of the `loam.handicap` shape (`LoamPhases.cs:151-156`) — `trade.handicap:<key>:<value>`, once
per affected faction per turn, audience that faction. None of the three v1 knobs triggers it.

### 3. The read

```csharp
namespace FusionRpg.Core.World.Trade;   // (new)

public sealed record TradeDifficulty(int LaneLossMilli, int AiBidAggressionMilli, int AiMaxSpendPerTurnMilli);

public static class TradeDifficultyHub
{
    public static void Configure(IReadOnlyDictionary<string, TradeDifficulty> byProfile);
    public static TradeDifficulty For(string profileId);   // throws on an unknown id
}
```

Callers pass the profile id from the world's stamp (`trade-foundation` `world-stamp`). The loader lives
beside the other trade tuning loaders; the host configures the hub at start (`gk-core/src/FusionRpg.Server/Program.cs` pattern).

### 4. Symmetry proof obligation

`laneLossMilli = 1000` must reproduce the un-knobbed lane loss exactly. `lane-loss` applies it as
`loss × laneLossMilli / 1000` in `long`, dividing once, after its own arithmetic — so 1000 is an identity.
That is a property of the arithmetic, tested; the shipped value of the default row is a tuning reading,
never pinned by a test.

## Tunables

The three keys above, per profile, in `data/tuning/trade.v{n}.json`, added through
`publish.py trade --add-key`. Starting value for the default profile: 1000 each (neutral, by principle:
the default world is the un-knobbed world).

## Numeric types

The knobs are `int` per-mille ratios. Where they multiply a magnitude (lane loss on goods), the product is
`long`, widened before multiplying, divided by 1000 last (PRINCIPLES §5); that arithmetic is
`lane-loss`'s and `ai-spend-limit`'s to implement, stated here as the contract.

## Acceptance (contract)

1. A missing profile row, a missing key, or a row for an unknown profile is a load rejection naming it.
2. With `laneLossMilli = 1000`, lane loss equals the un-knobbed result for every input (property test,
   once `lane-loss` exists; until then a unit test on the multiplier function).
3. A knob read in `Step` for a subset of factions writes one `trade.handicap` line per affected faction
   per turn (tested with a test-only knob, so the rule is proven before a real knob needs it).
4. `TradeDifficultyHub.For` is pure and never reads a file.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/TradeDifficultyTests.cs` (new): loader rejections, identity
  multiplier, handicap-line rule.

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/TradeDifficulty.cs','gk-core/src/FusionRpg.Server/Program.cs','tests/FusionRpg.Core.Tests/World/Trade/TradeDifficultyTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade.TradeDifficulty"
python gk-core/scripts/audit-magic-numbers.py --summary
```

## Hard edges

- **Tuning versions are process-global** (umbrella X4): a publish applies to every world. The stamp records
  the profile id and the tuning version so replay refuses honestly on a mismatch (`trade-foundation`
  `world-stamp`); two tuning versions never run side by side.

## Dependencies

| Consumes | From |
|---|---|
| Difficulty profile catalog (ids) | `world-continuity` `world-difficulty-profile` (audit m8: this row named the ideal tag *"W7"*, not a module id) |
| Profile id on the stamp | `trade-foundation` `world-stamp` |
| **No capability flag of its own** (round 6 C1 / landing order R3): the profile id is written onto the stamp at world creation (CM10), so a world's knobs are fixed from creation and nothing can change mid-life. This module lands in `counterparties` wave 1 and registers no row, which is the one case a spec may still say "no bump" | — |

| Exposes | To |
|---|---|
| `TradeDifficultyHub.For(profileId)` | `logistics-flow` `lane-loss`; `trade-ai` `ai-bidding`, `ai-spend-limit` |
| The handicap-line rule | any later trade knob |

## Contradictions found

None. The ideal calls the AI spend limit both *"structural"* (§7.5, §13) and a difficulty knob (§14b).
They are compatible: structural in the caps-rule sense (a per-turn rate, exempt from "no ceilings" and
commented as such), tunable in value.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: tunables, world turn (handicap reporting), AI parameters.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus trade-ai-map module 3 and
    trade-foundation-map world-stamp.
[x] decisions.md: no difficulty lock.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: UpkeepHandicapMilli and its report line, Program.cs tuning load, WorldTuningHub.
[x] Surrounding sections read (§7.5, §13 table row, §14b player-experience row).
[x] No "moves goldens" claim.
[x] No §2 invariant contradicted; symmetric by default.
[x] No population pinned; one row per profile is the catalog's reading.
[x] No cache; no ordering; no actor magnitude.
[x] No SOLID-violating path: one hub per domain, profile ids owned once.
[ ] Registry row: the handicap-line rule has no enforcement-registry row yet.
```

## Audit 2026-09-20

Checked and clean: three per-mille knobs, each classified (a symmetric rule inside `Step`, or an AI policy
parameter outside it); the handicap-line rule is proven with a test knob before any real knob needs it; the
default profile is the identity (1000) by property, never by a pinned reading; Core never reads a file (host
loads, hub configured at start); a missing or unknown profile row is a load rejection. The AI spend limit is a
per-turn structural rate in the caps-rule sense, tunable in value, commented where enforced (`trade-ai`).
**Verification boundary:** the `core-world-trade-counterparties` owner boundary (`spec-empire-goods-sinks.md`
*Audit 2026-09-20*) covers `World/Trade/**`; `Program.cs` keeps its Server owner.
