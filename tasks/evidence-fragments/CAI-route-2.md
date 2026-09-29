# CAI-route-2 — the routing section now reads what has landed

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## Why

`tasks/combat-ai-todo.md`'s **`Executor routing`** section is the manager's routing index — it exists so a
manager can size a fence without re-reading thirty rows, and it says so itself ("Grouped, so the routing
can be sized"). It was written on 2026-09-21 by lane `combat-ai-3`, **before the four wave-4 rows' Core
halves landed**, and its central claim had become false:

> one holding `gk-core/src/FusionRpg.Core/Match/**` clears **4** (`CAI4.2`, `CAI4.6`, `CAI4.7`, `CAI4.9`)

That lane is this one, and it landed all four Core halves (74 tests) plus two composition rows the routing
table never had. A manager reading the table would widen a fence to `gk-core/src/FusionRpg.Core/Match/**` expecting
to clear four rows and find the Core half of each already done — and would not learn that the remaining
halves are Injector/Contracts/Server/`web`/Diagnostics work.

## What changed (all dated, nothing rewritten silently)

| Site | Before | Now |
|---|---|---|
| the grouping sentence | `gk-core/src/FusionRpg.Core/Match/**` *clears* **4** | **cleared 4** and is now **spent** — pointing at the new status note |
| new status paragraph | — | measured 2026-09-22: that group is spent, with the per-row test counts; **no row in it is cleared by a Core/Match lane any longer**; three asks wait on a **fence** (`CAI-tests-1`, `CAI-handoff-1`); `gk-fusion/src/FusionRpg.Injector/**` is still the largest group **and claimed by no active session** |
| the four table rows (`CAI4.2`, `CAI4.6`, `CAI4.7`, `CAI4.9`) | "a lane holding `gk-core/src/FusionRpg.Core/Match/**` …" | each now says **Core half landed 2026-09-22** with its test count, and names **what actually remains** |
| the `R-CORE-MATCH` bullet | a live list of paths a lane would need | headed **DONE 2026-09-22**, with its file list kept as the record of what that fence was for |

No row's *state* changed except by the landings themselves — this is the index catching up with them, which
is why it is one commit and why every edit is dated rather than silent.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| The grouping no longer claims those four rows are still cleared by a Core/Match lane | `sed -n '/^\*\*Grouped, so the routing can be sized/,/^| \`CAI2.2\`/p' tasks/combat-ai-todo.md` | reads **cleared 4** … **spent**, then the dated status paragraph |
| Each of the four rows names its landed half and what remains | `grep -nE '^\| \`CAI4\.(2\|6\|7\|9)\`' tasks/combat-ai-todo.md` | four rows, each with the half landed, its test count and its remaining paths |
| The two new asks are routed as FENCE asks, not dependency asks | the status paragraph | `CAI-tests-1` and `CAI-handoff-1` named explicitly as fence asks |
| Nothing else in the section changed | `git diff tasks/combat-ai-todo.md` | only the grouping sentence, the new paragraph, the four rows and the one bullet |
