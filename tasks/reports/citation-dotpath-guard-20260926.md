# The doc-citation guard could not see a dot-directory

**Session:** `citation-dotpath-guard-20260926` (worktree `fix/citation-dotpath-guard-20260926`,
path `.claude/worktrees/citation-dotpath-guard-20260926`, forked from `features/mega-merge@e90cb0f7b`).
**Why this row exists:** the guard that answers "can a reader open that citation?" had a whole class
of blind spot, and it is the reason a wrong path sat in `AGENTS.md`'s own tooling table while the
audit reported that document clean.

## 1. The defect, and how it was found

`AGENTS.md`'s manager-tooling table pointed at `.claude/cmdc-agents/scripts/live-slot.ps1`. That file
does not exist; the real one is `scripts/live-slot.ps1`. `audit-doc-citations.py --scope AGENTS.md`
reported **0 HIGH**.

A probe settled the cause. A scratch document containing that dead path beside the real one produced
*"1 documents, 1 resolvable citations checked"* and **no** finding — the dead path was not even
counted as a citation. `CITATION` (`scripts/audit-doc-citations.py:58`) requires the backticked token
to begin with `[A-Za-z0-9_]`:

```python
CITATION = re.compile(
    r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:cs|ts|tsx|js|jsx|py|json|ps1|csproj|yml|yaml))"
    r"(?::(\d+)(?:\s*[-–]\s*\d+)?)?`")
```

A leading dot fails that class, so **every citation into a dot-directory was structurally invisible**:
`.claude/…`, `.kilo/…`, `.commandcode/…`. Measured across the 1691 documents the audit reads: **95 such
citations, 74 distinct tokens, none of them ever checked.**

## 2. The fix, and the counter-case that keeps it honest

A second pattern, `DOTPATH_CITATION`, recognises a citation whose **first segment is a dot-directory**
(a slash in it), chained into the same `D1`/`D2`/`D3` body in source order.

The slash is load-bearing. A leading dot alone is not a path: `` `.v1.json` ``, `` `.test.ts` `` and
`` `.Tests.csproj` `` are the *tail* of a citation whose head sits in an earlier backtick run, and
matching them would report a dead file for every such fragment in the corpus. That counter-case is a
`[Theory]` with three rows, and it is the reason the fix is 1 new pattern rather than a loosened
character class.

## 3. What it costs, measured — and the mistake I made while measuring it

Coverage: **25 860 → 25 925** citations checked. The five findings it newly surfaced were **not** dead
citations:

- `.kilo/setup-script.ps1` (×3) and `.kilo/agent-manager.json` (×2) are **real files that are
  untracked**: both are excluded through `.git/info/exclude` (machine-local), and both are read by
  shipped code — `gk-core/scripts/worktree_cleanup_core.py:215` opens the legacy manager registry and `:283`
  names it. They are EXEMPT 1's stated case, so they joined that closed list with their provenance.

**My own over-correction, recorded because it is the same trap.** I first rewrote `AGENTS.md` to say
"there is no worktree setup script in this repository", on the evidence that `git ls-files` matched
nothing. That was wrong: the file **does** exist on this machine, untracked. `git ls-files` cannot see
an excluded file — which is the entire reason EXEMPT 1 exists. The paragraph now states the truth
(machine-local, untracked, absent in a clone, so *verify* setup ran rather than assume it). I nearly
published a guard-blindness error as a doc correction, and only checked the filesystem before
committing.

Repo-wide after the fix: **0 HIGH, `--strict` exit 0** — strictly more coverage, no new red.

## 4. Verification

| Check | Command | Result |
|---|---|---|
| Guard tests for this tool | `dotnet test FusionRpg.Guard.Tests --filter DocCitationAudit` | **13 passed** (6 → 13) |
| Whole guard project | `dotnet test FusionRpg.Guard.Tests` | **700 passed** (693 → 700) |
| Repo-wide audit | `python scripts/audit-doc-citations.py --strict` | **0 HIGH, exit 0**, 25 925 citations |
| AGENTS.md scoped | `--scope AGENTS.md` | 0 HIGH, 39 citations |
| Session boundary | `session-boundary-check.py --session citation-dotpath-guard-20260926` | clean |

Tests added: a dead dot-directory citation reports HIGH; three bare-extension fragments do **not**
become citations; three real-but-untracked dot-files are exempt. The pre-existing
"An_invented_filename_still_reports_high" test is what keeps the exemption list from becoming a hole,
and it is why the new tests use an invented path rather than a real machine-local one.

## 5. Routed, not fixed here — a looseness this row deliberately did not change

A citation **without a line number** is accepted on basename alone: `audit-doc-citations.py:506` does
`checked += 1` then `if not cited_line: continue`, so the *directory* is never verified. That is why
`.claude/cmdc-agents/scripts/live-slot.ps1` passed even after this fix, while
`scripts/live-slot.ps1` exists. I corrected that one row in `AGENTS.md` because I knew the true path,
but I did **not** tighten the rule: doing so would light up every loosely-pathed citation in the
corpus, and how strict a citation must be is a policy decision for
`docs/architecture/spec-doc-citation-gate.md`'s owner, not a side effect of a scanner fix.

## 6. Next steps

- Merge this row (guard + `AGENTS.md`'s two corrected rows + the exemption list).
- Route to the doc-citation gate owner: decide whether a line-less citation must resolve its full
  path, and measure that population before changing the rule.
- `docs/contributing/session-boundary.md` §5 and `docs/architecture/data-test-substrate/
  fan-out-protocol.md:15` remain correct but read as if the setup script were repo-tracked; they now
  rely on the exemption rather than saying "machine-local" on the citing line. Tightening that wording
  is the same policy question as §5 above.
