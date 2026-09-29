# Lane brief — `findings-2` (KS-F2's guard + CS-F2, with the protected paths granted)

## Why this lane exists

`findings-1` closed **F14** (a committed regression test for the F13 schema upgrade) and **KS-F1** (the verified
answer that the boot cannot own a content-root resolver — it landed the eight missing Server copy rules that make
the plan's runtime exemption true, plus a contract case that keeps them), and filed **CS-F2**. It then hit a wall
that is not its own: **the pipeline guard refuses writes to `scripts/guard-*.ps1` and
`gk-core/scripts/enforcement-registry.v1.json`**, so the guard script KS-F2 needs could not land.

**This lane carries that grant.** Everything else about the work is unchanged — read
[`findings-1.md`](findings-1.md) for the full context, the hard rules and the verification commands.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this session, then verify against code.

## The rows

### KS-F2 — nothing forbids a private repo-root walk in a test (S)

`CS-F1` was a fixture defect: `SpeciesModLedgerTests` walked the tree privately with `..\..\..`, which passed in a
worktree and failed in the main checkout. It was fixed to use `FusionRpg.TestSupport.ContentRoot.Path`, but nothing
stops the next test from hand-rolling the same walk.

Deliver: an enforced refusal of a hand-rolled repo-root walk inside `tests/**` — a guard script under `scripts/`
(wired the way the other guards are: the tier list in `scripts/run-guards.ps1` and
`gk-core/scripts/enforcement-registry.v1.json`) **plus** a case in `gk-core/tests/FusionRpg.Guard.Tests` that proves the rule bites
on a **planted violation**. A guard without a planted-violation case is not a guard.

⚠ `findings-1` recorded an erratum worth reading before you write the rule: **the walk population is 58/30, not 28**
— measure the population yourself, and do not pin a count in the guard (a population is a reading, not a constant).

### CS-F2 — the packaging defect `findings-1` filed

Its row is in `tasks/keepverse-split-todo.md`; read it there and close it, or end the segment naming exactly what
blocks it.

## Grants this lane carries (the reason it exists)

- `scripts/guard-*.ps1` — **including new guard scripts**, via `--allow-protected`
- `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`
- `tests/**`, `tasks/keepverse-split-todo.md`, `tasks/keepverse-split-ledger.jsonl`, `docs/architecture/**`

Never widen a guard, never add a `knownRed`, never re-add a baseline exemption. If a new rule flags pre-existing
files, those files are the finding: tag or fix them and say which you did.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session findings-2`
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "<your new case>"` — the planted violation must fail, the real tree must pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next), and every claim
in it must already be a commit in this worktree.
