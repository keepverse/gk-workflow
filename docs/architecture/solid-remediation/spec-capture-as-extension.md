# spec — `capture-as-extension`

**Module 13 of `solid-remediation`.** Register entry: **D12**. Depends on `battle-mode-parity`.

**This module did not exist in the first draft of the map.** D12 had no owner, found by the 2026-09-17
standards review, which meant the definition of done ("every entry fixed, reassigned, or struck") was
unmeetable.

## Objective

Capture is an extension built **on top of** the battle engine, not a delve-local action that re-decides
battle mechanics beside it.

## The defect (D12)

> **Capture is built inside the Delve, not as a battle-engine extension** — the owner named it as
> *"definitely an extension of battle engine"*.

`Delve/Wild/CaptureAction.cs`, refused behind `CrossProgramLandedFlags.ItemCostRowLanded = false`.

Rule 3 — an extension re-deciding a mechanism instead of building on it. The battle-engine law is
explicit:

> *"Any feature that change battle mechanism is an extension of battle engine and must be build on the
> top of battle engine."*

## The complication, stated honestly

Capture is **refused behind a cross-program flag** today. So this module has two parts, and only one of
them is this program's:

1. **In scope — relocate the mechanism.** Capture builds on the engine's extension seam rather than
   owning battle logic inside the delve. This is a *move and re-wire*, the remedy the owner asked this
   program to prefer over delete-and-rewrite.
2. **Out of scope — finishing capture.** The `ItemCostRowLanded` flag belongs to another program. This
   module does not land it, does not flip it, and does not make capture reachable.

A module that made capture reachable would be completing a half-built feature, which is a different kind
of work with a different owner. **Relocating a mechanism and completing a feature are not the same task**,
and conflating them is how a remediation pass turns into a feature pass.

## Shape

- **Extend**, in the ideal doc's ladder: capture contributes to the engine's existing seam.
- The refusal stays a refusal. After this module, capture refuses **from the right place**.
- If relocating proves capture cannot be expressed on the current extension seam, that is a **finding**
  about the seam — record it and stop. It is not licence to widen the engine here.

## What T4.7 actually did, and the seam finding (2026-09-17)

**The move.** `CaptureAction.cs` now lives at `gk-core/src/FusionRpg.Core/Battle/Capture/`, namespace
`FusionRpg.Core.Battle.Capture`. Its test moved with it. Nothing else changed: same math, same gate, same
refusal id, same flag.

**Why the ownership was wrong rather than merely oddly-filed.** The engine already owned capture's
*randomness* — `BattleRunState.cs:284` derives the `"capture"` stream — while the mechanism that draws on
it sat under the delve. A feature whose RNG the engine seeds and whose logic another layer owns is the
split the owner's ruling names.

**⚠️ The seam finding the spec asked for.** *"If relocating proves capture cannot be expressed on the
current extension seam, that is a finding about the seam — record it and stop."*

**There is no named battle-extension seam.** A search for `IBattleExtension` / any registration interface
for engine extensions returns nothing; the engine's extension surface in practice is the **action
dispatch table**, and capture's entry in it is explicitly unbuilt — `spec-wild-room.md` §5 calls the
runner's `id → resolver` row "a one-line ask on `action-map.md`", a cross-program coordination point.

So capture could not be *routed through* a seam that does not exist as a declared contract. What was
achievable, and what this module did, is put the mechanism where an engine extension belongs, so that when
D4.8's wiring lands it builds on the engine instead of inside the delve. **Declaring that seam is a
finding, not licence to widen the engine here** — which the Boundaries forbid without recording it first.
This paragraph is that record.

**What was verified not to move**, because a "relocation" that quietly made capture reachable would be a
feature pass wearing a refactor's name:

- `CrossProgramLandedFlags.ItemCostRowLanded` is still `false` (`CrossProgramLandedFlags.cs:63`)
- `TryGate` still refuses with `capture.not-landed`
- No new reachability — capture has no dispatch entry, before or after
- `guard-battle-responsibility.py` green: 19 mechanisms, 1448 files scanned. Capture is **not** one of
  the 19, which is worth stating plainly: the guard was never going to catch this, because capture's
  battle-affecting half (the in-battle resolution) is unbuilt. D12 was found by reading the law against
  the file tree, not by a guard, and the relocation is what makes the guard's silence correct rather than
  merely lucky

## Tests to rewrite

Any test asserting capture's delve-local behaviour is pinning D12. Restate to the contract: capture
resolves through the engine's extension seam, and still refuses while its flag is false.

Assert the **contract** — the refusal reason is unchanged, the mechanism now routes through the engine.
Never assert capture's outcomes; it cannot produce any while the flag is false, and a test that seems to
is testing a fake.

## Boundaries

- **Always:** keep the refusal intact and the flag untouched
- **Ask first:** anything that makes capture reachable — that is the other program's call
- **Never:** widen the battle engine to fit capture without recording it as a finding first

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/Delve/Wild/CaptureAction.cs <engine seam> <tests> -Session solid-remediation-<date>
```

- [ ] Capture routes through the engine's extension seam
- [ ] `battle-responsibility-guard` green — no second owner of a battle mechanism in `Delve/`
- [ ] `CrossProgramLandedFlags.ItemCostRowLanded` still `false`; the refusal still refuses, with the same reason
- [ ] No new reachability

## Register

Appends to the **stub register**: capture is refused pending `ItemCostRowLanded`, with the owning program
named. That row is the hand-off.

## Success criteria

The owner's ruling holds mechanically: capture is an extension of the battle engine. Whether it *works*
is another program's question, and this spec deliberately does not answer it.
