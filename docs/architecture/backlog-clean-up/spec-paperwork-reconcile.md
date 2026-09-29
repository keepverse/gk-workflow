# Spec: `paperwork-reconcile`

**Program:** backlog-clean-up · **Map:** [../backlog-clean-up-map.md](../backlog-clean-up-map.md) module 1 ·
**Status:** spec, 2026-09-20. Map approved 2026-09-20.
**Evidence:** every row below cites a lane report in `docs/research/backlog-clean-up/`. The lane
report names the exact lines and commits.

## Objective

Make every todo, plan header and map status line **tell the truth about the code**. Today a reader
cannot tell a finished program ("rift-gate 0/134") from an unstarted one. This module changes no code.
It closes built, superseded and obsolete rows with a pointer, so the real gaps become visible.

## Rules

1. **Tick only against evidence.** A row is ticked `[x]` only when the change can quote at least one of:
   - a commit hash;
   - a file that exists;
   - a test name;
   - a todo header or ledger entry that records completion.

   Put the evidence inline:
   `— closed 2026-09-20 by <evidence> (backlog-clean-up paperwork-reconcile)`.
2. **Close superseded or obsolete rows with a pointer, never by deleting them.** Rewrite the row as:
   - `~~<text>~~ — SUPERSEDED by <program/task/commit>`; or
   - `~~<text>~~ — OBSOLETE: <ruling/commit>`.

   The history stays readable.
3. **Merge duplicates, don't drop them.** Keep one row as the owner. Rewrite the other as
   `→ tracked at <file>:<task>`.
4. **Bulk-ticked todos.** A todo whose header already records completion (rift-gate, onboarding-rift,
   debug-mcp, game-control, story-scene T1–T26) gets one banner line under its header:
   `**All boxes below are closed by the header above** (verified 2026-09-20 …)`.

   Do not hand-tick hundreds of boxes. The banner is the pointer, and `pipeline-audit-v2` reads it.
5. **Session boundary.** Never edit a file inside the `paths` of another **active** session record.
   Re-read `tasks/sessions/*.json` before each batch. At audit time these were active:
   keepverse-split, narrative-programs-spec2, narrative-seed-idea, trade-network-idea, and convergence
   lanes A2/B/C/D/D2.

   For a file in another session's fence, append the intended fix to
   [the deferred-fix list in the todo](../../../tasks/backlog-clean-up-todo.md) instead.
6. **Convergence files are read-only here.** That covers the maps, specs, plans and todos of the 11
   programs. Any fix they need goes into a cross-program note in this program's todo.
7. **No code, no generated data.** A row whose "fix" would touch `src/`, `web/`, `tools/` or
   `gk-data/packs/fusion/data/seed/**` belongs to a remainder module, not here.

## Scope — the closed list

Each batch is one commit. The lane reports carry exact lines.

| Batch | Files | Action |
|---|---|---|
| P1 tools and infra | `tasks/rift-gate-todo.md`, `onboarding-rift-todo.md`, `debug-mcp-todo.md`, `game-control-todo.md`, `live-probe-screenshot-todo.md` (also re-point its worktree-relative links), `data-test-substrate-todo.md` (checkpoints 1/2/6/7), `phaser-kernel-todo.md:43`, `overlay-switch-todo.md:123`, `world-map-runtime-gaps-todo.md:47`, `drop-tables-todo.md` (4 leftover lines) | Rule 4 banner or evidence ticks (lanes E, F, G) |
| P2 story, achievement, commander | `tasks/story-scene-todo.md` (banner for T1–T26; F1 stale "active session" fence → SUPERSEDED by `test-verification-boundary`), `achievement-title-todo.md` (T1–T7a), `commander-surface-todo.md:253` (Playwright half) | lanes E, G |
| P3 status lines | `docs/architecture/aura-skill-map.md:21-22`, `aura-skill/spec-aura-content.md:303` (decision 5 already made), `drop-tables-map.md:3`, `world-map-program.md:3`, `tasks/world-map-todo.md:4`, the 4 trailed `actor-sheet/spec-{derived-stats,gear,locked-preview,progression}-tab.md` status lines, `gk-core/data/tuning/battle.v5.json` `noteHybrid` comment → **excluded** (tuning is published, never edited in place: route to `infra-remainders`) | lanes B1, F, G |
| P4 backlog-clear | `tasks/backlog-clear-todo.md` phases 3 (B27 → `battle-timeline-todo.md` done 2026-09-04), 4 (WM1 code), 6 (loam → `loam-todo.md` SUPERSEDED 2026-09-03), 7 (E1/E2/E3 → `combat-unification-todo.md`), 8 premise, 9 housekeeping, 10 (seedsmith → `seedsmith-todo.md` 402/402), checkpoint 1 misattribution line, the retired "git hands-off" banner | lanes B1, B2 |
| P5 absorbed audits | `tasks/battle-derived-wire-todo.md` Tasks 1, 2, 10–13, 15, 16 + header → pointers to `solid-remediation` T2.3/T2.5/T2.6/T3.1–T3.4; `tasks/combat-math-dedup-todo.md` Tasks 1–4, 6 + header → T5.1/T5.2/T2.7/T4.11–T4.13; the matching rows in `docs/research/*-audit-2026-09-16.md`. Match by **content, never by number**: solid-remediation's D-numbers are unrelated. | lane D |
| P6 creatures and species | `tasks/creature-progression-todo.md` (D0.1, D1.1, D2.1; verify D1.2), `creature-seed-todo.md` (T13 → `be3ac8a6`; GAP-1/2/3/5), `species-build-todo.md` (T4.6 bullet, both G2 boxes), `creature-corpus-self-heal-todo.md` (checkpoint C after one `creatures run status`), `creature-lawn-deploy-todo.md:34` (self-declared obsolete), `creature-standalone-todo.md` F2.3 (blocker cleared) | lanes B2, C |
| P7 misc absorbed | `tasks/actor-hub-enforcement-todo.md:34` (→ `actor-hub-and-combat-power-solid-fixing` T13), `derived-cook-todo.md:61` (→ aura-skill T1), `verification-boundaries-todo.md` follow-ons → SUPERSEDED by `test-verification-boundary`, `action-distribution-gaps-todo.md` duplicate T4.1–T4.4 block, `item-todo.md` phase 7 module 23 lines (→ `species-gear-chain` T35/T36) and D39 → OBSOLETE (`AtomKindRegistry.cs:345-355`), `empire-development-plan.md` stale overview sentence and duplicate relic ask, `loam-todo.md` checkpoint 11 → SUPERSEDED/OBSOLETE (L47–L49 retired by world-continuity Q3, `d6931e43a`), `passive-tree-repair-todo.md:588-591` stale gate premise, `gui-lego-todo.md` queue (P1 done, add P1b row, split P4) | lanes B2, C, D, F, G |
| P8 duplicates | `lawn-combat-wire` L-N26 ↔ `live-probe` Task 17; `live-probe` Task 22 ↔ `lawn-playable/spec-summon-pool-integrity.md`; `lawn-combat-wire` proof 5 ↔ L-N2; `battle-derived-wire` W16/R1–R4 ↔ `class-system` P9.0 | rule 3 (lanes A, D) |

## Acceptance

- Every row in the batches above is ticked with evidence, closed with a pointer, merged, or moved to the
  deferred-fix list with the fencing session named. None is silently skipped.
- `python gk-core/scripts/audit-program-pipeline.py` still runs. After `pipeline-audit-v2` lands, no batch file
  reports "header says complete, boxes unticked".
- `git diff --stat` for each batch touches only `tasks/**` and `docs/**`, never `src/`, `web/`, `tools/`
  or `data/`.

## Verification

Documents only, so `verify-change.ps1` selects no tests. Run `python scripts/audit-doc-citations.py`
over the touched files so new pointers do not cite dead paths. Spot-check three random pointers per
batch by opening the cited commit or file.
