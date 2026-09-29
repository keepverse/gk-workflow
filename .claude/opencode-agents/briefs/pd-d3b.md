# Lane brief — `pd-d3b` (opencode continuation of `cmdc/pd-d3`, D4.13/D4.17 preflight)

## Why this lane exists

`cmdc/pd-d3` (pi, 27 segments) drained with 21 open rows and preflight WIP in
its tree, adopted as `e14f02c8a` on `cmdc/pd-d3`. Adopt that commit, then push
the preflight chain forward. Do NOT re-run the regression check below; it is
handover fact.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## Goal

Advance the D4 preflight chain in `tasks/party-dungeon-todo.md`: **D4.13**
(Preflight, coverage and refusals — `QuestPreflight.Run` with the spec's full
signature) and **D4.17** (`DomainPreflight`, the ten-row chain), building on
the adopted `EncounterPreflight` + bridge/harness tests.

## Handover facts (already verified — confirm at adopt time, do not re-derive)

- Regression on the merged head: full Delve filter **1754/1754** (the merge
  added 8 Delve tests from other lanes, zero failures).
- Adopted WIP (`e14f02c8a`, 4 files): `EncounterPreflight.cs`, its
  `EncounterPreflightTests`, the `DomainEncounterPreflightBridgeTests`, and the
  todo's own row updates.
- 21 open rows, all with correct states — read the row, not the checkbox
  count. D4.30/D4.31/D4.32 and the D5/F rows stay out of scope for this slice.

## Allowed paths

- `gk-core/src/FusionRpg.Core/Delve/**`
- `gk-core/tests/FusionRpg.Core.Tests/Delve/**`
- `docs/architecture/party-dungeon/**`
- `tasks/party-dungeon-todo.md`
- `tasks/party-dungeon-ledger.jsonl`

## Off limits

The rest of `tests/**` (especially `gk-core/tests/FusionRpg.Core.Tests` root-helper
files owned by the keepverse L3b slice landing in parallel), `scripts/**`,
`src/**` outside Delve, keepverse and content-stack todos/ledgers,
`tasks/reports/**`, other lanes' files. Combat writes through
`EntityStatWriter`; HP deltas through the Funnel; `ActorHub` is the sole
compose gate. Commit nothing, push nothing, create no branches — leave the
tree dirty; the orchestrator harvests.

## Definition of done

1. WIP `e14f02c8a` adopted (all 4 files present with their content).
2. D4.13 and D4.17 acceptance lines addressed or named unmet with the exact
   blocker; row(s) advanced with evidence fragments (exact command text +
   printed numbers).
3. `dotnet test` over the Delve filter prints `Failed: 0` on the changed tree.

## Verification

- `git log --oneline -3` and `git show e14f02c8a --stat` — confirm what you adopt first.
- The exact verify commands D4.13/D4.17 name (run them verbatim from the rows).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree.
