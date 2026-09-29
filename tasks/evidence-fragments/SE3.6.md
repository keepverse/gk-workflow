# SE3.6 — `population-pin` gates

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `--summary` 0 findings | `python gk-core/scripts/guard-population-pin.py --summary` | **P1 0, P2 0, P3 0, TOTAL 0** — SE3.2 (ActorHub/ActorSurface), SE3.3 (rest of Core.Tests), SE3.4 (Data/Server/Guard/TreeBinder/E2E/PassiveTreeRosterGen), and SE3.5 (seedsmith) together closed the entire repo backlog to zero | gk-core/scripts/guard-population-pin.py |
| Registry `gating` | edited `gk-core/scripts/enforcement-registry.v1.json` | `"population-pin"` flipped `status: "backlog"` → `"gating"`, `backlogModule: "population-pin"` → `null`, matching the convention every other gating guard in the file already uses. `pr-contract-not-population` already named `guards: ["population-pin"]` with no `unguardableReason` (SE3.1 anticipated this) — no change needed there | gk-core/scripts/enforcement-registry.v1.json |
| Wrapper propagates a real exit code | `powershell -File scripts/guard-population-pin.ps1` | prints the P1/P2/P3 report, **exit 0** on the clean repo (confirmed the thin `.ps1` wrapper's `exit $LASTEXITCODE` correctly forwards the Python guard's `sys.exit(main())`, which returns 1 on any finding, 0 clean) | scripts/guard-population-pin.ps1 |
| CI guard tier picks it up as gating | `.\scripts\run-guards.ps1 -Tier ci` | **18/18 guards, 0 red** (up from 17 — `population-pin` now runs and reports `gating` in the table, 11.3s) | — |
| Registry schema/consistency tests still pass | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistryGuardTests\|FullyQualifiedName~GuardRunnerTests"` | **18/18** (`EnforcementRegistryGuardTests`) **+ 8/8** (`GuardRunnerTests`) | — |
| Registry-wide sanity | `python -c "..."` counting guard statuses | **21 gating, 1 backlog** (the one remaining backlog guard is unrelated to population-pin) | gk-core/scripts/enforcement-registry.v1.json |

This closes solid-enforcement wave 3's population-pin program end to end: SE3.1 built the guard, SE3.2–SE3.5 dispositioned every real site the guard found (179 sites across 98 C#/Python test files, plus one scanner self-check defect fixed along the way), and SE3.6 makes a future regression a CI failure instead of a silent drift.
