# P1 dispatch manifest — resumed program

**Status:** staged, not dispatched. Phase 0 exact-SHA acceptance is a hard prerequisite.

At dispatch, the manager records the current integration SHA as each lane's base, creates a worktree session record with the exact paths below, spawns `opencode/space-bunny-free#max` with no fallback, and reviews the returned immutable reviewed SHA. The manager stages only the paths named here.

| Order | Lane | Program | Allowed paths | Dependency |
|---:|---|---|---|---|
| 1 | `resume-01-delve-owner` | `party-dungeon` | `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`; `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs`; three focused Delve test files | Phase 0 |
| 2 | `resume-02-battle-hub-numeric` | Core battle | four Core battle files; four focused battle test files | Phase 0 |
| 3 | `resume-03-web-recovery` | standalone/web recovery | listed Lawn/bus files; `RpgHub.cs`; `EventIngest.cs`; `gk-core/src/FusionRpg.Contracts/**`; three focused web tests | Phase 0 |
| 4 | `resume-04-expedition-durability` | standalone/expeditions | expedition endpoint/store/schema; `gk-core/src/FusionRpg.Contracts/**`; three focused expedition tests | Phase 0 |
| 5 | `resume-05-vocabulary-generator` | effect-atom/passive-tree | FamilyExpandGen/PassiveTreeRosterGen; owned generated vocabulary/atom trees; focused generator tests | Phase 0; CI wiring remains a named handoff if another lane owns the workflow |

## Dispatch controls

- All five lanes may run concurrently after Phase 0 because their post-reconciliation fences do not overlap.
- Each worker receives its persisted brief/context and leaves changes dirty for manager review; no worker commits, pushes, or merges.
- The manager records the worker's full SHA, changed paths, report, open questions, and verification output before creating an acceptance artifact.
- Acceptance artifacts use the exact eight-character lane SHA and are written only after a clean-checkout review.
- The manager merges only accepted SHAs, then runs the merged-head check at the new integration tip.
- Any generated data change must come from the owning generator and include regeneration/check output; a worker may not hand-edit emitted JSON to pass a test.
- Browser and legal live proof remain final-program gates; a focused web lane's unit/build result is not browser evidence.
