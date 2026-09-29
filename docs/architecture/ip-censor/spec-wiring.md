# Spec: `ip-censor` / `wiring` — an independent Python tool, verified like one

**Program:** `ip-censor` · **Module id:** `wiring` · **Depends on:** `report`
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Audit:** [../../research/ip-censor-spec-audit-2026-09-19.md](../../research/ip-censor-spec-audit-2026-09-19.md) A1, A5, A6
**Binding dependency:** [../test-verification-boundary/spec-python-test-lane.md](../test-verification-boundary/spec-python-test-lane.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Amended 2026-09-19 (owner rulings IC-3,
IC-5)** — adds the release-gate hook and the advisory CI scan.

---

## Objective

`ip-censor` is an **independent Python tool, shaped like `gk-forge/tools/seedsmith`** — its own package, its own
`pyproject.toml`, its own exact-pinned `requirements.lock`, its own `tests/`, and a **first-class
verification lane** so `verify-change.ps1` runs *its* pytest suite rather than a C# project that proves
nothing about it.

Owner decision (2026-09-19): *"add a python tool like seedsmith, independent tool for this task."* That
resolves the open question this spec previously carried as a choice between following the
`tuning-publish-tool` C#-lane precedent and adding a real Python project. **Decision: a real Python
project.**

**Why this matters, measured.** `spec-python-test-lane.md:11-20` records the exact failure the C# lane
produces today: `gk-core/tools/tuning/publish.py` maps to boundary `tuning-publish-tool` →
`dotnet test` of **Guard.Tests**, *"which contains no reference to `gk-core/tools/tuning` — the check runs,
passes, and proves nothing about the changed file."* A `python` runner lane is what fixes it.

**Success criteria**
- `.\scripts\verify-change.ps1 -Paths gk-core/tools/ip-censor/ipcensor/report.py -Session <active>` returns a
  **plan that names the ip-censor pytest lane** — not the throw
  `"VERIFICATION BOUNDARY MISSING: <path>. Add an owner mapping; do not run a broad suite as a
  fallback."` (`scripts/verify-change.ps1:118`), and not a `dotnet test` of an unrelated project.
- `python -m pytest gk-core/tools/ip-censor/tests -q` runs from a **clean clone** after installing from the
  committed lockfile; no reliance on a machine that happens to have `pyahocorasick`.
- `ci.yml` runs the tool's tests and fails the build on a red suite. (This tests the **tool**; it is
  not a content gate. A red `ip-censor` test suite is a code defect, not an IP finding.)
- A Guard test proves the lane cannot silently go unwired.
- **Amended 2026-09-19 (owner ruling IC-3).** The release workflow runs
  `python -m ipcensor.report scan --fail-on enforced` before it publishes, and an enforced finding
  fails the release. The release checklist names the same command. CI runs the scan **advisory** only:
  it uploads the report and exits 0 on findings. No commit, `verify-change.ps1` run or CI job is
  blocked by a finding.

## Tool shape — mirrored from `gk-forge/tools/seedsmith`, deliberately

| Concern | seedsmith (`gk-forge/tools/seedsmith/`) | ip-censor (`gk-core/tools/ip-censor/`) |
|---|---|---|
| Package | `seedsmith/` importable package | `ipcensor/` importable package |
| Metadata | `pyproject.toml`, `requires-python = ">=3.11"` | same floor |
| Dependencies | `[project.dependencies]` with **exact pins** (`jieba==0.42.1`) | `pyahocorasick==2.3.1`, `regex==2026.3.32` (+ stdlib only elsewhere) |
| Frozen env | `requirements.lock`, installed first in CI | `requirements.lock`, same discipline |
| Tests | `tests/` (144 files), `pytest==9.0.2` in dev extra | `tests/`, same |
| Pytest config | `[tool.pytest.ini_options]` `testpaths = ["tests"]`, `pythonpath = ["."]` | same keys |
| CLI | `python -m seedsmith <verb>` | `python -m ipcensor.report <verb>` |
| Install | `pip install -r requirements.lock; pip install -e . --no-deps` | same two commands |

**Independence is explicit, and it is the reason `spec-suggest` refuses to import seedsmith.** The two
tools share no code: `ip-censor` does not import `seedsmith`, and neither is a dependency of the other.
They share **conventions** (exact pins, editable install, `python -m <tool>` entry, a `tests/` tree),
because an operator should not have to learn two shapes. Sharing a *configuration key shape* is
deliberate too — `IPCENSOR_LLM_*` mirrors `SEEDSMITH_LLM_*` (`spec-suggest.md` §Configuration) — while
the code stays separate.

**Verified versions on this machine:** `pyahocorasick` **2.3.1**, `regex` **2026.3.32**, Python
**3.13.12**. Pins are `==` and the lockfile is committed (`spec-dependency-baseline.md:34`,
*"`pyproject.toml` with exact pins, never ranges"*).

## The lane depends on an unbuilt module — stated plainly

The `pytest` runner kind does **not** exist yet. Measured this session:

| Fact | Evidence |
|---|---|
| The lane is **spec'd, not built** | `docs/architecture/test-verification-boundary/spec-python-test-lane.md` (Wave 3: TVB3.1–TVB3.5, all `[ ]` in `tasks/test-verification-boundary-todo.md:168-196`) |
| The registry is still `schemaVersion: 1`, `projects` all strings, **no `runner` key**, no `knownRed` | Loaded `gk-core/scripts/verification-boundaries.v1.json` directly |
| The shared lib does not exist | `Test-Path scripts/lib/VerificationBoundaries.ps1` → **False**; `gk-core/scripts/checks/` → **False** |
| Wave 3 is gated behind Wave 2 (`registry-contract`, schema 3) | `tasks/test-verification-boundary-todo.md:170` — TVB3.1 deps `TVB2.*`, all `[ ]` |

So `wiring` has a **hard external dependency**, and it is not this program's to build:
`python-test-lane` TVB3.1 (object projects + closed `runner` vocabulary + `schemaVersion` 4) and TVB3.2
(the pytest runner branch). This spec does not duplicate those — it declares the dependency and names
exactly what it consumes.

### What this spec consumes from `python-test-lane` (already decided there — do not re-decide)

- **Runner vocabulary** is closed: `dotnet` / `pytest` / `script` (`spec-python-test-lane.md` D1). This
  spec uses `pytest`; it adds no fourth member.
- **Project shape:** `{ "runner": "pytest", "root": "gk-core/tools/ip-censor", "tests": "tests" }` (D1).
- **Selector:** a boundary on a `pytest` project selects with `testFiles`, **never**
  `verificationId`, and **never `pytest -k`** (D2) — *"a substring match over test names, so a rename
  silently selects zero or extra tests."*
- **`selfSelect`** for a changed file named `test_*.py` under the project's tests directory; any other
  file there (a conftest.py, fixtures) selects the module run (D2).
- **Exit 5 is a failure** — a selector collecting nothing is a registry defect, not a pass (D3).
- **`knownRed`** exists for a genuinely pre-existing red test (D6), and this tool **must not need
  it**: `ip-censor` is new code, so its suite is green from the first commit. If a lane needs a
  `knownRed` entry, that is this program's defect to fix, not to register.

### The precedent that lets `wiring` land before the lane does

`TVB0.3` already shipped a **standalone pytest CI step** for `gk-core/tools/tuning` while the registry was still
plain strings (`tasks/test-verification-boundary-todo.md:26`, live at `.github/workflows/ci.yml:311-317`):

```yaml
      - name: gk-core/tools/tuning own tests (test-verification-boundary python-test-lane, R15)
        shell: pwsh
        working-directory: gk-core/tools/tuning
        run: |
          python -m pytest . -q -p no:cacheprovider
          if ($LASTEXITCODE -ne 0) { throw "gk-core/tools/tuning's own test suite failed" }
```

So `wiring` has **two landable halves**, and this is the honest sequencing:

1. **Now (no dependency):** the tool exists as a Python package with pinned deps, a `tests/` tree, an
   install step, and a CI step in exactly the `TVB0.3` form. The tool is runnable and its suite runs in
   CI — the whole value, without the lane.
2. **After `python-test-lane` Wave 3 lands:** add the `ipcensor` project (`runner: "pytest"`) and its
   owner boundary, so `verify-change.ps1` selects the tool's own tests locally. This is the half that
   closes A1 fully.

**What half 1 does not fix, said out loud:** until half 2, `verify-change.ps1 -Paths <ip-censor file>`
still throws `VERIFICATION BOUNDARY MISSING`. The tool is usable via its CLI and its tests run in CI,
but the repo's focused local-verification path does not cover it. That is a **named, temporary gap**
with a named unblocker — not something to paper over by mapping the tool to a C# project, which is the
trap `spec-python-test-lane.md:14-20` documents.

## The release gate hook — amended 2026-09-19 (owner ruling IC-3)

The owner ruled the scan a **release gate**: it runs before any release and blocks it on a hit, and it
never blocks generation. The repo already has both release surfaces, measured this session:

| Hook | Where | What `wiring` adds |
|---|---|---|
| The release workflow | `.github/workflows/release.yml` — triggered on a `v*` tag (`:3-6`); the step `Unit tests (pre-publish)` (`:40`) runs before `Publish player pack` (`:258`; T12's gate step landed at `:212`, so this said `:81` before that commit) | A step after `Unit tests (pre-publish)` and before `Publish player pack`: install `gk-core/tools/ip-censor` from its lockfile, run the scan with `--fail-on enforced --authored-only`, check `$LASTEXITCODE` and `throw` on non-zero. The explicit exit check is required: `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` guards both workflows against unchecked commands |
| The release checklist | `docs/runbook/release-prove.md` §"Before tagging" (`:5`) | One checklist line naming the same command, so a local tag is gated the same way the workflow is |
| CI, advisory | `.github/workflows/ci.yml`, after the tool's own pytest step | `python -m ipcensor.report scan --format json` with the plan uploaded as a build artifact. Exit code 0 on findings, by design |

The gate needs no model and no network (`scan` never reaches `suggest`), and the registry is tracked
(IC-5), so the gate is reproducible on the release runner.

*Audit 2026-09-19:* the install runs in `gk-core/tools/ip-censor`, but the **scan** runs from the repository
root, and `report` resolves the tree from `git rev-parse --show-toplevel`: `git ls-files` run inside
`gk-core/tools/ip-censor` lists only that folder, and a gate over it would pass vacuously. The same holds for the
advisory CI step.

**What the gate does not replace.** The IC-4 fixes are release-blocking in their own right (see the
map's *Release-blocking fixes*). The `Jackson*` species ids are compound identifiers
(`JacksonZombie`) that the boundary policy deliberately does not split, so that fix is proven by the
rename map's own test, not by this scan. *Audit 2026-09-19:* the owner answered the plan's gate G1
**yes** — the ids themselves are re-keyed (`tasks/ip-censor-todo.md` T19b), and the same test then
covers id fields.

## Tech Stack

Python **3.11+** floor (seedsmith's), tested on 3.13.12. Exact-pinned third-party:
`pyahocorasick==2.3.1` (the `scan` automaton), `regex==2026.3.32` (if UAX#29 boundaries are wanted —
see `spec-scan.md`, which notes `regex`'s `(?V1)\b` **also** fails on `PvZ融合版`). `pytest==9.0.2` in a
`dev` extra, mirroring seedsmith.

No new C# dependency, no change to `verify-change.ps1`'s command building from this program (that is
`python-test-lane`'s), and no change to `guard-verification-boundaries.py`'s project validation beyond
accepting the object form the lane's schema 4 defines.

## Commands

```powershell
# Tool install (clean clone), same two commands as seedsmith
cd gk-core/tools/ip-censor; python -m pip install -r requirements.lock; python -m pip install -e . --no-deps
# The tool's own suite
python -m pytest gk-core/tools/ip-censor/tests -q -p no:cacheprovider
# The tool itself
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report scan --format json --authored-only

# After half 2 (the lane): the focused path, which must name the ipcensor lane
.\scripts\verify-change.ps1 -Paths gk-core/tools/ip-censor/ipcensor/report.py -Session <active-session-id> -PlanOnly
# Registry integrity, must stay green through the schema-4 amendment
python gk-core/scripts/guard-verification-boundaries.py
```

## Project Structure

```text
gk-core/tools/ip-censor/
  ipcensor/            → the package (source, registry, census, scan, suggest, curate, llm, report, cli)
  tests/               → test_source.py, test_registry.py, test_census.py, test_scan.py,
                         test_suggest.py, test_curate.py, test_report.py, test_wiring.py  (all new)
  pyproject.toml       → name = "ip-censor", requires-python, exact pins, [dev] pytest, pytest config
  requirements.lock    → frozen: pyahocorasick==2.3.1, regex==2026.3.32, pytest==9.0.2, …
  .env.example         → IPCENSOR_LLM_* keys (new; mirrors gk-forge/tools/seedsmith/.env.example)
gk-data/packs/fusion/data/seed/ip-censor/_registry/   → the four authored JSON registries + the IC-2 import filter
gk-core/scripts/verification-boundaries.v1.json   → half 2: + 1 project, + 1 owner boundary (schema 4)
.github/workflows/ci.yml                  → half 1: install + pytest step, TVB0.3 form;
                                            + advisory scan step (IC-3)
.github/workflows/release.yml             → the release gate step (IC-3)
docs/runbook/release-prove.md             → one "Before tagging" checklist line (IC-3)
gk-core/tests/FusionRpg.Guard.Tests/              → + a lane-wiring guard (half 2)
```

## Code Style

```jsonc
// half 2 — registry addition, consuming python-test-lane's schema 4 (D1 shape)
"projects": {
  // ...existing...
  "ipcensor": { "runner": "pytest", "root": "gk-core/tools/ip-censor", "tests": "tests" }
},
"boundaries": [
  {
    "id": "ip-censor-tool",
    "kind": "owner",
    "paths": ["gk-core/tools/ip-censor/**", "gk-data/packs/fusion/data/seed/ip-censor/**"],
    "project": "ipcensor",
    "level": "module",
    "testFiles": ["test_registry.py", "test_scan.py", "test_source.py"]
  }
]
```

`runner` is not invented here — it is the closed vocabulary `python-test-lane` D1 defines, and the
guard pins its membership. `testFiles` are repo-relative with last-segment wildcards allowed (D2); the
list above is illustrative of the *form*, and the real list is derived from which test file imports the
changed module, matching D4's `<area>` rule (*"derived, not guessed"*).

## Testing Strategy

Three levels, and the third is what makes the module real:

1. **The tool's own suite** (`gk-core/tools/ip-censor/tests/`), green from the first commit — new code, so no
   `knownRed` entry is legitimate. Run by CI in half 1.
2. **The wiring test** (`test_wiring.py` (new)) — a package-level test proving the shape the rest of the program assumes:
   importing `ipcensor.*` works from a clean install; `python -m ipcensor.report registry-check`
   exits 0; `pyahocorasick` and `regex` are importable at the pinned versions. It fails loudly if a
   dependency drifts out of the lockfile.
3. **A Guard test for the lane (half 2)** — the Python counterpart of `CiWiringGuardTests`, which the
   lane's own spec introduces as `CiPytestWiringTests` (`spec-python-test-lane.md` §CI): *"every pytest
   project in the registry has a `python -m pytest` line in `ci.yml` under a step whose
   `working-directory` equals its `root`."* `wiring` adds the `ipcensor` entry that test then covers;
   it does not write a second, competing guard.

The acceptance criterion is the **command**, not a proxy: `verify-change.ps1 -PlanOnly` over a proposed
path must exit 0 and name the ipcensor lane.

## Boundaries

- **Always:** keep the lockfile exact-pinned and committed; install in CI the same two commands as
  seedsmith; keep `ipcensor` and `seedsmith` code-independent; land the CI step (half 1) **with** the
  first code file, never after; prove the acceptance command after half 2.
- **Ask first:** adding any dependency beyond the two pinned matchers; adding a `knownRed` entry (it is
  almost certainly this program's defect instead); pointing CI at a wrapper script rather than the
  direct command.
- **Never:** make an unmapped path acceptable by loosening `verify-change.ps1` — `AGENTS.md` names the
  missing mapping the defect and *"never compensate by running the full suite"*; import `seedsmith`
  from `ipcensor`; commit a `.env`; use a floating version; register the tool as a `guard` (it is a
  project with tests, and `python-test-lane` D5 is explicit that a script check is **not** a guard);
  make the CI scan step fail on findings, or add the scan to `verify-change.ps1` (IC-3 — only the
  release blocks).

## Open Questions

1. **Does the `ipcensor` boundary cover `gk-data/packs/fusion/data/seed/ip-censor/_registry/**` too?** Recommendation:
   **yes, same boundary** — a registry edit changes the tool's behaviour, mirroring how `gk-core/data/tuning/**`
   inputs ride with their generator. Owner to confirm, since it makes a data edit select a Python lane.
2. **Which test files go in `testFiles`?** Per D4's *"derived, not guessed"* rule, the list is produced
   at build time by scanning `tests/` for imports of the changed module and committing the result. The
   illustration above is a form, not the final list.
3. **Timing of half 2.** Should `wiring` (a) land half 1 now and half 2 when `python-test-lane` Wave 3
   ships, or (b) wait for Wave 3 and land both together? Recommendation: **(a)** — half 1 is
   independently valuable and has precedent (TVB0.3), and waiting would block the tool on an unrelated
   program's schedule. The cost of (a) is a documented temporary gap in local verification; the cost of
   (b) is indefinite.
