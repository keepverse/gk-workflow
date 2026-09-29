# Manager H1 repair — BattleEffects guard re-pin

**Status:** focused repair complete; exact-SHA clean-checkout proof follows before merge.
**Owner row:** `tasks/combat-ai-todo.md` → `CAI-guard-1`
**Cause:** accepted P1 battle repair at reviewed SHA `7b4e8ef582a0744e20f501562a4b28167e402c89` changed the retained-damage observer surface in `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs`.

## Failure evidence

The stale merged-head run at `fa3635e6596f94459f347aee3561d10dfb2487cf` reported:

```text
PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline
Expected: E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35DA9835E8FB28799CA6733F8
Actual:   946E578D0092A77EB8DD59FDAF8C48FD3113B6042E0E4FB627E921EAB2B43013
Guard suite: 688 passed, 1 failed, 689 total
```

The failure was not treated as an allowlist item. The guard is an intentional H1 byte pin. The
accepted P1 battle change is the cause, so the correct repair is a deliberate re-pin with the cause
named, not a production revert or a weakened assertion.

## Repair

`gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs` now pins the full current hash
`946E578D0092A77EB8DD59FDAF8C48FD3113B6042E0E4FB627E921EAB2B43013`. Its adjacent comment names the
P1 reviewed SHA and explains that the retained-damage observer change intentionally moved the Core
bytes. `tasks/combat-ai-todo.md` records the reopened `CAI-guard-1` cause and handoff without
rewriting the historical re-pin notes.

## Verification

```text
dotnet test gk-core/tests/FusionRpg.Guard.Tests
  --filter "FullyQualifiedName~PlantSideStatus" --verbosity minimal
# Passed: 6, Failed: 0, Skipped: 0; exit 0

git diff --check
# pending at report-write gate; must pass before commit
```

The stale full merged-head run also had 1,776 legal-game/interop build errors and was aborted when
the branch moved; it is not reused as current-head evidence. This repair only addresses the
independent H1 guard red. The current-head merged gate must be rerun after all active reports/code
lanes stabilize.

## Remaining steps

1. Commit the three allowed paths at an exact SHA.
2. Run the focused PlantSideStatus test and `git diff --check` from a clean detached checkout.
3. Merge the reviewed SHA and update `CAI-guard-1` to its final accepted wording.
4. Rerun the full merged-head gate with the owner-provided legal environment; do not call the earlier
   blocked/aborted run green.

<<<REPORT {"status":"partial","summary":"Diagnosed the merged-head Guard red as the intentional H1 BattleEffects byte-pin movement caused by accepted P1 battle SHA 7b4e8ef5. Re-pinned the protected guard to the current full hash, recorded the reopened CAI-guard-1 cause, and passed the focused six-test PlantSideStatus selection; exact-SHA clean checkout and current-head gate remain.","changed_files":["gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs","tasks/combat-ai-todo.md","tasks/reports/resume-09-battle-guard-repin-20260925.md"],"verification":["stale gate log hash 23FBF19950D0E43083F2C2635DB6FD5B3D3E651692A7308FB0E8AB90976F5525","stale Guard result 688 passed / 1 failed / 689 total","focused PlantSideStatus result 6 passed / 0 failed / 0 skipped","focused log SHA-256 48752561CEFB2EDC9B1CE2BA46ACF4AF7D2317CFBE9BB8D58A4A439F116B543D"],"open_issues":["exact-SHA clean checkout and merge artifact are not yet created","current-head post-merge gate still needs a fresh run with legal environment","earlier merged-head run was stale and aborted after the branch moved"],"next_steps":["commit exact reviewed SHA","clean-checkout focused guard verification","merge and close CAI-guard-1","rerun current-head post-merge gate with H:/Games paths"]} REPORT>>>
