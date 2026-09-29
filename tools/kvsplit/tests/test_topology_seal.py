"""The gk-tests topology reconciliation, enforced rather than described.

`ownership.v1.json` named gk-tests zero times before this change, which meant nothing could
land there - by accident, not by decision. The plan then claimed the opposite in three places,
so the rules and the document named two different topologies and the document was the one a
reader believed. A seal turns the accident into a rule: the split may not place anything in
gk-tests, any route that tries is refused by name, and `check` asserts the staged tree.

Every test here fails against the pre-change tool, which is what makes them evidence rather
than decoration.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from conftest import LAYOUT, OWNERSHIP, make_repo, write_rules
from kvsplit.check import run_checks
from kvsplit.rules import RulesError, load_rules, parse_layout
from kvsplit.stage import stage
from kvsplit.transforms import REGISTRY

SHIPPED_RULES = Path(__file__).resolve().parents[1] / "rules"

SEAL = "gk-tests is for cross-repo suites, and the split may not write into it"

# A legacy tree small enough to reason about, holding exactly the file the competing copy of
# the plan wanted in gk-tests: a shared gate definition.
GATE_DEF = {
    "verification-boundaries.v1.json": '{"boundaries": []}\n',
    "suites/cross-repo/order.test.cs": "class OrderTest {}\n",
    ".github/workflows/gk-tests.yml": "name: gk-tests\n",
    "src/App.Core/App.Core.csproj": '<Project Sdk="x">\n</Project>\n',
    "docs/a.md": "x", "README.md": "x", "tests/t.cs": "x",
    "Directory.Build.props": "<Project>\n</Project>\n",
    "tools/Gen/g.cs": "x", "data/seed/a.json": "{}", "App.slnx": "x",
}


def _layout(sealed: bool) -> dict:
    doc = copy.deepcopy(LAYOUT)
    doc["repos"].append({
        "id": "gk-tests", "dir": "gk-tests", "visibility": "public",
        "property": "GkTestsRoot", "preserve": ["LICENSE"],
    })
    if sealed:
        doc["repos"][-1]["seal"] = {"reason": SEAL}
    return doc


def _ownership(target: str, pattern: str = "**", **extra) -> dict:
    doc = copy.deepcopy(OWNERSHIP)
    doc["rules"].append({"id": "tests-gates", "pattern": pattern, "target": target,
                         "priority": 99, "reason": "shared gates and cross-repo suites", **extra})
    return doc


def _rules_dir(tmp_path: Path, layout: dict, ownership: dict, name: str = "rules") -> Path:
    return write_rules(tmp_path / name, layout=layout, ownership=ownership)

# ---- layout: the seal is a declared, reasoned fact ------------------------------------------

def test_a_seal_needs_a_reason(tmp_path):
    doc = _layout(True)
    del doc["repos"][-1]["seal"]["reason"]
    with pytest.raises(RulesError, match=r"seal: missing required field 'reason'"):
        parse_layout(doc)


def test_a_seal_rejects_unknown_fields():
    doc = _layout(True)
    doc["repos"][-1]["seal"]["pattern"] = ".github/workflows/*.yml"
    with pytest.raises(RulesError, match="unknown field"):
        parse_layout(doc)


def test_the_seal_is_visible_on_the_layout():
    lay = parse_layout(_layout(True))
    assert "gk-tests" in lay.sealed
    assert lay.seal_reason("gk-tests") == SEAL
    assert "gk-core" not in lay.sealed


# ---- stage refuses the three routes into a sealed repo ---------------------------------------

def test_a_rule_placing_a_file_in_a_sealed_repo_is_refused(tmp_path):
    """The competing copy itself: a rule that would put a shared gate definition in gk-tests."""
    d = _rules_dir(tmp_path, _layout(True), _ownership("gk-tests", "verification-boundaries.v1.json"))
    with pytest.raises(RulesError, match="targets sealed repo 'gk-tests'"):
        load_rules(d, set(REGISTRY))


def test_a_copy_into_a_sealed_repo_is_refused(tmp_path):
    """A `copies` row is the same bytes in a second repository. It is the competing copy the
    seal exists to prevent, so it can never be the thin-entrypoint exception either."""
    doc = copy.deepcopy(OWNERSHIP)
    doc["rules"].append({"id": "tests-copy", "pattern": "Directory.Build.props", "target": "gk-core",
                         "priority": 99, "reason": "a shared file", "copies": ["gk-tests"]})
    d = _rules_dir(tmp_path, _layout(True), doc)
    with pytest.raises(RulesError, match="is sealed"):
        load_rules(d, set(REGISTRY))


def test_a_template_for_a_sealed_repo_is_refused(tmp_path):
    """kvsplit emits templates verbatim. A template in gk-tests is the split writing into a
    repository the seal says it may not write into - the same shape as H2's template row."""
    d = _rules_dir(tmp_path, _layout(True), _ownership("drop", "docs/**"))
    t = d / "templates" / "gk-tests" / "AGENTS.md"
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text("gates live here\n", encoding="utf-8")
    with pytest.raises(RulesError, match="templates/gk-tests/AGENTS.md: repo 'gk-tests' is sealed"):
        load_rules(d, set(REGISTRY))


def test_the_thin_entrypoint_exception_only_opens_for_a_sealed_repo(tmp_path):
    """`entrypoint: true` exists for one case: a CI file a platform requires inside a
    sub-repository. A rule may not claim it for an ordinary repository, or the exception
    becomes an unreviewed hole in every seal."""
    d = _rules_dir(tmp_path, _layout(True), _ownership("gk-core", "**", entrypoint=True))
    with pytest.raises(RulesError, match="not sealed"):
        load_rules(d, set(REGISTRY))


def test_a_declared_thin_entrypoint_is_allowed_into_a_sealed_repo(tmp_path):
    """The exception works, and it is narrow: one rule, naming itself, with its own reason."""
    d = _rules_dir(tmp_path, _layout(True),
                   _ownership("gk-tests", ".github/workflows/gk-tests.yml", entrypoint=True))
    rules = load_rules(d, set(REGISTRY))
    assert [r.entrypoint for r in rules.ownership if r.id == "tests-gates"] == [True]
    src = make_repo(tmp_path / "legacy", GATE_DEF)
    r = stage(src, "HEAD", d, tmp_path / "staging")
    rows = [f for f in r.files if f.repo == "gk-tests"]
    assert [f.path for f in rows] == [".github/workflows/gk-tests.yml"]
    assert not any(x.kind == "sealed-repo-received-file" for x in r.residue)


# ---- check asserts the invariant on the staged tree ------------------------------------------

def _open_and_sealed(tmp_path: Path):
    """Stage once with gk-tests open, then check that same tree against the sealed layout.

    This is the shape of the failure the check exists for: the tree is already built, so the
    only thing left is to assert the rule against it."""
    src = make_repo(tmp_path / "legacy", GATE_DEF)
    open_rules = _rules_dir(tmp_path, _layout(False), _ownership("gk-tests", "suites/**"), "open")
    r = stage(src, "HEAD", open_rules, tmp_path / "staging-open")
    assert [f.path for f in r.files if f.repo == "gk-tests"] == ["suites/cross-repo/order.test.cs"]
    sealed_rules = load_rules(_rules_dir(tmp_path, _layout(True), _ownership("drop", "suites/**"), "sealed"),
                              set(REGISTRY))
    return r, sealed_rules


def test_check_reports_a_file_staged_into_a_sealed_repo(tmp_path):
    r, sealed_rules = _open_and_sealed(tmp_path)
    residue = run_checks(r.files, r.cls, sealed_rules)
    bad = [x for x in residue if x.kind == "sealed-repo-received-file"]
    assert [x.path for x in bad] == ["gk-tests/suites/cross-repo/order.test.cs"]
    assert "is sealed" in bad[0].detail and "source file" in bad[0].detail
    assert bad[0].allowed_fix == "rule"


def test_check_reports_a_template_row_in_a_sealed_repo_too(tmp_path):
    """H2's shape: gk-assets had 228 files behind two non-primary rows. Assert the seal on
    every row shape, or it is a check that only one route can trip."""
    from kvsplit.stage import StagedFile

    r, sealed_rules = _open_and_sealed(tmp_path)
    extra = StagedFile("gk-tests", "AGENTS.md", b"gates live here\n", None, None, (), "template")
    residue = run_checks([*r.files, extra], r.cls, sealed_rules)
    bad = [x for x in residue if x.kind == "sealed-repo-received-file"]
    assert "gk-tests/AGENTS.md" in [x.path for x in bad]
    assert any("template file" in x.detail for x in bad)


def test_a_clean_staged_tree_reports_no_seal_finding(tmp_path):
    r, sealed_rules = _open_and_sealed(tmp_path)
    r.files = [f for f in r.files if f.repo != "gk-tests"]
    assert not any(x.kind == "sealed-repo-received-file"
                   for x in run_checks(r.files, r.cls, sealed_rules))


# ---- the shipped rules -------------------------------------------------------------------------

def test_the_shipped_rules_load_and_seal_gk_tests():
    rules = load_rules(SHIPPED_RULES, set(REGISTRY))
    assert "gk-tests" in rules.layout.sealed
    assert "gk-workflow" not in rules.layout.sealed


def test_the_shipped_rules_place_nothing_in_gk_tests():
    """The measured fact this change turns into a rule: no ownership rule names gk-tests, no
    template is emitted into it, and so no placement can reach it."""
    own = json.loads((SHIPPED_RULES / "ownership.v1.json").read_text(encoding="utf-8"))
    named = [r["id"] for r in own["rules"]
             if r["target"] == "gk-tests" or "gk-tests" in r.get("copies", [])]
    assert named == [], f"an ownership rule names the sealed repo: {named}"
    assert not (SHIPPED_RULES / "templates" / "gk-tests").exists()


def test_a_transform_cannot_reach_a_sealed_repo():
    """Transforms run per (source path, target repo) and the target repo comes from
    classification, which the seal has already refused. Asserted rather than assumed: an
    entrypoint rule is the one placement a transform could run against, and the seal check
    is what catches it if that stops being true."""
    from kvsplit.classify import classify
    from kvsplit.source import Entry

    lay = parse_layout(json.loads((SHIPPED_RULES / "layout.v1.json").read_text(encoding="utf-8")))
    rules = load_rules(SHIPPED_RULES, set(REGISTRY))
    # The shared gate declaration the old plan wanted in gk-tests, and the CI entrypoint the
    # seal makes room for. Both are real paths, so both really are classified.
    paths = ["scripts/verification-boundaries.v1.json", ".github/workflows/gk-tests.yml"]
    entries = [Entry(p, "100644", "blob", "0" * 40) for p in paths]
    cls, _ = classify(entries, rules.ownership, lay)
    landed = {p: cls.place(p).repo for p in paths}
    assert "gk-tests" not in landed.values(), landed
    assert landed["scripts/verification-boundaries.v1.json"] == "gk-core"
    assert landed[".github/workflows/gk-tests.yml"] == "root"
