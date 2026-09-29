# Lane brief — `docs-citations-1` (CV.3: the `decisions.md` citation drift)

**Program**: `test-verification-boundary` (this work is doc-integrity evidence, the same family as
`TVB-F1`). **Session id**: `docs-citations-1`. **Branch**: `cmdc/docs-citations-1`.
**Mode**: direct, one problem. **Base**: `features/mega-merge` at spawn time.

## Why this lane exists

`docs/architecture/decisions.md` is the architecture-lock index every program cites by LINE NUMBER,
and its line numbers have drifted away from the rows they name. CV.3 was analysed by the manager
(commit `48fd754e` records the ruling) and could not be executed, because no lane running at the time
held a `docs/**` + `tasks/**` fence. This lane is that fence.

## The defect, exactly (already measured — do not re-derive, verify then fix)

1. `docs/architecture/decisions.md` is **181 lines**. A **blank line at line 121** splits the decisions
   table in two, and because the second block (**rows 122–149**) has no delimiter row of its own, those
   28 decisions **render as literal pipe text** to every reader. Blank lines directly after a table row
   exist at **121** and **150**. Removing a blank line inside a table is the first half of the fix.
2. **52** citations of the form `decisions.md:<N>` with **N ≥ 118** exist across `docs/` and `tasks/`
   (~296–298 `decisions.md` citations repo-wide). **18 of them cite a line whose row contradicts the
   prose that cites it** — real drift, not a style question. Worked examples found by the manager:
   - `docs/architecture/species-progression-map.md:156` says `` `decisions.md:119` *Class system* ``,
     while line 119 is **'Golden ordering across streams (2026-08-22)'**; *Class system* is **122**.
   - `docs/architecture/species-gear-chain-map.md:239` and `:241`
   - `docs/architecture/tier-system-ideal.md:565`
   - `docs/architecture/strain-splice-host-map.md:183`
   - `docs/architecture/empire-progression-map.md:209`

## Deliverable

One commit (or two, split as *table repair* then *citation re-point* — a single cause per commit, H1):

1. Delete the blank line(s) that split the table so rows 122–149 render as a table.
2. Re-point **every** `decisions.md:<N>` citation with N ≥ 118 to **`decisions.md` + the row NAME**,
   not a bare number. **When the line number and the prose disagree, the row the PROSE names wins** —
   the citation is meant to point at the decision, and the number is what drifted. Cite the row name
   in the same form the file uses (e.g. `` `decisions.md` — 'Class system' ``), so the next renumber
   cannot silently mis-point again.
3. Record in the commit body what the re-point rule was and how many citations were changed.

**Do not** rewrite unrelated `decisions.md` rows, renumber anything, or touch citations with N < 118
unless one of them is one of the 18 contradictions.

## Verification (all three, with output quoted in the fragment)

```
python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md
python scripts/guard-doc-citations.ps1 -Strict
Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session docs-citations-1
```
```

`audit-doc-citations.py` currently reports **0 HIGH** for that file, and it CANNOT break: its
`CITATION` regex (`scripts/audit-doc-citations.py:57`) only matches code extensions
(`cs|ts|tsx|js|jsx|py|json|ps1|csproj|yml|yaml`), so `.md:line` citations are not audited at all.
State that in the fragment rather than claiming the guard proves the fix — the guard proves
*nothing* about this change, and saying so is part of the evidence.

## Evidence contract (binding)

A fragment at `tasks/evidence-fragments/CV.3.md` containing: the exact commands, the numbers printed,
the committed artifact, an explicit **Not proved** list, and the count of citations re-pointed. Plus
one ledger line per row closed, via
`python gk-core/scripts/anchor-ledger.py tasks/test-verification-boundary-ledger.jsonl ...`.

## Fence (`--allow`)

`docs/**`, `tasks/**`. Nothing under `src/`, `tests/` or `data/` — if the fix appears to need one,
stop and route the finding to that program's todo instead.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Run these yourself before you call a row done, and put their real output in the fragment:

Boundary check — run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then read the numbers printed:

```powershell
.\scriptserify-change.ps1 -Paths <paths you changed> -Session docs-citations-1
```
  path-owned boundary. It resolves `-Paths` against its own root and refuses paths outside this
  session's record, so list exactly what you changed.
- `python gk-core/scripts/anchor-ledger.py tasks/test-verification-boundary-ledger.jsonl check` — must exit 0
  after every ledger line you add.
- `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` — must exit 0; it ignores
  `.md:line` citations, so it is a no-regression check, not proof of the re-point.
- `python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md` — report the printed
  count; it audits code-extension citations only and proves nothing about this change.
- The render check is manual and must be written as such: count the rows that render as literal pipe
  text before (28, rows 122-149) and after (0). No test in this repo covers markdown table rendering.

## Queue

- `CV.3` — the table repair and the citation re-point (the whole deliverable), in
  `tasks/test-verification-boundary-todo.md`.
