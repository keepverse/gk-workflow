# Spec: `host-gate`

**Module id:** `host-gate` · **Program:** [strain-splice-host](../strain-splice-host-map.md) · **Build
order:** 1 of 8 · **Depends on:** — · **Rulings:** 1 (host never changes), 2 (coarse pins), 3 (helm is
a tuning row — its *value* revised to 4 at `sockets.v2.json` by R11 of
[spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md); the tuning-row *shape* this module enforces
is unchanged) · **Findings closed:** F4, F5, F6.

## Objective

Make the host side of a Strain/Splice **one** thing before anything else in this program extends it.

Before this module (SSH1.1), the question *"can this item carry this combination?"* was answered in
two places and the question *"does this fill satisfy this recipe?"* in two more:

**CLOSED by strain-splice-host SSH1.1 (2026-09-20)** — the table below described the fork as it stood
before that task; both columns now call one matcher, `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs`
(`HostAdmits`, `Match`). Kept as the historical record of what SSH1.1 fixed, per
`tasks/evidence-fragments/SSH1.1.md`.

| Question | Evaluator (the SSOT) | Preview copy |
<!-- citations-historical: this table describes the pre-SSH1.1 duplication this module fixed. CombinationEvaluator.HostMatches and MultisetSatisfied were extracted into the single gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs (HostAdmits at :46, Match at :68), now called by both CombinationEvaluator and CombinationDistance -- neither old method exists any more. -->

| Question | Evaluator (the SSOT, before SSH1.1) | Preview copy (before SSH1.1) |
|---|---|---|
| Host matches recipe | `CombinationEvaluator.cs:180` `HostMatches` (deleted; now `ComboMatcher.cs:46` `HostAdmits`) | `CombinationDistance.cs:175` `Reachable` (kept; now calls `ComboMatcher.HostAdmits`/`CanEverHold`) |
| Fill satisfies recipe | `CombinationEvaluator.cs:169` `MultisetSatisfied` (deleted; now `ComboMatcher.cs:68` `Match`) | `CombinationDistance.cs:211` `MultisetShortfall` (deleted; now calls the same `ComboMatcher.Match`) |

The preview's own doc comment forbids exactly this (`CombinationDistance.cs:70` — *"two functions is how
'the tooltip said one more and it did not fire' happens"*), and CLAUDE.md's SOLID rule forbids
extending a forked seam until the fork is fixed. `tier-ladder` (module 7) changes the matcher; if the
fork survives, the ladder lands in one copy and the preview lies. **So this module is first.**

It also closes two defects on the same seam and turns rulings 1–3 into tests:

- **F5** — `GET /api/items/{instanceId}/combinations` builds its host as
  `new SocketHost(instance.ContainerId, ItemRole.ArmamentPrimary, "", slots.Count)`
  (`gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs:183`): every item is an armament-primary with no frame
  and never a set piece, so a `core-guard`-pinned Splice previews as unreachable on a breastplate and a
  set piece previews Strains as reachable. The item-card path builds the real host
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemCard.cs:411`).
- **F6** — reachability compares `recipe.MinSockets > host.SocketCount` (`CombinationDistance.cs:177`)
  where `SocketCount` is the **opened** count. A chaff breastplate with 0 opened and `socketMax` 4 reads
  *undiscovered* for every Strain, although `socket-add` will open all four (D23;
  [ssot-sockets.md](../item/ssot-sockets.md) line 136: *"a bad socket roll is therefore a cost, not a
  discard"*). "Can never carry" is a capacity fact, not a fill fact.

**User outcome:** the socket bench and item card tell the player the truth about which words an item can
host — including a cheap base they have not bored yet — from the same code that decides whether the word
fires.

## Design

### 1. One predicate, one matcher

Extract (new) `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs`:

| Member | Replaces | Contract |
|---|---|---|
| `HostAdmits(SocketHost host, ComboRecipe r)` | `HostMatches` + first half of `Reachable` | role pin, frame pin, D21 set exclusivity for Strain/Splice shapes. **No socket count** — that is the next two members' job |
| `CanEverHold(SocketHost host, ComboRecipe r)` | `Reachable`'s count arms | `r.MinSockets <= host.Capacity` (and the resonance threshold arms against `Capacity`) |
| `Fits(SocketHost host, ComboRecipe r)` | `HostMatches`' count arm | `r.MinSockets <= host.SocketCount` (opened) |
| `Match(ComboRecipe r, IReadOnlyList<SocketFill> fill)` → `MatchResult(Claimed, Missing)` | both multiset loops | the shipped claiming discipline verbatim (most-specific-first, cheapest-qualifying, socket-index tiebreak); `Missing` is the shortfall list the preview renders |

`CombinationEvaluator.Evaluate` calls `HostAdmits && Fits` and `Match(...).Missing.Count == 0`;
`CombinationDistance` calls `HostAdmits && CanEverHold` for reachability and `Match(...).Missing` for
distance. Behaviour of the evaluator is unchanged byte for byte; the preview changes only where F6 made
it wrong.

### 2. `SocketHost` carries capacity

`SocketHost` (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:104`) gains `int Capacity` — the base
type's own `socketMax`, the value `socket-add` already caps at (`SocketOperations.cs:41`). Invariant,
thrown at construction: `0 <= SocketCount <= Capacity`. Both host builders fill it from the one lookup
the workbench already uses (`BaseTypeSocketMaxCorpus.Load`, `gk-core/src/FusionRpg.Server/WorkbenchEndpoints.cs:262`).

### 3. One host builder (F5)

Extract the item-card builder at `RpgStore.ItemCard.cs:411` into one store method (new)
`RpgStore.SocketHostFor(instanceId, Func<string,int?> socketMaxFor)` and call it from both the item
card and `ItemSurfaceEndpoints.cs:183`. The endpoint's hard-coded role, frame and set flag are deleted.

### 4. Rulings 1–3 as enforced contracts (no new behaviour)

| Ruling | Contract | Where it already holds | Test that proves it (new) |
|---|---|---|---|
| **1** — a combination never changes host rarity, tier window or fingerprint | socket operations and combination evaluation write no host `effect_instance` / `effect_instance_atom` row | `SocketOperations.cs:20` (doc), the op set in `SocketOperations.cs:32`; ssot-sockets §4.8 | fill a host to a firing Strain through the real workbench; assert host `InstanceRow.ContentFingerprint()` and `item_generation.rarity_ordinal` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs:127`) unchanged before and after |
| **2** — pins stay role / frame / size + non-set | `ComboRecipe` has no base-type, slot or container field; the generator schema offers none; the C# kind catalog accepts none | `SocketModel.cs:124`, `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:65` | reflection over `ComboRecipe`; field-name absence over `combination_schema`; `KindCatalog` extra-field set |
| **3** — the helm's ceiling is a tuning row (3 in v1; **4 in v2, R11**) | no role-specific branch or constant on the socket path; `head-guard` is reached only through `CeilingFor`; whether a role **hosts a word** is derived from its ceiling and `ingredientCount`, never named | `SocketTuning.cs:180`, `SocketGeometry.cs:85`, `SocketGeometry.cs:101` (host set); Python `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60` feeding `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:75` | source scan of `gk-core/src/FusionRpg.Core/Items/Sockets/**` and the workbench for `HeadGuard`/`head-guard` outside the role table; **plus the R11 derivation test**: a fixture tuning moving `head-guard` 3 → 4 puts the helm in `RolesThatCanHostAStrain` and in the Python `host_roles()` / schema `hostRole` enum, with no code change between the two runs |

**D21's "low rarity" is not a gate** ([map](../strain-splice-host-map.md) §6 C5): ruling 2 enumerates the
gate, and D23 makes the chassis cheap by price. No rarity arm is added to `HostAdmits`.

### 5. Craft-path role-ceiling hardening (ruling 3's one missing check)

`socket-add` caps at the base's own `socketMax` and never reads the role ceiling
(`SocketOperations.cs:32` takes an `int`; `ItemWorkbench.cs:687`). The corpus validator refuses a base
above its role ceiling at authoring time (`gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs:43`), but the
runtime lookup trusts the file. **Harden the one place the runtime reads it:** `BaseTypeSocketMaxCorpus.Load`
runs `SocketGeometry.ValidateEntry(role, socketMax, tuning)` (`SocketGeometry.cs:85`) per row and
**refuses the row by name** (the lookup returns `null`, which the workbench already refuses as
`socket.base-type-socket-max-unavailable`). No new rule id, no role branch, no `TryAdd` overload — the
helm stays a tuning row and a corrupt helm row can no longer be bored past its role ceiling (3 under
v1, 4 once `circuit-topology` publishes v2 — the check reads the row, so it needs no change at R11).

## Seedsmith / generator

**No generator changes in this module.** It asserts the *absence* of a per-base key in the generator's
output contract, which is ruling 2's grammar.

| Item | Detail |
|---|---|
| Adapter / stage | none changed; guarded: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:65` (`combination_schema`), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:144` (`assemble_entry`) |
| New seed fields | none — a test asserts no `baseType`/`baseTypeId`/`slot`/`container` field appears |
| Magnitudes | none; ceilings stay in `gk-core/data/tuning/sockets.v1.json` |
| Check | `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` |
| Pytest | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — add `test_the_schema_offers_no_base_type_or_slot_pin` |

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~ItemSurface"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BaseTypeSocketMaxCorpus|FullyQualifiedName~ItemPreviewEndpoints|FullyQualifiedName~ItemCardEndpoints"
cd tools\seedsmith; python -m pytest tests/test_strain_splice_gen.py -q
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

## Project structure

```text
gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs          (new)  the one predicate + one matcher
gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs         calls ComboMatcher; HostMatches/MultisetSatisfied deleted
gk-core/src/FusionRpg.Core/Items/Surfaces/CombinationDistance.cs         calls ComboMatcher; Reachable/MultisetShortfall deleted
gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs                  SocketHost gains Capacity
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemCard.cs                   SocketHostFor extracted
gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs                     uses SocketHostFor
gk-core/src/FusionRpg.Server/WorkbenchEndpoints.cs                       BaseTypeSocketMaxCorpus validates per row
gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboMatcherTests.cs      (new)
```

## Code style

```csharp
/// <summary>
/// The ONE answer to "may this host ever carry this recipe". Capacity, never the opened count:
/// socket-add tops any base up to its own socketMax (D23), so a bore away is not "never".
/// </summary>
public static bool CanEverHold(SocketHost host, ComboRecipe recipe) =>
    HostAdmits(host, recipe) && recipe.MinSockets <= host.Capacity;
```

Counts are `int`: a socket count is bounded by the structural ceiling (4 today, 8 after
`circuit-topology`), nowhere near `int`'s range, and never scales with `Θ`.

## Testing strategy

| Test | Asserts |
|---|---|
| `evaluator_and_preview_share_one_matcher` | reflection: no `MultisetSatisfied`/`MultisetShortfall`/`Reachable`/`HostMatches` remains; both call sites resolve to `ComboMatcher` |
| `a_fill_the_preview_reports_at_distance_zero_is_a_fill_the_evaluator_fires` | property over generated fills against the shipped recipe shapes — the one-function guarantee |
| `an_unbored_chassis_with_capacity_reads_reachable_not_undiscovered` | F6: `SocketCount` 0, `Capacity` 4, a 4-ingredient Strain → reachable, distance 4 |
| `a_host_whose_capacity_is_below_the_recipe_is_undiscovered` | the permanent case still reads undiscovered |
| `the_combinations_endpoint_reads_the_real_role_frame_and_set_flag` | F5: a `core-guard` humanoid host previews a `core-guard`-pinned Splice as reachable; a set piece never previews a Strain |
| `socket_host_refuses_opened_above_capacity` | construction invariant throws |
| `filling_a_strain_leaves_the_host_fingerprint_and_rarity_unchanged` | ruling 1, through the real workbench, read back through the store |
| `no_combination_contract_carries_a_base_or_slot_key` | ruling 2 — C# record, C# kind catalog, Python schema |
| `no_socket_path_branches_on_head_guard` | ruling 3 source scan |
| `a_role_hosts_a_word_iff_its_ceiling_reaches_the_ingredient_count` | R11 by derivation, both ports: fixture `head-guard` 3 → not a host; fixture `head-guard` 4 → host in `RolesThatCanHostAStrain`, `host_roles()` and the schema's `hostRole` enum. Asserts the rule, never the shipped host list |
| `a_helm_host_is_admitted_by_the_one_matcher_at_four_sockets` | `ComboMatcher.CanEverHold` on a `head-guard` host with capacity 4 and an unpinned Strain → true; at capacity 3 → false (capacity, not role, decides) |
| `a_base_row_above_its_role_ceiling_is_refused_at_load` | the hardening: lookup returns `null`, workbench refuses by name |

No test asserts how many recipes, bases or items exist.

## Boundaries

**Always:** keep the evaluator's observable output unchanged except where F5/F6 made the preview wrong;
refuse by name; read capacity from the same lookup the workbench uses.

**Ask first:** none — this module changes no schema, no tuning and no corpus.

**Never:** add a rarity arm to the host gate (C5); add a helm branch or `const`; keep either duplicate
"for compatibility"; let the preview call anything but `ComboMatcher`.

## Success criteria

- [ ] Exactly one host predicate family and one multiset matcher exist; the evaluator and the preview
      both call them; the duplicates are deleted.
- [ ] Reachability reads capacity; the fill test reads opened sockets.
- [ ] Every `SocketHost` in production is built by `SocketHostFor`; no hard-coded role/frame remains.
- [ ] Rulings 1, 2, 3 each have a test that fails if the rule is broken; ruling 3's includes the R11
      derivation (a ceiling of 4 makes any role, the helm included, a word host with no code change).
- [ ] A base row above its role ceiling cannot be bored past it at runtime.
- [ ] `verify-change.py` over the changed paths is green.

## Open questions

None. Every choice here is technical and resolved by the single-responsibility rule.
