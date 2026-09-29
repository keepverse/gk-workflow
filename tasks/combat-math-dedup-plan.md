# Implementation plan: combat-math-dedup

**Status: COMPLETE 2026-09-23** (lane `cmd-1`) — all 18 task blocks closed, the plan's Done-when list
fully ticked, and the audit §2 table annotated with every row's landing commit. Verification and the
per-line history are in `combat-math-dedup-todo.md`'s "Program close" section.

**Prior status:** ~~Plan ready for owner review.~~ — **stale, corrected 2026-09-20**
(`backlog-clean-up` `paperwork-reconcile` P5): most of Phase 1-3 (Tasks 1-6, D1-D5) already shipped
inside `solid-remediation` (2026-09-17), unreviewed and uncredited here until this pass. See
`combat-math-dedup-todo.md`'s per-task pointers. Written 2026-09-16 from
[docs/research/combat-math-dedup-audit-2026-09-16.md](../docs/research/combat-math-dedup-audit-2026-09-16.md).
**Program id:** `combat-math-dedup`
**Task list:** [combat-math-dedup-todo.md](combat-math-dedup-todo.md)
**Audit:** [docs/research/combat-math-dedup-audit-2026-09-16.md](../docs/research/combat-math-dedup-audit-2026-09-16.md)

---

## Overview

**Outcome: this program landed every reconcile-worthy duplicate the audit found** — see the status
line above and `combat-math-dedup-todo.md`'s Program close. The audit it was written from is kept as
the finding, so the framing below is past tense.

The audit found **no second damage resolver** — the shared mitigation and probability functions were
already extracted and declared once each. What remained was duplicated **assembly** (the order in
which those functions are called) and duplicated **closed vocabularies** (the same enum or id list
written out twice). Two of those duplicates had already drifted in ways that reach a real combat
number (D1, D2 — both closed).

This program reconciled them, one duplicate end to end per task, **each task shipping its own guard
in the same task**. A dedup with no guard comes back.

### Scope boundary

- **In:** formula and closed-vocabulary duplication in `src/**`, `gk-core/tools/CombatSim/**`,
  `gk-web/web/fusion-rpg-web/src/i18n/**`.
- **Out:** actor stat *composition* duplication. That is
  [actor-hub-and-combat-power-solid-fixing-plan.md](actor-hub-and-combat-power-solid-fixing-plan.md)'s
  program. The `BattleStatComposer` incident it closed on 2026-09-13 is not reopened here, and no
  task below touches `ActorHub` or any `IActorStatSubsystem`.
- **Out:** the six duplicates the audit recommends keeping (§4). They are named in the todo as
  explicit non-tasks so a later session does not "discover" them and refactor them.

### The template every task follows

The `AtomTriggers` → `EffectTriggers` reconcile done earlier this session is the shape to copy, in
both halves:

1. **Remove the duplicate outright where the assembly graph allows it** — alias, derive, or call
   through. Do not leave two declarations "kept in sync by convention".
2. **Leave a guard that fails if it returns.** Prefer the *negative* shape
   (`TriggerVocabularyTests.AtomTriggers_declares_no_string_literal_of_its_own`: "this file declares
   no literal of its own") over the *positive* shape `guard-class-system.py`'s G7 uses ("this file
   mentions a shipped symbol somewhere"). G7 is why `PhaseModel`'s hand-copied reflect formula (D3)
   passes a guard today.

### Assembly graph — this decides every reconcile shape

```
FusionRpg.Contracts  → (nothing)
FusionRpg.Core       → Contracts
FusionRpg.CheatCore  → Contracts            ← does NOT reference Core
FusionRpg.Data       → Contracts, Core, CheatCore
FusionRpg.Server     → Contracts, Core, CheatCore, Data
FusionRpg.Injector   → Core
gk-core/tools/CombatSim      → Core
gk-web/web/fusion-rpg-web   → (no assembly relationship)
```

| Situation | The fix the graph forces |
|---|---|
| Both copies in Core | Delete one. Free. |
| Contracts declares, Core mirrors | `global using` alias or `Enum.GetNames` derivation |
| CombatSim mirrors Core | Call through — the reference already exists |
| Server ↔ Injector, no shared type | Declare it in Contracts (the only assembly both see) |
| C# ↔ TypeScript | No shared implementation is possible. Parity test against the tuning JSON only |

---

## Build order

```
Phase 1 — the two that can reach a real combat number
  T1 (status category)  ──┐
  T2 (element id)       ──┴──► Checkpoint 1

Phase 2 — the estimators, worst first
  T3 (siege defense shape) ──► T4 (reflect formula) ──► Checkpoint 2

Phase 3 — finish the CombatSim migration (independent of each other after T5)
  T5 (boundary mapping + Phi) ──┬──► T6 (StrikeMixture)
                                ├──► T7 (StatusUptime)
                                └──► T8 (ActionSchedule / pool regen)  ──► Checkpoint 3

Phase 4 — closed vocabularies (fully parallel)
  T9 (DamageFxTag)  T10 (AreaShapes)  T11 (rarity ladder)
  T12 (channel families)  T13 (surface catalog literals)  T14 (inspect scope)  ──► Checkpoint 4

Phase 5 — cosmetic / cross-language
  T15 (VFX status roster)  T16 (HUD folds)  T17 (sigmoid display)  T18 (profile clamp parity)
  ──► Checkpoint 5
```

**Phase 1 is first because it is the only phase where a drift is already capable of changing a
number that reaches HP.** Phase 4 is last-but-one because every task in it is independent and
low-risk — it can be handed to parallel sessions once Phase 3 lands.

---

## Verification

Every task verifies with the path-owned command, never the full suite:

```powershell
.\scripts\verify-change.ps1 -Paths $changed -Session <active-session-id>
```

**Verification-boundary defects this program had to fix — both close 2026-09-23.**
`gk-core/scripts/verification-boundaries.v1.json` had **no entry for `gk-core/tools/CombatSim/**` or
`gk-core/tools/ProvePredictor/**`** (the only `tools/` boundaries were `ElementEnumGen`, `LawnCombatObserver`,
`ProveLiveProbe` and their test projects). Both now exist as focused owners — `tools-combat-sim` and
`tools-prove-predictor` — and `guard-verification-boundaries.py` prints OK; `verify-change --plan-only`
resolves `gk-core/tools/CombatSim/Analytic.cs` and `gk-core/tools/ProvePredictor/Program.cs` to them.

`gk-web/web/fusion-rpg-web/**` was likewise unmapped. It now has the `web-fusion-rpg-web` owner (a `script`
project running vitest then `npm run build`, added by ITEM-verify-2), which is T17's "or reports why"
branch resolved by the mapping existing rather than by a report.

The full suite (`test-fast.ps1 -AllDefault`) is run **once**, at Checkpoint 5, because by then the
program has crossed `Core` / `Injector` / `Server` / `tools` / `web` — the second of AGENTS.md's
three legitimate reasons. Not before. *(Done as five `-Project` batches because this host kills a
single ~15-minute run; every project in `$DefaultProjects` was covered, with 14 pre-existing
cross-lane reds and none this program's.)*

---

## Gates

**There are none.** Every task below is reversible, in scope, and decidable from the code. Per the
repo's own rule, a gate is only justified by an irreversible action.

Two tasks have a **decision embedded in them**, with a stated default so the task is never blocked:

- **T3** changes what the siege AI scores. Routing `IsKillingBlow` through the shipped divisive
  shape will change which targets the AI picks — that is the point, but it is a behaviour change.
  **Default if nobody objects: make the change**, since the current behaviour reproduces a defect
  the game deliberately removed (`combat-damage-ssot.md` §6.3a: 17.1% of landed hits dealt nothing
  under the subtractive shape). Named resolver: the owner. Record the before/after on a fixed
  scenario in the task body either way.
- **T17** requires deciding which of the two sigmoid display reads is correct. **Default:
  `docs/design/spec-magnitude-and-units.md` §5 decides** — it owns the read, and D.1's worked
  example is quoted in the TS file's own comment. Fix whichever side contradicts it. Named
  resolver: that document; escalate to the owner only if §5 is genuinely silent.

---

## Risks

| Risk | Mitigation |
|---|---|
| Another session owns the source tree | This program is documents-first. Before T1, run `scripts/session-boundary-check.py` and record a boundary whose `paths` fence matches the phase being built. Phase 4's tasks are individually tiny and can be fenced one at a time. |
| A dedup changes a golden | T1, T2, T9–T14 are pure declaration moves with no arithmetic change — no golden can move. T3 and T8 **do** change numbers; each records the before/after explicitly rather than re-blessing silently. |
| `StatusCategoryRegistry.Register` is additive at runtime (`ExhaustionPolicy.cs:69`, `StanceRuntime.cs:38`) | T1 seeds `Map` from the catalog and **keeps `Register`** for additive ids. The guard asserts "no hardcoded id literal in `StatusCategoryRegistry.cs`", not "the map is immutable". |
| G7's positive-presence check gives false confidence | T4 replaces G7's check for the files it covers with a negative one, and widens its file list to include `SiegeExpectedDamage.cs`, `SiegeHitChance.cs` and `ActionSchedule.cs`. |
| CombatSim is used to regenerate baselines (`scripts/regen-class-system-baselines.ps1`) | T6–T8 change what CombatSim computes only if the two copies already disagree. Each task's acceptance criterion is that the existing baselines are **unchanged**; if one moves, that is the drift the dedup just found, and it is reported, not re-blessed. |

---

## Documentation to fix in the same change

Four comments assert something the code no longer does. Each is fixed by the task that fixes its
duplicate, per the workflow rule "never leave a known-stale claim for the next session":

| Stale claim | Where | Fixed by |
|---|---|---|
| *"a reimplementation of the math here would drift from src/ … so there is deliberately none"* | `gk-core/tools/CombatSim/CombatSim.csproj:12-14` | T5 |
| *"Identical to OverlayCombatCalculator.Compute's own Omni-fallback branch (…cs:108-112)"* | `Battle/Siege/SiegeExpectedDamage.cs:33-35` | T3 |
| *"one row per catalog status"* | `Vfx/VfxCatalog.cs:85` | T15 |
| *"there is no shipped resolver to call here"* | `Balance/Analytic/ActionSchedule.cs:7-15` | T8 |

---

## Done when

- [x] Every duplicate in the audit's §2 table is either reconciled **with a guard in the same commit**,
  or listed in the todo's "deliberately kept" section with the reason.
- [x] `gk-core/scripts/guard-class-system.py` G7 is a negative check over every file it names:
  `StrikeMixture`, `PhaseModel`, `ActionSchedule`, `StatusUptime`, `Predictor`, `FirstPassage`,
  `SiegeExpectedDamage`, `SiegeHitChance` — only `Race` is excluded, because it legitimately writes the
  A&S `Math.Exp` / `1.0/(1.0 + ...)` normal CDF — plus the `gk-core/tools/CombatSim` call-through checks
  (`Analytic.Strike` calls `StrikeMixture`, `StatusModel` calls `StatusUptime`, `ActionEconomy` calls
  `ActionSchedule`).
- [x] `gk-core/tools/CombatSim/**` has a verification boundary. *(`tools-combat-sim` and `tools-prove-predictor`,
  both focused; landed before this lane and verified here.)*
- [x] The audit document's §2 table is updated with each row's landing commit. *(manager grant #1/
  final pass — all 19 reconciled rows carry a `landed <sha>` note, and §4 already holds the
  deliberately-kept reasons)*
