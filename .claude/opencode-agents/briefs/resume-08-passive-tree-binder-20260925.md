# PassiveTree binder/resolver repair lane — narrow code fence

The accepted FamilyExpand vocabulary recovery fixed the manifest reader, but the current
`gk-forge/tools/TreeBinder --check` still reports a large stale/refused corpus. This lane must diagnose that
seam and fix only a proven code/gate defect. It is not a BCU2.12 resume lane.

## Read first

- `docs/architecture/passive-tree/spec-tree-binder.md`
- `docs/architecture/passive-tree/spec-tree-language.md`
- `.agents/skills/seedsmith-passivetree-repair/SKILL.md`
- current `tasks/passive-tree-repair-todo.md` and the accepted vocabulary report/artifact

## Allowed paths

- `gk-forge/tools/TreeBinder/**`
- `gk-core/src/FusionRpg.Core/PassiveTree/**`
- `gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/**`
- `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/**` if present
- `tests/FusionRpg.Core.Tests/PassiveTree/**` if present
- `tasks/reports/resume-08-passive-tree-binder-20260925.md`

No `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, tuning, CI, release, web, Server, or unrelated Core paths.
No full model/corpus generation. No hand-edited generated JSON. If a green binder requires content
regeneration or a vocabulary/owner decision, stop at a precise classified blocker.

## Required work

1. Reproduce the current binder failure with the exact command and classify each dominant refusal or
   crash as generator (A), persistence/wiring (B), metric/gate (C), stale evidence (D), or incomplete
   run (E), citing the responsible source file/symbol.
2. Verify the current resolver actually reads the kinds the binder emits. Add or repair the smallest
   deterministic code/test seam for any proven B/C defect; do not weaken a gate or invent content.
3. Keep the existing `FamilyExpandGen`/vocabulary outputs untouched. Do not regenerate the BCU2.12
   corpus or claim a population is healthy from an aggregate.
4. Run focused restored tests, binder check/diagnostic, relevant guards, and path-owned PlanOnly. If the
   check remains red because the committed corpus is stale/incomplete, report that exact boundary and
   the owning follow-up rather than editing data.
5. Write a disk-backed report with commands/results, classification, changed files, open owner/content
   decisions, and next steps. Leave the worktree dirty for manager review; no commit/push/merge.

Use only OpenCode CLI `opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent,
and no external-directory reads.
