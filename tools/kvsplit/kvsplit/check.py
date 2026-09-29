"""Static verification of the staged workspace. Findings are residue, like everything else.

  * every ProjectReference in a staged project resolves to a staged project (repo-root
    properties evaluated to their sibling-folder defaults);
  * no public repo contains generated content (seedsmith provenance) or a content-data tree;
  * no repo outside layout.unityRepos imports a game-host namespace;
  * no file is staged into a sealed repo, whatever route put it there.
"""

from __future__ import annotations

import posixpath
import re
from typing import TYPE_CHECKING

from kvsplit.classify import Classification
from kvsplit.graph import PROJECT_EXT
from kvsplit.residue import Residue
from kvsplit.rules import Rules

if TYPE_CHECKING:
    from kvsplit.stage import StagedFile

_PROJREF = re.compile(r'<ProjectReference\b[^>]*\bInclude="([^"]+)"')
_PROP = re.compile(r"\$\((\w+)\)")
_PROVENANCE = re.compile(rb'"_meta"\s*:\s*\{[^{}]*"(?:model|promptVersion)"')
_CONTENT_TREE = re.compile(r"(?:^|/)data/(?:seed|generated)/")
_HOST_USING = re.compile(r"^\s*using\s+(?:UnityEngine|Il2Cpp\w*|HarmonyLib|BepInEx|MelonLoader)\b", re.M)


def run_checks(files: list["StagedFile"], cls: Classification, rules: Rules) -> list[Residue]:
    out: list[Residue] = []
    layout = rules.layout
    staged = {cls.workspace_path(f.repo, f.path) for f in files}
    props = {r.property: ("" if r.dir in (".", "") else r.dir + "/") for r in layout.repos if r.property}
    # The one route a sealed repo has: a rule that declared itself a thin entrypoint to
    # workflow-owned policy. Resolved from the same ownership the parser enforced, so `check`
    # cannot be stricter than the rules and cannot be talked round by a rule's target alone.
    entrypoint_rules = {r.id for r in rules.ownership if r.entrypoint}
    declared_entrypoints = {(repo, pl.path) for old, pl in cls.placements.items()
                            if pl.rule in entrypoint_rules for repo in (pl.repo, *pl.copies)}
    for f in files:
        ws = cls.workspace_path(f.repo, f.path)
        repo = layout.repo(f.repo)
        # The seal is refused at rules-load time, so a staged tree cannot contain one of these
        # through the rules. It is asserted here anyway, and it is asserted on every route:
        # a primary placement, a `copies` row and a `template` row all end up in `files`, and
        # gk-assets held 228 art files behind two non-primary rows, so a check that only
        # looked at placements would have read that repository as untouched.
        if f.repo in layout.sealed and (f.repo, f.path) not in declared_entrypoints:
            out.append(Residue("sealed-repo-received-file", ws, f.path, None,
                               f"{f.repo} is sealed ({layout.seal_reason(f.repo)}) and received a "
                               f"{f.origin} file anyway", "rule"))
        if f.path.endswith(PROJECT_EXT):
            text = f.data.decode("utf-8-sig", errors="replace")
            for m in _PROJREF.finditer(text):
                inc = m.group(1)
                unknown = [p for p in _PROP.findall(inc) if p not in props and p != "MSBuildThisFileDirectory"]
                if unknown:
                    out.append(Residue("staged-reference-broken", ws, inc, None,
                                       f"unknown property {unknown}", "rule"))
                    continue
                v = inc.replace("\\", "/")
                if v.startswith("$(MSBuildThisFileDirectory)"):
                    v = v[len("$(MSBuildThisFileDirectory)"):]
                m2 = _PROP.match(v)
                if m2:
                    target = posixpath.normpath(props[m2.group(1)] + v[m2.end():].lstrip("/"))
                else:
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(ws), v))
                if target not in staged:
                    out.append(Residue("staged-reference-broken", ws, inc, None,
                                       f"resolves to '{target}', which is not in the staged workspace", "transform"))
        if repo.visibility == "public":
            if _CONTENT_TREE.search(f.path):
                out.append(Residue("content-in-public-repo", ws, f.path, None,
                                   f"content-data tree in public repo {f.repo}", "rule"))
            elif f.path.endswith(".json") and _PROVENANCE.search(f.data):
                out.append(Residue("content-in-public-repo", ws, "_meta", None,
                                   f"generator provenance (_meta.model/promptVersion) in public repo {f.repo}", "rule"))
        if f.repo not in layout.unity_repos and f.path.endswith(".cs"):
            m = _HOST_USING.search(f.data.decode("utf-8-sig", errors="replace"))
            if m:
                out.append(Residue("unity-outside-host", ws, m.group(0).strip(), None,
                                   f"{f.repo} imports a game-host namespace", "source"))
    return out
