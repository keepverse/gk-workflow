# Task: empire-progression EP1.19–EP1.21 — adopt the stranded auto-assign work, finish it, prove it

Program: `tasks/empire-progression-plan.md` / `tasks/empire-progression-todo.md` (rows **EP1.19**,
**EP1.20**, **EP1.21** and checkpoint **CP2**). Read the rows, then these specs before writing anything:

- `docs/architecture/empire-progression/spec-auto-assign-control.md` (C1/C3/C4/C5 — the rules list, the
  draft-only rule, the refusal-vs-hide rule)
- `docs/architecture/empire-progression/auto-assign-control-ideal.md` (line 70: the rule display text is
  FE-hardcoded today and must come from the catalog; line 121: the new
  `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json`; line 175: the publish is an **H7** step — publish
  and switch the reader in the same commit)
- `docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md` (the draft fill rules EP1.19 lands on)

**First action:** merge the integration branch into your own — `git merge --no-ff features/mega-merge`
(HEAD `3f4d6411`). Then copy the session record template to `tasks/sessions/ep-autoassign.json` with your
paths, because your `verify-change.ps1` run needs that session id.

## The stranded work you are adopting (do not re-invent it)

An earlier native session on the `empire-progression` lane stopped mid-task (owner plan-quota stop). Its
worktree is `.claude/worktrees/agent-a62e66aeb29dc472c` (branch `worktree-agent-a62e66aeb29dc472c`,
HEAD `451b244c` = EP1.19's `/idea-ui` pass) and it holds **12 modified + 2 untracked files, 243
insertions** implementing EP1.20. It is stranded in a worktree nobody else can see, and it is now yours.

Adopt it as your starting point, then judge every line against the specs:

```
git -C "D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/agent-a62e66aeb29dc472c" \
    diff > D:/tmp/ep-autoassign-strand.patch
git apply --3way D:/tmp/ep-autoassign-strand.patch     # in YOUR worktree
```
plus the untracked `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` (copy it in) and
`docs/research/class-system/real-runs/` (inspect it: if it is research output, keep it with the row that
names it; if it is a leftover scratch dir, say so in your evidence and leave it out).

**Orchestrator's assessment of the strand (you must still verify it, not trust it):** the shape is right —
a closed `AptitudeAutoAssignRules.All` vocabulary, a `GET /rules?scope=` endpoint whose scope mapping hides
rather than refuses (C5), catalog-sourced FE labels with the closed TS union for keys, a Server endpoint
test and vitest coverage; it is uncommitted, based on a HEAD older than yours, and **EP1.21's Playwright
spec does not exist yet**.

## What you must add or fix

1. **Catalogs are tuning artifacts, not loose JSON.** `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` is
   a new published artifact: check how the neighbouring `*-catalog.v{n}.json` files are registered and
   published (`gk-core/tools/tuning/publish.py`, the tuning registry, and whatever the FE loads it through). If a
   registry/loader entry is missing, add it the sanctioned way (never hand-edit a published version in
   place). State in your evidence which path published it.
2. **H7 in one commit**: the catalog's publication and the switch of `autoAssign.ts`'s `ruleLabel`/
   `RULE_LABELS` to read it must land together.
3. **EP1.20's endpoint contract**: the closed rule ids a scope may offer come from the server
   (`GET /api/aptitude-presets/rules`), never a hardcoded FE list; `commander` omits `species-favour`
   because Mode C has no species; an unknown or missing scope refuses by name. Prove it with a Server test
   that goes through the real endpoint.
4. **EP1.21**: write `web/fusion-rpg-web/tests/e2e/aptitude-auto-assign.spec.ts` (match the existing spec
   layout — check where the other `*.spec.ts` files live) proving the control emits its rule and that
   **nothing persists before Confirm** (CP2's second clause).
5. **Tick EP1.19, EP1.20, EP1.21 and CP2** with an evidence fragment each: one table row per acceptance
   line, results quoted as numbers, and the commit that carries it. CP2 stays unticked unless both of its
   clauses pass.

## Rules that bind this work

- One logical change per commit: code + tests + evidence + ledger + the ticked todo box together.
- A defect you find outside your fence gets `file:line`, the cause you read, and a row in the OWNING
  program's todo in the same commit — never a sentence in your report only.
- Background/foreground: run everything in the FOREGROUND and keep working while a long command runs.
  Never end a turn waiting on your own job.
- No watermarks, no `git add -A`, explicit paths only, never push.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session ep-autoassign
```
- `cd gk-web/web/fusion-rpg-web && npm ci && npm test` (vitest) and `npm run build`
- `cd gk-web/web/fusion-rpg-web && npm run test:e2e` (playwright chromium; `npm run test:e2e:install` once first)
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeAutoAssign"`

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.
