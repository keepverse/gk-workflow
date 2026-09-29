# sgc-4 re-verification — T55 / T57 / RECON-F6 at the merged tip (2026-09-22)

Lane `sgc-4` · session `species-gear-chain-4` · measured on `features/mega-merge` @ `3e06b1fd7` + this lane's commits

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| T55's boundary-mapping lines now resolve | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/data/tuning/set-topology.v1.json') -Session species-gear-chain-4"` | plans `gk-core/data/tuning/set-topology.v1.json -> tuning-set-topology (module)` — **no `VERIFICATION BOUNDARY MISSING`**; the run then fails on the seedsmith suite (row below) | `tasks/species-gear-chain-todo.md` T55 |
| …and the item corpus tree resolves too | same, `-Paths @('gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json')` | plans `seed-items-corpus (module)` + `seed-items-validator-seam (seam)` + `generated-seed` guard + `gen-item-seed-validator`/`gen-items-gate`; fails with `item seed corpus failed validation` = T37's 498 owed `SameStageReference` rows | same |
| The seedsmith boundary still cannot pass | same first command | **17 `UNEXPECTED FAILURE`s** vs **5 `KNOWN RED`** (`test_actions_description_completeness`, SR-25). Failing set moved: only `test_cli::test_actions_check_uses_domain_loader_and_excludes_round_scratch` survives from the three the row named; `test_audit_doc_citations::RealTreeTests::test_the_real_scan_runs_and_produces_a_report` (the row's own cwd item) is red | `.v1.log` (deleted; list quoted in the row) |
| T57's last box: the cause is gone, the fence remains | `python gk-core/scripts/audit-magic-numbers.py --summary`; `pwsh … verify-change.ps1 -Paths @('gk-core/tools/tuning/publish.py','gk-core/tools/tuning/test_publish_set_value.py') -Session species-gear-chain-4` | `TOTAL 0 0 0 0 0` (the `SSH-route-1` finding is fixed); the check now refuses `path is outside session scope (species-gear-chain-4): gk-core/tools/tuning/publish.py` — the merge retired the predecessor record that carried the widened path | `tasks/sessions/species-gear-chain-4.json` |
| RECON-F6's banner option is dishonest here | `grep -n "RECONCILED_BANNER_RE" tasks/reports/backlog-reconciliation-20260921.md` | `re.compile(r"closed by the header above", re.IGNORECASE)`, scanned over the first 15 lines — writing it would declare the whole file closed while T37/T55/T57/T59 are open | `gk-core/scripts/audit-program-pipeline.py:99` (out of fence) |
| Open-block census at this tip | heading + unticked-box scan over `tasks/species-gear-chain-todo.md` | open: T37 (external), T55 (TVB-owned), T57 (1 box, session-record fence), RECON-F6 (metric, out of fence), T59 (external), plus the checkpoint boxes whose review lines are owner-gated | — |

**No code or tuning value changed in this batch.** **NOT proved:** T55's third and fourth acceptance lines (knownRed
disposition, cwd portability) remain TVB's to close — measured and handed over, not worked around.
