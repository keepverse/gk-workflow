"""python -m kvsplit <verb>

  stage    --source <legacy repo> --rev <commit> [--rules <dir>] --out <staging dir>
  residue  --staging <dir> [--kind K]      summary of residue.json, grouped by kind
  verify   --source ... --rev ... [--rules] --out ...
           stage twice into two directories and assert byte-identical output digests
  apply    --staging <dir> --workspace <Keepverse dir> [--rules] [--repo ID ...]
           --confirm-migration-start       (gate GM: only on the owner's command)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "rules"


def _cmd_stage(a: argparse.Namespace) -> int:
    from kvsplit.stage import stage
    r = stage(Path(a.source), a.rev, Path(a.rules), Path(a.out))
    rec = r.report["reconciliation"]
    print(f"source {r.report['sourceSha']}  rules {r.report['rulesDigest'][:12]}  output {r.report['outputDigest'][:12]}")
    print(f"tracked {rec['tracked']}  dropped {rec['dropped']}  unplaced {rec['unplaced']}  balanced {rec['balanced']}")
    for repo, n in rec["placedPerRepo"].items():
        print(f"  {repo:<12} {n}")
    print(f"residue {len(r.residue)}")
    for k, n in r.report["residueByKind"].items():
        print(f"  {k:<32} {n}")
    return 0


def _cmd_residue(a: argparse.Namespace) -> int:
    doc = json.loads((Path(a.staging) / "residue.json").read_text(encoding="utf-8"))
    items = [i for i in doc["items"] if not a.kind or i["kind"] == a.kind]
    by: dict[str, list[dict]] = {}
    for i in items:
        by.setdefault(i["kind"], []).append(i)
    for k in sorted(by):
        print(f"{k}  ({len(by[k])}, fix: {by[k][0]['allowedFix']})")
        for i in by[k][: a.limit]:
            loc = f"{i['path']}:{i['line']}" if "line" in i else i["path"]
            print(f"  {i['id']}  {loc}  {i['anchor']}  -- {i['detail']}")
        if len(by[k]) > a.limit:
            print(f"  ... {len(by[k]) - a.limit} more")
    return 0


def _cmd_verify(a: argparse.Namespace) -> int:
    from kvsplit.stage import stage
    out = Path(a.out)
    r1 = stage(Path(a.source), a.rev, Path(a.rules), out / "run-1")
    r2 = stage(Path(a.source), a.rev, Path(a.rules), out / "run-2")
    d1, d2 = r1.report["outputDigest"], r2.report["outputDigest"]
    same_res = [x.id for x in r1.residue] == [x.id for x in r2.residue]
    print(f"run-1 {d1}\nrun-2 {d2}\nresidue ids identical: {same_res}")
    return 0 if d1 == d2 and same_res else 1


def _cmd_apply(a: argparse.Namespace) -> int:
    from kvsplit.apply import apply
    from kvsplit.rules import load_rules
    from kvsplit.transforms import REGISTRY
    rules = load_rules(Path(a.rules), set(REGISTRY))
    ids = a.repo or rules.layout.ids()
    for line in apply(Path(a.staging), Path(a.workspace), rules.layout, ids, rules.digest, a.confirm_migration_start,
                      allow_residue=a.allow_residue, accept_overwrites=a.accept_overwrites):
        print(line)
    return 0


def _cmd_hash(a: argparse.Namespace) -> int:
    from kvsplit import hashes
    from kvsplit.rules import load_rules
    from kvsplit.transforms import REGISTRY
    if a.source:
        m = hashes.source_manifest(Path(a.source), a.rev)
    else:
        m = hashes.workspace_manifest(Path(a.workspace), load_rules(Path(a.rules), set(REGISTRY)).layout)
    hashes.dump(m, Path(a.out))
    print(f"{m['kind']} manifest: {len(m['files'])} files -> {a.out}")
    return 0


def _load(p) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _cmd_lossy(a: argparse.Namespace) -> int:
    from kvsplit import hashes
    from kvsplit.rules import load_rules
    from kvsplit.transforms import REGISTRY
    losses = hashes.lossy_check(_load(a.source_manifest), _load(Path(a.staging) / "report.json"),
                                _load(a.target_manifest), load_rules(Path(a.rules), set(REGISTRY)).layout)
    hashes.dump({"losses": [x.to_json() for x in losses]}, Path(a.out))
    by: dict[str, int] = {}
    for x in losses:
        by[x.kind] = by.get(x.kind, 0) + 1
    print(f"lossy check: {len(losses)} finding(s) {dict(sorted(by.items()))} -> {a.out}")
    return 0 if not losses else 1


def _cmd_index(a: argparse.Namespace) -> int:
    from kvsplit import hashes, index
    idx = index.build(_load(a.target_manifest), _load(Path(a.staging) / "report.json"))
    hashes.dump(idx.to_json(), Path(a.out))
    print(f"index: {len(idx.files)} files, {len(idx.moves)} moves -> {a.out}")
    return 0


def _cmd_reindex(a: argparse.Namespace) -> int:
    from kvsplit import index, reindex
    cfg = reindex.load_config(Path(a.rules) / "reindex.v1.json")
    res = reindex.reindex(Path(a.workspace), index.load(Path(a.index)), cfg)
    reindex.write(res, Path(a.workspace), a.apply, Path(a.out))
    mode = "applied" if a.apply else "dry run"
    print(f"reindex ({mode}): {len(res.rewritten)} rewritten in {len(res.changed)} document(s), "
          f"{len(res.stale)} stale, {len(res.pre_existing)} already broken before the move -> {a.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="kvsplit")
    sub = p.add_subparsers(dest="verb", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--source", required=True)
        sp.add_argument("--rev", required=True)
        sp.add_argument("--rules", default=str(DEFAULT_RULES))
        sp.add_argument("--out", required=True)

    common(sub.add_parser("stage"))
    common(sub.add_parser("verify"))
    r = sub.add_parser("residue")
    r.add_argument("--staging", required=True)
    r.add_argument("--kind")
    r.add_argument("--limit", type=int, default=20)
    ap = sub.add_parser("apply")
    ap.add_argument("--staging", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--rules", default=str(DEFAULT_RULES))
    ap.add_argument("--repo", action="append")
    ap.add_argument("--confirm-migration-start", action="store_true")
    ap.add_argument("--allow-residue", action="store_true",
                    help="move-first flow: carry residue into the post-move reindex and agent reconcile")
    ap.add_argument("--accept-overwrites", action="store_true",
                    help="apply even though staged files differ from files already committed in the "
                         "target repos; without it apply refuses, because that is silent data loss")
    h = sub.add_parser("hash")
    g = h.add_mutually_exclusive_group(required=True)
    g.add_argument("--source")
    g.add_argument("--workspace")
    h.add_argument("--rev", default="HEAD")
    h.add_argument("--rules", default=str(DEFAULT_RULES))
    h.add_argument("--out", required=True)
    lc = sub.add_parser("lossy-check")
    lc.add_argument("--source-manifest", required=True)
    lc.add_argument("--target-manifest", required=True)
    lc.add_argument("--staging", required=True)
    lc.add_argument("--rules", default=str(DEFAULT_RULES))
    lc.add_argument("--out", required=True)
    ix = sub.add_parser("index")
    ix.add_argument("--target-manifest", required=True)
    ix.add_argument("--staging", required=True)
    ix.add_argument("--out", required=True)
    ri = sub.add_parser("reindex")
    ri.add_argument("--workspace", required=True)
    ri.add_argument("--index", required=True)
    ri.add_argument("--rules", default=str(DEFAULT_RULES))
    ri.add_argument("--out", required=True)
    ri.add_argument("--apply", action="store_true")
    a = p.parse_args(argv)
    handler = {"stage": _cmd_stage, "residue": _cmd_residue, "verify": _cmd_verify, "apply": _cmd_apply,
               "hash": _cmd_hash, "lossy-check": _cmd_lossy, "index": _cmd_index, "reindex": _cmd_reindex}[a.verb]
    # A refusal is this tool's normal way of speaking, not a crash. It goes to stderr as one
    # named message with a non-zero exit; a traceback would bury the one line that says
    # what to fix, and a reader could mistake the trace for a tool defect.
    from kvsplit.apply import ApplyError
    from kvsplit.rules import RulesError
    from kvsplit.source import SourceError
    from kvsplit.stage import StageError
    try:
        return handler(a)
    except (ApplyError, RulesError, SourceError, StageError) as ex:
        print(f"kvsplit {a.verb}: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
