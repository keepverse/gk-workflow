# Lane: notification-ssot, wave 1 (26 open rows, needs the SSOT landed before its consumers move)

Program: `tasks/notification-ssot-anchor.md` (read it first), plan `tasks/notification-ssot-plan.md`,
todo `tasks/notification-ssot-todo.md`. Map `docs/architecture/notification-ssot-map.md`, specs in
`docs/architecture/notification-ssot/`. Read `.claude/cmdc-agents/rules.md` before writing anything.

**First action:** if `features/mega-merge` is not an ancestor of your HEAD, merge it
(`git merge --no-ff features/mega-merge`). Then run
`python gk-core/scripts/anchor-ledger.py tasks/notification-ssot-ledger.jsonl resume` for your queue and the
concrete next item. Two rows are **owner-assent gates** (`NS0.1` relocate `world-notify` to
`shell/notify/rail/`, `NS0.2` move the fog rule into Core `WorldReportVisibility`): treat an unanswered
gate as a blocker, not as permission — the wave rows that depend on them carry the dependency in their
own `deps:` line, so start with whatever the ledger's `resume` names as unblocked.

**The shape of this program.** One notification SSOT: a source (server → injector → FE), one rail
surface, channel controls, and a debt adapter for capture loss. The FE moves are file relocations with
their tests; the server/Core half is where the authority lives. Do not invent a second rail, a second
catalogue or a second channel store — the program exists because there were three.

**Every task, one commit, all of it together:** code + its test + `tasks/evidence-fragments/<id>.md` +
the ticked todo line + the ledger event. Findings outside your fence get a row in the OWNING program's
todo in the same commit. When a string table changes, run `npm run extract` in `gk-web/web/fusion-rpg-web` and
commit `src/i18n/locales` in that same commit.

**Verify your own task** with `.\scripts\verify-change.ps1 -PlanOnly -Session
notification-ssot-20260920`, plus the row's own Verify line; `npx vitest run <file>` and `npm run build`
when the FE is touched. Never the full suite. Report exact command + numbers + what you did NOT prove.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session notification-ssot-20260920
```
- the row's own `Verify:` line in `tasks/notification-ssot-todo.md`
Run this yourself with the real paths — it is deliberately not a bullet, because the
runner executes a bullet's first code span verbatim:

```powershell
npx vitest run <the spec you changed>
```
- `python gk-core/tools/tuning/resource_ownership.py --check` when `gk-core/data/tuning/**` is touched
- `python gk-core/scripts/anchor-ledger.py tasks/notification-ssot-ledger.jsonl check` must exit 0 with the task event appended

Every task in this lane self-verifies against the evidence contract, in this order:

Boundary check — run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then read the numbers printed:

```powershell
.\scriptserify-change.ps1 -Paths <paths you changed> -Session notification-ssot-20260920
```
   boundary command; it selects the focused tests and the applicable guards. Never the full suite.
2. The row's own `Verify:` line from `tasks/notification-ssot-todo.md`.
3. When the FE is touched: `npx vitest run <the changed spec>` and `npm run build` (type errors fail the
   build); when a string table changes also `npm run extract` and commit `src/i18n/locales` in the same
   commit. When `gk-core/data/tuning/**` is touched, `python gk-core/tools/tuning/resource_ownership.py --check`.
4. `python gk-core/scripts/anchor-ledger.py tasks/notification-ssot-ledger.jsonl check` must exit 0 with the task
   event appended, and `python scripts/guard-doc-citations.ps1` style citation checks must not regress.

Report in the fragment: the exact command text, the numbers it printed, the committed artifact, and an
explicit NOT-proved list. The full suite and the E2E suite belong to CC8 or this program's final
checkpoint — not to a wave-1 task.
