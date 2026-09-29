# ssh49f2 — the five rows recorded `blocked` re-checked against the live ledger (2026-09-22)

The queue carried **SSH7.1, SSH7.7, SSH8.4, SSH8.5, SSH6.8** as blocked. This re-reads each blocker and
re-measures the one thing three of them depended on: the `combo-budget` report.

## The measurement (the row's own verify command)

| Command | Result |
|---|---|
| `cd gk-forge/tools/seedsmith; python -m seedsmith items combo-budget --report` | exit 0 — `PASS — every cell is at or under the rarity route (164 priced, 0 refused).` (370 lines; no `derived` / `refused` / `no leg can fix` section — the report prints those only when red) |

⚠ My first two attempts wrapped it in `timeout 1200 ...`, which made the CLI's own
`subprocess.run(["dotnet", …])` (`combogen/tuning.py:139`) die with `FileNotFoundError: [WinError 2]`:
MSYS's `timeout` hands the child a POSIX-form `PATH`, which Windows `CreateProcess` cannot search. It is a
harness artifact, not a seedsmith defect — without `timeout` the same command exits 0.

## Row by row

| Row | Recorded blocker | Re-checked state | Verdict |
|---|---|---|---|
| **SSH8.5** | *"the `report exits 0` acceptance line is BLOCKED on SSH4.4's owner-run corpus regeneration (exit 0 also requires 0 refused cells)"* | SSH4.4 is DONE (ticked, corpus regenerated: `gk-data/packs/fusion/data/seed/items/combinations` 82 entries, 0 carrying `minTier`/`grantedTier`); the report exits 0 with **0 refused** | **DONE** — ticked; the erratum it asked for is not needed |
| **SSH6.8** | *"the passing report the acceptance requires does not exist: 35 priced / 25 FAIL / 161 unpriced — the 25 need SSH8.5's publish, the 161 need SSH4.4's remedy"* | both dependencies are done and the report is green, so the blocker is **lifted**; what remains is the publish + the guard test, whose paths are `gk-core/data/tuning/sockets.v3.json` (through `gk-core/tools/tuning/publish.py`), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs` | **blocked — on another lane / a fence widening**: none of those three is in this session's allowed paths (`gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/DebugEndpoints.cs`, `gk-core/tests/FusionRpg.E2E.Tests/**`, `tasks/strain-splice-host-todo.md`, `docs/architecture/item/**`, `tasks/reports/**`), so landing them here fails the run's allowed-path check |
| **SSH7.7** | *"the ladder publish and its measurement are one atomic act, and the measurement is red"* | the measurement is green now, but this row's own dep **SSH6.8 is not done**, and its publish needs `data/tuning/strain-splice.v2.json`, `data/tuning/sockets.v{n}.json` and `gk-forge/tools/seedsmith/…/combogen/tuning.py` — all outside this lane's allowed paths | **blocked** — on **SSH6.8** (itself fence-blocked, above) plus the same out-of-fence publish/tool paths |
| **SSH7.1** | *"`every_reader_loads_the_current_strain_splice_revision` needs `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`, a pipeline-protected path"* | unchanged: that file's `Literal` regex is still `sockets\.v[0-9]+\.json` only — no `strain-splice.v{n}.json` rule (`grep -n StrainSplice gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` is empty) | **blocked** — on the pipeline lane / that protected file, which is also outside this lane's fence |
| **SSH8.4** | same file, for `every_reader_loads_the_current_materials_revision` | unchanged: the file carries no `materials.v{n}.json` rule either | **blocked** — same dependency |

## What is already landed (so a successor starts from here, not from the blocker text)

- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs:21,27,34` — `Current = "sockets.v2.json"`,
  `StrainSplice = "strain-splice.v1.json"`, `Materials = "materials.v6.json"`. Both constant halves of
  SSH7.1/SSH8.4 and SSH8.5's reader switch are in.
- The shipped corpus carries no tier number (SSH7.6): 82 combination entries, 0 with `minTier`/`grantedTier`.
- `gk-core/data/tuning/materials.v6.json` (SSH8.5, `0661463aa`) is the current materials revision.

## NOT proved

- The publishes were **not** run: `gk-core/data/tuning/**` is outside this lane's allowed paths, and the rule is
  publish `v{n+1}` through `gk-core/tools/tuning/publish.py`, never hand-edit — so SSH6.8/SSH7.7 stay blocked.
- SSH6.8's `measuredAgainst` is to be "copied from the passing report, never typed"; the report prints the
  **sockets** and **materials** revisions but neither the strain-splice revision nor the corpus digest
  (the boot's own provenance line carries those: `sockets v2, strain-splice v1, materials v6, corpus
  ea0e042f98b0`). Whoever implements SSH6.8 should confirm its copy source — a detail, not a blocker.
- No guard test was added: `gk-core/tests/FusionRpg.Guard.Tests/**` is outside this lane's allowed paths.
