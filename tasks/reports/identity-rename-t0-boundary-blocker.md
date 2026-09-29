# identity-rename T0 — boundary blocker for `README.md` / `CONTRIBUTING.md`

**Row:** `T0` (session record and boundaries for the unmapped front pages)
**Lane:** `identity-rename-1` · branch `cmdc/identity-rename-1` · worktree mode
**Date:** 2026-09-22 · **Status:** the session-record half landed; the boundary-registry half is
**blocked on a pipeline-owned edit**.

## What landed

`tasks/sessions/identity-rename-1.json` — worktree-mode record, absolute `worktree` path, one problem,
the program's path fence plus the shared files its tasks name, and the plan §5 crossings recorded.
`python scripts/session-boundary-check.py --session identity-rename-1` is clean from this worktree.

## Why the registry half did not land

The row asks for one owner row mapping `README.md` and `CONTRIBUTING.md` to project `guard`,
verificationId `guard.doc-boundary`, at the end of `boundaries` in
`gk-core/scripts/verification-boundaries.v1.json`. The row was written, `guard-verification-boundaries.py`
returned `VERIFICATION BOUNDARY GUARD OK`, and `verify-change.ps1 -Paths README.md` stopped throwing
`VERIFICATION BOUNDARY MISSING` — the acceptance line.

It cannot be committed alone, because a second, **protected** file pins the opposite:

```
gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs:239-246
    public void Planner_refuses_an_unmapped_path_instead_of_selecting_a_broad_suite()
        // The example path must stay unmapped. It was docs/DESIGN-GATE.md until docs/** gained its
        // own owner (docs-and-assistant-config, DocBoundaryTests); the root README has no owner.
        "-File scripts/verify-change.ps1 -Paths README.md -AllowUnscoped -PlanOnly"
        Assert.Contains("VERIFICATION BOUNDARY MISSING", stdout + stderr, StringComparison.Ordinal);
```

The test is not stale by accident: it is a fixture that must move every time an unmapped path gains an
owner (the comment records the previous move, `docs/DESIGN-GATE.md` → `README.md`). T0 is exactly such
a move. Measured on the mapped tree:

```
Failed FusionRpg.Guard.Tests.VerificationBoundaryWorkflowTests.Planner_refuses_an_unmapped_path_instead_of_selecting_a_broad_suite [11 s]
  Error Message: unmapped path unexpectedly selected a test scope
  Stack Trace: ... VerificationBoundaryWorkflowTests.cs:line 245
Failed!  - Failed:     1, Passed:   590, Skipped:     0, Total:   591, Duration: 8 m 16 s - FusionRpg.Guard.Tests.dll (net8.0)
```

Editing that test is refused by the pipeline hook — `gk-core/tests/FusionRpg.Guard.Tests/**` is one of the
protected pipeline files ("guards"):

```
Blocked by the orchestrator pipeline guard: protected pipeline file (guards, verify, ledger script,
hooks, CI). Use the sanctioned path (plain git for your own commits, anchor-ledger.py for the ledger)
or record a blocker note; do not try another route around this rule.
```

A lane may not widen a guard or add a `knownRed` entry to pass, so the two edits must land together and
only the pipeline owner can make the second one. The registry edit was reverted; the tree stays green.

## The exact patch (two parts, one commit)

**1. `gk-core/scripts/verification-boundaries.v1.json`** — one new block at the end of `boundaries`, after
`core-siege-estimator-parity`, before the `knownRed` key:

```json
    {
      "id": "identity-rename-front-pages",
      "kind": "owner",
      "paths": [
        "README.md",
        "CONTRIBUTING.md"
      ],
      "project": "guard",
      "verificationId": "guard.doc-boundary",
      "guards": [],
      "level": "focused"
    }
```

**2. `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`** — move the "must stay
unmapped" fixture off `README.md`, which now has an owner. `LICENSE` was verified unmapped
(`verify-change.ps1 -Paths LICENSE -AllowUnscoped -PlanOnly` → `VERIFICATION BOUNDARY MISSING`) and is
claimed by no session record, so it cannot go stale the way the previous two fixtures did:

- `:225` — `const string outside = "README.md";` → `const string outside = "LICENSE";`
- `:243` — `"-File scripts/verify-change.ps1 -Paths README.md -AllowUnscoped -PlanOnly"` →
  `"-File scripts/verify-change.ps1 -Paths LICENSE -AllowUnscoped -PlanOnly"`
- both comments: `README.md` → `LICENSE`, with the T0 move named.

Then `verify-change.ps1 -Paths tasks/sessions/identity-rename-1.json,
gk-core/scripts/verification-boundaries.v1.json,README.md -Session identity-rename-1` is green, and the row's
second acceptance line passes.

## Why `LICENSE` and not `web/**`

`gk-web/web/fusion-rpg-web/**` is also unmapped today (`docs/architecture/identity-rename-plan.md` D7), but it
is the story-scene program's reported boundary defect and this lane's own record claims `web/**`, so a
fixture there would be stale again the moment `web/**` is mapped. `LICENSE` carries no session fence and
no task plans to own it.

## Reading, not a constant

Two further facts this lane measured while here, both recorded for the manager rather than asserted
anywhere:

- `gk-core/scripts/guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK` with the row present
  and again with it reverted.
- `docs/architecture/identity-rename-plan.md` §D7 still says "`README.md`, `CONTRIBUTING.md`, `web/**`
  and `gk-data/packs/fusion/data/seed/narrative/**` are not [mapped]". Once the patch above lands, that sentence is stale for
  the two front pages; the file is outside this lane's fence, so the correction belongs to whoever
  lands the patch.
