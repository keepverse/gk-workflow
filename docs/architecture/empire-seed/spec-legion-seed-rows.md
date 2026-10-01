# Spec: `legion-seed-rows`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `legion-seed-rows` · **Map row:** 15 ·
**Wave:** 4 (last)
**Depends on:** `legion-bands`, `world-namer` · **Cross-map (hard):** `legion-build` mechanics shipped
(the layer-5c binder and reader, `OwnerKind.Legion`, stack `Count`, the stack-scoped equipment layer)
**Model calls:** **yes**, through `world-namer` only
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build and no model run
authorized until this spec is approved, `legion-build`'s mechanics have shipped, and the first batch size
is agreed.

---

## 1. Objective

Generate the legion catalog **planner-first**:
- standards and doctrines over the element × world-trade-off grid
- traditions over the trigger-fact list
- equipment over the legion slot × `tierBand` grid, with element as a second axis only where a piece is
  attuned

The planner fills cells against the published legion budget and draws every enum. `world-namer` writes
identity text only. The catalog waits for its mechanics: *"a catalog for a mechanic that does not exist is
content nobody reads"* (`empire-seed-ideal.md` §2).

**Done means:**
- Every planned cell is filled by an accepted seed or recorded `unresolved`.
- Every seed passes the legion contract and the closed-loop legion metrics.
- Per-cell coverage sits inside the published band.
- A rerun makes zero calls.

## 2. Scope and non-goals

**In scope.**
- The legion planner. It uses the same shape as `call-budget-dry-run`'s structures planner, over the
  legion grids.
- The legion `NamingFamily` for `world-namer`.
- The legion accepted store and its one writer.
- The legion metric set.

**Not in scope.**
- Any number (`legion-bands`).
- Any vocabulary (`legion-build`, mirrored in `legion-seed-contract`).
- Any mechanic.
- A second namer or a second planner shape.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built (after upstream modules) | The contract, the exemplars, the ladder, the namer, the planner shape | `spec-legion-seed-contract.md`; `spec-legion-bands.md`; `spec-world-namer.md`; `spec-call-budget-dry-run.md` |
| Built | The closed element list (6) and the four trade-off kinds make a 24-cell standard/doctrine grid | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:46`; `docs/architecture/legion-build-map.md` §5.13 |
| Not built (cross-map) | `OwnerKind` has no `Legion` | `gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20-29` |
| Not built (cross-map) | `world-buff` is declared and never bound | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:38`, `:203` |
| Real gap | Every legion seed | — |

## 4. The generation rules, as they bind this module

- **The planner runs first.** Each planned entry carries its kind, its cell (for example
  `elementAffinity × worldTradeoffKind`) and every other VALIDATED field, drawn deterministically:
  - `atomFamilies` from the namespace (§5.1)
  - `forgeGoods` and `recipeGoods` from `MaterialCatalog.All`
  - `carrierRequirement` from the registry
  - (`producedBy` was removed by round 4 §B: the Workshop chain produces every piece, `spec-legion-seed-contract.md` §5.1)
- **The model writes identity only**: `name`, `flavor`, and for traditions `rankNames[]`, whose length
  the planner fixes from the seed's own plan (a count is structure, `item/seed-contract.md` §2.1) and never
  from `legion.v1.json` — a threshold publish must not invalidate generated seeds (audit 2026-09-20; ranks
  past the list reuse its last name, never a cap). **Ids are the writer's, never the model's:** every
  seed's `id` (and `pieceId`) is minted once per `planKey` and frozen, because saved worlds persist them
  (`world-namer` §5.4). Every text passes `world-namer`'s
  validators: no digit, a unique name across corpora, script, and length.
- **Permutation and voting.** The model is offered no enum, so the vote set is empty (stated with its
  reason in the plan). If a later spec lets a model choose an atom family from a short list, that field
  is permuted seeded from `(entity_id, field, sample_index)`, voted three times, and a 1-1-1 result
  resolves `unresolved`, using the existing helpers
  (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`,
  `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26`, `:67`).
- **Constrained decoding** is proven by `world-namer`'s proof call before the run.
- **Grid density** (seedsmith-design ①). 24 cells for standards and 24 for doctrines. At the band's
  target of 1–2 per cell (`empire-seed-ideal.md` §6.4), 24–48 seeds per kind is inside the clean band.
  The planner reads the published per-cell min and max and never a literal.
- **No second roll, no sets.** Equipment seeds are fixed pieces. The planner never draws a set, socket
  or roll field, and the contract rejects one anyway.

## 5. Design

### 5.1 The legion planner

`tools/seedsmith/seedsmith/adapters/legion/planner.py` reuses the structures planner's shape and writes a
committed `data/seed/legion/_plan.json`:
- per-cell counts from disk
- deficits against `legion-seed.v1.json` `budget`
- `plannedEntries` with a stable `planKey = "{kind}:{cellKey}:{ordinal}"`
- the call budget (`call-budget-dry-run` §5.2's formula)
- `voteFields: []` with its reason

Atom-family draws for a cell come from the namespace, filtered by the kind's legal families
(`vocab.v1.json` `legionAtomFamilies` if `legion-build` publishes a subset). They are least-used first,
with ties broken by family id, so a family is not over-drawn across cells. That guard exists against the
distribution-skew failure (the Hammerdin shape, `docs/research/game-design/05-failure-modes.md`).

### 5.2 Naming and writing

A legion `NamingFamily` (schema bounds from `legion-seed` tuning, prompt builder, accepted store at
`data/seed/legion/_generation/accepted.v1.json`) plugs into `world-namer` unchanged. A legion writer,
`adapters/legion/generate_corpus.py`, is **the only writer of `data/seed/legion/<kind>/`**. It emits
accepted entries, and `_exemplars/` stays hand-authored and outside its output.

### 5.3 Metrics (closed unless marked)

| Metric | Target |
|---|---|
| schema conformance per kind | 100% |
| every VALIDATED value joins its registry | 100% |
| every `tierBand` resolves (`legion-bands` catalog builds) | 100% |
| per-cell coverage | tuning `budget` per-cell min/max |
| atom-family spread: no family above the published share of draws | tuning |
| name unique across corpora | zero collisions |
| idempotency | rerun hash equality |
| unresolved rate | ≤ tuning ceiling |
| flavour distinctness, n-gram overlap | **open**, review queue |

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith legion plan --dry-run --out $env:TEMP\legion-dry-run
python -m seedsmith legion name --prove-only
python -m seedsmith legion name --limit <owner-approved>
python -m seedsmith.adapters.legion.generate_corpus
python -m seedsmith.adapters.legion.metrics
python -m pytest tools/seedsmith/tests/test_legion_planner.py tools/seedsmith/tests/test_legion_rows.py -q
.\scripts\verify-change.ps1 -Paths <C# catalog tests touched> -Session <build-session-id>
```

## 7. Acceptance (contract level)

1. Every planned entry ends as an accepted seed in the tree or `unresolved` in the ledger, never both and
   never neither.
2. Every seed passes the legion contract (`spec-legion-seed-contract.md` §7) and every closed-loop metric
   of §5.3.
3. Per-cell counts sit inside the published band, read from tuning. No cell exceeds the published
   maximum.
4. `LegionEquipmentCatalog` builds from the tree (`legion-bands`), and every piece stays under the share
   bound.
5. A rerun makes zero calls, and the tree is byte-identical.
6. The planner's output is byte-identical across two builds, and shuffling input file order changes
   nothing.
7. No test pins a seed count, and none asserts a generated string.

## 8. Test plan and verification boundary

`test_legion_planner.py` covers criteria 3 and 6. `test_legion_rows.py` covers 1, 2, 5 and 7 with a
scripted stub transport. Core.Tests catalog builds over the committed tree cover 4.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` and `data/seed/legion/**` are unmapped
(`gk-core/scripts/verify-change.py:771`). The owner of the fix is `test-verification-boundary` `python-test-lane`.
The pytest command is the boundary.

## 9. Hard edges

- **It is gated on another program's shipped code.** It does not start until `legion-build`'s layer-5c
  reader and stack-scoped equipment exist, because a catalog nobody reads is dead content.
- **Tokens are spent.** The first batch is small and reviewed. Run `seedsmith-preflight` first.
- **`legion-build`'s tests run on exemplars, not generated seeds.** Replacing an exemplar-based fixture
  with generated content is `legion-build`'s choice, never this module's.

## 10. Dependencies

- Upstream: `legion-bands`, `world-namer`, `legion-seed-contract`, `world-name-index`,
  `call-budget-dry-run` (the planner shape and prompt builder).
- Cross-map (hard): `legion-build` mechanics shipped.

## 11. Open questions

- **First batch size.** The owner confirms it before tokens are spent. Recommendation: one seed per kind
  (four entries) for the first reviewed batch.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: a new legion planner, naming family and writer; the legion metric set.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: empire-seed-ideal §6.4/§7, legion-build-ideal §6-§8, legion-build-map §5.11-§5.14,
    ai-native README, seedsmith-design ①④⑥.
[x] decisions.md: the legion 5c and legion equipment scope rows (working tree) are legion-build's; respected.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: OwnerKind has no Legion; world-buff unbound.
[x] Read surrounding sections.
[x] Tested: none claimed.
[x] No §2 invariant contradicted.
[x] Correction propagated: none new here.
[x] No population pin; the grid size (24) is computed from two closed vocabularies and used only as a reading.
[x] No cache; order-independent planning (criterion 6).
[x] Actor magnitude: none; contributions are legion-build's through ActorHub.
[x] SOLID: reuses the one namer and the one planner shape.
[ ] New rule registry row: none.
```
