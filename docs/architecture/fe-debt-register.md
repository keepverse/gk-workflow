# FE debt register

**What this is.** The tracking file for `web/**`, created 2026-09-17 by `solid-remediation` T1.3
(module `fe-debt-register`, register entry **X4**). Every module of that program appends to it **as it
runs**, and states in its commit which rows it added — or that it added none.

**Why it exists rather than a fix pass.** Owner ruling 2026-09-16:

> *"Solve the BE first. When it solid, we will make new plan to solve FE — but I don't think we really
> need, because the FE is ugly, so I want to refactor it almost completely. So we don't really do it
> now, but track it."*

So `web/**` is **out of scope for remediation and in scope for tracking**. Fixing a formula inside a
surface the owner intends to rebuild is effort spent twice. This file exists so the FE program starts
from a measurement instead of a fresh audit.

---

## What a row is

| Field | Meaning |
|---|---|
| `id` | Stable short id, referenced by the FE program |
| `what` | The debt, stated as a defect — not as a taste |
| `where` | `file:line`, or the guard that measures it |
| `blocks` | What cannot be done while this stands |
| `be-depends` | Whether anything **back-end** depends on it |

**`blocks` is load-bearing.** "The FE is ugly" is not a row: it names nothing that cannot proceed.
**`be-depends` is the column that matters to `solid-remediation`** — a row nothing back-end depends on
is genuinely deferrable, and a row something does depend on is a finding this program may have to act
on after all.

---

## Rows

| id | what | where | blocks | be-depends |
|---|---|---|---|---|
| `FE-01` | The TS sigmoid pins `steepness = 1.0` and all three scales at `100.0` as literals, while the C# side reads every one of them from `StatsTuningHub.Tuning`. The numbers agree today; the **structure** does not, so publishing `stats.v2.json` desyncs the FE silently and nothing fails | `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:122-136` vs `gk-core/src/FusionRpg.Core/Stats/Derived/CombatPolicies.cs:10-13` | any balance pass on accuracy/crit scales or steepness | **yes** — the BE owns the values and the FE will not follow them |
| `FE-02` | `web/**` has **no verification boundary** at all, so no FE path can be selected by `verify-change.py` | `gk-core/scripts/verification-boundaries.v1.json` — no `web/` path in any boundary | scoped verification of any FE change; the whole suite is the only option | no — deferred by `verification-boundaries-extend` (T1.7/T1.8), deliberately |
| `FE-03` | `hexGuard` fails: hex colour literals outside `src/theme/` | `gk-web/web/fusion-rpg-web/src/theme/hexGuard.test.ts` — 42 violations | a theme swap, and any claim that the web suite is green | no |
| `FE-04` | `disabledReasonGuard` fails: disabled controls with no accessible reason (GG-55) | `gk-web/web/fusion-rpg-web/src/ui/disabledReasonGuard.test.ts` — 19 violations | the accessibility contract GG-55 states | no |
| `FE-05` | `contractGuard` fails: files under `stages/`, `layers/` or `ui/` import REST DTO types directly | `gk-web/web/fusion-rpg-web/src/contract/contractGuard.test.ts` — 8 violations | the view-type boundary the contract layer exists to hold | no — but it is the FE half of the same layering rule the BE is being held to |
| `FE-06` | `delveViews` fails: three surfaces beyond the five the spec allows now import a `*Dto` | `gk-web/web/fusion-rpg-web/src/contract/delveViews.test.ts` — 8 files found, 5 expected | the same boundary as `FE-05`, scoped to the delve views | no |
| `FE-07` | `pendingCopyGuard` fails: dev jargon reaches player-facing pending reasons (R1b) | `gk-web/web/fusion-rpg-web/src/contract/pendingCopyGuard.test.ts` — 2 violations | player-facing copy quality | no |
| `FE-08` | The content measure is not owned in one place: `layouts/Page.tsx:20` caps document pages at `max-w-[1100px]` across 23 consumers, but rail stages each own theirs. `SanctumStage` had none and rendered 1780px wide until 2026-09-17; `DelveStage` still has none | `gk-web/web/fusion-rpg-web/src/layouts/Page.tsx:20`, `gk-web/web/fusion-rpg-web/src/stages/delve/DelveStage.tsx` | a single measure token, and the overlay WebView2 viewport where it was first seen | no |
| `FE-09` | God-TSX and page-level CSS — `LawnPage.tsx` is 1399 lines, `RelicsLayer.tsx` 679, `RpgProgressionPage.tsx` 661 | `gk-web/web/fusion-rpg-web/src/features/lawn/LawnPage.tsx` and siblings | the `gui-lego` composition model | no — owned by `gui-lego`, whose gate is `/idea-ui`, not `/idea` |

### Not rows

`LawnStage` and `WorldStage` have no measure cap **by design** — they are canvas stages and full-bleed
is correct for them. `SiegeStage` is a placeholder. Only `DelveStage` is a document stage missing the
cap, and that is `FE-08`, not four separate findings.

---

## What is a reading here

The violation counts in `FE-03` through `FE-07` are **readings taken 2026-09-17**, not constants. They
move whenever the FE changes, in either direction. Nothing asserts them, and a later measurement that
reports different numbers has not found a regression — it has taken the measurement again.

What *is* asserted is that each row names a defect, a location, what it blocks, and a back-end
dependency verdict.

---

## Module statements

| Module | Rows added | Touched `web/**`? |
|---|---|---|
| `fe-debt-register` (X4) | `FE-01`..`FE-09`, the seed measurement | no |
| `battle-responsibility-guard` (G2) | none | no |
| `verification-boundaries-extend` (G3) | none — `FE-02` already records the deferral | no |
| `elemental-resolver` (D14) | none | no |
| `battle-effect-math` (D1) | none | no |
| `retaliation-shared` (D2, D8) | none | no |
| `battle-mode-parity` (D3, D4, D5, D6) | none | no |

**No module in Phase 2 touched `web/**`**, which is the default this register exists to keep.

---

## The append rule

Every module of `solid-remediation` states which FE rows it added, and a module that touches `web/**`
at all says why — the default is that it does not. The one sanctioned exception is what
`green-baseline` needed to make a suite run at all.

**Assert the schema and the closure, never the row count.**

---

## Hand-off (`solid-remediation` T6.4, 2026-09-17)

Handed to the **FE program**. `web/**` was out of scope for remediation and in scope for tracking, which
is exactly what X4 says — so every row here is tracked, none is fixed, and that is the correct outcome
rather than an incomplete one.

`FE-01` is the row to read first: it is the **corrected** X4. The original entry was numeric; the real
defect is structural. A register that had been copied forward unchecked would still say the wrong thing.

