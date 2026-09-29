# Lane `dmf2` — DM-F2: gate `/api/sim/effect/*` behind `SimFlags.Enabled`

**Session:** `debug-mcp-f2-20260922` · **Program:** `debug-mcp` (row DM-F2) · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Server/**`, `tests/**`, `tasks/debug-mcp-todo.md`, `tasks/reports/**`

## Goal

The owner ruled 2026-09-22: the unconditional registration of `/api/sim/effect/*` is **drift — gate it**.
`gk-core/src/FusionRpg.Server/Program.cs` registers the sim effect surface unconditionally (~line 2052) while
the rest of the sim surface sits behind `SimFlags.Enabled` (~line 2050). Bring the effect surface under
the same gate.

## Known facts (verified — do not re-investigate)

- The row: `tasks/debug-mcp-todo.md`, **DM-F2** (filed by lane `sim-idea-b`, 2026-09-22).
- The owner answer: `tasks/rpg-simulator-decisions.md`, **F1 → (b) drift, gate it** (owner override).
- Registration site: `gk-core/src/FusionRpg.Server/Program.cs` around lines 2050–2052 — confirm the exact
  lines in your worktree before editing.

## Definition of done

- `/api/sim/effect/*` routes are registered only when `SimFlags.Enabled` is set, same as the rest
  of the sim surface.
- A regression test proves both sides: gate off → effect routes absent (404); gate on → routes serve.
- DM-F2 ticked in `tasks/debug-mcp-todo.md` with the named cause, evidence, and commit SHA.
- One commit: code + test + todo tick together.

## Verification

- `.\scripts\verify-change.ps1 -Paths <every file you changed> -Session debug-mcp-f2-20260922` — expected: exit 0

## Rules that bite here

- RPG layer only; SQL only inside `FusionRpg.Data`; never widen a guard allowlist to make a check pass.
- Generated data is never hand-edited.
- Explicit `git add <paths>`, never `-A`; never push; no watermarks in commit messages.

## Hand-back

- If the effect surface has a legitimate ungated consumer (something that needs it while the sim is
  disabled), STOP and report that as a finding instead of gating — do not break a real caller to
  satisfy the row.
