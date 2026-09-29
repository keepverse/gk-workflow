# Mega-merge QC 11 — ip-censor on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Tool suite. No live game.

## Verdict: GREEN (T16 was deferred in the QC pass; fixed in fix cycle 9)

| Check | Command | Result |
|---|---|---|
| ip-censor pytest | `python -m pytest gk-core/tools/ip-censor -q` | 218/218 |

## Open rows noted, not QC failures

ip-censor-todo: 15 done / 10 open — incl. deferred T16 (resume-later note in row). No merge-interaction red.

## Fix cycle 9 (2026-09-24) — T16 (IC-4.1) landed

Resumed the dead opencode lanes' staged work: the avoid_list helper + fixture tests (recovered from
branch `opencode/ipc-3d-staged`), the brief IP avoid line with `PROMPT_VERSION` → `tree-language/4`,
and the `trees generate --node <id>` selector. Node `skill.command-def-t8-n0` regenerated through the
generator's supersede path → `Structural Integrity Protocol` (`tree-language/4`); the live node is
clean of `overwatch`. One real defect found and fixed en route: the first `--node` implementation
trimmed the replay set, shrinking `command.json` 40→1; the selector now narrows generation only.
Residual (by design): the run-ledger keeps the prior row under `supersededRecord`. Proof: 589
nodegen+avoid_list tests pass; scan step 5 clean on the live node.

QC 11 T16 deferral is now closed.
