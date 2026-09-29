# Spec: `exchange-role`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `exchange-role` · **Map row:** 5 ·
**Wave:** 1 · **Decision:** D-E1 (confirmed by the owner 2026-09-19)
**Depends on:** `structure-bands`, `world-budgets` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

One reviewed widening of the closed structure role list: `Exchange`, the role of a building that
**clears trades between parties**. D-E1 chose a new role over reusing `Enable`, so `Enable` keeps its one
meaning (*"gates what may be built here"*). This module adds the **vocabulary only**. The trade hub's
behaviour (clearing capacity, prices) belongs to `trade-network` `exchange`.

**Done means:** `Exchange` is a member of the one role registry that Python and C# both read. It has a
description with a negative clause, a published budget target, and at least one legal slot kind that is
declared ahead of content. The documents that enumerate ten roles say eleven.

## 2. Scope and non-goals

**In scope.**
- The registry row.
- The planner's declared legal pairs.
- The budget row.
- The role-coverage test's contract.
- The C# registry test.
- The role-count annotations in the listed documents.

**Not in scope.**
- Any row. The first `Exchange` row is `trade-structure-rows`.
- The `StructureKind` member itself. ~~There is no trade mechanism yet. An `Exchange` row loads only when
  `trade-network` `exchange` adds the kind its `StructureDef` needs; until then such a row carries
  `structureKind: none`~~ — **superseded by round 6 C2:** an `Exchange`-**role** row is a feature building and
  carries the one neutral `structureKind: Feature`, which loads (`structure-bands` §5.4a). There is no
  per-building kind: `StructureKind.Exchange` is withdrawn, and `exchange`'s trade behaviour is reached
  through `featureUnlock` / `sector-features`, never through a kind. The `Feature` member lands in
  `trade-foundation` `sector-features`; this module still emits no row.
- Prices and clearing (`trade-network` `exchange`).

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The closed list of ten | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41` (moves to the role registry in `band-reader` §5.3) |
| Built | The zero-row test | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:182-189` (`test_no_role_has_zero_rows`) |
| Built | The decision row | `docs/architecture/decisions.md` — '`exchange` structure role (2026-09-19)' (working tree, 2026-09-19): *"The closed structure role list widens from ten to eleven with `exchange` … `wonder/` is a seed folder, not a role"* |
| Wiring gap | Legal `(role, slot kind)` pairs are derived only from existing rows, so a role with no row has no legal slot, and nothing can be planned into it | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:74-75`, `:88`, `:154-160` |
| Wiring gap | C# validates no role today. `band-reader` adds the registry check this module widens | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:119` |
| Real gap | The `Exchange` value itself | — |

**Documents that enumerate the roles** (grep this session):
- `docs/architecture/structure-seed-ideal.md` §4 (the role table)
- `docs/architecture/base-defense/spec-structure-schema.md`
- `docs/architecture/base-defense-ideal.md` §5.21
- `docs/architecture/trade-network-ideal.md:161`, which says *"11 roles"* and counts `wonder` as a role.
  That is wrong today and becomes true for a different reason: ten roles plus `exchange` (map §11 item 1).

## 4. Principles as they bind this module

- **A closed vocabulary's count is its contract** (`validation-ssot.md` §1). Eleven roles is pinned,
  and the reason is stated: a twelfth role is a reviewed change.
- **`none` is a value; a description carries a negative clause** (ai-native README §3).
- **Cheap axis** (seedsmith-design ①③). `role` is the structure corpus's cheap axis
  (`empire-seed-ideal.md` §6.1): it feeds legality and budget, and no stat keys off it. Widening it is
  the low-dependency widening.
- **The planner runs first** (base-defense decision 33). A role becomes plannable when the plan declares
  its legal slots, not when a model happens to produce a row.
- **No model.** Zero calls.

## 5. Design

### 5.1 The registry row

`data/seed/structures/_registry/roles.v2.json` equals `v1` plus one row. v1 stays on disk, the append-only
precedent (`docs/architecture/seedsmith-map.md` §3b note on themes v2):

```json
{ "id": "Exchange",
  "description": "Clears trades between parties: goods offered here meet goods wanted here. NOT storage (that is Store), NOT a road or depot (that is Move), NOT a charter that gates what may be built (that is Enable), NOT a price — prices belong to the exchange mechanism, never to this row.",
  "legalSlotKinds": ["Market", "Wildland"] }
```

`Market` is a shipped `SlotKind` (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:18`). Today it hosts only
`district-charter`, which is `Enable` (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:451-458`).
Its name matches the role's meaning. **Round 4 (2026-09-19) adds `Wildland`:** the one trade building, the
Trading Post chain, is buildable wherever the first clan trade needs it
([decisions-round-4.md](../trade-network/decisions-round-4.md) §B, Q1), and `Wildland` is the slot every sector
type allows. Which of the two the `trading-post` row requires was owner question ES-R4-1; it is **closed by round 5 B1**
(2026-09-20, [decisions-round-4.md](../trade-network/decisions-round-4.md) §R5-A): *"Wildland or Market — a
structure row may allow more than one slot kind; a Market slot gives a bonus"*, so the row carries
`requiredSlotKinds: [Wildland, Market]` (`spec-trade-structure-rows.md` §5.1, §5.4 item 3). Declaring both
legal here is what makes that a content change, not a registry change. Further slot kinds are added by the same kind of reviewed registry row.

**The same registry version carries one wording change** (round 4): `Enable`'s description widens from
*"gates what may be built here"* to *"gates what may be built or agreed here"*, so the Embassy chain
(`spec-trade-structure-rows.md` §5.3) has an honest role without a twelfth member. Its member list and
negative clause are unchanged.

### 5.2 Declared legal pairs

`legalRoleSlotPairs` = pairs derived from rows ∪ pairs declared in the role registry (`legalSlotKinds`).
Declared pairs make `check_plan`'s "declared and empty" branch meaningful for the first time
(`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:154-160`). A declared pair with zero rows is
reported in the plan as `targetNewRows` work. It is not a failure. The rows-derived pairs of the ten
existing roles are unchanged.

### 5.3 The budget row

The next `structure-seed` version adds `budget.Exchange` through
`gk-core/tools/tuning/publish.py --add-key "budget:Exchange=1"`. It is a floor of one trade hub, and with
`roleCountTolerance` 1 (`gk-core/data/tuning/structure-seed.v1.json:22`), zero rows still passes `check_plan`
until the first row ships. `world-budgets`' `validate_budget` then requires the key.

### 5.4 The zero-row test changes contract

`test_no_role_has_zero_rows` asserts a holey taxonomy. With a role that has legitimately not been filled
yet, that assertion would be red on purpose. That is forbidden, because a failing test is never the plan.
The test becomes:

> Every role has at least one row, **or** the committed plan names it in `targetNewRows` work.

It is a contract that holds before and after `trade-structure-rows`.

### 5.5 C#

`band-reader`'s role vocabulary is built from the registry, so `Exchange` is accepted with no C# code
edit. A C# test pins the eleven members.

### 5.6 Documents

Each document in §3 gets a one-line dated annotation: *"2026-09-19: eleven roles, `Exchange` added (D-E1,
`docs/architecture/decisions.md`)."* History is annotated, never rewritten. The base-defense documents are
edited under D-E2 (empire-seed owns the structure corpus), and their shipped history stays as written
(map §8).

## 6. Commands

```powershell
python gk-core/tools/tuning/publish.py structure-seed --add-key "budget:Exchange=1" --label "exchange-role: D-E1"
python -m seedsmith.adapters.structures.planner
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_anchor_contract.py -q
.\scripts\verify-change.ps1 -Paths <changed C# test> -Session <build-session-id>
python scripts/audit-doc-citations.py --scope <each annotated document>
```

## 7. Acceptance (contract level)

1. The role registry has exactly eleven members: the ten existing plus `Exchange`. Python `ROLE` and the
   C# vocabulary are equal. **Pinned as a closed vocabulary**, because a twelfth role is a reviewed
   change.
2. Every role has a description containing a negative clause (the existing mechanical test, extended to
   the registry), a budget target, and at least one legal slot kind.
3. A C# corpus row with `role` outside the registry is a load rejection naming the value.
4. `("Exchange", "Market")` and `("Exchange", "Wildland")` are in the regenerated plan's
   `legalRoleSlotPairs`. The adapter's legality function returns `True` for them and `False` for
   `("Exchange", "Rootbed")`.
5. The rewritten role-coverage test (§5.4) passes with zero `Exchange` rows, and it would fail if
   `Exchange` were dropped from the plan's work.
6. `python scripts/audit-doc-citations.py` reports no HIGH finding for each annotated document.

## 8. Test plan and verification boundary

| Test | Where | Criterion |
|---|---|---|
| `test_role_registry_is_the_eleven` | pytest | 1 |
| `StructureRoleRegistryTests.Eleven_roles` | Core.Tests | 1 |
| `test_every_role_description_has_a_negative_clause`, `test_every_role_has_budget_and_slot` | pytest | 2 |
| `StructureCorpusParseTests.Unknown_role_is_rejected` (from `band-reader`) | Core.Tests | 3 |
| `test_declared_pairs_are_legal_before_rows_exist` | pytest | 4 |
| `test_every_role_is_filled_or_planned` | pytest | 5 |

**Verification boundary.** The C# test runs through `verify-change.ps1` (`core-tests-fallback`). **Gap:**
`gk-forge/tools/seedsmith/**`, `data/seed/structures/_registry/**` and `data/tuning/structure-seed.*` are unmapped
(`scripts/verify-change.ps1:118`). The owner of the fix is `test-verification-boundary` `python-test-lane`.
The pytest command in §6 is the boundary for those paths.

## 9. Hard edges

- **Closed-vocabulary widening.** It is reviewed, and it lands in one commit: registry v2, budget
  publish, plan regeneration, and both language tests.
- **Four documents owned historically by `base-defense` and `trade-network`.** They get an annotation,
  not a rewrite.

## 10. Dependencies

- Upstream: `structure-bands` (removes `ROLE_TO_STRUCTURE_KIND`, which would otherwise need an `Exchange`
  entry, and puts the C# registry on the load path), `world-budgets` (`validate_budget`), and
  `band-reader` (the registry), transitively.
- Downstream: `world-exemplars` (an `Exchange` exemplar), `trade-structure-rows` (the first row).
- Cross-map: `trade-network` `exchange` gives the role its behaviour; no `StructureKind` follows from the
  role (round 6 C2 — the neutral `Feature` kind is the only one a feature building carries).

## 11. Open questions

None.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: structure role vocabulary (Python and C#), planner legality, structure-seed tuning, four docs.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares the doc paths it annotates.
[x] Read this session: validation-ssot, ai-native README §3, structure-seed-ideal §4, empire-seed-ideal §6.1 and §9.
[x] decisions.md: the D-E1 row is present (working tree), and this spec implements it.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: planner legality derivation, test_no_role_has_zero_rows, SlotKind has Market.
[x] Read the surrounding sections of the rules quoted.
[x] Tested: none claimed beyond reading. The tolerance arithmetic (0 >= 1 - 1) is stated from check_plan's code.
[x] No §2 invariant contradicted.
[x] Correction propagated: "11 roles incl. wonder" corrected in trade-network-ideal via annotation (§5.6).
[x] The one pin is the closed role vocabulary, with its reason.
[x] No event-refreshed cache.
[x] No ordering assumption.
[x] No actor magnitude.
[x] SOLID: one registry read by both languages; no second role list.
[ ] New rule registry row: none.
```
