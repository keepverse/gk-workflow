# Implementation Plan: battle-derived-wire

**Source audit:** [docs/research/battle-derived-wire-audit-2026-09-16.md](../docs/research/battle-derived-wire-audit-2026-09-16.md)
**Task list:** [tasks/battle-derived-wire-todo.md](battle-derived-wire-todo.md)
**Status:** ~~plan drafted 2026-09-16, unbuilt. No source was edited to produce it.~~ — **stale,
corrected 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P5): roughly a third of this plan
shipped inside `solid-remediation` (2026-09-17), unreviewed and uncredited here until this pass. See
`battle-derived-wire-todo.md`'s per-task pointers for exactly which.

---

## Overview

The audit found that "one battle engine for every mode" is **architecturally true and operationally
half-wired**. Battle already composes through `ActorHub`, already applies through
`DamageApplyPipeline` + `ShieldGate`, and already resolves its basic attack through
`OverlayCombatCalculator`. What is missing is a set of **null delegates, unset properties, unregistered
subsystems and absent fire sites** that make most of the RPG's vocabulary inert on the battle side of
the same machinery.

This program closes those, in order of player-visible impact per unit of risk. It adds **no new
composer, no new resolver, no new ledger**. Every task either (a) installs an already-shipped component
on a host that does not currently install it, or (b) supplies an argument to a call that already
accepts one.

**If only one task is done, do W1 (Task 1).** It is the single change that makes the most of the
existing stat vocabulary start mattering in battle: today every damage-over-time tick, every on-hit
rider and every atom-granted damage effect in a battle ignores accuracy, dodge, crit, elements,
penetration, absorption, amplification, reduction, parry and block — twenty families, on a code path
that already exists and already runs.

---

## Architecture decisions

1. **Contribute, never fork.** Every stat remedy registers an existing `IActorStatSubsystem` on
   `BattleHubCompose`'s hub, or supplies an existing `BattleHubInputs` field. No task introduces a
   second composer, a private fold, or a mode-local stat surface (CLAUDE.md "One ActorHub compose / one
   read"; DESIGN-GATE §2.15).
2. **Reversible defaults, not gates.** Each behaviour change lands behind a value on an existing
   policy/tuning surface where one exists, defaulting to the shipped behaviour for the task that
   introduces it and flipped on in the same phase once its goldens are re-blessed. That is the
   mechanism the repo already uses for `CombatPolicy.ReflectReadsPostShield`
   (`combat-damage-ssot.md` §6.7a) — not a new pattern.
3. **Goldens will move, and that is the deliverable, not a blocker.** Making twenty stat families
   start affecting battle damage changes battle outcomes by definition. Every task that can move a
   golden says so in its acceptance criteria and re-blesses in the same task, with the before/after
   delta recorded. DESIGN-GATE §3 rule 4 applies: nobody should escalate "this moves goldens" without
   having run the suite.
4. **Assert the contract, never the population.** No task may add an assertion pinning a channel count,
   a family count, or a trigger count as a *reading*. The closed vocabularies (13 triggers, 28 combat
   families, 5 `ActionCategory`) may be pinned and must say why (CLAUDE.md guardrail rule).
5. **Audit-first where the blast radius is unknown.** Task 1 is preceded by a measurement task, because
   the audit could not quantify how much shipped battle content carries a typed `ElementPayload`
   (audit §8 item 2). The measurement is a test, not a meeting.
6. **W4/W5 carry an owner reading, not a gate.** `BattleHubCompose.cs:15-17` asserts the omission of
   progression and status subsystems was deliberate; the audit could not find a decision row that
   ratifies it as an end state. Those two tasks therefore land **default-off** and are flipped by a
   named tuning value once the owner reads the delta. **Resolver:** the owner. **Default if unanswered:**
   ship off, keep the delta report, and let every other phase proceed — nothing else depends on them.

## Explicit non-goals

- The four **real gaps** (`status.expose.*`, `resource.efficiency.*`, non-hp `resource.restore.*`,
  `progression.xpRate`/`breakthroughSuccess`) are out of scope. They need consumer subsystems that do
  not exist; they are not wiring.
- Re-litigating the battle plan-item allowlist (`BattleEffects.cs:225`). It is narrow **and correct**;
  widening it is a separate reviewed change per DESIGN-GATE's Battle row.
- Touching `OverlayCombatCalculator`'s math. Every task consumes the resolver; none edits it.

---

## Dependency graph

```
Phase 0  B0 measure -------------------------------┐
                                                   v
Phase 1  T1 CombatMath in battle  ->  T2 ActorResolve + reflect  ->  T3 heal term
                                                   |
Phase 2  T4 ActiveAuras producer  ->  T5 AddDerivedContribution producer
         T6 status defense read (independent)
                                                   |
Phase 3  T7 delve HubInputs  ->  T8 siege HubInputs  ->  T9 Draughts producer
                                                   |
Phase 4  T10 OnDamageTaken/OnDeath  ->  T11 OnSpawn  ->  T12 OnTimer
         T13 OnMatchStart/OnMatchEnd/OnWave
                                                   |
Phase 5  T14 StatusDerivedSubsystem (default-off)
         T15 RpgProgressionSubsystem (default-off)
                                                   |
Phase 6  T16 per-element parry/block/reflect readers
         T17 turn.moveSpeed registration
         T18 loadout.slots feed
```

---

## Phase ordering rationale — player-visible impact per unit of risk

| Phase | Player-visible effect | Risk | Why here |
|---|---|---|---|
| **1** | Every DoT, rider and atom damage effect in battle starts respecting the whole combat stack; thorns builds start working in battle | high golden movement, **zero new code paths** — the components already exist and already run on the lawn | Biggest payoff per line changed. One unset property each. |
| **2** | Auras and mid-battle buffs become real in battle instead of dead seams | low — the recompose is already idempotent and already runs every round | Makes a whole designed mechanism live; nothing downstream depends on it |
| **3** | A specimen's gear and aptitude finally matter in the Delve and in siege, not only in web match | medium — changes the numbers delve/siege content was tuned against | High player-visible impact, but it moves content balance, so it follows the combat fix |
| **4** | Atom content authored for `OnDamageTaken`/`OnDeath`/`OnSpawn` starts firing in battle | medium — new fire sites can proc content that was never exercised there | Content-gated: the value only appears once content names these triggers |
| **5** | Live statuses and progression enter battle's composed stats | medium, **and carries an unresolved owner reading** | Deliberately last among the stat work: default-off, no downstream dependency |
| **6** | Element-typed avoidance; two dead channels | low | Cleanup; no player asked for it |

---

## Verification

Every task verifies with the repo's path-owned command, never the full suite
(AGENTS.md "Verification boundary"):

```powershell
.\scripts\verify-change.ps1 -Paths $changed -Session battle-derived-wire-20260916
```

The full suite (`.\scripts\test-fast.ps1 -AllDefault`) runs at exactly three points, matching
AGENTS.md's three sanctioned cases: **Checkpoint 1** (a change crossing Core/Server boundaries),
**Checkpoint 3** (same), and **Checkpoint 6** (finishing the program). Guards to run alongside any
task touching Core or the injector:

```powershell
.\scripts\guard-actor-hub.ps1
.\scripts\guard-funnel-delta.ps1
.\scripts\guard-single-writer.ps1
```

---

## Risks

| Risk | Handling |
|---|---|
| Phase 1 moves every battle golden | Expected. T1 re-blesses in the same task and records the before/after damage delta per fixture. `RulesetVersion` (`BattleModels.cs:95`) is bumped **once**, in T1, not per task. |
| Phase 3 makes delve/siege encounters measurably harder for the player and easier for the player's own squad | T7/T8 each report a win-rate delta over the existing encounter fixtures before the task closes. If the delta is out of band, the fix is content tuning in `gk-core/data/tuning/**`, published as `v{n+1}` — never a code clamp. |
| Phase 4 fire sites proc content that was authored and never exercised | Each trigger task first enumerates which shipped atoms name that trigger, and records the count. A trigger with zero authored content lands as a pure seam with a test and no behaviour change. |
| Two ledgers writing `combat.defense.omni` (audit §4.1) | T6 closes it explicitly: the status-sourced defense mod must route through the **same** push the `stat.modify` executor uses, never a second one. |
| Concurrent session owns the source tree | This plan is a document. Nothing here is started until the owner assigns `paths` and a session record exists (`/session-start`). |
