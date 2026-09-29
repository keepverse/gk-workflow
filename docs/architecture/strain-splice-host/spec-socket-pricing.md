# Spec: `socket-pricing`

**Module id:** `socket-pricing` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 8 of 8 (parallel with `tier-ladder`) · **Depends on:** `circuit-topology` (5),
`combo-budget` (6) · **Rulings:** 5 step 3 (*"tier-ladder + module-14 pricing"*); item D23 (*"rarity sets
the price, not the possibility"*), D24 (*"a crafted socket's affinity is chosen by the crafter, at a
cost"*); **R12** of [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md) — *"No count cap; price it
instead … scarcity comes from circuit geometry and socket/imbue cost, not a backstop count."*, **extended
to gems by R20** — *"The combo-budget report may publish a higher `forge-gem` price for those cells; one
pricing surface covers every route."*

## Objective

The Strain route is a plan: find a cheap base of the right role, **bore** its sockets, **imbue** them,
fill them. Two of those verbs must be payable for the plan to exist.

| Verb | Price curve | Recipe row a player can pay with | State |
|---|---|---|---|
| `socket-add` (`bore`) | `gk-core/data/tuning/materials.v1.json:50` — souls 50 × rung, substrate 3 × rung, catalyst flat | three rows, `gk-data/packs/fusion/data/seed/items/recipes/recipes.json` (`recipe.019` humanoid, `recipe.020` plant, `recipe.021` any) | ✅ payable |
| `socket-imbue` | `gk-core/data/tuning/materials.v1.json:56` — bore's legs verbatim plus essence 2 × rung | **none** | ⏸ *"reachable but not yet payable"* — the verb refuses `material.recipe-unknown` (`gk-core/src/FusionRpg.Server/ItemWorkbench.cs:829`) |

The imbue price is already decided and tested against bore's legs; what is missing is **content**: no
recipe row authors the verb, because the recipe generator deliberately refuses to invent a first use of
`imbue` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/opvocab.py:54`). D24 plus the priced row are
that basis now.

A second, smaller gap on the same verb: `SocketImbue` takes the element as a parameter and a recipe id
separately, and never checks that the recipe's essence line names that element
(`gk-core/src/FusionRpg.Server/ItemWorkbench.cs:835` – `:851`). A player could pay fire essence and imbue ice.

**This module now carries the combination scarcity (R12).** With `maxCombosPerActor` retired, nothing
counts how many words one actor wears; the only limits are circuit geometry and what each circuit costs.
Price is therefore not a convenience here — it is the whole balance lever for stacking combinations, and
`combo-budget`'s report is how it is checked (§5).

**Why this sits after the re-measure.** Ruling 5 puts pricing in step 3 with the ladder, after the
re-measure. Under R12 the re-measure *is* a price check: module 6 measures what each combination buys
against the cheapest legal price of wearing it and names every cell that is under-priced. This module
acts on that output.

**User outcome:** a player can open, imbue and fill a chaff chassis end to end, paying a cost that rises
with the host's rarity rung (D23) and naming the element with the essence they spend; every word they
can afford fires, and no word is a cheaper road to power than a better base.

## Design

### 1. Imbue rows are derived, so they are emitted deterministically

An imbue row carries no authored choice — frame and element fully determine it — the same argument
`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/forgegem.py` makes for forge-gem (`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/forgegem.py:1`:
*"a model call would only retype facts"*). Add (new) `recipegen/imbue.py`:

| Rule | Value |
|---|---|
| steps | one row per `(frame, element)`: frames from the bore rows' own frames, elements the concrete roster (`core.v1.json.elements.concrete`) — `omni` excluded (never an affinity, ssot-sockets §4.2) |
| cost lines | the bore row's substrate + catalyst lines for that frame, plus `essence.<element>` — the operation's four priced legs (`materials.v1.json:56`) |
| bands | the bore row's bands, verbatim — imbue prices on bore's curve (D24) |
| name / nameKey | `"Imbue: <Frame> <Element>"`, derived |
| idempotence | a step already covered by a shipped imbue row with the same `(frame, element)` is skipped; re-running converges |

`opvocab.SUPPORTED_FOR_GENERATION` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/opvocab.py:60`) is **not** widened: the model is still never offered
`imbue`. The emitter is a derivation path, exactly as forge-gem's is.

### 2. The essence must name the element

`ItemWorkbench.SocketImbue` refuses when the resolved recipe's essence line is not `essence.<element>`:
`ContentRuleViolated{socket.imbue-element-mismatch}` (new rule id in the existing `socket` namespace,
`gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:156`; no new rejection-enum member — that enum is closed).

### 3. Rarity scales the price, never the possibility (D23 re-confirmed, not changed)

Both legs are rung-linear in `materials.v1.json`; the workbench resolves them against the target's
rung (`RecipeContextFor(target)`, `ItemWorkbench.cs:866`). This module adds a test that a `chaff` host
bores cheaper than an `almanac` host, and that both succeed.

### 4. Named and deliberately out of scope

The high-rune 2:1 upcycle leg and gem-grade climb, and any rune downgrade path — the ideal names them
and does not settle them. `forge-gem`'s shipped 3:1 is unchanged.

### 5. Pricing carries the scarcity (R12, R20)

R12 retires the per-actor count cap and names price as its replacement; R20 puts the `forge-gem` leg on
the same pricing surface. What that means concretely:

| Lever | Where it lives | What it controls |
|---|---|---|
| `bore` souls / substrate coefficients (rung-linear) | `data/tuning/materials.v{n}.json` `operations.bore` (`gk-core/data/tuning/materials.v1.json:50`) | the cost of opening each socket of a circuit on a chassis that did not roll it |
| `imbue` legs (= bore's + essence, rung-linear) | `operations.imbue` (`gk-core/data/tuning/materials.v1.json:56`) | the cost of the attuned tier bonus — four imbues per circuit |
| `forge-gem` legs (priced on the output tier) | `operations.forge-gem` (`gk-core/data/tuning/materials.v1.json:43`) | the cost of the four ingredients at the ladder's floor tier — the **only** leg on the floor route of a chassis that rolled its circuit; **republished at the report's derived souls coefficient when a gem-only cell fails (R20)** |

The check is `combo-budget`'s: for every `(combination, rung)` it compares the power the word grants with
the cheapest crafted price of wearing it, against the rarity route, and exits non-zero naming each
under-priced cell, printing — per cell — the leg on that cell's floor route and the smallest souls
coefficient on it that makes the cell pass.

**Bore and imbue do not reach every cell (strengthen pass 2026-09-18).** A cell whose cheapest route is a
chassis that already rolled a full circuit (`rarityGrant[ρ].socketMax ≥ 4`: `sunwoven`/`almanac` today,
every rung from band 3 up under v2) pays no bore, and its plain variant pays no imbue; its price is its
four gems. No bore/imbue coefficient moves such a cell. The report says so by name, and the only lever
left is the `forge-gem` souls leg. **Ruled R20 (closes map §7.1 Q1): that lever is legitimate.** The
report derives the smallest `operations.forge-gem.souls.coefficient` that makes every gem-only cell pass,
and this module publishes it in the same `materials` revision as any bore/imbue coefficients — one
pricing surface for every route. species-gear-chain's `gem-tier` keeps the leg's shape and its
*"confirm, do not re-author"* stance against **hand** re-authoring; a derived republish from this report
is the one sanctioned reprice, cross-referenced there. A cell no leg can fix still keeps the report red
and is listed by id.

This module's rule when that report fails: **publish those derived coefficients** as the next materials
revision with the tool —

```powershell
python tools\tuning\publish.py materials operations.bore.souls.coefficient=<derived> operations.imbue.souls.coefficient=<derived> operations.forge-gem.souls.coefficient=<derived> --label "combination pricing (R12, R20)"
```

(each key only when the report derives a value for it; `operations.forge-gem.souls` is the leg at
`gk-core/data/tuning/materials.v1.json:45`)

— keeping imbue's legs equal to bore's plus essence (the shipped invariant), then re-run the report until
it passes and let `combo-budget` publish its provenance against the new `materialsVersion`.

**The next materials revision is a new file, and every reader moves to it (strengthen pass
2026-09-18).** The server reads `materials.v1.json` by literal (`gk-core/src/FusionRpg.Server/Program.cs:301`);
a `materials.v2.json` it never loads is a price nobody pays, and the boot provenance check (`combo-budget`
§5) would then compare against the wrong revision. This module applies `circuit-topology` §4's
one-current-revision rule to the `materials` domain in the same change as the publish. species-gear-chain
plans its own materials changes (`species-cost-shaping`) as an in-place `version` bump inside
`materials.v1.json` — which `gk-core/tools/tuning/publish.py` cannot do (it only writes `v{n+1}`,
`gk-core/tools/tuning/publish.py:556`) and which T4 forbids. Whichever program publishes first takes the next
filename; the other publishes on top of it with the tool (map §4 *Revision sequencing*, §6 C16). The derived
value is the default because it is computed, not chosen; the owner may publish a **higher** one. Never
lower than derived: that re-opens the cells the report just named.

**What this module never does in the name of scarcity:** refuse a bore, imbue or insert because an actor
already wears N words; make a price step with the number of words worn (that is a count cap wearing a
price — it would read the actor's loadout at craft time, a second path for the retired rule); gate on
rarity (D23 — price, never possibility). Every leg stays linear in the host's rung and uncapped.

## Seedsmith / generator

| Item | Detail |
|---|---|
| Adapter / stage | (new) `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/imbue.py`, precedent `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/forgegem.py:1`; reads `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/opvocab.py:88` (`CATALYST_FOR["imbue"]`) and `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/opvocab.py:105` (`ALLOWED_CLASSES["imbue"]`) for its legal legs |
| New seed fields | none new in shape — `operation: "imbue"` is already a legal enum value (`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/opvocab.py:49`); cost bands are the closed band enum |
| Magnitudes | `gk-core/data/tuning/materials.v1.json` `operations.imbue` (already published) — the emitter picks **bands**, never numbers; `materials.v2.json` (new) only when `combo-budget` names under-priced cells (§5), published with the tool |
| Regenerate | `python -m seedsmith items generate --kind recipe --write` with the imbue emitter step (dry-run first); `_meta.amendments` records the batch |
| Check | `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` · `dotnet run --project gk-forge/tools/ItemSeedValidator` · server boot import of `MaterialRecipeCatalog` (refuses unpayable rows by name) |
| Pytest | `gk-forge/tools/seedsmith/tests/test_recipes_gen.py` — `imbue_rows_are_derived_and_idempotent`, `imbue_is_never_offered_to_the_model`, `every_imbue_row_names_a_concrete_element_essence` |

## Commands

```powershell
cd tools\seedsmith
python -m seedsmith items generate --kind recipe --dry-run
python -m seedsmith items generate --kind recipe --write
python -m pytest tests/test_recipes_gen.py -q
python -m seedsmith items combo-budget --report      # must exit 0 against the published prices (R12)
cd ..\..
dotnet run --project gk-forge/tools/ItemSeedValidator
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints"
dotnet test tests\FusionRpg.Core.Tests --filter "Category=BalanceGuard&FullyQualifiedName~ComboPricing"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/imbue.py     (new)  deterministic imbue rows
gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/run.py              calls the emitter beside forge-gem
gk-data/packs/fusion/data/seed/items/recipes/recipes.json                                   GENERATED imbue rows appended
gk-core/src/FusionRpg.Server/ItemWorkbench.cs                                  essence/element check
gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs                        socket.imbue-element-mismatch rule id
gk-core/src/FusionRpg.Server/Program.cs                                        reads the current materials revision (only if one is published)
gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs            end-to-end bore → imbue → insert
```

## Code style

```python
def imbue_steps(bore_rows, concrete_elements):
    """One imbue row per (frame, element). All derivation: the bore row supplies the frame's
    substrate and catalyst legs and bands (D24 - imbue prices on bore's curve), the element
    supplies the essence leg. No model call; re-running converges."""
    for bore in sorted(bore_rows, key=lambda r: r["id"]):
        for element in concrete_elements:
            yield bore["frame"], element, bore["costLines"] + [
                {"material": f"essence.{element}", "costBand": bore["soulsCostBand"]}]
```

No magnitude is computed here; bands are enum picks read off an existing row.

## Testing strategy

| Test | Asserts |
|---|---|
| `a_chaff_chassis_can_be_bored_imbued_and_filled_end_to_end` | real workbench endpoints, real recipes, real stock debit, read back through `GetSockets` |
| `imbuing_with_a_mismatched_essence_is_refused_by_name` | `socket.imbue-element-mismatch` |
| `bore_and_imbue_cost_more_on_a_higher_rung_and_succeed_on_both` | D23: price, never possibility |
| `imbue_legs_equal_bore_legs_plus_essence` | the tuning invariant, already asserted, kept green |
| `imbue_rows_are_derived_and_idempotent` | seedsmith |
| `omni_is_never_an_imbue_element` | ssot-sockets §4.2 |
| `shipped_combination_pricing_is_bounded_by_the_rarity_route` | R12 — `combo-budget`'s BalanceGuard test, re-run against this module's published prices |
| `a_gem_only_cell_is_fixed_by_the_derived_forge_gem_coefficient` | R20: the report names the `forge-gem` leg for a cell no bore/imbue coefficient moves; after this module publishes the derived `forge-gem` souls coefficient, `combo-budget` passes that cell |
| `a_cell_no_leg_can_move_is_named_not_published` | a fixture cell even a derived `forge-gem` price cannot fix: listed by id, nothing published for it |
| `every_reader_loads_the_current_materials_revision` | the literal-scan guard extended to `materials.v{n}.json` |
| `no_price_reads_the_actors_worn_combinations` | R12 — the bore / imbue / insert cost paths take the target item and recipe only; source scan for any loadout or combination-count input on the workbench cost path |

⛔ No test asserts how many imbue rows exist; the contract is one per `(frame, concrete element)`,
computed from the inputs.

## Boundaries

**Always:** derive imbue rows; publish them through the generator with a batch record; keep imbue on
bore's curve.

**Ask first:** changing a price leg **other than** publishing `combo-budget`'s derived coefficients (§5;
bore / imbue / `forge-gem` souls under R12 + R20)
— e.g. a higher-than-derived value, or any change to substrate, essence or catalyst legs; the upcycle
high leg.

**Never:** offer `imbue` to the model; hand-add a recipe row; hand-edit a materials revision; gate
boring or imbuing on rarity; accept an imbue paid with another element's essence; publish a price below
the report's derived floor; price by the number of combinations an actor wears (R12).

## Success criteria

- [ ] `socket-imbue` is payable for every frame and concrete element.
- [ ] A mismatched essence is refused by name.
- [ ] A cheap chassis can be bored, imbued and filled to a firing Strain through the real endpoints, and
      the cost scales with the host's rung.
- [ ] `combo-budget`'s report exits 0 against the published materials revision, and its provenance names
      that revision (R12: pricing, not a count, bounds combination stacking).

## Open questions

None. Map §7.1 Q1 (may a `forge-gem` republish fix a cell bore and imbue cannot reach?) is **Ruled R20:
yes**, at the report's derived value (§5).
