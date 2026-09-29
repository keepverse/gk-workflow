#!/usr/bin/env python3
"""lane-signals -- the manager's single sweep: what each lane is doing, and what it is stuck on.

WHY THIS EXISTS
    The manager used to sweep by reading `status.json` (a state label) and counting `- [ ]` lines. Both
    misled it, repeatedly, in one session:

      * `status.json` said "running, seg 4" for a lane whose own session text said "Work complete" -- a
        finished fix looked unfinished, and the critical path sat unaccepted;
      * the same label said nothing at all about a lane whose segment had been **interrupted by an
        infrastructure error**;
      * `guard.jsonl` was read as a list of denials when it logs EVERY hook decision (493 allow / 15 deny
        for one lane) -- the manager reported "506 denials" and nearly went hunting a systemic fence gap
        that did not exist;
      * three lanes returning ~12-second EMPTY segments were fed four more times before anyone measured it.

    So: two halves. SIGNALS from the runner (state, unmerged commits, real denials, drained segments) and
    CONTEXT from the lane's own pi session (what it claims to have finished, what it is stuck on, whether
    it was interrupted). A state label is not evidence; the lane's own words and the runner's logs are.

USAGE
    python .claude/cmdc-agents/scripts/lane-signals.py                # every lane with an agent dir
    python .claude/cmdc-agents/scripts/lane-signals.py --lanes tvb58,ep-4
    python .claude/cmdc-agents/scripts/lane-signals.py --tail 6       # more session context per lane
    python .claude/cmdc-agents/scripts/lane-signals.py --json         # machine-readable

READ-ONLY. It never writes, steers, spawns or stops anything: it informs the manager's decision, which is
the manager's to make (grant, widen a fence, feed with a named brief, retire a drained lane, accept a SHA).
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AGENTS = Path('.claude/cmdc-agents/agents')
SESSIONS = Path(os.path.expanduser('~/.pi/agent/sessions'))
IDLE_STATES = {'partial', 'done', 'failed', 'retry_wait'}


def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def read_jsonl(p: Path) -> list:
    out = []
    try:
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return out


def git(repo: Path, *args) -> str:
    try:
        r = subprocess.run(['git', *args], cwd=str(repo), capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        return r.stdout.strip() if r.returncode == 0 else ''
    except Exception:
        return ''


def encode_cwd(path: str) -> str:
    """pi encodes a session directory as '--' + cwd with every non-alphanumeric as '-' + '--'."""
    return '--' + re.sub(r'[^A-Za-z0-9]', '-', path) + '--'


def session_context(cwd: str, tail: int) -> dict:
    """The lane's own words: last N assistant text blocks, plus interruption/permission markers."""
    d = SESSIONS / encode_cwd(cwd)
    if not d.is_dir():                                    # fall back to a glob on the lane worktree name
        name = Path(cwd).name
        hits = [p for p in SESSIONS.glob(f'*{name}*') if p.is_dir()]
        d = hits[0] if hits else None
    if not d or not d.is_dir():
        return {'session': None, 'texts': [], 'markers': []}
    files = sorted(glob.glob(str(d / '*.jsonl')), key=os.path.getmtime)
    if not files:
        return {'session': None, 'texts': [], 'markers': []}
    rows = read_jsonl(Path(files[-1]))
    texts, markers = [], []
    for r in rows:
        if r.get('type') not in ('message', 'assistant', 'agent_message'):
            continue
        msg = r.get('message') or r
        content = msg.get('content')
        blocks = []
        if isinstance(content, list):
            blocks = [c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text']
        elif isinstance(content, str):
            blocks = [content]
        for t in blocks:
            t = (t or '').strip()
            if not t:
                continue
            texts.append(t)
            low = t.lower()
            for needle, label in (('infrastructure error', 'INTERRUPTED (infrastructure error)'),
                                  ('interrupted', 'INTERRUPTED'),
                                  ('work complete', 'claims COMPLETE'),
                                  ('permission denied', 'PERMISSION DENIED'),
                                  ('refus', 'refusal mentioned'),
                                  ('blocked', 'blocked mentioned')):
                if needle in low and label not in markers:
                    markers.append(label)
    return {'session': os.path.basename(files[-1]), 'texts': texts[-tail:], 'markers': markers}


def lane_row(lane: str, repo: Path, tail: int) -> dict:
    adir = AGENTS / lane
    status = read_json(adir / 'status.json')
    meta = read_json(adir / 'meta.json')
    state, seg = status.get('state'), status.get('segment')

    branch = meta.get('branch') or f'cmdc/{lane}'
    ahead = git(repo, 'rev-list', '--count', f'HEAD..{branch}')

    # Drained-lane signal: a result event that finished fast with no output is a spent context, not a
    # judgement -- measured, never guessed (three lanes at ~12s/EMPTY were fed four times before this
    # existed).
    results = [r for r in read_jsonl(adir / 'events.jsonl') if r.get('type') == 'result'][-4:]
    segs = [{'s': round((r.get('durationMs') or 0) / 1000), 'out': len((r.get('finalText') or '').strip())}
            for r in results]
    drained = bool(segs) and all(s['out'] == 0 and s['s'] < 40 for s in segs)

    # REAL denials: guard.jsonl logs every decision, so count only decision != allow (the manager's own
    # error was reading its length as a denial count).
    guard = read_jsonl(adir / 'guard.jsonl')
    denies = [r for r in guard if r.get('decision') not in (None, 'allow')]
    deny_reasons = collections.Counter(str(r.get('reason'))[:70] for r in denies)

    # Is an acceptance artefact already written FOR THIS TIP? (The artefact is named for the 8-char SHA, so a
    # 9-char check reports a false PENDING -- and a stale artefact for an already-merged SHA reads as fresh.)
    tip8 = git(repo, 'rev-parse', '--short=8', branch)
    art = repo / '.claude/cmdc-agents/acceptance' / f'{lane}-{tip8}.json'
    accepted = None
    if art.exists():
        accepted = read_json(art).get('verdict')

    # The program ledger, checked rather than assumed (the DONE bar requires `anchor-ledger.py check` to pass).
    ledger = meta.get('ledger') or ''
    ledger_state = ''
    if ledger and (repo / ledger).exists():
        try:
            r = subprocess.run([sys.executable, 'scripts/anchor-ledger.py', ledger, 'check'], cwd=str(repo),
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            ledger_state = (r.stdout.strip().splitlines() or [''])[-1][:60]
        except Exception as e:
            ledger_state = f'check failed to run: {e}'

    # The runner's own last summary -- the lane's note, which often states completion before status catches up.
    last_note = ''
    notes = read_jsonl(adir / 'notes.jsonl')
    if notes:
        last = notes[-1]
        last_note = str(last.get('note') or last.get('text') or last)[:200]

    ctx = session_context(meta.get('cwd', ''), tail)
    return {
        'lane': lane, 'state': state, 'segment': seg, 'ahead': int(ahead or 0),
        'segments': segs, 'drained': drained,
        'allow': len(guard) - len(denies), 'deny': len(denies),
        'deny_reasons': deny_reasons.most_common(3),
        'acceptance_candidate': state in IDLE_STATES and int(ahead or 0) > 0,
        'tip': tip8, 'accepted': accepted, 'ledger': ledger, 'ledger_state': ledger_state,
        'last_note': last_note,
        'session': ctx['session'], 'markers': ctx['markers'], 'texts': ctx['texts'],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description='manager sweep: lane signals + the lane\'s own session context')
    ap.add_argument('--repo', default='.')
    ap.add_argument('--lanes', default='')
    ap.add_argument('--tail', type=int, default=2, help='assistant text blocks per lane (default 2)')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    repo = Path(a.repo).resolve()

    lanes = [x.strip() for x in a.lanes.split(',') if x.strip()] or \
            sorted(p.name for p in AGENTS.iterdir() if p.is_dir() and (p / 'status.json').exists())
    rows = [lane_row(l, repo, a.tail) for l in lanes]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    print(f'{"lane":13s} {"state":10s} {"seg":>4s} {"ahead":>5s} {"allow":>5s} {"DENY":>4s}  flags')
    for r in rows:
        flags = []
        if r['acceptance_candidate'] and not r['accepted']:
            flags.append('ACCEPTANCE-CANDIDATE (no artefact for this tip)')
        elif r['acceptance_candidate'] and r['accepted']:
            flags.append(f"acceptance WRITTEN: {r['accepted']} -- merge pending, do not re-run")
        if r['ledger_state'] and 'OK' not in r['ledger_state']:
            flags.append(f"LEDGER: {r['ledger_state']}")
        if r['drained']:
            flags.append('DRAINED (fast empty segments) -- retire+replace, do not feed')
        if r['deny']:
            flags.append(f'DENIED×{r["deny"]}')
        print(f'  {r["lane"]:11s} {str(r["state"]):10s} {str(r["segment"]):>4s} {r["ahead"]:>5d} '
              f'{r["allow"]:>5d} {r["deny"]:>4d}  {", ".join(flags) or "-"}')
        for reason, n in r['deny_reasons']:
            print(f'       deny×{n}: {reason}   <- a permission refusal is a GRANT REQUEST: escalate, do not retry')
        if r['last_note']:
            print(f'       runner note: {r["last_note"]}')
    print()
    for r in rows:
        if not r['texts'] and not r['markers']:
            continue
        print(f'--- {r["lane"]} session ({r["session"] or "none"}) markers: {", ".join(r["markers"]) or "-"}')
        for t in r['texts']:
            print('    ' + t[:300].replace('\n', ' '))
    return 0


if __name__ == '__main__':
    sys.exit(main())
