# SE0.1 — Seed gk-core/scripts/enforcement-registry.v1.json

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| every current guard catalogued (18 `guard-*.ps1` + `session-boundary`) with a measured tier/status/backlogModule/localReason | `& .\scripts\guard-<name>.ps1` for debug-scope, magic-numbers, overflow, power, stat-pairs, class-system, commit-policy; grep `ci.yml` for `scripts\guard-*.ps1` | the five unwired guards `exit=0` (green); `guard-class-system` `exit=1`; `guard-commit-policy` `exit=1` (check_history); ci.yml invokes 8 guards + `guard-verification-boundaries` in its own step | gk-core/scripts/enforcement-registry.v1.json |
| one invariant row per DESIGN-GATE §2 item (1–16) and per uncovered hard rule, each guarded or carrying an `unguardableReason` | seed validation (below) | 33 invariant rows; R1/R3/R4/R6/R8 all hold; a rule with no scan names the module that will guard it | gk-core/scripts/enforcement-registry.v1.json |
| JSON parses; every `script` path exists | `Get-Content .\scripts\enforcement-registry.v1.json -Raw \| ConvertFrom-Json` + `Test-Path` per script + R1/R3/R4/R6/R8 checks | `guards=19 invariants=33` → `REGISTRY SEED OK` | — |
