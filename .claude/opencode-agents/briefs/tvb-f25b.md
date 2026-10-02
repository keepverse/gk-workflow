# Lane brief — `tvb-f25b` (TVB-F25: re-bless two stale web fixtures)

## Why this lane exists

TVB5.9's third acceptance line (`test_fast.py -AllDefault` green once) is
blocked on TVB-F25: two stale **web** fixtures outside every TVB fence. The
owner approved a lane re-bless (2026-09-23). The Core group (68 projects,
15,836 tests), Data (1,766/0) and Server (826/0) legs are already green —
this lane owns ONLY the two fixtures. The AllDefault run itself is the
manager's (workers cannot run the full suite); leave it green-ready, do not
attempt it.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## Goal

Re-bless the two fixtures so each matches its producer's current output, then
tick TVB-F25 with the evidence.

## The two fixtures

1. `gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6`
2. `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json:4`

## Procedure (in order, no shortcuts)

1. For each fixture, find its producer (the code/test that emits the shape)
   and run it. Diff producer output against the fixture byte-for-byte.
2. If the producer output is CORRECT and the fixture stale: update the fixture
   to the output (re-bless), recording producer command + diff in
   `tasks/test-verification-boundary-todo.md` TVB-F25.
3. If the producer output is WRONG (a real drift, not staleness): STOP that
   fixture, report BLOCKED with the exact mismatch — never bless a lie to
   turn a suite green.
4. Run the web tests covering both fixtures (`npm test` filtered to the two
   suites) and quote the numbers.

## Allowed paths

- `gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json`
- `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json`
- `tasks/test-verification-boundary-todo.md`
- `tasks/tvb-wave5-ledger.jsonl`

## Off limits

Everything else — especially `src/**`, `tests/**`, `scripts/**`,
`data/**`, other lanes' files, and any producer source (read producers, never
edit them; a wrong producer is a finding for its owning program, filed as a
row, not fixed here). No `npm run` writes outside the two fixtures. Commit
nothing, push nothing, create no branches — leave the tree dirty; the
orchestrator harvests.

## Definition of done

1. Each fixture either re-blessed (producer command + byte-diff quoted) or
   declared BLOCKED with the exact producer-vs-fixture mismatch.
2. Covering web suites green, numbers quoted.
3. TVB-F25 ticked (or half-ticked per fixture) with the evidence fragment.

## Verification

- The producer commands, run verbatim, with their output quoted.
- `cd gk-web/web/fusion-rpg-web; npm test` over the two covering suites — numbers quoted.
- No other file changed (`git status --short` shows at most the 2 fixtures + 2 task files).

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree.
