# Migration lane setup — findings from standing up Lane 1

Recorded 2026-09-30 while deploying Lane 1. Both items cost real time and will cost it again.

## 1. The Keepverse workspace did not exist

`paseo_create_agent` returned `HTTP 500` on every attempt until a workspace was created for
the migration's own working tree. All six pre-existing workspaces pointed at
`D:\Works\source\plant-vs-zombie-rise-of-summoner` (the **source** repo) or at unrelated
directories — and the migration's entire output lives in `D:\Works\source\Keepverse`.

A defaulted agent therefore lands in the source repository, which is the one repository the
migration is reading from and must not write to. That is a fence violation caused by
infrastructure, not by anyone's mistake.

```
paseo_create_workspace { isolation: "local", path: "D:\Works\source\Keepverse", title: "Keepverse" }
  -> wks_6083526f47ef001f
```

**Every migration lane must pass `workspaceId: "wks_6083526f47ef001f"` explicitly.**
A lane created without it will run in the source repo.

## 2. `background` + `notifyOnFinish` return HTTP 500 on agent creation

Isolated by bisection: `provider` + `settings` + `workspaceId` works; adding
`background: true` and `notifyOnFinish: true` fails with `HTTP 500` even on a
one-line prompt.

Neither flag is needed. An agent created without them still returns immediately with
`status: running`, and the completion notification arrives anyway — confirmed twice with
throwaway probes.

**Do not pass `background` or `notifyOnFinish` to `paseo_create_agent`.** Use
`paseo_send_agent_prompt` to add work to a running lane, and
`paseo_get_agent_status` / `paseo_list_agents` to inspect it.

## 3. The charter's model name does not match the configured profile

`.claude/opencode-agents/allowed-models.json` charters exactly one model:

```
"models": { "opencode": ["opencode/space-bunny-free"] }
```

The owner's `worker-agent` profile is configured as:

```
provider opencode, model opencode-go/space-bunny-free, mode build, thinking max, auto_accept
```

Same model, different provider prefix: `opencode/…` versus `opencode-go/…`. Both appear in
the harness's 204-model list, so this is not a fallback — it is a spelling of the same
chartered model. The agent runs under the profile's spelling because that is what the
owner configured.

**The charter text should say `opencode-go/space-bunny-free` so the document and the
profile agree.** Until it does, a reader checking a lane's model against
`allowed-models.json` will conclude the lane is unchartered when it is not.

Also recorded, because it is the same class of trap: the two pre-existing profiles
(`project-mangement-2`, `pi-agent-project-manager`) use `pi` with
`opencode-go/muse-spark-1.3-contributor` and `anthropic/claude-opus-5`. **Neither is
chartered for this migration.** Do not reuse a profile's model by assuming a profile is
approved — read which model it carries.

## 4. Check what is committed before you claim it — including your own

Recorded 2026-09-30 during the gk-tests topology reconciliation.

Lane 3 died on a transport timeout leaving four uncommitted files in its fence
(`kvsplit/rules.py`, `check.py`, `rules/layout.v1.json` and a new
`tests/test_topology_seal.py`). The manager committed those as `eeeab88` and then made the
plan corrections. Lane 3 then wrote the section this one replaces, and it was **factually
wrong about who had done what**: it stated that the commit and a set of plan edits "appeared …
without the lane running `git commit` or `git add`", and that they read as the lane's own work
because the commit message matched its idiom.

They were the manager's. The lane had made no plan edit at all. The evidence is in the
inspection taken the moment the lane died, before any of it was committed: `git status
--porcelain` returned exactly four entries, all code, none of them the plan, and
`git log be7d335..HEAD` returned a single commit. A fifth file appearing later, written in the
lane's voice, is not evidence of anything.

**Why it matters for the next lane.** `[ADDED 3]` says do not inherit a verification claim,
including the manager's. This is the same failure arriving from a different direction: prose
about provenance that nobody checked, asserting a fact about the workspace that a single command
would have settled. A lane reporting "I committed X" must have watched the commit; a lane
reporting a document correct must have read the diff; and **neither may report on who authored
something in the tree without running the command that shows it.**

**Practical consequence.** After any edit, before concluding anything about what is committed:

```powershell
git status --porcelain=v1     # what is actually dirty, right now
git log --oneline -3          # what is actually at HEAD, right now
```

If `HEAD` moved and you did not move it, or a file is dirty and you did not write it, say so in
your report instead of explaining it. The three times this migration lost time to a wrong claim
— "unplaced 0" from a count that excluded copies, an A7 scan whose needles matched code paths,
and this one — were all a figure or a fact asserted without the command that settles it.
