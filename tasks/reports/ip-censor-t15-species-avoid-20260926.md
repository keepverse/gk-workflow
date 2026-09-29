# ip-censor T15 + the species avoid-list — lane report

**Lane:** `ip-censor-t15-species-avoid-20260926` · **Program:** `ip-censor` · **Mode:** direct on
`features/mega-merge` · **Start commit:** `10ba26399` · **Status:** code + tests complete, not merged
(the manager reviews the SHA).

Everything below is a reading I took in this tree. Where I could not run something, it says so.

---

## 0. Fence check (run before the first edit)

```
python scripts/session-boundary-check.py --session ip-censor-t15-species-avoid-20260926
  → [session-boundary] clean for 'ip-censor-t15-species-avoid-20260926'   (exit 0)
```

Independently, a sweep of every `tasks/sessions/*.json` with `status == "active"` found **four**
records — `mega-merge-program-manager-20260925-f78e`, `numeric-types-dedup-20260926`,
`ps1-ban-manager-20260926`, and `_template.json` — and **none of them claims `gk-forge/tools/seedsmith/**`**.
The records that do claim seedsmith paths (`ipc-avoid-list-20260926`,
`resume-00-composite-acceptance-20260925`, `passive-tree-j9-vote`, `item-seedgen-genfix`,
`species-gear-chain-*`, `seedsmith-gen-repair-*`, `narrative-seed-2`, `creature-seed-rank`,
`empire-progression-3/4`) are all `merged` or `abandoned`, so none of them fences this path.

`git status` at start showed two modified `.commandcode/taste/**` files (the ps1-ban lane) and one
untracked session record from another lane. **Both left untouched throughout**; every commit below
stages explicit paths.

Fence honoured: `gk-forge/tools/seedsmith/**`, this report, and my session record. Not touched:
`scripts/**` (ps1-ban owns it), `data/**` (generator-first), `src/**`, `web/**`,
`tasks/ip-censor-todo.md` and every other program ledger.

---

## 1. What T15 and T16 require, and whether the code agreed

### T15 — `tasks/ip-censor-todo.md:536-549`

> **T15 Uniques brief adopts the avoid line and drops its franchise citation.** *Depends:* T14.

Four acceptance clauses. Measured against the code at `10ba26399`:

| Clause | Code at start | Agreed? |
|---|---|---|
| "The uniques system text no longer names a franchise (`briefs.py:284`, 'a Diablo-style unique item')" | `briefs.py:283-284` shipped exactly that string | **no** — the finding is real |
| "The rendered uniques brief (fixture registry) contains the avoid line" | `build_brief` had **no** avoid parameter and `briefkit.avoid_list` was never imported by anything under `adapters/items/` | **no** — the *other* half of T15 was also open, and the brief I was given did not mention it |
| "…and no fixture `franchise-mark` spelling appears outside that line" | vacuously true (no line, no spelling) | vacuous |
| "If the uniques pipeline records a prompt version, it is bumped; if it records none (none found in `adapters/items/uniques/` on 2026-09-19), the ledger says so" | see below | **half true — the ledger's premise is incomplete** |

So T15 was **entirely open**, not half open, and the earlier lane's note
(`tasks/sessions/ipc-avoid-list-20260926.json:15`) that framed it as "*T15 (uniques brief adopts the
avoid line, drops the 'Diablo-style' citation …) is a separate ledger row, still open*" was right about
the row and wrong to imply the avoid-line half was done — `grep` for `avoid_list|render_avoid_line`
across `gk-forge/tools/seedsmith` at start found **zero** hits under `adapters/items/`.

**The prompt-version clause, measured.** `grep -n "promptVersion|PROMPT_VERSION"` over
`gk-forge/tools/seedsmith/seedsmith/adapters/items/` returns 29 matches; **none** is under
`adapters/items/uniques/`. So the ledger's parenthetical is still accurate *about the adapter*. But
the shipped corpus does record one: all **18** files in `gk-data/packs/fusion/data/seed/items/uniques/*.json` carry
`_meta.promptVersion: 1` (alongside `batch`, `partition`, `contractVersion`, `registryVersions`,
`exemplarVersion`, `model`, `authoredUtc`, `sourceRef`). No module under
`adapters/items/uniques/**` writes that `_meta` block — grep finds no `promptVersion` there at all —
so the value is hand-set in data, not generator-owned.

That makes T15's clause ("bumped") **actionable but not actionable in this fence**: the version lives
in `data/**` (generator-first, and no corpus regeneration is authorised in this lane) and the emit
path that would own it does not exist in the adapter. **Filed as finding F3 below.**

### T16 — the species half, which is not in T16's own file list

T16's row (`todo:551-613`, marked `[x]`) names `nodegen/brief.py`, `report/cli.py`, `nodegen/run.py`,
and the nodegen tests. It does **not** name `adapters/trees/species/generate_tree.py`, and it does
not claim the species path. So the species gap is real and **unowned by any closed row** — the same
"needs an owning task" shape `ip-censor-plan.md:25` records for IC-4.2. IC-3/IC-4 as a whole
("avoid-list reaches every adapter whose output reaches a player-facing surface",
`spec-avoid-list.md:30-32`) is what the species path violates.

Measured, as the brief stated: `generate_tree.py` is 330 lines and contains **zero** occurrences of
the substring `avoid`. Its `inputs_for` built `NodeGenerationInputs` with no `avoid_terms`, while the
generic CLI's own `inputs_for` (`report/cli.py:2438`) has passed `avoid_terms` since `93a2e16d9`. The
mechanism existed; the species caller never adopted it.

**Consequence, sized:** the species path writes 40 nodes per species into the shared
`gk-data/packs/fusion/data/seed/passive-tree/nodes/<speciesId>.json`, and nine such files are committed
(`AbyssSwordStar`, `AcientSunNut`, `AllPeater`, `Apple`, `ArmedGargantuar`, `ArmoredImpZombie`,
`AshThreePeater`, `BalloonZombie`, `BambooDragon`). Every one of those node briefs went to the model
with no IP protection.

---

## 2. Finding 1 — the prompt reword, and why it does not weaken the prompt

`gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:298-315`

**Before**

> You author identity for a **Diablo-style** unique item in a JSON object matching the given schema.

**After**

> You author identity for a **single hand-placed unique item — a named one-off built on a real base
> type, carrying its own fixed effects** — in a JSON object matching the given schema.

No allowlist, no suppression, no exception. The word is gone because the sentence that needed it is
gone.

**Why this constrains the model at least as tightly, clause by clause.** The old sentence's only
load-bearing content was *"this is a dark-fantasy action-RPG unique item"* — a genre label doing
double duty as the artifact description. T15's own acceptance says style must instead arrive
"through the adapter's own exemplars and anchor lines", so the genre label was the thing to drop. The
replacement spends the same slot on the *shape* of the artifact, which is strictly more informative
about what is being authored and is the part a model can act on:

- **single hand-placed** — it is authored once and lives at a fixed slot, not rolled. This is the
  fact that separates a unique from every other item kind in this corpus.
- **named one-off** — it carries its own identity (`name`/`nameKey`), which is exactly what the three
  legal name shapes below exist to serve.
- **built on a real base type** — restates, in the opening, the closed-`baseType` rule the rest of the
  prompt already states, one clause earlier than before.
- **carrying its own fixed effects** — restates `fixedAtoms` + the single optional `varianceSlot`
  before the model reaches the sentence that enumerates them.

Measured, not asserted: the prompt went from **1586 to 1670 characters**. It is longer. A rewording
that bought room for the removal by deleting a constraint would have gone the other way.

**And the anti-weakening guard, so this cannot be quietly undone later.**
`SystemPromptHygieneTests.REQUIRED_CLAUSES` in `gk-forge/tools/seedsmith/tests/test_unique_briefs.py` pins
**15** load-bearing clauses with the reason each exists, and
`test_the_system_prompt_still_carries_every_schema_rule_it_carried_before` asserts all 15. The clauses
cover everything the brief named: the eight PLANNED fields (`copy its const value verbatim`), the
closed `baseType` list, the real atom-family list (`ONLY from the real atom-family list given`,
`never invent a`), exactly-one-of for `massClass`/`materialNature`/`combatPosture`, the three exact
`name` shapes (`compound` / `of-construct` / `fusion`, each with its own example), the
engine-reserved fourth shape, the plural/possessive/connective rule, and the no-numbers rule.

**This guard is not a description of my new text.** It was written against the *pre-change* prompt and
**passes against the original** (15 subtests green in the falsification run below, on reverted
production code). That is what makes it a contract rather than a snapshot.

### The deny source, and the honest limit of a deny-source-driven test

The brief asked for the strongest check to be *"a test that scans shipped prompt strings in
`gk-forge/tools/seedsmith/seedsmith/**` for a franchise name from the program's own deny source, not a
hardcoded word"* and to report rather than invent a second list if the deny source is unusable.

**The deny source is machine-readable and I used it.** `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json`
parses as `schemaVersion: 1` + `groups[].{mark, category, scope, remediation, aliases, admission}`;
`seedsmith.briefkit.avoid_list.load_avoid_terms` reads it, and `ipcensor.registry.parse_registry` is
its validating authority. 5 groups, all `category: "franchise-mark"`, 12 in-scope spellings.
`PromptHygieneTests.test_no_mark_the_deny_source_carries_appears_in_a_shipped_prompt` reads that file
**at run time**, selects the spellings whose own effective scope includes `generator-prompt` (the
same surface-and-scope conjunction `Registry.enforces` applies, `ipcensor/registry.py:239-249`), and
asserts none appears in any shipped string literal. No real spelling is written into any seedsmith
file — which matters, because `gk-forge/tools/seedsmith/**` is itself an enforced `generator-prompt` surface
(`scope-policy.v1.json:28-33`).

**But it is structurally incapable of catching this finding, and that is the real defect.** The
registry carries no row for the brand the prompt was citing. `Registry.scope_for` returns the *empty
set* for an unknown mark (`ipcensor/registry.py:230-238`, "never to 'everything'"), so the word was
not merely unenforced — it was **not a finding at all**. Measured on the pre-change tree:

```
python -m ipcensor.report scan --tree gk-forge/tools/seedsmith --bucket generator-prompt --fail-on enforced
  → 45 finding(s)      EXIT=0
```

45 report-only findings (all `pvz` / `dr-zomboss`, out of scope on this surface per IC-1b), **zero
enforced, exit 0 — while the prompt shipped the franchise name.** The release gate was green on a
prompt that violated the program's own ruling. That is the false green this program exists to
prevent, and it is a **registry coverage gap in `gk-data/packs/fusion/data/seed/ip-censor/**`, which is outside this
lane's fence** → finding **F1**.

So the durable deny-source test above is necessary but not sufficient, and the second rule carries the
case it cannot see:

`PromptHygieneTests.test_no_shipped_string_cites_another_franchise_by_name` applies a **grammar** of
the citation — `\b[A-Z][a-z]{2,}-(?:style|like|esque|inspired|flavou?red|tone)\b` — to **every string
literal in every `.py` file under `gk-forge/tools/seedsmith/seedsmith/**`**, read through `ast` so a citation
cannot hide in a concatenation or a docstring. It names no franchise, so it holds for a brand nobody
has registered.

I measured the grammar's noise before committing to it, because a guard that cries wolf is worse
than none. Over all 34 948 string literals in the package at authoring time:

| pattern | distinct matches |
|---|---|
| bare `\b[A-Z][a-z]{2,}-[a-z]{3,}\b` | **109** — unusable (every hyphenated capitalised comment) |
| `…-(?:style\|like\|esque\|inspired\|flavou?red\|tone\|ish)\b` | 5 — still noisy (4× `Pure-ish`) |
| **shipped pattern** (same, without `-ish`) | **1** — and that one is the violation |

`SystemPromptHygieneTests.test_the_system_prompt_cites_no_franchise_as_a_style_reference` restates the
same grammar narrowly at the adapter seam, so the finding is also caught by the uniques adapter's own
test file rather than only by a cross-package test.

**Non-vacuity, split so neither half can rot.**
`test_this_surface_is_an_enforced_one_and_the_deny_source_is_readable` asserts (a) `generator-prompt`
is still in `scope-policy.v1.json`'s `enforcedSurfaces` — a policy fact that does not go stale — and
(b) the registry is present, `schemaVersion: 1`, and yields at least one player-facing spelling
(readability is already thrown by `load_avoid_terms`; repeated so the failure names this contract).

**What it deliberately does NOT assert**, because I got it wrong first and the correction matters: my
initial version required *at least one mark in scope on `generator-prompt`*, i.e. it tied this test's
red to the existence of the `overwatch` row. That is a **false red waiting to happen** — retiring
`overwatch` is a *correct* act now that IC-4.1's live node is clean, and a test that punishes it
trains people to weaken tests rather than to update the ledger. So the selection's own contract moved
to the fixture, where it can never rot and where no real content can break it:
`test_the_selection_honours_group_scope_and_an_alias_own_narrower_scope` proves the selection reads
the group's scope (empty on the player-scoped fixture, non-empty once the group is promoted onto the
surface) and honours an alias's own narrower scope (`Zqx` stays excluded even after its group is
promoted, so a group scope cannot leak onto an alias that narrowed itself). That test is itself
falsifiable — a selection that ignored scope entirely would fail its very first assertion.

No count over the real registry is pinned anywhere in these tests (`validation-ssot.md`): the registry
is a closed vocabulary a person edits, and a row added tomorrow must not redden them.

---

## 3. Finding 2 — the species threading, with `file:line`

Threaded through the **existing** helper. No second mechanism, no per-adapter list.

| What | Where | Line |
|---|---|---|
| import the shared reader | `gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py` | `199` — `from ....briefkit.avoid_list import load_avoid_terms` |
| read once, fail closed, **before** the favour fit / plan / quota / vocabulary builds | same | `202-208` |
| pass it into the species `NodeGenerationInputs` | same | `259` — `avoid_terms=avoid_terms)` |
| the rendered result, unchanged code below | `adapters/trees/nodegen/brief.py:168-169` | already rendered `render_avoid_line(avoid_terms)` as its own line |
| the transport, unchanged | `adapters/trees/nodegen/run.py:595` (field), `:875` (into `render_brief`) | pre-existing from `93a2e16d9` |

Reading it **first**, before the expensive work, is deliberate: a refused run then has built no plan
and written nothing. The species test asserts that too
(`test_an_unreadable_avoid_registry_refuses_the_run_instead_of_rendering_nothing` checks no
`nodes/AbyssSwordStar.json` appears).

### Why `PROMPT_VERSION` was deliberately **not** bumped

`nodegen/brief.py:63` is `tree-language/4`, already carrying the avoid line. Bumping to `/5` would
mark **every** committed node stale — and `--supersede` re-rolls every ledger row whose
`promptVersion` differs (`ip-censor-plan.md:144`, `report/cli.py:3039-3045`), i.e. it would demand
regenerating the whole 1677-node corpus. Out of fence, and explicitly not authorised here.

Measured, so the omission is safe rather than convenient — prompt versions across
`gk-data/packs/fusion/data/seed/passive-tree/nodes/*.json`:

```
{None: 1319, 'tree-language/3': 699, 'tree-language/4': 1}
```

Exactly **one** node in the entire corpus is at `/4`: the one T16 regenerated
(`command.json` → `skill.command-def-t8-n0`, *Structural Integrity Protocol*). It was generated
**with** the avoid line. Every species row is at `/3` or `None`, so **no committed row was generated
under `/4` without the avoid line** — the version stamp already separates the two populations
correctly and needs no bump. The nine species files will pick the avoid line up on their next
`--supersede` (their `/3` ≠ `/4` already makes them stale), which is a generation run, not an edit.

---

## 4. The missing-registry decision: **hard refusal**, justified from the ledger

A missing or unreadable registry **refuses the run**. It does not degrade to an empty list.

The ledger says so three times, and I checked each against shipped code rather than prose:

1. **T14's own acceptance** (`todo:529`): "`load_avoid_terms()` … Throws naming the key on a missing
   `groups` or `scope`". Shipped and confirmed: `avoid_list.py:48,55,59,64,69` all raise.
2. **T16's shipped caller** (`report/cli.py:2318-2327`): *"A missing registry is a hard error, never
   silently an empty list — an absent avoid line must not read as 'nothing to avoid'"* → prints and
   returns `EXIT_CANNOT_RUN`. This is the precedent I copied, so there is one rule with two callers
   rather than two rules.
3. **The spec's Boundaries** (`spec-avoid-list.md:141`): *"Never: import `ipcensor`; keep a per-adapter
   IP list; hand-edit a generated row to remove a mark; cite another franchise in a brief."*

**Why not the empty list, against IC-3.** IC-3 says *"the scan is a release gate and must not block
generation — block generation will cost more than help."* That is not in tension here, and the
distinction is the whole answer: IC-3 forbids an **answer-side** check — a retry, a re-ask, or a
rejection of the model's output on the strength of the list. There is none. Nothing is re-asked, no
answer is rejected, no call is spent. What is refused is a **missing input file**: the brief cannot be
rendered correctly without it. The failure mode IC-3 was ruling out ("generation blocked by IP
findings") cannot occur, because no IP finding is consulted at this point at all.

The empty list is the answer this repo would flag, and it is worse than useless: a brief with no avoid
line reads to the model *and to a reviewer* as "there is nothing to avoid". That is a silent,
green-looking loss of the exact protection IC-3/IC-4 bought.

Each caller refuses in its own vocabulary, matching its own error discipline:

- `generate_tree.py:203-208` → `SpeciesTreeRunError` (the module's own "refused, never silently
  skipped" type, `:94-95`).
- `pipelines.py:221-228` → `UniquesDrawRefused(RuntimeError)`, **new** (`pipelines.py:56-61`). It is
  deliberately a *different* type from `DrawResult(reason=...)`: a refusal happens before any cell is
  drawn, so there is no per-cell outcome to report and retrying a cell could not fix it. The uniques
  test asserts the model was called **zero** times.

Both catch `(OSError, ValueError)` — the helper's own raise plus a genuinely absent file — and re-raise
with the reason chained (`from ex`), so the original message is never lost.

---

## 5. Every caller, and what changed for each

### `uniques.briefs.build_brief` — signature gained a keyword-only parameter with a default

`build_brief(cell, schema, *, role=None, avoid_terms=())`. Checked rather than assumed:

| Caller | Site | Change |
|---|---|---|
| `uniques.pipelines.run_unique_draws` | `pipelines.py:252` | **changed** — now passes `avoid_terms=avoid_terms`, resolved once at `:221-228` |
| `uniques.audit` | `audit.py:164` | unaffected — imports `build_unique_schema` only, never `build_brief` |
| `test_unique_briefs.py` | 2 pre-existing tests | unaffected — pass `(cell, schema)` / `(cell, schema, role=…)` only |
| any positional caller | — | **none exists.** `build_brief` takes `cell` and `schema` positionally and everything else keyword-only, so a new keyword-only parameter with a default cannot collide with a positional argument. I verified this by grep, not by reasoning alone: the only importer of `build_brief` in the whole tool is `pipelines.py:34`. |

**"Cannot break a positional caller" is a claim, so I tested it rather than asserting it.**
`AvoidListAdoptionTests.test_without_terms_the_brief_is_unchanged` asserts the **exact** pre-T15 text
byte for byte, character by character, for the no-terms path. If the parameter had leaked into the
default rendering, that assertion goes red.

### `NodeGenerationInputs` — field already existed; only the species construction site changed

`avoid_terms: Sequence[str] = ()` (`nodegen/run.py:595`) is pre-existing from `93a2e16d9`. I added no
field.

| Construction site | Site | Change |
|---|---|---|
| generic CLI `inputs_for` | `report/cli.py:2430-2439` | **unchanged** — already passed `avoid_terms=avoid_terms` (`:2438`) |
| species `inputs_for` | `generate_tree.py:244-259` | **changed** — now passes it |
| `test_nodegen_language_stage.py` | `:62`, `:741` | unaffected — keyword construction, field defaults |
| `test_nodegen_generate.py` | `:48` | unaffected — `NodeGenerationInputs(**base)` over a base dict |

### `nodegen.brief.render_brief` — untouched

`avoid_terms` was already keyword-only with a `()` default (`brief.py:126`). I did not modify this
function; the species path reaches the existing rendering through it.

### `run_species_tree` — signature unchanged

| Caller | Site | Change |
|---|---|---|
| `_j9_batch_run.py` | `:239` | unaffected — keyword args only; the function resolves terms internally |
| `_j9_poc_run.py` | `:39` | unaffected — same |
| `test_tree_species_generate_tree.py` | 6 pre-existing tests | unaffected — I replaced only the module's `import` line, to also import `SpeciesTreeRunError` |

`git diff` on that test file shows **one** deleted line, and it is the old single-name import.

### `_marks_in_scope_for_prompts` / the shipped-literal sweep — test-local only

Both live in `gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py`. Neither is imported by production
code, so nothing outside the test tree sees them.

---

## 6. Falsification — red before, green after, both real

Method: the three production files were reverted with `git checkout --`, the new tests were run
against the **original** code, then the change was restored with `git apply` of a saved patch and
**verified byte-exact by SHA-256** (all three hashes identical before and after — no
`read_text`/`write_text` round-trip anywhere, which is the CRLF trap). The test files were never
reverted, so the new tests ran against the old code.

### Finding 1 — RED (original production code)

```
python -m pytest gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py::PromptHygieneTests \
  gk-forge/tools/seedsmith/tests/test_unique_briefs.py::SystemPromptHygieneTests \
  gk-forge/tools/seedsmith/tests/test_unique_briefs.py::AvoidListAdoptionTests -q

E  AssertionError: Lists differ: [] != ["gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:284
   cites a brand as a style reference: 'Diablo-style'"]
E  AssertionError: Lists differ: [] != ['Diablo-style']
E  TypeError: build_brief() got an unexpected keyword argument 'avoid_terms'
  → 5 failed, 5 passed, 15 subtests passed in 2.08s
```

The 5 failures are the two citation assertions and the three avoid-line assertions. Note the
**15 subtests passed** — that is `REQUIRED_CLAUSES` passing against the *original* prompt, which is
the proof that the anti-weakening guard is a contract and not a snapshot of my new wording.

### Finding 2 — RED (original production code)

```
python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py::SpeciesAvoidListTests -q

E  AssertionError: 'IP avoid-list — never use these third-party names in a node name, nameKey or
   flavor: crazy dave, crazy-dave, dr-zomboss, …' not found in "Tree: AbyssSwordStar\nBranch:
   offensive.  Depth: shallow.\n…"
E  AssertionError: SpeciesTreeRunError not raised
  → 2 failed in 434.03s (0:07:14)
```

The full 434 s is the honest cost of the red: the original code never reads the registry, so the
refusal test runs the whole species generation to completion before failing.

### GREEN (this change)

```
python -m pytest gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py \
  gk-forge/tools/seedsmith/tests/test_unique_briefs.py gk-forge/tools/seedsmith/tests/test_unique_pipelines.py \
  gk-forge/tools/seedsmith/tests/adapters/trees/ -q
  → 665 passed, 44 subtests passed in 88.61s (0:01:28)
```

Cost note for the manager: the new species tests exit after the **first** node brief
(`_StopAfterFirstNode`), because the real tree-plan / quota / vocabulary builds dominate and the brief
is rendered per node from the same `inputs_for`. The whole species file — 6 pre-existing full runs
plus my 2 — is **8 passed in 1.21 s**. The 7 minutes above is a property of the *red*, not a permanent
tax I added.

### Determinism, proven rather than trusted

`RenderAvoidLineTests` gains two assertions the helper's docstring only claimed:

- `test_terms_are_casefold_unique_and_sorted_as_a_property_not_a_fixture_list` — over **both** the
  fixture and the **real committed registry**: non-empty, `len(set(casefolds)) == len(terms)`, and
  `sorted(folded) == folded`, plus two loads equal. It pins **shape**, never a count, so a registry
  row added tomorrow cannot turn it red (`validation-ssot.md`).
- `test_the_rendered_line_is_byte_identical_not_merely_equal` — compares `str.encode("utf-8")`, not
  `str` equality, because a brief's identity is its bytes: the ledger's staleness key hashes the
  rendered text (`pipeline/staleness.py:32-40`). A newline or encoding difference cannot hide behind
  str equality.
- `AvoidListAdoptionTests.test_the_rendered_brief_is_byte_identical_across_renders` — the same byte
  comparison on the **rendered uniques brief** re-rendered from a re-read registry.
- Order-independence was already covered by T14's `test_order_does_not_depend_on_file_order`
  (reversed `groups` → identical terms); I did not duplicate it.

The species brief is byte-deterministic by the same construction (`render_brief` is pure over its
arguments) and I did not add a third copy of that assertion at a cost of minutes per run.

---

## 7. The narrative-reader finding — CONFIRMED, with `file:line`

I was told not to act on this and not to go looking. I found it by accident while auditing the
avoid-list callers, and it is real. **Reported, not fixed** — it is outside this lane's problem
statement.

**The claim is correct.** `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/character_vocab.py:285` does

```python
from ....ip_censor import avoid_list  # type: ignore[attr-defined]
```

inside `avoid_terms()`. Four dots from `seedsmith/adapters/narrative/` resolves to `seedsmith`, and
**`seedsmith/ip_censor` does not exist** — the helper lives at `seedsmith/briefkit/avoid_list.py`
(T14). The bare `except Exception: return ()` at `:290-291` then swallows the `ModuleNotFoundError`,
so `avoid_terms()` is **permanently empty**.

Runtime proof (not inference):

```
$ PYTHONPATH=gk-forge/tools/seedsmith python -c "import importlib; importlib.import_module('seedsmith.ip_censor')"
MISSING seedsmith.ip_censor -> ModuleNotFoundError No module named 'seedsmith.ip_censor'

$ PYTHONPATH=gk-forge/tools/seedsmith python -c "from seedsmith.adapters.narrative.character_vocab import avoid_terms; print(len(avoid_terms()))"
avoid_terms() len = 0
```

And the test built on it **passes by printing a skip**:

```
$ python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py \
    -k cite_no_other_franchise -q -s
voice exemplars: ip-censor's load_avoid_terms helper is absent in this tree -- skipping the mark check (IC-3)
1 passed, 12 deselected in 0.24s
```

`gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py:172-176` — the "intentional skip" branch.
The exemplar lines are therefore never checked against any mark, and the message reports an *absent
helper* when the helper is present under a different name.

**Why the earlier AST sweep missed it, stated as the likely mechanism (not asserted):** the import is
**function-local**, at `character_vocab.py:285` inside `avoid_terms()` — not module level. Verified:

```
ip_censor import at line 285 | module-level: False
```

A sweep of module-level imports cannot see it. I also note, as a caution about the negative result
rather than a correction of intent: a *static* resolver over this package produces large numbers of
false positives, because many of these directories are PEP 420 namespace packages with no
`__init__.py`. My own first two attempts reported 1 113 and then 0 unresolved imports; only the runtime
import was decisive. **`importlib.import_module` on the named module is the check that works here.**

The fix is one import path and one module name — it is **not** mine to make (it is the narrative
adapter's row, `seedsmith-narrative`, not T15/T16), and fixing it would *activate* a check that has
never run against six authored voice exemplars, which is a content decision for its owner. → **F2**.

---

## 8. Findings for the manager (nothing here was actioned)

**F1 — the release gate cannot see this class of finding, and the registry has no row.**
`marks.v1.json` carries 5 groups (`crazy-dave`, `dr-zomboss`, `overwatch`, `penny`, `pvz`), none of
which is the brand the uniques prompt cited, and `Registry.scope_for` returns the empty set for an
unknown mark (`ipcensor/registry.py:230-238`). Measured pre-change:
`scan --tree gk-forge/tools/seedsmith --bucket generator-prompt --fail-on enforced` → **45 findings, exit 0**
with the violation live. A registry row is the durable fix and lives in
`gk-data/packs/fusion/data/seed/ip-censor/_registry/**` — outside this fence. Until it exists, the citation grammar in
`PromptHygieneTests` is the only thing standing between a re-introduction and a green gate.
**Also applies to the narrative reader (F2):** a mark that is unregistered is invisible to both.

**F2 — `character_vocab.avoid_terms()` is permanently empty** (section 7). `character_vocab.py:285`,
swallowed at `:290-291`, reported as an intentional skip at
`test_narrative_character_vocab.py:172-176`. Confirmed at runtime.

**F3 — T15's prompt-version clause is half-true, and the half that is true is not actionable in this
fence.** `adapters/items/uniques/**` records no `PROMPT_VERSION` (29 grep hits under
`adapters/items/`, none under `uniques/`), but all **18** committed `gk-data/packs/fusion/data/seed/items/uniques/*.json`
carry a hand-set `_meta.promptVersion: 1` that no adapter module writes. This change alters the brief,
so `spec-avoid-list.md:138` ("bump an adopter's prompt version when its brief changes") applies — but
the value lives in `data/**` and the emit path that would own it does not exist. **T15's row cannot be
fully closed on this clause without either an adapter-side `PROMPT_VERSION` constant plus an emit path,
or an owner ruling that `_meta.promptVersion: 1` is a frozen hand-set marker.** Owner-gated; reported.

**F4 — the scoped local selector will not run the new cross-package prompt-hygiene tests.**
`python gk-core/scripts/verify-change.py --plan-only --paths <my three files> --session ip-censor-t15-species-avoid-20260926`
resolves correctly:

```
briefs.py     -> seedsmith-items (focused)      [includes test_unique_briefs.py, test_unique_pipelines.py] ✓
pipelines.py  -> seedsmith-items (focused)      [same] ✓
generate_tree.py -> seedsmith-trees (focused)   [includes test_tree_species_generate_tree.py] ✓
```

…but `test_briefkit_avoid_list.py`, where `PromptHygieneTests` lives, is in **no** selected list
(`seedsmith-narrative-briefkit`'s `testFiles` is the glob `test_briefkit*.py`, and that boundary is
selected by `briefkit/**` production paths, of which I changed none). So `verify-change` would not run
the package-wide citation scan. Two facts bound the severity: **CI does run it**
(`ci.yml:592`, `working-directory: gk-forge/tools/seedsmith`, `python -m pytest tests -q` — the whole tree), and
the two fixes that matter for *this* change are covered by files that *are* selected. The one-line
repair is adding `gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py` to `seedsmith-items` and
`seedsmith-trees` in `gk-core/scripts/verification-boundaries.v1.json` — **`scripts/**` is the ps1-ban lane's
fence**, so reported, not done.

**F8 — this working tree's `core.autocrlf=true` puts 1018 committed JSON files on disk as CRLF, and
one LF-only guard reads it.** `test_topology_repair::test_written_partitions_are_lf_only` reads bytes on
disk, so it is red in this checkout and green in a fresh one, on files this change never touched
(measured in §9: HEAD blob 0 CRLF, disk 3728 CRLF, `git diff` empty). Two consequences worth an owner's
attention, neither of them mine to fix: the guard is **environment-sensitive** in a way that makes a
local red indistinguishable from a real one for whoever runs it next, and any future `write_text` over
one of those 1018 files would commit a CRLF rewrite of an LF blob. The declared intent is already
right — `git check-attr` reports `eol: lf` — so the local `core.autocrlf=true` is overriding the
attribute at checkout time. Setting it false for this repo (or relying on the declared attributes) is
the repair. **Reported, not actioned:** `core.autocrlf` is machine-local git config, not a committed
file, and this lane's fence does not reach it.

**F7 — the species path was not an isolated oversight; ~31 other prompt-building modules are in the
same state, and that is a *sized* reading, not a surprise.** IC-3's rule is "every seedsmith adapter
whose output reaches a player-facing surface puts that line in its brief"
(`spec-avoid-list.md:30-32`), but the same spec scopes delivery to "**First adopters**: the
passive-tree node generator (required by IC-4) and the item uniques brief" and defers the rest
("Narrative adapters adopt it when they are built"). So the gap is a *known, deferred* slice — and the
species path was simply the one inside it that nobody had measured.

Measured at the final tree, by a name-based heuristic over `gk-forge/tools/seedsmith/seedsmith/**` (any module
defining `build_brief`/`render_brief`/`SYSTEM_PROMPT` or a `*_PROMPT` constant): **33 candidate
modules, 2 carrying the avoid list** (the tree nodegen brief and, as of this commit, the uniques
brief), 31 not. The 31 include `items/{setgen,combogen,gemgen,materialgen,consumablegen,milestonegen}
/brief.py`, `actions/{family,general,signature}_propose/prompts.py`,
`actions/description_backfill/prompts.py`, `creatures/{fusion,effects,anchor}`, `dungeon/briefs.py`,
`effects/affix/prompts.py`, `narrative/gloss/fill.py`, `trees/identity/prompts.py` and
`trees/species/prompts.py`.

**This reading is a heuristic and I am labelling it as one**: it counts by name, so it includes both
false positives (modules that merely mention a `*_PROMPT` symbol, e.g. `creatures/anchor/provenance.py`,
`workflow/graphs/item_set.py`, which delegate) and any false negatives (a prompt built without one of
those names). It is a **reading, not a constant** — re-measure before quoting it, and do not turn it
into a pinned number. The point is the shape: adoption is a first-adopters slice, not a finished
surface, and **no row in the todo currently owns the remaining 31.** If the manager wants IC-3's
"every adapter" clause actually true, that is a follow-on row with its own fence, not a widening of
this one. **Not actioned here** — each of those modules is a different adapter's row, and adopting
them from this lane would put 31 files across nine adapters into a two-finding change.

**F6 — the shared avoid line is worded for tree nodes, and now reads slightly off-domain in an item
brief.** `briefkit/avoid_list.py:87-88` renders *"never use these third-party names in a **node name**,
nameKey or flavor"*. In the uniques brief that sentence now appears verbatim, where "node name" is the
tree's word, not the item's. A model still reads the intent correctly, so this is cosmetic — and I
deliberately did **not** reword it, for two measured reasons. (1) The spec's own reason for having one
helper is that per-adapter wording is how the lists drift
(`spec-avoid-list.md:18-20`), and T16 already shipped this exact line on the tree path, so a
domain-neutral rewording forks one line into two. (2) Changing the tree brief's rendered text triggers
`spec-avoid-list.md:138` ("bump an adopter's prompt version when its brief changes") →
`tree-language/5` → `--supersede` re-rolls every one of the 1677 committed nodes. Cosmetic wording is
not worth a corpus-wide regeneration, and the call is not mine. **A future one-line change to
`render_avoid_line` should be taken together with a deliberate decision about the tree prompt
version**, not slipped in.

**F5 — the species path was never owned by a row.** T16's file list does not name
`adapters/trees/species/generate_tree.py`, and the todo marks T16 `[x]`. The IC-3/IC-4 requirement it
violated is unowned, the same shape `ip-censor-plan.md:25` records for IC-4.2. The code is now fixed;
**the ledger still needs a row that says so**, or the next reader of T16 will believe the whole of
IC-3's "every adapter" clause is closed. Manager applies.

---

## 9. Verification run

### Whole `gk-forge/tools/seedsmith` suite

```
$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/ -q

6 failed, 4719 passed, 4 skipped, 1 warning, 5034 subtests passed in 1366.95s (0:22:46)

FAILED gk-forge/tools/seedsmith/tests/test_guard_population_pin.py::RealTreeTests::test_P1_backlog_stays_empty
FAILED gk-forge/tools/seedsmith/tests/test_guard_population_pin.py::RealTreeTests::test_the_real_scan_runs_clean_and_the_backlog_stays_closed
FAILED gk-forge/tools/seedsmith/tests/test_tool_invocation_guard.py::test_every_python_file_under_the_tool_is_inside_a_scanned_scope
FAILED gk-forge/tools/seedsmith/tests/test_topology_repair.py::test_written_partitions_are_lf_only
FAILED gk-forge/tools/seedsmith/tests/test_tree_plan_emit.py::RosterAndVocabularyTests::test_property_vocabulary_counts_match_the_spec_table
FAILED gk-forge/tools/seedsmith/tests/test_tree_plan_emit.py::EmitCheckRoundTripTests::test_the_real_committed_plan_agrees_with_a_fresh_check
```

**Six red, and not one of them is mine.** I did not take that on trust: I created a detached
`git worktree` at my start commit `10ba26399`, ran exactly those six nodes there, and split the result.
The worktree was then removed (`git worktree remove --force` + `git worktree prune`); the 180-odd
other registered worktrees were untouched.

**4 of 6 pre-exist on a clean checkout of the commit I started from** (`4 failed, 2 passed in 60.86s`):

| Failing node | Pre-existing? |
|---|---|
| `test_guard_population_pin.py::RealTreeTests::test_P1_backlog_stays_empty` | **yes** |
| `test_guard_population_pin.py::RealTreeTests::test_the_real_scan_runs_clean_and_the_backlog_stays_closed` | **yes** |
| `test_tree_plan_emit.py::RosterAndVocabularyTests::test_property_vocabulary_counts_match_the_spec_table` | **yes** — `9 != 7`, `18 != 16` |
| `test_tree_plan_emit.py::EmitCheckRoundTripTests::test_the_real_committed_plan_agrees_with_a_fresh_check` | **yes** — same two counts, reading committed `gk-data/packs/fusion/data/seed/passive-tree/plan/might.v1.json` |

**2 of 6 pass on the clean checkout and are environmental in this working tree** — so I chased both to
a cause rather than writing them off:

**`test_tool_invocation_guard::test_every_python_file_under_the_tool_is_inside_a_scanned_scope`** — fails
on **1974** files, all of them under `tools/seedsmith/.venv-verify/`. That directory is
`git check-ignore`'d (`.gitignore:135`), holds **0** tracked files, and was created **2026-09-01**,
twenty-five days before this session. My commit adds **zero** new Python files. The clean worktree has
no `.venv-verify` (worktrees do not materialise gitignored paths), which is precisely why the node
passes there. Not caused by this change; caused by a local virtualenv sitting inside the tool tree.

**`test_topology_repair::test_written_partitions_are_lf_only`** — names
`gk-data/packs/fusion/data/seed/items/{charms,sets}/set-charm-gen.ledger.json`, which this change never touches. Cause,
measured at byte level:

```
HEAD blob   (git show HEAD:gk-data/packs/fusion/data/seed/items/charms/set-charm-gen.ledger.json) : 0 CRLF pairs
working tree (same path on disk)                                          : 3728 CRLF pairs
git diff --stat -- <path>                                                 : (empty — identical to HEAD)
git config core.autocrlf                                                  : true
git check-attr text eol -- <path>                                         : text: auto, eol: lf
```

The **committed blob is pure LF**; the on-disk copy is CRLF; git reports no change, because
`core.autocrlf=true` normalises on read and the fresh worktree honoured `eol: lf`. The test reads bytes
**on disk**, so it is red here and green there. Scope of the local drift: **1018** `.json` files under
`gk-data/packs/fusion/data/seed/items` are on-disk CRLF while byte-identical to their HEAD blobs. **This is the CRLF trap
the brief warned about, and I checked whether I had walked into it: all seven of my own edited files
carry 0 CRLF pairs, and `git diff --check` is clean.** The drift predates the session
(mtimes 2026-09-12); it is this checkout's `core.autocrlf`, not this change. → **F8**.

### The path-owned boundary, and the selector's own plan

```
$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest \
  gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py \
  gk-forge/tools/seedsmith/tests/test_unique_briefs.py gk-forge/tools/seedsmith/tests/test_unique_pipelines.py \
  gk-forge/tools/seedsmith/tests/adapters/trees/ -q
  → 665 passed, 44 subtests passed in 88.61s (0:01:28)
```

### Also run, and unchanged by this work:

- `python -m ipcensor.report scan --tree gk-forge/tools/seedsmith --bucket generator-prompt --fail-on enforced`
  → 45 findings, **exit 0** (all report-only `pvz`/`dr-zomboss`, per IC-1b). Identical before and after.
- `python -m ipcensor.report scan --tree data --bucket player-name` (T16 step 5's reading) → 5
  findings, **exit 0**. No `overwatch` in `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json`; the two
  `overwatch` hits are the `supersededRecord` in `tree-language.ledger.json:28543-28544`, which T16's
  own note already accepted by design (`record_superseded` requires the prior row be preserved).
- `git diff --check` → clean (no whitespace or line-ending damage).
- `python scripts/session-boundary-check.py --session ip-censor-t15-species-avoid-20260926` → clean.

**Not run, and why:** `dotnet test` — this change touches no C# and no `.csproj`; there is no
verification boundary from a Python-only `gk-forge/tools/seedsmith` edit to a .NET test project, and
`verify-change`'s plan above confirms it selected none. `npm` — no web change. No deploy: this is a
prompt string and a wiring parameter, nothing that runs in the game.

---

## 10. What remains unproven

- **No corpus was regenerated, and none was asked for.** The reworded prompt and the two new avoid
  lines change what the generator *would* produce; no shipped row reflects either. Per generator-first,
  `gk-data/packs/fusion/data/seed/**` was not touched and no regeneration was run. Whether the reworded prompt yields
  *better* unique names is a model-behaviour question this lane cannot answer — it is only proven not
  to be *less* constrained.
- **The uniques avoid line has never reached a real model call.** The wiring is proven by a
  `FakeCall` capturing the exact `(system, user)` pairs; no live LLM run was made, so the *effect* on
  generated names is unmeasured.
- **The species avoid line has never reached a real model call either** — proven against a stubbed
  `call_model` inside a real `run_species_tree`.
- **The citation grammar is a heuristic.** It is measured at exactly 1 match across the package today,
  but it is a pattern: a citation written as "*Diablo* like" (no hyphen) or "in the style of *Diablo*"
  would not match. It is a backstop behind the deny-source rule, not a substitute for a registry row
  (F1). The failure message says so and tells the reader to check which kind of match they are looking
  at before changing the pattern.
- **F1's registry row does not exist**, so the release gate remains structurally unable to catch this
  class of finding. The in-fence grammar is the only guard, and it is a heuristic.
- **I did not verify `gk-data/packs/fusion/data/seed/items/uniques/**` against the reworded prompt**, and could not: doing so
  means regenerating, which this lane may not do.
- **The full-suite reading is a reading, not a guarantee** — CI/nightly owns the unfiltered run.

## 11. Open questions

1. **F3 is owner-gated.** Is `data/seed/items/uniques/_meta.promptVersion: 1` a frozen hand-set marker
   (no bump owed), or should the uniques adapter grow a `PROMPT_VERSION` constant and an emit path so
   the corpus's prompt version becomes generator-owned like `tree-language/4`? T15's clause assumes
   the latter; the tree has no emit path for it either, so this may be a program-level decision rather
   than a T15 one.
2. **F1: who owns adding the registry row?** `gk-data/packs/fusion/data/seed/ip-censor/_registry/**` is outside every lane
   fence I have seen, and until a row exists the release gate is green on a class of violation it is
   designed to catch. If the answer is "the row should not exist because this brand is not a
   derivative-work concern", that is a ruling worth writing down, because the current state reads as
   accidental rather than decided.
3. **F2: who fixes the narrative reader, and should fixing it be gated on reviewing the six voice
   exemplars first?** Turning on a check that has never run is a content decision, not a code one.
4. **F5: does the manager want a new ledger row for the species half, or an amendment to T16's file
   list?** Both are ledger edits, which are mine to report and not to make.
