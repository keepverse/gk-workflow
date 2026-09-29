# Lane `pd-d3` — party-dungeon: finish the D3.x partials

**Session:** `party-dungeon-d3` · **Program:** `party-dungeon` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `tests/**`,
`docs/architecture/party-dungeon/**`, `tasks/party-dungeon-todo.md`, `tasks/reports/**`

## Work

`tasks/party-dungeon-todo.md` is the authority, and its rows are unusually well-documented — each carries what is
already built, what is not, and the exact reading that established it. Take them **one at a time, in todo order**,
and finish each to its acceptance:

- **`D2.16`** — freeze, resume and the SignalR surface: the live HTTP+SignalR wiring is **built** (2026-09-08);
  verify its acceptance and close it, or name precisely what is unmet.
- **`D3.3`** — `EventDeck.Build` / `Resolve` / `Answer` and the streams (partially built, re-scoped twice — read
  the row's own corrections before writing code).
- **`D3.5`** — `OutcomeResolver` (dispatch table + forced-outcome path recorded as built; find what remains).
- **`D3.9`** — store, endpoint, preflight and validator rules (rules added across two dates; one later retracted).

Then continue down the list while each row still has a clear acceptance.

## Why these rows are trustworthy starting points

They were written by lanes that measured the tree rather than recalled it, and several carry their own
corrections ("RE-SCOPED", "corrected same day", "later retracted"). **Read the whole row before acting on its
title** — a row's headline can be older than its body, and this todo is where that habit is most rewarded.

## Rules

- Findings about **other** programs (a Core rule, a boot concern, a spec gap) get a row in *that* program's todo,
  with the id asserted present — never only a mention in a report.
- ⛔ Never widen a guard or a validator to make a test pass; never add a `knownRed` entry.
- Do not hand-edit generated data; publish tuning as `v{n+1}` rather than editing in place.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet` (when a store path is touched)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session party-dungeon-d3`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- one commit per row (or per coherent increment), each naming the row it closes
- if a red is pre-existing, prove it predates you rather than assuming it

## Boundaries

- Your session record's `worktree` path must be **ABSOLUTE**.
