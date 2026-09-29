# Tasks: `species-rank` (creature-seed)

**Plan:** `tasks/creature-seed-plan.md` · **Spec:** `docs/architecture/creature-seed/spec-species-rank.md`. One complete path per task, not horizontal layers. Checkpoints review done work; no pre-work gates (nothing irreversible — see plan).

## Phase 1: Foundation (parallelizable once vocab ids fixed)

- [x] Task 1: Rank tuning table + loader validation — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t1.md` (15/15 focused tests,
  verify-change exit 0). `creature-rank.v1.json` authored at v1 (publish.py refuses to create a domain).
  - Acceptance: `creature-rank.v1.json` holds 10 ids + 100 cells diagonal-default; loader rejects unknown id naming table + cell; unresolved inputs never reach the table.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CreatureRankTuning"`; tuning JSON validates.
  - Files: `gk-core/data/tuning/creature-rank.v1.json`, `gk-core/src/FusionRpg.Core/Creatures/CreatureRankTuning.cs`, focused test.
  - Dependencies: None. Scope: M.

- [x] Task 2: Rank enum + ladder helpers + guard test — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t2.md` (Core ~CreatureRank 29/29,
  CreatureRankLadderGuardTests 19/19). The whole `gk-core/tests/FusionRpg.Guard.Tests` project is red on 2
  boundary-integrity cases caused by CS-R1 (the missing registry row), not by any Task 2 file.
  - Acceptance: 10-value `CreatureRank` closed enum; `AtLeast`/`AtMost`/`RungsBelow`/`OneRungAbove`/`All` agree with rarity ladder row-for-row; new guard test forbids bare `(int)rank` outside the ladder (beside existing rarity guard).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CreatureRank"`; `dotnet test gk-core/tests/FusionRpg.Guard.Tests`.
  - Files: `gk-core/src/FusionRpg.Core/Creatures/CreatureRank.cs`, `CreatureRankLadder.cs`, `gk-core/tests/FusionRpg.Guard.Tests/CreatureRankLadderGuardTests.cs`.
  - Dependencies: None (needs vocab ids from Task 1). Scope: M.

## Checkpoint: Foundation
- [x] Tuning validates; ladder + guard green; zero behavior change (nothing reads rank yet).
  **CLOSED 2026-09-23 (lane `cs-rank`), after the manager's CS-R1 registry row landed at the integration
  tip.** Tuning validates: `creature-rank.v1.json` parses with 10 ids / 100 diagonal-default cells / 5
  floors (`~CreatureRankTuning` 15/15). Ladder + guard green: `~CreatureRank` 29/29,
  `CreatureRankLadderGuardTests` 19/19, `LadderRestatementGuardTests` 13/13, and the two Guard tests CS-R1
  had made red are now 1/1 each (`Integrity_guard_passes_on_the_current_registry` 1 m 11 s;
  `P6_the_real_registry_resolves_seedsmith_and_tuning` 1 m 48 s). Zero behavior change: nothing in `src/`
  read rank at this point (Tasks 5-12 wire the readers), and `CreatureSpeciesGen --check` was clean
  throughout. Evidence: `tasks/reports/creature-seed-rank-t1.md` … `-t5.md`.

## Phase 2: Seed side

- [x] Task 3: Seedsmith derive + runner wiring — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t3.md` (`-k "anchor or rank"`
  186 passed / 1 skipped; the two anchor-related batches 170 + 154 passed). `emit.py` needed no edit, as
  the spec says. The committed anchor tree is deliberately untouched — that is Task 4's regen.
  - Acceptance: rank joins `DERIVED_FIELDS` + schema property + `descriptions.py` entry (no KeyError); `derive_rank` handles voted, fallback-stamped, and unresolved inputs; wired at `_finalize`, `fix_unresolved` recompute, and scoped-rerun merge; `audit_schema` clean.
  - Verify: `python -m pytest tests/ -q -k "anchor or rank"` in `gk-forge/tools/seedsmith`; scoped-rerun staleness test green.
  - Files: `anchor/schema.py`, `anchor/descriptions.py`, `anchor/derive.py`, `run/runner.py`, seedsmith tests.
  - Dependencies: Task 1 (table shape). Scope: M (5 files, one pipeline).

- [x] Task 4: Anchor regen, byte-identical rerun — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t4.md` (904/904 anchors carry
  the table's rank; rerun byte-identical, tree sha256 unchanged; `CreatureSpeciesGen --check` clean).
  **Premise corrected in the same commit:** no deterministic corpus-wide re-emit pass existed (each of the
  three existing passes skips what it does not change), so the deliverable grew a small module-9 pass —
  `python -m seedsmith creatures run refresh-rank` — plus one defect fix it exposed
  (`_write_species_entry` dropped `_provenance.relead`, 104/904 entries; `run/runner.py:312`).
  - Acceptance: every resolved anchor carries the table's rank; unresolved → absent (never defaulted); rerun over unchanged anchors byte-identical; `--check` green post-regen.
  - Verify: regen diff reviewed. (Rank-coverage line is Task 9, not Task 8 — corrected; see GAP-1.)
  - Files: `gk-data/packs/fusion/data/seed/creatures/species/**` (regen only — anchor tree). **Not** `gk-data/packs/fusion/data/generated/creatures/**`: concrete rows cannot carry `rank` until `SpeciesExpander` (Task 5) computes it and the `ConcreteSpecies` triad (Task 6) can serialize it — that regen belongs to Task 6's own verify line. See GAP-2.
  - Dependencies: Task 3. Scope: M.

## Checkpoint: Seed side
- [x] Anchors carry rank deterministically; rerun identical; review regen diff before proceeding.
  **CLOSED 2026-09-23 (lane `cs-rank`)**, in Task 4's own commit: 904 of 904 anchors carry the table's
  rank for their committed pair; a second `creatures run refresh-rank` reports 0 changes and leaves the
  tree's sha256 unchanged (`cd1ffeb4…`); and the 549-file diff was reviewed file-by-file — the only
  per-entry differences are the added `rank`, the widened `_derived` list and `_provenance.emittedUtc`,
  with 0 unexpected differences. Evidence: `tasks/reports/creature-seed-rank-t4.md`.

## Phase 3: Runtime flow

- [x] Task 5: AnchorRow + expansion — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t5.md` (`~SpeciesExpand`
  25/25, anchor-adjacent set 103/103, `CreatureSpeciesGen --check` still clean). Two readings recorded
  there for the manager to overrule: rank is RESOLVED from the anchor's own DERIVED field (not re-derived
  from the grid in C# — one derivation site), and rank-skipped is reported as a null `ConcreteSpecies.Rank`
  rather than by widening the batch-skip `UnresolvedFields` (the spec's Never list forbids blocking
  generation on rank).
  - Acceptance: nullable `rank` on `AnchorRow` (`Rarity` nullability untouched); `SpeciesExpander` computes rank post-expansion with theta path byte-identical; unresolved reporting covers rank-skipped.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesExpand"`.
  - Files: `Generation/AnchorRow.cs`, `Generation/SpeciesExpander.cs`, focused tests.
  - Dependencies: Task 4. Scope: S.

- [x] Task 6: Concrete triad + SeedReader — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t6.md`. `Canonical` gained the
  `rank` key (written only when the species has one), the SeedReader reads it optionally (absent -> null),
  `gk-data/packs/fusion/data/generated/creatures/**` regenerated in the SAME commit (904 files, each with exactly one added
  `rank`, 904/904 equal to its anchor's own), `--check` clean, and `SpeciesSnapshot.cs`'s stale
  "every host calls ConfigureFromCompiledDefault" comment corrected (GAP-3; the live hosts are
  `Server/Program.cs:618` store-backed and `Injector/Host/RpgHost.cs:145` committed-tree). The
  Mapper/`CreatureSpeciesDef` leg stays Task 7's, whose own acceptance names it.
  - Acceptance: record field + `Canonical` dict + optional-read for rank; Injector committed-tree path carries rank; `gk-data/packs/fusion/data/generated/creatures/**` regenerated here (moved from Task 4, see GAP-2) — `--check` green; fix stale comment `SpeciesSnapshot.cs:78-91` (claims every host calls `ConfigureFromCompiledDefault`; verified false — `Server/Program.cs:370` calls `Configure` with the store-backed snapshot) — doc hazard named in spec §4, bundle here per GAP-3.
  - Verify: Core tests green; regen output carries rank through all three; regen diff reviewed.
  - Files: `ConcreteSpecies.cs`, `ConcreteSpeciesSerializer.cs`, `ConcreteSpeciesSeedReader.cs`, `SpeciesSnapshot.cs` (comment only), `gk-data/packs/fusion/data/generated/creatures/**` (regen), focused tests.
  - Dependencies: Task 5. Scope: M.

- [x] Task 7: Persist + catalog + Mapper — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t7.md`. Nullable `rank`
  column (no default), null-safe read-back, `SameContent` compares it (rank-only change rewrites, same
  rank does not), `CreatureSpeciesDef.Rank` + the Mapper funnel, `Validate` refuses nothing (a closed
  enum already parsed at every boundary, and null is legal). Sharded Data + Core group via verify-change:
  exit 0, 4 shards / 1732 tests / no overlap, 15 647 tests passed, 0 failed.
  - Acceptance: nullable column via `EnsureColumn`; null-safe read-back; `SameContent` compares rank (reimport idempotent); `CreatureSpeciesDef` + `Validate` carry rank; Mapper funnel passes it; old DBs read null without crash.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Catalog"`; `guard-dal.ps1` clean.
  - Files: `RpgStore.Species.cs`, `CreatureSpeciesCatalog.cs`, `ConcreteSpeciesMapper.cs`, focused tests.
  - Dependencies: Task 6. Scope: M.

## Checkpoint: Flow
- [x] Rank queryable at runtime on Server (store-backed) and Injector (committed-tree) paths; suites green.
  **CLOSED 2026-09-23 (lane `cs-rank`), after Tasks 6 and 7.** Committed-tree path: `ConcreteSpecies`
  gained the field (T5), `Canonical` writes it and `ConcreteSpeciesSeedReader` optional-reads it (T6),
  proven over the real 904-file tree by a reconciliation test against the anchor tree. Store-backed path:
  `RpgStore.Species.cs` persists it in a nullable column with a null-safe read-back and `SameContent`
  comparing it, `CreatureSpeciesDef` carries it and `ConcreteSpeciesMapper` funnels it (T7). Suites:
  `gk-core/tests/FusionRpg.Core.Tests` 9509-9587/0 across the two tasks and the sharded Data project via
  `verify-change` exit 0 (4 shards, 1732 tests, no overlap). The GATES that read rank are Tasks 8-12, not
  part of this checkpoint. Evidence: `-t5.md`, `-t6.md`, `-t7.md`.

## Phase 4: Landing gates

- [x] Task 8: Fusion floors + preview parity — **IN-FENCE HALF LANDED 2026-09-23, ROW LEFT OPEN ON TWO
  DENIED-PATH BLOCKERS.** Evidence `tasks/reports/creature-seed-rank-t8.md`. Landed: the Core floor policy
  `CreatureRankFloors` (all five gates, null→bottom in one place, a missing gate refused at `Configure`),
  the rank floor beside the rarity floor at `EligibleOutputs`, and the two enforcing fusion gates in
  `RpgStore.Fusion.cs` (promotion `promotion.rank-floor`, inherit picks `picks.source-below-rank-floor`) with
  tests raising a floor above bottom, plus "no recompute on promotion" asserted. Full Core project 9516/0.
  **BLOCKER 1 (preview parity):** `gk-core/src/FusionRpg.Server/FusionEndpoints.cs` is outside this lane's fence —
  `verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/FusionEndpoints.cs -Session creature-seed-rank -PlanOnly`
  answers `path is outside session scope`. The two preview sites must call the same
  `CreatureRankFloors.Passes(<gate>, CreatureSpeciesCatalog.Get(speciesId)?.Rank)`; needs a row or a fence
  grant. **BLOCKER 2 (the floors' boot wiring):** `gk-core/src/FusionRpg.Server/**` and `gk-fusion/src/FusionRpg.Injector/**`
  are both outside the fence, and no host reads `creature-rank.v1.json` yet — so a floor tuned above bottom
  has no production effect until one host calls `CreatureRankFloors.Configure(CreatureRankTuningLoader.Parse(…))`
  at boot. Tasks 10-12 (the other three gates) are unaffected by both blockers.
  - Acceptance: rank floor beside `CanPromote`, recipe eligibility, inherit picks (enforcing sites); preview mirrors each exactly (parity tests); null→bottom at each gate; no recompute on promotion (stated + tested).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Fusion"`; behavior identical to pre-rank.
   - Files: `RpgStore.Fusion.cs`, `FusionEndpoints.cs`, `CreatureRecipeCatalog.cs`, focused tests.
   - Dependencies: Task 7. Scope: M.
   - **CLOSED 2026-09-23 by lane `cs-rank-b`** (evidence `tasks/reports/creature-seed-rank-t8.md` close-out):
     preview parity — promotion site refuses `promotion.rank-floor` and recipe pickable-atoms loop skips
     below-floor sources via the SAME `Passes` calls as the enforcing gates; recipe preview + browser carry
     `resultRank`/`resultRankDisplayName`; boot — Server `Program.cs` calls
     `CreatureRankFloors.Configure(Parse(creature-rank.v1.json))` once (Server, not Injector: every
     enforcing gate runs there). Orchestrator must still run the row's Verify line (no shell here).

- [x] Task 9: Display payloads + quality line — **IN-FENCE CLAUSE LANDED 2026-09-23, ROW LEFT OPEN ON
  THREE DENIED PATHS.** Evidence `tasks/reports/creature-seed-rank-t9.md`. Landed:
  `ConcreteAnchor.Rank` + the corpus join carries it (read off the expanded species, never re-parsed, never
  defaulted), reconciled against the anchor tree over the real 700+-row corpus with 0 mismatches, plus the
  skipped-rank → null and ranked → enum cases. **GAP-5 answered:** the quality report's diversity section is
  generic only in SHAPE (an explicit call list, not reflection), so an explicit `ReportDiversity("rank", …)`
  dimension IS needed — measured `grep -c rank gk-forge/tools/CreatureQualityReport/Program.cs` = 0.
  **BLOCKER 1:** the catalog projection and the roster/codex/summon/preview payloads need
  `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs` AND `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs` (`CreatureProfileDto`
  lives there) — both answer `path is outside session scope` to verify-change; `RpgStore.Creatures.cs` is in
  fence but cannot add a field the DTO does not declare. **BLOCKER 2:** the quality-report coverage line and
  the rank diversity dimension need `gk-forge/tools/CreatureQualityReport/**`, also outside the fence (proven).
  **BLOCKER 3:** rank display names (spec §5: copy lives in the runtime catalog file) travel with blocker 1.
  - Acceptance: catalog projection, roster/codex/preview/summon payloads carry rank id + display name (copy from catalog file); `ConcreteAnchor` join carries rank (filter + throw unchanged); quality report rank-coverage line, reports-only; confirm whether `CreatureQualityReport`'s existing diversity section (`gk-forge/tools/CreatureQualityReport/Program.cs:160-209`) needs an explicit rank dimension added or already reads the new tuning vocab generically — state which, don't skip silently (spec §7 ambiguity, see GAP-5).
  - Verify: endpoint payload checks; `dotnet run --project gk-forge/tools/CreatureQualityReport`.
  - Files: `CreatureEndpoints.cs`, `RpgStore.Creatures.cs`, `SlotFilter.cs` (join only), quality report, focused tests.
   - Dependencies: Task 7 (Task 8 parallel-safe — confirmed by owner 2026-09-12, see GAP-6/7; plan.md's graph corrected to match). Scope: M.
   - **CLOSED 2026-09-23 by lane `cs-rank-b`** (evidence `tasks/reports/creature-seed-rank-t9.md` close-out):
     `CreatureProfileDto` + `CreatureCodexEntryDto` carry nullable `rank`/`rankDisplayName`;
     `RpgStore.Creatures.cs` fills roster/codex/profile reads off the catalog (`IsKnown`-guarded);
     catalog projection + fusion previews project them off the def; `CreatureRankIds.ToDisplayName`
     beside `ToId` (no new tuning file — would be an unmapped enforced-root file); quality report gains
     the rank-coverage line + explicit `ReportDiversity("rank", …)` (GAP-5 closed). Orchestrator must
     still run the row's Verify line (no shell here).

## Checkpoint: Landing
- [x] Zero golden moves; full Core + Data + Guard suites green; audit-magic-numbers clean; review before follow-ups.
  **CLOSED 2026-09-23 (lane `cs-rank`) at the integration tip `d4ec51ffd`**, each suite run in this
  increment: `gk-core/tests/FusionRpg.Core.Tests` **EXIT=0 — 9705 passed / 0 failed, 1 m 17 s**; the Data project
  through the sharded runner (`verify-change` over `RpgStore.Species.cs` + `RpgStore.Fusion.cs` + their
  tests) **EXIT=0 — 4 shards, 1752 tests, no overlap**; `run-guards.ps1 -Tier ci` **EXIT=0 — 25 guard(s)
  run, 0 red**; `audit-magic-numbers.py` **M1=0 M2=0 M3=0 M4=0**; and zero golden moves —
  `CreatureSpeciesGen --check` is `clean, 904 species match`, the expedition tier goldens were proven
  unchanged by Task 10, and no test golden moved in any lane increment (T1-T12). Evidence:
  `tasks/reports/creature-seed-closeout.md`. The review the line names is the manager's, and it has been
  made at every increment (each accepted and merged).

## Phase 5: Follow-up gates (independent of each other; each with own pass-through proof)

- [x] Task 10: Expedition wild-band rank floor — closed 2026-09-23 by lane `cs-rank`
  (session `creature-seed-rank`); evidence `tasks/reports/creature-seed-rank-t10.md` (Expeditions project
  38/38 with the four tier goldens UNCHANGED, Core 9587/0). The floor is additive beside `!= CaptureOnly`
  and `!= Sunwoven`, and the task also fixed a defect it would otherwise have introduced: the empty-band
  fallback was a fixed `WildBand(Chaff)` lookup, which a floor above the Chaff band empties — the fallback
  now walks the ladder for the lowest non-empty band and refuses by name when none is left.
  - Acceptance: floor on `WildBand` filter; Sunwoven exclusion + EventOnly admission preserved; pass-through proof.
  - Verify: focused expedition tests green.
  - Files: `ExpeditionResolver.cs`, focused tests. Dependencies: Task 9. Scope: S.

- [x] Task 11: Wave-band rank floor — closed 2026-09-23 by lane `cs-rank` (session `creature-seed-rank`);
  evidence `tasks/reports/creature-seed-rank-t11.md` (wave suites 23/23, whole Core residual 9594/0). The
  floor is additive beside the rarity window and `CreatureAdmission.ForWave` — a raised floor refuses
  CaptureOnly/EventOnly on exactly the same terms as before (proven with the floor at the top rung), and a
  rank-skipped species is dropped rather than waved through because null maps to the bottom rung at the gate.
  **Doc erratum filed as T11-N** (the spec's own "Band has no acquisition filter" sentence is stale).
  - Acceptance: floor on band membership; no-acquisition-filter behavior preserved; pass-through proof.
  - Verify: focused battle/wave tests green.
  - Files: `WaveCatalog.cs`, focused tests. Dependencies: Task 9. Scope: S.

- [x] Task 12: Cage eligibility rank floor — **IN-FENCE HALF LANDED 2026-09-23, ROW LEFT OPEN ON THE
  CALLER WIRE; raised-floor clause REOPENED 2026-09-24, see close-out below.** Evidence `tasks/reports/creature-seed-rank-t12.md` (Delve/wild suites 160/160, whole Core
  residual 9596/0). Landed: `Cage.OccupantEligible` takes a REQUIRED `CreatureRank?` and narrows on it as a
  third condition beside `!captureOnly` / `!isTopRung`; the price is proven rank-blind (`OfferPricing.Contract`
  returns the same value with the floor at the bottom and at the TOP rung); the existing theory's four
  expectations pass with a null rank, which is both the shipped compiled-roster state and the pass-through.
  **BLOCKER:** `Cage.OccupantEligible` has NO production caller — measured, `grep` finds only the definition
  and `CageTests` — and the wire is the Delve wild endpoint at `gk-core/src/FusionRpg.Server/**`, which this lane's
  fence denies (`path is outside session scope`). Pre-existing, not introduced here (the spec's own table:
  "No Delve-side band selector exists … talk/cage commit caller-assembled specs"), so the floor is declared,
  tested and inert until a host passes a rank in — the same denied-path gap as T8's boot wire.
  - Acceptance: floor on `OccupantEligible`; pricing untouched (rarity-keyed); pass-through proof.
  - Verify: focused Delve/wild tests green.
   - Files: `Delve/Wild/Cage.cs`, focused tests. Dependencies: Task 9. Scope: S.
   - **CLOSED 2026-09-23 by lane `cs-rank-b`** (evidence `tasks/reports/creature-seed-rank-t12.md`
     close-out): `DelveWildEndpoints.HandleJoin` (shared `/talk`+`/cage`) passes the candidate's catalog
     rank into `Cage.OccupantEligible`; structural inputs mirror `ExpeditionResolver.WildBand`
     (`== CaptureOnly`, `== Sunwoven`); refusal `wild.below-rank-floor` before any spend; pricing
     untouched; 2 new endpoint tests (refusal + pass-through on scoped ranked defs). Orchestrator must
     still run the row's Verify line (no shell here).
    - **REOPENED 2026-09-24 (manager): the raised-floor refusal is UNPROVEN and the gate is REVERTED.**
      Manager-side gates: the below-floor test returns 200 (join succeeds) under an Almanac floor that
      provably sticks (asserted in-body, no throw) — root cause unidentified after link-by-link probing
      (floors/Validate/scoping/ladder/enum/catalog all read correct; single vs duplicated types ruled
      out). Per the no-unverified-harvest rule the `wild.below-rank-floor` hunk and the below-floor test
      are reverted out of this tree; the pass-through test, the Sunwoven-exclusion fixture fix, T8/T9 and
      all green gates stay. Gate code preserved verbatim in unmerged branch `opencode/cs-rank-b`.
      T12's remaining work: diagnose why a configured Almanac floor does not refuse, then re-land.
    - **DONE 2026-09-24 (mega-merge QC fix cycle 10) — ROOT CAUSE FOUND, RE-LANDED, PROVEN.**
      The reverted refusal was never the bug: the wire itself was correct. The manager's below-floor
      test used the shared `WildSpecies` fixture, whose predicate
      (`Acquisition != CaptureOnly && TraitPool.Count > 0`) resolves to **`dolldiamond`, a Sunwoven
      species — the top rarity rung, which the cage's structural rule has always excluded**. So the
      endpoint returned 400 for the STRUCTURAL reason, never reached the rank floor, and the test's
      200-vs-400 assertion was read as "the floor did not stick" when the candidate had simply been
      refused earlier. (The pre-wire endpoint was inert — `OccupantEligible` had no caller — so the
      fixture bug had been invisible.) Re-landed the exact wire from the preserved
      `cs-rank-b` ledger note: `HandleJoin` maps `Acquisition == CaptureOnly` / `BaseRarity ==
      Sunwoven` / `candidate.Rank` into `Cage.OccupantEligible`, refusing `wild.below-rank-floor`
      BEFORE `TalkJoin` spends; an unknown species keeps `TalkJoin`'s own refusal (no fabricated
      rank). Also fixed the fixture's predicate (now mirrors `ExpeditionResolver.WildBand`'s two
      structural conditions) — the "Sunwoven-exclusion fixture fix" the reopen note mentioned.
      *Proof:* `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter FullyQualifiedName~DelveWildEndpoints`
      → **15/15** (incl. a new below-floor test that asserts the exact `wild.below-rank-floor` reason,
      souls untouched, no mint, under an Almanac floor on a scoped Chaff def); whole
      `FusionRpg.Server.Tests` **862/862**; `CageTests` 13/13; `guard-magic-numbers` OK;
      `guard-population-pin` 0 findings.
      *Files:* `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`.

- [x] Task 13: C# mirror of `speciesKind: "excluded"`, consumed in `CreatureAdmission` (map ask 4) —
  closed 2026-09-20 by pointer (`backlog-clean-up` `paperwork-reconcile` P6):
  `tasks/summoner-convergence-lane-c-ledger.jsonl:45-47` "T47 closed with CS13 = `be3ac8a6`:
  speciesKind now rides AnchorRowReader -> SpeciesExpander -> ConcreteSpecies -> CreatureSpeciesDef ->
  CreatureAdmission refuses excluded in every context"; `gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs:9`
  doc-comments "R-CS3/R-CS4 (CS13)".
  - Why: the 12 `speciesKind: "excluded"` rows ship as `Summonable` in `gk-data/packs/fusion/data/generated/creatures/**`, and
    `CreatureAdmission.cs:14-24` admits them in every context; no C# code reads `speciesKind`. This
    enforces existing rulings R-CS3/R-CS4 ("never spawn, never draw"). It is not a new product decision.
  - Acceptance: `speciesKind` reaches the runtime species record through the generator's existing output
    (no hand-edit of generated files); `CreatureAdmission` refuses an excluded species in every context from
    that one declaring site (no per-roller or per-table filter); a planted excluded species is refused and
    a normal one admitted; the test asserts the contract, not the count of excluded rows.
  - Verify: focused `CreatureAdmission` tests plus the species import tests green; `CreatureSpeciesGen --check`
    clean.
  - Files: `gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs`, the species record or loader it reads,
    focused tests. Dependencies: none. Scope: S. Built by summoner-convergence lane C (the orchestrator
    assigned it on 2026-09-19: creature-seed has no active session, and species-gear-chain T47/T34c wait on it).

## Checkpoint: Complete
- [ ] All acceptance criteria met; all suites green; ready for review.

## Gap audit (2026-09-12 — plan/spec cross-check; see also inline GAP-1/2/3/5/6/7 notes above)

- [ ] **GAP-4 — `creature-seed-map.md` §3 module table not updated.** The map's 18-module table,
  dependency graph, and build-order block (all dated up to 2026-09-05) do not list `species-rank` as
  module 19, despite the spec's own header declaring `Program: creature-seed` and depending on modules
  4 (`threat-band`) and 10 (`rarity-migration`). Per this repo's own convention ("the capability map is
  the index — never guess the active spec from filenames"), landing this module leaves the program's
  own index stale from day one. Add a task (fold into Task 9's checkpoint, or its own S-scope task)
  to add module 19, its dependency-graph arrows, and a build-order line before Checkpoint: Complete.
  Dependencies: none (doc-only). Scope: S.

- [x] **GAP-1 — Task 4's Verify line cites the wrong task for the quality-report line.** Original text
  read *"rank-coverage line arrives in Task 8"*; Task 8 is fusion floors, not the quality report — the
  rank-coverage line is Task 9. Corrected inline above. — closed 2026-09-20 by pointer (P6): the fix
  is already visible inline at Task 4's own Verify line ("Corrected — see GAP-1"); this box was just
  never re-ticked to match.

- [x] **GAP-2 — Task 4 listed `gk-data/packs/fusion/data/generated/creatures/**` regen a phase too early.** That regen needs
  `SpeciesExpander` (Task 5) and the `ConcreteSpecies` triad (Task 6) to exist first — the concrete
  schema cannot carry a field that doesn't exist yet in the C# model. Moved to Task 6, which already
  claimed "regen output carries rank through all three" in its own verify line. Corrected inline above.
  — closed 2026-09-20 by pointer (P6): same pattern as GAP-1, the correction is already in Task 6's text.

- [x] **GAP-3 — Spec-named doc hazard never became a task.** `spec-species-rank.md` §4 explicitly flags
  `SpeciesSnapshot.cs:78-91`'s stale comment (*"every host calls `ConfigureFromCompiledDefault`"*) as a
  hazard to *"bundle with this change"* — verified still false and still present
  (`Server/Program.cs:370` calls the store-backed `Configure`, not `ConfigureFromCompiledDefault`).
  Folded into Task 6 (comment-only edit, same Injector-path task). Corrected inline above. — closed
  2026-09-20 by pointer (P6): the fold-in is already recorded in Task 6's own acceptance text.

- [x] **GAP-5 — Quality-report diversity section left ambiguous.** Spec §7 says the report's existing
  diversity section (`gk-forge/tools/CreatureQualityReport/Program.cs:160-209`) "reads the new tuning vocab" alongside the new
  rank-coverage line — unclear whether that means it already picks rank up generically or needs an
  explicit added dimension. Task 9's acceptance now asks to state which, rather than silently doing
  neither. Corrected inline above. — closed 2026-09-20 by pointer (P6): the ask is already recorded
  in Task 9's own acceptance text.

- [x] **GAP-6/7 — RESOLVED 2026-09-12 (owner).** `creature-seed-plan.md` and this file disagreed on
  Task 8/Task 9 ordering (plan said "T8→T9 sequential" + a linear ASCII graph; this file already said
  "Task 8 parallel-safe"). Owner confirmed parallel-safe — file sets are disjoint
  (`RpgStore.Fusion.cs`/`FusionEndpoints.cs`/`CreatureRecipeCatalog.cs` vs.
  `CreatureEndpoints.cs`/`RpgStore.Creatures.cs`/`SlotFilter.cs`), no code dependency forces the order.
  `creature-seed-plan.md`'s prose and dependency-graph ASCII both corrected to show T8/T9 as parallel
  branches after T7. Also fixed: the plan's stale `T5a→T5b→T6→T7` reference (this file only ever had
  a single Task 5) corrected to `T5→T6→T7`.

---

- [ ] **T11-N — the spec's Task 11 row describes a filter behaviour the code no longer has.** · XS ·
  **Owner:** this program (doc-only; `docs/**` is outside this lane's fence, hence the row).
  **Cause, read and not inferred:** `docs/architecture/creature-seed/spec-species-rank.md`'s gate table says
  `WaveCatalog.Band` "has no acquisition filter — CaptureOnly can march: pinned, not fixed here". Measured
  2026-09-23 while wiring the wave floor: `gk-core/src/FusionRpg.Core/Battle/WaveCatalog.cs` applies
  `CreatureAdmission.ForWave`, which requires `Summonable` and refuses `EventOnly`
  (`gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs:27-28`), and
  `gk-core/tests/FusionRpg.Core.Tests/Battle/WaveSpeciesRollTests.cs` pins that behaviour green — so CaptureOnly does
  not march. **Acceptance:** the spec sentence is corrected (or dated) to match the code, and the same
  sweep checks the neighbouring `WildBand`/Cage notes it was written alongside. **Verify:** read the two
  files named above against the spec row.

---

## Received from `roster-balance` (via `backlog-clean-up` BCU4.5, 2026-09-20) — the species roster's own real findings

`roster-balance` ran `creature_roster.py`'s existing, already-tuned metrics against the real corpus for
the first time (`T2.11`, `tasks/seed-to-concrete-todo.md`) and produced **19 real GAP findings**. It then
deliberately did *not* build against them: its own §0 correction proved the species roster and the
atom-family diversity bug it was named for are two systems sharing the word "family" and nothing else
(`docs/architecture/roster-balance-map.md:16-32`). The findings were handed here instead —
`roster-balance-map.md:59-66` and `tasks/roster-balance-todo.md:120-122`. **This row exists so they are
a real task, not a dropped handoff.**

**The findings (all readings from that one run — re-measure before acting, do not treat as constants):**

- **Grid occupancy 65/252 cells (257‰), against a 900‰ target.**
- **Non-monotone rarity** — the ladder's `count` vs rank relationship is not monotone against the shipped roster.
- **Single-element share 973‰**; **posture imbalance**; **aptitude skew** — axes that are nominal cover
  far less of their own grid than the count of species suggests.
- **A metric-blindness finding, separate from the content finding:** `posture: "unresolved"` (12 rows) is
  invisible to *every* existing metric. `UnresolvedCount`'s `VOTED_FIELDS` omits `posture`, and
  `PostureBalanceMetric` silently drops rows matching none of its three keys. **A row no metric can see
  is a row no gate can ever fail on**, which is the more urgent half: it means "posture is balanced" is
  currently unfalsifiable, not merely unmeasured.

- [x] **RB-H1 — audit the species roster's coverage axes, and make the two blind spots visible.** —
  **CLOSED 2026-09-23 by lane `cs-rank`** (session `creature-seed-rank`); evidence
  `tasks/reports/creature-seed-rb-h1.md` (readings for all eight axes + a disposition each; 18 passed in the
  metrics' own suite, 67 passed on the row's own `-k roster` line, 240 passed on `-k "metric or roster"`).
  The two blind spots are fixed: `UnresolvedCountMetric.VOTED_FIELDS` carries `posture` (with sub-threshold
  counts reported at `Severity.NOTE`, so no gating metric was silently tightened) and
  `PostureBalanceMetric` counts and reports every row whose posture is none of its three keys instead of
  skipping it. **Two dispositions came out as tuning changes and are filed as RB-H1-F** (the grid target is
  mis-scaled for a 252-cell cross-product; the 486-strong `fused` mass is the deterministic fallback's own
  rung, not a classification outcome).
  **Owner:** this program (`creature-seed`); the metrics themselves stay `roster-balance`'s.
  **Description:** re-run `creature_roster.py` against today's corpus to get current readings, then decide
  per axis whether the skew is a content gap (generate the missing cells), a ladder/curve problem
  (a `creature-seed` tuning change), or an accepted distribution with a stated reason — **a reading is
  not a defect until someone says which of the three it is.** Separately and first, fix the two metric
  blind spots so `posture: "unresolved"` is counted by `UnresolvedCount`'s `VOTED_FIELDS` and is not
  silently dropped by `PostureBalanceMetric`; a metric that skips its own unresolved rows cannot gate
  anything.
  **Acceptance:**
  - [x] `posture: "unresolved"` is visible to both metrics (a test with a planted unresolved row proves
        it, and proves the old behaviour was a silent drop rather than a zero) — 2026-09-23
  - [x] Current readings for each axis recorded in the evidence, each dispositioned as content gap /
        tuning change / accepted-with-reason — 2026-09-23
  - [x] No population size is pinned in a test — counts are readings (`validation-ssot.md`)
  **Verify:** `python -m pytest gk-forge/tools/seedsmith/tests -q -k roster` (or the metrics' own suite) once the
  metrics change, plus `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~Creature` if a
  tuning table moves. **Files:** the two metric implementations; possibly `data/tuning/creature*.v{n+1}.json`
  through `publish.py`. **Scope:** S–M.

---

- [ ] **RB-H1-F — the two tuning changes RB-H1's readings landed on.** · S · **Owner:** this program;
  **needs an owner ruling** (a balance change). **Filed by:** lane `cs-rank`, 2026-09-23, out of
  `tasks/reports/creature-seed-rb-h1.md`'s dispositions so they are a row rather than a paragraph.
  **Description:** two axes read as *ladder/curve* problems, not content: (1) `gridFill` reads
  **129/252 cells (511‰)** against a **900‰** target, and that target is unreachable for a 252-cell
  cross-product at this corpus size — the fix is a retune of
  `gk-core/data/tuning/creature-roster-targets.v1.json`'s `gridFill.minOccupiedSharePermille`, published as a new
  revision through `gk-core/tools/tuning/publish.py`; (2) `rarityMonotonicity` reads four non-monotone adjacent
  pairs, dominated by **`fused` 486** of 904 species, which is the *deterministic fallback's* own rung
  (`creature-rarity-power-fallback.v1.json` maps threat rung 5 → `fused`) — so either the fallback table or
  the metric's own band needs the ruling. **Acceptance:** each of the two axes is either retuned (a
  published `v{n+1}` file + the metrics re-run, numbers in the evidence) or accepted-with-reason in the
  target file itself (a `_meta` note saying why the shipped reading is the intended shape) — never left as a
  reading with no owner decision. **Verify:** `python -m pytest gk-forge/tools/seedsmith/tests -q -k roster` plus the
  metrics re-run over the corpus with the new/annotated target. **Files:**
  `data/tuning/creature-roster-targets.v*.json`, possibly `data/tuning/creature-rarity-power-fallback.v*.json`.
  **Dependencies:** RB-H1 (closed).

---

## Received from `party-dungeon` F1 (via `backlog-clean-up` BCU4.6, 2026-09-20) — 721 of 906 species anchors have no `threatBand`

**The finding, re-confirmed live 2026-09-20:** `721 of 906` real species anchors still lack a
`threatBand` (`tasks/party-dungeon-todo.md:3676-3683`, re-confirmed in BCU4.6). A reading, not a
constant — re-measure before acting.

**Why it is filed here rather than fixed in `party-dungeon`:** it is species-classification thinness,
not a dungeon defect. Every real dungeon domain refuses on row 6 (`domain.encounter:*`) because the
encounter pipeline needs a classified species to draw from, so a whole program's landing gate is held
by this one axis — and **module ownership is already split correctly**: module **4 `threat-band`**
owns the tuning table (parsed number -> one of ten threat-noun rungs -> a `Theta` offset, a table never
a formula — `docs/architecture/creature-seed-map.md:111`), and module **7 `classify-pipelines`** owns
the eight LLM judgement pipelines that fill it (`:114`). Nothing new needs inventing.

- [ ] **TB-H1 — raise real `threatBand` coverage to the corpus.** **Owner:** this program, modules 4
  and 7. **Description:** run the classification pipeline over the unclassified anchors so
  `domain.encounter:*` can resolve for a real domain, then confirm the tuning table still maps every
  produced rung to a `Theta` offset (a rung with no row is a silent no-op, not a classification).
  **A known, separate gap stays separate:** `creature-threat.v1.json`'s `thetaOffset` has **zero
  consumers in `src/`** (`creature-seed-map.md:296`) — filling `threatBand` does not make the offset
  live, and this row must not be read as closing that one.
  **Lane status 2026-09-23:** boxes 1 and 2 satisfied and evidenced in
  `tasks/reports/creature-seed-tb-h1.md` (the coverage fill landed earlier in the program: the row's own
  2026-09-20 reading of **721 of 906** missing became **904 of 904 resolved** — 1000 permille, remainder
  zero — with all 10 rungs populated, 0 orphans; and a new reconciliation test asserts both the mapping
  and the loud refusal of a rung with no row). **Box 3 stays open and is `party-dungeon`'s own
  acceptance** — "F1 can close on a real six-domain run, not on this row's own say-so" — so this row
  ends the segment open on exactly that one box, owned by that program.
  **Acceptance:**
  - [x] Coverage is reported as a before/after reading (never a pinned count), with the unclassified
        remainder named and its reason stated if it is not zero — 2026-09-23 (remainder is zero)
  - [x] Every produced rung maps to a real `creature-threat` table row (asserted), and a rung with no
        row fails loudly rather than classifying to nothing — 2026-09-23
  - [ ] `party-dungeon` F1 can close on a real six-domain run, not on this row's own say-so — **blocked
        on `party-dungeon`'s own run; nothing on this lane can satisfy it**
  **Verify:** the pipeline's own suite, plus whatever `creature-seed-map.md` §4 names for module 4's
  validator. **Scope:** M. **Blocks:** `party-dungeon` F1 (`domain.encounter:*` refusal).

- [ ] **TB-H2 — the corpus classifies against a retired threat ladder: `creature-threat.v2.json` was
  published and every C# reader stayed on v1.** **Owner:** this program, module 4 (`threat-band`).
  **Filed by:** lane `cmdc-ep2-1` (`empire-progression`), 2026-09-20, while wiring
  `per-species-lean`'s rung order.
  **Description:** `5eeddecc` published `gk-core/data/tuning/creature-threat.v2.json` (R-CS5: `maxScore`
  re-fitted with `costMilli`, because v1's boundaries were "a fit to missing-data-as-zero"). The
  seedsmith side followed — `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/power/bands.py:6` is
  `TUNING_KEY = "creature-threat.v2"` — but **no C# reader moved**:
  `gk-forge/tools/CreatureSpeciesGen/Program.cs:73`, `gk-forge/tools/CreatureQualityReport/Program.cs:64`,
  `gk-forge/tools/CreatureRecipeReconcileInput/Program.cs:65`, `gk-forge/tools/CreatureRecipeDistributionIndex/Program.cs:59`,
  `gk-forge/tools/CreatureSpeciesImport/Program.cs:71`, `gk-forge/tools/ProveHubCombat/Program.cs:81` and
  `gk-core/src/FusionRpg.Server/Program.cs:124` all still load `creature-threat.v1.json`. **Cause:** the
  publish was treated as a data-file change (the new file is what T4 records) without the reader switch
  that T5/H7 requires — so the maxScore boundaries the C# tools classify against are the retired ones,
  and `nuisance` (empty under the v1 fit the new file's own `_note` describes) can still be produced.
  `thetaOffset` and the rung ids are identical in both files, so nothing here is a magnitude change.
  **Acceptance:**
  - [ ] Every C# reader above reads the then-current `creature-threat.v{n}.json`, in one commit, with
        the version named in the commit body
  - [ ] A `rg -l "creature-threat\.v[0-9]+\.json" src tools tests --glob "*.cs"` sweep shows no reader
        on a superseded version (the tool pins are the check, not a comment)
  - [ ] `CreatureSpeciesGen --check` / `CreatureCorpusDump --verify` stay green, or the moved rungs are
        listed in the commit as this cause's only golden change
  **Verify:** the corpus tools' own `--check` runs plus `dotnet test tests\FusionRpg.Core.Tests
  --filter "FullyQualifiedName~CreatureThreat"`. **Scope:** S. **Blocks:** nothing in
  `empire-progression` — its own reader is new and reads v2 (`gk-forge/tools/CreatureBuildPlanGen/Program.cs`).


- [x] **CS-F1 — `SpeciesModLedgerTests.After_a_real_boot_a_save_that_never_fused_has_no_layer_1b_rows` FAILS at the integration head** · S · *(found by the manager running CC8's full suite, 2026-09-22, and reproduced in isolation)*
  - **Measured:** `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~After_a_real_boot_a_save_that_never_fused_has_no_layer_1b_rows"` → `Failed! 1/1` in 236 ms, `Assert.NotEqual() Failure: Values are equal — Expected: Not SeedTreeNotFound, Actual: SeedTreeNotFound`. In the full suite the same project reads `1 failed, 1780 passed`.
  - **What that means:** after a real boot, a save that never fused still carries layer-1b rows whose seed tree resolves to `SeedTreeNotFound` — the ledger is recording a fusion layer for a save that has no fusion, and the value it records is the *absence* sentinel.
  - **Why it is this program's:** the subject is the species-mod ledger's layer-1b rows; neither the test file nor its project was touched by any of the round's merges, so this is not merge fallout — it is a condition on the shipped corpus/boot path.
  - **Acceptance:** the test passes at the integration head, or the layer-1b rule it asserts is amended in the owning spec with the reading recorded. ⛔ Not by relaxing the assertion: `SeedTreeNotFound` reaching a ledger row is the defect the test exists for.
  - **Verify:** the same filter above, `Passed!`.
  - **Closed 2026-09-22 (lane `cs-f1`), and the row's own "What that means" reading was wrong.**
    Measured cause: `SpeciesModLedgerTests.RepoRoot()` (`gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs:98-102`)
    walked three levels up from a file that sits **directly** in `gk-core/tests/FusionRpg.Data.Tests`, i.e. the repo
    root's *parent* — `D:\Works\source` in the main checkout, which has no `gk-data/packs/fusion/data/seed` in any ancestor. The
    boot answered the absence sentinel **loudly and correctly** for the directory it was handed
    (`spec-player-content-boot.md:65-73`). **No layer-1b row existed and none was written**, and no sentinel
    was stored in a row, so the owning rule (`spec-species-mod-ledger.md` Behaviour 1, "No row means no
    1b.") is **not** amended and the assertion is **not** relaxed — it is strengthened. It passed in a lane
    worktree only because `FindUp` kept walking above the wrong answer and found the *main checkout's* tree,
    which is also why the worktree run silently read another tree. Fix: the private walk is deleted in favour
    of `FusionRpg.TestSupport.ContentRoot.Path` (the repo's resolver contract, `Directory.Build.props:19-22`),
    and `Assert.NotEqual(SeedTreeNotFound, …)` — which also accepted `Failed`, equally vacuous — becomes
    `Assert.True(boot.Ok, …)`. Evidence: `tasks/reports/creature-seed-csf1.md`; the filter reads `Passed!`
    (1/1) and the whole Data project `1850/0`.

- [x] **CS-R3 — the action-layer purity guard is red at the integration tip.** · S ·
  **Owner: the `lawn` program (LW1.3)** — filed here because this lane's fence excludes their files;
  the manager must route it.
  **CLOSED 2026-09-23 by that owning lane**, at the tip: `497bfa182 fix(lawn): LW1.3 exhaustion detector
  must not enumerate a dictionary (action-layer purity)` replaced `WindowCount`'s `_byPtr.Values`
  enumeration with `TrackedActors => _byPtr.Count` (a `Count`, not an enumeration). Verified from this
  lane after merging that commit: `dotnet test gk-core/tests/FusionRpg.Core.Tests` is **EXIT=0 — 9705 passed /
  0 failed**, with `ActionsPurityGuardTests` green inside it.
  **Filed by:** lane `cs-rank` (`creature-seed`), 2026-09-23, while running the whole Core project for
  TB-H1 (9611 passed / 1 failed).
  **Cause, read and not inferred:** `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionsPurityGuardTests.cs:35`
  reports `action-layer purity violated … Cost/ExhaustionEdgeDetector.cs:85 → .Values`;
  `ExhaustionEdgeDetector.WindowCount`'s getter is `foreach (var inner in _byPtr.Values) total += inner.Count;`.
  The guard forbids dictionary enumeration in the action layer because iteration order is not a contract
  (insertion/hash dependent), and the value is only a reading — so the fix is the code's, not the guard's.
  Introduced by `467cfa058 feat(lawn): LW1.3 exhaustion as an edge-triggered event, with a real lawn caller
  for ExhaustionPolicy`; this lane's diff over `gk-core/src/FusionRpg.Core/Actions/**` is empty.
  **Fix shape (owner's call):** sum over a deterministic projection keyed by the dictionary's own key
  (e.g. `_byPtr.OrderBy(kv => kv.Key).Sum(kv => kv.Value.Count)`), or keep a running counter incremented
  where windows are added. **Acceptance:** the guard is green. **Verify:**
  `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionsPurityGuardTests"`.

- [ ] **CS-F1-a — the production boot's seed-tree discovery has no Keepverse content-root awareness** ·
  S · **Owner: `keepverse-split`** (content-root owner; the caller is `content-stack`).
  **Filed by:** lane `cs-f1` (`creature-seed`), 2026-09-22. Filed *here* because this lane's fence excludes
  `tasks/keepverse-split-todo.md` — the manager must route it.
  **Cause, read and not inferred:** `SeedImportRunner.RunSelfHealing`
  (`gk-core/src/FusionRpg.Data/Seed/SeedImportRunner.cs:126-148`) finds the seed tree only through
  `FindUp(searchStartDir, "data", "seed")`, and its production caller hands it `AppContext.BaseDirectory`
  (`gk-core/src/FusionRpg.Server/Program.cs:964` region). Nothing under `src/` reads `KEEPVERSE_CONTENT_ROOT`
  (measured: `grep -rn KEEPVERSE src/` is empty), while every `*.Tests` project and every script resolve
  content through the shared contract (`gk-core/tests/Shared/KeepverseRoots.cs`, `scripts/lib/KeepverseRoots.ps1`).
  In the planned split layout (D6/D7: `gk-data/packs/fusion/data/seed/**` moves under `gk-data/packs/fusion`, binaries stay in
  gk-core) walking up from the binary cannot reach the pack, so the import answers `SeedTreeNotFound` on
  every launch — loud and non-fatal, with the content layer inert behind the code fallback. **Not measured
  in a split layout** (none exists yet); measured here is the missing resolver reference.
  **Acceptance:** the boot resolves content through the same contract as the tests, or the plan records that
  a player install ships `gk-data/packs/fusion/data/seed` beside the binary (the sibling gap already in
  `tasks/content-stack-todo.md`). **Verify:** one test booting through the real server path in a
  workspace-shaped layout.

- [ ] **CS-F1-b — nothing forbids a private repo-root walk in a test** · S · **Owner: `keepverse-split`**
  (resolver contract). **Filed by:** lane `cs-f1`, same routing reason as CS-F1-a.
  **Cause:** the resolver contract (`Directory.Build.props:19-22` comment; `tasks/keepverse-split-plan.md`)
  requires every `*.Tests` project to resolve content/core/workspace through `gk-core/tests/Shared/KeepverseRoots.cs`
  "instead of a private repo-root walk", but no guard enforces it — `gk-core/tests/FusionRpg.Guard.Tests/**` has no
  such scan and `tests/FusionRpg.Core.Tests/Workspace/KeepverseRootsTests.cs` tests the resolver itself only.
  A private `..\..\..` is depth-dependent: moving a test file into or out of a subdirectory silently changes
  which tree it reads, which is exactly CS-F1 — and the five sibling sites that use the same `"..", "..",
  ".."` are correct only because they happen to live in `Actions/`/`Saves/`.
  **Acceptance:** a Guard test fails on a `[CallerFilePath]`-derived private walk outside `gk-core/tests/Shared/`.
  **Verify:** `dotnet test gk-core/tests/FusionRpg.Guard.Tests`. The guard file is outside this lane's fence
  (`gk-core/tests/FusionRpg.Guard.Tests/**`), hence the row here.

- [x] **CS-R1 — `gk-core/data/tuning/creature-rank.v1.json` has no verification-boundary owner mapping** —
  **CLOSED 2026-09-23 by the manager** at the integration tip: `67abbcefb fix(registry): map the two
  enforced-root trees two lanes added without mapping them` adds the `creature-rank-tuning` owner boundary
  (`data/tuning/creature-rank.v*.json` -> project `core`, level `module`). Verified from this lane after
  fast-forwarding onto that tip: `guard-verification-boundaries.py` exits 0
  (`VERIFICATION BOUNDARY GUARD OK`); `verify-change.ps1 -Paths gk-core/data/tuning/creature-rank.v1.json
  -PlanOnly -AllowUnscoped` plans `creature-rank-tuning (module)` instead of aborting; and the two Guard
  tests it had made red both pass (1/1 each).
  · S · **Owner: `test-verification-boundary`** (registry owner; filed *here* because this lane's fence
  excludes `scripts/**` — the manager must route it).
  **Filed by:** lane `cs-rank` (`creature-seed`), 2026-09-23.
  **Cause, read and not inferred:** `gk-core/scripts/verification-boundaries.v1.json` carries one owner row per
  shipped tuning domain — `tuning-creature-threat` at `:3427-3433` is the sibling shape — and no row
  matches `gk-core/data/tuning/creature-rank.v1.json` (the mapping is per-domain, not a `gk-core/data/tuning/**` glob).
  `scripts/verify-change.ps1` therefore aborts `VERIFICATION BOUNDARY MISSING:
  gk-core/data/tuning/creature-rank.v1.json` for a lane that touches the new domain's own file, and the AGENTS.md
  rule forbids compensating with a broad suite.
  **Acceptance:** a `tuning-creature-rank` owner row (or a documented `gk-core/data/tuning/**` fallback) exists, and
  that path plans a focused check instead of aborting. **Verify:**
  `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/data/tuning/creature-rank.v1.json') -PlanOnly -AllowUnscoped"`.

---

## Finding routed from `test-verification-boundary` (TVB-F22, 2026-09-22)

- [x] **`gk-core/data/tuning/creature-rank.v1.json` has no verification-boundary owner** — **CLOSED 2026-09-23,
  by the same manager registry commit that closed this lane's own duplicate row (CS-R1, line 474):
  `67abbcefb` adds `creature-rank-tuning` (`data/tuning/creature-rank.v*.json` -> project `core`, level
  `module`).** Verified from this lane at the integration tip: `guard-verification-boundaries.py` exits 0
  (`VERIFICATION BOUNDARY GUARD OK`) and `verify-change.ps1 -Paths gk-core/data/tuning/creature-rank.v1.json
  -PlanOnly -AllowUnscoped` plans `creature-rank-tuning (module)` instead of aborting.
  `python gk-core/scripts/guard-verification-boundaries.py` fails with
  `unmapped enforced-root file: gk-core/data/tuning/creature-rank.v1.json` (`gk-core/data/tuning/**` is an enforced root from
  `seam-coverage`, TVB4.4, so every file under it must resolve to an owner row). Found while increment 66 of the
  Core test split was landing; the same walk passed on the previous increment, so the file arrived with recent
  work. **Fix:** one additive owner row in `gk-core/scripts/verification-boundaries.v1.json` — a wildcard
  `data/tuning/creature-rank.v*.json` mapped to the project whose tests prove it (or `gen-creature-*` if a
  generator owns it), the way the other tuning domains are mapped. Owning program: creature-seed.

- [x] **CS-R2 — the ci-tier GATING `population-pin` guard is red at the integration tip** —
  **CLOSED 2026-09-23: the owning lane fixed it at the integration tip** (`c9af301b2 fix(guards): three
  integration-head reds the merged lane work introduced` — the `Assert.Equal(500, grantedIds.Count)` line
  now derives its expectation from the roster instead of pinning the literal). Verified from this lane:
  `python gk-core/scripts/guard-population-pin.py` reports `total 0 finding(s)`. It was never this lane's file and
  this lane never touched it.
  · S · **Owner: the `ADG-F5` lane / `action-unlock` program** (filed *here* because this lane will not
  touch another lane's in-flight test file; the manager must route it).
  **Filed by:** lane `cs-rank` (`creature-seed`), 2026-09-23, while running the guard batch for Task 6.
  **Cause, read and not inferred:** `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:220`
  reads `Assert.Equal(500, grantedIds.Count);` with no `pin:` marker, and `gk-core/scripts/guard-population-pin.py`'s
  P1 requires a marker on that line or the line above (`pin: closed-vocabulary <Owner>` /
  `pin: immutable <path>`). The file is byte-identical to `features/mega-merge` (this lane's diff over it
  is empty) and was introduced by `3a3d0d2da fix(ADG-F5): a refused option is skipped with a reason and
  reported, never thrown`, so this is an integration red, not merge fallout and not this lane's.
  `gk-core/scripts/enforcement-registry.v1.json` lists `population-pin` as `tier: ci`, `status: gating`, so
  `run-guards.ps1` fails on it.
  **Fix shape (one line, the owner's call):** 500 is a seed-iteration count, so comparing against the
  loop's own bound (`Assert.Equal(seeds.Length, grantedIds.Count)`) is the contract-shaped fix; a
  `pin:` marker would also satisfy the guard but asserts a population reading.
  **Acceptance:** `python gk-core/scripts/guard-population-pin.py` reports 0 findings. **Verify:**
  `pwsh -NoProfile -File scripts/guard-population-pin.ps1`.
