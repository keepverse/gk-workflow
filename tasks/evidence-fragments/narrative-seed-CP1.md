# narrative-seed Checkpoint 1 — the two non-owner lines (registry hygiene, hand-off recorded)

Checkpoint: tasks/narrative-seed-todo.md §"Checkpoint 1 — Wave 1" · Specs: the Wave-1 registries

CP1's first two lines are checkable and recorded here; the third is an owner review and is the only line
left. Clearing the first two turns "CP1: three open lines" into "CP1: one owner action", which is what the
manager needs to route.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Line 1 — `test_narrative_*` registry suites green | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <3 changed paths> -AllowUnscoped` | pass — `pytest: seedsmith` (the whole narrative set) green in the same run; `guard.doc-boundary` 4 passed | `gk-forge/tools/seedsmith/tests/test_narrative_registry_hygiene.py` |
| Line 1 — no registry file carries a weight, probability or price | `pytest test_narrative_registry_hygiene.py -q -s` | pass — printed `owned registries scanned=17 keys=1752 forbidden-key hits=0` | same |
| The exclusion is by NAME, and cannot widen silently | same | pass — printed `foreign registry = doctrines.v1.json owner = docs/architecture/npc-story-events/spec-counter-doctrine.md#3`; the test asserts every other registry here declares no `_meta.owner` | same |
| Line 2 — hand-off recorded for the three consumers | (read) `docs/architecture/narrative-seed-map.md` §7 | pass — a "Hand-off (Checkpoint 1)" subsection lists every shared vocabulary file `narrative-vocabulary` may read, the two `narrative-text` may read, and the spine frame's `fragments[]` for `spine-progress` | `docs/architecture/narrative-seed-map.md` |
| Doc-citation audit of the changed map | `python scripts/audit-doc-citations.py --strict --scope docs/architecture/narrative-seed-map.md` | pass — `94 resolvable citations`, D1–D4 `(0 HIGH)`; the 9 D1 rows are PRE-EXISTING: the same command on `HEAD`'s map reports `90 citations`, D1 9. My paragraph added 4 resolvable citations and no D1 | same |
| Boundary guard | `python gk-core/scripts/guard-verification-boundaries.py` | pass — `VERIFICATION BOUNDARY GUARD OK` after adding the hygiene test to `seed-narrative-registry` | `gk-core/scripts/verification-boundaries.v1.json` |
| ruff | `ruff check test_narrative_registry_hygiene.py` | pass — `All checks passed!` | same |
| Line 3 — owner reviews the registries | — | **NOT RUN — an owner action this lane cannot perform.** Every registry value already carries both clauses (20 rows checked in the registry-hygiene scan's own set) and every reader refuses a row without them, so the review reads rather than repairs | — |

**Finding for routing (filed, not fixed).** `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` is the one file
in that directory this program does not own: its `_meta.owner` is
`docs/architecture/npc-story-events/spec-counter-doctrine.md#3`, and it carries per-mille effect weights
(`speciesElementBiasMilli` at `:12`, `orderWeightMilli` at `:13` and in every following row) **by design** —
the counter-doctrine module places its registry here. CP1's line 1, read literally as "no registry file",
therefore cannot hold while that file is in that directory; this program's scan excludes it BY NAME and
asserts every other registry declares no owner, so a new magnitude cannot inherit the exclusion. The
owning program's todo (`tasks/npc-story-events-todo.md`) is outside this lane's allowed paths, so the
manager must open the row there — or the line's wording needs an erratum scoping it to this program's own
registries.

`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).

## Addendum 2026-09-23 — the owner-review reading, and NS6b's refreshed constraint

**CP1 line 3 is a read, not a repair (measured).** Across the 17 owned registries, **267 rows carry a
`negative` clause and every one of them also carries its prose clause** — 138 `description`, 10
`teachingLine` (`teaches.v1.json`) and 119 `note` (`value-notes.v1.json`); **0 rows carry one without the
other**. The prose field differs by registry, which is why the checkpoint says "description" and three files
spell it otherwise. Reading taken with a scan over `gk-data/packs/fusion/data/seed/narrative/_registry/*.json` this session; no
file was changed by it. So the owner's review has nothing mechanical left to fix — it is 267
(prose, negative) pairs to read.

**NS6b's constraint re-measured, because its citations have drifted twice.** The row says
`.github/workflows/ci.yml` `:241`/`:295`; the 2026-09-23 predecessor note says `:346`/`:408`; the file today
has `Boundary guards` at **`:372`** (calling `run-guards.ps1 -Tier ci` at `:380`) and `Install seedsmith from
the lockfile` at **`:434`**. The ORDER is unchanged, and the file now states the reason itself at `:454`:
*"pytest is installed by the seedsmith lockfile step above; this step must stay after it."* So NS6b stays
skipped under its own clean-or-skip rule — a pytest-based guard cannot run in the guards tier until the move
lands — and `gk-core/scripts/guard-narrative.py` is no precedent: it runs `dotnet test` with a
`Guard=narrative` trait filter, so it needs no pip install.
