# Lane `npc-story-events-1` — the npc-story-events program, rows in dependency order

**Session:** `npc-story-events-1` · **Program:** `npc-story-events` · **Mode:** worktree
**Fence:** `src/**`, `tools/**`, `tests/**`, `gk-data/packs/fusion/data/seed/**`, `docs/architecture/npc-story-events/**`,
`tasks/npc-story-events-todo.md`, `tasks/reports/**`

## Work

`tasks/npc-story-events-todo.md` is the authority — it is the **largest open program in the repo** (105 open task
blocks at the last census). The owner ruled (2026-09-22, recorded in the charter) that it gets **implementation
lanes**, with the plan verified/reconciled by an architect where a gap exists. Take the rows **in dependency
order**, one commit each:

- **`NR0.1`** — session record. Its own text says it depends on *owner approval of the plan*: the owner's ruling to
  deploy implementation lanes **is** that approval — record the ruling as the row's evidence rather than stalling.
- **`NR0.2`** — focused verification boundaries.
- **`NR1.1`** — runtime-only closed vocabularies and structural bounds.
- Then continue down the list while each row has a clear acceptance.

⚠ The owner's ruling also says **Phase 7 needs the idea-ui architect**. When you reach a row whose design does not
exist yet, that is a finding to report with a sharpened question — **not** an invitation to invent a design and
implement it.

## Rules

- If a row's premise is stale (the code already does it, or the file it names has moved), say so with the reading
  and re-scope the row rather than implementing around it.
- Findings about other programs get a row in *that* program's todo, with the id asserted present.
- ⛔ Never widen a guard or a validator to pass; never add a `knownRed` entry; never hand-edit generated data;
  publish tuning as `v{n+1}` rather than editing in place.
- A guardrail validates the contract and closed enums — never a population count or authored prose.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --verbosity quiet` (when a server path is touched)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session npc-story-events-1`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- one commit per row, naming the row it closes
- if a red is pre-existing, prove it predates you

## Boundaries

- Your session record's `worktree` path must be **ABSOLUTE**.
