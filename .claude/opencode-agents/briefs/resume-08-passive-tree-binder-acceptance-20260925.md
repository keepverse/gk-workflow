# Manager acceptance review — PassiveTree binder/resolver parity repair

Review the dirty output of `resume-08-passive-tree-binder-20260925` at a clean exact SHA. Accept only
the proven report/read-seam repair; do not accept the red TreeBinder corpus as healthy and do not
edit generated data.

## Allowed paths

- `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs`
- `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeResolveReport.cs`
- `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeBinderResolverParityTests.cs`
- `tasks/reports/resume-08-passive-tree-binder-20260925.md`
- `tasks/reports/resume-08-passive-tree-binder-acceptance-20260925.md`

No gk-data/packs/fusion/data/seed, gk-data/packs/fusion/data/generated, tuning, CI, Server, Contracts, or unrelated Core paths.

## Acceptance boundary

1. Verify the report and the actual derived fan-in share the same kind/op predicate; no primary or
   mechanism atom may be called contributing when `TreeAtomSource` drops it.
2. Run focused PassiveTree/Core/TreeBinder/RosterGen tests, relevant guards, and path-owned PlanOnly.
3. Run the focused checks from a clean detached checkout at the exact reviewed SHA.
4. Preserve the TreeBinder red classification and the out-of-fence Data.Tests backup failure as
   limitations; do not broaden the repair into the primary `stat.modify` route, pool resolver, stale
   corpus, or BCU2.12 regeneration.
5. Write the manager report with exact commands/results, changed files, clean-checkout proof, and
   open owner decisions. Commit/merge only through the manager.
