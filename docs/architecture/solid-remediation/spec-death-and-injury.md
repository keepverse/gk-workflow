# spec — `death-and-injury`

**Module 14 of `solid-remediation`.** Register entry: **D10**. Depends on `battle-mode-parity`.

Created by the owner's 2026-09-17 ruling. D10 had no module at all until the 2026-09-17 standards review
found it, and the ruling made it a fix rather than a strike.

## Objective

Permanent death and injury become **battle-engine mechanisms**. Each mode keeps its own **ladder** —
the chance and severity curve — but the mechanism is one.

Owner, 2026-09-17:

> *"Promote it to battle engine, permanant death, injury statuses, each mode have different change and
> ladder for this injury/permanant death feature. So deploy unique actor is a cost. The delve system
> already have ladder to solve it base on delve difficult. So each game mechanism ship it own ladder. Our
> lawn use change base on damage taken. more damage taken more change to got more injury and permanant
> death."*

## The defect (D10)

> **Permanent death is delve-local.** `ExtractionSettlement` decides Retire/Recover/Roster for a delve; no
> other mode has an equivalent. `Delve/Attrition/ExtractionSettlement.cs:7,36-44`

Rule 4 — a mechanism one mode has and the others do not. Exactly the shape `battle-mode-parity` unifies,
which is why this module follows it: *"each mode ships its own ladder"* presupposes the modes agree on
the mechanism first.

## The design this implements

**Mechanism in the engine, ladder per mode.** That split is the whole ruling, and it is what stops this
becoming a per-mode reimplementation — the failure D10 already is.

| | Owned by | Example |
|---|---|---|
| **Mechanism** — what injury is, what permanent death is, how a status attaches, how an actor leaves the roster | the **battle engine**, once | `SettlementOutcome { Roster, Recover, Retire }` generalised out of the delve |
| **Ladder** — the chance and severity curve that decides *whether* it happens | **each mode**, separately | delve: keyed to delve difficulty (**already exists**). Lawn: keyed to **damage taken** — more damage taken, more chance of injury and permanent death |

**The consequence the owner named: deploying a unique actor is a cost.** That is the design intent this
module serves — risk is what makes a deployment decision matter. A mode with no ladder is a mode where
deployment is free, and that is the current lawn.

## What already exists — promotion, not construction

| Piece | Where | State |
|---|---|---|
| Settlement outcomes | `ExtractionSettlement.cs:7` — `SettlementOutcome { Roster, Recover, Retire }` | built, **delve-local** |
| Per-member decision + recovery counter | `MemberSettlement(Outcome, RecoverDelves, Won)`, `downedRecoveryDelves` | built, delve-local |
| Delve's difficulty ladder | delve risk tuning | **built — reuse, do not re-derive** |
| Injury as an ActorHub contribution | `ExpeditionInjurySubsystem`, registered at `ActorHub.cs:180` | built, **expedition-scoped** |
| Injury inputs on the battle bag | `BattleHubInputs.cs:29` — injury counts by actor key | built |

Injury is **already** an `IActorStatSubsystem` contributing through ActorHub. Promotion means generalising
its scope, not writing a new subsystem — and definitely not a second one.

## Shape

1. **Lift the mechanism out of `Delve/Attrition/`** into the engine, so `SettlementOutcome` and the
   member-settlement decision are engine vocabulary. Move and re-wire — the remedy this program prefers.
2. **Define the ladder as a per-mode input**, not a per-mode implementation. One interface, one call site;
   the delve passes its existing difficulty ladder unchanged.
3. **Give the lawn its ladder**: chance scales with **damage taken**. The owner calls this *"very simple
   to compare with delve difficult ladder"* — keep it that way. It is a mode input, not a new mechanism.
4. **Injury statuses use the status system**, not a parallel one. They are statuses; the engine already
   has a status runtime, and a second attachment path would be the defect this program exists to remove.

## ActorHub

Injury **contributes** through `ActorHub` via the existing subsystem, with its GG-49
`ContributionSourceIds` grammar id. Generalising `ExpeditionInjurySubsystem`'s scope is the correct
shape; a mode-local injury fold is not.

## Tunables — ship working values, tune after play

The ladder is made of numbers a balance pass will want to change, so they live in
`gk-core/data/tuning/<domain>.v{n}.json`, never as a `const`. That is the whole tunables rule and it applies here.

**It does not mean the module waits for balance.** An earlier draft of this spec said the lawn ladder
"cannot be shipped without numbers", required a separate tuning commit, and made the starting values an
owner decision. That was invented friction, and it contradicts both the owner and this repo's own
precedent.

Owner, 2026-09-17:

> *"Because it is tunable, so just ship with random number and we play game and tuning later. Remember we
> don't really do tuning phase in this repo yet because we still not complete the build."*

And the repo already has the idiom, named: **"default now, re-tune later"** (`action-corpus-ideal.md`
S36). `action-corpus-cost-templates.v1.json` ships with

> *"UNMEASURED placeholders, shipped per this repo's own 'default now, re-tune later' precedent — not a
> validated balance decision"*

and `contracts.v1.json`, `action-rungs.v1.json` and others carry the same
*"Working values, not a validated balance decision"* note.

**So:**

- Pick a defensible starting shape, ship it, move on. More damage taken means more chance — the curve's
  direction is the design; its constants are not.
- The tuning file's `_meta` says so in its own words: working values, unmeasured, not a validated balance
  decision, with the reasoning for the shape recorded.
- The delve's existing ladder still moves **unchanged** — that is a move, not a re-tune, and it has real
  values already.
- One commit is fine. T7's "never land a refactor and a rebalance together" is about *moving an existing
  number*; there is no prior lawn value to move, so there is no rebalance to separate. A later re-tune,
  once there is play data, is its own change and belongs to whoever owns lawn balance.

**What this program still does not do** is re-tune a number that already exists. That is the "no tunables"
rule, stated precisely.

## Numeric

Injury counts and thresholds are integer magnitudes: `long`, widen before multiplying, overflow throws.
The chance is a **bounded ratio** (per-mille, 0..1000) — comment it with its PS-8 class. No hard cap on
severity that is not derived and throwing.

## Tests to rewrite

Any test asserting permanent death is delve-only is pinning D10. Restate to the contract: the mechanism is
the engine's, and each mode supplies a ladder.

Assert the **contract**: every mode that can damage an actor resolves the same mechanism; a mode without a
ladder is a **refusal**, not a silent zero chance. A silent zero is how the lawn got here.

`SettlementOutcome` is a **closed vocabulary** — pin its three members and say why.

## Boundaries

- **Always:** one mechanism, ladders as inputs. Move the delve's ladder unchanged
- **Ask first:** nothing about the starting numbers — ship working values. Ask only before **re-tuning a number that already exists**, such as the delve ladder
- **Never:** a per-mode permanent-death implementation. Never a second injury-status attachment path

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/** gk-core/src/FusionRpg.Core/Delve/Attrition/** <tests> -Session solid-remediation-<date>
```

- [ ] The mechanism lives in the engine; the delve consumes it with its ladder unchanged
- [ ] The lawn has a ladder keyed to damage taken
- [ ] A mode with no ladder refuses rather than silently never triggering
- [ ] Injury contributes through ActorHub; `guard-actor-hub.py` green
- [ ] `battle-responsibility-guard` refuses a second implementation
- [ ] The lawn ladder ships with working values and an `_meta` note saying they are unmeasured

## Success criteria

Deploying a unique actor is a cost in every mode, not only in the delve — and the cost curve is each
mode's to set.
