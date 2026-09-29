#!/usr/bin/env python3
"""Turn cmdc lane state changes into a push event for the manager.

Why this exists: `cmdc_agent.py status` is the only place a lane's state is visible, and nothing pushes
it to the manager, so "manage by events only" had no event source for lanes -- the manager had to poll
on every goal turn. This watcher polls the runner's own status files and EXITS on the first transition,
which makes the exit a notification that wakes the manager. It is a poller, but a single one, in one
process, instead of a manager turn burned every few seconds.

What counts as an event: any lane whose `state` differs from the last observation (e.g.
running -> partial when a segment ends -- the actionable "continue this lane" signal -- or -> done).
A lane that stays in one state (a parked lane, a long segment) is NOT an event and does not wake anyone.

Stale/dead detection (added 2026-09-22): the runner's own --stall-min handles a LIVE-but-silent
segment (kill + retry, which is itself a transition). It cannot handle a DEAD or wedged runner:
status.json then freezes in a non-terminal state and no transition ever fires. So for every lane in
a non-terminal state, the watcher also checks (a) lastEventAt age -- older than --stale-min minutes
means the lane is STALE (runner hung, machine slept, or child wedged past the runner's own stall
handling), and (b) pid liveness -- a recorded pid that no longer exists means the runner DIED
without writing a terminal state. Both are reported as synthetic state values (STALE(...),
DEAD(...)) so the existing transition logic fires exactly once per lane and does not refire while
the condition persists. Keep --stale-min ABOVE the runner's --stall-min (default 20 vs 15) so the
runner's own kill+retry fires first whenever it is alive to do so.

It also exits when the BCU2.10 round-1 report artefact appears, since that releases BCU2.11/2.12.

State lives in `D:/tmp/cmdc-watch-state.json` so a relaunched watcher does not re-fire on old news.

Usage: `python .claude/cmdc-agents/scripts/watch-lanes.py [--interval 60] [--once]`
Exit codes: 0 = a transition was seen (or --once), 1 = the runner directory is unreadable (a real
failure, not silence), 2 = bad usage.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
AGENTS = REPO / ".claude" / "cmdc-agents" / "agents"
STATE_PATH = Path("D:/tmp/cmdc-watch-state.json")
BCU_REPORT = REPO / "tasks" / "reports" / "BCU2.10-round-1.json"

# Mirrors TERMINAL in cmdc_agent.py. A lane in any other state is expected to be
# making progress; if it is not (no events, dead pid), it is stale or dead.
NON_TERMINAL = {"running", "starting", "retry_wait", "verifying", "continuing"}


def pid_alive(pid) -> bool:
    """True if the pid is a running process. Never kills what it checks.

    POSIX: os.kill(pid, 0) is the standard liveness probe.
    Windows: os.kill does NOT probe -- non-CTRL signals map to TerminateProcess, and
    sig 0 raises for live processes too (verified 2026-09-22: a live pid was reported
    DEAD). So on Windows use OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION) +
    GetExitCodeProcess == STILL_ACTIVE via ctypes.
    """
    if not pid:
        return True  # no pid recorded: cannot prove death, so not DEAD
    try:
        pid = int(pid)
    except (ValueError, TypeError):
        return True  # malformed pid: not provably dead
    if pid <= 0:
        return True
    if os.name == "nt":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False  # no such process (or access denied to a process that exists;
            # access-denied still proves SOMETHING with that pid exists, but OpenProcess
            # does not distinguish -- treating it as alive is the safe direction: a false
            # DEAD wakes the manager to relaunch a lane that is still running)
        try:
            code = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == STILL_ACTIVE
            return True  # could not read exit code: not provably dead
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_states(stale_min: int) -> dict[str, str]:
    if not AGENTS.is_dir():
        raise FileNotFoundError(f"runner directory not found: {AGENTS}")
    states: dict[str, str] = {}
    now = datetime.now().astimezone()
    for meta in sorted(AGENTS.glob("*/status.json")):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except Exception as exc:  # a half-written status file is transient, not a lane event
            states[f"{meta.parent.name} (unreadable: {type(exc).__name__})"] = "unreadable"
            continue
        state = str(data.get("state", "?"))
        if state not in NON_TERMINAL:
            states[meta.parent.name] = state
            continue
        # Non-terminal: check liveness before staleness so a dead runner is named DEAD,
        # not merely STALE (the remediation differs: relaunch vs investigate).
        if not pid_alive(data.get("pid")):
            states[meta.parent.name] = "DEAD(pid gone)"
            continue
        last = data.get("lastEventAt")
        try:
            last_dt = datetime.fromisoformat(str(last))
        except (TypeError, ValueError):
            states[meta.parent.name] = f"{state} (lastEventAt unparsable: {last!r})"
            continue
        age_min = (now - last_dt).total_seconds() / 60
        if age_min > stale_min:
            states[meta.parent.name] = f"STALE({age_min:.0f}m silent)"
        else:
            states[meta.parent.name] = state
    return states


def load_previous() -> dict[str, str]:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def bcu_seen(previous: dict) -> bool:
    """True if a previous observation already recorded the BCU artefact.

    The BCU check must fire only on the absent -> present TRANSITION. A bare
    `.exists()` re-fires on every watcher relaunch for an artefact that landed
    days ago (seen 2026-09-22: a relaunch woke the manager on the 2026-09-21
    round-1 report). The marker is stored in the state file under a reserved
    key that can never collide with a lane name (lane dirs cannot contain ':').
    """
    return previous.get("_bcu_report_seen") is True



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=60, help="seconds between observations")
    ap.add_argument("--stale-min", type=int, default=20,
                    help="minutes of silence in a non-terminal lane before it is STALE; "
                         "keep above the runner's --stall-min (15) so the runner's own "
                         "kill+retry fires first when it is alive")
    ap.add_argument("--once", action="store_true", help="observe once, print, exit 0")
    args = ap.parse_args()

    try:
        first = read_states(args.stale_min)
    except FileNotFoundError as exc:
        print(f"WATCHER FAILURE: {exc}", flush=True)
        return 1

    previous = load_previous()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # BCU marker: kept OUT of the lane dicts entirely (a reserved key inside the
    # lane map once made the 'gone' check fire on the marker itself, 2026-09-22).
    # It fires only on the absent -> present transition during THIS watcher's
    # lifetime; a fresh launch on an existing artefact is old news, not an event.
    bcu_flag = bcu_seen(previous) or BCU_REPORT.exists()

    def persist(states: dict) -> None:
        out = {k: v for k, v in states.items() if not k.startswith("_")}
        if bcu_flag:
            out["_bcu_report_seen"] = True
        STATE_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")

    persist(first)

    if args.once:
        for lane, state in first.items():
            print(f"  {lane}: {state}")
        return 0

    print(f"watching {len(first)} lane(s) every {args.interval}s; exit on the first state change", flush=True)
    while True:
        time.sleep(args.interval)
        try:
            now_states = read_states(args.stale_min)
        except FileNotFoundError as exc:
            print(f"WATCHER FAILURE: {exc}", flush=True)
            return 1
        changes = [
            f"{lane}: {previous.get(lane, '(new)')} -> {state}"
            for lane, state in sorted(now_states.items())
            if previous.get(lane) != state
        ]
        gone = [lane for lane in previous
                if lane not in now_states and not lane.startswith("_")]
        if changes or gone:
            print("cmdc lane transition(s):", flush=True)
            for line in changes:
                print(f"  {line}", flush=True)
            for lane in gone:
                print(f"  {lane}: gone (record/lane removed)", flush=True)
            persist(now_states)
            return 0
        if BCU_REPORT.exists() and not bcu_flag:
            print(f"BCU2.10 round-1 report artefact appeared: {BCU_REPORT}", flush=True)
            bcu_flag = True
            persist(now_states)
            return 0
        previous = now_states
        persist(now_states)


if __name__ == "__main__":
    sys.exit(main())
