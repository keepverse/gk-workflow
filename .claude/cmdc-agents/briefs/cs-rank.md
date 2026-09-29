# Lane `cs-rank` — creature-seed Tasks 1–3 (rank tuning, ladder helpers, seedsmith wiring)

**Session:** `creature-seed-rank` · **Program:** `creature-seed` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-forge/tools/seedsmith/**`, `tests/**`,
`gk-data/packs/fusion/data/seed/creatures/**`, `gk-core/data/tuning/**`, `tasks/creature-seed-todo.md`, `tasks/reports/**`

## Work, in todo order

`tasks/creature-seed-todo.md` is the authority. Take **Tasks 1–3 in order**, one commit each, each with its own
evidence:

1. **Task 1** — rank tuning table + loader validation.
2. **Task 2** — rank enum + ladder helpers + guard test (its acceptance line says it plainly: *tuning validates;
   ladder + guard green; **zero behavior change** — nothing reads rank yet*).
3. **Task 3** — seedsmith derive + runner wiring.

Then continue down the list while the evidence holds. Tick each row with the numbers printed.

## Rules that bind this program

- ⛔ **Generated data is never hand-edited.** `gk-data/packs/fusion/data/seed/creatures/**` and any `_meta`-bearing tree is the OUTPUT
  of a generator: fix the generator (or its tuning/registry input), then regenerate and commit both. If the
  generator cannot express the fix yet, fixing the generator **is** the deliverable.
- ⛔ **No magic numbers on the balance surface.** A number a balance pass would change lives in
  `gk-core/data/tuning/<domain>.v{n}.json` — and tuning is **published** (`gk-core/tools/tuning/publish.py`), never edited in
  place. Readers must move in the same commit (the H7 shape).
- ⛔ Never widen a guard to make a test pass; never add a `knownRed` entry.
- A guardrail validates the **contract and closed enums**, never a population count or generated text — a test
  asserting today's species count guards nothing.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `python -m pytest gk-forge/tools/seedsmith/tests -q` (from `gk-forge/tools/seedsmith`, or with `PYTHONPATH=gk-forge/tools/seedsmith`)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session creature-seed-rank`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- findings routed to the owning todo in the same commit, **with the id asserted present**
- if a red is pre-existing, say so with the evidence that proves it predates you

## Boundaries

- Do not edit another lane's files; `tasks/**` is shared, so name your artifacts uniquely.
- Your session record's `worktree` path must be **ABSOLUTE**.
