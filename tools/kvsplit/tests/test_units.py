from __future__ import annotations

import copy
import json

import pytest

from conftest import LAYOUT, OWNERSHIP, git
from kvsplit.classify import classify
from kvsplit.globmatch import matches
from kvsplit.rules import RulesError, load_rules, parse_layout, parse_ownership
from kvsplit.source import Entry, GitSource
from kvsplit.transforms import REGISTRY


# ---- globmatch -------------------------------------------------------------------------------

@pytest.mark.parametrize("pattern,path,expected", [
    ("src/**", "src/a/b.cs", True),
    ("src/**", "srcx/a.cs", False),
    ("**/*.csproj", "a.csproj", True),
    ("**/*.csproj", "x/y/a.csproj", True),
    ("docs/*.md", "docs/a/b.md", False),
    ("data/seed/**", "data/seed", True),
    ("a?.txt", "ab.txt", True),
    ("a?.txt", "a/.txt", False),
])
def test_glob(pattern, path, expected):
    assert matches(pattern, path) is expected


@pytest.mark.parametrize("bad", ["", "/abs", "back\\slash"])
def test_glob_rejects_bad_patterns(bad):
    with pytest.raises(ValueError):
        matches(bad, "x")


# ---- rules strictness ------------------------------------------------------------------------

def test_missing_field_throws():
    doc = copy.deepcopy(OWNERSHIP)
    del doc["rules"][0]["reason"]
    with pytest.raises(RulesError, match="reason"):
        parse_ownership(doc, parse_layout(LAYOUT))


def test_unknown_field_throws():
    doc = copy.deepcopy(OWNERSHIP)
    doc["rules"][0]["prio"] = 1
    with pytest.raises(RulesError, match="unknown field"):
        parse_ownership(doc, parse_layout(LAYOUT))


def test_unknown_target_throws():
    doc = copy.deepcopy(OWNERSHIP)
    doc["rules"][0]["target"] = "gk-nowhere"
    with pytest.raises(RulesError, match="unknown target"):
        parse_ownership(doc, parse_layout(LAYOUT))


def test_bool_is_not_an_int():
    doc = copy.deepcopy(OWNERSHIP)
    doc["rules"][0]["priority"] = True
    with pytest.raises(RulesError, match="bool"):
        parse_ownership(doc, parse_layout(LAYOUT))


def test_rules_digest_changes_with_content(rules_dir):
    d1 = load_rules(rules_dir, set(REGISTRY)).digest
    doc = json.loads((rules_dir / "ownership.v1.json").read_text())
    doc["rules"][0]["reason"] = "changed"
    (rules_dir / "ownership.v1.json").write_text(json.dumps(doc))
    assert load_rules(rules_dir, set(REGISTRY)).digest != d1


# ---- source ----------------------------------------------------------------------------------

def test_source_reads_the_commit_not_the_working_tree(legacy):
    (legacy / "src/App.Core/Thing.cs").write_text("DIRTY")
    (legacy / "untracked.txt").write_text("x")
    src = GitSource(legacy, "HEAD")
    assert "untracked.txt" not in src.paths()
    assert src.load_blobs()["src/App.Core/Thing.cs"].startswith(b"namespace App;")


def test_source_pins_the_sha(legacy):
    sha = git(legacy, "rev-parse", "HEAD")
    (legacy / "new.txt").write_text("n")
    git(legacy, "add", "-A")
    git(legacy, "commit", "-q", "-m", "later")
    assert "new.txt" not in GitSource(legacy, sha).paths()


# ---- classify --------------------------------------------------------------------------------

def _e(*paths: str) -> list[Entry]:
    return [Entry(p, "100644", "blob", "0" * 40) for p in paths]


def _rules(*rules: dict):
    return parse_ownership({"schemaVersion": 1, "rules": list(rules)}, parse_layout(LAYOUT))


def _r(id, pattern, target, priority=0, **kw):
    return {"id": id, "pattern": pattern, "target": target, "priority": priority, "reason": "r", **kw}


def test_priority_wins_and_unowned_is_residue():
    cls, res = classify(_e("src/a.cs", "src/host/b.cs", "zzz"),
                        _rules(_r("a", "src/**", "gk-core"), _r("b", "src/host/**", "gk-fusion", 5)),
                        parse_layout(LAYOUT))
    assert cls.map_file("src/a.cs") == ("gk-core", "src/a.cs")
    assert cls.map_file("src/host/b.cs") == ("gk-fusion", "src/host/b.cs")
    assert [(r.kind, r.path) for r in res] == [("unowned-path", "zzz")]


def test_same_priority_tie_is_ambiguous():
    _, res = classify(_e("src/a.cs"), _rules(_r("a", "src/**", "gk-core"), _r("b", "**/*.cs", "gk-forge")),
                      parse_layout(LAYOUT))
    assert [r.kind for r in res] == ["ambiguous-path"]


def test_dead_rule_is_residue():
    _, res = classify(_e("src/a.cs"), _rules(_r("a", "src/**", "gk-core"), _r("dead", "nothing/**", "gk-core")),
                      parse_layout(LAYOUT))
    assert [(r.kind, r.anchor) for r in res] == [("dead-rule", "dead")]


def test_relocation_and_dir_mapping():
    cls, res = classify(_e("data/seed/x/a.json", "data/seed/x/b.json"),
                        _rules(_r("d", "data/seed/**", "gk-data", relocate={"from": "data/seed/", "to": "packs/fusion/seed/"})),
                        parse_layout(LAYOUT))
    assert not res
    assert cls.map_dir("data/seed/x") == ("gk-data", "packs/fusion/seed/x")
    assert cls.map_dir("data/seed") == ("gk-data", "packs/fusion/seed")


def test_split_directory_does_not_map():
    cls, _ = classify(_e("docs/a.md", "docs/injector/b.md"),
                      _rules(_r("a", "docs/**", "root"), _r("b", "docs/injector/**", "gk-fusion", 5)),
                      parse_layout(LAYOUT))
    assert cls.map_dir("docs") is None
    assert cls.map_dir("docs/injector") == ("gk-fusion", "docs/injector")


def test_symlink_is_residue_not_copied():
    entries = [Entry("link", "120000", "blob", "0" * 40)]
    cls, res = classify(entries, _rules(_r("a", "**", "gk-core")), parse_layout(LAYOUT))
    assert cls.place("link") is None
    assert "unsupported-entry" in [r.kind for r in res]


# ---- transforms (direct) ---------------------------------------------------------------------

from kvsplit.rules import ScanConfig, TransformRule  # noqa: E402
from kvsplit.scan import scan  # noqa: E402
from kvsplit.transforms import Ctx  # noqa: E402


def _cls(*paths_and_rules):
    paths, rules = paths_and_rules
    cls, res = classify(_e(*paths), _rules(*rules), parse_layout(LAYOUT))
    assert not res
    return cls


def test_untracked_build_output_moves_with_its_tracked_ancestor():
    cls = _cls(("src/Inj/Inj.csproj", "src/Host/Host.csproj"),
               (_r("a", "src/**", "gk-fusion"),))
    ctx = Ctx(cls, "src/Host/Host.csproj", "gk-fusion", "src/Host/Host.csproj",
              TransformRule("t", "msbuild-paths", "**", {}))
    data = b'<Project><ItemGroup><Compile Remove="..\\Inj\\bin\\**" /></ItemGroup></Project>'
    out, res = REGISTRY["msbuild-paths"](ctx, data)
    assert not res
    assert out == data  # same repo, same offset: untouched


def test_solution_split_keeps_only_this_repos_projects():
    cls = _cls(("App.slnx", "src/A/A.csproj", "src/B/B.csproj"),
               (_r("s", "App.slnx", "gk-core", copies=["gk-fusion"]), _r("a", "src/A/**", "gk-core"),
                _r("b", "src/B/**", "gk-fusion")))
    sln = (b'<Solution>\n  <Folder Name="/src/">\n    <Project Path="src/A/A.csproj" />\n'
           b'    <Project Path="src/B/B.csproj" />\n  </Folder>\n  <Folder Name="/x/">\n'
           b'    <Project Path="src/B/B.csproj" />\n  </Folder>\n</Solution>\n')
    rule = TransformRule("t", "solution-split", "App.slnx", {})
    core, _ = REGISTRY["solution-split"](Ctx(cls, "App.slnx", "gk-core", "App.slnx", rule), sln)
    fusion, _ = REGISTRY["solution-split"](Ctx(cls, "App.slnx", "gk-fusion", "App.slnx", rule), sln)
    assert b"src/A/A.csproj" in core and b"src/B/B.csproj" not in core and b'"/x/"' not in core
    assert b"src/B/B.csproj" in fusion and b"src/A/A.csproj" not in fusion


def test_citation_files_skip_workspace_relative_citations_but_not_code():
    cls = _cls(("docs/a.md", "src/x.cs", "data/seed/s.json"),
               (_r("d", "docs/**", "root"), _r("c", "src/**", "gk-core"),
                _r("s", "data/seed/**", "gk-data", relocate={"from": "data/seed/", "to": "packs/fusion/seed/"})))
    cfg = ScanConfig(frozenset({".json", ".cs"}), ("docs", "src", "data"), (), ("data/**",), {}, {}, ())
    blobs = {"data/seed/s.json": b'{"spec": "docs/a.md", "src": "src/x.cs"}',
             "src/x.cs": b'var d = "docs/a.md";', "docs/a.md": b""}
    res = scan(blobs, cls, cfg, set())
    got = {(r.path, r.anchor) for r in res}
    assert ("data/seed/s.json", "docs/a.md") not in got      # still resolves workspace-relative
    assert ("data/seed/s.json", "src/x.cs") in got           # workspace path is gk-core/src/x.cs
    assert ("src/x.cs", "docs/a.md") in got                  # code opens it at runtime


def test_comment_citations_rewrite_comments_only_and_scan_skips_them():
    cls = _cls(("src/x.cs", "data/seed/a.json"),
               (_r("c", "src/**", "gk-core"),
                _r("s", "data/seed/**", "gk-data", relocate={"from": "data/seed/", "to": "packs/fusion/seed/"})))
    src = b'/// see `data/seed/a.json`\nvar p = "data/seed/a.json";\n'
    rule = TransformRule("t", "comment-citations", "**/*.cs", {"citationRoots": ["data"]})
    out, res = REGISTRY["comment-citations"](Ctx(cls, "src/x.cs", "gk-core", "src/x.cs", rule), src)
    assert out == b'/// see `gk-data/packs/fusion/seed/a.json`\nvar p = "data/seed/a.json";\n'
    cfg = ScanConfig(frozenset({".cs"}), ("data",), (), (), {}, {}, ())
    found = scan({"src/x.cs": src}, cls, cfg, set(), {"src/x.cs"})
    assert [(r.line, r.anchor) for r in found] == [(2, "data/seed/a.json")]


def test_pack_relative_content_paths_become_one_item_per_consuming_file():
    cls = _cls(("src/x.cs", "data/seed/a.json", "data/seed/b.json"),
               (_r("c", "src/**", "gk-core"),
                _r("s", "data/**", "gk-data", relocate={"from": "data/", "to": "packs/fusion/data/"})))
    cfg = ScanConfig(frozenset({".cs", ".json"}), ("data",), (), ("data/**",), {"gk-data": "packs/fusion/"}, {}, ())
    blobs = {"src/x.cs": b'var a = "data/seed/a.json";\nvar b = "data/seed/b.json";\n',
             "data/seed/a.json": b'{"see": "data/seed/b.json"}'}
    res = scan(blobs, cls, cfg, set())
    assert [(r.kind, r.path, r.line) for r in res] == [("content-root-consumer", "src/x.cs", 1)]


def test_comment_lines_cover_docstrings_and_blocks_but_not_code_strings():
    from kvsplit.transforms import comment_lines
    py = '"""Module doc: data/a.json\nmore"""\nx = "data/a.json"\n# note data/a.json\ndef f():\n    """doc"""\n    return 1\n'
    assert comment_lines(py, ".py") == {1, 2, 4, 6}
    cs = '/* block\n   data/a.json\n*/\nvar s = "x";\n// line\n'
    assert comment_lines(cs, ".cs") == {1, 2, 3, 5}
    ps = '<#\n help data/a.json\n#>\n$x = "y"\n# c\n'
    assert comment_lines(ps, ".ps1") == {1, 2, 3, 5}


def test_a_file_that_uses_the_repo_resolver_is_accepted():
    cls = _cls(("tools/g.py", "data/tuning/t.json", "data/seed/a.json"),
               (_r("g", "tools/**", "gk-forge"), _r("t", "data/tuning/**", "gk-core"),
                _r("s", "data/seed/**", "gk-data", relocate={"from": "data/", "to": "packs/fusion/data/"})))
    cfg = ScanConfig(frozenset({".py"}), ("data",), (), (), {"gk-data": "packs/fusion/"},
                     {"gk-core": r"core_root\(", "gk-data": r"content_root\("}, ())
    before = {"tools/g.py": b'a = ROOT / "data/tuning/t.json"\nb = ROOT / "data/seed/a.json"\n'}
    after = {"tools/g.py": b'a = core_root() / "data/tuning/t.json"\nb = content_root() / "data/seed/a.json"\n'}
    assert {r.kind for r in scan(before, cls, cfg, set())} == {"path-literal-moves", "content-root-consumer"}
    assert scan(after, cls, cfg, set()) == []
