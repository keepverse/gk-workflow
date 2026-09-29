# ip-censor T12 — release gate step, checklist line, exit-check guard, enforcement row

Session `ip-censor-3`, worktree `.claude/worktrees/cmdc-ipc-3`, HEAD `4d6993b5`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Gate step exists, named, positioned | `grep -n "name: " .github/workflows/release.yml` | `:40 Unit tests` → `:212 IP release gate (ip-censor, IC-3)` → `:224 IP release gate findings` → `:236 Prepare injector refs` → `:258 Publish player pack` | `.github/workflows/release.yml` |
| Installs + scan, each exit-checked; installs in the tool, scan from the repo root | `python -m pip install -r gk-core/tools/ip-censor/requirements.lock` / `python -m pip install -e gk-core/tools/ip-censor --no-deps` / `python -m ipcensor.report scan --format json --fail-on enforced --authored-only > tasks/ip-censor/release-scan.json` | installs exit 0; scan exit 1 (expected) | same file |
| Checklist line in §Before tagging | `grep -n "ipcensor.report scan" docs/runbook/release-prove.md` | `:8` one line, same command, inside `## Before tagging` (`:5`) | `docs/runbook/release-prove.md` |
| Enforcement-registry invariants row | `python -c "json.load(...)['invariants'][-1]['id']"` | `ip-enforced-finding-blocks-release`; `guards: []`, non-empty `unguardableReason` naming the release step (R6 XOR holds; 46 rows, ids unique) | `gk-core/scripts/enforcement-registry.v1.json` |
| Gate fails loudly on the real tree and says what it found | `python -m ipcensor.report scan --format json --fail-on enforced --authored-only` | **exit 1**; 7,119 findings in 1,243 files; **111 enforced in 42 files** (`player-name` 7, `player-prose` 60, `generator-prompt` 44); `model: None` | `tasks/ip-censor/release-scan.json` (runner artifact, deleted before commit) |
| IC-4.1 target visible in the gate's own output | same run | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538,539` — `Overwatch`, `player-name`, enforced; same two lines in `_runs/tree-language.ledger.json` | same |
| `WorkflowExitCheckTests.TestCommandPrefixes` gains the prefix + a planted missing-check case | — | **not done — DENIED PATH.** The orchestrator pipeline hook refuses `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` ("protected pipeline file (guards, verify, ledger script, hooks, CI)") for both edits. The exit check is present in `release.yml`; nothing yet guards a later edit that drops it. | — |

Erratum carried in this commit (the shipped command differs from the row and `spec-report.md:54`):
`--authored-only` is required by `spec-report.md:39` and `gk-core/tools/ip-censor/ipcensor/suggest.py:11`, and
`gk-core/tools/ip-censor/ipcensor/cli.py:154-160` builds the LLM proposer without it. Measured: without the flag
the gate waited past 600 s against a live `IPCENSOR_LLM_*` endpoint; with it, `model: None` and exit 1.

Verification: `scripts/verify-change.ps1 -AllowUnscoped -Paths …` (`-Session ip-censor-3` is impossible —
`tasks/sessions/**` is outside this lane's allowed paths, so every run uses `-AllowUnscoped`, which selects
the same projects, guards and doc-citation checks and only skips the session-scope fence).
