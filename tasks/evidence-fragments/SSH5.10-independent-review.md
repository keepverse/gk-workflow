# SSH5.10 — independent H7 review of the `sockets.v2` flip (manager-commissioned)

**Why this exists:** a tuning publish is an H7 surface, so the manager commissions an independent
read-only reviewer and does not merge on the lane's own word. Commissioned 2026-09-21 when `ssh27` was
accepted; reviewed SHA `4e94fd92` in `.claude/worktrees/cmdc-review-ssh27`.

**Two verification paths, both recorded because the first path failed:**

| path | outcome |
|---|---|
| `bg_delegate` (inspect-only) | **failed to launch** — `fusion context projection encountered an unsupported conversation block: message role system` |
| `fusion_validate` | **failed before any candidate** — `pi_executable_resolution_failed` (`@earendil-works/pi-coding-agent/package.json` unresolvable); 0 candidates, 0 tokens |
| `subagent` → `reviewer` (read-only) | **ran to completion** — verdict below |
| manager cheap check (the acceptance duty) | run in parallel on the same checkout |

## Verdict — merge OK, no P0/P1

| Q | question | verdict |
|---|---|---|
| Q1 | do both revision constants name v2 | **PASS** — `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs:21` `Current = "sockets.v2.json"`; `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:22` `SOCKETS_PATH = … "sockets.v2.json"`; the second generator imports that constant (`basetypegen/tuning.py:27`); structural mirror `SocketTuning.cs:41` `SocketMaxCeiling = 8` |
| Q2 | v1 still on disk, and the selection picks v2 | **PASS** — `gk-core/data/tuning/sockets.v1.json` present (`structuralCeiling: 4`, `maxCombosPerActor` at `:25`); every selector names the constant, none globs a version (`Program.cs:365-366`, `SocketMaxCheck.cs:52`, `combogen/tuning.py:104-110`) |
| Q3 | any reader still naming a revision literal | **PASS** — every `sockets.vN.json` hit in `src/**`, `tools/**`, `tests/**` is the constant file itself or comment prose; the reviewer enumerated all 10 `.cs` hits and the single `.py` code hit |
| Q4 | magnitudes in data, `maxCombosPerActor` gone | **PASS** — ceilings/rarityGrant are JSON only (`sockets.v2.json:5-21`, `:23`, `:25-66`); no C#/Python reader of `maxCombosPerActor`; the identifier survives only as the `SOCKETS_OWNED_KEYS` deny-list (`combogen/tuning.py:33`) and the test that asserts its absence |
| Q5 | can the literal guard pass against these readers | **PASS** — static determination; the manager then ran the filter: **2 passed / 0 failed** in the review checkout |
| Q6 | what files cannot settle | the single-commit claim (needs `git show --stat`, which the manager checked: `611d9c23` carries the publish + both constants, v1 untouched) and test execution (the manager ran the sockets/guard/combogen filters) |

## P2 notes the reviewer raised (routed, not fixed here)

1. Stale in-code prose naming v1 or the old ceiling: `SocketTuning.cs:55`, `StrainSpliceTuning.cs:14`,
   `RarityBudgetKeys.cs:59`, `SocketMaxCheck.cs:11`, `Program.cs:359-363` ("the structural 4" — now 8),
   `combogen/tuning.py:3,45`, `combogen/__init__.py:30`, `basetypegen/__init__.py:22`, `gemgen/__init__.py:6`.
   Prose only and guard-exempt, but the same drift class H7 polices.
2. A **live-read** file names the superseded revision: `gk-core/data/tuning/strain-splice.v1.json:5,8,13` (still
   the live revision, `Program.cs:374`) and `gk-core/data/tuning/base-types-gen.v1.json:9` `sourceRefs` point at
   `sockets.v1.json` for values now in v2.
3. `gk-core/data/tuning/sockets.v2.json:3` carries `"version": 2` while `sockets.v1.json:3` carries `"version": 3`
   (non-monotonic; `gk-core/tools/tuning/publish.py:894-895` writes the filename-derived `v{n+1}`). No reader reads
   the field today — a trap for one that later does.
4. The corpus is deliberately not re-stamped (`humanoid-head-guard-b.json` still `socketMax: 3` against
   v2's `head-guard: 4`), so `--retry-blocked` refuses that role by name until the owner-run SSH5.12 —
   intended, and the reason SSH6.2's helm path is closed in this checkout.

## The manager's own cheap check, for the record

Both constants name v2; `sockets.v1.json` present; every remaining literal is comment prose; the
`maxCombosPerActor` mentions are the deny-list and the absence assertions; the
`TuningRevisionLiteral` guard filter is 2/2 green in that checkout. The merge was made at the reviewed
SHA, and the `--overwrite` + `--retry-blocked` union artifact the merge exposed was repaired in
`06a7c452` (`test_strain_splice_gen.py` 68 passed / 1 failed → 69 passed).
