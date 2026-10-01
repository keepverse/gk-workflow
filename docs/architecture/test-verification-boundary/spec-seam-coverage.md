# Spec: `seam-coverage`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
[`registry-contract`](spec-registry-contract.md) (wildcards, guard-only boundaries, enforced-root
machinery), [`python-test-lane`](spec-python-test-lane.md) (the `script` runner and its
`scripts/checks/gen-*.py` wrappers, `schemaVersion` 4) · closes map gap G8 and the tuning half of G4.

## Objective

The ideal's Bazel-diff caveat — a selector must also cover "inputs outside the ordinary import
graph, such as schemas, … code generators, shared fixtures" — is still almost entirely open. Readings
on this commit (map §2 G8; printed for scale, never pinned): 144 of 149 files under `gk-core/data/tuning/`,
2,215 of 2,234 under `gk-data/packs/fusion/data/seed/`, 906 of 948 under `gk-data/packs/fusion/data/generated/`, and all 79 under
`gk-core/tests/fixtures/` match no owner. An agent that publishes a tuning version, edits a fixture, or
regenerates a tree gets `VERIFICATION BOUNDARY MISSING`.

This module maps those four roots **by rule**, turns each root into an enforced root once it is fully
mapped, and gives an input with no local proof an explicit, visible declaration instead of a false
project.

**User:** every session that publishes tuning, edits fixtures, or regenerates seed/generated trees.

## Design

### S1 — the mapping rule (one rule, four roots)

For every input subtree, the owner is the **narrowest thing that actually reads that file**, found
by evidence, in this order:

1. A test that loads the **committed file** (text scan of `tests/**` and `tools/*.Tests/**` for the
   file's stem or directory, e.g. `lawn-attrition.v`, `fixtures/combat`) → that test's
   `VerificationId`/`testFiles` (focused), or its project (module).
2. A CI gate that validates the file (a `script` project from `python-test-lane` D5, or one of the
   three below) → an owner boundary whose `project` is that script check (module level).
3. Both, when both exist → the test is the owner and the script check is a **seam** on the same
   paths, so both run.
4. Neither → an explicit **`full`-level** owner (S3).

Guards are attached separately and never replace a check: `generated-seed` (below) and, where
`solid-enforcement` has created it, `tuning-immutability` (SE2.1, attached by that module; map §5.4).

Never an owner chosen because it is "nearby": `ContractTuningTestBootstrap` configures the Core tuning
hubs from **literal C# objects**, not the files (`gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs:33-40`),
so "Core.Tests reads tuning" is false for most domains and mapping `gk-core/data/tuning/**` to `core` would be
the Launcher→Guard defect again.

Additional `script` projects this module adds (same shape and parity test as `python-test-lane` D5,
under `gk-core/scripts/checks/`):

| Script project | Command | CI line |
|---|---|---|
| `gen-content-validate` | `dotnet run --project gk-forge/tools/AtomImporter -c Release -- --check --validate --db <temp dir>` (the wrapper creates and removes the temp dir; a removal failure fails the check). CI passes `$env:RUNNER_TEMP/atom-validate-db`, so `GeneratorCheckCiParityTests` compares the command up to `--db` | `ci.yml:287` |
| `gen-corpus-dump-verify` | `dotnet run --project gk-forge/tools/CreatureCorpusDump -c Release -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` | `ci.yml:298` |
| `gen-item-seed-validator` | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | `ci.yml:304` |

`generated-seed` (`gk-core/scripts/guard-generated-seed.py`; locally it checks the working tree plus staged
changes against HEAD, `guard-generated-seed.py:22`) attaches as a **guard** to **every** generated
tree. It is the mechanical form of the "never hand-edit generated seed" rule, and a repo-wide
invariant, so it is a guard. It is not in today's `guards` map. It resolves through the enforcement
catalog, which SE0.1 seeds with every `scripts/guard-*.ps1` (map §5). Its CI `-Range` argument lives
in the catalog row (`spec-guard-runner.md` rule 4); the planner calls it with none.

**A rewrite never verifies less.** Where this module replaces an existing entry, the new entry keeps
the old one's `project`, `verificationId` and every guard. `deployment-hierarchy-tuning`
(`verification-boundaries.v1.json:2928`) keeps `data` and `magic-numbers`. `lawn-attrition-tuning`
(`:2313`) keeps `core.lawn-attrition-ladder`. It also keeps any guard `solid-enforcement` attached
meanwhile.

### S2 — per-root specifics

Where several checks apply to one subtree, one of them is the owner's `project` and each of the others
is a **seam** on the same paths. A boundary names exactly one project, and seams are additive
(`gk-core/scripts/verify-change.py:794-802`).

| Root | Pattern shape | Known owners to start from (verified) |
|---|---|---|
| `gk-core/data/tuning/**` | one owner per **domain**: `gk-core/data/tuning/<domain>.v*.json` (wildcard, so a `publish.py` `v{n+1}` is covered on arrival, `gk-core/tools/tuning/publish.py:10`) | replace the exact-name entries `lawn-attrition-tuning` (`verification-boundaries.v1.json:2313`), `deployment-hierarchy-tuning` (`:2928`), `power-scale-tuning` (`:2987`, which today leaves `power-scale.v1`/`v2` unmapped) with wildcard forms; `aptitudes.v*.json` gains `gen-resource-ownership` (`ci.yml:68` reads it) |
| `gk-core/tests/fixtures/**` | one owner per fixture subtree | `fixtures/effects/**`, `fixtures/combat/**` are linked into Core.Tests (`FusionRpg.Core.Tests.csproj:54-55`) → `core`; `action-traces`/`battle-traces` are read by `Actions/ActionAdoptionFixtures.cs`, `Battle/Adoption/*` → `core` until `core-registry-rekey` narrows them |
| `gk-data/packs/fusion/data/generated/**` | one owner per generated tree, its `project` the tree's script check, guard `generated-seed` | `creatures/**` → `gen-creature-species`; `creatures/_species-build-plan.json` (exact) → `gen-build-plan`; `passive-tree/**` → existing `generated-trees` (`:607`, project `treebinder`, kept) + seam `gen-passive-tree`; all three carry `generated-seed` |
| `gk-data/packs/fusion/data/seed/**` | one owner per top-level subtree; authored sub-trees (`**/_registry/**`, `**/_exemplars/**`) get their own entries where a reader differs | `items/**` → `gen-items-gate`, `gen-item-seed-validator`; `creatures/**` → `gen-creature-contract`, `gen-creature-report`, `gen-creature-metrics`, `gen-creature-preflight`; `creatures/_dump/**` → `gen-corpus-dump-verify`; `structures/**` → `gen-structure-contract`; `atoms/**` keeps `seed-atoms-fallback` + `effect-catalog-drift` seam, `atoms/generated/**` adds `gen-family-expand`, `generated-seed`; `passive-tree/**` → `gen-passive-tree`; the remaining subtrees are derived by S1 at build time |

### S3 — `full` level: an explicit "no local proof"

Evidence levels become `focused | module | seam | full` — the fourth member already exists in the
predecessor's vocabulary (`verification-boundaries-map.md` §4: "`full` … CI, nightly, release").
A `full` owner boundary names **no** `project` and **no** `guards`; the planner prints
`<path> -> <boundary> (full): no local check; CI full evidence owns this input` and selects nothing.

Guard rules that keep it from becoming a dumping ground:

- `full` is legal only for paths under `data/**` and `gk-core/tests/fixtures/**` — never `src/**`, `tests/**/*.cs`,
  `tools/**` or `scripts/**`;
- `-Report` lists every `full` boundary under "inputs with no local proof" — the live Bazel-gap list;
- the level vocabulary's size is pinned at 4 in a Guard test, with the reason: a fifth level changes
  what a plan means and is a reviewed change.

This extends `registry-contract` C3's derivation: `full` ⇔ owner with neither project nor guards.
It changes what a reader must understand, so this module bumps `schemaVersion` from `4` (set by
`python-test-lane`) to `5` (map §3.2), in the same commit as planner and guard support. The planted
registry in `VerificationBoundaryWorkflowTests.cs` moves with it.

### S4 — enforced roots, switched on one at a time

`guard-verification-boundaries.py` gains an enforced-roots list (code-owned, in the shared lib). A root
enters the list only in the commit that maps every file under it, in this order: `gk-core/data/tuning/**`,
`gk-core/tests/fixtures/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**`. Before a root is on the list, unmapped files
under it are refused by the planner (as today) but do not fail the guard; after, they do. This is the
predecessor map's own rollout rule (`verification-boundaries-map.md` §6, "enforced roots").

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/data/tuning/lawn-attrition.v2.json -PlanOnly -AllowUnscoped
.\scripts\verify-change.ps1 -Paths gk-data/packs/fusion/data/generated/passive-tree/<file> -PlanOnly -AllowUnscoped
python gk-core/scripts/guard-verification-boundaries.py --report      # includes "inputs with no local proof"
# S1 evidence scan for one domain (read-only)
rg -l "lawn-attrition\.v" tests tools --glob "*.cs" --glob "*.py"
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/verification-boundaries.v1.json` | domain/subtree owners for the four roots; wildcard rewrites of the three exact tuning entries |
| `gk-core/scripts/lib/verification_boundaries.py` | enforced-roots list; `full` level |
| `gk-core/scripts/guard-verification-boundaries.py` | S3 rules; S4 walk; report section |
| `gk-core/scripts/verify-change.py` | `full` prints and selects nothing |
| `gk-core/scripts/checks/gen-content-validate.py`, `gen-corpus-dump-verify.py`, `gen-item-seed-validator.py` | (new) `script` projects |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` | cases below |
| `docs/contributing/testing-standard.md` §6 | one paragraph: data inputs select through the planner; `full` means CI-only |

## Code style

Registry entries, domain-shaped (the planner's own JSON style):

```jsonc
{ "id": "tuning-lawn-attrition", "kind": "owner",
  "paths": ["data/tuning/lawn-attrition.v*.json"],
  "project": "core", "verificationId": "core.lawn-attrition-ladder", "level": "focused", "guards": [] },
{ "id": "tuning-<domain>", "kind": "owner",
  "paths": ["gk-core/data/tuning/<domain>.v*.json"], "level": "full" }
```

(The second entry shows the shape only; which domains end up `full` is decided by S1 evidence.)

## Testing

| # | Case | Asserts |
|---|---|---|
| S-T1 | planted `data/tuning/x.v1.json` + `x.v*.json` owner; add `x.v2.json` | resolves with no registry edit |
| S-T2 | `full` boundary on `src/Foo.cs` | guard fails |
| S-T3 | `full` boundary on `data/foo.json` | plan prints the CI-owned line and has zero checks |
| S-T4 | enforced root with one unmapped planted file | guard fails naming it; same file outside an enforced root does not fail the guard |
| S-T5 | level vocabulary | exactly `focused, module, seam, full` (closed vocabulary; reason in the test) |
| S-T6 | the real registry | guard passes with every switched-on root |
| S-T7 | the real registry: plan for `gk-core/data/tuning/deployment-hierarchy.v3.json` (a planted, not-yet-published name) | same `project` and guards as today's exact entry (a rewrite never verifies less) |
| S-T8 | the real registry: plan for a file under `gk-data/packs/fusion/data/generated/creatures/` | `gen-creature-species` check + `generated-seed` guard |

No test asserts how many files a root holds, how many domains exist, or how many `full` boundaries
there are — all three are readings that move whenever content ships.

## Boundaries

- **Always:** derive each owner from S1 evidence and cite it in the commit body; attach
  `generated-seed` to generated trees; switch a root on only when it is fully mapped.
- **Ask first:** none (no CI edit; the three wrappers mirror existing CI steps).
- **Never:** drop a `project`, `verificationId` or guard when rewriting an existing entry.
- **Never:** a blanket `gk-core/data/tuning/**` → `core` (or any project) fallback; an owner that does not read
  the file; `full` on code; editing any file under `data/**` in this module (it maps paths, it does not
  touch content — the generated-seed rule applies in full).

## Success criteria

- [ ] Publishing a new tuning version needs no registry edit.
- [ ] Every file under each switched-on root resolves; the guard fails on a planted unmapped file there.
- [ ] `-Report` prints "inputs with no local proof".
- [ ] No boundary maps an input to a project that does not read it (each S1 owner cites its evidence).
- [ ] `schemaVersion` is 5 and both scripts accept only 5.
- [ ] S-T1–S-T8 green, verified with `.\scripts\verify-change.ps1 -Paths <every changed script, registry and test path> -Session <id>`.

## Open questions

None. Which domains land at `full` is a finding of S1, reported by `-Report`, not a decision.
