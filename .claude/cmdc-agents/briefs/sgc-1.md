# Lane: species-gear-chain, wave 1 (the biggest anchor — 287 open rows)

Program: `tasks/species-gear-chain-anchor.md` (read it first), plan `tasks/species-gear-chain-plan.md`,
todo `tasks/species-gear-chain-todo.md`. Map `docs/architecture/species-gear-chain-map.md`, specs in
`docs/architecture/species-gear-chain/`. Read `.claude/cmdc-agents/rules.md` before writing anything.

**First action:** if `features/mega-merge` is not an ancestor of your HEAD, merge it
(`git merge --no-ff features/mega-merge`). Then run
`python gk-core/scripts/anchor-ledger.py tasks/species-gear-chain-ledger.jsonl resume` — it prints your queue,
what is done, what is blocked and the concrete next item. Work the todo's own wave order, starting with
**Wave 0 (fix-first)**; do not re-order rows to suit yourself, and do not skip a row's dependencies.

**Scope you must respect (this is the whole point of the anchor).** 287 open rows is more than one
context window: work row by row, commit after each, and let `resume` carry you across windows. Never
batch-close rows. A row you cannot finish stays open with its blocker named in the ledger, not ticked.

**Three rules that bind this program harder than most:**
1. **Generated data is never hand-edited.** `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**` and
   `gk-data/packs/fusion/data/seed/atoms/generated/**` are generator output: change the generator (or its tuning) and
   regenerate, then commit the diff. The generators are `tools/*Gen` and seedsmith under
   `gk-forge/tools/seedsmith`.
2. **Tuning is published, never edited in place.** `gk-core/tools/tuning/publish.py` → `v{n+1}`, and where a
   file has more than one host reader the reader switch lands in the SAME commit as the publish (H7).
3. **A golden that moves needs the one cause in its own commit** (H1). If your change moves a battle
   golden and you cannot name the single cause, stop and report it — do not re-bless.

**Every task, one commit, all of it together:** code + its test + `tasks/evidence-fragments/<task-id>.md`
(the `| Criterion | Command | Result | Artifact |` shape, real executed output only) + the ticked todo
line + the ledger event. Findings outside your fence get a row in the OWNING program's todo in the same
commit — a sentence in your report is not a landing place.

**Verify your own task** with `.\scripts\verify-change.ps1 -PlanOnly -Session
species-gear-chain-20260920`, plus the row's own Verify line. When the web app is touched, `npm run
build` in `gk-web/web/fusion-rpg-web` must pass. Never run the full suite — that is CC8 or this program's final
checkpoint. Report your own verification like a senior engineer: exact command, the numbers, and what
you did NOT prove.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Run these before claiming any task done; the numbers go in the task's evidence fragment, and any
acceptance line you cannot satisfy is named unmet rather than reworded. Never the full suite: it belongs
to CC8 or this program's final checkpoint.

Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session species-gear-chain-20260920
```
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Item|FullyQualifiedName~Gear"`
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Item"`
- `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Item"` (only when Data changed)
- `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1`
- `python gk-core/tools/tuning/resource_ownership.py --check` (only when a tuning or resource edge moved)
- `cd gk-web/web/fusion-rpg-web; npx vitest run src; npm run build` (only when the FE changed)
- A golden that moves does so in its OWN commit, with the cause named — never inside a content commit.
