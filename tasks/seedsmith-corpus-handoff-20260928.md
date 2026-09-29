# Seedsmith materials corpus — handoff (2026-09-28)

Written because the work is finished but the *residuals* are real, and a next session that reads only the
commit log will not see them. Every number here was measured at the moment it is quoted; a dated reading is
a reading, not a contract, so re-derive before relying on it.

Session record: `tasks/sessions/mega-merge-program-manager-20260925-f78e.json` (`f78e`).
Ledger with the full reasoning: `tasks/seedsmith-todo.md`, entries **SS-F1..SS-F39**.

## Is the cleanup complete? No — and here is the exact shape of what is left

| area | state |
|---|---|
| the generate itself | **complete and converged** — 50 batches at exit 0, zero batch deaths |
| the regenerated corpus | **committed** on `features/mega-merge` (`1dc1f136b`), 3,633 rows |
| the run ledger | **committed** (`c05151f0e`), 2,133 of 2,176 subjects recorded done |
| `rescue/corpus-bcu211-itemseedgen-run` | **closed** on the owner's word; `rev-parse` no longer resolves it |
| cross-corpus name collisions | **zero**, measured |
| **53 within-materials name collisions** | **OPEN** — a model limit, not a wiring gap |
| **`display-templates/4,5,6`, `attributes`** | **OPEN** — no adapter generates them at all |
| **`sets/ultimategatling`** | **OPEN** — a measured variety limit |

## The three open items, and what each one actually needs

### 1. 53 within-materials name collisions — a MODEL limit

The re-emit converged because the tool said so, not because I stopped reading it:

> `11 of 20 subjects came back refused/blocked/missing (550 per mille) ... this is a variety
> limit, and more spending buys more of the same name`

The attempts lever is spent. Measured on this tail: **0 / 3 / 10 / 20 attempts → 437 / 125 / 200 per
mille**, and it then sat at 550. So raising the budget cannot help.

**What would help, and what would not:**
- A model with a wider name space would. That is the owner's endpoint and model choice, not a code change.
- Another pass on the same model will not. It has already been tried to 20 attempts per subject.
- **Do not "fix" this by editing `gk-data/packs/fusion/data/seed/items/materials/materials.json`.** The rule is that generated
  seed is never hand-edited, and here it is also *data loss*: the ledger records 2,133 subjects done, so
  restoring HEAD's corpus or hand-patching names makes the runner re-skip those subjects and leave their
  gaps open permanently.

**How to pick the work up:** re-derive the plan from the LIVE corpus, never from the rescue ref (which no
longer exists, and which held pre-pass names anyway):

```
python gk-core/scripts/reemit-colliding-item-names.py --corpus gk-data/packs/fusion/data/seed/items/materials/materials.json --json
```

Use `--ids a,b,c` to narrow to a named population. It is an **intersection** with what the gate derives from
the live corpus, never a union — a named id the gate does not flag is reported, not planned.

### 2. `display-templates/4,5,6` and `attributes` — NO GENERATOR EXISTS

`seedsmith check` reports these four as `Coverage/EmptyPartition`: the partitions are allocated and hold
nothing, because **no adapter generates either kind.** That is a product decision, not a defect, and it is
deliberately **reported rather than built**. Writing a generator is scope nobody has approved.

**This is the item most likely to be mistaken for a bug.** It is not one. If someone asks for these to be
filled, that is a new sub-program with its own plan, not a fix to this one.

### 3. `sets/ultimategatling` — a measured variety limit

The partition stays empty because the model returns the same name for it: `'Burst of Cherry'` three
consecutive times. Distinct from items 1 and 2 in that it is a *single* subject with a *demonstrated*
failure, not a population and not a missing generator.

## The defect worth remembering, because it was invisible to git

Three writers omitted `newline="\n"`, so on Windows every `\n` in the JSON became `\r\n` on disk — in
**61 of 945** `sets/*` partitions. Because `.gitattributes` declares `* text=auto eol=lf`, git **normalises
them away and reported them CLEAN**. Only a test reading raw bytes could see it.

Consequences a next session must know:

- A clean `git status` does **not** mean the seed bytes are right. Check raw bytes, or the LF test.
- `git checkout -- <path>` and `git checkout-index -f` both **skip** the rewrite for the same reason, and
  so do `git update-index --really-refresh` and `git add --refresh`. The stat entry survives all four.
- `git add -- <explicit paths>` **does** clear it, because it records a fresh stat entry per path. Verified
  safe here precisely because each file was byte-identical to its blob: `git diff --cached` stayed empty,
  which is the check that proves staging captured nothing. **Assert that emptiness** before committing
  after any such operation — otherwise you have staged content you never inspected.

`setgen/seedfile.py`, `setgen/repair.py` and `setgen/run.py` now pass `newline="\n"`, matching
`species_repair.py` and `name_repair.py`, which always did. 945 of 945 partitions measure CRLF-free.

## The 60 "dirty" sets partitions: a false alarm, resolved

`git status` listed 60 `sets/*` partitions as modified while their index, HEAD and worktree blob hashes
were **all identical** and a path-limited `git status` reported them **clean**. Content was never dirty;
`gk-data/packs/fusion/data/seed` dirty content measured **0**.

A full-tree status kept listing them through `--really-refresh` and `--refresh`. What cleared it was
`git add -- <paths>`, after which status went from 65 lines to 5 and `git diff --cached` stayed empty.

**If you see 60 modified `sets/*` partitions, check the hashes before you commit anything.** A commit that
lands 60 no-op changes as though they were content is worse than a dirty tree, because it teaches the next
reader that this tree is noisy.

## Not mine — do not commit these with this work

Two files were dirty in the shared tree and belong to the concurrent `ps1-ban` stream:

- `tasks/reports/mega-merge-manager-resume-20260925.md` — `guard-verification-boundaries.ps1` → `.py`.
- `tasks/backlog-clean-up-todo.md` — a rewrap of the BCU8.4 block.

Both are inside this session's fence, and the fence is an **upper bound on what may be edited, not a claim
of authorship**. They are left dirty for their owner.

`gk-core/scripts/run_guards.py` and `gk-core/tests/tools/test_run_guards.py` are likewise untracked work from that stream.

## Consequences of closing the rescue ref, stated plainly

`6fc3d2b21` was in exactly one ref. It is now reachable **only through the reflog until pruned**, and no
tag was created because none was asked for. `git cat-file -e 6fc3d2b21` still resolves it today.

**If that commit is ever wanted permanently, `git tag` at `6fc3d2b21` is the one line that does it, and it
must happen before any `git gc --prune`.** Its unique findings are already safe as prose at CB41/CB42/CB43 in
`tasks/backlog-clean-up-todo.md`; the raw commit is what would be lost.

## The measurement habit that made this work

Three defects in this session were only findable by **cross-checking two instruments against each other**,
and each time the *instrument* was the broken one:

- A probe said 13 cross-corpus collisions, the tool said 181, and the holders read `vs material.2447` —
  a cross-corpus collision by definition names something that is not a material. The tool was wrong: a
  repo-relative constant joined onto the items root built a path that cannot exist, so the skip was a no-op.
- The re-emit reported `PERSISTED 3 refused 1` on a 4-subject pass and changed nothing. The corpus write
  target and the plan's read source were not the same question.
- A whole-suite red was attributed to "pre-existing" until the suite was run again in a scratch HEAD
  worktree and diffed as sets: 19 in both, 1 fixed here, and **2 that were this change's own regressions.**

That last one is the one to keep: a baseline you did not measure is a recollection, and this repo has
repeatedly shown that a recollection is wrong in the direction that costs the most.
