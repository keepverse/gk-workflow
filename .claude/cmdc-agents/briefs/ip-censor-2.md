# Lane brief — `ip-censor-2` (the grants that unblock ip-censor's 17 blocked rows)

## Why this lane exists

`ip-censor-1` closed **8 rows** (T0, T1, T2, T3, T5, T6, T7, T9), landed the **in-fence halves** of T4 (classifier +
remediation), T8 (curate import + USPTO adapter) and T10 (composition root + CLI + versioned plan), and recorded
**17 rows blocked** — every one of them on the same thing: paths outside that lane's fence. Its tool suite is green
(198 passed). This lane has those paths granted, so the work is already scoped: read the rows and finish them.

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its ip-censor row
names, **in this session**, then verify each claim against code. A comment is not evidence.

## Read first

- `tasks/ip-censor-todo.md` — the rows. Each blocked row names the exact path it needs; that is your worklist.
- `tasks/ip-censor-ledger.jsonl` — what T0–T10 landed, and each blocked row's recorded reason.
- The spec the todo names under `docs/architecture/`.

## The grants this lane carries, and what each unblocks

| Grant | Unblocks |
|---|---|
| `tasks/ip-censor/**` | T22 (`tasks/ip-censor/curate/**`), T23 (`tasks/ip-censor/release-readiness.md`) |
| `gk-data/packs/fusion/data/seed/ip-censor/_registry/**` | T22's `marks.v1.json`, and any registry row |
| `gk-core/tools/ip-censor/**` | T4 part 2, T8 part 2, T10's remaining half, T11, T12 |
| `docs/architecture/**`, `gk-data/packs/fusion/data/seed/ip-censor/**`, `scripts/**`, `.github/workflows/ci.yml` | the wiring/doc rows |

If a row needs a path still outside that list, **stop and report it with the path named** — do not reach across the
fence.

## Rules

1. **The tool's own suite stays green**: `cd gk-core/tools/ip-censor; python -m pytest -q`. Read the printed counts.
2. **Owner ruling IC-3 stands**: a red ip-censor suite is a **code defect, never an IP finding**, and neither the
   advisory scan (T11) nor the release gate (T12) may block CI on a *finding*.
3. **Generated or registry data**: if a file carries generator provenance (`_meta.model` / `promptVersion` /
   `batch`), fix the generator and regenerate — never hand-edit the emitted JSON. Hand-authored registries
   (`**/_registry/**`) may be authored directly; say which you did.
4. **A row you close needs its evidence in the same commit**, and the row id must be asserted present after the
   edit (a reused id has silently appended nothing before).
5. **Test substrate**: tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it for `tests/**`.

## Verification

- `cd gk-core/tools/ip-censor && python -m pytest -q` — the tool's suite; read the counts.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session ip-censor-2`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — must stay at its printed guard count with 0 failures.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report (end every segment with this)

```
<<<REPORT
{"status": "partial|done|blocked",
 "summary": "<what landed, with commit shas and row ids>",
 "closed": ["<row id>: <one-line evidence>"],
 "open": ["<row id>: <what it now waits on, named>"],
 "blocked": ["<row id>: <the named external dependency or the sharpened question>"],
 "next": "<the single next row you would take>"}
REPORT
```

Every claim in the report must already be a commit in this worktree.
