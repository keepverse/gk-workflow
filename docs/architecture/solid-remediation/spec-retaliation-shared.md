# spec — `retaliation-shared`

**Module 7 of `solid-remediation`.** Register entries: **D2, D8**. Depends on `battle-effect-math`.

## Objective

Reflect becomes one shared mechanism instead of a lawn-local feature whose formula is written twice.

Sequenced immediately after `battle-effect-math` because it is **the same seam**: reflect needs
`ActorResolve` on the battle bag, which that module is already inside. Doing it separately would open the
same file twice.

## The defects

**D2 — reflect is lawn-only.** Four registered channel families are inert in battle, delve, siege and the
web match.

> `TryReflect` lives inside `DispatchInstant`, which battle never enters; battle's bag also never sets
> `ActorResolve`, so the `:84` guard would fail anyway. Zero occurrences of "Reflect" under `Battle/` or
> `Actions/`.

Rule 4 — a mechanism one mode has and the others do not.

**D8 — the reflect formula is written twice verbatim**, with no shared function:
`CombatDamageDispatcher.cs:113-118` (real damage) vs `PhaseModel.cs:152-157`.

Rule 2 — one mechanism, two owners. This is exactly the shape `battle-responsibility-guard` exists to
refuse, and it is why that guard had to be ownership-shaped: a hand-copied formula passes a
positive-presence check.

## Shape

**Share, then wire** — two of the ideal doc's seven shares and part of its eleven wires:

1. **Extract the formula once.** One function, one owner. The two current sites call it. This must land
   before the wiring, or the wiring propagates the duplicate into a third mode.
2. **Reach the mechanism from the shared path.** `TryReflect` is reachable only from `DispatchInstant`,
   which battle never enters; the dispatch seam is what needs to be shared, not the lawn's entry point
   copied.
3. **Set `ActorResolve` on the battle bag**, the same seam `battle-effect-math` opened.

**Do not "add reflect to battle."** That phrasing produces a second implementation. The mechanism exists;
what is missing is that battle reaches it.

## ActorHub

**Consumes** Hub output — reflect reads registered channel families and contributes no new compose. The
four inert families are already registered; this module makes them readable, it does not invent them.

## Numeric

Reflected damage is an integer magnitude: `long`, widen before multiplying, overflow throws. Reflect is a
**bounded ratio** applied to a magnitude — the ratio is per-mille and bounded, the product is not, and it
is the product that needs the range.

## Tests to rewrite

Any test asserting reflect behaviour against `PhaseModel`'s copy is pinning D8. After extraction it
asserts the **shared** function. A test that passes against either copy independently is the thing that
let them drift.

New tests assert the contract: reflect resolves identically in every mode that has an attacker and a
defender. That is a **mode-conformance** assertion — the same shape `battle-mode-parity` generalises —
and it is what stops D2 recurring.

## Boundaries

- **Always:** extract before wiring
- **Ask first:** changing the reflect formula itself. This module moves it, it does not re-derive it —
  a formula change is a balance change, and this program introduces none
- **Never:** a third copy, including a "temporary" one in battle

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Combat/<shared> gk-core/src/FusionRpg.Core/Battle/<bag> <tests> -Session solid-remediation-<date>
```

- [ ] One reflect implementation; both former sites call it
- [ ] `battle-responsibility-guard` refuses a reintroduced copy — verified with a synthetic fixture, not assumed
- [ ] Reflect resolves in battle, delve, siege and the web match
- [ ] `grep -r "Reflect" gk-core/src/FusionRpg.Core/Battle/` finds the shared call, not a formula

## Success criteria

The four registered channel families stop being inert outside the lawn, and the guard can prove the
formula has exactly one owner.
