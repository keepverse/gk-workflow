# The port contract

Every `.ps1` tool retirement in this program is the same operation with a different body. This
is that operation, written down because each item below exists because the alternative was measured
and cost something. It is not advice; every line is traceable to the commit that proved it.

Run `python gk-core/scripts/ps1-port-census.py --tool <stem>` first. It reports items 1, 2, 3, 5 and 7
mechanically; the rest are judgement.

---

## 0. Read the body before touching anything

The port is a translation with a contract, not a rewrite. Carry over **the pattern set, the
verdict strings, and the scope** verbatim. A port that quietly widens or narrows what a guard
catches is a different guard wearing the same name.

The things that are safe to change, because they are improvements rather than changes of meaning:
structured output, named refusals, finding text, and a comment-stripping fix the repo has already
justified in writing. The things that are not: which files are scanned, which symbols count, and
whether a case comparison folds.

## 1. Registry row — `gk-core/scripts/enforcement-registry.v1.json`

One `"script"` line per guard. Change the extension and nothing else.

## 2. Verification-boundary owner row — `gk-core/scripts/verification-boundaries.v1.json`

**Check this even when you are sure it exists.** The census has now reported **0 rows for
`guard-dal`, `guard-stat-pairs` and `guard-open-identity`** — a missing mapping, which is a defect
to fix rather than a non-issue. Where no owner row exists, add one carrying the ported script
*and its test file*, so the ported tool's own tests are selected for it. Model it on an existing
`kind: owner` row at the same specificity; a second overlapping row at the same level is ambiguous
and the planner refuses.

## 3. A C# test that SHELLS the guard

Search for an **invocation**, not a mention. `git grep -E '(pwsh|powershell).*-File.*<stem>'` over
`tests/` finds what actually runs; a plain name search also returns prose comments that cite a
guard's discipline and need only the sweep.

Repoint the invocation to `python <script> --root <root>`. `FileName = "python"` has precedent in
`DocCitationAuditTests`, `VerificationBoundaryWorkflowTests` and `VocabRenameTests`.

## 4. The stream split — findings on stderr, a clean verdict on stdout

**This has now been rediscovered on four consecutive ports and cost four red runs each time.**
State it once, here:

| | stream |
|---|---|
| clean verdict (`... GUARD OK`) | **stdout** |
| every finding and every refusal | **stderr** |

The PowerShell original emitted *both* with `Write-Host`, which writes the INFORMATION stream and
is invisible to a `2>&1` capture — the exact trap this migration exists to remove. So its findings
reached a test's `stdout` only by accident of redirection, and every port has to move those
assertions.

In the C# test: keep `Assert.Contains("... GUARD OK", stdout)`, and move **every finding
assertion** to `stderr`. A run that reports `exit == 0` with empty stdout is not a broken port; it
is this rule working.

## 5. Citations — `gk-core/scripts/ps1-rename-sweep.py`

Deleting a tool leaves documents naming it, and the tail scales with how famous the tool is:
`guard-dal` alone was **360 citation lines across 227 files**. Never hand-edit it.

```
python gk-core/scripts/ps1-rename-sweep.py --map <stem>              # dry run
python gk-core/scripts/ps1-rename-sweep.py --map <stem> --apply
python scripts/audit-doc-citations.py --strict               # must reach 0 HIGH
```

The sweep rewrites the **invocation form** too (`.\scripts\x.ps1` → `python scripts/x.py`), not
just the path, and is idempotent — a second run reports 0 changes. The audit caps its detail list,
so a clean-looking batch can hide more; run it to 0, not to the first empty-looking pass.

**The sweep's default scope is `docs/` and `.md`/`.html`. That is not the whole tree**, measured
twice now. `guard-actor-hub` had live citations in `gk-core/scripts/battle-responsibility.v1.json` (a
*second* registry, which coupling 1 and 2 do not know about), in another guard's own comment, and
in `.kilo/command/*.md`. Pass `--root` and `--suffix` for each, or better:

**After the sweep, `git grep` is the real check and the census is only a briefing.** The census
enumerates five couplings; it found none of those three. It is a briefing that saves reading, not
a guarantee, and treating it as one is how a citation to a deleted file survives a port:

```
git grep -l '<stem>\.ps1' | grep -v -E '^(tasks/|\.claude/)'   # must print nothing
```

Anything still matching is either a live defect to fix or a historical record to leave.

**Two references must survive the sweep on purpose**, so `git grep` reporting them is correct and
not a miss:

1. **The port's own docstring.** `guard-single-writer.py` opens with a sentence naming the
   `guard-single-writer.ps1` it replaced — retired, ported, no longer present under that name — and
   that sentence is the provenance the port standard requires. The sweep now skips any file whose
   stem IS a map target, and says so on stderr.
2. **`gk-core/scripts/ps1-rename-sweep.py`'s own comment**, which quotes that sentence to explain the
   exemption above.

A sweep that rewrote either would leave a guard whose docstring no longer says what it replaced.

3. **`Directory.Build.targets`' PowerShell FALLBACK arm**, added when `guard-game-profile` was
   ported. The build resolves the guard's path from its extension and keeps a `.ps1` arm so the
   file still works on a branch where the port has not landed. So `git grep` reporting
   `Directory.Build.targets` for a ported guard is CORRECT, and rewriting that arm to `.py` would
   remove the only thing that makes a partially-ported branch buildable.

## 6. Repo-root landmarks — the landmine

**~45 test files across six projects use a guard `.ps1` as their repo-root landmark.** A walk-up
loop that returns the directory containing a guard script (`scripts/guard-dal.ps1` — retired, ported
to `gk-core/scripts/guard-dal.py`) stops finding the repo root the
moment that file is deleted, breaking unrelated tests in projects this session does not own.

Repoint those to `Directory.Build.props`: tracked, present in every .NET project, and something
this program will never delete. A guard script is the one file in the tree whose deletion is the
goal, so it was always the wrong landmark.

**But classify the site first**, by what the enclosing loop RETURNS:

| the loop… | role | action |
|---|---|---|
| `if (File.Exists(x)) return dir.FullName;` | MARKER | repoint to `Directory.Build.props` |
| `if (File.Exists(x)) return x;` | SCRIPT | it RETURNS the guard to execute |

Rewriting a SCRIPT-role site to a stable landmark produces
`powershell -File <repo>/Directory.Build.props`. That mistake broke **11 tests** in
`OpenIdentityGuardTests` and `LawnRepositionSingleWriterGuardTests` and was reverted in
`6682d3327`. The census separates the two and prints SCRIPT sites as *do NOT repoint* — which
means *do not repoint to a stable landmark*. Once the guard **is** ported, that same site must
point at the `.py`.

## 7. Prove it, and prove it differentially

Three levels, weakest to strongest:

1. **Green on the real tree.** Necessary, nowhere near sufficient — it cannot distinguish a working
   guard from one that stopped looking.
2. **The consuming C# test class passes.** This is the real gate: its `PlantedViolation_*` tests
   are falsifiers, so they prove the guard still *fails* on a violation. A guard proven only on a
   clean tree is half-proven.
3. **Differential against the original**, before deleting it. Build a fixture carrying one planted
   violation per rule, run it through **both** implementations, and compare rule-by-rule. This is
   what found the block-comment false positive in `guard-open-identity` (original 6 findings, port
   5) and confirmed `guard-stat-pairs` (7 findings each, same order, same exit).

Build the fixture to break a *careless* port — the subtlety each rewrite silently loses. For
`guard-stat-pairs` that was: group separation, case-insensitive comparison, a boolean that is not a
number, and whitespace-only-is-absent. **A fixture that cannot fail proves nothing**: my first
`guard-open-identity` comment case had a `switch` but no typed *declaration*, so neither
implementation flagged it and it demonstrated nothing.

## 7b. Which comment stripper? Ask, do not assume

`gk-core/scripts/cscan.py` holds **four** policies, and the number is a reading rather than a preference —
the PowerShell copies did not drift by accident, they answer different questions:

| function | comments | a block becomes | literals | line numbers |
|---|---|---|---|---|
| `strip_comments` | removed | one space | **kept verbatim** | shift |
| `strip_comments_and_literals` | removed | one space | **contents blanked** | shift |
| `strip_whole_line_comments` | whole-line only, blanked | n/a | kept | **kept** |
| `strip_comments_preserving_layout` | each char → a space | spaces | kept | **kept** |

Two questions decide it:

- **May a pattern match text inside a string?** `Log("p.theHealth = 0")` is a finding under
  `strip_comments` and nothing under `strip_comments_and_literals`. A SQL/DAL boundary wants the
  former, because a `CREATE TABLE` in a string is real SQL handed to a driver.
- **Does the guard report a line number?** If it names a line, it wants
  `strip_comments_preserving_layout`. Under the first two a file with a large block comment near the
  top reports line numbers past the end of the source, which sends an operator to the wrong place.

Each was verified character-for-character against its PowerShell original before it was added
(18–20 probes, including the awkward ones: doubled quotes, a backslash inside a *single*-quoted
literal, `//` and `/*` inside a literal, unterminated comment and unterminated string).

**If a port needs a policy that is not there, add one under its own name with its own
differential. Do not widen an existing one.** A scanner that quietly gets stronger turns a passing
guard red for reasons nobody can point at; one that quietly gets weaker stops catching the thing it
was written for. `gk-core/tests/tools/test_cscan.py` asserts the four are pairwise distinct, so a
"simplification" that collapsed two would fail there rather than in a deploy.

## 8. Tests for the port

`tests/tools/test_<stem>.py`, `python -m unittest`, importable module.

Structure the suite around **the properties a careless rewrite loses**, not around the happy path,
because those properties are invisible on a clean corpus. Assert the contract and closed
vocabulary; never a row count, a message body, or a population — those rot and guard nothing.

**Falsify the suite.** Change the implementation the way a future edit would, and confirm a test
goes red. Done for `guard-stat-pairs` (dropping the bool exclusion turns 3 red), `guard-dal`
(comment cases are asserted *not* findings), and `ps1-port-census` (inverting the MARKER/SCRIPT
discriminator turns its classification test red). A green suite that has never been seen to fail
is not evidence.

## 9. Commit shape

One logical change per commit, explicit paths, **never amend** — a correction is a new commit. And
**always pass a pathspec**: sessions share one index in this worktree, and a commit without one
swept 45 of my test files into another session's commit (`1a376cc4e`), which is why
`5d296568f` exists.

---

## When the port is done

- `run-guards.ps1 -Tier local -Only <id>` runs the `.py`: 1 guard, 0 red
- `verify-change.py --paths <script>.py --plan-only` selects the boundary **and** the guard
- the consuming C# test class passes, falsifiers included
- `audit-doc-citations.py --strict` is 0 HIGH
- `python gk-core/scripts/ps1-port-census.py --tool <stem>` reports the source already gone
