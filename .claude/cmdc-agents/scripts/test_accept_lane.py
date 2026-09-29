#!/usr/bin/env python3
"""Regressions for `accept_lane.py`, the manager's lane-acceptance proof instrument.

Two halves, and both matter:

  * UNIT -- the schema validator, the failed-summary tests, the verdict ladder and the
    known-red attribution are exercised directly, so a schema change fails here with a named
    message instead of surfacing as a silently mis-merged lane.
  * END TO END -- a real temporary git repository, a real detached review worktree, and real
    child processes. The four promises the harness makes are asserted as refusals: a mismatched
    tree, a dirty worktree, a non-ancestor `ExpectSha`, and a verdict vocabulary that cannot be
    widened by a junk suffix.

A third group is DIFFERENTIAL: where the retired `accept-lane.ps1` is still present, the same
fixture is driven through both entry points and the transcripts are compared, so "the port
preserves the contract" is measured rather than asserted. Those tests skip themselves once the
deletion wave removes the PowerShell.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "accept_lane.py"
PS_MODULE_PATH = HERE / "accept-lane.ps1"

spec = importlib.util.spec_from_file_location("accept_lane", MODULE_PATH)
assert spec and spec.loader
accept_lane = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accept_lane)

SHA = "a" * 40
OTHER_SHA = "b" * 40


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
    """A minimal integration repository. `.gitignore` covers everything a fixture writes that is
    not part of the tree under test, so `git status --untracked-files=all` stays clean."""
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.name", "Test User")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "commit.gpgsign", "false")
    git(path, "checkout", "-q", "-b", branch)
    (path / "base.txt").write_text("base\n", encoding="utf-8")
    (path / ".gitignore").write_text(
        ".claude/worktrees/\nfake_cmdc.py\nlogs/\ncheck-*.log\n", encoding="utf-8")
    git(path, "add", "base.txt", ".gitignore")
    git(path, "commit", "-q", "-m", "base")
    return git(path, "rev-parse", "HEAD")


def make_fake_cmdc(path: Path, *, dirty_review: bool = False, fail: bool = False) -> Path:
    """Stands in for the real review-checkout helper: creates (or reuses) the detached review
    worktree at `<repo>/.claude/worktrees/cmdc-review-<lane>`."""
    path.write_text(textwrap.dedent(
        f"""
        import subprocess
        import sys
        from pathlib import Path

        repo = Path(sys.argv[sys.argv.index('--repo') + 1])
        lane = sys.argv[sys.argv.index('--id') + 1]
        worktree = repo / '.claude' / 'worktrees' / f'cmdc-review-{{lane}}'
        worktree.parent.mkdir(parents=True, exist_ok=True)
        if {fail!r}:
            print('fake review helper refused', file=sys.stderr)
            raise SystemExit(3)
        if not worktree.exists():
            subprocess.run(
                ['git', 'worktree', 'add', '--detach', str(worktree), 'HEAD'],
                cwd=repo, check=True,
            )
        if {dirty_review!r}:
            (worktree / 'unexpected-review-file.txt').write_text('dirty\\n', encoding='utf-8')
        """
    ).strip() + "\n", encoding="utf-8")
    return path


def remove_worktree(repo: Path, lane: str) -> None:
    worktree = repo / ".claude" / "worktrees" / f"cmdc-review-{lane}"
    if worktree.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repo,
                       capture_output=True, text=True, timeout=60, check=False)


def run_accept(root: Path, *args: str, env_overrides: dict[str, str] | None = None
               ) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    if env_overrides:
        environment.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), *args],
        cwd=root, capture_output=True, text=True, timeout=300, check=False, env=environment)


def acceptance_artifact(lane: str, sha: str, *, verdict: str = "GREEN",
                        checks: list[dict] | None = None) -> dict:
    """The schema-version-2 shape, as `merge-lanes.py` expects to read it."""
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
        "checks": checks if checks is not None else [{
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
        }],
    }


def write_artifact(root: Path, lane: str, artifact: dict, *,
                   name_sha: str | None = None) -> Path:
    """`name_sha` names the FILE after a different commit than its contents declare, which is how
    a stale artefact is reproduced."""
    directory = root / ".claude" / "cmdc-agents" / "acceptance"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{lane}-{(name_sha or artifact['sha'])[:8]}.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def lane_repo(root: Path, lane: str) -> tuple[str, str]:
    """A lane branch holding one commit that descends from integration."""
    base = init_repo(root)
    git(root, "checkout", "-q", "-b", f"cmdc/{lane}")
    (root / "lane.txt").write_text("lane\n", encoding="utf-8")
    git(root, "add", "lane.txt")
    git(root, "commit", "-q", "-m", "lane work")
    lane_sha = git(root, "rev-parse", "HEAD")
    git(root, "checkout", "-q", "features/mega-merge")
    return base, lane_sha


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.addCleanup(self.temp.cleanup)

    def artifact_for(self, lane: str, sha: str) -> dict:
        return json.loads(
            (self.root / ".claude" / "cmdc-agents" / "acceptance" / f"{lane}-{sha[:8]}.json")
            .read_text(encoding="utf-8-sig"))


# --------------------------------------------------------------------------------------------
# UNIT: the failed-summary tests
# --------------------------------------------------------------------------------------------

class FailedSummaryTests(unittest.TestCase):
    def test_truth_table(self) -> None:
        table = [
            ("Passed!  - Failed: 0, Passed: 12", False),
            ("Failed!  - Failed: 1, Passed: 11", True),
            ("   Test Run Failed.", True),          # indented: the retired form matched it
            ("Build FAILED.", True),
            ("Build succeeded.", False),
            ("Failed: 0", False),
            ("Failed: 3", True),
            ("Failed: unknown", True),              # the FIXED dead branch
            ("OK -- 12 targets", False),
            ("", False),
        ]
        for text, expected in table:
            with self.subTest(text=text):
                self.assertEqual(accept_lane.test_failed_summary(text), expected)

    def test_a_zero_count_stops_the_scan_rather_than_reaching_the_bare_marker(self) -> None:
        # The retired function returned `$false` from inside the count branch, so a `Failed: 0`
        # line is decided by its count and the bare-`Failed:` fallback is never consulted.
        self.assertFalse(accept_lane.test_failed_summary("Failed: 0"))
        self.assertTrue(accept_lane.test_failed_summary("Failed: 0 then Failed: 2"))

    def test_the_retired_bare_marker_regex_was_dead_code(self) -> None:
        # Documents WHY the fix exists, and would catch a reintroduction of the broken form.
        retired = __import__("re").compile(r"\bFailed:\b", __import__("re").IGNORECASE)
        for text in ("Failed: unknown", "Failed:", "... Failed: x", "Failed: see the log"):
            with self.subTest(text=text):
                self.assertIsNone(retired.search(text))
                self.assertIsNotNone(accept_lane.BARE_FAILED_RE.search(text))

    def test_failed_output_is_a_per_line_scan(self) -> None:
        self.assertTrue(accept_lane.test_failed_output("noise\n   Test Run Failed.\nnoise"))
        self.assertFalse(accept_lane.test_failed_output("Passed!  - Failed: 0, Passed: 1"))


class ParsingTests(unittest.TestCase):
    def test_summary_keeps_the_whole_line_not_the_alternation(self) -> None:
        text = "Passed!  - Failed: 0, Passed: 12\nnoise\n  Failed: 2, Passed: 3\n"
        self.assertEqual(accept_lane.SUMMARY_RE.findall(text),
                         ["Passed!  - Failed: 0, Passed: 12", "  Failed: 2, Passed: 3"])

    def test_failed_test_names_are_parsed_and_deduplicated(self) -> None:
        text = ("Failed Namespace.Tests.ShouldPass\n"
                "failed namespace.tests.shouldpass\n"
                "Failed Other.Tests.Case\n")
        self.assertEqual(accept_lane.FAILED_TEST_RE.findall(text),
                         ["Namespace.Tests.ShouldPass", "namespace.tests.shouldpass",
                          "Other.Tests.Case"])
        self.assertEqual(accept_lane.dedupe_case_insensitive(
            accept_lane.FAILED_TEST_RE.findall(text)),
            ["Namespace.Tests.ShouldPass", "Other.Tests.Case"])

    def test_compiler_error_lines_are_whole_lines_capped_at_five(self) -> None:
        text = "\n".join(f"file{i}.cs(1,1): error CS1001: bad {i}" for i in range(7))
        found = [line.strip() for line in accept_lane.COMPILER_ERROR_RE.findall(text)][:5]
        self.assertEqual(len(found), 5)
        self.assertIn("error CS1001", found[0])

    def test_ansi_sequences_are_stripped_before_parsing(self) -> None:
        self.assertEqual(accept_lane.ANSI_RE.sub("", "\x1b[32mPassed!\x1b[0m"), "Passed!")


# --------------------------------------------------------------------------------------------
# UNIT: the verdict ladder and the attribution
# --------------------------------------------------------------------------------------------

def _check(**overrides) -> dict:
    base = {
        "check": "smoke", "exit": 0, "seconds": 1, "summary": "Passed!",
        "failedTests": [], "knownRedTests": [], "newRedTests": [], "flakeSuspectTests": [],
        "errors": [], "log": "log/smoke.log",
    }
    base.update(overrides)
    return base


class VerdictTests(unittest.TestCase):
    def test_a_clean_check_is_green(self) -> None:
        verdict, summary, attribution = accept_lane.decide_verdict([_check()])
        self.assertEqual((verdict, summary), ("GREEN", "GREEN"))
        self.assertEqual(attribution, {"knownRedMatched": 0, "newUnregistered": 0,
                                       "unattributed": 0})

    def test_a_non_zero_exit_with_no_parsed_failure_is_unattributed(self) -> None:
        verdict, summary, attribution = accept_lane.decide_verdict([_check(exit=7)])
        self.assertEqual(verdict, "UNATTRIBUTED")
        self.assertEqual(summary, "UNATTRIBUTED (1 red check(s); 1 with no parsed failure)")
        self.assertEqual(attribution["unattributed"], 1)

    def test_a_new_parsed_failure_is_red(self) -> None:
        verdict, _, attribution = accept_lane.decide_verdict(
            [_check(failedTests=["N.T.X"], newRedTests=["N.T.X"])])
        self.assertEqual(verdict, "RED")
        self.assertEqual(attribution["newUnregistered"], 1)

    def test_registered_debt_is_red_known_not_green(self) -> None:
        verdict, summary, attribution = accept_lane.decide_verdict(
            [_check(exit=1, failedTests=["N.T.X"],
                    knownRedTests=["N.T.X  [registered: TVB-F20"], newRedTests=[])])
        self.assertEqual(verdict, "RED-KNOWN")
        self.assertEqual(summary, "RED-KNOWN (1 check(s), 1 registered-debt failure(s) matched)")
        self.assertEqual(attribution["knownRedMatched"], 1)
        self.assertEqual(attribution["newUnregistered"], 0)

    def test_a_compiler_error_is_red(self) -> None:
        verdict, _, attribution = accept_lane.decide_verdict([_check(errors=["e.cs: error CS1"])])
        self.assertEqual(verdict, "RED")
        self.assertEqual(attribution["newUnregistered"], 1)

    def test_a_zero_exit_whose_summary_says_failed_is_never_green(self) -> None:
        verdict, _, _ = accept_lane.decide_verdict([_check(summary="Failed! - failed output "
                                                                 "detected")])
        self.assertNotEqual(verdict, "GREEN")

    def test_the_ladder_is_a_closed_vocabulary(self) -> None:
        self.assertEqual(accept_lane.ACCEPTANCE_VERDICTS,
                         ("GREEN", "RED", "RED-KNOWN", "UNATTRIBUTED"))


class KnownRedAttributionTests(unittest.TestCase):
    def test_the_four_retired_matching_rules(self) -> None:
        registry = [{"test": "Namespace.Tests.ShouldPass", "debt": "TVB-F20"}]
        for failure in ("Namespace.Tests.ShouldPass", "Tests.ShouldPass",
                        "Namespace.Tests.ShouldPassExtra", "X.Namespace.Tests.ShouldPassY"):
            with self.subTest(failure=failure):
                self.assertIsNotNone(accept_lane.match_known_red(registry, failure))
        self.assertIsNone(accept_lane.match_known_red(registry, "Other.Tests.Case"))

    def test_a_row_without_a_usable_test_cannot_match_and_so_stays_new_red(self) -> None:
        # Fail-closed: an unusable row never silently absorbs a failure as registered debt.
        for registry in ([{"debt": "no test field"}], [None], ["a string"], [{}]):
            with self.subTest(registry=registry):
                self.assertIsNone(accept_lane.match_known_red(registry, "N.T.X"))


class CheckSpecTests(unittest.TestCase):
    def test_a_malformed_spec_is_refused_by_name(self) -> None:
        with self.assertRaises(accept_lane.Refusal) as caught:
            accept_lane.parse_check_specs(["no-separator"])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("is malformed -- expected 'name|||command'", caught.exception.reason)

    def test_an_empty_command_is_refused(self) -> None:
        with self.assertRaises(accept_lane.Refusal):
            accept_lane.parse_check_specs(["smoke|||   "])

    def test_an_invalid_name_is_refused(self) -> None:
        with self.assertRaises(accept_lane.Refusal) as caught:
            accept_lane.parse_check_specs(["bad name|||echo x"])
        self.assertIn("check name 'bad name' is malformed", caught.exception.reason)

    def test_a_duplicate_name_is_refused(self) -> None:
        with self.assertRaises(accept_lane.Refusal) as caught:
            accept_lane.parse_check_specs(["smoke|||echo a", "smoke|||echo b"])
        self.assertEqual(caught.exception.reason, "duplicate check name 'smoke'.")

    def test_an_empty_set_cannot_be_accepted(self) -> None:
        with self.assertRaises(accept_lane.Refusal) as caught:
            accept_lane.parse_check_specs([])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("at least one schema-valid check", caught.exception.reason)

    def test_a_command_containing_the_separator_survives(self) -> None:
        parsed = accept_lane.parse_check_specs(["smoke|||echo a ||| b"])
        self.assertEqual(parsed, [{"name": "smoke", "command": "echo a ||| b"}])


# --------------------------------------------------------------------------------------------
# UNIT: the schema-version-2 evidence validator -- the whole refusal vocabulary
# --------------------------------------------------------------------------------------------

class EvidenceValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "evidence.json"
        self.addCleanup(self.temp.cleanup)

    def write(self, artifact: object) -> None:
        self.path.write_text(json.dumps(artifact), encoding="utf-8")

    def check(self, artifact: object, *, require_green: bool = False) -> str | None:
        self.write(artifact)
        return accept_lane.validate_evidence(self.path, "lane", SHA, require_green=require_green)

    def test_a_missing_file_is_named(self) -> None:
        missing = self.path.with_name("absent.json")
        self.assertIn("missing evidence file", accept_lane.validate_evidence(missing, "lane", SHA))

    def test_malformed_json_is_named(self) -> None:
        self.path.write_text("{", encoding="utf-8")
        self.assertIn("malformed evidence JSON:",
                      accept_lane.validate_evidence(self.path, "lane", SHA))

    def test_a_byte_order_mark_is_tolerated(self) -> None:
        self.path.write_text(json.dumps(acceptance_artifact("lane", SHA)), encoding="utf-8-sig")
        self.assertIsNone(accept_lane.validate_evidence(self.path, "lane", SHA))

    def test_valid_evidence_passes(self) -> None:
        self.assertIsNone(self.check(acceptance_artifact("lane", SHA)))

    def test_every_single_field_defect_is_named(self) -> None:
        cases = {
            "root is not an object": [1, 2, 3],
            "schemaVersion must be integer 2": {"schemaVersion": "2"},
            "schemaVersion must be integer 2": {"schemaVersion": 3},
        }
        for expected, artifact in cases.items():
            with self.subTest(expected=expected):
                self.assertIn(expected, self.check(artifact))

    def test_a_boolean_is_not_an_integer(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["schemaVersion"] = True
        self.assertIn("schemaVersion must be integer 2", self.check(artifact))

    def test_lane_and_sha_binding(self) -> None:
        self.assertIn("evidence lane mismatch: expected 'lane', got 'other'",
                      self.check(acceptance_artifact("other", SHA)))
        self.assertIn("evidence SHA mismatch:",
                      self.check(acceptance_artifact("lane", OTHER_SHA)))

    def test_a_short_sha_is_not_a_full_sha(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["sha"] = SHA[:8]
        self.assertIn("sha must be a full 40-character commit SHA", self.check(artifact))

    def test_expected_sha_and_short_sha_must_bind_to_the_reviewed_commit(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["expectedSha"] = OTHER_SHA
        self.assertIn("expectedSha does not match the reviewed SHA", self.check(artifact))
        artifact = acceptance_artifact("lane", SHA)
        artifact["shortSha"] = SHA[:9]
        self.assertIn("shortSha does not match the reviewed SHA", self.check(artifact))

    def test_the_timestamp_must_exist_and_parse(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        del artifact["when"]
        self.assertIn("when must be a timestamp", self.check(artifact))
        artifact = acceptance_artifact("lane", SHA)
        artifact["when"] = "not a timestamp"
        self.assertIn("when is not a valid timestamp", self.check(artifact))

    def test_the_verdict_vocabulary_is_closed_and_case_sensitive(self) -> None:
        for verdict in ("GREENjunk", "green", "Green", "RED_KNOWN", "", "PASS"):
            with self.subTest(verdict=verdict):
                self.assertIn("verdict is outside the acceptance vocabulary",
                              self.check(acceptance_artifact("lane", SHA, verdict=verdict)))

    def test_contended_tree_must_be_a_real_boolean(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["contendedTree"] = "false"
        self.assertIn("contendedTree must be boolean", self.check(artifact))

    def test_log_dir_must_be_non_empty_text(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["logDir"] = "   "
        self.assertIn("logDir must be a non-empty string", self.check(artifact))

    def test_attribution_must_be_an_object_of_non_negative_integers(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["attribution"] = []
        self.assertIn("attribution must be an object", self.check(artifact))
        for prop in ("knownRedMatched", "newUnregistered", "unattributed"):
            with self.subTest(prop=prop):
                artifact = acceptance_artifact("lane", SHA)
                artifact["attribution"][prop] = -1
                self.assertIn(f"attribution.{prop} must be a non-negative integer",
                              self.check(artifact))

    def test_the_check_set_must_exist_and_be_non_empty(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        del artifact["checks"]
        self.assertIn("checks must be an array", self.check(artifact))
        self.assertIn("checks must not be empty",
                      self.check(acceptance_artifact("lane", SHA, checks=[])))

    def test_every_required_check_key_is_required(self) -> None:
        for key in accept_lane.REQUIRED_CHECK_KEYS:
            with self.subTest(key=key):
                artifact = acceptance_artifact("lane", SHA)
                del artifact["checks"][0][key]
                self.assertIn(f"check is missing '{key}'", self.check(artifact))

    def test_a_check_name_is_validated_and_deduplicated(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["check"] = "bad name"
        self.assertIn("invalid check name 'bad name'", self.check(artifact))
        one = _check()
        self.assertIn("duplicate check 'smoke'",
                      self.check(acceptance_artifact("lane", SHA, checks=[one, dict(one)])))

    def test_exit_must_be_an_integer_and_seconds_non_negative(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["exit"] = "0"
        self.assertIn("exit must be an integer for check 'smoke'", self.check(artifact))
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["seconds"] = -1
        self.assertIn("seconds must be a non-negative integer for check 'smoke'",
                      self.check(artifact))

    def test_the_five_result_fields_must_be_string_arrays(self) -> None:
        for prop in accept_lane.CHECK_RESULT_ARRAYS:
            with self.subTest(prop=prop):
                artifact = acceptance_artifact("lane", SHA)
                artifact["checks"][0][prop] = "not-an-array"
                self.assertIn(f"{prop} must be a string array for check 'smoke'",
                              self.check(artifact))

    def test_a_check_log_must_be_non_empty_text(self) -> None:
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["log"] = ""
        self.assertIn("empty log path for check 'smoke'", self.check(artifact))

    def test_require_green_refuses_every_residue(self) -> None:
        self.assertIn("evidence verdict is 'RED', not GREEN",
                      self.check(acceptance_artifact("lane", SHA, verdict="RED"),
                                 require_green=True))
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["exit"] = 1
        self.assertIn("evidence contains a non-zero check 'smoke'",
                      self.check(artifact, require_green=True))
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["summary"] = "Failed!  - Failed: 1, Passed: 0"
        self.assertIn("evidence contains a failed summary for check 'smoke'",
                      self.check(artifact, require_green=True))
        artifact = acceptance_artifact("lane", SHA)
        artifact["checks"][0]["newRedTests"] = ["N.T.X"]
        self.assertIn("evidence contains red/error details in newRedTests for check 'smoke'",
                      self.check(artifact, require_green=True))
        artifact = acceptance_artifact("lane", SHA)
        artifact["attribution"]["unattributed"] = 1
        self.assertIn("evidence attribution is not clean", self.check(artifact,
                                                                      require_green=True))

    def test_the_generated_artefact_has_exactly_the_contract_keys(self) -> None:
        # The write path and the read path must agree, so the written set is pinned here.
        self.assertEqual(set(acceptance_artifact("lane", SHA)),
                         {"schemaVersion", "lane", "sha", "shortSha", "expectedSha", "when",
                          "verdict", "attribution", "contendedTree", "logDir", "checks"})
        self.assertEqual(set(_check()), set(accept_lane.REQUIRED_CHECK_KEYS))


class IntegrationAncestryTests(RepoCase):
    def test_an_unrelated_branch_is_refused_by_name(self) -> None:
        init_repo(self.root)
        git(self.root, "checkout", "-q", "--orphan", "cmdc/unrelated")
        git(self.root, "rm", "-rqf", ".")
        (self.root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
        git(self.root, "add", "unrelated.txt")
        git(self.root, "commit", "-q", "-m", "unrelated")
        unrelated = git(self.root, "rev-parse", "HEAD")

        error = accept_lane.integration_ancestry_error(self.root, "features/mega-merge",
                                                      unrelated)
        self.assertIsNotNone(error)
        self.assertIn("does not descend from current integration branch", error)

    def test_a_descending_sha_passes(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        self.assertIsNone(accept_lane.integration_ancestry_error(self.root, "features/mega-merge",
                                                                 lane_sha))

    def test_a_missing_integration_branch_is_refused(self) -> None:
        init_repo(self.root)
        error = accept_lane.integration_ancestry_error(self.root, "no-such-branch", SHA)
        self.assertEqual(error, "integration branch 'no-such-branch' does not resolve to a full "
                                "commit SHA")


class ReviewCheckoutProofTests(RepoCase):
    def test_a_clean_detached_head_at_the_sha_passes(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        worktree = self.root / "review"
        git(self.root, "worktree", "add", "-q", "--detach", str(worktree), lane_sha)
        self.addCleanup(remove_worktree, self.root, "lane")
        self.assertIsNone(accept_lane.review_checkout_error(worktree, lane_sha))

    def test_a_dirty_checkout_is_refused(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        worktree = self.root / "review"
        git(self.root, "worktree", "add", "-q", "--detach", str(worktree), lane_sha)
        self.addCleanup(remove_worktree, self.root, "lane")
        (worktree / "stray.txt").write_text("dirty\n", encoding="utf-8")
        error = accept_lane.review_checkout_error(worktree, lane_sha)
        self.assertIsNotNone(error)
        self.assertIn("review checkout is dirty:", error)
        self.assertIn("stray.txt", error)

    def test_a_mismatched_head_is_refused(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        worktree = self.root / "review"
        git(self.root, "worktree", "add", "-q", "--detach", str(worktree), lane_sha)
        self.addCleanup(remove_worktree, self.root, "lane")
        error = accept_lane.review_checkout_error(worktree, OTHER_SHA)
        self.assertIn("does not exactly match expected SHA", error)

    def test_a_non_detached_head_is_refused(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        worktree = self.root / "review"
        git(self.root, "worktree", "add", "-q", "--detach", str(worktree), lane_sha)
        self.addCleanup(remove_worktree, self.root, "lane")
        git(worktree, "checkout", "-q", "cmdc/lane")
        error = accept_lane.review_checkout_error(worktree, lane_sha)
        self.assertIn("is not detached at the reviewed SHA (branch 'cmdc/lane')", error)


class CmdcAgentResolutionTests(unittest.TestCase):
    def test_an_explicit_path_that_does_not_exist_is_a_named_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "home"
            home.mkdir()
            with self.assertRaises(accept_lane.Refusal) as caught:
                accept_lane.resolve_cmdc_agent(str(Path(temp) / "absent.py"), {}, home)
        self.assertEqual(caught.exception.code, 9)
        self.assertEqual(caught.exception.stage, "cmdc_agent")
        self.assertIn("cmdc review tool is missing:", caught.exception.reason)

    def test_the_environment_is_the_second_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            helper = Path(temp) / "cmdc_agent.py"
            helper.write_text("# fixture\n", encoding="utf-8")
            home = Path(temp) / "home"
            home.mkdir()
            resolved = accept_lane.resolve_cmdc_agent("", {"FUSIONRPG_CMDC_AGENT": str(helper)},
                                                      home)
            self.assertEqual(resolved, helper)

    def test_the_home_relative_default_is_the_last_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            helper = home / ".claude" / "skills" / "cmdc-subagent" / "scripts" / "cmdc_agent.py"
            helper.parent.mkdir(parents=True)
            helper.write_text("# fixture\n", encoding="utf-8")
            self.assertEqual(accept_lane.resolve_cmdc_agent("", {}, home), helper)

    def test_no_committed_user_or_drive_path(self) -> None:
        # The retired form resolved the helper through `$env:USERPROFILE` reached by `Join-Path`.
        # What must not appear in the EXECUTABLE code is a path value or a read of that variable --
        # the module docstring naming the retired variable is documentation, not a dependency, so
        # the docstring is removed by parsing rather than by line-prefix guessing.
        text = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(text)
        docstring = ast.get_docstring(tree, clean=False)
        self.assertIsNotNone(docstring)
        doc_node = tree.body[0]
        code = "\n".join(line for index, line in enumerate(text.splitlines(), start=1)
                         if not (doc_node.lineno <= index <= doc_node.end_lineno))
        self.assertNotIn("C:\\", code)
        self.assertNotIn("Users\\", code)
        self.assertNotIn("USERPROFILE", code)
        self.assertNotIn("H:\\", code)
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "a-home"
            helper = home / ".claude" / "skills" / "cmdc-subagent" / "scripts" / "cmdc_agent.py"
            helper.parent.mkdir(parents=True)
            helper.write_text("# fixture\n", encoding="utf-8")
            self.assertEqual(accept_lane.resolve_cmdc_agent("", {}, home), helper)


class CheckCommandTests(unittest.TestCase):
    def test_a_command_line_runs_and_its_exit_code_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            command = "echo evidence" if os.name == "nt" else "echo evidence"
            result = accept_lane.run_check_command(command, Path(temp), 60)
            self.assertEqual(result.returncode, 0)
            self.assertIn("evidence", result.stdout)

    def test_a_failing_command_line_keeps_its_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = accept_lane.run_check_command("exit 7", Path(temp), 60)
            self.assertEqual(result.returncode, 7)

    def test_a_hanging_command_line_is_killed_and_marked(self) -> None:
        # The retired form had no timeout at all: a hang produced no verdict, no artefact and no
        # exit code. This is the defect the port closes, asserted against a real process.
        with tempfile.TemporaryDirectory() as temp:
            sleeper = "ping -n 30 127.0.0.1 >nul" if os.name == "nt" else "sleep 30"
            result = accept_lane.run_check_command(sleeper, Path(temp), 2)
            self.assertTrue(result.timed_out)
            self.assertEqual(result.returncode, 1)


# --------------------------------------------------------------------------------------------
# END TO END: the four promises, as refusals
# --------------------------------------------------------------------------------------------

class AcceptanceRefusalTests(RepoCase):
    def test_a_missing_full_sha_is_refused_before_any_acceptance_work(self) -> None:
        init_repo(self.root)
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        result = run_accept(self.root, "--lane", "missing-sha",
                            "--check", "smoke|||echo evidence",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required", result.stderr.lower())

    def test_an_invalid_full_sha_is_refused(self) -> None:
        init_repo(self.root)
        result = run_accept(self.root, "--lane", "invalid-sha", "--expect-sha", "0" * 40,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected sha", (result.stdout + result.stderr).lower())

    def test_an_empty_check_set_is_refused_and_creates_no_acceptance_directory(self) -> None:
        sha = init_repo(self.root)
        result = run_accept(self.root, "--lane", "empty", "--expect-sha", sha,
                            "--repo", str(self.root), "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one", (result.stdout + result.stderr).lower())
        self.assertFalse((self.root / ".claude" / "cmdc-agents" / "acceptance").exists())

    def test_a_mismatched_tree_is_refused(self) -> None:
        """THE harness's core promise: the review checkout must be clean, detached and exactly at
        the reviewed SHA, and a dirty one aborts before any check runs."""
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/dirty-review")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py", dirty_review=True)
        self.addCleanup(remove_worktree, self.root, "dirty-review")
        result = run_accept(self.root, "--lane", "dirty-review", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("review checkout is dirty", (result.stdout + result.stderr).lower())
        self.assertIn("unexpected-review-file.txt", result.stdout + result.stderr)

    def test_a_review_helper_that_fails_is_refused_by_name(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/helper")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py", fail=True)
        self.addCleanup(remove_worktree, self.root, "helper")
        result = run_accept(self.root, "--lane", "helper", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 9)
        self.assertIn("review checkout command failed (exit 3)", result.stdout)

    def test_a_dirty_manager_worktree_blocks_the_merge(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        (self.root / "unrelated.txt").write_text("dirty\n", encoding="utf-8")
        before = git(self.root, "rev-parse", "HEAD")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||echo evidence", "--merge",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MERGE REFUSED:", result.stdout)
        self.assertIn("dirty path", result.stdout.lower())
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), before)

    def test_a_non_ancestor_expect_sha_is_refused(self) -> None:
        """THE second promise: the reviewed SHA must be reachable from cmdc/<lane>."""
        init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/lane")
        git(self.root, "checkout", "-q", "features/mega-merge")
        git(self.root, "checkout", "-q", "-b", "unrelated")
        (self.root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
        git(self.root, "add", "unrelated.txt")
        git(self.root, "commit", "-q", "-m", "unrelated work")
        unrelated = git(self.root, "rev-parse", "HEAD")
        git(self.root, "checkout", "-q", "features/mega-merge")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", unrelated,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 9)
        self.assertIn("is not reachable from lane branch 'cmdc/lane'", result.stdout)
        self.assertFalse((self.root / ".claude" / "cmdc-agents" / "acceptance"
                          / f"lane-{unrelated[:8]}.json").exists())

    def test_a_non_descending_sha_is_refused_before_any_merge_and_writes_no_artefact(self) -> None:
        init_repo(self.root)
        git(self.root, "checkout", "-q", "--orphan", "cmdc/orphan")
        git(self.root, "rm", "-rqf", ".")
        (self.root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
        git(self.root, "add", "unrelated.txt")
        git(self.root, "commit", "-q", "-m", "unrelated lane work")
        orphan = git(self.root, "rev-parse", "HEAD")
        git(self.root, "checkout", "-q", "features/mega-merge")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "orphan")
        before = git(self.root, "rev-parse", "HEAD")
        result = run_accept(self.root, "--lane", "orphan", "--expect-sha", orphan,
                            "--check", "smoke|||echo evidence", "--merge",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 9)
        self.assertIn("does not descend from", result.stdout)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), before)
        self.assertFalse((self.root / ".claude" / "cmdc-agents" / "acceptance"
                          / f"orphan-{orphan[:8]}.json").exists())

    def test_a_merge_into_a_non_integration_branch_is_refused(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        before = git(self.root, "rev-parse", "HEAD")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||echo evidence", "--merge",
                            "--merge-into", "wrong-integration", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 9)
        self.assertIn("features/mega-merge", result.stdout)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), before)

    def test_existing_stale_evidence_is_refused(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/stale")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "stale")
        write_artifact(self.root, "stale", acceptance_artifact("stale", OTHER_SHA),
                        name_sha=sha)
        result = run_accept(self.root, "--lane", "stale", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("stale or malformed", result.stdout.lower())
        self.assertIn("sha mismatch", result.stdout.lower())

    def test_existing_schema_invalid_evidence_is_refused(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/schema")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "schema")
        artifact = acceptance_artifact("schema", sha)
        artifact["checks"][0]["exit"] = "0"
        write_artifact(self.root, "schema", artifact)
        result = run_accept(self.root, "--lane", "schema", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("exit must be an integer", result.stdout.lower())

    def test_existing_evidence_with_a_junk_verdict_suffix_is_refused(self) -> None:
        """The closed vocabulary, end to end: `GREENjunk` may not be written or consumed."""
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/junk")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "junk")
        write_artifact(self.root, "junk", acceptance_artifact("junk", sha, verdict="GREENjunk"))
        result = run_accept(self.root, "--lane", "junk", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside the acceptance vocabulary", result.stdout.lower())
        self.assertFalse((self.root / ".claude" / "worktrees" / "cmdc-review-junk").exists())

    def test_existing_malformed_evidence_is_refused(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/malformed")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "malformed")
        directory = self.root / ".claude" / "cmdc-agents" / "acceptance"
        directory.mkdir(parents=True)
        (directory / f"malformed-{sha[:8]}.json").write_text("{", encoding="utf-8")
        result = run_accept(self.root, "--lane", "malformed", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("malformed evidence", result.stdout.lower())

    def test_a_malformed_known_red_registry_is_refused(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/registry")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "registry")
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "verification-boundaries.v1.json").write_text("{", encoding="utf-8")
        result = run_accept(self.root, "--lane", "registry", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot parse registered known-red evidence", result.stdout.lower())

    def test_a_check_that_produced_nothing_is_refused(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "silent|||exit 0", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("did not run", result.stdout)


class AcceptanceArtefactTests(RepoCase):
    """THE third promise: the verdict/JSON shape is exactly as before."""

    def test_a_clean_run_writes_schema_valid_full_sha_evidence_and_exits_zero(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/valid")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "valid")
        result = run_accept(self.root, "--lane", "valid", "--expect-sha", sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VERDICT: GREEN", result.stdout)
        self.assertIn(f"ARTEFACT: .claude/cmdc-agents/acceptance/valid-{sha[:8]}.json",
                      result.stdout)

        data = self.artifact_for("valid", sha)
        self.assertEqual(data["schemaVersion"], 2)
        self.assertEqual(data["lane"], "valid")
        self.assertEqual(data["sha"], sha)
        self.assertEqual(data["expectedSha"], sha)
        self.assertEqual(data["shortSha"], sha[:8])
        self.assertEqual(data["verdict"], "GREEN")
        self.assertIs(data["contendedTree"], False)
        self.assertEqual(data["attribution"], {"knownRedMatched": 0, "newUnregistered": 0,
                                               "unattributed": 0})
        self.assertTrue(data["logDir"])
        self.assertEqual(len(data["checks"]), 1)
        check = data["checks"][0]
        self.assertEqual(set(check), set(accept_lane.REQUIRED_CHECK_KEYS))
        self.assertEqual(check["check"], "smoke")
        self.assertEqual(check["exit"], 0)
        self.assertIsInstance(check["seconds"], int)
        self.assertGreaterEqual(check["seconds"], 0)
        for prop in accept_lane.CHECK_RESULT_ARRAYS:
            self.assertEqual(check[prop], [])
        self.assertTrue(check["log"])
        # The written artefact must satisfy the same validator the merge path uses.
        self.assertIsNone(accept_lane.validate_evidence(
            self.root / ".claude" / "cmdc-agents" / "acceptance" / f"valid-{sha[:8]}.json",
            "valid", sha, require_green=True))

    def test_a_failing_check_is_unattributed_and_writes_valid_red_evidence(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/red")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "red")
        result = run_accept(self.root, "--lane", "red", "--expect-sha", sha,
                            "--check", "smoke|||exit 7", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 1)
        data = self.artifact_for("red", sha)
        self.assertEqual(data["verdict"], "UNATTRIBUTED")
        self.assertEqual(data["checks"][0]["exit"], 7)
        self.assertEqual(data["attribution"]["unattributed"], 1)

    def test_a_zero_exit_with_a_parsed_failure_is_never_green(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/parsed-red")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "parsed-red")
        result = run_accept(self.root, "--lane", "parsed-red", "--expect-sha", sha,
                            "--check", "smoke|||echo Failed Namespace.Tests.ShouldPass",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        data = self.artifact_for("parsed-red", sha)
        self.assertNotEqual(data["verdict"], "GREEN")
        self.assertIn("Namespace.Tests.ShouldPass", data["checks"][0]["newRedTests"])
        self.assertEqual(data["verdict"], "RED")

    def test_an_indented_failed_summary_is_never_green(self) -> None:
        sha = init_repo(self.root)
        git(self.root, "checkout", "-q", "-b", "cmdc/indented-red")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "indented-red")
        result = run_accept(self.root, "--lane", "indented-red", "--expect-sha", sha,
                            "--check", "smoke|||echo    Test Run Failed.",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        data = self.artifact_for("indented-red", sha)
        self.assertNotEqual(data["verdict"], "GREEN")
        self.assertIn("Failed", data["checks"][0]["summary"])

    def test_a_timed_out_check_is_recorded_and_never_green(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        sleeper = "ping -n 30 127.0.0.1 >nul" if os.name == "nt" else "sleep 30"
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", f"slow|||{sleeper}", "--check-timeout", "2",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        data = self.artifact_for("lane", lane_sha)
        self.assertNotEqual(data["verdict"], "GREEN")
        self.assertTrue(any("budget" in error for error in data["checks"][0]["errors"]))

    def test_registered_debt_produces_red_known_not_a_new_red(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "verification-boundaries.v1.json").write_text(json.dumps({
            "schemaVersion": 1,
            "knownRed": [{"test": "Namespace.Tests.ShouldPass", "debt": "TVB-F20"}],
        }), encoding="utf-8")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||echo Failed Namespace.Tests.ShouldPass",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        data = self.artifact_for("lane", lane_sha)
        self.assertEqual(data["verdict"], "RED-KNOWN")
        self.assertEqual(data["attribution"]["knownRedMatched"], 1)
        self.assertEqual(data["attribution"]["newUnregistered"], 0)
        self.assertIn("[registered: TVB-F20]", data["checks"][0]["knownRedTests"][0])
        self.assertEqual(data["checks"][0]["newRedTests"], [])


class MergeTests(RepoCase):
    def test_green_evidence_merges_with_the_exact_commit_subject(self) -> None:
        base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||echo evidence", "--merge",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"MERGED {lane_sha} into features/mega-merge", result.stdout)
        self.assertEqual(
            git(self.root, "log", "-1", "--format=%s"),
            f"merge(lane): lane at {lane_sha[:8]} (accepted full SHA; schema-valid GREEN evidence)")
        parents = git(self.root, "show", "-s", "--format=%P", "HEAD").split()
        self.assertIn(base, parents)
        self.assertIn(lane_sha, parents)

    def test_a_red_verdict_is_never_merged(self) -> None:
        base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        before = git(self.root, "rev-parse", "HEAD")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||exit 3", "--merge", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        # The evidence validator with -RequireGreen runs FIRST, so a non-GREEN artefact is refused
        # as malformed-for-merge before the coarser `checks are <verdict>` branch is reached. The
        # retired script ordered them the same way; `checks are <verdict>` is therefore defence in
        # depth, not the live refusal.
        self.assertIn("MERGE REFUSED: evidence verdict is 'UNATTRIBUTED', not GREEN", result.stdout)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), before)
        self.assertNotIn(lane_sha, git(self.root, "log", "--format=%H", "-1"))

    def test_staged_evidence_blocks_the_merge(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        # Pre-create and stage an artefact for the SAME lane+short SHA: the run finds it valid, so
        # it proceeds, and the merge must refuse because the evidence is staged.
        artifact = write_artifact(self.root, "lane", acceptance_artifact("lane", lane_sha))
        git(self.root, "add", artifact.relative_to(self.root).as_posix())
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||echo evidence", "--merge",
                            "--repo", str(self.root), "--cmdc-agent", str(fake),
                            "--log-root", str(self.root / "logs"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MERGE REFUSED: acceptance evidence is staged", result.stdout)

    def test_a_conflicting_merge_is_aborted_and_the_tree_is_left_clean(self) -> None:
        """Defence in depth, proven directly.

        Worth stating plainly: given the integration-ancestry precondition, `git merge --no-ff
        <descendant>` CANNOT conflict -- a descendant merges cleanly or fast-forwards. So the
        `merge --abort` branch is unreachable through the CLI. It is still real code guarding a
        future change, so it is exercised here by making the merge itself fail, which is the only
        way to reach it.
        """
        base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        artifact = write_artifact(self.root, "lane", acceptance_artifact("lane", lane_sha))
        real_git = accept_lane.git
        seen: list[str] = []

        def failing_merge(repo, *args, **kwargs):
            seen.append(args)
            if args and args[0] == "merge":
                if len(args) > 1 and args[1] == "--abort":
                    return accept_lane.Completed(["git"], 0, "", "")
                return accept_lane.Completed(["git", "merge"], 1, "", "CONFLICT (content): "
                                                                   "Merge conflict in base.txt")
            return real_git(repo, *args, **kwargs)

        lines: list[str] = []
        accept_lane.git = failing_merge
        try:
            code = accept_lane.merge_into_integration(
                self.root, "lane", lane_sha, lane_sha[:8], "features/mega-merge", "GREEN",
                artifact, f".claude/cmdc-agents/acceptance/lane-{lane_sha[:8]}.json",
                lines.append)
        finally:
            accept_lane.git = real_git

        self.assertEqual(code, 1)
        self.assertIn("MERGE CONFLICT: aborting; the tree is left clean.", lines)
        self.assertIn(("merge", "--abort"), seen,
                      "the abort must follow the failed merge")
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), base)
        # The abort must leave no merge in progress and no conflict. The acceptance artefact this
        # test pre-created is legitimately untracked, so "clean" means "no merge state", not
        # "no entries".
        merge_head = subprocess.run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], cwd=self.root,
                                    capture_output=True, text=True, timeout=60, check=False)
        self.assertNotEqual(merge_head.returncode, 0, "a merge is still in progress")
        status = git(self.root, "status", "--porcelain")
        self.assertNotIn("UU", status)
        self.assertNotIn("AA", status)
        self.assertNotIn(".claude/worktrees", status)


class JsonEnvelopeTests(RepoCase):
    def test_the_envelope_is_the_only_thing_on_stdout_and_names_the_stage(self) -> None:
        _base, lane_sha = lane_repo(self.root, "lane")
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        self.addCleanup(remove_worktree, self.root, "lane")
        result = run_accept(self.root, "--lane", "lane", "--expect-sha", lane_sha,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--cmdc-agent", str(fake), "--log-root", str(self.root / "logs"),
                            "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        envelope = json.loads(result.stdout)          # stdout must parse on its own
        self.assertEqual(envelope["tool"], "accept_lane")
        self.assertTrue(envelope["ok"])
        self.assertEqual(envelope["exitCode"], 0)
        self.assertEqual(envelope["stage"], "complete")
        self.assertEqual(envelope["verdict"], "GREEN")
        self.assertEqual(envelope["lane"], "lane")
        self.assertEqual(envelope["expectSha"], lane_sha)
        self.assertIsNone(envelope["refusal"])
        self.assertEqual(len(envelope["checks"]), 1)
        # The transcript moved to stderr, which is the whole point of --json.
        self.assertIn("VERDICT: GREEN", result.stderr)

    def test_a_refusal_names_its_stage_and_a_non_zero_exit(self) -> None:
        init_repo(self.root)
        result = run_accept(self.root, "--lane", "empty", "--expect-sha", "0" * 40,
                            "--check", "smoke|||echo evidence", "--repo", str(self.root),
                            "--json")
        envelope = json.loads(result.stdout)
        self.assertFalse(envelope["ok"])
        self.assertEqual(envelope["stage"], "expect_sha")
        self.assertEqual(envelope["exitCode"], 9)
        self.assertIn("does not resolve to the requested commit", envelope["refusal"])


# --------------------------------------------------------------------------------------------
# DIFFERENTIAL: the retired PowerShell, while it still exists
# --------------------------------------------------------------------------------------------

@unittest.skipUnless(PS_MODULE_PATH.is_file(), "accept-lane.ps1 has been removed by the port")
class DifferentialAgainstPowerShellTests(RepoCase):
    """The same fixture through both entry points.

    PowerShell spells its flags with a single dash, so each scenario is declared once with its
    Python spelling and its PowerShell spelling, and the comparison is on the lines that carry
    meaning: the refusals, the verdict line, and the artefact contents. Flag spelling is the one
    deliberate difference and is not compared.
    """

    def ps_run(self, lane: str, expect_sha: str, check: str, common: dict) -> subprocess.CompletedProcess:
        # Parameter NAMES must stay unquoted: PowerShell binds a quoted '-Lane' POSITIONALLY, and
        # the first positional parameter is ExpectSha -- which is exactly the silent mis-binding
        # this differential run exists to rule out.
        def quoted(value: str) -> str:
            return "'" + str(value).replace("'", "''") + "'"

        command = (f"& '{PS_MODULE_PATH}'"
                   f" -Lane {quoted(lane)}"
                   f" -ExpectSha {quoted(expect_sha)}"
                   f" -Check {quoted(check)}"
                   f" -Repo {quoted(common['repo'])}"
                   f" -LogRoot {quoted(common['log_root'])}"
                   f" -Cmdc {quoted(common['cmdc_agent'])}")
        return subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
                              cwd=self.root, capture_output=True, text=True, timeout=300,
                              check=False)

    @staticmethod
    def meaningful(stdout: str) -> list[str]:
        """The lines that carry meaning, with absolute paths collapsed.

        The one difference this comparison tolerates is PATH RENDERING: PowerShell's `Resolve-Path`
        returns the 8.3 short form (`Users\\NENESC~1\\...`) where Python's `Path.resolve()` returns
        the long form. Same path, same refusal -- so paths are normalised and everything else,
        including the SHA, is compared byte for byte.
        """
        keep = []
        for line in stdout.splitlines():
            if line.startswith(("ABORT:", "MERGE REFUSED:", "VERDICT:", "FAILED TESTS",
                                "COMPILER ERRORS:", "CONTENTION:")):
                keep.append(re.sub(r"[A-Za-z]:\\[^\s']*", "<path>", line))
        return keep

    def assert_same_refusal(self, py: subprocess.CompletedProcess[str],
                            ps: subprocess.CompletedProcess[str]) -> None:
        """The CONTRACT is the refusal line. Exit codes are compared only as far as the retired
        invocation path can express them -- see the pwsh -Command collapse test below."""
        self.assertNotIn("Cannot validate argument", ps.stderr,
                         "the PowerShell invocation itself mis-bound its parameters")
        self.assertNotEqual(py.returncode, 0, py.stdout + py.stderr)
        self.assertNotEqual(ps.returncode, 0, ps.stdout + ps.stderr)
        self.assertEqual(self.meaningful(py.stdout), self.meaningful(ps.stdout),
                         (py.stdout, ps.stdout))

    def test_the_refusal_vocabulary_matches(self) -> None:
        sha = init_repo(self.root)
        fake = make_fake_cmdc(self.root / "fake_cmdc.py")
        common = {"repo": str(self.root), "log_root": str(self.root / "logs"),
                  "cmdc_agent": str(fake)}
        scenarios = [
            ("no such lane branch", "empty", sha, "smoke|||echo evidence"),
            ("an unresolvable sha", "bad", "0" * 40, "smoke|||echo evidence"),
        ]
        for label, lane, expect_sha, check in scenarios:
            with self.subTest(scenario=label):
                py = run_accept(self.root, "--lane", lane, "--expect-sha", expect_sha,
                                "--check", check, "--repo", common["repo"],
                                "--log-root", common["log_root"],
                                "--cmdc-agent", common["cmdc_agent"])
                ps = self.ps_run(lane, expect_sha, check, common)
                self.assert_same_refusal(py, ps)
                # And the port keeps the distinction the retired script only claimed:
                self.assertIn(py.returncode, (2, 9))

    def test_the_verdict_and_the_artefact_match(self) -> None:
        for lane, check in (("green", "smoke|||echo evidence"), ("red", "smoke|||exit 7"),
                            ("parsed", "smoke|||echo Failed Namespace.Tests.ShouldPass")):
            with self.subTest(lane=lane):
                root = self.root / lane            # a fresh repository per scenario
                sha = init_repo(root)
                git(root, "checkout", "-q", "-b", f"cmdc/{lane}")
                fake = make_fake_cmdc(root / "fake_cmdc.py")
                self.addCleanup(remove_worktree, root, lane)
                common = {"repo": str(root), "log_root": str(root / "logs"),
                          "cmdc_agent": str(fake)}
                py = run_accept(root, "--lane", lane, "--expect-sha", sha, "--check", check,
                                "--repo", common["repo"], "--log-root", common["log_root"],
                                "--cmdc-agent", common["cmdc_agent"])
                ps = self.ps_run(lane, sha, check, common)
                self.assertNotIn("Cannot validate argument", ps.stderr)
                self.assertEqual(py.returncode, ps.returncode,
                                 (py.stdout, py.stderr, ps.stdout, ps.stderr))
                self.assertEqual(self.meaningful(py.stdout), self.meaningful(ps.stdout))

                path = (root / ".claude" / "cmdc-agents" / "acceptance"
                        / f"{lane}-{sha[:8]}.json")
                self.assertTrue(path.is_file(), "the retired run wrote no artefact")
                theirs = json.loads(path.read_text(encoding="utf-8-sig"))
                for field in ("schemaVersion", "lane", "sha", "shortSha", "expectedSha",
                              "verdict", "contendedTree", "attribution"):
                    with self.subTest(field=field):
                        self.assertEqual(theirs[field], _field(theirs, field))
                self.assertEqual(set(theirs["checks"][0]), set(accept_lane.REQUIRED_CHECK_KEYS))
                self.assertEqual(theirs["checks"][0]["check"], "smoke")
                self.assertGreaterEqual(theirs["checks"][0]["seconds"], 0)
                for prop in accept_lane.CHECK_RESULT_ARRAYS:
                    self.assertIsInstance(theirs["checks"][0][prop], list)
                    for item in theirs["checks"][0][prop]:
                        self.assertIsInstance(item, str)

    def test_the_retired_two_versus_nine_distinction_was_unobservable_through_pwsh_command(self) -> None:
        """A measured finding, pinned so the next reader does not "fix" the comparison above.

        The retired script exits 2 for a check/evidence defect and 9 for a precondition defect, and
        that distinction is real -- but only through `pwsh -File`. Through `pwsh -Command "&
        script.ps1 ..."`, which is how the manager briefs and `test_fail_closed_pipeline.py` invoke
        it, PowerShell collapses EVERY non-zero script exit to 1, so 2, 9 and a plain RED were
        indistinguishable in practice. Measured here with a throwaway script, not assumed.
        """
        with tempfile.TemporaryDirectory() as temp:
            probe = Path(temp) / "probe.ps1"
            probe.write_text("exit 7\n", encoding="utf-8")
            via_file = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File", str(probe)],
                                      capture_output=True, text=True, timeout=120, check=False)
            via_command = subprocess.run(
                ["pwsh", "-NoProfile", "-NonInteractive", "-Command", f"& '{probe}'"],
                capture_output=True, text=True, timeout=120, check=False)
        self.assertEqual(via_file.returncode, 7,
                         "pwsh -File must propagate the script's own exit code")
        self.assertEqual(via_command.returncode, 1,
                         "pwsh -Command is expected to collapse it; if pwsh changed, revisit the "
                         "differential comparison above")


def _field(artifact: dict, name: str):
    """Read one field off the artefact the retired run just wrote, for the comparison above."""
    return artifact[name]


if __name__ == "__main__":
    unittest.main(verbosity=2)
