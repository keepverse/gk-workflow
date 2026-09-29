#!/usr/bin/env python3
"""accept_lane -- run and record fail-closed acceptance for one manager lane at an immutable SHA.

Python replacement for the retired `.claude/cmdc-agents/scripts/accept-lane.ps1` (owner ruling
2026-09-25: every new tool is Python, and a `.ps1` this repo touches for a fix is a candidate to
port rather to keep).

WHAT THIS IS
    The manager's proof instrument. One lane, one immutable full 40-character commit SHA, one
    schema-versioned acceptance artefact at `.claude/cmdc-agents/acceptance/<lane>-<8-char>.json`.
    `merge-lanes.py` consumes that artefact and refuses to merge without exact GREEN evidence, so
    every guarantee below is load-bearing for every lane in every programme.

    The order IS the contract:

        1  resolve the repo, the check set and the full expected SHA   (nothing is created yet)
        2  reject existing evidence that is stale or malformed
        3  bind the SHA to the lane's history, and to integration when --merge is asked
        4  read the registered known-red debt
        5  refuse a contended tree (unless --allow-contended)
        6  create/sync the review checkout and PIN it to the SHA       (detached, clean, exact)
        7  re-prove the review checkout before EVERY check, and once more after all of them
        8  run each `name|||command`, parse its output, attribute its failures
        9  write the artefact, then VALIDATE THE WRITTEN ARTEFACT with the same validator
       10  only then consume it for --merge, re-validating with the GREEN requirement

## Why the PowerShell was retired

  * **Nothing had a timeout.** `cmd.exe /d /s /c $checkSpec.command` (accept-lane.ps1:425) and every
    `git` call could hang forever: no verdict, no artefact, no exit code. A gate that can hang is
    indistinguishable from a gate that is still working. Every child here has a hard budget and is
    KILLED, with its process tree, on expiry.
  * **`Set-Location` mutated the process working directory** (accept-lane.ps1:392, :557) and the
    review-checkout proof then depended on where the process happened to be standing, so
    `Get-ReviewCheckoutError` could not be unit-tested without reproducing that mutation. Every
    `git` call now takes an explicit `cwd=`, so the proof is a function of its arguments.
  * **The machine-local review helper was a runtime `$env:USERPROFILE` literal** reached through
    `Join-Path` (accept-lane.ps1:240), and `Join-Path` THROWS when `USERPROFILE` is unset -- so a
    machine without that variable died with a raw PowerShell error instead of the tool's own named
    refusal. Resolution is now explicit and ordered: `--cmdc-agent`, then
    `FUSIONRPG_CMDC_AGENT`, then the home-relative default; a missing result is the named refusal
    `cmdc review tool is missing`.
  * **Directory creation was unchecked** (accept-lane.ps1:282, :542). Had the log directory failed
    to be created, every check's `Set-Content` failed, the log read back EMPTY, and a genuinely
    passing check was caught only by accident -- because a passing check with no readable output
    happens to trip the `exit 0 in 0s with no output` guard. Both directories are now created, or
    refused by name.
  * **The transcript was `Write-Output`, so a caller reading `2>&1` got NOTHING** from a run that
    was working correctly. `--json` now keeps stdout a single machine-readable envelope and moves
    the transcript to stderr; without `--json` the transcript is on stdout, as before.
  * **None of it was importable.** The evidence validator, the failed-summary test, the
    integration-ancestry proof and the verdict ladder are functions with their own tests now, so
    the schema is a contract a test can hold instead of a comment.

    Deliberately NOT changed: a check's `command` is still an arbitrary command line handed to the
    platform shell (accept-lane.ps1:425). This tool is manager-invoked, not a trust boundary, and
    narrowing that would be a behaviour change rather than a port.

## Preserved exactly (a change here silently corrupts every future acceptance)

  * exit codes -- `0` GREEN, `1` a non-GREEN verdict or a refused merge, `2` a check-set or
    evidence defect, `9` a precondition defect.
  * the verdict vocabulary, matched as a CLOSED set and case-sensitively:
    `GREEN` / `RED` / `RED-KNOWN` / `UNATTRIBUTED`.
  * the schema-version-2 artefact, field for field, including `shortSha == sha[:8]` and the ten
    required per-check keys.
  * every `ABORT:` line and every `MERGE REFUSED:` reason.
  * the merge commit subject: `merge(lane): <lane> at <short> (accepted full SHA; schema-valid
    GREEN evidence)`.
  * Flag names change (`-Merge` -> `--merge`); no refusal's MEANING changes.

## Usage

    python .claude/cmdc-agents/scripts/accept_lane.py --lane <lane> --expect-sha <40-hex> \\
        --check 'smoke|||dotnet test gk-core/tests/FusionRpg.Guard.Tests' \\
        --check 'core|||dotnet test tests/Some.Core.Tests' --merge

    python .claude/cmdc-agents/scripts/accept_lane.py ... --json     # envelope on stdout

## Configuration

Machine-local values come from a flag or the environment, never from this file:

    --cmdc-agent / FUSIONRPG_CMDC_AGENT   the review-checkout helper (default:
                                           ~/.claude/skills/cmdc-subagent/scripts/cmdc_agent.py)
    --log-root                            default: <temp>/cmdc-acceptance
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

#: The one integration branch a merge may target.
INTEGRATION_BRANCH = "features/mega-merge"

#: A CLOSED vocabulary, not a pattern. `-cnotin` in the PowerShell meant an exact, case-sensitive
#: membership test; an unanchored regex here is the defect the resume-00a brief recorded.
ACCEPTANCE_VERDICTS = ("GREEN", "RED", "RED-KNOWN", "UNATTRIBUTED")

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# NOTE the non-capturing group: `findall` must return the WHOLE matched line, because the retired
# script recorded `$_.Value.Trim()` -- the whole line -- not the alternation.
SUMMARY_RE = re.compile(
    r"^[ \t]*(?:Passed!|Failed!|Build succeeded|Build FAILED|Test Run Failed\.|Failed:[ \t]*\d+.*"
    r"|OK --|ACTOR-HUB).*$",
    re.IGNORECASE | re.MULTILINE,
)
FAILED_TEST_RE = re.compile(r"^[ \t]*Failed[ \t]+([A-Za-z0-9_.<>`]+\.[A-Za-z0-9_<>`]+)",
                            re.IGNORECASE | re.MULTILINE)
COMPILER_ERROR_RE = re.compile(r"^.*error [A-Z]{2}[0-9]{3}.*$", re.IGNORECASE | re.MULTILINE)
FAILED_MARKER_RE = re.compile(r"Failed!", re.IGNORECASE)
FAILED_COUNT_RE = re.compile(r"\bFailed:\s*(\d+)", re.IGNORECASE)
# FIXED DEFECT, fail-closed direction only. accept-lane.ps1:60 ended its last branch with
# `$Summary -match '(?i)\bFailed:\b'`, and that expression can NEVER match: `\b` is a word/non-word
# transition, and both `:` and whatever follows it are non-word (or end-of-input). So the branch
# was dead code, and a check whose output carried `Failed: <non-numeric>` (`Failed: unknown`,
# `Failed: see log`) was NOT detected as a failure. The trailing `\b` is dropped so the marker is
# what it always meant to be. This can only ADD reds: a `Failed: <n>` line is caught by the count
# branch above and never reaches this one, so a GREEN line cannot be reclassified.
BARE_FAILED_RE = re.compile(r"\bFailed:", re.IGNORECASE)

#: Load-fragile Guard families: a failure in one of these is a suspect, never an attribution.
FLAKE_FAMILIES = (
    "PlantSideStatusGuardTests",
    "SubprocessPipeDrainGuardTests",
    "VerificationBoundaryWorkflowTests",
    "TuningRevisionLiteralGuardTests",
)

#: A held test binary means this tree is not an isolated evidence source.
CONTENDED_PROBES = (
    "tests/FusionRpg.Guard.Tests/bin/Debug/net8.0/FusionRpg.Guard.Tests.dll",
    "tests/FusionRpg.Core.Tests/bin/Debug/net6.0/FusionRpg.Core.Tests.dll",
    "tests/FusionRpg.Server.Tests/bin/Debug/net8.0/FusionRpg.Server.Tests.dll",
)

CHECK_RESULT_ARRAYS = ("failedTests", "knownRedTests", "newRedTests", "flakeSuspectTests", "errors")
REQUIRED_CHECK_KEYS = ("check", "exit", "seconds", "summary") + CHECK_RESULT_ARRAYS + ("log",)

#: Per-stage budgets in seconds. Nothing in this tool is unbounded; the retired script bounded
#: nothing, which is the defect that cost a real hang.
BUDGETS = {"git": 120.0, "review": 900.0, "check": 3600.0, "kill_grace": 20.0}


class Refusal(Exception):
    """A named precondition failure.

    `line` is the retired `ABORT:` vocabulary, byte for byte. `stage` and `code` are what a machine
    reads, and both are reported on stderr and in the --json envelope.
    """

    def __init__(self, code: int, stage: str, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.stage = stage
        self.reason = reason

    @property
    def line(self) -> str:
        return "ABORT: " + self.reason


class Completed:
    """A child's result. `timed_out` is its own field so a caller can never read a killed run's
    empty output as a clean pass."""

    def __init__(self, argv: list[str], returncode: int, stdout: str, stderr: str,
                 timed_out: bool = False) -> None:
        self.argv = argv
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out

    @property
    def output(self) -> str:
        return self.stdout + self.stderr

    @property
    def tail(self) -> str:
        """The retired `$output[-1]` tail that every refusal message ends with."""
        lines = [line.strip() for line in self.output.splitlines()]
        for line in reversed(lines):
            if line:
                return line
        return "no output"


def is_json_int(value: object) -> bool:
    """PowerShell's `-is [int]` is False for a bool; Python's isinstance(True, int) is True."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_string_array(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def is_timestamp(value: object) -> bool:
    """`[DateTimeOffset]::TryParse` in the PowerShell; a timezone-aware ISO-8601 string here, which
    is also what `merge-lanes.py` requires -- so accept -> merge speaks one format."""
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def test_failed_summary(summary: str) -> bool:
    """accept-lane.ps1:50-61, ported branch for branch.

    A `Failed: 0` count STOPS the scan: the retired function returned `$false` from inside the
    count branch, so only a bare `Failed:` word reaches the final test.
    """
    if FAILED_MARKER_RE.search(summary):
        return True
    if re.search(r"Build FAILED|Test Run Failed\.", summary, re.IGNORECASE):
        return True
    counts = FAILED_COUNT_RE.findall(summary)
    if counts:
        return any(int(count) > 0 for count in counts)
    return BARE_FAILED_RE.search(summary) is not None


def test_failed_output(text: str) -> bool:
    """accept-lane.ps1:63-68 -- any single LINE whose summary test fires."""
    return any(test_failed_summary(line) for line in re.split(r"\r?\n", text))


def dedupe_case_insensitive(values: list[str]) -> list[str]:
    """`Sort-Object -Unique` is case-insensitive and keeps the first occurrence."""
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def run(argv: list[str], *, stage: str, timeout: float, cwd: Path | None = None,
        check: bool = True) -> Completed:
    """Run a child with a HARD timeout. On expiry, kill its whole tree and refuse by name."""
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
    except subprocess.TimeoutExpired:
        _kill_tree(proc.pid)
        try:
            out, err = proc.communicate(timeout=BUDGETS["kill_grace"])
        except subprocess.TimeoutExpired:
            out, err = "", ""
        raise Refusal(9, stage, f"{Path(argv[0]).name} exceeded its {timeout:.0f}s budget "
                                f"and was killed (pid {proc.pid})") from None
    result = Completed(argv, proc.returncode, out or "", err or "")
    if check and result.returncode != 0:
        raise Refusal(9, stage, f"{Path(argv[0]).name} exited {result.returncode}: {result.tail}")
    return result


def git(repo: Path, *args: str, stage: str = "git", check: bool = False) -> Completed:
    """Every git call names its repository explicitly and runs under the git budget."""
    return run(["git", "-C", str(repo), *args], stage=stage, timeout=BUDGETS["git"], check=check)


def git_rev_parse(repo: Path, *args: str) -> tuple[str | None, int]:
    """`git rev-parse` as the retired script read it: the last non-empty line, trimmed, or None.

    The value is returned AS GIT WROTE IT. The retired script lowercased its SHA reads and left
    its `--abbrev-ref` reads alone, because the detached-HEAD proof compares against the literal
    `HEAD` and is case-SENSITIVE. Lowercasing both here made every review checkout read as branch
    'head' and aborted every acceptance.
    """
    result = git(repo, "rev-parse", *args)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None, result.returncode
    return lines[-1], result.returncode


def git_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return git(repo, "merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def integration_ancestry_error(repo: Path, integration: str, reviewed_sha: str) -> str | None:
    """accept-lane.ps1:70-92. Returns the refusal text, or None when the reviewed SHA is provably
    integrated. A branch that does not resolve to a FULL commit SHA is a refusal, not a pass."""
    integration_sha, code = git_rev_parse(repo, "--verify", f"refs/heads/{integration}^{{commit}}")
    integration_sha = (integration_sha or "").lower()
    if code != 0 or not SHA_RE.fullmatch(integration_sha):
        return f"integration branch '{integration}' does not resolve to a full commit SHA"
    if not git_is_ancestor(repo, integration_sha, reviewed_sha):
        return (f"reviewed SHA '{reviewed_sha}' does not descend from current integration branch "
                f"'{integration}' at {integration_sha}")
    return None


def validate_evidence(path: Path, expected_lane: str, expected_sha: str,
                      require_green: bool = False) -> str | None:
    """accept-lane.ps1:94-229 -- the whole schema-version-2 validator.

    Returns the refusal text, or None. The ORDER is the contract: the first defect decides the
    message, which is what lets a test assert on a specific one.
    """
    if not path.is_file():
        return f"missing evidence file: {path}"
    try:
        artifact = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return f"malformed evidence JSON: {exc}"
    if not isinstance(artifact, dict):
        return "malformed evidence: root is not an object"
    if not is_json_int(artifact.get("schemaVersion")) or artifact.get("schemaVersion") != 2:
        return "malformed evidence: schemaVersion must be integer 2"
    lane = artifact.get("lane")
    if not isinstance(lane, str) or lane != expected_lane:
        return f"evidence lane mismatch: expected '{expected_lane}', got '{lane}'"
    sha = artifact.get("sha")
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        return "malformed evidence: sha must be a full 40-character commit SHA"
    if sha.lower() != expected_sha:
        return f"evidence SHA mismatch: expected '{expected_sha}', got '{sha}'"
    expected = artifact.get("expectedSha")
    if (not isinstance(expected, str) or not SHA_RE.fullmatch(expected)
            or expected.lower() != expected_sha):
        return "malformed evidence: expectedSha does not match the reviewed SHA"
    short = artifact.get("shortSha")
    if not isinstance(short, str) or short != expected_sha[:8]:
        return "malformed evidence: shortSha does not match the reviewed SHA"
    if artifact.get("when") is None:
        return "malformed evidence: when must be a timestamp"
    if not is_timestamp(artifact.get("when")):
        return "malformed evidence: when is not a valid timestamp"
    verdict = artifact.get("verdict")
    if not isinstance(verdict, str) or verdict not in ACCEPTANCE_VERDICTS:
        return "malformed evidence: verdict is outside the acceptance vocabulary"
    if not isinstance(artifact.get("contendedTree"), bool):
        return "malformed evidence: contendedTree must be boolean"
    log_dir = artifact.get("logDir")
    if not isinstance(log_dir, str) or not log_dir.strip():
        return "malformed evidence: logDir must be a non-empty string"
    attribution = artifact.get("attribution")
    if not isinstance(attribution, dict):
        return "malformed evidence: attribution must be an object"
    for prop in ("knownRedMatched", "newUnregistered", "unattributed"):
        if not is_json_int(attribution.get(prop)) or attribution.get(prop) < 0:
            return f"malformed evidence: attribution.{prop} must be a non-negative integer"
    checks = artifact.get("checks")
    if not isinstance(checks, list):
        return "malformed evidence: checks must be an array"
    if not checks:
        return "malformed evidence: checks must not be empty"

    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            return "malformed evidence: check entry is not an object"
        for prop in REQUIRED_CHECK_KEYS:
            if prop not in check:
                return f"malformed evidence: check is missing '{prop}'"
        name = check["check"]
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            return f"malformed evidence: invalid check name '{name}'"
        if name in seen:
            return f"malformed evidence: duplicate check '{name}'"
        seen.add(name)
        if not is_json_int(check["exit"]):
            return f"malformed evidence: exit must be an integer for check '{name}'"
        if not is_json_int(check["seconds"]) or check["seconds"] < 0:
            return f"malformed evidence: seconds must be a non-negative integer for check '{name}'"
        if not isinstance(check["summary"], str):
            return f"malformed evidence: summary must be text for check '{name}'"
        for prop in CHECK_RESULT_ARRAYS:
            if not is_string_array(check[prop]):
                return f"malformed evidence: {prop} must be a string array for check '{name}'"
        if not isinstance(check["log"], str) or not check["log"].strip():
            return f"malformed evidence: empty log path for check '{name}'"

    if require_green:
        if verdict != "GREEN":
            return f"evidence verdict is '{verdict}', not GREEN"
        for check in checks:
            name = check["check"]
            if check["exit"] != 0:
                return f"evidence contains a non-zero check '{name}'"
            if test_failed_summary(check["summary"]):
                return f"evidence contains a failed summary for check '{name}'"
            for prop in CHECK_RESULT_ARRAYS:
                if check[prop]:
                    return f"evidence contains red/error details in {prop} for check '{name}'"
        if (attribution["knownRedMatched"] != 0 or attribution["newUnregistered"] != 0
                or attribution["unattributed"] != 0):
            return "evidence attribution is not clean"
    return None


def parse_check_specs(raw: list[str]) -> list[dict[str, str]]:
    """accept-lane.ps1:244-263. The COMPLETE check set is validated before any log or worktree is
    created, so a malformed set never leaves a half-built acceptance behind."""
    parsed: list[dict[str, str]] = []
    seen: set[str] = set()
    for text in raw:
        parts = text.split("|||", 1)
        if len(parts) != 2 or not parts[1].strip():
            raise Refusal(2, "check_specs", f"check '{text}' is malformed -- expected "
                                           "'name|||command' with a non-empty command.")
        name, command = parts[0].strip(), parts[1].strip()
        if not NAME_RE.fullmatch(name):
            raise Refusal(2, "check_specs", f"check name '{name}' is malformed -- use letters, "
                                           "digits, '.', '_' or '-'.")
        if name in seen:
            raise Refusal(2, "check_specs", f"duplicate check name '{name}'.")
        seen.add(name)
        parsed.append({"name": name, "command": command})
    if not parsed:
        raise Refusal(2, "check_specs", "at least one schema-valid check is required; an empty "
                                       "check set cannot be accepted.")
    return parsed


def contended_probes(repo: Path) -> list[str]:
    """accept-lane.ps1:326-344. A test binary another process holds exclusively is contention."""
    locked: list[str] = []
    for relative in CONTENDED_PROBES:
        target = repo / relative
        if not target.is_file():
            continue
        try:
            with open(target, "r+b"):  # noqa: SIM115 - an exclusivity probe, closed immediately
                pass
        except OSError:
            locked.append(relative)
    return locked


def review_checkout_error(repo: Path, expected_sha: str) -> str | None:
    """accept-lane.ps1:355-379. Clean AND detached AND exactly at the reviewed SHA."""
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        return f"git status failed in review checkout: {status.tail}"
    dirty = [line for line in status.stdout.splitlines() if line.strip()]
    if dirty:
        return "review checkout is dirty: " + " ;; ".join(dirty[:5])
    head, code = git_rev_parse(repo, "HEAD")
    if code != 0 or head != expected_sha:
        return f"review checkout HEAD '{head}' does not exactly match expected SHA '{expected_sha}'"
    branch, code = git_rev_parse(repo, "--abbrev-ref", "HEAD")
    if code != 0 or branch != "HEAD":
        return f"review checkout is not detached at the reviewed SHA (branch '{branch}')"
    return None


def resolve_cmdc_agent(explicit: str, environ: dict[str, str], home: Path) -> Path:
    """--cmdc-agent, then FUSIONRPG_CMDC_AGENT, then the home-relative default.

    No drive letter and no user path is written into this file, and a missing result is a NAMED
    refusal -- never a guess and never a raw interpreter error.
    """
    if explicit:
        candidate = Path(explicit)
    elif environ.get("FUSIONRPG_CMDC_AGENT"):
        candidate = Path(environ["FUSIONRPG_CMDC_AGENT"])
    else:
        candidate = home / ".claude" / "skills" / "cmdc-subagent" / "scripts" / "cmdc_agent.py"
    if not candidate.is_file():
        raise Refusal(9, "cmdc_agent", f"cmdc review tool is missing: {candidate}")
    return candidate


def run_check_command(command: str, cwd: Path, timeout: float) -> Completed:
    """One `name|||command`, exactly as the retired script ran it: a command line handed to the
    platform shell, in the pinned review checkout, under a hard budget.

    A timeout is NOT an abort: the check is recorded as failed with a named error, so the artefact
    is still written and the manager can read WHY. It can never read as a pass.
    """
    argv = (["cmd.exe", "/d", "/s", "/c", command] if os.name == "nt"
            else ["/bin/sh", "-c", command])
    proc = subprocess.Popen(  # noqa: S603 - a command LINE is this check's contract
        argv, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
    try:
        out, err = proc.communicate(timeout=timeout)
        return Completed(argv, proc.returncode, out or "", err or "")
    except subprocess.TimeoutExpired as expired:
        _kill_tree(proc.pid)
        try:
            out, err = proc.communicate(timeout=BUDGETS["kill_grace"])
        except subprocess.TimeoutExpired:
            out, err = "", ""
        return Completed(argv, 1, (expired.stdout or "") + (out or ""),
                         (expired.stderr or "") + (err or ""), timed_out=True)


def match_known_red(known_red: list[object], failure: str) -> str | None:
    """accept-lane.ps1:449-455. A registry row without a usable `test` cannot match, so its debt
    reads as NEW red -- the fail-closed direction, so the retired behaviour is kept."""
    for entry in known_red:
        if not isinstance(entry, dict):
            continue
        test = entry.get("test")
        if not isinstance(test, str) or not test:
            continue
        if test == failure or test.endswith(failure) or failure.endswith(test) or test in failure:
            debt = entry.get("debt")
            return str(debt) if debt is not None else ""
    return None


def run_one_check(spec: dict[str, str], review_path: Path, log_dir: Path, known_red: list[object],
                  check_timeout: float, transcript) -> dict[str, object]:
    """accept-lane.ps1:412-493 for ONE check: run it, log it, parse it, attribute it."""
    name, command = spec["name"], spec["command"]
    log = log_dir / f"{name}.log"
    transcript(f"=== {name} ===")
    transcript(f"> {command}")
    started = time.monotonic()
    result = run_check_command(command, review_path, check_timeout)
    seconds = int(time.monotonic() - started)
    try:
        log.write_text(result.output, encoding="utf-8")
        text = ANSI_RE.sub("", log.read_text(encoding="utf-8"))
    except OSError as exc:
        raise Refusal(9, "check_log", f"cannot write the log for check '{name}': {exc}") from exc

    summary = " ;; ".join(match.strip() for match in SUMMARY_RE.findall(text))
    if test_failed_output(text):
        if not summary.strip():
            summary = "Failed! - failed output detected"
        elif not FAILED_MARKER_RE.search(summary):
            summary += " ;; Failed! - failed output detected"

    failed = dedupe_case_insensitive(FAILED_TEST_RE.findall(text))
    errors = [line.strip() for line in COMPILER_ERROR_RE.findall(text)][:5]
    if result.timed_out:
        errors.insert(0, f"check '{name}' exceeded its {check_timeout:.0f}s budget and was killed")

    known: list[str] = []
    new: list[str] = []
    for failure in failed:
        hit = match_known_red(known_red, failure)
        if hit is None:
            new.append(failure)
        else:
            known.append(f"{failure}  [registered: {hit}]")
    flakes = [failure for failure in failed
              if any(family in failure for family in FLAKE_FAMILIES)]

    if result.returncode == 0 and seconds == 0 and not text.strip():
        raise Refusal(2, "check_execution",
                      f"check '{name}' returned exit 0 in 0s with no output; it did not run.")

    transcript(f"exit={result.returncode}  {seconds}s")
    if summary:
        transcript(summary)
    for heading, items in (
        ("FAILED TESTS (registered debt):", known),
        ("FAILED TESTS (NEW - no owning registration):", new),
        ("COMPILER ERRORS:", errors),
        ("FLAKE-SUSPECT (load-fragile Guard families; rerun alone before routing):", flakes),
    ):
        if items:
            transcript(heading)
            for item in items:
                transcript(f"  - {item}")

    return {
        "check": name,
        "exit": result.returncode,
        "seconds": seconds,
        "summary": summary,
        "failedTests": failed,
        "knownRedTests": known,
        "newRedTests": new,
        "flakeSuspectTests": flakes,
        "errors": errors,
        "log": str(log),
    }


def decide_verdict(results: list[dict[str, object]]) -> tuple[str, str, dict[str, int]]:
    """accept-lane.ps1:500-523 -- the verdict ladder, and the attribution counts the artefact
    records. The flattening of `newRedTests` and `errors` spans ALL checks, not only the red ones,
    exactly as the retired script did."""
    red = [check for check in results
           if check["exit"] != 0 or check["failedTests"] or check["errors"]
           or test_failed_summary(check["summary"])]
    new_reds = [item for check in results for item in check["newRedTests"] if item]
    compiler_errors = [item for check in results for item in check["errors"] if item]
    unattributed = [check for check in red
                    if not check["failedTests"] and not check["errors"]]
    known_count = sum(1 for check in results for item in check["knownRedTests"] if item)

    if not red:
        verdict = "GREEN"
    elif unattributed:
        verdict = "UNATTRIBUTED"
    elif compiler_errors:
        verdict = "RED"
    elif not new_reds:
        verdict = "RED-KNOWN"
    else:
        verdict = "RED"

    if verdict == "GREEN":
        summary = "GREEN"
    elif verdict == "UNATTRIBUTED":
        summary = (f"UNATTRIBUTED ({len(red)} red check(s); {len(unattributed)} with no parsed "
                   "failure)")
    elif verdict == "RED-KNOWN":
        summary = (f"RED-KNOWN ({len(red)} check(s), {known_count} registered-debt failure(s) "
                   "matched)")
    else:
        summary = (f"RED ({len(red)} check(s), {len(new_reds) + len(compiler_errors)} "
                   "unregistered/compiler failure(s))")
    attribution = {
        "knownRedMatched": known_count,
        "newUnregistered": len(new_reds) + len(compiler_errors),
        "unattributed": len(unattributed),
    }
    return verdict, summary, attribution


def read_known_red(repo: Path) -> list[object]:
    """Registered debt is attribution, never a green verdict (accept-lane.ps1:313-323)."""
    path = repo / "scripts" / "verification-boundaries.v1.json"
    if not path.is_file():
        return []
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise Refusal(2, "known_red",
                      f"cannot parse registered known-red evidence: {exc}") from exc
    if not isinstance(parsed, dict):
        raise Refusal(2, "known_red",
                      "cannot parse registered known-red evidence: root is not an object")
    known_red = parsed.get("knownRed", [])
    return known_red if isinstance(known_red, list) else []


def merge_into_integration(repo: Path, lane: str, head: str, short_sha: str, merge_into: str,
                           verdict: str, artifact_path: Path, own_artifact: str,
                           transcript) -> int:
    """accept-lane.ps1:555-601.

    Every refusal sets exit 1 and leaves the tree untouched. The merge is the only mutation, and a
    conflict is aborted so the tree is left clean.
    """
    evidence_error = validate_evidence(artifact_path, lane, head, require_green=True)
    branch, _ = git_rev_parse(repo, "--abbrev-ref", "HEAD")
    dirty: list[str] = []
    for line in git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout.splitlines():
        entry = re.sub(r"^..\s+", "", line).replace("\\", "/")
        if entry and entry != own_artifact:
            dirty.append(entry)
    staged = git(repo, "diff", "--cached", "--name-only", "--", own_artifact)
    staged_artifact = [line for line in staged.stdout.splitlines() if line.strip()]
    ancestry_error = integration_ancestry_error(repo, merge_into, head)

    if evidence_error:
        transcript(f"MERGE REFUSED: {evidence_error}")
        return 1
    if verdict != "GREEN":
        transcript(f"MERGE REFUSED: checks are {verdict}.")
        return 1
    if ancestry_error:
        transcript(f"MERGE REFUSED: {ancestry_error}")
        return 1
    if branch != merge_into:
        transcript(f"MERGE REFUSED: on {branch}, not {merge_into}.")
        return 1
    if dirty:
        transcript(f"MERGE REFUSED: {len(dirty)} dirty path(s) in the manager tree.")
        return 1
    if staged.returncode != 0:
        transcript("MERGE REFUSED: could not inspect staged acceptance evidence "
                   f"(git exit {staged.returncode}).")
        return 1
    if staged_artifact:
        transcript("MERGE REFUSED: acceptance evidence is staged; commit or unstage it before "
                   "merging.")
        return 1

    merge = git(repo, "merge", "--no-ff", head, "-m",
                f"merge(lane): {lane} at {short_sha} (accepted full SHA; schema-valid GREEN "
                "evidence)", stage="merge", check=False)
    if merge.returncode != 0:
        for line in merge.output.splitlines():
            transcript(line)
        transcript("MERGE CONFLICT: aborting; the tree is left clean.")
        git(repo, "merge", "--abort", stage="merge")
        return 1
    transcript(f"MERGED {head} into {merge_into}")
    return 0


class Config:
    """Everything resolved once, up front, and readable without touching a process CWD."""

    def __init__(self, args: argparse.Namespace) -> None:
        repo_input = args.repo if args.repo else Path(__file__).resolve().parent.parent.parent
        try:
            self.repo = Path(repo_input).resolve(strict=True)
        except OSError as exc:
            raise Refusal(9, "repo", f"repository root cannot be resolved: {exc}") from exc
        self.lane = args.lane
        self.expect_sha = args.expect_sha.lower()
        self.merge_into = args.merge_into
        self.merge = args.merge
        self.allow_contended = args.allow_contended
        self.check_timeout = args.check_timeout
        self.log_root = Path(args.log_root) if args.log_root else Path(tempfile.gettempdir()) \
            / "cmdc-acceptance"
        self.cmdc_agent = resolve_cmdc_agent(args.cmdc_agent, os.environ, Path.home())


def run_acceptance(config: Config, args: argparse.Namespace, transcript) -> tuple[int, dict]:
    """The whole harness, in the order documented at the top of this file."""
    repo, lane, expect_sha = config.repo, config.lane, config.expect_sha

    # 1. The complete check set, validated before anything at all is created.
    checks = parse_check_specs(args.check)

    if config.merge and config.merge_into != INTEGRATION_BRANCH:
        raise Refusal(9, "merge_target", f"--merge-into must be '{INTEGRATION_BRANCH}'; refusing a "
                                         f"direct merge into '{config.merge_into}'.")

    # 2. The full expected SHA, resolved in this repository before any lane checkout is trusted.
    resolved, code = git_rev_parse(repo, "--verify", f"{expect_sha}^{{commit}}")
    resolved = (resolved or "").lower()
    if code != 0 or not SHA_RE.fullmatch(resolved) or resolved != expect_sha:
        raise Refusal(9, "expect_sha", f"expected SHA '{expect_sha}' does not resolve to the "
                                      f"requested commit in {repo}.")

    # 3. Existing evidence for this lane+SHA must be valid, or it is refused as stale/malformed.
    short_sha = expect_sha[:8]
    artifact_dir = repo / ".claude" / "cmdc-agents" / "acceptance"
    artifact_path = artifact_dir / f"{lane}-{short_sha}.json"
    if artifact_path.is_file():
        existing_error = validate_evidence(artifact_path, lane, expect_sha)
        if existing_error:
            raise Refusal(2, "existing_evidence",
                          f"existing acceptance evidence is stale or malformed: {existing_error}")

    # 4. Bind the reviewed commit to the lane's history. The lane may advance after review, so
    #    ancestry -- not equality with the mutable tip -- is the acceptance boundary.
    lane_tip, code = git_rev_parse(repo, "--verify", f"refs/heads/cmdc/{lane}^{{commit}}")
    lane_tip = (lane_tip or "").lower()
    if code != 0 or not SHA_RE.fullmatch(lane_tip):
        raise Refusal(9, "lane_branch",
                      f"lane branch 'cmdc/{lane}' does not resolve to a full commit SHA.")
    if not git_is_ancestor(repo, expect_sha, lane_tip):
        raise Refusal(9, "lane_ancestry", f"expected SHA '{expect_sha}' is not reachable from "
                                          f"lane branch 'cmdc/{lane}' (tip {lane_tip}).")
    if config.merge:
        error = integration_ancestry_error(repo, config.merge_into, expect_sha)
        if error:
            raise Refusal(9, "integration_ancestry", error)

    known_red = read_known_red(repo)
    transcript(f"knownRed registered: {len(known_red)} "
               f"{'entry' if len(known_red) == 1 else 'entries'}")

    # 5. A held test binary means this tree is not an isolated evidence source.
    contended = contended_probes(repo)
    if contended:
        transcript("CONTENTION: another test process already holds this tree:")
        for relative in contended:
            transcript(f"  - {relative}")
        if not config.allow_contended:
            raise Refusal(9, "contention", "refusing to accept from a contended tree; rerun when "
                                          "the other suite finishes.")
        transcript("  --allow-contended given: continuing; every failure still requires an "
                   "isolated rerun.")

    # 6. Create/sync the review checkout, then PIN it to the immutable full SHA.
    review = run([sys.executable, str(config.cmdc_agent), "--repo", str(repo), "review",
                  "--id", lane], stage="review_checkout", timeout=BUDGETS["review"], check=False)
    if review.returncode != 0:
        raise Refusal(9, "review_checkout", f"review checkout command failed "
                                            f"(exit {review.returncode}): {review.tail}")
    review_path = repo / ".claude" / "worktrees" / f"cmdc-review-{lane}"
    if not (review_path / ".git").exists():
        raise Refusal(9, "review_checkout", f"review checkout missing at {review_path}.")
    checkout = git(review_path, "checkout", "--detach", expect_sha, stage="review_pin", check=False)
    if checkout.returncode != 0:
        raise Refusal(9, "review_pin", f"cannot check out the reviewed SHA {expect_sha} in the "
                                       f"review worktree: {checkout.tail}")
    head = (git_rev_parse(review_path, "HEAD")[0] or "").lower()
    transcript(f"LANE={lane}  REVIEW_HEAD={head}")
    if head != expect_sha:
        raise Refusal(9, "review_pin", f"review head {head} does not exactly match expected SHA "
                                       f"{expect_sha}.")
    error = review_checkout_error(review_path, expect_sha)
    if error:
        raise Refusal(9, "review_state", error)

    # 7. The log directory, created or refused by name. The retired script never checked, and a
    #    silent failure there emptied every check log.
    now = datetime.now()
    log_dir = config.log_root / f"accept-{lane}-{now.strftime('%Y%m%d-%H%M%S')}-" \
                                f"{now.microsecond // 1000:03d}"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise Refusal(9, "log_dir", f"cannot create the acceptance log directory: {exc}") from exc

    # 8. Every check, with the review checkout re-proved before each one and once more after all.
    results: list[dict[str, object]] = []
    for spec in checks:
        error = review_checkout_error(review_path, expect_sha)
        if error:
            raise Refusal(9, "review_state", f"review checkout changed before check "
                                            f"'{spec['name']}': {error}")
        results.append(run_one_check(spec, review_path, log_dir, known_red,
                                     config.check_timeout, transcript))
    error = review_checkout_error(review_path, expect_sha)
    if error:
        raise Refusal(9, "review_state", f"review checkout changed after checks: {error}")

    # 9. The verdict, the artefact, then the SAME validator over the file just written.
    verdict, verdict_summary, attribution = decide_verdict(results)
    artifact = {
        "schemaVersion": 2,
        "lane": lane,
        "sha": head,
        "shortSha": short_sha,
        "expectedSha": expect_sha,
        "when": utc_now(),
        "verdict": verdict,
        "attribution": attribution,
        "contendedTree": bool(contended),
        "logDir": str(log_dir),
        "checks": results,
    }
    try:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    except OSError as exc:
        raise Refusal(9, "artifact_write", f"cannot write the acceptance artefact: {exc}") from exc
    artifact_error = validate_evidence(artifact_path, lane, expect_sha)
    if artifact_error:
        artifact_path.unlink(missing_ok=True)
        raise Refusal(2, "artifact_validate",
                      f"generated acceptance evidence is invalid: {artifact_error}")
    transcript(f"VERDICT: {verdict_summary}")
    transcript(f"ARTEFACT: .claude/cmdc-agents/acceptance/{lane}-{short_sha}.json")

    exit_code = 0 if verdict == "GREEN" else 1

    # 10. --merge, re-validating the artefact with the GREEN requirement.
    if config.merge:
        own_artifact = f".claude/cmdc-agents/acceptance/{lane}-{short_sha}.json"
        exit_code = merge_into_integration(repo, lane, head, short_sha, config.merge_into, verdict,
                                           artifact_path, own_artifact, transcript)
    else:
        transcript("MERGE: not requested (pass --merge). Artefact above is the acceptance record.")

    return exit_code, {
        "verdict": verdict,
        "verdictSummary": verdict_summary,
        "artifact": artifact_path.as_posix(),
        "attribution": attribution,
        "contendedTree": bool(contended),
        "logDir": str(log_dir),
        "checks": results,
        "mergeRequested": config.merge,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="accept_lane.py",
        description="Run and record fail-closed acceptance for one manager lane at an immutable "
                    "full SHA. The review checkout is pinned to the expected commit before any "
                    "check runs, and a mismatched tree aborts.")
    parser.add_argument("--expect-sha", required=True, metavar="<40-hex>",
                        help="the reviewed commit, as a full 40-character SHA")
    parser.add_argument("--lane", required=True,
                        help="lane name; the branch under review is cmdc/<lane>")
    parser.add_argument("--check", action="append", default=[], metavar="'name|||command'",
                        help="repeatable; at least one schema-valid check is required")
    parser.add_argument("--repo", default="",
                        help="repository root (default: the checkout this script lives in)")
    parser.add_argument("--merge-into", default=INTEGRATION_BRANCH,
                        help=f"integration branch; must be {INTEGRATION_BRANCH}")
    parser.add_argument("--merge", action="store_true",
                        help="merge the accepted SHA once exact GREEN evidence exists")
    parser.add_argument("--allow-contended", action="store_true",
                        help="continue when another test process holds this tree")
    parser.add_argument("--cmdc-agent", default="",
                        help="the review-checkout helper (default: $FUSIONRPG_CMDC_AGENT, then "
                             "~/.claude/skills/cmdc-subagent/scripts/cmdc_agent.py)")
    parser.add_argument("--log-root", default="",
                        help="where the per-check logs are written (default: <temp>/"
                             "cmdc-acceptance)")
    parser.add_argument("--check-timeout", type=float, default=BUDGETS["check"],
                        help=f"hard budget per check, seconds (default {BUDGETS['check']:.0f})")
    parser.add_argument("--json", action="store_true",
                        help="print one machine-readable envelope on stdout; the transcript moves "
                             "to stderr")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.check_timeout <= 0:
        print("accept_lane: --check-timeout must be a positive number of seconds", file=sys.stderr)
        return 2

    transcript_stream = sys.stderr if args.json else sys.stdout

    def transcript(message: str = "") -> None:
        print(message, file=transcript_stream, flush=True)

    envelope: dict[str, object] = {
        "tool": "accept_lane",
        "lane": args.lane,
        "expectSha": args.expect_sha.lower(),
        "mergeRequested": args.merge,
        "ok": False,
        "exitCode": 2,
        "stage": None,
        "refusal": None,
        "verdict": None,
        "verdictSummary": None,
        "artifact": None,
    }
    try:
        config = Config(args)
        exit_code, detail = run_acceptance(config, args, transcript)
        envelope.update(detail)
        envelope["ok"] = exit_code == 0
        envelope["exitCode"] = exit_code
        envelope["stage"] = "complete"
    except Refusal as refusal:
        print(refusal.line, file=transcript_stream, flush=True)
        print(f"accept_lane refused at stage '{refusal.stage}' with exit {refusal.code}",
              file=sys.stderr, flush=True)
        envelope["exitCode"] = refusal.code
        envelope["stage"] = refusal.stage
        envelope["refusal"] = refusal.reason
        if args.json:
            print(json.dumps(envelope, indent=2))
        return refusal.code

    if args.json:
        print(json.dumps(envelope, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
