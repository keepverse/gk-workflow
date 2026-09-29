# spec — `battle-responsibility-guard`

**Module 2 of `solid-remediation`.** Register entry: **G2**. Depends on `green-baseline`.

## Objective

Make the battle-engine responsibility register mechanical. Today nothing refuses a **second owner** of a
battle mechanism, which is why every defect this program fixes could be reintroduced the week after it
lands.

This module changes no behaviour. That is the point: it is the safest possible first production change,
and every module after it lands already protected.

## The defect (G2)

> The enforcement is **presence-shaped, not ownership-shaped.**

- `gk-core/scripts/guard-actor-hub.py` refuses a second *composer*. Nothing refuses a second *owner* of a
  mechanism.
- `gk-core/scripts/guard-class-system.py:129-150` is a **positive-presence** check — one symbol reference
  anywhere satisfies it. That is why a hand-copied reflect formula (D8) passes it today.
- It scans two filenames and never `tools/`.

A presence check answers "does this symbol appear somewhere?". The rule it is asked to enforce is "is this
mechanism owned in exactly one place?". Those are different questions, and only the second one catches a
copy.

## The law it enforces

From [../battle-engine-ssot.md](../battle-engine-ssot.md), in the owner's words:

> *"What is battle engine? A battle resolver that build on the top of atom effect engine and fsm. What is
> it do? Solve every battle logic. Any feature that change battle mechanism is an extension of battle
> engine and must be build on the top of battle engine. Every battle mode in the game share ssot battle
> engine logic."*

With the two corrections the owner made to it: **battle AI is not the battle engine** — it is player
control and an AI system, entering through `IIntentSource` — and **the engine is deterministic**.

The register's rules this guard makes mechanical:

| Rule | What the guard must refuse |
|---|---|
| 2 | A mechanism implemented twice — the same formula or decision written in two places |
| 3 | An extension that re-decides a mechanism instead of building on it |
| 4 | A mechanism one mode has and the others do not |

## Shape

**Ownership-shaped, not presence-shaped.** For each mechanism in the closed responsibility register, the
guard names the one file that owns it and refuses a second implementation elsewhere.

Design constraints, each learned from a guard in this repo that failed for the reason given:

1. **Strip comments before matching.** A guard that reads source as text cannot tell a binding from a
   sentence about a binding. `EntityFields12PlusGuardTests` passed on a commented-out write;
   `keymapGuard` failed on a comment explaining the rule it enforces. Both were fixed by stripping
   comments — do it here from the start.
2. **Skip non-source directories and survive an unreadable one.** `LadderRestatementGuardTests` was
   vetoed for a week by a `.tmp-*` directory whose ACL denied enumeration.
3. **Scan `tools/` too.** G2's own finding. `gk-core/tools/CombatSim` and `gk-core/tools/ProvePredictor` hold estimator
   code that re-decides mechanisms — that is D7 and X5.
4. **Assert the closed vocabulary, never a population.** The number of mechanisms in the register is a
   contract the code owns and a human changes — pin it and say why. The number of *call sites* is a
   reading — never pin it.

## Scope boundary

This module ships the guard and makes the **currently-passing** state pass. It does not fix D1, D2 or D8
— those are later modules. Where the guard would fail today on a defect a later module owns, the entry is
allowlisted **with the module id that will remove the allowlist**, so the allowlist is a work list rather
than a permanent exception.

An allowlist entry with no owning module id is not allowed. That is how "grandfathered debt" becomes a
template.

## Tests to write

- The guard refuses a second implementation of a registered mechanism (synthetic fixture, not a real file)
- The guard **passes** when the second occurrence is inside a comment
- The guard passes when a non-source directory is unreadable, rather than throwing
- The guard scans `tools/`
- The register's mechanism count is pinned as a closed vocabulary, with the reason stated in the test

## Boundaries

- **Always:** every allowlist entry names the module that will remove it
- **Ask first:** widening the responsibility register itself — that is a change to the law, not to its
  enforcement
- **Never:** a positive-presence check. That is the defect, not the fix

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-battle-responsibility.py <tests> -Session solid-remediation-<date>
```

- [ ] Guard green on the current tree
- [ ] Guard red on a synthetic second-owner fixture
- [ ] Guard green on a commented-out second owner
- [ ] Added to CI alongside the other boundary guards, and to `deploy-play.py`
- [ ] Every allowlist entry names its owning module

## Register

Appends to the **stub register** any mechanism in the responsibility register that has no implementation
at all — a responsibility with no owner is a different finding from one with two, and this guard is the
first thing able to see both.
