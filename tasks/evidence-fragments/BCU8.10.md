# BCU8.10 — `battle.v5.json` `noteHybrid` is stale: routed to the next publish

**No tuning file was touched.** `gk-core/data/tuning/**` is never edited in place (a value ships as a new
`v{n+1}` through `gk-core/tools/tuning/publish.py`), and it is outside this lane's paths besides. The task's own
wording — *"note it for the next battle tuning publish"* — is the deliverable, so the note was routed to
where the next publisher will read it.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The staleness is real, and quantified | `rg -n "noteHybrid" gk-core/data/tuning/battle.v5.json` | `:9` — the clause *"DEFAULT 0 = the shipped behaviour exactly"* sits beside a published `300` | `data/tuning/battle.v{2,3,4,5}.json` |
| The value's real history, cited | `git diff -- tasks/combat-unification-todo.md` | `secondaryWeightMilli: 300` decided and published 2026-09-07, `RulesetVersion` 4→5 (`backlog-clean-up/lane-B1-backlog-clear.md:59`) | — |
| Note routed to the publisher, not to the data | `git diff tasks/combat-unification-todo.md` | new "Carried note for the next `battle` tuning publish" section: fix the clause in the new revision's `_meta.noteHybrid`, leave older revisions alone | `tasks/combat-unification-todo.md` |
| No tuning file changed | `git status --short data/` | empty | — |
| `verify-change.ps1` | `python scripts/audit-doc-citations.py --strict --scope tasks/combat-unification-todo.md` | 0 HIGH | — |

The comment text is copied forward per revision, so a publish that does not touch it re-carries the
stale sentence — which is exactly why this is a note at the publish site rather than a one-line edit
here.
