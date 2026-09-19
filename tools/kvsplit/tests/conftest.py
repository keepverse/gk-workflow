"""Fixture legacy repos and rules, built in pytest's tmp_path (cleaned by pytest; no swallowed deletes)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
}


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=GIT_ENV)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


def make_repo(root: Path, files: dict[str, str | bytes]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "core.autocrlf", "false")
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    return root


CORE_CSPROJ = '<Project Sdk="Microsoft.NET.Sdk">\n</Project>\n'
SERVER_CSPROJ = (
    '<Project Sdk="Microsoft.NET.Sdk.Web">\n'
    '  <ItemGroup>\n'
    '    <ProjectReference Include="..\\App.Core\\App.Core.csproj" />\n'
    '    <Content Include="..\\..\\data\\seed\\items\\**\\*.json" />\n'
    '    <Content Include="..\\..\\data\\tuning\\**\\*.json" />\n'
    '  </ItemGroup>\n'
    '</Project>\n'
)
GEN_CSPROJ = (
    '<Project Sdk="Microsoft.NET.Sdk">\n'
    '  <ItemGroup>\n'
    '    <ProjectReference Include="..\\..\\src\\App.Core\\App.Core.csproj" />\n'
    '  </ItemGroup>\n'
    '</Project>\n'
)
HOST_CSPROJ = (
    '<Project Sdk="Microsoft.NET.Sdk">\n'
    '  <ItemGroup>\n'
    '    <ProjectReference Include="..\\App.Core\\App.Core.csproj" />\n'
    '    <Reference Include="UnityEngine.CoreModule" />\n'
    '  </ItemGroup>\n'
    '</Project>\n'
)

LEGACY_FILES: dict[str, str | bytes] = {
    "App.slnx": "<Solution />\n",
    "Directory.Build.props": "<Project>\n  <PropertyGroup><LangVersion>latest</LangVersion></PropertyGroup>\n</Project>\n",
    "README.md": "See [core](src/App.Core/Thing.cs) and `src/App.Core/Thing.cs:3`.\n",
    "docs/guide.md": "Read [thing](../src/App.Core/Thing.cs#L3); tuning `data/tuning/a.v1.json`.\n",
    "docs/injector/host.md": "Host notes.\n",
    "src/App.Core/App.Core.csproj": CORE_CSPROJ,
    "src/App.Core/Thing.cs": "namespace App;\npublic class Thing {}\n",
    "src/App.Server/App.Server.csproj": SERVER_CSPROJ,
    "src/App.Server/Program.cs": 'var p = "data/seed/items/a.json";\n',
    "src/App.Host/App.Host.csproj": HOST_CSPROJ,
    "src/App.Host/Hooks.cs": "using UnityEngine;\nclass Hooks {}\n",
    "tools/Gen/Gen.csproj": GEN_CSPROJ,
    "tools/Gen/Gen.cs": "class Gen {}\n",
    "tests/App.Tests/RootTests.cs": 'var root = Find("App.slnx");\n',
    "data/seed/items/a.json": '{"_meta": {"model": "m", "promptVersion": "p/1"}, "name": "x"}\n',
    "data/tuning/a.v1.json": '{"k": 1}\n',
}

LAYOUT = {
    "schemaVersion": 1,
    "repos": [
        {"id": "root", "dir": ".", "visibility": "public", "property": "GkWorkflowRoot", "preserve": ["LICENSE", "tools/kvsplit/**"]},
        {"id": "gk-core", "dir": "gk-core", "visibility": "public", "property": "GkCoreRoot", "preserve": ["LICENSE"]},
        {"id": "gk-forge", "dir": "gk-forge", "visibility": "public", "property": "GkForgeRoot", "preserve": ["LICENSE"]},
        {"id": "gk-data", "dir": "gk-data", "visibility": "private", "property": "GkDataRoot", "preserve": ["LICENSE"]},
        {"id": "gk-fusion", "dir": "gk-fusion", "visibility": "public", "property": "GkFusionRoot", "preserve": ["LICENSE"]},
    ],
    "compileDeps": {"gk-forge": ["gk-core"], "gk-fusion": ["gk-core"]},
    "unityRepos": ["gk-fusion"],
}

OWNERSHIP = {
    "schemaVersion": 1,
    "rules": [
        {"id": "root-docs", "pattern": "docs/**", "target": "root", "priority": 0, "reason": "docs live in the root"},
        {"id": "root-readme", "pattern": "README.md", "target": "root", "priority": 0, "reason": "workspace readme"},
        {"id": "fusion-docs", "pattern": "docs/injector/**", "target": "gk-fusion", "priority": 10, "reason": "host docs"},
        {"id": "core-src", "pattern": "src/**", "target": "gk-core", "priority": 0, "reason": "engine source"},
        {"id": "fusion-host", "pattern": "src/App.Host/**", "target": "gk-fusion", "priority": 10, "reason": "game host"},
        {"id": "core-tests", "pattern": "tests/**", "target": "gk-core", "priority": 0, "reason": "engine tests"},
        {"id": "core-props", "pattern": "Directory.Build.props", "target": "gk-core", "priority": 0,
         "reason": "shared build settings", "copies": ["gk-forge", "gk-fusion"]},
        {"id": "forge-tools", "pattern": "tools/Gen/**", "target": "gk-forge", "priority": 0, "reason": "generator code"},
        {"id": "data-seed", "pattern": "data/seed/**", "target": "gk-data", "priority": 0, "reason": "content",
         "relocate": {"from": "data/seed/", "to": "packs/fusion/seed/"}},
        {"id": "core-tuning", "pattern": "data/tuning/**", "target": "gk-core", "priority": 0, "reason": "numbers"},
        {"id": "drop-sln", "pattern": "App.slnx", "target": "drop", "priority": 0, "reason": "regenerated per repo"},
    ],
}

TRANSFORMS = {
    "schemaVersion": 1,
    "transforms": [
        {"id": "msbuild", "kind": "msbuild-paths", "pattern": "**/*.csproj", "params": {}},
        {"id": "props", "kind": "msbuild-props-inject", "pattern": "Directory.Build.props", "params": {}},
        {"id": "md", "kind": "markdown-citations", "pattern": "**/*.md", "params": {"citationRoots": ["src", "tests", "tools", "data", "docs"]}},
    ],
}

SCAN = {
    "schemaVersion": 1,
    "extensions": [".cs", ".ps1", ".py"],
    "pathRoots": ["src", "tests", "tools", "data", "docs"],
    "skip": [],
    "citationGlobs": ["data/**"],
    "packRoots": {"gk-data": "packs/fusion/"},
    "tokens": [
        {"kind": "repo-root-discovery", "regex": "App\\.slnx", "allowedFix": "source",
         "detail": "repo root found through the legacy solution file"},
    ],
}


def write_rules(d: Path, **over: dict) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    for name, doc in (("layout.v1.json", LAYOUT), ("ownership.v1.json", OWNERSHIP),
                      ("transforms.v1.json", TRANSFORMS), ("scan.v1.json", SCAN)):
        key = name.split(".")[0]
        (d / name).write_text(json.dumps(over.get(key, doc), indent=2), encoding="utf-8")
    t = d / "templates" / "root" / ".gitignore"
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text("gk-core/\ngk-forge/\ngk-data/\ngk-fusion/\nstaging/\n", encoding="utf-8")
    return d


@pytest.fixture
def legacy(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "legacy", LEGACY_FILES)


@pytest.fixture
def rules_dir(tmp_path: Path) -> Path:
    return write_rules(tmp_path / "rules")
