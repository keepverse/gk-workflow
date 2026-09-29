# CAI-status-2 — the four wave-4 specs' status lines after the Core halves landed

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## Why this is a task and not tidying

`DESIGN-GATE.md` §0 sends every reader to a subsystem's authoritative documents first, and a spec's own
**`Status:` line is the first line of that document**. This program has already run this propagation twice
(`CAI-spec-status` corrected twelve status lines; `CAI-ideal-status` corrected the ideal's rows) because a
status line is what a reader trusts before reading anything else.

All four wave-4 specs still read **"Status: spec, 2026-09-20. Not built."** after the Core halves of those
four modules landed, were tested and were proven to compose — and their Project-structure tables still
marked **"new; does not exist yet"** on files that exist, are imported by a test project and pass.

## What changed

| Spec | Status line now says | File rows re-marked |
|---|---|---|
| `spec-lawn-held-actions.md` | part built (Core half, CAI4.2) | `Match/Ai/LawnHeldActionSets.cs` → landed; the test row repointed to its real path |
| `spec-lawn-cast-activation.md` | part built (pure half, CAI4.6) | `Match/Ai/LawnCastPlan.cs` → landed; test row repointed |
| `spec-lawn-cast-trigger.md` | part built (Core half, CAI4.7) | the three `Match/Ai/Lawn*` files → landed; test row repointed; `combat-ai.v1.json` → **published by CAI1.8** (three separate stale mentions, `:56`, `:288` and the table row) |
| `spec-commander-direct-orders.md` | part built (Core half, CAI4.9) | `Match/Ai/{LawnOrderQueue,DirectOrderAdmission}.cs` → landed; test row repointed; `combat-ai.v1.json` → published by CAI1.8 (two mentions) |

Each new status line names **what is owed and who owes it** (`CAI4.3`'s ptr registry; the Contracts
`CastOrigin` field and the injector fire site; `PerfProbe`/`CAI4.8`/the H7-blocked tuning revision; the two
`DirectOrder` identity fields, the router hook, the Server endpoint, the injector host and `web/**`), so the
correction cannot be read as an overclaim. Each also names **where the tests actually live** — the rows'
own `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside this lane's fence, which is `CAI-tests-1`.

Two further stale claims were corrected in the same pass: `spec-lawn-cast-trigger.md` and
`spec-commander-direct-orders.md` both said `gk-core/data/tuning/combat-ai.v1.json` "does not exist yet" — CAI1.8
published it on 2026-09-20. Measured: its top-level keys are `schemaVersion`, `version`, `_meta`,
`profiles`, `router`, **and it has no `lawn` section** — which is exactly the owed revision H7 blocks
until `CAI-F1` lands.

Each spec's design-gate checklist line that cited the audit's "(new; does not exist yet)" exemption now
carries a dated parenthetical saying which markers that exemption still applies to, because after this
change it no longer applies to the files that landed.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| No wave-4 spec still reads "Not built" | `grep -c "Not built" docs/architecture/combat-ai/spec-lawn-{held-actions,cast-activation,cast-trigger}.md docs/architecture/combat-ai/spec-commander-direct-orders.md` | **0, 0, 0, 0** |
| Every remaining "does not exist yet" marker is on an owed, out-of-fence path | `grep -n "does not exist yet"` on the same four | the injector/server/contracts rows, `gk-core/data/tuning/lawn-perf-budget.v1.json` (absent), and `DirectOrder.cs`'s owed fields — nothing else |
| The audit is not made worse by the repointed citations | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **D1 0, D2 0, D3 0, D4 0** — unchanged, and the new test paths resolve |

No code, no test and no tuning file was touched by this row: it is a documentation-propagation change,
which is why it is its own commit rather than riding a code commit.
