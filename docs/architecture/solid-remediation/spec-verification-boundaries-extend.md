# spec — `verification-boundaries-extend`

**Module 3 of `solid-remediation`.** Register entry: **G3**. Depends on `green-baseline`.

## Objective

Give the back-end tool trees a scoped verification boundary, so a change inside them selects real tests
instead of falling through to "run everything" or "run nothing".

Like the guard module, this changes no behaviour. It also *unblocks* `estimator-parity`, which cannot
prove anything about `gk-core/tools/CombatSim` or `gk-core/tools/ProvePredictor` until those paths are mapped.

## The defect (G3)

Three trees have no verification boundary at all:

- `gk-core/tools/CombatSim/**`
- `gk-core/tools/ProvePredictor/**`
- `web/**`

Per `AGENTS.md`, **an unmapped production path is itself a verification-boundary defect** — the rule is
that an unmapped path is repaired or reported, never compensated for by running the full suite.

## Scope

**Back-end trees only: `gk-core/tools/CombatSim/**` and `gk-core/tools/ProvePredictor/**`.**

`web/**` is out of scope for remediation and in scope for tracking (owner ruling: *"solve the BE first…
the FE is ugly, so I want to refactor it almost completely, so we don't really do it now, but track it"*).
Its missing boundary is a row in the **FE debt register**, not work here. Mapping a tree the owner intends
to rebuild is effort spent twice.

## Shape

Extend the existing mapping that `scripts/verify-change.ps1` reads. Two properties matter more than
coverage:

1. **A path maps to the tests that would actually notice it breaking**, not to the nearest suite by name.
   A mapping that selects tests which cannot fail for this path is worse than no mapping, because it
   reports confidence it has not earned.
2. **An unmapped path under these trees is a failure**, not a silent pass. That is the rule G3 cites; a
   boundary that quietly ignores what it does not know is how the gap appeared.

`scripts/verify-change.ps1` requires `-Session`, so this module also confirms the session record created
in `green-baseline` works for the tool trees.

## Tests to write

- A changed file under `gk-core/tools/CombatSim/**` selects a non-empty test set
- A changed file under `gk-core/tools/ProvePredictor/**` selects a non-empty test set
- An unmapped path under either tree **fails** rather than selecting nothing
- `-DeletedPaths` still resolves the former boundary for a deleted file in these trees

Assert the **mapping contract** — that a path resolves to a boundary, and that an unmapped one refuses.
Never assert how many tests a boundary selects: that is a population and it grows whenever a test ships.

## Boundaries

- **Always:** a mapping points at tests that can fail for that path
- **Ask first:** mapping `web/**` — it is deliberately excluded and belongs to the later FE program
- **Never:** compensate for a missing mapping by widening the selected suite

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/tools/CombatSim/<file> -Session solid-remediation-<date>
.\scripts\verify-change.ps1 -Paths gk-core/tools/ProvePredictor/<file> -Session solid-remediation-<date>
```

- [ ] Both tool trees select a non-empty, relevant test set
- [ ] An unmapped path under them fails with a message naming the path
- [ ] `estimator-parity` can now prove a change in either tree

## Register

Appends to the **FE debt register**: `web/**` has no verification boundary, deliberately deferred here,
owned by the later FE program.
