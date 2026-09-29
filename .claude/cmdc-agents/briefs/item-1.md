# Lane brief — `item-1` (program: item — the item system)

## Program

`item` — the item system: schema, logic, tests and the surface that proves each slice, together. It is the
**largest genuinely-open program in the repo** (39 open task blocks / 132 open rows at the 2026-09-23 census,
checkpoints excluded and after discounting the programs whose boxes a header closes).

- **Plan:** `tasks/item-plan.md` · **Specs:** `docs/architecture/item/` · **Rulings D1–D35:**
  `docs/architecture/item-ideal.md` · **Todo:** `tasks/item-todo.md` (10,124 lines — the authority).
- The todo's own rule: *"Each task is a **vertical slice** — schema, logic, tests and the surface that proves it,
  together. No task is done until its verification command is green."* Keep that shape.

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its item rows name,
**in this session**, then verify each claim against code. Code beats docs; docs beat comments. A comment is not
evidence.

## What is NOT yours (name it, do not run it)

Three Phase-0 rows are **corpus-scale model runs**, which this repo runs as manager-run detached jobs, never inside
a lane — and one is an owner row:

- **P0.1** — an accept-or-decline on every external dependency: an **owner** row. Name it, do not wait on it.
- **P0.2** (`seedsmith theme-refresh`), **P0.4** (`X1 frame-classify`), **P0.5** (the one regeneration pass:
  `core.v1.json` v2 + `classes.v1.json` v4) — **manager jobs**. Report them as such; do not spend model time.

Everything else in the todo is yours, in the todo's own order.

## The work

Work the open blocks in order. Two traps this repo has already paid for, both live in a todo this size:

1. **A block titled `✅ … BUILT AND VERIFIED` with one or two unchecked boxes is usually SHIPPED.** Before you
   "finish" such a block, read its boxes: if they are acceptance details of work that already landed, close the
   block by recording *where* it landed (commit + test + reading) rather than re-implementing it. If they are real
   remaining work, do it.
2. **A row that ends the segment still open must end naming EXACTLY what blocks it** — a path outside your fence,
   a specific owner ruling, or a named dependency row. "Needs investigation" is a failed segment.

## Fence (your session paths)

- `gk-core/src/FusionRpg.Core/**` — the item domain
- `gk-core/src/FusionRpg.Data/**` — item stores/schema
- `gk-core/src/FusionRpg.Server/**` — item endpoints/surfaces
- `gk-core/src/FusionRpg.Contracts/**` — item DTOs
- `gk-web/web/fusion-rpg-web/**` — the item surfaces
- `docs/architecture/item/**`, `docs/architecture/item-*.md`, `tasks/item-*.md`, `tasks/item-ledger.jsonl`
- `data/tuning/item*.json` — **publish `v{n+1}` through `gk-core/tools/tuning/publish.py`, never edit in place**
- `gk-data/packs/fusion/data/seed/items/**` — **generator-owned: never hand-edit** (see the hard rule below)
- `scripts/**` — only what a row you close requires

Anything else is another session's fence — name it as a dependency instead of reaching across.

## Hard rules

1. **Generated seed data is never hand-edited — fix the generator and regenerate.** `gk-data/packs/fusion/data/seed/items/**` entries
   carry generator provenance (`_meta.model` / `promptVersion` / `batch`); editing one by hand forks the corpus from
   its generator and the next run reverts you. Change the generator/registry/tuning, regenerate, commit the diff.
2. **A guardrail validates the CONTRACT and closed enums — never a population count or generated text.** Never
   "fix" a failing count by bumping a number.
3. **No magic numbers on the balance surface** — `gk-core/data/tuning/<domain>.v{n}.json`, published, never inline.
4. **Numeric range is a constraint**: widen before multiplying, integer overflow throws (`checked`), divide by 1000
   last in per-mille math.
5. **Test substrate:** tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it (a `tests/**` file
   constructing a file-backed store carries `[Trait("Category","DiskSemantics")]` — tag only what genuinely tests files).
6. **One ActorHub compose** — contribute via `IActorStatSubsystem` / registered atom readers, never a parallel composer.
7. **SQL only inside `FusionRpg.Data`** (`scripts/guard-dal.ps1`).
8. **A row you close needs its evidence in the same commit**, and the row id asserted present after the edit.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session item-1`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "<your tests>"` (and the Data/Server projects when those paths are touched).
- `cd gk-web/web/fusion-rpg-web; npm test` and `npm run build` when an item surface changes.
- `python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` after any regeneration.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next); every claim in
it must already be a commit in this worktree.
