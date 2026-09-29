# CAI-open-1 — the wave-4 specs' Open questions that landed work has answered

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## Why

An Open question with a recommended default is a **decision deferred to a build**. Once the build lands,
the question is settled — but the spec still reads as though it were not, so a reader who follows
`DESIGN-GATE.md` §0 to the authoritative document finds a fork in the road where the program actually took
one branch. This program has already corrected its status lines (`CAI-status-2`), its citations
(`CAI-cite-1`/`CAI-cite-2`/`CAI-cite-3`) and its ideal (`CAI-ideal-status`); this closes the same gap in
the Open questions.

**Eleven questions across six specs now carry a dated answer with its evidence.** Each answer names the
task and the *observable* fact, and each question whose answer is *not* settled is explicitly left open —
so the note can never be read as "everything here is resolved".

| Spec | Q | Answer, with its evidence |
|---|---|---|
| `spec-lawn-held-actions` | 1 — does the pushed set carry unlock state? | **Yes, option (a) shipped**: the store takes no unlock-state input and pushes only the compiled list (`CAI4.2`); the rung pricing the option defers to is real (`EffectiveRungResolver`, `CAI4.4`). **3 — still open**: the D6 deploy cap has no owner task (`LW5.1`, `CAI5.3`'s precondition) |
| `spec-lawn-held-actions` | 2 — the map's dependency row is wrong | **Landed upstream**: `combat-ai-map.md:78` now reads `— *(corrected: it reads no profile)*` |
| `spec-lawn-cast-trigger` | 1 — where do the lawn keys live? | **Option (a) taken and module 2 landed** (`combat-ai.v1.json` published by `CAI1.8`, no lawn section), the revision **H7-blocked by `CAI-F1`**, and the entry condition `lawn-perf-budget.v1.json` is still absent (`LW1.1`) — so the values are constructor parameters today |
| `spec-lawn-cast-trigger` | 2 — the map row says `AdvancedEffectClock` | **Landed upstream, verified by reading both files today**: the map's row 19 names `KernelDriveHost.NowTicks / 100` with the correction, and the ideal's `:138` names it for scheduling with `AdvancedEffectClock` for status expiry |
| `spec-lawn-cast-trigger` | 3 — does the counter accumulate through the lock? | **Answered by the landing: it accumulates**, documented in the trigger's own comment, pinned by the lock test and by `CAI-loop-1`. **4 and 5 remain open** (the deploy cap; module 15's revision seam) |
| `spec-lawn-cast-activation` | 2 — the token pool must backstop a missing release | **The pool half landed** (`LawnCastTokenPool`, `CAI4.7`; composed in `CAI-loop-1`). **1 and 3 remain open** — and 1 is blocked on the same two out-of-fence files the status line names |
| `spec-lawn-cost-authority` | 1 — the lawn's unknown-id floor | **Option (a) taken and pinned**: `floorWhenUnknown` is a parameter (`CAI4.4`) with floor 0 throwing and floor 1 paying; the lawn's own call site is owed with `CAI4.5` |
| `spec-lawn-cost-authority` | 2 — `RowsFor` allocates on every `Check` | **Module 7 landed**: `CAI1.14` precomputed the rows and `DecisionAllocationTests` measures a whole round at zero bytes |
| `spec-lawn-actor-view` | 1 — does the revision seam block the default-on flip? | **Both halves in force**: the seam returns a constant (`CAI4.1`) and module 19 is not default-on (`CAI5.3` open, `DefaultEnabled = false`) |
| `spec-lawn-actor-view` | 2 — `EffectiveTier` throws outside the range | **Landed**: `CAI1.13`'s saturating clamp with a signed `saturatedBy` |
| `spec-commander-direct-orders` | 3 — no decision-origin field | **Option (a) landed**: `AiDecisionOrigin { Policy, Order, Steered }` with `AiDecisionRecord` carrying it (`CAI2.4`) |

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| Every answer is dated and names its evidence | `grep -c "ANSWERED 2026-09-22" docs/architecture/combat-ai/spec-lawn-*.md docs/architecture/combat-ai/spec-commander-direct-orders.md` | **11** across 6 files (held-actions 2, cast-activation 1, trigger 3, commander 1, cost-authority 2, actor-view 2) |
| The audit is not degraded | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **D1 0, D2 0, D3 0, D4 0** — unchanged |
| Unanswered questions are explicitly left open | read back | 5 sites say "still open" with the blocking task named (D6 cap; module 15's seam; the rider scoping; the `ChainSynthetic` producer; ST2's status line) |

No code, test or tuning file touched. One cross-program item re-confirmed while answering: the trigger
spec's question 2 was owed to **`combat-ai-map.md`/`combat-ai-ideal.md`**, and both are now correct — so
that note is closed rather than re-filed.
