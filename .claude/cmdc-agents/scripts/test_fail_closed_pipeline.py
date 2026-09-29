#!/usr/bin/env python3
"""Focused fail-closed regressions for the manager merge/acceptance plane.

These tests deliberately exercise the repository's real Python entry points. Only the repositories and
command doubles they operate on live in temporary directories.

WHY THIS FILE USED TO SHELL `pwsh`
---------------------------------
It drove `post-merge-check.ps1` and `accept-lane.ps1` through an `& script -Flag 'value'` command
string, which meant a PowerShell quoting layer (`ps_quote`/`ps_array`, 103 call sites) existed only to
build that string. The Python twins take an ARGV LIST, so that layer is gone and two builders produce
lists directly.

A `pwsh -Command` string also RE-QUOTES every value, so a path containing a quote was previously a
silent behaviour change. An argv list cannot have that failure, which is the concrete reason the
migration is worth doing rather than cosmetic.

The twins are unit-tested by `test_post_merge_check.py` and `test_accept_lane.py`. Those suites passing
is NOT what this file checks, and that distinction is the whole point: it checks the INTEGRATION
contract - the fail-closed plane as a whole - and for a long time it checked that against the
PowerShell while the twins sat beside it, unit-tested and unexercised. That is a port which reads
green while the live path is untouched. `ThePipelineEntryPointsArePython` now fails if a `.ps1`
reappears.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".claude" / "cmdc-agents" / "scripts"
POST_MERGE = SCRIPTS / "post_merge_check.py"
ACCEPT_LANE = SCRIPTS / "accept_lane.py"
MERGE_LANES = SCRIPTS / "merge-lanes.py"

# Every child here is bounded. A test that can hang is a defect, and this budget is the TOOL's, not
# dotnet's -- the original had no such separation.
CHILD_TIMEOUT = 45


def process_environment(overrides: dict[str, str] | None = None) -> dict[str, str]:
    environment = os.environ.copy()
    if overrides:
        environment.update({key: str(value) for key, value in overrides.items()})
    return environment


def run_tool(
    script: Path,
    arguments: list[str],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """One Python entry point, one argv list, one hard budget.

    `sys.executable` rather than a bare `python`: the test must exercise the interpreter it is running
    under, and a `python` missing from PATH fails as a confusing "not found" deep inside a gate
    assertion rather than as an obvious launch error.
    """
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=CHILD_TIMEOUT,
        env=process_environment(env),
    )


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def commit_path(root: Path, path: str, message: str) -> None:
    git(root, "add", path)
    git(root, "commit", "-m", message)


def init_repo(path: Path, branch: str = "features/mega-merge") -> str:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init")
    git(path, "config", "user.name", "Test User")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "checkout", "-b", branch)
    (path / "base.txt").write_text("base\n", encoding="utf-8")
    (path / ".gitignore").write_text(
        ".claude/worktrees/\n"
        "fake_cmdc.py\n"
        "dotnet.cmd\n"
        "fake_dotnet.py\n"
        "fake-*.json\n"
        "legal-game/\n"
        "logs/\n",
        encoding="utf-8",
    )
    git(path, "add", "base.txt", ".gitignore")
    git(path, "commit", "-m", "base")
    return git(path, "rev-parse", "HEAD")


def make_unrelated_lane_repo(path: Path) -> tuple[str, str]:
    base = init_repo(path)
    git(path, "checkout", "--orphan", "cmdc/unrelated")
    git(path, "rm", "-rf", ".")
    (path / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
    git(path, "add", "unrelated.txt")
    git(path, "commit", "-m", "unrelated lane work")
    lane_sha = git(path, "rev-parse", "HEAD")
    git(path, "checkout", "features/mega-merge")
    return base, lane_sha


def fake_dotnet(path: Path) -> Path:
    """A dotnet stand-in the twins can launch DIRECTLY.

    The PowerShell form could not be kept: `subprocess` cannot launch a `.ps1` without a shell, and
    handing the twin a shell would put back the quoting surface the argv migration just removed. So
    the double is a two-line `.cmd` shim over a Python implementation - the JSON parsing stays in
    Python, where it is reliable, and the shim exists only because CreateProcess needs an executable
    extension. It lives in a TEMP fixture and is never tracked, so the repo's ban on tracked
    `.bat`/`.cmd` TOOLS is not in scope here.

    Behaviour matches the original: classify by argv (`build`; else a target naming
    `FusionRpg.Guard.Tests`; else `test`), read `fake-<kind>.json` from the CWD if present, print its
    `output` lines, exit with its `exit`. A missing or malformed state file falls back to the default
    GREEN, because a double that raised would be indistinguishable from the gate under test failing.
    """
    path = path.with_suffix(".cmd")
    # Named for the IGNORE list, not for `path`: the gate refuses a dirty checkout, so an untracked
    # shim aborts every test before the behaviour under test is reached. `dotnet.py` beside
    # `dotnet.cmd` was invisible to the `.gitignore` entry and took 21 tests down with it.
    shim = path.parent / "fake_dotnet.py"
    shim.write_text(
        textwrap.dedent(
            """
            import json
            import sys
            from pathlib import Path

            mode = sys.argv[1] if len(sys.argv) > 1 else ''
            target = sys.argv[2] if len(sys.argv) > 2 else ''
            if mode == 'build':
                kind = 'build'
            elif 'FusionRpg.Guard.Tests' in target:
                kind = 'guard'
            else:
                kind = 'test'
            default_output = ['Build succeeded.'] if kind == 'build' else [
                'Passed!  - Failed: 0, Passed: 1']
            output, code = default_output, 0
            state = Path('fake-%s.json' % kind)
            if state.is_file():
                try:
                    payload = json.loads(state.read_text(encoding='utf-8'))
                    output = [str(line) for line in payload.get('output', default_output)]
                    code = int(payload.get('exit', 0))
                except (ValueError, OSError, TypeError):
                    output, code = default_output, 0
            for line in output:
                print(line)
            sys.exit(code)
            """
        ).lstrip(),
        encoding="utf-8",
    )
    path.write_text(f'@echo off\r\n"{sys.executable}" "%~dp0fake_dotnet.py" %*\r\n', encoding="utf-8")
    return path


def set_fake_dotnet_state(root: Path, kind: str, output: list[str], exit_code: int) -> None:
    (root / f"fake-{kind}.json").write_text(
        json.dumps({"output": output, "exit": exit_code}),
        encoding="utf-8",
    )


def legal_game_environment(root: Path) -> dict[str, str]:
    game = root / "legal-game"
    required = [
        game / "BepInEx" / "core" / "BepInEx.Core.dll",
        game / "BepInEx" / "interop" / "Assembly-CSharp.dll",
        game / "MelonLoader" / "net6" / "MelonLoader.dll",
        game / "MelonLoader" / "Il2CppAssemblies" / "Assembly-CSharp.dll",
    ]
    for marker in required:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("fixture evidence\n", encoding="utf-8")
    return {
        "FUSIONRPG_GAME_DIR": str(game),
        "FUSIONRPG_ML_GAMEDIR": str(game),
    }


def make_post_fixture(root: Path, projects: list[str], residual: str = "FusionRpg.Core.Tests") -> None:
    init_repo(root)
    tests = root / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schemaVersion": 1,
        "residual": residual,
        "projects": [{"name": name} for name in projects],
    }
    (root / "tests" / "core-test-projects.v1.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    declared_names = [*projects]
    if residual:
        declared_names.append(residual)
    for name in declared_names:
        project = tests / name / f"{name}.csproj"
        project.parent.mkdir(parents=True, exist_ok=True)
        project.write_text("<Project />\n", encoding="utf-8")
    git(root, "add", "tests")
    git(root, "commit", "-m", "declared test surface")


def post_arguments(
    root: Path,
    dotnet: Path,
    projects: list[str] | None,
    *,
    skip_build: bool = False,
    skip_guards: bool = False,
) -> list[str]:
    """`post_merge_check.py`'s argv.

    `--test-project` is `action="append"`, so each project is its OWN `--test-project <path>`. Passing
    the list once, comma-joined, would arrive as a single project name matching nothing, and the gate
    would report the DECLARED surface green without ever running what the caller asked for. That is a
    silent narrowing, so `RepeatingATestProjectFlagIsNotACommaList` asserts it.
    """
    args = ["--repo", str(root), "--dotnet", str(dotnet)]
    if skip_build:
        args.append("--skip-build")
    if skip_guards:
        args.append("--skip-guards")
    if projects is not None:
        for project in projects:
            args += ["--test-project", project]
    return args


def accept_arguments(
    lane: str,
    *,
    repo: Path,
    expect_sha: str | None = None,
    checks: list[str] | None = None,
    cmdc: Path | None = None,
    log_root: Path | None = None,
    merge: bool = False,
    merge_into: str | None = None,
) -> list[str]:
    """`accept_lane.py`'s argv.

    `--check` is `action="append"`, so an EMPTY check list emits NO `--check` flag at all rather than
    an empty value - and that is load-bearing, because the tool refuses an empty check set and one of
    the regressions below exists to prove it. A comma-joined value would be one check named `'a,b'`,
    which is a different test entirely.
    """
    args = ["--lane", lane]
    if expect_sha is not None:
        args += ["--expect-sha", expect_sha]
    for check in checks or []:
        args += ["--check", check]
    args += ["--repo", str(repo)]
    if cmdc is not None:
        args += ["--cmdc-agent", str(cmdc)]
    if log_root is not None:
        args += ["--log-root", str(log_root)]
    if merge:
        args.append("--merge")
    if merge_into is not None:
        args += ["--merge-into", merge_into]
    return args


def make_fake_cmdc(path: Path, *, dirty_review: bool = False) -> Path:
    script = textwrap.dedent(
        """
        import subprocess
        import sys
        from pathlib import Path

        repo = Path(sys.argv[sys.argv.index('--repo') + 1])
        lane = sys.argv[sys.argv.index('--id') + 1]
        worktree = repo / '.claude' / 'worktrees' / f'cmdc-review-{lane}'
        worktree.parent.mkdir(parents=True, exist_ok=True)
        if not worktree.exists():
            subprocess.run(
                ['git', 'worktree', 'add', '--detach', str(worktree), 'HEAD'],
                cwd=repo,
                check=True,
            )
        if __DIRTY_REVIEW__:
            (worktree / 'unexpected-review-file.txt').write_text('dirty\\n', encoding='utf-8')
        """
    ).strip() + "\n"
    path.write_text(script.replace("__DIRTY_REVIEW__", repr(dirty_review)), encoding="utf-8")
    return path


def remove_worktree(repo: Path, lane: str) -> None:
    worktree = repo / ".claude" / "worktrees" / f"cmdc-review-{lane}"
    if worktree.exists():
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree)],
            cwd=repo,
            capture_output=True,
            text=True,
        )


def acceptance_artifact(
    lane: str,
    sha: str,
    *,
    verdict: str = "GREEN",
    checks: list[dict] | None = None,
) -> dict:
    return {
        "schemaVersion": 2,
        "lane": lane,
        "sha": sha,
        "shortSha": sha[:8],
        "expectedSha": sha,
        "when": "2026-09-25T00:00:00Z",
        "verdict": verdict,
        "attribution": {"knownRedMatched": 0, "newUnregistered": 0, "unattributed": 0},
        "contendedTree": False,
        "logDir": "temporary",
        "checks": checks
        if checks is not None
        else [
            {
                "check": "smoke",
                "exit": 0,
                "seconds": 1,
                "summary": "Passed!",
                "failedTests": [],
                "knownRedTests": [],
                "newRedTests": [],
                "flakeSuspectTests": [],
                "errors": [],
                "log": "temporary/smoke.log",
            }
        ],
    }


class PostMergeCheckTests(unittest.TestCase):
    def test_red_test_verdict_returns_nonzero_process_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "test", ["Failed!  - Failed: 1, Passed: 0"], 1)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("VERDICT: RED", result.stdout)

    def test_zero_exit_build_failed_summary_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "build", ["Build FAILED."], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("failed summary", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_zero_exit_guard_failed_summary_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "guard", ["Failed!  - Failed: 1, Passed: 0"], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("failed summary", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_zero_exit_test_failed_summary_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "test", ["Failed!  - Failed: 1, Passed: 0"], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("failed summary", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_zero_test_count_guard_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "guard", ["Passed!  - Failed: 0, Passed: 0, Total: 0"], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("zero", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_zero_test_count_test_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "test", ["Passed!  - Failed: 0, Passed: 0, Total: 0"], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("zero", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_build_without_success_summary_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "build", ["Build completed."], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("build-no-success-summary", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_red_build_returns_nonzero_process_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "build", ["Build FAILED."], 1)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("build: dotnet exited 1", result.stdout)
            self.assertIn("VERDICT: RED", result.stdout)

    def test_red_guard_returns_nonzero_process_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "guard", ["Failed!  - Failed: 1, Passed: 0"], 1)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("guards: dotnet test exited 1", result.stdout)
            self.assertIn("VERDICT: RED", result.stdout)

    def test_missing_guard_summary_returns_nonzero_process_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "guard", ["the command ran"], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("guards-no-summary", result.stdout.lower())

    def test_missing_test_summary_returns_nonzero_process_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(root, "test", ["the command ran"], 0)
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no-summary", result.stdout.lower())

    def test_declared_core_surface_cannot_be_silently_substituted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha", "Beta"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, ["tests/Alpha"]),
                root,
                env=legal_game_environment(root),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Alpha", result.stdout)
            self.assertIn("Beta", result.stdout)
            self.assertIn("FusionRpg.Core.Tests", result.stdout)

    def test_empty_declared_check_set_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            (root / "tests" / "core-test-projects.v1.json").write_text(
                json.dumps({"schemaVersion": 1, "residual": "", "projects": []}),
                encoding="utf-8",
            )
            commit_path(root, "tests/core-test-projects.v1.json", "empty declared surface")
            dotnet = fake_dotnet(root / "dotnet.ps1")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, [], skip_build=True, skip_guards=True),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("declared-test-manifest-empty", result.stdout)
            self.assertIn("VERDICT: RED", result.stdout)

    def test_skipping_required_build_is_blocked_not_green(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None, skip_build=True),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("VERDICT: BLOCKED", result.stdout)
            self.assertIn("build skipped", result.stdout)

    def test_one_missing_interop_environment_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env={"FUSIONRPG_GAME_DIR": str(root / "legal-game"), "FUSIONRPG_ML_GAMEDIR": ""},
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("FUSIONRPG_ML_GAMEDIR", result.stdout)
            self.assertIn("VERDICT: BLOCKED", result.stdout)

    def test_nonempty_but_invalid_legal_paths_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            missing = root / "not-a-real-game"
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env={"FUSIONRPG_GAME_DIR": str(missing), "FUSIONRPG_ML_GAMEDIR": str(missing)},
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("not-a-real-game", result.stdout)
            self.assertIn("VERDICT: BLOCKED", result.stdout)

    def test_interop_build_limitation_is_blocked_not_green(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, [])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(
                root,
                "build",
                ["[FusionRpg.Injector.BepInEx.csproj] : error : legal game directory is missing"],
                1,
            )
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, []),
                root,
                env={"FUSIONRPG_GAME_DIR": "", "FUSIONRPG_ML_GAMEDIR": ""},
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("BLOCKED", result.stdout)
            self.assertIn("FusionRpg.Injector.BepInEx.csproj", result.stdout)

    def test_mixed_interop_and_solution_build_errors_are_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            set_fake_dotnet_state(
                root,
                "build",
                [
                    "[FusionRpg.Injector.BepInEx.csproj] : error : legal game directory is missing",
                    "Solution.cs : error CS1001: unrelated solution failure",
                ],
                1,
            )
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("non-interop project errors", result.stdout)
            self.assertIn("VERDICT: RED", result.stdout)

    def test_malformed_declared_manifest_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            (root / "tests" / "core-test-projects.v1.json").write_text("{", encoding="utf-8")
            commit_path(root, "tests/core-test-projects.v1.json", "malformed declared surface")
            dotnet = fake_dotnet(root / "dotnet.ps1")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, [], skip_build=True, skip_guards=True),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("declared-test-manifest-invalid", result.stdout)
            self.assertIn("VERDICT: RED", result.stdout)

    def test_duplicate_declared_project_is_red_instead_of_silently_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            manifest_path = root / "tests" / "core-test-projects.v1.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["projects"].append({"name": "Alpha"})
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            commit_path(root, "tests/core-test-projects.v1.json", "duplicate declared surface")
            dotnet = fake_dotnet(root / "dotnet.ps1")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, [], skip_build=True, skip_guards=True),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("duplicate", result.stdout.lower())
            self.assertIn("VERDICT: RED", result.stdout)

    def test_dirty_merge_tree_is_rejected_before_checks_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            (root / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("dirty", result.stdout.lower())
            self.assertNotIn("STARTED=", result.stdout)

    def test_wrong_branch_is_rejected_before_checks_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_post_fixture(root, ["Alpha"])
            dotnet = fake_dotnet(root / "dotnet.ps1")
            git(root, "checkout", "-b", "not-the-integration-branch")
            result = run_tool(
        POST_MERGE,
                post_arguments(root, dotnet, None),
                root,
                env=legal_game_environment(root),
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("features/mega-merge", result.stdout + result.stderr)
            self.assertNotIn("STARTED=", result.stdout)

    def test_help_does_not_execute_the_gate(self) -> None:
        result = run_tool(POST_MERGE, ["--help"], ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("STARTED=", result.stdout)


class AcceptanceTests(unittest.TestCase):
    def test_missing_full_sha_is_rejected_before_any_acceptance_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            init_repo(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='missing-sha', checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            # The claim is "a missing full SHA is REFUSED, and it names the missing argument". The
            # spelling legitimately changed with the port - PowerShell's `-ExpectSha` is argparse's
            # `--expect-sha` - so the assertion is on the argument NAME case- and separator-
            # insensitively rather than on the old PowerShell token. Asserting `ExpectSha` verbatim
            # would pin an interface that no longer exists; asserting only a non-zero exit would drop
            # the whole point, which is that the refusal SAYS WHAT IS MISSING.
            self.assertNotEqual(result.returncode, 0)
            combined = (result.stdout + result.stderr).lower().replace("-", "")
            self.assertIn("expectsha", combined)
            # And the refusal must arrive BEFORE any acceptance work: no check log directory, and no
            # review checkout. A tool that validated late would still exit non-zero with the name in
            # it, and this is the assertion that separates the two.
            self.assertFalse((root / "logs").exists(),
                             "the tool created its log directory before refusing a missing SHA")
            self.assertFalse((root / ".claude" / "worktrees").exists(),
                             "the tool created a review checkout before refusing a missing SHA")

    def test_empty_check_set_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='empty', expect_sha=sha, checks=[], repo=root, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("at least one", result.stdout + result.stderr)
            self.assertFalse((root / ".claude" / "cmdc-agents" / "acceptance").exists())

    def test_invalid_full_sha_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            init_repo(root)
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='invalid-sha', expect_sha='0' * 40, checks=['smoke|||cmd /c echo evidence'], repo=root, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("expected sha", (result.stdout + result.stderr).lower())

    def test_existing_stale_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            directory = root / ".claude" / "cmdc-agents" / "acceptance"
            directory.mkdir(parents=True)
            stale_sha = "1" * 40
            (directory / f"stale-{sha[:8]}.json").write_text(
                json.dumps(acceptance_artifact("stale", stale_sha)),
                encoding="utf-8",
            )
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='stale', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("stale or malformed", (result.stdout + result.stderr).lower())
            self.assertIn("sha mismatch", (result.stdout + result.stderr).lower())

    def test_existing_schema_invalid_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            directory = root / ".claude" / "cmdc-agents" / "acceptance"
            directory.mkdir(parents=True)
            artifact = acceptance_artifact("schema", sha)
            artifact["checks"][0]["exit"] = "0"
            (directory / f"schema-{sha[:8]}.json").write_text(
                json.dumps(artifact),
                encoding="utf-8",
            )
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='schema', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("exit must be an integer", (result.stdout + result.stderr).lower())

    def test_existing_verdict_with_junk_suffix_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/schema")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            directory = root / ".claude" / "cmdc-agents" / "acceptance"
            directory.mkdir(parents=True)
            artifact = acceptance_artifact("schema", sha, verdict="GREENjunk")
            (directory / f"schema-{sha[:8]}.json").write_text(
                json.dumps(artifact),
                encoding="utf-8",
            )
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='schema', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("outside the acceptance vocabulary", (result.stdout + result.stderr).lower())
            self.assertFalse((root / ".claude" / "worktrees" / "cmdc-review-schema").exists())

    def test_existing_malformed_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            directory = root / ".claude" / "cmdc-agents" / "acceptance"
            directory.mkdir(parents=True)
            (directory / f"malformed-{sha[:8]}.json").write_text("{", encoding="utf-8")
            result = run_tool(
                ACCEPT_LANE,
                accept_arguments(lane='malformed', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                root,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("malformed evidence", (result.stdout + result.stderr).lower())

    def test_malformed_known_red_registry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/registry")
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "verification-boundaries.v1.json").write_text("{", encoding="utf-8")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='registry', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("cannot parse registered known-red evidence", (result.stdout + result.stderr).lower())
            finally:
                remove_worktree(root, "registry")

    def test_unrelated_sha_is_rejected_before_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = init_repo(root)
            git(root, "checkout", "-b", "cmdc/lane")
            git(root, "checkout", "features/mega-merge")
            git(root, "checkout", "-b", "unrelated")
            (root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
            git(root, "add", "unrelated.txt")
            git(root, "commit", "-m", "unrelated work")
            unrelated_sha = git(root, "rev-parse", "HEAD")
            git(root, "checkout", "features/mega-merge")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='lane', expect_sha=unrelated_sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("not reachable", (result.stdout + result.stderr).lower())
                self.assertIn(base[:8], result.stdout + result.stderr)
            finally:
                remove_worktree(root, "lane")

    def test_direct_merge_rejects_reviewed_sha_from_unrelated_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = make_unrelated_lane_repo(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            before = git(root, "rev-parse", "HEAD")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='unrelated', expect_sha=lane_sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs', merge=True),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("does not descend from", (result.stdout + result.stderr).lower())
                self.assertEqual(git(root, "rev-parse", "HEAD"), before)
                self.assertFalse(
                    (root / ".claude" / "cmdc-agents" / "acceptance" / f"unrelated-{lane_sha[:8]}.json").exists()
                )
            finally:
                remove_worktree(root, "unrelated")

    def test_direct_merge_accepts_reviewed_sha_descending_from_integration(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, lane_sha = self.make_lane_repo_for_acceptance(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='lane', expect_sha=lane_sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs', merge=True),
                    root,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                parents = git(root, "show", "-s", "--format=%P", "HEAD").split()
                self.assertIn(base, parents)
                self.assertIn(lane_sha, parents)
            finally:
                remove_worktree(root, "lane")

    def test_direct_merge_still_rejects_unrelated_dirty_manager_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo_for_acceptance(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            (root / "unrelated.txt").write_text("dirty\n", encoding="utf-8")
            before = git(root, "rev-parse", "HEAD")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='lane', expect_sha=lane_sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs', merge=True),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("dirty path", (result.stdout + result.stderr).lower())
                self.assertEqual(git(root, "rev-parse", "HEAD"), before)
            finally:
                remove_worktree(root, "lane")

    def test_direct_merge_into_non_integration_branch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, lane_sha = self.make_lane_repo_for_acceptance(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            git(root, "checkout", "-b", "wrong-integration")
            before = git(root, "rev-parse", "HEAD")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='lane', expect_sha=lane_sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs', merge_into='wrong-integration', merge=True),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("features/mega-merge", (result.stdout + result.stderr).lower())
                self.assertEqual(git(root, "rev-parse", "HEAD"), before)
            finally:
                remove_worktree(root, "lane")

    @staticmethod
    def make_lane_repo_for_acceptance(root: Path) -> tuple[str, str]:
        base = init_repo(root)
        git(root, "checkout", "-b", "cmdc/lane")
        (root / "lane.txt").write_text("lane\n", encoding="utf-8")
        git(root, "add", "lane.txt")
        git(root, "commit", "-m", "lane work")
        lane_sha = git(root, "rev-parse", "HEAD")
        git(root, "checkout", "features/mega-merge")
        return base, lane_sha

    def test_valid_run_writes_full_sha_machine_readable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/valid")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='valid', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = root / ".claude" / "cmdc-agents" / "acceptance" / f"valid-{sha[:8]}.json"
                data = json.loads(artifact.read_text(encoding="utf-8-sig"))
                self.assertEqual(data["schemaVersion"], 2)
                self.assertEqual(data["sha"], sha)
                self.assertEqual(data["verdict"], "GREEN")
                self.assertGreaterEqual(len(data["checks"]), 1)
            finally:
                remove_worktree(root, "valid")

    def test_dirty_review_checkout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/dirty-review")
            fake = make_fake_cmdc(root / "fake_cmdc.py", dirty_review=True)
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='dirty-review', expect_sha=sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("review checkout is dirty", (result.stdout + result.stderr).lower())
            finally:
                remove_worktree(root, "dirty-review")

    def test_red_check_writes_valid_red_evidence_and_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/red")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='red', expect_sha=sha, checks=['smoke|||cmd /c exit 7'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = root / ".claude" / "cmdc-agents" / "acceptance" / f"red-{sha[:8]}.json"
                data = json.loads(artifact.read_text(encoding="utf-8-sig"))
                self.assertEqual(data["verdict"], "UNATTRIBUTED")
                self.assertEqual(data["checks"][0]["exit"], 7)
            finally:
                remove_worktree(root, "red")


class MergeLaneTests(unittest.TestCase):
    def make_lane_repo(self, root: Path) -> tuple[str, str]:
        base = init_repo(root)
        git(root, "checkout", "-b", "cmdc/lane")
        (root / "lane.txt").write_text("lane\n", encoding="utf-8")
        git(root, "add", "lane.txt")
        git(root, "commit", "-m", "lane work")
        lane_sha = git(root, "rev-parse", "HEAD")
        git(root, "checkout", "features/mega-merge")
        return base, lane_sha

    def write_artifact(self, root: Path, lane: str, sha: str, **kwargs) -> Path:
        directory = root / ".claude" / "cmdc-agents" / "acceptance"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{lane}-{sha[:8]}.json"
        path.write_text(json.dumps(acceptance_artifact(lane, sha, **kwargs)), encoding="utf-8")
        return path

    def run_merge(self, root: Path, lane: str = "lane") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python", str(MERGE_LANES), lane],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=45,
        )

    def test_refuses_to_merge_without_acceptance_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("missing", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)
            self.assertNotIn(lane_sha, git(root, "log", "--format=%H", "-1"))

    def test_refuses_reviewed_sha_from_unrelated_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = make_unrelated_lane_repo(root)
            self.write_artifact(root, "unrelated", lane_sha)
            before = git(root, "rev-parse", "HEAD")
            result = subprocess.run(
                ["python", str(MERGE_LANES), "unrelated"],
                cwd=root,
                text=True,
                capture_output=True,
                timeout=45,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("does not descend from", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_stale_acceptance_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, lane_sha = self.make_lane_repo(root)
            directory = root / ".claude" / "cmdc-agents" / "acceptance"
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f"lane-{base[:8]}.json").write_text(
                json.dumps(acceptance_artifact("lane", base)), encoding="utf-8"
            )
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("stale", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)
            self.assertNotIn(lane_sha, before)

    def test_refuses_mismatched_sha_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", base)
            old = root / ".claude" / "cmdc-agents" / "acceptance" / f"lane-{base[:8]}.json"
            exact = root / ".claude" / "cmdc-agents" / "acceptance" / f"lane-{lane_sha[:8]}.json"
            old.rename(exact)
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("sha", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_malformed_acceptance_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            directory = root / ".claude" / "cmdc-agents" / "acceptance"
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f"lane-{lane_sha[:8]}.json").write_text("{", encoding="utf-8")
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("malformed", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_empty_check_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", lane_sha, checks=[])
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("non-empty", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_red_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", lane_sha, verdict="RED")
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("not green", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_green_verdict_with_junk_suffix_as_malformed_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", lane_sha, verdict="GREENjunk")
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("outside the acceptance vocabulary", (result.stdout + result.stderr).lower())
            self.assertNotIn("not green", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_green_artifact_with_failed_test_details(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            artifact = acceptance_artifact("lane", lane_sha)
            artifact["checks"][0]["failedTests"] = ["Namespace.Tests.ShouldPass"]
            self.write_artifact(root, "lane", lane_sha, checks=artifact["checks"])
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("failed", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_green_artifact_with_failed_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            artifact = acceptance_artifact("lane", lane_sha)
            artifact["checks"][0]["summary"] = "Failed!  - Failed: 1, Passed: 0"
            self.write_artifact(root, "lane", lane_sha, checks=artifact["checks"])
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("failed summary", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_dirty_manager_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", lane_sha)
            (root / "unrelated.txt").write_text("dirty\n", encoding="utf-8")
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("dirty", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_wrong_current_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", lane_sha)
            git(root, "checkout", "-b", "wrong-integration")
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("features/mega-merge", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_refuses_staged_acceptance_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane_sha = self.make_lane_repo(root)
            artifact = self.write_artifact(root, "lane", lane_sha)
            git(root, "add", str(artifact.relative_to(root)).replace("\\", "/"))
            before = git(root, "rev-parse", "HEAD")
            result = self.run_merge(root)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("staged", (result.stdout + result.stderr).lower())
            self.assertEqual(git(root, "rev-parse", "HEAD"), before)

    def test_merges_only_after_exact_green_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, lane_sha = self.make_lane_repo(root)
            self.write_artifact(root, "lane", lane_sha)
            result = self.run_merge(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            parents = git(root, "show", "-s", "--format=%P", "HEAD").split()
            self.assertIn(lane_sha, parents)
            self.assertIn(base, parents)

    def test_zero_exit_with_parsed_failure_is_not_green_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/parsed-red")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='parsed-red', expect_sha=sha, checks=['smoke|||cmd /c echo Failed Namespace.Tests.ShouldPass'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = root / ".claude" / "cmdc-agents" / "acceptance" / f"parsed-red-{sha[:8]}.json"
                data = json.loads(artifact.read_text(encoding="utf-8-sig"))
                self.assertNotEqual(data["verdict"], "GREEN")
                self.assertIn("Namespace.Tests.ShouldPass", data["checks"][0]["newRedTests"])
            finally:
                remove_worktree(root, "parsed-red")

    def test_zero_exit_failed_summary_is_not_green_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/summary-red")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='summary-red', expect_sha=sha, checks=['smoke|||cmd /c echo Failed! - Failed: 1'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = root / ".claude" / "cmdc-agents" / "acceptance" / f"summary-red-{sha[:8]}.json"
                data = json.loads(artifact.read_text(encoding="utf-8-sig"))
                self.assertNotEqual(data["verdict"], "GREEN")
            finally:
                remove_worktree(root, "summary-red")

    def test_indented_failed_summary_is_not_green_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = init_repo(root)
            git(root, "checkout", "-b", "cmdc/indented-red")
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                result = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='indented-red', expect_sha=sha, checks=['smoke|||cmd /c echo    Test Run Failed.'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = root / ".claude" / "cmdc-agents" / "acceptance" / f"indented-red-{sha[:8]}.json"
                data = json.loads(artifact.read_text(encoding="utf-8-sig"))
                self.assertNotEqual(data["verdict"], "GREEN")
                self.assertIn("Failed", data["checks"][0]["summary"])
            finally:
                remove_worktree(root, "indented-red")

    def test_consumes_artifact_written_by_real_acceptance_entry_point(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, lane_sha = self.make_lane_repo(root)
            fake = make_fake_cmdc(root / "fake_cmdc.py")
            try:
                accepted = run_tool(
                    ACCEPT_LANE,
                    accept_arguments(lane='lane', expect_sha=lane_sha, checks=['smoke|||cmd /c echo evidence'], repo=root, cmdc=fake, log_root=root / 'logs'),
                    root,
                )
                self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
                merged = self.run_merge(root)
                self.assertEqual(merged.returncode, 0, merged.stdout + merged.stderr)
                parents = git(root, "show", "-s", "--format=%P", "HEAD").split()
                self.assertIn(lane_sha, parents)
                self.assertIn(base, parents)
            finally:
                remove_worktree(root, "lane")


class EntryPointContract(unittest.TestCase):
    """Why this class exists.

    For a long time this file drove `post-merge-check.ps1` and `accept-lane.ps1` through `run_pwsh`
    while the Python twins sat beside them, unit-tested and UNEXERCISED by the integration contract.
    The twins' suites were green, so the port read as finished while the live path was untouched. These
    two tests make that state impossible to reach again by accident.
    """

    def test_the_pipeline_entry_points_are_Python(self) -> None:
        # A twin must not be added beside a still-live original without anything noticing.
        self.assertEqual(".py", POST_MERGE.suffix, "the merged-head gate must be the Python twin")
        self.assertEqual(".py", ACCEPT_LANE.suffix, "the acceptance gate must be the Python twin")
        for entry_point in (POST_MERGE, ACCEPT_LANE):
            with self.subTest(entry=entry_point.name):
                self.assertTrue(entry_point.is_file(), f"{entry_point} does not exist")
                self.assertFalse(entry_point.with_suffix(".ps1").exists(),
                                 f"{entry_point.with_suffix('.ps1')} still exists: the twins and a live "
                                 "PowerShell original is the state this class exists to prevent")

    def test_nothing_in_this_file_shells_pwsh(self) -> None:
        """Not a ban on the WORD: the module docstring names the retired scripts, and that sentence is
        provenance - removing it would make the migration unreadable. The contract is about LAUNCHING
        one, so the module's docstrings and comments are stripped through the AST (a line-based filter
        got this wrong first, and a fragile filter that passes is worse than none) and what remains is
        searched.
        """
        import ast as _ast

        tree = _ast.parse(Path(__file__).read_text(encoding="utf-8"))
        # THIS CLASS IS EXCLUDED, and that is not a convenience: the search list below is a tuple of
        # string literals naming the very launchers being banned, so scanning the test's own body finds
        # them immediately and the test can never pass. An earlier version failed exactly that way.
        tree.body = [node for node in tree.body
                     if not (isinstance(node, _ast.ClassDef)
                             and node.name == "EntryPointContract")]
        for node in _ast.walk(tree):
            if not isinstance(node, (_ast.Module, _ast.ClassDef, _ast.FunctionDef,
                                     _ast.AsyncFunctionDef)):
                continue
            body = node.body
            if (body and isinstance(body[0], _ast.Expr)
                    and isinstance(body[0].value, _ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [_ast.Pass()]
        code = _ast.unparse(tree)
        for launcher in ("pwsh", "powershell", "-NoProfile", "run_pwsh"):
            with self.subTest(launcher=launcher):
                self.assertNotIn(launcher, code.lower(),
                                 f"this file still launches or names a PowerShell launcher: {launcher}")

    def test_repeating_a_test_project_flag_is_not_a_comma_list(self) -> None:
        """`--test-project` is `action="append"`, so a comma-joined value arrives as ONE project name.

        The consequence is a silent narrowing rather than an error: the gate would run its DECLARED
        surface, report green, and never run what the caller asked for. Asserted on the builder, so the
        encoding is pinned without spawning a gate.
        """
        # `str(Path(...))` on Windows renders backslashes, so the expectation is built from the same
        # Path objects rather than from a hand-written "C:/repo" the platform disagrees with.
        repo, dotnet = Path("repo"), Path("dotnet.cmd")
        args = post_arguments(repo, dotnet, ["tests/Alpha", "tests/Beta"])
        self.assertEqual(
            ["--repo", str(repo), "--dotnet", str(dotnet),
             "--test-project", "tests/Alpha", "--test-project", "tests/Beta"],
            [str(a) for a in args])
        self.assertEqual(2, sum(1 for a in args if a == "--test-project"),
                         "each project needs its own flag; one flag would run neither")

    def test_an_empty_check_list_emits_no_check_flag(self) -> None:
        # `--check` is `action="append"` too, and an empty list must emit NOTHING rather than an empty
        # value: the tool refuses an empty check set, and `--check ""` would be a check named "".
        repo = Path("repo")
        self.assertNotIn("--check", accept_arguments("x", repo=repo))
        self.assertEqual(["--lane", "x", "--repo", str(repo)], accept_arguments("x", repo=repo))

    def test_the_log_root_is_passed_so_fixture_isolation_holds(self) -> None:
        """Found by falsification: dropping `--log-root` left all 62 tests green.

        The tool's DEFAULT log root is `<temp>/cmdc-acceptance` - the SHARED system temp, not the
        fixture. So a regression that stopped passing the flag would not change any verdict; it would
        quietly move every acceptance log out of the per-test temporary directory, where two concurrent
        runs share one path. That is the temp-store leak this repo has already paid for, and a gate
        whose isolation can be lost without a single test noticing is not fail-closed.
        """
        repo, logs = Path("repo"), Path("repo/logs")
        args = accept_arguments("x", repo=repo, log_root=logs)
        self.assertIn("--log-root", args)
        self.assertEqual(str(logs), args[args.index("--log-root") + 1])
        # And a call that does not name one must not silently acquire a flag pointing at the fixture.
        self.assertNotIn("--log-root", accept_arguments("x", repo=repo))

    def test_the_dotnet_double_is_launchable_without_a_shell(self) -> None:
        # A `.ps1` double cannot be launched by subprocess without a shell, and handing the gate a
        # shell would put back the quoting surface the argv migration removed. Asserted on the double
        # this file actually writes, because a regression here is invisible in every other test.
        with tempfile.TemporaryDirectory() as temp:
            double = fake_dotnet(Path(temp) / "dotnet.ps1")
            self.assertEqual(".cmd", double.suffix, "the double must be directly launchable")
            self.assertTrue(double.is_file())
            self.assertTrue(double.with_name("fake_dotnet.py").is_file(),
                            "the shim's Python half is missing, so the .cmd would exit 0 doing nothing")
            self.assertIn("fake_dotnet.py", double.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
