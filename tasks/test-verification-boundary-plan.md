# Implementation plan: `test-verification-boundary` (prefix `TVB`)

**Map:** [test-verification-boundary-map.md](../docs/architecture/test-verification-boundary-map.md) ·
**Specs:** [registry-contract](../docs/architecture/test-verification-boundary/spec-registry-contract.md) ·
[python-test-lane](../docs/architecture/test-verification-boundary/spec-python-test-lane.md) ·
[seam-coverage](../docs/architecture/test-verification-boundary/spec-seam-coverage.md) ·
[core-split-analyzer](../docs/architecture/test-verification-boundary/spec-core-split-analyzer.md) ·
[core-split-apply](../docs/architecture/test-verification-boundary/spec-core-split-apply.md) ·
[core-split-wiring](../docs/architecture/test-verification-boundary/spec-core-split-wiring.md) ·
[core-registry-rekey](../docs/architecture/test-verification-boundary/spec-core-registry-rekey.md) ·
[data-tests-sharding](../docs/architecture/test-verification-boundary/spec-data-tests-sharding.md) ·
**Tasks:** [test-verification-boundary-todo.md](test-verification-boundary-todo.md) ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md) — lane D. This program owns the
parent's hard edges **H4** and **H5** on its side, and the lane-D live defect (G14, `release.yml`).

## Overview

Contributor-tooling program; it changes no game loop. It closes the gaps the map found by running the
tools (§2 G1–G18): the release gate masks test failures; six test roots, the Python tools, the
generators and most data trees have no verification owner; `Data.Tests` cannot parallelise in one
process; and `FusionRpg.Core.Tests` is one assembly that R-TV1 splits into per-subsystem projects.
The work runs as five tracks: a **workflow track** (the live defect first, then the R15/R24 CI lines
that need nothing else), a **sharding track** and an **analyzer track** that are independent, a
**registry track** that edits the same file as `solid-enforcement` and therefore follows SE0.7 (H5),
and the **Core split**, which needs the analyzer, the registry's project groups and a reviewed
manifest.

## Verified against code (2026-09-18, this session)

| Claim | Check | Result |
|---|---|---|
| `release.yml:43-46` has four `dotnet test` lines with no exit check, `--blame-hang-timeout 5min` | read the file; a line scan of both workflows for the W0 rule | true; **`ci.yml` already satisfies the W0 rule**, `release.yml` is the only violator, so `WorkflowExitCheckTests` is green the day it lands with the fix |
| `test_resource_ownership.py:38,40` pin `version == 5` and `len == 166` | read | true |
| Nothing of this program is built | `ls` of `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`, `scripts/lib/VerificationBoundaries.ps1`, `gk-core/tools/TestSplitAnalyzer`, `scripts/test-sharded.ps1`, `WorkflowExitCheckTests.cs` | none exist; registry is at `schemaVersion` 1 |
| **`.github/workflows/*.yml` has no verification owner** | `verify-change.ps1 -Paths .github/workflows/release.yml -PlanOnly -AllowUnscoped` | `VERIFICATION BOUNDARY MISSING` — the W0 spec's own verify command cannot run as written. `TVB0.1` adds the owner (see Risks) |
| `gk-core/tools/tuning/test_resource_ownership.py` is unmapped | same, on that path | `VERIFICATION BOUNDARY MISSING` (map G5). `TVB0.2` is verified by pytest directly until `TVB3.3` maps it |
| Map citations `ci.yml:140-141`, `:153-156`, `:180-181`, `:321/323` | read | match |

## Architecture decisions (from the map; not re-litigated)

- **Hard failure, not ratchet**, for `tests/**` enforcement (map §3.1).
- **One `schemaVersion` sequence shared with `solid-enforcement`** (map §3.2): 1 today → **2 SE0.7** →
  3 `registry-contract` → 4 `python-test-lane` → 5 `seam-coverage`. Each bump lands in the same commit
  as planner and guard support. `data-tests-sharding` and the Core-split modules bump nothing.
- **Python tests select by file, never `pytest -k`** (§3.3).
- **Generator/corpus checks are `script` runner projects**, not guards (§3.4); wrappers under
  `gk-core/scripts/checks/`, kept identical to CI by `GeneratorCheckCiParityTests`.
- **The split keeps every namespace and relative path**; projects are direct children of `tests/`;
  files move byte for byte; split mode never routes through `FileMover.Plan` (§3.5, G17).
- **Test projects never reference test projects**; shared code is linked via one `.props` (§3.6).
- **The split extends `gk-core/tools/FileMove`**; the analyzer is a separate Roslyn tool (§3.7, SOLID "O").
- **Project groups** in the registry (§3.8, `registry-contract` C7).
- **Pre-existing reds:** `knownRed` + a `red` ledger row, printed every run, self-expiring; never a
  deselect; a test this program owns is fixed, not registered (§3.9, `python-test-lane` D6).
- **R15** approves the CI lines; **R24** wires `gk-fusion/tools/LawnCombatObserver.Tests` and
  `gk-fusion/tools/ProveLiveProbe.Tests` into `ci.yml`. The exact text of every workflow line is map §7.1
  (E1–E7) and the owner spec; the plan quotes it in the task, never paraphrases it. **Not in
  `release.yml`:** E2, E3, E4, E7.

## Dependency graph (modules)

```text
core-split-wiring W0 (TVB0.1) ──► CI lines that need nothing else: TVB0.3 (E2, after TVB0.2 — H4), TVB0.4 (E7/W7, R24)

data-tests-sharding (TVB1.1–1.5)                    independent

core-split-analyzer (TVB1.6–1.10)                   independent
        │
SE0.7 ══H5══► registry-contract (TVB2.1–2.7, schema 3) ──► python-test-lane (TVB3.1–3.10, schema 4) ──► seam-coverage (TVB4.1–4.7, schema 5)
                     │ C7 groups (TVB2.3)
                     ▼
core-split-analyzer ─► [Checkpoint M: manifest review, map §7.3] ─► core-split-apply ⇄ core-split-wiring (TVB5.*) ─► core-registry-rekey (TVB6.*)
```

## Suggested order and parallel lanes — **suggested, not enforced**

Only the edges marked **H#** are the parent's hard edges; everything else may be reordered, split or
parallelised by whoever builds it.

| Lane | Tasks | Starts | Why this order |
|---|---|---|---|
| D-wf (workflows) | TVB0.1 → TVB0.2 → TVB0.3 → TVB0.4 | now | live defect first (parent §2, CC1); TVB0.3's pytest step waits for TVB0.2 (**H4**) |
| D-shard | TVB1.1 → 1.2 → 1.3 → 1.4 → 1.5 | now | independent; its CI line (1.4) after W0 so the test enforcing rule (a) exists |
| D-analyzer | TVB1.6 → 1.7 → 1.8 → 1.9 → 1.10 | now | independent, read-only |
| D-registry | TVB2.* → TVB3.* → TVB4.* | after **SE0.7** (**H5**) | one file, monotonic schema; SE0.1–SE0.4 precede SE0.7 in SE's own plan |
| D-split | TVB5.1 → 5.2–5.4 → Checkpoint M → 5.5 → 5.6 → 5.7 → 5.8.k → 5.9 → TVB6.* | 5.1–5.4 now; 5.6 after TVB2.3 | apply and wiring land in one commit per increment; rekey after the split |

D-wf, D-shard and D-analyzer can run as three parallel sessions today. D-split's tool work
(TVB5.2–5.4) can run beside them; its increments wait for groups (TVB2.3) and the manifest review.

**Shared-file serialisation (soft, coordinate — not an H-edge):**
`gk-core/scripts/verification-boundaries.v1.json`, `scripts/verify-change.ps1`,
`gk-core/scripts/guard-verification-boundaries.py` are also edited by SE0.3/SE0.7 and SE2.1;
`.github/workflows/ci.yml` by SE0.5 and SE1.1. Commit one at a time; the later commit rebases. A
registry edit that lands before SE0.7 (TVB0.1, TVB1.1, TVB1.6) adds boundaries only and never
touches the `guards` map, so SE0.7's migration is not disturbed.

## Phases

| Wave | Module(s) | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 0 | core-split-wiring W0/W7, python-test-lane step 0 + E2 | TVB0.1–0.4 | S, XS, XS, S | internally sequential; parallel with waves 1a/1b |
| 1a | data-tests-sharding | TVB1.1–1.5 | M, M, XS, S, S | yes (own files; 1.5 touches `verify-change.ps1`) |
| 1b | core-split-analyzer | TVB1.6–1.10 | M, M, M, M, S | yes (own tool) |
| 2 | registry-contract | TVB2.1–2.7 | M, M, M, S, M, M, XS | sequential (same three scripts) |
| 3 | python-test-lane | TVB3.1–3.10 | M, M, M, S, M, M, S, S, M, XS | mostly sequential; 3.4 and wrappers 3.6–3.9 parallel-safe after 3.2 |
| 4 | seam-coverage | TVB4.1–4.7 | M, S, M, M, S, S, M | 4.4–4.7 one root per commit |
| 5 | core-split-apply + core-split-wiring | TVB5.1–5.9 (5.8.k repeats per manifest project) | XS, M, M, M, S, M, M, M each, S | 5.1–5.4 parallel with waves 1–2; increments strictly one at a time |
| 6 | core-registry-rekey | TVB6.1–6.4 | S, M, S, S | sequential |

## Checkpoints (review points, not gates)

- **Checkpoint 0 — live defect closed** (feeds parent CC1): release gate exit-checked, rule enforced by
  a test; `gk-core/tools/tuning` suite green and in CI; the two `tools/*.Tests` projects run in CI.
- **Checkpoint 1 — independent tracks**: sharded runner's completeness proven by set comparison and
  in CI; analyzer report produced, deterministic, three edges spot-checked.
- **Checkpoint M — manifest review (map §7.3)**: the owner is shown the analyzer's md report and the
  manifest draft. **Default if unanswered when TVB5.7 is reached: the analyzer's clean-SCC proposal is
  the manifest** (one project per reference-clean group, everything else stays in the residual). Not a
  gate: every increment is journal-revertible and a pure rename in git.
- **Checkpoint 2 — registry contract (schema 3)**.
- **Checkpoint 3 — Python lane (schema 4)**.
- **Checkpoint 4 — seam coverage (schema 5)**.
- **Checkpoint 5 — split landed** (the program's "finishing a large feature" point: `test-fast.ps1
  -AllDefault` once).
- **Checkpoint 6 — program close** (feeds parent CC7).

## Cross-program edges

| Edge | Kind | Note |
|---|---|---|
| **SE0.7** → TVB2.1 | **H5** (parent) | SE0.7 removes the `guards` section and sets `schemaVersion` 2; TVB2.1 starts from 2 |
| SE0.1–SE0.4 → SE0.7 | SE's own chain | referenced, not duplicated: catalog, its tests, `run-guards.ps1` |
| SE0.1 → TVB4.6 | soft | `generated-seed` resolves through the catalog SE0.1 seeds |
| SE0.2 → TVB2.5 | soft | the `bench-compile` catalog row must pass SE's R1–R8 registry tests |
| **SE0.8** → TVB3.4 | ordering (monotonic pin) | SE0.8 moves `StubRegisterTests`' kind pin 3→4 (`solid`); TVB3.4 moves it 4→5 (`red`) |
| SE2.1 `tuning-immutability` | soft | attached by SE; TVB4.4 keeps every guard a rewritten tuning entry carries |
| SE0.5, SE1.1 (`ci.yml`) | shared file | serialise commits; neither touches test lines |
| TVB0.2 → TVB0.3 | **H4** (parent) | pytest CI step only after the stale pins are dropped (R15: never red) |

## Tuning publishes

**None.** This program owns no row of the parent §5 ledger. `seam-coverage` maps `gk-core/data/tuning/**`
paths (wildcard owners, so a `publish.py` `v{n+1}` is covered on arrival) and never edits any file
under `data/**`.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Workflow files are unmapped, so every TVB task that edits `ci.yml`/`release.yml` would hit `VERIFICATION BOUNDARY MISSING` (found this session; not in the specs) | Med | TVB0.1 adds owner `ci-workflows` → `guard`, focused on a new `guard.workflows` `VerificationId` carried by every Guard test that reads a workflow file (`CiWiringGuardTests`, `WorkflowExitCheckTests`, and later H-T5, P7/P8, W1–W6). AGENTS.md: an unmapped path is a boundary defect to fix, never a reason to run a broad suite |
| SE0.7's todo acceptance does not name the `schemaVersion` 2 bump that map §3.2 assigns it | Med | TVB2.1 asserts it starts from 2. If SE0.7 lands without the bump, raise it with SE's owner; TVB never jumps 1 → 3 silently |
| Concurrent SE sessions editing the same three scripts and registry | Med | shared-file serialisation above; each TVB registry rewrite keeps every guard the replaced entry carried (seam-coverage S1, rekey "Always") |
| The CI seedsmith step (`ci.yml:341`) is already red for pre-existing reasons | Low | "first CI run green" is judged per step for TVB's own steps; D6 never deselects; CI stays red until the seedsmith owner fixes the corpus |
| Machine contention (many concurrent `dotnet` processes) skews shard walls | Low | shard walls are readings recorded in `_meta.measured`, never asserted; re-measure on an idle-ish box |
| A Core split increment breaks a string-keyed or location-sensitive test | Med | analyzer `BLOCKS SPLIT` findings fixed first (TVB5.1); depth invariant; build + test new project **and** residual before keeping; journal revert |
| A Core `BalanceGuard` filter that matches nothing exits 0 | Med | W6 set equality (TVB5.6) |

## Defaults shipped behind (no gates)

- **Manifest:** the analyzer's clean-SCC proposal (Checkpoint M), residual keeps the rest.
- **Roslyn package** (`Microsoft.CodeAnalysis.CSharp`): **approved by the owner 2026-09-18 (R26)** for the
  analyzer tool project only; added at TVB1.7 (previously: "the owner is told … default — add it" (the ideal names Roslyn; a
  tool-only, removable dependency).
- **Shard count:** 2 (the only measured shape) until TVB1.3 measures 2 vs 4.
- **`full` level:** any tuning/seed/generated/fixture subtree with no S1 evidence is declared `full`
  and listed by `-Report` — visible, never a false owner.
- **`knownRed`:** only the five seedsmith actions tests, behind one `red` row owned by the seedsmith
  actions pipeline.
- **W7 exemption table:** lands empty (R24).

## Out of scope (map §6), not tasks

Injector tests; `DebugEndpoints.cs` focused mapping; web; fixing pre-existing seedsmith reds (except
`test_resource_ownership.py`); `tools/**` as an enforced root; pointing CI at the `gen-*` wrappers
(the D5 dedupe — outside R15, "ask first"); the stale `AGENTS.md` line about `test_items_adapter.py`
(local-only file — an owner item, reported, not edited).
