# TVB3.3 — D4 boundaries: seedsmith + `gk-core/tools/tuning`; `CiPytestWiringTests`

| Criterion | Result |
|---|---|
| Projects `seedsmith`, `tuning-py` | added |
| `seedsmith-fallback` (module), `seedsmith-tests` (`selfSelect`) | added |
| One `seedsmith-<area>` per adapter area with an importing test | added (7: actions 23, creatures 37, dungeon 19, effects 3, items 39, structures 5, trees 40 test files — derived via an AST-precise `from/import seedsmith.adapters.<area>` scan, not naive grep, then reviewed) |
| `tuning-publish-tool` re-pointed to `tuning-py`, `magic-numbers` kept | done |
| `tuning-resource-ownership` | added |
| `CiPytestWiringTests` (every pytest project has a `python -m pytest` line under a step whose `working-directory` = its `root`) | new, 2 tests, carries `guard.workflows` |
| P6 (real registry: guard passes; seedsmith/tuning resolve) | passed |
| No path maps to Guard.Tests any more | confirmed — `tuning-publish-tool`'s project is `tuning-py`, not `guard` |

**One gap found and closed beyond the literal D4 table:** `gk-core/tools/tuning/test_publish_notification_catalog.py` and
`test_publish_reprice.py` are real files with no boundary of their own (D4 only names the two
explicit selectors), so `gk-core/tools/tuning/**` did not fully resolve as P6 requires. Added `tuning-fallback`
(module, `gk-core/tools/tuning/**`) — the same "specific boundaries + a fallback for the rest of the tree"
shape used everywhere else in this registry; it changes nothing for the two already-mapped pairs
(exact patterns still win) and only catches what neither of them owns.

Real end-to-end proof:
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/acquisition.py` -> `seedsmith-items`, plans the 39 items
  test files, not the whole suite.
- `gk-forge/tools/seedsmith/tests/test_items_adapter.py` -> `seedsmith-tests`, selects itself.
- `gk-core/tools/tuning/publish.py` -> `tuning-publish-tool`, one pytest target (`test_publish_add_key.py`).
- `gk-core/tools/tuning/test_publish_notification_catalog.py` -> `tuning-fallback`, module run (no crash).

Full class (`VerificationBoundaryWorkflowTests` + `CiPytestWiringTests`): 46/46 clean on the second
attempt (first attempt hit 5 spurious 120s timeouts under heavy concurrent load — confirmed
contention, not a defect, per the standing rule: individual test durations had roughly tripled
across the board that run, then returned to normal on retry).

Scoped verify (two checks, since `CiPytestWiringTests.cs` is new and not yet in the focused
boundary's own path list, so it plans the whole-project fallback too):
`.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/CiPytestWiringTests.cs,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session summoner-convergence-lane-d2-20260919`
-> `guard` project whole run 493/493 (11m57s), focused `guard.verification-boundaries` 44/44 (11m14s).

The plan's own second verify command (`gk-forge/tools/seedsmith/tests/test_items_adapter.py`,
`gk-core/tools/tuning/publish.py`) names paths outside this session's declared fence — run with
`-AllowUnscoped` instead of `-Session`, matching the established pattern for every other
out-of-session real-path proof in this program (gk-core/tools/CombatSim, gk-core/tools/ProvePredictor, etc.).
