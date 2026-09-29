# Mega-merge QC 1 — combat-ai (cai3) on the merged head

**QC date:** 2026-09-24 · **Head:** `11fe6306b` (features/mega-merge) · **Method:** solo, no agents.
Focused suites + Tier-ci guards + RPG-engine evidence. No live game.

## Verdict: GREEN with two routed findings (neither owned here)

| Check | Command | Result |
|---|---|---|
| Combat split projects | `dotnet test gk-core/tests/FusionRpg.Core.CombatCounterTests.Tests` etc. (4 projects) | 4 + 9 + 5 + 5 = 23/23 |
| Lawn tests | `dotnet test gk-core/tests/FusionRpg.Core.Lawn.Tests` | 15/15 |
| Core battle filter | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~Battle` | 1401/1401 (2 m 33 s) |
| Engine proof | `dotnet run --project gk-core/tools/CombatSim -- run -s baseline -n 200` | clean resolve, 200 trials,Reflection 0.00% (no errors) |
| Guard suite | `dotnet test gk-core/tests/FusionRpg.Guard.Tests` | 672 passed / **1 failed** (11 m) → routed, see F1 |
| CorpusDump verify | `dotnet run --project gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` | exit 0, self-consistent (was exit 1 at CAI-find-8 filing — resolved since) |
| ItemSeedValidator | `dotnet run --project gk-forge/tools/ItemSeedValidator` | exit 1, 498 errors — UNCHANGED since filing, routed, see F2 |

## Routed findings (not this program's — recorded for the owning queues)

- **F1 — `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` red, deterministic** (isolated re-run 1/1 red). Last touched by species-progression SP6.8 (`3a898f8f6`). Route to species-progression.
  **FIXED in QC fix cycle 2 (2026-09-24):** root cause was NOT species-progression — the vocabulary
  legitimately grew to ten via the reviewed T8 fusion rank floor (`picks.source-below-rank-floor`,
  merged `e2ede8ae6`). Re-blessed per the test's own comment (a tenth code from a reviewed change
  gets re-read): test renamed to ten, code added in sorted order with the reason stated. Proof:
  `closed_vocabulary` filter 3/3 green. No product change.
- **F2 — ItemSeedValidator still exit 1 / 498 errors**, byte-identical count to the 2026-09-23 filing. Route to items/seedsmith program.
  **INVESTIGATED in QC fix cycle 3 (2026-09-24):** full error census — 2134 MetaRegistryVersionBehind
  (warnings), **498 SameStageReference (all 498 errors: `successorOf` stage references)**,
  338 ImplicitFlavourDrift, 65 PartitionMetaMismatch, 48 TagAxisNotApplicable, 3 TierGap,
  1 MetaSourceRefMissing (warnings). Corpus AND validator both untouched since 2026-09-23, so this
  is stable pre-existing drift, not merge damage. The 498 need generator-side repair in the items
  program (hand-editing generated entries is forbidden) — routed with this breakdown, not fixed here.
  **FIXED in QC fix cycle 7 (2026-09-24), checked to QC 1 F2:** root cause was the *validator*, not
  the corpus. `successorOf` is the upgrade tree's authored peer edge — a base type's successor is
  **by design** a same-stage (1b) peer (owner ruling 2026-09-21,
  `spec-item-upgrade-tree.md` §1), authored as a reviewed table after the corpus exists, with its own
  closure gate in the generator (`basetypegen/successor_edges.py::violations_in_corpus`). The 498
  generated rows are correct; `ReferenceCheck` applied the same-stage ban to a field that is defined
  as a peer edge. Applied the ready exemption (`tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch`):
  `ResolveReference(..., allowSameStage: key == "successorOf")`, resolution unchanged. Documented in
  `seed-contract.md` §7.1. Proof: `dotnet run --project gk-forge/tools/ItemSeedValidator` → **PASS, 3962
  entries / 1013 files, 0 errors** (was 498), exit 0; `FusionRpg.ItemSeedValidator.Tests` **100/100**
  (98 + 2 new: a legal same-stage successor edge, and a typo still `ReferenceUnresolved`).
- **F0 (closed, recorded):** CAI-find-8's CreatureCorpusDump hash-mismatch is green at this head — some stream fixed the manifest/payload drift. No action.

## Open rows noted, not QC failures

combat-ai-todo carries ~26 open rows (CAI2.2–CAI5.3, cites, finds). Those are program work, not merge-interaction defects — out of QC scope by design. The merges under QC (6 × `merge(cmdc/cai3)`) introduce no red above.
