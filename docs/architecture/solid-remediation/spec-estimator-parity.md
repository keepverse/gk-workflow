# spec — `estimator-parity`

**Module 10 of `solid-remediation`.** Register entries: **D7, X5**. Depends on `battle-mode-parity`,
`verification-boundaries-extend`.

Needs a correct resolver to bind estimators to, and needs module 3's boundary to prove anything about
`tools/`.

## Objective

Estimators call the resolver's primitives, or are pinned to them by a test that fails when they drift.
An estimator that quietly disagrees with the resolver is a tool that reports confidence it has not earned.

## The defects

**D7 — `SiegeExpectedDamage` re-decides the mechanism.** It uses **subtractive** defense against a shipped
`"defenseShape": "divisive"` default, has **no base-damage term** and **no amp/crit** — while its own
comment claims it is *"identical to"* the resolver. `SiegeExpectedDamage.cs:40` vs `combat.v1.json:24`.

The comment is the dangerous part: it tells the next reader not to check. And §6.3a records that
subtractive was dropped **because 17.1% of landed hits dealt nothing** — so this estimator is running the
shape the project already measured and rejected.

Rule 3 — an extension re-deciding a mechanism.

**X5 — the analytic migration was a copy, not a move.** The original was left in place, so there are two
owners and they can drift. A copy that is never deleted is a duplicate with a migration story attached.

## Shape

**Share, not rewrite.** Two of the ideal doc's seven shares:

1. **Call the resolver's primitives** where the estimator needs a mechanism — defense shape, base damage,
   amp and crit are decisions the resolver owns.
2. **Where an estimator genuinely must approximate** (that is its job — it is an *estimator*), it is
   **pinned to the resolver by a test** that fails when the two disagree beyond a stated tolerance, with
   the tolerance and its reason written down.
3. **X5 completes the move**: delete the copy once the caller is repointed, having proved zero readers
   first. Do not delete and re-derive.

**Correct the comment in the same change.** A claim of identity that is false is worse than no comment,
and it is what let this survive.

## Numeric

Expected damage is an integer magnitude: `long`, widen before multiplying, overflow throws. An estimator
that averages must not silently truncate per-step — integer division truncates, so divide last.

Floating point is allowed here for a ratio or an expectation; precision is not overflow. What is refused
is an `int` magnitude that `P(Θ)` outgrows.

## Tests to rewrite

Any test asserting `SiegeExpectedDamage`'s current output is pinning D7 — it encodes subtractive defense
as correct. Restate to the contract: the estimator agrees with the resolver within a stated tolerance.

The parity test is the deliverable. Assert **agreement with the resolver**, not a fixed expected number,
so the test keeps working when balance moves and fails when the shapes diverge.

## Boundaries

- **Always:** state the tolerance and why, wherever the estimator approximates
- **Ask first:** changing the resolver to match the estimator. That is backwards — the resolver is the
  SSOT, and `combat.v1.json` already shipped `divisive`
- **Never:** leave a comment claiming identity that a test does not enforce

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/tools/CombatSim/** gk-core/tools/ProvePredictor/** src/**/SiegeExpectedDamage.cs <tests> -Session solid-remediation-<date>
```

- [ ] `SiegeExpectedDamage` uses the shipped defense shape, with a base-damage term and amp/crit
- [ ] A parity test fails on a synthetic divergence
- [ ] X5's copy is deleted, zero readers proved first
- [ ] The false identity comment is corrected
- [ ] `tools/` changes select real tests via module 3's boundary

## Success criteria

No estimator in the repo claims to match the resolver without a test that would notice if it stopped.
