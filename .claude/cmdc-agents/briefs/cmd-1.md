# Lane brief — `cmd-1` (program: combat-math-dedup)

## Program

`combat-math-dedup` — de-duplicating combat math so each rule is declared **once**. It is one of the largest
genuinely-open untended programs in the repo (8 open task blocks / 41 open rows at the 2026-09-23 census).

- **Plan:** `tasks/combat-math-dedup-plan.md` · **Todo:** `tasks/combat-math-dedup-todo.md` (the authority).
- Its rows name the shape, each with the ruling it implements:
  *Task 1 — Status id → L2b category is declared once (D1) · Task 2 — one element-enum → element-id switch (D2) ·
  Task 3 — the siege kill estimate uses the shipped defense shape (D4) · Task 4 — one reflect rate/share formula,
  and G7 becomes a real guard (D3) · Task 5 — CombatSim gets a verification boundary, and one `Phi` (D7) ·
  Task 6 — CombatSim's per-swing mixture calls `StrikeMixture` (D5)*.

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its combat rows name,
**in this session**, then verify each claim against code. Code beats docs; docs beat comments.

## What this program is really for

Every row is the same defect class: **a rule written in two places, where the two copies can drift**. The
acceptance is therefore never "the number matches today" — it is that the second copy is *gone* and the surviving
one is the one both callers read. When you close a row, say which copy you removed and which single declaration now
serves both callers, and name any caller you had to leave (with the reason).

## Hard rules that bind this program specifically

1. **One ActorHub compose.** Actor combat derived and AppliedCombat compose **once** in `ActorHub`. Contribute via
   `IActorStatSubsystem` / registered atom readers, or consume Hub output — never a parallel composer.
   Guard: `scripts/guard-actor-hub.ps1`.
2. **Combat writes go through `EntityStatWriter` / the effect `Funnel`** (`guard-single-writer.ps1`), and **HP deltas
   only via Funnel → FA10** (`guard-funnel-delta.ps1`).
3. **Task 4's G7 must become a guard that bites on a planted violation** — a rule never seen to fail is not known to
   work. Wire it the way every other guard is wired (its tier in `scripts/run-guards.ps1`, its row in
   `gk-core/scripts/enforcement-registry.v1.json`) and prove it with a case in `gk-core/tests/FusionRpg.Guard.Tests`.
4. **No magic numbers on the balance surface** — `gk-core/data/tuning/<domain>.v{n}.json`, published through
   `gk-core/tools/tuning/publish.py`, never inline. **Numeric range is a constraint**: widen before multiplying, integer
   overflow throws (`checked`), divide by 1000 last in per-mille math.
5. **Test substrate**: tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it.
6. **A row you close needs its evidence in the same commit**, the row id asserted present after the tick, and a row
   that ends the segment still open must end naming EXACTLY what blocks it — never "needs investigation".

## Fence (your session paths)

- `gk-core/src/FusionRpg.Core/**` — the combat math
- `gk-core/src/FusionRpg.Server/**` — server-side combat surfaces
- `tests/**` — the tests and the guard case
- `docs/architecture/combat*/**`, `docs/architecture/*combat*`, `tasks/combat-math-dedup-*`
- `gk-core/data/tuning/*.json` — published only, never edited in place
- `scripts/**` — only what a row you close requires

Anything else is another session's fence — name it as a dependency instead of reaching across.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session cmd-1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-actor-hub.ps1` · `scripts/guard-single-writer.ps1` · `scripts/guard-funnel-delta.ps1` — read the printed verdicts.
- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "<your tests>"` (and the Guard project for the new case).

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next); every claim in
it must already be a commit in this worktree.
