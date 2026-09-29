# Implementation plan: `backlog-clean-up`

**Map:** [../docs/architecture/backlog-clean-up-map.md](../docs/architecture/backlog-clean-up-map.md) ·
**Ideal:** [../docs/architecture/backlog-clean-up-ideal.md](../docs/architecture/backlog-clean-up-ideal.md) ·
**Specs:** `docs/architecture/backlog-clean-up/spec-{paperwork-reconcile,owner-decision-batch,orphan-plan-authoring,pipeline-audit-v2}.md` ·
**Tasks:** [backlog-clean-up-todo.md](backlog-clean-up-todo.md) ·
**Evidence:** [../docs/research/backlog-clean-up/](../docs/research/backlog-clean-up/README.md)

**Status:** plan approved with the map, 2026-09-20 (owner). Waves 0–1 may start.

**Relationship to `summoner-convergence`.** A sibling program, not a sub-plan. It never edits the 11
convergence programs' files, and it waits on two of their tasks: `SP6.6` and `SE4.31`–`SE4.36`. It
schedules work that several convergence documents delegate outward and that no schedule owned until
now: Θ freshness L5, `species-flavour-lawn`, `injury-tiers`, and the notify sources.

---

## Overview

The 2026-09-20 drift audit (eight agent lanes) found four things:
- the pipeline's "forgotten" work is mostly **built but unrecorded**;
- some of it is **absorbed without pointers**;
- a smaller core is **specified and never planned**;
- a pile of **owner gates** have no default.

This plan fixes the records first (`paperwork-reconcile`), so every later decision reads true state.
It then puts owner-only questions in one packet, writes the four missing plan pairs, and routes every
remaining item to exactly one owner. It builds only small, self-contained fixes directly: D17, the
clamp sites, `GearTab.tsx`, the `disabledReasonGuard` fixes, and the tool upgrade. Larger work is built
under the plans it writes.

## Architecture decisions (from the map; not re-litigated)

1. **Code beats checkboxes.** Every tick carries evidence, and every close carries a pointer (spec
   `paperwork-reconcile` rules 1–4).
2. **Convergence files are read-only here.** Cross-program needs become notes in this todo's
   "Cross-program notes" section.
3. **`SP6.6` owns the save-switch notice.** `actor-liveness-refresh` extends it (map module 4). This is
   the one collision this program must prevent.
4. **Orphan programs get plans in their own names** (`lawn`, `deployment-hierarchy`, `effect-pipeline`,
   `battle-wire-remainder`). This program's todo does not absorb their build tasks.
5. **Owner gates carry defaults.** Any "owner review" step cites an `owner-decision-batch` question id
   (D1–Dn).
6. **Repo hard rules apply unchanged:**
   - no hand-edited generated data;
   - tunables published as `v{n+1}`;
   - one ActorHub compose;
   - SOLID;
   - tests assert contracts, not populations;
   - the session boundary.

## Dependency graph

```
W0  lawn-signal-ownership (BCU0.1)          pipeline-audit-v2 (BCU0.2–0.5)
W1  paperwork-reconcile P1..P8 (BCU1.1–1.9) ─────────────┐
W2  owner-decision-batch (BCU2.1) ──► answers applied (BCU2.2)
    orphan-plan-authoring (BCU2.3–2.8)  [lawn plan also needs BCU0.1]
W3  aura-close-out (BCU3.*)  [BP1 route needs BCU2.1's D1]
    creature- / world- / item- / ui- / infra-remainders (BCU4.* … BCU8.*)   — parallel by module
```

## Suggested order and parallel lanes (suggested, not enforced)

| Lane | Tasks | Notes |
|---|---|---|
| α documents | BCU0.1 → BCU1.1–1.9 → BCU2.1 → BCU2.3–2.8 | One writer, because the paperwork batches touch many todos. Re-read session records before each batch. |
| β tool | BCU0.2–0.5 | Disjoint (`scripts/`, tests). |
| γ small fixes | BCU8.1 (D17), BCU8.2, BCU7.1, BCU7.2 | Code, but single-file and independent. BCU8.1 goes first: it is a live bug. |
| δ remainders | BCU3.* … BCU8.* | After W1. Per module, one session each. |

**Hard edges this plan honours:**
- **E1:** no lawn *build* task starts before BCU0.1 lands.
- **E2:** no second `Player`-kind notice before convergence `SP6.6` ships.
- **H7:** any tuning publish lands with its readers.
- **H1:** a golden move is one cause, one commit. W3/W17 in the battle-wire plan may move battle goldens.

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 0 | lawn-signal-ownership, pipeline-audit-v2 | BCU0.1–0.5 | S–M | yes (disjoint files) |
| 1 | paperwork-reconcile | BCU1.1–1.9 | S each | batches are sequential (one writer); parallel to wave 0 |
| 2 | owner-decision-batch, orphan-plan-authoring | BCU2.1–2.8 | S–M | 2.3–2.7 parallel; 2.8 after |
| 3 | aura-close-out, creature/world/item/ui/infra remainders | BCU3.1–8.10 | XS–M | yes, per module |

## Checkpoints (review points, not gates)

| # | Checkpoint | Evidence |
|---|---|---|
| CB1 | **Records tell the truth.** Every paperwork batch is closed or deferred with its fencing session named. `pipeline-audit-v2` reports no `todo-header-vs-boxes` rows for batch files. | audit tool output (quoted decisive line), batch commit hashes |
| CB2 | **Owner packet delivered and plans exist.** The packet reconciles against every lane's OWNER-ONLY rows, and the four plan pairs are written and agent-reviewed. `map-plan-missing` no longer lists lawn-playable, lawn-tuning-profile or deployment-hierarchy. | packet file, plan paths, reviewer verdicts |
| CB3 | **Every remainder has one owner.** Each item in map modules 5–10 is done with evidence, is a task in a named plan, or is in the owner packet with a default. | this todo's module sections |

## Cross-program edges

- `SP6.6`, `SE4.31`–`SE4.36` (convergence lane B): wait for them, never edit them (BCU0.1, lawn plan).
- `species-progression` (lane B) vs `creature-seed` Tasks 1–12: an overlap check before either builds
  (BCU4.1).
- `notification-ssot` (lane D): it closes empire-development's three silent notify sources. Verify
  through its ledger; do not re-plan (BCU5.4).
- `test-verification-boundary` (lane D): the owner of verification-boundaries' follow-ons and
  story-scene F1 web boundaries. Paperwork pointers only (BCU1.2, BCU1.7).
- `class-system` P9.0 ↔ battle-wire W16/R1–R4: one finding, linked both ways (BCU8.9).

## Tuning publishes

None owned directly. The lawn plan (BCU2.4) owns `lawn-perf-budget.v1` and `mode-profiles.v1`. The
deployment-hierarchy plan (BCU2.5) owns the next wear revision. The `battle.v5.json` `noteHybrid`
comment is fixed in the next battle publish by whoever makes it; it is never edited in place (BCU8.10).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| A paperwork tick is wrong, and hides a real gap (the first audit made four such errors) | Evidence inline on every tick; three random pointers spot-checked per batch; `pipeline-audit-v2` B2/B3 re-run at CB1 |
| Editing a file another active session is changing | Rule 5 of `paperwork-reconcile`: re-read session records before each batch; fenced files go to the deferred list |
| The lawn build duplicates `SP6.6` | Hard edge E1/E2; BCU0.1 lands the split in both documents first |
| The owner packet becomes another silent gate | Every question carries a default the work ships behind (spec `owner-decision-batch`) |

## Owner rulings (2026-09-20)

[D1–D4](../docs/architecture/backlog-clean-up/rulings-2026-09-20.md):
- R28 extends to all programs.
- The lawn combat loop stays on, and a `lawn-combat-ai` is added (BCU2.9).
- Task 17 is closed.
- The four corpus-run groups are authorized (BCU2.10–2.13), each run under its own owner charter.

The defaults below are kept only for questions not yet ruled.

## Defaults shipped behind (no gates)

- **R28 scope unanswered.** Gates outside convergence stay owner gates. Agent-reachable steps with
  precedent are listed under D1, not blocked.
- **`rider-default-on`.** Stays on. The lawn plan front-loads the budget tunable and the scale gate.
- **Model-calling runs.** None scheduled until the owner picks them (D4).
