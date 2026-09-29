# Lane brief — `lawn-1` (program: lawn)

## Program

`lawn` — the playable-lawn program: freshness, the scale foundation and its consumers, and the live proof.
It carries **17 open rows across 5 blocks** at the 2026-09-23 census.

- **Plan:** `tasks/lawn-plan.md` · **Todo:** `tasks/lawn-todo.md` (the authority)
- **Maps:** `docs/architecture/lawn-playable-map.md`, `docs/architecture/lawn-tuning-profile-map.md`
- **Specs:** `docs/architecture/lawn-playable/**`, `docs/architecture/lawn-tuning-profile/**`
- Its blocks, in the todo's own order: *Wave 1 — freshness and the two silent failures* (6 rows) ·
  *Wave 2 — the scale foundation and its two consumers* (6) · *Wave 3 — the two dependents* (2) ·
  *Wave 4 — the live proof and close-out* (2) · one row routed in from `combat-ai` (2026-09-21).

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its lawn rows name,
**in this session**, then verify each claim against code. Code beats docs; docs beat comments.

## Hard rules that bind this program

1. **One ActorHub compose.** Actor combat derived and AppliedCombat compose **once** in `ActorHub` (lawn, sheet,
   battle, delve, siege, sim). Contribute via `IActorStatSubsystem` / registered atom readers, or consume Hub
   output — never a parallel composer. Guard: `scripts/guard-actor-hub.ps1`.
2. **Combat writes go through `EntityStatWriter` / the effect `Funnel`** (`guard-single-writer.ps1`); **HP deltas
   only via Funnel → FA10** (`guard-funnel-delta.ps1`).
3. **No magic numbers on the balance surface** — `data/tuning/lawn-*.v{n}.json`, published through
   `gk-core/tools/tuning/publish.py`, never inline. The program's own `lawn-perf-budget.v1` is the budget's home.
4. **Numeric range is a constraint**: widen before multiplying, integer overflow throws (`checked`), divide by 1000
   last in per-mille math.
5. **Test substrate**: tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it.
6. **The live proof (Wave 4) is a live probe** — it runs against a pooled slot per
   `docs/contributing/live-probe-standard.md`: readiness first, a real operation, and a read-back through the normal
   query path; never a response body alone. If you cannot reach a slot, end the row naming that, do not fake it.
7. **A row you close needs its evidence in the same commit**, the row id asserted present after the tick, and a row
   that ends the segment still open must end naming EXACTLY what blocks it — never "needs investigation".

## Fence (your session paths)

- `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector/**` — the lawn path and its consumers
- `tests/**`
- `docs/architecture/lawn*/**`, `docs/architecture/lawn*.md`, `tasks/lawn-*.md`, `tasks/lawn-ledger.jsonl`
- `data/tuning/lawn*.json` — published only, never edited in place
- `scripts/**` — only what a row you close requires

Anything else is another session's fence — name it as a dependency instead of reaching across.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session lawn-1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-actor-hub.ps1` · `scripts/guard-single-writer.ps1` · `scripts/guard-funnel-delta.ps1` — read the printed verdicts.
- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "<your tests>"` (and the Server/Injector projects when their paths are touched).

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next); every claim in
it must already be a commit in this worktree.
