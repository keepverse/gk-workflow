from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import git, make_repo
from kvsplit.apply import ApplyError, apply
from kvsplit.cli import main
from kvsplit.rules import load_rules
from kvsplit.stage import StageError, stage
from kvsplit.transforms import REGISTRY


def _staged(out: Path, ws_path: str) -> str:
    return (out / "workspace" / ws_path).read_text(encoding="utf-8")


def _kinds(result) -> dict[str, list]:
    by: dict[str, list] = {}
    for r in result.residue:
        by.setdefault(r.kind, []).append(r)
    return by


def test_stage_places_files_in_workspace_layout(legacy, rules_dir, tmp_path):
    out = tmp_path / "staging"
    r = stage(legacy, "HEAD", rules_dir, out)
    ws = out / "workspace"
    assert (ws / "gk-core/src/App.Core/Thing.cs").exists()
    assert (ws / "gk-fusion/src/App.Host/Hooks.cs").exists()
    assert (ws / "gk-data/packs/fusion/seed/items/a.json").exists()
    assert (ws / "gk-forge/tools/Gen/Gen.cs").exists()
    assert (ws / "docs/guide.md").exists()
    assert (ws / "gk-fusion/docs/injector/host.md").exists()
    assert not (ws / "App.slnx").exists()
    # copies: props land in three repos
    for repo in ("gk-core", "gk-forge", "gk-fusion"):
        assert (ws / repo / "Directory.Build.props").exists()
    rec = r.report["reconciliation"]
    assert rec["balanced"] is True


def test_msbuild_paths_rewritten_across_and_within_repos(legacy, rules_dir, tmp_path):
    out = tmp_path / "staging"
    stage(legacy, "HEAD", rules_dir, out)
    server = _staged(out, "gk-core/src/App.Server/App.Server.csproj")
    assert 'Include="..\\App.Core\\App.Core.csproj"' in server          # same repo: untouched
    assert 'Include="$(GkDataRoot)packs\\fusion\\seed\\items\\**\\*.json"' in server
    assert 'Include="..\\..\\data\\tuning\\**\\*.json"' in server       # tuning stays in gk-core
    gen = _staged(out, "gk-forge/tools/Gen/Gen.csproj")
    assert 'Include="$(GkCoreRoot)src\\App.Core\\App.Core.csproj"' in gen


def test_props_inject_defines_every_repo_root(legacy, rules_dir, tmp_path):
    out = tmp_path / "staging"
    stage(legacy, "HEAD", rules_dir, out)
    props = _staged(out, "gk-forge/Directory.Build.props")
    assert "<GkCoreRoot Condition=\"'$(GkCoreRoot)' == ''\">$(MSBuildThisFileDirectory)..\\gk-core\\</GkCoreRoot>" in props
    assert "<LangVersion>latest</LangVersion>" in props


def test_markdown_links_and_citations(legacy, rules_dir, tmp_path):
    out = tmp_path / "staging"
    stage(legacy, "HEAD", rules_dir, out)
    readme = _staged(out, "README.md")
    assert "[core](gk-core/src/App.Core/Thing.cs)" in readme
    assert "`gk-core/src/App.Core/Thing.cs:3`" in readme
    guide = _staged(out, "docs/guide.md")
    assert "[thing](../gk-core/src/App.Core/Thing.cs#L3)" in guide
    assert "`gk-core/data/tuning/a.v1.json`" in guide


def test_residue_reports_what_no_transform_owns(legacy, rules_dir, tmp_path):
    r = stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    k = _kinds(r)
    assert [x.path for x in k["repo-root-discovery"]] == ["tests/App.Tests/RootTests.cs"]
    moves = k["path-literal-moves"]
    assert any(x.path == "src/App.Server/Program.cs" and "gk-data:packs/fusion/seed/items/a.json" in x.detail for x in moves)
    assert all(x.allowed_fix == "source" for x in moves)
    assert "unity-outside-host" not in k   # the host lives in gk-fusion


def test_direction_and_unity_violations(tmp_path, rules_dir):
    files = {
        "src/App.Core/App.Core.csproj": ('<Project Sdk="x">\n  <ItemGroup>\n'
                                         '    <ProjectReference Include="..\\App.Host\\App.Host.csproj" />\n'
                                         '    <Reference Include="UnityEngine" />\n'
                                         '  </ItemGroup>\n</Project>\n'),
        "src/App.Core/Bad.cs": "using UnityEngine;\n",
        "src/App.Host/App.Host.csproj": '<Project Sdk="x">\n</Project>\n',
        "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x", "tests/t.cs": "x",
        "Directory.Build.props": "<Project>\n</Project>\n", "tools/Gen/g.cs": "x",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    repo = make_repo(tmp_path / "bad", files)
    k = _kinds(stage(repo, "HEAD", rules_dir, tmp_path / "staging"))
    assert "direction-violation" in k
    assert len(k["unity-outside-host"]) == 2  # csproj Reference + using


def test_generated_content_in_public_repo_is_flagged(legacy, rules_dir, tmp_path):
    own = json.loads((rules_dir / "ownership.v1.json").read_text())
    for rule in own["rules"]:
        if rule["id"] == "data-seed":
            rule["target"] = "gk-core"
            del rule["relocate"]
    (rules_dir / "ownership.v1.json").write_text(json.dumps(own))
    k = _kinds(stage(legacy, "HEAD", rules_dir, tmp_path / "staging"))
    assert k["content-in-public-repo"]


def test_two_runs_are_byte_identical(legacy, rules_dir, tmp_path):
    assert main(["verify", "--source", str(legacy), "--rev", "HEAD", "--rules", str(rules_dir),
                 "--out", str(tmp_path / "v")]) == 0
    a = (tmp_path / "v/run-1/report.json").read_bytes()
    b = (tmp_path / "v/run-2/report.json").read_bytes()
    assert a == b
    assert (tmp_path / "v/run-1/residue.json").read_bytes() == (tmp_path / "v/run-2/residue.json").read_bytes()


def test_residue_ids_are_stable_across_unrelated_changes(legacy, rules_dir, tmp_path):
    r1 = stage(legacy, "HEAD", rules_dir, tmp_path / "s1")
    (legacy / "src/App.Core/Other.cs").write_text("class O {}\n")
    git(legacy, "add", "-A")
    git(legacy, "commit", "-q", "-m", "unrelated")
    r2 = stage(legacy, "HEAD", rules_dir, tmp_path / "s2")
    assert {x.id for x in r1.residue} == {x.id for x in r2.residue}


def test_stage_refuses_to_clear_an_unmarked_directory(legacy, rules_dir, tmp_path):
    out = tmp_path / "precious"
    out.mkdir()
    (out / "keep.txt").write_text("mine")
    with pytest.raises(StageError):
        stage(legacy, "HEAD", rules_dir, out)
    assert (out / "keep.txt").read_text() == "mine"


# ---- apply -----------------------------------------------------------------------------------

def _workspace(tmp_path: Path) -> Path:
    ws = make_repo(tmp_path / "Keepverse", {"LICENSE": "L", "tools/kvsplit/x.py": "x"})
    for d in ("gk-core", "gk-forge", "gk-data", "gk-fusion"):
        make_repo(ws / d, {"LICENSE": "L"})
    return ws


def test_apply_is_held_without_the_owner_confirmation(legacy, rules_dir, tmp_path):
    stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    rules = load_rules(rules_dir, set(REGISTRY))
    with pytest.raises(ApplyError, match="gate GM"):
        apply(tmp_path / "staging", _workspace(tmp_path), rules.layout, ["gk-core"], rules.digest, False)


def test_apply_refuses_while_residue_remains(legacy, rules_dir, tmp_path):
    stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    rules = load_rules(rules_dir, set(REGISTRY))
    with pytest.raises(ApplyError, match="residue is not empty"):
        apply(tmp_path / "staging", _workspace(tmp_path), rules.layout, ["gk-core"], rules.digest, True)


def test_apply_commits_a_snapshot_and_preserves_license(tmp_path, rules_dir):
    clean = {
        "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
        "src/App.Core/Thing.cs": "class T {}\n",
        "src/App.Host/h.cs": "x", "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x",
        "tests/t.cs": "x", "Directory.Build.props": "<Project>\n</Project>\n", "tools/Gen/g.cs": "x",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    legacy = make_repo(tmp_path / "legacy", clean)
    stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    assert json.loads((tmp_path / "staging/residue.json").read_text())["items"] == []
    ws = _workspace(tmp_path)
    rules = load_rules(rules_dir, set(REGISTRY))
    out = apply(tmp_path / "staging", ws, rules.layout, rules.layout.ids(), rules.digest, True)
    assert len(out) == 5
    assert (ws / "gk-core/src/App.Core/Thing.cs").exists()
    assert (ws / "gk-core/LICENSE").read_text() == "L"
    assert (ws / "gk-data/packs/fusion/seed/a.json").exists()
    assert (ws / "tools/kvsplit/x.py").exists()          # root preserve
    assert "Import snapshot from legacy repo" in git(ws / "gk-core", "log", "-1", "--format=%B")
    assert git(ws, "status", "--porcelain") == ""          # sub-repos ignored by the staged .gitignore
