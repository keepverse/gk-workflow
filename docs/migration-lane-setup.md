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
