# Mega-merge deep audit — manager handoff

**Status:** complete — eight read-only OpenCode CLI audit passes completed and independently checked. This is an evidence handoff, not an implementation approval.

## Decision summary

The current `mega-merge` process is **not sufficient deep audit evidence**. The verification lane reproduced a false-green merged-head path: `.claude/cmdc-agents/scripts/post_merge_check.py` can print `VERDICT: RED` and still leave the process exit code at `0`. The lane also found that acceptance does not require an immutable reviewed SHA or a non-empty check set, release is not a superset of CI, and scoped verification can omit split Core projects. A green guard run is therefore evidence that the selected checks ran, not evidence that the merged repository is correct.

The independent cross-domain falsifier confirmed the major runtime candidates and added a reachable long-to-int HP narrowing defect. No P0 incident was established. The highest-priority confirmed work is server-owned Delve resolution/pricing, fail-closed merge/release verification, battle ActorHub/numeric integrity, web recovery contracts, expedition replay/concurrency identity, and generated-vocabulary closure.

## Charter and fleet

- Runtime: repository OpenCode CLI runner
- Model: `opencode/space-bunny-free`
- Allocation: six independent domain audits, then one cross-domain falsifier and one roadmap/verification verifier
- Token cap: removed by the owner on 2026-09-25; lanes were allowed to finish
- Concurrency: maximum six lanes
- Stop rule: report completion or quota/context error; no model fallback
- Agent changes: forbidden; every completed lane returned `changed_files: []`

| Lane | Audited SHA | Result | Scope |
|---|---|---|---|
| 01 integration | `ae5e217e9f21ab7f01f7dcf83626a1e45f3a0d2b` | done | merged interaction seams |
| 02 Core combat | `ae5e217e9f21ab7f01f7dcf83626a1e45f3a0d2b` | done | Hub, writer, Funnel, battle apply |
| 03 Data/Server | `ae5e217e9f21ab7f01f7dcf83626a1e45f3a0d2b` | done | expedition dispatch/collect/read-back |
| 04 Web | `ae5e217e9f21ab7f01f7dcf83626a1e45f3a0d2b` | partial | one Server-to-lawn synchronization path; no browser/deps |
| 05 Content/seed | `ae5e217e9f21ab7f01f7dcf83626a1e45f3a0d2b` | done | FamilyExpandGen and atom consumer closure |
| 06 Verification/release | `351c30828` | partial report | merged-head, CI/release, guards, operations |
| 07 falsifier | `31f83afe971a199cda1617dedf9d501e919e2e7d` | partial report | independent candidate disproof |
| 08 roadmap verifier | `bb22d8052` | partial report | maps, owners, sequencing, verification boundaries |

The first broad attempts that were replaced after budget exhaustion or worktree-permission failures were not counted as evidence. The final report set above is the accepted evidence set. Every retained agent directory has `verify.json: pass=true`, no out-of-scope files, no changed files, and `audit --id` returned no findings.

## Confirmed findings

### Verification and merge process

1. **P1 — merged-head check is not fail-closed.** `.claude/cmdc-agents/scripts/post_merge_check.py:61-84,144-145` records/prints a RED verdict but does not return a failing process status. Its default project list is also only two projects, and no CI/release caller was found.
2. **P1 — acceptance is not bound to an immutable reviewed SHA.** `.github/workflows/ci.yml:3-7`, `.claude/cmdc-agents/scripts/merge-lanes.py`, and `.claude/cmdc-agents/scripts/accept-lane.ps1` make the expected SHA optional, allow an empty check array, and do not require a schema-valid acceptance artifact before merging a mutable lane tip.
3. **P1 — release is not a full CI superset.** `.github/workflows/release.yml` omits multiple test, guard, generator, content, web, E2E, Server, and importer surfaces present in CI and has no enforcement-gate dependency.
4. **P1 — scoped verification routes split Core areas to `core-residual`.** `gk-core/scripts/verification-boundaries.v1.json:5436-5453,5489-5526` maps Activity, Delve, Expeditions, PassiveTree, Progression, Scope, and Vfx to the residual project despite owner groups existing. `verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs -PlanOnly` selected `core-residual` rather than the split Expeditions project.
5. **P1 — generated-seed protection is not push-range complete.** `scripts/run-guards.ps1:41-50` defaults to `HEAD~1..HEAD`; `guard-generated-seed.py:97-110` therefore misses an earlier hand edit in a multi-commit push. CI fetch depth reinforces the same boundary.
6. **P1 — session boundaries are advisory rather than diff-enforced.** The `session-boundary` guard is backlog status, no CI/release caller invokes `session-boundary-check.py`, `verify-change.ps1` checks only caller-supplied paths, and acceptance does not compare the reviewed diff with the session record.
7. **P1 — zero-test filtered runs can be accepted as green.** `verify-change.ps1:306-317` checks process status but not a non-zero executed-test count. A `dotnet test --filter FullyQualifiedName~ResidualFitLoopTests` reproduction printed `No test matches the given testcase filter` without failing the command.
8. **P1 — player packaging can continue after native build failure.** `scripts/publish-player.ps1:46-81,105-115,154-178` does not consistently check `npm`/`dotnet` exit codes. The reproduction `pwsh -NoProfile -Command '$ErrorActionPreference="Stop"; & cmd /c exit 7; "after-native-failure"'` printed the trailing line and returned process exit `0`.
9. **P2 — verification ownership is incomplete.** The boundary walk filters test files to `.cs`; `gk-core/tests/tools/test_audit_program_pipeline.py`, operational scripts, and several production tools have no path-owned plan. The Data-only nightly is explicitly intentional and is recorded as a topology/documentation question, not promoted to a defect.

### Delve / Server

10. **P1 — join outcome and price are caller-controlled within the scoped route.** `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:103-134` accepts the submitted `Spec` and `Price`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:1495-1525` spends that price and mints that spec. `DelvePrices.OfferFloor` is not called. The persisted room row/column is resolved by `sectorId`, so the stronger “room coordinates are caller-controlled” subclaim was rejected.
11. **P2 — party steering is structurally permissive.** `ProductionIsPartySteered` always returns true in the inspected route and `PartyEntityId` is not passed into the join call. This needs an explicit reachability/ownership decision, not another local default.

### Core / battle

12. **P1 — live battle derived state bypasses ActorHub.** `BattleDerivedModifierLedger.Recompose` writes live state directly (`BattleDerivedModifierLedger.cs:86-96`; `BattleRunState.cs:390-434,250-260`) instead of contributing through the one ActorHub fold. Initial setup still uses `BattleHubCompose`; the defect is the live update path.
13. **P1 — battle damage telemetry reports pre-clamp amounts to higher-level observers.** `DamageApplyPipeline.cs:87-105` returns the requested post-shield amount while the sink may clamp HP; `BattleRunState.cs:1207-1224` raises `OnDamageTaken` from that pre-clamp value. `BattleEffects.LastApplied` itself is already clamped, so the defect is the higher-level result/event path.
14. **P1 — reachable long HP is narrowed to int.** `BattleModels.MaxHp` is `long`, but `BattleEffects.cs:315-317` casts the bounded resource delta to `int`. This violates the repository's checked magnitude-range rule at reachable values above `Int32.MaxValue`.

### Web / control room

15. **P1 — cold clients and reconnect have no authoritative hydration/replay edge.** `hub-provider.tsx:213-232`, `RpgHub.cs:32-38`, and `EventIngest.cs:215-223` rejoin groups but do not replay events or send a snapshot. A reload or reconnect can retain an empty/stale view.
16. **P1 — snapshot bindings lose empty and reverse-order edges.** `lawnProjectorFold.ts:770-848` overlays bindings only onto existing occupants, does not clear stale bindings for an empty snapshot, and loses a binding that arrives before spawn.
17. **P2 — the client ring is not partitioned by match key.** `log-store.ts:8-10,71-89` and `lawnProjectorFold.ts:872-877` can accept a delayed/foreign-match event and change the visible model. The code behavior is definite; reachability depends on the server's multi-match contract.
18. **P2 — load failures are rendered as stale/empty.** `queries.ts:368-377` and `LawnPage.tsx:900-925,1362-1369` do not distinguish a 404 from a 500/network failure. The same report identified keyboard-inaccessible occupant rows and a hard-coded hub-status label.
19. **P2 — active board-stat polling rebuilds/rehydrates the full living model.** `LawnPage.tsx:143-159` polls at 1.5 seconds; volume measurements at 10/100/1000 occupants were not present. This is a measured-risk follow-up, not a claimed performance failure.

### Data / expedition

20. **P1 — committed collect has no durable result/replay response.** `ApplyExpeditionRewards` commits terminal state/rewards at `RpgStore.Expeditions.cs:296-364`; `CollectAsync` constructs the result only in memory at `ExpeditionEndpoints.cs:193-233`, and a retry returns `expedition.collected` at `:83-86` without rebuilding the result. A post-commit crash loses the reveal/materials/XP response.
21. **P2 — active expedition membership has no database-enforced uniqueness.** The check is an instance-local gate, while `RpgStore.cs:837-844` creates a non-unique partial index. The single-store sequential path is green; multi-handle/process concurrency remains exposed.
22. **P2 — expedition routes admit archived save IDs.** `PlayerExists` delegates to `GetPlayerUnlocked`, which does not filter `archived_utc`; the strict human-empire lookup can fail later instead of returning a clean admission error.
23. **P2 — tests cover sequential idempotency, not crash/reconnect/concurrency windows.** The E2E and Data tests do not exercise post-commit response loss, concurrent collect, or independent-handle dispatch.
24. **P3 — expedition request/result types are server-local rather than shared Contracts DTOs.** This is a wire-drift risk, not a demonstrated current corruption.

### Content / generators

25. **P2 — FamilyExpandGen refusal/pool/version/provenance closure is incomplete.** `--check` is byte-stable (144 families, 370 rows, 70 refusals), but refusals do not affect the exit code; pool IDs are duplicated in `FamilyExpansion.cs:49-64`; status-anchor selection is lexicographic (`gk-forge/tools/FamilyExpandGen/Program.cs:193-196`), so `v9` outranks `v10` when both exist; output provenance lacks complete input hashes/revisions. The current scan found no duplicate family IDs.
26. **P1 — passive-tree atom vocabulary drift is not CI-gated.** `PassiveTreeRosterGen --atom-vocab-check` fails with live 9 attach points/18 kinds versus mirror 7/16, missing `Element`, `Siege`, `element.convert`, and `structure.place`; CI wires `TreeBinder --check`, not this vocabulary check.
27. **P2 — real-corpus fixtures still use stale `tier-bands.v1.json` vocabulary in Armoury/ItemCard tests.** This is a fixture-currency gap, separate from the generator's currently green byte check.

## Falsified or qualified claims

- Delve room coordinates are resolved from persisted `sectorId`; only outcome/price and party semantics remain in the confirmed scope.
- `BattleEffects.LastApplied` already records the clamped delta; the defect is the higher-level damage result/event path.
- The current FamilyExpand corpus has no duplicate family IDs in the bounded scan.
- `accept-lane.ps1` rejects malformed individual checks; the remaining acceptance gap is an entirely empty check array and optional SHA.
- Data-only nightly is documented as intentional; it is an owner decision/topology question, not automatically a missing-suite defect.
- No browser or live-game conclusion was promoted from static evidence.

## Open questions

1. Which server component owns the resolved Delve candidate, room kind, party steering, and `OfferFloor` calculation?
2. Is production deployment contractually limited to one `RpgStore` handle/server process, and is that invariant enforced rather than assumed?
3. Is expedition collect intended to be fire-and-forget after commit, or must a durable result manifest be replayable after reconnect?
4. Is `PlayerId` protected by an external live-session boundary, or must expedition routes enforce archived-save admission themselves?
5. What is the authoritative recovery contract for a cold/reconnecting web client: replay endpoint, match snapshot, or server `Join` snapshot?
6. Can multiple capture matches share the web group, and where should `matchKey` partitioning live?
7. Are empty debug binding snapshots authoritative, and what ordering guarantee exists between snapshot and spawn?
8. Should the `features/mega-merge` branch be a required CI branch, and which component owns the immutable accepted SHA?
9. Are Python tests, operational scripts, and production tools first-class verification-boundary roots or explicitly exempt?
10. Is the CI-drop injector fallback approved, and what source SHA/hash/provenance policy applies to a packaged DLL?
11. What legal game/interops environment is available for the required pre-release injector and live gate?
12. Which owner decisions are required before changing Delve party semantics, web recovery contracts, or the Data-only nightly contract?

## Recommended next plan

This order follows the falsifier's correctness-first recommendation. It is a plan, not authorization to edit.

### Phase 0 — contain false-green and economy/security paths

1. **Make merged-head verification fail closed.** Fix `post_merge_check.py` to return nonzero for build, guard, missing-summary, and test failures; require a full expected SHA; add a regression test that a RED verdict produces a nonzero process status.
2. **Bind acceptance to a reviewed artifact.** Make `-ExpectSha` and at least one schema-valid check mandatory; make the merge tool consume the acceptance artifact rather than a mutable branch tip.
3. **Close Delve caller-controlled outcome/price.** Resolve room kind, candidate, party ownership, and altar floor server-side; add route-level tests for wrong room, wrong species, wrong party, and `Price=1`; stop when no request field can substitute a server-owned value.
4. **Close battle correctness seams.** Route live derived state through ActorHub, return sink-retained damage to observers, remove the long-to-int HP narrowing, and add focused overkill/Hub/numeric tests.

### Phase 1 — recovery, persistence, and content contracts

5. **Define and implement web recovery.** Choose replay versus snapshot, add cold/reconnect/cross-match/empty-binding tests first, then hydrate/invalidate/refetch at the selected edge. Include explicit loading/error/stale states and keyboard semantics.
6. **Close expedition durability and identity.** Add post-commit fault injection, a durable collect result manifest, database-enforced active membership, archived-save admission, shared DTOs, and two-handle/concurrent tests.
7. **Close generator/vocabulary closure.** Wire the passive vocabulary check into CI, regenerate/fix the mirror through its generator, add v10/version-selection and refusal/pool/provenance fixtures, and update stale real-corpus fixtures.

### Phase 2 — topology and release proof

8. **Repair verification topology.** Map split Core areas to owner groups, add Python/operational/tool roots or explicit exemptions, make filtered tests require a nonzero executed count, and make session paths compare against the actual reviewed diff.
9. **Make release a declared CI superset.** Add omitted test/guard/content/web/E2E/Server/importer gates, require `npm ci`, and check every native packaging command explicitly.
10. **Bind injector and deploy artifacts to source/environment.** Record SHA, environment, and hash for any fallback artifact; remove machine-local defaults; refuse stale/unhealthy server launches.
11. **Run final evidence on the final SHA.** Execute the path-owned focused tests first, then the full required suite only at the large-feature/release/live boundary, followed by legal injector compilation and live/browser proof where applicable.

### Ownership and stop rules

- Delve changes belong to the Server/Data/party-dungeon owner; coordinate with active Delve session fences before editing.
- Battle changes belong to the Core/ActorHub owner; do not add a second composer.
- Web recovery requires the chosen snapshot/replay contract before implementation; no guessed parallel event source.
- Verification/release changes belong to the test-verification/CMDC owner and must update registry, workflows, guards, and tests together.
- Content changes regenerate artifacts from the generator; never hand-edit generated JSON to make a check pass.
- Stop any phase on a red result, missing executed test, unbound SHA/artifact, unknown owner decision, or unverified environment assumption; report it as open rather than GREEN.

## Evidence and limitations

- All eight retained agent verification artifacts report `pass: true`, no changed files, and no out-of-scope paths.
- All eight `audit --id` runs returned `findings: []`.
- The verification lane ran 25 CI guards with 0 red and focused Guard tests with 35/35 and 57/57 passes; those green results coexist with the confirmed false-green topology defects.
- Focused evidence included 47 seedsmith tests/subtests, a 1-test expedition E2E, FamilyExpandGen `--check`, 15 Delve tests, 14 expedition Data tests, 7 battle tests, and a 1-failing passive vocabulary check.
- No browser evidence was collected because the web worktree had no installed Node dependency tree; no live game/server probe, injector build, release build, or full suite was run because no legal game directory was available and the audit was read-only.
- The initial lanes audited earlier SHAs as the integration branch advanced; the cross-domain falsifier's final SHA `31f83afe971a199cda1617dedf9d501e919e2e7d` matches the current manager HEAD. Re-run path-owned checks if the branch advances before implementation.
- The runner's `partial` states on lanes 04, 06, 07, and 08 reflect bounded/static reports or a nonstandard `status: complete`; their report bodies and verification artifacts were retained and reviewed.

## Agent allocation rationale

Six initial domains were necessary because the repository crosses Server/Data, Core/Injector, web, generated content, and release topology; one broad agent would have repeated the mega-merge failure mode of trusting a single narrative. Two fresh follow-ups were then required: one to try to disprove inherited findings, and one to map accepted work onto real owners, hard edges, and verification boundaries. This is the recommended 6+2 shape for future deep audits of this size.
