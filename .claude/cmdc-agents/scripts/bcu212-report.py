#!/usr/bin/env python3
"""BCU2.12 report artefact: readings, never assertions.

Run from the worktree after `bcu212-full-run.ps1`. Writes `tasks/reports/BCU2.12-full-run.json`.
Every section is guarded: a reporting failure must never lose the run, so each records either its
reading or the exception that stopped it. The launcher passes its selected interpreter with
`--python`; when omitted this process uses `sys.executable`. Malformed node/species evidence is
written as an explicit error and makes the report return non-zero after the artefact is saved.

Modelled on `bcu211-report.py`. What is specific to BCU2.12 (passive-tree J9/J10):

* the run's population is the ROSTER's own length, never the spec's stale "840" (`_index.json` holds
  904 ids today; `load_roster()` deliberately never hardcodes the count);
* the J10 census is derived from the **ledger + the committed node files**, not from the harness's
  `_j9_batch_run_results.json` -- that file is overwritten by every pass, so after the resume pass it
  describes only the last pass (measured: it read `acceptedNodes: 0` while 40 real nodes sat on disk).
  The batch file is still reported, labelled as last-pass-only;
* a species is called COMPLETE only when it has 40 ledger-backed nodes AND its
  `gk-data/packs/fusion/data/seed/passive-tree/species/<id>.json` codex supplement -- the spec's own rule is that a tree
  without a Codex sentence never ships, so "nodes written" alone is not completeness.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "tasks" / "reports" / "BCU2.12-full-run.json"
SEED = ROOT / "data" / "seed" / "passive-tree"
EXPECTED_NODES_PER_SPECIES = 40


class ReportCommandError(RuntimeError):
    """A report input command failed or returned no usable reading."""


class MalformedEvidenceError(ValueError):
    """A committed evidence artifact could not be read as its declared shape."""


class _CommandResult(str):
    """String output plus the process status, while remaining string-compatible for old callers."""

    returncode: int

    def __new__(cls, text: str, returncode: int = 0):
        value = str.__new__(cls, text)
        value.returncode = returncode
        return value


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def sh(*args: str) -> _CommandResult:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=600)
        text = (r.stdout or "").strip()
        if r.returncode != 0:
            detail = (r.stderr or "").strip()
            if detail:
                text = f"{text}\n{detail}".strip()
        return _CommandResult(text, r.returncode)
    except Exception as exc:  # pragma: no cover - diagnostic only
        return _CommandResult(f"<{type(exc).__name__}: {exc}>", 1)


def roster_ids(python_command: str = sys.executable) -> "list[str]":
    result = sh(
        python_command, "-c",
        "from seedsmith.adapters.trees.species.roster import load_roster;"
        "print('\\n'.join(load_roster().species_ids))",
    )
    returncode = getattr(result, "returncode", 0)
    if returncode != 0:
        raise ReportCommandError(
            f"roster command exited {returncode}: {result}")
    ids = [line.strip() for line in str(result).splitlines() if line.strip()]
    if not ids:
        raise ReportCommandError("roster command returned no species ids")
    return ids


def _record_evidence_error(path: Path, detail: str, errors: "dict[str, str] | None") -> None:
    name = _relative_path(path)
    message = f"{name}: {detail}"
    if errors is None:
        raise MalformedEvidenceError(message)
    errors[name] = message


def node_counts(*, errors: "dict[str, str] | None" = None) -> "dict[str, int]":
    """Read node documents, naming every malformed artifact instead of treating it as zero nodes."""
    out: "dict[str, int]" = {}
    for path in sorted((SEED / "nodes").glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(doc, dict):
                raise ValueError("document root is not an object")
            nodes = doc.get("nodes")
            if not isinstance(nodes, list):
                raise ValueError("document has no nodes list")
            if any(not isinstance(node, dict) for node in nodes):
                raise ValueError("nodes list contains a non-object row")
        except Exception as exc:
            _record_evidence_error(path, f"{type(exc).__name__}: {exc}", errors)
            continue
        out[path.stem] = len(nodes)
    return out


def resolved_species_ids(*, errors: "dict[str, str] | None" = None) -> "set[str]":
    """Species supplements that really carry a Codex sentence.

    ``finalize_codex`` deliberately writes a named failure document at this same path when its bounded
    retry ends unresolved. File existence alone therefore cannot mean "complete" — the old report
    would count every such failure as shipped Codex content. A malformed document is a report error,
    never an ordinary unresolved species.
    """
    resolved: "set[str]" = set()
    for path in sorted((SEED / "species").glob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(document, dict):
                raise ValueError("document root is not an object")
            if "codexSummary" not in document:
                raise ValueError("document has no codexSummary field")
            summary = document["codexSummary"]
            if summary is None:
                reason = document.get("codexUnresolvedReason")
                if not isinstance(reason, str) or not reason.strip():
                    raise ValueError("null codexSummary has no named codexUnresolvedReason")
            elif not isinstance(summary, str) or not summary.strip():
                raise ValueError("codexSummary must be a non-empty string or null")
            else:
                resolved.add(path.stem)
        except Exception as exc:
            _record_evidence_error(path, f"{type(exc).__name__}: {exc}", errors)
    return resolved


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--python", default=sys.executable,
        help="the Python command used for roster and family-check subprocesses")
    args = parser.parse_args(argv)
    python_command = (args.python or "").strip() or sys.executable

    command_errors: "dict[str, str]" = {}
    out: "dict[str, object]" = {
        "job": "BCU2.12 passive-tree J9 species run + J10 census",
        "pythonCommand": python_command,
        "head": sh("git", "rev-parse", "--short", "HEAD"),
        "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
    }

    try:
        ids = roster_ids(python_command)
    except ReportCommandError as exc:
        ids = []
        command_errors["roster"] = str(exc)
    out["rosterSpecies"] = len(ids)
    roster = set(ids)

    # Pass an error sink so one corrupt artifact does not abort the diagnostic report. The sink is
    # what keeps malformed evidence from being silently omitted; main() marks the report failed and
    # names every artifact before it returns.
    node_errors: "dict[str, str]" = {}
    species_errors: "dict[str, str]" = {}
    counts = node_counts(errors=node_errors)
    meta = resolved_species_ids(errors=species_errors)

    # --- ledger: the resume state and the per-species progress of record -----------------------
    ledger_rows: "dict[str, int]" = {}
    ledger_accepted: "dict[str, int]" = {}
    try:
        ledger = json.loads((SEED / "_runs" / "tree-language.ledger.json").read_text(encoding="utf-8"))
        done = ledger.get("done", {})
        out["ledgerDoneRows"] = len(done)
        for subject, row in done.items():
            sid = subject.split(":", 1)[0]
            ledger_rows[sid] = ledger_rows.get(sid, 0) + 1
            if isinstance(row, dict) and row.get("record"):
                ledger_accepted[sid] = ledger_accepted.get(sid, 0) + 1
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        out["ledgerError"] = detail
        command_errors["ledger"] = detail

    # --- J10 census over the ROSTER's own ids --------------------------------------------------
    complete, nodes_no_codex, partial, untouched = [], [], {}, []
    malformed: "dict[str, list[str]]" = {}
    for sid in ids:
        malformed_reasons = []
        for directory, errors in (("nodes", node_errors), ("species", species_errors)):
            artifact = _relative_path(SEED / directory / f"{sid}.json")
            if artifact in errors:
                malformed_reasons.append(errors[artifact])
        if malformed_reasons:
            malformed[sid] = malformed_reasons
            continue

        nodes = counts.get(sid, 0)
        has_meta = sid in meta
        ledger_backed = ledger_accepted.get(sid, 0)
        if (nodes >= EXPECTED_NODES_PER_SPECIES
                and ledger_backed >= EXPECTED_NODES_PER_SPECIES and has_meta):
            complete.append(sid)
        elif nodes > 0 and not has_meta:
            nodes_no_codex.append(sid)
        elif nodes == 0 and (ledger_rows.get(sid, 0) or sid not in counts):
            if ledger_rows.get(sid, 0):
                partial[sid] = {"ledgerRows": ledger_rows[sid],
                                "ledgerAccepted": ledger_accepted.get(sid, 0), "nodesOnDisk": nodes}
            else:
                untouched.append(sid)
        else:
            partial[sid] = {"ledgerRows": ledger_rows.get(sid, 0),
                            "ledgerAccepted": ledger_accepted.get(sid, 0), "nodesOnDisk": nodes}

    out["evidenceErrors"] = {"nodes": node_errors, "species": species_errors}
    out["census"] = {
        "complete": {"count": len(complete), "sample": complete[:10]},
        "nodesWithoutCodexSupplement": {"count": len(nodes_no_codex), "sample": nodes_no_codex[:10]},
        "startedIncomplete": {"count": len(partial), "sample": dict(list(partial.items())[:10])},
        "malformedEvidence": {"count": len(malformed), "sample": dict(list(malformed.items())[:10])},
        "untouched": len(untouched),
        "genericTrees": {
            "count": len([k for k in counts if k not in roster]),
            "total": sum(v for k, v in counts.items() if k not in roster),
        },
    }

    # --- the harness's own per-pass file (LAST PASS ONLY -- see the module docstring) -----------
    batch = ROOT / "tools" / "seedsmith" / "_j9_batch_run_results.json"
    try:
        rows = json.loads(batch.read_text(encoding="utf-8"))
        out["batchResultsLastPassOnly"] = {
            "path": str(batch.relative_to(ROOT)).replace("\\", "/"),
            "species": len(rows),
            "favourUnresolved": Counter(r.get("favourUnresolvedReason") or "<resolved>" for r in rows).most_common(5),
            "nodeKeyRefused": sum(1 for r in rows if r.get("nodeKeyRefusedReason")),
            "hardGateFailures": [r for r in rows if r.get("hardGate")],
            "codexUnresolved": Counter(r.get("codexUnresolvedReason") or "<resolved>" for r in rows).most_common(5),
            "metadataWritten": sum(1 for r in rows if r.get("metadataWritten")),
            "acceptedNodesThisPass": sum(int(r.get("outcomeCounts", {}).get("accepted", 0)) for r in rows),
            "sample": rows[:3],
        }
    except FileNotFoundError:
        out["batchResultsLastPassOnly"] = "absent -- the harness had not run when the report was written"
    except Exception as exc:
        out["batchResultsLastPassOnly"] = f"{type(exc).__name__}: {exc}"

    check_result = sh(python_command, "-m", "seedsmith", "check", "--family", "PassiveTree")
    check_exit = getattr(check_result, "returncode", 0)
    out["checkFamilyPassiveTreeTail"] = str(check_result).splitlines()[-8:]
    if check_exit != 0:
        command_errors["PassiveTreeCheck"] = f"exit {check_exit}: {check_result}"
    out["gitStatusPorcelainCount"] = len([l for l in sh("git", "status", "--porcelain").splitlines() if l.strip()])
    out["diffStatTail"] = sh("git", "diff", "--stat").splitlines()[-1:] or []

    out["commandErrors"] = command_errors
    out["evidenceStatus"] = "error" if node_errors or species_errors else "ok"
    out["reportStatus"] = "error" if command_errors or node_errors or species_errors else "ok"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False)[:2500])
    print(f"REPORT_STATUS={out['reportStatus']}")
    print(f"ARTEFACT={OUT}")
    return 1 if out["reportStatus"] == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
