# Spec: `circuit-topology`

**Module id:** `circuit-topology` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 5 of 8 · **Depends on:** `host-gate` (1), `combination-regen` (2) · **Rulings:** 5 step 2
(*"eight-socket tuning revision"*), 3 (*"helm moves only if re-confirmed then"*) **as revised by R11**
(*"Helm goes to 4 sockets in `sockets.v2`"*), R12 (*"`maxCombosPerActor` is retired"*) — both in
[spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md) · **Decision applied:**
[decisions.md](../decisions.md) row *Eight-socket topology (2026-09-10)* (line 139 at this writing — cite
by name; three other docs cite stale line numbers, map §6 C1).

## Objective

Apply the decided, unapplied eight-socket topology as a **new tuning revision**, without editing
`sockets.v1.json`, without an eight-ingredient recipe, and without a rewrite of any generated row by
hand. The decision row states the whole contract: role ceilings 0–8 in versioned tuning; sockets
partitioned into consecutive four-socket circuits (`floor(socketIndex / 4)`); resonance and at most one
four-ingredient Strain/Splice evaluated **per circuit**; the model authors no count, index, circuit,
position or tier; the per-actor budget re-measured before implementation (that is module 6 — under R12
a measurement of combination power against price, since the count cap is retired).

What ships today is the halved topology: `structuralCeiling: 4` (`gk-core/data/tuning/sockets.v1.json:23`)
mirrored by `SocketLimits.SocketMaxCeiling = 4` (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs:41`),
role ceilings half of the re-issued table (`gk-core/data/tuning/sockets.v1.json:5` vs
[spec-sockets.md](../item/spec-sockets.md) §3), and an evaluator that scores the whole fill as one
multiset with one identity (`gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs:75`). The
migration task is recorded, unrun, at `tasks/item-todo.md` line 9946.

**This is not a geometry prerequisite for Strains** — today's corpus already clears four on the two
host roles (ideal, re-count 2026-09-18). It is ruling 5's second step: it widens *where* a combination
can live and doubles *how many* one host can carry, which is why combination pricing is measured after it.

**User outcome:** a breastplate or main weapon can carry two independent four-gem words; a mantle, a
shield or a **helm** can carry one (R11); the socket bench shows each circuit as its own readable decision.

## Design

### 1. The revision — `gk-core/data/tuning/sockets.v2.json` (new), published, never hand-written

Published with `python gk-core/tools/tuning/publish.py sockets ...` (`set` for existing keys, `--remove-key` for
the retired cap). `v1` stays on disk untouched.

| Key | v1 | v2 | Source |
|---|---|---|---|
| `structuralCeiling` | 4 | **8** | decision row |
| `socketCeiling.armament-primary` / `core-guard` | 4 / 4 | **8 / 8** | spec-sockets §3 |
| `ward-array`, `armament-secondary`, `mantle` | 3 | **6** | same |
| `head-guard` | 3 | **4** — one complete circuit, so the helm becomes a word host | **R11** (revises ruling 3's value; the doubled table's 6 is not used) |
| `manipulator`, `girdle`, `footing`, `infusion`, `retinue` | 2 | **4** | same |
| `jewel-major`, `sense`, `jewel-minor-a`, `jewel-minor-b` | 1 | **2** | same |
| `rarityGrant` (ten rungs, two per band) | `0/0 · 0/1 · 1/2 · 1/3 · 2/4` | **`0/0 · 0/2 · 2/4 · 2/6 · 4/8`** | [ssot-sockets.md](../item/ssot-sockets.md) §4.1 band table |
| `strainSplice.ingredientCount` | 4 | 4 | D20 as amended — unchanged |
| `maxCombosPerActor`, `maxCombosPerActorNote` | 3, note | **removed** (`--remove-key`); no reader remains after `combo-bind` | **R12** — no count cap; `combo-budget` publishes `comboPricing` in v3 instead |

**Why the helm row is 4, not the table's 6.** R11 sets it; the mechanism that makes 4 sufficient is
verified in code: every gem word is exactly `ingredientCount` 4 gems (`gk-core/data/tuning/sockets.v1.json:67`),
and the combination generator closes `hostRole` to the roles whose ceiling reaches that count
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:75`; the list is `host_roles()`,
`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60`; C# twin
`SocketGeometry.RolesThatCanHostAStrain`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs:101`). At 4
the helm holds exactly one complete circuit and no remainder; nothing in code names the helm.

**`publish.py` gains `--remove-key container.path:leaf`** (new). The tool has `--add-key` and
`--rename-key` but no removal (`gk-core/tools/tuning/publish.py:430` `main`), and tunables-ssot T4 says extend the
tool rather than hand-edit. Same refusal discipline as its siblings: refuses when the key is absent.

`rarityGrant` rows only affect **future** drops: `item_socket` is the SSOT for an existing item's
sockets (D2 §6; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs:22`), so no dropped item is re-socketed.

### 2. Two structural constants, both commented, both mirrored

- `SocketLimits.SocketMaxCeiling` 4 → **8** (`SocketTuning.cs:41`) — the capacity legibility limit; the
  parser keeps refusing a tuning value that disagrees with it (`SocketTuning.cs:204`).
- (new) `SocketLimits.SocketCircuitSize = 4` — the recipe-width legibility limit. **Not tunable**:
  changing it changes whether a recipe is readable, not how the game feels.

Parser rules added to `SocketTuning.Parse` (all throw, none clamp):
`strainSplice.ingredientCount == SocketCircuitSize` (a Strain consumes exactly one complete circuit);
every resonance threshold `<= SocketCircuitSize` (resonance is evaluated per circuit — today's check is
against the structural ceiling, `SocketTuning.cs:240`, which would admit an unmatchable threshold of 5
once the ceiling is 8).

### 3. Circuits in the one evaluator

`CombinationEvaluator.Evaluate` groups the fill by `circuit = socketIndex / SocketCircuitSize` and runs
its existing ordered pass **per circuit**: at most one Strain/Splice (identity), then Pure, Ring,
Eclipse, Diversity. `CombinationResult` gains `int Circuit`. A Strain/Splice fits a circuit only when
that circuit's opened sockets reach `MinSockets` (through `ComboMatcher.Fits`, module 1) — so a
six-socket mantle has one complete circuit (0–3) and a two-socket remainder (4–5) that can carry
resonance only.

**Unordered within a circuit** — D41 stands (spec-sockets.md line 347; `CombinationEvaluator.cs:23`).
spec-sockets.md line 163's *"ordered four-ingredient"* is superseded by D41 (map §6 C3).

No cross-circuit resonance, no cross-circuit recipe, no eight-ingredient match. `CombinationDistance`
inherits all of this for free because, after module 1, it calls the same matcher.

### 4. Every reader moves in one change

Today the revision is named by literal filename in many places — among them
`gk-core/src/FusionRpg.Server/Program.cs:316`, `gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs:52`,
`gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py:32`,
`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:22`, and a dozen test files that load
"the real shipped" socket tuning. A literal per reader is how one reader stays on `v1`.

- C#: one constant (new) `SocketTuningFiles.Current` in Core (a filename, not a file read) used by the
  server, the validator and every test that means *the shipped tuning*. Tests that mean *v1 as
  history* keep `v1` explicitly and say so. The same class later carries one constant per domain this
  program revises — `tier-ladder` adds `strain-splice`, `socket-pricing` adds `materials` if it publishes
  — rather than three look-alike classes.
- **Precondition:** the combogen reader may point at v2 only after `combo-bind` has deleted
  `_require(..., "maxCombosPerActor")` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:118`);
  v2 has no such key, and the loader refuses a missing key rather than defaulting.
- Python: one constant (new) in `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` imported by
  `basetypegen/tuning.py`.
- A guard test scans for any other `sockets.v{n}.json` literal.

### 5. Base-type capacity follows by generator verb (ask-first corpus write)

`socketMax` is decided in exactly one place: `resolve_socket_max(role, band, seq_index)`
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py:258`) over `socketMaxSplit`, which is
per-mille **of the ceiling** (`gk-core/data/tuning/base-types-gen.v1.json`) — so doubling the ceiling doubles
the resolved range with no split change. Existing rows are re-stamped by a new deterministic verb
(new) `basetypegen/resocket.py`, modelled on `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/reslate.py`: for every base-type row, recompute
`socketMax` from its own `(role, band, seq)` under the current revision, change **only** that field,
keep id, name, class, band and flavour, and record a run-ledger amendment. No model call.

Consequence named so it is not a surprise: after the re-stamp, the set of roles that can host a Strain
widens by derivation (`SocketGeometry.RolesThatCanHostAStrain`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs:101`;
Python mirror `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60`) from two roles to every role whose ceiling reaches four —
**including `head-guard` at 4 (R11)**. The helm's ceiling moves 3 → 4 rather than doubling, so its
re-stamped `socketMax` range is `socketMaxSplit` per-mille of 4; that is still the one resolver, no helm
case. Shipped combinations keep their coarse pins (ruling 2); newly generated ones may pin the wider set —
that re-run is `combination-regen`'s R11 step, which follows this module.

**Tests that pin today's host set or today's maximum `socketMax` are rewritten to the contract, never
bumped.** Re-inventoried in the strengthen pass (2026-09-18) — the first draft named two lines of one
file; there are seven assertions in two files, and the resocket breaks the corpus ones as surely as v2
breaks the tuning ones:

| Site | Pins | Breaks on |
|---|---|---|
| `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:161` – `:163` | max `socketMax` over the corpus == `ingredientCount`, and == it on `armament-primary` / `core-guard` | resocket (those roles reach 8) |
| `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:169` | corpus host set == `armament-primary` + `core-guard` | resocket |
| `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:178`, `:182` | tuning host set == those two; count 2 | v2 |
| `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py:203` | Python `HOST_ROLES` == those two | v2 |
| `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py:238`, `:241` | corpus max == `ingredient_count`; corpus host set == those two | resocket |

(`StrainSpliceGridTests.cs:183` – `:184` and `test_strain_splice_gen.py:245` are the cap's, deleted by
`combo-bind`.) **Landed by SSH5.1 (2026-09-20) — the line citations in the table above are the
pre-rewrite pins; both files now carry the three role-free contracts and those lines no longer
resolve.** Rewritten as three contracts, none naming a role: the tuning host set equals
`{ role | ceiling(role) >= ingredientCount }`; the **corpus** host set equals the tuning host set (the
Python test's own last line, `:243`, already says this — it becomes the whole test); and no corpus row
exceeds its role's ceiling. C# and Python agree on all three.

## Seedsmith / generator

| Item | Detail |
|---|---|
| Adapter / stage | `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py:32` and `:145` (read the current revision); `basetypegen/resocket.py` (new verb, precedent `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/reslate.py:1`); `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:22` (current revision; `host_roles()` at `:54` widens by derivation) |
| New seed fields | **none.** `socketMax` is the one field that moves, and it was already resolved by code, never by the model |
| Magnitudes | `gk-core/data/tuning/sockets.v2.json` (new) — ceilings (`head-guard` 4, R11), rarity windows, no `maxCombosPerActor` (R12); `gk-core/data/tuning/base-types-gen.v1.json` `socketMaxSplit` — unchanged |
| Tool | `gk-core/tools/tuning/publish.py` — `--remove-key` (new) |
| Regenerate | `python -m seedsmith.adapters.items.basetypegen.resocket --dry-run` (new) → review → `--write` (**ask-first**: production corpus rewrite, item-todo line 9946) |
| Check | `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` · `dotnet run --project gk-forge/tools/ItemSeedValidator` (`SocketMaxExceedsRoleCeiling` against v2) |
| Pytest | `gk-forge/tools/seedsmith/tests/test_base_types_gen.py` (resocket determinism, identity preservation), `gk-forge/tools/seedsmith/tests/test_combogen.py` (`host_roles` mirrors C#) |

## Commands

```powershell
python tools\tuning\publish.py sockets structuralCeiling=8 socketCeiling.armament-primary=8 socketCeiling.core-guard=8 socketCeiling.head-guard=4 ... --remove-key ":maxCombosPerActor" --remove-key ":maxCombosPerActorNote" --label "eight-socket topology; helm 4 (R11); combo cap retired (R12)"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~SocketAllowance|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~BaseTypeCorpus"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore|FullyQualifiedName~ItemCardStore"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~GemTier|FullyQualifiedName~ItemWorkbenchEndpoints|FullyQualifiedName~ItemPreviewEndpoints"
cd tools\seedsmith; python -m pytest tests/test_base_types_gen.py tests/test_combogen.py -q
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

This change crosses Core, Data, Server, a tool and seedsmith — one of the three points where the full
suite is the right call (AGENTS.md verification boundary, point 2): `deploy-play.py --full-suite` once,
at the end.

## Project structure

```text
gk-core/data/tuning/sockets.v2.json                               (new, published)
gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs                 SocketMaxCeiling 8, SocketCircuitSize 4, two parser rules
gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs     (new)  the one current-revision name
gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs         per-circuit pass; Circuit on the result
gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs                  CombinationResult.Circuit
gk-core/src/FusionRpg.Server/Program.cs                                  reads the current revision
gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs                 reads the current revision
gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/resocket.py (new)
gk-core/tools/tuning/publish.py                                          --remove-key (new)
gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs        host-set + max-socketMax assertions rewritten to the derivation
gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py                  the same, Python side
gk-data/packs/fusion/data/seed/items/base-types/**                                    RE-STAMPED by the verb (ask-first)
```

## Code style

```csharp
/// <summary>
/// STRUCTURAL, not tunable: the width of one recipe. A four-insert decision is readable; an
/// eight-insert one is a wiki page. Capacity (SocketMaxCeiling) may grow; this does not.
/// </summary>
public const int SocketCircuitSize = 4;

static int CircuitOf(int socketIndex) => socketIndex / SocketLimits.SocketCircuitSize;
```

Counts and indices are `int` — bounded by the structural ceiling of 8.

## Testing strategy

| Test | Asserts |
|---|---|
| `sockets_zero_to_eight_are_capacity_for_every_role_ceiling` | parser accepts 0–8, throws at 9, never clamps |
| `indices_three_and_four_never_combine` | a Strain whose four ingredients straddle the boundary does not fire |
| `an_eight_socket_host_fires_two_independent_combinations` | two circuits, two identities, each with its own `Circuit` |
| `a_six_socket_host_has_one_complete_circuit_and_a_resonance_only_remainder` | mantle shape |
| `a_recipe_is_unordered_within_a_circuit` | D41, per circuit |
| `ingredient_count_must_equal_the_circuit_size` | parser throws otherwise |
| `a_resonance_threshold_above_the_circuit_size_throws` | the tightened check |
| `head_guard_ceiling_is_read_from_tuning_only` | ruling 3 — no branch; the v2 row decides |
| `a_four_socket_helm_has_one_complete_circuit_and_no_remainder` | R11 shape, fixture tuning: a head-guard host at 4 fires one Strain in circuit 0 |
| `the_host_set_is_every_role_whose_ceiling_reaches_the_ingredient_count` | replaces the pins at `StrainSpliceGridTests.cs:178`/`:182` and `test_strain_splice_gen.py:203`; computed from the loaded tuning, C#/Python parity — no role named |
| `the_corpus_host_set_equals_the_tuning_host_set` | replaces the corpus pins at `StrainSpliceGridTests.cs:161` – `:169` and `test_strain_splice_gen.py:238`/`:241`; after the re-stamp every tuning host role has at least one base reaching `ingredientCount` |
| `the_current_socket_revision_carries_no_combination_cap` | R12: `maxCombosPerActor` absent from the file `SocketTuningFiles.Current` names |
| `publish_remove_key_refuses_an_absent_key` | tool extension |
| `no_reader_names_a_sockets_revision_literal` | guard over `src/`, `tools/`, `tests/` except the named history tests |
| `resocket_is_deterministic_and_changes_only_socket_max` | seedsmith |
| `no_base_type_exceeds_its_role_ceiling_after_resocket` | ItemSeedValidator against the real re-stamped corpus |
| `existing_items_keep_their_socket_rows` | `item_socket` unchanged by the revision |

## Boundaries

**Always:** publish tuning with the tool; keep `v1`; move every reader together; re-stamp the corpus
with the verb.

**Ask first:** running `resocket --write` over `gk-data/packs/fusion/data/seed/items/base-types/**` (production corpus
rewrite). **Sequencing consequence:** `combination-regen`'s R11 re-run waits for this write. The generator
offers every role whose *tuning* ceiling reaches 4, so a re-run under v2 before the re-stamp would author
helm-hosted words while no helm base type yet holds four sockets — words no item can fire. If the owner
declines the re-stamp, the R11 re-run does not run either.

**Never:** an eight-ingredient recipe; a cross-circuit match; a helm branch (the helm reaches host status
only through its tuning row, R11); carry `maxCombosPerActor` into v2 or any later revision (R12);
hand-edit a base-type row; edit `sockets.v1.json`; clamp an out-of-range ceiling.

## Success criteria

- [ ] `sockets.v2.json` is published and is the only revision any reader loads as current.
- [ ] The evaluator evaluates per four-socket circuit; indices 3 and 4 never combine.
- [ ] The two structural constants exist, are commented, and are mirrored by throwing parser rules.
- [ ] The base-type corpus is re-stamped by the verb, changes only `socketMax`, and validates.
- [ ] `head-guard` is 4 in v2 (R11), reached only through tuning, and appears in the derived host set of
      both ports.
- [ ] `sockets.v2.json` carries no `maxCombosPerActor` (R12), removed by the tool.

## Open questions

None. The helm question (map §7, former O1) was answered by R11: `head-guard` 4 in `sockets.v2.json`.
