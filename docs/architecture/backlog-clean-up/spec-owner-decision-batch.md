# Spec: `owner-decision-batch`

**Program:** backlog-clean-up · **Map:** [../backlog-clean-up-map.md](../backlog-clean-up-map.md) module 2 ·
**Status:** spec, 2026-09-20. Map approved 2026-09-20. **D1–D4 answered the same day:** [rulings-2026-09-20.md](rulings-2026-09-20.md). The packet keeps only the K3 rows those answers did not cover.

## Objective

Replace about 47 scattered, silent owner gates with **one packet the owner can answer in one sitting**.
Each question states:

- the default the work ships behind if unanswered;
- the rows it releases;
- which kind of owner-only it is.

Nothing waits without a default again. That is the repo's "gates must be answerable" rule; BP1 has sat
since 2026-08-31 without one.

## Classification rule (what belongs in the packet)

A question enters the packet only if it is one of these four kinds. Anything else is agent work and
goes to a remainder module.

| Kind | Test | Examples from the audit |
|---|---|---|
| **K1 scope/authority** | Only the owner can grant it | R28 scope beyond convergence |
| **K2 model-calling run** | It spends model credit or days of machine time; R28 already excludes full corpus runs | action-distribution-gaps B0→B1; item-seedgen full corpus run; passive-tree J9/J10/J13; combat-unification F2b element-secondary (127 species); roster-balance FC3 re-run; species-build `doublecherry` re-classify |
| **K3 product/balance call** | It changes how the game feels, and no ruling covers it | `rider-default-on` scale debt; base-defense force size, `Dugout` CONCEAL rule, `Fortress` flag; relic weights, `EmpireWonderUpkeepRateMilli`; battle UI for T6/T10 (B20/B21); GG1 Checkpoint I reframe; unique pity and the other `item` §9–§11 ask-first rows; `war-feedback` promotions; `seedsmith` `bond` tree name tie |
| **K4 live visual judgement** | Human eyes on the real game or UI, *and* no in-repo precedent of an assistant running it | empire-development inventory/wonder UI reviews; actor-hud Unity eyeball; overlay-switch z-order/alt-tab/crash; shield live grant→absorb; injector-stub spot-check; story-scene visual gate; creature-standalone PT7 LIVE and F2 fusion execute; buff-debuff-scope T11; player-guide screenshots |

**Precedent test for K4.** A gate an assistant has already run under owner direction in the same
program is **not** K4. Examples: B27 live perf (`battle-timeline-todo.md`, 2026-09-04) and the world-map
playtest (`world-map-todo.md:510`). Such a gate is listed under K1 as "released if R28 extends", not as
its own question.

## The packet

The packet is `docs/research/backlog-clean-up/owner-decision-packet.md`. One table per kind, with these
columns: `# · question · default if unanswered · releases (file:task list) · evidence`. Its first rows
are fixed by this spec:

| # | Question | Default |
|---|---|---|
| D1 (K1) | Does R28's no-human-gate autonomy extend beyond the 11 convergence programs? The rulings table literally says "all programs". | **No change until answered.** Gates outside convergence stay owner gates. If "yes", the packet's K4 rows with precedent and BP1 are released to independent agent review. |
| D2 (K3) | `rider-default-on` flipped on the cost gate only. Keep the combat loop on while the scale gate (`lawn-scale-live-proof`, not built yet; the spec file does not exist yet under that name) is built, or revert to off until then? | **Keep on.** The cost is measured at 3.46% against 6%. The lawn plan puts `lawn-perf-budget.v1.json` and the scale-gate modules first. |
| D3 (K3) | live-probe Task 17 / lawn-combat-wire L-N26: close the kill→soul gap after 30+ clean reconciliations, or keep it open until a recurrence? | **Keep open** (the todo's own default). |
| D4 (K2) | Which model-calling runs to schedule, and in what order? | **None scheduled.** The list is recorded with each run's size estimate from its own todo. |
| D5 (K3) | Approve `identity-rename` / `ip-censor` plans? | Out of this program's scope. The question is listed only to point at their own plan headers. |

## Acceptance

- The packet exists. Every row cites its evidence and the exact rows it releases.
- Every K4 row states that it passed the precedent test.
- Every owner-gated row in the lane reports appears in the packet exactly once, or is reclassified as
  agent work with a reason.
- After the owner answers, each answered question is applied as a paperwork edit in the rows it
  releases, citing the answer's date.

## Verification

Reconcile the packet's release lists against the lane reports' OWNER-ONLY rows (lanes A–G). The count
of unaccounted OWNER-ONLY rows must be zero. That is a reconciliation check, not a pinned number.
