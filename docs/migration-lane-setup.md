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

## 4. Check what is committed, and who committed it, before claiming either

Recorded 2026-09-30 while running Lane 3 (the gk-tests topology reconciliation). Two
attributions in this file were wrong before they were right, and both errors were the same
error, so the rule is recorded rather than the incident.

**What the git evidence says, with nothing inferred.** Lane 3 edited four files in its fence:
`kvsplit/rules.py`, `kvsplit/check.py`, `rules/layout.v1.json` and a new
`tests/test_topology_seal.py`. Those four reached `HEAD` as `eeeab88`, whose `--stat` lists
exactly those four paths and no documentation. `b4d359e` is Lane 3's own commit of the three
document files. Those are the two commits, and the split between them is recorded here because
it is checkable:

```
git show --stat --format="" eeeab88   # 4 code paths, no docs/
git show --stat --format="" b4d359e   # 3 docs/ paths
```

**What is NOT established, and was asserted anyway.** Twice during this lane, prose appeared
about the origin of the commits and the plan edits — once crediting an agent acting
autonomously, once crediting a manager acting after a lane death. Neither claim was supported
by anything, and the second was written into this file in place of a version that was at least
honest about its own uncertainty. A fifth possibility, that a hook or the harness committed the
work, was not excluded by either account. **Provenance here is unknown.** The four files and the
content are verified; who ran `git commit` is not, and no agent should assert otherwise.

**Why it matters for the next lane.** `[ADDED 3]` says do not inherit a verification claim,
including the manager's. This is the same failure arriving from a new direction: not a number
that looks like evidence, but a *story* about the workspace that nobody checked, in a document
whose whole purpose is to be the place where checked things are written down. It is more
infectious than a bad figure, because a bad figure is contradicted the moment someone re-runs
the command, while a plausible story is repeated.

**Practical consequence.** After any edit, before concluding anything about what is committed
or who committed it:

```powershell
git status --porcelain=v1     # what is dirty, right now
git log --oneline -3          # what is at HEAD, right now
git show --stat --format="" HEAD   # what the last commit actually touched
```

If `HEAD` moved and you did not move it, or a file is dirty and you did not write it, **report
that as the finding and do not explain it.** Say what the commands show, say that the origin is
not established, and leave it. The times this migration lost time to a wrong claim — "unplaced
0" from a count that excluded copies, an A7 scan whose needles matched code paths merely
mentioning the word, and this one — were all a fact asserted without the command that settles
it. An unverified attribution is the same defect with a worse shelf life.
