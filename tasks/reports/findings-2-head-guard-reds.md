# Two pre-existing `FusionRpg.Guard.Tests` reds at the merger head (`1945aa05c`)

Lane `findings-2`, 2026-09-23. Found because this lane's row verification maps any `tasks/**` path to the
`session-and-program-records` boundary, whose project is the whole `guard` module — so a docs-only row
inherits the guard suite's state. **Neither red is this lane's**: lane `findings-2`'s delta against the head
is `scripts/publish-player.ps1`, `scripts/smoke-player-pack.ps1`, `gk-core/scripts/verification-boundaries.v1.json`,
`gk-fusion/src/FusionRpg.Launcher/Services/PlayerPackProbe.cs`, `gk-fusion/tests/FusionRpg.Launcher.Tests/{PlayerPackProbeTests,MelonHostGapTests}.cs`
and task/report files. Both are "the code moved and its pin did not", which is the class
`DESIGN-GATE.md` §1's atom row already records as recurring.

| Reading | Command | Result | Artifact |
|---|---|---|---|
| Guard suite at `1945aa05c` | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --verbosity minimal` | `Failed! - Failed: 2, Passed: 667, Skipped: 0, Total: 669` (5 m 10 s) | this file |
| Guard suite re-taken at `3e908c097` (head moved; same two reds) | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --verbosity minimal` | `Failed! - Failed: 2, Passed: 667, Skipped: 0, Total: 669` (7 m 23 s); both pins verified still stale by grep — `PlantSideStatusGuardTests.cs:114` still `02B04A25…`, `PlayerSpeciesMaterialiseCallerGuardTests.cs:122` still `Assert.Equal(9, found.Count)` | this file |
| Guard suite re-taken at `c020686bd` (39 merges later, via CS-F4's own verify-change run) | `pwsh -NoProfile -ExecutionPolicy Bypass -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/content-stack-todo.md') -AllowUnscoped"` | doc-citation step passes (`D1 3 (0 HIGH)`), then `Failed! - Failed: 2, Passed: 667, Skipped: 0, Total: 669` (6 m 8 s), command exits 1 — the same two reds, unmoved by 39 merges | this file |

**Why this lane did not fix them, stated so the routing is a decision and not an omission.** Red 2's own
guard comment says *"A tenth code is a reviewed change that should fail this test and be re-read; that is the
opposite of the species-count anti-pattern"* — and the lane that added the tenth code recorded that it left
the row open pending a manager ruling (`tasks/reports/creature-seed-rank-t8.md:37`). Re-reading it here
would pre-empt that pending ruling, and the test's name (`The_nine_pick_refusal_codes_are_a_closed_vocabulary`)
is cited by `docs/architecture/species-progression/spec-species-mod-ledger.md:174` and two evidence
fragments, so a rename is not a drive-by either. Red 1's re-pin is the same shape: the pin's own comment at
`PlantSideStatusGuardTests.cs:108-111` records that the previous re-pin came with the changing commit's
reason (`c3bb0ba2`, combat-ai CAI1.12). Both are filed here with `file:line`, the moving commit and the
printed reading; the fix is one reviewed act in each owning lane.
| Red 1 | same run | `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` — `Expected: "02B04A25BC9ADB37533D0973EF7C2E02D2E773412…"`, `Actual: "E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35…"` | `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs:112,115` |
| Red 2 | same run | `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` — `Assert.Equal() Failure: Collections differ` at position 6 | `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:121,122` |

## Red 1 — the `BattleEffects.cs` byte-identity pin is stale

`Assert.Equal(baselineHash, hash)` at `PlantSideStatusGuardTests.cs:115` pins
`02B04A25BC9ADB37533D0973EF7C2E02D2E7734128D39112BC554B81F21CC00B` for
`gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs`; the file now hashes to `E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35…`.
**Cause:** `5e33ad647 "fix(battle): T6 (W11) one gate owns combat.defense.omni"` (2026-09-23) changed that
file and did not re-pin. The pin's own comment at `:108-111` records the intended procedure — the previous
re-pin came with a reason (`c3bb0ba2`, combat-ai CAI1.12). **Owner:** the W11 / `battle-derived-wire` lane
that made the change; the fix is a deliberate re-pin with that reason, never a blind bump.
**Why this lane did not fix it:** re-pinning a byte-identity guard without knowing the intent is exactly the
"widen the guard / add a knownRed" move the brief forbids, and this lane did not make the change.

## Red 2 — the pick-refusal vocabulary grew to ten and its closed-vocabulary pin still lists nine

`22fc4f3d3 "feat(creature-seed): T8 rank floors at the two enforcing fusion gates (row left open)"` added
`picks.source-below-rank-floor` in `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:305` (beside
`promotion.rank-floor`), so the vocabulary is **ten**. The guard pin at
`PlayerSpeciesMaterialiseCallerGuardTests.cs:96-104` lists nine and `:122` asserts `Assert.Equal(9, found.Count)`;
the test's own name says "nine". The T8 report itself flags the situation —
`tasks/reports/creature-seed-rank-t8.md:37` asks for "One row or one fence grant from the manager".
**Owner:** `creature-seed` (row T8 / `species-rank`, `tasks/creature-seed-todo.md:108`). Per `DESIGN-GATE.md`
the widening module is not finished until the pinned count moves with it, and widening is a **reviewed**
change — so the fix is that lane's re-pin (nine → ten, with the reviewed reason), not a mechanical bump here.

## Routed

Both owning todos (`tasks/battle-derived-wire-todo.md`, `tasks/creature-seed-todo.md`) are **outside lane
`findings-2`'s allowed paths**, so this report plus the `finding` notes in `tasks/keepverse-split-ledger.jsonl`
and `tasks/content-stack-ledger.jsonl` are the filing. **Manager: please route red 1 to the W11 /
battle-derived-wire lane and red 2 to creature-seed T8.** Until one of them lands, `verify-change.ps1` is red
for every `tasks/**` and `gk-core/tests/FusionRpg.Guard.Tests/**` path in the repo (the `guard` module runs whole),
which is what stopped this lane's docs-only row from showing a green scoped run.
