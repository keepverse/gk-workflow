# Task: backlog-clean-up BCU8.2 onward — Injector write-path honesty

Program: `tasks/backlog-clean-up-plan.md` / `tasks/backlog-clean-up-todo.md`. Read your rows there.
BCU waves 0 through 3 and BCU8.1 are already merged into `features/mega-merge`. Start from HEAD.

Your next task is **BCU8.2 (Injector write-path honesty)**, then continue down the BCU8 list in the
todo's own order. Do not re-order it.

## What "write-path honesty" means here, so you do not guess

The repo's rule is that combat writes reach Unity only through `EntityStatWriter`, and HP deltas only
through the Funnel to FA10. A write path is *dishonest* when code claims to write a stat that never
reaches a Unity field, or reports success for a write the engine never applied. That is the exact
defect class a 2026-09-13 live probe hid: Hub-bonus grants for atk/maxHp never reached Unity, while
the response said `ok: true`.

So for each item: find what the code claims, check what actually reaches Unity, and make the claim
match the truth — either by wiring the path or by making the failure visible. **Never** make a
report say success for something that did not happen.

## Rules

- `scripts/guard-single-writer.ps1` and `scripts/guard-funnel-delta.ps1` are the boundary. Do not
  add an ad-hoc Unity stat patch to make something work.
- An inert path (a default-off toggle, a null delegate, a debug-only entry point) is a **wiring
  gap**, not an architectural wall. Say "wiring gap" and cite the line, rather than reporting it as
  a limitation.
- One logical change per commit: code + evidence + ledger line.
- Do not run the live game. A separate QA pass owns live proof.

## Verification

- `pwsh -NoProfile -File scripts/guard-single-writer.ps1`
- `pwsh -NoProfile -File scripts/guard-funnel-delta.ps1`
- `pwsh -NoProfile -File scripts/guard-secondary-no-unity.ps1`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Category=BalanceGuard"`

Run them in the FOREGROUND. Never end a turn waiting on your own background job.
On `user-mapped section open`, run `dotnet build-server shutdown` and retry.
