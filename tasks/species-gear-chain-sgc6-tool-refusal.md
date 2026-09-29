# A missing tool was reported as an opaque `FileNotFoundError`, defeating 6 modules' own refusal contract

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result |
|---|---|---|
| the defect, measured | `python -m pytest tests/test_combogen.py tests/test_item_name_repair.py -q` (cwd `gk-forge/tools/seedsmith`, `dotnet` NOT on PATH) | **6 failed, 42 passed** — every failure `FileNotFoundError: [WinError 2] The system cannot find the file specified` indistinguishable from a content defect |
| the same rows are green with the tool present | the same command with `/c/Program Files/dotnet` on `PATH` | **48 passed** — so all six are environment artifacts, not content failures (the hazard lane sgc-5 recorded 2026-09-22: "the wrapper replaces the child PATH with 10 entries and hides `dotnet`, which alone 'fails' six rows that pass without it") |
| the cause, read from the code | `grep -n "subprocess.run" gk-forge/tools/seedsmith/seedsmith/adapters/**` | 8 call sites in 6 modules, every one `subprocess.run(["dotnet", ...])` behind a docstring saying *"Raises `RepairRefused` if the tool cannot run, because a repair planned against a guessed list is worse than no repair"*. `subprocess.run` raises `FileNotFoundError` **before** the caller's own `returncode` guard can run, so the documented refusal was never delivered |
| the fix | `gk-forge/tools/seedsmith/seedsmith/tooling.py::run_tool` | one helper wrapping `subprocess.run`: a missing executable raises the CALLER'S own refusal type, naming the executable and what needed it. All 8 sites now go through it; the 5 now-unused `import subprocess` lines are removed |
| a missing tool is still a FAILURE, never a skip | same command as row 1, after the fix | the same **6 failed, 42 passed** — no `Skip` added; the error is now `RuntimeError: 'dotnet' is not runnable here (The system cannot find the file specified) — install it, or put it on PATH; needed for: the validator's authoritative collision groups` |
| no regression where the tool IS present | `python -m pytest tests/test_combogen.py tests/test_item_name_repair.py tests/test_tooling.py tests/test_grant_repair.py tests/test_tag_axis_repair.py tests/test_naming_grammar_repair.py -q` with `dotnet` on PATH | **92 passed, 7 subtests passed**; `python -m pytest tests/test_fusion_recipe.py -q` → **30 passed, 1 skipped** |
| the helper's own contract is pinned | `python -m pytest gk-forge/tools/seedsmith/tests/test_tooling.py -q` | **6 passed** — the caller's refusal type and its message; the default `RuntimeError`; the `CompletedProcess` passthrough; `stdin` never passed alongside `input` (three real call sites pass a JSON payload); `capture_output`/`text` defaults; an empty argv is a named refusal, not an `IndexError` |

## A NINTH call site, missed by my own truncated grep — and the guard that would have caught it

`a41d5d152` fixed **eight** call sites in six modules, and this fragment said so. It was wrong: the sweep
that produced that list ended in `| head -20`, so it never saw
`gk-forge/tools/seedsmith/seedsmith/adapters/items/unique_frame_repair.py:58-61` — a ninth bare-`dotnet`
`subprocess.run`, with the exact defect the commit exists to remove (its own `RepairRefused` guard cannot
fire when the executable is missing).

| Criterion | Command | Result |
|---|---|---|
| the miss, measured | `grep -rn "subprocess\.\(run\|Popen\|check_output\|check_call\|call\)" gk-forge/tools/seedsmith/seedsmith/ --include=*.py` (NO `head`) | exactly two files: `tooling.py` (the sanctioned one) and `adapters/items/unique_frame_repair.py` |
| the fix | same pattern as the other eight | `run_tool([...], cwd=…, refusal=RepairRefused, what="the UniqueFrameImpossible findings this repair plans against")`; the now-unused `import subprocess` removed |
| the fix's effect, demonstrated | `unique_frame_repair.findings(Path('gk-data/packs/fusion/data/seed/items'), validator_project=Path('gk-forge/tools/ItemSeedValidator/ItemSeedValidator.csproj'))` with `dotnet` NOT on `PATH` | **`RepairRefused: 'dotnet' is not runnable here (The system cannot find the file specified) — install it, or put it on PATH; needed for: the UniqueFrameImpossible findings this repair plans against`** — was a bare `FileNotFoundError` |
| its own tests | `python -m pytest tests/test_unique_frame_repair.py -q` | **9 passed** (both with and without `dotnet` on `PATH` — they inject a validator project, so they never reached the launch; the demonstration above is what shows the fix) |
| the GUARD, so the class cannot return | `python -m pytest gk-forge/tools/seedsmith/tests/test_tool_invocation_guard.py -q` | **2 passed** — a source scan asserting no module under `seedsmith/**` calls `subprocess.run`/`Popen`/`check_output`/`check_call`/`call` except `tooling.py`, plus a planted-module case proving the scan CAN fail |
| the whole boundary after both | `pytest <the 21 seedsmith-actions files> -q` | see the boundary table above; re-run with the guard included |

**The lesson is the truncated grep, not the missing call site.** A sweep whose output is piped through
`head` is a reading of the first N lines, and this lane quoted it as a complete inventory ("8 call sites in
6 modules") — the same class of error as the twelve self-corrections above. The guard is the fix for the
*class*: a source scan that fails on any future direct launch is what turns "I grepped" into "the build
says so".

## The same class in TEST code — a third scope, a different rule (2026-09-23, lane sgc-6)

`test_tool_invocation_guard.py` covered the package and nothing else, and the C# instance (SGC5-F5) shows
the class lives in test code too. Sweeping `gk-forge/tools/seedsmith/tests/**` for a direct launch found six:

| Site | Launch | Disposition |
|---|---|---|
| `test_distribution_planner.py:1740` | `["python", …audit-magic-numbers.py…]` | **fixed → `sys.executable`** |
| `test_innate_picker.py:1007` | the same | **fixed → `sys.executable`** |
| `test_audit_doc_citations.py:44` | `["git", …]` | left — `git` is a hard prerequisite of this repo, and the helper is the fixture's own |
| `test_sampling_quality.py:127` | `cmd_template = [sys.executable, …]` | already correct |
| `test_strain_splice_gen.py:882, 921, 944` | `[sys.executable, …]` | already correct |

**The rule that fits test code is not `run_tool`** — that helper exists so a *module's* own refusal fires.
For a test, the defect is subtler and worse: `["python", …]` may run a **different interpreter than the one
executing the test**, and fails opaquely where `python` is not on `PATH`, while `sys.executable` is by
construction present and is the same interpreter. (Measured on this machine: `shutil.which("python")` is
**None**, yet `subprocess.run(["python", "-c", "print(1)"])` still succeeds — so the bare name resolves
here through Windows' own search, which is exactly why the defect is invisible locally and would surface
elsewhere.)

| Criterion | Command | Result |
|---|---|---|
| the two fixed sites | `python -m pytest tests/test_distribution_planner.py tests/test_innate_picker.py -q -k audit_script_confirms` | **2 passed** |
| the third scope is now guarded | `python -m pytest gk-forge/tools/seedsmith/tests/test_tool_invocation_guard.py -q` | **4 passed** — the package scan + its planted case, and the tests-scope scan + its planted case |

## A TENTH site — the tool ROOT, a scope the guard did not scan (2026-09-23, lane sgc-6)

The guard scanned the package and (as of the last commit) `tests/`. It did not scan the **loose scripts
beside the package** — `gk-forge/tools/seedsmith/*.py` — and one of them launched a tool directly:

`refresh_allocated_partitions.py:47-51` ran `subprocess.run(["dotnet", "run", "--project", …ItemSeedValidator…])`
with `check=False` and its own `SystemExit` messages after it. A missing `dotnet` therefore died with an
opaque `FileNotFoundError` **before any of those messages could fire** — the same defect as the other nine,
in the one in-fence scope nobody had swept.

| Criterion | Command | Result |
|---|---|---|
| the fix | `run_tool([...], cwd=str(root), refusal=SystemExit, what="the ItemSeedValidator partition list this snapshot is regenerated from")`; `import subprocess` removed; the script now inserts its own directory on `sys.path` to import `seedsmith.tooling` (it is otherwise stdlib-only) | one implementation of "launch a repo tool", not two |
| the script still works | `python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --check` with `dotnet` on `PATH` | **`current (1069 partitions)`**, EXIT 0 |
| and now refuses by name | the same command with `dotnet` NOT on `PATH` | **`'dotnet' is not runnable here (The system cannot find the file specified) — install it, or put it on PATH; needed for: the ItemSeedValidator partition list this snapshot is regenerated from`**, EXIT 1 — was a bare traceback |
| the third scope is guarded | `python -m pytest gk-forge/tools/seedsmith/tests/test_tool_invocation_guard.py -q` | **5 passed** — the package scan, the tests-scope scan, the NEW tool-root scan, and a planted case for the package/tool-root rule |
| and the scan no longer matches prose | read | the guard skips whole-line comments, because the fixed script's own comment QUOTES `subprocess.run(["dotnet", …])` while explaining why it no longer calls it — a source scan that matches prose is a false positive |

## The scope inventory is now asserted, because "I swept" failed three times (2026-09-23, lane sgc-6)

This class has hidden a site in an unscanned scope **three times in this lane**:

1. `a41d5d152`'s sweep ended in `| head -20` and missed `unique_frame_repair.py` (the ninth site);
2. the guard then scanned the package but not `tests/` (two sites using a bare `python`);
3. and then not the tool root (`refresh_allocated_partitions.py`, the tenth).

Each time the cause was the same: *"I swept" meant "I swept the place I was thinking about"*. So the guard's
last case asserts the **inventory** rather than trusting another sweep — every `.py` under
`gk-forge/tools/seedsmith/**` must be inside one of the three scanned scopes (`seedsmith/`, `tests/`, or a tool-root
loose script), or the case fails on the day a new directory is created.

| Criterion | Command | Result |
|---|---|---|
| the inventory, measured | `find gk-forge/tools/seedsmith -name "*.py" -not -path "*/__pycache__/*" \| sed 's\|gk-forge/tools/seedsmith/\|\|' \| awk -F/ '{print $1}' \| sort \| uniq -c` | **8 loose root scripts · 420 under `seedsmith/` · 216 under `tests/`** — and no fourth scope exists today |
| no direct launch is left in any of them | `grep -rlE "subprocess\.(run\|Popen\|…)\|os\.(system\|popen\|…)\|pty\.spawn" gk-forge/tools/seedsmith/ --include=*.py` | only `tooling.py` (the sanctioned implementation) and the five test files whose launches are `sys.executable` or the fixture's own `git` helper — plus this guard's own planted strings |
| the inventory is asserted | `python -m pytest gk-forge/tools/seedsmith/tests/test_tool_invocation_guard.py -q` | **6 passed** — package scan + planted case, tests-scope scan + planted case, tool-root scan, and the scope-inventory case |
