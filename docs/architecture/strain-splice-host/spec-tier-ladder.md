# Spec: `tier-ladder`

**Module id:** `tier-ladder` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 7 of 8 · **Depends on:** `host-gate` (1), `combo-bind` (4), `combo-budget` (6) ·
**Rulings:** 4 (*"higher granted tier ⇔ higher `minTier` floor, D41 unordered and `minSockets`-as-floor
unchanged; exact steps go to tuning and matcher tests, never the generator"*), 5 step 3 · **Findings
closed:** F7 (ladder half), F8.

## Objective

Give the Diablo half the program is missing: **better runes make a better word.** Today every Strain
and Splice grants one flat tier (`baseTier: strain 1, splice 1`, `gk-core/data/tuning/strain-splice.v1.json:10`)
behind one flat floor (`minTierPlan [1,1,2,2]`, `gk-core/data/tuning/strain-splice.v1.json:7`), so a word built
from five-tier gems is exactly as strong as one built from the cheapest gems that clear the floor.

And today's floor lives in the wrong place (F8). The generator zips `minTierPlan` onto the four family
picks **sorted by family id** and writes the result into each entry
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:120`), then writes `grantedTier` into each
entry too (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:111`). Two consequences:

- *Which* ingredient needs the higher tier is an alphabetical accident of family ids.
- A balance pass on the floor or the grant needs a **regeneration**, which is the exact property rulings
  2–4 exist to protect: *"every specific lives in data, and the generator only knows shapes."*

So this module moves the ladder into tuning, read at match time by the one matcher, and takes every
tier number out of the corpus.

**User outcome:** upgrading a word's gems (the 3:1 forge the workbench already has) visibly raises the
word's tier; the socket bench says what the next rung needs.

## Design

### 1. The ladder — `data/tuning/strain-splice.v2.json` (new)

`recipe.minTierPlan` is replaced by `recipe.tierLadder`; `recipe.baseTier` stays per shape.

```jsonc
"tierLadder": [
  { "floor": [1, 1, 2, 2], "grantDelta": 0 },   // rung 1 == today's flat floor: no behaviour change
  { "floor": [2, 2, 3, 3], "grantDelta": 1 },
  { "floor": [3, 3, 4, 4], "grantDelta": 2 },
  { "floor": [4, 4, 5, 5], "grantDelta": 3 }
]
```

Rung 1 reproduces today exactly. The higher rungs are **working values, not a validated balance
decision** (the `_meta` note every tuning file carries); a balance pass moves them with the publish
tool, never with code or a regeneration. The owner deliberately left exact steps to tuning (ideal,
*"What this deliberately does not decide"*).

`floor` is **positional over the claimed ingredients' tiers sorted ascending** — the lowest gem must meet
`floor[0]`, the next `floor[1]`, and so on. It names no family, so it survives any regeneration and
encodes the Diablo shape (*a word's level is set by its runes*) without Diablo's exact-order rule: D41
stands, because sorting the claimed tiers erases position. `minSockets` stays a floor.

**Load-time rules** (`StrainSpliceTuning.Parse`, `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs:76`;
all throw, none clamp): at least one rung; every `floor` has `strainSplice.ingredientCount` entries, is
ascending, and lies in `[1..insertTiers.count]`; rungs are strictly increasing (each floor elementwise
`>=` the previous and not equal); `grantDelta` starts at 0 and strictly increases; and **the atom-ladder
bound (F7):** `max(baseTier) + top grantDelta + attunedTierBonus <= FamilyExpansion.TierCount`
(`gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs:28`). With the working values above:
1 + 3 + 1 = 5, exactly the ladder. Plus `combo-budget`'s gate: a ladder of more than one rung refuses
to load unless combination pricing has been measured and passed against the **loaded** socket,
strain-splice and materials revisions and the loaded combination corpus (`comboPricing.measuredAgainst`,
checked by `ComboPricingProvenance.Check`, `combo-budget` §5). Under R12 of [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)
there is no per-actor count budget; what is measured is power against price. Every new rung the ladder
adds is a new `(combination, rung)` cell that report must pass, so a ladder step that grants more power
without a matching ingredient-tier (and therefore gem-price) step fails there, not in play.

**This module re-runs the measurement — it does not inherit module 6's (strengthen pass 2026-09-18).**
`combo-budget` runs before this module and can only measure the one rung that exists then. Its
provenance names `strainSpliceVersion` 1, so publishing `strain-splice.v2.json` makes the server refuse
to boot by name until the report has priced rungs 2..n and a new `measuredAgainst` (with the new
`strainSpliceVersion`) is published as the next sockets revision. The first draft checked only that some
provenance existed, which let a four-rung ladder bind against a one-rung measurement. The same rule holds
for every later ladder rebalance: a ladder publish and its re-measure are one step.

**Every reader moves to v2 (strengthen pass 2026-09-18).** `strain-splice.v1.json` is named by literal in
the server (`gk-core/src/FusionRpg.Server/Program.cs:324`), the combogen parser
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:21`) and the tests that load the shipped
file. A v2 only the publish tool knows about is a ladder nothing plays. This module applies
`circuit-topology` §4's rule to the `strain-splice` domain — one current-revision constant per language,
the guard test extended to `strain-splice.v{n}.json` literals — in the same change as the publish.

### 2. The matcher reads the ladder — in one place

After module 1 there is one matcher (`ComboMatcher.Match`). It changes in exactly two ways:

1. Ingredients match on `(family, quantity)` only — no per-ingredient `MinTier`.
2. After a successful claim, it sorts the claimed tiers and returns the **highest rung** whose floor
   they meet (`Rung`, 1-based), or no match if rung 1 is not met.

```text
GrantedTier = baseTier[shape] + ladder[rung].grantDelta + (allAttuned ? attunedTierBonus : 0)
```

The evaluator reports it (`gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs:91` today computes
`BaseTier + attuned`); the preview reads the same `MatchResult` and gains two fields for module 20's
socket bench — the rung reached, and for the next rung the positions still short (`TierShortfall(position,
have, need)`). A fill whose families match but whose tiers miss rung 1 reports those shortfalls instead
of a missing family. D22 as amended is unchanged: attunement is a bonus and never a gate.

`combo-bind` (module 4) builds combination containers for every tier the ladder can grant; because the
top bound is validated at load, a container for every reachable tier exists.

### 3. The corpus stops carrying tier numbers (generator change + deterministic re-emit)

| Field | Today | After |
|---|---|---|
| `ingredients[]` | `{family, minTier, quantity}` | `{family, quantity}` — identical families fold |
| `grantedTier` | per entry, from tuning | **removed** — the shape's `baseTier` is read from tuning at import |

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` stops zipping the plan (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:104`, `ingredient_rows`) and stops writing
  `grantedTier` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:111`); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` validates the ladder instead of the plan
  (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:165`).
- The shipped corpus is **re-emitted from the run ledger** (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:275`,
  `entries_from_ledger`) by a deterministic verb (new) `combogen-reemit` — the model's recorded answers
  (families, grants, pins, names) are unchanged, only the emitted shape moves, and `_meta.amendments`
  records the re-emit. **No model call, no hand edit.**
- `KindCatalog` (`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132`) drops `grantedTier` from the
  required and extra sets; the Python `combination` KindSpec (module 2) matches.
- `recipe-import` (module 3) fills `ComboRecipe.BaseTier` from `StrainSpliceTuning.BaseTierFor`, so the
  `strainsplice.base-tier-not-tunable` rule (`gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceGrid.cs:164`)
  has nothing left to check and is deleted rather than kept as dead code.

### 4. Storage

`ComboIngredient` loses `MinTier` (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:138`), and
`socket_combo_ingredient` loses `min_tier` from its columns and its primary key
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs:84`, `:88`). **Owner-approved 2026-09-21; executed by
SSH7.8.** The migration drops the pre-re-key table before any write (H2) and the same `CREATE` rebuilds
it keyed `(combo_id, family_id)`. The table is content re-seeded at every boot, holds no player state,
and is rebuilt by `SeedComboRecipes`; the migration is drop-and-reseed of a content table. The recipe's
rung-1 floors are persisted on `socket_combo_recipe.base_floors`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs:77`) because `ComboRecipe.BaseFloors` is what the
no-ladder matcher reads after the store round-trip — the dropped `min_tier` column used to carry them.

## Seedsmith / generator

| Item | Detail |
|---|---|
| Adapter / stage | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:104` (`ingredient_rows` — family + quantity only); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:133` (`granted_tier` — deleted; the runtime owns it); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:111` (no `grantedTier` field); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:165` (validate `tierLadder`); `combogen-reemit` verb (new) over `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:275` |
| New / changed seed fields | **removes** `ingredients[].minTier` and `grantedTier`. Adds nothing. The model's schema is unchanged — it never offered a tier (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:19`) |
| Magnitudes | `data/tuning/strain-splice.v2.json` (new) — `tierLadder`, `baseTier` |
| Regenerate | `python -m seedsmith items combogen-reemit --dry-run` (new) → `--write`; then `--gate` check |
| Check | `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` · `dotnet run --project gk-forge/tools/ItemSeedValidator` |
| Pytest | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — `the_emitted_entry_carries_no_tier_number`, `reemit_is_byte_identical_on_a_second_run`, `reemit_preserves_every_model_answer`; `gk-forge/tools/seedsmith/tests/test_combogen.py` — ladder validation mirrors C# |

## Commands

```powershell
python tools\tuning\publish.py strain-splice --add-key "recipe:tierLadder=[{\"floor\":[1,1,2,2],\"grantDelta\":0},...]" --remove-key recipe:minTierPlan --label "graduated tier ladder"
# --remove-key already exists by then: circuit-topology (module 5) adds it to gk-core/tools/tuning/publish.py
cd tools\seedsmith
python -m seedsmith items combogen-reemit --dry-run
python -m seedsmith items combogen-reemit --write
python -m pytest tests/test_strain_splice_gen.py tests/test_combogen.py -q
python -m seedsmith items combo-budget --report      # prices rungs 2..n; must exit 0
cd ..\..
python tools\tuning\publish.py sockets comboPricing.measuredAgainst.strainSpliceVersion=<n> comboPricing.measuredAgainst.socketsVersion=<n> comboPricing.measuredAgainst.combinationCorpusDigest=<printed> ... --label "re-measure for the tier ladder"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ItemSurface|FullyQualifiedName~ComboPricing"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

Crosses Core, Data, a tool, seedsmith and tuning: run `deploy-play.py --full-suite` once at the end
(AGENTS.md verification boundary, point 2).

## Project structure

```text
data/tuning/strain-splice.v2.json                                 (new, published)
gk-core/tools/tuning/publish.py                                                  --remove-key (landed by circuit-topology; reused)
gk-core/src/FusionRpg.Server/Program.cs                                          reads the current strain-splice revision
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py              STRAIN_SPLICE_PATH → the current revision
data/tuning/sockets.v{n}.json                                            (next, published) re-measured provenance
gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs                   TierLadder + load-time rules
gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs                         rung from sorted claimed tiers
gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs                 GrantedTier via the ladder
gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs                          ComboIngredient without MinTier
gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceGrid.cs                     base-tier rule deleted
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs                            min_tier column dropped (ask-first)
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py                no tier numbers emitted
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py              ladder validation
gk-forge/tools/seedsmith/seedsmith/report/cli.py                                  items combogen-reemit (new verb)
gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs                        grantedTier dropped
gk-data/packs/fusion/data/seed/items/combinations/*.json                                      RE-EMITTED from the ledger
```

## Code style

```csharp
/// <summary>
/// The highest ladder rung the claimed inserts reach. Positional over the tiers SORTED, so an
/// unordered fill (D41) and its every permutation reach the same rung; the floor names no family,
/// so no regeneration can move it.
/// </summary>
static int RungOf(IReadOnlyList<int> claimedTiers, IReadOnlyList<TierRung> ladder)
{
    var sorted = claimedTiers.OrderBy(t => t).ToArray();
    for (var r = ladder.Count - 1; r >= 0; r--)
        if (sorted.Zip(ladder[r].Floor).All(p => p.First >= p.Second)) return r + 1;
    return 0; // rung 1 not met: the combination does not fire
}
```

Tiers, rungs and deltas are `int`, bounded by `insertTiers.count` and `FamilyExpansion.TierCount`.

## Testing strategy

| Test | Asserts |
|---|---|
| `rung_one_reproduces_the_shipped_flat_floor` | every fill that fired before fires at the same granted tier |
| `higher_tier_gems_reach_a_higher_rung` | a fill upgraded by the 3:1 forge climbs one rung |
| `every_permutation_of_a_fill_reaches_the_same_rung` | D41 through the ladder |
| `attunement_adds_its_bonus_on_top_of_the_rung_and_never_gates` | D22 as amended |
| `a_fill_below_rung_one_reports_tier_shortfalls_not_missing_families` | preview truth |
| `a_ladder_whose_top_exceeds_the_atom_ladder_throws` | F7 bound |
| `a_non_ascending_or_non_increasing_ladder_throws` | load rules |
| `a_multi_rung_ladder_needs_measured_combination_pricing` | module 6 gate, from this side (R12: pricing provenance, not a count budget) |
| `a_ladder_publish_invalidates_the_previous_measurement` | provenance from the one-rung measurement + loaded v2 ladder → boot refuses by name |
| `every_reader_loads_the_current_strain_splice_revision` | the literal-scan guard extended to `strain-splice.v{n}.json` |
| `the_emitted_corpus_carries_no_tier_number` | F8, over the real re-emitted corpus |
| `rebalancing_the_ladder_needs_no_regeneration` | publish a v3 ladder in a fixture; the corpus is unchanged and the evaluator follows |
| `reemit_changes_no_model_answer` | families, grants, pins, names identical before and after |

## Boundaries

**Always:** one matcher; ladder in tuning; re-emit from the ledger; publish tuning with the tool.

**Ask first:** the `socket_combo_ingredient` DDL change; publishing ladder values beyond rung 1 as
anything other than working values.

**Never:** put a tier, floor or grant in the model schema or the corpus; order ingredients; clamp a
granted tier; call the model for a re-emit; hand-edit a combination row.

## Success criteria

- [ ] `strain-splice.v2.json` carries `tierLadder`; rung 1 equals today's floor.
- [ ] The one matcher returns a rung; the evaluator grants `baseTier + grantDelta + attuned`.
- [ ] No combination row carries `minTier` or `grantedTier`; the corpus was re-emitted without a model
      call.
- [ ] A ladder rebalance is a tuning publish and nothing else.
- [ ] The top rung cannot exceed the atom ladder.
- [ ] The ladder was priced rung by rung by `combo-budget`'s report after it was published, and the
      provenance names the ladder's revision.

## Open questions

None. The steps are tuning (ruling 4); the rest is technical.
