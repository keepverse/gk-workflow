"""Classify every remaining repo-root helper by what its CALL SITES join onto it.

The previous attempt guessed one meaning per helper and was disproved by 27 test
failures: FindDataDir() serves both Path.Combine(FindDataDir(), "seed", ...) (which
wants the gk-data pack) and `var dir = FindDataDir();` (which wants a data directory
in its own right). A helper's name says nothing about which root it means; only its
call sites do. So read them.

Emits a decision table, not an edit. Each row is one helper name with the evidence
that decides it:

  content   every call joins "seed" or "generated"  -> KeepverseRoots.Content()
  core      every call joins "tuning", or names src/tests/scripts -> KeepverseRoots.Core()
  BOTH      the two kinds appear                      -> the helper means two things and
                                                        must be split into two named
                                                        helpers with call sites divided
  bare      no call site joins a segment              -> cannot be decided from paths;
                                                        needs a read of what it returns

Anything already delegating to a KeepverseRoots accessor is reported as done, and the
temp-fixture helpers are excluded because they CREATE directories and would break.
"""

import collections
import pathlib
import re
import sys

sys.path.insert(0, r"C:\Users\NeneScarlet\AppData\Local\Temp")
import kvcsharp as CS  # noqa: E402

ROOT = pathlib.Path(r"D:\Works\source\plant-vs-zombie-rise-of-summoner")
USING = "using FusionRpg.Core.Workspace;"

# Create a fixture rather than resolve a root. Collapsing these would delete them.
EXCLUDE = {"NewTempRoot", "NewTempDir", "NewDataDir", "FreshTempDir", "MakeTuningDir"}

CONTENT_SEGS = {"seed", "generated"}
CORE_SEGS = {"tuning", "src", "tests", "scripts", "tools", "docs"}
AUTHORED_SEGS = {"content"}

DEF = re.compile(r"static\s+string\??\s+(\w+)\s*\(")
ROOTISH = re.compile(r"(?:Root|Dir|Repo|Base|Dir)$|^(?:Find|Read|Get|Repo)\w*(?:Root|Dir|Repo|File)")


def body_of(text, masked, m):
    """Source of a member's body: from after '(' to its '}' or its ';'."""
    i = m.end()
    arrow = re.match(r"\s*(=>|\{)", masked[i:i + 8])
    if not arrow:
        return ""
    if arrow.group(1) == "=>":
        semi = text.find(";", i)
        return text[i: semi if semi > 0 else i + 600]
    ob = text.find("{", i)
    end = CS.match_in(masked, ob) if ob >= 0 else -1
    return text[i: end + 1] if end > 0 else ""


def segments_in(fragment, limit=260):
    """Path segments a fragment joins, in order, as (segment, kind) pairs.

    Two shapes matter and they answer different questions:
      Path.Combine(X(), "data", "seed", ...)   -> X is a bare root and the CALLER
                                                  names the tree, so the caller decides.
      Path.Combine(X(), "power-scale.v2.json") -> X already names its own tree
                                                  (X returned .../data/tuning), so the
                                                  helper's OWN body decides.
    Both are answered by collecting every string literal in the fragment and asking
    which trees appear; a bare filename contributes nothing, so it cannot mislead.

    The literal search runs on the RAW fragment, not a masked copy. Masking blanks out
    string contents, which is the point of masking for brace counting and precisely
    wrong here - an early version of this function masked first and therefore reported
    every helper as bare.
    """
    out = []
    head = fragment[:limit]
    # a literal inside a line comment is not a path segment; drop those cheaply
    head = re.sub(r"//[^\n]*", "", head)
    head = re.sub(r"/\*.*?\*/", "", head, flags=re.S)
    for lit in re.findall(r'"([a-z_]+)"', head):
        if lit in CONTENT_SEGS:
            out.append((lit, "content"))
        elif lit in AUTHORED_SEGS:
            out.append((lit, "authored"))
        elif lit in CORE_SEGS:
            out.append((lit, "core"))
    return out


def classify(pairs):
    kinds = {k for _, k in pairs}
    if "content" in kinds and "core" in kinds:
        return "BOTH"
    if "content" in kinds:
        return "content"
    if "authored" in kinds:
        return "authored"
    if "core" in kinds:
        return "core"
    return "bare"


def main():
    # ---- 1. definitions, and what each body itself names ----------------
    # Load every test file ONCE, masked and raw. Re-reading per helper name turns a
    # 45-name pass into 45 x 1500 file reads, which is minutes instead of seconds.
    corpus = []
    for p in sorted(ROOT.glob("tests/**/*.cs")):
        if any(x in p.parts for x in ("bin", "obj")):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        corpus.append((str(p), t, CS.mask(t)))

    defs = collections.defaultdict(list)
    bodies = collections.defaultdict(list)
    for rel, t, masked in corpus:
        for m in DEF.finditer(t):
            name = m.group(1)
            if name in EXCLUDE or not ROOTISH.search(name):
                continue
            body = body_of(t, masked, m)
            delegates = bool(re.search(
                r"(KeepverseRoots|ContentRoot|CoreRoot|WorkspaceRoot)", body or t[m.end():m.end() + 700]))
            defs[name].append((rel, delegates))
            if not delegates:
                bodies[name].append(body)

    rows = []
    for name, sites in sorted(defs.items()):
        done = sum(1 for _, d in sites if d)
        if done == len(sites):
            rows.append((name, len(sites), "already-delegates", 0, 0, done, ""))
            continue
        own = [kv for b in bodies[name] for kv in segments_in(b, 400)]
        own_v = classify(own)
        if own_v != "bare":
            rows.append((name, len(sites), f"body:{own_v}", len(own), 0, done,
                         f"names {'/'.join(sorted({s for s, _ in own}))}"))
            continue
        pairs = []
        call_re = re.compile(r"(?<![\w.])" + re.escape(name) + r"\s*\(")
        for rel, t, masked in corpus:
            for m in call_re.finditer(masked):
                pairs += segments_in(t[m.end(): m.end() + 260])
        rows.append((name, len(sites), f"calls:{classify(pairs)}", len(pairs), 0, done,
                     f"joins {'/'.join(sorted({s for s, _ in pairs})) or '(nothing)'}"))

    print("  helper                       defs  verdict             signals  done  evidence")
    print("  " + "-" * 100)
    for name, n, verdict, sig, _, done, ev in rows:
        print(f"  {name:<28} {n:>4}  {verdict:<20} {sig:>7}  {done:>4}  {ev}")
    tally = collections.Counter(r[2] for r in rows)
    print()
    print("  verdicts:", dict(tally))
    open_rows = [r for r in rows if "BOTH" in r[2] or r[2].endswith(":bare")]
    print(f"  helpers still needing a human decision: {len(open_rows)} of {len(rows)}")
    for r in open_rows:
        print(f"     {r[0]:<28} {r[2]}")


if __name__ == "__main__":
    main()

