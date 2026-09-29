# Task: strain-splice-host SSH2.7, then continue the SSH2 tail

Program: `tasks/strain-splice-host-plan.md` / `tasks/strain-splice-host-todo.md`.
Spec: the `combination-regen` module spec, section "The helm joins the host set".

SSH2.1 through SSH2.6 are merged into `features/mega-merge`. Start from HEAD.

Your task row is line 122 of the todo:

> **SSH2.7 — `Coverage/HostRoleDiversity` (a report-only reading) and the R11-step preflight** · S · deps: —

Read that row and its spec section before writing anything.

## The one rule this task will try to break

`Coverage` and `HostRoleDiversity` are **readings, not constants**. This repo has a hard rule:

> A guardrail validates the CONTRACT and the closed enums. It never asserts the size of a derived
> population, a per-cycle outcome, or generated text.

So: **print** the coverage and diversity numbers, never assert them. A test that pins today's
host-role diversity guards nothing — it fails the day content ships, and the "fix" is to bump the
number. What you may assert is the envelope: ids unique, every join closes, shares sum to their
expected total, the reading is reproducible from the same input.

The row says "report-only reading" for exactly this reason. Honour it.

SSH5.13 depends on your SSH2.7 and is owner-run, so your preflight is what makes that run possible.
Make the preflight say plainly what it checked and what it could not.

After SSH2.7, continue down the SSH todo in its own order. Do not re-order it and do not start an
`owner` task — those are the owner's to run.

## Rules

- One logical change per commit: code + evidence + ledger line.
- `gk-data/packs/fusion/data/seed/**` entries carrying `_meta.model` are generator OUTPUT. Never hand-edit them to make
  a check pass; fix the generator and regenerate. Registries (`**/_registry/**`) are authored and
  may be edited by hand.
- Re-anchor doc citations in the same commit as any code move that breaks them.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Combination|FullyQualifiedName~Host"`
- `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

Run them in the FOREGROUND. Never end a turn waiting on your own background job.
On `user-mapped section open`, run `dotnet build-server shutdown` and retry.
