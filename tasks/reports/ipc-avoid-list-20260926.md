# `ip-censor` IC-3/IC-4 — the avoid-list brief seam: verified, and two findings the manager owns

**Session:** `ipc-avoid-list-20260926` · **Branch:** `features/mega-merge` · **Head I started from:** `3460de325`
**Fence:** `gk-forge/tools/seedsmith/**`, `tasks/reports/ipc-avoid-list-20260926.md`, `tasks/sessions/ipc-avoid-list-20260926.json`

---

## 0. Headline: the premise of the brief was stale. The wiring is already on the integration head.

The brief says *"3 of the 14 fail"*, measured on commit `f4769a660`, and asks me to wire the missing
half. That measurement is **correct for `f4769a660` and false for the current head**:

| Claim | Measured on `f4769a660` | Measured on `3460de325` (this head) |
|---|---|---|
| The three staged files exist | yes | yes, **byte-identical** (`git diff f4769a660 HEAD -- <3 paths>` is empty for all three) |
| `render_brief` takes `avoid_terms` | no | **yes** — `adapters/trees/nodegen/brief.py:126` |
| The 14 tests | 11 pass / 3 fail | **14 pass** |

The wiring landed in **`93a2e16d9`** *"feat(ipcensor): T16 IC-4.1 - tree brief avoid line, `--node`
selector, regenerate Overwatch node"*, which the `ip-censor` ledger records as **T16 DONE
2026-09-24** (`tasks/ip-censor-todo.md:579-611`). So there was **nothing left to wire**, and I wired
nothing. What this session produced instead: the verification the brief asked for, **two new
contract tests** for the one control in this seam that had zero coverage, and **two findings** the
manager owns.

**A correction to the brief's diagnosis.** The brief located the missing parameter at
`gk-forge/tools/seedsmith/seedsmith/briefkit/render.py:82`. That is a **different function** — the
`briefkit` package's own content-addressed brief renderer (`Brief` dataclass, `CITATION_PATTERNS`,
`render_briefs`). The 14 tests import `seedsmith.adapters.trees.nodegen.brief`, whose `render_brief`
is at **`adapters/trees/nodegen/brief.py:120`** — keyword-only (`def render_brief(*, …)`), which is
why a caller could not pass it positionally. `spec-avoid-list.md:70` names the right one
("`render_brief` (`adapters/trees/nodegen/brief.py:114`)"). `briefkit/render.py` is untouched and
correctly so: the spec's Project Structure (`:57-62`) never lists it, and no ledger row adopts it.

---

## 1. What IC-3/IC-4 actually require, and whether the tests agree

Read in this session, not recalled: `docs/architecture/ip-censor-map.md` (rows IC-3 `:43`, IC-4
`:44`, the `avoid-list` module row `:61`, IC-4.1 `:131`, the "why it is a module" note `:92-97`),
`docs/architecture/ip-censor/spec-avoid-list.md` (whole file), `tasks/ip-censor-todo.md:520-617`
(T14/T15/T16 + Checkpoint 5), `tasks/ip-censor-plan.md:24-25,255-258,311`.

| Requirement | Source | Do the 14 tests agree? |
|---|---|---|
| One helper renders the list from `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json`; every alias of every group scoped `player-name`/`player-prose`; **case-folded unique, sorted, deterministic** | `spec:27-29`; todo T14 `:526-528` | **Yes** — `LoadAvoidTermsTests` (7) + `RenderAvoidLineTests` (3) |
| **Throws naming the key** on a shape it cannot read; never defaults | `spec:44-45,88`; todo T14 `:529` | **Yes** — `test_a_registry_missing_groups_throws_naming_the_key`, `…_missing_scope_…`. The helper also refuses a non-object group, a missing/non-list `aliases`, and a non-object/blank alias (`avoid_list.py:52,59,64,68`) — **more than the spec names**, which is the fail-closed direction, not a divergence |
| The IP line is a **separate line** from the motif `Avoid entirely:` line | `spec:70-72`; todo T16 step 1 `:558-560` | **Yes** — `test_the_avoid_line_is_separate_from_the_motif_avoid_line` |
| Empty terms → the brief is unchanged (an adapter never prints an empty list) | `spec:92` | **Yes** — `render_avoid_line(()) == ""` and `test_without_terms_the_brief_is_unchanged` |
| Prompt hygiene: **no fixture mark spelling appears outside the avoid line**, over the brief text | `spec:34-35,104-106` | **Yes** — `test_no_fixture_mark_spelling_appears_outside_the_avoid_line` |
| Fixtures use **invented marks only** (`gk-forge/tools/seedsmith/**` is an enforced `generator-prompt` surface) | `spec:107-108` | **Yes** — `Examplemark`/`example mark`/`Zorblax`/`Zqx`/`CodeonlyInternal`; no real registry spelling appears in the fixture or the test file |
| **No count pinned** for the real registry | `spec:109-111`; `validation-ssot.md` | **Yes** — the tests read the fixture only. (Confirmed by reading: `load_avoid_terms` is called with `FIXTURE_REGISTRY` in all 14.) |
| IC-3: **no answer-side check, no retry, no refusal** on the strength of this list | `spec:33`; map `:43` | **Yes, and provable beyond the tests**: the helper is pure (`json` + `str` only, no model import — `avoid_list.py:12-16`), and the adopter prints a line |

**Where the tests are narrower than the ledger** (not wrong, just partial — and I did not widen them):

- The spec's Testing Strategy names **two** adopters — *"the tree node brief **and the uniques
  brief**, rendered from a fixture registry, contain the avoid line"* (`spec:104-106`). The 14 tests
  cover the **tree** half only. The uniques half is **T15, a separate row**, still `[ ]` open
  (`todo:536`) — see Finding 1.
- The spec's IC-4 fix has **four** steps (`spec:119-124`); the 14 tests cover step 2 (the adoption).
  Steps 1, 3 and 4 are generator/corpus/release-gate steps, and the ledger records them as done at
  `todo:579-606` (`Structural Integrity Protocol`, `promptVersion: tree-language/4`, no `overwatch`
  finding). **Not re-verified by me** — see §6.

---

## 2. The wiring, `file:line`, read on the current head

End-to-end, four files, all already committed:

| Where | What |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py:36` | `load_avoid_terms(registry_file=None)` — reads the committed registry, folds by `str.casefold()`, keeps the lexicographically smallest spelling per fold, sorts by casefold |
| `…/avoid_list.py:82` | `render_avoid_line(terms)` — `()` → `""`; otherwise one line |
| `…/adapters/trees/nodegen/brief.py:30` | `from ....briefkit.avoid_list import render_avoid_line` |
| `…/adapters/trees/nodegen/brief.py:126` | `avoid_terms: "Sequence[str]" = ()` — the keyword-only parameter the brief asked for |
| `…/adapters/trees/nodegen/brief.py:168-169` | `ip_avoid_line = render_avoid_line(avoid_terms)`; `ip_avoid_block = f"\n{ip_avoid_line}" if ip_avoid_line else ""` — a **separate** line from `motif_line`/`anti_line` (`:163-164`) |
| `…/adapters/trees/nodegen/brief.py:63` | `PROMPT_VERSION = "tree-language/4"` (was `/3`), with the vintage note at `:58-62` |
| `…/adapters/trees/nodegen/run.py:595` | `NodeGenerationInputs.avoid_terms: Sequence[str] = ()` |
| `…/adapters/trees/nodegen/run.py:875` | `avoid_terms=inputs.avoid_terms` into `render_brief` |
| `…/report/cli.py:2322-2327` | reads the registry **once**, fail-closed (§4) |
| `…/report/cli.py:2373` and `:2438` | passes `avoid_terms` to the sample brief and into `NodeGenerationInputs` |

The brief's own claim that *"a keyword-only parameter with a default cannot break a positional
caller"* is **true but was checked, not assumed**: `def render_brief(*, …)` makes a positional call
impossible at the call boundary, and `()` makes every pre-existing keyword caller unchanged. Both
production callers pass keywords; the empirical proof is §5's falsification (11 of 14 pass against
the pre-wiring file) and the 605-test trees run.

---

## 3. Every caller of `render_brief`, and what changed for each

There are **two distinct functions** with this name. Confusing them is what made the original brief
point at the wrong file.

### A. `adapters/trees/nodegen/brief.py:120` — the one this feature is about

| Caller | Kind | What changed |
|---|---|---|
| `adapters/trees/nodegen/run.py:867` | production | **Changed** — now passes `avoid_terms=inputs.avoid_terms`. Node generation is the IC-4.1 path. |
| `report/cli.py:2367` | production | **Changed** — now passes `avoid_terms=avoid_terms` (the dry-run `--sample-brief` preview). |
| `adapters/trees/species/generate_tree.py:224` | production (**indirect** — builds `NodeGenerationInputs`, not `render_brief`) | **Unchanged, and it is the gap.** It does not pass `avoid_terms`, so every **species-tree node brief renders with no IP avoid line** while defaulting to `()`. See Finding 2. |
| `tests/adapters/trees/test_nodegen_brief.py:60,71,82,88,97,112,134` | test | Unchanged — keyword-only + default ⇒ identical behaviour. |
| `tests/adapters/trees/test_nodegen_generate.py:165` | test | Unchanged. |
| `tests/test_briefkit_avoid_list.py:93,103,117,129` | test | The 4 adoption tests; 3 of them are the ones that failed on `f4769a660`. |

### B. `briefkit/render.py:82` — a different function, deliberately untouched

| Caller | Kind | What changed |
|---|---|---|
| `briefkit/render.py:187` (`render_briefs`) | production | **Nothing.** No ledger row adopts it; the spec does not list it. |
| `tests/test_briefkit.py` (13 sites), `tests/test_cp_g_end_to_end.py:102`, `tests/test_narrative_names_registry.py:239,245` | test | Nothing. |

If the briefkit pipeline's output ever reaches a player-facing surface, adopting the line there is a
**new ledger row**, not a fix — raised as Open Question 2.

---

## 4. The missing-registry decision, and its justification

**Decision (already implemented at `report/cli.py:2322-2327`, and now pinned by a test): an
unreadable registry is a HARD REFUSAL, not an empty list.**

```python
from ..briefkit.avoid_list import load_avoid_terms
try:
    avoid_terms = load_avoid_terms()
except (OSError, ValueError) as ex:
    print(f"seedsmith: the IP avoid-list registry could not be read — {ex}", file=sys.stderr)
    return EXIT_CANNOT_RUN
```

**Justification, from the ledger, not from taste:**

- `spec-avoid-list.md:44-45` — *"the helper throws on any shape it cannot read rather than
  guessing"*; `:88` — *"never defaults"*. An empty list is exactly the default the spec forbids.
- `spec:92` — an empty tuple renders an **empty string** "so an adapter never prints an empty
  list". That is an adapter-comfort rule, not a licence to substitute "no registry" for "no terms".
- The distinguishing failure: a brief with no avoid line and a brief produced under an absent
  registry are **indistinguishable in the output**. Silently rendering nothing is the one answer a
  content-safety control must never give — the run looks clean and is not.
- **IC-3 does not forbid this.** IC-3 forbids an *answer-side* check blocking generation
  (`spec:12-16,33`: "the scan is a release gate and must not block generation", "no model call, no
  retry and no answer-side refusal"). A refusal to *start* because the prompt's own inputs are
  unreadable is a precondition failure, not an answer-side verdict: it costs zero model calls, and
  the code's own comment says so ("a missing registry is a hard error, never silently an empty list
  — an absent avoid line must not read as 'nothing to avoid'"). The gate stays the release scan.
- It refuses **before** the tree loop and before any call, so it cannot waste a run.

**The contrary case, and why it does not apply here.** The narrative voice-exemplar reader
(`adapters/narrative/character_vocab.py:281-291`) is deliberately **fail-open** (`except Exception:
return ()`), citing IC-3. Two things are true there and must not be conflated: fail-open is
defensible *in direction* for a prompt-hygiene check, but that reader **also imports a path that
does not exist** — `from ....ip_censor import avoid_list` resolves to `seedsmith.ip_censor`, which is
not a package here (`Test-Path tools/seedsmith/seedsmith/ip_censor` → `False`; the real module is
`seedsmith.briefkit.avoid_list`). So it returns `()` unconditionally, and its own test
(`test_narrative_character_vocab.py:172-176`) silently **skips** its mark check with a printed note.
A "documented soft edge" that can never be anything but empty is Finding 3.

---

## 5. Verification — real commands, real output

### 5.1 The 14 tests

```
$ $env:PYTHONPATH="gk-forge/tools/seedsmith"
$ python -m pytest gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py -q
..............                                                           [100%]
14 passed in 0.31s
```

### 5.2 The whole seedsmith suite — run twice at this head, plus a third with my two tests added

```
$ PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/ -q
6 failed, 4701 passed, 4 skipped, 1 warning, 5017 subtests passed in 1379.16s (0:22:59)   # run 1
6 failed, 4701 passed, 4 skipped, 1 warning, 5017 subtests passed in 1366.50s (0:22:46)   # run 2
```

The six failures, each attributed to a cause **outside** the avoid-list surface:

| Failing test | Cause | Proven how |
|---|---|---|
| `test_guard_population_pin.py::RealTreeTests::test_P1_backlog_stays_empty` | 1 P1 finding, and it is **`gk-core/tests/tools/test_union_append_only.py:508`** — a repo-root test from the `union-append-only` program (record `[merged]`), not this one | `python gk-core/scripts/guard-population-pin.py` → names the file and line; its scanned scopes are `tests` and `gk-forge/tools/seedsmith/tests`, and it does **not** flag `test_briefkit_avoid_list.py` |
| `…::test_the_real_scan_runs_clean_and_the_backlog_stays_closed` | the same single finding | same run |
| `test_tool_invocation_guard.py::test_every_python_file_under_the_tool_is_inside_a_scanned_scope` | the **gitignored local virtualenv** `tools/seedsmith/.venv-verify/` — 1,974 `.py` files the guard's `rglob` walks. `SCANNED_SCOPES = ("seedsmith", "tests")`, so `seedsmith/briefkit/avoid_list.py` **is** scanned and is **not** in the list | `git check-ignore -v` → `.gitignore:135`; and I re-ran the guard's own body with only that one directory filtered: **result `[]`** (vs 1,974 with it present) |
| `test_topology_repair.py::test_written_partitions_are_lf_only` | `repair_set_classes` writes `set-charm-gen.ledger.json` with **CRLF** on Windows | the assertion text names the file and the `\r\n` bytes |
| `test_tree_plan_emit.py::RosterAndVocabularyTests::test_property_vocabulary_counts_match_the_spec_table` | passive-tree property vocabulary drift: `atomAttachPoint` 9 vs the spec table's 7 | the assertion |
| `test_tree_plan_emit.py::EmitCheckRoundTripTests::test_the_real_committed_plan_agrees_with_a_fresh_check` | the same drift, via `plan_emit.check` (`atomKind` 18 vs 16 too) | the diff list |

**A stale note in the repo's own contributor guide, worth correcting at this head:**
`AGENTS.md` says *"`test_actions_description_completeness` fails pre-existing on a clean HEAD"* and
tells an agent to *"[c]onfirm a failure already exists before blaming your change"*. At `3460de325`
it **does not fail** — it appears nowhere in the `FAILED` list of either run (`test_items_adapter`
likewise). The instruction's *method* is right and I followed it; its example is out of date, and an
agent who trusted the sentence instead of the run would have gone looking for a failure that is not
there.

**"Pre-existing" is a structural fact here, not a claim.** Before this session I changed **zero**
files under `gk-forge/tools/seedsmith` (`git status --porcelain gk-forge/tools/seedsmith` → empty), so runs 1 and 2
*are* runs of the head I started from. The one caveat is stated rather than hidden: on a truly clean
CI checkout, the `.venv-verify` failure would not occur (proved above by filtering it); the other
five would, and they are owned by the vocabulary / setgen / union-append streams, not this fence.

### 5.3 Falsification — the wiring is load-bearing

**The 3 tests the brief named, against the exact pre-wiring source.** I extracted
`adapters/trees/nodegen/brief.py` from **`93a2e16d9^`** (no `avoid_terms`, no `avoid_list` import,
`PROMPT_VERSION = "tree-language/3"`) into an out-of-tree copy of the package and ran the 14 there:

```
$ PYTHONPATH=<temp copy> python -m pytest <temp>/tests/test_briefkit_avoid_list.py -q
E  TypeError: render_brief() got an unexpected keyword argument 'avoid_terms'
FAILED ::TreeBriefAdoptionTests::test_no_fixture_mark_spelling_appears_outside_the_avoid_line
FAILED ::TreeBriefAdoptionTests::test_the_avoid_line_is_separate_from_the_motif_avoid_line
FAILED ::TreeBriefAdoptionTests::test_the_tree_brief_contains_the_avoid_line
3 failed, 11 passed in 47.65s
```

Exactly the 3 the brief predicted, with exactly the predicted error; the other 11 pass — so the
tests are specific to the wiring and not incidentally green. (The out-of-tree copy cannot host the
*CLI* test: the package resolves the repo `data/` root from its own path. Hence §5.4.)

### 5.4 My two new tests, each falsified in-tree

I added them to `tests/adapters/trees/test_nodegen_cli.py` (the idiomatic home — it owns the CLI
refusal paths and the shared `raising_call` "zero model calls" harness). They pin the two halves of
§4 that had **no** coverage anywhere: the registry read at the CLI seam, and the refusal.

| Mutation (one line, in my fence, reverted immediately) | Result |
|---|---|
| drop `avoid_terms=avoid_terms` from the sample-brief call (`cli.py:2373`) | `test_the_avoid_list_reaches_the_rendered_sample_brief` **FAILS** — the rendered brief carries no avoid line |
| replace `return EXIT_CANNOT_RUN` with `avoid_terms = ()` (the fail-open variant) at `cli.py:2325-2327` | `test_an_unreadable_avoid_list_registry_is_refused_not_silently_empty` **FAILS** — `AssertionError: 0 != 2` (`EXIT_CLEAN` instead of `EXIT_CANNOT_RUN`) |

The second is the falsification that matters for a content-safety control: **the test distinguishes
the two directions**, so a later "make it tolerant" edit turns it red.

**Restore was byte-exact**, not approximate (the CRLF trap): SHA-256 of
`seedsmith/report/cli.py` before the mutations and after both `git checkout --` restores —
`BE276CD0A14004E3A8D967523B179AB3823579F374986405A3EA70DD879CC6F1`, identical. The file is LF-only
(0 CRLF lines of 235,464 bytes), and it was never written by a script.

### 5.5 Determinism and the casefold/sort claims — proved, not read off the docstring

Against the **real** committed registry (`gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json`):

```
count: 12
terms: ('crazy dave', 'crazy-dave', 'dr-zomboss', 'dr. zomboss', 'overwatch', 'penny',
        'plant vs zombie', 'plants versus zombies', 'plants vs zombies', 'plants vs. zombies',
        'pvz', 'zomboss')
two loads byte-identical: True   (sha256 of the JSON tuple: d43a4c35186f2121)
casefold-unique:        True   (12 folds, 12 distinct)
sorted by casefold:     True
render twice identical: True   (sha256 of the line: 71723b3dd1760f1a)
```

I also ran the same three properties on the **fixture** (the 14 tests' scope) and the
file-order-independence test in the suite covers reordering. Note the two *different* orders agree
here (`sorted by raw str: True`) — that is **coincidence for this data, not a property of the
helper**; the code sorts by `key=str.casefold` (`avoid_list.py:78`), which is the correct choice and
the one the docstring claims.

### 5.6 Scoped gate for the one file I changed

```
$ python gk-core/scripts/verify-change.py --paths gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_cli.py \
                                 --session ipc-avoid-list-20260926
23 passed in 80.42s (0:01:20)
Verification plan:
  gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_cli.py -> seedsmith-tests (focused)
  pytest: seedsmith
  full evidence: CI/nightly/release
exit=0
```

And the trees/briefkit neighbourhood, run earlier: **605 passed, 27 subtests**.

### 5.7 Fence check

`python scripts/session-boundary-check.py --session ipc-avoid-list-20260926` → **`[session-boundary]
clean for 'ipc-avoid-list-20260926'`, exit 0**. Independently, I read every
`tasks/sessions/*.json` and matched each **active** record's `paths` against `tools/seedsmith/x.py`:
**only my own record claims it** (4 active records total). The two dirty
`.commandcode/taste/**` files and the untracked `tasks/sessions/numeric-types-dedup-20260926.json`
were left untouched, and every commit here names explicit paths.

---

## 6. What remains unproven — stated, not glossed

- **IC-4.1's corpus and gate half was not re-verified by me.** The `Overwatch Protocol` →
  `Structural Integrity Protocol` regeneration, the `supersededRecord` bookkeeping and
  "scan reports no `overwatch` finding" are ledger claims (`todo:579-606`). I did **not** run
  `python -m ipcensor.report scan` and I did **not** run a generation pass; I read the node file and
  confirmed the prompt-version distribution, nothing more. A regeneration needs the local model
  endpoint, so it was out of reach by design.
- **The release gate itself.** IC-3 makes the scan a release gate; the wiring is the *free prompt
  half* only. Whether the gate is green on the current corpus is Checkpoint 4/5's business
  (`todo:514-518,615-617`), not this seam's.
- **`tree-language/4` makes the whole committed node corpus stale.** Measured over
  `gk-data/packs/fusion/data/seed/passive-tree/nodes/*.json`: **2,019 nodes, of which 2,018 are stale** under the current
  `PROMPT_VERSION` (1,319 with **no** `promptVersion`, 699 at `tree-language/3`, 1 at `/4`) — and
  `plan_run`'s own rule is "ABSENT or DIFFERENT → stale". A bare
  `trees generate --supersede` today would therefore re-roll the **entire corpus** (real model
  time). That is the designed cost of a prompt-version bump and `--node` exists for it, but the
  number is a reading, not a constant, and no ledger row carries it. **T16's note does not state
  it.**
- **The uniques adoption and the prompt-hygiene criterion are unproven** — Finding 1.
- **The species-tree generation path carries no avoid list** — Finding 2. Not a test gap; a wiring
  gap.
- **No test anywhere pins the narrative reader's non-empty case** — Finding 3.
- I ran the full suite **three times** — two at the untouched head, one with my two tests — and
  diffed the failure sets (§7). A release-level claim is CI/nightly's; I am not making one.

---

## 7. The third full-suite run (with my two tests in the tree)

Same command, same head, after adding the two contract tests of §5.4:

```
$ PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/ -q
6 failed, 4703 passed, 4 skipped, 1 warning, 5017 subtests passed in 1383.97s (0:23:03)
```

Diffed against the run-2 baseline **programmatically** (the two `FAILED` lists compared as sets, not
by eye): **identical — 6 = 6, `fa == fb` is `True`**, and every one is a row in §5.2's table. The
pass count moved **4701 → 4703**, which is exactly the two tests I added; the skip count, the
warning count and the subtest count are unchanged. So the delta this session introduced into the
whole suite is `+2 passed, +0 failed`, measured rather than argued.

---

## 8. Findings for the manager (not mine to land)

### Finding 1 — T15 is open, and a real franchise name still ships inside a live prompt

`tasks/ip-censor-todo.md:536` (T15) is `[ ]`. Verified at this head:

- `adapters/items/uniques/briefs.py:283-284` — `SYSTEM_PROMPT` opens *"You author identity for a
  **Diablo-style** unique item…"*. This is the exact string `spec:35` and T15's first acceptance
  bullet name. It is a **shipped** prompt, not a comment.
- `build_brief` (`briefs.py:306`) takes no `avoid_terms` and renders no avoid line.
- No uniques test asserts an avoid line (`test_unique_briefs.py` covers schema/`acquisition_for_band`/
  `role_for_cell` only).

**Why I did not simply do it:** T15 is a separate ledger row with its own acceptance, and its
acceptance contains a decision with a data consequence I am not placed to make — changing a shipped
`SYSTEM_PROMPT` in a pipeline that **records no prompt version** means the corpus silently diverges
from the brief that produced it, with no provenance stamp to detect it. (T15's own text anticipates
this: "If the uniques pipeline records a prompt version, it is bumped; if it records none (none
found …), the ledger says so.") That is a program/owner call. Also note a citation drift to resolve
first: the ledger names `briefs.py:284`, the spec names `:267`; the string is at **`:284`** today.

### Finding 2 — the second production caller silently renders no avoid list

`adapters/trees/species/generate_tree.py:224-232` builds `NodeGenerationInputs` **without**
`avoid_terms`. The field defaults to `()` (`run.py:595`) precisely so pre-T16 construction sites are
unchanged — which is right for compatibility and wrong for a content-safety control. Consequence:
every **species-tree node brief** (the live BCU2.12 species generation path) carries no IP avoid
line, with no error and no signal. The `trees` CLI path resolves the registry fail-closed
(`cli.py:2322`); this one resolves nothing.

One-line shape of the fix, if the program wants it: resolve `load_avoid_terms()` in
`generate_tree.py` with the same `except (OSError, ValueError) → refuse` treatment, and pass it.
**The consequence to weigh first:** it changes the species prompt, so under `plan_run`'s rule every
species row whose `promptVersion` is absent or older becomes stale — model calls and a re-roll
decision. That is why it belongs to the program, not to a verification lane.

### Finding 3 — a documented soft edge that can never be anything but empty

`adapters/narrative/character_vocab.py:281-291` reads
`from ....ip_censor import avoid_list` → `seedsmith.ip_censor`, **a package that does not exist**
(the helper is `seedsmith.briefkit.avoid_list`, per `ip-censor-plan.md:311`). Fail-open means it
returns `()` unconditionally, and `test_narrative_character_vocab.py:172-176` **skips its mark
check with a printed note** rather than failing. A control that is always-off and reports itself as
"absent in this tree" is worse than one that is absent: it makes the skip look intentional forever.
One-line fix (point it at `....briefkit.avoid_list`), but it belongs to the `narrative-seed` program
(module 15 / `lore-packet`), and turning it on makes that test start asserting for the first time.

---

## 9. Open questions

1. **Should the species path adopt the avoid list (Finding 2), and who pays the re-roll?** It is
   the last production node-brief path without the control.
2. **Is `briefkit/render.py:82` a third adopter row?** If the briefkit pipeline's output reaches a
   player-facing surface, IC-3's "every adapter" criterion is unmet by construction. No ledger row
   exists; the spec's Project Structure does not list it. I did not touch it.
3. **T15's prompt-version question** (Finding 1): a shipped `SYSTEM_PROMPT` change in a pipeline
   with no provenance stamp — accept the divergence, or add a version stamp first?
4. **Is the 2,018-node staleness under `tree-language/4` intended to stand?** A bare
   `trees generate --supersede` re-rolls everything. If that is the accepted state, the number
   belongs in the T16 note; if not, the corpus re-roll is a costed decision.
5. **Should the six pre-existing suite failures be routed?** They belong to
   `union-append-only` (1 P1 pin), the vocabulary/binder wave (2 vocabulary-drift), setgen CRLF (1),
   and a machine-local `.venv-verify` (1, CI-invisible). None is in this fence; this report names
   them rather than working around them.

---

## 10. What this session changed

**One test file**, plus this report and the session record. **No production code was changed** —
the wiring was already correct and complete for the `trees` path, and re-touching it would have been
a cosmetic diff over `93a2e16d9`.

- `gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_cli.py` — **+2 tests**:
  `test_the_avoid_list_reaches_the_rendered_sample_brief` (the registry→caller→brief wire, via a
  fixture registry with invented marks, patching the helper's own default path so it also pins
  *where* the CLI reads from) and
  `test_an_unreadable_avoid_list_registry_is_refused_not_silently_empty` (the fail-closed half,
  asserting `EXIT_CANNOT_RUN` and the refusal message, with `raising_call` in place so a model call
  would raise).
- `tasks/reports/ipc-avoid-list-20260926.md` (this file), `tasks/sessions/ipc-avoid-list-20260926.json`.

**Not touched:** the three staged files (untouched **byte-for-byte** — the previous lane's spec, and
a test edited to pass is the failure mode this repo keeps writing incident notes about);
`data/**`, `src/**`, `web/**`, `tasks/ip-censor-todo.md`, and every other program's ledger.
