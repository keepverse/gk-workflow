"""Cross-boundary text references no transform owns -> residue with file:line.

Two sources of findings:
  * configured tokens (scan.v1.json `tokens`): fixed regexes such as repo-root discovery through
    the legacy solution file, each with its own allowed fix;
  * path literals rooted at a configured top-level directory (`pathRoots`), in files a transform
    does not already rewrite: a literal whose target changes location relative to the file that
    mentions it is residue `path-literal-moves` (allowed fix: source).
"""

from __future__ import annotations

import bisect
import posixpath
import re

from kvsplit.classify import Classification
from kvsplit.globmatch import compile_glob
from kvsplit.residue import Residue
from kvsplit.rules import DROP, ScanConfig


def _ext(path: str) -> str:
    base = posixpath.basename(path)
    return base[base.rfind("."):].lower() if "." in base else base


def _path_regex(roots: tuple[str, ...]) -> re.Pattern[str]:
    alt = "|".join(re.escape(r) for r in roots)
    # optional leading ../ (or ..\) chain, a root, then a path body; '\' accepted as separator
    return re.compile(r"(?<![\w.\-/\\])((?:\.\.[\\/])*(?:" + alt + r")[\\/][\w.\-\\/]*[\w\-])")


def scan(blobs: dict[str, bytes], cls: Classification, cfg: ScanConfig, transformed: set[str],
         comment_owned: set[str] | None = None) -> list[Residue]:
    from kvsplit.transforms import comment_lines, file_ext
    comment_owned = comment_owned or set()
    out: list[Residue] = []
    skip = [compile_glob(g) for g in cfg.skip]
    cites = [compile_glob(g) for g in cfg.citation_globs]
    tokens = [(t, re.compile(t.regex)) for t in cfg.tokens]
    prx = _path_regex(cfg.path_roots) if cfg.path_roots else None
    for path in sorted(blobs):
        place = cls.place(path)
        if place is None or place.repo == DROP:
            continue
        if _ext(path) not in cfg.extensions or any(s.match(path) for s in skip):
            continue
        data = blobs[path]
        if b"\0" in data:
            continue
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        line_starts = [0]
        for i, ch in enumerate(text):
            if ch == "\n":
                line_starts.append(i + 1)

        def line_of(pos: int) -> int:
            return bisect.bisect_right(line_starts, pos)

        for t, rx in tokens:
            for m in rx.finditer(text):
                out.append(Residue(t.kind, path, m.group(0), line_of(m.start()), t.detail, t.allowed_fix))
        if prx is None or path in transformed:
            continue
        citation_file = any(c.match(path) for c in cites)
        owns_comments = path in comment_owned
        content_hits: list[int] = []
        ext = file_ext(path)
        doc_lines = comment_lines(text, ext) if owns_comments else set()
        for m in prx.finditer(text):
            if owns_comments and line_of(m.start()) in doc_lines:
                continue
            lit = m.group(1)
            norm = lit.replace("\\", "/")
            if norm.startswith("../"):
                old_target = posixpath.normpath(posixpath.join(posixpath.dirname(path), norm))
                if old_target.startswith(".."):
                    continue
            else:
                old_target = norm
            mapped = cls.map_any(old_target)
            if mapped is None:
                if cls.place(old_target) is None and not _is_known_prefix(cls, old_target):
                    continue  # prose or a path that never existed: not a reference we can judge
                out.append(Residue("path-literal-unmappable", path, lit, line_of(m.start()),
                                   f"'{old_target}' splits across repos or is dropped", "source"))
                continue
            repo, new_target = mapped
            prefix = cfg.pack_roots.get(repo)
            if prefix is not None and not norm.startswith("../") and new_target == prefix + old_target:
                # pack-relative content path: the literal survives; what changes is the root it is
                # resolved from. Citations are fine as they are; code gets one item per file.
                if not citation_file:
                    content_hits.append(line_of(m.start()))
                continue
            same_place = repo == place.repo and new_target == old_target and place.path == path
            if citation_file and not norm.startswith("../") and cls.workspace_path(repo, new_target) == old_target:
                continue  # a workspace-relative citation that still resolves
            if not same_place:
                ws = cls.workspace_path(repo, new_target)
                out.append(Residue("path-literal-moves", path, lit, line_of(m.start()),
                                   f"'{old_target}' -> {repo}:{new_target} (workspace '{ws}'); "
                                   f"file moves {place.repo}:{place.path}", "source"))
        if content_hits:
            out.append(Residue("content-root-consumer", path, "content-root", content_hits[0],
                               f"{len(content_hits)} repo-relative content path(s); resolve them from the content "
                               f"pack root (GkDataRoot + packs/<pack>/) instead of the repo root", "source"))
    return out


def _is_known_prefix(cls: Classification, p: str) -> bool:
    base = p.rstrip("/") + "/"
    keys = cls._sorted
    i = bisect.bisect_left(keys, base)
    return i < len(keys) and keys[i].startswith(base)
