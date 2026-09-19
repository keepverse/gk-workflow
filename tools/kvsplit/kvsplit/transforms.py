"""Registered, pure transforms: (context, path, bytes) -> bytes, plus residue.

A transform either rewrites exactly what it understands or reports residue. It never passes a
half-rewritten file through: on any residue for a value, that value is left byte-identical and
the residue says so.

Kinds:
  msbuild-paths          rewrite relative paths in MSBuild Include/Exclude/Project/Update
                         attributes to their post-split location (same repo: relative path;
                         other repo: $(<RepoProperty>)<path>)
  msbuild-props-inject   insert a PropertyGroup defining every repo-root property, right after
                         the <Project ...> opening tag
  markdown-citations     rewrite relative markdown links and repo-relative path citations to
                         their post-split, workspace-relative location
"""

from __future__ import annotations

import bisect
import posixpath
import re
from dataclasses import dataclass
from typing import Callable

from kvsplit.classify import Classification
from kvsplit.graph import resolve_rel
from kvsplit.residue import Residue
from kvsplit.rules import TransformRule


@dataclass
class Ctx:
    cls: Classification
    old_path: str
    repo: str
    new_path: str
    rule: TransformRule


TransformFn = Callable[[Ctx, bytes], tuple[bytes, list[Residue]]]
REGISTRY: dict[str, TransformFn] = {}
# What a transform takes responsibility for: "file" (scan skips the whole file) or
# "comments" (scan skips path literals on comment lines only).
OWNS: dict[str, str] = {}


def register(kind: str, owns: str = "file") -> Callable[[TransformFn], TransformFn]:
    def deco(fn: TransformFn) -> TransformFn:
        REGISTRY[kind] = fn
        OWNS[kind] = owns
        return fn
    return deco


_C_LIKE = {".cs", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".java", ".css"}
_HASH = {".py", ".ps1", ".psm1", ".yml", ".yaml", ".toml", ".sh"}


def is_comment_line(line: str, ext: str) -> bool:
    """Whole-line comments only: deterministic and never inside a string literal."""
    s = line.lstrip()
    if ext in _C_LIKE:
        return s.startswith(("//", "/*", "*"))
    if ext in _HASH:
        return s.startswith("#")
    return False


def comment_lines(text: str, ext: str) -> set[int]:
    """1-based line numbers that are wholly comment or documentation, never executable strings.

    Python: # lines plus every bare string-expression statement (docstrings), found with st.
    C-like: //, /*, * lines and the interior of /* ... */ blocks.
    PowerShell: # lines and <# ... #> blocks. Other hash languages: # lines.
    """
    lines = text.splitlines()
    out: set[int] = set()
    if ext == ".py":
        import ast
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("#"):
                out.add(i)
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            return out
        for node in ast.walk(tree):
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str) and node.end_lineno is not None):
                out.update(range(node.lineno, node.end_lineno + 1))
        return out
    if ext in _C_LIKE:
        in_block = False
        for i, line in enumerate(lines, 1):
            s = line.lstrip()
            if in_block:
                out.add(i)
                if "*/" in s:
                    in_block = False
                continue
            if s.startswith(("//", "*")):
                out.add(i)
            elif s.startswith("/*"):
                out.add(i)
                in_block = "*/" not in s[2:]
        return out
    if ext in (".ps1", ".psm1"):
        in_block = False
        for i, line in enumerate(lines, 1):
            s = line.lstrip()
            if in_block:
                out.add(i)
                if "#>" in s:
                    in_block = False
                continue
            if s.startswith("<#"):
                out.add(i)
                in_block = "#>" not in s[2:]
            elif s.startswith("#"):
                out.add(i)
        return out
    if ext in _HASH:
        return {i for i, line in enumerate(lines, 1) if line.lstrip().startswith("#")}
    return out


def file_ext(path: str) -> str:
    base = posixpath.basename(path)
    return base[base.rfind("."):].lower() if "." in base else ""


def _decode(ctx: Ctx, data: bytes) -> tuple[str | None, str, list[Residue]]:
    bom = ""
    if data.startswith(b"\xef\xbb\xbf"):
        bom, data = "﻿", data[3:]
    try:
        return data.decode("utf-8"), bom, []
    except UnicodeDecodeError:
        return None, bom, [Residue("transform-decode", ctx.old_path, ctx.rule.id, None,
                                   "file is not UTF-8; transform skipped", "transform")]


def _wild_split(v: str) -> tuple[str, str]:
    """Split a path into (base without wildcards, remainder starting at the first wildcard segment)."""
    parts = v.split("/")
    for i, seg in enumerate(parts):
        if "*" in seg or "?" in seg:
            return "/".join(parts[:i]), "/".join(parts[i:])
    return v, ""


def _has_tracked(cls: Classification, path: str) -> bool:
    if cls.place(path) is not None:
        return True
    base = path.rstrip("/") + "/"
    i = bisect.bisect_left(cls._sorted, base)
    return i < len(cls._sorted) and cls._sorted[i].startswith(base)


def relocate_value(ctx: Ctx, value: str) -> tuple[str, Residue | None]:
    """New spelling of one MSBuild path value, or (value, residue)."""
    raw = value.strip()
    if not raw or ("/" not in raw and "\\" not in raw and not raw.startswith("..")):
        return value, None  # bare file name next to the project: moves with it
    if "$(" in raw and not raw.startswith("$(MSBuildThisFileDirectory)"):
        return value, None  # already property-rooted: not ours to reinterpret
    backslash = "\\" in raw
    target = resolve_rel(ctx.old_path, raw)
    if target is None:
        return value, Residue("msbuild-unresolved", ctx.old_path, raw, None,
                              "path escapes the repo or is absolute", "source")
    base, rest = _wild_split(target)
    mapped = ctx.cls.map_any(base) if base else None
    if mapped is None and base and not _has_tracked(ctx.cls, base):
        # an untracked path (bin/, obj/, a build output) moves with its nearest tracked ancestor
        anc, tail = base, ""
        while anc and mapped is None:
            anc, _, seg = anc.rpartition("/")
            tail = seg if not tail else f"{seg}/{tail}"
            mapped = ctx.cls.map_any(anc) if anc else None
        if mapped is not None:
            mapped = (mapped[0], f"{mapped[1]}/{tail}" if mapped[1] else tail)
    if mapped is None:
        return value, Residue("msbuild-unresolved", ctx.old_path, raw, None,
                              f"'{base}' does not map to one repo location after the split", "rule")
    repo, newbase = mapped
    if repo == ctx.repo:
        rel = posixpath.relpath(newbase or ".", posixpath.dirname(ctx.new_path) or ".")
        new = rel if not rest else (rest if rel == "." else f"{rel}/{rest}")
        if raw.startswith("$(MSBuildThisFileDirectory)"):
            new = "$(MSBuildThisFileDirectory)" + new
    else:
        prop = ctx.cls.layout.repo(repo).property
        if not prop:
            return value, Residue("msbuild-unresolved", ctx.old_path, raw, None,
                                  f"target repo {repo} has no MSBuild property in layout", "rule")
        tail = newbase if not rest else (f"{newbase}/{rest}" if newbase else rest)
        new = f"$({prop}){tail}"
    if backslash:
        new = new.replace("/", "\\")
    # keep the original's leading/trailing whitespace
    lead = value[: len(value) - len(value.lstrip())]
    trail = value[len(value.rstrip()):]
    return lead + new + trail, None


_ATTR = re.compile(r'\b(Include|Exclude|Project|Update|Remove)="([^"]*)"')


@register("msbuild-paths")
def msbuild_paths(ctx: Ctx, data: bytes) -> tuple[bytes, list[Residue]]:
    text, bom, res = _decode(ctx, data)
    if text is None:
        return data, res
    out_res: list[Residue] = []

    def repl(m: re.Match[str]) -> str:
        items = m.group(2).split(";")
        new_items = []
        for it in items:
            new, r = relocate_value(ctx, it)
            if r is not None:
                line = text.count("\n", 0, m.start()) + 1
                out_res.append(Residue(r.kind, r.path, r.anchor, line, r.detail, r.allowed_fix))
            new_items.append(new)
        return f'{m.group(1)}="{";".join(new_items)}"'

    new_text = _ATTR.sub(repl, text)
    return (bom + new_text).encode("utf-8"), out_res


@register("msbuild-props-inject")
def msbuild_props_inject(ctx: Ctx, data: bytes) -> tuple[bytes, list[Residue]]:
    text, bom, res = _decode(ctx, data)
    if text is None:
        return data, res
    m = re.search(r"<Project\b[^>]*>", text)
    if m is None:
        return data, [Residue("transform-shape", ctx.old_path, ctx.rule.id, None,
                              "no <Project> element to inject into", "transform")]
    nl = "\r\n" if "\r\n" in text else "\n"
    here = ctx.cls.layout.repo(ctx.repo).dir
    up = "" if here in (".", "") else "../" * (here.count("/") + 1)
    lines = [f"  <!-- kvsplit: workspace repo roots. Default = sibling folder in the Keepverse workspace. -->",
             "  <PropertyGroup>"]
    for r in ctx.cls.layout.repos:
        if not r.property:
            continue
        rel = "" if r.dir in (".", "") else r.dir + "/"
        val = ("$(MSBuildThisFileDirectory)" + up + rel).replace("/", "\\")
        lines.append(f"    <{r.property} Condition=\"'$({r.property})' == ''\">{val}</{r.property}>")
    lines.append("  </PropertyGroup>")
    block = nl + nl.join(lines)
    new_text = text[: m.end()] + block + text[m.end():]
    return (bom + new_text).encode("utf-8"), []


_SLN_PROJECT = re.compile(r'^([ \t]*)<Project\s+Path="([^"]+)"\s*/>[ \t]*\r?\n', re.M)
_SLN_EMPTY_FOLDER = re.compile(r'^[ \t]*<Folder\b[^>]*>\s*</Folder>[ \t]*\r?\n', re.M)


@register("solution-split")
def solution_split(ctx: Ctx, data: bytes) -> tuple[bytes, list[Residue]]:
    """Keep only the projects that land in this repo (paths rewritten); drop emptied folders.

    Used with an ownership `copies` rule so every .NET repo receives its own solution.
    """
    text, bom, res = _decode(ctx, data)
    if text is None:
        return data, res
    out_res: list[Residue] = []
    sln_dir = posixpath.dirname(ctx.old_path)

    def repl(m: re.Match[str]) -> str:
        old = posixpath.normpath(posixpath.join(sln_dir, m.group(2).replace("\\", "/")))
        mapped = ctx.cls.map_file(old)
        if mapped is None:
            out_res.append(Residue("solution-unresolved", ctx.old_path, m.group(2), None,
                                   "solution project is not a migrated file", "rule"))
            return ""
        repo, new = mapped
        if repo != ctx.repo:
            return ""
        rel = posixpath.relpath(new, posixpath.dirname(ctx.new_path) or ".")
        return m.group(0).replace(f'"{m.group(2)}"', f'"{rel}"')

    text2 = _SLN_PROJECT.sub(repl, text)
    prev = None
    while prev != text2:
        prev, text2 = text2, _SLN_EMPTY_FOLDER.sub("", text2)
    return (bom + text2).encode("utf-8"), out_res


@register("comment-citations", owns="comments")
def comment_citations(ctx: Ctx, data: bytes) -> tuple[bytes, list[Residue]]:
    """Rewrite repo-relative path citations on whole-line comments to workspace-relative paths."""
    text, bom, res = _decode(ctx, data)
    if text is None:
        return data, res
    ext = file_ext(ctx.old_path)
    rx = _cite_regex(tuple(ctx.rule.params.get("citationRoots", [])))
    cls = ctx.cls

    def cite(m: re.Match[str]) -> str:
        mapped = cls.map_any(m.group(1))
        if mapped is None:
            return m.group(0)
        return cls.workspace_path(*mapped) + m.group(2)

    doc = comment_lines(text, ext)
    out = []
    for i, line in enumerate(text.splitlines(keepends=True), 1):
        out.append(rx.sub(cite, line) if i in doc else line)
    return (bom + "".join(out)).encode("utf-8"), []


@register("text-citations")
def text_citations(ctx: Ctx, data: bytes) -> tuple[bytes, list[Residue]]:
    """Rewrite every repo-relative path citation in a citation-only text file (research JSON, notes)."""
    text, bom, res = _decode(ctx, data)
    if text is None:
        return data, res
    rx = _cite_regex(tuple(ctx.rule.params.get("citationRoots", [])))
    cls = ctx.cls

    def cite(m: re.Match[str]) -> str:
        mapped = cls.map_any(m.group(1))
        if mapped is None:
            return m.group(0)
        return cls.workspace_path(*mapped) + m.group(2)

    return (bom + rx.sub(cite, text)).encode("utf-8"), []


_MD_LINK = re.compile(r"(\]\()([^)\s#]+)((?:#[^)\s]*)?\))")


def _cite_regex(roots: tuple[str, ...]) -> re.Pattern[str]:
    alt = "|".join(re.escape(r) for r in roots)
    return re.compile(r"(?<![\w./\-])((?:" + alt + r")/[\w.\-/]*[\w\-])((?::\d+(?:-\d+)?)?)")


@register("markdown-citations")
def markdown_citations(ctx: Ctx, data: bytes) -> tuple[bytes, list[Residue]]:
    text, bom, res = _decode(ctx, data)
    if text is None:
        return data, res
    roots = tuple(ctx.rule.params.get("citationRoots", []))
    cls = ctx.cls
    my_ws = cls.workspace_path(ctx.repo, ctx.new_path)
    my_dir = posixpath.dirname(my_ws) or "."

    def link(m: re.Match[str]) -> str:
        target = m.group(2)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("/"):
            return m.group(0)
        old = posixpath.normpath(posixpath.join(posixpath.dirname(ctx.old_path), target))
        if old.startswith(".."):
            return m.group(0)
        mapped = cls.map_any(old)
        if mapped is None:
            return m.group(0)
        ws = cls.workspace_path(*mapped)
        rel = posixpath.relpath(ws, my_dir)
        if target.endswith("/") and not rel.endswith("/"):
            rel += "/"
        return m.group(1) + rel + m.group(3)

    text2 = _MD_LINK.sub(link, text)
    if roots:
        rx = _cite_regex(roots)

        def cite(m: re.Match[str]) -> str:
            mapped = cls.map_any(m.group(1))
            if mapped is None:
                return m.group(0)
            return cls.workspace_path(*mapped) + m.group(2)

        text2 = rx.sub(cite, text2)
    return (bom + text2).encode("utf-8"), []
