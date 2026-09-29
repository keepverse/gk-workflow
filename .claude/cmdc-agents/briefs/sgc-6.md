# Lane `sgc-6` — species-gear-chain: the two ruled rows, then the workable remainder

**Session:** `species-gear-chain-6` · **Program:** `species-gear-chain` · **Mode:** worktree
**Todo:** `tasks/species-gear-chain-todo.md`
**Plan / map / specs:** this program's own `tasks/species-gear-chain-plan.md`, `docs/architecture/species-gear-chain*/**` (the rows cite their spec sections — read the cited one before writing)
**Fence:** `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `gk-forge/tools/seedsmith/**`, `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `tests/**`, `scripts/**`, `docs/architecture/species-gear-chain*/**`, `tasks/species-gear-chain-*`
**Protected, granted to this lane:** `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`

## Why this lane exists

At the 2026-09-23 reading of `.claude/cmdc-agents/scripts/convergence-census.py` (the t1 contract's own
instrument — run it yourself rather than trusting this number) `species-gear-chain` carries **26 open task
blocks** and has no lane. A measurement of its open rows splits them honestly: **263 workable**, only **3**
owner-gated — and two of those three were ruled by the owner on 2026-09-23, so they are now work with a
decided shape. Take them first; they are the program's blocking edge.

## Work, in this order

1. **SGC5-F1 — track a minimal fixture** (owner ruling, 2026-09-23; recorded in the todo). Six seedsmith
   tests need `data/seed/actions/_candidates/`, which `.gitignore:113` ignores, so they fail in every fresh
   checkout (`python -m pytest gk-forge/tools/seedsmith/tests/test_usage_stats.py
   gk-forge/tools/seedsmith/tests/test_general_propose.py -q` → 6 failed, measured 2026-09-22). Commit the
   worked-example brief/answer pair — or a minimal fixture — to a **tracked** path and remove the
   dependency. ⛔ **Not** a `knownRed` row (the repo's standing rule against it), ⛔ **not** a skip for
   absent runtime state (that is exactly what the audit flags as `Skip`). Acceptance: both test files pass
   on a clean checkout, fixture committed in the same commit.
2. **SGC5-F2 — regenerate the actions corpus** (owner ruling, 2026-09-23). `gk-data/packs/fusion/data/seed/actions/authored-basics.json`'s
   `act.attack` names `atom.fx-overlay-damage`, which no longer exists, and the domain loader refuses it by
   name (`[GAP] Actions/Loader …`), leaving `python -m pytest gk-forge/tools/seedsmith/tests/test_cli.py
   gk-forge/tools/seedsmith/tests/test_corpus_loader.py -q` at 2 failed. Re-run the generator
   (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/**`) so the corpus derives from the registry that exists
   now; commit the regenerated diff **with the reason**. ⛔ **Not** "restore the family" — it was retired
   deliberately. Generated content is never hand-edited.
3. **The remaining workable rows, in the todo's own order.** `T37` is already ruled ("author the
   per-base-type edges" — 2026-09-21) so it is work, not a question. Work the rows the todo lists; where a
   row genuinely needs a mapping or a boundary that does not exist, add it in the same commit (see TVB-F24
   below) rather than leaving the row open on it.

## Rules

- One logical change per commit: code + its test + the evidence fragment + the ledger line
  (`tasks/species-gear-chain-ledger.jsonl`) **in the same commit**.
- Tick the row in the same commit and assert the row id is still present after the tick.
- A row you end still open must name **exactly** what blocks it — never "needs investigation".
- Findings outside your fence get a row in the OWNING program's todo in the same commit, with `file:line`
  and the cause you read.
- **Generated data is never hand-edited** — fix the generator, regenerate, commit the diff with the reason.
  `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**` are enforced roots: a new file under one needs its boundary row in
  `gk-core/scripts/verification-boundaries.v1.json` in the same commit, or the integration guard goes red while your
  local `verify-change` stays green (TVB-F24).
- Foreground commands only. **Every segment ends with the report block** — without it the runner restarts
  the segment labelled `report_missing` and burns its context for nothing. On `429 GoUsageLimitError`, end
  the segment with your report instead of retrying in a loop.
- Merge `features/mega-merge` freely; a registry conflict is resolved with
  `.claude/cmdc-agents/scripts/union-registry-sides.py` (it unions the merge sides from git and reports
  differences) — never by hand-editing a conflicted registry.

## Verification

- `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <files you changed> -Session species-gear-chain-6`
- `python gk-core/scripts/guard-verification-boundaries.py`
- `$SS gk-forge/tools/seedsmith/tests -q` for the touched areas (named test files, not the whole tree) — the
  seedsmith skill's runbook; `test_actions_description_completeness` fails pre-existing on a clean HEAD, so
  confirm a failure already exists before blaming your change.
- the two ruled rows' own acceptance commands, above

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

## Evidence contract

The **printed reading**, never an exit code: a pytest line with its counts, a seedsmith check's findings
line, a regenerated corpus's file count, a guard's printed verdict. Fragments go under
`tasks/evidence-fragments/`.

## Boundaries

Do not widen the fence. Do not touch another session's files. Never commit conflict markers. SQL lives only
in `FusionRpg.Data`; combat writes go through `EntityStatWriter`/Funnel; a level-derived number goes through
the power ladder; no magic numbers on the balance surface (`gk-core/data/tuning/<domain>.v{n}.json`, published
`v{n+1}` via `gk-core/tools/tuning/publish.py`).
