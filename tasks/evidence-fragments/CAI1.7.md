# CAI1.7 — `publish.py --remove-key`

**Known collision, resolved per the manager's brief.** After merging `features/mega-merge`, `--remove-key`
(plus `--remove-edge`, `--remove-entry`) already existed in `gk-core/tools/tuning/publish.py` (built by the
concurrently-active `solid-enforcement` lane, which the session-boundary crossing note in
`tasks/sessions/combat-ai-build-20260920.json` already flags as also claiming this file). Per the brief:
**verify-and-test-only, no second implementation.**

| Criterion | Command | Result |
|---|---|---|
| Removes exactly one existing key | `python -m pytest gk-core/tools/tuning/test_publish_add_key.py -q` (pre-existing `RemoveKeyTests`) | 26 passed (unedited) |
| Refuses an unresolvable path | `python -m pytest gk-core/tools/tuning/test_publish_remove_key.py -v` | `test_refuses_an_unresolvable_path_rather_than_a_silent_no_op` passed |
| Repeatable within one invocation; one invocation writes exactly one `v{n+1}` | same run | `test_three_removals_in_one_invocation_produce_exactly_one_new_version` passed — 3 removals, `widget.v1.json` -> `widget.v2.json` only |
| Requires `--reason`, recorded in `_meta` beside each removed path | same run | **does not hold** — no `--reason` flag exists; only an optional, invocation-wide `--label` (`_meta.rebalanceLabel`). `test_reason_is_not_required_known_gap_vs_spec` pins this honestly rather than silently passing |

**Named gap, not silently accepted:** `spec-profile-schema.md`'s acceptance line for a required,
per-path `--reason` does not hold against the shipped tool. `gk-core/tools/tuning/publish.py` is a contested
file (claimed by the concurrently-active solid-enforcement/lane-d3 session), so this task does not
extend it — the gap is recorded here and in the ledger for the manager to rule on: accept `--label` as
the de facto reason, or assign the `--reason` addition to whichever lane currently owns `publish.py`.

**Also named:** the real CLI syntax is `container:leaf` (colon-separated, e.g. `ai:weightHitChance`),
not the plain-dotted `ai.weightHitChance` example `spec-profile-schema.md`'s own Commands section
shows. `CAI1.8`/`CAI3.1` must use the colon form when they call this tool for real.

verify-change.ps1 -Paths gk-core/tools/tuning/test_publish_remove_key.py: 62 tuning-domain pytest cases passed.
