from __future__ import annotations

import json
import subprocess
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


def _add_symlink(repo: Path, path: str, target: str) -> None:
    """Plant a real mode=120000 index entry.

    `git add` on a symlink is not usable here: without core.symlinks git records the
    link target as an ordinary file, so the entry never becomes a symlink and the test
    would silently exercise the wrong path. Writing the index entry directly is how a
    symlink is authored anyway.
    """
    blob = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
                          input=target, capture_output=True, text=True, check=True).stdout.strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"120000,{blob},{path}")


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


def test_a_test_project_may_drive_a_generator_it_may_not_compile_against(rules_dir, tmp_path):
    """compileDeps governs what ships. A test project verifies a generator's output, so
    layout.testProjectGlobs waives the direction for it - but only for it."""
    lay = json.loads((rules_dir / "layout.v1.json").read_text())
    lay["testProjectGlobs"] = ["tests/**/*.Tests.csproj"]
    (rules_dir / "layout.v1.json").write_text(json.dumps(lay))

    proj = ('<Project Sdk="x">\n  <ItemGroup>\n'
            '    <ProjectReference Include="..\\..\\tools\\Gen\\Gen.csproj" />\n'
            '  </ItemGroup>\n</Project>\n')
    files = {
        "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
        "src/App.Host/App.Host.csproj": proj,
        "tests/App.Tests/App.Tests.csproj": proj,
        "tools/Gen/Gen.csproj": '<Project Sdk="x">\n</Project>\n',
        "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x", "tests/t.cs": "x",
        "Directory.Build.props": "<Project>\n</Project>\n",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    repo = make_repo(tmp_path / "testproj", files)
    k = _kinds(stage(repo, "HEAD", rules_dir, tmp_path / "staging"))
    bad = [x.path for x in k.get("direction-violation", [])]
    assert "tests/App.Tests/App.Tests.csproj" not in bad   # exempted
    assert "src/App.Host/App.Host.csproj" in bad             # still refused


def test_without_test_project_globs_a_test_project_is_still_refused(rules_dir, tmp_path):
    """The waiver is opt-in. Absent the field, nothing changes."""
    proj = ('<Project Sdk="x">\n  <ItemGroup>\n'
            '    <ProjectReference Include="..\\..\\tools\\Gen\\Gen.csproj" />\n'
            '  </ItemGroup>\n</Project>\n')
    files = {
        "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
        "src/App.Host/App.Host.csproj": proj,
        "tests/App.Tests/App.Tests.csproj": proj,
        "tools/Gen/Gen.csproj": '<Project Sdk="x">\n</Project>\n',
        "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x", "tests/t.cs": "x",
        "Directory.Build.props": "<Project>\n</Project>\n",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    repo = make_repo(tmp_path / "notestproj", files)
    k = _kinds(stage(repo, "HEAD", rules_dir, tmp_path / "staging"))
    bad = [x.path for x in k.get("direction-violation", [])]
    assert "tests/App.Tests/App.Tests.csproj" in bad


def test_a_drop_rule_retires_a_symlink_and_the_reconciliation_counts_it(rules_dir, tmp_path):
    """A symlink cannot be migrated, and it never reaches ordinary classification, so a
    `drop` rule is the only way to resolve one - and it must land in `dropped`."""
    own = json.loads((rules_dir / "ownership.v1.json").read_text())
    own["rules"].append({"id": "t-drop-links", "pattern": ".claude/skills/*",
                         "target": "drop", "priority": 20, "reason": "retire the alias"})
    (rules_dir / "ownership.v1.json").write_text(json.dumps(own))

    files = {
        "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
        "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x", "tests/t.cs": "x",
        "Directory.Build.props": "<Project>\n</Project>\n",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    repo = make_repo(tmp_path / "links", files)
    baseline = stage(repo, "HEAD", rules_dir, tmp_path / "baseline").report["reconciliation"]
    for name in ("alpha", "beta"):
        _add_symlink(repo, f".claude/skills/{name}", f"../../.agents/skills/{name}")
    git(repo, "commit", "-q", "--allow-empty", "-m", "links")

    r = stage(repo, "HEAD", rules_dir, tmp_path / "staging")
    k = _kinds(r)
    assert "unsupported-entry" not in k
    rec = r.report["reconciliation"]
    # The fixture already drops App.slnx, so the claim under test is the delta: the drop
    # rule adds exactly the two symlinks, and they are named in the report.
    assert rec["dropped"] - baseline["dropped"] == 2
    assert {".claude/skills/alpha", ".claude/skills/beta"} <= set(r.report["dropped"])
    assert rec["tracked"] - baseline["tracked"] == 2
    assert rec["unplaced"] == 0
    assert rec["balanced"]


def test_a_symlink_without_a_drop_rule_is_still_refused(rules_dir, tmp_path):
    files = {
        "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
        "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x", "tests/t.cs": "x",
        "Directory.Build.props": "<Project>\n</Project>\n",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    repo = make_repo(tmp_path / "nolinks", files)
    _add_symlink(repo, ".claude/skills/alpha", "../../.agents/skills/alpha")
    git(repo, "commit", "-q", "--allow-empty", "-m", "link")
    k = _kinds(stage(repo, "HEAD", rules_dir, tmp_path / "staging"))
    assert [x.path for x in k["unsupported-entry"]] == [".claude/skills/alpha"]


_CLEAN = {
    "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
    "src/App.Core/Thing.cs": "class T {}\n",
    "src/App.Host/h.cs": "x", "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x",
    "tests/t.cs": "x", "Directory.Build.props": "<Project>\n</Project>\n", "tools/Gen/g.cs": "x",
    "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
}


def _collision_case(tmp_path, rules_dir):
    """A staged file that is ALSO already committed in the target, with other content."""
    src = make_repo(tmp_path / "legacy", _CLEAN)
    stage(src, "HEAD", rules_dir, tmp_path / "staging")
    ws = _workspace(tmp_path)
    make_repo(ws / "gk-core", {"src/App.Core/Thing.cs": "// the owner's newer version\n"})
    return tmp_path / "staging", ws


def test_apply_refuses_to_overwrite_a_committed_file_that_differs(rules_dir, tmp_path):
    """preserve stops apply DELETING a file; it does not stop the write loop overwriting
    one. An owner who already migrated and then improved a file must not lose it silently."""
    staging, ws = _collision_case(tmp_path, rules_dir)
    rules = load_rules(rules_dir, set(REGISTRY))
    with pytest.raises(ApplyError) as ex:
        apply(staging, ws, rules.layout, ["gk-core"], rules.digest, True, allow_residue=True)
    msg = str(ex.value)
    assert "would overwrite" in msg
    assert "gk-core/src/App.Core/Thing.cs" in msg
    assert "silent data loss" in msg
    assert (ws / "gk-core/src/App.Core/Thing.cs").read_text() == "// the owner's newer version\n"


def test_accept_overwrites_lets_the_owner_proceed_deliberately(rules_dir, tmp_path):
    staging, ws = _collision_case(tmp_path, rules_dir)
    rules = load_rules(rules_dir, set(REGISTRY))
    out = apply(staging, ws, rules.layout, ["gk-core"], rules.digest, True,
                allow_residue=True, accept_overwrites=True)
    assert out and out[0].startswith("gk-core:")
    assert (ws / "gk-core/src/App.Core/Thing.cs").read_text() == "class T {}\n"


def test_apply_writes_a_collision_whose_content_is_identical(rules_dir, tmp_path):
    """Identical bytes are not a conflict, so the happy path stays happy."""
    src = make_repo(tmp_path / "legacy", _CLEAN)
    stage(src, "HEAD", rules_dir, tmp_path / "staging")
    ws = _workspace(tmp_path)
    make_repo(ws / "gk-core", {"src/App.Core/Thing.cs": "class T {}\n"})
    rules = load_rules(rules_dir, set(REGISTRY))
    out = apply(tmp_path / "staging", ws, rules.layout, ["gk-core"], rules.digest, True,
                allow_residue=True)
    assert out


def test_a_repo_that_receives_nothing_is_reported_not_failed(rules_dir, tmp_path):
    """A repo holding hand-authored content that the split hands zero files to is a
    legitimate state. `git commit` on an empty index is an error, and that must not fail
    the migration."""
    src = make_repo(tmp_path / "legacy", _CLEAN)
    out = tmp_path / "staging"
    # Empty one repo on purpose: the fixture stages into all of them otherwise.
    own = json.loads((rules_dir / "ownership.v1.json").read_text())
    own["rules"].append({"id": "t-empty-gk-data", "pattern": "data/seed/**", "target": "drop",
                         "priority": 99, "reason": "test: leave gk-data with no migrated files"})
    (rules_dir / "ownership.v1.json").write_text(json.dumps(own))
    stage(src, "HEAD", rules_dir, out)
    report = json.loads((out / "report.json").read_text())
    per_repo: dict[str, int] = {r: 0 for r in report["reconciliation"]["placedPerRepo"]}
    for r in report["files"]:
        per_repo[r["repo"]] = per_repo.get(r["repo"], 0) + 1
    empty = [rid for rid, n in per_repo.items() if n == 0 and rid != "root"]
    assert empty, f"fixture stages into every repo, so this case is untestable here: {per_repo}"
    rid = empty[0]
    rules = load_rules(rules_dir, set(REGISTRY))

    ws = _workspace(tmp_path)
    # _workspace seeds each sub-repo with LICENSE, which the synthetic layout preserves.
    # Adding anything else here would give apply a legitimate deletion to commit, which is
    # a different case.
    hand = ws / rid
    before = git(hand, "rev-parse", "HEAD")
    res = apply(out, ws, rules.layout, [rid], rules.digest, True, allow_residue=True)
    assert res == [f"{rid}: unchanged (nothing staged for this repo)"]
    assert git(hand, "rev-parse", "HEAD") == before
    assert (hand / "LICENSE").read_text() == "L"


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
