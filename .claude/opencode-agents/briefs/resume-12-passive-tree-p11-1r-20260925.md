# PassiveTree P11.1r — primary stat.modify fan-in

Implement only the named P11.1r row: make a node's existing `stat.modify` atom reach the existing
`BoundDerivedAtom`/`AtomDerivedSubsystem` fan-in, without adding a subsystem or order band. The
accepted binder/report parity repair is the baseline; preserve its shared admission predicate.

## Read first
- `docs/architecture/passive-tree/spec-mechanism-wiring.md` (§2.3 and the primary/derived split)
- `docs/architecture/passive-tree/spec-tree-resolve.md`
- `tasks/passive-tree-repair-todo.md` P11.1r
- accepted binder parity report/artifact

## Allowed paths
- `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs`
- `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeAtomSourceTests.cs`
- a pre-existing focused parity test only if the row requires it
- `tasks/reports/resume-12-passive-tree-p11-1r-20260925.md`

No `TreeResolveReport` rewrite unless the existing shared predicate cannot express the proven
behavior; no gk-data/packs/fusion/data/seed, gk-data/packs/fusion/data/generated, tuning, generator, CI, Server, or new subsystem paths.

## Required behavior
- Map `stat.modify` through the existing `BoundDerivedAtom` shape and operation/scale contract.
- Keep one ActorHub composition and the existing derived fan-in; do not reinterpret primary channels
  as a new composer or add an order band.
- `TreeResolveReport` and `BoundAtomsFor` must agree on live contribution after the change.
- Prove a primary atom contributes in both lawn and battle read shapes with focused tests, or report
  the exact missing production seam instead of fabricating one.
- Do not regenerate or hand-edit any corpus.

## Verification/report
Run restored focused PassiveTree tests, relevant Core parity/balance tests, `guard-actor-hub`,
`guard-power`, and path-owned `verify-change -PlanOnly` for every changed path. Record exact commands,
changed files, unresolved KMicro/ScaleAxis or owner decisions, and next steps. Use only
`opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent, no external reads.
