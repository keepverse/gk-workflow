# Lane brief — `findings-1` (close the three findings that have no owner)

## What this lane is for

Three findings were surfaced during the summoner-convergence and backlog work and **all three are still open**.
Each is small on its own; together they are one lane. Your job is to close them, or to end the segment saying
precisely what each now waits on.

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its row names for
these subsystems, **in this session**, then verify every claim against code. A comment is not evidence; code beats
docs; docs beat comments.

## The three rows

### F14 — F13's fix has no committed regression test

F13 was a real production defect: the `dungeon_domain` table was missing the `first_clear_ref` column, and the fix
registers it through `EnsureColumn` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs`). The lane that fixed it had
`tests/**` outside its fence, so **the fix ships unguarded** — the next person to touch that schema gets no signal.

Deliverable: a committed regression test that **fails if the column is absent** — boot a store through the real
schema path and assert the column exists (and that a read/write against it works). It must be a test of the
*contract* (the column is part of the schema), not of a literal count of columns.

### KS-F2 — nothing forbids a private repo-root walk in a test

`CS-F1` was a **fixture defect**: `SpeciesModLedgerTests` walked the tree privately with `..\..\..`, which passed in
a worktree and failed in the main checkout. It was fixed to use `FusionRpg.TestSupport.ContentRoot.Path`, but
**nothing stops the next test from hand-rolling the same walk** — `Directory.Build.props` compiles the shared
resolver into every `*.Tests` project and no guard or analyzer refuses the private form.

Deliverable: an enforced refusal of a hand-rolled repo-root walk inside `tests/**` — a guard script under
`scripts/` (wired the way the other guards are, see `scripts/run-guards.ps1` and its tier list) **plus** a case in
`gk-core/tests/FusionRpg.Guard.Tests` that proves the rule bites on a planted violation. A guard without a
planted-violation case is not a guard — this repo has already paid for that lesson.

### KS-F1 — the production boot's seed-tree discovery has no Keepverse content-root awareness

`CS-F1-a`. The *test* now resolves content through `FusionRpg.TestSupport.ContentRoot.Path`, but the **boot's own
discovery** still has no notion of the Keepverse content root — so a real boot in the split world has nothing to
consult. This one is a production-code row, not a test row.

Deliverable: give the boot's discovery the same content-root awareness the test resolver has, or — if the honest
answer is that the boot cannot own it — end the row with the question sharpened and the alternative named. Do not
invent a second content-root concept; find the one that exists and make the boot consult it.

## Fence (your session paths)

- `tests/**` — all test projects
- `scripts/**` — guards and their wiring (including `run-guards.ps1`'s tier list, `verification-boundaries.v1.json` if a new test project needs a boundary)
- `gk-core/src/FusionRpg.Data/**` — only for F14's schema path if the test needs a seam
- `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**` — only for KS-F1's discovery seam
- `tasks/content-stack-todo.md`, `tasks/keepverse-split-todo.md`, `tasks/*-ledger.jsonl` — the rows you close
- `docs/architecture/**` — only where a row's own spec sentence must be recorded

Anything else is another session's fence. If a row needs a file outside this list, **stop and report it as an
external dependency with the path named** — do not reach across the fence.

## Hard rules

1. **A guardrail validates the CONTRACT and closed enums — never a population count or generated text.** No
   literal that rots: assert the envelope, membership, joins, uniqueness, determinism, structural bounds.
2. **A guard must have a planted-violation case.** A rule that has never been seen to fail is not known to work.
3. **Test substrate:** tests run **in memory**. `gk-core/scripts/guard-test-substrate.py` now enforces it: a `tests/**`
   file constructing a file-backed store must carry `[Trait("Category","DiskSemantics")]`. Tag only what genuinely
   tests file behaviour — never to silence the rule.
4. **Never widen a guard, never add a `knownRed`, never re-add a baseline exemption.** If a rule you add flags
   pre-existing files, those files are the finding: tag them properly or fix them, and say which you did.
5. **Close the row in its own todo in the same commit** as its evidence, and assert the row id is present after
   the edit (a reused id has silently appended nothing before).

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session findings-1`
- `python gk-core/scripts/guard-test-substrate.py` — must exit 0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — must stay at 21 guards / 0 failures (read the printed counts, not the exit code).
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "<your new case>"` — the planted violation must fail, and the real tree must pass.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report (end every segment with this)

```
<<<REPORT
{"status": "partial|done|blocked",
 "summary": "<what landed, with commit shas and row ids>",
 "closed": ["<row id>: <one-line evidence>"],
 "open": ["<row id>: <what it now waits on, named>"],
 "blocked": ["<row id>: <the named external dependency or the sharpened question>"],
 "next": "<the single next row you would take>"}
REPORT
```

Every claim in the report must already be a commit in this worktree.
