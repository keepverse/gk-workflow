# Spec: `combo-budget`

**Module id:** `combo-budget` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 6 of 8 · **Depends on:** `combination-regen` (2, including its R11 helm-host re-run),
`combo-bind` (4), `circuit-topology` (5) · **Ruling:** 5's re-measure clause (*"with the per-actor budget
re-measured before any of it binds"*), **as re-read by owner ruling R12** of
[spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md): *"No count cap; price it instead … scarcity
comes from circuit geometry and socket/imbue cost, not a backstop count. `maxCombosPerActor` is retired."*
**Extended by R20** (same file): *"The combo-budget report may publish a higher `forge-gem` price for those
cells; one pricing surface covers every route."* · **Gates:** `tier-ladder` (7) and `socket-pricing` (8).

> **Rewritten 2026-09-18 for R12.** The first draft re-measured a per-actor count cap and published a new
> `maxCombosPerActor`. R12 retires the cap, so there is no count to re-measure. What ruling 5 still
> requires — *measure before the ladder and the prices bind, against the corpus that will ship* — now
> means measuring **what a combination buys against what it costs**. The module id is kept so every
> cross-reference stays valid.

## Objective

The per-actor cap shipped as `maxCombosPerActor: 3` (`gk-core/data/tuning/sockets.v1.json:25`) with no
production caller (`SocketCombinationCap.Apply`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:237` — **deleted by R12/SSH4.1; the line is gone**).
R12 retires it: `combo-bind` deletes the code and `circuit-topology` drops the key from `sockets.v2.json`.

With no count, two things bound how many combinations one actor profits from:

1. **Geometry** — one Strain/Splice per complete four-socket circuit. After `circuit-topology` that is
   `Σ floor(socketCeiling(role) / SocketCircuitSize)` over the equipped roles, built from two structural
   constants (`SocketMaxCeiling`, `SocketCircuitSize`) and the tuned ceilings. It is a **reading**, not a
   limit anyone tunes to restrict combinations.
2. **Price** — a word lives in a cheap chassis whose sockets are bored (and optionally imbued) one at a
   time on rung-linear legs (`gk-core/data/tuning/materials.v1.json:50` bore, `:56` imbue), and is filled with
   four gems whose cost climbs with tier — `forge-gem` prices on the output tier
   (`gk-core/data/tuning/materials.v1.json:18`, `:43`) and the upcycle route consumes
   `insertTiers.upcycleInputPerOutput` gems per step (`gk-core/data/tuning/sockets.v1.json:49`).

This module makes the second bound **checked, not assumed**. The ideal names the risk: tuning the ladder
against a measurement taken before the 25→102 regeneration and the circuit revision *"would be tuning
against a corpus that no longer exists."* item-ideal's chaff-inversion watch names what to measure: whether
a chaff chassis plus a word buys more power than a rarer base does
([item-ideal.md](../item-ideal.md) line 1513).

1. **Measure** — a deterministic report of the power each combination grants against the cheapest legal
   price of wearing it, compared with the rarity route's power per price.
2. **Prove** — the report fails, naming each `(combination, rung)` cell, when a combination buys power more
   cheaply than the rarity route. The fix is a price publish in `socket-pricing`, **never a count**.
3. **Make the clause mechanical** — the ladder's tuning refuses to load until the report has passed against
   the current socket and material revisions.

**User outcome:** every Strain and Splice a player can build fires; wearing more of them costs more, and
no combination is a cheaper route to power than finding a better base.

## Design

### 1. The measurement

For every enabled Strain/Splice `c`, every rung `k` of the ladder (one rung until `tier-ladder` ships),
and both the plain and the fully attuned variant:

```text
power(c, k)       = ActorPowerCache.Compose( atoms of ComboContainerBuild(c, grants, tier) ).Total
                    tier = baseTier / ladder rung k  (+ attunedTierBonus for the attuned variant)

priceFloor(c, k)  = min over host rarity rungs ρ admitted for c of
                      bores(ρ) · bore(ρ)  +  imbues · imbue(ρ)  +  Σ over the 4 ingredients gem(minTier_k(i))
    bores(ρ)      = max(0, SocketCircuitSize − rarityGrant[ρ].socketMax)   the best-rolled chassis: the cheapest legal route
    imbues        = 0 for the plain variant, SocketCircuitSize for the attuned one
    bore/imbue(ρ) = souls leg of the operation's recipe at rung ρ          MaterialRecipeCatalog.Resolve
    gem(t)        = souls leg of forge-gem resolved at output tier t          (rung input = output gem tier,
                    gk-core/data/tuning/materials.v1.json:18), or of the upcycle chain from t−1 if cheaper

ratio(c, k)       = power(c, k) · 1000 / priceFloor(c, k)                   power per 1000 souls

reference(ρ)      = (PriceReferenceSlate(ρ+1) − PriceReferenceSlate(ρ)) · 1000 / elevate(ρ)
                    the rarity route: what one rung of base buys, per 1000 souls of elevate

bound holds  ⇔  for every cell, ratio(c, k) · 1000 ≤ min_ρ reference(ρ) · comboPricing.maxRatioToRarityRouteMilli
```

**Edge rules (strengthen pass 2026-09-18) — each refuses or excludes by name, none clamps:**

- **Evaluated cross-multiplied, not as two truncated quotients.** The comparison is
  `power(c,k) · elevate(ρ*) · 1000 ≤ ΔPower(ρ*) · priceFloor(c,k) · maxRatioToRarityRouteMilli` in `long`,
  `checked`, where `ρ*` is the step that attains the minimum reference. Computing `ratio` and `reference`
  first truncates twice, and a truncated `ratio` can pass a cell that fails by less than one per-mille.
  `ratio` and `reference` are still **printed**, as readings.
- **The top rung has no `ρ+1`** and contributes no reference step.
- **A step whose `ΔPower ≤ 0` is excluded from the minimum and printed by name.**
  `PriceReferenceSlate` returns 0 for a rung with no affix slots
  (`gk-core/src/FusionRpg.Core/Items/Power/RarityPowerCeiling.cs:202`), so an early step can buy nothing; a step
  that buys nothing is an infinitely dear rarity route, and letting it into the minimum would demand every
  word be free. If **every** step is excluded, the report refuses by name — there is no rarity route to
  compare against, which is a content defect, not a pass.
- **`priceFloor` is never 0:** `gem(t)` carries a `rung`-variable souls leg evaluated as
  `coefficient · (rungIndex + 1)` (`gk-core/src/FusionRpg.Core/Items/Materials/MaterialTuning.cs:39`), so four gems
  always cost something. A zero floor is refused by name rather than divided by.

Every function above already exists — nothing here writes a second curve:

| Term | Source |
|---|---|
| combination power | `ActorPowerCache.Compose` (`gk-core/src/FusionRpg.Core/Effects/Atoms/Power/ActorPowerCache.cs:53`), `PowerVector.Total` (`gk-core/src/FusionRpg.Core/Effects/Atoms/Power/PowerVector.cs:62`), over the containers `combo-bind` builds |
| rarity-route power | `RarityPowerCeilings.PriceReferenceSlate` (`gk-core/src/FusionRpg.Core/Items/Power/RarityPowerCeiling.cs:200`) — prices the rung's reference slate through the same `Compose`, so both sides share one unit |
| prices | `MaterialRecipeCatalog.Resolve` (`gk-core/src/FusionRpg.Core/Items/Materials/MaterialRecipeCatalog.cs:318`) over `materials.v{n}.json` `bore`, `imbue`, `forge-gem`, `elevate` (`gk-core/data/tuning/materials.v1.json:43`, `:50`, `:56`, `:69`) |
| socket windows | `rarityGrant` in the current socket revision |
| geometry | `SocketGeometry.GeometricCombinationCeiling` (new, below) |

**Souls is the unit of price.** No exchange rate across material classes exists, so the report prices in
the souls leg (present on bore, imbue, forge-gem and elevate) and prints every other leg beside it. The
cheaper-than-rarity check is therefore a souls check; the other legs are readings the owner sees.

**Worst case, not average — over the craft route.** `priceFloor` is the **cheapest crafted** way to wear
the word (the best-rolled chassis, the cheapest rung that admits it), so a pass bounds every other
crafted route too. It is a craft-route comparison on **both** sides: the rarity side is priced by
`elevate`, not by a lucky drop, and the word side by `bore`/`imbue`/`forge-gem`, not by a dropped gem or a
dropped pre-socketed chassis. Drops are free on both sides and are excluded symmetrically — the report
says so in its header rather than claiming to bound a drop.

**Which lever moves a failing cell.** The floor route at a rung whose `rarityGrant[ρ].socketMax ≥
SocketCircuitSize` needs **no** bore — under v1 that is already `sunwoven`/`almanac` (`2/4`,
`gk-core/data/tuning/sockets.v1.json:36` – `:37`), and under the v2 table (`circuit-topology` §1) every rung from
band 3 up. The plain variant needs no imbue either. For such a cell `bore` and `imbue` do not appear in
`priceFloor` at all, and **no bore/imbue coefficient can make it pass**; only the gem leg moves it. So the
report's derived fix is per cell and names the leg that is actually on that cell's floor route: `bore`
and/or `imbue` where they appear, `forge-gem` souls where they do not. **Ruled R20 (2026-09-18,
closes map §7.1 Q1): the `forge-gem` souls leg is a legitimate lever.** R20 extends R12's *"socket/imbue
cost"* to gems — one pricing surface covers every route. So a gem-only cell is no longer a red-by-name
dead end: the report **derives** the smallest `forge-gem` souls coefficient that makes it pass (the same
derivation as bore/imbue, never a hand-picked number), and `socket-pricing` publishes it with the tool.
species-gear-chain's `gem-tier` still owns the leg's *shape* (souls ×coef on `rung` = output gem tier,
`gk-core/data/tuning/materials.v1.json:43`); its *"confirm, do not re-author"* now means *do not re-author by hand*
— the souls coefficient is repriced only by this report's derived number, as a `materials.v{n+1}` publish
sequenced per both maps' revision tables (strain-splice-host map §4 *Revision sequencing*;
[species-gear-chain-map.md](../species-gear-chain-map.md) § Tuning revisions, `materials` row). A cell
that **no** leg can fix — not even a derived `forge-gem` price — is still listed by id and fails.

### 2. The geometry reading — one function, two ports, one agreement test

`geometric_combo_ceiling` exists in Python only and counts roles, not circuits
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:68`, returns `len(host_roles)`). It becomes
circuit-aware, stops being compared to a cap, and gains a C# twin:

```text
geometricCeiling(frame) = Σ over the frame's equip roles r of floor(socketCeiling(r) / SocketCircuitSize)
reachableCeiling(frame) = same sum, restricted to roles that at least one ENABLED Strain/Splice admits
                          (a recipe with no hostRole admits every role)
```

C#: (new) `SocketGeometry.GeometricCombinationCeiling(tuning, roles)` beside `RolesThatCanHostAStrain`
(`gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs:101`). A test asserts the two ports agree against the
same shipped file — the pattern `host_roles()` already uses (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60`).
Printed by the report; **never an acceptance value**.

### 3. The report

New CLI verb, `python -m seedsmith items combo-budget --report`. It prints, per frame: both geometric
readings, the per-role circuit count, the enabled combinations per admitted role (the helm included after
R11); per cell: `power`, `priceFloor` and all its legs, `ratio`, the reference, and pass/fail. Then, **when
any cell fails**, per failing cell the leg(s) on its floor route and the smallest souls coefficient on
those legs that would make it pass, and overall the smallest `bore` / `imbue` / `forge-gem` (R20)
coefficients that make every cell pass — derived, so `socket-pricing` publishes a computed
number rather than a guess. A cell no permitted leg can fix is listed as such.

The report **exits non-zero** when a cell fails. It asserts nothing about the size of any reading.

The C# side runs the same computation in a Core.Tests `[Trait("Category","BalanceGuard")]` test over
the shipped tuning and corpus, so CI's existing BalanceGuard filter enforces it; the Python report is the
readable form of the same numbers (parity test, §Testing).

### 4. The tunable — a bounded ratio, published with the tool

Published as the next socket revision by `--add-key` — `gk-core/data/tuning/sockets.v3.json` if nothing else has
published a sockets revision after `circuit-topology`'s v2 (map §4, *Revision sequencing*):

```jsonc
"comboPricing": {
  "maxRatioToRarityRouteMilli": 1000,
  "measuredAgainst": { "socketsVersion": 2, "strainSpliceVersion": 1, "materialsVersion": 1, "circuitSize": 4, "combinationCorpusDigest": "<sha256>" },
  "note": "BOUNDED RATIO, exempt from the no-hard-ceilings rule and saying so: it limits how cheaply a combination buys power RELATIVE to the rarity route, checked when tuning or content is published. It never refuses, suppresses or clamps anything a player does. 1000 = a word is never a cheaper route to power than a better base (D23: rarity sets the price, not the possibility)."
}
```

**Default `1000`** is not a guess: it is D23 stated as arithmetic — a combination may equal, never
undercut, the rarity route. A balance pass may loosen it (say 1200, "words are a slightly better deal")
with a publish, never a rebuild.

`measuredAgainst` is written **only when the report passes**. If it fails, `socket-pricing` publishes the
report's derived coefficients into the next materials revision, the report is re-run, and the provenance
is published then with that `materialsVersion`.

**What each provenance field means (strengthen pass 2026-09-18).**

| Field | Value | Why it is needed |
|---|---|---|
| `socketsVersion`, `strainSpliceVersion`, `materialsVersion` | the **filename** revision `n` of `<domain>.v{n}.json` — what `gk-core/tools/tuning/publish.py` `latest_version` reads (`gk-core/tools/tuning/publish.py:60`) — **never** the file's internal `"version"` field | the two disagree today: `sockets.v1.json` carries `"version": 3` (`gk-core/data/tuning/sockets.v1.json:3`, bumped in place by species-gear-chain T4, `72607c136`), and `publish.py` rewrites `doc["version"] = n+1` (`gk-core/tools/tuning/publish.py:552`), so v2's internal version would be 2 — *lower* than v1's. Only the filename is monotonic |
| `strainSpliceVersion` | as above | **without it a multi-rung ladder binds against a one-rung measurement:** this module runs before `tier-ladder` and measures rung 1 only; `tier-ladder` then publishes `strain-splice.v2.json` with more rungs, and a presence-only gate would accept the old provenance. Every ladder publish therefore invalidates the provenance until the report is re-run (`tier-ladder` §1) |
| `combinationCorpusDigest` | SHA-256 over the accepted Strain/Splice set (ids, ingredient families, grants, host pins, sorted) as `recipe-import` + `combo-bind` accept it | the corpus moves without any tuning file moving — `combination-regen`'s R11 re-run, and every R13 per-id ruling applied later — and a new word is new power nobody priced |
| `circuitSize` | `SocketCircuitSize` | a structural reading, recorded so a future change to it cannot reuse the measurement |

### 5. The gate — the ladder cannot bind against unmeasured prices

`SocketTuning` exposes the provenance (new `ComboPricingMeasuredAgainst`). The parsers cannot enforce it
alone — `StrainSpliceTuning.Parse` (`gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs:76`) is handed
file *text* and never learns which revision it read — so the check is one pure Core function (new)
`ComboPricingProvenance.Check(measuredAgainst, loadedRevisions, corpusDigest, ladderRungs)`, called by the
server at boot once sockets, strain-splice, materials and the accepted combination set are all loaded, and
by the Python report at start. It refuses by name when:

- the ladder has more than one rung and `comboPricing.measuredAgainst` is absent, **or**
- `comboPricing` is present and any of `socketsVersion`, `strainSpliceVersion`, `materialsVersion`,
  `combinationCorpusDigest` differs from what was loaded.

Today's single flat floor with no `comboPricing` at all is unaffected, so nothing breaks before this
module ships.

**Where the bound is enforced — stated, because it is never a play-time check.** R12 and D23 forbid
refusing a player action on price-per-power grounds, so there is deliberately **no** runtime check at
bore, insert or bind. The bound is enforced at three points, and together they leave no silent path:

| Point | Catches |
|---|---|
| the report's exit code, at publish time | an under-priced cell before any provenance is written |
| the BalanceGuard test in CI (`.github/workflows/ci.yml:140`, `Category=BalanceGuard`) over the **shipped** tuning and corpus, recomputing the inequality — never trusting `measuredAgainst` | every commit that moves power or price by *any* route, including those provenance cannot see: atom-family magnitudes (`gk-data/packs/fusion/data/seed/items/affix-families/**`), power tables, a hand-typed provenance |
| `ComboPricingProvenance.Check` at server boot | a local tree whose tuning revisions or combination corpus moved after the last passing measurement |

### 6. No-hard-ceilings, checked

| Number | Kind | Why it is not a progression ceiling |
|---|---|---|
| `SocketCircuitSize`, `SocketMaxCeiling` | structural (commented `const`s, `circuit-topology`) | legibility limits on one item's recipe shape |
| `geometricCeiling` | reading | printed, never enforced |
| `maxRatioToRarityRouteMilli` | bounded ratio | a content/tuning validation threshold; no player action is ever refused by it |
| bore / imbue / forge-gem legs | tunable, rung-linear, uncapped | price scales, never forbids (D23) |

## Seedsmith / generator

| Item | Detail |
|---|---|
| Adapter / stage | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:68` (`geometric_combo_ceiling` → circuit-aware reading); `max_combos_per_actor` is **already gone** — deleted by `combo-bind` (module 4), which must land before `circuit-topology` points the reader at a revision without the key; report verb (new) registered beside `combogen-migrate` in `gk-forge/tools/seedsmith/seedsmith/report/cli.py:3146` |
| New seed fields | none — no corpus is written |
| Magnitudes | `gk-core/data/tuning/sockets.v3.json` (new): `comboPricing.maxRatioToRarityRouteMilli`, `comboPricing.measuredAgainst`; prices stay in `data/tuning/materials.v{n}.json` |
| Regenerate | none (read-only report) |
| Check | `python -m seedsmith items combo-budget --report` (exit code is the check) |
| Pytest | `gk-forge/tools/seedsmith/tests/test_combogen.py` — circuit-aware geometry, price floor, pass/fail, provenance check (the backstop test at `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py:245` is `combo-bind`'s deletion, not this module's) |

## Commands

```powershell
cd tools\seedsmith
python -m seedsmith items combo-budget --report
python -m pytest tests/test_combogen.py tests/test_strain_splice_gen.py -q
cd ..\..
python tools\tuning\publish.py sockets --add-key ":comboPricing={\"maxRatioToRarityRouteMilli\":1000,\"measuredAgainst\":{<printed by the passing report>},\"note\":\"...\"}" --label "combination pricing measured"
# the passing report prints the exact measuredAgainst object (revisions + corpus digest); it is copied, never typed
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

## Project structure

```text
gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs          GeometricCombinationCeiling (new member)
gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs     (new)  power / priceFloor / reference / bound
gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs            comboPricing parse + ComboPricingMeasuredAgainst
gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricingProvenance.cs (new) the one provenance check (boot + report)
gk-core/src/FusionRpg.Server/Program.cs                             calls the check once every input is loaded
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py circuit-aware reading
gk-forge/tools/seedsmith/seedsmith/report/cli.py                     items combo-budget --report (new verb)
gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboPricingTests.cs (new) incl. the BalanceGuard test
gk-core/data/tuning/sockets.v3.json                          (new, published)
```

## Code style

```csharp
/// <summary>
/// The cheapest legal price of wearing one combination, in souls. The best-rolled chassis at the
/// cheapest admitting rung — a bound on the cheapest route bounds every route.
/// </summary>
public static long PriceFloorSouls(ComboRecipe recipe, int rung, bool attuned, ComboPricingInputs inputs)
{
    checked
    {
        long best = long.MaxValue;
        foreach (var rho in inputs.RungsAdmitting(recipe))
        {
            long bores = Math.Max(0, SocketLimits.SocketCircuitSize - inputs.RolledMax(rho));
            long imbues = attuned ? SocketLimits.SocketCircuitSize : 0;
            long price = bores * inputs.BoreSouls(rho) + imbues * inputs.ImbueSouls(rho) + inputs.GemsSouls(recipe, rung);
            best = Math.Min(best, price);   // selection of the cheapest route, not a clamp
        }
        return best;
    }
}
```

**Integer widths.** Prices are `long` and `checked`: souls legs are rung-linear, and the upcycle route
in `gem(t)` multiplies by `upcycleInputPerOutput` per tier, which grows geometrically with the ladder's
top tier — widen before multiplying, throw on overflow, never wrap. `ratio` is per-mille in `long` and divides last. Power points
are `int` per `PowerVector` category, widened to `long` before the `· 1000`. Counts (circuits, rungs) are
`int`, bounded by 15 roles × 2 circuits.

## Testing strategy

| Test | Asserts |
|---|---|
| `geometric_ceiling_counts_complete_circuits_not_roles` | fixture tuning: an 8-ceiling role contributes 2, a 6 or a 4 contributes 1, a 3 contributes 0 |
| `python_and_csharp_readings_agree_on_the_shipped_tuning` | geometry and price-floor parity, no literal |
| `price_floor_takes_the_cheapest_admitting_rung_and_best_rolled_chassis` | fixture: the minimum is selected, bores never negative |
| `a_combination_cheaper_than_the_rarity_route_fails_the_report_by_cell` | fixture prices: exit non-zero, the failing `(combo, rung)` named |
| `the_derived_coefficient_makes_every_cell_pass` | re-running with the printed coefficients passes |
| `shipped_combination_pricing_is_bounded_by_the_rarity_route` | **BalanceGuard**, real tuning + corpus: the bound holds for every cell — a contract, no count |
| `a_multi_rung_ladder_refuses_unmeasured_pricing` | `ComboPricingProvenance.Check` refuses a >1-rung ladder with no provenance |
| `a_ladder_published_after_the_measurement_is_refused_until_re_measured` | provenance `strainSpliceVersion` 1, loaded revision 2 → refused by name; the rung-1-only measurement cannot vouch for rungs 2..n |
| `boot_refuses_a_revision_or_corpus_the_pricing_was_not_measured_against` | each of the four fields, one at a time, refused by name |
| `provenance_versions_are_filename_revisions_not_the_internal_version_field` | a fixture where the two disagree (as `sockets.v1.json` does today) → the filename wins |
| `a_rarity_step_that_buys_nothing_is_excluded_by_name` | `ΔPower ≤ 0` step printed and left out of the minimum; all steps excluded → refused |
| `the_comparison_is_cross_multiplied` | a fixture cell failing by less than one per-mille fails (two truncated quotients would pass it) |
| `a_cell_with_no_bore_or_imbue_on_its_floor_route_names_forge_gem_as_its_lever` | top-band fixture: the derived fix names the gem leg, never a bore coefficient that cannot move the cell |
| `the_derived_forge_gem_coefficient_makes_a_gem_only_cell_pass` | R20: top-band fixture where only the gem leg is on the floor route; re-running with the printed `forge-gem` souls coefficient passes, and the coefficient is the smallest that does (one below it still fails) |
| `a_single_rung_ladder_loads_without_provenance` | today's file keeps loading |
| `no_combination_count_cap_exists` | source scan: no `MaxCombosPerActor` / `max_combos_per_actor` / `SocketCombinationCap` identifier in `src/`, `tools/`, `tests/`; the current socket revision carries no `maxCombosPerActor` key |

⛔ No test asserts the geometric reading's value, a combination's power, a price, or a ratio on the shipped
files. The BalanceGuard test asserts the **inequality**, which is the contract.

## Boundaries

**Always:** measure against the current socket and material revisions and the regenerated corpus
(helm-hosted cells included); price the cheapest route; publish with the tool; record provenance only on
a pass.

**Ask first:** moving `maxRatioToRarityRouteMilli` off its D23 default of 1000.

**Never:** reintroduce a count of active combinations in any form (tunable, `const`, UI limit, or
"soft" suppression); refuse or suppress an insert or a firing combination; derive the bound in code;
invent a material exchange rate; let the ladder bind against unmeasured prices.

## Success criteria

- [x] The circuit-aware geometry reading exists in both languages and they agree; nothing compares it to a cap.
- [x] The report prices every enabled combination at every rung against the rarity route and exits non-zero
      on any failing cell, printing the coefficients that would fix it.
- [x] The BalanceGuard test holds on the shipped tuning and corpus.
- [x] `comboPricing` is published with provenance naming the socket and material revisions it passed against.
- [x] A multi-rung ladder cannot load against unmeasured pricing, and no tuning revision or corpus change
      made after the last passing measurement loads at boot without a re-measure.
- [x] No per-actor combination count exists anywhere in code, tuning's current revision, or tests.

## Open questions

None. The strengthen pass's Q1 (map §7.1) — may a `forge-gem` republish fix a cell whose cheapest route
has no bore or imbue leg? — is **Ruled R20: yes**; the report derives the price (§1, §3). R12 answered the
old owner question (map §7, former O2); the default bound is D23 as arithmetic.
