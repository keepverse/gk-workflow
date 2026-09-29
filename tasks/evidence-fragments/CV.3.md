# CV.3 — `decisions.md` table repair + citation re-point

Row `CV.3` in `tasks/summoner-convergence-todo.md`. Two commits, one cause each: the table repair
(`c3b78fb4`), then the citation re-point.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the blank line inside the table is gone and rows 122–149 are one table again | `python -c "L=open('docs/architecture/decisions.md',encoding='utf-8').read().split(chr(10));i=[n for n,x in enumerate(L,1) if x.startswith('|')];print(i[0],i[-1],len(i),i==list(range(i[0],i[-1]+1)))"` | `5 148 144 True` — first `\|` row 5, last 148, 144 rows, contiguous, no gap | `docs/architecture/decisions.md` |
| how many rows render as literal pipe text | **manual — no test in this repo covers markdown table rendering** | before: **28** (rows 122–149, the block after the blank line at 121 had no delimiter row of its own); after: **0** | this fragment |
| every `decisions.md:<N>` citation with `N >= 118` names the row, not the number | `git grep -n -o -E "decisions\.md:[0-9]+" <ref> -- docs tasks \| awk -F'decisions.md:' '{if ($2+0>=118) print}' \| sed -E 's/^([^:]+:[0-9]+):.*$/\1/' \| sort -u \| wc -l` | base `d12dcb90`: **52**; tree after the re-point: **0** (53 occurrences, 52 lines) | `git diff --name-only d12dcb90` — 30 files |
| how many of the 52 cited a line holding a different row than their own prose names | per-cite reading during the re-point (prose-named row vs cited line) | **39 of 52** — the brief's reading was 18 | this fragment |
| citation audit for the file the row names | `python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md` | `1 documents, 104 resolvable citations checked`; D1 0, D2 0, D3 0, D4 0; exit 0 | this fragment |
| repo citation guard | `powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\scripts\guard-doc-citations.ps1' -Strict"` | `1681 documents, 24859 resolvable citations`; D1 `938 (0 HIGH)`, D2 `12 (0 HIGH)`, D3 `57 (0 HIGH)`, D4 `0 (0 HIGH)`; exit 0 | this fragment |
| path-owned verification | the exact command in §1 | **fail** — 2 reds, neither one in the deliverable (§2) | this fragment |
| the lane's own fence, scoped to it | `python scripts/session-boundary-check.py --session docs-citations-1` | **fail**, exit 1, `DRIFT (14)` — every line a path overlap with two other `active` records (§2) | this fragment |

**§1 the exact verify-change command** (every path this lane changed; run from the worktree root):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\scripts\verify-change.ps1' -Session docs-citations-1 -Paths 'docs/DESIGN-GATE.md','docs/architecture/build-preset/spec-preset-surface.md','docs/architecture/decisions.md','docs/architecture/empire-inventory-surfaces/spec-legion-sheet.md','docs/architecture/empire-progression-map.md','docs/architecture/empire-progression/spec-specimen-respec-price.md','docs/architecture/empire-seed-map.md','docs/architecture/empire-seed/spec-decision-45-revision.md','docs/architecture/empire-seed/spec-exchange-role.md','docs/architecture/empire-seed/spec-structure-bands.md','docs/architecture/spec-rulings-2026-09-18.md','docs/architecture/species-craft-ideal.md','docs/architecture/species-gear-chain-map.md','docs/architecture/species-gear-chain/spec-creature-drop-tables.md','docs/architecture/species-gear-chain/spec-set-species-binding.md','docs/architecture/species-gear-chain/spec-socket-allowance-by-kind.md','docs/architecture/species-gear-chain/spec-species-materials.md','docs/architecture/species-progression-map.md','docs/architecture/species-progression/spec-species-layer-delivery.md','docs/architecture/strain-splice-host-map.md','docs/architecture/tier-system-ideal.md','docs/architecture/trade-network/exchange/spec-treaty-vocabulary.md','docs/architecture/trade-network/trade-surface-map.md','docs/architecture/world-continuity-ideal.md','docs/architecture/world-continuity-map.md','tasks/evidence-fragments/T27.md','tasks/ip-censor-plan.md','tasks/run-board-20260920.md','tasks/sessions/docs-citations-1.json','tasks/summoner-convergence-todo.md','tasks/test-verification-boundary-todo.md','tasks/evidence-fragments/CV.3.md','tasks/test-verification-boundary-ledger.jsonl','tasks/summoner-convergence-ledger.jsonl'; Write-Output ('VERIFY_EXIT=' + $LASTEXITCODE)"
```

**§2 the two reds — both diagnosed, neither caused by this change.**

- **R1 — `verify-change` exits 1 at its own per-path `doc-citations` check for
  `tasks/ip-censor-plan.md`**, on a **pre-existing** finding on a line this lane did not touch:
  `tasks/ip-censor-plan.md:448  D3  \`_index.json:382-387\`  - 8 files share this name`. The lane's
  only edit in that file is one token on `:299` (`git diff -U0 tasks/ip-censor-plan.md` = a single
  hunk at `:299`). Root cause: `scripts/audit-doc-citations.py:372` defaults `--scope` to `docs/`, so
  the repo guard never audits `tasks/**` — at `--scope tasks/` this session measured **485 HIGH**
  over 728 documents (`D1 1286 / 357 HIGH`, `D2 15 / 15 HIGH`, `D3 113 / 113 HIGH`) — while
  verify-change's per-path check applies the `docs/` bar to every changed `.md`. Filed as `TVB-F6`
  in `tasks/test-verification-boundary-todo.md`. The run stops here, so it never reaches R2.
- **R2 — `session-boundary-check.py --session docs-citations-1` exits 1 with `DRIFT (14)`**, all of
  it path overlap: `keepverse-split.json` (active, direct, claims `docs/**` incl.
  `docs/architecture/decisions.md`) and `convergence-resume-20260920.json` (active, direct, claims
  `tasks/summoner-convergence-todo.md`, `tasks/summoner-convergence-ledger.jsonl`,
  `tasks/run-board-20260920.md`, `tasks/evidence-fragments/**`, `tasks/sessions/**`). The manager's
  own ruling grants this lane that fence (`tasks/run-board-20260920.md` §"Ruling — CV.3 gets the first
  fence that can actually hold it"), so the crossing is deliberate and recorded in the session
  record's `crossingNote`. Bounded: `git status --short` on `features/mega-merge` is empty, so
  neither record holds uncommitted work in this fence, and this lane commits on its own branch in its
  own worktree.

**§3 Not proved.**

- **`audit-doc-citations.py` proves nothing about this change.** Its `CITATION` regex
  (`scripts/audit-doc-citations.py:57`) matches only code extensions
  (`cs|ts|tsx|js|jsx|py|json|ps1|csproj|yml|yaml`), so `.md:line` citations are never audited. Its
  0-HIGH report on `docs/architecture/decisions.md` is a report about *other* citations in that file;
  it would have said the same before this change. Neither `-Strict` nor verify-change can see a
  `decisions.md:<N>` citation, before or after.
- **`guard-doc-citations.ps1 -Strict` was green before and after** (both measured this session), so
  its green is not evidence for the fix — only the census row above is.
- **No rendered check.** "Rows 122–149 render as a table" is asserted from the byte-level contiguity
  of `|` rows; no test or browser renders the markdown.
- **Not fixed, deliberately, and filed:** `decisions.md:54` and `:120` each hold an unescaped `|`
  inside a code span, which GFM reads as a cell delimiter and silently truncates the rest of the row;
  and the `decisions.md … (:N)` shorthand citation form (~30 sites, 3 drifted) is a second,
  unaudited form outside CV.3's stated `decisions.md:<N>` scope. Both are `TVB-F5`.
- **Nothing gates the census.** A `decisions.md:<N>` citation written after this fragment would
  reopen the drift unnoticed; the fix is a name-only convention, not an enforced one.
- **The `N < 118` band was left by the brief's cutoff, and it is drifted too** — measured over tracked
  files: 56 occurrences with `N` in 110–117 over 25 files, ~54 naming a different row than their line,
  6 of them outside `docs/**` + `tasks/**` (`src/**`, `web/**`). Filed as `TVB-F7`; not touched here.
