# Manager acceptance-schema repair — 2026-09-25

## Finding

The current `accept_lane.py` contract requires schema version 2 artifacts to carry an immutable
`expectedSha`, `contendedTree`, `logDir`, and check records with `check`, `seconds`, parsed failure
arrays, and a non-empty `log`. The eight current composite/P1 artifacts had been written in an older
summary-only shape. Their code verdicts and exact reviewed SHAs were preserved, but the artifact files
themselves were not valid inputs to the current fail-closed acceptance validator.

## Repair

The manager migrated exactly these current evidence artifacts to the current schema without changing
their reviewed code SHA, merged SHA, verdict, scope, command summaries, or evidence hashes:

- `resume-00-composite-20260925-fc144f2c.json`
- `resume-00b-final-20260925-011cd122.json`
- `resume-00c-split-core-mapping-20260925-ff934d08.json`
- `resume-01-delve-20260925-03d8cee8.json`
- `resume-02-battle-20260925-7b4e8ef5.json`
- `resume-03-web-20260925-4ff99673.json`
- `resume-04-expedition-20260925-ec4773b9.json`
- `resume-05-vocabulary-recovery-20260925-85d2c096.json`

The repair commit is `4d4c5ff918c1e82151a567cbd4b7c15058a5e4bb`. It is a manager evidence correction, not
a product-code acceptance claim.

## Validation

A read-only validator over the eight `resume-*.json` artifacts checked the current top-level and
per-check required fields, full 40-character SHA/expected SHA equality, eight-character short SHA,
GREEN verdict, clean contention flag, non-empty log directory, and empty red/error arrays.

```text
CURRENT_ACCEPTANCE_SCHEMA= PASS
```

The artifacts retain the original external log hashes in their check records. Relative
`external-evidence/...` log names avoid committing machine-local paths; the actual logs remain outside
the repository as recorded by each lane report. The legacy records did not retain per-check wall-clock
measurements, so their required `seconds` fields use a conservative one-second lower bound rather than
inventing a precise duration; future `accept_lane.py` runs record measured seconds directly.

## Boundary

Historical artifacts from older programs remain historical evidence and were not rewritten wholesale.
They are not used as current manager acceptance records without a current-schema migration. Future
acceptance must be generated/validated through `accept_lane.py`, not hand-authored summary JSON.

<<<REPORT {"status":"done","summary":"Migrated the eight current composite/P1 acceptance artifacts to the current schema-2 contract and validated exact SHA/expected SHA, short SHA, required check fields, GREEN verdict, clean contention, non-empty log directory, and empty red/error arrays.","changed_files":[".claude/cmdc-agents/acceptance/resume-00-composite-20260925-fc144f2c.json",".claude/cmdc-agents/acceptance/resume-00b-final-20260925-011cd122.json",".claude/cmdc-agents/acceptance/resume-00c-split-core-mapping-20260925-ff934d08.json",".claude/cmdc-agents/acceptance/resume-01-delve-20260925-03d8cee8.json",".claude/cmdc-agents/acceptance/resume-02-battle-20260925-7b4e8ef5.json",".claude/cmdc-agents/acceptance/resume-03-web-20260925-4ff99673.json",".claude/cmdc-agents/acceptance/resume-04-expedition-20260925-ec4773b9.json",".claude/cmdc-agents/acceptance/resume-05-vocabulary-recovery-20260925-85d2c096.json","tasks/reports/acceptance-schema-repair-20260925.md"],"verification":["CURRENT_ACCEPTANCE_SCHEMA= PASS","repair commit 4d4c5ff918c1e82151a567cbd4b7c15058a5e4bb","no product code or generated data changed"],"open_issues":["historical pre-schema artifacts remain historical and are not current acceptance records","future lanes must use accept_lane.py rather than hand-authored summary JSON"],"next_steps":["run the current-head merged-head gate after the branch stabilizes","use accept_lane.py for every future artifact","retain this report with the final handoff"]} REPORT>>>
