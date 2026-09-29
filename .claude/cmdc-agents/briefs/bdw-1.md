# Lane brief — `bdw-1` (program: battle-derived-wire)

## Program

`battle-derived-wire` — the wiring that makes battle consume the same derived combat path the rest of the game
does. It is one of the largest genuinely-open programs in the repo (19 open task blocks / 86 open rows at the
2026-09-23 census).

- **Plan:** `tasks/battle-derived-wire-plan.md` · **Todo:** `tasks/battle-derived-wire-todo.md` (the authority).
- Its own opening rows name the shape: *Task 0 — count what battle's effect path actually carries · Task 1 — install
  `OverlayCombatMath` on battle's `EffectBag` (W1) · Task 2 — supply `ActorResolve` and route battle HP through the
  reflect step (W2, W3) · Task 3 — make `resource.restore.hp` reach battle heals (W13) · Task 4 — give
  `BattleActorSetup.ActiveAuras` a production producer (W7)*.

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its battle/combat rows
name, **in this session**, then verify each claim against code. Code beats docs; docs beat comments.

## Why this program is dangerous, and why the rules below are not optional

This is the seam where a second combat composer has already been built once and had to be deleted
(`BattleStatComposer`, fused 2026-09-13). Every row here risks recreating it. **Task 0 is the discipline**: measure
what the path carries *before* wiring anything, and report the reading — a count you have not reproduced is not
evidence.

## Hard rules that bind this program specifically

1. **One ActorHub compose.** Actor combat derived and AppliedCombat compose **once** in `ActorHub` (lawn, sheet,
   battle, delve, siege, sim). Contribute through `IActorStatSubsystem` / registered atom readers, or consume Hub
   output. Never a parallel composer. Guard: `scripts/guard-actor-hub.ps1`.
2. **Combat writes go through `EntityStatWriter` / the effect `Funnel`** — no ad-hoc Unity or stat patches. Guard:
   `scripts/guard-single-writer.ps1`.
3. **HP deltas only via Funnel → FA10.** Guard: `scripts/guard-funnel-delta.ps1`.
4. **SQL only inside `FusionRpg.Data`.** Guard: `scripts/guard-dal.ps1`.
5. **Test substrate:** tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it.
6. **No magic numbers on the balance surface** — `gk-core/data/tuning/<domain>.v{n}.json`, published through
   `gk-core/tools/tuning/publish.py`, never inline.
7. **A row you close needs its evidence in the same commit**, the row id asserted present after the tick, and a row
   that ends the segment still open must end naming EXACTLY what blocks it (a path outside your fence, an owner
   ruling, or a named dependency row) — never "needs investigation".

## Fence (your session paths)

- `gk-core/src/FusionRpg.Core/**` — the battle/effect path
- `gk-core/src/FusionRpg.Server/**` — `BattleActorSetup` and the server-side battle wiring
- `tests/**` — the tests that prove each row
- `docs/architecture/battle*/**`, `docs/architecture/combat*/**`, `tasks/battle-derived-wire-*`
- `gk-core/data/tuning/*.json` — published only, never edited in place
- `scripts/**` — only what a row you close requires

Anything else is another session's fence — name it as a dependency instead of reaching across.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session bdw-1`
- The four guards named above (`guard-actor-hub`, `guard-single-writer`, `guard-funnel-delta`, `guard-dal`) — read their printed verdicts.
- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "<your tests>"`, plus the Server project when its paths are touched.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next); every claim in
it must already be a commit in this worktree.
