# T49 — the pass's instrument was incomplete; completed, and what it now shows (2026-09-22, lane sgc-4)

Row: `tasks/species-gear-chain-todo.md` T49 · spec: `docs/architecture/species-gear-chain/spec-craft-assurance.md` § Design 7

## Why the earlier "no publish" answer was not the whole story

The spec assigns the one-pass job and names what the report must compute: *"per enhance level, the expected
material cost of gambling to the next level (**success chance, downgrade risk, craft wear**) against the cost of
certainty"*. The shipped `CraftAssuranceHorizonReport` computed the success chance and the certainty cost only —
its own doc comment said so (*"a lower bound, not the true expectation: it ignores a failed attempt's own
downgrade risk"*) — so two of the four things the pass is supposed to read did not exist, and Finding 2's "no
report line speaks to wear" was a property of the instrument, not of the balance. That is now fixed.

## What was added (no shipped value changed)

| Column | Where | What it is |
|---|---|---|
| `gambleAttemptsWithDowngradeMilli` | `CraftAssuranceHorizonReport.ExpectedAttemptsWithDowngradeMilli` (new public helper) | The expectation with `EnhancePolicy.Resolve`'s own downgrade rule read from the same tuning (`band.CanDowngrade && level >= DowngradeFromLevel`, unwarded): `E = 1/p` below the floor, `E = (1 + q·E(prev))/p` at and above it. `checked`, divided last, per-mille integers. |
| `craftWearPerMilleOfMaxGambling` / `…Certainty` | `Row`/`Render` (new optional `long? craftWearPerAttemptMilli`, null = today's output) | The gamble route's `attempts × rate` and the certainty route's `rate`, in per-mille of max durability — the unit `CraftRiskPolicy.WearFor` uses. The rate only bites past potential exhaustion and is suppressed by `protect`; the doc says so. |

Contract tests (5 new, in `CraftAssuranceHorizonReportTests`): exact equality with the geometric mean below the
floor; strict inequality above it; monotone across the peril band; the wear pair scales with the rate (the
certainty column exactly, the gamble column within the documented ceil-1); no rate ⇒ no wear columns.
`gk-core/tests/FusionRpg.Core.Items.Tests` **1407 passed, 0 failed**. `verify-change` on both paths **EXIT 0**.

## What the completed report now shows (artifact: `tasks/evidence-fragments/t49-report-20260922.txt`)

| Level | naive `gambleAttemptsMilli` | with downgrade | ratio | wear (gamble / certainty, ‰ of max) |
|---|---:|---:|---:|---:|
| +14 | 1666 | 1666 | 1.0× | 84 / 50 |
| +16 | 2127 | 2127 | 1.0× | 107 / 50 |
| +17 | 2272 | **4979** | 2.2× | 249 / 50 |
| +20 | 2857 | **36837** | 12.9× | 1842 / 50 |
| +24 | 4347 | **1 949 043** | 448× | 97 453 / 50 |
| +30 | 5000 | **7 990 103 080** | 1.6 M× | 399 505 154 / 50 |

This is R-G1's **first failure mode** — *"a guarantee reachable only in theory"* — as a number, and the shipped
lower bound could not show it: from `downgradeFromLevel` upward the roll sits on the peril band's
`successEndMilli: 200` soft floor, so each level's fall-back has to be re-earned against the same 1-in-5 chance
and the expectation compounds ≈×4 per level. The wear column carries the same explosion (at +24 the gamble route
costs ~97 item-maxima of durability; the certainty route 50‰).

## The pass's decision, and the two owner calls it needs

**No value moves on this evidence**, for the same reason as before plus a better one: the spec's § Design 7 says
the report *"asserts nothing — the right ratio is a balance judgement"*, and § Tunables says *"Shipping first
values is sanctioned; calling them balance is not"*. But the completed instrument turns the pass's open question
from "which number?" into two decidable design calls:

1. **The high end is a design decision, not a tuning value.** +24 and above multiply into the millions of
   attempts; whether that is intended (the levels are beyond shipped `ilvl_cap`, so unreachable today) or a band
   shape to fix (raise `successEndMilli`, shorten `spanLevels`, or cap the open band) is the owner's call — no
   implementer can pick it, and either answer changes `enhancement.v2`.
2. **The wear price per attempt** (`craftWearPerAttemptMilli: 50`) now has a printed column on both routes, so a
   target ("certainty should cost at most N item-maxima") makes a `deployment-hierarchy.v6` publish citable. The
   publish path is proven ready (`craft-assurance` → v2, `deployment-hierarchy` → **v6**, `enhancement` → v2 via
   the nested `bands[id=…]` selector), each one command plus a one-line reader switch.

**Erratum requested (manager):** the brief's `deployment-hierarchy` **v3** cannot be published (v5 exists — that
would be a rollback) and the other two need one of the two numbers above. Absent them, the row's outcome is
"instrument completed, no publish", which is what this fragment records.
