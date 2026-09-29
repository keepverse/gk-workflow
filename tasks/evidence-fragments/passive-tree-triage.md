# passive-tree — open-row triage for this lane (2026-09-21)

The lane brief's step 6 says take only rows whose acceptance is executable without an owner. All 33
open rows in `tasks/passive-tree-todo.md` were classified; **none is lane-executable**, so all stay
unchecked with the reason below. Two real checks were run while measuring, and both are recorded.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Generic tree corpus is byte-identical to a fresh regeneration | `dotnet run --project gk-forge/tools/TreeBinder -- --check` | exit `0`, zero `STALE` lines. `--check` gates ONLY byte-identity (`gk-forge/tools/TreeBinder/Program.cs:146`), never the per-tree `verdict=Fail` lines it also prints | `gk-data/packs/fusion/data/generated/passive-tree/**` |
| The family's own gate readings, re-measured | `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --family PassiveTree` | `HiddenFileCount walked 0`; `ExclusionRate 637‰ vs ≤30‰`; `NameCollision 388/1679`; `MechanismRamp wither:defensive:t9 2 vs 3`; the one hard gate `UnresolvedCount` green | — |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |
| Path-owned verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/passive-tree-todo.md','tasks/evidence-fragments/passive-tree-triage.md','tasks/seed-corpus-ledger.jsonl') -Session seed-corpus-20260920"` | exit `1`; doc-citations `0 HIGH` on both docs; session-boundary clean; `test: guard` `Failed: 1, Passed: 579, Total: 580` | the one failure is the pre-existing, other-owned `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (`tasks/combat-ai-todo.md:1089`, riding `tvb58`) |

## Row classification (33 open rows)

| Heading / rows | Count | Why not this lane |
|---|---|---|
| Checkpoint B — `537` | 1 | Owner review before phase C; the row says so. |
| F2 / F3 / F6 / Checkpoint F — `2023`, `2088`, `2270`, `2389`, `2490`, `2491`, `2492` | 7 | Squad-harness measurement no smoke run reaches: F3 wants a real production sweep at its own confidence; F6's D42 dials are structurally unresolvable and closing it needs the harness re-run, not a fragment read; `2389`'s acceptance is literally `N/A`. |
| H5 + PTR-EF1 — `3369`, `3455` | 2 | Both need the passive-tree program's `spec-tree-review.md` §7 ruling; PTR-EF1 is the erratum this lane filed. |
| H8 — `3602`, `3603` | 2 | The heading says *"GENUINELY OWNER-ONLY"*: a timed human reading of 20 real cards. |
| Checkpoint H / I — `4702`, `4708`, `5288` | 3 | 480-node generation at the H8 rate, plus owner card review / eyeball pass. |
| J1 — `5606`, `5619` | 2 | Content + live integration: the real bound corpus imported into a running server. |
| J7 — `6312` | 1 | The real 6,720-affix species-namespace run. |
| J9 — `6736`, `6737`, `6738` | 3 | The 840×40 species generation run (days). 6737's **generic** half is verified above; the species half needs the run. |
| J10 — `6753`, `6754`, `6756`, `6757` | 4 | Human judging of every tree at the H8 rate. |
| J11 — `6782` | 1 | A deliberate *"call site NOT built"* design note, not a build task. |
| J13 — `6963`, `6965`, `6966`, `6968`, `6970` | 5 | Model spend **authorised 2026-09-21** (owner, every corpus run, local LM Studio `google/gemma-4-26b-a4b-qat`), then a regeneration run. |
| Checkpoint J — `6977`, `6978` | 2 | Owner-only, irreversible ship point (D24). |

## Not proved
- **No passive-tree row was closed.** This is a triage; each reason is read from the row's own text and
  its heading, not inferred from a summary.
- `TreeBinder --check` exit `0` proves byte-identity only, never binding health. Its `verdict=Fail` /
  1,120 `REFUSED` readings (the D2 tier-bands pricing gap and `affix … does not exist in the shipped seed
  content`) are real and already tracked by the J1/J9/D2 rows — not re-filed here.
