# TVB3.4 — Debt ledger `red` kind + the seedsmith actions `red` row

| Criterion | Result |
|---|---|
| `stub-register.md` documents kind `red` with the exact quote ("a committed test that fails on a clean HEAD; the test is right and the tree is wrong") | added |
| One `red` row owned by the seedsmith actions pipeline, `waits-on` the description backfill | `SR-25`, owner `seedsmith-actions`, `waits-on` "the description backfill for the committed action corpus" |
| `StubRegisterTests` kind pin 4 -> 5 with its reason | done (comment explains why `red` differs from all four existing kinds) |

`SR-25`'s five test names confirmed by actually running the file, not assumed from the spec text:
`test_load_committed_reports_zero_loader_findings`, `test_content_field_missing_is_clean_on_the_real_corpus`,
`test_every_real_committed_action_carries_provenance`,
`test_resumed_plan_is_empty_now_that_every_real_action_has_a_description`,
`test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done` — all in
`RealCommittedCorpusCleanPassTests`, all caused by the same root cause (two real actions,
`act.attack` and `action.family.academic.004`, carry no content description; `act.attack`'s
`atomFamilies` also names an unregistered value). `cd gk-forge/tools/seedsmith; python -m pytest
tests/test_actions_description_completeness.py -q`: 5 failed, 6 passed — matches the spec's stated
finding exactly.

**One pre-existing defect found and fixed, unrelated to this task, discovered by its own scoped
verify:** the doc-citation audit (merged in from the mega-merge) flagged `SR-21`'s citation
(`gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:20`) as stale — `commander-identity` SE4.1-SE4.3
(`b0b46579`, `1588875d`) deleted the `CommanderId` enum months before this task and replaced it with
`EmpireId`/`CommanderRef`, so the file is now a 2-line tombstone with no line 20. This is exactly the
enum SR-21 was about, so the row was closed, not just re-pointed: struck through
(`~~SR-21~~`), citation trimmed to the bare surviving file, `waits-on` set to "nothing — closed".
`SR-20`'s own citation still resolves cleanly (585-line file, line 8 real) so it was left untouched —
its own "SR-20 struck" claim in `963bc692`'s commit message never actually touched this doc, but that
gap doesn't fail the audit and is out of this task's scope to chase.

Scoped verify: `.\scripts\verify-change.ps1 -Paths docs/architecture/stub-register.md,gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs -Session summoner-convergence-lane-d2-20260919`
-> doc-citation audit clean (0 HIGH), `guard.stub-register` 7/7.
