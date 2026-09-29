---
name: seedsmith-preflight
description: Before starting any demon-seed generation run (classify-pipelines, species-effects, affix-authoring, etc.), run the committed preflight and have a real conversation with the owner about anything it can't resolve on its own. Use before "demons generate", "demons classify", or any long unattended seedsmith run.
---

# seedsmith-preflight

**This skill detects nothing.** Every check lives in `tools/seedsmith/seedsmith/adapters/demons/preflight.py` —
committed, CI-visible, testable without this file. This skill's only job is the part a library
cannot do: turning a failed check into a question for the owner, and turning their answer into the
right next command.

Per spec-dump-preflight.md: *"A run that cannot be trusted is more expensive than a run that never
started."* Two long unattended runs in this repo's history produced plausible output from a stale
or partial input, discovered hours later — this skill exists so a third one doesn't happen.

## When to use

Before any `seedsmith demons <generate|classify|threat-band|power-parse>` invocation that will run
unattended for more than a couple of minutes, or before handing a run off to `run-control`
(demon-seed module 9, once built).

## Step 1 — run the real check

```powershell
cd gk-forge/tools/seedsmith
python -m seedsmith demons preflight
```

Read the output. Every failed check prints its own fix command — do not improvise a different fix.

## Step 2 — sort what came back

- **Any `[REFUSE]` line** (checks 3, 4, 6, 8 by design): do not proceed under any circumstance,
  and do not offer to. These fail closed because proceeding produces confidently wrong data with
  no signal it's wrong. Run the named fix command, then re-run preflight from Step 1.
- **Any `[ASK]` line** (checks 1, 2, 5, 7, 9 by design): this is a real decision, not a formality.
  Ask the owner directly, naming the specific check and its observed/expected values:
  - Check 1/2 (dump missing/stale): *"The corpus dump is missing/stale — hash `X` on disk vs `Y`
    in the manifest. Re-export with `DemonCorpusDump`, or is running against the pinned older
    dump intentional?"*
  - Check 5 (model unreachable): *"LM Studio doesn't seem to be answering at the configured
    endpoint. Is it running? Is the model loaded? Is the endpoint in `seedsmith.toml` correct?"*
  - Check 7 (lockfile drift): *"The installed packages don't match `requirements.lock` — N
    mismatches, e.g. `<first mismatch>`. Install from the lock, or is this environment
    intentionally ahead/behind?"*
  - Check 9 (disk headroom): *"Only `X`MB free, below the `Y`MB starting-value threshold. Free
    space, or is this run's expected output known to be small enough to proceed anyway?"*

Never answer these questions yourself and proceed — they exist because the choice is legitimately
the owner's, not because the check couldn't decide.

## Step 3 — never let `--skip-model` reach a real run

`--skip-model` exists only for CI, which has no local model to call. If you find yourself tempted
to pass it so a real generation run can start without LM Studio running, stop — that is exactly the
scenario `run-control` (demon-seed module 9) is built to refuse: a preflight record written with
`skipModel: true` must never authorize a real classification run. Start LM Studio instead, or don't
run yet.

## Step 4 — full pass

A full pass writes `data/seed/demons/_dump/_preflight.json` automatically (the CLI does this, not
this skill). That record is what `run-control` checks the dump against before starting — if the
dump changes after preflight passes but before the run starts, the record goes stale and the next
preflight run will show check 2 failing again.
