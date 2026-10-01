# Spec: `orphan-plan-authoring`

**Program:** backlog-clean-up · **Map:** [../backlog-clean-up-map.md](../backlog-clean-up-map.md) module 3 ·
**Status:** spec, 2026-09-20. Map approved 2026-09-20.

## Objective

Four bodies of specified work have no plan, so nothing can schedule them (cause C1/C3). This module
writes each one a plan pair, **in the owning program's name**, following the template in
`tasks/summoner-convergence-plan.md` (Appendix). After that, each program is built through its own
plan like any other. This module plans; it does not build.

## The four plans

| Plan pair to write | Built from | Must record as already shipped (pointers, not tasks) | Must plan |
|---|---|---|---|
| `tasks/lawn-plan.md` / `-todo.md`, program id `lawn` (one plan over `lawn-playable` + `lawn-tuning-profile`, which share a surface and a cross-gate) | `lawn-playable-map.md` + 6 specs, `lawn-tuning-profile-map.md` + 7 specs | `DefaultEnabled = true` (`9f985313`); `hub-snapshot-cache` / `rider-hit-cost` superseded by `83054adb`, `5a3e941c`, `b48f0e7e`; the attack write removed (`2b9fb2c2`, which narrows `base-relative-read` to hp/armour) | See the lawn plan contents list below |
| `tasks/deployment-hierarchy-plan.md` / `-todo.md` (the paths its map already names) | `deployment-hierarchy-map.md` + 7 specs | Modules 3–6 built by `empire-development` (`1b6fd8de`, `29459f9e`, `RpgStore.CacheRetrieval.cs`); module 7 workbench slice (`species-gear-chain` T10/T11/T23/T24) | `deploy-carry` production wiring (`CarryInPools` has zero assignments today); `injury-tiers` in full, which lets `empire-progression`'s documented fallback be dropped *by that program*; module 7 §3 battle wear (no blocker), D4 field touch-up (after `party-dungeon` `PackGrid`), D6 commander pouch |
| `tasks/effect-pipeline-plan.md` / `-todo.md` | `effect-pipeline-map.md` + 12 specs (written 2026-09-02/03) | Whatever the map records as built (verify per module; trap 1: spec names ≠ code names) | The modules that `passive-tree-repair` P10/P12 and the `AffixComposer` channel-pool defect (module 2) wait on, first |
| `tasks/battle-wire-remainder-plan.md` / `-todo.md` | `tasks/battle-derived-wire-*`, `tasks/combat-math-dedup-*`, both 2026-09-16 audits, lane D | Everything `solid-remediation` closed (see `paperwork-reconcile` P5) | W3 (reflect on the basic-attack `ApplyHp` path); W4 as a **decision task**: one owner of status → `combat.*` (`StatusDerivedSubsystem` vs `BattleStatModifierLedger`), never both; W8 `Draughts` producer; W13 narrowed to the positive-amount `ApplyHp` path; W14, W15; W17 `BattleHubCompose` → `Resolve` (AppliedCombat merge); D6–D9 (reuse the `gk-core/tools/CombatSim` verification boundary that `solid-remediation` T1.7/T1.8 already added); D11/D12; D13–D16, D18–D21. D17 and D22 are **not** here; they are in `infra-remainders`. |

**Lawn plan contents** (order from the maps):
- `lawn-perf-budget.v1.json` (new; does not exist yet) as a tunable, so the ceiling stops living in a commit message;
- `summon-pool-integrity` (closes live-probe Task 22);
- `exhaustion-event`;
- `actor-liveness-refresh`, **after `lawn-signal-ownership`**, extending `SP6.6` (closes live-probe
  Tasks 23/24/25);
- `regen-unit-trace` and `mode-profile` (no dependencies);
- `base-relative-read` (hp/armour only);
- `lawn-combat-baseline` and `zombie-power-source`: **write their specs first**, and narrow
  `zombie-power-source` to wiring, since `ZombossCommanderAllocation` exists;
- `lawn-resource-scale`, then `basic-attack-cost-scale` and `species-flavour-lawn`;
- `lawn-scale-live-proof`, which closes `lawn-combat-wire` proof 5 / L-N2.

## Rules

1. **Plan only what the lanes found open.** Anything the lanes marked BUILT or SUPERSEDED appears as a
   pointer in the plan's "already shipped" section, never as a task.
2. **Task format** is the parent template:
   ```
   - [ ] **<PREFIX><wave>.<n> — <title>** · <XS|S|M|L> · deps · *(spec: <module-id>)*
   ```
   Each task has acceptance, `verify-change.py` verification and ≤5 files. No L+ task. Prefixes:
   `LW` lawn, `DH` deployment-hierarchy, `EPL` effect-pipeline, `BWR` battle-wire-remainder.
3. **Cross-program edges** use `<prefix><id>`. Examples: `SP6.6` (lawn), `SE4.31`–`SE4.36` (lawn),
   `class-system P9.0` (battle-wire readers), `party-dungeon PackGrid` (deployment-hierarchy D4).
4. **Hard edges are named, not re-invented.**
   - A tuning publish lands with its readers (H7): `lawn-perf-budget`, `mode-profiles`,
     `deployment-hierarchy` wear.
   - A golden move lands with its one cause (H1): W17 and W3 may move battle goldens.
   - `BattleHubCompose` changes obey the one-ActorHub-compose rule. No second compose, no private fold.
5. **The program's map gets updated in the same commit as its plan.** The status line names the plan,
   so `map-plan-missing` stops firing for it.
6. **Owner-gated steps** in these plans cite the `owner-decision-batch` question that governs them, with
   its default. They never use a bare "owner review".

## Acceptance

- Four plan pairs exist, each with its map status updated.
- `python gk-core/scripts/audit-program-pipeline.py --only map-plan-missing` no longer lists
  `lawn-playable`, `lawn-tuning-profile` or `deployment-hierarchy`. `effect-pipeline` has a plan.
- No task in the four plans duplicates a row that `paperwork-reconcile` closed. Check by grepping each
  plan's task titles against the lane reports' BUILT and SUPERSEDED rows.
- The two new lawn specs exist under `docs/architecture/lawn-tuning-profile/` and pass the DESIGN-GATE
  §5 checklist.

## Verification

Documents only. Run `python gk-core/scripts/audit-program-pipeline.py` and
`python scripts/audit-doc-citations.py` on the new files. An independent agent reviews each plan
against its map and the lane report, from a fresh context, before the plan's status reads approved.
