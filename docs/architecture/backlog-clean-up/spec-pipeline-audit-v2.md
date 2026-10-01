# Spec: `pipeline-audit-v2`

**Program:** backlog-clean-up · **Map:** [../backlog-clean-up-map.md](../backlog-clean-up-map.md) module 11 ·
**Status:** spec, 2026-09-20. Map approved 2026-09-20.

## Objective

`gk-core/scripts/audit-program-pipeline.py` (v1, commits `178e81b2`, `d5ed561b`) finds breaks in the document
chain. Its first real use produced four false readings. Each was fixed later by hand, and each is a
pattern the tool can learn. v2 teaches it those patterns, so the next drift audit starts from a truer
list.

## The four blind spots, and what v2 does about each

| # | Blind spot (with the instance that exposed it) | v2 behaviour |
|---|---|---|
| B1 | **Status lives in a blockquote banner.** The 6 roster-balance specs open with `> ⛔ **SUPERSEDED 2026-09-06.**`; v1's `**Status` regex saw nothing. | The status reader also accepts a first-10-line banner matching `^\s*>\s*.*\*\*(SUPERSEDED\|WITHDRAWN\|OBSOLETE\|RETIRED\|CLOSED)[^*]*\*\*`. The closed-status vocabulary is one module-level tuple. |
| B2 | **Completion recorded outside checkboxes.** rift-gate's header says "Build complete"; story-scene uses a HANDOFF section; convergence uses `*-ledger.jsonl`; live-probe-screenshot's merge is only in `tasks/sessions/*.json`. | New finding kind `todo-header-vs-boxes`: a todo whose header (first 15 lines) claims completion (`complete\|done\|closed\|all .* gated PASS`) and still has unticked boxes. Also, `stalled-todo` rows are suppressed when a merged session record names the program in `program`/`paths`, or when a ledger names the task ids. |
| B3 | **Built by another program without a pointer (C3/C4).** `empire-development` built `deployment-hierarchy` modules 3–6. | New kind `absorbed-no-pointer` (advisory): for each `spec-<id>.md`, if a *different* program's todo or plan names the module id **and** marks it `[x]`/done, while the owning program's todo/map never cites that program, report the pair. |
| B4 | **Stalled detection.** v1 had none; the manual pass counted boxes and read 0/134 as stalled. | New kind `stalled-todo`: open boxes > 0, and no commit touching the program's paths (by name grep in `git log --grep` and the todo's own `Files:` lines) in the last N days. N is a CLI flag (`--stale-days`, default 7). It is structural, not balance, so a flag and not tuning. It runs after B2's suppression. |

## Constraints

- **Read-only.** It does not write files and does not run git mutations.
- **Contracts, never populations** (hard rule). Tests may pin the closed vocabularies: the `KINDS`
  tuple, the closed-status tuple, and the header-completion phrases. Tests assert behaviour on
  **fixture trees** built in a temporary in-memory or `tmp_path` structure, per the test-substrate
  rule; a failed cleanup fails the test. Tests never assert how many findings the real repo produces.
- **Advisory kinds are labelled.** `absorbed-no-pointer` and `stalled-todo` print `(advisory)` and are
  excluded from `--fail-on-open` unless `--strict` is passed. Both are heuristics, and the audit showed
  heuristics mislead when treated as verdicts.
- Runtime stays within one `git log` pass and one file-read pass. It needs no per-program subprocess
  per check.

## Acceptance

- A fixture with a blockquote SUPERSEDED banner is reported closed (B1).
- A fixture todo with a "Build complete" header and 3 open boxes yields exactly one
  `todo-header-vs-boxes` row (B2). The same fixture plus a merged session record naming the program
  yields no `stalled-todo` row.
- A fixture where program B's todo ticks `corpse-cache` and program A (the spec owner) never cites B
  yields one `absorbed-no-pointer` row (B3).
- `--only`, `--json`, `--include-closed` and `--fail-on-open` keep their v1 meaning. `--strict` is added.
- Tests live at `gk-core/tests/tools/test_audit_program_pipeline.py` (new; does not exist yet), or the repo's established location for
  script tests if one exists. Check `verify-change.py`'s mapping, and add the mapping if the path is
  unmapped.

## Verification

`python -m pytest <test file> -q`, then
`.\scripts\verify-change.ps1 -Paths gk-core/scripts/audit-program-pipeline.py,<test file> -Session <id>`.
