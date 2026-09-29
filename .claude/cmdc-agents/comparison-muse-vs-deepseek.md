# Model comparison: Muse Spark 1.3 contributor (xhigh) vs DeepSeek v4.1 Flash (default effort)

Owner experiment, 2026-09-19. Question: which model is the better long-run implementer for work
that already has solid specs and plans?

## Controlled

Both workers run the same lane (summoner-convergence lane A) with the same pipeline:

- the same ledger, queue, session record, rules digest, guard hook and audit;
- the same brief shape and verification;
- the same manager review process, which runs my own falsifier for every done task;
- one cmdc session per worker for its whole run (no context rotation, per the owner ruling).

The tasks differ: Muse did ST1.x, STCP1 and AE1.1; DeepSeek continues from AE1.2. The per-task
figures below are normalised by task size, where S/M/XS comes from the todo.

## Numbers (from runner logs, git and manager review; nothing self-reported)

| Metric | Muse xhigh (`lane-a`) | DeepSeek default (`lane-a-ds`) |
|---|---|---|
| Tasks done (sizes) | 5: ST1.1 M, ST1.2 S, ST1.3 XS, STCP1 checkpoint, AE1.1 S | |
| Turns per done task | 78.8 (394 turns in total) | |
| Input tokens per done task | 46.2M (231M total, 86% cache reads) | |
| Output tokens per done task | 68k (340k total) | |
| Wall time per done task | about 1 h (setup ~2026-09-18 22:26 to handover 00:58) | |
| Manager corrections (steers and reopens) per task | 7 steers / 5 tasks; 1 reopen (ST1.2) | |
| False done-claims | 1 (ST1.2 test asserted the opposite) | |
| Commit-rule violations | 3 (ST1.1, ST1.2 batch, AE1.1: audit FAIL) | |
| Audit FAIL / WARN | 1 FAIL (AE1.1 done-without-commit); WARNs fixed | |
| Guard denials | 0 | |
| Falsifier result on main after merge | all green: Data 21/21, Core 54/54, server build 0 errors, Golden+Parity 18/18 | |
| Cost ($, from the Command Code dashboard) | | |

## Muse baseline notes (to 2026-09-19)

- ST1.1: done, then corrected (no commit; a worktree-only failure mislabelled as "pre-existing";
  a placeholder in the evidence).
- ST1.2: false done-claim (the test asserted the opposite of the acceptance), reopened and fixed.
- ST1.3, STCP1: accepted first time.
- Context re-sent per request grew to about 770k tokens; about $0.002 per request (cached).

## Decision rule (fixed 2026-09-19, before the DeepSeek result is known)

The owner delegated the choice ("the two models cost about the same; decide from the data, not
without a reason"). The rule is fixed in advance so the data decides, not an impression.

**When:** after DeepSeek has at least 4 done tasks, at least one of them M-sized or an H1 re-bless
(for example AE1.4 or AE1.5), so the sample includes hard work and not only small tasks.

**Order of criteria.** A higher criterion decides; lower ones only break ties:

1. **Defects that escaped the worker**, per done task: false done-claims, wrong numbers, tests that
   do not test the acceptance, and defects found later by anyone. These cost the most, because they
   reach review or main.
2. **Rule violations**, per done task: commit-rule breaks, red commits, spec departures without a
   ruling, guard probing or bypass attempts, retroactive ledger lines.
3. **Manager interventions**, per done task: blocking stops, reopens, corrective steers.
4. **Cost**, per done task: input tokens (they count against usage limits), then turns.
5. **Wall time** per done task.

A criterion counts as a win only if the gap is clear: at least 1.5× on a rate, or a difference of
at least 1 event per 3 tasks. Otherwise it is a tie and the next criterion decides.

**Output:** the default `coder` model in `profiles.json`, with the numbers that decided it, and
the other model kept as a named alternative profile.

## Running tally (DeepSeek, from AE1.2)

| Task | Size | Escaped defects | Rule violations | Interventions | Input tokens | Notes |
|---|---|---|---|---|---|---|
| AE1.2 | S | 0 | 0 | 0 | ~5.5M | clean; committed before done |
| AE1.3 | S | 0 | 1 (retroactive `started`) | 0 | (in segment totals) | genuine evidence |
| AE1.4 | S | in progress | 3 (red commit; spec departure without a ruling; guard probing) | 2 (unblock + probing stop; the ruling) | | found Muse's 1000x AE1.1 defect (credit) |

Muse final (5 tasks): escaped defects 2 (ST1.2 false test; the AE1.1 1000x found later); rule
violations 3 (commits) + 1 (mislabelled pre-existing failure); interventions 7 steers and 1 reopen;
46.2M input tokens per task.

## Verdict (2026-09-19 ~02:37, rule condition met: DeepSeek 6 done tasks including the AE1.5 H1 re-bless)

| # | Criterion | Muse xhigh (5 tasks) | DeepSeek default (6 tasks) | Winner |
|---|---|---|---|---|
| 1 | Escaped defects per task | 2 (ST1.2 false test; AE1.1 x1000) = 0.40 | 0 (full Core 14159/14159 on merged main) | **DeepSeek (decides)** |
| 2 | Rule violations per task | 4/5 = 0.80 | 7/6 = 1.17 | Muse (not reached: criterion 1 decided) |
| 3 | Interventions per task | 8/5 = 1.60 | 7/6 = 1.17 (one was the manager's own wrong steer) | tie (<1.5x) |
| 4 | Input tokens per task | 46.2M | 8.4M | DeepSeek (5.5x) |
| 5 | Turns per task | 78.8 | 28.2 | DeepSeek (2.8x) |

**Decision: DeepSeek v4.1 Flash (default effort) is the default `coder`.** Muse stays available as
`coder-muse`.

**Caveats.** The samples are small, and the tasks differ: Muse had ST1.x and AE1.1, DeepSeek had
AE1.2 to AE1.6 and AECP1. DeepSeek's session is younger, so its context and cost per task will
rise. Its rule discipline is weaker; the guard hook, audit v1.2 and runner auto-continue now
enforce that structurally rather than relying on the prompt.

**Re-check:** after the next 10 DeepSeek tasks, re-apply the same rule. If DeepSeek's escaped
defects per task rise above Muse's 0.40, switch back.

## Post-verdict tally (running, for the 10-task re-check)

| Date | Model | Event | Counts as |
|---|---|---|---|
| 2026-09-19 | Muse (AE1.1, `08ac65ef`) | `ActionBaseTuningHub` added without configuring it in Server.Tests; 18 Server.Tests failures were adopted as a "baseline" until DeepSeek traced them during ST4.5c | escaped defect (Muse now 3 / 5 tasks = 0.60). The manager's acceptance of the number is a process miss, logged in retro |
| 2026-09-19 | DeepSeek (ST3.5) | closed done with the core criterion unproven (analysis was correct) | rule violation, not escaped (caught at review) |
| 2026-09-19 | DeepSeek (ST4.5a, ST4.5c) | found two real shipped defects no test caught (empty published action catalog via missing copy rule, found by the manager live; every triggered atom priced 0) and traced the Server.Tests "baseline" to its cause | credit |
