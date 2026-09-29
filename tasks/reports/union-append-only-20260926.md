# `union_append_only.py` — fail closed on input it cannot handle

**Session** `union-append-only-20260926` · **SHA** `78c797c8a` · **branch** `features/mega-merge` (direct)
**Files** `.claude/cmdc-agents/scripts/union_append_only.py`, `gk-core/tests/tools/test_union_append_only.py`,
`tasks/sessions/union-append-only-20260926.json`, this report.
**Read-only** `gk-core/scripts/verification-boundaries.v1.json` (read, never written — see Finding 1).

---

## 1. The "before", reproduced

The defect was reproduced **before any line of the fix was written**, on a pair cut from the *real*
`gk-core/scripts/verification-boundaries.v1.json` — the same shape (`projects` arrays on single lines,
`boundaries` as multi-line objects, 2-space indent), 6 boundaries, both sides well-formed documents.
Size is the only thing reduced: the defect is about shape, and a 6-entry fixture is diffable by eye.

```
$ python old_union_append_only.py --ours vb-ours.json --theirs vb-theirs.json --out vb-union-before.json
vb-union-before.json: ours=101 theirs=100 theirs_only=2 result=62 sorted_by_ts=False
exit=0

  vb-ours.json         2800 bytes
  vb-theirs.json       2743 bytes
  vb-union-before.json 2147 bytes

output parses: NO -> Expecting ',' delimiter: line 22 column 15 (char 483)
```

Two 2.8 KB sides became a 2.1 KB file that is not JSON, and the tool exited **0**. Same mechanism and
same size ratio as the reported 182 KB → 96 KB incident; the mechanism is exact, not a guess:

> the dedup collapses the repeated structural lines. Both sides carry `    {` (opening each boundary
> object) and `    },` (closing it), 6 and 7 times respectively. `set` membership keeps **one** of each.
> 201 physical lines in, 62 out, and every comma and brace position has moved.

The pre-fix source for that run is `git show 359aacf36:.claude/cmdc-agents/scripts/union_append_only.py`
(2 554 bytes; `INPUT-SHAPE-UNSUPPORTED` absent).

### The same five scenarios, both tools, as subprocesses

Exit code and the parse state of the file left behind — the tool's own numbers, not a harness opinion.

| scenario | tool | exit | wrote | output parses as JSON? |
|---|---|---|---|---|
| **A** registry pair, `.json` sides + `.json` out | pre-fix | **0** | yes | **NO — destroyed** |
| | fixed | **2** | **no** | n/a (nothing written) |
| **B** registry sides renamed to `.txt` (the real call shape) | pre-fix | **0** | yes | **NO — destroyed** |
| | fixed | **2** | **no** | n/a (nothing written) |
| **C** a conflicted registry behind its own `<<<<<<<` markers | pre-fix | **0** | yes | **NO — destroyed** |
| | fixed | **2** | **no** | n/a (nothing written) |
| **D** a refusal must not touch an existing destination | pre-fix | **0** | yes | **NO — destroyed** |
| | fixed | **2** | **kept** | yes (previous content, byte-identical) |
| **E** the class the tool **is** for: a jsonl ledger | pre-fix | 0 | yes | yes |
| | fixed | 0 | yes | yes — `result=2 sorted_by_ts=True` in both |

Pre-fix lines for A–D, verbatim:
`ours=29 theirs=29 theirs_only=2 result=24 sorted_by_ts=False` · `ours=58 theirs=58 theirs_only=0 result=24 sorted_by_ts=False`

### Why "scenario B" is the one that matters

`resolve-append-only.ps1:38-39` renames **both** sides before calling this tool:

```powershell
git show ":2:$rel" | Out-File -Encoding utf8 $o     # $o = ...\ours.txt
git show ":3:$rel" | Out-File -Encoding utf8 $t     # $t = ...\theirs.txt
python union_append_only.py --ours $o --theirs $t --out $rel
```

So the incident arrived with the sides named `ours.txt` / `theirs.txt` and only `--out` carrying the
real name. **A suffix rule on the inputs alone would not have caught it.** That is why the shape is
decided from two independent signals and either one is sufficient.

---

## 2. Input classes refused, and classes deliberately not refused

The vocabulary is closed in the module (`STRUCTURED_SUFFIXES`, `JSONL_SUFFIXES`) and asserted as a set
by a test, so widening it is a reviewed change rather than an accident.

| class | verdict | signal | evidence |
|---|---|---|---|
| **`.json` document** (e.g. `verification-boundaries.v1.json`) | **REFUSE** | declared suffix **and** content | **MEASURED** — §1, scenarios A/B/C/D |
| **`.yaml` `.yml` `.toml` `.xml` `.ini` `.cfg` `.conf`** | **REFUSE** | declared suffix | **REASONED, not measured.** Same class as JSON by construction: a line is not the unit of meaning. No instance of this tool being handed one has been observed in this repo. A false refusal costs a named error message, not data. |
| **content parses as one JSON document**, any other suffix | **REFUSE** | content probe, per conflict-free **region** | **MEASURED** — this is the signal that catches scenario B |
| **`.jsonl` / `.ndjson`** | merge, re-sort by `ts` | — | the tool's own class |
| **`.md` / `.txt` / `.log` / no extension** | merge | — | the tool's own class |
| **`.csv` / `.tsv`** | **NOT refused** | — | see below |
| **one-line file that parses as a document, under a non-`.jsonl` name** | **REFUSE** | content probe | stated trade-off, below |
| **`.jsonl` whose rows lack `ts`** | merge, unsorted, **exit 0** | — | pre-existing contract, unchanged |
| **a `.json` file that is really a JSONL ledger** | **REFUSE** | declared suffix | the message says to use a `.jsonl` path |

**Why the content probe looks at conflict *regions*, not the whole file.** A conflicted working file is
`<<<<<<< ours … ======= … >>>>>>> theirs`; its marker-stripped **whole** text is two documents
concatenated, which parses as nothing (measured: `json.loads` → `Extra data: line 1 column 2700`).
A whole-file-only probe would classify that registry as plain text and mangle it. Probing each
maximal marker-free block separately is what sees through it. Asserted directly, so the probe cannot
quietly become decorative.

**`.csv` / `.tsv` — deliberately not refused, and the honest reason.** A row-per-line table *is* a
legitimate line union, so refusing it would block a valid use. The hazard is real and is **not** caught
here: a quoted field containing a newline makes a record span physical lines, and the dedup can then
drop a line that repeats. This tool has never been handed such a file. If one appears, the fix is a
csv-aware reader — not a suffix ban that would also block the well-formed case.

**The one-line trade-off, stated rather than hidden.** A one-line file whose content parses as a JSON
document, under a name that is not `.jsonl`, is refused. A minified structured file is the likelier
reading, and a one-line append-only ledger cannot conflict in the first place — there is nothing to
append. The same content under a `.jsonl` name is **not** refused (asserted), so the rule is the
declared suffix, not the content, in that corner.

**No `--allow-structured`.** An override is how the destructive path gets reopened by the next agent in
a hurry. The option list is asserted from the parser, so adding one turns a test red.

---

## 3. The round-trip guarantee

The guarantee is a **write-path property**, not a promise:

1. The union is written to a **sibling staged file** in the destination's own directory.
2. It is **re-read and re-validated there** — the lines must equal the lines built, and a `.jsonl`
   output must re-parse row by row.
3. Only then is it `os.replace`d onto the destination.
4. A staged file that cannot be removed is a **named refusal** (`OUTPUT-STAGED-LEFT-BEHIND`, with the
   path in the detail), never a swallowed delete — `docs/contributing/testing-standard.md` R3 applied to
   the tool itself.

So the destination is only ever touched by an atomic replace of an already-validated file. Measured:
a refusal over an existing `registry.json` left it **byte-identical** (scenario D) and left no
`.staged-` file behind.

### Honest limit of this evidence

**The two round-trip predicates are unreachable from the CLI once the pre-write checks pass.** That is
what makes them worth having — they are a cheap precondition on a write, like
`json.loads(out)  # validate BEFORE writing` in `union-verification-registry.py:112` — but it also means
**no exit code honestly exercises them end to end.** They are therefore tested as *predicates* with
crafted corrupt input (reordered, truncated, a row that no longer parses, an unreadable staged file) and
through an **injected failing validator** into `atomic_write_validated`, which is what proves "the
destination is untouched and no staged file is left". A green CLI exit code is **not** claimed here,
because no honest input can produce one.

---

## 4. Which tests fail against the pre-fix code

`gk-core/tests/tools/test_union_append_only.py` — **37 passed, 59 subtests passed** against the fixed tool
(6.7 s).

Run against the pre-fix source (`TOOL` repointed at `git show HEAD:…`, same file, `REPO` pinned):
**46 failed, 8 passed**. The 8 "passed" need reading carefully — three of them pass only because their
failures are recorded at *subtest* level, so pytest's parent line reads PASSED while the subtests failed.

### (a) Falsifiers — fail on **behaviour**, `0 != 2`

| test | pre-fix failure message |
|---|---|
| `FalsifierTests::test_A_json_registry_pair_is_refused_by_name_and_writes_nothing` | `True is not false : the destructive path must be unreachable` |
| `FalsifierTests::test_B_registry_sides_named_txt_are_refused_by_content` | `2 != 0` |
| `FalsifierTests::test_C_a_conflicted_registry_is_refused_behind_its_own_markers` | `2 != 0` |
| `FalsifierTests::test_D_a_refusal_leaves_an_existing_destination_byte_identical` | `2 != 0` |
| `FalsifierTests::test_A2_the_refusal_is_a_machine_readable_claim_not_only_prose` | `unexpectedly None` (no `--json`) |
| `JsonlContractTests::test_a_row_that_is_not_json_is_refused_and_nothing_is_written` | the pre-fix refusal has no **name** — `'INPUT-ROW-NOT-JSON' not found in 'REFUSING: not json (…)'` |

**Test A asserts the file's non-existence *before* the exit code, on purpose.** `argparse` also exits 2
on an unrecognised flag, so an exit-code-first test can pass for the wrong reason. The assertion order
was changed after that was observed.

**The expected exit codes and refusal names are literals in the falsifier class, not `uao.*`
attributes.** A test asserting `uao.EXIT_INPUT_SHAPE` fails pre-fix with an `AttributeError`, which
proves only that a name is missing. Asserting `2` fails with `0 != 2`, which is the defect. The
constants are still asserted, as a closed vocabulary, in `VocabularyTests`.

### (b) Parity — passes against **both**, by running both

These are the tests that make "unchanged" a measurement rather than an assertion:

- `ParityTests::test_jsonl_ledgers_merge_byte_identically_to_the_pre_fix_algorithm` — **37 subtests**
  (one per real `tasks/*ledger.jsonl` at the time of writing)
- `ParityTests::test_markdown_task_lists_merge_byte_identically_to_the_pre_fix_algorithm`
- `JsonlContractTests::test_a_jsonl_ledger_merges_and_re_sorts_by_ts`
- `JsonlContractTests::test_a_row_without_ts_is_merged_unsorted`
- `FalsifierTests::test_E_the_fixture_really_is_a_reproducer` — passes pre-fix **by design**; it pins
  the "before" from inside the suite (the legacy algorithm on the same fixture does not parse), so the
  falsifiers above cannot silently stop testing anything.

The parity reference `legacy_merge` / `legacy_lines` is the pre-fix algorithm **transcribed verbatim**,
not a hand-written expectation.

### (c) New-capability contract tests — unrunnable pre-fix, and labelled as such

`ShapeTests`, `RoundTripTests`, `VocabularyTests`, and the `--json` parts of `ReportTests` and
`JsonlContractTests` call `classify` / `verify_round_trip` / `atomic_write_validated` / `build_parser`,
or pass `--json`. They fail pre-fix because the API does not exist, **not** because behaviour differs.
They are kept in separate classes from the falsifiers and the parity sweep for exactly that reason, and
this report does not count them as falsification.

---

## 5. Append-only parity, measured by running both

Not asserted — both implementations were run as subprocesses over the same inputs and the bytes
compared. Sides were cut the way a real conflict looks: a shared prefix, then each lane's rows.

| input | ours/theirs lines | pre-fix sha256 (16) | fixed sha256 (16) | bytes | identical |
|---|---|---|---|---|---|
| `tasks/data-test-substrate-ledger.jsonl` | 19 / 24 | `c77c345c7a827498` | `c77c345c7a827498` | 6 400 | **yes** |
| `tasks/combat-ai-ledger.jsonl` | 218 / 422 | `ef703caa49f02057` | `ef703caa49f02057` | 144 339 | **yes** |
| `tasks/empire-progression-ledger.jsonl` | 253 / 491 | `cb816e7da4651ca6` | `cb816e7da4651ca6` | 107 791 | **yes** |
| `tasks/species-gear-chain-ledger.jsonl` | 182 / 349 | `6e3c09f64d8a7970` | `6e3c09f64d8a7970` | 89 548 | **yes** |
| `tasks/data-test-substrate-todo.md` | 290 / 566 | `8da16bccc061d74e` | `8da16bccc061d74e` | 75 932 | **yes** |
| `tasks/actor-hud-todo.md` | 116 / 218 | `8e6fee3d82deb73c` | `8e6fee3d82deb73c` | 18 645 | **yes** |
| `tasks/summoner-convergence-todo.md` | 75 / 136 | `758f8d8143bff1d0` | `758f8d8143bff1d0` | 13 133 | **yes** |

Exit codes equal in all seven. The committed suite generalises this: it sweeps **every**
`tasks/*ledger.jsonl` (**37** ledgers at the time of writing → 37 subtests) plus a named set of **5**
real task lists (5 subtests) — **42 subtests** in total — and asserts the bytes equal the
transcription. No count is pinned in the test: adding a ledger adds a case.

**What did change on the pass path, deliberately:**

1. The human summary gained two fields. The original fields keep their order, so a human grep and
   `resolve-append-only.ps1` (which reads only `$LASTEXITCODE`) are unaffected:
   `… sorted_by_ts=False shape=lines roundtrip=ok`
2. `--json` exists: a machine-readable envelope on **stdout**, with the human line moved to **stderr**
   so a caller parsing stdout never has to skip prose.
3. A `.jsonl` whose rows lack `ts` now also prints a `NOTE: N row(s) carry no 'ts' …` line and sets
   `rowsWithoutTs` in the envelope. Exit code, the union, and the absence of a sort are unchanged.

**The pre-existing `INPUT-ROW-NOT-JSON` refusal keeps its exit code (1) and its message** (`not json
(…): <line>`), with the machine name added.

---

## 6. `--structured`: **deferred, deliberately**

**Not built.** The brief allowed it "if cheap and clearly right". It is not clearly right, for three
reasons that are measurements, not preferences:

1. **Boundary-union logic already exists in the manager plane under two CONFLICTING rules.**
   `union-registry-sides.py` — *ours wins, differences reported, exit 3 asks you to read them*.
   `union-verification-registry.py:73-74` — *refuse outright if any shared entry differs; insert
   textually; validate before writing*. A `--structured` mode would have to pick one. That is a product
   decision, and this tool must not make it by accident.
2. **The two disagree on formatting, visibly.** `union-registry-sides.py:89` writes
   `json.dumps(merged, indent=2)`, which reformats the whole 186 KB registry; the other preserves the
   file's own layout by textual insertion, and says so in its own docstring
   (`union-verification-registry.py:14-17`). A delegation would silently choose which convention lands
   in a 490-entry registry.
3. **It would give one entry point two mutually exclusive contracts and two exit-code vocabularies**,
   which is the opposite of the fail-closed shape this change is for.

**What was built instead: the thin delegation.** The refusal names the tool to run —
`union-registry-sides.py` for a `.json`, and "use a `.jsonl` path / run the boundary-union tool" for a
mislabelled one. A pointer, not an implementation. It is deliberately a **Python** tool name, because
`resolve-append-only.ps1` and the unreferenced one-off `.ps1` files in that directory are being retired
by the ps1-ban program — naming a `.ps1` remedy would have shipped a dead pointer.

**If the manager wants the capability, the cheap correct shape is** to unify the two existing tools
first and let this one refuse until that exists.

---

## 7. Findings for the manager (not fixed here — the registry is outside this fence)

### Finding 1 — `verify-change.py` cannot plan this change: two `BOUNDARY-MISSING` refusals

```
$ python scripts\verify-change.py --plan-only \
    --paths .claude/cmdc-agents/scripts/union_append_only.py gk-core/tests/tools/test_union_append_only.py \
    --session union-append-only-20260926
VERIFY-CHANGE REFUSED [plan]: BOUNDARY-MISSING: .claude/cmdc-agents/scripts/union_append_only.py.
  meaning: no owner boundary and no explicit exemption maps this path
```

- **`.claude/cmdc-agents/scripts/union_append_only.py` — PRE-EXISTING gap.** The registry maps
  `.claude/cmdc-agents/scripts/*` file-by-file into `manager-fail-closed` and `seedsmith-bcu212`, plus
  `.claude/**/*.md` into `docs-and-assistant-config`. Neither names this file, at HEAD, before this
  change. Verified pre-existing: the file's previous commit is `ba077932b` and the registry was not
  modified here.
- **`gk-core/tests/tools/test_union_append_only.py` — gap this change introduces.** Every sibling
  (`test_live_slot.py`, `test_program_status.py`, `test_verify_change.py`, `test_retire_worktrees.py`,
  `test_audit_program_pipeline.py`) is mapped; this new file is not.

`gk-core/scripts/guard-verification-boundaries.py` **passes** (it enforces `src/**` and `tests/**/*.cs` — C#
only, not `.py`), so this is a *planner* gap, not a guard gap. Per AGENTS.md this is reported, not
worked around, and the full suite was **not** run as a substitute.

**Exact remedy** (modelled on `live-slot-tool`, which is the same shape), for whoever owns the registry:

```json
{
  "id": "manager-append-only-resolver",
  "kind": "owner",
  "paths": [
    ".claude/cmdc-agents/scripts/union_append_only.py",
    ".claude/cmdc-agents/scripts/resolve-append-only.ps1"
  ],
  "project": "tools-audit-tests",
  "testFiles": ["gk-core/tests/tools/test_union_append_only.py"],
  "level": "focused",
  "guards": []
}
```

`tools-audit-tests` is `{"runner": "pytest", "root": ".", "tests": "gk-core/tests/tools"}` — it already picks
the new test up, and `python -m pytest gk-core/tests/tools` is a wired CI step (`ci.yml:526`). `union-registry-sides.py`
and `union-verification-registry.py` are unmapped too and belong in the same or an adjacent row.

### Finding 2 — `session-boundary-check.py --session union-append-only-20260926` exits 1 on one DRIFT

```
! mega-merge-program-manager-20260925-f78e.json and union-append-only-20260926.json both claim
  '.claude/**' / '.claude/cmdc-agents/scripts/union_append_only.py' while active
  — narrow the scope or move one to a worktree
```

**Box I could not tick.** Both records are `direct` on the same branch, and neither prescribed remedy
is available: I cannot move another session, and narrowing my fence to zero files would mean not doing
the task. Region evidence, measured rather than assumed:

- `git status -- .claude/` was **empty** before this lane's commit — no `.claude/**` work in flight.
- `git log -- .claude/cmdc-agents/scripts/` shows the concurrent stream working on `*-lane.ps1`,
  `post_merge_check.py` and one-off `.ps1` **deletions** (`406b32f17`, `9a8e35e31`, `1905c8b35`). Those
  are PowerShell artefacts; this lane's file is Python, which the ps1-ban ruling keeps.
- This lane edits exactly one file in that directory and does **not** touch `resolve-append-only.ps1`,
  the file in that directory the other lane is most likely to be porting.

Recorded in the session record's `crossings` rather than assumed harmless. **Recommendation:** accept the
overlap; the clean fix is for the mega-merge session to drop `.claude/**` from its fence (its actual work
is the `.ps1` → `.py` port), not for this lane to retreat.

---

## 8. What remains unproven

- **`resolve-append-only.ps1` was never run end to end.** It refuses unless `MERGE_HEAD` exists and git
  reports an unmerged path, so driving it needs a real in-progress merge. Its *invocation shape* is
  reproduced exactly (sides named `ours.txt` / `theirs.txt`, `--out` the real repo-relative path) and that
  is scenario B, but the `.ps1` itself is unobserved against the new tool. It reads only
  `$LASTEXITCODE -ne 0`, and exit 2 satisfies that as "NOT RESOLVED", which is the correct branch.
- **The 182 KB actor-hud registry pair was not re-run.** The manager's inputs were not preserved in the
  tree and re-creating them would mean hand-building a merge. The 6-boundary pair is the same shape and
  the same mechanism at 1/40 scale, and the size ratio matches — but this is a scaled reproduction, not
  the original file.
- **The `.yaml`/`.toml`/`.xml`/`.ini`/`.cfg`/`.conf` refusals are reasoned, not observed.** No instance of
  this tool being handed one exists in this repo. A false refusal costs a named message, not data.
- **The round-trip predicates are not exercised end to end through the CLI** — unreachable by
  construction (§3). Predicate-level and injected-validator tests only.
- **The `.csv` hazard is real and uncaught** by choice (§2). No test covers it because no fix was built.
- **The refusal text names `union-registry-sides.py`, whose rule is "ours wins".** If the manager decides
  the correct rule for a registry merge is the *other* existing tool's ("refuse if any shared entry
  differs"), this lane's advice string is the thing to change — and that is a one-line edit.
- **`STAGED-LEFT-BEHIND` is tested only on Windows.** An open handle does not block `unlink` on POSIX, so
  the test skips rather than passing quietly. The repo is Windows; the skip is explicit.
- No `src/**`, `data/**`, `web/**`, `.agents/skills/**`, or `gk-core/scripts/verification-boundaries.v1.json` file
  was modified. The ps1-ban lane's two dirty `.commandcode/taste/**` files and its staged
  `docs/guide/mechanisms/_gen-stubs.ps1` deletion survived this commit untouched (verified before and
  after with `git status --porcelain`; the commit used an explicit pathspec).

---

## 9. Open questions

1. **Should the refusal name `union-registry-sides.py` or `union-verification-registry.py`?** The two
   existing tools disagree on what to do with a shared-but-differing boundary id. The actor-hud conflict
   had **9** of those. Whichever the manager picks, one advice string and one report line change.
2. **Should the two existing boundary-union tools be unified?** Until they are, a `--structured` mode on
   this tool cannot be written honestly. That unification is the prerequisite, and it is a different lane.
3. **Should `.csv`/`.tsv` get a real reader?** A suffix ban would be wrong; a csv-aware reader is a
   small addition if an append-only table ever shows up.
4. **Who owns the registry row in Finding 1?** The `ps1-ban` program already has the registry in its fence
   (`gk-core/scripts/enforcement-registry.v1.json`, `scripts/guard-*.ps1`) but not
   `gk-core/scripts/verification-boundaries.v1.json`; the `actor-hud` lane that last merged the registry has
   closed. It needs a named owner.
5. **Is `tools-audit-tests` the right project for a manager-plane tool's tests?** `manager-fail-closed`
   uses its own root (`.claude/cmdc-agents/scripts`, `tests: "."`); this lane's test lives in
   `gk-core/tests/tools/` because that is where the other `*-tool` tests already are. Both work; the registry
   row should pick one deliberately.
