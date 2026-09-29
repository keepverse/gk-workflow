# Lane `ns-2` — narrative-seed: the remaining rows, NS25 first (it must be redone)

**Session:** `narrative-seed-2` · **Program:** `narrative-seed` · **Mode:** worktree
**Todo:** `tasks/narrative-seed-todo.md` (82 open rows) · **Plan:** `tasks/narrative-seed-plan.md` · **Map:** `docs/architecture/narrative-seed-map.md` · **Ledger:** `tasks/narrative-seed-ledger.jsonl`
**Specs:** `docs/architecture/narrative-seed/**` (the rows cite their own; read the cited one before writing)
**Fence:** `gk-data/packs/fusion/data/seed/narrative/**`, `gk-data/packs/fusion/data/seed/dungeon/events/**`, `gk-forge/tools/seedsmith/**`, `docs/architecture/narrative-seed*/**`, `docs/architecture/decisions.md`, `tasks/narrative-seed-*`, `tests/**`, `scripts/**`
**Protected, granted to this lane:** `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`

## Why this lane exists (and one thing it must redo)

Its predecessor `narrative-seed-1` was retired at segment 50: its session reached **4.39 MB / 1324 lines**
and the provider answered `400 status code (no body)` on **28 consecutive attempts** — the same drain class
as `tvb58` (retired at 4.99 MB the same day). You are spawned with `--rotate-at-tokens`, so the drain
cannot repeat; if a segment ever starts answering 400, say so in your report rather than retrying.

**Lost work, recorded rather than glossed:** the predecessor's ledger said *"NS25 drafts are in the
worktree, UNCOMMITTED (registry, `token_grammar.py`, test): 16 of 22 tests passing"* — and its worktree
holds none of them (its reflog shows only commits, no reset). The drafts are **gone**. **Redo NS25 from
its row's own acceptance list**, which is complete: files `_registry/tokens.v1.json` (new),
`adapters/narrative/token_grammar.py` (new), `gk-forge/tools/seedsmith/tests/test_narrative_token_grammar.py` (new),
plus the `docs/architecture/decisions.md` row; acceptance is the ten named tests on that row
(`parse_accepts_every_form` … `features_are_closed`, and fixtures containing no real name).

## Work — the todo's own order, starting at NS25

Take the rows as the todo lists them, `deps:` respected. The program's shape: registries and readers first
(NS8 gloss registry, NS9 glossed motifs), then the model-backed batches (NS16 gloss batch 1, NS17 the full
pass — NS17 waits on **NSG4**, an owner go after batch 1: do not start it without that), then the
regeneration driver (NS13) and the token grammar / names registry (NS25, NS26).

## Rules

- One logical change per commit: code + its test + the evidence fragment + the ledger line **in the same
  commit**. Tick the row in the same commit and assert the row id is still present after the tick.
- A row you end still open must name **exactly** what blocks it — never "needs investigation".
- Findings outside your fence get a row in the OWNING program's todo in the same commit, with `file:line`
  and the cause you read.
- **Generated data is never hand-edited** — fix the generator, regenerate, commit the diff with the reason.
  `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**` are enforced roots: a new file under one needs its boundary row in
  `gk-core/scripts/verification-boundaries.v1.json` **in the same commit** (TVB-F24: your local `verify-change`
  stays green while the integration guard goes red without it).
- Foreground commands only. **Every segment ends with the report block** — without it the runner restarts
  the segment labelled `report_missing` and burns context for nothing. On `429 GoUsageLimitError`, end the
  segment with your report instead of retrying in a loop.
- Merge `features/mega-merge` freely; a registry conflict is resolved with
  `.claude/cmdc-agents/scripts/union-registry-sides.py` (it unions the merge sides from git and reports
  differences) — never by hand-editing a conflicted registry.

## Verification

- `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <files you changed> -Session narrative-seed-2`
- `python gk-core/scripts/guard-verification-boundaries.py`
- `$SS gk-forge/tools/seedsmith/tests -q` for the touched areas (named test files, not the whole tree) — the
  seedsmith runbook; `test_actions_description_completeness` fails pre-existing on a clean HEAD, so confirm
  a failure already exists before blaming your change.

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

## Evidence contract

The **printed reading**, never an exit code: a pytest line with its counts, a registry's own row count, a
guard's printed verdict. Fragments go under `tasks/evidence-fragments/`.

## Boundaries

Do not widen the fence. Do not touch another session's files. Never commit conflict markers. SQL lives only
in `FusionRpg.Data`. LLMs author identity only — every magnitude is table-owned; `gk-core/data/tuning/**` is
authored but published (`v{n+1}` via `gk-core/tools/tuning/publish.py`), never edited in place.
