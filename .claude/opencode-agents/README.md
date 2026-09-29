# opencode lanes — operator runbook

`scripts/opencode_lane.py` runs headless opencode workers with the same
agent-dir contract as the cmdc/pi runner (`brief.md`, `status.json`,
`timeline.jsonl`, `notes.jsonl`, `result.json`, `events.jsonl`,
`<<<REPORT … REPORT>>>`). Contract spec: `opencode-backend-spec.md`.

## 0. Charter first (hard rule, never skipped)

`allowed-models.json` must carry `approvedAt`, exact `models.opencode` ids
(opencode native `provider/model` form — `opencode models` lists them), and
`budget.tokensPerLane`. `spawn` refuses without them, and a lane stops at its
token budget. A credit/quota error stops the lane; never switch models to keep
going — report it. Only the owner edits the charter.

## 1. Spawn (detaches immediately)

```
python .claude/opencode-agents/scripts/opencode_lane.py spawn --id <kebab>
    --brief <brief.md> --context <context.jsonl>
    --model <provider/model> --allow <glob> [--allow ...]
    [--verify "<cmd>"] [--setup "<cmd>"] [--budget N] [--segment N]
    [--effort <variant>] [--base HEAD]
```

Creates branch `opencode/<id>` and worktree `.claude/worktrees/opencode-<id>`,
runs `--setup` there, then supervises segments (`--segment` steps each,
default 40) until done/partial/blocked/failed/stopped/budget_exhausted.

## 2. Watch

```
python .claude/opencode-agents/scripts/opencode_lane.py status [--id X]
python .claude/opencode-agents/scripts/opencode_lane.py tail --id X --notes
```

## 3. Steer / stop

`steer --id X "text"` (next segment), `budget --id X --add N`,
`stop --id X` (`--now` kills the running segment).

## 4. Receive and land

`result.json` holds the lane's REPORT (claim) plus `runnerVerify` (evidence:
re-run commands, scope check, diffstat) and the real git facts. Then:

```
python .claude/opencode-agents/scripts/opencode_lane.py audit --id X
python .claude/opencode-agents/scripts/opencode_lane.py harvest --id X
git apply --3way .claude/opencode-agents/agents/<id>/changes.patch
git add <explicit paths> && git commit   # never -A/-a
python .claude/opencode-agents/scripts/opencode_lane.py cleanup --id X [--purge]
```

`verify --id X [--command "<cmd>"]` re-checks after a fix. `cleanup` removes
the worktree+branch (keeps the agent dir); `--purge` deletes that too.

## 5. Differences from cmdc/pi (deliberate, documented)

- No pre-tool guard hook exists for opencode (verified absent 2026-09-23).
  Posture: cwd jail (positional worktree) + scope verify + audit detect layer.
- No fallback models until the owner names them; `tune` across runtimes is not
  implemented — respawn instead.
- Runtime state under `agents/` is gitignored; only code/docs/charter are tracked.
