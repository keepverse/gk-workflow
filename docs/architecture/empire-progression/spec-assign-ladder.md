# Spec: `assign-ladder`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave A** · depends on: nothing.
**Rulings honoured:** the ideal's §"3. Assignment ladder" and R-Q3 (auto-assign is a default, never a
lock). **Status:** spec, not reviewed, no build authorized.

## Objective

Answer **"which build does the game suggest for this actor?"** in exactly one place, on the server,
for every caller: the silent default (`default-build`), the player's explicit auto-assign button
(`auto-assign-control`), the AI empire (`ai-empire-species`) — its species **and, by ruling R23
(2026-09-18), Zomboss's commander pool**, whose computed default mirrors the player's pool side-wide — and
the deferred species level-up grants sub-program (`species-progression-ideal.md` §"Deferred sub-program").

**R23's commander context.** Zomboss's pool calls `Suggest` with `ActivePresetRows = null` (an AI has no
preset surface today), `SpeciesFavourPermille = null` (a commander pool has no species),
`SpeciesPosture = null`, `FavourAllowed = false`. The walk therefore skips `active-preset`,
`species-favour` and `posture` **by name** and ends on `even` — the terminal rung's totality guarantee is
exactly what makes this caller safe. No new rule id and no commander-specific branch: the ladder is
unchanged, only a caller is added (`ai-empire-species` § *Zomboss's commander pool — R23*).

Three defects close here:

| Defect | Evidence | Fix |
|---|---|---|
| **W1** — the C# auto-assign had no production caller; the FE carried its own TypeScript copy. **Closed by EP1.4/EP1.5** (below): the fill mirror is deleted, not moved — `autoAssign.ts` dropped from 125 to 48 lines and `runAutoAssign.ts` is now a thin `/suggest` caller | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs:110`; `gk-web/web/fusion-rpg-web/src/features/aptitudes/runAutoAssign.ts:30-42` (the caller that replaced both old ranges) | the server owns the ladder; the FE calls it |
| **W3** — `species-favour` refuses every real species | `AptitudeAutoAssign.cs:89-90` returns `autoAssign.favour.incomplete` for a missing key; every plan row carries at most `maxAptitudesPerSpecies` keys (`gk-core/data/tuning/species-build.v1.json`, value 5). The spec it implements refuses only an empty map or a missing species (`docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md:62`) | zero-fill a missing aptitude; refuse only empty, or an id outside the closed twelve |
| No ladder | the rules exist as six independent ids (`AptitudeAutoAssign.cs:4-12`), with nothing that picks one | an ordered, data-driven walk that always ends on `even` |

**A user story.** *A player opens a specimen they have never built. The game already shows a sensible
build (its species' favour). They press "posture: force" and get a draft; they press Confirm or walk
away. Nothing is ever locked, and nothing is saved without Confirm.*

## Design

### The ladder is a walk over the closed rule set

The rule ids stay the closed set in `AptitudeAutoAssignRules` (`AptitudeAutoAssign.cs:4-12`). That is
a vocabulary the code owns, and adding a rule is a reviewed change. What is data is the **order**:

```
1. active-preset     if the scope has an active preset binding
2. species-favour    if the actor has a species with a plan row (zero-filled to 12)
3. posture           the posture of the species' primary aptitude, if known
4. even              always succeeds; the walk's terminal rung
```

`posture` is one ladder rung that resolves to `posture-force`, `posture-finesse` or `posture-bastion`
from `AptitudeCatalog`'s own `Posture` on the species' primary aptitude. It is not a seventh rule id.

The walk returns the **first rung that succeeds** plus a record of every rung it skipped and why. No
skip is silent: *"species-favour: species has no plan row"* is part of the result, and the sheet can
show it. This is the NWN / Mass Effect / FFXII gambit shape the ideal's prior art settled on, and it
is the same shape `FrontierRulesPolicy` already uses.

### The ladder returns a distribution, never points (map D3)

```csharp
namespace FusionRpg.Core.Stats.Aptitudes;

/// <summary>What the ladder suggests: which rule won and the twelve target shares it implies.
/// Points are the caller's business, via the scope's existing math.</summary>
public sealed record AssignSuggestion(                                  // (new)
    string RuleId,                                   // closed: AptitudeAutoAssignRules
    IReadOnlyList<AptitudePresetRowSpec> Rows,       // 12 rows; permille; favour/even/posture sum to 1000
    IReadOnlyList<AssignSkip> Skipped);              // every earlier rung and its named reason

public sealed record AssignSkip(string RuleId, string Reason);          // (new)

public sealed record AssignContext(                                     // (new)
    IReadOnlyList<AptitudePresetRowSpec>? ActivePresetRows,
    IReadOnlyDictionary<string, long>? SpeciesFavourPermille,    // a plan row, 0..12 keys
    Posture? SpeciesPosture,
    bool FavourAllowed);                                         // Mode C passes false (spec E-rules)
```

Two consumers turn a suggestion into points, each with the math it already ships:

| Path | Function | Rounding |
|---|---|---|
| Silent default (`default-build`) | `UniqueCreatureAllocation.Baseline` / `SpeciesAllocation.Baseline` | largest remainder; points sum to the budget |
| Draft button (this module's endpoint) | `AptitudePresetMaterialize.Materialize` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetMaterialize.cs:57`) | floor; leftover returned and legal (spec E2) |

This keeps the existing split intact rather than writing a third permille-to-points function.

### Zero-fill (W3)

`species-favour` builds 12 rows from the plan row: a present key keeps its permille, an absent key is
`0`. It refuses with a named reason only when:

- the map is empty (`autoAssign.favour.empty`, today's reason), or
- a key is not one of the twelve (`autoAssign.favour.unknownAptitude`, new reason), or
- the values do not sum to exactly 1000 (`autoAssign.favour.notNormalised`, new reason). A plan row
  always sums to 1000 (`SpeciesBuildPlannerTests.cs:93` asserts it), so this rung refusing means a
  corrupt input, never a normal case.

`autoAssign.favour.incomplete` is deleted. Its only meaning was the defect.

### One implementation

`AptitudeAutoAssign` keeps its per-rule fills (they are correct and tested) and gains
`AssignLadder.Suggest(AssignContext, AssignLadderTuning) → AssignSuggestion` (new). The server exposes
it:

| Route | Body | Returns | Persists |
|---|---|---|---|
| `POST /api/aptitude-presets/suggest` (new) | `{ playerId, scope, scopeKey, rule? }` | `{ ruleId, rows, skipped, draftShares, leftover }` | **never** |

With `rule` omitted, the ladder walks. With `rule` given, only that rule runs, which is what the
explicit button needs. `draftShares` is the materialized draft at the scope's current budget.

The FE's `runAutoAssign.ts` becomes a thin caller of this route, and `autoAssign.ts` keeps only its
types and the `APTITUDE_IDS` constant. `evenPermille.ts` keeps its editor-seed helper, which is a UI
concern and not a fill rule.

## Seedsmith / generator

**No generator change.** The ladder reads `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json` through
`SpeciesBuildPlanCatalog.SharesFor` (`gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanCatalog.cs:31`).
That file is `gk-forge/tools/CreatureBuildPlanGen`'s output and is never hand-edited. Wave B changes its
content; this module consumes whatever is committed.

## Tunables

`gk-core/data/tuning/aptitude-presets.v2.json` (new), published by the tool, never hand-edited:

```powershell
python gk-core/tools/tuning/publish.py aptitude-presets --label "assign ladder order" `
  --add-key ':assignLadder={"order":["active-preset","species-favour","posture","even"]}'
```

- **Load contract** (a load rejection names the key): every id is a known ladder rung; no duplicates;
  the last rung is `even`. The terminal rule is structural, since it is what makes the walk total. It
  is not tunable, and the loader comment says so.
- Move the pin at `gk-core/src/FusionRpg.Server/Program.cs:251` and `gk-forge/tools/ProveHubCombat/Program.cs:125` from
  `aptitude-presets.v1.json` to v2 in the same change.

## ActorHub gate

**Neither contributes nor consumes.** The ladder produces a suggestion. A suggestion reaches Hub only
as an ordinary allocation through the seams that already carry allocations, and that is
`default-build`'s concern, not this module's.

## Integer widths and the power ladder

`long` throughout, as the existing fills are (`AptitudeAutoAssign.cs:36-43`). Permille values sit in
`[0, 1000]` and are bounded ratios. No level-derived number is computed here, so no `Θ` or `P(Θ)` read.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AutoAssign|FullyQualifiedName~AssignLadder"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"
cd web\fusion-rpg-web; npm test -- --run aptitude
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs` | zero-fill; two new refusal reasons; `incomplete` removed |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AssignLadder.cs` (new) | `Suggest`, `AssignSuggestion`, `AssignSkip`, `AssignContext` |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetTuning.cs` | `AssignLadder` section parsed and validated |
| `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs` | `POST /suggest` |
| `gk-core/src/FusionRpg.Server/Program.cs` | v2 pin |
| `gk-core/data/tuning/aptitude-presets.v2.json` (new) | published, never hand-written |
| `gk-web/web/fusion-rpg-web/src/features/aptitudes/runAutoAssign.ts` | calls `/suggest` |
| `gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.ts` | fill logic removed; types stay |
| `gk-core/tests/FusionRpg.Core.ClassSystem.Tests/ClassSystem/AptitudeAutoAssignTests.cs` | real 5-key rows |
| `gk-core/tests/FusionRpg.Core.ClassSystem.Tests/ClassSystem/AssignLadderTests.cs` (new) | ladder walk |

## Code style

```csharp
public static AssignSuggestion Suggest(AssignContext ctx, AssignLadderTuning tuning)
{
    var skipped = new List<AssignSkip>();
    foreach (var rung in tuning.Order)                  // data; validated to end on "even"
    {
        var attempt = TryRung(rung, ctx);
        if (attempt.Ok) return new AssignSuggestion(attempt.RuleId, attempt.Rows, skipped);
        skipped.Add(new AssignSkip(rung, attempt.Reason));   // never a silent skip
    }
    // Unreachable by the load contract: the last rung is "even", and even cannot fail.
    throw new InvalidOperationException("assign ladder did not terminate on 'even'");
}
```

## Testing strategy

1. **The real plan shape.** A species-favour fill from a 5-key row (the shape every plan row has)
   succeeds, zero-fills seven aptitudes, and sums to 1000. Built from a row read out of the committed
   plan by id, never a synthetic 12-key map. **The ideal named the synthetic map as the defect's cover.**
2. **Refusals are named.** Empty map, unknown id and a non-normalised sum each refuse with their own
   reason.
3. **Ladder order is data.** Two tuning orders produce two different winning rules for the same context.
4. **Every skip is recorded.** A context with no preset and no plan row returns `posture` (or `even`)
   with each earlier rung in `Skipped` and its reason.
5. **Totality.** Every combination of absent inputs returns a suggestion (`even` at worst). This is
   the property the terminal-rung load rule exists for.
6. **Loader contract.** An order not ending in `even`, a duplicate, or an unknown id is a load rejection
   naming the key.
7. **FE parity by deletion.** The FE test asserts `runAutoAssign` calls `/suggest` and computes no share
   itself. This replaces the TypeScript mirror's own unit tests, which are removed with it.
8. **Draft-only.** `/suggest` leaves `rpg_aptitude_allocation` byte-identical (read back through
   `LoadAllocation`).
9. **R23 commander context.** A context with no preset, no favour map, no posture and
   `FavourAllowed = false` returns `even`, with `active-preset`, `species-favour` and `posture` each in
   `Skipped` with its reason; adding an active preset to the same context makes `active-preset` win.

No test counts species, plan rows, or shapes.

## Boundaries

- **Always:** keep the rule set closed in code; keep the order in data; record every skip.
- **Ask first:** adding a rule id; changing the terminal rung; letting `/suggest` persist anything.
- **Never:** a second fill implementation in the FE; refusing a real plan row for having fewer than
  twelve keys; treating species GET baseline **points** as permille
  (`spec-aptitude-auto-assign.md:61`).

## Success criteria

- [ ] `AptitudeAutoAssign`'s fills have a production caller, through `AssignLadder.Suggest`.
- [ ] `species-favour` succeeds on committed plan rows.
- [ ] The FE computes no shares; it renders what `/suggest` returns.
- [ ] Ladder order lives in `aptitude-presets.v2.json`, and its load contract is tested.
- [ ] `verify-change.ps1` green for every touched path.

## Open questions

None. The ladder order is the ideal's proposal, and it is shipped as a tunable. Ruling R23 (map Q-S1)
adds Zomboss's commander pool as a caller; it changes no rung.

## Self-audit — the debate

- **"The draft button and the default use different rounding. That is two answers."** They answer two
  questions. The draft shows the player the leftover to place (E2); the default must spend the whole
  budget, as the species baseline already does. Unifying them would change one of two shipped
  contracts. The *distribution* is one answer, and that is the part this module owns.
- **"Removing the FE mirror breaks gameless-first."** The server is the gameless core. The web already
  needs it for every allocation write.
- **"`posture` as a rung but not a rule id is a hidden eighth concept."** It is a resolver onto three
  existing ids, chosen by a fact the actor already has. The winning `RuleId` in the result is always
  one of the six real ids.
