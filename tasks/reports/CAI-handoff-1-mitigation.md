# `CAI-handoff-1` — the entry point's false state, mitigated where the lane can reach it

Lane `cai3` (session `combat-ai-3`), 2026-09-23. The row's own acceptance is about
`tasks/combat-ai-handoff.md`, which is **outside every combat-ai lane's fence** — so the fix stays owed and
this is what the lane could do instead.

## What was wrong, and where else it lived

`tasks/combat-ai-handoff.md` §1 reads **"Build | Not started. Nothing exists."** and names four facts that
are all false (measured by lane `cai4` on 2026-09-22, re-measured here): `gk-core/src/FusionRpg.Core/Actions/Ai/`
holds 22 files, both `gk-core/data/tuning/combat-ai.v1.json` and `.v2.json` exist,
`grep -c remove-key gk-core/tools/tuning/publish.py` is 4, and `PerfProbe.SectionCount` is 27.

**The same false claim lived in the authority document.** `tasks/combat-ai-todo.md`'s own status line read
*"written 2026-09-20. Not started. Prefix `CAI`."* — and that file **is** in this lane's fence, and is what
the row's three pointers (`combat-ai-plan.md:7`, `combat-ai-map.md:14`, `combat-ai-todo.md:6`) send a new
session to first.

## What landed

| Where | Was | Now |
|---|---|---|
| `tasks/combat-ai-todo.md` status line | *"written 2026-09-20. Not started."* | the measured state, dated: **46 done / 25 open** counted as TASK BLOCKS (never checkbox lines — a shipped task carries 6-10 permanently-unchecked acceptance boxes), waves 1-2 landed, wave 3 partly, wave 4's Core halves with their remainders named per row, wave 5 on a live probe — plus the four measured facts that replace the handoff's §1 |
| the todo's Handoff pointer | a bare link | a warning that the handoff's §1 is stale, dated, and that `CAI-handoff-1` holds it |

**The row stays OPEN on the path grant.** A warning is a mitigation, not the fix: the handoff file's own
state table still tells a new session the program does not exist, and its *"Your first task is `CAI1.1`"*
still names a row that is in the ledger's `done` set.

## Verified

| Criterion | Command | Result |
|---|---|---|
| The counts are read, not guessed | `grep -c '^- \[x\] \*\*' tasks/combat-ai-todo.md` ; `grep -c '^- \[ \] \*\*' tasks/combat-ai-todo.md` | **46** and **25** |
| The four facts that replace the handoff's §1 | `ls gk-core/src/FusionRpg.Core/Actions/Ai/*.cs \| wc -l` ; `ls data/tuning/combat-ai.*.json` ; `grep -c remove-key gk-core/tools/tuning/publish.py` ; `grep -n 'const int SectionCount' gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` | **22**; **v1 + v2**; **4**; **27** |
| The row is still present and still open | `grep -c '^- \[ \] \*\*\`CAI-handoff-1\`' tasks/combat-ai-todo.md` | **1** |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** |

## NOT proved

- **No code, so no test run.** This is a documentation-state correction in the authority document plus a
  warning at the pointer.
- **`tasks/combat-ai-handoff.md` was not edited** — it is outside this lane's allowed paths, and editing it
  would fail the run's path check rather than fix the row. Its acceptance still needs the grant.
