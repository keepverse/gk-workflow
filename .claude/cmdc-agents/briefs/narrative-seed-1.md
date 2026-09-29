# Lane brief — `narrative-seed` (program: narrative-seed)

## Program

`narrative-seed` — the seed-side narrative content program. Its capability map is
`docs/architecture/narrative-seed-map.md`; its ideal is `docs/architecture/narrative-seed-ideal.md`; its module
specs are `docs/architecture/narrative-seed/spec-<module-id>.md`. Its task list is
`tasks/narrative-seed-todo.md` — **975 lines, 33 headings carrying 93 unchecked rows** at the time this brief was
written (a reading, not a constant: re-measure before you report).

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its narrative-seed row
names, **in this session**, then verify each claim against code before you propose anything. A comment is not
evidence; code beats docs; docs beat comments.

## Why this lane exists

The goal requires every program's open task-block count driven to **zero with evidence**. This program has the
largest untended backlog in the repo and no lane has ever worked it. Your job is to **close rows, not to survey
them** — a row that ends the segment still open must end it with a *sharper question* or a *named external
dependency*, never with "needs investigation".

## Fence (your session paths)

You may edit only:

- `gk-forge/tools/seedsmith/**` — the generator/CLI code these rows are about
- `docs/architecture/narrative-seed/**`, `docs/architecture/narrative-seed-map.md`, `docs/architecture/narrative-seed-ideal.md`
- `tasks/narrative-seed-todo.md`, `tasks/narrative-seed-*.md`, `tasks/narrative-seed-ledger.jsonl`
- `gk-data/packs/fusion/data/seed/**` — **only by regenerating**, never by hand-editing (see the hard rule below)
- `gk-core/data/tuning/**` — **only by publishing `v{n+1}`** through `gk-core/tools/tuning/publish.py`
- `scripts/**` — only what a row you are closing actually requires

Anything else is another session's fence. If a row needs a file outside this list, **stop and report it as an
external dependency with the path named** — do not reach across the fence.

## The rows, in the order the todo lists them

Start at the top and work down; the todo's own order is the program's order. The open blocks at the time of
writing (re-measure, then confirm or correct this list in your first report):

| Todo line | Block | Open rows |
|---|---|---|
| L36 | Phase 0 — Boundary and verification | 3 |
| L74 | `model-config-resolve` (`spec-model-config-resolve.md`) | 5 |
| L162 | `script-check` (`spec-script-check.md`) | 1 |
| L174 | `gloss-registry` (`spec-gloss-registry.md`) | 1 |
| L187 | `dungeon-generator-repair` code (`spec-dungeon-generator-repair.md`) | 5 |
| L244 | `gloss-fill` code (`spec-gloss-fill.md`) | 2 |
| L267 | Wave-0 runs | 4 |
| L320 | Checkpoint 0 — Wave 0 | 4 |
| L334 | `storylet-vocab` (`spec-storylet-vocab.md`) | 3 |
| L361 | `character-vocab` (`spec-character-vocab.md`) | 2 |

## Hard rules that bind this program specifically

1. **Generated seed data is never hand-edited — fix the generator and regenerate.** `gk-data/packs/fusion/data/seed/**` entries carry
   generator provenance (`_meta.model` / `promptVersion` / `batch`); editing them by hand forks the corpus from its
   generator and the next run reverts you. The only sanctioned path is: change the generator/tuning/registry, then
   regenerate and commit the diff. If the generator cannot yet express the fix, **the generator is the deliverable**.
2. **A guardrail validates the CONTRACT and closed enums — never a population count or generated text.**
   `test_actions_description_completeness` already fails pre-existing on a clean HEAD; confirm a failure exists
   before blaming your change, and never "fix" a population reading by bumping a number.
3. **LLMs author identity only** (names, flavour, atom-family picks); all magnitudes are table-owned.
4. **Test substrate:** tests run **in memory**. A test that writes a file to disk is a defect now enforced by
   `gk-core/scripts/guard-test-substrate.py` (contract rule `untagged-file-store`): a `tests/**` file constructing a
   file-backed store must carry `[Trait("Category","DiskSemantics")]`. Do not add that tag to avoid the rule —
   tag only what genuinely tests file behaviour.
5. **A row you close needs its evidence in the same commit** — the reading printed, not asserted.

## Verification

Per row, run the path-owned boundary. These are the commands the runner uses to verify your segments:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session narrative-seed-1` — the path-owned boundary for every row you close.
- `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/<file> -q` — for seedsmith code rows.
- `python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` — corpus health after a regeneration.
- `python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1 --dry-run` — the generator's own dry-run.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report (end every segment with this)

```
<<<REPORT
{"status": "partial|done|blocked",
 "summary": "<what landed, with commit shas and the row ids>",
 "closed": ["<row id>: <one-line evidence>"],
 "open": ["<row id>: <what it now waits on, named>"],
 "blocked": ["<row id>: <the named external dependency or the sharpened question>"],
 "next": "<the single next row you would take>"}
REPORT
```

The report block is not decoration: it is how the manager reads your segment without re-reading your transcript.
Every claim in it must already be a commit in this worktree.
