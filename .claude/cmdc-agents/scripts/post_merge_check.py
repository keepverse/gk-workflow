#!/usr/bin/env python3
"""post_merge_check -- the manager's fail-closed gate, run against the MERGED repository head.

Python replacement for the retired `.claude/cmdc-agents/scripts/post-merge-check.ps1` (owner
ruling 2026-09-25: every new tool is Python, and a `.ps1` this repo touches for a fix is a
candidate to port rather to keep).

WHAT THIS IS
    A lane's own acceptance proves that lane at its own SHA; cross-lane interaction breakage is
    invisible to it. THIS is the gate that sees the merged result: it builds the solution, runs the
    Guard suite, and runs the declared post-split Core test surface -- all on
    `features/mega-merge`, at a clean head, with the checkout re-proved before every phase.

    A missing tool, a missing project, a missing test summary, a build/test failure, and
    unavailable legal-game/interop evidence are NEVER reported as GREEN.

    The verdict vocabulary is closed, and it is the contract:

        GREEN                                    everything ran and nothing failed
        RED -- <reasons>                         a real failure, named
        BLOCKED -- <reasons>                     nothing failed, but evidence is absent
        UNKNOWN -- no check ran, which is never a pass

## Why the PowerShell was retired

  * **The build had no timeout at all, and the test timeouts were dotnet's, not the tool's.** The
    suite leaned entirely on `--blame-hang-timeout 20m` (guards) / `10m` (tests); a wedged
    `dotnet build` had no bound whatsoever, and a test host that ignored blame-hang left the gate
    hanging with no verdict. Every child here has a hard budget that sits OUTSIDE dotnet's own, and
    is killed with its process tree on expiry. The blame-hang flag is still passed, so the inner
    guard remains.
  * **The build log was written INSIDE the repository** as `$root/.tmp-post-merge-build.txt`
    (post-merge-check.ps1:46) and removed in a `finally` (:331). A run killed between creating and
    deleting it left the file behind -- and because every phase asserts a CLEAN tree with
    `--untracked-files=all`, the NEXT run refused at 'initial merged checkout: merged checkout is
    dirty: .tmp-post-merge-build.txt', as did every run after it, until a human deleted the file.
    One interrupted run permanently bricked the gate. The log now lives in the OS temp directory:
    the tree is never polluted, and nothing observable about a verdict changes.
  * **A dead `catch` dressed the git precondition as handled.** `try { $head = (git rev-parse
    HEAD | Select-Object -Last 1)... } catch { ... }` (:283-289) cannot fire, because a native
    command that fails sets `$LASTEXITCODE` and does not throw. The fail-closed behaviour was real
    -- the SHA pattern test caught it -- but a git failure was reported under the wrong name.
    `git_now` is one function with one budget that raises the named refusal itself.
  * **`Resolve-DotnetExecutable` fell back to a hardcoded `'C:\\Program Files\\dotnet\\dotnet.exe'`**
    (:74). A committed file carries no drive-specific fallback. Resolution is `--dotnet`, then
    `DOTNET_PATH`, then `PATH`, then the `DOTNET_ROOT` / `ProgramFiles` environment values.
  * **A transcript a `2>&1` reader could not see.** `--json` now keeps stdout a single
    machine-readable envelope and moves the transcript to stderr.
  * **None of it was importable.** The manifest reader, the legal-game probe, the summary tests
    and the verdict ladder are functions with their own tests now.

    Deliberately NOT changed: an ABORT still exits 1, exactly as the retired script did, because
    the process status is what CI and the manager read. The distinction between "aborted" and
    "RED" lives in the named stage, on stderr, and in the --json envelope.

## Preserved exactly (a change here silently weakens the merged-head gate)

  * exit codes -- `0` only for GREEN, `9` for a precondition refusal, `1` for everything else,
    including every checkout abort.
  * every `ABORT:` line, every failure reason code (`guards-no-summary`,
    `build-no-success-summary`, `declared-test-manifest-*`, `test-project-*`, ...), every blocked
    reason, and the four verdict strings.
  * the checkout proof -- `git status --porcelain=v1 --untracked-files=all` empty, HEAD equal to
    the head read at the start, branch `features/mega-merge` -- asserted before the build, before
    the Guard phase, before the test phase, before EACH test project, and after all checks.
  * the declared post-split Core surface from `gk-core/tests/core-test-projects.v1.json` is ALWAYS run and
    cannot be replaced by `--test-project`, so a malformed manifest is RED rather than a silently
    smaller test set.
  * the interop split: an error in a `FusionRpg.Injector*` project is recorded as BLOCKED
    evidence (a legal-game limitation); an error anywhere else is RED. Both are named. Note the
    consequence, measured and preserved: a build that emits an interop error has by definition
    emitted no 'Build succeeded' line, so `build-no-success-summary` fires too and RED outranks
    BLOCKED -- the reachable BLOCKED path is a CLEAN build with absent legal-game evidence. The
    retired test named `test_interop_build_limitation_is_blocked_not_green` does not assert this
    either way; `test_a_successful_build_with_absent_legal_evidence_is_blocked_not_red` in
    test_post_merge_check.py pins the reachable case and the other pins the unreachable one.
  * Flag names change (`-SkipBuild` -> `--skip-build`); no refusal's MEANING changes.

## Usage

    python .claude/cmdc-agents/scripts/post_merge_check.py
    python .claude/cmdc-agents/scripts/post_merge_check.py --test-project tests/Some.Tests
    python .claude/cmdc-agents/scripts/post_merge_check.py --skip-guards   # BLOCKED, never GREEN
    python .claude/cmdc-agents/scripts/post_merge_check.py --json            # envelope on stdout

## Configuration

    --dotnet / DOTNET_PATH    the dotnet executable; else PATH, then $DOTNET_ROOT / $ProgramFiles
    FUSIONRPG_GAME_DIR        the legal BepInEx install whose interop assemblies must exist
    FUSIONRPG_ML_GAMEDIR      the legal MelonLoader install whose interop assemblies must exist

    Both game variables are machine-local and are NEVER committed. An absent or incomplete one is
    reported as BLOCKED evidence: not a pass, and not a failure of the change under review.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

#: The one branch a merged-head verdict may be taken on.
INTEGRATION_BRANCH = "features/mega-merge"

#: A closed vocabulary: this is an identifier, not prose.
SAFE_PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FULL_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
TEST_SUMMARY_LINE_RE = re.compile(r"(Passed!|Failed!|Passed:|Failed:)", re.IGNORECASE)
GUARD_DETAIL_RE = re.compile(r"(Failed FusionRpg|Passed!|Failed!|Passed:|Failed:)", re.IGNORECASE)
FAILING_LINE_RE = re.compile(r"(\[FAIL\]|Failed FusionRpg\.)", re.IGNORECASE)
FAILED_MARKER_RE = re.compile(r"(Failed!|Build FAILED)", re.IGNORECASE)
FAILED_COUNT_RE = re.compile(r"\bFailed:\s*(\d+)", re.IGNORECASE)
#: FIXED DEFECT, fail-closed direction. This pattern used to read `(?:Total|Passed)`, and `Total`
#: counts SKIPPED tests, so an all-skipped run satisfied it: VSTest prints
#: `Skipped!  - Failed: 0, Passed: 0, Skipped: 38, Total: 38`, the pattern finds `['0', '38']`, and
#: `any(int(count) > 0 ...)` reports a positive executed-test count for a run in which nothing
#: executed. Measured against this module's own predicates before the change: that shape returned
#: GREEN, while `No test matches the given testcase filter` and a genuine `Failed!` both correctly
#: returned RED - so the hole was the `Total` alternative alone, not a permissive gate. `Total` is
#: removed and only an EXECUTED count counts. The existing suite still passes because every GREEN
#: fixture also carries a `Passed: n > 0`, and every RED fixture carried `Passed: 0` already.
#: If the runner ever moves to Microsoft.Testing.Platform, whose summary reads
#: `total: 38, succeeded: 38`, then `Passed:` stops matching and this gate fails CLOSED on
#: `no-summary` - the correct direction. Add the new token then, never `total`.
POSITIVE_COUNT_RE = re.compile(r"\bPassed:\s*(\d+)", re.IGNORECASE)
BUILD_SUCCEEDED_RE = re.compile(r"Build succeeded", re.IGNORECASE)
BUILD_ERROR_LINE_RE = re.compile(r": error ")
CSPROJ_IN_ERROR_RE = re.compile(r"\[([^\]]+\.csproj)\]")

#: FIXED DEFECT, fail-closed direction only. post-merge-check.ps1:244 ended its last branch with
#: `$line -match '(?i)\bFailed:\b'`, and that expression can NEVER match: `\b` is a word/non-word
#: transition, and both `:` and whatever follows it are non-word (or end-of-input). The branch was
#: dead code, so a run reporting `Failed: <non-numeric>` was not detected as a failure. The
#: trailing `\b` is dropped. A `Failed: <n>` line is caught by the count branch above and never
#: reaches this one, so no GREEN line is reclassified.
BARE_FAILED_RE = re.compile(r"\bFailed:", re.IGNORECASE)

#: Per-stage budgets in seconds. The retired script bounded nothing itself; every budget here sits
#: OUTSIDE dotnet's own blame-hang, and blame-hang is still passed so the inner guard remains.
BUDGETS = {"build": 2400.0, "guards": 1500.0, "test": 900.0, "git": 120.0, "kill_grace": 30.0}

#: dotnet's own hang guard, unchanged.
BLAME_HANG_GUARDS = "20m"
BLAME_HANG_TESTS = "10m"

#: A guard run that fails faster than this is a contention artefact, not a verdict.
GUARD_SUSPECT_SECONDS = 120.0

#: The legal-game evidence each loader host needs before absent interop evidence is BLOCKED rather
#: than unexplained.
LEGAL_GAME_REQUIREMENTS = (
    ("FUSIONRPG_GAME_DIR",
     ("BepInEx/core/BepInEx.Core.dll", "BepInEx/interop/Assembly-CSharp.dll")),
    ("FUSIONRPG_ML_GAMEDIR",
     ("MelonLoader/net6/MelonLoader.dll", "MelonLoader/Il2CppAssemblies/Assembly-CSharp.dll")),
)

#: A build error in a project under this prefix is a legal-game limitation, not a product failure.
INTEROP_PROJECT_PREFIX = "FusionRpg.Injector"


class Refusal(Exception):
    """A named precondition failure: the tool ABORTS and never reports a verdict."""

    def __init__(self, code: int, stage: str, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.stage = stage
        self.reason = reason

    @property
    def line(self) -> str:
        return "ABORT: " + self.reason


class CheckoutAbort(Exception):
    """`Assert-MergedCheckout` fired. The tree moved under the gate, so the run stops with the
    retired script's exit code 1 and no verdict."""

    def __init__(self, context: str, reason: str) -> None:
        super().__init__(f"{context}: {reason}")
        self.context = context
        self.reason = reason

    @property
    def line(self) -> str:
        return f"ABORT: {self.context}: {self.reason}"


class Transcript:
    """stdout by default; stderr under --json, so the envelope is the only thing on stdout."""

    def __init__(self, stream) -> None:
        self.stream = stream

    def __call__(self, message: str = "") -> None:
        print(message, file=self.stream, flush=True)


class Completed:
    def __init__(self, argv: list[str], returncode: int, stdout: str, stderr: str, seconds: float,
                 timed_out: bool = False) -> None:
        self.argv = argv
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.seconds = seconds
        self.timed_out = timed_out

    @property
    def output(self) -> str:
        return self.stdout + self.stderr

    @property
    def clean_lines(self) -> list[str]:
        return [ANSI_RE.sub("", line) for line in self.output.splitlines()]

    @property
    def tail(self) -> str:
        for line in reversed([line.strip() for line in self.output.splitlines()]):
            if line:
                return line
        return "no output"


def _kill_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],  # noqa: S603,S607
                       capture_output=True, text=True, timeout=30)
        return
    import signal
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except Exception:  # noqa: BLE001 - best effort while already failing
        pass


def run(argv: list[str], *, stage: str, timeout: float, cwd: Path | None = None) -> Completed:
    """Run a child with a HARD timeout. On expiry, kill its whole tree and return a result marked
    `timed_out` -- never a bare non-zero exit a caller could read as an ordinary failure."""
    started = time.monotonic()
    try:
        proc = subprocess.Popen(  # noqa: S603 - fixed argv, no shell
            argv, cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
    except OSError as exc:
        raise Refusal(9, stage, f"cannot start {Path(argv[0]).name}: {exc}") from exc
    try:
        out, err = proc.communicate(timeout=timeout)
        return Completed(argv, proc.returncode, out or "", err or "",
                         time.monotonic() - started)
    except subprocess.TimeoutExpired as expired:
        _kill_tree(proc.pid)
        try:
            out, err = proc.communicate(timeout=BUDGETS["kill_grace"])
        except subprocess.TimeoutExpired:
            out, err = "", ""
        return Completed(argv, 1, (expired.stdout or "") + (out or ""),
                         (expired.stderr or "") + (err or ""), time.monotonic() - started,
                         timed_out=True)


def git_now(repo: Path, *args: str, stage: str = "git") -> Completed:
    """One git reader, one budget, one named refusal."""
    return run(["git", "-C", str(repo), *args], stage=stage, timeout=BUDGETS["git"])


def git_last_line(result: Completed) -> str:
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def test_failed_summary(lines: list[str]) -> bool:
    """post-merge-check.ps1:234-249, ported branch for branch. Per line, and the scan CONTINUES
    past a `Failed: 0` line -- the retired `elseif` skipped only that line's fallback."""
    for line in lines:
        if FAILED_MARKER_RE.search(line):
            return True
        counts = FAILED_COUNT_RE.findall(line)
        if counts:
            if any(int(count) > 0 for count in counts):
                return True
        elif BARE_FAILED_RE.search(line):
            return True
    return False


def test_positive_test_count(lines: list[str]) -> bool:
    """A suite that reports no positive executed-test count has proved nothing."""
    return any(int(count) > 0 for line in lines
               for count in POSITIVE_COUNT_RE.findall(line))


def test_build_succeeded(lines: list[str]) -> bool:
    return any(BUILD_SUCCEEDED_RE.search(line) for line in lines)


def has_test_summary(lines: list[str]) -> bool:
    return any(TEST_SUMMARY_LINE_RE.search(line) for line in lines)


def merged_checkout_error(repo: Path, expected_head: str, expected_branch: str) -> str | None:
    """Clean, at the head read at the start, on the integration branch."""
    status = git_now(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        return f"git status failed: {status.tail}"
    dirty = [line for line in status.stdout.splitlines() if line.strip()]
    if dirty:
        return "merged checkout is dirty: " + " ;; ".join(dirty[:5])
    head = git_now(repo, "rev-parse", "HEAD")
    current = git_last_line(head).lower()
    if head.returncode != 0 or current != expected_head:
        return f"merged checkout HEAD changed: expected '{expected_head}', got '{current}'"
    branch = git_now(repo, "rev-parse", "--abbrev-ref", "HEAD")
    current_branch = git_last_line(branch)
    if branch.returncode != 0 or current_branch != expected_branch:
        return (f"merged checkout branch changed: expected '{expected_branch}', "
                 f"got '{current_branch}'")
    return None


def assert_merged_checkout(repo: Path, head: str, branch: str, context: str) -> None:
    error = merged_checkout_error(repo, head, branch)
    if error:
        raise CheckoutAbort(context, error)


def resolve_test_project_path(requested: str, root: Path, add_failure) -> str | None:
    """post-merge-check.ps1:82-105. A directory must hold EXACTLY ONE csproj, and it must be named
    after the directory. Both failures are named."""
    candidate = Path(requested)
    if not candidate.is_absolute():
        candidate = root / requested
    if candidate.is_dir():
        projects = sorted(candidate.glob("*.csproj"))
        if len(projects) != 1:
            add_failure(f"test-project-ambiguous: {requested} contains {len(projects)} csproj "
                        "files; expected exactly one")
            return None
        if projects[0].stem != candidate.name:
            add_failure(f"test-project-name-mismatch: {requested} resolves to {projects[0].name}, "
                        f"expected {candidate.name}.csproj")
            return None
        return str(projects[0].resolve())
    if candidate.is_file():
        return str(candidate.resolve())
    return None


def declared_test_projects(root: Path, add_failure) -> list[str]:
    """post-merge-check.ps1:111-171 -- the declared post-split surface, read from the manifest."""
    manifest_path = root / "tests" / "core-test-projects.v1.json"
    if not manifest_path.is_file():
        add_failure(f"declared-test-manifest-missing: {manifest_path}")
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        add_failure(f"declared-test-manifest-invalid: {exc}")
        return []
    if not isinstance(manifest, dict):
        add_failure("declared-test-manifest-invalid: root is not an object")
        return []
    if type(manifest.get("schemaVersion")) is not int or manifest.get("schemaVersion") != 1:
        add_failure("declared-test-manifest-schema: expected integer schemaVersion 1")
        return []
    projects = manifest.get("projects")
    if not isinstance(projects, list):
        add_failure("declared-test-manifest-schema: projects must be an array")
        return []

    paths: list[str] = []
    seen: set[str] = set()
    for entry in projects:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            add_failure("declared-test-manifest-schema: every project needs a string name")
            continue
        name = entry["name"]
        if not SAFE_PROJECT_NAME_RE.fullmatch(name):
            add_failure(f"declared-test-manifest-name-invalid: {name}")
            continue
        if name.casefold() in seen:
            add_failure(f"declared-test-manifest-duplicate: {name}")
            continue
        seen.add(name.casefold())
        paths.append(str(Path("tests") / name))
    if not paths:
        add_failure("declared-test-manifest-empty: no post-split projects")

    residual = manifest.get("residual", "")
    if not isinstance(residual, str) or not SAFE_PROJECT_NAME_RE.fullmatch(residual):
        add_failure("declared-test-manifest-missing-residual")
    elif residual.casefold() in seen:
        add_failure(f"declared-test-manifest-duplicate: residual {residual} is already declared")
    else:
        seen.add(residual.casefold())
        paths.append(str(Path("tests") / residual))
    return paths


def legal_game_evidence_error(environ: dict[str, str]) -> str | None:
    """post-merge-check.ps1:199-232. Absent or incomplete legal-game evidence is BLOCKED evidence."""
    problems: list[str] = []
    for name, files in LEGAL_GAME_REQUIREMENTS:
        value = (environ.get(name) or "").strip()
        if not value:
            problems.append(f"{name} is not set")
            continue
        directory = Path(value)
        if not directory.is_dir():
            problems.append(f"{name} path does not exist: {value}")
            continue
        for relative in files:
            if not (directory / relative).is_file():
                problems.append(f"{name} is missing {str(Path(relative))}")
    return "; ".join(problems) if problems else None


def resolve_dotnet(requested: str, environ: dict[str, str]) -> str:
    """--dotnet, then DOTNET_PATH, then PATH, then the environment's own install roots.

    No drive-specific fallback is written into this file, and a dotnet that cannot be found is the
    named refusal below: no verdict, never a guess.
    """
    if requested:
        candidate = Path(requested)
        if candidate.is_file():
            return str(candidate.resolve())
        found = shutil.which(requested)
        if found:
            return found
        raise Refusal(9, "dotnet", "dotnet not found (pass --dotnet <path>). Refusing to report a "
                                   "verdict on checks that cannot run.")
    if environ.get("DOTNET_PATH") and Path(environ["DOTNET_PATH"]).is_file():
        return str(Path(environ["DOTNET_PATH"]).resolve())
    found = shutil.which("dotnet")
    if found:
        return found
    executable = "dotnet.exe" if os.name == "nt" else "dotnet"
    for variable in ("DOTNET_ROOT", "ProgramFiles"):
        value = (environ.get(variable) or "").strip()
        if not value:
            continue
        candidate = Path(value) / "dotnet" / executable
        if candidate.is_file():
            return str(candidate.resolve())
    raise Refusal(9, "dotnet", "dotnet not found (pass --dotnet <path>). Refusing to report a "
                               "verdict on checks that cannot run.")


class Report:
    """The accumulating verdict. Nothing is decided until every phase has run."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.blocked: list[str] = []
        self.ran = 0

    def failure(self, message: str) -> None:
        self.failures.append(message)

    def block(self, message: str) -> None:
        self.blocked.append(message)

    def verdict(self) -> str:
        if self.failures:
            return "RED -- " + ", ".join(self.failures)
        if self.ran == 0:
            return "UNKNOWN -- no check ran, which is never a pass"
        if self.blocked:
            return "BLOCKED -- " + "; ".join(self.blocked)
        return "GREEN"


def run_build_phase(dotnet: str, root: Path, report: Report, timeout: float,
                    transcript: Transcript) -> None:
    transcript("=== build FusionRpg.slnx (legal-game/interop limitations are reported as "
               "BLOCKED) ===")
    report.ran += 1
    result = run([dotnet, "build", "FusionRpg.slnx", "-c", "Debug", "--nologo"],
                 stage="build", timeout=timeout, cwd=root)
    lines = result.clean_lines
    if result.timed_out:
        report.failure(f"build-timeout: dotnet build exceeded its {timeout:.0f}s budget and was "
                       "killed")

    by_project: dict[str, int] = {}
    error_lines = [line for line in lines if BUILD_ERROR_LINE_RE.search(line)]
    for line in error_lines:
        match = CSPROJ_IN_ERROR_RE.search(line)
        project = Path(match.group(1)).name if match else "unknown"
        by_project[project] = by_project.get(project, 0) + 1

    if test_failed_summary(lines):
        report.failure("build: failed summary was emitted despite a zero process exit")
    if not test_build_succeeded(lines):
        report.failure("build-no-success-summary: the build emitted no successful build summary")

    interop = sorted(name for name in by_project if name.startswith(INTEROP_PROJECT_PREFIX))
    real = sorted(name for name in by_project if not name.startswith(INTEROP_PROJECT_PREFIX))
    if error_lines and not by_project:
        real = ["unknown"]
    transcript(f"build_exit={result.returncode}  error_lines={len(error_lines)}  "
               f"projects_with_errors={len(by_project)}")
    for project in sorted(by_project):
        transcript(f"  {by_project[project]:6d}  {project}")
    if real:
        report.failure("build: non-interop project errors: " + ", ".join(real))
    elif result.returncode != 0 and not interop:
        report.failure(f"build: dotnet exited {result.returncode} without a classifiable project "
                       "error")
    if interop:
        report.block("legal-game/interops build unavailable: " + ", ".join(interop))


def run_guards_phase(dotnet: str, root: Path, report: Report, timeout: float, head: str,
                     transcript: Transcript) -> None:
    transcript("=== Guard suite ===")
    report.ran += 1
    result = run([dotnet, "test", "tests/FusionRpg.Guard.Tests", "-c", "Debug", "--nologo",
                  "--blame-hang-timeout", BLAME_HANG_GUARDS],
                 stage="guards", timeout=timeout, cwd=root)
    lines = result.clean_lines
    seconds = round(result.seconds, 1)
    if result.timed_out:
        report.failure(f"guards-timeout: dotnet test exceeded its {timeout:.0f}s budget and was "
                       "killed")
    if not has_test_summary(lines):
        report.failure("guards-no-summary: the Guard run did not produce a test summary")
    if test_failed_summary(lines):
        report.failure("guards: failed summary was emitted despite a zero process exit")
    if not test_positive_test_count(lines):
        report.failure("guards-zero-tests: no positive executed-test count was reported")
    if result.returncode != 0:
        report.failure(f"guards: dotnet test exited {result.returncode}")
    if result.returncode != 0 and seconds < GUARD_SUSPECT_SECONDS:
        report.failure("guards-suspect-contention: failed unusually quickly; rerun alone before "
                       "routing")
    transcript(f"guards_seconds={seconds}")
    for line in lines:
        if GUARD_DETAIL_RE.search(line):
            transcript("  " + line.strip())
    transcript(f"guards_exit={result.returncode}")
    if result.returncode != 0:
        failing = [line for line in lines if FAILING_LINE_RE.search(line)]
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{datetime.now().microsecond // 1000:03d}"
        path = Path(tempfile.gettempdir()) / f"post-merge-guards-{head[:8]}-{stamp}.log"
        transcript(f"  failing lines: {len(failing)} -- each needs an owning row, never an "
                   "allowlist entry")
        try:
            path.write_text(result.output, encoding="utf-8")
        except OSError:
            return
        transcript(f"  transcript: {path}")


def run_test_phase(dotnet: str, root: Path, report: Report, test_path: str, timeout: float,
                   transcript: Transcript) -> None:
    display = Path(test_path).stem
    report.ran += 1
    result = run([dotnet, "test", test_path, "-c", "Debug", "--nologo", "--blame-hang-timeout",
                  BLAME_HANG_TESTS], stage=f"test:{display}", timeout=timeout, cwd=root)
    lines = result.clean_lines
    if result.timed_out:
        report.failure(f"{display}-timeout: dotnet test exceeded its {timeout:.0f}s budget and was "
                       "killed")
    if not has_test_summary(lines):
        report.failure(f"{display}-no-summary: the test run did not produce a test summary")
    if test_failed_summary(lines):
        report.failure(f"{display}: failed summary was emitted despite a zero process exit")
    if not test_positive_test_count(lines):
        report.failure(f"{display}-zero-tests: no positive executed-test count was reported")
    for line in lines:
        if TEST_SUMMARY_LINE_RE.search(line):
            transcript("  " + line.strip())
    transcript(f"{display}_exit={result.returncode}")
    if result.returncode != 0:
        report.failure(f"test: {display} exited {result.returncode}")


class Config:
    def __init__(self, args: argparse.Namespace) -> None:
        repo_input = args.repo if args.repo else Path(__file__).resolve().parent.parent.parent
        try:
            self.root = Path(repo_input).resolve(strict=True)
        except OSError as exc:
            raise Refusal(9, "repo", f"repository root cannot be resolved: {exc}") from exc
        self.dotnet = resolve_dotnet(args.dotnet, os.environ)
        self.build_timeout = args.build_timeout
        self.guards_timeout = args.guards_timeout
        self.test_timeout = args.test_timeout


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gate(args: argparse.Namespace, transcript: Transcript) -> tuple[int, dict]:
    """The whole gate, in the order documented at the top of this file."""
    config = Config(args)
    root = config.root

    head_result = git_now(root, "rev-parse", "HEAD", stage="head")
    if head_result.returncode != 0:
        raise Refusal(9, "head", "cannot identify the merged head: " + head_result.tail)
    head = git_last_line(head_result)
    branch_result = git_now(root, "rev-parse", "--abbrev-ref", "HEAD", stage="head")
    if branch_result.returncode != 0:
        raise Refusal(9, "head", "cannot identify the merged branch: " + branch_result.tail)
    branch = git_last_line(branch_result)
    if not FULL_SHA_RE.fullmatch(head):
        raise Refusal(9, "head", f"git did not return a full merged-head SHA (got '{head}').")
    head = head.lower()
    if branch != INTEGRATION_BRANCH:
        raise Refusal(9, "branch", f"merged-head check must run on '{INTEGRATION_BRANCH}', "
                                   f"not '{branch}'.")
    assert_merged_checkout(root, head, branch, "initial merged checkout")

    report = Report()
    transcript(f"dotnet={config.dotnet}")
    transcript(f"post-merge check  HEAD={head}  branch={branch}")
    transcript(f"STARTED={iso_now()}")

    assert_merged_checkout(root, head, branch, "before build phase")
    if args.skip_build:
        report.block("build skipped by request; merged-head build evidence is absent")
    else:
        run_build_phase(config.dotnet, root, report, config.build_timeout, transcript)
        legal = legal_game_evidence_error(os.environ)
        if legal:
            report.block("legal-game/interops evidence is unavailable: " + legal)

    assert_merged_checkout(root, head, branch, "before Guard phase")
    if args.skip_guards:
        report.block("Guard suite skipped by request; merged-head guard evidence is absent")
    else:
        run_guards_phase(config.dotnet, root, report, config.guards_timeout, head, transcript)

    requested: list[str] = list(declared_test_projects(root, report.failure))
    requested.extend(args.test_project or [])

    test_paths: list[str] = []
    seen: set[str] = set()
    for entry in requested:
        if not entry.strip():
            report.failure("test-project-empty-entry")
            continue
        before = len(report.failures)
        resolved = resolve_test_project_path(entry, root, report.failure)
        if not resolved:
            if len(report.failures) == before:
                report.failure("test-project-missing: " + entry)
            continue
        if resolved.casefold() not in seen:
            seen.add(resolved.casefold())
            test_paths.append(resolved)

    assert_merged_checkout(root, head, branch, "before test phase")
    for test_path in test_paths:
        display = Path(test_path).stem
        assert_merged_checkout(root, head, branch, f"before test project '{display}'")
        transcript(f"=== {test_path} ({display}) ===")
        run_test_phase(config.dotnet, root, report, test_path, config.test_timeout, transcript)
    assert_merged_checkout(root, head, branch, "after all checks")

    verdict = report.verdict()
    transcript(f"=== VERDICT: {verdict} ===")
    transcript(f"FINISHED={iso_now()}")
    return (0 if verdict == "GREEN" else 1), {
        "head": head,
        "branch": branch,
        "dotnet": config.dotnet,
        "ran": report.ran,
        "verdict": verdict,
        "failures": report.failures,
        "blocked": report.blocked,
        "testProjects": test_paths,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="post_merge_check.py",
        description="The manager's fail-closed gate at the MERGED head: build, Guard suite, and "
                    "the declared post-split Core test surface. A missing tool, project or summary "
                    "is never GREEN.")
    parser.add_argument("--test-project", action="append", default=[], metavar="PATH",
                        help="additional explicit test project; repeatable. The declared surface is "
                             "always included and cannot be replaced by this list")
    parser.add_argument("--skip-build", action="store_true",
                        help="skip the build; reported BLOCKED, never GREEN")
    parser.add_argument("--skip-guards", action="store_true",
                        help="skip the Guard suite; reported BLOCKED, never GREEN")
    parser.add_argument("--dotnet", default="",
                        help="the dotnet executable (default: $DOTNET_PATH, then PATH, then "
                             "$DOTNET_ROOT / $ProgramFiles)")
    parser.add_argument("--repo", default="",
                        help="repository root (default: the checkout this script lives in)")
    parser.add_argument("--build-timeout", type=float, default=BUDGETS["build"],
                        help=f"hard budget for the build, seconds (default {BUDGETS['build']:.0f})")
    parser.add_argument("--guards-timeout", type=float, default=BUDGETS["guards"],
                        help=f"hard budget for the Guard suite, seconds "
                             f"(default {BUDGETS['guards']:.0f})")
    parser.add_argument("--test-timeout", type=float, default=BUDGETS["test"],
                        help=f"hard budget per test project, seconds (default {BUDGETS['test']:.0f})")
    parser.add_argument("--json", action="store_true",
                        help="print one machine-readable envelope on stdout; the transcript moves "
                             "to stderr")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for name in ("build_timeout", "guards_timeout", "test_timeout"):
        if getattr(args, name) <= 0:
            print(f"post_merge_check: --{name.replace('_', '-')} must be a positive number of "
                  "seconds", file=sys.stderr)
            return 2

    transcript = Transcript(sys.stderr if args.json else sys.stdout)
    envelope: dict[str, object] = {
        "tool": "post_merge_check",
        "ok": False,
        "exitCode": 2,
        "stage": None,
        "refusal": None,
        "verdict": None,
        "failures": [],
        "blocked": [],
    }
    try:
        exit_code, detail = run_gate(args, transcript)
        envelope.update(detail)
        envelope["ok"] = exit_code == 0
        envelope["exitCode"] = exit_code
        envelope["stage"] = "complete"
    except Refusal as refusal:
        print(refusal.line, file=transcript.stream, flush=True)
        print(f"post_merge_check refused at stage '{refusal.stage}' with exit {refusal.code}",
              file=sys.stderr, flush=True)
        envelope["exitCode"] = refusal.code
        envelope["stage"] = refusal.stage
        envelope["refusal"] = refusal.reason
        if args.json:
            print(json.dumps(envelope, indent=2))
        return refusal.code
    except CheckoutAbort as abort:
        print(abort.line, file=transcript.stream, flush=True)
        print(f"post_merge_check aborted at '{abort.context}' with exit 1", file=sys.stderr,
              flush=True)
        envelope["exitCode"] = 1
        envelope["stage"] = f"checkout_assert:{abort.context}"
        envelope["refusal"] = abort.reason
        if args.json:
            print(json.dumps(envelope, indent=2))
        return 1

    if args.json:
        print(json.dumps(envelope, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
