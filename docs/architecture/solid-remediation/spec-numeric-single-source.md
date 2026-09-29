# spec — `numeric-single-source`

**Module 15 of `solid-remediation`.** Register entry: **X3**. Depends on `green-baseline`.

Small and independent, with no dependants.

## Objective

Pool regeneration is implemented once. Today it exists twice **with different numerics**, which is worse
than a plain duplicate: the two do not merely risk drifting, they already disagree.

## The defect (X3)

> **Pool regeneration is implemented twice with different numerics.**

Rule 2 — one mechanism, two owners. A **share** in the ideal doc's ladder.

The "different numerics" part is what makes this more than tidying: a player's pool regenerates at one
rate in one path and another rate elsewhere, and nothing reports the difference.

## Related measured evidence

The lawn-tuning work recorded a live example of how this surfaces: **M3, an unverified regen unit** —
a POC computing per 1000 ms per round against a runtime ticking per 100 ms. A regen number is meaningless
without its unit, and two implementations are two chances to get the unit wrong.

**T6 applies:** every tunable carries its unit — `Milli`, `Ms`, `PerMatch`, `PerDay`, `Permille`. The
units trap is the most expensive kind of balance bug, because `+10 hp` and `+10 fire power` read
identically.

## Shape

1. **Pick the correct implementation first, and say why.** Do not merge them or average them. One is
   right — establish which against the tuning file's stated unit before touching code.
2. **The second site calls the first.**
3. **Delete the loser** once zero readers are proved.
4. **The unit is in the name** at the surviving site.

If both turn out to be wrong, that is a finding for the resource owner, not a licence to invent a third
number here. **This program introduces no tunables.**

## Numeric

Regen is an integer magnitude; `long`, widen before multiplying, overflow throws. In integer per-mille
maths, divide by 1000 **last** so truncation happens once, and the product before it must still fit the
range.

Floating point is allowed for a rate; precision is not overflow. What is refused is an `int` magnitude
that `P(Θ)` outgrows — `int` per-mille passes its range at Θ=3,213.

## Tests to rewrite

Any test asserting the losing implementation's numbers is pinning X3. Restate to the contract: regen
resolves through the single implementation, in the unit the tuning file declares.

Assert the **unit and the contract**, not a rate value — a rate is balance and belongs to its tuning file.

## Boundaries

- **Always:** establish which implementation is correct, and record the reasoning, before deleting
- **Ask first:** publishing a corrected regen rate. That is `lawn-tuning-profile`'s or the resource
  owner's, not this program's
- **Never:** a third implementation, including a "shared helper" that re-derives the maths

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths <surviving impl> <former second site> <tests> -Session solid-remediation-<date>
```

- [ ] One implementation; the former second site calls it
- [ ] The surviving site's name carries its unit
- [ ] Zero readers proved before deletion
- [ ] Which implementation won, and why, recorded in the commit

## Success criteria

A pool regenerates at the same rate everywhere, in a unit that is stated rather than inferred.
