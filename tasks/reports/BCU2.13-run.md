# BCU2.13 — the element-secondary re-classify: run report

**Row:** `tasks/backlog-clean-up-todo.md` BCU2.13 · **Run:** 2026-09-23, manager-run detached job in
`.claude/worktrees/corpus-bcu213` (branch `corpus/bcu213`) · **Tool:** `seedsmith creatures run start
--pipeline element-secondary`

## The selector, computed rather than recalled

Species whose anchor carries `elementSecondary: "none"` **and** which no fusion recipe names —
**108 species** at 2026-09-23. The register's 2026-09-07 measurement of the same set was **127**; the corpus has
moved since (904 anchors now). A reading, not a constant, and the row's own text says this half has no fixed
acceptance bar: *"which of these 127 should get a second element" is a content/balance judgment call*, and a
lore-based classifier may legitimately answer `none` again for most of them.

Two earlier selector attempts were wrong and are recorded because both produced confident nonsense: the first
walked the species files as dicts when they are **lists of entries**; the second compared lowercase recipe ids
against CamelCase anchor ids, so it reported **450** "unnamed" species — i.e. everything.

## The run

```
run 20260923T000115.772708-6QR8PN: state=completed completed=0 failed=0 callsMade=0
```

**Zero calls, zero changes.** The classifier had nothing to do: those 108 species keep `elementSecondary: "none"`,
which the row anticipated. The run's own artefact is the job log
(`.pi/tasks/session-67372-67372/b2cf9f164.output`) plus this report.

## What the run exposed: the committed dump and its manifest disagreed

The first attempt was **refused by run-control**, not by the model:

```
seedsmith: run start refused: preflight's dumpHash (cc322647cd…) does not match the current dump
(6181dc2d…) — re-run preflight
```

Measured: `gk-data/packs/fusion/data/seed/creatures/_dump/_manifest.json` recorded `contentHash cc322647cd…` **captured 2026-08-23**
while the dump's actual content hashes to `6181dc2d…`; `_preflight.json` carried the same stale value
(`writtenUtc 2026-09-04`). So the committed dump had changed under a record that still claimed the old hash — the
pair was inconsistent, and the tool refused to run on it rather than silently classifying a corpus it could not
identify. **That refusal is the guard working.** The fix was the tool's own named one: regenerate the dump from the
server data dir, then re-run the preflight, which re-records the pair. After that all nine checks passed:

```
[OK] dump-exists · dump-is-complete · contract-audits-clean (0 findings) · model-answers · model-honours-schema
[OK] venv-lock-current · tuning-present (10 rungs) · disk-headroom (116 GB free)
PASS — 0 refusal(s), 0 thing(s) to ask about
```

**Finding worth carrying:** a committed `_dump/_manifest.json` can go stale against its own dump when the dump is
regenerated without re-running the preflight that records it. Any lane that regenerates the dump must re-run the
preflight in the same commit — otherwise the next consumer pays a refusal that looks like a tooling bug.

## State of the four corpus rows after this

| Row | State |
|---|---|
| `BCU2.10` action round-1 | **running** (manager job, resumed) |
| `BCU2.11` item-seedgen | **defect-gated** on its `SetCompleitability` GAPs — closes by fixing the generator |
| `BCU2.12` passive-tree J9/J10/J13 | **running** (`[137/904]`) |
| `BCU2.13` element-secondary | **run** (this report; 0 calls, 0 changes) |
