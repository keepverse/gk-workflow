# Spec: `combo-bind`

**Module id:** `combo-bind` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 4 of 8 · **Depends on:** `host-gate` (1), `recipe-import` (3) · **Findings closed:**
F1, F3 (by deletion, R12), and the binding half of F7 · **Ruling:** R12 of
[spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md) — *"No count cap; price it instead …
`maxCombosPerActor` is retired."*

## Objective

**A Strain that fires today does nothing in a fight.** The equip projection binds the host and each
socketed insert (`gk-core/src/FusionRpg.Core/Items/EquipProjector.cs:98` – `:111`); it never binds the
combination. The lane and the module spec both say it must
([ssot-sockets.md](../item/ssot-sockets.md) line 83, [spec-sockets.md](../item/spec-sockets.md) line 45:
*"the item's atoms, every insert's atoms and every satisfied combination's atoms bind together; unequip
and all of them withdraw together"*), and `tasks/item-todo.md` line 5384 marks module 16 built without
it. The per-actor backstop that was supposed to govern these bindings has no production caller
(`SocketCombinationCap.Apply`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:237` — **deleted by R12/SSH4.1; the line is gone**) — and under R12
it never gets one: **every firing combination binds**, and this module deletes the cap (§2).

This is the program's central wiring gap. It is an RPG-layer path end to end — evaluator → container →
binding → ActorHub → battle engine — and needs nothing from PvZ.

**User outcome:** a player who fills a chaff breastplate's four sockets with a Strain's ingredients sees
the Strain's mechanism on their sheet, in battle, in the delve and on the lawn, attributed to that item
and circuit, and loses it the moment the host is unequipped or a gem is removed.

## Design

### 1. The combination's container, built from content already shipped

A combination entry carries `grants` — atom **family** ids, a closed enum the generator writes
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:107`) — and the evaluator produces a
`GrantedTier` (`gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs:91`). A combination container is
therefore a pure function of `(comboId, grants, tier)`, exactly the build-at-use-time shape gems already
use (`gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:43`: family × tier → `AtomRow.DeriveId`).

Add (new) `gk-core/src/FusionRpg.Core/Items/Sockets/ComboContainerBuild.cs`:

```text
TryBuild(comboId, grants, tier, lookupAtom) -> ContainerRow? (kind = Combo, pool rolls 0, fixed atoms)
    id      = "{comboId}-t{tier}"            one segment after `combo.`, legal under ContainerValidator.cs:35
    atoms   = [ AtomRow.DeriveId(family, "", tier) for family in grants ]
    refuses = by name, when any derived atom id is absent from the real atom catalog
```

At boot, for every accepted Strain/Splice recipe and every tier the ladder can grant, the server builds
and upserts these containers into `effect_container` — **content rows, not mutations** (ssot-sockets
§4.8's own table: *"effect_instance (insert / combination) — yes, new rows for new things"*). Grants are
therefore stored as ordinary container atoms; **no new table and no new column** are needed.

**One acceptance set (strengthen pass 2026-09-18).** A recipe the grid validator accepts but whose
container build is refused (a grant family with no atom row) would otherwise be seeded by `recipe-import`,
evaluate as *firing*, preview as *firing* — and bind nothing: a word that visibly fires and does nothing.
So the container build runs **before** `recipe-import`'s seed, and the accepted set becomes
*grid-valid ∩ buildable at every reachable tier*. A container refusal is printed by name beside the grid
refusals, and the recipe is left out of the seed and disabled by the same `DisableCombinationsNotIn`
(`recipe-import` §3). One acceptance set, read by the evaluator, the preview and the binder alike.

**The tier bound (F7, resolved).** `GrantedTier` is documented as unbounded above
(`gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:139`), but atoms materialise only for tiers
`1..FamilyExpansion.TierCount` (`gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs:28`,
structural). The bound is the atom ladder's, so it is enforced where tuning is loaded:
`StrainSpliceTuning.Parse` **throws** if `max(baseTier) + attunedTierBonus` exceeds `TierCount`
(module 7 extends the same check to the ladder's top rung). A throw at load, never a clamp at bind — a
clamp would make *"your better gems stopped mattering"* a silent bug. Magnitude growth is untouched: it
rides the atom ladder's `contentScale`, one power ladder, no private curve.

### 2. Binding through the one projection

`EquipProjector`'s own comment is the rule: *"The insert's binding MUST come out of this projection, not
a parallel Bind() call beside it"* (`EquipProjector.cs:98`), because `ApplyEquipProjection` withdraws
every binding absent from the desired set. Combinations obey the same rule.

- `EquipProjector` gains one optional delegate (new) `combosOf(EquipAssignment, IReadOnlyList<SocketSlot>)
  → IReadOnlyList<ComboBindTarget>`, where `ComboBindTarget = (CombinationResult Result, int Circuit,
  string ComboInstanceId)`. The projector stays pure; the caller supplies the evaluator call.
- For each projectable host the projector adds one `EquipAssignment(specimen, host role,
  EquipRefKinds.Rolled, ComboInstanceId, assignedUtc)` per target, after the insert bindings.
- **Every target binds. There is no per-actor count (R12).** The only "at most one" is structural and
  lives where it already lives: one Strain/Splice identity per circuit, picked inside the evaluator
  (`gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs:80`, made per-circuit by `circuit-topology`).
  No `ProjectionResult.Suppressed` list, no suppression reason, no UI "suppressed" state.

**The cap code is deleted, not wired — decided here.** The two options R12 leaves are *remove the cap's
caller* or *delete the cap*. There is no production caller to remove (map F3: `git grep` finds only
`gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationEvaluatorTests.cs:404` and `:429`), so the choice is between
deleting the class and keeping it idle. Keeping it idle fails SOLID: its single responsibility is a rule
the owner retired (S); an idle backstop beside the projection is exactly the second path a later change
would "just re-enable" instead of pricing (O); and `SocketTuning.MaxCombosPerActor` would keep a parser
requirement alive for a number that no longer exists (I). Deleted in this module, in one change:

| Removed | Where |
|---|---|
| `SocketCombinationCap` (class, `ActorCombination`, `Apply`, `Suppressed`, its doc comment) | `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:217` – `:260` — **deleted by SSH4.1/R12; the class is gone and those lines no longer resolve** |
| `SocketTuning.MaxCombosPerActor`, its constructor parameter and the required-key read `Positive(root, "maxCombosPerActor")` | `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs:93`, `:102`, `:124`, `:256` |
| the two cap tests | `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationEvaluatorTests.cs:404`, `:429` — **deleted by SSH4.1/R12; those lines no longer resolve** |
| the "non-binding" assertions | `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketGeometryTests.cs:362` (whole test), `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:181` – `:184` (the cap lines only) — **deleted by SSH4.1/R12; those lines no longer resolve** |
| Python: `ComboTuning.max_combos_per_actor` and its required read; the run-summary key | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:48`, `:104`; `gk-forge/tools/seedsmith/seedsmith/report/cli.py:1262` — **deleted by SSH4.2/R12; the symbol is gone and those lines no longer resolve** |
| Python backstop test | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py:245` — **deleted by SSH4.2/R12; the line no longer resolves** |
| prose that still describes the backstop (reworded, not deleted — the modules stay) | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:3` – `:4` (module docstring), `:61` – `:67` (`geometric_combo_ceiling` docstring; the function itself is `combo-budget`'s), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/__init__.py:29` — **reworded by SSH4.2/R12** |

**This module is the only one that deletes the cap** (strengthen pass 2026-09-18: the map's seedsmith
table briefly gave the Python half to `combo-budget` as well — one owner, and it must be this one,
because `circuit-topology` (module 5) points the combogen reader at `sockets.v2.json`, which has no
`maxCombosPerActor`; a `_require(..., "maxCombosPerActor")` still alive at module 5 raises at load and
stops every generator run). Tests that pin the **two-role host set** are not this module's: they break
on `circuit-topology`'s ceilings and are rewritten there (`circuit-topology` §5).

After this module the parsers ignore the key, which `sockets.v1.json:25` still carries as history (v1 is
never edited); `circuit-topology` publishes `sockets.v2.json` without it. `SOCKETS_OWNED_KEYS`
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:32`) and its C# mirror
(`gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:226`) **keep** `maxCombosPerActor`: the
strain-splice file must still never define it, now because it is retired rather than because sockets owns it.
`combo-budget` adds the source scan that keeps the identifier from returning.

**Map §6 C4 is moot.** It asked for one total suppression order; with nothing suppressed there is no
order to define. Binding order within a projection is irrelevant to the result because every binding id
is content-derived (below).

`ComboInstanceId` is deterministic: `cmb:{hostInstanceId}#c{circuit}:{containerId}` (new). The caller
ensures the instance exists with `Instantiator.TryInstantiate` on the combo container before
`ApplyEquipProjection` writes bindings — pool rolls are zero, so instantiation consumes no RNG and a
re-projection of the same state writes nothing new. A combination that stops firing leaves its instance row behind with no binding; the id is
reused if the same fill returns, and an unbound instance contributes nothing (bindings, not instances,
reach the actor).

### 2.1 Every trigger that changes the binding set (DESIGN-GATE §2.16)

The binding set is refreshed on discrete events, not polled, so every trigger is listed and tested.
Verified this pass: the projection runs today only on equip (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:478`)
and at squad build (`gk-core/src/FusionRpg.Server/WebMatchService.cs:576`), both through
`RpgStore.MaterializeRolledEquipRuntime` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:913`) — **never on a
socket write**. A word completed on an already-equipped host would therefore stay unbound until the next
equip or deploy. The read side is self-correcting for *removals* (`EquippedBoundAtoms` recognises only
bindings that match a current target, so a stale binding contributes nothing) but not for *additions* —
the key-set edge: a combination that starts firing.

| Trigger | What moves | Refresh |
|---|---|---|
| equip / unequip the host | the host enters/leaves the projection | existing — equip endpoint |
| squad build / deploy | full rebuild | existing — `WebMatchService` |
| **socket-insert on an equipped host** (key-set edge: a combination starts firing) | a new target | **new:** the workbench socket write calls `MaterializeRolledEquipRuntime` for the wearing specimen in the same request, after the socket row commits |
| socket-remove on an equipped host | a target disappears | same new call (withdraws the binding eagerly rather than leaving it unrecognised) |
| socket-imbue on an equipped host | attunement → granted tier → container id `-t{tier}` → a **different** target | same new call |
| boot: recipe disabled / enabled (`recipe-import` §3) | targets appear or vanish | next projection; read side ignores a binding with no current target |
| tuning revision (ladder, `attunedTierBonus`) | granted tier → target id | next projection; same read-side rule |

**Order-independent:** *fill then equip* and *equip then fill* must reach the same binding set; both
orders are tested.

### 3. ActorHub — contribute, never fold

| DESIGN-GATE question | Answer |
|---|---|
| Layer | the equipment layer (an item's socket content), not a new layer |
| Scope | per specimen (the actor wearing the host) |
| Lifetime | live — re-derived from socket rows at every projection; nothing about the combination is persisted except the fill (ssot-sockets §3) |
| Carrier | an atom effect container bound at deploy — one of the two sanctioned carriers |
| Naming | a new `ContributionSourceIds` arm, (new) `ContributionSourceIds.Combo(role, hostItemRefId, comboId, circuit)` → `combo:{role}:{hostItemRef}:{comboId}#c{circuit}`, beside `Insert` (`gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs:37`), with a display arm beside `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs:118` |

**The grammar is the one [actor-hub-ssot.md](../actor-hub-ssot.md) §8.1 already reserved, plus a circuit
suffix (strengthen pass 2026-09-18).** §8.1 (amended 2026-09-16 for species-gear-chain T21) reserves
`combo:{role}:{hostItemRef}:{comboId}` for exactly this arm (*"reserved, not minted … no code may mint
`combo:` before then"*). The first draft of this spec minted `combo:{role}:{host}#c{circuit}` instead — a
second grammar for the same producer. The reserved form is kept; it gains `#c{circuit}` because the
reservation predates the eight-socket topology: an eight-socket host can carry the **same** comboId in
circuit 0 and circuit 1, and the reserved form would collapse two contributions into one id (the same
reason `Insert` carries `#{socketIndex}`). The §8.1 amendment is therefore one suffix on an
already-reviewed row, made in the same change as the code (Boundaries).

**One owner for combination binding.** species-gear-chain's `socket-combat-wiring` names *"arm 2
(combination grants)"* as its own follow-on ([spec-socket-combat-wiring.md](../species-gear-chain/spec-socket-combat-wiring.md)
§5, plan decision #6). This module **is** that arm: same projection, same carrier, the reserved grammar.
species-gear-chain ships arm 1 (inserts) only; nothing there builds arm 2 (map §6 C15).

`EquippedBoundAtoms.InputsFromStore` (`gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs:18`) already re-reads
each host's socket rows at resolve time to recognise inserts (`:54`). It re-evaluates the same host's
combinations with the same evaluator and recognises a binding whose `InstanceId` equals a target's
`ComboInstanceId`; `EquippedAtomInput` (`gk-core/src/FusionRpg.Core/Battle/EquipAtomSource.cs:26`) gains an
optional `Circuit`, and `EquipAtomSource` mints `Combo(...)` for it beside the `Insert` arm
(`EquipAtomSource.cs:145`). Everything downstream — Hub compose, AppliedCombat, battle, delve, siege,
lawn — is unchanged: combination atoms enter through the registered equip atom reader like any other
equip atom. **No private fold, no second composer**; `gk-core/scripts/guard-actor-hub.py` must stay green.

**Battle engine.** A Strain grants a mechanism (proc, rider, spawn) through ordinary atom kinds; the
battle engine resolves it. No mode owns a combination mechanism.

### 4. Resonances — named, not built

The same path binds a resonance once resonance recipes carry grants. Today they carry none
(`ResonanceGenerator` emits recipe rows only, `gk-core/src/FusionRpg.Core/Items/Sockets/ResonanceGenerator.cs:44`).
That content is item module 16's; this module's path accepts it without change (open for extension).

## Seedsmith / generator

**No generator change.** `grants` is already a closed family enum and `combination-regen` closes it
against the atom catalog.

| Item | Detail |
|---|---|
| Adapter / stage | none changed; consumes `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:107` (`grants`) |
| New seed fields | none |
| Magnitudes | atom tier ladder from `gk-data/packs/fusion/data/seed/items/affix-families/**` via `FamilyExpansion`; `attunedTierBonus` from `gk-core/data/tuning/sockets.v1.json`; `baseTier` from `gk-core/data/tuning/strain-splice.v1.json` |
| Check | none new |
| Pytest | none new; the R12 deletion removes `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py:245` and the `max_combos_per_actor` field (§2 table) |

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~EquipProjectionSockets|FullyQualifiedName~ContributionSourceIds|FullyQualifiedName~EquipAtomSourceId"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EquipProjectionSockets|FullyQualifiedName~EquipRuntimeStore"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemEquipEndpoints"
python gk-core/scripts/guard-actor-hub.py
python gk-fusion/scripts/guard-single-writer.py
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

A live check follows the live-probe standard: socket a real chassis through the real
`/api/items/workbench/*` endpoints, equip it through `/api/items/equip`, and read the contribution back
through the real sheet — RPG Server scope, never a fabricated binding.

## Project structure

```text
gk-core/src/FusionRpg.Core/Items/Sockets/ComboContainerBuild.cs        (new)  (comboId, grants, tier) -> ContainerRow
gk-core/src/FusionRpg.Core/Items/EquipProjector.cs                            combosOf delegate; every target binds
gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs                  SocketCombinationCap DELETED (R12)
gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs                      MaxCombosPerActor + its required read DELETED (R12)
gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py           max_combos_per_actor DELETED (R12)
gk-forge/tools/seedsmith/seedsmith/report/cli.py                               maxCombosPerActor summary key DELETED (R12)
gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs                load-time tier bound (throws)
gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs             Combo(role, host, circuit) + display arm
gk-core/src/FusionRpg.Core/Battle/EquipAtomSource.cs                          Circuit on EquippedAtomInput; Combo mint
gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs                            recognise combo bindings per host
gk-core/src/FusionRpg.Server/Program.cs                                       build + upsert combo containers at boot, before recipe-import's seed; refusals shrink the accepted set
gk-core/src/FusionRpg.Server/ItemWorkbench.cs                                 socket insert/remove/imbue on an equipped host re-runs the one projection (§2.1)
gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs   (new)
gk-core/tests/FusionRpg.Core.Items.Tests/Items/EquipProjectionSocketsTests.cs       extended
```

## Code style

```csharp
/// <summary>
/// A combination's contribution: actor-hub-ssot §8.1's reserved combo:{role}:{host}:{comboId}, plus
/// the circuit, because an eight-socket host can carry two combinations (even the same one twice), and a sheet that collapsed them would lie about where the number came
/// from — the same reason Insert carries the socket index.
/// </summary>
public static string Combo(string role, string hostItemRefId, string comboId, int circuit) =>
    $"combo:{NullToUnknown(role)}:{NullToUnknown(hostItemRefId)}:{NullToUnknown(comboId)}#c{circuit}";
```

Tiers, circuits and counts are `int`: a tier is bounded by `FamilyExpansion.TierCount`, a circuit index
by `structuralCeiling / circuitSize`. None is a magnitude.

## Testing strategy

| Test | Asserts |
|---|---|
| `a_firing_strain_binds_its_container_through_the_projection` | projector output contains the combo binding; no binding is written outside `Project` |
| `unequipping_the_host_withdraws_the_combination` | one assignment deleted → combo binding absent on next projection |
| `removing_one_ingredient_withdraws_the_combination` | re-evaluation is a withdraw-and-rebind |
| `the_combination_contributes_under_its_own_source_id` | sheet contribution id is `combo:{role}:{host}:{comboId}#c0` — the §8.1 reserved form plus the circuit — distinct from `equip:` and `insert:`; `FictionLabel` parses it |
| `the_same_word_in_two_circuits_is_two_contributions` | an eight-socket fixture host with one comboId in circuits 0 and 1 → two distinct SourceIds |
| `every_firing_combination_binds_with_no_actor_wide_count` | a loadout with more firing combinations than the retired cap's 3 binds all of them; nothing is suppressed, every insert stays socketed |
| `one_identity_per_circuit_is_the_only_limit` | two Strains satisfiable in one circuit → one binds (evaluator's pick); the same two in two circuits → both bind |
| `binding_set_is_independent_of_loadout_iteration_order` | both orders of the same loadout → same binding ids |
| `socket_tuning_parses_without_max_combos_per_actor` | a fixture revision with the key absent loads; the v1 file (key present) still loads — the key is ignored, not required |
| `a_granted_tier_above_the_atom_ladder_throws_at_load` | tuning whose `baseTier + bonus` exceeds `TierCount` fails `Parse` |
| `a_grant_family_without_an_atom_is_refused_by_name` | `ComboContainerBuild` refusal, never a substitute atom |
| `reprojecting_unchanged_state_writes_no_new_instance` | deterministic instance id, zero RNG |
| `completing_a_word_on_an_equipped_host_binds_it_without_a_re_equip` | §2.1 key-set edge: socket-insert on an equipped host → binding present on the next sheet read |
| `fill_then_equip_and_equip_then_fill_reach_the_same_bindings` | §2.1, order-independent, both orders |
| `imbuing_an_equipped_host_rebinds_at_the_attuned_tier` | §2.1: the old `-t{tier}` binding withdrawn, the new one bound |
| `a_recipe_whose_container_cannot_build_is_neither_seeded_nor_previewed` | §1 one acceptance set: refused by name, disabled, absent from `GetComboRecipes` |
| `the_host_fingerprint_is_unchanged_by_binding` | ruling 1, again, at the binding layer |

## Boundaries

**Always:** bind through `EquipProjector.Project` only; contribute through the equip atom reader;
refuse by name.

**Ask first:** the `#c{circuit}` suffix on §8.1's reserved `combo:` row — amended in
[actor-hub-ssot.md](../actor-hub-ssot.md) §8.1 in the same change as the code; any change to
`effect_binding` (none is needed).

**Never:** a second `Bind()` beside the projection; a private fold of combination numbers; clamp a
granted tier; count, cap or suppress active combinations per actor in any form (R12 — scarcity is
priced, `combo-budget` / `socket-pricing`); keep `SocketCombinationCap` "disabled"; copy the stale
`BattleStatComposer` reference in `EquippedBoundAtoms.cs:12`; mint a `combo:` id in any shape other than
§8.1's reserved form plus the circuit.

## Success criteria

- [ ] A firing Strain/Splice binds, contributes under `combo:{role}:{hostItemRef}:{comboId}#c{circuit}`
      and withdraws with its host or an ingredient — including when the word is completed, broken or
      imbued on a host that is already equipped (§2.1, both orders).
- [ ] A recipe whose container cannot be built is refused by name and never seeded (§1).
- [ ] Every firing combination binds; `SocketCombinationCap`, `SocketTuning.MaxCombosPerActor` and the
      Python `max_combos_per_actor` are deleted with their tests (R12).
- [ ] A granted tier the atom ladder cannot express fails tuning load.
- [ ] `guard-actor-hub.py` and `guard-single-writer.py` are green.
- [ ] A live probe through the real endpoints shows the contribution on the real sheet.

## Open questions

None. The former cap-value question (map §7, former O2) was answered by R12: no count cap; this module
deletes the cap and `combo-budget` measures the pricing that replaces it.
