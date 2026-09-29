# Lane brief — `ipc-3b` (opencode continuation of `cmdc/ipc-3`, T16 / IC-4.1)

## Why this lane exists

`cmdc/ipc-3` (pi, 7 segments) drained with its T12 gate reading and the IC-4.1
target confirmed but unlanded. Its worktree is adopted as `b6a8c53a4` on
`cmdc/ipc-3` — adopt that commit, then close the row below. Do NOT re-do the
gate reading; it is handover fact.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## Goal

Close `tasks/ip-censor-todo.md` **T16**: tree brief adopts the avoid line,
`--node` selector, regenerate the Overwatch node (`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538,539`,
player-name, enforced) — IC-4.1. Checkpoint 5 names the commit
`ip-censor T16: tree brief avoid-list and regenerate skill.command-def-t8-n0 (IC-4.1)`.

## Handover facts (already verified — confirm at adopt time, do not re-derive)

- T12 gate reading on the real tree: exit 1; 7119 findings in 1243 files; 111
  enforced in 42 files (player-name 7, player-prose 60, generator-prompt 44).
  Evidence: `tasks/evidence-fragments/ip-censor-T12.md` (adopted in `b6a8c53a4`).
- IC-4.1 target: `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538,539`
  (Overwatch, player-name, enforced).
- Generated data is NEVER hand-edited: change the brief/generator, then
  regenerate and commit the diff. If the generator cannot express the fix,
  stop and say so — the generator fix is the deliverable, not a data edit.

## Allowed paths

- `gk-core/tools/ip-censor/**`
- `gk-forge/tools/seedsmith/**`
- `docs/architecture/ip-censor*/**`
- `docs/runbook/release-prove.md`
- `.github/workflows/release.yml`
- `gk-core/scripts/enforcement-registry.v1.json`
- `gk-data/packs/fusion/data/seed/passive-tree/nodes/**`
- `tasks/ip-censor-*`
- `tasks/evidence-fragments/ip-censor-*`

## Off limits

`tests/**`, the rest of `scripts/**`, `gk-data/packs/fusion/data/seed/**` outside passive-tree
nodes, `gk-data/packs/fusion/data/generated/**`, keepverse and content-stack todos/ledgers,
`tasks/reports/**`, other lanes' files (including `opencode/findings-2b`'s
`gk-core/tests/FusionRpg.Core.Tests` helpers and keepverse ledger). Never widen a
guard, never add a `knownRed`. Commit nothing, push nothing, create no
branches — leave the tree dirty; the orchestrator harvests.

## Definition of done

1. WIP `b6a8c53a4` adopted (cherry-pick -n or equivalent re-apply; new files
   such as the T12 evidence fragment must be present).
2. T16's three acceptances landed in one commit-shaped change: avoid line in
   the tree brief, working `--node` selector, regenerated Overwatch node.
3. `tasks/ip-censor-todo.md` T16 ticked with the evidence fragment (exact
   command text + printed numbers); ledger line appended.

## Verification

- `git log --oneline -3` and `git show b6a8c53a4 --stat` — confirm what you adopt first.
- The exact verify commands T16's row names (run them verbatim from the row).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree.
