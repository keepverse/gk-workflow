# Spec: `commit-policy-green`

> **RETIRED 2026-09-19.** The owner retired the whole git gate (`scripts/commit-tool/`, `.githooks`, the `commit-policy` guard, the history check). This module has nothing left to make green; it is kept as history only.

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 1** · depends on:
`guard-runner`.

## Objective

`guard-commit-policy` enforces the no-watermark and allowlisted-identity rules, and it is **red**, so
it can never gate. The cause is not a policy violation. It is a policy gap: GitHub's web UI writes PR
merge commits under the owner's display name and GitHub's own committer identity, which the allowlist
has never heard of:

| Commit | Parents | Author | Committer | Subject |
|---|---|---|---|---|
| `2882f81d` | 2 | `Lê Tú Hào <letuhao1994@gmail.com>` | `GitHub <noreply@github.com>` | Merge pull request #9 … |
| `f384b380` | 2 | same | same | Merge pull request #7 … |
| `29e75528` | 2 | same | same | Merge pull request #8 … |
| `44e5761b` | 2 | same | same | Merge pull request #11 … |
| `9dae00c1` | 2 | same | same | Merge pull request #12 … |

All five are the owner's own PR merges. History is immutable (no force path exists, by design), so
the only honest fix is to teach the policy what a legitimate web merge looks like, **narrowly**, and
then gate.

## Design

### the deleted `scripts/commit-tool/policy.json` — two additions (git gate retired 2026-09-19)

<!-- citations-historical: scripts/commit-tool/ (including policy.json, check_history.py) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->


```jsonc
"allowedAuthors": [
  { "name": "letuhao1994", "email": "letuhao1994@gmail.com" },
  { "name": "Lê Tú Hào",   "email": "letuhao1994@gmail.com" }          // the owner's GitHub display name
],
"allowedMergeCommitters": [
  { "name": "GitHub", "email": "noreply@github.com" }                  // GitHub web-UI PR merges only
]
```

### the deleted `scripts/commit-tool/check_history.py` — the rule (git gate retired 2026-09-19)

<!-- citations-historical: scripts/commit-tool/ (including policy.json, check_history.py) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->


A commit passes the **committer** check when either:

- the committer is in `allowedAuthors` (today's rule, unchanged), or
- **all three** hold: the commit has **≥ 2 parents**, the committer is in `allowedMergeCommitters`,
  and the **author** passes `allowedAuthors`.

A single-parent commit committed by `GitHub` stays refused. That covers web-UI file edits, squash
merges and bot commits. Every other check (forbidden trailers, message patterns, forbidden author
substrings) still applies to merge commits in full.

### Why each condition is load-bearing

<!-- citations-historical: scripts/commit-tool/ (including validate.py) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->

| Condition | What it prevents |
|---|---|
| ≥ 2 parents | GitHub-committed **single** commits: web edits, squash merges, anything a bot pushes through the UI |
| author allowlisted | Someone else's PR merged in the owner's repo passing as the owner's |
| committer = exactly `GitHub <noreply@github.com>` | A spoofed committer name with a different email |

**How this sits with the existing checks.** `validate.py:86` `validate_identity` runs for author
**and** committer alike. It returns early for an allowlisted pair, and otherwise reports the
identity error *plus* any forbidden name/email substring (`validate.py:98-105`). The merge rule
therefore lives **before** that call: when all three conditions hold, the committer goes through a
dedicated `validate_merge_committer` that checks exact membership in `allowedMergeCommitters`, and the
general function is never called for it. The forbidden-substring lists keep applying to every
identity they covered before. As it happens, `forbiddenAuthorEmailSubstrings`' `noreply.github.com`
(the `users.noreply.github.com` privacy shape) does not occur in `noreply@github.com`, so there is no
conflict to resolve. It is recorded so nobody later "fixes" a mismatch that isn't one.

## Commands

```powershell
python scripts/commit-tool/smoke_test.py
python scripts/commit-tool/check_history.py --range 9523b9e8..HEAD
.\scripts\guard-commit-policy.ps1
```

## Project structure

<!-- citations-historical: scripts/commit-tool/ (including policy.json, check_history.py) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->


| Path | Change |
|---|---|
| `scripts/commit-tool/policy.json` | alias author and `allowedMergeCommitters` |
| `scripts/commit-tool/check_history.py` | merge-committer rule |
| `scripts/commit-tool/smoke_test.py` (or its test file) | four new cases, below |
| `gk-core/scripts/enforcement-registry.v1.json` | `commit-policy` → `ci` / `gating` |
| `docs/contributing/agent-git.md` | one paragraph: web-UI merges are allowed; everything else about the policy is unchanged |

## Testing strategy

<!-- citations-historical: scripts/commit-tool/ (including policy.json, check_history.py, guard-commit-policy.ps1) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->

The four smoke cases, each built as a commit in a temporary repository with a checked cleanup:

1. A 2-parent commit, author allowlisted, committer `GitHub <noreply@github.com>` → **passes**.
2. A 1-parent commit, same identities → **fails** (this is the squash-merge / web-edit case).
3. A 2-parent commit, committer `GitHub`, author **not** allowlisted → **fails**.
4. A 2-parent commit, committer name `GitHub` with a different email → **fails**.

Then `guard-commit-policy.ps1` exits 0 on the real tree, and CI runs it through the runner.

## Boundaries

- **Always:** keep every non-identity check applying to merge commits.
- **Ask first:** any further allowlist entry.
- **Never:** allow single-parent commits by `GitHub`. Never rewrite history to turn the guard green.

## Success criteria

- [ ] The four smoke cases pass and fail exactly as listed.
- [ ] The guard is green on the real tree and gating in CI.
- [ ] `agent-git.md` states the rule.

## Self-audit — the debate

<!-- citations-historical: scripts/commit-tool/ (including policy.json, check_history.py, guard-commit-policy.ps1) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->

**Objection: "Adding an allowlist entry is the owner's call."** Correct, and the owner made it:
**yes**, 2026-09-18 (map question 3). This spec was the default, and it is now the decision. It is
the narrowest rule that turns the guard green without rewriting history. The alternative that was
on the table, a `--range` starting after `9dae00c1`, would have silently exempted those five commits
forever and hidden the next web merge as well.

**Objection: "The display name contains non-ASCII characters. Could encoding break the comparison?"**
`check_history.py` reads `git log` output. The build must confirm it decodes UTF-8 (`git log
--encoding=UTF-8`) and add case 1 using the literal name `Lê Tú Hào`, so an encoding regression fails
a test instead of turning the guard red for unrelated reasons.

**Objection: "Why not drop committer checking entirely? The author is what matters."** The committer
is how a rebase or cherry-pick by a *tool* shows up, and those are exactly the watermark vectors the
policy exists to catch. The rule stays, with one narrow exception.

## Gaps found and closed while writing

<!-- citations-historical: scripts/commit-tool/ (including validate.py) was deleted 2026-09-19 when the git gate was retired; agents now use plain git with explicit paths, docs/contributing/agent-git.md -->

- **The first draft allowed `GitHub` as a committer unconditionally.** That would have admitted squash
  merges and web edits. The parent-count condition closes it.
- **UTF-8 decoding of the display name was unverified.** Added as an explicit test case.
- **A wrong claim in the first draft, caught by reading the code.** The draft said the forbidden
  substring lists apply to authors only. `validate.py:86-105` shows one function checking both roles.
  The design moved the merge rule *before* that function, so the committer never reaches the general
  path. The strings don't collide in any case, which is now stated with the line reference instead
  of asserted.
- **The merge path needs its own `role` label** in error text (`"… merge-committer"`), so a failure
  on a web merge is distinguishable from an ordinary committer failure in CI output.
