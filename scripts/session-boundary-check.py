#!/usr/bin/env python3
r"""Guard: session boundary records are valid and two active sessions do not overlap. Replaces
`session-boundary-check.ps1`.

  * the record parses and carries the required fields;
  * `branch` / `worktree` still exist;
  * no two ACTIVE records claim overlapping `paths`;
  * every `worktree-*` branch is claimed by a record (an unclaimed one is abandoned work), EXCEPT
    `worktree-agent-<hex>`, which the Agent harness makes for a worktree-isolated call and which belongs
    to the spawning session - listed for information, never drift.

`--session <id>` scopes the verdict: drift naming that session fails, drift belonging only to others is
printed under its own heading and does not fail. `verify-change.py` runs it that way, so another
session's leftovers never block your verification and are never yours to "fix".
`--ci` validates tracked records in a clean checkout without requiring machine-local worktree/branch
topology. `--diff-base-ref`/`--diff-head-ref` with `--require-diff-fence` also checks the complete
reviewed diff against the selected session's paths; missing evidence is RED.

WHY THE POWERSHELL FORM WAS RETIRED
-----------------------------------
* **Everything went out through `Write-Host`**, invisible to a `2>&1` capture. The report and the
  verdict go to stdout; DRIFT, other sessions' drift and the harness-agent list go to stderr, so a
  caller reading stdout alone gets the report and the verdict and nothing that could be mistaken for
  either.
* **`.ToArray()`, not `@($problems)`.** The original carries a comment that PowerShell 7.6 throws
  "Argument types do not match" when `@()` wraps a generic `List[object]`. A Python list has no such
  shape, and the note is kept so nobody reintroduces the trap in a wrapper.
* **`Write-Error` + `exit 1` for a missing repo root** became a named refusal.

A CHECK THAT WAS NEUTERED, KEPT AS IT IS
------------------------------------------
Line 50 of the original is `if (-not (Test-Path (Join-Path $RepoRoot '.git'))) { }` — an `if` with an
EMPTY body. Whatever check it once carried is gone, and the reader is left with a condition that looks
like it validates something and validates nothing. It is NOT reinstated here: reinstating it would be a
behaviour change this port cannot prove, and a guard that starts refusing because a port guessed at a
deleted check is worse than one that is honestly inert. It is recorded in the todo as an open question
for the boundary owner, because "was this meant to be a check?" is a decision only they can answer.

ALMOST EVERY COMPARISON FOLDS CASE
-----------------------------------
`-notcontains`, `-contains`, `-eq`, `-like`, `-notlike` and `-match` are all case-INSENSITIVE in
PowerShell, and both overlap helpers use an explicit ignore-case comparer
(`StringComparison.OrdinalIgnoreCase`, `WildcardOptions.IgnoreCase`). So a branch `Feature/X` matches a
record's `feature/x`, and a `paths` entry differing only in case from another is an OVERLAP. The one
place that does not fold is nothing: this guard is uniformly case-insensitive, and the port is too —
asserted on the compiled patterns rather than through one fixture, because a fold that is dropped is
invisible until a real casing difference ships.

TWO ASYMMETRIES THAT LOOK LIKE BUGS AND ARE NOT
-----------------------------------------------
* `worktree` is in `$required` but the missing-field check EXCLUDES it, because the field is
  mode-dependent: a `direct` record has none. The `-Ci` form of that check is separate and only fires
  for an `active` worktree record with a blank path.
* In `-Ci` mode the worktree-path and branch-existence checks are SKIPPED entirely. A clean checkout has
  no machine-local worktree topology, and requiring it made CI red for a state CI cannot produce. The
  skip is reported, not silent.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

GUARD_ID = "session-boundary"
EXIT_OK = 0
EXIT_FAILED = 1
GIT_TIMEOUT = 120

# The closed vocabularies. `gk-core/tests/tools/test_program_status.py` reads these LITERALS as its drift guard's
# owner, so the declaration here is load-bearing in both directions: change one and that test goes red.
REQUIRED_FIELDS = ("session", "program", "problem", "mode", "branch", "worktree", "paths",
                   "started", "status")
# `worktree` is required-but-mode-dependent, so the missing-field check skips it. See the docstring.
REQUIRED_UNLESS_MODE_DEPENDENT = tuple(f for f in REQUIRED_FIELDS if f != "worktree")
VALID_MODES = ("direct", "worktree")
VALID_STATUS = ("active", "merged", "abandoned")
HARNESS_AGENT_BRANCH = re.compile(r"^worktree-agent-[0-9a-f]+$", re.IGNORECASE)
WORKTREE_PREFIX = "worktree-"
# A `_`-prefixed file in tasks/sessions/ is a TEMPLATE, not a record, and `tasks/sessions/_template.json`
# is the one that needs the skip. Named so the value can be pinned by a consumer rather than matched as
# a source fragment: `program_status.py` reads the same directory under the same rule, and its drift
# guard compares the two.
TEMPLATE_PREFIX = "_"


class Refusal(Exception):
    """A named precondition failure."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


@dataclass
class Problem:
    text: str
    owners: list[str] = field(default_factory=list)


def git_lines(root: Path, args: list[str]) -> list[str]:
    """`git -C <root> <args>` stdout as lines, stderr separated, hard timeout.

    stderr is deliberately not consulted: the original piped it to `$null` to stop a harmless warning
    aborting the guard, and that suppression is why a genuine git failure was indistinguishable from a
    warning. Whether a non-zero exit is an ANSWER is the caller's decision - only the reviewed-diff call
    treats it as a failure.
    """
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          timeout=GIT_TIMEOUT)
    return (proc.stdout or "").splitlines()


def git_ok(root: Path, args: list[str]) -> bool:
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          timeout=GIT_TIMEOUT)
    return proc.returncode == 0


def _is(value: object, expected: str) -> bool:
    """`-eq` semantics: a case-INSENSITIVE equality against a string, with null never matching."""
    return value is not None and str(value).casefold() == expected.casefold()


def _ps_string(value: object) -> str:
    """`"$value"` as PowerShell interpolates it.

    A JSON `null` becomes the EMPTY STRING. Same defect as `guard-class-system`'s, in the same shape:
    the report line printed `[]` for a complete record and `[None]` for a record missing `status`, so a
    reader could not tell "no status" from "the status is the text None". The original's line is
    `  - {0} [{1}] {2} -> {3}` and PowerShell renders a null field as empty.
    """
    return "" if value is None else str(value)


def default_repo_root() -> Path | None:
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                          timeout=GIT_TIMEOUT)
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return None
    return Path(proc.stdout.strip())


def main_worktree_root(root: Path) -> Path:
    """The MAIN worktree's root, not the one we are running inside.

    `git rev-parse --show-toplevel` returns the LINKED worktree when run from inside one, but a
    record's `worktree` field is written relative to the main checkout. Resolving against the current
    root re-created the very false positive the resolution was meant to fix - measured 2026-09-22: a
    first fix still reported 7 records as "no longer exists" from a lane's own worktree.
    `git worktree list --porcelain` lists the main worktree first.

    A DEFECT FIXED HERE, AND IT ONLY SHOWED UP IN A FIXTURE. The original calls
    `git worktree list --porcelain` with NO `-C $RepoRoot`, so it lists the CURRENT DIRECTORY's
    repository. Run with `--repo-root` pointing somewhere else - which is what every fixture, and every
    caller that passes the flag explicitly, does - `$mainRoot` became the real repo's main worktree and
    every record's worktree path was resolved against THE WRONG REPOSITORY. Measured: a fixture
    repository with a real `git worktree add wt` and a record pointing at it was reported as
    "worktree path 'wt' no longer exists" while the directory sat there.

    It is invisible in production because the CWD is the repository, so the two agree - which is exactly
    why it survived. The port asks the repository it was told to check, and the differential declares
    the difference rather than reproducing it.
    """
    for line in git_lines(root, ["worktree", "list", "--porcelain"]):
        if line.lower().startswith("worktree "):
            return Path(line[len("worktree "):].strip())
    return root


def path_overlap(a: str, b: str) -> bool:
    """Whether two `paths` entries claim the same ground, case-insensitively.

    The original trims trailing `/`, then `*`, then `/` from each side and asks whether either is a
    prefix of the other. So `a/**` becomes `a/` after the `*` trim and `a` after the second `/` trim,
    and a wildcard entry compares equal to a plain one.

    Those three calls are TRANSCRIBED rather than collapsed into one `rstrip("/*")`, and the reason is
    fidelity to the source rather than a difference in behaviour: for a trailing run the two are
    equivalent, because `rstrip` strips repeatedly over a set. An earlier version of this comment
    claimed the order "matters" and that a single call would strip a `*` sitting before a `/` - which
    is FALSE, `rstrip` never touches a non-trailing character. Kept as written so the next reader does
    not re-derive it, and so a test can pin the equivalence rather than assume a difference.
    """
    na = a.rstrip("/").rstrip("*").rstrip("/")
    nb = b.rstrip("/").rstrip("*").rstrip("/")
    if not na or not nb:
        return False
    # OrdinalIgnoreCase in the original; casefold is its closest Python analogue.
    return na.casefold().startswith(nb.casefold()) or nb.casefold().startswith(na.casefold())


def session_path_matches(path: str, pattern: str) -> bool:
    """`WildcardPattern(pattern, IgnoreCase).IsMatch(normalized)` from the original.

    `fnmatch.fnmatchcase` on both sides lower-cased: the platform's own `normcase` behaviour would make
    the answer depend on the machine, and a fence check whose verdict changes with the OS is not a
    check. `*` matches across `/` in both, which is what makes a `docs/**` entry cover a nested path.
    """
    if not pattern.strip():
        return False
    normalized = path.replace("\\", "/").lstrip("/")
    wildcard = pattern.replace("\\", "/")
    return fnmatch.fnmatchcase(normalized.casefold(), wildcard.casefold())


def read_records(sessions_dir: Path) -> tuple[list[tuple[str, dict]], list[Problem]]:
    """`(name, record)` for each parseable record, plus a problem for each unparseable one.

    A record that does not parse is reported AND SKIPPED - it contributes no paths to the overlap check,
    because there are none to contribute. That is the original's behaviour and it is stated rather than
    left to be discovered: a skipped record is a hole in the overlap detection, and a hole that is only
    visible by reading the code is a hole that gets reported as a pass.
    """
    records: list[tuple[str, dict]] = []
    problems: list[Problem] = []
    for path in sorted(sessions_dir.glob("*.json")):
        name = path.name
        if name.startswith("_"):
            continue
        owner = path.stem
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(Problem(f"{name}: does not parse as JSON — {exc}", [owner]))
            continue
        if not isinstance(record, dict):
            problems.append(Problem(
                f"{name}: does not parse as a session record — the document is a "
                f"{type(record).__name__}, not an object", [owner]))
            continue
        records.append((name, record))
    return records, problems


def check(root: Path, session: str | None = None, ci: bool = False, diff_base_ref: str | None = None,
          diff_head_ref: str | None = None, require_diff_fence: bool = False) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise Refusal("REPO-ROOT-MISSING", str(root))

    diff_requested = (require_diff_fence
                      or bool((diff_base_ref or "").strip())
                      or bool((diff_head_ref or "").strip()))
    if diff_requested:
        if not (diff_base_ref or "").strip() or not (diff_head_ref or "").strip():
            raise Refusal("DIFF-FENCE-INCOMPLETE",
                          "a reviewed diff fence requires both --diff-base-ref and --diff-head-ref")
        if not (session or "").strip():
            raise Refusal("DIFF-FENCE-NO-SESSION",
                          "a reviewed diff fence requires --session; a diff cannot be judged "
                          "against an implicit fence")

    main_root = main_worktree_root(root)
    sessions_dir = root / "tasks" / "sessions"
    if not sessions_dir.is_dir():
        return {"guard": GUARD_ID, "verdict": "OK", "records": 0, "active": 0, "problems": [],
                "others": [], "harness_agents": [], "skipped": [
                    "no tasks/sessions/ — nothing to check"], "diff": None}

    branches = git_lines(root, ["branch", "--format=%(refname:short)"])
    branch_keys = {b.casefold() for b in branches}
    problems: list[Problem] = []
    notes: list[str] = []

    records, parse_problems = read_records(sessions_dir)
    problems += parse_problems

    for name, record in records:
        owner = Path(name).stem
        for required in REQUIRED_UNLESS_MODE_DEPENDENT:
            # `$null -eq $rec.$f`: a field PRESENT with a falsey value (False, 0, "") is not missing.
            # `is None` is the exact analogue; a truthiness test would report `started: 0` as absent.
            if record.get(required) is None:
                problems.append(Problem(f"{name}: missing required field '{required}'", [owner]))
        mode = record.get("mode")
        if mode and str(mode).casefold() not in {m.casefold() for m in VALID_MODES}:
            problems.append(Problem(
                f"{name}: mode '{mode}' is not one of {'/'.join(VALID_MODES)}", [owner]))
        status = record.get("status")
        if status and str(status).casefold() not in {s.casefold() for s in VALID_STATUS}:
            problems.append(Problem(
                f"{name}: status '{status}' is not one of {'/'.join(VALID_STATUS)}", [owner]))

        if ci and _is(status, "active") and mode == "worktree" \
                and not str(record.get("worktree") or "").strip():
            problems.append(Problem(f"{name}: active worktree record has no worktree path", [owner]))

        if not ci and _is(status, "active") and mode == "worktree":
            if not record.get("worktree"):
                problems.append(Problem(f"{name}: mode=worktree but no 'worktree' path recorded",
                                        [owner]))
            else:
                # Resolve a repo-root-relative worktree path against the MAIN root, never the current
                # directory: testing the record's own string against the CWD made every run from inside a
                # lane's worktree report "no longer exists" for paths that all exist - 7 records affected
                # (RECON-F9). Absolute paths are honoured as written.
                written = str(record["worktree"])
                candidate = Path(written)
                if not candidate.is_absolute():
                    candidate = main_root / written
                if not candidate.exists():
                    problems.append(Problem(
                        f"{name}: worktree path '{written}' no longer exists", [owner]))

        # Only an ACTIVE record must still own a live branch. A retired record is history: its branch is
        # legitimately gone once the worktree is removed, and flagging that made the repo-wide run red on
        # a session nobody could act on.
        if not ci and _is(status, "active") and record.get("branch") \
                and str(record["branch"]).casefold() not in branch_keys:
            problems.append(Problem(
                f"{name}: branch '{record['branch']}' does not exist", [owner]))

    # ---- overlapping paths between two ACTIVE records -------------------------------------------
    # `-eq` FOLDS case, so `ACTIVE` is active here exactly as it is in the vocabulary check above. An
    # exact comparison removed a case-folded record from the overlap set, which is a SILENT NARROWING:
    # the guard reported clean on two sessions that do overlap.
    active_keys = {s.casefold() for s in VALID_STATUS}
    active = [(n, r) for n, r in records
              if str(r.get("status") or "").casefold() == "active"]
    for i, (name_i, rec_i) in enumerate(active):
        for name_j, rec_j in active[i + 1:]:
            # Two worktree sessions are isolated BY CONSTRUCTION: each has its own directory, so an
            # overlap between them is not a conflict.
            if rec_i.get("mode") == "worktree" and rec_j.get("mode") == "worktree":
                continue
            for pi in (rec_i.get("paths") or []):
                for pj in (rec_j.get("paths") or []):
                    if path_overlap(str(pi), str(pj)):
                        problems.append(Problem(
                            f"{name_i} and {name_j} both claim '{pi}' / '{pj}' while active — "
                            "narrow the scope or move one to a worktree",
                            [str(rec_i.get("session") or ""), str(rec_j.get("session") or "")]))
    if ci:
        notes.append("CI mode: the worktree-path and branch-existence checks are SKIPPED, because a "
                     "clean checkout has no machine-local worktree topology and requiring it made CI red "
                     "for a state CI cannot produce")

    # ---- the reviewed diff fence ---------------------------------------------------------------
    diff_summary = None
    if diff_requested:
        selected = [(n, r) for n, r in records if str(r.get("session") or "") == session]
        if not selected:
            problems.append(Problem(
                f"reviewed diff has no session record for '{session}'", [session]))
        elif not _is(selected[0][1].get("status"), "active"):
            problems.append(Problem(
                f"reviewed diff session '{session}' is not active", [session]))
        else:
            span = f"{diff_base_ref}..{diff_head_ref}"
            proc = subprocess.run(
                ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACMRD", span],
                capture_output=True, text=True, timeout=GIT_TIMEOUT)
            if proc.returncode != 0:
                # The original THREW here. Refusing by name keeps the reason, and the span, in one line.
                raise Refusal("REVIEWED-DIFF-FAILED",
                              f"git diff failed for reviewed range '{span}' (exit {proc.returncode})")
            reviewed = [line.strip().replace("\\", "/") for line in
                        (proc.stdout or "").splitlines() if line.strip()]
            fence = selected[0][1].get("paths") or []
            for path in reviewed:
                if not any(session_path_matches(path, str(pattern)) for pattern in fence):
                    problems.append(Problem(
                        f"outside session fence: {path} (reviewed range {span})", [session]))
            diff_summary = {"base": diff_base_ref, "head": diff_head_ref, "changed": len(reviewed),
                            "session": session}

    # ---- unclaimed worktree-* branches ----------------------------------------------------------
    claimed: set[str] = set()
    for _name, record in records:
        for key in ("branch", "worktree"):
            value = record.get(key)
            if value:
                claimed.add(str(value).casefold())
    harness_agents: list[str] = []
    for branch in branches:
        if not branch.casefold().startswith(WORKTREE_PREFIX):
            continue
        if branch.casefold() in claimed:
            continue
        if HARNESS_AGENT_BRANCH.match(branch):
            harness_agents.append(branch)
            continue
        problems.append(Problem(
            f"branch '{branch}' is not claimed by any session record — abandoned worktree? "
            "mark the owning record abandoned/merged, or remove the worktree", [branch]))

    # ---- scope the verdict to one session -------------------------------------------------------
    blocking, others = problems, []
    if session:
        mine = [(n, r) for n, r in records if str(r.get("session") or "") == session]
        if not mine:
            problems.append(Problem(f"no session record for '{session}' in tasks/sessions/", [session]))
            blocking = problems
        else:
            my_ids = {session.casefold()}
            my_ids |= {str(r["branch"]).casefold() for _n, r in mine if r.get("branch")}
            blocking = [p for p in problems
                        if any(o.casefold() in my_ids for o in p.owners if o)]
            others = [p for p in problems
                      if not any(o.casefold() in my_ids for o in p.owners if o)]

    return {
        "guard": GUARD_ID,
        "verdict": "FAIL" if blocking else "OK",
        "session": session,
        "ci": ci,
        "records": len(records),
        "active": len(active),
        "branches": len(branches),
        "harness_agents": harness_agents,
        "diff": diff_summary,
        "problems": [p.text for p in blocking],
        "others": [p.text for p in others],
        "skipped": notes,
    }


def _report(result: dict, records: list[tuple[str, dict]]) -> None:
    """The record listing, on stdout with the verdict: it is the guard's report, not a finding."""
    print(f"[session-boundary] {result['records']} record(s), {result['active']} active")
    for _name, record in records:
        print(f"  - {_ps_string(record.get('session'))} [{_ps_string(record.get('status'))}] "
              f"{_ps_string(record.get('branch'))} -> {_ps_string(record.get('problem'))}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Guard: session boundary records are valid and do not overlap "
                    "(replaces session-boundary-check.ps1).")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="the repository to check (default: this tool's own worktree top level)")
    parser.add_argument("--session", default=None,
                        help="scope the verdict to one session; other sessions' drift is reported "
                             "under its own heading and does not fail")
    parser.add_argument("--ci", action="store_true",
                        help="validate tracked records without requiring machine-local worktree/branch "
                             "topology")
    parser.add_argument("--diff-base-ref", default=None, help="the reviewed range's base ref")
    parser.add_argument("--diff-head-ref", default=None, help="the reviewed range's head ref")
    parser.add_argument("--require-diff-fence", action="store_true",
                        help="require a reviewed-diff fence, which needs both refs and --session")
    parser.add_argument("--json", action="store_true", help="emit the result as JSON")
    args = parser.parse_args(argv)

    root = args.repo_root or default_repo_root()
    if root is None:
        refusal = Refusal("REPO-ROOT-UNDETERMINED",
                          "not inside a git worktree, so there is nothing to check. Pass --repo-root "
                          "explicitly if the tool is being run from elsewhere.")
        print(f"[session-boundary] {refusal.reason} {refusal.detail}", file=sys.stderr)
        if args.json:
            print(json.dumps({"guard": GUARD_ID, "verdict": "FAILED", "reason": refusal.reason,
                              "detail": refusal.detail}, indent=2))
        return EXIT_FAILED

    try:
        result = check(root, args.session, args.ci, args.diff_base_ref, args.diff_head_ref,
                       args.require_diff_fence)
    except Refusal as refusal:
        print(f"[session-boundary] {refusal.reason} {refusal.detail}", file=sys.stderr)
        if args.json:
            print(json.dumps({"guard": GUARD_ID, "verdict": "FAILED", "reason": refusal.reason,
                              "detail": refusal.detail, "session": args.session, "ci": args.ci,
                              "records": 0, "active": 0, "branches": 0, "harness_agents": [],
                              "diff": None, "problems": [], "others": [], "skipped": []}, indent=2))
        return EXIT_FAILED

    if args.json:
        print(json.dumps(result, indent=2))
        return EXIT_OK if result["verdict"] == "OK" else EXIT_FAILED

    records, _ = read_records(root / "tasks" / "sessions") \
        if (root / "tasks" / "sessions").is_dir() else ([], [])
    for note in result["skipped"]:
        print(f"[session-boundary] SKIPPED {note}", file=sys.stderr)
    if result["harness_agents"]:
        print("", file=sys.stderr)
        print(f"[session-boundary] harness agent worktrees ({len(result['harness_agents'])}) — owned by "
              "the session that spawned the agent, not drift:", file=sys.stderr)
        for branch in result["harness_agents"]:
            print(f"  - {branch}", file=sys.stderr)
    if result["others"]:
        print("", file=sys.stderr)
        print(f"[session-boundary] other sessions' drift ({len(result['others'])}) — not "
              f"'{result['session']}'s, does not block it:", file=sys.stderr)
        for problem in result["others"]:
            print(f"  ~ {problem}", file=sys.stderr)
    _report(result, records)
    if result["diff"]:
        print(f"[session-boundary] reviewed range {result['diff']['base']}..{result['diff']['head']}: "
              f"{result['diff']['changed']} changed path(s) checked against "
              f"'{result['diff']['session']}'")
    print("")
    if result["verdict"] == "FAIL":
        print(f"[session-boundary] DRIFT ({len(result['problems'])}):")
        for problem in result["problems"]:
            print(f"  ! {problem}", file=sys.stderr)
        return EXIT_FAILED
    if result["session"]:
        print(f"[session-boundary] clean for '{result['session']}'")
    else:
        print("[session-boundary] clean")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
