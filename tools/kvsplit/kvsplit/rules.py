"""Authored rule files. Strict parsing: a missing or mistyped field throws, never defaults.

rules/
  layout.v1.json      repositories of the workspace and the direction contract; a repo may
                      declare a `seal`, which states that the split may place nothing in it
  ownership.v1.json   path -> target repo (+ optional relocation), one reason per rule
  transforms.v1.json  which registered transform runs on which paths
  scan.v1.json        cross-boundary text reference scan configuration
  templates/<repo>/** files emitted verbatim into a staged repo (origin "template")
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kvsplit.globmatch import compile_glob

DROP = "drop"


class RulesError(ValueError):
    pass


def _sentence(text: str) -> str:
    """A reason is written as sentences; a refusal that appends one must not double the stop."""
    return text if text.endswith((".", "!", "?")) else text + "."


def _req(obj: dict[str, Any], key: str, typ: type | tuple[type, ...], where: str) -> Any:
    if not isinstance(obj, dict):
        raise RulesError(f"{where}: expected an object")
    if key not in obj:
        raise RulesError(f"{where}: missing required field '{key}'")
    val = obj[key]
    if typ is int and isinstance(val, bool):
        raise RulesError(f"{where}.{key}: expected int, got bool")
    if not isinstance(val, typ):
        raise RulesError(f"{where}.{key}: expected {typ}, got {type(val).__name__}")
    return val


def _opt(obj: dict[str, Any], key: str, typ: type | tuple[type, ...], where: str) -> Any:
    if key not in obj:
        return None
    return _req(obj, key, typ, where)


def _no_extra(obj: dict[str, Any], allowed: set[str], where: str) -> None:
    extra = set(obj) - allowed
    if extra:
        raise RulesError(f"{where}: unknown field(s) {sorted(extra)}")


def _schema(doc: Any, where: str) -> None:
    if _req(doc, "schemaVersion", int, where) != 1:
        raise RulesError(f"{where}: unsupported schemaVersion")


@dataclass(frozen=True)
class Repo:
    id: str
    dir: str            # workspace-relative directory; "." for the root repo
    visibility: str     # public | private
    property: str | None  # MSBuild property naming this repo's root, e.g. GkCoreRoot
    preserve: tuple[str, ...]  # globs in the target repo that `apply` never deletes
    seal: str | None = None   # non-None: the split may place nothing here, and `reason` says why


@dataclass(frozen=True)
class Layout:
    repos: tuple[Repo, ...]
    compile_deps: dict[str, frozenset[str]]  # repo -> repos it may ProjectReference
    unity_repos: frozenset[str]               # the only repos allowed to reference Unity/Il2Cpp/Harmony
    test_projects: tuple[str, ...] = ()       # globs exempt from compileDeps (they verify, they do not ship)
    sealed: frozenset[str] = frozenset()      # repos the split may not place a file into

    def repo(self, repo_id: str) -> Repo:
        for r in self.repos:
            if r.id == repo_id:
                return r
        raise KeyError(repo_id)

    def ids(self) -> list[str]:
        return [r.id for r in self.repos]

    def seal_reason(self, repo_id: str) -> str | None:
        return self.repo(repo_id).seal


@dataclass(frozen=True)
class Relocate:
    src: str
    dst: str


@dataclass(frozen=True)
class OwnershipRule:
    id: str
    pattern: str
    target: str
    priority: int
    reason: str
    relocate: Relocate | None
    copies: tuple[str, ...]  # additional repos that receive an identical copy
    entrypoint: bool = False  # may target a sealed repo: a thin entrypoint to workflow-owned policy


@dataclass(frozen=True)
class TransformRule:
    id: str
    kind: str
    pattern: str
    params: dict[str, Any]


@dataclass(frozen=True)
class ScanToken:
    kind: str
    regex: str
    allowed_fix: str
    detail: str


@dataclass(frozen=True)
class Accept:
    path: str
    kind: str
    anchor: str | None
    reason: str


@dataclass(frozen=True)
class ScanConfig:
    extensions: frozenset[str]
    path_roots: tuple[str, ...]
    skip: tuple[str, ...]
    citation_globs: tuple[str, ...]  # files whose path literals are citations (workspace-relative)
    pack_roots: dict[str, str]       # repo -> prefix under which legacy repo-relative content paths survive
    resolvers: dict[str, str]        # repo -> regex; a file matching it resolves that repo's root itself
    output_relative_globs: tuple[str, ...]  # runtime code resolving content against a build output laid out by <Link>
    tokens: tuple[ScanToken, ...]
    accept: tuple[Accept, ...] = ()


@dataclass
class Rules:
    layout: Layout
    ownership: tuple[OwnershipRule, ...]
    transforms: tuple[TransformRule, ...]
    scan: ScanConfig
    templates: dict[str, dict[str, bytes]] = field(default_factory=dict)  # repo -> path -> bytes
    digest: str = ""


ALLOWED_FIX = {"rule", "transform", "source"}


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RulesError(f"missing rules file {path}") from None
    except json.JSONDecodeError as ex:
        raise RulesError(f"{path}: invalid JSON: {ex}") from None


def parse_layout(doc: Any) -> Layout:
    w = "layout"
    _schema(doc, w)
    _no_extra(doc, {"schemaVersion", "repos", "compileDeps", "unityRepos", "testProjectGlobs"}, w)
    repos: list[Repo] = []
    for i, r in enumerate(_req(doc, "repos", list, w)):
        wi = f"{w}.repos[{i}]"
        _no_extra(r, {"id", "dir", "visibility", "property", "preserve", "seal"}, wi)
        vis = _req(r, "visibility", str, wi)
        if vis not in ("public", "private"):
            raise RulesError(f"{wi}.visibility: must be public or private")
        prop = _opt(r, "property", str, wi)
        preserve = tuple(_req(r, "preserve", list, wi))
        for g in preserve:
            compile_glob(g)
        seal = None
        sl = _opt(r, "seal", dict, wi)
        if sl is not None:
            _no_extra(sl, {"reason"}, f"{wi}.seal")
            seal = _req(sl, "reason", str, f"{wi}.seal")
            if not seal.strip():
                raise RulesError(f"{wi}.seal.reason: must not be empty")
        repos.append(Repo(_req(r, "id", str, wi), _req(r, "dir", str, wi), vis, prop, preserve, seal))
    ids = [r.id for r in repos]
    if len(set(ids)) != len(ids) or DROP in ids:
        raise RulesError(f"{w}.repos: duplicate id or reserved id '{DROP}'")
    deps_raw = _req(doc, "compileDeps", dict, w)
    deps: dict[str, frozenset[str]] = {}
    for k, v in deps_raw.items():
        if k not in ids or not isinstance(v, list) or any(x not in ids for x in v):
            raise RulesError(f"{w}.compileDeps.{k}: unknown repo id")
        deps[k] = frozenset(v)
    for rid in ids:
        deps.setdefault(rid, frozenset())
    unity = _req(doc, "unityRepos", list, w)
    if any(x not in ids for x in unity):
        raise RulesError(f"{w}.unityRepos: unknown repo id")
    # A test project may drive a generator in a repo it may not compile against: it
    # verifies that generator's output, it does not ship against it. The edge is still
    # recorded in the graph, so the dependency stays visible - it is only the shipped
    # direction that compileDeps governs.
    test_globs = tuple(_opt(doc, "testProjectGlobs", list, w) or ())
    for g in test_globs:
        compile_glob(g)
    return Layout(tuple(repos), deps, frozenset(unity), test_globs,
                  frozenset(r.id for r in repos if r.seal is not None))


def parse_ownership(doc: Any, layout: Layout) -> tuple[OwnershipRule, ...]:
    w = "ownership"
    _schema(doc, w)
    _no_extra(doc, {"schemaVersion", "rules"}, w)
    targets = set(layout.ids()) | {DROP}
    out: list[OwnershipRule] = []
    seen: set[str] = set()
    for i, r in enumerate(_req(doc, "rules", list, w)):
        wi = f"{w}.rules[{i}]"
        _no_extra(r, {"id", "pattern", "target", "priority", "reason", "relocate", "copies", "entrypoint"}, wi)
        rid = _req(r, "id", str, wi)
        if rid in seen:
            raise RulesError(f"{wi}: duplicate rule id '{rid}'")
        seen.add(rid)
        pattern = _req(r, "pattern", str, wi)
        try:
            compile_glob(pattern)
        except ValueError as ex:
            raise RulesError(f"{wi}.pattern: {ex}") from None
        target = _req(r, "target", str, wi)
        if target not in targets:
            raise RulesError(f"{wi}.target: unknown target '{target}'")
        reason = _req(r, "reason", str, wi)
        if not reason.strip():
            raise RulesError(f"{wi}.reason: must not be empty")
        # A sealed repo is one the split may not write into at all. The only exception the
        # workspace has is a CI file a platform requires inside a sub-repository, which stays
        # a thin entrypoint to workflow-owned policy - so it must be asked for by name and
        # carry its own reason, and it is the one route into a sealed repo.
        entrypoint = bool(_opt(r, "entrypoint", bool, wi) or False)
        if target in layout.sealed:
            if not entrypoint:
                raise RulesError(f"{wi}: rule {rid} targets sealed repo '{target}' - "
                                 f"{_sentence(layout.seal_reason(target))} A rule that places a file "
                                 f"there must set 'entrypoint': true and say why.")
        elif entrypoint:
            raise RulesError(f"{wi}: rule {rid} claims the thin-entrypoint exception but its target '{target}' is "
                             f"not sealed. The exception exists only for a sealed repository, so claiming it "
                             f"elsewhere is an unreviewed hole in the seal.")
        reloc = None
        rel = _opt(r, "relocate", dict, wi)
        if rel is not None:
            _no_extra(rel, {"from", "to"}, f"{wi}.relocate")
            reloc = Relocate(_req(rel, "from", str, f"{wi}.relocate"), _req(rel, "to", str, f"{wi}.relocate"))
            if target == DROP:
                raise RulesError(f"{wi}: a dropped path cannot be relocated")
        copies = tuple(_opt(r, "copies", list, wi) or ())
        if any(c not in layout.ids() or c == target for c in copies):
            raise RulesError(f"{wi}.copies: unknown repo or same as target")
        sealed_copies = [c for c in copies if c in layout.sealed]
        if sealed_copies:
            raise RulesError(f"{wi}.copies: {','.join(sorted(sealed_copies))} is sealed. A copy is the same bytes "
                             f"in a second repository - the competing copy a seal exists to prevent - so it can "
                             f"never be a thin entrypoint.")
        out.append(OwnershipRule(rid, pattern, target, _req(r, "priority", int, wi), reason, reloc, copies, entrypoint))
    return tuple(out)


def parse_transforms(doc: Any, known_kinds: set[str]) -> tuple[TransformRule, ...]:
    w = "transforms"
    _schema(doc, w)
    _no_extra(doc, {"schemaVersion", "transforms"}, w)
    out: list[TransformRule] = []
    for i, t in enumerate(_req(doc, "transforms", list, w)):
        wi = f"{w}.transforms[{i}]"
        _no_extra(t, {"id", "kind", "pattern", "params"}, wi)
        kind = _req(t, "kind", str, wi)
        if kind not in known_kinds:
            raise RulesError(f"{wi}.kind: unknown transform kind '{kind}'")
        pattern = _req(t, "pattern", str, wi)
        compile_glob(pattern)
        out.append(TransformRule(_req(t, "id", str, wi), kind, pattern, _req(t, "params", dict, wi)))
    return tuple(out)


def parse_scan(doc: Any) -> ScanConfig:
    w = "scan"
    _schema(doc, w)
    _no_extra(doc, {"schemaVersion", "extensions", "pathRoots", "skip", "citationGlobs", "packRoots", "resolvers", "outputRelativeGlobs", "tokens", "accept"}, w)
    toks: list[ScanToken] = []
    for i, t in enumerate(_req(doc, "tokens", list, w)):
        wi = f"{w}.tokens[{i}]"
        _no_extra(t, {"kind", "regex", "allowedFix", "detail"}, wi)
        fix = _req(t, "allowedFix", str, wi)
        if fix not in ALLOWED_FIX:
            raise RulesError(f"{wi}.allowedFix: must be one of {sorted(ALLOWED_FIX)}")
        toks.append(ScanToken(_req(t, "kind", str, wi), _req(t, "regex", str, wi), fix, _req(t, "detail", str, wi)))
    skip = tuple(_req(doc, "skip", list, w))
    cites = tuple(_req(doc, "citationGlobs", list, w))
    for g in (*skip, *cites):
        compile_glob(g)
    return ScanConfig(
        frozenset(_req(doc, "extensions", list, w)),
        tuple(_req(doc, "pathRoots", list, w)),
        skip,
        cites,
        _pack_roots(_req(doc, "packRoots", dict, w), w),
        _resolvers(_req(doc, "resolvers", dict, w), w),
        tuple(_req(doc, "outputRelativeGlobs", list, w)),
        tuple(toks),
        _accept(_req(doc, "accept", list, w), w),
    )


def _accept(raw: list, where: str) -> tuple[Accept, ...]:
    out = []
    for i, a in enumerate(raw):
        wi = f"{where}.accept[{i}]"
        _no_extra(a, {"path", "kind", "anchor", "reason"}, wi)
        reason = _req(a, "reason", str, wi)
        if not reason.strip():
            raise RulesError(f"{wi}.reason: must not be empty")
        compile_glob(_req(a, "path", str, wi))
        out.append(Accept(a["path"], _req(a, "kind", str, wi), _opt(a, "anchor", str, wi), reason))
    return tuple(out)


def _pack_roots(raw: dict, where: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in raw.items():
        if not isinstance(v, str) or not v.endswith("/"):
            raise RulesError(f"{where}.packRoots.{k}: must be a string ending in '/'")
        out[k] = v
    return out


def _resolvers(raw: dict, where: str) -> dict[str, str]:
    import re as _re
    out: dict[str, str] = {}
    for k, v in raw.items():
        if not isinstance(v, str):
            raise RulesError(f"{where}.resolvers.{k}: must be a regex string")
        try:
            _re.compile(v)
        except _re.error as ex:
            raise RulesError(f"{where}.resolvers.{k}: {ex}") from None
        out[k] = v
    return out


def load_rules(rules_dir: Path, known_transform_kinds: set[str]) -> Rules:
    rules_dir = Path(rules_dir)
    files = ["layout.v1.json", "ownership.v1.json", "transforms.v1.json", "scan.v1.json"]
    h = hashlib.sha256()
    docs = {}
    for f in files:
        p = rules_dir / f
        raw = p.read_bytes() if p.exists() else b""
        h.update(f.encode() + b"\0" + raw + b"\0")
        docs[f] = _load_json(p)
    layout = parse_layout(docs["layout.v1.json"])
    templates: dict[str, dict[str, bytes]] = {}
    tdir = rules_dir / "templates"
    if tdir.exists():
        for p in sorted(tdir.rglob("*")):
            if p.is_file():
                rel = p.relative_to(tdir).as_posix()
                repo, _, sub = rel.partition("/")
                if repo not in layout.ids():
                    raise RulesError(f"templates/{rel}: unknown repo '{repo}'")
                if repo in layout.sealed:
                    raise RulesError(f"templates/{rel}: repo '{repo}' is sealed - "
                                     f"{_sentence(layout.seal_reason(repo))} kvsplit emits templates verbatim, "
                                     f"so a template here is the split writing into a repository it may not "
                                     f"write into, and it is never a thin entrypoint.")
                data = p.read_bytes()
                templates.setdefault(repo, {})[sub] = data
                h.update(b"T" + rel.encode() + b"\0" + data + b"\0")
    return Rules(
        layout=layout,
        ownership=parse_ownership(docs["ownership.v1.json"], layout),
        transforms=parse_transforms(docs["transforms.v1.json"], known_transform_kinds),
        scan=parse_scan(docs["scan.v1.json"]),
        templates=templates,
        digest=h.hexdigest(),
    )
