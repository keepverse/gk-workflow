#!/usr/bin/env python3
"""Regressions for `post_merge_check.py`, the manager's fail-closed gate at the MERGED head.

Three groups:

  * UNIT -- the summary classifiers, the declared-manifest reader, the legal-game probe, the
    project resolver, the dotnet resolution, and the four-branch verdict ladder, all driven
    directly so a reason code cannot be renamed unnoticed.
  * END TO END -- real temporary repositories and real child processes, for the two preconditions
    the retired script refused to report a verdict without: dotnet missing, and a head/branch that
    is not a clean `features/mega-merge`. Plus the argv each phase is given, pinned, because the
    phase logic is exercised with a substituted runner and a wrong command line would be
    invisible.
  * DIFFERENTIAL -- while `post-merge-check.ps1` still exists, the same fixture goes through both
    entry points and the verdict lines are compared.

The build/Guard/test phases are exercised by substituting `run`, which is the reason the tool is
importable: a real `dotnet build` of the solution is not something a unit test should pay for, and
the classification logic is the part that decides a verdict. The kill path is proven against a
real process.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "post_merge_check.py"
PS_MODULE_PATH = HERE / "post-merge-check.ps1"
ACCEPT_MODULE_PATH = HERE / "accept_lane.py"

spec = importlib.util.spec_from_file_location("post_merge_check", MODULE_PATH)
assert spec and spec.loader
post_merge_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(post_merge_check)

accept_spec = importlib.util.spec_from_file_location("accept_lane", ACCEPT_MODULE_PATH)
assert accept_spec and accept_spec.loader
accept_lane = importlib.util.module_from_spec(accept_spec)
accept_spec.loader.exec_module(accept_lane)


# --------------------------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------------------------

def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                            timeout=60, check=False)
    if result.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr or result.stdout}")
    return result.stdout.strip()


def init_repo(path: Path, branch: str = "features/mega-merge") -> str:
    """A minimal integration repository. The gate refuses a dirty tree, so every fixture file a
    test writes has to be committed (or ignored) -- that is the contract, not an inconvenience."""
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.name", "Test User")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "commit.gpgsign", "false")
    git(path, "checkout", "-q", "-b", branch)
    (path / "base.txt").write_text("base\n", encoding="utf-8")
    (path / ".gitignore").write_text("legal-game/\nfake-*.json\n", encoding="utf-8")
    git(path, "add", "base.txt", ".gitignore")
    git(path, "commit", "-q", "-m", "base")
    return git(path, "rev-parse", "HEAD")


def commit_fixture(root: Path, message: str = "fixture") -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)


def write_manifest(root: Path, projects: list[str], residual: str = "FusionRpg.Core.Tests",
                   schema_version: int = 1) -> None:
    (root / "tests").mkdir(parents=True, exist_ok=True)
    manifest = {"schemaVersion": schema_version, "residual": residual,
                "projects": [{"name": name} for name in projects]}
    (root / "tests" / "core-test-projects.v1.json").write_text(json.dumps(manifest),
                                                                encoding="utf-8")


def make_test_projects(root: Path, names: list[str]) -> None:
    for name in names:
        project = root / "tests" / name / f"{name}.csproj"
        project.parent.mkdir(parents=True, exist_ok=True)
        project.write_text("<Project />\n", encoding="utf-8")


def legal_game_environment(root: Path) -> dict[str, str]:
    game = root / "legal-game"
    for relative in ("BepInEx/core/BepInEx.Core.dll", "BepInEx/interop/Assembly-CSharp.dll",
                     "MelonLoader/net6/MelonLoader.dll",
                     "MelonLoader/Il2CppAssemblies/Assembly-CSharp.dll"):
        marker = game / relative
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("fixture evidence\n", encoding="utf-8")
    return {"FUSIONRPG_GAME_DIR": str(game), "FUSIONRPG_ML_GAMEDIR": str(game)}


def run_gate(root: Path, *args: str, env_overrides: dict[str, str] | None = None
             ) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    if env_overrides:
        environment.update(env_overrides)
    return subprocess.run([sys.executable, str(MODULE_PATH), *args], cwd=root,
                          capture_output=True, text=True, timeout=300, check=False,
                          env=environment)


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.addCleanup(self.temp.cleanup)

    def gate(self, *args: str, env_overrides: dict[str, str] | None = None
             ) -> subprocess.CompletedProcess[str]:
        """The preconditions need a resolvable dotnet that is never actually invoked, because the
        gate refuses before any phase runs. `sys.executable` is a real file, so `resolve_dotnet`
        accepts it, and the abort happens before the first build/test."""
        return run_gate(self.root, "--repo", str(self.root), "--dotnet", sys.executable,
                        *args, env_overrides=env_overrides)


class Recorder:
    """Stands in for `run`, recording the argv each phase asked for and returning a canned result.

    `git` calls pass straight through: the checkout proof is part of what the gate decides, and
    substituting it would let the gate "prove" a clean tree that was never inspected.
    """

    def __init__(self, results: dict[str, object], real_run) -> None:
        self.results = results
        self.real_run = real_run
        self.calls: list[list[str]] = []

    def __call__(self, argv, *, stage, timeout, cwd=None):
        if Path(argv[0]).name.lower() in ("git", "git.exe"):
            return self.real_run(argv, stage=stage, timeout=timeout, cwd=cwd)
        self.calls.append(list(argv))
        joined = " ".join(argv)
        key = "build" if " build " in f" {joined} " else (
            "guard" if "FusionRpg.Guard.Tests" in joined else "test")
        output, code = self.results.get(key, (["ok"], 0))
        return post_merge_check.Completed(list(argv), code, "\n".join(output), "", 0.1)


def build_args(root: Path, projects: list[str] | None = None, *, skip_build: bool = False,
               skip_guards: bool = False) -> list[str]:
    args = ["--repo", str(root), "--dotnet", sys.executable]
    if skip_build:
        args.append("--skip-build")
    if skip_guards:
        args.append("--skip-guards")
    for project in projects or []:
        args.extend(["--test-project", project])
    return args


def run_in_process(root: Path, results: dict[str, object], *, projects: list[str] | None = None,
                   skip_build: bool = False, skip_guards: bool = False,
                   env_overrides: dict[str, str] | None = None
                   ) -> tuple[int, dict, list[str], str]:
    """Drive `run_gate` in-process with `run` substituted, so the phase logic is exercised
    deterministically and cheaply. Returns (exit code, envelope, argv calls, transcript)."""
    arguments = post_merge_check.build_parser().parse_args(
        build_args(root, projects, skip_build=skip_build, skip_guards=skip_guards))
    if env_overrides:
        saved = dict(os.environ)
        os.environ.update(env_overrides)
    else:
        saved = None
    real_run = post_merge_check.run
    recorder = Recorder(results, real_run)
    stream = io.StringIO()
    transcript = post_merge_check.Transcript(stream)
    post_merge_check.run = recorder
    try:
        code, envelope = post_merge_check.run_gate(arguments, transcript)
    finally:
        post_merge_check.run = real_run
        if saved is not None:
            os.environ.clear()
            os.environ.update(saved)
    return code, envelope, recorder.calls, stream.getvalue()


# --------------------------------------------------------------------------------------------
# UNIT: the summary classifiers
# --------------------------------------------------------------------------------------------

class SummaryTests(unittest.TestCase):
    def test_failed_summary_truth_table(self) -> None:
        table = [
            (["Passed!  - Failed: 0, Passed: 1"], False),
            (["Failed!  - Failed: 1, Passed: 0"], True),
            (["Build FAILED."], True),
            (["Build succeeded."], False),
            (["the command ran"], False),
            (["Failed: unknown"], True),               # the FIXED dead branch
            (["a", "b", "Failed: 2, Passed: 3"], True),
        ]
        for lines, expected in table:
            with self.subTest(lines=lines):
                self.assertEqual(post_merge_check.test_failed_summary(lines), expected)

    def test_a_zero_count_line_does_not_stop_the_scan(self) -> None:
        # The retired function used `elseif`, so a `Failed: 0` line skipped only ITS OWN fallback
        # and the loop continued to the next line. Ported as written -- and a later line is still
        # found.
        self.assertTrue(post_merge_check.test_failed_summary(
            ["Failed: 0", "Failed: 1, Passed: 0"]))
        self.assertFalse(post_merge_check.test_failed_summary(
            ["Failed: 0", "Passed: 12"]))

    def test_the_retired_bare_marker_regex_was_dead_code(self) -> None:
        retired = re.compile(r"\bFailed:\b", re.IGNORECASE)
        for text in ("Failed: unknown", "Failed:", "Failed: see the log"):
            with self.subTest(text=text):
                self.assertIsNone(retired.search(text))
                self.assertIsNotNone(post_merge_check.BARE_FAILED_RE.search(text))

    def test_a_positive_test_count_is_required(self) -> None:
        self.assertFalse(post_merge_check.test_positive_test_count(
            ["Passed!  - Failed: 0, Passed: 0, Total: 0"]))
        self.assertTrue(post_merge_check.test_positive_test_count(["Passed: 3"]))
        self.assertFalse(post_merge_check.test_positive_test_count(["the command ran"]))

    def test_a_skipped_run_is_not_a_positive_test_count(self) -> None:
        """`Total` counts SKIPPED tests, so an all-skipped run must not read as executed.

        The test above pins `Total: 0`, which fails for the uninteresting reason that zero is not
        positive - so a `Total`-based gate looks covered while failing open. This is the shape that
        slipped through: the pattern found `['0', '38']` and `any(int(count) > 0 ...)` reported a
        positive executed count for a run in which nothing executed.
        """
        all_skipped = ["Skipped!  - Failed: 0, Passed: 0, Skipped: 38, Total: 38"]
        self.assertEqual(post_merge_check.POSITIVE_COUNT_RE.findall(all_skipped[0]), ["0"])
        self.assertFalse(post_merge_check.test_positive_test_count(all_skipped))
        # A run that really did execute still counts, and a partially-skipped run counts on what ran.
        self.assertTrue(post_merge_check.test_positive_test_count(
            ["Passed!  - Failed: 0, Passed: 36, Skipped: 2, Total: 38"]))

    def test_a_build_success_summary_is_required(self) -> None:
        self.assertTrue(post_merge_check.test_build_succeeded(["Build succeeded."]))
        self.assertFalse(post_merge_check.test_build_succeeded(["Build completed."]))

    def test_a_test_summary_line_is_required(self) -> None:
        self.assertTrue(post_merge_check.has_test_summary(["Passed!  - Failed: 0, Passed: 1"]))
        self.assertFalse(post_merge_check.has_test_summary(["the command ran"]))


class CrossToolAgreementTests(unittest.TestCase):
    """The two tools each carry their own copy of the failed-summary test, ported separately
    because each was a separate copy in the retired scripts.

    They agree on everything a dotnet run actually prints EXCEPT one input, and the divergence is
    real and inherited, not introduced here:

      * `accept_lane` treats `Test Run Failed.` as a failure (accept-lane.ps1:52).
      * `post_merge_check` does not (post-merge-check.ps1:237-238 tests only `Failed!` and
        `Build FAILED`).

    A `dotnet test` run that prints `Test Run Failed.` therefore makes the merged-head gate
    quieter than the lane gate. That is pinned here rather than papered over; whether to close it
    is a decision for the owning program, not a silent port.
    """

    CORPUS = [
        "Passed!  - Failed: 0, Passed: 12",
        "Failed!  - Failed: 1, Passed: 11",
        "Build FAILED.",
        "Build succeeded.",
        "Failed: 0",
        "Failed: 3",
        "Failed: unknown",
        "OK -- 12 targets",
        "",
        "error CS1001: no definition",
    ]

    #: The one documented divergence, with the truth on both sides.
    KNOWN_DIVERGENCE = "   Test Run Failed."

    def test_the_two_copies_agree_except_on_the_documented_input(self) -> None:
        for line in self.CORPUS:
            with self.subTest(line=line):
                self.assertEqual(post_merge_check.test_failed_summary([line]),
                                 accept_lane.test_failed_summary(line),
                                 f"the two copies diverged on {line!r}")

    def test_the_documented_divergence_is_still_the_inherited_one(self) -> None:
        self.assertTrue(accept_lane.test_failed_summary(self.KNOWN_DIVERGENCE),
                        "the lane harness must keep treating this as a failure")
        self.assertFalse(post_merge_check.test_failed_summary([self.KNOWN_DIVERGENCE]),
                         "the merged gate must keep its inherited, narrower reading")


class VerdictLadderTests(unittest.TestCase):
    def test_no_check_is_never_a_pass(self) -> None:
        self.assertEqual(post_merge_check.Report().verdict(),
                         "UNKNOWN -- no check ran, which is never a pass")

    def test_a_failure_outranks_everything(self) -> None:
        report = post_merge_check.Report()
        report.ran = 3
        report.block("legal-game/interops evidence is unavailable: FUSIONRPG_GAME_DIR is not set")
        report.failure("guards: dotnet test exited 1")
        self.assertEqual(report.verdict(), "RED -- guards: dotnet test exited 1")

    def test_blocked_is_not_green(self) -> None:
        report = post_merge_check.Report()
        report.ran = 2
        report.block("build skipped by request; merged-head build evidence is absent")
        self.assertTrue(report.verdict().startswith("BLOCKED -- "))
        self.assertNotIn("GREEN", report.verdict())

    def test_only_a_clean_run_is_green(self) -> None:
        report = post_merge_check.Report()
        report.ran = 4
        self.assertEqual(report.verdict(), "GREEN")

    def test_multiple_failures_are_all_named(self) -> None:
        report = post_merge_check.Report()
        report.ran = 2
        report.failure("guards: dotnet test exited 1")
        report.failure("Alpha: failed summary was emitted despite a zero process exit")
        self.assertEqual(
            report.verdict(),
            "RED -- guards: dotnet test exited 1, Alpha: failed summary was emitted despite a "
            "zero process exit")


# --------------------------------------------------------------------------------------------
# UNIT: the declared manifest, the project resolver, the legal-game probe, dotnet
# --------------------------------------------------------------------------------------------

class DeclaredManifestTests(RepoCase):
    def declared(self, **kwargs) -> tuple[list[str], list[str]]:
        failures: list[str] = []
        return post_merge_check.declared_test_projects(self.root, failures.append), failures

    def test_the_declared_surface_and_residual_are_always_included(self) -> None:
        write_manifest(self.root, ["Alpha", "Beta"])
        paths, failures = self.declared()
        self.assertEqual(failures, [])
        self.assertEqual([Path(p).as_posix() for p in paths],
                         ["tests/Alpha", "tests/Beta", "tests/FusionRpg.Core.Tests"])

    def test_a_missing_manifest_is_red(self) -> None:
        (self.root / "tests").mkdir(parents=True, exist_ok=True)
        paths, failures = self.declared()
        self.assertEqual(paths, [])
        self.assertTrue(failures[0].startswith("declared-test-manifest-missing:"))

    def test_malformed_json_is_red(self) -> None:
        (self.root / "tests").mkdir(parents=True, exist_ok=True)
        (self.root / "tests" / "core-test-projects.v1.json").write_text("{", encoding="utf-8")
        _paths, failures = self.declared()
        self.assertTrue(failures[0].startswith("declared-test-manifest-invalid:"))

    def test_a_non_object_root_is_red(self) -> None:
        (self.root / "tests").mkdir(parents=True, exist_ok=True)
        (self.root / "tests" / "core-test-projects.v1.json").write_text("[]", encoding="utf-8")
        _paths, failures = self.declared()
        self.assertEqual(failures, ["declared-test-manifest-invalid: root is not an object"])

    def test_the_schema_version_is_a_closed_integer_one(self) -> None:
        for version in (0, 2, "1", 1.0, True):
            with self.subTest(version=version):
                write_manifest(self.root, ["Alpha"], schema_version=version)
                _paths, failures = self.declared()
                self.assertEqual(failures,
                                 ["declared-test-manifest-schema: expected integer schemaVersion 1"])

    def test_projects_must_be_an_array(self) -> None:
        (self.root / "tests").mkdir(parents=True, exist_ok=True)
        (self.root / "tests" / "core-test-projects.v1.json").write_text(
            json.dumps({"schemaVersion": 1, "residual": "R", "projects": {}}), encoding="utf-8")
        _paths, failures = self.declared()
        self.assertEqual(failures, ["declared-test-manifest-schema: projects must be an array"])

    def test_an_empty_declared_surface_is_red(self) -> None:
        write_manifest(self.root, [], residual="")
        paths, failures = self.declared()
        self.assertIn("declared-test-manifest-empty: no post-split projects", failures)
        self.assertIn("declared-test-manifest-missing-residual", failures)
        self.assertEqual(paths, [])

    def test_a_duplicate_is_red_rather_than_silently_deduplicated(self) -> None:
        write_manifest(self.root, ["Alpha", "Alpha"])
        _paths, failures = self.declared()
        self.assertIn("declared-test-manifest-duplicate: Alpha", failures)

    def test_a_duplicate_residual_is_red(self) -> None:
        write_manifest(self.root, ["Alpha"], residual="Alpha")
        _paths, failures = self.declared()
        self.assertIn("declared-test-manifest-duplicate: residual Alpha is already declared",
                      failures)

    def test_duplicates_are_case_insensitive(self) -> None:
        write_manifest(self.root, ["Alpha", "ALPHA"])
        _paths, failures = self.declared()
        self.assertTrue(any("duplicate" in failure.lower() for failure in failures))

    def test_an_unsafe_project_name_is_red(self) -> None:
        write_manifest(self.root, ["../escape"])
        _paths, failures = self.declared()
        # Both the bad name AND the empty resulting surface are reported: the retired reader does
        # not stop at the first bad row.
        self.assertEqual(failures, ["declared-test-manifest-name-invalid: ../escape",
                                    "declared-test-manifest-empty: no post-split projects"])

    def test_a_non_string_name_is_red(self) -> None:
        (self.root / "tests").mkdir(parents=True, exist_ok=True)
        (self.root / "tests" / "core-test-projects.v1.json").write_text(
            json.dumps({"schemaVersion": 1, "residual": "R", "projects": [{"name": 7}]}),
            encoding="utf-8")
        _paths, failures = self.declared()
        self.assertEqual(failures, ["declared-test-manifest-schema: every project needs a string "
                                    "name", "declared-test-manifest-empty: no post-split projects"])


class ProjectResolutionTests(RepoCase):
    def resolve(self, requested: str) -> tuple[str | None, list[str]]:
        failures: list[str] = []
        return post_merge_check.resolve_test_project_path(requested, self.root, failures.append), failures

    def test_a_directory_with_one_matching_csproj_resolves(self) -> None:
        make_test_projects(self.root, ["Alpha"])
        resolved, failures = self.resolve("tests/Alpha")
        self.assertEqual(failures, [])
        self.assertEqual(Path(resolved).name, "Alpha.csproj")

    def test_a_directory_with_two_projects_is_named_ambiguous(self) -> None:
        make_test_projects(self.root, ["Alpha"])
        (self.root / "tests" / "Alpha" / "Other.csproj").write_text("<Project />\n",
                                                                   encoding="utf-8")
        resolved, failures = self.resolve("tests/Alpha")
        self.assertIsNone(resolved)
        self.assertIn("test-project-ambiguous: tests/Alpha contains 2 csproj files; expected "
                      "exactly one", failures)

    def test_a_name_mismatch_is_named(self) -> None:
        directory = self.root / "tests" / "Alpha"
        directory.mkdir(parents=True)
        (directory / "Other.csproj").write_text("<Project />\n", encoding="utf-8")
        resolved, failures = self.resolve("tests/Alpha")
        self.assertIsNone(resolved)
        self.assertIn("test-project-name-mismatch: tests/Alpha resolves to Other.csproj, expected "
                      "Alpha.csproj", failures)

    def test_an_explicit_file_resolves(self) -> None:
        make_test_projects(self.root, ["Alpha"])
        resolved, failures = self.resolve("tests/Alpha/Alpha.csproj")
        self.assertEqual(failures, [])
        self.assertEqual(Path(resolved).name, "Alpha.csproj")


class LegalGameEvidenceTests(RepoCase):
    def test_both_hosts_present_is_no_problem(self) -> None:
        self.assertIsNone(post_merge_check.legal_game_evidence_error(
            legal_game_environment(self.root)))

    def test_an_unset_variable_is_named(self) -> None:
        problem = post_merge_check.legal_game_evidence_error(
            {name: "" for name, _ in post_merge_check.LEGAL_GAME_REQUIREMENTS})
        self.assertIn("FUSIONRPG_GAME_DIR is not set", problem)
        self.assertIn("FUSIONRPG_ML_GAMEDIR is not set", problem)

    def test_a_nonempty_but_absent_path_is_named(self) -> None:
        missing = str(self.root / "not-a-real-game")
        problem = post_merge_check.legal_game_evidence_error(
            {"FUSIONRPG_GAME_DIR": missing, "FUSIONRPG_ML_GAMEDIR": missing})
        self.assertIn("path does not exist:", problem)
        self.assertIn("not-a-real-game", problem)

    def test_a_missing_marker_file_is_named(self) -> None:
        environment = legal_game_environment(self.root)
        (self.root / "legal-game" / "BepInEx" / "core" / "BepInEx.Core.dll").unlink()
        problem = post_merge_check.legal_game_evidence_error(environment)
        self.assertIn("FUSIONRPG_GAME_DIR is missing", problem)
        self.assertIn("BepInEx", problem)


class DotnetResolutionTests(unittest.TestCase):
    def test_an_explicit_existing_path_wins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp) / "dotnet"
            fake.write_text("# fixture\n", encoding="utf-8")
            self.assertEqual(post_merge_check.resolve_dotnet(str(fake), {}), str(fake.resolve()))

    def test_a_requested_path_that_does_not_exist_is_a_named_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(post_merge_check.Refusal) as caught:
                post_merge_check.resolve_dotnet(str(Path(temp) / "absent"), {})
        self.assertEqual(caught.exception.code, 9)
        self.assertEqual(caught.exception.stage, "dotnet")
        self.assertIn("dotnet not found", caught.exception.reason)
        self.assertIn("Refusing to report a verdict", caught.exception.reason)

    def test_the_environment_is_the_second_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp) / "dotnet"
            fake.write_text("# fixture\n", encoding="utf-8")
            resolved = post_merge_check.resolve_dotnet("", {"DOTNET_PATH": str(fake)})
            self.assertEqual(resolved, str(fake.resolve()))

    def test_no_committed_drive_specific_fallback(self) -> None:
        # The retired script fell back to a literal 'C:\\Program Files\\dotnet\\dotnet.exe'.
        text = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("C:\\Program Files", text)
        self.assertNotIn("Users\\", text)


class CheckoutProofTests(RepoCase):
    def head_and_branch(self) -> tuple[str, str]:
        return (git(self.root, "rev-parse", "HEAD"),
                git(self.root, "rev-parse", "--abbrev-ref", "HEAD"))

    def test_a_clean_integration_checkout_passes(self) -> None:
        init_repo(self.root)
        head, branch = self.head_and_branch()
        self.assertIsNone(post_merge_check.merged_checkout_error(self.root, head, branch))

    def test_a_dirty_checkout_is_refused(self) -> None:
        init_repo(self.root)
        head, branch = self.head_and_branch()
        (self.root / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        error = post_merge_check.merged_checkout_error(self.root, head, branch)
        self.assertIn("merged checkout is dirty:", error)
        self.assertIn("dirty.txt", error)

    def test_a_moved_head_is_refused(self) -> None:
        init_repo(self.root)
        _head, branch = self.head_and_branch()
        error = post_merge_check.merged_checkout_error(self.root, "0" * 40, branch)
        self.assertIn("merged checkout HEAD changed: expected", error)

    def test_a_moved_branch_is_refused(self) -> None:
        init_repo(self.root)
        head, _branch = self.head_and_branch()
        error = post_merge_check.merged_checkout_error(self.root, head, "somewhere-else")
        self.assertIn("merged checkout branch changed: expected 'somewhere-else', got "
                      "'features/mega-merge'", error)


# --------------------------------------------------------------------------------------------
# END TO END: the preconditions that must ABORT rather than report a verdict
# --------------------------------------------------------------------------------------------

class PreconditionAbortTests(RepoCase):
    def test_a_missing_dotnet_aborts_and_reports_no_verdict(self) -> None:
        init_repo(self.root)
        result = run_gate(self.root, "--repo", str(self.root),
                          "--dotnet", str(self.root / "no-such-dotnet"))
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertIn("ABORT: dotnet not found", result.stdout)
        self.assertNotIn("VERDICT", result.stdout)
        self.assertNotIn("STARTED=", result.stdout)

    def test_a_wrong_branch_aborts_before_any_phase(self) -> None:
        init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "not-the-integration-branch")
        result = self.gate()
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertIn("merged-head check must run on 'features/mega-merge'", result.stdout)
        self.assertNotIn("STARTED=", result.stdout)

    def test_a_dirty_tree_aborts_before_any_phase(self) -> None:
        init_repo(self.root)
        (self.root / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        result = self.gate()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("merged checkout is dirty", result.stdout)
        self.assertNotIn("STARTED=", result.stdout)

    def test_an_unresolvable_repo_is_a_named_refusal(self) -> None:
        result = run_gate(Path(self.temp.name), "--repo", str(self.root / "absent"),
                          "--dotnet", sys.executable)
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertIn("repository root cannot be resolved:", result.stdout)

    def test_a_non_positive_budget_is_refused_before_anything_runs(self) -> None:
        init_repo(self.root)
        result = self.gate("--build-timeout", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--build-timeout must be a positive number of seconds", result.stderr)


class ArgvTests(RepoCase):
    """The command lines are the contract with dotnet, and the phase logic is exercised with a
    substituted runner -- so the argv must be pinned here or a wrong flag would be invisible."""

    def test_each_phase_is_given_its_exact_command_line(self) -> None:
        init_repo(self.root)
        standard_fixture(self.root)
        _code, _envelope, calls, _out = run_in_process(self.root, {})
        flat = [" ".join(call[1:]) for call in calls]      # call[0] is the dotnet executable
        self.assertIn("build FusionRpg.slnx -c Debug --nologo", flat)
        self.assertIn("test tests/FusionRpg.Guard.Tests -c Debug --nologo --blame-hang-timeout 20m",
                      flat)
        self.assertTrue(any(line.startswith("test ") and "Alpha.csproj" in line and
                            line.endswith("--blame-hang-timeout 10m") for line in flat), flat)
        self.assertTrue(any("FusionRpg.Core.Tests.csproj" in line for line in flat), flat)
        self.assertTrue(all("-c Debug --nologo" in line for line in flat), flat)

    def test_the_blame_hang_flag_is_still_passed_so_the_inner_guard_survives(self) -> None:
        # The outer budget is new; dotnet's own hang guard is not a substitute for it, and removing
        # it would be a behaviour change in the other direction.
        self.assertEqual(post_merge_check.BLAME_HANG_GUARDS, "20m")
        self.assertEqual(post_merge_check.BLAME_HANG_TESTS, "10m")
        self.assertGreater(post_merge_check.BUDGETS["guards"], 20 * 60)
        self.assertGreater(post_merge_check.BUDGETS["test"], 10 * 60)

    def test_every_stage_carries_a_positive_budget(self) -> None:
        for name, budget in post_merge_check.BUDGETS.items():
            with self.subTest(stage=name):
                self.assertGreater(budget, 0)


class TimeoutTests(unittest.TestCase):
    def test_a_hanging_child_is_killed_and_marked_rather_than_hanging_the_gate(self) -> None:
        # The retired form had no build timeout at all and leaned entirely on dotnet's blame-hang.
        sleeper = "ping -n 30 127.0.0.1 >nul" if os.name == "nt" else "sleep 30"
        if os.name == "nt":
            argv = ["cmd.exe", "/d", "/s", "/c", sleeper]
        else:
            argv = ["/bin/sh", "-c", sleeper]
        with tempfile.TemporaryDirectory() as temp:
            result = post_merge_check.run(argv, stage="probe", timeout=2, cwd=Path(temp))
        self.assertTrue(result.timed_out)
        self.assertEqual(result.returncode, 1)

    def test_a_clean_child_reports_its_own_output_and_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = post_merge_check.run([sys.executable, "-c", "print('hello')"],
                                          stage="probe", timeout=60, cwd=Path(temp))
        self.assertFalse(result.timed_out)
        self.assertEqual(result.returncode, 0)
        self.assertIn("hello", result.stdout)


# --------------------------------------------------------------------------------------------
# END TO END: the phase classifications, through a substituted runner
# --------------------------------------------------------------------------------------------

GREEN_BUILD = ["Build succeeded.", "    0 Warning(s)", "    0 Error(s)"]
GREEN_TEST = ["Passed!  - Failed: 0, Passed: 1, Total: 1"]


def standard_fixture(root: Path, projects: list[str] | None = None) -> None:
    """The declared surface, its projects and the legal-game evidence, all committed so the
    checkout proof has a clean tree to accept."""
    write_manifest(root, projects if projects is not None else ["Alpha"])
    make_test_projects(root, (projects or ["Alpha"]) + ["FusionRpg.Core.Tests"])
    legal_game_environment(root)
    commit_fixture(root, "declared test surface")


class PhaseClassificationTests(RepoCase):
    def setUp(self) -> None:
        super().setUp()
        init_repo(self.root)
        standard_fixture(self.root)
        self.legal = legal_game_environment(self.root)

    def run_gate_with(self, results, **kwargs):
        return run_in_process(self.root, results, env_overrides=self.legal, **kwargs)

    def test_a_clean_run_is_green(self) -> None:
        code, envelope, _calls, out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertEqual(envelope["verdict"], "GREEN", out)
        self.assertEqual(code, 0)
        self.assertIn("=== VERDICT: GREEN ===", out)
        self.assertIn(f"branch=features/mega-merge", out)

    def test_a_zero_exit_with_a_failed_summary_is_red(self) -> None:
        for kind, needle in (("build", "build: failed summary"), ("guard", "guards: failed summary"),
                             ("test", "failed summary")):
            with self.subTest(kind=kind):
                results = {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                           "test": (GREEN_TEST, 0)}
                results[kind] = (["Failed!  - Failed: 1, Passed: 0"], 0)
                code, envelope, _calls, out = self.run_gate_with(results)
                self.assertTrue(envelope["verdict"].startswith("RED -- "), out)
                self.assertIn(needle, envelope["verdict"])
                self.assertEqual(code, 1)

    def test_a_zero_test_count_is_red(self) -> None:
        results = {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)}
        results["guard"] = (["Passed!  - Failed: 0, Passed: 0, Total: 0"], 0)
        _code, envelope, _calls, _out = self.run_gate_with(results)
        self.assertIn("guards-zero-tests", envelope["verdict"])

    def test_a_missing_summary_is_red(self) -> None:
        results = {"build": (GREEN_BUILD, 0), "guard": (["the command ran"], 0),
                   "test": (GREEN_TEST, 0)}
        _code, envelope, _calls, _out = self.run_gate_with(results)
        self.assertIn("guards-no-summary", envelope["verdict"])

    def test_a_build_without_a_success_summary_is_red(self) -> None:
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (["Build completed."], 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("build-no-success-summary", envelope["verdict"])

    def test_a_red_build_reports_the_project_error(self) -> None:
        # A solution-level error line carries no `[X.csproj]`, so the retired reader names it
        # `unknown` -- and still calls it a non-interop RED. That is the fail-closed direction.
        _code, envelope, _calls, out = self.run_gate_with(
            {"build": (["Solution.cs : error CS1001: unrelated solution failure"], 1),
             "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("build: non-interop project errors: unknown", envelope["verdict"])
        self.assertIn("error_lines=1", out)

    def test_a_bracketed_project_error_names_that_project(self) -> None:
        _code, envelope, _calls, out = self.run_gate_with(
            {"build": (["[FusionRpg.Server] : error CS1001: unrelated"], 1),
             "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        # Only a path ending in `.csproj` inside brackets is recognised; anything else is `unknown`.
        self.assertIn("build: non-interop project errors: unknown", envelope["verdict"])
        _code, envelope, _calls, out = self.run_gate_with(
            {"build": (["[src/FusionRpg.Server/FusionRpg.Server.csproj] : error CS1001: x"], 1),
             "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("build: non-interop project errors: FusionRpg.Server.csproj",
                      envelope["verdict"])
        self.assertIn("1  FusionRpg.Server.csproj", out)

    def test_a_nonzero_build_with_no_classifiable_error_is_still_red(self) -> None:
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 3), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("build: dotnet exited 3 without a classifiable project error",
                      envelope["verdict"])

    def test_an_interop_only_build_error_is_recorded_as_blocked_evidence(self) -> None:
        """A gap in the retired gate, measured rather than inherited on trust.

        `test_interop_build_limitation_is_blocked_not_green` in test_fail_closed_pipeline.py is
        named as though an interop limitation yields BLOCKED. It does not. A build that emits an
        interop project error has, by definition, emitted no 'Build succeeded' line, so
        `build-no-success-summary` fires as well and the verdict is RED. The interop fact IS
        recorded -- in the blocked list -- but the verdict never reaches BLOCKED, because RED
        outranks BLOCKED. The retired test passes only because it asserts neither the verdict nor
        the exit code.

        This is the fail-closed direction, so the behaviour is PRESERVED exactly. Recorded here
        because the retired test's name is misleading and someone will otherwise trust it.
        """
        _code, envelope, _calls, out = self.run_gate_with(
            {"build": (["[FusionRpg.Injector.BepInEx.csproj] : error : legal game directory is "
                        "missing"], 1), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("legal-game/interops build unavailable: FusionRpg.Injector.BepInEx.csproj",
                      envelope["blocked"])
        self.assertIn("FusionRpg.Injector.BepInEx.csproj", out)
        self.assertTrue(envelope["verdict"].startswith("RED -- "), envelope["verdict"])
        self.assertIn("build-no-success-summary", envelope["verdict"])
        self.assertNotIn("build: non-interop project errors", envelope["verdict"])

    def test_a_successful_build_with_absent_legal_evidence_is_blocked_not_red(self) -> None:
        # The reachable BLOCKED path: the build itself is fine, the interop evidence is absent.
        _code, envelope, _calls, _out = run_in_process(
            self.root, {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                        "test": (GREEN_TEST, 0)},
            env_overrides={"FUSIONRPG_GAME_DIR": "", "FUSIONRPG_ML_GAMEDIR": ""})
        self.assertTrue(envelope["verdict"].startswith("BLOCKED -- "), envelope["verdict"])
        self.assertEqual(envelope["failures"], [])

    def test_mixed_interop_and_product_errors_are_red(self) -> None:
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (["[FusionRpg.Injector.BepInEx.csproj] : error : missing",
                        "[src/FusionRpg.Server/FusionRpg.Server.csproj] : error CS1001: x"], 1),
             "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("build: non-interop project errors: FusionRpg.Server.csproj",
                      envelope["verdict"])
        # The interop project is ALSO reported as blocked evidence: both facts are true at once.
        self.assertIn("legal-game/interops build unavailable: FusionRpg.Injector.BepInEx.csproj",
                      envelope["blocked"])

    def test_skipping_the_build_is_blocked_not_green(self) -> None:
        _code, envelope, _calls, out = self.run_gate_with(
            {"guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)}, skip_build=True)
        self.assertTrue(envelope["verdict"].startswith("BLOCKED -- "), out)
        self.assertIn("build skipped by request", envelope["verdict"])

    def test_skipping_the_guards_is_blocked_not_green(self) -> None:
        _code, envelope, _calls, out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "test": (GREEN_TEST, 0)}, skip_guards=True)
        self.assertTrue(envelope["verdict"].startswith("BLOCKED -- "), out)
        self.assertIn("Guard suite skipped by request", envelope["verdict"])

    def test_missing_legal_game_evidence_is_blocked_not_green(self) -> None:
        code, envelope, _calls, out = run_in_process(
            self.root, {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                        "test": (GREEN_TEST, 0)},
            env_overrides={"FUSIONRPG_GAME_DIR": "", "FUSIONRPG_ML_GAMEDIR": ""})
        self.assertTrue(envelope["verdict"].startswith("BLOCKED -- "), out)
        self.assertIn("FUSIONRPG_ML_GAMEDIR", envelope["verdict"])
        self.assertEqual(code, 1, "BLOCKED is never a zero exit")

    def test_a_nonzempty_but_invalid_legal_path_is_blocked_and_named(self) -> None:
        missing = str(self.root / "not-a-real-game")
        _code, envelope, _calls, _out = run_in_process(
            self.root, {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                        "test": (GREEN_TEST, 0)},
            env_overrides={"FUSIONRPG_GAME_DIR": missing, "FUSIONRPG_ML_GAMEDIR": missing})
        self.assertIn("not-a-real-game", envelope["verdict"])

    def test_a_nonzero_guard_run_is_red(self) -> None:
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (["Failed!  - Failed: 1, Passed: 0"], 1),
             "test": (GREEN_TEST, 0)})
        self.assertIn("guards: dotnet test exited 1", envelope["verdict"])
        self.assertIn("guards-suspect-contention", envelope["verdict"])

    def test_a_nonzero_test_run_names_the_project(self) -> None:
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
             "test": (["Failed!  - Failed: 1, Passed: 0"], 1)})
        self.assertIn("test: Alpha exited 1", envelope["verdict"])

    def test_a_malformed_manifest_is_red(self) -> None:
        (self.root / "tests" / "core-test-projects.v1.json").write_text("{", encoding="utf-8")
        commit_fixture(self.root, "malformed manifest")
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)},
            skip_build=True, skip_guards=True)
        self.assertIn("declared-test-manifest-invalid", envelope["verdict"])

    def test_an_empty_declared_surface_is_red(self) -> None:
        write_manifest(self.root, [], residual="")
        commit_fixture(self.root, "empty declared surface")
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)},
            skip_build=True, skip_guards=True)
        self.assertIn("declared-test-manifest-empty", envelope["verdict"])

    def test_a_missing_explicit_project_is_red(self) -> None:
        _code, envelope, _calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)},
            projects=["tests/Absent"])
        self.assertIn("test-project-missing: tests/Absent", envelope["verdict"])

    def test_the_declared_surface_cannot_be_replaced_by_an_explicit_list(self) -> None:
        make_test_projects(self.root, ["Beta"])
        commit_fixture(self.root, "an extra project")
        _code, _envelope, calls, _out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)},
            projects=["tests/Beta"])
        flat = [" ".join(call) for call in calls]
        self.assertTrue(any("Alpha.csproj" in line for line in flat), flat)
        self.assertTrue(any("FusionRpg.Core.Tests.csproj" in line for line in flat), flat)
        self.assertTrue(any("Beta.csproj" in line for line in flat), flat)

    def test_the_artefact_free_transcript_reports_the_head_and_the_project_list(self) -> None:
        _code, envelope, _calls, out = self.run_gate_with(
            {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0), "test": (GREEN_TEST, 0)})
        self.assertIn("dotnet=", out)
        self.assertIn("post-merge check  HEAD=", out)
        self.assertIn("=== build FusionRpg.slnx", out)
        self.assertIn("=== Guard suite ===", out)
        self.assertIn("STARTED=", out)
        self.assertIn("FINISHED=", out)
        self.assertEqual(envelope["head"], git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(envelope["branch"], "features/mega-merge")
        self.assertEqual(len(envelope["testProjects"]), 2)

    def test_the_gate_never_writes_into_the_repository(self) -> None:
        # The retired form wrote .tmp-post-merge-build.txt INSIDE the tree and removed it in a
        # `finally`; a killed run left it, and every later run then refused on a dirty tree. The
        # build transcript now lives in the OS temp directory.
        self.run_gate_with({"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                            "test": (GREEN_TEST, 0)})
        self.assertEqual(git(self.root, "status", "--porcelain"), "")
        self.assertFalse((self.root / ".tmp-post-merge-build.txt").exists())


class JsonEnvelopeTests(RepoCase):
    def test_a_refusal_envelope_names_its_stage_and_code(self) -> None:
        init_repo(self.root)
        result = run_gate(self.root, "--repo", str(self.root),
                          "--dotnet", str(self.root / "no-such-dotnet"), "--json")
        envelope = json.loads(result.stdout)          # stdout must parse on its own
        self.assertFalse(envelope["ok"])
        self.assertEqual(envelope["stage"], "dotnet")
        self.assertEqual(envelope["exitCode"], 9)
        self.assertIn("dotnet not found", envelope["refusal"])
        self.assertIsNone(envelope["verdict"])
        self.assertIn("refused at stage 'dotnet'", result.stderr)

    def test_a_verdict_envelope_carries_the_whole_reading(self) -> None:
        init_repo(self.root)
        standard_fixture(self.root)
        _code, envelope, _calls, _out = run_in_process(
            self.root, {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                        "test": (GREEN_TEST, 0)},
            env_overrides=legal_game_environment(self.root))
        self.assertEqual(envelope["verdict"], "GREEN")
        self.assertEqual(envelope["ran"], 4)          # build + guards + Alpha + residual
        self.assertEqual(envelope["failures"], [])
        self.assertEqual(envelope["blocked"], [])
        self.assertEqual(envelope["head"], git(self.root, "rev-parse", "HEAD"))


# --------------------------------------------------------------------------------------------
# DIFFERENTIAL: the retired PowerShell, while it still exists
# --------------------------------------------------------------------------------------------

@unittest.skipUnless(PS_MODULE_PATH.is_file(), "post-merge-check.ps1 has been removed by the port")
class DifferentialAgainstPowerShellTests(RepoCase):
    """The verdict vocabulary is the contract, so it is compared line for line."""

    def ps_run(self, *args: str) -> subprocess.CompletedProcess[str]:
        def quoted(value: str) -> str:
            return "'" + str(value).replace("'", "''") + "'"

        # Parameter NAMES must stay unquoted: PowerShell binds a quoted '-Repo' POSITIONALLY.
        command = f"& '{PS_MODULE_PATH}' -Repo {quoted(str(self.root))} -Dotnet {quoted(sys.executable)}"
        for index, value in enumerate(args):
            switch = "-SkipBuild" if value == "--skip-build" else (
                "-SkipGuards" if value == "--skip-guards" else None)
            if switch:
                command += f" {switch}"
            elif value.startswith("--"):
                continue
            else:
                command += f" -TestProject {quoted(value)}"
        return subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
                              cwd=self.root, capture_output=True, text=True, timeout=300,
                              check=False)

    @staticmethod
    def verdicts(stdout: str) -> list[str]:
        return [re.sub(r"[A-Za-z]:\\[^\s']*", "<path>", line)
                for line in stdout.splitlines() if line.startswith("=== VERDICT:")]

    def setUp(self) -> None:
        super().setUp()
        init_repo(self.root)
        standard_fixture(self.root)

    def test_the_precondition_refusal_matches(self) -> None:
        # The refusal TEXT is the contract. Exit codes are compared only as far as the retired
        # invocation can express them: "pwsh -Command" with a call operator collapses every
        # non-zero script exit to 1, so the retired 9 was never observable on this path. See the
        # matching test in test_accept_lane.py, which pins that pwsh behaviour.
        git(self.root, "checkout", "-q", "-b", "not-the-integration-branch")
        mine = self.gate("--skip-build", "--skip-guards")
        theirs = self.ps_run("--skip-build", "--skip-guards")
        self.assertNotIn("Cannot validate argument", theirs.stderr)
        self.assertNotEqual(mine.returncode, 0, mine.stdout + mine.stderr)
        self.assertNotEqual(theirs.returncode, 0, theirs.stdout + theirs.stderr)
        self.assertIn("merged-head check must run on 'features/mega-merge'", mine.stdout)
        self.assertIn("merged-head check must run on 'features/mega-merge'", theirs.stdout)
        self.assertNotIn("VERDICT", mine.stdout)
        self.assertNotIn("VERDICT", theirs.stdout)

    def test_the_verdict_line_shape_matches(self) -> None:
        code, envelope, _calls, out = run_in_process(
            self.root, {"build": (GREEN_BUILD, 0), "guard": (GREEN_TEST, 0),
                        "test": (GREEN_TEST, 0)},
            env_overrides=legal_game_environment(self.root))
        self.assertTrue(self.verdicts(out), out)
        self.assertTrue(self.verdicts(out)[0].startswith("=== VERDICT: GREEN ==="))


if __name__ == "__main__":
    unittest.main(verbosity=2)
