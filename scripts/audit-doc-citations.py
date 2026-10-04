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

`--parity` is a SEPARATE mode with its own checks, because it compares two repositories rather
than auditing one document, and it is the opposite shape to D1-D5 - see WHY below before reading
its verdict:

    P1  a lock-file line that exists in the superseded tree and NOT in the authoritative tree
    P2  both trees' index lock files declare which tree is authoritative
    P3  all 14 lock files are tracked in BOTH trees

Gating (spec-doc-citation-gate.md, 2026-09-20): D3 is HIGH outside docs/research/ and prior-art
sections (an ambiguous line-numbered citation cannot be opened either, so it is no longer a lesser
finding than D1/D2 there); D4 is always HIGH where it fires. `--strict` fails on D1/D2 HIGH plus
D3 plus D4.

WHY `--parity` EXISTS, and why it is the opposite shape to the checks above. This repository - the
`gk-workflow` workspace root - and the pre-split monorepo (`letuhao/plant-vs-zombie-rise-of-
summoner`) BOTH track all 14 lock files - `decisions.md`, `DESIGN-GATE.md` and the twelve
`docs/architecture/decisions/<category>.md` - and they diverged silently.
`keepverse_roots.workspace_root()` answers "the directory holding docs/" with whichever tree the
calling script sits in, so every citation check ran against one of two documents that both claimed
to be the same one, and `guard-citation-stability` fingerprinted only the gk-workflow copy.
An ADR written to close a finding therefore lands in one tree and does not exist in the other.

WHY THIS TOOL LIVES HERE, and why it is the only copy. The tool that checks the documentation was
itself forked: two copies, 39,210 bytes here and 33,876 in the monorepo before the merge, each with
a feature the other lacked - the sibling-repository file index here, `--parity` there - and the copy
outside the authoritative tree ran only when somebody remembered it. The split-topology ADR names
gk-workflow as the source of truth for "shared guards, verification and migration harnesses,
orchestration tools, path rules, CI policy", and gk-core's enforcement registry already carries the
row `doc-citations -> scripts/audit-doc-citations.py`, which `run_guards.py` resolves to this
repository across the workspace roots by design (its own docstring measures 23 guards in gk-core, 4
in gk-fusion, and `session-boundary` and `doc-citations` here). So this file is the single copy, it
carries both feature sets, and it runs from `.github/workflows/lock-file-parity.yml`.

Because this copy IS the authoritative tree, `--parity` names the other side with `--legacy-root`
rather than assuming it is the tree the script sits in. Left as it was, running from here would
compare gk-workflow against itself and refuse - the fail-closed shape is preserved deliberately,
because a guard pointed at one tree is green by construction.

    Measured 2026-10-05: gk-workflow `decisions.md` is 229 lines, the monorepo's is 220. The
    `Status tracks - combat and out-of-combat (2026-10-02)` index row exists only in gk-workflow.
    Pointing `guard-citation-stability.py` at the monorepo copy produces 76 drift findings and
    10 orphaned baseline entries against 0 in place.

The authority is NOT a preference. The split-topology ADR - `gk-workflow` `docs/architecture/
decisions/world.md:27`, "Repository topology - Keepverse split", owner ruling 2026-09-30 - names
gk-workflow as the single source of truth for architecture decisions, principles, plans, task
records and development documentation, and the monorepo's own copy of that same row still carries
the pre-ruling text. So this guard is deliberately ONE-DIRECTIONAL: it fails when the superseded
tree holds lock content the authoritative tree lacks, and it says nothing when the superseded tree
is merely behind - being behind is the declared state, not a defect.

What is canonicalised before comparing, and why each erasure is safe:
  * post-split path prefixes (`gk-core/`, `gk-fusion/`, `gk-forge/`, `gk-web/`, `gk-content/`,
    `gk-assets/`, `gk-tests/`, `gk-data/packs/fusion/`) - the legacy tree spells these paths the
    pre-split way, and that spelling is the whole point of it being the superseded copy;
  * positional citation renumbering (`decisions.md:N`, `DESIGN-GATE.md:N`) - the authoritative
    `decisions.md` has grown, so a legacy row citing `decisions.md:103` is not asserting a rule the
    authoritative tree lacks, it is asserting the same rule at the legacy tree's line 103;
  * CR bytes - both repositories' `.gitattributes` says `* text=auto eol=lf` and both track these
    files as LF, so a CRLF working tree is a checkout artefact and treating it as drift would
    manufacture a finding that is not in the repository. Comparison reads the committed blob.

Everything else must match exactly. An erasure that were too broad would hide a real one-sided
rule, which is the defect class this guard exists for, so the canonicalisation is deliberately
limited to the two classes above and to whitespace.

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

    python scripts/audit-doc-citations.py --parity        # the two-tree lock-file check; exit 1 on drift
    python scripts/audit-doc-citations.py --parity --workspace-root <gk-workflow clone>
    python scripts/audit-doc-citations.py --parity --json

Run from this repository - the AUTHORITATIVE tree - both roots must be named, because neither is
implied any more:

    python scripts/audit-doc-citations.py --parity \
        --workspace-root . --legacy-root <pre-split monorepo clone>

`--legacy-root` falls back to `$KEEPVERSE_LEGACY_ROOT`, then to the tree this script sits in, which
is what a copy living in the superseded tree needs and why the mode was written that way first.

`--parity` never needs `--strict`: it is a gate by itself and exits 1 on any P1/P2/P3 finding, so a
green run cannot mean "it reported a drift and carried on".

Exit codes: 0 = report produced (default, even with findings), 1 = HIGH findings and --strict,
2 = usage error, 3 = --parity could not compare (either tree absent, the two roots resolving to the
same directory, or a lock file untracked in one of them), which is a refusal rather than a pass.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# `keepverse_roots` is gk-CORE's, this script is gk-workflow's, so the sibling resolution below needs
# that directory on the path. The same two-line insert every other tool in this workspace uses, copied
# from gk-fusion/scripts/guard-single-writer.py:53-54. Without it the import is guarded, returns nothing,
# and the change reads as a fix that did nothing - which is worse than not making it. `os.path` rather
# than `pathlib` for the path arithmetic, because this module uses `os` throughout for it; `pathlib`'s
# `Path` is imported separately above for `--parity`'s two-root resolution, which is a different job.
#
# `scripts/lib/` is tried FIRST and is this repository's own future copy; `../gk-core/scripts/lib` is
# gk-core's, which is where the module lives today. Both are relative to this file, never a literal.
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


def citation_prefix(base: str) -> str:
    """The prefix a document uses for a path under `base`, in this workspace's citation spelling.

    A REPOSITORY is named by itself: `gk-core`, `gk-forge`, `gk-fusion`, `gk-web`, `gk-content`. The content
    pack is NOT a repository — `content_root()` returns `<workspace>/gk-data/packs/fusion`, a subdirectory of
    gk-data — and every document spells its files `gk-data/packs/fusion/...`.

    Indexing the pack under `os.path.basename(base)` therefore made `fusion/data/...` the indexed spelling
    while the documents said `gk-data/packs/fusion/data/...`, so `c.endswith(ref)` was false for every pack
    file and D3 fired on citations that are unambiguous. Measured: 36 of 186 D3 findings printed "1 files share
    this name" — the finding's own note refuting it — and all 36 were pack citations.

    So the prefix is the path from the CONTAINING repository down to `base`, under that repository's name. The
    repository is found by walking up to the nearest directory holding `.git`, which keeps the `packs/` layout
    out of this function: a pack nested differently later still resolves.

    Falls back to the basename when no repository is found above, which is the pre-split behaviour for a
    single checkout.
    """
    directory = base
    for _ in range(6):
        if os.path.isdir(os.path.join(directory, ".git")):
            relative = os.path.relpath(base, directory).replace("\\", "/")
            name = os.path.basename(directory)
            return name if relative == "." else f"{name}/{relative}"
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return os.path.basename(base)


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
        # NOT os.path.basename(base): the content pack is a SUBDIRECTORY of gk-data, so its
        # basename is `fusion` while every document spells it `gk-data/packs/fusion`. See
        # citation_prefix for the measurement that made this a defect rather than a preference.
        prefix = citation_prefix(base)
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


# --- P1/P2/P3: the two-tree lock-file parity check ---------------------------------------------
#
# The 14 lock files. `decisions.md` and `DESIGN-GATE.md` are the two INDEXES; the other twelve are
# the per-category files each index row links to. Declared rather than globbed, for the reason
# guard-citation-stability declares its own two: ADDING a file to this set has to be an explicit,
# reviewable edit, because a glob would silently widen what the gate protects - and a thirteenth
# category file that nobody compares is exactly the silent fork this mode exists to prevent.
LOCK_FILES = (
    "docs/architecture/decisions.md",
    "docs/DESIGN-GATE.md",
    "docs/architecture/decisions/combat.md",
    "docs/architecture/decisions/content-gen.md",
    "docs/architecture/decisions/game-host.md",
    "docs/architecture/decisions/launcher.md",
    "docs/architecture/decisions/persistence.md",
    "docs/architecture/decisions/power-caps.md",
    "docs/architecture/decisions/presentation.md",
    "docs/architecture/decisions/progression.md",
    "docs/architecture/decisions/repo-tooling.md",
    "docs/architecture/decisions/stats.md",
    "docs/architecture/decisions/transport.md",
    "docs/architecture/decisions/world.md",
)

# The two indexes must both carry this block. It is a fenced block rather than prose because the
# block's CONTENT DELIBERATELY DIFFERS between the trees - the authoritative one says "this copy is
# authoritative", the superseded one says "this copy is a superseded snapshot", and comparing those
# two sentences for equality would be comparing two answers to different questions. So the block is
# marked out of band: P2 requires it in both trees, and P1 does not compare its contents.
AUTHORITY_BEGIN = "<!-- lock-file-authority:begin -->"
AUTHORITY_END = "<!-- lock-file-authority:end -->"
AUTHORITY_CLAIM = "lock-file-authority: gk-workflow"

# The authority itself, and the reason. Named here so the marker line and the refusal text agree,
# and so a reader who has never seen this file can check the claim in one hop.
AUTHORITY_WHY = (
    "gk-workflow is the single source of truth for architecture decisions, principles, plans, task "
    "records and development documentation (owner ruling 2026-09-30, recorded in "
    "gk-workflow docs/architecture/decisions/world.md:27, 'Repository topology - Keepverse split'). "
    "This copy is a SUPERSEDED SNAPSHOT: it is behind on purpose and that is not a defect. Two trees "
    "holding a lock file is the defect, and the one direction that matters is a rule that exists "
    "here and not there - an ADR written to close a finding landing in one tree and silently not "
    "existing in the other."
)

# Post-split path prefixes. The legacy tree spells these paths the pre-split way; that spelling is
# the entire reason it is the superseded copy, so erasing it is erasing the declared difference and
# not a real one. `gk-data/packs/fusion/` is listed whole because stripping only `gk-data/` would
# leave `packs/fusion/data/seed/...`, which matches nothing.
REPO_PREFIXES = (
    "gk-data/packs/fusion/",
    "gk-data/packs/keepverse/",
    "gk-core/",
    "gk-fusion/",
    "gk-forge/",
    "gk-web/",
    "gk-content/",
    "gk-assets/",
    "gk-tests/",
)
_PREFIX_RE = re.compile(r"(?:%s)" % "|".join(re.escape(p) for p in REPO_PREFIXES))
# A positional citation's LINE NUMBER is renumbered by any legitimate growth of the index, so the
# number is not identity. The basename is.
_POS_CITE_RE = re.compile(r"(decisions\.md|DESIGN-GATE\.md):\d+")


def parity_canon(line: str) -> str:
    """A lock line's identity for cross-tree comparison.

    Erases exactly three things: CR bytes, the post-split path prefixes, and the line number in a
    positional citation. Whitespace is collapsed because a re-wrap is not a rule change. Anything
    else that differs is a DIFFERENCE, deliberately not erased - an over-broad erasure would hide
    the one-sided rule this is here to catch.
    """
    line = line.replace("\r", "").replace("\r\n", "\n")
    line = " ".join(line.split())
    prev = None
    while prev != line:                      # `gk-data/packs/fusion/gk-core/...` is not a real path,
        prev = line                          # but looping costs nothing and never guesses an order
        line = _PREFIX_RE.sub("", line)
    return _POS_CITE_RE.sub(r"\1:LINE", line)


def git_blob_lines(root: Path, rel: str) -> tuple[list[str] | None, str]:
    """The COMMITTED lines of `rel`, plus how they were obtained."""
    try:
        raw = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-p", f"HEAD:{rel}"],
            capture_output=True, timeout=60, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        return None, f"not committed ({exc.__class__.__name__})"
    return raw.decode("utf-8", errors="replace").splitlines(), "blob"


def lock_lines(root: Path, rel: str, committed: bool = False) -> tuple[list[str] | None, str]:
    """The lines of `rel` in `root`, and where they were read from.

    The WORKING TREE is the default, and that is a correction of the first version of this guard.
    Reading only the committed blob was defensible - both repositories' `.gitattributes` says
    `* text=auto eol=lf`, so a CRLF checkout is an artefact - and it did keep the EOL phantom out.
    But it also meant the guard could not see an uncommitted edit, which is the exact moment this
    guard has value: an ADR written to the wrong tree should be caught while the author is still
    holding it, not after it is history. The first mutation control proved that the blob-only guard
    stayed GREEN through a planted one-sided rule, a deleted authority block and an unterminated
    fence - three reds it could not raise, because none of them were committed.

    `--committed` restores the blob reading for a CI step that must judge a push rather than a desk.
    EOL cannot make either reading phantom, because `parity_canon` strips CR before comparing.
    """
    if not committed:
        path = root / rel
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace").splitlines(), "worktree"
    return git_blob_lines(root, rel)


def find_workspace_root(explicit: str | None) -> Path | None:
    """The gk-workflow clone, or a NAMED absence. A missing second tree is a refusal, not a pass."""
    for cand in (explicit, os.environ.get("KEEPVERSE_WORKSPACE_ROOT")):
        if cand:
            p = Path(cand)
            return p if p.is_dir() else None
    here = Path(__file__).resolve().parent
    for d in (here, *here.parents):
        if (d / "gk-core").is_dir() and (d / "gk-data").is_dir() and (d / "docs").is_dir():
            return d
        # A legacy clone nested inside the workspace resolves to itself, which is the documented
        # nearest-match-wins rule rather than a special case for this tool.
        if (d / "docs").is_dir() and (d / "scripts").is_dir() and (d / "src").is_dir():
            return None
    return None


def find_legacy_root(explicit: str | None) -> Path | None:
    """The SUPERSEDED pre-split tree, or a NAMED absence.

    Written AFTER the tool moved to gk-workflow, so the direction the mode was first written in no
    longer holds: this file now sits in the tree the mode treats as AUTHORITATIVE, and the superseded
    side has to be named or taken from the environment. Defaulting to "the tree this script sits in"
    is kept as the LAST fallback because it is what a copy living in the superseded tree needs, and
    because with no second root named the two sides resolve to one directory - which main() refuses
    rather than comparing. A guard cannot name both trees and be asked to compare them.

    The absence is NAMED rather than substituted: returning the authoritative tree here would make
    `--parity` compare gk-workflow against itself, which is green by construction and is the exact
    shape of defect this mode exists to catch.
    """
    for cand in (explicit, os.environ.get("KEEPVERSE_LEGACY_ROOT")):
        if cand:
            p = Path(cand)
            return p if p.is_dir() else None
    here = Path(__file__).resolve().parent.parent
    return here if here.is_dir() else None


def split_authority_block(lines: list[str]) -> tuple[list[tuple[int, str]], list[str]]:
    """Separate an authority block from the lock content around it.

    Returns (content lines as (1-based line number, text), authority-block lines). Line numbers are
    preserved so a P1 finding still names the line a reader would have to open.

    An unterminated block is a finding rather than a shrug: a fence with no end would silently exempt
    every line after it, which is the one shape that could turn this guard into a no-op.
    """
    content: list[tuple[int, str]] = []
    block: list[str] = []
    inside = False
    unterminated = False
    for i, ln in enumerate(lines, 1):
        if AUTHORITY_BEGIN in ln:
            inside = True
            block.append(ln)
            continue
        if AUTHORITY_END in ln:
            inside = False
            block.append(ln)
            continue
        if inside:
            block.append(ln)
        else:
            content.append((i, ln))
    if inside:
        unterminated = True
    return content, block, unterminated


def audit_parity(legacy: Path, workspace: Path, committed: bool = False
                 ) -> tuple[list[str], list[str], dict]:
    """One-sided lock content, authority declared on both sides, and a full inventory."""
    findings: list[str] = []
    notes: list[str] = []
    stats = {"files": len(LOCK_FILES), "compared": 0, "legacy_lines": 0, "workspace_lines": 0,
             "read": "blob" if committed else "worktree"}

    for rel in LOCK_FILES:
        mine, mine_how = lock_lines(legacy, rel, committed)
        theirs, theirs_how = lock_lines(workspace, rel, committed)
        if mine is None or theirs is None:
            where = []
            if mine is None:
                where.append(f"this tree has no committed copy ({mine_how})")
            if theirs is None:
                where.append(f"gk-workflow has no committed copy ({theirs_how})")
            findings.append(
                f"P3  {rel}: tracked in one tree only - " + "; ".join(where)
            )
            continue

        stats["compared"] += 1

        mine_content, _, mine_open = split_authority_block(mine)
        theirs_content, _, theirs_open = split_authority_block(theirs)
        for label, flag in (("this tree", mine_open), ("gk-workflow", theirs_open)):
            if flag:
                findings.append(
                    f"P3  {rel} ({label}): {AUTHORITY_BEGIN} has no {AUTHORITY_END}. An unterminated "
                    f"block would exempt every line after it from comparison, which is the one shape "
                    f"that turns this guard into a no-op."
                )
        stats["legacy_lines"] += len(mine_content)
        stats["workspace_lines"] += len(theirs_content)

        # P1 - one-sided CONTENT, in the ONE direction that matters.
        #
        # A legacy line is accounted for when some gk-workflow line EQUALS it, or CONTAINS it. The
        # containment case is gk-workflow having since revised or extended that very row, which is
        # what "superseded" means and is the declared state of this tree - so it is reported as a
        # NOTE, not a failure. Absence is the failure: a legacy line no gk-workflow line accounts
        # for is a rule written to the wrong tree, and it is the case that has actually happened.
        #
        # The multiset matters even though the match is by containment: without it a legacy tree
        # passes by duplicating text it invented, and a guard that can be satisfied by copying is
        # not a guard. It is deliberately NOT enforced against containment matches - gk-workflow
        # merges rows rather than leaving near-duplicates, so demanding a distinct authoritative
        # line per legacy line would fail on a legitimate merge.
        pool: dict[str, int] = defaultdict(int)
        for _, ln in theirs_content:
            pool[parity_canon(ln)] += 1
        revised = 0
        for i, ln in mine_content:
            key = parity_canon(ln)
            if pool.get(key, 0) > 0:
                pool[key] -= 1
                continue
            if key and any(key in other for other in pool if other):
                revised += 1
                continue
            findings.append(
                f"P1  {rel}:{i} exists in this superseded tree and not in gk-workflow "
                f"(compared as blob/blob)\n      {ln[:180]}"
            )
        if revised:
            notes.append(
                f"N1  {rel}: {revised} row(s) in the superseded tree have been REVISED or extended "
                f"in gk-workflow. Reported every run because that copy is behind by design and a "
                f"reader who acts on the stale row is wrong; not a failure, because 'behind' is the "
                f"declared state."
            )

        if mine_how != theirs_how:
            findings.append(
                f"P3  {rel}: this tree was read as {mine_how} and gk-workflow as {theirs_how} - one "
                f"side has no copy on disk, so the comparison does not prove the two trees track the "
                f"same content"
            )

    for rel in ("docs/architecture/decisions.md", "docs/DESIGN-GATE.md"):
        for label, root in (("this tree", legacy), ("gk-workflow", workspace)):
            got, _ = lock_lines(root, rel, committed)
            if got is None:
                continue          # already reported as P3; do not report the marker as missing too
            _, block, _ = split_authority_block(got)
            if not block:
                findings.append(
                    f"P2  {rel} ({label}) carries no authority block. Expected {AUTHORITY_BEGIN} .. "
                    f"{AUTHORITY_END} naming {AUTHORITY_CLAIM!r}, because without it neither tree "
                    f"says which copy is authoritative and the next reader has to re-derive it."
                )
            elif not any(AUTHORITY_CLAIM in ln for ln in block):
                findings.append(
                    f"P2  {rel} ({label}) has an authority block that does not name "
                    f"{AUTHORITY_CLAIM!r} - a block that fails to say which tree wins is worse than "
                    f"no block, because it looks like it said."
                )
    return findings, notes, stats


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--scope", default="docs/", help="path prefix to audit (default: docs/)")
    ap.add_argument("--summary", action="store_true", help="per-document counts only")
    ap.add_argument("--targets", metavar="CODE", help="bare file:line list for one code (D1-D5)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when HIGH findings exist")
    ap.add_argument("--parity", action="store_true",
                    help="compare the 14 lock files against the gk-workflow tree; exit 1 on drift")
    ap.add_argument("--workspace-root", metavar="PATH",
                    help="the authoritative gk-workflow tree (default: $KEEPVERSE_WORKSPACE_ROOT, "
                         "then discovered by walking up for gk-core/ and gk-data/)")
    ap.add_argument("--legacy-root", metavar="PATH",
                    help="the SUPERSEDED pre-split tree to compare against (default: "
                         "$KEEPVERSE_LEGACY_ROOT, then the tree this script sits in)")
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    ap.add_argument("--committed", action="store_true",
                    help="compare the committed blobs instead of the working trees, for a CI step "
                         "that must judge a push rather than a desk")
    args = ap.parse_args()

    if args.parity:
        workspace = find_workspace_root(args.workspace_root)
        if workspace is None:
            print("REFUSING: --parity needs the authoritative gk-workflow tree and it could "
                  "not be found.\n  Pass --workspace-root <gk-workflow clone>, or set "
                  "KEEPVERSE_WORKSPACE_ROOT.\n  One tree alone cannot prove two trees agree, so this "
                  "is a refusal (exit 3), never a green run.", file=sys.stderr)
            return 3
        legacy = find_legacy_root(args.legacy_root)
        if legacy is None:
            print("REFUSING: --parity needs the SUPERSEDED pre-split tree and it could not be "
                  "found.\n  Pass --legacy-root <pre-split monorepo clone>, or set "
                  "KEEPVERSE_LEGACY_ROOT.\n  Running from gk-workflow, that tree is a SEPARATE clone "
                  "and is\n  not discovered by walking, so it has to be named. Refusing rather than "
                  "comparing\n  the authoritative tree against itself.", file=sys.stderr)
            return 3
        if workspace.resolve() == legacy.resolve():
            print("REFUSING: the two roots resolved to the same directory (%s). A guard pointed at "
                  "one tree reports that tree against itself and is green by construction, which is "
                  "the exact shape of the defect it exists to catch." % legacy,
                  file=sys.stderr)
            return 3

        findings, notes, stats = audit_parity(legacy, workspace, args.committed)
        result = {
            "mode": "parity",
            "legacy_root": str(legacy),
            "workspace_root": str(workspace),
            "authoritative": "gk-workflow",
            "read": stats["read"],
            "files": stats["files"],
            "compared": stats["compared"],
            "findings": findings,
            "notes": notes,
            "verdict": "PARITY OK" if not findings else "REFUSING: the lock files have forked",
        }
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
            return 1 if findings else 0

        print("Doc-citation parity - %d lock files, %d compared (read: %s)\n"
              % (stats["files"], stats["compared"], stats["read"]))
        print("  authoritative tree : %s" % workspace)
        print("  superseded tree    : %s" % legacy)
        print("  authority          : gk-workflow (owner ruling 2026-09-30, "
              "decisions/world.md:27)")
        print("  compared content   : %d lines here vs %d lines in gk-workflow\n"
              % (stats["legacy_lines"], stats["workspace_lines"]))
        for note in notes:
            print("  %s\n" % note)
        if not findings:
            print("PARITY OK - every lock line in this superseded tree is accounted for in "
                  "gk-workflow, every\nlock file is tracked in both, and both declare the "
                  "authority. Being BEHIND is the\ndeclared state; a rule that exists only here is "
                  "not.")
            return 0
        print("REFUSING: the lock files have forked. %d finding(s):\n" % len(findings))
        for f in findings:
            print("  %s" % f)
        print("\n  A finding here means one of the two trees holds lock content the other does "
              "not.\n  If the authoritative tree is missing it, fix that tree. If this superseded "
              "tree\n  holds a rule gk-workflow lacks, that rule was written to the wrong tree "
              "and the\n  ADR does not exist where every reader of the lock file will look.")
        return 1

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
