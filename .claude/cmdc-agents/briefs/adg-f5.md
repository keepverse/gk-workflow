# Lane `adg-f5` — the unlock roll offers actions it can never grant, and throws instead of skipping them

**Session:** `adg-f5` · **Program:** `action-distribution-gaps` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Core/Actions/**`, `gk-core/src/FusionRpg.Server/**`, `tests/**`,
`tasks/action-distribution-gaps-todo.md`, `tasks/reports/**`

## The defect — found while fixing ADG-F4, measured, do not re-derive it

Row **`ADG-F5`** in `tasks/action-distribution-gaps-todo.md` (line ~293):

- `ActionUnlockGrantService.TryRollOnce` (`gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:56-93`)
  draws the action a level-up offers from the **whole catalog of the store it awards XP on**, filtered only by
  already-held ids — never by `Grantable` / `Kind`.
- `ActionValidator.ValidateGrant` (`gk-core/src/FusionRpg.Core/Actions/ActionValidator.cs:83`) refuses every `Basic` **by
  construction**, so the grant throws and the XP award's transaction **rolls the level-up back**.
- `Program.cs:644` imports `authored-basics.json` on every real boot, so a live level-up is one unlucky roll away
  from this.

`ADG-F4` fixed only the *test* that surfaced it (the E2E test now owns its store); the production half is yours.

## Why it matters

A player's level-up can silently vanish — the XP is awarded, the grant throws, and the transaction discards the
whole award. "The candidate list contained something un-grantable" should be an **outcome**, never a throw.

## Deliverable

1. **The fix at the responsible layer**: the roll must not offer a candidate it cannot grant. Decide *where* the
   filter belongs — the query/delegate that supplies candidates, or the service — and say why that layer, by
   `file:line`. `ActionValidator` stays the authority on what is grantable; do not weaken it, and do not add a
   second definition of "grantable" that can drift from it.
2. **What happens when the candidate set is empty** — say it explicitly and make it an outcome (no throw that
   discards a level-up).
3. **A regression proof**: a test through the real path showing that a store whose catalog contains a Basic still
   awards the level-up, and that the roll never returns an un-grantable action. The strongest form drives the real
   `ActionUnlockGrantService` against a real store.
4. **Check the sibling rows** (`ADG-F1`..`ADG-F4`) are not re-opened by your change; tick `ADG-F5` with evidence.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` (the unlock path has E2E coverage)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session adg-f5`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- findings routed to the owning todo in the same commit, **with the id asserted present**
- if a red is pre-existing, prove it predates you

## Boundaries

- ⛔ Never widen a validator or a guard to make a test pass; never add a `knownRed` entry.
- No magic numbers on the balance surface — a number a balance pass would change belongs in
  `gk-core/data/tuning/<domain>.v{n}.json`, published as `v{n+1}` with its readers in the same commit.
- Your session record's `worktree` path must be **ABSOLUTE**.
