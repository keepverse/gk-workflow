# Program inventory and next-lane queue — read-only

The P1 containment lanes have now been independently accepted and merged at exact SHAs. Before dispatching the next implementation wave, produce a read-only, disk-backed inventory of the remaining Garden Keeper program work at the current `features/mega-merge` head.

## Scope

Read the current task ledgers/todos, capability maps, module specs, acceptance artifacts, session records, and the deep-audit handoff. Do not edit product code, generated data, tuning, CI, verification scripts, or existing task ledgers. The only permitted write is this lane's report and its session record.

## Questions to answer

1. Which program task blocks remain genuinely open after the accepted P1 work, using task blocks rather than raw unchecked checkbox lines?
2. Which are dependency-ready for an implementation lane now, and which are owner-decision, live-environment, generated-corpus, migration/hard-edge, or external-environment blocked?
3. What is the next dependency-aware dispatch queue of 3–6 bounded lanes, with exact program, row/task id, allowed repository paths, likely shared fences, required hard-edge treatment, focused verification boundary, and stop condition?
4. Which findings from the deep audit or lane reports still have no owning todo/ledger row? List the exact target file and row id that should receive each one.
5. What current evidence is stale after the recent merges, especially the merged-head post-merge report and Seedsmith BCU2.12 state?

## Evidence rules

- Read the actual current files; do not rely on the historical summary.
- Do not count generated populations or unchecked lines as completion metrics.
- Do not call browser/live/legal-injector evidence complete without a current artifact.
- Preserve owner decisions as open; do not invent defaults.
- Report exact paths/rows/SHAs and commands used. No commit, push, or merge.

## Required report

Write `tasks/reports/resume-06-program-inventory-20260925.md` with status, current head, method, open task-block queue, dependency graph, proposed fences, blocked decisions/evidence, stale reports, and next manager actions. End with a valid `<<<REPORT {json} REPORT>>>` block.

Use only OpenCode CLI `opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent, and no external-directory reads.
