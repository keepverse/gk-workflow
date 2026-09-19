"""Compile-time dependency graph from MSBuild project files, checked against the direction contract.

Only `ProjectReference` edges are compile-time edges. A project that references a project in a
repo its own repo may not depend on (layout.compileDeps) is residue. So is an unresolvable edge.
Unity/Il2Cpp/Harmony references outside the allowed repos are residue.
"""

from __future__ import annotations

import posixpath
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from kvsplit.classify import Classification
from kvsplit.residue import Residue
from kvsplit.rules import DROP

PROJECT_EXT = (".csproj", ".fsproj", ".vbproj")
UNITY_REF = re.compile(r"\b(UnityEngine|Il2Cpp\w*|HarmonyLib|0Harmony|BepInEx|MelonLoader)\b")


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    src_repo: str
    dst_repo: str


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def resolve_rel(base_file: str, value: str) -> str | None:
    v = value.strip().replace("\\", "/")
    if v.startswith("$(MSBuildThisFileDirectory)"):
        v = v[len("$(MSBuildThisFileDirectory)"):]
    if "$(" in v or v.startswith("/") or re.match(r"^[A-Za-z]:", v):
        return None
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(base_file), v))
    if joined.startswith("../") or joined == "..":
        return None
    return joined


def build(blobs: dict[str, bytes], cls: Classification) -> tuple[list[Edge], list[Residue]]:
    edges: list[Edge] = []
    residue: list[Residue] = []
    for path in sorted(blobs):
        if not path.endswith(PROJECT_EXT):
            continue
        place = cls.place(path)
        if place is None or place.repo == DROP:
            continue
        try:
            root = ET.fromstring(blobs[path])
        except ET.ParseError as ex:
            residue.append(Residue("project-parse-error", path, "", None, str(ex), "source"))
            continue
        for el in root.iter():
            name = _local(el.tag)
            if name == "ProjectReference":
                inc = el.get("Include")
                if inc is None:
                    continue
                target = resolve_rel(path, inc)
                tplace = cls.place(target) if target else None
                if tplace is None or tplace.repo == DROP:
                    residue.append(Residue("unresolved-project-reference", path, inc, None,
                                           "ProjectReference does not resolve to a migrated project", "source"))
                    continue
                edges.append(Edge(path, target, place.repo, tplace.repo))
                if tplace.repo != place.repo and tplace.repo not in cls.layout.compile_deps[place.repo]:
                    residue.append(Residue("direction-violation", path, inc, None,
                                           f"{place.repo} may not compile against {tplace.repo} (layout.compileDeps)",
                                           "source"))
            elif name in ("Reference", "PackageReference"):
                inc = el.get("Include") or ""
                if UNITY_REF.search(inc) and place.repo not in cls.layout.unity_repos:
                    residue.append(Residue("unity-outside-host", path, inc, None,
                                           f"{place.repo} references a game-host assembly", "source"))
    return edges, residue
