# Lane `sgc-5` — species-gear-chain: the remaining open task blocks

**Session:** `species-gear-chain-5` · **Program:** `species-gear-chain` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `gk-forge/tools/seedsmith/**`,
`gk-data/packs/fusion/data/seed/items/**`, `gk-core/data/tuning/**`, `tests/**`, `docs/architecture/species-gear-chain/**`,
`tasks/species-gear-chain-todo.md`, `tasks/reports/**`

## Work

`tasks/species-gear-chain-todo.md` is the authority: **28 open task blocks** (the "283 open lines" a line-count
would report are acceptance checkboxes inside finished blocks — measure blocks, never lines). Take the open
blocks **in the todo's order**, one commit each.

**Start with the `T49` family**, which the previous lane left with a precise diagnosis: the spec
(`spec-craft-assurance.md` Design 7) requires the gamble column to carry **success chance, downgrade risk and
craft wear**, while the shipped `CraftAssuranceHorizonReport` computes only the first — its own doc comment
admitted it. That is a real gap with a named instrument, and the lane's finding is the row's evidence.

## Rules that bind this program

- ⛔ **Generated data is never hand-edited** — `gk-data/packs/fusion/data/seed/items/**` is seedsmith's output: fix the generator (or
  its brief/quota/registry input), then regenerate and commit both. If the generator cannot express the fix,
  fixing the generator **is** the deliverable.
- ⛔ **No magic numbers on the balance surface** — a number a balance pass would change lives in
  `gk-core/data/tuning/<domain>.v{n}.json`, **published** (`gk-core/tools/tuning/publish.py`), never edited in place, with its
  readers in the same commit (the H7 shape).
- ⛔ Never widen a guard or a validator to pass; never add a `knownRed` entry.
- A guardrail validates the **contract and closed enums**, never a population count or authored text.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet`
- `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet` (when a store path is touched)
- `python -m pytest gk-forge/tools/seedsmith/tests -q` (when the generator moves)
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session species-gear-chain-5`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- one commit per block, naming the row it closes
- findings routed to the owning todo in the same commit, **with the id asserted present**

## Boundaries

- Rows whose heading names an **owner ruling** are not yours to close: sharpen the question to one line with the
  evidence on both sides and leave them open.
- Your session record's `worktree` path must be **ABSOLUTE**.
