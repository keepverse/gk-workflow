"""Move-first flow: apply, hash manifests, lossy check, index, reindex."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import git, make_repo
from kvsplit import hashes, index, reindex
from kvsplit.apply import apply
from kvsplit.rules import load_rules
from kvsplit.stage import stage
from kvsplit.transforms import REGISTRY

CFG = reindex.ReindexConfig(("**/*.md",), (), ("src", "docs", "data", "packs"))


@pytest.fixture
def moved(legacy, rules_dir, tmp_path):
    stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    ws = make_repo(tmp_path / "Keepverse", {"LICENSE": "L", "tools/kvsplit/x.py": "x"})
    for d in ("gk-core", "gk-forge", "gk-data", "gk-fusion"):
        make_repo(ws / d, {"LICENSE": "L"})
    rules = load_rules(rules_dir, set(REGISTRY))
    apply(tmp_path / "staging", ws, rules.layout, rules.layout.ids(), rules.digest, True, allow_residue=True)
    report = json.loads((tmp_path / "staging" / "report.json").read_text(encoding="utf-8"))
    return legacy, ws, rules, report


def _check(legacy, ws, rules, report):
    return hashes.lossy_check(hashes.source_manifest(legacy, "HEAD"), report,
                              hashes.workspace_manifest(ws, rules.layout), rules.layout)


def test_apply_refuses_residue_unless_the_move_first_flow_carries_it(legacy, rules_dir, tmp_path):
    from kvsplit.apply import ApplyError
    stage(legacy, "HEAD", rules_dir, tmp_path / "s")
    rules = load_rules(rules_dir, set(REGISTRY))
    with pytest.raises(ApplyError, match="residue"):
        apply(tmp_path / "s", tmp_path, rules.layout, ["gk-core"], rules.digest, True)


def test_a_faithful_move_is_lossless(moved):
    assert _check(*moved) == []


def test_altered_missing_and_unexplained_files_are_losses(moved):
    legacy, ws, rules, report = moved
    (ws / "gk-core/src/App.Core/Thing.cs").write_text("tampered")
    (ws / "gk-data/packs/fusion/seed/items/a.json").unlink()
    (ws / "gk-core/stray.txt").write_text("?")
    for d in ("gk-core", "gk-data"):
        git(ws / d, "add", "-A")
        git(ws / d, "commit", "-q", "-m", "damage")
    kinds = {(l.kind, l.path) for l in _check(legacy, ws, rules, report)}
    assert ("altered", "gk-core/src/App.Core/Thing.cs") in kinds
    assert ("missing", "gk-data/packs/fusion/seed/items/a.json") in kinds
    assert ("unexplained", "gk-core/stray.txt") in kinds


def test_source_drift_is_caught(moved):
    legacy, ws, rules, report = moved
    report = {**report, "sourceSha": "0" * 40}
    assert any(l.kind == "source-drift" for l in _check(legacy, ws, rules, report))


def test_index_maps_primary_placements_only(moved):
    legacy, ws, rules, report = moved
    idx = index.build(hashes.workspace_manifest(ws, rules.layout), report)
    assert idx.moves["src/App.Core/Thing.cs"] == "gk-core/src/App.Core/Thing.cs"
    assert idx.moves["Directory.Build.props"] == "gk-core/Directory.Build.props"   # not a copy
    assert idx.moved("data/seed/items") == "gk-data/packs/fusion/seed/items"
    assert idx.moved("docs") is None                                             # split: root + gk-fusion
    assert idx.exists("gk-core/src/App.Core")


def test_reindex_on_a_staged_move_is_idempotent(moved, tmp_path):
    legacy, ws, rules, report = moved
    idx = index.build(hashes.workspace_manifest(ws, rules.layout), report)
    first = reindex.reindex(ws, idx, CFG)
    reindex.write(first, ws, True, tmp_path / "r1.json")
    second = reindex.reindex(ws, idx, CFG)
    assert second.changed == {}


def test_reindex_rewrites_mapped_references_and_reports_stale_ones():
    idx = index.PathIndex(
        files=["docs/a.md", "gk-core/src/X.cs", "gk-fusion/docs/injector/h.md", "docs/b.md"],
        moves={"docs/a.md": "docs/a.md", "src/X.cs": "gk-core/src/X.cs", "docs/b.md": "docs/b.md",
               "docs/injector/h.md": "gk-fusion/docs/injector/h.md", "src/Gone.cs": "gk-fusion/src/Gone.cs"})
    text = ("see [x](../src/X.cs#L3), [b](b.md), [gone](../src/Nope.cs), `src/X.cs:12`, "
            "[docs](../docs/), `src/Gone.cs`, `src/never/was.cs`\n")
    res = reindex.Result()
    reverse = {v: k for k, v in idx.moves.items()}
    out = reindex.reindex_text("docs/a.md", text, idx, reverse, CFG, res)
    assert "[x](../gk-core/src/X.cs#L3)" in out
    assert "[b](b.md)" in out                     # already resolves
    assert "`gk-core/src/X.cs:12`" in out
    assert "`src/never/was.cs`" in out           # never existed: left alone, not stale
    stale = {(f.ref, f.reason) for f in res.stale}
    assert ("../src/Nope.cs", "already broken before the move") in {(f.ref, f.reason) for f in res.pre_existing}
    assert ("src/Gone.cs", "legacy path split across repos or dropped") in stale  # maps, but file absent now
    assert "[docs](../docs/)" in out               # docs/ still exists (root keeps most of it)


def test_apply_writes_nothing_when_any_repo_fails_preflight(legacy, rules_dir, tmp_path):
    from kvsplit.apply import ApplyError
    stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    ws = make_repo(tmp_path / "Keepverse", {"LICENSE": "L", "tools/kvsplit/x.py": "x"})
    for d in ("gk-core", "gk-forge", "gk-data", "gk-fusion"):
        make_repo(ws / d, {"LICENSE": "L"})
    (ws / "gk-fusion" / "dirty.txt").write_text("uncommitted")
    rules = load_rules(rules_dir, set(REGISTRY))
    before = git(ws, "rev-parse", "HEAD")
    with pytest.raises(ApplyError, match="not clean"):
        apply(tmp_path / "staging", ws, rules.layout, rules.layout.ids(), rules.digest, True, allow_residue=True)
    assert git(ws, "rev-parse", "HEAD") == before           # root untouched although it comes first
    assert not (ws / "gk-core" / "src").exists()


def test_route_slugs_and_repo_relative_citations_are_left_alone():
    idx = index.PathIndex(files=["gk-core/AGENTS.md", "gk-core/tests/T/T.csproj", "docs/g.md"],
                          moves={"docs/g.md": "docs/g.md"})
    res = reindex.Result()
    out = reindex.reindex_text("gk-core/AGENTS.md", "run `tests/T` and see [page](passive-trees)\n",
                               idx, {}, CFG, res)
    assert out == "run `tests/T` and see [page](passive-trees)\n"
    assert res.stale == [] and res.rewritten == []


def test_apply_force_adds_files_a_copied_gitignore_would_hide(tmp_path, rules_dir):
    files = {
        ".gitignore": "*.lock.json\n",
        "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
        "src/App.Core/pinned.lock.json": "{}",
        "src/App.Host/h.cs": "x", "docs/a.md": "x", "docs/injector/b.md": "x", "README.md": "x",
        "tests/t.cs": "x", "Directory.Build.props": "<Project>\n</Project>\n", "tools/Gen/g.cs": "x",
        "data/seed/a.json": "{}", "data/tuning/t.json": "{}", "App.slnx": "x",
    }
    legacy = tmp_path / "legacy"
    make_repo(legacy, {k: v for k, v in files.items()})
    git(legacy, "add", "-f", "src/App.Core/pinned.lock.json")
    git(legacy, "commit", "-q", "-m", "force-tracked")
    own = json.loads((rules_dir / "ownership.v1.json").read_text())
    own["rules"].append({"id": "gi", "pattern": ".gitignore", "target": "gk-core", "priority": 0, "reason": "r"})
    (rules_dir / "ownership.v1.json").write_text(json.dumps(own))
    stage(legacy, "HEAD", rules_dir, tmp_path / "staging")
    ws = make_repo(tmp_path / "Keepverse", {"LICENSE": "L"})
    for d in ("gk-core", "gk-forge", "gk-data", "gk-fusion"):
        make_repo(ws / d, {"LICENSE": "L"})
    rules = load_rules(rules_dir, set(REGISTRY))
    apply(tmp_path / "staging", ws, rules.layout, rules.layout.ids(), rules.digest, True, allow_residue=True)
    assert "src/App.Core/pinned.lock.json" in git(ws / "gk-core", "ls-files")
