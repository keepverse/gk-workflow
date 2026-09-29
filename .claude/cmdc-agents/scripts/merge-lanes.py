#!/usr/bin/env python3
"""Merge only lanes with machine-readable evidence for their exact reviewed SHA.

The manager must never merge a mutable branch tip merely because a previous acceptance
artefact exists. This tool preflights every requested lane, validates the full SHA and
schema of the artefact named for that tip, requires the current integration branch and a
clean manager tree, then merges the immutable reviewed SHA. Registry-only conflicts retain
the existing gated union behavior.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


INTEGRATION_BRANCH = "features/mega-merge"
LANE_PREFIX = "cmdc/"
ACCEPTANCE_DIR = Path(".claude/cmdc-agents/acceptance")
REGISTRY = "scripts/verification-boundaries.v1.json"
UNION = ".claude/cmdc-agents/scripts/union-verification-registry.py"
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
LANE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
CHECK_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
VERDICT_RE = re.compile(r"(?:GREEN|RED|RED-KNOWN|UNATTRIBUTED)")
REQUIRED_CHECK_FIELDS = {
    "check",
    "exit",
    "seconds",
    "summary",
    "failedTests",
    "knownRedTests",
    "newRedTests",
    "flakeSuspectTests",
    "errors",
    "log",
}
FAILURE_LIST_FIELDS = (
    "failedTests",
    "knownRedTests",
    "newRedTests",
    "flakeSuspectTests",
    "errors",
)
ATTRIBUTION_FIELDS = ("knownRedMatched", "newUnregistered", "unattributed")


def run(command: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git_value(repo: Path, *args: str) -> tuple[str, int]:
    result = run(["git", *args], repo)
    return result.stdout.strip(), result.returncode


def resolve_tip(repo: Path, lane: str) -> tuple[str | None, str | None]:
    if not LANE_RE.fullmatch(lane):
        return None, f"invalid lane name '{lane}'"
    branch = f"{LANE_PREFIX}{lane}"
    value, code = git_value(repo, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}")
    if code != 0 or not SHA_RE.fullmatch(value):
        return None, f"lane branch '{branch}' does not resolve to a full commit SHA"
    return value.lower(), None


def resolve_integration_head(repo: Path) -> tuple[str | None, str | None]:
    value, code = git_value(
        repo,
        "rev-parse",
        "--verify",
        f"refs/heads/{INTEGRATION_BRANCH}^{{commit}}",
    )
    if code != 0 or not SHA_RE.fullmatch(value):
        return None, (
            f"integration branch '{INTEGRATION_BRANCH}' does not resolve to a full commit SHA"
        )
    return value.lower(), None


def ensure_integration_ancestry(
    repo: Path,
    reviewed_sha: str,
    integration_sha: str,
) -> str | None:
    result = run(
        ["git", "merge-base", "--is-ancestor", integration_sha, reviewed_sha],
        repo,
    )
    if result.returncode != 0:
        return (
            f"reviewed SHA {reviewed_sha} does not descend from current integration branch "
            f"'{INTEGRATION_BRANCH}' at {integration_sha}"
        )
    return None


def ahead(repo: Path, lane_sha: str) -> tuple[int | None, str | None]:
    value, code = git_value(
        repo,
        "rev-list",
        "--count",
        f"{INTEGRATION_BRANCH}..{lane_sha}",
    )
    if code != 0:
        return None, f"cannot count commits ahead of {INTEGRATION_BRANCH}"
    try:
        count = int(value)
    except ValueError:
        return None, f"git returned a non-numeric ahead count: {value!r}"
    if count < 0:
        return None, f"git returned a negative ahead count: {count}"
    return count, None


def valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def valid_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def failed_summary(value: str) -> bool:
    if re.search(r"Failed!|Build FAILED", value, re.IGNORECASE):
        return True
    counts = re.findall(r"\bFailed:\s*(\d+)", value, re.IGNORECASE)
    if counts:
        return any(int(count) > 0 for count in counts)
    return re.search(r"\bFailed:\b", value, re.IGNORECASE) is not None


def parse_artifact(
    path: Path,
    lane: str,
    expected_sha: str,
) -> tuple[dict[str, object] | None, str | None]:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, f"missing acceptance evidence: {path}"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"malformed acceptance evidence {path}: {exc}"

    if not isinstance(artifact, dict):
        return None, f"malformed acceptance evidence {path}: root is not an object"
    if type(artifact.get("schemaVersion")) is not int or artifact.get("schemaVersion") != 2:
        return None, f"malformed acceptance evidence {path}: schemaVersion must be integer 2"
    if artifact.get("lane") != lane:
        return None, (
            f"acceptance evidence lane mismatch in {path}: "
            f"expected {lane!r}, got {artifact.get('lane')!r}"
        )

    artifact_sha = artifact.get("sha")
    if not isinstance(artifact_sha, str) or not SHA_RE.fullmatch(artifact_sha):
        return None, f"malformed acceptance evidence {path}: sha is not a full 40-character SHA"
    if artifact_sha.lower() != expected_sha:
        return None, (
            f"acceptance evidence SHA mismatch in {path}: "
            f"expected {expected_sha}, got {artifact_sha}"
        )
    if artifact.get("expectedSha") != expected_sha:
        return None, (
            f"malformed acceptance evidence {path}: expectedSha does not match {expected_sha}"
        )
    if artifact.get("shortSha") != expected_sha[:8]:
        return None, f"malformed acceptance evidence {path}: shortSha does not match the reviewed SHA"
    if not valid_timestamp(artifact.get("when")):
        return None, f"malformed acceptance evidence {path}: when is not a timezone-aware timestamp"

    verdict = artifact.get("verdict")
    if not isinstance(verdict, str) or not VERDICT_RE.fullmatch(verdict):
        return None, f"malformed acceptance evidence {path}: verdict is outside the acceptance vocabulary"
    if verdict != "GREEN":
        return None, f"acceptance evidence verdict is {verdict!r}, not GREEN"
    if type(artifact.get("contendedTree")) is not bool:
        return None, f"malformed acceptance evidence {path}: contendedTree must be boolean"
    if not isinstance(artifact.get("logDir"), str) or not artifact["logDir"].strip():
        return None, f"malformed acceptance evidence {path}: logDir must be non-empty text"

    attribution = artifact.get("attribution")
    if not isinstance(attribution, dict):
        return None, f"malformed acceptance evidence {path}: attribution is missing"
    for field in ATTRIBUTION_FIELDS:
        value = attribution.get(field)
        if type(value) is not int or value < 0:
            return None, (
                f"malformed acceptance evidence {path}: attribution.{field} "
                "must be a non-negative integer"
            )
        if value != 0:
            return None, f"acceptance evidence attribution is not clean: {attribution}"

    checks = artifact.get("checks")
    if not isinstance(checks, list) or not checks:
        return None, f"malformed acceptance evidence {path}: checks must be a non-empty array"

    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            return None, f"malformed acceptance evidence {path}: check entry is not an object"
        missing = sorted(REQUIRED_CHECK_FIELDS - set(check))
        if missing:
            return None, f"malformed acceptance evidence {path}: check is missing {', '.join(missing)}"
        name = check["check"]
        if not isinstance(name, str) or not CHECK_NAME_RE.fullmatch(name) or name in seen:
            return None, f"malformed acceptance evidence {path}: invalid or duplicate check name"
        seen.add(name)
        if type(check["exit"]) is not int or check["exit"] != 0:
            return None, f"acceptance evidence contains a non-zero check {name!r}"
        if type(check["seconds"]) is not int or check["seconds"] < 0:
            return None, f"malformed acceptance evidence {path}: seconds is invalid for {name!r}"
        if not isinstance(check["summary"], str):
            return None, f"malformed acceptance evidence {path}: summary is not text for {name!r}"
        if failed_summary(check["summary"]):
            return None, f"acceptance evidence contains a failed summary for check {name!r}"
        for field in FAILURE_LIST_FIELDS:
            if not valid_string_list(check[field]):
                return None, (
                    f"malformed acceptance evidence {path}: {field} "
                    f"must be a string array for {name!r}"
                )
            if check[field]:
                return None, f"acceptance evidence contains failed/red details for check {name!r}"
        if not isinstance(check["log"], str) or not check["log"].strip():
            return None, f"malformed acceptance evidence {path}: log is empty for {name!r}"

    return artifact, None


def evidence_for(repo: Path, lane: str, lane_sha: str) -> tuple[Path | None, str | None]:
    acceptance_dir = repo / ACCEPTANCE_DIR
    exact = acceptance_dir / f"{lane}-{lane_sha[:8]}.json"
    if exact.is_file():
        _, reason = parse_artifact(exact, lane, lane_sha)
        if reason:
            return None, reason
        return exact, None

    stale = sorted(acceptance_dir.glob(f"{lane}-*.json")) if acceptance_dir.is_dir() else []
    if stale:
        names = ", ".join(str(path.relative_to(repo)) for path in stale)
        return None, (
            f"missing exact acceptance evidence for {lane_sha}; "
            f"stale artifact(s): {names}"
        )
    return None, f"missing acceptance evidence for {lane} at {lane_sha}"


def prepare_lane(
    repo: Path,
    lane: str,
    integration_sha: str,
) -> tuple[dict[str, object] | None, str | None]:
    lane_sha, reason = resolve_tip(repo, lane)
    if lane_sha is None:
        return None, reason
    count, reason = ahead(repo, lane_sha)
    if count is None:
        return None, reason
    if count == 0:
        return None, None

    reason = ensure_integration_ancestry(repo, lane_sha, integration_sha)
    if reason:
        return None, reason

    artifact_path, reason = evidence_for(repo, lane, lane_sha)
    if artifact_path is None:
        return None, reason

    current_sha, reason = resolve_tip(repo, lane)
    if current_sha is None:
        return None, reason
    if current_sha != lane_sha:
        return None, (
            f"lane moved from reviewed SHA {lane_sha} to {current_sha} "
            "while evidence was being consumed"
        )

    return {
        "lane": lane,
        "sha": lane_sha,
        "count": count,
        "artifact": artifact_path.resolve(),
    }, None


def current_branch(repo: Path) -> tuple[str | None, str | None]:
    value, code = git_value(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if code != 0:
        return None, "cannot identify the current branch"
    return value, None


def status_paths(repo: Path) -> tuple[list[str] | None, str | None]:
    result = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], repo)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        return None, f"git status failed: {detail}"
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            paths.append(line.strip())
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.replace("\\", "/"))
    return paths, None


def staged_paths(repo: Path, relative_path: str) -> tuple[list[str] | None, str | None]:
    result = run(["git", "diff", "--cached", "--name-only", "--", relative_path], repo)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        return None, detail
    return [line for line in result.stdout.splitlines() if line.strip()], None


def unmerged(repo: Path) -> list[str]:
    value, _ = git_value(repo, "diff", "--name-only", "--diff-filter=U")
    return [line for line in value.splitlines() if line.strip()]


def parses(path: Path) -> tuple[bool, str]:
    try:
        with path.open(encoding="utf-8") as handle:
            json.load(handle)
        return True, ""
    except (OSError, json.JSONDecodeError) as exc:
        return False, str(exc)[:120]


def merge_prepared_lane(repo: Path, plan: dict[str, object]) -> int:
    lane = str(plan["lane"])
    lane_sha = str(plan["sha"])
    count = int(plan["count"])
    artifact_path = Path(plan["artifact"])

    _, reason = parse_artifact(artifact_path, lane, lane_sha)
    if reason:
        print(f"  {lane}: REFUSING -- acceptance evidence changed after preflight: {reason}")
        return 1

    branch, reason = current_branch(repo)
    if reason or branch != INTEGRATION_BRANCH:
        print(
            f"  {lane}: REFUSING -- current branch is {branch or 'unknown'}, "
            f"not {INTEGRATION_BRANCH}"
        )
        return 1
    current_sha, reason = resolve_tip(repo, lane)
    if current_sha is None:
        print(f"  {lane}: REFUSING -- {reason}")
        return 1
    if current_sha != lane_sha:
        print(
            f"  {lane}: REFUSING -- lane moved from reviewed SHA {lane_sha} "
            f"to {current_sha} after preflight"
        )
        return 1

    result = run(
        [
            "git",
            "merge",
            "--no-ff",
            lane_sha,
            "-m",
            f"merge(cmdc/{lane}): accepted lane at {lane_sha[:8]} (schema-valid GREEN evidence)",
        ],
        repo,
    )
    if result.returncode == 0:
        head, _ = git_value(repo, "log", "--oneline", "-1")
        print(f"  {lane}: merged exact reviewed SHA {lane_sha[:12]} ({count} commit(s)) -- {head[:80]}")
        return 0

    files = unmerged(repo)
    if not files:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        print(f"  {lane}: MERGE FAILED without unmerged paths: {detail}")
        return 1
    if files == [REGISTRY]:
        print(f"  {lane}: registry conflict -> union (gated)")
        union_script = repo / UNION
        union = run([sys.executable, str(union_script), lane_sha], repo)
        if union.stdout.strip():
            print("      " + union.stdout.strip().splitlines()[-1])
            for line in union.stdout.splitlines():
                if "REFUSING" in line or "differing" in line:
                    print("      " + line.strip())
        valid, parse_error = parses(repo / REGISTRY)
        if union.returncode != 0 or not valid:
            print(
                f"  {lane}: STOPPING -- union did not produce a valid registry "
                f"(tool exit {union.returncode}; parse: {parse_error or 'ok'}). "
                "The merge is left in place."
            )
            return 1
        add = run(["git", "add", REGISTRY], repo)
        if add.returncode != 0:
            print(f"  {lane}: STOPPING -- could not stage the validated registry")
            return 1
        commit = run(["git", "commit", "-q", "--no-edit"], repo)
        if commit.returncode != 0:
            detail = commit.stderr.strip() or commit.stdout.strip() or "no output"
            print(f"  {lane}: STOPPING -- registry commit failed: {detail[:120]}")
            return 1
        print(f"  {lane}: merged with the gated union ({count} commit(s))")
        return 0

    print(f"  {lane}: CONFLICT outside the registry: {files}")
    print("      STOPPING before any commit; the merge is left in place for hand resolution.")
    return 1


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python merge-lanes.py <lane> [<lane> ...]      (run from the repo root)")
        return 2
    root_result = run(["git", "rev-parse", "--show-toplevel"], Path.cwd())
    if root_result.returncode != 0:
        print("REFUSING -- run merge-lanes.py from inside the repository root")
        return 1
    repo = Path(root_result.stdout.strip()).resolve()

    integration_sha, reason = resolve_integration_head(repo)
    if integration_sha is None:
        print(f"REFUSING -- {reason}")
        return 1

    plans: list[dict[str, object]] = []
    seen_lanes: set[str] = set()
    for lane in argv:
        if lane in seen_lanes:
            print(f"  {lane}: REFUSING -- duplicate lane argument")
            return 1
        seen_lanes.add(lane)
        plan, reason = prepare_lane(repo, lane, integration_sha)
        if reason:
            print(f"  {lane}: REFUSING -- {reason}")
            return 1
        if plan is None:
            print(f"  {lane}: nothing ahead")
            continue
        plans.append(plan)

    if not plans:
        print("  batch complete")
        return 0

    branch, reason = current_branch(repo)
    if reason or branch != INTEGRATION_BRANCH:
        print(
            f"REFUSING -- current branch is {branch or 'unknown'}, not {INTEGRATION_BRANCH}"
        )
        return 1
    current_integration_sha, reason = resolve_integration_head(repo)
    if current_integration_sha is None:
        print(f"REFUSING -- {reason}")
        return 1
    if current_integration_sha != integration_sha:
        print(
            "REFUSING -- integration branch moved during batch preflight: "
            f"{integration_sha} -> {current_integration_sha}"
        )
        return 1
    conflicts = unmerged(repo)
    if conflicts:
        print(f"REFUSING -- manager tree already has unmerged paths: {conflicts}")
        return 1
    dirty_paths, reason = status_paths(repo)
    if dirty_paths is None:
        print(f"REFUSING -- {reason}")
        return 1
    allowed_artifacts = {
        Path(plan["artifact"]).relative_to(repo).as_posix()
        for plan in plans
    }
    for artifact in sorted(allowed_artifacts):
        staged, reason = staged_paths(repo, artifact)
        if staged is None:
            print(f"REFUSING -- could not inspect staged evidence {artifact}: {reason}")
            return 1
        if staged:
            print(f"REFUSING -- acceptance evidence is staged: {artifact}")
            return 1
    dirty = [path for path in dirty_paths if path not in allowed_artifacts]
    if dirty:
        print(f"REFUSING -- manager tree has {len(dirty)} unrelated dirty path(s): {dirty}")
        return 1

    for plan in plans:
        code = merge_prepared_lane(repo, plan)
        if code != 0:
            return code
    print("  batch complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
