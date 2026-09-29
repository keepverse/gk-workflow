# Implementation plan: `battle-wire-remainder`

**Source todos:** `tasks/battle-derived-wire-todo.md`, `tasks/combat-math-dedup-todo.md` (both closed
by pointer at `backlog-clean-up` `paperwork-reconcile` P5, BCU1.5) · **Source audits:**
`docs/research/battle-derived-wire-audit-2026-09-16.md`, `docs/research/combat-math-dedup-audit-2026-09-16.md` ·
**Tasks:** [battle-wire-remainder-todo.md](battle-wire-remainder-todo.md) ·
**Written by:** `backlog-clean-up` `orphan-plan-authoring` (BCU2.7).

**Relationship to `solid-remediation`.** `solid-remediation` (2026-09-17, 96/96 done) silently closed
6 of 18 `battle-derived-wire` gaps and 5 of 22 `combat-math-dedup` ones, without citing either plan —
confirmed and pointed at by `paperwork-reconcile` P5 (BCU1.5). This plan is the **true remainder**:
everything genuinely still open across both audits, merged into one plan because they are the same
program's own leftover findings, not two.

## Overview

Battle's damage math mostly resolves through the SSOT calculator now, but three real gaps remain in
how battle differs from the lawn (the basic attack still cannot reflect; two subsystems have an
unresolved dual-mechanism status; `progression.bonus.*` never reaches battle), plus a long tail of
smaller dedup/wiring items ranked by blast radius. Nothing here is owner-gated; every item is
agent-buildable against its own audit finding.

## Architecture decisions (from the audits; not re-litigated)

1. **W17 requires an `AppliedCombat` merge through `ActorHub.Resolve`, never `ResolveDerived` alone**
   — the one-ActorHub-compose rule's own territory; no second compose, no private fold.
2. **W4 is a decision task, not a wiring task** — `StatusDerivedSubsystem` and `BattleStatModifierLedger`
   both currently claim status→`combat.*` ownership in different modes; migrate to one, never register both.
3. **D6-D9 reuse the `gk-core/tools/CombatSim` verification boundary `solid-remediation` T1.7/T1.8 already
   added** — no second boundary registration.
4. **Match by content, never by number** — `solid-remediation`'s own internal D-numbering is a
   coincidental, unrelated scheme; every task below cites the actual defect, not a shared digit.
5. **H1 (golden re-bless order) applies to W3 and W17** — either may move battle goldens; the change
   and the re-bless land in the same commit, never split.

## Already shipped (pointers, not tasks — closed at BCU1.5)

See `battle-derived-wire-todo.md`'s and `combat-math-dedup-todo.md`'s own per-task pointers
(11 BUILT rows total: W1, W2, W5, W9-siege, W10 (7 of 9 triggers), W12; D1-D5). Not re-listed here.

## Dependency graph

```
W3 (reflect on basic-attack ApplyHp) ──► H1 golden re-bless, same commit
W4 (status→combat.* decision) ──► migrates one mechanism's callers
W8 (Draughts producer) ──► independent
W13 (ApplyHp positive-amount heals) ──► independent, narrowed scope
W14, W15 ──► independent, smallest remaining items
W17 (AppliedCombat merge) ──► H1 golden re-bless, same commit

D6 ──► D9 (shares a file, D6 lands first)
D7 (Race.Phi/Analytic.Phi, part b only — part a's boundary is already reused)
D8 ──► independent
D11/D12 (sigmoid display parity, C#/TS) ──► independent, crosses into web/**
D13,D14,D15,D16,D18,D19 ──► fully parallelizable, single-file each
D20/D21 (HUD folds) ──► independent
```

## Suggested order and parallel lanes

| Lane | Tasks | Notes |
|---|---|---|
| α real gaps | BWR1.1 (W3+H1), BWR1.2 (W4 decision), BWR1.3 (W8), BWR1.4 (W13), BWR1.5 (W14/W15 pair), BWR1.6 (W17+H1) | W3/W17 need the golden re-bless in the same commit as the change (H1) — never split. |
| β CombatSim dedup | BWR2.1 (D6) → BWR2.2 (D9) · BWR2.3 (D7 part b) · BWR2.4 (D8) | D6 before D9 (shared file); D7/D8 independent. |
| γ display parity | BWR2.5 (D11/D12) | Crosses into `web/**` — its own focused verify. |
| δ cosmetic tail | BWR3.1 (D13-D16, D18/D19 batched by file) | Fully parallelizable, good `cavecrew`/batch-session candidate per the audit's own note. |
| ε HUD folds | BWR3.2 (D20/D21) | Independent, debug-payload-only blast radius. |

**Hard edges this plan honours:**
- **H1:** BWR1.1 (W3) and BWR1.6 (W17) each re-bless any moved battle goldens in the same commit as
  the change, with the per-fixture delta recorded in the commit body — never a follow-up commit.
- **One ActorHub compose:** BWR1.6 changes `BattleHubCompose.cs:92` from `ResolveDerived` to `Resolve`
  — the merge itself, not a second fold.

## Phases

| Wave | Items | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 1 | W3, W4, W8, W13, W14, W15, W17 | BWR1.1–BWR1.6 | S–M, two carry H1 | mostly yes, W3/W17 each their own golden-move commit |
| 2 | D6, D7(b), D8, D9, D11/D12 | BWR2.1–BWR2.5 | S–M | D6→D9 sequential; rest parallel |
| 3 | D13–D16, D18/D19, D20/D21 | BWR3.1–BWR3.2 | S | fully parallel |

## Checkpoints

| # | Checkpoint | Evidence |
|---|---|---|
| BWR-C1 | **Battle's reflect and progression gaps close.** W3 and W17 each land with a re-blessed golden set and a recorded delta. | commit bodies |
| BWR-C2 | **One status→combat.* owner.** W4's decision is made and both mechanisms' callers migrated; `guard-actor-hub.ps1` proves no double-apply. | focused tests |
| BWR-C3 | **The dedup tail is closed or explicitly kept.** Every D-item in scope is either fixed or moved to the audit's own "Deliberately kept" table with its reasoning intact. | audit doc cross-check |

## Cross-program edges

- `class-system` P9.0's readiness gate — W16/R1-R4's missing-reader channel families are the identical
  set class-system's own gate reports (cross-linked at `paperwork-reconcile` P8, BCU1.8). Merged
  write-up owned by `backlog-clean-up` `infra-remainders` BCU8.9, not this plan.
- `aura-skill` T23 — owns W6/W7 (SR-14), re-homed 2026-09-20 (`backlog-clean-up` BCU3.7; T13 shipped
  2026-08-30 and does not close this gap). Not built here, not re-opened.
- `solid-enforcement` (`summoner-convergence` lane D) — the nearest owner if D6-D9/W8/W14 stall; not
  edited here.

## Tuning publishes

None owned directly by this plan's tasks — every item here is a code-shape or wiring fix, not a
balance number.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| W3/W17 move a battle golden and the commit splits the change from the re-bless | H1 named explicitly per task; the acceptance criterion requires both in one commit. |
| W4's decision is deferred indefinitely because "both work today" | Named as its own decision task (BWR1.2) with an explicit acceptance (one owner, migrated callers), not a checkbox that closes by inaction. |
| D11/D12's `web/**` half gets skipped because `verify-change.ps1` cannot select FE tests | BWR2.5 names both a C# test and a vitest explicitly, per the audit's own file list. |

## Defaults shipped behind (no gates)

- No owner gate anywhere in this plan. Every item traces to a specific audit finding with its own
  acceptance criterion; none needs a product or balance call.
