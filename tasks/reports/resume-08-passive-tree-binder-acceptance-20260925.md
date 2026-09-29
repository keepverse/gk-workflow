# Manager acceptance review — PassiveTree binder/resolver parity

**Reviewed lane:** `resume-08-passive-tree-binder-20260925`
**Status:** GREEN for the narrow report/read-seam repair; the TreeBinder corpus remains RED and is not accepted as healthy.

## Review verdict

The worker's three-code-path change is narrow and preserves the existing primary/derived boundary. `TreeAtomSource.TryReadOp` is now the single admission predicate used by the live derived fan-in and `TreeResolveReport.HasReadableAtom`; a binder-emitted `stat.modify` or mechanism/status-only node is no longer reported as a derived contribution when the resolver drops it. The regression test constructs a real binder result and proves both the empty resolver output and the non-contributing report projection.

No generated seed, generated catalog, tuning, Server, CI, or unrelated Core path changed. The worker report's classification is preserved: 611 stale tree-language affix refusals, 507 pool-channel wiring refusals, one incomplete `wither` node, one stale `command.json`, and an unresolved primary `stat.modify` route remain open owner/content work. This acceptance does not widen the resolver into a second composer or regenerate BCU2.12.

## Independent checks

```text
dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests
  --filter "FullyQualifiedName~TreeBinderResolverParityTests"
# 1 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests --no-restore
# 406 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-forge/tests/FusionRpg.TreeBinder.Tests --no-restore
# 45 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests --no-restore
# 25 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Core.Tests
  --filter "FullyQualifiedName~TreeAtomSourceParityTests" --no-restore
# 5 passed, 0 failed, 0 skipped; exit 0

scripts/guard-single-writer.ps1                 # exit 0
scripts/guard-secondary-no-unity.ps1            # exit 0
scripts/guard-funnel-delta.ps1                  # exit 0
scripts/guard-dal.ps1                           # exit 0
scripts/guard-actor-hub.ps1                     # ACTOR-HUB GUARD OK; exit 0
gk-core/scripts/guard-test-substrate.py                # exit 0
verify-change.ps1 -Paths <three concrete paths>
  -Session resume-08-passive-tree-binder-acceptance-20260925 -PlanOnly -Format json
# exit 0; core-passivetree and unique-allocation seams selected
scripts/session-boundary-check.py
  -Session resume-08-passive-tree-binder-acceptance-20260925
# clean; exit 0
```

External focused log SHA-256:
`8BF6EFE9C05AAA510C3B5B770AEF2D09920BCFE5B6E4800DE85B4AC7FD091D4A`.

The worker's full selected `verify-change` run also recorded the already-known out-of-fence
`RpgStoreStoragePlanTests.Memory_schema_is_identical_to_the_file_store` SQLite backup failure. It
is not counted as a green aggregate or attributed to this three-path change.

## Open boundaries

- Primary `stat.modify` route into the existing battle/Hub path: owner/design follow-up.
- Pool-channel bake/roll resolution: effect-pipeline module 2, not a second TreeBinder resolver.
- Stale tree-language/generated corpus and missing `wither` node: generator/content follow-up.
- `TreeBinder --check` remains red; no corpus health claim is made.
- BCU2.12 remains paused; no generated data was regenerated.

## Exact-SHA steps remaining

1. Commit the reviewed code/test/report set at an exact SHA.
2. Run the focused checks and `git status --porcelain=v1` from a clean detached checkout.
3. Write a schema-v2 acceptance artifact and merge only that SHA.
4. Route the five open follow-ups to their owning ledgers.

<<<REPORT {"status":"done","summary":"Accepted the narrow PassiveTree TreeAtomSource/TreeResolveReport parity repair: the report and actual derived resolver now share the same kind/op admission predicate, with a real binder-result regression test. Focused Core.PassiveTree 406/406, TreeBinder 45/45, RosterGen 25/25, Core parity 5/5, guards, PlanOnly, and boundary checks passed. The TreeBinder corpus remains red and the primary stat.modify route, pool resolver, stale corpus, missing wither node, and BCU2.12 resume remain open.","changed_files":["gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs","gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeResolveReport.cs","gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeBinderResolverParityTests.cs","tasks/reports/resume-08-passive-tree-binder-20260925.md","tasks/reports/resume-08-passive-tree-binder-acceptance-20260925.md"],"verification":["focused log SHA-256 8BF6EFE9C05AAA510C3B5B770AEF2D09920BCFE5B6E4800DE85B4AC7FD091D4A","1 parity test, 406 Core.PassiveTree tests, 45 TreeBinder tests, 25 RosterGen tests, and 5 Core parity tests passed","single-writer, secondary-no-unity, funnel-delta, DAL, ActorHub, and test-substrate guards passed","path-owned PlanOnly and session boundary check passed","full selected verify-change stopped on the documented out-of-fence Data.Tests SQLite backup failure; not counted green"],"open_issues":["exact-SHA clean checkout and artifact are not yet created","TreeBinder --check remains red on stale/incomplete content and pool wiring","primary stat.modify route and BCU2.12 resume remain open"],"next_steps":["commit exact reviewed SHA","clean-checkout focused verification and schema-v2 artifact","merge exact SHA","route primary-route, pool, stale-corpus, and missing-node follow-ups"]} REPORT>>>
