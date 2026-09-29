# Lane `identity-rename-1` — the identity-rename program, rows in order

**Session:** `identity-rename-1` · **Program:** `identity-rename` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `gk-core/src/FusionRpg.Contracts/**`,
`tools/**`, `tests/**`, `docs/architecture/identity-rename/**`, `tasks/identity-rename-todo.md`, `tasks/reports/**`

## Work

`tasks/identity-rename-todo.md` is the authority. The owner ruled (2026-09-22, recorded in the charter) that this
program gets **implementation lanes** — an architect verifies/reconciles the plan where a gap exists, rather than
the program waiting. Take the rows **in dependency order**, one commit each:

- **`T0`** — session record and boundaries for the unmapped front pages (do this first; it is the row that makes
  the rest safe to touch).
- **`T1`** — names registry and its C# parser. ⚠ It declares an **external dependency on `narrative-seed` plan
  D1**: if that input does not exist yet, say so as a finding and take the next row rather than inventing it.
- **`T2`** — the server loads the registry.
- Then continue down the list while each row has a clear acceptance.

## Rules

- If a row's premise is stale (the code already does it, or the file it names has moved), **say so with the
  reading** and re-scope the row rather than implementing around it — this program's own plan is the thing most
  likely to have drifted.
- Findings about other programs get a row in *that* program's todo, with the id asserted present.
- ⛔ Never widen a guard or a validator to pass; never add a `knownRed` entry; never hand-edit generated data;
  publish tuning as `v{n+1}` rather than editing in place.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --verbosity quiet` (when a server path is touched)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session identity-rename-1`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- one commit per row, naming the row it closes

## Boundaries

- Your session record's `worktree` path must be **ABSOLUTE**.
