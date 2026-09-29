# CAI-status-3 — fifty-two Project-structure markers that said "does not exist yet" about files that exist

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## What was wrong

Every combat-ai spec carries a **Project structure** table, and the one column a reader plans from is the
"new / changed" marker. **52 rows across 15 specs still said `new; does not exist yet`** — or the bold
table-cell form `**new; does not exist yet**` — about files that exist today, are imported by a test
project and pass.

`CAI-status-2` corrected the four wave-4 specs' status lines and their own markers; this is the same
defect one wave wider, including the wave-1 and wave-2 specs whose halves landed weeks earlier and whose
status lines `CAI-spec-status` had already corrected. So a reader of, say, `spec-profile-schema.md` was
told `AiVocabulary.cs`, `CombatAiProfile.cs`, `CombatAiTuningLoader.cs`, `CombatAiProfilePolicy.cs`,
`AiRowSelector.cs`, `combat-ai.v1.json` and `siege.v2.json` all do not exist — seven false claims in one
table, for a module whose status line correctly says built.

## Why not a blind flip

**A marker is not always about a file's existence.** Three sites needed judgement, and each was read:

| Site | Why the generic flip would have been wrong | What it now says |
|---|---|---|
| `spec-commander-direct-orders.md:72` | The row is about the **two additive identity fields on `DirectOrder`**, not about the file — the file exists (`CAI1.10`), the fields do not | "**the file exists** (CAI1.10); its two additive identity fields are still owed (CAI4.9)" |
| `spec-core-scorer.md:76` | The marker carried a reason ("the type moves out of `SiegeAiIntentSource.cs:316-351`") and the move is **done** — that file no longer holds it | "**landed**, CAI1.4 — the type moved out of `SiegeAiIntentSource.cs`, which no longer holds it" |
| `spec-delve-automated-wiring.md:323` | Not a marker at all: a **quotation** of `IBattleView.cs`'s own doc text ("a wiring seam for content that does not exist yet …") | **left exactly as it is** |

That third row is the reason the sweep was scripted *and then read*: a pattern match would have rewritten
a quotation of source code, making the spec misquote the file it is citing.

## The change

52 markers now read `(new — **landed**, <task>)`, each with the task that landed it, derived from the path
and confirmed against the ledger's `done` list: `CAI1.1`–`CAI1.4`, `CAI1.6`, `CAI1.8`, `CAI1.9`,
`CAI1.10`, `CAI1.12`, `CAI1.13`, `CAI1.14`, `CAI2.3`, `CAI3.1`, `CAI3.3`, `CAI3.4`, `CAI4.1`, `CAI4.4`,
`CAI4.9`. Nothing else on any line changed — the diff is 53 insertions against 53 deletions, one line
each.

**Deliberately left saying "does not exist yet"**: every marker whose path genuinely does not exist — the
Injector/Server/Contracts/web rows, `gk-core/data/tuning/lawn-perf-budget.v1.json`, `combat-ai.v2/v3.json`, and the
`DirectOrder` fields above. `grep` is the check, not prose.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| No marker on an existing path survives | a script that extracts every `does not exist yet` line naming a path that exists | **1 residual**, and it is the `IBattleView.cs` **quotation** — `spec-delve-automated-wiring.md:323` |
| The audit is not degraded by the flips | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **D1 0, D2 0, D3 0, D4 0** — unchanged. Flipping a marker removes the audit's D1 exemption for that line, so the citations on those rows are now *live claims* and they resolve |
| The diff is the flips and nothing else | `git diff --stat docs/architecture/combat-ai/` | **15 files changed, 53 insertions(+), 53 deletions(-)** |

No code, test or tuning file touched.
