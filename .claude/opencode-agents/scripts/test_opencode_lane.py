"""Offline tests for opencode_lane.py — no model, no spend, no worktree.

Run: python .claude/opencode-agents/scripts/test_opencode_lane.py
Covers the charter hard rule, the REPORT/scope/brief parsing, and the event
normalisation the supervisor feeds from opencode --format json.
"""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opencode_lane as lane


class CharterTest(unittest.TestCase):
    def test_charter_state_matches_file(self):
        # Live repo state: owner approved one smoke model on 2026-09-23.
        c = lane.charter()
        if not c.get("approvedAt"):
            self.assertIsNotNone(lane.charter_refusal())
        else:
            self.assertIsNone(lane.charter_refusal())
            allowed = (c.get("models") or {}).get("opencode") or []
            self.assertTrue(allowed)
            self.assertIsNone(lane.model_refusal(allowed[0]))

    def test_unlisted_model_refused(self):
        self.assertIsNotNone(lane.model_refusal("anything/at-all"))
        self.assertIsNotNone(lane.model_refusal(None))


class InvocationTest(unittest.TestCase):
    def test_v2_directory_is_positional_and_variant_is_model_suffix(self):
        original = lane.opencode_argv
        lane.opencode_argv = lambda: ["opencode"]
        try:
            args = lane.opencode_run_argv({
                "cwd": "D:/repo",
                "model": "opencode/space-bunny-free",
                "effort": "high",
            }, "ses_test")
        finally:
            lane.opencode_argv = original
        self.assertEqual(args, [
            "opencode", "run", "--format", "json", "D:/repo",
            "--model", "opencode/space-bunny-free#high", "--session", "ses_test",
        ])

    def test_clean_v2_exit_with_final_text_is_success(self):
        self.assertTrue(lane.run_segment_succeeded(0, "tool-calls", "done"))
        self.assertTrue(lane.run_segment_succeeded(0, "stop", ""))
        self.assertFalse(lane.run_segment_succeeded(0, None, ""))
        self.assertFalse(lane.run_segment_succeeded(1, "stop", "done"))


class ReportTest(unittest.TestCase):
    def test_parses_report_block(self):
        text = ('done stuff\n<<<REPORT {"status": "done", "summary": "s", '
                '"changed_files": ["a.cs"], "verification": [], '
                '"open_issues": []} REPORT>>>')
        r = lane.parse_report(text)
        self.assertEqual(r["status"], "done")
        self.assertEqual(r["changed_files"], ["a.cs"])

    def test_prose_without_report_is_none(self):
        self.assertIsNone(lane.parse_report("all done, trust me"))


class ScopeTest(unittest.TestCase):
    ALLOW = ["src/FusionRpg.Core/Items/**", "tests/FusionRpg.Core.Items.Tests/**"]

    def test_member_file_in_scope(self):
        self.assertTrue(lane.in_scope("src/FusionRpg.Core/Items/Sword.cs", self.ALLOW))

    def test_nested_member_in_scope(self):
        self.assertTrue(lane.in_scope(
            "src/FusionRpg.Core/Items/Sub/Deep.cs", self.ALLOW))

    def test_outsider_out_of_scope(self):
        self.assertFalse(lane.in_scope("src/FusionRpg.Server/Program.cs", self.ALLOW))
        self.assertFalse(lane.in_scope(".github/workflows/ci.yml", self.ALLOW))

    def test_brief_commands_extracted_only_from_verification_section(self):
        brief = (
            "Use `opencode/space-bunny-free` and read `README.md`.\n"
            "## Verification\n"
            "- `dotnet test a`\n"
            "- `npm test`\n"
            "## Notes\n"
            "- `not-a-command`\n"
        )
        self.assertEqual(lane.brief_verification(brief), ["dotnet test a", "npm test"])


class NormaliseTest(unittest.TestCase):
    def test_full_step_sequence_updates_status(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "meta.json").write_text("{}", encoding="utf-8")
            sup = lane.Supervisor(d)
            sup.st = {"turnsUsed": 0,
                      "tokens": {"input": 0, "output": 0, "cacheRead": 0}}
            sup.on_event({"type": "run_start", "sessionId": "ses_x"})
            sup.on_event({"type": "turn_start", "step": 1})
            sup.on_event({"type": "tool_queued", "toolName": "read",
                          "input": "probe-in.txt"})
            sup.on_event({"type": "message_end",
                          "content": [{"type": "text", "text": "DONE"}]})
            sup.on_event({"type": "model_request_end",
                          "usage": {"inputTokens": 100, "outputTokens": 20,
                                    "cacheReadTokens": 10, "cacheWriteTokens": 5}})
            self.assertEqual(sup.st["sessionId"], "ses_x")
            self.assertEqual(sup.st["turnsUsed"], 1)
            self.assertEqual(sup.st["tokens"]["input"], 100)
            self.assertEqual(sup.st["tokens"]["output"], 20)
            self.assertEqual(sup.st["tokens"]["cacheRead"], 10)
            self.assertEqual(sup.st["contextTokens"], 115)
            self.assertEqual(sup.st["lastSaid"], "DONE")
            tl = (d / "timeline.jsonl").read_text(encoding="utf-8")
            self.assertIn('"kind": "tool"', tl)
            self.assertIn('"kind": "say"', tl)

    def test_run_error_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "meta.json").write_text("{}", encoding="utf-8")
            sup = lane.Supervisor(d)
            sup.st = {}
            sup.on_event({"type": "run_error", "error": "quota exploded"})
            self.assertIn("quota", sup.last_error)


class CliTest(unittest.TestCase):
    def test_status_empty_agents_dir(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            lane.cmd_status(type("A", (), {"id": None})())
        rows = json.loads(buf.getvalue())
        self.assertIsInstance(rows, list)
        for r in rows:  # any pre-existing local agents must at least shape-check
            self.assertIn("id", r)
            self.assertIn("state", r)

    def test_unknown_agent_refused(self):
        with self.assertRaises(SystemExit):
            lane.agent_dir("definitely-not-a-real-agent-xyz")


if __name__ == "__main__":
    unittest.main(verbosity=1)
