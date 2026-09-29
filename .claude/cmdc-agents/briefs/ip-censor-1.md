# Lane `ip-censor-1` — the ip-censor program, rows in order

**Session:** `ip-censor-1` · **Program:** `ip-censor` · **Mode:** worktree
**Fence:** `gk-core/tools/ip-censor/**`, `.github/workflows/ci.yml`, `tests/**`, `docs/architecture/ip-censor/**`,
`tasks/ip-censor-todo.md`, `tasks/reports/**` — `.github/workflows/ci.yml` is granted **because this program's own
T1 owns its CI pytest step**; change nothing else in that file.

## Work

`tasks/ip-censor-todo.md` is the authority. The owner ruled (2026-09-22, recorded in the charter) that this
program gets **implementation lanes** — an architect verifies/reconciles the plan where a gap exists rather than
the program waiting. Take the rows **in dependency order**, one commit each:

- **`T0`** — session record (its own line says it depends on owner approval of the plan; the owner's ruling to
  deploy lanes *is* that approval — record it as the row's evidence rather than stalling).
- **`T1`** — tool package, lockfile, wiring test, CI pytest step (`wiring` half 1). This is the row that touches
  `ci.yml`; keep the edit to the minimum the row names.
- **`T2`** — `source` — the tracked-tree reader.
- Then continue down the list while each row has a clear acceptance.

## Rules

- This program's subject is **detection and reporting**, not silent rewriting: if a row would have you modify
  game files or binaries, stop — that is outside this repo's hard boundaries and outside this fence.
- If a row's premise is stale, say so with the reading and re-scope the row rather than implementing around it.
- ⛔ Never widen a guard or a validator to pass; never add a `knownRed` entry.
- Findings about other programs get a row in *that* program's todo, with the id asserted present.

## Verification

- `python -m pytest gk-core/tools/ip-censor/tests -q` (or the program's own test entry point once T1 names it)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session ip-censor-1`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- one commit per row, naming the row it closes

## Boundaries

- Your session record's `worktree` path must be **ABSOLUTE**.
