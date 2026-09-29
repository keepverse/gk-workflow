"""Resolve a verification-boundaries merge conflict as a union -- boundaries AND projects.

Two unions, because getting only the first one is a real failure mode that already happened:

  * `boundaries` -- both sides only ADD entries (this script refuses if any entry differs),
    so the union is ours' list plus theirs' added entries.
  * `projects`   -- a new boundary entry names a project, and a branch may add that project
    key in the same commit. Merging only the list leaves the entry naming a project that
    does not exist, and the guard then fails with `unknown project: <key>` (and, for a
    pytest lane, `testFiles only allowed on a pytest project`). Measured 2026-09-23.

`knownRed` is unioned by (project, test) for the same reason.

Formatting: the file keeps `projects` arrays on single lines and `boundaries` as multi-line
objects, so a json.dumps round-trip would churn the whole file. Every insertion here is
textual, and the result is parsed BEFORE it is written -- a bad insertion leaves the file
untouched.

usage: python union-verification-registry.py <branch> [--file gk-core/scripts/verification-boundaries.v1.json]
"""
import argparse
import json
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("branch")
ap.add_argument("--file", default="scripts/verification-boundaries.v1.json")
args = ap.parse_args()
PATH = args.file

ours_text = open(PATH, encoding="utf-8").read()
theirs_text = subprocess.run(["git", "show", f"{args.branch}:{PATH}"],
                             capture_output=True, text=True, check=True).stdout
O = json.loads(ours_text)
T = json.loads(theirs_text)


def entry_span(text, key):
    """Verbatim line span of the boundary entry whose id is `key` (brace-matched, string-aware)."""
    i = text.index('"id": "%s"' % key)
    start = text.rindex("{", 0, i)
    depth = 0
    instr = False
    esc = False
    for j in range(start, len(text)):
        c = text[j]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[start:j + 1]
    raise AssertionError("unclosed entry: " + key)


# ---- boundaries -------------------------------------------------------------------------
ob = {b["id"]: b for b in O["boundaries"]}
tb = {b["id"]: b for b in T["boundaries"]}
only_t = sorted(set(tb) - set(ob))
differing = [i for i in set(ob) & set(tb) if ob[i] != tb[i]]
print("  boundaries: ours %d | theirs %d | only theirs %s | differing %s"
      % (len(O["boundaries"]), len(T["boundaries"]), only_t, differing[:6]))
if differing:
    raise SystemExit("  REFUSING: an entry was MODIFIED on both sides -- union is not safe here")

lines = ours_text.split("\n")
if only_t:
    kr = next(i for i, l in enumerate(lines) if l.strip().startswith('"knownRed"'))
    close = kr - 1
    while not lines[close].strip().startswith("]"):
        close -= 1
    if not lines[close - 1].rstrip().endswith(","):
        lines[close - 1] = lines[close - 1].rstrip() + ","
    blocks = [entry_span(theirs_text, i) for i in only_t]
    lines[close:close] = [b + ("," if k < len(blocks) - 1 else "") for k, b in enumerate(blocks)]

# ---- projects (and knownRed) ------------------------------------------------------------
missing_p = sorted(set(T["projects"]) - set(O["projects"]))
if missing_p:
    bi = next(i for i, l in enumerate(lines) if l.strip().startswith('"boundaries"'))
    close = bi - 1
    while lines[close].strip() != "},":
        close -= 1
    if not lines[close - 1].rstrip().endswith(","):
        lines[close - 1] = lines[close - 1].rstrip() + ","
    ins = []
    for k in missing_p:
        v = T["projects"][k]
        if isinstance(v, dict):
            ins.append('    "%s": {' % k)
            for kk, vv in v.items():
                ins.append('      "%s": %s%s' % (kk, json.dumps(vv), "," if kk != list(v)[-1] else ""))
            ins.append("    },")
        else:
            ins.append('    "%s": %s,' % (k, json.dumps(v)))
    if ins:
        ins[-1] = ins[-1].rstrip(",")
    lines[close:close] = ins
print("  projects: ours %d | theirs %d | missing %s" % (len(O["projects"]), len(T["projects"]), missing_p))

out = "\n".join(lines)
d = json.loads(out)  # validate BEFORE writing
ids = [b["id"] for b in d["boundaries"]]
missing_after = sorted(set(T["projects"]) - set(d["projects"]))
print("  result: boundaries=%d projects=%d knownRed=%d | no dup ids=%s | projects complete=%s"
      % (len(d["boundaries"]), len(d["projects"]), len(d["knownRed"]),
         len(ids) == len(set(ids)), not missing_after))
if missing_after:
    raise SystemExit("  REFUSING to write: projects still incomplete: %s" % missing_after)
with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(out)
print("  written")
