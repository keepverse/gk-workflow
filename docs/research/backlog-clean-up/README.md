# Drift audit evidence — `backlog-clean-up` (2026-09-20)

Eight read-only audit lanes checked every open item that was specified or planned outside
`summoner-convergence`, against the code, git history, session records and ledgers.

- **Charter:** Claude Code native agents, Sonnet only, no token cap. About 1.89M tokens across the
  eight lanes.
- **Starting point:** [../../architecture/program-pipeline-audit-2026-09-20.md](../../architecture/program-pipeline-audit-2026-09-20.md).
- **Where it leads:** [../../architecture/backlog-clean-up-map.md](../../architecture/backlog-clean-up-map.md).

Each lane file is evidence. Its rows cite `file:line` and commits, and name one of seven verdicts:
BUILT, PARTIAL, NOT-BUILT, SUPERSEDED, OBSOLETE, OWNER-ONLY or UNKNOWN. The row counts are what each
lane found on 2026-09-20. They are readings, not a contract.

| Lane | File | Scope |
|---|---|---|
| A | [lane-A-lawn.md](lane-A-lawn.md) | `lawn-playable`, `lawn-tuning-profile`, open `lawn-combat-wire` / `live-probe` items |
| B1 | [lane-B1-backlog-clear.md](lane-B1-backlog-clear.md) | `backlog-clear` phases 1–9, `aura-skill` reconciliation |
| B2 | [lane-B2-seedsmith-content.md](lane-B2-seedsmith-content.md) | `backlog-clear` phase 10, seedsmith todos, `action-distribution-gaps`, `roster-balance`, `passive-tree(-repair)`, `creature-seed` |
| C | [lane-C-deployment-creatures.md](lane-C-deployment-creatures.md) | `deployment-hierarchy`, `creature-progression`, `creature-lawn-deploy`, `creature-standalone`, `species-build`, the empire-development family |
| D | [lane-D-combat.md](lane-D-combat.md) | `battle-derived-wire`, `combat-math-dedup` vs `solid-remediation`, class-system / derived-cook / buff-debuff-scope / actor-hub-enforcement leftovers |
| E | [lane-E-stale-todos.md](lane-E-stale-todos.md) | rift-gate, onboarding-rift, debug-mcp, game-control, live-probe-screenshot, achievement-title, story-scene, first-session-progression, player-guide, keepverse-split, identity-rename, ip-censor, data-test-substrate, verification-boundaries, war-feedback, worktree-23-failures |
| F | [lane-F-world-empire.md](lane-F-world-empire.md) | base-defense, loam, empire-development, party-dungeon, the world-map family, drop-tables |
| G | [lane-G-ui-item.md](lane-G-ui-item.md) | game-gui, actor-hud, actor-sheet, gui-lego, shield-sheet, aptitude-sheet and other single-item UI todos; `item`, `item-content`, `item-seedgen` |

## What the lanes established (cross-lane)

1. **Most "stalled" work is built.** The completion is recorded in a todo header, a ledger, a merged
   session or a commit, and the boxes were never ticked. Programs where this was confirmed include:
   - rift-gate, onboarding-rift, debug-mcp, game-control, live-probe-screenshot;
   - story-scene (T1–T26), data-test-substrate, worktree-23-failures, the whole seedsmith family;
   - aura-skill (78/78), phaser-kernel, drop-tables;
   - four `deployment-hierarchy` modules (built by `empire-development`);
   - most of `creature-progression`, and `creature-seed` Task 13 (built by convergence lane C).
2. **Later programs absorbed earlier work without a pointer.**
   - `solid-remediation` closed six of `battle-derived-wire`'s gaps (W1, W2, W5, W9-siege, W10, W12)
     and `combat-math-dedup` D1–D5.
   - `species-gear-chain` T35/T36 built item module 23.
   - `party-dungeon` wired battle-timeline's session registry (B22).
   - The perf pass `83054adb` / `5a3e941c` / `b48f0e7e` superseded `lawn-playable`'s `hub-snapshot-cache`
     and `rider-hit-cost`.
3. **Two claims in the first audit were wrong** and are corrected there:
   - `LawnBasicAttackFeature.DefaultEnabled` is **`true`** (`9f985313`, 2026-09-16), not false.
   - The six `roster-balance` specs already carry a `⛔ SUPERSEDED 2026-09-06` banner.
4. **Specified but never planned** (cause C1):
   - `lawn-playable` (4 live modules) and `lawn-tuning-profile` (all 9 modules);
   - `effect-pipeline` (12 specs, no plan pair);
   - the remainder of `deployment-hierarchy`: `deploy-carry` wiring, `injury-tiers`, module 7 §3/D4/D6;
   - the two absorbed audits' true remainder.
5. **A live defect nobody owns.** `combat-math-dedup` D17: `VfxCatalog.cs` has no rows for
   `nerve.unsettled`, `nerve.shaken` or `nerve.afflicted`.
6. **A shipped switch that skipped half its gate.** `rider-default-on` flipped on the cost gate. The
   scale gate (`lawn-scale-live-proof`, M2 stamina) never ran, and the perf ceiling is still prose, not
   a tunable.
7. **One gap seen twice.** The missing-reader channel families (`resource.efficiency.*`,
   `skill.cooldown/effectiveness.*`, `progression.xpRate/breakthroughSuccess`, `move.range`) appear in
   both `battle-derived-wire` W16/R1–R4 and `class-system` P9.0.
8. **Owner decisions pile up behind one ambiguity.** R28's table says "all programs", while the plan
   reads it as convergence-only. About 47 owner-gated rows sit outside convergence. Many are
   agent-reachable under existing precedent: B27 and WM1 were both run by an assistant before.
