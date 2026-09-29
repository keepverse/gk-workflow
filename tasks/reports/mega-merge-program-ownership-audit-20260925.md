# Mega-merge program ownership audit — P1 fence collisions

**Measured:** 2026-09-24T19:14:39Z
**Decision state:** blocker for P1 implementation dispatch; no product lane was spawned from this audit.

## Question

Can the five prepared P1 containment lanes be given exact, non-overlapping path fences without editing another active session's worktree?

## Method

1. Parse every `tasks/sessions/*.json` record with `status: active` and a non-empty `paths` fence.
2. Match those fences against the exact candidate paths in the five persisted P1 briefs.
3. For every matching record, measure:
   - whether its worktree path exists;
   - `git rev-list --count features/mega-merge..<branch>`;
   - `git status --porcelain` in its worktree;
   - whether a current `.claude/cmdc-agents/agents/<session>/status.json` exists and what state it reports.

This is an ownership/readiness measurement, not an acceptance decision. A branch with zero commits ahead of `features/mega-merge` is not automatically accepted; existing acceptance artifacts and task evidence still govern that claim.

## Result

- **24 active records** overlap at least one prepared P1 fence.
- **24/24** matching worktrees exist.
- **24/24** matching branches have `ahead=0` relative to `features/mega-merge`.
- **23/24** matching worktrees are clean; `npc-story-events-1` has one dirty path and must not be touched.
- **10/24** have a current cmdc agent status directory: 3 `done`, 1 `partial`, 3 `blocked`, 3 `failed`.
- **14/24** have no current cmdc agent status directory; this is a missing live signal, not proof of abandonment.
- The records therefore block safe fence assignment even where their branch tips are already reachable from the integration branch. Retiring or re-fencing them is an ownership action, not an inference from `ahead=0`.

## Matching records

| Session | Areas | Worktree | Ahead | Dirty | Current status signal |
|---|---|---:|---:|---:|---|
| `action-dist-gaps-f4` | expedition | yes | 0 | 0 | no agent dir |
| `adg-f5` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | done |
| `bdw-1` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | blocked |
| `creature-seed-csf1` | delve, battle, expedition | yes | 0 | 0 | no agent dir |
| `creature-seed-rank` | delve, battle, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `diskw-fix` | delve, expedition | yes | 0 | 0 | partial |
| `diskw-fix2` | delve, expedition | yes | 0 | 0 | done |
| `empire-progression-4` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `identity-rename-1` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | failed |
| `ip-censor-1` | delve, battle, expedition, vocabulary | yes | 0 | 0 | blocked |
| `narrative-seed-2` | delve, battle, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `npc-story-events-1` | delve, battle, web, expedition, vocabulary | yes | 0 | 1 | blocked |
| `party-dungeon-d3` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `party-dungeon-f13` | delve, battle, expedition | yes | 0 | 0 | no agent dir |
| `passive-tree-j9-vote` | vocabulary | yes | 0 | 0 | no agent dir |
| `rpg-sim-runner` | expedition | yes | 0 | 0 | no agent dir |
| `rscf2` | delve, battle, expedition, vocabulary | yes | 0 | 0 | done |
| `species-gear-chain-4` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `species-gear-chain-5` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `species-gear-chain-6` | delve, battle, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `ssh49f2` | delve, battle, expedition, vocabulary | yes | 0 | 0 | failed |
| `strain-splice-host-20260922` | delve, battle, web, expedition, vocabulary | yes | 0 | 0 | no agent dir |
| `test-verification-boundary-2` | vocabulary | yes | 0 | 0 | no agent dir |
| `tvb58` | delve, battle, expedition, vocabulary | yes | 0 | 0 | failed |

## Owner authorization and closure result

The owner authorized evidence-based reconciliation of project-internal session records. The manager may now decide and execute work inside the repository, evidence, and test workspaces; questions are reserved for external resources or irreversible/destructive actions.

At `2026-09-24T19:19:36Z`, all 24 matching records were closed without deleting or modifying any lane worktree:

- **2 `merged`:** `empire-progression-4` and `species-gear-chain-4`, each with an exact branch-tip `GREEN` acceptance artifact.
- **22 `abandoned`:** no exact branch-tip `GREEN` artifact was retained. These records are explicitly **not** acceptance claims; their branch tips are already reachable from `features/mega-merge`, but their unverified lane state is not promoted to green.
- The dirty `npc-story-events-1` worktree was preserved untouched; its record is closed as `abandoned` with the dirty-state evidence recorded.
- Each record contains a machine-readable `closureAudit` with branch, tip, integration head, ahead count, worktree state, artifact, decision, and reason.

This closes the ownership fence; it does not retroactively certify the abandoned lanes or their program work.

## Safe next action

1. Re-run the session-boundary check and the collision audit against the updated records.
2. Keep the five P1 briefs staged, but do not spawn product implementation until the Phase 0 fail-closed pipeline lane is reviewed and accepted.
3. After Phase 0 acceptance, dispatch the P1 lanes in dependency order with their own exact fences and fresh reviewed SHAs.

## Post-closure verification

At integration SHA `011b026e2afc0d9af1459527fc184aa333cb6ad8`:

- `scripts/session-boundary-check.py --session mega-merge-program-resume-20260925` returned `clean`.
- The repeated P1 collision audit returned `active_p1_collision_records= 0`.

The previous duplicate-work/drift blocker is therefore closed for P1 dispatch. This does not make the Phase 0 pipeline gate green; the fail-closed merge lane still requires exact-SHA review.
