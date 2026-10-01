#!/usr/bin/env python3
"""
Doc-citation audit - a `file:line` in a document must resolve, or it is not evidence.

Standard: docs/DESIGN-GATE.md section 0 ("read -> verify against code -> propose") and its rule that
**a comment is not evidence**. This audit enforces the weaker, mechanical half of that rule: a
citation nobody can open is not a citation, whatever it claims.

    D1  the cited file exists
    D2  the cited line is inside that file
    D3  a citation that cannot be resolved unambiguously is reported, never guessed
    D4  an ideal doc whose own map says approved/authorized/in use, while its status line still
        says it isn't, and it carries no status banner
    D5  a line-numbered citation into a JSON registry still holds the entry the sentence names

Gating (spec-doc-citation-gate.md, 2026-09-20): D3 is HIGH outside docs/research/ and prior-art
sections (an ambiguous line-numbered citation cannot be opened either, so it is no longer a lesser
finding than D1/D2 there); D4 is always HIGH where it fires. `--strict` fails on D1/D2 HIGH plus
D3 plus D4.

Why this exists (2026-09-18). Two audits spent roughly ninety minutes of agent time re-reading
documents against code. Between them they found ~40 defects, and almost every one was mechanical:
a `file:line` that no longer resolved, or a count that had moved. The single most damaging class
was the **stale negative** - "X has zero production callers", "no kind writes an element payload",
"the corpus does not exist" - because a stale positive merely misleads, while a stale negative
licenses rebuilding something that already works. That is the 2026-08-29 aura incident exactly:
four inert paths reported as architectural limits, a feature declared half-impossible, an hour lost.

This script reproduces the citation half of that audit in about two seconds. It cannot judge whether
a claim is true; it can prove that the evidence offered for it is unopenable, which is enough to stop
the claim being quoted.

Precision over coverage, per `audit-magic-numbers.py`'s own docstring and the lesson behind it
(`audit-overflow.py`'s first run: 121 findings, every one a false positive). Seven exemptions below
exist for that reason, and each says what it is for.

Usage (repo root):
    python scripts/audit-doc-citations.py                 # full report
    python scripts/audit-doc-citations.py --summary       # per-document counts only
    python scripts/audit-doc-citations.py --targets D2    # bare file:line list for targeted work
    python scripts/audit-doc-citations.py --scope docs/architecture
    python scripts/audit-doc-citations.py --strict        # exit 1 on HIGH findings

Exit codes: 0 = report produced (default, even with findings), 1 = HIGH findings and --strict,
2 = usage error.
"""
import argparse
import io
import os
import re
import subprocess
import sys
from collections import defaultdict
# `keepverse_roots` is gk-CORE's, this script is gk-workflow's, so the sibling resolution below needs
# that directory on the path. The same two-line insert every other tool in this workspace uses, copied
# from gk-fusion/scripts/guard-single-writer.py:53-54. Without it the import is guarded, returns nothing,
# and the change reads as a fix that did nothing - which is worse than not making it. `os.path` rather
# than `pathlib`, because this module uses `os` throughout and imports no `Path`.
_HERE = os.path.dirname(os.path.abspath(__file__))
for _extra in (os.path.join(_HERE, "lib"),
               os.path.join(os.path.dirname(_HERE), "gk-core", "scripts", "lib")):
    if os.path.isdir(_extra) and _extra not in sys.path:
        sys.path.insert(0, _extra)

# --- what counts as a citation ---------------------------------------------------------------

# Backtick-quoted, ends in a source extension, optional `:line` or `:line-line`.
CITATION = re.compile(
    r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:cs|ts|tsx|js|jsx|py|json|ps1|csproj|yml|yaml))"
    r"(?::(\d+)(?:\s*[-–]\s*\d+)?)?`")

# DOTPATH_CITATION - a citation into a dot-directory (`.claude/…`, `.kilo/…`, `.commandcode/…`).
#
# Measured 2026-09-26: `CITATION` above requires the token to start with `[A-Za-z0-9_]`, so EVERY
# dot-directory citation in the repo was invisible to this audit — 95 of them, 74 distinct tokens,
# across 1693 documents. That is how `.claude/cmdc-agents/scripts/live-slot.ps1` sat in AGENTS.md's
# own tooling table pointing at a file that does not exist (the real one is `scripts/live-slot.ps1`)
# while the audit reported AGENTS.md clean.
#
# The slash in the first segment is load-bearing, and it is what keeps this from inventing citations.
# A leading dot alone is not a path: `` `.v1.json` ``, `` `.test.ts` `` and `` `.Tests.csproj` `` are
# the tail of a path whose head sits in an earlier backtick run, and matching them would report a
# dead file for every such fragment in the corpus. A dot-DIRECTORY is unambiguous, so only that is
# recognised here; a bare dotfile (`.mcp.json`) is handled by EXEMPT 1, which already names it.
DOTPATH_CITATION = re.compile(
    r"`(\.[A-Za-z0-9_-]+(?:/[A-Za-z0-9_.-]+)+"
    r"\.(?:cs|ts|tsx|js|jsx|py|json|ps1|csproj|yml|yaml))"
    r"(?::(\d+)(?:\s*[-–]\s*\d+)?)?`")

FENCE = re.compile(r"^\s*(```|~~~)")

# EXEMPT 1 - files that are gitignored on purpose. `AGENTS.md`/`CLAUDE.md` are local-only assistant
# config (AGENTS.md says so itself), and `.mcp.json` likewise. They are cited constantly and
# correctly, and `git ls-files` will never list them.
EXEMPT_BASENAMES = {"AGENTS.md", "CLAUDE.md", ".mcp.json", "package-lock.json"}
# Same reason, found 2026-09-19 when verify-change.ps1 began auditing every changed .md file:
# files that exist on every owner machine but live outside git by design. A closed list, each named
# with where it lives, so an invented filename still reports.
EXEMPT_BASENAMES |= {
    "skills-lock.json",       # vendored-skill hash lock, .gitignore
    "settings.local.json",    # .claude/settings.local.json, per-machine harness settings, .gitignore
    "cmdc_agent.py",          # user-level ~/.claude/skills/cmdc-subagent runner (AGENTS.md charter rule)
    "allowed-models.json",    # the owner charter file next to cmdc_agent.py, written only by the manager
    "status.json",            # per-lane runtime state, .claude/cmdc-agents/agents/<lane>/ (gitignored, .gitignore:169)
    # Owner ruling 2026-09-25: the .commandcode settings file is local-only behind a narrow ignore
    # (.gitignore), while its taste files ARE tracked. It is real and deliberately untracked, so a
    # citation to it is correct and must not be reported - the same case as the entries above.
    "settings.json",
    # Machine-local Kilo runtime files, excluded through `.git/info/exclude` (NOT the committed
    # .gitignore, so a fresh clone does not even list them - which is why
    # docs/contributing/session-boundary.md:121 says the setup script "does not exist in a clone").
    # Both are read by shipped code, so the citations in the docs that name them are correct:
    #   - agent-manager.json: the legacy Kilo manager registry, read by
    #     gk-core/scripts/worktree_cleanup_core.py:215 and named at :283.
    #   - setup-script.ps1: the machine-local worktree setup step, described in
    #     docs/contributing/session-boundary.md section 5.
    "agent-manager.json",
    "setup-script.ps1",
}

# EXEMPT 2 - a citation on a line that is *about* the file being gone. These are the honest ones:
# a correction notice, a supersession marker, an incident record. Flagging them would punish exactly
# the fix this audit exists to encourage, and would have flagged every banner added on 2026-09-18.
DELIBERATE_DEAD = re.compile(
    r"(deleted|no longer exist|does not exist|neither exist|never existed|never created|"
    r"nonexistent|non-existent|was fused|\bgone\b|removed in|retired|superseded|"
    r"dead citation|stale|corrected|~~|struck|withdrawn|renamed to|replaced by|predecessor|"
    r"former|hypothetical|unbuilt)", re.I)

# EXEMPT 3 - prior-art prose quotes OTHER projects' data files by name (Ragnarok Online's
# `mob_db.yml`, Path of Exile's `Stats.dat`). Those are not claims about this repo and cannot be
# resolved against it. Two signals, because one is not enough: the whole `docs/research/` tree, and
# any section whose heading is about prior art wherever it appears - every ideal doc carries one,
# and `mob_db.yml` inside `creature-seed-ideal.md`'s prior-art section was this rule's first false
# positive (2026-09-18, caught on the audit's own first run).
EXTERNAL_SCOPE = ("docs/research/",)
PRIOR_ART_HEADING = re.compile(
    r"^#{1,6}\s.*\b(prior art|research|genre|references?|further reading|bibliograph)",
    re.I)

# EXEMPT 5 - an explicit, authored declaration that a run of citations describes code AS IT WAS,
# not as it is. Written as a marker line, and it holds until the next heading:
#
#     <!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover -->
#
# This exists because the alternative is worse. `story-scene-ideal.md` carried 25 citations into two
# files the 2026-09-16 cutover reduced or deleted; re-pointing each one means inventing 25 line
# numbers in a successor file, which manufactures exactly the false precision this audit exists to
# catch. A survey of what the code USED to be is legitimate history and worth keeping - it just must
# not read as a claim about today. The marker makes that distinction explicit and greppable, and it
# costs an author one deliberate line, so it cannot be applied by accident.
CITATIONS_HISTORICAL = re.compile(r"<!--\s*citations-historical\s*:", re.I)

# EXEMPT 6 - a forward-looking document proposing a file that does not exist yet. Specs, capability
# maps, plans and task lists name the files they will create ("`gk-core/scripts/run_guards.py` | new"), so a
# missing file there is usually a PROPOSAL, not rot. Found 2026-09-18 on the solid-enforcement
# program's own docs: 87 "dead" citations, every one a planned file, which would have made --strict
# unusable on the document type the design gate produces most.
#
# Two facts make the rule precise, and the second exists because the first alone was measured wrong:
#
#   1. A citation WITH a line number to a missing file is never a proposal. Nobody can cite line 40
#      of a file that does not exist yet.
#   2. A missing file that git history shows was DELETED is rot, not a proposal, line number or not.
#      The first draft of this exemption claimed rot was "overwhelmingly line-numbered". Measured,
#      58 of 262 line-less "proposals" named files that had existed and been deleted, 14 of them in
#      `spec-world-map-gaps.md` alone. The deleted-path check below catches all of those.
#
# So LOW ("proposed") needs all three: a forward-looking doc, no line cited, and a file that never
# existed in this repository's history.
FORWARD_LOOKING = re.compile(r"(^|/)(spec-[^/]+|[^/]+-map|[^/]+-plan|[^/]+-todo)\.md$")

# EXEMPT 7 - an explicit "(new)" marker on the line, in ANY document. Ideal docs propose files too
# (their Tunables section names the tuning file a feature will add), but exemption 6 deliberately does
# not cover ideals: an ideal describes the code as it is, and a never-existed file cited there as if
# real is exactly the defect this audit caught on its first run (`Combat/Guard/PoiseRuntime.cs` in
# creature-seed-ideal.md). So an ideal must SAY a file is proposed, with a "(new)" or "**new**" marker
# on the same line. It still counts only when git history shows the file never existed, so a marker
# cannot hide rot.
PROPOSED_MARKER = re.compile(r"\(new\)|\*\*new\*\*", re.I)

# EXEMPT 4 - a NEXT tuning version that has not been published yet. `gk-core/data/tuning/**` is versioned
# `v{n+1}` through `gk-core/tools/tuning/publish.py`, so a document proposing a re-tune necessarily names a
# file that does not exist. That is a proposal, not a dead citation. Recognised only when a sibling
# version of the same domain IS tracked, so a genuinely invented filename still reports.
VERSIONED_TUNING = re.compile(r"^(?P<stem>.*?)\.v(?P<n>\d+)\.json$")

# --- D5: a line-numbered citation into a JSON registry must still hold the entry it names --------
#
# A JSON registry is append-mostly, so every entry a program adds shifts every citation after it,
# and D2 cannot see the shift: the cited line is still inside the file, it just holds a DIFFERENT
# entry now. Measured 2026-09-23 (TVB-F34): 20 such citations existed repo-wide, and 20 of the 29
# entry citations in `docs/architecture/test-verification-boundary*` and
# `tasks/test-verification-boundary-*` were stale, by 673-1713 lines each.
#
# The rule resolves the entry the sentence names against the registry's own line map. It fires when
# the citation is a registry line citation, the citation's own sentence names at least one entry the
# registry knows (a boundary `id`, or a `projects` key), and the cited span does not hold the entry
# that sentence position names -- positionally when the line cites as many spans as it names entries,
# and only as "none of them is anywhere on the line" otherwise, so a mis-attributed note is never
# produced.
#
# LOW, not HIGH, and the distinction is this file's own (see the docstring above): D2 is HIGH because
# the cited line cannot be opened at all, while a stale D5 line opens and merely shows the wrong
# entry - the "a stale positive merely misleads" case. It is HIGH-eligible once the repository reads
# 0; until then a gate would turn a repo-wide green into a repo-wide red over citations in other
# programs' fences (TVB-F34's residual: 9 citations in 7 files, none of them this program's).
REGISTRY_BASENAMES = {"verification-boundaries.v1.json"}
# How far back a citation's own sentence may reach for the entries it names. Three lines covers the
# `**name** (`\n`file:line`)` wrapping these docs use; a token farther back is another sentence.
D5_LOOKBACK_LINES = 3
# A citation resolves when it lands inside the entry it names, not only on the entry's own `"id"`
# line: these sentences point at the boundary object (`:679` for the object whose `"id"` is on
# `:680`; `:3325` for that boundary's `paths` array), and the reader who lands there sees the entry.
# So each entry carries its OBJECT EXTENT, and a cited span resolves if it overlaps that extent.
D5_SHORTHAND = re.compile(r"`:(\d+)(?:\s*[-–]\s*(\d+))?`")
D5_REGISTRY_NAME = re.compile(r"verification-boundaries\.v1\.json:(\d+)(?:\s*[-–]\s*(\d+))?")
# name -> every (start, end) it occupies, for every loaded registry. A name is not unique across the
# file's two shapes: `web-fusion-rpg-web` is a `projects` key at one line and a boundary `id` at
# another, so a single line per name would report the second as rot.
_REGISTRY_ENTRY_EXTENTS = {}


def object_extent(lines, start):
    """The last line of the JSON object/array opening at `start` (1-based, inclusive)."""
    depth = 0
    for i in range(start, len(lines) + 1):
        depth += lines[i - 1].count("{") + lines[i - 1].count("[")
        depth -= lines[i - 1].count("}") + lines[i - 1].count("]")
        if i > start and depth <= 0:
            return i
    return len(lines)


def registry_entry_extents(path):
    """{entry-name: ((start, end), ...)} for a JSON registry's boundary `id`s and `projects` keys."""
    try:
        raw = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return {}
    lines = raw.split("\n")
    out = defaultdict(list)
    for n, line in enumerate(lines, start=1):
        m = re.match(r'^\s*"id"\s*:\s*"([^"]+)"', line)
        if m:
            # A boundary object opens on the line before its `"id"`.
            start = n - 1 if n > 1 and lines[n - 2].strip() == "{" else n
        else:
            m = re.match(r'^ {4}"([^"]+)"\s*:\s*[\[{]', line)
            if not m:
                m = re.match(r'^ {4}"([^"]+)"\s*:\s*"', line)
                if not m:
                    continue
            start = n
        out[m.group(1)].append((start, object_extent(lines, start)))
    return {k: tuple(sorted(set(v))) for k, v in out.items()}


def registry_entries_in_sentence(text_lines, lineno, col):
    """{entry-name: extents} for every registry entry the sentence NAMES, as a code token.

    Backticks (or the `projects["x"]` form) are required, and that is not decoration: `data`,
    `core` and `server` are all `projects` keys AND ordinary words these docs use constantly, so a
    bare-word scan reported a citation as naming `data` and blamed it for a shift it never cited.
    """
    first = max(0, lineno - 1 - D5_LOOKBACK_LINES)
    window = [t[:col] if i == lineno else t
              for i, t in enumerate(text_lines[first:lineno], start=first + 1)]
    found = {}
    for text in window:
        tokens = re.findall(r"`([A-Za-z0-9][A-Za-z0-9._-]*)`", text)
        tokens += re.findall(r'projects\["([^"]+)"\]', text)
        for token in tokens:
            if token in _REGISTRY_ENTRY_EXTENTS:
                found[token] = _REGISTRY_ENTRY_EXTENTS[token]
    return found


def registry_spans(line):
    """Ordered [(start, end, text)] for every line citation into a registry on this line."""
    out = [(int(m.group(1)), int(m.group(2) or m.group(1)), m.group(0))
           for m in D5_REGISTRY_NAME.finditer(line)]
    first = re.search(r"verification-boundaries\.v1\.json", line)
    if first:
        out += [(int(m.group(1)), int(m.group(2) or m.group(1)), m.group(0))
                for m in D5_SHORTHAND.finditer(line[first.end():])]
    return out


def audit_d5_line(doc, lineno, line, text_lines, deliberate):
    """D5 findings for one line: a registry entry the sentence names is not where the citation says.

    These sentences are written positionally -- "`a` (`:32-48`), `b` (`:1043`), `c` (`:549`)" -- so
    when the line cites as many spans as it names entries, span i is checked against entry i. That
    pairing is what keeps a shorthand span from being blamed on the wrong entry. When the counts
    differ the line is only reported if NO named entry's extent meets ANY of its spans, which is the
    conservative reading: one finding for the line, never a mis-attributed one per span.
    """
    if deliberate:
        return []
    spans = registry_spans(line)
    if not spans:
        return []
    named = registry_entries_in_sentence(text_lines, lineno, len(line))
    if not named:
        return []
    every = [e for extents in named.values() for e in extents]
    where = ", ".join("%s=%s" % (k, "/".join("%d-%d" % e for e in extents))
                      for k, extents in sorted(named.items()))

    def inside(start, end, extents):
        return any(s <= end and start <= e for s, e in extents)

    def finding(start, end, text):
        return dict(code="D5", sev="LOW", doc=doc, line=lineno, ref=text,
                    note="names %s; none is at %d-%d" % (where, start, end))

    if len(spans) == len(named):
        return [finding(s, e, t)
                for (s, e, t), extents in zip(spans, named.values()) if not inside(s, e, extents)]
    if any(inside(s, e, every) for s, e, _ in spans):
        return []
    s, e, t = spans[0]
    return [dict(code="D5", sev="LOW", doc=doc, line=lineno, ref=t,
                 note="names %s; none is at %s" % (where, "/".join("%d-%d" % (a, b)
                                                                   for a, b, _ in spans)))]

# --- D4: the ideal-vs-approved-map status-line check (spec-doc-citation-gate.md) ---------------
#
# Systemic finding of the 2026-09-18 gap survey: 21 ideal docs contradicted their own capability
# map. An ideal's status line says "no build authorized" long after the map it links says
# "approved" and the program shipped -- the exact stale negative this whole audit exists to catch,
# just at the document-pair level instead of the single-citation level.
#
# Scoped to `docs/architecture/<p>-ideal.md` / `docs/architecture/<p>-map.md` pairs only (the
# spec's own naming, not the `-program.md` alternate some capability maps use -- a pair that never
# shipped a `-map.md` has nothing for this check to compare against and is silently skipped, same
# as a citation to an exempt basename).
IDEAL_PATH_RE = re.compile(r"^docs/architecture/([^/]+)-ideal\.md$")
# "Status line" is read as the first 15 lines of each file, the same window on both sides of the
# pair -- where every real example of this convention (world-stage-map.md:3,
# world-stage-ideal.md:14) places its bolded "**Status:...**" declaration.
STATUS_WINDOW_LINES = 15
MAP_STATUS_SHIPPED_RE = re.compile(r"\bapproved\b|\bauthorized\b|\bin use\b|\bcomplete\b", re.I)
IDEAL_STATUS_UNBUILT_RE = re.compile(
    r"no build authorized|not a spec|nothing specced|nothing built|no spec, no plan", re.I)
D4_BANNER_RE = re.compile(r"status line vs\.? what shipped", re.I)

# A bare substring match on MAP_STATUS_SHIPPED_RE fires on "no build AUTHORIZED", "once this map
# is APPROVED", "pending owner APPROVAL", "written AFTER this map is approved", and (via the
# unbounded "complete") "cache triggers COMPLETED" -- five real, shipped-as-of-2026-09-19/20 status
# lines that either say the OPPOSITE of shipped, or use "complete" as a past-tense verb about one
# sub-task rather than the program's own build status. Measured against the real tree while
# building this check: of the original 20 raw hits, only 14 held up as a genuine positive,
# present-tense, program-level claim once these were excluded. Cheap and precise beats clever:
# (1) word-bound "complete" so it never matches "completed"/"completing"/"incomplete"; (2) reject a
# hit whose preceding ~40 chars carry a negation or future/conditional word, per this module's own
# "precision over coverage" rule.
_MAP_STATUS_HEDGE_RE = re.compile(
    r"(?:\bno\b|\bnot\b|\bnever\b|\bonce\b|\buntil\b|\bpending\b|\bafter\b|\bwhen\b|\bif\b)"
    r"[^.]{0,40}$", re.I)


def map_positively_claims_shipped(text):
    for m in MAP_STATUS_SHIPPED_RE.finditer(text):
        if not _MAP_STATUS_HEDGE_RE.search(text[:m.start()]):
            return True
    return False


def first_lines(path, n):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return "".join(fh.readline() for _ in range(n))
    except OSError:
        return ""


def audit_d4(tracked_set):
    """One finding per ideal/map pair where the map claims the program shipped, the ideal's own
    status line still denies it, and neither says which one to trust (the banner)."""
    findings = []
    for path in sorted(tracked_set):
        m = IDEAL_PATH_RE.match(path)
        if not m:
            continue
        map_path = "docs/architecture/%s-map.md" % m.group(1)
        if map_path not in tracked_set:
            continue
        if not map_positively_claims_shipped(first_lines(map_path, STATUS_WINDOW_LINES)):
            continue
        try:
            ideal_text = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if D4_BANNER_RE.search(ideal_text):
            continue
        if IDEAL_STATUS_UNBUILT_RE.search(first_lines(path, STATUS_WINDOW_LINES)):
            findings.append(dict(
                code="D4", sev="HIGH", doc=path, line=1, ref=map_path,
                note="%s reads approved/authorized/in use/complete, but this ideal's own status "
                     "line still denies a build, and it carries no "
                     "'Status line vs. what shipped' banner" % map_path))
    return findings


def _ls_files(cwd):
    """`git ls-files` in ONE repository: tracked plus untracked non-ignored, forward-slashed."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True, text=True, check=True, cwd=cwd, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return {p for p in out.replace("\\", "/").split("\n") if p}


def sibling_repositories():
    """Every sibling repository beside this one, from the shared resolver.

    A MISSING sibling returns nothing rather than raising: this is a document check, and a sibling's
    absence must not become the run's outcome. The accessors are wrapped individually because
    `content_root` REFUSES when the pack is absent, and one absent pack must not abort the audit.
    """
    try:
        from keepverse_roots import (authored_content_root, content_root, core_root,
                                     forge_root, fusion_root, web_root)
    except ImportError:
        return []
    here = os.path.realpath(os.getcwd())
    out = []
    for accessor in (core_root, forge_root, fusion_root, web_root, authored_content_root, content_root):
        try:
            base = accessor(here)
        except Exception:
            continue
        if not base:
            continue
        base = os.path.realpath(str(base))
        if os.path.isdir(base) and base != here:
            out.append(base)
    return out


def tracked_files():
    """Every resolvable path in the WORKSPACE, not only in the repository that tracks this file.

    Tracked files PLUS untracked, non-ignored ones. Untracked files are included on purpose:
    DESIGN-GATE's checklist says to run this audit on the doc you just wrote, which is before it is
    committed, and the first version listed tracked files only and reported "0 documents" for a
    brand-new doc (found 2026-09-18 on this program's own specs). Ignored files stay out, and they never
    resolve a citation, because nothing another reader has can open them.

    WHY THE SIBLINGS ARE HERE. This repository is the workspace root, and the eight other repositories
    are UNTRACKED here — each has its own remote, which is the point of the split. So `git ls-files` on
    its own could not see a single file in gk-core, gk-forge, gk-web or gk-fusion, and every citation
    into one was reported as "no tracked file with this name".

    MEASURED before this change, over the workspace: 52315 findings, of which 12722 named a path a
    sibling repository DOES carry and that exists on disk — every one a correct citation reported as
    broken. `gk-core/scripts/anchor-ledger.py` is one, and the file is there. A guard that cannot open
    the files it audits is not a finding about the documents.

    A sibling's paths are included UNDER ITS OWN NAME (`gk-core/scripts/...`), because that is how a
    document in this workspace cites across repositories, and a bare `scripts/...` from two repositories
    would be ambiguous. The pack (`content_root`) is a subdirectory of gk-data and is included under
    `gk-data/…` for the same reason.
    """
    paths = _ls_files(os.getcwd())
    for base in sibling_repositories():
        prefix = os.path.basename(base)
        for rel in _ls_files(base):
            paths.add(f"{prefix}/{rel}")
    return sorted(paths)

def deleted_paths():
    """Every path git history shows as deleted. Used by EXEMPT 6 to tell a proposal (never existed)
    from rot (existed, then deleted)."""
    out = subprocess.run(["git", "log", "--all", "--pretty=format:", "--name-only", "--diff-filter=D"],
                         capture_output=True, text=True, check=True).stdout
    return {p for p in out.replace("\\", "/").split("\n") if p}


def was_deleted(ref, deleted, deleted_basenames):
    """A ref with a directory must match a deleted path's suffix; a bare basename matches by name."""
    if "/" in ref:
        return any(d.endswith(ref) for d in deleted)
    return ref in deleted_basenames


def line_count(path):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return None


def strip_fences(text):
    """Blank out fenced code blocks - a filename inside an example command is not a citation."""
    out, inside = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return out


def audit(scope):
    tracked = tracked_files()
    by_name = defaultdict(list)
    for path in tracked:
        by_name[os.path.basename(path)].append(path)

    findings = []
    checked = 0
    deleted = deleted_paths()
    deleted_basenames = {os.path.basename(d) for d in deleted}
    docs = [p for p in tracked if p.startswith(scope) and p.endswith(".md")]
    # D5 reads each registry's own entry extents; load them once per run, not once per citation.
    _REGISTRY_ENTRY_EXTENTS.clear()
    for path in tracked:
        if os.path.basename(path) in REGISTRY_BASENAMES:
            _REGISTRY_ENTRY_EXTENTS.update(registry_entry_extents(path))

    for doc in docs:
        external = any(doc.startswith(s) for s in EXTERNAL_SCOPE)
        forward_looking = bool(FORWARD_LOOKING.search(doc))
        try:
            raw = io.open(doc, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        section_is_prior_art = False
        section_is_historical = False
        text_lines = strip_fences(raw)
        for lineno, line in enumerate(text_lines, start=1):
            if line.startswith("#"):
                section_is_prior_art = bool(PRIOR_ART_HEADING.match(line))
                section_is_historical = False
            elif CITATIONS_HISTORICAL.search(line):
                section_is_historical = True
            if section_is_historical:
                continue
            deliberate = bool(DELIBERATE_DEAD.search(line))
            # Both patterns, merged in source order. A dot-directory citation and a plain one are the
            # same kind of claim and must go through the identical D1/D2/D3 body below, so the two
            # finditer results are chained rather than the body duplicated for the second shape.
            for match in sorted(list(CITATION.finditer(line)) + list(DOTPATH_CITATION.finditer(line)),
                                key=lambda m: m.start()):
                ref, cited_line = match.group(1), match.group(2)
                base = os.path.basename(ref)
                if base in EXEMPT_BASENAMES:
                    continue
                candidates = by_name.get(base, [])

                if not candidates:
                    if deliberate:
                        continue
                    vm = VERSIONED_TUNING.match(base)
                    if vm and any(
                            VERSIONED_TUNING.match(k) and
                            VERSIONED_TUNING.match(k).group("stem") == vm.group("stem")
                            for k in by_name):
                        continue  # EXEMPT 4 - an unpublished next version is a proposal
                    never_existed = not was_deleted(ref, deleted, deleted_basenames)
                    proposed = never_existed and (
                        (forward_looking and not cited_line)                 # EXEMPT 6
                        or bool(PROPOSED_MARKER.search(line)))               # EXEMPT 7
                    findings.append(dict(
                        code="D1",
                        sev="LOW" if (external or section_is_prior_art or proposed) else "HIGH",
                        doc=doc, line=lineno,
                        ref=match.group(0),
                        note=("no such file yet - read as proposed (forward-looking doc, no line cited)"
                              if proposed else "no tracked file with this name")))
                    continue

                checked += 1
                if not cited_line:
                    continue

                exact = [c for c in candidates if c.endswith(ref)]
                if len(exact) != 1:
                    # D3 promoted (spec-doc-citation-gate.md, 2026-09-20): LOW only in
                    # docs/research/ and prior-art sections, where the ambiguous name usually
                    # belongs to another project's file this repo cannot resolve. Everywhere else
                    # an ambiguous line-numbered citation is exactly the "cannot be opened"
                    # failure D1/D2 already gate on -- ambiguity is not evidence either.
                    findings.append(dict(
                        code="D3",
                        sev="LOW" if (external or section_is_prior_art) else "HIGH",
                        doc=doc, line=lineno, ref=match.group(0),
                        note="%d files share this name - cite a path, not a bare basename, so the "
                             "line number can be checked" % len(candidates)))
                    continue

                total = line_count(exact[0])
                if total is None:
                    continue
                if int(cited_line) > total:
                    if deliberate:
                        continue
                    findings.append(dict(
                        code="D2",
                        sev="LOW" if (external or section_is_prior_art) else "HIGH",
                        doc=doc, line=lineno,
                        ref=match.group(0), note="%s is %d lines" % (exact[0], total)))

            # D5 is a per-LINE check, not a per-citation one: the shorthand form `` `:N` `` carries
            # no filename, so the citation loop above cannot see it at all.
            findings += audit_d5_line(doc, lineno, line, text_lines, deliberate)

    # D4 is a document-PAIR check, not a per-citation one -- scoped the same way as the citation
    # scan above (only ideal docs under `scope`), so `--scope docs/architecture/item` still limits
    # a batch to its own directory.
    tracked_set = set(tracked)
    findings += [f for f in audit_d4(tracked_set) if f["doc"].startswith(scope)]
    return findings, checked, len(docs)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--scope", default="docs/", help="path prefix to audit (default: docs/)")
    ap.add_argument("--summary", action="store_true", help="per-document counts only")
    ap.add_argument("--targets", metavar="CODE", help="bare file:line list for one code (D1-D5)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when HIGH findings exist")
    args = ap.parse_args()

    # `.` and `./` are how a caller asks for the whole repository, and until 2026-09-23 they silently
    # meant something else: `docs = [p for p in tracked if p.startswith(scope)]` reads `.` as the
    # dot-directory prefix, so `--scope .` audited 664 documents under `.agents/`, `.claude/`,
    # `.github/` and reported a plausible verdict for the rest of the tree, while `--scope ./`
    # audited **0** and exited 0. Both are the "a run that proves nothing while printing a verdict"
    # shape this repo already filed once (TVB-F27).
    scope = args.scope.replace("\\", "/").strip()
    if scope in (".", "./"):
        scope = ""
    findings, checked, doc_count = audit(scope)

    if doc_count == 0 and args.strict:
        print("Doc-citation audit - scope %r matched 0 documents: nothing was audited, so nothing "
              "is proven.\n" % args.scope)
        return 1

    if args.targets:
        for f in findings:
            if f["code"] == args.targets.upper():
                print("%s:%d" % (f["doc"], f["line"]))
        return 0

    by_code = defaultdict(list)
    for f in findings:
        by_code[f["code"]].append(f)
    high = [f for f in findings if f["sev"] == "HIGH"]

    print("Doc-citation audit - %d documents, %d resolvable citations checked\n" % (doc_count, checked))
    print("  D1 file does not exist      %5d   (%d HIGH)"
          % (len(by_code["D1"]), sum(1 for f in by_code["D1"] if f["sev"] == "HIGH")))
    print("  D2 line past end of file    %5d   (%d HIGH)"
          % (len(by_code["D2"]), sum(1 for f in by_code["D2"] if f["sev"] == "HIGH")))
    print("  D3 ambiguous basename       %5d   (%d HIGH)"
          % (len(by_code["D3"]), sum(1 for f in by_code["D3"] if f["sev"] == "HIGH")))
    print("  D4 ideal vs approved map    %5d   (%d HIGH)"
          % (len(by_code["D4"]), sum(1 for f in by_code["D4"] if f["sev"] == "HIGH")))
    print("  D5 registry entry moved     %5d   (%d HIGH)"
          % (len(by_code["D5"]), sum(1 for f in by_code["D5"] if f["sev"] == "HIGH")))

    per_doc = defaultdict(int)
    for f in high:
        per_doc[f["doc"]] += 1
    if per_doc:
        print("\nHIGH findings by document, worst first:")
        for doc, n in sorted(per_doc.items(), key=lambda kv: -kv[1])[:20]:
            print("  %5d  %s" % (n, doc))

    if not args.summary and high:
        print("\nHIGH detail:")
        for f in sorted(high, key=lambda f: (f["doc"], f["line"])):
            print("  %s:%d  %s  %s  - %s" % (f["doc"], f["line"], f["code"], f["ref"], f["note"]))

    print("\nA citation nobody can open is not evidence. Fix the citation, or say on that line that "
          "the file\nis gone - this audit exempts any citation whose own line says so.")
    return 1 if (args.strict and high) else 0


if __name__ == "__main__":
    sys.exit(main())
