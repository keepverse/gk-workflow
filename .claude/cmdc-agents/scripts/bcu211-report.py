#!/usr/bin/env python3
"""BCU2.11 report artefact: readings, never assertions.

Run from the corpus-bcu211 worktree after the full item fill. Writes
`tasks/reports/BCU2.11-full-run.json`. Every step is guarded: a reporting failure must never lose the run,
so each section records either its reading or the exception that stopped it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "tasks" / "reports" / "BCU2.11-full-run.json"


def sh(*args: str) -> str:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120)
        return (r.stdout or "").strip()
    except Exception as exc:  # pragma: no cover - diagnostic only
        return f"<{type(exc).__name__}: {exc}>"


def main() -> int:
    out: dict[str, object] = {
        "job": "BCU2.11 item-seedgen full run",
        "head": sh("git", "rev-parse", "--short", "HEAD"),
        "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
    }

    items = ROOT / "data" / "seed" / "items"
    try:
        files = sorted(p for p in items.rglob("*.json") if p.is_file())
        out["itemJsonFiles"] = len(files)
        kinds = Counter(p.relative_to(items).parts[0] for p in files if len(p.relative_to(items).parts) > 1)
        out["itemJsonFilesByKind"] = dict(kinds.most_common())
    except Exception as exc:
        out["itemJsonFilesError"] = f"{type(exc).__name__}: {exc}"

    try:
        ledgers = sorted(items.rglob("*ledger*.jsonl"))
        out["ledgerFiles"] = [str(p.relative_to(ROOT)).replace("\\", "/") for p in ledgers]
        summary: dict[str, dict[str, int]] = {}
        for lp in ledgers:
            outcomes: Counter = Counter()
            for line in lp.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    outcomes["<unparseable>"] += 1
                    continue
                outcomes[str(row.get("outcome") or row.get("status") or row.get("state") or "?")] += 1
            summary[str(lp.relative_to(ROOT)).replace("\\", "/")] = dict(outcomes.most_common())
        out["ledgerOutcomes"] = summary
    except Exception as exc:
        out["ledgerError"] = f"{type(exc).__name__}: {exc}"

    out["gitStatusPorcelainCount"] = len(
        [l for l in sh("git", "status", "--porcelain").splitlines() if l.strip()]
    )
    out["diffStatTail"] = sh("git", "diff", "--stat").splitlines()[-1:] or []

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False)[:2000])
    print(f"ARTEFACT={OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
